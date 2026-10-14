# Microservicios · contrato v1 (Segundo Parcial)

**Codex Innovations · Equipo 04**

Diez servicios Flask, cada uno con **una sola responsabilidad de negocio**, en su contenedor y su puerto, que atienden a la app Android (JSON) y a la app de escritorio (XML
validado con los XSD oficiales de `app_escritorio/contratos/`). Comparten PostgreSQL, Redis y MongoDB con el sistema web, que
sigue funcionando por su cuenta.

| Servicio | Puerto | Responsabilidad | Rutas (`/api/v1/…`) | Datos |
|---|---|---|---|---|
| auth | 5101 | Sesión común JWT + Redis | `auth/login`, `auth/renovar`, `auth/salir`, `auth/validar` | PostgreSQL, Redis |
| usuarios | 5102 | Perfil y consulta de usuarios | `usuarios/yo` (GET, PATCH), `usuarios`, `usuarios/{id}` | PostgreSQL |
| productos | 5103 | Catálogo comercial (solo lectura) | `productos[/{id}]` | PostgreSQL, caché Redis |
| pedidos | 5104 | Consulta y cambio de estado | `pedidos`, `pedidos/{id}`, `pedidos/{id}/historial`, `pedidos/{id}/estado` | PostgreSQL |
| entregas | 5105 | Reparto: paradas y cierre idempotente | `entregas/mias`, `entregas[/{id}]`, `entregas/{id}/resultado` | PostgreSQL, MongoDB |
| planeacion | 5106 | Viabilidad de microhubs | `candidatos[/{id}]`, `candidatos/{id}/decision`, `candidatos/{id}/simular`, `simulaciones`, `simulaciones/resumen`, `escenarios[/{id}]` | PostgreSQL, MongoDB |
| documentos | 5107 | Evidencias y archivos | `documentos`, `documentos/{id}`, `documentos/{id}/contenido`, `documentos/resumen` | MongoDB |
| zonas | 5108 | Zonas de cobertura (solo lectura) | `zonas[/{id}]` | PostgreSQL, caché Redis |
| microhubs | 5109 | Red de microhubs (solo lectura) | `microhubs[/{id}]` | PostgreSQL, caché Redis |
| seguimiento | 5110 | Rastro GPS de la entrega | `seguimiento/{id}/ubicaciones`, `seguimiento/{id}/recorrido` | MongoDB (PostgreSQL solo para el ámbito del perfil) |

## Una responsabilidad por servicio

Cada servicio responde a un solo objetivo de negocio y no mezcla temas ajenos:

| Servicio | Objetivo de negocio |
|---|---|
| auth | Quién eres y si tu sesión sigue vigente |
| usuarios | Perfil de la cuenta |
| productos | Qué se vende |
| zonas | Dónde se atiende (colonias) |
| microhubs | Desde qué puntos se atiende |
| pedidos | Ciclo de vida del pedido |
| entregas | Ejecutar la entrega y cerrarla con sus reglas |
| seguimiento | Dónde va el repartidor (GPS) |
| planeacion | Decidir si conviene abrir un microhub |
| documentos | Archivos y evidencias |

Cambios de este parcial respecto a la primera versión: `catalogos` se separó en `productos`, `zonas` y `microhubs`; el GPS salió de `entregas`
hacia `seguimiento` (las rutas pasaron de `entregas/{id}/ubicaciones|recorrido` a `seguimiento/{id}/ubicaciones|recorrido`); y se retiró
`notificaciones` para quedar en 10 servicios (el máximo del parcial). Los avisos siguen existiendo: los crea el trigger del motor en
`web_notificacion` y el portal web los muestra en su propia bandeja. `notificaciones.xsd` y sus ejemplos se conservan en el contrato v1.

Cada servicio publica `GET /health` (alias de `/salud`, también bajo `/api/v1/`) y su documentación en
**`http://localhost:51XX/api/v1/docs`** (Swagger UI, ejecutable con «Authorize» + «Try it out») y `/api/v1/openapi.json`.
Los ejemplos de Swagger son los archivos oficiales del contrato. Métodos usados: GET, POST, PUT (candidatos), PATCH
(perfil y estado de pedido) y DELETE (documentos, candidatos con baja lógica y escenarios).

Cada servicio tiene **su propio Dockerfile** (`servicios/<servicio>/Dockerfile`) y corre en su propio contenedor.

## Lo que comparten (`comun/`)

| Pieza | Archivo | Qué hace |
|---|---|---|
| Formatos | `formatos.py`, `esquemas.py` | `Accept` decide JSON o XML; todo XML de entrada se valida con los 9 XSD; DTD y entidades rechazadas |
| Autenticación | `base.py` | JWT HS256 con la misma llave que el web; Redis confirma la sesión (`auth:sesion:{id}`) y la revocación (`auth:jti:revocado:{jti}`) en cada petición |
| Autorización | `datos.py` | Permisos de la tabla `rol_permiso` (caché `cache:permisos:{rol}`, 5 min), los mismos del web |
| Errores | `base_errores.py`, `validar.py` | `{codigo, mensaje, detalles[campo, mensaje], traza_id}`; todos los errores de validación juntos |
| Límites | `base.py` | 240 solicitudes/min por IP y servicio (30 para login) en Redis; 429 con `Retry-After` |
| Caché de catálogo | `catalogo.py` | Redis (base 1, `cache:catalogo:*`) para productos, zonas y microhubs; cada servicio conserva su propia consulta |
| Registro | `base.py` | Cada petición: `logs_tecnicos` y `metricas_servicio` en MongoDB, sin tokens ni contraseñas |
| Auditoría | PostgreSQL | El servicio declara quién actúa (`app.usuario_id`, `app.rol`); los triggers del motor auditan y validan transiciones |

Los cálculos de planeación **no se duplican**: el servicio usa `sistema_web/planeacion_calc.py` y las consultas de
`sistema_web/planeacion.py`. Web, servicio y escritorio dan los mismos números.

## Datos que agrega este parcial

- `bloque_c/sql/08_microservicios.sql` (idempotente): cierre idempotente de entregas (`entrega.id_cliente_local`), evidencias y
  ubicación del cierre, tipo y referencia en `web_notificacion`, y el trigger que avisa al repartidor cuando se le asigna una entrega.
- `bloque_c/mongo/02_microservicios.js`: colecciones `documentos` y `ubicaciones_entrega` (índice 2dsphere, TTL de 180 días).
- MongoDB en uso: `documentos` (insertar, consultar, agregar), `ubicaciones_entrega` (Seguimiento: insertar en lote, agregación del recorrido),
  `sincronizaciones_moviles` (upsert por UUID: cada reintento actualiza el mismo documento), `ejecuciones_analiticas` (cada
  simulación; resumen con `$group`), `logs_tecnicos` y `metricas_servicio`.

## Integración con el sistema web

El portal web consume los servicios por HTTP con el **mismo JWT de la sesión del usuario** (`sistema_web/integracion.py`):

| Pantalla del web | Servicios que llama | Qué demuestra |
|---|---|---|
| **Microservicios** (menú del administrador, `/web/servicios`) | los 10 (`/salud`), documentos y planeación (resúmenes), zonas (XML) | estado de cada servicio, agregaciones de MongoDB y una respuesta XML real |
| **Pedido → «Entrega, recorrido y evidencias»** (`/web/servicios/pedido/<id>`) | pedidos, entregas, seguimiento, documentos | detalle, historial, recorrido GPS (MongoDB) y fotos de evidencia; adjuntar un archivo que se guarda en MongoDB |

Cada llamada muestra su código HTTP, tiempo y `X-Traza-Id`, que también queda en `logs_tecnicos` de MongoDB. Si un servicio no
responde, el web lo indica y sigue funcionando.

## Levantar y detener

Desde la raíz del repositorio:

```bash
docker compose -f docker-compose.integrado.yml up --build -d          # levantar (la primera vez construye 12 imágenes)
docker compose -f docker-compose.integrado.yml ps -a                  # todo healthy; «migraciones» termina en Exited (0)
docker compose -f docker-compose.integrado.yml logs -f entregas       # registro de un servicio
docker compose -f docker-compose.integrado.yml exec entregas python pruebas/preparar_entregas.py --cantidad 2
docker compose -f docker-compose.integrado.yml down                   # detener (conserva los datos)
docker compose -f docker-compose.integrado.yml down -v                # detener y borrar volúmenes (base desde cero)
```

Web: `http://localhost:5000`. Servicios: puertos 5101 a 5110. Cuentas: `sistema_web/README.md` (clave `Codex#2026`).
Con un volumen de PostgreSQL ya existente, el contenedor `migraciones` aplica 06, 07 y 08 sin borrar datos. Si el puerto
5000 está ocupado (por ejemplo, por `sistema_web/docker-compose.yml`), detener ese compose o usar `WEB_PORT=5050`.

### Variables de entorno

| Variable | Valor en el compose | Uso |
|---|---|---|
| `SECRET_KEY` | `${SECRET_KEY:-cambiar-en-produccion}` | Firma de los JWT; **la misma** en web y servicios (sesión común) |
| `PG_DSN` | `host=postgres … dbname=microhubs_p1 user=microhubs` | PostgreSQL |
| `REDIS_URL` | `redis://redis:6379` | Sesiones y revocación (db 0), caché y límites (db 1) |
| `MONGO_URL` | `mongodb://mongo:27017/microhubs_eventos` | Documentos, GPS, simulaciones, sincronizaciones, logs |
| `POSTGRES_PASSWORD` | `${POSTGRES_PASSWORD:-microhubs_dev}` | Clave de PostgreSQL |
| `WEB_PORT` | `5000` | Puerto del portal web en el equipo |
| `LIMITE_POR_MINUTO`, `LIMITE_LOGIN_POR_MINUTO` | 240 y 30 (por omisión) | Límite de consumo por IP |
| `MICROSERVICIOS_URL` (web) | `http://{servicio}:{puerto}` | Cómo el web encuentra a los servicios en la red de Docker |

Redes: `datos` (interna: PostgreSQL, Redis y MongoDB sin puertos al equipo) y `publica` (web y servicios). Volúmenes:
`datos_pg` y `datos_mongo`.

## Pruebas

**Cambian datos: úsenlas en una base de pruebas** (requieren PostgreSQL y Redis con el modelo 01 a 08).

```bash
pip install -r servicios/requirements.txt mongomock
cd servicios
python -m unittest -v pruebas.test_unitarias          # 14 · sin bases de datos: formatos, validación, XSD, OpenAPI, cálculos
python -m unittest -v pruebas.test_contrato           # 7  · los 10 servicios: recorridos de escritorio y Android, XML vs XSD, JSON vs ejemplos
python -m unittest -v pruebas.test_web_integracion    # 5  · el web llamando a los servicios por HTTP real
```

## Evidencias de petición y respuesta

`pruebas/evidencias.py` ejecuta **93 casos reales** contra los servicios desplegados (correctos, datos inválidos, registros
inexistentes, sin permiso, token inválido, sesión revocada, errores de negocio, límite de consumo) y documenta de cada uno la
petición, la respuesta y lo que quedó en PostgreSQL, MongoDB o Redis:

```bash
docker compose -f docker-compose.integrado.yml exec entregas python pruebas/evidencias.py
docker compose -f docker-compose.integrado.yml cp entregas:/tmp/evidencias ./evidencias
```

Resultado en `./evidencias`: `evidencias.html` (para capturas), `evidencias.md` (para el reporte), `pruebas.md` (tabla de
casos con esperado contra obtenido) y `evidencias.json`. Al final agota a propósito el límite de consumo de catálogos:
espera un minuto antes de volver a usar ese servicio desde el mismo contenedor.

Para probar las apps Android y de escritorio contra estos servicios, ver `INSTRUCCIONES_PARTE_B.md` en la raíz.

## Decisiones

- **HTTP en los puertos locales.** Las apps permiten HTTP solo hacia `localhost` (escritorio) y `10.0.2.2` o el host fijado al
  compilar (Android debug). TLS con proxy inverso queda para el despliegue en nube del Tercer Parcial.
- **Token de renovación opaco** (`rt_…`) que se guarda en Redis como hash y sirve una sola vez; no puede usarse como acceso.
- **Notificaciones automáticas por trigger**, no por llamada entre servicios: llegan aunque el cambio lo haga el web, un servicio
  o un script.
- **MongoDB no bloquea la operación de pedidos**: si no responde, el cierre de entrega se aplica en PostgreSQL y solo se pierde
  el rastro analítico; los servicios cuyo almacén es MongoDB (documentos, recorrido, resumen) responden 503.

## Límites conocidos

- Las pruebas automáticas usan MongoDB simulado; los validadores `$jsonSchema` solo los aplica un MongoDB real.
- La contraseña de demostración es común a todas las cuentas y `SECRET_KEY` tiene un valor por omisión: cambiar ambos fuera
  de desarrollo.
- Catálogo en caché hasta 5 minutos: un cambio hecho en el web tarda ese tiempo en verse en las apps.

## Inventario y revisión documental

El código expone 45 operaciones de negocio por método y ruta; ver `INVENTARIO_ENDPOINTS.md`. Hay 10 contenedores de microservicios, 1 web, 3 almacenes y 1 de migraciones: 15 definidos, 14 continuos. Web espera migraciones y Redis; los diez servicios esperan migraciones, Redis y MongoDB.

Los nueve XSD se conservan: `catalogos.xsd` atiende tres servicios y `entregas.xsd` también contiene estructuras de Seguimiento. `notificaciones.xsd` no representa un servicio activo.
