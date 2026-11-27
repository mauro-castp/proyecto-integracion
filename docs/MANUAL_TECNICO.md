# Manual técnico · Plataforma de Microhubs

Codex Innovations · Equipo 04 · Entrega final. Es para quien mantenga o extienda el sistema. La instalación está en
[`MANUAL_INSTALACION.md`](MANUAL_INSTALACION.md).

## 1. Mapa del repositorio

| Carpeta | Qué hay |
|---|---|
| `bloque_a/`, `bloque_b/` | Problema, perfiles y permisos, requerimientos, reglas de negocio (RN), historias, casos de uso y trazabilidad |
| `bloque_c/` | Modelo de datos: `sql/01–13` (esquema, lógica en triggers y funciones, semilla, migraciones por ola), `mongo/01–03`, `redis/` (claves y scripts Lua), `scripts/` (semilla y **generar_volumen.py**) |
| `bloque_d/` | Diagramas 1–21 (fuentes PlantUML en `fuentes/`) y prototipos |
| `servicios/` | Los 26 microservicios (`<nombre>/app.py` + `Dockerfile`), la base común `comun/`, los contratos generados `contratos/` y las pruebas `pruebas/` |
| `sistema_web/` | Portal Flask; `integracion.py` y `procesos.py` son el web como cliente de los servicios |
| `app_movil/` | App Android (Kotlin, JSON) |
| `app_escritorio/` | App de escritorio (C# WinForms, XML) y los **XSD oficiales** del contrato (`contratos/`) |
| `deploy/gcp/` | Instalador de la VM, Nginx y compose de la nube (los genera `generar.py`) |
| `pruebas_carga/` | Locust: perfiles, muestreo de recursos y resumen |
| `evidencias/` | Corridas: `ola1–3`, `nube`, `volumen`, `carga`, `fallos`, `procesos`, `algoritmos` |
| `docs/` | Manuales, algoritmos, plan de pruebas, incidencias, runbook, guías |

## 2. Anatomía de un microservicio

Cada servicio es un `app.py` que crea su aplicación con `comun.base.crear_app(nombre, título, descripción, puerto, dependencias)`.
Esa fábrica añade lo mismo a todos:

| Pieza | Archivo | Qué hace |
|---|---|---|
| Autenticación | `comun/base.py` (`requiere`) | JWT HS256 con la `SECRET_KEY` común. En **cada** petición Redis confirma que la sesión sigue viva (`auth:sesion:{id}`) y que el token no fue revocado (`auth:jti:revocado:{jti}`). Si Redis no responde → 503 (cierre seguro) |
| Autorización | `comun/datos.py` | Permisos por rol de la tabla `rol_permiso` (caché `cache:permisos:{rol}`, 5 min). `limitar_microhub` impone RN22 |
| Formatos | `comun/formatos.py`, `esquemas.py` | `Accept` decide JSON o XML. Todo XML de entrada se valida contra los XSD; se rechazan DTD y entidades |
| Validación | `comun/validar.py` | `Campo(...)`: tipo, rango, longitud, patrón y opciones; todos los errores juntos en 422 |
| Errores | `comun/base_errores.py` | `{error: {codigo, mensaje, detalles[], traza_id}}`. PostgreSQL o Redis caídos → 503. MongoDB caído → 503 (entrega final). Bucket caído → 503 |
| Límites | `_limitar` | 240 peticiones por IP, servicio y minuto; 30 inicios de sesión; 429 con `Retry-After`. Con `DETRAS_DE_PROXY=1` la IP sale de `X-Forwarded-For` |
| Registro | `_registrar` | Cada petición va a `logs_tecnicos` y `metricas_servicio` (MongoDB) con su `correlacion_id` = traza. Hay un **cortacircuitos**: si MongoDB falla, no se reintenta durante 30 s |
| Salud | `/salud` (`/health`) | Proceso, PostgreSQL, Redis, MongoDB, bucket, versión y `tiempo_ms`. Si una dependencia falla: 503 y «degradado» |
| Swagger | `comun/documentacion.py` | `/api/v1/docs` y `/api/v1/openapi.json`, con los ejemplos oficiales del contrato |
| Llamadas entre servicios | `comun/clientes.py` | `llamar` y `exigir`: HTTP con el **mismo JWT** y la misma `X-Traza-Id`, con `MICROSERVICIOS_TIEMPO` de espera (4 s) |
| Archivos | `comun/almacen.py` | `local` (carpeta) o `gcs` (bucket). Ruta de objeto generada (nunca el nombre del usuario) y URL firmada V4 |

**Agregar un servicio:** ver [`servicios/NUEVO_SERVICIO.md`](../servicios/NUEVO_SERVICIO.md). En resumen:

1. Carpeta, `app.py` y `Dockerfile`.
2. Puerto en `comun/config.PUERTOS`.
3. Entrada en `docker-compose.integrado.yml`.
4. `python deploy/gcp/generar.py` (Nginx y compose de la nube).
5. Su XSD en `app_escritorio/contratos/`.
6. Pruebas, evidencias y el web (`integracion.PUERTOS`).

## 3. Reglas de diseño

1. **Una responsabilidad por servicio.** Lo que no es suyo lo pide por HTTP al dueño. Excepciones heredadas del Segundo Parcial:
   documentos y entregas consultan `pedido`/`entrega` para el ámbito. La base sigue siendo una sola; separarla por servicio es trabajo
   futuro.
2. **Las reglas de negocio críticas viven en PostgreSQL** (triggers y funciones de `02_logica.sql`):
   - transiciones de estado;
   - límite por línea;
   - auditoría inmutable;
   - avisos;
   - devolución de inventario.
   Así se cumplen igual desde el web, un servicio o un script.
3. **Idempotencia** donde hay reintentos:
   - cierre de entrega (`id_cliente_local`);
   - recepción de mercancía y movimientos (`operacion_uuid`);
   - sincronización (`dispositivo, operacion_uuid`).
4. **Nada a medias.**
   - El archivo se guarda antes que sus metadatos, y si MongoDB falla se borra.
   - Un cálculo que no tiene todos sus datos responde 503 y no guarda.
   - El despacho de rutas es una **saga**: si entregas rechaza, el plan vuelve a «propuesto».
5. **Los supuestos son datos.** Viven en `configuracion` y `supuesto_documentado`, y cada resultado dice cuáles usó
   ([`servicios/SUPUESTOS.md`](../servicios/SUPUESTOS.md)).

## 4. Datos

- **PostgreSQL** (`microhubs`): operación, catálogo, seguridad, planeación, abastecimiento, análisis y observabilidad.
  - Scripts 01–14 idempotentes desde la 06.
  - Zona horaria de la base: America/Monterrey (`fn_hoy()`).
  - `12_rendimiento.sql`: `fn_pedidos_visibles` en SQL que el planificador puede integrar, y los índices `ix_pedido_dia_local` e
    `ix_detalle_pedido_cubriente`.
  - `13_entrega_final.sql`: `ruta` y `almacen` en `reporte_exportacion`.
  - `14_pedidos_api.sql`: `pedido.operacion_uuid`, para que reenviar el mismo pedido por la API no lo duplique.
- **MongoDB** (`microhubs_eventos`):
  - `documentos`: solo metadatos; el archivo está en el bucket. Tipos de referencia: entrega, pedido, usuario, candidato y
    **orden_compra**.
  - `ubicaciones_entrega`: GPS, con índices 2dsphere y TTL de 180 días.
  - `logs_tecnicos` (capped de 512 MB), `metricas_servicio` (serie de tiempo), `sincronizaciones_moviles` y `ejecuciones_analiticas`.
- **Redis**:
  - base 0: sesiones y revocación;
  - base 1: caché de catálogo (`cache:catalogo:*`), de permisos, de **resúmenes paginados** (`cache:pedidos:*`, 60 s, solo de la
    página 2 en adelante) y contadores de límite (`rate:*`).
  - Sin persistencia: un reinicio cierra todas las sesiones.
- **Cloud Storage**:
  - `documentos/AAAA/MM/<id>.<ext>`: evidencias y comprobantes;
  - `reportes/AAAA/MM/<id>.<ext>`: exportaciones.
  - Es privado. Se descarga con URL firmada V4 de 300 s, que se firma con la identidad de la VM (sin llave).

## 5. Observabilidad

- `auditoria-monitoreo` consulta el `/salud` de los 26 cada 30 s y guarda el resultado en `monitoreo_verificacion`. Abre y cierra
  alertas solas: caído, degradado, dependencia caída, latencia y 5xx. Los umbrales están en `configuracion`. Un candado en Redis
  coordina para que la ronda la haga un solo proceso; sin Redis, todos verifican.
- Panel: `/web/servicios/monitoreo`. API: `/monitoreo/estado`, `/disponibilidad`, `/metricas`, `/alertas`.
- **Seguir un error:**
  1. Tomar la `traza_id` de la respuesta.
  2. Buscarla en `db.logs_tecnicos.find({correlacion_id: …})` o en Cloud Logging.
  3. Seguirla en los demás servicios: el que llama reenvía la traza.

## 6. Pruebas (detalle en [`PLAN_DE_PRUEBAS.md`](PLAN_DE_PRUEBAS.md))

```bash
servicios/pruebas/correr.sh test pruebas.test_unitarias pruebas.test_unitarias_ola2   # sin bases
servicios/pruebas/correr.sh test pruebas.test_ola1 pruebas.test_ola2 pruebas.test_ola3 # contra las bases reales
servicios/pruebas/correr.sh evidencias ola3                                            # 403 casos de petición y respuesta
python servicios/pruebas/procesos_integrales.py                                        # P1, P2 y P3 de punta a punta
python servicios/pruebas/demo_fallos_infra.py                                          # Redis, Mongo, Postgres, bucket, timeout
locust -f pruebas_carga/locustfile.py …                                                # carga (pruebas_carga/LEEME.md)
```

## 7. Operación y mantenimiento

| Tarea | Cómo |
|---|---|
| Rotar `SECRET_KEY` | Cambiarla en `.env` y reiniciar. Cierra todas las sesiones |
| Cambiar un límite o umbral | `UPDATE configuracion` (se lee en caliente) o las variables `LIMITE_*` |
| Ver la carga de un servicio | Panel de monitoreo (peticiones/h, 5xx/h, p95) o `docker stats` |
| Respaldar | `pg_dump -Fc` del volumen de PostgreSQL. `mongodump` de `microhubs_eventos`. En el bucket se puede activar el versionado de objetos |
| Quitar datos de prueba de volumen | `python bloque_c/scripts/generar_volumen.py --borrar` |
| Escalar un servicio con fila | Subir sus workers (`-w 4`) o duplicar el contenedor detrás de Nginx: los servicios no tienen estado propio |
