# Evidencias de la plataforma en Google Cloud

Corridas del 26 de noviembre de 2026 sobre la VM `microhubs-vm` con los 26 microservicios. La VM se apagó al terminar cada una. La **versión final
desplegada es `fd85013`**; lo que se midió con una versión anterior lo dice.

## Versión final (`fd85013`)

| Archivo | Qué demuestra |
|---|---|
| `salud_26_servicios.txt` | `/salud` de cada servicio por HTTPS a través de Nginx: versión, PostgreSQL, Redis, MongoDB, bucket y tiempo (26 de 26 en HTTP 200) |
| `monitoreo_estado.json` | Panel central: 26 servicios sanos, sin alertas abiertas y el verificador activo |
| `procesos/` | Tres procesos por API y portal web, con el archivo comprobado en el bucket: 32 de 32 pasos |
| `flujos/` | Tres procesos de principio a fin por API: 40 de 40 pasos |
| `ola4/pruebas.md` | 436 casos de petición y respuesta, todos aprobados. Solo la tabla: las respuestas completas no se publican porque llevan tokens de esa instalación |
| `pruebas_bucket.txt` | 9 pruebas contra Cloud Storage: URL firmada, caducidad, manipulación, privacidad y bucket caído |
| `carga/informe_carga.md` y `carga/ANALISIS.md` | Locust hasta 200 usuarios: rendimiento, p95/p99, errores, saturación, recuperación, recursos y mejoras |
| `fallos.md` | 32 de 32: servicio detenido, Redis, MongoDB, PostgreSQL, almacén de archivos, tiempo de espera e integridad |
| `seguridad.md` | 23 de 23: sesiones, permisos, bloqueo, bitácora inmutable, entradas maliciosas, enlaces firmados, límite de consumo, secretos y puertos |
| `certificado.txt` | HTTPS con certificado propio (autofirmado): el navegador avisa que no lo conoce |

## Corridas anteriores

| Archivo | Versión | Qué demuestra |
|---|---|---|
| `volumen/volumen.md` | `0cab2a9` | 1 000 000 de pedidos y 3 000 000 de líneas; 3 000 000 de documentos en MongoDB; con y sin índices y con y sin Redis |
| `contenedores.txt`, `puertos.txt` | `56f38c9` | Contenedores sanos con sus puertos solo en 127.0.0.1 y qué escucha hacia fuera |
| `monitoreo_disponibilidad.json`, `monitoreo_alertas.json` | `56f38c9` | Disponibilidad y percentiles por servicio; alertas abiertas y cerradas solas |
| `pruebas_en_la_nube.md` | `56f38c9` | 401 casos de petición y respuesta de la versión de la Ola 3 |
| `recursos_gcp.txt`, `cloud_logging.txt` | `56f38c9` | VM, IP, firewall, bucket y permisos; registros de los contenedores en Cloud Logging |

Acceso: el portal y las API se publican por HTTP (80) y por HTTPS (443) con un certificado autofirmado; un certificado reconocido (Let's Encrypt) es un
paso opcional del instalador. La clave de las cuentas de demostración en la nube es distinta de la del repositorio y solo está en el `.env` de la VM.
