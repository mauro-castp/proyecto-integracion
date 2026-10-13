# Evidencias de petición y respuesta · microservicios v1

Generado el 2026-10-13 14:12 contra los servicios en ejecución. 93 de 93 casos pasan.

## Servicio auth · puerto 5101

### AUTH-01 · Iniciar sesión (JSON) · PASA

**Objetivo.** Emitir el JWT de acceso y el token de renovación del repartidor.

**Petición.** `POST http://auth:5101/api/v1/auth/login`

```http
Accept: application/json
X-Traza-Id: 00ed5311-52c7-4b8c-b159-c0160301ecac
Content-Type: application/json
```

```json
{
  "correo": "repartidor1@codex.mx",
  "clave": "********",
  "dispositivo": "Pixel 7"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 417 ms · traza `00ed5311-52c7-4b8c-b159-c0160301ecac`

```json
{
  "token_acceso": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwicm9sIjo…(291 caracteres)",
  "token_renovacion": "rt_f3558c330c96be0d10b2e9c5c5592fda",
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

**Evidencia en Redis.** `SMEMBERS auth:sesion:7; TTL auth:sesion:7; TTL auth:refresh:4d48abd90481262657b62a850cb9a2b71ca9f98bcc850f8f40d75d33f0a89b1b`

```json
[
  {
    "comando": "SMEMBERS auth:sesion:7",
    "valor": [
      "c5c90ba624184b6eb098ccacab3f9ca7"
    ]
  },
  {
    "comando": "TTL auth:sesion:7",
    "valor": 900
  },
  {
    "comando": "TTL auth:refresh:4d48abd90481262657b62a850cb9a2b71ca9f98bcc850f8f40d75d33f0a89b1b",
    "valor": 604800
  }
]
```

**Evidencia en PostgreSQL.** `SELECT fecha, modulo, accion, detalle FROM auditoria WHERE correo_intento IS NULL AND usuario_id = 7 AND modulo = 'auth' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "fecha": "2026-10-13 14:11:59.823065+00:00",
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
X-Traza-Id: 4371b0ff-0b8c-4437-8272-609d71302ff0
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><login xmlns="urn:microhubs:v1"><correo>planeador@codex.mx</correo><clave>********</clave></login>
```

**Respuesta.** HTTP 200 (esperado 200) · 290 ms · traza `4371b0ff-0b8c-4437-8272-609d71302ff0`

```xml
<?xml version='1.0' encoding='utf-8'?>
<sesion xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><token_acceso>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwicm9sIjo…(291 caracteres)</token_acceso><token_renovacion>rt_47b149e07a8361828c13c193ace14aac</token_renovacion><tipo>Bearer</tipo><expira_en>900</expira_en><usuario><id>5</id><nombre>Vanessa</nombre><apellidos>Morante López</apellidos><correo>planeador@codex.mx</correo><rol>planeador</rol><microhub_id xsi:nil="true" /><permisos><permiso>archivos.crear</permiso><permiso>archivos.ver</permiso><permiso>catalogo_publico.ver</permiso><permiso>configuracion.ver</permiso><permiso>indicadores.ver</permiso><permiso>inventario.ver</permiso><permiso>microhubs.ver</permiso><permiso>notificaciones.ver</permiso><permiso>pedidos.reasignar</permiso><permiso>pedidos.ver</permiso><permiso>planeacion.editar</permiso><permiso>planeacion.ver</permiso><permiso>productos.ver</permiso><permiso>reportes.exportar</permiso><permiso>reportes.ver</permiso><permiso>simulacion.ejecutar</permiso><permiso>simulacion.ver</permiso><permiso>zonas.ver</permiso></permisos></usuario></sesion>
```

**Explicación.** El cuerpo XML se valida contra los XSD antes de procesarse; la respuesta <sesion> también cumple el XSD.

### AUTH-03 · Clave incorrecta · PASA

**Objetivo.** Rechazar credenciales y contar el intento.

**Petición.** `POST http://auth:5101/api/v1/auth/login`

```http
Accept: application/json
X-Traza-Id: e881a156-51d9-48f7-80d3-380c99ad054e
Content-Type: application/json
```

```json
{
  "correo": "auditor@codex.mx",
  "clave": "********"
}
```

**Respuesta.** HTTP 401 (esperado 401) · 161 ms · traza `e881a156-51d9-48f7-80d3-380c99ad054e`

```json
{
  "error": {
    "codigo": "CREDENCIALES_INVALIDAS",
    "mensaje": "Correo o clave incorrectos. Intento 1 de 5.",
    "traza_id": "e881a156-51d9-48f7-80d3-380c99ad054e"
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
X-Traza-Id: d3bf58cb-21ad-459c-b73e-09ca46ada6b3
Content-Type: application/json
```

```json
{
  "correo": "sin-arroba",
  "clave": "********"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 3 ms · traza `d3bf58cb-21ad-459c-b73e-09ca46ada6b3`

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
    "traza_id": "d3bf58cb-21ad-459c-b73e-09ca46ada6b3"
  }
}
```

### AUTH-05 · XML con DTD (ataque XXE) · PASA

**Objetivo.** Rechazar entidades externas y DTD.

**Petición.** `POST http://auth:5101/api/v1/auth/login`

```http
Accept: application/xml
X-Traza-Id: a50c4a3c-66e4-45cd-9fb5-37d32a53ba04
Content-Type: application/xml
```

```xml
<?xml version="1.0"?><!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]><login xmlns="urn:microhubs:v1"><correo>&e;</correo><clave>********</clave></login>
```

**Respuesta.** HTTP 400 (esperado 400) · 4 ms · traza `a50c4a3c-66e4-45cd-9fb5-37d32a53ba04`

```xml
<?xml version='1.0' encoding='utf-8'?>
<error xmlns="urn:microhubs:v1" version="1"><codigo>XML_INVALIDO</codigo><mensaje>El cuerpo XML no está bien formado o contiene DTD/entidades.</mensaje><traza_id>a50c4a3c-66e4-45cd-9fb5-37d32a53ba04</traza_id></error>
```

**Explicación.** El lector XML (defusedxml) prohíbe DTD y entidades; el error también llega en XML.

### AUTH-06 · Validar token · PASA

**Objetivo.** Comprobar firma, vigencia y sesión activa en Redis.

**Petición.** `GET http://auth:5101/api/v1/auth/validar`

```http
Accept: application/json
X-Traza-Id: 96fd3586-a4fa-447e-ac43-2dcd3ed6b98c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 4 ms · traza `96fd3586-a4fa-447e-ac43-2dcd3ed6b98c`

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
X-Traza-Id: 95c5d297-2eea-40d0-8f02-f651ff7cb532
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 401 (esperado 401) · 3 ms · traza `95c5d297-2eea-40d0-8f02-f651ff7cb532`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.",
    "traza_id": "95c5d297-2eea-40d0-8f02-f651ff7cb532"
  }
}
```

### AUTH-08 · Renovar sesión · PASA

**Objetivo.** Obtener tokens nuevos con el token de renovación (rotación).

**Petición.** `POST http://auth:5101/api/v1/auth/renovar`

```http
Accept: application/json
X-Traza-Id: 997caac8-b7aa-4deb-8983-3c3d45659f7c
Content-Type: application/json
```

```json
{
  "token_renovacion": "rt_41edd150a3235a49dee6f71541a43863"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 53 ms · traza `997caac8-b7aa-4deb-8983-3c3d45659f7c`

```json
{
  "token_acceso": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwicm9sIjo…(291 caracteres)",
  "token_renovacion": "rt_36ed13be77aa358d4d76c7f38c7770f2",
  "tipo": "Bearer",
  "expira_en": 900
}
```

**Explicación.** El token de renovación usado se borra de Redis y su acceso anterior queda revocado.

**Evidencia en Redis.** `EXISTS auth:refresh:2fc25c071527034cf85ce5ec3301350b5615371bf1dc43d431cbaddc0288321a`

```json
[
  {
    "comando": "EXISTS auth:refresh:2fc25c071527034cf85ce5ec3301350b5615371bf1dc43d431cbaddc0288321a",
    "valor": 0
  }
]
```

### AUTH-09 · Reusar un token de renovación · PASA

**Objetivo.** Un token de renovación sirve una sola vez.

**Petición.** `POST http://auth:5101/api/v1/auth/renovar`

```http
Accept: application/json
X-Traza-Id: 89a16a4e-632d-46b8-a182-8e2610728e74
Content-Type: application/json
```

```json
{
  "token_renovacion": "rt_41edd150a3235a49dee6f71541a43863"
}
```

**Respuesta.** HTTP 401 (esperado 401) · 4 ms · traza `89a16a4e-632d-46b8-a182-8e2610728e74`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.",
    "traza_id": "89a16a4e-632d-46b8-a182-8e2610728e74"
  }
}
```

### AUTH-10 · Cerrar sesión · PASA

**Objetivo.** Revocar el acceso del encabezado y la renovación del cuerpo.

**Petición.** `POST http://auth:5101/api/v1/auth/salir`

```http
Accept: application/json
X-Traza-Id: 7b572420-4ea8-4f50-a6e1-c0b7cf19db7e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "token_renovacion": "rt_36ed13be77aa358d4d76c7f38c7770f2"
}
```

**Respuesta.** HTTP 204 (esperado 204) · 21 ms · traza `7b572420-4ea8-4f50-a6e1-c0b7cf19db7e`

```json
(sin cuerpo)
```

**Explicación.** El jti se agrega a la lista de revocados con TTL igual a su vida restante y sale del conjunto de sesión.

**Evidencia en Redis.** `TTL auth:jti:revocado:c768c882c2bf475cb0868d47a8dff499; SISMEMBER auth:sesion:7 c768c882c2bf475cb0868d47a8dff499`

```json
[
  {
    "comando": "TTL auth:jti:revocado:c768c882c2bf475cb0868d47a8dff499",
    "valor": 899
  },
  {
    "comando": "SISMEMBER auth:sesion:7 c768c882c2bf475cb0868d47a8dff499",
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
X-Traza-Id: 287e5e6b-ef87-4d06-965a-bc44da500c1f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 401 (esperado 401) · 131 ms · traza `287e5e6b-ef87-4d06-965a-bc44da500c1f`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.",
    "traza_id": "287e5e6b-ef87-4d06-965a-bc44da500c1f"
  }
}
```

**Explicación.** El servicio de usuarios consulta auth:jti:revocado en Redis: la revocación es común a todos.

### USR-01 · Mi perfil (JSON) · PASA

**Objetivo.** Consultar el perfil de quien inició sesión.

**Petición.** `GET http://usuarios:5102/api/v1/usuarios/yo`

```http
Accept: application/json
X-Traza-Id: 8c00dff4-987d-4c0b-b209-aa385ee7998f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 27 ms · traza `8c00dff4-987d-4c0b-b209-aa385ee7998f`

```json
{
  "id": 7,
  "nombre": "Ramiro",
  "apellidos": "Alanís Lozano",
  "correo": "repartidor1@codex.mx",
  "telefono": "8114641034",
  "rol": "repartidor",
  "microhub": null,
  "ultimo_acceso": "2026-10-13T08:12:00-06:00"
}
```

### USR-02 · Mi perfil (XML) · PASA

**Objetivo.** El mismo recurso en XML según Accept.

**Petición.** `GET http://usuarios:5102/api/v1/usuarios/yo`

```http
Accept: application/xml
X-Traza-Id: 88f3ff63-11ae-4834-a698-6a6678f01fcf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 26 ms · traza `88f3ff63-11ae-4834-a698-6a6678f01fcf`

```xml
<?xml version='1.0' encoding='utf-8'?>
<usuario xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>5</id><nombre>Vanessa</nombre><apellidos>Morante López</apellidos><correo>planeador@codex.mx</correo><telefono>8178109897</telefono><rol>planeador</rol><microhub xsi:nil="true" /><ultimo_acceso>2026-10-13T08:12:01-06:00</ultimo_acceso></usuario>
```

### USR-03 · Actualizar mi teléfono (PATCH) · PASA

**Objetivo.** Modificar un dato del perfil.

**Petición.** `PATCH http://usuarios:5102/api/v1/usuarios/yo`

```http
Accept: application/json
X-Traza-Id: 62fb103d-e448-4a02-bc2a-d55a35154760
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "telefono": "8112345678"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 79 ms · traza `62fb103d-e448-4a02-bc2a-d55a35154760`

```json
{
  "id": 7,
  "nombre": "Ramiro",
  "apellidos": "Alanís Lozano",
  "correo": "repartidor1@codex.mx",
  "telefono": "8112345678",
  "rol": "repartidor",
  "microhub": null,
  "ultimo_acceso": "2026-10-13T08:12:00-06:00"
}
```

**Explicación.** El trigger de auditoría registra el cambio con el usuario que actuó.

**Evidencia en PostgreSQL.** `SELECT id, telefono, actualizado_en FROM usuario WHERE id = 7`

```json
[
  {
    "id": 7,
    "telefono": "8112345678",
    "actualizado_en": "2026-10-13 14:12:01.779540+00:00"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT fecha, accion, entidad, detalle FROM auditoria WHERE entidad = 'usuario' AND entidad_id = '7' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "fecha": "2026-10-13 14:12:01.779540+00:00",
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
X-Traza-Id: 54ed1f66-134b-4fbc-a94f-43f5f387cd9d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "telefono": "12ab"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 96 ms · traza `54ed1f66-134b-4fbc-a94f-43f5f387cd9d`

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
    "traza_id": "54ed1f66-134b-4fbc-a94f-43f5f387cd9d"
  }
}
```

### USR-05 · Lista de usuarios (administrador) · PASA

**Objetivo.** Búsqueda y paginación.

**Petición.** `GET http://usuarios:5102/api/v1/usuarios?q=codex&rol=operador&pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 2050fe80-5b9a-4df9-a436-70d22455413a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 58 ms · traza `2050fe80-5b9a-4df9-a436-70d22455413a`

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
X-Traza-Id: 70ef2d61-7d28-467c-8288-1d60252fe434
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 27 ms · traza `70ef2d61-7d28-467c-8288-1d60252fe434`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "70ef2d61-7d28-467c-8288-1d60252fe434"
  }
}
```

**Evidencia en PostgreSQL.** `SELECT fecha, modulo, accion, detalle, exitoso FROM auditoria WHERE accion = 'acceso_denegado' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "fecha": "2026-10-13 14:12:02.055673+00:00",
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
X-Traza-Id: 3c3850a0-8e21-4288-a04d-a5fcab17a1eb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 29 ms · traza `3c3850a0-8e21-4288-a04d-a5fcab17a1eb`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "3c3850a0-8e21-4288-a04d-a5fcab17a1eb"
  }
}
```

## Servicio catalogos · puerto 5103

### CAT-01 · Productos con búsqueda (caché vacía) · PASA

**Objetivo.** Consultar productos; la respuesta se guarda en Redis.

**Petición.** `GET http://catalogos:5103/api/v1/productos?q=arroz&pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: fd21af2f-aff6-47cf-ba42-c3d05cbacc3f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 228 ms · traza `fd21af2f-aff6-47cf-ba42-c3d05cbacc3f`

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

### CAT-02 · Misma consulta (desde Redis) · PASA

**Objetivo.** La segunda consulta no toca PostgreSQL.

**Petición.** `GET http://catalogos:5103/api/v1/productos?q=arroz&pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 9b5ada92-0da7-424e-97a2-f52c41684341
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 6 ms · traza `9b5ada92-0da7-424e-97a2-f52c41684341`

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

### CAT-03 · Productos (XML) · PASA

**Objetivo.** Lista en XML válida contra catalogos.xsd.

**Petición.** `GET http://catalogos:5103/api/v1/productos?pagina=1&por_pagina=2`

```http
Accept: application/xml
X-Traza-Id: 971269c8-ca1d-4b4b-8890-d6eca1af2165
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 71 ms · traza `971269c8-ca1d-4b4b-8890-d6eca1af2165`

```xml
<?xml version='1.0' encoding='utf-8'?>
<productos xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><datos><producto><id>3</id><clave_interna>AB-003</clave_interna><nombre>Aceite vegetal</nombre><categoria><id>1</id><nombre>Abarrote básico</nombre></categoria><unidad>botella</unidad><presentacion>900 ml</presentacion><precio>42.00</precio><imagen_url xsi:nil="true" /><estatus>activo</estatus></producto><producto><id>2</id><clave_interna>AB-002</clave_interna><nombre>Arroz superextra</nombre><categoria><id>1</id><nombre>Abarrote básico</nombre></categoria><unidad>kg</unidad><presentacion>1 kg</presentacion><precio>29.90</precio><imagen_url xsi:nil="true" /><estatus>activo</estatus></producto></datos><paginacion><pagina>1</pagina><por_pagina>2</por_pagina><total>51</total><paginas>26</paginas></paginacion></productos>
```

### CAT-04 · Un producto · PASA

**Objetivo.** Detalle por id.

**Petición.** `GET http://catalogos:5103/api/v1/productos/3`

```http
Accept: application/json
X-Traza-Id: 918f7f5e-54a2-4430-9b5f-87b4869b2ddd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 47 ms · traza `918f7f5e-54a2-4430-9b5f-87b4869b2ddd`

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

### CAT-05 · Producto inexistente · PASA

**Objetivo.** Registro que no existe.

**Petición.** `GET http://catalogos:5103/api/v1/productos/999999`

```http
Accept: application/json
X-Traza-Id: e61cd803-9dd5-422b-ba05-c9037150bd8e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 50 ms · traza `e61cd803-9dd5-422b-ba05-c9037150bd8e`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "e61cd803-9dd5-422b-ba05-c9037150bd8e"
  }
}
```

### CAT-06 · Zonas (XML) · PASA

**Objetivo.** Colonias atendidas con centroide.

**Petición.** `GET http://catalogos:5103/api/v1/zonas`

```http
Accept: application/xml
X-Traza-Id: de02e3cc-e369-4765-9729-b2d5859cba84
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 74 ms · traza `de02e3cc-e369-4765-9729-b2d5859cba84`

```xml
<?xml version='1.0' encoding='utf-8'?>
<zonas xmlns="urn:microhubs:v1" version="1"><datos><zona><id>1</id><clave>ZN-SB01</clave><nombre>San Bernabé Centro</nombre><colonia>San Bernabé</colonia><codigo_postal>64100</codigo_postal><latitud>25.7455</latitud><longitud>-100.3585</longitud></zona><zona><id>2</id><clave>ZN-SB02</clave><nombre>Valles de San Bernabé</nombre><colonia>Valles de San Bernabé</colonia><codigo_postal>64103</codigo_postal><latitud>25.753</latitud><longitud>-100.369</longitud></zona><zona><id>3</id><clave>ZN-SB03</clave><nombre>Paseo de San Bernabé</nombre><colonia>Paseo de San Bernabé</colonia><codigo_postal>64103</codigo_postal><latitud>25.758</latitud><longitud>-100.3745</longitud></zona><zona><id>4</id><clave>ZN-SB04</clave><nombre>San Bernabé X (F-113)</nombre><colonia>San Bernabé X (F-113)</colonia><codigo_postal>64105</codigo_postal><latitud>25.7495</latitud><longitud>-100.38</longitud></zona></datos><paginacion><pagina>1</pagina><por_pagina>20</por_pagina><total>4</total><paginas>1</paginas></paginacion></zonas>
```

### CAT-07 · Microhubs · PASA

**Objetivo.** Microhubs con coordenadas y radio.

**Petición.** `GET http://catalogos:5103/api/v1/microhubs?estatus=activo`

```http
Accept: application/json
X-Traza-Id: a6e6cdb5-a7d6-4714-b98c-27753c3a00fb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 79 ms · traza `a6e6cdb5-a7d6-4714-b98c-27753c3a00fb`

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

### CAT-08 · Paginación fuera de rango · PASA

**Objetivo.** por_pagina máximo 100.

**Petición.** `GET http://catalogos:5103/api/v1/productos?por_pagina=500`

```http
Accept: application/json
X-Traza-Id: ea604574-3c9f-407a-88cb-9baf220006ba
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 6 ms · traza `ea604574-3c9f-407a-88cb-9baf220006ba`

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
    "traza_id": "ea604574-3c9f-407a-88cb-9baf220006ba"
  }
}
```

### CAT-09 · Sin token · PASA

**Objetivo.** Todo endpoint protegido exige Authorization: Bearer.

**Petición.** `GET http://catalogos:5103/api/v1/productos`

```http
Accept: application/json
X-Traza-Id: 3c095b18-2c8b-4c12-b21f-f9d63456718a
```

**Respuesta.** HTTP 401 (esperado 401) · 5 ms · traza `3c095b18-2c8b-4c12-b21f-f9d63456718a`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "Falta el encabezado Authorization: Bearer <token>.",
    "traza_id": "3c095b18-2c8b-4c12-b21f-f9d63456718a"
  }
}
```

## Servicio pedidos · puerto 5104

### PED-01 · Pedidos entregados (JSON) · PASA

**Objetivo.** Lista filtrada por estado y fechas.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos?estado=entregado&pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: b93167b9-213e-4fce-a4f6-937394ee054e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 242 ms · traza `b93167b9-213e-4fce-a4f6-937394ee054e`

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
      "creado_en": "2026-10-12T13:20:40-06:00"
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
      "creado_en": "2026-10-12T12:12:25-06:00"
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
      "creado_en": "2026-10-12T08:44:46-06:00"
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
      "creado_en": "2026-10-12T08:18:54-06:00"
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
      "creado_en": "2026-10-10T19:31:46-06:00"
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
X-Traza-Id: 699aecb5-ae4a-4790-90ab-b3eca0830a9e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 69 ms · traza `699aecb5-ae4a-4790-90ab-b3eca0830a9e`

```xml
<?xml version='1.0' encoding='utf-8'?>
<pedidos xmlns="urn:microhubs:v1" version="1"><datos><pedido><id>105</id><folio>PED-20261013-000105</folio><estado>entregado</estado><zona><id>2</id><nombre>Valles de San Bernabé</nombre></zona><microhub_id>2</microhub_id><total>148.00</total><creado_en>2026-10-12T13:20:40-06:00</creado_en></pedido><pedido><id>18</id><folio>PED-20261013-000018</folio><estado>entregado</estado><zona><id>1</id><nombre>San Bernabé Centro</nombre></zona><microhub_id>1</microhub_id><total>180.50</total><creado_en>2026-10-12T12:12:25-06:00</creado_en></pedido></datos><paginacion><pagina>1</pagina><por_pagina>2</por_pagina><total>113</total><paginas>57</paginas></paginacion></pedidos>
```

### PED-03 · Detalle con líneas · PASA

**Objetivo.** Cliente, domicilio y líneas del pedido.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/105`

```http
Accept: application/json
X-Traza-Id: c8847297-a45e-493c-8d3d-8ea4dc9756f7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 88 ms · traza `c8847297-a45e-493c-8d3d-8ea4dc9756f7`

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
  "creado_en": "2026-10-12T13:20:40-06:00",
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
X-Traza-Id: b85c72c7-7951-4386-83fb-84ef05f1bd97
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 92 ms · traza `b85c72c7-7951-4386-83fb-84ef05f1bd97`

```json
{
  "pedido_id": 105,
  "eventos": [
    {
      "estado_anterior": null,
      "estado_nuevo": "creado",
      "usuario": null,
      "motivo": null,
      "fecha": "2026-10-12T13:20:40-06:00"
    },
    {
      "estado_anterior": "creado",
      "estado_nuevo": "asignado",
      "usuario": null,
      "motivo": null,
      "fecha": "2026-10-12T13:20:40-06:00"
    },
    {
      "estado_anterior": "asignado",
      "estado_nuevo": "en_preparacion",
      "usuario": null,
      "motivo": null,
      "fecha": "2026-10-12T13:20:40-06:00"
    },
    {
      "estado_anterior": "en_preparacion",
      "estado_nuevo": "en_ruta",
      "usuario": null,
      "motivo": null,
      "fecha": "2026-10-12T13:20:40-06:00"
    },
    {
      "estado_anterior": "en_ruta",
      "estado_nuevo": "entregado",
      "usuario": null,
      "motivo": null,
      "fecha": "2026-10-12T13:20:40-06:00"
    }
  ]
}
```

**Evidencia en PostgreSQL.** `SELECT fecha, estado_anterior, estado_nuevo, usuario_id FROM historial_estatus WHERE pedido_id = %s ORDER BY fecha, id`

```json
[
  {
    "fecha": "2026-10-12 19:20:40.369734+00:00",
    "estado_anterior": null,
    "estado_nuevo": "creado",
    "usuario_id": null
  },
  {
    "fecha": "2026-10-12 19:20:40.369734+00:00",
    "estado_anterior": "creado",
    "estado_nuevo": "asignado",
    "usuario_id": null
  },
  {
    "fecha": "2026-10-12 19:20:40.369734+00:00",
    "estado_anterior": "asignado",
    "estado_nuevo": "en_preparacion",
    "usuario_id": null
  },
  {
    "fecha": "2026-10-12 19:20:40.369734+00:00",
    "estado_anterior": "en_preparacion",
    "estado_nuevo": "en_ruta",
    "usuario_id": null
  },
  {
    "fecha": "2026-10-12 19:20:40.369734+00:00",
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
X-Traza-Id: 50bef59e-3e07-4078-bc58-dde99054ec51
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 87 ms · traza `50bef59e-3e07-4078-bc58-dde99054ec51`

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
    "traza_id": "50bef59e-3e07-4078-bc58-dde99054ec51"
  }
}
```

### PED-06 · Pedido fuera del ámbito · PASA

**Objetivo.** El operador del MH-01 no ve pedidos de otro microhub (RN22).

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/1`

```http
Accept: application/json
X-Traza-Id: e9bcee3a-6bf3-4a83-a437-55750039499f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 51 ms · traza `e9bcee3a-6bf3-4a83-a437-55750039499f`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el pedido o no está en tu ámbito.",
    "traza_id": "e9bcee3a-6bf3-4a83-a437-55750039499f"
  }
}
```

**Explicación.** El ámbito lo decide PostgreSQL con fn_pedidos_visibles; el servicio no lo puede saltar.

### PED-07 · Cerrar desde pedidos · PASA

**Objetivo.** Los cierres de entrega solo se registran en el servicio de entregas.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/105/estado`

```http
Accept: application/json
X-Traza-Id: 12ed2826-fb49-45e6-8ae8-9ed4d9fb5976
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "estado": "entregado"
}
```

**Respuesta.** HTTP 409 (esperado 409) · 8 ms · traza `12ed2826-fb49-45e6-8ae8-9ed4d9fb5976`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "El cierre de una entrega se registra con POST /api/v1/entregas/{id}/resultado.",
    "traza_id": "12ed2826-fb49-45e6-8ae8-9ed4d9fb5976"
  }
}
```

### PED-08 · Transición ilegal (regla del motor) · PASA

**Objetivo.** Un pedido entregado no puede regresar a preparación.

**Petición.** `PATCH http://pedidos:5104/api/v1/pedidos/2/estado`

```http
Accept: application/json
X-Traza-Id: 1f222a5f-7824-4473-8922-e4289a6e10e4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0Iiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "estado": "en_preparacion"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 68 ms · traza `1f222a5f-7824-4473-8922-e4289a6e10e4`

```json
{
  "error": {
    "codigo": "REGLA_NEGOCIO",
    "mensaje": "RN20: transición ilegal entregado -> en_preparacion para el rol operador. El pedido PED-20261013-000002 conserva su estado.",
    "traza_id": "1f222a5f-7824-4473-8922-e4289a6e10e4"
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
X-Traza-Id: d027d198-92b5-4edc-a3fb-d7cf4f2458e2
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

**Respuesta.** HTTP 201 (esperado 201) · 38 ms · traza `d027d198-92b5-4edc-a3fb-d7cf4f2458e2`

```json
{
  "id": "6ace3c3457a2d24c02b0d703",
  "nombre": "evidencia-entrega-129.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "129"
  },
  "subido_por": 7,
  "creado_en": "2026-10-13T08:12:04-06:00"
}
```

**Explicación.** Se valida que el contenido sea JPEG real, se calcula su SHA-256 y que la entrega sea del repartidor.

**Evidencia en MongoDB.** `db.documentos.findOne({_id: ObjectId('6ace3c3457a2d24c02b0d703')}, {contenido: 0})`

```json
{
  "_id": "6ace3c3457a2d24c02b0d703",
  "nombre": "evidencia-entrega-129.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "129"
  },
  "subido_por": 7,
  "creado_en": "2026-10-13 14:12:04.120000+00:00"
}
```

### DOC-02 · Subir evidencia de la segunda entrega · PASA

**Objetivo.** Evidencia para el cierre parcial.

**Petición.** `POST http://documentos:5107/api/v1/documentos`

```http
Accept: application/json
X-Traza-Id: 5eee03e5-8a01-436e-812c-a292bc91e0c2
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

**Respuesta.** HTTP 201 (esperado 201) · 54 ms · traza `5eee03e5-8a01-436e-812c-a292bc91e0c2`

```json
{
  "id": "6ace3c3457a2d24c02b0d706",
  "nombre": "evidencia-entrega-130.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "130"
  },
  "subido_por": 7,
  "creado_en": "2026-10-13T08:12:04-06:00"
}
```

### DOC-03 · Tipo de archivo falso · PASA

**Objetivo.** Un PDF declarado como JPEG se rechaza por su firma.

**Petición.** `POST http://documentos:5107/api/v1/documentos`

```http
Accept: application/json
X-Traza-Id: 44ec8ab3-8db3-46ba-b9bc-154ed1a834ee
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

**Respuesta.** HTTP 422 (esperado 422) · 8 ms · traza `44ec8ab3-8db3-46ba-b9bc-154ed1a834ee`

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
    "traza_id": "44ec8ab3-8db3-46ba-b9bc-154ed1a834ee"
  }
}
```

### DOC-04 · Evidencia en entrega ajena · PASA

**Objetivo.** Un repartidor no adjunta a entregas de otro.

**Petición.** `POST http://documentos:5107/api/v1/documentos`

```http
Accept: application/json
X-Traza-Id: ba73d365-8fc4-40d6-af2c-003ab0f4d533
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

**Respuesta.** HTTP 403 (esperado 403) · 30 ms · traza `ba73d365-8fc4-40d6-af2c-003ab0f4d533`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Solo puedes adjuntar evidencia a tus entregas.",
    "traza_id": "ba73d365-8fc4-40d6-af2c-003ab0f4d533"
  }
}
```

### DOC-05 · Documento temporal · PASA

**Objetivo.** Documento que después se elimina.

**Petición.** `POST http://documentos:5107/api/v1/documentos`

```http
Accept: application/json
X-Traza-Id: 1696a0ba-fa52-4b4e-a3c1-8a091f662b96
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

**Respuesta.** HTTP 201 (esperado 201) · 6 ms · traza `1696a0ba-fa52-4b4e-a3c1-8a091f662b96`

```json
{
  "id": "6ace3c3457a2d24c02b0d70d",
  "nombre": "borrador.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "usuario",
    "id": "7"
  },
  "subido_por": 7,
  "creado_en": "2026-10-13T08:12:04-06:00"
}
```

### DOC-06 · Mis documentos · PASA

**Objetivo.** Filtro por referencia.

**Petición.** `GET http://documentos:5107/api/v1/documentos?referencia_tipo=entrega&referencia_id=129`

```http
Accept: application/json
X-Traza-Id: 6a64105c-1369-4700-8b66-7ec62653687c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 23 ms · traza `6a64105c-1369-4700-8b66-7ec62653687c`

```json
{
  "datos": [
    {
      "id": "6ace3c3457a2d24c02b0d703",
      "nombre": "evidencia-entrega-129.jpg",
      "tipo_mime": "image/jpeg",
      "tamano_bytes": 276,
      "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
      "referencia": {
        "tipo": "entrega",
        "id": "129"
      },
      "subido_por": 7,
      "creado_en": "2026-10-13T08:12:04-06:00"
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

**Petición.** `GET http://documentos:5107/api/v1/documentos/6ace3c3457a2d24c02b0d703`

```http
Accept: application/xml
X-Traza-Id: 34a698a5-71f1-4daf-ba5d-d24bef14cb65
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 7 ms · traza `34a698a5-71f1-4daf-ba5d-d24bef14cb65`

```xml
<?xml version='1.0' encoding='utf-8'?>
<documento xmlns="urn:microhubs:v1" version="1"><id>6ace3c3457a2d24c02b0d703</id><nombre>evidencia-entrega-129.jpg</nombre><tipo_mime>image/jpeg</tipo_mime><tamano_bytes>276</tamano_bytes><sha256>7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc</sha256><referencia><tipo>entrega</tipo><id>129</id></referencia><subido_por>7</subido_por><creado_en>2026-10-13T08:12:04-06:00</creado_en></documento>
```

### DOC-08 · Contenido en Base64 · PASA

**Objetivo.** Recuperar el archivo.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6ace3c3457a2d24c02b0d703/contenido`

```http
Accept: application/json
X-Traza-Id: f19a00be-3abf-4295-9f52-2ab6de11fe0c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 7 ms · traza `f19a00be-3abf-4295-9f52-2ab6de11fe0c`

```json
{
  "id": "6ace3c3457a2d24c02b0d703",
  "nombre": "evidencia-entrega-129.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "129"
  },
  "subido_por": 7,
  "creado_en": "2026-10-13T08:12:04-06:00",
  "contenido_base64": "/9j/4AAQSkZJRgABAQAAAQABAAAAAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcY…(368 caracteres)"
}
```

### DOC-09 · Eliminar documento (DELETE) · PASA

**Objetivo.** Borrar un documento propio.

**Petición.** `DELETE http://documentos:5107/api/v1/documentos/6ace3c3457a2d24c02b0d70d`

```http
Accept: application/json
X-Traza-Id: 1c5f6445-8dba-491a-8048-5d7ae3835842
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 31 ms · traza `1c5f6445-8dba-491a-8048-5d7ae3835842`

```json
(sin cuerpo)
```

**Evidencia en MongoDB.** `db.documentos.countDocuments({_id: ObjectId('6ace3c3457a2d24c02b0d70d')})`

```json
0
```

### DOC-10 · Id inexistente · PASA

**Objetivo.** Registro que no existe.

**Petición.** `GET http://documentos:5107/api/v1/documentos/ffffffffffffffffffffffff`

```http
Accept: application/json
X-Traza-Id: 939bc153-1886-42c6-b05c-9d37d88dadb6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 6 ms · traza `939bc153-1886-42c6-b05c-9d37d88dadb6`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "939bc153-1886-42c6-b05c-9d37d88dadb6"
  }
}
```

## Servicio entregas · puerto 5105

### ENT-01 · Mis entregas · PASA

**Objetivo.** Paradas abiertas del repartidor en el turno de hoy (RN25).

**Petición.** `GET http://entregas:5105/api/v1/entregas/mias?pagina=1&por_pagina=20`

```http
Accept: application/json
X-Traza-Id: 79391155-f76b-42aa-876c-7a60fef6b97e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 63 ms · traza `79391155-f76b-42aa-876c-7a60fef6b97e`

```json
{
  "datos": [
    {
      "id": 129,
      "pedido_id": 153,
      "folio": "PED-20261013-000153",
      "estado_pedido": "en_ruta",
      "orden_parada": 1,
      "direccion": "Paseo del Valle 1762, Paseo de San Bernabé",
      "zona": "Paseo de San Bernabé",
      "distancia_km": 1.35,
      "minutos_estimados": 10.0,
      "total": 162.0
    },
    {
      "id": 130,
      "pedido_id": 154,
      "folio": "PED-20261013-000154",
      "estado_pedido": "en_ruta",
      "orden_parada": 2,
      "direccion": "Cerro Prieto 4059, Valles de San Bernabé",
      "zona": "Valles de San Bernabé",
      "distancia_km": 1.14,
      "minutos_estimados": 16.0,
      "total": 141.0
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
X-Traza-Id: 119881ff-c0da-4b81-8a42-5e7f6e136d8c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 89 ms · traza `119881ff-c0da-4b81-8a42-5e7f6e136d8c`

```json
{
  "id": 129,
  "pedido_id": 153,
  "folio": "PED-20261013-000153",
  "estado_pedido": "en_ruta",
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
  "orden_parada": 1,
  "distancia_km": 1.35,
  "minutos_estimados": 10.0,
  "total": 162.0,
  "lineas": [
    {
      "pedido_detalle_id": 683,
      "nombre": "Toallas femeninas",
      "cantidad": 2
    },
    {
      "pedido_detalle_id": 684,
      "nombre": "Crema ácida",
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
X-Traza-Id: 3e5f77fa-050f-4c40-86ef-912f65c0e77b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4Iiwi…(296 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 42 ms · traza `3e5f77fa-050f-4c40-86ef-912f65c0e77b`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe la entrega o no está asignada a ti.",
    "traza_id": "3e5f77fa-050f-4c40-86ef-912f65c0e77b"
  }
}
```

### ENT-04 · Enviar puntos GPS · PASA

**Objetivo.** Guardar el recorrido del repartidor en MongoDB.

**Petición.** `POST http://entregas:5105/api/v1/entregas/129/ubicaciones`

```http
Accept: application/json
X-Traza-Id: a4b51f9c-acfa-407d-835b-43c04eff40cf
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
      "capturado_en": "2026-10-13T14:06:05+00:00"
    },
    {
      "latitud": 25.7486,
      "longitud": -100.3606,
      "precision_m": 8.0,
      "capturado_en": "2026-10-13T14:08:05+00:00"
    },
    {
      "latitud": 25.7491,
      "longitud": -100.3611,
      "precision_m": 8.5,
      "capturado_en": "2026-10-13T14:10:05+00:00"
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 52 ms · traza `a4b51f9c-acfa-407d-835b-43c04eff40cf`

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
    "capturado_en": "2026-10-13 14:06:05+00:00",
    "recibido_en": "2026-10-13 14:12:05.210000+00:00"
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
    "capturado_en": "2026-10-13 14:08:05+00:00",
    "recibido_en": "2026-10-13 14:12:05.210000+00:00"
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
    "capturado_en": "2026-10-13 14:10:05+00:00",
    "recibido_en": "2026-10-13 14:12:05.210000+00:00"
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

### ENT-05 · Resumen del recorrido · PASA

**Objetivo.** Agregación en MongoDB sobre los puntos GPS.

**Petición.** `GET http://entregas:5105/api/v1/entregas/129/recorrido`

```http
Accept: application/json
X-Traza-Id: 9c602309-9f58-44f8-819e-46242d6abfaa
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 41 ms · traza `9c602309-9f58-44f8-819e-46242d6abfaa`

```json
{
  "entrega_id": 129,
  "puntos": 3,
  "distancia_km": 0.16,
  "inicio": "2026-10-13T08:06:05-06:00",
  "fin": "2026-10-13T08:10:05-06:00",
  "precision_promedio_m": 8.5,
  "ultimo_punto": {
    "latitud": 25.7491,
    "longitud": -100.3611,
    "precision_m": 8.5
  }
}
```

**Explicación.** Pipeline: $match por entrega_id → $sort por capturado_en → $group (conteo, inicio, fin, precisión promedio y ruta). La distancia se calcula con Haversine sobre la ruta.

### ENT-06 · Monto incorrecto (regla de negocio) · PASA

**Objetivo.** Una entrega completa cobra el total (RN27).

**Petición.** `POST http://entregas:5105/api/v1/entregas/129/resultado`

```http
Accept: application/json
X-Traza-Id: dfb4f3c5-2c15-4e39-b0a3-d553287aae81
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
    "6ace3c3457a2d24c02b0d703"
  ],
  "capturado_en": "2026-10-13T14:12:05+00:00",
  "id_cliente_local": "d8ce0660-cf47-488b-95c4-3660367d51f6"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 75 ms · traza `dfb4f3c5-2c15-4e39-b0a3-d553287aae81`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "monto_cobrado",
        "mensaje": "Una entrega completa cobra el total del pedido (162.00)."
      }
    ],
    "traza_id": "dfb4f3c5-2c15-4e39-b0a3-d553287aae81"
  }
}
```

### ENT-07 · Cerrar entrega como entregado · PASA

**Objetivo.** Registrar el resultado con evidencia y ubicación.

**Petición.** `POST http://entregas:5105/api/v1/entregas/129/resultado`

```http
Accept: application/json
X-Traza-Id: 3c4a1961-e0a2-4014-9848-c15f002a2ddf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 162.0,
  "cambio_entregado": 0.0,
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611,
    "precision_m": 8.5
  },
  "evidencia_ids": [
    "6ace3c3457a2d24c02b0d703"
  ],
  "capturado_en": "2026-10-13T14:12:05+00:00",
  "id_cliente_local": "d8ce0660-cf47-488b-95c4-3660367d51f6"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 128 ms · traza `3c4a1961-e0a2-4014-9848-c15f002a2ddf`

```json
{
  "entrega_id": 129,
  "pedido_id": 153,
  "estado_pedido": "entregado",
  "cerrado_en": "2026-10-13T08:12:05-06:00",
  "duplicado": false
}
```

**Explicación.** Una sola transacción: cierra la entrega, cambia el pedido (el trigger valida la transición y escribe historial y bitácora) y el trigger de cierre avisa al cliente. La operación se registra en MongoDB.

**Evidencia en PostgreSQL.** `SELECT id, cierre_en, resultado, monto_cobrado, id_cliente_local, evidencia_ids, cierre_latitud, cierre_longitud FROM entrega WHERE id = %s`

```json
[
  {
    "id": 129,
    "cierre_en": "2026-10-13 14:12:05.399707+00:00",
    "resultado": "entregado",
    "monto_cobrado": "162.00",
    "id_cliente_local": "d8ce0660-cf47-488b-95c4-3660367d51f6",
    "evidencia_ids": [
      "6ace3c3457a2d24c02b0d703"
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
    "fecha": "2026-10-13 14:12:05.399707+00:00"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT destinatario_id, tipo, titulo, mensaje, referencia_tipo, referencia_id FROM web_notificacion WHERE referencia_tipo = 'pedido' AND referencia_id = %s ORDER BY id DESC LIMIT 1`

```json
[]
```

**Evidencia en MongoDB.** `db.sincronizaciones_moviles.findOne({operacion_uuid: 'd8ce0660-cf47-488b-95c4-3660367d51f6'})`

```json
{
  "operacion_uuid": "d8ce0660-cf47-488b-95c4-3660367d51f6",
  "capturado_en": "2026-10-13 14:12:05+00:00",
  "carga": {
    "entrega_id": 129,
    "resultado": "entregado",
    "monto_cobrado": 162.0,
    "evidencia_ids": [
      "6ace3c3457a2d24c02b0d703"
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
  "sincronizado_en": "2026-10-13 14:12:05.456000+00:00",
  "tipo_operacion": "cierre_entrega",
  "usuario_id": 7
}
```

### ENT-08 · Reintento con el mismo UUID · PASA

**Objetivo.** Idempotencia: el cierre no se aplica dos veces.

**Petición.** `POST http://entregas:5105/api/v1/entregas/129/resultado`

```http
Accept: application/json
X-Traza-Id: 9951dccc-e4c2-4678-bc64-587719a19d07
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 162.0,
  "cambio_entregado": 0.0,
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611,
    "precision_m": 8.5
  },
  "evidencia_ids": [
    "6ace3c3457a2d24c02b0d703"
  ],
  "capturado_en": "2026-10-13T14:12:05+00:00",
  "id_cliente_local": "d8ce0660-cf47-488b-95c4-3660367d51f6"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 78 ms · traza `9951dccc-e4c2-4678-bc64-587719a19d07`

```json
{
  "entrega_id": 129,
  "pedido_id": 153,
  "estado_pedido": "entregado",
  "cerrado_en": "2026-10-13T08:12:05-06:00",
  "duplicado": true
}
```

**Explicación.** La respuesta es la misma con duplicado=true. MongoDB actualiza el documento de la operación (intentos = 2).

**Evidencia en MongoDB.** `db.sincronizaciones_moviles.findOne({operacion_uuid: 'd8ce0660-cf47-488b-95c4-3660367d51f6'}, {estado: 1, intentos: 1})`

```json
{
  "estado": "aplicada",
  "intentos": 2,
  "sincronizado_en": "2026-10-13 14:12:05.602000+00:00"
}
```

### ENT-09 · Otro cierre sobre la misma entrega · PASA

**Objetivo.** Conflicto: ya estaba cerrada con otra operación.

**Petición.** `POST http://entregas:5105/api/v1/entregas/129/resultado`

```http
Accept: application/json
X-Traza-Id: 1e3b66f9-8bb7-4668-a170-e48740bf9cd9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 162.0,
  "cambio_entregado": 0.0,
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611,
    "precision_m": 8.5
  },
  "evidencia_ids": [
    "6ace3c3457a2d24c02b0d703"
  ],
  "capturado_en": "2026-10-13T14:12:05+00:00",
  "id_cliente_local": "5c6a3b47-6643-4c55-af51-36ec9610ed1c"
}
```

**Respuesta.** HTTP 409 (esperado 409) · 67 ms · traza `1e3b66f9-8bb7-4668-a170-e48740bf9cd9`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "La entrega ya se cerró con otra operación.",
    "traza_id": "1e3b66f9-8bb7-4668-a170-e48740bf9cd9"
  }
}
```

### ENT-10 · Detalle tras el cierre · PASA

**Objetivo.** El repartidor deja de ver el domicilio (RN26).

**Petición.** `GET http://entregas:5105/api/v1/entregas/129`

```http
Accept: application/json
X-Traza-Id: 85a85d66-14ab-4f09-8420-c6321d99a789
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 37 ms · traza `85a85d66-14ab-4f09-8420-c6321d99a789`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "La entrega ya se cerró; su información ya no está disponible.",
    "traza_id": "85a85d66-14ab-4f09-8420-c6321d99a789"
  }
}
```

### ENT-11 · Parcial sin motivo · PASA

**Objetivo.** Cada línea devuelta necesita motivo (RN28).

**Petición.** `POST http://entregas:5105/api/v1/entregas/130/resultado`

```http
Accept: application/json
X-Traza-Id: b45a2abc-0348-4481-8432-062ce48b9745
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
      "cantidad_entregada": 1,
      "cantidad_devuelta": 0
    },
    {
      "pedido_detalle_id": 686,
      "cantidad_entregada": 0,
      "cantidad_devuelta": 1
    }
  ],
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611
  },
  "evidencia_ids": [
    "6ace3c3457a2d24c02b0d706"
  ],
  "capturado_en": "2026-10-13T14:12:05+00:00",
  "id_cliente_local": "6108e6c8-4fae-4b8d-903a-be4fa13d629f"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 70 ms · traza `b45a2abc-0348-4481-8432-062ce48b9745`

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
    "traza_id": "b45a2abc-0348-4481-8432-062ce48b9745"
  }
}
```

### ENT-12 · Cerrar como entrega parcial · PASA

**Objetivo.** Devolver al inventario lo que no se entregó.

**Petición.** `POST http://entregas:5105/api/v1/entregas/130/resultado`

```http
Accept: application/json
X-Traza-Id: 991fe92b-b770-40bc-8c7e-b694c9bca2f7
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
      "cantidad_entregada": 1,
      "cantidad_devuelta": 0
    },
    {
      "pedido_detalle_id": 686,
      "cantidad_entregada": 0,
      "cantidad_devuelta": 1,
      "motivo": "El cliente la rechazó."
    }
  ],
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611
  },
  "evidencia_ids": [
    "6ace3c3457a2d24c02b0d706"
  ],
  "capturado_en": "2026-10-13T14:12:05+00:00",
  "id_cliente_local": "6108e6c8-4fae-4b8d-903a-be4fa13d629f"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 135 ms · traza `991fe92b-b770-40bc-8c7e-b694c9bca2f7`

```json
{
  "entrega_id": 130,
  "pedido_id": 154,
  "estado_pedido": "entrega_parcial",
  "cerrado_en": "2026-10-13T08:12:05-06:00",
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
    "cantidad_entregada": 1,
    "cantidad_devuelta": 0,
    "motivo": null
  },
  {
    "entrega_id": 130,
    "pedido_detalle_id": 686,
    "cantidad_entregada": 0,
    "cantidad_devuelta": 1,
    "motivo": "El cliente la rechazó."
  }
]
```

**Evidencia en PostgreSQL.** `SELECT tipo, producto_id, cantidad, existencia_resultante, motivo FROM movimiento_inventario WHERE referencia_id = %s AND tipo = 'devolucion_parcial'`

```json
[
  {
    "tipo": "devolucion_parcial",
    "producto_id": 47,
    "cantidad": 1,
    "existencia_resultante": 62,
    "motivo": "Entrega parcial: regresan las unidades devueltas (RN28)."
  }
]
```

### ENT-13 · Entregas de un pedido (administrador) · PASA

**Objetivo.** Consulta por pedido para el portal web.

**Petición.** `GET http://entregas:5105/api/v1/entregas?pedido_id=153`

```http
Accept: application/json
X-Traza-Id: dfb29b72-537e-437a-8348-b156c229da9e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 57 ms · traza `dfb29b72-537e-437a-8348-b156c229da9e`

```json
{
  "datos": [
    {
      "id": 129,
      "pedido_id": 153,
      "folio": "PED-20261013-000153",
      "estado_pedido": "entregado",
      "orden_parada": 1,
      "direccion": "Paseo del Valle 1762, Paseo de San Bernabé",
      "zona": "Paseo de San Bernabé",
      "distancia_km": 1.35,
      "minutos_estimados": 10.0,
      "total": 162.0
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
X-Traza-Id: 8b9746b0-413b-4f7c-ad01-f2a628ff1432
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 68 ms · traza `8b9746b0-413b-4f7c-ad01-f2a628ff1432`

```xml
<?xml version='1.0' encoding='utf-8'?>
<candidatos xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><datos><candidato><id>1</id><clave>CAND-01</clave><nombre>San Bernabé Norte</nombre><latitud>25.752</latitud><longitud>-100.361</longitud><renta_estimada>18000.00</renta_estimada><nomina_estimada>42000.00</nomina_estimada><servicios_estimados>7000.00</servicios_estimados><otros_costos>5000.00</otros_costos><costo_fijo>72000.00</costo_fijo><superficie_m2>130</superficie_m2><capacidad_fisica>150</capacidad_fisica><accesibilidad_vial>9</accesibilidad_vial><zona_id>1</zona_id><poblacion_cubierta>8420</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato><candidato><id>2</id><clave>CAND-02</clave><nombre>Valles Poniente</nombre><latitud>25.7555</latitud><longitud>-100.376</longitud><renta_estimada>15500.00</renta_estimada><nomina_estimada>42000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><costo_fijo>68500.00</costo_fijo><superficie_m2>105</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>2</zona_id><poblacion_cubierta>6180</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato><candidato><id>3</id><clave>CAND-05</clave><nombre>Alianza Real</nombre><latitud>25.7625</latitud><longitud>-100.353</longitud><renta_estimada>21000.00</renta_estimada><nomina_estimada>46000.00</nomina_estimada><servicios_estimados>8000.00</servicios_estimados><otros_costos>6000.00</otros_costos><costo_fijo>81000.00</costo_fijo><superficie_m2>150</superficie_m2><capacidad_fisica>180</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>3900</poblacion_cubierta><radio_km>1.6</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>5</total><paginas>2</paginas></paginacion></candidatos>
```

### PLA-02 · Registrar candidato (XML) · PASA

**Objetivo.** Alta con costo fijo calculado por PostgreSQL.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos`

```http
Accept: application/xml
X-Traza-Id: bbf407e6-384d-4290-b758-adc5a68ec56f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><candidato_nuevo xmlns="urn:microhubs:v1"><clave>********</clave><nombre>Alianza Norte</nombre><latitud>25.7601</latitud><longitud>-100.3555</longitud><renta_estimada>16000.00</renta_estimada><nomina_estimada>40000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><superficie_m2>110</superficie_m2><capacidad_fisica>130</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km></candidato_nuevo>
```

**Respuesta.** HTTP 201 (esperado 201) · 79 ms · traza `bbf407e6-384d-4290-b758-adc5a68ec56f`

```xml
<?xml version='1.0' encoding='utf-8'?>
<candidato xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>16</id><clave>EV-D44B9B</clave><nombre>Alianza Norte</nombre><latitud>25.7601</latitud><longitud>-100.3555</longitud><renta_estimada>16000.00</renta_estimada><nomina_estimada>40000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><costo_fijo>67000.00</costo_fijo><superficie_m2>110</superficie_m2><capacidad_fisica>130</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato>
```

**Evidencia en PostgreSQL.** `SELECT id, clave, nombre, renta_estimada, costo_fijo, decision FROM ubicacion_candidata WHERE clave = %s`

```json
[
  {
    "id": 16,
    "clave": "EV-D44B9B",
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
X-Traza-Id: c9c1af53-ad8b-401e-bbc1-78ee90a3b3dc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><candidato_nuevo xmlns="urn:microhubs:v1"><clave>********</clave><nombre>Alianza Norte</nombre><latitud>25.7601</latitud><longitud>-100.3555</longitud><renta_estimada>16000.00</renta_estimada><nomina_estimada>40000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><superficie_m2>110</superficie_m2><capacidad_fisica>130</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km></candidato_nuevo>
```

**Respuesta.** HTTP 409 (esperado 409) · 66 ms · traza `c9c1af53-ad8b-401e-bbc1-78ee90a3b3dc`

```xml
<?xml version='1.0' encoding='utf-8'?>
<error xmlns="urn:microhubs:v1" version="1"><codigo>CONFLICTO</codigo><mensaje>Ya existe un registro con esos datos.</mensaje><traza_id>c9c1af53-ad8b-401e-bbc1-78ee90a3b3dc</traza_id></error>
```

### PLA-04 · Modificar candidato (PUT) · PASA

**Objetivo.** Cambiar la renta recalcula el costo fijo.

**Petición.** `PUT http://planeacion:5106/api/v1/candidatos/16`

```http
Accept: application/json
X-Traza-Id: e2cbcb81-7886-4e11-94a1-df87771cee1f
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

**Respuesta.** HTTP 200 (esperado 200) · 118 ms · traza `e2cbcb81-7886-4e11-94a1-df87771cee1f`

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
X-Traza-Id: f98bb9b5-d4f6-4d17-ba60-0a2ba4cdbfb9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<simular xmlns="urn:microhubs:v1"/>
```

**Respuesta.** HTTP 200 (esperado 200) · 375 ms · traza `f98bb9b5-d4f6-4d17-ba60-0a2ba4cdbfb9`

```xml
<?xml version='1.0' encoding='utf-8'?>
<resultados xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><atendidos>0</atendidos><rechazados>0</rechazados><utilizacion>0</utilizacion><nivel>estable</nivel><tiempo_estimado_min>18.6</tiempo_estimado_min><operadores_requeridos>0</operadores_requeridos><repartidores_requeridos>0</repartidores_requeridos><ingreso_dia>0.00</ingreso_dia><margen_dia>-2300.00</margen_dia><costo_por_pedido xsi:nil="true" /><equilibrio><margen_pedido>23.89</margen_pedido><mensual>2888.8</mensual><diario>96.3</diario></equilibrio><decision>NO VIABLE CON LOS SUPUESTOS ACTUALES</decision><explicacion><motivo>la demanda atendida (0/día) no alcanza el equilibrio (96/día)</motivo><motivo>reducir costos fijos, aumentar ticket o buscar una ubicación con más demanda</motivo></explicacion></resultados>
```

**Explicación.** Usa planeacion_calc.py (las mismas fórmulas del web) y guarda la ejecución en MongoDB.

**Evidencia en MongoDB.** `db.ejecuciones_analiticas.find().sort({ejecutado_en: -1}).limit(1)`

```json
{
  "escenario_id": "candidato-16",
  "nombre_escenario": "Candidato 16",
  "tipo_analisis": "punto_equilibrio",
  "ejecutado_en": "2026-10-13 14:12:06.743000+00:00",
  "usuario_id": 5,
  "version_modelo": "planeacion_calc 2.1",
  "parametros_entrada": {
    "demanda_diaria": 0.0,
    "operadores": 3.0,
    "repartidores": 3.0,
    "ticket": 149.59,
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
    "ticket = 149.59",
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
    "equilibrio_diario": 96.3,
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
X-Traza-Id: bc4baef6-b33c-4d69-abe9-7197a857a214
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aceptado",
  "motivo": "ok"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 34 ms · traza `bc4baef6-b33c-4d69-abe9-7197a857a214`

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
    "traza_id": "bc4baef6-b33c-4d69-abe9-7197a857a214"
  }
}
```

### PLA-07 · Decisión humana de apertura · PASA

**Objetivo.** Registrar la decisión con motivo.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/16/decision`

```http
Accept: application/json
X-Traza-Id: 8c822e78-2d56-410f-947a-dd1ad985260b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "condicionado",
  "motivo": "Renegociar la renta antes de firmar."
}
```

**Respuesta.** HTTP 200 (esperado 200) · 75 ms · traza `8c822e78-2d56-410f-947a-dd1ad985260b`

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
    "decision_en": "2026-10-13 14:12:06.834490+00:00"
  }
]
```

### PLA-08 · Simulación libre: Escenario A · PASA

**Objetivo.** Punto de equilibrio del caso de la retroalimentación.

**Petición.** `POST http://planeacion:5106/api/v1/simulaciones`

```http
Accept: application/json
X-Traza-Id: c79178ee-296f-4460-a33c-f9237948c03e
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

**Respuesta.** HTTP 200 (esperado 200) · 82 ms · traza `c79178ee-296f-4460-a33c-f9237948c03e`

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
X-Traza-Id: 2c018343-fde5-471c-a266-107e427f7438
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

**Respuesta.** HTTP 201 (esperado 201) · 116 ms · traza `2c018343-fde5-471c-a266-107e427f7438`

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
  "creado_en": "2026-10-13T08:12:07-06:00"
}
```

### PLA-10 · Abrir escenario (XML) · PASA

**Objetivo.** Escenario con supuestos y resultados.

**Petición.** `GET http://planeacion:5106/api/v1/escenarios/1`

```http
Accept: application/xml
X-Traza-Id: 99d8a85b-f034-44b6-ab62-7f9259e8b45a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 25 ms · traza `99d8a85b-f034-44b6-ab62-7f9259e8b45a`

```xml
<?xml version='1.0' encoding='utf-8'?>
<escenario xmlns="urn:microhubs:v1" version="1"><id>1</id><nombre>Escenario A - evidencias</nombre><candidato_id>16</candidato_id><supuestos><demanda_diaria>120</demanda_diaria><operadores>3</operadores><repartidores>4</repartidores><ticket>135.00</ticket><costo_entrega>22.00</costo_entrega><margen_bruto>0.28</margen_bruto><renta>18000.00</renta><nomina>42000.00</nomina><servicios>7000.00</servicios><otros>5000.00</otros><distancia_km>2.4</distancia_km><capacidad_fisica>150</capacidad_fisica></supuestos><resultados><atendidos>120</atendidos><rechazados>0</rechazados><utilizacion>80</utilizacion><nivel>atencion</nivel><tiempo_estimado_min>19.4</tiempo_estimado_min><operadores_requeridos>3</operadores_requeridos><repartidores_requeridos>2</repartidores_requeridos><ingreso_dia>16200.00</ingreso_dia><margen_dia>-504.00</margen_dia><costo_por_pedido>42.00</costo_por_pedido><equilibrio><margen_pedido>15.80</margen_pedido><mensual>4557</mensual><diario>151.9</diario></equilibrio><decision>NO VIABLE CON LOS SUPUESTOS ACTUALES</decision><explicacion><motivo>la demanda atendida (120/día) no alcanza el equilibrio (152/día)</motivo><motivo>el espacio físico del local limita la capacidad</motivo><motivo>reducir costos fijos, aumentar ticket o buscar una ubicación con más demanda</motivo></explicacion></resultados><creado_en>2026-10-13T08:12:07-06:00</creado_en></escenario>
```

### PLA-11 · Resumen de simulaciones · PASA

**Objetivo.** Agregación $group en MongoDB por decisión.

**Petición.** `GET http://planeacion:5106/api/v1/simulaciones/resumen`

```http
Accept: application/json
X-Traza-Id: a16a19c8-5acc-4175-961c-1f56b5edf02f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 10 ms · traza `a16a19c8-5acc-4175-961c-1f56b5edf02f`

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
X-Traza-Id: 76551a75-b4d6-4f45-9b45-6581b7132674
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

**Respuesta.** HTTP 403 (esperado 403) · 28 ms · traza `76551a75-b4d6-4f45-9b45-6581b7132674`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "76551a75-b4d6-4f45-9b45-6581b7132674"
  }
}
```

### PLA-13 · Auditor intenta simular · PASA

**Objetivo.** Sin simulacion.ejecutar.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/16/simular`

```http
Accept: application/json
X-Traza-Id: c70b673c-6133-455b-a751-4db5f35da358
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 403 (esperado 403) · 30 ms · traza `c70b673c-6133-455b-a751-4db5f35da358`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "c70b673c-6133-455b-a751-4db5f35da358"
  }
}
```

### PLA-14 · Eliminar escenario (DELETE) · PASA

**Objetivo.** Borrar un escenario.

**Petición.** `DELETE http://planeacion:5106/api/v1/escenarios/1`

```http
Accept: application/json
X-Traza-Id: c822ac8b-1c41-4ccb-83da-7cdae3d35b25
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 38 ms · traza `c822ac8b-1c41-4ccb-83da-7cdae3d35b25`

```json
(sin cuerpo)
```

### PLA-15 · Dar de baja candidato (DELETE) · PASA

**Objetivo.** Baja lógica: se conserva su historia.

**Petición.** `DELETE http://planeacion:5106/api/v1/candidatos/16`

```http
Accept: application/json
X-Traza-Id: eba69fe2-0b0b-400d-89fa-067b0b2bc8ce
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 57 ms · traza `eba69fe2-0b0b-400d-89fa-067b0b2bc8ce`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT id, clave, estatus, decision FROM ubicacion_candidata WHERE id = %s`

```json
[
  {
    "id": 16,
    "clave": "EV-D44B9B",
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
X-Traza-Id: 4f29fb6f-877f-4b4d-8d29-a68297804f77
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 23 ms · traza `4f29fb6f-877f-4b4d-8d29-a68297804f77`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el candidato.",
    "traza_id": "4f29fb6f-877f-4b4d-8d29-a68297804f77"
  }
}
```

## Servicio notificaciones · puerto 5108

### NOT-01 · Mi bandeja · PASA

**Objetivo.** Avisos del repartidor (misma tabla que el web).

**Petición.** `GET http://notificaciones:5108/api/v1/notificaciones?pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 8200564b-f98f-4951-9e0a-84397fa4c3d1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 202 ms · traza `8200564b-f98f-4951-9e0a-84397fa4c3d1`

```json
{
  "datos": [
    {
      "id": 2,
      "tipo": "entrega",
      "titulo": "Nueva entrega asignada",
      "mensaje": "Se te asignó el pedido PED-20261013-000154 (parada 2).",
      "leida": false,
      "referencia": {
        "tipo": "entrega",
        "id": "130"
      },
      "creada_en": "2026-10-13T08:11:59-06:00"
    },
    {
      "id": 1,
      "tipo": "entrega",
      "titulo": "Nueva entrega asignada",
      "mensaje": "Se te asignó el pedido PED-20261013-000153 (parada 1).",
      "leida": false,
      "referencia": {
        "tipo": "entrega",
        "id": "129"
      },
      "creada_en": "2026-10-13T08:11:59-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 2,
    "paginas": 1
  }
}
```

**Explicación.** Incluye los avisos «Nueva entrega asignada» que genera el trigger al asignar la entrega.

### NOT-02 · Conteo sin leer · PASA

**Objetivo.** Número de avisos pendientes.

**Petición.** `GET http://notificaciones:5108/api/v1/notificaciones/conteo`

```http
Accept: application/json
X-Traza-Id: 0ca61f54-6349-4262-93df-d0acfb3b8959
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 25 ms · traza `0ca61f54-6349-4262-93df-d0acfb3b8959`

```json
{
  "no_leidas": 2
}
```

### NOT-03 · Marcar como leída · PASA

**Objetivo.** Actualizar el aviso.

**Petición.** `POST http://notificaciones:5108/api/v1/notificaciones/2/leer`

```http
Accept: application/json
X-Traza-Id: f849d966-06fd-4de1-8a33-558e11afb073
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 44 ms · traza `f849d966-06fd-4de1-8a33-558e11afb073`

```json
{
  "id": 2,
  "tipo": "entrega",
  "titulo": "Nueva entrega asignada",
  "mensaje": "Se te asignó el pedido PED-20261013-000154 (parada 2).",
  "leida": true,
  "referencia": {
    "tipo": "entrega",
    "id": "130"
  },
  "creada_en": "2026-10-13T08:11:59-06:00"
}
```

**Evidencia en PostgreSQL.** `SELECT id, titulo, leido_en FROM web_notificacion WHERE id = %s`

```json
[
  {
    "id": 2,
    "titulo": "Nueva entrega asignada",
    "leido_en": "2026-10-13 14:12:07.580080+00:00"
  }
]
```

### NOT-04 · Leer un aviso ajeno · PASA

**Objetivo.** Cada quien solo toca su bandeja.

**Petición.** `POST http://notificaciones:5108/api/v1/notificaciones/2/leer`

```http
Accept: application/json
X-Traza-Id: 7196591b-c48b-4b0a-930f-9fb830bb31fd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4Iiwi…(296 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 27 ms · traza `7196591b-c48b-4b0a-930f-9fb830bb31fd`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe ese aviso en tu bandeja.",
    "traza_id": "7196591b-c48b-4b0a-930f-9fb830bb31fd"
  }
}
```

### NOT-05 · Enviar aviso (administrador) · PASA

**Objetivo.** Aviso manual a un usuario.

**Petición.** `POST http://notificaciones:5108/api/v1/notificaciones`

```http
Accept: application/json
X-Traza-Id: 21ba92db-d5af-42c3-93da-597eb805803c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "usuario_id": 7,
  "tipo": "sistema",
  "titulo": "Reunión de turno",
  "mensaje": "Revisión de rutas a las 9:00.",
  "referencia": {
    "tipo": "sistema",
    "id": "turno"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 150 ms · traza `21ba92db-d5af-42c3-93da-597eb805803c`

```json
{
  "id": 5,
  "tipo": "sistema",
  "titulo": "Reunión de turno",
  "mensaje": "Revisión de rutas a las 9:00.",
  "leida": false,
  "referencia": {
    "tipo": "sistema",
    "id": "turno"
  },
  "creada_en": "2026-10-13T08:12:07-06:00"
}
```

### NOT-06 · Enviar aviso sin permiso · PASA

**Objetivo.** Un repartidor no envía avisos.

**Petición.** `POST http://notificaciones:5108/api/v1/notificaciones`

```http
Accept: application/json
X-Traza-Id: 0857ea94-08f2-461f-a627-a17d6be5fef4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "usuario_id": 1,
  "tipo": "sistema",
  "titulo": "x",
  "mensaje": "y"
}
```

**Respuesta.** HTTP 403 (esperado 403) · 28 ms · traza `0857ea94-08f2-461f-a627-a17d6be5fef4`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "0857ea94-08f2-461f-a627-a17d6be5fef4"
  }
}
```

### NOT-07 · Destinatario inexistente · PASA

**Objetivo.** Validación contra PostgreSQL.

**Petición.** `POST http://notificaciones:5108/api/v1/notificaciones`

```http
Accept: application/json
X-Traza-Id: d7b36bef-58e0-42ff-9109-97ec8295c670
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "usuario_id": 999999,
  "tipo": "sistema",
  "titulo": "x",
  "mensaje": "y"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 26 ms · traza `d7b36bef-58e0-42ff-9109-97ec8295c670`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "usuario_id",
        "mensaje": "No existe un usuario activo con ese id."
      }
    ],
    "traza_id": "d7b36bef-58e0-42ff-9109-97ec8295c670"
  }
}
```

### NOT-08 · Borrar un aviso (DELETE) · PASA

**Objetivo.** Quitarlo de la bandeja.

**Petición.** `DELETE http://notificaciones:5108/api/v1/notificaciones/5`

```http
Accept: application/json
X-Traza-Id: fc75ad14-4474-4e18-b6f5-7a8424ea1b63
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 25 ms · traza `fc75ad14-4474-4e18-b6f5-7a8424ea1b63`

```json
(sin cuerpo)
```

### NOT-09 · Mi bandeja (XML) · PASA

**Objetivo.** La bandeja en XML.

**Petición.** `GET http://notificaciones:5108/api/v1/notificaciones?por_pagina=2`

```http
Accept: application/xml
X-Traza-Id: 345aea5f-d409-4256-8849-5dfa0151036d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 46 ms · traza `345aea5f-d409-4256-8849-5dfa0151036d`

```xml
<?xml version='1.0' encoding='utf-8'?>
<notificaciones xmlns="urn:microhubs:v1" version="1"><datos><notificacion><id>2</id><tipo>entrega</tipo><titulo>Nueva entrega asignada</titulo><mensaje>Se te asignó el pedido PED-20261013-000154 (parada 2).</mensaje><leida>true</leida><referencia><tipo>entrega</tipo><id>130</id></referencia><creada_en>2026-10-13T08:11:59-06:00</creada_en></notificacion><notificacion><id>1</id><tipo>entrega</tipo><titulo>Nueva entrega asignada</titulo><mensaje>Se te asignó el pedido PED-20261013-000153 (parada 1).</mensaje><leida>false</leida><referencia><tipo>entrega</tipo><id>129</id></referencia><creada_en>2026-10-13T08:11:59-06:00</creada_en></notificacion></datos><paginacion><pagina>1</pagina><por_pagina>2</por_pagina><total>2</total><paginas>1</paginas></paginacion></notificaciones>
```

## Servicio auth · puerto 5101

### SAL-AUT · Salud de auth · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://auth:5101/api/v1/health`

```http
Accept: application/json
X-Traza-Id: e00faf43-349a-443e-8434-93bad4570415
```

**Respuesta.** HTTP 200 (esperado 200) · 15 ms · traza `e00faf43-349a-443e-8434-93bad4570415`

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
X-Traza-Id: b7ceabaf-59af-475b-a369-0181a58439d0
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `b7ceabaf-59af-475b-a369-0181a58439d0`

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

## Servicio catalogos · puerto 5103

### SAL-CAT · Salud de catalogos · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://catalogos:5103/api/v1/health`

```http
Accept: application/json
X-Traza-Id: be50f0a0-045a-4557-a2ed-faacca43c2fb
```

**Respuesta.** HTTP 200 (esperado 200) · 15 ms · traza `be50f0a0-045a-4557-a2ed-faacca43c2fb`

```json
{
  "servicio": "catalogos",
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
X-Traza-Id: c3e2cf96-f789-4a87-9a11-8a5b69ea0a3b
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `c3e2cf96-f789-4a87-9a11-8a5b69ea0a3b`

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
X-Traza-Id: ba082ec5-2e1f-4b52-99b8-7097b619278f
```

**Respuesta.** HTTP 200 (esperado 200) · 21 ms · traza `ba082ec5-2e1f-4b52-99b8-7097b619278f`

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
X-Traza-Id: 8e94097f-a936-4634-b393-7ade29280ea6
```

**Respuesta.** HTTP 200 (esperado 200) · 21 ms · traza `8e94097f-a936-4634-b393-7ade29280ea6`

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
X-Traza-Id: c0c0ced3-6d10-4cd1-857f-b95ab4c979b6
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `c0c0ced3-6d10-4cd1-857f-b95ab4c979b6`

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

## Servicio notificaciones · puerto 5108

### SAL-NOT · Salud de notificaciones · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://notificaciones:5108/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 32597578-f057-48f1-a7d8-53a8a2032040
```

**Respuesta.** HTTP 200 (esperado 200) · 15 ms · traza `32597578-f057-48f1-a7d8-53a8a2032040`

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
X-Traza-Id: 027bc2a8-f6d6-4c8a-8a10-4b1a30efcd4d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 87 ms · traza `027bc2a8-f6d6-4c8a-8a10-4b1a30efcd4d`

```json
{
  "valido": true,
  "expira_en": 893,
  "usuario": {
    "id": 1,
    "rol": "administrador",
    "microhub_id": null
  }
}
```

**Explicación.** El X-Traza-Id de la petición se recupera en logs_tecnicos.correlacion_id.

**Evidencia en MongoDB.** `db.logs_tecnicos.findOne({correlacion_id: '027bc2a8-f6d6-4c8a-8a10-4b1a30efcd4d'})`

```json
{
  "nivel": "INFO",
  "componente": "auth",
  "registrado_en": "2026-10-13 14:12:08.082000+00:00",
  "correlacion_id": "027bc2a8-f6d6-4c8a-8a10-4b1a30efcd4d",
  "mensaje": "GET /api/v1/auth/validar -> 200",
  "usuario_id": 1,
  "ruta": "/api/v1/auth/validar",
  "duracion_ms": 3,
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
    "ms_promedio": 153.44444444444446
  },
  {
    "_id": "catalogos",
    "peticiones": 9,
    "ms_promedio": 41.22222222222222
  },
  {
    "_id": "documentos",
    "peticiones": 10,
    "ms_promedio": 16.1
  },
  {
    "_id": "entregas",
    "peticiones": 14,
    "ms_promedio": 69.57142857142857
  },
  {
    "_id": "notificaciones",
    "peticiones": 9,
    "ms_promedio": 31.333333333333332
  },
  {
    "_id": "pedidos",
    "peticiones": 8,
    "ms_promedio": 52.375
  },
  {
    "_id": "planeacion",
    "peticiones": 16,
    "ms_promedio": 69.25
  },
  {
    "_id": "usuarios",
    "peticiones": 8,
    "ms_promedio": 27.75
  }
]
```

## Servicio catalogos · puerto 5103

### RAT-01 · Límite de consumo excedido · PASA

**Objetivo.** Más de 240 solicitudes por minuto desde la misma IP.

**Petición.** `GET http://catalogos:5103/api/v1/zonas`

```http
Accept: application/json
X-Traza-Id: ee6181ab-8772-49f2-b4b2-486f8c128219
```

**Respuesta.** HTTP 429 (esperado 429) · 4 ms · traza `ee6181ab-8772-49f2-b4b2-486f8c128219`

```json
{
  "error": {
    "codigo": "LIMITE_EXCEDIDO",
    "mensaje": "Máximo 240 solicitudes por minuto. Espera 50 segundos.",
    "traza_id": "ee6181ab-8772-49f2-b4b2-486f8c128219"
  }
}
```

**Explicación.** Contador rate:catalogos:{ip}:{minuto} en Redis (db 1) con TTL de 120 s; responde Retry-After.

**Evidencia en Redis.** `db1 GET rate:catalogos:a2c150a8debab0b5:29865012; db1 TTL rate:catalogos:a2c150a8debab0b5:29865012`

```json
[
  {
    "comando": "db1 GET rate:catalogos:a2c150a8debab0b5:29865012",
    "valor": "242"
  },
  {
    "comando": "db1 TTL rate:catalogos:a2c150a8debab0b5:29865012",
    "valor": 113
  }
]
```
