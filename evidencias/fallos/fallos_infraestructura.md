# Fallos de infraestructura: qué pasa y cómo se recupera

Corrida del 2026-11-26T23:41:46+00:00 con `servicios/pruebas/demo_fallos_infra.py` (entorno local sin Docker: PostgreSQL 16, MongoDB 7, Redis 7 y los 26 servicios con gunicorn). Datos crudos: `fallos_infraestructura.json`.

«Recuperación» es el tiempo desde que termina el comando que restablece la pieza hasta la primera respuesta correcta, sin reiniciar ningún otro servicio (los servicios reconectan solos a PostgreSQL, Redis y MongoDB en la siguiente petición).

| Caso | Peticiones | Cumplen lo esperado | Recuperación |
|---|---|---|---|
| Un microservicio se detiene (inventario) | 6 | 5 de 5 | 0.0 s |
| Redis no responde | 6 | 6 de 6 | 0.0 s |
| MongoDB no responde | 9 | 9 de 9 | 0.0 s |
| PostgreSQL no responde | 6 | 6 de 6 | 0.0 s |
| El servicio de archivos no está disponible | 4 | 4 de 4 | 0.0 s |
| Una petición excede el tiempo máximo (costos congelado) | 3 | 3 de 3 | 0.1 s |

## Un microservicio se detiene (inventario)

| Paso | HTTP | Esperado | Código | Mensaje | ms | Traza |
|---|---|---|---|---|---|---|
| Antes: GET inventario (operador) | 200 ✓ | 200 | — | — | 45 | — |
| Durante: GET inventario directo | sin conexión: [Errno 111] Connection refused | — | — | — | 0 | — |
| Durante: GET abastecimiento/necesidades (necesita inventario) | 503 ✓ | 503 | SERVICIO_NO_DISPONIBLE | El servicio inventario no responde. Intenta más tarde. | 14 | 73ea1e0e |
| Durante: GET productos (no depende de inventario) | 200 ✓ | 200 | — | — | 2 | — |
| Durante: el monitoreo verifica (POST monitoreo/verificaciones) | 201 ✓ | 201 | — | — | 43 | — |
| Después: GET inventario | 200 ✓ | 200 | — | — | 20 | — |

```json
{
  "recuperacion_s": 0.0,
  "monitoreo": {
    "estado_verificado": "caido",
    "error": "El servicio inventario no responde. Intenta más tarde.",
    "alertas_abiertas": [
      [
        "servicio_caido",
        "critica",
        "inventario no responde. El servicio inventario no responde. Intenta más tarde."
      ]
    ],
    "ultima_alerta_tras_volver": [
      [
        "servicio_caido",
        "2026-11-26 17:41:48.138985-06",
        "2026-11-26 17:41:52.337247-06"
      ]
    ]
  }
}
```

Registro técnico de la traza del error (MongoDB `logs_tecnicos`):

```json
{
  "nivel": "ERROR",
  "componente": "abastecimiento",
  "registrado_en": "2026-11-26T23:41:48.098000",
  "mensaje": "GET /api/v1/abastecimiento/necesidades -> 503",
  "ruta": "/api/v1/abastecimiento/necesidades",
  "duracion_ms": 8,
  "contexto": {
    "metodo": "GET",
    "status": 503,
    "formato": "json",
    "codigo_error": "SERVICIO_NO_DISPONIBLE"
  },
  "excepcion": null
}
```

## Redis no responde

| Paso | HTTP | Esperado | Código | Mensaje | ms | Traza |
|---|---|---|---|---|---|---|
| Antes: GET productos (con sesión en Redis) | 200 ✓ | 200 | — | — | 3 | — |
| Durante: GET productos con un token válido | 503 ✓ | 503 | SERVICIO_NO_DISPONIBLE | No se pudo validar la sesión. Intenta más tarde. | 2 | 953dfa86 |
| Durante: POST auth/login | 503 ✓ | 503 | SERVICIO_NO_DISPONIBLE | Una base de datos no responde. Intenta más tarde. | 17 | a2cfddea |
| Durante: GET /salud de productos | 503 ✓ | 503 | — | — | 5 | — |
| Después: el token anterior | 401 ✓ | 401 | TOKEN_INVALIDO | La sesión venció o fue cerrada. Inicia sesión de nuevo. | 5 | 184e73b3 |
| Después: se vuelve a iniciar sesión y GET productos | 200 ✓ | 200 | — | — | 58 | — |

```json
{
  "recuperacion_s": 0.0,
  "salud_durante": {
    "postgres": "ok",
    "redis": "error",
    "mongo": "no_aplica",
    "bucket": "no_aplica"
  },
  "monitoreo": {
    "verificaciones_guardadas_durante_la_falla": 364,
    "ultima_de_productos": [
      [
        "productos",
        "degradado",
        "{\"postgres\": \"ok\", \"redis\": \"error\", \"mongo\": \"no_aplica\", \"bucket\": \"no_aplica\"}"
      ]
    ]
  }
}
```

## MongoDB no responde

| Paso | HTTP | Esperado | Código | Mensaje | ms | Traza |
|---|---|---|---|---|---|---|
| Antes: GET documentos (resumen en MongoDB) | 200 ✓ | 200 | — | — | 6 | — |
| Antes: el repartidor sube la foto de evidencia de la entrega 95076 | 201 ✓ | 201 | — | — | 28 | — |
| Durante: GET documentos/resumen | 503 ✓ | 503 | SERVICIO_NO_DISPONIBLE | MongoDB no responde. Intenta más tarde. | 4038 | 93aea8e8 |
| Durante: GET seguimiento/95076/recorrido | 503 ✓ | 503 | SERVICIO_NO_DISPONIBLE | MongoDB no responde. Intenta más tarde. | 4502 | d62c6e24 |
| Durante: POST entregas/95076/resultado (cierre en PostgreSQL) | 201 ✓ | 201 | — | — | 5008 | — |
| Durante: GET productos (no usa MongoDB) #1 | 200 ✓ | 200 | — | — | 2489 | — |
| Durante: GET productos (no usa MongoDB) #2 | 200 ✓ | 200 | — | — | 3 | — |
| Durante: GET productos (no usa MongoDB) #3 | 200 ✓ | 200 | — | — | 2 | — |
| Después: GET documentos/resumen | 200 ✓ | 200 | — | — | 4 | — |

```json
{
  "recuperacion_s": 0.0,
  "entrega_cerrada_en_postgres": [
    [
      "fallida",
      "entrega_fallida"
    ]
  ]
}
```

## PostgreSQL no responde

| Paso | HTTP | Esperado | Código | Mensaje | ms | Traza |
|---|---|---|---|---|---|---|
| Antes: GET pedidos | 200 ✓ | 200 | — | — | 37 | — |
| Durante: GET pedidos | 503 ✓ | 503 | SERVICIO_NO_DISPONIBLE | Una base de datos no responde. Intenta más tarde. | 9 | d3f0cd33 |
| Durante: POST auth/login | 503 ✓ | 503 | SERVICIO_NO_DISPONIBLE | Una base de datos no responde. Intenta más tarde. | 14 | 64ee9839 |
| Durante: POST abastecimiento/solicitudes (escritura) | 503 ✓ | 503 | SERVICIO_NO_DISPONIBLE | Una base de datos no responde. Intenta más tarde. | 7 | 7e798c69 |
| Durante: GET /salud de pedidos | 503 ✓ | 503 | — | — | 2 | — |
| Después: GET pedidos (sin reiniciar el servicio) | 200 ✓ | 200 | — | — | 21 | — |

```json
{
  "recuperacion_s": 0.0,
  "salud_durante": {
    "postgres": "error",
    "redis": "ok",
    "mongo": "no_aplica",
    "bucket": "no_aplica"
  },
  "datos_a_medias": {
    "solicitudes_guardadas_durante_la_falla": [
      [
        0
      ]
    ]
  }
}
```

Registro técnico de la traza del error (MongoDB `logs_tecnicos`):

```json
{
  "nivel": "ERROR",
  "componente": "pedidos",
  "registrado_en": "2026-11-26T23:43:00.985000",
  "mensaje": "GET /api/v1/pedidos -> 503",
  "ruta": "/api/v1/pedidos",
  "duracion_ms": 2,
  "contexto": {
    "metodo": "GET",
    "status": 503,
    "formato": "json",
    "codigo_error": "SERVICIO_NO_DISPONIBLE"
  },
  "excepcion": {
    "detalle": "OperationalError: connection failed: connection to server at \"127.0.0.1\", port 5432 failed: Connection refused\n\tIs the server running on that host and accepting TCP/IP connections?"
  }
}
```

## El servicio de archivos no está disponible

| Paso | HTTP | Esperado | Código | Mensaje | ms | Traza |
|---|---|---|---|---|---|---|
| Antes: GET documentos/resumen | 200 ✓ | 200 | — | — | 4 | — |
| Durante: GET /salud de documentos | 503 ✓ | 503 | — | — | 22 | — |
| Durante: POST documentos (subir una imagen) | 503 ✓ | 503 | SERVICIO_NO_DISPONIBLE | El almacén de archivos no responde. Intenta más tarde. | 14 | 21772bc2 |
| Después: POST documentos | 201 ✓ | 201 | — | — | 25 | — |

```json
{
  "recuperacion_s": 0.0,
  "datos_a_medias": {
    "documentos_en_mongo_antes": 4,
    "documentos_en_mongo_durante": 4,
    "ok": true
  }
}
```

Registro técnico de la traza del error (MongoDB `logs_tecnicos`):

```json
{
  "nivel": "ERROR",
  "componente": "documentos",
  "registrado_en": "2026-11-26T23:43:08.362000",
  "mensaje": "POST /api/v1/documentos -> 503",
  "ruta": "/api/v1/documentos",
  "duracion_ms": 10,
  "contexto": {
    "metodo": "POST",
    "status": 503,
    "formato": "json",
    "codigo_error": "SERVICIO_NO_DISPONIBLE"
  },
  "excepcion": {
    "detalle": "ErrorAlmacen: No se pudo escribir en el almacén local: [Errno 2] No such file or directory: '/proc/almacen_no_disponible'"
  }
}
```

## Una petición excede el tiempo máximo (costos congelado)

| Paso | HTTP | Esperado | Código | Mensaje | ms | Traza |
|---|---|---|---|---|---|---|
| Antes: POST punto-equilibrio/calculos (pide datos a costos, demanda y cobertura) | 200 ✓ | 200 | — | — | 202 | — |
| Durante: el mismo cálculo con costos congelado (guardar = true) | 503 ✓ | 503 | SERVICIO_NO_DISPONIBLE | El servicio costos no responde. Intenta más tarde. | 4056 | a8533bf4 |
| Después: el cálculo | 200 ✓ | 200 | — | — | 67 | — |

```json
{
  "recuperacion_s": 0.1,
  "tiempo_maximo_s": 4.0,
  "respuesta_ms": 4056,
  "datos_a_medias": {
    "escenarios_antes": [
      [
        0
      ]
    ],
    "escenarios_despues": [
      [
        0
      ]
    ]
  }
}
```

Registro técnico de la traza del error (MongoDB `logs_tecnicos`):

```json
{
  "nivel": "INFO",
  "componente": "demanda",
  "registrado_en": "2026-11-26T23:43:15.766000",
  "mensaje": "GET /api/v1/demanda/resumen -> 200",
  "ruta": "/api/v1/demanda/resumen",
  "duracion_ms": 34,
  "contexto": {
    "metodo": "GET",
    "status": 200,
    "formato": "json",
    "codigo_error": null
  },
  "excepcion": null
}
```
