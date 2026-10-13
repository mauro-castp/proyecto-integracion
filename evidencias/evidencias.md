# Evidencias de petición y respuesta · microservicios v1

Generado el 2026-10-13 21:27 contra los servicios en ejecución. 93 de 93 casos pasan.

## Servicio auth · puerto 5101

### AUTH-01 · Iniciar sesión (JSON) · PASA

**Objetivo.** Emitir el JWT de acceso y el token de renovación del repartidor.

**Petición.** `POST http://auth:5101/api/v1/auth/login`

```http
Accept: application/json
X-Traza-Id: c2f17193-fb19-4052-a445-d4a5413a0268
Content-Type: application/json
```

```json
{
  "correo": "repartidor1@codex.mx",
  "clave": "********",
  "dispositivo": "Pixel 7"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 1021 ms · traza `c2f17193-fb19-4052-a445-d4a5413a0268`

```json
{
  "token_acceso": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwicm9sIjo…(291 caracteres)",
  "token_renovacion": "rt_0fb67ef39a4d86fae2784cbf43591f9a",
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

**Evidencia en Redis.** `SMEMBERS auth:sesion:7; TTL auth:sesion:7; TTL auth:refresh:cfb0fed4091e4be1070ea8b6b69244550c1a88c621306131995693a0ce0f4741`

```json
[
  {
    "comando": "SMEMBERS auth:sesion:7",
    "valor": [
      "1de3ba91c6784f47aa1f1291fa846ff1"
    ]
  },
  {
    "comando": "TTL auth:sesion:7",
    "valor": 899
  },
  {
    "comando": "TTL auth:refresh:cfb0fed4091e4be1070ea8b6b69244550c1a88c621306131995693a0ce0f4741",
    "valor": 604799
  }
]
```

**Evidencia en PostgreSQL.** `SELECT fecha, modulo, accion, detalle FROM auditoria WHERE correo_intento IS NULL AND usuario_id = 7 AND modulo = 'auth' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "fecha": "2026-10-13 21:27:30.361277+00:00",
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
X-Traza-Id: 78daf990-8950-4c9d-ad1c-ba0ee691d807
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><login xmlns="urn:microhubs:v1"><correo>planeador@codex.mx</correo><clave>********</clave></login>
```

**Respuesta.** HTTP 200 (esperado 200) · 504 ms · traza `78daf990-8950-4c9d-ad1c-ba0ee691d807`

```xml
<?xml version='1.0' encoding='utf-8'?>
<sesion xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><token_acceso>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwicm9sIjo…(291 caracteres)</token_acceso><token_renovacion>rt_a643ff383e66a3d1d13785b6d8367f8e</token_renovacion><tipo>Bearer</tipo><expira_en>900</expira_en><usuario><id>5</id><nombre>Vanessa</nombre><apellidos>Morante López</apellidos><correo>planeador@codex.mx</correo><rol>planeador</rol><microhub_id xsi:nil="true" /><permisos><permiso>archivos.crear</permiso><permiso>archivos.ver</permiso><permiso>catalogo_publico.ver</permiso><permiso>configuracion.ver</permiso><permiso>indicadores.ver</permiso><permiso>inventario.ver</permiso><permiso>microhubs.ver</permiso><permiso>notificaciones.ver</permiso><permiso>pedidos.reasignar</permiso><permiso>pedidos.ver</permiso><permiso>planeacion.editar</permiso><permiso>planeacion.ver</permiso><permiso>productos.ver</permiso><permiso>reportes.exportar</permiso><permiso>reportes.ver</permiso><permiso>simulacion.ejecutar</permiso><permiso>simulacion.ver</permiso><permiso>zonas.ver</permiso></permisos></usuario></sesion>
```

**Explicación.** El cuerpo XML se valida contra los XSD antes de procesarse; la respuesta <sesion> también cumple el XSD.

### AUTH-03 · Clave incorrecta · PASA

**Objetivo.** Rechazar credenciales y contar el intento.

**Petición.** `POST http://auth:5101/api/v1/auth/login`

```http
Accept: application/json
X-Traza-Id: 42afbaec-d1ca-4fc2-af45-11ea09b6f38f
Content-Type: application/json
```

```json
{
  "correo": "auditor@codex.mx",
  "clave": "********"
}
```

**Respuesta.** HTTP 401 (esperado 401) · 269 ms · traza `42afbaec-d1ca-4fc2-af45-11ea09b6f38f`

```json
{
  "error": {
    "codigo": "CREDENCIALES_INVALIDAS",
    "mensaje": "Correo o clave incorrectos. Intento 1 de 5.",
    "traza_id": "42afbaec-d1ca-4fc2-af45-11ea09b6f38f"
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
X-Traza-Id: 297a0f6d-f4db-47d0-92f6-fd0c44866775
Content-Type: application/json
```

```json
{
  "correo": "sin-arroba",
  "clave": "********"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 346 ms · traza `297a0f6d-f4db-47d0-92f6-fd0c44866775`

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
    "traza_id": "297a0f6d-f4db-47d0-92f6-fd0c44866775"
  }
}
```

### AUTH-05 · XML con DTD (ataque XXE) · PASA

**Objetivo.** Rechazar entidades externas y DTD.

**Petición.** `POST http://auth:5101/api/v1/auth/login`

```http
Accept: application/xml
X-Traza-Id: 885fcd14-4128-4598-9ba5-61094bc357a3
Content-Type: application/xml
```

```xml
<?xml version="1.0"?><!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]><login xmlns="urn:microhubs:v1"><correo>&e;</correo><clave>********</clave></login>
```

**Respuesta.** HTTP 400 (esperado 400) · 16 ms · traza `885fcd14-4128-4598-9ba5-61094bc357a3`

```xml
<?xml version='1.0' encoding='utf-8'?>
<error xmlns="urn:microhubs:v1" version="1"><codigo>XML_INVALIDO</codigo><mensaje>El cuerpo XML no está bien formado o contiene DTD/entidades.</mensaje><traza_id>885fcd14-4128-4598-9ba5-61094bc357a3</traza_id></error>
```

**Explicación.** El lector XML (defusedxml) prohíbe DTD y entidades; el error también llega en XML.

### AUTH-06 · Validar token · PASA

**Objetivo.** Comprobar firma, vigencia y sesión activa en Redis.

**Petición.** `GET http://auth:5101/api/v1/auth/validar`

```http
Accept: application/json
X-Traza-Id: 0e1f7f0e-fea3-4b4d-8ed0-b9e00907e79b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `0e1f7f0e-fea3-4b4d-8ed0-b9e00907e79b`

```json
{
  "valido": true,
  "expira_en": 898,
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
X-Traza-Id: 940ce2ab-e9f2-448c-8454-c6177e808bf3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 401 (esperado 401) · 7 ms · traza `940ce2ab-e9f2-448c-8454-c6177e808bf3`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.",
    "traza_id": "940ce2ab-e9f2-448c-8454-c6177e808bf3"
  }
}
```

### AUTH-08 · Renovar sesión · PASA

**Objetivo.** Obtener tokens nuevos con el token de renovación (rotación).

**Petición.** `POST http://auth:5101/api/v1/auth/renovar`

```http
Accept: application/json
X-Traza-Id: 51db92d1-4f23-4686-a1c7-75d5465afab3
Content-Type: application/json
```

```json
{
  "token_renovacion": "rt_81e9fc89584e5e5c2fb6916130defb33"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 88 ms · traza `51db92d1-4f23-4686-a1c7-75d5465afab3`

```json
{
  "token_acceso": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwicm9sIjo…(291 caracteres)",
  "token_renovacion": "rt_e00fe92edfb146ffa978c86255fe8e32",
  "tipo": "Bearer",
  "expira_en": 900
}
```

**Explicación.** El token de renovación usado se borra de Redis y su acceso anterior queda revocado.

**Evidencia en Redis.** `EXISTS auth:refresh:536c73d5ada15601b4f80a4f900d7f63cc18a99e98de23b2296f4ff49f0afefa`

```json
[
  {
    "comando": "EXISTS auth:refresh:536c73d5ada15601b4f80a4f900d7f63cc18a99e98de23b2296f4ff49f0afefa",
    "valor": 0
  }
]
```

### AUTH-09 · Reusar un token de renovación · PASA

**Objetivo.** Un token de renovación sirve una sola vez.

**Petición.** `POST http://auth:5101/api/v1/auth/renovar`

```http
Accept: application/json
X-Traza-Id: ea621b2f-de19-44b9-9524-088ad152a194
Content-Type: application/json
```

```json
{
  "token_renovacion": "rt_81e9fc89584e5e5c2fb6916130defb33"
}
```

**Respuesta.** HTTP 401 (esperado 401) · 7 ms · traza `ea621b2f-de19-44b9-9524-088ad152a194`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.",
    "traza_id": "ea621b2f-de19-44b9-9524-088ad152a194"
  }
}
```

### AUTH-10 · Cerrar sesión · PASA

**Objetivo.** Revocar el acceso del encabezado y la renovación del cuerpo.

**Petición.** `POST http://auth:5101/api/v1/auth/salir`

```http
Accept: application/json
X-Traza-Id: ee01153b-9a3f-4afd-9252-5093738692a6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "token_renovacion": "rt_e00fe92edfb146ffa978c86255fe8e32"
}
```

**Respuesta.** HTTP 204 (esperado 204) · 38 ms · traza `ee01153b-9a3f-4afd-9252-5093738692a6`

```json
(sin cuerpo)
```

**Explicación.** El jti se agrega a la lista de revocados con TTL igual a su vida restante y sale del conjunto de sesión.

**Evidencia en Redis.** `TTL auth:jti:revocado:e13868ddd5d34146bc8abdc810cd00ab; SISMEMBER auth:sesion:7 e13868ddd5d34146bc8abdc810cd00ab`

```json
[
  {
    "comando": "TTL auth:jti:revocado:e13868ddd5d34146bc8abdc810cd00ab",
    "valor": 899
  },
  {
    "comando": "SISMEMBER auth:sesion:7 e13868ddd5d34146bc8abdc810cd00ab",
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
X-Traza-Id: f41fb72d-1b86-4c00-af7c-ae0c9fb6fa14
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 401 (esperado 401) · 565 ms · traza `f41fb72d-1b86-4c00-af7c-ae0c9fb6fa14`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.",
    "traza_id": "f41fb72d-1b86-4c00-af7c-ae0c9fb6fa14"
  }
}
```

**Explicación.** El servicio de usuarios consulta auth:jti:revocado en Redis: la revocación es común a todos.

### USR-01 · Mi perfil (JSON) · PASA

**Objetivo.** Consultar el perfil de quien inició sesión.

**Petición.** `GET http://usuarios:5102/api/v1/usuarios/yo`

```http
Accept: application/json
X-Traza-Id: 435198a2-9d33-439e-ab2f-59c3f03c8bd8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 48 ms · traza `435198a2-9d33-439e-ab2f-59c3f03c8bd8`

```json
{
  "id": 7,
  "nombre": "Ramiro",
  "apellidos": "Alanís Lozano",
  "correo": "repartidor1@codex.mx",
  "telefono": "8114641034",
  "rol": "repartidor",
  "microhub": null,
  "ultimo_acceso": "2026-10-13T15:27:32-06:00"
}
```

### USR-02 · Mi perfil (XML) · PASA

**Objetivo.** El mismo recurso en XML según Accept.

**Petición.** `GET http://usuarios:5102/api/v1/usuarios/yo`

```http
Accept: application/xml
X-Traza-Id: 66ee53c9-f3bb-4de9-8e7e-61914e67aa4c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 36 ms · traza `66ee53c9-f3bb-4de9-8e7e-61914e67aa4c`

```xml
<?xml version='1.0' encoding='utf-8'?>
<usuario xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>5</id><nombre>Vanessa</nombre><apellidos>Morante López</apellidos><correo>planeador@codex.mx</correo><telefono>8178109897</telefono><rol>planeador</rol><microhub xsi:nil="true" /><ultimo_acceso>2026-10-13T15:27:33-06:00</ultimo_acceso></usuario>
```

### USR-03 · Actualizar mi teléfono (PATCH) · PASA

**Objetivo.** Modificar un dato del perfil.

**Petición.** `PATCH http://usuarios:5102/api/v1/usuarios/yo`

```http
Accept: application/json
X-Traza-Id: 61eff429-5965-4981-b95f-ff536d48c95a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "telefono": "8112345678"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 65 ms · traza `61eff429-5965-4981-b95f-ff536d48c95a`

```json
{
  "id": 7,
  "nombre": "Ramiro",
  "apellidos": "Alanís Lozano",
  "correo": "repartidor1@codex.mx",
  "telefono": "8112345678",
  "rol": "repartidor",
  "microhub": null,
  "ultimo_acceso": "2026-10-13T15:27:32-06:00"
}
```

**Explicación.** El trigger de auditoría registra el cambio con el usuario que actuó.

**Evidencia en PostgreSQL.** `SELECT id, telefono, actualizado_en FROM usuario WHERE id = 7`

```json
[
  {
    "id": 7,
    "telefono": "8112345678",
    "actualizado_en": "2026-10-13 21:27:34.349981+00:00"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT fecha, accion, entidad, detalle FROM auditoria WHERE entidad = 'usuario' AND entidad_id = '7' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "fecha": "2026-10-13 21:27:34.349981+00:00",
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
X-Traza-Id: 3c86ec34-e1f7-433b-a60b-b37bfc2acaa1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "telefono": "12ab"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 366 ms · traza `3c86ec34-e1f7-433b-a60b-b37bfc2acaa1`

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
    "traza_id": "3c86ec34-e1f7-433b-a60b-b37bfc2acaa1"
  }
}
```

### USR-05 · Lista de usuarios (administrador) · PASA

**Objetivo.** Búsqueda y paginación.

**Petición.** `GET http://usuarios:5102/api/v1/usuarios?q=codex&rol=operador&pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 317b003c-bb53-470f-81f1-b0246f746b22
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 96 ms · traza `317b003c-bb53-470f-81f1-b0246f746b22`

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
X-Traza-Id: f4aee7bc-281d-4be7-8680-a3044f41eefa
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 38 ms · traza `f4aee7bc-281d-4be7-8680-a3044f41eefa`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "f4aee7bc-281d-4be7-8680-a3044f41eefa"
  }
}
```

**Evidencia en PostgreSQL.** `SELECT fecha, modulo, accion, detalle, exitoso FROM auditoria WHERE accion = 'acceso_denegado' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "fecha": "2026-10-13 21:27:34.947836+00:00",
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
X-Traza-Id: 388c34d6-1754-4961-a9a5-3e3f040ebaa8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 36 ms · traza `388c34d6-1754-4961-a9a5-3e3f040ebaa8`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "388c34d6-1754-4961-a9a5-3e3f040ebaa8"
  }
}
```

## Servicio productos · puerto 5103

### PRO-01 · Productos con búsqueda (caché vacía) · PASA

**Objetivo.** Consultar productos; la respuesta se guarda en Redis.

**Petición.** `GET http://productos:5103/api/v1/productos?q=arroz&pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: a6accf2f-2ad8-4a75-ab14-bd2496b0a535
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 647 ms · traza `a6accf2f-2ad8-4a75-ab14-bd2496b0a535`

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
    "valor": 299
  }
]
```

### PRO-02 · Misma consulta (desde Redis) · PASA

**Objetivo.** La segunda consulta no toca PostgreSQL.

**Petición.** `GET http://productos:5103/api/v1/productos?q=arroz&pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 391dea8f-514e-4be4-892c-a8ec0e0d6856
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 6 ms · traza `391dea8f-514e-4be4-892c-a8ec0e0d6856`

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
X-Traza-Id: 4f68c4f4-e195-4daa-b058-4fe520b56766
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 84 ms · traza `4f68c4f4-e195-4daa-b058-4fe520b56766`

```xml
<?xml version='1.0' encoding='utf-8'?>
<productos xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><datos><producto><id>3</id><clave_interna>AB-003</clave_interna><nombre>Aceite vegetal</nombre><categoria><id>1</id><nombre>Abarrote básico</nombre></categoria><unidad>botella</unidad><presentacion>900 ml</presentacion><precio>42.00</precio><imagen_url xsi:nil="true" /><estatus>activo</estatus></producto><producto><id>2</id><clave_interna>AB-002</clave_interna><nombre>Arroz superextra</nombre><categoria><id>1</id><nombre>Abarrote básico</nombre></categoria><unidad>kg</unidad><presentacion>1 kg</presentacion><precio>29.90</precio><imagen_url xsi:nil="true" /><estatus>activo</estatus></producto></datos><paginacion><pagina>1</pagina><por_pagina>2</por_pagina><total>51</total><paginas>26</paginas></paginacion></productos>
```

### PRO-04 · Un producto · PASA

**Objetivo.** Detalle por id.

**Petición.** `GET http://productos:5103/api/v1/productos/3`

```http
Accept: application/json
X-Traza-Id: 71a4e67f-bdf4-476b-bb45-4440bdefaae7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 64 ms · traza `71a4e67f-bdf4-476b-bb45-4440bdefaae7`

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
X-Traza-Id: 2d6a2b9e-2728-4f9c-b71d-23dcdc7e1094
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 60 ms · traza `2d6a2b9e-2728-4f9c-b71d-23dcdc7e1094`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "2d6a2b9e-2728-4f9c-b71d-23dcdc7e1094"
  }
}
```

### PRO-06 · Paginación fuera de rango · PASA

**Objetivo.** por_pagina máximo 100.

**Petición.** `GET http://productos:5103/api/v1/productos?por_pagina=500`

```http
Accept: application/json
X-Traza-Id: c043f5a6-fad4-4c1b-92e7-52479513fdb1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 7 ms · traza `c043f5a6-fad4-4c1b-92e7-52479513fdb1`

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
    "traza_id": "c043f5a6-fad4-4c1b-92e7-52479513fdb1"
  }
}
```

### PRO-07 · Sin token · PASA

**Objetivo.** Todo endpoint protegido exige Authorization: Bearer.

**Petición.** `GET http://productos:5103/api/v1/productos`

```http
Accept: application/json
X-Traza-Id: db4ac512-cfd6-41b7-a964-8ad421542c8c
```

**Respuesta.** HTTP 401 (esperado 401) · 7 ms · traza `db4ac512-cfd6-41b7-a964-8ad421542c8c`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "Falta el encabezado Authorization: Bearer <token>.",
    "traza_id": "db4ac512-cfd6-41b7-a964-8ad421542c8c"
  }
}
```

## Servicio zonas · puerto 5108

### ZON-01 · Zonas (XML) · PASA

**Objetivo.** Colonias atendidas con centroide, válidas contra catalogos.xsd.

**Petición.** `GET http://zonas:5108/api/v1/zonas`

```http
Accept: application/xml
X-Traza-Id: 18fc7d0e-cda3-4668-a5bc-5db4f5dc71ac
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 514 ms · traza `18fc7d0e-cda3-4668-a5bc-5db4f5dc71ac`

```xml
<?xml version='1.0' encoding='utf-8'?>
<zonas xmlns="urn:microhubs:v1" version="1"><datos><zona><id>1</id><clave>ZN-SB01</clave><nombre>San Bernabé Centro</nombre><colonia>San Bernabé</colonia><codigo_postal>64100</codigo_postal><latitud>25.7455</latitud><longitud>-100.3585</longitud></zona><zona><id>2</id><clave>ZN-SB02</clave><nombre>Valles de San Bernabé</nombre><colonia>Valles de San Bernabé</colonia><codigo_postal>64103</codigo_postal><latitud>25.753</latitud><longitud>-100.369</longitud></zona><zona><id>3</id><clave>ZN-SB03</clave><nombre>Paseo de San Bernabé</nombre><colonia>Paseo de San Bernabé</colonia><codigo_postal>64103</codigo_postal><latitud>25.758</latitud><longitud>-100.3745</longitud></zona><zona><id>4</id><clave>ZN-SB04</clave><nombre>San Bernabé X (F-113)</nombre><colonia>San Bernabé X (F-113)</colonia><codigo_postal>64105</codigo_postal><latitud>25.7495</latitud><longitud>-100.38</longitud></zona></datos><paginacion><pagina>1</pagina><por_pagina>20</por_pagina><total>4</total><paginas>1</paginas></paginacion></zonas>
```

### ZON-02 · Una zona · PASA

**Objetivo.** Detalle por id.

**Petición.** `GET http://zonas:5108/api/v1/zonas/1`

```http
Accept: application/json
X-Traza-Id: abecd8ad-6d53-40ea-bdd8-6b08af34c9e4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 36 ms · traza `abecd8ad-6d53-40ea-bdd8-6b08af34c9e4`

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
X-Traza-Id: ff7da3ef-de28-46fd-af87-dbb90ec47ede
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 31 ms · traza `ff7da3ef-de28-46fd-af87-dbb90ec47ede`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "ff7da3ef-de28-46fd-af87-dbb90ec47ede"
  }
}
```

### ZON-04 · Sin token · PASA

**Objetivo.** Todo endpoint protegido exige Authorization: Bearer.

**Petición.** `GET http://zonas:5108/api/v1/zonas`

```http
Accept: application/json
X-Traza-Id: 2c454140-d641-4398-8140-b9902d475b06
```

**Respuesta.** HTTP 401 (esperado 401) · 6 ms · traza `2c454140-d641-4398-8140-b9902d475b06`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "Falta el encabezado Authorization: Bearer <token>.",
    "traza_id": "2c454140-d641-4398-8140-b9902d475b06"
  }
}
```

## Servicio microhubs · puerto 5109

### MIC-01 · Microhubs activos · PASA

**Objetivo.** Microhubs con coordenadas y radio.

**Petición.** `GET http://microhubs:5109/api/v1/microhubs?estatus=activo`

```http
Accept: application/json
X-Traza-Id: e9ab3e07-63ac-492b-9a53-124a9babf778
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 839 ms · traza `e9ab3e07-63ac-492b-9a53-124a9babf778`

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
X-Traza-Id: 7e2c0155-0260-484b-aa39-16338c54bcb8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 34 ms · traza `7e2c0155-0260-484b-aa39-16338c54bcb8`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "7e2c0155-0260-484b-aa39-16338c54bcb8"
  }
}
```

### MIC-03 · Sin token · PASA

**Objetivo.** Todo endpoint protegido exige Authorization: Bearer.

**Petición.** `GET http://microhubs:5109/api/v1/microhubs`

```http
Accept: application/json
X-Traza-Id: 6348355f-ccff-43b4-a23d-81730ecc3dfd
```

**Respuesta.** HTTP 401 (esperado 401) · 7 ms · traza `6348355f-ccff-43b4-a23d-81730ecc3dfd`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "Falta el encabezado Authorization: Bearer <token>.",
    "traza_id": "6348355f-ccff-43b4-a23d-81730ecc3dfd"
  }
}
```

## Servicio pedidos · puerto 5104

### PED-01 · Pedidos entregados (JSON) · PASA

**Objetivo.** Lista filtrada por estado y fechas.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos?estado=entregado&pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: defea63e-8c77-4ed8-99ef-21f2be1f8259
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 742 ms · traza `defea63e-8c77-4ed8-99ef-21f2be1f8259`

```json
{
  "datos": [
    {
      "id": 105,
      "folio": "PED-20261013-000105",
      "estado": "entregado",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "microhub_id": 2,
      "total": 148.0,
      "creado_en": "2026-10-12T20:34:56-06:00"
    },
    {
      "id": 18,
      "folio": "PED-20261013-000018",
      "estado": "entregado",
      "zona": {
        "id": 1,
        "nombre": "San Bernabé Centro"
      },
      "microhub_id": 1,
      "total": 180.5,
      "creado_en": "2026-10-12T19:26:41-06:00"
    },
    {
      "id": 91,
      "folio": "PED-20261013-000091",
      "estado": "entregado",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "microhub_id": 2,
      "total": 128.5,
      "creado_en": "2026-10-12T15:59:02-06:00"
    },
    {
      "id": 63,
      "folio": "PED-20261013-000063",
      "estado": "entregado",
      "zona": {
        "id": 3,
        "nombre": "Paseo de San Bernabé"
      },
      "microhub_id": 2,
      "total": 148.5,
      "creado_en": "2026-10-12T15:33:11-06:00"
    },
    {
      "id": 3,
      "folio": "PED-20261013-000003",
      "estado": "entregado",
      "zona": {
        "id": 3,
        "nombre": "Paseo de San Bernabé"
      },
      "microhub_id": 2,
      "total": 142.9,
      "creado_en": "2026-10-11T02:46:03-06:00"
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
X-Traza-Id: f1198f5c-7d1f-4e18-b56c-36bc4addfedf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 90 ms · traza `f1198f5c-7d1f-4e18-b56c-36bc4addfedf`

```xml
<?xml version='1.0' encoding='utf-8'?>
<pedidos xmlns="urn:microhubs:v1" version="1"><datos><pedido><id>105</id><folio>PED-20261013-000105</folio><estado>entregado</estado><zona><id>2</id><nombre>Valles de San Bernabé</nombre></zona><microhub_id>2</microhub_id><total>148.00</total><creado_en>2026-10-12T20:34:56-06:00</creado_en></pedido><pedido><id>18</id><folio>PED-20261013-000018</folio><estado>entregado</estado><zona><id>1</id><nombre>San Bernabé Centro</nombre></zona><microhub_id>1</microhub_id><total>180.50</total><creado_en>2026-10-12T19:26:41-06:00</creado_en></pedido></datos><paginacion><pagina>1</pagina><por_pagina>2</por_pagina><total>113</total><paginas>57</paginas></paginacion></pedidos>
```

### PED-03 · Detalle con líneas · PASA

**Objetivo.** Cliente, domicilio y líneas del pedido.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/105`

```http
Accept: application/json
X-Traza-Id: 7f192095-ad12-4b7d-9220-6e04e7ef2c19
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 94 ms · traza `7f192095-ad12-4b7d-9220-6e04e7ef2c19`

```json
{
  "id": 105,
  "folio": "PED-20261013-000105",
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
  "creado_en": "2026-10-12T20:34:56-06:00",
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
X-Traza-Id: f678da68-4ec6-42fa-a402-a7f3d5c00e77
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 309 ms · traza `f678da68-4ec6-42fa-a402-a7f3d5c00e77`

```json
{
  "pedido_id": 105,
  "eventos": [
    {
      "estado_anterior": null,
      "estado_nuevo": "creado",
      "usuario": null,
      "motivo": null,
      "fecha": "2026-10-12T20:34:56-06:00"
    },
    {
      "estado_anterior": "creado",
      "estado_nuevo": "asignado",
      "usuario": null,
      "motivo": null,
      "fecha": "2026-10-12T20:34:56-06:00"
    },
    {
      "estado_anterior": "asignado",
      "estado_nuevo": "en_preparacion",
      "usuario": null,
      "motivo": null,
      "fecha": "2026-10-12T20:34:56-06:00"
    },
    {
      "estado_anterior": "en_preparacion",
      "estado_nuevo": "en_ruta",
      "usuario": null,
      "motivo": null,
      "fecha": "2026-10-12T20:34:56-06:00"
    },
    {
      "estado_anterior": "en_ruta",
      "estado_nuevo": "entregado",
      "usuario": null,
      "motivo": null,
      "fecha": "2026-10-12T20:34:56-06:00"
    }
  ]
}
```

**Evidencia en PostgreSQL.** `SELECT fecha, estado_anterior, estado_nuevo, usuario_id FROM historial_estatus WHERE pedido_id = %s ORDER BY fecha, id`

```json
[
  {
    "fecha": "2026-10-13 02:34:56.678271+00:00",
    "estado_anterior": null,
    "estado_nuevo": "creado",
    "usuario_id": null
  },
  {
    "fecha": "2026-10-13 02:34:56.678271+00:00",
    "estado_anterior": "creado",
    "estado_nuevo": "asignado",
    "usuario_id": null
  },
  {
    "fecha": "2026-10-13 02:34:56.678271+00:00",
    "estado_anterior": "asignado",
    "estado_nuevo": "en_preparacion",
    "usuario_id": null
  },
  {
    "fecha": "2026-10-13 02:34:56.678271+00:00",
    "estado_anterior": "en_preparacion",
    "estado_nuevo": "en_ruta",
    "usuario_id": null
  },
  {
    "fecha": "2026-10-13 02:34:56.678271+00:00",
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
X-Traza-Id: 74ed6cde-7d74-4268-a421-ec5805811bbf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 11 ms · traza `74ed6cde-7d74-4268-a421-ec5805811bbf`

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
    "traza_id": "74ed6cde-7d74-4268-a421-ec5805811bbf"
  }
}
```

### PED-06 · Pedido fuera del ámbito · PASA

**Objetivo.** El operador del MH-01 no ve pedidos de otro microhub (RN22).

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/1`

```http
Accept: application/json
X-Traza-Id: 02f8990f-f088-4b67-8c84-5e3041063b90
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 35 ms · traza `02f8990f-f088-4b67-8c84-5e3041063b90`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el pedido o no está en tu ámbito.",
    "traza_id": "02f8990f-f088-4b67-8c84-5e3041063b90"
  }
}
```

**Explicación.** El ámbito lo decide PostgreSQL con fn_pedidos_visibles; el servicio no lo puede saltar.

### PED-07 · Cerrar desde pedidos · PASA

**Objetivo.** Los cierres de entrega solo se registran en el servicio de entregas.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/105/estado`

```http
Accept: application/json
X-Traza-Id: 505fe53a-6f77-46f0-93ef-b468bc19577b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "estado": "entregado"
}
```

**Respuesta.** HTTP 409 (esperado 409) · 11 ms · traza `505fe53a-6f77-46f0-93ef-b468bc19577b`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "El cierre de una entrega se registra con POST /api/v1/entregas/{id}/resultado.",
    "traza_id": "505fe53a-6f77-46f0-93ef-b468bc19577b"
  }
}
```

### PED-08 · Transición ilegal (regla del motor) · PASA

**Objetivo.** Un pedido entregado no puede regresar a preparación.

**Petición.** `PATCH http://pedidos:5104/api/v1/pedidos/2/estado`

```http
Accept: application/json
X-Traza-Id: a20da0f6-41eb-40f2-880e-c03433a26ec1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0Iiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "estado": "en_preparacion"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 76 ms · traza `a20da0f6-41eb-40f2-880e-c03433a26ec1`

```json
{
  "error": {
    "codigo": "REGLA_NEGOCIO",
    "mensaje": "RN20: transición ilegal entregado -> en_preparacion para el rol operador. El pedido PED-20261013-000002 conserva su estado.",
    "traza_id": "a20da0f6-41eb-40f2-880e-c03433a26ec1"
  }
}
```

**Explicación.** El trigger fn_valida_transicion de PostgreSQL rechaza la transición (RN20); el estado no cambia.

**Evidencia en PostgreSQL.** `SELECT id, folio, estado FROM pedido WHERE id = %s`

```json
[
  {
    "id": 2,
    "folio": "PED-20261013-000002",
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
X-Traza-Id: 3cf34327-5b01-4b85-b641-9491b7596d5f
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

**Respuesta.** HTTP 201 (esperado 201) · 125 ms · traza `3cf34327-5b01-4b85-b641-9491b7596d5f`

```json
{
  "id": "6acea24bbf5616d8602a1205",
  "nombre": "evidencia-entrega-129.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "129"
  },
  "subido_por": 7,
  "creado_en": "2026-10-13T15:27:39-06:00"
}
```

**Explicación.** Se valida que el contenido sea JPEG real, se calcula su SHA-256 y que la entrega sea del repartidor.

**Evidencia en MongoDB.** `db.documentos.findOne({_id: ObjectId('6acea24bbf5616d8602a1205')}, {contenido: 0})`

```json
{
  "_id": "6acea24bbf5616d8602a1205",
  "nombre": "evidencia-entrega-129.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "129"
  },
  "subido_por": 7,
  "creado_en": "2026-10-13 21:27:39.603000+00:00"
}
```

### DOC-02 · Subir evidencia de la segunda entrega · PASA

**Objetivo.** Evidencia para el cierre parcial.

**Petición.** `POST http://documentos:5107/api/v1/documentos`

```http
Accept: application/json
X-Traza-Id: 7a0ef7fd-feaa-4dd0-8048-08e3c8c00a9c
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

**Respuesta.** HTTP 201 (esperado 201) · 31 ms · traza `7a0ef7fd-feaa-4dd0-8048-08e3c8c00a9c`

```json
{
  "id": "6acea24bbf5616d8602a1208",
  "nombre": "evidencia-entrega-130.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "130"
  },
  "subido_por": 7,
  "creado_en": "2026-10-13T15:27:39-06:00"
}
```

### DOC-03 · Tipo de archivo falso · PASA

**Objetivo.** Un PDF declarado como JPEG se rechaza por su firma.

**Petición.** `POST http://documentos:5107/api/v1/documentos`

```http
Accept: application/json
X-Traza-Id: ab18d466-face-44db-bd40-830284d9f751
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

**Respuesta.** HTTP 422 (esperado 422) · 14 ms · traza `ab18d466-face-44db-bd40-830284d9f751`

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
    "traza_id": "ab18d466-face-44db-bd40-830284d9f751"
  }
}
```

### DOC-04 · Evidencia en entrega ajena · PASA

**Objetivo.** Un repartidor no adjunta a entregas de otro.

**Petición.** `POST http://documentos:5107/api/v1/documentos`

```http
Accept: application/json
X-Traza-Id: 9d4466ba-20e4-44c2-b2bc-3448a41fec5b
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

**Respuesta.** HTTP 403 (esperado 403) · 56 ms · traza `9d4466ba-20e4-44c2-b2bc-3448a41fec5b`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Solo puedes adjuntar evidencia a tus entregas.",
    "traza_id": "9d4466ba-20e4-44c2-b2bc-3448a41fec5b"
  }
}
```

### DOC-05 · Documento temporal · PASA

**Objetivo.** Documento que después se elimina.

**Petición.** `POST http://documentos:5107/api/v1/documentos`

```http
Accept: application/json
X-Traza-Id: 103784db-ee04-491b-9feb-0162f42a3b25
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

**Respuesta.** HTTP 201 (esperado 201) · 9 ms · traza `103784db-ee04-491b-9feb-0162f42a3b25`

```json
{
  "id": "6acea24c114e5b7d09dc7612",
  "nombre": "borrador.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "usuario",
    "id": "7"
  },
  "subido_por": 7,
  "creado_en": "2026-10-13T15:27:40-06:00"
}
```

### DOC-06 · Mis documentos · PASA

**Objetivo.** Filtro por referencia.

**Petición.** `GET http://documentos:5107/api/v1/documentos?referencia_tipo=entrega&referencia_id=129`

```http
Accept: application/json
X-Traza-Id: dc283371-be74-4755-a353-2a22a2d0f5d4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 54 ms · traza `dc283371-be74-4755-a353-2a22a2d0f5d4`

```json
{
  "datos": [
    {
      "id": "6acea24bbf5616d8602a1205",
      "nombre": "evidencia-entrega-129.jpg",
      "tipo_mime": "image/jpeg",
      "tamano_bytes": 276,
      "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
      "referencia": {
        "tipo": "entrega",
        "id": "129"
      },
      "subido_por": 7,
      "creado_en": "2026-10-13T15:27:39-06:00"
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

**Petición.** `GET http://documentos:5107/api/v1/documentos/6acea24bbf5616d8602a1205`

```http
Accept: application/xml
X-Traza-Id: a253f644-4cd7-4db7-b500-49935be8a4eb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 14 ms · traza `a253f644-4cd7-4db7-b500-49935be8a4eb`

```xml
<?xml version='1.0' encoding='utf-8'?>
<documento xmlns="urn:microhubs:v1" version="1"><id>6acea24bbf5616d8602a1205</id><nombre>evidencia-entrega-129.jpg</nombre><tipo_mime>image/jpeg</tipo_mime><tamano_bytes>276</tamano_bytes><sha256>7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc</sha256><referencia><tipo>entrega</tipo><id>129</id></referencia><subido_por>7</subido_por><creado_en>2026-10-13T15:27:39-06:00</creado_en></documento>
```

### DOC-08 · Contenido en Base64 · PASA

**Objetivo.** Recuperar el archivo.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6acea24bbf5616d8602a1205/contenido`

```http
Accept: application/json
X-Traza-Id: c97599f2-da2c-48a5-a038-5f854404987e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 8 ms · traza `c97599f2-da2c-48a5-a038-5f854404987e`

```json
{
  "id": "6acea24bbf5616d8602a1205",
  "nombre": "evidencia-entrega-129.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "129"
  },
  "subido_por": 7,
  "creado_en": "2026-10-13T15:27:39-06:00",
  "contenido_base64": "/9j/4AAQSkZJRgABAQAAAQABAAAAAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcY…(368 caracteres)"
}
```

### DOC-09 · Eliminar documento (DELETE) · PASA

**Objetivo.** Borrar un documento propio.

**Petición.** `DELETE http://documentos:5107/api/v1/documentos/6acea24c114e5b7d09dc7612`

```http
Accept: application/json
X-Traza-Id: f6546bac-8a4e-49df-9443-5acd5784ddd6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 40 ms · traza `f6546bac-8a4e-49df-9443-5acd5784ddd6`

```json
(sin cuerpo)
```

**Evidencia en MongoDB.** `db.documentos.countDocuments({_id: ObjectId('6acea24c114e5b7d09dc7612')})`

```json
0
```

### DOC-10 · Id inexistente · PASA

**Objetivo.** Registro que no existe.

**Petición.** `GET http://documentos:5107/api/v1/documentos/ffffffffffffffffffffffff`

```http
Accept: application/json
X-Traza-Id: 2bdb3d9a-3a45-46a7-927f-cc075a580e1b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 8 ms · traza `2bdb3d9a-3a45-46a7-927f-cc075a580e1b`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "2bdb3d9a-3a45-46a7-927f-cc075a580e1b"
  }
}
```

## Servicio seguimiento · puerto 5110

### SEG-01 · Enviar puntos GPS · PASA

**Objetivo.** Guardar el recorrido del repartidor en MongoDB.

**Petición.** `POST http://seguimiento:5110/api/v1/seguimiento/129/ubicaciones`

```http
Accept: application/json
X-Traza-Id: 51494dd9-a321-4954-9ffe-b87b081ddb8d
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
      "capturado_en": "2026-10-13T21:21:40+00:00"
    },
    {
      "latitud": 25.7486,
      "longitud": -100.3606,
      "precision_m": 8.0,
      "capturado_en": "2026-10-13T21:23:40+00:00"
    },
    {
      "latitud": 25.7491,
      "longitud": -100.3611,
      "precision_m": 8.5,
      "capturado_en": "2026-10-13T21:25:40+00:00"
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 83 ms · traza `51494dd9-a321-4954-9ffe-b87b081ddb8d`

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
    "capturado_en": "2026-10-13 21:21:40+00:00",
    "recibido_en": "2026-10-13 21:27:40.837000+00:00"
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
    "capturado_en": "2026-10-13 21:23:40+00:00",
    "recibido_en": "2026-10-13 21:27:40.837000+00:00"
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
    "capturado_en": "2026-10-13 21:25:40+00:00",
    "recibido_en": "2026-10-13 21:27:40.837000+00:00"
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
X-Traza-Id: fc69019a-25d0-45cf-8569-1fb57df3e5b6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 47 ms · traza `fc69019a-25d0-45cf-8569-1fb57df3e5b6`

```json
{
  "entrega_id": 129,
  "puntos": 3,
  "distancia_km": 0.16,
  "inicio": "2026-10-13T15:21:40-06:00",
  "fin": "2026-10-13T15:25:40-06:00",
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
X-Traza-Id: 10e577c3-d309-4e0e-b29e-797732d98bea
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4Iiwi…(296 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 29 ms · traza `10e577c3-d309-4e0e-b29e-797732d98bea`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe la entrega o no está asignada a ti.",
    "traza_id": "10e577c3-d309-4e0e-b29e-797732d98bea"
  }
}
```

### SEG-04 · Recorrido sin token · PASA

**Objetivo.** Todo endpoint protegido exige Authorization: Bearer.

**Petición.** `GET http://seguimiento:5110/api/v1/seguimiento/129/recorrido`

```http
Accept: application/json
X-Traza-Id: 61ce3820-12b6-49d5-a881-0f39e630e243
```

**Respuesta.** HTTP 401 (esperado 401) · 5 ms · traza `61ce3820-12b6-49d5-a881-0f39e630e243`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "Falta el encabezado Authorization: Bearer <token>.",
    "traza_id": "61ce3820-12b6-49d5-a881-0f39e630e243"
  }
}
```

## Servicio entregas · puerto 5105

### ENT-01 · Mis entregas · PASA

**Objetivo.** Paradas abiertas del repartidor en el turno de hoy (RN25).

**Petición.** `GET http://entregas:5105/api/v1/entregas/mias?pagina=1&por_pagina=20`

```http
Accept: application/json
X-Traza-Id: e82c0688-87db-448b-a0ba-18187091c397
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 174 ms · traza `e82c0688-87db-448b-a0ba-18187091c397`

```json
{
  "datos": [
    {
      "id": 129,
      "pedido_id": 153,
      "folio": "PED-20261013-000153",
      "estado_pedido": "en_ruta",
      "orden_parada": 1,
      "direccion": "Camino a San Bernabé 3818, San Bernabé X (F-113)",
      "zona": "San Bernabé X (F-113)",
      "distancia_km": 0.62,
      "minutos_estimados": 10.0,
      "total": 146.8
    },
    {
      "id": 130,
      "pedido_id": 154,
      "folio": "PED-20261013-000154",
      "estado_pedido": "en_ruta",
      "orden_parada": 2,
      "direccion": "Río Salinas 4110, Paseo de San Bernabé",
      "zona": "Paseo de San Bernabé",
      "distancia_km": 1.48,
      "minutos_estimados": 16.0,
      "total": 238.0
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
X-Traza-Id: 0e6c2b9a-bfe8-4ed0-bf3e-133182bc2c06
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 188 ms · traza `0e6c2b9a-bfe8-4ed0-bf3e-133182bc2c06`

```json
{
  "id": 129,
  "pedido_id": 153,
  "folio": "PED-20261013-000153",
  "estado_pedido": "en_ruta",
  "cliente": {
    "nombre": "Leticia González Chapa",
    "telefono": "8186734386"
  },
  "domicilio": {
    "calle": "Camino a San Bernabé",
    "numero_ext": "3818",
    "colonia": "San Bernabé X (F-113)",
    "latitud": 25.744103,
    "longitud": -100.377598
  },
  "orden_parada": 1,
  "distancia_km": 0.62,
  "minutos_estimados": 10.0,
  "total": 146.8,
  "lineas": [
    {
      "pedido_detalle_id": 683,
      "nombre": "Toallas femeninas",
      "cantidad": 2
    },
    {
      "pedido_detalle_id": 684,
      "nombre": "Arroz superextra",
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
X-Traza-Id: 11cad444-9c66-4020-986d-7b83dc54ede3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4Iiwi…(296 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 41 ms · traza `11cad444-9c66-4020-986d-7b83dc54ede3`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe la entrega o no está asignada a ti.",
    "traza_id": "11cad444-9c66-4020-986d-7b83dc54ede3"
  }
}
```

### ENT-04 · Monto incorrecto (regla de negocio) · PASA

**Objetivo.** Una entrega completa cobra el total (RN27).

**Petición.** `POST http://entregas:5105/api/v1/entregas/129/resultado`

```http
Accept: application/json
X-Traza-Id: 4381bc6d-65c5-4b75-bf49-fef3555f12d2
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
    "6acea24bbf5616d8602a1205"
  ],
  "capturado_en": "2026-10-13T21:27:40+00:00",
  "id_cliente_local": "1bec9a94-bc99-4e2f-9ee8-b54260ec32b5"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 96 ms · traza `4381bc6d-65c5-4b75-bf49-fef3555f12d2`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "monto_cobrado",
        "mensaje": "Una entrega completa cobra el total del pedido (146.80)."
      }
    ],
    "traza_id": "4381bc6d-65c5-4b75-bf49-fef3555f12d2"
  }
}
```

### ENT-05 · Cerrar entrega como entregado · PASA

**Objetivo.** Registrar el resultado con evidencia y ubicación.

**Petición.** `POST http://entregas:5105/api/v1/entregas/129/resultado`

```http
Accept: application/json
X-Traza-Id: ca8d9f63-7888-4513-87b6-4d3da30c1098
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 146.8,
  "cambio_entregado": 0.0,
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611,
    "precision_m": 8.5
  },
  "evidencia_ids": [
    "6acea24bbf5616d8602a1205"
  ],
  "capturado_en": "2026-10-13T21:27:40+00:00",
  "id_cliente_local": "1bec9a94-bc99-4e2f-9ee8-b54260ec32b5"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 151 ms · traza `ca8d9f63-7888-4513-87b6-4d3da30c1098`

```json
{
  "entrega_id": 129,
  "pedido_id": 153,
  "estado_pedido": "entregado",
  "cerrado_en": "2026-10-13T15:27:41-06:00",
  "duplicado": false
}
```

**Explicación.** Una sola transacción: cierra la entrega, cambia el pedido (el trigger valida la transición y escribe historial y bitácora) y el trigger de cierre avisa al cliente. La operación se registra en MongoDB.

**Evidencia en PostgreSQL.** `SELECT id, cierre_en, resultado, monto_cobrado, id_cliente_local, evidencia_ids, cierre_latitud, cierre_longitud FROM entrega WHERE id = %s`

```json
[
  {
    "id": 129,
    "cierre_en": "2026-10-13 21:27:41.588898+00:00",
    "resultado": "entregado",
    "monto_cobrado": "146.80",
    "id_cliente_local": "1bec9a94-bc99-4e2f-9ee8-b54260ec32b5",
    "evidencia_ids": [
      "6acea24bbf5616d8602a1205"
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
    "fecha": "2026-10-13 21:27:41.588898+00:00"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT destinatario_id, tipo, titulo, mensaje, referencia_tipo, referencia_id FROM web_notificacion WHERE referencia_tipo = 'pedido' AND referencia_id = %s ORDER BY id DESC LIMIT 1`

```json
[]
```

**Evidencia en MongoDB.** `db.sincronizaciones_moviles.findOne({operacion_uuid: '1bec9a94-bc99-4e2f-9ee8-b54260ec32b5'})`

```json
{
  "operacion_uuid": "1bec9a94-bc99-4e2f-9ee8-b54260ec32b5",
  "capturado_en": "2026-10-13 21:27:40+00:00",
  "carga": {
    "entrega_id": 129,
    "resultado": "entregado",
    "monto_cobrado": 146.8,
    "evidencia_ids": [
      "6acea24bbf5616d8602a1205"
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
  "sincronizado_en": "2026-10-13 21:27:41.658000+00:00",
  "tipo_operacion": "cierre_entrega",
  "usuario_id": 7
}
```

### ENT-06 · Reintento con el mismo UUID · PASA

**Objetivo.** Idempotencia: el cierre no se aplica dos veces.

**Petición.** `POST http://entregas:5105/api/v1/entregas/129/resultado`

```http
Accept: application/json
X-Traza-Id: fcc57583-d122-4a28-b36e-009c109c7f57
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 146.8,
  "cambio_entregado": 0.0,
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611,
    "precision_m": 8.5
  },
  "evidencia_ids": [
    "6acea24bbf5616d8602a1205"
  ],
  "capturado_en": "2026-10-13T21:27:40+00:00",
  "id_cliente_local": "1bec9a94-bc99-4e2f-9ee8-b54260ec32b5"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 77 ms · traza `fcc57583-d122-4a28-b36e-009c109c7f57`

```json
{
  "entrega_id": 129,
  "pedido_id": 153,
  "estado_pedido": "entregado",
  "cerrado_en": "2026-10-13T15:27:41-06:00",
  "duplicado": true
}
```

**Explicación.** La respuesta es la misma con duplicado=true. MongoDB actualiza el documento de la operación (intentos = 2).

**Evidencia en MongoDB.** `db.sincronizaciones_moviles.findOne({operacion_uuid: '1bec9a94-bc99-4e2f-9ee8-b54260ec32b5'}, {estado: 1, intentos: 1})`

```json
{
  "estado": "aplicada",
  "intentos": 2,
  "sincronizado_en": "2026-10-13 21:27:41.825000+00:00"
}
```

### ENT-07 · Otro cierre sobre la misma entrega · PASA

**Objetivo.** Conflicto: ya estaba cerrada con otra operación.

**Petición.** `POST http://entregas:5105/api/v1/entregas/129/resultado`

```http
Accept: application/json
X-Traza-Id: cb5440ad-2f93-43fa-981d-293845a850cd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 146.8,
  "cambio_entregado": 0.0,
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611,
    "precision_m": 8.5
  },
  "evidencia_ids": [
    "6acea24bbf5616d8602a1205"
  ],
  "capturado_en": "2026-10-13T21:27:40+00:00",
  "id_cliente_local": "8ca27640-39cb-41dd-9b77-7ed9ec1090a0"
}
```

**Respuesta.** HTTP 409 (esperado 409) · 72 ms · traza `cb5440ad-2f93-43fa-981d-293845a850cd`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "La entrega ya se cerró con otra operación.",
    "traza_id": "cb5440ad-2f93-43fa-981d-293845a850cd"
  }
}
```

### ENT-08 · Detalle tras el cierre · PASA

**Objetivo.** El repartidor deja de ver el domicilio (RN26).

**Petición.** `GET http://entregas:5105/api/v1/entregas/129`

```http
Accept: application/json
X-Traza-Id: f15d92be-6987-4c2c-b4af-a2fa80e10cf4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 35 ms · traza `f15d92be-6987-4c2c-b4af-a2fa80e10cf4`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "La entrega ya se cerró; su información ya no está disponible.",
    "traza_id": "f15d92be-6987-4c2c-b4af-a2fa80e10cf4"
  }
}
```

### ENT-09 · Parcial sin motivo · PASA

**Objetivo.** Cada línea devuelta necesita motivo (RN28).

**Petición.** `POST http://entregas:5105/api/v1/entregas/130/resultado`

```http
Accept: application/json
X-Traza-Id: 6d6eb9d2-da69-4415-b69c-cfe294084bcb
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
      "cantidad_entregada": 2,
      "cantidad_devuelta": 0
    },
    {
      "pedido_detalle_id": 686,
      "cantidad_entregada": 0,
      "cantidad_devuelta": 2
    }
  ],
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611
  },
  "evidencia_ids": [
    "6acea24bbf5616d8602a1208"
  ],
  "capturado_en": "2026-10-13T21:27:40+00:00",
  "id_cliente_local": "b2c05104-d016-4a63-a423-cf3f0546a85a"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 69 ms · traza `6d6eb9d2-da69-4415-b69c-cfe294084bcb`

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
    "traza_id": "6d6eb9d2-da69-4415-b69c-cfe294084bcb"
  }
}
```

### ENT-10 · Cerrar como entrega parcial · PASA

**Objetivo.** Devolver al inventario lo que no se entregó.

**Petición.** `POST http://entregas:5105/api/v1/entregas/130/resultado`

```http
Accept: application/json
X-Traza-Id: 4d38d71f-1bd1-4ae7-8c7d-af53554a6d13
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
      "cantidad_entregada": 2,
      "cantidad_devuelta": 0
    },
    {
      "pedido_detalle_id": 686,
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
    "6acea24bbf5616d8602a1208"
  ],
  "capturado_en": "2026-10-13T21:27:40+00:00",
  "id_cliente_local": "b2c05104-d016-4a63-a423-cf3f0546a85a"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 126 ms · traza `4d38d71f-1bd1-4ae7-8c7d-af53554a6d13`

```json
{
  "entrega_id": 130,
  "pedido_id": 154,
  "estado_pedido": "entrega_parcial",
  "cerrado_en": "2026-10-13T15:27:42-06:00",
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
    "cantidad_entregada": 2,
    "cantidad_devuelta": 0,
    "motivo": null
  },
  {
    "entrega_id": 130,
    "pedido_detalle_id": 686,
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
    "producto_id": 51,
    "cantidad": 2,
    "existencia_resultante": 75,
    "motivo": "Entrega parcial: regresan las unidades devueltas (RN28)."
  }
]
```

### ENT-11 · Entregas de un pedido (administrador) · PASA

**Objetivo.** Consulta por pedido para el portal web.

**Petición.** `GET http://entregas:5105/api/v1/entregas?pedido_id=153`

```http
Accept: application/json
X-Traza-Id: 5a639837-10dd-42dd-8d8c-669d3dd4b51f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 62 ms · traza `5a639837-10dd-42dd-8d8c-669d3dd4b51f`

```json
{
  "datos": [
    {
      "id": 129,
      "pedido_id": 153,
      "folio": "PED-20261013-000153",
      "estado_pedido": "entregado",
      "orden_parada": 1,
      "direccion": "Camino a San Bernabé 3818, San Bernabé X (F-113)",
      "zona": "San Bernabé X (F-113)",
      "distancia_km": 0.62,
      "minutos_estimados": 10.0,
      "total": 146.8
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
X-Traza-Id: 3e14b159-2971-4fbb-b3ad-f1a491d6b850
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 117 ms · traza `3e14b159-2971-4fbb-b3ad-f1a491d6b850`

```xml
<?xml version='1.0' encoding='utf-8'?>
<candidatos xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><datos><candidato><id>1</id><clave>CAND-01</clave><nombre>San Bernabé Norte</nombre><latitud>25.752</latitud><longitud>-100.361</longitud><renta_estimada>18000.00</renta_estimada><nomina_estimada>42000.00</nomina_estimada><servicios_estimados>7000.00</servicios_estimados><otros_costos>5000.00</otros_costos><costo_fijo>72000.00</costo_fijo><superficie_m2>130</superficie_m2><capacidad_fisica>150</capacidad_fisica><accesibilidad_vial>9</accesibilidad_vial><zona_id>1</zona_id><poblacion_cubierta>8420</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato><candidato><id>2</id><clave>CAND-02</clave><nombre>Valles Poniente</nombre><latitud>25.7555</latitud><longitud>-100.376</longitud><renta_estimada>15500.00</renta_estimada><nomina_estimada>42000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><costo_fijo>68500.00</costo_fijo><superficie_m2>105</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>2</zona_id><poblacion_cubierta>6180</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato><candidato><id>3</id><clave>CAND-05</clave><nombre>Alianza Real</nombre><latitud>25.7625</latitud><longitud>-100.353</longitud><renta_estimada>21000.00</renta_estimada><nomina_estimada>46000.00</nomina_estimada><servicios_estimados>8000.00</servicios_estimados><otros_costos>6000.00</otros_costos><costo_fijo>81000.00</costo_fijo><superficie_m2>150</superficie_m2><capacidad_fisica>180</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>3900</poblacion_cubierta><radio_km>1.6</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>5</total><paginas>2</paginas></paginacion></candidatos>
```

### PLA-02 · Registrar candidato (XML) · PASA

**Objetivo.** Alta con costo fijo calculado por PostgreSQL.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos`

```http
Accept: application/xml
X-Traza-Id: d6c50876-8376-4043-a7aa-21ec32863e79
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><candidato_nuevo xmlns="urn:microhubs:v1"><clave>********</clave><nombre>Alianza Norte</nombre><latitud>25.7601</latitud><longitud>-100.3555</longitud><renta_estimada>16000.00</renta_estimada><nomina_estimada>40000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><superficie_m2>110</superficie_m2><capacidad_fisica>130</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km></candidato_nuevo>
```

**Respuesta.** HTTP 201 (esperado 201) · 188 ms · traza `d6c50876-8376-4043-a7aa-21ec32863e79`

```xml
<?xml version='1.0' encoding='utf-8'?>
<candidato xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>16</id><clave>EV-FC84B1</clave><nombre>Alianza Norte</nombre><latitud>25.7601</latitud><longitud>-100.3555</longitud><renta_estimada>16000.00</renta_estimada><nomina_estimada>40000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><costo_fijo>67000.00</costo_fijo><superficie_m2>110</superficie_m2><capacidad_fisica>130</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato>
```

**Evidencia en PostgreSQL.** `SELECT id, clave, nombre, renta_estimada, costo_fijo, decision FROM ubicacion_candidata WHERE clave = %s`

```json
[
  {
    "id": 16,
    "clave": "EV-FC84B1",
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
X-Traza-Id: 85821a03-0ef1-4b7d-af54-d91b7b0d1af1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><candidato_nuevo xmlns="urn:microhubs:v1"><clave>********</clave><nombre>Alianza Norte</nombre><latitud>25.7601</latitud><longitud>-100.3555</longitud><renta_estimada>16000.00</renta_estimada><nomina_estimada>40000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><superficie_m2>110</superficie_m2><capacidad_fisica>130</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km></candidato_nuevo>
```

**Respuesta.** HTTP 409 (esperado 409) · 68 ms · traza `85821a03-0ef1-4b7d-af54-d91b7b0d1af1`

```xml
<?xml version='1.0' encoding='utf-8'?>
<error xmlns="urn:microhubs:v1" version="1"><codigo>CONFLICTO</codigo><mensaje>Ya existe un registro con esos datos.</mensaje><traza_id>85821a03-0ef1-4b7d-af54-d91b7b0d1af1</traza_id></error>
```

### PLA-04 · Modificar candidato (PUT) · PASA

**Objetivo.** Cambiar la renta recalcula el costo fijo.

**Petición.** `PUT http://planeacion:5106/api/v1/candidatos/16`

```http
Accept: application/json
X-Traza-Id: c7845f2b-7d3e-44bf-a8d5-1c10125acfb5
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

**Respuesta.** HTTP 200 (esperado 200) · 95 ms · traza `c7845f2b-7d3e-44bf-a8d5-1c10125acfb5`

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
X-Traza-Id: 7aee91ce-5f63-4ff6-a313-f3e44c8c2922
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<simular xmlns="urn:microhubs:v1"/>
```

**Respuesta.** HTTP 200 (esperado 200) · 321 ms · traza `7aee91ce-5f63-4ff6-a313-f3e44c8c2922`

```xml
<?xml version='1.0' encoding='utf-8'?>
<resultados xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><atendidos>0</atendidos><rechazados>0</rechazados><utilizacion>0</utilizacion><nivel>estable</nivel><tiempo_estimado_min>18.6</tiempo_estimado_min><operadores_requeridos>0</operadores_requeridos><repartidores_requeridos>0</repartidores_requeridos><ingreso_dia>0.00</ingreso_dia><margen_dia>-2300.00</margen_dia><costo_por_pedido xsi:nil="true" /><equilibrio><margen_pedido>24.04</margen_pedido><mensual>2869.6</mensual><diario>95.7</diario></equilibrio><decision>NO VIABLE CON LOS SUPUESTOS ACTUALES</decision><explicacion><motivo>la demanda atendida (0/día) no alcanza el equilibrio (96/día)</motivo><motivo>reducir costos fijos, aumentar ticket o buscar una ubicación con más demanda</motivo></explicacion></resultados>
```

**Explicación.** Usa planeacion_calc.py (las mismas fórmulas del web) y guarda la ejecución en MongoDB.

**Evidencia en MongoDB.** `db.ejecuciones_analiticas.find().sort({ejecutado_en: -1}).limit(1)`

```json
{
  "escenario_id": "candidato-16",
  "nombre_escenario": "Candidato 16",
  "tipo_analisis": "punto_equilibrio",
  "ejecutado_en": "2026-10-13 21:27:43.055000+00:00",
  "usuario_id": 5,
  "version_modelo": "planeacion_calc 2.1",
  "parametros_entrada": {
    "demanda_diaria": 0.0,
    "operadores": 3.0,
    "repartidores": 3.0,
    "ticket": 150.16,
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
    "ticket = 150.16",
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
    "equilibrio_diario": 95.7,
    "costo_por_pedido": null
  },
  "recomendacion": "NO VIABLE CON LOS SUPUESTOS ACTUALES",
  "datos_suficientes": true,
  "duracion_ms": 1,
  "aplicado_por": null
}
```

### PLA-06 · Decisión sin motivo suficiente · PASA

**Objetivo.** La decisión humana exige motivo.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/16/decision`

```http
Accept: application/json
X-Traza-Id: 23ffe819-0ced-4ce4-b70e-2d22e2968e29
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aceptado",
  "motivo": "ok"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 27 ms · traza `23ffe819-0ced-4ce4-b70e-2d22e2968e29`

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
    "traza_id": "23ffe819-0ced-4ce4-b70e-2d22e2968e29"
  }
}
```

### PLA-07 · Decisión humana de apertura · PASA

**Objetivo.** Registrar la decisión con motivo.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/16/decision`

```http
Accept: application/json
X-Traza-Id: 7454272b-ac47-4c08-80a8-a330a5e91c67
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "condicionado",
  "motivo": "Renegociar la renta antes de firmar."
}
```

**Respuesta.** HTTP 200 (esperado 200) · 60 ms · traza `7454272b-ac47-4c08-80a8-a330a5e91c67`

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
    "decision_en": "2026-10-13 21:27:43.134770+00:00"
  }
]
```

### PLA-08 · Simulación libre: Escenario A · PASA

**Objetivo.** Punto de equilibrio del caso de la retroalimentación.

**Petición.** `POST http://planeacion:5106/api/v1/simulaciones`

```http
Accept: application/json
X-Traza-Id: 52501209-b796-4ef2-ac68-f2ad30a0427d
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

**Respuesta.** HTTP 200 (esperado 200) · 32 ms · traza `52501209-b796-4ef2-ac68-f2ad30a0427d`

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
X-Traza-Id: ded24b30-a87e-4ea5-b1a9-b1b1fdc0c6ba
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

**Respuesta.** HTTP 201 (esperado 201) · 109 ms · traza `ded24b30-a87e-4ea5-b1a9-b1b1fdc0c6ba`

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
  "creado_en": "2026-10-13T15:27:43-06:00"
}
```

### PLA-10 · Abrir escenario (XML) · PASA

**Objetivo.** Escenario con supuestos y resultados.

**Petición.** `GET http://planeacion:5106/api/v1/escenarios/1`

```http
Accept: application/xml
X-Traza-Id: 82e4df7d-3487-4957-9f2f-17b0586a57ea
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 24 ms · traza `82e4df7d-3487-4957-9f2f-17b0586a57ea`

```xml
<?xml version='1.0' encoding='utf-8'?>
<escenario xmlns="urn:microhubs:v1" version="1"><id>1</id><nombre>Escenario A - evidencias</nombre><candidato_id>16</candidato_id><supuestos><demanda_diaria>120</demanda_diaria><operadores>3</operadores><repartidores>4</repartidores><ticket>135.00</ticket><costo_entrega>22.00</costo_entrega><margen_bruto>0.28</margen_bruto><renta>18000.00</renta><nomina>42000.00</nomina><servicios>7000.00</servicios><otros>5000.00</otros><distancia_km>2.4</distancia_km><capacidad_fisica>150</capacidad_fisica></supuestos><resultados><atendidos>120</atendidos><rechazados>0</rechazados><utilizacion>80</utilizacion><nivel>atencion</nivel><tiempo_estimado_min>19.4</tiempo_estimado_min><operadores_requeridos>3</operadores_requeridos><repartidores_requeridos>2</repartidores_requeridos><ingreso_dia>16200.00</ingreso_dia><margen_dia>-504.00</margen_dia><costo_por_pedido>42.00</costo_por_pedido><equilibrio><margen_pedido>15.80</margen_pedido><mensual>4557</mensual><diario>151.9</diario></equilibrio><decision>NO VIABLE CON LOS SUPUESTOS ACTUALES</decision><explicacion><motivo>la demanda atendida (120/día) no alcanza el equilibrio (152/día)</motivo><motivo>el espacio físico del local limita la capacidad</motivo><motivo>reducir costos fijos, aumentar ticket o buscar una ubicación con más demanda</motivo></explicacion></resultados><creado_en>2026-10-13T15:27:43-06:00</creado_en></escenario>
```

### PLA-11 · Resumen de simulaciones · PASA

**Objetivo.** Agregación $group en MongoDB por decisión.

**Petición.** `GET http://planeacion:5106/api/v1/simulaciones/resumen`

```http
Accept: application/json
X-Traza-Id: d2e33a25-9529-49e9-a4a5-00cf52a84f76
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 18 ms · traza `d2e33a25-9529-49e9-a4a5-00cf52a84f76`

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
X-Traza-Id: c390afad-1958-4986-a937-e05681b16ddc
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

**Respuesta.** HTTP 403 (esperado 403) · 33 ms · traza `c390afad-1958-4986-a937-e05681b16ddc`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "c390afad-1958-4986-a937-e05681b16ddc"
  }
}
```

### PLA-13 · Auditor intenta simular · PASA

**Objetivo.** Sin simulacion.ejecutar.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/16/simular`

```http
Accept: application/json
X-Traza-Id: 2f16f7e6-e648-4f6b-9054-abf6c25a5a1f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 403 (esperado 403) · 29 ms · traza `2f16f7e6-e648-4f6b-9054-abf6c25a5a1f`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "2f16f7e6-e648-4f6b-9054-abf6c25a5a1f"
  }
}
```

### PLA-14 · Eliminar escenario (DELETE) · PASA

**Objetivo.** Borrar un escenario.

**Petición.** `DELETE http://planeacion:5106/api/v1/escenarios/1`

```http
Accept: application/json
X-Traza-Id: 9dc4c3be-6e32-4db7-b7ec-2ba82690c793
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 50 ms · traza `9dc4c3be-6e32-4db7-b7ec-2ba82690c793`

```json
(sin cuerpo)
```

### PLA-15 · Dar de baja candidato (DELETE) · PASA

**Objetivo.** Baja lógica: se conserva su historia.

**Petición.** `DELETE http://planeacion:5106/api/v1/candidatos/16`

```http
Accept: application/json
X-Traza-Id: 4a28cf6f-0b4a-4fe3-b687-c817793a7f05
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 84 ms · traza `4a28cf6f-0b4a-4fe3-b687-c817793a7f05`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT id, clave, estatus, decision FROM ubicacion_candidata WHERE id = %s`

```json
[
  {
    "id": 16,
    "clave": "EV-FC84B1",
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
X-Traza-Id: 9f09ac1e-e7d4-43d4-9c51-027ad5013f3a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 155 ms · traza `9f09ac1e-e7d4-43d4-9c51-027ad5013f3a`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el candidato.",
    "traza_id": "9f09ac1e-e7d4-43d4-9c51-027ad5013f3a"
  }
}
```

## Servicio auth · puerto 5101

### SAL-AUT · Salud de auth · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://auth:5101/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 0711bfb5-ada7-4532-9207-25656cca4c68
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `0711bfb5-ada7-4532-9207-25656cca4c68`

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
X-Traza-Id: 9a9b45cb-63c7-4cab-ac2b-f7314fa71ce6
```

**Respuesta.** HTTP 200 (esperado 200) · 18 ms · traza `9a9b45cb-63c7-4cab-ac2b-f7314fa71ce6`

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
X-Traza-Id: f43a3f9c-83b7-45b4-8daa-9306a4a73b28
```

**Respuesta.** HTTP 200 (esperado 200) · 32 ms · traza `f43a3f9c-83b7-45b4-8daa-9306a4a73b28`

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
X-Traza-Id: 2968864a-27ab-4366-b7fc-7921ec58e47e
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `2968864a-27ab-4366-b7fc-7921ec58e47e`

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
X-Traza-Id: 2cc5f595-e623-4e21-8d59-45ebebeac82a
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `2cc5f595-e623-4e21-8d59-45ebebeac82a`

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
X-Traza-Id: 4451c503-704a-4636-b4eb-2baccedd3f8e
```

**Respuesta.** HTTP 200 (esperado 200) · 18 ms · traza `4451c503-704a-4636-b4eb-2baccedd3f8e`

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
X-Traza-Id: 466feb21-c008-4beb-9e29-23b1b2ac5634
```

**Respuesta.** HTTP 200 (esperado 200) · 18 ms · traza `466feb21-c008-4beb-9e29-23b1b2ac5634`

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
X-Traza-Id: db540f44-c95c-4849-9dcd-ccbef9c3ef02
```

**Respuesta.** HTTP 200 (esperado 200) · 26 ms · traza `db540f44-c95c-4849-9dcd-ccbef9c3ef02`

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
X-Traza-Id: 24bc704d-6248-4d0f-89e7-1de7eec8aa81
```

**Respuesta.** HTTP 200 (esperado 200) · 19 ms · traza `24bc704d-6248-4d0f-89e7-1de7eec8aa81`

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
X-Traza-Id: c10147b8-3f8a-4bfb-a925-97543ca76e68
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `c10147b8-3f8a-4bfb-a925-97543ca76e68`

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

## Servicio auth · puerto 5101

### MON-01 · Registro de actividad · PASA

**Objetivo.** Cada petición queda en MongoDB con su traza.

**Petición.** `GET http://auth:5101/api/v1/auth/validar`

```http
Accept: application/json
X-Traza-Id: 7860f153-17bc-414b-a9c4-4f52e1452719
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 5 ms · traza `7860f153-17bc-414b-a9c4-4f52e1452719`

```json
{
  "valido": true,
  "expira_en": 890,
  "usuario": {
    "id": 1,
    "rol": "administrador",
    "microhub_id": null
  }
}
```

**Explicación.** El X-Traza-Id de la petición se recupera en logs_tecnicos.correlacion_id.

**Evidencia en MongoDB.** `db.logs_tecnicos.findOne({correlacion_id: '7860f153-17bc-414b-a9c4-4f52e1452719'})`

```json
{
  "nivel": "INFO",
  "componente": "auth",
  "registrado_en": "2026-10-13 21:27:43.953000+00:00",
  "correlacion_id": "7860f153-17bc-414b-a9c4-4f52e1452719",
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
    "_id": "auth",
    "peticiones": 18,
    "ms_promedio": 221.44444444444446
  },
  {
    "_id": "documentos",
    "peticiones": 10,
    "ms_promedio": 29.6
  },
  {
    "_id": "entregas",
    "peticiones": 12,
    "ms_promedio": 90.25
  },
  {
    "_id": "microhubs",
    "peticiones": 3,
    "ms_promedio": 68.0
  },
  {
    "_id": "pedidos",
    "peticiones": 8,
    "ms_promedio": 69.375
  },
  {
    "_id": "planeacion",
    "peticiones": 16,
    "ms_promedio": 77.625
  },
  {
    "_id": "productos",
    "peticiones": 7,
    "ms_promedio": 48.0
  },
  {
    "_id": "seguimiento",
    "peticiones": 4,
    "ms_promedio": 35.25
  },
  {
    "_id": "usuarios",
    "peticiones": 8,
    "ms_promedio": 47.125
  },
  {
    "_id": "zonas",
    "peticiones": 4,
    "ms_promedio": 46.5
  }
]
```

## Servicio zonas · puerto 5108

### RAT-01 · Límite de consumo excedido · PASA

**Objetivo.** Más de 240 solicitudes por minuto desde la misma IP.

**Petición.** `GET http://zonas:5108/api/v1/zonas`

```http
Accept: application/json
X-Traza-Id: 08471f50-02aa-496f-bf9d-ab2edfc30c5d
```

**Respuesta.** HTTP 429 (esperado 429) · 4 ms · traza `08471f50-02aa-496f-bf9d-ab2edfc30c5d`

```json
{
  "error": {
    "codigo": "LIMITE_EXCEDIDO",
    "mensaje": "Máximo 240 solicitudes por minuto. Espera 13 segundos.",
    "traza_id": "08471f50-02aa-496f-bf9d-ab2edfc30c5d"
  }
}
```

**Explicación.** Contador rate:zonas:{ip}:{minuto} en Redis (db 1) con TTL de 120 s; responde Retry-After.

**Evidencia en Redis.** `db1 GET rate:zonas:01e0126676ba0221:29865447; db1 TTL rate:zonas:01e0126676ba0221:29865447`

```json
[
  {
    "comando": "db1 GET rate:zonas:01e0126676ba0221:29865447",
    "valor": "242"
  },
  {
    "comando": "db1 TTL rate:zonas:01e0126676ba0221:29865447",
    "valor": 110
  }
]
```
