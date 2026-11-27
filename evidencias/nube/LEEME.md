# Evidencias de la plataforma en Google Cloud

Corridas del 26 de noviembre de 2026 sobre la VM `microhubs-vm` con los 26 microservicios. La VM se apagó al terminar cada una. La **versión final
desplegada es `dba94ea`** (27 de noviembre); lo que se midió con una versión anterior lo dice.

## Versión final (`dba94ea`)

| Archivo | Qué demuestra |
|---|---|
| `salud_26_servicios.txt` | `/salud` de cada servicio por HTTPS a través de Nginx: versión, tiempo y las cuatro dependencias en `ok` (26 de 26 en HTTP 200) |
| `health_rutas.txt` | `/health/live`, `ready`, `database`, `redis`, `mongodb` y `storage` de los 26 servicios: 156 de 156 en HTTP 200 |
| `archivos_portal.txt` | La pantalla «Archivos» del portal sube al bucket y baja con URL firmada; PostgreSQL ya no guarda el archivo (4 de 4) |
| `procesos/` | Tres procesos por API y portal web, con el archivo comprobado en el bucket: 32 de 32 pasos |
| `flujos/` | Tres procesos de principio a fin por API: 40 de 40 pasos |
| `ola4/pruebas.md` | 436 casos de petición y respuesta, todos aprobados. Solo la tabla: las respuestas completas no se publican porque llevan tokens de esa instalación |
| `pruebas_bucket.txt` | 9 pruebas contra Cloud Storage: URL firmada, caducidad, manipulación, privacidad y bucket caído |
| `fallos.md` | 32 de 32: servicio detenido, Redis, MongoDB, PostgreSQL, almacén de archivos, tiempo de espera e integridad |
| `seguridad.md` | 23 de 23: sesiones, permisos, bloqueo, bitácora inmutable, entradas maliciosas, enlaces firmados, límite de consumo, secretos y puertos |
| `certificado.txt` | Certificado de Let's Encrypt activo desde el 27 de noviembre (las corridas de arriba se hicieron con el autofirmado) |

## Corridas anteriores

| Archivo | Versión | Qué demuestra |
|---|---|---|
| `carga/informe_carga.md` y `carga/ANALISIS.md` | `fd85013` | Locust hasta 200 usuarios: rendimiento, p95/p99, errores, saturación, recuperación, recursos y mejoras |
| `monitoreo_estado.json` | `fd85013` | Panel central: 26 servicios sanos, sin alertas abiertas y el verificador activo |
| `volumen/volumen.md` | `0cab2a9` | 1 000 000 de pedidos y 3 000 000 de líneas; 3 000 000 de documentos en MongoDB; con y sin índices y con y sin Redis |
| `contenedores.txt`, `puertos.txt` | `56f38c9` | Contenedores sanos con sus puertos solo en 127.0.0.1 y qué escucha hacia fuera |
| `monitoreo_disponibilidad.json`, `monitoreo_alertas.json` | `56f38c9` | Disponibilidad y percentiles por servicio; alertas abiertas y cerradas solas |
| `pruebas_en_la_nube.md` | `56f38c9` | 401 casos de petición y respuesta de la versión de la Ola 3 |
| `recursos_gcp.txt`, `cloud_logging.txt` | `56f38c9` | VM, IP, firewall, bucket y permisos; registros de los contenedores en Cloud Logging |

Acceso: el portal y las API se publican por HTTPS (443) con un certificado de Let's Encrypt; HTTP (80) redirige. Comprobado el 27 de noviembre: 26 de
26 servicios sanos con el certificado validado, también después de reiniciar la VM sin correr el instalador. La clave de las cuentas de demostración
en la nube es distinta de la del repositorio y solo está en el `.env` de la VM.
