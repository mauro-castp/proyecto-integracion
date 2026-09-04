# Sistema web mínimo funcional

**Plataforma de Microhubs y Comercio de Proximidad**
Codex Innovations · Equipo 04 · Entregable 11

Aplicación Flask que ejecuta el proceso comprometido de punta a punta: consulta pública, alta de cliente, carrito, confirmación con asignación automática de microhub, preparación, cierre de entrega con cobro, indicadores y bitácora.

**33 de 33 comprobaciones de extremo a extremo pasan** contra la aplicación corriendo, con navegador real.

---

## Levantar

### Con Docker (recomendado)

```bash
cp .env.ejemplo .env          # y ajustar SECRET_KEY
docker compose up --build
```

Un solo comando levanta web, PostgreSQL, Redis y MongoDB (RF42, RNF05). Los scripts del Bloque C se ejecutan solos en el primer arranque, así que la base queda con el modelo y los datos de las cuatro colonias.

Abre `http://localhost:5000`.

### Sin Docker

```bash
pip install -r requirements.txt
export PG_DSN="host=127.0.0.1 dbname=microhubs_p1 user=postgres password=..."
export REDIS_URL="redis://127.0.0.1:6379"
python3 app.py
```

Requiere que la base ya tenga cargados los scripts `01` a `04` del Bloque C.

## Verificar

```bash
python3 prueba_e2e.py     # requiere: pip install playwright && playwright install chromium
curl localhost:5000/salud # RF47
```

## Cuentas

Contraseña de todas: `Codex#2026`

| Correo | Perfil | Qué puede hacer |
|---|---|---|
| `admin@codex.mx` | Administrador | Todo: usuarios, parámetros, indicadores, bitácora |
| `operador.mh01@codex.mx` | Operador MH-01 | Bandeja e inventario **de su microhub** |
| `operador.mh02@codex.mx` | Operador MH-02 | Lo mismo, otro ámbito |
| `planeador@codex.mx` | Planeador | Pendientes de asignación, indicadores |
| `auditor@codex.mx` | Auditor | Bitácora, solo lectura |

Los 40 clientes de la semilla usan la misma contraseña. Para obtener uno:

```sql
SELECT u.correo FROM microhubs.usuario u
  JOIN microhubs.cliente c ON c.usuario_id = u.id
  JOIN microhubs.rol r ON r.id = u.rol_id
 WHERE r.clave = 'cliente' LIMIT 1;
```

---

## Qué demostrar el día de la revisión

Cuatro recorridos que muestran las reglas funcionando, no solo pantallas:

**1. El código postal ambiguo.** En Cobertura, consulta `64103`. En vez de responder sí o no, pregunta cuál de las dos colonias, porque Valles y Paseo lo comparten con ticket mínimo distinto.

**2. El ticket mínimo.** Como cliente, agrega un producto barato y ve al carrito: dice cuánto falta y no ofrece confirmar. Agrega más y aparece el botón.

**3. El ámbito no depende del menú.** Entra como `operador.mh01@codex.mx` y escribe `localhost:5000/admin/parametros` en la barra de direcciones. Devuelve 403 aunque la opción no esté en el menú, y el intento aparece en la bitácora. Esto es HU10 CA2.

**4. Un parámetro sin recompilar.** Como administrador, en Parámetros baja `ticket_minimo` a 40. Vuelve al carrito que no alcanzaba: ahora sí se puede confirmar. Nadie reinició nada.

---

## Arquitectura de la aplicación

Tres módulos, unas 1,250 líneas:

| Archivo | Responsabilidad |
|---|---|
| `nucleo.py` | Conexión, sesión JWT, permisos, traducción de errores |
| `rutas.py` | Los cinco blueprints |
| `app.py` | Ensamblado, filtros de plantilla, manejo de errores, `/salud` |

### Por qué no hay ORM

Las invariantes del negocio viven en PostgreSQL como restricciones, funciones y triggers. La aplicación abre la transacción, declara quién actúa y llama a la función. Un ORM añadiría una capa de traducción sin resolver nada, y tentaría a reimplementar en Python reglas que ya están en el motor.

Ejemplo concreto: confirmar un pedido no calcula qué microhub gana. Inserta el pedido y llama a `fn_asignar_pedido`, que evalúa candidatos, aplica el desempate, descuenta inventario y registra la decisión en una sola transacción.

### El punto de integración que importa

Cada conexión fija tres variables de sesión antes de trabajar:

```sql
SET app.usuario_id = '7';
SET app.rol = 'operador';
SET app.ip_origen = '10.0.0.4';
```

Los triggers de auditoría e historial las leen. Sin ellas la bitácora queda sin autor y el trigger de transición no puede validar el rol. Es la costura entre la aplicación y el modelo, y está en `nucleo.conexion()`.

### Los errores del motor se traducen

Cuando PostgreSQL rechaza una operación, el mensaje técnico no sirve al usuario. `mensaje_de_error()` traduce las violaciones conocidas: `ck_inv_existencia` se vuelve "no hay existencia suficiente", `RN17` se vuelve "alguien tomó la última unidad mientras confirmabas".

Cuando el mensaje del motor ya explica la regla en español, se usa tal cual en vez de reescribirlo. Duplicar el texto sería otro lugar donde la regla puede quedar desactualizada.

### El menú se construye desde permisos

El contexto de plantilla carga los permisos del rol y las plantillas dibujan solo los enlaces autorizados. **Eso no es control de acceso**: cada ruta lleva el decorador `@requiere(...)`, que verifica el permiso y registra el intento fallido. Ocultar el enlace es comodidad; cerrar la ruta es la seguridad.

### Dónde vive cada cosa

El carrito está en Redis: perderlo solo cuesta armarlo otra vez. El pedido confirmado está en PostgreSQL, porque es una transacción. Es el mismo criterio del entregable de claves aplicado a un caso concreto.

---

## Cobertura de requisitos

| Requisito | Dónde |
|---|---|
| RF03, RF04 · JWT y revocación | `nucleo.emitir_token`, `revocar_token` |
| RF06 · Bloqueo por intentos | `rutas.entrar`, contador en Redis y en PostgreSQL |
| RF07 · Bitácora | Triggers del modelo, más `auditar()` para eventos de sesión |
| RF11 · Inventario | `rutas.inventario` |
| RF12, RF13 · Cobertura y catálogo público | `rutas.catalogo`, `rutas.cobertura` |
| RF14, RF15 · Pedido y asignación | `rutas.confirmar` → `fn_asignar_pedido` |
| RF16 · Máquina de estados | `rutas.cambiar_estado` → trigger del modelo |
| RF18 · Cierre de entrega | `rutas.cerrar` |
| RF19 · Indicadores | `rutas.indicadores` sobre las vistas del modelo |
| RF20 · Consulta de bitácora | `rutas.bitacora` |
| RF21 · Configuración | `rutas.parametros` |
| RF47 · Endpoint de salud | `app.salud` |
| RNF23 · Control de acceso consistente | Decorador `@requiere` en cada ruta |

---

## Imágenes del catálogo

Las fotografías están en `static/productos/` y se relacionan con el catálogo
mediante la clave interna del producto, por ejemplo `AB-001.jpg` o
`HI-004.webp`. Para agregar o sustituir una imagen basta con usar la misma clave
y una extensión compatible (`jpg`, `jpeg`, `png` o `webp`) y reconstruir el
contenedor. Si un producto no tiene fotografía se muestra automáticamente
`sin-imagen.svg`. Falta la foto de `LI-008` (Bolsas para basura) — no se encontró una fotografía de producto (empaquetado) libre de uso; los bancos de imágenes solo tienen fotos de bolsas ya usadas en la calle, que no sirven para el catálogo.

---

## Lo que falta

1. **Recuperación de contraseña (RF05).** El diseño de claves Redis la contempla y la base tiene el parámetro de vigencia, pero la pantalla no está.
2. **Entrega parcial por líneas.** El cierre registra el resultado parcial y el monto, pero no permite marcar cuáles líneas se devolvieron; usa el reintegro completo. `entrega_linea` ya existe en el modelo.
3. **Asignación a repartidor (RF32).** El cierre lo hace el operador, que es lo previsto para el Primer Parcial. El perfil Repartidor llega en el Segundo.
4. **MongoDB conectado.** El compose lo levanta y las colecciones se crean, pero la aplicación todavía no escribe eventos ahí. La traza de asignación se guarda en PostgreSQL; falta el detalle de candidatos.
5. **Docker probado.** ~~El `docker-compose.yml` está escrito pero no se ejecutó~~ — verificado el 2026-09-01: los 4 contenedores levantan sanos y las 26 aserciones de reglas de negocio pasan contra Postgres real.
