# Pruebas de carga con Locust

Entorno: equipo local con Docker (corrida corta de verificación). Perfiles y escalones en `rendimiento/locustfile.py`. Tiempos en milisegundos.

**Total:** 369 peticiones · 4.1 por segundo · media 253 ms · p95 1400 ms · p99 3500 ms · errores 0 (0.00 %).

## Por escalón de usuarios

| Usuarios simultáneos | Peticiones/s | Media | p50 | p95 | p99 | Errores |
|---|---|---|---|---|---|---|
| 5 | 1.6 | 89 | 120 | 2000 | 2300 | 0.00 % |
| 20 | 8.2 | 127 | 74 | 2000 | 3700 | 0.00 % |
| 5 | 1.8 | 50 | 68 | 1500 | 3500 | 0.00 % |

## Lectura

- Mayor rendimiento: **8.2 peticiones por segundo** con 20 usuarios.
- No se alcanzó la saturación (errores ≤ 1 % y sin que el p95 se duplicara) hasta 20 usuarios.
- **Recuperación:** al bajar a 5 usuarios el p95 volvió a 1500 ms (con 5 al principio: 2000 ms).

## Los 10 puntos más lentos (p95)

| Petición | Veces | Media | p95 | p99 | Errores |
|---|---|---|---|---|---|
| reportes  GET reportes/indicadores | 6 | 1282 | 3900 | 3900 | 0 |
| auth  POST login | 20 | 2000 | 3800 | 3800 | 0 |
| reportes  GET reportes/comparacion_microhubs | 6 | 1171 | 2400 | 2400 | 0 |
| cobertura  GET cobertura/zonas | 6 | 406 | 2200 | 2200 | 0 |
| pedidos  POST pedidos | 2 | 831 | 1400 | 1400 | 0 |
| reportes  GET reportes/pedidos_por_dia | 7 | 379 | 1200 | 1200 | 0 |
| inventario  GET inventario/alertas | 20 | 212 | 1100 | 1100 | 0 |
| simulacion  POST simulacion/ejecuciones | 4 | 506 | 1000 | 1000 | 0 |
| planeacion  GET candidatos | 4 | 241 | 800 | 800 | 0 |
| auditoria-monitoreo  GET monitoreo/estado | 12 | 203 | 600 | 600 | 0 |

## Errores

No hubo errores.

## Recursos: los contenedores que más CPU usaron

| Contenedor | CPU máxima | CPU media | Memoria |
|---|---|---|---|
| postgres | 166 % | 45 % | 116.4MiB |
| auth | 98 % | 17 % | 116.7MiB |
| mongo | 74 % | 15 % | 351.3MiB |
| microhubs-web-prueba-web | 53 % | 13 % | 27.57MiB |
| demanda | 50 % | 7 % | 112.4MiB |
| zonas | 43 % | 5 % | 108.9MiB |
| entregas | 43 % | 7 % | 114.9MiB |
| precios | 40 % | 7 % | 94.84MiB |
| auditoria-monitoreo | 38 % | 9 % | 136MiB |
| usuarios | 37 % | 4 % | 100.4MiB |

El 100 % equivale a un núcleo completo.
