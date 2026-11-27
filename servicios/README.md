# Microservicios · contrato v1

**Codex Innovations · Equipo 04**

Veintiséis servicios Flask (diez del Segundo Parcial, cinco de la Ola 1 y ocho de la Ola 2 del Tercer Parcial, y tres de la Ola 3 de la entrega final), cada uno con **una sola responsabilidad de negocio**, en su contenedor y su puerto, que atienden a la app Android (JSON) y a la app de escritorio (XML
validado con los XSD oficiales de `app_escritorio/contratos/`). Comparten PostgreSQL, Redis y MongoDB con el sistema web, que
sigue funcionando por su cuenta.

| Servicio | Puerto | Responsabilidad | Rutas (`/api/v1/…`) | Datos |
|---|---|---|---|---|
| auth | 5101 | Sesión común JWT + Redis | `auth/login`, `auth/renovar`, `auth/salir`, `auth/validar` | PostgreSQL, Redis |
| usuarios | 5102 | Perfil y consulta de usuarios | `usuarios/yo` (GET, PATCH), `usuarios`, `usuarios/{id}` | PostgreSQL |
| productos | 5103 | Catálogo comercial (solo lectura) | `productos[/{id}]` | PostgreSQL, caché Redis |
| pedidos | 5104 | Consulta y cambio de estado; alimenta al análisis | `pedidos`, `pedidos/{id}`, `pedidos/{id}/historial`, `pedidos/{id}/estado`, `pedidos/resumen`, `pedidos/ventas`, `pedidos/listos` | PostgreSQL |
| entregas | 5105 | Reparto: paradas y cierre idempotente | `entregas/mias`, `entregas[/{id}]`, `entregas/{id}/resultado`, `entregas/repartidores`, `entregas/asignaciones` | PostgreSQL, MongoDB |
| planeacion | 5106 | Viabilidad de microhubs | `candidatos[/{id}]`, `candidatos/{id}/decision`, `candidatos/{id}/simular`, `simulaciones`, `simulaciones/resumen`, `escenarios[/{id}]` | PostgreSQL, MongoDB |
| documentos | 5107 | Evidencias y archivos | `documentos`, `documentos/{id}`, `documentos/{id}/contenido`, `documentos/resumen` | MongoDB |
| zonas | 5108 | Zonas de cobertura (solo lectura) | `zonas[/{id}]` | PostgreSQL, caché Redis |
| microhubs | 5109 | Red de microhubs (solo lectura) | `microhubs[/{id}]` | PostgreSQL, caché Redis |
| seguimiento | 5110 | Rastro GPS de la entrega | `seguimiento/{id}/ubicaciones`, `seguimiento/{id}/recorrido` | MongoDB (PostgreSQL solo para el ámbito del perfil) |
| inventario | 5111 | Existencias, movimientos, transferencias, reservas y alertas | `inventario`, `inventario/{mh}/{producto}[/minimo]`, `inventario/movimientos`, `inventario/transferencias`, `inventario/reservas[/{id}/liberar]`, `inventario/alertas`, `inventario/quiebres` | PostgreSQL |
| precios | 5112 | Política de precios: listas por zona, promociones, márgenes y sensibilidad | `precios/listas[/{id}[/items/{producto}]]`, `precios/vigente`, `precios/calcular`, `precios/promociones[/{id}]`, `precios/historial`, `precios/margenes`, `precios/sensibilidad` | PostgreSQL (precio base y categoría desde productos) |
| proveedores | 5113 | Quién surte, qué, a qué precio y qué tan bien cumple | `proveedores[/{id}]`, `proveedores/{id}/catalogo[/{producto}]`, `proveedores/ofertas`, `proveedores/{id}/evaluaciones` | PostgreSQL |
| abastecimiento | 5114 | Ciclo de reposición: necesidades, solicitudes, órdenes y recepción | `abastecimiento/necesidades`, `abastecimiento/solicitudes[/{id}[/decision\|/ordenar]]`, `abastecimiento/ordenes[/{id}[/recepcion\|/cancelar]]`, `abastecimiento/seguimiento` | PostgreSQL (alertas desde inventario, ofertas desde proveedores) |
| notificaciones | 5124 | Bandeja de avisos, envío por persona o rol y preferencias | `notificaciones[/{id}[/leer]]`, `notificaciones/conteo`, `notificaciones/leer-todas`, `notificaciones/preferencias[/{tipo}]` | PostgreSQL |
| demanda | 5115 | Cuánto se pide, dónde y cuándo; patrón semanal, proyección con banda de error y demanda potencial | `demanda/observaciones`, `demanda/resumen`, `demanda/patrones`, `demanda/proyeccion`, `demanda/comparacion`, `demanda/potencial`, `demanda/sincronizacion`, `demanda/supuestos` | PostgreSQL (pedidos desde el servicio de pedidos) |
| cobertura | 5116 | Qué zonas y hogares cubre la red, evaluación de ubicaciones nuevas y escenarios de radio | `cobertura/zonas`, `cobertura/resumen`, `cobertura/punto`, `cobertura/candidatos`, `cobertura/evaluaciones[/{id}]`, `cobertura/escenarios`, `cobertura/zonas/{id}/poblacion`, `cobertura/supuestos` | PostgreSQL (zonas, microhubs y candidatas desde sus servicios) |
| capacidad | 5117 | Cuántos pedidos procesa un microhub, utilización y cuello de botella | `capacidad/recursos[/{mh}]`, `capacidad/microhubs[/{mh}]`, `capacidad/simulaciones`, `capacidad/cargas`, `capacidad/supuestos` | PostgreSQL (carga desde pedidos) |
| rutas | 5118 | Quién entrega qué y en qué orden: agrupar por zona, asignar repartidor, ordenar paradas y ajustar ante incidencias | `rutas/planes[/{id}[/confirmar\|/cancelar\|/ajustes]]` (confirmar con `despachar` crea las entregas), `rutas/comparaciones`, `rutas/supuestos` | PostgreSQL (pedidos listos, repartidores y microhubs desde sus servicios) |
| costos | 5119 | Cuánto cuesta operar: conceptos fijos y variables, costo por pedido y por entrega, rentabilidad | `costos/conceptos[/{id}]`, `costos/resumen`, `costos/unitarios`, `costos/rentabilidad`, `costos/sensibilidad`, `costos/supuestos` | PostgreSQL |
| punto-equilibrio | 5120 | Cuántos pedidos hacen falta para no perder y si la demanda esperada los alcanza, paso a paso | `punto-equilibrio/calculos`, `punto-equilibrio/microhubs`, `punto-equilibrio/sensibilidad`, `punto-equilibrio/escenarios[/{id}]`, `punto-equilibrio/comparacion`, `punto-equilibrio/supuestos` | PostgreSQL (costos, demanda y cobertura desde sus servicios) |
| simulacion | 5121 | Qué tan estable es la operación cuando la demanda varía y falta personal (Monte Carlo, asíncrona y reproducible) | `simulacion/ejecuciones[/{id}[/cancelar\|/repetir]]`, `simulacion/comparacion`, `simulacion/supuestos` | PostgreSQL (entrada desde punto-equilibrio y capacidad) |
| surtido | 5122 | Qué productos tener y cuántos: ABC, rotación, margen, quiebres y recomendaciones con espacio y presupuesto | `surtido/abc`, `surtido/analisis`, `surtido/recomendaciones[/{id}]`, `surtido/restricciones/{mh}`, `surtido/supuestos` | PostgreSQL (ventas, existencias, catálogo y costos desde sus servicios) |
| reportes | 5123 | Reportes operativos, logísticos, comerciales y financieros, indicadores, gráficas y exportación a CSV, Excel y PDF | `reportes`, `reportes/indicadores`, `reportes/{clave}[/grafica\|/exportar]`, `reportes/exportaciones[/{id}/enlace]` (archivo en el bucket) | PostgreSQL (bitácora de exportaciones); los datos, de sus servicios dueños |
| sincronizacion | 5125 | Aplica sin duplicar lo que Android y escritorio hicieron sin conexión; conflictos y reintentos | `sincronizacion/lotes[/{id}]`, `sincronizacion/pendientes`, `sincronizacion/conflictos`, `sincronizacion/estado`, `sincronizacion/supuestos` | PostgreSQL |
| auditoria-monitoreo | 5126 | Bitácora y trazabilidad; salud, disponibilidad, métricas y alertas de todos los servicios | `auditoria[/accesos\|/trazabilidad/…]`, `monitoreo/estado`, `monitoreo/disponibilidad`, `monitoreo/metricas`, `monitoreo/alertas[/{id}/reconocer]`, `monitoreo/verificaciones` | PostgreSQL, MongoDB |

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
| inventario | Cuántas unidades hay de cada producto en cada microhub y cómo se mueven |
| precios | A qué precio se vende cada producto en cada zona |
| proveedores | Quién nos surte, a qué precio y con qué plazo |
| abastecimiento | Reponer lo que falta, desde la solicitud hasta la recepción |
| notificaciones | Que cada persona reciba, lea y administre sus avisos |
| demanda | Cuánto se pide, dónde y cuándo, y cuánto se podría pedir |
| cobertura | A cuántos hogares llega la red y qué sumaría una ubicación nueva |
| capacidad | Cuántos pedidos puede procesar un microhub y qué tan cerca está de saturarse |
| rutas | En qué orden y con quién sale cada pedido listo |
| costos | Cuánto cuesta operar un microhub o una ubicación candidata |
| punto-equilibrio | Cuántos pedidos hacen falta para no perder dinero |
| simulacion | Qué tan estable es la operación ante la variación de la demanda y del personal |
| surtido | Qué productos tener, cuántos y cuáles sobran |

Cambios respecto a la primera versión: `catalogos` se separó en `productos`, `zonas` y `microhubs`; el GPS salió de `entregas`
hacia `seguimiento` (las rutas pasaron de `entregas/{id}/ubicaciones|recorrido` a `seguimiento/{id}/ubicaciones|recorrido`); en el Segundo
Parcial `notificaciones` se había retirado para quedar en 10 servicios, y en la Ola 1 vuelve en el puerto 5124 con su bandeja, envío por
rol y preferencias. Los avisos automáticos siguen naciendo en triggers de PostgreSQL (`web_notificacion`) y el portal web los muestra en
su propia bandeja; el servicio ofrece esa misma bandeja a las apps.

La Ola 2 agrega los ocho servicios de análisis y planeación (puertos 5115 a 5122). Ninguno lee las tablas de otro: lo que no es suyo lo pide por HTTP con el JWT
de quien consulta. Cada uno publica sus **supuestos** (`GET /<servicio>/supuestos`: valor, si es medido, supuesto o normativo, justificación y cómo
calibrarlo) y cada resultado dice cuáles usó; ver [`SUPUESTOS.md`](SUPUESTOS.md) y los escenarios en `evidencias/ola2/escenarios.md`.

La Ola 3 completa los 26 servicios del plan:

- **auditoria-monitoreo** consulta la bitácora que escriben los triggers (y, para la línea de tiempo, `historial_estatus` y `movimiento_inventario`, que son
  bitácoras de solo lectura). Cada 30 s pregunta `/salud` a todos, guarda estado, tiempo y dependencias, y abre y cierra alertas sola (caído, degradado,
  dependencia con falla, latencia y errores 5xx). Con Redis caído sigue verificando.
- **reportes** no lee tablas de otros: arma cada reporte con las respuestas de los servicios dueños y el JWT de quien lo pide, así que cada uno aplica su
  alcance. Si un servicio no responde, el indicador falta y se nombra; un reporte nunca inventa datos.
- **sincronizacion** aplica en el orden en que ocurrieron las operaciones hechas sin conexión llamando al servicio dueño. `(dispositivo, operacion_uuid)` es
  único (reenviar no duplica), un conflicto lo gana el servidor y lo que no se pudo aplicar queda pendiente para reintentar.

**Salud:** los 26 informan PostgreSQL, Redis, MongoDB y bucket, y quedan degradados solo si falla una dependencia que necesitan. Además de
`/salud` publican `/health/live`, `/health/ready`, `/health/database`, `/health/redis`, `/health/mongodb` y `/health/storage`.

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
| Llamadas entre servicios | `clientes.py` | Un servicio le pregunta a otro por HTTP con el mismo JWT y la misma traza (`llamar`, `exigir`); `mapa` trae un catálogo completo con caché para poner nombres a ids |
| Caché de catálogo | `catalogo.py` | Redis (base 1, `cache:catalogo:*`) para productos, zonas y microhubs; cada servicio conserva su propia consulta |
| Registro | `base.py` | Cada petición: `logs_tecnicos` y `metricas_servicio` en MongoDB, sin tokens ni contraseñas |
| Auditoría | PostgreSQL | El servicio declara quién actúa (`app.usuario_id`, `app.rol`); los triggers del motor auditan y validan transiciones |

Los servicios **no dependen del portal**: usan `comun/planeacion_calc.py` (fórmulas puras) y `comun/consultas_planeacion.py`, y sus
imágenes se construyen sin `sistema_web/`. El portal conserva su propia copia de las fórmulas; la prueba `IndependenciaDelPortal`
exige que sean idénticas, así que web, servicio y escritorio dan los mismos números.

## Datos que agrega este parcial

- `bloque_c/sql/08_microservicios.sql` (idempotente): cierre idempotente de entregas (`entrega.id_cliente_local`), evidencias y
  ubicación del cierre, tipo y referencia en `web_notificacion`, y el trigger que avisa al repartidor cuando se le asigna una entrega.
- `bloque_c/sql/09_ola1_flujo_negocio.sql` (idempotente): reservas de inventario y la vista `v_inventario_disponible`, listas de precios, promociones,
  proveedores, solicitudes y órdenes de compra, preferencias de avisos, los triggers de aviso (faltante, solicitud, orden) y los permisos nuevos.
- `bloque_c/sql/10_ola2_analitica.sql` (idempotente): demanda por día, zona y categoría (con historia sintética de demostración, marcada como tal), población por zona,
  evaluaciones de cobertura, personal por microhub, conceptos de costo, escenarios de equilibrio, ejecuciones de simulación, restricciones y recomendaciones de surtido,
  planes de despacho, `supuesto_documentado` (de dónde sale y cómo se calibra cada supuesto), parámetros nuevos en `configuracion` y permisos.
- `bloque_c/sql/11_ola3_observabilidad.sql` (idempotente): verificaciones y alertas del monitoreo, bitácora de exportaciones, lotes y operaciones de sincronización,
  parámetros y permisos nuevos, la acción de bitácora `descarga` y la zona horaria de la base en Monterrey (para que `current_date` sea el día local).
- `bloque_c/sql/12_rendimiento.sql` (entrega final): `fn_pedidos_visibles` en SQL que el planificador integra a la consulta e índices `ix_pedido_dia_local`
  e `ix_detalle_pedido_cubriente` (ver `evidencias/volumen/LEEME.md`).
- `bloque_c/sql/13_entrega_final.sql`: ruta del archivo de cada exportación de reportes en el bucket.
- `bloque_c/sql/14_pedidos_api.sql`: `pedido.operacion_uuid`, para que reenviar el mismo pedido por la API no lo duplique.
- `bloque_c/sql/15_archivos_bucket.sql`: los archivos del portal van al almacén de objetos.
- `bloque_c/sql/16_apps_cliente.sql`: confirmación de recepción y soporte de las pantallas nuevas de las apps.
- `bloque_c/sql/17_perfil_proveedor.sql`: rol `proveedor`, permiso `proveedor.portal` y la liga entre cuenta y proveedor.
- `bloque_c/sql/15_archivos_bucket.sql`: retira la tabla donde el portal guardaba archivos; ahora van al almacén (servicio `documentos`).
- `bloque_c/sql/16_apps_cliente.sql`: `sincronizacion.usar` para el cliente (pedidos hechos sin red en la app Android). Lo aplica `migrar.py`.
- Cierre de la entrega final: `POST capacidad/colas` (M/M/1 y M/M/c, `comun/colas.py`), `POST entregas/recepciones` (el cliente confirma
  la recepción), el tipo `pedido_nuevo` en sincronización y el contrato XML `operacion.xsd`/`colas.xsd` (`contratos/ola5.py`). Pruebas:
  `pruebas.test_apps_cliente`, `test_unitarias_ola2.Colas` y `test_ola2.T4Capacidad.test_colas_mm1_y_mmc`.
- `bloque_c/mongo/03_documentos_nube.js`: validador de `documentos` para los archivos en Cloud Storage (en MongoDB quedan solo sus datos).
- `bloque_c/mongo/02_microservicios.js`: colecciones `documentos` y `ubicaciones_entrega` (índice 2dsphere, TTL de 180 días).
- MongoDB en uso: `documentos` (insertar, consultar, agregar), `ubicaciones_entrega` (Seguimiento: insertar en lote, agregación del recorrido),
  `sincronizaciones_moviles` (upsert por UUID: cada reintento actualiza el mismo documento), `ejecuciones_analiticas` (cada
  simulación; resumen con `$group`), `logs_tecnicos` y `metricas_servicio`.

## Integración con el sistema web

El portal web consume los servicios por HTTP con el **mismo JWT de la sesión del usuario** (`sistema_web/integracion.py`):

| Pantalla del web | Servicios que llama | Qué demuestra |
|---|---|---|
| **Monitoreo** (`/web/servicios/monitoreo`) | auditoria-monitoreo | panel central: estado, disponibilidad, tiempos, dependencias caídas y alertas; verificar y reconocer |
| **Microservicios** (menú del administrador, `/web/servicios`) | los 26 (`/salud`), documentos y planeación (resúmenes), zonas (XML) | estado de cada servicio, agregaciones de MongoDB y una respuesta XML real |
| **Pedido → «Entrega, recorrido y evidencias»** (`/web/servicios/pedido/<id>`) | pedidos, entregas, seguimiento, documentos | detalle, historial, recorrido GPS (MongoDB) y fotos de evidencia; adjuntar un archivo que se guarda en MongoDB |

Cada llamada muestra su código HTTP, tiempo y `X-Traza-Id`, que también queda en `logs_tecnicos` de MongoDB. Si un servicio no
responde, el web lo indica y sigue funcionando.

## Levantar y detener

Desde la raíz del repositorio:

```bash
docker compose -f docker-compose.integrado.yml up --build -d          # levantar (la primera vez construye las imágenes de los 26 servicios y del portal)
docker compose -f docker-compose.integrado.yml ps -a                  # todo healthy; «migraciones» termina en Exited (0)
docker compose -f docker-compose.integrado.yml logs -f entregas       # registro de un servicio
docker compose -f docker-compose.integrado.yml exec entregas python pruebas/preparar_entregas.py --cantidad 2
docker compose -f docker-compose.integrado.yml down                   # detener (conserva los datos)
docker compose -f docker-compose.integrado.yml down -v                # detener y borrar volúmenes (base desde cero)
```

Web: `http://localhost:5000`. Servicios: puertos 5101 a 5126. Cuentas: `sistema_web/README.md` (clave `Codex#2026`, solo para desarrollo local; el
despliegue en la nube la cambia, ver [`deploy/gcp/LEEME.md`](../deploy/gcp/LEEME.md)).
Con un volumen de PostgreSQL ya existente, el contenedor `migraciones` aplica 06 a 13 sin borrar datos. Si el puerto
5000 está ocupado (por ejemplo, por `sistema_web/docker-compose.yml`), detener ese compose o usar `WEB_PORT=5050`.

### Variables de entorno

| Variable | Valor en el compose | Uso |
|---|---|---|
| `SECRET_KEY` | `${SECRET_KEY:-cambiar-en-produccion}` | Firma de los JWT; **la misma** en web y servicios (sesión común) |
| `PG_DSN` | `host=postgres … dbname=microhubs_p1 user=microhubs` | PostgreSQL |
| `REDIS_URL` | `redis://redis:6379` | Sesiones y revocación (db 0), caché y límites (db 1) |
| `MONGO_URL` | `mongodb://mongo:27017/microhubs_eventos` | Documentos, GPS, simulaciones, sincronizaciones, logs |
| `POSTGRES_PASSWORD` | `${POSTGRES_PASSWORD:-microhubs_dev}` | Clave de PostgreSQL |
| `ALMACEN`, `GCS_BUCKET` | `local` y vacío | Dónde guarda los archivos `documentos`: carpeta del contenedor o bucket de Cloud Storage |
| `URL_FIRMADA_SEGUNDOS` | 300 | Vigencia del enlace firmado de descarga |
| `VERSION_DESPLEGADA` | 1.0.0 | La versión que informa `/salud` |
| `MONITOR_AUTO` | 1 | `0` apaga la verificación periódica del monitoreo (pruebas) |
| `WEB_PORT` | `5000` | Puerto del portal web en el equipo |
| `LIMITE_POR_MINUTO`, `LIMITE_LOGIN_POR_MINUTO` | 240 y 30 (por omisión) | Límite de consumo por IP |
| `MICROSERVICIOS_URL` (web y servicios) | `http://{servicio}:{puerto}` | Cómo el web y cada servicio encuentran a los demás en la red de Docker |
| `DETRAS_DE_PROXY` | `0` (`1` en la nube) | Número de proxies de confianza: con Nginx delante, la IP del cliente sale de `X-Forwarded-For` (límite por IP y bitácora) |

Redes: `datos` (interna: PostgreSQL, Redis y MongoDB sin puertos al equipo) y `publica` (web y servicios). Volúmenes:
`datos_pg` y `datos_mongo`.

## Pruebas

**Cambian datos: úsenlas en una base de pruebas** (requieren PostgreSQL y Redis con el modelo 01 a 11).

```bash
pip install -r servicios/requirements.txt mongomock
cd servicios
python -m unittest -v pruebas.test_unitarias          # 37 · sin bases de datos: formatos, validación, XSD, OpenAPI, precios, reposición, cliente entre servicios y ejemplos
python -m unittest -v pruebas.test_unitarias_ola2     # 65 · sin bases de datos: las fórmulas de la Ola 2
python -m unittest -v pruebas.test_almacen            # 31 · archivos en el bucket: URL firmada, caducidad, manipulación y bucket caído
python -m unittest -v pruebas.test_contrato           # 7  · los 26 servicios: recorridos de escritorio y Android, XML vs XSD, JSON vs ejemplos
python -m unittest -v pruebas.test_web_integracion    # 8  · el web llamando a los servicios por HTTP real, con el panel de monitoreo
python -m unittest -v pruebas.test_ola1               # 24 · inventario, precios, proveedores, abastecimiento y notificaciones, con permisos por perfil
python -m unittest -v pruebas.test_ola2               # 102 · los ocho servicios de la Ola 2
python -m unittest -v pruebas.test_ola3               # 74 · monitoreo, auditoría, reportes y sincronización: servicio caído, conflictos, idempotencia
python -m unittest -v pruebas.test_nube               # contra el bucket real, en la VM (ver deploy/gcp/LEEME.md)
```

Entrega final (contra la plataforma en marcha; cambian datos):

```bash
python pruebas/procesos_integrales.py      # P1, P2 y P3 de punta a punta → evidencias/procesos/
python pruebas/demo_fallos_infra.py       # servicio, Redis, MongoDB, PostgreSQL, bucket y tiempo excedido → evidencias/fallos/
python pruebas/medir_volumen.py --etiqueta 100k  # tras bloque_c/scripts/generar_volumen.py → evidencias/volumen/
python pruebas/benchmark_algoritmos.py    # rutas y Monte Carlo, sin bases → evidencias/algoritmos/
```

Para correr las pruebas sin instalar nada, dentro de la red de Docker del sistema integrado (`servicios/pruebas/correr.sh`).

## Evidencias de petición y respuesta

`pruebas/evidencias.py` ejecuta **403 casos reales** contra los servicios desplegados (correctos, datos inválidos, registros inexistentes, sin permiso,
token inválido, sesión revocada, errores de negocio, límite de consumo) y documenta de cada uno la petición, la respuesta y lo que quedó en PostgreSQL,
MongoDB o Redis. En la corrida adjunta pasan **403 de 403**.

```bash
servicios/pruebas/correr.sh evidencias ola3
```

Resultado en `./evidencias/ola3` (las corridas anteriores se conservan en `./evidencias/ola1` y `./evidencias/ola2`): `evidencias.html` (para capturas),
`evidencias.md` (para el reporte), `pruebas.md` (tabla de casos con esperado contra obtenido) y `evidencias.json`. Al final agota a propósito el límite de
consumo de catálogos: espera un minuto antes de volver a usar ese servicio desde el mismo contenedor.

Para probar las apps Android y de escritorio contra estos servicios, ver `INSTRUCCIONES_PARTE_B.md` en la raíz.

La corrida principal se complementa con `pruebas/evidencias.py --complementarias` (3 casos: `DOC-11`, `PLA-17` y `USR-08`, en `evidencias/ola3/complementarias/`) para que todas las operaciones tengan evidencia; ver `INVENTARIO_ENDPOINTS.md`, que escribe `pruebas/generar_inventario.py` a partir del código y de esos casos. La corrida del 13 de octubre (93 casos) se conserva en `evidencias/` porque el reporte del Segundo Parcial cita sus números.

## Decisiones

- **HTTP en los puertos locales.** Las apps permiten HTTP solo hacia `localhost` (escritorio) y `10.0.2.2` o el host fijado al
  compilar (Android debug). En la nube, Nginx es la única puerta (80/443) y los servicios solo escuchan en
  127.0.0.1; ver [`deploy/gcp/LEEME.md`](../deploy/gcp/LEEME.md) (el certificado HTTPS es un paso opcional del instalador).
- **Token de renovación opaco** (`rt_…`) que se guarda en Redis como hash y sirve una sola vez; no puede usarse como acceso.
- **Notificaciones automáticas por trigger**, no por llamada entre servicios: llegan aunque el cambio lo haga el web, un servicio
  o un script, y respetan las preferencias de quien las recibe.
- **Un servicio no lee las tablas de otro.** Los de la Ola 1 son dueños de sus tablas; lo que no es suyo (nombres y precios base de
  productos, alertas de inventario, ofertas de proveedores) lo piden por HTTP con el JWT de quien hizo la petición (`comun/clientes.py`).
  La base de datos sigue siendo una sola; separarla por servicio queda declarado como deuda técnica.
- **Recepción de mercancía sin pérdidas ni duplicados.** Abastecimiento guarda la recepción antes de avisar a inventario y cada línea lleva
  una `operacion_uuid`. Si inventario no responde, la respuesta es 202 con la entrada pendiente, y repetir el POST sin líneas la aplica una
  sola vez.
- **La fecha de hoy es la de Monterrey.** PostgreSQL trabaja en UTC; `fn_hoy()` y `hoy()` evitan que una lista de precios que empieza «hoy»
  empiece mañana a partir de las 6 de la tarde.
- **Cada supuesto tiene dueño, origen y forma de calibrarse.** El valor vive en `configuracion` (RN40) y `supuesto_documentado` dice si es medido, supuesto o normativo,
  por qué ese valor y con qué dato real se corregiría. Hoy ninguno es «medido»: la operación real es chica. Los resultados lo dicen (`supuestos_usados`, `origen` de cada dato)
  y las conclusiones se prueban contra otros valores (`evidencias/ola2/escenarios.md`).
- **Los datos de demostración se dicen sintéticos.** La historia de demanda de los 60 días anteriores la genera la migración con una fórmula determinista y cada renglón
  trae `fuente = sintetica`; `POST /demanda/sincronizacion` la reemplaza por pedidos reales rango por rango.
- **La cobertura es el radio en línea recta; el rodeo de las calles solo estima tiempos.** Es la misma regla que `fn_cubre` en PostgreSQL. El factor (1.3) es un supuesto documentado.
- **La simulación no bloquea la petición.** `POST /simulacion/ejecuciones` junta la entrada, la guarda y responde 202; un hilo del servicio la toma de la cola (`FOR UPDATE SKIP
  LOCKED`). Misma entrada y misma semilla dan la misma huella (SHA-256 de los resultados), aunque los datos de origen cambien después. Una ejecución abandonada a medias
  regresa a la cola a los 5 minutos y falla tras 3 intentos.
- **Un servicio de apoyo caído se nota y no deja nada a medias.** Los cálculos que necesitan otro servicio responden 503 con el motivo; los que tienen todos los datos
  escritos siguen funcionando (`pruebas/demo_fallo_ola2.py`, `evidencias/ola2/fallo_servicios.md`).
- **MongoDB no bloquea la operación de pedidos**: si no responde, el cierre de entrega se aplica en PostgreSQL (con la foto ya subida) y solo
  se pierde el rastro analítico; los servicios cuyo almacén es MongoDB (documentos, recorrido, resumen) responden 503. Un cortacircuitos deja de
  intentar escribir logs y métricas durante 30 s tras una falla, para que el resto de los servicios no espere la selección de servidor en cada petición.
- **Despacho como saga.** Confirmar un plan de rutas con `despachar: true` deja las rutas y pide a entregas (dueño de la entrega) que cree y asigne
  las entregas en una sola transacción; si entregas rechaza o no responde, rutas regresa el plan a «propuesto» (compensación).

## Límites conocidos

- Las pruebas automáticas usan MongoDB simulado; los validadores `$jsonSchema` solo los aplica un MongoDB real.
- La contraseña de demostración es común a todas las cuentas y `SECRET_KEY` tiene un valor por omisión: cambiar ambos fuera
  de desarrollo.
- Catálogo en caché hasta 5 minutos: un cambio hecho en el web tarda ese tiempo en verse en las apps.
- Con las ventas reales de la demostración (pocos pedidos) casi todo el inventario aparece con exceso en el análisis de surtido, y el punto de equilibrio sale «no viable» para
  cualquier microhub: es lo que dicen los supuestos y los costos sembrados, no un error. Los valores cambian cuando haya volumen real o se corrijan los supuestos.
- `costo_km_reparto` y `costo_base_entrega` (rutas y cobertura) y los conceptos de costo equivalentes en el servicio de costos arrancan con el mismo valor pero son dos lugares;
  ver [`SUPUESTOS.md`](SUPUESTOS.md).
- Las ubicaciones candidatas de la semilla caen dentro de zonas que la red ya cubre, así que la evaluación de cobertura da cero hogares nuevos; la prueba con una coordenada fuera
  de la red sí los suma.

## Inventario y revisión documental

El código expone 199 operaciones de negocio por método y ruta (PUT y PATCH contados por separado); ver `INVENTARIO_ENDPOINTS.md`. Cada una tiene al menos un caso de evidencia (`evidencias/ola3`). Hay 26 contenedores de microservicios, 1 web, 3 almacenes y 1 de migraciones: 31 definidos, 30 continuos. Web espera migraciones y Redis; los servicios esperan migraciones, Redis y MongoDB.

Los XSD: `catalogos.xsd` atiende tres servicios y `entregas.xsd` también contiene estructuras de Seguimiento. `inventario.xsd`, `precios.xsd`, `proveedores.xsd`, `abastecimiento.xsd` y `notificaciones.xsd` se generan con `contratos/generar.py` a partir de `contratos/ola1.py` (que también escribe los ejemplos XML y JSON); `comun_ola1.xsd` guarda las referencias que comparten. Los ocho servicios de la Ola 2 se describen en `contratos/ola2.py` (tipos tomados de las respuestas reales en JSON y XML y afinados a mano: enumeraciones y campos que pueden ir vacíos; los cuerpos de entrada llevan las mismas restricciones que `validar.py`) y generan `demanda.xsd`, `cobertura.xsd`, `capacidad.xsd`, `rutas.xsd`, `costos.xsd`, `punto_equilibrio.xsd`, `simulacion.xsd`, `surtido.xsd`, `comun_ola2.xsd` y los complementos `pedidos_ola2.xsd`, `entregas_ola2.xsd` e `inventario_ola2.xsd`. Para agregar un servicio, ver `NUEVO_SERVICIO.md`.
