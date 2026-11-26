# Evidencias de petición y respuesta · microservicios v1

Generado el 2026-11-26 20:20 contra los servicios en ejecución. 403 de 403 casos pasan.

## Servicio auth · puerto 5101

### AUTH-01 · Iniciar sesión (JSON) · PASA

**Objetivo.** Emitir el JWT de acceso y el token de renovación del repartidor.

**Petición.** `POST http://auth:5101/api/v1/auth/login`

```http
Accept: application/json
X-Traza-Id: c9cc56c1-adc5-4b49-aa65-c348c94e91f2
Content-Type: application/json
```

```json
{
  "correo": "repartidor1@codex.mx",
  "clave": "********",
  "dispositivo": "Pixel 7"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 284 ms · traza `c9cc56c1-adc5-4b49-aa65-c348c94e91f2`

```json
{
  "token_acceso": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwicm9sIjo…(291 caracteres)",
  "token_renovacion": "rt_cd8988ee36f1285b846425af639734a8",
  "tipo": "Bearer",
  "expira_en": 900,
  "usuario": {
    "id": 7,
    "nombre": "Ramiro",
    "apellidos": "Alanís Lozano",
    "correo": "repartidor1@codex.mx",
    "rol": "repartidor",
    "microhub_id": null,
    "permisos": [
      "archivos.crear",
      "archivos.ver",
      "entregas.cerrar",
      "entregas.ver",
      "notificaciones.ver",
      "pedidos.ver",
      "sincronizacion.usar"
    ]
  }
}
```

**Explicación.** bcrypt valida la clave; el jti del acceso se agrega a la sesión activa en Redis y la renovación se guarda como hash con TTL de 7 días. El login queda en la bitácora.

**Evidencia en Redis.** `SMEMBERS auth:sesion:7; TTL auth:sesion:7; TTL auth:refresh:359280775d8800603045338d0eaee9364bfc5e42da97fc8d6aaaff889b3f856d`

```json
[
  {
    "comando": "SMEMBERS auth:sesion:7",
    "valor": [
      "1dfde881f7ad4e70930bf2b7caa7879b",
      "2c7905a2c5d445828bf1c5b1c41cbd22",
      "a2ff69ed182942d9bd19314b5a58a18e"
    ]
  },
  {
    "comando": "TTL auth:sesion:7",
    "valor": 900
  },
  {
    "comando": "TTL auth:refresh:359280775d8800603045338d0eaee9364bfc5e42da97fc8d6aaaff889b3f856d",
    "valor": 604800
  }
]
```

**Evidencia en PostgreSQL.** `SELECT fecha, modulo, accion, detalle FROM auditoria WHERE correo_intento IS NULL AND usuario_id = 7 AND modulo = 'auth' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "fecha": "2026-11-26 14:19:27.765061-06:00",
    "modulo": "auth",
    "accion": "login_exitoso",
    "detalle": "Inicio de sesión por API (Pixel 7)."
  }
]
```

### AUTH-02 · Iniciar sesión (XML) · PASA

**Objetivo.** La app de escritorio entra con XML validado por auth.xsd.

**Petición.** `POST http://auth:5101/api/v1/auth/login`

```http
Accept: application/xml
X-Traza-Id: 9c8afe0d-04b3-49e7-91ab-22afa38c38ed
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><login xmlns="urn:microhubs:v1"><correo>planeador@codex.mx</correo><clave>********</clave></login>
```

**Respuesta.** HTTP 200 (esperado 200) · 330 ms · traza `9c8afe0d-04b3-49e7-91ab-22afa38c38ed`

```xml
<?xml version='1.0' encoding='utf-8'?>
<sesion xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><token_acceso>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwicm9sIjo…(291 caracteres)</token_acceso><token_renovacion>rt_3ce1c52c0b0b1ebbb76f2562c6cd5e9e</token_renovacion><tipo>Bearer</tipo><expira_en>900</expira_en><usuario><id>5</id><nombre>Vanessa</nombre><apellidos>Morante López</apellidos><correo>planeador@codex.mx</correo><rol>planeador</rol><microhub_id xsi:nil="true" /><permisos><permiso>abastecimiento.ver</permiso><permiso>archivos.crear</permiso><permiso>archivos.ver</permiso><permiso>capacidad.editar</permiso><permiso>capacidad.ver</permiso><permiso>catalogo_publico.ver</permiso><permiso>cobertura.ver</permiso><permiso>configuracion.ver</permiso><permiso>costos.editar</permiso><permiso>costos.ver</permiso><permiso>demanda.editar</permiso><permiso>demanda.ver</permiso><permiso>equilibrio.editar</permiso><permiso>equilibrio.ver</permiso><permiso>indicadores.ver</permiso><permiso>inventario.ver</permiso><permiso>microhubs.ver</permiso><permiso>monitoreo.ver</permiso><permiso>notificaciones.ver</permiso><permiso>pedidos.reasignar</permiso><permiso>pedidos.ver</permiso><permiso>planeacion.editar</permiso><permiso>planeacion.ver</permiso><permiso>precios.ver</permiso><permiso>productos.ver</permiso><permiso>proveedores.ver</permiso><permiso>reportes.exportar</permiso><permiso>reportes.ver</permiso><permiso>rutas.planear</permiso><permiso>rutas.ver</permiso><permiso>simulacion.ejecutar</permiso><permiso>simulacion.ver</permiso><permiso>surtido.editar</permiso><permiso>surtido.ver</permiso><permiso>zonas.ver</permiso></permisos></usuario></sesion>
```

**Explicación.** El cuerpo XML se valida contra los XSD antes de procesarse; la respuesta <sesion> también cumple el XSD.

### AUTH-03 · Clave incorrecta · PASA

**Objetivo.** Rechazar credenciales y contar el intento.

**Petición.** `POST http://auth:5101/api/v1/auth/login`

```http
Accept: application/json
X-Traza-Id: 732661d4-17f1-4cf4-940d-dc73c1eb1283
Content-Type: application/json
```

```json
{
  "correo": "auditor@codex.mx",
  "clave": "********"
}
```

**Respuesta.** HTTP 401 (esperado 401) · 228 ms · traza `732661d4-17f1-4cf4-940d-dc73c1eb1283`

```json
{
  "error": {
    "codigo": "CREDENCIALES_INVALIDAS",
    "mensaje": "Correo o clave incorrectos. Intento 1 de 5.",
    "traza_id": "732661d4-17f1-4cf4-940d-dc73c1eb1283"
  }
}
```

**Explicación.** Cada intento fallido incrementa un contador en Redis; al quinto la cuenta se bloquea 15 minutos (423).

**Evidencia en Redis.** `GET auth:intentos:auditor@codex.mx; TTL auth:intentos:auditor@codex.mx`

```json
[
  {
    "comando": "GET auth:intentos:auditor@codex.mx",
    "valor": "1"
  },
  {
    "comando": "TTL auth:intentos:auditor@codex.mx",
    "valor": 900
  }
]
```

### AUTH-04 · Correo con formato inválido · PASA

**Objetivo.** Validación de entrada con detalle por campo.

**Petición.** `POST http://auth:5101/api/v1/auth/login`

```http
Accept: application/json
X-Traza-Id: 6abf943a-982a-433b-82e2-6112cea6ad48
Content-Type: application/json
```

```json
{
  "correo": "sin-arroba",
  "clave": "********"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 6 ms · traza `6abf943a-982a-433b-82e2-6112cea6ad48`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "correo",
        "mensaje": "Ingresa un correo válido."
      },
      {
        "campo": "clave",
        "mensaje": "Debe tener al menos 1 caracteres."
      }
    ],
    "traza_id": "6abf943a-982a-433b-82e2-6112cea6ad48"
  }
}
```

### AUTH-05 · XML con DTD (ataque XXE) · PASA

**Objetivo.** Rechazar entidades externas y DTD.

**Petición.** `POST http://auth:5101/api/v1/auth/login`

```http
Accept: application/xml
X-Traza-Id: 34057b3f-062b-4396-bfc9-4fe14bf1af83
Content-Type: application/xml
```

```xml
<?xml version="1.0"?><!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]><login xmlns="urn:microhubs:v1"><correo>&e;</correo><clave>********</clave></login>
```

**Respuesta.** HTTP 400 (esperado 400) · 7 ms · traza `34057b3f-062b-4396-bfc9-4fe14bf1af83`

```xml
<?xml version='1.0' encoding='utf-8'?>
<error xmlns="urn:microhubs:v1" version="1"><codigo>XML_INVALIDO</codigo><mensaje>El cuerpo XML no está bien formado o contiene DTD/entidades.</mensaje><traza_id>34057b3f-062b-4396-bfc9-4fe14bf1af83</traza_id></error>
```

**Explicación.** El lector XML (defusedxml) prohíbe DTD y entidades; el error también llega en XML.

### AUTH-06 · Validar token · PASA

**Objetivo.** Comprobar firma, vigencia y sesión activa en Redis.

**Petición.** `GET http://auth:5101/api/v1/auth/validar`

```http
Accept: application/json
X-Traza-Id: 3d95ce9a-8dcf-40bc-8c7d-8e9481e9e037
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 6 ms · traza `3d95ce9a-8dcf-40bc-8c7d-8e9481e9e037`

```json
{
  "valido": true,
  "expira_en": 899,
  "usuario": {
    "id": 7,
    "rol": "repartidor",
    "microhub_id": null
  }
}
```

### AUTH-07 · Token alterado · PASA

**Objetivo.** Un token con la firma modificada no pasa.

**Petición.** `GET http://auth:5101/api/v1/auth/validar`

```http
Accept: application/json
X-Traza-Id: ccaf13c3-f5bc-4d37-b303-d29cdcf5a3bc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 401 (esperado 401) · 5 ms · traza `ccaf13c3-f5bc-4d37-b303-d29cdcf5a3bc`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.",
    "traza_id": "ccaf13c3-f5bc-4d37-b303-d29cdcf5a3bc"
  }
}
```

### AUTH-08 · Renovar sesión · PASA

**Objetivo.** Obtener tokens nuevos con el token de renovación (rotación).

**Petición.** `POST http://auth:5101/api/v1/auth/renovar`

```http
Accept: application/json
X-Traza-Id: 9ec1eaec-0acd-4d97-93fb-8bc0948f8567
Content-Type: application/json
```

```json
{
  "token_renovacion": "rt_a044f2a7bec4ef41b2d75c00cb9f44a5"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 72 ms · traza `9ec1eaec-0acd-4d97-93fb-8bc0948f8567`

```json
{
  "token_acceso": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwicm9sIjo…(291 caracteres)",
  "token_renovacion": "rt_e936bd994e785a0acb797aff9140f148",
  "tipo": "Bearer",
  "expira_en": 900
}
```

**Explicación.** El token de renovación usado se borra de Redis y su acceso anterior queda revocado.

**Evidencia en Redis.** `EXISTS auth:refresh:f03639dbbdeb433ab08c2a89db15c46b0faef3dfe2a579eb6dbb66b747accc26`

```json
[
  {
    "comando": "EXISTS auth:refresh:f03639dbbdeb433ab08c2a89db15c46b0faef3dfe2a579eb6dbb66b747accc26",
    "valor": 0
  }
]
```

### AUTH-09 · Reusar un token de renovación · PASA

**Objetivo.** Un token de renovación sirve una sola vez.

**Petición.** `POST http://auth:5101/api/v1/auth/renovar`

```http
Accept: application/json
X-Traza-Id: c520b43b-c547-4535-86e9-cdc74620a76b
Content-Type: application/json
```

```json
{
  "token_renovacion": "rt_a044f2a7bec4ef41b2d75c00cb9f44a5"
}
```

**Respuesta.** HTTP 401 (esperado 401) · 6 ms · traza `c520b43b-c547-4535-86e9-cdc74620a76b`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.",
    "traza_id": "c520b43b-c547-4535-86e9-cdc74620a76b"
  }
}
```

### AUTH-10 · Cerrar sesión · PASA

**Objetivo.** Revocar el acceso del encabezado y la renovación del cuerpo.

**Petición.** `POST http://auth:5101/api/v1/auth/salir`

```http
Accept: application/json
X-Traza-Id: 939a319b-e4df-47c2-91ca-5729559bf3cf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "token_renovacion": "rt_e936bd994e785a0acb797aff9140f148"
}
```

**Respuesta.** HTTP 204 (esperado 204) · 28 ms · traza `939a319b-e4df-47c2-91ca-5729559bf3cf`

```json
(sin cuerpo)
```

**Explicación.** El jti se agrega a la lista de revocados con TTL igual a su vida restante y sale del conjunto de sesión.

**Evidencia en Redis.** `TTL auth:jti:revocado:d29fdcb3aa6f43458192546b0b10d404; SISMEMBER auth:sesion:7 d29fdcb3aa6f43458192546b0b10d404`

```json
[
  {
    "comando": "TTL auth:jti:revocado:d29fdcb3aa6f43458192546b0b10d404",
    "valor": 899
  },
  {
    "comando": "SISMEMBER auth:sesion:7 d29fdcb3aa6f43458192546b0b10d404",
    "valor": 0
  }
]
```

## Servicio usuarios · puerto 5102

### AUTH-11 · Usar un token revocado · PASA

**Objetivo.** Una sesión cerrada ya no entra a ningún servicio.

**Petición.** `GET http://usuarios:5102/api/v1/usuarios/yo`

```http
Accept: application/json
X-Traza-Id: d105d50a-4cd5-4c51-8837-6887431821e9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 401 (esperado 401) · 8 ms · traza `d105d50a-4cd5-4c51-8837-6887431821e9`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.",
    "traza_id": "d105d50a-4cd5-4c51-8837-6887431821e9"
  }
}
```

**Explicación.** El servicio de usuarios consulta auth:jti:revocado en Redis: la revocación es común a todos.

### USR-01 · Mi perfil (JSON) · PASA

**Objetivo.** Consultar el perfil de quien inició sesión.

**Petición.** `GET http://usuarios:5102/api/v1/usuarios/yo`

```http
Accept: application/json
X-Traza-Id: 298a67b8-6f2b-423a-ad9c-77a8a32a9319
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 29 ms · traza `298a67b8-6f2b-423a-ad9c-77a8a32a9319`

```json
{
  "id": 7,
  "nombre": "Ramiro",
  "apellidos": "Alanís Lozano",
  "correo": "repartidor1@codex.mx",
  "telefono": "8112345678",
  "rol": "repartidor",
  "microhub": null,
  "ultimo_acceso": "2026-11-26T14:19:28-06:00"
}
```

### USR-02 · Mi perfil (XML) · PASA

**Objetivo.** El mismo recurso en XML según Accept.

**Petición.** `GET http://usuarios:5102/api/v1/usuarios/yo`

```http
Accept: application/xml
X-Traza-Id: 8039126f-e75e-447d-8fd5-d8860ead716b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 27 ms · traza `8039126f-e75e-447d-8fd5-d8860ead716b`

```xml
<?xml version='1.0' encoding='utf-8'?>
<usuario xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>5</id><nombre>Vanessa</nombre><apellidos>Morante López</apellidos><correo>planeador@codex.mx</correo><telefono>8178109897</telefono><rol>planeador</rol><microhub xsi:nil="true" /><ultimo_acceso>2026-11-26T14:19:29-06:00</ultimo_acceso></usuario>
```

### USR-03 · Actualizar mi teléfono (PATCH) · PASA

**Objetivo.** Modificar un dato del perfil.

**Petición.** `PATCH http://usuarios:5102/api/v1/usuarios/yo`

```http
Accept: application/json
X-Traza-Id: 069a6078-efaa-4a6d-a77f-5bed0d4d73ea
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "telefono": "8112345678"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 64 ms · traza `069a6078-efaa-4a6d-a77f-5bed0d4d73ea`

```json
{
  "id": 7,
  "nombre": "Ramiro",
  "apellidos": "Alanís Lozano",
  "correo": "repartidor1@codex.mx",
  "telefono": "8112345678",
  "rol": "repartidor",
  "microhub": null,
  "ultimo_acceso": "2026-11-26T14:19:28-06:00"
}
```

**Explicación.** El trigger de auditoría registra el cambio con el usuario que actuó.

**Evidencia en PostgreSQL.** `SELECT id, telefono, actualizado_en FROM usuario WHERE id = 7`

```json
[
  {
    "id": 7,
    "telefono": "8112345678",
    "actualizado_en": "2026-11-26 14:19:29.824418-06:00"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT fecha, accion, entidad, detalle FROM auditoria WHERE entidad = 'usuario' AND entidad_id = '7' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "fecha": "2026-11-26 14:19:29.824418-06:00",
    "accion": "modificacion",
    "entidad": "usuario",
    "detalle": null
  }
]
```

### USR-04 · Teléfono inválido · PASA

**Objetivo.** Validación de patrón (10 dígitos).

**Petición.** `PATCH http://usuarios:5102/api/v1/usuarios/yo`

```http
Accept: application/json
X-Traza-Id: 78dc60ac-804b-4e0a-94d2-6c5e933aa9dd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "telefono": "12ab"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 28 ms · traza `78dc60ac-804b-4e0a-94d2-6c5e933aa9dd`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "telefono",
        "mensaje": "Debe tener 10 dígitos."
      }
    ],
    "traza_id": "78dc60ac-804b-4e0a-94d2-6c5e933aa9dd"
  }
}
```

### USR-05 · Lista de usuarios (administrador) · PASA

**Objetivo.** Búsqueda y paginación.

**Petición.** `GET http://usuarios:5102/api/v1/usuarios?q=codex&rol=operador&pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 28222dcb-d5b6-4463-9f58-62411a9854f6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 56 ms · traza `28222dcb-d5b6-4463-9f58-62411a9854f6`

```json
{
  "datos": [
    {
      "id": 2,
      "nombre": "Ruth Elizabeth",
      "apellidos": "Soriano",
      "correo": "operador.mh01@codex.mx",
      "telefono": "8144383556",
      "rol": "operador",
      "microhub": {
        "id": 1,
        "clave": "********",
        "nombre": "Microhub San Bernabé Centro"
      },
      "ultimo_acceso": "2026-11-26T14:09:14-06:00"
    },
    {
      "id": 3,
      "nombre": "María José",
      "apellidos": "Cedillo Mata",
      "correo": "operador.mh02@codex.mx",
      "telefono": "8120362394",
      "rol": "operador",
      "microhub": {
        "id": 2,
        "clave": "********",
        "nombre": "Microhub Valles"
      },
      "ultimo_acceso": "2026-11-26T14:05:01-06:00"
    },
    {
      "id": 4,
      "nombre": "Jorge Antonio",
      "apellidos": "Arreola Cantu",
      "correo": "operador.mh03@codex.mx",
      "telefono": "8153988349",
      "rol": "operador",
      "microhub": {
        "id": 3,
        "clave": "********",
        "nombre": "Microhub Poniente F-113"
      },
      "ultimo_acceso": "2026-11-26T13:53:32-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 3,
    "paginas": 1
  }
}
```

### USR-06 · Lista de usuarios sin permiso · PASA

**Objetivo.** Un repartidor no tiene usuarios.ver.

**Petición.** `GET http://usuarios:5102/api/v1/usuarios`

```http
Accept: application/json
X-Traza-Id: b5fe6a25-a34b-4ae4-8f28-cd5d3bcefaeb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 62 ms · traza `b5fe6a25-a34b-4ae4-8f28-cd5d3bcefaeb`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "b5fe6a25-a34b-4ae4-8f28-cd5d3bcefaeb"
  }
}
```

**Evidencia en PostgreSQL.** `SELECT fecha, modulo, accion, detalle, exitoso FROM auditoria WHERE accion = 'acceso_denegado' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "fecha": "2026-11-26 14:19:30.052081-06:00",
    "modulo": "usuarios",
    "accion": "acceso_denegado",
    "detalle": "GET /api/v1/usuarios sin usuarios.ver",
    "exitoso": false
  }
]
```

### USR-07 · Usuario inexistente · PASA

**Objetivo.** Registro que no existe.

**Petición.** `GET http://usuarios:5102/api/v1/usuarios/999999`

```http
Accept: application/json
X-Traza-Id: bb75f902-d94a-42fe-ad3f-47ed23da1264
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 28 ms · traza `bb75f902-d94a-42fe-ad3f-47ed23da1264`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "bb75f902-d94a-42fe-ad3f-47ed23da1264"
  }
}
```

## Servicio productos · puerto 5103

### PRO-01 · Productos con búsqueda (caché vacía) · PASA

**Objetivo.** Consultar productos; la respuesta se guarda en Redis.

**Petición.** `GET http://productos:5103/api/v1/productos?q=arroz&pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: f36db00c-bcf6-4dc3-be23-cf1763c4d9ee
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 75 ms · traza `f36db00c-bcf6-4dc3-be23-cf1763c4d9ee`

```json
{
  "datos": [
    {
      "id": 2,
      "clave_interna": "AB-002",
      "nombre": "Arroz superextra",
      "categoria": {
        "id": 1,
        "nombre": "Abarrote básico"
      },
      "unidad": "kg",
      "presentacion": "1 kg",
      "precio": 29.9,
      "imagen_url": null,
      "estatus": "activo"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 1,
    "paginas": 1
  }
}
```

**Explicación.** Encabezado X-Cache: MISS. La llave cache:catalogo:productos:* expira según cache_catalogo_segundos.

**Evidencia en Redis.** `db1 TTL cache:catalogo:productos:04d4a6a9d27021cf`

```json
[
  {
    "comando": "db1 TTL cache:catalogo:productos:04d4a6a9d27021cf",
    "valor": 300
  }
]
```

### PRO-02 · Misma consulta (desde Redis) · PASA

**Objetivo.** La segunda consulta no toca PostgreSQL.

**Petición.** `GET http://productos:5103/api/v1/productos?q=arroz&pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 6fcc120b-f097-42fc-8ea2-cc65a983f8f0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 7 ms · traza `6fcc120b-f097-42fc-8ea2-cc65a983f8f0`

```json
{
  "datos": [
    {
      "id": 2,
      "clave_interna": "AB-002",
      "nombre": "Arroz superextra",
      "categoria": {
        "id": 1,
        "nombre": "Abarrote básico"
      },
      "unidad": "kg",
      "presentacion": "1 kg",
      "precio": 29.9,
      "imagen_url": null,
      "estatus": "activo"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 1,
    "paginas": 1
  }
}
```

### PRO-03 · Productos (XML) · PASA

**Objetivo.** Lista en XML válida contra catalogos.xsd.

**Petición.** `GET http://productos:5103/api/v1/productos?pagina=1&por_pagina=2`

```http
Accept: application/xml
X-Traza-Id: 0813aaae-61a1-4b00-a32a-de94957423fd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 89 ms · traza `0813aaae-61a1-4b00-a32a-de94957423fd`

```xml
<?xml version='1.0' encoding='utf-8'?>
<productos xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><datos><producto><id>3</id><clave_interna>AB-003</clave_interna><nombre>Aceite vegetal</nombre><categoria><id>1</id><nombre>Abarrote básico</nombre></categoria><unidad>botella</unidad><presentacion>900 ml</presentacion><precio>42.00</precio><imagen_url xsi:nil="true" /><estatus>activo</estatus></producto><producto><id>2</id><clave_interna>AB-002</clave_interna><nombre>Arroz superextra</nombre><categoria><id>1</id><nombre>Abarrote básico</nombre></categoria><unidad>kg</unidad><presentacion>1 kg</presentacion><precio>29.90</precio><imagen_url xsi:nil="true" /><estatus>activo</estatus></producto></datos><paginacion><pagina>1</pagina><por_pagina>2</por_pagina><total>51</total><paginas>26</paginas></paginacion></productos>
```

### PRO-04 · Un producto · PASA

**Objetivo.** Detalle por id.

**Petición.** `GET http://productos:5103/api/v1/productos/3`

```http
Accept: application/json
X-Traza-Id: 2eb68985-070a-430d-9e24-3e87a8f3c34a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 51 ms · traza `2eb68985-070a-430d-9e24-3e87a8f3c34a`

```json
{
  "id": 3,
  "clave_interna": "AB-003",
  "nombre": "Aceite vegetal",
  "categoria": {
    "id": 1,
    "nombre": "Abarrote básico"
  },
  "unidad": "botella",
  "presentacion": "900 ml",
  "precio": 42.0,
  "imagen_url": null,
  "estatus": "activo"
}
```

### PRO-05 · Producto inexistente · PASA

**Objetivo.** Registro que no existe.

**Petición.** `GET http://productos:5103/api/v1/productos/999999`

```http
Accept: application/json
X-Traza-Id: fcc6b17e-f201-4345-851a-3e05697ad235
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 52 ms · traza `fcc6b17e-f201-4345-851a-3e05697ad235`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "fcc6b17e-f201-4345-851a-3e05697ad235"
  }
}
```

### PRO-06 · Paginación fuera de rango · PASA

**Objetivo.** por_pagina máximo 100.

**Petición.** `GET http://productos:5103/api/v1/productos?por_pagina=500`

```http
Accept: application/json
X-Traza-Id: 7b0f058f-9c0e-4757-8214-8790430e9de2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 5 ms · traza `7b0f058f-9c0e-4757-8214-8790430e9de2`

```json
{
  "error": {
    "codigo": "FILTRO_INVALIDO",
    "mensaje": "por_pagina debe estar entre 1 y 100.",
    "detalles": [
      {
        "campo": "por_pagina",
        "mensaje": "por_pagina debe estar entre 1 y 100."
      }
    ],
    "traza_id": "7b0f058f-9c0e-4757-8214-8790430e9de2"
  }
}
```

### PRO-07 · Sin token · PASA

**Objetivo.** Todo endpoint protegido exige Authorization: Bearer.

**Petición.** `GET http://productos:5103/api/v1/productos`

```http
Accept: application/json
X-Traza-Id: 425dad03-1e5e-4fc7-9f7b-a9e6acedacf8
```

**Respuesta.** HTTP 401 (esperado 401) · 4 ms · traza `425dad03-1e5e-4fc7-9f7b-a9e6acedacf8`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "Falta el encabezado Authorization: Bearer <token>.",
    "traza_id": "425dad03-1e5e-4fc7-9f7b-a9e6acedacf8"
  }
}
```

## Servicio zonas · puerto 5108

### ZON-01 · Zonas (XML) · PASA

**Objetivo.** Colonias atendidas con centroide, válidas contra catalogos.xsd.

**Petición.** `GET http://zonas:5108/api/v1/zonas`

```http
Accept: application/xml
X-Traza-Id: f34fa8a1-ba40-49f4-8b3a-99b653a64ddc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 66 ms · traza `f34fa8a1-ba40-49f4-8b3a-99b653a64ddc`

```xml
<?xml version='1.0' encoding='utf-8'?>
<zonas xmlns="urn:microhubs:v1" version="1"><datos><zona><id>1</id><clave>ZN-SB01</clave><nombre>San Bernabé Centro</nombre><colonia>San Bernabé</colonia><codigo_postal>64100</codigo_postal><latitud>25.7455</latitud><longitud>-100.3585</longitud></zona><zona><id>2</id><clave>ZN-SB02</clave><nombre>Valles de San Bernabé</nombre><colonia>Valles de San Bernabé</colonia><codigo_postal>64103</codigo_postal><latitud>25.753</latitud><longitud>-100.369</longitud></zona><zona><id>3</id><clave>ZN-SB03</clave><nombre>Paseo de San Bernabé</nombre><colonia>Paseo de San Bernabé</colonia><codigo_postal>64103</codigo_postal><latitud>25.758</latitud><longitud>-100.3745</longitud></zona><zona><id>4</id><clave>ZN-SB04</clave><nombre>San Bernabé X (F-113)</nombre><colonia>San Bernabé X (F-113)</colonia><codigo_postal>64105</codigo_postal><latitud>25.7495</latitud><longitud>-100.38</longitud></zona></datos><paginacion><pagina>1</pagina><por_pagina>20</por_pagina><total>4</total><paginas>1</paginas></paginacion></zonas>
```

### ZON-02 · Una zona · PASA

**Objetivo.** Detalle por id.

**Petición.** `GET http://zonas:5108/api/v1/zonas/1`

```http
Accept: application/json
X-Traza-Id: aec0dcb3-4300-4e10-af21-49a6788a8d4a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 22 ms · traza `aec0dcb3-4300-4e10-af21-49a6788a8d4a`

```json
{
  "id": 1,
  "clave": "********",
  "nombre": "San Bernabé Centro",
  "colonia": "San Bernabé",
  "codigo_postal": "64100",
  "latitud": 25.7455,
  "longitud": -100.3585
}
```

### ZON-03 · Zona inexistente · PASA

**Objetivo.** Registro que no existe.

**Petición.** `GET http://zonas:5108/api/v1/zonas/999999`

```http
Accept: application/json
X-Traza-Id: 1df169ce-d184-433b-90ea-38790a2359dc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 23 ms · traza `1df169ce-d184-433b-90ea-38790a2359dc`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "1df169ce-d184-433b-90ea-38790a2359dc"
  }
}
```

### ZON-04 · Sin token · PASA

**Objetivo.** Todo endpoint protegido exige Authorization: Bearer.

**Petición.** `GET http://zonas:5108/api/v1/zonas`

```http
Accept: application/json
X-Traza-Id: 58b2dab3-3a93-42dd-b1fb-e4f4f09fd6d4
```

**Respuesta.** HTTP 401 (esperado 401) · 4 ms · traza `58b2dab3-3a93-42dd-b1fb-e4f4f09fd6d4`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "Falta el encabezado Authorization: Bearer <token>.",
    "traza_id": "58b2dab3-3a93-42dd-b1fb-e4f4f09fd6d4"
  }
}
```

## Servicio microhubs · puerto 5109

### MIC-01 · Microhubs activos · PASA

**Objetivo.** Microhubs con coordenadas y radio.

**Petición.** `GET http://microhubs:5109/api/v1/microhubs?estatus=activo`

```http
Accept: application/json
X-Traza-Id: 440d33dd-d6b1-4c26-9b9d-e4a34ebd5360
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 78 ms · traza `440d33dd-d6b1-4c26-9b9d-e4a34ebd5360`

```json
{
  "datos": [
    {
      "id": 1,
      "clave": "********",
      "nombre": "Microhub San Bernabé Centro",
      "latitud": 25.748,
      "longitud": -100.364,
      "radio_km": 1.5,
      "estatus": "activo"
    },
    {
      "id": 2,
      "clave": "********",
      "nombre": "Microhub Valles",
      "latitud": 25.7555,
      "longitud": -100.372,
      "radio_km": 1.5,
      "estatus": "activo"
    },
    {
      "id": 3,
      "clave": "********",
      "nombre": "Microhub Poniente F-113",
      "latitud": 25.75,
      "longitud": -100.381,
      "radio_km": 1.2,
      "estatus": "activo"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 3,
    "paginas": 1
  }
}
```

### MIC-02 · Microhub inexistente · PASA

**Objetivo.** Registro que no existe.

**Petición.** `GET http://microhubs:5109/api/v1/microhubs/999999`

```http
Accept: application/json
X-Traza-Id: 643341ae-04cf-4b96-82f2-3edb742c96f3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 30 ms · traza `643341ae-04cf-4b96-82f2-3edb742c96f3`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "643341ae-04cf-4b96-82f2-3edb742c96f3"
  }
}
```

### MIC-03 · Sin token · PASA

**Objetivo.** Todo endpoint protegido exige Authorization: Bearer.

**Petición.** `GET http://microhubs:5109/api/v1/microhubs`

```http
Accept: application/json
X-Traza-Id: 3f84285e-8484-48e5-b9fd-3b5a34304da6
```

**Respuesta.** HTTP 401 (esperado 401) · 4 ms · traza `3f84285e-8484-48e5-b9fd-3b5a34304da6`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "Falta el encabezado Authorization: Bearer <token>.",
    "traza_id": "3f84285e-8484-48e5-b9fd-3b5a34304da6"
  }
}
```

## Servicio pedidos · puerto 5104

### PED-01 · Pedidos entregados (JSON) · PASA

**Objetivo.** Lista filtrada por estado y fechas.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos?estado=entregado&pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 6ad8895c-b09d-4add-a2da-9668aa325bcc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 69 ms · traza `6ad8895c-b09d-4add-a2da-9668aa325bcc`

```json
{
  "datos": [
    {
      "id": 534,
      "folio": "PED-20261126-000534",
      "estado": "entregado",
      "zona": {
        "id": 3,
        "nombre": "Paseo de San Bernabé"
      },
      "microhub_id": 2,
      "total": 177.0,
      "creado_en": "2026-11-26T13:53:28-06:00"
    },
    {
      "id": 524,
      "folio": "PED-20261126-000524",
      "estado": "entregado",
      "zona": {
        "id": 1,
        "nombre": "San Bernabé Centro"
      },
      "microhub_id": 1,
      "total": 144.0,
      "creado_en": "2026-11-26T13:51:12-06:00"
    },
    {
      "id": 522,
      "folio": "PED-20261126-000522",
      "estado": "entregado",
      "zona": {
        "id": 1,
        "nombre": "San Bernabé Centro"
      },
      "microhub_id": 1,
      "total": 155.0,
      "creado_en": "2026-11-26T00:39:01-06:00"
    },
    {
      "id": 521,
      "folio": "PED-20261126-000521",
      "estado": "entregado",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "microhub_id": 2,
      "total": 163.0,
      "creado_en": "2026-11-26T00:38:47-06:00"
    },
    {
      "id": 513,
      "folio": "PED-20261126-000513",
      "estado": "entregado",
      "zona": {
        "id": 4,
        "nombre": "San Bernabé X (F-113)"
      },
      "microhub_id": 3,
      "total": 183.0,
      "creado_en": "2026-11-26T00:37:14-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 147,
    "paginas": 30
  }
}
```

### PED-02 · Pedidos (XML) · PASA

**Objetivo.** La misma lista en XML.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos?estado=entregado&por_pagina=2`

```http
Accept: application/xml
X-Traza-Id: 722bdb12-8b2d-456f-be7f-98e3fe12ddfd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 72 ms · traza `722bdb12-8b2d-456f-be7f-98e3fe12ddfd`

```xml
<?xml version='1.0' encoding='utf-8'?>
<pedidos xmlns="urn:microhubs:v1" version="1"><datos><pedido><id>534</id><folio>PED-20261126-000534</folio><estado>entregado</estado><zona><id>3</id><nombre>Paseo de San Bernabé</nombre></zona><microhub_id>2</microhub_id><total>177.00</total><creado_en>2026-11-26T13:53:28-06:00</creado_en></pedido><pedido><id>524</id><folio>PED-20261126-000524</folio><estado>entregado</estado><zona><id>1</id><nombre>San Bernabé Centro</nombre></zona><microhub_id>1</microhub_id><total>144.00</total><creado_en>2026-11-26T13:51:12-06:00</creado_en></pedido></datos><paginacion><pagina>1</pagina><por_pagina>2</por_pagina><total>147</total><paginas>74</paginas></paginacion></pedidos>
```

### PED-03 · Detalle con líneas · PASA

**Objetivo.** Cliente, domicilio y líneas del pedido.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/534`

```http
Accept: application/json
X-Traza-Id: a0e38a86-4181-483b-8341-f5855ccf04b5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 84 ms · traza `a0e38a86-4181-483b-8341-f5855ccf04b5`

```json
{
  "id": 534,
  "folio": "PED-20261126-000534",
  "estado": "entregado",
  "cliente": {
    "nombre": "Juan Chapa Sepúlveda",
    "telefono": "8177163004"
  },
  "domicilio": {
    "calle": "Paseo del Valle",
    "numero_ext": "1762",
    "colonia": "Paseo de San Bernabé",
    "latitud": 25.758514,
    "longitud": -100.373251
  },
  "zona": {
    "id": 3,
    "nombre": "Paseo de San Bernabé"
  },
  "microhub_id": 2,
  "subtotal": 159.0,
  "costo_envio": 18.0,
  "total": 177.0,
  "creado_en": "2026-11-26T13:53:28-06:00",
  "lineas": [
    {
      "id": 1427,
      "producto_id": 9,
      "nombre": "Atún en agua",
      "cantidad": 3,
      "precio_unitario": 21.0,
      "importe": 63.0
    },
    {
      "id": 1428,
      "producto_id": 48,
      "nombre": "Pasta dental",
      "cantidad": 3,
      "precio_unitario": 32.0,
      "importe": 96.0
    }
  ]
}
```

### PED-04 · Historial de estados · PASA

**Objetivo.** Cambios de estado con usuario y fecha.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/534/historial`

```http
Accept: application/json
X-Traza-Id: 0b02e753-9494-4f25-88cc-9032201ec6b9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 62 ms · traza `0b02e753-9494-4f25-88cc-9032201ec6b9`

```json
{
  "pedido_id": 534,
  "eventos": [
    {
      "estado_anterior": null,
      "estado_nuevo": "creado",
      "usuario": null,
      "motivo": null,
      "fecha": "2026-11-26T13:53:28-06:00"
    },
    {
      "estado_anterior": "creado",
      "estado_nuevo": "asignado",
      "usuario": null,
      "motivo": null,
      "fecha": "2026-11-26T13:53:28-06:00"
    },
    {
      "estado_anterior": "asignado",
      "estado_nuevo": "en_preparacion",
      "usuario": "operador.mh02@codex.mx",
      "motivo": null,
      "fecha": "2026-11-26T13:53:28-06:00"
    },
    {
      "estado_anterior": "en_preparacion",
      "estado_nuevo": "en_ruta",
      "usuario": "operador.mh02@codex.mx",
      "motivo": null,
      "fecha": "2026-11-26T13:53:28-06:00"
    },
    {
      "estado_anterior": "en_ruta",
      "estado_nuevo": "entregado",
      "usuario": "repartidor1@codex.mx",
      "motivo": null,
      "fecha": "2026-11-26T13:54:47-06:00"
    }
  ]
}
```

**Evidencia en PostgreSQL.** `SELECT fecha, estado_anterior, estado_nuevo, usuario_id FROM historial_estatus WHERE pedido_id = %s ORDER BY fecha, id`

```json
[
  {
    "fecha": "2026-11-26 13:53:28.684399-06:00",
    "estado_anterior": null,
    "estado_nuevo": "creado",
    "usuario_id": null
  },
  {
    "fecha": "2026-11-26 13:53:28.684399-06:00",
    "estado_anterior": "creado",
    "estado_nuevo": "asignado",
    "usuario_id": null
  },
  {
    "fecha": "2026-11-26 13:53:28.684399-06:00",
    "estado_anterior": "asignado",
    "estado_nuevo": "en_preparacion",
    "usuario_id": 3
  },
  {
    "fecha": "2026-11-26 13:53:28.684399-06:00",
    "estado_anterior": "en_preparacion",
    "estado_nuevo": "en_ruta",
    "usuario_id": 3
  },
  {
    "fecha": "2026-11-26 13:54:47.483102-06:00",
    "estado_anterior": "en_ruta",
    "estado_nuevo": "entregado",
    "usuario_id": 7
  }
]
```

### PED-05 · Filtro inválido · PASA

**Objetivo.** Un estado que no existe se rechaza.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos?estado=inventado`

```http
Accept: application/json
X-Traza-Id: 781be3ac-56f8-493a-832b-3666acdde5b8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 8 ms · traza `781be3ac-56f8-493a-832b-3666acdde5b8`

```json
{
  "error": {
    "codigo": "FILTRO_INVALIDO",
    "mensaje": "Valor no permitido para estado: inventado.",
    "detalles": [
      {
        "campo": "estado",
        "mensaje": "Valor no permitido para estado: inventado."
      }
    ],
    "traza_id": "781be3ac-56f8-493a-832b-3666acdde5b8"
  }
}
```

### PED-06 · Pedido fuera del ámbito · PASA

**Objetivo.** El operador del MH-01 no ve pedidos de otro microhub (RN22).

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/1`

```http
Accept: application/json
X-Traza-Id: 5b41faeb-a726-4eb7-9a17-519164fc81a4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 36 ms · traza `5b41faeb-a726-4eb7-9a17-519164fc81a4`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el pedido o no está en tu ámbito.",
    "traza_id": "5b41faeb-a726-4eb7-9a17-519164fc81a4"
  }
}
```

**Explicación.** El ámbito lo decide PostgreSQL con fn_pedidos_visibles; el servicio no lo puede saltar.

### PED-07 · Cerrar desde pedidos · PASA

**Objetivo.** Los cierres de entrega solo se registran en el servicio de entregas.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/534/estado`

```http
Accept: application/json
X-Traza-Id: 256652ed-69e6-46c0-bf3d-14634115b931
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "estado": "entregado"
}
```

**Respuesta.** HTTP 409 (esperado 409) · 19 ms · traza `256652ed-69e6-46c0-bf3d-14634115b931`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "El cierre de una entrega se registra con POST /api/v1/entregas/{id}/resultado.",
    "traza_id": "256652ed-69e6-46c0-bf3d-14634115b931"
  }
}
```

### PED-08 · Transición ilegal (regla del motor) · PASA

**Objetivo.** Un pedido entregado no puede regresar a preparación.

**Petición.** `PATCH http://pedidos:5104/api/v1/pedidos/2/estado`

```http
Accept: application/json
X-Traza-Id: 01adf3fe-0fa3-4f50-af04-a1410e4ae421
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0Iiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "estado": "en_preparacion"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 65 ms · traza `01adf3fe-0fa3-4f50-af04-a1410e4ae421`

```json
{
  "error": {
    "codigo": "REGLA_NEGOCIO",
    "mensaje": "RN20: transición ilegal entregado -> en_preparacion para el rol operador. El pedido PED-20261020-000002 conserva su estado.",
    "traza_id": "01adf3fe-0fa3-4f50-af04-a1410e4ae421"
  }
}
```

**Explicación.** El trigger fn_valida_transicion de PostgreSQL rechaza la transición (RN20); el estado no cambia.

**Evidencia en PostgreSQL.** `SELECT id, folio, estado FROM pedido WHERE id = %s`

```json
[
  {
    "id": 2,
    "folio": "PED-20261020-000002",
    "estado": "entregado"
  }
]
```

## Servicio documentos · puerto 5107

### DOC-01 · Subir evidencia de entrega · PASA

**Objetivo.** Guardar la foto en MongoDB ligada a la entrega.

**Petición.** `POST http://documentos:5107/api/v1/documentos`

```http
Accept: application/json
X-Traza-Id: 7a7cc0f3-fe40-4a1b-8a7c-89d3500a31f5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "evidencia-entrega-277.jpg",
  "tipo_mime": "image/jpeg",
  "contenido_base64": "/9j/4AAQSkZJRgABAQAAAQABAAAAAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcY…(368 caracteres)",
  "referencia": {
    "tipo": "entrega",
    "id": "277"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 57 ms · traza `7a7cc0f3-fe40-4a1b-8a7c-89d3500a31f5`

```json
{
  "id": "6b089453cc73360fa2e7f17a",
  "nombre": "evidencia-entrega-277.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "277"
  },
  "subido_por": 7,
  "creado_en": "2026-11-26T14:19:31-06:00",
  "ruta": "documentos/2026/11/6b089453cc73360fa2e7f17a.jpg",
  "privacidad": "privado",
  "estado": "activo",
  "metadatos": {
    "almacen": "local",
    "origen": "api"
  }
}
```

**Explicación.** Se valida que el contenido sea JPEG real, se calcula su SHA-256 y que la entrega sea del repartidor.

**Evidencia en MongoDB.** `db.documentos.findOne({_id: ObjectId('6b089453cc73360fa2e7f17a')}, {contenido: 0})`

```json
{
  "_id": "6b089453cc73360fa2e7f17a",
  "nombre": "evidencia-entrega-277.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "277"
  },
  "subido_por": 7,
  "creado_en": "2026-11-26 20:19:31.753000+00:00",
  "ruta": "documentos/2026/11/6b089453cc73360fa2e7f17a.jpg",
  "privacidad": "privado",
  "estado": "activo",
  "metadatos": {
    "almacen": "local",
    "origen": "api"
  }
}
```

### DOC-02 · Subir evidencia de la segunda entrega · PASA

**Objetivo.** Evidencia para el cierre parcial.

**Petición.** `POST http://documentos:5107/api/v1/documentos`

```http
Accept: application/json
X-Traza-Id: a32e31b1-bbe3-45e6-ac89-0880ec7c19a9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "evidencia-entrega-278.jpg",
  "tipo_mime": "image/jpeg",
  "contenido_base64": "/9j/4AAQSkZJRgABAQAAAQABAAAAAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcY…(368 caracteres)",
  "referencia": {
    "tipo": "entrega",
    "id": "278"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 49 ms · traza `a32e31b1-bbe3-45e6-ac89-0880ec7c19a9`

```json
{
  "id": "6b089454cc73360fa2e7f17d",
  "nombre": "evidencia-entrega-278.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "278"
  },
  "subido_por": 7,
  "creado_en": "2026-11-26T14:19:32-06:00",
  "ruta": "documentos/2026/11/6b089454cc73360fa2e7f17d.jpg",
  "privacidad": "privado",
  "estado": "activo",
  "metadatos": {
    "almacen": "local",
    "origen": "api"
  }
}
```

### DOC-03 · Tipo de archivo falso · PASA

**Objetivo.** Un PDF declarado como JPEG se rechaza por su firma.

**Petición.** `POST http://documentos:5107/api/v1/documentos`

```http
Accept: application/json
X-Traza-Id: f1850994-5e34-40c7-a3b3-c3533e80f110
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "foto.jpg",
  "tipo_mime": "image/jpeg",
  "contenido_base64": "JVBERi0xLjQgZmFsc28=",
  "referencia": {
    "tipo": "entrega",
    "id": "277"
  }
}
```

**Respuesta.** HTTP 422 (esperado 422) · 14 ms · traza `f1850994-5e34-40c7-a3b3-c3533e80f110`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "tipo_mime",
        "mensaje": "El contenido no corresponde al tipo declarado."
      }
    ],
    "traza_id": "f1850994-5e34-40c7-a3b3-c3533e80f110"
  }
}
```

### DOC-04 · Evidencia en entrega ajena · PASA

**Objetivo.** Un repartidor no adjunta a entregas de otro.

**Petición.** `POST http://documentos:5107/api/v1/documentos`

```http
Accept: application/json
X-Traza-Id: 7734d695-f88e-4dc3-a5b0-ea68eaee7cf7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4Iiwi…(296 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "x.jpg",
  "tipo_mime": "image/jpeg",
  "contenido_base64": "/9j/4AAQSkZJRgABAQAAAQABAAAAAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcY…(368 caracteres)",
  "referencia": {
    "tipo": "entrega",
    "id": "277"
  }
}
```

**Respuesta.** HTTP 403 (esperado 403) · 28 ms · traza `7734d695-f88e-4dc3-a5b0-ea68eaee7cf7`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Solo puedes adjuntar evidencia a tus entregas.",
    "traza_id": "7734d695-f88e-4dc3-a5b0-ea68eaee7cf7"
  }
}
```

### DOC-05 · Documento temporal · PASA

**Objetivo.** Documento que después se elimina.

**Petición.** `POST http://documentos:5107/api/v1/documentos`

```http
Accept: application/json
X-Traza-Id: 0d7c4da9-6b19-43db-912f-420ddce1003a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "borrador.jpg",
  "tipo_mime": "image/jpeg",
  "contenido_base64": "/9j/4AAQSkZJRgABAQAAAQABAAAAAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcY…(368 caracteres)",
  "referencia": {
    "tipo": "usuario",
    "id": "7"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 29 ms · traza `0d7c4da9-6b19-43db-912f-420ddce1003a`

```json
{
  "id": "6b089454cc73360fa2e7f184",
  "nombre": "borrador.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "usuario",
    "id": "7"
  },
  "subido_por": 7,
  "creado_en": "2026-11-26T14:19:32-06:00",
  "ruta": "documentos/2026/11/6b089454cc73360fa2e7f184.jpg",
  "privacidad": "privado",
  "estado": "activo",
  "metadatos": {
    "almacen": "local",
    "origen": "api"
  }
}
```

### DOC-06 · Mis documentos · PASA

**Objetivo.** Filtro por referencia.

**Petición.** `GET http://documentos:5107/api/v1/documentos?referencia_tipo=entrega&referencia_id=277`

```http
Accept: application/json
X-Traza-Id: 683cb37d-ae06-4b11-a0fc-842991113150
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 14 ms · traza `683cb37d-ae06-4b11-a0fc-842991113150`

```json
{
  "datos": [
    {
      "id": "6b089453cc73360fa2e7f17a",
      "nombre": "evidencia-entrega-277.jpg",
      "tipo_mime": "image/jpeg",
      "tamano_bytes": 276,
      "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
      "referencia": {
        "tipo": "entrega",
        "id": "277"
      },
      "subido_por": 7,
      "creado_en": "2026-11-26T14:19:31-06:00",
      "ruta": "documentos/2026/11/6b089453cc73360fa2e7f17a.jpg",
      "privacidad": "privado",
      "estado": "activo",
      "metadatos": {
        "almacen": "local",
        "origen": "api"
      }
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 1,
    "paginas": 1
  }
}
```

### DOC-07 · Metadatos (XML) · PASA

**Objetivo.** Documento en XML, sin contenido.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b089453cc73360fa2e7f17a`

```http
Accept: application/xml
X-Traza-Id: adfba13c-fa7a-4884-b0d2-f391d996da8f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `adfba13c-fa7a-4884-b0d2-f391d996da8f`

```xml
<?xml version='1.0' encoding='utf-8'?>
<documento xmlns="urn:microhubs:v1" version="1"><id>6b089453cc73360fa2e7f17a</id><nombre>evidencia-entrega-277.jpg</nombre><tipo_mime>image/jpeg</tipo_mime><tamano_bytes>276</tamano_bytes><sha256>7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc</sha256><referencia><tipo>entrega</tipo><id>277</id></referencia><subido_por>7</subido_por><creado_en>2026-11-26T14:19:31-06:00</creado_en><ruta>documentos/2026/11/6b089453cc73360fa2e7f17a.jpg</ruta><privacidad>privado</privacidad><estado>activo</estado><metadatos><almacen>local</almacen><origen>api</origen></metadatos></documento>
```

### DOC-08 · Contenido en Base64 · PASA

**Objetivo.** Recuperar el archivo.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b089453cc73360fa2e7f17a/contenido`

```http
Accept: application/json
X-Traza-Id: 0ad99796-5847-4184-bbc9-64d56484cf49
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 8 ms · traza `0ad99796-5847-4184-bbc9-64d56484cf49`

```json
{
  "id": "6b089453cc73360fa2e7f17a",
  "nombre": "evidencia-entrega-277.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "277"
  },
  "subido_por": 7,
  "creado_en": "2026-11-26T14:19:31-06:00",
  "ruta": "documentos/2026/11/6b089453cc73360fa2e7f17a.jpg",
  "privacidad": "privado",
  "estado": "activo",
  "metadatos": {
    "almacen": "local",
    "origen": "api"
  },
  "contenido_base64": "/9j/4AAQSkZJRgABAQAAAQABAAAAAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcY…(368 caracteres)"
}
```

### DOC-09 · Eliminar documento (DELETE) · PASA

**Objetivo.** Borrar un documento propio.

**Petición.** `DELETE http://documentos:5107/api/v1/documentos/6b089454cc73360fa2e7f184`

```http
Accept: application/json
X-Traza-Id: 6f78fdd6-03d5-4236-ad37-e13f704d2361
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 48 ms · traza `6f78fdd6-03d5-4236-ad37-e13f704d2361`

```json
(sin cuerpo)
```

**Evidencia en MongoDB.** `db.documentos.countDocuments({_id: ObjectId('6b089454cc73360fa2e7f184')})`

```json
1
```

### DOC-10 · Id inexistente · PASA

**Objetivo.** Registro que no existe.

**Petición.** `GET http://documentos:5107/api/v1/documentos/ffffffffffffffffffffffff`

```http
Accept: application/json
X-Traza-Id: b1144f6a-9b9d-4b37-9ebc-8fac96c22510
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 7 ms · traza `b1144f6a-9b9d-4b37-9ebc-8fac96c22510`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "b1144f6a-9b9d-4b37-9ebc-8fac96c22510"
  }
}
```

## Servicio seguimiento · puerto 5110

### SEG-01 · Enviar puntos GPS · PASA

**Objetivo.** Guardar el recorrido del repartidor en MongoDB.

**Petición.** `POST http://seguimiento:5110/api/v1/seguimiento/277/ubicaciones`

```http
Accept: application/json
X-Traza-Id: 8c5165f7-6ebb-4eba-8dd8-b36f8c6e5abd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "puntos": [
    {
      "latitud": 25.748,
      "longitud": -100.36,
      "precision_m": 9.0,
      "capturado_en": "2026-11-26T20:13:32+00:00"
    },
    {
      "latitud": 25.7486,
      "longitud": -100.3606,
      "precision_m": 8.0,
      "capturado_en": "2026-11-26T20:15:32+00:00"
    },
    {
      "latitud": 25.7491,
      "longitud": -100.3611,
      "precision_m": 8.5,
      "capturado_en": "2026-11-26T20:17:32+00:00"
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 33 ms · traza `8c5165f7-6ebb-4eba-8dd8-b36f8c6e5abd`

```json
{
  "recibidos": 3
}
```

**Evidencia en MongoDB.** `db.ubicaciones_entrega.find({entrega_id: NumberLong(277)}).sort({capturado_en: 1})`

```json
[
  {
    "entrega_id": 277,
    "usuario_id": 7,
    "posicion": {
      "type": "Point",
      "coordinates": [
        -100.36,
        25.748
      ]
    },
    "precision_m": 9.0,
    "capturado_en": "2026-11-26 20:13:32+00:00",
    "recibido_en": "2026-11-26 20:19:32.488000+00:00"
  },
  {
    "entrega_id": 277,
    "usuario_id": 7,
    "posicion": {
      "type": "Point",
      "coordinates": [
        -100.3606,
        25.7486
      ]
    },
    "precision_m": 8.0,
    "capturado_en": "2026-11-26 20:15:32+00:00",
    "recibido_en": "2026-11-26 20:19:32.488000+00:00"
  },
  {
    "entrega_id": 277,
    "usuario_id": 7,
    "posicion": {
      "type": "Point",
      "coordinates": [
        -100.3611,
        25.7491
      ]
    },
    "precision_m": 8.5,
    "capturado_en": "2026-11-26 20:17:32+00:00",
    "recibido_en": "2026-11-26 20:19:32.488000+00:00"
  }
]
```

**Evidencia en MongoDB.** `db.ubicaciones_entrega.getIndexes()`

```json
[
  "_id_",
  "ix_entrega_tiempo",
  "ix_posicion",
  "ix_ttl"
]
```

### SEG-02 · Resumen del recorrido · PASA

**Objetivo.** Agregación en MongoDB sobre los puntos GPS.

**Petición.** `GET http://seguimiento:5110/api/v1/seguimiento/277/recorrido`

```http
Accept: application/json
X-Traza-Id: e1c02e57-6ef3-4fbf-b5ba-c673d4566f6f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 33 ms · traza `e1c02e57-6ef3-4fbf-b5ba-c673d4566f6f`

```json
{
  "entrega_id": 277,
  "puntos": 3,
  "distancia_km": 0.16,
  "inicio": "2026-11-26T14:13:32-06:00",
  "fin": "2026-11-26T14:17:32-06:00",
  "precision_promedio_m": 8.5,
  "ultimo_punto": {
    "latitud": 25.7491,
    "longitud": -100.3611,
    "precision_m": 8.5
  }
}
```

**Explicación.** Pipeline: $match por entrega_id → $sort por capturado_en → $group (conteo, inicio, fin, precisión promedio y ruta). La distancia se calcula con Haversine sobre la ruta.

### SEG-03 · Recorrido de otro repartidor · PASA

**Objetivo.** El repartidor 2 no ve el rastro de la entrega del repartidor 1.

**Petición.** `GET http://seguimiento:5110/api/v1/seguimiento/277/recorrido`

```http
Accept: application/json
X-Traza-Id: 80005aa2-3742-4f12-a0b0-a0cda3c53b0a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4Iiwi…(296 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 29 ms · traza `80005aa2-3742-4f12-a0b0-a0cda3c53b0a`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe la entrega o no está asignada a ti.",
    "traza_id": "80005aa2-3742-4f12-a0b0-a0cda3c53b0a"
  }
}
```

### SEG-04 · Recorrido sin token · PASA

**Objetivo.** Todo endpoint protegido exige Authorization: Bearer.

**Petición.** `GET http://seguimiento:5110/api/v1/seguimiento/277/recorrido`

```http
Accept: application/json
X-Traza-Id: f23a51af-5d0d-4e5a-84e0-309cdefbadee
```

**Respuesta.** HTTP 401 (esperado 401) · 5 ms · traza `f23a51af-5d0d-4e5a-84e0-309cdefbadee`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "Falta el encabezado Authorization: Bearer <token>.",
    "traza_id": "f23a51af-5d0d-4e5a-84e0-309cdefbadee"
  }
}
```

## Servicio entregas · puerto 5105

### ENT-01 · Mis entregas · PASA

**Objetivo.** Paradas abiertas del repartidor en el turno de hoy (RN25).

**Petición.** `GET http://entregas:5105/api/v1/entregas/mias?pagina=1&por_pagina=20`

```http
Accept: application/json
X-Traza-Id: 1686cc15-218c-4c1d-a0b2-bfe3b90fa390
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 57 ms · traza `1686cc15-218c-4c1d-a0b2-bfe3b90fa390`

```json
{
  "datos": [
    {
      "id": 277,
      "pedido_id": 542,
      "folio": "PED-20261126-000542",
      "estado_pedido": "en_ruta",
      "orden_parada": 1,
      "direccion": "Cerro Prieto 4059, Valles de San Bernabé",
      "zona": "Valles de San Bernabé",
      "distancia_km": 1.16,
      "minutos_estimados": 10.0,
      "total": 143.0
    },
    {
      "id": 278,
      "pedido_id": 543,
      "folio": "PED-20261126-000543",
      "estado_pedido": "en_ruta",
      "orden_parada": 2,
      "direccion": "Emiliano Zapata 231, Valles de San Bernabé",
      "zona": "Valles de San Bernabé",
      "distancia_km": 0.61,
      "minutos_estimados": 16.0,
      "total": 173.0
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 2,
    "paginas": 1
  }
}
```

### ENT-02 · Detalle de la entrega · PASA

**Objetivo.** Cliente, domicilio y líneas.

**Petición.** `GET http://entregas:5105/api/v1/entregas/277`

```http
Accept: application/json
X-Traza-Id: a029b759-881d-41aa-9b1f-96db86c64865
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 82 ms · traza `a029b759-881d-41aa-9b1f-96db86c64865`

```json
{
  "id": 277,
  "pedido_id": 542,
  "folio": "PED-20261126-000542",
  "estado_pedido": "en_ruta",
  "cliente": {
    "nombre": "Francisco Treviño Alanís",
    "telefono": "8164763027"
  },
  "domicilio": {
    "calle": "Cerro Prieto",
    "numero_ext": "4059",
    "colonia": "Valles de San Bernabé",
    "latitud": 25.751679,
    "longitud": -100.366615
  },
  "orden_parada": 1,
  "distancia_km": 1.16,
  "minutos_estimados": 10.0,
  "total": 143.0,
  "lineas": [
    {
      "pedido_detalle_id": 1443,
      "nombre": "Limpiador multiusos",
      "cantidad": 2
    },
    {
      "pedido_detalle_id": 1444,
      "nombre": "Refresco sabor manzana",
      "cantidad": 2
    }
  ]
}
```

### ENT-03 · Entrega de otro repartidor · PASA

**Objetivo.** El repartidor 2 no ve la entrega del repartidor 1.

**Petición.** `GET http://entregas:5105/api/v1/entregas/277`

```http
Accept: application/json
X-Traza-Id: 3986fce6-747b-46fe-b858-b81f9fcd042a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4Iiwi…(296 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 38 ms · traza `3986fce6-747b-46fe-b858-b81f9fcd042a`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe la entrega o no está asignada a ti.",
    "traza_id": "3986fce6-747b-46fe-b858-b81f9fcd042a"
  }
}
```

### ENT-04 · Monto incorrecto (regla de negocio) · PASA

**Objetivo.** Una entrega completa cobra el total (RN27).

**Petición.** `POST http://entregas:5105/api/v1/entregas/277/resultado`

```http
Accept: application/json
X-Traza-Id: 40c578d8-277c-4b24-a4dc-4cc51a1e85bf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 1.0,
  "cambio_entregado": 0.0,
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611,
    "precision_m": 8.5
  },
  "evidencia_ids": [
    "6b089453cc73360fa2e7f17a"
  ],
  "capturado_en": "2026-11-26T20:19:32+00:00",
  "id_cliente_local": "1a51d53e-2d75-495c-a912-cdd6fc81a519"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 73 ms · traza `40c578d8-277c-4b24-a4dc-4cc51a1e85bf`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "monto_cobrado",
        "mensaje": "Una entrega completa cobra el total del pedido (143.00)."
      }
    ],
    "traza_id": "40c578d8-277c-4b24-a4dc-4cc51a1e85bf"
  }
}
```

### ENT-05 · Cerrar entrega como entregado · PASA

**Objetivo.** Registrar el resultado con evidencia y ubicación.

**Petición.** `POST http://entregas:5105/api/v1/entregas/277/resultado`

```http
Accept: application/json
X-Traza-Id: 4900d6b1-aeb6-4a43-a428-cdffe45d2bd5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 143.0,
  "cambio_entregado": 0.0,
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611,
    "precision_m": 8.5
  },
  "evidencia_ids": [
    "6b089453cc73360fa2e7f17a"
  ],
  "capturado_en": "2026-11-26T20:19:32+00:00",
  "id_cliente_local": "1a51d53e-2d75-495c-a912-cdd6fc81a519"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 139 ms · traza `4900d6b1-aeb6-4a43-a428-cdffe45d2bd5`

```json
{
  "entrega_id": 277,
  "pedido_id": 542,
  "estado_pedido": "entregado",
  "cerrado_en": "2026-11-26T14:19:32-06:00",
  "duplicado": false
}
```

**Explicación.** Una sola transacción: cierra la entrega, cambia el pedido (el trigger valida la transición y escribe historial y bitácora) y el trigger de cierre avisa al cliente. La operación se registra en MongoDB.

**Evidencia en PostgreSQL.** `SELECT id, cierre_en, resultado, monto_cobrado, id_cliente_local, evidencia_ids, cierre_latitud, cierre_longitud FROM entrega WHERE id = %s`

```json
[
  {
    "id": 277,
    "cierre_en": "2026-11-26 14:19:32.985270-06:00",
    "resultado": "entregado",
    "monto_cobrado": "143.00",
    "id_cliente_local": "1a51d53e-2d75-495c-a912-cdd6fc81a519",
    "evidencia_ids": [
      "6b089453cc73360fa2e7f17a"
    ],
    "cierre_latitud": "25.749100",
    "cierre_longitud": "-100.361100"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT estado_anterior, estado_nuevo, usuario_id, fecha FROM historial_estatus WHERE pedido_id = %s ORDER BY id DESC LIMIT 1`

```json
[
  {
    "estado_anterior": "en_ruta",
    "estado_nuevo": "entregado",
    "usuario_id": 7,
    "fecha": "2026-11-26 14:19:32.985270-06:00"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT destinatario_id, tipo, titulo, mensaje, referencia_tipo, referencia_id FROM web_notificacion WHERE referencia_tipo = 'pedido' AND referencia_id = %s ORDER BY id DESC LIMIT 1`

```json
[
  {
    "destinatario_id": 39,
    "tipo": "pedido",
    "titulo": "Pedido PED-20261126-000542",
    "mensaje": "El pedido cambió a entregado.",
    "referencia_tipo": "pedido",
    "referencia_id": "542"
  }
]
```

**Evidencia en MongoDB.** `db.sincronizaciones_moviles.findOne({operacion_uuid: '1a51d53e-2d75-495c-a912-cdd6fc81a519'})`

```json
{
  "operacion_uuid": "1a51d53e-2d75-495c-a912-cdd6fc81a519",
  "capturado_en": "2026-11-26 20:19:32+00:00",
  "carga": {
    "entrega_id": 277,
    "resultado": "entregado",
    "monto_cobrado": 143.0,
    "evidencia_ids": [
      "6b089453cc73360fa2e7f17a"
    ],
    "ubicacion": {
      "latitud": 25.7491,
      "longitud": -100.3611,
      "precision_m": 8.5
    }
  },
  "conflicto": null,
  "dispositivo_id": "app-movil",
  "estado": "aplicada",
  "intentos": 1,
  "pedido_id": 542,
  "sincronizado_en": "2026-11-26 20:19:33.040000+00:00",
  "tipo_operacion": "cierre_entrega",
  "usuario_id": 7
}
```

### ENT-06 · Reintento con el mismo UUID · PASA

**Objetivo.** Idempotencia: el cierre no se aplica dos veces.

**Petición.** `POST http://entregas:5105/api/v1/entregas/277/resultado`

```http
Accept: application/json
X-Traza-Id: a4d2bc65-1235-4126-a11f-a6856a36d7ca
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 143.0,
  "cambio_entregado": 0.0,
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611,
    "precision_m": 8.5
  },
  "evidencia_ids": [
    "6b089453cc73360fa2e7f17a"
  ],
  "capturado_en": "2026-11-26T20:19:32+00:00",
  "id_cliente_local": "1a51d53e-2d75-495c-a912-cdd6fc81a519"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 70 ms · traza `a4d2bc65-1235-4126-a11f-a6856a36d7ca`

```json
{
  "entrega_id": 277,
  "pedido_id": 542,
  "estado_pedido": "entregado",
  "cerrado_en": "2026-11-26T14:19:32-06:00",
  "duplicado": true
}
```

**Explicación.** La respuesta es la misma con duplicado=true. MongoDB actualiza el documento de la operación (intentos = 2).

**Evidencia en MongoDB.** `db.sincronizaciones_moviles.findOne({operacion_uuid: '1a51d53e-2d75-495c-a912-cdd6fc81a519'}, {estado: 1, intentos: 1})`

```json
{
  "estado": "aplicada",
  "intentos": 2,
  "sincronizado_en": "2026-11-26 20:19:33.171000+00:00"
}
```

### ENT-07 · Otro cierre sobre la misma entrega · PASA

**Objetivo.** Conflicto: ya estaba cerrada con otra operación.

**Petición.** `POST http://entregas:5105/api/v1/entregas/277/resultado`

```http
Accept: application/json
X-Traza-Id: 32ac6889-9e06-41e8-b913-22bbeeb8b6cb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 143.0,
  "cambio_entregado": 0.0,
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611,
    "precision_m": 8.5
  },
  "evidencia_ids": [
    "6b089453cc73360fa2e7f17a"
  ],
  "capturado_en": "2026-11-26T20:19:32+00:00",
  "id_cliente_local": "915ed23d-3209-4c72-ba34-a92bce3c4b86"
}
```

**Respuesta.** HTTP 409 (esperado 409) · 70 ms · traza `32ac6889-9e06-41e8-b913-22bbeeb8b6cb`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "La entrega ya se cerró con otra operación.",
    "traza_id": "32ac6889-9e06-41e8-b913-22bbeeb8b6cb"
  }
}
```

### ENT-08 · Detalle tras el cierre · PASA

**Objetivo.** El repartidor deja de ver el domicilio (RN26).

**Petición.** `GET http://entregas:5105/api/v1/entregas/277`

```http
Accept: application/json
X-Traza-Id: 62bfdbfd-421e-4c58-b98b-d69b47b194ef
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 37 ms · traza `62bfdbfd-421e-4c58-b98b-d69b47b194ef`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "La entrega ya se cerró; su información ya no está disponible.",
    "traza_id": "62bfdbfd-421e-4c58-b98b-d69b47b194ef"
  }
}
```

### ENT-09 · Parcial sin motivo · PASA

**Objetivo.** Cada línea devuelta necesita motivo (RN28).

**Petición.** `POST http://entregas:5105/api/v1/entregas/278/resultado`

```http
Accept: application/json
X-Traza-Id: 35f7fcb5-3625-4d76-a668-44c55d6c2d04
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "parcial",
  "monto_cobrado": 10.0,
  "cambio_entregado": 0.0,
  "incidencia": "El cliente rechazó una línea.",
  "lineas": [
    {
      "pedido_detalle_id": 1445,
      "cantidad_entregada": 2,
      "cantidad_devuelta": 0
    },
    {
      "pedido_detalle_id": 1446,
      "cantidad_entregada": 0,
      "cantidad_devuelta": 2
    }
  ],
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611
  },
  "evidencia_ids": [
    "6b089454cc73360fa2e7f17d"
  ],
  "capturado_en": "2026-11-26T20:19:32+00:00",
  "id_cliente_local": "e023dfd5-2f4a-4389-8ff9-8678579adc15"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 73 ms · traza `35f7fcb5-3625-4d76-a668-44c55d6c2d04`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "lineas[1].motivo",
        "mensaje": "Explica por qué regresan unidades."
      }
    ],
    "traza_id": "35f7fcb5-3625-4d76-a668-44c55d6c2d04"
  }
}
```

### ENT-10 · Cerrar como entrega parcial · PASA

**Objetivo.** Devolver al inventario lo que no se entregó.

**Petición.** `POST http://entregas:5105/api/v1/entregas/278/resultado`

```http
Accept: application/json
X-Traza-Id: fa056b5d-7bd9-431b-bb02-2f3ba2972830
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "parcial",
  "monto_cobrado": 10.0,
  "cambio_entregado": 0.0,
  "incidencia": "El cliente rechazó una línea.",
  "lineas": [
    {
      "pedido_detalle_id": 1445,
      "cantidad_entregada": 2,
      "cantidad_devuelta": 0
    },
    {
      "pedido_detalle_id": 1446,
      "cantidad_entregada": 0,
      "cantidad_devuelta": 2,
      "motivo": "El cliente la rechazó."
    }
  ],
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611
  },
  "evidencia_ids": [
    "6b089454cc73360fa2e7f17d"
  ],
  "capturado_en": "2026-11-26T20:19:32+00:00",
  "id_cliente_local": "e023dfd5-2f4a-4389-8ff9-8678579adc15"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 116 ms · traza `fa056b5d-7bd9-431b-bb02-2f3ba2972830`

```json
{
  "entrega_id": 278,
  "pedido_id": 543,
  "estado_pedido": "entrega_parcial",
  "cerrado_en": "2026-11-26T14:19:33-06:00",
  "duplicado": false
}
```

**Explicación.** fn_devolver_inventario (la misma función que usa el web) regresa las unidades devueltas.

**Evidencia en PostgreSQL.** `SELECT entrega_id, pedido_detalle_id, cantidad_entregada, cantidad_devuelta, motivo FROM entrega_linea WHERE entrega_id = %s`

```json
[
  {
    "entrega_id": 278,
    "pedido_detalle_id": 1445,
    "cantidad_entregada": 2,
    "cantidad_devuelta": 0,
    "motivo": null
  },
  {
    "entrega_id": 278,
    "pedido_detalle_id": 1446,
    "cantidad_entregada": 0,
    "cantidad_devuelta": 2,
    "motivo": "El cliente la rechazó."
  }
]
```

**Evidencia en PostgreSQL.** `SELECT tipo, producto_id, cantidad, existencia_resultante, motivo FROM movimiento_inventario WHERE referencia_id = %s AND tipo = 'devolucion_parcial'`

```json
[
  {
    "tipo": "devolucion_parcial",
    "producto_id": 49,
    "cantidad": 2,
    "existencia_resultante": 36,
    "motivo": "Entrega parcial: regresan las unidades devueltas (RN28)."
  }
]
```

### ENT-11 · Entregas de un pedido (administrador) · PASA

**Objetivo.** Consulta por pedido para el portal web.

**Petición.** `GET http://entregas:5105/api/v1/entregas?pedido_id=542`

```http
Accept: application/json
X-Traza-Id: f16d0a69-56d5-46ce-8c61-7fc4873b9aa5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 57 ms · traza `f16d0a69-56d5-46ce-8c61-7fc4873b9aa5`

```json
{
  "datos": [
    {
      "id": 277,
      "pedido_id": 542,
      "folio": "PED-20261126-000542",
      "estado_pedido": "entregado",
      "orden_parada": 1,
      "direccion": "Cerro Prieto 4059, Valles de San Bernabé",
      "zona": "Valles de San Bernabé",
      "distancia_km": 1.16,
      "minutos_estimados": 10.0,
      "total": 143.0
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 1,
    "paginas": 1
  }
}
```

## Servicio planeacion · puerto 5106

### PLA-01 · Candidatos (XML) · PASA

**Objetivo.** Lista de ubicaciones candidatas.

**Petición.** `GET http://planeacion:5106/api/v1/candidatos?pagina=1&por_pagina=3`

```http
Accept: application/xml
X-Traza-Id: 63481298-672d-411c-a6cc-c415091bed0b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 83 ms · traza `63481298-672d-411c-a6cc-c415091bed0b`

```xml
<?xml version='1.0' encoding='utf-8'?>
<candidatos xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><datos><candidato><id>1</id><clave>CAND-01</clave><nombre>San Bernabé Norte</nombre><latitud>25.752</latitud><longitud>-100.361</longitud><renta_estimada>18000.00</renta_estimada><nomina_estimada>42000.00</nomina_estimada><servicios_estimados>7000.00</servicios_estimados><otros_costos>5000.00</otros_costos><costo_fijo>72000.00</costo_fijo><superficie_m2>130</superficie_m2><capacidad_fisica>150</capacidad_fisica><accesibilidad_vial>9</accesibilidad_vial><zona_id>1</zona_id><poblacion_cubierta>8420</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato><candidato><id>2</id><clave>CAND-02</clave><nombre>Valles Poniente</nombre><latitud>25.7555</latitud><longitud>-100.376</longitud><renta_estimada>15500.00</renta_estimada><nomina_estimada>42000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><costo_fijo>68500.00</costo_fijo><superficie_m2>105</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>2</zona_id><poblacion_cubierta>6180</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato><candidato><id>3</id><clave>CAND-05</clave><nombre>Alianza Real</nombre><latitud>25.7625</latitud><longitud>-100.353</longitud><renta_estimada>21000.00</renta_estimada><nomina_estimada>46000.00</nomina_estimada><servicios_estimados>8000.00</servicios_estimados><otros_costos>6000.00</otros_costos><costo_fijo>81000.00</costo_fijo><superficie_m2>150</superficie_m2><capacidad_fisica>180</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>3900</poblacion_cubierta><radio_km>1.6</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>16</total><paginas>6</paginas></paginacion></candidatos>
```

### PLA-02 · Registrar candidato (XML) · PASA

**Objetivo.** Alta con costo fijo calculado por PostgreSQL.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos`

```http
Accept: application/xml
X-Traza-Id: b3869468-9d02-4e57-9c7d-ef0985cbc260
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><candidato_nuevo xmlns="urn:microhubs:v1"><clave>********</clave><nombre>Alianza Norte</nombre><latitud>25.7601</latitud><longitud>-100.3555</longitud><renta_estimada>16000.00</renta_estimada><nomina_estimada>40000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><superficie_m2>110</superficie_m2><capacidad_fisica>130</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km></candidato_nuevo>
```

**Respuesta.** HTTP 201 (esperado 201) · 85 ms · traza `b3869468-9d02-4e57-9c7d-ef0985cbc260`

```xml
<?xml version='1.0' encoding='utf-8'?>
<candidato xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>139</id><clave>EV-727EE4</clave><nombre>Alianza Norte</nombre><latitud>25.7601</latitud><longitud>-100.3555</longitud><renta_estimada>16000.00</renta_estimada><nomina_estimada>40000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><costo_fijo>67000.00</costo_fijo><superficie_m2>110</superficie_m2><capacidad_fisica>130</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato>
```

**Evidencia en PostgreSQL.** `SELECT id, clave, nombre, renta_estimada, costo_fijo, decision FROM ubicacion_candidata WHERE clave = %s`

```json
[
  {
    "id": 139,
    "clave": "EV-727EE4",
    "nombre": "Alianza Norte",
    "renta_estimada": "16000.00",
    "costo_fijo": "67000.00",
    "decision": "pendiente"
  }
]
```

### PLA-03 · Clave duplicada · PASA

**Objetivo.** No se repite la clave de un candidato.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos`

```http
Accept: application/xml
X-Traza-Id: 0e0cbe94-d0c5-497a-928c-4c9093c76683
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><candidato_nuevo xmlns="urn:microhubs:v1"><clave>********</clave><nombre>Alianza Norte</nombre><latitud>25.7601</latitud><longitud>-100.3555</longitud><renta_estimada>16000.00</renta_estimada><nomina_estimada>40000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><superficie_m2>110</superficie_m2><capacidad_fisica>130</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km></candidato_nuevo>
```

**Respuesta.** HTTP 409 (esperado 409) · 48 ms · traza `0e0cbe94-d0c5-497a-928c-4c9093c76683`

```xml
<?xml version='1.0' encoding='utf-8'?>
<error xmlns="urn:microhubs:v1" version="1"><codigo>CONFLICTO</codigo><mensaje>Ya existe un registro con esos datos.</mensaje><traza_id>0e0cbe94-d0c5-497a-928c-4c9093c76683</traza_id></error>
```

### PLA-04 · Modificar candidato (PUT) · PASA

**Objetivo.** Cambiar la renta recalcula el costo fijo.

**Petición.** `PUT http://planeacion:5106/api/v1/candidatos/139`

```http
Accept: application/json
X-Traza-Id: 2ef91958-69f2-4027-a457-2924d7b53a88
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "clave": "********",
  "nombre": "Alianza Norte (editado)",
  "latitud": "25.7601",
  "longitud": "-100.3555",
  "renta_estimada": 18000,
  "nomina_estimada": "40000.00",
  "servicios_estimados": "6500.00",
  "otros_costos": "4500.00",
  "superficie_m2": "110",
  "capacidad_fisica": "130",
  "accesibilidad_vial": "7",
  "zona_id": "3",
  "poblacion_cubierta": "5200",
  "radio_km": "1.5"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 88 ms · traza `2ef91958-69f2-4027-a457-2924d7b53a88`

```json
{
  "id": 139,
  "clave": "********",
  "nombre": "Alianza Norte (editado)",
  "latitud": 25.7601,
  "longitud": -100.3555,
  "renta_estimada": 18000.0,
  "nomina_estimada": 40000.0,
  "servicios_estimados": 6500.0,
  "otros_costos": 4500.0,
  "costo_fijo": 69000.0,
  "superficie_m2": 110.0,
  "capacidad_fisica": 130,
  "accesibilidad_vial": 7,
  "zona_id": 3,
  "poblacion_cubierta": 5200,
  "radio_km": 1.5,
  "decision": "pendiente",
  "decision_motivo": null
}
```

### PLA-05 · Simular candidato (XML) · PASA

**Objetivo.** Viabilidad con los costos del candidato.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/139/simular`

```http
Accept: application/xml
X-Traza-Id: efac0387-2277-4e8f-8e7a-f5633324921a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<simular xmlns="urn:microhubs:v1"/>
```

**Respuesta.** HTTP 200 (esperado 200) · 281 ms · traza `efac0387-2277-4e8f-8e7a-f5633324921a`

```xml
<?xml version='1.0' encoding='utf-8'?>
<resultados xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><atendidos>0</atendidos><rechazados>0</rechazados><utilizacion>0</utilizacion><nivel>estable</nivel><tiempo_estimado_min>18.6</tiempo_estimado_min><operadores_requeridos>0</operadores_requeridos><repartidores_requeridos>0</repartidores_requeridos><ingreso_dia>0.00</ingreso_dia><margen_dia>-2300.00</margen_dia><costo_por_pedido xsi:nil="true" /><equilibrio><margen_pedido>23.46</margen_pedido><mensual>2941.6</mensual><diario>98.1</diario></equilibrio><decision>NO VIABLE CON LOS SUPUESTOS ACTUALES</decision><explicacion><motivo>la demanda atendida (0/día) no alcanza el equilibrio (98/día)</motivo><motivo>reducir costos fijos, aumentar ticket o buscar una ubicación con más demanda</motivo></explicacion></resultados>
```

**Explicación.** Usa planeacion_calc.py (las mismas fórmulas del web) y guarda la ejecución en MongoDB.

**Evidencia en MongoDB.** `db.ejecuciones_analiticas.find().sort({ejecutado_en: -1}).limit(1)`

```json
{
  "escenario_id": "candidato-139",
  "nombre_escenario": "Candidato 139",
  "tipo_analisis": "punto_equilibrio",
  "ejecutado_en": "2026-11-26 20:19:34.173000+00:00",
  "usuario_id": 5,
  "version_modelo": "planeacion_calc 2.1",
  "parametros_entrada": {
    "demanda_diaria": 0.0,
    "operadores": 3.0,
    "repartidores": 3.0,
    "ticket": 148.06,
    "costo_entrega": 18.0,
    "margen_bruto": 0.28,
    "renta": 18000.0,
    "nomina": 40000.0,
    "servicios": 6500.0,
    "otros": 4500.0,
    "distancia_km": 2.0,
    "capacidad_fisica": 130.0
  },
  "supuestos": [
    "demanda_diaria = 0.0",
    "operadores = 3",
    "repartidores = 3",
    "ticket = 148.06",
    "costo_entrega = 18.00",
    "margen_bruto = 0.28",
    "renta = 18000.00",
    "nomina = 40000.00",
    "servicios = 6500.00",
    "otros = 4500.00",
    "distancia_km = 2.0",
    "capacidad_fisica = 130"
  ],
  "resultados": {
    "decision": "NO VIABLE CON LOS SUPUESTOS ACTUALES",
    "utilizacion": 0.0,
    "atendidos": 0.0,
    "equilibrio_diario": 98.1,
    "costo_por_pedido": null
  },
  "recomendacion": "NO VIABLE CON LOS SUPUESTOS ACTUALES",
  "datos_suficientes": true,
  "duracion_ms": 0,
  "aplicado_por": null
}
```

### PLA-06 · Decisión sin motivo suficiente · PASA

**Objetivo.** La decisión humana exige motivo.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/139/decision`

```http
Accept: application/json
X-Traza-Id: e064cf38-49f1-4ef9-9ac9-73f2f62ad1c2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aceptado",
  "motivo": "ok"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 22 ms · traza `e064cf38-49f1-4ef9-9ac9-73f2f62ad1c2`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "motivo",
        "mensaje": "Debe tener al menos 3 caracteres."
      }
    ],
    "traza_id": "e064cf38-49f1-4ef9-9ac9-73f2f62ad1c2"
  }
}
```

### PLA-07 · Decisión humana de apertura · PASA

**Objetivo.** Registrar la decisión con motivo.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/139/decision`

```http
Accept: application/json
X-Traza-Id: da167ffd-9327-4436-a8e5-dd5068e083e1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "condicionado",
  "motivo": "Renegociar la renta antes de firmar."
}
```

**Respuesta.** HTTP 200 (esperado 200) · 55 ms · traza `da167ffd-9327-4436-a8e5-dd5068e083e1`

```json
{
  "id": 139,
  "clave": "********",
  "nombre": "Alianza Norte (editado)",
  "latitud": 25.7601,
  "longitud": -100.3555,
  "renta_estimada": 18000.0,
  "nomina_estimada": 40000.0,
  "servicios_estimados": 6500.0,
  "otros_costos": 4500.0,
  "costo_fijo": 69000.0,
  "superficie_m2": 110.0,
  "capacidad_fisica": 130,
  "accesibilidad_vial": 7,
  "zona_id": 3,
  "poblacion_cubierta": 5200,
  "radio_km": 1.5,
  "decision": "condicionado",
  "decision_motivo": "Renegociar la renta antes de firmar."
}
```

**Evidencia en PostgreSQL.** `SELECT id, decision, decision_motivo, decision_por, decision_en FROM ubicacion_candidata WHERE id = %s`

```json
[
  {
    "id": 139,
    "decision": "condicionado",
    "decision_motivo": "Renegociar la renta antes de firmar.",
    "decision_por": 5,
    "decision_en": "2026-11-26 14:19:34.236321-06:00"
  }
]
```

### PLA-08 · Simulación libre: Escenario A · PASA

**Objetivo.** Punto de equilibrio del caso de la retroalimentación.

**Petición.** `POST http://planeacion:5106/api/v1/simulaciones`

```http
Accept: application/json
X-Traza-Id: fde8b5d9-49b4-4d48-8ed2-8706c1fd056e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "supuestos": {
    "demanda_diaria": 120,
    "operadores": 3,
    "repartidores": 4,
    "ticket": 135.0,
    "costo_entrega": 22.0,
    "margen_bruto": 0.28,
    "renta": 18000.0,
    "nomina": 42000.0,
    "servicios": 7000.0,
    "otros": 5000.0,
    "distancia_km": 2.4,
    "capacidad_fisica": 150
  }
}
```

**Respuesta.** HTTP 200 (esperado 200) · 27 ms · traza `fde8b5d9-49b4-4d48-8ed2-8706c1fd056e`

```json
{
  "atendidos": 120.0,
  "rechazados": 0.0,
  "utilizacion": 80.0,
  "nivel": "atencion",
  "tiempo_estimado_min": 19.4,
  "operadores_requeridos": 3,
  "repartidores_requeridos": 2,
  "ingreso_dia": 16200.0,
  "margen_dia": -504.0,
  "costo_por_pedido": 42.0,
  "equilibrio": {
    "margen_pedido": 15.8,
    "mensual": 4557.0,
    "diario": 151.9
  },
  "decision": "NO VIABLE CON LOS SUPUESTOS ACTUALES",
  "explicacion": [
    "la demanda atendida (120/día) no alcanza el equilibrio (152/día)",
    "el espacio físico del local limita la capacidad",
    "reducir costos fijos, aumentar ticket o buscar una ubicación con más demanda"
  ]
}
```

**Explicación.** 72,000 de costos fijos entre 15.80 de margen por pedido = 4,557 pedidos al mes (151.9 al día).

### PLA-09 · Guardar escenario · PASA

**Objetivo.** Escenario compartido con el portal web.

**Petición.** `POST http://planeacion:5106/api/v1/escenarios`

```http
Accept: application/json
X-Traza-Id: 95382520-abe0-4ff9-a1ca-8f1424f4c76b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Escenario A - evidencias",
  "candidato_id": 139,
  "supuestos": {
    "demanda_diaria": 120,
    "operadores": 3,
    "repartidores": 4,
    "ticket": 135.0,
    "costo_entrega": 22.0,
    "margen_bruto": 0.28,
    "renta": 18000.0,
    "nomina": 42000.0,
    "servicios": 7000.0,
    "otros": 5000.0,
    "distancia_km": 2.4,
    "capacidad_fisica": 150
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 80 ms · traza `95382520-abe0-4ff9-a1ca-8f1424f4c76b`

```json
{
  "id": 24,
  "nombre": "Escenario A - evidencias",
  "candidato_id": 139,
  "supuestos": {
    "demanda_diaria": 120.0,
    "operadores": 3,
    "repartidores": 4,
    "ticket": 135.0,
    "costo_entrega": 22.0,
    "margen_bruto": 0.28,
    "renta": 18000.0,
    "nomina": 42000.0,
    "servicios": 7000.0,
    "otros": 5000.0,
    "distancia_km": 2.4,
    "capacidad_fisica": 150
  },
  "resultados": {
    "atendidos": 120.0,
    "rechazados": 0.0,
    "utilizacion": 80.0,
    "nivel": "atencion",
    "tiempo_estimado_min": 19.4,
    "operadores_requeridos": 3,
    "repartidores_requeridos": 2,
    "ingreso_dia": 16200.0,
    "margen_dia": -504.0,
    "costo_por_pedido": 42.0,
    "equilibrio": {
      "margen_pedido": 15.8,
      "mensual": 4557.0,
      "diario": 151.9
    },
    "decision": "NO VIABLE CON LOS SUPUESTOS ACTUALES",
    "explicacion": [
      "la demanda atendida (120/día) no alcanza el equilibrio (152/día)",
      "el espacio físico del local limita la capacidad",
      "reducir costos fijos, aumentar ticket o buscar una ubicación con más demanda"
    ]
  },
  "creado_en": "2026-11-26T14:19:34-06:00"
}
```

### PLA-10 · Abrir escenario (XML) · PASA

**Objetivo.** Escenario con supuestos y resultados.

**Petición.** `GET http://planeacion:5106/api/v1/escenarios/24`

```http
Accept: application/xml
X-Traza-Id: 9b515b0e-fa5f-410b-955d-5381ae46b330
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 25 ms · traza `9b515b0e-fa5f-410b-955d-5381ae46b330`

```xml
<?xml version='1.0' encoding='utf-8'?>
<escenario xmlns="urn:microhubs:v1" version="1"><id>24</id><nombre>Escenario A - evidencias</nombre><candidato_id>139</candidato_id><supuestos><demanda_diaria>120</demanda_diaria><operadores>3</operadores><repartidores>4</repartidores><ticket>135.00</ticket><costo_entrega>22.00</costo_entrega><margen_bruto>0.28</margen_bruto><renta>18000.00</renta><nomina>42000.00</nomina><servicios>7000.00</servicios><otros>5000.00</otros><distancia_km>2.4</distancia_km><capacidad_fisica>150</capacidad_fisica></supuestos><resultados><atendidos>120</atendidos><rechazados>0</rechazados><utilizacion>80</utilizacion><nivel>atencion</nivel><tiempo_estimado_min>19.4</tiempo_estimado_min><operadores_requeridos>3</operadores_requeridos><repartidores_requeridos>2</repartidores_requeridos><ingreso_dia>16200.00</ingreso_dia><margen_dia>-504.00</margen_dia><costo_por_pedido>42.00</costo_por_pedido><equilibrio><margen_pedido>15.80</margen_pedido><mensual>4557</mensual><diario>151.9</diario></equilibrio><decision>NO VIABLE CON LOS SUPUESTOS ACTUALES</decision><explicacion><motivo>la demanda atendida (120/día) no alcanza el equilibrio (152/día)</motivo><motivo>el espacio físico del local limita la capacidad</motivo><motivo>reducir costos fijos, aumentar ticket o buscar una ubicación con más demanda</motivo></explicacion></resultados><creado_en>2026-11-26T14:19:34-06:00</creado_en></escenario>
```

### PLA-11 · Resumen de simulaciones · PASA

**Objetivo.** Agregación $group en MongoDB por decisión.

**Petición.** `GET http://planeacion:5106/api/v1/simulaciones/resumen`

```http
Accept: application/json
X-Traza-Id: 5de1c962-910a-4f51-b283-7b055a85849e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 9 ms · traza `5de1c962-910a-4f51-b283-7b055a85849e`

```json
{
  "total": 64,
  "por_decision": [
    {
      "decision": "NO VIABLE CON LOS SUPUESTOS ACTUALES",
      "cantidad": 64,
      "utilizacion_promedio": 55.0
    }
  ]
}
```

**Evidencia en MongoDB.** `db.ejecuciones_analiticas.aggregate([{$match:{tipo_analisis:'punto_equilibrio'}}, {$group:{_id:'$resultados.decision', cantidad:{$sum:1}, utilizacion_promedio:{$avg:'$resultados.utilizacion'}}}])`

```json
[
  {
    "_id": "NO VIABLE CON LOS SUPUESTOS ACTUALES",
    "cantidad": 64,
    "utilizacion_promedio": 55.0
  }
]
```

### PLA-12 · Auditor intenta registrar · PASA

**Objetivo.** El auditor solo consulta (RN-E01).

**Petición.** `POST http://planeacion:5106/api/v1/candidatos`

```http
Accept: application/json
X-Traza-Id: 5f84bf73-7538-4180-b48d-5e4c4d97deac
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{
  "clave": "********",
  "nombre": "Alianza Norte",
  "latitud": "25.7601",
  "longitud": "-100.3555",
  "renta_estimada": "16000.00",
  "nomina_estimada": "40000.00",
  "servicios_estimados": "6500.00",
  "otros_costos": "4500.00",
  "superficie_m2": "110",
  "capacidad_fisica": "130",
  "accesibilidad_vial": "7",
  "zona_id": "3",
  "poblacion_cubierta": "5200",
  "radio_km": "1.5"
}
```

**Respuesta.** HTTP 403 (esperado 403) · 58 ms · traza `5f84bf73-7538-4180-b48d-5e4c4d97deac`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "5f84bf73-7538-4180-b48d-5e4c4d97deac"
  }
}
```

### PLA-13 · Auditor intenta simular · PASA

**Objetivo.** Sin simulacion.ejecutar.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/139/simular`

```http
Accept: application/json
X-Traza-Id: 5d7380c0-7b87-4726-8bc5-be0c75f9be4d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 403 (esperado 403) · 26 ms · traza `5d7380c0-7b87-4726-8bc5-be0c75f9be4d`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "5d7380c0-7b87-4726-8bc5-be0c75f9be4d"
  }
}
```

### PLA-14 · Eliminar escenario (DELETE) · PASA

**Objetivo.** Borrar un escenario.

**Petición.** `DELETE http://planeacion:5106/api/v1/escenarios/24`

```http
Accept: application/json
X-Traza-Id: 2ef8c583-eb69-4c34-a840-f12c82202319
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 35 ms · traza `2ef8c583-eb69-4c34-a840-f12c82202319`

```json
(sin cuerpo)
```

### PLA-15 · Dar de baja candidato (DELETE) · PASA

**Objetivo.** Baja lógica: se conserva su historia.

**Petición.** `DELETE http://planeacion:5106/api/v1/candidatos/139`

```http
Accept: application/json
X-Traza-Id: 5446dffa-323b-426a-9a58-27948db1ff14
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 55 ms · traza `5446dffa-323b-426a-9a58-27948db1ff14`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT id, clave, estatus, decision FROM ubicacion_candidata WHERE id = %s`

```json
[
  {
    "id": 139,
    "clave": "EV-727EE4",
    "estatus": "inactivo",
    "decision": "condicionado"
  }
]
```

### PLA-16 · Candidato inexistente · PASA

**Objetivo.** Registro que no existe.

**Petición.** `GET http://planeacion:5106/api/v1/candidatos/999999`

```http
Accept: application/json
X-Traza-Id: d28d931f-8027-40d0-abd0-835ef325c45b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 24 ms · traza `d28d931f-8027-40d0-abd0-835ef325c45b`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el candidato.",
    "traza_id": "d28d931f-8027-40d0-abd0-835ef325c45b"
  }
}
```

## Servicio inventario · puerto 5111

### INV-01 · Existencias por microhub · PASA

**Objetivo.** Existencia física, reservada y disponible de cada producto.

**Petición.** `GET http://inventario:5111/api/v1/inventario?por_pagina=5`

```http
Accept: application/json
X-Traza-Id: c96fc4b7-e251-45a8-9c1b-ef139a0888c9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 632 ms · traza `c96fc4b7-e251-45a8-9c1b-ef139a0888c9`

```json
{
  "datos": [
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 1,
        "clave_interna": "AB-001",
        "nombre": "Frijol negro a granel"
      },
      "existencia": 58,
      "minimo": 10,
      "reservado": 0,
      "disponible": 58,
      "estado": "normal",
      "actualizado_en": "2026-11-25T15:47:14-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 2,
        "clave_interna": "AB-002",
        "nombre": "Arroz superextra"
      },
      "existencia": 36,
      "minimo": 10,
      "reservado": 0,
      "disponible": 36,
      "estado": "normal",
      "actualizado_en": "2026-11-26T00:34:30-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 3,
        "clave_interna": "AB-003",
        "nombre": "Aceite vegetal"
      },
      "existencia": 10,
      "minimo": 5,
      "reservado": 0,
      "disponible": 10,
      "estado": "normal",
      "actualizado_en": "2026-11-26T13:51:58-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 4,
        "clave_interna": "AB-004",
        "nombre": "Azúcar estándar"
      },
      "existencia": 18,
      "minimo": 10,
      "reservado": 0,
      "disponible": 18,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 5,
        "clave_interna": "AB-005",
        "nombre": "Sal de mesa"
      },
      "existencia": 30,
      "minimo": 8,
      "reservado": 0,
      "disponible": 30,
      "estado": "normal",
      "actualizado_en": "2026-11-26T00:34:28-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 153,
    "paginas": 31
  }
}
```

**Explicación.** Lee la vista v_inventario_disponible (existencia − reservas activas y vigentes). Los nombres de producto y microhub los pide a los servicios de productos y microhubs, no los lee de sus tablas.

**Evidencia en PostgreSQL.** `SELECT count(*) AS filas, sum(existencia) AS unidades, sum(reservado) AS reservado FROM v_inventario_disponible`

```json
[
  {
    "filas": 153,
    "unidades": 7558,
    "reservado": 0
  }
]
```

### INV-02 · Existencias (XML) · PASA

**Objetivo.** La app de escritorio recibe XML que cumple inventario.xsd.

**Petición.** `GET http://inventario:5111/api/v1/inventario?por_pagina=3`

```http
Accept: application/xml
X-Traza-Id: 419d2873-229f-414b-8ae8-82f2fd34e049
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 69 ms · traza `419d2873-229f-414b-8ae8-82f2fd34e049`

```xml
<?xml version='1.0' encoding='utf-8'?>
<existencias xmlns="urn:microhubs:v1" version="1"><datos><existencia><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><producto><id>1</id><clave_interna>AB-001</clave_interna><nombre>Frijol negro a granel</nombre></producto><existencia>58</existencia><minimo>10</minimo><reservado>0</reservado><disponible>58</disponible><estado>normal</estado><actualizado_en>2026-11-25T15:47:14-06:00</actualizado_en></existencia><existencia><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><producto><id>2</id><clave_interna>AB-002</clave_interna><nombre>Arroz superextra</nombre></producto><existencia>36</existencia><minimo>10</minimo><reservado>0</reservado><disponible>36</disponible><estado>normal</estado><actualizado_en>2026-11-26T00:34:30-06:00</actualizado_en></existencia><existencia><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><producto><id>3</id><clave_interna>AB-003</clave_interna><nombre>Aceite vegetal</nombre></producto><existencia>10</existencia><minimo>5</minimo><reservado>0</reservado><disponible>10</disponible><estado>normal</estado><actualizado_en>2026-11-26T13:51:58-06:00</actualizado_en></existencia></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>153</total><paginas>51</paginas></paginacion></existencias>
```

### INV-03 · Filtro de estado inválido · PASA

**Objetivo.** Un filtro desconocido se rechaza.

**Petición.** `GET http://inventario:5111/api/v1/inventario?estado=inventado`

```http
Accept: application/json
X-Traza-Id: 1bf52970-8385-413b-b84d-9aa499f0052b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 9 ms · traza `1bf52970-8385-413b-b84d-9aa499f0052b`

```json
{
  "error": {
    "codigo": "FILTRO_INVALIDO",
    "mensaje": "Valor no permitido para estado: inventado.",
    "detalles": [
      {
        "campo": "estado",
        "mensaje": "Valor no permitido para estado: inventado."
      }
    ],
    "traza_id": "1bf52970-8385-413b-b84d-9aa499f0052b"
  }
}
```

### INV-04 · El operador ve solo su microhub · PASA

**Objetivo.** Ámbito por microhub del perfil operador.

**Petición.** `GET http://inventario:5111/api/v1/inventario?por_pagina=100`

```http
Accept: application/json
X-Traza-Id: 72eb9d61-0450-44fc-8c4c-02453edf51c5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 62 ms · traza `72eb9d61-0450-44fc-8c4c-02453edf51c5`

```json
{
  "datos": [
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 1,
        "clave_interna": "AB-001",
        "nombre": "Frijol negro a granel"
      },
      "existencia": 58,
      "minimo": 10,
      "reservado": 0,
      "disponible": 58,
      "estado": "normal",
      "actualizado_en": "2026-11-25T15:47:14-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 2,
        "clave_interna": "AB-002",
        "nombre": "Arroz superextra"
      },
      "existencia": 36,
      "minimo": 10,
      "reservado": 0,
      "disponible": 36,
      "estado": "normal",
      "actualizado_en": "2026-11-26T00:34:30-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 3,
        "clave_interna": "AB-003",
        "nombre": "Aceite vegetal"
      },
      "existencia": 10,
      "minimo": 5,
      "reservado": 0,
      "disponible": 10,
      "estado": "normal",
      "actualizado_en": "2026-11-26T13:51:58-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 4,
        "clave_interna": "AB-004",
        "nombre": "Azúcar estándar"
      },
      "existencia": 18,
      "minimo": 10,
      "reservado": 0,
      "disponible": 18,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 5,
        "clave_interna": "AB-005",
        "nombre": "Sal de mesa"
      },
      "existencia": 30,
      "minimo": 8,
      "reservado": 0,
      "disponible": 30,
      "estado": "normal",
      "actualizado_en": "2026-11-26T00:34:28-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 6,
        "clave_interna": "AB-006",
        "nombre": "Harina de maíz nixtamalizado"
      },
      "existencia": 81,
      "minimo": 10,
      "reservado": 0,
      "disponible": 81,
      "estado": "normal",
      "actualizado_en": "2026-11-26T14:04:48-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 7,
        "clave_interna": "AB-007",
        "nombre": "Harina de trigo"
      },
      "existencia": 14,
      "minimo": 10,
      "reservado": 0,
      "disponible": 14,
      "estado": "normal",
      "actualizado_en": "2026-11-26T14:04:49-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 8,
        "clave_interna": "AB-008",
        "nombre": "Pasta para sopa surtida"
      },
      "existencia": 21,
      "minimo": 10,
      "reservado": 0,
      "disponible": 21,
      "estado": "normal",
      "actualizado_en": "2026-11-26T00:35:10-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 9,
        "clave_interna": "AB-009",
        "nombre": "Atún en agua"
      },
      "existencia": 42,
      "minimo": 10,
      "reservado": 0,
      "disponible": 42,
      "estado": "normal",
      "actualizado_en": "2026-11-26T14:04:50-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 10,
        "clave_interna": "AB-010",
        "nombre": "Sardina en salsa de tomate"
      },
      "existencia": 644,
      "minimo": 10,
      "reservado": 0,
      "disponible": 644,
      "estado": "normal",
      "actualizado_en": "2026-11-26T14:04:58-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 11,
        "clave_interna": "AB-011",
        "nombre": "Frijoles refritos"
      },
      "existencia": 27,
      "minimo": 10,
      "reservado": 0,
      "disponible": 27,
      "estado": "normal",
      "actualizado_en": "2026-11-26T14:09:01-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 12,
        "clave_interna": "AB-012",
        "nombre": "Chiles jalapeños en escabeche"
      },
      "existencia": 392,
      "minimo": 8,
      "reservado": 0,
      "disponible": 392,
      "estado": "normal",
      "actualizado_en": "2026-11-26T00:32:06-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 13,
        "clave_interna": "AB-013",
        "nombre": "Puré de tomate"
      },
      "existencia": 56,
      "minimo": 5,
      "reservado": 0,
      "disponible": 56,
      "estado": "normal",
      "actualizado_en": "2026-11-26T13:51:58-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 14,
        "clave_interna": "AB-014",
        "nombre": "Café soluble"
      },
      "existencia": 33,
      "minimo": 5,
      "reservado": 0,
      "disponible": 33,
      "estado": "normal",
      "actualizado_en": "2026-11-26T14:09:01-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 15,
        "clave_interna": "AB-015",
        "nombre": "Avena en hojuelas"
      },
      "existencia": 52,
      "minimo": 5,
      "reservado": 0,
      "disponible": 52,
      "estado": "normal",
      "actualizado_en": "2026-11-26T14:04:56-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 16,
        "clave_interna": "AB-016",
        "nombre": "Galletas María"
      },
      "existencia": 81,
      "minimo": 8,
      "reservado": 0,
      "disponible": 81,
      "estado": "normal",
      "actualizado_en": "2026-11-26T14:09:01-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 17,
        "clave_interna": "AB-017",
        "nombre": "Tortillas de maíz"
      },
      "existencia": 21,
      "minimo": 8,
      "reservado": 0,
      "disponible": 21,
      "estado": "normal",
      "actualizado_en": "2026-11-26T00:38:20-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 18,
        "clave_interna": "AB-018",
        "nombre": "Pan de caja blanco"
      },
      "existencia": 80,
      "minimo": 8,
      "reservado": 0,
      "disponible": 80,
      "estado": "normal",
      "actualizado_en": "2026-11-26T14:09:21-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 19,
        "clave_interna": "AB-019",
        "nombre": "Huevo blanco"
      },
      "existencia": 49,
      "minimo": 5,
      "reservado": 0,
      "disponible": 49,
      "estado": "normal",
      "actualizado_en": "2026-11-26T13:51:58-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 20,
        "clave_interna": "AB-020",
        "nombre": "Lenteja"
      },
      "existencia": 73,
      "minimo": 5,
      "reservado": 0,
      "disponible": 73,
      "estado": "normal",
      "actualizado_en": "2026-11-26T13:51:12-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 21,
        "clave_interna": "BE-001",
        "nombre": "Agua purificada"
      },
      "existencia": 0,
      "minimo": 10,
      "reservado": 0,
      "disponible": 0,
      "estado": "agotado",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 22,
        "clave_interna": "BE-002",
        "nombre": "Agua embotellada"
      },
      "existencia": 72,
      "minimo": 8,
      "reservado": 0,
      "disponible": 72,
      "estado": "normal",
      "actualizado_en": "2026-11-26T00:38:20-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 23,
        "clave_interna": "BE-003",
        "nombre": "Refresco de cola"
      },
      "existencia": 54,
      "minimo": 5,
      "reservado": 0,
      "disponible": 54,
      "estado": "normal",
      "actualizado_en": "2026-11-26T13:51:58-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 24,
        "clave_interna": "BE-004",
        "nombre": "Refresco sabor manzana"
      },
      "existencia": 39,
      "minimo": 5,
      "reservado": 0,
      "disponible": 39,
      "estado": "normal",
      "actualizado_en": "2026-11-26T14:19:27-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 25,
        "clave_interna": "BE-005",
        "nombre": "Jugo de naranja"
      },
      "existencia": 80,
      "minimo": 5,
      "reservado": 0,
      "disponible": 80,
      "estado": "normal",
      "actualizado_en": "2026-11-26T14:09:21-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 26,
        "clave_interna": "BE-006",
        "nombre": "Bebida de soya"
      },
      "existencia": 17,
      "minimo": 10,
      "reservado": 0,
      "disponible": 17,
      "estado": "normal",
      "actualizado_en": "2026-11-26T13:51:21-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 27,
        "clave_interna": "BE-007",
        "nombre": "Té helado de limón"
      },
      "existencia": 84,
      "minimo": 10,
      "reservado": 0,
      "disponible": 84,
      "estado": "normal",
      "actualizado_en": "2026-11-26T00:34:29-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 28,
        "clave_interna": "BE-008",
        "nombre": "Polvo para agua de sabor"
      },
      "existencia": 30,
      "minimo": 5,
      "reservado": 0,
      "disponible": 30,
      "estado": "normal",
      "actualizado_en": "2026-11-26T00:29:13-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 29,
        "clave_interna": "LA-001",
        "nombre": "Leche entera"
      },
      "existencia": 48,
      "minimo": 10,
      "reservado": 0,
      "disponible": 48,
      "estado": "normal",
      "actualizado_en": "2026-11-26T00:34:27-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 30,
        "clave_interna": "LA-002",
        "nombre": "Leche deslactosada"
      },
      "existencia": 12,
      "minimo": 5,
      "reservado": 0,
      "disponible": 12,
      "estado": "normal",
      "actualizado_en": "2026-11-26T14:19:27-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 31,
        "clave_interna": "LA-003",
        "nombre": "Queso fresco"
      },
      "existencia": 55,
      "minimo": 5,
      "reservado": 0,
      "disponible": 55,
      "estado": "normal",
      "actualizado_en": "2026-11-26T00:33:03-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 32,
        "clave_interna": "LA-004",
        "nombre": "Queso Oaxaca"
      },
      "existencia": 20,
      "minimo": 10,
      "reservado": 0,
      "disponible": 20,
      "estado": "normal",
      "actualizado_en": "2026-11-26T14:09:01-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 33,
        "clave_interna": "LA-005",
        "nombre": "Crema ácida"
      },
      "existencia": 82,
      "minimo": 5,
      "reservado": 0,
      "disponible": 82,
      "estado": "normal",
      "actualizado_en": "2026-11-26T00:38:20-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 34,
        "clave_interna": "LA-006",
        "nombre": "Yogur natural"
      },
      "existencia": 10,
      "minimo": 8,
      "reservado": 0,
      "disponible": 10,
      "estado": "normal",
      "actualizado_en": "2026-11-26T00:35:12-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 35,
        "clave_interna": "LA-007",
        "nombre": "Mantequilla"
      },
      "existencia": 64,
      "minimo": 8,
      "reservado": 0,
      "disponible": 64,
      "estado": "normal",
      "actualizado_en": "2026-11-26T14:09:01-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 36,
        "clave_interna": "LA-008",
        "nombre": "Jamón de pavo"
      },
      "existencia": 47,
      "minimo": 8,
      "reservado": 0,
      "disponible": 47,
      "estado": "normal",
      "actualizado_en": "2026-11-26T00:37:09-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 37,
        "clave_interna": "LI-001",
        "nombre": "Detergente en polvo"
      },
      "existencia": 13,
      "minimo": 5,
      "reservado": 0,
      "disponible": 13,
      "estado": "normal",
      "actualizado_en": "2026-11-26T14:09:01-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 38,
        "clave_interna": "LI-002",
        "nombre": "Jabón para trastes"
      },
      "existencia": 47,
      "minimo": 5,
      "reservado": 0,
      "disponible": 47,
      "estado": "normal",
      "actualizado_en": "2026-11-26T00:34:27-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 39,
        "clave_interna": "LI-003",
        "nombre": "Cloro"
      },
      "existencia": 44,
      "minimo": 10,
      "reservado": 0,
      "disponible": 44,
      "estado": "normal",
      "actualizado_en": "2026-11-26T13:51:58-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 40,
        "clave_interna": "LI-004",
        "nombre": "Limpiador multiusos"
      },
      "existencia": 14,
      "minimo": 8,
      "reservado": 0,
      "disponible": 14,
      "estado": "normal",
      "actualizado_en": "2026-11-26T14:19:27-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 41,
        "clave_interna": "LI-005",
        "nombre": "Suavizante de telas"
      },
      "existencia": 69,
      "minimo": 8,
      "reservado": 0,
      "disponible": 69,
      "estado": "normal",
      "actualizado_en": "2026-10-20T00:43:43-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 42,
        "clave_interna": "LI-006",
        "nombre": "Papel higiénico"
      },
      "existencia": 64,
      "minimo": 8,
      "reservado": 0,
      "disponible": 64,
      "estado": "normal",
      "actualizado_en": "2026-11-26T00:39:01-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 43,
        "clave_interna": "LI-007",
        "nombre": "Servilletas"
      },
      "existencia": 65,
      "minimo": 5,
      "reservado": 0,
      "disponible": 65,
      "estado": "normal",
      "actualizado_en": "2026-11-26T14:09:01-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 44,
        "clave_interna": "LI-008",
        "nombre": "Bolsas para basura"
      },
      "existencia": 26,
      "minimo": 5,
      "reservado": 0,
      "disponible": 26,
      "estado": "normal",
      "actualizado_en": "2026-11-25T16:05:48-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 45,
        "clave_interna": "LI-009",
        "nombre": "Fibra para trastes"
      },
      "existencia": 43,
      "minimo": 10,
      "reservado": 0,
      "disponible": 43,
      "estado": "normal",
      "actualizado_en": "2026-11-26T00:38:20-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 46,
        "clave_interna": "HI-001",
        "nombre": "Jabón de tocador"
      },
      "existencia": 63,
      "minimo": 5,
      "reservado": 0,
      "disponible": 63,
      "estado": "normal",
      "actualizado_en": "2026-11-26T00:38:20-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 47,
        "clave_interna": "HI-002",
        "nombre": "Shampoo"
      },
      "existencia": 60,
      "minimo": 10,
      "reservado": 0,
      "disponible": 60,
      "estado": "normal",
      "actualizado_en": "2026-11-26T00:36:24-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 48,
        "clave_interna": "HI-003",
        "nombre": "Pasta dental"
      },
      "existencia": 74,
      "minimo": 10,
      "reservado": 0,
      "disponible": 74,
      "estado": "normal",
      "actualizado_en": "2026-11-26T00:34:27-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 49,
        "clave_interna": "HI-004",
        "nombre": "Desodorante"
      },
      "existencia": 36,
      "minimo": 5,
      "reservado": 0,
      "disponible": 36,
      "estado": "normal",
      "actualizado_en": "2026-11-26T14:19:33-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 50,
        "clave_interna": "HI-005",
        "nombre": "Toallas femeninas"
      },
      "existencia": 76,
      "minimo": 8,
      "reservado": 0,
      "disponible": 76,
      "estado": "normal",
      "actualizado_en": "2026-11-26T00:34:30-06:00"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 51,
        "clave_interna": "HI-006",
        "nombre": "Pañal etapa 3"
      },
      "existencia": 29,
      "minimo": 10,
      "reservado": 0,
      "disponible": 29,
      "estado": "normal",
      "actualizado_en": "2026-11-26T00:38:20-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 100,
    "total": 51,
    "paginas": 1
  }
}
```

### INV-05 · El operador pide otro microhub · PASA

**Objetivo.** No puede consultar el inventario de otro microhub.

**Petición.** `GET http://inventario:5111/api/v1/inventario?microhub_id=2`

```http
Accept: application/json
X-Traza-Id: 12a16407-4e48-444b-9477-e78e04cb2d3e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 8 ms · traza `12a16407-4e48-444b-9477-e78e04cb2d3e`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "12a16407-4e48-444b-9477-e78e04cb2d3e"
  }
}
```

### INV-06 · Una existencia · PASA

**Objetivo.** Existencia, apartado y disponible de un producto en un microhub.

**Petición.** `GET http://inventario:5111/api/v1/inventario/1/6`

```http
Accept: application/json
X-Traza-Id: 5f962d55-fe58-4e5b-be3c-9c4b78dc3115
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 37 ms · traza `5f962d55-fe58-4e5b-be3c-9c4b78dc3115`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "producto": {
    "id": 6,
    "clave_interna": "AB-006",
    "nombre": "Harina de maíz nixtamalizado"
  },
  "existencia": 81,
  "minimo": 10,
  "reservado": 0,
  "disponible": 81,
  "estado": "normal",
  "actualizado_en": "2026-11-26T14:04:48-06:00"
}
```

### INV-07 · Recibir mercancía · PASA

**Objetivo.** Suma al inventario y deja el movimiento con la referencia.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: 5afd67ce-3404-4f0e-b578-42d3d4cc4844
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "producto_id": 6,
  "tipo": "recepcion",
  "cantidad": 5,
  "motivo": "Llegada de mercancía",
  "operacion_uuid": "169a6682-7e98-40a4-aca2-20c5a5dbfa48",
  "referencia": {
    "tipo": "orden_compra",
    "id": "1"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 93 ms · traza `5afd67ce-3404-4f0e-b578-42d3d4cc4844`

```json
{
  "movimiento": {
    "id": 2213,
    "microhub_id": 1,
    "producto_id": 6,
    "tipo": "recepcion",
    "cantidad": 5,
    "existencia_resultante": 86,
    "referencia": {
      "tipo": "orden_compra",
      "id": "1"
    },
    "motivo": "Llegada de mercancía",
    "usuario_id": 2,
    "fecha": "2026-11-26T14:19:37-06:00"
  },
  "duplicado": false
}
```

**Explicación.** Bloquea la fila del inventario, suma, y guarda el movimiento con la existencia resultante. La operacion_uuid hace el movimiento idempotente.

**Evidencia en PostgreSQL.** `SELECT id, tipo, cantidad, existencia_resultante, referencia_tipo, referencia_id, operacion_uuid FROM movimiento_inventario WHERE operacion_uuid = %s`

```json
[
  {
    "id": 2213,
    "tipo": "recepcion",
    "cantidad": 5,
    "existencia_resultante": 86,
    "referencia_tipo": "orden_compra",
    "referencia_id": 1,
    "operacion_uuid": "169a6682-7e98-40a4-aca2-20c5a5dbfa48"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT existencia FROM inventario WHERE microhub_id = %s AND producto_id = %s`

```json
[
  {
    "existencia": 86
  }
]
```

### INV-08 · Reintento con la misma operación · PASA

**Objetivo.** Idempotencia: la misma entrada no se aplica dos veces.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: 9695d86d-9723-48ea-b61b-a3c03993e463
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "producto_id": 6,
  "tipo": "recepcion",
  "cantidad": 5,
  "motivo": "Llegada de mercancía",
  "operacion_uuid": "169a6682-7e98-40a4-aca2-20c5a5dbfa48",
  "referencia": {
    "tipo": "orden_compra",
    "id": "1"
  }
}
```

**Respuesta.** HTTP 200 (esperado 200) · 39 ms · traza `9695d86d-9723-48ea-b61b-a3c03993e463`

```json
{
  "movimiento": {
    "id": 2213,
    "microhub_id": 1,
    "producto_id": 6,
    "tipo": "recepcion",
    "cantidad": 5,
    "existencia_resultante": 86,
    "referencia": {
      "tipo": "orden_compra",
      "id": "1"
    },
    "motivo": "Llegada de mercancía",
    "usuario_id": 2,
    "fecha": "2026-11-26T14:19:37-06:00"
  },
  "duplicado": true
}
```

**Evidencia en PostgreSQL.** `SELECT count(*) AS movimientos FROM movimiento_inventario WHERE operacion_uuid = %s`

```json
[
  {
    "movimientos": 1
  }
]
```

**Evidencia en PostgreSQL.** `SELECT existencia FROM inventario WHERE microhub_id = %s AND producto_id = %s`

```json
[
  {
    "existencia": 86
  }
]
```

### INV-09 · Ajuste sin motivo · PASA

**Objetivo.** Un ajuste, merma o conteo necesita el motivo.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: cc819c18-bcb1-4dc0-9ab9-d26e281f11e3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "producto_id": 6,
  "tipo": "ajuste",
  "cantidad": 1
}
```

**Respuesta.** HTTP 422 (esperado 422) · 8 ms · traza `cc819c18-bcb1-4dc0-9ab9-d26e281f11e3`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "motivo",
        "mensaje": "Una ajuste necesita el motivo."
      }
    ],
    "traza_id": "cc819c18-bcb1-4dc0-9ab9-d26e281f11e3"
  }
}
```

### INV-10 · Ajuste grande por un operador · PASA

**Objetivo.** Más de 25 unidades lo autoriza un administrador.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: 9b0b3cc3-4719-4c59-a453-d7a46d0cec3c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "producto_id": 6,
  "tipo": "ajuste",
  "cantidad": 30,
  "motivo": "Ajuste grande de prueba"
}
```

**Respuesta.** HTTP 403 (esperado 403) · 53 ms · traza `9b0b3cc3-4719-4c59-a453-d7a46d0cec3c`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Un movimiento de más de 25 unidades lo autoriza un administrador.",
    "traza_id": "9b0b3cc3-4719-4c59-a453-d7a46d0cec3c"
  }
}
```

**Explicación.** El umbral viene de configuracion.umbral_ajuste_inventario, no de una constante en el código.

### INV-11 · Ajuste grande por un administrador · PASA

**Objetivo.** El administrador sí puede.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: bcdbab55-23a1-42de-a69f-97690bded588
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "producto_id": 6,
  "tipo": "ajuste",
  "cantidad": 30,
  "motivo": "Ajuste grande de prueba"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 59 ms · traza `bcdbab55-23a1-42de-a69f-97690bded588`

```json
{
  "movimiento": {
    "id": 2214,
    "microhub_id": 1,
    "producto_id": 6,
    "tipo": "ajuste",
    "cantidad": 30,
    "existencia_resultante": 116,
    "referencia": null,
    "motivo": "Ajuste grande de prueba",
    "usuario_id": 1,
    "fecha": "2026-11-26T14:19:37-06:00"
  },
  "duplicado": false
}
```

**Evidencia en PostgreSQL.** `SELECT tipo, cantidad, existencia_resultante, motivo, usuario_id FROM movimiento_inventario WHERE id = %s`

```json
[
  {
    "tipo": "ajuste",
    "cantidad": 30,
    "existencia_resultante": 116,
    "motivo": "Ajuste grande de prueba",
    "usuario_id": 1
  }
]
```

### INV-12 · Transferencia entre microhubs · PASA

**Objetivo.** Resta del origen y suma al destino en una sola transacción.

**Petición.** `POST http://inventario:5111/api/v1/inventario/transferencias`

```http
Accept: application/json
X-Traza-Id: 0739fc40-d675-4de3-b340-d7372c107d96
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "origen_microhub_id": 1,
  "destino_microhub_id": 2,
  "producto_id": 7,
  "cantidad": 2,
  "motivo": "El microhub 2 se quedó sin producto",
  "operacion_uuid": "9ffb73f6-dfae-4b60-b98d-cb9d6b0ef857"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 92 ms · traza `0739fc40-d675-4de3-b340-d7372c107d96`

```json
{
  "producto_id": 7,
  "cantidad": 2,
  "duplicado": false,
  "origen": {
    "microhub_id": 1,
    "existencia": 12,
    "movimiento_id": 2217
  },
  "destino": {
    "microhub_id": 2,
    "existencia": 78,
    "movimiento_id": 2218
  }
}
```

**Explicación.** Bloquea las dos filas en orden de microhub (sin interbloqueos) y escribe dos movimientos enlazados.

**Evidencia en PostgreSQL.** `SELECT microhub_id, tipo, cantidad, existencia_resultante, referencia_tipo, referencia_id FROM movimiento_inventario WHERE operacion_uuid LIKE %s ORDER BY id`

```json
[
  {
    "microhub_id": 1,
    "tipo": "transferencia_salida",
    "cantidad": -2,
    "existencia_resultante": 12,
    "referencia_tipo": "transferencia",
    "referencia_id": 2
  },
  {
    "microhub_id": 2,
    "tipo": "transferencia_entrada",
    "cantidad": 2,
    "existencia_resultante": 78,
    "referencia_tipo": "transferencia",
    "referencia_id": 1
  }
]
```

### INV-13 · Transferir más de lo disponible · PASA

**Objetivo.** No se puede mandar lo que no hay.

**Petición.** `POST http://inventario:5111/api/v1/inventario/transferencias`

```http
Accept: application/json
X-Traza-Id: dd6df2e1-795f-4bcf-85c6-cc5e9b84931b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "origen_microhub_id": 1,
  "destino_microhub_id": 2,
  "producto_id": 7,
  "cantidad": 1014,
  "motivo": "El microhub 2 se quedó sin producto",
  "operacion_uuid": "1d3e8ca7-6114-464b-ac42-529f8d223b42"
}
```

**Respuesta.** HTTP 409 (esperado 409) · 72 ms · traza `dd6df2e1-795f-4bcf-85c6-cc5e9b84931b`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "En el microhub de origen hay 12 disponibles y se piden 1014.",
    "traza_id": "dd6df2e1-795f-4bcf-85c6-cc5e9b84931b"
  }
}
```

### INV-14 · Apartar existencia · PASA

**Objetivo.** Una reserva resta de lo disponible sin tocar la existencia física.

**Petición.** `POST http://inventario:5111/api/v1/inventario/reservas`

```http
Accept: application/json
X-Traza-Id: f3b670ea-3f30-4c16-8960-5b6c2770939f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "producto_id": 8,
  "cantidad": 3,
  "referencia": {
    "tipo": "manual",
    "id": "evidencia-fa7fde"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 91 ms · traza `f3b670ea-3f30-4c16-8960-5b6c2770939f`

```json
{
  "id": 18,
  "microhub_id": 1,
  "producto_id": 8,
  "cantidad": 3,
  "estado": "activa",
  "vigente": true,
  "referencia": {
    "tipo": "manual",
    "id": "evidencia-fa7fde"
  },
  "creada_en": "2026-11-26T14:19:38-06:00",
  "vence_en": "2026-11-26T14:49:38-06:00",
  "cerrada_en": null
}
```

**Evidencia en PostgreSQL.** `SELECT existencia, reservado, disponible FROM v_inventario_disponible WHERE microhub_id = %s AND producto_id = %s`

```json
[
  {
    "existencia": 21,
    "reservado": 3,
    "disponible": 18
  }
]
```

### INV-15 · Reservar más de lo disponible · PASA

**Objetivo.** Responde 409 si no alcanza.

**Petición.** `POST http://inventario:5111/api/v1/inventario/reservas`

```http
Accept: application/json
X-Traza-Id: 0137cfe6-d899-4675-9274-6b0ff770fc41
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "producto_id": 8,
  "cantidad": 121,
  "referencia": {
    "tipo": "manual",
    "id": "evidencia-fa7fde"
  }
}
```

**Respuesta.** HTTP 409 (esperado 409) · 49 ms · traza `0137cfe6-d899-4675-9274-6b0ff770fc41`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "No hay existencia disponible: hay 18 sin apartar y se piden 121.",
    "traza_id": "0137cfe6-d899-4675-9274-6b0ff770fc41"
  }
}
```

### INV-16 · Reservas activas · PASA

**Objetivo.** Filtro por producto, estado y referencia.

**Petición.** `GET http://inventario:5111/api/v1/inventario/reservas?producto_id=8&estado=activa&referencia_id=evidencia-fa7fde`

```http
Accept: application/json
X-Traza-Id: ed894342-0e94-4b02-811a-46e56cedba66
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 50 ms · traza `ed894342-0e94-4b02-811a-46e56cedba66`

```json
{
  "datos": [
    {
      "id": 18,
      "microhub_id": 1,
      "producto_id": 8,
      "cantidad": 3,
      "estado": "activa",
      "vigente": true,
      "referencia": {
        "tipo": "manual",
        "id": "evidencia-fa7fde"
      },
      "creada_en": "2026-11-26T14:19:38-06:00",
      "vence_en": "2026-11-26T14:49:38-06:00",
      "cerrada_en": null
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 1,
    "paginas": 1
  }
}
```

### INV-17 · Liberar una reserva · PASA

**Objetivo.** Lo apartado vuelve a estar disponible.

**Petición.** `POST http://inventario:5111/api/v1/inventario/reservas/18/liberar`

```http
Accept: application/json
X-Traza-Id: c4dfd3b4-7114-4816-a642-d34d6d156113
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 37 ms · traza `c4dfd3b4-7114-4816-a642-d34d6d156113`

```json
{
  "id": 18,
  "microhub_id": 1,
  "producto_id": 8,
  "cantidad": 3,
  "estado": "liberada",
  "vigente": false,
  "referencia": {
    "tipo": "manual",
    "id": "evidencia-fa7fde"
  },
  "creada_en": "2026-11-26T14:19:38-06:00",
  "vence_en": "2026-11-26T14:49:38-06:00",
  "cerrada_en": "2026-11-26T14:19:38-06:00"
}
```

**Evidencia en PostgreSQL.** `SELECT estado, cerrada_en IS NOT NULL AS cerrada FROM inventario_reserva WHERE id = %s`

```json
[
  {
    "estado": "liberada",
    "cerrada": true
  }
]
```

**Evidencia en PostgreSQL.** `SELECT existencia, reservado, disponible FROM v_inventario_disponible WHERE microhub_id = %s AND producto_id = %s`

```json
[
  {
    "existencia": 21,
    "reservado": 0,
    "disponible": 21
  }
]
```

### INV-18 · Cambiar el mínimo · PASA

**Objetivo.** Solo un administrador cambia el mínimo de un producto.

**Petición.** `PATCH http://inventario:5111/api/v1/inventario/1/9/minimo`

```http
Accept: application/json
X-Traza-Id: 5f6dc9b4-e2c9-4101-b52c-65699a98230d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "minimo": 41
}
```

**Respuesta.** HTTP 200 (esperado 200) · 100 ms · traza `5f6dc9b4-e2c9-4101-b52c-65699a98230d`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "producto": {
    "id": 9,
    "clave_interna": "AB-009",
    "nombre": "Atún en agua"
  },
  "existencia": 42,
  "minimo": 41,
  "reservado": 0,
  "disponible": 42,
  "estado": "normal",
  "actualizado_en": "2026-11-26T14:19:38-06:00"
}
```

**Evidencia en PostgreSQL.** `SELECT existencia, minimo FROM inventario WHERE microhub_id = %s AND producto_id = %s`

```json
[
  {
    "existencia": 42,
    "minimo": 41
  }
]
```

### INV-23 · Cambiar el mínimo con PUT · PASA

**Objetivo.** PUT es alias de PATCH: lo usa la app Android cuando la JVM no admite PATCH.

**Petición.** `PUT http://inventario:5111/api/v1/inventario/1/9/minimo`

```http
Accept: application/json
X-Traza-Id: 2ca88a59-d097-49ea-b97a-c7b3c7fa1f0f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "minimo": 41
}
```

**Respuesta.** HTTP 200 (esperado 200) · 158 ms · traza `2ca88a59-d097-49ea-b97a-c7b3c7fa1f0f`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "producto": {
    "id": 9,
    "clave_interna": "AB-009",
    "nombre": "Atún en agua"
  },
  "existencia": 42,
  "minimo": 41,
  "reservado": 0,
  "disponible": 42,
  "estado": "normal",
  "actualizado_en": "2026-11-26T14:19:39-06:00"
}
```

**Explicación.** Misma validación y misma auditoría que PATCH; el trigger registra quién cambió el mínimo.

**Evidencia en PostgreSQL.** `SELECT modulo, accion, entidad, valores_nuevos FROM auditoria WHERE entidad = 'inventario' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "modulo": "inventario",
    "accion": "modificacion",
    "entidad": "inventario",
    "valores_nuevos": {
      "actualizado_en": "2026-11-26T14:19:39.043821-06:00"
    }
  }
]
```

### INV-19 · El operador intenta cambiar el mínimo · PASA

**Objetivo.** Sin inventario.ajuste.

**Petición.** `PATCH http://inventario:5111/api/v1/inventario/1/9/minimo`

```http
Accept: application/json
X-Traza-Id: 77afbb39-94b9-41c7-9f5f-970eb9a76b59
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "minimo": 1
}
```

**Respuesta.** HTTP 403 (esperado 403) · 51 ms · traza `77afbb39-94b9-41c7-9f5f-970eb9a76b59`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "77afbb39-94b9-41c7-9f5f-970eb9a76b59"
  }
}
```

### INV-20 · Una merma cruza el mínimo · PASA

**Objetivo.** El trigger avisa del faltante al operador y al administrador.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: 7ddcf7bc-16d5-47a7-9397-c2a893a61bcf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "producto_id": 9,
  "tipo": "merma",
  "cantidad": 2,
  "motivo": "Se rompieron dos"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 105 ms · traza `7ddcf7bc-16d5-47a7-9397-c2a893a61bcf`

```json
{
  "movimiento": {
    "id": 2221,
    "microhub_id": 1,
    "producto_id": 9,
    "tipo": "merma",
    "cantidad": -2,
    "existencia_resultante": 40,
    "referencia": null,
    "motivo": "Se rompieron dos",
    "usuario_id": 1,
    "fecha": "2026-11-26T14:19:39-06:00"
  },
  "duplicado": false
}
```

**Explicación.** fn_notificar_faltante se dispara cuando la existencia pasa de arriba a abajo del mínimo; el aviso respeta las preferencias.

**Evidencia en PostgreSQL.** `SELECT destinatario_id, tipo, titulo, mensaje, referencia_tipo, referencia_id FROM web_notificacion WHERE tipo = 'inventario' AND referencia_id = %s ORDER BY id DESC LIMIT 2`

```json
[
  {
    "destinatario_id": 1,
    "tipo": "inventario",
    "titulo": "Faltante en Microhub San Bernabé Centro",
    "mensaje": "Atún en agua: quedan 40 (mínimo 41).",
    "referencia_tipo": "producto",
    "referencia_id": "9"
  },
  {
    "destinatario_id": 2,
    "tipo": "inventario",
    "titulo": "Faltante en Microhub San Bernabé Centro",
    "mensaje": "Atún en agua: quedan 40 (mínimo 41).",
    "referencia_tipo": "producto",
    "referencia_id": "9"
  }
]
```

### INV-21 · Alertas de faltantes · PASA

**Objetivo.** Productos agotados o bajo su mínimo, los más graves primero.

**Petición.** `GET http://inventario:5111/api/v1/inventario/alertas?microhub_id=1&por_pagina=100`

```http
Accept: application/json
X-Traza-Id: 1a061c5b-f184-4c7c-9d88-954256d415ad
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 77 ms · traza `1a061c5b-f184-4c7c-9d88-954256d415ad`

```json
{
  "datos": [
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 21,
        "clave_interna": "BE-001",
        "nombre": "Agua purificada"
      },
      "existencia": 0,
      "minimo": 10,
      "disponible": 0,
      "faltante": 10,
      "severidad": "agotado"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 9,
        "clave_interna": "AB-009",
        "nombre": "Atún en agua"
      },
      "existencia": 40,
      "minimo": 41,
      "disponible": 40,
      "faltante": 1,
      "severidad": "baja"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 100,
    "total": 2,
    "paginas": 1
  }
}
```

### INV-22 · Movimientos de un producto · PASA

**Objetivo.** Bitácora del producto con sus referencias.

**Petición.** `GET http://inventario:5111/api/v1/inventario/movimientos?microhub_id=1&producto_id=6&tipo=recepcion`

```http
Accept: application/json
X-Traza-Id: 9f1b5a03-4157-4c01-a589-d7dd3eeab255
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 50 ms · traza `9f1b5a03-4157-4c01-a589-d7dd3eeab255`

```json
{
  "datos": [
    {
      "id": 2213,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 5,
      "existencia_resultante": 86,
      "referencia": {
        "tipo": "orden_compra",
        "id": "1"
      },
      "motivo": "Llegada de mercancía",
      "usuario_id": 2,
      "fecha": "2026-11-26T14:19:37-06:00"
    },
    {
      "id": 2172,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 5,
      "existencia_resultante": 86,
      "referencia": {
        "tipo": "orden_compra",
        "id": "1"
      },
      "motivo": "Llegada de mercancía",
      "usuario_id": 2,
      "fecha": "2026-11-26T14:04:47-06:00"
    },
    {
      "id": 2122,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 5,
      "existencia_resultante": 86,
      "referencia": {
        "tipo": "orden_compra",
        "id": "1"
      },
      "motivo": "Llegada de mercancía",
      "usuario_id": 2,
      "fecha": "2026-11-26T13:51:25-06:00"
    },
    {
      "id": 1896,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 5,
      "existencia_resultante": 79,
      "referencia": {
        "tipo": "orden_compra",
        "id": "1"
      },
      "motivo": "Prueba de recepción",
      "usuario_id": 2,
      "fecha": "2026-11-26T00:31:39-06:00"
    },
    {
      "id": 1894,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 3,
      "existencia_resultante": 77,
      "referencia": null,
      "motivo": "Prueba XML",
      "usuario_id": 2,
      "fecha": "2026-11-26T00:31:38-06:00"
    },
    {
      "id": 1655,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 5,
      "existencia_resultante": 76,
      "referencia": {
        "tipo": "orden_compra",
        "id": "1"
      },
      "motivo": "Prueba de recepción",
      "usuario_id": 2,
      "fecha": "2026-10-20T08:13:27-06:00"
    },
    {
      "id": 1653,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 3,
      "existencia_resultante": 74,
      "referencia": null,
      "motivo": "Prueba XML",
      "usuario_id": 2,
      "fecha": "2026-10-20T08:13:27-06:00"
    },
    {
      "id": 1514,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 5,
      "existencia_resultante": 71,
      "referencia": {
        "tipo": "orden_compra",
        "id": "1"
      },
      "motivo": "Prueba de recepción",
      "usuario_id": 2,
      "fecha": "2026-10-20T00:49:55-06:00"
    },
    {
      "id": 1512,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 3,
      "existencia_resultante": 69,
      "referencia": null,
      "motivo": "Prueba XML",
      "usuario_id": 2,
      "fecha": "2026-10-20T00:49:55-06:00"
    },
    {
      "id": 1465,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 5,
      "existencia_resultante": 71,
      "referencia": {
        "tipo": "orden_compra",
        "id": "1"
      },
      "motivo": "Llegada de mercancía",
      "usuario_id": 2,
      "fecha": "2026-10-20T00:43:14-06:00"
    },
    {
      "id": 1400,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 5,
      "existencia_resultante": 71,
      "referencia": {
        "tipo": "orden_compra",
        "id": "1"
      },
      "motivo": "Llegada de mercancía",
      "usuario_id": 2,
      "fecha": "2026-10-20T00:32:28-06:00"
    },
    {
      "id": 1165,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 5,
      "existencia_resultante": 69,
      "referencia": {
        "tipo": "orden_compra",
        "id": "1"
      },
      "motivo": "Llegada de mercancía",
      "usuario_id": 2,
      "fecha": "2026-10-20T00:29:37-06:00"
    },
    {
      "id": 1047,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 5,
      "existencia_resultante": 69,
      "referencia": {
        "tipo": "orden_compra",
        "id": "1"
      },
      "motivo": "Llegada de mercancía",
      "usuario_id": 2,
      "fecha": "2026-10-20T00:21:38-06:00"
    },
    {
      "id": 1030,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 5,
      "existencia_resultante": 69,
      "referencia": {
        "tipo": "orden_compra",
        "id": "1"
      },
      "motivo": "Llegada de mercancía",
      "usuario_id": 2,
      "fecha": "2026-10-20T00:20:31-06:00"
    },
    {
      "id": 1015,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 5,
      "existencia_resultante": 64,
      "referencia": {
        "tipo": "orden_compra",
        "id": "1"
      },
      "motivo": "Prueba de recepción",
      "usuario_id": 2,
      "fecha": "2026-10-20T00:16:27-06:00"
    },
    {
      "id": 1013,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 3,
      "existencia_resultante": 62,
      "referencia": null,
      "motivo": "Prueba XML",
      "usuario_id": 2,
      "fecha": "2026-10-20T00:16:26-06:00"
    },
    {
      "id": 919,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 5,
      "existencia_resultante": 61,
      "referencia": {
        "tipo": "orden_compra",
        "id": "1"
      },
      "motivo": "Prueba de recepción",
      "usuario_id": 2,
      "fecha": "2026-10-19T19:32:40-06:00"
    },
    {
      "id": 917,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 3,
      "existencia_resultante": 59,
      "referencia": null,
      "motivo": "Prueba XML",
      "usuario_id": 2,
      "fecha": "2026-10-19T19:32:40-06:00"
    },
    {
      "id": 898,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 5,
      "existencia_resultante": 61,
      "referencia": {
        "tipo": "orden_compra",
        "id": "1"
      },
      "motivo": "Llegada de mercancía",
      "usuario_id": 2,
      "fecha": "2026-10-19T19:31:31-06:00"
    },
    {
      "id": 6,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 60,
      "existencia_resultante": 60,
      "referencia": {
        "tipo": "carga_inicial",
        "id": "None"
      },
      "motivo": "Carga inicial de semilla",
      "usuario_id": null,
      "fecha": "2026-10-19T19:30:40-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 20,
    "paginas": 1
  }
}
```

## Servicio notificaciones · puerto 5124

### NOT-01 · Enviar un aviso a todo un rol · PASA

**Objetivo.** El administrador avisa a los operadores de un microhub.

**Petición.** `POST http://notificaciones:5124/api/v1/notificaciones`

```http
Accept: application/json
X-Traza-Id: 55c4271d-9198-4937-88a0-19dd13de70d8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "rol": "operador",
  "microhub_id": 1,
  "tipo": "sistema",
  "titulo": "Evidencia c14386",
  "mensaje": "Aviso de prueba para el microhub 1",
  "referencia": {
    "tipo": "sistema",
    "id": "evidencia"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 50 ms · traza `55c4271d-9198-4937-88a0-19dd13de70d8`

```json
{
  "enviadas": 1,
  "omitidas": 0,
  "ids": [
    751
  ]
}
```

**Evidencia en PostgreSQL.** `SELECT destinatario_id, emisor_id, tipo, titulo, referencia_tipo, referencia_id FROM web_notificacion WHERE titulo = %s`

```json
[
  {
    "destinatario_id": 2,
    "emisor_id": 1,
    "tipo": "sistema",
    "titulo": "Evidencia c14386",
    "referencia_tipo": "sistema",
    "referencia_id": "evidencia"
  }
]
```

### NOT-02 · Operador intenta enviar un aviso · PASA

**Objetivo.** Sin notificaciones.crear.

**Petición.** `POST http://notificaciones:5124/api/v1/notificaciones`

```http
Accept: application/json
X-Traza-Id: a0f47232-7b5d-4848-8218-0b37ad97f223
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "rol": "operador",
  "tipo": "sistema",
  "titulo": "x",
  "mensaje": "x"
}
```

**Respuesta.** HTTP 403 (esperado 403) · 32 ms · traza `a0f47232-7b5d-4848-8218-0b37ad97f223`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "a0f47232-7b5d-4848-8218-0b37ad97f223"
  }
}
```

### NOT-03 · Destino inexistente · PASA

**Objetivo.** Un rol sin personas activas se rechaza.

**Petición.** `POST http://notificaciones:5124/api/v1/notificaciones`

```http
Accept: application/json
X-Traza-Id: bbc66fd2-7071-4e0a-a1bc-192e0dba021d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "rol": "no_existe",
  "tipo": "sistema",
  "titulo": "x",
  "mensaje": "x"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 33 ms · traza `bbc66fd2-7071-4e0a-a1bc-192e0dba021d`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "rol",
        "mensaje": "No hay personas activas con ese destino."
      }
    ],
    "traza_id": "bbc66fd2-7071-4e0a-a1bc-192e0dba021d"
  }
}
```

### NOT-04 · Mi bandeja · PASA

**Objetivo.** Los avisos de la persona, el más reciente primero.

**Petición.** `GET http://notificaciones:5124/api/v1/notificaciones?solo_no_leidas=true&por_pagina=20`

```http
Accept: application/json
X-Traza-Id: 758e6f29-8e85-408e-87d5-5d6879ef74f2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 82 ms · traza `758e6f29-8e85-408e-87d5-5d6879ef74f2`

```json
{
  "datos": [
    {
      "id": 751,
      "tipo": "sistema",
      "titulo": "Evidencia c14386",
      "mensaje": "Aviso de prueba para el microhub 1",
      "leida": false,
      "referencia": {
        "tipo": "sistema",
        "id": "evidencia"
      },
      "creada_en": "2026-11-26T14:19:39-06:00"
    },
    {
      "id": 749,
      "tipo": "inventario",
      "titulo": "Faltante en Microhub San Bernabé Centro",
      "mensaje": "Atún en agua: quedan 40 (mínimo 41).",
      "leida": false,
      "referencia": {
        "tipo": "producto",
        "id": "9"
      },
      "creada_en": "2026-11-26T14:19:39-06:00"
    },
    {
      "id": 736,
      "tipo": "abastecimiento",
      "titulo": "Orden de compra OC-20261126-000032",
      "mensaje": "La orden quedó cancelada.",
      "leida": false,
      "referencia": {
        "tipo": "orden",
        "id": "32"
      },
      "creada_en": "2026-11-26T14:04:59-06:00"
    },
    {
      "id": 735,
      "tipo": "abastecimiento",
      "titulo": "Solicitud de compra SC-20261126-000052",
      "mensaje": "Tu solicitud fue aprobada.",
      "leida": false,
      "referencia": {
        "tipo": "solicitud",
        "id": "52"
      },
      "creada_en": "2026-11-26T14:04:58-06:00"
    },
    {
      "id": 732,
      "tipo": "abastecimiento",
      "titulo": "Orden de compra OC-20261126-000031",
      "mensaje": "La orden quedó recibida.",
      "leida": false,
      "referencia": {
        "tipo": "orden",
        "id": "31"
      },
      "creada_en": "2026-11-26T14:04:58-06:00"
    },
    {
      "id": 731,
      "tipo": "abastecimiento",
      "titulo": "Solicitud de compra SC-20261126-000051",
      "mensaje": "Tu solicitud fue aprobada.",
      "leida": false,
      "referencia": {
        "tipo": "solicitud",
        "id": "51"
      },
      "creada_en": "2026-11-26T14:04:56-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 6,
    "paginas": 1
  }
}
```

### NOT-05 · Mi bandeja (XML) · PASA

**Objetivo.** Respuesta XML que cumple notificaciones.xsd.

**Petición.** `GET http://notificaciones:5124/api/v1/notificaciones?por_pagina=3`

```http
Accept: application/xml
X-Traza-Id: 3a1b94f4-cbed-4f25-a193-de0046fd6e0b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 45 ms · traza `3a1b94f4-cbed-4f25-a193-de0046fd6e0b`

```xml
<?xml version='1.0' encoding='utf-8'?>
<notificaciones xmlns="urn:microhubs:v1" version="1"><datos><notificacion><id>751</id><tipo>sistema</tipo><titulo>Evidencia c14386</titulo><mensaje>Aviso de prueba para el microhub 1</mensaje><leida>false</leida><referencia><tipo>sistema</tipo><id>evidencia</id></referencia><creada_en>2026-11-26T14:19:39-06:00</creada_en></notificacion><notificacion><id>749</id><tipo>inventario</tipo><titulo>Faltante en Microhub San Bernabé Centro</titulo><mensaje>Atún en agua: quedan 40 (mínimo 41).</mensaje><leida>false</leida><referencia><tipo>producto</tipo><id>9</id></referencia><creada_en>2026-11-26T14:19:39-06:00</creada_en></notificacion><notificacion><id>736</id><tipo>abastecimiento</tipo><titulo>Orden de compra OC-20261126-000032</titulo><mensaje>La orden quedó cancelada.</mensaje><leida>false</leida><referencia><tipo>orden</tipo><id>32</id></referencia><creada_en>2026-11-26T14:04:59-06:00</creada_en></notificacion></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>119</total><paginas>40</paginas></paginacion></notificaciones>
```

### NOT-06 · Avisos sin leer · PASA

**Objetivo.** Conteo para la insignia de la app.

**Petición.** `GET http://notificaciones:5124/api/v1/notificaciones/conteo`

```http
Accept: application/json
X-Traza-Id: 84fe687b-26dd-4f36-95fb-fb1dbc6f0e1d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 60 ms · traza `84fe687b-26dd-4f36-95fb-fb1dbc6f0e1d`

```json
{
  "no_leidas": 6
}
```

### NOT-07 · Confirmar la lectura · PASA

**Objetivo.** El aviso queda leído.

**Petición.** `POST http://notificaciones:5124/api/v1/notificaciones/751/leer`

```http
Accept: application/json
X-Traza-Id: 2a0f9159-ca06-4c5b-895e-1f433a6dd98f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 26 ms · traza `2a0f9159-ca06-4c5b-895e-1f433a6dd98f`

```json
{
  "id": 751,
  "tipo": "sistema",
  "titulo": "Evidencia c14386",
  "mensaje": "Aviso de prueba para el microhub 1",
  "leida": true,
  "referencia": {
    "tipo": "sistema",
    "id": "evidencia"
  },
  "creada_en": "2026-11-26T14:19:39-06:00"
}
```

**Evidencia en PostgreSQL.** `SELECT id, leido_en IS NOT NULL AS leido FROM web_notificacion WHERE id = %s`

```json
[
  {
    "id": 751,
    "leido": true
  }
]
```

### NOT-08 · Leído por otra persona · PASA

**Objetivo.** Un aviso ajeno no se puede marcar.

**Petición.** `POST http://notificaciones:5124/api/v1/notificaciones/751/leer`

```http
Accept: application/json
X-Traza-Id: efb1ec87-3383-41f0-b83d-0b9737ffdbfa
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 28 ms · traza `efb1ec87-3383-41f0-b83d-0b9737ffdbfa`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe ese aviso en tu bandeja.",
    "traza_id": "efb1ec87-3383-41f0-b83d-0b9737ffdbfa"
  }
}
```

### NOT-09 · Marcar todos como leídos · PASA

**Objetivo.** Confirma la lectura de todos los pendientes.

**Petición.** `POST http://notificaciones:5124/api/v1/notificaciones/leer-todas`

```http
Accept: application/json
X-Traza-Id: 88f3656b-5a88-439d-83c8-1c21583daa20
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 29 ms · traza `88f3656b-5a88-439d-83c8-1c21583daa20`

```json
{
  "marcadas": 5
}
```

### NOT-10 · Mis preferencias · PASA

**Objetivo.** Qué tipos de aviso recibe la persona.

**Petición.** `GET http://notificaciones:5124/api/v1/notificaciones/preferencias`

```http
Accept: application/json
X-Traza-Id: b262f27e-c861-4611-867f-6a31f6cab703
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 27 ms · traza `b262f27e-c861-4611-867f-6a31f6cab703`

```json
{
  "datos": [
    {
      "tipo": "pedido",
      "activa": true
    },
    {
      "tipo": "entrega",
      "activa": true
    },
    {
      "tipo": "planeacion",
      "activa": true
    },
    {
      "tipo": "inventario",
      "activa": true
    },
    {
      "tipo": "abastecimiento",
      "activa": true
    }
  ]
}
```

### NOT-11 · Apagar un tipo de aviso · PASA

**Objetivo.** El operador deja de recibir avisos de inventario.

**Petición.** `PUT http://notificaciones:5124/api/v1/notificaciones/preferencias/inventario`

```http
Accept: application/json
X-Traza-Id: ba64f65d-302d-4e5a-818f-dccd6f86f99d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "activa": false
}
```

**Respuesta.** HTTP 200 (esperado 200) · 37 ms · traza `ba64f65d-302d-4e5a-818f-dccd6f86f99d`

```json
{
  "tipo": "inventario",
  "activa": false
}
```

**Evidencia en PostgreSQL.** `SELECT usuario_id, tipo, activa FROM notificacion_preferencia WHERE usuario_id = %s`

```json
[
  {
    "usuario_id": 2,
    "tipo": "inventario",
    "activa": false
  }
]
```

### NOT-12 · Aviso omitido por preferencia · PASA

**Objetivo.** Quien apagó el tipo no lo recibe y se cuenta como omitido.

**Petición.** `POST http://notificaciones:5124/api/v1/notificaciones`

```http
Accept: application/json
X-Traza-Id: 21157c2a-7b18-4ae6-b23d-7be8e05fd7f1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "rol": "operador",
  "microhub_id": 1,
  "tipo": "inventario",
  "titulo": "Evidencia c14386",
  "mensaje": "Faltante de prueba"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 37 ms · traza `21157c2a-7b18-4ae6-b23d-7be8e05fd7f1`

```json
{
  "enviadas": 0,
  "omitidas": 1,
  "ids": []
}
```

### NOT-13 · Los avisos del sistema no se apagan · PASA

**Objetivo.** El tipo sistema siempre llega.

**Petición.** `PUT http://notificaciones:5124/api/v1/notificaciones/preferencias/sistema`

```http
Accept: application/json
X-Traza-Id: bc11a2b9-7ce2-463f-bc8a-74ce17237b15
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "activa": false
}
```

**Respuesta.** HTTP 409 (esperado 409) · 6 ms · traza `bc11a2b9-7ce2-463f-bc8a-74ce17237b15`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Los avisos del sistema no se pueden apagar.",
    "traza_id": "bc11a2b9-7ce2-463f-bc8a-74ce17237b15"
  }
}
```

### NOT-14 · Borrar un aviso · PASA

**Objetivo.** Quita el aviso de la bandeja propia.

**Petición.** `DELETE http://notificaciones:5124/api/v1/notificaciones/751`

```http
Accept: application/json
X-Traza-Id: 59908844-3930-4ead-950b-16f896c79ada
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 25 ms · traza `59908844-3930-4ead-950b-16f896c79ada`

```json
(sin cuerpo)
```

## Servicio proveedores · puerto 5113

### PRV-01 · Proveedores · PASA

**Objetivo.** Lista con cobertura y calificación.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores?por_pagina=10`

```http
Accept: application/json
X-Traza-Id: b61b195c-5db3-4106-ba29-473cd5b26c2a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 50 ms · traza `b61b195c-5db3-4106-ba29-473cd5b26c2a`

```json
{
  "datos": [
    {
      "id": 1,
      "clave": "********",
      "nombre": "Abarrotes del Norte",
      "contacto": "Rosa Garza",
      "correo": "ventas@abarrotesdelnorte.example",
      "telefono": "8181000101",
      "dias_entrega": 2,
      "pedido_minimo": 800.0,
      "condiciones_pago": "Contado",
      "estatus": "activo",
      "zonas": [
        1,
        2,
        3,
        4
      ],
      "calificacion": 4.0,
      "evaluaciones": 1
    },
    {
      "id": 2,
      "clave": "********",
      "nombre": "Distribuidora Regia",
      "contacto": "Luis Treviño",
      "correo": "pedidos@distregia.example",
      "telefono": "8181000102",
      "dias_entrega": 1,
      "pedido_minimo": 500.0,
      "condiciones_pago": "Crédito a 7 días",
      "estatus": "activo",
      "zonas": [
        1,
        2,
        3,
        4
      ],
      "calificacion": 4.0,
      "evaluaciones": 1
    },
    {
      "id": 3,
      "clave": "********",
      "nombre": "Mayorista San Nicolás",
      "contacto": "Elena Cantú",
      "correo": "compras@mayoristasn.example",
      "telefono": "8181000103",
      "dias_entrega": 4,
      "pedido_minimo": 1500.0,
      "condiciones_pago": "Crédito a 15 días",
      "estatus": "activo",
      "zonas": [
        1,
        2,
        3,
        4
      ],
      "calificacion": 4.0,
      "evaluaciones": 1
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 10,
    "total": 3,
    "paginas": 1
  }
}
```

### PRV-02 · Proveedores (XML) · PASA

**Objetivo.** Respuesta XML que cumple proveedores.xsd.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores?por_pagina=3`

```http
Accept: application/xml
X-Traza-Id: 1bd1e42a-e9ee-431b-8a00-cefb66c00afd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 68 ms · traza `1bd1e42a-e9ee-431b-8a00-cefb66c00afd`

```xml
<?xml version='1.0' encoding='utf-8'?>
<proveedores xmlns="urn:microhubs:v1" version="1"><datos><proveedor><id>1</id><clave>PV-01</clave><nombre>Abarrotes del Norte</nombre><contacto>Rosa Garza</contacto><correo>ventas@abarrotesdelnorte.example</correo><telefono>8181000101</telefono><dias_entrega>2</dias_entrega><pedido_minimo>800.00</pedido_minimo><condiciones_pago>Contado</condiciones_pago><estatus>activo</estatus><zonas><zona_id>1</zona_id><zona_id>2</zona_id><zona_id>3</zona_id><zona_id>4</zona_id></zonas><calificacion>4</calificacion><evaluaciones>1</evaluaciones></proveedor><proveedor><id>2</id><clave>PV-02</clave><nombre>Distribuidora Regia</nombre><contacto>Luis Treviño</contacto><correo>pedidos@distregia.example</correo><telefono>8181000102</telefono><dias_entrega>1</dias_entrega><pedido_minimo>500.00</pedido_minimo><condiciones_pago>Crédito a 7 días</condiciones_pago><estatus>activo</estatus><zonas><zona_id>1</zona_id><zona_id>2</zona_id><zona_id>3</zona_id><zona_id>4</zona_id></zonas><calificacion>4</calificacion><evaluaciones>1</evaluaciones></proveedor><proveedor><id>3</id><clave>PV-03</clave><nombre>Mayorista San Nicolás</nombre><contacto>Elena Cantú</contacto><correo>compras@mayoristasn.example</correo><telefono>8181000103</telefono><dias_entrega>4</dias_entrega><pedido_minimo>1500.00</pedido_minimo><condiciones_pago>Crédito a 15 días</condiciones_pago><estatus>activo</estatus><zonas><zona_id>1</zona_id><zona_id>2</zona_id><zona_id>3</zona_id><zona_id>4</zona_id></zonas><calificacion>4</calificacion><evaluaciones>1</evaluaciones></proveedor></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>3</total><paginas>1</paginas></paginacion></proveedores>
```

### PRV-03 · Un cliente intenta ver proveedores · PASA

**Objetivo.** El perfil cliente no tiene proveedores.ver.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores`

```http
Accept: application/json
X-Traza-Id: 4d9bcc13-796b-4e7e-899a-4e009f56f09f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 37 ms · traza `4d9bcc13-796b-4e7e-899a-4e009f56f09f`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "4d9bcc13-796b-4e7e-899a-4e009f56f09f"
  }
}
```

### PRV-04 · Un proveedor · PASA

**Objetivo.** Con las zonas que cubre y su calificación.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/2`

```http
Accept: application/json
X-Traza-Id: 5dd288b2-c0ad-414d-b40d-08d256168765
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 65 ms · traza `5dd288b2-c0ad-414d-b40d-08d256168765`

```json
{
  "id": 2,
  "clave": "********",
  "nombre": "Distribuidora Regia",
  "contacto": "Luis Treviño",
  "correo": "pedidos@distregia.example",
  "telefono": "8181000102",
  "dias_entrega": 1,
  "pedido_minimo": 500.0,
  "condiciones_pago": "Crédito a 7 días",
  "estatus": "activo",
  "zonas": [
    1,
    2,
    3,
    4
  ],
  "calificacion": 4.0,
  "evaluaciones": 1
}
```

### PRV-05 · Dar de alta un proveedor · PASA

**Objetivo.** Alta con su cobertura por zonas.

**Petición.** `POST http://proveedores:5113/api/v1/proveedores`

```http
Accept: application/json
X-Traza-Id: 4e485473-fc6b-472f-9966-c22c6ace98dd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "clave": "********",
  "nombre": "Proveedor de evidencias",
  "contacto": "Ana Prueba",
  "correo": "ana@prueba.example",
  "telefono": "8180000000",
  "dias_entrega": 3,
  "pedido_minimo": 250.0,
  "condiciones_pago": "Contado",
  "zonas": [
    1,
    2
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 128 ms · traza `4e485473-fc6b-472f-9966-c22c6ace98dd`

```json
{
  "id": 72,
  "clave": "********",
  "nombre": "Proveedor de evidencias",
  "contacto": "Ana Prueba",
  "correo": "ana@prueba.example",
  "telefono": "8180000000",
  "dias_entrega": 3,
  "pedido_minimo": 250.0,
  "condiciones_pago": "Contado",
  "estatus": "activo",
  "zonas": [
    1,
    2
  ],
  "calificacion": null,
  "evaluaciones": 0
}
```

**Evidencia en PostgreSQL.** `SELECT p.id, p.clave, p.dias_entrega, p.pedido_minimo, array_agg(z.zona_id ORDER BY z.zona_id) AS zonas FROM proveedor p JOIN proveedor_zona z ON z.proveedor_id = p.id WHERE p.clave = %s GROUP BY p.id`

```json
[
  {
    "id": 72,
    "clave": "EV-4933AB",
    "dias_entrega": 3,
    "pedido_minimo": "250.00",
    "zonas": [
      1,
      2
    ]
  }
]
```

**Evidencia en PostgreSQL.** `SELECT modulo, accion, entidad FROM auditoria WHERE entidad = 'proveedor' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "modulo": "proveedores",
    "accion": "alta",
    "entidad": "proveedor"
  }
]
```

### PRV-06 · Clave repetida · PASA

**Objetivo.** Dos proveedores no comparten clave.

**Petición.** `POST http://proveedores:5113/api/v1/proveedores`

```http
Accept: application/json
X-Traza-Id: b40f98fc-459e-46ed-b4cd-7c9aa4dca511
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "clave": "********",
  "nombre": "Proveedor de evidencias",
  "contacto": "Ana Prueba",
  "correo": "ana@prueba.example",
  "telefono": "8180000000",
  "dias_entrega": 3,
  "pedido_minimo": 250.0,
  "condiciones_pago": "Contado",
  "zonas": [
    1,
    2
  ]
}
```

**Respuesta.** HTTP 409 (esperado 409) · 28 ms · traza `b40f98fc-459e-46ed-b4cd-7c9aa4dca511`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Ya existe un proveedor con la clave EV-4933AB.",
    "traza_id": "b40f98fc-459e-46ed-b4cd-7c9aa4dca511"
  }
}
```

### PRV-07 · Correo inválido · PASA

**Objetivo.** Validación con detalle por campo.

**Petición.** `POST http://proveedores:5113/api/v1/proveedores`

```http
Accept: application/json
X-Traza-Id: 8d0e1233-b2d8-435d-b4ab-4417ee1a32a8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "clave": "********",
  "nombre": "Proveedor de evidencias",
  "contacto": "Ana Prueba",
  "correo": "sin-arroba",
  "telefono": "8180000000",
  "dias_entrega": 3,
  "pedido_minimo": 250.0,
  "condiciones_pago": "Contado",
  "zonas": [
    1,
    2
  ]
}
```

**Respuesta.** HTTP 422 (esperado 422) · 52 ms · traza `8d0e1233-b2d8-435d-b4ab-4417ee1a32a8`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "correo",
        "mensaje": "Debe ser un correo válido."
      }
    ],
    "traza_id": "8d0e1233-b2d8-435d-b4ab-4417ee1a32a8"
  }
}
```

### PRV-08 · Un planeador intenta dar de alta · PASA

**Objetivo.** Sin proveedores.editar.

**Petición.** `POST http://proveedores:5113/api/v1/proveedores`

```http
Accept: application/json
X-Traza-Id: 47a763ca-b585-4614-a4d4-23c627089eef
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "clave": "********",
  "nombre": "Proveedor de evidencias",
  "contacto": "Ana Prueba",
  "correo": "ana@prueba.example",
  "telefono": "8180000000",
  "dias_entrega": 3,
  "pedido_minimo": 250.0,
  "condiciones_pago": "Contado",
  "zonas": [
    1,
    2
  ]
}
```

**Respuesta.** HTTP 403 (esperado 403) · 28 ms · traza `47a763ca-b585-4614-a4d4-23c627089eef`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "47a763ca-b585-4614-a4d4-23c627089eef"
  }
}
```

### PRV-09 · Modificar un proveedor · PASA

**Objetivo.** Cambia el plazo y la cobertura; la clave no se toca.

**Petición.** `PUT http://proveedores:5113/api/v1/proveedores/72`

```http
Accept: application/json
X-Traza-Id: 58fd798f-fe4d-471c-8a51-dddcbf35b8ea
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "dias_entrega": 5,
  "zonas": [
    3
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 91 ms · traza `58fd798f-fe4d-471c-8a51-dddcbf35b8ea`

```json
{
  "id": 72,
  "clave": "********",
  "nombre": "Proveedor de evidencias",
  "contacto": "Ana Prueba",
  "correo": "ana@prueba.example",
  "telefono": "8180000000",
  "dias_entrega": 5,
  "pedido_minimo": 250.0,
  "condiciones_pago": "Contado",
  "estatus": "activo",
  "zonas": [
    3
  ],
  "calificacion": null,
  "evaluaciones": 0
}
```

### PRV-21 · Corregir un dato con PATCH · PASA

**Objetivo.** PATCH cambia solo los campos enviados; también acepta PUT.

**Petición.** `PATCH http://proveedores:5113/api/v1/proveedores/72`

```http
Accept: application/json
X-Traza-Id: 25a5aa9b-8a80-487b-8738-f0f60c78b57a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "contacto": "Luis Prueba"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 84 ms · traza `25a5aa9b-8a80-487b-8738-f0f60c78b57a`

```json
{
  "id": 72,
  "clave": "********",
  "nombre": "Proveedor de evidencias",
  "contacto": "Luis Prueba",
  "correo": "ana@prueba.example",
  "telefono": "8180000000",
  "dias_entrega": 5,
  "pedido_minimo": 250.0,
  "condiciones_pago": "Contado",
  "estatus": "activo",
  "zonas": [
    3
  ],
  "calificacion": null,
  "evaluaciones": 0
}
```

**Evidencia en PostgreSQL.** `SELECT clave, contacto, dias_entrega FROM proveedor WHERE id = %s`

```json
[
  {
    "clave": "EV-4933AB",
    "contacto": "Luis Prueba",
    "dias_entrega": 5
  }
]
```

### PRV-10 · Fijar una oferta · PASA

**Objetivo.** Alta del precio de compra de un producto.

**Petición.** `PUT http://proveedores:5113/api/v1/proveedores/72/catalogo/6`

```http
Accept: application/json
X-Traza-Id: 07eaa3ce-1e8d-4c1c-b7b3-a5c550c0f211
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "precio_compra": 0.05,
  "capacidad_semanal": 100,
  "minimo_compra": 5,
  "unidad_compra": "caja"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 115 ms · traza `07eaa3ce-1e8d-4c1c-b7b3-a5c550c0f211`

```json
{
  "producto": {
    "id": 6,
    "nombre": "Harina de maíz nixtamalizado"
  },
  "precio_compra": 0.05,
  "unidad_compra": "caja",
  "capacidad_semanal": 100,
  "minimo_compra": 5,
  "vigente_hasta": null
}
```

**Evidencia en PostgreSQL.** `SELECT proveedor_id, producto_id, precio_compra, capacidad_semanal, minimo_compra FROM proveedor_producto WHERE proveedor_id = %s`

```json
[
  {
    "proveedor_id": 72,
    "producto_id": 6,
    "precio_compra": "0.05",
    "capacidad_semanal": 100,
    "minimo_compra": 5
  }
]
```

### PRV-11 · Producto inexistente en la oferta · PASA

**Objetivo.** La llave foránea rechaza el producto.

**Petición.** `PUT http://proveedores:5113/api/v1/proveedores/72/catalogo/999999`

```http
Accept: application/json
X-Traza-Id: 04862b07-9df2-499d-9d3b-174a40136c7f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "precio_compra": 1,
  "capacidad_semanal": 10
}
```

**Respuesta.** HTTP 422 (esperado 422) · 50 ms · traza `04862b07-9df2-499d-9d3b-174a40136c7f`

```json
{
  "error": {
    "codigo": "REGLA_NEGOCIO",
    "mensaje": "El producto no existe.",
    "traza_id": "04862b07-9df2-499d-9d3b-174a40136c7f"
  }
}
```

### PRV-12 · Catálogo del proveedor · PASA

**Objetivo.** Sus ofertas, con el nombre del producto.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/72/catalogo`

```http
Accept: application/json
X-Traza-Id: 3b1289aa-b8e8-4bb2-a41f-ae99c6f56f46
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 66 ms · traza `3b1289aa-b8e8-4bb2-a41f-ae99c6f56f46`

```json
{
  "datos": [
    {
      "producto": {
        "id": 6,
        "nombre": "Harina de maíz nixtamalizado"
      },
      "precio_compra": 0.05,
      "unidad_compra": "caja",
      "capacidad_semanal": 100,
      "minimo_compra": 5,
      "vigente_hasta": null
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 1,
    "paginas": 1
  }
}
```

### PRV-13 · Evaluar al proveedor · PASA

**Objetivo.** Un operador califica puntualidad, calidad y precio.

**Petición.** `POST http://proveedores:5113/api/v1/proveedores/72/evaluaciones`

```http
Accept: application/json
X-Traza-Id: e38db6ea-b0be-47fd-a0eb-1b5b9ab904fc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "puntualidad": 5,
  "calidad": 4,
  "precio": 3,
  "comentario": "Llegó a tiempo"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 58 ms · traza `e38db6ea-b0be-47fd-a0eb-1b5b9ab904fc`

```json
{
  "id": 22,
  "proveedor_id": 72,
  "puntualidad": 5,
  "calidad": 4,
  "precio": 3,
  "comentario": "Llegó a tiempo",
  "evaluado_por": 2,
  "evaluado_en": "2026-11-26T14:19:41-06:00"
}
```

**Evidencia en PostgreSQL.** `SELECT proveedor_id, puntualidad, calidad, precio, evaluado_por FROM proveedor_evaluacion WHERE proveedor_id = %s`

```json
[
  {
    "proveedor_id": 72,
    "puntualidad": 5,
    "calidad": 4,
    "precio": 3,
    "evaluado_por": 2
  }
]
```

### PRV-14 · Evaluaciones y promedio · PASA

**Objetivo.** Calificaciones recibidas y su promedio.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/72/evaluaciones`

```http
Accept: application/json
X-Traza-Id: ea51ca00-aced-4dc8-9684-476e510dd45d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 69 ms · traza `ea51ca00-aced-4dc8-9684-476e510dd45d`

```json
{
  "datos": [
    {
      "id": 22,
      "proveedor_id": 72,
      "puntualidad": 5,
      "calidad": 4,
      "precio": 3,
      "comentario": "Llegó a tiempo",
      "evaluado_por": 2,
      "evaluado_en": "2026-11-26T14:19:41-06:00"
    }
  ],
  "promedio": {
    "puntualidad": 5.0,
    "calidad": 4.0,
    "precio": 3.0,
    "general": 4.0
  },
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 1,
    "paginas": 1
  }
}
```

### PRV-15 · Un auditor intenta evaluar · PASA

**Objetivo.** El auditor solo consulta.

**Petición.** `POST http://proveedores:5113/api/v1/proveedores/72/evaluaciones`

```http
Accept: application/json
X-Traza-Id: e5f2b287-dbd4-42fb-a5e9-502969ae24dd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{
  "puntualidad": 5,
  "calidad": 5,
  "precio": 5
}
```

**Respuesta.** HTTP 403 (esperado 403) · 25 ms · traza `e5f2b287-dbd4-42fb-a5e9-502969ae24dd`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "e5f2b287-dbd4-42fb-a5e9-502969ae24dd"
  }
}
```

### PRV-16 · Ofertas de un producto · PASA

**Objetivo.** De la más barata a la más cara.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/ofertas?producto_id=6`

```http
Accept: application/json
X-Traza-Id: ace4f3c8-4535-4510-babf-2b757b5bfe84
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 61 ms · traza `ace4f3c8-4535-4510-babf-2b757b5bfe84`

```json
{
  "datos": [
    {
      "proveedor": {
        "id": 72,
        "clave": "********",
        "nombre": "Proveedor de evidencias"
      },
      "producto": {
        "id": 6,
        "nombre": "Harina de maíz nixtamalizado"
      },
      "precio_compra": 0.05,
      "unidad_compra": "caja",
      "capacidad_semanal": 100,
      "minimo_compra": 5,
      "dias_entrega": 5,
      "pedido_minimo": 250.0,
      "vigente_hasta": null,
      "calificacion": 4.0
    },
    {
      "proveedor": {
        "id": 3,
        "clave": "********",
        "nombre": "Mayorista San Nicolás"
      },
      "producto": {
        "id": 6,
        "nombre": "Harina de maíz nixtamalizado"
      },
      "precio_compra": 17.68,
      "unidad_compra": "caja",
      "capacidad_semanal": 900,
      "minimo_compra": 24,
      "dias_entrega": 4,
      "pedido_minimo": 1500.0,
      "vigente_hasta": null,
      "calificacion": 4.0
    },
    {
      "proveedor": {
        "id": 1,
        "clave": "********",
        "nombre": "Abarrotes del Norte"
      },
      "producto": {
        "id": 6,
        "nombre": "Harina de maíz nixtamalizado"
      },
      "precio_compra": 18.2,
      "unidad_compra": "pieza",
      "capacidad_semanal": 500,
      "minimo_compra": 6,
      "dias_entrega": 2,
      "pedido_minimo": 800.0,
      "vigente_hasta": null,
      "calificacion": 4.0
    },
    {
      "proveedor": {
        "id": 2,
        "clave": "********",
        "nombre": "Distribuidora Regia"
      },
      "producto": {
        "id": 6,
        "nombre": "Harina de maíz nixtamalizado"
      },
      "precio_compra": 19.24,
      "unidad_compra": "pieza",
      "capacidad_semanal": 200,
      "minimo_compra": 12,
      "dias_entrega": 1,
      "pedido_minimo": 500.0,
      "vigente_hasta": null,
      "calificacion": 4.0
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 4,
    "paginas": 1
  }
}
```

### PRV-17 · Mejor oferta de varios productos · PASA

**Objetivo.** Una oferta, la más barata, por producto.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/ofertas?producto_ids=6,7&mejor=true`

```http
Accept: application/json
X-Traza-Id: 83d73e4b-2d77-4329-a0b6-e0c6ca320cf9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 65 ms · traza `83d73e4b-2d77-4329-a0b6-e0c6ca320cf9`

```json
{
  "datos": [
    {
      "proveedor": {
        "id": 72,
        "clave": "********",
        "nombre": "Proveedor de evidencias"
      },
      "producto": {
        "id": 6,
        "nombre": "Harina de maíz nixtamalizado"
      },
      "precio_compra": 0.05,
      "unidad_compra": "caja",
      "capacidad_semanal": 100,
      "minimo_compra": 5,
      "dias_entrega": 5,
      "pedido_minimo": 250.0,
      "vigente_hasta": null,
      "calificacion": 4.0
    },
    {
      "proveedor": {
        "id": 1,
        "clave": "********",
        "nombre": "Abarrotes del Norte"
      },
      "producto": {
        "id": 7,
        "nombre": "Harina de trigo"
      },
      "precio_compra": 17.15,
      "unidad_compra": "pieza",
      "capacidad_semanal": 500,
      "minimo_compra": 6,
      "dias_entrega": 2,
      "pedido_minimo": 800.0,
      "vigente_hasta": null,
      "calificacion": 4.0
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 2,
    "paginas": 1
  }
}
```

### PRV-18 · Ofertas sin indicar producto · PASA

**Objetivo.** Falta producto_id o producto_ids.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/ofertas`

```http
Accept: application/json
X-Traza-Id: fb742f3c-6c8f-4214-848f-9f703c8a4a88
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 6 ms · traza `fb742f3c-6c8f-4214-848f-9f703c8a4a88`

```json
{
  "error": {
    "codigo": "FILTRO_INVALIDO",
    "mensaje": "Indica producto_id o producto_ids.",
    "detalles": [
      {
        "campo": "producto_id",
        "mensaje": "Indica producto_id o producto_ids."
      }
    ],
    "traza_id": "fb742f3c-6c8f-4214-848f-9f703c8a4a88"
  }
}
```

### PRV-19 · Dar de baja un proveedor · PASA

**Objetivo.** Baja lógica: ya no aparece en las ofertas.

**Petición.** `DELETE http://proveedores:5113/api/v1/proveedores/72`

```http
Accept: application/json
X-Traza-Id: 2b729f82-ef9f-4272-a1dc-c3485588336e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 34 ms · traza `2b729f82-ef9f-4272-a1dc-c3485588336e`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT clave, estatus FROM proveedor WHERE id = %s`

```json
[
  {
    "clave": "EV-4933AB",
    "estatus": "inactivo"
  }
]
```

### PRV-20 · Ofertas sin el proveedor de baja · PASA

**Objetivo.** El proveedor dado de baja no ofrece.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/ofertas?producto_id=6`

```http
Accept: application/json
X-Traza-Id: f3db38c2-b243-435d-bc24-71480d88bff7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 63 ms · traza `f3db38c2-b243-435d-bc24-71480d88bff7`

```json
{
  "datos": [
    {
      "proveedor": {
        "id": 3,
        "clave": "********",
        "nombre": "Mayorista San Nicolás"
      },
      "producto": {
        "id": 6,
        "nombre": "Harina de maíz nixtamalizado"
      },
      "precio_compra": 17.68,
      "unidad_compra": "caja",
      "capacidad_semanal": 900,
      "minimo_compra": 24,
      "dias_entrega": 4,
      "pedido_minimo": 1500.0,
      "vigente_hasta": null,
      "calificacion": 4.0
    },
    {
      "proveedor": {
        "id": 1,
        "clave": "********",
        "nombre": "Abarrotes del Norte"
      },
      "producto": {
        "id": 6,
        "nombre": "Harina de maíz nixtamalizado"
      },
      "precio_compra": 18.2,
      "unidad_compra": "pieza",
      "capacidad_semanal": 500,
      "minimo_compra": 6,
      "dias_entrega": 2,
      "pedido_minimo": 800.0,
      "vigente_hasta": null,
      "calificacion": 4.0
    },
    {
      "proveedor": {
        "id": 2,
        "clave": "********",
        "nombre": "Distribuidora Regia"
      },
      "producto": {
        "id": 6,
        "nombre": "Harina de maíz nixtamalizado"
      },
      "precio_compra": 19.24,
      "unidad_compra": "pieza",
      "capacidad_semanal": 200,
      "minimo_compra": 12,
      "dias_entrega": 1,
      "pedido_minimo": 500.0,
      "vigente_hasta": null,
      "calificacion": 4.0
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 3,
    "paginas": 1
  }
}
```

## Servicio precios · puerto 5112

### PRE-01 · Listas de precios · PASA

**Objetivo.** Listas por zona y su vigencia.

**Petición.** `GET http://precios:5112/api/v1/precios/listas`

```http
Accept: application/json
X-Traza-Id: f7526094-5c51-4a3b-b102-40462287fa7e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 55 ms · traza `f7526094-5c51-4a3b-b102-40462287fa7e`

```json
{
  "datos": [
    {
      "id": 34,
      "nombre": "Lista de evidencias f9009f",
      "zona_id": 3,
      "vigente_desde": "2027-01-01",
      "vigente_hasta": "2027-01-31",
      "estatus": "inactivo",
      "productos": 1
    },
    {
      "id": 33,
      "nombre": "Lista de evidencias 3fdd2e",
      "zona_id": 3,
      "vigente_desde": "2027-01-01",
      "vigente_hasta": "2027-01-31",
      "estatus": "inactivo",
      "productos": 1
    },
    {
      "id": 29,
      "nombre": "Lista de prueba 994bc9b6",
      "zona_id": 3,
      "vigente_desde": "2027-01-01",
      "vigente_hasta": "2027-01-31",
      "estatus": "inactivo",
      "productos": 1
    },
    {
      "id": 25,
      "nombre": "Lista de prueba 53ef8464",
      "zona_id": 3,
      "vigente_desde": "2027-01-01",
      "vigente_hasta": "2027-01-31",
      "estatus": "inactivo",
      "productos": 1
    },
    {
      "id": 23,
      "nombre": "Lista de prueba 6efd002d",
      "zona_id": 3,
      "vigente_desde": "2027-01-01",
      "vigente_hasta": "2027-01-31",
      "estatus": "inactivo",
      "productos": 1
    },
    {
      "id": 20,
      "nombre": "Lista de evidencias dba9cd",
      "zona_id": 3,
      "vigente_desde": "2027-01-01",
      "vigente_hasta": "2027-01-31",
      "estatus": "inactivo",
      "productos": 1
    },
    {
      "id": 17,
      "nombre": "Lista de evidencias 4ccd1c",
      "zona_id": 3,
      "vigente_desde": "2027-01-01",
      "vigente_hasta": "2027-01-31",
      "estatus": "inactivo",
      "productos": 1
    },
    {
      "id": 16,
      "nombre": "Lista de evidencias 6ddeea",
      "zona_id": 3,
      "vigente_desde": "2027-01-01",
      "vigente_hasta": "2027-01-31",
      "estatus": "inactivo",
      "productos": 1
    },
    {
      "id": 15,
      "nombre": "Lista de evidencias 962abe",
      "zona_id": 3,
      "vigente_desde": "2027-01-01",
      "vigente_hasta": "2027-01-31",
      "estatus": "inactivo",
      "productos": 1
    },
    {
      "id": 14,
      "nombre": "Lista de evidencias fa981b",
      "zona_id": 3,
      "vigente_desde": "2027-01-01",
      "vigente_hasta": "2027-01-31",
      "estatus": "inactivo",
      "productos": 1
    },
    {
      "id": 11,
      "nombre": "Lista de prueba a8dad7c8",
      "zona_id": 3,
      "vigente_desde": "2027-01-01",
      "vigente_hasta": "2027-01-31",
      "estatus": "inactivo",
      "productos": 1
    },
    {
      "id": 4,
      "nombre": "Lista de prueba 8a4e607d",
      "zona_id": 3,
      "vigente_desde": "2027-01-01",
      "vigente_hasta": "2027-01-31",
      "estatus": "inactivo",
      "productos": 1
    },
    {
      "id": 3,
      "nombre": "Lista de evidencias 0c58f9",
      "zona_id": 3,
      "vigente_desde": "2027-01-01",
      "vigente_hasta": "2027-01-31",
      "estatus": "inactivo",
      "productos": 1
    },
    {
      "id": 1,
      "nombre": "Lista San Bernabé Centro",
      "zona_id": 1,
      "vigente_desde": "2026-10-19",
      "vigente_hasta": null,
      "estatus": "activo",
      "productos": 20
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 14,
    "paginas": 1
  }
}
```

### PRE-02 · Listas (XML) · PASA

**Objetivo.** Respuesta XML que cumple precios.xsd.

**Petición.** `GET http://precios:5112/api/v1/precios/listas`

```http
Accept: application/xml
X-Traza-Id: 35913912-353b-4236-b458-05873ab210a5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 57 ms · traza `35913912-353b-4236-b458-05873ab210a5`

```xml
<?xml version='1.0' encoding='utf-8'?>
<listas xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><datos><lista><id>34</id><nombre>Lista de evidencias f9009f</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>33</id><nombre>Lista de evidencias 3fdd2e</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>29</id><nombre>Lista de prueba 994bc9b6</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>25</id><nombre>Lista de prueba 53ef8464</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>23</id><nombre>Lista de prueba 6efd002d</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>20</id><nombre>Lista de evidencias dba9cd</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>17</id><nombre>Lista de evidencias 4ccd1c</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>16</id><nombre>Lista de evidencias 6ddeea</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>15</id><nombre>Lista de evidencias 962abe</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>14</id><nombre>Lista de evidencias fa981b</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>11</id><nombre>Lista de prueba a8dad7c8</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>4</id><nombre>Lista de prueba 8a4e607d</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>3</id><nombre>Lista de evidencias 0c58f9</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>1</id><nombre>Lista San Bernabé Centro</nombre><zona_id>1</zona_id><vigente_desde>2026-10-19</vigente_desde><vigente_hasta xsi:nil="true" /><estatus>activo</estatus><productos>20</productos></lista></datos><paginacion><pagina>1</pagina><por_pagina>20</por_pagina><total>14</total><paginas>1</paginas></paginacion></listas>
```

### PRE-03 · Un cliente intenta ver las listas · PASA

**Objetivo.** Sin precios.ver.

**Petición.** `GET http://precios:5112/api/v1/precios/listas`

```http
Accept: application/json
X-Traza-Id: af0f06dd-d72b-4d6e-af96-9a7496771168
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 27 ms · traza `af0f06dd-d72b-4d6e-af96-9a7496771168`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "af0f06dd-d72b-4d6e-af96-9a7496771168"
  }
}
```

### PRE-04 · Crear una lista · PASA

**Objetivo.** Lista de una zona con un precio y su costo.

**Petición.** `POST http://precios:5112/api/v1/precios/listas`

```http
Accept: application/json
X-Traza-Id: b692b4b1-3569-4b6c-9bed-cfcf92aff83d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Lista de evidencias 41a205",
  "zona_id": 3,
  "vigente_desde": "2027-01-01",
  "vigente_hasta": "2027-01-31",
  "items": [
    {
      "producto_id": 2,
      "precio": 50.0,
      "costo": 30.0
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 90 ms · traza `b692b4b1-3569-4b6c-9bed-cfcf92aff83d`

```json
{
  "id": 35,
  "nombre": "Lista de evidencias 41a205",
  "zona_id": 3,
  "vigente_desde": "2027-01-01",
  "vigente_hasta": "2027-01-31",
  "estatus": "activo",
  "productos": 1,
  "items": [
    {
      "producto": {
        "id": 2,
        "nombre": "Arroz superextra"
      },
      "precio": 50.0,
      "costo": 30.0,
      "margen_pct": 40.0,
      "actualizado_en": "2026-11-26T14:19:42-06:00"
    }
  ]
}
```

**Explicación.** Margen = (precio − costo) / precio = (50 − 30) / 50 = 40 %.

**Evidencia en PostgreSQL.** `SELECT l.id, l.nombre, l.zona_id, l.vigente_desde, l.vigente_hasta, i.producto_id, i.precio, i.costo FROM lista_precio l JOIN lista_precio_item i ON i.lista_id = l.id WHERE l.nombre = %s`

```json
[
  {
    "id": 35,
    "nombre": "Lista de evidencias 41a205",
    "zona_id": 3,
    "vigente_desde": "2027-01-01",
    "vigente_hasta": "2027-01-31",
    "producto_id": 2,
    "precio": "50.00",
    "costo": "30.00"
  }
]
```

### PRE-05 · Listas que se traslapan · PASA

**Objetivo.** Una zona no tiene dos listas vigentes a la vez.

**Petición.** `POST http://precios:5112/api/v1/precios/listas`

```http
Accept: application/json
X-Traza-Id: 0a208667-955b-4275-9896-054a08a2019c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Lista de evidencias 41a205 bis",
  "zona_id": 3,
  "vigente_desde": "2027-01-15",
  "vigente_hasta": "2027-02-15",
  "items": [
    {
      "producto_id": 2,
      "precio": 50.0,
      "costo": 30.0
    }
  ]
}
```

**Respuesta.** HTTP 409 (esperado 409) · 27 ms · traza `0a208667-955b-4275-9896-054a08a2019c`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "La lista «Lista de evidencias 41a205» ya rige en esa zona durante esas fechas.",
    "traza_id": "0a208667-955b-4275-9896-054a08a2019c"
  }
}
```

### PRE-06 · Cambiar el precio de un producto · PASA

**Objetivo.** Sube el precio de 50 a 52; el costo se conserva.

**Petición.** `PUT http://precios:5112/api/v1/precios/listas/35/items/2`

```http
Accept: application/json
X-Traza-Id: 1e435418-c888-4c7c-a8f4-933433058123
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "precio": 52.0
}
```

**Respuesta.** HTTP 200 (esperado 200) · 45 ms · traza `1e435418-c888-4c7c-a8f4-933433058123`

```json
{
  "producto": {
    "id": 2,
    "nombre": "Arroz superextra"
  },
  "precio": 52.0,
  "costo": 30.0,
  "margen_pct": 42.3,
  "actualizado_en": "2026-11-26T14:19:42-06:00"
}
```

**Evidencia en PostgreSQL.** `SELECT precio_anterior, precio_nuevo, usuario_id FROM lista_precio_historico WHERE lista_id = %s ORDER BY id`

```json
[
  {
    "precio_anterior": null,
    "precio_nuevo": "50.00",
    "usuario_id": 1
  },
  {
    "precio_anterior": "50.00",
    "precio_nuevo": "52.00",
    "usuario_id": 1
  }
]
```

### PRE-07 · Historial de cambios · PASA

**Objetivo.** Cada cambio de precio queda registrado por un trigger.

**Petición.** `GET http://precios:5112/api/v1/precios/historial?lista_id=35&producto_id=2`

```http
Accept: application/json
X-Traza-Id: a9297c60-57d4-47ba-a7b9-99b16b33abd8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 54 ms · traza `a9297c60-57d4-47ba-a7b9-99b16b33abd8`

```json
{
  "datos": [
    {
      "id": 48,
      "lista_id": 35,
      "producto_id": 2,
      "precio_anterior": 50.0,
      "precio_nuevo": 52.0,
      "usuario_id": 1,
      "fecha": "2026-11-26T14:19:42-06:00"
    },
    {
      "id": 47,
      "lista_id": 35,
      "producto_id": 2,
      "precio_anterior": null,
      "precio_nuevo": 50.0,
      "usuario_id": 1,
      "fecha": "2026-11-26T14:19:42-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 2,
    "paginas": 1
  }
}
```

### PRE-08 · Una lista con sus márgenes · PASA

**Objetivo.** Precios, costos y margen de cada renglón.

**Petición.** `GET http://precios:5112/api/v1/precios/listas/35`

```http
Accept: application/json
X-Traza-Id: 3599dc79-0f92-496f-8c50-4030d02dec08
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 55 ms · traza `3599dc79-0f92-496f-8c50-4030d02dec08`

```json
{
  "id": 35,
  "nombre": "Lista de evidencias 41a205",
  "zona_id": 3,
  "vigente_desde": "2027-01-01",
  "vigente_hasta": "2027-01-31",
  "estatus": "activo",
  "productos": 1,
  "items": [
    {
      "producto": {
        "id": 2,
        "nombre": "Arroz superextra"
      },
      "precio": 52.0,
      "costo": 30.0,
      "margen_pct": 42.3,
      "actualizado_en": "2026-11-26T14:19:42-06:00"
    }
  ]
}
```

### PRE-09 · Precio dentro de la vigencia · PASA

**Objetivo.** Rige el precio de la lista de la zona.

**Petición.** `GET http://precios:5112/api/v1/precios/vigente?producto_id=2&zona_id=3&fecha=2027-01-15`

```http
Accept: application/json
X-Traza-Id: 1ada642b-6b78-4084-ae24-b8e60b7ce135
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 100 ms · traza `1ada642b-6b78-4084-ae24-b8e60b7ce135`

```json
{
  "producto_id": 2,
  "zona_id": 3,
  "fecha": "2027-01-15",
  "precio_base": 29.9,
  "lista": {
    "id": 35,
    "nombre": "Lista de evidencias 41a205"
  },
  "precio_vigente": 52.0,
  "promocion": null,
  "descuento": 0.0,
  "descuento_limitado": false,
  "precio_final": 52.0,
  "costo": 30.0,
  "margen_pct": 42.3,
  "bajo_margen": false
}
```

### PRE-10 · Precio fuera de la vigencia · PASA

**Objetivo.** Sin lista vigente rige el precio base del catálogo.

**Petición.** `GET http://precios:5112/api/v1/precios/vigente?producto_id=2&zona_id=3&fecha=2026-10-19`

```http
Accept: application/json
X-Traza-Id: c586473b-e0b5-4db7-9cca-dba25cc5efc0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 97 ms · traza `c586473b-e0b5-4db7-9cca-dba25cc5efc0`

```json
{
  "producto_id": 2,
  "zona_id": 3,
  "fecha": "2026-10-19",
  "precio_base": 29.9,
  "lista": null,
  "precio_vigente": 29.9,
  "promocion": null,
  "descuento": 0.0,
  "descuento_limitado": false,
  "precio_final": 29.9,
  "costo": null,
  "margen_pct": null,
  "bajo_margen": false
}
```

### PRE-11 · Precio con lista de la zona · PASA

**Objetivo.** Precio base, lista, promoción y margen de un producto.

**Petición.** `GET http://precios:5112/api/v1/precios/vigente?producto_id=1&zona_id=1`

```http
Accept: application/json
X-Traza-Id: 25b297fd-5a13-4034-a03f-1b3007a6ce25
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 95 ms · traza `25b297fd-5a13-4034-a03f-1b3007a6ce25`

```json
{
  "producto_id": 1,
  "zona_id": 1,
  "fecha": "2026-11-26",
  "precio_base": 38.5,
  "lista": {
    "id": 1,
    "nombre": "Lista San Bernabé Centro"
  },
  "precio_vigente": 39.66,
  "promocion": null,
  "descuento": 0.0,
  "descuento_limitado": false,
  "precio_final": 39.66,
  "costo": 26.95,
  "margen_pct": 32.0,
  "bajo_margen": false
}
```

**Explicación.** Lista de la zona sobre el precio base, luego una sola promoción (la de mayor descuento), luego el margen si hay costo.

### PRE-12 · Precio con promoción · PASA

**Objetivo.** Bebidas con 10 % de descuento.

**Petición.** `GET http://precios:5112/api/v1/precios/vigente?producto_id=21&zona_id=1`

```http
Accept: application/json
X-Traza-Id: 2f8d956c-3281-4b2c-b14c-98ca672230fa
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 170 ms · traza `2f8d956c-3281-4b2c-b14c-98ca672230fa`

```json
{
  "producto_id": 21,
  "zona_id": 1,
  "fecha": "2026-11-26",
  "precio_base": 38.0,
  "lista": null,
  "precio_vigente": 38.0,
  "promocion": {
    "id": 1,
    "nombre": "Bebidas -10 %",
    "tipo": "porcentaje",
    "valor": 10.0
  },
  "descuento": 3.8,
  "descuento_limitado": false,
  "precio_final": 34.2,
  "costo": null,
  "margen_pct": null,
  "bajo_margen": false
}
```

### PRE-13 · Calcular un pedido · PASA

**Objetivo.** Precio final, descuento e importe de cada línea.

**Petición.** `POST http://precios:5112/api/v1/precios/calcular`

```http
Accept: application/json
X-Traza-Id: 4ace3733-5342-4536-8e6d-c3f02db07559
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
Content-Type: application/json
```

```json
{
  "zona_id": 1,
  "lineas": [
    {
      "producto_id": 1,
      "cantidad": 2
    },
    {
      "producto_id": 21,
      "cantidad": 3
    }
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 93 ms · traza `4ace3733-5342-4536-8e6d-c3f02db07559`

```json
{
  "zona_id": 1,
  "fecha": "2026-11-26",
  "lineas": [
    {
      "producto_id": 1,
      "cantidad": 2,
      "precio_unitario": 39.66,
      "descuento_unitario": 0.0,
      "importe": 79.32,
      "promocion_id": null,
      "bajo_margen": false
    },
    {
      "producto_id": 21,
      "cantidad": 3,
      "precio_unitario": 34.2,
      "descuento_unitario": 3.8,
      "importe": 102.6,
      "promocion_id": 1,
      "bajo_margen": false
    }
  ],
  "subtotal": 193.32,
  "descuento_total": 11.4,
  "total": 181.92
}
```

### PRE-14 · Calcular un producto inexistente · PASA

**Objetivo.** Validación con detalle por línea.

**Petición.** `POST http://precios:5112/api/v1/precios/calcular`

```http
Accept: application/json
X-Traza-Id: 8434fdaf-0c7b-4125-9440-a975930258aa
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
Content-Type: application/json
```

```json
{
  "lineas": [
    {
      "producto_id": 999999,
      "cantidad": 1
    }
  ]
}
```

**Respuesta.** HTTP 422 (esperado 422) · 6 ms · traza `8434fdaf-0c7b-4125-9440-a975930258aa`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "lineas[0].producto_id",
        "mensaje": "No existe ese producto."
      }
    ],
    "traza_id": "8434fdaf-0c7b-4125-9440-a975930258aa"
  }
}
```

### PRE-15 · Promoción que pasa del descuento máximo · PASA

**Objetivo.** Un porcentaje mayor al tope de la configuración se rechaza.

**Petición.** `POST http://precios:5112/api/v1/precios/promociones`

```http
Accept: application/json
X-Traza-Id: e806aec2-34fa-4603-a042-da2250d251c5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Promoción excesiva",
  "tipo": "porcentaje",
  "valor": 31.0,
  "producto_id": 1,
  "vigente_hasta": "2030-12-31"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 26 ms · traza `e806aec2-34fa-4603-a042-da2250d251c5`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "valor",
        "mensaje": "Un descuento porcentual no puede pasar de 30 %."
      }
    ],
    "traza_id": "e806aec2-34fa-4603-a042-da2250d251c5"
  }
}
```

### PRE-16 · Crear una promoción · PASA

**Objetivo.** Descuento de $2 en un producto.

**Petición.** `POST http://precios:5112/api/v1/precios/promociones`

```http
Accept: application/json
X-Traza-Id: 66042fbb-9652-4bd6-9a81-6964d12e1a70
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Promoción de evidencias e5c5",
  "tipo": "monto",
  "valor": 2.0,
  "producto_id": 1,
  "vigente_hasta": "2030-12-31"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 79 ms · traza `66042fbb-9652-4bd6-9a81-6964d12e1a70`

```json
{
  "id": 15,
  "nombre": "Promoción de evidencias e5c5",
  "tipo": "monto",
  "valor": 2.0,
  "producto_id": 1,
  "categoria_id": null,
  "zona_id": null,
  "vigente_desde": "2026-11-26",
  "vigente_hasta": "2030-12-31",
  "estatus": "activo"
}
```

**Evidencia en PostgreSQL.** `SELECT id, nombre, tipo, valor, producto_id, vigente_hasta, estatus FROM promocion WHERE id = %s`

```json
[
  {
    "id": 15,
    "nombre": "Promoción de evidencias e5c5",
    "tipo": "monto",
    "valor": "2.00",
    "producto_id": 1,
    "vigente_hasta": "2030-12-31",
    "estatus": "activo"
  }
]
```

### PRE-17 · Promociones vigentes · PASA

**Objetivo.** Filtro por producto.

**Petición.** `GET http://precios:5112/api/v1/precios/promociones?vigente=true&producto_id=1`

```http
Accept: application/json
X-Traza-Id: 2c4c3dea-a0c8-431d-9b30-5dcbd180129e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 54 ms · traza `2c4c3dea-a0c8-431d-9b30-5dcbd180129e`

```json
{
  "datos": [
    {
      "id": 15,
      "nombre": "Promoción de evidencias e5c5",
      "tipo": "monto",
      "valor": 2.0,
      "producto_id": 1,
      "categoria_id": null,
      "zona_id": null,
      "vigente_desde": "2026-11-26",
      "vigente_hasta": "2030-12-31",
      "estatus": "activo"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 1,
    "paginas": 1
  }
}
```

### PRE-18 · Dar de baja la promoción · PASA

**Objetivo.** Baja lógica.

**Petición.** `DELETE http://precios:5112/api/v1/precios/promociones/15`

```http
Accept: application/json
X-Traza-Id: 4d34931c-329c-41ad-8e03-eb8c9f9056ec
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 43 ms · traza `4d34931c-329c-41ad-8e03-eb8c9f9056ec`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT id, estatus FROM promocion WHERE id = %s`

```json
[
  {
    "id": 15,
    "estatus": "inactivo"
  }
]
```

### PRE-19 · Márgenes · PASA

**Objetivo.** Renglones con costo, del margen más bajo al más alto.

**Petición.** `GET http://precios:5112/api/v1/precios/margenes?por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 1cf1830f-6139-40ef-85c4-689c2c825add
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 82 ms · traza `1cf1830f-6139-40ef-85c4-689c2c825add`

```json
{
  "datos": [
    {
      "lista": {
        "id": 1,
        "nombre": "Lista San Bernabé Centro"
      },
      "producto": {
        "id": 3,
        "nombre": "Aceite vegetal"
      },
      "precio": 43.26,
      "costo": 29.4,
      "margen_pct": 32.0,
      "bajo_margen": false
    },
    {
      "lista": {
        "id": 1,
        "nombre": "Lista San Bernabé Centro"
      },
      "producto": {
        "id": 5,
        "nombre": "Sal de mesa"
      },
      "precio": 14.42,
      "costo": 9.8,
      "margen_pct": 32.0,
      "bajo_margen": false
    },
    {
      "lista": {
        "id": 1,
        "nombre": "Lista San Bernabé Centro"
      },
      "producto": {
        "id": 6,
        "nombre": "Harina de maíz nixtamalizado"
      },
      "precio": 26.78,
      "costo": 18.2,
      "margen_pct": 32.0,
      "bajo_margen": false
    },
    {
      "lista": {
        "id": 1,
        "nombre": "Lista San Bernabé Centro"
      },
      "producto": {
        "id": 9,
        "nombre": "Atún en agua"
      },
      "precio": 21.63,
      "costo": 14.7,
      "margen_pct": 32.0,
      "bajo_margen": false
    },
    {
      "lista": {
        "id": 1,
        "nombre": "Lista San Bernabé Centro"
      },
      "producto": {
        "id": 11,
        "nombre": "Frijoles refritos"
      },
      "precio": 23.69,
      "costo": 16.1,
      "margen_pct": 32.0,
      "bajo_margen": false
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 20,
    "paginas": 4
  }
}
```

### PRE-20 · Sensibilidad al precio · PASA

**Objetivo.** Qué pasa con ingreso y margen si el precio sube o baja.

**Petición.** `GET http://precios:5112/api/v1/precios/sensibilidad?producto_id=1&zona_id=1&volumen_base=100&elasticidad=-1.2`

```http
Accept: application/json
X-Traza-Id: f6489577-2276-47c2-8b24-d99286a88f1e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 134 ms · traza `f6489577-2276-47c2-8b24-d99286a88f1e`

```json
{
  "producto_id": 1,
  "zona_id": 1,
  "precio_final": 39.66,
  "costo": 26.95,
  "volumen_base": 100,
  "elasticidad": -1.2,
  "supuestos": "La elasticidad es un supuesto, no una medición: indica cuánt…(219 caracteres)",
  "escenarios": [
    {
      "variacion_pct": -20,
      "precio": 31.73,
      "volumen_estimado": 124.0,
      "ingreso": 3934.27,
      "ingreso_vs_base_pct": -0.8,
      "margen_total": 592.47,
      "volumen_para_igualar_margen": 266.0
    },
    {
      "variacion_pct": -10,
      "precio": 35.69,
      "volumen_estimado": 112.0,
      "ingreso": 3997.73,
      "ingreso_vs_base_pct": 0.8,
      "margen_total": 979.33,
      "volumen_para_igualar_margen": 145.4
    },
    {
      "variacion_pct": -5,
      "precio": 37.68,
      "volumen_estimado": 106.0,
      "ingreso": 3993.76,
      "ingreso_vs_base_pct": 0.7,
      "margen_total": 1137.06,
      "volumen_para_igualar_margen": 118.5
    },
    {
      "variacion_pct": 5,
      "precio": 41.64,
      "volumen_estimado": 94.0,
      "ingreso": 3914.44,
      "ingreso_vs_base_pct": -1.3,
      "margen_total": 1381.14,
      "volumen_para_igualar_margen": 86.5
    },
    {
      "variacion_pct": 10,
      "precio": 43.63,
      "volumen_estimado": 88.0,
      "ingreso": 3839.09,
      "ingreso_vs_base_pct": -3.2,
      "margen_total": 1467.49,
      "volumen_para_igualar_margen": 76.2
    },
    {
      "variacion_pct": 20,
      "precio": 47.59,
      "volumen_estimado": 76.0,
      "ingreso": 3616.99,
      "ingreso_vs_base_pct": -8.8,
      "margen_total": 1568.79,
      "volumen_para_igualar_margen": 61.6
    }
  ]
}
```

**Explicación.** volumen = base × (1 + elasticidad × variación). Con elasticidad −1.2, un precio 10 % más alto baja el volumen 12 % (100 → 88). La elasticidad es un supuesto; la respuesta lo dice en el campo `supuestos`.

### PRE-21 · Elasticidad fuera de rango · PASA

**Objetivo.** La elasticidad va de −10 a 0.

**Petición.** `GET http://precios:5112/api/v1/precios/sensibilidad?producto_id=1&elasticidad=1`

```http
Accept: application/json
X-Traza-Id: b3651d10-bd05-4f9c-80e7-498501cc3eee
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 7 ms · traza `b3651d10-bd05-4f9c-80e7-498501cc3eee`

```json
{
  "error": {
    "codigo": "FILTRO_INVALIDO",
    "mensaje": "elasticidad debe estar entre -10 y 0.",
    "detalles": [
      {
        "campo": "elasticidad",
        "mensaje": "elasticidad debe estar entre -10 y 0."
      }
    ],
    "traza_id": "b3651d10-bd05-4f9c-80e7-498501cc3eee"
  }
}
```

## Servicio abastecimiento · puerto 5114

### ABA-01 · Necesidades de reposición · PASA

**Objetivo.** Productos bajo su mínimo, con la mejor oferta.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/necesidades?por_pagina=100`

```http
Accept: application/json
X-Traza-Id: 258d3d99-9be6-4540-930c-dc94f92317f9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 248 ms · traza `258d3d99-9be6-4540-930c-dc94f92317f9`

```json
{
  "microhub_id": 1,
  "factor_objetivo": 3.0,
  "datos": [
    {
      "producto": {
        "id": 21,
        "nombre": "Agua purificada"
      },
      "existencia": 0,
      "minimo": 10,
      "disponible": 0,
      "en_camino": 0,
      "solicitado": 0,
      "cantidad_sugerida": 30,
      "cantidad_a_comprar": 30,
      "mejor_oferta": {
        "proveedor": {
          "id": 3,
          "nombre": "Mayorista San Nicolás"
        },
        "precio_compra": 25.84,
        "dias_entrega": 4,
        "capacidad_semanal": 900,
        "minimo_compra": 24
      },
      "costo_estimado": 775.2
    },
    {
      "producto": {
        "id": 15,
        "nombre": "Avena en hojuelas"
      },
      "existencia": 52,
      "minimo": 72,
      "disponible": 52,
      "en_camino": 0,
      "solicitado": 0,
      "cantidad_sugerida": 164,
      "cantidad_a_comprar": 164,
      "mejor_oferta": {
        "proveedor": {
          "id": 3,
          "nombre": "Mayorista San Nicolás"
        },
        "precio_compra": 18.36,
        "dias_entrega": 4,
        "capacidad_semanal": 900,
        "minimo_compra": 24
      },
      "costo_estimado": 3011.04
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 100,
    "total": 2,
    "paginas": 1
  }
}
```

**Explicación.** Pide las alertas al servicio de inventario y la mejor oferta al de proveedores (HTTP con el mismo JWT). Sugiere llegar a 3 × el mínimo, sin contar lo que ya viene en camino ni lo ya solicitado.

### ABA-02 · Necesidades sin indicar el microhub · PASA

**Objetivo.** El administrador debe elegir un microhub.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/necesidades`

```http
Accept: application/json
X-Traza-Id: cfdb6db5-8790-455d-a6d6-7fac60f3b27f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 6 ms · traza `cfdb6db5-8790-455d-a6d6-7fac60f3b27f`

```json
{
  "error": {
    "codigo": "FILTRO_INVALIDO",
    "mensaje": "microhub_id es obligatorio.",
    "detalles": [
      {
        "campo": "microhub_id",
        "mensaje": "microhub_id es obligatorio."
      }
    ],
    "traza_id": "cfdb6db5-8790-455d-a6d6-7fac60f3b27f"
  }
}
```

### ABA-03 · Pedir mercancía · PASA

**Objetivo.** El operador pide reposición de su microhub.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: acb41692-6bc9-481e-bbae-452b921337c8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "motivo": "Se acabó el producto el fin de semana",
  "lineas": [
    {
      "producto_id": 10,
      "cantidad": 46
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 120 ms · traza `acb41692-6bc9-481e-bbae-452b921337c8`

```json
{
  "id": 53,
  "folio": "SC-20261126-000053",
  "microhub_id": 1,
  "estado": "pendiente",
  "motivo": "Se acabó el producto el fin de semana",
  "solicitada_por": 2,
  "decidida_por": null,
  "decision_motivo": null,
  "decidida_en": null,
  "creada_en": "2026-11-26T14:19:43-06:00",
  "lineas": [
    {
      "producto": {
        "id": 10,
        "nombre": "Sardina en salsa de tomate"
      },
      "cantidad": 46
    }
  ]
}
```

**Evidencia en PostgreSQL.** `SELECT id, folio, microhub_id, estado, solicitada_por FROM solicitud_compra WHERE id = %s`

```json
[
  {
    "id": 53,
    "folio": "SC-20261126-000053",
    "microhub_id": 1,
    "estado": "pendiente",
    "solicitada_por": 2
  }
]
```

**Evidencia en PostgreSQL.** `SELECT destinatario_id, tipo, titulo, referencia_tipo FROM web_notificacion WHERE tipo = 'abastecimiento' AND referencia_tipo = 'solicitud' AND referencia_id = %s`

```json
[
  {
    "destinatario_id": 1,
    "tipo": "abastecimiento",
    "titulo": "Solicitud de compra SC-20261126-000053",
    "referencia_tipo": "solicitud"
  }
]
```

### ABA-04 · Pedir para otro microhub · PASA

**Objetivo.** El operador solo trabaja con el suyo.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: ab927100-5b55-4771-b965-721b8a03df0c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 2,
  "lineas": [
    {
      "producto_id": 10,
      "cantidad": 12
    }
  ]
}
```

**Respuesta.** HTTP 403 (esperado 403) · 9 ms · traza `ab927100-5b55-4771-b965-721b8a03df0c`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "ab927100-5b55-4771-b965-721b8a03df0c"
  }
}
```

### ABA-05 · Producto repetido en la solicitud · PASA

**Objetivo.** Un producto aparece una sola vez.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: 7563af8b-7914-4f90-b4be-36f7b5bdd2b0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "lineas": [
    {
      "producto_id": 10,
      "cantidad": 1
    },
    {
      "producto_id": 10,
      "cantidad": 2
    }
  ]
}
```

**Respuesta.** HTTP 422 (esperado 422) · 8 ms · traza `7563af8b-7914-4f90-b4be-36f7b5bdd2b0`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "lineas",
        "mensaje": "Un producto no puede aparecer dos veces en la misma solicitud."
      }
    ],
    "traza_id": "7563af8b-7914-4f90-b4be-36f7b5bdd2b0"
  }
}
```

### ABA-06 · Solicitud de otro microhub · PASA

**Objetivo.** Otro operador no la ve.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/53`

```http
Accept: application/json
X-Traza-Id: 234a67db-fe23-4231-bc61-5c357a1086b1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 22 ms · traza `234a67db-fe23-4231-bc61-5c357a1086b1`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe esa solicitud de compra.",
    "traza_id": "234a67db-fe23-4231-bc61-5c357a1086b1"
  }
}
```

### ABA-07 · Aprobar sin permiso · PASA

**Objetivo.** Solo el administrador decide.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/53/decision`

```http
Accept: application/json
X-Traza-Id: 9e8d17ce-6135-4b79-a741-b019610d799a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aprobada"
}
```

**Respuesta.** HTTP 403 (esperado 403) · 31 ms · traza `9e8d17ce-6135-4b79-a741-b019610d799a`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "9e8d17ce-6135-4b79-a741-b019610d799a"
  }
}
```

### ABA-08 · Rechazar sin motivo · PASA

**Objetivo.** Rechazar exige el motivo.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/53/decision`

```http
Accept: application/json
X-Traza-Id: 1dca2484-f70b-4a40-a63f-954e09ca0fe3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "rechazada"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 7 ms · traza `1dca2484-f70b-4a40-a63f-954e09ca0fe3`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "motivo",
        "mensaje": "Rechazar una solicitud exige el motivo."
      }
    ],
    "traza_id": "1dca2484-f70b-4a40-a63f-954e09ca0fe3"
  }
}
```

### ABA-09 · Ordenar antes de aprobar · PASA

**Objetivo.** Solo se ordena una solicitud aprobada.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/53/ordenar`

```http
Accept: application/json
X-Traza-Id: d9535afb-e1c8-41ed-8bda-778048ca9668
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "proveedor_id": 1
}
```

**Respuesta.** HTTP 409 (esperado 409) · 43 ms · traza `d9535afb-e1c8-41ed-8bda-778048ca9668`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Solo se ordena una solicitud aprobada; esta está pendiente.",
    "traza_id": "d9535afb-e1c8-41ed-8bda-778048ca9668"
  }
}
```

### ABA-10 · Aprobar la solicitud · PASA

**Objetivo.** El administrador aprueba y quien pidió recibe el aviso.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/53/decision`

```http
Accept: application/json
X-Traza-Id: 9d02d8da-ccb9-4e74-8d7e-af8d1d4ff8b9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aprobada",
  "motivo": "Hay presupuesto"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 95 ms · traza `9d02d8da-ccb9-4e74-8d7e-af8d1d4ff8b9`

```json
{
  "id": 53,
  "folio": "SC-20261126-000053",
  "microhub_id": 1,
  "estado": "aprobada",
  "motivo": "Se acabó el producto el fin de semana",
  "solicitada_por": 2,
  "decidida_por": 1,
  "decision_motivo": "Hay presupuesto",
  "decidida_en": "2026-11-26T14:19:44-06:00",
  "creada_en": "2026-11-26T14:19:43-06:00",
  "lineas": [
    {
      "producto": {
        "id": 10,
        "nombre": "Sardina en salsa de tomate"
      },
      "cantidad": 46
    }
  ]
}
```

**Evidencia en PostgreSQL.** `SELECT estado, decidida_por, decision_motivo FROM solicitud_compra WHERE id = %s`

```json
[
  {
    "estado": "aprobada",
    "decidida_por": 1,
    "decision_motivo": "Hay presupuesto"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT destinatario_id, titulo, mensaje FROM web_notificacion WHERE referencia_tipo = 'solicitud' AND referencia_id = %s AND destinatario_id = %s`

```json
[
  {
    "destinatario_id": 2,
    "titulo": "Solicitud de compra SC-20261126-000053",
    "mensaje": "Tu solicitud fue aprobada."
  }
]
```

### ABA-11 · Emitir la orden de compra · PASA

**Objetivo.** Cada línea va al proveedor indicado; el total es piezas × precio de compra.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/53/ordenar`

```http
Accept: application/json
X-Traza-Id: 453afb61-939a-4297-80ba-64938107387f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "proveedor_id": 1
}
```

**Respuesta.** HTTP 201 (esperado 201) · 285 ms · traza `453afb61-939a-4297-80ba-64938107387f`

```json
{
  "solicitud_id": 53,
  "ordenes": [
    {
      "id": 33,
      "folio": "OC-20261126-000033",
      "solicitud_id": 53,
      "proveedor": {
        "id": 1,
        "nombre": "Abarrotes del Norte"
      },
      "microhub_id": 1,
      "estado": "emitida",
      "fecha_esperada": "2026-11-28",
      "total": 853.3,
      "creada_en": "2026-11-26T14:19:44-06:00",
      "cerrada_en": null,
      "lineas": [
        {
          "producto": {
            "id": 10,
            "nombre": "Sardina en salsa de tomate"
          },
          "cantidad": 46,
          "precio_compra": 18.55,
          "cantidad_recibida": 0,
          "pendiente_inventario": 0
        }
      ]
    }
  ]
}
```

**Evidencia en PostgreSQL.** `SELECT o.id, o.folio, o.estado, o.fecha_esperada, o.total, l.producto_id, l.cantidad, l.precio_compra FROM orden_compra o JOIN orden_compra_linea l ON l.orden_id = o.id WHERE o.solicitud_id = %s`

```json
[
  {
    "id": 33,
    "folio": "OC-20261126-000033",
    "estado": "emitida",
    "fecha_esperada": "2026-11-28",
    "total": "853.30",
    "producto_id": 10,
    "cantidad": 46,
    "precio_compra": "18.55"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT estado FROM solicitud_compra WHERE id = %s`

```json
[
  {
    "estado": "ordenada"
  }
]
```

### ABA-12 · Ordenar dos veces · PASA

**Objetivo.** La solicitud ya quedó ordenada.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/53/ordenar`

```http
Accept: application/json
X-Traza-Id: a1edcb89-690d-4a92-81c8-1da025a4ba21
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "proveedor_id": 1
}
```

**Respuesta.** HTTP 409 (esperado 409) · 43 ms · traza `a1edcb89-690d-4a92-81c8-1da025a4ba21`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Solo se ordena una solicitud aprobada; esta está ordenada.",
    "traza_id": "a1edcb89-690d-4a92-81c8-1da025a4ba21"
  }
}
```

### ABA-13 · Recepción parcial · PASA

**Objetivo.** La mercancía que llegó entra al inventario.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/33/recepcion`

```http
Accept: application/json
X-Traza-Id: cc407457-be93-4e39-b413-bec8dda482a1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "operacion_uuid": "bb519aba-c5be-4904-94f9-a155ade438a9",
  "nota": "Llegó la primera caja",
  "lineas": [
    {
      "producto_id": 10,
      "cantidad": 23
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 279 ms · traza `cc407457-be93-4e39-b413-bec8dda482a1`

```json
{
  "orden": {
    "id": 33,
    "folio": "OC-20261126-000033",
    "solicitud_id": 53,
    "proveedor": {
      "id": 1,
      "nombre": "Abarrotes del Norte"
    },
    "microhub_id": 1,
    "estado": "parcial",
    "fecha_esperada": "2026-11-28",
    "total": 853.3,
    "creada_en": "2026-11-26T14:19:44-06:00",
    "cerrada_en": null,
    "lineas": [
      {
        "producto": {
          "id": 10,
          "nombre": "Sardina en salsa de tomate"
        },
        "cantidad": 46,
        "precio_compra": 18.55,
        "cantidad_recibida": 23,
        "pendiente_inventario": 0
      }
    ]
  },
  "aplicadas": 1,
  "pendientes": 0,
  "aviso": null
}
```

**Explicación.** Guarda la recepción, llama a POST /inventario/movimientos con la operacion_uuid del lote y marca la entrada como aplicada.

**Evidencia en PostgreSQL.** `SELECT producto_id, cantidad, operacion_uuid, aplicada FROM orden_compra_recepcion WHERE orden_id = %s`

```json
[
  {
    "producto_id": 10,
    "cantidad": 23,
    "operacion_uuid": "bb519aba-c5be-4904-94f9-a155ade438a9:10",
    "aplicada": true
  }
]
```

**Evidencia en PostgreSQL.** `SELECT tipo, cantidad, existencia_resultante, referencia_tipo, referencia_id FROM movimiento_inventario WHERE operacion_uuid = %s`

```json
[
  {
    "tipo": "recepcion",
    "cantidad": 23,
    "existencia_resultante": 667,
    "referencia_tipo": "orden_compra",
    "referencia_id": 33
  }
]
```

**Evidencia en PostgreSQL.** `SELECT estado FROM orden_compra WHERE id = %s`

```json
[
  {
    "estado": "parcial"
  }
]
```

### ABA-14 · Repetir la misma recepción · PASA

**Objetivo.** No entra dos veces al inventario.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/33/recepcion`

```http
Accept: application/json
X-Traza-Id: 95a41ecc-b3b6-4b32-8a2f-43c3b2fde0d4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "operacion_uuid": "bb519aba-c5be-4904-94f9-a155ade438a9",
  "nota": "Llegó la primera caja",
  "lineas": [
    {
      "producto_id": 10,
      "cantidad": 23
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 167 ms · traza `95a41ecc-b3b6-4b32-8a2f-43c3b2fde0d4`

```json
{
  "orden": {
    "id": 33,
    "folio": "OC-20261126-000033",
    "solicitud_id": 53,
    "proveedor": {
      "id": 1,
      "nombre": "Abarrotes del Norte"
    },
    "microhub_id": 1,
    "estado": "parcial",
    "fecha_esperada": "2026-11-28",
    "total": 853.3,
    "creada_en": "2026-11-26T14:19:44-06:00",
    "cerrada_en": null,
    "lineas": [
      {
        "producto": {
          "id": 10,
          "nombre": "Sardina en salsa de tomate"
        },
        "cantidad": 46,
        "precio_compra": 18.55,
        "cantidad_recibida": 23,
        "pendiente_inventario": 0
      }
    ]
  },
  "aplicadas": 0,
  "pendientes": 0,
  "aviso": null
}
```

**Evidencia en PostgreSQL.** `SELECT existencia FROM inventario WHERE microhub_id = %s AND producto_id = %s`

```json
[
  {
    "existencia": 667
  }
]
```

### ABA-15 · Recibir más de lo pedido · PASA

**Objetivo.** Solo falta lo que no ha llegado.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/33/recepcion`

```http
Accept: application/json
X-Traza-Id: f6b48a26-8c8b-495a-8fd3-37584fcfca49
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "lineas": [
    {
      "producto_id": 10,
      "cantidad": 24
    }
  ]
}
```

**Respuesta.** HTTP 422 (esperado 422) · 52 ms · traza `f6b48a26-8c8b-495a-8fd3-37584fcfca49`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "lineas[0].cantidad",
        "mensaje": "Solo faltan 23 por recibir de ese producto."
      }
    ],
    "traza_id": "f6b48a26-8c8b-495a-8fd3-37584fcfca49"
  }
}
```

### ABA-16 · Cancelar una orden con mercancía recibida · PASA

**Objetivo.** Solo se cancela una orden sin recepciones.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/33/cancelar`

```http
Accept: application/json
X-Traza-Id: 39ccdd5a-a085-46cc-bc64-50b91b6caa46
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "motivo": "Ya llegó"
}
```

**Respuesta.** HTTP 409 (esperado 409) · 45 ms · traza `39ccdd5a-a085-46cc-bc64-50b91b6caa46`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Solo se cancela una orden emitida que todavía no recibió mercancía.",
    "traza_id": "39ccdd5a-a085-46cc-bc64-50b91b6caa46"
  }
}
```

### ABA-17 · Recepción final · PASA

**Objetivo.** Llega el resto: la orden queda recibida y avisa.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/33/recepcion`

```http
Accept: application/json
X-Traza-Id: 91e0e95e-b8b8-4889-91bd-d6f91365b2cc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "lineas": [
    {
      "producto_id": 10,
      "cantidad": 23
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 293 ms · traza `91e0e95e-b8b8-4889-91bd-d6f91365b2cc`

```json
{
  "orden": {
    "id": 33,
    "folio": "OC-20261126-000033",
    "solicitud_id": 53,
    "proveedor": {
      "id": 1,
      "nombre": "Abarrotes del Norte"
    },
    "microhub_id": 1,
    "estado": "recibida",
    "fecha_esperada": "2026-11-28",
    "total": 853.3,
    "creada_en": "2026-11-26T14:19:44-06:00",
    "cerrada_en": "2026-11-26T14:19:45-06:00",
    "lineas": [
      {
        "producto": {
          "id": 10,
          "nombre": "Sardina en salsa de tomate"
        },
        "cantidad": 46,
        "precio_compra": 18.55,
        "cantidad_recibida": 46,
        "pendiente_inventario": 0
      }
    ]
  },
  "aplicadas": 1,
  "pendientes": 0,
  "aviso": null
}
```

**Evidencia en PostgreSQL.** `SELECT estado, cerrada_en IS NOT NULL AS cerrada FROM orden_compra WHERE id = %s`

```json
[
  {
    "estado": "recibida",
    "cerrada": true
  }
]
```

**Evidencia en PostgreSQL.** `SELECT existencia FROM inventario WHERE microhub_id = %s AND producto_id = %s`

```json
[
  {
    "existencia": 690
  }
]
```

**Evidencia en PostgreSQL.** `SELECT destinatario_id, titulo, mensaje FROM web_notificacion WHERE referencia_tipo = 'orden' AND referencia_id = %s`

```json
[
  {
    "destinatario_id": 2,
    "titulo": "Orden de compra OC-20261126-000033",
    "mensaje": "La orden quedó recibida."
  },
  {
    "destinatario_id": 1,
    "titulo": "Orden de compra OC-20261126-000033",
    "mensaje": "La orden quedó recibida."
  }
]
```

### ABA-18 · Recibir en una orden ya recibida · PASA

**Objetivo.** Una orden recibida no admite más mercancía.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/33/recepcion`

```http
Accept: application/json
X-Traza-Id: 98af1617-6944-4ef3-a0de-28c84efb967e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "lineas": [
    {
      "producto_id": 10,
      "cantidad": 1
    }
  ]
}
```

**Respuesta.** HTTP 409 (esperado 409) · 43 ms · traza `98af1617-6944-4ef3-a0de-28c84efb967e`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "La orden está recibida; ya no recibe mercancía.",
    "traza_id": "98af1617-6944-4ef3-a0de-28c84efb967e"
  }
}
```

### ABA-19 · Una orden · PASA

**Objetivo.** Con lo recibido de cada línea.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/ordenes/33`

```http
Accept: application/json
X-Traza-Id: 51c16a5b-2f50-42c7-8afa-7d06fd838c94
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 63 ms · traza `51c16a5b-2f50-42c7-8afa-7d06fd838c94`

```json
{
  "id": 33,
  "folio": "OC-20261126-000033",
  "solicitud_id": 53,
  "proveedor": {
    "id": 1,
    "nombre": "Abarrotes del Norte"
  },
  "microhub_id": 1,
  "estado": "recibida",
  "fecha_esperada": "2026-11-28",
  "total": 853.3,
  "creada_en": "2026-11-26T14:19:44-06:00",
  "cerrada_en": "2026-11-26T14:19:45-06:00",
  "lineas": [
    {
      "producto": {
        "id": 10,
        "nombre": "Sardina en salsa de tomate"
      },
      "cantidad": 46,
      "precio_compra": 18.55,
      "cantidad_recibida": 46,
      "pendiente_inventario": 0
    }
  ]
}
```

### ABA-20 · Órdenes recibidas (XML) · PASA

**Objetivo.** Respuesta XML que cumple abastecimiento.xsd.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/ordenes?estado=recibida`

```http
Accept: application/xml
X-Traza-Id: 652046f5-e377-424a-b7cc-2c6b10ff4d31
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 95 ms · traza `652046f5-e377-424a-b7cc-2c6b10ff4d31`

```xml
<?xml version='1.0' encoding='utf-8'?>
<ordenes xmlns="urn:microhubs:v1" version="1"><datos><orden><id>33</id><folio>OC-20261126-000033</folio><solicitud_id>53</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>853.30</total><creada_en>2026-11-26T14:19:44-06:00</creada_en><cerrada_en>2026-11-26T14:19:45-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>31</id><folio>OC-20261126-000031</folio><solicitud_id>51</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>853.30</total><creada_en>2026-11-26T14:04:57-06:00</creada_en><cerrada_en>2026-11-26T14:04:58-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>29</id><folio>OC-20261126-000029</folio><solicitud_id>49</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>853.30</total><creada_en>2026-11-26T13:51:34-06:00</creada_en><cerrada_en>2026-11-26T13:51:35-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>28</id><folio>OC-20261126-000028</folio><solicitud_id>47</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>859.95</total><creada_en>2026-11-26T00:32:05-06:00</creada_en><cerrada_en>2026-11-26T00:32:06-06:00</cerrada_en><lineas><linea><producto><id>12</id><nombre>Chiles jalapeños en escabeche</nombre></producto><cantidad>63</cantidad><precio_compra>13.65</precio_compra><cantidad_recibida>63</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>27</id><folio>OC-20261126-000027</folio><solicitud_id>45</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>853.30</total><creada_en>2026-11-26T00:32:01-06:00</creada_en><cerrada_en>2026-11-26T00:32:03-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>25</id><folio>OC-20261020-000025</folio><solicitud_id>40</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>859.95</total><creada_en>2026-10-20T08:13:53-06:00</creada_en><cerrada_en>2026-10-20T08:13:54-06:00</cerrada_en><lineas><linea><producto><id>12</id><nombre>Chiles jalapeños en escabeche</nombre></producto><cantidad>63</cantidad><precio_compra>13.65</precio_compra><cantidad_recibida>63</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>24</id><folio>OC-20261020-000024</folio><solicitud_id>38</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>853.30</total><creada_en>2026-10-20T08:13:49-06:00</creada_en><cerrada_en>2026-10-20T08:13:51-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>22</id><folio>OC-20261020-000022</folio><solicitud_id>33</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>859.95</total><creada_en>2026-10-20T00:50:20-06:00</creada_en><cerrada_en>2026-10-20T00:50:21-06:00</cerrada_en><lineas><linea><producto><id>12</id><nombre>Chiles jalapeños en escabeche</nombre></producto><cantidad>63</cantidad><precio_compra>13.65</precio_compra><cantidad_recibida>63</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>21</id><folio>OC-20261020-000021</folio><solicitud_id>31</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>853.30</total><creada_en>2026-10-20T00:50:16-06:00</creada_en><cerrada_en>2026-10-20T00:50:17-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>18</id><folio>OC-20261020-000018</folio><solicitud_id>26</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>853.30</total><creada_en>2026-10-20T00:43:22-06:00</creada_en><cerrada_en>2026-10-20T00:43:24-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>16</id><folio>OC-20261020-000016</folio><solicitud_id>24</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>853.30</total><creada_en>2026-10-20T00:32:35-06:00</creada_en><cerrada_en>2026-10-20T00:32:36-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>14</id><folio>OC-20261020-000014</folio><solicitud_id>22</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>853.30</total><creada_en>2026-10-20T00:29:44-06:00</creada_en><cerrada_en>2026-10-20T00:29:45-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>12</id><folio>OC-20261020-000012</folio><solicitud_id>20</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>853.30</total><creada_en>2026-10-20T00:21:44-06:00</creada_en><cerrada_en>2026-10-20T00:21:45-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>10</id><folio>OC-20261020-000010</folio><solicitud_id>18</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>853.30</total><creada_en>2026-10-20T00:20:38-06:00</creada_en><cerrada_en>2026-10-20T00:20:39-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>9</id><folio>OC-20261020-000009</folio><solicitud_id>16</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>859.95</total><creada_en>2026-10-20T00:16:49-06:00</creada_en><cerrada_en>2026-10-20T00:16:50-06:00</cerrada_en><lineas><linea><producto><id>12</id><nombre>Chiles jalapeños en escabeche</nombre></producto><cantidad>63</cantidad><precio_compra>13.65</precio_compra><cantidad_recibida>63</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>8</id><folio>OC-20261020-000008</folio><solicitud_id>14</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>853.30</total><creada_en>2026-10-20T00:16:46-06:00</creada_en><cerrada_en>2026-10-20T00:16:47-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>6</id><folio>OC-20261020-000006</folio><solicitud_id>10</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-21</fecha_esperada><total>854.70</total><creada_en>2026-10-19T19:33:42-06:00</creada_en><cerrada_en>2026-10-19T19:33:58-06:00</cerrada_en><lineas><linea><producto><id>16</id><nombre>Galletas María</nombre></producto><cantidad>74</cantidad><precio_compra>11.55</precio_compra><cantidad_recibida>74</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>5</id><folio>OC-20261020-000005</folio><solicitud_id>8</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-21</fecha_esperada><total>859.95</total><creada_en>2026-10-19T19:33:05-06:00</creada_en><cerrada_en>2026-10-19T19:33:06-06:00</cerrada_en><lineas><linea><producto><id>12</id><nombre>Chiles jalapeños en escabeche</nombre></producto><cantidad>63</cantidad><precio_compra>13.65</precio_compra><cantidad_recibida>63</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>4</id><folio>OC-20261020-000004</folio><solicitud_id>6</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-21</fecha_esperada><total>853.30</total><creada_en>2026-10-19T19:33:01-06:00</creada_en><cerrada_en>2026-10-19T19:33:03-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>1</id><folio>OC-20261020-000001</folio><solicitud_id>1</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-21</fecha_esperada><total>853.30</total><creada_en>2026-10-19T19:31:38-06:00</creada_en><cerrada_en>2026-10-19T19:31:40-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden></datos><paginacion><pagina>1</pagina><por_pagina>20</por_pagina><total>20</total><paginas>1</paginas></paginacion></ordenes>
```

### ABA-21 · Tablero de abastecimiento · PASA

**Objetivo.** Solicitudes y órdenes por estado.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/seguimiento`

```http
Accept: application/json
X-Traza-Id: e0e52e1d-f23b-4118-8d87-74d0e2f2cc0b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 121 ms · traza `e0e52e1d-f23b-4118-8d87-74d0e2f2cc0b`

```json
{
  "microhub_id": 1,
  "solicitudes": {
    "pendiente": 0,
    "aprobada": 0,
    "rechazada": 15,
    "ordenada": 33
  },
  "ordenes": {
    "emitida": 0,
    "parcial": 0,
    "recibida": 20,
    "cancelada": 13
  },
  "atrasadas": 0,
  "pendientes_inventario": 0,
  "proxima_entrega": null
}
```

### ABA-22 · Cancelar sin permiso · PASA

**Objetivo.** Cancelar una orden es del administrador.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/34/cancelar`

```http
Accept: application/json
X-Traza-Id: 7d35a007-6926-41ae-b0a6-047763c0f84b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "motivo": "No hace falta"
}
```

**Respuesta.** HTTP 403 (esperado 403) · 39 ms · traza `7d35a007-6926-41ae-b0a6-047763c0f84b`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "7d35a007-6926-41ae-b0a6-047763c0f84b"
  }
}
```

### ABA-23 · Cancelar una orden emitida · PASA

**Objetivo.** Una orden sin recepciones se puede cancelar con motivo.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/34/cancelar`

```http
Accept: application/json
X-Traza-Id: 7f1085ad-e1db-4ae8-a768-5f6fd5f1c314
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "motivo": "El proveedor ya no surte"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 193 ms · traza `7f1085ad-e1db-4ae8-a768-5f6fd5f1c314`

```json
{
  "id": 34,
  "folio": "OC-20261126-000034",
  "solicitud_id": 54,
  "proveedor": {
    "id": 1,
    "nombre": "Abarrotes del Norte"
  },
  "microhub_id": 1,
  "estado": "cancelada",
  "fecha_esperada": "2026-11-28",
  "total": 853.3,
  "creada_en": "2026-11-26T14:19:46-06:00",
  "cerrada_en": "2026-11-26T14:19:46-06:00",
  "lineas": [
    {
      "producto": {
        "id": 10,
        "nombre": "Sardina en salsa de tomate"
      },
      "cantidad": 46,
      "precio_compra": 18.55,
      "cantidad_recibida": 0,
      "pendiente_inventario": 0
    }
  ]
}
```

**Evidencia en PostgreSQL.** `SELECT estado, motivo_cancelacion, cerrada_en IS NOT NULL AS cerrada FROM orden_compra WHERE id = %s`

```json
[
  {
    "estado": "cancelada",
    "motivo_cancelacion": "El proveedor ya no surte",
    "cerrada": true
  }
]
```

### ABA-24 · Recibir en una orden cancelada · PASA

**Objetivo.** No recibe mercancía.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/34/recepcion`

```http
Accept: application/json
X-Traza-Id: feedc520-ca65-4e84-a6ea-4a36d245c401
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "lineas": [
    {
      "producto_id": 10,
      "cantidad": 1
    }
  ]
}
```

**Respuesta.** HTTP 409 (esperado 409) · 54 ms · traza `feedc520-ca65-4e84-a6ea-4a36d245c401`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "La orden está cancelada; ya no recibe mercancía.",
    "traza_id": "feedc520-ca65-4e84-a6ea-4a36d245c401"
  }
}
```

### ABA-25 · Solicitudes (XML) · PASA

**Objetivo.** Respuesta XML que cumple abastecimiento.xsd.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/solicitudes?por_pagina=3`

```http
Accept: application/xml
X-Traza-Id: d4cf21eb-f187-464d-904d-b955ddbf1963
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 83 ms · traza `d4cf21eb-f187-464d-904d-b955ddbf1963`

```xml
<?xml version='1.0' encoding='utf-8'?>
<solicitudes xmlns="urn:microhubs:v1" version="1"><datos><solicitud><id>54</id><folio>SC-20261126-000054</folio><microhub_id>1</microhub_id><estado>ordenada</estado><motivo>Compra para cancelar</motivo><solicitada_por>2</solicitada_por><decidida_por>1</decidida_por><decision_motivo>Hay presupuesto</decision_motivo><decidida_en>2026-11-26T14:19:46-06:00</decidida_en><creada_en>2026-11-26T14:19:46-06:00</creada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad></linea></lineas></solicitud><solicitud><id>53</id><folio>SC-20261126-000053</folio><microhub_id>1</microhub_id><estado>ordenada</estado><motivo>Se acabó el producto el fin de semana</motivo><solicitada_por>2</solicitada_por><decidida_por>1</decidida_por><decision_motivo>Hay presupuesto</decision_motivo><decidida_en>2026-11-26T14:19:44-06:00</decidida_en><creada_en>2026-11-26T14:19:43-06:00</creada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad></linea></lineas></solicitud><solicitud><id>52</id><folio>SC-20261126-000052</folio><microhub_id>1</microhub_id><estado>ordenada</estado><motivo>Compra para cancelar</motivo><solicitada_por>2</solicitada_por><decidida_por>1</decidida_por><decision_motivo>Hay presupuesto</decision_motivo><decidida_en>2026-11-26T14:04:58-06:00</decidida_en><creada_en>2026-11-26T14:04:58-06:00</creada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad></linea></lineas></solicitud></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>49</total><paginas>17</paginas></paginacion></solicitudes>
```

### ABA-26 · Un auditor consulta · PASA

**Objetivo.** El auditor ve las solicitudes sin poder crear.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: 1aa9f2a0-a2b8-4aa3-92d7-9c5d18227266
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 99 ms · traza `1aa9f2a0-a2b8-4aa3-92d7-9c5d18227266`

```json
{
  "datos": [
    {
      "id": 54,
      "folio": "SC-20261126-000054",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Compra para cancelar",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-11-26T14:19:46-06:00",
      "creada_en": "2026-11-26T14:19:46-06:00",
      "lineas": [
        {
          "producto": {
            "id": 10,
            "nombre": "Sardina en salsa de tomate"
          },
          "cantidad": 46
        }
      ]
    },
    {
      "id": 53,
      "folio": "SC-20261126-000053",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Se acabó el producto el fin de semana",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-11-26T14:19:44-06:00",
      "creada_en": "2026-11-26T14:19:43-06:00",
      "lineas": [
        {
          "producto": {
            "id": 10,
            "nombre": "Sardina en salsa de tomate"
          },
          "cantidad": 46
        }
      ]
    },
    {
      "id": 52,
      "folio": "SC-20261126-000052",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Compra para cancelar",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-11-26T14:04:58-06:00",
      "creada_en": "2026-11-26T14:04:58-06:00",
      "lineas": [
        {
          "producto": {
            "id": 10,
            "nombre": "Sardina en salsa de tomate"
          },
          "cantidad": 46
        }
      ]
    },
    {
      "id": 51,
      "folio": "SC-20261126-000051",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Se acabó el producto el fin de semana",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-11-26T14:04:56-06:00",
      "creada_en": "2026-11-26T14:04:56-06:00",
      "lineas": [
        {
          "producto": {
            "id": 10,
            "nombre": "Sardina en salsa de tomate"
          },
          "cantidad": 46
        }
      ]
    },
    {
      "id": 50,
      "folio": "SC-20261126-000050",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Compra para cancelar",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-11-26T13:51:36-06:00",
      "creada_en": "2026-11-26T13:51:36-06:00",
      "lineas": [
        {
          "producto": {
            "id": 10,
            "nombre": "Sardina en salsa de tomate"
          },
          "cantidad": 46
        }
      ]
    },
    {
      "id": 49,
      "folio": "SC-20261126-000049",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Se acabó el producto el fin de semana",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-11-26T13:51:34-06:00",
      "creada_en": "2026-11-26T13:51:34-06:00",
      "lineas": [
        {
          "producto": {
            "id": 10,
            "nombre": "Sardina en salsa de tomate"
          },
          "cantidad": 46
        }
      ]
    },
    {
      "id": 48,
      "folio": "SC-20261126-000048",
      "microhub_id": 1,
      "estado": "rechazada",
      "motivo": "Prueba XML",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Prueba XML",
      "decidida_en": "2026-11-26T00:32:06-06:00",
      "creada_en": "2026-11-26T00:32:06-06:00",
      "lineas": [
        {
          "producto": {
            "id": 14,
            "nombre": "Café soluble"
          },
          "cantidad": 12
        }
      ]
    },
    {
      "id": 47,
      "folio": "SC-20261126-000047",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-11-26T00:32:05-06:00",
      "creada_en": "2026-11-26T00:32:05-06:00",
      "lineas": [
        {
          "producto": {
            "id": 12,
            "nombre": "Chiles jalapeños en escabeche"
          },
          "cantidad": 63
        }
      ]
    },
    {
      "id": 46,
      "folio": "SC-20261126-000046",
      "microhub_id": 1,
      "estado": "rechazada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": null,
      "decision_motivo": "Limpieza de la prueba",
      "decidida_en": null,
      "creada_en": "2026-11-26T00:32:04-06:00",
      "lineas": [
        {
          "producto": {
            "id": 15,
            "nombre": "Avena en hojuelas"
          },
          "cantidad": 160
        }
      ]
    },
    {
      "id": 45,
      "folio": "SC-20261126-000045",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "ok",
      "decidida_en": "2026-11-26T00:32:01-06:00",
      "creada_en": "2026-11-26T00:32:00-06:00",
      "lineas": [
        {
          "producto": {
            "id": 10,
            "nombre": "Sardina en salsa de tomate"
          },
          "cantidad": 46
        }
      ]
    },
    {
      "id": 43,
      "folio": "SC-20261126-000043",
      "microhub_id": 1,
      "estado": "rechazada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Todavía hay existencia",
      "decidida_en": "2026-11-26T00:32:00-06:00",
      "creada_en": "2026-11-26T00:32:00-06:00",
      "lineas": [
        {
          "producto": {
            "id": 13,
            "nombre": "Puré de tomate"
          },
          "cantidad": 111
        }
      ]
    },
    {
      "id": 42,
      "folio": "SC-20261126-000042",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-11-26T00:31:59-06:00",
      "creada_en": "2026-11-26T00:31:59-06:00",
      "lineas": [
        {
          "producto": {
            "id": 13,
            "nombre": "Puré de tomate"
          },
          "cantidad": 111
        }
      ]
    },
    {
      "id": 41,
      "folio": "SC-20261020-000041",
      "microhub_id": 1,
      "estado": "rechazada",
      "motivo": "Prueba XML",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Prueba XML",
      "decidida_en": "2026-10-20T08:13:55-06:00",
      "creada_en": "2026-10-20T08:13:55-06:00",
      "lineas": [
        {
          "producto": {
            "id": 14,
            "nombre": "Café soluble"
          },
          "cantidad": 12
        }
      ]
    },
    {
      "id": 40,
      "folio": "SC-20261020-000040",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-10-20T08:13:53-06:00",
      "creada_en": "2026-10-20T08:13:53-06:00",
      "lineas": [
        {
          "producto": {
            "id": 12,
            "nombre": "Chiles jalapeños en escabeche"
          },
          "cantidad": 63
        }
      ]
    },
    {
      "id": 39,
      "folio": "SC-20261020-000039",
      "microhub_id": 1,
      "estado": "rechazada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": null,
      "decision_motivo": "Limpieza de la prueba",
      "decidida_en": null,
      "creada_en": "2026-10-20T08:13:52-06:00",
      "lineas": [
        {
          "producto": {
            "id": 15,
            "nombre": "Avena en hojuelas"
          },
          "cantidad": 164
        }
      ]
    },
    {
      "id": 38,
      "folio": "SC-20261020-000038",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "ok",
      "decidida_en": "2026-10-20T08:13:49-06:00",
      "creada_en": "2026-10-20T08:13:48-06:00",
      "lineas": [
        {
          "producto": {
            "id": 10,
            "nombre": "Sardina en salsa de tomate"
          },
          "cantidad": 46
        }
      ]
    },
    {
      "id": 36,
      "folio": "SC-20261020-000036",
      "microhub_id": 1,
      "estado": "rechazada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Todavía hay existencia",
      "decidida_en": "2026-10-20T08:13:48-06:00",
      "creada_en": "2026-10-20T08:13:48-06:00",
      "lineas": [
        {
          "producto": {
            "id": 13,
            "nombre": "Puré de tomate"
          },
          "cantidad": 111
        }
      ]
    },
    {
      "id": 35,
      "folio": "SC-20261020-000035",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-10-20T08:13:47-06:00",
      "creada_en": "2026-10-20T08:13:47-06:00",
      "lineas": [
        {
          "producto": {
            "id": 13,
            "nombre": "Puré de tomate"
          },
          "cantidad": 111
        }
      ]
    },
    {
      "id": 34,
      "folio": "SC-20261020-000034",
      "microhub_id": 1,
      "estado": "rechazada",
      "motivo": "Prueba XML",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Prueba XML",
      "decidida_en": "2026-10-20T00:50:21-06:00",
      "creada_en": "2026-10-20T00:50:21-06:00",
      "lineas": [
        {
          "producto": {
            "id": 14,
            "nombre": "Café soluble"
          },
          "cantidad": 12
        }
      ]
    },
    {
      "id": 33,
      "folio": "SC-20261020-000033",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-10-20T00:50:20-06:00",
      "creada_en": "2026-10-20T00:50:20-06:00",
      "lineas": [
        {
          "producto": {
            "id": 12,
            "nombre": "Chiles jalapeños en escabeche"
          },
          "cantidad": 63
        }
      ]
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 49,
    "paginas": 3
  }
}
```

### ABA-27 · Un cliente consulta · PASA

**Objetivo.** El cliente no tiene abastecimiento.ver.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: 398fd01f-9d49-4ed5-b59c-e7cdb0653404
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 37 ms · traza `398fd01f-9d49-4ed5-b59c-e7cdb0653404`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "398fd01f-9d49-4ed5-b59c-e7cdb0653404"
  }
}
```

## Servicio pedidos · puerto 5104

### ALI-01 · Resumen de pedidos por día y zona · PASA

**Objetivo.** Lo consume el servicio de demanda: pedidos, unidades, venta y clientes por día y zona.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/resumen?por_pagina=5`

```http
Accept: application/json
X-Traza-Id: d3e88896-5778-4188-8636-871c64cb7454
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 128 ms · traza `d3e88896-5778-4188-8636-871c64cb7454`

```json
{
  "datos": [
    {
      "fecha": "2026-11-25",
      "zona_id": 1,
      "categoria_id": null,
      "pedidos": 12,
      "unidades": 58,
      "venta": 1791.5,
      "clientes": 6,
      "no_atendidos": 0
    },
    {
      "fecha": "2026-11-25",
      "zona_id": 2,
      "categoria_id": null,
      "pedidos": 19,
      "unidades": 92,
      "venta": 2657.6,
      "clientes": 8,
      "no_atendidos": 0
    },
    {
      "fecha": "2026-11-25",
      "zona_id": 3,
      "categoria_id": null,
      "pedidos": 12,
      "unidades": 68,
      "venta": 1906.8,
      "clientes": 8,
      "no_atendidos": 0
    },
    {
      "fecha": "2026-11-25",
      "zona_id": 4,
      "categoria_id": null,
      "pedidos": 13,
      "unidades": 64,
      "venta": 1676.5,
      "clientes": 8,
      "no_atendidos": 0
    },
    {
      "fecha": "2026-11-26",
      "zona_id": 1,
      "categoria_id": null,
      "pedidos": 32,
      "unidades": 168,
      "venta": 4542.3,
      "clientes": 7,
      "no_atendidos": 0
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 8,
    "paginas": 2
  }
}
```

**Explicación.** Agrupa por el día de Monterrey (no el de UTC), sin pedidos cancelados. La demanda no atendida solo se suma en consultas de toda la red.

**Evidencia en PostgreSQL.** `SELECT (creado_en AT TIME ZONE 'America/Monterrey')::date AS dia, zona_id, count(*) AS pedidos FROM pedido WHERE estado <> 'cancelado' GROUP BY 1, 2 ORDER BY 1, 2 LIMIT 5`

```json
[
  {
    "dia": "2026-09-04",
    "zona_id": 3,
    "pedidos": 1
  },
  {
    "dia": "2026-09-04",
    "zona_id": 4,
    "pedidos": 1
  },
  {
    "dia": "2026-09-05",
    "zona_id": 1,
    "pedidos": 1
  },
  {
    "dia": "2026-09-05",
    "zona_id": 2,
    "pedidos": 2
  },
  {
    "dia": "2026-09-05",
    "zona_id": 3,
    "pedidos": 1
  }
]
```

### ALI-02 · Resumen con agrupación inválida · PASA

**Objetivo.** Un valor desconocido de «agrupar» se rechaza.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/resumen?agrupar=otra`

```http
Accept: application/json
X-Traza-Id: 6bbc4636-cc5a-4ea1-9c88-c94b561cf7db
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 6 ms · traza `6bbc4636-cc5a-4ea1-9c88-c94b561cf7db`

```json
{
  "error": {
    "codigo": "FILTRO_INVALIDO",
    "mensaje": "Valor no permitido para agrupar: otra.",
    "detalles": [
      {
        "campo": "agrupar",
        "mensaje": "Valor no permitido para agrupar: otra."
      }
    ],
    "traza_id": "6bbc4636-cc5a-4ea1-9c88-c94b561cf7db"
  }
}
```

### ALI-03 · Ventas por producto · PASA

**Objetivo.** Lo consume surtido: unidades y venta de cada producto, sin cancelados.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/ventas?por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 5f3e26af-4389-41e0-9898-ac23d64126e3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 96 ms · traza `5f3e26af-4389-41e0-9898-ac23d64126e3`

```json
{
  "datos": [
    {
      "producto_id": 28,
      "unidades": 64,
      "venta": 480.0,
      "pedidos": 18
    },
    {
      "producto_id": 16,
      "unidades": 43,
      "venta": 709.5,
      "pedidos": 21
    },
    {
      "producto_id": 15,
      "unidades": 40,
      "venta": 1080.0,
      "pedidos": 23
    },
    {
      "producto_id": 7,
      "unidades": 38,
      "venta": 931.0,
      "pedidos": 19
    },
    {
      "producto_id": 23,
      "unidades": 38,
      "venta": 1463.0,
      "pedidos": 23
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 51,
    "paginas": 11
  }
}
```

### ALI-04 · Pedidos listos sin microhub · PASA

**Objetivo.** El microhub es obligatorio.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/listos`

```http
Accept: application/json
X-Traza-Id: 84e5ee96-a5e2-45a0-9bd6-05a6d3d206e4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 6 ms · traza `84e5ee96-a5e2-45a0-9bd6-05a6d3d206e4`

```json
{
  "error": {
    "codigo": "FILTRO_INVALIDO",
    "mensaje": "microhub_id es obligatorio.",
    "detalles": [
      {
        "campo": "microhub_id",
        "mensaje": "microhub_id es obligatorio."
      }
    ],
    "traza_id": "84e5ee96-a5e2-45a0-9bd6-05a6d3d206e4"
  }
}
```

### ALI-05 · Pedidos listos de un microhub · PASA

**Objetivo.** Con las coordenadas de entrega: lo que rutas agrupa y ordena.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/listos?microhub_id=1`

```http
Accept: application/json
X-Traza-Id: 5fa19951-4ab6-4075-bc25-b70258df7528
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 75 ms · traza `5fa19951-4ab6-4075-bc25-b70258df7528`

```json
{
  "datos": [
    {
      "id": 428,
      "folio": "PED-20261126-000428",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "latitud": 25.753225,
      "longitud": -100.365213,
      "total": 177.0,
      "listo_en": "2026-11-26T00:33:03-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 100,
    "total": 1,
    "paginas": 1
  }
}
```

**Evidencia en PostgreSQL.** `SELECT count(*) AS listos FROM pedido WHERE microhub_id = %s AND estado = 'en_preparacion' AND listo_en IS NOT NULL`

```json
[
  {
    "listos": 1
  }
]
```

## Servicio entregas · puerto 5105

### ALI-06 · Repartidores activos · PASA

**Objetivo.** Con las entregas que tienen abiertas hoy; lo consume rutas.

**Petición.** `GET http://entregas:5105/api/v1/entregas/repartidores`

```http
Accept: application/json
X-Traza-Id: ca5bd934-edd3-4b9e-9396-9bcc1b7d6cb0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 59 ms · traza `ca5bd934-edd3-4b9e-9396-9bcc1b7d6cb0`

```json
{
  "datos": [
    {
      "id": 7,
      "nombre": "Ramiro Alanís Lozano",
      "entregas_abiertas": 0
    },
    {
      "id": 8,
      "nombre": "Diana Sepúlveda Ibarra",
      "entregas_abiertas": 0
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 100,
    "total": 2,
    "paginas": 1
  }
}
```

## Servicio inventario · puerto 5111

### ALI-07 · Quiebres de inventario · PASA

**Objetivo.** Veces que una salida dejó el producto en cero y si hoy está agotado; lo consume surtido.

**Petición.** `GET http://inventario:5111/api/v1/inventario/quiebres?microhub_id=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 151ff0b8-8889-4227-983d-94c91e1662a5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 110 ms · traza `151ff0b8-8889-4227-983d-94c91e1662a5`

```json
{
  "datos": [
    {
      "microhub_id": 1,
      "producto_id": 21,
      "quiebres": 1,
      "ultimo": "2026-10-19T19:30:44-06:00",
      "agotado_hoy": true
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 1,
    "paginas": 1
  }
}
```

### ALI-08 · Quiebres con ventana inválida · PASA

**Objetivo.** dias debe estar entre 1 y 365.

**Petición.** `GET http://inventario:5111/api/v1/inventario/quiebres?dias=0`

```http
Accept: application/json
X-Traza-Id: 89070aa6-ebb7-4432-888d-36357d5c92dc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 7 ms · traza `89070aa6-ebb7-4432-888d-36357d5c92dc`

```json
{
  "error": {
    "codigo": "FILTRO_INVALIDO",
    "mensaje": "dias debe estar entre 1 y 365.",
    "detalles": [
      {
        "campo": "dias",
        "mensaje": "dias debe estar entre 1 y 365."
      }
    ],
    "traza_id": "89070aa6-ebb7-4432-888d-36357d5c92dc"
  }
}
```

## Servicio demanda · puerto 5115

### DEM-01 · Observaciones de demanda · PASA

**Objetivo.** Pedidos por día, zona y categoría, con la fuente de cada dato.

**Petición.** `GET http://demanda:5115/api/v1/demanda/observaciones?nivel=total&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 6080c91f-15ee-45ab-9f46-8f3a853d62a0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 235 ms · traza `6080c91f-15ee-45ab-9f46-8f3a853d62a0`

```json
{
  "datos": [
    {
      "fecha": "2026-11-25",
      "zona": {
        "id": 1,
        "nombre": "San Bernabé Centro"
      },
      "categoria": null,
      "pedidos": 17,
      "unidades": 88,
      "venta": 2423.7,
      "clientes": 14,
      "no_atendidos": 1,
      "fuente": "sintetica"
    },
    {
      "fecha": "2026-11-25",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "categoria": null,
      "pedidos": 11,
      "unidades": 57,
      "venta": 1506.05,
      "clientes": 9,
      "no_atendidos": 1,
      "fuente": "sintetica"
    },
    {
      "fecha": "2026-11-25",
      "zona": {
        "id": 3,
        "nombre": "Paseo de San Bernabé"
      },
      "categoria": null,
      "pedidos": 9,
      "unidades": 47,
      "venta": 1165.48,
      "clientes": 8,
      "no_atendidos": 1,
      "fuente": "sintetica"
    },
    {
      "fecha": "2026-11-25",
      "zona": {
        "id": 4,
        "nombre": "San Bernabé X (F-113)"
      },
      "categoria": null,
      "pedidos": 8,
      "unidades": 42,
      "venta": 1017.12,
      "clientes": 7,
      "no_atendidos": 0,
      "fuente": "sintetica"
    },
    {
      "fecha": "2026-11-24",
      "zona": {
        "id": 1,
        "nombre": "San Bernabé Centro"
      },
      "categoria": null,
      "pedidos": 16,
      "unidades": 83,
      "venta": 2281.13,
      "clientes": 14,
      "no_atendidos": 1,
      "fuente": "sintetica"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 240,
    "paginas": 48
  }
}
```

**Explicación.** La historia de demostración es sintética y lo dice en cada renglón (fuente = sintetica): no se hace pasar por ventas reales.

**Evidencia en PostgreSQL.** `SELECT fuente, count(*) AS observaciones, min(fecha) AS desde, max(fecha) AS hasta FROM demanda_observacion GROUP BY fuente`

```json
[
  {
    "fuente": "sintetica",
    "observaciones": 2352,
    "desde": "2026-08-20",
    "hasta": "2026-11-25"
  }
]
```

### DEM-02 · Observaciones (XML) · PASA

**Objetivo.** Respuesta XML que cumple demanda.xsd.

**Petición.** `GET http://demanda:5115/api/v1/demanda/observaciones?por_pagina=3`

```http
Accept: application/xml
X-Traza-Id: 2fd0e03b-a496-4b11-8e63-a59dedc232c6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 101 ms · traza `2fd0e03b-a496-4b11-8e63-a59dedc232c6`

```xml
<?xml version='1.0' encoding='utf-8'?>
<observaciones_demanda xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><datos><observacion><fecha>2026-11-25</fecha><zona><id>1</id><nombre>San Bernabé Centro</nombre></zona><categoria xsi:nil="true" /><pedidos>17</pedidos><unidades>88</unidades><venta>2423.70</venta><clientes>14</clientes><no_atendidos>1</no_atendidos><fuente>sintetica</fuente></observacion><observacion><fecha>2026-11-25</fecha><zona><id>1</id><nombre>San Bernabé Centro</nombre></zona><categoria><id>1</id><nombre>Abarrote básico</nombre></categoria><pedidos>17</pedidos><unidades>40</unidades><venta>1090.67</venta><clientes>0</clientes><no_atendidos>0</no_atendidos><fuente>sintetica</fuente></observacion><observacion><fecha>2026-11-25</fecha><zona><id>1</id><nombre>San Bernabé Centro</nombre></zona><categoria><id>2</id><nombre>Bebidas</nombre></categoria><pedidos>7</pedidos><unidades>18</unidades><venta>484.74</venta><clientes>0</clientes><no_atendidos>0</no_atendidos><fuente>sintetica</fuente></observacion></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>1440</total><paginas>480</paginas></paginacion></observaciones_demanda>
```

### DEM-03 · Fuente desconocida · PASA

**Objetivo.** Un filtro desconocido se rechaza.

**Petición.** `GET http://demanda:5115/api/v1/demanda/observaciones?fuente=inventada`

```http
Accept: application/json
X-Traza-Id: 700f6b4e-140e-4694-b3da-621d37b07e34
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 47 ms · traza `700f6b4e-140e-4694-b3da-621d37b07e34`

```json
{
  "error": {
    "codigo": "FILTRO_INVALIDO",
    "mensaje": "Valor no permitido para fuente: inventada.",
    "detalles": [
      {
        "campo": "fuente",
        "mensaje": "Valor no permitido para fuente: inventada."
      }
    ],
    "traza_id": "700f6b4e-140e-4694-b3da-621d37b07e34"
  }
}
```

### DEM-04 · El operador consulta la demanda · PASA

**Objetivo.** Sin demanda.ver.

**Petición.** `GET http://demanda:5115/api/v1/demanda/observaciones`

```http
Accept: application/json
X-Traza-Id: 1d56ab4b-b1d0-4446-8082-8ff1d06452fc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 34 ms · traza `1d56ab4b-b1d0-4446-8082-8ff1d06452fc`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "1d56ab4b-b1d0-4446-8082-8ff1d06452fc"
  }
}
```

### DEM-05 · Resumen por zona · PASA

**Objetivo.** Pedidos, ticket promedio, pedidos por cliente y demanda no atendida.

**Petición.** `GET http://demanda:5115/api/v1/demanda/resumen`

```http
Accept: application/json
X-Traza-Id: 22adf0e1-3368-4a43-bb03-21c9946d194d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 111 ms · traza `22adf0e1-3368-4a43-bb03-21c9946d194d`

```json
{
  "desde": "2026-09-27",
  "hasta": "2026-11-25",
  "dias": 60,
  "total": {
    "pedidos": 2970,
    "pedidos_dia": 49.5,
    "unidades_por_pedido": 5.2,
    "venta": 400449.26,
    "ticket_promedio": 134.83,
    "pedidos_por_cliente": 1.17,
    "no_atendidos": 208,
    "pct_no_atendida": 6.5
  },
  "zonas": [
    {
      "zona": {
        "id": 1,
        "nombre": "San Bernabé Centro"
      },
      "pedidos": 1037,
      "pedidos_dia": 17.28,
      "unidades_por_pedido": 5.2,
      "venta": 140030.05,
      "ticket_promedio": 135.03,
      "pedidos_por_cliente": 1.17,
      "no_atendidos": 61,
      "pct_no_atendida": 5.6
    },
    {
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "pedidos": 758,
      "pedidos_dia": 12.63,
      "unidades_por_pedido": 5.2,
      "venta": 102092.05,
      "ticket_promedio": 134.69,
      "pedidos_por_cliente": 1.19,
      "no_atendidos": 60,
      "pct_no_atendida": 7.3
    },
    {
      "zona": {
        "id": 3,
        "nombre": "Paseo de San Bernabé"
      },
      "pedidos": 646,
      "pedidos_dia": 10.77,
      "unidades_por_pedido": 5.2,
      "venta": 86960.01,
      "ticket_promedio": 134.61,
      "pedidos_por_cliente": 1.16,
      "no_atendidos": 60,
      "pct_no_atendida": 8.5
    },
    {
      "zona": {
        "id": 4,
        "nombre": "San Bernabé X (F-113)"
      },
      "pedidos": 529,
      "pedidos_dia": 8.82,
      "unidades_por_pedido": 5.21,
      "venta": 71367.15,
      "ticket_promedio": 134.91,
      "pedidos_por_cliente": 1.16,
      "no_atendidos": 27,
      "pct_no_atendida": 4.9
    }
  ],
  "observaciones_por_fuente": {
    "pedidos": 0,
    "sintetica": 240,
    "manual": 0
  }
}
```

**Evidencia en PostgreSQL.** `SELECT zona_id, sum(pedidos) AS pedidos, round(sum(venta) / NULLIF(sum(pedidos), 0), 2) AS ticket FROM demanda_observacion WHERE categoria_id IS NULL GROUP BY zona_id ORDER BY zona_id`

```json
[
  {
    "zona_id": 1,
    "pedidos": 1657,
    "ticket": "134.93"
  },
  {
    "zona_id": 2,
    "pedidos": 1215,
    "ticket": "134.37"
  },
  {
    "zona_id": 3,
    "pedidos": 1032,
    "ticket": "134.39"
  },
  {
    "zona_id": 4,
    "pedidos": 847,
    "ticket": "134.98"
  }
]
```

### DEM-06 · Patrones de la semana · PASA

**Objetivo.** Índice de cada día de la semana y venta por categoría.

**Petición.** `GET http://demanda:5115/api/v1/demanda/patrones`

```http
Accept: application/json
X-Traza-Id: c6d65ee0-ba27-40d1-a446-a6d54d8039da
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 134 ms · traza `c6d65ee0-ba27-40d1-a446-a6d54d8039da`

```json
{
  "desde": "2026-09-27",
  "hasta": "2026-11-25",
  "dias": 60,
  "suficiente": true,
  "semanal": [
    {
      "dia": 1,
      "nombre": "lunes",
      "pedidos_promedio": 44.22,
      "indice": 0.893
    },
    {
      "dia": 2,
      "nombre": "martes",
      "pedidos_promedio": 41.78,
      "indice": 0.844
    },
    {
      "dia": 3,
      "nombre": "miércoles",
      "pedidos_promedio": 43.78,
      "indice": 0.884
    },
    {
      "dia": 4,
      "nombre": "jueves",
      "pedidos_promedio": 46.38,
      "indice": 0.937
    },
    {
      "dia": 5,
      "nombre": "viernes",
      "pedidos_promedio": 57.12,
      "indice": 1.154
    },
    {
      "dia": 6,
      "nombre": "sábado",
      "pedidos_promedio": 64.5,
      "indice": 1.303
    },
    {
      "dia": 7,
      "nombre": "domingo",
      "pedidos_promedio": 50.89,
      "indice": 1.028
    }
  ],
  "categorias": [
    {
      "categoria": {
        "id": 1,
        "nombre": "Abarrote básico"
      },
      "unidades": 6955,
      "venta": 180202.25,
      "pct_venta": 45.0
    },
    {
      "categoria": {
        "id": 2,
        "nombre": "Bebidas"
      },
      "unidades": 3069,
      "venta": 80089.9,
      "pct_venta": 20.0
    },
    {
      "categoria": {
        "id": 3,
        "nombre": "Lácteos y huevo"
      },
      "unidades": 2317,
      "venta": 60067.41,
      "pct_venta": 15.0
    },
    {
      "categoria": {
        "id": 4,
        "nombre": "Limpieza del hogar"
      },
      "unidades": 1852,
      "venta": 48053.83,
      "pct_venta": 12.0
    },
    {
      "categoria": {
        "id": 5,
        "nombre": "Higiene personal"
      },
      "unidades": 1254,
      "venta": 32035.93,
      "pct_venta": 8.0
    }
  ],
  "dia_pico": "sábado",
  "dia_valle": "martes",
  "fuerza_estacional": 1.54
}
```

**Explicación.** Índice = promedio de ese día ÷ promedio general. Con menos de dos semanas completas vale 1 y el resultado lo dice (suficiente = false).

### DEM-07 · Proyección con banda de error · PASA

**Objetivo.** 14 días con mínimo y máximo; la banda sale del error del propio ajuste.

**Petición.** `GET http://demanda:5115/api/v1/demanda/proyeccion`

```http
Accept: application/json
X-Traza-Id: 4c802881-90e0-40bc-a66f-97acc2d1c8a5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 111 ms · traza `4c802881-90e0-40bc-a66f-97acc2d1c8a5`

```json
{
  "metodo": "tendencia_estacional",
  "zona": null,
  "historia_desde": "2026-09-27",
  "historia_hasta": "2026-11-25",
  "historia_dias": 60,
  "horizonte": 14,
  "indices_confiables": true,
  "nivel_pedidos_dia": 49.87,
  "pendiente_pedidos_dia": 0.013,
  "desviacion_error": 1.88,
  "total_pedidos": 703.9,
  "promedio_dia": 50.28,
  "serie": [
    {
      "fecha": "2026-11-26",
      "pedidos": 46.7,
      "minimo": 44.3,
      "maximo": 49.1
    },
    {
      "fecha": "2026-11-27",
      "pedidos": 57.6,
      "minimo": 55.2,
      "maximo": 60.0
    },
    {
      "fecha": "2026-11-28",
      "pedidos": 65.0,
      "minimo": 62.6,
      "maximo": 67.4
    },
    {
      "fecha": "2026-11-29",
      "pedidos": 51.3,
      "minimo": 48.9,
      "maximo": 53.7
    },
    {
      "fecha": "2026-11-30",
      "pedidos": 44.6,
      "minimo": 42.2,
      "maximo": 47.0
    },
    {
      "fecha": "2026-12-01",
      "pedidos": 42.2,
      "minimo": 39.8,
      "maximo": 44.6
    },
    {
      "fecha": "2026-12-02",
      "pedidos": 44.2,
      "minimo": 41.8,
      "maximo": 46.6
    },
    {
      "fecha": "2026-12-03",
      "pedidos": 46.8,
      "minimo": 44.4,
      "maximo": 49.2
    },
    {
      "fecha": "2026-12-04",
      "pedidos": 57.7,
      "minimo": 55.3,
      "maximo": 60.1
    },
    {
      "fecha": "2026-12-05",
      "pedidos": 65.1,
      "minimo": 62.7,
      "maximo": 67.5
    },
    {
      "fecha": "2026-12-06",
      "pedidos": 51.4,
      "minimo": 49.0,
      "maximo": 53.8
    },
    {
      "fecha": "2026-12-07",
      "pedidos": 44.7,
      "minimo": 42.3,
      "maximo": 47.1
    },
    {
      "fecha": "2026-12-08",
      "pedidos": 42.2,
      "minimo": 39.8,
      "maximo": 44.6
    },
    {
      "fecha": "2026-12-09",
      "pedidos": 44.3,
      "minimo": 41.9,
      "maximo": 46.7
    }
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 1.28,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 60.0,
      "modificado": false
    }
  ]
}
```

**Explicación.** Tendencia por mínimos cuadrados sobre la serie sin estacionalidad, por el índice del día. Banda = proyección ± 1.28 desviaciones.

### DEM-08 · Proyección con promedio móvil · PASA

**Objetivo.** El otro método: nivel de los últimos 7 días, sin tendencia.

**Petición.** `GET http://demanda:5115/api/v1/demanda/proyeccion?metodo=promedio_movil&horizonte=7`

```http
Accept: application/json
X-Traza-Id: 14b93c2a-51ad-45f2-9f83-3962ad1beecb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 71 ms · traza `14b93c2a-51ad-45f2-9f83-3962ad1beecb`

```json
{
  "metodo": "promedio_movil",
  "zona": null,
  "historia_desde": "2026-09-27",
  "historia_hasta": "2026-11-25",
  "historia_dias": 60,
  "horizonte": 7,
  "indices_confiables": true,
  "nivel_pedidos_dia": 50.8,
  "pendiente_pedidos_dia": 0.0,
  "desviacion_error": 1.77,
  "total_pedidos": 357.8,
  "promedio_dia": 51.12,
  "serie": [
    {
      "fecha": "2026-11-26",
      "pedidos": 47.6,
      "minimo": 45.3,
      "maximo": 49.9
    },
    {
      "fecha": "2026-11-27",
      "pedidos": 58.6,
      "minimo": 56.4,
      "maximo": 60.9
    },
    {
      "fecha": "2026-11-28",
      "pedidos": 66.2,
      "minimo": 63.9,
      "maximo": 68.5
    },
    {
      "fecha": "2026-11-29",
      "pedidos": 52.2,
      "minimo": 50.0,
      "maximo": 54.5
    },
    {
      "fecha": "2026-11-30",
      "pedidos": 45.4,
      "minimo": 43.1,
      "maximo": 47.6
    },
    {
      "fecha": "2026-12-01",
      "pedidos": 42.9,
      "minimo": 40.6,
      "maximo": 45.1
    },
    {
      "fecha": "2026-12-02",
      "pedidos": 44.9,
      "minimo": 42.7,
      "maximo": 47.2
    }
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 1.28,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 60.0,
      "modificado": false
    }
  ]
}
```

### DEM-09 · Método inventado · PASA

**Objetivo.** Solo existen dos métodos.

**Petición.** `GET http://demanda:5115/api/v1/demanda/proyeccion?metodo=magico`

```http
Accept: application/json
X-Traza-Id: da2e9be6-4c6e-4252-a173-664c3a8adc4f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 31 ms · traza `da2e9be6-4c6e-4252-a173-664c3a8adc4f`

```json
{
  "error": {
    "codigo": "FILTRO_INVALIDO",
    "mensaje": "Valor no permitido para metodo: magico.",
    "detalles": [
      {
        "campo": "metodo",
        "mensaje": "Valor no permitido para metodo: magico."
      }
    ],
    "traza_id": "da2e9be6-4c6e-4252-a173-664c3a8adc4f"
  }
}
```

### DEM-10 · Comparación contra lo observado · PASA

**Objetivo.** Se ocultan los últimos 7 días, se proyectan y se miden el error y el sesgo.

**Petición.** `GET http://demanda:5115/api/v1/demanda/comparacion`

```http
Accept: application/json
X-Traza-Id: ea698e9b-832e-4ccc-834f-6378e89720ef
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 65 ms · traza `ea698e9b-832e-4ccc-834f-6378e89720ef`

```json
{
  "metodo": "tendencia_estacional",
  "zona": null,
  "dias_prueba": 7,
  "dias_entrenamiento": 53,
  "mape_pct": 3.7,
  "sesgo_pct": -3.2,
  "dentro_banda_pct": 71.4,
  "filas": [
    {
      "fecha": "2026-11-19",
      "observado": 47,
      "proyectado": 46.2,
      "error": -0.8,
      "error_pct": -1.7
    },
    {
      "fecha": "2026-11-20",
      "observado": 56,
      "proyectado": 57.2,
      "error": 1.2,
      "error_pct": 2.1
    },
    {
      "fecha": "2026-11-21",
      "observado": 68,
      "proyectado": 63.8,
      "error": -4.2,
      "error_pct": -6.1
    },
    {
      "fecha": "2026-11-22",
      "observado": 54,
      "proyectado": 50.4,
      "error": -3.6,
      "error_pct": -6.7
    },
    {
      "fecha": "2026-11-23",
      "observado": 45,
      "proyectado": 44.0,
      "error": -1.0,
      "error_pct": -2.2
    },
    {
      "fecha": "2026-11-24",
      "observado": 43,
      "proyectado": 41.5,
      "error": -1.5,
      "error_pct": -3.5
    },
    {
      "fecha": "2026-11-25",
      "observado": 45,
      "proyectado": 43.5,
      "error": -1.5,
      "error_pct": -3.3
    }
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 1.28,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 7.0,
      "modificado": false
    }
  ]
}
```

**Explicación.** MAPE = promedio de |proyectado − observado| ÷ observado. «dentro_banda_pct» dice cuántos días reales cayeron dentro de la banda.

### DEM-11 · Demanda potencial · PASA

**Objetivo.** Hogares × penetración × pedidos por hogar, contra lo observado.

**Petición.** `GET http://demanda:5115/api/v1/demanda/potencial`

```http
Accept: application/json
X-Traza-Id: 395e0e75-93f1-4be7-91fd-7e23cc75d57a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 118 ms · traza `395e0e75-93f1-4be7-91fd-7e23cc75d57a`

```json
{
  "zona": null,
  "hogares": 6709,
  "penetracion": 0.12,
  "pedidos_hogar_mes": 2.5,
  "pedidos_mes_potencial": 2012.7,
  "pedidos_dia_potencial": 67.1,
  "pedidos_dia_observados": 50.1,
  "cuota_capturada_pct": 74.6,
  "brecha_pedidos_dia": 17.0,
  "escenarios": [
    {
      "penetracion": 0.04,
      "pedidos_mes": 670.9,
      "pedidos_dia": 22.4,
      "cuota_capturada_pct": 223.9,
      "brecha_pedidos_dia": -27.7
    },
    {
      "penetracion": 0.08,
      "pedidos_mes": 1341.8,
      "pedidos_dia": 44.7,
      "cuota_capturada_pct": 111.9,
      "brecha_pedidos_dia": -5.3
    },
    {
      "penetracion": 0.12,
      "pedidos_mes": 2012.7,
      "pedidos_dia": 67.1,
      "cuota_capturada_pct": 74.6,
      "brecha_pedidos_dia": 17.0
    },
    {
      "penetracion": 0.16,
      "pedidos_mes": 2683.6,
      "pedidos_dia": 89.5,
      "cuota_capturada_pct": 56.0,
      "brecha_pedidos_dia": 39.4
    },
    {
      "penetracion": 0.2,
      "pedidos_mes": 3354.5,
      "pedidos_dia": 111.8,
      "cuota_capturada_pct": 44.8,
      "brecha_pedidos_dia": 61.7
    }
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 0.12,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 2.5,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.6,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    }
  ]
}
```

**Explicación.** Penetración 12 % y 2.5 pedidos por hogar al mes son supuestos documentados (GET /demanda/supuestos): no son datos medidos.

### DEM-12 · Potencial con otra penetración · PASA

**Objetivo.** El cálculo no cambia la configuración: solo la consulta.

**Petición.** `GET http://demanda:5115/api/v1/demanda/potencial?penetracion=0.2`

```http
Accept: application/json
X-Traza-Id: fdfedc82-2089-42ff-8c41-cd03dcf2040d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 134 ms · traza `fdfedc82-2089-42ff-8c41-cd03dcf2040d`

```json
{
  "zona": null,
  "hogares": 6709,
  "penetracion": 0.2,
  "pedidos_hogar_mes": 2.5,
  "pedidos_mes_potencial": 3354.5,
  "pedidos_dia_potencial": 111.8,
  "pedidos_dia_observados": 50.1,
  "cuota_capturada_pct": 44.8,
  "brecha_pedidos_dia": 61.7,
  "escenarios": [
    {
      "penetracion": 0.04,
      "pedidos_mes": 670.9,
      "pedidos_dia": 22.4,
      "cuota_capturada_pct": 223.9,
      "brecha_pedidos_dia": -27.7
    },
    {
      "penetracion": 0.08,
      "pedidos_mes": 1341.8,
      "pedidos_dia": 44.7,
      "cuota_capturada_pct": 111.9,
      "brecha_pedidos_dia": -5.3
    },
    {
      "penetracion": 0.12,
      "pedidos_mes": 2012.7,
      "pedidos_dia": 67.1,
      "cuota_capturada_pct": 74.6,
      "brecha_pedidos_dia": 17.0
    },
    {
      "penetracion": 0.16,
      "pedidos_mes": 2683.6,
      "pedidos_dia": 89.5,
      "cuota_capturada_pct": 56.0,
      "brecha_pedidos_dia": 39.4
    },
    {
      "penetracion": 0.2,
      "pedidos_mes": 3354.5,
      "pedidos_dia": 111.8,
      "cuota_capturada_pct": 44.8,
      "brecha_pedidos_dia": 61.7
    }
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 0.12,
      "modificado": true
    },
    {
      "clave": "********",
      "valor": 2.5,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.6,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    }
  ]
}
```

### DEM-13 · Sincronizar sin permiso · PASA

**Objetivo.** Traer la demanda real exige demanda.editar.

**Petición.** `POST http://demanda:5115/api/v1/demanda/sincronizacion`

```http
Accept: application/json
X-Traza-Id: e62feaf2-9f4a-4203-a084-fd863154023d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{
  "desde": "2026-11-24",
  "hasta": "2026-11-26"
}
```

**Respuesta.** HTTP 403 (esperado 403) · 31 ms · traza `e62feaf2-9f4a-4203-a084-fd863154023d`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "e62feaf2-9f4a-4203-a084-fd863154023d"
  }
}
```

### DEM-14 · Sincronizar con pedidos reales · PASA

**Objetivo.** Lo sintético del rango se reemplaza por lo real.

**Petición.** `POST http://demanda:5115/api/v1/demanda/sincronizacion`

```http
Accept: application/json
X-Traza-Id: da988b0c-c36f-4427-aafe-4d508aa1bbcf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "desde": "2026-11-24",
  "hasta": "2026-11-26"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 165 ms · traza `da988b0c-c36f-4427-aafe-4d508aa1bbcf`

```json
{
  "desde": "2026-11-24",
  "hasta": "2026-11-26",
  "filas_escritas": 8,
  "pedidos_leidos": 174,
  "sinteticas_reemplazadas": 48
}
```

**Explicación.** Lee pedidos/resumen y guarda las observaciones como propias (fuente = pedidos). Es idempotente: repetirlo deja lo mismo.

**Evidencia en PostgreSQL.** `SELECT fuente, count(*) AS observaciones FROM demanda_observacion WHERE fecha BETWEEN %s AND %s GROUP BY fuente`

```json
[
  {
    "fuente": "pedidos",
    "observaciones": 8
  }
]
```

### DEM-15 · Sincronizar con fechas inválidas · PASA

**Objetivo.** desde no puede ser posterior a hasta.

**Petición.** `POST http://demanda:5115/api/v1/demanda/sincronizacion`

```http
Accept: application/json
X-Traza-Id: 4a304771-f653-4af5-b43f-95d8b1293514
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "desde": "2026-10-10",
  "hasta": "2026-10-01"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 13 ms · traza `4a304771-f653-4af5-b43f-95d8b1293514`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "hasta",
        "mensaje": "El rango va de desde a hasta, con 400 días como máximo."
      }
    ],
    "traza_id": "4a304771-f653-4af5-b43f-95d8b1293514"
  }
}
```

### DEM-16 · Sincronizar (XML) · PASA

**Objetivo.** El cuerpo XML se valida contra demanda.xsd antes de procesarse.

**Petición.** `POST http://demanda:5115/api/v1/demanda/sincronizacion`

```http
Accept: application/xml
X-Traza-Id: 59d1722c-7c37-4f8d-875e-f57c11789315
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><sincronizacion_nueva xmlns="urn:microhubs:v1"><desde>2026-11-26</desde><hasta>2026-11-26</hasta></sincronizacion_nueva>
```

**Respuesta.** HTTP 201 (esperado 201) · 134 ms · traza `59d1722c-7c37-4f8d-875e-f57c11789315`

```xml
<?xml version='1.0' encoding='utf-8'?>
<sincronizacion xmlns="urn:microhubs:v1" version="1"><desde>2026-11-26</desde><hasta>2026-11-26</hasta><filas_escritas>4</filas_escritas><pedidos_leidos>118</pedidos_leidos><sinteticas_reemplazadas>0</sinteticas_reemplazadas></sincronizacion>
```

### DEM-17 · Supuestos de la demanda · PASA

**Objetivo.** Valor, origen (medido, supuesto o normativo), justificación y cómo calibrarlo.

**Petición.** `GET http://demanda:5115/api/v1/demanda/supuestos`

```http
Accept: application/json
X-Traza-Id: 1bca9792-ceec-4d4c-8039-4af0a7821475
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 32 ms · traza `1bca9792-ceec-4d4c-8039-4af0a7821475`

```json
{
  "datos": [
    {
      "clave": "********",
      "valor": "7",
      "unidad": "días",
      "origen": "supuesto",
      "justificacion": "Se ocultan los últimos 7 días para medir el error del modelo contra lo que de verdad pasó.",
      "como_calibrar": "Ninguna; es el tamaño de la prueba."
    },
    {
      "clave": "********",
      "valor": "1.28",
      "unidad": "desviaciones",
      "origen": "supuesto",
      "justificacion": "Con 1.28 desviaciones, la banda deja afuera 10 % por arriba y 10 % por abajo si los errores se reparten como una campana.",
      "como_calibrar": "Revisar qué porcentaje de los días reales cae dentro de la banda."
    },
    {
      "clave": "********",
      "valor": "14",
      "unidad": "días",
      "origen": "supuesto",
      "justificacion": "Dos semanas: cubre el plazo de reposición y de contratación de personal.",
      "como_calibrar": "Se ajusta al plazo de decisión que se quiera apoyar."
    },
    {
      "clave": "********",
      "valor": "2.5",
      "unidad": "pedidos",
      "origen": "supuesto",
      "justificacion": "Un hogar que usa el servicio pide unas dos veces y media al mes: la compra grande del súper no se sustituye, pero sí las de reposición.",
      "como_calibrar": "Frecuencia de compra observada (pedidos entre clientes distintos)."
    },
    {
      "clave": "********",
      "valor": "0.12",
      "unidad": "fracción",
      "origen": "supuesto",
      "justificacion": "Parte de los hogares que pide a domicilio en un mes. 12 % es…(142 caracteres)",
      "como_calibrar": "Clientes distintos por mes entre los hogares de la zona."
    },
    {
      "clave": "********",
      "valor": "60",
      "unidad": "días",
      "origen": "supuesto",
      "justificacion": "Con 60 días hay ocho semanas completas, suficientes para ver el patrón de cada día de la semana.",
      "como_calibrar": "Probar con otras ventanas y comparar el error del respaldo (backtest)."
    },
    {
      "clave": "********",
      "valor": "30",
      "unidad": "días",
      "origen": "normativo",
      "justificacion": "El microhub opera todos los días del mes.",
      "como_calibrar": "Cambiar si se decide cerrar un día a la semana."
    },
    {
      "clave": "********",
      "valor": "3.6",
      "unidad": "personas",
      "origen": "supuesto",
      "justificacion": "Personas por hogar para convertir población en hogares. Se u…(145 caracteres)",
      "como_calibrar": "Tomar el dato del Censo de Población y Vivienda (INEGI) de la AGEB de cada colonia."
    }
  ]
}
```

**Evidencia en PostgreSQL.** `SELECT clave, origen, left(justificacion, 80) AS justificacion FROM supuesto_documentado WHERE servicio = 'demanda' ORDER BY clave`

```json
[
  {
    "clave": "dem_backtest_dias",
    "origen": "supuesto",
    "justificacion": "Se ocultan los últimos 7 días para medir el error del modelo contra lo que de ve"
  },
  {
    "clave": "dem_banda_z",
    "origen": "supuesto",
    "justificacion": "Con 1.28 desviaciones, la banda deja afuera 10 % por arriba y 10 % por abajo si "
  },
  {
    "clave": "dem_horizonte_dias",
    "origen": "supuesto",
    "justificacion": "Dos semanas: cubre el plazo de reposición y de contratación de personal."
  },
  {
    "clave": "dem_pedidos_hogar_mes",
    "origen": "supuesto",
    "justificacion": "Un hogar que usa el servicio pide unas dos veces y media al mes: la compra grand"
  },
  {
    "clave": "dem_penetracion",
    "origen": "supuesto",
    "justificacion": "Parte de los hogares que pide a domicilio en un mes. 12 % es un valor prudente p"
  },
  {
    "clave": "dem_ventana_dias",
    "origen": "supuesto",
    "justificacion": "Con 60 días hay ocho semanas completas, suficientes para ver el patrón de cada d"
  }
]
```

## Servicio cobertura · puerto 5116

### COB-01 · Cobertura por zona · PASA

**Objetivo.** Qué microhubs cubren cada zona, a cuántos minutos y si hay traslape.

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/zonas`

```http
Accept: application/json
X-Traza-Id: b60c8c9a-7c67-4fb3-b549-4ea4e27943b8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 48 ms · traza `b60c8c9a-7c67-4fb3-b549-4ea4e27943b8`

```json
{
  "datos": [
    {
      "zona": {
        "id": 1,
        "nombre": "San Bernabé Centro"
      },
      "hogares": 2339,
      "estado": "cubierta",
      "solapada": false,
      "cubierta_por": [
        {
          "microhub": {
            "id": 1,
            "nombre": "Microhub San Bernabé Centro"
          },
          "distancia_km": 0.62,
          "distancia_calle_km": 0.8,
          "minutos": 6.2,
          "cubre": true,
          "dentro_promesa": true
        }
      ],
      "mas_cercano": {
        "microhub": {
          "id": 1,
          "nombre": "Microhub San Bernabé Centro"
        },
        "distancia_km": 0.62,
        "distancia_calle_km": 0.8,
        "minutos": 6.2,
        "cubre": true,
        "dentro_promesa": true
      },
      "minutos_mejor": 6.2
    },
    {
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "hogares": 1717,
      "estado": "cubierta",
      "solapada": true,
      "cubierta_por": [
        {
          "microhub": {
            "id": 2,
            "nombre": "Microhub Valles"
          },
          "distancia_km": 0.41,
          "distancia_calle_km": 0.53,
          "minutos": 5.5,
          "cubre": true,
          "dentro_promesa": true
        },
        {
          "microhub": {
            "id": 1,
            "nombre": "Microhub San Bernabé Centro"
          },
          "distancia_km": 0.75,
          "distancia_calle_km": 0.97,
          "minutos": 6.7,
          "cubre": true,
          "dentro_promesa": true
        }
      ],
      "mas_cercano": {
        "microhub": {
          "id": 2,
          "nombre": "Microhub Valles"
        },
        "distancia_km": 0.41,
        "distancia_calle_km": 0.53,
        "minutos": 5.5,
        "cubre": true,
        "dentro_promesa": true
      },
      "minutos_mejor": 5.5
    },
    {
      "zona": {
        "id": 3,
        "nombre": "Paseo de San Bernabé"
      },
      "hogares": 1456,
      "estado": "cubierta",
      "solapada": true,
      "cubierta_por": [
        {
          "microhub": {
            "id": 2,
            "nombre": "Microhub Valles"
          },
          "distancia_km": 0.37,
          "distancia_calle_km": 0.49,
          "minutos": 5.3,
          "cubre": true,
          "dentro_promesa": true
        },
        {
          "microhub": {
            "id": 3,
            "nombre": "Microhub Poniente F-113"
          },
          "distancia_km": 1.1,
          "distancia_calle_km": 1.43,
          "minutos": 7.9,
          "cubre": true,
          "dentro_promesa": true
        }
      ],
      "mas_cercano": {
        "microhub": {
          "id": 2,
          "nombre": "Microhub Valles"
        },
        "distancia_km": 0.37,
        "distancia_calle_km": 0.49,
        "minutos": 5.3,
        "cubre": true,
        "dentro_promesa": true
      },
      "minutos_mejor": 5.3
    },
    {
      "zona": {
        "id": 4,
        "nombre": "San Bernabé X (F-113)"
      },
      "hogares": 1197,
      "estado": "cubierta",
      "solapada": true,
      "cubierta_por": [
        {
          "microhub": {
            "id": 3,
            "nombre": "Microhub Poniente F-113"
          },
          "distancia_km": 0.11,
          "distancia_calle_km": 0.15,
          "minutos": 4.4,
          "cubre": true,
          "dentro_promesa": true
        },
        {
          "microhub": {
            "id": 2,
            "nombre": "Microhub Valles"
          },
          "distancia_km": 1.04,
          "distancia_calle_km": 1.36,
          "minutos": 7.7,
          "cubre": true,
          "dentro_promesa": true
        }
      ],
      "mas_cercano": {
        "microhub": {
          "id": 3,
          "nombre": "Microhub Poniente F-113"
        },
        "distancia_km": 0.11,
        "distancia_calle_km": 0.15,
        "minutos": 4.4,
        "cubre": true,
        "dentro_promesa": true
      },
      "minutos_mejor": 4.4
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 4,
    "paginas": 1
  }
}
```

**Explicación.** La regla de cobertura es el radio en línea recta (igual que fn_cubre en PostgreSQL); la distancia por calle (× 1.3) solo estima el tiempo.

**Evidencia en —.** `evidencia`

```json
"No se pudo consultar: column z.latitud does not exist\nLINE 1: ...ona, round(fn_distancia_km(m.latitud, m.longitud, z.latitud,...\n                                                             ^\nHINT:  Perhaps you meant to reference the column \"m.latitud\"."
```

### COB-02 · Resumen de la red · PASA

**Objetivo.** Porcentaje de zonas y hogares cubiertos, tiempo promedio y zonas traslapadas.

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/resumen`

```http
Accept: application/json
X-Traza-Id: a99c73f3-8319-4b7b-86a3-47b0eb62a6fe
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 48 ms · traza `a99c73f3-8319-4b7b-86a3-47b0eb62a6fe`

```json
{
  "zonas": 4,
  "zonas_cubiertas": 4,
  "pct_zonas": 100.0,
  "hogares": 6709,
  "hogares_cubiertos": 6709,
  "pct_hogares": 100.0,
  "tiempo_promedio_min": 5.5,
  "dentro_promesa_pct": 100.0,
  "zonas_solapadas": 3,
  "zonas_sin_cobertura": [],
  "microhubs_activos": 3,
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 1.3,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 40.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.6,
      "modificado": false
    }
  ]
}
```

### COB-03 · Resumen (XML) · PASA

**Objetivo.** Respuesta XML que cumple cobertura.xsd.

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/resumen`

```http
Accept: application/xml
X-Traza-Id: 9983c62f-afd2-4402-9fc0-0e4bca543880
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 45 ms · traza `9983c62f-afd2-4402-9fc0-0e4bca543880`

```xml
<?xml version='1.0' encoding='utf-8'?>
<cobertura_resumen xmlns="urn:microhubs:v1" version="1"><zonas>4</zonas><zonas_cubiertas>4</zonas_cubiertas><pct_zonas>100</pct_zonas><hogares>6709</hogares><hogares_cubiertos>6709</hogares_cubiertos><pct_hogares>100</pct_hogares><tiempo_promedio_min>5.5</tiempo_promedio_min><dentro_promesa_pct>100</dentro_promesa_pct><zonas_solapadas>3</zonas_solapadas><zonas_sin_cobertura /><microhubs_activos>3</microhubs_activos><supuestos_usados><supuesto><clave>factor_rodeo_distancia</clave><valor>1.3</valor><modificado>false</modificado></supuesto><supuesto><clave>velocidad_reparto_kmh</clave><valor>22</valor><modificado>false</modificado></supuesto><supuesto><clave>tiempo_servicio_min</clave><valor>4</valor><modificado>false</modificado></supuesto><supuesto><clave>cob_tiempo_max_min</clave><valor>30</valor><modificado>false</modificado></supuesto><supuesto><clave>cob_solape_max_pct</clave><valor>40</valor><modificado>false</modificado></supuesto><supuesto><clave>tamano_hogar</clave><valor>3.6</valor><modificado>false</modificado></supuesto></supuestos_usados></cobertura_resumen>
```

### COB-04 · Un punto junto a un microhub · PASA

**Objetivo.** Qué microhubs lo cubren y a qué distancia.

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/punto?latitud=25.748&longitud=-100.364`

```http
Accept: application/json
X-Traza-Id: 8ffb9b47-4786-4595-b84a-6453b1c53bf7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 48 ms · traza `8ffb9b47-4786-4595-b84a-6453b1c53bf7`

```json
{
  "latitud": 25.748,
  "longitud": -100.364,
  "cubierto": true,
  "zona_mas_cercana": {
    "id": 1,
    "nombre": "San Bernabé Centro",
    "distancia_km": 0.62
  },
  "opciones": [
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "distancia_km": 0.0,
      "distancia_calle_km": 0.0,
      "minutos": 4.0,
      "cubre": true,
      "dentro_promesa": true
    },
    {
      "microhub": {
        "id": 2,
        "nombre": "Microhub Valles"
      },
      "distancia_km": 1.16,
      "distancia_calle_km": 1.5,
      "minutos": 8.1,
      "cubre": true,
      "dentro_promesa": true
    },
    {
      "microhub": {
        "id": 3,
        "nombre": "Microhub Poniente F-113"
      },
      "distancia_km": 1.72,
      "distancia_calle_km": 2.23,
      "minutos": 10.1,
      "cubre": false,
      "dentro_promesa": true
    }
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 1.3,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 40.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.6,
      "modificado": false
    }
  ]
}
```

### COB-05 · Un punto fuera de la red · PASA

**Objetivo.** Nadie lo cubre; se dice cuál es la zona más cercana.

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/punto?latitud=26.9&longitud=-101.4`

```http
Accept: application/json
X-Traza-Id: 23ad8697-0024-4c86-9eab-0a4c520f4ca1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 47 ms · traza `23ad8697-0024-4c86-9eab-0a4c520f4ca1`

```json
{
  "latitud": 26.9,
  "longitud": -101.4,
  "cubierto": false,
  "zona_mas_cercana": {
    "id": 3,
    "nombre": "Paseo de San Bernabé",
    "distancia_km": 163.0
  },
  "opciones": [
    {
      "microhub": {
        "id": 3,
        "nombre": "Microhub Poniente F-113"
      },
      "distancia_km": 163.29,
      "distancia_calle_km": 212.28,
      "minutos": 583.0,
      "cubre": false,
      "dentro_promesa": false
    },
    {
      "microhub": {
        "id": 2,
        "nombre": "Microhub Valles"
      },
      "distancia_km": 163.38,
      "distancia_calle_km": 212.39,
      "minutos": 583.2,
      "cubre": false,
      "dentro_promesa": false
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "distancia_km": 164.53,
      "distancia_calle_km": 213.88,
      "minutos": 587.3,
      "cubre": false,
      "dentro_promesa": false
    }
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 1.3,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 40.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.6,
      "modificado": false
    }
  ]
}
```

### COB-06 · Coordenadas inválidas · PASA

**Objetivo.** La latitud debe estar entre 20 y 33.

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/punto?latitud=95&longitud=10`

```http
Accept: application/json
X-Traza-Id: 70e79c29-007c-4f53-9ebc-81412f1c92cf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 5 ms · traza `70e79c29-007c-4f53-9ebc-81412f1c92cf`

```json
{
  "error": {
    "codigo": "FILTRO_INVALIDO",
    "mensaje": "latitud debe estar entre 20 y 33.",
    "detalles": [
      {
        "campo": "latitud",
        "mensaje": "latitud debe estar entre 20 y 33."
      }
    ],
    "traza_id": "70e79c29-007c-4f53-9ebc-81412f1c92cf"
  }
}
```

### COB-07 · Ubicaciones candidatas con ranking · PASA

**Objetivo.** Cada candidata de planeación frente a la red actual.

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/candidatos`

```http
Accept: application/json
X-Traza-Id: 4d5b4176-7442-4dff-b7cd-ed6585ed16fe
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 121 ms · traza `4d5b4176-7442-4dff-b7cd-ed6585ed16fe`

```json
{
  "datos": [
    {
      "candidato": {
        "id": 3,
        "clave": "********",
        "nombre": "Alianza Real"
      },
      "latitud": 25.7625,
      "longitud": -100.353,
      "radio_km": 1.6,
      "zonas_nuevas": 0,
      "hogares_nuevos": 0,
      "hogares_con_mejor_tiempo": 0,
      "minutos_ahorrados": 0.0,
      "solapamiento_pct": 0.0,
      "canibaliza": false,
      "minutos_promedio": 4.0,
      "costo_ultima_milla": 18.0,
      "ranking": 1
    },
    {
      "candidato": {
        "id": 25,
        "clave": "********",
        "nombre": "Alianza Norte (editado)"
      },
      "latitud": 25.7601,
      "longitud": -100.3555,
      "radio_km": 1.5,
      "zonas_nuevas": 0,
      "hogares_nuevos": 0,
      "hogares_con_mejor_tiempo": 0,
      "minutos_ahorrados": 0.0,
      "solapamiento_pct": 0.0,
      "canibaliza": false,
      "minutos_promedio": 4.0,
      "costo_ultima_milla": 18.0,
      "ranking": 2
    },
    {
      "candidato": {
        "id": 79,
        "clave": "********",
        "nombre": "Alianza Norte (editado)"
      },
      "latitud": 25.7601,
      "longitud": -100.3555,
      "radio_km": 1.5,
      "zonas_nuevas": 0,
      "hogares_nuevos": 0,
      "hogares_con_mejor_tiempo": 0,
      "minutos_ahorrados": 0.0,
      "solapamiento_pct": 0.0,
      "canibaliza": false,
      "minutos_promedio": 4.0,
      "costo_ultima_milla": 18.0,
      "ranking": 3
    },
    {
      "candidato": {
        "id": 116,
        "clave": "********",
        "nombre": "Alianza Norte (editado)"
      },
      "latitud": 25.7601,
      "longitud": -100.3555,
      "radio_km": 1.5,
      "zonas_nuevas": 0,
      "hogares_nuevos": 0,
      "hogares_con_mejor_tiempo": 0,
      "minutos_ahorrados": 0.0,
      "solapamiento_pct": 0.0,
      "canibaliza": false,
      "minutos_promedio": 4.0,
      "costo_ultima_milla": 18.0,
      "ranking": 4
    },
    {
      "candidato": {
        "id": 114,
        "clave": "********",
        "nombre": "Alianza Norte (editado)"
      },
      "latitud": 25.7601,
      "longitud": -100.3555,
      "radio_km": 1.5,
      "zonas_nuevas": 0,
      "hogares_nuevos": 0,
      "hogares_con_mejor_tiempo": 0,
      "minutos_ahorrados": 0.0,
      "solapamiento_pct": 0.0,
      "canibaliza": false,
      "minutos_promedio": 4.0,
      "costo_ultima_milla": 18.0,
      "ranking": 5
    },
    {
      "candidato": {
        "id": 112,
        "clave": "********",
        "nombre": "Alianza Norte (editado)"
      },
      "latitud": 25.7601,
      "longitud": -100.3555,
      "radio_km": 1.5,
      "zonas_nuevas": 0,
      "hogares_nuevos": 0,
      "hogares_con_mejor_tiempo": 0,
      "minutos_ahorrados": 0.0,
      "solapamiento_pct": 0.0,
      "canibaliza": false,
      "minutos_promedio": 4.0,
      "costo_ultima_milla": 18.0,
      "ranking": 6
    },
    {
      "candidato": {
        "id": 91,
        "clave": "********",
        "nombre": "Alianza Norte (editado)"
      },
      "latitud": 25.7601,
      "longitud": -100.3555,
      "radio_km": 1.5,
      "zonas_nuevas": 0,
      "hogares_nuevos": 0,
      "hogares_con_mejor_tiempo": 0,
      "minutos_ahorrados": 0.0,
      "solapamiento_pct": 0.0,
      "canibaliza": false,
      "minutos_promedio": 4.0,
      "costo_ultima_milla": 18.0,
      "ranking": 7
    },
    {
      "candidato": {
        "id": 93,
        "clave": "********",
        "nombre": "Alianza Norte (editado)"
      },
      "latitud": 25.7601,
      "longitud": -100.3555,
      "radio_km": 1.5,
      "zonas_nuevas": 0,
      "hogares_nuevos": 0,
      "hogares_con_mejor_tiempo": 0,
      "minutos_ahorrados": 0.0,
      "solapamiento_pct": 0.0,
      "canibaliza": false,
      "minutos_promedio": 4.0,
      "costo_ultima_milla": 18.0,
      "ranking": 8
    },
    {
      "candidato": {
        "id": 52,
        "clave": "********",
        "nombre": "Alianza Norte (editado)"
      },
      "latitud": 25.7601,
      "longitud": -100.3555,
      "radio_km": 1.5,
      "zonas_nuevas": 0,
      "hogares_nuevos": 0,
      "hogares_con_mejor_tiempo": 0,
      "minutos_ahorrados": 0.0,
      "solapamiento_pct": 0.0,
      "canibaliza": false,
      "minutos_promedio": 4.0,
      "costo_ultima_milla": 18.0,
      "ranking": 9
    },
    {
      "candidato": {
        "id": 118,
        "clave": "********",
        "nombre": "Alianza Norte (editado)"
      },
      "latitud": 25.7601,
      "longitud": -100.3555,
      "radio_km": 1.5,
      "zonas_nuevas": 0,
      "hogares_nuevos": 0,
      "hogares_con_mejor_tiempo": 0,
      "minutos_ahorrados": 0.0,
      "solapamiento_pct": 0.0,
      "canibaliza": false,
      "minutos_promedio": 4.0,
      "costo_ultima_milla": 18.0,
      "ranking": 10
    },
    {
      "candidato": {
        "id": 110,
        "clave": "********",
        "nombre": "Alianza Norte (editado)"
      },
      "latitud": 25.7601,
      "longitud": -100.3555,
      "radio_km": 1.5,
      "zonas_nuevas": 0,
      "hogares_nuevos": 0,
      "hogares_con_mejor_tiempo": 0,
      "minutos_ahorrados": 0.0,
      "solapamiento_pct": 0.0,
      "canibaliza": false,
      "minutos_promedio": 4.0,
      "costo_ultima_milla": 18.0,
      "ranking": 11
    },
    {
      "candidato": {
        "id": 18,
        "clave": "********",
        "nombre": "Alianza Norte (editado)"
      },
      "latitud": 25.7601,
      "longitud": -100.3555,
      "radio_km": 1.5,
      "zonas_nuevas": 0,
      "hogares_nuevos": 0,
      "hogares_con_mejor_tiempo": 0,
      "minutos_ahorrados": 0.0,
      "solapamiento_pct": 0.0,
      "canibaliza": false,
      "minutos_promedio": 4.0,
      "costo_ultima_milla": 18.0,
      "ranking": 12
    },
    {
      "candidato": {
        "id": 1,
        "clave": "********",
        "nombre": "San Bernabé Norte"
      },
      "latitud": 25.752,
      "longitud": -100.361,
      "radio_km": 1.5,
      "zonas_nuevas": 0,
      "hogares_nuevos": 0,
      "hogares_con_mejor_tiempo": 0,
      "minutos_ahorrados": 0.0,
      "solapamiento_pct": 100.0,
      "canibaliza": true,
      "minutos_promedio": 6.8,
      "costo_ultima_milla": 21.06,
      "ranking": 13
    },
    {
      "candidato": {
        "id": 2,
        "clave": "********",
        "nombre": "Valles Poniente"
      },
      "latitud": 25.7555,
      "longitud": -100.376,
      "radio_km": 1.5,
      "zonas_nuevas": 0,
      "hogares_nuevos": 0,
      "hogares_con_mejor_tiempo": 0,
      "minutos_ahorrados": 0.0,
      "solapamiento_pct": 100.0,
      "canibaliza": true,
      "minutos_promedio": 6.2,
      "costo_ultima_milla": 20.4,
      "ranking": 14
    },
    {
      "candidato": {
        "id": 4,
        "clave": "********",
        "nombre": "Paseo Sur"
      },
      "latitud": 25.759,
      "longitud": -100.372,
      "radio_km": 1.4,
      "zonas_nuevas": 0,
      "hogares_nuevos": 0,
      "hogares_con_mejor_tiempo": 0,
      "minutos_ahorrados": 0.0,
      "solapamiento_pct": 100.0,
      "canibaliza": true,
      "minutos_promedio": 6.6,
      "costo_ultima_milla": 20.89,
      "ranking": 15
    },
    {
      "candidato": {
        "id": 5,
        "clave": "********",
        "nombre": "F-113 Oriente"
      },
      "latitud": 25.747,
      "longitud": -100.3765,
      "radio_km": 1.3,
      "zonas_nuevas": 0,
      "hogares_nuevos": 0,
      "hogares_con_mejor_tiempo": 0,
      "minutos_ahorrados": 0.0,
      "solapamiento_pct": 100.0,
      "canibaliza": true,
      "minutos_promedio": 7.3,
      "costo_ultima_milla": 21.63,
      "ranking": 16
    }
  ],
  "red_actual": {
    "pct_zonas": 100.0,
    "pct_hogares": 100.0
  },
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 1.3,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 40.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.6,
      "modificado": false
    }
  ]
}
```

**Explicación.** Primero la que suma más hogares nuevos y, a igualdad, la que acerca el servicio a más hogares ya cubiertos. Las candidatas salen del servicio de planeación (cobertura no lee su tabla).

### COB-08 · Evaluar una candidata · PASA

**Objetivo.** Zonas nuevas, hogares nuevos, traslape y costo de la última milla.

**Petición.** `POST http://cobertura:5116/api/v1/cobertura/evaluaciones`

```http
Accept: application/json
X-Traza-Id: 66377fdc-1848-484d-b762-b06b99dd4dd7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "candidato_id": 3
}
```

**Respuesta.** HTTP 200 (esperado 200) · 88 ms · traza `66377fdc-1848-484d-b762-b06b99dd4dd7`

```json
{
  "id": null,
  "nombre": "Evaluación de CAND-05",
  "candidato": {
    "id": 3,
    "clave": "********",
    "nombre": "Alianza Real"
  },
  "latitud": 25.7625,
  "longitud": -100.353,
  "radio_km": 1.6,
  "zonas": [],
  "zonas_nuevas": 0,
  "hogares_en_radio": 0,
  "hogares_nuevos": 0,
  "hogares_con_mejor_tiempo": 0,
  "minutos_ahorrados": 0.0,
  "solapamiento_pct": 0.0,
  "canibaliza": false,
  "distancia_promedio_km": 0.0,
  "minutos_promedio": 4.0,
  "costo_ultima_milla": 18.0,
  "antes": {
    "pct_zonas": 100.0,
    "pct_hogares": 100.0
  },
  "despues": {
    "pct_zonas": 100.0,
    "pct_hogares": 100.0
  },
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 1.3,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 40.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.6,
      "modificado": false
    }
  ]
}
```

### COB-09 · Guardar la evaluación sin permiso · PASA

**Objetivo.** Guardar exige planeacion.editar.

**Petición.** `POST http://cobertura:5116/api/v1/cobertura/evaluaciones`

```http
Accept: application/json
X-Traza-Id: 06856afd-0782-4dca-8809-b6d137456edc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{
  "candidato_id": 3,
  "guardar": true
}
```

**Respuesta.** HTTP 403 (esperado 403) · 146 ms · traza `06856afd-0782-4dca-8809-b6d137456edc`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Guardar una evaluación exige el permiso planeacion.editar.",
    "traza_id": "06856afd-0782-4dca-8809-b6d137456edc"
  }
}
```

### COB-10 · Guardar la evaluación · PASA

**Objetivo.** Queda en cobertura_evaluacion con su resultado completo.

**Petición.** `POST http://cobertura:5116/api/v1/cobertura/evaluaciones`

```http
Accept: application/json
X-Traza-Id: 02be5dd5-e129-4caa-b565-2bad744493ef
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "candidato_id": 3,
  "guardar": true,
  "nombre": "Evidencia Ola 2"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 148 ms · traza `02be5dd5-e129-4caa-b565-2bad744493ef`

```json
{
  "id": 22,
  "nombre": "Evidencia Ola 2",
  "candidato": {
    "id": 3,
    "clave": "********",
    "nombre": "Alianza Real"
  },
  "latitud": 25.7625,
  "longitud": -100.353,
  "radio_km": 1.6,
  "zonas": [],
  "zonas_nuevas": 0,
  "hogares_en_radio": 0,
  "hogares_nuevos": 0,
  "hogares_con_mejor_tiempo": 0,
  "minutos_ahorrados": 0.0,
  "solapamiento_pct": 0.0,
  "canibaliza": false,
  "distancia_promedio_km": 0.0,
  "minutos_promedio": 4.0,
  "costo_ultima_milla": 18.0,
  "antes": {
    "pct_zonas": 100.0,
    "pct_hogares": 100.0
  },
  "despues": {
    "pct_zonas": 100.0,
    "pct_hogares": 100.0
  },
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 1.3,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 40.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.6,
      "modificado": false
    }
  ]
}
```

**Evidencia en PostgreSQL.** `SELECT id, nombre, parametros, creado_por FROM cobertura_evaluacion WHERE nombre = 'Evidencia Ola 2'`

```json
[
  {
    "id": 22,
    "nombre": "Evidencia Ola 2",
    "parametros": {
      "latitud": 25.7625,
      "longitud": -100.353,
      "radio_km": 1.6,
      "candidato_id": 3
    },
    "creado_por": 5
  }
]
```

### COB-17 · Evaluaciones guardadas · PASA

**Objetivo.** Lista de lo que el planeador ha evaluado.

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/evaluaciones?por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 6743c3d2-c094-428a-bb1a-a61c1f24f1f7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 59 ms · traza `6743c3d2-c094-428a-bb1a-a61c1f24f1f7`

```json
{
  "datos": [
    {
      "id": 22,
      "nombre": "Evidencia Ola 2",
      "zonas_nuevas": 0,
      "hogares_nuevos": 0,
      "solapamiento_pct": 0.0,
      "canibaliza": false,
      "creado_por": 5,
      "creado_en": "2026-11-26T14:19:53-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 1,
    "paginas": 1
  }
}
```

### COB-18 · Abrir una evaluación guardada · PASA

**Objetivo.** Con el resultado completo con que se guardó.

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/evaluaciones/22`

```http
Accept: application/json
X-Traza-Id: 960aebbe-2bf7-4a92-962d-f1ed49e80caa
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 33 ms · traza `960aebbe-2bf7-4a92-962d-f1ed49e80caa`

```json
{
  "id": 22,
  "nombre": "Evidencia Ola 2",
  "candidato": {
    "id": 3,
    "clave": "********",
    "nombre": "Alianza Real"
  },
  "latitud": 25.7625,
  "longitud": -100.353,
  "radio_km": 1.6,
  "zonas": [],
  "zonas_nuevas": 0,
  "hogares_en_radio": 0,
  "hogares_nuevos": 0,
  "hogares_con_mejor_tiempo": 0,
  "minutos_ahorrados": 0.0,
  "solapamiento_pct": 0.0,
  "canibaliza": false,
  "distancia_promedio_km": 0.0,
  "minutos_promedio": 4.0,
  "costo_ultima_milla": 18.0,
  "antes": {
    "pct_zonas": 100.0,
    "pct_hogares": 100.0
  },
  "despues": {
    "pct_zonas": 100.0,
    "pct_hogares": 100.0
  },
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 1.3,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 40.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.6,
      "modificado": false
    }
  ]
}
```

### COB-11 · Evaluar una coordenada sobre un microhub · PASA

**Objetivo.** Todo se traslapa: se avisa de canibalización.

**Petición.** `POST http://cobertura:5116/api/v1/cobertura/evaluaciones`

```http
Accept: application/json
X-Traza-Id: 6189adad-4c07-45f4-9393-6e258cb6089a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "latitud": 25.748,
  "longitud": -100.364,
  "radio_km": 2
}
```

**Respuesta.** HTTP 200 (esperado 200) · 56 ms · traza `6189adad-4c07-45f4-9393-6e258cb6089a`

```json
{
  "id": null,
  "nombre": "Evaluación de una coordenada",
  "candidato": null,
  "latitud": 25.748,
  "longitud": -100.364,
  "radio_km": 2.0,
  "zonas": [
    {
      "zona": {
        "id": 1,
        "nombre": "San Bernabé Centro"
      },
      "hogares": 2339,
      "distancia_km": 0.62,
      "distancia_calle_km": 0.8,
      "minutos": 6.2,
      "microhubs_que_ya_cubren": 1
    },
    {
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "hogares": 1717,
      "distancia_km": 0.75,
      "distancia_calle_km": 0.97,
      "minutos": 6.7,
      "microhubs_que_ya_cubren": 2
    },
    {
      "zona": {
        "id": 3,
        "nombre": "Paseo de San Bernabé"
      },
      "hogares": 1456,
      "distancia_km": 1.53,
      "distancia_calle_km": 1.99,
      "minutos": 9.4,
      "microhubs_que_ya_cubren": 2
    },
    {
      "zona": {
        "id": 4,
        "nombre": "San Bernabé X (F-113)"
      },
      "hogares": 1197,
      "distancia_km": 1.61,
      "distancia_calle_km": 2.09,
      "minutos": 9.7,
      "microhubs_que_ya_cubren": 2
    }
  ],
  "zonas_nuevas": 0,
  "hogares_en_radio": 6709,
  "hogares_nuevos": 0,
  "hogares_con_mejor_tiempo": 0,
  "minutos_ahorrados": 0.0,
  "solapamiento_pct": 100.0,
  "canibaliza": true,
  "distancia_promedio_km": 1.33,
  "minutos_promedio": 7.6,
  "costo_ultima_milla": 22.0,
  "antes": {
    "pct_zonas": 100.0,
    "pct_hogares": 100.0
  },
  "despues": {
    "pct_zonas": 100.0,
    "pct_hogares": 100.0
  },
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 1.3,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 40.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.6,
      "modificado": false
    }
  ]
}
```

### COB-12 · Evaluar sin coordenadas · PASA

**Objetivo.** Hace falta un candidato o una coordenada.

**Petición.** `POST http://cobertura:5116/api/v1/cobertura/evaluaciones`

```http
Accept: application/json
X-Traza-Id: 2538a4b3-c3ec-4865-9b51-bec87b5a7cdc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "radio_km": 2
}
```

**Respuesta.** HTTP 422 (esperado 422) · 8 ms · traza `2538a4b3-c3ec-4865-9b51-bec87b5a7cdc`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "latitud",
        "mensaje": "Indica latitud y longitud, o un candidato_id."
      }
    ],
    "traza_id": "2538a4b3-c3ec-4865-9b51-bec87b5a7cdc"
  }
}
```

### COB-13 · Escenarios de radio y de rodeo · PASA

**Objetivo.** Cuánto cubre la red con otros radios y otro factor de calle.

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/escenarios?radios=0.5,1,1.5,2&rodeos=1.2,1.5`

```http
Accept: application/json
X-Traza-Id: 9e76bf07-67bb-45ed-95e4-dd292ce579c1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 61 ms · traza `9e76bf07-67bb-45ed-95e4-dd292ce579c1`

```json
{
  "filas": [
    {
      "radio_km": 0.5,
      "rodeo": 1.2,
      "zonas_cubiertas": 3,
      "pct_zonas": 75.0,
      "pct_hogares": 65.1,
      "tiempo_promedio_min": 5.0,
      "dentro_promesa_pct": 100.0
    },
    {
      "radio_km": 1.0,
      "rodeo": 1.2,
      "zonas_cubiertas": 4,
      "pct_zonas": 100.0,
      "pct_hogares": 100.0,
      "tiempo_promedio_min": 5.4,
      "dentro_promesa_pct": 100.0
    },
    {
      "radio_km": 1.5,
      "rodeo": 1.2,
      "zonas_cubiertas": 4,
      "pct_zonas": 100.0,
      "pct_hogares": 100.0,
      "tiempo_promedio_min": 5.4,
      "dentro_promesa_pct": 100.0
    },
    {
      "radio_km": 2.0,
      "rodeo": 1.2,
      "zonas_cubiertas": 4,
      "pct_zonas": 100.0,
      "pct_hogares": 100.0,
      "tiempo_promedio_min": 5.4,
      "dentro_promesa_pct": 100.0
    },
    {
      "radio_km": 0.5,
      "rodeo": 1.5,
      "zonas_cubiertas": 3,
      "pct_zonas": 75.0,
      "pct_hogares": 65.1,
      "tiempo_promedio_min": 5.3,
      "dentro_promesa_pct": 100.0
    },
    {
      "radio_km": 1.0,
      "rodeo": 1.5,
      "zonas_cubiertas": 4,
      "pct_zonas": 100.0,
      "pct_hogares": 100.0,
      "tiempo_promedio_min": 5.7,
      "dentro_promesa_pct": 100.0
    },
    {
      "radio_km": 1.5,
      "rodeo": 1.5,
      "zonas_cubiertas": 4,
      "pct_zonas": 100.0,
      "pct_hogares": 100.0,
      "tiempo_promedio_min": 5.7,
      "dentro_promesa_pct": 100.0
    },
    {
      "radio_km": 2.0,
      "rodeo": 1.5,
      "zonas_cubiertas": 4,
      "pct_zonas": 100.0,
      "pct_hogares": 100.0,
      "tiempo_promedio_min": 5.7,
      "dentro_promesa_pct": 100.0
    }
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 1.3,
      "modificado": true
    },
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 40.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.6,
      "modificado": false
    }
  ]
}
```

**Explicación.** El rodeo (1.3 por omisión) es un supuesto: la distancia real por calle es mayor que la recta.

### COB-14 · Corregir la población con su fuente · PASA

**Objetivo.** La población de cada zona se corrige con el dato de INEGI; hay que decir de dónde sale.

**Petición.** `PUT http://cobertura:5116/api/v1/cobertura/zonas/1/poblacion`

```http
Accept: application/json
X-Traza-Id: fe916f3e-f77d-4258-9b88-b3c320a01361
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "poblacion": 8520,
  "fuente": "INEGI, Censo 2020, AGEB de prueba"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 63 ms · traza `fe916f3e-f77d-4258-9b88-b3c320a01361`

```json
{
  "zona": {
    "id": 1,
    "nombre": "San Bernabé Centro"
  },
  "poblacion": 8520,
  "hogares": 2367,
  "fuente": "INEGI, Censo 2020, AGEB de prueba"
}
```

**Evidencia en PostgreSQL.** `SELECT zona_id, poblacion, fuente FROM cobertura_zona_dato WHERE zona_id = %s`

```json
[
  {
    "zona_id": 1,
    "poblacion": 8520,
    "fuente": "INEGI, Censo 2020, AGEB de prueba"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT accion, entidad, valores_anteriores, valores_nuevos FROM auditoria WHERE entidad = 'cobertura_zona_dato' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "accion": "modificacion",
    "entidad": "cobertura_zona_dato",
    "valores_anteriores": {
      "fuente": "Estimación del equipo (06_planeacion.sql); sustituir por el dato de INEGI de cada colonia",
      "poblacion": 8420,
      "actualizado_en": "2026-11-26T14:05:06.258042-06:00"
    },
    "valores_nuevos": {
      "fuente": "INEGI, Censo 2020, AGEB de prueba",
      "poblacion": 8520,
      "actualizado_en": "2026-11-26T14:19:53.511685-06:00"
    }
  }
]
```

### COB-15 · Corregir la población sin permiso · PASA

**Objetivo.** Es del planeador.

**Petición.** `PUT http://cobertura:5116/api/v1/cobertura/zonas/1/poblacion`

```http
Accept: application/json
X-Traza-Id: 09192e99-e54f-40e6-ac7b-4bf468711955
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "poblacion": 1,
  "fuente": "Sin permiso"
}
```

**Respuesta.** HTTP 403 (esperado 403) · 28 ms · traza `09192e99-e54f-40e6-ac7b-4bf468711955`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "09192e99-e54f-40e6-ac7b-4bf468711955"
  }
}
```

### COB-16 · Supuestos de la cobertura · PASA

**Objetivo.** Rodeo, velocidad, tiempo de servicio, promesa de entrega y tamaño del hogar.

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/supuestos`

```http
Accept: application/json
X-Traza-Id: c1eb62c9-d84c-4ce5-ab39-87a9d1241d86
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 31 ms · traza `c1eb62c9-d84c-4ce5-ab39-87a9d1241d86`

```json
{
  "datos": [
    {
      "clave": "********",
      "valor": "40",
      "unidad": "%",
      "origen": "supuesto",
      "justificacion": "Si más del 40 % de las zonas de un microhub ya las cubre otro, los dos se reparten la misma demanda y se canibalizan.",
      "como_calibrar": "Comparar la demanda de las zonas compartidas antes y después de abrir el segundo microhub."
    },
    {
      "clave": "********",
      "valor": "30",
      "unidad": "minutos",
      "origen": "normativo",
      "justificacion": "Promesa de entrega que fija el equipo: llegar en 30 minutos o menos desde que sale el repartidor.",
      "como_calibrar": "Se revisa con el tiempo real de las entregas cerradas."
    },
    {
      "clave": "********",
      "valor": "18",
      "unidad": "MXN",
      "origen": "supuesto",
      "justificacion": "Pago fijo por entrega al repartidor; se suma al costo por di…(186 caracteres)",
      "como_calibrar": "Lo que se paga de verdad por entrega en el contrato o en la nómina de repartidores; al corregirlo, corregir también el concepto en costos."
    },
    {
      "clave": "********",
      "valor": "4.5",
      "unidad": "MXN/km",
      "origen": "supuesto",
      "justificacion": "Combustible, mantenimiento y desgaste por kilómetro de una m…(204 caracteres)",
      "como_calibrar": "Gasto real de combustible y mantenimiento entre los kilómetr…(147 caracteres)"
    },
    {
      "clave": "********",
      "valor": "1.3",
      "unidad": "veces",
      "origen": "supuesto",
      "justificacion": "La distancia por calle es mayor que la línea recta; en una r…(220 caracteres)",
      "como_calibrar": "Cociente entre la distancia del recorrido GPS y la distancia en línea recta entre el microhub y el domicilio, en entregas cerradas."
    },
    {
      "clave": "********",
      "valor": "3",
      "unidad": "paradas",
      "origen": "supuesto",
      "justificacion": "Paradas promedio de una salida cuando los pedidos se agrupan por zona. Reparte el costo del regreso al microhub entre ellas.",
      "como_calibrar": "Promedio de la columna paradas de plan_ruta."
    },
    {
      "clave": "********",
      "valor": "3.6",
      "unidad": "personas",
      "origen": "supuesto",
      "justificacion": "Personas por hogar para convertir población en hogares. Se u…(145 caracteres)",
      "como_calibrar": "Tomar el dato del Censo de Población y Vivienda (INEGI) de la AGEB de cada colonia."
    },
    {
      "clave": "********",
      "valor": "4",
      "unidad": "minutos",
      "origen": "supuesto",
      "justificacion": "Minutos que el repartidor pasa en cada parada: estacionar, entregar, cobrar y confirmar con el cliente.",
      "como_calibrar": "Diferencia entre la llegada al domicilio y el cierre de la entrega en el recorrido GPS."
    },
    {
      "clave": "********",
      "valor": "22",
      "unidad": "km/h",
      "origen": "supuesto",
      "justificacion": "Velocidad media de un repartidor en moto o bicicleta dentro …(180 caracteres)",
      "como_calibrar": "Dividir la distancia del recorrido GPS entre su duración en …(147 caracteres)"
    }
  ]
}
```

## Servicio capacidad · puerto 5117

### CAP-01 · Personal de cada microhub · PASA

**Objetivo.** Operadores, repartidores y tope de espacio.

**Petición.** `GET http://capacidad:5117/api/v1/capacidad/recursos`

```http
Accept: application/json
X-Traza-Id: e556bd28-2e28-4b56-956d-739649c6226f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 41 ms · traza `e556bd28-2e28-4b56-956d-739649c6226f`

```json
{
  "datos": [
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "operadores": 3,
      "repartidores": 3,
      "capacidad_fisica": 150,
      "actualizado_en": "2026-11-26T14:05:06-06:00"
    },
    {
      "microhub": {
        "id": 2,
        "nombre": "Microhub Valles"
      },
      "operadores": 3,
      "repartidores": 2,
      "capacidad_fisica": 120,
      "actualizado_en": "2026-10-19T23:44:58-06:00"
    },
    {
      "microhub": {
        "id": 3,
        "nombre": "Microhub Poniente F-113"
      },
      "operadores": 2,
      "repartidores": 2,
      "capacidad_fisica": 100,
      "actualizado_en": "2026-10-19T23:44:58-06:00"
    },
    {
      "microhub": {
        "id": 4,
        "nombre": "Microhub Piloto Alianza"
      },
      "operadores": 2,
      "repartidores": 2,
      "capacidad_fisica": 110,
      "actualizado_en": "2026-10-19T23:44:58-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 4,
    "paginas": 1
  }
}
```

**Evidencia en PostgreSQL.** `SELECT microhub_id, operadores, repartidores, capacidad_fisica FROM capacidad_recurso ORDER BY microhub_id`

```json
[
  {
    "microhub_id": 1,
    "operadores": 3,
    "repartidores": 3,
    "capacidad_fisica": 150
  },
  {
    "microhub_id": 2,
    "operadores": 3,
    "repartidores": 2,
    "capacidad_fisica": 120
  },
  {
    "microhub_id": 3,
    "operadores": 2,
    "repartidores": 2,
    "capacidad_fisica": 100
  },
  {
    "microhub_id": 4,
    "operadores": 2,
    "repartidores": 2,
    "capacidad_fisica": 110
  }
]
```

### CAP-02 · El operador pide otro microhub · PASA

**Objetivo.** Solo ve los recursos del suyo.

**Petición.** `GET http://capacidad:5117/api/v1/capacidad/recursos/2`

```http
Accept: application/json
X-Traza-Id: 3808ed2a-9af8-4310-af7e-2c9ae1fc5a0f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 5 ms · traza `3808ed2a-9af8-4310-af7e-2c9ae1fc5a0f`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "3808ed2a-9af8-4310-af7e-2c9ae1fc5a0f"
  }
}
```

### CAP-03 · Capacidad con una carga dada · PASA

**Objetivo.** Capacidad por etapa, utilización, cuello de botella y personal requerido.

**Petición.** `GET http://capacidad:5117/api/v1/capacidad/microhubs/1?carga_dia=60`

```http
Accept: application/json
X-Traza-Id: 62fecb14-8995-4131-9eab-432ac7d06bfc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 45 ms · traza `62fecb14-8995-4131-9eab-432ac7d06bfc`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "operadores": 3,
  "repartidores": 3,
  "capacidad_fisica": 150,
  "horas": 10.0,
  "distancia_km": 2.4,
  "carga_dia": 60.0,
  "capacidad_hora": 16.36,
  "capacidad_dia": 150,
  "utilizacion_pct": 40.0,
  "nivel": "estable",
  "utilizacion_pico_pct": 49.5,
  "nivel_pico": "estable",
  "cuello_botella": "espacio físico",
  "minutos_por_pedido_operacion": 11.0,
  "minutos_por_entrega": 8.4,
  "etapas": [
    {
      "etapa": "picking",
      "minutos_por_pedido": 6.0,
      "pct_tiempo": 54.5,
      "capacidad_hora": 30.0
    },
    {
      "etapa": "empaque",
      "minutos_por_pedido": 3.0,
      "pct_tiempo": 27.3,
      "capacidad_hora": 60.0
    },
    {
      "etapa": "despacho",
      "minutos_por_pedido": 2.0,
      "pct_tiempo": 18.2,
      "capacidad_hora": 90.0
    },
    {
      "etapa": "reparto",
      "minutos_por_pedido": 8.4,
      "pct_tiempo": null,
      "capacidad_hora": 21.5
    }
  ],
  "operadores_requeridos": 2,
  "repartidores_requeridos": 1,
  "holgura_pedidos_dia": 90.0,
  "formula": "3 operadores × 5.45 pedidos/h combinados; 3 repartidores × 7.17 entregas/h",
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 70.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 85.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 1.35,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 10.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 20.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.0,
      "modificado": false
    }
  ]
}
```

**Explicación.** Cada operador hace picking, empaque y despacho uno tras otro: su ritmo combinado es 1 ÷ (1/10 + 1/20 + 1/30). El reparto depende de repartidores, distancia y paradas por viaje. La capacidad es la menor de las dos, limitada por el espacio.

### CAP-13 · Capacidad de todos los microhubs · PASA

**Objetivo.** Una fila por microhub con su utilización y su nivel; el operador solo ve el suyo.

**Petición.** `GET http://capacidad:5117/api/v1/capacidad/microhubs?carga_dia=40&por_pagina=100`

```http
Accept: application/json
X-Traza-Id: 94a46ffd-ddec-4e8a-9c9c-dd20237e49b3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 66 ms · traza `94a46ffd-ddec-4e8a-9c9c-dd20237e49b3`

```json
{
  "datos": [
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "operadores": 3,
      "repartidores": 3,
      "capacidad_fisica": 150,
      "horas": 10.0,
      "distancia_km": 2.4,
      "carga_dia": 40.0,
      "capacidad_hora": 16.36,
      "capacidad_dia": 150,
      "utilizacion_pct": 26.7,
      "nivel": "estable",
      "utilizacion_pico_pct": 33.0,
      "nivel_pico": "estable",
      "cuello_botella": "espacio físico",
      "minutos_por_pedido_operacion": 11.0,
      "minutos_por_entrega": 8.4,
      "etapas": [
        {
          "etapa": "picking",
          "minutos_por_pedido": 6.0,
          "pct_tiempo": 54.5,
          "capacidad_hora": 30.0
        },
        {
          "etapa": "empaque",
          "minutos_por_pedido": 3.0,
          "pct_tiempo": 27.3,
          "capacidad_hora": 60.0
        },
        {
          "etapa": "despacho",
          "minutos_por_pedido": 2.0,
          "pct_tiempo": 18.2,
          "capacidad_hora": 90.0
        },
        {
          "etapa": "reparto",
          "minutos_por_pedido": 8.4,
          "pct_tiempo": null,
          "capacidad_hora": 21.5
        }
      ],
      "operadores_requeridos": 1,
      "repartidores_requeridos": 1,
      "holgura_pedidos_dia": 110.0,
      "formula": "3 operadores × 5.45 pedidos/h combinados; 3 repartidores × 7.17 entregas/h",
      "supuestos_usados": [
        {
          "clave": "********",
          "valor": 70.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 85.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 1.35,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 10.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 20.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 30.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 22.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 4.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 3.0,
          "modificado": false
        }
      ]
    },
    {
      "microhub": {
        "id": 2,
        "nombre": "Microhub Valles"
      },
      "operadores": 3,
      "repartidores": 2,
      "capacidad_fisica": 120,
      "horas": 10.0,
      "distancia_km": 2.4,
      "carga_dia": 40.0,
      "capacidad_hora": 14.35,
      "capacidad_dia": 120,
      "utilizacion_pct": 33.3,
      "nivel": "estable",
      "utilizacion_pico_pct": 37.6,
      "nivel_pico": "estable",
      "cuello_botella": "espacio físico",
      "minutos_por_pedido_operacion": 11.0,
      "minutos_por_entrega": 8.4,
      "etapas": [
        {
          "etapa": "picking",
          "minutos_por_pedido": 6.0,
          "pct_tiempo": 54.5,
          "capacidad_hora": 30.0
        },
        {
          "etapa": "empaque",
          "minutos_por_pedido": 3.0,
          "pct_tiempo": 27.3,
          "capacidad_hora": 60.0
        },
        {
          "etapa": "despacho",
          "minutos_por_pedido": 2.0,
          "pct_tiempo": 18.2,
          "capacidad_hora": 90.0
        },
        {
          "etapa": "reparto",
          "minutos_por_pedido": 8.4,
          "pct_tiempo": null,
          "capacidad_hora": 14.3
        }
      ],
      "operadores_requeridos": 1,
      "repartidores_requeridos": 1,
      "holgura_pedidos_dia": 80.0,
      "formula": "3 operadores × 5.45 pedidos/h combinados; 2 repartidores × 7.17 entregas/h",
      "supuestos_usados": [
        {
          "clave": "********",
          "valor": 70.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 85.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 1.35,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 10.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 20.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 30.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 22.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 4.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 3.0,
          "modificado": false
        }
      ]
    },
    {
      "microhub": {
        "id": 3,
        "nombre": "Microhub Poniente F-113"
      },
      "operadores": 2,
      "repartidores": 2,
      "capacidad_fisica": 100,
      "horas": 10.0,
      "distancia_km": 2.4,
      "carga_dia": 40.0,
      "capacidad_hora": 10.91,
      "capacidad_dia": 100,
      "utilizacion_pct": 40.0,
      "nivel": "estable",
      "utilizacion_pico_pct": 49.5,
      "nivel_pico": "estable",
      "cuello_botella": "espacio físico",
      "minutos_por_pedido_operacion": 11.0,
      "minutos_por_entrega": 8.4,
      "etapas": [
        {
          "etapa": "picking",
          "minutos_por_pedido": 6.0,
          "pct_tiempo": 54.5,
          "capacidad_hora": 20.0
        },
        {
          "etapa": "empaque",
          "minutos_por_pedido": 3.0,
          "pct_tiempo": 27.3,
          "capacidad_hora": 40.0
        },
        {
          "etapa": "despacho",
          "minutos_por_pedido": 2.0,
          "pct_tiempo": 18.2,
          "capacidad_hora": 60.0
        },
        {
          "etapa": "reparto",
          "minutos_por_pedido": 8.4,
          "pct_tiempo": null,
          "capacidad_hora": 14.3
        }
      ],
      "operadores_requeridos": 1,
      "repartidores_requeridos": 1,
      "holgura_pedidos_dia": 60.0,
      "formula": "2 operadores × 5.45 pedidos/h combinados; 2 repartidores × 7.17 entregas/h",
      "supuestos_usados": [
        {
          "clave": "********",
          "valor": 70.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 85.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 1.35,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 10.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 20.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 30.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 22.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 4.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 3.0,
          "modificado": false
        }
      ]
    },
    {
      "microhub": {
        "id": 4,
        "nombre": "Microhub Piloto Alianza"
      },
      "operadores": 2,
      "repartidores": 2,
      "capacidad_fisica": 110,
      "horas": 10.0,
      "distancia_km": 2.4,
      "carga_dia": 40.0,
      "capacidad_hora": 10.91,
      "capacidad_dia": 109.1,
      "utilizacion_pct": 36.7,
      "nivel": "estable",
      "utilizacion_pico_pct": 49.5,
      "nivel_pico": "estable",
      "cuello_botella": "operacion",
      "minutos_por_pedido_operacion": 11.0,
      "minutos_por_entrega": 8.4,
      "etapas": [
        {
          "etapa": "picking",
          "minutos_por_pedido": 6.0,
          "pct_tiempo": 54.5,
          "capacidad_hora": 20.0
        },
        {
          "etapa": "empaque",
          "minutos_por_pedido": 3.0,
          "pct_tiempo": 27.3,
          "capacidad_hora": 40.0
        },
        {
          "etapa": "despacho",
          "minutos_por_pedido": 2.0,
          "pct_tiempo": 18.2,
          "capacidad_hora": 60.0
        },
        {
          "etapa": "reparto",
          "minutos_por_pedido": 8.4,
          "pct_tiempo": null,
          "capacidad_hora": 14.3
        }
      ],
      "operadores_requeridos": 1,
      "repartidores_requeridos": 1,
      "holgura_pedidos_dia": 69.1,
      "formula": "2 operadores × 5.45 pedidos/h combinados; 2 repartidores × 7.17 entregas/h",
      "supuestos_usados": [
        {
          "clave": "********",
          "valor": 70.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 85.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 1.35,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 10.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 20.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 30.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 22.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 4.0,
          "modificado": false
        },
        {
          "clave": "********",
          "valor": 3.0,
          "modificado": false
        }
      ]
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 100,
    "total": 4,
    "paginas": 1
  }
}
```

### CAP-04 · Un microhub saturado · PASA

**Objetivo.** Con 95 % de la capacidad el nivel es de riesgo (umbral 85 %).

**Petición.** `GET http://capacidad:5117/api/v1/capacidad/microhubs/1?carga_dia=140`

```http
Accept: application/json
X-Traza-Id: a51e7299-48b1-4dba-86ed-4bab7f645b72
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 45 ms · traza `a51e7299-48b1-4dba-86ed-4bab7f645b72`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "operadores": 3,
  "repartidores": 3,
  "capacidad_fisica": 150,
  "horas": 10.0,
  "distancia_km": 2.4,
  "carga_dia": 140.0,
  "capacidad_hora": 16.36,
  "capacidad_dia": 150,
  "utilizacion_pct": 93.3,
  "nivel": "riesgo",
  "utilizacion_pico_pct": 115.5,
  "nivel_pico": "riesgo",
  "cuello_botella": "espacio físico",
  "minutos_por_pedido_operacion": 11.0,
  "minutos_por_entrega": 8.4,
  "etapas": [
    {
      "etapa": "picking",
      "minutos_por_pedido": 6.0,
      "pct_tiempo": 54.5,
      "capacidad_hora": 30.0
    },
    {
      "etapa": "empaque",
      "minutos_por_pedido": 3.0,
      "pct_tiempo": 27.3,
      "capacidad_hora": 60.0
    },
    {
      "etapa": "despacho",
      "minutos_por_pedido": 2.0,
      "pct_tiempo": 18.2,
      "capacidad_hora": 90.0
    },
    {
      "etapa": "reparto",
      "minutos_por_pedido": 8.4,
      "pct_tiempo": null,
      "capacidad_hora": 21.5
    }
  ],
  "operadores_requeridos": 4,
  "repartidores_requeridos": 3,
  "holgura_pedidos_dia": 10.0,
  "formula": "3 operadores × 5.45 pedidos/h combinados; 3 repartidores × 7.17 entregas/h",
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 70.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 85.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 1.35,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 10.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 20.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.0,
      "modificado": false
    }
  ]
}
```

### CAP-05 · Horas fuera de rango · PASA

**Objetivo.** horas va de 1 a 24.

**Petición.** `GET http://capacidad:5117/api/v1/capacidad/microhubs/1?horas=99`

```http
Accept: application/json
X-Traza-Id: 228512b3-c8ad-4c34-bec3-4a98892280f7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 28 ms · traza `228512b3-c8ad-4c34-bec3-4a98892280f7`

```json
{
  "error": {
    "codigo": "FILTRO_INVALIDO",
    "mensaje": "horas debe estar entre 1 y 24.",
    "detalles": [
      {
        "campo": "horas",
        "mensaje": "horas debe estar entre 1 y 24."
      }
    ],
    "traza_id": "228512b3-c8ad-4c34-bec3-4a98892280f7"
  }
}
```

### CAP-06 · Capacidad (XML) · PASA

**Objetivo.** Respuesta XML que cumple capacidad.xsd.

**Petición.** `GET http://capacidad:5117/api/v1/capacidad/microhubs/1?carga_dia=60`

```http
Accept: application/xml
X-Traza-Id: 2f3091fd-232b-4dba-8faa-584ef8ed85a7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 90 ms · traza `2f3091fd-232b-4dba-8faa-584ef8ed85a7`

```xml
<?xml version='1.0' encoding='utf-8'?>
<capacidad_microhub xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><operadores>3</operadores><repartidores>3</repartidores><capacidad_fisica>150</capacidad_fisica><horas>10</horas><distancia_km>2.4</distancia_km><carga_dia>60</carga_dia><capacidad_hora>16.36</capacidad_hora><capacidad_dia>150</capacidad_dia><utilizacion_pct>40</utilizacion_pct><nivel>estable</nivel><utilizacion_pico_pct>49.5</utilizacion_pico_pct><nivel_pico>estable</nivel_pico><cuello_botella>espacio físico</cuello_botella><minutos_por_pedido_operacion>11</minutos_por_pedido_operacion><minutos_por_entrega>8.4</minutos_por_entrega><etapas><etapa><etapa>picking</etapa><minutos_por_pedido>6</minutos_por_pedido><pct_tiempo>54.5</pct_tiempo><capacidad_hora>30</capacidad_hora></etapa><etapa><etapa>empaque</etapa><minutos_por_pedido>3</minutos_por_pedido><pct_tiempo>27.3</pct_tiempo><capacidad_hora>60</capacidad_hora></etapa><etapa><etapa>despacho</etapa><minutos_por_pedido>2</minutos_por_pedido><pct_tiempo>18.2</pct_tiempo><capacidad_hora>90</capacidad_hora></etapa><etapa><etapa>reparto</etapa><minutos_por_pedido>8.4</minutos_por_pedido><pct_tiempo xsi:nil="true" /><capacidad_hora>21.5</capacidad_hora></etapa></etapas><operadores_requeridos>2</operadores_requeridos><repartidores_requeridos>1</repartidores_requeridos><holgura_pedidos_dia>90</holgura_pedidos_dia><formula>3 operadores × 5.45 pedidos/h combinados; 3 repartidores × 7.17 entregas/h</formula><supuestos_usados><supuesto><clave>umbral_utilizacion_estable</clave><valor>70</valor><modificado>false</modificado></supuesto><supuesto><clave>umbral_utilizacion_riesgo</clave><valor>85</valor><modificado>false</modificado></supuesto><supuesto><clave>cap_factor_pico</clave><valor>1.35</valor><modificado>false</modificado></supuesto><supuesto><clave>picking_pedidos_hora</clave><valor>10</valor><modificado>false</modificado></supuesto><supuesto><clave>packing_pedidos_hora</clave><valor>20</valor><modificado>false</modificado></supuesto><supuesto><clave>despacho_pedidos_hora</clave><valor>30</valor><modificado>false</modificado></supuesto><supuesto><clave>velocidad_reparto_kmh</clave><valor>22</valor><modificado>false</modificado></supuesto><supuesto><clave>tiempo_servicio_min</clave><valor>4</valor><modificado>false</modificado></supuesto><supuesto><clave>paradas_por_viaje</clave><valor>3</valor><modificado>false</modificado></supuesto></supuestos_usados></capacidad_microhub>
```

### CAP-07 · Simular más personal · PASA

**Objetivo.** Qué pasa con 120 pedidos al día y 6 operadores y 6 repartidores.

**Petición.** `POST http://capacidad:5117/api/v1/capacidad/simulaciones`

```http
Accept: application/json
X-Traza-Id: 49e6a865-eb18-4542-9426-3d361cb06ca4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "pedidos_dia": 120,
  "operadores": 6,
  "repartidores": 6,
  "capacidad_fisica": 1000
}
```

**Respuesta.** HTTP 200 (esperado 200) · 47 ms · traza `49e6a865-eb18-4542-9426-3d361cb06ca4`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "pedidos_dia": 120.0,
  "escenario": {
    "operadores": 6,
    "repartidores": 6,
    "capacidad_fisica": 1000,
    "horas": 10.0,
    "distancia_km": 2.4,
    "carga_dia": 120.0,
    "capacidad_hora": 32.73,
    "capacidad_dia": 327.3,
    "utilizacion_pct": 36.7,
    "nivel": "estable",
    "utilizacion_pico_pct": 49.5,
    "nivel_pico": "estable",
    "cuello_botella": "operacion",
    "minutos_por_pedido_operacion": 11.0,
    "minutos_por_entrega": 8.4,
    "etapas": [
      {
        "etapa": "picking",
        "minutos_por_pedido": 6.0,
        "pct_tiempo": 54.5,
        "capacidad_hora": 60.0
      },
      {
        "etapa": "empaque",
        "minutos_por_pedido": 3.0,
        "pct_tiempo": 27.3,
        "capacidad_hora": 120.0
      },
      {
        "etapa": "despacho",
        "minutos_por_pedido": 2.0,
        "pct_tiempo": 18.2,
        "capacidad_hora": 180.0
      },
      {
        "etapa": "reparto",
        "minutos_por_pedido": 8.4,
        "pct_tiempo": null,
        "capacidad_hora": 43.0
      }
    ],
    "operadores_requeridos": 3,
    "repartidores_requeridos": 2,
    "holgura_pedidos_dia": 207.3,
    "formula": "6 operadores × 5.45 pedidos/h combinados; 6 repartidores × 7.17 entregas/h"
  },
  "actual": {
    "operadores": 3,
    "repartidores": 3,
    "capacidad_fisica": 150,
    "horas": 10.0,
    "distancia_km": 2.4,
    "carga_dia": 120.0,
    "capacidad_hora": 16.36,
    "capacidad_dia": 150,
    "utilizacion_pct": 80.0,
    "nivel": "atencion",
    "utilizacion_pico_pct": 99.0,
    "nivel_pico": "riesgo",
    "cuello_botella": "espacio físico",
    "minutos_por_pedido_operacion": 11.0,
    "minutos_por_entrega": 8.4,
    "etapas": [
      {
        "etapa": "picking",
        "minutos_por_pedido": 6.0,
        "pct_tiempo": 54.5,
        "capacidad_hora": 30.0
      },
      {
        "etapa": "empaque",
        "minutos_por_pedido": 3.0,
        "pct_tiempo": 27.3,
        "capacidad_hora": 60.0
      },
      {
        "etapa": "despacho",
        "minutos_por_pedido": 2.0,
        "pct_tiempo": 18.2,
        "capacidad_hora": 90.0
      },
      {
        "etapa": "reparto",
        "minutos_por_pedido": 8.4,
        "pct_tiempo": null,
        "capacidad_hora": 21.5
      }
    ],
    "operadores_requeridos": 3,
    "repartidores_requeridos": 2,
    "holgura_pedidos_dia": 30.0,
    "formula": "3 operadores × 5.45 pedidos/h combinados; 3 repartidores × 7.17 entregas/h"
  },
  "diferencia_capacidad_dia": 177.3,
  "diferencia_utilizacion_pct": -43.3,
  "valores_modificados": [
    "operadores",
    "repartidores",
    "capacidad_fisica"
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 70.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 85.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 1.35,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 10.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 20.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.0,
      "modificado": false
    }
  ]
}
```

### CAP-08 · Curva de carga · PASA

**Objetivo.** Utilización a distintas cargas y el punto donde se pasa del umbral.

**Petición.** `GET http://capacidad:5117/api/v1/capacidad/cargas?microhub_id=1`

```http
Accept: application/json
X-Traza-Id: f2af4fd8-bfb3-4dfd-a8b8-c9a461a75835
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 45 ms · traza `f2af4fd8-bfb3-4dfd-a8b8-c9a461a75835`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "capacidad_dia": 150,
  "carga_en_riesgo": 127.5,
  "carga_estable": 105.0,
  "filas": [
    {
      "pedidos_dia": 37.5,
      "utilizacion_pct": 25.0,
      "nivel": "estable",
      "utilizacion_pico_pct": 30.9,
      "atendidos": 37.5,
      "rechazados": 0
    },
    {
      "pedidos_dia": 64.3,
      "utilizacion_pct": 42.9,
      "nivel": "estable",
      "utilizacion_pico_pct": 53.0,
      "atendidos": 64.3,
      "rechazados": 0
    },
    {
      "pedidos_dia": 91.1,
      "utilizacion_pct": 60.7,
      "nivel": "estable",
      "utilizacion_pico_pct": 75.2,
      "atendidos": 91.1,
      "rechazados": 0
    },
    {
      "pedidos_dia": 117.9,
      "utilizacion_pct": 78.6,
      "nivel": "atencion",
      "utilizacion_pico_pct": 97.3,
      "atendidos": 117.9,
      "rechazados": 0
    },
    {
      "pedidos_dia": 144.6,
      "utilizacion_pct": 96.4,
      "nivel": "riesgo",
      "utilizacion_pico_pct": 119.4,
      "atendidos": 144.6,
      "rechazados": 0
    },
    {
      "pedidos_dia": 171.4,
      "utilizacion_pct": 114.3,
      "nivel": "riesgo",
      "utilizacion_pico_pct": 141.5,
      "atendidos": 150,
      "rechazados": 21.4
    },
    {
      "pedidos_dia": 198.2,
      "utilizacion_pct": 132.1,
      "nivel": "riesgo",
      "utilizacion_pico_pct": 163.6,
      "atendidos": 150,
      "rechazados": 48.2
    },
    {
      "pedidos_dia": 225.0,
      "utilizacion_pct": 150.0,
      "nivel": "riesgo",
      "utilizacion_pico_pct": 185.7,
      "atendidos": 150,
      "rechazados": 75.0
    }
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 70.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 85.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 1.35,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 10.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 20.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.0,
      "modificado": false
    }
  ]
}
```

### CAP-09 · Cambiar el personal · PASA

**Objetivo.** El planeador corrige operadores y repartidores del microhub.

**Petición.** `PUT http://capacidad:5117/api/v1/capacidad/recursos/1`

```http
Accept: application/json
X-Traza-Id: 2f0e18ae-799e-4fb2-89a4-e9d6ed835dac
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "operadores": 4,
  "repartidores": 3,
  "capacidad_fisica": 150
}
```

**Respuesta.** HTTP 200 (esperado 200) · 54 ms · traza `2f0e18ae-799e-4fb2-89a4-e9d6ed835dac`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "operadores": 4,
  "repartidores": 3,
  "capacidad_fisica": 150,
  "actualizado_en": "2026-11-26T14:19:54-06:00"
}
```

**Evidencia en PostgreSQL.** `SELECT operadores, repartidores, capacidad_fisica FROM capacidad_recurso WHERE microhub_id = %s`

```json
[
  {
    "operadores": 4,
    "repartidores": 3,
    "capacidad_fisica": 150
  }
]
```

**Evidencia en PostgreSQL.** `SELECT accion, valores_anteriores, valores_nuevos FROM auditoria WHERE entidad = 'capacidad_recurso' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "accion": "modificacion",
    "valores_anteriores": {
      "operadores": 3,
      "actualizado_en": "2026-11-26T14:05:06.969982-06:00"
    },
    "valores_nuevos": {
      "operadores": 4,
      "actualizado_en": "2026-11-26T14:19:54.152364-06:00"
    }
  }
]
```

### CAP-10 · Cambiar el personal sin permiso · PASA

**Objetivo.** El operador no tiene capacidad.editar.

**Petición.** `PUT http://capacidad:5117/api/v1/capacidad/recursos/1`

```http
Accept: application/json
X-Traza-Id: 84cde4fc-c20b-49f6-998b-996ffb06104a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "operadores": 9,
  "repartidores": 9
}
```

**Respuesta.** HTTP 403 (esperado 403) · 28 ms · traza `84cde4fc-c20b-49f6-998b-996ffb06104a`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "84cde4fc-c20b-49f6-998b-996ffb06104a"
  }
}
```

### CAP-11 · Personal inválido · PASA

**Objetivo.** Al menos un operador.

**Petición.** `PUT http://capacidad:5117/api/v1/capacidad/recursos/1`

```http
Accept: application/json
X-Traza-Id: eecca9cb-7568-4798-b9f7-8bd6e8d8f450
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "operadores": 0,
  "repartidores": 3
}
```

**Respuesta.** HTTP 422 (esperado 422) · 7 ms · traza `eecca9cb-7568-4798-b9f7-8bd6e8d8f450`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "operadores",
        "mensaje": "Debe ser mayor o igual a 1."
      }
    ],
    "traza_id": "eecca9cb-7568-4798-b9f7-8bd6e8d8f450"
  }
}
```

### CAP-12 · Supuestos de la capacidad · PASA

**Objetivo.** Productividad por etapa, umbrales y horas del turno.

**Petición.** `GET http://capacidad:5117/api/v1/capacidad/supuestos`

```http
Accept: application/json
X-Traza-Id: 27081e3b-32a4-4c84-b71a-70b55a739d77
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 33 ms · traza `27081e3b-32a4-4c84-b71a-70b55a739d77`

```json
{
  "datos": [
    {
      "clave": "********",
      "valor": "2.4",
      "unidad": "km",
      "origen": "supuesto",
      "justificacion": "Distancia típica de entrega desde el microhub, ida solamente; es el valor del Escenario A de la retroalimentación.",
      "como_calibrar": "Distancia promedio entre el microhub y los domicilios de las entregas cerradas."
    },
    {
      "clave": "********",
      "valor": "1.35",
      "unidad": "veces",
      "origen": "supuesto",
      "justificacion": "La hora pico recibe de 1.3 a 1.4 veces el promedio horario.",
      "como_calibrar": "Distribución de pedidos por hora de pedido.creado_en."
    },
    {
      "clave": "********",
      "valor": "30",
      "unidad": "pedidos/h",
      "origen": "supuesto",
      "justificacion": "Un operador despacha unos 30 pedidos por hora (2 minutos: verificar y entregar al repartidor).",
      "como_calibrar": "Tiempo entre listo_en y la salida del repartidor."
    },
    {
      "clave": "********",
      "valor": "10",
      "unidad": "horas",
      "origen": "supuesto",
      "justificacion": "El microhub abre 12 horas (8 a 20 h); se toman 10 de trabajo efectivo descontando comida y cierre.",
      "como_calibrar": "Horas realmente trabajadas según la asistencia del personal."
    },
    {
      "clave": "********",
      "valor": "20",
      "unidad": "pedidos/h",
      "origen": "supuesto",
      "justificacion": "Un operador empaca unos 20 pedidos por hora (3 minutos por pedido).",
      "como_calibrar": "Cronometrar una muestra de pedidos en el área de empaque."
    },
    {
      "clave": "********",
      "valor": "3",
      "unidad": "paradas",
      "origen": "supuesto",
      "justificacion": "Paradas promedio de una salida cuando los pedidos se agrupan por zona. Reparte el costo del regreso al microhub entre ellas.",
      "como_calibrar": "Promedio de la columna paradas de plan_ruta."
    },
    {
      "clave": "********",
      "valor": "10",
      "unidad": "pedidos/h",
      "origen": "supuesto",
      "justificacion": "Un operador junta unos 10 pedidos por hora (6 minutos por pedido de cinco líneas aproximadamente).",
      "como_calibrar": "Tiempo entre asignado y en_preparacion en historial_estatus, o cronometrar una muestra de pedidos."
    },
    {
      "clave": "********",
      "valor": "4",
      "unidad": "minutos",
      "origen": "supuesto",
      "justificacion": "Minutos que el repartidor pasa en cada parada: estacionar, entregar, cobrar y confirmar con el cliente.",
      "como_calibrar": "Diferencia entre la llegada al domicilio y el cierre de la entrega en el recorrido GPS."
    },
    {
      "clave": "********",
      "valor": "70",
      "unidad": "porcentaje",
      "origen": "supuesto",
      "justificacion": "Por debajo de 70 % queda holgura para los picos, que suelen ser de 1.3 a 1.4 veces el promedio.",
      "como_calibrar": "Comparar la utilización por hora con los días en que hubo retrasos o rechazos."
    },
    {
      "clave": "********",
      "valor": "85",
      "unidad": "porcentaje",
      "origen": "supuesto",
      "justificacion": "Por encima de 85 % la espera en una fila crece muy rápido (teoría de colas), así que se considera riesgo de saturación.",
      "como_calibrar": "Medir el tiempo de espera de los pedidos contra la utilización de cada día."
    },
    {
      "clave": "********",
      "valor": "22",
      "unidad": "km/h",
      "origen": "supuesto",
      "justificacion": "Velocidad media de un repartidor en moto o bicicleta dentro …(180 caracteres)",
      "como_calibrar": "Dividir la distancia del recorrido GPS entre su duración en …(147 caracteres)"
    }
  ]
}
```

## Servicio costos · puerto 5119

### COS-01 · Conceptos de un microhub · PASA

**Objetivo.** Los globales (pago al repartidor, empaque, comisión) y los propios (renta, nómina…).

**Petición.** `GET http://costos:5119/api/v1/costos/conceptos?microhub_id=1&por_pagina=100`

```http
Accept: application/json
X-Traza-Id: f26a68e8-fc2d-443a-9d56-e2a37fab1fda
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 49 ms · traza `f26a68e8-fc2d-443a-9d56-e2a37fab1fda`

```json
{
  "datos": [
    {
      "id": 2,
      "ambito": "global",
      "ambito_id": null,
      "nombre": "Combustible y desgaste",
      "categoria": "transporte",
      "tipo": "variable",
      "unidad": "km",
      "monto": 4.5,
      "vigente_desde": "2026-10-19",
      "vigente_hasta": null,
      "estatus": "activo",
      "fuente": "supuesto",
      "justificacion": "Combustible, mantenimiento y desgaste de una moto pequeña; mismo valor que costo_km_reparto."
    },
    {
      "id": 4,
      "ambito": "global",
      "ambito_id": null,
      "nombre": "Comisión por pago con tarjeta",
      "categoria": "operacion",
      "tipo": "variable",
      "unidad": "pct_venta",
      "monto": 2.9,
      "vigente_desde": "2026-10-19",
      "vigente_hasta": null,
      "estatus": "activo",
      "fuente": "supuesto",
      "justificacion": "Comisión típica de un cobro con terminal o link de pago. Confirmar con el contrato del procesador."
    },
    {
      "id": 3,
      "ambito": "global",
      "ambito_id": null,
      "nombre": "Empaque por pedido",
      "categoria": "operacion",
      "tipo": "variable",
      "unidad": "pedido",
      "monto": 3.5,
      "vigente_desde": "2026-10-19",
      "vigente_hasta": null,
      "estatus": "activo",
      "fuente": "supuesto",
      "justificacion": "Bolsa, sello y etiqueta de un pedido de unas cinco líneas. Estimación a confirmar con el proveedor de empaque."
    },
    {
      "id": 1,
      "ambito": "global",
      "ambito_id": null,
      "nombre": "Pago base al repartidor",
      "categoria": "transporte",
      "tipo": "variable",
      "unidad": "entrega",
      "monto": 18.0,
      "vigente_desde": "2026-10-19",
      "vigente_hasta": null,
      "estatus": "activo",
      "fuente": "supuesto",
      "justificacion": "Pago fijo por entrega; mismo valor que el parámetro costo_base_entrega."
    },
    {
      "id": 5,
      "ambito": "microhub",
      "ambito_id": 1,
      "nombre": "Mantenimiento y seguros",
      "categoria": "otros",
      "tipo": "fijo",
      "unidad": "mes",
      "monto": 2500.0,
      "vigente_desde": "2026-10-19",
      "vigente_hasta": null,
      "estatus": "activo",
      "fuente": "supuesto",
      "justificacion": "Seguro del local y mantenimiento menor; estimación a confirmar con la aseguradora."
    },
    {
      "id": 7,
      "ambito": "microhub",
      "ambito_id": 1,
      "nombre": "Nómina de operadores",
      "categoria": "personal",
      "tipo": "fijo",
      "unidad": "mes",
      "monto": 42000.0,
      "vigente_desde": "2026-10-19",
      "vigente_hasta": null,
      "estatus": "activo",
      "fuente": "supuesto",
      "justificacion": "Tres operadores a 14,000 pesos mensuales con prestaciones; cuadra con los recursos de capacidad."
    },
    {
      "id": 8,
      "ambito": "microhub",
      "ambito_id": 1,
      "nombre": "Renta del local",
      "categoria": "renta",
      "tipo": "fijo",
      "unidad": "mes",
      "monto": 18000.0,
      "vigente_desde": "2026-10-19",
      "vigente_hasta": null,
      "estatus": "activo",
      "fuente": "supuesto",
      "justificacion": "Renta mensual estimada de un local comercial pequeño en el sector; sustituir por el contrato."
    },
    {
      "id": 6,
      "ambito": "microhub",
      "ambito_id": 1,
      "nombre": "Servicios (luz, agua, internet)",
      "categoria": "servicios",
      "tipo": "fijo",
      "unidad": "mes",
      "monto": 7000.0,
      "vigente_desde": "2026-10-19",
      "vigente_hasta": null,
      "estatus": "activo",
      "fuente": "supuesto",
      "justificacion": "Consumo estimado de un local con refrigeración básica."
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 100,
    "total": 8,
    "paginas": 1
  }
}
```

**Evidencia en PostgreSQL.** `SELECT ambito, tipo, categoria, count(*) AS conceptos, sum(monto) AS monto FROM costo_concepto WHERE estatus = 'activo' AND (ambito = 'global' OR (ambito = 'microhub' AND ambito_id = %s)) GROUP BY ambito, tipo, categoria ORDER BY 1, 2, 3`

```json
[
  {
    "ambito": "global",
    "tipo": "variable",
    "categoria": "operacion",
    "conceptos": 2,
    "monto": "6.40"
  },
  {
    "ambito": "global",
    "tipo": "variable",
    "categoria": "transporte",
    "conceptos": 2,
    "monto": "22.50"
  },
  {
    "ambito": "microhub",
    "tipo": "fijo",
    "categoria": "otros",
    "conceptos": 1,
    "monto": "2500.00"
  },
  {
    "ambito": "microhub",
    "tipo": "fijo",
    "categoria": "personal",
    "conceptos": 1,
    "monto": "42000.00"
  },
  {
    "ambito": "microhub",
    "tipo": "fijo",
    "categoria": "renta",
    "conceptos": 1,
    "monto": "18000.00"
  },
  {
    "ambito": "microhub",
    "tipo": "fijo",
    "categoria": "servicios",
    "conceptos": 1,
    "monto": "7000.00"
  }
]
```

### COS-02 · Resumen de costos · PASA

**Objetivo.** Fijos del mes por categoría y variables por unidad.

**Petición.** `GET http://costos:5119/api/v1/costos/resumen?microhub_id=1`

```http
Accept: application/json
X-Traza-Id: 40b74a22-e1e6-48af-b1be-eff6d5214aa6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 30 ms · traza `40b74a22-e1e6-48af-b1be-eff6d5214aa6`

```json
{
  "ambito": "microhub",
  "ambito_id": 1,
  "origen": "costos",
  "conceptos": 8,
  "fijos_mes": 69500.0,
  "por_categoria": [
    {
      "categoria": "otros",
      "monto": 2500.0
    },
    {
      "categoria": "personal",
      "monto": 42000.0
    },
    {
      "categoria": "renta",
      "monto": 18000.0
    },
    {
      "categoria": "servicios",
      "monto": 7000.0
    }
  ],
  "variables": [
    {
      "nombre": "Comisión por pago con tarjeta",
      "unidad": "pct_venta",
      "monto": 2.9
    },
    {
      "nombre": "Empaque por pedido",
      "unidad": "pedido",
      "monto": 3.5
    },
    {
      "nombre": "Combustible y desgaste",
      "unidad": "km",
      "monto": 4.5
    },
    {
      "nombre": "Pago base al repartidor",
      "unidad": "entrega",
      "monto": 18.0
    }
  ],
  "variable_pedido": 3.5,
  "variable_entrega": 18.0,
  "variable_km": 4.5,
  "comision_pct": 2.9
}
```

### COS-03 · Costo por pedido y por entrega · PASA

**Objetivo.** Costo fijo ÷ pedidos del mes + variable + comisión + entrega.

**Petición.** `GET http://costos:5119/api/v1/costos/unitarios?microhub_id=1&pedidos_mes=1000&ticket=150`

```http
Accept: application/json
X-Traza-Id: 202a8d19-f666-42fb-b403-98766007b86f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 48 ms · traza `202a8d19-f666-42fb-b403-98766007b86f`

```json
{
  "entrada": {
    "ambito": "microhub",
    "ambito_id": 1,
    "origen": "costos",
    "pedidos_mes": 1000.0,
    "ticket": 150.0,
    "margen_bruto": 0.28,
    "distancia_km": 2.4,
    "paradas_por_viaje": 3.0,
    "valores_modificados": [
      "pedidos_mes",
      "ticket"
    ]
  },
  "fijos_mes": 69500.0,
  "costo_fijo_pedido": 69.5,
  "variable_pedido": 3.5,
  "comision_pedido": 4.35,
  "costo_entrega": 25.2,
  "costo_variable_pedido": 33.05,
  "costo_por_pedido": 102.55,
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 1000.0,
      "modificado": true
    },
    {
      "clave": "********",
      "valor": 150.0,
      "modificado": true
    },
    {
      "clave": "********",
      "valor": 0.28,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 2.4,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 18.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.5,
      "modificado": false
    }
  ]
}
```

**Explicación.** Costo de entrega = pago por entrega + 2 × distancia × costo por km ÷ paradas por viaje. Los valores que la petición cambia aparecen en «valores_modificados».

### COS-04 · Rentabilidad · PASA

**Objetivo.** Margen de contribución, utilidad del mes y margen operativo.

**Petición.** `GET http://costos:5119/api/v1/costos/rentabilidad?microhub_id=1&pedidos_mes=1500`

```http
Accept: application/json
X-Traza-Id: 469f14d9-1626-4de4-9b3f-aec0c63c1aa3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 85 ms · traza `469f14d9-1626-4de4-9b3f-aec0c63c1aa3`

```json
{
  "entrada": {
    "ambito": "microhub",
    "ambito_id": 1,
    "origen": "costos",
    "pedidos_mes": 1500.0,
    "ticket": 135.0,
    "margen_bruto": 0.28,
    "distancia_km": 2.4,
    "paradas_por_viaje": 3.0,
    "valores_modificados": [
      "pedidos_mes"
    ]
  },
  "ingresos_mes": 202500.0,
  "margen_bruto_mes": 56700.0,
  "costo_variable_mes": 48922.5,
  "margen_contribucion_pedido": 5.19,
  "margen_contribucion_mes": 7777.5,
  "costos_fijos_mes": 69500.0,
  "utilidad_mes": -61722.5,
  "margen_operativo_pct": -30.48,
  "costo_por_pedido": 78.95,
  "cubre_costos": false,
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 1500.0,
      "modificado": true
    },
    {
      "clave": "********",
      "valor": 135.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.28,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 2.4,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 18.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.5,
      "modificado": false
    }
  ]
}
```

### COS-05 · Sensibilidad de costos · PASA

**Objetivo.** Cada palanca sube y baja 10 y 20 %; se dice cuál mueve más la utilidad.

**Petición.** `GET http://costos:5119/api/v1/costos/sensibilidad?microhub_id=1&pedidos_mes=1500`

```http
Accept: application/json
X-Traza-Id: 73b76180-a2c7-4b96-907a-1b6315f49196
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 52 ms · traza `73b76180-a2c7-4b96-907a-1b6315f49196`

```json
{
  "entrada": {
    "ambito": "microhub",
    "ambito_id": 1,
    "origen": "costos",
    "pedidos_mes": 1500.0,
    "ticket": 135.0,
    "margen_bruto": 0.28,
    "distancia_km": 2.4,
    "paradas_por_viaje": 3.0,
    "valores_modificados": [
      "pedidos_mes"
    ]
  },
  "costo_por_pedido": 78.95,
  "utilidad_mes": -61722.5,
  "palanca_mas_sensible": "Fijo: personal",
  "filas": [
    {
      "palanca": "Fijo: otros",
      "cambio_pct": -20,
      "costo_por_pedido": 78.62,
      "utilidad_mes": -61222.5,
      "cambio_utilidad": 500.0
    },
    {
      "palanca": "Fijo: otros",
      "cambio_pct": -10,
      "costo_por_pedido": 78.78,
      "utilidad_mes": -61472.5,
      "cambio_utilidad": 250.0
    },
    {
      "palanca": "Fijo: otros",
      "cambio_pct": 10,
      "costo_por_pedido": 79.12,
      "utilidad_mes": -61972.5,
      "cambio_utilidad": -250.0
    },
    {
      "palanca": "Fijo: otros",
      "cambio_pct": 20,
      "costo_por_pedido": 79.28,
      "utilidad_mes": -62222.5,
      "cambio_utilidad": -500.0
    },
    {
      "palanca": "Fijo: personal",
      "cambio_pct": -20,
      "costo_por_pedido": 73.35,
      "utilidad_mes": -53322.5,
      "cambio_utilidad": 8400.0
    },
    {
      "palanca": "Fijo: personal",
      "cambio_pct": -10,
      "costo_por_pedido": 76.15,
      "utilidad_mes": -57522.5,
      "cambio_utilidad": 4200.0
    },
    {
      "palanca": "Fijo: personal",
      "cambio_pct": 10,
      "costo_por_pedido": 81.75,
      "utilidad_mes": -65922.5,
      "cambio_utilidad": -4200.0
    },
    {
      "palanca": "Fijo: personal",
      "cambio_pct": 20,
      "costo_por_pedido": 84.55,
      "utilidad_mes": -70122.5,
      "cambio_utilidad": -8400.0
    },
    {
      "palanca": "Fijo: renta",
      "cambio_pct": -20,
      "costo_por_pedido": 76.55,
      "utilidad_mes": -58122.5,
      "cambio_utilidad": 3600.0
    },
    {
      "palanca": "Fijo: renta",
      "cambio_pct": -10,
      "costo_por_pedido": 77.75,
      "utilidad_mes": -59922.5,
      "cambio_utilidad": 1800.0
    },
    {
      "palanca": "Fijo: renta",
      "cambio_pct": 10,
      "costo_por_pedido": 80.15,
      "utilidad_mes": -63522.5,
      "cambio_utilidad": -1800.0
    },
    {
      "palanca": "Fijo: renta",
      "cambio_pct": 20,
      "costo_por_pedido": 81.35,
      "utilidad_mes": -65322.5,
      "cambio_utilidad": -3600.0
    },
    {
      "palanca": "Fijo: servicios",
      "cambio_pct": -20,
      "costo_por_pedido": 78.02,
      "utilidad_mes": -60322.5,
      "cambio_utilidad": 1400.0
    },
    {
      "palanca": "Fijo: servicios",
      "cambio_pct": -10,
      "costo_por_pedido": 78.48,
      "utilidad_mes": -61022.5,
      "cambio_utilidad": 700.0
    },
    {
      "palanca": "Fijo: servicios",
      "cambio_pct": 10,
      "costo_por_pedido": 79.41,
      "utilidad_mes": -62422.5,
      "cambio_utilidad": -700.0
    },
    {
      "palanca": "Fijo: servicios",
      "cambio_pct": 20,
      "costo_por_pedido": 79.88,
      "utilidad_mes": -63122.5,
      "cambio_utilidad": -1400.0
    },
    {
      "palanca": "Pago y kilometraje de la entrega",
      "cambio_pct": -20,
      "costo_por_pedido": 73.91,
      "utilidad_mes": -54162.5,
      "cambio_utilidad": 7560.0
    },
    {
      "palanca": "Pago y kilometraje de la entrega",
      "cambio_pct": -10,
      "costo_por_pedido": 76.43,
      "utilidad_mes": -57942.5,
      "cambio_utilidad": 3780.0
    },
    {
      "palanca": "Pago y kilometraje de la entrega",
      "cambio_pct": 10,
      "costo_por_pedido": 81.47,
      "utilidad_mes": -65502.5,
      "cambio_utilidad": -3780.0
    },
    {
      "palanca": "Pago y kilometraje de la entrega",
      "cambio_pct": 20,
      "costo_por_pedido": 83.99,
      "utilidad_mes": -69282.5,
      "cambio_utilidad": -7560.0
    },
    {
      "palanca": "Costos variables por pedido",
      "cambio_pct": -20,
      "costo_por_pedido": 78.25,
      "utilidad_mes": -60672.5,
      "cambio_utilidad": 1050.0
    },
    {
      "palanca": "Costos variables por pedido",
      "cambio_pct": -10,
      "costo_por_pedido": 78.6,
      "utilidad_mes": -61197.5,
      "cambio_utilidad": 525.0
    },
    {
      "palanca": "Costos variables por pedido",
      "cambio_pct": 10,
      "costo_por_pedido": 79.3,
      "utilidad_mes": -62247.5,
      "cambio_utilidad": -525.0
    },
    {
      "palanca": "Costos variables por pedido",
      "cambio_pct": 20,
      "costo_por_pedido": 79.65,
      "utilidad_mes": -62772.5,
      "cambio_utilidad": -1050.0
    }
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 1500.0,
      "modificado": true
    },
    {
      "clave": "********",
      "valor": 135.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.28,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 2.4,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 18.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.5,
      "modificado": false
    }
  ]
}
```

### COS-06 · Costos (XML) · PASA

**Objetivo.** Respuesta XML que cumple costos.xsd.

**Petición.** `GET http://costos:5119/api/v1/costos/unitarios?microhub_id=1`

```http
Accept: application/xml
X-Traza-Id: 640e49a6-1eb6-4d09-a8c9-1762b8907fe4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 89 ms · traza `640e49a6-1eb6-4d09-a8c9-1762b8907fe4`

```xml
<?xml version='1.0' encoding='utf-8'?>
<costos_unitarios xmlns="urn:microhubs:v1" version="1"><entrada><ambito>microhub</ambito><ambito_id>1</ambito_id><origen>costos</origen><pedidos_mes>1800</pedidos_mes><ticket>135.00</ticket><margen_bruto>0.28</margen_bruto><distancia_km>2.4</distancia_km><paradas_por_viaje>3</paradas_por_viaje><valores_modificados /></entrada><fijos_mes>69500.00</fijos_mes><costo_fijo_pedido>38.61</costo_fijo_pedido><variable_pedido>3.50</variable_pedido><comision_pedido>3.92</comision_pedido><costo_entrega>25.20</costo_entrega><costo_variable_pedido>32.62</costo_variable_pedido><costo_por_pedido>71.23</costo_por_pedido><supuestos_usados><supuesto><clave>pedidos_mes</clave><valor>1800</valor><modificado>false</modificado></supuesto><supuesto><clave>ticket</clave><valor>135</valor><modificado>false</modificado></supuesto><supuesto><clave>margen_bruto</clave><valor>0.28</valor><modificado>false</modificado></supuesto><supuesto><clave>distancia_km</clave><valor>2.4</valor><modificado>false</modificado></supuesto><supuesto><clave>paradas_por_viaje</clave><valor>3</valor><modificado>false</modificado></supuesto><supuesto><clave>costo_base_entrega</clave><valor>18</valor><modificado>false</modificado></supuesto><supuesto><clave>costo_km_reparto</clave><valor>4.5</valor><modificado>false</modificado></supuesto></supuestos_usados></costos_unitarios>
```

### COS-07 · El operador consulta costos · PASA

**Objetivo.** Sin costos.ver.

**Petición.** `GET http://costos:5119/api/v1/costos/conceptos`

```http
Accept: application/json
X-Traza-Id: 02e0bda5-ad2f-49fa-8f72-77eed65b101b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 30 ms · traza `02e0bda5-ad2f-49fa-8f72-77eed65b101b`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "02e0bda5-ad2f-49fa-8f72-77eed65b101b"
  }
}
```

### COS-08 · Alta de un concepto sin permiso · PASA

**Objetivo.** Un auditor consulta, no edita.

**Petición.** `POST http://costos:5119/api/v1/costos/conceptos`

```http
Accept: application/json
X-Traza-Id: 2e79228b-04f8-4e03-b810-de2b3adddcfd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{
  "ambito": "microhub",
  "ambito_id": 1,
  "nombre": "Evidencia de vigilancia",
  "categoria": "servicios",
  "tipo": "fijo",
  "unidad": "mes",
  "monto": 1500.0,
  "justificacion": "Concepto creado por la evidencia de la Ola 2"
}
```

**Respuesta.** HTTP 403 (esperado 403) · 28 ms · traza `2e79228b-04f8-4e03-b810-de2b3adddcfd`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "2e79228b-04f8-4e03-b810-de2b3adddcfd"
  }
}
```

### COS-09 · Alta de un concepto · PASA

**Objetivo.** Costo fijo de un microhub con su justificación.

**Petición.** `POST http://costos:5119/api/v1/costos/conceptos`

```http
Accept: application/json
X-Traza-Id: 86f200ec-d907-4f11-9ce9-f2312b3c568e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "ambito": "microhub",
  "ambito_id": 1,
  "nombre": "Evidencia de vigilancia",
  "categoria": "servicios",
  "tipo": "fijo",
  "unidad": "mes",
  "monto": 1500.0,
  "justificacion": "Concepto creado por la evidencia de la Ola 2"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 62 ms · traza `86f200ec-d907-4f11-9ce9-f2312b3c568e`

```json
{
  "id": 63,
  "ambito": "microhub",
  "ambito_id": 1,
  "nombre": "Evidencia de vigilancia",
  "categoria": "servicios",
  "tipo": "fijo",
  "unidad": "mes",
  "monto": 1500.0,
  "vigente_desde": "2026-11-26",
  "vigente_hasta": null,
  "estatus": "activo",
  "fuente": "supuesto",
  "justificacion": "Concepto creado por la evidencia de la Ola 2"
}
```

**Evidencia en PostgreSQL.** `SELECT id, ambito, ambito_id, nombre, tipo, unidad, monto, fuente, creado_por FROM costo_concepto WHERE nombre = 'Evidencia de vigilancia'`

```json
[
  {
    "id": 63,
    "ambito": "microhub",
    "ambito_id": 1,
    "nombre": "Evidencia de vigilancia",
    "tipo": "fijo",
    "unidad": "mes",
    "monto": "1500.00",
    "fuente": "supuesto",
    "creado_por": 5
  }
]
```

**Evidencia en PostgreSQL.** `SELECT accion, entidad, modulo FROM auditoria WHERE entidad = 'costo_concepto' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "accion": "alta",
    "entidad": "costo_concepto",
    "modulo": "costos"
  }
]
```

### COS-10 · Cambiar el monto · PASA

**Objetivo.** Cualquier subconjunto de campos; el ámbito no cambia.

**Petición.** `PUT http://costos:5119/api/v1/costos/conceptos/63`

```http
Accept: application/json
X-Traza-Id: 4f66772c-0109-4d7f-b142-93914bf1e0e2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "monto": 1800.0,
  "justificacion": "Se ajustó el monto en la evidencia"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 138 ms · traza `4f66772c-0109-4d7f-b142-93914bf1e0e2`

```json
{
  "id": 63,
  "ambito": "microhub",
  "ambito_id": 1,
  "nombre": "Evidencia de vigilancia",
  "categoria": "servicios",
  "tipo": "fijo",
  "unidad": "mes",
  "monto": 1800.0,
  "vigente_desde": "2026-11-26",
  "vigente_hasta": null,
  "estatus": "activo",
  "fuente": "supuesto",
  "justificacion": "Se ajustó el monto en la evidencia"
}
```

### COS-16 · Cambiar con PATCH · PASA

**Objetivo.** PATCH es alias de PUT: lo usa la app Android cuando la JVM no admite PUT con cuerpo parcial.

**Petición.** `PATCH http://costos:5119/api/v1/costos/conceptos/63`

```http
Accept: application/json
X-Traza-Id: 631a2184-5d69-49b1-ad90-3755dfe1b65e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "monto": 1900.0,
  "justificacion": "Segundo ajuste del monto en la evidencia"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 108 ms · traza `631a2184-5d69-49b1-ad90-3755dfe1b65e`

```json
{
  "id": 63,
  "ambito": "microhub",
  "ambito_id": 1,
  "nombre": "Evidencia de vigilancia",
  "categoria": "servicios",
  "tipo": "fijo",
  "unidad": "mes",
  "monto": 1900.0,
  "vigente_desde": "2026-11-26",
  "vigente_hasta": null,
  "estatus": "activo",
  "fuente": "supuesto",
  "justificacion": "Segundo ajuste del monto en la evidencia"
}
```

### COS-11 · Dar de baja un concepto · PASA

**Objetivo.** Baja lógica: el renglón se conserva para la historia.

**Petición.** `DELETE http://costos:5119/api/v1/costos/conceptos/63`

```http
Accept: application/json
X-Traza-Id: efb68f43-5fc0-4972-9abc-36215fee8c6e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 35 ms · traza `efb68f43-5fc0-4972-9abc-36215fee8c6e`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT id, estatus FROM costo_concepto WHERE id = %s`

```json
[
  {
    "id": 63,
    "estatus": "inactivo"
  }
]
```

### COS-12 · Fijo con unidad variable · PASA

**Objetivo.** Un costo fijo se da por mes.

**Petición.** `POST http://costos:5119/api/v1/costos/conceptos`

```http
Accept: application/json
X-Traza-Id: 971e8d3f-5c77-4a3f-b513-072d56259fe7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "ambito": "microhub",
  "ambito_id": 1,
  "nombre": "Evidencia inválida",
  "categoria": "servicios",
  "tipo": "fijo",
  "unidad": "pedido",
  "monto": 1500.0,
  "justificacion": "Concepto creado por la evidencia de la Ola 2"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 6 ms · traza `971e8d3f-5c77-4a3f-b513-072d56259fe7`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "unidad",
        "mensaje": "Un costo fijo se da por mes; uno variable, por pedido, entrega, km o porcentaje de la venta."
      }
    ],
    "traza_id": "971e8d3f-5c77-4a3f-b513-072d56259fe7"
  }
}
```

### COS-13 · Microhub inexistente · PASA

**Objetivo.** El ámbito debe existir.

**Petición.** `POST http://costos:5119/api/v1/costos/conceptos`

```http
Accept: application/json
X-Traza-Id: 72fbf54c-34d7-4348-bcaa-8462ddbdc236
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "ambito": "microhub",
  "ambito_id": 99999,
  "nombre": "Evidencia inválida",
  "categoria": "servicios",
  "tipo": "fijo",
  "unidad": "mes",
  "monto": 1500.0,
  "justificacion": "Concepto creado por la evidencia de la Ola 2"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 6 ms · traza `72fbf54c-34d7-4348-bcaa-8462ddbdc236`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "ambito_id",
        "mensaje": "No existe ese microhub."
      }
    ],
    "traza_id": "72fbf54c-34d7-4348-bcaa-8462ddbdc236"
  }
}
```

### COS-14 · Costos de una ubicación candidata · PASA

**Objetivo.** Sin conceptos propios toma renta, nómina y servicios de la ubicación (planeación).

**Petición.** `GET http://costos:5119/api/v1/costos/resumen?candidato_id=3`

```http
Accept: application/json
X-Traza-Id: 434d84b9-bab0-45aa-8f15-514294fc82d8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 68 ms · traza `434d84b9-bab0-45aa-8f15-514294fc82d8`

```json
{
  "ambito": "candidato",
  "ambito_id": 3,
  "origen": "planeacion",
  "conceptos": 8,
  "fijos_mes": 81000.0,
  "por_categoria": [
    {
      "categoria": "otros",
      "monto": 6000.0
    },
    {
      "categoria": "personal",
      "monto": 46000.0
    },
    {
      "categoria": "renta",
      "monto": 21000.0
    },
    {
      "categoria": "servicios",
      "monto": 8000.0
    }
  ],
  "variables": [
    {
      "nombre": "Comisión por pago con tarjeta",
      "unidad": "pct_venta",
      "monto": 2.9
    },
    {
      "nombre": "Empaque por pedido",
      "unidad": "pedido",
      "monto": 3.5
    },
    {
      "nombre": "Combustible y desgaste",
      "unidad": "km",
      "monto": 4.5
    },
    {
      "nombre": "Pago base al repartidor",
      "unidad": "entrega",
      "monto": 18.0
    }
  ],
  "variable_pedido": 3.5,
  "variable_entrega": 18.0,
  "variable_km": 4.5,
  "comision_pct": 2.9
}
```

### COS-15 · Supuestos de los costos · PASA

**Objetivo.** Volumen y ticket de referencia, paradas por viaje y margen por omisión; los montos de cada costo son conceptos con su propia justificación.

**Petición.** `GET http://costos:5119/api/v1/costos/supuestos`

```http
Accept: application/json
X-Traza-Id: 767eba5f-3b34-467f-a9fe-3e2a351696ea
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 32 ms · traza `767eba5f-3b34-467f-a9fe-3e2a351696ea`

```json
{
  "datos": [
    {
      "clave": "********",
      "valor": "2.4",
      "unidad": "km",
      "origen": "supuesto",
      "justificacion": "Distancia típica de entrega desde el microhub, ida solamente; es el valor del Escenario A de la retroalimentación.",
      "como_calibrar": "Distancia promedio entre el microhub y los domicilios de las entregas cerradas."
    },
    {
      "clave": "********",
      "valor": "1800",
      "unidad": "pedidos",
      "origen": "supuesto",
      "justificacion": "Volumen de referencia de 60 pedidos al día para repartir los costos fijos cuando no se indica otro.",
      "como_calibrar": "Pedidos reales por mes del microhub."
    },
    {
      "clave": "********",
      "valor": "135",
      "unidad": "MXN",
      "origen": "supuesto",
      "justificacion": "Ticket de referencia del escenario de la retroalimentación.",
      "como_calibrar": "Ticket promedio real del servicio de demanda."
    },
    {
      "clave": "********",
      "valor": "30",
      "unidad": "días",
      "origen": "normativo",
      "justificacion": "El microhub opera todos los días del mes.",
      "como_calibrar": "Cambiar si se decide cerrar un día a la semana."
    },
    {
      "clave": "********",
      "valor": "0.28",
      "unidad": "fracción",
      "origen": "supuesto",
      "justificacion": "Margen bruto sobre la venta cuando no se conoce el costo del producto. En abarrotes urbanos es de 20 a 35 %.",
      "como_calibrar": "Margen real por producto: servicio de precios, GET /precios/margenes."
    },
    {
      "clave": "********",
      "valor": "3",
      "unidad": "paradas",
      "origen": "supuesto",
      "justificacion": "Paradas promedio de una salida cuando los pedidos se agrupan por zona. Reparte el costo del regreso al microhub entre ellas.",
      "como_calibrar": "Promedio de la columna paradas de plan_ruta."
    }
  ]
}
```

## Servicio punto-equilibrio · puerto 5120

### EQU-01 · El escenario A de la retroalimentación · PASA

**Objetivo.** 45 pedidos al día, ticket 135, margen 28 %, fijos 60,000 y entrega 32.60.

**Petición.** `POST http://punto-equilibrio:5120/api/v1/punto-equilibrio/calculos`

```http
Accept: application/json
X-Traza-Id: 59ab6acd-e99b-4e77-b829-d2aa1f202a99
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "pedidos_dia": 45,
  "ticket": 135,
  "margen_bruto": 0.28,
  "costos_fijos": 60000,
  "costo_variable_pedido": 32.6
}
```

**Respuesta.** HTTP 200 (esperado 200) · 32 ms · traza `59ab6acd-e99b-4e77-b829-d2aa1f202a99`

```json
{
  "id": null,
  "nombre": null,
  "objeto": {
    "tipo": "manual",
    "id": null,
    "nombre": null
  },
  "entrada": {
    "costos_fijos_mes": 60000.0,
    "costo_variable_pedido": 32.6,
    "ticket": 135.0,
    "margen_bruto": 0.28,
    "pedidos_dia": 45.0,
    "dias_mes": 30.0,
    "margen_seguridad_minimo_pct": 15.0,
    "origen": {
      "costos_fijos": "manual",
      "costo_variable_pedido": "manual",
      "ticket": "manual",
      "margen_bruto": "manual",
      "pedidos_dia": "manual"
    }
  },
  "margen_pedido": 5.2,
  "equilibrio_mensual": 11538.46,
  "equilibrio_diario": 384.62,
  "ingresos_equilibrio_mes": 1557692.31,
  "diferencia_pedidos_dia": -339.62,
  "margen_seguridad_pct": -88.3,
  "utilidad_dia": -1766.0,
  "utilidad_mes": -52980.0,
  "decision": "no_viable",
  "explicacion": [
    "la demanda esperada (45.0 pedidos/día) no alcanza el equilibrio (384.6 pedidos/día)"
  ],
  "pasos": [
    "Margen por pedido = ticket × margen bruto − costo de entrega = 135.00 × 28.00% − 32.60 = 5.20",
    "Punto de equilibrio mensual = costos fijos ÷ margen por pedido = 60,000.00 ÷ 5.20 = 11,538 pedidos/mes",
    "Punto de equilibrio diario = 11,538 ÷ 30 días = 384.6 pedidos/día"
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 15.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.28,
      "modificado": false
    }
  ]
}
```

**Explicación.** Margen por pedido = 135 × 28 % − 32.60 = 5.20. Equilibrio mensual = 60,000 ÷ 5.20 = 11,538 pedidos; diario = 384.6, contra 45 esperados: no es viable con estos supuestos. La respuesta trae el cálculo paso a paso.

### EQU-02 · Decisión: viable · PASA

**Objetivo.** Con 70 pedidos al día el equilibrio es 53.3.

**Petición.** `POST http://punto-equilibrio:5120/api/v1/punto-equilibrio/calculos`

```http
Accept: application/json
X-Traza-Id: b8c0ce08-44f1-44d9-82dc-c28a866d5225
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "ticket": 150,
  "margen_bruto": 0.3,
  "costos_fijos": 40000,
  "costo_variable_pedido": 20,
  "pedidos_dia": 70
}
```

**Respuesta.** HTTP 200 (esperado 200) · 29 ms · traza `b8c0ce08-44f1-44d9-82dc-c28a866d5225`

```json
{
  "id": null,
  "nombre": null,
  "objeto": {
    "tipo": "manual",
    "id": null,
    "nombre": null
  },
  "entrada": {
    "costos_fijos_mes": 40000.0,
    "costo_variable_pedido": 20.0,
    "ticket": 150.0,
    "margen_bruto": 0.3,
    "pedidos_dia": 70.0,
    "dias_mes": 30.0,
    "margen_seguridad_minimo_pct": 15.0,
    "origen": {
      "costos_fijos": "manual",
      "costo_variable_pedido": "manual",
      "ticket": "manual",
      "margen_bruto": "manual",
      "pedidos_dia": "manual"
    }
  },
  "margen_pedido": 25.0,
  "equilibrio_mensual": 1600.0,
  "equilibrio_diario": 53.33,
  "ingresos_equilibrio_mes": 240000.0,
  "diferencia_pedidos_dia": 16.67,
  "margen_seguridad_pct": 31.25,
  "utilidad_dia": 416.67,
  "utilidad_mes": 12500.0,
  "decision": "viable",
  "explicacion": [
    "supera el equilibrio por 31.2 % (mínimo 15 %)"
  ],
  "pasos": [
    "Margen por pedido = ticket × margen bruto − costo de entrega = 150.00 × 30.00% − 20.00 = 25.00",
    "Punto de equilibrio mensual = costos fijos ÷ margen por pedido = 40,000.00 ÷ 25.00 = 1,600 pedidos/mes",
    "Punto de equilibrio diario = 1,600 ÷ 30 días = 53.3 pedidos/día"
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 15.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.28,
      "modificado": false
    }
  ]
}
```

### EQU-03 · Decisión: viable_ajustado · PASA

**Objetivo.** Con 55 pedidos al día el equilibrio es 53.3.

**Petición.** `POST http://punto-equilibrio:5120/api/v1/punto-equilibrio/calculos`

```http
Accept: application/json
X-Traza-Id: 305c55a1-dc9b-417e-b43a-1c0744b9a99a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "ticket": 150,
  "margen_bruto": 0.3,
  "costos_fijos": 40000,
  "costo_variable_pedido": 20,
  "pedidos_dia": 55
}
```

**Respuesta.** HTTP 200 (esperado 200) · 29 ms · traza `305c55a1-dc9b-417e-b43a-1c0744b9a99a`

```json
{
  "id": null,
  "nombre": null,
  "objeto": {
    "tipo": "manual",
    "id": null,
    "nombre": null
  },
  "entrada": {
    "costos_fijos_mes": 40000.0,
    "costo_variable_pedido": 20.0,
    "ticket": 150.0,
    "margen_bruto": 0.3,
    "pedidos_dia": 55.0,
    "dias_mes": 30.0,
    "margen_seguridad_minimo_pct": 15.0,
    "origen": {
      "costos_fijos": "manual",
      "costo_variable_pedido": "manual",
      "ticket": "manual",
      "margen_bruto": "manual",
      "pedidos_dia": "manual"
    }
  },
  "margen_pedido": 25.0,
  "equilibrio_mensual": 1600.0,
  "equilibrio_diario": 53.33,
  "ingresos_equilibrio_mes": 240000.0,
  "diferencia_pedidos_dia": 1.67,
  "margen_seguridad_pct": 3.12,
  "utilidad_dia": 41.67,
  "utilidad_mes": 1250.0,
  "decision": "viable_ajustado",
  "explicacion": [
    "supera el equilibrio por 3.1 %, menos del 15 % de margen de seguridad que pide el equipo"
  ],
  "pasos": [
    "Margen por pedido = ticket × margen bruto − costo de entrega = 150.00 × 30.00% − 20.00 = 25.00",
    "Punto de equilibrio mensual = costos fijos ÷ margen por pedido = 40,000.00 ÷ 25.00 = 1,600 pedidos/mes",
    "Punto de equilibrio diario = 1,600 ÷ 30 días = 53.3 pedidos/día"
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 15.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.28,
      "modificado": false
    }
  ]
}
```

### EQU-04 · Decisión: no_viable · PASA

**Objetivo.** Con 40 pedidos al día el equilibrio es 53.3.

**Petición.** `POST http://punto-equilibrio:5120/api/v1/punto-equilibrio/calculos`

```http
Accept: application/json
X-Traza-Id: 6d307c44-9848-4914-86a7-bfc06fd2c332
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "ticket": 150,
  "margen_bruto": 0.3,
  "costos_fijos": 40000,
  "costo_variable_pedido": 20,
  "pedidos_dia": 40
}
```

**Respuesta.** HTTP 200 (esperado 200) · 32 ms · traza `6d307c44-9848-4914-86a7-bfc06fd2c332`

```json
{
  "id": null,
  "nombre": null,
  "objeto": {
    "tipo": "manual",
    "id": null,
    "nombre": null
  },
  "entrada": {
    "costos_fijos_mes": 40000.0,
    "costo_variable_pedido": 20.0,
    "ticket": 150.0,
    "margen_bruto": 0.3,
    "pedidos_dia": 40.0,
    "dias_mes": 30.0,
    "margen_seguridad_minimo_pct": 15.0,
    "origen": {
      "costos_fijos": "manual",
      "costo_variable_pedido": "manual",
      "ticket": "manual",
      "margen_bruto": "manual",
      "pedidos_dia": "manual"
    }
  },
  "margen_pedido": 25.0,
  "equilibrio_mensual": 1600.0,
  "equilibrio_diario": 53.33,
  "ingresos_equilibrio_mes": 240000.0,
  "diferencia_pedidos_dia": -13.33,
  "margen_seguridad_pct": -25.0,
  "utilidad_dia": -333.33,
  "utilidad_mes": -10000.0,
  "decision": "no_viable",
  "explicacion": [
    "la demanda esperada (40.0 pedidos/día) no alcanza el equilibrio (53.3 pedidos/día)"
  ],
  "pasos": [
    "Margen por pedido = ticket × margen bruto − costo de entrega = 150.00 × 30.00% − 20.00 = 25.00",
    "Punto de equilibrio mensual = costos fijos ÷ margen por pedido = 40,000.00 ÷ 25.00 = 1,600 pedidos/mes",
    "Punto de equilibrio diario = 1,600 ÷ 30 días = 53.3 pedidos/día"
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 15.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.28,
      "modificado": false
    }
  ]
}
```

### EQU-05 · Equilibrio de un microhub con sus datos · PASA

**Objetivo.** Costos de costos, ticket y demanda de demanda, personal de cobertura.

**Petición.** `POST http://punto-equilibrio:5120/api/v1/punto-equilibrio/calculos`

```http
Accept: application/json
X-Traza-Id: de11bdc0-76a2-448b-baba-ca08c501cf98
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1
}
```

**Respuesta.** HTTP 200 (esperado 200) · 236 ms · traza `de11bdc0-76a2-448b-baba-ca08c501cf98`

```json
{
  "id": null,
  "nombre": null,
  "objeto": {
    "tipo": "microhub",
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "entrada": {
    "costos_fijos_mes": 69500.0,
    "costo_variable_pedido": 32.61,
    "ticket": 134.83,
    "margen_bruto": 0.28,
    "pedidos_dia": 23.6,
    "dias_mes": 30.0,
    "margen_seguridad_minimo_pct": 15.0,
    "origen": {
      "costos_fijos": "costos",
      "costo_variable_pedido": "costos",
      "ticket": "demanda",
      "margen_bruto": "configuracion",
      "pedidos_dia": "demanda_repartida"
    }
  },
  "margen_pedido": 5.14,
  "equilibrio_mensual": 13515.09,
  "equilibrio_diario": 450.5,
  "ingresos_equilibrio_mes": 1822239.62,
  "diferencia_pedidos_dia": -426.91,
  "margen_seguridad_pct": -94.76,
  "utilidad_dia": -2195.33,
  "utilidad_mes": -65859.95,
  "decision": "no_viable",
  "explicacion": [
    "la demanda esperada (23.6 pedidos/día) no alcanza el equilibrio (450.5 pedidos/día)"
  ],
  "pasos": [
    "Margen por pedido = ticket × margen bruto − costo de entrega = 134.83 × 28.00% − 32.61 = 5.14",
    "Punto de equilibrio mensual = costos fijos ÷ margen por pedido = 69,500.00 ÷ 5.14 = 13,515 pedidos/mes",
    "Punto de equilibrio diario = 13,515 ÷ 30 días = 450.5 pedidos/día"
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 15.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.28,
      "modificado": false
    }
  ]
}
```

**Explicación.** La respuesta dice de dónde salió cada número (costos, demanda, configuración o manual). La demanda de cada zona se reparte entre los microhubs que la cubren.

### EQU-06 · Un dato escrito sustituye al de otro servicio · PASA

**Objetivo.** Con ticket = 200 el origen del ticket es «manual».

**Petición.** `POST http://punto-equilibrio:5120/api/v1/punto-equilibrio/calculos`

```http
Accept: application/json
X-Traza-Id: 827d2e97-068c-4915-b022-a5cd80ca2a04
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "ticket": 200
}
```

**Respuesta.** HTTP 200 (esperado 200) · 289 ms · traza `827d2e97-068c-4915-b022-a5cd80ca2a04`

```json
{
  "id": null,
  "nombre": null,
  "objeto": {
    "tipo": "microhub",
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "entrada": {
    "costos_fijos_mes": 69500.0,
    "costo_variable_pedido": 34.5,
    "ticket": 200.0,
    "margen_bruto": 0.28,
    "pedidos_dia": 23.6,
    "dias_mes": 30.0,
    "margen_seguridad_minimo_pct": 15.0,
    "origen": {
      "costos_fijos": "costos",
      "costo_variable_pedido": "costos",
      "ticket": "manual",
      "margen_bruto": "configuracion",
      "pedidos_dia": "demanda_repartida"
    }
  },
  "margen_pedido": 21.5,
  "equilibrio_mensual": 3232.56,
  "equilibrio_diario": 107.75,
  "ingresos_equilibrio_mes": 646511.63,
  "diferencia_pedidos_dia": -84.16,
  "margen_seguridad_pct": -78.1,
  "utilidad_dia": -1809.37,
  "utilidad_mes": -54281.22,
  "decision": "no_viable",
  "explicacion": [
    "la demanda esperada (23.6 pedidos/día) no alcanza el equilibrio (107.8 pedidos/día)"
  ],
  "pasos": [
    "Margen por pedido = ticket × margen bruto − costo de entrega = 200.00 × 28.00% − 34.50 = 21.50",
    "Punto de equilibrio mensual = costos fijos ÷ margen por pedido = 69,500.00 ÷ 21.50 = 3,233 pedidos/mes",
    "Punto de equilibrio diario = 3,233 ÷ 30 días = 107.8 pedidos/día"
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 15.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.28,
      "modificado": false
    }
  ]
}
```

### EQU-07 · Falta información · PASA

**Objetivo.** Sin microhub ni candidato hay que dar los datos.

**Petición.** `POST http://punto-equilibrio:5120/api/v1/punto-equilibrio/calculos`

```http
Accept: application/json
X-Traza-Id: 025548c2-0cfe-48b4-8613-d2872a7d2b4b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "pedidos_dia": 10
}
```

**Respuesta.** HTTP 422 (esperado 422) · 186 ms · traza `025548c2-0cfe-48b4-8613-d2872a7d2b4b`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "costos_fijos",
        "mensaje": "Sin microhub ni candidato hay que indicar costos_fijos y costo_variable_pedido."
      }
    ],
    "traza_id": "025548c2-0cfe-48b4-8613-d2872a7d2b4b"
  }
}
```

### EQU-08 · Sensibilidad · PASA

**Objetivo.** Cada variable sube y baja 10 y 20 %; se ordenan por lo que mueven la utilidad.

**Petición.** `POST http://punto-equilibrio:5120/api/v1/punto-equilibrio/sensibilidad`

```http
Accept: application/json
X-Traza-Id: 7fc6103d-a8b4-449d-8eb5-e61b02409527
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "ticket": 150,
  "margen_bruto": 0.3,
  "costos_fijos": 40000,
  "costo_variable_pedido": 20,
  "pedidos_dia": 70
}
```

**Respuesta.** HTTP 200 (esperado 200) · 32 ms · traza `7fc6103d-a8b4-449d-8eb5-e61b02409527`

```json
{
  "objeto": {
    "tipo": "manual",
    "id": null,
    "nombre": null
  },
  "entrada": {
    "costos_fijos_mes": 40000.0,
    "costo_variable_pedido": 20.0,
    "ticket": 150.0,
    "margen_bruto": 0.3,
    "pedidos_dia": 70.0,
    "dias_mes": 30.0,
    "margen_seguridad_minimo_pct": 15.0,
    "origen": {
      "costos_fijos": "manual",
      "costo_variable_pedido": "manual",
      "ticket": "manual",
      "margen_bruto": "manual",
      "pedidos_dia": "manual"
    }
  },
  "decision_base": "viable",
  "utilidad_mes_base": 12500.0,
  "equilibrio_diario_base": 53.33,
  "variable_mas_sensible": "Ticket promedio",
  "ranking": [
    {
      "variable": "ticket",
      "etiqueta": "Ticket promedio",
      "rango_utilidad_mes": 37800.0
    },
    {
      "variable": "margen_bruto",
      "etiqueta": "Margen bruto",
      "rango_utilidad_mes": 37800.0
    },
    {
      "variable": "pedidos_dia",
      "etiqueta": "Pedidos por día",
      "rango_utilidad_mes": 21000.0
    },
    {
      "variable": "costo_variable_pedido",
      "etiqueta": "Costo variable por pedido",
      "rango_utilidad_mes": 16800.0
    },
    {
      "variable": "costos_fijos",
      "etiqueta": "Costos fijos del mes",
      "rango_utilidad_mes": 16000.0
    }
  ],
  "filas": [
    {
      "variable": "ticket",
      "etiqueta": "Ticket promedio",
      "cambio_pct": -20,
      "valor": 120.0,
      "equilibrio_diario": 83.33,
      "utilidad_mes": -6400.0,
      "cambio_utilidad": -18900.0,
      "decision": "no_viable"
    },
    {
      "variable": "ticket",
      "etiqueta": "Ticket promedio",
      "cambio_pct": -10,
      "valor": 135.0,
      "equilibrio_diario": 65.04,
      "utilidad_mes": 3050.0,
      "cambio_utilidad": -9450.0,
      "decision": "viable_ajustado"
    },
    {
      "variable": "ticket",
      "etiqueta": "Ticket promedio",
      "cambio_pct": 10,
      "valor": 165.0,
      "equilibrio_diario": 45.2,
      "utilidad_mes": 21950.0,
      "cambio_utilidad": 9450.0,
      "decision": "viable"
    },
    {
      "variable": "ticket",
      "etiqueta": "Ticket promedio",
      "cambio_pct": 20,
      "valor": 180.0,
      "equilibrio_diario": 39.22,
      "utilidad_mes": 31400.0,
      "cambio_utilidad": 18900.0,
      "decision": "viable"
    },
    {
      "variable": "pedidos_dia",
      "etiqueta": "Pedidos por día",
      "cambio_pct": -20,
      "valor": 56.0,
      "equilibrio_diario": 53.33,
      "utilidad_mes": 2000.0,
      "cambio_utilidad": -10500.0,
      "decision": "viable_ajustado"
    },
    {
      "variable": "pedidos_dia",
      "etiqueta": "Pedidos por día",
      "cambio_pct": -10,
      "valor": 63.0,
      "equilibrio_diario": 53.33,
      "utilidad_mes": 7250.0,
      "cambio_utilidad": -5250.0,
      "decision": "viable"
    },
    {
      "variable": "pedidos_dia",
      "etiqueta": "Pedidos por día",
      "cambio_pct": 10,
      "valor": 77.0,
      "equilibrio_diario": 53.33,
      "utilidad_mes": 17750.0,
      "cambio_utilidad": 5250.0,
      "decision": "viable"
    },
    {
      "variable": "pedidos_dia",
      "etiqueta": "Pedidos por día",
      "cambio_pct": 20,
      "valor": 84.0,
      "equilibrio_diario": 53.33,
      "utilidad_mes": 23000.0,
      "cambio_utilidad": 10500.0,
      "decision": "viable"
    },
    {
      "variable": "costos_fijos",
      "etiqueta": "Costos fijos del mes",
      "cambio_pct": -20,
      "valor": 32000.0,
      "equilibrio_diario": 42.67,
      "utilidad_mes": 20500.0,
      "cambio_utilidad": 8000.0,
      "decision": "viable"
    },
    {
      "variable": "costos_fijos",
      "etiqueta": "Costos fijos del mes",
      "cambio_pct": -10,
      "valor": 36000.0,
      "equilibrio_diario": 48.0,
      "utilidad_mes": 16500.0,
      "cambio_utilidad": 4000.0,
      "decision": "viable"
    },
    {
      "variable": "costos_fijos",
      "etiqueta": "Costos fijos del mes",
      "cambio_pct": 10,
      "valor": 44000.0,
      "equilibrio_diario": 58.67,
      "utilidad_mes": 8500.0,
      "cambio_utilidad": -4000.0,
      "decision": "viable"
    },
    {
      "variable": "costos_fijos",
      "etiqueta": "Costos fijos del mes",
      "cambio_pct": 20,
      "valor": 48000.0,
      "equilibrio_diario": 64.0,
      "utilidad_mes": 4500.0,
      "cambio_utilidad": -8000.0,
      "decision": "viable_ajustado"
    },
    {
      "variable": "costo_variable_pedido",
      "etiqueta": "Costo variable por pedido",
      "cambio_pct": -20,
      "valor": 16.0,
      "equilibrio_diario": 45.98,
      "utilidad_mes": 20900.0,
      "cambio_utilidad": 8400.0,
      "decision": "viable"
    },
    {
      "variable": "costo_variable_pedido",
      "etiqueta": "Costo variable por pedido",
      "cambio_pct": -10,
      "valor": 18.0,
      "equilibrio_diario": 49.38,
      "utilidad_mes": 16700.0,
      "cambio_utilidad": 4200.0,
      "decision": "viable"
    },
    {
      "variable": "costo_variable_pedido",
      "etiqueta": "Costo variable por pedido",
      "cambio_pct": 10,
      "valor": 22.0,
      "equilibrio_diario": 57.97,
      "utilidad_mes": 8300.0,
      "cambio_utilidad": -4200.0,
      "decision": "viable"
    },
    {
      "variable": "costo_variable_pedido",
      "etiqueta": "Costo variable por pedido",
      "cambio_pct": 20,
      "valor": 24.0,
      "equilibrio_diario": 63.49,
      "utilidad_mes": 4100.0,
      "cambio_utilidad": -8400.0,
      "decision": "viable_ajustado"
    },
    {
      "variable": "margen_bruto",
      "etiqueta": "Margen bruto",
      "cambio_pct": -20,
      "valor": 0.24,
      "equilibrio_diario": 83.33,
      "utilidad_mes": -6400.0,
      "cambio_utilidad": -18900.0,
      "decision": "no_viable"
    },
    {
      "variable": "margen_bruto",
      "etiqueta": "Margen bruto",
      "cambio_pct": -10,
      "valor": 0.27,
      "equilibrio_diario": 65.04,
      "utilidad_mes": 3050.0,
      "cambio_utilidad": -9450.0,
      "decision": "viable_ajustado"
    },
    {
      "variable": "margen_bruto",
      "etiqueta": "Margen bruto",
      "cambio_pct": 10,
      "valor": 0.33,
      "equilibrio_diario": 45.2,
      "utilidad_mes": 21950.0,
      "cambio_utilidad": 9450.0,
      "decision": "viable"
    },
    {
      "variable": "margen_bruto",
      "etiqueta": "Margen bruto",
      "cambio_pct": 20,
      "valor": 0.36,
      "equilibrio_diario": 39.22,
      "utilidad_mes": 31400.0,
      "cambio_utilidad": 18900.0,
      "decision": "viable"
    }
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 15.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    }
  ]
}
```

### EQU-09 · Equilibrio (XML) · PASA

**Objetivo.** Entrada y salida en XML, validadas contra punto_equilibrio.xsd.

**Petición.** `POST http://punto-equilibrio:5120/api/v1/punto-equilibrio/calculos`

```http
Accept: application/xml
X-Traza-Id: 4f58e2b4-3a8f-4d62-828b-2c3006a09340
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><equilibrio_calculo_nuevo xmlns="urn:microhubs:v1"><pedidos_dia>45</pedidos_dia><ticket>135</ticket><margen_bruto>0.28</margen_bruto><costos_fijos>60000</costos_fijos><costo_variable_pedido>32.6</costo_variable_pedido></equilibrio_calculo_nuevo>
```

**Respuesta.** HTTP 200 (esperado 200) · 31 ms · traza `4f58e2b4-3a8f-4d62-828b-2c3006a09340`

```xml
<?xml version='1.0' encoding='utf-8'?>
<equilibrio_calculo xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id xsi:nil="true" /><nombre xsi:nil="true" /><objeto><tipo>manual</tipo><id xsi:nil="true" /><nombre xsi:nil="true" /></objeto><entrada><costos_fijos_mes>60000</costos_fijos_mes><costo_variable_pedido>32.6</costo_variable_pedido><ticket>135</ticket><margen_bruto>0.28</margen_bruto><pedidos_dia>45</pedidos_dia><dias_mes>30</dias_mes><margen_seguridad_minimo_pct>15</margen_seguridad_minimo_pct><origen><costos_fijos>manual</costos_fijos><costo_variable_pedido>manual</costo_variable_pedido><ticket>manual</ticket><margen_bruto>manual</margen_bruto><pedidos_dia>manual</pedidos_dia></origen></entrada><margen_pedido>5.2</margen_pedido><equilibrio_mensual>11538.46</equilibrio_mensual><equilibrio_diario>384.62</equilibrio_diario><ingresos_equilibrio_mes>1557692.31</ingresos_equilibrio_mes><diferencia_pedidos_dia>-339.62</diferencia_pedidos_dia><margen_seguridad_pct>-88.3</margen_seguridad_pct><utilidad_dia>-1766</utilidad_dia><utilidad_mes>-52980</utilidad_mes><decision>no_viable</decision><explicacion><motivo>la demanda esperada (45.0 pedidos/día) no alcanza el equilibrio (384.6 pedidos/día)</motivo></explicacion><pasos><paso>Margen por pedido = ticket × margen bruto − costo de entrega = 135.00 × 28.00% − 32.60 = 5.20</paso><paso>Punto de equilibrio mensual = costos fijos ÷ margen por pedido = 60,000.00 ÷ 5.20 = 11,538 pedidos/mes</paso><paso>Punto de equilibrio diario = 11,538 ÷ 30 días = 384.6 pedidos/día</paso></pasos><supuestos_usados><supuesto><clave>peq_margen_seguridad_pct</clave><valor>15</valor><modificado>false</modificado></supuesto><supuesto><clave>dias_operacion_mes</clave><valor>30</valor><modificado>false</modificado></supuesto><supuesto><clave>margen_bruto_default</clave><valor>0.28</valor><modificado>false</modificado></supuesto></supuestos_usados></equilibrio_calculo>
```

### EQU-10 · Guardar sin permiso · PASA

**Objetivo.** Guardar un escenario exige equilibrio.editar.

**Petición.** `POST http://punto-equilibrio:5120/api/v1/punto-equilibrio/calculos`

```http
Accept: application/json
X-Traza-Id: edbcdca7-6125-43ee-a661-1cd94c426b99
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{
  "pedidos_dia": 45,
  "ticket": 135,
  "margen_bruto": 0.28,
  "costos_fijos": 60000,
  "costo_variable_pedido": 32.6,
  "guardar": true
}
```

**Respuesta.** HTTP 403 (esperado 403) · 7 ms · traza `edbcdca7-6125-43ee-a661-1cd94c426b99`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Guardar un escenario exige el permiso equilibrio.editar.",
    "traza_id": "edbcdca7-6125-43ee-a661-1cd94c426b99"
  }
}
```

### EQU-11 · Guardar «Evidencia equilibrio A» · PASA

**Objetivo.** Queda en equilibrio_escenario con su cálculo completo.

**Petición.** `POST http://punto-equilibrio:5120/api/v1/punto-equilibrio/calculos`

```http
Accept: application/json
X-Traza-Id: a920622c-e060-4112-8754-cd20d2b6f630
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "ticket": 150,
  "margen_bruto": 0.3,
  "costos_fijos": 40000,
  "costo_variable_pedido": 20,
  "pedidos_dia": 45,
  "guardar": true,
  "nombre": "Evidencia equilibrio A"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 59 ms · traza `a920622c-e060-4112-8754-cd20d2b6f630`

```json
{
  "id": 42,
  "nombre": "Evidencia equilibrio A",
  "objeto": {
    "tipo": "manual",
    "id": null,
    "nombre": null
  },
  "entrada": {
    "costos_fijos_mes": 40000.0,
    "costo_variable_pedido": 20.0,
    "ticket": 150.0,
    "margen_bruto": 0.3,
    "pedidos_dia": 45.0,
    "dias_mes": 30.0,
    "margen_seguridad_minimo_pct": 15.0,
    "origen": {
      "costos_fijos": "manual",
      "costo_variable_pedido": "manual",
      "ticket": "manual",
      "margen_bruto": "manual",
      "pedidos_dia": "manual"
    }
  },
  "margen_pedido": 25.0,
  "equilibrio_mensual": 1600.0,
  "equilibrio_diario": 53.33,
  "ingresos_equilibrio_mes": 240000.0,
  "diferencia_pedidos_dia": -8.33,
  "margen_seguridad_pct": -15.62,
  "utilidad_dia": -208.33,
  "utilidad_mes": -6250.0,
  "decision": "no_viable",
  "explicacion": [
    "la demanda esperada (45.0 pedidos/día) no alcanza el equilibrio (53.3 pedidos/día)"
  ],
  "pasos": [
    "Margen por pedido = ticket × margen bruto − costo de entrega = 150.00 × 30.00% − 20.00 = 25.00",
    "Punto de equilibrio mensual = costos fijos ÷ margen por pedido = 40,000.00 ÷ 25.00 = 1,600 pedidos/mes",
    "Punto de equilibrio diario = 1,600 ÷ 30 días = 53.3 pedidos/día"
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 15.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.28,
      "modificado": false
    }
  ]
}
```

**Evidencia en PostgreSQL.** `SELECT id, nombre, microhub_id, candidato_id, creado_por FROM equilibrio_escenario WHERE nombre = %s`

```json
[
  {
    "id": 42,
    "nombre": "Evidencia equilibrio A",
    "microhub_id": null,
    "candidato_id": null,
    "creado_por": 5
  }
]
```

### EQU-12 · Guardar «Evidencia equilibrio B» · PASA

**Objetivo.** Queda en equilibrio_escenario con su cálculo completo.

**Petición.** `POST http://punto-equilibrio:5120/api/v1/punto-equilibrio/calculos`

```http
Accept: application/json
X-Traza-Id: 998df549-6c6a-4baf-9120-00922c6d9efe
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "ticket": 150,
  "margen_bruto": 0.3,
  "costos_fijos": 40000,
  "costo_variable_pedido": 20,
  "pedidos_dia": 80,
  "guardar": true,
  "nombre": "Evidencia equilibrio B"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 74 ms · traza `998df549-6c6a-4baf-9120-00922c6d9efe`

```json
{
  "id": 43,
  "nombre": "Evidencia equilibrio B",
  "objeto": {
    "tipo": "manual",
    "id": null,
    "nombre": null
  },
  "entrada": {
    "costos_fijos_mes": 40000.0,
    "costo_variable_pedido": 20.0,
    "ticket": 150.0,
    "margen_bruto": 0.3,
    "pedidos_dia": 80.0,
    "dias_mes": 30.0,
    "margen_seguridad_minimo_pct": 15.0,
    "origen": {
      "costos_fijos": "manual",
      "costo_variable_pedido": "manual",
      "ticket": "manual",
      "margen_bruto": "manual",
      "pedidos_dia": "manual"
    }
  },
  "margen_pedido": 25.0,
  "equilibrio_mensual": 1600.0,
  "equilibrio_diario": 53.33,
  "ingresos_equilibrio_mes": 240000.0,
  "diferencia_pedidos_dia": 26.67,
  "margen_seguridad_pct": 50.0,
  "utilidad_dia": 666.67,
  "utilidad_mes": 20000.0,
  "decision": "viable",
  "explicacion": [
    "supera el equilibrio por 50.0 % (mínimo 15 %)"
  ],
  "pasos": [
    "Margen por pedido = ticket × margen bruto − costo de entrega = 150.00 × 30.00% − 20.00 = 25.00",
    "Punto de equilibrio mensual = costos fijos ÷ margen por pedido = 40,000.00 ÷ 25.00 = 1,600 pedidos/mes",
    "Punto de equilibrio diario = 1,600 ÷ 30 días = 53.3 pedidos/día"
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 15.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.28,
      "modificado": false
    }
  ]
}
```

**Evidencia en PostgreSQL.** `SELECT id, nombre, microhub_id, candidato_id, creado_por FROM equilibrio_escenario WHERE nombre = %s`

```json
[
  {
    "id": 43,
    "nombre": "Evidencia equilibrio B",
    "microhub_id": null,
    "candidato_id": null,
    "creado_por": 5
  }
]
```

### EQU-13 · Escenarios guardados · PASA

**Objetivo.** Abrir la lista de escenarios.

**Petición.** `GET http://punto-equilibrio:5120/api/v1/punto-equilibrio/escenarios?por_pagina=100`

```http
Accept: application/json
X-Traza-Id: 5ace7f56-c072-4d52-b85d-a619837cd6dc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 74 ms · traza `5ace7f56-c072-4d52-b85d-a619837cd6dc`

```json
{
  "datos": [
    {
      "id": 43,
      "nombre": "Evidencia equilibrio B",
      "microhub_id": null,
      "candidato_id": null,
      "decision": "viable",
      "equilibrio_diario": 53.33,
      "pedidos_dia": 80.0,
      "utilidad_mes": 20000.0,
      "creado_por": 5,
      "creado_en": "2026-11-26T14:19:56-06:00"
    },
    {
      "id": 42,
      "nombre": "Evidencia equilibrio A",
      "microhub_id": null,
      "candidato_id": null,
      "decision": "no_viable",
      "equilibrio_diario": 53.33,
      "pedidos_dia": 45.0,
      "utilidad_mes": -6250.0,
      "creado_por": 5,
      "creado_en": "2026-11-26T14:19:56-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 100,
    "total": 2,
    "paginas": 1
  }
}
```

### EQU-14 · Comparar escenarios · PASA

**Objetivo.** Lado a lado: decisión, equilibrio, diferencia y utilidad.

**Petición.** `GET http://punto-equilibrio:5120/api/v1/punto-equilibrio/comparacion?ids=42,43`

```http
Accept: application/json
X-Traza-Id: a2b1e161-d4e5-4b26-86c0-4baa08c098a6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 83 ms · traza `a2b1e161-d4e5-4b26-86c0-4baa08c098a6`

```json
{
  "filas": [
    {
      "id": 42,
      "nombre": "Evidencia equilibrio A",
      "decision": "no_viable",
      "pedidos_dia": 45.0,
      "equilibrio_diario": 53.33,
      "diferencia_pedidos_dia": -8.33,
      "margen_seguridad_pct": -15.62,
      "utilidad_mes": -6250.0
    },
    {
      "id": 43,
      "nombre": "Evidencia equilibrio B",
      "decision": "viable",
      "pedidos_dia": 80.0,
      "equilibrio_diario": 53.33,
      "diferencia_pedidos_dia": 26.67,
      "margen_seguridad_pct": 50.0,
      "utilidad_mes": 20000.0
    }
  ],
  "mejor_utilidad_id": 43,
  "mejor_utilidad_nombre": "Evidencia equilibrio B"
}
```

### EQU-15 · Abrir un escenario · PASA

**Objetivo.** Con su cálculo paso a paso.

**Petición.** `GET http://punto-equilibrio:5120/api/v1/punto-equilibrio/escenarios/42`

```http
Accept: application/json
X-Traza-Id: 0fe09f4f-824f-4bb6-84ac-ea5b9721cc43
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 45 ms · traza `0fe09f4f-824f-4bb6-84ac-ea5b9721cc43`

```json
{
  "id": 42,
  "nombre": "Evidencia equilibrio A",
  "objeto": {
    "tipo": "manual",
    "id": null,
    "nombre": null
  },
  "entrada": {
    "costos_fijos_mes": 40000.0,
    "costo_variable_pedido": 20.0,
    "ticket": 150.0,
    "margen_bruto": 0.3,
    "pedidos_dia": 45.0,
    "dias_mes": 30.0,
    "margen_seguridad_minimo_pct": 15.0,
    "origen": {
      "costos_fijos": "manual",
      "costo_variable_pedido": "manual",
      "ticket": "manual",
      "margen_bruto": "manual",
      "pedidos_dia": "manual"
    }
  },
  "margen_pedido": 25.0,
  "equilibrio_mensual": 1600.0,
  "equilibrio_diario": 53.33,
  "ingresos_equilibrio_mes": 240000.0,
  "diferencia_pedidos_dia": -8.33,
  "margen_seguridad_pct": -15.62,
  "utilidad_dia": -208.33,
  "utilidad_mes": -6250.0,
  "decision": "no_viable",
  "explicacion": [
    "la demanda esperada (45.0 pedidos/día) no alcanza el equilibrio (53.3 pedidos/día)"
  ],
  "pasos": [
    "Margen por pedido = ticket × margen bruto − costo de entrega = 150.00 × 30.00% − 20.00 = 25.00",
    "Punto de equilibrio mensual = costos fijos ÷ margen por pedido = 40,000.00 ÷ 25.00 = 1,600 pedidos/mes",
    "Punto de equilibrio diario = 1,600 ÷ 30 días = 53.3 pedidos/día"
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 15.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.28,
      "modificado": false
    }
  ]
}
```

### EQU-16 · Borrar sin permiso · PASA

**Objetivo.** Borrar es de equilibrio.editar.

**Petición.** `DELETE http://punto-equilibrio:5120/api/v1/punto-equilibrio/escenarios/42`

```http
Accept: application/json
X-Traza-Id: d1416b77-333b-44b3-b664-35ae5fdba012
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 38 ms · traza `d1416b77-333b-44b3-b664-35ae5fdba012`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "d1416b77-333b-44b3-b664-35ae5fdba012"
  }
}
```

### EQU-17 · Borrar un escenario · PASA

**Objetivo.** Se elimina el escenario.

**Petición.** `DELETE http://punto-equilibrio:5120/api/v1/punto-equilibrio/escenarios/42`

```http
Accept: application/json
X-Traza-Id: a951567f-d711-4824-b1c1-b187f58ff0b7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 50 ms · traza `a951567f-d711-4824-b1c1-b187f58ff0b7`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT count(*) AS quedan FROM equilibrio_escenario WHERE id = %s`

```json
[
  {
    "quedan": 0
  }
]
```

### EQU-18 · Equilibrio de todos los microhubs · PASA

**Objetivo.** Una fila por microhub activo con sus datos reales.

**Petición.** `GET http://punto-equilibrio:5120/api/v1/punto-equilibrio/microhubs`

```http
Accept: application/json
X-Traza-Id: c6823a79-5d62-4124-aea9-7e8fe9566f0f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 564 ms · traza `c6823a79-5d62-4124-aea9-7e8fe9566f0f`

```json
{
  "datos": [
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "costos_fijos_mes": 69500.0,
      "margen_pedido": 5.14,
      "equilibrio_diario": 450.5,
      "pedidos_dia": 23.6,
      "diferencia_pedidos_dia": -426.91,
      "utilidad_mes": -65859.95,
      "decision": "no_viable"
    },
    {
      "microhub": {
        "id": 2,
        "nombre": "Microhub Valles"
      },
      "costos_fijos_mes": 66500.0,
      "margen_pedido": 5.14,
      "equilibrio_diario": 431.06,
      "pedidos_dia": 16.11,
      "diferencia_pedidos_dia": -414.95,
      "utilidad_mes": -64014.68,
      "decision": "no_viable"
    },
    {
      "microhub": {
        "id": 3,
        "nombre": "Microhub Poniente F-113"
      },
      "costos_fijos_mes": 50000.0,
      "margen_pedido": 5.14,
      "equilibrio_diario": 324.1,
      "pedidos_dia": 9.79,
      "diferencia_pedidos_dia": -314.31,
      "utilidad_mes": -48488.91,
      "decision": "no_viable"
    }
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 15.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    }
  ]
}
```

### EQU-19 · Supuestos del equilibrio · PASA

**Objetivo.** Margen de seguridad mínimo y margen bruto por omisión.

**Petición.** `GET http://punto-equilibrio:5120/api/v1/punto-equilibrio/supuestos`

```http
Accept: application/json
X-Traza-Id: 3a5292bd-c778-4411-b4dd-23b6c7abdb58
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 33 ms · traza `3a5292bd-c778-4411-b4dd-23b6c7abdb58`

```json
{
  "datos": [
    {
      "clave": "********",
      "valor": "135",
      "unidad": "MXN",
      "origen": "supuesto",
      "justificacion": "Ticket de referencia del escenario de la retroalimentación.",
      "como_calibrar": "Ticket promedio real del servicio de demanda."
    },
    {
      "clave": "********",
      "valor": "30",
      "unidad": "días",
      "origen": "normativo",
      "justificacion": "El microhub opera todos los días del mes.",
      "como_calibrar": "Cambiar si se decide cerrar un día a la semana."
    },
    {
      "clave": "********",
      "valor": "0.28",
      "unidad": "fracción",
      "origen": "supuesto",
      "justificacion": "Margen bruto sobre la venta cuando no se conoce el costo del producto. En abarrotes urbanos es de 20 a 35 %.",
      "como_calibrar": "Margen real por producto: servicio de precios, GET /precios/margenes."
    },
    {
      "clave": "********",
      "valor": "15",
      "unidad": "%",
      "origen": "normativo",
      "justificacion": "Decisión del equipo: un microhub es viable si la demanda esp…(144 caracteres)",
      "como_calibrar": "Variación diaria de la demanda observada."
    }
  ]
}
```

## Servicio surtido · puerto 5122

### SUR-01 · Clasificación ABC · PASA

**Objetivo.** A hasta 80 % acumulado de unidades, B hasta 95 %, C el resto.

**Petición.** `GET http://surtido:5122/api/v1/surtido/abc?microhub_id=1`

```http
Accept: application/json
X-Traza-Id: 24322252-c54c-474b-9882-f110e04a661d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 342 ms · traza `24322252-c54c-474b-9882-f110e04a661d`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "ventana_dias": 90,
  "clases": [
    {
      "clase": "A",
      "productos": 32,
      "unidades": 330,
      "venta": 9584.6,
      "pct_unidades": 80.1,
      "pct_venta": 78.8
    },
    {
      "clase": "B",
      "productos": 13,
      "unidades": 65,
      "venta": 1975.5,
      "pct_unidades": 15.8,
      "pct_venta": 16.2
    },
    {
      "clase": "C",
      "productos": 6,
      "unidades": 17,
      "venta": 607.0,
      "pct_unidades": 4.1,
      "pct_venta": 5.0
    }
  ],
  "filas": [
    {
      "producto": {
        "id": 28,
        "clave_interna": "BE-008",
        "nombre": "Polvo para agua de sabor"
      },
      "clase": "A",
      "unidades": 22,
      "venta": 165.0,
      "pct_acum": 5.3
    },
    {
      "producto": {
        "id": 45,
        "clave_interna": "LI-009",
        "nombre": "Fibra para trastes"
      },
      "clase": "A",
      "unidades": 16,
      "venta": 288.0,
      "pct_acum": 9.2
    },
    {
      "producto": {
        "id": 7,
        "clave_interna": "AB-007",
        "nombre": "Harina de trigo"
      },
      "clase": "A",
      "unidades": 15,
      "venta": 367.5,
      "pct_acum": 12.9
    },
    {
      "producto": {
        "id": 25,
        "clave_interna": "BE-005",
        "nombre": "Jugo de naranja"
      },
      "clase": "A",
      "unidades": 15,
      "venta": 420.0,
      "pct_acum": 16.5
    },
    {
      "producto": {
        "id": 48,
        "clave_interna": "HI-003",
        "nombre": "Pasta dental"
      },
      "clase": "A",
      "unidades": 15,
      "venta": 480.0,
      "pct_acum": 20.1
    },
    {
      "producto": {
        "id": 13,
        "clave_interna": "AB-013",
        "nombre": "Puré de tomate"
      },
      "clase": "A",
      "unidades": 14,
      "venta": 154.0,
      "pct_acum": 23.5
    },
    {
      "producto": {
        "id": 20,
        "clave_interna": "AB-020",
        "nombre": "Lenteja"
      },
      "clase": "A",
      "unidades": 13,
      "venta": 312.0,
      "pct_acum": 26.7
    },
    {
      "producto": {
        "id": 36,
        "clave_interna": "LA-008",
        "nombre": "Jamón de pavo"
      },
      "clase": "A",
      "unidades": 13,
      "venta": 598.0,
      "pct_acum": 29.9
    },
    {
      "producto": {
        "id": 30,
        "clave_interna": "LA-002",
        "nombre": "Leche deslactosada"
      },
      "clase": "A",
      "unidades": 12,
      "venta": 372.0,
      "pct_acum": 32.8
    },
    {
      "producto": {
        "id": 34,
        "clave_interna": "LA-006",
        "nombre": "Yogur natural"
      },
      "clase": "A",
      "unidades": 12,
      "venta": 528.0,
      "pct_acum": 35.7
    },
    {
      "producto": {
        "id": 42,
        "clave_interna": "LI-006",
        "nombre": "Papel higiénico"
      },
      "clase": "A",
      "unidades": 12,
      "venta": 456.0,
      "pct_acum": 38.6
    },
    {
      "producto": {
        "id": 39,
        "clave_interna": "LI-003",
        "nombre": "Cloro"
      },
      "clase": "A",
      "unidades": 11,
      "venta": 214.5,
      "pct_acum": 41.3
    },
    {
      "producto": {
        "id": 43,
        "clave_interna": "LI-007",
        "nombre": "Servilletas"
      },
      "clase": "A",
      "unidades": 10,
      "venta": 320.0,
      "pct_acum": 43.7
    },
    {
      "producto": {
        "id": 2,
        "clave_interna": "AB-002",
        "nombre": "Arroz superextra"
      },
      "clase": "A",
      "unidades": 9,
      "venta": 269.1,
      "pct_acum": 45.9
    },
    {
      "producto": {
        "id": 11,
        "clave_interna": "AB-011",
        "nombre": "Frijoles refritos"
      },
      "clase": "A",
      "unidades": 9,
      "venta": 207.0,
      "pct_acum": 48.1
    },
    {
      "producto": {
        "id": 12,
        "clave_interna": "AB-012",
        "nombre": "Chiles jalapeños en escabeche"
      },
      "clase": "A",
      "unidades": 9,
      "venta": 175.5,
      "pct_acum": 50.2
    },
    {
      "producto": {
        "id": 19,
        "clave_interna": "AB-019",
        "nombre": "Huevo blanco"
      },
      "clase": "A",
      "unidades": 9,
      "venta": 378.0,
      "pct_acum": 52.4
    },
    {
      "producto": {
        "id": 44,
        "clave_interna": "LI-008",
        "nombre": "Bolsas para basura"
      },
      "clase": "A",
      "unidades": 9,
      "venta": 216.0,
      "pct_acum": 54.6
    },
    {
      "producto": {
        "id": 1,
        "clave_interna": "AB-001",
        "nombre": "Frijol negro a granel"
      },
      "clase": "A",
      "unidades": 8,
      "venta": 308.0,
      "pct_acum": 56.6
    },
    {
      "producto": {
        "id": 6,
        "clave_interna": "AB-006",
        "nombre": "Harina de maíz nixtamalizado"
      },
      "clase": "A",
      "unidades": 8,
      "venta": 208.0,
      "pct_acum": 58.5
    },
    {
      "producto": {
        "id": 24,
        "clave_interna": "BE-004",
        "nombre": "Refresco sabor manzana"
      },
      "clase": "A",
      "unidades": 8,
      "venta": 288.0,
      "pct_acum": 60.4
    },
    {
      "producto": {
        "id": 27,
        "clave_interna": "BE-007",
        "nombre": "Té helado de limón"
      },
      "clase": "A",
      "unidades": 8,
      "venta": 136.0,
      "pct_acum": 62.4
    },
    {
      "producto": {
        "id": 29,
        "clave_interna": "LA-001",
        "nombre": "Leche entera"
      },
      "clase": "A",
      "unidades": 8,
      "venta": 220.0,
      "pct_acum": 64.3
    },
    {
      "producto": {
        "id": 40,
        "clave_interna": "LI-004",
        "nombre": "Limpiador multiusos"
      },
      "clase": "A",
      "unidades": 8,
      "venta": 224.0,
      "pct_acum": 66.3
    },
    {
      "producto": {
        "id": 51,
        "clave_interna": "HI-006",
        "nombre": "Pañal etapa 3"
      },
      "clase": "A",
      "unidades": 8,
      "venta": 544.0,
      "pct_acum": 68.2
    },
    {
      "producto": {
        "id": 5,
        "clave_interna": "AB-005",
        "nombre": "Sal de mesa"
      },
      "clase": "A",
      "unidades": 7,
      "venta": 98.0,
      "pct_acum": 69.9
    },
    {
      "producto": {
        "id": 8,
        "clave_interna": "AB-008",
        "nombre": "Pasta para sopa surtida"
      },
      "clase": "A",
      "unidades": 7,
      "venta": 66.5,
      "pct_acum": 71.6
    },
    {
      "producto": {
        "id": 10,
        "clave_interna": "AB-010",
        "nombre": "Sardina en salsa de tomate"
      },
      "clase": "A",
      "unidades": 7,
      "venta": 185.5,
      "pct_acum": 73.3
    },
    {
      "producto": {
        "id": 14,
        "clave_interna": "AB-014",
        "nombre": "Café soluble"
      },
      "clase": "A",
      "unidades": 7,
      "venta": 364.0,
      "pct_acum": 75.0
    },
    {
      "producto": {
        "id": 18,
        "clave_interna": "AB-018",
        "nombre": "Pan de caja blanco"
      },
      "clase": "A",
      "unidades": 7,
      "venta": 308.0,
      "pct_acum": 76.7
    },
    {
      "producto": {
        "id": 47,
        "clave_interna": "HI-002",
        "nombre": "Shampoo"
      },
      "clase": "A",
      "unidades": 7,
      "venta": 378.0,
      "pct_acum": 78.4
    },
    {
      "producto": {
        "id": 49,
        "clave_interna": "HI-004",
        "nombre": "Desodorante"
      },
      "clase": "A",
      "unidades": 7,
      "venta": 336.0,
      "pct_acum": 80.1
    },
    {
      "producto": {
        "id": 3,
        "clave_interna": "AB-003",
        "nombre": "Aceite vegetal"
      },
      "clase": "B",
      "unidades": 6,
      "venta": 252.0,
      "pct_acum": 81.6
    },
    {
      "producto": {
        "id": 17,
        "clave_interna": "AB-017",
        "nombre": "Tortillas de maíz"
      },
      "clase": "B",
      "unidades": 6,
      "venta": 144.0,
      "pct_acum": 83.0
    },
    {
      "producto": {
        "id": 26,
        "clave_interna": "BE-006",
        "nombre": "Bebida de soya"
      },
      "clase": "B",
      "unidades": 6,
      "venta": 192.0,
      "pct_acum": 84.5
    },
    {
      "producto": {
        "id": 16,
        "clave_interna": "AB-016",
        "nombre": "Galletas María"
      },
      "clase": "B",
      "unidades": 5,
      "venta": 82.5,
      "pct_acum": 85.7
    },
    {
      "producto": {
        "id": 22,
        "clave_interna": "BE-002",
        "nombre": "Agua embotellada"
      },
      "clase": "B",
      "unidades": 5,
      "venta": 75.0,
      "pct_acum": 86.9
    },
    {
      "producto": {
        "id": 23,
        "clave_interna": "BE-003",
        "nombre": "Refresco de cola"
      },
      "clase": "B",
      "unidades": 5,
      "venta": 192.5,
      "pct_acum": 88.1
    },
    {
      "producto": {
        "id": 35,
        "clave_interna": "LA-007",
        "nombre": "Mantequilla"
      },
      "clase": "B",
      "unidades": 5,
      "venta": 110.0,
      "pct_acum": 89.3
    },
    {
      "producto": {
        "id": 41,
        "clave_interna": "LI-005",
        "nombre": "Suavizante de telas"
      },
      "clase": "B",
      "unidades": 5,
      "venta": 165.0,
      "pct_acum": 90.5
    },
    {
      "producto": {
        "id": 46,
        "clave_interna": "HI-001",
        "nombre": "Jabón de tocador"
      },
      "clase": "B",
      "unidades": 5,
      "venta": 72.5,
      "pct_acum": 91.7
    },
    {
      "producto": {
        "id": 50,
        "clave_interna": "HI-005",
        "nombre": "Toallas femeninas"
      },
      "clase": "B",
      "unidades": 5,
      "venta": 180.0,
      "pct_acum": 93.0
    },
    {
      "producto": {
        "id": 4,
        "clave_interna": "AB-004",
        "nombre": "Azúcar estándar"
      },
      "clase": "B",
      "unidades": 4,
      "venta": 114.0,
      "pct_acum": 93.9
    },
    {
      "producto": {
        "id": 15,
        "clave_interna": "AB-015",
        "nombre": "Avena en hojuelas"
      },
      "clase": "B",
      "unidades": 4,
      "venta": 108.0,
      "pct_acum": 94.9
    },
    {
      "producto": {
        "id": 32,
        "clave_interna": "LA-004",
        "nombre": "Queso Oaxaca"
      },
      "clase": "B",
      "unidades": 4,
      "venta": 288.0,
      "pct_acum": 95.9
    },
    {
      "producto": {
        "id": 33,
        "clave_interna": "LA-005",
        "nombre": "Crema ácida"
      },
      "clase": "C",
      "unidades": 4,
      "venta": 144.0,
      "pct_acum": 96.8
    },
    {
      "producto": {
        "id": 37,
        "clave_interna": "LI-001",
        "nombre": "Detergente en polvo"
      },
      "clase": "C",
      "unidades": 4,
      "venta": 168.0,
      "pct_acum": 97.8
    },
    {
      "producto": {
        "id": 9,
        "clave_interna": "AB-009",
        "nombre": "Atún en agua"
      },
      "clase": "C",
      "unidades": 3,
      "venta": 63.0,
      "pct_acum": 98.5
    },
    {
      "producto": {
        "id": 38,
        "clave_interna": "LI-002",
        "nombre": "Jabón para trastes"
      },
      "clase": "C",
      "unidades": 3,
      "venta": 78.0,
      "pct_acum": 99.3
    },
    {
      "producto": {
        "id": 31,
        "clave_interna": "LA-003",
        "nombre": "Queso fresco"
      },
      "clase": "C",
      "unidades": 2,
      "venta": 116.0,
      "pct_acum": 99.8
    },
    {
      "producto": {
        "id": 21,
        "clave_interna": "BE-001",
        "nombre": "Agua purificada"
      },
      "clase": "C",
      "unidades": 1,
      "venta": 38.0,
      "pct_acum": 100.0
    }
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 80.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 95.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 7.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 5.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 90.0,
      "modificado": false
    }
  ]
}
```

**Explicación.** El corte (80/95) es una convención de Pareto, documentada como «normativo» en GET /surtido/supuestos.

### SUR-02 · Análisis de un microhub · PASA

**Objetivo.** Clase, rotación, cobertura, margen, quiebres y recomendación por producto.

**Petición.** `GET http://surtido:5122/api/v1/surtido/analisis?microhub_id=1`

```http
Accept: application/json
X-Traza-Id: 9cc43112-1d1f-4ddc-840d-2eb3e0b1f7e6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 374 ms · traza `9cc43112-1d1f-4ddc-840d-2eb3e0b1f7e6`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "ventana_dias": 90,
  "resumen": {
    "productos": 51,
    "aumentar": 1,
    "mantener": 0,
    "reducir": 50,
    "eliminar": 0,
    "excluir": 0,
    "clase_a": 32,
    "clase_b": 13,
    "clase_c": 6,
    "unidades_a_comprar": 1,
    "con_costo_estimado": 51,
    "espacio": {
      "total": 3600.0,
      "ocupado": 3301.0,
      "sugerido": 1.0,
      "ocupacion_pct": 91.7
    },
    "presupuesto": {
      "total": 120000.0,
      "requerido": 27.36,
      "uso_pct": 0.0
    }
  },
  "filas": [
    {
      "producto": {
        "id": 28,
        "clave_interna": "BE-008",
        "nombre": "Polvo para agua de sabor"
      },
      "categoria": "Bebidas",
      "clase": "A",
      "pct_acum": 5.3,
      "unidades": 22,
      "venta": 165.0,
      "margen_unitario": 2.1,
      "margen_total": 46.2,
      "costo_estimado": true,
      "existencia": 30,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.24,
      "cobertura_dias": 122.7,
      "rotacion": 0.73,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 123 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 45,
        "clave_interna": "LI-009",
        "nombre": "Fibra para trastes"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 9.2,
      "unidades": 16,
      "venta": 288.0,
      "margen_unitario": 5.04,
      "margen_total": 80.64,
      "costo_estimado": true,
      "existencia": 43,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.18,
      "cobertura_dias": 241.9,
      "rotacion": 0.37,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 242 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 7,
        "clave_interna": "AB-007",
        "nombre": "Harina de trigo"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 12.9,
      "unidades": 15,
      "venta": 367.5,
      "margen_unitario": 6.86,
      "margen_total": 102.9,
      "costo_estimado": true,
      "existencia": 14,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.17,
      "cobertura_dias": 84.0,
      "rotacion": 1.07,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 84 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 25,
        "clave_interna": "BE-005",
        "nombre": "Jugo de naranja"
      },
      "categoria": "Bebidas",
      "clase": "A",
      "pct_acum": 16.5,
      "unidades": 15,
      "venta": 420.0,
      "margen_unitario": 7.84,
      "margen_total": 117.6,
      "costo_estimado": true,
      "existencia": 80,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.17,
      "cobertura_dias": 480.0,
      "rotacion": 0.19,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 480 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 48,
        "clave_interna": "HI-003",
        "nombre": "Pasta dental"
      },
      "categoria": "Higiene personal",
      "clase": "A",
      "pct_acum": 20.1,
      "unidades": 15,
      "venta": 480.0,
      "margen_unitario": 8.96,
      "margen_total": 134.4,
      "costo_estimado": true,
      "existencia": 74,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.17,
      "cobertura_dias": 444.0,
      "rotacion": 0.2,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 444 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 13,
        "clave_interna": "AB-013",
        "nombre": "Puré de tomate"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 23.5,
      "unidades": 14,
      "venta": 154.0,
      "margen_unitario": 3.08,
      "margen_total": 43.12,
      "costo_estimado": true,
      "existencia": 56,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.16,
      "cobertura_dias": 360.0,
      "rotacion": 0.25,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 360 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 20,
        "clave_interna": "AB-020",
        "nombre": "Lenteja"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 26.7,
      "unidades": 13,
      "venta": 312.0,
      "margen_unitario": 6.72,
      "margen_total": 87.36,
      "costo_estimado": true,
      "existencia": 73,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.14,
      "cobertura_dias": 505.4,
      "rotacion": 0.18,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 505 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 36,
        "clave_interna": "LA-008",
        "nombre": "Jamón de pavo"
      },
      "categoria": "Lácteos y huevo",
      "clase": "A",
      "pct_acum": 29.9,
      "unidades": 13,
      "venta": 598.0,
      "margen_unitario": 12.88,
      "margen_total": 167.44,
      "costo_estimado": true,
      "existencia": 47,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.14,
      "cobertura_dias": 325.4,
      "rotacion": 0.28,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 325 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 30,
        "clave_interna": "LA-002",
        "nombre": "Leche deslactosada"
      },
      "categoria": "Lácteos y huevo",
      "clase": "A",
      "pct_acum": 32.8,
      "unidades": 12,
      "venta": 372.0,
      "margen_unitario": 8.68,
      "margen_total": 104.16,
      "costo_estimado": true,
      "existencia": 12,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.13,
      "cobertura_dias": 90.0,
      "rotacion": 1.0,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 90 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 34,
        "clave_interna": "LA-006",
        "nombre": "Yogur natural"
      },
      "categoria": "Lácteos y huevo",
      "clase": "A",
      "pct_acum": 35.7,
      "unidades": 12,
      "venta": 528.0,
      "margen_unitario": 12.32,
      "margen_total": 147.84,
      "costo_estimado": true,
      "existencia": 10,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.13,
      "cobertura_dias": 75.0,
      "rotacion": 1.2,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 75 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 42,
        "clave_interna": "LI-006",
        "nombre": "Papel higiénico"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 38.6,
      "unidades": 12,
      "venta": 456.0,
      "margen_unitario": 10.64,
      "margen_total": 127.68,
      "costo_estimado": true,
      "existencia": 64,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.13,
      "cobertura_dias": 480.0,
      "rotacion": 0.19,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 480 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 39,
        "clave_interna": "LI-003",
        "nombre": "Cloro"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 41.3,
      "unidades": 11,
      "venta": 214.5,
      "margen_unitario": 5.46,
      "margen_total": 60.06,
      "costo_estimado": true,
      "existencia": 44,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.12,
      "cobertura_dias": 360.0,
      "rotacion": 0.25,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 360 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 43,
        "clave_interna": "LI-007",
        "nombre": "Servilletas"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 43.7,
      "unidades": 10,
      "venta": 320.0,
      "margen_unitario": 8.96,
      "margen_total": 89.6,
      "costo_estimado": true,
      "existencia": 65,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.11,
      "cobertura_dias": 585.0,
      "rotacion": 0.15,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 585 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 2,
        "clave_interna": "AB-002",
        "nombre": "Arroz superextra"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 45.9,
      "unidades": 9,
      "venta": 269.1,
      "margen_unitario": 8.37,
      "margen_total": 75.33,
      "costo_estimado": true,
      "existencia": 36,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 360.0,
      "rotacion": 0.25,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 360 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 11,
        "clave_interna": "AB-011",
        "nombre": "Frijoles refritos"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 48.1,
      "unidades": 9,
      "venta": 207.0,
      "margen_unitario": 6.44,
      "margen_total": 57.96,
      "costo_estimado": true,
      "existencia": 27,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 270.0,
      "rotacion": 0.33,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 270 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 12,
        "clave_interna": "AB-012",
        "nombre": "Chiles jalapeños en escabeche"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 50.2,
      "unidades": 9,
      "venta": 175.5,
      "margen_unitario": 5.46,
      "margen_total": 49.14,
      "costo_estimado": true,
      "existencia": 392,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 3920.0,
      "rotacion": 0.02,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 3920 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 19,
        "clave_interna": "AB-019",
        "nombre": "Huevo blanco"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 52.4,
      "unidades": 9,
      "venta": 378.0,
      "margen_unitario": 11.76,
      "margen_total": 105.84,
      "costo_estimado": true,
      "existencia": 49,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 490.0,
      "rotacion": 0.18,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 490 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 44,
        "clave_interna": "LI-008",
        "nombre": "Bolsas para basura"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 54.6,
      "unidades": 9,
      "venta": 216.0,
      "margen_unitario": 6.72,
      "margen_total": 60.48,
      "costo_estimado": true,
      "existencia": 26,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 260.0,
      "rotacion": 0.35,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 260 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 1,
        "clave_interna": "AB-001",
        "nombre": "Frijol negro a granel"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 56.6,
      "unidades": 8,
      "venta": 308.0,
      "margen_unitario": 10.78,
      "margen_total": 86.24,
      "costo_estimado": true,
      "existencia": 58,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 652.5,
      "rotacion": 0.14,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 652 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 6,
        "clave_interna": "AB-006",
        "nombre": "Harina de maíz nixtamalizado"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 58.5,
      "unidades": 8,
      "venta": 208.0,
      "margen_unitario": 7.28,
      "margen_total": 58.24,
      "costo_estimado": true,
      "existencia": 81,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 911.2,
      "rotacion": 0.1,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 911 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 24,
        "clave_interna": "BE-004",
        "nombre": "Refresco sabor manzana"
      },
      "categoria": "Bebidas",
      "clase": "A",
      "pct_acum": 60.4,
      "unidades": 8,
      "venta": 288.0,
      "margen_unitario": 10.08,
      "margen_total": 80.64,
      "costo_estimado": true,
      "existencia": 39,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 438.8,
      "rotacion": 0.21,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 439 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 27,
        "clave_interna": "BE-007",
        "nombre": "Té helado de limón"
      },
      "categoria": "Bebidas",
      "clase": "A",
      "pct_acum": 62.4,
      "unidades": 8,
      "venta": 136.0,
      "margen_unitario": 4.76,
      "margen_total": 38.08,
      "costo_estimado": true,
      "existencia": 84,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 945.0,
      "rotacion": 0.1,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 945 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 29,
        "clave_interna": "LA-001",
        "nombre": "Leche entera"
      },
      "categoria": "Lácteos y huevo",
      "clase": "A",
      "pct_acum": 64.3,
      "unidades": 8,
      "venta": 220.0,
      "margen_unitario": 7.7,
      "margen_total": 61.6,
      "costo_estimado": true,
      "existencia": 48,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 540.0,
      "rotacion": 0.17,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 540 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 40,
        "clave_interna": "LI-004",
        "nombre": "Limpiador multiusos"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 66.3,
      "unidades": 8,
      "venta": 224.0,
      "margen_unitario": 7.84,
      "margen_total": 62.72,
      "costo_estimado": true,
      "existencia": 14,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 157.5,
      "rotacion": 0.57,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 158 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 51,
        "clave_interna": "HI-006",
        "nombre": "Pañal etapa 3"
      },
      "categoria": "Higiene personal",
      "clase": "A",
      "pct_acum": 68.2,
      "unidades": 8,
      "venta": 544.0,
      "margen_unitario": 19.04,
      "margen_total": 152.32,
      "costo_estimado": true,
      "existencia": 29,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 326.2,
      "rotacion": 0.28,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 326 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 5,
        "clave_interna": "AB-005",
        "nombre": "Sal de mesa"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 69.9,
      "unidades": 7,
      "venta": 98.0,
      "margen_unitario": 3.92,
      "margen_total": 27.44,
      "costo_estimado": true,
      "existencia": 30,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 385.7,
      "rotacion": 0.23,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 386 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 8,
        "clave_interna": "AB-008",
        "nombre": "Pasta para sopa surtida"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 71.6,
      "unidades": 7,
      "venta": 66.5,
      "margen_unitario": 2.66,
      "margen_total": 18.62,
      "costo_estimado": true,
      "existencia": 21,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 270.0,
      "rotacion": 0.33,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 270 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 10,
        "clave_interna": "AB-010",
        "nombre": "Sardina en salsa de tomate"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 73.3,
      "unidades": 7,
      "venta": 185.5,
      "margen_unitario": 7.42,
      "margen_total": 51.94,
      "costo_estimado": true,
      "existencia": 690,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 8871.4,
      "rotacion": 0.01,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 8871 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 14,
        "clave_interna": "AB-014",
        "nombre": "Café soluble"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 75.0,
      "unidades": 7,
      "venta": 364.0,
      "margen_unitario": 14.56,
      "margen_total": 101.92,
      "costo_estimado": true,
      "existencia": 33,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 424.3,
      "rotacion": 0.21,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 424 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 18,
        "clave_interna": "AB-018",
        "nombre": "Pan de caja blanco"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 76.7,
      "unidades": 7,
      "venta": 308.0,
      "margen_unitario": 12.32,
      "margen_total": 86.24,
      "costo_estimado": true,
      "existencia": 80,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 1028.6,
      "rotacion": 0.09,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1029 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 47,
        "clave_interna": "HI-002",
        "nombre": "Shampoo"
      },
      "categoria": "Higiene personal",
      "clase": "A",
      "pct_acum": 78.4,
      "unidades": 7,
      "venta": 378.0,
      "margen_unitario": 15.12,
      "margen_total": 105.84,
      "costo_estimado": true,
      "existencia": 60,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 771.4,
      "rotacion": 0.12,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 771 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 49,
        "clave_interna": "HI-004",
        "nombre": "Desodorante"
      },
      "categoria": "Higiene personal",
      "clase": "A",
      "pct_acum": 80.1,
      "unidades": 7,
      "venta": 336.0,
      "margen_unitario": 13.44,
      "margen_total": 94.08,
      "costo_estimado": true,
      "existencia": 36,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 462.9,
      "rotacion": 0.19,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 463 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 3,
        "clave_interna": "AB-003",
        "nombre": "Aceite vegetal"
      },
      "categoria": "Abarrote básico",
      "clase": "B",
      "pct_acum": 81.6,
      "unidades": 6,
      "venta": 252.0,
      "margen_unitario": 11.76,
      "margen_total": 70.56,
      "costo_estimado": true,
      "existencia": 10,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.07,
      "cobertura_dias": 150.0,
      "rotacion": 0.6,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 150 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 17,
        "clave_interna": "AB-017",
        "nombre": "Tortillas de maíz"
      },
      "categoria": "Abarrote básico",
      "clase": "B",
      "pct_acum": 83.0,
      "unidades": 6,
      "venta": 144.0,
      "margen_unitario": 6.72,
      "margen_total": 40.32,
      "costo_estimado": true,
      "existencia": 21,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.07,
      "cobertura_dias": 315.0,
      "rotacion": 0.29,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 315 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 26,
        "clave_interna": "BE-006",
        "nombre": "Bebida de soya"
      },
      "categoria": "Bebidas",
      "clase": "B",
      "pct_acum": 84.5,
      "unidades": 6,
      "venta": 192.0,
      "margen_unitario": 8.96,
      "margen_total": 53.76,
      "costo_estimado": true,
      "existencia": 17,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.07,
      "cobertura_dias": 255.0,
      "rotacion": 0.35,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 255 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 16,
        "clave_interna": "AB-016",
        "nombre": "Galletas María"
      },
      "categoria": "Abarrote básico",
      "clase": "B",
      "pct_acum": 85.7,
      "unidades": 5,
      "venta": 82.5,
      "margen_unitario": 4.62,
      "margen_total": 23.1,
      "costo_estimado": true,
      "existencia": 81,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 1458.0,
      "rotacion": 0.06,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1458 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 22,
        "clave_interna": "BE-002",
        "nombre": "Agua embotellada"
      },
      "categoria": "Bebidas",
      "clase": "B",
      "pct_acum": 86.9,
      "unidades": 5,
      "venta": 75.0,
      "margen_unitario": 4.2,
      "margen_total": 21.0,
      "costo_estimado": true,
      "existencia": 72,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 1296.0,
      "rotacion": 0.07,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1296 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 23,
        "clave_interna": "BE-003",
        "nombre": "Refresco de cola"
      },
      "categoria": "Bebidas",
      "clase": "B",
      "pct_acum": 88.1,
      "unidades": 5,
      "venta": 192.5,
      "margen_unitario": 10.78,
      "margen_total": 53.9,
      "costo_estimado": true,
      "existencia": 54,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 972.0,
      "rotacion": 0.09,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 972 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 35,
        "clave_interna": "LA-007",
        "nombre": "Mantequilla"
      },
      "categoria": "Lácteos y huevo",
      "clase": "B",
      "pct_acum": 89.3,
      "unidades": 5,
      "venta": 110.0,
      "margen_unitario": 6.16,
      "margen_total": 30.8,
      "costo_estimado": true,
      "existencia": 64,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 1152.0,
      "rotacion": 0.08,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1152 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 41,
        "clave_interna": "LI-005",
        "nombre": "Suavizante de telas"
      },
      "categoria": "Limpieza del hogar",
      "clase": "B",
      "pct_acum": 90.5,
      "unidades": 5,
      "venta": 165.0,
      "margen_unitario": 9.24,
      "margen_total": 46.2,
      "costo_estimado": true,
      "existencia": 69,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 1242.0,
      "rotacion": 0.07,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1242 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 46,
        "clave_interna": "HI-001",
        "nombre": "Jabón de tocador"
      },
      "categoria": "Higiene personal",
      "clase": "B",
      "pct_acum": 91.7,
      "unidades": 5,
      "venta": 72.5,
      "margen_unitario": 4.06,
      "margen_total": 20.3,
      "costo_estimado": true,
      "existencia": 63,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 1134.0,
      "rotacion": 0.08,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1134 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 50,
        "clave_interna": "HI-005",
        "nombre": "Toallas femeninas"
      },
      "categoria": "Higiene personal",
      "clase": "B",
      "pct_acum": 93.0,
      "unidades": 5,
      "venta": 180.0,
      "margen_unitario": 10.08,
      "margen_total": 50.4,
      "costo_estimado": true,
      "existencia": 76,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 1368.0,
      "rotacion": 0.07,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1368 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 4,
        "clave_interna": "AB-004",
        "nombre": "Azúcar estándar"
      },
      "categoria": "Abarrote básico",
      "clase": "B",
      "pct_acum": 93.9,
      "unidades": 4,
      "venta": 114.0,
      "margen_unitario": 7.98,
      "margen_total": 31.92,
      "costo_estimado": true,
      "existencia": 18,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.04,
      "cobertura_dias": 405.0,
      "rotacion": 0.22,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 405 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 15,
        "clave_interna": "AB-015",
        "nombre": "Avena en hojuelas"
      },
      "categoria": "Abarrote básico",
      "clase": "B",
      "pct_acum": 94.9,
      "unidades": 4,
      "venta": 108.0,
      "margen_unitario": 7.56,
      "margen_total": 30.24,
      "costo_estimado": true,
      "existencia": 52,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.04,
      "cobertura_dias": 1170.0,
      "rotacion": 0.08,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1170 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 32,
        "clave_interna": "LA-004",
        "nombre": "Queso Oaxaca"
      },
      "categoria": "Lácteos y huevo",
      "clase": "B",
      "pct_acum": 95.9,
      "unidades": 4,
      "venta": 288.0,
      "margen_unitario": 20.16,
      "margen_total": 80.64,
      "costo_estimado": true,
      "existencia": 20,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.04,
      "cobertura_dias": 450.0,
      "rotacion": 0.2,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 450 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 33,
        "clave_interna": "LA-005",
        "nombre": "Crema ácida"
      },
      "categoria": "Lácteos y huevo",
      "clase": "C",
      "pct_acum": 96.8,
      "unidades": 4,
      "venta": 144.0,
      "margen_unitario": 10.08,
      "margen_total": 40.32,
      "costo_estimado": true,
      "existencia": 82,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.04,
      "cobertura_dias": 1845.0,
      "rotacion": 0.05,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1845 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 37,
        "clave_interna": "LI-001",
        "nombre": "Detergente en polvo"
      },
      "categoria": "Limpieza del hogar",
      "clase": "C",
      "pct_acum": 97.8,
      "unidades": 4,
      "venta": 168.0,
      "margen_unitario": 11.76,
      "margen_total": 47.04,
      "costo_estimado": true,
      "existencia": 13,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.04,
      "cobertura_dias": 292.5,
      "rotacion": 0.31,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 292 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 9,
        "clave_interna": "AB-009",
        "nombre": "Atún en agua"
      },
      "categoria": "Abarrote básico",
      "clase": "C",
      "pct_acum": 98.5,
      "unidades": 3,
      "venta": 63.0,
      "margen_unitario": 5.88,
      "margen_total": 17.64,
      "costo_estimado": true,
      "existencia": 42,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.03,
      "cobertura_dias": 1260.0,
      "rotacion": 0.07,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1260 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 38,
        "clave_interna": "LI-002",
        "nombre": "Jabón para trastes"
      },
      "categoria": "Limpieza del hogar",
      "clase": "C",
      "pct_acum": 99.3,
      "unidades": 3,
      "venta": 78.0,
      "margen_unitario": 7.28,
      "margen_total": 21.84,
      "costo_estimado": true,
      "existencia": 47,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.03,
      "cobertura_dias": 1410.0,
      "rotacion": 0.06,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1410 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 31,
        "clave_interna": "LA-003",
        "nombre": "Queso fresco"
      },
      "categoria": "Lácteos y huevo",
      "clase": "C",
      "pct_acum": 99.8,
      "unidades": 2,
      "venta": 116.0,
      "margen_unitario": 16.24,
      "margen_total": 32.48,
      "costo_estimado": true,
      "existencia": 55,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.02,
      "cobertura_dias": 2475.0,
      "rotacion": 0.04,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 2475 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 21,
        "clave_interna": "BE-001",
        "nombre": "Agua purificada"
      },
      "categoria": "Bebidas",
      "clase": "C",
      "pct_acum": 100.0,
      "unidades": 1,
      "venta": 38.0,
      "margen_unitario": 10.64,
      "margen_total": 10.64,
      "costo_estimado": true,
      "existencia": 0,
      "minimo": 10,
      "quiebres": 2,
      "demanda_dia": 0.01,
      "cobertura_dias": 0.0,
      "rotacion": 99.0,
      "recomendacion": "Aumentar",
      "motivo": "hubo quiebres",
      "sugerido": 1,
      "limitado_por": null
    }
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 80.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 95.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 7.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 5.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 90.0,
      "modificado": false
    }
  ]
}
```

**Explicación.** Aumentar si hubo quiebres, la existencia está en el mínimo o la cobertura de un A o B es menos de la mitad del objetivo; Reducir con más de 30 días de cobertura; Eliminar si no se movió. Lo que se sugiere aumentar se limita al espacio y al presupuesto del microhub.

**Evidencia en PostgreSQL.** `SELECT microhub_id, espacio_total, presupuesto FROM surtido_restriccion ORDER BY microhub_id`

```json
[
  {
    "microhub_id": 1,
    "espacio_total": "3600.0",
    "presupuesto": "120000.00"
  },
  {
    "microhub_id": 2,
    "espacio_total": "3000.0",
    "presupuesto": "100000.00"
  },
  {
    "microhub_id": 3,
    "espacio_total": "3200.0",
    "presupuesto": "100000.00"
  },
  {
    "microhub_id": 4,
    "espacio_total": "2800.0",
    "presupuesto": "90000.00"
  }
]
```

### SUR-03 · Análisis de toda la red · PASA

**Objetivo.** Sin microhub no hay restricciones de espacio ni de presupuesto.

**Petición.** `GET http://surtido:5122/api/v1/surtido/analisis`

```http
Accept: application/json
X-Traza-Id: 6d59c623-fac5-42ed-93b7-73e823a0dfc8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 448 ms · traza `6d59c623-fac5-42ed-93b7-73e823a0dfc8`

```json
{
  "microhub": null,
  "ventana_dias": 90,
  "resumen": {
    "productos": 51,
    "aumentar": 5,
    "mantener": 0,
    "reducir": 46,
    "eliminar": 0,
    "excluir": 0,
    "clase_a": 36,
    "clase_b": 10,
    "clase_c": 5,
    "unidades_a_comprar": 1,
    "con_costo_estimado": 51,
    "espacio": {
      "total": null,
      "ocupado": 7604.0,
      "sugerido": 1.0,
      "ocupacion_pct": null
    },
    "presupuesto": {
      "total": null,
      "requerido": 27.36,
      "uso_pct": null
    }
  },
  "filas": [
    {
      "producto": {
        "id": 28,
        "clave_interna": "BE-008",
        "nombre": "Polvo para agua de sabor"
      },
      "categoria": "Bebidas",
      "clase": "A",
      "pct_acum": 4.7,
      "unidades": 64,
      "venta": 480.0,
      "margen_unitario": 2.1,
      "margen_total": 134.4,
      "costo_estimado": true,
      "existencia": 161,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.71,
      "cobertura_dias": 226.4,
      "rotacion": 0.4,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 226 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 16,
        "clave_interna": "AB-016",
        "nombre": "Galletas María"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 7.8,
      "unidades": 43,
      "venta": 709.5,
      "margen_unitario": 4.62,
      "margen_total": 198.66,
      "costo_estimado": true,
      "existencia": 148,
      "minimo": 21,
      "quiebres": 0,
      "demanda_dia": 0.48,
      "cobertura_dias": 309.8,
      "rotacion": 0.29,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 310 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 15,
        "clave_interna": "AB-015",
        "nombre": "Avena en hojuelas"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 10.8,
      "unidades": 40,
      "venta": 1080.0,
      "margen_unitario": 7.56,
      "margen_total": 302.4,
      "costo_estimado": true,
      "existencia": 155,
      "minimo": 15,
      "quiebres": 0,
      "demanda_dia": 0.44,
      "cobertura_dias": 348.8,
      "rotacion": 0.26,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 349 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 7,
        "clave_interna": "AB-007",
        "nombre": "Harina de trigo"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 13.6,
      "unidades": 38,
      "venta": 931.0,
      "margen_unitario": 6.86,
      "margen_total": 260.68,
      "costo_estimado": true,
      "existencia": 156,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.42,
      "cobertura_dias": 369.5,
      "rotacion": 0.24,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 369 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 23,
        "clave_interna": "BE-003",
        "nombre": "Refresco de cola"
      },
      "categoria": "Bebidas",
      "clase": "A",
      "pct_acum": 16.3,
      "unidades": 38,
      "venta": 1463.0,
      "margen_unitario": 10.78,
      "margen_total": 409.64,
      "costo_estimado": true,
      "existencia": 179,
      "minimo": 21,
      "quiebres": 0,
      "demanda_dia": 0.42,
      "cobertura_dias": 423.9,
      "rotacion": 0.21,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 424 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 45,
        "clave_interna": "LI-009",
        "nombre": "Fibra para trastes"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 19.0,
      "unidades": 37,
      "venta": 666.0,
      "margen_unitario": 5.04,
      "margen_total": 186.48,
      "costo_estimado": true,
      "existencia": 167,
      "minimo": 26,
      "quiebres": 0,
      "demanda_dia": 0.41,
      "cobertura_dias": 406.2,
      "rotacion": 0.22,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 406 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 13,
        "clave_interna": "AB-013",
        "nombre": "Puré de tomate"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 21.6,
      "unidades": 35,
      "venta": 385.0,
      "margen_unitario": 3.08,
      "margen_total": 107.8,
      "costo_estimado": true,
      "existencia": 82,
      "minimo": 20,
      "quiebres": 2,
      "demanda_dia": 0.39,
      "cobertura_dias": 210.9,
      "rotacion": 0.43,
      "recomendacion": "Aumentar",
      "motivo": "hubo quiebres",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 2,
        "clave_interna": "AB-002",
        "nombre": "Arroz superextra"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 24.0,
      "unidades": 33,
      "venta": 986.7,
      "margen_unitario": 8.37,
      "margen_total": 276.21,
      "costo_estimado": true,
      "existencia": 108,
      "minimo": 25,
      "quiebres": 0,
      "demanda_dia": 0.37,
      "cobertura_dias": 294.5,
      "rotacion": 0.31,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 295 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 36,
        "clave_interna": "LA-008",
        "nombre": "Jamón de pavo"
      },
      "categoria": "Lácteos y huevo",
      "clase": "A",
      "pct_acum": 26.4,
      "unidades": 33,
      "venta": 1518.0,
      "margen_unitario": 12.88,
      "margen_total": 425.04,
      "costo_estimado": true,
      "existencia": 94,
      "minimo": 18,
      "quiebres": 0,
      "demanda_dia": 0.37,
      "cobertura_dias": 256.4,
      "rotacion": 0.35,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 256 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 40,
        "clave_interna": "LI-004",
        "nombre": "Limpiador multiusos"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 28.9,
      "unidades": 33,
      "venta": 924.0,
      "margen_unitario": 7.84,
      "margen_total": 258.72,
      "costo_estimado": true,
      "existencia": 71,
      "minimo": 24,
      "quiebres": 0,
      "demanda_dia": 0.37,
      "cobertura_dias": 193.6,
      "rotacion": 0.46,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 194 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 30,
        "clave_interna": "LA-002",
        "nombre": "Leche deslactosada"
      },
      "categoria": "Lácteos y huevo",
      "clase": "A",
      "pct_acum": 31.2,
      "unidades": 32,
      "venta": 992.0,
      "margen_unitario": 8.68,
      "margen_total": 277.76,
      "costo_estimado": true,
      "existencia": 60,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.36,
      "cobertura_dias": 168.8,
      "rotacion": 0.53,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 169 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 25,
        "clave_interna": "BE-005",
        "nombre": "Jugo de naranja"
      },
      "categoria": "Bebidas",
      "clase": "A",
      "pct_acum": 33.5,
      "unidades": 31,
      "venta": 868.0,
      "margen_unitario": 7.84,
      "margen_total": 243.04,
      "costo_estimado": true,
      "existencia": 198,
      "minimo": 15,
      "quiebres": 0,
      "demanda_dia": 0.34,
      "cobertura_dias": 574.8,
      "rotacion": 0.16,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 575 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 26,
        "clave_interna": "BE-006",
        "nombre": "Bebida de soya"
      },
      "categoria": "Bebidas",
      "clase": "A",
      "pct_acum": 35.8,
      "unidades": 31,
      "venta": 992.0,
      "margen_unitario": 8.96,
      "margen_total": 277.76,
      "costo_estimado": true,
      "existencia": 50,
      "minimo": 28,
      "quiebres": 2,
      "demanda_dia": 0.34,
      "cobertura_dias": 145.2,
      "rotacion": 0.62,
      "recomendacion": "Aumentar",
      "motivo": "hubo quiebres",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 34,
        "clave_interna": "LA-006",
        "nombre": "Yogur natural"
      },
      "categoria": "Lácteos y huevo",
      "clase": "A",
      "pct_acum": 38.0,
      "unidades": 31,
      "venta": 1364.0,
      "margen_unitario": 12.32,
      "margen_total": 381.92,
      "costo_estimado": true,
      "existencia": 86,
      "minimo": 21,
      "quiebres": 1,
      "demanda_dia": 0.34,
      "cobertura_dias": 249.7,
      "rotacion": 0.36,
      "recomendacion": "Aumentar",
      "motivo": "hubo quiebres",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 48,
        "clave_interna": "HI-003",
        "nombre": "Pasta dental"
      },
      "categoria": "Higiene personal",
      "clase": "A",
      "pct_acum": 40.3,
      "unidades": 31,
      "venta": 992.0,
      "margen_unitario": 8.96,
      "margen_total": 277.76,
      "costo_estimado": true,
      "existencia": 165,
      "minimo": 20,
      "quiebres": 0,
      "demanda_dia": 0.34,
      "cobertura_dias": 479.0,
      "rotacion": 0.19,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 479 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 50,
        "clave_interna": "HI-005",
        "nombre": "Toallas femeninas"
      },
      "categoria": "Higiene personal",
      "clase": "A",
      "pct_acum": 42.6,
      "unidades": 31,
      "venta": 1116.0,
      "margen_unitario": 10.08,
      "margen_total": 312.48,
      "costo_estimado": true,
      "existencia": 148,
      "minimo": 21,
      "quiebres": 0,
      "demanda_dia": 0.34,
      "cobertura_dias": 429.7,
      "rotacion": 0.21,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 430 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 1,
        "clave_interna": "AB-001",
        "nombre": "Frijol negro a granel"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 44.8,
      "unidades": 30,
      "venta": 1155.0,
      "margen_unitario": 10.78,
      "margen_total": 323.4,
      "costo_estimado": true,
      "existencia": 161,
      "minimo": 25,
      "quiebres": 0,
      "demanda_dia": 0.33,
      "cobertura_dias": 483.0,
      "rotacion": 0.19,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 483 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 20,
        "clave_interna": "AB-020",
        "nombre": "Lenteja"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 47.0,
      "unidades": 30,
      "venta": 720.0,
      "margen_unitario": 6.72,
      "margen_total": 201.6,
      "costo_estimado": true,
      "existencia": 196,
      "minimo": 20,
      "quiebres": 0,
      "demanda_dia": 0.33,
      "cobertura_dias": 588.0,
      "rotacion": 0.15,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 588 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 51,
        "clave_interna": "HI-006",
        "nombre": "Pañal etapa 3"
      },
      "categoria": "Higiene personal",
      "clase": "A",
      "pct_acum": 49.2,
      "unidades": 30,
      "venta": 2040.0,
      "margen_unitario": 19.04,
      "margen_total": 571.2,
      "costo_estimado": true,
      "existencia": 127,
      "minimo": 20,
      "quiebres": 0,
      "demanda_dia": 0.33,
      "cobertura_dias": 381.0,
      "rotacion": 0.24,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 381 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 10,
        "clave_interna": "AB-010",
        "nombre": "Sardina en salsa de tomate"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 51.3,
      "unidades": 29,
      "venta": 768.5,
      "margen_unitario": 7.42,
      "margen_total": 215.18,
      "costo_estimado": true,
      "existencia": 796,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.32,
      "cobertura_dias": 2470.3,
      "rotacion": 0.04,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 2470 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 17,
        "clave_interna": "AB-017",
        "nombre": "Tortillas de maíz"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 53.4,
      "unidades": 29,
      "venta": 696.0,
      "margen_unitario": 6.72,
      "margen_total": 194.88,
      "costo_estimado": true,
      "existencia": 101,
      "minimo": 18,
      "quiebres": 0,
      "demanda_dia": 0.32,
      "cobertura_dias": 313.4,
      "rotacion": 0.29,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 313 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 39,
        "clave_interna": "LI-003",
        "nombre": "Cloro"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 55.5,
      "unidades": 29,
      "venta": 565.5,
      "margen_unitario": 5.46,
      "margen_total": 158.34,
      "costo_estimado": true,
      "existencia": 150,
      "minimo": 28,
      "quiebres": 0,
      "demanda_dia": 0.32,
      "cobertura_dias": 465.5,
      "rotacion": 0.19,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 466 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 42,
        "clave_interna": "LI-006",
        "nombre": "Papel higiénico"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 57.7,
      "unidades": 29,
      "venta": 1102.0,
      "margen_unitario": 10.64,
      "margen_total": 308.56,
      "costo_estimado": true,
      "existencia": 141,
      "minimo": 18,
      "quiebres": 0,
      "demanda_dia": 0.32,
      "cobertura_dias": 437.6,
      "rotacion": 0.21,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 438 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 12,
        "clave_interna": "AB-012",
        "nombre": "Chiles jalapeños en escabeche"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 59.6,
      "unidades": 27,
      "venta": 526.5,
      "margen_unitario": 5.46,
      "margen_total": 147.42,
      "costo_estimado": true,
      "existencia": 482,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.3,
      "cobertura_dias": 1606.7,
      "rotacion": 0.06,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1607 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 27,
        "clave_interna": "BE-007",
        "nombre": "Té helado de limón"
      },
      "categoria": "Bebidas",
      "clase": "A",
      "pct_acum": 61.6,
      "unidades": 27,
      "venta": 459.0,
      "margen_unitario": 4.76,
      "margen_total": 128.52,
      "costo_estimado": true,
      "existencia": 148,
      "minimo": 28,
      "quiebres": 0,
      "demanda_dia": 0.3,
      "cobertura_dias": 493.3,
      "rotacion": 0.18,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 493 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 33,
        "clave_interna": "LA-005",
        "nombre": "Crema ácida"
      },
      "categoria": "Lácteos y huevo",
      "clase": "A",
      "pct_acum": 63.6,
      "unidades": 27,
      "venta": 972.0,
      "margen_unitario": 10.08,
      "margen_total": 272.16,
      "costo_estimado": true,
      "existencia": 200,
      "minimo": 20,
      "quiebres": 0,
      "demanda_dia": 0.3,
      "cobertura_dias": 666.7,
      "rotacion": 0.14,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 667 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 19,
        "clave_interna": "AB-019",
        "nombre": "Huevo blanco"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 65.5,
      "unidades": 26,
      "venta": 1092.0,
      "margen_unitario": 11.76,
      "margen_total": 305.76,
      "costo_estimado": true,
      "existencia": 171,
      "minimo": 21,
      "quiebres": 0,
      "demanda_dia": 0.29,
      "cobertura_dias": 591.9,
      "rotacion": 0.15,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 592 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 43,
        "clave_interna": "LI-007",
        "nombre": "Servilletas"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 67.4,
      "unidades": 26,
      "venta": 832.0,
      "margen_unitario": 8.96,
      "margen_total": 232.96,
      "costo_estimado": true,
      "existencia": 118,
      "minimo": 25,
      "quiebres": 0,
      "demanda_dia": 0.29,
      "cobertura_dias": 408.5,
      "rotacion": 0.22,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 408 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 44,
        "clave_interna": "LI-008",
        "nombre": "Bolsas para basura"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 69.3,
      "unidades": 26,
      "venta": 624.0,
      "margen_unitario": 6.72,
      "margen_total": 174.72,
      "costo_estimado": true,
      "existencia": 49,
      "minimo": 21,
      "quiebres": 0,
      "demanda_dia": 0.29,
      "cobertura_dias": 169.6,
      "rotacion": 0.53,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 170 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 8,
        "clave_interna": "AB-008",
        "nombre": "Pasta para sopa surtida"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 71.1,
      "unidades": 25,
      "venta": 237.5,
      "margen_unitario": 2.66,
      "margen_total": 66.5,
      "costo_estimado": true,
      "existencia": 107,
      "minimo": 28,
      "quiebres": 0,
      "demanda_dia": 0.28,
      "cobertura_dias": 385.2,
      "rotacion": 0.23,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 385 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 29,
        "clave_interna": "LA-001",
        "nombre": "Leche entera"
      },
      "categoria": "Lácteos y huevo",
      "clase": "A",
      "pct_acum": 73.0,
      "unidades": 25,
      "venta": 687.5,
      "margen_unitario": 7.7,
      "margen_total": 192.5,
      "costo_estimado": true,
      "existencia": 130,
      "minimo": 25,
      "quiebres": 0,
      "demanda_dia": 0.28,
      "cobertura_dias": 468.0,
      "rotacion": 0.19,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 468 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 47,
        "clave_interna": "HI-002",
        "nombre": "Shampoo"
      },
      "categoria": "Higiene personal",
      "clase": "A",
      "pct_acum": 74.8,
      "unidades": 25,
      "venta": 1350.0,
      "margen_unitario": 15.12,
      "margen_total": 378.0,
      "costo_estimado": true,
      "existencia": 152,
      "minimo": 25,
      "quiebres": 0,
      "demanda_dia": 0.28,
      "cobertura_dias": 547.2,
      "rotacion": 0.16,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 547 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 41,
        "clave_interna": "LI-005",
        "nombre": "Suavizante de telas"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 76.6,
      "unidades": 24,
      "venta": 792.0,
      "margen_unitario": 9.24,
      "margen_total": 221.76,
      "costo_estimado": true,
      "existencia": 143,
      "minimo": 24,
      "quiebres": 0,
      "demanda_dia": 0.27,
      "cobertura_dias": 536.2,
      "rotacion": 0.17,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 536 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 3,
        "clave_interna": "AB-003",
        "nombre": "Aceite vegetal"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 78.2,
      "unidades": 23,
      "venta": 966.0,
      "margen_unitario": 11.76,
      "margen_total": 270.48,
      "costo_estimado": true,
      "existencia": 97,
      "minimo": 15,
      "quiebres": 0,
      "demanda_dia": 0.26,
      "cobertura_dias": 379.6,
      "rotacion": 0.24,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 380 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 11,
        "clave_interna": "AB-011",
        "nombre": "Frijoles refritos"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 79.9,
      "unidades": 23,
      "venta": 529.0,
      "margen_unitario": 6.44,
      "margen_total": 148.12,
      "costo_estimado": true,
      "existencia": 130,
      "minimo": 20,
      "quiebres": 0,
      "demanda_dia": 0.26,
      "cobertura_dias": 508.7,
      "rotacion": 0.18,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 509 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 18,
        "clave_interna": "AB-018",
        "nombre": "Pan de caja blanco"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 81.6,
      "unidades": 23,
      "venta": 1012.0,
      "margen_unitario": 12.32,
      "margen_total": 283.36,
      "costo_estimado": true,
      "existencia": 159,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.26,
      "cobertura_dias": 622.2,
      "rotacion": 0.14,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 622 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 14,
        "clave_interna": "AB-014",
        "nombre": "Café soluble"
      },
      "categoria": "Abarrote básico",
      "clase": "B",
      "pct_acum": 83.2,
      "unidades": 22,
      "venta": 1144.0,
      "margen_unitario": 14.56,
      "margen_total": 320.32,
      "costo_estimado": true,
      "existencia": 104,
      "minimo": 15,
      "quiebres": 0,
      "demanda_dia": 0.24,
      "cobertura_dias": 425.5,
      "rotacion": 0.21,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 425 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 37,
        "clave_interna": "LI-001",
        "nombre": "Detergente en polvo"
      },
      "categoria": "Limpieza del hogar",
      "clase": "B",
      "pct_acum": 84.8,
      "unidades": 22,
      "venta": 924.0,
      "margen_unitario": 11.76,
      "margen_total": 258.72,
      "costo_estimado": true,
      "existencia": 54,
      "minimo": 21,
      "quiebres": 2,
      "demanda_dia": 0.24,
      "cobertura_dias": 220.9,
      "rotacion": 0.41,
      "recomendacion": "Aumentar",
      "motivo": "hubo quiebres",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 32,
        "clave_interna": "LA-004",
        "nombre": "Queso Oaxaca"
      },
      "categoria": "Lácteos y huevo",
      "clase": "B",
      "pct_acum": 86.3,
      "unidades": 20,
      "venta": 1440.0,
      "margen_unitario": 20.16,
      "margen_total": 403.2,
      "costo_estimado": true,
      "existencia": 117,
      "minimo": 28,
      "quiebres": 0,
      "demanda_dia": 0.22,
      "cobertura_dias": 526.5,
      "rotacion": 0.17,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 526 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 5,
        "clave_interna": "AB-005",
        "nombre": "Sal de mesa"
      },
      "categoria": "Abarrote básico",
      "clase": "B",
      "pct_acum": 87.7,
      "unidades": 19,
      "venta": 266.0,
      "margen_unitario": 3.92,
      "margen_total": 74.48,
      "costo_estimado": true,
      "existencia": 119,
      "minimo": 21,
      "quiebres": 0,
      "demanda_dia": 0.21,
      "cobertura_dias": 563.7,
      "rotacion": 0.16,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 564 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 24,
        "clave_interna": "BE-004",
        "nombre": "Refresco sabor manzana"
      },
      "categoria": "Bebidas",
      "clase": "B",
      "pct_acum": 89.0,
      "unidades": 18,
      "venta": 648.0,
      "margen_unitario": 10.08,
      "margen_total": 181.44,
      "costo_estimado": true,
      "existencia": 90,
      "minimo": 25,
      "quiebres": 0,
      "demanda_dia": 0.2,
      "cobertura_dias": 450.0,
      "rotacion": 0.2,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 450 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 31,
        "clave_interna": "LA-003",
        "nombre": "Queso fresco"
      },
      "categoria": "Lácteos y huevo",
      "clase": "B",
      "pct_acum": 90.3,
      "unidades": 18,
      "venta": 1044.0,
      "margen_unitario": 16.24,
      "margen_total": 292.32,
      "costo_estimado": true,
      "existencia": 203,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.2,
      "cobertura_dias": 1015.0,
      "rotacion": 0.09,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1015 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 49,
        "clave_interna": "HI-004",
        "nombre": "Desodorante"
      },
      "categoria": "Higiene personal",
      "clase": "B",
      "pct_acum": 91.6,
      "unidades": 18,
      "venta": 864.0,
      "margen_unitario": 13.44,
      "margen_total": 241.92,
      "costo_estimado": true,
      "existencia": 93,
      "minimo": 15,
      "quiebres": 0,
      "demanda_dia": 0.2,
      "cobertura_dias": 465.0,
      "rotacion": 0.19,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 465 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 9,
        "clave_interna": "AB-009",
        "nombre": "Atún en agua"
      },
      "categoria": "Abarrote básico",
      "clase": "B",
      "pct_acum": 92.9,
      "unidades": 17,
      "venta": 357.0,
      "margen_unitario": 5.88,
      "margen_total": 99.96,
      "costo_estimado": true,
      "existencia": 129,
      "minimo": 20,
      "quiebres": 0,
      "demanda_dia": 0.19,
      "cobertura_dias": 682.9,
      "rotacion": 0.13,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 683 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 35,
        "clave_interna": "LA-007",
        "nombre": "Mantequilla"
      },
      "categoria": "Lácteos y huevo",
      "clase": "B",
      "pct_acum": 94.1,
      "unidades": 17,
      "venta": 374.0,
      "margen_unitario": 6.16,
      "margen_total": 104.72,
      "costo_estimado": true,
      "existencia": 155,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.19,
      "cobertura_dias": 820.6,
      "rotacion": 0.11,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 821 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 46,
        "clave_interna": "HI-001",
        "nombre": "Jabón de tocador"
      },
      "categoria": "Higiene personal",
      "clase": "B",
      "pct_acum": 95.4,
      "unidades": 17,
      "venta": 246.5,
      "margen_unitario": 4.06,
      "margen_total": 69.02,
      "costo_estimado": true,
      "existencia": 183,
      "minimo": 21,
      "quiebres": 0,
      "demanda_dia": 0.19,
      "cobertura_dias": 968.8,
      "rotacion": 0.09,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 969 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 22,
        "clave_interna": "BE-002",
        "nombre": "Agua embotellada"
      },
      "categoria": "Bebidas",
      "clase": "C",
      "pct_acum": 96.6,
      "unidades": 16,
      "venta": 240.0,
      "margen_unitario": 4.2,
      "margen_total": 67.2,
      "costo_estimado": true,
      "existencia": 179,
      "minimo": 26,
      "quiebres": 0,
      "demanda_dia": 0.18,
      "cobertura_dias": 1006.9,
      "rotacion": 0.09,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1007 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 38,
        "clave_interna": "LI-002",
        "nombre": "Jabón para trastes"
      },
      "categoria": "Limpieza del hogar",
      "clase": "C",
      "pct_acum": 97.7,
      "unidades": 15,
      "venta": 390.0,
      "margen_unitario": 7.28,
      "margen_total": 109.2,
      "costo_estimado": true,
      "existencia": 148,
      "minimo": 18,
      "quiebres": 0,
      "demanda_dia": 0.17,
      "cobertura_dias": 888.0,
      "rotacion": 0.1,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 888 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 6,
        "clave_interna": "AB-006",
        "nombre": "Harina de maíz nixtamalizado"
      },
      "categoria": "Abarrote básico",
      "clase": "C",
      "pct_acum": 98.7,
      "unidades": 14,
      "venta": 364.0,
      "margen_unitario": 7.28,
      "margen_total": 101.92,
      "costo_estimado": true,
      "existencia": 196,
      "minimo": 30,
      "quiebres": 0,
      "demanda_dia": 0.16,
      "cobertura_dias": 1260.0,
      "rotacion": 0.07,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1260 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 4,
        "clave_interna": "AB-004",
        "nombre": "Azúcar estándar"
      },
      "categoria": "Abarrote básico",
      "clase": "C",
      "pct_acum": 99.5,
      "unidades": 11,
      "venta": 313.5,
      "margen_unitario": 7.98,
      "margen_total": 87.78,
      "costo_estimado": true,
      "existencia": 48,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.12,
      "cobertura_dias": 392.7,
      "rotacion": 0.23,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 393 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 21,
        "clave_interna": "BE-001",
        "nombre": "Agua purificada"
      },
      "categoria": "Bebidas",
      "clase": "C",
      "pct_acum": 100.0,
      "unidades": 7,
      "venta": 266.0,
      "margen_unitario": 10.64,
      "margen_total": 74.48,
      "costo_estimado": true,
      "existencia": 0,
      "minimo": 30,
      "quiebres": 6,
      "demanda_dia": 0.08,
      "cobertura_dias": 0.0,
      "rotacion": 99.0,
      "recomendacion": "Aumentar",
      "motivo": "hubo quiebres",
      "sugerido": 1,
      "limitado_por": null
    }
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 80.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 95.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 7.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 5.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 90.0,
      "modificado": false
    }
  ]
}
```

### SUR-04 · Solo clase A · PASA

**Objetivo.** Filtro por clase.

**Petición.** `GET http://surtido:5122/api/v1/surtido/analisis?microhub_id=1&clase=A`

```http
Accept: application/json
X-Traza-Id: 2cee05ba-8041-48e4-8beb-92962b2f793f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 375 ms · traza `2cee05ba-8041-48e4-8beb-92962b2f793f`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "ventana_dias": 90,
  "resumen": {
    "productos": 51,
    "aumentar": 1,
    "mantener": 0,
    "reducir": 50,
    "eliminar": 0,
    "excluir": 0,
    "clase_a": 32,
    "clase_b": 13,
    "clase_c": 6,
    "unidades_a_comprar": 1,
    "con_costo_estimado": 51,
    "espacio": {
      "total": 3600.0,
      "ocupado": 3301.0,
      "sugerido": 1.0,
      "ocupacion_pct": 91.7
    },
    "presupuesto": {
      "total": 120000.0,
      "requerido": 27.36,
      "uso_pct": 0.0
    }
  },
  "filas": [
    {
      "producto": {
        "id": 28,
        "clave_interna": "BE-008",
        "nombre": "Polvo para agua de sabor"
      },
      "categoria": "Bebidas",
      "clase": "A",
      "pct_acum": 5.3,
      "unidades": 22,
      "venta": 165.0,
      "margen_unitario": 2.1,
      "margen_total": 46.2,
      "costo_estimado": true,
      "existencia": 30,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.24,
      "cobertura_dias": 122.7,
      "rotacion": 0.73,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 123 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 45,
        "clave_interna": "LI-009",
        "nombre": "Fibra para trastes"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 9.2,
      "unidades": 16,
      "venta": 288.0,
      "margen_unitario": 5.04,
      "margen_total": 80.64,
      "costo_estimado": true,
      "existencia": 43,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.18,
      "cobertura_dias": 241.9,
      "rotacion": 0.37,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 242 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 7,
        "clave_interna": "AB-007",
        "nombre": "Harina de trigo"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 12.9,
      "unidades": 15,
      "venta": 367.5,
      "margen_unitario": 6.86,
      "margen_total": 102.9,
      "costo_estimado": true,
      "existencia": 14,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.17,
      "cobertura_dias": 84.0,
      "rotacion": 1.07,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 84 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 25,
        "clave_interna": "BE-005",
        "nombre": "Jugo de naranja"
      },
      "categoria": "Bebidas",
      "clase": "A",
      "pct_acum": 16.5,
      "unidades": 15,
      "venta": 420.0,
      "margen_unitario": 7.84,
      "margen_total": 117.6,
      "costo_estimado": true,
      "existencia": 80,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.17,
      "cobertura_dias": 480.0,
      "rotacion": 0.19,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 480 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 48,
        "clave_interna": "HI-003",
        "nombre": "Pasta dental"
      },
      "categoria": "Higiene personal",
      "clase": "A",
      "pct_acum": 20.1,
      "unidades": 15,
      "venta": 480.0,
      "margen_unitario": 8.96,
      "margen_total": 134.4,
      "costo_estimado": true,
      "existencia": 74,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.17,
      "cobertura_dias": 444.0,
      "rotacion": 0.2,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 444 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 13,
        "clave_interna": "AB-013",
        "nombre": "Puré de tomate"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 23.5,
      "unidades": 14,
      "venta": 154.0,
      "margen_unitario": 3.08,
      "margen_total": 43.12,
      "costo_estimado": true,
      "existencia": 56,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.16,
      "cobertura_dias": 360.0,
      "rotacion": 0.25,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 360 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 20,
        "clave_interna": "AB-020",
        "nombre": "Lenteja"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 26.7,
      "unidades": 13,
      "venta": 312.0,
      "margen_unitario": 6.72,
      "margen_total": 87.36,
      "costo_estimado": true,
      "existencia": 73,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.14,
      "cobertura_dias": 505.4,
      "rotacion": 0.18,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 505 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 36,
        "clave_interna": "LA-008",
        "nombre": "Jamón de pavo"
      },
      "categoria": "Lácteos y huevo",
      "clase": "A",
      "pct_acum": 29.9,
      "unidades": 13,
      "venta": 598.0,
      "margen_unitario": 12.88,
      "margen_total": 167.44,
      "costo_estimado": true,
      "existencia": 47,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.14,
      "cobertura_dias": 325.4,
      "rotacion": 0.28,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 325 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 30,
        "clave_interna": "LA-002",
        "nombre": "Leche deslactosada"
      },
      "categoria": "Lácteos y huevo",
      "clase": "A",
      "pct_acum": 32.8,
      "unidades": 12,
      "venta": 372.0,
      "margen_unitario": 8.68,
      "margen_total": 104.16,
      "costo_estimado": true,
      "existencia": 12,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.13,
      "cobertura_dias": 90.0,
      "rotacion": 1.0,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 90 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 34,
        "clave_interna": "LA-006",
        "nombre": "Yogur natural"
      },
      "categoria": "Lácteos y huevo",
      "clase": "A",
      "pct_acum": 35.7,
      "unidades": 12,
      "venta": 528.0,
      "margen_unitario": 12.32,
      "margen_total": 147.84,
      "costo_estimado": true,
      "existencia": 10,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.13,
      "cobertura_dias": 75.0,
      "rotacion": 1.2,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 75 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 42,
        "clave_interna": "LI-006",
        "nombre": "Papel higiénico"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 38.6,
      "unidades": 12,
      "venta": 456.0,
      "margen_unitario": 10.64,
      "margen_total": 127.68,
      "costo_estimado": true,
      "existencia": 64,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.13,
      "cobertura_dias": 480.0,
      "rotacion": 0.19,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 480 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 39,
        "clave_interna": "LI-003",
        "nombre": "Cloro"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 41.3,
      "unidades": 11,
      "venta": 214.5,
      "margen_unitario": 5.46,
      "margen_total": 60.06,
      "costo_estimado": true,
      "existencia": 44,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.12,
      "cobertura_dias": 360.0,
      "rotacion": 0.25,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 360 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 43,
        "clave_interna": "LI-007",
        "nombre": "Servilletas"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 43.7,
      "unidades": 10,
      "venta": 320.0,
      "margen_unitario": 8.96,
      "margen_total": 89.6,
      "costo_estimado": true,
      "existencia": 65,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.11,
      "cobertura_dias": 585.0,
      "rotacion": 0.15,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 585 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 2,
        "clave_interna": "AB-002",
        "nombre": "Arroz superextra"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 45.9,
      "unidades": 9,
      "venta": 269.1,
      "margen_unitario": 8.37,
      "margen_total": 75.33,
      "costo_estimado": true,
      "existencia": 36,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 360.0,
      "rotacion": 0.25,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 360 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 11,
        "clave_interna": "AB-011",
        "nombre": "Frijoles refritos"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 48.1,
      "unidades": 9,
      "venta": 207.0,
      "margen_unitario": 6.44,
      "margen_total": 57.96,
      "costo_estimado": true,
      "existencia": 27,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 270.0,
      "rotacion": 0.33,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 270 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 12,
        "clave_interna": "AB-012",
        "nombre": "Chiles jalapeños en escabeche"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 50.2,
      "unidades": 9,
      "venta": 175.5,
      "margen_unitario": 5.46,
      "margen_total": 49.14,
      "costo_estimado": true,
      "existencia": 392,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 3920.0,
      "rotacion": 0.02,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 3920 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 19,
        "clave_interna": "AB-019",
        "nombre": "Huevo blanco"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 52.4,
      "unidades": 9,
      "venta": 378.0,
      "margen_unitario": 11.76,
      "margen_total": 105.84,
      "costo_estimado": true,
      "existencia": 49,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 490.0,
      "rotacion": 0.18,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 490 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 44,
        "clave_interna": "LI-008",
        "nombre": "Bolsas para basura"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 54.6,
      "unidades": 9,
      "venta": 216.0,
      "margen_unitario": 6.72,
      "margen_total": 60.48,
      "costo_estimado": true,
      "existencia": 26,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 260.0,
      "rotacion": 0.35,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 260 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 1,
        "clave_interna": "AB-001",
        "nombre": "Frijol negro a granel"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 56.6,
      "unidades": 8,
      "venta": 308.0,
      "margen_unitario": 10.78,
      "margen_total": 86.24,
      "costo_estimado": true,
      "existencia": 58,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 652.5,
      "rotacion": 0.14,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 652 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 6,
        "clave_interna": "AB-006",
        "nombre": "Harina de maíz nixtamalizado"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 58.5,
      "unidades": 8,
      "venta": 208.0,
      "margen_unitario": 7.28,
      "margen_total": 58.24,
      "costo_estimado": true,
      "existencia": 81,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 911.2,
      "rotacion": 0.1,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 911 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 24,
        "clave_interna": "BE-004",
        "nombre": "Refresco sabor manzana"
      },
      "categoria": "Bebidas",
      "clase": "A",
      "pct_acum": 60.4,
      "unidades": 8,
      "venta": 288.0,
      "margen_unitario": 10.08,
      "margen_total": 80.64,
      "costo_estimado": true,
      "existencia": 39,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 438.8,
      "rotacion": 0.21,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 439 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 27,
        "clave_interna": "BE-007",
        "nombre": "Té helado de limón"
      },
      "categoria": "Bebidas",
      "clase": "A",
      "pct_acum": 62.4,
      "unidades": 8,
      "venta": 136.0,
      "margen_unitario": 4.76,
      "margen_total": 38.08,
      "costo_estimado": true,
      "existencia": 84,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 945.0,
      "rotacion": 0.1,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 945 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 29,
        "clave_interna": "LA-001",
        "nombre": "Leche entera"
      },
      "categoria": "Lácteos y huevo",
      "clase": "A",
      "pct_acum": 64.3,
      "unidades": 8,
      "venta": 220.0,
      "margen_unitario": 7.7,
      "margen_total": 61.6,
      "costo_estimado": true,
      "existencia": 48,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 540.0,
      "rotacion": 0.17,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 540 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 40,
        "clave_interna": "LI-004",
        "nombre": "Limpiador multiusos"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 66.3,
      "unidades": 8,
      "venta": 224.0,
      "margen_unitario": 7.84,
      "margen_total": 62.72,
      "costo_estimado": true,
      "existencia": 14,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 157.5,
      "rotacion": 0.57,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 158 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 51,
        "clave_interna": "HI-006",
        "nombre": "Pañal etapa 3"
      },
      "categoria": "Higiene personal",
      "clase": "A",
      "pct_acum": 68.2,
      "unidades": 8,
      "venta": 544.0,
      "margen_unitario": 19.04,
      "margen_total": 152.32,
      "costo_estimado": true,
      "existencia": 29,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 326.2,
      "rotacion": 0.28,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 326 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 5,
        "clave_interna": "AB-005",
        "nombre": "Sal de mesa"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 69.9,
      "unidades": 7,
      "venta": 98.0,
      "margen_unitario": 3.92,
      "margen_total": 27.44,
      "costo_estimado": true,
      "existencia": 30,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 385.7,
      "rotacion": 0.23,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 386 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 8,
        "clave_interna": "AB-008",
        "nombre": "Pasta para sopa surtida"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 71.6,
      "unidades": 7,
      "venta": 66.5,
      "margen_unitario": 2.66,
      "margen_total": 18.62,
      "costo_estimado": true,
      "existencia": 21,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 270.0,
      "rotacion": 0.33,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 270 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 10,
        "clave_interna": "AB-010",
        "nombre": "Sardina en salsa de tomate"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 73.3,
      "unidades": 7,
      "venta": 185.5,
      "margen_unitario": 7.42,
      "margen_total": 51.94,
      "costo_estimado": true,
      "existencia": 690,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 8871.4,
      "rotacion": 0.01,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 8871 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 14,
        "clave_interna": "AB-014",
        "nombre": "Café soluble"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 75.0,
      "unidades": 7,
      "venta": 364.0,
      "margen_unitario": 14.56,
      "margen_total": 101.92,
      "costo_estimado": true,
      "existencia": 33,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 424.3,
      "rotacion": 0.21,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 424 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 18,
        "clave_interna": "AB-018",
        "nombre": "Pan de caja blanco"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 76.7,
      "unidades": 7,
      "venta": 308.0,
      "margen_unitario": 12.32,
      "margen_total": 86.24,
      "costo_estimado": true,
      "existencia": 80,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 1028.6,
      "rotacion": 0.09,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1029 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 47,
        "clave_interna": "HI-002",
        "nombre": "Shampoo"
      },
      "categoria": "Higiene personal",
      "clase": "A",
      "pct_acum": 78.4,
      "unidades": 7,
      "venta": 378.0,
      "margen_unitario": 15.12,
      "margen_total": 105.84,
      "costo_estimado": true,
      "existencia": 60,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 771.4,
      "rotacion": 0.12,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 771 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 49,
        "clave_interna": "HI-004",
        "nombre": "Desodorante"
      },
      "categoria": "Higiene personal",
      "clase": "A",
      "pct_acum": 80.1,
      "unidades": 7,
      "venta": 336.0,
      "margen_unitario": 13.44,
      "margen_total": 94.08,
      "costo_estimado": true,
      "existencia": 36,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 462.9,
      "rotacion": 0.19,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 463 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    }
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 80.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 95.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 7.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 5.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 90.0,
      "modificado": false
    }
  ]
}
```

### SUR-05 · Clase inventada · PASA

**Objetivo.** Solo A, B o C.

**Petición.** `GET http://surtido:5122/api/v1/surtido/analisis?microhub_id=1&clase=Z`

```http
Accept: application/json
X-Traza-Id: 1bee0ed0-6582-4c2f-80f6-0f88c219bb19
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 10 ms · traza `1bee0ed0-6582-4c2f-80f6-0f88c219bb19`

```json
{
  "error": {
    "codigo": "FILTRO_INVALIDO",
    "mensaje": "Valor no permitido para clase: Z.",
    "detalles": [
      {
        "campo": "clase",
        "mensaje": "Valor no permitido para clase: Z."
      }
    ],
    "traza_id": "1bee0ed0-6582-4c2f-80f6-0f88c219bb19"
  }
}
```

### SUR-06 · Análisis (XML) · PASA

**Objetivo.** Respuesta XML que cumple surtido.xsd.

**Petición.** `GET http://surtido:5122/api/v1/surtido/analisis?microhub_id=1`

```http
Accept: application/xml
X-Traza-Id: aecd9cc1-7cca-41fe-b767-b3a67c275959
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 412 ms · traza `aecd9cc1-7cca-41fe-b767-b3a67c275959`

```xml
<?xml version='1.0' encoding='utf-8'?>
<surtido_analisis xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><ventana_dias>90</ventana_dias><resumen><productos>51</productos><aumentar>1</aumentar><mantener>0</mantener><reducir>50</reducir><eliminar>0</eliminar><excluir>0</excluir><clase_a>32</clase_a><clase_b>13</clase_b><clase_c>6</clase_c><unidades_a_comprar>1</unidades_a_comprar><con_costo_estimado>51</con_costo_estimado><espacio><total>3600</total><ocupado>3301</ocupado><sugerido>1</sugerido><ocupacion_pct>91.7</ocupacion_pct></espacio><presupuesto><total>120000</total><requerido>27.36</requerido><uso_pct>0</uso_pct></presupuesto></resumen><filas><fila><producto><id>28</id><clave_interna>BE-008</clave_interna><nombre>Polvo para agua de sabor</nombre></producto><categoria>Bebidas</categoria><clase>A</clase><pct_acum>5.3</pct_acum><unidades>22</unidades><venta>165</venta><margen_unitario>2.1</margen_unitario><margen_total>46.2</margen_total><costo_estimado>true</costo_estimado><existencia>30</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.24</demanda_dia><cobertura_dias>122.7</cobertura_dias><rotacion>0.73</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 123 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>45</id><clave_interna>LI-009</clave_interna><nombre>Fibra para trastes</nombre></producto><categoria>Limpieza del hogar</categoria><clase>A</clase><pct_acum>9.2</pct_acum><unidades>16</unidades><venta>288</venta><margen_unitario>5.04</margen_unitario><margen_total>80.64</margen_total><costo_estimado>true</costo_estimado><existencia>43</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.18</demanda_dia><cobertura_dias>241.9</cobertura_dias><rotacion>0.37</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 242 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>7</id><clave_interna>AB-007</clave_interna><nombre>Harina de trigo</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>12.9</pct_acum><unidades>15</unidades><venta>367.5</venta><margen_unitario>6.86</margen_unitario><margen_total>102.9</margen_total><costo_estimado>true</costo_estimado><existencia>14</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.17</demanda_dia><cobertura_dias>84</cobertura_dias><rotacion>1.07</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 84 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>25</id><clave_interna>BE-005</clave_interna><nombre>Jugo de naranja</nombre></producto><categoria>Bebidas</categoria><clase>A</clase><pct_acum>16.5</pct_acum><unidades>15</unidades><venta>420</venta><margen_unitario>7.84</margen_unitario><margen_total>117.6</margen_total><costo_estimado>true</costo_estimado><existencia>80</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.17</demanda_dia><cobertura_dias>480</cobertura_dias><rotacion>0.19</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 480 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>48</id><clave_interna>HI-003</clave_interna><nombre>Pasta dental</nombre></producto><categoria>Higiene personal</categoria><clase>A</clase><pct_acum>20.1</pct_acum><unidades>15</unidades><venta>480</venta><margen_unitario>8.96</margen_unitario><margen_total>134.4</margen_total><costo_estimado>true</costo_estimado><existencia>74</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.17</demanda_dia><cobertura_dias>444</cobertura_dias><rotacion>0.2</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 444 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>13</id><clave_interna>AB-013</clave_interna><nombre>Puré de tomate</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>23.5</pct_acum><unidades>14</unidades><venta>154</venta><margen_unitario>3.08</margen_unitario><margen_total>43.12</margen_total><costo_estimado>true</costo_estimado><existencia>56</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.16</demanda_dia><cobertura_dias>360</cobertura_dias><rotacion>0.25</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 360 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>20</id><clave_interna>AB-020</clave_interna><nombre>Lenteja</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>26.7</pct_acum><unidades>13</unidades><venta>312</venta><margen_unitario>6.72</margen_unitario><margen_total>87.36</margen_total><costo_estimado>true</costo_estimado><existencia>73</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.14</demanda_dia><cobertura_dias>505.4</cobertura_dias><rotacion>0.18</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 505 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>36</id><clave_interna>LA-008</clave_interna><nombre>Jamón de pavo</nombre></producto><categoria>Lácteos y huevo</categoria><clase>A</clase><pct_acum>29.9</pct_acum><unidades>13</unidades><venta>598</venta><margen_unitario>12.88</margen_unitario><margen_total>167.44</margen_total><costo_estimado>true</costo_estimado><existencia>47</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.14</demanda_dia><cobertura_dias>325.4</cobertura_dias><rotacion>0.28</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 325 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>30</id><clave_interna>LA-002</clave_interna><nombre>Leche deslactosada</nombre></producto><categoria>Lácteos y huevo</categoria><clase>A</clase><pct_acum>32.8</pct_acum><unidades>12</unidades><venta>372</venta><margen_unitario>8.68</margen_unitario><margen_total>104.16</margen_total><costo_estimado>true</costo_estimado><existencia>12</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.13</demanda_dia><cobertura_dias>90</cobertura_dias><rotacion>1</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 90 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>34</id><clave_interna>LA-006</clave_interna><nombre>Yogur natural</nombre></producto><categoria>Lácteos y huevo</categoria><clase>A</clase><pct_acum>35.7</pct_acum><unidades>12</unidades><venta>528</venta><margen_unitario>12.32</margen_unitario><margen_total>147.84</margen_total><costo_estimado>true</costo_estimado><existencia>10</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.13</demanda_dia><cobertura_dias>75</cobertura_dias><rotacion>1.2</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 75 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>42</id><clave_interna>LI-006</clave_interna><nombre>Papel higiénico</nombre></producto><categoria>Limpieza del hogar</categoria><clase>A</clase><pct_acum>38.6</pct_acum><unidades>12</unidades><venta>456</venta><margen_unitario>10.64</margen_unitario><margen_total>127.68</margen_total><costo_estimado>true</costo_estimado><existencia>64</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.13</demanda_dia><cobertura_dias>480</cobertura_dias><rotacion>0.19</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 480 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>39</id><clave_interna>LI-003</clave_interna><nombre>Cloro</nombre></producto><categoria>Limpieza del hogar</categoria><clase>A</clase><pct_acum>41.3</pct_acum><unidades>11</unidades><venta>214.5</venta><margen_unitario>5.46</margen_unitario><margen_total>60.06</margen_total><costo_estimado>true</costo_estimado><existencia>44</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.12</demanda_dia><cobertura_dias>360</cobertura_dias><rotacion>0.25</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 360 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>43</id><clave_interna>LI-007</clave_interna><nombre>Servilletas</nombre></producto><categoria>Limpieza del hogar</categoria><clase>A</clase><pct_acum>43.7</pct_acum><unidades>10</unidades><venta>320</venta><margen_unitario>8.96</margen_unitario><margen_total>89.6</margen_total><costo_estimado>true</costo_estimado><existencia>65</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.11</demanda_dia><cobertura_dias>585</cobertura_dias><rotacion>0.15</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 585 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>2</id><clave_interna>AB-002</clave_interna><nombre>Arroz superextra</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>45.9</pct_acum><unidades>9</unidades><venta>269.1</venta><margen_unitario>8.37</margen_unitario><margen_total>75.33</margen_total><costo_estimado>true</costo_estimado><existencia>36</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.1</demanda_dia><cobertura_dias>360</cobertura_dias><rotacion>0.25</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 360 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>11</id><clave_interna>AB-011</clave_interna><nombre>Frijoles refritos</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>48.1</pct_acum><unidades>9</unidades><venta>207</venta><margen_unitario>6.44</margen_unitario><margen_total>57.96</margen_total><costo_estimado>true</costo_estimado><existencia>27</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.1</demanda_dia><cobertura_dias>270</cobertura_dias><rotacion>0.33</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 270 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>12</id><clave_interna>AB-012</clave_interna><nombre>Chiles jalapeños en escabeche</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>50.2</pct_acum><unidades>9</unidades><venta>175.5</venta><margen_unitario>5.46</margen_unitario><margen_total>49.14</margen_total><costo_estimado>true</costo_estimado><existencia>392</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.1</demanda_dia><cobertura_dias>3920</cobertura_dias><rotacion>0.02</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 3920 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>19</id><clave_interna>AB-019</clave_interna><nombre>Huevo blanco</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>52.4</pct_acum><unidades>9</unidades><venta>378</venta><margen_unitario>11.76</margen_unitario><margen_total>105.84</margen_total><costo_estimado>true</costo_estimado><existencia>49</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.1</demanda_dia><cobertura_dias>490</cobertura_dias><rotacion>0.18</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 490 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>44</id><clave_interna>LI-008</clave_interna><nombre>Bolsas para basura</nombre></producto><categoria>Limpieza del hogar</categoria><clase>A</clase><pct_acum>54.6</pct_acum><unidades>9</unidades><venta>216</venta><margen_unitario>6.72</margen_unitario><margen_total>60.48</margen_total><costo_estimado>true</costo_estimado><existencia>26</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.1</demanda_dia><cobertura_dias>260</cobertura_dias><rotacion>0.35</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 260 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>1</id><clave_interna>AB-001</clave_interna><nombre>Frijol negro a granel</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>56.6</pct_acum><unidades>8</unidades><venta>308</venta><margen_unitario>10.78</margen_unitario><margen_total>86.24</margen_total><costo_estimado>true</costo_estimado><existencia>58</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.09</demanda_dia><cobertura_dias>652.5</cobertura_dias><rotacion>0.14</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 652 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>6</id><clave_interna>AB-006</clave_interna><nombre>Harina de maíz nixtamalizado</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>58.5</pct_acum><unidades>8</unidades><venta>208</venta><margen_unitario>7.28</margen_unitario><margen_total>58.24</margen_total><costo_estimado>true</costo_estimado><existencia>81</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.09</demanda_dia><cobertura_dias>911.2</cobertura_dias><rotacion>0.1</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 911 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>24</id><clave_interna>BE-004</clave_interna><nombre>Refresco sabor manzana</nombre></producto><categoria>Bebidas</categoria><clase>A</clase><pct_acum>60.4</pct_acum><unidades>8</unidades><venta>288</venta><margen_unitario>10.08</margen_unitario><margen_total>80.64</margen_total><costo_estimado>true</costo_estimado><existencia>39</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.09</demanda_dia><cobertura_dias>438.8</cobertura_dias><rotacion>0.21</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 439 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>27</id><clave_interna>BE-007</clave_interna><nombre>Té helado de limón</nombre></producto><categoria>Bebidas</categoria><clase>A</clase><pct_acum>62.4</pct_acum><unidades>8</unidades><venta>136</venta><margen_unitario>4.76</margen_unitario><margen_total>38.08</margen_total><costo_estimado>true</costo_estimado><existencia>84</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.09</demanda_dia><cobertura_dias>945</cobertura_dias><rotacion>0.1</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 945 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>29</id><clave_interna>LA-001</clave_interna><nombre>Leche entera</nombre></producto><categoria>Lácteos y huevo</categoria><clase>A</clase><pct_acum>64.3</pct_acum><unidades>8</unidades><venta>220</venta><margen_unitario>7.7</margen_unitario><margen_total>61.6</margen_total><costo_estimado>true</costo_estimado><existencia>48</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.09</demanda_dia><cobertura_dias>540</cobertura_dias><rotacion>0.17</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 540 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>40</id><clave_interna>LI-004</clave_interna><nombre>Limpiador multiusos</nombre></producto><categoria>Limpieza del hogar</categoria><clase>A</clase><pct_acum>66.3</pct_acum><unidades>8</unidades><venta>224</venta><margen_unitario>7.84</margen_unitario><margen_total>62.72</margen_total><costo_estimado>true</costo_estimado><existencia>14</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.09</demanda_dia><cobertura_dias>157.5</cobertura_dias><rotacion>0.57</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 158 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>51</id><clave_interna>HI-006</clave_interna><nombre>Pañal etapa 3</nombre></producto><categoria>Higiene personal</categoria><clase>A</clase><pct_acum>68.2</pct_acum><unidades>8</unidades><venta>544</venta><margen_unitario>19.04</margen_unitario><margen_total>152.32</margen_total><costo_estimado>true</costo_estimado><existencia>29</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.09</demanda_dia><cobertura_dias>326.2</cobertura_dias><rotacion>0.28</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 326 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>5</id><clave_interna>AB-005</clave_interna><nombre>Sal de mesa</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>69.9</pct_acum><unidades>7</unidades><venta>98</venta><margen_unitario>3.92</margen_unitario><margen_total>27.44</margen_total><costo_estimado>true</costo_estimado><existencia>30</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.08</demanda_dia><cobertura_dias>385.7</cobertura_dias><rotacion>0.23</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 386 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>8</id><clave_interna>AB-008</clave_interna><nombre>Pasta para sopa surtida</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>71.6</pct_acum><unidades>7</unidades><venta>66.5</venta><margen_unitario>2.66</margen_unitario><margen_total>18.62</margen_total><costo_estimado>true</costo_estimado><existencia>21</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.08</demanda_dia><cobertura_dias>270</cobertura_dias><rotacion>0.33</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 270 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>10</id><clave_interna>AB-010</clave_interna><nombre>Sardina en salsa de tomate</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>73.3</pct_acum><unidades>7</unidades><venta>185.5</venta><margen_unitario>7.42</margen_unitario><margen_total>51.94</margen_total><costo_estimado>true</costo_estimado><existencia>690</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.08</demanda_dia><cobertura_dias>8871.4</cobertura_dias><rotacion>0.01</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 8871 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>14</id><clave_interna>AB-014</clave_interna><nombre>Café soluble</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>75</pct_acum><unidades>7</unidades><venta>364</venta><margen_unitario>14.56</margen_unitario><margen_total>101.92</margen_total><costo_estimado>true</costo_estimado><existencia>33</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.08</demanda_dia><cobertura_dias>424.3</cobertura_dias><rotacion>0.21</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 424 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>18</id><clave_interna>AB-018</clave_interna><nombre>Pan de caja blanco</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>76.7</pct_acum><unidades>7</unidades><venta>308</venta><margen_unitario>12.32</margen_unitario><margen_total>86.24</margen_total><costo_estimado>true</costo_estimado><existencia>80</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.08</demanda_dia><cobertura_dias>1028.6</cobertura_dias><rotacion>0.09</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1029 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>47</id><clave_interna>HI-002</clave_interna><nombre>Shampoo</nombre></producto><categoria>Higiene personal</categoria><clase>A</clase><pct_acum>78.4</pct_acum><unidades>7</unidades><venta>378</venta><margen_unitario>15.12</margen_unitario><margen_total>105.84</margen_total><costo_estimado>true</costo_estimado><existencia>60</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.08</demanda_dia><cobertura_dias>771.4</cobertura_dias><rotacion>0.12</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 771 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>49</id><clave_interna>HI-004</clave_interna><nombre>Desodorante</nombre></producto><categoria>Higiene personal</categoria><clase>A</clase><pct_acum>80.1</pct_acum><unidades>7</unidades><venta>336</venta><margen_unitario>13.44</margen_unitario><margen_total>94.08</margen_total><costo_estimado>true</costo_estimado><existencia>36</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.08</demanda_dia><cobertura_dias>462.9</cobertura_dias><rotacion>0.19</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 463 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>3</id><clave_interna>AB-003</clave_interna><nombre>Aceite vegetal</nombre></producto><categoria>Abarrote básico</categoria><clase>B</clase><pct_acum>81.6</pct_acum><unidades>6</unidades><venta>252</venta><margen_unitario>11.76</margen_unitario><margen_total>70.56</margen_total><costo_estimado>true</costo_estimado><existencia>10</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.07</demanda_dia><cobertura_dias>150</cobertura_dias><rotacion>0.6</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 150 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>17</id><clave_interna>AB-017</clave_interna><nombre>Tortillas de maíz</nombre></producto><categoria>Abarrote básico</categoria><clase>B</clase><pct_acum>83</pct_acum><unidades>6</unidades><venta>144</venta><margen_unitario>6.72</margen_unitario><margen_total>40.32</margen_total><costo_estimado>true</costo_estimado><existencia>21</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.07</demanda_dia><cobertura_dias>315</cobertura_dias><rotacion>0.29</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 315 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>26</id><clave_interna>BE-006</clave_interna><nombre>Bebida de soya</nombre></producto><categoria>Bebidas</categoria><clase>B</clase><pct_acum>84.5</pct_acum><unidades>6</unidades><venta>192</venta><margen_unitario>8.96</margen_unitario><margen_total>53.76</margen_total><costo_estimado>true</costo_estimado><existencia>17</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.07</demanda_dia><cobertura_dias>255</cobertura_dias><rotacion>0.35</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 255 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>16</id><clave_interna>AB-016</clave_interna><nombre>Galletas María</nombre></producto><categoria>Abarrote básico</categoria><clase>B</clase><pct_acum>85.7</pct_acum><unidades>5</unidades><venta>82.5</venta><margen_unitario>4.62</margen_unitario><margen_total>23.1</margen_total><costo_estimado>true</costo_estimado><existencia>81</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>1458</cobertura_dias><rotacion>0.06</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1458 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>22</id><clave_interna>BE-002</clave_interna><nombre>Agua embotellada</nombre></producto><categoria>Bebidas</categoria><clase>B</clase><pct_acum>86.9</pct_acum><unidades>5</unidades><venta>75</venta><margen_unitario>4.2</margen_unitario><margen_total>21</margen_total><costo_estimado>true</costo_estimado><existencia>72</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>1296</cobertura_dias><rotacion>0.07</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1296 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>23</id><clave_interna>BE-003</clave_interna><nombre>Refresco de cola</nombre></producto><categoria>Bebidas</categoria><clase>B</clase><pct_acum>88.1</pct_acum><unidades>5</unidades><venta>192.5</venta><margen_unitario>10.78</margen_unitario><margen_total>53.9</margen_total><costo_estimado>true</costo_estimado><existencia>54</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>972</cobertura_dias><rotacion>0.09</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 972 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>35</id><clave_interna>LA-007</clave_interna><nombre>Mantequilla</nombre></producto><categoria>Lácteos y huevo</categoria><clase>B</clase><pct_acum>89.3</pct_acum><unidades>5</unidades><venta>110</venta><margen_unitario>6.16</margen_unitario><margen_total>30.8</margen_total><costo_estimado>true</costo_estimado><existencia>64</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>1152</cobertura_dias><rotacion>0.08</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1152 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>41</id><clave_interna>LI-005</clave_interna><nombre>Suavizante de telas</nombre></producto><categoria>Limpieza del hogar</categoria><clase>B</clase><pct_acum>90.5</pct_acum><unidades>5</unidades><venta>165</venta><margen_unitario>9.24</margen_unitario><margen_total>46.2</margen_total><costo_estimado>true</costo_estimado><existencia>69</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>1242</cobertura_dias><rotacion>0.07</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1242 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>46</id><clave_interna>HI-001</clave_interna><nombre>Jabón de tocador</nombre></producto><categoria>Higiene personal</categoria><clase>B</clase><pct_acum>91.7</pct_acum><unidades>5</unidades><venta>72.5</venta><margen_unitario>4.06</margen_unitario><margen_total>20.3</margen_total><costo_estimado>true</costo_estimado><existencia>63</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>1134</cobertura_dias><rotacion>0.08</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1134 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>50</id><clave_interna>HI-005</clave_interna><nombre>Toallas femeninas</nombre></producto><categoria>Higiene personal</categoria><clase>B</clase><pct_acum>93</pct_acum><unidades>5</unidades><venta>180</venta><margen_unitario>10.08</margen_unitario><margen_total>50.4</margen_total><costo_estimado>true</costo_estimado><existencia>76</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>1368</cobertura_dias><rotacion>0.07</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1368 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>4</id><clave_interna>AB-004</clave_interna><nombre>Azúcar estándar</nombre></producto><categoria>Abarrote básico</categoria><clase>B</clase><pct_acum>93.9</pct_acum><unidades>4</unidades><venta>114</venta><margen_unitario>7.98</margen_unitario><margen_total>31.92</margen_total><costo_estimado>true</costo_estimado><existencia>18</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.04</demanda_dia><cobertura_dias>405</cobertura_dias><rotacion>0.22</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 405 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>15</id><clave_interna>AB-015</clave_interna><nombre>Avena en hojuelas</nombre></producto><categoria>Abarrote básico</categoria><clase>B</clase><pct_acum>94.9</pct_acum><unidades>4</unidades><venta>108</venta><margen_unitario>7.56</margen_unitario><margen_total>30.24</margen_total><costo_estimado>true</costo_estimado><existencia>52</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.04</demanda_dia><cobertura_dias>1170</cobertura_dias><rotacion>0.08</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1170 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>32</id><clave_interna>LA-004</clave_interna><nombre>Queso Oaxaca</nombre></producto><categoria>Lácteos y huevo</categoria><clase>B</clase><pct_acum>95.9</pct_acum><unidades>4</unidades><venta>288</venta><margen_unitario>20.16</margen_unitario><margen_total>80.64</margen_total><costo_estimado>true</costo_estimado><existencia>20</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.04</demanda_dia><cobertura_dias>450</cobertura_dias><rotacion>0.2</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 450 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>33</id><clave_interna>LA-005</clave_interna><nombre>Crema ácida</nombre></producto><categoria>Lácteos y huevo</categoria><clase>C</clase><pct_acum>96.8</pct_acum><unidades>4</unidades><venta>144</venta><margen_unitario>10.08</margen_unitario><margen_total>40.32</margen_total><costo_estimado>true</costo_estimado><existencia>82</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.04</demanda_dia><cobertura_dias>1845</cobertura_dias><rotacion>0.05</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1845 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>37</id><clave_interna>LI-001</clave_interna><nombre>Detergente en polvo</nombre></producto><categoria>Limpieza del hogar</categoria><clase>C</clase><pct_acum>97.8</pct_acum><unidades>4</unidades><venta>168</venta><margen_unitario>11.76</margen_unitario><margen_total>47.04</margen_total><costo_estimado>true</costo_estimado><existencia>13</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.04</demanda_dia><cobertura_dias>292.5</cobertura_dias><rotacion>0.31</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 292 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>9</id><clave_interna>AB-009</clave_interna><nombre>Atún en agua</nombre></producto><categoria>Abarrote básico</categoria><clase>C</clase><pct_acum>98.5</pct_acum><unidades>3</unidades><venta>63</venta><margen_unitario>5.88</margen_unitario><margen_total>17.64</margen_total><costo_estimado>true</costo_estimado><existencia>42</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.03</demanda_dia><cobertura_dias>1260</cobertura_dias><rotacion>0.07</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1260 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>38</id><clave_interna>LI-002</clave_interna><nombre>Jabón para trastes</nombre></producto><categoria>Limpieza del hogar</categoria><clase>C</clase><pct_acum>99.3</pct_acum><unidades>3</unidades><venta>78</venta><margen_unitario>7.28</margen_unitario><margen_total>21.84</margen_total><costo_estimado>true</costo_estimado><existencia>47</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.03</demanda_dia><cobertura_dias>1410</cobertura_dias><rotacion>0.06</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1410 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>31</id><clave_interna>LA-003</clave_interna><nombre>Queso fresco</nombre></producto><categoria>Lácteos y huevo</categoria><clase>C</clase><pct_acum>99.8</pct_acum><unidades>2</unidades><venta>116</venta><margen_unitario>16.24</margen_unitario><margen_total>32.48</margen_total><costo_estimado>true</costo_estimado><existencia>55</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.02</demanda_dia><cobertura_dias>2475</cobertura_dias><rotacion>0.04</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 2475 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>21</id><clave_interna>BE-001</clave_interna><nombre>Agua purificada</nombre></producto><categoria>Bebidas</categoria><clase>C</clase><pct_acum>100</pct_acum><unidades>1</unidades><venta>38</venta><margen_unitario>10.64</margen_unitario><margen_total>10.64</margen_total><costo_estimado>true</costo_estimado><existencia>0</existencia><minimo>10</minimo><quiebres>2</quiebres><demanda_dia>0.01</demanda_dia><cobertura_dias>0</cobertura_dias><rotacion>99</rotacion><recomendacion>Aumentar</recomendacion><motivo>hubo quiebres</motivo><sugerido>1</sugerido><limitado_por xsi:nil="true" /></fila></filas><supuestos_usados><supuesto><clave>abc_a_pct</clave><valor>80</valor><modificado>false</modificado></supuesto><supuesto><clave>abc_b_pct</clave><valor>95</valor><modificado>false</modificado></supuesto><supuesto><clave>cobertura_dias_a</clave><valor>7</valor><modificado>false</modificado></supuesto><supuesto><clave>cobertura_dias_b</clave><valor>5</valor><modificado>false</modificado></supuesto><supuesto><clave>cobertura_dias_c</clave><valor>3</valor><modificado>false</modificado></supuesto><supuesto><clave>cobertura_dias_exceso</clave><valor>30</valor><modificado>false</modificado></supuesto><supuesto><clave>ventana_analisis_dias</clave><valor>90</valor><modificado>false</modificado></supuesto></supuestos_usados></surtido_analisis>
```

### SUR-07 · El operador analiza su microhub · PASA

**Objetivo.** Operador y supervisor solo trabajan con el suyo.

**Petición.** `GET http://surtido:5122/api/v1/surtido/analisis?microhub_id=1`

```http
Accept: application/json
X-Traza-Id: 4b16f021-9f82-47a8-9edb-b287c4b59c3a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 380 ms · traza `4b16f021-9f82-47a8-9edb-b287c4b59c3a`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "ventana_dias": 90,
  "resumen": {
    "productos": 51,
    "aumentar": 1,
    "mantener": 0,
    "reducir": 50,
    "eliminar": 0,
    "excluir": 0,
    "clase_a": 32,
    "clase_b": 13,
    "clase_c": 6,
    "unidades_a_comprar": 1,
    "con_costo_estimado": 51,
    "espacio": {
      "total": 3600.0,
      "ocupado": 3301.0,
      "sugerido": 1.0,
      "ocupacion_pct": 91.7
    },
    "presupuesto": {
      "total": 120000.0,
      "requerido": 27.36,
      "uso_pct": 0.0
    }
  },
  "filas": [
    {
      "producto": {
        "id": 28,
        "clave_interna": "BE-008",
        "nombre": "Polvo para agua de sabor"
      },
      "categoria": "Bebidas",
      "clase": "A",
      "pct_acum": 5.3,
      "unidades": 22,
      "venta": 165.0,
      "margen_unitario": 2.1,
      "margen_total": 46.2,
      "costo_estimado": true,
      "existencia": 30,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.24,
      "cobertura_dias": 122.7,
      "rotacion": 0.73,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 123 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 45,
        "clave_interna": "LI-009",
        "nombre": "Fibra para trastes"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 9.2,
      "unidades": 16,
      "venta": 288.0,
      "margen_unitario": 5.04,
      "margen_total": 80.64,
      "costo_estimado": true,
      "existencia": 43,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.18,
      "cobertura_dias": 241.9,
      "rotacion": 0.37,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 242 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 7,
        "clave_interna": "AB-007",
        "nombre": "Harina de trigo"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 12.9,
      "unidades": 15,
      "venta": 367.5,
      "margen_unitario": 6.86,
      "margen_total": 102.9,
      "costo_estimado": true,
      "existencia": 14,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.17,
      "cobertura_dias": 84.0,
      "rotacion": 1.07,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 84 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 25,
        "clave_interna": "BE-005",
        "nombre": "Jugo de naranja"
      },
      "categoria": "Bebidas",
      "clase": "A",
      "pct_acum": 16.5,
      "unidades": 15,
      "venta": 420.0,
      "margen_unitario": 7.84,
      "margen_total": 117.6,
      "costo_estimado": true,
      "existencia": 80,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.17,
      "cobertura_dias": 480.0,
      "rotacion": 0.19,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 480 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 48,
        "clave_interna": "HI-003",
        "nombre": "Pasta dental"
      },
      "categoria": "Higiene personal",
      "clase": "A",
      "pct_acum": 20.1,
      "unidades": 15,
      "venta": 480.0,
      "margen_unitario": 8.96,
      "margen_total": 134.4,
      "costo_estimado": true,
      "existencia": 74,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.17,
      "cobertura_dias": 444.0,
      "rotacion": 0.2,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 444 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 13,
        "clave_interna": "AB-013",
        "nombre": "Puré de tomate"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 23.5,
      "unidades": 14,
      "venta": 154.0,
      "margen_unitario": 3.08,
      "margen_total": 43.12,
      "costo_estimado": true,
      "existencia": 56,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.16,
      "cobertura_dias": 360.0,
      "rotacion": 0.25,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 360 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 20,
        "clave_interna": "AB-020",
        "nombre": "Lenteja"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 26.7,
      "unidades": 13,
      "venta": 312.0,
      "margen_unitario": 6.72,
      "margen_total": 87.36,
      "costo_estimado": true,
      "existencia": 73,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.14,
      "cobertura_dias": 505.4,
      "rotacion": 0.18,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 505 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 36,
        "clave_interna": "LA-008",
        "nombre": "Jamón de pavo"
      },
      "categoria": "Lácteos y huevo",
      "clase": "A",
      "pct_acum": 29.9,
      "unidades": 13,
      "venta": 598.0,
      "margen_unitario": 12.88,
      "margen_total": 167.44,
      "costo_estimado": true,
      "existencia": 47,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.14,
      "cobertura_dias": 325.4,
      "rotacion": 0.28,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 325 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 30,
        "clave_interna": "LA-002",
        "nombre": "Leche deslactosada"
      },
      "categoria": "Lácteos y huevo",
      "clase": "A",
      "pct_acum": 32.8,
      "unidades": 12,
      "venta": 372.0,
      "margen_unitario": 8.68,
      "margen_total": 104.16,
      "costo_estimado": true,
      "existencia": 12,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.13,
      "cobertura_dias": 90.0,
      "rotacion": 1.0,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 90 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 34,
        "clave_interna": "LA-006",
        "nombre": "Yogur natural"
      },
      "categoria": "Lácteos y huevo",
      "clase": "A",
      "pct_acum": 35.7,
      "unidades": 12,
      "venta": 528.0,
      "margen_unitario": 12.32,
      "margen_total": 147.84,
      "costo_estimado": true,
      "existencia": 10,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.13,
      "cobertura_dias": 75.0,
      "rotacion": 1.2,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 75 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 42,
        "clave_interna": "LI-006",
        "nombre": "Papel higiénico"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 38.6,
      "unidades": 12,
      "venta": 456.0,
      "margen_unitario": 10.64,
      "margen_total": 127.68,
      "costo_estimado": true,
      "existencia": 64,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.13,
      "cobertura_dias": 480.0,
      "rotacion": 0.19,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 480 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 39,
        "clave_interna": "LI-003",
        "nombre": "Cloro"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 41.3,
      "unidades": 11,
      "venta": 214.5,
      "margen_unitario": 5.46,
      "margen_total": 60.06,
      "costo_estimado": true,
      "existencia": 44,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.12,
      "cobertura_dias": 360.0,
      "rotacion": 0.25,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 360 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 43,
        "clave_interna": "LI-007",
        "nombre": "Servilletas"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 43.7,
      "unidades": 10,
      "venta": 320.0,
      "margen_unitario": 8.96,
      "margen_total": 89.6,
      "costo_estimado": true,
      "existencia": 65,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.11,
      "cobertura_dias": 585.0,
      "rotacion": 0.15,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 585 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 2,
        "clave_interna": "AB-002",
        "nombre": "Arroz superextra"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 45.9,
      "unidades": 9,
      "venta": 269.1,
      "margen_unitario": 8.37,
      "margen_total": 75.33,
      "costo_estimado": true,
      "existencia": 36,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 360.0,
      "rotacion": 0.25,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 360 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 11,
        "clave_interna": "AB-011",
        "nombre": "Frijoles refritos"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 48.1,
      "unidades": 9,
      "venta": 207.0,
      "margen_unitario": 6.44,
      "margen_total": 57.96,
      "costo_estimado": true,
      "existencia": 27,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 270.0,
      "rotacion": 0.33,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 270 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 12,
        "clave_interna": "AB-012",
        "nombre": "Chiles jalapeños en escabeche"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 50.2,
      "unidades": 9,
      "venta": 175.5,
      "margen_unitario": 5.46,
      "margen_total": 49.14,
      "costo_estimado": true,
      "existencia": 392,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 3920.0,
      "rotacion": 0.02,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 3920 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 19,
        "clave_interna": "AB-019",
        "nombre": "Huevo blanco"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 52.4,
      "unidades": 9,
      "venta": 378.0,
      "margen_unitario": 11.76,
      "margen_total": 105.84,
      "costo_estimado": true,
      "existencia": 49,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 490.0,
      "rotacion": 0.18,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 490 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 44,
        "clave_interna": "LI-008",
        "nombre": "Bolsas para basura"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 54.6,
      "unidades": 9,
      "venta": 216.0,
      "margen_unitario": 6.72,
      "margen_total": 60.48,
      "costo_estimado": true,
      "existencia": 26,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 260.0,
      "rotacion": 0.35,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 260 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 1,
        "clave_interna": "AB-001",
        "nombre": "Frijol negro a granel"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 56.6,
      "unidades": 8,
      "venta": 308.0,
      "margen_unitario": 10.78,
      "margen_total": 86.24,
      "costo_estimado": true,
      "existencia": 58,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 652.5,
      "rotacion": 0.14,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 652 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 6,
        "clave_interna": "AB-006",
        "nombre": "Harina de maíz nixtamalizado"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 58.5,
      "unidades": 8,
      "venta": 208.0,
      "margen_unitario": 7.28,
      "margen_total": 58.24,
      "costo_estimado": true,
      "existencia": 81,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 911.2,
      "rotacion": 0.1,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 911 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 24,
        "clave_interna": "BE-004",
        "nombre": "Refresco sabor manzana"
      },
      "categoria": "Bebidas",
      "clase": "A",
      "pct_acum": 60.4,
      "unidades": 8,
      "venta": 288.0,
      "margen_unitario": 10.08,
      "margen_total": 80.64,
      "costo_estimado": true,
      "existencia": 39,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 438.8,
      "rotacion": 0.21,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 439 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 27,
        "clave_interna": "BE-007",
        "nombre": "Té helado de limón"
      },
      "categoria": "Bebidas",
      "clase": "A",
      "pct_acum": 62.4,
      "unidades": 8,
      "venta": 136.0,
      "margen_unitario": 4.76,
      "margen_total": 38.08,
      "costo_estimado": true,
      "existencia": 84,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 945.0,
      "rotacion": 0.1,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 945 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 29,
        "clave_interna": "LA-001",
        "nombre": "Leche entera"
      },
      "categoria": "Lácteos y huevo",
      "clase": "A",
      "pct_acum": 64.3,
      "unidades": 8,
      "venta": 220.0,
      "margen_unitario": 7.7,
      "margen_total": 61.6,
      "costo_estimado": true,
      "existencia": 48,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 540.0,
      "rotacion": 0.17,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 540 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 40,
        "clave_interna": "LI-004",
        "nombre": "Limpiador multiusos"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 66.3,
      "unidades": 8,
      "venta": 224.0,
      "margen_unitario": 7.84,
      "margen_total": 62.72,
      "costo_estimado": true,
      "existencia": 14,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 157.5,
      "rotacion": 0.57,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 158 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 51,
        "clave_interna": "HI-006",
        "nombre": "Pañal etapa 3"
      },
      "categoria": "Higiene personal",
      "clase": "A",
      "pct_acum": 68.2,
      "unidades": 8,
      "venta": 544.0,
      "margen_unitario": 19.04,
      "margen_total": 152.32,
      "costo_estimado": true,
      "existencia": 29,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 326.2,
      "rotacion": 0.28,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 326 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 5,
        "clave_interna": "AB-005",
        "nombre": "Sal de mesa"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 69.9,
      "unidades": 7,
      "venta": 98.0,
      "margen_unitario": 3.92,
      "margen_total": 27.44,
      "costo_estimado": true,
      "existencia": 30,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 385.7,
      "rotacion": 0.23,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 386 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 8,
        "clave_interna": "AB-008",
        "nombre": "Pasta para sopa surtida"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 71.6,
      "unidades": 7,
      "venta": 66.5,
      "margen_unitario": 2.66,
      "margen_total": 18.62,
      "costo_estimado": true,
      "existencia": 21,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 270.0,
      "rotacion": 0.33,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 270 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 10,
        "clave_interna": "AB-010",
        "nombre": "Sardina en salsa de tomate"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 73.3,
      "unidades": 7,
      "venta": 185.5,
      "margen_unitario": 7.42,
      "margen_total": 51.94,
      "costo_estimado": true,
      "existencia": 690,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 8871.4,
      "rotacion": 0.01,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 8871 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 14,
        "clave_interna": "AB-014",
        "nombre": "Café soluble"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 75.0,
      "unidades": 7,
      "venta": 364.0,
      "margen_unitario": 14.56,
      "margen_total": 101.92,
      "costo_estimado": true,
      "existencia": 33,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 424.3,
      "rotacion": 0.21,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 424 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 18,
        "clave_interna": "AB-018",
        "nombre": "Pan de caja blanco"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 76.7,
      "unidades": 7,
      "venta": 308.0,
      "margen_unitario": 12.32,
      "margen_total": 86.24,
      "costo_estimado": true,
      "existencia": 80,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 1028.6,
      "rotacion": 0.09,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1029 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 47,
        "clave_interna": "HI-002",
        "nombre": "Shampoo"
      },
      "categoria": "Higiene personal",
      "clase": "A",
      "pct_acum": 78.4,
      "unidades": 7,
      "venta": 378.0,
      "margen_unitario": 15.12,
      "margen_total": 105.84,
      "costo_estimado": true,
      "existencia": 60,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 771.4,
      "rotacion": 0.12,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 771 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 49,
        "clave_interna": "HI-004",
        "nombre": "Desodorante"
      },
      "categoria": "Higiene personal",
      "clase": "A",
      "pct_acum": 80.1,
      "unidades": 7,
      "venta": 336.0,
      "margen_unitario": 13.44,
      "margen_total": 94.08,
      "costo_estimado": true,
      "existencia": 36,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 462.9,
      "rotacion": 0.19,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 463 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 3,
        "clave_interna": "AB-003",
        "nombre": "Aceite vegetal"
      },
      "categoria": "Abarrote básico",
      "clase": "B",
      "pct_acum": 81.6,
      "unidades": 6,
      "venta": 252.0,
      "margen_unitario": 11.76,
      "margen_total": 70.56,
      "costo_estimado": true,
      "existencia": 10,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.07,
      "cobertura_dias": 150.0,
      "rotacion": 0.6,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 150 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 17,
        "clave_interna": "AB-017",
        "nombre": "Tortillas de maíz"
      },
      "categoria": "Abarrote básico",
      "clase": "B",
      "pct_acum": 83.0,
      "unidades": 6,
      "venta": 144.0,
      "margen_unitario": 6.72,
      "margen_total": 40.32,
      "costo_estimado": true,
      "existencia": 21,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.07,
      "cobertura_dias": 315.0,
      "rotacion": 0.29,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 315 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 26,
        "clave_interna": "BE-006",
        "nombre": "Bebida de soya"
      },
      "categoria": "Bebidas",
      "clase": "B",
      "pct_acum": 84.5,
      "unidades": 6,
      "venta": 192.0,
      "margen_unitario": 8.96,
      "margen_total": 53.76,
      "costo_estimado": true,
      "existencia": 17,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.07,
      "cobertura_dias": 255.0,
      "rotacion": 0.35,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 255 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 16,
        "clave_interna": "AB-016",
        "nombre": "Galletas María"
      },
      "categoria": "Abarrote básico",
      "clase": "B",
      "pct_acum": 85.7,
      "unidades": 5,
      "venta": 82.5,
      "margen_unitario": 4.62,
      "margen_total": 23.1,
      "costo_estimado": true,
      "existencia": 81,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 1458.0,
      "rotacion": 0.06,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1458 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 22,
        "clave_interna": "BE-002",
        "nombre": "Agua embotellada"
      },
      "categoria": "Bebidas",
      "clase": "B",
      "pct_acum": 86.9,
      "unidades": 5,
      "venta": 75.0,
      "margen_unitario": 4.2,
      "margen_total": 21.0,
      "costo_estimado": true,
      "existencia": 72,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 1296.0,
      "rotacion": 0.07,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1296 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 23,
        "clave_interna": "BE-003",
        "nombre": "Refresco de cola"
      },
      "categoria": "Bebidas",
      "clase": "B",
      "pct_acum": 88.1,
      "unidades": 5,
      "venta": 192.5,
      "margen_unitario": 10.78,
      "margen_total": 53.9,
      "costo_estimado": true,
      "existencia": 54,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 972.0,
      "rotacion": 0.09,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 972 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 35,
        "clave_interna": "LA-007",
        "nombre": "Mantequilla"
      },
      "categoria": "Lácteos y huevo",
      "clase": "B",
      "pct_acum": 89.3,
      "unidades": 5,
      "venta": 110.0,
      "margen_unitario": 6.16,
      "margen_total": 30.8,
      "costo_estimado": true,
      "existencia": 64,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 1152.0,
      "rotacion": 0.08,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1152 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 41,
        "clave_interna": "LI-005",
        "nombre": "Suavizante de telas"
      },
      "categoria": "Limpieza del hogar",
      "clase": "B",
      "pct_acum": 90.5,
      "unidades": 5,
      "venta": 165.0,
      "margen_unitario": 9.24,
      "margen_total": 46.2,
      "costo_estimado": true,
      "existencia": 69,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 1242.0,
      "rotacion": 0.07,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1242 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 46,
        "clave_interna": "HI-001",
        "nombre": "Jabón de tocador"
      },
      "categoria": "Higiene personal",
      "clase": "B",
      "pct_acum": 91.7,
      "unidades": 5,
      "venta": 72.5,
      "margen_unitario": 4.06,
      "margen_total": 20.3,
      "costo_estimado": true,
      "existencia": 63,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 1134.0,
      "rotacion": 0.08,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1134 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 50,
        "clave_interna": "HI-005",
        "nombre": "Toallas femeninas"
      },
      "categoria": "Higiene personal",
      "clase": "B",
      "pct_acum": 93.0,
      "unidades": 5,
      "venta": 180.0,
      "margen_unitario": 10.08,
      "margen_total": 50.4,
      "costo_estimado": true,
      "existencia": 76,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 1368.0,
      "rotacion": 0.07,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1368 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 4,
        "clave_interna": "AB-004",
        "nombre": "Azúcar estándar"
      },
      "categoria": "Abarrote básico",
      "clase": "B",
      "pct_acum": 93.9,
      "unidades": 4,
      "venta": 114.0,
      "margen_unitario": 7.98,
      "margen_total": 31.92,
      "costo_estimado": true,
      "existencia": 18,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.04,
      "cobertura_dias": 405.0,
      "rotacion": 0.22,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 405 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 15,
        "clave_interna": "AB-015",
        "nombre": "Avena en hojuelas"
      },
      "categoria": "Abarrote básico",
      "clase": "B",
      "pct_acum": 94.9,
      "unidades": 4,
      "venta": 108.0,
      "margen_unitario": 7.56,
      "margen_total": 30.24,
      "costo_estimado": true,
      "existencia": 52,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.04,
      "cobertura_dias": 1170.0,
      "rotacion": 0.08,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1170 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 32,
        "clave_interna": "LA-004",
        "nombre": "Queso Oaxaca"
      },
      "categoria": "Lácteos y huevo",
      "clase": "B",
      "pct_acum": 95.9,
      "unidades": 4,
      "venta": 288.0,
      "margen_unitario": 20.16,
      "margen_total": 80.64,
      "costo_estimado": true,
      "existencia": 20,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.04,
      "cobertura_dias": 450.0,
      "rotacion": 0.2,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 450 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 33,
        "clave_interna": "LA-005",
        "nombre": "Crema ácida"
      },
      "categoria": "Lácteos y huevo",
      "clase": "C",
      "pct_acum": 96.8,
      "unidades": 4,
      "venta": 144.0,
      "margen_unitario": 10.08,
      "margen_total": 40.32,
      "costo_estimado": true,
      "existencia": 82,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.04,
      "cobertura_dias": 1845.0,
      "rotacion": 0.05,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1845 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 37,
        "clave_interna": "LI-001",
        "nombre": "Detergente en polvo"
      },
      "categoria": "Limpieza del hogar",
      "clase": "C",
      "pct_acum": 97.8,
      "unidades": 4,
      "venta": 168.0,
      "margen_unitario": 11.76,
      "margen_total": 47.04,
      "costo_estimado": true,
      "existencia": 13,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.04,
      "cobertura_dias": 292.5,
      "rotacion": 0.31,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 292 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 9,
        "clave_interna": "AB-009",
        "nombre": "Atún en agua"
      },
      "categoria": "Abarrote básico",
      "clase": "C",
      "pct_acum": 98.5,
      "unidades": 3,
      "venta": 63.0,
      "margen_unitario": 5.88,
      "margen_total": 17.64,
      "costo_estimado": true,
      "existencia": 42,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.03,
      "cobertura_dias": 1260.0,
      "rotacion": 0.07,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1260 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 38,
        "clave_interna": "LI-002",
        "nombre": "Jabón para trastes"
      },
      "categoria": "Limpieza del hogar",
      "clase": "C",
      "pct_acum": 99.3,
      "unidades": 3,
      "venta": 78.0,
      "margen_unitario": 7.28,
      "margen_total": 21.84,
      "costo_estimado": true,
      "existencia": 47,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.03,
      "cobertura_dias": 1410.0,
      "rotacion": 0.06,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1410 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 31,
        "clave_interna": "LA-003",
        "nombre": "Queso fresco"
      },
      "categoria": "Lácteos y huevo",
      "clase": "C",
      "pct_acum": 99.8,
      "unidades": 2,
      "venta": 116.0,
      "margen_unitario": 16.24,
      "margen_total": 32.48,
      "costo_estimado": true,
      "existencia": 55,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.02,
      "cobertura_dias": 2475.0,
      "rotacion": 0.04,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 2475 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 21,
        "clave_interna": "BE-001",
        "nombre": "Agua purificada"
      },
      "categoria": "Bebidas",
      "clase": "C",
      "pct_acum": 100.0,
      "unidades": 1,
      "venta": 38.0,
      "margen_unitario": 10.64,
      "margen_total": 10.64,
      "costo_estimado": true,
      "existencia": 0,
      "minimo": 10,
      "quiebres": 2,
      "demanda_dia": 0.01,
      "cobertura_dias": 0.0,
      "rotacion": 99.0,
      "recomendacion": "Aumentar",
      "motivo": "hubo quiebres",
      "sugerido": 1,
      "limitado_por": null
    }
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 80.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 95.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 7.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 5.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 90.0,
      "modificado": false
    }
  ]
}
```

### SUR-08 · El operador analiza otro microhub · PASA

**Objetivo.** No puede.

**Petición.** `GET http://surtido:5122/api/v1/surtido/analisis?microhub_id=2`

```http
Accept: application/json
X-Traza-Id: 99c94724-e1b2-44f1-bd3e-b253139cdba5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 6 ms · traza `99c94724-e1b2-44f1-bd3e-b253139cdba5`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "99c94724-e1b2-44f1-bd3e-b253139cdba5"
  }
}
```

### SUR-09 · Restricciones de un microhub · PASA

**Objetivo.** Espacio y presupuesto.

**Petición.** `GET http://surtido:5122/api/v1/surtido/restricciones/1`

```http
Accept: application/json
X-Traza-Id: cbcdd8b0-9d10-4c59-878a-7ca1d1556f37
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 25 ms · traza `cbcdd8b0-9d10-4c59-878a-7ca1d1556f37`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "espacio_total": 3600.0,
  "presupuesto": 120000.0,
  "actualizado_en": "2026-11-26T14:08:55-06:00"
}
```

### SUR-10 · Cambiar las restricciones · PASA

**Objetivo.** El planeador fija otro espacio y presupuesto.

**Petición.** `PUT http://surtido:5122/api/v1/surtido/restricciones/1`

```http
Accept: application/json
X-Traza-Id: 3f1792e7-157f-4c84-84ce-647a98fee56d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "espacio_total": 3700.0,
  "presupuesto": 120000.0
}
```

**Respuesta.** HTTP 200 (esperado 200) · 54 ms · traza `3f1792e7-157f-4c84-84ce-647a98fee56d`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "espacio_total": 3700.0,
  "presupuesto": 120000.0,
  "actualizado_en": "2026-11-26T14:19:59-06:00"
}
```

**Evidencia en PostgreSQL.** `SELECT espacio_total, presupuesto FROM surtido_restriccion WHERE microhub_id = %s`

```json
[
  {
    "espacio_total": "3700.0",
    "presupuesto": "120000.00"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT accion, entidad, valores_anteriores, valores_nuevos FROM auditoria WHERE entidad = 'surtido_restriccion' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "accion": "modificacion",
    "entidad": "surtido_restriccion",
    "valores_anteriores": {
      "espacio_total": 3600.0,
      "actualizado_en": "2026-11-26T14:08:55.70453-06:00"
    },
    "valores_nuevos": {
      "espacio_total": 3700.0,
      "actualizado_en": "2026-11-26T14:19:59.881007-06:00"
    }
  }
]
```

### SUR-19 · Cambiar las restricciones con PATCH · PASA

**Objetivo.** PATCH es alias de PUT.

**Petición.** `PATCH http://surtido:5122/api/v1/surtido/restricciones/1`

```http
Accept: application/json
X-Traza-Id: 4092e14c-5b8e-4c9f-be7f-964b8f99d2b4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "espacio_total": 3650.0,
  "presupuesto": 120000.0
}
```

**Respuesta.** HTTP 200 (esperado 200) · 56 ms · traza `4092e14c-5b8e-4c9f-be7f-964b8f99d2b4`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "espacio_total": 3650.0,
  "presupuesto": 120000.0,
  "actualizado_en": "2026-11-26T14:20:00-06:00"
}
```

### SUR-11 · Cambiar restricciones sin permiso · PASA

**Objetivo.** Solo surtido.editar.

**Petición.** `PUT http://surtido:5122/api/v1/surtido/restricciones/1`

```http
Accept: application/json
X-Traza-Id: 4cdf878b-d7f3-4f2f-9361-47195254de5c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{
  "espacio_total": 10
}
```

**Respuesta.** HTTP 403 (esperado 403) · 30 ms · traza `4cdf878b-d7f3-4f2f-9361-47195254de5c`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "4cdf878b-d7f3-4f2f-9361-47195254de5c"
  }
}
```

### SUR-12 · Espacio inválido · PASA

**Objetivo.** Mayor que cero.

**Petición.** `PUT http://surtido:5122/api/v1/surtido/restricciones/1`

```http
Accept: application/json
X-Traza-Id: d30ae4fe-fc70-4505-88f1-08da8c1ea41a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "espacio_total": 0
}
```

**Respuesta.** HTTP 422 (esperado 422) · 14 ms · traza `d30ae4fe-fc70-4505-88f1-08da8c1ea41a`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "espacio_total",
        "mensaje": "Debe ser mayor o igual a 1."
      }
    ],
    "traza_id": "d30ae4fe-fc70-4505-88f1-08da8c1ea41a"
  }
}
```

### SUR-13 · Guardar la recomendación · PASA

**Objetivo.** Queda con sus líneas y los supuestos usados, para compararla después.

**Petición.** `POST http://surtido:5122/api/v1/surtido/recomendaciones`

```http
Accept: application/json
X-Traza-Id: d0096b46-3518-4656-81ee-72facd3746cc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "nota": "Evidencia de la Ola 2"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 466 ms · traza `d0096b46-3518-4656-81ee-72facd3746cc`

```json
{
  "id": 34,
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "ventana_dias": 90,
  "nota": "Evidencia de la Ola 2",
  "resumen": {
    "productos": 51,
    "aumentar": 1,
    "mantener": 0,
    "reducir": 50,
    "eliminar": 0,
    "excluir": 0,
    "clase_a": 32,
    "clase_b": 13,
    "clase_c": 6,
    "unidades_a_comprar": 1,
    "con_costo_estimado": 51,
    "espacio": {
      "total": 3600.0,
      "ocupado": 3301.0,
      "sugerido": 1.0,
      "ocupacion_pct": 91.7
    },
    "presupuesto": {
      "total": 120000.0,
      "requerido": 27.36,
      "uso_pct": 0.0
    }
  },
  "creado_por": 5,
  "creado_en": "2026-11-26T14:20:00-06:00",
  "lineas": [
    {
      "producto": {
        "id": 28,
        "clave_interna": "BE-008",
        "nombre": "Polvo para agua de sabor"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 22,
      "existencia": 30,
      "sugerido": 0,
      "margen_unitario": 2.1,
      "rotacion": 0.73,
      "motivo": "cobertura de 123 días, exceso de stock"
    },
    {
      "producto": {
        "id": 45,
        "clave_interna": "LI-009",
        "nombre": "Fibra para trastes"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 16,
      "existencia": 43,
      "sugerido": 0,
      "margen_unitario": 5.04,
      "rotacion": 0.37,
      "motivo": "cobertura de 242 días, exceso de stock"
    },
    {
      "producto": {
        "id": 7,
        "clave_interna": "AB-007",
        "nombre": "Harina de trigo"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 15,
      "existencia": 14,
      "sugerido": 0,
      "margen_unitario": 6.86,
      "rotacion": 1.07,
      "motivo": "cobertura de 84 días, exceso de stock"
    },
    {
      "producto": {
        "id": 25,
        "clave_interna": "BE-005",
        "nombre": "Jugo de naranja"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 15,
      "existencia": 80,
      "sugerido": 0,
      "margen_unitario": 7.84,
      "rotacion": 0.19,
      "motivo": "cobertura de 480 días, exceso de stock"
    },
    {
      "producto": {
        "id": 48,
        "clave_interna": "HI-003",
        "nombre": "Pasta dental"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 15,
      "existencia": 74,
      "sugerido": 0,
      "margen_unitario": 8.96,
      "rotacion": 0.2,
      "motivo": "cobertura de 444 días, exceso de stock"
    },
    {
      "producto": {
        "id": 13,
        "clave_interna": "AB-013",
        "nombre": "Puré de tomate"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 14,
      "existencia": 56,
      "sugerido": 0,
      "margen_unitario": 3.08,
      "rotacion": 0.25,
      "motivo": "cobertura de 360 días, exceso de stock"
    },
    {
      "producto": {
        "id": 20,
        "clave_interna": "AB-020",
        "nombre": "Lenteja"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 13,
      "existencia": 73,
      "sugerido": 0,
      "margen_unitario": 6.72,
      "rotacion": 0.18,
      "motivo": "cobertura de 505 días, exceso de stock"
    },
    {
      "producto": {
        "id": 36,
        "clave_interna": "LA-008",
        "nombre": "Jamón de pavo"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 13,
      "existencia": 47,
      "sugerido": 0,
      "margen_unitario": 12.88,
      "rotacion": 0.28,
      "motivo": "cobertura de 325 días, exceso de stock"
    },
    {
      "producto": {
        "id": 30,
        "clave_interna": "LA-002",
        "nombre": "Leche deslactosada"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 12,
      "existencia": 12,
      "sugerido": 0,
      "margen_unitario": 8.68,
      "rotacion": 1.0,
      "motivo": "cobertura de 90 días, exceso de stock"
    },
    {
      "producto": {
        "id": 34,
        "clave_interna": "LA-006",
        "nombre": "Yogur natural"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 12,
      "existencia": 10,
      "sugerido": 0,
      "margen_unitario": 12.32,
      "rotacion": 1.2,
      "motivo": "cobertura de 75 días, exceso de stock"
    },
    {
      "producto": {
        "id": 42,
        "clave_interna": "LI-006",
        "nombre": "Papel higiénico"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 12,
      "existencia": 64,
      "sugerido": 0,
      "margen_unitario": 10.64,
      "rotacion": 0.19,
      "motivo": "cobertura de 480 días, exceso de stock"
    },
    {
      "producto": {
        "id": 39,
        "clave_interna": "LI-003",
        "nombre": "Cloro"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 11,
      "existencia": 44,
      "sugerido": 0,
      "margen_unitario": 5.46,
      "rotacion": 0.25,
      "motivo": "cobertura de 360 días, exceso de stock"
    },
    {
      "producto": {
        "id": 43,
        "clave_interna": "LI-007",
        "nombre": "Servilletas"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 10,
      "existencia": 65,
      "sugerido": 0,
      "margen_unitario": 8.96,
      "rotacion": 0.15,
      "motivo": "cobertura de 585 días, exceso de stock"
    },
    {
      "producto": {
        "id": 2,
        "clave_interna": "AB-002",
        "nombre": "Arroz superextra"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 9,
      "existencia": 36,
      "sugerido": 0,
      "margen_unitario": 8.37,
      "rotacion": 0.25,
      "motivo": "cobertura de 360 días, exceso de stock"
    },
    {
      "producto": {
        "id": 11,
        "clave_interna": "AB-011",
        "nombre": "Frijoles refritos"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 9,
      "existencia": 27,
      "sugerido": 0,
      "margen_unitario": 6.44,
      "rotacion": 0.33,
      "motivo": "cobertura de 270 días, exceso de stock"
    },
    {
      "producto": {
        "id": 12,
        "clave_interna": "AB-012",
        "nombre": "Chiles jalapeños en escabeche"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 9,
      "existencia": 392,
      "sugerido": 0,
      "margen_unitario": 5.46,
      "rotacion": 0.02,
      "motivo": "cobertura de 3920 días, exceso de stock"
    },
    {
      "producto": {
        "id": 19,
        "clave_interna": "AB-019",
        "nombre": "Huevo blanco"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 9,
      "existencia": 49,
      "sugerido": 0,
      "margen_unitario": 11.76,
      "rotacion": 0.18,
      "motivo": "cobertura de 490 días, exceso de stock"
    },
    {
      "producto": {
        "id": 44,
        "clave_interna": "LI-008",
        "nombre": "Bolsas para basura"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 9,
      "existencia": 26,
      "sugerido": 0,
      "margen_unitario": 6.72,
      "rotacion": 0.35,
      "motivo": "cobertura de 260 días, exceso de stock"
    },
    {
      "producto": {
        "id": 1,
        "clave_interna": "AB-001",
        "nombre": "Frijol negro a granel"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 8,
      "existencia": 58,
      "sugerido": 0,
      "margen_unitario": 10.78,
      "rotacion": 0.14,
      "motivo": "cobertura de 652 días, exceso de stock"
    },
    {
      "producto": {
        "id": 6,
        "clave_interna": "AB-006",
        "nombre": "Harina de maíz nixtamalizado"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 8,
      "existencia": 81,
      "sugerido": 0,
      "margen_unitario": 7.28,
      "rotacion": 0.1,
      "motivo": "cobertura de 911 días, exceso de stock"
    },
    {
      "producto": {
        "id": 24,
        "clave_interna": "BE-004",
        "nombre": "Refresco sabor manzana"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 8,
      "existencia": 39,
      "sugerido": 0,
      "margen_unitario": 10.08,
      "rotacion": 0.21,
      "motivo": "cobertura de 439 días, exceso de stock"
    },
    {
      "producto": {
        "id": 27,
        "clave_interna": "BE-007",
        "nombre": "Té helado de limón"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 8,
      "existencia": 84,
      "sugerido": 0,
      "margen_unitario": 4.76,
      "rotacion": 0.1,
      "motivo": "cobertura de 945 días, exceso de stock"
    },
    {
      "producto": {
        "id": 29,
        "clave_interna": "LA-001",
        "nombre": "Leche entera"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 8,
      "existencia": 48,
      "sugerido": 0,
      "margen_unitario": 7.7,
      "rotacion": 0.17,
      "motivo": "cobertura de 540 días, exceso de stock"
    },
    {
      "producto": {
        "id": 40,
        "clave_interna": "LI-004",
        "nombre": "Limpiador multiusos"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 8,
      "existencia": 14,
      "sugerido": 0,
      "margen_unitario": 7.84,
      "rotacion": 0.57,
      "motivo": "cobertura de 158 días, exceso de stock"
    },
    {
      "producto": {
        "id": 51,
        "clave_interna": "HI-006",
        "nombre": "Pañal etapa 3"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 8,
      "existencia": 29,
      "sugerido": 0,
      "margen_unitario": 19.04,
      "rotacion": 0.28,
      "motivo": "cobertura de 326 días, exceso de stock"
    },
    {
      "producto": {
        "id": 5,
        "clave_interna": "AB-005",
        "nombre": "Sal de mesa"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 30,
      "sugerido": 0,
      "margen_unitario": 3.92,
      "rotacion": 0.23,
      "motivo": "cobertura de 386 días, exceso de stock"
    },
    {
      "producto": {
        "id": 8,
        "clave_interna": "AB-008",
        "nombre": "Pasta para sopa surtida"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 21,
      "sugerido": 0,
      "margen_unitario": 2.66,
      "rotacion": 0.33,
      "motivo": "cobertura de 270 días, exceso de stock"
    },
    {
      "producto": {
        "id": 10,
        "clave_interna": "AB-010",
        "nombre": "Sardina en salsa de tomate"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 690,
      "sugerido": 0,
      "margen_unitario": 7.42,
      "rotacion": 0.01,
      "motivo": "cobertura de 8871 días, exceso de stock"
    },
    {
      "producto": {
        "id": 14,
        "clave_interna": "AB-014",
        "nombre": "Café soluble"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 33,
      "sugerido": 0,
      "margen_unitario": 14.56,
      "rotacion": 0.21,
      "motivo": "cobertura de 424 días, exceso de stock"
    },
    {
      "producto": {
        "id": 18,
        "clave_interna": "AB-018",
        "nombre": "Pan de caja blanco"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 80,
      "sugerido": 0,
      "margen_unitario": 12.32,
      "rotacion": 0.09,
      "motivo": "cobertura de 1029 días, exceso de stock"
    },
    {
      "producto": {
        "id": 47,
        "clave_interna": "HI-002",
        "nombre": "Shampoo"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 60,
      "sugerido": 0,
      "margen_unitario": 15.12,
      "rotacion": 0.12,
      "motivo": "cobertura de 771 días, exceso de stock"
    },
    {
      "producto": {
        "id": 49,
        "clave_interna": "HI-004",
        "nombre": "Desodorante"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 36,
      "sugerido": 0,
      "margen_unitario": 13.44,
      "rotacion": 0.19,
      "motivo": "cobertura de 463 días, exceso de stock"
    },
    {
      "producto": {
        "id": 3,
        "clave_interna": "AB-003",
        "nombre": "Aceite vegetal"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 6,
      "existencia": 10,
      "sugerido": 0,
      "margen_unitario": 11.76,
      "rotacion": 0.6,
      "motivo": "cobertura de 150 días, exceso de stock"
    },
    {
      "producto": {
        "id": 17,
        "clave_interna": "AB-017",
        "nombre": "Tortillas de maíz"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 6,
      "existencia": 21,
      "sugerido": 0,
      "margen_unitario": 6.72,
      "rotacion": 0.29,
      "motivo": "cobertura de 315 días, exceso de stock"
    },
    {
      "producto": {
        "id": 26,
        "clave_interna": "BE-006",
        "nombre": "Bebida de soya"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 6,
      "existencia": 17,
      "sugerido": 0,
      "margen_unitario": 8.96,
      "rotacion": 0.35,
      "motivo": "cobertura de 255 días, exceso de stock"
    },
    {
      "producto": {
        "id": 16,
        "clave_interna": "AB-016",
        "nombre": "Galletas María"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 81,
      "sugerido": 0,
      "margen_unitario": 4.62,
      "rotacion": 0.06,
      "motivo": "cobertura de 1458 días, exceso de stock"
    },
    {
      "producto": {
        "id": 22,
        "clave_interna": "BE-002",
        "nombre": "Agua embotellada"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 72,
      "sugerido": 0,
      "margen_unitario": 4.2,
      "rotacion": 0.07,
      "motivo": "cobertura de 1296 días, exceso de stock"
    },
    {
      "producto": {
        "id": 23,
        "clave_interna": "BE-003",
        "nombre": "Refresco de cola"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 54,
      "sugerido": 0,
      "margen_unitario": 10.78,
      "rotacion": 0.09,
      "motivo": "cobertura de 972 días, exceso de stock"
    },
    {
      "producto": {
        "id": 35,
        "clave_interna": "LA-007",
        "nombre": "Mantequilla"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 64,
      "sugerido": 0,
      "margen_unitario": 6.16,
      "rotacion": 0.08,
      "motivo": "cobertura de 1152 días, exceso de stock"
    },
    {
      "producto": {
        "id": 41,
        "clave_interna": "LI-005",
        "nombre": "Suavizante de telas"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 69,
      "sugerido": 0,
      "margen_unitario": 9.24,
      "rotacion": 0.07,
      "motivo": "cobertura de 1242 días, exceso de stock"
    },
    {
      "producto": {
        "id": 46,
        "clave_interna": "HI-001",
        "nombre": "Jabón de tocador"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 63,
      "sugerido": 0,
      "margen_unitario": 4.06,
      "rotacion": 0.08,
      "motivo": "cobertura de 1134 días, exceso de stock"
    },
    {
      "producto": {
        "id": 50,
        "clave_interna": "HI-005",
        "nombre": "Toallas femeninas"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 76,
      "sugerido": 0,
      "margen_unitario": 10.08,
      "rotacion": 0.07,
      "motivo": "cobertura de 1368 días, exceso de stock"
    },
    {
      "producto": {
        "id": 4,
        "clave_interna": "AB-004",
        "nombre": "Azúcar estándar"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 4,
      "existencia": 18,
      "sugerido": 0,
      "margen_unitario": 7.98,
      "rotacion": 0.22,
      "motivo": "cobertura de 405 días, exceso de stock"
    },
    {
      "producto": {
        "id": 15,
        "clave_interna": "AB-015",
        "nombre": "Avena en hojuelas"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 4,
      "existencia": 52,
      "sugerido": 0,
      "margen_unitario": 7.56,
      "rotacion": 0.08,
      "motivo": "cobertura de 1170 días, exceso de stock"
    },
    {
      "producto": {
        "id": 32,
        "clave_interna": "LA-004",
        "nombre": "Queso Oaxaca"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 4,
      "existencia": 20,
      "sugerido": 0,
      "margen_unitario": 20.16,
      "rotacion": 0.2,
      "motivo": "cobertura de 450 días, exceso de stock"
    },
    {
      "producto": {
        "id": 33,
        "clave_interna": "LA-005",
        "nombre": "Crema ácida"
      },
      "clase": "C",
      "recomendacion": "Reducir",
      "unidades": 4,
      "existencia": 82,
      "sugerido": 0,
      "margen_unitario": 10.08,
      "rotacion": 0.05,
      "motivo": "cobertura de 1845 días, exceso de stock"
    },
    {
      "producto": {
        "id": 37,
        "clave_interna": "LI-001",
        "nombre": "Detergente en polvo"
      },
      "clase": "C",
      "recomendacion": "Reducir",
      "unidades": 4,
      "existencia": 13,
      "sugerido": 0,
      "margen_unitario": 11.76,
      "rotacion": 0.31,
      "motivo": "cobertura de 292 días, exceso de stock"
    },
    {
      "producto": {
        "id": 9,
        "clave_interna": "AB-009",
        "nombre": "Atún en agua"
      },
      "clase": "C",
      "recomendacion": "Reducir",
      "unidades": 3,
      "existencia": 42,
      "sugerido": 0,
      "margen_unitario": 5.88,
      "rotacion": 0.07,
      "motivo": "cobertura de 1260 días, exceso de stock"
    },
    {
      "producto": {
        "id": 38,
        "clave_interna": "LI-002",
        "nombre": "Jabón para trastes"
      },
      "clase": "C",
      "recomendacion": "Reducir",
      "unidades": 3,
      "existencia": 47,
      "sugerido": 0,
      "margen_unitario": 7.28,
      "rotacion": 0.06,
      "motivo": "cobertura de 1410 días, exceso de stock"
    },
    {
      "producto": {
        "id": 31,
        "clave_interna": "LA-003",
        "nombre": "Queso fresco"
      },
      "clase": "C",
      "recomendacion": "Reducir",
      "unidades": 2,
      "existencia": 55,
      "sugerido": 0,
      "margen_unitario": 16.24,
      "rotacion": 0.04,
      "motivo": "cobertura de 2475 días, exceso de stock"
    },
    {
      "producto": {
        "id": 21,
        "clave_interna": "BE-001",
        "nombre": "Agua purificada"
      },
      "clase": "C",
      "recomendacion": "Aumentar",
      "unidades": 1,
      "existencia": 0,
      "sugerido": 1,
      "margen_unitario": 10.64,
      "rotacion": 99.0,
      "motivo": "hubo quiebres"
    }
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 80.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 95.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 7.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 5.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 90.0,
      "modificado": false
    }
  ]
}
```

**Evidencia en PostgreSQL.** `SELECT id, microhub_id, resumen, creado_por FROM surtido_recomendacion WHERE parametros::jsonb ->> 'nota' = 'Evidencia de la Ola 2'`

```json
[
  {
    "id": 34,
    "microhub_id": 1,
    "resumen": {
      "productos": 51,
      "aumentar": 1,
      "mantener": 0,
      "reducir": 50,
      "eliminar": 0,
      "excluir": 0,
      "clase_a": 32,
      "clase_b": 13,
      "clase_c": 6,
      "unidades_a_comprar": 1,
      "con_costo_estimado": 51,
      "espacio": {
        "total": 3600.0,
        "ocupado": 3301.0,
        "sugerido": 1.0,
        "ocupacion_pct": 91.7
      },
      "presupuesto": {
        "total": 120000.0,
        "requerido": 27.36,
        "uso_pct": 0.0
      }
    },
    "creado_por": 5
  }
]
```

**Evidencia en PostgreSQL.** `SELECT accion, count(*) AS lineas, sum(sugerido) AS sugerido FROM surtido_recomendacion_linea WHERE recomendacion_id = (SELECT max(id) FROM surtido_recomendacion) GROUP BY accion ORDER BY accion`

```json
[
  {
    "accion": "Aumentar",
    "lineas": 1,
    "sugerido": 1
  },
  {
    "accion": "Reducir",
    "lineas": 50,
    "sugerido": 0
  }
]
```

### SUR-18 · Recomendaciones guardadas · PASA

**Objetivo.** Para compararlas con el tiempo.

**Petición.** `GET http://surtido:5122/api/v1/surtido/recomendaciones?microhub_id=1`

```http
Accept: application/json
X-Traza-Id: e6a054f7-ce58-4549-b3a1-b542bf67312d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 45 ms · traza `e6a054f7-ce58-4549-b3a1-b542bf67312d`

```json
{
  "datos": [
    {
      "id": 34,
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "ventana_dias": 90,
      "nota": "Evidencia de la Ola 2",
      "resumen": {
        "productos": 51,
        "aumentar": 1,
        "mantener": 0,
        "reducir": 50,
        "eliminar": 0,
        "excluir": 0,
        "clase_a": 32,
        "clase_b": 13,
        "clase_c": 6,
        "unidades_a_comprar": 1,
        "con_costo_estimado": 51,
        "espacio": {
          "total": 3600.0,
          "ocupado": 3301.0,
          "sugerido": 1.0,
          "ocupacion_pct": 91.7
        },
        "presupuesto": {
          "total": 120000.0,
          "requerido": 27.36,
          "uso_pct": 0.0
        }
      },
      "creado_por": 5,
      "creado_en": "2026-11-26T14:20:00-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 1,
    "paginas": 1
  }
}
```

### SUR-14 · Abrir la recomendación · PASA

**Objetivo.** Con el mismo resumen con que se guardó.

**Petición.** `GET http://surtido:5122/api/v1/surtido/recomendaciones/34`

```http
Accept: application/json
X-Traza-Id: 5f6bdd57-7048-42d9-861b-0eb6e9fb757c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 45 ms · traza `5f6bdd57-7048-42d9-861b-0eb6e9fb757c`

```json
{
  "id": 34,
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "ventana_dias": 90,
  "nota": "Evidencia de la Ola 2",
  "resumen": {
    "productos": 51,
    "aumentar": 1,
    "mantener": 0,
    "reducir": 50,
    "eliminar": 0,
    "excluir": 0,
    "clase_a": 32,
    "clase_b": 13,
    "clase_c": 6,
    "unidades_a_comprar": 1,
    "con_costo_estimado": 51,
    "espacio": {
      "total": 3600.0,
      "ocupado": 3301.0,
      "sugerido": 1.0,
      "ocupacion_pct": 91.7
    },
    "presupuesto": {
      "total": 120000.0,
      "requerido": 27.36,
      "uso_pct": 0.0
    }
  },
  "creado_por": 5,
  "creado_en": "2026-11-26T14:20:00-06:00",
  "lineas": [
    {
      "producto": {
        "id": 28,
        "clave_interna": "BE-008",
        "nombre": "Polvo para agua de sabor"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 22,
      "existencia": 30,
      "sugerido": 0,
      "margen_unitario": 2.1,
      "rotacion": 0.73,
      "motivo": "cobertura de 123 días, exceso de stock"
    },
    {
      "producto": {
        "id": 45,
        "clave_interna": "LI-009",
        "nombre": "Fibra para trastes"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 16,
      "existencia": 43,
      "sugerido": 0,
      "margen_unitario": 5.04,
      "rotacion": 0.37,
      "motivo": "cobertura de 242 días, exceso de stock"
    },
    {
      "producto": {
        "id": 7,
        "clave_interna": "AB-007",
        "nombre": "Harina de trigo"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 15,
      "existencia": 14,
      "sugerido": 0,
      "margen_unitario": 6.86,
      "rotacion": 1.07,
      "motivo": "cobertura de 84 días, exceso de stock"
    },
    {
      "producto": {
        "id": 25,
        "clave_interna": "BE-005",
        "nombre": "Jugo de naranja"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 15,
      "existencia": 80,
      "sugerido": 0,
      "margen_unitario": 7.84,
      "rotacion": 0.19,
      "motivo": "cobertura de 480 días, exceso de stock"
    },
    {
      "producto": {
        "id": 48,
        "clave_interna": "HI-003",
        "nombre": "Pasta dental"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 15,
      "existencia": 74,
      "sugerido": 0,
      "margen_unitario": 8.96,
      "rotacion": 0.2,
      "motivo": "cobertura de 444 días, exceso de stock"
    },
    {
      "producto": {
        "id": 13,
        "clave_interna": "AB-013",
        "nombre": "Puré de tomate"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 14,
      "existencia": 56,
      "sugerido": 0,
      "margen_unitario": 3.08,
      "rotacion": 0.25,
      "motivo": "cobertura de 360 días, exceso de stock"
    },
    {
      "producto": {
        "id": 20,
        "clave_interna": "AB-020",
        "nombre": "Lenteja"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 13,
      "existencia": 73,
      "sugerido": 0,
      "margen_unitario": 6.72,
      "rotacion": 0.18,
      "motivo": "cobertura de 505 días, exceso de stock"
    },
    {
      "producto": {
        "id": 36,
        "clave_interna": "LA-008",
        "nombre": "Jamón de pavo"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 13,
      "existencia": 47,
      "sugerido": 0,
      "margen_unitario": 12.88,
      "rotacion": 0.28,
      "motivo": "cobertura de 325 días, exceso de stock"
    },
    {
      "producto": {
        "id": 30,
        "clave_interna": "LA-002",
        "nombre": "Leche deslactosada"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 12,
      "existencia": 12,
      "sugerido": 0,
      "margen_unitario": 8.68,
      "rotacion": 1.0,
      "motivo": "cobertura de 90 días, exceso de stock"
    },
    {
      "producto": {
        "id": 34,
        "clave_interna": "LA-006",
        "nombre": "Yogur natural"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 12,
      "existencia": 10,
      "sugerido": 0,
      "margen_unitario": 12.32,
      "rotacion": 1.2,
      "motivo": "cobertura de 75 días, exceso de stock"
    },
    {
      "producto": {
        "id": 42,
        "clave_interna": "LI-006",
        "nombre": "Papel higiénico"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 12,
      "existencia": 64,
      "sugerido": 0,
      "margen_unitario": 10.64,
      "rotacion": 0.19,
      "motivo": "cobertura de 480 días, exceso de stock"
    },
    {
      "producto": {
        "id": 39,
        "clave_interna": "LI-003",
        "nombre": "Cloro"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 11,
      "existencia": 44,
      "sugerido": 0,
      "margen_unitario": 5.46,
      "rotacion": 0.25,
      "motivo": "cobertura de 360 días, exceso de stock"
    },
    {
      "producto": {
        "id": 43,
        "clave_interna": "LI-007",
        "nombre": "Servilletas"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 10,
      "existencia": 65,
      "sugerido": 0,
      "margen_unitario": 8.96,
      "rotacion": 0.15,
      "motivo": "cobertura de 585 días, exceso de stock"
    },
    {
      "producto": {
        "id": 2,
        "clave_interna": "AB-002",
        "nombre": "Arroz superextra"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 9,
      "existencia": 36,
      "sugerido": 0,
      "margen_unitario": 8.37,
      "rotacion": 0.25,
      "motivo": "cobertura de 360 días, exceso de stock"
    },
    {
      "producto": {
        "id": 11,
        "clave_interna": "AB-011",
        "nombre": "Frijoles refritos"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 9,
      "existencia": 27,
      "sugerido": 0,
      "margen_unitario": 6.44,
      "rotacion": 0.33,
      "motivo": "cobertura de 270 días, exceso de stock"
    },
    {
      "producto": {
        "id": 12,
        "clave_interna": "AB-012",
        "nombre": "Chiles jalapeños en escabeche"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 9,
      "existencia": 392,
      "sugerido": 0,
      "margen_unitario": 5.46,
      "rotacion": 0.02,
      "motivo": "cobertura de 3920 días, exceso de stock"
    },
    {
      "producto": {
        "id": 19,
        "clave_interna": "AB-019",
        "nombre": "Huevo blanco"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 9,
      "existencia": 49,
      "sugerido": 0,
      "margen_unitario": 11.76,
      "rotacion": 0.18,
      "motivo": "cobertura de 490 días, exceso de stock"
    },
    {
      "producto": {
        "id": 44,
        "clave_interna": "LI-008",
        "nombre": "Bolsas para basura"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 9,
      "existencia": 26,
      "sugerido": 0,
      "margen_unitario": 6.72,
      "rotacion": 0.35,
      "motivo": "cobertura de 260 días, exceso de stock"
    },
    {
      "producto": {
        "id": 1,
        "clave_interna": "AB-001",
        "nombre": "Frijol negro a granel"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 8,
      "existencia": 58,
      "sugerido": 0,
      "margen_unitario": 10.78,
      "rotacion": 0.14,
      "motivo": "cobertura de 652 días, exceso de stock"
    },
    {
      "producto": {
        "id": 6,
        "clave_interna": "AB-006",
        "nombre": "Harina de maíz nixtamalizado"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 8,
      "existencia": 81,
      "sugerido": 0,
      "margen_unitario": 7.28,
      "rotacion": 0.1,
      "motivo": "cobertura de 911 días, exceso de stock"
    },
    {
      "producto": {
        "id": 24,
        "clave_interna": "BE-004",
        "nombre": "Refresco sabor manzana"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 8,
      "existencia": 39,
      "sugerido": 0,
      "margen_unitario": 10.08,
      "rotacion": 0.21,
      "motivo": "cobertura de 439 días, exceso de stock"
    },
    {
      "producto": {
        "id": 27,
        "clave_interna": "BE-007",
        "nombre": "Té helado de limón"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 8,
      "existencia": 84,
      "sugerido": 0,
      "margen_unitario": 4.76,
      "rotacion": 0.1,
      "motivo": "cobertura de 945 días, exceso de stock"
    },
    {
      "producto": {
        "id": 29,
        "clave_interna": "LA-001",
        "nombre": "Leche entera"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 8,
      "existencia": 48,
      "sugerido": 0,
      "margen_unitario": 7.7,
      "rotacion": 0.17,
      "motivo": "cobertura de 540 días, exceso de stock"
    },
    {
      "producto": {
        "id": 40,
        "clave_interna": "LI-004",
        "nombre": "Limpiador multiusos"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 8,
      "existencia": 14,
      "sugerido": 0,
      "margen_unitario": 7.84,
      "rotacion": 0.57,
      "motivo": "cobertura de 158 días, exceso de stock"
    },
    {
      "producto": {
        "id": 51,
        "clave_interna": "HI-006",
        "nombre": "Pañal etapa 3"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 8,
      "existencia": 29,
      "sugerido": 0,
      "margen_unitario": 19.04,
      "rotacion": 0.28,
      "motivo": "cobertura de 326 días, exceso de stock"
    },
    {
      "producto": {
        "id": 5,
        "clave_interna": "AB-005",
        "nombre": "Sal de mesa"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 30,
      "sugerido": 0,
      "margen_unitario": 3.92,
      "rotacion": 0.23,
      "motivo": "cobertura de 386 días, exceso de stock"
    },
    {
      "producto": {
        "id": 8,
        "clave_interna": "AB-008",
        "nombre": "Pasta para sopa surtida"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 21,
      "sugerido": 0,
      "margen_unitario": 2.66,
      "rotacion": 0.33,
      "motivo": "cobertura de 270 días, exceso de stock"
    },
    {
      "producto": {
        "id": 10,
        "clave_interna": "AB-010",
        "nombre": "Sardina en salsa de tomate"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 690,
      "sugerido": 0,
      "margen_unitario": 7.42,
      "rotacion": 0.01,
      "motivo": "cobertura de 8871 días, exceso de stock"
    },
    {
      "producto": {
        "id": 14,
        "clave_interna": "AB-014",
        "nombre": "Café soluble"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 33,
      "sugerido": 0,
      "margen_unitario": 14.56,
      "rotacion": 0.21,
      "motivo": "cobertura de 424 días, exceso de stock"
    },
    {
      "producto": {
        "id": 18,
        "clave_interna": "AB-018",
        "nombre": "Pan de caja blanco"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 80,
      "sugerido": 0,
      "margen_unitario": 12.32,
      "rotacion": 0.09,
      "motivo": "cobertura de 1029 días, exceso de stock"
    },
    {
      "producto": {
        "id": 47,
        "clave_interna": "HI-002",
        "nombre": "Shampoo"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 60,
      "sugerido": 0,
      "margen_unitario": 15.12,
      "rotacion": 0.12,
      "motivo": "cobertura de 771 días, exceso de stock"
    },
    {
      "producto": {
        "id": 49,
        "clave_interna": "HI-004",
        "nombre": "Desodorante"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 36,
      "sugerido": 0,
      "margen_unitario": 13.44,
      "rotacion": 0.19,
      "motivo": "cobertura de 463 días, exceso de stock"
    },
    {
      "producto": {
        "id": 3,
        "clave_interna": "AB-003",
        "nombre": "Aceite vegetal"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 6,
      "existencia": 10,
      "sugerido": 0,
      "margen_unitario": 11.76,
      "rotacion": 0.6,
      "motivo": "cobertura de 150 días, exceso de stock"
    },
    {
      "producto": {
        "id": 17,
        "clave_interna": "AB-017",
        "nombre": "Tortillas de maíz"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 6,
      "existencia": 21,
      "sugerido": 0,
      "margen_unitario": 6.72,
      "rotacion": 0.29,
      "motivo": "cobertura de 315 días, exceso de stock"
    },
    {
      "producto": {
        "id": 26,
        "clave_interna": "BE-006",
        "nombre": "Bebida de soya"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 6,
      "existencia": 17,
      "sugerido": 0,
      "margen_unitario": 8.96,
      "rotacion": 0.35,
      "motivo": "cobertura de 255 días, exceso de stock"
    },
    {
      "producto": {
        "id": 16,
        "clave_interna": "AB-016",
        "nombre": "Galletas María"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 81,
      "sugerido": 0,
      "margen_unitario": 4.62,
      "rotacion": 0.06,
      "motivo": "cobertura de 1458 días, exceso de stock"
    },
    {
      "producto": {
        "id": 22,
        "clave_interna": "BE-002",
        "nombre": "Agua embotellada"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 72,
      "sugerido": 0,
      "margen_unitario": 4.2,
      "rotacion": 0.07,
      "motivo": "cobertura de 1296 días, exceso de stock"
    },
    {
      "producto": {
        "id": 23,
        "clave_interna": "BE-003",
        "nombre": "Refresco de cola"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 54,
      "sugerido": 0,
      "margen_unitario": 10.78,
      "rotacion": 0.09,
      "motivo": "cobertura de 972 días, exceso de stock"
    },
    {
      "producto": {
        "id": 35,
        "clave_interna": "LA-007",
        "nombre": "Mantequilla"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 64,
      "sugerido": 0,
      "margen_unitario": 6.16,
      "rotacion": 0.08,
      "motivo": "cobertura de 1152 días, exceso de stock"
    },
    {
      "producto": {
        "id": 41,
        "clave_interna": "LI-005",
        "nombre": "Suavizante de telas"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 69,
      "sugerido": 0,
      "margen_unitario": 9.24,
      "rotacion": 0.07,
      "motivo": "cobertura de 1242 días, exceso de stock"
    },
    {
      "producto": {
        "id": 46,
        "clave_interna": "HI-001",
        "nombre": "Jabón de tocador"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 63,
      "sugerido": 0,
      "margen_unitario": 4.06,
      "rotacion": 0.08,
      "motivo": "cobertura de 1134 días, exceso de stock"
    },
    {
      "producto": {
        "id": 50,
        "clave_interna": "HI-005",
        "nombre": "Toallas femeninas"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 76,
      "sugerido": 0,
      "margen_unitario": 10.08,
      "rotacion": 0.07,
      "motivo": "cobertura de 1368 días, exceso de stock"
    },
    {
      "producto": {
        "id": 4,
        "clave_interna": "AB-004",
        "nombre": "Azúcar estándar"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 4,
      "existencia": 18,
      "sugerido": 0,
      "margen_unitario": 7.98,
      "rotacion": 0.22,
      "motivo": "cobertura de 405 días, exceso de stock"
    },
    {
      "producto": {
        "id": 15,
        "clave_interna": "AB-015",
        "nombre": "Avena en hojuelas"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 4,
      "existencia": 52,
      "sugerido": 0,
      "margen_unitario": 7.56,
      "rotacion": 0.08,
      "motivo": "cobertura de 1170 días, exceso de stock"
    },
    {
      "producto": {
        "id": 32,
        "clave_interna": "LA-004",
        "nombre": "Queso Oaxaca"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 4,
      "existencia": 20,
      "sugerido": 0,
      "margen_unitario": 20.16,
      "rotacion": 0.2,
      "motivo": "cobertura de 450 días, exceso de stock"
    },
    {
      "producto": {
        "id": 33,
        "clave_interna": "LA-005",
        "nombre": "Crema ácida"
      },
      "clase": "C",
      "recomendacion": "Reducir",
      "unidades": 4,
      "existencia": 82,
      "sugerido": 0,
      "margen_unitario": 10.08,
      "rotacion": 0.05,
      "motivo": "cobertura de 1845 días, exceso de stock"
    },
    {
      "producto": {
        "id": 37,
        "clave_interna": "LI-001",
        "nombre": "Detergente en polvo"
      },
      "clase": "C",
      "recomendacion": "Reducir",
      "unidades": 4,
      "existencia": 13,
      "sugerido": 0,
      "margen_unitario": 11.76,
      "rotacion": 0.31,
      "motivo": "cobertura de 292 días, exceso de stock"
    },
    {
      "producto": {
        "id": 9,
        "clave_interna": "AB-009",
        "nombre": "Atún en agua"
      },
      "clase": "C",
      "recomendacion": "Reducir",
      "unidades": 3,
      "existencia": 42,
      "sugerido": 0,
      "margen_unitario": 5.88,
      "rotacion": 0.07,
      "motivo": "cobertura de 1260 días, exceso de stock"
    },
    {
      "producto": {
        "id": 38,
        "clave_interna": "LI-002",
        "nombre": "Jabón para trastes"
      },
      "clase": "C",
      "recomendacion": "Reducir",
      "unidades": 3,
      "existencia": 47,
      "sugerido": 0,
      "margen_unitario": 7.28,
      "rotacion": 0.06,
      "motivo": "cobertura de 1410 días, exceso de stock"
    },
    {
      "producto": {
        "id": 31,
        "clave_interna": "LA-003",
        "nombre": "Queso fresco"
      },
      "clase": "C",
      "recomendacion": "Reducir",
      "unidades": 2,
      "existencia": 55,
      "sugerido": 0,
      "margen_unitario": 16.24,
      "rotacion": 0.04,
      "motivo": "cobertura de 2475 días, exceso de stock"
    },
    {
      "producto": {
        "id": 21,
        "clave_interna": "BE-001",
        "nombre": "Agua purificada"
      },
      "clase": "C",
      "recomendacion": "Aumentar",
      "unidades": 1,
      "existencia": 0,
      "sugerido": 1,
      "margen_unitario": 10.64,
      "rotacion": 99.0,
      "motivo": "hubo quiebres"
    }
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 80.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 95.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 7.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 5.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 90.0,
      "modificado": false
    }
  ]
}
```

### SUR-15 · Otro microhub abre la recomendación · PASA

**Objetivo.** El operador de otro microhub no la ve.

**Petición.** `GET http://surtido:5122/api/v1/surtido/recomendaciones/34`

```http
Accept: application/json
X-Traza-Id: f970d90c-c9ed-4ce6-90d3-d70346daa5d8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 23 ms · traza `f970d90c-c9ed-4ce6-90d3-d70346daa5d8`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "f970d90c-c9ed-4ce6-90d3-d70346daa5d8"
  }
}
```

### SUR-16 · Guardar sin permiso · PASA

**Objetivo.** El operador no tiene surtido.editar.

**Petición.** `POST http://surtido:5122/api/v1/surtido/recomendaciones`

```http
Accept: application/json
X-Traza-Id: 738e74b8-f18a-4769-b084-2136340cf565
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1
}
```

**Respuesta.** HTTP 403 (esperado 403) · 27 ms · traza `738e74b8-f18a-4769-b084-2136340cf565`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "738e74b8-f18a-4769-b084-2136340cf565"
  }
}
```

### SUR-17 · Supuestos del surtido · PASA

**Objetivo.** Cortes ABC, días de cobertura y ventana de análisis.

**Petición.** `GET http://surtido:5122/api/v1/surtido/supuestos`

```http
Accept: application/json
X-Traza-Id: e4f5ddc7-fcdd-4bca-afcb-709d44dcb3e8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 31 ms · traza `e4f5ddc7-fcdd-4bca-afcb-709d44dcb3e8`

```json
{
  "datos": [
    {
      "clave": "********",
      "valor": "80",
      "unidad": "porcentaje",
      "origen": "normativo",
      "justificacion": "Regla de Pareto: los productos que acumulan hasta 80 % del movimiento son clase A.",
      "como_calibrar": "No se calibra; es una convención de clasificación."
    },
    {
      "clave": "********",
      "valor": "95",
      "unidad": "porcentaje",
      "origen": "normativo",
      "justificacion": "Los productos hasta 95 % acumulado son clase B; el resto, clase C.",
      "como_calibrar": "No se calibra; es una convención de clasificación."
    },
    {
      "clave": "********",
      "valor": "7",
      "unidad": "días",
      "origen": "supuesto",
      "justificacion": "Días de existencia que se quiere tener de un producto clase A.",
      "como_calibrar": "Comparar con los quiebres de inventario de los productos A."
    },
    {
      "clave": "********",
      "valor": "5",
      "unidad": "días",
      "origen": "supuesto",
      "justificacion": "Días de existencia que se quiere tener de un producto clase B.",
      "como_calibrar": "Comparar con los quiebres de inventario de los productos B."
    },
    {
      "clave": "********",
      "valor": "3",
      "unidad": "días",
      "origen": "supuesto",
      "justificacion": "Días de existencia que se quiere tener de un producto clase C.",
      "como_calibrar": "Comparar con los quiebres de inventario de los productos C."
    },
    {
      "clave": "********",
      "valor": "30",
      "unidad": "días",
      "origen": "supuesto",
      "justificacion": "Con más de 30 días de cobertura el producto se considera con exceso.",
      "como_calibrar": "Revisar con la caducidad y la rotación real."
    },
    {
      "clave": "********",
      "valor": "0.28",
      "unidad": "fracción",
      "origen": "supuesto",
      "justificacion": "Margen bruto sobre la venta cuando no se conoce el costo del producto. En abarrotes urbanos es de 20 a 35 %.",
      "como_calibrar": "Margen real por producto: servicio de precios, GET /precios/margenes."
    },
    {
      "clave": "********",
      "valor": "90",
      "unidad": "días",
      "origen": "supuesto",
      "justificacion": "Tres meses de ventas para clasificar los productos: suficiente para ver la rotación sin arrastrar temporadas viejas.",
      "como_calibrar": "Probar con 30 y 180 días y ver si cambian las clases A."
    }
  ]
}
```

## Servicio pedidos · puerto 5104

### RUT-01 · Pedidos listos para despachar · PASA

**Objetivo.** Los que rutas va a agrupar: en preparación y marcados como listos.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/listos?microhub_id=1&por_pagina=100`

```http
Accept: application/json
X-Traza-Id: 123224b6-9c59-4ce8-9c63-f5afcce5397d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 76 ms · traza `123224b6-9c59-4ce8-9c63-f5afcce5397d`

```json
{
  "datos": [
    {
      "id": 428,
      "folio": "PED-20261126-000428",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "latitud": 25.753225,
      "longitud": -100.365213,
      "total": 177.0,
      "listo_en": "2026-11-26T00:33:03-06:00"
    },
    {
      "id": 544,
      "folio": "PED-20261126-000544",
      "zona": {
        "id": 1,
        "nombre": "San Bernabé Centro"
      },
      "latitud": 25.745527,
      "longitud": -100.362981,
      "total": 190.5,
      "listo_en": "2026-11-26T14:20:00-06:00"
    },
    {
      "id": 545,
      "folio": "PED-20261126-000545",
      "zona": {
        "id": 1,
        "nombre": "San Bernabé Centro"
      },
      "latitud": 25.745527,
      "longitud": -100.362981,
      "total": 255.0,
      "listo_en": "2026-11-26T14:20:00-06:00"
    },
    {
      "id": 547,
      "folio": "PED-20261126-000547",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "latitud": 25.752587,
      "longitud": -100.364483,
      "total": 183.0,
      "listo_en": "2026-11-26T14:20:00-06:00"
    },
    {
      "id": 548,
      "folio": "PED-20261126-000548",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "latitud": 25.751679,
      "longitud": -100.366615,
      "total": 147.0,
      "listo_en": "2026-11-26T14:20:00-06:00"
    },
    {
      "id": 549,
      "folio": "PED-20261126-000549",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "latitud": 25.752587,
      "longitud": -100.364483,
      "total": 145.0,
      "listo_en": "2026-11-26T14:20:00-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 100,
    "total": 6,
    "paginas": 1
  }
}
```

**Evidencia en PostgreSQL.** `SELECT id, folio, estado, zona_id, listo_en IS NOT NULL AS listo FROM pedido WHERE id = ANY(%s) ORDER BY id`

```json
[
  {
    "id": 428,
    "folio": "PED-20261126-000428",
    "estado": "en_preparacion",
    "zona_id": 2,
    "listo": true
  },
  {
    "id": 544,
    "folio": "PED-20261126-000544",
    "estado": "en_preparacion",
    "zona_id": 1,
    "listo": true
  },
  {
    "id": 545,
    "folio": "PED-20261126-000545",
    "estado": "en_preparacion",
    "zona_id": 1,
    "listo": true
  },
  {
    "id": 547,
    "folio": "PED-20261126-000547",
    "estado": "en_preparacion",
    "zona_id": 2,
    "listo": true
  },
  {
    "id": 548,
    "folio": "PED-20261126-000548",
    "estado": "en_preparacion",
    "zona_id": 2,
    "listo": true
  },
  {
    "id": 549,
    "folio": "PED-20261126-000549",
    "estado": "en_preparacion",
    "zona_id": 2,
    "listo": true
  }
]
```

## Servicio rutas · puerto 5118

### RUT-02 · Calcular un plan sin guardarlo · PASA

**Objetivo.** Agrupa por zona, reparte entre repartidores, ordena las paradas, y calcula distancia, tiempo y costo.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/json
X-Traza-Id: 2298b6da-9c5d-42ea-831d-2849e070302e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "pedido_ids": [
    428,
    544,
    545,
    547,
    548,
    549
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 158 ms · traza `2298b6da-9c5d-42ea-831d-2849e070302e`

```json
{
  "id": null,
  "estado": "calculo",
  "version": 1,
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "fecha": "2026-11-26",
  "metodo_pedido": "automatico",
  "rutas": [
    {
      "repartidor": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "metodo": "TSP exacto",
      "zonas": [
        "Valles de San Bernabé"
      ],
      "paradas": [
        {
          "orden": 1,
          "pedido": {
            "id": 548,
            "folio": "PED-20261126-000548"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.751679,
          "longitud": -100.366615,
          "tramo_km": 0.63,
          "minutos_acum": 5.7
        },
        {
          "orden": 2,
          "pedido": {
            "id": 428,
            "folio": "PED-20261126-000428"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.29,
          "minutos_acum": 10.5
        },
        {
          "orden": 3,
          "pedido": {
            "id": 547,
            "folio": "PED-20261126-000547"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.13,
          "minutos_acum": 14.9
        },
        {
          "orden": 4,
          "pedido": {
            "id": 549,
            "folio": "PED-20261126-000549"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.0,
          "minutos_acum": 18.9
        }
      ],
      "distancia_km": 1.05,
      "minutos": 18.9,
      "costo": 76.74
    },
    {
      "repartidor": {
        "id": 8,
        "nombre": "Diana Sepúlveda Ibarra"
      },
      "metodo": "TSP exacto",
      "zonas": [
        "San Bernabé Centro"
      ],
      "paradas": [
        {
          "orden": 1,
          "pedido": {
            "id": 544,
            "folio": "PED-20261126-000544"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.745527,
          "longitud": -100.362981,
          "tramo_km": 0.38,
          "minutos_acum": 5.0
        },
        {
          "orden": 2,
          "pedido": {
            "id": 545,
            "folio": "PED-20261126-000545"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.745527,
          "longitud": -100.362981,
          "tramo_km": 0.0,
          "minutos_acum": 9.0
        }
      ],
      "distancia_km": 0.38,
      "minutos": 9.0,
      "costo": 37.72
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 2,
    "paradas": 6,
    "distancia_km": 1.43,
    "minutos_maximo": 18.9,
    "costo": 114.46
  },
  "cambios": [],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.5,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 18.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 8.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 1.3,
      "modificado": false
    }
  ]
}
```

**Explicación.** Exacto (prueba todos los órdenes) hasta 8 paradas; con más, vecino más cercano mejorado con 2-opt. Distancia por calle = línea recta × 1.3; minutos = distancia ÷ 22 km/h + 4 min por parada; costo = km × 4.50 + 18 por entrega.

**Evidencia en PostgreSQL.** `SELECT count(*) AS planes FROM plan_despacho WHERE microhub_id = %s`

```json
[
  {
    "planes": 0
  }
]
```

### RUT-03 · Comparar métodos de recorrido · PASA

**Objetivo.** Las mismas paradas con orden de llegada, vecino más cercano, 2-opt y exacto.

**Petición.** `POST http://rutas:5118/api/v1/rutas/comparaciones`

```http
Accept: application/json
X-Traza-Id: 0b1d175a-5881-4d03-a963-bcc6933a9ab1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "pedido_ids": [
    428,
    544,
    545,
    547,
    548,
    549
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 145 ms · traza `0b1d175a-5881-4d03-a963-bcc6933a9ab1`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "paradas": 6,
  "filas": [
    {
      "metodo": "Orden de llegada",
      "distancia_km": 3.57,
      "minutos": 33.7,
      "costo": 124.09,
      "mejora_pct": 0.0
    },
    {
      "metodo": "Vecino más cercano",
      "distancia_km": 1.81,
      "minutos": 28.9,
      "costo": 116.14,
      "mejora_pct": 49.3
    },
    {
      "metodo": "Vecino más cercano + 2-opt",
      "distancia_km": 1.81,
      "minutos": 28.9,
      "costo": 116.14,
      "mejora_pct": 49.3
    },
    {
      "metodo": "TSP exacto",
      "distancia_km": 1.81,
      "minutos": 28.9,
      "costo": 116.14,
      "mejora_pct": 49.3
    }
  ],
  "mejor_metodo": "Vecino más cercano",
  "nota": "Una sola ruta con todas las paradas.",
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.5,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 18.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 8.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 1.3,
      "modificado": false
    }
  ]
}
```

### RUT-04 · Otro método · PASA

**Objetivo.** El exacto con un solo repartidor.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/json
X-Traza-Id: 9f3267d0-9cc6-4285-9fca-18e40d5b6ef1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "pedido_ids": [
    428,
    544,
    545,
    547,
    548,
    549
  ],
  "metodo": "exacto"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 164 ms · traza `9f3267d0-9cc6-4285-9fca-18e40d5b6ef1`

```json
{
  "id": null,
  "estado": "calculo",
  "version": 1,
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "fecha": "2026-11-26",
  "metodo_pedido": "exacto",
  "rutas": [
    {
      "repartidor": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "metodo": "TSP exacto",
      "zonas": [
        "Valles de San Bernabé"
      ],
      "paradas": [
        {
          "orden": 1,
          "pedido": {
            "id": 548,
            "folio": "PED-20261126-000548"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.751679,
          "longitud": -100.366615,
          "tramo_km": 0.63,
          "minutos_acum": 5.7
        },
        {
          "orden": 2,
          "pedido": {
            "id": 428,
            "folio": "PED-20261126-000428"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.29,
          "minutos_acum": 10.5
        },
        {
          "orden": 3,
          "pedido": {
            "id": 547,
            "folio": "PED-20261126-000547"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.13,
          "minutos_acum": 14.9
        },
        {
          "orden": 4,
          "pedido": {
            "id": 549,
            "folio": "PED-20261126-000549"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.0,
          "minutos_acum": 18.9
        }
      ],
      "distancia_km": 1.05,
      "minutos": 18.9,
      "costo": 76.74
    },
    {
      "repartidor": {
        "id": 8,
        "nombre": "Diana Sepúlveda Ibarra"
      },
      "metodo": "TSP exacto",
      "zonas": [
        "San Bernabé Centro"
      ],
      "paradas": [
        {
          "orden": 1,
          "pedido": {
            "id": 544,
            "folio": "PED-20261126-000544"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.745527,
          "longitud": -100.362981,
          "tramo_km": 0.38,
          "minutos_acum": 5.0
        },
        {
          "orden": 2,
          "pedido": {
            "id": 545,
            "folio": "PED-20261126-000545"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.745527,
          "longitud": -100.362981,
          "tramo_km": 0.0,
          "minutos_acum": 9.0
        }
      ],
      "distancia_km": 0.38,
      "minutos": 9.0,
      "costo": 37.72
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 2,
    "paradas": 6,
    "distancia_km": 1.43,
    "minutos_maximo": 18.9,
    "costo": 114.46
  },
  "cambios": [],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.5,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 18.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 8.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 1.3,
      "modificado": false
    }
  ]
}
```

### RUT-05 · Guardar un plan propuesto · PASA

**Objetivo.** Queda en plan_despacho como «propuesto»; todavía no escribe rutas.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/json
X-Traza-Id: b48a0231-a463-4a88-9c90-86a1d9aac075
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "pedido_ids": [
    428,
    544,
    545,
    547,
    548,
    549
  ],
  "guardar": true
}
```

**Respuesta.** HTTP 201 (esperado 201) · 190 ms · traza `b48a0231-a463-4a88-9c90-86a1d9aac075`

```json
{
  "id": 93,
  "estado": "propuesto",
  "version": 1,
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "fecha": "2026-11-26",
  "metodo_pedido": "automatico",
  "rutas": [
    {
      "repartidor": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "metodo": "TSP exacto",
      "zonas": [
        "Valles de San Bernabé"
      ],
      "paradas": [
        {
          "orden": 1,
          "pedido": {
            "id": 548,
            "folio": "PED-20261126-000548"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.751679,
          "longitud": -100.366615,
          "tramo_km": 0.63,
          "minutos_acum": 5.7
        },
        {
          "orden": 2,
          "pedido": {
            "id": 428,
            "folio": "PED-20261126-000428"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.29,
          "minutos_acum": 10.5
        },
        {
          "orden": 3,
          "pedido": {
            "id": 547,
            "folio": "PED-20261126-000547"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.13,
          "minutos_acum": 14.9
        },
        {
          "orden": 4,
          "pedido": {
            "id": 549,
            "folio": "PED-20261126-000549"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.0,
          "minutos_acum": 18.9
        }
      ],
      "distancia_km": 1.05,
      "minutos": 18.9,
      "costo": 76.74
    },
    {
      "repartidor": {
        "id": 8,
        "nombre": "Diana Sepúlveda Ibarra"
      },
      "metodo": "TSP exacto",
      "zonas": [
        "San Bernabé Centro"
      ],
      "paradas": [
        {
          "orden": 1,
          "pedido": {
            "id": 544,
            "folio": "PED-20261126-000544"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.745527,
          "longitud": -100.362981,
          "tramo_km": 0.38,
          "minutos_acum": 5.0
        },
        {
          "orden": 2,
          "pedido": {
            "id": 545,
            "folio": "PED-20261126-000545"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.745527,
          "longitud": -100.362981,
          "tramo_km": 0.0,
          "minutos_acum": 9.0
        }
      ],
      "distancia_km": 0.38,
      "minutos": 9.0,
      "costo": 37.72
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 2,
    "paradas": 6,
    "distancia_km": 1.43,
    "minutos_maximo": 18.9,
    "costo": 114.46
  },
  "cambios": [],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.5,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 18.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 8.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 1.3,
      "modificado": false
    }
  ]
}
```

**Evidencia en PostgreSQL.** `SELECT id, microhub_id, estado, version FROM plan_despacho WHERE id = %s`

```json
[
  {
    "id": 93,
    "microhub_id": 1,
    "estado": "propuesto",
    "version": 1
  }
]
```

**Evidencia en PostgreSQL.** `SELECT count(*) AS rutas FROM plan_ruta WHERE plan_despacho_id = %s`

```json
[
  {
    "rutas": 0
  }
]
```

### RUT-06 · Retraso de un repartidor · PASA

**Objetivo.** Suma minutos a su ruta y dice qué paradas quedan fuera de la promesa de 30 minutos.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes/93/ajustes`

```http
Accept: application/json
X-Traza-Id: d5cfb54f-4474-4586-b778-3bcda9dc0232
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "tipo": "retraso",
  "repartidor_id": 7,
  "minutos": 25
}
```

**Respuesta.** HTTP 200 (esperado 200) · 79 ms · traza `d5cfb54f-4474-4586-b778-3bcda9dc0232`

```json
{
  "id": 93,
  "estado": "propuesto",
  "version": 2,
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "fecha": "2026-11-26",
  "metodo_pedido": "automatico",
  "rutas": [
    {
      "repartidor": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "metodo": "TSP exacto",
      "zonas": [
        "Valles de San Bernabé"
      ],
      "paradas": [
        {
          "orden": 1,
          "pedido": {
            "id": 548,
            "folio": "PED-20261126-000548"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.751679,
          "longitud": -100.366615,
          "tramo_km": 0.63,
          "minutos_acum": 30.7
        },
        {
          "orden": 2,
          "pedido": {
            "id": 428,
            "folio": "PED-20261126-000428"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.29,
          "minutos_acum": 35.5
        },
        {
          "orden": 3,
          "pedido": {
            "id": 547,
            "folio": "PED-20261126-000547"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.13,
          "minutos_acum": 39.9
        },
        {
          "orden": 4,
          "pedido": {
            "id": 549,
            "folio": "PED-20261126-000549"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.0,
          "minutos_acum": 43.9
        }
      ],
      "distancia_km": 1.05,
      "minutos": 43.9,
      "costo": 76.74
    },
    {
      "repartidor": {
        "id": 8,
        "nombre": "Diana Sepúlveda Ibarra"
      },
      "metodo": "TSP exacto",
      "zonas": [
        "San Bernabé Centro"
      ],
      "paradas": [
        {
          "orden": 1,
          "pedido": {
            "id": 544,
            "folio": "PED-20261126-000544"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.745527,
          "longitud": -100.362981,
          "tramo_km": 0.38,
          "minutos_acum": 5.0
        },
        {
          "orden": 2,
          "pedido": {
            "id": 545,
            "folio": "PED-20261126-000545"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.745527,
          "longitud": -100.362981,
          "tramo_km": 0.0,
          "minutos_acum": 9.0
        }
      ],
      "distancia_km": 0.38,
      "minutos": 9.0,
      "costo": 37.72
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 2,
    "paradas": 6,
    "distancia_km": 1.43,
    "minutos_maximo": 43.9,
    "costo": 114.46
  },
  "cambios": [
    "Retraso de 25 minutos en la ruta de Ramiro Alanís Lozano: 4 de 4 paradas quedan fuera de la promesa de 30 minutos."
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.5,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 18.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 8.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 1.3,
      "modificado": false
    }
  ],
  "paradas_fuera_de_promesa": [
    "PED-20261126-000548",
    "PED-20261126-000428",
    "PED-20261126-000547",
    "PED-20261126-000549"
  ]
}
```

### RUT-07 · Quitar un pedido · PASA

**Objetivo.** Recalcula la ruta afectada con el mismo método.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes/93/ajustes`

```http
Accept: application/json
X-Traza-Id: 636f5ea8-1bee-4eea-8fad-ac42e50445db
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "tipo": "quitar_pedido",
  "pedido_id": 548
}
```

**Respuesta.** HTTP 200 (esperado 200) · 81 ms · traza `636f5ea8-1bee-4eea-8fad-ac42e50445db`

```json
{
  "id": 93,
  "estado": "propuesto",
  "version": 3,
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "fecha": "2026-11-26",
  "metodo_pedido": "automatico",
  "rutas": [
    {
      "repartidor": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "metodo": "TSP exacto",
      "zonas": [
        "Valles de San Bernabé"
      ],
      "paradas": [
        {
          "orden": 1,
          "pedido": {
            "id": 547,
            "folio": "PED-20261126-000547"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.67,
          "minutos_acum": 5.8
        },
        {
          "orden": 2,
          "pedido": {
            "id": 549,
            "folio": "PED-20261126-000549"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.0,
          "minutos_acum": 9.8
        },
        {
          "orden": 3,
          "pedido": {
            "id": 428,
            "folio": "PED-20261126-000428"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.13,
          "minutos_acum": 14.2
        }
      ],
      "distancia_km": 0.8,
      "minutos": 14.2,
      "costo": 57.59
    },
    {
      "repartidor": {
        "id": 8,
        "nombre": "Diana Sepúlveda Ibarra"
      },
      "metodo": "TSP exacto",
      "zonas": [
        "San Bernabé Centro"
      ],
      "paradas": [
        {
          "orden": 1,
          "pedido": {
            "id": 544,
            "folio": "PED-20261126-000544"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.745527,
          "longitud": -100.362981,
          "tramo_km": 0.38,
          "minutos_acum": 5.0
        },
        {
          "orden": 2,
          "pedido": {
            "id": 545,
            "folio": "PED-20261126-000545"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.745527,
          "longitud": -100.362981,
          "tramo_km": 0.0,
          "minutos_acum": 9.0
        }
      ],
      "distancia_km": 0.38,
      "minutos": 9.0,
      "costo": 37.72
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 2,
    "paradas": 5,
    "distancia_km": 1.18,
    "minutos_maximo": 14.2,
    "costo": 95.31
  },
  "cambios": [
    "Se quitó el pedido PED-20261126-000548; la ruta de Ramiro Alanís Lozano se recalculó con 3 paradas."
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.5,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 18.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 8.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 1.3,
      "modificado": false
    }
  ],
  "paradas_fuera_de_promesa": []
}
```

### RUT-08 · Agregar de nuevo el pedido · PASA

**Objetivo.** Lo pone en la ruta con menos paradas, sin pasar del tope de 8.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes/93/ajustes`

```http
Accept: application/json
X-Traza-Id: 332ae524-bd04-4609-aca8-392fe6784b9c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "tipo": "agregar_pedido",
  "pedido_id": 548
}
```

**Respuesta.** HTTP 200 (esperado 200) · 178 ms · traza `332ae524-bd04-4609-aca8-392fe6784b9c`

```json
{
  "id": 93,
  "estado": "propuesto",
  "version": 4,
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "fecha": "2026-11-26",
  "metodo_pedido": "automatico",
  "rutas": [
    {
      "repartidor": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "metodo": "TSP exacto",
      "zonas": [
        "Valles de San Bernabé"
      ],
      "paradas": [
        {
          "orden": 1,
          "pedido": {
            "id": 547,
            "folio": "PED-20261126-000547"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.67,
          "minutos_acum": 5.8
        },
        {
          "orden": 2,
          "pedido": {
            "id": 549,
            "folio": "PED-20261126-000549"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.0,
          "minutos_acum": 9.8
        },
        {
          "orden": 3,
          "pedido": {
            "id": 428,
            "folio": "PED-20261126-000428"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.13,
          "minutos_acum": 14.2
        }
      ],
      "distancia_km": 0.8,
      "minutos": 14.2,
      "costo": 57.59
    },
    {
      "repartidor": {
        "id": 8,
        "nombre": "Diana Sepúlveda Ibarra"
      },
      "metodo": "TSP exacto",
      "zonas": [
        "San Bernabé Centro",
        "Valles de San Bernabé"
      ],
      "paradas": [
        {
          "orden": 1,
          "pedido": {
            "id": 544,
            "folio": "PED-20261126-000544"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.745527,
          "longitud": -100.362981,
          "tramo_km": 0.38,
          "minutos_acum": 5.0
        },
        {
          "orden": 2,
          "pedido": {
            "id": 545,
            "folio": "PED-20261126-000545"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.745527,
          "longitud": -100.362981,
          "tramo_km": 0.0,
          "minutos_acum": 9.0
        },
        {
          "orden": 3,
          "pedido": {
            "id": 548,
            "folio": "PED-20261126-000548"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.751679,
          "longitud": -100.366615,
          "tramo_km": 1.01,
          "minutos_acum": 15.8
        }
      ],
      "distancia_km": 1.39,
      "minutos": 15.8,
      "costo": 60.25
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 2,
    "paradas": 6,
    "distancia_km": 2.19,
    "minutos_maximo": 15.8,
    "costo": 117.84
  },
  "cambios": [
    "Se agregó el pedido PED-20261126-000548 a la ruta de Diana Sepúlveda Ibarra; ahora tiene 3 paradas."
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.5,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 18.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 8.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 1.3,
      "modificado": false
    }
  ],
  "paradas_fuera_de_promesa": []
}
```

### RUT-09 · El operador de otro microhub abre el plan · PASA

**Objetivo.** Operador y supervisor solo trabajan con el suyo.

**Petición.** `GET http://rutas:5118/api/v1/rutas/planes/93`

```http
Accept: application/json
X-Traza-Id: 45d3e0ee-94f4-41e5-8f3d-9d55178b6a0c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 24 ms · traza `45d3e0ee-94f4-41e5-8f3d-9d55178b6a0c`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "45d3e0ee-94f4-41e5-8f3d-9d55178b6a0c"
  }
}
```

### RUT-10 · Confirmar el plan · PASA

**Objetivo.** Comprueba que los pedidos sigan listos y deja las rutas en plan_ruta.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes/93/confirmar`

```http
Accept: application/json
X-Traza-Id: 0006193c-513d-4392-9d10-7c8f0db14ae9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 186 ms · traza `0006193c-513d-4392-9d10-7c8f0db14ae9`

```json
{
  "id": 93,
  "estado": "confirmado",
  "version": 4,
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "fecha": "2026-11-26",
  "metodo_pedido": "automatico",
  "rutas": [
    {
      "repartidor": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "metodo": "TSP exacto",
      "zonas": [
        "Valles de San Bernabé"
      ],
      "paradas": [
        {
          "orden": 1,
          "pedido": {
            "id": 547,
            "folio": "PED-20261126-000547"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.67,
          "minutos_acum": 5.8
        },
        {
          "orden": 2,
          "pedido": {
            "id": 549,
            "folio": "PED-20261126-000549"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.0,
          "minutos_acum": 9.8
        },
        {
          "orden": 3,
          "pedido": {
            "id": 428,
            "folio": "PED-20261126-000428"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.13,
          "minutos_acum": 14.2
        }
      ],
      "distancia_km": 0.8,
      "minutos": 14.2,
      "costo": 57.59
    },
    {
      "repartidor": {
        "id": 8,
        "nombre": "Diana Sepúlveda Ibarra"
      },
      "metodo": "TSP exacto",
      "zonas": [
        "San Bernabé Centro",
        "Valles de San Bernabé"
      ],
      "paradas": [
        {
          "orden": 1,
          "pedido": {
            "id": 544,
            "folio": "PED-20261126-000544"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.745527,
          "longitud": -100.362981,
          "tramo_km": 0.38,
          "minutos_acum": 5.0
        },
        {
          "orden": 2,
          "pedido": {
            "id": 545,
            "folio": "PED-20261126-000545"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.745527,
          "longitud": -100.362981,
          "tramo_km": 0.0,
          "minutos_acum": 9.0
        },
        {
          "orden": 3,
          "pedido": {
            "id": 548,
            "folio": "PED-20261126-000548"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.751679,
          "longitud": -100.366615,
          "tramo_km": 1.01,
          "minutos_acum": 15.8
        }
      ],
      "distancia_km": 1.39,
      "minutos": 15.8,
      "costo": 60.25
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 2,
    "paradas": 6,
    "distancia_km": 2.19,
    "minutos_maximo": 15.8,
    "costo": 117.84
  },
  "cambios": [
    "Se agregó el pedido PED-20261126-000548 a la ruta de Diana Sepúlveda Ibarra; ahora tiene 3 paradas."
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.5,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 18.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 8.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 1.3,
      "modificado": false
    }
  ]
}
```

**Evidencia en PostgreSQL.** `SELECT id, repartidor_id, metodo, paradas, distancia_km, minutos, costo_estimado FROM plan_ruta WHERE plan_despacho_id = %s ORDER BY id`

```json
[
  {
    "id": 90,
    "repartidor_id": 7,
    "metodo": "TSP exacto",
    "paradas": 3,
    "distancia_km": "0.80",
    "minutos": "14.2",
    "costo_estimado": "57.59"
  },
  {
    "id": 91,
    "repartidor_id": 8,
    "metodo": "TSP exacto",
    "paradas": 3,
    "distancia_km": "1.39",
    "minutos": "15.8",
    "costo_estimado": "60.25"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT count(*) AS paradas FROM plan_ruta_parada WHERE plan_ruta_id IN (SELECT id FROM plan_ruta WHERE plan_despacho_id = %s)`

```json
[
  {
    "paradas": 6
  }
]
```

### RUT-11 · Confirmar otra vez · PASA

**Objetivo.** Un plan confirmado no se vuelve a confirmar.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes/93/confirmar`

```http
Accept: application/json
X-Traza-Id: ead3063b-b821-4a86-b606-c903d39e723e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 409 (esperado 409) · 53 ms · traza `ead3063b-b821-4a86-b606-c903d39e723e`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Solo se confirma un plan propuesto; este está confirmado.",
    "traza_id": "ead3063b-b821-4a86-b606-c903d39e723e"
  }
}
```

### RUT-12 · Planes guardados · PASA

**Objetivo.** Lista con estado, rutas, paradas, distancia y costo.

**Petición.** `GET http://rutas:5118/api/v1/rutas/planes?microhub_id=1`

```http
Accept: application/json
X-Traza-Id: ab4910bb-f720-4ac8-8cac-e7a8fbdfe03d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 43 ms · traza `ab4910bb-f720-4ac8-8cac-e7a8fbdfe03d`

```json
{
  "datos": [
    {
      "id": 93,
      "estado": "confirmado",
      "version": 4,
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "fecha": "2026-11-26",
      "rutas": 2,
      "paradas": 6,
      "distancia_km": 2.19,
      "costo": 117.84,
      "creado_por": 5,
      "creado_en": "2026-11-26T14:20:01-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 1,
    "paginas": 1
  }
}
```

### RUT-13 · Cancelar un plan propuesto · PASA

**Objetivo.** Un plan que no se confirmó se cancela.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes/94/cancelar`

```http
Accept: application/json
X-Traza-Id: c484d948-bd39-41d8-849e-1e3ade9ae588
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 80 ms · traza `c484d948-bd39-41d8-849e-1e3ade9ae588`

```json
{
  "id": 94,
  "estado": "cancelado",
  "version": 1,
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "fecha": "2026-11-26",
  "metodo_pedido": "automatico",
  "rutas": [
    {
      "repartidor": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "metodo": "TSP exacto",
      "zonas": [
        "Valles de San Bernabé"
      ],
      "paradas": [
        {
          "orden": 1,
          "pedido": {
            "id": 548,
            "folio": "PED-20261126-000548"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.751679,
          "longitud": -100.366615,
          "tramo_km": 0.63,
          "minutos_acum": 5.7
        },
        {
          "orden": 2,
          "pedido": {
            "id": 428,
            "folio": "PED-20261126-000428"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.29,
          "minutos_acum": 10.5
        },
        {
          "orden": 3,
          "pedido": {
            "id": 547,
            "folio": "PED-20261126-000547"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.13,
          "minutos_acum": 14.9
        },
        {
          "orden": 4,
          "pedido": {
            "id": 549,
            "folio": "PED-20261126-000549"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.0,
          "minutos_acum": 18.9
        }
      ],
      "distancia_km": 1.05,
      "minutos": 18.9,
      "costo": 76.74
    },
    {
      "repartidor": {
        "id": 8,
        "nombre": "Diana Sepúlveda Ibarra"
      },
      "metodo": "TSP exacto",
      "zonas": [
        "San Bernabé Centro"
      ],
      "paradas": [
        {
          "orden": 1,
          "pedido": {
            "id": 544,
            "folio": "PED-20261126-000544"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.745527,
          "longitud": -100.362981,
          "tramo_km": 0.38,
          "minutos_acum": 5.0
        },
        {
          "orden": 2,
          "pedido": {
            "id": 545,
            "folio": "PED-20261126-000545"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.745527,
          "longitud": -100.362981,
          "tramo_km": 0.0,
          "minutos_acum": 9.0
        }
      ],
      "distancia_km": 0.38,
      "minutos": 9.0,
      "costo": 37.72
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 2,
    "paradas": 6,
    "distancia_km": 1.43,
    "minutos_maximo": 18.9,
    "costo": 114.46
  },
  "cambios": [],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.5,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 18.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 8.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 1.3,
      "modificado": false
    }
  ]
}
```

### RUT-14 · Un microhub sin pedidos listos · PASA

**Objetivo.** No hay nada que despachar.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/json
X-Traza-Id: 3b61fd2d-521f-442b-99df-0d8f6d325703
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 3
}
```

**Respuesta.** HTTP 422 (esperado 422) · 140 ms · traza `3b61fd2d-521f-442b-99df-0d8f6d325703`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "No hay pedidos listos para despachar en ese microhub.",
    "traza_id": "3b61fd2d-521f-442b-99df-0d8f6d325703"
  }
}
```

### RUT-15 · Pedidos que no están listos · PASA

**Objetivo.** Un pedido ajeno o no listo se rechaza.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/json
X-Traza-Id: 06b2dcf9-506b-4239-934e-f46377df9ccc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "pedido_ids": [
    999999
  ]
}
```

**Respuesta.** HTTP 422 (esperado 422) · 150 ms · traza `06b2dcf9-506b-4239-934e-f46377df9ccc`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Algunos pedidos no están listos para despachar en ese microhub.",
    "detalles": [
      {
        "campo": "pedido_ids",
        "mensaje": "El pedido 999999 no está listo o no es de ese microhub."
      }
    ],
    "traza_id": "06b2dcf9-506b-4239-934e-f46377df9ccc"
  }
}
```

### RUT-16 · El operador planea otro microhub · PASA

**Objetivo.** No puede.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/json
X-Traza-Id: 3573447c-0ce0-4ad9-8e75-a80bf31062ad
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "pedido_ids": [
    428,
    544,
    545,
    547,
    548,
    549
  ]
}
```

**Respuesta.** HTTP 403 (esperado 403) · 5 ms · traza `3573447c-0ce0-4ad9-8e75-a80bf31062ad`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "3573447c-0ce0-4ad9-8e75-a80bf31062ad"
  }
}
```

### RUT-17 · El auditor intenta planear · PASA

**Objetivo.** Consulta, no planea.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/json
X-Traza-Id: af14db1d-b07f-4fea-b90b-327bfc712d6f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1
}
```

**Respuesta.** HTTP 403 (esperado 403) · 57 ms · traza `af14db1d-b07f-4fea-b90b-327bfc712d6f`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "af14db1d-b07f-4fea-b90b-327bfc712d6f"
  }
}
```

### RUT-18 · Plan en XML con lista de pedidos · PASA

**Objetivo.** El cuerpo XML lleva la lista de pedidos y se valida contra rutas.xsd.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/xml
X-Traza-Id: c1337744-1bf1-4edd-bac5-51fca76f3836
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><ruta_plan_nuevo xmlns="urn:microhubs:v1"><microhub_id>1</microhub_id><pedido_ids><id>428</id><id>544</id><id>545</id></pedido_ids><metodo>exacto</metodo></ruta_plan_nuevo>
```

**Respuesta.** HTTP 200 (esperado 200) · 324 ms · traza `c1337744-1bf1-4edd-bac5-51fca76f3836`

```xml
<?xml version='1.0' encoding='utf-8'?>
<ruta_plan xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id xsi:nil="true" /><estado>calculo</estado><version>1</version><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><fecha>2026-11-26</fecha><metodo_pedido>exacto</metodo_pedido><rutas><ruta><repartidor><id>7</id><nombre>Ramiro Alanís Lozano</nombre></repartidor><metodo>TSP exacto</metodo><zonas><nombre_zona>San Bernabé Centro</nombre_zona></zonas><paradas><parada><orden>1</orden><pedido><id>544</id><folio>PED-20261126-000544</folio></pedido><zona><id>1</id><nombre>San Bernabé Centro</nombre></zona><latitud>25.745527</latitud><longitud>-100.362981</longitud><tramo_km>0.38</tramo_km><minutos_acum>5</minutos_acum></parada><parada><orden>2</orden><pedido><id>545</id><folio>PED-20261126-000545</folio></pedido><zona><id>1</id><nombre>San Bernabé Centro</nombre></zona><latitud>25.745527</latitud><longitud>-100.362981</longitud><tramo_km>0</tramo_km><minutos_acum>9</minutos_acum></parada></paradas><distancia_km>0.38</distancia_km><minutos>9</minutos><costo>37.72</costo></ruta><ruta><repartidor><id>8</id><nombre>Diana Sepúlveda Ibarra</nombre></repartidor><metodo>TSP exacto</metodo><zonas><nombre_zona>Valles de San Bernabé</nombre_zona></zonas><paradas><parada><orden>1</orden><pedido><id>428</id><folio>PED-20261126-000428</folio></pedido><zona><id>2</id><nombre>Valles de San Bernabé</nombre></zona><latitud>25.753225</latitud><longitud>-100.365213</longitud><tramo_km>0.77</tramo_km><minutos_acum>6.1</minutos_acum></parada></paradas><distancia_km>0.77</distancia_km><minutos>6.1</minutos><costo>21.47</costo></ruta></rutas><sin_asignar /><total><rutas>2</rutas><paradas>3</paradas><distancia_km>1.15</distancia_km><minutos_maximo>9</minutos_maximo><costo>59.19</costo></total><cambios /><supuestos_usados><supuesto><clave>velocidad_reparto_kmh</clave><valor>22</valor><modificado>false</modificado></supuesto><supuesto><clave>tiempo_servicio_min</clave><valor>4</valor><modificado>false</modificado></supuesto><supuesto><clave>costo_km_reparto</clave><valor>4.5</valor><modificado>false</modificado></supuesto><supuesto><clave>costo_base_entrega</clave><valor>18</valor><modificado>false</modificado></supuesto><supuesto><clave>max_paradas_repartidor</clave><valor>8</valor><modificado>false</modificado></supuesto><supuesto><clave>factor_rodeo_distancia</clave><valor>1.3</valor><modificado>false</modificado></supuesto></supuestos_usados></ruta_plan>
```

### RUT-19 · Supuestos de las rutas · PASA

**Objetivo.** Velocidad, tiempo por parada, costo por km, tope de paradas y rodeo.

**Petición.** `GET http://rutas:5118/api/v1/rutas/supuestos`

```http
Accept: application/json
X-Traza-Id: 3575225a-5fdc-4843-aef1-5029a75961bf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 31 ms · traza `3575225a-5fdc-4843-aef1-5029a75961bf`

```json
{
  "datos": [
    {
      "clave": "********",
      "valor": "30",
      "unidad": "minutos",
      "origen": "normativo",
      "justificacion": "Promesa de entrega que fija el equipo: llegar en 30 minutos o menos desde que sale el repartidor.",
      "como_calibrar": "Se revisa con el tiempo real de las entregas cerradas."
    },
    {
      "clave": "********",
      "valor": "18",
      "unidad": "MXN",
      "origen": "supuesto",
      "justificacion": "Pago fijo por entrega al repartidor; se suma al costo por di…(186 caracteres)",
      "como_calibrar": "Lo que se paga de verdad por entrega en el contrato o en la nómina de repartidores; al corregirlo, corregir también el concepto en costos."
    },
    {
      "clave": "********",
      "valor": "4.5",
      "unidad": "MXN/km",
      "origen": "supuesto",
      "justificacion": "Combustible, mantenimiento y desgaste por kilómetro de una m…(204 caracteres)",
      "como_calibrar": "Gasto real de combustible y mantenimiento entre los kilómetr…(147 caracteres)"
    },
    {
      "clave": "********",
      "valor": "1.3",
      "unidad": "veces",
      "origen": "supuesto",
      "justificacion": "La distancia por calle es mayor que la línea recta; en una r…(220 caracteres)",
      "como_calibrar": "Cociente entre la distancia del recorrido GPS y la distancia en línea recta entre el microhub y el domicilio, en entregas cerradas."
    },
    {
      "clave": "********",
      "valor": "8",
      "unidad": "paradas",
      "origen": "normativo",
      "justificacion": "Tope que fija el equipo: con más paradas el pedido llega frí…(149 caracteres)",
      "como_calibrar": "Se revisa si el tiempo promedio de entrega supera la promesa de cobertura."
    },
    {
      "clave": "********",
      "valor": "3",
      "unidad": "paradas",
      "origen": "supuesto",
      "justificacion": "Paradas promedio de una salida cuando los pedidos se agrupan por zona. Reparte el costo del regreso al microhub entre ellas.",
      "como_calibrar": "Promedio de la columna paradas de plan_ruta."
    },
    {
      "clave": "********",
      "valor": "4",
      "unidad": "minutos",
      "origen": "supuesto",
      "justificacion": "Minutos que el repartidor pasa en cada parada: estacionar, entregar, cobrar y confirmar con el cliente.",
      "como_calibrar": "Diferencia entre la llegada al domicilio y el cierre de la entrega en el recorrido GPS."
    },
    {
      "clave": "********",
      "valor": "22",
      "unidad": "km/h",
      "origen": "supuesto",
      "justificacion": "Velocidad media de un repartidor en moto o bicicleta dentro …(180 caracteres)",
      "como_calibrar": "Dividir la distancia del recorrido GPS entre su duración en …(147 caracteres)"
    }
  ]
}
```

## Servicio simulacion · puerto 5121

### SIM-01 · Poner una simulación en cola · PASA

**Objetivo.** Junta la entrada de otros servicios, la guarda y responde 202 sin esperar el resultado.

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones`

```http
Accept: application/json
X-Traza-Id: a240603c-ba85-4a9b-9e3f-da3d41ad1d62
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "dias": 14,
  "replicas": 100,
  "semilla": 11
}
```

**Respuesta.** HTTP 202 (esperado 202) · 594 ms · traza `a240603c-ba85-4a9b-9e3f-da3d41ad1d62`

```json
{
  "id": "25c5f9b3-04b6-4b10-be41-6d47a2c79f96",
  "nombre": "Simulación de Microhub San Bernabé Centro 2026-11-26",
  "estado": "en_cola",
  "objeto": {
    "tipo": "microhub",
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "semilla": 11,
  "version_modelo": "1.0",
  "dias": 14,
  "replicas": 100,
  "entrada": {
    "pedidos_dia": 23.6,
    "ticket": 134.83,
    "margen_bruto": 0.28,
    "costos_fijos_mes": 69500.0,
    "costo_variable_pedido": 32.61,
    "dias_mes": 30.0,
    "operadores": 3,
    "repartidores": 3,
    "capacidad_fisica": 150,
    "horas": 10.0,
    "distancia_km": 2.4,
    "ausentismo": 0.05,
    "variacion_demanda": 0.1,
    "indice_semanal": [
      0.893,
      0.844,
      0.884,
      0.937,
      1.154,
      1.303,
      1.028
    ],
    "dia_inicio": 4,
    "origen_de_datos": [
      {
        "dato": "costos_fijos",
        "fuente": "costos"
      },
      {
        "dato": "costo_variable_pedido",
        "fuente": "costos"
      },
      {
        "dato": "ticket",
        "fuente": "demanda"
      },
      {
        "dato": "margen_bruto",
        "fuente": "configuracion"
      },
      {
        "dato": "pedidos_dia",
        "fuente": "demanda_repartida"
      },
      {
        "dato": "operadores",
        "fuente": "capacidad"
      },
      {
        "dato": "repartidores",
        "fuente": "capacidad"
      },
      {
        "dato": "capacidad_fisica",
        "fuente": "capacidad"
      },
      {
        "dato": "horas",
        "fuente": "configuracion"
      },
      {
        "dato": "distancia_km",
        "fuente": "configuracion"
      },
      {
        "dato": "ausentismo",
        "fuente": "configuracion"
      },
      {
        "dato": "variacion_demanda",
        "fuente": "configuracion"
      },
      {
        "dato": "indice_semanal",
        "fuente": "demanda"
      }
    ]
  },
  "resultados": null,
  "huella": null,
  "repeticion_de": null,
  "reproducible": null,
  "error": null,
  "creado_por": 5,
  "creado_en": "2026-11-26T14:20:04-06:00",
  "inicio_en": null,
  "fin_en": null,
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 10.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 20.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 10.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 85.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.05,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.1,
      "modificado": false
    }
  ]
}
```

**Explicación.** La entrada (demanda, ticket, costos, personal, capacidad y su origen) queda guardada en la ejecución: con ella y la semilla el resultado es siempre el mismo. Un hilo del servicio la toma de la cola con FOR UPDATE SKIP LOCKED.

**Evidencia en PostgreSQL.** `SELECT id, estado, semilla, version_modelo, creado_por, parametros::jsonb -> 'replicas' AS replicas FROM simulacion_ejecucion WHERE id = %s`

```json
[
  {
    "id": "25c5f9b3-04b6-4b10-be41-6d47a2c79f96",
    "estado": "en_cola",
    "semilla": 11,
    "version_modelo": "1.0",
    "creado_por": 5,
    "replicas": 100
  }
]
```

### SIM-02 · Resultados de la simulación · PASA

**Objetivo.** Media y percentiles 10, 50 y 90 de utilidad, pedidos atendidos y rechazados; probabilidad de perder.

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones/25c5f9b3-04b6-4b10-be41-6d47a2c79f96`

```http
Accept: application/json
X-Traza-Id: 77cb84cf-2bb0-4329-91eb-1f4e8e5a3b39
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 36 ms · traza `77cb84cf-2bb0-4329-91eb-1f4e8e5a3b39`

```json
{
  "id": "25c5f9b3-04b6-4b10-be41-6d47a2c79f96",
  "nombre": "Simulación de Microhub San Bernabé Centro 2026-11-26",
  "estado": "terminada",
  "objeto": {
    "tipo": "microhub",
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "semilla": 11,
  "version_modelo": "1.0",
  "dias": 14,
  "replicas": 100,
  "entrada": {
    "pedidos_dia": 23.6,
    "ticket": 134.83,
    "margen_bruto": 0.28,
    "costos_fijos_mes": 69500.0,
    "costo_variable_pedido": 32.61,
    "dias_mes": 30.0,
    "operadores": 3,
    "repartidores": 3,
    "capacidad_fisica": 150,
    "horas": 10.0,
    "distancia_km": 2.4,
    "ausentismo": 0.05,
    "variacion_demanda": 0.1,
    "indice_semanal": [
      0.893,
      0.844,
      0.884,
      0.937,
      1.154,
      1.303,
      1.028
    ],
    "dia_inicio": 4,
    "origen_de_datos": [
      {
        "dato": "costos_fijos",
        "fuente": "costos"
      },
      {
        "dato": "costo_variable_pedido",
        "fuente": "costos"
      },
      {
        "dato": "ticket",
        "fuente": "demanda"
      },
      {
        "dato": "margen_bruto",
        "fuente": "configuracion"
      },
      {
        "dato": "pedidos_dia",
        "fuente": "demanda_repartida"
      },
      {
        "dato": "operadores",
        "fuente": "capacidad"
      },
      {
        "dato": "repartidores",
        "fuente": "capacidad"
      },
      {
        "dato": "capacidad_fisica",
        "fuente": "capacidad"
      },
      {
        "dato": "horas",
        "fuente": "configuracion"
      },
      {
        "dato": "distancia_km",
        "fuente": "configuracion"
      },
      {
        "dato": "ausentismo",
        "fuente": "configuracion"
      },
      {
        "dato": "variacion_demanda",
        "fuente": "configuracion"
      },
      {
        "dato": "indice_semanal",
        "fuente": "demanda"
      }
    ]
  },
  "resultados": {
    "dias": 14,
    "replicas": 100,
    "metricas": [
      {
        "clave": "********",
        "etiqueta": "Utilidad del periodo",
        "unidad": "MXN",
        "media": -30726.0565,
        "p10": -30849.9884,
        "p50": -30731.1989,
        "p90": -30592.3541,
        "minimo": -30957.4645,
        "maximo": -30463.7941
      },
      {
        "clave": "********",
        "etiqueta": "Ingreso del periodo",
        "unidad": "MXN",
        "media": 44763.56,
        "p10": 41514.157,
        "p50": 44628.73,
        "p90": 48269.14,
        "minimo": 38696.21,
        "maximo": 51639.89
      },
      {
        "clave": "********",
        "etiqueta": "Pedidos atendidos",
        "unidad": "pedidos",
        "media": 332.0,
        "p10": 307.9,
        "p50": 331.0,
        "p90": 358.0,
        "minimo": 287.0,
        "maximo": 383.0
      },
      {
        "clave": "********",
        "etiqueta": "Pedidos rechazados por falta de capacidad",
        "unidad": "pedidos",
        "media": 0.0,
        "p10": 0.0,
        "p50": 0.0,
        "p90": 0.0,
        "minimo": 0.0,
        "maximo": 0.0
      },
      {
        "clave": "********",
        "etiqueta": "Utilización de la capacidad",
        "unidad": "%",
        "media": 16.6967,
        "p10": 15.1808,
        "p50": 16.5512,
        "p90": 18.2782,
        "minimo": 14.3747,
        "maximo": 19.9776
      },
      {
        "clave": "********",
        "etiqueta": "Días saturados",
        "unidad": "días",
        "media": 0.0,
        "p10": 0.0,
        "p50": 0.0,
        "p90": 0.0,
        "minimo": 0.0,
        "maximo": 0.0
      }
    ],
    "prob_perdida_pct": 100.0,
    "dias_saturados_pct": 0.0,
    "contraste": {
      "utilidad_sin_variacion": -30734.2844,
      "utilidad_media": -30726.0565,
      "diferencia": 8.2279,
      "capacidad_dia_con_todo_el_personal": 150.0
    },
    "lectura": [
      "En 100 réplicas de 14 días, la utilidad media fue de -30,726 MXN (P10 -30,850, P90 -30,592).",
      "Hubo pérdida en 100.0 % de las réplicas y 0.0 % de los días estuvieron saturados.",
      "La capacidad alcanzó para casi toda la demanda.",
      "Con estos supuestos, lo más probable es perder dinero."
    ],
    "serie": [
      {
        "dia": 1,
        "demanda_media": 22.37,
        "atendidos_media": 22.37,
        "utilidad_acumulada_media": -2201.6312
      },
      {
        "dia": 2,
        "demanda_media": 26.87,
        "atendidos_media": 26.87,
        "utilidad_acumulada_media": -4380.1216
      },
      {
        "dia": 3,
        "demanda_media": 30.63,
        "atendidos_media": 30.63,
        "utilidad_acumulada_media": -6539.2765
      },
      {
        "dia": 4,
        "demanda_media": 24.91,
        "atendidos_media": 24.91,
        "utilidad_acumulada_media": -8727.846
      },
      {
        "dia": 5,
        "demanda_media": 21.32,
        "atendidos_media": 21.32,
        "utilidad_acumulada_media": -10934.8767
      },
      {
        "dia": 6,
        "demanda_media": 20.2,
        "atendidos_media": 20.2,
        "utilidad_acumulada_media": -13147.6669
      },
      {
        "dia": 7,
        "demanda_media": 20.31,
        "atendidos_media": 20.31,
        "utilidad_acumulada_media": -15359.8914
      },
      {
        "dia": 8,
        "demanda_media": 22.51,
        "atendidos_media": 22.51,
        "utilidad_acumulada_media": -17560.8026
      },
      {
        "dia": 9,
        "demanda_media": 26.5,
        "atendidos_media": 26.5,
        "utilidad_acumulada_media": -19741.1957
      },
      {
        "dia": 10,
        "demanda_media": 30.91,
        "atendidos_media": 30.91,
        "utilidad_acumulada_media": -21898.9108
      },
      {
        "dia": 11,
        "demanda_media": 24.61,
        "atendidos_media": 24.61,
        "utilidad_acumulada_media": -24089.023
      },
      {
        "dia": 12,
        "demanda_media": 21.06,
        "atendidos_media": 21.06,
        "utilidad_acumulada_media": -26297.3907
      },
      {
        "dia": 13,
        "demanda_media": 18.56,
        "atendidos_media": 18.56,
        "utilidad_acumulada_media": -28518.6144
      },
      {
        "dia": 14,
        "demanda_media": 21.24,
        "atendidos_media": 21.24,
        "utilidad_acumulada_media": -30726.0565
      }
    ]
  },
  "huella": "7b88bea8fcb6e15b0dc9714e258549fc8ff623fb13d10d91c72f63b04deb0054",
  "repeticion_de": null,
  "reproducible": null,
  "error": null,
  "creado_por": 5,
  "creado_en": "2026-11-26T14:20:04-06:00",
  "inicio_en": "2026-11-26T14:20:05-06:00",
  "fin_en": "2026-11-26T14:20:05-06:00",
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 10.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 20.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 10.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 85.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.05,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.1,
      "modificado": false
    }
  ]
}
```

**Explicación.** Monte Carlo día por día: demanda de Poisson por el índice semanal, ausentismo de operadores y repartidores, capacidad con el personal presente. La huella es el SHA-256 de los resultados.

**Evidencia en PostgreSQL.** `SELECT estado, huella, inicio_en IS NOT NULL AS inicio, fin_en IS NOT NULL AS fin, intentos FROM simulacion_ejecucion WHERE id = %s`

```json
[
  {
    "estado": "terminada",
    "huella": "7b88bea8fcb6e15b0dc9714e258549fc8ff623fb13d10d91c72f63b04deb0054",
    "inicio": true,
    "fin": true,
    "intentos": 1
  }
]
```

### SIM-03 · Repetir con la misma entrada y semilla · PASA

**Objetivo.** Debe dar exactamente lo mismo.

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones/25c5f9b3-04b6-4b10-be41-6d47a2c79f96/repetir`

```http
Accept: application/json
X-Traza-Id: 61cd5e85-9f5b-4136-a314-2c7fe99f3ec0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 202 (esperado 202) · 104 ms · traza `61cd5e85-9f5b-4136-a314-2c7fe99f3ec0`

```json
{
  "id": "357fa160-4fff-4b90-8c4e-28c9cf1b62e1",
  "nombre": "Repetición de Simulación de Microhub San Bernabé Centro 2026-11-26",
  "estado": "ejecutando",
  "objeto": {
    "tipo": "microhub",
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "semilla": 11,
  "version_modelo": "1.0",
  "dias": 14,
  "replicas": 100,
  "entrada": {
    "pedidos_dia": 23.6,
    "ticket": 134.83,
    "margen_bruto": 0.28,
    "costos_fijos_mes": 69500.0,
    "costo_variable_pedido": 32.61,
    "dias_mes": 30.0,
    "operadores": 3,
    "repartidores": 3,
    "capacidad_fisica": 150,
    "horas": 10.0,
    "distancia_km": 2.4,
    "ausentismo": 0.05,
    "variacion_demanda": 0.1,
    "indice_semanal": [
      0.893,
      0.844,
      0.884,
      0.937,
      1.154,
      1.303,
      1.028
    ],
    "dia_inicio": 4,
    "origen_de_datos": [
      {
        "dato": "costos_fijos",
        "fuente": "costos"
      },
      {
        "dato": "costo_variable_pedido",
        "fuente": "costos"
      },
      {
        "dato": "ticket",
        "fuente": "demanda"
      },
      {
        "dato": "margen_bruto",
        "fuente": "configuracion"
      },
      {
        "dato": "pedidos_dia",
        "fuente": "demanda_repartida"
      },
      {
        "dato": "operadores",
        "fuente": "capacidad"
      },
      {
        "dato": "repartidores",
        "fuente": "capacidad"
      },
      {
        "dato": "capacidad_fisica",
        "fuente": "capacidad"
      },
      {
        "dato": "horas",
        "fuente": "configuracion"
      },
      {
        "dato": "distancia_km",
        "fuente": "configuracion"
      },
      {
        "dato": "ausentismo",
        "fuente": "configuracion"
      },
      {
        "dato": "variacion_demanda",
        "fuente": "configuracion"
      },
      {
        "dato": "indice_semanal",
        "fuente": "demanda"
      }
    ]
  },
  "resultados": null,
  "huella": null,
  "repeticion_de": "25c5f9b3-04b6-4b10-be41-6d47a2c79f96",
  "reproducible": null,
  "error": null,
  "creado_por": 5,
  "creado_en": "2026-11-26T14:20:06-06:00",
  "inicio_en": "2026-11-26T14:20:06-06:00",
  "fin_en": null,
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 10.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 20.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 10.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 85.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.05,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.1,
      "modificado": false
    }
  ]
}
```

### SIM-04 · La repetición coincide · PASA

**Objetivo.** Misma huella: la simulación es reproducible.

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones/357fa160-4fff-4b90-8c4e-28c9cf1b62e1`

```http
Accept: application/json
X-Traza-Id: e8fa8491-667f-4625-aacc-15cc3f74ed70
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 73 ms · traza `e8fa8491-667f-4625-aacc-15cc3f74ed70`

```json
{
  "id": "357fa160-4fff-4b90-8c4e-28c9cf1b62e1",
  "nombre": "Repetición de Simulación de Microhub San Bernabé Centro 2026-11-26",
  "estado": "terminada",
  "objeto": {
    "tipo": "microhub",
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "semilla": 11,
  "version_modelo": "1.0",
  "dias": 14,
  "replicas": 100,
  "entrada": {
    "pedidos_dia": 23.6,
    "ticket": 134.83,
    "margen_bruto": 0.28,
    "costos_fijos_mes": 69500.0,
    "costo_variable_pedido": 32.61,
    "dias_mes": 30.0,
    "operadores": 3,
    "repartidores": 3,
    "capacidad_fisica": 150,
    "horas": 10.0,
    "distancia_km": 2.4,
    "ausentismo": 0.05,
    "variacion_demanda": 0.1,
    "indice_semanal": [
      0.893,
      0.844,
      0.884,
      0.937,
      1.154,
      1.303,
      1.028
    ],
    "dia_inicio": 4,
    "origen_de_datos": [
      {
        "dato": "costos_fijos",
        "fuente": "costos"
      },
      {
        "dato": "costo_variable_pedido",
        "fuente": "costos"
      },
      {
        "dato": "ticket",
        "fuente": "demanda"
      },
      {
        "dato": "margen_bruto",
        "fuente": "configuracion"
      },
      {
        "dato": "pedidos_dia",
        "fuente": "demanda_repartida"
      },
      {
        "dato": "operadores",
        "fuente": "capacidad"
      },
      {
        "dato": "repartidores",
        "fuente": "capacidad"
      },
      {
        "dato": "capacidad_fisica",
        "fuente": "capacidad"
      },
      {
        "dato": "horas",
        "fuente": "configuracion"
      },
      {
        "dato": "distancia_km",
        "fuente": "configuracion"
      },
      {
        "dato": "ausentismo",
        "fuente": "configuracion"
      },
      {
        "dato": "variacion_demanda",
        "fuente": "configuracion"
      },
      {
        "dato": "indice_semanal",
        "fuente": "demanda"
      }
    ]
  },
  "resultados": {
    "dias": 14,
    "replicas": 100,
    "metricas": [
      {
        "clave": "********",
        "etiqueta": "Utilidad del periodo",
        "unidad": "MXN",
        "media": -30726.0565,
        "p10": -30849.9884,
        "p50": -30731.1989,
        "p90": -30592.3541,
        "minimo": -30957.4645,
        "maximo": -30463.7941
      },
      {
        "clave": "********",
        "etiqueta": "Ingreso del periodo",
        "unidad": "MXN",
        "media": 44763.56,
        "p10": 41514.157,
        "p50": 44628.73,
        "p90": 48269.14,
        "minimo": 38696.21,
        "maximo": 51639.89
      },
      {
        "clave": "********",
        "etiqueta": "Pedidos atendidos",
        "unidad": "pedidos",
        "media": 332.0,
        "p10": 307.9,
        "p50": 331.0,
        "p90": 358.0,
        "minimo": 287.0,
        "maximo": 383.0
      },
      {
        "clave": "********",
        "etiqueta": "Pedidos rechazados por falta de capacidad",
        "unidad": "pedidos",
        "media": 0.0,
        "p10": 0.0,
        "p50": 0.0,
        "p90": 0.0,
        "minimo": 0.0,
        "maximo": 0.0
      },
      {
        "clave": "********",
        "etiqueta": "Utilización de la capacidad",
        "unidad": "%",
        "media": 16.6967,
        "p10": 15.1808,
        "p50": 16.5512,
        "p90": 18.2782,
        "minimo": 14.3747,
        "maximo": 19.9776
      },
      {
        "clave": "********",
        "etiqueta": "Días saturados",
        "unidad": "días",
        "media": 0.0,
        "p10": 0.0,
        "p50": 0.0,
        "p90": 0.0,
        "minimo": 0.0,
        "maximo": 0.0
      }
    ],
    "prob_perdida_pct": 100.0,
    "dias_saturados_pct": 0.0,
    "contraste": {
      "utilidad_sin_variacion": -30734.2844,
      "utilidad_media": -30726.0565,
      "diferencia": 8.2279,
      "capacidad_dia_con_todo_el_personal": 150.0
    },
    "lectura": [
      "En 100 réplicas de 14 días, la utilidad media fue de -30,726 MXN (P10 -30,850, P90 -30,592).",
      "Hubo pérdida en 100.0 % de las réplicas y 0.0 % de los días estuvieron saturados.",
      "La capacidad alcanzó para casi toda la demanda.",
      "Con estos supuestos, lo más probable es perder dinero."
    ],
    "serie": [
      {
        "dia": 1,
        "demanda_media": 22.37,
        "atendidos_media": 22.37,
        "utilidad_acumulada_media": -2201.6312
      },
      {
        "dia": 2,
        "demanda_media": 26.87,
        "atendidos_media": 26.87,
        "utilidad_acumulada_media": -4380.1216
      },
      {
        "dia": 3,
        "demanda_media": 30.63,
        "atendidos_media": 30.63,
        "utilidad_acumulada_media": -6539.2765
      },
      {
        "dia": 4,
        "demanda_media": 24.91,
        "atendidos_media": 24.91,
        "utilidad_acumulada_media": -8727.846
      },
      {
        "dia": 5,
        "demanda_media": 21.32,
        "atendidos_media": 21.32,
        "utilidad_acumulada_media": -10934.8767
      },
      {
        "dia": 6,
        "demanda_media": 20.2,
        "atendidos_media": 20.2,
        "utilidad_acumulada_media": -13147.6669
      },
      {
        "dia": 7,
        "demanda_media": 20.31,
        "atendidos_media": 20.31,
        "utilidad_acumulada_media": -15359.8914
      },
      {
        "dia": 8,
        "demanda_media": 22.51,
        "atendidos_media": 22.51,
        "utilidad_acumulada_media": -17560.8026
      },
      {
        "dia": 9,
        "demanda_media": 26.5,
        "atendidos_media": 26.5,
        "utilidad_acumulada_media": -19741.1957
      },
      {
        "dia": 10,
        "demanda_media": 30.91,
        "atendidos_media": 30.91,
        "utilidad_acumulada_media": -21898.9108
      },
      {
        "dia": 11,
        "demanda_media": 24.61,
        "atendidos_media": 24.61,
        "utilidad_acumulada_media": -24089.023
      },
      {
        "dia": 12,
        "demanda_media": 21.06,
        "atendidos_media": 21.06,
        "utilidad_acumulada_media": -26297.3907
      },
      {
        "dia": 13,
        "demanda_media": 18.56,
        "atendidos_media": 18.56,
        "utilidad_acumulada_media": -28518.6144
      },
      {
        "dia": 14,
        "demanda_media": 21.24,
        "atendidos_media": 21.24,
        "utilidad_acumulada_media": -30726.0565
      }
    ]
  },
  "huella": "7b88bea8fcb6e15b0dc9714e258549fc8ff623fb13d10d91c72f63b04deb0054",
  "repeticion_de": "25c5f9b3-04b6-4b10-be41-6d47a2c79f96",
  "reproducible": true,
  "error": null,
  "creado_por": 5,
  "creado_en": "2026-11-26T14:20:06-06:00",
  "inicio_en": "2026-11-26T14:20:06-06:00",
  "fin_en": "2026-11-26T14:20:06-06:00",
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 10.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 20.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 10.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 85.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.05,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.1,
      "modificado": false
    }
  ]
}
```

**Evidencia en PostgreSQL.** `SELECT id, estado, huella, parametros::jsonb ->> 'repeticion_de' AS repite_a FROM simulacion_ejecucion WHERE id = ANY(%s::uuid[]) ORDER BY creado_en`

```json
[
  {
    "id": "25c5f9b3-04b6-4b10-be41-6d47a2c79f96",
    "estado": "terminada",
    "huella": "7b88bea8fcb6e15b0dc9714e258549fc8ff623fb13d10d91c72f63b04deb0054",
    "repite_a": null
  },
  {
    "id": "357fa160-4fff-4b90-8c4e-28c9cf1b62e1",
    "estado": "terminada",
    "huella": "7b88bea8fcb6e15b0dc9714e258549fc8ff623fb13d10d91c72f63b04deb0054",
    "repite_a": "25c5f9b3-04b6-4b10-be41-6d47a2c79f96"
  }
]
```

### SIM-05 · Otra semilla, otro resultado · PASA

**Objetivo.** Misma entrada con semilla 12: la huella cambia.

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones/a15b01d8-c9d3-4cb1-84e8-aa39e1553e66`

```http
Accept: application/json
X-Traza-Id: bbb81faa-9d77-4637-a3d5-b978f59354df
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 24 ms · traza `bbb81faa-9d77-4637-a3d5-b978f59354df`

```json
{
  "id": "a15b01d8-c9d3-4cb1-84e8-aa39e1553e66",
  "nombre": "Simulación de Microhub San Bernabé Centro 2026-11-26",
  "estado": "terminada",
  "objeto": {
    "tipo": "microhub",
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "semilla": 12,
  "version_modelo": "1.0",
  "dias": 14,
  "replicas": 100,
  "entrada": {
    "pedidos_dia": 23.6,
    "ticket": 134.83,
    "margen_bruto": 0.28,
    "costos_fijos_mes": 69500.0,
    "costo_variable_pedido": 32.61,
    "dias_mes": 30.0,
    "operadores": 3,
    "repartidores": 3,
    "capacidad_fisica": 150,
    "horas": 10.0,
    "distancia_km": 2.4,
    "ausentismo": 0.05,
    "variacion_demanda": 0.1,
    "indice_semanal": [
      0.893,
      0.844,
      0.884,
      0.937,
      1.154,
      1.303,
      1.028
    ],
    "dia_inicio": 4,
    "origen_de_datos": [
      {
        "dato": "costos_fijos",
        "fuente": "costos"
      },
      {
        "dato": "costo_variable_pedido",
        "fuente": "costos"
      },
      {
        "dato": "ticket",
        "fuente": "demanda"
      },
      {
        "dato": "margen_bruto",
        "fuente": "configuracion"
      },
      {
        "dato": "pedidos_dia",
        "fuente": "demanda_repartida"
      },
      {
        "dato": "operadores",
        "fuente": "capacidad"
      },
      {
        "dato": "repartidores",
        "fuente": "capacidad"
      },
      {
        "dato": "capacidad_fisica",
        "fuente": "capacidad"
      },
      {
        "dato": "horas",
        "fuente": "configuracion"
      },
      {
        "dato": "distancia_km",
        "fuente": "configuracion"
      },
      {
        "dato": "ausentismo",
        "fuente": "configuracion"
      },
      {
        "dato": "variacion_demanda",
        "fuente": "configuracion"
      },
      {
        "dato": "indice_semanal",
        "fuente": "demanda"
      }
    ]
  },
  "resultados": {
    "dias": 14,
    "replicas": 100,
    "metricas": [
      {
        "clave": "********",
        "etiqueta": "Utilidad del periodo",
        "unidad": "MXN",
        "media": -30727.8049,
        "p10": -30860.7874,
        "p50": -30738.9125,
        "p90": -30582.0693,
        "minimo": -31024.3157,
        "maximo": -30474.0789
      },
      {
        "clave": "********",
        "etiqueta": "Ingreso del periodo",
        "unidad": "MXN",
        "media": 44717.7178,
        "p10": 41231.014,
        "p50": 44426.485,
        "p90": 48538.8,
        "minimo": 36943.42,
        "maximo": 51370.23
      },
      {
        "clave": "********",
        "etiqueta": "Pedidos atendidos",
        "unidad": "pedidos",
        "media": 331.66,
        "p10": 305.8,
        "p50": 329.5,
        "p90": 360.0,
        "minimo": 274.0,
        "maximo": 381.0
      },
      {
        "clave": "********",
        "etiqueta": "Pedidos rechazados por falta de capacidad",
        "unidad": "pedidos",
        "media": 0.29,
        "p10": 0.0,
        "p50": 0.0,
        "p90": 0.0,
        "minimo": 0.0,
        "maximo": 29.0
      },
      {
        "clave": "********",
        "etiqueta": "Utilización de la capacidad",
        "unidad": "%",
        "media": 16.6912,
        "p10": 15.2623,
        "p50": 16.5442,
        "p90": 18.3873,
        "minimo": 14.0872,
        "maximo": 19.309
      },
      {
        "clave": "********",
        "etiqueta": "Días saturados",
        "unidad": "días",
        "media": 0.01,
        "p10": 0.0,
        "p50": 0.0,
        "p90": 0.0,
        "minimo": 0.0,
        "maximo": 1.0
      }
    ],
    "prob_perdida_pct": 100.0,
    "dias_saturados_pct": 0.0714,
    "contraste": {
      "utilidad_sin_variacion": -30734.2844,
      "utilidad_media": -30727.8049,
      "diferencia": 6.4795,
      "capacidad_dia_con_todo_el_personal": 150.0
    },
    "lectura": [
      "En 100 réplicas de 14 días, la utilidad media fue de -30,728 MXN (P10 -30,861, P90 -30,582).",
      "Hubo pérdida en 100.0 % de las réplicas y 0.1 % de los días estuvieron saturados.",
      "La capacidad alcanzó para casi toda la demanda.",
      "Con estos supuestos, lo más probable es perder dinero."
    ],
    "serie": [
      {
        "dia": 1,
        "demanda_media": 22.09,
        "atendidos_media": 22.09,
        "utilidad_acumulada_media": -2203.0711
      },
      {
        "dia": 2,
        "demanda_media": 27.73,
        "atendidos_media": 27.73,
        "utilidad_acumulada_media": -4377.139
      },
      {
        "dia": 3,
        "demanda_media": 30.45,
        "atendidos_media": 30.45,
        "utilidad_acumulada_media": -6537.2196
      },
      {
        "dia": 4,
        "demanda_media": 24.87,
        "atendidos_media": 24.87,
        "utilidad_acumulada_media": -8725.9947
      },
      {
        "dia": 5,
        "demanda_media": 21.46,
        "atendidos_media": 21.46,
        "utilidad_acumulada_media": -10932.3055
      },
      {
        "dia": 6,
        "demanda_media": 19.74,
        "atendidos_media": 19.74,
        "utilidad_acumulada_media": -13147.4612
      },
      {
        "dia": 7,
        "demanda_media": 20.07,
        "atendidos_media": 20.07,
        "utilidad_acumulada_media": -15360.9199
      },
      {
        "dia": 8,
        "demanda_media": 22.54,
        "atendidos_media": 22.54,
        "utilidad_acumulada_media": -17561.6769
      },
      {
        "dia": 9,
        "demanda_media": 27.87,
        "atendidos_media": 27.87,
        "utilidad_acumulada_media": -19735.0248
      },
      {
        "dia": 10,
        "demanda_media": 30.12,
        "atendidos_media": 29.83,
        "utilidad_acumulada_media": -21898.2937
      },
      {
        "dia": 11,
        "demanda_media": 23.62,
        "atendidos_media": 23.62,
        "utilidad_acumulada_media": -24093.4969
      },
      {
        "dia": 12,
        "demanda_media": 21.93,
        "atendidos_media": 21.93,
        "utilidad_acumulada_media": -26297.3907
      },
      {
        "dia": 13,
        "demanda_media": 19.68,
        "atendidos_media": 19.68,
        "utilidad_acumulada_media": -28512.855
      },
      {
        "dia": 14,
        "demanda_media": 19.78,
        "atendidos_media": 19.78,
        "utilidad_acumulada_media": -30727.8049
      }
    ]
  },
  "huella": "027f7eb1f5278c5f1e9d9e90d547b7d63c22ed64ebc0e15a69e1b5303c65aeba",
  "repeticion_de": null,
  "reproducible": null,
  "error": null,
  "creado_por": 5,
  "creado_en": "2026-11-26T14:20:07-06:00",
  "inicio_en": "2026-11-26T14:20:08-06:00",
  "fin_en": "2026-11-26T14:20:08-06:00",
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 10.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 20.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 10.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 85.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.05,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.1,
      "modificado": false
    }
  ]
}
```

### SIM-06 · Comparar ejecuciones · PASA

**Objetivo.** Utilidad media, P10, P90, probabilidad de pérdida y días saturados lado a lado.

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/comparacion?ids=25c5f9b3-04b6-4b10-be41-6d47a2c79f96,a15b01d8-c9d3-4cb1-84e8-aa39e1553e66`

```http
Accept: application/json
X-Traza-Id: ee5621e0-0c7c-4d59-91eb-d35453a4a52f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 41 ms · traza `ee5621e0-0c7c-4d59-91eb-d35453a4a52f`

```json
{
  "ejecuciones": [
    {
      "id": "25c5f9b3-04b6-4b10-be41-6d47a2c79f96",
      "nombre": "Simulación de Microhub San Bernabé Centro 2026-11-26",
      "objeto": {
        "tipo": "microhub",
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "dias": 14,
      "replicas": 100,
      "utilidad_media": -30726.0565,
      "utilidad_p10": -30849.9884,
      "utilidad_p90": -30592.3541,
      "prob_perdida_pct": 100.0,
      "atendidos_media": 332.0,
      "rechazados_media": 0.0,
      "dias_saturados_pct": 0.0,
      "huella": "7b88bea8fcb6e15b0dc9714e258549fc8ff623fb13d10d91c72f63b04deb0054"
    },
    {
      "id": "a15b01d8-c9d3-4cb1-84e8-aa39e1553e66",
      "nombre": "Simulación de Microhub San Bernabé Centro 2026-11-26",
      "objeto": {
        "tipo": "microhub",
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "dias": 14,
      "replicas": 100,
      "utilidad_media": -30727.8049,
      "utilidad_p10": -30860.7874,
      "utilidad_p90": -30582.0693,
      "prob_perdida_pct": 100.0,
      "atendidos_media": 331.66,
      "rechazados_media": 0.29,
      "dias_saturados_pct": 0.0714,
      "huella": "027f7eb1f5278c5f1e9d9e90d547b7d63c22ed64ebc0e15a69e1b5303c65aeba"
    }
  ],
  "mejor_id": "25c5f9b3-04b6-4b10-be41-6d47a2c79f96",
  "criterio": "Mayor utilidad media entre las que pierden dinero en menos de la mitad de las réplicas."
}
```

### SIM-07 · Escenario manual · PASA

**Objetivo.** Sin microhub ni candidato, con todos los datos escritos (el escenario A).

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones`

```http
Accept: application/json
X-Traza-Id: 98437266-0dbd-4af5-9ba2-a4d4e5e5d2eb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "pedidos_dia": 45,
  "ticket": 135,
  "costos_fijos": 60000,
  "costo_variable_pedido": 32.6,
  "operadores": 3,
  "repartidores": 2,
  "dias": 14,
  "replicas": 100,
  "semilla": 12
}
```

**Respuesta.** HTTP 202 (esperado 202) · 229 ms · traza `98437266-0dbd-4af5-9ba2-a4d4e5e5d2eb`

```json
{
  "id": "d663c0c3-2ffb-49ff-b440-3eed2ebe44b1",
  "nombre": "Simulación de escenario manual 2026-11-26",
  "estado": "en_cola",
  "objeto": {
    "tipo": "manual",
    "id": null,
    "nombre": null
  },
  "semilla": 12,
  "version_modelo": "1.0",
  "dias": 14,
  "replicas": 100,
  "entrada": {
    "pedidos_dia": 45.0,
    "ticket": 135.0,
    "margen_bruto": 0.28,
    "costos_fijos_mes": 60000.0,
    "costo_variable_pedido": 32.6,
    "dias_mes": 30.0,
    "operadores": 3,
    "repartidores": 2,
    "capacidad_fisica": null,
    "horas": 10.0,
    "distancia_km": 2.4,
    "ausentismo": 0.05,
    "variacion_demanda": 0.1,
    "indice_semanal": [
      0.893,
      0.844,
      0.884,
      0.937,
      1.154,
      1.303,
      1.028
    ],
    "dia_inicio": 4,
    "origen_de_datos": [
      {
        "dato": "pedidos_dia",
        "fuente": "manual"
      },
      {
        "dato": "ticket",
        "fuente": "manual"
      },
      {
        "dato": "margen_bruto",
        "fuente": "manual"
      },
      {
        "dato": "costos_fijos",
        "fuente": "manual"
      },
      {
        "dato": "costo_variable_pedido",
        "fuente": "manual"
      },
      {
        "dato": "operadores",
        "fuente": "manual"
      },
      {
        "dato": "repartidores",
        "fuente": "manual"
      },
      {
        "dato": "capacidad_fisica",
        "fuente": "sin_dato"
      },
      {
        "dato": "horas",
        "fuente": "configuracion"
      },
      {
        "dato": "distancia_km",
        "fuente": "configuracion"
      },
      {
        "dato": "ausentismo",
        "fuente": "configuracion"
      },
      {
        "dato": "variacion_demanda",
        "fuente": "configuracion"
      },
      {
        "dato": "indice_semanal",
        "fuente": "demanda"
      }
    ]
  },
  "resultados": null,
  "huella": null,
  "repeticion_de": null,
  "reproducible": null,
  "error": null,
  "creado_por": 5,
  "creado_en": "2026-11-26T14:20:08-06:00",
  "inicio_en": null,
  "fin_en": null,
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 10.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 20.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 10.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 85.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.05,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.1,
      "modificado": false
    }
  ]
}
```

### SIM-08 · Con el escenario A se pierde dinero · PASA

**Objetivo.** 100 % de las réplicas terminan en pérdida: lo que ya decía el punto de equilibrio.

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones/d663c0c3-2ffb-49ff-b440-3eed2ebe44b1`

```http
Accept: application/json
X-Traza-Id: 60d40d3b-465e-4864-9100-d40b7dbaa44c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 24 ms · traza `60d40d3b-465e-4864-9100-d40b7dbaa44c`

```json
{
  "id": "d663c0c3-2ffb-49ff-b440-3eed2ebe44b1",
  "nombre": "Simulación de escenario manual 2026-11-26",
  "estado": "terminada",
  "objeto": {
    "tipo": "manual",
    "id": null,
    "nombre": null
  },
  "semilla": 12,
  "version_modelo": "1.0",
  "dias": 14,
  "replicas": 100,
  "entrada": {
    "pedidos_dia": 45.0,
    "ticket": 135.0,
    "margen_bruto": 0.28,
    "costos_fijos_mes": 60000.0,
    "costo_variable_pedido": 32.6,
    "dias_mes": 30.0,
    "operadores": 3,
    "repartidores": 2,
    "capacidad_fisica": null,
    "horas": 10.0,
    "distancia_km": 2.4,
    "ausentismo": 0.05,
    "variacion_demanda": 0.1,
    "indice_semanal": [
      0.893,
      0.844,
      0.884,
      0.937,
      1.154,
      1.303,
      1.028
    ],
    "dia_inicio": 4,
    "origen_de_datos": [
      {
        "dato": "pedidos_dia",
        "fuente": "manual"
      },
      {
        "dato": "ticket",
        "fuente": "manual"
      },
      {
        "dato": "margen_bruto",
        "fuente": "manual"
      },
      {
        "dato": "costos_fijos",
        "fuente": "manual"
      },
      {
        "dato": "costo_variable_pedido",
        "fuente": "manual"
      },
      {
        "dato": "operadores",
        "fuente": "manual"
      },
      {
        "dato": "repartidores",
        "fuente": "manual"
      },
      {
        "dato": "capacidad_fisica",
        "fuente": "sin_dato"
      },
      {
        "dato": "horas",
        "fuente": "configuracion"
      },
      {
        "dato": "distancia_km",
        "fuente": "configuracion"
      },
      {
        "dato": "ausentismo",
        "fuente": "configuracion"
      },
      {
        "dato": "variacion_demanda",
        "fuente": "configuracion"
      },
      {
        "dato": "indice_semanal",
        "fuente": "demanda"
      }
    ]
  },
  "resultados": {
    "dias": 14,
    "replicas": 100,
    "metricas": [
      {
        "clave": "********",
        "etiqueta": "Utilidad del periodo",
        "unidad": "MXN",
        "media": -24688.744,
        "p10": -24896.64,
        "p50": -24672.0,
        "p90": -24478.04,
        "minimo": -25114.0,
        "maximo": -24339.2
      },
      {
        "clave": "********",
        "etiqueta": "Ingreso del periodo",
        "unidad": "MXN",
        "media": 85965.3,
        "p10": 80568.0,
        "p50": 86400.0,
        "p90": 91435.5,
        "minimo": 74925.0,
        "maximo": 95040.0
      },
      {
        "clave": "********",
        "etiqueta": "Pedidos atendidos",
        "unidad": "pedidos",
        "media": 636.78,
        "p10": 596.8,
        "p50": 640.0,
        "p90": 677.3,
        "minimo": 555.0,
        "maximo": 704.0
      },
      {
        "clave": "********",
        "etiqueta": "Pedidos rechazados por falta de capacidad",
        "unidad": "pedidos",
        "media": 1.94,
        "p10": 0.0,
        "p50": 0.0,
        "p90": 0.0,
        "minimo": 0.0,
        "maximo": 62.0
      },
      {
        "clave": "********",
        "etiqueta": "Utilización de la capacidad",
        "unidad": "%",
        "media": 34.6534,
        "p10": 31.9498,
        "p50": 34.7636,
        "p90": 37.2065,
        "minimo": 30.234,
        "maximo": 39.7653
      },
      {
        "clave": "********",
        "etiqueta": "Días saturados",
        "unidad": "días",
        "media": 0.18,
        "p10": 0.0,
        "p50": 0.0,
        "p90": 1.0,
        "minimo": 0.0,
        "maximo": 2.0
      }
    ],
    "prob_perdida_pct": 100.0,
    "dias_saturados_pct": 1.2857,
    "contraste": {
      "utilidad_sin_variacion": -24724.0,
      "utilidad_media": -24688.744,
      "diferencia": 35.256,
      "capacidad_dia_con_todo_el_personal": 143.5
    },
    "lectura": [
      "En 100 réplicas de 14 días, la utilidad media fue de -24,689 MXN (P10 -24,897, P90 -24,478).",
      "Hubo pérdida en 100.0 % de las réplicas y 1.3 % de los días estuvieron saturados.",
      "Faltó capacidad: se rechazaron en promedio 2 pedidos en el periodo.",
      "Con estos supuestos, lo más probable es perder dinero."
    ],
    "serie": [
      {
        "dia": 1,
        "demanda_media": 42.61,
        "atendidos_media": 42.61,
        "utilidad_acumulada_media": -1778.428
      },
      {
        "dia": 2,
        "demanda_media": 51.04,
        "atendidos_media": 51.04,
        "utilidad_acumulada_media": -3513.02
      },
      {
        "dia": 3,
        "demanda_media": 58.23,
        "atendidos_media": 57.56,
        "utilidad_acumulada_media": -5213.708
      },
      {
        "dia": 4,
        "demanda_media": 48.09,
        "atendidos_media": 48.09,
        "utilidad_acumulada_media": -6963.64
      },
      {
        "dia": 5,
        "demanda_media": 41.15,
        "atendidos_media": 41.15,
        "utilidad_acumulada_media": -8749.66
      },
      {
        "dia": 6,
        "demanda_media": 38.06,
        "atendidos_media": 38.06,
        "utilidad_acumulada_media": -10551.748
      },
      {
        "dia": 7,
        "demanda_media": 40.06,
        "atendidos_media": 40.06,
        "utilidad_acumulada_media": -12343.436
      },
      {
        "dia": 8,
        "demanda_media": 42.88,
        "atendidos_media": 42.47,
        "utilidad_acumulada_media": -14122.592
      },
      {
        "dia": 9,
        "demanda_media": 52.1,
        "atendidos_media": 52.1,
        "utilidad_acumulada_media": -15851.672
      },
      {
        "dia": 10,
        "demanda_media": 58.42,
        "atendidos_media": 58.42,
        "utilidad_acumulada_media": -17547.888
      },
      {
        "dia": 11,
        "demanda_media": 47.22,
        "atendidos_media": 47.22,
        "utilidad_acumulada_media": -19302.344
      },
      {
        "dia": 12,
        "demanda_media": 39.74,
        "atendidos_media": 39.74,
        "utilidad_acumulada_media": -21095.696
      },
      {
        "dia": 13,
        "demanda_media": 38.61,
        "atendidos_media": 38.15,
        "utilidad_acumulada_media": -22897.316
      },
      {
        "dia": 14,
        "demanda_media": 40.51,
        "atendidos_media": 40.11,
        "utilidad_acumulada_media": -24688.744
      }
    ]
  },
  "huella": "38204b4324381f9b56ea08ebc42468713df697fbc39c99eac8fa6332f5d6a743",
  "repeticion_de": null,
  "reproducible": null,
  "error": null,
  "creado_por": 5,
  "creado_en": "2026-11-26T14:20:08-06:00",
  "inicio_en": "2026-11-26T14:20:08-06:00",
  "fin_en": "2026-11-26T14:20:08-06:00",
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 10.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 20.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 10.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 85.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.05,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.1,
      "modificado": false
    }
  ]
}
```

### SIM-09 · Entrada incompleta · PASA

**Objetivo.** Sin microhub hay que dar todos los datos.

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones`

```http
Accept: application/json
X-Traza-Id: 6fc17ebf-ed9d-4def-aec1-654682993066
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "pedidos_dia": 45
}
```

**Respuesta.** HTTP 422 (esperado 422) · 34 ms · traza `6fc17ebf-ed9d-4def-aec1-654682993066`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Sin microhub ni candidato hay que indicar todos los datos del escenario.",
    "detalles": [
      {
        "campo": "ticket",
        "mensaje": "Es obligatorio sin microhub ni candidato."
      },
      {
        "campo": "costos_fijos",
        "mensaje": "Es obligatorio sin microhub ni candidato."
      },
      {
        "campo": "costo_variable_pedido",
        "mensaje": "Es obligatorio sin microhub ni candidato."
      },
      {
        "campo": "operadores",
        "mensaje": "Es obligatorio sin microhub ni candidato."
      },
      {
        "campo": "repartidores",
        "mensaje": "Es obligatorio sin microhub ni candidato."
      }
    ],
    "traza_id": "6fc17ebf-ed9d-4def-aec1-654682993066"
  }
}
```

### SIM-10 · Demasiado trabajo · PASA

**Objetivo.** Días × réplicas no puede pasar de 200,000.

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones`

```http
Accept: application/json
X-Traza-Id: 7af44afd-9d07-4791-9721-2c6131f0605b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "dias": 365,
  "replicas": 2000
}
```

**Respuesta.** HTTP 422 (esperado 422) · 492 ms · traza `7af44afd-9d07-4791-9721-2c6131f0605b`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Días × réplicas no puede pasar de 200,000; pediste 730,000.",
    "detalles": [
      {
        "campo": "replicas",
        "mensaje": "Reduce los días o las réplicas (máximo 200,000 entre las dos)."
      }
    ],
    "traza_id": "7af44afd-9d07-4791-9721-2c6131f0605b"
  }
}
```

### SIM-11 · Cancelar una ejecución · PASA

**Objetivo.** Una ejecución en cola o en curso se puede cancelar.

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones/602f3dd1-335b-4487-a893-e6820eac4d90/cancelar`

```http
Accept: application/json
X-Traza-Id: d39d1237-6b8c-4332-b09b-3990278bc40d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 89 ms · traza `d39d1237-6b8c-4332-b09b-3990278bc40d`

```json
{
  "id": "602f3dd1-335b-4487-a893-e6820eac4d90",
  "nombre": "Simulación de Microhub San Bernabé Centro 2026-11-26",
  "estado": "cancelada",
  "objeto": {
    "tipo": "microhub",
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "semilla": 2026,
  "version_modelo": "1.0",
  "dias": 300,
  "replicas": 600,
  "entrada": {
    "pedidos_dia": 23.6,
    "ticket": 134.83,
    "margen_bruto": 0.28,
    "costos_fijos_mes": 69500.0,
    "costo_variable_pedido": 32.61,
    "dias_mes": 30.0,
    "operadores": 3,
    "repartidores": 3,
    "capacidad_fisica": 150,
    "horas": 10.0,
    "distancia_km": 2.4,
    "ausentismo": 0.05,
    "variacion_demanda": 0.1,
    "indice_semanal": [
      0.893,
      0.844,
      0.884,
      0.937,
      1.154,
      1.303,
      1.028
    ],
    "dia_inicio": 4,
    "origen_de_datos": [
      {
        "dato": "costos_fijos",
        "fuente": "costos"
      },
      {
        "dato": "costo_variable_pedido",
        "fuente": "costos"
      },
      {
        "dato": "ticket",
        "fuente": "demanda"
      },
      {
        "dato": "margen_bruto",
        "fuente": "configuracion"
      },
      {
        "dato": "pedidos_dia",
        "fuente": "demanda_repartida"
      },
      {
        "dato": "operadores",
        "fuente": "capacidad"
      },
      {
        "dato": "repartidores",
        "fuente": "capacidad"
      },
      {
        "dato": "capacidad_fisica",
        "fuente": "capacidad"
      },
      {
        "dato": "horas",
        "fuente": "configuracion"
      },
      {
        "dato": "distancia_km",
        "fuente": "configuracion"
      },
      {
        "dato": "ausentismo",
        "fuente": "configuracion"
      },
      {
        "dato": "variacion_demanda",
        "fuente": "configuracion"
      },
      {
        "dato": "indice_semanal",
        "fuente": "demanda"
      }
    ]
  },
  "resultados": null,
  "huella": null,
  "repeticion_de": null,
  "reproducible": null,
  "error": null,
  "creado_por": 5,
  "creado_en": "2026-11-26T14:20:10-06:00",
  "inicio_en": null,
  "fin_en": "2026-11-26T14:20:10-06:00",
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 10.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 20.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 3.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 10.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 85.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.05,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.1,
      "modificado": false
    }
  ]
}
```

**Evidencia en PostgreSQL.** `SELECT id, estado, fin_en IS NOT NULL AS fin, resultados IS NULL AS sin_resultados FROM simulacion_ejecucion WHERE id = %s`

```json
[
  {
    "id": "602f3dd1-335b-4487-a893-e6820eac4d90",
    "estado": "cancelada",
    "fin": true,
    "sin_resultados": true
  }
]
```

### SIM-12 · Cancelar una cancelada · PASA

**Objetivo.** Solo se cancela lo que está en cola o en curso.

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones/602f3dd1-335b-4487-a893-e6820eac4d90/cancelar`

```http
Accept: application/json
X-Traza-Id: 397fc486-77ce-42f8-94c9-7c1694b8d95e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 409 (esperado 409) · 44 ms · traza `397fc486-77ce-42f8-94c9-7c1694b8d95e`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Solo se cancela una ejecución en cola o en curso; esta está cancelada.",
    "traza_id": "397fc486-77ce-42f8-94c9-7c1694b8d95e"
  }
}
```

### SIM-13 · Ejecuciones · PASA

**Objetivo.** Lista paginada, la más reciente primero.

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones?por_pagina=5`

```http
Accept: application/json
X-Traza-Id: c88075b2-8143-4f5d-88e0-b852ae0220dc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 46 ms · traza `c88075b2-8143-4f5d-88e0-b852ae0220dc`

```json
{
  "datos": [
    {
      "id": "602f3dd1-335b-4487-a893-e6820eac4d90",
      "nombre": "Simulación de Microhub San Bernabé Centro 2026-11-26",
      "estado": "cancelada",
      "objeto": {
        "tipo": "microhub",
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "semilla": 2026,
      "dias": 300,
      "replicas": 600,
      "utilidad_media": null,
      "prob_perdida_pct": null,
      "huella": null,
      "creado_en": "2026-11-26T14:20:10-06:00",
      "fin_en": "2026-11-26T14:20:10-06:00"
    },
    {
      "id": "d663c0c3-2ffb-49ff-b440-3eed2ebe44b1",
      "nombre": "Simulación de escenario manual 2026-11-26",
      "estado": "terminada",
      "objeto": {
        "tipo": "manual",
        "id": null,
        "nombre": null
      },
      "semilla": 12,
      "dias": 14,
      "replicas": 100,
      "utilidad_media": -24688.744,
      "prob_perdida_pct": 100.0,
      "huella": "38204b4324381f9b56ea08ebc42468713df697fbc39c99eac8fa6332f5d6a743",
      "creado_en": "2026-11-26T14:20:08-06:00",
      "fin_en": "2026-11-26T14:20:08-06:00"
    },
    {
      "id": "a15b01d8-c9d3-4cb1-84e8-aa39e1553e66",
      "nombre": "Simulación de Microhub San Bernabé Centro 2026-11-26",
      "estado": "terminada",
      "objeto": {
        "tipo": "microhub",
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "semilla": 12,
      "dias": 14,
      "replicas": 100,
      "utilidad_media": -30727.8049,
      "prob_perdida_pct": 100.0,
      "huella": "027f7eb1f5278c5f1e9d9e90d547b7d63c22ed64ebc0e15a69e1b5303c65aeba",
      "creado_en": "2026-11-26T14:20:07-06:00",
      "fin_en": "2026-11-26T14:20:08-06:00"
    },
    {
      "id": "357fa160-4fff-4b90-8c4e-28c9cf1b62e1",
      "nombre": "Repetición de Simulación de Microhub San Bernabé Centro 2026-11-26",
      "estado": "terminada",
      "objeto": {
        "tipo": "microhub",
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "semilla": 11,
      "dias": 14,
      "replicas": 100,
      "utilidad_media": -30726.0565,
      "prob_perdida_pct": 100.0,
      "huella": "7b88bea8fcb6e15b0dc9714e258549fc8ff623fb13d10d91c72f63b04deb0054",
      "creado_en": "2026-11-26T14:20:06-06:00",
      "fin_en": "2026-11-26T14:20:06-06:00"
    },
    {
      "id": "25c5f9b3-04b6-4b10-be41-6d47a2c79f96",
      "nombre": "Simulación de Microhub San Bernabé Centro 2026-11-26",
      "estado": "terminada",
      "objeto": {
        "tipo": "microhub",
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "semilla": 11,
      "dias": 14,
      "replicas": 100,
      "utilidad_media": -30726.0565,
      "prob_perdida_pct": 100.0,
      "huella": "7b88bea8fcb6e15b0dc9714e258549fc8ff623fb13d10d91c72f63b04deb0054",
      "creado_en": "2026-11-26T14:20:04-06:00",
      "fin_en": "2026-11-26T14:20:05-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 5,
    "paginas": 1
  }
}
```

### SIM-14 · El auditor consulta simulaciones · PASA

**Objetivo.** Sin simulacion.ver.

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones`

```http
Accept: application/json
X-Traza-Id: 0ffbf455-f231-4052-ab12-9f48c3fbd7b0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 28 ms · traza `0ffbf455-f231-4052-ab12-9f48c3fbd7b0`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "0ffbf455-f231-4052-ab12-9f48c3fbd7b0"
  }
}
```

### SIM-15 · El operador simula · PASA

**Objetivo.** Sin simulacion.ejecutar.

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones`

```http
Accept: application/json
X-Traza-Id: e52870fe-e83f-45db-9e65-a41d4a5bfea0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1
}
```

**Respuesta.** HTTP 403 (esperado 403) · 25 ms · traza `e52870fe-e83f-45db-9e65-a41d4a5bfea0`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "e52870fe-e83f-45db-9e65-a41d4a5bfea0"
  }
}
```

### SIM-16 · Poner en cola (XML) · PASA

**Objetivo.** Entrada y salida en XML, validadas contra simulacion.xsd.

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones`

```http
Accept: application/xml
X-Traza-Id: 513600d3-55fc-4c2e-a320-462a6621ed06
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><simulacion_nueva xmlns="urn:microhubs:v1"><microhub_id>1</microhub_id><dias>5</dias><replicas>20</replicas><semilla>3</semilla></simulacion_nueva>
```

**Respuesta.** HTTP 202 (esperado 202) · 535 ms · traza `513600d3-55fc-4c2e-a320-462a6621ed06`

```xml
<?xml version='1.0' encoding='utf-8'?>
<simulacion_ejecucion xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>890d2a67-8e47-4078-94fc-88b7a1c880f6</id><nombre>Simulación de Microhub San Bernabé Centro 2026-11-26</nombre><estado>en_cola</estado><objeto><tipo>microhub</tipo><id>1</id><nombre>Microhub San Bernabé Centro</nombre></objeto><semilla>3</semilla><version_modelo>1.0</version_modelo><dias>5</dias><replicas>20</replicas><entrada><pedidos_dia>23.6</pedidos_dia><ticket>134.83</ticket><margen_bruto>0.28</margen_bruto><costos_fijos_mes>69500</costos_fijos_mes><costo_variable_pedido>32.61</costo_variable_pedido><dias_mes>30</dias_mes><operadores>3</operadores><repartidores>3</repartidores><capacidad_fisica>150</capacidad_fisica><horas>10</horas><distancia_km>2.4</distancia_km><ausentismo>0.05</ausentismo><variacion_demanda>0.1</variacion_demanda><indice_semanal><indice>0.893</indice><indice>0.844</indice><indice>0.884</indice><indice>0.937</indice><indice>1.154</indice><indice>1.303</indice><indice>1.028</indice></indice_semanal><dia_inicio>4</dia_inicio><origen_de_datos><dato><dato>costos_fijos</dato><fuente>costos</fuente></dato><dato><dato>costo_variable_pedido</dato><fuente>costos</fuente></dato><dato><dato>ticket</dato><fuente>demanda</fuente></dato><dato><dato>margen_bruto</dato><fuente>configuracion</fuente></dato><dato><dato>pedidos_dia</dato><fuente>demanda_repartida</fuente></dato><dato><dato>operadores</dato><fuente>capacidad</fuente></dato><dato><dato>repartidores</dato><fuente>capacidad</fuente></dato><dato><dato>capacidad_fisica</dato><fuente>capacidad</fuente></dato><dato><dato>horas</dato><fuente>configuracion</fuente></dato><dato><dato>distancia_km</dato><fuente>configuracion</fuente></dato><dato><dato>ausentismo</dato><fuente>configuracion</fuente></dato><dato><dato>variacion_demanda</dato><fuente>configuracion</fuente></dato><dato><dato>indice_semanal</dato><fuente>demanda</fuente></dato></origen_de_datos></entrada><resultados xsi:nil="true" /><huella xsi:nil="true" /><repeticion_de xsi:nil="true" /><reproducible xsi:nil="true" /><error xsi:nil="true" /><creado_por>5</creado_por><creado_en>2026-11-26T14:20:11-06:00</creado_en><inicio_en xsi:nil="true" /><fin_en xsi:nil="true" /><supuestos_usados><supuesto><clave>picking_pedidos_hora</clave><valor>10</valor><modificado>false</modificado></supuesto><supuesto><clave>packing_pedidos_hora</clave><valor>20</valor><modificado>false</modificado></supuesto><supuesto><clave>despacho_pedidos_hora</clave><valor>30</valor><modificado>false</modificado></supuesto><supuesto><clave>velocidad_reparto_kmh</clave><valor>22</valor><modificado>false</modificado></supuesto><supuesto><clave>tiempo_servicio_min</clave><valor>4</valor><modificado>false</modificado></supuesto><supuesto><clave>paradas_por_viaje</clave><valor>3</valor><modificado>false</modificado></supuesto><supuesto><clave>horas_turno</clave><valor>10</valor><modificado>false</modificado></supuesto><supuesto><clave>umbral_utilizacion_riesgo</clave><valor>85</valor><modificado>false</modificado></supuesto><supuesto><clave>sim_ausentismo</clave><valor>0.05</valor><modificado>false</modificado></supuesto><supuesto><clave>sim_variacion_demanda</clave><valor>0.1</valor><modificado>false</modificado></supuesto></supuestos_usados></simulacion_ejecucion>
```

### SIM-17 · Una ejecución inexistente · PASA

**Objetivo.** Un identificador que no existe.

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones/054be617-6510-4792-aae6-ba1181c4657d`

```http
Accept: application/json
X-Traza-Id: dd5ffd00-d944-42a9-8cf4-6db9e67e8434
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 24 ms · traza `dd5ffd00-d944-42a9-8cf4-6db9e67e8434`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe esa ejecución.",
    "traza_id": "dd5ffd00-d944-42a9-8cf4-6db9e67e8434"
  }
}
```

### SIM-18 · Supuestos de la simulación · PASA

**Objetivo.** Réplicas, ausentismo, variación de la demanda y semilla.

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/supuestos`

```http
Accept: application/json
X-Traza-Id: 85981486-73cf-4a63-8b0e-29299a594230
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 30 ms · traza `85981486-73cf-4a63-8b0e-29299a594230`

```json
{
  "datos": [
    {
      "clave": "********",
      "valor": "2.4",
      "unidad": "km",
      "origen": "supuesto",
      "justificacion": "Distancia típica de entrega desde el microhub, ida solamente; es el valor del Escenario A de la retroalimentación.",
      "como_calibrar": "Distancia promedio entre el microhub y los domicilios de las entregas cerradas."
    },
    {
      "clave": "********",
      "valor": "30",
      "unidad": "pedidos/h",
      "origen": "supuesto",
      "justificacion": "Un operador despacha unos 30 pedidos por hora (2 minutos: verificar y entregar al repartidor).",
      "como_calibrar": "Tiempo entre listo_en y la salida del repartidor."
    },
    {
      "clave": "********",
      "valor": "30",
      "unidad": "días",
      "origen": "normativo",
      "justificacion": "El microhub opera todos los días del mes.",
      "como_calibrar": "Cambiar si se decide cerrar un día a la semana."
    },
    {
      "clave": "********",
      "valor": "10",
      "unidad": "horas",
      "origen": "supuesto",
      "justificacion": "El microhub abre 12 horas (8 a 20 h); se toman 10 de trabajo efectivo descontando comida y cierre.",
      "como_calibrar": "Horas realmente trabajadas según la asistencia del personal."
    },
    {
      "clave": "********",
      "valor": "20",
      "unidad": "pedidos/h",
      "origen": "supuesto",
      "justificacion": "Un operador empaca unos 20 pedidos por hora (3 minutos por pedido).",
      "como_calibrar": "Cronometrar una muestra de pedidos en el área de empaque."
    },
    {
      "clave": "********",
      "valor": "3",
      "unidad": "paradas",
      "origen": "supuesto",
      "justificacion": "Paradas promedio de una salida cuando los pedidos se agrupan por zona. Reparte el costo del regreso al microhub entre ellas.",
      "como_calibrar": "Promedio de la columna paradas de plan_ruta."
    },
    {
      "clave": "********",
      "valor": "10",
      "unidad": "pedidos/h",
      "origen": "supuesto",
      "justificacion": "Un operador junta unos 10 pedidos por hora (6 minutos por pedido de cinco líneas aproximadamente).",
      "como_calibrar": "Tiempo entre asignado y en_preparacion en historial_estatus, o cronometrar una muestra de pedidos."
    },
    {
      "clave": "********",
      "valor": "0.05",
      "unidad": "fracción",
      "origen": "supuesto",
      "justificacion": "Cada operador o repartidor falta un día con probabilidad 5 %. No hay registros de asistencia todavía.",
      "como_calibrar": "Faltas reales entre días laborables, cuando exista el registro de asistencia."
    },
    {
      "clave": "********",
      "valor": "30",
      "unidad": "días",
      "origen": "supuesto",
      "justificacion": "Un mes de operación: el mismo plazo en que se miden los costos fijos y la utilidad.",
      "como_calibrar": "Ninguna; es el horizonte de la simulación, se cambia según la decisión que se quiera apoyar."
    },
    {
      "clave": "********",
      "valor": "200",
      "unidad": "réplicas",
      "origen": "supuesto",
      "justificacion": "Con 200 réplicas el promedio y los percentiles ya no cambian de forma notable entre corridas.",
      "como_calibrar": "Aumentar las réplicas hasta que P10, P50 y P90 se estabilicen."
    },
    {
      "clave": "********",
      "valor": "2026",
      "unidad": "semilla",
      "origen": "normativo",
      "justificacion": "La semilla fija el generador aleatorio: con los mismos parámetros se obtiene exactamente el mismo resultado.",
      "como_calibrar": "Ninguna; cambiarla da otra corrida con la misma distribución, útil para comprobar que el resultado no depende del azar."
    },
    {
      "clave": "********",
      "valor": "0.10",
      "unidad": "fracción",
      "origen": "supuesto",
      "justificacion": "Un día cualquiera puede desviarse alrededor de 10 % de su pr…(142 caracteres)",
      "como_calibrar": "Desviación estándar de pedidos reales dividida entre su promedio, por día de la semana."
    },
    {
      "clave": "********",
      "valor": "4",
      "unidad": "minutos",
      "origen": "supuesto",
      "justificacion": "Minutos que el repartidor pasa en cada parada: estacionar, entregar, cobrar y confirmar con el cliente.",
      "como_calibrar": "Diferencia entre la llegada al domicilio y el cierre de la entrega en el recorrido GPS."
    },
    {
      "clave": "********",
      "valor": "85",
      "unidad": "porcentaje",
      "origen": "supuesto",
      "justificacion": "Por encima de 85 % la espera en una fila crece muy rápido (teoría de colas), así que se considera riesgo de saturación.",
      "como_calibrar": "Medir el tiempo de espera de los pedidos contra la utilización de cada día."
    },
    {
      "clave": "********",
      "valor": "22",
      "unidad": "km/h",
      "origen": "supuesto",
      "justificacion": "Velocidad media de un repartidor en moto o bicicleta dentro …(180 caracteres)",
      "como_calibrar": "Dividir la distancia del recorrido GPS entre su duración en …(147 caracteres)"
    }
  ]
}
```

## Servicio documentos · puerto 5107

### ENL-01 · Pedir un enlace de descarga firmado · PASA

**Objetivo.** URL de un solo método y con caducidad para bajar el archivo del almacén.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b08947e14ec03b218378d3f/enlace`

```http
Accept: application/json
X-Traza-Id: e8d8072d-08e4-473f-834f-a73a2d1fdbb8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 45 ms · traza `e8d8072d-08e4-473f-834f-a73a2d1fdbb8`

```json
{
  "id": "6b08947e14ec03b218378d3f",
  "nombre": "evidencia-enlace.pdf",
  "url_firmada": "http://documentos:5107/api/v1/documentos/descarga?k=document…(207 caracteres)",
  "metodo": "GET",
  "segundos": 300,
  "expira_en": "2026-11-26T14:25:14-06:00"
}
```

**Explicación.** En la nube la URL es una firmada V4 de Cloud Storage; en local apunta al propio servicio. La base de datos no guarda el archivo.

**Evidencia en PostgreSQL.** `SELECT fecha, modulo, accion, detalle FROM auditoria WHERE entidad = 'documento' AND entidad_id = %s ORDER BY id`

```json
[
  {
    "fecha": "2026-11-26 14:20:14.668114-06:00",
    "modulo": "documentos",
    "accion": "alta",
    "detalle": "evidencia-enlace.pdf (42 bytes) a usuario 7."
  },
  {
    "fecha": "2026-11-26 14:20:14.713145-06:00",
    "modulo": "documentos",
    "accion": "descarga",
    "detalle": "Enlace de descarga de evidencia-enlace.pdf (caduca en 300 s)."
  }
]
```

### ENL-02 · Descargar con el enlace firmado · PASA

**Objetivo.** El enlace funciona sin token: la firma es el permiso.

**Petición.** `GET http://documentos:5107/api/v1/documentos/descarga?k=documentos%2F2026%2F11%2F6b08947e14ec03b218378d3f.pdf&e=1795724714&n=evidencia-enlace.pdf&t=application%2Fpdf&s=Zx3fIbbP9gRII5QKr7HKXMGyKahBV_5PPz6hh-2SKjw`

```http
Accept: application/json
X-Traza-Id: e4f609d0-4b47-443b-8ca6-e96bcb049a82
```

**Respuesta.** HTTP 200 (esperado 200) · 8 ms · traza `e4f609d0-4b47-443b-8ca6-e96bcb049a82`

```json
%PDF-1.4 evidencia de enlace firmado %%EOF
```

### ENL-03 · Enlace manipulado · PASA

**Objetivo.** Cambiar un carácter de la firma lo invalida.

**Petición.** `GET http://documentos:5107/api/v1/documentos/descarga?k=documentos%2F2026%2F11%2F6b08947e14ec03b218378d3f.pdf&e=1795724714&n=evidencia-enlace.pdf&t=application%2Fpdf&s=Zx3fIbbP9gRII5QKr7HKXMGyKahBV_5PPz6hh-2SKAA`

```http
Accept: application/json
X-Traza-Id: 3dab19a9-77b1-4057-8636-d39ed8eabcdf
```

**Respuesta.** HTTP 403 (esperado 403) · 5 ms · traza `3dab19a9-77b1-4057-8636-d39ed8eabcdf`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "El enlace de descarga no es válido o ya caducó.",
    "traza_id": "3dab19a9-77b1-4057-8636-d39ed8eabcdf"
  }
}
```

## Servicio auditoria-monitoreo · puerto 5126

### MNT-01 · Forzar una verificación de todos los servicios · PASA

**Objetivo.** Pregunta la salud de cada servicio y guarda el resultado.

**Petición.** `POST http://auditoria-monitoreo:5126/api/v1/monitoreo/verificaciones`

```http
Accept: application/json
X-Traza-Id: dad1ea8e-b040-492b-9149-b2d2b9b24fe8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 201 (esperado 201) · 230 ms · traza `dad1ea8e-b040-492b-9149-b2d2b9b24fe8`

```json
{
  "verificados": 26,
  "ok": 26,
  "degradados": 0,
  "caidos": 0,
  "servicios": [
    {
      "servicio": "auth",
      "estado": "ok",
      "tiempo_ms": 28.1,
      "error": null
    },
    {
      "servicio": "usuarios",
      "estado": "ok",
      "tiempo_ms": 26.5,
      "error": null
    },
    {
      "servicio": "productos",
      "estado": "ok",
      "tiempo_ms": 33.5,
      "error": null
    },
    {
      "servicio": "pedidos",
      "estado": "ok",
      "tiempo_ms": 37.1,
      "error": null
    },
    {
      "servicio": "entregas",
      "estado": "ok",
      "tiempo_ms": 38.5,
      "error": null
    },
    {
      "servicio": "planeacion",
      "estado": "ok",
      "tiempo_ms": 34.5,
      "error": null
    },
    {
      "servicio": "documentos",
      "estado": "ok",
      "tiempo_ms": 34.0,
      "error": null
    },
    {
      "servicio": "zonas",
      "estado": "ok",
      "tiempo_ms": 36.8,
      "error": null
    },
    {
      "servicio": "microhubs",
      "estado": "ok",
      "tiempo_ms": 45.0,
      "error": null
    },
    {
      "servicio": "seguimiento",
      "estado": "ok",
      "tiempo_ms": 36.8,
      "error": null
    },
    {
      "servicio": "inventario",
      "estado": "ok",
      "tiempo_ms": 26.9,
      "error": null
    },
    {
      "servicio": "precios",
      "estado": "ok",
      "tiempo_ms": 35.7,
      "error": null
    },
    {
      "servicio": "proveedores",
      "estado": "ok",
      "tiempo_ms": 25.8,
      "error": null
    },
    {
      "servicio": "abastecimiento",
      "estado": "ok",
      "tiempo_ms": 23.2,
      "error": null
    },
    {
      "servicio": "demanda",
      "estado": "ok",
      "tiempo_ms": 25.2,
      "error": null
    },
    {
      "servicio": "cobertura",
      "estado": "ok",
      "tiempo_ms": 25.5,
      "error": null
    },
    {
      "servicio": "capacidad",
      "estado": "ok",
      "tiempo_ms": 41.0,
      "error": null
    },
    {
      "servicio": "rutas",
      "estado": "ok",
      "tiempo_ms": 47.0,
      "error": null
    },
    {
      "servicio": "costos",
      "estado": "ok",
      "tiempo_ms": 38.8,
      "error": null
    },
    {
      "servicio": "punto-equilibrio",
      "estado": "ok",
      "tiempo_ms": 35.2,
      "error": null
    },
    {
      "servicio": "simulacion",
      "estado": "ok",
      "tiempo_ms": 35.9,
      "error": null
    },
    {
      "servicio": "surtido",
      "estado": "ok",
      "tiempo_ms": 36.6,
      "error": null
    },
    {
      "servicio": "notificaciones",
      "estado": "ok",
      "tiempo_ms": 42.0,
      "error": null
    },
    {
      "servicio": "reportes",
      "estado": "ok",
      "tiempo_ms": 27.8,
      "error": null
    },
    {
      "servicio": "sincronizacion",
      "estado": "ok",
      "tiempo_ms": 26.0,
      "error": null
    },
    {
      "servicio": "auditoria-monitoreo",
      "estado": "ok",
      "tiempo_ms": 27.3,
      "error": null
    }
  ]
}
```

**Explicación.** Cada 30 s se hace sola; con dos procesos, un candado en Redis deja que solo uno verifique.

**Evidencia en PostgreSQL.** `SELECT estado, count(*) AS verificaciones, round(avg(tiempo_ms), 1) AS ms_promedio FROM monitoreo_verificacion WHERE verificado_en > now() - interval '1 minute' GROUP BY estado`

```json
[
  {
    "estado": "ok",
    "verificaciones": 78,
    "ms_promedio": "32.5"
  }
]
```

### MNT-02 · Panel de monitoreo · PASA

**Objetivo.** Estado, última verificación, tiempo, versión, dependencias, errores y disponibilidad de cada servicio.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/monitoreo/estado`

```http
Accept: application/json
X-Traza-Id: cae9bccb-8a97-4835-aea4-d0b31c169bec
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 136 ms · traza `cae9bccb-8a97-4835-aea4-d0b31c169bec`

```json
{
  "generado_en": "2026-11-26T14:20:15-06:00",
  "resumen": {
    "total": 26,
    "ok": 26,
    "degradados": 0,
    "caidos": 0,
    "sin_datos": 0,
    "alertas_abiertas": 0,
    "monitor_activo": true,
    "intervalo_seg": 30,
    "ultima_ronda": "2026-11-26T14:20:15-06:00"
  },
  "servicios": [
    {
      "servicio": "auth",
      "puerto": 5101,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 28.1,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 113,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "usuarios",
      "puerto": 5102,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 26.5,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 26,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "productos",
      "puerto": 5103,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 33.5,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 24,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "pedidos",
      "puerto": 5104,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 37.1,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 134,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "entregas",
      "puerto": 5105,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 38.5,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "ok",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 60,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "planeacion",
      "puerto": 5106,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 34.5,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "ok",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 71,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "documentos",
      "puerto": 5107,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 34.0,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "ok",
        "bucket": "ok"
      },
      "error": null,
      "peticiones_hora": 46,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "zonas",
      "puerto": 5108,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 36.8,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 658,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "microhubs",
      "puerto": 5109,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 45.0,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 12,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "seguimiento",
      "puerto": 5110,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 36.8,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "ok",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 14,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "inventario",
      "puerto": 5111,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 26.9,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 173,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "precios",
      "puerto": 5112,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 35.7,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 84,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "proveedores",
      "puerto": 5113,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 25.8,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 78,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "abastecimiento",
      "puerto": 5114,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 23.2,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 90,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "demanda",
      "puerto": 5115,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 25.2,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 100,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "cobertura",
      "puerto": 5116,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 25.5,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 88,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "capacidad",
      "puerto": 5117,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 41.0,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 54,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "rutas",
      "puerto": 5118,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 47.0,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 57,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "costos",
      "puerto": 5119,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 38.8,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 90,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "punto-equilibrio",
      "puerto": 5120,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 35.2,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 76,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "simulacion",
      "puerto": 5121,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 35.9,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 97,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "surtido",
      "puerto": 5122,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 36.6,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 57,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "notificaciones",
      "puerto": 5124,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 42.0,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 48,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "reportes",
      "puerto": 5123,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 27.8,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 18,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 96.15,
      "bajo_objetivo": true
    },
    {
      "servicio": "sincronizacion",
      "puerto": 5125,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 26.0,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 24,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 96.15,
      "bajo_objetivo": true
    },
    {
      "servicio": "auditoria-monitoreo",
      "puerto": 5126,
      "estado": "ok",
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 27.3,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "ok",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 39,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 96.15,
      "bajo_objetivo": true
    }
  ],
  "dependencias_caidas": []
}
```

### MNT-03 · Panel en XML · PASA

**Objetivo.** El mismo panel validado contra auditoria_monitoreo.xsd.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/monitoreo/estado`

```http
Accept: application/xml
X-Traza-Id: 405003b4-f74b-4253-aa4b-d45d0c59f0b2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 129 ms · traza `405003b4-f74b-4253-aa4b-d45d0c59f0b2`

```xml
<?xml version='1.0' encoding='utf-8'?>
<monitoreo_estado xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><generado_en>2026-11-26T14:20:15-06:00</generado_en><resumen><total>26</total><ok>26</ok><degradados>0</degradados><caidos>0</caidos><sin_datos>0</sin_datos><alertas_abiertas>0</alertas_abiertas><monitor_activo>true</monitor_activo><intervalo_seg>30</intervalo_seg><ultima_ronda>2026-11-26T14:20:15-06:00</ultima_ronda></resumen><servicios><servicio><servicio>auth</servicio><puerto>5101</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>28.1</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>113</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>usuarios</servicio><puerto>5102</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>26.5</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>26</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>productos</servicio><puerto>5103</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>33.5</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>24</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>pedidos</servicio><puerto>5104</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>37.1</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>134</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>entregas</servicio><puerto>5105</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>38.5</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>ok</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>60</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>planeacion</servicio><puerto>5106</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>34.5</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>ok</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>71</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>documentos</servicio><puerto>5107</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>34</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>ok</mongo><bucket>ok</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>46</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>zonas</servicio><puerto>5108</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>36.8</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>658</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>microhubs</servicio><puerto>5109</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>45</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>12</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>seguimiento</servicio><puerto>5110</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>36.8</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>ok</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>14</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>inventario</servicio><puerto>5111</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>26.9</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>173</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>precios</servicio><puerto>5112</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>35.7</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>84</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>proveedores</servicio><puerto>5113</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>25.8</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>78</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>abastecimiento</servicio><puerto>5114</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>23.2</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>90</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>demanda</servicio><puerto>5115</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>25.2</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>100</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>cobertura</servicio><puerto>5116</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>25.5</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>88</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>capacidad</servicio><puerto>5117</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>41</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>54</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>rutas</servicio><puerto>5118</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>47</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>57</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>costos</servicio><puerto>5119</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>38.8</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>90</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>punto-equilibrio</servicio><puerto>5120</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>35.2</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>76</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>simulacion</servicio><puerto>5121</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>35.9</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>97</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>surtido</servicio><puerto>5122</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>36.6</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>57</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>notificaciones</servicio><puerto>5124</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>42</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>48</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>reportes</servicio><puerto>5123</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>27.8</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>18</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>96.15</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>sincronizacion</servicio><puerto>5125</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>26</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>24</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>96.15</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>auditoria-monitoreo</servicio><puerto>5126</puerto><estado>ok</estado><verificado_en>2026-11-26T14:20:15-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>27.3</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>ok</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>40</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>96.15</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio></servicios><dependencias_caidas /></monitoreo_estado>
```

### MNT-04 · Historial de un servicio · PASA

**Objetivo.** Serie de verificaciones, la más reciente primero.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/monitoreo/servicios/pedidos/historial?por_pagina=3`

```http
Accept: application/json
X-Traza-Id: 57b0327b-1b7f-4a36-be49-ff30377dc4d6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 55 ms · traza `57b0327b-1b7f-4a36-be49-ff30377dc4d6`

```json
{
  "datos": [
    {
      "verificado_en": "2026-11-26T14:20:15-06:00",
      "estado": "ok",
      "http_status": 200,
      "tiempo_ms": 37.1,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null
    },
    {
      "verificado_en": "2026-11-26T14:19:56-06:00",
      "estado": "ok",
      "http_status": 200,
      "tiempo_ms": 42.5,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null
    },
    {
      "verificado_en": "2026-11-26T14:19:25-06:00",
      "estado": "ok",
      "http_status": 200,
      "tiempo_ms": 27.4,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 3,
    "total": 26,
    "paginas": 9
  }
}
```

### MNT-05 · Disponibilidad de las últimas 24 horas · PASA

**Objetivo.** Porcentaje disponible, salud plena y percentiles p50 y p95.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/monitoreo/disponibilidad?horas=24`

```http
Accept: application/json
X-Traza-Id: 3177a9e2-733c-4583-bb52-c72294c8d75e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 58 ms · traza `3177a9e2-733c-4583-bb52-c72294c8d75e`

```json
{
  "horas": 24,
  "objetivo_pct": 99.0,
  "servicios": [
    {
      "servicio": "auth",
      "verificaciones": 26,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 48.5,
      "tiempo_p95_ms": 207.3,
      "tiempo_max_ms": 423.8,
      "bajo_objetivo": false
    },
    {
      "servicio": "usuarios",
      "verificaciones": 26,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 51.7,
      "tiempo_p95_ms": 178.3,
      "tiempo_max_ms": 497.6,
      "bajo_objetivo": false
    },
    {
      "servicio": "productos",
      "verificaciones": 26,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 53.0,
      "tiempo_p95_ms": 202.5,
      "tiempo_max_ms": 568.7,
      "bajo_objetivo": false
    },
    {
      "servicio": "pedidos",
      "verificaciones": 26,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 55.7,
      "tiempo_p95_ms": 185.6,
      "tiempo_max_ms": 252.1,
      "bajo_objetivo": false
    },
    {
      "servicio": "entregas",
      "verificaciones": 26,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 51.4,
      "tiempo_p95_ms": 227.2,
      "tiempo_max_ms": 636.9,
      "bajo_objetivo": false
    },
    {
      "servicio": "planeacion",
      "verificaciones": 26,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 60.1,
      "tiempo_p95_ms": 270.6,
      "tiempo_max_ms": 418.7,
      "bajo_objetivo": false
    },
    {
      "servicio": "documentos",
      "verificaciones": 26,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 58.6,
      "tiempo_p95_ms": 415.9,
      "tiempo_max_ms": 503.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "zonas",
      "verificaciones": 28,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 53.1,
      "tiempo_p95_ms": 125.4,
      "tiempo_max_ms": 601.5,
      "bajo_objetivo": false
    },
    {
      "servicio": "microhubs",
      "verificaciones": 26,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 46.4,
      "tiempo_p95_ms": 206.4,
      "tiempo_max_ms": 740.8,
      "bajo_objetivo": false
    },
    {
      "servicio": "seguimiento",
      "verificaciones": 26,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 49.5,
      "tiempo_p95_ms": 140.8,
      "tiempo_max_ms": 380.1,
      "bajo_objetivo": false
    },
    {
      "servicio": "inventario",
      "verificaciones": 26,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 43.8,
      "tiempo_p95_ms": 140.6,
      "tiempo_max_ms": 845.9,
      "bajo_objetivo": false
    },
    {
      "servicio": "precios",
      "verificaciones": 26,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 46.1,
      "tiempo_p95_ms": 102.6,
      "tiempo_max_ms": 309.4,
      "bajo_objetivo": false
    },
    {
      "servicio": "proveedores",
      "verificaciones": 26,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 47.6,
      "tiempo_p95_ms": 186.5,
      "tiempo_max_ms": 560.9,
      "bajo_objetivo": false
    },
    {
      "servicio": "abastecimiento",
      "verificaciones": 26,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 49.6,
      "tiempo_p95_ms": 106.5,
      "tiempo_max_ms": 243.5,
      "bajo_objetivo": false
    },
    {
      "servicio": "demanda",
      "verificaciones": 26,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 44.8,
      "tiempo_p95_ms": 177.9,
      "tiempo_max_ms": 368.1,
      "bajo_objetivo": false
    },
    {
      "servicio": "cobertura",
      "verificaciones": 26,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 52.1,
      "tiempo_p95_ms": 180.8,
      "tiempo_max_ms": 338.4,
      "bajo_objetivo": false
    },
    {
      "servicio": "capacidad",
      "verificaciones": 26,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 41.2,
      "tiempo_p95_ms": 143.6,
      "tiempo_max_ms": 149.6,
      "bajo_objetivo": false
    },
    {
      "servicio": "rutas",
      "verificaciones": 26,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 51.0,
      "tiempo_p95_ms": 111.3,
      "tiempo_max_ms": 386.5,
      "bajo_objetivo": false
    },
    {
      "servicio": "costos",
      "verificaciones": 26,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 45.5,
      "tiempo_p95_ms": 188.1,
      "tiempo_max_ms": 1393.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "punto-equilibrio",
      "verificaciones": 26,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 40.0,
      "tiempo_p95_ms": 156.9,
      "tiempo_max_ms": 325.9,
      "bajo_objetivo": false
    },
    {
      "servicio": "simulacion",
      "verificaciones": 26,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 36.0,
      "tiempo_p95_ms": 115.1,
      "tiempo_max_ms": 151.7,
      "bajo_objetivo": false
    },
    {
      "servicio": "surtido",
      "verificaciones": 26,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 41.8,
      "tiempo_p95_ms": 128.9,
      "tiempo_max_ms": 234.9,
      "bajo_objetivo": false
    },
    {
      "servicio": "notificaciones",
      "verificaciones": 26,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 38.0,
      "tiempo_p95_ms": 148.8,
      "tiempo_max_ms": 252.1,
      "bajo_objetivo": false
    },
    {
      "servicio": "reportes",
      "verificaciones": 26,
      "caidas": 1,
      "disponibilidad_pct": 96.15,
      "salud_plena_pct": 96.15,
      "tiempo_p50_ms": 38.5,
      "tiempo_p95_ms": 140.9,
      "tiempo_max_ms": 186.5,
      "bajo_objetivo": true
    },
    {
      "servicio": "sincronizacion",
      "verificaciones": 26,
      "caidas": 1,
      "disponibilidad_pct": 96.15,
      "salud_plena_pct": 96.15,
      "tiempo_p50_ms": 30.6,
      "tiempo_p95_ms": 133.5,
      "tiempo_max_ms": 642.7,
      "bajo_objetivo": true
    },
    {
      "servicio": "auditoria-monitoreo",
      "verificaciones": 26,
      "caidas": 1,
      "disponibilidad_pct": 96.15,
      "salud_plena_pct": 96.15,
      "tiempo_p50_ms": 33.5,
      "tiempo_p95_ms": 168.2,
      "tiempo_max_ms": 271.4,
      "bajo_objetivo": true
    }
  ]
}
```

### MNT-06 · Tráfico y errores · PASA

**Objetivo.** Peticiones, errores y percentiles de duración por servicio, desde MongoDB.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/monitoreo/metricas?minutos=60`

```http
Accept: application/json
X-Traza-Id: 93938f13-ca7c-4442-94ea-bc9d7d446b2c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 59 ms · traza `93938f13-ca7c-4442-94ea-bc9d7d446b2c`

```json
{
  "minutos": 60,
  "peticiones_total": 2335,
  "servicios": [
    {
      "servicio": "auth",
      "peticiones": 113,
      "errores_5xx": 0,
      "errores_4xx": 16,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 288,
      "duracion_p95_ms": 451,
      "duracion_p99_ms": 1290
    },
    {
      "servicio": "usuarios",
      "peticiones": 26,
      "errores_5xx": 0,
      "errores_4xx": 12,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 24,
      "duracion_p95_ms": 59,
      "duracion_p99_ms": 137
    },
    {
      "servicio": "productos",
      "peticiones": 24,
      "errores_5xx": 0,
      "errores_4xx": 9,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 2,
      "duracion_p95_ms": 103,
      "duracion_p99_ms": 132
    },
    {
      "servicio": "pedidos",
      "peticiones": 134,
      "errores_5xx": 0,
      "errores_4xx": 18,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 76,
      "duracion_p95_ms": 155,
      "duracion_p99_ms": 528
    },
    {
      "servicio": "entregas",
      "peticiones": 60,
      "errores_5xx": 0,
      "errores_4xx": 17,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 68,
      "duracion_p95_ms": 450,
      "duracion_p99_ms": 1864
    },
    {
      "servicio": "planeacion",
      "peticiones": 71,
      "errores_5xx": 0,
      "errores_4xx": 15,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 45,
      "duracion_p95_ms": 234,
      "duracion_p99_ms": 555
    },
    {
      "servicio": "documentos",
      "peticiones": 46,
      "errores_5xx": 0,
      "errores_4xx": 11,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 23,
      "duracion_p95_ms": 76,
      "duracion_p99_ms": 149
    },
    {
      "servicio": "zonas",
      "peticiones": 658,
      "errores_5xx": 0,
      "errores_4xx": 649,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 0,
      "duracion_p95_ms": 6,
      "duracion_p99_ms": 30
    },
    {
      "servicio": "microhubs",
      "peticiones": 12,
      "errores_5xx": 0,
      "errores_4xx": 6,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 19,
      "duracion_p95_ms": 94,
      "duracion_p99_ms": 94
    },
    {
      "servicio": "seguimiento",
      "peticiones": 14,
      "errores_5xx": 0,
      "errores_4xx": 6,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 27,
      "duracion_p95_ms": 53,
      "duracion_p99_ms": 53
    },
    {
      "servicio": "inventario",
      "peticiones": 173,
      "errores_5xx": 0,
      "errores_4xx": 24,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 61,
      "duracion_p95_ms": 165,
      "duracion_p99_ms": 345
    },
    {
      "servicio": "precios",
      "peticiones": 84,
      "errores_5xx": 0,
      "errores_4xx": 18,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 50,
      "duracion_p95_ms": 140,
      "duracion_p99_ms": 165
    },
    {
      "servicio": "proveedores",
      "peticiones": 78,
      "errores_5xx": 0,
      "errores_4xx": 21,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 58,
      "duracion_p95_ms": 156,
      "duracion_p99_ms": 237
    },
    {
      "servicio": "abastecimiento",
      "peticiones": 90,
      "errores_5xx": 0,
      "errores_4xx": 42,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 58,
      "duracion_p95_ms": 287,
      "duracion_p99_ms": 372
    },
    {
      "servicio": "demanda",
      "peticiones": 100,
      "errores_5xx": 0,
      "errores_4xx": 15,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 98,
      "duracion_p95_ms": 177,
      "duracion_p99_ms": 394
    },
    {
      "servicio": "cobertura",
      "peticiones": 88,
      "errores_5xx": 0,
      "errores_4xx": 12,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 44,
      "duracion_p95_ms": 117,
      "duracion_p99_ms": 149
    },
    {
      "servicio": "capacidad",
      "peticiones": 54,
      "errores_5xx": 0,
      "errores_4xx": 12,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 46,
      "duracion_p95_ms": 146,
      "duracion_p99_ms": 192
    },
    {
      "servicio": "rutas",
      "peticiones": 57,
      "errores_5xx": 0,
      "errores_4xx": 18,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 138,
      "duracion_p95_ms": 371,
      "duracion_p99_ms": 507
    },
    {
      "servicio": "costos",
      "peticiones": 90,
      "errores_5xx": 0,
      "errores_4xx": 12,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 47,
      "duracion_p95_ms": 100,
      "duracion_p99_ms": 138
    },
    {
      "servicio": "punto-equilibrio",
      "peticiones": 76,
      "errores_5xx": 0,
      "errores_4xx": 9,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 58,
      "duracion_p95_ms": 393,
      "duracion_p99_ms": 559
    },
    {
      "servicio": "simulacion",
      "peticiones": 97,
      "errores_5xx": 0,
      "errores_4xx": 18,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 29,
      "duracion_p95_ms": 719,
      "duracion_p99_ms": 1015
    },
    {
      "servicio": "surtido",
      "peticiones": 57,
      "errores_5xx": 0,
      "errores_4xx": 18,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 49,
      "duracion_p95_ms": 1204,
      "duracion_p99_ms": 3201
    },
    {
      "servicio": "notificaciones",
      "peticiones": 48,
      "errores_5xx": 0,
      "errores_4xx": 12,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 30,
      "duracion_p95_ms": 78,
      "duracion_p99_ms": 110
    },
    {
      "servicio": "reportes",
      "peticiones": 18,
      "errores_5xx": 0,
      "errores_4xx": 4,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 230,
      "duracion_p95_ms": 829,
      "duracion_p99_ms": 829
    },
    {
      "servicio": "sincronizacion",
      "peticiones": 24,
      "errores_5xx": 0,
      "errores_4xx": 4,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 61,
      "duracion_p95_ms": 396,
      "duracion_p99_ms": 412
    },
    {
      "servicio": "auditoria-monitoreo",
      "peticiones": 43,
      "errores_5xx": 0,
      "errores_4xx": 6,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 60,
      "duracion_p95_ms": 223,
      "duracion_p99_ms": 239
    }
  ]
}
```

### MNT-07 · Umbrales y su justificación · PASA

**Objetivo.** Cada umbral con su origen y cómo se calibra.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/monitoreo/supuestos`

```http
Accept: application/json
X-Traza-Id: 8c42e26f-b8f1-467e-a322-e6413283994c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 33 ms · traza `8c42e26f-b8f1-467e-a322-e6413283994c`

```json
{
  "datos": [
    {
      "clave": "********",
      "valor": "99",
      "unidad": "%",
      "origen": "normativo",
      "justificacion": "99 % es el objetivo razonable para una VM única sin alta disponibilidad (unas 7 horas de caída al mes).",
      "como_calibrar": "Cambiar si el acuerdo de servicio con el cliente pide otro valor."
    },
    {
      "clave": "********",
      "valor": "20",
      "unidad": "peticiones",
      "origen": "supuesto",
      "justificacion": "Con menos de 20 peticiones un solo error ya sería 5 % o más; se exige una muestra mínima para no alertar por casualidad.",
      "como_calibrar": "Ajustar al tráfico real: debe ser una fracción pequeña de lo que recibe un servicio en la ventana."
    },
    {
      "clave": "********",
      "valor": "20",
      "unidad": "%",
      "origen": "supuesto",
      "justificacion": "20 % de errores del servidor en 10 minutos es una falla clara y no un error aislado.",
      "como_calibrar": "Revisar las alertas falsas del primer mes y ajustar."
    },
    {
      "clave": "********",
      "valor": "10",
      "unidad": "minutos",
      "origen": "supuesto",
      "justificacion": "10 minutos son suficientes peticiones para distinguir una falla de un error aislado sin tardar en avisar.",
      "como_calibrar": "Alargarla si el tráfico es muy bajo; acortarla si se quiere avisar más rápido."
    },
    {
      "clave": "********",
      "valor": "30",
      "unidad": "segundos",
      "origen": "supuesto",
      "justificacion": "30 segundos detecta una caída en menos de un minuto y genera…(144 caracteres)",
      "como_calibrar": "Subirlo si el panel carga demasiado la base; bajarlo si se exige detectar caídas en menos de medio minuto."
    },
    {
      "clave": "********",
      "valor": "1000",
      "unidad": "ms",
      "origen": "supuesto",
      "justificacion": "Un /salud sano responde en decenas de milisegundos; 1 s ya indica saturación de alguna dependencia.",
      "como_calibrar": "Tomar el p95 de tiempo_ms de monitoreo_verificacion en una semana normal y poner el umbral al doble."
    },
    {
      "clave": "********",
      "valor": "7",
      "unidad": "días",
      "origen": "supuesto",
      "justificacion": "Una semana alcanza para ver tendencias y revisar un incidente reciente; a 30 s por servicio son unas 600 mil filas por semana.",
      "como_calibrar": "Alargarla si se exige historial más largo y el volumen de la base lo permite."
    },
    {
      "clave": "********",
      "valor": "3",
      "unidad": "segundos",
      "origen": "supuesto",
      "justificacion": "3 segundos es más de lo que tarda un /salud sano; un servicio que no contesta en ese tiempo ya no atiende a nadie en la práctica.",
      "como_calibrar": "Subirlo si hay falsos «caído» por picos de carga; bajarlo para detectar antes."
    }
  ]
}
```

### MNT-08 · Alertas abiertas · PASA

**Objetivo.** Con el umbral de latencia en 0 ms, la verificación abre una alerta real.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/monitoreo/alertas?estado=abiertas&servicio=zonas`

```http
Accept: application/json
X-Traza-Id: 59d4bf7b-078b-460a-b7f4-a7ee277c9c34
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 53 ms · traza `59d4bf7b-078b-460a-b7f4-a7ee277c9c34`

```json
{
  "datos": [
    {
      "id": 195,
      "servicio": "zonas",
      "tipo": "latencia_alta",
      "severidad": "media",
      "detalle": "/salud de zonas tardó 16 ms (umbral 0 ms).",
      "abierta_en": "2026-11-26T14:20:15-06:00",
      "cerrada_en": null,
      "duracion_seg": 0,
      "reconocida": null
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 1,
    "paginas": 1
  }
}
```

**Evidencia en PostgreSQL.** `SELECT servicio, tipo, severidad, detalle FROM monitoreo_alerta WHERE cerrada_en IS NULL AND servicio = 'zonas'`

```json
[
  {
    "servicio": "zonas",
    "tipo": "latencia_alta",
    "severidad": "media",
    "detalle": "/salud de zonas tardó 16 ms (umbral 0 ms)."
  }
]
```

### MNT-09 · Reconocer una alerta · PASA

**Objetivo.** Queda quién se hizo cargo y cuándo.

**Petición.** `POST http://auditoria-monitoreo:5126/api/v1/monitoreo/alertas/195/reconocer`

```http
Accept: application/json
X-Traza-Id: 166f8189-9b9f-4719-95eb-21c60038f34c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 63 ms · traza `166f8189-9b9f-4719-95eb-21c60038f34c`

```json
{
  "id": 195,
  "servicio": "zonas",
  "tipo": "latencia_alta",
  "severidad": "media",
  "detalle": "/salud de zonas tardó 16 ms (umbral 0 ms).",
  "abierta_en": "2026-11-26T14:20:15-06:00",
  "cerrada_en": null,
  "duracion_seg": 0,
  "reconocida": {
    "por": {
      "id": 1,
      "nombre": "Mauro Castillo Peña"
    },
    "en": "2026-11-26T14:20:15-06:00"
  }
}
```

**Evidencia en PostgreSQL.** `SELECT fecha, accion, detalle, usuario_id FROM auditoria WHERE entidad = 'monitoreo_alerta' AND entidad_id = %s ORDER BY id`

```json
[
  {
    "fecha": "2026-11-26 14:20:15.690329-06:00",
    "accion": "alta",
    "detalle": null,
    "usuario_id": 1
  },
  {
    "fecha": "2026-11-26 14:20:15.829560-06:00",
    "accion": "modificacion",
    "detalle": null,
    "usuario_id": 1
  }
]
```

### MNT-10 · Reconocer sin permiso · PASA

**Objetivo.** El auditor ve el monitoreo pero no lo opera.

**Petición.** `POST http://auditoria-monitoreo:5126/api/v1/monitoreo/alertas/195/reconocer`

```http
Accept: application/json
X-Traza-Id: 0a091bf0-b51d-4f5a-b546-65512ecc2171
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 403 (esperado 403) · 57 ms · traza `0a091bf0-b51d-4f5a-b546-65512ecc2171`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "0a091bf0-b51d-4f5a-b546-65512ecc2171"
  }
}
```

### MNT-11 · El operador no ve el monitoreo · PASA

**Objetivo.** Sin monitoreo.ver.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/monitoreo/estado`

```http
Accept: application/json
X-Traza-Id: 8799fb2a-1052-42af-9582-8e61f7760ec0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 31 ms · traza `8799fb2a-1052-42af-9582-8e61f7760ec0`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "8799fb2a-1052-42af-9582-8e61f7760ec0"
  }
}
```

### AUD-01 · Bitácora con filtros · PASA

**Objetivo.** Quién cambió qué, cuándo y desde dónde.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria?modulo=pedidos&por_pagina=3`

```http
Accept: application/json
X-Traza-Id: 7adcec8d-b857-48b2-b657-209522b535a4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 60 ms · traza `7adcec8d-b857-48b2-b657-209522b535a4`

```json
{
  "datos": [
    {
      "id": 16671,
      "fecha": "2026-11-26T14:20:03-06:00",
      "usuario": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "correo_intento": null,
      "ip_origen": null,
      "modulo": "pedidos",
      "accion": "cambio_estado",
      "entidad": {
        "tipo": "pedido",
        "id": "549"
      },
      "exitoso": true,
      "detalle": null,
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-26T14:20:00.833879-06:00",
          "nuevo": "2026-11-26T14:20:03.787702-06:00"
        },
        {
          "campo": "cerrado_en",
          "anterior": null,
          "nuevo": "2026-11-26T14:20:03.787702-06:00"
        },
        {
          "campo": "estado",
          "anterior": "asignado",
          "nuevo": "cancelado"
        },
        {
          "campo": "motivo_cancelacion",
          "anterior": null,
          "nuevo": "Pedido de prueba"
        }
      ]
    },
    {
      "id": 16668,
      "fecha": "2026-11-26T14:20:03-06:00",
      "usuario": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "correo_intento": null,
      "ip_origen": null,
      "modulo": "pedidos",
      "accion": "cambio_estado",
      "entidad": {
        "tipo": "pedido",
        "id": "548"
      },
      "exitoso": true,
      "detalle": null,
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-26T14:20:00.833879-06:00",
          "nuevo": "2026-11-26T14:20:03.787702-06:00"
        },
        {
          "campo": "cerrado_en",
          "anterior": null,
          "nuevo": "2026-11-26T14:20:03.787702-06:00"
        },
        {
          "campo": "estado",
          "anterior": "asignado",
          "nuevo": "cancelado"
        },
        {
          "campo": "motivo_cancelacion",
          "anterior": null,
          "nuevo": "Pedido de prueba"
        }
      ]
    },
    {
      "id": 16665,
      "fecha": "2026-11-26T14:20:03-06:00",
      "usuario": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "correo_intento": null,
      "ip_origen": null,
      "modulo": "pedidos",
      "accion": "cambio_estado",
      "entidad": {
        "tipo": "pedido",
        "id": "547"
      },
      "exitoso": true,
      "detalle": null,
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-26T14:20:00.833879-06:00",
          "nuevo": "2026-11-26T14:20:03.787702-06:00"
        },
        {
          "campo": "cerrado_en",
          "anterior": null,
          "nuevo": "2026-11-26T14:20:03.787702-06:00"
        },
        {
          "campo": "estado",
          "anterior": "asignado",
          "nuevo": "cancelado"
        },
        {
          "campo": "motivo_cancelacion",
          "anterior": null,
          "nuevo": "Pedido de prueba"
        }
      ]
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 3,
    "total": 4493,
    "paginas": 1498
  }
}
```

**Explicación.** La bitácora es de solo escritura (RN31); los valores de contraseñas nunca aparecen.

### AUD-02 · Accesos al sistema · PASA

**Objetivo.** Inicios, fallos, bloqueos y accesos denegados del periodo.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/accesos`

```http
Accept: application/json
X-Traza-Id: dc6fb96d-a900-47c5-8872-81344dee641d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 87 ms · traza `dc6fb96d-a900-47c5-8872-81344dee641d`

```json
{
  "desde": "2026-11-19",
  "hasta": "2026-11-26",
  "totales": {
    "login_exitoso": 711,
    "login_fallido": 27,
    "logout": 12,
    "bloqueo_cuenta": 1,
    "desbloqueo": 0,
    "acceso_denegado": 871
  },
  "correos_con_mas_fallos": [
    {
      "correo": "repartidor1@codex.mx",
      "intentos": 5,
      "ultimo_intento": "2026-11-26T00:39:02-06:00"
    },
    {
      "correo": "planeador@codex.mx",
      "intentos": 5,
      "ultimo_intento": "2026-11-26T00:38:58-06:00"
    },
    {
      "correo": "no.existe.ola3@codex.mx",
      "intentos": 4,
      "ultimo_intento": "2026-11-25T15:46:41-06:00"
    },
    {
      "correo": "auditor@codex.mx",
      "intentos": 3,
      "ultimo_intento": "2026-11-26T14:19:28-06:00"
    },
    {
      "correo": "no.existe.fc976e0727@codex.mx",
      "intentos": 1,
      "ultimo_intento": "2026-11-26T00:36:49-06:00"
    }
  ],
  "denegados_frecuentes": [
    {
      "detalle": "GET /api/v1/auditoria sin auditoria.ver",
      "veces": 54
    },
    {
      "detalle": "GET /api/v1/auditoria/accesos sin auditoria.ver",
      "veces": 52
    },
    {
      "detalle": "GET /api/v1/auditoria/trazabilidad/inventario sin auditoria.ver",
      "veces": 52
    },
    {
      "detalle": "GET /api/v1/auditoria/trazabilidad/pedido/1 sin auditoria.ver",
      "veces": 52
    },
    {
      "detalle": "GET /api/v1/monitoreo/estado sin monitoreo.ver",
      "veces": 48
    }
  ]
}
```

### AUD-03 · Línea de tiempo de un pedido · PASA

**Objetivo.** Une bitácora, cambios de estado, inventario y archivos del pedido.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/pedido/1`

```http
Accept: application/json
X-Traza-Id: 6745ce50-ec12-4524-9b1e-889be1897564
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 218 ms · traza `6745ce50-ec12-4524-9b1e-889be1897564`

```json
{
  "objeto": {
    "tipo": "pedido",
    "id": "1"
  },
  "total": 20,
  "eventos": [
    {
      "fecha": "2026-10-19T19:30:41-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "actualizado_en = 2026-10-20T01:30:41.656544+00:00; asignado_en = None; cerrado_en = None; cliente_id = 40",
      "usuario": null,
      "entidad": {
        "tipo": "pedido",
        "id": "1"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": null,
          "nuevo": "2026-10-20T01:30:41.656544+00:00"
        },
        {
          "campo": "asignado_en",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "cerrado_en",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "cliente_id",
          "anterior": null,
          "nuevo": "40"
        },
        {
          "campo": "costo_envio",
          "anterior": null,
          "nuevo": "15.0"
        },
        {
          "campo": "creado_en",
          "anterior": null,
          "nuevo": "2026-10-20T01:30:41.656544+00:00"
        },
        {
          "campo": "domicilio_id",
          "anterior": null,
          "nuevo": "40"
        },
        {
          "campo": "estado",
          "anterior": null,
          "nuevo": "creado"
        },
        {
          "campo": "folio",
          "anterior": null,
          "nuevo": "PED-20261020-000001"
        },
        {
          "campo": "id",
          "anterior": null,
          "nuevo": "1"
        },
        {
          "campo": "microhub_id",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "motivo_cancelacion",
          "anterior": null,
          "nuevo": null
        }
      ]
    },
    {
      "fecha": "2026-10-19T19:30:41-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "asignado_en = 2026-10-20T01:30:41.656544+00:00; estado: creado → asignado; microhub_id = 3",
      "usuario": null,
      "entidad": {
        "tipo": "pedido",
        "id": "1"
      },
      "cambios": [
        {
          "campo": "asignado_en",
          "anterior": null,
          "nuevo": "2026-10-20T01:30:41.656544+00:00"
        },
        {
          "campo": "estado",
          "anterior": "creado",
          "nuevo": "asignado"
        },
        {
          "campo": "microhub_id",
          "anterior": null,
          "nuevo": "3"
        }
      ]
    },
    {
      "fecha": "2026-10-19T19:30:41-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "asignado_en: 2026-10-20T01:30:41.656544+00:00 → 2026-10-15T0…(156 caracteres)",
      "usuario": null,
      "entidad": {
        "tipo": "pedido",
        "id": "1"
      },
      "cambios": [
        {
          "campo": "asignado_en",
          "anterior": "2026-10-20T01:30:41.656544+00:00",
          "nuevo": "2026-10-15T07:47:04.7975+00:00"
        },
        {
          "campo": "creado_en",
          "anterior": "2026-10-20T01:30:41.656544+00:00",
          "nuevo": "2026-10-15T07:47:04.7975+00:00"
        }
      ]
    },
    {
      "fecha": "2026-10-19T19:30:41-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "nuevo → creado (proceso alta_pedido)",
      "usuario": null,
      "entidad": {
        "tipo": "pedido",
        "id": "1"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-19T19:30:41-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "creado → asignado (proceso motor_asignacion)",
      "usuario": null,
      "entidad": {
        "tipo": "pedido",
        "id": "1"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-19T19:30:41-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -1 de producto 16 en microhub 3 (existencia 23)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "3-16"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-19T19:30:41-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -1 de producto 31 en microhub 3 (existencia 72)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "3-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-19T19:30:41-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -1 de producto 37 en microhub 3 (existencia 2)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "3-37"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-19T19:30:41-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -1 de producto 41 en microhub 3 (existencia 22)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "3-41"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-19T19:30:41-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -1 de producto 48 en microhub 3 (existencia 49)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "3-48"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-19T19:32:16-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-10-20T01:30:41.656544+00:00 → 2026-10-20T01:32:16.697978+00:00; estado: asignado → en_preparacion",
      "usuario": {
        "id": 4,
        "nombre": "Jorge Antonio Arreola Cantu"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "1"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-10-20T01:30:41.656544+00:00",
          "nuevo": "2026-10-20T01:32:16.697978+00:00"
        },
        {
          "campo": "estado",
          "anterior": "asignado",
          "nuevo": "en_preparacion"
        }
      ]
    },
    {
      "fecha": "2026-10-19T19:32:16-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "listo_en = 2026-10-20T01:32:16.697978+00:00",
      "usuario": {
        "id": 4,
        "nombre": "Jorge Antonio Arreola Cantu"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "1"
      },
      "cambios": [
        {
          "campo": "listo_en",
          "anterior": null,
          "nuevo": "2026-10-20T01:32:16.697978+00:00"
        }
      ]
    },
    {
      "fecha": "2026-10-19T19:32:16-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "asignada_en = 2026-10-20T01:32:16.697978+00:00; cambio_entregado = None; capturado_en = None; cerrada_por_usuario_id = None",
      "usuario": {
        "id": 4,
        "nombre": "Jorge Antonio Arreola Cantu"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "132"
      },
      "cambios": [
        {
          "campo": "asignada_en",
          "anterior": null,
          "nuevo": "2026-10-20T01:32:16.697978+00:00"
        },
        {
          "campo": "cambio_entregado",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "capturado_en",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "cerrada_por_usuario_id",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "cierre_latitud",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "cierre_longitud",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "cierre_precision_m",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "confirmacion_recepcion",
          "anterior": null,
          "nuevo": "false"
        },
        {
          "campo": "costo_entrega_estimado",
          "anterior": null,
          "nuevo": "22.0"
        },
        {
          "campo": "distancia_km",
          "anterior": null,
          "nuevo": "1.45"
        },
        {
          "campo": "evidencia_ids",
          "anterior": null,
          "nuevo": null
        }
      ]
    },
    {
      "fecha": "2026-10-19T19:32:16-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "estado: en_preparacion → en_ruta",
      "usuario": {
        "id": 4,
        "nombre": "Jorge Antonio Arreola Cantu"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "1"
      },
      "cambios": [
        {
          "campo": "estado",
          "anterior": "en_preparacion",
          "nuevo": "en_ruta"
        }
      ]
    },
    {
      "fecha": "2026-10-19T19:32:16-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "asignado → en_preparacion",
      "usuario": {
        "id": 4,
        "nombre": "Jorge Antonio Arreola Cantu"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "1"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-19T19:32:16-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "en_preparacion → en_ruta",
      "usuario": {
        "id": 4,
        "nombre": "Jorge Antonio Arreola Cantu"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "1"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-19T19:32:18-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "cambio_entregado = 0.0; capturado_en = 2026-10-13T00:40:00+00:00; cerrada_por_usuario_id = 7; cierre_en = 2026-10-20T01:32:18.497549+00:00",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "132"
      },
      "cambios": [
        {
          "campo": "cambio_entregado",
          "anterior": null,
          "nuevo": "0.0"
        },
        {
          "campo": "capturado_en",
          "anterior": null,
          "nuevo": "2026-10-13T00:40:00+00:00"
        },
        {
          "campo": "cerrada_por_usuario_id",
          "anterior": null,
          "nuevo": "7"
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": "2026-10-20T01:32:18.497549+00:00"
        },
        {
          "campo": "cierre_latitud",
          "anterior": null,
          "nuevo": "25.7491"
        },
        {
          "campo": "cierre_longitud",
          "anterior": null,
          "nuevo": "-100.3611"
        },
        {
          "campo": "confirmacion_recepcion",
          "anterior": "false",
          "nuevo": "true"
        },
        {
          "campo": "evidencia_ids",
          "anterior": null,
          "nuevo": "[\"6ad6c4a2f02e9460f6b40acb\"]"
        },
        {
          "campo": "evidencia_url",
          "anterior": null,
          "nuevo": "/api/v1/documentos/6ad6c4a2f02e9460f6b40acb"
        },
        {
          "campo": "id_cliente_local",
          "anterior": null,
          "nuevo": "49804448-d487-4521-a334-ab1b386cf4b5"
        },
        {
          "campo": "incidencia",
          "anterior": null,
          "nuevo": "El cliente rechazó una línea."
        },
        {
          "campo": "monto_cobrado",
          "anterior": null,
          "nuevo": "10.0"
        }
      ]
    },
    {
      "fecha": "2026-10-19T19:32:18-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-10-20T01:32:16.697978+00:00 → 2026-10-2…(217 caracteres)",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "1"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-10-20T01:32:16.697978+00:00",
          "nuevo": "2026-10-20T01:32:18.497549+00:00"
        },
        {
          "campo": "cerrado_en",
          "anterior": null,
          "nuevo": "2026-10-20T01:32:18.497549+00:00"
        },
        {
          "campo": "estado",
          "anterior": "en_ruta",
          "nuevo": "entrega_parcial"
        },
        {
          "campo": "motivo_cancelacion",
          "anterior": null,
          "nuevo": "El cliente rechazó una línea."
        }
      ]
    },
    {
      "fecha": "2026-10-19T19:32:18-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "en_ruta → entrega_parcial. El cliente rechazó una línea.",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "1"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-19T19:32:18-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "devolucion_parcial: +1 de producto 31 en microhub 3 (existencia 72). Entrega parcial: regresan las unidades devueltas (RN28).",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "3-31"
      },
      "cambios": []
    }
  ]
}
```

**Evidencia en PostgreSQL.** `SELECT estado_anterior, estado_nuevo, fecha FROM historial_estatus WHERE pedido_id = %s ORDER BY fecha`

```json
[
  {
    "estado_anterior": null,
    "estado_nuevo": "creado",
    "fecha": "2026-10-19 19:30:41.656544-06:00"
  },
  {
    "estado_anterior": "creado",
    "estado_nuevo": "asignado",
    "fecha": "2026-10-19 19:30:41.656544-06:00"
  },
  {
    "estado_anterior": "asignado",
    "estado_nuevo": "en_preparacion",
    "fecha": "2026-10-19 19:32:16.697978-06:00"
  },
  {
    "estado_anterior": "en_preparacion",
    "estado_nuevo": "en_ruta",
    "fecha": "2026-10-19 19:32:16.697978-06:00"
  },
  {
    "estado_anterior": "en_ruta",
    "estado_nuevo": "entrega_parcial",
    "fecha": "2026-10-19 19:32:18.497549-06:00"
  }
]
```

### AUD-04 · Línea de tiempo de una entrega · PASA

**Objetivo.** Bitácora y archivos de la entrega.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/entrega/1`

```http
Accept: application/json
X-Traza-Id: bdfa72dc-3a08-493e-ac1b-b7d30af067f6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 156 ms · traza `bdfa72dc-3a08-493e-ac1b-b7d30af067f6`

```json
{
  "objeto": {
    "tipo": "entrega",
    "id": "1"
  },
  "total": 2,
  "eventos": [
    {
      "fecha": "2026-10-19T19:30:41-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "asignada_en = 2026-09-15T23:38:39.893332+00:00; cambio_entregado = None; cerrada_por_usuario_id = None; cierre_en = None",
      "usuario": null,
      "entidad": {
        "tipo": "entrega",
        "id": "1"
      },
      "cambios": [
        {
          "campo": "asignada_en",
          "anterior": null,
          "nuevo": "2026-09-15T23:38:39.893332+00:00"
        },
        {
          "campo": "cambio_entregado",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "cerrada_por_usuario_id",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "confirmacion_recepcion",
          "anterior": null,
          "nuevo": "false"
        },
        {
          "campo": "evidencia_url",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "id",
          "anterior": null,
          "nuevo": "1"
        },
        {
          "campo": "incidencia",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "monto_cobrado",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "pedido_id",
          "anterior": null,
          "nuevo": "2"
        },
        {
          "campo": "repartidor_id",
          "anterior": null,
          "nuevo": "7"
        },
        {
          "campo": "resultado",
          "anterior": null,
          "nuevo": null
        }
      ]
    },
    {
      "fecha": "2026-10-19T19:30:41-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "cambio_entregado = 7.5; cierre_en = 2026-09-15T23:38:39.893332+00:00; confirmacion_recepcion: false → true; monto_cobrado = 250.0",
      "usuario": null,
      "entidad": {
        "tipo": "entrega",
        "id": "1"
      },
      "cambios": [
        {
          "campo": "cambio_entregado",
          "anterior": null,
          "nuevo": "7.5"
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": "2026-09-15T23:38:39.893332+00:00"
        },
        {
          "campo": "confirmacion_recepcion",
          "anterior": "false",
          "nuevo": "true"
        },
        {
          "campo": "monto_cobrado",
          "anterior": null,
          "nuevo": "250.0"
        },
        {
          "campo": "resultado",
          "anterior": null,
          "nuevo": "entregado"
        }
      ]
    }
  ]
}
```

### AUD-05 · Movimientos de un producto en un microhub · PASA

**Objetivo.** Trazabilidad del inventario.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/inventario?microhub_id=1&producto_id=1`

```http
Accept: application/json
X-Traza-Id: f96eb2ce-68dd-448b-8184-8f60eb86c1ee
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 69 ms · traza `f96eb2ce-68dd-448b-8184-8f60eb86c1ee`

```json
{
  "objeto": {
    "tipo": "inventario",
    "id": "1-1"
  },
  "total": 16,
  "eventos": [
    {
      "fecha": "2026-09-05T21:35:37-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -1 de producto 1 en microhub 1 (existencia 63)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-1"
      },
      "cambios": []
    },
    {
      "fecha": "2026-09-10T03:35:26-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -1 de producto 1 en microhub 1 (existencia 62)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-1"
      },
      "cambios": []
    },
    {
      "fecha": "2026-09-21T19:04:44-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -1 de producto 1 en microhub 1 (existencia 61)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-1"
      },
      "cambios": []
    },
    {
      "fecha": "2026-09-30T06:41:58-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -1 de producto 1 en microhub 1 (existencia 64)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-1"
      },
      "cambios": []
    },
    {
      "fecha": "2026-09-30T14:18:11-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -1 de producto 1 en microhub 1 (existencia 60)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-1"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-08T16:11:50-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -1 de producto 1 en microhub 1 (existencia 65)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-1"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-19T19:30:40-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "recepcion: +66 de producto 1 en microhub 1 (existencia 66). Carga inicial de semilla",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-1"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-20T00:32:01-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -2 de producto 1 en microhub 1 (existencia 58)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-1"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-20T00:32:06-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "devolucion_cancelacion: +2 de producto 1 en microhub 1 (existencia 60). Pedido de prueba cancelado",
      "usuario": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-1"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-20T00:32:50-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -2 de producto 1 en microhub 1 (existencia 58)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-1"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-20T00:32:53-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "devolucion_cancelacion: +2 de producto 1 en microhub 1 (existencia 60). Pedido de prueba cancelado",
      "usuario": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-1"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-20T00:51:29-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -4 de producto 1 en microhub 1 (existencia 56)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-1"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-20T00:51:36-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "devolucion_cancelacion: +4 de producto 1 en microhub 1 (existencia 60). Pedido de prueba cancelado",
      "usuario": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-1"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-20T08:09:08-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -4 de producto 1 en microhub 1 (existencia 56)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-1"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-20T08:09:14-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "devolucion_cancelacion: +4 de producto 1 en microhub 1 (existencia 60). Pedido de prueba cancelado",
      "usuario": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-1"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-25T15:47:14-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -2 de producto 1 en microhub 1 (existencia 58)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-1"
      },
      "cambios": []
    }
  ]
}
```

### AUD-06 · La bitácora está restringida · PASA

**Objetivo.** El planeador no tiene auditoria.ver; el intento queda registrado.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria`

```http
Accept: application/json
X-Traza-Id: 4e5c6cec-659b-494e-82e4-6690ef5bab77
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 72 ms · traza `4e5c6cec-659b-494e-82e4-6690ef5bab77`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "4e5c6cec-659b-494e-82e4-6690ef5bab77"
  }
}
```

**Evidencia en PostgreSQL.** `SELECT fecha, accion, detalle, exitoso FROM auditoria WHERE accion = 'acceso_denegado' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "fecha": "2026-11-26 14:20:16.965973-06:00",
    "accion": "acceso_denegado",
    "detalle": "GET /api/v1/auditoria sin auditoria.ver",
    "exitoso": false
  }
]
```

## Servicio reportes · puerto 5123

### REP-01 · Catálogo de reportes · PASA

**Objetivo.** Cuatro familias y los filtros que admite cada uno.

**Petición.** `GET http://reportes:5123/api/v1/reportes`

```http
Accept: application/json
X-Traza-Id: ddcbf6ba-3050-4d93-bc05-5b167e55630f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 11 ms · traza `ddcbf6ba-3050-4d93-bc05-5b167e55630f`

```json
{
  "datos": [
    {
      "clave": "********",
      "familia": "operativo",
      "titulo": "Pedidos por día",
      "descripcion": "Pedidos, unidades, venta, ticket promedio y demanda no atendida de cada día, sin pedidos cancelados.",
      "filtros": [
        "desde",
        "hasta",
        "zona_id",
        "microhub_id"
      ]
    },
    {
      "clave": "********",
      "familia": "operativo",
      "titulo": "Pedidos por zona",
      "descripcion": "Lo mismo agrupado por zona, con el porcentaje de demanda que no se pudo atender.",
      "filtros": [
        "desde",
        "hasta",
        "zona_id",
        "microhub_id"
      ]
    },
    {
      "clave": "********",
      "familia": "logistico",
      "titulo": "Alertas de inventario",
      "descripcion": "Productos agotados o por debajo de su mínimo en cada microhub y cuántas unidades faltan.",
      "filtros": [
        "microhub_id"
      ]
    },
    {
      "clave": "********",
      "familia": "logistico",
      "titulo": "Quiebres de inventario",
      "descripcion": "Veces que una salida dejó un producto en cero dentro del periodo.",
      "filtros": [
        "desde",
        "hasta",
        "microhub_id"
      ]
    },
    {
      "clave": "********",
      "familia": "logistico",
      "titulo": "Carga de repartidores",
      "descripcion": "Repartidores activos y entregas que tienen abiertas hoy.",
      "filtros": []
    },
    {
      "clave": "********",
      "familia": "comercial",
      "titulo": "Ventas por producto",
      "descripcion": "Unidades, venta y participación de cada producto en el periodo.",
      "filtros": [
        "desde",
        "hasta",
        "microhub_id"
      ]
    },
    {
      "clave": "********",
      "familia": "comercial",
      "titulo": "Comparación entre microhubs",
      "descripcion": "Pedidos, venta, ticket y participación de cada microhub, lado a lado.",
      "filtros": [
        "desde",
        "hasta",
        "zona_id",
        "microhub_id"
      ]
    },
    {
      "clave": "********",
      "familia": "financiero",
      "titulo": "Punto de equilibrio por microhub",
      "descripcion": "Costos fijos, equilibrio, demanda esperada, utilidad y decisión de cada microhub.",
      "filtros": [
        "microhub_id"
      ]
    }
  ]
}
```

### REP-02 · Indicadores del periodo · PASA

**Objetivo.** Pedidos, venta, ticket, alertas, repartidores y microhubs no viables.

**Petición.** `GET http://reportes:5123/api/v1/reportes/indicadores?desde=2026-08-28`

```http
Accept: application/json
X-Traza-Id: 30c869ab-72dc-4bf8-bd67-a14e5b9e436d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 856 ms · traza `30c869ab-72dc-4bf8-bd67-a14e5b9e436d`

```json
{
  "desde": "2026-08-28",
  "hasta": "2026-11-26",
  "indicadores": [
    {
      "clave": "********",
      "titulo": "Pedidos del periodo",
      "valor": 339,
      "unidad": "pedidos",
      "fuente": "pedidos"
    },
    {
      "clave": "********",
      "titulo": "Venta del periodo",
      "valor": 50192.1,
      "unidad": "MXN",
      "fuente": "pedidos"
    },
    {
      "clave": "********",
      "titulo": "Ticket promedio",
      "valor": 148.06,
      "unidad": "MXN",
      "fuente": "pedidos"
    },
    {
      "clave": "********",
      "titulo": "Demanda no atendida",
      "valor": 50,
      "unidad": "pedidos",
      "fuente": "pedidos"
    },
    {
      "clave": "********",
      "titulo": "Productos en alerta de inventario",
      "valor": 8,
      "unidad": "productos",
      "fuente": "inventario"
    },
    {
      "clave": "********",
      "titulo": "Repartidores activos",
      "valor": 2,
      "unidad": "personas",
      "fuente": "entregas"
    },
    {
      "clave": "********",
      "titulo": "Entregas abiertas hoy",
      "valor": 0,
      "unidad": "entregas",
      "fuente": "entregas"
    },
    {
      "clave": "********",
      "titulo": "Microhubs que no alcanzan su equilibrio",
      "valor": 3,
      "unidad": "microhubs",
      "fuente": "punto-equilibrio"
    }
  ],
  "fuentes_no_disponibles": []
}
```

**Explicación.** Cada cifra la entrega el servicio dueño; si uno no responde, solo falta su indicador.

### REP-03 · Comparación entre microhubs · PASA

**Objetivo.** Pedidos, venta y participación de cada microhub.

**Petición.** `GET http://reportes:5123/api/v1/reportes/comparacion_microhubs?desde=2026-08-28`

```http
Accept: application/json
X-Traza-Id: 4bd9b036-7eb9-4a4e-a369-eca59ada6b03
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 484 ms · traza `4bd9b036-7eb9-4a4e-a369-eca59ada6b03`

```json
{
  "reporte": "comparacion_microhubs",
  "familia": "comercial",
  "titulo": "Comparación entre microhubs",
  "generado_en": "2026-11-26T14:20:18-06:00",
  "filtros": {
    "desde": "2026-08-28",
    "hasta": "2026-11-26",
    "zona_id": null,
    "microhub_id": null
  },
  "columnas": [
    {
      "clave": "********",
      "titulo": "Microhub",
      "tipo": "texto"
    },
    {
      "clave": "********",
      "titulo": "Pedidos",
      "tipo": "entero"
    },
    {
      "clave": "********",
      "titulo": "Unidades",
      "tipo": "entero"
    },
    {
      "clave": "********",
      "titulo": "Venta",
      "tipo": "dinero"
    },
    {
      "clave": "********",
      "titulo": "Ticket promedio",
      "tipo": "dinero"
    },
    {
      "clave": "********",
      "titulo": "Participación en la venta (%)",
      "tipo": "porcentaje"
    }
  ],
  "filas": [
    {
      "celdas": [
        "Microhub Valles",
        "126",
        "618",
        "19260.90",
        "152.86",
        "46.44"
      ]
    },
    {
      "celdas": [
        "Microhub San Bernabé Centro",
        "86",
        "412",
        "12167.10",
        "141.48",
        "29.34"
      ]
    },
    {
      "celdas": [
        "Microhub Poniente F-113",
        "65",
        "335",
        "10046.70",
        "154.56",
        "24.22"
      ]
    },
    {
      "celdas": [
        "Microhub Piloto Alianza",
        "0",
        "0",
        "0.00",
        "",
        "0.00"
      ]
    }
  ],
  "totales": {
    "celdas": [
      "Total",
      "277",
      "1365",
      "41474.70",
      "149.73",
      "100.00"
    ]
  },
  "total_filas": 4
}
```

**Evidencia en PostgreSQL.** `SELECT m.nombre, count(*) AS pedidos, round(sum(p.subtotal), 2) AS venta FROM pedido p JOIN microhub m ON m.id = p.microhub_id WHERE p.estado <> 'cancelado' AND p.creado_en > now() - interval '90 days' GROUP BY m.nombre ORDER BY venta DESC`

```json
[
  {
    "nombre": "Microhub Valles",
    "pedidos": 126,
    "venta": "19260.90"
  },
  {
    "nombre": "Microhub San Bernabé Centro",
    "pedidos": 86,
    "venta": "12167.10"
  },
  {
    "nombre": "Microhub Poniente F-113",
    "pedidos": 65,
    "venta": "10046.70"
  }
]
```

### REP-04 · Reporte en XML · PASA

**Objetivo.** El reporte financiero validado contra reportes.xsd.

**Petición.** `GET http://reportes:5123/api/v1/reportes/equilibrio_microhubs`

```http
Accept: application/xml
X-Traza-Id: 7098488e-f5e4-4739-8bf8-d6a70da4b627
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 470 ms · traza `7098488e-f5e4-4739-8bf8-d6a70da4b627`

```xml
<?xml version='1.0' encoding='utf-8'?>
<reporte xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><reporte>equilibrio_microhubs</reporte><familia>financiero</familia><titulo>Punto de equilibrio por microhub</titulo><generado_en>2026-11-26T14:20:18-06:00</generado_en><filtros><desde>2026-10-28</desde><hasta>2026-11-26</hasta><zona_id xsi:nil="true" /><microhub_id xsi:nil="true" /></filtros><columnas><columna><clave>microhub</clave><titulo>Microhub</titulo><tipo>texto</tipo></columna><columna><clave>costos_fijos_mes</clave><titulo>Costos fijos del mes</titulo><tipo>dinero</tipo></columna><columna><clave>margen_pedido</clave><titulo>Margen por pedido</titulo><tipo>dinero</tipo></columna><columna><clave>equilibrio_diario</clave><titulo>Equilibrio (pedidos/día)</titulo><tipo>dinero</tipo></columna><columna><clave>pedidos_dia</clave><titulo>Pedidos/día esperados</titulo><tipo>dinero</tipo></columna><columna><clave>diferencia_pedidos_dia</clave><titulo>Diferencia (pedidos/día)</titulo><tipo>dinero</tipo></columna><columna><clave>utilidad_mes</clave><titulo>Utilidad del mes</titulo><tipo>dinero</tipo></columna><columna><clave>decision</clave><titulo>Decisión</titulo><tipo>texto</tipo></columna></columnas><filas><fila><celdas><celda>Microhub San Bernabé Centro</celda><celda>69500.00</celda><celda>5.14</celda><celda>450.50</celda><celda>23.60</celda><celda>-426.91</celda><celda>-65859.95</celda><celda>no_viable</celda></celdas></fila><fila><celdas><celda>Microhub Valles</celda><celda>66500.00</celda><celda>5.14</celda><celda>431.06</celda><celda>16.11</celda><celda>-414.95</celda><celda>-64014.68</celda><celda>no_viable</celda></celdas></fila><fila><celdas><celda>Microhub Poniente F-113</celda><celda>50000.00</celda><celda>5.14</celda><celda>324.10</celda><celda>9.79</celda><celda>-314.31</celda><celda>-48488.91</celda><celda>no_viable</celda></celdas></fila></filas><totales><celdas><celda>Total</celda><celda>186000.00</celda><celda /><celda /><celda /><celda /><celda>-178363.54</celda><celda /></celdas></totales><total_filas>3</total_filas></reporte>
```

### REP-05 · Datos para Highcharts · PASA

**Objetivo.** Categorías y series listas para graficar.

**Petición.** `GET http://reportes:5123/api/v1/reportes/pedidos_por_zona/grafica?desde=2026-08-28`

```http
Accept: application/json
X-Traza-Id: 6caeb9d0-2b14-40d6-bec0-80d0eaed3ad1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 259 ms · traza `6caeb9d0-2b14-40d6-bec0-80d0eaed3ad1`

```json
{
  "reporte": "pedidos_por_zona",
  "titulo": "Pedidos por zona",
  "tipo": "column",
  "unidad": "pedidos",
  "categorias": [
    "Valles de San Bernabé",
    "San Bernabé X (F-113)",
    "Paseo de San Bernabé",
    "San Bernabé Centro"
  ],
  "series": [
    {
      "nombre": "Pedidos",
      "datos": [
        129.0,
        70.0,
        67.0,
        73.0
      ]
    },
    {
      "nombre": "Demanda no atendida",
      "datos": [
        13.0,
        12.0,
        13.0,
        12.0
      ]
    }
  ]
}
```

### REP-06 · Exportar a CSV · PASA

**Objetivo.** Descarga con SHA-256 y registro en la bitácora de exportaciones.

**Petición.** `GET http://reportes:5123/api/v1/reportes/pedidos_por_zona/exportar?formato=csv&desde=2026-08-28`

```http
Accept: application/json
X-Traza-Id: fe6d0a08-3056-4843-ba08-e0645beaf3c3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 263 ms · traza `fe6d0a08-3056-4843-ba08-e0645beaf3c3`

```json
﻿Zona,Pedidos,Unidades,Venta,Ticket promedio,Demanda no atendida,No atendida (%)
Valles de San Bernabé,129,597,18633.90,144.45,13,9.15
San Bernabé X (F-113),70,356,10766.70,153.81,12,14.63
Paseo de San Bernabé,67,348,10672.90,159.30,13,16.25
San Bernabé Centro,73,360,10118.60,138.61,12,14.12
Total,339,1661,50192.10,148.06,50,12.85

```

**Explicación.** Excel (xlsx) y PDF usan la misma ruta con formato=xlsx|pdf. El archivo se genera al momento; no se guarda.

**Evidencia en PostgreSQL.** `SELECT reporte, formato, filas, bytes, left(sha256, 16) AS sha256, creado_por FROM reporte_exportacion ORDER BY id DESC LIMIT 1`

```json
[
  {
    "reporte": "pedidos_por_zona",
    "formato": "csv",
    "filas": 4,
    "bytes": 345,
    "sha256": "877796a5bdaf0bb1",
    "creado_por": 1
  }
]
```

### REP-07 · Bitácora de exportaciones · PASA

**Objetivo.** Quién exportó qué, con qué filtros.

**Petición.** `GET http://reportes:5123/api/v1/reportes/exportaciones?por_pagina=3`

```http
Accept: application/json
X-Traza-Id: de9edeaa-906d-46c4-8709-29ba2ff346cc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 47 ms · traza `de9edeaa-906d-46c4-8709-29ba2ff346cc`

```json
{
  "datos": [
    {
      "id": 69,
      "reporte": "pedidos_por_zona",
      "formato": "csv",
      "filtros": {
        "desde": "2026-08-28",
        "hasta": "2026-11-26",
        "zona_id": null,
        "microhub_id": null
      },
      "filas": 4,
      "bytes": 345,
      "sha256": "877796a5bdaf0bb1c46830be46149b1206d5107aba8089ee86f6e3051eece050",
      "creado_por": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "creado_en": "2026-11-26T14:20:19-06:00"
    },
    {
      "id": 68,
      "reporte": "pedidos_por_zona",
      "formato": "csv",
      "filtros": {
        "desde": "2026-08-28",
        "hasta": "2026-11-26",
        "zona_id": null,
        "microhub_id": null
      },
      "filas": 4,
      "bytes": 344,
      "sha256": "673765ea19071649ac68ffbc70f69ca5ab37668189331e718636832754430f55",
      "creado_por": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "creado_en": "2026-11-26T14:09:19-06:00"
    },
    {
      "id": 67,
      "reporte": "pedidos_por_zona",
      "formato": "csv",
      "filtros": {
        "desde": "2026-08-28",
        "hasta": "2026-11-26",
        "zona_id": null,
        "microhub_id": null
      },
      "filas": 4,
      "bytes": 344,
      "sha256": "85e7713249de90569a3822ab3081e4354455179af17ed53db0a9f34ec1607580",
      "creado_por": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "creado_en": "2026-11-26T13:52:17-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 3,
    "total": 69,
    "paginas": 23
  }
}
```

### REP-08 · Filtro que el reporte no admite · PASA

**Objetivo.** Se rechaza en lugar de ignorarse.

**Petición.** `GET http://reportes:5123/api/v1/reportes/carga_repartidores?zona_id=1`

```http
Accept: application/json
X-Traza-Id: dadf9143-844b-4f09-8cc1-6d63d5472d83
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 6 ms · traza `dadf9143-844b-4f09-8cc1-6d63d5472d83`

```json
{
  "error": {
    "codigo": "FILTRO_INVALIDO",
    "mensaje": "Este reporte no admite el filtro zona_id.",
    "detalles": [
      {
        "campo": "zona_id",
        "mensaje": "Este reporte no admite el filtro zona_id."
      }
    ],
    "traza_id": "dadf9143-844b-4f09-8cc1-6d63d5472d83"
  }
}
```

### REP-09 · El cliente no ve reportes · PASA

**Objetivo.** Sin reportes.ver.

**Petición.** `GET http://reportes:5123/api/v1/reportes`

```http
Accept: application/json
X-Traza-Id: ae1c778c-3aa3-4b8b-925c-43d1aade5aec
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 51 ms · traza `ae1c778c-3aa3-4b8b-925c-43d1aade5aec`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "ae1c778c-3aa3-4b8b-925c-43d1aade5aec"
  }
}
```

## Servicio sincronizacion · puerto 5125

### SYN-01 · Enviar lo hecho sin conexión · PASA

**Objetivo.** La app manda el cierre y el recorrido; se aplican en el orden en que ocurrieron.

**Petición.** `POST http://sincronizacion:5125/api/v1/sincronizacion/lotes`

```http
Accept: application/json
X-Traza-Id: 5f730294-190e-4e34-8979-cbfad792d5ec
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "bed93d32-05f1-497c-9cb1-7d1298fa6c4b",
  "dispositivo": "android-evidencia-64d972",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "508aa577-0432-47b9-8213-a071200fd9ea",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-26T20:17:19.770076+00:00",
      "datos": {
        "entrega_id": 279,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "Cliente ausente",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b08948314ec03b218378d44"
        ],
        "capturado_en": "2026-11-26T20:17:19.770019+00:00"
      }
    },
    {
      "operacion_uuid": "d460d53b-e328-4ca4-8e8e-4ae07982c386",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-26T20:08:19.770104+00:00",
      "datos": {
        "entrega_id": 279,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-26T20:08:19.770111+00:00"
          }
        ]
      }
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 383 ms · traza `5f730294-190e-4e34-8979-cbfad792d5ec`

```json
{
  "id": 157,
  "lote_uuid": "bed93d32-05f1-497c-9cb1-7d1298fa6c4b",
  "dispositivo": "android-evidencia-64d972",
  "recibido_en": "2026-11-26T14:20:19-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 0,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "508aa577-0432-47b9-8213-a071200fd9ea",
      "tipo": "entrega_resultado",
      "estado": "aplicada",
      "duplicada": false,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "d460d53b-e328-4ca4-8e8e-4ae07982c386",
      "tipo": "ubicaciones",
      "estado": "aplicada",
      "duplicada": false,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    }
  ]
}
```

**Explicación.** Cada operación llama al servicio dueño con el JWT del repartidor.

**Evidencia en PostgreSQL.** `SELECT e.id, e.resultado, e.id_cliente_local, p.estado FROM entrega e JOIN pedido p ON p.id = e.pedido_id WHERE e.id = %s`

```json
[
  {
    "id": 279,
    "resultado": "fallida",
    "id_cliente_local": "508aa577-0432-47b9-8213-a071200fd9ea",
    "estado": "entrega_fallida"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT operacion_uuid, tipo, estado, intentos FROM sync_operacion WHERE dispositivo = %s ORDER BY creada_en`

```json
[
  {
    "operacion_uuid": "d460d53b-e328-4ca4-8e8e-4ae07982c386",
    "tipo": "ubicaciones",
    "estado": "aplicada",
    "intentos": 1
  },
  {
    "operacion_uuid": "508aa577-0432-47b9-8213-a071200fd9ea",
    "tipo": "entrega_resultado",
    "estado": "aplicada",
    "intentos": 1
  }
]
```

### SYN-02 · Reenviar el mismo lote · PASA

**Objetivo.** Idempotencia: nada se repite.

**Petición.** `POST http://sincronizacion:5125/api/v1/sincronizacion/lotes`

```http
Accept: application/json
X-Traza-Id: d297bbf1-8c54-40ed-989a-d240788dab81
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "bed93d32-05f1-497c-9cb1-7d1298fa6c4b",
  "dispositivo": "android-evidencia-64d972",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "508aa577-0432-47b9-8213-a071200fd9ea",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-26T20:17:19.770076+00:00",
      "datos": {
        "entrega_id": 279,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "Cliente ausente",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b08948314ec03b218378d44"
        ],
        "capturado_en": "2026-11-26T20:17:19.770019+00:00"
      }
    },
    {
      "operacion_uuid": "d460d53b-e328-4ca4-8e8e-4ae07982c386",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-26T20:08:19.770104+00:00",
      "datos": {
        "entrega_id": 279,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-26T20:08:19.770111+00:00"
          }
        ]
      }
    }
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 198 ms · traza `d297bbf1-8c54-40ed-989a-d240788dab81`

```json
{
  "id": 157,
  "lote_uuid": "bed93d32-05f1-497c-9cb1-7d1298fa6c4b",
  "dispositivo": "android-evidencia-64d972",
  "recibido_en": "2026-11-26T14:20:19-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 2,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "508aa577-0432-47b9-8213-a071200fd9ea",
      "tipo": "entrega_resultado",
      "estado": "aplicada",
      "duplicada": true,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "d460d53b-e328-4ca4-8e8e-4ae07982c386",
      "tipo": "ubicaciones",
      "estado": "aplicada",
      "duplicada": true,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    }
  ]
}
```

### SYN-03 · Conflicto: la entrega ya estaba cerrada · PASA

**Objetivo.** Gana el servidor y queda para revisión.

**Petición.** `POST http://sincronizacion:5125/api/v1/sincronizacion/lotes`

```http
Accept: application/json
X-Traza-Id: 133acaa9-d3f1-4f4f-97b9-6e14ceac3fcc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "fb34ccaf-d8a2-4def-b2d3-40bd09912549",
  "dispositivo": "android-evidencia-64d972",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "f40d3251-63df-42d2-9cfe-fca1e4bab661",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-26T20:19:20.398515+00:00",
      "datos": {
        "entrega_id": 279,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "Cliente ausente",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b08948314ec03b218378d44"
        ],
        "capturado_en": "2026-11-26T20:17:19.770019+00:00"
      }
    }
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 311 ms · traza `133acaa9-d3f1-4f4f-97b9-6e14ceac3fcc`

```json
{
  "id": 158,
  "lote_uuid": "fb34ccaf-d8a2-4def-b2d3-40bd09912549",
  "dispositivo": "android-evidencia-64d972",
  "recibido_en": "2026-11-26T14:20:20-06:00",
  "total": 1,
  "aplicadas": 0,
  "duplicadas": 0,
  "conflictos": 1,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "f40d3251-63df-42d2-9cfe-fca1e4bab661",
      "tipo": "entrega_resultado",
      "estado": "conflicto",
      "duplicada": false,
      "http_status": 409,
      "codigo": "CONFLICTO",
      "mensaje": "La entrega ya se cerró con otra operación.",
      "reintentar": false
    }
  ]
}
```

### SYN-04 · Conflictos por revisar · PASA

**Objetivo.** Los ve quien tiene sincronizacion.ver.

**Petición.** `GET http://sincronizacion:5125/api/v1/sincronizacion/conflictos?por_pagina=3`

```http
Accept: application/json
X-Traza-Id: 59414f0a-2420-4d20-9b5a-7fabe8c14e3c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 67 ms · traza `59414f0a-2420-4d20-9b5a-7fabe8c14e3c`

```json
{
  "datos": [
    {
      "id": 170,
      "lote_uuid": "fb34ccaf-d8a2-4def-b2d3-40bd09912549",
      "dispositivo": "android-evidencia-64d972",
      "operacion_uuid": "f40d3251-63df-42d2-9cfe-fca1e4bab661",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-26T14:19:20-06:00",
      "estado": "conflicto",
      "http_status": 409,
      "codigo": "CONFLICTO",
      "mensaje": "La entrega ya se cerró con otra operación.",
      "intentos": 1,
      "procesada_en": "2026-11-26T14:20:20-06:00",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      }
    },
    {
      "id": 167,
      "lote_uuid": "d39c7f6f-3da2-4840-90e1-46574f6fe996",
      "dispositivo": "android-evidencia-034da2",
      "operacion_uuid": "099d8cdf-9a9f-4a99-9b73-563ebb36c625",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-26T14:08:21-06:00",
      "estado": "conflicto",
      "http_status": 409,
      "codigo": "CONFLICTO",
      "mensaje": "La entrega ya se cerró con otra operación.",
      "intentos": 1,
      "procesada_en": "2026-11-26T14:09:21-06:00",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      }
    },
    {
      "id": 164,
      "lote_uuid": "ecac77bc-d507-43c9-b884-1670eed0044a",
      "dispositivo": "android-evidencia-80a876",
      "operacion_uuid": "2a0d1376-77f0-4977-ac63-1ad07ef6aa82",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-26T13:51:18-06:00",
      "estado": "conflicto",
      "http_status": 409,
      "codigo": "CONFLICTO",
      "mensaje": "La entrega ya se cerró con otra operación.",
      "intentos": 1,
      "procesada_en": "2026-11-26T13:52:18-06:00",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      }
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 3,
    "total": 11,
    "paginas": 4
  }
}
```

### SYN-05 · Mis lotes · PASA

**Objetivo.** El repartidor ve solo los suyos.

**Petición.** `GET http://sincronizacion:5125/api/v1/sincronizacion/lotes?por_pagina=3`

```http
Accept: application/json
X-Traza-Id: 19480e49-9586-49ef-bcde-4d1103aaa60e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 53 ms · traza `19480e49-9586-49ef-bcde-4d1103aaa60e`

```json
{
  "datos": [
    {
      "id": 158,
      "lote_uuid": "fb34ccaf-d8a2-4def-b2d3-40bd09912549",
      "dispositivo": "android-evidencia-64d972",
      "cliente": "android",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "recibido_en": "2026-11-26T14:20:20-06:00",
      "total": 1,
      "aplicadas": 0,
      "duplicadas": 0,
      "conflictos": 1,
      "rechazadas": 0,
      "pendientes": 0
    },
    {
      "id": 157,
      "lote_uuid": "bed93d32-05f1-497c-9cb1-7d1298fa6c4b",
      "dispositivo": "android-evidencia-64d972",
      "cliente": "android",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "recibido_en": "2026-11-26T14:20:19-06:00",
      "total": 2,
      "aplicadas": 2,
      "duplicadas": 2,
      "conflictos": 0,
      "rechazadas": 0,
      "pendientes": 0
    },
    {
      "id": 156,
      "lote_uuid": "d39c7f6f-3da2-4840-90e1-46574f6fe996",
      "dispositivo": "android-evidencia-034da2",
      "cliente": "android",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "recibido_en": "2026-11-26T14:09:21-06:00",
      "total": 1,
      "aplicadas": 0,
      "duplicadas": 0,
      "conflictos": 1,
      "rechazadas": 0,
      "pendientes": 0
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 3,
    "total": 134,
    "paginas": 45
  }
}
```

### SYN-06 · Un lote con sus operaciones · PASA

**Objetivo.** Cada operación con su resultado.

**Petición.** `GET http://sincronizacion:5125/api/v1/sincronizacion/lotes/157`

```http
Accept: application/json
X-Traza-Id: ef884e17-97fe-428a-aea8-6e032852823e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 66 ms · traza `ef884e17-97fe-428a-aea8-6e032852823e`

```json
{
  "id": 157,
  "lote_uuid": "bed93d32-05f1-497c-9cb1-7d1298fa6c4b",
  "dispositivo": "android-evidencia-64d972",
  "cliente": "android",
  "usuario": {
    "id": 7,
    "nombre": "Ramiro Alanís Lozano"
  },
  "recibido_en": "2026-11-26T14:20:19-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 2,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "id": 168,
      "lote_uuid": "bed93d32-05f1-497c-9cb1-7d1298fa6c4b",
      "dispositivo": "android-evidencia-64d972",
      "operacion_uuid": "d460d53b-e328-4ca4-8e8e-4ae07982c386",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-26T14:08:19-06:00",
      "estado": "aplicada",
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "intentos": 1,
      "procesada_en": "2026-11-26T14:20:19-06:00",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      }
    },
    {
      "id": 169,
      "lote_uuid": "bed93d32-05f1-497c-9cb1-7d1298fa6c4b",
      "dispositivo": "android-evidencia-64d972",
      "operacion_uuid": "508aa577-0432-47b9-8213-a071200fd9ea",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-26T14:17:19-06:00",
      "estado": "aplicada",
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "intentos": 1,
      "procesada_en": "2026-11-26T14:20:20-06:00",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      }
    }
  ]
}
```

### SYN-07 · Pendientes por reintentar · PASA

**Objetivo.** Lo que no se pudo aplicar porque un servicio no respondió.

**Petición.** `GET http://sincronizacion:5125/api/v1/sincronizacion/pendientes`

```http
Accept: application/json
X-Traza-Id: 4c98f890-cc37-43ee-ae7a-2e05ca81ab87
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 63 ms · traza `4c98f890-cc37-43ee-ae7a-2e05ca81ab87`

```json
{
  "datos": [
    {
      "id": 29,
      "lote_uuid": "7616dbd6-28ea-4e71-abad-5e8600fd5dd2",
      "dispositivo": "android-reintento-ola3",
      "operacion_uuid": "6424e817-c67c-4de2-a5d5-3ed4851835f2",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-25T16:02:20-06:00",
      "estado": "pendiente",
      "http_status": null,
      "codigo": "SERVICIO_NO_DISPONIBLE",
      "mensaje": "El servicio entregas no responde. Intenta más tarde.",
      "intentos": 1,
      "procesada_en": "2026-11-25T16:05:20-06:00",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      }
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 1,
    "paginas": 1
  }
}
```

### SYN-08 · Estado del dispositivo · PASA

**Objetivo.** Última sincronización y pendientes.

**Petición.** `GET http://sincronizacion:5125/api/v1/sincronizacion/estado?dispositivo=android-evidencia-64d972`

```http
Accept: application/json
X-Traza-Id: 94b9c8c7-3d83-4cb0-bab1-2e7c85fe7fc1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 51 ms · traza `94b9c8c7-3d83-4cb0-bab1-2e7c85fe7fc1`

```json
{
  "dispositivo": "android-evidencia-64d972",
  "ultima_sincronizacion": "2026-11-26T14:20:20-06:00",
  "lotes": 2,
  "aplicadas": 2,
  "conflictos": 1,
  "rechazadas": 0,
  "pendientes": 0
}
```

### SYN-09 · Límites de la sincronización · PASA

**Objetivo.** Tamaño de lote, antigüedad y reloj.

**Petición.** `GET http://sincronizacion:5125/api/v1/sincronizacion/supuestos`

```http
Accept: application/json
X-Traza-Id: 0171c946-93c0-4699-bfe8-b5ed2bce222a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 32 ms · traza `0171c946-93c0-4699-bfe8-b5ed2bce222a`

```json
{
  "datos": [
    {
      "clave": "********",
      "valor": "14",
      "unidad": "días",
      "origen": "supuesto",
      "justificacion": "Un repartidor sin red por dos semanas ya no tiene datos vigentes: precios, inventario y pedidos habrán cambiado.",
      "como_calibrar": "Medir cuántos días pasan realmente sin conexión en la operación."
    },
    {
      "clave": "********",
      "valor": "200",
      "unidad": "operaciones",
      "origen": "supuesto",
      "justificacion": "Un lote de 200 operaciones cabe en una petición de menos de …(151 caracteres)",
      "como_calibrar": "Medir cuántas operaciones junta un repartidor en una jornada sin conexión y poner el límite al doble."
    },
    {
      "clave": "********",
      "valor": "10",
      "unidad": "minutos",
      "origen": "supuesto",
      "justificacion": "Los relojes de los teléfonos se desvían minutos; una operaci…(143 caracteres)",
      "como_calibrar": "Comparar la hora de creación de las operaciones con la hora de recepción."
    }
  ]
}
```

### SYN-10 · El cliente no sincroniza · PASA

**Objetivo.** Sin sincronizacion.usar.

**Petición.** `POST http://sincronizacion:5125/api/v1/sincronizacion/lotes`

```http
Accept: application/json
X-Traza-Id: bb89c063-904a-4baf-8bc9-9c912fdabe1a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "bed93d32-05f1-497c-9cb1-7d1298fa6c4b",
  "dispositivo": "android-evidencia-64d972",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "508aa577-0432-47b9-8213-a071200fd9ea",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-26T20:17:19.770076+00:00",
      "datos": {
        "entrega_id": 279,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "Cliente ausente",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b08948314ec03b218378d44"
        ],
        "capturado_en": "2026-11-26T20:17:19.770019+00:00"
      }
    },
    {
      "operacion_uuid": "d460d53b-e328-4ca4-8e8e-4ae07982c386",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-26T20:08:19.770104+00:00",
      "datos": {
        "entrega_id": 279,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-26T20:08:19.770111+00:00"
          }
        ]
      }
    }
  ]
}
```

**Respuesta.** HTTP 403 (esperado 403) · 56 ms · traza `bb89c063-904a-4baf-8bc9-9c912fdabe1a`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "bb89c063-904a-4baf-8bc9-9c912fdabe1a"
  }
}
```

### SYN-11 · Lote mal formado · PASA

**Objetivo.** operaciones debe ser una lista.

**Petición.** `POST http://sincronizacion:5125/api/v1/sincronizacion/lotes`

```http
Accept: application/json
X-Traza-Id: fd04242f-c70b-488c-941c-65260623aa1f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "bed93d32-05f1-497c-9cb1-7d1298fa6c4b",
  "dispositivo": "android-evidencia-64d972",
  "cliente": "android",
  "operaciones": "x"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 29 ms · traza `fd04242f-c70b-488c-941c-65260623aa1f`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "operaciones",
        "mensaje": "operaciones debe ser una lista."
      }
    ],
    "traza_id": "fd04242f-c70b-488c-941c-65260623aa1f"
  }
}
```

### SYN-12 · Estado en XML · PASA

**Objetivo.** Validado contra sincronizacion.xsd.

**Petición.** `GET http://sincronizacion:5125/api/v1/sincronizacion/estado?dispositivo=android-evidencia-64d972`

```http
Accept: application/xml
X-Traza-Id: e894b4f8-9e16-4337-8b27-5de1e426311c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 51 ms · traza `e894b4f8-9e16-4337-8b27-5de1e426311c`

```xml
<?xml version='1.0' encoding='utf-8'?>
<sync_estado xmlns="urn:microhubs:v1" version="1"><dispositivo>android-evidencia-64d972</dispositivo><ultima_sincronizacion>2026-11-26T14:20:20-06:00</ultima_sincronizacion><lotes>2</lotes><aplicadas>2</aplicadas><conflictos>1</conflictos><rechazadas>0</rechazadas><pendientes>0</pendientes></sync_estado>
```

## Servicio auth · puerto 5101

### SAL-AUT · Salud de auth · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://auth:5101/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 8ef298b5-16a6-4ff3-b07e-b49e03d20178
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `8ef298b5-16a6-4ff3-b07e-b49e03d20178`

```json
{
  "servicio": "auth",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica",
    "bucket": "no_aplica"
  },
  "tiempo_ms": 13.9
}
```

## Servicio usuarios · puerto 5102

### SAL-USU · Salud de usuarios · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://usuarios:5102/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 4a5d290a-80d1-4712-b348-fe217fa6b1f5
```

**Respuesta.** HTTP 200 (esperado 200) · 19 ms · traza `4a5d290a-80d1-4712-b348-fe217fa6b1f5`

```json
{
  "servicio": "usuarios",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica",
    "bucket": "no_aplica"
  },
  "tiempo_ms": 15.5
}
```

## Servicio productos · puerto 5103

### SAL-PRO · Salud de productos · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://productos:5103/api/v1/health`

```http
Accept: application/json
X-Traza-Id: d483b5b6-9ac1-4a00-ad98-020e455b5a9e
```

**Respuesta.** HTTP 200 (esperado 200) · 20 ms · traza `d483b5b6-9ac1-4a00-ad98-020e455b5a9e`

```json
{
  "servicio": "productos",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica",
    "bucket": "no_aplica"
  },
  "tiempo_ms": 16.1
}
```

## Servicio pedidos · puerto 5104

### SAL-PED · Salud de pedidos · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://pedidos:5104/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 67e80480-6575-45e7-a8ed-23eff555755d
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `67e80480-6575-45e7-a8ed-23eff555755d`

```json
{
  "servicio": "pedidos",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica",
    "bucket": "no_aplica"
  },
  "tiempo_ms": 14.0
}
```

## Servicio entregas · puerto 5105

### SAL-ENT · Salud de entregas · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://entregas:5105/api/v1/health`

```http
Accept: application/json
X-Traza-Id: aab8bbb0-0daa-46d4-a4b4-da4d0bfa4da2
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `aab8bbb0-0daa-46d4-a4b4-da4d0bfa4da2`

```json
{
  "servicio": "entregas",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "ok",
    "bucket": "no_aplica"
  },
  "tiempo_ms": 13.8
}
```

## Servicio planeacion · puerto 5106

### SAL-PLA · Salud de planeacion · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://planeacion:5106/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 30de5c38-84ef-4d06-9aa2-1d1f5391a3e7
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `30de5c38-84ef-4d06-9aa2-1d1f5391a3e7`

```json
{
  "servicio": "planeacion",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "ok",
    "bucket": "no_aplica"
  },
  "tiempo_ms": 14.1
}
```

## Servicio documentos · puerto 5107

### SAL-DOC · Salud de documentos · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://documentos:5107/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 55a09a44-b2bd-4cc6-81d8-14a1b19b98d7
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `55a09a44-b2bd-4cc6-81d8-14a1b19b98d7`

```json
{
  "servicio": "documentos",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "ok",
    "bucket": "ok"
  },
  "tiempo_ms": 14.8
}
```

## Servicio zonas · puerto 5108

### SAL-ZON · Salud de zonas · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://zonas:5108/api/v1/health`

```http
Accept: application/json
X-Traza-Id: bf184612-0204-47f3-8a1e-546fc745e44b
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `bf184612-0204-47f3-8a1e-546fc745e44b`

```json
{
  "servicio": "zonas",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica",
    "bucket": "no_aplica"
  },
  "tiempo_ms": 13.4
}
```

## Servicio microhubs · puerto 5109

### SAL-MIC · Salud de microhubs · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://microhubs:5109/api/v1/health`

```http
Accept: application/json
X-Traza-Id: df796803-55a2-4429-a40e-6db96a974d9f
```

**Respuesta.** HTTP 200 (esperado 200) · 15 ms · traza `df796803-55a2-4429-a40e-6db96a974d9f`

```json
{
  "servicio": "microhubs",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica",
    "bucket": "no_aplica"
  },
  "tiempo_ms": 12.7
}
```

## Servicio seguimiento · puerto 5110

### SAL-SEG · Salud de seguimiento · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://seguimiento:5110/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 016bec28-f5d1-46ad-a52f-9bc9a355a320
```

**Respuesta.** HTTP 200 (esperado 200) · 18 ms · traza `016bec28-f5d1-46ad-a52f-9bc9a355a320`

```json
{
  "servicio": "seguimiento",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "ok",
    "bucket": "no_aplica"
  },
  "tiempo_ms": 15.3
}
```

## Servicio inventario · puerto 5111

### SAL-INV · Salud de inventario · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://inventario:5111/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 5a7b5cb5-c62a-4548-9226-4214c1f88214
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `5a7b5cb5-c62a-4548-9226-4214c1f88214`

```json
{
  "servicio": "inventario",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica",
    "bucket": "no_aplica"
  },
  "tiempo_ms": 13.0
}
```

## Servicio precios · puerto 5112

### SAL-PRE · Salud de precios · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://precios:5112/api/v1/health`

```http
Accept: application/json
X-Traza-Id: aaded433-5b5d-45b8-9005-e7a9d4ff1566
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `aaded433-5b5d-45b8-9005-e7a9d4ff1566`

```json
{
  "servicio": "precios",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica",
    "bucket": "no_aplica"
  },
  "tiempo_ms": 13.8
}
```

## Servicio proveedores · puerto 5113

### SAL-PRO · Salud de proveedores · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://proveedores:5113/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 97a6775a-f00f-4358-a76f-6d14b8958583
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `97a6775a-f00f-4358-a76f-6d14b8958583`

```json
{
  "servicio": "proveedores",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica",
    "bucket": "no_aplica"
  },
  "tiempo_ms": 14.0
}
```

## Servicio abastecimiento · puerto 5114

### SAL-ABA · Salud de abastecimiento · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://abastecimiento:5114/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 0d87b69d-470f-4062-8632-3e0d677d1f0b
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `0d87b69d-470f-4062-8632-3e0d677d1f0b`

```json
{
  "servicio": "abastecimiento",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica",
    "bucket": "no_aplica"
  },
  "tiempo_ms": 14.0
}
```

## Servicio demanda · puerto 5115

### SAL-DEM · Salud de demanda · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://demanda:5115/api/v1/health`

```http
Accept: application/json
X-Traza-Id: d00080e1-1b9e-428b-9fb9-4ba6a390e42d
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `d00080e1-1b9e-428b-9fb9-4ba6a390e42d`

```json
{
  "servicio": "demanda",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica",
    "bucket": "no_aplica"
  },
  "tiempo_ms": 14.0
}
```

## Servicio cobertura · puerto 5116

### SAL-COB · Salud de cobertura · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://cobertura:5116/api/v1/health`

```http
Accept: application/json
X-Traza-Id: e443bd6b-c64c-45b6-a7bd-4cf8411cd769
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `e443bd6b-c64c-45b6-a7bd-4cf8411cd769`

```json
{
  "servicio": "cobertura",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica",
    "bucket": "no_aplica"
  },
  "tiempo_ms": 13.9
}
```

## Servicio capacidad · puerto 5117

### SAL-CAP · Salud de capacidad · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://capacidad:5117/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 5da0a760-0127-40f7-9c00-66ec23f205fa
```

**Respuesta.** HTTP 200 (esperado 200) · 15 ms · traza `5da0a760-0127-40f7-9c00-66ec23f205fa`

```json
{
  "servicio": "capacidad",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica",
    "bucket": "no_aplica"
  },
  "tiempo_ms": 13.2
}
```

## Servicio rutas · puerto 5118

### SAL-RUT · Salud de rutas · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://rutas:5118/api/v1/health`

```http
Accept: application/json
X-Traza-Id: ba51915b-a1e1-45ae-8fc2-77065e0492f8
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `ba51915b-a1e1-45ae-8fc2-77065e0492f8`

```json
{
  "servicio": "rutas",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica",
    "bucket": "no_aplica"
  },
  "tiempo_ms": 13.5
}
```

## Servicio costos · puerto 5119

### SAL-COS · Salud de costos · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://costos:5119/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 79f1d1da-ffb3-4397-b2a7-b5418a61c501
```

**Respuesta.** HTTP 200 (esperado 200) · 15 ms · traza `79f1d1da-ffb3-4397-b2a7-b5418a61c501`

```json
{
  "servicio": "costos",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica",
    "bucket": "no_aplica"
  },
  "tiempo_ms": 13.1
}
```

## Servicio punto-equilibrio · puerto 5120

### SAL-PUN · Salud de punto-equilibrio · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://punto-equilibrio:5120/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 380fbbee-ec12-4b84-9f26-0891ed912b2b
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `380fbbee-ec12-4b84-9f26-0891ed912b2b`

```json
{
  "servicio": "punto-equilibrio",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica",
    "bucket": "no_aplica"
  },
  "tiempo_ms": 13.8
}
```

## Servicio simulacion · puerto 5121

### SAL-SIM · Salud de simulacion · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://simulacion:5121/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 991877cf-86ad-45ff-ba6d-6731901eea3b
```

**Respuesta.** HTTP 200 (esperado 200) · 15 ms · traza `991877cf-86ad-45ff-ba6d-6731901eea3b`

```json
{
  "servicio": "simulacion",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica",
    "bucket": "no_aplica"
  },
  "tiempo_ms": 12.3
}
```

## Servicio surtido · puerto 5122

### SAL-SUR · Salud de surtido · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://surtido:5122/api/v1/health`

```http
Accept: application/json
X-Traza-Id: a33b5b45-7ac4-458f-867f-44defe8e5095
```

**Respuesta.** HTTP 200 (esperado 200) · 15 ms · traza `a33b5b45-7ac4-458f-867f-44defe8e5095`

```json
{
  "servicio": "surtido",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica",
    "bucket": "no_aplica"
  },
  "tiempo_ms": 13.2
}
```

## Servicio notificaciones · puerto 5124

### SAL-NOT · Salud de notificaciones · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://notificaciones:5124/api/v1/health`

```http
Accept: application/json
X-Traza-Id: bb0dcfc4-8dea-4260-9b9a-10f9b5eea534
```

**Respuesta.** HTTP 200 (esperado 200) · 15 ms · traza `bb0dcfc4-8dea-4260-9b9a-10f9b5eea534`

```json
{
  "servicio": "notificaciones",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica",
    "bucket": "no_aplica"
  },
  "tiempo_ms": 12.9
}
```

## Servicio reportes · puerto 5123

### SAL-REP · Salud de reportes · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://reportes:5123/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 9cad32ca-4095-4a9d-abaa-42d0270f9114
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `9cad32ca-4095-4a9d-abaa-42d0270f9114`

```json
{
  "servicio": "reportes",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica",
    "bucket": "no_aplica"
  },
  "tiempo_ms": 13.8
}
```

## Servicio sincronizacion · puerto 5125

### SAL-SIN · Salud de sincronizacion · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://sincronizacion:5125/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 6702a575-26f1-4368-b4fc-8151a548882c
```

**Respuesta.** HTTP 200 (esperado 200) · 15 ms · traza `6702a575-26f1-4368-b4fc-8151a548882c`

```json
{
  "servicio": "sincronizacion",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica",
    "bucket": "no_aplica"
  },
  "tiempo_ms": 12.7
}
```

## Servicio auditoria-monitoreo · puerto 5126

### SAL-AUD · Salud de auditoria-monitoreo · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/health`

```http
Accept: application/json
X-Traza-Id: ad46a175-1919-4ef0-847d-939e242d10df
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `ad46a175-1919-4ef0-847d-939e242d10df`

```json
{
  "servicio": "auditoria-monitoreo",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "ok",
    "bucket": "no_aplica"
  },
  "tiempo_ms": 15.0
}
```

## Servicio auth · puerto 5101

### MON-01 · Registro de actividad · PASA

**Objetivo.** Cada petición queda en MongoDB con su traza.

**Petición.** `GET http://auth:5101/api/v1/auth/validar`

```http
Accept: application/json
X-Traza-Id: 55587f87-9313-4662-bd25-07c906a10500
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 5 ms · traza `55587f87-9313-4662-bd25-07c906a10500`

```json
{
  "valido": true,
  "expira_en": 848,
  "usuario": {
    "id": 1,
    "rol": "administrador",
    "microhub_id": null
  }
}
```

**Explicación.** El X-Traza-Id de la petición se recupera en logs_tecnicos.correlacion_id.

**Evidencia en MongoDB.** `db.logs_tecnicos.findOne({correlacion_id: '55587f87-9313-4662-bd25-07c906a10500'})`

```json
{
  "nivel": "INFO",
  "componente": "auth",
  "registrado_en": "2026-11-26 20:20:21.632000+00:00",
  "correlacion_id": "55587f87-9313-4662-bd25-07c906a10500",
  "mensaje": "GET /api/v1/auth/validar -> 200",
  "usuario_id": 1,
  "ruta": "/api/v1/auth/validar",
  "duracion_ms": 1,
  "contexto": {
    "metodo": "GET",
    "status": 200,
    "formato": "json",
    "codigo_error": null
  },
  "excepcion": null
}
```

**Evidencia en MongoDB.** `db.metricas_servicio.aggregate([{$group:{_id:'$etiquetas.servicio', peticiones:{$sum:1}, ms_promedio:{$avg:'$duracion_ms'}}}])`

```json
[
  {
    "_id": "abastecimiento",
    "peticiones": 617,
    "ms_promedio": 107.17341977309563
  },
  {
    "_id": "auditoria-monitoreo",
    "peticiones": 2110,
    "ms_promedio": 54.1085308056872
  },
  {
    "_id": "auth",
    "peticiones": 2159,
    "ms_promedio": 270.06855025474755
  },
  {
    "_id": "capacidad",
    "peticiones": 859,
    "ms_promedio": 61.07450523864959
  },
  {
    "_id": "cobertura",
    "peticiones": 1407,
    "ms_promedio": 51.3134328358209
  },
  {
    "_id": "costos",
    "peticiones": 1665,
    "ms_promedio": 44.65345345345345
  },
  {
    "_id": "demanda",
    "peticiones": 1559,
    "ms_promedio": 101.08017960230917
  },
  {
    "_id": "documentos",
    "peticiones": 371,
    "ms_promedio": 28.22911051212938
  },
  {
    "_id": "entregas",
    "peticiones": 819,
    "ms_promedio": 76.47741147741148
  },
  {
    "_id": "inventario",
    "peticiones": 1638,
    "ms_promedio": 57.41941391941392
  },
  {
    "_id": "microhubs",
    "peticiones": 290,
    "ms_promedio": 16.213793103448275
  },
  {
    "_id": "notificaciones",
    "peticiones": 330,
    "ms_promedio": 31.254545454545454
  },
  {
    "_id": "pedidos",
    "peticiones": 2121,
    "ms_promedio": 84.44413012729845
  },
  {
    "_id": "planeacion",
    "peticiones": 682,
    "ms_promedio": 46.49853372434018
  },
  {
    "_id": "precios",
    "peticiones": 743,
    "ms_promedio": 48.814266487214
  },
  {
    "_id": "productos",
    "peticiones": 206,
    "ms_promedio": 28.92233009708738
  },
  {
    "_id": "proveedores",
    "peticiones": 535,
    "ms_promedio": 51.592523364485984
  },
  {
    "_id": "punto-equilibrio",
    "peticiones": 1016,
    "ms_promedio": 174.99507874015748
  },
  {
    "_id": "reportes",
    "peticiones": 962,
    "ms_promedio": 163.34719334719335
  },
  {
    "_id": "rutas",
    "peticiones": 868,
    "ms_promedio": 103.91013824884793
  },
  {
    "_id": "seguimiento",
    "peticiones": 157,
    "ms_promedio": 29.53503184713376
  },
  {
    "_id": "simulacion",
    "peticiones": 1307,
    "ms_promedio": 152.51185921958685
  },
  {
    "_id": "sincronizacion",
    "peticiones": 575,
    "ms_promedio": 96.84
  },
  {
    "_id": "surtido",
    "peticiones": 673,
    "ms_promedio": 187.11144130757802
  },
  {
    "_id": "usuarios",
    "peticiones": 111,
    "ms_promedio": 44.24324324324324
  },
  {
    "_id": "zonas",
    "peticiones": 2392,
    "ms_promedio": 2.500836120401338
  }
]
```

## Servicio zonas · puerto 5108

### RAT-01 · Límite de consumo excedido · PASA

**Objetivo.** Más de 240 solicitudes por minuto desde la misma IP.

**Petición.** `GET http://zonas:5108/api/v1/zonas`

```http
Accept: application/json
X-Traza-Id: 724b0632-a4a7-471f-ad67-c595c4283a6b
```

**Respuesta.** HTTP 429 (esperado 429) · 5 ms · traza `724b0632-a4a7-471f-ad67-c595c4283a6b`

```json
{
  "error": {
    "codigo": "LIMITE_EXCEDIDO",
    "mensaje": "Máximo 240 solicitudes por minuto. Espera 37 segundos.",
    "traza_id": "724b0632-a4a7-471f-ad67-c595c4283a6b"
  }
}
```

**Explicación.** Contador rate:zonas:{ip}:{minuto} en Redis (db 1) con TTL de 120 s; responde Retry-After.

**Evidencia en Redis.** `db1 GET rate:zonas:67c0438560c481fa:29928739; db1 TTL rate:zonas:67c0438560c481fa:29928739`

```json
[
  {
    "comando": "db1 GET rate:zonas:67c0438560c481fa:29928739",
    "valor": "1"
  },
  {
    "comando": "db1 TTL rate:zonas:67c0438560c481fa:29928739",
    "valor": 87
  }
]
```
