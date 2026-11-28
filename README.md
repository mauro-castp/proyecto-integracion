# Plataforma de Microhubs y Comercio de Proximidad

**Codex Innovations · Equipo 04**
Integración de Aplicaciones Computacionales · Entrega final (Primer, Segundo y Tercer Parcial integrados)

Sistema para una red de microalmacenes de barrio («microhubs») que surten pedidos de abarrotes en cuatro colonias del sector San Bernabé,
Monterrey, Nuevo León. Opera el día a día (pedidos, inventario, reposición, rutas, entregas con evidencia) y responde con datos si conviene
abrir o mantener un microhub.

**27 microservicios** · portal web · app Android (JSON) · app de escritorio (XML/XSD) · PostgreSQL, MongoDB y Redis · Google Cloud Storage ·
desplegado en Google Compute Engine.

## Empieza aquí

| Necesito… | Documento |
|---|---|
| El expediente técnico completo (31 secciones) | [`docs/EXPEDIENTE_TECNICO.md`](docs/EXPEDIENTE_TECNICO.md) · Word: [`reporte_tecnico/Expediente_Tecnico_Final_Equipo04.docx`](reporte_tecnico/Expediente_Tecnico_Final_Equipo04.docx) |
| Instalarlo (local, GCP, Android, escritorio) | [`docs/MANUAL_INSTALACION.md`](docs/MANUAL_INSTALACION.md) |
| Usarlo según mi perfil | [`docs/MANUAL_USUARIO.md`](docs/MANUAL_USUARIO.md) |
| Mantenerlo o extenderlo | [`docs/MANUAL_TECNICO.md`](docs/MANUAL_TECNICO.md) |
| El algoritmo complejo (rutas y Monte Carlo) | [`docs/ALGORITMOS.md`](docs/ALGORITMOS.md) |
| El plan de pruebas y sus resultados | [`docs/PLAN_DE_PRUEBAS.md`](docs/PLAN_DE_PRUEBAS.md) |
| Las incidencias y cómo se resolvieron | [`docs/REGISTRO_INCIDENCIAS.md`](docs/REGISTRO_INCIDENCIAS.md) |
| La demostración de fallos en vivo | [`docs/RUNBOOK_FALLOS.md`](docs/RUNBOOK_FALLOS.md) |
| Descargar las apps (APK de Android y escritorio para Windows) | [Release `v1.0-entrega-final`](https://github.com/mauro-castp/proyecto-integracion/releases/tag/v1.0-entrega-final) · cómo instalarlas: [`entrega/INSTALADORES.md`](entrega/INSTALADORES.md) |
| La presentación final | [`presentacion/Microhubs · Presentación final.pptx`](presentacion/) |
| Preparar el video y la presentación | [`docs/GUION_VIDEO_Y_PRESENTACION.md`](docs/GUION_VIDEO_Y_PRESENTACION.md) |
| Prepararse para las preguntas individuales | [`docs/GUIA_ESTUDIO_PREGUNTAS.md`](docs/GUIA_ESTUDIO_PREGUNTAS.md) |
| Lo que falta antes de entregar | [`PENDIENTES_ENTREGA_FINAL.md`](PENDIENTES_ENTREGA_FINAL.md) |

## Estructura del repositorio

| Carpeta | Contenido |
|---|---|
| [`bloque_a/`](bloque_a/) | Análisis del problema, matriz de perfiles y permisos, propuesta y plan de trabajo |
| [`bloque_b/`](bloque_b/) | 54 requerimientos funcionales y 39 no funcionales, 45 reglas de negocio, historias, casos de uso, trazabilidad |
| [`bloque_c/`](bloque_c/) | Modelo de datos: `sql/01–13`, `mongo/01–03`, claves y scripts de Redis, semilla y **generador de alto volumen** |
| [`bloque_d/`](bloque_d/) | Arquitectura: diagramas 1 a 21 (18: despliegue real en GCP; 19: los 26 servicios; 20–21: procesos integrales) |
| [`sistema_web/`](sistema_web/) | Portal Flask; `integracion.py` y `procesos.py` son el web como cliente de los servicios |
| [`servicios/`](servicios/) | Los 27 microservicios (puertos 5101–5127), su base común, contratos generados y pruebas |
| [`app_movil/`](app_movil/) | App Android del repartidor y del cliente (Kotlin, JSON) |
| [`app_escritorio/`](app_escritorio/) | App de escritorio para análisis y operadores (C#, XML) y los XSD oficiales del contrato |
| [`deploy/gcp/`](deploy/gcp/LEEME.md) | Despliegue en Google Cloud: VM, Nginx, bucket con URL firmadas, registros |
| [`pruebas_carga/`](pruebas_carga/LEEME.md) | Pruebas de carga con Locust (6 perfiles, estrés y recuperación) |
| [`evidencias/`](evidencias/LEEME.md) | Corridas: Olas 1–3, nube, **volumen, carga, fallos, procesos integrales y algoritmos** |
| [`docs/`](docs/) | Expediente, manuales, algoritmos, pruebas, incidencias, runbook, guías, bitácora y reflexiones |
| [`presentacion/`](presentacion/LEEME.txt) | Presentación final (`Microhubs · Presentación final.pptx`) y la del Segundo Parcial |
| [`reporte_tecnico/`](reporte_tecnico/) | Expediente final en Word y los reportes de parciales anteriores |

## Arrancar la plataforma completa

```bash
docker compose -f docker-compose.integrado.yml up --build -d
```

| Qué | Dónde |
|---|---|
| Web | http://localhost:5000 |
| Monitoreo | `/web/servicios/monitoreo` |
| Procesos integrales | `/web/servicios/abastecimiento`, `/web/servicios/rutas`, `/web/servicios/reportes` |
| Servicios | Puertos 5101–5126, con Swagger en `/api/v1/docs` |

Cuentas y clave de demostración: [`docs/MANUAL_INSTALACION.md`](docs/MANUAL_INSTALACION.md). En la nube:
`https://34-51-89-253.sslip.io` (ver [`deploy/gcp/LEEME.md`](deploy/gcp/LEEME.md)).

## Resultados principales de la entrega final

| Qué | Resultado | Evidencia |
|---|---|---|
| Procesos integrales de punta a punta (P1 cierre de entrega, P2 reabastecimiento, P3 despacho con rutas y reporte archivado) | En GCP: 32 de 32 pasos por el portal, comprobados en PostgreSQL, MongoDB y el bucket, y 40 de 40 por API | [`evidencias/nube/procesos/`](evidencias/nube/procesos/procesos_integrales.md), [`flujos/`](evidencias/nube/flujos/flujos.md) |
| Datos de alto volumen | En GCP: 1 M de pedidos y 3 M de documentos, con y sin índices y Redis. En local: 4 consultas lentas corregidas (sincronización de demanda de 37.5 s a 1.1 s) | [`evidencias/nube/volumen/`](evidencias/nube/volumen/volumen.md), [`evidencias/volumen/`](evidencias/volumen/LEEME.md) |
| Pruebas de carga (Locust) | En GCP (4 vCPU): 100 usuarios sin errores y p95 de 1.3 s; se satura con 200 (51 peticiones/s, 0.37 % de 503). En local, 150 usuarios: p95 de 110 ms | [`evidencias/nube/carga/`](evidencias/nube/carga/ANALISIS.md), [`evidencias/carga/`](evidencias/carga/RESULTADOS.md) |
| Fallos y seguridad | En GCP: 32 de 32 comprobaciones de fallos y 23 de 23 de seguridad. En local: 6 de 6 casos de infraestructura | [`evidencias/nube/`](evidencias/nube/fallos.md), [`evidencias/fallos/`](evidencias/fallos/fallos_infraestructura.md) |
| Algoritmos | Rutas: 2-opt a 1–2.5 % del óptimo; 24–40 % menos que el orden de llegada | [`evidencias/algoritmos/`](evidencias/algoritmos/benchmark.md) |
| Petición y respuesta | 439 de 439 en local y 436 de 436 en GCP | [`evidencias/ola4/`](evidencias/ola4/pruebas.md), [`evidencias/nube/`](evidencias/nube/LEEME.md) |

## Equipo

Ruth Elizabeth Soriano Barrera · Vanessa Morante López · Mauro Castillo Peña · María José Cedillo Mata · Jorge Antonio Arreola Cantú

## Videos

- Segundo Parcial: [Presentación Equipo 4 Microhubs en YouTube](https://youtu.be/wEvJhCQN4rM).
- Entrega final (corregida después de la retroalimentación; ver `entrega/CORRECCIONES_RETROALIMENTACION.md`): [Demostración Proyecto Final Equipo 04 Microhubs en YouTube](https://youtu.be/zwWkkMCn0qc). Versión anterior: <https://youtu.be/Q1Rm-Kr09Vw>. Guion en [`docs/GUION_VIDEO_Y_PRESENTACION.md`](docs/GUION_VIDEO_Y_PRESENTACION.md).

## Historial de la documentación

- Segundo Parcial:
  - [`reporte_tecnico/Reporte_Tecnico_Segundo_Parcial_Equipo04.docx`](reporte_tecnico/) (v4.3);
  - `Arquitectura_Plataforma_Microhubs_v4.2_Segundo_Parcial.docx`;
  - [`CAMBIOS_DOCUMENTACION_SEGUNDO_PARCIAL.md`](CAMBIOS_DOCUMENTACION_SEGUNDO_PARCIAL.md).
- Tercer Parcial (Olas 1 a 3) y entrega final: [`CAMBIOS_TERCER_PARCIAL.md`](CAMBIOS_TERCER_PARCIAL.md).
