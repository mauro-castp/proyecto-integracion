# Pruebas de carga con Locust

Entorno: VM de Google Cloud e2-standard-4 (4 vCPU, 16 GB); el generador de carga corre en la misma máquina. Perfiles y escalones en `rendimiento/locustfile.py`. Tiempos en milisegundos.

**Total:** 10,590 peticiones · 23.5 por segundo · media 823 ms · p95 5200 ms · p99 10000 ms · errores 11 (0.10 %).

## Por escalón de usuarios

| Usuarios simultáneos | Peticiones/s | Media | p50 | p95 | p99 | Errores |
|---|---|---|---|---|---|---|
| 10 | 4.3 | 79 | 45 | 630 | 1200 | 0.00 % |
| 25 | 11.8 | 71 | 43 | 440 | 1200 | 0.00 % |
| 50 | 23.9 | 102 | 46 | 470 | 1400 | 0.00 % |
| 100 | 42.5 | 313 | 56 | 1100 | 4000 | 0.00 % |
| 200 | 51.8 | 1892 | 72 | 3600 | 11000 | 0.33 % |
| 10 | 4.7 | 68 | 77 | 5300 | 10000 | 0.00 % |

## Lectura

- Mayor rendimiento: **51.8 peticiones por segundo** con 200 usuarios.
- **Saturación:** a partir de 200 usuarios (p95 de 3600 ms, 0.33 % de errores).
- **Recuperación:** al bajar a 10 usuarios el p95 volvió a 5300 ms (con 10 al principio: 630 ms).

## Los 10 puntos más lentos (p95)

| Petición | Veces | Media | p95 | p99 | Errores |
|---|---|---|---|---|---|
| reportes  GET reportes/indicadores | 129 | 5831 | 43000 | 54000 | 0 |
| reportes  GET reportes/comparacion_microhubs | 99 | 5711 | 37000 | 55000 | 9 |
| auth  POST login | 200 | 9961 | 29000 | 33000 | 0 |
| pedidos  POST pedidos | 181 | 2598 | 8300 | 10000 | 0 |
| pedidos  POST pedidos/{id}/estado | 177 | 2166 | 8300 | 10000 | 0 |
| pedidos  GET pedidos?estado | 505 | 2155 | 8200 | 10000 | 0 |
| reportes  GET reportes/pedidos_por_dia | 119 | 2629 | 8100 | 46000 | 2 |
| pedidos  GET pedidos | 973 | 2130 | 8000 | 9900 | 0 |
| simulacion  POST simulacion/ejecuciones | 18 | 453 | 1700 | 1700 | 0 |
| entregas  GET entregas/mias | 1427 | 282 | 1100 | 1500 | 0 |

## Errores

| Petición | Error | Veces |
|---|---|---|
| reportes  GET reportes/comparacion_microhubs | CatchResponseError('HTTP 503') | 9 |
| reportes  GET reportes/pedidos_por_dia | CatchResponseError('HTTP 503') | 2 |

## Recursos: los contenedores que más CPU usaron

| Contenedor | CPU máxima | CPU media | Memoria |
|---|---|---|---|
| postgres | 207 % | 97 % | 241.4MiB |
| auth | 111 % | 9 % | 103.1MiB |
| mongo | 55 % | 8 % | 1.146GiB |
| inventario | 51 % | 9 % | 104.2MiB |
| sincronizacion | 46 % | 5 % | 105.1MiB |
| notificaciones | 45 % | 8 % | 103.8MiB |
| simulacion | 44 % | 4 % | 110MiB |
| entregas | 43 % | 8 % | 107.3MiB |
| seguimiento | 42 % | 5 % | 104.3MiB |
| rutas | 41 % | 5 % | 105.2MiB |

El 100 % equivale a un núcleo completo.
