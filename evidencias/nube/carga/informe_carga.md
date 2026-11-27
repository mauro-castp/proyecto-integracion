# Pruebas de carga con Locust

Entorno: VM de Google Cloud e2-standard-4 (4 vCPU, 16 GB); el generador de carga corre en la misma máquina. Perfiles y escalones en `rendimiento/locustfile.py`. Tiempos en milisegundos.

**Total:** 10,412 peticiones · 23.1 por segundo · media 857 ms · p95 5700 ms · p99 12000 ms · errores 15 (0.14 %).

## Por escalón de usuarios

| Usuarios simultáneos | Peticiones/s | Media | p50 | p95 | p99 | Errores |
|---|---|---|---|---|---|---|
| 10 | 4.4 | 69 | 46 | 500 | 1100 | 0.00 % |
| 25 | 12.0 | 68 | 44 | 430 | 1400 | 0.00 % |
| 50 | 24.1 | 102 | 47 | 470 | 1800 | 0.00 % |
| 100 | 41.5 | 431 | 58 | 1300 | 6800 | 0.00 % |
| 200 | 51.2 | 1885 | 77 | 4500 | 12000 | 0.37 % |
| 10 | 4.7 | 69 | 81 | 5700 | 12000 | 0.00 % |

## Lectura

- Mayor rendimiento: **51.2 peticiones por segundo** con 200 usuarios.
- **Saturación:** a partir de 100 usuarios (p95 de 1300 ms, 0.00 % de errores).
- **Recuperación:** al bajar a 10 usuarios el p95 volvió a 5700 ms (con 10 al principio: 500 ms).

## Los 10 puntos más lentos (p95)

| Petición | Veces | Media | p95 | p99 | Errores |
|---|---|---|---|---|---|
| reportes  GET reportes/indicadores | 116 | 6765 | 42000 | 52000 | 0 |
| auth  POST login | 200 | 10626 | 29000 | 33000 | 0 |
| reportes  GET reportes/comparacion_microhubs | 74 | 5332 | 26000 | 52000 | 9 |
| reportes  GET reportes/pedidos_por_dia | 119 | 4119 | 23000 | 49000 | 6 |
| pedidos  POST pedidos | 192 | 2490 | 8500 | 8700 | 0 |
| pedidos  GET pedidos | 912 | 2301 | 8400 | 8800 | 0 |
| pedidos  GET pedidos?estado | 477 | 2379 | 8300 | 8900 | 0 |
| pedidos  POST pedidos/{id}/estado | 190 | 2236 | 8100 | 9000 | 0 |
| simulacion  POST simulacion/ejecuciones | 17 | 417 | 1300 | 1300 | 0 |
| entregas  GET entregas/mias | 1435 | 262 | 920 | 1500 | 0 |

## Errores

| Petición | Error | Veces |
|---|---|---|
| reportes  GET reportes/comparacion_microhubs | CatchResponseError('HTTP 503') | 9 |
| reportes  GET reportes/pedidos_por_dia | CatchResponseError('HTTP 503') | 6 |

## Recursos: los contenedores que más CPU usaron

| Contenedor | CPU máxima | CPU media | Memoria |
|---|---|---|---|
| postgres | 229 % | 91 % | 64.64MiB |
| mongo | 79 % | 11 % | 364MiB |
| auditoria-monitoreo | 57 % | 8 % | 126MiB |
| auth | 54 % | 6 % | 107.2MiB |
| demanda | 52 % | 4 % | 107.7MiB |
| inventario | 49 % | 8 % | 107.6MiB |
| sincronizacion | 47 % | 8 % | 107.2MiB |
| precios | 45 % | 5 % | 106.7MiB |
| documentos | 42 % | 3 % | 140.4MiB |
| pedidos | 42 % | 14 % | 108MiB |

El 100 % equivale a un núcleo completo.
