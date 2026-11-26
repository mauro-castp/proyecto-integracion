# Evidencias de petición y respuesta · microservicios v1

Generado el 2026-10-20 01:31 contra los servicios en ejecución. 204 de 204 casos pasan.

## Servicio auth · puerto 5101

### AUTH-01 · Iniciar sesión (JSON) · PASA

**Objetivo.** Emitir el JWT de acceso y el token de renovación del repartidor.

**Petición.** `POST http://auth:5101/api/v1/auth/login`

```http
Accept: application/json
X-Traza-Id: 493bf573-6c70-4605-a9b0-af1bf8d35d68
Content-Type: application/json
```

```json
{
  "correo": "repartidor1@codex.mx",
  "clave": "********",
  "dispositivo": "Pixel 7"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 422 ms · traza `493bf573-6c70-4605-a9b0-af1bf8d35d68`

```json
{
  "token_acceso": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwicm9sIjo…(291 caracteres)",
  "token_renovacion": "rt_c0715fef36707bdedde4417923bdbdd7",
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
      "pedidos.ver"
    ]
  }
}
```

**Explicación.** bcrypt valida la clave; el jti del acceso se agrega a la sesión activa en Redis y la renovación se guarda como hash con TTL de 7 días. El login queda en la bitácora.

**Evidencia en Redis.** `SMEMBERS auth:sesion:7; TTL auth:sesion:7; TTL auth:refresh:1a89f3eb11973b99c3107410ea3e7b2df3968aeca34ba086797a2726345ae84f`

```json
[
  {
    "comando": "SMEMBERS auth:sesion:7",
    "valor": [
      "1d21201b329f41d0bd2191a03b0ba0b5"
    ]
  },
  {
    "comando": "TTL auth:sesion:7",
    "valor": 900
  },
  {
    "comando": "TTL auth:refresh:1a89f3eb11973b99c3107410ea3e7b2df3968aeca34ba086797a2726345ae84f",
    "valor": 604800
  }
]
```

**Evidencia en PostgreSQL.** `SELECT fecha, modulo, accion, detalle FROM auditoria WHERE correo_intento IS NULL AND usuario_id = 7 AND modulo = 'auth' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "fecha": "2026-10-20 01:31:19.695709+00:00",
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
X-Traza-Id: 135e4f18-ce73-45d0-94f0-55569e51469a
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><login xmlns="urn:microhubs:v1"><correo>planeador@codex.mx</correo><clave>********</clave></login>
```

**Respuesta.** HTTP 200 (esperado 200) · 407 ms · traza `135e4f18-ce73-45d0-94f0-55569e51469a`

```xml
<?xml version='1.0' encoding='utf-8'?>
<sesion xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><token_acceso>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwicm9sIjo…(291 caracteres)</token_acceso><token_renovacion>rt_df4d668ca9e11af4b477d3c699969d0a</token_renovacion><tipo>Bearer</tipo><expira_en>900</expira_en><usuario><id>5</id><nombre>Vanessa</nombre><apellidos>Morante López</apellidos><correo>planeador@codex.mx</correo><rol>planeador</rol><microhub_id xsi:nil="true" /><permisos><permiso>abastecimiento.ver</permiso><permiso>archivos.crear</permiso><permiso>archivos.ver</permiso><permiso>catalogo_publico.ver</permiso><permiso>configuracion.ver</permiso><permiso>indicadores.ver</permiso><permiso>inventario.ver</permiso><permiso>microhubs.ver</permiso><permiso>notificaciones.ver</permiso><permiso>pedidos.reasignar</permiso><permiso>pedidos.ver</permiso><permiso>planeacion.editar</permiso><permiso>planeacion.ver</permiso><permiso>precios.ver</permiso><permiso>productos.ver</permiso><permiso>proveedores.ver</permiso><permiso>reportes.exportar</permiso><permiso>reportes.ver</permiso><permiso>simulacion.ejecutar</permiso><permiso>simulacion.ver</permiso><permiso>zonas.ver</permiso></permisos></usuario></sesion>
```

**Explicación.** El cuerpo XML se valida contra los XSD antes de procesarse; la respuesta <sesion> también cumple el XSD.

### AUTH-03 · Clave incorrecta · PASA

**Objetivo.** Rechazar credenciales y contar el intento.

**Petición.** `POST http://auth:5101/api/v1/auth/login`

```http
Accept: application/json
X-Traza-Id: 4741ceab-1092-413c-a7c6-f8c06dc895d4
Content-Type: application/json
```

```json
{
  "correo": "auditor@codex.mx",
  "clave": "********"
}
```

**Respuesta.** HTTP 401 (esperado 401) · 263 ms · traza `4741ceab-1092-413c-a7c6-f8c06dc895d4`

```json
{
  "error": {
    "codigo": "CREDENCIALES_INVALIDAS",
    "mensaje": "Correo o clave incorrectos. Intento 1 de 5.",
    "traza_id": "4741ceab-1092-413c-a7c6-f8c06dc895d4"
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
X-Traza-Id: b517d255-8177-4353-9953-47d3dc074e7e
Content-Type: application/json
```

```json
{
  "correo": "sin-arroba",
  "clave": "********"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 6 ms · traza `b517d255-8177-4353-9953-47d3dc074e7e`

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
    "traza_id": "b517d255-8177-4353-9953-47d3dc074e7e"
  }
}
```

### AUTH-05 · XML con DTD (ataque XXE) · PASA

**Objetivo.** Rechazar entidades externas y DTD.

**Petición.** `POST http://auth:5101/api/v1/auth/login`

```http
Accept: application/xml
X-Traza-Id: 505b840c-e28b-43f8-bf54-509a511fa37c
Content-Type: application/xml
```

```xml
<?xml version="1.0"?><!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]><login xmlns="urn:microhubs:v1"><correo>&e;</correo><clave>********</clave></login>
```

**Respuesta.** HTTP 400 (esperado 400) · 6 ms · traza `505b840c-e28b-43f8-bf54-509a511fa37c`

```xml
<?xml version='1.0' encoding='utf-8'?>
<error xmlns="urn:microhubs:v1" version="1"><codigo>XML_INVALIDO</codigo><mensaje>El cuerpo XML no está bien formado o contiene DTD/entidades.</mensaje><traza_id>505b840c-e28b-43f8-bf54-509a511fa37c</traza_id></error>
```

**Explicación.** El lector XML (defusedxml) prohíbe DTD y entidades; el error también llega en XML.

### AUTH-06 · Validar token · PASA

**Objetivo.** Comprobar firma, vigencia y sesión activa en Redis.

**Petición.** `GET http://auth:5101/api/v1/auth/validar`

```http
Accept: application/json
X-Traza-Id: 092a6c3c-ed6c-4d3c-a0b1-e9d15c1b4c39
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 7 ms · traza `092a6c3c-ed6c-4d3c-a0b1-e9d15c1b4c39`

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
X-Traza-Id: 5bab4f8d-b4d3-4563-afaf-0f829527101d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 401 (esperado 401) · 6 ms · traza `5bab4f8d-b4d3-4563-afaf-0f829527101d`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.",
    "traza_id": "5bab4f8d-b4d3-4563-afaf-0f829527101d"
  }
}
```

### AUTH-08 · Renovar sesión · PASA

**Objetivo.** Obtener tokens nuevos con el token de renovación (rotación).

**Petición.** `POST http://auth:5101/api/v1/auth/renovar`

```http
Accept: application/json
X-Traza-Id: 2a002b8c-42a7-4673-9927-a80c3f23270f
Content-Type: application/json
```

```json
{
  "token_renovacion": "rt_d8c5e8b2a353837272d0542d77b27130"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 88 ms · traza `2a002b8c-42a7-4673-9927-a80c3f23270f`

```json
{
  "token_acceso": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwicm9sIjo…(291 caracteres)",
  "token_renovacion": "rt_e6f82aea31ae4be80e28072a8e2810af",
  "tipo": "Bearer",
  "expira_en": 900
}
```

**Explicación.** El token de renovación usado se borra de Redis y su acceso anterior queda revocado.

**Evidencia en Redis.** `EXISTS auth:refresh:4c9d9239fefce278de41c25fd48d3174fdf7406ef2d6fe4950121470dd891117`

```json
[
  {
    "comando": "EXISTS auth:refresh:4c9d9239fefce278de41c25fd48d3174fdf7406ef2d6fe4950121470dd891117",
    "valor": 0
  }
]
```

### AUTH-09 · Reusar un token de renovación · PASA

**Objetivo.** Un token de renovación sirve una sola vez.

**Petición.** `POST http://auth:5101/api/v1/auth/renovar`

```http
Accept: application/json
X-Traza-Id: 7f769cff-87f4-4088-b8e9-6ad95cedf1c0
Content-Type: application/json
```

```json
{
  "token_renovacion": "rt_d8c5e8b2a353837272d0542d77b27130"
}
```

**Respuesta.** HTTP 401 (esperado 401) · 7 ms · traza `7f769cff-87f4-4088-b8e9-6ad95cedf1c0`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.",
    "traza_id": "7f769cff-87f4-4088-b8e9-6ad95cedf1c0"
  }
}
```

### AUTH-10 · Cerrar sesión · PASA

**Objetivo.** Revocar el acceso del encabezado y la renovación del cuerpo.

**Petición.** `POST http://auth:5101/api/v1/auth/salir`

```http
Accept: application/json
X-Traza-Id: f7d6609b-dbc3-4717-83bf-e74f8779985e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "token_renovacion": "rt_e6f82aea31ae4be80e28072a8e2810af"
}
```

**Respuesta.** HTTP 204 (esperado 204) · 147 ms · traza `f7d6609b-dbc3-4717-83bf-e74f8779985e`

```json
(sin cuerpo)
```

**Explicación.** El jti se agrega a la lista de revocados con TTL igual a su vida restante y sale del conjunto de sesión.

**Evidencia en Redis.** `TTL auth:jti:revocado:9e69015b8f7e4b2cafe8414542a58a7e; SISMEMBER auth:sesion:7 9e69015b8f7e4b2cafe8414542a58a7e`

```json
[
  {
    "comando": "TTL auth:jti:revocado:9e69015b8f7e4b2cafe8414542a58a7e",
    "valor": 899
  },
  {
    "comando": "SISMEMBER auth:sesion:7 9e69015b8f7e4b2cafe8414542a58a7e",
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
X-Traza-Id: 76c71580-d262-4257-b541-4439d1d2dc1c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 401 (esperado 401) · 209 ms · traza `76c71580-d262-4257-b541-4439d1d2dc1c`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.",
    "traza_id": "76c71580-d262-4257-b541-4439d1d2dc1c"
  }
}
```

**Explicación.** El servicio de usuarios consulta auth:jti:revocado en Redis: la revocación es común a todos.

### USR-01 · Mi perfil (JSON) · PASA

**Objetivo.** Consultar el perfil de quien inició sesión.

**Petición.** `GET http://usuarios:5102/api/v1/usuarios/yo`

```http
Accept: application/json
X-Traza-Id: 767a38d6-840a-4a3d-b35d-889e4ef2e2dd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 72 ms · traza `767a38d6-840a-4a3d-b35d-889e4ef2e2dd`

```json
{
  "id": 7,
  "nombre": "Ramiro",
  "apellidos": "Alanís Lozano",
  "correo": "repartidor1@codex.mx",
  "telefono": "8114641034",
  "rol": "repartidor",
  "microhub": null,
  "ultimo_acceso": "2026-10-19T19:31:20-06:00"
}
```

### USR-02 · Mi perfil (XML) · PASA

**Objetivo.** El mismo recurso en XML según Accept.

**Petición.** `GET http://usuarios:5102/api/v1/usuarios/yo`

```http
Accept: application/xml
X-Traza-Id: ccf283b2-8a02-4c26-a82a-7177b0839c11
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 46 ms · traza `ccf283b2-8a02-4c26-a82a-7177b0839c11`

```xml
<?xml version='1.0' encoding='utf-8'?>
<usuario xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>5</id><nombre>Vanessa</nombre><apellidos>Morante López</apellidos><correo>planeador@codex.mx</correo><telefono>8178109897</telefono><rol>planeador</rol><microhub xsi:nil="true" /><ultimo_acceso>2026-10-19T19:31:21-06:00</ultimo_acceso></usuario>
```

### USR-03 · Actualizar mi teléfono (PATCH) · PASA

**Objetivo.** Modificar un dato del perfil.

**Petición.** `PATCH http://usuarios:5102/api/v1/usuarios/yo`

```http
Accept: application/json
X-Traza-Id: 8d0f0b9c-ea75-47ed-8808-3c92eaa4be59
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "telefono": "8112345678"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 87 ms · traza `8d0f0b9c-ea75-47ed-8808-3c92eaa4be59`

```json
{
  "id": 7,
  "nombre": "Ramiro",
  "apellidos": "Alanís Lozano",
  "correo": "repartidor1@codex.mx",
  "telefono": "8112345678",
  "rol": "repartidor",
  "microhub": null,
  "ultimo_acceso": "2026-10-19T19:31:20-06:00"
}
```

**Explicación.** El trigger de auditoría registra el cambio con el usuario que actuó.

**Evidencia en PostgreSQL.** `SELECT id, telefono, actualizado_en FROM usuario WHERE id = 7`

```json
[
  {
    "id": 7,
    "telefono": "8112345678",
    "actualizado_en": "2026-10-20 01:31:22.511507+00:00"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT fecha, accion, entidad, detalle FROM auditoria WHERE entidad = 'usuario' AND entidad_id = '7' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "fecha": "2026-10-20 01:31:22.511507+00:00",
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
X-Traza-Id: 95a2f077-d7d4-4d44-82ce-423cde5d55d1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "telefono": "12ab"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 7 ms · traza `95a2f077-d7d4-4d44-82ce-423cde5d55d1`

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
    "traza_id": "95a2f077-d7d4-4d44-82ce-423cde5d55d1"
  }
}
```

### USR-05 · Lista de usuarios (administrador) · PASA

**Objetivo.** Búsqueda y paginación.

**Petición.** `GET http://usuarios:5102/api/v1/usuarios?q=codex&rol=operador&pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 0a47bcd9-1609-451f-8f27-8694117ea1e6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 70 ms · traza `0a47bcd9-1609-451f-8f27-8694117ea1e6`

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
      "ultimo_acceso": null
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
      "ultimo_acceso": null
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
      "ultimo_acceso": null
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
X-Traza-Id: 0ed18af0-b59b-42ce-ab6f-49089a11c4c3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 62 ms · traza `0ed18af0-b59b-42ce-ab6f-49089a11c4c3`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "0ed18af0-b59b-42ce-ab6f-49089a11c4c3"
  }
}
```

**Evidencia en PostgreSQL.** `SELECT fecha, modulo, accion, detalle, exitoso FROM auditoria WHERE accion = 'acceso_denegado' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "fecha": "2026-10-20 01:31:22.735077+00:00",
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
X-Traza-Id: 2d37e38e-f7e3-4502-a9eb-4219c322e88b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 27 ms · traza `2d37e38e-f7e3-4502-a9eb-4219c322e88b`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "2d37e38e-f7e3-4502-a9eb-4219c322e88b"
  }
}
```

## Servicio productos · puerto 5103

### PRO-01 · Productos con búsqueda (caché vacía) · PASA

**Objetivo.** Consultar productos; la respuesta se guarda en Redis.

**Petición.** `GET http://productos:5103/api/v1/productos?q=arroz&pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: f90b5beb-463e-4196-9786-52e3ddc5590c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 215 ms · traza `f90b5beb-463e-4196-9786-52e3ddc5590c`

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
X-Traza-Id: 4d95d727-0d73-4e4b-a5ce-a8fd5f902147
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 4 ms · traza `4d95d727-0d73-4e4b-a5ce-a8fd5f902147`

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
X-Traza-Id: e388c551-d939-4d42-ae77-aa770c74d493
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 70 ms · traza `e388c551-d939-4d42-ae77-aa770c74d493`

```xml
<?xml version='1.0' encoding='utf-8'?>
<productos xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><datos><producto><id>3</id><clave_interna>AB-003</clave_interna><nombre>Aceite vegetal</nombre><categoria><id>1</id><nombre>Abarrote básico</nombre></categoria><unidad>botella</unidad><presentacion>900 ml</presentacion><precio>42.00</precio><imagen_url xsi:nil="true" /><estatus>activo</estatus></producto><producto><id>2</id><clave_interna>AB-002</clave_interna><nombre>Arroz superextra</nombre><categoria><id>1</id><nombre>Abarrote básico</nombre></categoria><unidad>kg</unidad><presentacion>1 kg</presentacion><precio>29.90</precio><imagen_url xsi:nil="true" /><estatus>activo</estatus></producto></datos><paginacion><pagina>1</pagina><por_pagina>2</por_pagina><total>51</total><paginas>26</paginas></paginacion></productos>
```

### PRO-04 · Un producto · PASA

**Objetivo.** Detalle por id.

**Petición.** `GET http://productos:5103/api/v1/productos/3`

```http
Accept: application/json
X-Traza-Id: fbb9dbac-c6f6-4e25-8e0b-2a6f71c6802e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 47 ms · traza `fbb9dbac-c6f6-4e25-8e0b-2a6f71c6802e`

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
X-Traza-Id: 2d159442-8a6d-43ab-811e-de0763031848
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 47 ms · traza `2d159442-8a6d-43ab-811e-de0763031848`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "2d159442-8a6d-43ab-811e-de0763031848"
  }
}
```

### PRO-06 · Paginación fuera de rango · PASA

**Objetivo.** por_pagina máximo 100.

**Petición.** `GET http://productos:5103/api/v1/productos?por_pagina=500`

```http
Accept: application/json
X-Traza-Id: 25a5101c-0e9a-4304-a6fb-24e6d4d740c3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 4 ms · traza `25a5101c-0e9a-4304-a6fb-24e6d4d740c3`

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
    "traza_id": "25a5101c-0e9a-4304-a6fb-24e6d4d740c3"
  }
}
```

### PRO-07 · Sin token · PASA

**Objetivo.** Todo endpoint protegido exige Authorization: Bearer.

**Petición.** `GET http://productos:5103/api/v1/productos`

```http
Accept: application/json
X-Traza-Id: aa4283fd-48cb-4703-9760-6995fc2a4f04
```

**Respuesta.** HTTP 401 (esperado 401) · 4 ms · traza `aa4283fd-48cb-4703-9760-6995fc2a4f04`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "Falta el encabezado Authorization: Bearer <token>.",
    "traza_id": "aa4283fd-48cb-4703-9760-6995fc2a4f04"
  }
}
```

## Servicio zonas · puerto 5108

### ZON-01 · Zonas (XML) · PASA

**Objetivo.** Colonias atendidas con centroide, válidas contra catalogos.xsd.

**Petición.** `GET http://zonas:5108/api/v1/zonas`

```http
Accept: application/xml
X-Traza-Id: 1650ce36-e5a1-460a-a9f5-d792de69a1e7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 195 ms · traza `1650ce36-e5a1-460a-a9f5-d792de69a1e7`

```xml
<?xml version='1.0' encoding='utf-8'?>
<zonas xmlns="urn:microhubs:v1" version="1"><datos><zona><id>1</id><clave>ZN-SB01</clave><nombre>San Bernabé Centro</nombre><colonia>San Bernabé</colonia><codigo_postal>64100</codigo_postal><latitud>25.7455</latitud><longitud>-100.3585</longitud></zona><zona><id>2</id><clave>ZN-SB02</clave><nombre>Valles de San Bernabé</nombre><colonia>Valles de San Bernabé</colonia><codigo_postal>64103</codigo_postal><latitud>25.753</latitud><longitud>-100.369</longitud></zona><zona><id>3</id><clave>ZN-SB03</clave><nombre>Paseo de San Bernabé</nombre><colonia>Paseo de San Bernabé</colonia><codigo_postal>64103</codigo_postal><latitud>25.758</latitud><longitud>-100.3745</longitud></zona><zona><id>4</id><clave>ZN-SB04</clave><nombre>San Bernabé X (F-113)</nombre><colonia>San Bernabé X (F-113)</colonia><codigo_postal>64105</codigo_postal><latitud>25.7495</latitud><longitud>-100.38</longitud></zona></datos><paginacion><pagina>1</pagina><por_pagina>20</por_pagina><total>4</total><paginas>1</paginas></paginacion></zonas>
```

### ZON-02 · Una zona · PASA

**Objetivo.** Detalle por id.

**Petición.** `GET http://zonas:5108/api/v1/zonas/1`

```http
Accept: application/json
X-Traza-Id: a021503a-5605-451f-930c-86005a672e6c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 31 ms · traza `a021503a-5605-451f-930c-86005a672e6c`

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
X-Traza-Id: ece294ba-ba5d-48ed-949e-3c6c981cb17f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 26 ms · traza `ece294ba-ba5d-48ed-949e-3c6c981cb17f`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "ece294ba-ba5d-48ed-949e-3c6c981cb17f"
  }
}
```

### ZON-04 · Sin token · PASA

**Objetivo.** Todo endpoint protegido exige Authorization: Bearer.

**Petición.** `GET http://zonas:5108/api/v1/zonas`

```http
Accept: application/json
X-Traza-Id: 337cf1aa-fac6-4f00-b990-4ade235865d5
```

**Respuesta.** HTTP 401 (esperado 401) · 5 ms · traza `337cf1aa-fac6-4f00-b990-4ade235865d5`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "Falta el encabezado Authorization: Bearer <token>.",
    "traza_id": "337cf1aa-fac6-4f00-b990-4ade235865d5"
  }
}
```

## Servicio microhubs · puerto 5109

### MIC-01 · Microhubs activos · PASA

**Objetivo.** Microhubs con coordenadas y radio.

**Petición.** `GET http://microhubs:5109/api/v1/microhubs?estatus=activo`

```http
Accept: application/json
X-Traza-Id: 1b455851-0c04-4e01-b7ae-6575e4e335b1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 231 ms · traza `1b455851-0c04-4e01-b7ae-6575e4e335b1`

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
X-Traza-Id: 4fa76a60-950c-41eb-b999-15677bd53c27
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 22 ms · traza `4fa76a60-950c-41eb-b999-15677bd53c27`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "4fa76a60-950c-41eb-b999-15677bd53c27"
  }
}
```

### MIC-03 · Sin token · PASA

**Objetivo.** Todo endpoint protegido exige Authorization: Bearer.

**Petición.** `GET http://microhubs:5109/api/v1/microhubs`

```http
Accept: application/json
X-Traza-Id: cd349635-f06f-41a0-a202-8e0edf21d92c
```

**Respuesta.** HTTP 401 (esperado 401) · 4 ms · traza `cd349635-f06f-41a0-a202-8e0edf21d92c`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "Falta el encabezado Authorization: Bearer <token>.",
    "traza_id": "cd349635-f06f-41a0-a202-8e0edf21d92c"
  }
}
```

## Servicio pedidos · puerto 5104

### PED-01 · Pedidos entregados (JSON) · PASA

**Objetivo.** Lista filtrada por estado y fechas.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos?estado=entregado&pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 29461999-5848-4c51-9f16-a8b6a14a45d3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 222 ms · traza `29461999-5848-4c51-9f16-a8b6a14a45d3`

```json
{
  "datos": [
    {
      "id": 105,
      "folio": "PED-20261020-000105",
      "estado": "entregado",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "microhub_id": 2,
      "total": 148.0,
      "creado_en": "2026-10-19T00:40:09-06:00"
    },
    {
      "id": 18,
      "folio": "PED-20261020-000018",
      "estado": "entregado",
      "zona": {
        "id": 1,
        "nombre": "San Bernabé Centro"
      },
      "microhub_id": 1,
      "total": 180.5,
      "creado_en": "2026-10-18T23:31:54-06:00"
    },
    {
      "id": 91,
      "folio": "PED-20261020-000091",
      "estado": "entregado",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "microhub_id": 2,
      "total": 128.5,
      "creado_en": "2026-10-18T20:04:15-06:00"
    },
    {
      "id": 63,
      "folio": "PED-20261020-000063",
      "estado": "entregado",
      "zona": {
        "id": 3,
        "nombre": "Paseo de San Bernabé"
      },
      "microhub_id": 2,
      "total": 148.5,
      "creado_en": "2026-10-18T19:38:24-06:00"
    },
    {
      "id": 3,
      "folio": "PED-20261020-000003",
      "estado": "entregado",
      "zona": {
        "id": 3,
        "nombre": "Paseo de San Bernabé"
      },
      "microhub_id": 2,
      "total": 142.9,
      "creado_en": "2026-10-17T06:51:16-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 113,
    "paginas": 23
  }
}
```

### PED-02 · Pedidos (XML) · PASA

**Objetivo.** La misma lista en XML.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos?estado=entregado&por_pagina=2`

```http
Accept: application/xml
X-Traza-Id: 4ca5500e-bcb6-49a7-aa4c-207a65e3850d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 71 ms · traza `4ca5500e-bcb6-49a7-aa4c-207a65e3850d`

```xml
<?xml version='1.0' encoding='utf-8'?>
<pedidos xmlns="urn:microhubs:v1" version="1"><datos><pedido><id>105</id><folio>PED-20261020-000105</folio><estado>entregado</estado><zona><id>2</id><nombre>Valles de San Bernabé</nombre></zona><microhub_id>2</microhub_id><total>148.00</total><creado_en>2026-10-19T00:40:09-06:00</creado_en></pedido><pedido><id>18</id><folio>PED-20261020-000018</folio><estado>entregado</estado><zona><id>1</id><nombre>San Bernabé Centro</nombre></zona><microhub_id>1</microhub_id><total>180.50</total><creado_en>2026-10-18T23:31:54-06:00</creado_en></pedido></datos><paginacion><pagina>1</pagina><por_pagina>2</por_pagina><total>113</total><paginas>57</paginas></paginacion></pedidos>
```

### PED-03 · Detalle con líneas · PASA

**Objetivo.** Cliente, domicilio y líneas del pedido.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/105`

```http
Accept: application/json
X-Traza-Id: e3e481dd-cf4a-4c8e-aea6-419f66d2ef84
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 89 ms · traza `e3e481dd-cf4a-4c8e-aea6-419f66d2ef84`

```json
{
  "id": 105,
  "folio": "PED-20261020-000105",
  "estado": "entregado",
  "cliente": {
    "nombre": "Juan Sepúlveda Martínez",
    "telefono": "8136595095"
  },
  "domicilio": {
    "calle": "Fidel Velázquez",
    "numero_ext": "2470",
    "colonia": "Valles de San Bernabé",
    "latitud": 25.758336,
    "longitud": -100.370653
  },
  "zona": {
    "id": 2,
    "nombre": "Valles de San Bernabé"
  },
  "microhub_id": 2,
  "subtotal": 133.0,
  "costo_envio": 15.0,
  "total": 148.0,
  "creado_en": "2026-10-19T00:40:09-06:00",
  "lineas": [
    {
      "id": 481,
      "producto_id": 33,
      "nombre": "Crema ácida",
      "cantidad": 1,
      "precio_unitario": 36.0,
      "importe": 36.0
    },
    {
      "id": 482,
      "producto_id": 5,
      "nombre": "Sal de mesa",
      "cantidad": 1,
      "precio_unitario": 14.0,
      "importe": 14.0
    },
    {
      "id": 483,
      "producto_id": 45,
      "nombre": "Fibra para trastes",
      "cantidad": 1,
      "precio_unitario": 18.0,
      "importe": 18.0
    },
    {
      "id": 484,
      "producto_id": 39,
      "nombre": "Cloro",
      "cantidad": 1,
      "precio_unitario": 19.5,
      "importe": 19.5
    },
    {
      "id": 485,
      "producto_id": 7,
      "nombre": "Harina de trigo",
      "cantidad": 1,
      "precio_unitario": 24.5,
      "importe": 24.5
    },
    {
      "id": 486,
      "producto_id": 9,
      "nombre": "Atún en agua",
      "cantidad": 1,
      "precio_unitario": 21.0,
      "importe": 21.0
    }
  ]
}
```

### PED-04 · Historial de estados · PASA

**Objetivo.** Cambios de estado con usuario y fecha.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/105/historial`

```http
Accept: application/json
X-Traza-Id: a4d7514f-fa3f-4aba-a78f-8d9abfaa8d56
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 64 ms · traza `a4d7514f-fa3f-4aba-a78f-8d9abfaa8d56`

```json
{
  "pedido_id": 105,
  "eventos": [
    {
      "estado_anterior": null,
      "estado_nuevo": "creado",
      "usuario": null,
      "motivo": null,
      "fecha": "2026-10-19T00:40:09-06:00"
    },
    {
      "estado_anterior": "creado",
      "estado_nuevo": "asignado",
      "usuario": null,
      "motivo": null,
      "fecha": "2026-10-19T00:40:09-06:00"
    },
    {
      "estado_anterior": "asignado",
      "estado_nuevo": "en_preparacion",
      "usuario": null,
      "motivo": null,
      "fecha": "2026-10-19T00:40:09-06:00"
    },
    {
      "estado_anterior": "en_preparacion",
      "estado_nuevo": "en_ruta",
      "usuario": null,
      "motivo": null,
      "fecha": "2026-10-19T00:40:09-06:00"
    },
    {
      "estado_anterior": "en_ruta",
      "estado_nuevo": "entregado",
      "usuario": null,
      "motivo": null,
      "fecha": "2026-10-19T00:40:09-06:00"
    }
  ]
}
```

**Evidencia en PostgreSQL.** `SELECT fecha, estado_anterior, estado_nuevo, usuario_id FROM historial_estatus WHERE pedido_id = %s ORDER BY fecha, id`

```json
[
  {
    "fecha": "2026-10-19 06:40:09.882139+00:00",
    "estado_anterior": null,
    "estado_nuevo": "creado",
    "usuario_id": null
  },
  {
    "fecha": "2026-10-19 06:40:09.882139+00:00",
    "estado_anterior": "creado",
    "estado_nuevo": "asignado",
    "usuario_id": null
  },
  {
    "fecha": "2026-10-19 06:40:09.882139+00:00",
    "estado_anterior": "asignado",
    "estado_nuevo": "en_preparacion",
    "usuario_id": null
  },
  {
    "fecha": "2026-10-19 06:40:09.882139+00:00",
    "estado_anterior": "en_preparacion",
    "estado_nuevo": "en_ruta",
    "usuario_id": null
  },
  {
    "fecha": "2026-10-19 06:40:09.882139+00:00",
    "estado_anterior": "en_ruta",
    "estado_nuevo": "entregado",
    "usuario_id": null
  }
]
```

### PED-05 · Filtro inválido · PASA

**Objetivo.** Un estado que no existe se rechaza.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos?estado=inventado`

```http
Accept: application/json
X-Traza-Id: 91113c51-4b16-478e-8f0f-9cd1b21f68fd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 7 ms · traza `91113c51-4b16-478e-8f0f-9cd1b21f68fd`

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
    "traza_id": "91113c51-4b16-478e-8f0f-9cd1b21f68fd"
  }
}
```

### PED-06 · Pedido fuera del ámbito · PASA

**Objetivo.** El operador del MH-01 no ve pedidos de otro microhub (RN22).

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/1`

```http
Accept: application/json
X-Traza-Id: 537c15b0-83dc-4f45-bf2e-d3d7a358a8b5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 37 ms · traza `537c15b0-83dc-4f45-bf2e-d3d7a358a8b5`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el pedido o no está en tu ámbito.",
    "traza_id": "537c15b0-83dc-4f45-bf2e-d3d7a358a8b5"
  }
}
```

**Explicación.** El ámbito lo decide PostgreSQL con fn_pedidos_visibles; el servicio no lo puede saltar.

### PED-07 · Cerrar desde pedidos · PASA

**Objetivo.** Los cierres de entrega solo se registran en el servicio de entregas.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/105/estado`

```http
Accept: application/json
X-Traza-Id: 35c0c179-4440-4c3a-ae59-a4f12a53a400
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "estado": "entregado"
}
```

**Respuesta.** HTTP 409 (esperado 409) · 6 ms · traza `35c0c179-4440-4c3a-ae59-a4f12a53a400`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "El cierre de una entrega se registra con POST /api/v1/entregas/{id}/resultado.",
    "traza_id": "35c0c179-4440-4c3a-ae59-a4f12a53a400"
  }
}
```

### PED-08 · Transición ilegal (regla del motor) · PASA

**Objetivo.** Un pedido entregado no puede regresar a preparación.

**Petición.** `PATCH http://pedidos:5104/api/v1/pedidos/2/estado`

```http
Accept: application/json
X-Traza-Id: 695ef117-5b30-4c52-9983-322500ce4071
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0Iiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "estado": "en_preparacion"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 67 ms · traza `695ef117-5b30-4c52-9983-322500ce4071`

```json
{
  "error": {
    "codigo": "REGLA_NEGOCIO",
    "mensaje": "RN20: transición ilegal entregado -> en_preparacion para el rol operador. El pedido PED-20261020-000002 conserva su estado.",
    "traza_id": "695ef117-5b30-4c52-9983-322500ce4071"
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
X-Traza-Id: 1a4a24d9-5246-47ae-882c-dd3833bdd846
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "evidencia-entrega-129.jpg",
  "tipo_mime": "image/jpeg",
  "contenido_base64": "/9j/4AAQSkZJRgABAQAAAQABAAAAAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcY…(368 caracteres)",
  "referencia": {
    "tipo": "entrega",
    "id": "129"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 135 ms · traza `1a4a24d9-5246-47ae-882c-dd3833bdd846`

```json
{
  "id": "6ad6c46d86a22ebc8612b586",
  "nombre": "evidencia-entrega-129.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "129"
  },
  "subido_por": 7,
  "creado_en": "2026-10-19T19:31:25-06:00"
}
```

**Explicación.** Se valida que el contenido sea JPEG real, se calcula su SHA-256 y que la entrega sea del repartidor.

**Evidencia en MongoDB.** `db.documentos.findOne({_id: ObjectId('6ad6c46d86a22ebc8612b586')}, {contenido: 0})`

```json
{
  "_id": "6ad6c46d86a22ebc8612b586",
  "nombre": "evidencia-entrega-129.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "129"
  },
  "subido_por": 7,
  "creado_en": "2026-10-20 01:31:25.129000+00:00"
}
```

### DOC-02 · Subir evidencia de la segunda entrega · PASA

**Objetivo.** Evidencia para el cierre parcial.

**Petición.** `POST http://documentos:5107/api/v1/documentos`

```http
Accept: application/json
X-Traza-Id: 60e7586a-1f74-4732-90ca-baa54397508d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "evidencia-entrega-130.jpg",
  "tipo_mime": "image/jpeg",
  "contenido_base64": "/9j/4AAQSkZJRgABAQAAAQABAAAAAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcY…(368 caracteres)",
  "referencia": {
    "tipo": "entrega",
    "id": "130"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 28 ms · traza `60e7586a-1f74-4732-90ca-baa54397508d`

```json
{
  "id": "6ad6c46d86a22ebc8612b589",
  "nombre": "evidencia-entrega-130.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "130"
  },
  "subido_por": 7,
  "creado_en": "2026-10-19T19:31:25-06:00"
}
```

### DOC-03 · Tipo de archivo falso · PASA

**Objetivo.** Un PDF declarado como JPEG se rechaza por su firma.

**Petición.** `POST http://documentos:5107/api/v1/documentos`

```http
Accept: application/json
X-Traza-Id: 741e821e-262e-45fe-940e-ba569a8b0015
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
    "id": "129"
  }
}
```

**Respuesta.** HTTP 422 (esperado 422) · 6 ms · traza `741e821e-262e-45fe-940e-ba569a8b0015`

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
    "traza_id": "741e821e-262e-45fe-940e-ba569a8b0015"
  }
}
```

### DOC-04 · Evidencia en entrega ajena · PASA

**Objetivo.** Un repartidor no adjunta a entregas de otro.

**Petición.** `POST http://documentos:5107/api/v1/documentos`

```http
Accept: application/json
X-Traza-Id: f3a21f16-2af2-46ac-8064-2c0412a8e4a8
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
    "id": "129"
  }
}
```

**Respuesta.** HTTP 403 (esperado 403) · 33 ms · traza `f3a21f16-2af2-46ac-8064-2c0412a8e4a8`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Solo puedes adjuntar evidencia a tus entregas.",
    "traza_id": "f3a21f16-2af2-46ac-8064-2c0412a8e4a8"
  }
}
```

### DOC-05 · Documento temporal · PASA

**Objetivo.** Documento que después se elimina.

**Petición.** `POST http://documentos:5107/api/v1/documentos`

```http
Accept: application/json
X-Traza-Id: 22f6892a-bc3e-47e1-9ed7-799279594bc5
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

**Respuesta.** HTTP 201 (esperado 201) · 9 ms · traza `22f6892a-bc3e-47e1-9ed7-799279594bc5`

```json
{
  "id": "6ad6c46d86a22ebc8612b590",
  "nombre": "borrador.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "usuario",
    "id": "7"
  },
  "subido_por": 7,
  "creado_en": "2026-10-19T19:31:25-06:00"
}
```

### DOC-06 · Mis documentos · PASA

**Objetivo.** Filtro por referencia.

**Petición.** `GET http://documentos:5107/api/v1/documentos?referencia_tipo=entrega&referencia_id=129`

```http
Accept: application/json
X-Traza-Id: b986ba60-b0bd-4941-a3d6-31a92d2edd0e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 13 ms · traza `b986ba60-b0bd-4941-a3d6-31a92d2edd0e`

```json
{
  "datos": [
    {
      "id": "6ad6c46d86a22ebc8612b586",
      "nombre": "evidencia-entrega-129.jpg",
      "tipo_mime": "image/jpeg",
      "tamano_bytes": 276,
      "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
      "referencia": {
        "tipo": "entrega",
        "id": "129"
      },
      "subido_por": 7,
      "creado_en": "2026-10-19T19:31:25-06:00"
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

**Petición.** `GET http://documentos:5107/api/v1/documentos/6ad6c46d86a22ebc8612b586`

```http
Accept: application/xml
X-Traza-Id: 1a1105f7-a016-47fd-a70f-249e5cb33bb7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 9 ms · traza `1a1105f7-a016-47fd-a70f-249e5cb33bb7`

```xml
<?xml version='1.0' encoding='utf-8'?>
<documento xmlns="urn:microhubs:v1" version="1"><id>6ad6c46d86a22ebc8612b586</id><nombre>evidencia-entrega-129.jpg</nombre><tipo_mime>image/jpeg</tipo_mime><tamano_bytes>276</tamano_bytes><sha256>7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc</sha256><referencia><tipo>entrega</tipo><id>129</id></referencia><subido_por>7</subido_por><creado_en>2026-10-19T19:31:25-06:00</creado_en></documento>
```

### DOC-08 · Contenido en Base64 · PASA

**Objetivo.** Recuperar el archivo.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6ad6c46d86a22ebc8612b586/contenido`

```http
Accept: application/json
X-Traza-Id: f6b523fa-d1b9-47f0-9736-15ec957aa3fc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 8 ms · traza `f6b523fa-d1b9-47f0-9736-15ec957aa3fc`

```json
{
  "id": "6ad6c46d86a22ebc8612b586",
  "nombre": "evidencia-entrega-129.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "129"
  },
  "subido_por": 7,
  "creado_en": "2026-10-19T19:31:25-06:00",
  "contenido_base64": "/9j/4AAQSkZJRgABAQAAAQABAAAAAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcY…(368 caracteres)"
}
```

### DOC-09 · Eliminar documento (DELETE) · PASA

**Objetivo.** Borrar un documento propio.

**Petición.** `DELETE http://documentos:5107/api/v1/documentos/6ad6c46d86a22ebc8612b590`

```http
Accept: application/json
X-Traza-Id: 21440aa9-1c5a-4d5a-82bc-7939c4e815a6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 31 ms · traza `21440aa9-1c5a-4d5a-82bc-7939c4e815a6`

```json
(sin cuerpo)
```

**Evidencia en MongoDB.** `db.documentos.countDocuments({_id: ObjectId('6ad6c46d86a22ebc8612b590')})`

```json
0
```

### DOC-10 · Id inexistente · PASA

**Objetivo.** Registro que no existe.

**Petición.** `GET http://documentos:5107/api/v1/documentos/ffffffffffffffffffffffff`

```http
Accept: application/json
X-Traza-Id: fc20f4d9-f7e1-406c-88fb-a5806de81de2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 8 ms · traza `fc20f4d9-f7e1-406c-88fb-a5806de81de2`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "fc20f4d9-f7e1-406c-88fb-a5806de81de2"
  }
}
```

## Servicio seguimiento · puerto 5110

### SEG-01 · Enviar puntos GPS · PASA

**Objetivo.** Guardar el recorrido del repartidor en MongoDB.

**Petición.** `POST http://seguimiento:5110/api/v1/seguimiento/129/ubicaciones`

```http
Accept: application/json
X-Traza-Id: d8b37a33-ff9a-409e-9493-322cc7d303da
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
      "capturado_en": "2026-10-20T01:25:25+00:00"
    },
    {
      "latitud": 25.7486,
      "longitud": -100.3606,
      "precision_m": 8.0,
      "capturado_en": "2026-10-20T01:27:25+00:00"
    },
    {
      "latitud": 25.7491,
      "longitud": -100.3611,
      "precision_m": 8.5,
      "capturado_en": "2026-10-20T01:29:25+00:00"
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 143 ms · traza `d8b37a33-ff9a-409e-9493-322cc7d303da`

```json
{
  "recibidos": 3
}
```

**Evidencia en MongoDB.** `db.ubicaciones_entrega.find({entrega_id: NumberLong(129)}).sort({capturado_en: 1})`

```json
[
  {
    "entrega_id": 129,
    "usuario_id": 7,
    "posicion": {
      "type": "Point",
      "coordinates": [
        -100.36,
        25.748
      ]
    },
    "precision_m": 9.0,
    "capturado_en": "2026-10-20 01:25:25+00:00",
    "recibido_en": "2026-10-20 01:31:25.835000+00:00"
  },
  {
    "entrega_id": 129,
    "usuario_id": 7,
    "posicion": {
      "type": "Point",
      "coordinates": [
        -100.3606,
        25.7486
      ]
    },
    "precision_m": 8.0,
    "capturado_en": "2026-10-20 01:27:25+00:00",
    "recibido_en": "2026-10-20 01:31:25.835000+00:00"
  },
  {
    "entrega_id": 129,
    "usuario_id": 7,
    "posicion": {
      "type": "Point",
      "coordinates": [
        -100.3611,
        25.7491
      ]
    },
    "precision_m": 8.5,
    "capturado_en": "2026-10-20 01:29:25+00:00",
    "recibido_en": "2026-10-20 01:31:25.835000+00:00"
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

**Petición.** `GET http://seguimiento:5110/api/v1/seguimiento/129/recorrido`

```http
Accept: application/json
X-Traza-Id: 8b98593e-304a-4765-8038-0b3e1945e5b6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 34 ms · traza `8b98593e-304a-4765-8038-0b3e1945e5b6`

```json
{
  "entrega_id": 129,
  "puntos": 3,
  "distancia_km": 0.16,
  "inicio": "2026-10-19T19:25:25-06:00",
  "fin": "2026-10-19T19:29:25-06:00",
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

**Petición.** `GET http://seguimiento:5110/api/v1/seguimiento/129/recorrido`

```http
Accept: application/json
X-Traza-Id: 5394ca50-3712-4ee0-bd8d-e837c0328e71
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4Iiwi…(296 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 30 ms · traza `5394ca50-3712-4ee0-bd8d-e837c0328e71`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe la entrega o no está asignada a ti.",
    "traza_id": "5394ca50-3712-4ee0-bd8d-e837c0328e71"
  }
}
```

### SEG-04 · Recorrido sin token · PASA

**Objetivo.** Todo endpoint protegido exige Authorization: Bearer.

**Petición.** `GET http://seguimiento:5110/api/v1/seguimiento/129/recorrido`

```http
Accept: application/json
X-Traza-Id: f0fb265f-abda-4651-9e53-62cd5c875366
```

**Respuesta.** HTTP 401 (esperado 401) · 4 ms · traza `f0fb265f-abda-4651-9e53-62cd5c875366`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "Falta el encabezado Authorization: Bearer <token>.",
    "traza_id": "f0fb265f-abda-4651-9e53-62cd5c875366"
  }
}
```

## Servicio entregas · puerto 5105

### ENT-01 · Mis entregas · PASA

**Objetivo.** Paradas abiertas del repartidor en el turno de hoy (RN25).

**Petición.** `GET http://entregas:5105/api/v1/entregas/mias?pagina=1&por_pagina=20`

```http
Accept: application/json
X-Traza-Id: a26808f4-fe61-421a-8926-0cfbbc7dffbd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 60 ms · traza `a26808f4-fe61-421a-8926-0cfbbc7dffbd`

```json
{
  "datos": [
    {
      "id": 129,
      "pedido_id": 153,
      "folio": "PED-20261020-000153",
      "estado_pedido": "en_ruta",
      "orden_parada": 1,
      "direccion": "Fidel Velázquez 2470, Valles de San Bernabé",
      "zona": "Valles de San Bernabé",
      "distancia_km": 0.23,
      "minutos_estimados": 10.0,
      "total": 148.0
    },
    {
      "id": 130,
      "pedido_id": 154,
      "folio": "PED-20261020-000154",
      "estado_pedido": "en_ruta",
      "orden_parada": 2,
      "direccion": "Fresno 3177, Valles de San Bernabé",
      "zona": "Valles de San Bernabé",
      "distancia_km": 1.39,
      "minutos_estimados": 16.0,
      "total": 199.5
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

**Petición.** `GET http://entregas:5105/api/v1/entregas/129`

```http
Accept: application/json
X-Traza-Id: 1bbda815-10c8-481c-a8f0-8a68f5c63af2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 82 ms · traza `1bbda815-10c8-481c-a8f0-8a68f5c63af2`

```json
{
  "id": 129,
  "pedido_id": 153,
  "folio": "PED-20261020-000153",
  "estado_pedido": "en_ruta",
  "cliente": {
    "nombre": "Juan Sepúlveda Martínez",
    "telefono": "8136595095"
  },
  "domicilio": {
    "calle": "Fidel Velázquez",
    "numero_ext": "2470",
    "colonia": "Valles de San Bernabé",
    "latitud": 25.758336,
    "longitud": -100.370653
  },
  "orden_parada": 1,
  "distancia_km": 0.23,
  "minutos_estimados": 10.0,
  "total": 148.0,
  "lineas": [
    {
      "pedido_detalle_id": 683,
      "nombre": "Refresco de cola",
      "cantidad": 2
    },
    {
      "pedido_detalle_id": 684,
      "nombre": "Limpiador multiusos",
      "cantidad": 2
    }
  ]
}
```

### ENT-03 · Entrega de otro repartidor · PASA

**Objetivo.** El repartidor 2 no ve la entrega del repartidor 1.

**Petición.** `GET http://entregas:5105/api/v1/entregas/129`

```http
Accept: application/json
X-Traza-Id: 66f12d74-34a3-401e-b852-970857a37522
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4Iiwi…(296 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 41 ms · traza `66f12d74-34a3-401e-b852-970857a37522`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe la entrega o no está asignada a ti.",
    "traza_id": "66f12d74-34a3-401e-b852-970857a37522"
  }
}
```

### ENT-04 · Monto incorrecto (regla de negocio) · PASA

**Objetivo.** Una entrega completa cobra el total (RN27).

**Petición.** `POST http://entregas:5105/api/v1/entregas/129/resultado`

```http
Accept: application/json
X-Traza-Id: 4488a77f-6679-4a6a-ad89-1c562fbcdce7
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
    "6ad6c46d86a22ebc8612b586"
  ],
  "capturado_en": "2026-10-20T01:31:25+00:00",
  "id_cliente_local": "f96b27d4-a998-4f99-9e4c-87a8b338b08f"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 72 ms · traza `4488a77f-6679-4a6a-ad89-1c562fbcdce7`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "monto_cobrado",
        "mensaje": "Una entrega completa cobra el total del pedido (148.00)."
      }
    ],
    "traza_id": "4488a77f-6679-4a6a-ad89-1c562fbcdce7"
  }
}
```

### ENT-05 · Cerrar entrega como entregado · PASA

**Objetivo.** Registrar el resultado con evidencia y ubicación.

**Petición.** `POST http://entregas:5105/api/v1/entregas/129/resultado`

```http
Accept: application/json
X-Traza-Id: 8565ee2b-39be-493d-add9-1a062c9ab9df
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 148.0,
  "cambio_entregado": 0.0,
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611,
    "precision_m": 8.5
  },
  "evidencia_ids": [
    "6ad6c46d86a22ebc8612b586"
  ],
  "capturado_en": "2026-10-20T01:31:25+00:00",
  "id_cliente_local": "f96b27d4-a998-4f99-9e4c-87a8b338b08f"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 106 ms · traza `8565ee2b-39be-493d-add9-1a062c9ab9df`

```json
{
  "entrega_id": 129,
  "pedido_id": 153,
  "estado_pedido": "entregado",
  "cerrado_en": "2026-10-19T19:31:26-06:00",
  "duplicado": false
}
```

**Explicación.** Una sola transacción: cierra la entrega, cambia el pedido (el trigger valida la transición y escribe historial y bitácora) y el trigger de cierre avisa al cliente. La operación se registra en MongoDB.

**Evidencia en PostgreSQL.** `SELECT id, cierre_en, resultado, monto_cobrado, id_cliente_local, evidencia_ids, cierre_latitud, cierre_longitud FROM entrega WHERE id = %s`

```json
[
  {
    "id": 129,
    "cierre_en": "2026-10-20 01:31:26.388267+00:00",
    "resultado": "entregado",
    "monto_cobrado": "148.00",
    "id_cliente_local": "f96b27d4-a998-4f99-9e4c-87a8b338b08f",
    "evidencia_ids": [
      "6ad6c46d86a22ebc8612b586"
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
    "fecha": "2026-10-20 01:31:26.388267+00:00"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT destinatario_id, tipo, titulo, mensaje, referencia_tipo, referencia_id FROM web_notificacion WHERE referencia_tipo = 'pedido' AND referencia_id = %s ORDER BY id DESC LIMIT 1`

```json
[
  {
    "destinatario_id": 16,
    "tipo": "pedido",
    "titulo": "Pedido PED-20261020-000153",
    "mensaje": "El pedido cambió a entregado.",
    "referencia_tipo": "pedido",
    "referencia_id": "153"
  }
]
```

**Evidencia en MongoDB.** `db.sincronizaciones_moviles.findOne({operacion_uuid: 'f96b27d4-a998-4f99-9e4c-87a8b338b08f'})`

```json
{
  "operacion_uuid": "f96b27d4-a998-4f99-9e4c-87a8b338b08f",
  "capturado_en": "2026-10-20 01:31:25+00:00",
  "carga": {
    "entrega_id": 129,
    "resultado": "entregado",
    "monto_cobrado": 148.0,
    "evidencia_ids": [
      "6ad6c46d86a22ebc8612b586"
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
  "pedido_id": 153,
  "sincronizado_en": "2026-10-20 01:31:26.439000+00:00",
  "tipo_operacion": "cierre_entrega",
  "usuario_id": 7
}
```

### ENT-06 · Reintento con el mismo UUID · PASA

**Objetivo.** Idempotencia: el cierre no se aplica dos veces.

**Petición.** `POST http://entregas:5105/api/v1/entregas/129/resultado`

```http
Accept: application/json
X-Traza-Id: 313f9d79-d167-4dd2-8508-0e3ce29e9b74
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 148.0,
  "cambio_entregado": 0.0,
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611,
    "precision_m": 8.5
  },
  "evidencia_ids": [
    "6ad6c46d86a22ebc8612b586"
  ],
  "capturado_en": "2026-10-20T01:31:25+00:00",
  "id_cliente_local": "f96b27d4-a998-4f99-9e4c-87a8b338b08f"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 91 ms · traza `313f9d79-d167-4dd2-8508-0e3ce29e9b74`

```json
{
  "entrega_id": 129,
  "pedido_id": 153,
  "estado_pedido": "entregado",
  "cerrado_en": "2026-10-19T19:31:26-06:00",
  "duplicado": true
}
```

**Explicación.** La respuesta es la misma con duplicado=true. MongoDB actualiza el documento de la operación (intentos = 2).

**Evidencia en MongoDB.** `db.sincronizaciones_moviles.findOne({operacion_uuid: 'f96b27d4-a998-4f99-9e4c-87a8b338b08f'}, {estado: 1, intentos: 1})`

```json
{
  "estado": "aplicada",
  "intentos": 2,
  "sincronizado_en": "2026-10-20 01:31:26.640000+00:00"
}
```

### ENT-07 · Otro cierre sobre la misma entrega · PASA

**Objetivo.** Conflicto: ya estaba cerrada con otra operación.

**Petición.** `POST http://entregas:5105/api/v1/entregas/129/resultado`

```http
Accept: application/json
X-Traza-Id: eaba3733-c0d3-432a-b90a-db732c5edac8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 148.0,
  "cambio_entregado": 0.0,
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611,
    "precision_m": 8.5
  },
  "evidencia_ids": [
    "6ad6c46d86a22ebc8612b586"
  ],
  "capturado_en": "2026-10-20T01:31:25+00:00",
  "id_cliente_local": "f901be9e-213c-4aad-9c79-eee765d05a88"
}
```

**Respuesta.** HTTP 409 (esperado 409) · 66 ms · traza `eaba3733-c0d3-432a-b90a-db732c5edac8`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "La entrega ya se cerró con otra operación.",
    "traza_id": "eaba3733-c0d3-432a-b90a-db732c5edac8"
  }
}
```

### ENT-08 · Detalle tras el cierre · PASA

**Objetivo.** El repartidor deja de ver el domicilio (RN26).

**Petición.** `GET http://entregas:5105/api/v1/entregas/129`

```http
Accept: application/json
X-Traza-Id: 82ce13a0-ffa7-41bc-83f1-040b75adcd3f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 35 ms · traza `82ce13a0-ffa7-41bc-83f1-040b75adcd3f`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "La entrega ya se cerró; su información ya no está disponible.",
    "traza_id": "82ce13a0-ffa7-41bc-83f1-040b75adcd3f"
  }
}
```

### ENT-09 · Parcial sin motivo · PASA

**Objetivo.** Cada línea devuelta necesita motivo (RN28).

**Petición.** `POST http://entregas:5105/api/v1/entregas/130/resultado`

```http
Accept: application/json
X-Traza-Id: a5a1d57e-4d37-49e8-9e58-1c4b773672aa
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
      "pedido_detalle_id": 685,
      "cantidad_entregada": 3,
      "cantidad_devuelta": 0
    },
    {
      "pedido_detalle_id": 686,
      "cantidad_entregada": 0,
      "cantidad_devuelta": 3
    }
  ],
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611
  },
  "evidencia_ids": [
    "6ad6c46d86a22ebc8612b589"
  ],
  "capturado_en": "2026-10-20T01:31:25+00:00",
  "id_cliente_local": "dcf00411-2396-4f16-a9b9-671290a5b8d4"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 72 ms · traza `a5a1d57e-4d37-49e8-9e58-1c4b773672aa`

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
    "traza_id": "a5a1d57e-4d37-49e8-9e58-1c4b773672aa"
  }
}
```

### ENT-10 · Cerrar como entrega parcial · PASA

**Objetivo.** Devolver al inventario lo que no se entregó.

**Petición.** `POST http://entregas:5105/api/v1/entregas/130/resultado`

```http
Accept: application/json
X-Traza-Id: 9b2a51f5-4303-49b1-bb2d-d8f3197f2c3a
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
      "pedido_detalle_id": 685,
      "cantidad_entregada": 3,
      "cantidad_devuelta": 0
    },
    {
      "pedido_detalle_id": 686,
      "cantidad_entregada": 0,
      "cantidad_devuelta": 3,
      "motivo": "El cliente la rechazó."
    }
  ],
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611
  },
  "evidencia_ids": [
    "6ad6c46d86a22ebc8612b589"
  ],
  "capturado_en": "2026-10-20T01:31:25+00:00",
  "id_cliente_local": "dcf00411-2396-4f16-a9b9-671290a5b8d4"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 150 ms · traza `9b2a51f5-4303-49b1-bb2d-d8f3197f2c3a`

```json
{
  "entrega_id": 130,
  "pedido_id": 154,
  "estado_pedido": "entrega_parcial",
  "cerrado_en": "2026-10-19T19:31:26-06:00",
  "duplicado": false
}
```

**Explicación.** fn_devolver_inventario (la misma función que usa el web) regresa las unidades devueltas.

**Evidencia en PostgreSQL.** `SELECT entrega_id, pedido_detalle_id, cantidad_entregada, cantidad_devuelta, motivo FROM entrega_linea WHERE entrega_id = %s`

```json
[
  {
    "entrega_id": 130,
    "pedido_detalle_id": 685,
    "cantidad_entregada": 3,
    "cantidad_devuelta": 0,
    "motivo": null
  },
  {
    "entrega_id": 130,
    "pedido_detalle_id": 686,
    "cantidad_entregada": 0,
    "cantidad_devuelta": 3,
    "motivo": "El cliente la rechazó."
  }
]
```

**Evidencia en PostgreSQL.** `SELECT tipo, producto_id, cantidad, existencia_resultante, motivo FROM movimiento_inventario WHERE referencia_id = %s AND tipo = 'devolucion_parcial'`

```json
[
  {
    "tipo": "devolucion_parcial",
    "producto_id": 12,
    "cantidad": 3,
    "existencia_resultante": 14,
    "motivo": "Entrega parcial: regresan las unidades devueltas (RN28)."
  }
]
```

### ENT-11 · Entregas de un pedido (administrador) · PASA

**Objetivo.** Consulta por pedido para el portal web.

**Petición.** `GET http://entregas:5105/api/v1/entregas?pedido_id=153`

```http
Accept: application/json
X-Traza-Id: 51123161-9a7f-4483-be48-42494d3e537a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 64 ms · traza `51123161-9a7f-4483-be48-42494d3e537a`

```json
{
  "datos": [
    {
      "id": 129,
      "pedido_id": 153,
      "folio": "PED-20261020-000153",
      "estado_pedido": "entregado",
      "orden_parada": 1,
      "direccion": "Fidel Velázquez 2470, Valles de San Bernabé",
      "zona": "Valles de San Bernabé",
      "distancia_km": 0.23,
      "minutos_estimados": 10.0,
      "total": 148.0
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
X-Traza-Id: 9aabdf93-8104-4dc8-b300-0f40d0ff9da1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 184 ms · traza `9aabdf93-8104-4dc8-b300-0f40d0ff9da1`

```xml
<?xml version='1.0' encoding='utf-8'?>
<candidatos xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><datos><candidato><id>1</id><clave>CAND-01</clave><nombre>San Bernabé Norte</nombre><latitud>25.752</latitud><longitud>-100.361</longitud><renta_estimada>18000.00</renta_estimada><nomina_estimada>42000.00</nomina_estimada><servicios_estimados>7000.00</servicios_estimados><otros_costos>5000.00</otros_costos><costo_fijo>72000.00</costo_fijo><superficie_m2>130</superficie_m2><capacidad_fisica>150</capacidad_fisica><accesibilidad_vial>9</accesibilidad_vial><zona_id>1</zona_id><poblacion_cubierta>8420</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato><candidato><id>2</id><clave>CAND-02</clave><nombre>Valles Poniente</nombre><latitud>25.7555</latitud><longitud>-100.376</longitud><renta_estimada>15500.00</renta_estimada><nomina_estimada>42000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><costo_fijo>68500.00</costo_fijo><superficie_m2>105</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>2</zona_id><poblacion_cubierta>6180</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato><candidato><id>3</id><clave>CAND-05</clave><nombre>Alianza Real</nombre><latitud>25.7625</latitud><longitud>-100.353</longitud><renta_estimada>21000.00</renta_estimada><nomina_estimada>46000.00</nomina_estimada><servicios_estimados>8000.00</servicios_estimados><otros_costos>6000.00</otros_costos><costo_fijo>81000.00</costo_fijo><superficie_m2>150</superficie_m2><capacidad_fisica>180</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>3900</poblacion_cubierta><radio_km>1.6</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>5</total><paginas>2</paginas></paginacion></candidatos>
```

### PLA-02 · Registrar candidato (XML) · PASA

**Objetivo.** Alta con costo fijo calculado por PostgreSQL.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos`

```http
Accept: application/xml
X-Traza-Id: 347dfc82-98d9-42e5-a859-faed5f86c407
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><candidato_nuevo xmlns="urn:microhubs:v1"><clave>********</clave><nombre>Alianza Norte</nombre><latitud>25.7601</latitud><longitud>-100.3555</longitud><renta_estimada>16000.00</renta_estimada><nomina_estimada>40000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><superficie_m2>110</superficie_m2><capacidad_fisica>130</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km></candidato_nuevo>
```

**Respuesta.** HTTP 201 (esperado 201) · 88 ms · traza `347dfc82-98d9-42e5-a859-faed5f86c407`

```xml
<?xml version='1.0' encoding='utf-8'?>
<candidato xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>16</id><clave>EV-C9885A</clave><nombre>Alianza Norte</nombre><latitud>25.7601</latitud><longitud>-100.3555</longitud><renta_estimada>16000.00</renta_estimada><nomina_estimada>40000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><costo_fijo>67000.00</costo_fijo><superficie_m2>110</superficie_m2><capacidad_fisica>130</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato>
```

**Evidencia en PostgreSQL.** `SELECT id, clave, nombre, renta_estimada, costo_fijo, decision FROM ubicacion_candidata WHERE clave = %s`

```json
[
  {
    "id": 16,
    "clave": "EV-C9885A",
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
X-Traza-Id: beba1cc4-6582-4456-8d65-8373358c6c3a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><candidato_nuevo xmlns="urn:microhubs:v1"><clave>********</clave><nombre>Alianza Norte</nombre><latitud>25.7601</latitud><longitud>-100.3555</longitud><renta_estimada>16000.00</renta_estimada><nomina_estimada>40000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><superficie_m2>110</superficie_m2><capacidad_fisica>130</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km></candidato_nuevo>
```

**Respuesta.** HTTP 409 (esperado 409) · 64 ms · traza `beba1cc4-6582-4456-8d65-8373358c6c3a`

```xml
<?xml version='1.0' encoding='utf-8'?>
<error xmlns="urn:microhubs:v1" version="1"><codigo>CONFLICTO</codigo><mensaje>Ya existe un registro con esos datos.</mensaje><traza_id>beba1cc4-6582-4456-8d65-8373358c6c3a</traza_id></error>
```

### PLA-04 · Modificar candidato (PUT) · PASA

**Objetivo.** Cambiar la renta recalcula el costo fijo.

**Petición.** `PUT http://planeacion:5106/api/v1/candidatos/16`

```http
Accept: application/json
X-Traza-Id: 6d57de86-b7ac-42e5-9158-435d65968400
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

**Respuesta.** HTTP 200 (esperado 200) · 79 ms · traza `6d57de86-b7ac-42e5-9158-435d65968400`

```json
{
  "id": 16,
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

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/16/simular`

```http
Accept: application/xml
X-Traza-Id: 43a4b1b3-7fad-46dc-8a1e-29fc28ed7e04
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<simular xmlns="urn:microhubs:v1"/>
```

**Respuesta.** HTTP 200 (esperado 200) · 261 ms · traza `43a4b1b3-7fad-46dc-8a1e-29fc28ed7e04`

```xml
<?xml version='1.0' encoding='utf-8'?>
<resultados xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><atendidos>0</atendidos><rechazados>0</rechazados><utilizacion>0</utilizacion><nivel>estable</nivel><tiempo_estimado_min>18.6</tiempo_estimado_min><operadores_requeridos>0</operadores_requeridos><repartidores_requeridos>0</repartidores_requeridos><ingreso_dia>0.00</ingreso_dia><margen_dia>-2300.00</margen_dia><costo_por_pedido xsi:nil="true" /><equilibrio><margen_pedido>23.98</margen_pedido><mensual>2877.7</mensual><diario>95.9</diario></equilibrio><decision>NO VIABLE CON LOS SUPUESTOS ACTUALES</decision><explicacion><motivo>la demanda atendida (0/día) no alcanza el equilibrio (96/día)</motivo><motivo>reducir costos fijos, aumentar ticket o buscar una ubicación con más demanda</motivo></explicacion></resultados>
```

**Explicación.** Usa planeacion_calc.py (las mismas fórmulas del web) y guarda la ejecución en MongoDB.

**Evidencia en MongoDB.** `db.ejecuciones_analiticas.find().sort({ejecutado_en: -1}).limit(1)`

```json
{
  "escenario_id": "candidato-16",
  "nombre_escenario": "Candidato 16",
  "tipo_analisis": "punto_equilibrio",
  "ejecutado_en": "2026-10-20 01:31:27.771000+00:00",
  "usuario_id": 5,
  "version_modelo": "planeacion_calc 2.1",
  "parametros_entrada": {
    "demanda_diaria": 0.0,
    "operadores": 3.0,
    "repartidores": 3.0,
    "ticket": 149.92,
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
    "ticket = 149.92",
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
    "equilibrio_diario": 95.9,
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

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/16/decision`

```http
Accept: application/json
X-Traza-Id: c0d9ddf2-3921-4389-b55f-ce8ae3b4b38b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aceptado",
  "motivo": "ok"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 28 ms · traza `c0d9ddf2-3921-4389-b55f-ce8ae3b4b38b`

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
    "traza_id": "c0d9ddf2-3921-4389-b55f-ce8ae3b4b38b"
  }
}
```

### PLA-07 · Decisión humana de apertura · PASA

**Objetivo.** Registrar la decisión con motivo.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/16/decision`

```http
Accept: application/json
X-Traza-Id: e8df83de-3d0d-4406-89de-3809344d3500
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "condicionado",
  "motivo": "Renegociar la renta antes de firmar."
}
```

**Respuesta.** HTTP 200 (esperado 200) · 56 ms · traza `e8df83de-3d0d-4406-89de-3809344d3500`

```json
{
  "id": 16,
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
    "id": 16,
    "decision": "condicionado",
    "decision_motivo": "Renegociar la renta antes de firmar.",
    "decision_por": 5,
    "decision_en": "2026-10-20 01:31:27.843865+00:00"
  }
]
```

### PLA-08 · Simulación libre: Escenario A · PASA

**Objetivo.** Punto de equilibrio del caso de la retroalimentación.

**Petición.** `POST http://planeacion:5106/api/v1/simulaciones`

```http
Accept: application/json
X-Traza-Id: e3f71512-b249-4f60-9b68-324c92e78b11
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

**Respuesta.** HTTP 200 (esperado 200) · 32 ms · traza `e3f71512-b249-4f60-9b68-324c92e78b11`

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
X-Traza-Id: 12a947da-c4e1-4ec1-a589-339e281517db
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Escenario A - evidencias",
  "candidato_id": 16,
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

**Respuesta.** HTTP 201 (esperado 201) · 119 ms · traza `12a947da-c4e1-4ec1-a589-339e281517db`

```json
{
  "id": 1,
  "nombre": "Escenario A - evidencias",
  "candidato_id": 16,
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
  "creado_en": "2026-10-19T19:31:27-06:00"
}
```

### PLA-10 · Abrir escenario (XML) · PASA

**Objetivo.** Escenario con supuestos y resultados.

**Petición.** `GET http://planeacion:5106/api/v1/escenarios/1`

```http
Accept: application/xml
X-Traza-Id: 1cad6a91-d62b-46be-bc67-d125c59f1805
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 27 ms · traza `1cad6a91-d62b-46be-bc67-d125c59f1805`

```xml
<?xml version='1.0' encoding='utf-8'?>
<escenario xmlns="urn:microhubs:v1" version="1"><id>1</id><nombre>Escenario A - evidencias</nombre><candidato_id>16</candidato_id><supuestos><demanda_diaria>120</demanda_diaria><operadores>3</operadores><repartidores>4</repartidores><ticket>135.00</ticket><costo_entrega>22.00</costo_entrega><margen_bruto>0.28</margen_bruto><renta>18000.00</renta><nomina>42000.00</nomina><servicios>7000.00</servicios><otros>5000.00</otros><distancia_km>2.4</distancia_km><capacidad_fisica>150</capacidad_fisica></supuestos><resultados><atendidos>120</atendidos><rechazados>0</rechazados><utilizacion>80</utilizacion><nivel>atencion</nivel><tiempo_estimado_min>19.4</tiempo_estimado_min><operadores_requeridos>3</operadores_requeridos><repartidores_requeridos>2</repartidores_requeridos><ingreso_dia>16200.00</ingreso_dia><margen_dia>-504.00</margen_dia><costo_por_pedido>42.00</costo_por_pedido><equilibrio><margen_pedido>15.80</margen_pedido><mensual>4557</mensual><diario>151.9</diario></equilibrio><decision>NO VIABLE CON LOS SUPUESTOS ACTUALES</decision><explicacion><motivo>la demanda atendida (120/día) no alcanza el equilibrio (152/día)</motivo><motivo>el espacio físico del local limita la capacidad</motivo><motivo>reducir costos fijos, aumentar ticket o buscar una ubicación con más demanda</motivo></explicacion></resultados><creado_en>2026-10-19T19:31:27-06:00</creado_en></escenario>
```

### PLA-11 · Resumen de simulaciones · PASA

**Objetivo.** Agregación $group en MongoDB por decisión.

**Petición.** `GET http://planeacion:5106/api/v1/simulaciones/resumen`

```http
Accept: application/json
X-Traza-Id: dfaffd48-4630-4c95-b0e2-8b7798867a15
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 8 ms · traza `dfaffd48-4630-4c95-b0e2-8b7798867a15`

```json
{
  "total": 3,
  "por_decision": [
    {
      "decision": "NO VIABLE CON LOS SUPUESTOS ACTUALES",
      "cantidad": 3,
      "utilizacion_promedio": 53.3
    }
  ]
}
```

**Evidencia en MongoDB.** `db.ejecuciones_analiticas.aggregate([{$match:{tipo_analisis:'punto_equilibrio'}}, {$group:{_id:'$resultados.decision', cantidad:{$sum:1}, utilizacion_promedio:{$avg:'$resultados.utilizacion'}}}])`

```json
[
  {
    "_id": "NO VIABLE CON LOS SUPUESTOS ACTUALES",
    "cantidad": 3,
    "utilizacion_promedio": 53.333333333333336
  }
]
```

### PLA-12 · Auditor intenta registrar · PASA

**Objetivo.** El auditor solo consulta (RN-E01).

**Petición.** `POST http://planeacion:5106/api/v1/candidatos`

```http
Accept: application/json
X-Traza-Id: 184716ae-6d9a-4d3f-90c2-5ab1046b95c3
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

**Respuesta.** HTTP 403 (esperado 403) · 66 ms · traza `184716ae-6d9a-4d3f-90c2-5ab1046b95c3`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "184716ae-6d9a-4d3f-90c2-5ab1046b95c3"
  }
}
```

### PLA-13 · Auditor intenta simular · PASA

**Objetivo.** Sin simulacion.ejecutar.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/16/simular`

```http
Accept: application/json
X-Traza-Id: 0423614e-66d1-4190-824d-abc05c1d084b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 403 (esperado 403) · 28 ms · traza `0423614e-66d1-4190-824d-abc05c1d084b`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "0423614e-66d1-4190-824d-abc05c1d084b"
  }
}
```

### PLA-14 · Eliminar escenario (DELETE) · PASA

**Objetivo.** Borrar un escenario.

**Petición.** `DELETE http://planeacion:5106/api/v1/escenarios/1`

```http
Accept: application/json
X-Traza-Id: 1e6f3adb-052e-4d2a-b0f5-8c3e93afa3da
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 35 ms · traza `1e6f3adb-052e-4d2a-b0f5-8c3e93afa3da`

```json
(sin cuerpo)
```

### PLA-15 · Dar de baja candidato (DELETE) · PASA

**Objetivo.** Baja lógica: se conserva su historia.

**Petición.** `DELETE http://planeacion:5106/api/v1/candidatos/16`

```http
Accept: application/json
X-Traza-Id: cd6d5065-6455-4d12-9621-d787af30a1da
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 67 ms · traza `cd6d5065-6455-4d12-9621-d787af30a1da`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT id, clave, estatus, decision FROM ubicacion_candidata WHERE id = %s`

```json
[
  {
    "id": 16,
    "clave": "EV-C9885A",
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
X-Traza-Id: 17a9a81b-542d-4852-9cbd-3fed55f5f26e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 26 ms · traza `17a9a81b-542d-4852-9cbd-3fed55f5f26e`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el candidato.",
    "traza_id": "17a9a81b-542d-4852-9cbd-3fed55f5f26e"
  }
}
```

## Servicio inventario · puerto 5111

### INV-01 · Existencias por microhub · PASA

**Objetivo.** Existencia física, reservada y disponible de cada producto.

**Petición.** `GET http://inventario:5111/api/v1/inventario?por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 4df674d0-ac51-4dbd-a587-37428af5674e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 457 ms · traza `4df674d0-ac51-4dbd-a587-37428af5674e`

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
      "existencia": 60,
      "minimo": 10,
      "reservado": 0,
      "disponible": 60,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 35,
      "minimo": 10,
      "reservado": 0,
      "disponible": 35,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
    "unidades": 6855,
    "reservado": 0
  }
]
```

### INV-02 · Existencias (XML) · PASA

**Objetivo.** La app de escritorio recibe XML que cumple inventario.xsd.

**Petición.** `GET http://inventario:5111/api/v1/inventario?por_pagina=3`

```http
Accept: application/xml
X-Traza-Id: b5702be2-9c85-4782-9bc1-d957d9d8715a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 54 ms · traza `b5702be2-9c85-4782-9bc1-d957d9d8715a`

```xml
<?xml version='1.0' encoding='utf-8'?>
<existencias xmlns="urn:microhubs:v1" version="1"><datos><existencia><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><producto><id>1</id><clave_interna>AB-001</clave_interna><nombre>Frijol negro a granel</nombre></producto><existencia>60</existencia><minimo>10</minimo><reservado>0</reservado><disponible>60</disponible><estado>normal</estado><actualizado_en>2026-10-19T19:30:41-06:00</actualizado_en></existencia><existencia><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><producto><id>2</id><clave_interna>AB-002</clave_interna><nombre>Arroz superextra</nombre></producto><existencia>35</existencia><minimo>10</minimo><reservado>0</reservado><disponible>35</disponible><estado>normal</estado><actualizado_en>2026-10-19T19:30:41-06:00</actualizado_en></existencia><existencia><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><producto><id>3</id><clave_interna>AB-003</clave_interna><nombre>Aceite vegetal</nombre></producto><existencia>10</existencia><minimo>5</minimo><reservado>0</reservado><disponible>10</disponible><estado>normal</estado><actualizado_en>2026-10-19T19:30:41-06:00</actualizado_en></existencia></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>153</total><paginas>51</paginas></paginacion></existencias>
```

### INV-03 · Filtro de estado inválido · PASA

**Objetivo.** Un filtro desconocido se rechaza.

**Petición.** `GET http://inventario:5111/api/v1/inventario?estado=inventado`

```http
Accept: application/json
X-Traza-Id: 2b6d945b-5274-4448-b174-2c8a019a06df
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 8 ms · traza `2b6d945b-5274-4448-b174-2c8a019a06df`

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
    "traza_id": "2b6d945b-5274-4448-b174-2c8a019a06df"
  }
}
```

### INV-04 · El operador ve solo su microhub · PASA

**Objetivo.** Ámbito por microhub del perfil operador.

**Petición.** `GET http://inventario:5111/api/v1/inventario?por_pagina=100`

```http
Accept: application/json
X-Traza-Id: f746c0a0-12e8-405b-af1b-4d0d10b165b9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 59 ms · traza `f746c0a0-12e8-405b-af1b-4d0d10b165b9`

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
      "existencia": 60,
      "minimo": 10,
      "reservado": 0,
      "disponible": 60,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 35,
      "minimo": 10,
      "reservado": 0,
      "disponible": 35,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 56,
      "minimo": 10,
      "reservado": 0,
      "disponible": 56,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 20,
      "minimo": 10,
      "reservado": 0,
      "disponible": 20,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 49,
      "minimo": 10,
      "reservado": 0,
      "disponible": 49,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 33,
      "minimo": 10,
      "reservado": 0,
      "disponible": 33,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 80,
      "minimo": 8,
      "reservado": 0,
      "disponible": 80,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 10,
      "minimo": 8,
      "reservado": 0,
      "disponible": 10,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 81,
      "minimo": 5,
      "reservado": 0,
      "disponible": 81,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 40,
      "minimo": 5,
      "reservado": 0,
      "disponible": 40,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 82,
      "minimo": 5,
      "reservado": 0,
      "disponible": 82,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 19,
      "minimo": 10,
      "reservado": 0,
      "disponible": 19,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 87,
      "minimo": 10,
      "reservado": 0,
      "disponible": 87,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 42,
      "minimo": 5,
      "reservado": 0,
      "disponible": 42,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 15,
      "minimo": 5,
      "reservado": 0,
      "disponible": 15,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 57,
      "minimo": 5,
      "reservado": 0,
      "disponible": 57,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 85,
      "minimo": 5,
      "reservado": 0,
      "disponible": 85,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 13,
      "minimo": 8,
      "reservado": 0,
      "disponible": 13,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 15,
      "minimo": 5,
      "reservado": 0,
      "disponible": 15,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 50,
      "minimo": 10,
      "reservado": 0,
      "disponible": 50,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 16,
      "minimo": 8,
      "reservado": 0,
      "disponible": 16,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 68,
      "minimo": 8,
      "reservado": 0,
      "disponible": 68,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 73,
      "minimo": 5,
      "reservado": 0,
      "disponible": 73,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 28,
      "minimo": 5,
      "reservado": 0,
      "disponible": 28,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 46,
      "minimo": 10,
      "reservado": 0,
      "disponible": 46,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 62,
      "minimo": 10,
      "reservado": 0,
      "disponible": 62,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 80,
      "minimo": 10,
      "reservado": 0,
      "disponible": 80,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "existencia": 78,
      "minimo": 8,
      "reservado": 0,
      "disponible": 78,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
      "actualizado_en": "2026-10-19T19:30:41-06:00"
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
X-Traza-Id: 7a2d7710-1d9c-40f9-831d-150d381ae7c2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 7 ms · traza `7a2d7710-1d9c-40f9-831d-150d381ae7c2`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "7a2d7710-1d9c-40f9-831d-150d381ae7c2"
  }
}
```

### INV-06 · Una existencia · PASA

**Objetivo.** Existencia, apartado y disponible de un producto en un microhub.

**Petición.** `GET http://inventario:5111/api/v1/inventario/1/6`

```http
Accept: application/json
X-Traza-Id: 368cfc53-30c9-4c5b-be41-5a138d1fb901
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 33 ms · traza `368cfc53-30c9-4c5b-be41-5a138d1fb901`

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
  "existencia": 56,
  "minimo": 10,
  "reservado": 0,
  "disponible": 56,
  "estado": "normal",
  "actualizado_en": "2026-10-19T19:30:41-06:00"
}
```

### INV-07 · Recibir mercancía · PASA

**Objetivo.** Suma al inventario y deja el movimiento con la referencia.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: cc26a2ae-c70e-4ca2-9df0-15ddc8e2e951
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
  "operacion_uuid": "4aabfe72-961b-4918-8f95-eb3fd76b95e1",
  "referencia": {
    "tipo": "orden_compra",
    "id": "1"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 88 ms · traza `cc26a2ae-c70e-4ca2-9df0-15ddc8e2e951`

```json
{
  "movimiento": {
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
  "duplicado": false
}
```

**Explicación.** Bloquea la fila del inventario, suma, y guarda el movimiento con la existencia resultante. La operacion_uuid hace el movimiento idempotente.

**Evidencia en PostgreSQL.** `SELECT id, tipo, cantidad, existencia_resultante, referencia_tipo, referencia_id, operacion_uuid FROM movimiento_inventario WHERE operacion_uuid = %s`

```json
[
  {
    "id": 898,
    "tipo": "recepcion",
    "cantidad": 5,
    "existencia_resultante": 61,
    "referencia_tipo": "orden_compra",
    "referencia_id": 1,
    "operacion_uuid": "4aabfe72-961b-4918-8f95-eb3fd76b95e1"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT existencia FROM inventario WHERE microhub_id = %s AND producto_id = %s`

```json
[
  {
    "existencia": 61
  }
]
```

### INV-08 · Reintento con la misma operación · PASA

**Objetivo.** Idempotencia: la misma entrada no se aplica dos veces.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: 89fc5c02-7e0b-4be8-af99-e351325cc1dc
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
  "operacion_uuid": "4aabfe72-961b-4918-8f95-eb3fd76b95e1",
  "referencia": {
    "tipo": "orden_compra",
    "id": "1"
  }
}
```

**Respuesta.** HTTP 200 (esperado 200) · 30 ms · traza `89fc5c02-7e0b-4be8-af99-e351325cc1dc`

```json
{
  "movimiento": {
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
    "existencia": 61
  }
]
```

### INV-09 · Ajuste sin motivo · PASA

**Objetivo.** Un ajuste, merma o conteo necesita el motivo.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: f811d14a-07f1-44b8-ab1e-7d5cd2faef36
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

**Respuesta.** HTTP 422 (esperado 422) · 8 ms · traza `f811d14a-07f1-44b8-ab1e-7d5cd2faef36`

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
    "traza_id": "f811d14a-07f1-44b8-ab1e-7d5cd2faef36"
  }
}
```

### INV-10 · Ajuste grande por un operador · PASA

**Objetivo.** Más de 25 unidades lo autoriza un administrador.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: 12047dfc-fb1f-43a0-864f-2fa704c1cafa
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

**Respuesta.** HTTP 403 (esperado 403) · 157 ms · traza `12047dfc-fb1f-43a0-864f-2fa704c1cafa`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Un movimiento de más de 25 unidades lo autoriza un administrador.",
    "traza_id": "12047dfc-fb1f-43a0-864f-2fa704c1cafa"
  }
}
```

**Explicación.** El umbral viene de configuracion.umbral_ajuste_inventario, no de una constante en el código.

### INV-11 · Ajuste grande por un administrador · PASA

**Objetivo.** El administrador sí puede.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: a7e7cf8d-95dc-4892-a488-47aa48f91829
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

**Respuesta.** HTTP 201 (esperado 201) · 67 ms · traza `a7e7cf8d-95dc-4892-a488-47aa48f91829`

```json
{
  "movimiento": {
    "id": 899,
    "microhub_id": 1,
    "producto_id": 6,
    "tipo": "ajuste",
    "cantidad": 30,
    "existencia_resultante": 91,
    "referencia": null,
    "motivo": "Ajuste grande de prueba",
    "usuario_id": 1,
    "fecha": "2026-10-19T19:31:31-06:00"
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
    "existencia_resultante": 91,
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
X-Traza-Id: 65d2f24e-2866-48f2-867d-43ba44f1a33f
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
  "operacion_uuid": "7a4a411a-1ff4-4e00-8581-4cc460db4c6d"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 109 ms · traza `65d2f24e-2866-48f2-867d-43ba44f1a33f`

```json
{
  "producto_id": 7,
  "cantidad": 2,
  "duplicado": false,
  "origen": {
    "microhub_id": 1,
    "existencia": 18,
    "movimiento_id": 902
  },
  "destino": {
    "microhub_id": 2,
    "existencia": 82,
    "movimiento_id": 903
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
    "existencia_resultante": 18,
    "referencia_tipo": "transferencia",
    "referencia_id": 2
  },
  {
    "microhub_id": 2,
    "tipo": "transferencia_entrada",
    "cantidad": 2,
    "existencia_resultante": 82,
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
X-Traza-Id: d6c2d150-9f32-403a-9f45-4aed48bc2790
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "origen_microhub_id": 1,
  "destino_microhub_id": 2,
  "producto_id": 7,
  "cantidad": 1020,
  "motivo": "El microhub 2 se quedó sin producto",
  "operacion_uuid": "dd04e2e4-911a-4915-abbb-91058ad696b7"
}
```

**Respuesta.** HTTP 409 (esperado 409) · 78 ms · traza `d6c2d150-9f32-403a-9f45-4aed48bc2790`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "En el microhub de origen hay 18 disponibles y se piden 1020.",
    "traza_id": "d6c2d150-9f32-403a-9f45-4aed48bc2790"
  }
}
```

### INV-14 · Apartar existencia · PASA

**Objetivo.** Una reserva resta de lo disponible sin tocar la existencia física.

**Petición.** `POST http://inventario:5111/api/v1/inventario/reservas`

```http
Accept: application/json
X-Traza-Id: 5c751d75-e031-49a7-a4f9-f3f8e5577372
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
    "id": "evidencia-1c83ea"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 101 ms · traza `5c751d75-e031-49a7-a4f9-f3f8e5577372`

```json
{
  "id": 1,
  "microhub_id": 1,
  "producto_id": 8,
  "cantidad": 3,
  "estado": "activa",
  "vigente": true,
  "referencia": {
    "tipo": "manual",
    "id": "evidencia-1c83ea"
  },
  "creada_en": "2026-10-19T19:31:32-06:00",
  "vence_en": "2026-10-19T20:01:32-06:00",
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
X-Traza-Id: fd327334-2bb5-47dd-ae54-8b0f666c3c12
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
    "id": "evidencia-1c83ea"
  }
}
```

**Respuesta.** HTTP 409 (esperado 409) · 68 ms · traza `fd327334-2bb5-47dd-ae54-8b0f666c3c12`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "No hay existencia disponible: hay 18 sin apartar y se piden 121.",
    "traza_id": "fd327334-2bb5-47dd-ae54-8b0f666c3c12"
  }
}
```

### INV-16 · Reservas activas · PASA

**Objetivo.** Filtro por producto, estado y referencia.

**Petición.** `GET http://inventario:5111/api/v1/inventario/reservas?producto_id=8&estado=activa&referencia_id=evidencia-1c83ea`

```http
Accept: application/json
X-Traza-Id: 0bd73e2d-a545-43cb-8dc5-f233e7320dfd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 66 ms · traza `0bd73e2d-a545-43cb-8dc5-f233e7320dfd`

```json
{
  "datos": [
    {
      "id": 1,
      "microhub_id": 1,
      "producto_id": 8,
      "cantidad": 3,
      "estado": "activa",
      "vigente": true,
      "referencia": {
        "tipo": "manual",
        "id": "evidencia-1c83ea"
      },
      "creada_en": "2026-10-19T19:31:32-06:00",
      "vence_en": "2026-10-19T20:01:32-06:00",
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

**Petición.** `POST http://inventario:5111/api/v1/inventario/reservas/1/liberar`

```http
Accept: application/json
X-Traza-Id: 0fd18d8b-ac20-4f06-bcec-4c93b24130af
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 85 ms · traza `0fd18d8b-ac20-4f06-bcec-4c93b24130af`

```json
{
  "id": 1,
  "microhub_id": 1,
  "producto_id": 8,
  "cantidad": 3,
  "estado": "liberada",
  "vigente": false,
  "referencia": {
    "tipo": "manual",
    "id": "evidencia-1c83ea"
  },
  "creada_en": "2026-10-19T19:31:32-06:00",
  "vence_en": "2026-10-19T20:01:32-06:00",
  "cerrada_en": "2026-10-19T19:31:32-06:00"
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
X-Traza-Id: 41d82531-623b-4c6a-aa31-b7a3ea13861d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "minimo": 41
}
```

**Respuesta.** HTTP 200 (esperado 200) · 82 ms · traza `41d82531-623b-4c6a-aa31-b7a3ea13861d`

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
  "actualizado_en": "2026-10-19T19:31:32-06:00"
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
X-Traza-Id: ab7b1257-49e5-4e5f-9743-c3a18a7cc848
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "minimo": 41
}
```

**Respuesta.** HTTP 200 (esperado 200) · 92 ms · traza `ab7b1257-49e5-4e5f-9743-c3a18a7cc848`

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
  "actualizado_en": "2026-10-19T19:31:32-06:00"
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
      "actualizado_en": "2026-10-20T01:31:32.734262+00:00"
    }
  }
]
```

### INV-19 · El operador intenta cambiar el mínimo · PASA

**Objetivo.** Sin inventario.ajuste.

**Petición.** `PATCH http://inventario:5111/api/v1/inventario/1/9/minimo`

```http
Accept: application/json
X-Traza-Id: 4c715c14-6c2c-4631-96ff-8e9c93967399
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "minimo": 1
}
```

**Respuesta.** HTTP 403 (esperado 403) · 42 ms · traza `4c715c14-6c2c-4631-96ff-8e9c93967399`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "4c715c14-6c2c-4631-96ff-8e9c93967399"
  }
}
```

### INV-20 · Una merma cruza el mínimo · PASA

**Objetivo.** El trigger avisa del faltante al operador y al administrador.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: 6e885d34-ecf9-4d95-97c3-49439345a6b5
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

**Respuesta.** HTTP 201 (esperado 201) · 83 ms · traza `6e885d34-ecf9-4d95-97c3-49439345a6b5`

```json
{
  "movimiento": {
    "id": 906,
    "microhub_id": 1,
    "producto_id": 9,
    "tipo": "merma",
    "cantidad": -2,
    "existencia_resultante": 40,
    "referencia": null,
    "motivo": "Se rompieron dos",
    "usuario_id": 1,
    "fecha": "2026-10-19T19:31:32-06:00"
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
X-Traza-Id: 3d2b0c2e-8c34-4136-a70d-7437125daf2b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 75 ms · traza `3d2b0c2e-8c34-4136-a70d-7437125daf2b`

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
X-Traza-Id: 7d2670d8-07d1-4abf-a0f7-5c317784bf07
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 49 ms · traza `7d2670d8-07d1-4abf-a0f7-5c317784bf07`

```json
{
  "datos": [
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
    "total": 2,
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
X-Traza-Id: 6223809d-6336-4cf3-8271-f27aae2aff0e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "rol": "operador",
  "microhub_id": 1,
  "tipo": "sistema",
  "titulo": "Evidencia 979193",
  "mensaje": "Aviso de prueba para el microhub 1",
  "referencia": {
    "tipo": "sistema",
    "id": "evidencia"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 177 ms · traza `6223809d-6336-4cf3-8271-f27aae2aff0e`

```json
{
  "enviadas": 1,
  "omitidas": 0,
  "ids": [
    7
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
    "titulo": "Evidencia 979193",
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
X-Traza-Id: e290fa25-21b2-4fe8-be57-227d0ee86f9f
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

**Respuesta.** HTTP 403 (esperado 403) · 27 ms · traza `e290fa25-21b2-4fe8-be57-227d0ee86f9f`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "e290fa25-21b2-4fe8-be57-227d0ee86f9f"
  }
}
```

### NOT-03 · Destino inexistente · PASA

**Objetivo.** Un rol sin personas activas se rechaza.

**Petición.** `POST http://notificaciones:5124/api/v1/notificaciones`

```http
Accept: application/json
X-Traza-Id: fbc194d8-adb7-4360-b610-4cba9924f2ba
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

**Respuesta.** HTTP 422 (esperado 422) · 31 ms · traza `fbc194d8-adb7-4360-b610-4cba9924f2ba`

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
    "traza_id": "fbc194d8-adb7-4360-b610-4cba9924f2ba"
  }
}
```

### NOT-04 · Mi bandeja · PASA

**Objetivo.** Los avisos de la persona, el más reciente primero.

**Petición.** `GET http://notificaciones:5124/api/v1/notificaciones?solo_no_leidas=true&por_pagina=20`

```http
Accept: application/json
X-Traza-Id: b03b80ec-e1f0-429c-9b97-87b17d9b2484
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 41 ms · traza `b03b80ec-e1f0-429c-9b97-87b17d9b2484`

```json
{
  "datos": [
    {
      "id": 7,
      "tipo": "sistema",
      "titulo": "Evidencia 979193",
      "mensaje": "Aviso de prueba para el microhub 1",
      "leida": false,
      "referencia": {
        "tipo": "sistema",
        "id": "evidencia"
      },
      "creada_en": "2026-10-19T19:31:33-06:00"
    },
    {
      "id": 5,
      "tipo": "inventario",
      "titulo": "Faltante en Microhub San Bernabé Centro",
      "mensaje": "Atún en agua: quedan 40 (mínimo 41).",
      "leida": false,
      "referencia": {
        "tipo": "producto",
        "id": "9"
      },
      "creada_en": "2026-10-19T19:31:32-06:00"
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

### NOT-05 · Mi bandeja (XML) · PASA

**Objetivo.** Respuesta XML que cumple notificaciones.xsd.

**Petición.** `GET http://notificaciones:5124/api/v1/notificaciones?por_pagina=3`

```http
Accept: application/xml
X-Traza-Id: d2185fc0-329c-40e0-b454-ccf844dcd42c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 42 ms · traza `d2185fc0-329c-40e0-b454-ccf844dcd42c`

```xml
<?xml version='1.0' encoding='utf-8'?>
<notificaciones xmlns="urn:microhubs:v1" version="1"><datos><notificacion><id>7</id><tipo>sistema</tipo><titulo>Evidencia 979193</titulo><mensaje>Aviso de prueba para el microhub 1</mensaje><leida>false</leida><referencia><tipo>sistema</tipo><id>evidencia</id></referencia><creada_en>2026-10-19T19:31:33-06:00</creada_en></notificacion><notificacion><id>5</id><tipo>inventario</tipo><titulo>Faltante en Microhub San Bernabé Centro</titulo><mensaje>Atún en agua: quedan 40 (mínimo 41).</mensaje><leida>false</leida><referencia><tipo>producto</tipo><id>9</id></referencia><creada_en>2026-10-19T19:31:32-06:00</creada_en></notificacion></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>2</total><paginas>1</paginas></paginacion></notificaciones>
```

### NOT-06 · Avisos sin leer · PASA

**Objetivo.** Conteo para la insignia de la app.

**Petición.** `GET http://notificaciones:5124/api/v1/notificaciones/conteo`

```http
Accept: application/json
X-Traza-Id: 0fe8cbba-9db8-40eb-abbd-e945c3189eff
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 24 ms · traza `0fe8cbba-9db8-40eb-abbd-e945c3189eff`

```json
{
  "no_leidas": 2
}
```

### NOT-07 · Confirmar la lectura · PASA

**Objetivo.** El aviso queda leído.

**Petición.** `POST http://notificaciones:5124/api/v1/notificaciones/7/leer`

```http
Accept: application/json
X-Traza-Id: bda9add3-8d66-4da6-ae54-5a21bbd394ed
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 66 ms · traza `bda9add3-8d66-4da6-ae54-5a21bbd394ed`

```json
{
  "id": 7,
  "tipo": "sistema",
  "titulo": "Evidencia 979193",
  "mensaje": "Aviso de prueba para el microhub 1",
  "leida": true,
  "referencia": {
    "tipo": "sistema",
    "id": "evidencia"
  },
  "creada_en": "2026-10-19T19:31:33-06:00"
}
```

**Evidencia en PostgreSQL.** `SELECT id, leido_en IS NOT NULL AS leido FROM web_notificacion WHERE id = %s`

```json
[
  {
    "id": 7,
    "leido": true
  }
]
```

### NOT-08 · Leído por otra persona · PASA

**Objetivo.** Un aviso ajeno no se puede marcar.

**Petición.** `POST http://notificaciones:5124/api/v1/notificaciones/7/leer`

```http
Accept: application/json
X-Traza-Id: 23029418-132e-4d0f-88a1-43cb171969c0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 26 ms · traza `23029418-132e-4d0f-88a1-43cb171969c0`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe ese aviso en tu bandeja.",
    "traza_id": "23029418-132e-4d0f-88a1-43cb171969c0"
  }
}
```

### NOT-09 · Marcar todos como leídos · PASA

**Objetivo.** Confirma la lectura de todos los pendientes.

**Petición.** `POST http://notificaciones:5124/api/v1/notificaciones/leer-todas`

```http
Accept: application/json
X-Traza-Id: cc93eda1-253e-4cd2-be9b-c5203745112f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 62 ms · traza `cc93eda1-253e-4cd2-be9b-c5203745112f`

```json
{
  "marcadas": 1
}
```

### NOT-10 · Mis preferencias · PASA

**Objetivo.** Qué tipos de aviso recibe la persona.

**Petición.** `GET http://notificaciones:5124/api/v1/notificaciones/preferencias`

```http
Accept: application/json
X-Traza-Id: c7c65a9b-26e1-4f71-926c-d1eb9fe6ac43
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 23 ms · traza `c7c65a9b-26e1-4f71-926c-d1eb9fe6ac43`

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
X-Traza-Id: 4b402a0a-5035-4218-af52-17c975611fd1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "activa": false
}
```

**Respuesta.** HTTP 200 (esperado 200) · 69 ms · traza `4b402a0a-5035-4218-af52-17c975611fd1`

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
X-Traza-Id: ea7f0813-f837-4c7a-84f0-62e26206ce73
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "rol": "operador",
  "microhub_id": 1,
  "tipo": "inventario",
  "titulo": "Evidencia 979193",
  "mensaje": "Faltante de prueba"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 36 ms · traza `ea7f0813-f837-4c7a-84f0-62e26206ce73`

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
X-Traza-Id: 60e5db82-8f4f-4823-ada7-14867737cd41
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "activa": false
}
```

**Respuesta.** HTTP 409 (esperado 409) · 8 ms · traza `60e5db82-8f4f-4823-ada7-14867737cd41`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Los avisos del sistema no se pueden apagar.",
    "traza_id": "60e5db82-8f4f-4823-ada7-14867737cd41"
  }
}
```

### NOT-14 · Borrar un aviso · PASA

**Objetivo.** Quita el aviso de la bandeja propia.

**Petición.** `DELETE http://notificaciones:5124/api/v1/notificaciones/7`

```http
Accept: application/json
X-Traza-Id: f5fee72f-636b-4dbb-8bd6-4ffcb7efc6e3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 28 ms · traza `f5fee72f-636b-4dbb-8bd6-4ffcb7efc6e3`

```json
(sin cuerpo)
```

## Servicio proveedores · puerto 5113

### PRV-01 · Proveedores · PASA

**Objetivo.** Lista con cobertura y calificación.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores?por_pagina=10`

```http
Accept: application/json
X-Traza-Id: 57547977-cb71-4231-ae6b-3cc9cd5a36a1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 185 ms · traza `57547977-cb71-4231-ae6b-3cc9cd5a36a1`

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
X-Traza-Id: 5ae8053f-1e70-4f2d-8ff5-7b9fe44db2ec
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 47 ms · traza `5ae8053f-1e70-4f2d-8ff5-7b9fe44db2ec`

```xml
<?xml version='1.0' encoding='utf-8'?>
<proveedores xmlns="urn:microhubs:v1" version="1"><datos><proveedor><id>1</id><clave>PV-01</clave><nombre>Abarrotes del Norte</nombre><contacto>Rosa Garza</contacto><correo>ventas@abarrotesdelnorte.example</correo><telefono>8181000101</telefono><dias_entrega>2</dias_entrega><pedido_minimo>800.00</pedido_minimo><condiciones_pago>Contado</condiciones_pago><estatus>activo</estatus><zonas><zona_id>1</zona_id><zona_id>2</zona_id><zona_id>3</zona_id><zona_id>4</zona_id></zonas><calificacion>4</calificacion><evaluaciones>1</evaluaciones></proveedor><proveedor><id>2</id><clave>PV-02</clave><nombre>Distribuidora Regia</nombre><contacto>Luis Treviño</contacto><correo>pedidos@distregia.example</correo><telefono>8181000102</telefono><dias_entrega>1</dias_entrega><pedido_minimo>500.00</pedido_minimo><condiciones_pago>Crédito a 7 días</condiciones_pago><estatus>activo</estatus><zonas><zona_id>1</zona_id><zona_id>2</zona_id><zona_id>3</zona_id><zona_id>4</zona_id></zonas><calificacion>4</calificacion><evaluaciones>1</evaluaciones></proveedor><proveedor><id>3</id><clave>PV-03</clave><nombre>Mayorista San Nicolás</nombre><contacto>Elena Cantú</contacto><correo>compras@mayoristasn.example</correo><telefono>8181000103</telefono><dias_entrega>4</dias_entrega><pedido_minimo>1500.00</pedido_minimo><condiciones_pago>Crédito a 15 días</condiciones_pago><estatus>activo</estatus><zonas><zona_id>1</zona_id><zona_id>2</zona_id><zona_id>3</zona_id><zona_id>4</zona_id></zonas><calificacion>4</calificacion><evaluaciones>1</evaluaciones></proveedor></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>3</total><paginas>1</paginas></paginacion></proveedores>
```

### PRV-03 · Un cliente intenta ver proveedores · PASA

**Objetivo.** El perfil cliente no tiene proveedores.ver.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores`

```http
Accept: application/json
X-Traza-Id: 2d97d1c2-a79b-48e4-a789-6b65e16114d7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 61 ms · traza `2d97d1c2-a79b-48e4-a789-6b65e16114d7`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "2d97d1c2-a79b-48e4-a789-6b65e16114d7"
  }
}
```

### PRV-04 · Un proveedor · PASA

**Objetivo.** Con las zonas que cubre y su calificación.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/2`

```http
Accept: application/json
X-Traza-Id: 92ca261c-08f0-43ab-bb9f-362e3170edf9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 48 ms · traza `92ca261c-08f0-43ab-bb9f-362e3170edf9`

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
X-Traza-Id: a6feef2c-bf22-4f1b-9bf3-fff40212fd9d
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

**Respuesta.** HTTP 201 (esperado 201) · 107 ms · traza `a6feef2c-bf22-4f1b-9bf3-fff40212fd9d`

```json
{
  "id": 7,
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
    "id": 7,
    "clave": "EV-88F5D3",
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
X-Traza-Id: 3b44e5de-2e8a-4cd5-93cd-a95d0c0b21cb
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

**Respuesta.** HTTP 409 (esperado 409) · 29 ms · traza `3b44e5de-2e8a-4cd5-93cd-a95d0c0b21cb`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Ya existe un proveedor con la clave EV-88F5D3.",
    "traza_id": "3b44e5de-2e8a-4cd5-93cd-a95d0c0b21cb"
  }
}
```

### PRV-07 · Correo inválido · PASA

**Objetivo.** Validación con detalle por campo.

**Petición.** `POST http://proveedores:5113/api/v1/proveedores`

```http
Accept: application/json
X-Traza-Id: 0d3cb62b-29b0-46eb-ac2a-c65a51df0300
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

**Respuesta.** HTTP 422 (esperado 422) · 95 ms · traza `0d3cb62b-29b0-46eb-ac2a-c65a51df0300`

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
    "traza_id": "0d3cb62b-29b0-46eb-ac2a-c65a51df0300"
  }
}
```

### PRV-08 · Un planeador intenta dar de alta · PASA

**Objetivo.** Sin proveedores.editar.

**Petición.** `POST http://proveedores:5113/api/v1/proveedores`

```http
Accept: application/json
X-Traza-Id: 051f5097-8f90-4994-8a4c-4827b9aea66c
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

**Respuesta.** HTTP 403 (esperado 403) · 60 ms · traza `051f5097-8f90-4994-8a4c-4827b9aea66c`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "051f5097-8f90-4994-8a4c-4827b9aea66c"
  }
}
```

### PRV-09 · Modificar un proveedor · PASA

**Objetivo.** Cambia el plazo y la cobertura; la clave no se toca.

**Petición.** `PUT http://proveedores:5113/api/v1/proveedores/7`

```http
Accept: application/json
X-Traza-Id: 6d6f01fd-9ccb-4524-8020-2a1d1dafc1ae
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

**Respuesta.** HTTP 200 (esperado 200) · 93 ms · traza `6d6f01fd-9ccb-4524-8020-2a1d1dafc1ae`

```json
{
  "id": 7,
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

**Petición.** `PATCH http://proveedores:5113/api/v1/proveedores/7`

```http
Accept: application/json
X-Traza-Id: b701472b-3868-4873-ac4e-ef7a39550c7e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "contacto": "Luis Prueba"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 118 ms · traza `b701472b-3868-4873-ac4e-ef7a39550c7e`

```json
{
  "id": 7,
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
    "clave": "EV-88F5D3",
    "contacto": "Luis Prueba",
    "dias_entrega": 5
  }
]
```

### PRV-10 · Fijar una oferta · PASA

**Objetivo.** Alta del precio de compra de un producto.

**Petición.** `PUT http://proveedores:5113/api/v1/proveedores/7/catalogo/6`

```http
Accept: application/json
X-Traza-Id: ebe4d88f-06e5-4cdd-816d-1549a5046940
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

**Respuesta.** HTTP 200 (esperado 200) · 91 ms · traza `ebe4d88f-06e5-4cdd-816d-1549a5046940`

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
    "proveedor_id": 7,
    "producto_id": 6,
    "precio_compra": "0.05",
    "capacidad_semanal": 100,
    "minimo_compra": 5
  }
]
```

### PRV-11 · Producto inexistente en la oferta · PASA

**Objetivo.** La llave foránea rechaza el producto.

**Petición.** `PUT http://proveedores:5113/api/v1/proveedores/7/catalogo/999999`

```http
Accept: application/json
X-Traza-Id: cb9886ee-a759-4038-a4cf-a2382c18bf06
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "precio_compra": 1,
  "capacidad_semanal": 10
}
```

**Respuesta.** HTTP 422 (esperado 422) · 50 ms · traza `cb9886ee-a759-4038-a4cf-a2382c18bf06`

```json
{
  "error": {
    "codigo": "REGLA_NEGOCIO",
    "mensaje": "El producto no existe.",
    "traza_id": "cb9886ee-a759-4038-a4cf-a2382c18bf06"
  }
}
```

### PRV-12 · Catálogo del proveedor · PASA

**Objetivo.** Sus ofertas, con el nombre del producto.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/7/catalogo`

```http
Accept: application/json
X-Traza-Id: 82f1dbf0-d829-4a01-bd8a-5c966e238f48
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 64 ms · traza `82f1dbf0-d829-4a01-bd8a-5c966e238f48`

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

**Petición.** `POST http://proveedores:5113/api/v1/proveedores/7/evaluaciones`

```http
Accept: application/json
X-Traza-Id: 61340a2e-e3f0-4fde-82a1-f536d93da0a6
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

**Respuesta.** HTTP 201 (esperado 201) · 59 ms · traza `61340a2e-e3f0-4fde-82a1-f536d93da0a6`

```json
{
  "id": 4,
  "proveedor_id": 7,
  "puntualidad": 5,
  "calidad": 4,
  "precio": 3,
  "comentario": "Llegó a tiempo",
  "evaluado_por": 2,
  "evaluado_en": "2026-10-19T19:31:35-06:00"
}
```

**Evidencia en PostgreSQL.** `SELECT proveedor_id, puntualidad, calidad, precio, evaluado_por FROM proveedor_evaluacion WHERE proveedor_id = %s`

```json
[
  {
    "proveedor_id": 7,
    "puntualidad": 5,
    "calidad": 4,
    "precio": 3,
    "evaluado_por": 2
  }
]
```

### PRV-14 · Evaluaciones y promedio · PASA

**Objetivo.** Calificaciones recibidas y su promedio.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/7/evaluaciones`

```http
Accept: application/json
X-Traza-Id: 0dafcd72-78bf-4d1e-a82e-4716bbaa8684
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 68 ms · traza `0dafcd72-78bf-4d1e-a82e-4716bbaa8684`

```json
{
  "datos": [
    {
      "id": 4,
      "proveedor_id": 7,
      "puntualidad": 5,
      "calidad": 4,
      "precio": 3,
      "comentario": "Llegó a tiempo",
      "evaluado_por": 2,
      "evaluado_en": "2026-10-19T19:31:35-06:00"
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

**Petición.** `POST http://proveedores:5113/api/v1/proveedores/7/evaluaciones`

```http
Accept: application/json
X-Traza-Id: fbf8c830-fad0-46d3-8321-338e7c664075
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

**Respuesta.** HTTP 403 (esperado 403) · 28 ms · traza `fbf8c830-fad0-46d3-8321-338e7c664075`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "fbf8c830-fad0-46d3-8321-338e7c664075"
  }
}
```

### PRV-16 · Ofertas de un producto · PASA

**Objetivo.** De la más barata a la más cara.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/ofertas?producto_id=6`

```http
Accept: application/json
X-Traza-Id: a77fb2b4-e72a-47e4-8db6-65c377280795
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 96 ms · traza `a77fb2b4-e72a-47e4-8db6-65c377280795`

```json
{
  "datos": [
    {
      "proveedor": {
        "id": 7,
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
X-Traza-Id: 205e4407-f3aa-44df-af01-5b17bc7bc638
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 81 ms · traza `205e4407-f3aa-44df-af01-5b17bc7bc638`

```json
{
  "datos": [
    {
      "proveedor": {
        "id": 7,
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
X-Traza-Id: 653cb3d2-eca3-4481-846a-2148cd64e1c8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 7 ms · traza `653cb3d2-eca3-4481-846a-2148cd64e1c8`

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
    "traza_id": "653cb3d2-eca3-4481-846a-2148cd64e1c8"
  }
}
```

### PRV-19 · Dar de baja un proveedor · PASA

**Objetivo.** Baja lógica: ya no aparece en las ofertas.

**Petición.** `DELETE http://proveedores:5113/api/v1/proveedores/7`

```http
Accept: application/json
X-Traza-Id: e675ce80-9469-4bdd-a4b5-93f40792dc30
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 37 ms · traza `e675ce80-9469-4bdd-a4b5-93f40792dc30`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT clave, estatus FROM proveedor WHERE id = %s`

```json
[
  {
    "clave": "EV-88F5D3",
    "estatus": "inactivo"
  }
]
```

### PRV-20 · Ofertas sin el proveedor de baja · PASA

**Objetivo.** El proveedor dado de baja no ofrece.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/ofertas?producto_id=6`

```http
Accept: application/json
X-Traza-Id: a937ee06-ad22-42e8-9ac2-17b13fbd91b9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 65 ms · traza `a937ee06-ad22-42e8-9ac2-17b13fbd91b9`

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
X-Traza-Id: 090ff4ed-c198-4799-baa6-6e8220ac8466
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 217 ms · traza `090ff4ed-c198-4799-baa6-6e8220ac8466`

```json
{
  "datos": [
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
    "total": 1,
    "paginas": 1
  }
}
```

### PRE-02 · Listas (XML) · PASA

**Objetivo.** Respuesta XML que cumple precios.xsd.

**Petición.** `GET http://precios:5112/api/v1/precios/listas`

```http
Accept: application/xml
X-Traza-Id: c0992c19-7842-4a98-83bf-d61ad3d3722c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 44 ms · traza `c0992c19-7842-4a98-83bf-d61ad3d3722c`

```xml
<?xml version='1.0' encoding='utf-8'?>
<listas xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><datos><lista><id>1</id><nombre>Lista San Bernabé Centro</nombre><zona_id>1</zona_id><vigente_desde>2026-10-19</vigente_desde><vigente_hasta xsi:nil="true" /><estatus>activo</estatus><productos>20</productos></lista></datos><paginacion><pagina>1</pagina><por_pagina>20</por_pagina><total>1</total><paginas>1</paginas></paginacion></listas>
```

### PRE-03 · Un cliente intenta ver las listas · PASA

**Objetivo.** Sin precios.ver.

**Petición.** `GET http://precios:5112/api/v1/precios/listas`

```http
Accept: application/json
X-Traza-Id: a58b36c8-1bf0-4573-bee5-1bc4c078cd24
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 31 ms · traza `a58b36c8-1bf0-4573-bee5-1bc4c078cd24`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "a58b36c8-1bf0-4573-bee5-1bc4c078cd24"
  }
}
```

### PRE-04 · Crear una lista · PASA

**Objetivo.** Lista de una zona con un precio y su costo.

**Petición.** `POST http://precios:5112/api/v1/precios/listas`

```http
Accept: application/json
X-Traza-Id: ace29e63-c425-44a4-aab7-a9d2d91d33a2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Lista de evidencias 0c58f9",
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

**Respuesta.** HTTP 201 (esperado 201) · 117 ms · traza `ace29e63-c425-44a4-aab7-a9d2d91d33a2`

```json
{
  "id": 3,
  "nombre": "Lista de evidencias 0c58f9",
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
      "actualizado_en": "2026-10-19T19:31:36-06:00"
    }
  ]
}
```

**Explicación.** Margen = (precio − costo) / precio = (50 − 30) / 50 = 40 %.

**Evidencia en PostgreSQL.** `SELECT l.id, l.nombre, l.zona_id, l.vigente_desde, l.vigente_hasta, i.producto_id, i.precio, i.costo FROM lista_precio l JOIN lista_precio_item i ON i.lista_id = l.id WHERE l.nombre = %s`

```json
[
  {
    "id": 3,
    "nombre": "Lista de evidencias 0c58f9",
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
X-Traza-Id: 128f375e-ce24-4e2f-b72e-a4495b70be6f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Lista de evidencias 0c58f9 bis",
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

**Respuesta.** HTTP 409 (esperado 409) · 122 ms · traza `128f375e-ce24-4e2f-b72e-a4495b70be6f`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "La lista «Lista de evidencias 0c58f9» ya rige en esa zona durante esas fechas.",
    "traza_id": "128f375e-ce24-4e2f-b72e-a4495b70be6f"
  }
}
```

### PRE-06 · Cambiar el precio de un producto · PASA

**Objetivo.** Sube el precio de 50 a 52; el costo se conserva.

**Petición.** `PUT http://precios:5112/api/v1/precios/listas/3/items/2`

```http
Accept: application/json
X-Traza-Id: 70bbb2e4-3403-40bd-a08f-433a0b69023a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "precio": 52.0
}
```

**Respuesta.** HTTP 200 (esperado 200) · 81 ms · traza `70bbb2e4-3403-40bd-a08f-433a0b69023a`

```json
{
  "producto": {
    "id": 2,
    "nombre": "Arroz superextra"
  },
  "precio": 52.0,
  "costo": 30.0,
  "margen_pct": 42.3,
  "actualizado_en": "2026-10-19T19:31:36-06:00"
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

**Petición.** `GET http://precios:5112/api/v1/precios/historial?lista_id=3&producto_id=2`

```http
Accept: application/json
X-Traza-Id: abd1a093-1037-43cd-b058-98ef4171c4de
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 56 ms · traza `abd1a093-1037-43cd-b058-98ef4171c4de`

```json
{
  "datos": [
    {
      "id": 22,
      "lista_id": 3,
      "producto_id": 2,
      "precio_anterior": 50.0,
      "precio_nuevo": 52.0,
      "usuario_id": 1,
      "fecha": "2026-10-19T19:31:36-06:00"
    },
    {
      "id": 21,
      "lista_id": 3,
      "producto_id": 2,
      "precio_anterior": null,
      "precio_nuevo": 50.0,
      "usuario_id": 1,
      "fecha": "2026-10-19T19:31:36-06:00"
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

**Petición.** `GET http://precios:5112/api/v1/precios/listas/3`

```http
Accept: application/json
X-Traza-Id: 53b833e0-0bb7-40f2-a23f-b2ae86acd277
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 50 ms · traza `53b833e0-0bb7-40f2-a23f-b2ae86acd277`

```json
{
  "id": 3,
  "nombre": "Lista de evidencias 0c58f9",
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
      "actualizado_en": "2026-10-19T19:31:36-06:00"
    }
  ]
}
```

### PRE-09 · Precio dentro de la vigencia · PASA

**Objetivo.** Rige el precio de la lista de la zona.

**Petición.** `GET http://precios:5112/api/v1/precios/vigente?producto_id=2&zona_id=3&fecha=2027-01-15`

```http
Accept: application/json
X-Traza-Id: 0851c1c1-a38b-4183-a747-d39cf4941b9a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 97 ms · traza `0851c1c1-a38b-4183-a747-d39cf4941b9a`

```json
{
  "producto_id": 2,
  "zona_id": 3,
  "fecha": "2027-01-15",
  "precio_base": 29.9,
  "lista": {
    "id": 3,
    "nombre": "Lista de evidencias 0c58f9"
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
X-Traza-Id: 928549a7-2af5-4632-9979-aa1cb2adea3f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 145 ms · traza `928549a7-2af5-4632-9979-aa1cb2adea3f`

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
X-Traza-Id: 94250808-b3f0-4b4b-82b0-0b7e6f21fc02
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 96 ms · traza `94250808-b3f0-4b4b-82b0-0b7e6f21fc02`

```json
{
  "producto_id": 1,
  "zona_id": 1,
  "fecha": "2026-10-19",
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
X-Traza-Id: 67aafc09-6257-4d3a-ada7-19e6c80b4c30
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 94 ms · traza `67aafc09-6257-4d3a-ada7-19e6c80b4c30`

```json
{
  "producto_id": 21,
  "zona_id": 1,
  "fecha": "2026-10-19",
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
X-Traza-Id: 175c6428-a8d4-4f0f-9a5d-600b0f9bafba
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

**Respuesta.** HTTP 200 (esperado 200) · 91 ms · traza `175c6428-a8d4-4f0f-9a5d-600b0f9bafba`

```json
{
  "zona_id": 1,
  "fecha": "2026-10-19",
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
X-Traza-Id: 924eea46-e896-4fa1-b453-1eb1bc35c454
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

**Respuesta.** HTTP 422 (esperado 422) · 6 ms · traza `924eea46-e896-4fa1-b453-1eb1bc35c454`

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
    "traza_id": "924eea46-e896-4fa1-b453-1eb1bc35c454"
  }
}
```

### PRE-15 · Promoción que pasa del descuento máximo · PASA

**Objetivo.** Un porcentaje mayor al tope de la configuración se rechaza.

**Petición.** `POST http://precios:5112/api/v1/precios/promociones`

```http
Accept: application/json
X-Traza-Id: 963e5e4b-731f-4d55-8ba6-4a268c447619
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

**Respuesta.** HTTP 422 (esperado 422) · 26 ms · traza `963e5e4b-731f-4d55-8ba6-4a268c447619`

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
    "traza_id": "963e5e4b-731f-4d55-8ba6-4a268c447619"
  }
}
```

### PRE-16 · Crear una promoción · PASA

**Objetivo.** Descuento de $2 en un producto.

**Petición.** `POST http://precios:5112/api/v1/precios/promociones`

```http
Accept: application/json
X-Traza-Id: da503858-ca1d-4d71-81a4-d41c8842ac8b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Promoción de evidencias 87b4",
  "tipo": "monto",
  "valor": 2.0,
  "producto_id": 1,
  "vigente_hasta": "2030-12-31"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 72 ms · traza `da503858-ca1d-4d71-81a4-d41c8842ac8b`

```json
{
  "id": 2,
  "nombre": "Promoción de evidencias 87b4",
  "tipo": "monto",
  "valor": 2.0,
  "producto_id": 1,
  "categoria_id": null,
  "zona_id": null,
  "vigente_desde": "2026-10-19",
  "vigente_hasta": "2030-12-31",
  "estatus": "activo"
}
```

**Evidencia en PostgreSQL.** `SELECT id, nombre, tipo, valor, producto_id, vigente_hasta, estatus FROM promocion WHERE id = %s`

```json
[
  {
    "id": 2,
    "nombre": "Promoción de evidencias 87b4",
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
X-Traza-Id: 57d43446-1390-4987-aba9-f0ca80e64028
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 48 ms · traza `57d43446-1390-4987-aba9-f0ca80e64028`

```json
{
  "datos": [
    {
      "id": 2,
      "nombre": "Promoción de evidencias 87b4",
      "tipo": "monto",
      "valor": 2.0,
      "producto_id": 1,
      "categoria_id": null,
      "zona_id": null,
      "vigente_desde": "2026-10-19",
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

**Petición.** `DELETE http://precios:5112/api/v1/precios/promociones/2`

```http
Accept: application/json
X-Traza-Id: 2eab5e25-8561-44d5-9e52-42d6ef47e3f6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 34 ms · traza `2eab5e25-8561-44d5-9e52-42d6ef47e3f6`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT id, estatus FROM promocion WHERE id = %s`

```json
[
  {
    "id": 2,
    "estatus": "inactivo"
  }
]
```

### PRE-19 · Márgenes · PASA

**Objetivo.** Renglones con costo, del margen más bajo al más alto.

**Petición.** `GET http://precios:5112/api/v1/precios/margenes?por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 7d37200a-8941-429c-9048-224e2e53ccc0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 99 ms · traza `7d37200a-8941-429c-9048-224e2e53ccc0`

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
X-Traza-Id: 86f8ef5b-f2d3-495a-8701-ce91ef5353c3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 114 ms · traza `86f8ef5b-f2d3-495a-8701-ce91ef5353c3`

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
X-Traza-Id: 041a9f82-a092-4bf0-a3ef-6d9535d763b8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 5 ms · traza `041a9f82-a092-4bf0-a3ef-6d9535d763b8`

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
    "traza_id": "041a9f82-a092-4bf0-a3ef-6d9535d763b8"
  }
}
```

## Servicio abastecimiento · puerto 5114

### ABA-01 · Necesidades de reposición · PASA

**Objetivo.** Productos bajo su mínimo, con la mejor oferta.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/necesidades?por_pagina=100`

```http
Accept: application/json
X-Traza-Id: 26d1f67a-bd9e-4068-9a4f-7ebfaffb4df4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 344 ms · traza `26d1f67a-bd9e-4068-9a4f-7ebfaffb4df4`

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
X-Traza-Id: 15001bce-93cb-40ae-8640-dd49305117a1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 6 ms · traza `15001bce-93cb-40ae-8640-dd49305117a1`

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
    "traza_id": "15001bce-93cb-40ae-8640-dd49305117a1"
  }
}
```

### ABA-03 · Pedir mercancía · PASA

**Objetivo.** El operador pide reposición de su microhub.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: e0c57b40-4bd3-4560-b070-19299b87dd99
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

**Respuesta.** HTTP 201 (esperado 201) · 93 ms · traza `e0c57b40-4bd3-4560-b070-19299b87dd99`

```json
{
  "id": 1,
  "folio": "SC-20261020-000001",
  "microhub_id": 1,
  "estado": "pendiente",
  "motivo": "Se acabó el producto el fin de semana",
  "solicitada_por": 2,
  "decidida_por": null,
  "decision_motivo": null,
  "decidida_en": null,
  "creada_en": "2026-10-19T19:31:38-06:00",
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
    "id": 1,
    "folio": "SC-20261020-000001",
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
    "titulo": "Solicitud de compra SC-20261020-000001",
    "referencia_tipo": "solicitud"
  }
]
```

### ABA-04 · Pedir para otro microhub · PASA

**Objetivo.** El operador solo trabaja con el suyo.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: 3bac3c0e-2bfd-4b9d-b4c5-c178d6299fca
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

**Respuesta.** HTTP 403 (esperado 403) · 8 ms · traza `3bac3c0e-2bfd-4b9d-b4c5-c178d6299fca`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "3bac3c0e-2bfd-4b9d-b4c5-c178d6299fca"
  }
}
```

### ABA-05 · Producto repetido en la solicitud · PASA

**Objetivo.** Un producto aparece una sola vez.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: 2ac66d36-279b-4b4f-bcf4-f75ce1985251
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

**Respuesta.** HTTP 422 (esperado 422) · 6 ms · traza `2ac66d36-279b-4b4f-bcf4-f75ce1985251`

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
    "traza_id": "2ac66d36-279b-4b4f-bcf4-f75ce1985251"
  }
}
```

### ABA-06 · Solicitud de otro microhub · PASA

**Objetivo.** Otro operador no la ve.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/1`

```http
Accept: application/json
X-Traza-Id: 36a76e4e-6a86-4bdf-92df-0562a670789b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 26 ms · traza `36a76e4e-6a86-4bdf-92df-0562a670789b`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe esa solicitud de compra.",
    "traza_id": "36a76e4e-6a86-4bdf-92df-0562a670789b"
  }
}
```

### ABA-07 · Aprobar sin permiso · PASA

**Objetivo.** Solo el administrador decide.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/1/decision`

```http
Accept: application/json
X-Traza-Id: 3feb803f-ac89-48d7-8789-d6200e75fdaa
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aprobada"
}
```

**Respuesta.** HTTP 403 (esperado 403) · 32 ms · traza `3feb803f-ac89-48d7-8789-d6200e75fdaa`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "3feb803f-ac89-48d7-8789-d6200e75fdaa"
  }
}
```

### ABA-08 · Rechazar sin motivo · PASA

**Objetivo.** Rechazar exige el motivo.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/1/decision`

```http
Accept: application/json
X-Traza-Id: 5c07cc80-5b3f-4cd1-a35d-92d14064d585
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "rechazada"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 8 ms · traza `5c07cc80-5b3f-4cd1-a35d-92d14064d585`

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
    "traza_id": "5c07cc80-5b3f-4cd1-a35d-92d14064d585"
  }
}
```

### ABA-09 · Ordenar antes de aprobar · PASA

**Objetivo.** Solo se ordena una solicitud aprobada.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/1/ordenar`

```http
Accept: application/json
X-Traza-Id: f8c3e259-74bb-4f7e-96ed-011ee781c80e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "proveedor_id": 1
}
```

**Respuesta.** HTTP 409 (esperado 409) · 46 ms · traza `f8c3e259-74bb-4f7e-96ed-011ee781c80e`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Solo se ordena una solicitud aprobada; esta está pendiente.",
    "traza_id": "f8c3e259-74bb-4f7e-96ed-011ee781c80e"
  }
}
```

### ABA-10 · Aprobar la solicitud · PASA

**Objetivo.** El administrador aprueba y quien pidió recibe el aviso.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/1/decision`

```http
Accept: application/json
X-Traza-Id: 67bda198-3b84-439a-86bb-46c89ed1e062
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aprobada",
  "motivo": "Hay presupuesto"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 137 ms · traza `67bda198-3b84-439a-86bb-46c89ed1e062`

```json
{
  "id": 1,
  "folio": "SC-20261020-000001",
  "microhub_id": 1,
  "estado": "aprobada",
  "motivo": "Se acabó el producto el fin de semana",
  "solicitada_por": 2,
  "decidida_por": 1,
  "decision_motivo": "Hay presupuesto",
  "decidida_en": "2026-10-19T19:31:38-06:00",
  "creada_en": "2026-10-19T19:31:38-06:00",
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
    "titulo": "Solicitud de compra SC-20261020-000001",
    "mensaje": "Tu solicitud fue aprobada."
  }
]
```

### ABA-11 · Emitir la orden de compra · PASA

**Objetivo.** Cada línea va al proveedor indicado; el total es piezas × precio de compra.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/1/ordenar`

```http
Accept: application/json
X-Traza-Id: be5939f4-1b30-4aa4-92d4-8b67235c0a4c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "proveedor_id": 1
}
```

**Respuesta.** HTTP 201 (esperado 201) · 448 ms · traza `be5939f4-1b30-4aa4-92d4-8b67235c0a4c`

```json
{
  "solicitud_id": 1,
  "ordenes": [
    {
      "id": 1,
      "folio": "OC-20261020-000001",
      "solicitud_id": 1,
      "proveedor": {
        "id": 1,
        "nombre": "Abarrotes del Norte"
      },
      "microhub_id": 1,
      "estado": "emitida",
      "fecha_esperada": "2026-10-21",
      "total": 853.3,
      "creada_en": "2026-10-19T19:31:38-06:00",
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
    "id": 1,
    "folio": "OC-20261020-000001",
    "estado": "emitida",
    "fecha_esperada": "2026-10-21",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/1/ordenar`

```http
Accept: application/json
X-Traza-Id: b51250b1-89bc-4078-8cf1-d57a9d347115
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "proveedor_id": 1
}
```

**Respuesta.** HTTP 409 (esperado 409) · 44 ms · traza `b51250b1-89bc-4078-8cf1-d57a9d347115`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Solo se ordena una solicitud aprobada; esta está ordenada.",
    "traza_id": "b51250b1-89bc-4078-8cf1-d57a9d347115"
  }
}
```

### ABA-13 · Recepción parcial · PASA

**Objetivo.** La mercancía que llegó entra al inventario.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/1/recepcion`

```http
Accept: application/json
X-Traza-Id: f4358b80-e3dc-42ef-ac80-9c1a8be26ad2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "operacion_uuid": "7cc2794e-8090-4a6b-8335-fc0aa1ab1dc3",
  "nota": "Llegó la primera caja",
  "lineas": [
    {
      "producto_id": 10,
      "cantidad": 23
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 365 ms · traza `f4358b80-e3dc-42ef-ac80-9c1a8be26ad2`

```json
{
  "orden": {
    "id": 1,
    "folio": "OC-20261020-000001",
    "solicitud_id": 1,
    "proveedor": {
      "id": 1,
      "nombre": "Abarrotes del Norte"
    },
    "microhub_id": 1,
    "estado": "parcial",
    "fecha_esperada": "2026-10-21",
    "total": 853.3,
    "creada_en": "2026-10-19T19:31:38-06:00",
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
    "operacion_uuid": "7cc2794e-8090-4a6b-8335-fc0aa1ab1dc3:10",
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
    "existencia_resultante": 72,
    "referencia_tipo": "orden_compra",
    "referencia_id": 1
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/1/recepcion`

```http
Accept: application/json
X-Traza-Id: a49bac2e-ba9c-47b0-ae71-64e03993ebc4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "operacion_uuid": "7cc2794e-8090-4a6b-8335-fc0aa1ab1dc3",
  "nota": "Llegó la primera caja",
  "lineas": [
    {
      "producto_id": 10,
      "cantidad": 23
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 161 ms · traza `a49bac2e-ba9c-47b0-ae71-64e03993ebc4`

```json
{
  "orden": {
    "id": 1,
    "folio": "OC-20261020-000001",
    "solicitud_id": 1,
    "proveedor": {
      "id": 1,
      "nombre": "Abarrotes del Norte"
    },
    "microhub_id": 1,
    "estado": "parcial",
    "fecha_esperada": "2026-10-21",
    "total": 853.3,
    "creada_en": "2026-10-19T19:31:38-06:00",
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
    "existencia": 72
  }
]
```

### ABA-15 · Recibir más de lo pedido · PASA

**Objetivo.** Solo falta lo que no ha llegado.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/1/recepcion`

```http
Accept: application/json
X-Traza-Id: 1e61e8c1-bc77-466b-ba7a-6377ddf99dae
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

**Respuesta.** HTTP 422 (esperado 422) · 51 ms · traza `1e61e8c1-bc77-466b-ba7a-6377ddf99dae`

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
    "traza_id": "1e61e8c1-bc77-466b-ba7a-6377ddf99dae"
  }
}
```

### ABA-16 · Cancelar una orden con mercancía recibida · PASA

**Objetivo.** Solo se cancela una orden sin recepciones.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/1/cancelar`

```http
Accept: application/json
X-Traza-Id: 99ba33c8-0e1e-4e99-8797-42fe5ebe3053
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "motivo": "Ya llegó"
}
```

**Respuesta.** HTTP 409 (esperado 409) · 48 ms · traza `99ba33c8-0e1e-4e99-8797-42fe5ebe3053`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Solo se cancela una orden emitida que todavía no recibió mercancía.",
    "traza_id": "99ba33c8-0e1e-4e99-8797-42fe5ebe3053"
  }
}
```

### ABA-17 · Recepción final · PASA

**Objetivo.** Llega el resto: la orden queda recibida y avisa.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/1/recepcion`

```http
Accept: application/json
X-Traza-Id: 08d3d4ad-4789-4999-89b0-3e8a5e17e5cd
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

**Respuesta.** HTTP 201 (esperado 201) · 330 ms · traza `08d3d4ad-4789-4999-89b0-3e8a5e17e5cd`

```json
{
  "orden": {
    "id": 1,
    "folio": "OC-20261020-000001",
    "solicitud_id": 1,
    "proveedor": {
      "id": 1,
      "nombre": "Abarrotes del Norte"
    },
    "microhub_id": 1,
    "estado": "recibida",
    "fecha_esperada": "2026-10-21",
    "total": 853.3,
    "creada_en": "2026-10-19T19:31:38-06:00",
    "cerrada_en": "2026-10-19T19:31:40-06:00",
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
    "existencia": 95
  }
]
```

**Evidencia en PostgreSQL.** `SELECT destinatario_id, titulo, mensaje FROM web_notificacion WHERE referencia_tipo = 'orden' AND referencia_id = %s`

```json
[
  {
    "destinatario_id": 2,
    "titulo": "Orden de compra OC-20261020-000001",
    "mensaje": "La orden quedó recibida."
  },
  {
    "destinatario_id": 1,
    "titulo": "Orden de compra OC-20261020-000001",
    "mensaje": "La orden quedó recibida."
  }
]
```

### ABA-18 · Recibir en una orden ya recibida · PASA

**Objetivo.** Una orden recibida no admite más mercancía.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/1/recepcion`

```http
Accept: application/json
X-Traza-Id: 295a78ee-e21c-456d-a612-9524a9f75512
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

**Respuesta.** HTTP 409 (esperado 409) · 42 ms · traza `295a78ee-e21c-456d-a612-9524a9f75512`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "La orden está recibida; ya no recibe mercancía.",
    "traza_id": "295a78ee-e21c-456d-a612-9524a9f75512"
  }
}
```

### ABA-19 · Una orden · PASA

**Objetivo.** Con lo recibido de cada línea.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/ordenes/1`

```http
Accept: application/json
X-Traza-Id: 97204231-7b2a-4dc7-a4f8-408066498a29
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 65 ms · traza `97204231-7b2a-4dc7-a4f8-408066498a29`

```json
{
  "id": 1,
  "folio": "OC-20261020-000001",
  "solicitud_id": 1,
  "proveedor": {
    "id": 1,
    "nombre": "Abarrotes del Norte"
  },
  "microhub_id": 1,
  "estado": "recibida",
  "fecha_esperada": "2026-10-21",
  "total": 853.3,
  "creada_en": "2026-10-19T19:31:38-06:00",
  "cerrada_en": "2026-10-19T19:31:40-06:00",
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
X-Traza-Id: 4ebad015-d995-40da-a33c-8f27ba09fe74
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 87 ms · traza `4ebad015-d995-40da-a33c-8f27ba09fe74`

```xml
<?xml version='1.0' encoding='utf-8'?>
<ordenes xmlns="urn:microhubs:v1" version="1"><datos><orden><id>1</id><folio>OC-20261020-000001</folio><solicitud_id>1</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-21</fecha_esperada><total>853.30</total><creada_en>2026-10-19T19:31:38-06:00</creada_en><cerrada_en>2026-10-19T19:31:40-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden></datos><paginacion><pagina>1</pagina><por_pagina>20</por_pagina><total>1</total><paginas>1</paginas></paginacion></ordenes>
```

### ABA-21 · Tablero de abastecimiento · PASA

**Objetivo.** Solicitudes y órdenes por estado.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/seguimiento`

```http
Accept: application/json
X-Traza-Id: 66bf3237-f7a2-434b-8db7-30554a4e8eef
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 112 ms · traza `66bf3237-f7a2-434b-8db7-30554a4e8eef`

```json
{
  "microhub_id": 1,
  "solicitudes": {
    "pendiente": 0,
    "aprobada": 0,
    "rechazada": 0,
    "ordenada": 1
  },
  "ordenes": {
    "emitida": 0,
    "parcial": 0,
    "recibida": 1,
    "cancelada": 0
  },
  "atrasadas": 0,
  "pendientes_inventario": 0,
  "proxima_entrega": null
}
```

### ABA-22 · Cancelar sin permiso · PASA

**Objetivo.** Cancelar una orden es del administrador.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/2/cancelar`

```http
Accept: application/json
X-Traza-Id: ea40dbe4-8902-4810-8a12-8e3574905ea2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "motivo": "No hace falta"
}
```

**Respuesta.** HTTP 403 (esperado 403) · 28 ms · traza `ea40dbe4-8902-4810-8a12-8e3574905ea2`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "ea40dbe4-8902-4810-8a12-8e3574905ea2"
  }
}
```

### ABA-23 · Cancelar una orden emitida · PASA

**Objetivo.** Una orden sin recepciones se puede cancelar con motivo.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/2/cancelar`

```http
Accept: application/json
X-Traza-Id: 641f0f60-4803-4643-ba33-d6c7f5f019d0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "motivo": "El proveedor ya no surte"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 160 ms · traza `641f0f60-4803-4643-ba33-d6c7f5f019d0`

```json
{
  "id": 2,
  "folio": "OC-20261020-000002",
  "solicitud_id": 2,
  "proveedor": {
    "id": 1,
    "nombre": "Abarrotes del Norte"
  },
  "microhub_id": 1,
  "estado": "cancelada",
  "fecha_esperada": "2026-10-21",
  "total": 853.3,
  "creada_en": "2026-10-19T19:31:40-06:00",
  "cerrada_en": "2026-10-19T19:31:41-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/2/recepcion`

```http
Accept: application/json
X-Traza-Id: a39f4ec0-a3ab-46b0-bbd7-349dd03360be
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

**Respuesta.** HTTP 409 (esperado 409) · 47 ms · traza `a39f4ec0-a3ab-46b0-bbd7-349dd03360be`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "La orden está cancelada; ya no recibe mercancía.",
    "traza_id": "a39f4ec0-a3ab-46b0-bbd7-349dd03360be"
  }
}
```

### ABA-25 · Solicitudes (XML) · PASA

**Objetivo.** Respuesta XML que cumple abastecimiento.xsd.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/solicitudes?por_pagina=3`

```http
Accept: application/xml
X-Traza-Id: c80fedb9-1fa2-4e80-932a-e8605089dd2c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 65 ms · traza `c80fedb9-1fa2-4e80-932a-e8605089dd2c`

```xml
<?xml version='1.0' encoding='utf-8'?>
<solicitudes xmlns="urn:microhubs:v1" version="1"><datos><solicitud><id>2</id><folio>SC-20261020-000002</folio><microhub_id>1</microhub_id><estado>ordenada</estado><motivo>Compra para cancelar</motivo><solicitada_por>2</solicitada_por><decidida_por>1</decidida_por><decision_motivo>Hay presupuesto</decision_motivo><decidida_en>2026-10-19T19:31:40-06:00</decidida_en><creada_en>2026-10-19T19:31:40-06:00</creada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad></linea></lineas></solicitud><solicitud><id>1</id><folio>SC-20261020-000001</folio><microhub_id>1</microhub_id><estado>ordenada</estado><motivo>Se acabó el producto el fin de semana</motivo><solicitada_por>2</solicitada_por><decidida_por>1</decidida_por><decision_motivo>Hay presupuesto</decision_motivo><decidida_en>2026-10-19T19:31:38-06:00</decidida_en><creada_en>2026-10-19T19:31:38-06:00</creada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad></linea></lineas></solicitud></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>2</total><paginas>1</paginas></paginacion></solicitudes>
```

### ABA-26 · Un auditor consulta · PASA

**Objetivo.** El auditor ve las solicitudes sin poder crear.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: c323f302-aa8c-4809-9cb2-2c5ebab921df
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 67 ms · traza `c323f302-aa8c-4809-9cb2-2c5ebab921df`

```json
{
  "datos": [
    {
      "id": 2,
      "folio": "SC-20261020-000002",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Compra para cancelar",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-10-19T19:31:40-06:00",
      "creada_en": "2026-10-19T19:31:40-06:00",
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
      "id": 1,
      "folio": "SC-20261020-000001",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Se acabó el producto el fin de semana",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-10-19T19:31:38-06:00",
      "creada_en": "2026-10-19T19:31:38-06:00",
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
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 2,
    "paginas": 1
  }
}
```

### ABA-27 · Un cliente consulta · PASA

**Objetivo.** El cliente no tiene abastecimiento.ver.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: 9aee2735-1e1f-4e25-b7d7-dd4e84336baa
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 28 ms · traza `9aee2735-1e1f-4e25-b7d7-dd4e84336baa`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "9aee2735-1e1f-4e25-b7d7-dd4e84336baa"
  }
}
```

## Servicio auth · puerto 5101

### SAL-AUT · Salud de auth · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://auth:5101/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 639c66f3-3ad2-4fe4-848e-8972b6257377
```

**Respuesta.** HTTP 200 (esperado 200) · 19 ms · traza `639c66f3-3ad2-4fe4-848e-8972b6257377`

```json
{
  "servicio": "auth",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica"
  }
}
```

## Servicio usuarios · puerto 5102

### SAL-USU · Salud de usuarios · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://usuarios:5102/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 2ef9ec06-01e9-48a3-867e-4ee498178e28
```

**Respuesta.** HTTP 200 (esperado 200) · 19 ms · traza `2ef9ec06-01e9-48a3-867e-4ee498178e28`

```json
{
  "servicio": "usuarios",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica"
  }
}
```

## Servicio productos · puerto 5103

### SAL-PRO · Salud de productos · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://productos:5103/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 7a6687ad-869d-4645-ac74-6871c5c196ce
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `7a6687ad-869d-4645-ac74-6871c5c196ce`

```json
{
  "servicio": "productos",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica"
  }
}
```

## Servicio pedidos · puerto 5104

### SAL-PED · Salud de pedidos · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://pedidos:5104/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 363074e4-5c8b-457b-b70d-c2987abf6004
```

**Respuesta.** HTTP 200 (esperado 200) · 19 ms · traza `363074e4-5c8b-457b-b70d-c2987abf6004`

```json
{
  "servicio": "pedidos",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica"
  }
}
```

## Servicio entregas · puerto 5105

### SAL-ENT · Salud de entregas · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://entregas:5105/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 69c5674d-bafc-4574-af0b-5e39ce54c11d
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `69c5674d-bafc-4574-af0b-5e39ce54c11d`

```json
{
  "servicio": "entregas",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "ok"
  }
}
```

## Servicio planeacion · puerto 5106

### SAL-PLA · Salud de planeacion · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://planeacion:5106/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 2d0432ac-beda-4b0d-a419-ee9e4a5f11d3
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `2d0432ac-beda-4b0d-a419-ee9e4a5f11d3`

```json
{
  "servicio": "planeacion",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "ok"
  }
}
```

## Servicio documentos · puerto 5107

### SAL-DOC · Salud de documentos · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://documentos:5107/api/v1/health`

```http
Accept: application/json
X-Traza-Id: d1130658-2d09-4d53-b24c-9010cff8b54d
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `d1130658-2d09-4d53-b24c-9010cff8b54d`

```json
{
  "servicio": "documentos",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "ok"
  }
}
```

## Servicio zonas · puerto 5108

### SAL-ZON · Salud de zonas · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://zonas:5108/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 0da26188-877f-4dbd-be70-2d87ae8ad535
```

**Respuesta.** HTTP 200 (esperado 200) · 33 ms · traza `0da26188-877f-4dbd-be70-2d87ae8ad535`

```json
{
  "servicio": "zonas",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica"
  }
}
```

## Servicio microhubs · puerto 5109

### SAL-MIC · Salud de microhubs · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://microhubs:5109/api/v1/health`

```http
Accept: application/json
X-Traza-Id: bd0f759a-ef73-4723-bab2-2a3ea273747b
```

**Respuesta.** HTTP 200 (esperado 200) · 18 ms · traza `bd0f759a-ef73-4723-bab2-2a3ea273747b`

```json
{
  "servicio": "microhubs",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica"
  }
}
```

## Servicio seguimiento · puerto 5110

### SAL-SEG · Salud de seguimiento · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://seguimiento:5110/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 9c416ef1-403e-4b69-baa1-1e4dae893445
```

**Respuesta.** HTTP 200 (esperado 200) · 18 ms · traza `9c416ef1-403e-4b69-baa1-1e4dae893445`

```json
{
  "servicio": "seguimiento",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "ok"
  }
}
```

## Servicio inventario · puerto 5111

### SAL-INV · Salud de inventario · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://inventario:5111/api/v1/health`

```http
Accept: application/json
X-Traza-Id: b033d328-f2d3-479d-86b5-9a5588f29769
```

**Respuesta.** HTTP 200 (esperado 200) · 15 ms · traza `b033d328-f2d3-479d-86b5-9a5588f29769`

```json
{
  "servicio": "inventario",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica"
  }
}
```

## Servicio precios · puerto 5112

### SAL-PRE · Salud de precios · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://precios:5112/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 0024b0fe-86ab-4ac4-a166-b4dd04dc558a
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `0024b0fe-86ab-4ac4-a166-b4dd04dc558a`

```json
{
  "servicio": "precios",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica"
  }
}
```

## Servicio proveedores · puerto 5113

### SAL-PRO · Salud de proveedores · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://proveedores:5113/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 084db775-927b-4d57-99f3-833e1edd938e
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `084db775-927b-4d57-99f3-833e1edd938e`

```json
{
  "servicio": "proveedores",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica"
  }
}
```

## Servicio abastecimiento · puerto 5114

### SAL-ABA · Salud de abastecimiento · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://abastecimiento:5114/api/v1/health`

```http
Accept: application/json
X-Traza-Id: a3c883c2-5a31-4f31-994b-8fb9686cff35
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `a3c883c2-5a31-4f31-994b-8fb9686cff35`

```json
{
  "servicio": "abastecimiento",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica"
  }
}
```

## Servicio notificaciones · puerto 5124

### SAL-NOT · Salud de notificaciones · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://notificaciones:5124/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 019c735f-f398-4c10-8bd2-a165c06fa6ff
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `019c735f-f398-4c10-8bd2-a165c06fa6ff`

```json
{
  "servicio": "notificaciones",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica"
  }
}
```

## Servicio auth · puerto 5101

### MON-01 · Registro de actividad · PASA

**Objetivo.** Cada petición queda en MongoDB con su traza.

**Petición.** `GET http://auth:5101/api/v1/auth/validar`

```http
Accept: application/json
X-Traza-Id: 0268342d-2a2d-41f2-acbb-05660aeb47a0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 5 ms · traza `0268342d-2a2d-41f2-acbb-05660aeb47a0`

```json
{
  "valido": true,
  "expira_en": 880,
  "usuario": {
    "id": 1,
    "rol": "administrador",
    "microhub_id": null
  }
}
```

**Explicación.** El X-Traza-Id de la petición se recupera en logs_tecnicos.correlacion_id.

**Evidencia en MongoDB.** `db.logs_tecnicos.findOne({correlacion_id: '0268342d-2a2d-41f2-acbb-05660aeb47a0'})`

```json
{
  "nivel": "INFO",
  "componente": "auth",
  "registrado_en": "2026-10-20 01:31:41.837000+00:00",
  "correlacion_id": "0268342d-2a2d-41f2-acbb-05660aeb47a0",
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
    "peticiones": 30,
    "ms_promedio": 98.53333333333333
  },
  {
    "_id": "auth",
    "peticiones": 24,
    "ms_promedio": 221.91666666666666
  },
  {
    "_id": "documentos",
    "peticiones": 10,
    "ms_promedio": 21.3
  },
  {
    "_id": "entregas",
    "peticiones": 12,
    "ms_promedio": 71.41666666666667
  },
  {
    "_id": "inventario",
    "peticiones": 40,
    "ms_promedio": 62.725
  },
  {
    "_id": "microhubs",
    "peticiones": 4,
    "ms_promedio": 41.5
  },
  {
    "_id": "notificaciones",
    "peticiones": 16,
    "ms_promedio": 34.5625
  },
  {
    "_id": "pedidos",
    "peticiones": 8,
    "ms_promedio": 46.125
  },
  {
    "_id": "planeacion",
    "peticiones": 16,
    "ms_promedio": 59.625
  },
  {
    "_id": "precios",
    "peticiones": 21,
    "ms_promedio": 61.38095238095238
  },
  {
    "_id": "productos",
    "peticiones": 8,
    "ms_promedio": 36.375
  },
  {
    "_id": "proveedores",
    "peticiones": 26,
    "ms_promedio": 55.38461538461539
  },
  {
    "_id": "seguimiento",
    "peticiones": 4,
    "ms_promedio": 45.25
  },
  {
    "_id": "usuarios",
    "peticiones": 8,
    "ms_promedio": 41.0
  },
  {
    "_id": "zonas",
    "peticiones": 4,
    "ms_promedio": 27.25
  }
]
```

## Servicio zonas · puerto 5108

### RAT-01 · Límite de consumo excedido · PASA

**Objetivo.** Más de 240 solicitudes por minuto desde la misma IP.

**Petición.** `GET http://zonas:5108/api/v1/zonas`

```http
Accept: application/json
X-Traza-Id: f7822466-a9d8-4187-9119-a63f0c0b3393
```

**Respuesta.** HTTP 429 (esperado 429) · 3 ms · traza `f7822466-a9d8-4187-9119-a63f0c0b3393`

```json
{
  "error": {
    "codigo": "LIMITE_EXCEDIDO",
    "mensaje": "Máximo 240 solicitudes por minuto. Espera 16 segundos.",
    "traza_id": "f7822466-a9d8-4187-9119-a63f0c0b3393"
  }
}
```

**Explicación.** Contador rate:zonas:{ip}:{minuto} en Redis (db 1) con TTL de 120 s; responde Retry-After.

**Evidencia en Redis.** `db1 GET rate:zonas:a4df1c04ca164e83:29874331; db1 TTL rate:zonas:a4df1c04ca164e83:29874331`

```json
[
  {
    "comando": "db1 GET rate:zonas:a4df1c04ca164e83:29874331",
    "valor": "242"
  },
  {
    "comando": "db1 TTL rate:zonas:a4df1c04ca164e83:29874331",
    "valor": 100
  }
]
```
