# Runbook: demostración de tolerancia a fallos en vivo

En la presentación final el profesor puede pedir cualquiera de los ocho casos de esta guía. Para cada uno hay un comando exacto,
lo que se debe ver y dónde mostrarlo. Los resultados de una corrida completa están en
[`evidencias/fallos/fallos_infraestructura.md`](../evidencias/fallos/fallos_infraestructura.md). Se generan con
`python servicios/pruebas/demo_fallos_infra.py`.

## Antes de empezar (10 minutos antes)

```bash
gcloud compute instances start microhubs-vm --zone northamerica-south1-c      # la VM está apagada para no gastar
gcloud compute ssh microhubs-vm --zone northamerica-south1-c
cd ~/microhubs && set -a && . ./.env && set +a
C="docker compose --env-file .env -f docker-compose.integrado.yml -f deploy/gcp/docker-compose.gcp.yml"
$C ps                                                                          # todo healthy
$C exec entregas python pruebas/preparar_entregas.py --cantidad 3             # entregas en ruta para la app
```

Pestañas abiertas en el navegador:

1. `https://<host>/web/servicios/monitoreo`: el panel, con sesión de administrador.
2. `https://<host>/servicios/auth/api/v1/docs`: Swagger, para pedir tokens.
3. La consola de **Cloud Logging**, filtrada por `jsonPayload.traza_id` o por texto.

Tener una terminal con `H=https://<host>/servicios`, un token de administrador en `$TA` y uno de repartidor en `$TR`:

```bash
TA=$(curl -s -X POST $H/auth/api/v1/auth/login -H 'Content-Type: application/json' -d "{\"correo\":\"admin@codex.mx\",\"clave\":\"$MICROHUBS_CLAVE\"}" | jq -r .token_acceso)
TR=$(curl -s -X POST $H/auth/api/v1/auth/login -H 'Content-Type: application/json' -d "{\"correo\":\"repartidor1@codex.mx\",\"clave\":\"$MICROHUBS_CLAVE\"}" | jq -r .token_acceso)
```

## Lo que el sistema debe demostrar en cada caso

1. **Detecta**: `/salud` del servicio y el panel cambian a *caído* o *degradado*, y se abre una alerta.
2. **Registra**: la respuesta de error trae `traza_id`, y esa misma traza aparece en `logs_tecnicos` (MongoDB) y en Cloud Logging.
3. **Informa**: un JSON `{codigo, mensaje, traza_id}` en español. Nunca una página de error ni un *stack trace*.
4. **No corrompe**: lo que no se pudo completar no deja nada a medias (se muestra con un conteo antes y después).
5. **Se recupera**: al restablecer la pieza, la siguiente petición funciona sin reiniciar nada más.

## 1. Detener un microservicio

```bash
$C stop inventario
curl -s $H/abastecimiento/api/v1/abastecimiento/necesidades?microhub_id=1 -H "Authorization: Bearer $TA" | jq   # 503: «El servicio inventario no responde»
curl -s $H/productos/api/v1/productos?por_pagina=2 -H "Authorization: Bearer $TA" | jq .paginacion            # 200: lo demás sigue
curl -s -X POST $H/auditoria-monitoreo/api/v1/monitoreo/verificaciones -H "Authorization: Bearer $TA" -H 'Content-Type: application/json' -d '{"servicio":"inventario"}' | jq
$C start inventario      # en el panel la alerta «servicio_caido» se cierra sola en la siguiente ronda (≤ 30 s)
```

Lo que se ve en la corrida: 503 en 14 ms, el panel con *caído* y una alerta crítica que se cerró 4 s después de arrancar el servicio.

Si piden la recepción de mercancía con inventario caído: responde **202** con la entrada pendiente. Repetir el POST la aplica una sola
vez (`evidencias/ola1/fallo_inventario.md`).

## 2. Revocar un token

```bash
curl -s -X POST $H/auth/api/v1/auth/salir -H "Authorization: Bearer $TR" -o /dev/null -w "%{http_code}\n"    # 204
curl -s $H/usuarios/api/v1/usuarios/yo -H "Authorization: Bearer $TR" | jq                                   # 401 TOKEN_INVALIDO en CUALQUIER servicio
```

Por qué funciona: el `jti` queda en `auth:jti:revocado:{jti}` y sale de `auth:sesion:{id}` en Redis. Cada servicio lo revisa en cada
petición. El token de renovación sirve una sola vez (casos AUTH-08 a AUTH-11).

## 3. Desactivar temporalmente Redis

```bash
$C stop redis
curl -s $H/productos/api/v1/productos -H "Authorization: Bearer $TA" | jq     # 503 «No se pudo validar la sesión»
curl -s $H/productos/api/v1/salud | jq .dependencias                         # redis: error → degradado
$C start redis
curl -s $H/productos/api/v1/productos -H "Authorization: Bearer $TA" | jq     # 401: la sesión se perdió → volver a entrar
```

Hay que saber explicar dos decisiones:

- **Cierre seguro.** Sin Redis no hay forma de saber si un token fue revocado, así que se niega el paso (503). No se deja entrar a
  ciegas.
- **Sesiones que se pierden.** Redis corre sin persistencia (`--save ""`), así que al volver todos tienen que iniciar sesión otra vez.
  Es la consecuencia aceptada del cierre seguro. El límite de consumo *no* bloquea si Redis falla, y el verificador del monitoreo sigue
  trabajando (en la corrida guardó 364 verificaciones mientras Redis estaba abajo).

## 4. Provocar una respuesta inválida

```bash
# JSON mal formado
curl -s -X POST $H/auth/api/v1/auth/login -H 'Content-Type: application/json' -d '{"correo": ' | jq                      # 400
# Datos que no cumplen el contrato: todos los errores juntos, campo por campo
curl -s -X PATCH $H/usuarios/api/v1/usuarios/yo -H "Authorization: Bearer $TA" -H 'Content-Type: application/json' -d '{"telefono":"12"}' | jq   # 422
# XML con DTD (ataque XXE)
curl -s -X POST $H/auth/api/v1/auth/login -H 'Content-Type: application/xml' -H 'Accept: application/xml' \
  -d '<?xml version="1.0"?><!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]><login xmlns="urn:microhubs:v1"><correo>&e;</correo><clave>x</clave></login>'   # 400
# Un archivo que dice ser JPEG pero es PDF
#   caso DOC-03 de las evidencias: 422 «La firma del archivo no corresponde al tipo»
```

## 5. Consultar un archivo inexistente

```bash
curl -s $H/documentos/api/v1/documentos/ffffffffffffffffffffffff -H "Authorization: Bearer $TA" | jq                      # 404 NO_ENCONTRADO
curl -s $H/documentos/api/v1/documentos/<id>/enlace -H "Authorization: Bearer $TA" | jq -r .url | xargs curl -s -o /dev/null -w "%{http_code}\n"   # 200 recién firmada
# 6 minutos después la misma URL → 400/403 de Cloud Storage (caducó: 300 s). Una URL con la firma alterada → 403 (evidencias/nube/pruebas_bucket.txt).
```

## 6. Simular una sobrecarga

Desde la laptop, no desde la VM:

```bash
MICROHUBS_PLANTILLA="https://<host>/servicios/{servicio}" MICROHUBS_CLAVE=... \
  locust -f pruebas_carga/locustfile.py --headless -u 150 -r 25 -t 60s --host https://<host>
```

Lo que se ve, con los límites normales:

- después de 30 inicios de sesión por minuto desde la misma IP, **429** con `Retry-After`;
- después de 20 peticiones por segundo, Nginx también responde **429**;
- en el panel suben el p95 y las peticiones por hora, y al terminar todo vuelve a la normalidad en segundos.

En la prueba de estrés, al bajar de 500 a 50 usuarios el p95 volvió a lo normal en **8 s**
(`evidencias/carga/RESULTADOS.md`). Una ráfaga corta desde la terminal:

```bash
for i in $(seq 1 40); do curl -s -o /dev/null -w "%{http_code} " -X POST $H/auth/api/v1/auth/login -H 'Content-Type: application/json' -d '{"correo":"x@x.mx","clave":"malaclave1"}'; done; echo
```

## 7. Mostrar un intento sin permisos

```bash
curl -s $H/usuarios/api/v1/usuarios -H "Authorization: Bearer $TR" | jq          # 403: un repartidor no tiene usuarios.ver
curl -s $H/entregas/api/v1/entregas/<entrega de otro repartidor> -H "Authorization: Bearer $TR" | jq   # 404: ni siquiera se revela que existe
curl -s "$H/auditoria-monitoreo/api/v1/auditoria?exitoso=false&por_pagina=5" -H "Authorization: Bearer $TA" | jq '.datos[] | {fecha, modulo, accion, detalle, ip_origen}'
```

Desde la entrega final, la IP que queda en la bitácora es la del cliente real, no la de Nginx (`DETRAS_DE_PROXY=1`).

## 8. Explicar un error en los logs

1. Provocar un 503, por ejemplo con el caso 1, y copiar su `traza_id` de la respuesta.
2. En **Cloud Logging**: `jsonPayload.traza_id="<traza>"` o `textPayload:"<traza>"`. Muestra la línea del contenedor con la excepción.
3. En MongoDB:
   `$C exec mongo mongosh microhubs_eventos --quiet --eval 'db.logs_tecnicos.findOne({correlacion_id:"<traza>"})'`
   Muestra nivel, componente, ruta, duración, código de error y la excepción real. Por ejemplo, con PostgreSQL caído:
   `OperationalError: connection failed … Connection refused`.
4. Explicar el camino: el servicio que falló registra la traza que recibió en `X-Traza-Id`. El que lo llamó reenvía la misma traza, así
   que una sola búsqueda muestra toda la cadena (web → servicio → servicio).

## Otros casos ya probados

| Caso | Resultado | Evidencia |
|---|---|---|
| MongoDB no responde | documentos y recorrido GPS: 503. El **cierre de la entrega sí se aplica en PostgreSQL** (201, la foto ya estaba subida). El catálogo sigue funcionando: solo la primera petición de cada proceso espera 2 s; después el cortacircuitos no vuelve a intentar durante 30 s | `evidencias/fallos/` |
| PostgreSQL no responde | 503 uniforme en lecturas, escrituras y login; 0 solicitudes guardadas a medias; vuelve sin reiniciar los servicios | `evidencias/fallos/` |
| Bucket no disponible | `/salud` de documentos degradado, subir da 503 y no queda el registro en MongoDB | `evidencias/fallos/`, `evidencias/nube/pruebas_bucket.txt` |
| Tiempo máximo excedido | con costos congelado, el punto de equilibrio corta a los 4 s (`MICROSERVICIOS_TIEMPO`) con 503 y no guarda el escenario | `evidencias/fallos/` |
