# Guía de estudio para las preguntas individuales (3 × 15 puntos)

Las preguntas salen de la presentación y la demostración, y cada integrante debe poder contestar sobre **todo** el proyecto. Cada
pregunta de esta guía trae una respuesta corta, con lo que hay que decir, y un dato o archivo para mostrar.

## Arquitectura e integración

**1. Recorre una petición de la app Android hasta la base de datos.**
App → HTTPS → Nginx (`/servicios/entregas/`) → contenedor de entregas en 127.0.0.1:5105. Ahí pasa por cinco filtros:

1. `before_request`: traza y límite de consumo en Redis.
2. `requiere`: JWT válido, sesión viva y token no revocado (Redis), permiso del rol.
3. Validación del cuerpo.
4. PostgreSQL, con `app.usuario_id` fijado para que los triggers auditen.
5. Respuesta JSON o XML con `X-Traza-Id`, y una línea en `logs_tecnicos` de MongoDB.

**2. ¿Por qué 26 servicios y no uno?**
Hay una responsabilidad de negocio por servicio: cada uno se despliega, escala y falla por separado. Si inventario cae, el catálogo
sigue. Lo que no es suyo, el servicio lo pide por HTTP con el JWT del usuario, y el otro servicio aplica su propio permiso.

**3. ¿Cómo se comunican y qué pasa si uno no responde?**
Por HTTP con `comun/clientes.py`: mismo JWT, misma traza y una espera máxima de 4 s. Si el otro no responde, se devuelve 503 con el
motivo y **no se guarda nada a medias**. Ejemplos: abastecimiento devuelve 202 con la recepción pendiente, y en rutas → entregas hay
una saga con compensación.

**4. ¿Qué es una saga y dónde la usan?**
Es una transacción repartida en pasos de varios servicios, cada uno con su paso de deshacer. En el despacho, rutas confirma el plan y
llama a `entregas/asignaciones`, que es todo o nada. Si entregas rechaza, rutas regresa el plan a «propuesto» y borra sus rutas
(I-15).

**5. ¿Por qué una sola base de datos si son microservicios?**
Fue una decisión por costo y tiempo del semestre. Se mantiene la regla de que cada servicio es dueño de sus tablas y no lee las de
otro. Separarlas es trabajo futuro (una instancia o un esquema por servicio). Hay excepciones heredadas del Segundo Parcial.

## Seguridad

**6. ¿Cómo funciona la sesión?**
- El JWT de acceso dura 15 min e incluye un `jti`. El servidor lo registra en `auth:sesion:{id}` en Redis.
- El refresh es opaco, de un solo uso y rota. Se guarda en Redis como hash.
- `salir` revoca el `jti`, y cada servicio lo revisa en cada petición.

Por eso un token robado deja de servir al cerrar sesión, aunque su firma siga siendo válida.

**7. ¿Qué pasa si Redis se cae?**
Cierre seguro: 503 «No se pudo validar la sesión». No se puede saber si un token fue revocado, así que no se deja pasar a nadie. El
límite de consumo no bloquea, y al volver Redis todos inician sesión otra vez (sin persistencia).

**8. ¿Qué validan de los archivos?**
- La firma real de los primeros bytes (un PDF disfrazado de JPEG da 422).
- El tamaño máximo de 5 MB.
- El ámbito: un repartidor solo adjunta a sus entregas y la orden de compra se consulta con abastecimiento.
- Al guardar: SHA-256, una ruta de objeto generada y privacidad privada o interna.

**9. ¿Por qué la base no guarda archivos? ¿Qué es una URL firmada?**
Los archivos inflan los respaldos y la memoria de la base. MongoDB guarda solo id, ruta, tipo, tamaño, dueño, fecha, hash,
privacidad, estado y metadatos. La URL firmada V4 es un GET de un solo objeto que caduca en 300 s. La firma la VM con su identidad
(IAM signBlob), sin llave guardada en ningún archivo.

**10. Rate limiting y la IP detrás de Nginx.**
El límite es de 240 peticiones por minuto por IP y servicio, y 30 inicios de sesión. Responde 429 con `Retry-After`. Detrás de Nginx,
la IP de la conexión es la del proxy: por eso se agregó `DETRAS_DE_PROXY=1`, para que la IP salga de `X-Forwarded-For` (I-12).

## Datos

**11. ¿Qué va en cada base?**
- **PostgreSQL:** lo transaccional y las reglas en triggers (transiciones, auditoría inmutable, avisos, inventario).
- **MongoDB:** lo de alto volumen o con esquema flexible (GPS con 2dsphere y TTL, documentos, logs, métricas, simulaciones).
- **Redis:** lo efímero y rápido (sesiones, revocación, caché, límites, candados).

**12. ¿Qué aprendieron con 100 000 pedidos?**
Que una función PL/pgSQL no deja que el planificador use índices (I-09). Que filtrar por `::date` no usa índice. Que paginar
recalculando todo el periodo es cuadrático: la sincronización de demanda tardaba 37 s y ahora tarda 1.1 s (I-10). El catálogo con
caché de Redis es 6.4× más rápido. `COPY` es 3.4× más rápido que `INSERT` y `insert_many` de 12 a 16× más rápido que `insert_one`.

## Algoritmos

**13. Explica el algoritmo de rutas y su complejidad.**
Agrupa por zona, reparte en trozos de máximo 8 paradas al repartidor menos cargado y ordena las paradas así:

- **TSP exacto**, que prueba las n! permutaciones (O(n!·n)), hasta 8 paradas: ~170 ms.
- **Vecino más cercano** (O(n²)) mejorado con **2-opt** (O(n³) por pasada en esta implementación) cuando hay más paradas.

2-opt queda en promedio entre 1 % y 2.5 % arriba del óptimo y da el óptimo en el 60–100 % de los casos. Contra el orden de llegada,
la ruta es de 24 % a 40 % más corta. Ver [`ALGORITMOS.md`](ALGORITMOS.md).

**14. ¿Qué hace la simulación Monte Carlo y por qué es reproducible?**
Simula día por día: demanda de Poisson con índice semanal y ruido, y ausentismo binomial del personal. Repite eso en N réplicas y
resume con percentiles y la probabilidad de pérdida. Cada réplica usa `Random(semilla·1000003 + r)`, y la huella SHA-256 de los
resultados prueba que la misma semilla da lo mismo. Corre en segundo plano (202).

## Nube, monitoreo y pruebas

**15. Describe el despliegue en GCP.**
- Una VM e2-standard-4 en Querétaro, con IP fija.
- El firewall solo abre 80 y 443. Nginx es la única puerta.
- Los 27 contenedores publican solo en 127.0.0.1. Las bases están en una red interna sin puertos.
- El bucket es privado y la cuenta de servicio tiene permiso solo sobre él, sin llaves.
- El `.env` tiene permiso 600.
- Los registros van a Cloud Logging con el Ops Agent.

Se usó una VM y no Cloud SQL o Memorystore por costo, por control de versiones y extensiones, y porque el curso pedía administrar la
infraestructura. Ver diagrama 18.

**16. ¿Qué mide un health check y cómo decide el monitoreo?**
`/salud` informa el proceso, las dependencias (PostgreSQL, Redis, MongoDB y bucket, cuando aplican), la versión y los ms. El
monitoreo lo consulta cada 30 s:

- sin respuesta → **caído**;
- 503 con una dependencia en error → **degradado**.

Abre alertas por caída, degradación, dependencia caída, latencia o 5xx, y las cierra solo cuando el servicio vuelve.

**17. Resultados de Locust.**
- 50 usuarios: p95 de 75 ms. 150 usuarios: p95 de 110 ms. Ambos con 0 errores.
- Satura desde 350 usuarios en 2 vCPU (~95 peticiones/s, CPU al 100 %).
- Con 450 usuarios aparecen 503 controlados, ningún 500.
- Se recupera en 8 s.
- El primero en hacer fila es pedidos (2 workers síncronos). La solución sería más workers o escalar horizontalmente.

**18. Muestra un error en los logs.**
Se provoca un 503 y se toma su `traza_id`. Con ella se busca `db.logs_tecnicos.findOne({correlacion_id})` o en Cloud Logging, donde
aparecen el componente, la ruta, la duración, el código y la excepción real. Ver [`RUNBOOK_FALLOS.md`](RUNBOOK_FALLOS.md) §8.
