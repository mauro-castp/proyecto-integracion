# Análisis de la prueba de carga en la nube

Datos en [`informe_carga.md`](informe_carga.md) y [`carga.html`](carga.html). Una sola VM e2-standard-4; el generador de carga corre en la misma máquina,
así que las cifras son un piso: con el generador aparte la plataforma tendría algo más de CPU.

## Qué aguanta

- Hasta **100 usuarios simultáneos** (42.5 peticiones por segundo) el 95 % de las peticiones responde en poco más de un segundo y no hay errores.
- Con **200 usuarios** rinde 51.8 peticiones por segundo, el p95 sube a 3.6 s y aparece 0.33 % de errores: ahí se satura. La mitad de las peticiones sigue
  respondiendo en menos de 0.1 s; la degradación está en unas pocas rutas.

## Dónde está el cuello de botella

| Observación | Causa probable | Mejora propuesta |
|---|---|---|
| `reportes/indicadores` y `reportes/comparacion_microhubs` llegan a decenas de segundos y son el origen de los 11 errores (503) | Cada reporte encadena muchas llamadas a otros servicios, página por página; con ellos ocupados, alguna excede su tiempo de espera | Guardar el resultado en Redis 60 s, pedir resúmenes ya agregados al servicio dueño y paginar menos |
| PostgreSQL es el contenedor que más CPU usa (media 97 %, máximo 207 %) | Todas las consultas van a la misma base sin conexiones reutilizadas: cada petición abre una conexión nueva | Conjunto de conexiones (pool o PgBouncer) y los índices medidos en `../volumen/volumen.md` |
| Las rutas de pedidos suben a un p95 de 8 s en el escalón alto | El filtro de alcance por perfil (`fn_pedidos_visibles`) se evalúa en cada consulta y compite por la base | Índices por cliente y estado y caché corta de la primera página |
| El inicio de sesión es lento mientras entran los usuarios | bcrypt es lento a propósito y consume CPU cuando muchos entran a la vez | Es el costo de la seguridad; en operación las entradas no son simultáneas. Escalar `auth` con más procesos |

## Recuperación

Al bajar a 10 usuarios la mediana vuelve de inmediato (77 ms), pero el p95 del último escalón sigue alto (5.3 s) porque todavía se estaban contestando los
reportes que quedaron encolados durante el pico. No hubo errores en ese escalón ni hizo falta reiniciar nada, y las pruebas de fallos y de integridad que
corrieron después pasaron completas.

## Límite de consumo

La plataforma permite 240 peticiones por minuto por IP y servicio. Como toda la carga sale de una sola IP, el script lo sube mientras mide y lo restaura al
terminar (comprobado: volvió a 240).
