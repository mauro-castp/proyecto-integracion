# Evidencias de la plataforma en Google Cloud

Dos corridas del 26 de noviembre de 2026 sobre la VM `microhubs-vm` con los 26 microservicios: la primera (versión `56f38c9`) y la completa (versión `0cab2a9`,
con volumen, carga, fallos y seguridad). La VM se apagó al terminar cada una.

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
| `flujos/` | Tres procesos de principio a fin en la nube: 40 de 40 pasos |
| `ola4/pruebas.md` | 428 casos de petición y respuesta contra la versión con altas y cambios, todos aprobados |
| `volumen/volumen.md` | 1 000 000 de pedidos y 3 000 000 de líneas; 3 000 000 de documentos en MongoDB; con y sin índices y con y sin Redis |
| `carga/informe_carga.md` y `carga/ANALISIS.md` | Locust hasta 200 usuarios: rendimiento, p95/p99, errores, saturación, recuperación, recursos y mejoras |
| `fallos.md` | 32 de 32: servicio detenido, Redis, MongoDB, PostgreSQL, almacén de archivos, tiempo de espera e integridad |
| `seguridad.md` | 23 de 23: sesiones, permisos, bloqueo, bitácora inmutable, entradas maliciosas, enlaces firmados, límite de consumo, secretos y puertos |
| `certificado.txt` | HTTPS con certificado propio (autofirmado): el navegador avisa que no lo conoce |
| `recursos_gcp.txt` | VM, IP, firewall, bucket, permisos y cuentas de servicio (sin llaves) |
| `cloud_logging.txt` | Registros de los contenedores en Cloud Logging, ya en campos |

Acceso: el portal y las API se publican por HTTP (80) y por HTTPS (443) con un certificado autofirmado; un certificado reconocido (Let's Encrypt) es un
paso opcional del instalador. La clave de las cuentas de demostración en la nube es distinta de la del repositorio y solo está en el `.env` de la VM.
