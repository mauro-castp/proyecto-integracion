# Diseño de claves Redis

**Plataforma de Microhubs · Codex Innovations · Equipo 04 · Primer Parcial**
Responsable: Mauro Castillo Peña

Redis cubre cuatro responsabilidades declaradas en la propuesta: revocación de sesión (RF04), bloqueos de inventario (RN17), caché de consultas públicas (RNF07) y datos temporales de seguridad (RF05, RF06). Nada más.

## Principio de asignación

Redis no es durable. Cualquier dato cuya pérdida produzca una inconsistencia contable, un saldo equivocado o un folio duplicado **no puede vivir aquí**. La prueba práctica: si un `FLUSHALL` accidental obligara a algo más que volver a iniciar sesión y recalcular caché, ese dato está en el lugar equivocado.

Por eso el folio de pedido se genera con una secuencia de PostgreSQL y no con un `INCR` de Redis, aunque `INCR` sea más rápido y más cómodo. Un folio repetido después de un reinicio sería un incidente de conciliación, no un problema de rendimiento.

## Convención de nombres

```
{ambito}:{dominio}:{entidad}[:{subclave}]
```

Todo en minúsculas, separado por dos puntos, sin acentos ni espacios. El primer segmento identifica la base lógica y permite auditar con `SCAN MATCH` sin tocar claves de otro dominio.

## Separación por base lógica

Las políticas de expulsión de estas dos familias son incompatibles y por eso no pueden compartir base:

| Base | Contenido | `maxmemory-policy` | Justificación |
|---|---|---|---|
| `db 0` | Sesión, bloqueos, seguridad | `noeviction` | Si Redis expulsa un bloqueo de inventario por presión de memoria, se produce sobreventa. Estas claves **no son descartables**. |
| `db 1` | Caché de catálogo, cobertura, indicadores | `allkeys-lru` | Perder una entrada de caché solo cuesta una consulta a PostgreSQL. |

Configurar una sola instancia con `allkeys-lru` sería el error más caro del diseño: haría que un pico de tráfico público pudiera borrar un bloqueo de inventario activo.

---

## 1. Sesión y seguridad — `db 0`

| Clave | Tipo | TTL | Requisito |
|---|---|---|---|
| `auth:jti:revocado:{jti}` | String | Vigencia restante del token de acceso | RF04, HU12 CA1 |
| `auth:sesion:{usuario_id}` | Set de `jti` | Vigencia del refresh | RF03 |
| `auth:refresh:{jti}` | Hash | `jwt_refresh_dias` | RF03 |
| `auth:intentos:{correo_hash}` | String contador | `bloqueo_minutos` | RF06, HU13 CA2 |
| `auth:bloqueo:{usuario_id}` | String | `bloqueo_minutos` | RF06 |
| `auth:reset:{token_hash}` | String | `reset_token_minutos` | RF05, HU13 CA1 |

Tres decisiones que conviene no perder:

**El TTL de la clave de revocación es la vida restante del token, no un valor fijo.** Una vez que el token expira por sí solo, la entrada de revocación ya no sirve para nada y solo ocupa memoria. Calcularlo como `exp - now` mantiene la lista de revocados acotada al número de tokens vivos.

**El correo y el token de recuperación se guardan hasheados, no en claro.** Un volcado de Redis no debe entregar la lista de correos que intentaron entrar ni un token de recuperación utilizable. HU13 CA3 exige trazabilidad de los intentos fallidos sin almacenar la contraseña intentada; esto lo extiende al identificador.

**El contador de intentos vive también en PostgreSQL (`usuario.intentos_fallidos`).** Redis lleva la ventana corta, que es la que decide el bloqueo inmediato; PostgreSQL conserva el histórico, que sobrevive a un reinicio y alimenta la auditoría. No es duplicación: son dos preguntas distintas.

**El logout revoca por `jti`, no por usuario.** Un usuario puede tener sesión abierta en el sistema web y en la app; cerrar una no debe tumbar la otra. Por eso existe `auth:sesion:{usuario_id}` como conjunto: permite el cierre masivo cuando el Administrador lo ordena, sin que sea el comportamiento por omisión.

---

## 2. Bloqueo de inventario — `db 0`

| Clave | Tipo | TTL | Requisito |
|---|---|---|---|
| `lock:inv:{microhub_id}:{producto_id}` | String con token de propietario | 5 s | RN17, HU21 CA2 |
| `lock:pedido:{pedido_id}` | String con token de propietario | 10 s | RNF08 |

Adquisición:

```
SET lock:inv:1:42 <token-uuid> NX PX 5000
```

`NX` garantiza que solo un cliente lo obtiene. `PX` garantiza que un proceso muerto no deja el producto bloqueado para siempre. El **token de propietario es lo que hace correcta la liberación**: sin él, un proceso lento podría borrar el bloqueo que ya adquirió otro después de que el suyo expiró. Por eso la liberación es un script Lua que compara antes de borrar (`02_liberar_lock.lua`), y nunca un `DEL` directo.

### Relación con el bloqueo de PostgreSQL

Este bloqueo **no sustituye** al `SELECT ... FOR UPDATE` de `fn_asignar_pedido`. Cumplen funciones distintas:

- Redis evita que dos peticiones lleguen siquiera a competir, y protege la fase de evaluación de candidatos, que ocurre fuera de la transacción.
- PostgreSQL garantiza la atomicidad real del descuento. Es la única capa que puede prometer que no habrá existencia negativa, y lo hace además con el `CHECK (existencia >= 0)`.

Si Redis se cae por completo, el sistema se vuelve más lento y más contencioso, pero **no sobrevende**. Esa es la propiedad que se buscaba: la corrección no depende del componente no durable.

El orden de adquisición de bloqueos es siempre ascendente por `producto_id`, igual que en la función de PostgreSQL. Dos convenciones distintas de orden entre las dos capas producirían interbloqueos.

---

## 3. Caché — `db 1`

| Clave | Tipo | TTL | Requisito |
|---|---|---|---|
| `cache:catalogo:{categoria}:{pagina}` | String JSON | `cache_catalogo_segundos` (300) | RF13, RNF07 |
| `cache:producto:{clave_interna}` | Hash | 300 s | RNF07 |
| `cache:cobertura:{cp}` | String JSON | 600 s | RF12 |
| `cache:cobertura:colonia:{slug}` | String JSON | 600 s | RF12 |
| `cache:indicadores:{microhub_id}:{periodo}` | String JSON | 60 s | RF19 |
| `cache:catalogo:version` | String contador | sin TTL | invalidación |

**La invalidación se hace por versión, no por borrado.** Cuando cambia un precio o un producto, se hace `INCR cache:catalogo:version` y la versión entra en la clave real (`cache:catalogo:v{n}:{categoria}:{pagina}`). Borrar con `KEYS cache:catalogo:*` bloquearía el servidor completo mientras recorre el espacio de claves, y hacerlo con `SCAN` deja una ventana en la que conviven entradas viejas y nuevas.

**La caché de cobertura respeta RN34.** Guarda disponible o no disponible, ticket mínimo, costo de envío y horario. No guarda coordenadas ni identificador del microhub que da la cobertura: si esa entrada se filtrara, no revelaría dónde está el almacén.

**La caché pública nunca guarda existencias exactas** (RN11, HU27 CA2). El valor cacheado es `disponible: true|false`, calculado antes de escribir, no la cantidad.

---

## 4. Limitación de frecuencia — `db 1`

| Clave | Tipo | TTL | Requisito |
|---|---|---|---|
| `rate:publico:{ip_hash}:{minuto}` | String contador | 120 s | CU02 A3 |
| `rate:login:{ip_hash}:{minuto}` | String contador | 120 s | RF06 |

Ventana fija por minuto: el minuto va en la clave y el TTL la limpia sola. La IP se guarda hasheada porque una dirección IP es un dato personal bajo la LFPDPPP y no hay razón operativa para conservarla legible en un almacén volátil.

CU02 A3 pide limitar la frecuencia sin exponer el catálogo masivamente; este es el mecanismo.

---

## 5. Catálogo móvil — `db 1`

| Clave | Tipo | TTL | Requisito |
|---|---|---|---|
| `movil:catalogo:{version}` | String JSON comprimido | 24 h | RF31, RNF18 |
| `movil:catalogo:actual` | String | sin TTL | RF31 |

RNF18 exige respuestas ligeras para usuarios con planes de datos limitados. La copia ligera del catálogo se arma una vez, se comprime y se sirve desde memoria; el dispositivo compara su versión con `movil:catalogo:actual` y solo descarga si difiere.

---

## Lo que NO va en Redis

Vale la pena dejarlo escrito, porque son las tentaciones habituales:

| Dato | Por qué no |
|---|---|
| Folio de pedido | Un reinicio produciría folios repetidos. Va en secuencia de PostgreSQL. |
| Carrito confirmado | Un carrito puede vivir en Redis; un pedido confirmado es una transacción. |
| Bitácora de auditoría | RN31 exige permanencia e inmutabilidad. PostgreSQL. |
| Existencias | RN16 exige atomicidad transaccional. PostgreSQL. |
| Historial de estados | RN32 exige reconstrucción completa. PostgreSQL. |
| Evidencia de entrega | Objeto binario permanente. Almacenamiento de archivos, con la referencia en PostgreSQL. |

## Operación

- `appendonly no` y `save ''`: no se persiste. Se asume que un reinicio de Redis vacía todo, y el sistema debe tolerarlo.
- `maxmemory` fijado explícitamente en ambas bases. Sin límite, la política de expulsión nunca se activa y el proceso muere por OOM en lugar de degradarse.
- Las claves de `db 0` se monitorean por conteo: un crecimiento sostenido de `lock:inv:*` indica bloqueos que no se están liberando.
