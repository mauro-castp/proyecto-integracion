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
| 18 | `figura_18_pantalla_microservicios_del_portal_web_salud_de.png` | Pantalla Microservicios del portal web: salud de los diez servicios, agregaciones de MongoDB y una respuesta XML real del servicio de zonas, todo obtenido por HTTP. |
| 19 | `figura_19_ped_20261014_000166_armado_por_el_web.png` | PED-20261014-000166 armado por el web con los servicios de pedidos, entregas, seguimiento y documentos: historial (el cierre lo hizo repartidor1@codex.mx a través del servicio), recorrido GPS de MongoDB y evidencia. Se omiten la tabla de líneas y el formulario de adjuntar. |
| 20 | `figura_20_reporte_de_pedidos_con_filtros_importe_y.png` | Reporte de pedidos con filtros, importe y gráficas Highcharts. |
| 21 | `figura_21_cobertura_y_mapa_microhubs_con_su_radio.png` | Cobertura y mapa: microhubs con su radio, candidatos, demanda por zona y demanda no atendida. |
| 22 | `figura_22_simulacion_de_operacion_con_supuestos_editables_ficha.png` | Simulación de operación con supuestos editables, ficha de viabilidad y capacidad. |
| 23 | `figura_23_docker_compose_f_docker_compose_integrado_yml.png` | docker compose -f docker-compose.integrado.yml ps -a: los 15 contenedores definidos; 14 en ejecución y sanos y migraciones terminada con código 0 (el web se publica en el puerto 5051 de esta máquina porque el 5000 estaba ocupado). |
| 24 | `figura_24_bitacora_del_web_el_login_inicio_de.png` | Bitácora del web: el login «Inicio de sesión por API (PowerShell)», la modificación de la entrega 142 y el cambio del pedido 166 a entregado, hechos por el repartidor a través de los microservicios. |
| 25 | `figura_25_el_mismo_flujo_que_hace_la_app.png` | El mismo flujo que hace la app del repartidor, ejecutado desde PowerShell contra los servicios (el GPS va al servicio de seguimiento): login, mis entregas, foto, tres puntos GPS, cierre (estado_pedido: entregado, duplicado: False) y recorrido calculado por MongoDB. |
| 26 | `figura_26_la_clienta_del_pedido_recibe_en_el.png` | La clienta del pedido recibe en el web el aviso que generó el trigger de PostgreSQL al cerrar la entrega. |

## Cómo se tomaron

Las figuras 1 a 12 son diagramas y modelos. Las figuras 13 a 26 se tomaron de nuevo el 13 de octubre de 2026 (por la noche, hora de Monterrey) con el sistema de diez servicios levantado desde `docker-compose.integrado.yml`.

- **Pantallas de Swagger y del portal** (15, 16, 18, 19, 20, 21, 22, 24 y 26): capturas reales con Chrome, con la sesión de cada perfil. En la 15 la clave de demostración aparece como `********`; la petición se hizo con la clave real. En la 19 se ocultaron la tabla de líneas y el formulario de adjuntar, y en la 20 y la 24 solo se ven las primeras filas.
- **Salidas de terminal** (13, 14, 17, 23 y 25): son el texto real que devolvió cada comando, dibujado en una consola oscura; no son capturas de una ventana. El texto original está en `salidas_terminal/`. En la 17 la imagen omite las líneas intermedias y el archivo tiene la salida completa (107 líneas). En la 25 la clave sale de una variable de entorno y no se ve.

Los nombres de archivo no cambiaron, salvo la figura 19, porque llevaba el folio del pedido anterior.

Los casos de petición y respuesta están en `evidencias/`: 93 casos, 13-oct-2026 21:27 UTC.
