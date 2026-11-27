# Análisis de la prueba de carga en la nube

Corrida de la versión `fd85013` (26 de noviembre de 2026). Datos en [`informe_carga.md`](informe_carga.md) y [`carga.html`](carga.html). Una sola VM
e2-standard-4; el generador de carga corre en la misma máquina, así que las cifras son un piso: con el generador aparte habría algo más de CPU.

**Total:** 10,412 peticiones, 23.1 por segundo, media 857 ms, p95 5.7 s, p99 12 s y 15 errores (0.14 %), todos 503.

## Qué aguanta

- Hasta **100 usuarios simultáneos** (41.5 peticiones por segundo) sin errores; el 95 % responde en 1.3 s o menos.
- Con **200 usuarios** rinde 51.2 peticiones por segundo, el p95 sube a 4.5 s y aparece 0.37 % de errores: ahí se satura. La mitad de las peticiones sigue
  respondiendo en menos de 0.1 s; la degradación está en unas pocas rutas.

## Dónde está el cuello de botella

| Observación | Causa probable | Mejora propuesta |
|---|---|---|
| `reportes/indicadores` (p95 42 s), `comparacion_microhubs` (26 s) y `pedidos_por_dia` (23 s). Los dos últimos dan los 15 errores 503 | Cada reporte encadena muchas llamadas a otros servicios, página por página; con ellos ocupados, alguna excede su tiempo de espera | Guardar el resultado en Redis 60 s, pedir resúmenes ya agregados al servicio dueño y paginar menos |
| PostgreSQL es el contenedor que más CPU usa (media 91 %, máximo 229 %) | Todas las consultas van a la misma base sin conexiones reutilizadas | Conjunto de conexiones (pool o PgBouncer) |
| Las rutas de pedidos llegan a un p95 de 8.4 s | Compiten por la base y por los pocos procesos del servicio | Más procesos para `pedidos` y caché corta de la primera página |
| El inicio de sesión es lento mientras entran los usuarios (p95 29 s) | bcrypt es lento a propósito y consume CPU cuando muchos entran a la vez | Es el costo de la seguridad; en operación las entradas no son simultáneas. Más procesos en `auth` |

## Comparación con la corrida anterior

| Versión | Peticiones | p95 | Errores | Máximo de peticiones/s |
|---|---|---|---|---|
| `0cab2a9` (antes de las mejoras de rendimiento) | 10,590 | 5.2 s | 0.10 % | 51.8 |
| `fd85013` (final) | 10,412 | 5.7 s | 0.14 % | 51.2 |

Es **una corrida de cada una** y la diferencia está dentro de lo que varía entre corridas: **bajo esta carga concurrente las mejoras no cambiaron el
resultado**. Su efecto se midió en consultas sueltas con tablas grandes (en local, `../../volumen/LEEME.md`); aquí el límite sigue siendo la CPU y los
reportes encadenados.

## Recuperación

Al bajar a 10 usuarios la mediana vuelve de inmediato (81 ms), pero el p95 del último escalón sigue alto (5.7 s) porque todavía se estaban contestando los
reportes que quedaron encolados durante el pico. No hubo errores en ese escalón ni hizo falta reiniciar nada, y las pruebas de seguridad, fallos e
integridad que corrieron después pasaron completas.

## Límite de consumo

La plataforma permite 240 peticiones por minuto por IP y servicio. Como toda la carga sale de una sola IP, el script lo sube mientras mide y lo restaura al
terminar.
