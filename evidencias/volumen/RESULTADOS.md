# Procesamiento de grandes volúmenes · resultados

Generado por `servicios/pruebas/medir_volumen.py --reporte` el 2026-11-26. Datos crudos en `medicion_*.json` e `insercion.json`.

## Volumen cargado por etapa

| Etapa | Pedidos | Líneas | Historial | Auditoría | Entregas | Puntos GPS | Logs técnicos | Base PG (MB) | GPS en MongoDB (MB datos + índices) |
|---|---|---|---|---|---|---|---|---|---|
| 010k | 10,148 | 28,720 | 10,683 | 56,713 | 9,590 | 141,945 | 20,358 | 52.4 | 27.8 + 6.5 |
| 050k | 50,148 | 140,276 | 50,683 | 208,271 | 47,590 | 711,945 | 101,043 | 162.3 | 139.2 + 38.6 |
| 100k | 100,148 | 279,286 | 100,683 | 397,283 | 95,073 | 1,424,190 | 201,728 | 298.5 | 278.4 + 90.2 |
| 100k_optimizado | 100,187 | 279,420 | 100,873 | 398,937 | 95,272 | 1,426,721 | 202,796 | 309.4 | 278.9 + 71.2 |

## Tiempo de inserción

| Etapa | Método | Registros | Segundos | Registros/s |
|---|---|---|---|---|
| 0 → 10,000 | PostgreSQL · INSERT fila por fila (pedido + líneas, con triggers) | 5,000 | 3.22 | 1,553 |
| 0 → 10,000 | PostgreSQL · COPY por lotes (pedido + líneas, con triggers) | 5,000 | 0.951 | 5,258 |
| 0 → 10,000 | PostgreSQL · COPY de entregas históricas (sin triggers) | 9,463 | 0.105 | 90,124 |
| 0 → 10,000 | MongoDB · insert_one (GPS) | 20,000 | 4.477 | 4,467 |
| 0 → 10,000 | MongoDB · insert_many lotes de 5 000 (GPS) | 121,945 | 1.642 | 74,266 |
| 0 → 10,000 | MongoDB · insert_many (logs técnicos) | 20,000 | 0.36 | 55,556 |
| 10,000 → 50,000 | PostgreSQL · COPY por lotes (pedido + líneas, con triggers) | 40,000 | 7.67 | 5,215 |
| 10,000 → 50,000 | PostgreSQL · COPY de entregas históricas (sin triggers) | 38,000 | 0.399 | 95,238 |
| 10,000 → 50,000 | MongoDB · insert_many lotes de 5 000 (GPS) | 570,000 | 9.636 | 59,153 |
| 10,000 → 50,000 | MongoDB · insert_many (logs técnicos) | 80,000 | 1.572 | 50,891 |
| 50,000 → 100,000 | PostgreSQL · COPY por lotes (pedido + líneas, con triggers) | 50,000 | 10.168 | 4,917 |
| 50,000 → 100,000 | PostgreSQL · COPY de entregas históricas (sin triggers) | 47,483 | 0.587 | 80,891 |
| 50,000 → 100,000 | MongoDB · insert_many lotes de 5 000 (GPS) | 712,245 | 13.338 | 53,400 |
| 50,000 → 100,000 | MongoDB · insert_many (logs técnicos) | 100,000 | 2.776 | 36,023 |

## Etapa 010k (10,148 pedidos)

### Consultas SQL (EXPLAIN ANALYZE)

| Consulta | Con índice (ms) | Plan | Sin índice (ms) | Plan sin índice | Índice |
|---|---|---|---|---|---|
| Lista de pedidos del administrador (servicio pedidos, fn_pedidos_visibles) | 10.99 | Seq Scan on zona → Function Scan | — | — | — |
| Lista de pedidos de un operador (su microhub) | 1.39 | Function Scan | — | — | — |
| Pedidos de un cliente, más recientes primero | 0.05 | Bitmap Heap Scan on pedido → Bitmap Index Scan (ix_pedido_cliente) | 6.56 | Seq Scan on pedido | ix_pedido_cliente |
| Pedidos de una zona en una semana | 0.07 | Index Only Scan (ix_pedido_zona_fecha) | 0.37 | Bitmap Heap Scan on pedido → Bitmap Index Scan (ix_web_pedido_fecha) | ix_pedido_zona_fecha |
| Historial de estados de un pedido | 0.02 | Index Scan (ix_hist_pedido) | 0.53 | Seq Scan on historial_estatus | ix_hist_pedido |
| Líneas de un pedido | 0.02 | Index Scan (ix_detalle_pedido) | 0.02 | Index Scan (uq_detalle_producto) | ix_detalle_pedido |
| Auditoría de una entidad (trazabilidad) | 0.02 | Index Scan (ix_aud_entidad) | 8.37 | Seq Scan on auditoria | ix_aud_entidad |
| Auditoría por módulo y acción, últimos 7 días | 0.04 | Index Scan (ix_aud_fecha) | 15.58 | Seq Scan on auditoria | ix_aud_modulo_accion, ix_aud_fecha |
| Resumen por día y zona, 30 días (servicio pedidos/resumen) | 14.44 | Seq Scan on pedido_detalle → Function Scan | — | — | — |
| Ventas por producto, 90 días (servicio pedidos/ventas) | 17.69 | Function Scan → Index Scan (ix_detalle_pedido) | — | — | — |

### MongoDB (explain executionStats)

| Consulta | Con índice (ms / docs examinados) | Sin índice (ms / docs examinados) | Índice |
|---|---|---|---|
| Recorrido GPS de una entrega | 0 / 15 | 38 / 141,945 | ix_entrega_tiempo |
| Puntos GPS a 300 m del MH-01 | 55 / 20,198 | 112 / 141,945 | ix_posicion (2dsphere) |
| Registros técnicos por nivel, 30 días ($group) | 10.1 | — | — |

### API (milisegundos, cliente en la misma máquina)

| Endpoint | HTTP | Primer llamado | Mediana | p95 | Máx |
|---|---|---|---|---|---|
| GET pedidos (entregados, página 1) | 200 | — | 25.5 | 31.6 | 89.7 |
| GET pedidos (página 200) | 200 | — | 26.4 | 28.5 | 29.5 |
| GET pedidos/resumen (30 días) | 200 | — | 40.0 | 45.3 | 48.3 |
| GET pedidos/resumen (170 días) | 200 | — | 62.2 | 71.7 | 101.0 |
| GET pedidos/ventas (90 días) | 200 | — | 52.7 | 58.4 | 63.0 |
| GET reportes/pedidos_por_dia (90 días) | 200 | — | 206.7 | 255.0 | 323.5 |
| GET reportes/ventas_por_producto (90 días) | 200 | — | 66.1 | 78.1 | 91.2 |
| GET auditoria (módulo pedidos) | 200 | — | 31.7 | 33.2 | 39.4 |
| GET auditoria/trazabilidad/pedido | 200 | — | 25.5 | 37.4 | 58.1 |
| GET seguimiento/{id}/recorrido | 200 | — | 8.1 | 10.3 | 11.2 |
| POST demanda/sincronizacion (170 días, por categoría) | 201 | — | 5212.1 | 5212.1 | 5212.1 |

### Caché de Redis

| Endpoint | Con caché: mediana / p95 | Sin caché: mediana / p95 | Mejora de la mediana |
|---|---|---|---|
| GET productos?q=a&por_pagina=50 | 3.0 / 4.0 ms | 18.5 / 23.3 ms | 6.2× |

Recursos (RSS en MB): postgres 207, mongod 271, redis-server 8, servicios (gunicorn) 4798 · CPU promedio durante la medición: 56.9 % de 2 núcleos · Redis: 1.56 MB.

## Etapa 050k (50,148 pedidos)

### Consultas SQL (EXPLAIN ANALYZE)

| Consulta | Con índice (ms) | Plan | Sin índice (ms) | Plan sin índice | Índice |
|---|---|---|---|---|---|
| Lista de pedidos del administrador (servicio pedidos, fn_pedidos_visibles) | 25.05 | Seq Scan on zona → Function Scan | — | — | — |
| Lista de pedidos de un operador (su microhub) | 4.77 | Function Scan | — | — | — |
| Pedidos de un cliente, más recientes primero | 0.06 | Index Scan (ix_pedido_cliente) | 2.96 | Seq Scan on pedido | ix_pedido_cliente |
| Pedidos de una zona en una semana | 0.44 | Bitmap Heap Scan on pedido → Bitmap Index Scan (ix_pedido_zona_fecha) | 1.02 | Bitmap Heap Scan on pedido → Bitmap Index Scan (ix_web_pedido_fecha) | ix_pedido_zona_fecha |
| Historial de estados de un pedido | 0.02 | Index Scan (ix_hist_pedido) | 2.52 | Seq Scan on historial_estatus | ix_hist_pedido |
| Líneas de un pedido | 0.01 | Index Scan (ix_detalle_pedido) | 0.01 | Index Scan (uq_detalle_producto) | ix_detalle_pedido |
| Auditoría de una entidad (trazabilidad) | 0.03 | Index Scan (ix_aud_entidad) | 23.11 | Seq Scan on auditoria | ix_aud_entidad |
| Auditoría por módulo y acción, últimos 7 días | 0.04 | Index Scan (ix_aud_fecha) | 35.74 | Seq Scan on auditoria | ix_aud_modulo_accion, ix_aud_fecha |
| Resumen por día y zona, 30 días (servicio pedidos/resumen) | 63.94 | Seq Scan on pedido_detalle → Function Scan | — | — | — |
| Ventas por producto, 90 días (servicio pedidos/ventas) | 92.56 | Function Scan → Index Scan (ix_detalle_pedido) | — | — | — |

### MongoDB (explain executionStats)

| Consulta | Con índice (ms / docs examinados) | Sin índice (ms / docs examinados) | Índice |
|---|---|---|---|
| Recorrido GPS de una entrega | 0 / 15 | 217 / 711,945 | ix_entrega_tiempo |
| Puntos GPS a 300 m del MH-01 | 264 / 102,511 | 521 / 711,945 | ix_posicion (2dsphere) |
| Registros técnicos por nivel, 30 días ($group) | 67.2 | — | — |

### API (milisegundos, cliente en la misma máquina)

| Endpoint | HTTP | Primer llamado | Mediana | p95 | Máx |
|---|---|---|---|---|---|
| GET pedidos (entregados, página 1) | 200 | — | 68.4 | 80.1 | 80.4 |
| GET pedidos (página 200) | 200 | — | 65.1 | 82.8 | 102.1 |
| GET pedidos/resumen (30 días) | 200 | — | 127.4 | 152.3 | 161.7 |
| GET pedidos/resumen (170 días) | 200 | — | 207.3 | 251.0 | 256.1 |
| GET pedidos/ventas (90 días) | 200 | — | 224.8 | 247.4 | 257.9 |
| GET reportes/pedidos_por_dia (90 días) | 200 | — | 672.7 | 743.8 | 747.1 |
| GET reportes/ventas_por_producto (90 días) | 200 | — | 214.8 | 253.3 | 266.4 |
| GET auditoria (módulo pedidos) | 200 | — | 78.6 | 95.9 | 103.8 |
| GET auditoria/trazabilidad/pedido | 200 | — | 27.7 | 29.8 | 31.3 |
| GET seguimiento/{id}/recorrido | 200 | — | 10.2 | 11.8 | 13.1 |
| POST demanda/sincronizacion (170 días, por categoría) | 201 | — | 19477.4 | 19477.4 | 19477.4 |

### Caché de Redis

| Endpoint | Con caché: mediana / p95 | Sin caché: mediana / p95 | Mejora de la mediana |
|---|---|---|---|
| GET productos?q=a&por_pagina=50 | 2.9 / 4.0 ms | 19.9 / 24.8 ms | 6.9× |

Recursos (RSS en MB): postgres 391, mongod 507, redis-server 8, servicios (gunicorn) 4800 · CPU promedio durante la medición: 55.2 % de 2 núcleos · Redis: 1.61 MB.

## Etapa 100k (100,148 pedidos)

### Consultas SQL (EXPLAIN ANALYZE)

| Consulta | Con índice (ms) | Plan | Sin índice (ms) | Plan sin índice | Índice |
|---|---|---|---|---|---|
| Lista de pedidos del administrador (servicio pedidos, fn_pedidos_visibles) | 57.34 | Seq Scan on zona → Function Scan | — | — | — |
| Lista de pedidos de un operador (su microhub) | 11.53 | Function Scan | — | — | — |
| Pedidos de un cliente, más recientes primero | 0.12 | Bitmap Heap Scan on pedido → Bitmap Index Scan (ix_pedido_cliente) | 6.06 | Seq Scan on pedido | ix_pedido_cliente |
| Pedidos de una zona en una semana | 0.21 | Index Only Scan (ix_pedido_zona_fecha) | 2.24 | Bitmap Heap Scan on pedido → Bitmap Index Scan (ix_web_pedido_fecha) | ix_pedido_zona_fecha |
| Historial de estados de un pedido | 0.02 | Index Scan (ix_hist_pedido) | 3.6 | Seq Scan on historial_estatus | ix_hist_pedido |
| Líneas de un pedido | 0.02 | Index Scan (ix_detalle_pedido) | 0.02 | Index Scan (uq_detalle_producto) | ix_detalle_pedido |
| Auditoría de una entidad (trazabilidad) | 0.03 | Index Scan (ix_aud_entidad) | 51.96 | Seq Scan on auditoria | ix_aud_entidad |
| Auditoría por módulo y acción, últimos 7 días | 0.05 | Index Scan (ix_aud_fecha) | 91.43 | Seq Scan on auditoria | ix_aud_modulo_accion, ix_aud_fecha |
| Resumen por día y zona, 30 días (servicio pedidos/resumen) | 116.51 | Function Scan → Index Scan (ix_detalle_pedido) | — | — | — |
| Ventas por producto, 90 días (servicio pedidos/ventas) | 148.79 | Function Scan → Index Scan (ix_detalle_pedido) | — | — | — |

### MongoDB (explain executionStats)

| Consulta | Con índice (ms / docs examinados) | Sin índice (ms / docs examinados) | Índice |
|---|---|---|---|
| Recorrido GPS de una entrega | 0 / 15 | 369 / 1,424,190 | ix_entrega_tiempo |
| Puntos GPS a 300 m del MH-01 | 566 / 205,738 | 1086 / 1,424,190 | ix_posicion (2dsphere) |
| Registros técnicos por nivel, 30 días ($group) | 105.1 | — | — |

### API (milisegundos, cliente en la misma máquina)

| Endpoint | HTTP | Primer llamado | Mediana | p95 | Máx |
|---|---|---|---|---|---|
| GET pedidos (entregados, página 1) | 200 | — | 128.5 | 146.6 | 151.0 |
| GET pedidos (página 200) | 200 | — | 109.5 | 124.7 | 151.9 |
| GET pedidos/resumen (30 días) | 200 | — | 196.6 | 219.1 | 224.2 |
| GET pedidos/resumen (170 días) | 200 | — | 395.0 | 425.6 | 526.7 |
| GET pedidos/ventas (90 días) | 200 | — | 398.2 | 417.7 | 424.0 |
| GET reportes/pedidos_por_dia (90 días) | 200 | — | 1103.1 | 1184.7 | 1222.8 |
| GET reportes/ventas_por_producto (90 días) | 200 | — | 390.8 | 425.0 | 532.1 |
| GET auditoria (módulo pedidos) | 200 | — | 61.9 | 77.2 | 80.3 |
| GET auditoria/trazabilidad/pedido | 200 | — | 30.6 | 38.3 | 45.3 |
| GET seguimiento/{id}/recorrido | 200 | — | 8.9 | 12.6 | 16.6 |
| POST demanda/sincronizacion (170 días, por categoría) | 201 | — | 37547.9 | 37547.9 | 37547.9 |

### Caché de Redis

| Endpoint | Con caché: mediana / p95 | Sin caché: mediana / p95 | Mejora de la mediana |
|---|---|---|---|
| GET productos?q=a&por_pagina=50 | 3.0 / 4.1 ms | 19.8 / 25.8 ms | 6.6× |

Recursos (RSS en MB): postgres 447, mongod 782, redis-server 8, servicios (gunicorn) 4801 · CPU promedio durante la medición: 54.8 % de 2 núcleos · Redis: 1.59 MB.

## Etapa 100k_optimizado (100,187 pedidos)

### Consultas SQL (EXPLAIN ANALYZE)

| Consulta | Con índice (ms) | Plan | Sin índice (ms) | Plan sin índice | Índice |
|---|---|---|---|---|---|
| Lista de pedidos del administrador (servicio pedidos, fn_pedidos_visibles) | 53.95 | Subquery Scan → Index Scan (usuario_pkey) → Seq Scan on rol → Seq Scan on pedido | — | — | — |
| Lista de pedidos del administrador como la arma ahora el servicio (tabla directa, ámbito total) | 0.15 | Index Scan (ix_web_pedido_fecha) → Index Only Scan (zona_pkey) | 27.43 | Seq Scan on pedido → Seq Scan on zona | ix_web_pedido_fecha |
| Buscar un pedido por id dentro del ámbito (fn_pedidos_visibles … WHERE id = ?) | 0.19 | Subquery Scan → Index Scan (usuario_pkey) → Seq Scan on rol → Index Only Scan (pedido_pkey) | — | — | — |
| Lista de pedidos de un operador (su microhub) | 16.5 | Subquery Scan → Index Scan (usuario_pkey) → Seq Scan on rol → Seq Scan on pedido | — | — | — |
| Pedidos de un cliente, más recientes primero | 0.13 | Bitmap Heap Scan on pedido → Bitmap Index Scan (ix_pedido_cliente) | 6.4 | Seq Scan on pedido | ix_pedido_cliente |
| Pedidos de una zona en una semana | 1.17 | Bitmap Heap Scan on pedido → Bitmap Index Scan (ix_pedido_zona_fecha) | 2.68 | Bitmap Heap Scan on pedido → Bitmap Index Scan (ix_web_pedido_fecha) | ix_pedido_zona_fecha |
| Historial de estados de un pedido | 0.02 | Index Scan (ix_hist_pedido) | 4.92 | Seq Scan on historial_estatus | ix_hist_pedido |
| Líneas de un pedido | 0.03 | Index Scan (ix_detalle_pedido_cubriente) | 0.02 | Index Scan (uq_detalle_producto) | ix_detalle_pedido, ix_detalle_pedido_cubriente |
| Auditoría de una entidad (trazabilidad) | 0.03 | Index Scan (ix_aud_entidad) | 74.44 | Seq Scan on auditoria | ix_aud_entidad |
| Auditoría por módulo y acción, últimos 7 días | 0.06 | Index Scan (ix_aud_fecha) | 82.57 | Seq Scan on auditoria | ix_aud_modulo_accion, ix_aud_fecha |
| Resumen por día y zona, 30 días (servicio pedidos/resumen) | 187.34 | Subquery Scan → Index Scan (usuario_pkey) → Seq Scan on rol → Bitmap Heap Scan on pedido | — | — | — |
| Resumen por día y zona, 30 días, con rango de creado_en (como ahora el servicio) | 118.56 | Index Scan (ix_detalle_pedido) → Bitmap Heap Scan on pedido → Bitmap Index Scan (ix_web_pedido_fecha) | — | — | — |
| Ventas por producto, 90 días (servicio pedidos/ventas) | 136.64 | Subquery Scan → Index Scan (usuario_pkey) → Seq Scan on rol → Bitmap Heap Scan on pedido | — | — | — |

### MongoDB (explain executionStats)

| Consulta | Con índice (ms / docs examinados) | Sin índice (ms / docs examinados) | Índice |
|---|---|---|---|
| Recorrido GPS de una entrega | 0 / 15 | 385 / 1,426,721 | ix_entrega_tiempo |
| Puntos GPS a 300 m del MH-01 | 600 / 205,381 | 1176 / 1,426,721 | ix_posicion (2dsphere) |
| Registros técnicos por nivel, 30 días ($group) | 123.0 | — | — |

### API (milisegundos, cliente en la misma máquina)

| Endpoint | HTTP | Primer llamado | Mediana | p95 | Máx |
|---|---|---|---|---|---|
| GET pedidos (entregados, página 1) | 200 | 55.5 | 28.3 | 41.9 | 52.1 |
| GET pedidos (página 200) | 200 | 34.5 | 29.8 | 39.4 | 40.7 |
| GET pedidos/resumen (30 días) | 200 | 126.9 | 97.4 | 127.4 | 143.0 |
| GET pedidos/resumen (170 días) | 200 | 219.5 | 215.9 | 248.2 | 262.4 |
| GET pedidos/ventas (90 días) | 200 | 162.9 | 219.8 | 242.1 | 289.0 |
| GET reportes/pedidos_por_dia (90 días) | 200 | 255.9 | 212.1 | 230.3 | 233.8 |
| GET reportes/ventas_por_producto (90 días) | 200 | 232.2 | 209.5 | 238.7 | 334.3 |
| GET auditoria (módulo pedidos) | 200 | 104.1 | 95.7 | 104.0 | 116.2 |
| GET auditoria/trazabilidad/pedido | 200 | 84.5 | 29.8 | 35.2 | 38.0 |
| GET seguimiento/{id}/recorrido | 200 | 13.6 | 9.6 | 11.3 | 13.1 |
| POST demanda/sincronizacion (170 días, por categoría) | 201 | — | 1144.1 | 1144.1 | 1144.1 |

### Caché de Redis

| Endpoint | Con caché: mediana / p95 | Sin caché: mediana / p95 | Mejora de la mediana |
|---|---|---|---|
| GET productos?q=a&por_pagina=50 | 3.5 / 5.4 ms | 20.8 / 26.2 ms | 5.9× |

Recursos (RSS en MB): postgres 429, mongod 781, redis-server 10, servicios (gunicorn) 4648 · CPU promedio durante la medición: 57.1 % de 2 núcleos · Redis: 1.75 MB.

## Escalabilidad (mediana de la API en ms por etapa)

| Endpoint | 010k | 050k | 100k | 100k_optimizado |
|---|---|---|---|---|
| GET pedidos (entregados, página 1) | 25.5 | 68.4 | 128.5 | 28.3 |
| GET pedidos (página 200) | 26.4 | 65.1 | 109.5 | 29.8 |
| GET pedidos/resumen (30 días) | 40.0 | 127.4 | 196.6 | 97.4 |
| GET pedidos/resumen (170 días) | 62.2 | 207.3 | 395.0 | 215.9 |
| GET pedidos/ventas (90 días) | 52.7 | 224.8 | 398.2 | 219.8 |
| GET reportes/pedidos_por_dia (90 días) | 206.7 | 672.7 | 1103.1 | 212.1 |
| GET reportes/ventas_por_producto (90 días) | 66.1 | 214.8 | 390.8 | 209.5 |
| GET auditoria (módulo pedidos) | 31.7 | 78.6 | 61.9 | 95.7 |
| GET auditoria/trazabilidad/pedido | 25.5 | 27.7 | 30.6 | 29.8 |
| GET seguimiento/{id}/recorrido | 8.1 | 10.2 | 8.9 | 9.6 |
| POST demanda/sincronizacion (170 días, por categoría) | 5212.1 | 19477.4 | 37547.9 | 1144.1 |

