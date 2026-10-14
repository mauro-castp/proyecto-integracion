# Capturas y figuras del Reporte Técnico · Segundo Parcial (anexo E2)

Una imagen por cada figura del reporte, con el mismo número. Las figuras 2 a 12 son los diagramas 10 a 17 de `bloque_d/diagramas/` (fuentes PlantUML en `bloque_d/fuentes/`).

| Figura | Archivo | Qué muestra |
|---|---|---|
| 1 | `figura_01_arquitectura_desplegada_en_el_segundo_parcial.png` | arquitectura desplegada en el Segundo Parcial |
| 2 | `figura_02_despliegue_del_segundo_parcial_13_contenedores_dos.png` | Despliegue vigente: 15 contenedores definidos, dos redes y dos volúmenes (diagrama 10). |
| 3 | `figura_03_componentes_y_comunicacion_clientes_web_microservicios_y.png` | Componentes y comunicación: clientes, web, microservicios y almacenes (diagrama 11). |
| 4 | `figura_04_secuencia_del_cierre_de_una_entrega_con.png` | Secuencia del cierre de una entrega con evidencia (1 de 2): sesión, consulta, evidencia y GPS (diagrama 12). |
| 5 | `figura_05_secuencia_del_cierre_de_una_entrega_con.png` | Secuencia del cierre de una entrega con evidencia (2 de 2): cierre idempotente y visibilidad en el web (diagrama 12). |
| 6 | `figura_06_autenticacion_comun_1_de_3_inicio_de.png` | Autenticación común (1 de 3): inicio de sesión y bloqueo por intentos (diagrama 13). |
| 7 | `figura_07_autenticacion_comun_2_de_3_peticion_protegida.png` | Autenticación común (2 de 3): petición protegida en cualquier servicio (diagrama 13). |
| 8 | `figura_08_autenticacion_comun_3_de_3_renovacion_con.png` | Autenticación común (3 de 3): renovación con rotación y cierre de sesión (diagrama 13). |
| 9 | `figura_09_modelo_de_datos_de_postgresql_1_de.png` | Modelo de datos de PostgreSQL (1 de 3): seguridad, catálogo y abasto (diagrama 14). |
| 10 | `figura_10_modelo_de_datos_de_postgresql_2_de.png` | Modelo de datos de PostgreSQL (2 de 3): pedidos y entregas; entrega agrega id_cliente_local, evidencia_ids y la ubicación del cierre (diagrama 15). |
| 11 | `figura_11_modelo_de_datos_de_postgresql_3_de.png` | Modelo de datos de PostgreSQL (3 de 3): planeación y avisos (diagrama 16). |
| 12 | `figura_12_datos_distribuidos_postgresql_mongodb_y_redis_y.png` | Datos distribuidos: PostgreSQL, MongoDB y Redis y sus relaciones (diagrama 17). |
| 13 | `figura_13_colecciones_de_mongodb_y_numero_de_documentos.png` | Colecciones de MongoDB y número de documentos en el despliegue Docker. |
| 14 | `figura_14_claves_reales_en_redis_sesiones_auth_sesion.png` | Claves reales en Redis: sesiones (auth:sesion), tokens de renovación guardados como hash (auth:refresh), caché de permisos y contador de límite de consumo (rate:entregas). |
| 15 | `figura_15_swagger_del_servicio_de_autenticacion_ejecutando_post.png` | Swagger del servicio de autenticación ejecutando POST /api/v1/auth/login contra el servicio desplegado: respuesta 200 con el token. |
| 16 | `figura_16_swagger_del_servicio_de_entregas_con_authorize.png` | Swagger del servicio de entregas con «Authorize»: GET /api/v1/entregas/mias con Authorization: Bearer, respuesta 200 paginada. |
| 17 | `figura_17_ejecucion_de_evidencias_py_dentro_del_contenedor.png` | Ejecución de evidencias.py dentro del contenedor de entregas: 93 de 93 casos pasan. |
| 18 | `figura_18_pantalla_microservicios_del_portal_web_salud_de.png` | Pantalla Microservicios del portal web: captura histórica de salud de los 8 servicios, agregaciones de MongoDB y una respuesta XML real, todo obtenido por HTTP. |
| 19 | `figura_19_ped_20261013_000155_armado_por_el_web.png` | PED-20261013-000155 armado por el web con los servicios de pedidos, entregas y documentos: historial (el cierre lo hizo repartidor1@codex.mx a través del servicio), recorrido GPS de MongoDB y evidencia. |
| 20 | `figura_20_reporte_de_pedidos_con_filtros_importe_y.png` | Reporte de pedidos con filtros, importe y gráficas Highcharts. |
| 21 | `figura_21_cobertura_y_mapa_microhubs_con_su_radio.png` | Cobertura y mapa: microhubs con su radio, candidatos, demanda por zona y demanda no atendida. |
| 22 | `figura_22_simulacion_de_operacion_con_supuestos_editables_ficha.png` | Simulación de operación con supuestos editables, ficha de viabilidad y capacidad. |
| 23 | `figura_23_docker_compose_f_docker_compose_integrado_yml.png` | docker compose -f docker-compose.integrado.yml ps -a: captura histórica de 12 contenedores en ejecución y migraciones. La configuración actual define 14 continuos y migraciones. |
| 24 | `figura_24_bitacora_del_web_el_login_inicio_de.png` | Bitácora del web: el login «Inicio de sesión por API (PowerShell)», la modificación de la entrega 129 y el cambio del pedido 1 a entregado, hechos por el repartidor a través de los microservicios. |
| 25 | `figura_25_el_mismo_flujo_que_hace_la_app.png` | El mismo flujo que hace la app del repartidor, ejecutado desde PowerShell contra los servicios: login, mis entregas, foto, tres puntos GPS, cierre (estado_pedido: entregado, duplicado: False) y recorrido calculado por MongoDB. |
| 26 | `figura_26_la_clienta_del_pedido_recibe_en_el.png` | La clienta del pedido recibe en el web el aviso que generó el trigger de PostgreSQL al cerrar la entrega. |

## Vigencia y capturas por renovar

Las figuras 1 a 5 fueron actualizadas con los diagramas vigentes. Las figuras 6 a 12 muestran contratos o modelos sin cambios en esta refactorización. Las capturas manuales 13 a 26 son históricas; no se editaron para aparentar una nueva ejecución. Los nombres de archivo se conservan para no romper referencias (incluido el nombre antiguo de la figura 2).

Renovar prioritariamente:
1. Figura 18: tablero con los diez servicios, Productos :5103, Zonas :5108, Microhubs :5109 y Seguimiento :5110.
2. Figura 23: `docker compose -f docker-compose.integrado.yml ps -a`, con 14 contenedores continuos y migraciones en Exited (0).
3. Figuras 19 y 25: pedido integrado y llamadas GPS bajo `/api/v1/seguimiento/{id}`.

La evidencia estructurada vigente está en `evidencias/`: corrida adjunta de 93 casos, 13-oct-2026 21:27 UTC.
