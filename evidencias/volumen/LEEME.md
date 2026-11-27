# Procesamiento de grandes volúmenes

Corrida del 26 de noviembre de 2026. Las tablas completas, etapa por etapa, están en [`RESULTADOS.md`](RESULTADOS.md). Los datos
crudos están en `insercion.json` y `medicion_*.json`.

## Qué se cargó

| Dato | Cantidad final | Dónde |
|---|---|---|
| Clientes sintéticos (usuario + cliente + domicilio) | 5 000 | PostgreSQL |
| Pedidos históricos de 170 días | 100 000 | PostgreSQL |
| Líneas de pedido | 279 286 | PostgreSQL |
| Historial de estados (lo escribe el trigger) | 100 683 | PostgreSQL |
| Auditoría (la escriben los triggers) | 397 283 | PostgreSQL |
| Entregas cerradas | 95 073 | PostgreSQL |
| **Lecturas GPS** | **1 424 190** | MongoDB `ubicaciones_entrega` |
| Registros técnicos | 201 728 | MongoDB `logs_tecnicos` |

En total son más de 1.4 millones de lecturas GPS y casi 900 mil eventos en PostgreSQL. La base de PostgreSQL llega a 298 MB y el
GPS ocupa 278 MB más 90 MB de índices.

El generador es [`bloque_c/scripts/generar_volumen.py`](../../bloque_c/scripts/generar_volumen.py). Es incremental, así que se corrió
por etapas (10 k → 50 k → 100 k pedidos) y se midió entre una y otra. Todo lo sintético está marcado: folio `VOL-…`, correos
`vol.*@sintetico.microhubs.mx` y `sintetico: true` en MongoDB. Para quitarlo: `python bloque_c/scripts/generar_volumen.py --borrar`.

## Cómo se midió

```bash
python bloque_c/scripts/generar_volumen.py --pedidos 10000 --clientes 5000   # etapa 1 (incluye la comparación fila por fila / COPY)
python servicios/pruebas/medir_volumen.py --etiqueta 010k
python bloque_c/scripts/generar_volumen.py --pedidos 50000  && python servicios/pruebas/medir_volumen.py --etiqueta 050k
python bloque_c/scripts/generar_volumen.py --pedidos 100000 && python servicios/pruebas/medir_volumen.py --etiqueta 100k
# … correcciones de 12_rendimiento.sql y del servicio de pedidos …
python servicios/pruebas/medir_volumen.py --etiqueta 100k_optimizado
python servicios/pruebas/medir_volumen.py --reporte                          # escribe RESULTADOS.md
```

**Ambiente:** una estación de trabajo Linux con 2 vCPU y 7 GB de RAM (más pequeña que la VM e2-standard-4) y las mismas versiones
que el compose: PostgreSQL 16, MongoDB 7.0 y Redis 7. Corrían los 26 servicios y el web con gunicorn (2 workers por servicio,
3 el web). El cliente de medición estaba en la misma máquina, así que los tiempos no incluyen red. En la VM de GCP se repite igual:
`servicios/pruebas/correr.sh modulo pruebas.medir_volumen --etiqueta nube_100k`.

## Resultados principales

**1. Inserción.** Por pedido con sus líneas, y con los triggers del motor activos (historial, auditoría y límite por línea):

| Método | Registros/s |
|---|---|
| PostgreSQL · `INSERT` fila por fila | ~1 550 pedidos/s |
| PostgreSQL · `COPY` por lotes | ~4 900–5 300 pedidos/s (**3.4× más rápido**) |
| MongoDB · `insert_one` | ~4 500 lecturas GPS/s |
| MongoDB · `insert_many` en lotes de 5 000 | ~53 000–74 000 lecturas/s (**12–16× más rápido**) |

Por eso el servicio de seguimiento recibe el GPS en lotes de hasta 500 puntos.

**2. Índices.** Con 100 k pedidos, cada índice evita recorrer la tabla completa:

| Consulta | Con índice | Sin índice |
|---|---|---|
| Auditoría de una entidad (trazabilidad) | 0.03 ms | 40 ms (recorre 397 k filas) |
| Auditoría por módulo, últimos 7 días | 0.05 ms | 78 ms |
| Historial de un pedido | 0.01 ms | 4 ms |
| Recorrido GPS de una entrega (MongoDB) | 0 ms, examina 15 documentos | 320 ms, examina 1.4 millones |
| Puntos GPS a 300 m de un microhub (2dsphere) | 658 ms, examina 206 k | 1 098 ms, examina 1.4 millones |

**3. Caché de Redis.** En el catálogo (`GET productos`), la mediana baja de 19.1 ms sin caché a 3.0 ms con caché (**6.4×**).

**4. Escalabilidad y lo que se corrigió.** Al pasar de 10 k a 100 k pedidos, varios endpoints crecieron en línea recta con la tabla.
Eran consultas lentas reales, que con los pocos datos de la demostración no se notaban. La columna «100 k corregido» se midió otra
vez sobre una carga nueva de 100 k pedidos, después de todas las correcciones:

| Endpoint (mediana) | 10 k | 50 k | 100 k | 100 k corregido |
|---|---|---|---|---|
| `GET pedidos` (página 1, entregados) | 25 ms | 68 ms | 128 ms | **28 ms** |
| `GET pedidos/resumen` (170 días, una página) | 62 ms | 207 ms | 395 ms | **216 ms** |
| `GET pedidos/ventas` (90 días) | 53 ms | 225 ms | 398 ms | **220 ms** |
| `GET reportes/pedidos_por_dia` (90 días, recorre varias páginas) | 207 ms | 673 ms | 1 103 ms | **212 ms** |
| `POST demanda/sincronizacion` (170 días por categoría, ~70 páginas) | 5.2 s | 19.5 s | **37.5 s** | **1.1 s** |

Causas y correcciones (`bloque_c/sql/12_rendimiento.sql`, `servicios/pedidos/app.py`, `servicios/demanda/app.py`):

- `fn_pedidos_visibles` estaba en PL/pgSQL. PostgreSQL ejecuta esa función completa, así que devolvía los 100 000 pedidos y
  **después** filtraba. Ahora es una función SQL que el planificador integra a la consulta: buscar un pedido por id dentro del
  ámbito bajó de 31.6 ms a 0.2 ms. Se comprobó que devuelve exactamente los mismos pedidos que la versión anterior para los 98
  usuarios probados. En las listas, el servicio aplica la misma regla de ámbito directamente sobre la tabla y recorre el índice
  `ix_web_pedido_fecha`: la página 1 bajó de 55 ms a 0.17 ms en la base y de 128 ms a 28 ms en la API.
- `pedidos/resumen` y `pedidos/ventas` filtraban con `(creado_en AT TIME ZONE …)::date BETWEEN`, que no usa índice, y calculaban
  todo el periodo **dos veces por página** (una para contar y otra para la página). Demanda y reportes recorren todas las páginas, así
  que el trabajo crecía con *páginas × pedidos*. Ahora filtran por rango de `creado_en` y calculan una sola vez. La página 1 siempre
  se calcula de nuevo (una consulta suelta está al día). De la 2 en adelante salen de una copia de 60 s en Redis
  (`cache:pedidos:*`, con el ámbito del perfil en la llave), así que quien recorre todas las páginas recibe una sola foto
  consistente. Con la caché sirviendo también la página 1, las pruebas de reportes de la Ola 3 detectaron totales viejos tras crear
  pedidos; por eso la página 1 no la usa.
- La sincronización de demanda insertaba fila por fila; ahora usa `executemany` (un viaje por lote).
- Se agregaron dos índices: `ix_pedido_dia_local` (expresión del día local) e `ix_detalle_pedido_cubriente` (las ventas se suman
  sin ir a la tabla).
- Lo que no se aceleró: una página suelta de un resumen de 170 días sigue costando ~200 ms con 100 k pedidos. Es una agregación de
  todo el periodo y crece con el volumen. Con millones de pedidos haría falta una tabla de resumen diaria (vista materializada o
  `demanda_observacion`, que ya existe y se alimenta con la sincronización).

**5. Recursos con 100 k pedidos.** Memoria residente: PostgreSQL 531 MB, MongoDB 783 MB, Redis 10 MB y los 27 procesos web y de
servicios unos 4.8 GB (≈ 90 MB por worker de gunicorn). La memoria de los servicios no depende del volumen de datos sino del número
de workers. En la VM de 16 GB caben con holgura; en una máquina de 8 GB conviene bajar a 1 worker los servicios de poco uso.

## Límites y lo que sigue

- `GET auditoria` cuenta el total exacto de filas que cumplen el filtro (63 ms con 300 k eventos de pedidos). Con millones de
  eventos convendría paginar por cursor (`fecha, id`) o mostrar un total estimado.
- `ix_detalle_pedido` es redundante con el índice único `(pedido_id, producto_id)`, que ya empieza por `pedido_id`. Se puede quitar
  para abaratar las inserciones.
- No hizo falta particionar ni usar BigQuery o Pub/Sub: 100 k pedidos y 1.4 millones de puntos GPS caben bien en una sola instancia.
  El primer candidato a particionar por mes sería `ubicaciones_entrega` (en MongoDB, por fecha), si el GPS se mandara cada 5 s en lugar de cada 30 s.
