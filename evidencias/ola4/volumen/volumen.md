# Datos de alto volumen

Corrida del 2026-11-26 21:25 en `x86_64 · 12 CPU`. Esquema y base aparte, borrados al terminar.

## PostgreSQL: inserción

| Forma | Filas | Tiempo | Filas por segundo |
|---|---|---|---|
| Masiva (pedidos) | 200,000 | 1,102 ms | 181,538 |
| Masiva (líneas de pedido) | 600,000 | 2,554 ms | 234,917 |
| Una por una | 2,000 | 746 ms | 2,680 |

Tamaño en disco de las tablas: **107 MB**.

## PostgreSQL: consultas con y sin índices (EXPLAIN ANALYZE)

| Consulta | Sin índice | Con índice | Mejora | Plan con índice |
|---|---|---|---|---|
| Pedidos de un cliente | 21.94 ms | 0.38 ms | 57.7× | Limit → Sort → Bitmap Heap Scan |
| Pedidos abiertos de un microhub | 21.87 ms | 0.21 ms | 104.1× | Aggregate → Index Only Scan (ix_v_abiertos) |
| Venta por día de los últimos 30 días | 55.63 ms | 83.88 ms | 0.7× | Aggregate → Sort → Index Only Scan (ix_v_fecha) |
| Líneas de un pedido | 30.34 ms | 0.59 ms | 51.4× | Index Only Scan (ix_v_detalle) |
| 10 productos más vendidos de la semana | 95.81 ms | 141.66 ms | 0.7× | Limit → Sort → Aggregate |

## Con y sin Redis

«Venta por día de los últimos 30 días»: calculada en PostgreSQL **14.9 ms**; leída de Redis **0.3 ms** (49.7×; mediana de 30 repeticiones).

## MongoDB

| Colección | Documentos | Tiempo de inserción | Documentos por segundo |
|---|---|---|---|
| puntos GPS | 400,000 | 7,077 ms | 56,519 |
| eventos de demanda | 200,000 | 3,039 ms | 65,808 |

| Consulta | Sin índice | Con índice | Mejora |
|---|---|---|---|
| Recorrido de una entrega | 244.56 ms | 1.59 ms | 153.8× |
| Puntos a 100 m de un microhub | 611.96 ms | 39.73 ms | 15.4× |
| Eventos de una zona en la última hora | 186.12 ms | 4.44 ms | 41.9× |

## Consultas medidas

- **Pedidos de un cliente:** `SELECT id, estado, subtotal, creado_en FROM volumen.pedido WHERE cliente_id = 4321 ORDER BY creado_en DESC LIMIT 20`
- **Pedidos abiertos de un microhub:** `SELECT count(*) FROM volumen.pedido WHERE microhub_id = 2 AND estado IN ('asignado','en_preparacion','en_ruta') AND creado_en >= now() - interval '2 days'`
- **Venta por día de los últimos 30 días:** `SELECT creado_en::date, count(*), sum(subtotal) FROM volumen.pedido WHERE creado_en >= now() - interval '30 days' AND estado <> 'cancelado' GROUP BY 1 ORDER BY 1`
- **Líneas de un pedido:** `SELECT producto_id, cantidad, precio_unitario FROM volumen.pedido_detalle WHERE pedido_id = 123456`
- **10 productos más vendidos de la semana:** `SELECT d.producto_id, sum(d.cantidad) AS u FROM volumen.pedido p JOIN volumen.pedido_detalle d ON d.pedido_id = p.id WHERE p.creado_en >= now() - interval '7 days' AND p.estado <> 'cancelado' GROUP BY 1 ORDER BY u DESC LIMIT 10`
