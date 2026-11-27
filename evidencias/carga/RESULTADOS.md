# Pruebas de carga con Locust · resultados

Generado por `pruebas_carga/resumir.py` a partir de los CSV de esta carpeta. Cómo se corrió y qué significa: [`pruebas_carga/LEEME.md`](../../pruebas_carga/LEEME.md). Reporte HTML de Locust de cada escenario: `<escenario>.html`.

## Resumen por escenario

| Escenario | Usuarios (máx.) | Peticiones | RPS promedio | Mediana (ms) | p95 (ms) | p99 (ms) | Máx. (ms) | Errores |
|---|---|---|---|---|---|---|---|---|
| Carga normal | 50 | 2,858 | 15.9 | 17 | 75 | 290 | 665 | 0 (0.00 %) |
| Carga alta | 150 | 8,457 | 47.0 | 22 | 110 | 710 | 2,480 | 0 (0.00 %) |
| Estrés y recuperación | 500 | 34,256 | 65.8 | 96 | 5600 | 9400 | 83,825 | 70 (0.20 %) |
| Protección: límites de consumo activos | 80 | 2,521 | 16.9 | 17 | 98 | 320 | 888 | 316 (12.53 %) |

## Carga normal

### Endpoints más lentos (p95)

| Endpoint | Peticiones | Errores | Mediana | p95 | p99 | Máx. |
|---|---|---|---|---|---|---|
| POST auth · POST login | 50 | 0 | 300 | 510 | 670 | 665 |
| POST simulacion · POST ejecucion (202) | 25 | 0 | 160 | 350 | 360 | 364 |
| POST sincronizacion · POST lote | 33 | 0 | 160 | 250 | 270 | 274 |
| POST sincronizacion · POST lote (reenvío) | 37 | 0 | 70 | 200 | 220 | 224 |
| GET reportes · GET ventas_por_producto (XML) | 46 | 0 | 31 | 150 | 290 | 290 |

## Carga alta

### Endpoints más lentos (p95)

| Endpoint | Peticiones | Errores | Mediana | p95 | p99 | Máx. |
|---|---|---|---|---|---|---|
| POST auth · POST login | 150 | 0 | 820 | 2000 | 2400 | 2,480 |
| POST sincronizacion · POST lote | 94 | 0 | 230 | 370 | 400 | 401 |
| POST simulacion · POST ejecucion (202) | 56 | 0 | 230 | 350 | 370 | 372 |
| POST sincronizacion · POST lote (reenvío) | 88 | 0 | 94 | 180 | 220 | 222 |
| GET reportes · GET ventas_por_producto (XML) | 116 | 0 | 40 | 160 | 340 | 362 |

## Estrés y recuperación

### Endpoints más lentos (p95)

| Endpoint | Peticiones | Errores | Mediana | p95 | p99 | Máx. |
|---|---|---|---|---|---|---|
| GET reportes · GET pedidos_por_dia (XML) | 422 | 38 | 130 | 70000 | 81000 | 83,825 |
| GET reportes · GET ventas_por_producto (XML) | 242 | 16 | 95 | 65000 | 81000 | 82,324 |
| POST auth · POST login | 500 | 0 | 2800 | 19000 | 21000 | 22,835 |
| GET pedidos · GET del microhub | 909 | 0 | 1600 | 8600 | 9600 | 9,990 |
| GET pedidos · GET mis pedidos | 2,189 | 0 | 900 | 8400 | 9700 | 10,001 |

### Errores

| Endpoint | Error | Veces |
|---|---|---|
| GET reportes · GET pedidos_por_dia (XML) | CatchResponseError('HTTP 503') | 38 |
| POST simulacion · POST ejecucion (202) | CatchResponseError('HTTP 503') | 16 |
| GET reportes · GET ventas_por_producto (XML) | CatchResponseError('HTTP 503') | 16 |

### Escalones

| Desde (s) | Usuarios | RPS | p95 (ms) | Errores/s |
|---|---|---|---|---|
| 5 | 50 | 16.7 | 54 | 0 |
| 45 | 100 | 32.2 | 64 | 0 |
| 85 | 150 | 48.5 | 76 | 0 |
| 125 | 200 | 63.4 | 130 | 0 |
| 165 | 250 | 77.8 | 210 | 0 |
| 205 | 300 | 91.4 | 810 | 0 |
| 245 | 350 | 93.0 | 2200 | 0 |
| 285 | 400 | 98.0 | 3500 | 0 |
| 325 | 450 | 96.9 | 5700 | 0.37 |
| 365 | 500 | 95.8 | 8100 | 0.65 |
| 450 | 50 | 16.1 | 71 | 0 |

- **Rendimiento máximo:** 98.0 peticiones/s con 400 usuarios.
- **Saturación:** desde 350 usuarios el p95 del tramo estable pasa de 1 s (2200 ms).
- **Recuperación:** la carga baja a 50 usuarios en el segundo 450; el p95 vuelve a menos del doble del inicial (54 ms) en el segundo 458, es decir **8 s** después.

## Protección: límites de consumo activos

### Endpoints más lentos (p95)

| Endpoint | Peticiones | Errores | Mediana | p95 | p99 | Máx. |
|---|---|---|---|---|---|---|
| POST auth · POST login | 146 | 68 | 120 | 680 | 880 | 888 |
| POST simulacion · POST ejecucion (202) | 7 | 0 | 250 | 280 | 280 | 282 |
| POST sincronizacion · POST lote | 23 | 0 | 160 | 270 | 290 | 286 |
| GET reportes · GET ventas_por_producto (XML) | 37 | 3 | 37 | 140 | 180 | 177 |
| GET monitoreo · GET estado | 61 | 0 | 73 | 130 | 200 | 195 |

### Errores

| Endpoint | Error | Veces |
|---|---|---|
| GET productos · GET buscar | CatchResponseError('HTTP 429') | 145 |
| GET productos · GET {id} | CatchResponseError('HTTP 429') | 84 |
| POST auth · POST login | HTTP 429 | 68 |
| GET pedidos · GET mis pedidos | CatchResponseError('HTTP 429') | 11 |
| GET reportes · GET ventas_por_producto (XML) | CatchResponseError('HTTP 429') | 3 |
| GET pedidos · GET del microhub | CatchResponseError('HTTP 429') | 3 |
| GET reportes · GET pedidos_por_dia (XML) | CatchResponseError('HTTP 429') | 2 |
