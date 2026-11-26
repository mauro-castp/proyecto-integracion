# Evidencias de la plataforma en Google Cloud

Corrida del 26 de noviembre de 2026 sobre la VM `microhubs-vm`, versión `56f38c9`, con los 26 microservicios desplegados. La VM se apagó al terminar.

| Archivo | Qué demuestra |
|---|---|
| `salud_26_servicios.txt` | `/salud` de cada servicio a través de Nginx: versión, PostgreSQL, Redis, MongoDB, bucket y tiempo de respuesta (26 de 26 en HTTP 200) |
| `contenedores.txt` | Los 30 contenedores sanos y sus puertos publicados solo en 127.0.0.1 |
| `puertos.txt` | Qué escucha hacia fuera en la VM |
| `monitoreo_estado.json` | Panel central: 26 servicios sanos, sin alertas abiertas y el verificador activo |
| `monitoreo_disponibilidad.json` | Disponibilidad y percentiles de respuesta por servicio |
| `monitoreo_alertas.json` | Alertas abiertas y cerradas solas |
| `pruebas_bucket.txt` | 9 pruebas contra Cloud Storage: URL firmada, caducidad, manipulación, privacidad y bucket caído |
| `pruebas_en_la_nube.md` | 401 casos de petición y respuesta contra los servicios en la nube, todos aprobados (los 2 de descarga local no aplican con el bucket). Solo la tabla: las respuestas completas no se publican porque llevan tokens de esa instalación |
| `recursos_gcp.txt` | VM, IP, firewall, bucket, permisos y cuentas de servicio (sin llaves) |
| `cloud_logging.txt` | Registros de los contenedores en Cloud Logging, ya en campos |

Acceso: el portal y las API se publican por HTTP en el puerto 80 de la VM (el certificado HTTPS es un paso opcional del instalador que todavía no
se ha ejecutado). La clave de las cuentas de demostración en la nube es distinta de la del repositorio y solo está en el `.env` de la VM.
