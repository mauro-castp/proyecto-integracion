# Bitácora de participación · Equipo 04

> Responsables según lo que cada integrante describe en su reflexión (`docs/reflexiones/`) y el historial de Git (27 de noviembre de 2026).
> Todos participamos en el proyecto. Las confirmaciones **no miden** el trabajo real: quien sube o une archivos figura como autor, y el
> análisis, las pruebas con personas, la revisión o la presentación pueden no dejar rastro. Parte del código de las apps lo escribieron María José y
> Vanessa y lo subió Mauro, y María José trabajó con Mauro en las Olas 1 a 3 desde la computadora de él, por lo que ese trabajo figura a
> nombre de Mauro. Las horas no se registraron. La cuenta
> `SrTequila` es la de Jorge.

Integrantes: Ruth Elizabeth Soriano Barrera · Vanessa Morante López · Mauro Castillo Peña · María José Cedillo Mata · Jorge Antonio Arreola Cantú

## Responsables por componente

| Componente | Responsable principal | Apoyo | Evidencia (archivos, confirmaciones) |
|---|---|---|---|
| Análisis, requerimientos y reglas (bloques A y B) | María José (análisis del problema, perfiles y permisos, requerimientos, historias de usuario, casos de uso, reglas y trazabilidad) | Ruth | `bloque_a, bloque_b` · confirmaciones: María José 12, Ruth 3 |
| Modelo de datos (bloque C: SQL, MongoDB, Redis) | Vanessa (modelo entidad-relación, normalización y modelo físico en PostgreSQL) | Ruth (scripts SQL y migraciones), Mauro (claves de Redis) | `bloque_c` · confirmaciones: Ruth 14, Mauro 2 |
| Arquitectura y diagramas (bloque D) | Ruth | Vanessa (documento de arquitectura), Mauro (diagramas del Segundo Parcial) | `bloque_d` · confirmaciones: Ruth 5, Mauro 1 |
| Portal web | Ruth | Vanessa (altas y cambios de productos y catálogos, módulo de planeación), Mauro (integración con los microservicios) | `sistema_web` · confirmaciones: Ruth 17, Mauro 2, Vanessa 2 |
| Microservicios: Segundo Parcial (10) | Mauro (contrato v1, compose integrado y pruebas) | Ruth | `servicios/…` · confirmaciones: Ruth 9, Mauro 3 |
| Microservicios: Ola 1 | Ruth | Mauro y María José (trabajando juntos en la computadora de Mauro) | `servicios/…` · confirmaciones: Ruth 3, Mauro 2 |
| Microservicios: Ola 2 (algoritmos: rutas, simulación, surtido) | Ruth | Mauro y María José (colas M/M/1 y M/M/c en capacidad, trabajando juntos en la computadora de Mauro) | `servicios/…` · confirmaciones: Ruth 3, Mauro 1 |
| Microservicios: Ola 3 (reportes, sincronización, monitoreo) | Ruth | Mauro y María José (trabajando juntos en la computadora de Mauro) | `servicios/…` · confirmaciones: Ruth 7, Mauro 1 |
| App Android | Ruth (base y flujo del repartidor) | Mauro (perfil cliente, pruebas en el emulador), María José y Vanessa (archivos para el emulador y corrección de errores, entregados a Mauro) | `app_movil` · confirmaciones: Ruth 16, Mauro 4 |
| App de escritorio | Ruth (base y módulos de análisis) | Mauro (módulos de operación, manifiesto, permisos, pruebas en Windows), María José y Vanessa (archivos y corrección de errores, entregados a Mauro) | `app_escritorio` · confirmaciones: Ruth 9, Mauro 3 |
| Despliegue en GCP | Ruth | Mauro (pruebas de las apps contra la nube) | `deploy` · confirmaciones: Ruth 8 |
| Pruebas de volumen, carga (Locust) y fallos | Ruth | Mauro (pruebas de las apps) | `rendimiento, pruebas_carga, evidencias` · confirmaciones: Ruth 19 |
| Prueba de usabilidad con personas | Mauro | — | `entrega/FORMATO_USABILIDAD.md` |
| Instaladores y Release v1.0 | Mauro | — | `entrega/INSTALADORES.md`, Release `v1.0-entrega-final` |
| Reportes técnicos y expediente | Ruth | Mauro (correcciones del Primer Parcial y reporte 4.2), Vanessa (reporte del Segundo Parcial), María José (reporte del Primer Parcial) | `reporte_tecnico, docs` |
| Presentaciones y videos | María José (presentación final; edición y elaboración del video final) | Vanessa (presentación final; edición y elaboración del video final), Mauro (presentación del Segundo Parcial, grabación de la demostración final), Jorge (video del Segundo Parcial), Ruth (presentación del Primer Parcial) | `presentacion, entrega` · confirmaciones: Ruth 24, Mauro 13, María José 4, Vanessa 2, Jorge 1 |
| Reflexión individual | Cada integrante | — | `docs/reflexiones/` |

## Registro de sesiones de trabajo

| Fecha | Integrante(s) | Horas | Qué se hizo (asuntos de las confirmaciones) | Resultado |
|---|---|---|---|---|
| 2026-08-28 | Mauro | — | Initial commit | 1 confirmación |
| 2026-09-01 | María José | — | Add files via upload; Create bloque_a; Delete bloque_a; y 4 más | 14 confirmaciones |
| 2026-09-01 | Ruth | — | Primer Parcial: modelo de datos, arquitectura y sistema web mínimo funcional | 1 confirmación |
| 2026-09-03 | Mauro | — | Agregar imagenes de productos al catalogo | 1 confirmación |
| 2026-09-04 | Ruth | — | Agregar presentacion del Primer Parcial (pptx, capturas y generador); Agregar propuesta de negocio (incluye plan de trabajo del semestre); Corregir README de sistema_web y agregar README a cada bloque; y 3 más | 6 confirmaciones |
| 2026-09-17 | Vanessa | — | Add files via upload; Add database files to .gitignore | 2 confirmaciones |
| 2026-09-29 | María José | — | Delete reporte_tecnico/Reporte_Tecnico_Equipo04.docx | 1 confirmación |
| 2026-09-29 | Mauro | — | Add files via upload; Delete reporte_tecnico/Reporte_Tecnico_Equipo04_DIAGRAMAS_ESTILO_ORIGINAL (1).docx; Reporte Tecnico de Correciones Actualizado | 3 confirmaciones |
| 2026-09-29 | Ruth | — | Agregar módulo de Planeación y viabilidad de microhubs; Actualizar Reporte Técnico: evidencia Git, participación y correcciones de forma; Eliminar generar_reporte.js: el Reporte Técnico se mantiene directamente en el .docx | 3 confirmaciones |
| 2026-09-29 | Vanessa | — | Add files via upload | 3 confirmaciones |
| 2026-10-12 | Mauro | — | Microservicios del contrato v1, compose integrado y pruebas | 1 confirmación |
| 2026-10-12 | Ruth | — | Ruth Soriano: aplicaciones movil y de escritorio; Implementar web ampliado del segundo parcial; Ruth Soriano: corregir compilacion y verificar apps; y 1 más | 4 confirmaciones |
| 2026-10-13 | Mauro | — | Integración web con microservicios, evidencias reales y Dockerfile por servicio; Documentación del Segundo Parcial: reporte 4.2, diez microservicios, diagramas y presentación; Reporte técnico: pies de figura sin la leyenda de capturas históricas | 3 confirmaciones |
| 2026-10-13 | Ruth | — | Ruth Soriano: rediseño de la interfaz Android y perfil editable; Ruth Soriano: diagramas del Segundo Parcial y anexos E1 y E2 del reporte técnico; Ruth Soriano: reporte técnico del Segundo Parcial (versión 4.1); y 7 más | 10 confirmaciones |
| 2026-10-13 | Vanessa | — | Actualización documento del segundo parcial. | 1 confirmación |
| 2026-10-14 | Jorge | — | Add YouTube video link for 2nd partial; Update YouTube video link | 2 confirmaciones |
| 2026-10-19 | Ruth | — | Ola 1: inventario, precios, proveedores, abastecimiento y notificaciones; Ola 1: contratos XML y JSON de los servicios nuevos; Ola 1: pruebas, evidencias de 204 casos y demostración de fallo de inventario; y 1 más | 4 confirmaciones |
| 2026-11-25 | Ruth | — | Ola 2: base comun, supuestos documentados y migracion SQL; Ola 2: ocho servicios de analisis y planeacion (5115-5122); Ola 2: pedidos, entregas, inventario y planeacion alimentan al analisis; y 6 más | 9 confirmaciones |
| 2026-11-26 | Ruth | — | Ola 3 (3/3): servicio sincronizacion (5125) y arreglo de la bitácora de documentos; Cierre de la entrega en el repositorio: evidencias de la Ola 3, documentación, despliegue y fecha del turno; Instalador: Nginx se recarga aunque estuviera detenido; y 12 más | 15 confirmaciones |
| 2026-11-27 | Jorge | — | Add files via upload | 1 confirmación |
| 2026-11-27 | María José | — | Create Video Demostración; Update Video Demostración; Add files via upload | 3 confirmaciones |
| 2026-11-27 | Mauro | — | Entrega: instaladores con un comando, Release sobre main y guion al día con HTTPS; Apps: arreglos encontrados al probar en Windows y contra la nube; Escritorio para operadores y colas M/M/1 y M/M/c en capacidad; y 6 más | 9 confirmaciones |
| 2026-11-27 | Ruth | — | Apps: conectarse a la nube enrutando por nombre de servicio; Compose: PostgreSQL, Redis y MongoDB vuelven a encender solos; Documentos: HTTPS de Let's Encrypt activo, apps contra la nube y encendido de la VM; y 8 más | 11 confirmaciones |
| 2026-11-27 | Vanessa | — | Add link to final project video; Reflexion individual vane | 2 confirmaciones |
