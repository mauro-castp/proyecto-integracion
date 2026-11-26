# Datos de alto volumen

Corrida del 2026-11-26 21:40 en `x86_64 · 4 CPU`. Esquema y base aparte, borrados al terminar.

## PostgreSQL: inserción

| Forma | Filas | Tiempo | Filas por segundo |
|---|---|---|---|
| Masiva (pedidos) | 1,000,000 | 4,929 ms | 202,876 |
| Masiva (líneas de pedido) | 3,000,000 | 8,706 ms | 344,597 |
| Una por una | 2,000 | 299 ms | 6,679 |

Tamaño en disco de las tablas: **535 MB**.

## PostgreSQL: consultas con y sin índices (EXPLAIN ANALYZE)

| Consulta | Sin índice | Con índice | Mejora | Plan con índice |
|---|---|---|---|---|
| Pedidos de un cliente | 105.89 ms | 0.22 ms | 481.3× | Limit → Index Scan (ix_v_cliente) |
| Pedidos abiertos de un microhub | 98.96 ms | 0.26 ms | 380.6× | Aggregate → Index Only Scan (ix_v_abiertos) |
| Venta por día de los últimos 30 días | 143.14 ms | 78.35 ms | 1.8× | Aggregate → Sort → Index Only Scan (ix_v_fecha) |
| Líneas de un pedido | 106.34 ms | 0.08 ms | 1329.2× | Index Only Scan (ix_v_detalle) |
| 10 productos más vendidos de la semana | 403.22 ms | 195.56 ms | 2.1× | Limit → Sort → Aggregate |

## Con y sin Redis

«Venta por día de los últimos 30 días»: calculada en PostgreSQL **51.16 ms**; leída de Redis **0.16 ms** (319.8×; mediana de 30 repeticiones).

## MongoDB

| Colección | Documentos | Tiempo de inserción | Documentos por segundo |
|---|---|---|---|
| puntos GPS | 2,000,000 | 24,281 ms | 82,368 |
| eventos de demanda | 1,000,000 | 11,875 ms | 84,207 |

| Consulta | Sin índice | Con índice | Mejora |
|---|---|---|---|
| Recorrido de una entrega | 769.74 ms | 1.64 ms | 469.4× |
| Puntos a 100 m de un microhub | 2753.32 ms | 108.09 ms | 25.5× |
| Eventos de una zona en la última hora | 432.34 ms | 1.85 ms | 233.7× |

## Consultas medidas

- **Pedidos de un cliente:** `SELECT id, estado, subtotal, creado_en FROM volumen.pedido WHERE cliente_id = 4321 ORDER BY creado_en DESC LIMIT 20`
- **Pedidos abiertos de un microhub:** `SELECT count(*) FROM volumen.pedido WHERE microhub_id = 2 AND estado IN ('asignado','en_preparacion','en_ruta') AND creado_en >= now() - interval '2 days'`
- **Venta por día de los últimos 30 días:** `SELECT creado_en::date, count(*), sum(subtotal) FROM volumen.pedido WHERE creado_en >= now() - interval '30 days' AND estado <> 'cancelado' GROUP BY 1 ORDER BY 1`
- **Líneas de un pedido:** `SELECT producto_id, cantidad, precio_unitario FROM volumen.pedido_detalle WHERE pedido_id = 123456`
- **10 productos más vendidos de la semana:** `SELECT d.producto_id, sum(d.cantidad) AS u FROM volumen.pedido p JOIN volumen.pedido_detalle d ON d.pedido_id = p.id WHERE p.creado_en >= now() - interval '7 days' AND p.estado <> 'cancelado' GROUP BY 1 ORDER BY u DESC LIMIT 10`
