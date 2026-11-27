# Guion del video de demostración y de la presentación final

## A. Video (8–10 min). Se graba contra la VM con HTTPS

| # | Tiempo | Qué se ve | Qué se dice |
|---|---|---|---|
| 1 | 0:00–0:40 | Mapa de San Bernabé y los 4 microhubs | **El problema.** Los pedidos de abarrotes de barrio llegan tarde y caros. ¿Conviene una red de microalmacenes? ¿Con qué personal y con qué surtido? |
| 2 | 0:40–1:30 | Diagramas 18 (GCP) y 19 (26 servicios) | **Arquitectura.** Web, Android y escritorio; 26 servicios con una responsabilidad cada uno; PostgreSQL, MongoDB, Redis y bucket; Nginx como única puerta |
| 3 | 1:30–2:30 | Portal web: cliente compra → operador prepara → **Abastecimiento** (P2 completo con el comprobante) | Cada pantalla es cliente de los servicios: se ve la tabla de llamadas con HTTP, ms y traza |
| 4 | 2:30–3:30 | **App Android**: mis entregas → foto → GPS → cierre parcial | Cierre idempotente; la foto va al bucket; el cliente recibe el aviso |
| 5 | 3:30–4:15 | **App de escritorio** (XML): candidatos, simulación, punto de equilibrio | Todo XML validado contra los XSD en ambos lados |
| 6 | 4:15–4:45 | **Swagger** de rutas: «Authorize» y «Try it out» en `rutas/comparaciones` | Contratos JSON y XML, ejemplos oficiales |
| 7 | 4:45–5:45 | **Rutas** (P3): proponer → confirmar y despachar → la app del repartidor muestra las paradas; la tabla de métodos | **Algoritmo**: exacto contra 2-opt, 24–40 % menos que el orden de llegada |
| 8 | 5:45–6:30 | **Monitoreo**: `docker compose stop inventario` → alerta crítica → `start` → se cierra sola | Tolerancia a fallos y salud de los 26 servicios |
| 9 | 6:30–7:15 | **La nube**: consola de GCP (VM, firewall, bucket privado con los objetos `documentos/` y `reportes/`), Cloud Logging buscando una traza | Infraestructura y registros |
| 10 | 7:15–8:15 | `evidencias/nube/carga/carga.html` (gráficas de Locust) y `evidencias/nube/volumen/volumen.md` | **Carga y volumen**: en la nube, 100 usuarios sin errores con p95 de 1.3 s y saturación con 200; con un millón de pedidos, una consulta pasa de 106 ms a 0.2 ms con índice |
| 11 | 8:15–9:00 | `evidencias/nube/procesos/procesos_integrales.md` | **Integración**: 3 procesos de punta a punta en la nube, 32 de 32 pasos comprobados en las bases y en el bucket |

Consejos de grabación:

- Grabar a 1080p con el zoom del navegador al 125 %.
- Dejar la VM encendida y las sesiones abiertas antes de grabar.
- Tener el `.env` a mano para la clave de la nube, sin mostrarlo en pantalla.

## B. Presentación final (16 partes recomendadas)

| # | Diapositiva | Contenido | Fuente en el repositorio |
|---|---|---|---|
| 1 | Problema | Barrio, tiempo, costo y la pregunta de viabilidad | `bloque_a/Analisis_del_Problema.pdf` |
| 2 | Usuarios | Los 6 perfiles con lo que hace cada uno | `docs/MANUAL_USUARIO.md` |
| 3 | Solución | Red de microhubs y plataforma de operación y planeación | README |
| 4 | Arquitectura | Diagramas 18 y 19; la regla «un servicio, un dueño» | `bloque_d/diagramas/18_*`, `19_*` |
| 5 | Demo web | P2 en vivo (o grabado) | `/web/servicios/abastecimiento` |
| 6 | Demo móvil | Cierre de entrega con foto y GPS | app Android |
| 7 | Demo escritorio | Simulación y punto de equilibrio en XML | app de escritorio |
| 8 | Microservicios | 26 servicios en 4 olas; Swagger; 202 operaciones con evidencia | `servicios/README.md`, `INVENTARIO_ENDPOINTS.md` |
| 9 | Seguridad | JWT + Redis, revocación, roles y ámbito, XXE, archivos, límites, IP real | `docs/PLAN_DE_PRUEBAS.md` §5 |
| 10 | Datos | Políglota: qué va en cada base; 100 k pedidos y 1.4 M de puntos GPS | `bloque_d/diagramas/17_*`, `evidencias/volumen` |
| 11 | Algoritmo | Rutas: pseudocódigo, complejidad, tabla de calidad y tiempo | `docs/ALGORITMOS.md` |
| 12 | Infraestructura | GCP: VM, firewall, bucket, IAM sin llaves, Nginx, HTTPS | `deploy/gcp/LEEME.md` |
| 13 | Monitoreo | Panel, alertas, trazas | captura del panel |
| 14 | Pruebas | Matriz de pruebas con resultados | `docs/PLAN_DE_PRUEBAS.md` |
| 15 | Resultados | Locust (gráfica de escalones), volumen (antes y después), fallos (6 de 6), viabilidad (no viable con los supuestos actuales: 385 pedidos/día contra capacidad de 164) | `evidencias/*` |
| 16 | Conclusiones | Qué se logró, lo que falta, trabajo futuro | `docs/EXPEDIENTE_TECNICO.md` §30–31 |

Para la sesión de preguntas: [`GUIA_ESTUDIO_PREGUNTAS.md`](GUIA_ESTUDIO_PREGUNTAS.md). Para la demostración de fallos en vivo:
[`RUNBOOK_FALLOS.md`](RUNBOOK_FALLOS.md).
