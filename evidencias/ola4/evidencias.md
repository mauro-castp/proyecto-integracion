# Evidencias de petición y respuesta · microservicios v1

Generado el 2026-11-26 21:24 contra los servicios en ejecución. 430 de 430 casos pasan.

## Servicio auth · puerto 5101

### AUTH-01 · Iniciar sesión (JSON) · PASA

**Objetivo.** Emitir el JWT de acceso y el token de renovación del repartidor.

**Petición.** `POST http://auth:5101/api/v1/auth/login`

```http
Accept: application/json
X-Traza-Id: cd3fe5b1-21a9-4e2f-875c-8e74940d7583
Content-Type: application/json
```

```json
{
  "correo": "repartidor1@codex.mx",
  "clave": "********",
  "dispositivo": "Pixel 7"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 310 ms · traza `cd3fe5b1-21a9-4e2f-875c-8e74940d7583`

```json
{
  "token_acceso": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwicm9sIjo…(291 caracteres)",
  "token_renovacion": "rt_e8e9910611e3201502019d1e4346c858",
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

**Evidencia en Redis.** `SMEMBERS auth:sesion:7; TTL auth:sesion:7; TTL auth:refresh:75927d09c02adae14b0b0459d0a82a2ddb5b8b307b88471d02f1035aa3a2df57`

```json
[
  {
    "comando": "SMEMBERS auth:sesion:7",
    "valor": [
      "1a42f6d90c0442e498f590a07421bc75",
      "398d91578fb74138a34898c79d922de4",
      "466a4354e09e4f648f12aec6d6499541",
      "52a13feb8d6f4ee99085ccc783963ce1",
      "64e2341a9a254d01b86ec22b0a223c72",
      "70767108147a485b895a30370ee52e41",
      "822428bbf26246f5844af3f10768a61f",
      "aec359bfeb4a4faaa2eea67ab980f22a",
      "b020502625ec4de7a2717f3a9250232a",
      "b4d9562bbd5f43d49a3347439b0fa4d7",
      "b51c853f9f664e41ba5133efb3670570",
      "b973d67902034639b1f737dcd86a914d",
      "ca6690fecf81465098da47050a9e9fee",
      "cde33f8dd9c0414f85f5964e97492a47"
    ]
  },
  {
    "comando": "TTL auth:sesion:7",
    "valor": 900
  },
  {
    "comando": "TTL auth:refresh:75927d09c02adae14b0b0459d0a82a2ddb5b8b307b88471d02f1035aa3a2df57",
    "valor": 604800
  }
]
```

**Evidencia en PostgreSQL.** `SELECT fecha, modulo, accion, detalle FROM auditoria WHERE correo_intento IS NULL AND usuario_id = 7 AND modulo = 'auth' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "fecha": "2026-11-26 15:22:46.041392-06:00",
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
X-Traza-Id: a44ebdc1-3554-4ba1-97fb-d9c6a2e18aa1
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><login xmlns="urn:microhubs:v1"><correo>planeador@codex.mx</correo><clave>********</clave></login>
```

**Respuesta.** HTTP 200 (esperado 200) · 399 ms · traza `a44ebdc1-3554-4ba1-97fb-d9c6a2e18aa1`

```xml
<?xml version='1.0' encoding='utf-8'?>
<sesion xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><token_acceso>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwicm9sIjo…(291 caracteres)</token_acceso><token_renovacion>rt_3eefded49e131c01633f063282862bfc</token_renovacion><tipo>Bearer</tipo><expira_en>900</expira_en><usuario><id>5</id><nombre>Vanessa</nombre><apellidos>Morante López</apellidos><correo>planeador@codex.mx</correo><rol>planeador</rol><microhub_id xsi:nil="true" /><permisos><permiso>abastecimiento.ver</permiso><permiso>archivos.crear</permiso><permiso>archivos.ver</permiso><permiso>capacidad.editar</permiso><permiso>capacidad.ver</permiso><permiso>catalogo_publico.ver</permiso><permiso>cobertura.ver</permiso><permiso>configuracion.ver</permiso><permiso>costos.editar</permiso><permiso>costos.ver</permiso><permiso>demanda.editar</permiso><permiso>demanda.ver</permiso><permiso>equilibrio.editar</permiso><permiso>equilibrio.ver</permiso><permiso>indicadores.ver</permiso><permiso>inventario.ver</permiso><permiso>microhubs.ver</permiso><permiso>monitoreo.ver</permiso><permiso>notificaciones.ver</permiso><permiso>pedidos.reasignar</permiso><permiso>pedidos.ver</permiso><permiso>planeacion.editar</permiso><permiso>planeacion.ver</permiso><permiso>precios.ver</permiso><permiso>productos.ver</permiso><permiso>proveedores.ver</permiso><permiso>reportes.exportar</permiso><permiso>reportes.ver</permiso><permiso>rutas.planear</permiso><permiso>rutas.ver</permiso><permiso>simulacion.ejecutar</permiso><permiso>simulacion.ver</permiso><permiso>surtido.editar</permiso><permiso>surtido.ver</permiso><permiso>zonas.ver</permiso></permisos></usuario></sesion>
```

**Explicación.** El cuerpo XML se valida contra los XSD antes de procesarse; la respuesta <sesion> también cumple el XSD.

### AUTH-03 · Clave incorrecta · PASA

**Objetivo.** Rechazar credenciales y contar el intento.

**Petición.** `POST http://auth:5101/api/v1/auth/login`

```http
Accept: application/json
X-Traza-Id: 33af0437-a3ba-4164-a56e-599b2296654c
Content-Type: application/json
```

```json
{
  "correo": "auditor@codex.mx",
  "clave": "********"
}
```

**Respuesta.** HTTP 401 (esperado 401) · 222 ms · traza `33af0437-a3ba-4164-a56e-599b2296654c`

```json
{
  "error": {
    "codigo": "CREDENCIALES_INVALIDAS",
    "mensaje": "Correo o clave incorrectos. Intento 1 de 5.",
    "traza_id": "33af0437-a3ba-4164-a56e-599b2296654c"
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
X-Traza-Id: 6b323327-bac5-4198-9e87-977f8dc83d64
Content-Type: application/json
```

```json
{
  "correo": "sin-arroba",
  "clave": "********"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 6 ms · traza `6b323327-bac5-4198-9e87-977f8dc83d64`

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
    "traza_id": "6b323327-bac5-4198-9e87-977f8dc83d64"
  }
}
```

### AUTH-05 · XML con DTD (ataque XXE) · PASA

**Objetivo.** Rechazar entidades externas y DTD.

**Petición.** `POST http://auth:5101/api/v1/auth/login`

```http
Accept: application/xml
X-Traza-Id: 8f62e6c3-107c-4862-823b-fb1345b88566
Content-Type: application/xml
```

```xml
<?xml version="1.0"?><!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]><login xmlns="urn:microhubs:v1"><correo>&e;</correo><clave>********</clave></login>
```

**Respuesta.** HTTP 400 (esperado 400) · 6 ms · traza `8f62e6c3-107c-4862-823b-fb1345b88566`

```xml
<?xml version='1.0' encoding='utf-8'?>
<error xmlns="urn:microhubs:v1" version="1"><codigo>XML_INVALIDO</codigo><mensaje>El cuerpo XML no está bien formado o contiene DTD/entidades.</mensaje><traza_id>8f62e6c3-107c-4862-823b-fb1345b88566</traza_id></error>
```

**Explicación.** El lector XML (defusedxml) prohíbe DTD y entidades; el error también llega en XML.

### AUTH-06 · Validar token · PASA

**Objetivo.** Comprobar firma, vigencia y sesión activa en Redis.

**Petición.** `GET http://auth:5101/api/v1/auth/validar`

```http
Accept: application/json
X-Traza-Id: 423ba807-501e-4e52-a056-bc8e72c97cc4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 7 ms · traza `423ba807-501e-4e52-a056-bc8e72c97cc4`

```json
{
  "valido": true,
  "expira_en": 900,
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
X-Traza-Id: 50f6306e-53d8-44d2-8f21-0ae6ff123330
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 401 (esperado 401) · 8 ms · traza `50f6306e-53d8-44d2-8f21-0ae6ff123330`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.",
    "traza_id": "50f6306e-53d8-44d2-8f21-0ae6ff123330"
  }
}
```

### AUTH-08 · Renovar sesión · PASA

**Objetivo.** Obtener tokens nuevos con el token de renovación (rotación).

**Petición.** `POST http://auth:5101/api/v1/auth/renovar`

```http
Accept: application/json
X-Traza-Id: c6c186cf-afbb-4f5c-b944-7a281006db8c
Content-Type: application/json
```

```json
{
  "token_renovacion": "rt_51b28f7c58fa24efedead03e6a477366"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 94 ms · traza `c6c186cf-afbb-4f5c-b944-7a281006db8c`

```json
{
  "token_acceso": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwicm9sIjo…(291 caracteres)",
  "token_renovacion": "rt_ee2f9310c4962af1339543bae5ee4c92",
  "tipo": "Bearer",
  "expira_en": 900
}
```

**Explicación.** El token de renovación usado se borra de Redis y su acceso anterior queda revocado.

**Evidencia en Redis.** `EXISTS auth:refresh:b5fbdc425fe2433e88b34386fa2e56fcb95cbc309fee9e5a807ca156836a2f1f`

```json
[
  {
    "comando": "EXISTS auth:refresh:b5fbdc425fe2433e88b34386fa2e56fcb95cbc309fee9e5a807ca156836a2f1f",
    "valor": 0
  }
]
```

### AUTH-09 · Reusar un token de renovación · PASA

**Objetivo.** Un token de renovación sirve una sola vez.

**Petición.** `POST http://auth:5101/api/v1/auth/renovar`

```http
Accept: application/json
X-Traza-Id: 4b5d5efd-a3be-4326-b153-289eaf6d6c3b
Content-Type: application/json
```

```json
{
  "token_renovacion": "rt_51b28f7c58fa24efedead03e6a477366"
}
```

**Respuesta.** HTTP 401 (esperado 401) · 19 ms · traza `4b5d5efd-a3be-4326-b153-289eaf6d6c3b`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.",
    "traza_id": "4b5d5efd-a3be-4326-b153-289eaf6d6c3b"
  }
}
```

### AUTH-10 · Cerrar sesión · PASA

**Objetivo.** Revocar el acceso del encabezado y la renovación del cuerpo.

**Petición.** `POST http://auth:5101/api/v1/auth/salir`

```http
Accept: application/json
X-Traza-Id: 81827b68-094f-408f-976d-2cf2c1d1a422
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "token_renovacion": "rt_ee2f9310c4962af1339543bae5ee4c92"
}
```

**Respuesta.** HTTP 204 (esperado 204) · 32 ms · traza `81827b68-094f-408f-976d-2cf2c1d1a422`

```json
(sin cuerpo)
```

**Explicación.** El jti se agrega a la lista de revocados con TTL igual a su vida restante y sale del conjunto de sesión.

**Evidencia en Redis.** `TTL auth:jti:revocado:e66eb3d014a24f619a81c0918a3f9ca5; SISMEMBER auth:sesion:7 e66eb3d014a24f619a81c0918a3f9ca5`

```json
[
  {
    "comando": "TTL auth:jti:revocado:e66eb3d014a24f619a81c0918a3f9ca5",
    "valor": 899
  },
  {
    "comando": "SISMEMBER auth:sesion:7 e66eb3d014a24f619a81c0918a3f9ca5",
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
X-Traza-Id: e6d27ae9-7436-4f51-b34f-546a9bfa785d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 401 (esperado 401) · 7 ms · traza `e6d27ae9-7436-4f51-b34f-546a9bfa785d`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.",
    "traza_id": "e6d27ae9-7436-4f51-b34f-546a9bfa785d"
  }
}
```

**Explicación.** El servicio de usuarios consulta auth:jti:revocado en Redis: la revocación es común a todos.

### USR-01 · Mi perfil (JSON) · PASA

**Objetivo.** Consultar el perfil de quien inició sesión.

**Petición.** `GET http://usuarios:5102/api/v1/usuarios/yo`

```http
Accept: application/json
X-Traza-Id: dc82c4f9-8fd4-43f8-a776-6b0bbbe824fd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 29 ms · traza `dc82c4f9-8fd4-43f8-a776-6b0bbbe824fd`

```json
{
  "id": 7,
  "nombre": "Ramiro",
  "apellidos": "Alanís Lozano",
  "correo": "repartidor1@codex.mx",
  "telefono": "8112345678",
  "rol": "repartidor",
  "microhub": null,
  "ultimo_acceso": "2026-11-26T15:22:46-06:00"
}
```

### USR-02 · Mi perfil (XML) · PASA

**Objetivo.** El mismo recurso en XML según Accept.

**Petición.** `GET http://usuarios:5102/api/v1/usuarios/yo`

```http
Accept: application/xml
X-Traza-Id: 324e7f5b-e085-4a82-bc6d-3e16ce639889
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 26 ms · traza `324e7f5b-e085-4a82-bc6d-3e16ce639889`

```xml
<?xml version='1.0' encoding='utf-8'?>
<usuario xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>5</id><nombre>Vanessa</nombre><apellidos>Morante López</apellidos><correo>planeador@codex.mx</correo><telefono>8178109897</telefono><rol>planeador</rol><microhub xsi:nil="true" /><ultimo_acceso>2026-11-26T15:22:47-06:00</ultimo_acceso></usuario>
```

### USR-03 · Actualizar mi teléfono (PATCH) · PASA

**Objetivo.** Modificar un dato del perfil.

**Petición.** `PATCH http://usuarios:5102/api/v1/usuarios/yo`

```http
Accept: application/json
X-Traza-Id: 727bdde9-31db-4d6d-a81b-a48dd96c5b8b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "telefono": "8112345678"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 68 ms · traza `727bdde9-31db-4d6d-a81b-a48dd96c5b8b`

```json
{
  "id": 7,
  "nombre": "Ramiro",
  "apellidos": "Alanís Lozano",
  "correo": "repartidor1@codex.mx",
  "telefono": "8112345678",
  "rol": "repartidor",
  "microhub": null,
  "ultimo_acceso": "2026-11-26T15:22:46-06:00"
}
```

**Explicación.** El trigger de auditoría registra el cambio con el usuario que actuó.

**Evidencia en PostgreSQL.** `SELECT id, telefono, actualizado_en FROM usuario WHERE id = 7`

```json
[
  {
    "id": 7,
    "telefono": "8112345678",
    "actualizado_en": "2026-11-26 15:22:48.221527-06:00"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT fecha, accion, entidad, detalle FROM auditoria WHERE entidad = 'usuario' AND entidad_id = '7' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "fecha": "2026-11-26 15:22:48.221527-06:00",
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
X-Traza-Id: 389ae0fd-3569-4e02-be17-08a272d21311
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "telefono": "12ab"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 6 ms · traza `389ae0fd-3569-4e02-be17-08a272d21311`

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
    "traza_id": "389ae0fd-3569-4e02-be17-08a272d21311"
  }
}
```

### USR-05 · Lista de usuarios (administrador) · PASA

**Objetivo.** Búsqueda y paginación.

**Petición.** `GET http://usuarios:5102/api/v1/usuarios?q=codex&rol=operador&pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: b1c71532-197a-4665-b9e1-08f77ae88e1c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 66 ms · traza `b1c71532-197a-4665-b9e1-08f77ae88e1c`

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
      "ultimo_acceso": "2026-11-26T15:22:02-06:00"
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
      "ultimo_acceso": "2026-11-26T15:22:07-06:00"
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
      "ultimo_acceso": "2026-11-26T14:19:31-06:00"
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
X-Traza-Id: 4d4e9d90-83f3-4601-8d6e-fe1a42a752f3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 26 ms · traza `4d4e9d90-83f3-4601-8d6e-fe1a42a752f3`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "4d4e9d90-83f3-4601-8d6e-fe1a42a752f3"
  }
}
```

**Evidencia en PostgreSQL.** `SELECT fecha, modulo, accion, detalle, exitoso FROM auditoria WHERE accion = 'acceso_denegado' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "fecha": "2026-11-26 15:22:48.401232-06:00",
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
X-Traza-Id: 173a3d4c-4315-4c02-9c3e-ee2e19ccb71a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 29 ms · traza `173a3d4c-4315-4c02-9c3e-ee2e19ccb71a`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "173a3d4c-4315-4c02-9c3e-ee2e19ccb71a"
  }
}
```

## Servicio productos · puerto 5103

### PRO-01 · Productos con búsqueda (caché vacía) · PASA

**Objetivo.** Consultar productos; la respuesta se guarda en Redis.

**Petición.** `GET http://productos:5103/api/v1/productos?q=arroz&pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 249c2ae1-0969-43a7-9cbc-ddba171ef3a0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 69 ms · traza `249c2ae1-0969-43a7-9cbc-ddba171ef3a0`

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

**Evidencia en Redis.** `db1 TTL cache:catalogo:productos:538d03b535d84110; db1 TTL cache:catalogo:productos:04d4a6a9d27021cf`

```json
[
  {
    "comando": "db1 TTL cache:catalogo:productos:538d03b535d84110",
    "valor": 216
  },
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
X-Traza-Id: 5a342d8f-f90b-4102-a19e-10e9d0475ba9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 5 ms · traza `5a342d8f-f90b-4102-a19e-10e9d0475ba9`

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
X-Traza-Id: 3e6e17ce-72e0-4693-acf8-3953246eb615
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 68 ms · traza `3e6e17ce-72e0-4693-acf8-3953246eb615`

```xml
<?xml version='1.0' encoding='utf-8'?>
<productos xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><datos><producto><id>3</id><clave_interna>AB-003</clave_interna><nombre>Aceite vegetal</nombre><categoria><id>1</id><nombre>Abarrote básico</nombre></categoria><unidad>botella</unidad><presentacion>900 ml</presentacion><precio>42.00</precio><imagen_url xsi:nil="true" /><estatus>activo</estatus></producto><producto><id>2</id><clave_interna>AB-002</clave_interna><nombre>Arroz superextra</nombre><categoria><id>1</id><nombre>Abarrote básico</nombre></categoria><unidad>kg</unidad><presentacion>1 kg</presentacion><precio>29.90</precio><imagen_url xsi:nil="true" /><estatus>activo</estatus></producto></datos><paginacion><pagina>1</pagina><por_pagina>2</por_pagina><total>51</total><paginas>26</paginas></paginacion></productos>
```

### PRO-04 · Un producto · PASA

**Objetivo.** Detalle por id.

**Petición.** `GET http://productos:5103/api/v1/productos/3`

```http
Accept: application/json
X-Traza-Id: 74d04447-71d5-4889-a39a-516985ef26c7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 47 ms · traza `74d04447-71d5-4889-a39a-516985ef26c7`

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
X-Traza-Id: 99b35915-f44b-4c74-b7dd-67c8e5d5e138
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 48 ms · traza `99b35915-f44b-4c74-b7dd-67c8e5d5e138`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "99b35915-f44b-4c74-b7dd-67c8e5d5e138"
  }
}
```

### PRO-06 · Paginación fuera de rango · PASA

**Objetivo.** por_pagina máximo 100.

**Petición.** `GET http://productos:5103/api/v1/productos?por_pagina=500`

```http
Accept: application/json
X-Traza-Id: 63808f95-d4d0-4a64-a8b3-fb8ffd70e442
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 6 ms · traza `63808f95-d4d0-4a64-a8b3-fb8ffd70e442`

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
    "traza_id": "63808f95-d4d0-4a64-a8b3-fb8ffd70e442"
  }
}
```

### PRO-07 · Sin token · PASA

**Objetivo.** Todo endpoint protegido exige Authorization: Bearer.

**Petición.** `GET http://productos:5103/api/v1/productos`

```http
Accept: application/json
X-Traza-Id: 8ce3d5f5-1979-48c5-82ea-3b787d69826a
```

**Respuesta.** HTTP 401 (esperado 401) · 4 ms · traza `8ce3d5f5-1979-48c5-82ea-3b787d69826a`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "Falta el encabezado Authorization: Bearer <token>.",
    "traza_id": "8ce3d5f5-1979-48c5-82ea-3b787d69826a"
  }
}
```

## Servicio zonas · puerto 5108

### ZON-01 · Zonas (XML) · PASA

**Objetivo.** Colonias atendidas con centroide, válidas contra catalogos.xsd.

**Petición.** `GET http://zonas:5108/api/v1/zonas`

```http
Accept: application/xml
X-Traza-Id: dcfebb45-27d9-454c-8a6e-ee11668e1709
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 594 ms · traza `dcfebb45-27d9-454c-8a6e-ee11668e1709`

```xml
<?xml version='1.0' encoding='utf-8'?>
<zonas xmlns="urn:microhubs:v1" version="1"><datos><zona><id>1</id><clave>ZN-SB01</clave><nombre>San Bernabé Centro</nombre><colonia>San Bernabé</colonia><codigo_postal>64100</codigo_postal><latitud>25.7455</latitud><longitud>-100.3585</longitud></zona><zona><id>2</id><clave>ZN-SB02</clave><nombre>Valles de San Bernabé</nombre><colonia>Valles de San Bernabé</colonia><codigo_postal>64103</codigo_postal><latitud>25.753</latitud><longitud>-100.369</longitud></zona><zona><id>3</id><clave>ZN-SB03</clave><nombre>Paseo de San Bernabé</nombre><colonia>Paseo de San Bernabé</colonia><codigo_postal>64103</codigo_postal><latitud>25.758</latitud><longitud>-100.3745</longitud></zona><zona><id>4</id><clave>ZN-SB04</clave><nombre>San Bernabé X (F-113)</nombre><colonia>San Bernabé X (F-113)</colonia><codigo_postal>64105</codigo_postal><latitud>25.7495</latitud><longitud>-100.38</longitud></zona></datos><paginacion><pagina>1</pagina><por_pagina>20</por_pagina><total>4</total><paginas>1</paginas></paginacion></zonas>
```

### ZON-02 · Una zona · PASA

**Objetivo.** Detalle por id.

**Petición.** `GET http://zonas:5108/api/v1/zonas/1`

```http
Accept: application/json
X-Traza-Id: a5bd87d9-a9ef-49d8-bd3e-2130d7a25255
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 26 ms · traza `a5bd87d9-a9ef-49d8-bd3e-2130d7a25255`

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
X-Traza-Id: 6df9dd3b-2a62-48ab-a854-a7f54682846a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 23 ms · traza `6df9dd3b-2a62-48ab-a854-a7f54682846a`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "6df9dd3b-2a62-48ab-a854-a7f54682846a"
  }
}
```

### ZON-04 · Sin token · PASA

**Objetivo.** Todo endpoint protegido exige Authorization: Bearer.

**Petición.** `GET http://zonas:5108/api/v1/zonas`

```http
Accept: application/json
X-Traza-Id: ba930db9-6e52-42ce-9e01-842d981d9677
```

**Respuesta.** HTTP 401 (esperado 401) · 35 ms · traza `ba930db9-6e52-42ce-9e01-842d981d9677`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "Falta el encabezado Authorization: Bearer <token>.",
    "traza_id": "ba930db9-6e52-42ce-9e01-842d981d9677"
  }
}
```

## Servicio microhubs · puerto 5109

### MIC-01 · Microhubs activos · PASA

**Objetivo.** Microhubs con coordenadas y radio.

**Petición.** `GET http://microhubs:5109/api/v1/microhubs?estatus=activo`

```http
Accept: application/json
X-Traza-Id: 899186e6-d194-418c-a552-549b1d28293f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 1214 ms · traza `899186e6-d194-418c-a552-549b1d28293f`

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
X-Traza-Id: 67cda861-84de-4fc7-936e-db7070b9e0ef
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 91 ms · traza `67cda861-84de-4fc7-936e-db7070b9e0ef`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "67cda861-84de-4fc7-936e-db7070b9e0ef"
  }
}
```

### MIC-03 · Sin token · PASA

**Objetivo.** Todo endpoint protegido exige Authorization: Bearer.

**Petición.** `GET http://microhubs:5109/api/v1/microhubs`

```http
Accept: application/json
X-Traza-Id: 3c8623d9-be2a-44a2-b9d2-8a128f26fd41
```

**Respuesta.** HTTP 401 (esperado 401) · 11 ms · traza `3c8623d9-be2a-44a2-b9d2-8a128f26fd41`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "Falta el encabezado Authorization: Bearer <token>.",
    "traza_id": "3c8623d9-be2a-44a2-b9d2-8a128f26fd41"
  }
}
```

## Servicio pedidos · puerto 5104

### PED-01 · Pedidos entregados (JSON) · PASA

**Objetivo.** Lista filtrada por estado y fechas.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos?estado=entregado&pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 09531e89-3e0f-498c-bf9e-2b618711459c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 152 ms · traza `09531e89-3e0f-498c-bf9e-2b618711459c`

```json
{
  "datos": [
    {
      "id": 586,
      "folio": "PED-20261126-000586",
      "estado": "entregado",
      "zona": {
        "id": 3,
        "nombre": "Paseo de San Bernabé"
      },
      "microhub_id": 9,
      "total": 336.0,
      "creado_en": "2026-11-26T15:21:59-06:00"
    },
    {
      "id": 583,
      "folio": "PED-20261126-000583",
      "estado": "entregado",
      "zona": {
        "id": 3,
        "nombre": "Paseo de San Bernabé"
      },
      "microhub_id": 8,
      "total": 336.0,
      "creado_en": "2026-11-26T15:21:17-06:00"
    },
    {
      "id": 579,
      "folio": "PED-20261126-000579",
      "estado": "entregado",
      "zona": {
        "id": 3,
        "nombre": "Paseo de San Bernabé"
      },
      "microhub_id": 2,
      "total": 300.0,
      "creado_en": "2026-11-26T15:17:20-06:00"
    },
    {
      "id": 575,
      "folio": "PED-20261126-000575",
      "estado": "entregado",
      "zona": {
        "id": 3,
        "nombre": "Paseo de San Bernabé"
      },
      "microhub_id": 2,
      "total": 300.0,
      "creado_en": "2026-11-26T15:17:02-06:00"
    },
    {
      "id": 571,
      "folio": "PED-20261126-000571",
      "estado": "entregado",
      "zona": {
        "id": 3,
        "nombre": "Paseo de San Bernabé"
      },
      "microhub_id": 2,
      "total": 300.0,
      "creado_en": "2026-11-26T15:16:30-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 157,
    "paginas": 32
  }
}
```

### PED-02 · Pedidos (XML) · PASA

**Objetivo.** La misma lista en XML.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos?estado=entregado&por_pagina=2`

```http
Accept: application/xml
X-Traza-Id: 4aa562ee-4486-4111-89cf-8eb13e13abcb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 147 ms · traza `4aa562ee-4486-4111-89cf-8eb13e13abcb`

```xml
<?xml version='1.0' encoding='utf-8'?>
<pedidos xmlns="urn:microhubs:v1" version="1"><datos><pedido><id>586</id><folio>PED-20261126-000586</folio><estado>entregado</estado><zona><id>3</id><nombre>Paseo de San Bernabé</nombre></zona><microhub_id>9</microhub_id><total>336.00</total><creado_en>2026-11-26T15:21:59-06:00</creado_en></pedido><pedido><id>583</id><folio>PED-20261126-000583</folio><estado>entregado</estado><zona><id>3</id><nombre>Paseo de San Bernabé</nombre></zona><microhub_id>8</microhub_id><total>336.00</total><creado_en>2026-11-26T15:21:17-06:00</creado_en></pedido></datos><paginacion><pagina>1</pagina><por_pagina>2</por_pagina><total>157</total><paginas>79</paginas></paginacion></pedidos>
```

### PED-03 · Detalle con líneas · PASA

**Objetivo.** Cliente, domicilio y líneas del pedido.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/586`

```http
Accept: application/json
X-Traza-Id: 590dee30-12d2-4794-92a9-c5bcd1032083
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 131 ms · traza `590dee30-12d2-4794-92a9-c5bcd1032083`

```json
{
  "id": 586,
  "folio": "PED-20261126-000586",
  "estado": "entregado",
  "cliente": {
    "nombre": "Juan Chapa Sepúlveda",
    "telefono": "8132806648"
  },
  "domicilio": {
    "calle": "Nogal",
    "numero_ext": "1440",
    "colonia": "Paseo de San Bernabé",
    "latitud": 25.759995,
    "longitud": -100.371091
  },
  "zona": {
    "id": 3,
    "nombre": "Paseo de San Bernabé"
  },
  "microhub_id": 9,
  "subtotal": 336.0,
  "costo_envio": 0.0,
  "total": 336.0,
  "creado_en": "2026-11-26T15:21:59-06:00",
  "lineas": [
    {
      "id": 1527,
      "producto_id": 31,
      "nombre": "Queso fresco",
      "cantidad": 3,
      "precio_unitario": 58.0,
      "importe": 174.0
    },
    {
      "id": 1528,
      "producto_id": 47,
      "nombre": "Shampoo",
      "cantidad": 3,
      "precio_unitario": 54.0,
      "importe": 162.0
    }
  ]
}
```

### PED-04 · Historial de estados · PASA

**Objetivo.** Cambios de estado con usuario y fecha.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/586/historial`

```http
Accept: application/json
X-Traza-Id: 2e25f845-0407-449e-a7a6-61065b5afd20
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 94 ms · traza `2e25f845-0407-449e-a7a6-61065b5afd20`

```json
{
  "pedido_id": 586,
  "eventos": [
    {
      "estado_anterior": null,
      "estado_nuevo": "creado",
      "usuario": "juan.chapa1@correo.mx",
      "motivo": null,
      "fecha": "2026-11-26T15:21:59-06:00"
    },
    {
      "estado_anterior": "creado",
      "estado_nuevo": "asignado",
      "usuario": "juan.chapa1@correo.mx",
      "motivo": null,
      "fecha": "2026-11-26T15:21:59-06:00"
    },
    {
      "estado_anterior": "asignado",
      "estado_nuevo": "en_preparacion",
      "usuario": "operador.e0fde@ejemplo.mx",
      "motivo": null,
      "fecha": "2026-11-26T15:21:59-06:00"
    },
    {
      "estado_anterior": "en_preparacion",
      "estado_nuevo": "en_ruta",
      "usuario": "operador.e0fde@ejemplo.mx",
      "motivo": null,
      "fecha": "2026-11-26T15:21:59-06:00"
    },
    {
      "estado_anterior": "en_ruta",
      "estado_nuevo": "entregado",
      "usuario": "repartidor1@codex.mx",
      "motivo": null,
      "fecha": "2026-11-26T15:22:00-06:00"
    }
  ]
}
```

**Evidencia en PostgreSQL.** `SELECT fecha, estado_anterior, estado_nuevo, usuario_id FROM historial_estatus WHERE pedido_id = %s ORDER BY fecha, id`

```json
[
  {
    "fecha": "2026-11-26 15:21:59.114200-06:00",
    "estado_anterior": null,
    "estado_nuevo": "creado",
    "usuario_id": 9
  },
  {
    "fecha": "2026-11-26 15:21:59.114200-06:00",
    "estado_anterior": "creado",
    "estado_nuevo": "asignado",
    "usuario_id": 9
  },
  {
    "fecha": "2026-11-26 15:21:59.334760-06:00",
    "estado_anterior": "asignado",
    "estado_nuevo": "en_preparacion",
    "usuario_id": 59
  },
  {
    "fecha": "2026-11-26 15:21:59.730963-06:00",
    "estado_anterior": "en_preparacion",
    "estado_nuevo": "en_ruta",
    "usuario_id": 59
  },
  {
    "fecha": "2026-11-26 15:22:00.366559-06:00",
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
X-Traza-Id: af762c31-cd54-4ba1-b892-014189a87eac
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 7 ms · traza `af762c31-cd54-4ba1-b892-014189a87eac`

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
    "traza_id": "af762c31-cd54-4ba1-b892-014189a87eac"
  }
}
```

### PED-06 · Pedido fuera del ámbito · PASA

**Objetivo.** El operador del MH-01 no ve pedidos de otro microhub (RN22).

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/1`

```http
Accept: application/json
X-Traza-Id: a8890ff1-f23a-444a-bd4d-0a1bfff117c4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 43 ms · traza `a8890ff1-f23a-444a-bd4d-0a1bfff117c4`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el pedido o no está en tu ámbito.",
    "traza_id": "a8890ff1-f23a-444a-bd4d-0a1bfff117c4"
  }
}
```

**Explicación.** El ámbito lo decide PostgreSQL con fn_pedidos_visibles; el servicio no lo puede saltar.

### PED-07 · Cerrar desde pedidos · PASA

**Objetivo.** Los cierres de entrega solo se registran en el servicio de entregas.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/586/estado`

```http
Accept: application/json
X-Traza-Id: 227bdad2-c865-4b60-ab4c-3b5469d87d5f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "estado": "entregado"
}
```

**Respuesta.** HTTP 409 (esperado 409) · 7 ms · traza `227bdad2-c865-4b60-ab4c-3b5469d87d5f`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "El cierre de una entrega se registra con POST /api/v1/entregas/{id}/resultado.",
    "traza_id": "227bdad2-c865-4b60-ab4c-3b5469d87d5f"
  }
}
```

### PED-08 · Transición ilegal (regla del motor) · PASA

**Objetivo.** Un pedido entregado no puede regresar a preparación.

**Petición.** `PATCH http://pedidos:5104/api/v1/pedidos/2/estado`

```http
Accept: application/json
X-Traza-Id: e1cabf19-a3bd-4e36-99b2-3c617c4058b4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0Iiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "estado": "en_preparacion"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 79 ms · traza `e1cabf19-a3bd-4e36-99b2-3c617c4058b4`

```json
{
  "error": {
    "codigo": "REGLA_NEGOCIO",
    "mensaje": "RN20: transición ilegal entregado -> en_preparacion para el rol operador. El pedido PED-20261020-000002 conserva su estado.",
    "traza_id": "e1cabf19-a3bd-4e36-99b2-3c617c4058b4"
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
X-Traza-Id: 2929d3bd-a9cb-4ef6-b597-8a4c0dd75172
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "evidencia-entrega-302.jpg",
  "tipo_mime": "image/jpeg",
  "contenido_base64": "/9j/4AAQSkZJRgABAQAAAQABAAAAAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcY…(368 caracteres)",
  "referencia": {
    "tipo": "entrega",
    "id": "302"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 61 ms · traza `2929d3bd-a9cb-4ef6-b597-8a4c0dd75172`

```json
{
  "id": "6b08a32c5ea8dba9ecdb0af9",
  "nombre": "evidencia-entrega-302.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "302"
  },
  "subido_por": 7,
  "creado_en": "2026-11-26T15:22:52-06:00",
  "ruta": "documentos/2026/11/6b08a32c5ea8dba9ecdb0af9.jpg",
  "privacidad": "privado",
  "estado": "activo",
  "metadatos": {
    "almacen": "local",
    "origen": "api"
  }
}
```

**Explicación.** Se valida que el contenido sea JPEG real, se calcula su SHA-256 y que la entrega sea del repartidor.

**Evidencia en MongoDB.** `db.documentos.findOne({_id: ObjectId('6b08a32c5ea8dba9ecdb0af9')}, {contenido: 0})`

```json
{
  "_id": "6b08a32c5ea8dba9ecdb0af9",
  "nombre": "evidencia-entrega-302.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "302"
  },
  "subido_por": 7,
  "creado_en": "2026-11-26 21:22:52.133000+00:00",
  "ruta": "documentos/2026/11/6b08a32c5ea8dba9ecdb0af9.jpg",
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
X-Traza-Id: 2c88ab5d-3fbf-47a7-8656-511702d6cf5b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "evidencia-entrega-303.jpg",
  "tipo_mime": "image/jpeg",
  "contenido_base64": "/9j/4AAQSkZJRgABAQAAAQABAAAAAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcY…(368 caracteres)",
  "referencia": {
    "tipo": "entrega",
    "id": "303"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 87 ms · traza `2c88ab5d-3fbf-47a7-8656-511702d6cf5b`

```json
{
  "id": "6b08a32c5ea8dba9ecdb0afc",
  "nombre": "evidencia-entrega-303.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "303"
  },
  "subido_por": 7,
  "creado_en": "2026-11-26T15:22:52-06:00",
  "ruta": "documentos/2026/11/6b08a32c5ea8dba9ecdb0afc.jpg",
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
X-Traza-Id: e637de76-dcba-4b01-ba85-d8fcd0586442
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
    "id": "302"
  }
}
```

**Respuesta.** HTTP 422 (esperado 422) · 8 ms · traza `e637de76-dcba-4b01-ba85-d8fcd0586442`

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
    "traza_id": "e637de76-dcba-4b01-ba85-d8fcd0586442"
  }
}
```

### DOC-04 · Evidencia en entrega ajena · PASA

**Objetivo.** Un repartidor no adjunta a entregas de otro.

**Petición.** `POST http://documentos:5107/api/v1/documentos`

```http
Accept: application/json
X-Traza-Id: 00059624-c77e-4f70-a623-8e30d961fad4
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
    "id": "302"
  }
}
```

**Respuesta.** HTTP 403 (esperado 403) · 75 ms · traza `00059624-c77e-4f70-a623-8e30d961fad4`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Solo puedes adjuntar evidencia a tus entregas.",
    "traza_id": "00059624-c77e-4f70-a623-8e30d961fad4"
  }
}
```

### DOC-05 · Documento temporal · PASA

**Objetivo.** Documento que después se elimina.

**Petición.** `POST http://documentos:5107/api/v1/documentos`

```http
Accept: application/json
X-Traza-Id: 3dbc4fec-3339-4501-b2ee-930b3e38671d
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

**Respuesta.** HTTP 201 (esperado 201) · 40 ms · traza `3dbc4fec-3339-4501-b2ee-930b3e38671d`

```json
{
  "id": "6b08a32df59f7f9d08b26dd4",
  "nombre": "borrador.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "usuario",
    "id": "7"
  },
  "subido_por": 7,
  "creado_en": "2026-11-26T15:22:53-06:00",
  "ruta": "documentos/2026/11/6b08a32df59f7f9d08b26dd4.jpg",
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

**Petición.** `GET http://documentos:5107/api/v1/documentos?referencia_tipo=entrega&referencia_id=302`

```http
Accept: application/json
X-Traza-Id: 2fa4a263-2fa0-4a4d-ab7d-b50efa4023b6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 48 ms · traza `2fa4a263-2fa0-4a4d-ab7d-b50efa4023b6`

```json
{
  "datos": [
    {
      "id": "6b08a32c5ea8dba9ecdb0af9",
      "nombre": "evidencia-entrega-302.jpg",
      "tipo_mime": "image/jpeg",
      "tamano_bytes": 276,
      "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
      "referencia": {
        "tipo": "entrega",
        "id": "302"
      },
      "subido_por": 7,
      "creado_en": "2026-11-26T15:22:52-06:00",
      "ruta": "documentos/2026/11/6b08a32c5ea8dba9ecdb0af9.jpg",
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

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b08a32c5ea8dba9ecdb0af9`

```http
Accept: application/xml
X-Traza-Id: 16f8d562-3d87-48b9-8042-dfb4d0175eff
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 10 ms · traza `16f8d562-3d87-48b9-8042-dfb4d0175eff`

```xml
<?xml version='1.0' encoding='utf-8'?>
<documento xmlns="urn:microhubs:v1" version="1"><id>6b08a32c5ea8dba9ecdb0af9</id><nombre>evidencia-entrega-302.jpg</nombre><tipo_mime>image/jpeg</tipo_mime><tamano_bytes>276</tamano_bytes><sha256>7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc</sha256><referencia><tipo>entrega</tipo><id>302</id></referencia><subido_por>7</subido_por><creado_en>2026-11-26T15:22:52-06:00</creado_en><ruta>documentos/2026/11/6b08a32c5ea8dba9ecdb0af9.jpg</ruta><privacidad>privado</privacidad><estado>activo</estado><metadatos><almacen>local</almacen><origen>api</origen></metadatos></documento>
```

### DOC-08 · Contenido en Base64 · PASA

**Objetivo.** Recuperar el archivo.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b08a32c5ea8dba9ecdb0af9/contenido`

```http
Accept: application/json
X-Traza-Id: 5d51eb6f-7d3d-45ca-8937-7ef422dd1600
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 11 ms · traza `5d51eb6f-7d3d-45ca-8937-7ef422dd1600`

```json
{
  "id": "6b08a32c5ea8dba9ecdb0af9",
  "nombre": "evidencia-entrega-302.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "302"
  },
  "subido_por": 7,
  "creado_en": "2026-11-26T15:22:52-06:00",
  "ruta": "documentos/2026/11/6b08a32c5ea8dba9ecdb0af9.jpg",
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

**Petición.** `DELETE http://documentos:5107/api/v1/documentos/6b08a32df59f7f9d08b26dd4`

```http
Accept: application/json
X-Traza-Id: d015bbac-5f33-4e0f-8462-5c3e0dec7c1f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 73 ms · traza `d015bbac-5f33-4e0f-8462-5c3e0dec7c1f`

```json
(sin cuerpo)
```

**Evidencia en MongoDB.** `db.documentos.countDocuments({_id: ObjectId('6b08a32df59f7f9d08b26dd4')})`

```json
1
```

### DOC-10 · Id inexistente · PASA

**Objetivo.** Registro que no existe.

**Petición.** `GET http://documentos:5107/api/v1/documentos/ffffffffffffffffffffffff`

```http
Accept: application/json
X-Traza-Id: 2229e281-a671-4a83-b20e-dad10a368652
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 12 ms · traza `2229e281-a671-4a83-b20e-dad10a368652`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "2229e281-a671-4a83-b20e-dad10a368652"
  }
}
```

## Servicio seguimiento · puerto 5110

### SEG-01 · Enviar puntos GPS · PASA

**Objetivo.** Guardar el recorrido del repartidor en MongoDB.

**Petición.** `POST http://seguimiento:5110/api/v1/seguimiento/302/ubicaciones`

```http
Accept: application/json
X-Traza-Id: 847e274a-aff2-4acd-82d2-02140da7fb82
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
      "capturado_en": "2026-11-26T21:16:53+00:00"
    },
    {
      "latitud": 25.7486,
      "longitud": -100.3606,
      "precision_m": 8.0,
      "capturado_en": "2026-11-26T21:18:53+00:00"
    },
    {
      "latitud": 25.7491,
      "longitud": -100.3611,
      "precision_m": 8.5,
      "capturado_en": "2026-11-26T21:20:53+00:00"
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 45 ms · traza `847e274a-aff2-4acd-82d2-02140da7fb82`

```json
{
  "recibidos": 3
}
```

**Evidencia en MongoDB.** `db.ubicaciones_entrega.find({entrega_id: NumberLong(302)}).sort({capturado_en: 1})`

```json
[
  {
    "entrega_id": 302,
    "usuario_id": 7,
    "posicion": {
      "type": "Point",
      "coordinates": [
        -100.36,
        25.748
      ]
    },
    "precision_m": 9.0,
    "capturado_en": "2026-11-26 21:16:53+00:00",
    "recibido_en": "2026-11-26 21:22:53.306000+00:00"
  },
  {
    "entrega_id": 302,
    "usuario_id": 7,
    "posicion": {
      "type": "Point",
      "coordinates": [
        -100.3606,
        25.7486
      ]
    },
    "precision_m": 8.0,
    "capturado_en": "2026-11-26 21:18:53+00:00",
    "recibido_en": "2026-11-26 21:22:53.306000+00:00"
  },
  {
    "entrega_id": 302,
    "usuario_id": 7,
    "posicion": {
      "type": "Point",
      "coordinates": [
        -100.3611,
        25.7491
      ]
    },
    "precision_m": 8.5,
    "capturado_en": "2026-11-26 21:20:53+00:00",
    "recibido_en": "2026-11-26 21:22:53.306000+00:00"
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

**Petición.** `GET http://seguimiento:5110/api/v1/seguimiento/302/recorrido`

```http
Accept: application/json
X-Traza-Id: f24720a8-51a7-425c-9dce-ffe1353d0dd5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 53 ms · traza `f24720a8-51a7-425c-9dce-ffe1353d0dd5`

```json
{
  "entrega_id": 302,
  "puntos": 3,
  "distancia_km": 0.16,
  "inicio": "2026-11-26T15:16:53-06:00",
  "fin": "2026-11-26T15:20:53-06:00",
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

**Petición.** `GET http://seguimiento:5110/api/v1/seguimiento/302/recorrido`

```http
Accept: application/json
X-Traza-Id: 775963cd-d6e2-4c64-92e1-0b80afe8bb02
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4Iiwi…(296 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 55 ms · traza `775963cd-d6e2-4c64-92e1-0b80afe8bb02`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe la entrega o no está asignada a ti.",
    "traza_id": "775963cd-d6e2-4c64-92e1-0b80afe8bb02"
  }
}
```

### SEG-04 · Recorrido sin token · PASA

**Objetivo.** Todo endpoint protegido exige Authorization: Bearer.

**Petición.** `GET http://seguimiento:5110/api/v1/seguimiento/302/recorrido`

```http
Accept: application/json
X-Traza-Id: 95058d41-4259-4d8e-8c1c-7fd61e2f5fe6
```

**Respuesta.** HTTP 401 (esperado 401) · 8 ms · traza `95058d41-4259-4d8e-8c1c-7fd61e2f5fe6`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "Falta el encabezado Authorization: Bearer <token>.",
    "traza_id": "95058d41-4259-4d8e-8c1c-7fd61e2f5fe6"
  }
}
```

## Servicio entregas · puerto 5105

### ENT-01 · Mis entregas · PASA

**Objetivo.** Paradas abiertas del repartidor en el turno de hoy (RN25).

**Petición.** `GET http://entregas:5105/api/v1/entregas/mias?pagina=1&por_pagina=20`

```http
Accept: application/json
X-Traza-Id: 35465c29-8cd2-4b21-9f6f-eaef434f4f66
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 76 ms · traza `35465c29-8cd2-4b21-9f6f-eaef434f4f66`

```json
{
  "datos": [
    {
      "id": 302,
      "pedido_id": 589,
      "folio": "PED-20261126-000589",
      "estado_pedido": "en_ruta",
      "orden_parada": 1,
      "direccion": "Rodrigo Gómez 1934, Paseo de San Bernabé",
      "zona": "Paseo de San Bernabé",
      "distancia_km": 1.35,
      "minutos_estimados": 10.0,
      "total": 250.0
    },
    {
      "id": 303,
      "pedido_id": 590,
      "folio": "PED-20261126-000590",
      "estado_pedido": "en_ruta",
      "orden_parada": 2,
      "direccion": "Fresno 3177, Valles de San Bernabé",
      "zona": "Valles de San Bernabé",
      "distancia_km": 0.4,
      "minutos_estimados": 16.0,
      "total": 156.0
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

**Petición.** `GET http://entregas:5105/api/v1/entregas/302`

```http
Accept: application/json
X-Traza-Id: dd9015af-d34d-44d6-b724-9c46b3ef3cfc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 97 ms · traza `dd9015af-d34d-44d6-b724-9c46b3ef3cfc`

```json
{
  "id": 302,
  "pedido_id": 589,
  "folio": "PED-20261126-000589",
  "estado_pedido": "en_ruta",
  "cliente": {
    "nombre": "Yolanda Ibarra Ramos",
    "telefono": "8163881461"
  },
  "domicilio": {
    "calle": "Rodrigo Gómez",
    "numero_ext": "1934",
    "colonia": "Paseo de San Bernabé",
    "latitud": 25.756459,
    "longitud": -100.373581
  },
  "orden_parada": 1,
  "distancia_km": 1.35,
  "minutos_estimados": 10.0,
  "total": 250.0,
  "lineas": [
    {
      "pedido_detalle_id": 1532,
      "nombre": "Yogur natural",
      "cantidad": 2
    },
    {
      "pedido_detalle_id": 1533,
      "nombre": "Queso Oaxaca",
      "cantidad": 2
    }
  ]
}
```

### ENT-03 · Entrega de otro repartidor · PASA

**Objetivo.** El repartidor 2 no ve la entrega del repartidor 1.

**Petición.** `GET http://entregas:5105/api/v1/entregas/302`

```http
Accept: application/json
X-Traza-Id: b004318f-ceb1-4191-9ed1-313b8a252d94
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4Iiwi…(296 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 58 ms · traza `b004318f-ceb1-4191-9ed1-313b8a252d94`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe la entrega o no está asignada a ti.",
    "traza_id": "b004318f-ceb1-4191-9ed1-313b8a252d94"
  }
}
```

### ENT-04 · Monto incorrecto (regla de negocio) · PASA

**Objetivo.** Una entrega completa cobra el total (RN27).

**Petición.** `POST http://entregas:5105/api/v1/entregas/302/resultado`

```http
Accept: application/json
X-Traza-Id: c24bc036-b6c3-457a-b66a-51de20261bab
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
    "6b08a32c5ea8dba9ecdb0af9"
  ],
  "capturado_en": "2026-11-26T21:22:53+00:00",
  "id_cliente_local": "615e1301-2782-4ebb-b526-5bf798e4c049"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 109 ms · traza `c24bc036-b6c3-457a-b66a-51de20261bab`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "monto_cobrado",
        "mensaje": "Una entrega completa cobra el total del pedido (250.00)."
      }
    ],
    "traza_id": "c24bc036-b6c3-457a-b66a-51de20261bab"
  }
}
```

### ENT-05 · Cerrar entrega como entregado · PASA

**Objetivo.** Registrar el resultado con evidencia y ubicación.

**Petición.** `POST http://entregas:5105/api/v1/entregas/302/resultado`

```http
Accept: application/json
X-Traza-Id: bc07a56c-adef-4d62-90ba-05c21821e461
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 250.0,
  "cambio_entregado": 0.0,
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611,
    "precision_m": 8.5
  },
  "evidencia_ids": [
    "6b08a32c5ea8dba9ecdb0af9"
  ],
  "capturado_en": "2026-11-26T21:22:53+00:00",
  "id_cliente_local": "615e1301-2782-4ebb-b526-5bf798e4c049"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 131 ms · traza `bc07a56c-adef-4d62-90ba-05c21821e461`

```json
{
  "entrega_id": 302,
  "pedido_id": 589,
  "estado_pedido": "entregado",
  "cerrado_en": "2026-11-26T15:22:53-06:00",
  "duplicado": false
}
```

**Explicación.** Una sola transacción: cierra la entrega, cambia el pedido (el trigger valida la transición y escribe historial y bitácora) y el trigger de cierre avisa al cliente. La operación se registra en MongoDB.

**Evidencia en PostgreSQL.** `SELECT id, cierre_en, resultado, monto_cobrado, id_cliente_local, evidencia_ids, cierre_latitud, cierre_longitud FROM entrega WHERE id = %s`

```json
[
  {
    "id": 302,
    "cierre_en": "2026-11-26 15:22:53.958618-06:00",
    "resultado": "entregado",
    "monto_cobrado": "250.00",
    "id_cliente_local": "615e1301-2782-4ebb-b526-5bf798e4c049",
    "evidencia_ids": [
      "6b08a32c5ea8dba9ecdb0af9"
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
    "fecha": "2026-11-26 15:22:53.958618-06:00"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT destinatario_id, tipo, titulo, mensaje, referencia_tipo, referencia_id FROM web_notificacion WHERE referencia_tipo = 'pedido' AND referencia_id = %s ORDER BY id DESC LIMIT 1`

```json
[
  {
    "destinatario_id": 24,
    "tipo": "pedido",
    "titulo": "Pedido PED-20261126-000589",
    "mensaje": "El pedido cambió a entregado.",
    "referencia_tipo": "pedido",
    "referencia_id": "589"
  }
]
```

**Evidencia en MongoDB.** `db.sincronizaciones_moviles.findOne({operacion_uuid: '615e1301-2782-4ebb-b526-5bf798e4c049'})`

```json
{
  "operacion_uuid": "615e1301-2782-4ebb-b526-5bf798e4c049",
  "capturado_en": "2026-11-26 21:22:53+00:00",
  "carga": {
    "entrega_id": 302,
    "resultado": "entregado",
    "monto_cobrado": 250.0,
    "evidencia_ids": [
      "6b08a32c5ea8dba9ecdb0af9"
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
  "pedido_id": 589,
  "sincronizado_en": "2026-11-26 21:22:54.016000+00:00",
  "tipo_operacion": "cierre_entrega",
  "usuario_id": 7
}
```

### ENT-06 · Reintento con el mismo UUID · PASA

**Objetivo.** Idempotencia: el cierre no se aplica dos veces.

**Petición.** `POST http://entregas:5105/api/v1/entregas/302/resultado`

```http
Accept: application/json
X-Traza-Id: ca34c661-2dfb-4420-bead-64b1c3c44920
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 250.0,
  "cambio_entregado": 0.0,
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611,
    "precision_m": 8.5
  },
  "evidencia_ids": [
    "6b08a32c5ea8dba9ecdb0af9"
  ],
  "capturado_en": "2026-11-26T21:22:53+00:00",
  "id_cliente_local": "615e1301-2782-4ebb-b526-5bf798e4c049"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 76 ms · traza `ca34c661-2dfb-4420-bead-64b1c3c44920`

```json
{
  "entrega_id": 302,
  "pedido_id": 589,
  "estado_pedido": "entregado",
  "cerrado_en": "2026-11-26T15:22:53-06:00",
  "duplicado": true
}
```

**Explicación.** La respuesta es la misma con duplicado=true. MongoDB actualiza el documento de la operación (intentos = 2).

**Evidencia en MongoDB.** `db.sincronizaciones_moviles.findOne({operacion_uuid: '615e1301-2782-4ebb-b526-5bf798e4c049'}, {estado: 1, intentos: 1})`

```json
{
  "estado": "aplicada",
  "intentos": 2,
  "sincronizado_en": "2026-11-26 21:22:54.174000+00:00"
}
```

### ENT-07 · Otro cierre sobre la misma entrega · PASA

**Objetivo.** Conflicto: ya estaba cerrada con otra operación.

**Petición.** `POST http://entregas:5105/api/v1/entregas/302/resultado`

```http
Accept: application/json
X-Traza-Id: 24785495-9f99-48d9-a428-a9190284c1e1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 250.0,
  "cambio_entregado": 0.0,
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611,
    "precision_m": 8.5
  },
  "evidencia_ids": [
    "6b08a32c5ea8dba9ecdb0af9"
  ],
  "capturado_en": "2026-11-26T21:22:53+00:00",
  "id_cliente_local": "22fb92db-85d4-456e-aaa3-57bf1bef83ac"
}
```

**Respuesta.** HTTP 409 (esperado 409) · 77 ms · traza `24785495-9f99-48d9-a428-a9190284c1e1`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "La entrega ya se cerró con otra operación.",
    "traza_id": "24785495-9f99-48d9-a428-a9190284c1e1"
  }
}
```

### ENT-08 · Detalle tras el cierre · PASA

**Objetivo.** El repartidor deja de ver el domicilio (RN26).

**Petición.** `GET http://entregas:5105/api/v1/entregas/302`

```http
Accept: application/json
X-Traza-Id: 49281ffb-a659-4534-bc65-64d3434f6fba
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 39 ms · traza `49281ffb-a659-4534-bc65-64d3434f6fba`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "La entrega ya se cerró; su información ya no está disponible.",
    "traza_id": "49281ffb-a659-4534-bc65-64d3434f6fba"
  }
}
```

### ENT-09 · Parcial sin motivo · PASA

**Objetivo.** Cada línea devuelta necesita motivo (RN28).

**Petición.** `POST http://entregas:5105/api/v1/entregas/303/resultado`

```http
Accept: application/json
X-Traza-Id: 6eec85d7-84fa-48a4-928b-4fdcdf57e98b
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
      "pedido_detalle_id": 1534,
      "cantidad_entregada": 3,
      "cantidad_devuelta": 0
    },
    {
      "pedido_detalle_id": 1535,
      "cantidad_entregada": 0,
      "cantidad_devuelta": 3
    }
  ],
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611
  },
  "evidencia_ids": [
    "6b08a32c5ea8dba9ecdb0afc"
  ],
  "capturado_en": "2026-11-26T21:22:53+00:00",
  "id_cliente_local": "7abc5932-4aa9-4e7f-a424-ab7e7abad130"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 83 ms · traza `6eec85d7-84fa-48a4-928b-4fdcdf57e98b`

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
    "traza_id": "6eec85d7-84fa-48a4-928b-4fdcdf57e98b"
  }
}
```

### ENT-10 · Cerrar como entrega parcial · PASA

**Objetivo.** Devolver al inventario lo que no se entregó.

**Petición.** `POST http://entregas:5105/api/v1/entregas/303/resultado`

```http
Accept: application/json
X-Traza-Id: 96c604d3-af41-4c3e-8a22-5d3329a1cae8
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
      "pedido_detalle_id": 1534,
      "cantidad_entregada": 3,
      "cantidad_devuelta": 0
    },
    {
      "pedido_detalle_id": 1535,
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
    "6b08a32c5ea8dba9ecdb0afc"
  ],
  "capturado_en": "2026-11-26T21:22:53+00:00",
  "id_cliente_local": "7abc5932-4aa9-4e7f-a424-ab7e7abad130"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 177 ms · traza `96c604d3-af41-4c3e-8a22-5d3329a1cae8`

```json
{
  "entrega_id": 303,
  "pedido_id": 590,
  "estado_pedido": "entrega_parcial",
  "cerrado_en": "2026-11-26T15:22:54-06:00",
  "duplicado": false
}
```

**Explicación.** fn_devolver_inventario (la misma función que usa el web) regresa las unidades devueltas.

**Evidencia en PostgreSQL.** `SELECT entrega_id, pedido_detalle_id, cantidad_entregada, cantidad_devuelta, motivo FROM entrega_linea WHERE entrega_id = %s`

```json
[
  {
    "entrega_id": 303,
    "pedido_detalle_id": 1534,
    "cantidad_entregada": 3,
    "cantidad_devuelta": 0,
    "motivo": null
  },
  {
    "entrega_id": 303,
    "pedido_detalle_id": 1535,
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
    "producto_id": 26,
    "cantidad": 3,
    "existencia_resultante": 17,
    "motivo": "Entrega parcial: regresan las unidades devueltas (RN28)."
  }
]
```

### ENT-11 · Entregas de un pedido (administrador) · PASA

**Objetivo.** Consulta por pedido para el portal web.

**Petición.** `GET http://entregas:5105/api/v1/entregas?pedido_id=589`

```http
Accept: application/json
X-Traza-Id: ce25514c-f64e-4ae7-a041-53a3cd8eb59d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 58 ms · traza `ce25514c-f64e-4ae7-a041-53a3cd8eb59d`

```json
{
  "datos": [
    {
      "id": 302,
      "pedido_id": 589,
      "folio": "PED-20261126-000589",
      "estado_pedido": "entregado",
      "orden_parada": 1,
      "direccion": "Rodrigo Gómez 1934, Paseo de San Bernabé",
      "zona": "Paseo de San Bernabé",
      "distancia_km": 1.35,
      "minutos_estimados": 10.0,
      "total": 250.0
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
X-Traza-Id: 1bfd8565-6c29-45fa-87ad-f82373c82b9d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 68 ms · traza `1bfd8565-6c29-45fa-87ad-f82373c82b9d`

```xml
<?xml version='1.0' encoding='utf-8'?>
<candidatos xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><datos><candidato><id>1</id><clave>CAND-01</clave><nombre>San Bernabé Norte</nombre><latitud>25.752</latitud><longitud>-100.361</longitud><renta_estimada>18000.00</renta_estimada><nomina_estimada>42000.00</nomina_estimada><servicios_estimados>7000.00</servicios_estimados><otros_costos>5000.00</otros_costos><costo_fijo>72000.00</costo_fijo><superficie_m2>130</superficie_m2><capacidad_fisica>150</capacidad_fisica><accesibilidad_vial>9</accesibilidad_vial><zona_id>1</zona_id><poblacion_cubierta>8420</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato><candidato><id>2</id><clave>CAND-02</clave><nombre>Valles Poniente</nombre><latitud>25.7555</latitud><longitud>-100.376</longitud><renta_estimada>15500.00</renta_estimada><nomina_estimada>42000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><costo_fijo>68500.00</costo_fijo><superficie_m2>105</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>2</zona_id><poblacion_cubierta>6180</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato><candidato><id>3</id><clave>CAND-05</clave><nombre>Alianza Real</nombre><latitud>25.7625</latitud><longitud>-100.353</longitud><renta_estimada>21000.00</renta_estimada><nomina_estimada>46000.00</nomina_estimada><servicios_estimados>8000.00</servicios_estimados><otros_costos>6000.00</otros_costos><costo_fijo>81000.00</costo_fijo><superficie_m2>150</superficie_m2><capacidad_fisica>180</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>3900</poblacion_cubierta><radio_km>1.6</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>20</total><paginas>7</paginas></paginacion></candidatos>
```

### PLA-02 · Registrar candidato (XML) · PASA

**Objetivo.** Alta con costo fijo calculado por PostgreSQL.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos`

```http
Accept: application/xml
X-Traza-Id: 9d19c232-fe7a-45b4-9e67-694148892491
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><candidato_nuevo xmlns="urn:microhubs:v1"><clave>********</clave><nombre>Alianza Norte</nombre><latitud>25.7601</latitud><longitud>-100.3555</longitud><renta_estimada>16000.00</renta_estimada><nomina_estimada>40000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><superficie_m2>110</superficie_m2><capacidad_fisica>130</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km></candidato_nuevo>
```

**Respuesta.** HTTP 201 (esperado 201) · 87 ms · traza `9d19c232-fe7a-45b4-9e67-694148892491`

```xml
<?xml version='1.0' encoding='utf-8'?>
<candidato xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>162</id><clave>EV-B7C8E6</clave><nombre>Alianza Norte</nombre><latitud>25.7601</latitud><longitud>-100.3555</longitud><renta_estimada>16000.00</renta_estimada><nomina_estimada>40000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><costo_fijo>67000.00</costo_fijo><superficie_m2>110</superficie_m2><capacidad_fisica>130</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato>
```

**Evidencia en PostgreSQL.** `SELECT id, clave, nombre, renta_estimada, costo_fijo, decision FROM ubicacion_candidata WHERE clave = %s`

```json
[
  {
    "id": 162,
    "clave": "EV-B7C8E6",
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
X-Traza-Id: 0217a682-1312-4e27-bb62-b41916f435a8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><candidato_nuevo xmlns="urn:microhubs:v1"><clave>********</clave><nombre>Alianza Norte</nombre><latitud>25.7601</latitud><longitud>-100.3555</longitud><renta_estimada>16000.00</renta_estimada><nomina_estimada>40000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><superficie_m2>110</superficie_m2><capacidad_fisica>130</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km></candidato_nuevo>
```

**Respuesta.** HTTP 409 (esperado 409) · 62 ms · traza `0217a682-1312-4e27-bb62-b41916f435a8`

```xml
<?xml version='1.0' encoding='utf-8'?>
<error xmlns="urn:microhubs:v1" version="1"><codigo>CONFLICTO</codigo><mensaje>Ya existe un registro con esos datos.</mensaje><traza_id>0217a682-1312-4e27-bb62-b41916f435a8</traza_id></error>
```

### PLA-04 · Modificar candidato (PUT) · PASA

**Objetivo.** Cambiar la renta recalcula el costo fijo.

**Petición.** `PUT http://planeacion:5106/api/v1/candidatos/162`

```http
Accept: application/json
X-Traza-Id: 8498314e-6d12-472e-84e0-d25798097a0a
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

**Respuesta.** HTTP 200 (esperado 200) · 91 ms · traza `8498314e-6d12-472e-84e0-d25798097a0a`

```json
{
  "id": 162,
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

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/162/simular`

```http
Accept: application/xml
X-Traza-Id: 2402eacb-69c7-4daa-a2cf-a7ede1529223
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<simular xmlns="urn:microhubs:v1"/>
```

**Respuesta.** HTTP 200 (esperado 200) · 376 ms · traza `2402eacb-69c7-4daa-a2cf-a7ede1529223`

```xml
<?xml version='1.0' encoding='utf-8'?>
<resultados xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><atendidos>0</atendidos><rechazados>0</rechazados><utilizacion>0</utilizacion><nivel>estable</nivel><tiempo_estimado_min>18.6</tiempo_estimado_min><operadores_requeridos>0</operadores_requeridos><repartidores_requeridos>0</repartidores_requeridos><ingreso_dia>0.00</ingreso_dia><margen_dia>-2300.00</margen_dia><costo_por_pedido xsi:nil="true" /><equilibrio><margen_pedido>24.79</margen_pedido><mensual>2783.4</mensual><diario>92.8</diario></equilibrio><decision>NO VIABLE CON LOS SUPUESTOS ACTUALES</decision><explicacion><motivo>la demanda atendida (0/día) no alcanza el equilibrio (93/día)</motivo><motivo>reducir costos fijos, aumentar ticket o buscar una ubicación con más demanda</motivo></explicacion></resultados>
```

**Explicación.** Usa planeacion_calc.py (las mismas fórmulas del web) y guarda la ejecución en MongoDB.

**Evidencia en MongoDB.** `db.ejecuciones_analiticas.find().sort({ejecutado_en: -1}).limit(1)`

```json
{
  "escenario_id": "candidato-162",
  "nombre_escenario": "Candidato 162",
  "tipo_analisis": "punto_equilibrio",
  "ejecutado_en": "2026-11-26 21:22:55.365000+00:00",
  "usuario_id": 5,
  "version_modelo": "planeacion_calc 2.1",
  "parametros_entrada": {
    "demanda_diaria": 0.0,
    "operadores": 3.0,
    "repartidores": 3.0,
    "ticket": 152.82,
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
    "ticket = 152.82",
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
    "equilibrio_diario": 92.8,
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

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/162/decision`

```http
Accept: application/json
X-Traza-Id: 56af80b5-b336-4b97-93da-772de7794105
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aceptado",
  "motivo": "ok"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 40 ms · traza `56af80b5-b336-4b97-93da-772de7794105`

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
    "traza_id": "56af80b5-b336-4b97-93da-772de7794105"
  }
}
```

### PLA-07 · Decisión humana de apertura · PASA

**Objetivo.** Registrar la decisión con motivo.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/162/decision`

```http
Accept: application/json
X-Traza-Id: 995af369-e989-4a4a-ac7b-b35cb57a6fdb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "condicionado",
  "motivo": "Renegociar la renta antes de firmar."
}
```

**Respuesta.** HTTP 200 (esperado 200) · 88 ms · traza `995af369-e989-4a4a-ac7b-b35cb57a6fdb`

```json
{
  "id": 162,
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
    "id": 162,
    "decision": "condicionado",
    "decision_motivo": "Renegociar la renta antes de firmar.",
    "decision_por": 5,
    "decision_en": "2026-11-26 15:22:55.470994-06:00"
  }
]
```

### PLA-08 · Simulación libre: Escenario A · PASA

**Objetivo.** Punto de equilibrio del caso de la retroalimentación.

**Petición.** `POST http://planeacion:5106/api/v1/simulaciones`

```http
Accept: application/json
X-Traza-Id: dc8642c2-6bda-4f7d-a4f6-42d3746022a8
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

**Respuesta.** HTTP 200 (esperado 200) · 50 ms · traza `dc8642c2-6bda-4f7d-a4f6-42d3746022a8`

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
X-Traza-Id: 3b94e5f3-08dc-43dd-af35-4335ad3d089d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Escenario A - evidencias",
  "candidato_id": 162,
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

**Respuesta.** HTTP 201 (esperado 201) · 121 ms · traza `3b94e5f3-08dc-43dd-af35-4335ad3d089d`

```json
{
  "id": 28,
  "nombre": "Escenario A - evidencias",
  "candidato_id": 162,
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
  "creado_en": "2026-11-26T15:22:55-06:00"
}
```

### PLA-10 · Abrir escenario (XML) · PASA

**Objetivo.** Escenario con supuestos y resultados.

**Petición.** `GET http://planeacion:5106/api/v1/escenarios/28`

```http
Accept: application/xml
X-Traza-Id: b22c3948-7407-4b0a-9d37-b54eb3f8889d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 63 ms · traza `b22c3948-7407-4b0a-9d37-b54eb3f8889d`

```xml
<?xml version='1.0' encoding='utf-8'?>
<escenario xmlns="urn:microhubs:v1" version="1"><id>28</id><nombre>Escenario A - evidencias</nombre><candidato_id>162</candidato_id><supuestos><demanda_diaria>120</demanda_diaria><operadores>3</operadores><repartidores>4</repartidores><ticket>135.00</ticket><costo_entrega>22.00</costo_entrega><margen_bruto>0.28</margen_bruto><renta>18000.00</renta><nomina>42000.00</nomina><servicios>7000.00</servicios><otros>5000.00</otros><distancia_km>2.4</distancia_km><capacidad_fisica>150</capacidad_fisica></supuestos><resultados><atendidos>120</atendidos><rechazados>0</rechazados><utilizacion>80</utilizacion><nivel>atencion</nivel><tiempo_estimado_min>19.4</tiempo_estimado_min><operadores_requeridos>3</operadores_requeridos><repartidores_requeridos>2</repartidores_requeridos><ingreso_dia>16200.00</ingreso_dia><margen_dia>-504.00</margen_dia><costo_por_pedido>42.00</costo_por_pedido><equilibrio><margen_pedido>15.80</margen_pedido><mensual>4557</mensual><diario>151.9</diario></equilibrio><decision>NO VIABLE CON LOS SUPUESTOS ACTUALES</decision><explicacion><motivo>la demanda atendida (120/día) no alcanza el equilibrio (152/día)</motivo><motivo>el espacio físico del local limita la capacidad</motivo><motivo>reducir costos fijos, aumentar ticket o buscar una ubicación con más demanda</motivo></explicacion></resultados><creado_en>2026-11-26T15:22:55-06:00</creado_en></escenario>
```

### PLA-11 · Resumen de simulaciones · PASA

**Objetivo.** Agregación $group en MongoDB por decisión.

**Petición.** `GET http://planeacion:5106/api/v1/simulaciones/resumen`

```http
Accept: application/json
X-Traza-Id: 3f545ee5-7267-4312-8879-65b0514bd115
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 38 ms · traza `3f545ee5-7267-4312-8879-65b0514bd115`

```json
{
  "total": 76,
  "por_decision": [
    {
      "decision": "NO VIABLE CON LOS SUPUESTOS ACTUALES",
      "cantidad": 75,
      "utilizacion_promedio": 54.4
    },
    {
      "decision": "VIABLE",
      "cantidad": 1,
      "utilizacion_promedio": 83.3
    }
  ]
}
```

**Evidencia en MongoDB.** `db.ejecuciones_analiticas.aggregate([{$match:{tipo_analisis:'punto_equilibrio'}}, {$group:{_id:'$resultados.decision', cantidad:{$sum:1}, utilizacion_promedio:{$avg:'$resultados.utilizacion'}}}])`

```json
[
  {
    "_id": "VIABLE",
    "cantidad": 1,
    "utilizacion_promedio": 83.3
  },
  {
    "_id": "NO VIABLE CON LOS SUPUESTOS ACTUALES",
    "cantidad": 75,
    "utilizacion_promedio": 54.446666666666665
  }
]
```

### PLA-12 · Auditor intenta registrar · PASA

**Objetivo.** El auditor solo consulta (RN-E01).

**Petición.** `POST http://planeacion:5106/api/v1/candidatos`

```http
Accept: application/json
X-Traza-Id: 795fd40e-6bc0-4985-aaa7-4cc9e9113100
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

**Respuesta.** HTTP 403 (esperado 403) · 40 ms · traza `795fd40e-6bc0-4985-aaa7-4cc9e9113100`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "795fd40e-6bc0-4985-aaa7-4cc9e9113100"
  }
}
```

### PLA-13 · Auditor intenta simular · PASA

**Objetivo.** Sin simulacion.ejecutar.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/162/simular`

```http
Accept: application/json
X-Traza-Id: 0ab9f653-52d1-4e70-9c9f-f659f7f7a795
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 403 (esperado 403) · 100 ms · traza `0ab9f653-52d1-4e70-9c9f-f659f7f7a795`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "0ab9f653-52d1-4e70-9c9f-f659f7f7a795"
  }
}
```

### PLA-14 · Eliminar escenario (DELETE) · PASA

**Objetivo.** Borrar un escenario.

**Petición.** `DELETE http://planeacion:5106/api/v1/escenarios/28`

```http
Accept: application/json
X-Traza-Id: 1fe6c027-440d-49b4-b2d6-b3033088aef8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 70 ms · traza `1fe6c027-440d-49b4-b2d6-b3033088aef8`

```json
(sin cuerpo)
```

### PLA-15 · Dar de baja candidato (DELETE) · PASA

**Objetivo.** Baja lógica: se conserva su historia.

**Petición.** `DELETE http://planeacion:5106/api/v1/candidatos/162`

```http
Accept: application/json
X-Traza-Id: 63a17635-efce-4101-ba7f-e41ea8bb4179
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 118 ms · traza `63a17635-efce-4101-ba7f-e41ea8bb4179`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT id, clave, estatus, decision FROM ubicacion_candidata WHERE id = %s`

```json
[
  {
    "id": 162,
    "clave": "EV-B7C8E6",
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
X-Traza-Id: e0fd2ee5-89a7-4879-9ad7-47e5a36cbc91
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 44 ms · traza `e0fd2ee5-89a7-4879-9ad7-47e5a36cbc91`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el candidato.",
    "traza_id": "e0fd2ee5-89a7-4879-9ad7-47e5a36cbc91"
  }
}
```

## Servicio inventario · puerto 5111

### INV-01 · Existencias por microhub · PASA

**Objetivo.** Existencia física, reservada y disponible de cada producto.

**Petición.** `GET http://inventario:5111/api/v1/inventario?por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 1bb90132-d0d3-47b7-82f8-0b6b74d12b11
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 89 ms · traza `1bb90132-d0d3-47b7-82f8-0b6b74d12b11`

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
      "actualizado_en": "2026-11-26T14:26:53-06:00"
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
    "total": 157,
    "paginas": 32
  }
}
```

**Explicación.** Lee la vista v_inventario_disponible (existencia − reservas activas y vigentes). Los nombres de producto y microhub los pide a los servicios de productos y microhubs, no los lee de sus tablas.

**Evidencia en PostgreSQL.** `SELECT count(*) AS filas, sum(existencia) AS unidades, sum(reservado) AS reservado FROM v_inventario_disponible`

```json
[
  {
    "filas": 157,
    "unidades": 7742,
    "reservado": 0
  }
]
```

### INV-02 · Existencias (XML) · PASA

**Objetivo.** La app de escritorio recibe XML que cumple inventario.xsd.

**Petición.** `GET http://inventario:5111/api/v1/inventario?por_pagina=3`

```http
Accept: application/xml
X-Traza-Id: 58cd5223-27ee-4028-94e0-cdcaeb750fdf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 118 ms · traza `58cd5223-27ee-4028-94e0-cdcaeb750fdf`

```xml
<?xml version='1.0' encoding='utf-8'?>
<existencias xmlns="urn:microhubs:v1" version="1"><datos><existencia><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><producto><id>1</id><clave_interna>AB-001</clave_interna><nombre>Frijol negro a granel</nombre></producto><existencia>58</existencia><minimo>10</minimo><reservado>0</reservado><disponible>58</disponible><estado>normal</estado><actualizado_en>2026-11-25T15:47:14-06:00</actualizado_en></existencia><existencia><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><producto><id>2</id><clave_interna>AB-002</clave_interna><nombre>Arroz superextra</nombre></producto><existencia>36</existencia><minimo>10</minimo><reservado>0</reservado><disponible>36</disponible><estado>normal</estado><actualizado_en>2026-11-26T14:26:53-06:00</actualizado_en></existencia><existencia><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><producto><id>3</id><clave_interna>AB-003</clave_interna><nombre>Aceite vegetal</nombre></producto><existencia>10</existencia><minimo>5</minimo><reservado>0</reservado><disponible>10</disponible><estado>normal</estado><actualizado_en>2026-11-26T13:51:58-06:00</actualizado_en></existencia></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>157</total><paginas>53</paginas></paginacion></existencias>
```

### INV-03 · Filtro de estado inválido · PASA

**Objetivo.** Un filtro desconocido se rechaza.

**Petición.** `GET http://inventario:5111/api/v1/inventario?estado=inventado`

```http
Accept: application/json
X-Traza-Id: ea963386-639d-4340-bb6f-226f205948a4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 13 ms · traza `ea963386-639d-4340-bb6f-226f205948a4`

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
    "traza_id": "ea963386-639d-4340-bb6f-226f205948a4"
  }
}
```

### INV-04 · El operador ve solo su microhub · PASA

**Objetivo.** Ámbito por microhub del perfil operador.

**Petición.** `GET http://inventario:5111/api/v1/inventario?por_pagina=100`

```http
Accept: application/json
X-Traza-Id: 303f18be-6cbf-423e-b377-0666beb9320f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 89 ms · traza `303f18be-6cbf-423e-b377-0666beb9320f`

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
      "actualizado_en": "2026-11-26T14:26:53-06:00"
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
      "existencia": 86,
      "minimo": 10,
      "reservado": 0,
      "disponible": 86,
      "estado": "normal",
      "actualizado_en": "2026-11-26T14:21:55-06:00"
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
      "actualizado_en": "2026-11-26T14:25:47-06:00"
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
      "actualizado_en": "2026-11-26T14:26:32-06:00"
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
      "actualizado_en": "2026-11-26T14:25:47-06:00"
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
      "existencia": 736,
      "minimo": 10,
      "reservado": 0,
      "disponible": 736,
      "estado": "normal",
      "actualizado_en": "2026-11-26T14:22:17-06:00"
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
      "existencia": 455,
      "minimo": 8,
      "reservado": 0,
      "disponible": 455,
      "estado": "normal",
      "actualizado_en": "2026-11-26T14:22:20-06:00"
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
      "actualizado_en": "2026-11-26T14:20:03-06:00"
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
      "actualizado_en": "2026-11-26T14:22:19-06:00"
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
      "actualizado_en": "2026-11-26T14:20:03-06:00"
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
      "existencia": 78,
      "minimo": 8,
      "reservado": 0,
      "disponible": 78,
      "estado": "normal",
      "actualizado_en": "2026-11-26T15:15:01-06:00"
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
      "actualizado_en": "2026-11-26T14:25:47-06:00"
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
      "existencia": 69,
      "minimo": 8,
      "reservado": 0,
      "disponible": 69,
      "estado": "normal",
      "actualizado_en": "2026-11-26T15:22:45-06:00"
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
      "actualizado_en": "2026-11-26T14:25:47-06:00"
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
      "actualizado_en": "2026-11-26T15:22:54-06:00"
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
      "actualizado_en": "2026-11-26T14:20:03-06:00"
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
      "actualizado_en": "2026-11-26T14:25:47-06:00"
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
      "existencia": 131,
      "minimo": 5,
      "reservado": 0,
      "disponible": 131,
      "estado": "normal",
      "actualizado_en": "2026-11-26T15:22:05-06:00"
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
      "actualizado_en": "2026-11-26T14:25:47-06:00"
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
      "actualizado_en": "2026-11-26T14:26:53-06:00"
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
      "actualizado_en": "2026-11-26T14:20:03-06:00"
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
      "actualizado_en": "2026-11-26T14:20:03-06:00"
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
      "existencia": 36,
      "minimo": 10,
      "reservado": 0,
      "disponible": 36,
      "estado": "normal",
      "actualizado_en": "2026-11-26T15:21:58-06:00"
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
      "actualizado_en": "2026-11-26T14:26:32-06:00"
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
      "actualizado_en": "2026-11-26T15:21:26-06:00"
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
X-Traza-Id: 1bcc409a-a670-4f18-bd63-71d85fd99420
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 21 ms · traza `1bcc409a-a670-4f18-bd63-71d85fd99420`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "1bcc409a-a670-4f18-bd63-71d85fd99420"
  }
}
```

### INV-06 · Una existencia · PASA

**Objetivo.** Existencia, apartado y disponible de un producto en un microhub.

**Petición.** `GET http://inventario:5111/api/v1/inventario/1/6`

```http
Accept: application/json
X-Traza-Id: 342ca72c-b05f-4744-a685-fa3468314a2b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 60 ms · traza `342ca72c-b05f-4744-a685-fa3468314a2b`

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
  "existencia": 86,
  "minimo": 10,
  "reservado": 0,
  "disponible": 86,
  "estado": "normal",
  "actualizado_en": "2026-11-26T14:21:55-06:00"
}
```

### INV-07 · Recibir mercancía · PASA

**Objetivo.** Suma al inventario y deja el movimiento con la referencia.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: a237515e-70e5-438f-a558-1d19f14b587a
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
  "operacion_uuid": "063758b2-f906-4f1b-ab22-327fa7b5ae3c",
  "referencia": {
    "tipo": "orden_compra",
    "id": "1"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 195 ms · traza `a237515e-70e5-438f-a558-1d19f14b587a`

```json
{
  "movimiento": {
    "id": 2392,
    "microhub_id": 1,
    "producto_id": 6,
    "tipo": "recepcion",
    "cantidad": 5,
    "existencia_resultante": 91,
    "referencia": {
      "tipo": "orden_compra",
      "id": "1"
    },
    "motivo": "Llegada de mercancía",
    "usuario_id": 2,
    "fecha": "2026-11-26T15:23:00-06:00"
  },
  "duplicado": false
}
```

**Explicación.** Bloquea la fila del inventario, suma, y guarda el movimiento con la existencia resultante. La operacion_uuid hace el movimiento idempotente.

**Evidencia en PostgreSQL.** `SELECT id, tipo, cantidad, existencia_resultante, referencia_tipo, referencia_id, operacion_uuid FROM movimiento_inventario WHERE operacion_uuid = %s`

```json
[
  {
    "id": 2392,
    "tipo": "recepcion",
    "cantidad": 5,
    "existencia_resultante": 91,
    "referencia_tipo": "orden_compra",
    "referencia_id": 1,
    "operacion_uuid": "063758b2-f906-4f1b-ab22-327fa7b5ae3c"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT existencia FROM inventario WHERE microhub_id = %s AND producto_id = %s`

```json
[
  {
    "existencia": 91
  }
]
```

### INV-08 · Reintento con la misma operación · PASA

**Objetivo.** Idempotencia: la misma entrada no se aplica dos veces.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: a7c55d0c-0cf7-4d1b-b2ae-6d7ba57239f4
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
  "operacion_uuid": "063758b2-f906-4f1b-ab22-327fa7b5ae3c",
  "referencia": {
    "tipo": "orden_compra",
    "id": "1"
  }
}
```

**Respuesta.** HTTP 200 (esperado 200) · 67 ms · traza `a7c55d0c-0cf7-4d1b-b2ae-6d7ba57239f4`

```json
{
  "movimiento": {
    "id": 2392,
    "microhub_id": 1,
    "producto_id": 6,
    "tipo": "recepcion",
    "cantidad": 5,
    "existencia_resultante": 91,
    "referencia": {
      "tipo": "orden_compra",
      "id": "1"
    },
    "motivo": "Llegada de mercancía",
    "usuario_id": 2,
    "fecha": "2026-11-26T15:23:00-06:00"
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
    "existencia": 91
  }
]
```

### INV-09 · Ajuste sin motivo · PASA

**Objetivo.** Un ajuste, merma o conteo necesita el motivo.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: d933a7be-9b5b-4271-85cd-135c092957d6
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

**Respuesta.** HTTP 422 (esperado 422) · 17 ms · traza `d933a7be-9b5b-4271-85cd-135c092957d6`

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
    "traza_id": "d933a7be-9b5b-4271-85cd-135c092957d6"
  }
}
```

### INV-10 · Ajuste grande por un operador · PASA

**Objetivo.** Más de 25 unidades lo autoriza un administrador.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: ece14f74-81c5-47ae-adf3-ba312863267c
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

**Respuesta.** HTTP 403 (esperado 403) · 109 ms · traza `ece14f74-81c5-47ae-adf3-ba312863267c`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Un movimiento de más de 25 unidades lo autoriza un administrador.",
    "traza_id": "ece14f74-81c5-47ae-adf3-ba312863267c"
  }
}
```

**Explicación.** El umbral viene de configuracion.umbral_ajuste_inventario, no de una constante en el código.

### INV-11 · Ajuste grande por un administrador · PASA

**Objetivo.** El administrador sí puede.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: a91557cf-700a-4a36-8d48-6732973c4f0e
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

**Respuesta.** HTTP 201 (esperado 201) · 94 ms · traza `a91557cf-700a-4a36-8d48-6732973c4f0e`

```json
{
  "movimiento": {
    "id": 2393,
    "microhub_id": 1,
    "producto_id": 6,
    "tipo": "ajuste",
    "cantidad": 30,
    "existencia_resultante": 121,
    "referencia": null,
    "motivo": "Ajuste grande de prueba",
    "usuario_id": 1,
    "fecha": "2026-11-26T15:23:00-06:00"
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
    "existencia_resultante": 121,
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
X-Traza-Id: 5eabf00f-3eae-404e-be60-1b7e10d6983a
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
  "operacion_uuid": "6bf9c079-8fbc-4280-a293-0b2dd8fb89c8"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 100 ms · traza `5eabf00f-3eae-404e-be60-1b7e10d6983a`

```json
{
  "producto_id": 7,
  "cantidad": 2,
  "duplicado": false,
  "origen": {
    "microhub_id": 1,
    "existencia": 12,
    "movimiento_id": 2396
  },
  "destino": {
    "microhub_id": 2,
    "existencia": 78,
    "movimiento_id": 2397
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
X-Traza-Id: b2e31afe-fc5a-47a8-887b-04519ca9a6ee
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
  "operacion_uuid": "7cd84567-f6f5-41d0-b2dd-ad9139b74e08"
}
```

**Respuesta.** HTTP 409 (esperado 409) · 75 ms · traza `b2e31afe-fc5a-47a8-887b-04519ca9a6ee`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "En el microhub de origen hay 12 disponibles y se piden 1014.",
    "traza_id": "b2e31afe-fc5a-47a8-887b-04519ca9a6ee"
  }
}
```

### INV-14 · Apartar existencia · PASA

**Objetivo.** Una reserva resta de lo disponible sin tocar la existencia física.

**Petición.** `POST http://inventario:5111/api/v1/inventario/reservas`

```http
Accept: application/json
X-Traza-Id: 171f3f5c-f890-4272-a38d-33e9825eb427
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
    "id": "evidencia-042caa"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 63 ms · traza `171f3f5c-f890-4272-a38d-33e9825eb427`

```json
{
  "id": 21,
  "microhub_id": 1,
  "producto_id": 8,
  "cantidad": 3,
  "estado": "activa",
  "vigente": true,
  "referencia": {
    "tipo": "manual",
    "id": "evidencia-042caa"
  },
  "creada_en": "2026-11-26T15:23:01-06:00",
  "vence_en": "2026-11-26T15:53:01-06:00",
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
X-Traza-Id: fe96abd8-94a7-423f-9ddf-5419bcbe7184
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
    "id": "evidencia-042caa"
  }
}
```

**Respuesta.** HTTP 409 (esperado 409) · 55 ms · traza `fe96abd8-94a7-423f-9ddf-5419bcbe7184`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "No hay existencia disponible: hay 18 sin apartar y se piden 121.",
    "traza_id": "fe96abd8-94a7-423f-9ddf-5419bcbe7184"
  }
}
```

### INV-16 · Reservas activas · PASA

**Objetivo.** Filtro por producto, estado y referencia.

**Petición.** `GET http://inventario:5111/api/v1/inventario/reservas?producto_id=8&estado=activa&referencia_id=evidencia-042caa`

```http
Accept: application/json
X-Traza-Id: 0b8e1e94-b721-4bf6-8cfa-0c90cf72d142
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 53 ms · traza `0b8e1e94-b721-4bf6-8cfa-0c90cf72d142`

```json
{
  "datos": [
    {
      "id": 21,
      "microhub_id": 1,
      "producto_id": 8,
      "cantidad": 3,
      "estado": "activa",
      "vigente": true,
      "referencia": {
        "tipo": "manual",
        "id": "evidencia-042caa"
      },
      "creada_en": "2026-11-26T15:23:01-06:00",
      "vence_en": "2026-11-26T15:53:01-06:00",
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

**Petición.** `POST http://inventario:5111/api/v1/inventario/reservas/21/liberar`

```http
Accept: application/json
X-Traza-Id: d178cd20-f88c-4dc8-b3cb-ca30ba0d6492
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 42 ms · traza `d178cd20-f88c-4dc8-b3cb-ca30ba0d6492`

```json
{
  "id": 21,
  "microhub_id": 1,
  "producto_id": 8,
  "cantidad": 3,
  "estado": "liberada",
  "vigente": false,
  "referencia": {
    "tipo": "manual",
    "id": "evidencia-042caa"
  },
  "creada_en": "2026-11-26T15:23:01-06:00",
  "vence_en": "2026-11-26T15:53:01-06:00",
  "cerrada_en": "2026-11-26T15:23:01-06:00"
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
X-Traza-Id: 3943e2d7-f814-4f78-9403-bff99c800d42
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "minimo": 41
}
```

**Respuesta.** HTTP 200 (esperado 200) · 70 ms · traza `3943e2d7-f814-4f78-9403-bff99c800d42`

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
  "actualizado_en": "2026-11-26T15:23:01-06:00"
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
X-Traza-Id: 37c4ac97-efbe-4716-b260-9c6fdd2ae122
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "minimo": 41
}
```

**Respuesta.** HTTP 200 (esperado 200) · 66 ms · traza `37c4ac97-efbe-4716-b260-9c6fdd2ae122`

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
  "actualizado_en": "2026-11-26T15:23:01-06:00"
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
      "actualizado_en": "2026-11-26T15:23:01.927224-06:00"
    }
  }
]
```

### INV-19 · El operador intenta cambiar el mínimo · PASA

**Objetivo.** Sin inventario.ajuste.

**Petición.** `PATCH http://inventario:5111/api/v1/inventario/1/9/minimo`

```http
Accept: application/json
X-Traza-Id: 7e402af1-9430-4488-ac88-fde50e6d3a71
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "minimo": 1
}
```

**Respuesta.** HTTP 403 (esperado 403) · 28 ms · traza `7e402af1-9430-4488-ac88-fde50e6d3a71`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "7e402af1-9430-4488-ac88-fde50e6d3a71"
  }
}
```

### INV-20 · Una merma cruza el mínimo · PASA

**Objetivo.** El trigger avisa del faltante al operador y al administrador.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: 7142f08d-7f71-4102-afa3-5ca8216b5e97
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

**Respuesta.** HTTP 201 (esperado 201) · 74 ms · traza `7142f08d-7f71-4102-afa3-5ca8216b5e97`

```json
{
  "movimiento": {
    "id": 2400,
    "microhub_id": 1,
    "producto_id": 9,
    "tipo": "merma",
    "cantidad": -2,
    "existencia_resultante": 40,
    "referencia": null,
    "motivo": "Se rompieron dos",
    "usuario_id": 1,
    "fecha": "2026-11-26T15:23:02-06:00"
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
X-Traza-Id: 9019f329-63a6-4968-b098-bc62fe8fa792
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 85 ms · traza `9019f329-63a6-4968-b098-bc62fe8fa792`

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
X-Traza-Id: 38c27f3e-8dec-4002-8b73-b349b307b2b7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 63 ms · traza `38c27f3e-8dec-4002-8b73-b349b307b2b7`

```json
{
  "datos": [
    {
      "id": 2392,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 5,
      "existencia_resultante": 91,
      "referencia": {
        "tipo": "orden_compra",
        "id": "1"
      },
      "motivo": "Llegada de mercancía",
      "usuario_id": 2,
      "fecha": "2026-11-26T15:23:00-06:00"
    },
    {
      "id": 2262,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 5,
      "existencia_resultante": 86,
      "referencia": {
        "tipo": "orden_compra",
        "id": "1"
      },
      "motivo": "Prueba de recepción",
      "usuario_id": 2,
      "fecha": "2026-11-26T14:21:54-06:00"
    },
    {
      "id": 2260,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 3,
      "existencia_resultante": 84,
      "referencia": null,
      "motivo": "Prueba XML",
      "usuario_id": 2,
      "fecha": "2026-11-26T14:21:54-06:00"
    },
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
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 23,
    "paginas": 2
  }
}
```

## Servicio notificaciones · puerto 5124

### NOT-01 · Enviar un aviso a todo un rol · PASA

**Objetivo.** El administrador avisa a los operadores de un microhub.

**Petición.** `POST http://notificaciones:5124/api/v1/notificaciones`

```http
Accept: application/json
X-Traza-Id: aaa1385c-ebba-4bf8-9ce1-1dd35c7c0b02
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "rol": "operador",
  "microhub_id": 1,
  "tipo": "sistema",
  "titulo": "Evidencia 60b2bf",
  "mensaje": "Aviso de prueba para el microhub 1",
  "referencia": {
    "tipo": "sistema",
    "id": "evidencia"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 54 ms · traza `aaa1385c-ebba-4bf8-9ce1-1dd35c7c0b02`

```json
{
  "enviadas": 1,
  "omitidas": 0,
  "ids": [
    864
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
    "titulo": "Evidencia 60b2bf",
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
X-Traza-Id: 3c76938e-1052-4ca8-baf1-847c427254e9
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

**Respuesta.** HTTP 403 (esperado 403) · 36 ms · traza `3c76938e-1052-4ca8-baf1-847c427254e9`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "3c76938e-1052-4ca8-baf1-847c427254e9"
  }
}
```

### NOT-03 · Destino inexistente · PASA

**Objetivo.** Un rol sin personas activas se rechaza.

**Petición.** `POST http://notificaciones:5124/api/v1/notificaciones`

```http
Accept: application/json
X-Traza-Id: 62ecd12e-e0b9-4810-bc57-3e46be22e5a1
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

**Respuesta.** HTTP 422 (esperado 422) · 35 ms · traza `62ecd12e-e0b9-4810-bc57-3e46be22e5a1`

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
    "traza_id": "62ecd12e-e0b9-4810-bc57-3e46be22e5a1"
  }
}
```

### NOT-04 · Mi bandeja · PASA

**Objetivo.** Los avisos de la persona, el más reciente primero.

**Petición.** `GET http://notificaciones:5124/api/v1/notificaciones?solo_no_leidas=true&por_pagina=20`

```http
Accept: application/json
X-Traza-Id: 2b48f1e5-0f82-4cd5-a0bd-575d82ffe10b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 51 ms · traza `2b48f1e5-0f82-4cd5-a0bd-575d82ffe10b`

```json
{
  "datos": [
    {
      "id": 864,
      "tipo": "sistema",
      "titulo": "Evidencia 60b2bf",
      "mensaje": "Aviso de prueba para el microhub 1",
      "leida": false,
      "referencia": {
        "tipo": "sistema",
        "id": "evidencia"
      },
      "creada_en": "2026-11-26T15:23:02-06:00"
    },
    {
      "id": 862,
      "tipo": "inventario",
      "titulo": "Faltante en Microhub San Bernabé Centro",
      "mensaje": "Atún en agua: quedan 40 (mínimo 41).",
      "leida": false,
      "referencia": {
        "tipo": "producto",
        "id": "9"
      },
      "creada_en": "2026-11-26T15:23:02-06:00"
    },
    {
      "id": 853,
      "tipo": "abastecimiento",
      "titulo": "Orden de compra OC-20261126-000038",
      "mensaje": "La orden quedó recibida.",
      "leida": false,
      "referencia": {
        "tipo": "orden",
        "id": "38"
      },
      "creada_en": "2026-11-26T15:22:04-06:00"
    },
    {
      "id": 852,
      "tipo": "abastecimiento",
      "titulo": "Solicitud de compra SC-20261126-000063",
      "mensaje": "Tu solicitud fue aprobada.",
      "leida": false,
      "referencia": {
        "tipo": "solicitud",
        "id": "63"
      },
      "creada_en": "2026-11-26T15:22:03-06:00"
    },
    {
      "id": 845,
      "tipo": "abastecimiento",
      "titulo": "Solicitud de compra SC-20261126-000062",
      "mensaje": "Tu solicitud fue aprobada.",
      "leida": false,
      "referencia": {
        "tipo": "solicitud",
        "id": "62"
      },
      "creada_en": "2026-11-26T15:21:25-06:00"
    },
    {
      "id": 802,
      "tipo": "inventario",
      "titulo": "Faltante en Microhub San Bernabé Centro",
      "mensaje": "Yogur natural: quedan 8 (mínimo 8).",
      "leida": false,
      "referencia": {
        "tipo": "producto",
        "id": "34"
      },
      "creada_en": "2026-11-26T14:25:42-06:00"
    },
    {
      "id": 800,
      "tipo": "inventario",
      "titulo": "Faltante en Microhub San Bernabé Centro",
      "mensaje": "Harina de trigo: quedan 10 (mínimo 10).",
      "leida": false,
      "referencia": {
        "tipo": "producto",
        "id": "7"
      },
      "creada_en": "2026-11-26T14:25:42-06:00"
    },
    {
      "id": 798,
      "tipo": "inventario",
      "titulo": "Faltante en Microhub San Bernabé Centro",
      "mensaje": "Frijol negro a granel: quedan 0 (mínimo 10).",
      "leida": false,
      "referencia": {
        "tipo": "producto",
        "id": "1"
      },
      "creada_en": "2026-11-26T14:25:34-06:00"
    },
    {
      "id": 797,
      "tipo": "abastecimiento",
      "titulo": "Solicitud de compra SC-20261126-000061",
      "mensaje": "Tu solicitud fue rechazada.",
      "leida": false,
      "referencia": {
        "tipo": "solicitud",
        "id": "61"
      },
      "creada_en": "2026-11-26T14:22:22-06:00"
    },
    {
      "id": 794,
      "tipo": "abastecimiento",
      "titulo": "Orden de compra OC-20261126-000037",
      "mensaje": "La orden quedó recibida.",
      "leida": false,
      "referencia": {
        "tipo": "orden",
        "id": "37"
      },
      "creada_en": "2026-11-26T14:22:21-06:00"
    },
    {
      "id": 793,
      "tipo": "abastecimiento",
      "titulo": "Solicitud de compra SC-20261126-000060",
      "mensaje": "Tu solicitud fue aprobada.",
      "leida": false,
      "referencia": {
        "tipo": "solicitud",
        "id": "60"
      },
      "creada_en": "2026-11-26T14:22:19-06:00"
    },
    {
      "id": 791,
      "tipo": "abastecimiento",
      "titulo": "Solicitud de compra SC-20261126-000059",
      "mensaje": "Tu solicitud fue rechazada.",
      "leida": false,
      "referencia": {
        "tipo": "solicitud",
        "id": "59"
      },
      "creada_en": "2026-11-26T14:22:19-06:00"
    },
    {
      "id": 788,
      "tipo": "abastecimiento",
      "titulo": "Orden de compra OC-20261126-000036",
      "mensaje": "La orden quedó recibida.",
      "leida": false,
      "referencia": {
        "tipo": "orden",
        "id": "36"
      },
      "creada_en": "2026-11-26T14:22:17-06:00"
    },
    {
      "id": 787,
      "tipo": "abastecimiento",
      "titulo": "Solicitud de compra SC-20261126-000058",
      "mensaje": "Tu solicitud fue aprobada.",
      "leida": false,
      "referencia": {
        "tipo": "solicitud",
        "id": "58"
      },
      "creada_en": "2026-11-26T14:22:15-06:00"
    },
    {
      "id": 784,
      "tipo": "abastecimiento",
      "titulo": "Solicitud de compra SC-20261126-000056",
      "mensaje": "Tu solicitud fue rechazada.",
      "leida": false,
      "referencia": {
        "tipo": "solicitud",
        "id": "56"
      },
      "creada_en": "2026-11-26T14:22:14-06:00"
    },
    {
      "id": 781,
      "tipo": "abastecimiento",
      "titulo": "Orden de compra OC-20261126-000035",
      "mensaje": "La orden quedó cancelada.",
      "leida": false,
      "referencia": {
        "tipo": "orden",
        "id": "35"
      },
      "creada_en": "2026-11-26T14:22:14-06:00"
    },
    {
      "id": 780,
      "tipo": "abastecimiento",
      "titulo": "Solicitud de compra SC-20261126-000055",
      "mensaje": "Tu solicitud fue aprobada.",
      "leida": false,
      "referencia": {
        "tipo": "solicitud",
        "id": "55"
      },
      "creada_en": "2026-11-26T14:22:14-06:00"
    },
    {
      "id": 778,
      "tipo": "sistema",
      "titulo": "Prueba dfcaad9f",
      "mensaje": "Sistema",
      "leida": false,
      "referencia": null,
      "creada_en": "2026-11-26T14:22:00-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 18,
    "paginas": 1
  }
}
```

### NOT-05 · Mi bandeja (XML) · PASA

**Objetivo.** Respuesta XML que cumple notificaciones.xsd.

**Petición.** `GET http://notificaciones:5124/api/v1/notificaciones?por_pagina=3`

```http
Accept: application/xml
X-Traza-Id: 0896a711-1454-49be-a445-2598bcb96666
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 46 ms · traza `0896a711-1454-49be-a445-2598bcb96666`

```xml
<?xml version='1.0' encoding='utf-8'?>
<notificaciones xmlns="urn:microhubs:v1" version="1"><datos><notificacion><id>864</id><tipo>sistema</tipo><titulo>Evidencia 60b2bf</titulo><mensaje>Aviso de prueba para el microhub 1</mensaje><leida>false</leida><referencia><tipo>sistema</tipo><id>evidencia</id></referencia><creada_en>2026-11-26T15:23:02-06:00</creada_en></notificacion><notificacion><id>862</id><tipo>inventario</tipo><titulo>Faltante en Microhub San Bernabé Centro</titulo><mensaje>Atún en agua: quedan 40 (mínimo 41).</mensaje><leida>false</leida><referencia><tipo>producto</tipo><id>9</id></referencia><creada_en>2026-11-26T15:23:02-06:00</creada_en></notificacion><notificacion><id>853</id><tipo>abastecimiento</tipo><titulo>Orden de compra OC-20261126-000038</titulo><mensaje>La orden quedó recibida.</mensaje><leida>false</leida><referencia><tipo>orden</tipo><id>38</id></referencia><creada_en>2026-11-26T15:22:04-06:00</creada_en></notificacion></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>141</total><paginas>47</paginas></paginacion></notificaciones>
```

### NOT-06 · Avisos sin leer · PASA

**Objetivo.** Conteo para la insignia de la app.

**Petición.** `GET http://notificaciones:5124/api/v1/notificaciones/conteo`

```http
Accept: application/json
X-Traza-Id: 5da56692-3552-428a-a2dd-e1a064b49003
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 26 ms · traza `5da56692-3552-428a-a2dd-e1a064b49003`

```json
{
  "no_leidas": 18
}
```

### NOT-07 · Confirmar la lectura · PASA

**Objetivo.** El aviso queda leído.

**Petición.** `POST http://notificaciones:5124/api/v1/notificaciones/864/leer`

```http
Accept: application/json
X-Traza-Id: 9b708dc7-6e61-48a0-9e1f-d52dc121d069
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 28 ms · traza `9b708dc7-6e61-48a0-9e1f-d52dc121d069`

```json
{
  "id": 864,
  "tipo": "sistema",
  "titulo": "Evidencia 60b2bf",
  "mensaje": "Aviso de prueba para el microhub 1",
  "leida": true,
  "referencia": {
    "tipo": "sistema",
    "id": "evidencia"
  },
  "creada_en": "2026-11-26T15:23:02-06:00"
}
```

**Evidencia en PostgreSQL.** `SELECT id, leido_en IS NOT NULL AS leido FROM web_notificacion WHERE id = %s`

```json
[
  {
    "id": 864,
    "leido": true
  }
]
```

### NOT-08 · Leído por otra persona · PASA

**Objetivo.** Un aviso ajeno no se puede marcar.

**Petición.** `POST http://notificaciones:5124/api/v1/notificaciones/864/leer`

```http
Accept: application/json
X-Traza-Id: 312a5f7c-ef56-4e19-98a9-9e3738c1160e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 27 ms · traza `312a5f7c-ef56-4e19-98a9-9e3738c1160e`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe ese aviso en tu bandeja.",
    "traza_id": "312a5f7c-ef56-4e19-98a9-9e3738c1160e"
  }
}
```

### NOT-09 · Marcar todos como leídos · PASA

**Objetivo.** Confirma la lectura de todos los pendientes.

**Petición.** `POST http://notificaciones:5124/api/v1/notificaciones/leer-todas`

```http
Accept: application/json
X-Traza-Id: c3d26283-5d38-4b5c-9e83-96c693888a81
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 30 ms · traza `c3d26283-5d38-4b5c-9e83-96c693888a81`

```json
{
  "marcadas": 17
}
```

### NOT-10 · Mis preferencias · PASA

**Objetivo.** Qué tipos de aviso recibe la persona.

**Petición.** `GET http://notificaciones:5124/api/v1/notificaciones/preferencias`

```http
Accept: application/json
X-Traza-Id: fefb435b-6040-4324-a962-323683af3299
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 48 ms · traza `fefb435b-6040-4324-a962-323683af3299`

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
X-Traza-Id: 58c0d189-f072-468c-b7dc-d95e2ab64f1f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "activa": false
}
```

**Respuesta.** HTTP 200 (esperado 200) · 75 ms · traza `58c0d189-f072-468c-b7dc-d95e2ab64f1f`

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
X-Traza-Id: 5f23b94c-d32f-4f8c-83bd-a075bd8d3a37
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "rol": "operador",
  "microhub_id": 1,
  "tipo": "inventario",
  "titulo": "Evidencia 60b2bf",
  "mensaje": "Faltante de prueba"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 58 ms · traza `5f23b94c-d32f-4f8c-83bd-a075bd8d3a37`

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
X-Traza-Id: c108bcaa-8bb4-4ba8-bd9b-e67044ce50b2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "activa": false
}
```

**Respuesta.** HTTP 409 (esperado 409) · 7 ms · traza `c108bcaa-8bb4-4ba8-bd9b-e67044ce50b2`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Los avisos del sistema no se pueden apagar.",
    "traza_id": "c108bcaa-8bb4-4ba8-bd9b-e67044ce50b2"
  }
}
```

### NOT-14 · Borrar un aviso · PASA

**Objetivo.** Quita el aviso de la bandeja propia.

**Petición.** `DELETE http://notificaciones:5124/api/v1/notificaciones/864`

```http
Accept: application/json
X-Traza-Id: 0282e9b5-8995-461e-88c9-16c75980f20b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 26 ms · traza `0282e9b5-8995-461e-88c9-16c75980f20b`

```json
(sin cuerpo)
```

## Servicio proveedores · puerto 5113

### PRV-01 · Proveedores · PASA

**Objetivo.** Lista con cobertura y calificación.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores?por_pagina=10`

```http
Accept: application/json
X-Traza-Id: 14d58fa0-7a67-40bf-8376-2c7b8272e0d3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 52 ms · traza `14d58fa0-7a67-40bf-8376-2c7b8272e0d3`

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
X-Traza-Id: 83911aa0-95f8-4cf8-9ba2-6e198acefbf9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 52 ms · traza `83911aa0-95f8-4cf8-9ba2-6e198acefbf9`

```xml
<?xml version='1.0' encoding='utf-8'?>
<proveedores xmlns="urn:microhubs:v1" version="1"><datos><proveedor><id>1</id><clave>PV-01</clave><nombre>Abarrotes del Norte</nombre><contacto>Rosa Garza</contacto><correo>ventas@abarrotesdelnorte.example</correo><telefono>8181000101</telefono><dias_entrega>2</dias_entrega><pedido_minimo>800.00</pedido_minimo><condiciones_pago>Contado</condiciones_pago><estatus>activo</estatus><zonas><zona_id>1</zona_id><zona_id>2</zona_id><zona_id>3</zona_id><zona_id>4</zona_id></zonas><calificacion>4</calificacion><evaluaciones>1</evaluaciones></proveedor><proveedor><id>2</id><clave>PV-02</clave><nombre>Distribuidora Regia</nombre><contacto>Luis Treviño</contacto><correo>pedidos@distregia.example</correo><telefono>8181000102</telefono><dias_entrega>1</dias_entrega><pedido_minimo>500.00</pedido_minimo><condiciones_pago>Crédito a 7 días</condiciones_pago><estatus>activo</estatus><zonas><zona_id>1</zona_id><zona_id>2</zona_id><zona_id>3</zona_id><zona_id>4</zona_id></zonas><calificacion>4</calificacion><evaluaciones>1</evaluaciones></proveedor><proveedor><id>3</id><clave>PV-03</clave><nombre>Mayorista San Nicolás</nombre><contacto>Elena Cantú</contacto><correo>compras@mayoristasn.example</correo><telefono>8181000103</telefono><dias_entrega>4</dias_entrega><pedido_minimo>1500.00</pedido_minimo><condiciones_pago>Crédito a 15 días</condiciones_pago><estatus>activo</estatus><zonas><zona_id>1</zona_id><zona_id>2</zona_id><zona_id>3</zona_id><zona_id>4</zona_id></zonas><calificacion>4</calificacion><evaluaciones>1</evaluaciones></proveedor></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>3</total><paginas>1</paginas></paginacion></proveedores>
```

### PRV-03 · Un cliente intenta ver proveedores · PASA

**Objetivo.** El perfil cliente no tiene proveedores.ver.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores`

```http
Accept: application/json
X-Traza-Id: 1719180c-b00c-4742-9734-8776e067b58b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 31 ms · traza `1719180c-b00c-4742-9734-8776e067b58b`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "1719180c-b00c-4742-9734-8776e067b58b"
  }
}
```

### PRV-04 · Un proveedor · PASA

**Objetivo.** Con las zonas que cubre y su calificación.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/2`

```http
Accept: application/json
X-Traza-Id: 70ce3668-0fcd-4480-838c-84b3e688f50c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 33 ms · traza `70ce3668-0fcd-4480-838c-84b3e688f50c`

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
X-Traza-Id: a17d552d-3334-4a92-a749-44d61812930c
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

**Respuesta.** HTTP 201 (esperado 201) · 88 ms · traza `a17d552d-3334-4a92-a749-44d61812930c`

```json
{
  "id": 82,
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
    "id": 82,
    "clave": "EV-ED6557",
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
X-Traza-Id: 04d266e6-a2ac-4e10-97b6-f81ede4e04b2
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

**Respuesta.** HTTP 409 (esperado 409) · 28 ms · traza `04d266e6-a2ac-4e10-97b6-f81ede4e04b2`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Ya existe un proveedor con la clave EV-ED6557.",
    "traza_id": "04d266e6-a2ac-4e10-97b6-f81ede4e04b2"
  }
}
```

### PRV-07 · Correo inválido · PASA

**Objetivo.** Validación con detalle por campo.

**Petición.** `POST http://proveedores:5113/api/v1/proveedores`

```http
Accept: application/json
X-Traza-Id: 91ad3885-7321-4c20-867e-f19f5ddb9984
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

**Respuesta.** HTTP 422 (esperado 422) · 7 ms · traza `91ad3885-7321-4c20-867e-f19f5ddb9984`

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
    "traza_id": "91ad3885-7321-4c20-867e-f19f5ddb9984"
  }
}
```

### PRV-08 · Un planeador intenta dar de alta · PASA

**Objetivo.** Sin proveedores.editar.

**Petición.** `POST http://proveedores:5113/api/v1/proveedores`

```http
Accept: application/json
X-Traza-Id: 8aedc1e2-7b6e-476d-98ad-47505ecdb3fa
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

**Respuesta.** HTTP 403 (esperado 403) · 28 ms · traza `8aedc1e2-7b6e-476d-98ad-47505ecdb3fa`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "8aedc1e2-7b6e-476d-98ad-47505ecdb3fa"
  }
}
```

### PRV-09 · Modificar un proveedor · PASA

**Objetivo.** Cambia el plazo y la cobertura; la clave no se toca.

**Petición.** `PUT http://proveedores:5113/api/v1/proveedores/82`

```http
Accept: application/json
X-Traza-Id: 58b0627a-0de5-4938-b132-d69fb2676c0b
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

**Respuesta.** HTTP 200 (esperado 200) · 92 ms · traza `58b0627a-0de5-4938-b132-d69fb2676c0b`

```json
{
  "id": 82,
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

**Petición.** `PATCH http://proveedores:5113/api/v1/proveedores/82`

```http
Accept: application/json
X-Traza-Id: 53cccc19-6d8b-4c48-b933-5261db9d8472
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "contacto": "Luis Prueba"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 119 ms · traza `53cccc19-6d8b-4c48-b933-5261db9d8472`

```json
{
  "id": 82,
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
    "clave": "EV-ED6557",
    "contacto": "Luis Prueba",
    "dias_entrega": 5
  }
]
```

### PRV-10 · Fijar una oferta · PASA

**Objetivo.** Alta del precio de compra de un producto.

**Petición.** `PUT http://proveedores:5113/api/v1/proveedores/82/catalogo/6`

```http
Accept: application/json
X-Traza-Id: cac43a93-222f-41b9-b7b5-93a0d2ed65cd
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

**Respuesta.** HTTP 200 (esperado 200) · 85 ms · traza `cac43a93-222f-41b9-b7b5-93a0d2ed65cd`

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
    "proveedor_id": 82,
    "producto_id": 6,
    "precio_compra": "0.05",
    "capacidad_semanal": 100,
    "minimo_compra": 5
  }
]
```

### PRV-11 · Producto inexistente en la oferta · PASA

**Objetivo.** La llave foránea rechaza el producto.

**Petición.** `PUT http://proveedores:5113/api/v1/proveedores/82/catalogo/999999`

```http
Accept: application/json
X-Traza-Id: ba5810f8-6584-402c-9941-7ed8a015fdb7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "precio_compra": 1,
  "capacidad_semanal": 10
}
```

**Respuesta.** HTTP 422 (esperado 422) · 60 ms · traza `ba5810f8-6584-402c-9941-7ed8a015fdb7`

```json
{
  "error": {
    "codigo": "REGLA_NEGOCIO",
    "mensaje": "El producto no existe.",
    "traza_id": "ba5810f8-6584-402c-9941-7ed8a015fdb7"
  }
}
```

### PRV-12 · Catálogo del proveedor · PASA

**Objetivo.** Sus ofertas, con el nombre del producto.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/82/catalogo`

```http
Accept: application/json
X-Traza-Id: 74d07ab0-b4e9-45b7-8973-4e2e398d9386
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 75 ms · traza `74d07ab0-b4e9-45b7-8973-4e2e398d9386`

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

**Petición.** `POST http://proveedores:5113/api/v1/proveedores/82/evaluaciones`

```http
Accept: application/json
X-Traza-Id: f69f50da-e369-464b-a8ab-4fa416b2bfed
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

**Respuesta.** HTTP 201 (esperado 201) · 104 ms · traza `f69f50da-e369-464b-a8ab-4fa416b2bfed`

```json
{
  "id": 25,
  "proveedor_id": 82,
  "puntualidad": 5,
  "calidad": 4,
  "precio": 3,
  "comentario": "Llegó a tiempo",
  "evaluado_por": 2,
  "evaluado_en": "2026-11-26T15:23:04-06:00"
}
```

**Evidencia en PostgreSQL.** `SELECT proveedor_id, puntualidad, calidad, precio, evaluado_por FROM proveedor_evaluacion WHERE proveedor_id = %s`

```json
[
  {
    "proveedor_id": 82,
    "puntualidad": 5,
    "calidad": 4,
    "precio": 3,
    "evaluado_por": 2
  }
]
```

### PRV-14 · Evaluaciones y promedio · PASA

**Objetivo.** Calificaciones recibidas y su promedio.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/82/evaluaciones`

```http
Accept: application/json
X-Traza-Id: 91c87377-93e1-4794-91cd-3fc1c07f4ff5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 75 ms · traza `91c87377-93e1-4794-91cd-3fc1c07f4ff5`

```json
{
  "datos": [
    {
      "id": 25,
      "proveedor_id": 82,
      "puntualidad": 5,
      "calidad": 4,
      "precio": 3,
      "comentario": "Llegó a tiempo",
      "evaluado_por": 2,
      "evaluado_en": "2026-11-26T15:23:04-06:00"
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

**Petición.** `POST http://proveedores:5113/api/v1/proveedores/82/evaluaciones`

```http
Accept: application/json
X-Traza-Id: d9f38f4a-8987-431a-9d76-e1f8811fcf8b
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

**Respuesta.** HTTP 403 (esperado 403) · 28 ms · traza `d9f38f4a-8987-431a-9d76-e1f8811fcf8b`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "d9f38f4a-8987-431a-9d76-e1f8811fcf8b"
  }
}
```

### PRV-16 · Ofertas de un producto · PASA

**Objetivo.** De la más barata a la más cara.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/ofertas?producto_id=6`

```http
Accept: application/json
X-Traza-Id: 958bc6b3-e70e-4f8b-ae44-4da9c1d0235e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 72 ms · traza `958bc6b3-e70e-4f8b-ae44-4da9c1d0235e`

```json
{
  "datos": [
    {
      "proveedor": {
        "id": 82,
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
X-Traza-Id: 3c44e586-d480-4471-8bb1-f4326b6b9d6e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 96 ms · traza `3c44e586-d480-4471-8bb1-f4326b6b9d6e`

```json
{
  "datos": [
    {
      "proveedor": {
        "id": 82,
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
X-Traza-Id: 24fb727f-757d-453f-a909-7a39199de9e8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 8 ms · traza `24fb727f-757d-453f-a909-7a39199de9e8`

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
    "traza_id": "24fb727f-757d-453f-a909-7a39199de9e8"
  }
}
```

### PRV-19 · Dar de baja un proveedor · PASA

**Objetivo.** Baja lógica: ya no aparece en las ofertas.

**Petición.** `DELETE http://proveedores:5113/api/v1/proveedores/82`

```http
Accept: application/json
X-Traza-Id: 0087b142-9f0e-4f7a-8e30-66b17a6a479a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 58 ms · traza `0087b142-9f0e-4f7a-8e30-66b17a6a479a`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT clave, estatus FROM proveedor WHERE id = %s`

```json
[
  {
    "clave": "EV-ED6557",
    "estatus": "inactivo"
  }
]
```

### PRV-20 · Ofertas sin el proveedor de baja · PASA

**Objetivo.** El proveedor dado de baja no ofrece.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/ofertas?producto_id=6`

```http
Accept: application/json
X-Traza-Id: ec53aaba-898e-4396-ba8c-86ee27911407
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 139 ms · traza `ec53aaba-898e-4396-ba8c-86ee27911407`

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
X-Traza-Id: bedc6294-f384-4516-818a-77db235fae61
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 836 ms · traza `bedc6294-f384-4516-818a-77db235fae61`

```json
{
  "datos": [
    {
      "id": 36,
      "nombre": "Lista de prueba cf2a1ce6",
      "zona_id": 3,
      "vigente_desde": "2027-01-01",
      "vigente_hasta": "2027-01-31",
      "estatus": "inactivo",
      "productos": 1
    },
    {
      "id": 35,
      "nombre": "Lista de evidencias 41a205",
      "zona_id": 3,
      "vigente_desde": "2027-01-01",
      "vigente_hasta": "2027-01-31",
      "estatus": "inactivo",
      "productos": 1
    },
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
    "total": 16,
    "paginas": 1
  }
}
```

### PRE-02 · Listas (XML) · PASA

**Objetivo.** Respuesta XML que cumple precios.xsd.

**Petición.** `GET http://precios:5112/api/v1/precios/listas`

```http
Accept: application/xml
X-Traza-Id: f7425aa5-f542-4e14-a8a4-1687ca004814
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 43 ms · traza `f7425aa5-f542-4e14-a8a4-1687ca004814`

```xml
<?xml version='1.0' encoding='utf-8'?>
<listas xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><datos><lista><id>36</id><nombre>Lista de prueba cf2a1ce6</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>35</id><nombre>Lista de evidencias 41a205</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>34</id><nombre>Lista de evidencias f9009f</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>33</id><nombre>Lista de evidencias 3fdd2e</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>29</id><nombre>Lista de prueba 994bc9b6</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>25</id><nombre>Lista de prueba 53ef8464</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>23</id><nombre>Lista de prueba 6efd002d</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>20</id><nombre>Lista de evidencias dba9cd</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>17</id><nombre>Lista de evidencias 4ccd1c</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>16</id><nombre>Lista de evidencias 6ddeea</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>15</id><nombre>Lista de evidencias 962abe</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>14</id><nombre>Lista de evidencias fa981b</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>11</id><nombre>Lista de prueba a8dad7c8</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>4</id><nombre>Lista de prueba 8a4e607d</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>3</id><nombre>Lista de evidencias 0c58f9</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>1</id><nombre>Lista San Bernabé Centro</nombre><zona_id>1</zona_id><vigente_desde>2026-10-19</vigente_desde><vigente_hasta xsi:nil="true" /><estatus>activo</estatus><productos>20</productos></lista></datos><paginacion><pagina>1</pagina><por_pagina>20</por_pagina><total>16</total><paginas>1</paginas></paginacion></listas>
```

### PRE-03 · Un cliente intenta ver las listas · PASA

**Objetivo.** Sin precios.ver.

**Petición.** `GET http://precios:5112/api/v1/precios/listas`

```http
Accept: application/json
X-Traza-Id: 7ce3aa1f-26a4-4b89-a978-05b52e65508a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 29 ms · traza `7ce3aa1f-26a4-4b89-a978-05b52e65508a`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "7ce3aa1f-26a4-4b89-a978-05b52e65508a"
  }
}
```

### PRE-04 · Crear una lista · PASA

**Objetivo.** Lista de una zona con un precio y su costo.

**Petición.** `POST http://precios:5112/api/v1/precios/listas`

```http
Accept: application/json
X-Traza-Id: 4da2867e-1c58-4f7a-ab39-4323959d52fd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Lista de evidencias a7a59e",
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

**Respuesta.** HTTP 201 (esperado 201) · 104 ms · traza `4da2867e-1c58-4f7a-ab39-4323959d52fd`

```json
{
  "id": 40,
  "nombre": "Lista de evidencias a7a59e",
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
      "actualizado_en": "2026-11-26T15:23:05-06:00"
    }
  ]
}
```

**Explicación.** Margen = (precio − costo) / precio = (50 − 30) / 50 = 40 %.

**Evidencia en PostgreSQL.** `SELECT l.id, l.nombre, l.zona_id, l.vigente_desde, l.vigente_hasta, i.producto_id, i.precio, i.costo FROM lista_precio l JOIN lista_precio_item i ON i.lista_id = l.id WHERE l.nombre = %s`

```json
[
  {
    "id": 40,
    "nombre": "Lista de evidencias a7a59e",
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
X-Traza-Id: bedb4e62-7acc-4cf0-9c15-2ae465d0ac9e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Lista de evidencias a7a59e bis",
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

**Respuesta.** HTTP 409 (esperado 409) · 30 ms · traza `bedb4e62-7acc-4cf0-9c15-2ae465d0ac9e`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "La lista «Lista de evidencias a7a59e» ya rige en esa zona durante esas fechas.",
    "traza_id": "bedb4e62-7acc-4cf0-9c15-2ae465d0ac9e"
  }
}
```

### PRE-06 · Cambiar el precio de un producto · PASA

**Objetivo.** Sube el precio de 50 a 52; el costo se conserva.

**Petición.** `PUT http://precios:5112/api/v1/precios/listas/40/items/2`

```http
Accept: application/json
X-Traza-Id: 18fe3560-ce1a-496b-b5fb-6049df5da0b1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "precio": 52.0
}
```

**Respuesta.** HTTP 200 (esperado 200) · 41 ms · traza `18fe3560-ce1a-496b-b5fb-6049df5da0b1`

```json
{
  "producto": {
    "id": 2,
    "nombre": "Arroz superextra"
  },
  "precio": 52.0,
  "costo": 30.0,
  "margen_pct": 42.3,
  "actualizado_en": "2026-11-26T15:23:05-06:00"
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

**Petición.** `GET http://precios:5112/api/v1/precios/historial?lista_id=40&producto_id=2`

```http
Accept: application/json
X-Traza-Id: 0d720c21-b948-4b12-a83e-9b3789934699
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 48 ms · traza `0d720c21-b948-4b12-a83e-9b3789934699`

```json
{
  "datos": [
    {
      "id": 52,
      "lista_id": 40,
      "producto_id": 2,
      "precio_anterior": 50.0,
      "precio_nuevo": 52.0,
      "usuario_id": 1,
      "fecha": "2026-11-26T15:23:05-06:00"
    },
    {
      "id": 51,
      "lista_id": 40,
      "producto_id": 2,
      "precio_anterior": null,
      "precio_nuevo": 50.0,
      "usuario_id": 1,
      "fecha": "2026-11-26T15:23:05-06:00"
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

**Petición.** `GET http://precios:5112/api/v1/precios/listas/40`

```http
Accept: application/json
X-Traza-Id: daebf9e8-40be-4332-bd10-d36ae0175dd5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 47 ms · traza `daebf9e8-40be-4332-bd10-d36ae0175dd5`

```json
{
  "id": 40,
  "nombre": "Lista de evidencias a7a59e",
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
      "actualizado_en": "2026-11-26T15:23:05-06:00"
    }
  ]
}
```

### PRE-09 · Precio dentro de la vigencia · PASA

**Objetivo.** Rige el precio de la lista de la zona.

**Petición.** `GET http://precios:5112/api/v1/precios/vigente?producto_id=2&zona_id=3&fecha=2027-01-15`

```http
Accept: application/json
X-Traza-Id: 94c7ec99-57e9-49db-8f2b-464497dc7924
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 96 ms · traza `94c7ec99-57e9-49db-8f2b-464497dc7924`

```json
{
  "producto_id": 2,
  "zona_id": 3,
  "fecha": "2027-01-15",
  "precio_base": 29.9,
  "lista": {
    "id": 40,
    "nombre": "Lista de evidencias a7a59e"
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
X-Traza-Id: ef49dae3-f43a-431a-9ffc-d3638253817a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 95 ms · traza `ef49dae3-f43a-431a-9ffc-d3638253817a`

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
X-Traza-Id: 09427093-8213-4162-954b-1a19e189d0ad
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 95 ms · traza `09427093-8213-4162-954b-1a19e189d0ad`

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
X-Traza-Id: 060fffec-b319-499a-ba77-78c116b9be94
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 93 ms · traza `060fffec-b319-499a-ba77-78c116b9be94`

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
X-Traza-Id: d154f9a9-b8ea-45e4-a289-8b321de3b3e5
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

**Respuesta.** HTTP 200 (esperado 200) · 89 ms · traza `d154f9a9-b8ea-45e4-a289-8b321de3b3e5`

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
X-Traza-Id: aa0e1b44-3ea9-4304-b9ae-a18bc2d19738
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

**Respuesta.** HTTP 422 (esperado 422) · 7 ms · traza `aa0e1b44-3ea9-4304-b9ae-a18bc2d19738`

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
    "traza_id": "aa0e1b44-3ea9-4304-b9ae-a18bc2d19738"
  }
}
```

### PRE-15 · Promoción que pasa del descuento máximo · PASA

**Objetivo.** Un porcentaje mayor al tope de la configuración se rechaza.

**Petición.** `POST http://precios:5112/api/v1/precios/promociones`

```http
Accept: application/json
X-Traza-Id: 84565f2e-8992-4a35-a52c-09492436c578
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

**Respuesta.** HTTP 422 (esperado 422) · 26 ms · traza `84565f2e-8992-4a35-a52c-09492436c578`

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
    "traza_id": "84565f2e-8992-4a35-a52c-09492436c578"
  }
}
```

### PRE-16 · Crear una promoción · PASA

**Objetivo.** Descuento de $2 en un producto.

**Petición.** `POST http://precios:5112/api/v1/precios/promociones`

```http
Accept: application/json
X-Traza-Id: cf211638-9701-446e-87af-4ce0fcb7efb0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Promoción de evidencias bec1",
  "tipo": "monto",
  "valor": 2.0,
  "producto_id": 1,
  "vigente_hasta": "2030-12-31"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 95 ms · traza `cf211638-9701-446e-87af-4ce0fcb7efb0`

```json
{
  "id": 17,
  "nombre": "Promoción de evidencias bec1",
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
    "id": 17,
    "nombre": "Promoción de evidencias bec1",
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
X-Traza-Id: cdaa4060-8ed3-479c-91e1-8786de651173
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 50 ms · traza `cdaa4060-8ed3-479c-91e1-8786de651173`

```json
{
  "datos": [
    {
      "id": 17,
      "nombre": "Promoción de evidencias bec1",
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

**Petición.** `DELETE http://precios:5112/api/v1/precios/promociones/17`

```http
Accept: application/json
X-Traza-Id: 37ade334-5123-4b2d-82a5-b0c5cb5edf82
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 34 ms · traza `37ade334-5123-4b2d-82a5-b0c5cb5edf82`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT id, estatus FROM promocion WHERE id = %s`

```json
[
  {
    "id": 17,
    "estatus": "inactivo"
  }
]
```

### PRE-19 · Márgenes · PASA

**Objetivo.** Renglones con costo, del margen más bajo al más alto.

**Petición.** `GET http://precios:5112/api/v1/precios/margenes?por_pagina=5`

```http
Accept: application/json
X-Traza-Id: c7455653-1176-4e9d-863d-f4187de14ac3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 72 ms · traza `c7455653-1176-4e9d-863d-f4187de14ac3`

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
X-Traza-Id: 8947e3f9-b3e3-4591-a755-381c9036d60b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 113 ms · traza `8947e3f9-b3e3-4591-a755-381c9036d60b`

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
X-Traza-Id: 4f7e6da2-aa3e-4d93-93d3-4e21acd900ae
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 6 ms · traza `4f7e6da2-aa3e-4d93-93d3-4e21acd900ae`

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
    "traza_id": "4f7e6da2-aa3e-4d93-93d3-4e21acd900ae"
  }
}
```

## Servicio abastecimiento · puerto 5114

### ABA-01 · Necesidades de reposición · PASA

**Objetivo.** Productos bajo su mínimo, con la mejor oferta.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/necesidades?por_pagina=100`

```http
Accept: application/json
X-Traza-Id: d197d35f-d664-4b35-ac60-bda511387c6d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 257 ms · traza `d197d35f-d664-4b35-ac60-bda511387c6d`

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
X-Traza-Id: 2e4747b8-0dd8-4177-8ae7-4187c3506b5b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 9 ms · traza `2e4747b8-0dd8-4177-8ae7-4187c3506b5b`

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
    "traza_id": "2e4747b8-0dd8-4177-8ae7-4187c3506b5b"
  }
}
```

### ABA-03 · Pedir mercancía · PASA

**Objetivo.** El operador pide reposición de su microhub.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: 1d9f5777-31bf-4a0a-a166-8343bb3e51f5
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

**Respuesta.** HTTP 201 (esperado 201) · 86 ms · traza `1d9f5777-31bf-4a0a-a166-8343bb3e51f5`

```json
{
  "id": 64,
  "folio": "SC-20261126-000064",
  "microhub_id": 1,
  "estado": "pendiente",
  "motivo": "Se acabó el producto el fin de semana",
  "solicitada_por": 2,
  "decidida_por": null,
  "decision_motivo": null,
  "decidida_en": null,
  "creada_en": "2026-11-26T15:23:07-06:00",
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
    "id": 64,
    "folio": "SC-20261126-000064",
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
    "titulo": "Solicitud de compra SC-20261126-000064",
    "referencia_tipo": "solicitud"
  }
]
```

### ABA-04 · Pedir para otro microhub · PASA

**Objetivo.** El operador solo trabaja con el suyo.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: 06413826-d66b-4e58-b095-7776d0e220d8
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

**Respuesta.** HTTP 403 (esperado 403) · 7 ms · traza `06413826-d66b-4e58-b095-7776d0e220d8`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "06413826-d66b-4e58-b095-7776d0e220d8"
  }
}
```

### ABA-05 · Producto repetido en la solicitud · PASA

**Objetivo.** Un producto aparece una sola vez.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: e8f7dd03-0453-4b73-b9f5-f7d4b3a753a2
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

**Respuesta.** HTTP 422 (esperado 422) · 6 ms · traza `e8f7dd03-0453-4b73-b9f5-f7d4b3a753a2`

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
    "traza_id": "e8f7dd03-0453-4b73-b9f5-f7d4b3a753a2"
  }
}
```

### ABA-06 · Solicitud de otro microhub · PASA

**Objetivo.** Otro operador no la ve.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/64`

```http
Accept: application/json
X-Traza-Id: 3c72da7e-a5f8-48cf-b73b-5e262d14633a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 24 ms · traza `3c72da7e-a5f8-48cf-b73b-5e262d14633a`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe esa solicitud de compra.",
    "traza_id": "3c72da7e-a5f8-48cf-b73b-5e262d14633a"
  }
}
```

### ABA-07 · Aprobar sin permiso · PASA

**Objetivo.** Solo el administrador decide.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/64/decision`

```http
Accept: application/json
X-Traza-Id: 8269acf5-2b11-4502-94c6-a3d604ca0d19
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aprobada"
}
```

**Respuesta.** HTTP 403 (esperado 403) · 30 ms · traza `8269acf5-2b11-4502-94c6-a3d604ca0d19`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "8269acf5-2b11-4502-94c6-a3d604ca0d19"
  }
}
```

### ABA-08 · Rechazar sin motivo · PASA

**Objetivo.** Rechazar exige el motivo.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/64/decision`

```http
Accept: application/json
X-Traza-Id: 138b40a4-520a-4d55-a163-0597fd89015a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "rechazada"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 9 ms · traza `138b40a4-520a-4d55-a163-0597fd89015a`

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
    "traza_id": "138b40a4-520a-4d55-a163-0597fd89015a"
  }
}
```

### ABA-09 · Ordenar antes de aprobar · PASA

**Objetivo.** Solo se ordena una solicitud aprobada.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/64/ordenar`

```http
Accept: application/json
X-Traza-Id: 2ab07d22-a10f-4227-be68-afbeb75d6435
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "proveedor_id": 1
}
```

**Respuesta.** HTTP 409 (esperado 409) · 86 ms · traza `2ab07d22-a10f-4227-be68-afbeb75d6435`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Solo se ordena una solicitud aprobada; esta está pendiente.",
    "traza_id": "2ab07d22-a10f-4227-be68-afbeb75d6435"
  }
}
```

### ABA-10 · Aprobar la solicitud · PASA

**Objetivo.** El administrador aprueba y quien pidió recibe el aviso.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/64/decision`

```http
Accept: application/json
X-Traza-Id: f1d34e48-89f5-4164-8b3e-8b65c85406be
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aprobada",
  "motivo": "Hay presupuesto"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 142 ms · traza `f1d34e48-89f5-4164-8b3e-8b65c85406be`

```json
{
  "id": 64,
  "folio": "SC-20261126-000064",
  "microhub_id": 1,
  "estado": "aprobada",
  "motivo": "Se acabó el producto el fin de semana",
  "solicitada_por": 2,
  "decidida_por": 1,
  "decision_motivo": "Hay presupuesto",
  "decidida_en": "2026-11-26T15:23:07-06:00",
  "creada_en": "2026-11-26T15:23:07-06:00",
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
    "titulo": "Solicitud de compra SC-20261126-000064",
    "mensaje": "Tu solicitud fue aprobada."
  }
]
```

### ABA-11 · Emitir la orden de compra · PASA

**Objetivo.** Cada línea va al proveedor indicado; el total es piezas × precio de compra.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/64/ordenar`

```http
Accept: application/json
X-Traza-Id: 17c160eb-fde3-4c40-8fa2-1ecc4399f21f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "proveedor_id": 1
}
```

**Respuesta.** HTTP 201 (esperado 201) · 265 ms · traza `17c160eb-fde3-4c40-8fa2-1ecc4399f21f`

```json
{
  "solicitud_id": 64,
  "ordenes": [
    {
      "id": 39,
      "folio": "OC-20261126-000039",
      "solicitud_id": 64,
      "proveedor": {
        "id": 1,
        "nombre": "Abarrotes del Norte"
      },
      "microhub_id": 1,
      "estado": "emitida",
      "fecha_esperada": "2026-11-28",
      "total": 853.3,
      "creada_en": "2026-11-26T15:23:08-06:00",
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
    "id": 39,
    "folio": "OC-20261126-000039",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/64/ordenar`

```http
Accept: application/json
X-Traza-Id: 53850d12-0eb9-4dd6-a9f3-e416297e2892
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "proveedor_id": 1
}
```

**Respuesta.** HTTP 409 (esperado 409) · 52 ms · traza `53850d12-0eb9-4dd6-a9f3-e416297e2892`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Solo se ordena una solicitud aprobada; esta está ordenada.",
    "traza_id": "53850d12-0eb9-4dd6-a9f3-e416297e2892"
  }
}
```

### ABA-13 · Recepción parcial · PASA

**Objetivo.** La mercancía que llegó entra al inventario.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/39/recepcion`

```http
Accept: application/json
X-Traza-Id: e77d4699-e406-48b6-ab35-63f14bc96799
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "operacion_uuid": "ef689530-5a1a-4b3f-b60e-a1cf897f7d64",
  "nota": "Llegó la primera caja",
  "lineas": [
    {
      "producto_id": 10,
      "cantidad": 23
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 352 ms · traza `e77d4699-e406-48b6-ab35-63f14bc96799`

```json
{
  "orden": {
    "id": 39,
    "folio": "OC-20261126-000039",
    "solicitud_id": 64,
    "proveedor": {
      "id": 1,
      "nombre": "Abarrotes del Norte"
    },
    "microhub_id": 1,
    "estado": "parcial",
    "fecha_esperada": "2026-11-28",
    "total": 853.3,
    "creada_en": "2026-11-26T15:23:08-06:00",
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
    "operacion_uuid": "ef689530-5a1a-4b3f-b60e-a1cf897f7d64:10",
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
    "existencia_resultante": 759,
    "referencia_tipo": "orden_compra",
    "referencia_id": 39
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/39/recepcion`

```http
Accept: application/json
X-Traza-Id: 952364e2-63df-4936-8925-a49336ff3cf5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "operacion_uuid": "ef689530-5a1a-4b3f-b60e-a1cf897f7d64",
  "nota": "Llegó la primera caja",
  "lineas": [
    {
      "producto_id": 10,
      "cantidad": 23
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 164 ms · traza `952364e2-63df-4936-8925-a49336ff3cf5`

```json
{
  "orden": {
    "id": 39,
    "folio": "OC-20261126-000039",
    "solicitud_id": 64,
    "proveedor": {
      "id": 1,
      "nombre": "Abarrotes del Norte"
    },
    "microhub_id": 1,
    "estado": "parcial",
    "fecha_esperada": "2026-11-28",
    "total": 853.3,
    "creada_en": "2026-11-26T15:23:08-06:00",
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
    "existencia": 759
  }
]
```

### ABA-15 · Recibir más de lo pedido · PASA

**Objetivo.** Solo falta lo que no ha llegado.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/39/recepcion`

```http
Accept: application/json
X-Traza-Id: 64bff15a-f9fb-4dc5-a7fa-37a5da97c705
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

**Respuesta.** HTTP 422 (esperado 422) · 51 ms · traza `64bff15a-f9fb-4dc5-a7fa-37a5da97c705`

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
    "traza_id": "64bff15a-f9fb-4dc5-a7fa-37a5da97c705"
  }
}
```

### ABA-16 · Cancelar una orden con mercancía recibida · PASA

**Objetivo.** Solo se cancela una orden sin recepciones.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/39/cancelar`

```http
Accept: application/json
X-Traza-Id: 693d213c-7345-4246-b898-fb4a23b03f26
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "motivo": "Ya llegó"
}
```

**Respuesta.** HTTP 409 (esperado 409) · 46 ms · traza `693d213c-7345-4246-b898-fb4a23b03f26`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Solo se cancela una orden emitida que todavía no recibió mercancía.",
    "traza_id": "693d213c-7345-4246-b898-fb4a23b03f26"
  }
}
```

### ABA-17 · Recepción final · PASA

**Objetivo.** Llega el resto: la orden queda recibida y avisa.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/39/recepcion`

```http
Accept: application/json
X-Traza-Id: e898ae18-3815-48a5-976e-753beb483a94
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

**Respuesta.** HTTP 201 (esperado 201) · 311 ms · traza `e898ae18-3815-48a5-976e-753beb483a94`

```json
{
  "orden": {
    "id": 39,
    "folio": "OC-20261126-000039",
    "solicitud_id": 64,
    "proveedor": {
      "id": 1,
      "nombre": "Abarrotes del Norte"
    },
    "microhub_id": 1,
    "estado": "recibida",
    "fecha_esperada": "2026-11-28",
    "total": 853.3,
    "creada_en": "2026-11-26T15:23:08-06:00",
    "cerrada_en": "2026-11-26T15:23:09-06:00",
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
    "existencia": 782
  }
]
```

**Evidencia en PostgreSQL.** `SELECT destinatario_id, titulo, mensaje FROM web_notificacion WHERE referencia_tipo = 'orden' AND referencia_id = %s`

```json
[
  {
    "destinatario_id": 2,
    "titulo": "Orden de compra OC-20261126-000039",
    "mensaje": "La orden quedó recibida."
  },
  {
    "destinatario_id": 1,
    "titulo": "Orden de compra OC-20261126-000039",
    "mensaje": "La orden quedó recibida."
  }
]
```

### ABA-18 · Recibir en una orden ya recibida · PASA

**Objetivo.** Una orden recibida no admite más mercancía.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/39/recepcion`

```http
Accept: application/json
X-Traza-Id: a46fcc3b-efbc-4fe7-ae4a-f2d1a97f2bc2
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

**Respuesta.** HTTP 409 (esperado 409) · 45 ms · traza `a46fcc3b-efbc-4fe7-ae4a-f2d1a97f2bc2`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "La orden está recibida; ya no recibe mercancía.",
    "traza_id": "a46fcc3b-efbc-4fe7-ae4a-f2d1a97f2bc2"
  }
}
```

### ABA-19 · Una orden · PASA

**Objetivo.** Con lo recibido de cada línea.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/ordenes/39`

```http
Accept: application/json
X-Traza-Id: 545295de-5c81-46de-b7c0-64942c4f8d24
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 66 ms · traza `545295de-5c81-46de-b7c0-64942c4f8d24`

```json
{
  "id": 39,
  "folio": "OC-20261126-000039",
  "solicitud_id": 64,
  "proveedor": {
    "id": 1,
    "nombre": "Abarrotes del Norte"
  },
  "microhub_id": 1,
  "estado": "recibida",
  "fecha_esperada": "2026-11-28",
  "total": 853.3,
  "creada_en": "2026-11-26T15:23:08-06:00",
  "cerrada_en": "2026-11-26T15:23:09-06:00",
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
X-Traza-Id: 9c954818-6bbc-4ad2-ab8b-943bd06c5af6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 98 ms · traza `9c954818-6bbc-4ad2-ab8b-943bd06c5af6`

```xml
<?xml version='1.0' encoding='utf-8'?>
<ordenes xmlns="urn:microhubs:v1" version="1"><datos><orden><id>39</id><folio>OC-20261126-000039</folio><solicitud_id>64</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>853.30</total><creada_en>2026-11-26T15:23:08-06:00</creada_en><cerrada_en>2026-11-26T15:23:09-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>38</id><folio>OC-20261126-000038</folio><solicitud_id>63</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>4060.00</total><creada_en>2026-11-26T15:22:04-06:00</creada_en><cerrada_en>2026-11-26T15:22:04-06:00</cerrada_en><lineas><linea><producto><id>31</id><nombre>Queso fresco</nombre></producto><cantidad>100</cantidad><precio_compra>40.60</precio_compra><cantidad_recibida>100</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>37</id><folio>OC-20261126-000037</folio><solicitud_id>60</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>859.95</total><creada_en>2026-11-26T14:22:19-06:00</creada_en><cerrada_en>2026-11-26T14:22:21-06:00</cerrada_en><lineas><linea><producto><id>12</id><nombre>Chiles jalapeños en escabeche</nombre></producto><cantidad>63</cantidad><precio_compra>13.65</precio_compra><cantidad_recibida>63</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>36</id><folio>OC-20261126-000036</folio><solicitud_id>58</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>853.30</total><creada_en>2026-11-26T14:22:16-06:00</creada_en><cerrada_en>2026-11-26T14:22:17-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>33</id><folio>OC-20261126-000033</folio><solicitud_id>53</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>853.30</total><creada_en>2026-11-26T14:19:44-06:00</creada_en><cerrada_en>2026-11-26T14:19:45-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>31</id><folio>OC-20261126-000031</folio><solicitud_id>51</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>853.30</total><creada_en>2026-11-26T14:04:57-06:00</creada_en><cerrada_en>2026-11-26T14:04:58-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>29</id><folio>OC-20261126-000029</folio><solicitud_id>49</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>853.30</total><creada_en>2026-11-26T13:51:34-06:00</creada_en><cerrada_en>2026-11-26T13:51:35-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>28</id><folio>OC-20261126-000028</folio><solicitud_id>47</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>859.95</total><creada_en>2026-11-26T00:32:05-06:00</creada_en><cerrada_en>2026-11-26T00:32:06-06:00</cerrada_en><lineas><linea><producto><id>12</id><nombre>Chiles jalapeños en escabeche</nombre></producto><cantidad>63</cantidad><precio_compra>13.65</precio_compra><cantidad_recibida>63</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>27</id><folio>OC-20261126-000027</folio><solicitud_id>45</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>853.30</total><creada_en>2026-11-26T00:32:01-06:00</creada_en><cerrada_en>2026-11-26T00:32:03-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>25</id><folio>OC-20261020-000025</folio><solicitud_id>40</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>859.95</total><creada_en>2026-10-20T08:13:53-06:00</creada_en><cerrada_en>2026-10-20T08:13:54-06:00</cerrada_en><lineas><linea><producto><id>12</id><nombre>Chiles jalapeños en escabeche</nombre></producto><cantidad>63</cantidad><precio_compra>13.65</precio_compra><cantidad_recibida>63</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>24</id><folio>OC-20261020-000024</folio><solicitud_id>38</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>853.30</total><creada_en>2026-10-20T08:13:49-06:00</creada_en><cerrada_en>2026-10-20T08:13:51-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>22</id><folio>OC-20261020-000022</folio><solicitud_id>33</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>859.95</total><creada_en>2026-10-20T00:50:20-06:00</creada_en><cerrada_en>2026-10-20T00:50:21-06:00</cerrada_en><lineas><linea><producto><id>12</id><nombre>Chiles jalapeños en escabeche</nombre></producto><cantidad>63</cantidad><precio_compra>13.65</precio_compra><cantidad_recibida>63</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>21</id><folio>OC-20261020-000021</folio><solicitud_id>31</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>853.30</total><creada_en>2026-10-20T00:50:16-06:00</creada_en><cerrada_en>2026-10-20T00:50:17-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>18</id><folio>OC-20261020-000018</folio><solicitud_id>26</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>853.30</total><creada_en>2026-10-20T00:43:22-06:00</creada_en><cerrada_en>2026-10-20T00:43:24-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>16</id><folio>OC-20261020-000016</folio><solicitud_id>24</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>853.30</total><creada_en>2026-10-20T00:32:35-06:00</creada_en><cerrada_en>2026-10-20T00:32:36-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>14</id><folio>OC-20261020-000014</folio><solicitud_id>22</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>853.30</total><creada_en>2026-10-20T00:29:44-06:00</creada_en><cerrada_en>2026-10-20T00:29:45-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>12</id><folio>OC-20261020-000012</folio><solicitud_id>20</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>853.30</total><creada_en>2026-10-20T00:21:44-06:00</creada_en><cerrada_en>2026-10-20T00:21:45-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>10</id><folio>OC-20261020-000010</folio><solicitud_id>18</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>853.30</total><creada_en>2026-10-20T00:20:38-06:00</creada_en><cerrada_en>2026-10-20T00:20:39-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>9</id><folio>OC-20261020-000009</folio><solicitud_id>16</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>859.95</total><creada_en>2026-10-20T00:16:49-06:00</creada_en><cerrada_en>2026-10-20T00:16:50-06:00</cerrada_en><lineas><linea><producto><id>12</id><nombre>Chiles jalapeños en escabeche</nombre></producto><cantidad>63</cantidad><precio_compra>13.65</precio_compra><cantidad_recibida>63</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>8</id><folio>OC-20261020-000008</folio><solicitud_id>14</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>853.30</total><creada_en>2026-10-20T00:16:46-06:00</creada_en><cerrada_en>2026-10-20T00:16:47-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden></datos><paginacion><pagina>1</pagina><por_pagina>20</por_pagina><total>24</total><paginas>2</paginas></paginacion></ordenes>
```

### ABA-21 · Tablero de abastecimiento · PASA

**Objetivo.** Solicitudes y órdenes por estado.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/seguimiento`

```http
Accept: application/json
X-Traza-Id: 309f8832-0add-4938-961a-07e903c28c72
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 118 ms · traza `309f8832-0add-4938-961a-07e903c28c72`

```json
{
  "microhub_id": 1,
  "solicitudes": {
    "pendiente": 0,
    "aprobada": 1,
    "rechazada": 18,
    "ordenada": 39
  },
  "ordenes": {
    "emitida": 0,
    "parcial": 0,
    "recibida": 24,
    "cancelada": 15
  },
  "atrasadas": 0,
  "pendientes_inventario": 0,
  "proxima_entrega": null
}
```

### ABA-22 · Cancelar sin permiso · PASA

**Objetivo.** Cancelar una orden es del administrador.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/40/cancelar`

```http
Accept: application/json
X-Traza-Id: 77a6a5b7-ecd1-438c-8e85-a54a23ded4c6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "motivo": "No hace falta"
}
```

**Respuesta.** HTTP 403 (esperado 403) · 90 ms · traza `77a6a5b7-ecd1-438c-8e85-a54a23ded4c6`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "77a6a5b7-ecd1-438c-8e85-a54a23ded4c6"
  }
}
```

### ABA-23 · Cancelar una orden emitida · PASA

**Objetivo.** Una orden sin recepciones se puede cancelar con motivo.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/40/cancelar`

```http
Accept: application/json
X-Traza-Id: af3b1033-09ce-4dac-9228-118796f6e26a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "motivo": "El proveedor ya no surte"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 273 ms · traza `af3b1033-09ce-4dac-9228-118796f6e26a`

```json
{
  "id": 40,
  "folio": "OC-20261126-000040",
  "solicitud_id": 65,
  "proveedor": {
    "id": 1,
    "nombre": "Abarrotes del Norte"
  },
  "microhub_id": 1,
  "estado": "cancelada",
  "fecha_esperada": "2026-11-28",
  "total": 853.3,
  "creada_en": "2026-11-26T15:23:10-06:00",
  "cerrada_en": "2026-11-26T15:23:10-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/40/recepcion`

```http
Accept: application/json
X-Traza-Id: 45d4feae-27e4-4f2b-a5e2-12d060cdd595
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

**Respuesta.** HTTP 409 (esperado 409) · 48 ms · traza `45d4feae-27e4-4f2b-a5e2-12d060cdd595`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "La orden está cancelada; ya no recibe mercancía.",
    "traza_id": "45d4feae-27e4-4f2b-a5e2-12d060cdd595"
  }
}
```

### ABA-25 · Solicitudes (XML) · PASA

**Objetivo.** Respuesta XML que cumple abastecimiento.xsd.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/solicitudes?por_pagina=3`

```http
Accept: application/xml
X-Traza-Id: 5671d71b-d492-4614-be26-08f826c17fc6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 60 ms · traza `5671d71b-d492-4614-be26-08f826c17fc6`

```xml
<?xml version='1.0' encoding='utf-8'?>
<solicitudes xmlns="urn:microhubs:v1" version="1"><datos><solicitud><id>65</id><folio>SC-20261126-000065</folio><microhub_id>1</microhub_id><estado>ordenada</estado><motivo>Compra para cancelar</motivo><solicitada_por>2</solicitada_por><decidida_por>1</decidida_por><decision_motivo>Hay presupuesto</decision_motivo><decidida_en>2026-11-26T15:23:09-06:00</decidida_en><creada_en>2026-11-26T15:23:09-06:00</creada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad></linea></lineas></solicitud><solicitud><id>64</id><folio>SC-20261126-000064</folio><microhub_id>1</microhub_id><estado>ordenada</estado><motivo>Se acabó el producto el fin de semana</motivo><solicitada_por>2</solicitada_por><decidida_por>1</decidida_por><decision_motivo>Hay presupuesto</decision_motivo><decidida_en>2026-11-26T15:23:07-06:00</decidida_en><creada_en>2026-11-26T15:23:07-06:00</creada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad></linea></lineas></solicitud><solicitud><id>63</id><folio>SC-20261126-000063</folio><microhub_id>1</microhub_id><estado>ordenada</estado><motivo>Faltante detectado por el sistema</motivo><solicitada_por>2</solicitada_por><decidida_por>1</decidida_por><decision_motivo>Con presupuesto</decision_motivo><decidida_en>2026-11-26T15:22:03-06:00</decidida_en><creada_en>2026-11-26T15:22:03-06:00</creada_en><lineas><linea><producto><id>31</id><nombre>Queso fresco</nombre></producto><cantidad>100</cantidad></linea></lineas></solicitud></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>59</total><paginas>20</paginas></paginacion></solicitudes>
```

### ABA-26 · Un auditor consulta · PASA

**Objetivo.** El auditor ve las solicitudes sin poder crear.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: e285de8e-289d-4a54-bc21-2566fca8c61b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 61 ms · traza `e285de8e-289d-4a54-bc21-2566fca8c61b`

```json
{
  "datos": [
    {
      "id": 65,
      "folio": "SC-20261126-000065",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Compra para cancelar",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-11-26T15:23:09-06:00",
      "creada_en": "2026-11-26T15:23:09-06:00",
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
      "id": 64,
      "folio": "SC-20261126-000064",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Se acabó el producto el fin de semana",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-11-26T15:23:07-06:00",
      "creada_en": "2026-11-26T15:23:07-06:00",
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
      "id": 63,
      "folio": "SC-20261126-000063",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Faltante detectado por el sistema",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Con presupuesto",
      "decidida_en": "2026-11-26T15:22:03-06:00",
      "creada_en": "2026-11-26T15:22:03-06:00",
      "lineas": [
        {
          "producto": {
            "id": 31,
            "nombre": "Queso fresco"
          },
          "cantidad": 100
        }
      ]
    },
    {
      "id": 62,
      "folio": "SC-20261126-000062",
      "microhub_id": 1,
      "estado": "aprobada",
      "motivo": "Faltante detectado por el sistema",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Con presupuesto",
      "decidida_en": "2026-11-26T15:21:25-06:00",
      "creada_en": "2026-11-26T15:21:25-06:00",
      "lineas": [
        {
          "producto": {
            "id": 51,
            "nombre": "Pañal etapa 3"
          },
          "cantidad": 30
        }
      ]
    },
    {
      "id": 61,
      "folio": "SC-20261126-000061",
      "microhub_id": 1,
      "estado": "rechazada",
      "motivo": "Prueba XML",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Prueba XML",
      "decidida_en": "2026-11-26T14:22:22-06:00",
      "creada_en": "2026-11-26T14:22:22-06:00",
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
      "id": 60,
      "folio": "SC-20261126-000060",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-11-26T14:22:19-06:00",
      "creada_en": "2026-11-26T14:22:19-06:00",
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
      "id": 59,
      "folio": "SC-20261126-000059",
      "microhub_id": 1,
      "estado": "rechazada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": null,
      "decision_motivo": "Limpieza de la prueba",
      "decidida_en": null,
      "creada_en": "2026-11-26T14:22:18-06:00",
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
      "id": 58,
      "folio": "SC-20261126-000058",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "ok",
      "decidida_en": "2026-11-26T14:22:15-06:00",
      "creada_en": "2026-11-26T14:22:15-06:00",
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
      "id": 56,
      "folio": "SC-20261126-000056",
      "microhub_id": 1,
      "estado": "rechazada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Todavía hay existencia",
      "decidida_en": "2026-11-26T14:22:14-06:00",
      "creada_en": "2026-11-26T14:22:14-06:00",
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
      "id": 55,
      "folio": "SC-20261126-000055",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-11-26T14:22:14-06:00",
      "creada_en": "2026-11-26T14:22:13-06:00",
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
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 59,
    "paginas": 3
  }
}
```

### ABA-27 · Un cliente consulta · PASA

**Objetivo.** El cliente no tiene abastecimiento.ver.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: 78a9d9b3-c2aa-4f5d-9344-f7aa469ee1ff
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 30 ms · traza `78a9d9b3-c2aa-4f5d-9344-f7aa469ee1ff`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "78a9d9b3-c2aa-4f5d-9344-f7aa469ee1ff"
  }
}
```

## Servicio pedidos · puerto 5104

### ALI-01 · Resumen de pedidos por día y zona · PASA

**Objetivo.** Lo consume el servicio de demanda: pedidos, unidades, venta y clientes por día y zona.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/resumen?por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 5db3a115-b5d0-4776-bec7-25e05875d74e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 107 ms · traza `5db3a115-b5d0-4776-bec7-25e05875d74e`

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
      "pedidos": 34,
      "unidades": 182,
      "venta": 4853.6,
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
X-Traza-Id: e5852600-41d8-45db-a8e2-aa1ae3a0afec
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 8 ms · traza `e5852600-41d8-45db-a8e2-aa1ae3a0afec`

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
    "traza_id": "e5852600-41d8-45db-a8e2-aa1ae3a0afec"
  }
}
```

### ALI-03 · Ventas por producto · PASA

**Objetivo.** Lo consume surtido: unidades y venta de cada producto, sin cancelados.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/ventas?por_pagina=5`

```http
Accept: application/json
X-Traza-Id: c32313cd-2897-4d27-bb26-26bfb869f4d3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 107 ms · traza `c32313cd-2897-4d27-bb26-26bfb869f4d3`

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
      "producto_id": 19,
      "unidades": 44,
      "venta": 1848.0,
      "pedidos": 28
    },
    {
      "producto_id": 16,
      "unidades": 43,
      "venta": 709.5,
      "pedidos": 21
    },
    {
      "producto_id": 23,
      "unidades": 43,
      "venta": 1655.5,
      "pedidos": 25
    },
    {
      "producto_id": 31,
      "unidades": 42,
      "venta": 2436.0,
      "pedidos": 22
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
X-Traza-Id: 810e9ad6-003f-42db-8c04-fc96671b55ba
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 9 ms · traza `810e9ad6-003f-42db-8c04-fc96671b55ba`

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
    "traza_id": "810e9ad6-003f-42db-8c04-fc96671b55ba"
  }
}
```

### ALI-05 · Pedidos listos de un microhub · PASA

**Objetivo.** Con las coordenadas de entrega: lo que rutas agrupa y ordena.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/listos?microhub_id=1`

```http
Accept: application/json
X-Traza-Id: 1d73ec30-5787-423a-a0d5-e4e53dbe2e45
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 83 ms · traza `1d73ec30-5787-423a-a0d5-e4e53dbe2e45`

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
X-Traza-Id: d465479f-23c3-4716-9592-6d40fdc9034f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 62 ms · traza `d465479f-23c3-4716-9592-6d40fdc9034f`

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
X-Traza-Id: f4f46e54-1aa4-4d72-a3c2-c63cf76b08e3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 90 ms · traza `f4f46e54-1aa4-4d72-a3c2-c63cf76b08e3`

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
X-Traza-Id: 0a8f3c5a-a9da-45cd-b5dd-1a76329c1eeb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 6 ms · traza `0a8f3c5a-a9da-45cd-b5dd-1a76329c1eeb`

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
    "traza_id": "0a8f3c5a-a9da-45cd-b5dd-1a76329c1eeb"
  }
}
```

## Servicio demanda · puerto 5115

### DEM-01 · Observaciones de demanda · PASA

**Objetivo.** Pedidos por día, zona y categoría, con la fuente de cada dato.

**Petición.** `GET http://demanda:5115/api/v1/demanda/observaciones?nivel=total&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 021ca66b-899b-44c9-9599-06811e25d571
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 1367 ms · traza `021ca66b-899b-44c9-9599-06811e25d571`

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
X-Traza-Id: f779035c-2075-4bbe-9a4b-c7b45707dc36
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 1173 ms · traza `f779035c-2075-4bbe-9a4b-c7b45707dc36`

```xml
<?xml version='1.0' encoding='utf-8'?>
<observaciones_demanda xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><datos><observacion><fecha>2026-11-25</fecha><zona><id>1</id><nombre>San Bernabé Centro</nombre></zona><categoria xsi:nil="true" /><pedidos>17</pedidos><unidades>88</unidades><venta>2423.70</venta><clientes>14</clientes><no_atendidos>1</no_atendidos><fuente>sintetica</fuente></observacion><observacion><fecha>2026-11-25</fecha><zona><id>1</id><nombre>San Bernabé Centro</nombre></zona><categoria><id>1</id><nombre>Abarrote básico</nombre></categoria><pedidos>17</pedidos><unidades>40</unidades><venta>1090.67</venta><clientes>0</clientes><no_atendidos>0</no_atendidos><fuente>sintetica</fuente></observacion><observacion><fecha>2026-11-25</fecha><zona><id>1</id><nombre>San Bernabé Centro</nombre></zona><categoria><id>2</id><nombre>Bebidas</nombre></categoria><pedidos>7</pedidos><unidades>18</unidades><venta>484.74</venta><clientes>0</clientes><no_atendidos>0</no_atendidos><fuente>sintetica</fuente></observacion></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>1440</total><paginas>480</paginas></paginacion></observaciones_demanda>
```

### DEM-03 · Fuente desconocida · PASA

**Objetivo.** Un filtro desconocido se rechaza.

**Petición.** `GET http://demanda:5115/api/v1/demanda/observaciones?fuente=inventada`

```http
Accept: application/json
X-Traza-Id: 7572d503-4f39-4425-b5c6-13639bd2e34b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 47 ms · traza `7572d503-4f39-4425-b5c6-13639bd2e34b`

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
    "traza_id": "7572d503-4f39-4425-b5c6-13639bd2e34b"
  }
}
```

### DEM-04 · El operador consulta la demanda · PASA

**Objetivo.** Sin demanda.ver.

**Petición.** `GET http://demanda:5115/api/v1/demanda/observaciones`

```http
Accept: application/json
X-Traza-Id: b29b7ea5-4413-40f0-9c4a-2fbea83e7cb9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 27 ms · traza `b29b7ea5-4413-40f0-9c4a-2fbea83e7cb9`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "b29b7ea5-4413-40f0-9c4a-2fbea83e7cb9"
  }
}
```

### DEM-05 · Resumen por zona · PASA

**Objetivo.** Pedidos, ticket promedio, pedidos por cliente y demanda no atendida.

**Petición.** `GET http://demanda:5115/api/v1/demanda/resumen`

```http
Accept: application/json
X-Traza-Id: 55b64be6-403f-4adf-9052-df1a04ffae05
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 112 ms · traza `55b64be6-403f-4adf-9052-df1a04ffae05`

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
X-Traza-Id: d0d3d642-84e3-4a9f-9b1d-c90dc3c22c27
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 95 ms · traza `d0d3d642-84e3-4a9f-9b1d-c90dc3c22c27`

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
X-Traza-Id: dd737421-17f4-4f84-83d4-eca4a6345482
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 72 ms · traza `dd737421-17f4-4f84-83d4-eca4a6345482`

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
X-Traza-Id: 1b35721b-f3b8-42d3-8277-cdf5d60985fb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 82 ms · traza `1b35721b-f3b8-42d3-8277-cdf5d60985fb`

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
X-Traza-Id: 224af3bc-8e26-490e-8c92-3a5a95671fda
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 48 ms · traza `224af3bc-8e26-490e-8c92-3a5a95671fda`

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
    "traza_id": "224af3bc-8e26-490e-8c92-3a5a95671fda"
  }
}
```

### DEM-10 · Comparación contra lo observado · PASA

**Objetivo.** Se ocultan los últimos 7 días, se proyectan y se miden el error y el sesgo.

**Petición.** `GET http://demanda:5115/api/v1/demanda/comparacion`

```http
Accept: application/json
X-Traza-Id: cb36a4ef-258a-466c-8a0f-71e3e18310f4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 98 ms · traza `cb36a4ef-258a-466c-8a0f-71e3e18310f4`

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
X-Traza-Id: e96f8bd8-f06c-4f1b-b2f5-66b7574211d8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 1266 ms · traza `e96f8bd8-f06c-4f1b-b2f5-66b7574211d8`

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
X-Traza-Id: 41370c1d-fee8-4749-be57-9b35b0bd0ffb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 140 ms · traza `41370c1d-fee8-4749-be57-9b35b0bd0ffb`

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
X-Traza-Id: 1d3e4613-78e2-4056-9763-24bda153ea77
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{
  "desde": "2026-11-24",
  "hasta": "2026-11-26"
}
```

**Respuesta.** HTTP 403 (esperado 403) · 38 ms · traza `1d3e4613-78e2-4056-9763-24bda153ea77`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "1d3e4613-78e2-4056-9763-24bda153ea77"
  }
}
```

### DEM-14 · Sincronizar con pedidos reales · PASA

**Objetivo.** Lo sintético del rango se reemplaza por lo real.

**Petición.** `POST http://demanda:5115/api/v1/demanda/sincronizacion`

```http
Accept: application/json
X-Traza-Id: f503c5d1-857c-4bb9-9110-adb1e4f6da9a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "desde": "2026-11-24",
  "hasta": "2026-11-26"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 140 ms · traza `f503c5d1-857c-4bb9-9110-adb1e4f6da9a`

```json
{
  "desde": "2026-11-24",
  "hasta": "2026-11-26",
  "filas_escritas": 8,
  "pedidos_leidos": 201,
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
X-Traza-Id: 1d7dec2f-6532-431b-bdc0-48dd026ecaef
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "desde": "2026-10-10",
  "hasta": "2026-10-01"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 6 ms · traza `1d7dec2f-6532-431b-bdc0-48dd026ecaef`

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
    "traza_id": "1d7dec2f-6532-431b-bdc0-48dd026ecaef"
  }
}
```

### DEM-16 · Sincronizar (XML) · PASA

**Objetivo.** El cuerpo XML se valida contra demanda.xsd antes de procesarse.

**Petición.** `POST http://demanda:5115/api/v1/demanda/sincronizacion`

```http
Accept: application/xml
X-Traza-Id: e19d15ac-68e8-4881-bfa0-078f3dda44b4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><sincronizacion_nueva xmlns="urn:microhubs:v1"><desde>2026-11-26</desde><hasta>2026-11-26</hasta></sincronizacion_nueva>
```

**Respuesta.** HTTP 201 (esperado 201) · 275 ms · traza `e19d15ac-68e8-4881-bfa0-078f3dda44b4`

```xml
<?xml version='1.0' encoding='utf-8'?>
<sincronizacion xmlns="urn:microhubs:v1" version="1"><desde>2026-11-26</desde><hasta>2026-11-26</hasta><filas_escritas>4</filas_escritas><pedidos_leidos>145</pedidos_leidos><sinteticas_reemplazadas>0</sinteticas_reemplazadas></sincronizacion>
```

### DEM-17 · Supuestos de la demanda · PASA

**Objetivo.** Valor, origen (medido, supuesto o normativo), justificación y cómo calibrarlo.

**Petición.** `GET http://demanda:5115/api/v1/demanda/supuestos`

```http
Accept: application/json
X-Traza-Id: ffec6cc9-9227-40c7-969a-61911d923b6e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 35 ms · traza `ffec6cc9-9227-40c7-969a-61911d923b6e`

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
X-Traza-Id: c1f4a75f-20a0-452c-b02b-1225f60a50a9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 47 ms · traza `c1f4a75f-20a0-452c-b02b-1225f60a50a9`

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
X-Traza-Id: bd837d8e-9261-4d59-9a6e-214445750ef8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 49 ms · traza `bd837d8e-9261-4d59-9a6e-214445750ef8`

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
X-Traza-Id: 5521c101-40ff-49e1-9040-210dad785165
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 50 ms · traza `5521c101-40ff-49e1-9040-210dad785165`

```xml
<?xml version='1.0' encoding='utf-8'?>
<cobertura_resumen xmlns="urn:microhubs:v1" version="1"><zonas>4</zonas><zonas_cubiertas>4</zonas_cubiertas><pct_zonas>100</pct_zonas><hogares>6709</hogares><hogares_cubiertos>6709</hogares_cubiertos><pct_hogares>100</pct_hogares><tiempo_promedio_min>5.5</tiempo_promedio_min><dentro_promesa_pct>100</dentro_promesa_pct><zonas_solapadas>3</zonas_solapadas><zonas_sin_cobertura /><microhubs_activos>3</microhubs_activos><supuestos_usados><supuesto><clave>factor_rodeo_distancia</clave><valor>1.3</valor><modificado>false</modificado></supuesto><supuesto><clave>velocidad_reparto_kmh</clave><valor>22</valor><modificado>false</modificado></supuesto><supuesto><clave>tiempo_servicio_min</clave><valor>4</valor><modificado>false</modificado></supuesto><supuesto><clave>cob_tiempo_max_min</clave><valor>30</valor><modificado>false</modificado></supuesto><supuesto><clave>cob_solape_max_pct</clave><valor>40</valor><modificado>false</modificado></supuesto><supuesto><clave>tamano_hogar</clave><valor>3.6</valor><modificado>false</modificado></supuesto></supuestos_usados></cobertura_resumen>
```

### COB-04 · Un punto junto a un microhub · PASA

**Objetivo.** Qué microhubs lo cubren y a qué distancia.

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/punto?latitud=25.748&longitud=-100.364`

```http
Accept: application/json
X-Traza-Id: 72ae07ed-c590-437d-b19e-b78ff4d08d53
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 654 ms · traza `72ae07ed-c590-437d-b19e-b78ff4d08d53`

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
X-Traza-Id: 113668e3-6b0c-4831-86ce-f9cc3c99e59b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 76 ms · traza `113668e3-6b0c-4831-86ce-f9cc3c99e59b`

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
X-Traza-Id: 7aad0f78-f983-48cf-a0ed-7657d473d512
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 9 ms · traza `7aad0f78-f983-48cf-a0ed-7657d473d512`

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
    "traza_id": "7aad0f78-f983-48cf-a0ed-7657d473d512"
  }
}
```

### COB-07 · Ubicaciones candidatas con ranking · PASA

**Objetivo.** Cada candidata de planeación frente a la red actual.

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/candidatos`

```http
Accept: application/json
X-Traza-Id: f3e4f471-616d-40ce-84ac-dcae357fc804
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 186 ms · traza `f3e4f471-616d-40ce-84ac-dcae357fc804`

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
        "id": 143,
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
      "ranking": 9
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
      "ranking": 10
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
      "ranking": 11
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
      "ranking": 12
    },
    {
      "candidato": {
        "id": 141,
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
      "ranking": 13
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
      "ranking": 14
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
      "ranking": 15
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
      "ranking": 16
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
      "ranking": 17
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
      "ranking": 18
    },
    {
      "candidato": {
        "id": 160,
        "clave": "********",
        "nombre": "Ubicación del flujo C81FE"
      },
      "latitud": 25.760195,
      "longitud": -100.370891,
      "radio_km": 1.5,
      "zonas_nuevas": 0,
      "hogares_nuevos": 0,
      "hogares_con_mejor_tiempo": 0,
      "minutos_ahorrados": 0.0,
      "solapamiento_pct": 100.0,
      "canibaliza": true,
      "minutos_promedio": 7.1,
      "costo_ultima_milla": 21.43,
      "ranking": 19
    },
    {
      "candidato": {
        "id": 161,
        "clave": "********",
        "nombre": "Ubicación del flujo E0FDE"
      },
      "latitud": 25.760195,
      "longitud": -100.370891,
      "radio_km": 1.5,
      "zonas_nuevas": 0,
      "hogares_nuevos": 0,
      "hogares_con_mejor_tiempo": 0,
      "minutos_ahorrados": 0.0,
      "solapamiento_pct": 100.0,
      "canibaliza": true,
      "minutos_promedio": 7.1,
      "costo_ultima_milla": 21.43,
      "ranking": 20
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
X-Traza-Id: 8099559f-823a-4686-9c2e-eb3a9c3a2a0c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "candidato_id": 3
}
```

**Respuesta.** HTTP 200 (esperado 200) · 75 ms · traza `8099559f-823a-4686-9c2e-eb3a9c3a2a0c`

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
X-Traza-Id: bd070de3-7342-4a0c-810d-16b497593b4c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{
  "candidato_id": 3,
  "guardar": true
}
```

**Respuesta.** HTTP 403 (esperado 403) · 73 ms · traza `bd070de3-7342-4a0c-810d-16b497593b4c`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Guardar una evaluación exige el permiso planeacion.editar.",
    "traza_id": "bd070de3-7342-4a0c-810d-16b497593b4c"
  }
}
```

### COB-10 · Guardar la evaluación · PASA

**Objetivo.** Queda en cobertura_evaluacion con su resultado completo.

**Petición.** `POST http://cobertura:5116/api/v1/cobertura/evaluaciones`

```http
Accept: application/json
X-Traza-Id: 27399fa2-2636-4fd4-afb0-33f752aeb928
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

**Respuesta.** HTTP 201 (esperado 201) · 119 ms · traza `27399fa2-2636-4fd4-afb0-33f752aeb928`

```json
{
  "id": 24,
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
    "id": 24,
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
X-Traza-Id: d73972e3-b0e9-449d-b096-eeff60d6a8b9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 49 ms · traza `d73972e3-b0e9-449d-b096-eeff60d6a8b9`

```json
{
  "datos": [
    {
      "id": 24,
      "nombre": "Evidencia Ola 2",
      "zonas_nuevas": 0,
      "hogares_nuevos": 0,
      "solapamiento_pct": 0.0,
      "canibaliza": false,
      "creado_por": 5,
      "creado_en": "2026-11-26T15:23:21-06:00"
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

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/evaluaciones/24`

```http
Accept: application/json
X-Traza-Id: 13ae0749-a74f-4305-beff-e8c10cafd7cc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 26 ms · traza `13ae0749-a74f-4305-beff-e8c10cafd7cc`

```json
{
  "id": 24,
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
X-Traza-Id: 9a8ec9dc-3203-4784-ba22-cff2b84f3ea9
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

**Respuesta.** HTTP 200 (esperado 200) · 54 ms · traza `9a8ec9dc-3203-4784-ba22-cff2b84f3ea9`

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
X-Traza-Id: 4189e77e-9848-4441-9a06-2341512f0be6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "radio_km": 2
}
```

**Respuesta.** HTTP 422 (esperado 422) · 9 ms · traza `4189e77e-9848-4441-9a06-2341512f0be6`

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
    "traza_id": "4189e77e-9848-4441-9a06-2341512f0be6"
  }
}
```

### COB-13 · Escenarios de radio y de rodeo · PASA

**Objetivo.** Cuánto cubre la red con otros radios y otro factor de calle.

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/escenarios?radios=0.5,1,1.5,2&rodeos=1.2,1.5`

```http
Accept: application/json
X-Traza-Id: 162a223f-7360-40e8-b61c-a50833921bcb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 47 ms · traza `162a223f-7360-40e8-b61c-a50833921bcb`

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
X-Traza-Id: 7afddbdf-b2f9-4a6e-95e1-b25eb56915d6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "poblacion": 8520,
  "fuente": "INEGI, Censo 2020, AGEB de prueba"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 64 ms · traza `7afddbdf-b2f9-4a6e-95e1-b25eb56915d6`

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
      "actualizado_en": "2026-11-26T14:25:13.500982-06:00"
    },
    "valores_nuevos": {
      "fuente": "INEGI, Censo 2020, AGEB de prueba",
      "poblacion": 8520,
      "actualizado_en": "2026-11-26T15:23:21.372967-06:00"
    }
  }
]
```

### COB-15 · Corregir la población sin permiso · PASA

**Objetivo.** Es del planeador.

**Petición.** `PUT http://cobertura:5116/api/v1/cobertura/zonas/1/poblacion`

```http
Accept: application/json
X-Traza-Id: ad075e6a-4bc7-4e1e-b62a-aa0f60f4f8d2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "poblacion": 1,
  "fuente": "Sin permiso"
}
```

**Respuesta.** HTTP 403 (esperado 403) · 27 ms · traza `ad075e6a-4bc7-4e1e-b62a-aa0f60f4f8d2`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "ad075e6a-4bc7-4e1e-b62a-aa0f60f4f8d2"
  }
}
```

### COB-16 · Supuestos de la cobertura · PASA

**Objetivo.** Rodeo, velocidad, tiempo de servicio, promesa de entrega y tamaño del hogar.

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/supuestos`

```http
Accept: application/json
X-Traza-Id: bf2da3a7-979d-45a7-95b2-3145ac81cf5f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 32 ms · traza `bf2da3a7-979d-45a7-95b2-3145ac81cf5f`

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
X-Traza-Id: d0e38d35-d95c-45c8-bfd1-185118c3559a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 48 ms · traza `d0e38d35-d95c-45c8-bfd1-185118c3559a`

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
      "actualizado_en": "2026-11-26T14:25:16-06:00"
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
    },
    {
      "microhub": {
        "id": 8,
        "nombre": "Microhub C81FE"
      },
      "operadores": 2,
      "repartidores": 2,
      "capacidad_fisica": 120,
      "actualizado_en": "2026-11-26T15:21:14-06:00"
    },
    {
      "microhub": {
        "id": 9,
        "nombre": "Microhub E0FDE"
      },
      "operadores": 2,
      "repartidores": 2,
      "capacidad_fisica": 120,
      "actualizado_en": "2026-11-26T15:21:58-06:00"
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
  },
  {
    "microhub_id": 8,
    "operadores": 2,
    "repartidores": 2,
    "capacidad_fisica": 120
  },
  {
    "microhub_id": 9,
    "operadores": 2,
    "repartidores": 2,
    "capacidad_fisica": 120
  }
]
```

### CAP-02 · El operador pide otro microhub · PASA

**Objetivo.** Solo ve los recursos del suyo.

**Petición.** `GET http://capacidad:5117/api/v1/capacidad/recursos/2`

```http
Accept: application/json
X-Traza-Id: c0326b87-272c-4aaa-a28f-45796b578a63
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 517 ms · traza `c0326b87-272c-4aaa-a28f-45796b578a63`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "c0326b87-272c-4aaa-a28f-45796b578a63"
  }
}
```

### CAP-03 · Capacidad con una carga dada · PASA

**Objetivo.** Capacidad por etapa, utilización, cuello de botella y personal requerido.

**Petición.** `GET http://capacidad:5117/api/v1/capacidad/microhubs/1?carga_dia=60`

```http
Accept: application/json
X-Traza-Id: f683fab6-3946-4748-9149-37a0b9567837
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 66 ms · traza `f683fab6-3946-4748-9149-37a0b9567837`

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
X-Traza-Id: b06569c8-e2a4-4826-b732-a21cace066f5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 73 ms · traza `b06569c8-e2a4-4826-b732-a21cace066f5`

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
    },
    {
      "microhub": {
        "id": 8,
        "nombre": "Microhub C81FE"
      },
      "operadores": 2,
      "repartidores": 2,
      "capacidad_fisica": 120,
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
    },
    {
      "microhub": {
        "id": 9,
        "nombre": "Microhub E0FDE"
      },
      "operadores": 2,
      "repartidores": 2,
      "capacidad_fisica": 120,
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
    "total": 6,
    "paginas": 1
  }
}
```

### CAP-04 · Un microhub saturado · PASA

**Objetivo.** Con 95 % de la capacidad el nivel es de riesgo (umbral 85 %).

**Petición.** `GET http://capacidad:5117/api/v1/capacidad/microhubs/1?carga_dia=140`

```http
Accept: application/json
X-Traza-Id: 5c244367-7581-4095-8035-2fbaddbc7dd3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 56 ms · traza `5c244367-7581-4095-8035-2fbaddbc7dd3`

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
X-Traza-Id: fc9e1762-5ece-43eb-9ef4-9d936cd44541
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 41 ms · traza `fc9e1762-5ece-43eb-9ef4-9d936cd44541`

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
    "traza_id": "fc9e1762-5ece-43eb-9ef4-9d936cd44541"
  }
}
```

### CAP-06 · Capacidad (XML) · PASA

**Objetivo.** Respuesta XML que cumple capacidad.xsd.

**Petición.** `GET http://capacidad:5117/api/v1/capacidad/microhubs/1?carga_dia=60`

```http
Accept: application/xml
X-Traza-Id: 8a8c3544-b00f-407b-bc85-f5d5fc2a29fb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 53 ms · traza `8a8c3544-b00f-407b-bc85-f5d5fc2a29fb`

```xml
<?xml version='1.0' encoding='utf-8'?>
<capacidad_microhub xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><operadores>3</operadores><repartidores>3</repartidores><capacidad_fisica>150</capacidad_fisica><horas>10</horas><distancia_km>2.4</distancia_km><carga_dia>60</carga_dia><capacidad_hora>16.36</capacidad_hora><capacidad_dia>150</capacidad_dia><utilizacion_pct>40</utilizacion_pct><nivel>estable</nivel><utilizacion_pico_pct>49.5</utilizacion_pico_pct><nivel_pico>estable</nivel_pico><cuello_botella>espacio físico</cuello_botella><minutos_por_pedido_operacion>11</minutos_por_pedido_operacion><minutos_por_entrega>8.4</minutos_por_entrega><etapas><etapa><etapa>picking</etapa><minutos_por_pedido>6</minutos_por_pedido><pct_tiempo>54.5</pct_tiempo><capacidad_hora>30</capacidad_hora></etapa><etapa><etapa>empaque</etapa><minutos_por_pedido>3</minutos_por_pedido><pct_tiempo>27.3</pct_tiempo><capacidad_hora>60</capacidad_hora></etapa><etapa><etapa>despacho</etapa><minutos_por_pedido>2</minutos_por_pedido><pct_tiempo>18.2</pct_tiempo><capacidad_hora>90</capacidad_hora></etapa><etapa><etapa>reparto</etapa><minutos_por_pedido>8.4</minutos_por_pedido><pct_tiempo xsi:nil="true" /><capacidad_hora>21.5</capacidad_hora></etapa></etapas><operadores_requeridos>2</operadores_requeridos><repartidores_requeridos>1</repartidores_requeridos><holgura_pedidos_dia>90</holgura_pedidos_dia><formula>3 operadores × 5.45 pedidos/h combinados; 3 repartidores × 7.17 entregas/h</formula><supuestos_usados><supuesto><clave>umbral_utilizacion_estable</clave><valor>70</valor><modificado>false</modificado></supuesto><supuesto><clave>umbral_utilizacion_riesgo</clave><valor>85</valor><modificado>false</modificado></supuesto><supuesto><clave>cap_factor_pico</clave><valor>1.35</valor><modificado>false</modificado></supuesto><supuesto><clave>picking_pedidos_hora</clave><valor>10</valor><modificado>false</modificado></supuesto><supuesto><clave>packing_pedidos_hora</clave><valor>20</valor><modificado>false</modificado></supuesto><supuesto><clave>despacho_pedidos_hora</clave><valor>30</valor><modificado>false</modificado></supuesto><supuesto><clave>velocidad_reparto_kmh</clave><valor>22</valor><modificado>false</modificado></supuesto><supuesto><clave>tiempo_servicio_min</clave><valor>4</valor><modificado>false</modificado></supuesto><supuesto><clave>paradas_por_viaje</clave><valor>3</valor><modificado>false</modificado></supuesto></supuestos_usados></capacidad_microhub>
```

### CAP-07 · Simular más personal · PASA

**Objetivo.** Qué pasa con 120 pedidos al día y 6 operadores y 6 repartidores.

**Petición.** `POST http://capacidad:5117/api/v1/capacidad/simulaciones`

```http
Accept: application/json
X-Traza-Id: e441d0c1-44b2-4771-8909-a0e81223c21a
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

**Respuesta.** HTTP 200 (esperado 200) · 52 ms · traza `e441d0c1-44b2-4771-8909-a0e81223c21a`

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
X-Traza-Id: 58674914-fb9c-438a-9c44-fe5ae4e55958
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 81 ms · traza `58674914-fb9c-438a-9c44-fe5ae4e55958`

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
X-Traza-Id: d97dcc05-8643-4017-b91e-e15a90f441fd
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

**Respuesta.** HTTP 200 (esperado 200) · 94 ms · traza `d97dcc05-8643-4017-b91e-e15a90f441fd`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "operadores": 4,
  "repartidores": 3,
  "capacidad_fisica": 150,
  "actualizado_en": "2026-11-26T15:23:22-06:00"
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
      "actualizado_en": "2026-11-26T14:25:16.932509-06:00"
    },
    "valores_nuevos": {
      "operadores": 4,
      "actualizado_en": "2026-11-26T15:23:22.624323-06:00"
    }
  }
]
```

### CAP-10 · Cambiar el personal sin permiso · PASA

**Objetivo.** El operador no tiene capacidad.editar.

**Petición.** `PUT http://capacidad:5117/api/v1/capacidad/recursos/1`

```http
Accept: application/json
X-Traza-Id: 6f25e2cc-a86c-4fda-bc9f-0f106560334a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "operadores": 9,
  "repartidores": 9
}
```

**Respuesta.** HTTP 403 (esperado 403) · 64 ms · traza `6f25e2cc-a86c-4fda-bc9f-0f106560334a`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "6f25e2cc-a86c-4fda-bc9f-0f106560334a"
  }
}
```

### CAP-11 · Personal inválido · PASA

**Objetivo.** Al menos un operador.

**Petición.** `PUT http://capacidad:5117/api/v1/capacidad/recursos/1`

```http
Accept: application/json
X-Traza-Id: a7f6b755-1901-43d8-b9db-7a59079da367
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "operadores": 0,
  "repartidores": 3
}
```

**Respuesta.** HTTP 422 (esperado 422) · 9 ms · traza `a7f6b755-1901-43d8-b9db-7a59079da367`

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
    "traza_id": "a7f6b755-1901-43d8-b9db-7a59079da367"
  }
}
```

### CAP-12 · Supuestos de la capacidad · PASA

**Objetivo.** Productividad por etapa, umbrales y horas del turno.

**Petición.** `GET http://capacidad:5117/api/v1/capacidad/supuestos`

```http
Accept: application/json
X-Traza-Id: 179dfc23-6e74-48b9-80c8-a28ba817713b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 42 ms · traza `179dfc23-6e74-48b9-80c8-a28ba817713b`

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
X-Traza-Id: 6703b2fa-9bbf-4bea-91d4-f208aeec86fd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 922 ms · traza `6703b2fa-9bbf-4bea-91d4-f208aeec86fd`

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
X-Traza-Id: ecb2e4f4-e84c-4533-ac97-4c0d8db08699
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 34 ms · traza `ecb2e4f4-e84c-4533-ac97-4c0d8db08699`

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
X-Traza-Id: 55428802-e78f-4f11-a34f-c92a48b32808
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 56 ms · traza `55428802-e78f-4f11-a34f-c92a48b32808`

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
X-Traza-Id: c0a486d3-94b0-490b-bd1b-3239f4433145
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 55 ms · traza `c0a486d3-94b0-490b-bd1b-3239f4433145`

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
X-Traza-Id: 7ff1a56f-dd0a-49a7-8376-d3d1e5022195
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 52 ms · traza `7ff1a56f-dd0a-49a7-8376-d3d1e5022195`

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
X-Traza-Id: 6bc7b2c6-77c2-4031-afb0-10e2d9f7fdc6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 60 ms · traza `6bc7b2c6-77c2-4031-afb0-10e2d9f7fdc6`

```xml
<?xml version='1.0' encoding='utf-8'?>
<costos_unitarios xmlns="urn:microhubs:v1" version="1"><entrada><ambito>microhub</ambito><ambito_id>1</ambito_id><origen>costos</origen><pedidos_mes>1800</pedidos_mes><ticket>135.00</ticket><margen_bruto>0.28</margen_bruto><distancia_km>2.4</distancia_km><paradas_por_viaje>3</paradas_por_viaje><valores_modificados /></entrada><fijos_mes>69500.00</fijos_mes><costo_fijo_pedido>38.61</costo_fijo_pedido><variable_pedido>3.50</variable_pedido><comision_pedido>3.92</comision_pedido><costo_entrega>25.20</costo_entrega><costo_variable_pedido>32.62</costo_variable_pedido><costo_por_pedido>71.23</costo_por_pedido><supuestos_usados><supuesto><clave>pedidos_mes</clave><valor>1800</valor><modificado>false</modificado></supuesto><supuesto><clave>ticket</clave><valor>135</valor><modificado>false</modificado></supuesto><supuesto><clave>margen_bruto</clave><valor>0.28</valor><modificado>false</modificado></supuesto><supuesto><clave>distancia_km</clave><valor>2.4</valor><modificado>false</modificado></supuesto><supuesto><clave>paradas_por_viaje</clave><valor>3</valor><modificado>false</modificado></supuesto><supuesto><clave>costo_base_entrega</clave><valor>18</valor><modificado>false</modificado></supuesto><supuesto><clave>costo_km_reparto</clave><valor>4.5</valor><modificado>false</modificado></supuesto></supuestos_usados></costos_unitarios>
```

### COS-07 · El operador consulta costos · PASA

**Objetivo.** Sin costos.ver.

**Petición.** `GET http://costos:5119/api/v1/costos/conceptos`

```http
Accept: application/json
X-Traza-Id: 75e3d59d-0137-40f8-9e0e-f1fc6e0d3264
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 31 ms · traza `75e3d59d-0137-40f8-9e0e-f1fc6e0d3264`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "75e3d59d-0137-40f8-9e0e-f1fc6e0d3264"
  }
}
```

### COS-08 · Alta de un concepto sin permiso · PASA

**Objetivo.** Un auditor consulta, no edita.

**Petición.** `POST http://costos:5119/api/v1/costos/conceptos`

```http
Accept: application/json
X-Traza-Id: 6e1e896b-0f05-4dad-a748-d34072ff199c
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

**Respuesta.** HTTP 403 (esperado 403) · 35 ms · traza `6e1e896b-0f05-4dad-a748-d34072ff199c`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "6e1e896b-0f05-4dad-a748-d34072ff199c"
  }
}
```

### COS-09 · Alta de un concepto · PASA

**Objetivo.** Costo fijo de un microhub con su justificación.

**Petición.** `POST http://costos:5119/api/v1/costos/conceptos`

```http
Accept: application/json
X-Traza-Id: 3df0b692-0b59-444b-b338-62be1e90f0ed
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

**Respuesta.** HTTP 201 (esperado 201) · 70 ms · traza `3df0b692-0b59-444b-b338-62be1e90f0ed`

```json
{
  "id": 67,
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
    "id": 67,
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

**Petición.** `PUT http://costos:5119/api/v1/costos/conceptos/67`

```http
Accept: application/json
X-Traza-Id: 20489e0a-8e78-48b5-94b4-d0361b489490
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "monto": 1800.0,
  "justificacion": "Se ajustó el monto en la evidencia"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 81 ms · traza `20489e0a-8e78-48b5-94b4-d0361b489490`

```json
{
  "id": 67,
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

**Petición.** `PATCH http://costos:5119/api/v1/costos/conceptos/67`

```http
Accept: application/json
X-Traza-Id: 2ad0c16d-068e-433b-b30b-dc1d55b3804a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "monto": 1900.0,
  "justificacion": "Segundo ajuste del monto en la evidencia"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 100 ms · traza `2ad0c16d-068e-433b-b30b-dc1d55b3804a`

```json
{
  "id": 67,
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

**Petición.** `DELETE http://costos:5119/api/v1/costos/conceptos/67`

```http
Accept: application/json
X-Traza-Id: 3c2d51c6-e3c6-4c00-9acc-1eeea785c4bc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 44 ms · traza `3c2d51c6-e3c6-4c00-9acc-1eeea785c4bc`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT id, estatus FROM costo_concepto WHERE id = %s`

```json
[
  {
    "id": 67,
    "estatus": "inactivo"
  }
]
```

### COS-12 · Fijo con unidad variable · PASA

**Objetivo.** Un costo fijo se da por mes.

**Petición.** `POST http://costos:5119/api/v1/costos/conceptos`

```http
Accept: application/json
X-Traza-Id: 5ba06696-9559-4399-b74c-2f915f65c6c8
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

**Respuesta.** HTTP 422 (esperado 422) · 6 ms · traza `5ba06696-9559-4399-b74c-2f915f65c6c8`

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
    "traza_id": "5ba06696-9559-4399-b74c-2f915f65c6c8"
  }
}
```

### COS-13 · Microhub inexistente · PASA

**Objetivo.** El ámbito debe existir.

**Petición.** `POST http://costos:5119/api/v1/costos/conceptos`

```http
Accept: application/json
X-Traza-Id: b6a4e027-1577-48ad-9f59-5e615ed80bc3
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

**Respuesta.** HTTP 422 (esperado 422) · 5 ms · traza `b6a4e027-1577-48ad-9f59-5e615ed80bc3`

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
    "traza_id": "b6a4e027-1577-48ad-9f59-5e615ed80bc3"
  }
}
```

### COS-14 · Costos de una ubicación candidata · PASA

**Objetivo.** Sin conceptos propios toma renta, nómina y servicios de la ubicación (planeación).

**Petición.** `GET http://costos:5119/api/v1/costos/resumen?candidato_id=3`

```http
Accept: application/json
X-Traza-Id: 339d9352-35e5-439f-af99-fc3993100472
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 82 ms · traza `339d9352-35e5-439f-af99-fc3993100472`

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
X-Traza-Id: 636d6f9f-d0f8-45f1-88f3-af40df3326b9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 523 ms · traza `636d6f9f-d0f8-45f1-88f3-af40df3326b9`

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
X-Traza-Id: 022fd166-5b29-4316-a58e-c641fa62576a
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

**Respuesta.** HTTP 200 (esperado 200) · 30 ms · traza `022fd166-5b29-4316-a58e-c641fa62576a`

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
X-Traza-Id: 140e3ecc-1817-4923-acbc-457f1a6fa1e6
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

**Respuesta.** HTTP 200 (esperado 200) · 32 ms · traza `140e3ecc-1817-4923-acbc-457f1a6fa1e6`

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
X-Traza-Id: a603cfac-6263-48f1-8e2f-48140fc89a75
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

**Respuesta.** HTTP 200 (esperado 200) · 31 ms · traza `a603cfac-6263-48f1-8e2f-48140fc89a75`

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
X-Traza-Id: 46fa1c97-31f0-4e29-ac3c-508e603531c5
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

**Respuesta.** HTTP 200 (esperado 200) · 28 ms · traza `46fa1c97-31f0-4e29-ac3c-508e603531c5`

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
X-Traza-Id: 0bec6aec-1592-422f-a37d-5e55d1c3a53f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1
}
```

**Respuesta.** HTTP 200 (esperado 200) · 401 ms · traza `0bec6aec-1592-422f-a37d-5e55d1c3a53f`

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
X-Traza-Id: 981024f2-e298-4f79-944e-6803b1c7c291
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "ticket": 200
}
```

**Respuesta.** HTTP 200 (esperado 200) · 254 ms · traza `981024f2-e298-4f79-944e-6803b1c7c291`

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
X-Traza-Id: b1092810-c668-4576-b394-91e631454423
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "pedidos_dia": 10
}
```

**Respuesta.** HTTP 422 (esperado 422) · 142 ms · traza `b1092810-c668-4576-b394-91e631454423`

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
    "traza_id": "b1092810-c668-4576-b394-91e631454423"
  }
}
```

### EQU-08 · Sensibilidad · PASA

**Objetivo.** Cada variable sube y baja 10 y 20 %; se ordenan por lo que mueven la utilidad.

**Petición.** `POST http://punto-equilibrio:5120/api/v1/punto-equilibrio/sensibilidad`

```http
Accept: application/json
X-Traza-Id: c8b9f3d5-9e1f-4157-8b72-7c1d52c8336a
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

**Respuesta.** HTTP 200 (esperado 200) · 32 ms · traza `c8b9f3d5-9e1f-4157-8b72-7c1d52c8336a`

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
X-Traza-Id: 7b1ba69a-682c-4063-af10-295de1e15506
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><equilibrio_calculo_nuevo xmlns="urn:microhubs:v1"><pedidos_dia>45</pedidos_dia><ticket>135</ticket><margen_bruto>0.28</margen_bruto><costos_fijos>60000</costos_fijos><costo_variable_pedido>32.6</costo_variable_pedido></equilibrio_calculo_nuevo>
```

**Respuesta.** HTTP 200 (esperado 200) · 140 ms · traza `7b1ba69a-682c-4063-af10-295de1e15506`

```xml
<?xml version='1.0' encoding='utf-8'?>
<equilibrio_calculo xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id xsi:nil="true" /><nombre xsi:nil="true" /><objeto><tipo>manual</tipo><id xsi:nil="true" /><nombre xsi:nil="true" /></objeto><entrada><costos_fijos_mes>60000</costos_fijos_mes><costo_variable_pedido>32.6</costo_variable_pedido><ticket>135</ticket><margen_bruto>0.28</margen_bruto><pedidos_dia>45</pedidos_dia><dias_mes>30</dias_mes><margen_seguridad_minimo_pct>15</margen_seguridad_minimo_pct><origen><costos_fijos>manual</costos_fijos><costo_variable_pedido>manual</costo_variable_pedido><ticket>manual</ticket><margen_bruto>manual</margen_bruto><pedidos_dia>manual</pedidos_dia></origen></entrada><margen_pedido>5.2</margen_pedido><equilibrio_mensual>11538.46</equilibrio_mensual><equilibrio_diario>384.62</equilibrio_diario><ingresos_equilibrio_mes>1557692.31</ingresos_equilibrio_mes><diferencia_pedidos_dia>-339.62</diferencia_pedidos_dia><margen_seguridad_pct>-88.3</margen_seguridad_pct><utilidad_dia>-1766</utilidad_dia><utilidad_mes>-52980</utilidad_mes><decision>no_viable</decision><explicacion><motivo>la demanda esperada (45.0 pedidos/día) no alcanza el equilibrio (384.6 pedidos/día)</motivo></explicacion><pasos><paso>Margen por pedido = ticket × margen bruto − costo de entrega = 135.00 × 28.00% − 32.60 = 5.20</paso><paso>Punto de equilibrio mensual = costos fijos ÷ margen por pedido = 60,000.00 ÷ 5.20 = 11,538 pedidos/mes</paso><paso>Punto de equilibrio diario = 11,538 ÷ 30 días = 384.6 pedidos/día</paso></pasos><supuestos_usados><supuesto><clave>peq_margen_seguridad_pct</clave><valor>15</valor><modificado>false</modificado></supuesto><supuesto><clave>dias_operacion_mes</clave><valor>30</valor><modificado>false</modificado></supuesto><supuesto><clave>margen_bruto_default</clave><valor>0.28</valor><modificado>false</modificado></supuesto></supuestos_usados></equilibrio_calculo>
```

### EQU-10 · Guardar sin permiso · PASA

**Objetivo.** Guardar un escenario exige equilibrio.editar.

**Petición.** `POST http://punto-equilibrio:5120/api/v1/punto-equilibrio/calculos`

```http
Accept: application/json
X-Traza-Id: 0fbb60a1-1460-4224-a6fe-6a2bc63dd8b9
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

**Respuesta.** HTTP 403 (esperado 403) · 8 ms · traza `0fbb60a1-1460-4224-a6fe-6a2bc63dd8b9`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Guardar un escenario exige el permiso equilibrio.editar.",
    "traza_id": "0fbb60a1-1460-4224-a6fe-6a2bc63dd8b9"
  }
}
```

### EQU-11 · Guardar «Evidencia equilibrio A» · PASA

**Objetivo.** Queda en equilibrio_escenario con su cálculo completo.

**Petición.** `POST http://punto-equilibrio:5120/api/v1/punto-equilibrio/calculos`

```http
Accept: application/json
X-Traza-Id: 8ed61fac-204d-473f-bae8-519775f0469a
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

**Respuesta.** HTTP 201 (esperado 201) · 64 ms · traza `8ed61fac-204d-473f-bae8-519775f0469a`

```json
{
  "id": 46,
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
    "id": 46,
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
X-Traza-Id: f269d394-d6c1-4f42-9c1c-0a3377947338
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

**Respuesta.** HTTP 201 (esperado 201) · 82 ms · traza `f269d394-d6c1-4f42-9c1c-0a3377947338`

```json
{
  "id": 47,
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
    "id": 47,
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
X-Traza-Id: 50966d22-cd2f-4035-91fd-48196d551dd0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 972 ms · traza `50966d22-cd2f-4035-91fd-48196d551dd0`

```json
{
  "datos": [
    {
      "id": 47,
      "nombre": "Evidencia equilibrio B",
      "microhub_id": null,
      "candidato_id": null,
      "decision": "viable",
      "equilibrio_diario": 53.33,
      "pedidos_dia": 80.0,
      "utilidad_mes": 20000.0,
      "creado_por": 5,
      "creado_en": "2026-11-26T15:23:26-06:00"
    },
    {
      "id": 46,
      "nombre": "Evidencia equilibrio A",
      "microhub_id": null,
      "candidato_id": null,
      "decision": "no_viable",
      "equilibrio_diario": 53.33,
      "pedidos_dia": 45.0,
      "utilidad_mes": -6250.0,
      "creado_por": 5,
      "creado_en": "2026-11-26T15:23:26-06:00"
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

**Petición.** `GET http://punto-equilibrio:5120/api/v1/punto-equilibrio/comparacion?ids=46,47`

```http
Accept: application/json
X-Traza-Id: cf5447d5-c72e-4a32-86a6-97e1efb51ded
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 47 ms · traza `cf5447d5-c72e-4a32-86a6-97e1efb51ded`

```json
{
  "filas": [
    {
      "id": 46,
      "nombre": "Evidencia equilibrio A",
      "decision": "no_viable",
      "pedidos_dia": 45.0,
      "equilibrio_diario": 53.33,
      "diferencia_pedidos_dia": -8.33,
      "margen_seguridad_pct": -15.62,
      "utilidad_mes": -6250.0
    },
    {
      "id": 47,
      "nombre": "Evidencia equilibrio B",
      "decision": "viable",
      "pedidos_dia": 80.0,
      "equilibrio_diario": 53.33,
      "diferencia_pedidos_dia": 26.67,
      "margen_seguridad_pct": 50.0,
      "utilidad_mes": 20000.0
    }
  ],
  "mejor_utilidad_id": 47,
  "mejor_utilidad_nombre": "Evidencia equilibrio B"
}
```

### EQU-15 · Abrir un escenario · PASA

**Objetivo.** Con su cálculo paso a paso.

**Petición.** `GET http://punto-equilibrio:5120/api/v1/punto-equilibrio/escenarios/46`

```http
Accept: application/json
X-Traza-Id: 4c5868c1-9817-440c-a337-936d8e141bc4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 27 ms · traza `4c5868c1-9817-440c-a337-936d8e141bc4`

```json
{
  "id": 46,
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

**Petición.** `DELETE http://punto-equilibrio:5120/api/v1/punto-equilibrio/escenarios/46`

```http
Accept: application/json
X-Traza-Id: 3d2f3bdc-1fdd-4760-8462-5adb71e2c52f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 45 ms · traza `3d2f3bdc-1fdd-4760-8462-5adb71e2c52f`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "3d2f3bdc-1fdd-4760-8462-5adb71e2c52f"
  }
}
```

### EQU-17 · Borrar un escenario · PASA

**Objetivo.** Se elimina el escenario.

**Petición.** `DELETE http://punto-equilibrio:5120/api/v1/punto-equilibrio/escenarios/46`

```http
Accept: application/json
X-Traza-Id: 9a48cff4-049d-4071-9e70-79e656c84337
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 37 ms · traza `9a48cff4-049d-4071-9e70-79e656c84337`

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
X-Traza-Id: 4067c3ef-e9b1-4a2e-a6b8-9a0e41b41db0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 369 ms · traza `4067c3ef-e9b1-4a2e-a6b8-9a0e41b41db0`

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
X-Traza-Id: 2437b4c6-a750-42bb-b657-2fa6be4dd199
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 38 ms · traza `2437b4c6-a750-42bb-b657-2fa6be4dd199`

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
X-Traza-Id: f70442e9-12c7-4040-88d0-c67f8250d90d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 1339 ms · traza `f70442e9-12c7-4040-88d0-c67f8250d90d`

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
      "unidades": 349,
      "venta": 9697.9,
      "pct_unidades": 80.0,
      "pct_venta": 75.9
    },
    {
      "clase": "B",
      "productos": 12,
      "unidades": 66,
      "venta": 2178.5,
      "pct_unidades": 15.1,
      "pct_venta": 17.1
    },
    {
      "clase": "C",
      "productos": 7,
      "unidades": 21,
      "venta": 895.0,
      "pct_unidades": 4.8,
      "pct_venta": 7.0
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
      "pct_acum": 5.0
    },
    {
      "producto": {
        "id": 48,
        "clave_interna": "HI-003",
        "nombre": "Pasta dental"
      },
      "clase": "A",
      "unidades": 20,
      "venta": 640.0,
      "pct_acum": 9.6
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
      "pct_acum": 13.3
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
      "pct_acum": 16.7
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
      "pct_acum": 20.2
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
      "pct_acum": 23.4
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
      "pct_acum": 26.4
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
      "pct_acum": 29.4
    },
    {
      "producto": {
        "id": 8,
        "clave_interna": "AB-008",
        "nombre": "Pasta para sopa surtida"
      },
      "clase": "A",
      "unidades": 12,
      "venta": 114.0,
      "pct_acum": 32.1
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
      "pct_acum": 34.9
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
      "pct_acum": 37.6
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
      "pct_acum": 40.4
    },
    {
      "producto": {
        "id": 2,
        "clave_interna": "AB-002",
        "nombre": "Arroz superextra"
      },
      "clase": "A",
      "unidades": 11,
      "venta": 328.9,
      "pct_acum": 42.9
    },
    {
      "producto": {
        "id": 26,
        "clave_interna": "BE-006",
        "nombre": "Bebida de soya"
      },
      "clase": "A",
      "unidades": 11,
      "venta": 352.0,
      "pct_acum": 45.4
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
      "pct_acum": 47.9
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
      "pct_acum": 50.2
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
      "pct_acum": 52.3
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
      "pct_acum": 54.4
    },
    {
      "producto": {
        "id": 18,
        "clave_interna": "AB-018",
        "nombre": "Pan de caja blanco"
      },
      "clase": "A",
      "unidades": 9,
      "venta": 396.0,
      "pct_acum": 56.4
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
      "pct_acum": 58.5
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
      "pct_acum": 60.6
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
      "pct_acum": 62.4
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
      "pct_acum": 64.2
    },
    {
      "producto": {
        "id": 22,
        "clave_interna": "BE-002",
        "nombre": "Agua embotellada"
      },
      "clase": "A",
      "unidades": 8,
      "venta": 120.0,
      "pct_acum": 66.1
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
      "pct_acum": 67.9
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
      "pct_acum": 69.7
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
      "pct_acum": 71.6
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
      "pct_acum": 73.4
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
      "pct_acum": 75.2
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
      "pct_acum": 76.8
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
      "pct_acum": 78.4
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
      "pct_acum": 80.0
    },
    {
      "producto": {
        "id": 35,
        "clave_interna": "LA-007",
        "nombre": "Mantequilla"
      },
      "clase": "B",
      "unidades": 7,
      "venta": 154.0,
      "pct_acum": 81.7
    },
    {
      "producto": {
        "id": 47,
        "clave_interna": "HI-002",
        "nombre": "Shampoo"
      },
      "clase": "B",
      "unidades": 7,
      "venta": 378.0,
      "pct_acum": 83.3
    },
    {
      "producto": {
        "id": 49,
        "clave_interna": "HI-004",
        "nombre": "Desodorante"
      },
      "clase": "B",
      "unidades": 7,
      "venta": 336.0,
      "pct_acum": 84.9
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
      "pct_acum": 86.2
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
      "pct_acum": 87.6
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
      "pct_acum": 88.8
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
      "pct_acum": 89.9
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
      "pct_acum": 91.1
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
      "pct_acum": 92.2
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
      "pct_acum": 93.3
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
      "pct_acum": 94.3
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
      "pct_acum": 95.2
    },
    {
      "producto": {
        "id": 32,
        "clave_interna": "LA-004",
        "nombre": "Queso Oaxaca"
      },
      "clase": "C",
      "unidades": 4,
      "venta": 288.0,
      "pct_acum": 96.1
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
      "pct_acum": 97.0
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
      "pct_acum": 97.9
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
      "pct_acum": 98.6
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
X-Traza-Id: 64bd6a3f-fbfa-43b6-81f6-f32e45fdb681
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 355 ms · traza `64bd6a3f-fbfa-43b6-81f6-f32e45fdb681`

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
    "clase_b": 12,
    "clase_c": 7,
    "unidades_a_comprar": 1,
    "con_costo_estimado": 51,
    "espacio": {
      "total": 3600.0,
      "ocupado": 3508.0,
      "sugerido": 1.0,
      "ocupacion_pct": 97.5
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
      "pct_acum": 5.0,
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
        "id": 48,
        "clave_interna": "HI-003",
        "nombre": "Pasta dental"
      },
      "categoria": "Higiene personal",
      "clase": "A",
      "pct_acum": 9.6,
      "unidades": 20,
      "venta": 640.0,
      "margen_unitario": 8.96,
      "margen_total": 179.2,
      "costo_estimado": true,
      "existencia": 74,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.22,
      "cobertura_dias": 333.0,
      "rotacion": 0.27,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 333 días, exceso de stock",
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
      "pct_acum": 13.3,
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
      "pct_acum": 16.7,
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
      "pct_acum": 20.2,
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
        "id": 13,
        "clave_interna": "AB-013",
        "nombre": "Puré de tomate"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 23.4,
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
      "pct_acum": 26.4,
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
      "pct_acum": 29.4,
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
        "id": 8,
        "clave_interna": "AB-008",
        "nombre": "Pasta para sopa surtida"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 32.1,
      "unidades": 12,
      "venta": 114.0,
      "margen_unitario": 2.66,
      "margen_total": 31.92,
      "costo_estimado": true,
      "existencia": 21,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.13,
      "cobertura_dias": 157.5,
      "rotacion": 0.57,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 158 días, exceso de stock",
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
      "pct_acum": 34.9,
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
      "pct_acum": 37.6,
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
      "pct_acum": 40.4,
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
        "id": 2,
        "clave_interna": "AB-002",
        "nombre": "Arroz superextra"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 42.9,
      "unidades": 11,
      "venta": 328.9,
      "margen_unitario": 8.37,
      "margen_total": 92.07,
      "costo_estimado": true,
      "existencia": 36,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.12,
      "cobertura_dias": 294.5,
      "rotacion": 0.31,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 295 días, exceso de stock",
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
      "pct_acum": 45.4,
      "unidades": 11,
      "venta": 352.0,
      "margen_unitario": 8.96,
      "margen_total": 98.56,
      "costo_estimado": true,
      "existencia": 17,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.12,
      "cobertura_dias": 139.1,
      "rotacion": 0.65,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 139 días, exceso de stock",
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
      "pct_acum": 47.9,
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
      "pct_acum": 50.2,
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
        "id": 11,
        "clave_interna": "AB-011",
        "nombre": "Frijoles refritos"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 52.3,
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
      "pct_acum": 54.4,
      "unidades": 9,
      "venta": 175.5,
      "margen_unitario": 5.46,
      "margen_total": 49.14,
      "costo_estimado": true,
      "existencia": 455,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 4550.0,
      "rotacion": 0.02,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 4550 días, exceso de stock",
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
      "pct_acum": 56.4,
      "unidades": 9,
      "venta": 396.0,
      "margen_unitario": 12.32,
      "margen_total": 110.88,
      "costo_estimado": true,
      "existencia": 78,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 780.0,
      "rotacion": 0.12,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 780 días, exceso de stock",
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
      "pct_acum": 58.5,
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
      "pct_acum": 60.6,
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
      "pct_acum": 62.4,
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
      "pct_acum": 64.2,
      "unidades": 8,
      "venta": 208.0,
      "margen_unitario": 7.28,
      "margen_total": 58.24,
      "costo_estimado": true,
      "existencia": 86,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 967.5,
      "rotacion": 0.09,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 968 días, exceso de stock",
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
      "clase": "A",
      "pct_acum": 66.1,
      "unidades": 8,
      "venta": 120.0,
      "margen_unitario": 4.2,
      "margen_total": 33.6,
      "costo_estimado": true,
      "existencia": 69,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 776.2,
      "rotacion": 0.12,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 776 días, exceso de stock",
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
      "pct_acum": 67.9,
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
      "pct_acum": 69.7,
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
      "pct_acum": 71.6,
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
      "pct_acum": 73.4,
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
      "pct_acum": 75.2,
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
      "pct_acum": 76.8,
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
        "id": 10,
        "clave_interna": "AB-010",
        "nombre": "Sardina en salsa de tomate"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 78.4,
      "unidades": 7,
      "venta": 185.5,
      "margen_unitario": 7.42,
      "margen_total": 51.94,
      "costo_estimado": true,
      "existencia": 782,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 10054.3,
      "rotacion": 0.01,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 10054 días, exceso de stock",
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
      "pct_acum": 80.0,
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
        "id": 35,
        "clave_interna": "LA-007",
        "nombre": "Mantequilla"
      },
      "categoria": "Lácteos y huevo",
      "clase": "B",
      "pct_acum": 81.7,
      "unidades": 7,
      "venta": 154.0,
      "margen_unitario": 6.16,
      "margen_total": 43.12,
      "costo_estimado": true,
      "existencia": 64,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 822.9,
      "rotacion": 0.11,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 823 días, exceso de stock",
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
      "clase": "B",
      "pct_acum": 83.3,
      "unidades": 7,
      "venta": 378.0,
      "margen_unitario": 15.12,
      "margen_total": 105.84,
      "costo_estimado": true,
      "existencia": 36,
      "minimo": 10,
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
        "id": 49,
        "clave_interna": "HI-004",
        "nombre": "Desodorante"
      },
      "categoria": "Higiene personal",
      "clase": "B",
      "pct_acum": 84.9,
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
      "pct_acum": 86.2,
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
      "pct_acum": 87.6,
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
        "id": 16,
        "clave_interna": "AB-016",
        "nombre": "Galletas María"
      },
      "categoria": "Abarrote básico",
      "clase": "B",
      "pct_acum": 88.8,
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
        "id": 23,
        "clave_interna": "BE-003",
        "nombre": "Refresco de cola"
      },
      "categoria": "Bebidas",
      "clase": "B",
      "pct_acum": 89.9,
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
        "id": 41,
        "clave_interna": "LI-005",
        "nombre": "Suavizante de telas"
      },
      "categoria": "Limpieza del hogar",
      "clase": "B",
      "pct_acum": 91.1,
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
      "pct_acum": 92.2,
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
      "pct_acum": 93.3,
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
      "pct_acum": 94.3,
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
      "pct_acum": 95.2,
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
      "clase": "C",
      "pct_acum": 96.1,
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
      "pct_acum": 97.0,
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
      "pct_acum": 97.9,
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
      "pct_acum": 98.6,
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
      "existencia": 131,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.02,
      "cobertura_dias": 5895.0,
      "rotacion": 0.02,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 5895 días, exceso de stock",
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
X-Traza-Id: 1a1e7972-67e1-4954-bf21-820c197adf43
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 1303 ms · traza `1a1e7972-67e1-4954-bf21-820c197adf43`

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
      "ocupado": 7788.0,
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
      "pct_acum": 4.2,
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
        "id": 19,
        "clave_interna": "AB-019",
        "nombre": "Huevo blanco"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 7.1,
      "unidades": 44,
      "venta": 1848.0,
      "margen_unitario": 11.76,
      "margen_total": 517.44,
      "costo_estimado": true,
      "existencia": 153,
      "minimo": 21,
      "quiebres": 0,
      "demanda_dia": 0.49,
      "cobertura_dias": 313.0,
      "rotacion": 0.29,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 313 días, exceso de stock",
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
      "pct_acum": 10.0,
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
        "id": 23,
        "clave_interna": "BE-003",
        "nombre": "Refresco de cola"
      },
      "categoria": "Bebidas",
      "clase": "A",
      "pct_acum": 12.8,
      "unidades": 43,
      "venta": 1655.5,
      "margen_unitario": 10.78,
      "margen_total": 463.54,
      "costo_estimado": true,
      "existencia": 179,
      "minimo": 21,
      "quiebres": 0,
      "demanda_dia": 0.48,
      "cobertura_dias": 374.7,
      "rotacion": 0.24,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 375 días, exceso de stock",
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
      "clase": "A",
      "pct_acum": 15.6,
      "unidades": 42,
      "venta": 2436.0,
      "margen_unitario": 16.24,
      "margen_total": 682.08,
      "costo_estimado": true,
      "existencia": 279,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.47,
      "cobertura_dias": 597.9,
      "rotacion": 0.15,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 598 días, exceso de stock",
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
      "pct_acum": 18.3,
      "unidades": 41,
      "venta": 1004.5,
      "margen_unitario": 6.86,
      "margen_total": 281.26,
      "costo_estimado": true,
      "existencia": 156,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.46,
      "cobertura_dias": 342.4,
      "rotacion": 0.26,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 342 días, exceso de stock",
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
      "pct_acum": 21.0,
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
        "id": 45,
        "clave_interna": "LI-009",
        "nombre": "Fibra para trastes"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 23.6,
      "unidades": 40,
      "venta": 720.0,
      "margen_unitario": 5.04,
      "margen_total": 201.6,
      "costo_estimado": true,
      "existencia": 167,
      "minimo": 26,
      "quiebres": 0,
      "demanda_dia": 0.44,
      "cobertura_dias": 375.8,
      "rotacion": 0.24,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 376 días, exceso de stock",
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
      "pct_acum": 26.0,
      "unidades": 37,
      "venta": 1106.3,
      "margen_unitario": 8.37,
      "margen_total": 309.69,
      "costo_estimado": true,
      "existencia": 108,
      "minimo": 25,
      "quiebres": 0,
      "demanda_dia": 0.41,
      "cobertura_dias": 262.7,
      "rotacion": 0.34,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 263 días, exceso de stock",
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
      "pct_acum": 28.4,
      "unidades": 36,
      "venta": 1152.0,
      "margen_unitario": 8.96,
      "margen_total": 322.56,
      "costo_estimado": true,
      "existencia": 50,
      "minimo": 28,
      "quiebres": 2,
      "demanda_dia": 0.4,
      "cobertura_dias": 125.0,
      "rotacion": 0.72,
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
      "pct_acum": 30.8,
      "unidades": 36,
      "venta": 1152.0,
      "margen_unitario": 8.96,
      "margen_total": 322.56,
      "costo_estimado": true,
      "existencia": 165,
      "minimo": 20,
      "quiebres": 0,
      "demanda_dia": 0.4,
      "cobertura_dias": 412.5,
      "rotacion": 0.22,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 412 días, exceso de stock",
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
      "pct_acum": 33.2,
      "unidades": 36,
      "venta": 2448.0,
      "margen_unitario": 19.04,
      "margen_total": 685.44,
      "costo_estimado": true,
      "existencia": 127,
      "minimo": 20,
      "quiebres": 0,
      "demanda_dia": 0.4,
      "cobertura_dias": 317.5,
      "rotacion": 0.28,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 318 días, exceso de stock",
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
      "pct_acum": 35.5,
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
        "id": 40,
        "clave_interna": "LI-004",
        "nombre": "Limpiador multiusos"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 37.8,
      "unidades": 35,
      "venta": 980.0,
      "margen_unitario": 7.84,
      "margen_total": 274.4,
      "costo_estimado": true,
      "existencia": 71,
      "minimo": 24,
      "quiebres": 0,
      "demanda_dia": 0.39,
      "cobertura_dias": 182.6,
      "rotacion": 0.49,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 183 días, exceso de stock",
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
      "pct_acum": 40.1,
      "unidades": 34,
      "venta": 1054.0,
      "margen_unitario": 8.68,
      "margen_total": 295.12,
      "costo_estimado": true,
      "existencia": 58,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.38,
      "cobertura_dias": 153.5,
      "rotacion": 0.59,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 154 días, exceso de stock",
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
      "pct_acum": 42.2,
      "unidades": 33,
      "venta": 1270.5,
      "margen_unitario": 10.78,
      "margen_total": 355.74,
      "costo_estimado": true,
      "existencia": 158,
      "minimo": 25,
      "quiebres": 0,
      "demanda_dia": 0.37,
      "cobertura_dias": 430.9,
      "rotacion": 0.21,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 431 días, exceso de stock",
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
      "pct_acum": 44.4,
      "unidades": 33,
      "venta": 792.0,
      "margen_unitario": 6.72,
      "margen_total": 221.76,
      "costo_estimado": true,
      "existencia": 101,
      "minimo": 18,
      "quiebres": 0,
      "demanda_dia": 0.37,
      "cobertura_dias": 275.5,
      "rotacion": 0.33,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 275 días, exceso de stock",
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
      "pct_acum": 46.6,
      "unidades": 33,
      "venta": 924.0,
      "margen_unitario": 7.84,
      "margen_total": 258.72,
      "costo_estimado": true,
      "existencia": 198,
      "minimo": 15,
      "quiebres": 0,
      "demanda_dia": 0.37,
      "cobertura_dias": 540.0,
      "rotacion": 0.17,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 540 días, exceso de stock",
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
      "pct_acum": 48.8,
      "unidades": 33,
      "venta": 1452.0,
      "margen_unitario": 12.32,
      "margen_total": 406.56,
      "costo_estimado": true,
      "existencia": 84,
      "minimo": 21,
      "quiebres": 1,
      "demanda_dia": 0.37,
      "cobertura_dias": 229.1,
      "rotacion": 0.39,
      "recomendacion": "Aumentar",
      "motivo": "hubo quiebres",
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
      "pct_acum": 51.0,
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
        "id": 10,
        "clave_interna": "AB-010",
        "nombre": "Sardina en salsa de tomate"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 53.0,
      "unidades": 31,
      "venta": 821.5,
      "margen_unitario": 7.42,
      "margen_total": 230.02,
      "costo_estimado": true,
      "existencia": 888,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.34,
      "cobertura_dias": 2578.1,
      "rotacion": 0.03,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 2578 días, exceso de stock",
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
      "pct_acum": 55.1,
      "unidades": 31,
      "venta": 1674.0,
      "margen_unitario": 15.12,
      "margen_total": 468.72,
      "costo_estimado": true,
      "existencia": 146,
      "minimo": 25,
      "quiebres": 0,
      "demanda_dia": 0.34,
      "cobertura_dias": 423.9,
      "rotacion": 0.21,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 424 días, exceso de stock",
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
      "pct_acum": 57.1,
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
        "id": 8,
        "clave_interna": "AB-008",
        "nombre": "Pasta para sopa surtida"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 59.1,
      "unidades": 30,
      "venta": 285.0,
      "margen_unitario": 2.66,
      "margen_total": 79.8,
      "costo_estimado": true,
      "existencia": 107,
      "minimo": 28,
      "quiebres": 0,
      "demanda_dia": 0.33,
      "cobertura_dias": 321.0,
      "rotacion": 0.28,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 321 días, exceso de stock",
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
      "pct_acum": 61.1,
      "unidades": 30,
      "venta": 585.0,
      "margen_unitario": 5.46,
      "margen_total": 163.8,
      "costo_estimado": true,
      "existencia": 542,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.33,
      "cobertura_dias": 1626.0,
      "rotacion": 0.06,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1626 días, exceso de stock",
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
      "pct_acum": 63.1,
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
        "id": 43,
        "clave_interna": "LI-007",
        "nombre": "Servilletas"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 65.0,
      "unidades": 30,
      "venta": 960.0,
      "margen_unitario": 8.96,
      "margen_total": 268.8,
      "costo_estimado": true,
      "existencia": 116,
      "minimo": 25,
      "quiebres": 0,
      "demanda_dia": 0.33,
      "cobertura_dias": 348.0,
      "rotacion": 0.26,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 348 días, exceso de stock",
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
      "pct_acum": 67.0,
      "unidades": 29,
      "venta": 1044.0,
      "margen_unitario": 10.08,
      "margen_total": 292.32,
      "costo_estimado": true,
      "existencia": 200,
      "minimo": 20,
      "quiebres": 0,
      "demanda_dia": 0.32,
      "cobertura_dias": 620.7,
      "rotacion": 0.14,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 621 días, exceso de stock",
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
      "pct_acum": 68.9,
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
      "pct_acum": 70.8,
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
        "id": 29,
        "clave_interna": "LA-001",
        "nombre": "Leche entera"
      },
      "categoria": "Lácteos y huevo",
      "clase": "A",
      "pct_acum": 72.6,
      "unidades": 28,
      "venta": 770.0,
      "margen_unitario": 7.7,
      "margen_total": 215.6,
      "costo_estimado": true,
      "existencia": 130,
      "minimo": 25,
      "quiebres": 0,
      "demanda_dia": 0.31,
      "cobertura_dias": 417.9,
      "rotacion": 0.22,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 418 días, exceso de stock",
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
      "clase": "A",
      "pct_acum": 74.5,
      "unidades": 28,
      "venta": 2016.0,
      "margen_unitario": 20.16,
      "margen_total": 564.48,
      "costo_estimado": true,
      "existencia": 115,
      "minimo": 28,
      "quiebres": 0,
      "demanda_dia": 0.31,
      "cobertura_dias": 369.6,
      "rotacion": 0.24,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 370 días, exceso de stock",
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
      "pct_acum": 76.3,
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
        "id": 41,
        "clave_interna": "LI-005",
        "nombre": "Suavizante de telas"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 78.0,
      "unidades": 26,
      "venta": 858.0,
      "margen_unitario": 9.24,
      "margen_total": 240.24,
      "costo_estimado": true,
      "existencia": 143,
      "minimo": 24,
      "quiebres": 0,
      "demanda_dia": 0.29,
      "cobertura_dias": 495.0,
      "rotacion": 0.18,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 495 días, exceso de stock",
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
      "pct_acum": 79.7,
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
        "id": 18,
        "clave_interna": "AB-018",
        "nombre": "Pan de caja blanco"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 81.4,
      "unidades": 25,
      "venta": 1100.0,
      "margen_unitario": 12.32,
      "margen_total": 308.0,
      "costo_estimado": true,
      "existencia": 157,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.28,
      "cobertura_dias": 565.2,
      "rotacion": 0.16,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 565 días, exceso de stock",
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
      "pct_acum": 83.0,
      "unidades": 25,
      "venta": 375.0,
      "margen_unitario": 4.2,
      "margen_total": 105.0,
      "costo_estimado": true,
      "existencia": 173,
      "minimo": 26,
      "quiebres": 0,
      "demanda_dia": 0.28,
      "cobertura_dias": 622.8,
      "rotacion": 0.14,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 623 días, exceso de stock",
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
      "pct_acum": 84.7,
      "unidades": 25,
      "venta": 1050.0,
      "margen_unitario": 11.76,
      "margen_total": 294.0,
      "costo_estimado": true,
      "existencia": 54,
      "minimo": 21,
      "quiebres": 2,
      "demanda_dia": 0.28,
      "cobertura_dias": 194.4,
      "rotacion": 0.46,
      "recomendacion": "Aumentar",
      "motivo": "hubo quiebres",
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
      "pct_acum": 86.2,
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
      "clase": "B",
      "pct_acum": 87.7,
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
        "id": 5,
        "clave_interna": "AB-005",
        "nombre": "Sal de mesa"
      },
      "categoria": "Abarrote básico",
      "clase": "B",
      "pct_acum": 89.2,
      "unidades": 22,
      "venta": 308.0,
      "margen_unitario": 3.92,
      "margen_total": 86.24,
      "costo_estimado": true,
      "existencia": 116,
      "minimo": 21,
      "quiebres": 0,
      "demanda_dia": 0.24,
      "cobertura_dias": 474.5,
      "rotacion": 0.19,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 475 días, exceso de stock",
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
      "pct_acum": 90.6,
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
        "id": 35,
        "clave_interna": "LA-007",
        "nombre": "Mantequilla"
      },
      "categoria": "Lácteos y huevo",
      "clase": "B",
      "pct_acum": 92.1,
      "unidades": 22,
      "venta": 484.0,
      "margen_unitario": 6.16,
      "margen_total": 135.52,
      "costo_estimado": true,
      "existencia": 155,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.24,
      "cobertura_dias": 634.1,
      "rotacion": 0.14,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 634 días, exceso de stock",
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
      "pct_acum": 93.4,
      "unidades": 20,
      "venta": 290.0,
      "margen_unitario": 4.06,
      "margen_total": 81.2,
      "costo_estimado": true,
      "existencia": 180,
      "minimo": 21,
      "quiebres": 0,
      "demanda_dia": 0.22,
      "cobertura_dias": 810.0,
      "rotacion": 0.11,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 810 días, exceso de stock",
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
      "pct_acum": 94.6,
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
        "id": 49,
        "clave_interna": "HI-004",
        "nombre": "Desodorante"
      },
      "categoria": "Higiene personal",
      "clase": "B",
      "pct_acum": 95.8,
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
      "clase": "C",
      "pct_acum": 96.9,
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
        "id": 38,
        "clave_interna": "LI-002",
        "nombre": "Jabón para trastes"
      },
      "categoria": "Limpieza del hogar",
      "clase": "C",
      "pct_acum": 97.9,
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
      "pct_acum": 98.8,
      "unidades": 14,
      "venta": 364.0,
      "margen_unitario": 7.28,
      "margen_total": 101.92,
      "costo_estimado": true,
      "existencia": 201,
      "minimo": 30,
      "quiebres": 0,
      "demanda_dia": 0.16,
      "cobertura_dias": 1292.1,
      "rotacion": 0.07,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1292 días, exceso de stock",
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
X-Traza-Id: c0c009bb-23f9-4660-8866-5af1081e8874
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 391 ms · traza `c0c009bb-23f9-4660-8866-5af1081e8874`

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
    "clase_b": 12,
    "clase_c": 7,
    "unidades_a_comprar": 1,
    "con_costo_estimado": 51,
    "espacio": {
      "total": 3600.0,
      "ocupado": 3508.0,
      "sugerido": 1.0,
      "ocupacion_pct": 97.5
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
      "pct_acum": 5.0,
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
        "id": 48,
        "clave_interna": "HI-003",
        "nombre": "Pasta dental"
      },
      "categoria": "Higiene personal",
      "clase": "A",
      "pct_acum": 9.6,
      "unidades": 20,
      "venta": 640.0,
      "margen_unitario": 8.96,
      "margen_total": 179.2,
      "costo_estimado": true,
      "existencia": 74,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.22,
      "cobertura_dias": 333.0,
      "rotacion": 0.27,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 333 días, exceso de stock",
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
      "pct_acum": 13.3,
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
      "pct_acum": 16.7,
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
      "pct_acum": 20.2,
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
        "id": 13,
        "clave_interna": "AB-013",
        "nombre": "Puré de tomate"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 23.4,
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
      "pct_acum": 26.4,
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
      "pct_acum": 29.4,
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
        "id": 8,
        "clave_interna": "AB-008",
        "nombre": "Pasta para sopa surtida"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 32.1,
      "unidades": 12,
      "venta": 114.0,
      "margen_unitario": 2.66,
      "margen_total": 31.92,
      "costo_estimado": true,
      "existencia": 21,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.13,
      "cobertura_dias": 157.5,
      "rotacion": 0.57,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 158 días, exceso de stock",
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
      "pct_acum": 34.9,
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
      "pct_acum": 37.6,
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
      "pct_acum": 40.4,
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
        "id": 2,
        "clave_interna": "AB-002",
        "nombre": "Arroz superextra"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 42.9,
      "unidades": 11,
      "venta": 328.9,
      "margen_unitario": 8.37,
      "margen_total": 92.07,
      "costo_estimado": true,
      "existencia": 36,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.12,
      "cobertura_dias": 294.5,
      "rotacion": 0.31,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 295 días, exceso de stock",
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
      "pct_acum": 45.4,
      "unidades": 11,
      "venta": 352.0,
      "margen_unitario": 8.96,
      "margen_total": 98.56,
      "costo_estimado": true,
      "existencia": 17,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.12,
      "cobertura_dias": 139.1,
      "rotacion": 0.65,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 139 días, exceso de stock",
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
      "pct_acum": 47.9,
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
      "pct_acum": 50.2,
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
        "id": 11,
        "clave_interna": "AB-011",
        "nombre": "Frijoles refritos"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 52.3,
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
      "pct_acum": 54.4,
      "unidades": 9,
      "venta": 175.5,
      "margen_unitario": 5.46,
      "margen_total": 49.14,
      "costo_estimado": true,
      "existencia": 455,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 4550.0,
      "rotacion": 0.02,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 4550 días, exceso de stock",
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
      "pct_acum": 56.4,
      "unidades": 9,
      "venta": 396.0,
      "margen_unitario": 12.32,
      "margen_total": 110.88,
      "costo_estimado": true,
      "existencia": 78,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 780.0,
      "rotacion": 0.12,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 780 días, exceso de stock",
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
      "pct_acum": 58.5,
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
      "pct_acum": 60.6,
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
      "pct_acum": 62.4,
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
      "pct_acum": 64.2,
      "unidades": 8,
      "venta": 208.0,
      "margen_unitario": 7.28,
      "margen_total": 58.24,
      "costo_estimado": true,
      "existencia": 86,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 967.5,
      "rotacion": 0.09,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 968 días, exceso de stock",
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
      "clase": "A",
      "pct_acum": 66.1,
      "unidades": 8,
      "venta": 120.0,
      "margen_unitario": 4.2,
      "margen_total": 33.6,
      "costo_estimado": true,
      "existencia": 69,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 776.2,
      "rotacion": 0.12,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 776 días, exceso de stock",
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
      "pct_acum": 67.9,
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
      "pct_acum": 69.7,
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
      "pct_acum": 71.6,
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
      "pct_acum": 73.4,
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
      "pct_acum": 75.2,
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
      "pct_acum": 76.8,
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
        "id": 10,
        "clave_interna": "AB-010",
        "nombre": "Sardina en salsa de tomate"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 78.4,
      "unidades": 7,
      "venta": 185.5,
      "margen_unitario": 7.42,
      "margen_total": 51.94,
      "costo_estimado": true,
      "existencia": 782,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 10054.3,
      "rotacion": 0.01,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 10054 días, exceso de stock",
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
      "pct_acum": 80.0,
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
X-Traza-Id: 1be6d436-d36a-423c-90f4-a47cd89fc584
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 563 ms · traza `1be6d436-d36a-423c-90f4-a47cd89fc584`

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
    "traza_id": "1be6d436-d36a-423c-90f4-a47cd89fc584"
  }
}
```

### SUR-06 · Análisis (XML) · PASA

**Objetivo.** Respuesta XML que cumple surtido.xsd.

**Petición.** `GET http://surtido:5122/api/v1/surtido/analisis?microhub_id=1`

```http
Accept: application/xml
X-Traza-Id: 52339f3d-c9bb-4f7d-bd1e-6726584c96ce
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 580 ms · traza `52339f3d-c9bb-4f7d-bd1e-6726584c96ce`

```xml
<?xml version='1.0' encoding='utf-8'?>
<surtido_analisis xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><ventana_dias>90</ventana_dias><resumen><productos>51</productos><aumentar>1</aumentar><mantener>0</mantener><reducir>50</reducir><eliminar>0</eliminar><excluir>0</excluir><clase_a>32</clase_a><clase_b>12</clase_b><clase_c>7</clase_c><unidades_a_comprar>1</unidades_a_comprar><con_costo_estimado>51</con_costo_estimado><espacio><total>3600</total><ocupado>3508</ocupado><sugerido>1</sugerido><ocupacion_pct>97.5</ocupacion_pct></espacio><presupuesto><total>120000</total><requerido>27.36</requerido><uso_pct>0</uso_pct></presupuesto></resumen><filas><fila><producto><id>28</id><clave_interna>BE-008</clave_interna><nombre>Polvo para agua de sabor</nombre></producto><categoria>Bebidas</categoria><clase>A</clase><pct_acum>5</pct_acum><unidades>22</unidades><venta>165</venta><margen_unitario>2.1</margen_unitario><margen_total>46.2</margen_total><costo_estimado>true</costo_estimado><existencia>30</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.24</demanda_dia><cobertura_dias>122.7</cobertura_dias><rotacion>0.73</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 123 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>48</id><clave_interna>HI-003</clave_interna><nombre>Pasta dental</nombre></producto><categoria>Higiene personal</categoria><clase>A</clase><pct_acum>9.6</pct_acum><unidades>20</unidades><venta>640</venta><margen_unitario>8.96</margen_unitario><margen_total>179.2</margen_total><costo_estimado>true</costo_estimado><existencia>74</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.22</demanda_dia><cobertura_dias>333</cobertura_dias><rotacion>0.27</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 333 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>45</id><clave_interna>LI-009</clave_interna><nombre>Fibra para trastes</nombre></producto><categoria>Limpieza del hogar</categoria><clase>A</clase><pct_acum>13.3</pct_acum><unidades>16</unidades><venta>288</venta><margen_unitario>5.04</margen_unitario><margen_total>80.64</margen_total><costo_estimado>true</costo_estimado><existencia>43</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.18</demanda_dia><cobertura_dias>241.9</cobertura_dias><rotacion>0.37</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 242 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>7</id><clave_interna>AB-007</clave_interna><nombre>Harina de trigo</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>16.7</pct_acum><unidades>15</unidades><venta>367.5</venta><margen_unitario>6.86</margen_unitario><margen_total>102.9</margen_total><costo_estimado>true</costo_estimado><existencia>14</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.17</demanda_dia><cobertura_dias>84</cobertura_dias><rotacion>1.07</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 84 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>25</id><clave_interna>BE-005</clave_interna><nombre>Jugo de naranja</nombre></producto><categoria>Bebidas</categoria><clase>A</clase><pct_acum>20.2</pct_acum><unidades>15</unidades><venta>420</venta><margen_unitario>7.84</margen_unitario><margen_total>117.6</margen_total><costo_estimado>true</costo_estimado><existencia>80</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.17</demanda_dia><cobertura_dias>480</cobertura_dias><rotacion>0.19</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 480 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>13</id><clave_interna>AB-013</clave_interna><nombre>Puré de tomate</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>23.4</pct_acum><unidades>14</unidades><venta>154</venta><margen_unitario>3.08</margen_unitario><margen_total>43.12</margen_total><costo_estimado>true</costo_estimado><existencia>56</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.16</demanda_dia><cobertura_dias>360</cobertura_dias><rotacion>0.25</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 360 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>20</id><clave_interna>AB-020</clave_interna><nombre>Lenteja</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>26.4</pct_acum><unidades>13</unidades><venta>312</venta><margen_unitario>6.72</margen_unitario><margen_total>87.36</margen_total><costo_estimado>true</costo_estimado><existencia>73</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.14</demanda_dia><cobertura_dias>505.4</cobertura_dias><rotacion>0.18</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 505 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>36</id><clave_interna>LA-008</clave_interna><nombre>Jamón de pavo</nombre></producto><categoria>Lácteos y huevo</categoria><clase>A</clase><pct_acum>29.4</pct_acum><unidades>13</unidades><venta>598</venta><margen_unitario>12.88</margen_unitario><margen_total>167.44</margen_total><costo_estimado>true</costo_estimado><existencia>47</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.14</demanda_dia><cobertura_dias>325.4</cobertura_dias><rotacion>0.28</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 325 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>8</id><clave_interna>AB-008</clave_interna><nombre>Pasta para sopa surtida</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>32.1</pct_acum><unidades>12</unidades><venta>114</venta><margen_unitario>2.66</margen_unitario><margen_total>31.92</margen_total><costo_estimado>true</costo_estimado><existencia>21</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.13</demanda_dia><cobertura_dias>157.5</cobertura_dias><rotacion>0.57</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 158 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>30</id><clave_interna>LA-002</clave_interna><nombre>Leche deslactosada</nombre></producto><categoria>Lácteos y huevo</categoria><clase>A</clase><pct_acum>34.9</pct_acum><unidades>12</unidades><venta>372</venta><margen_unitario>8.68</margen_unitario><margen_total>104.16</margen_total><costo_estimado>true</costo_estimado><existencia>12</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.13</demanda_dia><cobertura_dias>90</cobertura_dias><rotacion>1</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 90 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>34</id><clave_interna>LA-006</clave_interna><nombre>Yogur natural</nombre></producto><categoria>Lácteos y huevo</categoria><clase>A</clase><pct_acum>37.6</pct_acum><unidades>12</unidades><venta>528</venta><margen_unitario>12.32</margen_unitario><margen_total>147.84</margen_total><costo_estimado>true</costo_estimado><existencia>10</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.13</demanda_dia><cobertura_dias>75</cobertura_dias><rotacion>1.2</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 75 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>42</id><clave_interna>LI-006</clave_interna><nombre>Papel higiénico</nombre></producto><categoria>Limpieza del hogar</categoria><clase>A</clase><pct_acum>40.4</pct_acum><unidades>12</unidades><venta>456</venta><margen_unitario>10.64</margen_unitario><margen_total>127.68</margen_total><costo_estimado>true</costo_estimado><existencia>64</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.13</demanda_dia><cobertura_dias>480</cobertura_dias><rotacion>0.19</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 480 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>2</id><clave_interna>AB-002</clave_interna><nombre>Arroz superextra</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>42.9</pct_acum><unidades>11</unidades><venta>328.9</venta><margen_unitario>8.37</margen_unitario><margen_total>92.07</margen_total><costo_estimado>true</costo_estimado><existencia>36</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.12</demanda_dia><cobertura_dias>294.5</cobertura_dias><rotacion>0.31</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 295 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>26</id><clave_interna>BE-006</clave_interna><nombre>Bebida de soya</nombre></producto><categoria>Bebidas</categoria><clase>A</clase><pct_acum>45.4</pct_acum><unidades>11</unidades><venta>352</venta><margen_unitario>8.96</margen_unitario><margen_total>98.56</margen_total><costo_estimado>true</costo_estimado><existencia>17</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.12</demanda_dia><cobertura_dias>139.1</cobertura_dias><rotacion>0.65</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 139 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>39</id><clave_interna>LI-003</clave_interna><nombre>Cloro</nombre></producto><categoria>Limpieza del hogar</categoria><clase>A</clase><pct_acum>47.9</pct_acum><unidades>11</unidades><venta>214.5</venta><margen_unitario>5.46</margen_unitario><margen_total>60.06</margen_total><costo_estimado>true</costo_estimado><existencia>44</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.12</demanda_dia><cobertura_dias>360</cobertura_dias><rotacion>0.25</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 360 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>43</id><clave_interna>LI-007</clave_interna><nombre>Servilletas</nombre></producto><categoria>Limpieza del hogar</categoria><clase>A</clase><pct_acum>50.2</pct_acum><unidades>10</unidades><venta>320</venta><margen_unitario>8.96</margen_unitario><margen_total>89.6</margen_total><costo_estimado>true</costo_estimado><existencia>65</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.11</demanda_dia><cobertura_dias>585</cobertura_dias><rotacion>0.15</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 585 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>11</id><clave_interna>AB-011</clave_interna><nombre>Frijoles refritos</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>52.3</pct_acum><unidades>9</unidades><venta>207</venta><margen_unitario>6.44</margen_unitario><margen_total>57.96</margen_total><costo_estimado>true</costo_estimado><existencia>27</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.1</demanda_dia><cobertura_dias>270</cobertura_dias><rotacion>0.33</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 270 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>12</id><clave_interna>AB-012</clave_interna><nombre>Chiles jalapeños en escabeche</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>54.4</pct_acum><unidades>9</unidades><venta>175.5</venta><margen_unitario>5.46</margen_unitario><margen_total>49.14</margen_total><costo_estimado>true</costo_estimado><existencia>455</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.1</demanda_dia><cobertura_dias>4550</cobertura_dias><rotacion>0.02</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 4550 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>18</id><clave_interna>AB-018</clave_interna><nombre>Pan de caja blanco</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>56.4</pct_acum><unidades>9</unidades><venta>396</venta><margen_unitario>12.32</margen_unitario><margen_total>110.88</margen_total><costo_estimado>true</costo_estimado><existencia>78</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.1</demanda_dia><cobertura_dias>780</cobertura_dias><rotacion>0.12</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 780 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>19</id><clave_interna>AB-019</clave_interna><nombre>Huevo blanco</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>58.5</pct_acum><unidades>9</unidades><venta>378</venta><margen_unitario>11.76</margen_unitario><margen_total>105.84</margen_total><costo_estimado>true</costo_estimado><existencia>49</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.1</demanda_dia><cobertura_dias>490</cobertura_dias><rotacion>0.18</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 490 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>44</id><clave_interna>LI-008</clave_interna><nombre>Bolsas para basura</nombre></producto><categoria>Limpieza del hogar</categoria><clase>A</clase><pct_acum>60.6</pct_acum><unidades>9</unidades><venta>216</venta><margen_unitario>6.72</margen_unitario><margen_total>60.48</margen_total><costo_estimado>true</costo_estimado><existencia>26</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.1</demanda_dia><cobertura_dias>260</cobertura_dias><rotacion>0.35</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 260 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>1</id><clave_interna>AB-001</clave_interna><nombre>Frijol negro a granel</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>62.4</pct_acum><unidades>8</unidades><venta>308</venta><margen_unitario>10.78</margen_unitario><margen_total>86.24</margen_total><costo_estimado>true</costo_estimado><existencia>58</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.09</demanda_dia><cobertura_dias>652.5</cobertura_dias><rotacion>0.14</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 652 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>6</id><clave_interna>AB-006</clave_interna><nombre>Harina de maíz nixtamalizado</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>64.2</pct_acum><unidades>8</unidades><venta>208</venta><margen_unitario>7.28</margen_unitario><margen_total>58.24</margen_total><costo_estimado>true</costo_estimado><existencia>86</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.09</demanda_dia><cobertura_dias>967.5</cobertura_dias><rotacion>0.09</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 968 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>22</id><clave_interna>BE-002</clave_interna><nombre>Agua embotellada</nombre></producto><categoria>Bebidas</categoria><clase>A</clase><pct_acum>66.1</pct_acum><unidades>8</unidades><venta>120</venta><margen_unitario>4.2</margen_unitario><margen_total>33.6</margen_total><costo_estimado>true</costo_estimado><existencia>69</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.09</demanda_dia><cobertura_dias>776.2</cobertura_dias><rotacion>0.12</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 776 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>24</id><clave_interna>BE-004</clave_interna><nombre>Refresco sabor manzana</nombre></producto><categoria>Bebidas</categoria><clase>A</clase><pct_acum>67.9</pct_acum><unidades>8</unidades><venta>288</venta><margen_unitario>10.08</margen_unitario><margen_total>80.64</margen_total><costo_estimado>true</costo_estimado><existencia>39</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.09</demanda_dia><cobertura_dias>438.8</cobertura_dias><rotacion>0.21</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 439 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>27</id><clave_interna>BE-007</clave_interna><nombre>Té helado de limón</nombre></producto><categoria>Bebidas</categoria><clase>A</clase><pct_acum>69.7</pct_acum><unidades>8</unidades><venta>136</venta><margen_unitario>4.76</margen_unitario><margen_total>38.08</margen_total><costo_estimado>true</costo_estimado><existencia>84</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.09</demanda_dia><cobertura_dias>945</cobertura_dias><rotacion>0.1</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 945 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>29</id><clave_interna>LA-001</clave_interna><nombre>Leche entera</nombre></producto><categoria>Lácteos y huevo</categoria><clase>A</clase><pct_acum>71.6</pct_acum><unidades>8</unidades><venta>220</venta><margen_unitario>7.7</margen_unitario><margen_total>61.6</margen_total><costo_estimado>true</costo_estimado><existencia>48</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.09</demanda_dia><cobertura_dias>540</cobertura_dias><rotacion>0.17</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 540 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>40</id><clave_interna>LI-004</clave_interna><nombre>Limpiador multiusos</nombre></producto><categoria>Limpieza del hogar</categoria><clase>A</clase><pct_acum>73.4</pct_acum><unidades>8</unidades><venta>224</venta><margen_unitario>7.84</margen_unitario><margen_total>62.72</margen_total><costo_estimado>true</costo_estimado><existencia>14</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.09</demanda_dia><cobertura_dias>157.5</cobertura_dias><rotacion>0.57</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 158 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>51</id><clave_interna>HI-006</clave_interna><nombre>Pañal etapa 3</nombre></producto><categoria>Higiene personal</categoria><clase>A</clase><pct_acum>75.2</pct_acum><unidades>8</unidades><venta>544</venta><margen_unitario>19.04</margen_unitario><margen_total>152.32</margen_total><costo_estimado>true</costo_estimado><existencia>29</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.09</demanda_dia><cobertura_dias>326.2</cobertura_dias><rotacion>0.28</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 326 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>5</id><clave_interna>AB-005</clave_interna><nombre>Sal de mesa</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>76.8</pct_acum><unidades>7</unidades><venta>98</venta><margen_unitario>3.92</margen_unitario><margen_total>27.44</margen_total><costo_estimado>true</costo_estimado><existencia>30</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.08</demanda_dia><cobertura_dias>385.7</cobertura_dias><rotacion>0.23</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 386 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>10</id><clave_interna>AB-010</clave_interna><nombre>Sardina en salsa de tomate</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>78.4</pct_acum><unidades>7</unidades><venta>185.5</venta><margen_unitario>7.42</margen_unitario><margen_total>51.94</margen_total><costo_estimado>true</costo_estimado><existencia>782</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.08</demanda_dia><cobertura_dias>10054.3</cobertura_dias><rotacion>0.01</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 10054 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>14</id><clave_interna>AB-014</clave_interna><nombre>Café soluble</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>80</pct_acum><unidades>7</unidades><venta>364</venta><margen_unitario>14.56</margen_unitario><margen_total>101.92</margen_total><costo_estimado>true</costo_estimado><existencia>33</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.08</demanda_dia><cobertura_dias>424.3</cobertura_dias><rotacion>0.21</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 424 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>35</id><clave_interna>LA-007</clave_interna><nombre>Mantequilla</nombre></producto><categoria>Lácteos y huevo</categoria><clase>B</clase><pct_acum>81.7</pct_acum><unidades>7</unidades><venta>154</venta><margen_unitario>6.16</margen_unitario><margen_total>43.12</margen_total><costo_estimado>true</costo_estimado><existencia>64</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.08</demanda_dia><cobertura_dias>822.9</cobertura_dias><rotacion>0.11</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 823 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>47</id><clave_interna>HI-002</clave_interna><nombre>Shampoo</nombre></producto><categoria>Higiene personal</categoria><clase>B</clase><pct_acum>83.3</pct_acum><unidades>7</unidades><venta>378</venta><margen_unitario>15.12</margen_unitario><margen_total>105.84</margen_total><costo_estimado>true</costo_estimado><existencia>36</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.08</demanda_dia><cobertura_dias>462.9</cobertura_dias><rotacion>0.19</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 463 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>49</id><clave_interna>HI-004</clave_interna><nombre>Desodorante</nombre></producto><categoria>Higiene personal</categoria><clase>B</clase><pct_acum>84.9</pct_acum><unidades>7</unidades><venta>336</venta><margen_unitario>13.44</margen_unitario><margen_total>94.08</margen_total><costo_estimado>true</costo_estimado><existencia>36</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.08</demanda_dia><cobertura_dias>462.9</cobertura_dias><rotacion>0.19</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 463 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>3</id><clave_interna>AB-003</clave_interna><nombre>Aceite vegetal</nombre></producto><categoria>Abarrote básico</categoria><clase>B</clase><pct_acum>86.2</pct_acum><unidades>6</unidades><venta>252</venta><margen_unitario>11.76</margen_unitario><margen_total>70.56</margen_total><costo_estimado>true</costo_estimado><existencia>10</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.07</demanda_dia><cobertura_dias>150</cobertura_dias><rotacion>0.6</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 150 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>17</id><clave_interna>AB-017</clave_interna><nombre>Tortillas de maíz</nombre></producto><categoria>Abarrote básico</categoria><clase>B</clase><pct_acum>87.6</pct_acum><unidades>6</unidades><venta>144</venta><margen_unitario>6.72</margen_unitario><margen_total>40.32</margen_total><costo_estimado>true</costo_estimado><existencia>21</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.07</demanda_dia><cobertura_dias>315</cobertura_dias><rotacion>0.29</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 315 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>16</id><clave_interna>AB-016</clave_interna><nombre>Galletas María</nombre></producto><categoria>Abarrote básico</categoria><clase>B</clase><pct_acum>88.8</pct_acum><unidades>5</unidades><venta>82.5</venta><margen_unitario>4.62</margen_unitario><margen_total>23.1</margen_total><costo_estimado>true</costo_estimado><existencia>81</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>1458</cobertura_dias><rotacion>0.06</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1458 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>23</id><clave_interna>BE-003</clave_interna><nombre>Refresco de cola</nombre></producto><categoria>Bebidas</categoria><clase>B</clase><pct_acum>89.9</pct_acum><unidades>5</unidades><venta>192.5</venta><margen_unitario>10.78</margen_unitario><margen_total>53.9</margen_total><costo_estimado>true</costo_estimado><existencia>54</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>972</cobertura_dias><rotacion>0.09</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 972 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>41</id><clave_interna>LI-005</clave_interna><nombre>Suavizante de telas</nombre></producto><categoria>Limpieza del hogar</categoria><clase>B</clase><pct_acum>91.1</pct_acum><unidades>5</unidades><venta>165</venta><margen_unitario>9.24</margen_unitario><margen_total>46.2</margen_total><costo_estimado>true</costo_estimado><existencia>69</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>1242</cobertura_dias><rotacion>0.07</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1242 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>46</id><clave_interna>HI-001</clave_interna><nombre>Jabón de tocador</nombre></producto><categoria>Higiene personal</categoria><clase>B</clase><pct_acum>92.2</pct_acum><unidades>5</unidades><venta>72.5</venta><margen_unitario>4.06</margen_unitario><margen_total>20.3</margen_total><costo_estimado>true</costo_estimado><existencia>63</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>1134</cobertura_dias><rotacion>0.08</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1134 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>50</id><clave_interna>HI-005</clave_interna><nombre>Toallas femeninas</nombre></producto><categoria>Higiene personal</categoria><clase>B</clase><pct_acum>93.3</pct_acum><unidades>5</unidades><venta>180</venta><margen_unitario>10.08</margen_unitario><margen_total>50.4</margen_total><costo_estimado>true</costo_estimado><existencia>76</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>1368</cobertura_dias><rotacion>0.07</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1368 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>4</id><clave_interna>AB-004</clave_interna><nombre>Azúcar estándar</nombre></producto><categoria>Abarrote básico</categoria><clase>B</clase><pct_acum>94.3</pct_acum><unidades>4</unidades><venta>114</venta><margen_unitario>7.98</margen_unitario><margen_total>31.92</margen_total><costo_estimado>true</costo_estimado><existencia>18</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.04</demanda_dia><cobertura_dias>405</cobertura_dias><rotacion>0.22</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 405 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>15</id><clave_interna>AB-015</clave_interna><nombre>Avena en hojuelas</nombre></producto><categoria>Abarrote básico</categoria><clase>B</clase><pct_acum>95.2</pct_acum><unidades>4</unidades><venta>108</venta><margen_unitario>7.56</margen_unitario><margen_total>30.24</margen_total><costo_estimado>true</costo_estimado><existencia>52</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.04</demanda_dia><cobertura_dias>1170</cobertura_dias><rotacion>0.08</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1170 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>32</id><clave_interna>LA-004</clave_interna><nombre>Queso Oaxaca</nombre></producto><categoria>Lácteos y huevo</categoria><clase>C</clase><pct_acum>96.1</pct_acum><unidades>4</unidades><venta>288</venta><margen_unitario>20.16</margen_unitario><margen_total>80.64</margen_total><costo_estimado>true</costo_estimado><existencia>20</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.04</demanda_dia><cobertura_dias>450</cobertura_dias><rotacion>0.2</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 450 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>33</id><clave_interna>LA-005</clave_interna><nombre>Crema ácida</nombre></producto><categoria>Lácteos y huevo</categoria><clase>C</clase><pct_acum>97</pct_acum><unidades>4</unidades><venta>144</venta><margen_unitario>10.08</margen_unitario><margen_total>40.32</margen_total><costo_estimado>true</costo_estimado><existencia>82</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.04</demanda_dia><cobertura_dias>1845</cobertura_dias><rotacion>0.05</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1845 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>37</id><clave_interna>LI-001</clave_interna><nombre>Detergente en polvo</nombre></producto><categoria>Limpieza del hogar</categoria><clase>C</clase><pct_acum>97.9</pct_acum><unidades>4</unidades><venta>168</venta><margen_unitario>11.76</margen_unitario><margen_total>47.04</margen_total><costo_estimado>true</costo_estimado><existencia>13</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.04</demanda_dia><cobertura_dias>292.5</cobertura_dias><rotacion>0.31</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 292 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>9</id><clave_interna>AB-009</clave_interna><nombre>Atún en agua</nombre></producto><categoria>Abarrote básico</categoria><clase>C</clase><pct_acum>98.6</pct_acum><unidades>3</unidades><venta>63</venta><margen_unitario>5.88</margen_unitario><margen_total>17.64</margen_total><costo_estimado>true</costo_estimado><existencia>42</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.03</demanda_dia><cobertura_dias>1260</cobertura_dias><rotacion>0.07</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1260 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>38</id><clave_interna>LI-002</clave_interna><nombre>Jabón para trastes</nombre></producto><categoria>Limpieza del hogar</categoria><clase>C</clase><pct_acum>99.3</pct_acum><unidades>3</unidades><venta>78</venta><margen_unitario>7.28</margen_unitario><margen_total>21.84</margen_total><costo_estimado>true</costo_estimado><existencia>47</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.03</demanda_dia><cobertura_dias>1410</cobertura_dias><rotacion>0.06</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1410 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>31</id><clave_interna>LA-003</clave_interna><nombre>Queso fresco</nombre></producto><categoria>Lácteos y huevo</categoria><clase>C</clase><pct_acum>99.8</pct_acum><unidades>2</unidades><venta>116</venta><margen_unitario>16.24</margen_unitario><margen_total>32.48</margen_total><costo_estimado>true</costo_estimado><existencia>131</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.02</demanda_dia><cobertura_dias>5895</cobertura_dias><rotacion>0.02</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 5895 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>21</id><clave_interna>BE-001</clave_interna><nombre>Agua purificada</nombre></producto><categoria>Bebidas</categoria><clase>C</clase><pct_acum>100</pct_acum><unidades>1</unidades><venta>38</venta><margen_unitario>10.64</margen_unitario><margen_total>10.64</margen_total><costo_estimado>true</costo_estimado><existencia>0</existencia><minimo>10</minimo><quiebres>2</quiebres><demanda_dia>0.01</demanda_dia><cobertura_dias>0</cobertura_dias><rotacion>99</rotacion><recomendacion>Aumentar</recomendacion><motivo>hubo quiebres</motivo><sugerido>1</sugerido><limitado_por xsi:nil="true" /></fila></filas><supuestos_usados><supuesto><clave>abc_a_pct</clave><valor>80</valor><modificado>false</modificado></supuesto><supuesto><clave>abc_b_pct</clave><valor>95</valor><modificado>false</modificado></supuesto><supuesto><clave>cobertura_dias_a</clave><valor>7</valor><modificado>false</modificado></supuesto><supuesto><clave>cobertura_dias_b</clave><valor>5</valor><modificado>false</modificado></supuesto><supuesto><clave>cobertura_dias_c</clave><valor>3</valor><modificado>false</modificado></supuesto><supuesto><clave>cobertura_dias_exceso</clave><valor>30</valor><modificado>false</modificado></supuesto><supuesto><clave>ventana_analisis_dias</clave><valor>90</valor><modificado>false</modificado></supuesto></supuestos_usados></surtido_analisis>
```

### SUR-07 · El operador analiza su microhub · PASA

**Objetivo.** Operador y supervisor solo trabajan con el suyo.

**Petición.** `GET http://surtido:5122/api/v1/surtido/analisis?microhub_id=1`

```http
Accept: application/json
X-Traza-Id: 01168184-acda-4d01-8813-2e018cff0eaf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 339 ms · traza `01168184-acda-4d01-8813-2e018cff0eaf`

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
    "clase_b": 12,
    "clase_c": 7,
    "unidades_a_comprar": 1,
    "con_costo_estimado": 51,
    "espacio": {
      "total": 3600.0,
      "ocupado": 3508.0,
      "sugerido": 1.0,
      "ocupacion_pct": 97.5
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
      "pct_acum": 5.0,
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
        "id": 48,
        "clave_interna": "HI-003",
        "nombre": "Pasta dental"
      },
      "categoria": "Higiene personal",
      "clase": "A",
      "pct_acum": 9.6,
      "unidades": 20,
      "venta": 640.0,
      "margen_unitario": 8.96,
      "margen_total": 179.2,
      "costo_estimado": true,
      "existencia": 74,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.22,
      "cobertura_dias": 333.0,
      "rotacion": 0.27,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 333 días, exceso de stock",
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
      "pct_acum": 13.3,
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
      "pct_acum": 16.7,
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
      "pct_acum": 20.2,
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
        "id": 13,
        "clave_interna": "AB-013",
        "nombre": "Puré de tomate"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 23.4,
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
      "pct_acum": 26.4,
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
      "pct_acum": 29.4,
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
        "id": 8,
        "clave_interna": "AB-008",
        "nombre": "Pasta para sopa surtida"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 32.1,
      "unidades": 12,
      "venta": 114.0,
      "margen_unitario": 2.66,
      "margen_total": 31.92,
      "costo_estimado": true,
      "existencia": 21,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.13,
      "cobertura_dias": 157.5,
      "rotacion": 0.57,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 158 días, exceso de stock",
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
      "pct_acum": 34.9,
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
      "pct_acum": 37.6,
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
      "pct_acum": 40.4,
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
        "id": 2,
        "clave_interna": "AB-002",
        "nombre": "Arroz superextra"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 42.9,
      "unidades": 11,
      "venta": 328.9,
      "margen_unitario": 8.37,
      "margen_total": 92.07,
      "costo_estimado": true,
      "existencia": 36,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.12,
      "cobertura_dias": 294.5,
      "rotacion": 0.31,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 295 días, exceso de stock",
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
      "pct_acum": 45.4,
      "unidades": 11,
      "venta": 352.0,
      "margen_unitario": 8.96,
      "margen_total": 98.56,
      "costo_estimado": true,
      "existencia": 17,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.12,
      "cobertura_dias": 139.1,
      "rotacion": 0.65,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 139 días, exceso de stock",
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
      "pct_acum": 47.9,
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
      "pct_acum": 50.2,
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
        "id": 11,
        "clave_interna": "AB-011",
        "nombre": "Frijoles refritos"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 52.3,
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
      "pct_acum": 54.4,
      "unidades": 9,
      "venta": 175.5,
      "margen_unitario": 5.46,
      "margen_total": 49.14,
      "costo_estimado": true,
      "existencia": 455,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 4550.0,
      "rotacion": 0.02,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 4550 días, exceso de stock",
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
      "pct_acum": 56.4,
      "unidades": 9,
      "venta": 396.0,
      "margen_unitario": 12.32,
      "margen_total": 110.88,
      "costo_estimado": true,
      "existencia": 78,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 780.0,
      "rotacion": 0.12,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 780 días, exceso de stock",
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
      "pct_acum": 58.5,
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
      "pct_acum": 60.6,
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
      "pct_acum": 62.4,
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
      "pct_acum": 64.2,
      "unidades": 8,
      "venta": 208.0,
      "margen_unitario": 7.28,
      "margen_total": 58.24,
      "costo_estimado": true,
      "existencia": 86,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 967.5,
      "rotacion": 0.09,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 968 días, exceso de stock",
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
      "clase": "A",
      "pct_acum": 66.1,
      "unidades": 8,
      "venta": 120.0,
      "margen_unitario": 4.2,
      "margen_total": 33.6,
      "costo_estimado": true,
      "existencia": 69,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 776.2,
      "rotacion": 0.12,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 776 días, exceso de stock",
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
      "pct_acum": 67.9,
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
      "pct_acum": 69.7,
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
      "pct_acum": 71.6,
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
      "pct_acum": 73.4,
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
      "pct_acum": 75.2,
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
      "pct_acum": 76.8,
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
        "id": 10,
        "clave_interna": "AB-010",
        "nombre": "Sardina en salsa de tomate"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 78.4,
      "unidades": 7,
      "venta": 185.5,
      "margen_unitario": 7.42,
      "margen_total": 51.94,
      "costo_estimado": true,
      "existencia": 782,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 10054.3,
      "rotacion": 0.01,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 10054 días, exceso de stock",
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
      "pct_acum": 80.0,
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
        "id": 35,
        "clave_interna": "LA-007",
        "nombre": "Mantequilla"
      },
      "categoria": "Lácteos y huevo",
      "clase": "B",
      "pct_acum": 81.7,
      "unidades": 7,
      "venta": 154.0,
      "margen_unitario": 6.16,
      "margen_total": 43.12,
      "costo_estimado": true,
      "existencia": 64,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 822.9,
      "rotacion": 0.11,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 823 días, exceso de stock",
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
      "clase": "B",
      "pct_acum": 83.3,
      "unidades": 7,
      "venta": 378.0,
      "margen_unitario": 15.12,
      "margen_total": 105.84,
      "costo_estimado": true,
      "existencia": 36,
      "minimo": 10,
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
        "id": 49,
        "clave_interna": "HI-004",
        "nombre": "Desodorante"
      },
      "categoria": "Higiene personal",
      "clase": "B",
      "pct_acum": 84.9,
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
      "pct_acum": 86.2,
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
      "pct_acum": 87.6,
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
        "id": 16,
        "clave_interna": "AB-016",
        "nombre": "Galletas María"
      },
      "categoria": "Abarrote básico",
      "clase": "B",
      "pct_acum": 88.8,
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
        "id": 23,
        "clave_interna": "BE-003",
        "nombre": "Refresco de cola"
      },
      "categoria": "Bebidas",
      "clase": "B",
      "pct_acum": 89.9,
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
        "id": 41,
        "clave_interna": "LI-005",
        "nombre": "Suavizante de telas"
      },
      "categoria": "Limpieza del hogar",
      "clase": "B",
      "pct_acum": 91.1,
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
      "pct_acum": 92.2,
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
      "pct_acum": 93.3,
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
      "pct_acum": 94.3,
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
      "pct_acum": 95.2,
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
      "clase": "C",
      "pct_acum": 96.1,
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
      "pct_acum": 97.0,
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
      "pct_acum": 97.9,
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
      "pct_acum": 98.6,
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
      "existencia": 131,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.02,
      "cobertura_dias": 5895.0,
      "rotacion": 0.02,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 5895 días, exceso de stock",
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
X-Traza-Id: c61da0df-b346-44c4-84a5-0324181afa1c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 7 ms · traza `c61da0df-b346-44c4-84a5-0324181afa1c`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "c61da0df-b346-44c4-84a5-0324181afa1c"
  }
}
```

### SUR-09 · Restricciones de un microhub · PASA

**Objetivo.** Espacio y presupuesto.

**Petición.** `GET http://surtido:5122/api/v1/surtido/restricciones/1`

```http
Accept: application/json
X-Traza-Id: 8829d191-9562-42c2-92c5-bef862cf60b6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 27 ms · traza `8829d191-9562-42c2-92c5-bef862cf60b6`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "espacio_total": 3600.0,
  "presupuesto": 120000.0,
  "actualizado_en": "2026-11-26T14:25:36-06:00"
}
```

### SUR-10 · Cambiar las restricciones · PASA

**Objetivo.** El planeador fija otro espacio y presupuesto.

**Petición.** `PUT http://surtido:5122/api/v1/surtido/restricciones/1`

```http
Accept: application/json
X-Traza-Id: 2a9ef238-f933-47ae-951d-26498f996917
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "espacio_total": 3700.0,
  "presupuesto": 120000.0
}
```

**Respuesta.** HTTP 200 (esperado 200) · 52 ms · traza `2a9ef238-f933-47ae-951d-26498f996917`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "espacio_total": 3700.0,
  "presupuesto": 120000.0,
  "actualizado_en": "2026-11-26T15:23:33-06:00"
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
      "actualizado_en": "2026-11-26T14:25:36.309036-06:00"
    },
    "valores_nuevos": {
      "espacio_total": 3700.0,
      "actualizado_en": "2026-11-26T15:23:33.099693-06:00"
    }
  }
]
```

### SUR-19 · Cambiar las restricciones con PATCH · PASA

**Objetivo.** PATCH es alias de PUT.

**Petición.** `PATCH http://surtido:5122/api/v1/surtido/restricciones/1`

```http
Accept: application/json
X-Traza-Id: 6679711b-b185-4654-927a-3833b377f5d1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "espacio_total": 3650.0,
  "presupuesto": 120000.0
}
```

**Respuesta.** HTTP 200 (esperado 200) · 49 ms · traza `6679711b-b185-4654-927a-3833b377f5d1`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "espacio_total": 3650.0,
  "presupuesto": 120000.0,
  "actualizado_en": "2026-11-26T15:23:33-06:00"
}
```

### SUR-11 · Cambiar restricciones sin permiso · PASA

**Objetivo.** Solo surtido.editar.

**Petición.** `PUT http://surtido:5122/api/v1/surtido/restricciones/1`

```http
Accept: application/json
X-Traza-Id: 9ed65657-b269-4628-96c7-5d722e00bb78
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{
  "espacio_total": 10
}
```

**Respuesta.** HTTP 403 (esperado 403) · 29 ms · traza `9ed65657-b269-4628-96c7-5d722e00bb78`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "9ed65657-b269-4628-96c7-5d722e00bb78"
  }
}
```

### SUR-12 · Espacio inválido · PASA

**Objetivo.** Mayor que cero.

**Petición.** `PUT http://surtido:5122/api/v1/surtido/restricciones/1`

```http
Accept: application/json
X-Traza-Id: fea1018f-7cf9-4022-8d42-c0495252cc6d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "espacio_total": 0
}
```

**Respuesta.** HTTP 422 (esperado 422) · 7 ms · traza `fea1018f-7cf9-4022-8d42-c0495252cc6d`

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
    "traza_id": "fea1018f-7cf9-4022-8d42-c0495252cc6d"
  }
}
```

### SUR-13 · Guardar la recomendación · PASA

**Objetivo.** Queda con sus líneas y los supuestos usados, para compararla después.

**Petición.** `POST http://surtido:5122/api/v1/surtido/recomendaciones`

```http
Accept: application/json
X-Traza-Id: 6f71c215-387f-46c8-82da-20105995ec1e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "nota": "Evidencia de la Ola 2"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 446 ms · traza `6f71c215-387f-46c8-82da-20105995ec1e`

```json
{
  "id": 37,
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
    "clase_b": 12,
    "clase_c": 7,
    "unidades_a_comprar": 1,
    "con_costo_estimado": 51,
    "espacio": {
      "total": 3600.0,
      "ocupado": 3508.0,
      "sugerido": 1.0,
      "ocupacion_pct": 97.5
    },
    "presupuesto": {
      "total": 120000.0,
      "requerido": 27.36,
      "uso_pct": 0.0
    }
  },
  "creado_por": 5,
  "creado_en": "2026-11-26T15:23:33-06:00",
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
        "id": 48,
        "clave_interna": "HI-003",
        "nombre": "Pasta dental"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 20,
      "existencia": 74,
      "sugerido": 0,
      "margen_unitario": 8.96,
      "rotacion": 0.27,
      "motivo": "cobertura de 333 días, exceso de stock"
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
        "id": 8,
        "clave_interna": "AB-008",
        "nombre": "Pasta para sopa surtida"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 12,
      "existencia": 21,
      "sugerido": 0,
      "margen_unitario": 2.66,
      "rotacion": 0.57,
      "motivo": "cobertura de 158 días, exceso de stock"
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
        "id": 2,
        "clave_interna": "AB-002",
        "nombre": "Arroz superextra"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 11,
      "existencia": 36,
      "sugerido": 0,
      "margen_unitario": 8.37,
      "rotacion": 0.31,
      "motivo": "cobertura de 295 días, exceso de stock"
    },
    {
      "producto": {
        "id": 26,
        "clave_interna": "BE-006",
        "nombre": "Bebida de soya"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 11,
      "existencia": 17,
      "sugerido": 0,
      "margen_unitario": 8.96,
      "rotacion": 0.65,
      "motivo": "cobertura de 139 días, exceso de stock"
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
      "existencia": 455,
      "sugerido": 0,
      "margen_unitario": 5.46,
      "rotacion": 0.02,
      "motivo": "cobertura de 4550 días, exceso de stock"
    },
    {
      "producto": {
        "id": 18,
        "clave_interna": "AB-018",
        "nombre": "Pan de caja blanco"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 9,
      "existencia": 78,
      "sugerido": 0,
      "margen_unitario": 12.32,
      "rotacion": 0.12,
      "motivo": "cobertura de 780 días, exceso de stock"
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
      "existencia": 86,
      "sugerido": 0,
      "margen_unitario": 7.28,
      "rotacion": 0.09,
      "motivo": "cobertura de 968 días, exceso de stock"
    },
    {
      "producto": {
        "id": 22,
        "clave_interna": "BE-002",
        "nombre": "Agua embotellada"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 8,
      "existencia": 69,
      "sugerido": 0,
      "margen_unitario": 4.2,
      "rotacion": 0.12,
      "motivo": "cobertura de 776 días, exceso de stock"
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
        "id": 10,
        "clave_interna": "AB-010",
        "nombre": "Sardina en salsa de tomate"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 782,
      "sugerido": 0,
      "margen_unitario": 7.42,
      "rotacion": 0.01,
      "motivo": "cobertura de 10054 días, exceso de stock"
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
        "id": 35,
        "clave_interna": "LA-007",
        "nombre": "Mantequilla"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 64,
      "sugerido": 0,
      "margen_unitario": 6.16,
      "rotacion": 0.11,
      "motivo": "cobertura de 823 días, exceso de stock"
    },
    {
      "producto": {
        "id": 47,
        "clave_interna": "HI-002",
        "nombre": "Shampoo"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 36,
      "sugerido": 0,
      "margen_unitario": 15.12,
      "rotacion": 0.19,
      "motivo": "cobertura de 463 días, exceso de stock"
    },
    {
      "producto": {
        "id": 49,
        "clave_interna": "HI-004",
        "nombre": "Desodorante"
      },
      "clase": "B",
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
      "clase": "C",
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
      "existencia": 131,
      "sugerido": 0,
      "margen_unitario": 16.24,
      "rotacion": 0.02,
      "motivo": "cobertura de 5895 días, exceso de stock"
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
    "id": 37,
    "microhub_id": 1,
    "resumen": {
      "productos": 51,
      "aumentar": 1,
      "mantener": 0,
      "reducir": 50,
      "eliminar": 0,
      "excluir": 0,
      "clase_a": 32,
      "clase_b": 12,
      "clase_c": 7,
      "unidades_a_comprar": 1,
      "con_costo_estimado": 51,
      "espacio": {
        "total": 3600.0,
        "ocupado": 3508.0,
        "sugerido": 1.0,
        "ocupacion_pct": 97.5
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
X-Traza-Id: 213ee062-4b51-42ed-b6c9-c0fde80c8621
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 45 ms · traza `213ee062-4b51-42ed-b6c9-c0fde80c8621`

```json
{
  "datos": [
    {
      "id": 37,
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
        "clase_b": 12,
        "clase_c": 7,
        "unidades_a_comprar": 1,
        "con_costo_estimado": 51,
        "espacio": {
          "total": 3600.0,
          "ocupado": 3508.0,
          "sugerido": 1.0,
          "ocupacion_pct": 97.5
        },
        "presupuesto": {
          "total": 120000.0,
          "requerido": 27.36,
          "uso_pct": 0.0
        }
      },
      "creado_por": 5,
      "creado_en": "2026-11-26T15:23:33-06:00"
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

**Petición.** `GET http://surtido:5122/api/v1/surtido/recomendaciones/37`

```http
Accept: application/json
X-Traza-Id: fe2aca91-d29b-4a48-8567-bbadafb93e9a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 47 ms · traza `fe2aca91-d29b-4a48-8567-bbadafb93e9a`

```json
{
  "id": 37,
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
    "clase_b": 12,
    "clase_c": 7,
    "unidades_a_comprar": 1,
    "con_costo_estimado": 51,
    "espacio": {
      "total": 3600.0,
      "ocupado": 3508.0,
      "sugerido": 1.0,
      "ocupacion_pct": 97.5
    },
    "presupuesto": {
      "total": 120000.0,
      "requerido": 27.36,
      "uso_pct": 0.0
    }
  },
  "creado_por": 5,
  "creado_en": "2026-11-26T15:23:33-06:00",
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
        "id": 48,
        "clave_interna": "HI-003",
        "nombre": "Pasta dental"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 20,
      "existencia": 74,
      "sugerido": 0,
      "margen_unitario": 8.96,
      "rotacion": 0.27,
      "motivo": "cobertura de 333 días, exceso de stock"
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
        "id": 8,
        "clave_interna": "AB-008",
        "nombre": "Pasta para sopa surtida"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 12,
      "existencia": 21,
      "sugerido": 0,
      "margen_unitario": 2.66,
      "rotacion": 0.57,
      "motivo": "cobertura de 158 días, exceso de stock"
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
        "id": 2,
        "clave_interna": "AB-002",
        "nombre": "Arroz superextra"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 11,
      "existencia": 36,
      "sugerido": 0,
      "margen_unitario": 8.37,
      "rotacion": 0.31,
      "motivo": "cobertura de 295 días, exceso de stock"
    },
    {
      "producto": {
        "id": 26,
        "clave_interna": "BE-006",
        "nombre": "Bebida de soya"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 11,
      "existencia": 17,
      "sugerido": 0,
      "margen_unitario": 8.96,
      "rotacion": 0.65,
      "motivo": "cobertura de 139 días, exceso de stock"
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
      "existencia": 455,
      "sugerido": 0,
      "margen_unitario": 5.46,
      "rotacion": 0.02,
      "motivo": "cobertura de 4550 días, exceso de stock"
    },
    {
      "producto": {
        "id": 18,
        "clave_interna": "AB-018",
        "nombre": "Pan de caja blanco"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 9,
      "existencia": 78,
      "sugerido": 0,
      "margen_unitario": 12.32,
      "rotacion": 0.12,
      "motivo": "cobertura de 780 días, exceso de stock"
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
      "existencia": 86,
      "sugerido": 0,
      "margen_unitario": 7.28,
      "rotacion": 0.09,
      "motivo": "cobertura de 968 días, exceso de stock"
    },
    {
      "producto": {
        "id": 22,
        "clave_interna": "BE-002",
        "nombre": "Agua embotellada"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 8,
      "existencia": 69,
      "sugerido": 0,
      "margen_unitario": 4.2,
      "rotacion": 0.12,
      "motivo": "cobertura de 776 días, exceso de stock"
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
        "id": 10,
        "clave_interna": "AB-010",
        "nombre": "Sardina en salsa de tomate"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 782,
      "sugerido": 0,
      "margen_unitario": 7.42,
      "rotacion": 0.01,
      "motivo": "cobertura de 10054 días, exceso de stock"
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
        "id": 35,
        "clave_interna": "LA-007",
        "nombre": "Mantequilla"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 64,
      "sugerido": 0,
      "margen_unitario": 6.16,
      "rotacion": 0.11,
      "motivo": "cobertura de 823 días, exceso de stock"
    },
    {
      "producto": {
        "id": 47,
        "clave_interna": "HI-002",
        "nombre": "Shampoo"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 36,
      "sugerido": 0,
      "margen_unitario": 15.12,
      "rotacion": 0.19,
      "motivo": "cobertura de 463 días, exceso de stock"
    },
    {
      "producto": {
        "id": 49,
        "clave_interna": "HI-004",
        "nombre": "Desodorante"
      },
      "clase": "B",
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
      "clase": "C",
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
      "existencia": 131,
      "sugerido": 0,
      "margen_unitario": 16.24,
      "rotacion": 0.02,
      "motivo": "cobertura de 5895 días, exceso de stock"
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

**Petición.** `GET http://surtido:5122/api/v1/surtido/recomendaciones/37`

```http
Accept: application/json
X-Traza-Id: 2608ce76-9ee8-4705-95aa-a7e85404d4bf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 25 ms · traza `2608ce76-9ee8-4705-95aa-a7e85404d4bf`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "2608ce76-9ee8-4705-95aa-a7e85404d4bf"
  }
}
```

### SUR-16 · Guardar sin permiso · PASA

**Objetivo.** El operador no tiene surtido.editar.

**Petición.** `POST http://surtido:5122/api/v1/surtido/recomendaciones`

```http
Accept: application/json
X-Traza-Id: d4cfb0c5-ade0-4d18-92fc-4f2f0b544eeb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1
}
```

**Respuesta.** HTTP 403 (esperado 403) · 31 ms · traza `d4cfb0c5-ade0-4d18-92fc-4f2f0b544eeb`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "d4cfb0c5-ade0-4d18-92fc-4f2f0b544eeb"
  }
}
```

### SUR-17 · Supuestos del surtido · PASA

**Objetivo.** Cortes ABC, días de cobertura y ventana de análisis.

**Petición.** `GET http://surtido:5122/api/v1/surtido/supuestos`

```http
Accept: application/json
X-Traza-Id: 5a9afc70-fd9b-46e5-af1a-99fdeaf898ab
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 37 ms · traza `5a9afc70-fd9b-46e5-af1a-99fdeaf898ab`

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
X-Traza-Id: 8034a8da-087b-4d38-ba45-a03ac7b1cacb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 82 ms · traza `8034a8da-087b-4d38-ba45-a03ac7b1cacb`

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
      "id": 591,
      "folio": "PED-20261126-000591",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "latitud": 25.752587,
      "longitud": -100.364483,
      "total": 138.0,
      "listo_en": "2026-11-26T15:23:34-06:00"
    },
    {
      "id": 592,
      "folio": "PED-20261126-000592",
      "zona": {
        "id": 1,
        "nombre": "San Bernabé Centro"
      },
      "latitud": 25.742956,
      "longitud": -100.361173,
      "total": 161.0,
      "listo_en": "2026-11-26T15:23:34-06:00"
    },
    {
      "id": 594,
      "folio": "PED-20261126-000594",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "latitud": 25.754086,
      "longitud": -100.366767,
      "total": 156.0,
      "listo_en": "2026-11-26T15:23:34-06:00"
    },
    {
      "id": 595,
      "folio": "PED-20261126-000595",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "latitud": 25.752587,
      "longitud": -100.364483,
      "total": 187.0,
      "listo_en": "2026-11-26T15:23:34-06:00"
    },
    {
      "id": 596,
      "folio": "PED-20261126-000596",
      "zona": {
        "id": 1,
        "nombre": "San Bernabé Centro"
      },
      "latitud": 25.745527,
      "longitud": -100.362981,
      "total": 126.0,
      "listo_en": "2026-11-26T15:23:34-06:00"
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
    "id": 591,
    "folio": "PED-20261126-000591",
    "estado": "en_preparacion",
    "zona_id": 2,
    "listo": true
  },
  {
    "id": 592,
    "folio": "PED-20261126-000592",
    "estado": "en_preparacion",
    "zona_id": 1,
    "listo": true
  },
  {
    "id": 594,
    "folio": "PED-20261126-000594",
    "estado": "en_preparacion",
    "zona_id": 2,
    "listo": true
  },
  {
    "id": 595,
    "folio": "PED-20261126-000595",
    "estado": "en_preparacion",
    "zona_id": 2,
    "listo": true
  },
  {
    "id": 596,
    "folio": "PED-20261126-000596",
    "estado": "en_preparacion",
    "zona_id": 1,
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
X-Traza-Id: e2e7e38b-945a-4f30-9cbc-76d4d87aa06e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "pedido_ids": [
    428,
    591,
    592,
    594,
    595,
    596
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 199 ms · traza `e2e7e38b-945a-4f30-9cbc-76d4d87aa06e`

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
            "id": 591,
            "folio": "PED-20261126-000591"
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
            "id": 595,
            "folio": "PED-20261126-000595"
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
        },
        {
          "orden": 4,
          "pedido": {
            "id": 594,
            "folio": "PED-20261126-000594"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.754086,
          "longitud": -100.366767,
          "tramo_km": 0.24,
          "minutos_acum": 18.8
        }
      ],
      "distancia_km": 1.04,
      "minutos": 18.8,
      "costo": 76.66
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
            "id": 596,
            "folio": "PED-20261126-000596"
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
            "id": 592,
            "folio": "PED-20261126-000592"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.742956,
          "longitud": -100.361173,
          "tramo_km": 0.44,
          "minutos_acum": 10.2
        }
      ],
      "distancia_km": 0.82,
      "minutos": 10.2,
      "costo": 39.7
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 2,
    "paradas": 6,
    "distancia_km": 1.86,
    "minutos_maximo": 18.8,
    "costo": 116.36
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
X-Traza-Id: 7cb77004-335a-41b9-86e7-6a9f54464816
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "pedido_ids": [
    428,
    591,
    592,
    594,
    595,
    596
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 114 ms · traza `7cb77004-335a-41b9-86e7-6a9f54464816`

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
      "distancia_km": 5.53,
      "minutos": 39.1,
      "costo": 132.91,
      "mejora_pct": 0.0
    },
    {
      "metodo": "Vecino más cercano",
      "distancia_km": 2.65,
      "minutos": 31.2,
      "costo": 119.92,
      "mejora_pct": 52.1
    },
    {
      "metodo": "Vecino más cercano + 2-opt",
      "distancia_km": 2.65,
      "minutos": 31.2,
      "costo": 119.92,
      "mejora_pct": 52.1
    },
    {
      "metodo": "TSP exacto",
      "distancia_km": 2.65,
      "minutos": 31.2,
      "costo": 119.92,
      "mejora_pct": 52.1
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
X-Traza-Id: 539cd0d8-a169-4a3c-ab5a-4a36ac31e3c4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "pedido_ids": [
    428,
    591,
    592,
    594,
    595,
    596
  ],
  "metodo": "exacto"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 218 ms · traza `539cd0d8-a169-4a3c-ab5a-4a36ac31e3c4`

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
            "id": 591,
            "folio": "PED-20261126-000591"
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
            "id": 595,
            "folio": "PED-20261126-000595"
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
        },
        {
          "orden": 4,
          "pedido": {
            "id": 594,
            "folio": "PED-20261126-000594"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.754086,
          "longitud": -100.366767,
          "tramo_km": 0.24,
          "minutos_acum": 18.8
        }
      ],
      "distancia_km": 1.04,
      "minutos": 18.8,
      "costo": 76.66
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
            "id": 596,
            "folio": "PED-20261126-000596"
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
            "id": 592,
            "folio": "PED-20261126-000592"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.742956,
          "longitud": -100.361173,
          "tramo_km": 0.44,
          "minutos_acum": 10.2
        }
      ],
      "distancia_km": 0.82,
      "minutos": 10.2,
      "costo": 39.7
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 2,
    "paradas": 6,
    "distancia_km": 1.86,
    "minutos_maximo": 18.8,
    "costo": 116.36
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
X-Traza-Id: 94aa7744-3cf8-4156-b684-b78ae2ae5926
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "pedido_ids": [
    428,
    591,
    592,
    594,
    595,
    596
  ],
  "guardar": true
}
```

**Respuesta.** HTTP 201 (esperado 201) · 326 ms · traza `94aa7744-3cf8-4156-b684-b78ae2ae5926`

```json
{
  "id": 103,
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
            "id": 591,
            "folio": "PED-20261126-000591"
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
            "id": 595,
            "folio": "PED-20261126-000595"
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
        },
        {
          "orden": 4,
          "pedido": {
            "id": 594,
            "folio": "PED-20261126-000594"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.754086,
          "longitud": -100.366767,
          "tramo_km": 0.24,
          "minutos_acum": 18.8
        }
      ],
      "distancia_km": 1.04,
      "minutos": 18.8,
      "costo": 76.66
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
            "id": 596,
            "folio": "PED-20261126-000596"
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
            "id": 592,
            "folio": "PED-20261126-000592"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.742956,
          "longitud": -100.361173,
          "tramo_km": 0.44,
          "minutos_acum": 10.2
        }
      ],
      "distancia_km": 0.82,
      "minutos": 10.2,
      "costo": 39.7
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 2,
    "paradas": 6,
    "distancia_km": 1.86,
    "minutos_maximo": 18.8,
    "costo": 116.36
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
    "id": 103,
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

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes/103/ajustes`

```http
Accept: application/json
X-Traza-Id: 9a773f3a-e3b9-4d7b-b2c2-8e4e5ebc7aa5
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

**Respuesta.** HTTP 200 (esperado 200) · 242 ms · traza `9a773f3a-e3b9-4d7b-b2c2-8e4e5ebc7aa5`

```json
{
  "id": 103,
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
            "id": 591,
            "folio": "PED-20261126-000591"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.67,
          "minutos_acum": 30.8
        },
        {
          "orden": 2,
          "pedido": {
            "id": 595,
            "folio": "PED-20261126-000595"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.0,
          "minutos_acum": 34.8
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
          "minutos_acum": 39.2
        },
        {
          "orden": 4,
          "pedido": {
            "id": 594,
            "folio": "PED-20261126-000594"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.754086,
          "longitud": -100.366767,
          "tramo_km": 0.24,
          "minutos_acum": 43.8
        }
      ],
      "distancia_km": 1.04,
      "minutos": 43.8,
      "costo": 76.66
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
            "id": 596,
            "folio": "PED-20261126-000596"
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
            "id": 592,
            "folio": "PED-20261126-000592"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.742956,
          "longitud": -100.361173,
          "tramo_km": 0.44,
          "minutos_acum": 10.2
        }
      ],
      "distancia_km": 0.82,
      "minutos": 10.2,
      "costo": 39.7
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 2,
    "paradas": 6,
    "distancia_km": 1.86,
    "minutos_maximo": 43.8,
    "costo": 116.36
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
    "PED-20261126-000591",
    "PED-20261126-000595",
    "PED-20261126-000428",
    "PED-20261126-000594"
  ]
}
```

### RUT-07 · Quitar un pedido · PASA

**Objetivo.** Recalcula la ruta afectada con el mismo método.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes/103/ajustes`

```http
Accept: application/json
X-Traza-Id: f6b85679-70db-4baa-a7bd-e6705adc8010
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "tipo": "quitar_pedido",
  "pedido_id": 591
}
```

**Respuesta.** HTTP 200 (esperado 200) · 158 ms · traza `f6b85679-70db-4baa-a7bd-e6705adc8010`

```json
{
  "id": 103,
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
            "id": 595,
            "folio": "PED-20261126-000595"
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
          "minutos_acum": 10.2
        },
        {
          "orden": 3,
          "pedido": {
            "id": 594,
            "folio": "PED-20261126-000594"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.754086,
          "longitud": -100.366767,
          "tramo_km": 0.24,
          "minutos_acum": 14.8
        }
      ],
      "distancia_km": 1.04,
      "minutos": 14.8,
      "costo": 58.66
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
            "id": 596,
            "folio": "PED-20261126-000596"
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
            "id": 592,
            "folio": "PED-20261126-000592"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.742956,
          "longitud": -100.361173,
          "tramo_km": 0.44,
          "minutos_acum": 10.2
        }
      ],
      "distancia_km": 0.82,
      "minutos": 10.2,
      "costo": 39.7
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 2,
    "paradas": 5,
    "distancia_km": 1.86,
    "minutos_maximo": 14.8,
    "costo": 98.36
  },
  "cambios": [
    "Se quitó el pedido PED-20261126-000591; la ruta de Ramiro Alanís Lozano se recalculó con 3 paradas."
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

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes/103/ajustes`

```http
Accept: application/json
X-Traza-Id: c1e6dad8-d4a3-43fe-9854-e0083f88b55b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "tipo": "agregar_pedido",
  "pedido_id": 591
}
```

**Respuesta.** HTTP 200 (esperado 200) · 241 ms · traza `c1e6dad8-d4a3-43fe-9854-e0083f88b55b`

```json
{
  "id": 103,
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
            "id": 595,
            "folio": "PED-20261126-000595"
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
          "minutos_acum": 10.2
        },
        {
          "orden": 3,
          "pedido": {
            "id": 594,
            "folio": "PED-20261126-000594"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.754086,
          "longitud": -100.366767,
          "tramo_km": 0.24,
          "minutos_acum": 14.8
        }
      ],
      "distancia_km": 1.04,
      "minutos": 14.8,
      "costo": 58.66
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
            "id": 591,
            "folio": "PED-20261126-000591"
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
            "id": 596,
            "folio": "PED-20261126-000596"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.745527,
          "longitud": -100.362981,
          "tramo_km": 1.04,
          "minutos_acum": 12.7
        },
        {
          "orden": 3,
          "pedido": {
            "id": 592,
            "folio": "PED-20261126-000592"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.742956,
          "longitud": -100.361173,
          "tramo_km": 0.44,
          "minutos_acum": 17.9
        }
      ],
      "distancia_km": 2.15,
      "minutos": 17.9,
      "costo": 63.65
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 2,
    "paradas": 6,
    "distancia_km": 3.19,
    "minutos_maximo": 17.9,
    "costo": 122.31
  },
  "cambios": [
    "Se agregó el pedido PED-20261126-000591 a la ruta de Diana Sepúlveda Ibarra; ahora tiene 3 paradas."
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

**Petición.** `GET http://rutas:5118/api/v1/rutas/planes/103`

```http
Accept: application/json
X-Traza-Id: 7b794de7-f38f-4c0e-ab41-e8443fecdaec
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 31 ms · traza `7b794de7-f38f-4c0e-ab41-e8443fecdaec`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "7b794de7-f38f-4c0e-ab41-e8443fecdaec"
  }
}
```

### RUT-10 · Confirmar el plan · PASA

**Objetivo.** Comprueba que los pedidos sigan listos y deja las rutas en plan_ruta.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes/103/confirmar`

```http
Accept: application/json
X-Traza-Id: 943be3a8-217f-4ea6-bddc-cfc0721c89e6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 232 ms · traza `943be3a8-217f-4ea6-bddc-cfc0721c89e6`

```json
{
  "id": 103,
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
            "id": 595,
            "folio": "PED-20261126-000595"
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
          "minutos_acum": 10.2
        },
        {
          "orden": 3,
          "pedido": {
            "id": 594,
            "folio": "PED-20261126-000594"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.754086,
          "longitud": -100.366767,
          "tramo_km": 0.24,
          "minutos_acum": 14.8
        }
      ],
      "distancia_km": 1.04,
      "minutos": 14.8,
      "costo": 58.66
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
            "id": 591,
            "folio": "PED-20261126-000591"
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
            "id": 596,
            "folio": "PED-20261126-000596"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.745527,
          "longitud": -100.362981,
          "tramo_km": 1.04,
          "minutos_acum": 12.7
        },
        {
          "orden": 3,
          "pedido": {
            "id": 592,
            "folio": "PED-20261126-000592"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.742956,
          "longitud": -100.361173,
          "tramo_km": 0.44,
          "minutos_acum": 17.9
        }
      ],
      "distancia_km": 2.15,
      "minutos": 17.9,
      "costo": 63.65
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 2,
    "paradas": 6,
    "distancia_km": 3.19,
    "minutos_maximo": 17.9,
    "costo": 122.31
  },
  "cambios": [
    "Se agregó el pedido PED-20261126-000591 a la ruta de Diana Sepúlveda Ibarra; ahora tiene 3 paradas."
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
    "id": 98,
    "repartidor_id": 7,
    "metodo": "TSP exacto",
    "paradas": 3,
    "distancia_km": "1.04",
    "minutos": "14.8",
    "costo_estimado": "58.66"
  },
  {
    "id": 99,
    "repartidor_id": 8,
    "metodo": "TSP exacto",
    "paradas": 3,
    "distancia_km": "2.15",
    "minutos": "17.9",
    "costo_estimado": "63.65"
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

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes/103/confirmar`

```http
Accept: application/json
X-Traza-Id: 21feefac-4e61-4fe0-b194-b08b047eec4b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 409 (esperado 409) · 25 ms · traza `21feefac-4e61-4fe0-b194-b08b047eec4b`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Solo se confirma un plan propuesto; este está confirmado.",
    "traza_id": "21feefac-4e61-4fe0-b194-b08b047eec4b"
  }
}
```

### RUT-12 · Planes guardados · PASA

**Objetivo.** Lista con estado, rutas, paradas, distancia y costo.

**Petición.** `GET http://rutas:5118/api/v1/rutas/planes?microhub_id=1`

```http
Accept: application/json
X-Traza-Id: d264f636-7d15-451e-bad1-678b226f4035
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 50 ms · traza `d264f636-7d15-451e-bad1-678b226f4035`

```json
{
  "datos": [
    {
      "id": 103,
      "estado": "confirmado",
      "version": 4,
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "fecha": "2026-11-26",
      "rutas": 2,
      "paradas": 6,
      "distancia_km": 3.19,
      "costo": 122.31,
      "creado_por": 5,
      "creado_en": "2026-11-26T15:23:35-06:00"
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

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes/104/cancelar`

```http
Accept: application/json
X-Traza-Id: 1eaef179-afb9-4790-b552-b559b0f87a3e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 75 ms · traza `1eaef179-afb9-4790-b552-b559b0f87a3e`

```json
{
  "id": 104,
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
            "id": 591,
            "folio": "PED-20261126-000591"
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
            "id": 595,
            "folio": "PED-20261126-000595"
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
        },
        {
          "orden": 4,
          "pedido": {
            "id": 594,
            "folio": "PED-20261126-000594"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.754086,
          "longitud": -100.366767,
          "tramo_km": 0.24,
          "minutos_acum": 18.8
        }
      ],
      "distancia_km": 1.04,
      "minutos": 18.8,
      "costo": 76.66
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
            "id": 596,
            "folio": "PED-20261126-000596"
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
            "id": 592,
            "folio": "PED-20261126-000592"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.742956,
          "longitud": -100.361173,
          "tramo_km": 0.44,
          "minutos_acum": 10.2
        }
      ],
      "distancia_km": 0.82,
      "minutos": 10.2,
      "costo": 39.7
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 2,
    "paradas": 6,
    "distancia_km": 1.86,
    "minutos_maximo": 18.8,
    "costo": 116.36
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
X-Traza-Id: 5296427b-ea78-4dd6-be2b-48bf0059069c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 3
}
```

**Respuesta.** HTTP 422 (esperado 422) · 114 ms · traza `5296427b-ea78-4dd6-be2b-48bf0059069c`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "No hay pedidos listos para despachar en ese microhub.",
    "traza_id": "5296427b-ea78-4dd6-be2b-48bf0059069c"
  }
}
```

### RUT-15 · Pedidos que no están listos · PASA

**Objetivo.** Un pedido ajeno o no listo se rechaza.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/json
X-Traza-Id: b22319e5-e0c5-459b-bc47-24be60e9eb41
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

**Respuesta.** HTTP 422 (esperado 422) · 107 ms · traza `b22319e5-e0c5-459b-bc47-24be60e9eb41`

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
    "traza_id": "b22319e5-e0c5-459b-bc47-24be60e9eb41"
  }
}
```

### RUT-16 · El operador planea otro microhub · PASA

**Objetivo.** No puede.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/json
X-Traza-Id: 21535d02-e491-4675-8d7a-560af4bac1ab
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "pedido_ids": [
    428,
    591,
    592,
    594,
    595,
    596
  ]
}
```

**Respuesta.** HTTP 403 (esperado 403) · 6 ms · traza `21535d02-e491-4675-8d7a-560af4bac1ab`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "21535d02-e491-4675-8d7a-560af4bac1ab"
  }
}
```

### RUT-17 · El auditor intenta planear · PASA

**Objetivo.** Consulta, no planea.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/json
X-Traza-Id: cf8f8311-6c90-4f69-b841-fc007ba4b443
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1
}
```

**Respuesta.** HTTP 403 (esperado 403) · 41 ms · traza `cf8f8311-6c90-4f69-b841-fc007ba4b443`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "cf8f8311-6c90-4f69-b841-fc007ba4b443"
  }
}
```

### RUT-18 · Plan en XML con lista de pedidos · PASA

**Objetivo.** El cuerpo XML lleva la lista de pedidos y se valida contra rutas.xsd.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/xml
X-Traza-Id: 17e98e31-9b55-4a5f-9236-53d575bcaca0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><ruta_plan_nuevo xmlns="urn:microhubs:v1"><microhub_id>1</microhub_id><pedido_ids><id>428</id><id>591</id><id>592</id></pedido_ids><metodo>exacto</metodo></ruta_plan_nuevo>
```

**Respuesta.** HTTP 200 (esperado 200) · 377 ms · traza `17e98e31-9b55-4a5f-9236-53d575bcaca0`

```xml
<?xml version='1.0' encoding='utf-8'?>
<ruta_plan xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id xsi:nil="true" /><estado>calculo</estado><version>1</version><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><fecha>2026-11-26</fecha><metodo_pedido>exacto</metodo_pedido><rutas><ruta><repartidor><id>7</id><nombre>Ramiro Alanís Lozano</nombre></repartidor><metodo>TSP exacto</metodo><zonas><nombre_zona>Valles de San Bernabé</nombre_zona></zonas><paradas><parada><orden>1</orden><pedido><id>591</id><folio>PED-20261126-000591</folio></pedido><zona><id>2</id><nombre>Valles de San Bernabé</nombre></zona><latitud>25.752587</latitud><longitud>-100.364483</longitud><tramo_km>0.67</tramo_km><minutos_acum>5.8</minutos_acum></parada><parada><orden>2</orden><pedido><id>428</id><folio>PED-20261126-000428</folio></pedido><zona><id>2</id><nombre>Valles de San Bernabé</nombre></zona><latitud>25.753225</latitud><longitud>-100.365213</longitud><tramo_km>0.13</tramo_km><minutos_acum>10.2</minutos_acum></parada></paradas><distancia_km>0.8</distancia_km><minutos>10.2</minutos><costo>39.59</costo></ruta><ruta><repartidor><id>8</id><nombre>Diana Sepúlveda Ibarra</nombre></repartidor><metodo>TSP exacto</metodo><zonas><nombre_zona>San Bernabé Centro</nombre_zona></zonas><paradas><parada><orden>1</orden><pedido><id>592</id><folio>PED-20261126-000592</folio></pedido><zona><id>1</id><nombre>San Bernabé Centro</nombre></zona><latitud>25.742956</latitud><longitud>-100.361173</longitud><tramo_km>0.82</tramo_km><minutos_acum>6.2</minutos_acum></parada></paradas><distancia_km>0.82</distancia_km><minutos>6.2</minutos><costo>21.68</costo></ruta></rutas><sin_asignar /><total><rutas>2</rutas><paradas>3</paradas><distancia_km>1.62</distancia_km><minutos_maximo>10.2</minutos_maximo><costo>61.27</costo></total><cambios /><supuestos_usados><supuesto><clave>velocidad_reparto_kmh</clave><valor>22</valor><modificado>false</modificado></supuesto><supuesto><clave>tiempo_servicio_min</clave><valor>4</valor><modificado>false</modificado></supuesto><supuesto><clave>costo_km_reparto</clave><valor>4.5</valor><modificado>false</modificado></supuesto><supuesto><clave>costo_base_entrega</clave><valor>18</valor><modificado>false</modificado></supuesto><supuesto><clave>max_paradas_repartidor</clave><valor>8</valor><modificado>false</modificado></supuesto><supuesto><clave>factor_rodeo_distancia</clave><valor>1.3</valor><modificado>false</modificado></supuesto></supuestos_usados></ruta_plan>
```

### RUT-19 · Supuestos de las rutas · PASA

**Objetivo.** Velocidad, tiempo por parada, costo por km, tope de paradas y rodeo.

**Petición.** `GET http://rutas:5118/api/v1/rutas/supuestos`

```http
Accept: application/json
X-Traza-Id: ef3d824d-3074-45a1-baf3-d41373520d01
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 31 ms · traza `ef3d824d-3074-45a1-baf3-d41373520d01`

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
X-Traza-Id: e1b84b84-bc9e-429f-a9eb-bb6a38427c2d
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

**Respuesta.** HTTP 202 (esperado 202) · 1463 ms · traza `e1b84b84-bc9e-429f-a9eb-bb6a38427c2d`

```json
{
  "id": "eea71576-00d7-4e50-9597-23b4cf326d5e",
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
  "creado_en": "2026-11-26T15:23:38-06:00",
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
    "id": "eea71576-00d7-4e50-9597-23b4cf326d5e",
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

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones/eea71576-00d7-4e50-9597-23b4cf326d5e`

```http
Accept: application/json
X-Traza-Id: e0a0af19-2a04-4b35-b78e-6a8ddbd15bec
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 24 ms · traza `e0a0af19-2a04-4b35-b78e-6a8ddbd15bec`

```json
{
  "id": "eea71576-00d7-4e50-9597-23b4cf326d5e",
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
  "creado_en": "2026-11-26T15:23:38-06:00",
  "inicio_en": "2026-11-26T15:23:40-06:00",
  "fin_en": "2026-11-26T15:23:40-06:00",
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

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones/eea71576-00d7-4e50-9597-23b4cf326d5e/repetir`

```http
Accept: application/json
X-Traza-Id: ff0d58f3-abe7-4d40-b83f-6b2e2d73195b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 202 (esperado 202) · 89 ms · traza `ff0d58f3-abe7-4d40-b83f-6b2e2d73195b`

```json
{
  "id": "ba8a4787-565a-4154-a61c-3eedf76428b3",
  "nombre": "Repetición de Simulación de Microhub San Bernabé Centro 2026-11-26",
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
  "repeticion_de": "eea71576-00d7-4e50-9597-23b4cf326d5e",
  "reproducible": null,
  "error": null,
  "creado_por": 5,
  "creado_en": "2026-11-26T15:23:40-06:00",
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

### SIM-04 · La repetición coincide · PASA

**Objetivo.** Misma huella: la simulación es reproducible.

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones/ba8a4787-565a-4154-a61c-3eedf76428b3`

```http
Accept: application/json
X-Traza-Id: be5acb59-d150-4173-a2db-a67fd381caf4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 51 ms · traza `be5acb59-d150-4173-a2db-a67fd381caf4`

```json
{
  "id": "ba8a4787-565a-4154-a61c-3eedf76428b3",
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
  "repeticion_de": "eea71576-00d7-4e50-9597-23b4cf326d5e",
  "reproducible": true,
  "error": null,
  "creado_por": 5,
  "creado_en": "2026-11-26T15:23:40-06:00",
  "inicio_en": "2026-11-26T15:23:42-06:00",
  "fin_en": "2026-11-26T15:23:42-06:00",
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
    "id": "eea71576-00d7-4e50-9597-23b4cf326d5e",
    "estado": "terminada",
    "huella": "7b88bea8fcb6e15b0dc9714e258549fc8ff623fb13d10d91c72f63b04deb0054",
    "repite_a": null
  },
  {
    "id": "ba8a4787-565a-4154-a61c-3eedf76428b3",
    "estado": "terminada",
    "huella": "7b88bea8fcb6e15b0dc9714e258549fc8ff623fb13d10d91c72f63b04deb0054",
    "repite_a": "eea71576-00d7-4e50-9597-23b4cf326d5e"
  }
]
```

### SIM-05 · Otra semilla, otro resultado · PASA

**Objetivo.** Misma entrada con semilla 12: la huella cambia.

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones/4480483f-3c47-47b8-85fb-a4820abb7105`

```http
Accept: application/json
X-Traza-Id: 83bcf48a-edf3-4611-9038-67f21d138767
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 31 ms · traza `83bcf48a-edf3-4611-9038-67f21d138767`

```json
{
  "id": "4480483f-3c47-47b8-85fb-a4820abb7105",
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
  "creado_en": "2026-11-26T15:23:43-06:00",
  "inicio_en": "2026-11-26T15:23:44-06:00",
  "fin_en": "2026-11-26T15:23:44-06:00",
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

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/comparacion?ids=eea71576-00d7-4e50-9597-23b4cf326d5e,4480483f-3c47-47b8-85fb-a4820abb7105`

```http
Accept: application/json
X-Traza-Id: ff1d22ab-24ca-4f4b-817c-0c4813e05310
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 55 ms · traza `ff1d22ab-24ca-4f4b-817c-0c4813e05310`

```json
{
  "ejecuciones": [
    {
      "id": "eea71576-00d7-4e50-9597-23b4cf326d5e",
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
      "id": "4480483f-3c47-47b8-85fb-a4820abb7105",
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
  "mejor_id": "eea71576-00d7-4e50-9597-23b4cf326d5e",
  "criterio": "Mayor utilidad media entre las que pierden dinero en menos de la mitad de las réplicas."
}
```

### SIM-07 · Escenario manual · PASA

**Objetivo.** Sin microhub ni candidato, con todos los datos escritos (el escenario A).

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones`

```http
Accept: application/json
X-Traza-Id: c0f649a5-f12b-4ab9-9dbc-71f0faa0bed3
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

**Respuesta.** HTTP 202 (esperado 202) · 228 ms · traza `c0f649a5-f12b-4ab9-9dbc-71f0faa0bed3`

```json
{
  "id": "27520d88-f644-4c05-9430-dcc36246faf5",
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
  "creado_en": "2026-11-26T15:23:45-06:00",
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

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones/27520d88-f644-4c05-9430-dcc36246faf5`

```http
Accept: application/json
X-Traza-Id: 34e1e408-0a91-44d1-82c8-bc40c5bc5047
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 25 ms · traza `34e1e408-0a91-44d1-82c8-bc40c5bc5047`

```json
{
  "id": "27520d88-f644-4c05-9430-dcc36246faf5",
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
  "creado_en": "2026-11-26T15:23:45-06:00",
  "inicio_en": "2026-11-26T15:23:46-06:00",
  "fin_en": "2026-11-26T15:23:46-06:00",
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
X-Traza-Id: 4f181d9a-27a5-452b-9edf-761cc2d2aed1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "pedidos_dia": 45
}
```

**Respuesta.** HTTP 422 (esperado 422) · 29 ms · traza `4f181d9a-27a5-452b-9edf-761cc2d2aed1`

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
    "traza_id": "4f181d9a-27a5-452b-9edf-761cc2d2aed1"
  }
}
```

### SIM-10 · Demasiado trabajo · PASA

**Objetivo.** Días × réplicas no puede pasar de 200,000.

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones`

```http
Accept: application/json
X-Traza-Id: 45aaa36e-c3d7-4c19-ae0a-e5b45be77dc5
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

**Respuesta.** HTTP 422 (esperado 422) · 604 ms · traza `45aaa36e-c3d7-4c19-ae0a-e5b45be77dc5`

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
    "traza_id": "45aaa36e-c3d7-4c19-ae0a-e5b45be77dc5"
  }
}
```

### SIM-11 · Cancelar una ejecución · PASA

**Objetivo.** Una ejecución en cola o en curso se puede cancelar.

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones/b5b40d4c-5895-4eb4-b452-7ad08220261e/cancelar`

```http
Accept: application/json
X-Traza-Id: 0ac7a2d5-4ac3-4c47-9c50-a779e6bb91ba
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 112 ms · traza `0ac7a2d5-4ac3-4c47-9c50-a779e6bb91ba`

```json
{
  "id": "b5b40d4c-5895-4eb4-b452-7ad08220261e",
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
  "creado_en": "2026-11-26T15:23:48-06:00",
  "inicio_en": null,
  "fin_en": "2026-11-26T15:23:48-06:00",
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
    "id": "b5b40d4c-5895-4eb4-b452-7ad08220261e",
    "estado": "cancelada",
    "fin": true,
    "sin_resultados": true
  }
]
```

### SIM-12 · Cancelar una cancelada · PASA

**Objetivo.** Solo se cancela lo que está en cola o en curso.

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones/b5b40d4c-5895-4eb4-b452-7ad08220261e/cancelar`

```http
Accept: application/json
X-Traza-Id: 9fe1d578-e45a-4fe9-a360-21b067c0c610
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 409 (esperado 409) · 50 ms · traza `9fe1d578-e45a-4fe9-a360-21b067c0c610`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Solo se cancela una ejecución en cola o en curso; esta está cancelada.",
    "traza_id": "9fe1d578-e45a-4fe9-a360-21b067c0c610"
  }
}
```

### SIM-13 · Ejecuciones · PASA

**Objetivo.** Lista paginada, la más reciente primero.

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones?por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 9b8479bb-eacf-4e39-9bb6-fdfe8780e4e0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 47 ms · traza `9b8479bb-eacf-4e39-9bb6-fdfe8780e4e0`

```json
{
  "datos": [
    {
      "id": "b5b40d4c-5895-4eb4-b452-7ad08220261e",
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
      "creado_en": "2026-11-26T15:23:48-06:00",
      "fin_en": "2026-11-26T15:23:48-06:00"
    },
    {
      "id": "27520d88-f644-4c05-9430-dcc36246faf5",
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
      "creado_en": "2026-11-26T15:23:45-06:00",
      "fin_en": "2026-11-26T15:23:46-06:00"
    },
    {
      "id": "4480483f-3c47-47b8-85fb-a4820abb7105",
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
      "creado_en": "2026-11-26T15:23:43-06:00",
      "fin_en": "2026-11-26T15:23:44-06:00"
    },
    {
      "id": "ba8a4787-565a-4154-a61c-3eedf76428b3",
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
      "creado_en": "2026-11-26T15:23:40-06:00",
      "fin_en": "2026-11-26T15:23:42-06:00"
    },
    {
      "id": "eea71576-00d7-4e50-9597-23b4cf326d5e",
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
      "creado_en": "2026-11-26T15:23:38-06:00",
      "fin_en": "2026-11-26T15:23:40-06:00"
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
X-Traza-Id: 70497688-8f41-4be4-bb70-a586c1a92b38
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 32 ms · traza `70497688-8f41-4be4-bb70-a586c1a92b38`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "70497688-8f41-4be4-bb70-a586c1a92b38"
  }
}
```

### SIM-15 · El operador simula · PASA

**Objetivo.** Sin simulacion.ejecutar.

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones`

```http
Accept: application/json
X-Traza-Id: 3dff6af5-65cb-462f-b240-b3c13ffcbd2d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1
}
```

**Respuesta.** HTTP 403 (esperado 403) · 28 ms · traza `3dff6af5-65cb-462f-b240-b3c13ffcbd2d`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "3dff6af5-65cb-462f-b240-b3c13ffcbd2d"
  }
}
```

### SIM-16 · Poner en cola (XML) · PASA

**Objetivo.** Entrada y salida en XML, validadas contra simulacion.xsd.

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones`

```http
Accept: application/xml
X-Traza-Id: 6d045cc0-f539-4351-8687-cb3eeb6cc527
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><simulacion_nueva xmlns="urn:microhubs:v1"><microhub_id>1</microhub_id><dias>5</dias><replicas>20</replicas><semilla>3</semilla></simulacion_nueva>
```

**Respuesta.** HTTP 202 (esperado 202) · 661 ms · traza `6d045cc0-f539-4351-8687-cb3eeb6cc527`

```xml
<?xml version='1.0' encoding='utf-8'?>
<simulacion_ejecucion xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>7d1e67c5-8871-4e50-ab00-9af78f0ae87d</id><nombre>Simulación de Microhub San Bernabé Centro 2026-11-26</nombre><estado>en_cola</estado><objeto><tipo>microhub</tipo><id>1</id><nombre>Microhub San Bernabé Centro</nombre></objeto><semilla>3</semilla><version_modelo>1.0</version_modelo><dias>5</dias><replicas>20</replicas><entrada><pedidos_dia>23.6</pedidos_dia><ticket>134.83</ticket><margen_bruto>0.28</margen_bruto><costos_fijos_mes>69500</costos_fijos_mes><costo_variable_pedido>32.61</costo_variable_pedido><dias_mes>30</dias_mes><operadores>3</operadores><repartidores>3</repartidores><capacidad_fisica>150</capacidad_fisica><horas>10</horas><distancia_km>2.4</distancia_km><ausentismo>0.05</ausentismo><variacion_demanda>0.1</variacion_demanda><indice_semanal><indice>0.893</indice><indice>0.844</indice><indice>0.884</indice><indice>0.937</indice><indice>1.154</indice><indice>1.303</indice><indice>1.028</indice></indice_semanal><dia_inicio>4</dia_inicio><origen_de_datos><dato><dato>costos_fijos</dato><fuente>costos</fuente></dato><dato><dato>costo_variable_pedido</dato><fuente>costos</fuente></dato><dato><dato>ticket</dato><fuente>demanda</fuente></dato><dato><dato>margen_bruto</dato><fuente>configuracion</fuente></dato><dato><dato>pedidos_dia</dato><fuente>demanda_repartida</fuente></dato><dato><dato>operadores</dato><fuente>capacidad</fuente></dato><dato><dato>repartidores</dato><fuente>capacidad</fuente></dato><dato><dato>capacidad_fisica</dato><fuente>capacidad</fuente></dato><dato><dato>horas</dato><fuente>configuracion</fuente></dato><dato><dato>distancia_km</dato><fuente>configuracion</fuente></dato><dato><dato>ausentismo</dato><fuente>configuracion</fuente></dato><dato><dato>variacion_demanda</dato><fuente>configuracion</fuente></dato><dato><dato>indice_semanal</dato><fuente>demanda</fuente></dato></origen_de_datos></entrada><resultados xsi:nil="true" /><huella xsi:nil="true" /><repeticion_de xsi:nil="true" /><reproducible xsi:nil="true" /><error xsi:nil="true" /><creado_por>5</creado_por><creado_en>2026-11-26T15:23:49-06:00</creado_en><inicio_en xsi:nil="true" /><fin_en xsi:nil="true" /><supuestos_usados><supuesto><clave>picking_pedidos_hora</clave><valor>10</valor><modificado>false</modificado></supuesto><supuesto><clave>packing_pedidos_hora</clave><valor>20</valor><modificado>false</modificado></supuesto><supuesto><clave>despacho_pedidos_hora</clave><valor>30</valor><modificado>false</modificado></supuesto><supuesto><clave>velocidad_reparto_kmh</clave><valor>22</valor><modificado>false</modificado></supuesto><supuesto><clave>tiempo_servicio_min</clave><valor>4</valor><modificado>false</modificado></supuesto><supuesto><clave>paradas_por_viaje</clave><valor>3</valor><modificado>false</modificado></supuesto><supuesto><clave>horas_turno</clave><valor>10</valor><modificado>false</modificado></supuesto><supuesto><clave>umbral_utilizacion_riesgo</clave><valor>85</valor><modificado>false</modificado></supuesto><supuesto><clave>sim_ausentismo</clave><valor>0.05</valor><modificado>false</modificado></supuesto><supuesto><clave>sim_variacion_demanda</clave><valor>0.1</valor><modificado>false</modificado></supuesto></supuestos_usados></simulacion_ejecucion>
```

### SIM-17 · Una ejecución inexistente · PASA

**Objetivo.** Un identificador que no existe.

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones/8bec6f6e-1b30-4da4-8efb-4482d554efc4`

```http
Accept: application/json
X-Traza-Id: 7788c753-4207-47f3-9b4d-ef11ea08fe0e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 28 ms · traza `7788c753-4207-47f3-9b4d-ef11ea08fe0e`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe esa ejecución.",
    "traza_id": "7788c753-4207-47f3-9b4d-ef11ea08fe0e"
  }
}
```

### SIM-18 · Supuestos de la simulación · PASA

**Objetivo.** Réplicas, ausentismo, variación de la demanda y semilla.

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/supuestos`

```http
Accept: application/json
X-Traza-Id: 7b5ed0c8-f086-46a9-9db5-9a0b91a7372b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 33 ms · traza `7b5ed0c8-f086-46a9-9db5-9a0b91a7372b`

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

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b08a3685ea8dba9ecdb0b05/enlace`

```http
Accept: application/json
X-Traza-Id: b8786834-4b04-4273-8eaf-9b7312d559a3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 35 ms · traza `b8786834-4b04-4273-8eaf-9b7312d559a3`

```json
{
  "id": "6b08a3685ea8dba9ecdb0b05",
  "nombre": "evidencia-enlace.pdf",
  "url_firmada": "http://documentos:5107/api/v1/documentos/descarga?k=document…(207 caracteres)",
  "metodo": "GET",
  "segundos": 300,
  "expira_en": "2026-11-26T15:28:53-06:00"
}
```

**Explicación.** En la nube la URL es una firmada V4 de Cloud Storage; en local apunta al propio servicio. La base de datos no guarda el archivo.

**Evidencia en PostgreSQL.** `SELECT fecha, modulo, accion, detalle FROM auditoria WHERE entidad = 'documento' AND entidad_id = %s ORDER BY id`

```json
[
  {
    "fecha": "2026-11-26 15:23:52.989446-06:00",
    "modulo": "documentos",
    "accion": "alta",
    "detalle": "evidencia-enlace.pdf (42 bytes) a usuario 7."
  },
  {
    "fecha": "2026-11-26 15:23:53.025351-06:00",
    "modulo": "documentos",
    "accion": "descarga",
    "detalle": "Enlace de descarga de evidencia-enlace.pdf (caduca en 300 s)."
  }
]
```

### ENL-02 · Descargar con el enlace firmado · PASA

**Objetivo.** El enlace funciona sin token: la firma es el permiso.

**Petición.** `GET http://documentos:5107/api/v1/documentos/descarga?k=documentos%2F2026%2F11%2F6b08a3685ea8dba9ecdb0b05.pdf&e=1795728533&n=evidencia-enlace.pdf&t=application%2Fpdf&s=X6Hba3ECzVcXOO0M5-DFXMUv_-9koDIRWlw05ENr90M`

```http
Accept: application/json
X-Traza-Id: 40fe3a68-e92f-47a6-9e53-0cb5cf2f9dec
```

**Respuesta.** HTTP 200 (esperado 200) · 15 ms · traza `40fe3a68-e92f-47a6-9e53-0cb5cf2f9dec`

```json
%PDF-1.4 evidencia de enlace firmado %%EOF
```

### ENL-03 · Enlace manipulado · PASA

**Objetivo.** Cambiar un carácter de la firma lo invalida.

**Petición.** `GET http://documentos:5107/api/v1/documentos/descarga?k=documentos%2F2026%2F11%2F6b08a3685ea8dba9ecdb0b05.pdf&e=1795728533&n=evidencia-enlace.pdf&t=application%2Fpdf&s=X6Hba3ECzVcXOO0M5-DFXMUv_-9koDIRWlw05ENr9AA`

```http
Accept: application/json
X-Traza-Id: f2783ac9-aec6-4c27-8e47-1c4467f8440b
```

**Respuesta.** HTTP 403 (esperado 403) · 7 ms · traza `f2783ac9-aec6-4c27-8e47-1c4467f8440b`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "El enlace de descarga no es válido o ya caducó.",
    "traza_id": "f2783ac9-aec6-4c27-8e47-1c4467f8440b"
  }
}
```

## Servicio auditoria-monitoreo · puerto 5126

### MNT-01 · Forzar una verificación de todos los servicios · PASA

**Objetivo.** Pregunta la salud de cada servicio y guarda el resultado.

**Petición.** `POST http://auditoria-monitoreo:5126/api/v1/monitoreo/verificaciones`

```http
Accept: application/json
X-Traza-Id: 087319ac-8922-4ba8-ab7e-12d2835a1310
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 201 (esperado 201) · 207 ms · traza `087319ac-8922-4ba8-ab7e-12d2835a1310`

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
      "tiempo_ms": 25.5,
      "error": null
    },
    {
      "servicio": "usuarios",
      "estado": "ok",
      "tiempo_ms": 28.5,
      "error": null
    },
    {
      "servicio": "productos",
      "estado": "ok",
      "tiempo_ms": 32.4,
      "error": null
    },
    {
      "servicio": "pedidos",
      "estado": "ok",
      "tiempo_ms": 25.8,
      "error": null
    },
    {
      "servicio": "entregas",
      "estado": "ok",
      "tiempo_ms": 28.0,
      "error": null
    },
    {
      "servicio": "planeacion",
      "estado": "ok",
      "tiempo_ms": 32.5,
      "error": null
    },
    {
      "servicio": "documentos",
      "estado": "ok",
      "tiempo_ms": 28.5,
      "error": null
    },
    {
      "servicio": "zonas",
      "estado": "ok",
      "tiempo_ms": 34.3,
      "error": null
    },
    {
      "servicio": "microhubs",
      "estado": "ok",
      "tiempo_ms": 26.7,
      "error": null
    },
    {
      "servicio": "seguimiento",
      "estado": "ok",
      "tiempo_ms": 34.1,
      "error": null
    },
    {
      "servicio": "inventario",
      "estado": "ok",
      "tiempo_ms": 27.6,
      "error": null
    },
    {
      "servicio": "precios",
      "estado": "ok",
      "tiempo_ms": 27.8,
      "error": null
    },
    {
      "servicio": "proveedores",
      "estado": "ok",
      "tiempo_ms": 28.1,
      "error": null
    },
    {
      "servicio": "abastecimiento",
      "estado": "ok",
      "tiempo_ms": 24.6,
      "error": null
    },
    {
      "servicio": "demanda",
      "estado": "ok",
      "tiempo_ms": 23.4,
      "error": null
    },
    {
      "servicio": "cobertura",
      "estado": "ok",
      "tiempo_ms": 25.9,
      "error": null
    },
    {
      "servicio": "capacidad",
      "estado": "ok",
      "tiempo_ms": 29.5,
      "error": null
    },
    {
      "servicio": "rutas",
      "estado": "ok",
      "tiempo_ms": 33.2,
      "error": null
    },
    {
      "servicio": "costos",
      "estado": "ok",
      "tiempo_ms": 33.3,
      "error": null
    },
    {
      "servicio": "punto-equilibrio",
      "estado": "ok",
      "tiempo_ms": 32.0,
      "error": null
    },
    {
      "servicio": "simulacion",
      "estado": "ok",
      "tiempo_ms": 30.0,
      "error": null
    },
    {
      "servicio": "surtido",
      "estado": "ok",
      "tiempo_ms": 31.2,
      "error": null
    },
    {
      "servicio": "notificaciones",
      "estado": "ok",
      "tiempo_ms": 28.5,
      "error": null
    },
    {
      "servicio": "reportes",
      "estado": "ok",
      "tiempo_ms": 25.9,
      "error": null
    },
    {
      "servicio": "sincronizacion",
      "estado": "ok",
      "tiempo_ms": 23.7,
      "error": null
    },
    {
      "servicio": "auditoria-monitoreo",
      "estado": "ok",
      "tiempo_ms": 20.4,
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
    "ms_promedio": "45.8"
  }
]
```

### MNT-02 · Panel de monitoreo · PASA

**Objetivo.** Estado, última verificación, tiempo, versión, dependencias, errores y disponibilidad de cada servicio.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/monitoreo/estado`

```http
Accept: application/json
X-Traza-Id: 88d6cdad-ebde-44cd-8981-2019b1f29312
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 123 ms · traza `88d6cdad-ebde-44cd-8981-2019b1f29312`

```json
{
  "generado_en": "2026-11-26T15:23:53-06:00",
  "resumen": {
    "total": 26,
    "ok": 26,
    "degradados": 0,
    "caidos": 0,
    "sin_datos": 0,
    "alertas_abiertas": 0,
    "monitor_activo": true,
    "intervalo_seg": 30,
    "ultima_ronda": "2026-11-26T15:23:53-06:00"
  },
  "servicios": [
    {
      "servicio": "auth",
      "puerto": 5101,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
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
      "peticiones_hora": 278,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 88.89,
      "bajo_objetivo": true
    },
    {
      "servicio": "usuarios",
      "puerto": 5102,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 28.5,
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
      "disponibilidad_24h_pct": 88.89,
      "bajo_objetivo": true
    },
    {
      "servicio": "productos",
      "puerto": 5103,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 32.4,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 91,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 88.89,
      "bajo_objetivo": true
    },
    {
      "servicio": "pedidos",
      "puerto": 5104,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
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
      "peticiones_hora": 263,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 88.89,
      "bajo_objetivo": true
    },
    {
      "servicio": "entregas",
      "puerto": 5105,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 28.0,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "ok",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 113,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 88.89,
      "bajo_objetivo": true
    },
    {
      "servicio": "planeacion",
      "puerto": 5106,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 32.5,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "ok",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 70,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 88.89,
      "bajo_objetivo": true
    },
    {
      "servicio": "documentos",
      "puerto": 5107,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 28.5,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "ok",
        "bucket": "ok"
      },
      "error": null,
      "peticiones_hora": 47,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 88.89,
      "bajo_objetivo": true
    },
    {
      "servicio": "zonas",
      "puerto": 5108,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 34.3,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 70,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 88.89,
      "bajo_objetivo": true
    },
    {
      "servicio": "microhubs",
      "puerto": 5109,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 26.7,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 74,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 88.89,
      "bajo_objetivo": true
    },
    {
      "servicio": "seguimiento",
      "puerto": 5110,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 34.1,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "ok",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 18,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 88.89,
      "bajo_objetivo": true
    },
    {
      "servicio": "inventario",
      "puerto": 5111,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 27.6,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 125,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 88.89,
      "bajo_objetivo": true
    },
    {
      "servicio": "precios",
      "puerto": 5112,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
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
      "peticiones_hora": 44,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 88.89,
      "bajo_objetivo": true
    },
    {
      "servicio": "proveedores",
      "puerto": 5113,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
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
      "peticiones_hora": 28,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 88.89,
      "bajo_objetivo": true
    },
    {
      "servicio": "abastecimiento",
      "puerto": 5114,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 24.6,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 37,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 88.89,
      "bajo_objetivo": true
    },
    {
      "servicio": "demanda",
      "puerto": 5115,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 23.4,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 135,
      "errores_5xx_hora": 1,
      "disponibilidad_24h_pct": 88.89,
      "bajo_objetivo": true
    },
    {
      "servicio": "cobertura",
      "puerto": 5116,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 25.9,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 119,
      "errores_5xx_hora": 2,
      "disponibilidad_24h_pct": 88.89,
      "bajo_objetivo": true
    },
    {
      "servicio": "capacidad",
      "puerto": 5117,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 29.5,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 76,
      "errores_5xx_hora": 1,
      "disponibilidad_24h_pct": 88.89,
      "bajo_objetivo": true
    },
    {
      "servicio": "rutas",
      "puerto": 5118,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 33.2,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 75,
      "errores_5xx_hora": 2,
      "disponibilidad_24h_pct": 88.89,
      "bajo_objetivo": true
    },
    {
      "servicio": "costos",
      "puerto": 5119,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 33.3,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 142,
      "errores_5xx_hora": 1,
      "disponibilidad_24h_pct": 88.89,
      "bajo_objetivo": true
    },
    {
      "servicio": "punto-equilibrio",
      "puerto": 5120,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 32.0,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 90,
      "errores_5xx_hora": 3,
      "disponibilidad_24h_pct": 88.89,
      "bajo_objetivo": true
    },
    {
      "servicio": "simulacion",
      "puerto": 5121,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 30.0,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 119,
      "errores_5xx_hora": 3,
      "disponibilidad_24h_pct": 88.89,
      "bajo_objetivo": true
    },
    {
      "servicio": "surtido",
      "puerto": 5122,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 31.2,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 61,
      "errores_5xx_hora": 3,
      "disponibilidad_24h_pct": 88.89,
      "bajo_objetivo": true
    },
    {
      "servicio": "notificaciones",
      "puerto": 5124,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 28.5,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 22,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 88.89,
      "bajo_objetivo": true
    },
    {
      "servicio": "reportes",
      "puerto": 5123,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 25.9,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 90,
      "errores_5xx_hora": 2,
      "disponibilidad_24h_pct": 88.89,
      "bajo_objetivo": true
    },
    {
      "servicio": "sincronizacion",
      "puerto": 5125,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 23.7,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 58,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 88.89,
      "bajo_objetivo": true
    },
    {
      "servicio": "auditoria-monitoreo",
      "puerto": 5126,
      "estado": "ok",
      "verificado_en": "2026-11-26T15:23:53-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 20.4,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "ok",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 147,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 88.89,
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
X-Traza-Id: b4e0eb78-c67e-4859-93b2-a61c58680b95
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 135 ms · traza `b4e0eb78-c67e-4859-93b2-a61c58680b95`

```xml
<?xml version='1.0' encoding='utf-8'?>
<monitoreo_estado xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><generado_en>2026-11-26T15:23:53-06:00</generado_en><resumen><total>26</total><ok>26</ok><degradados>0</degradados><caidos>0</caidos><sin_datos>0</sin_datos><alertas_abiertas>0</alertas_abiertas><monitor_activo>true</monitor_activo><intervalo_seg>30</intervalo_seg><ultima_ronda>2026-11-26T15:23:53-06:00</ultima_ronda></resumen><servicios><servicio><servicio>auth</servicio><puerto>5101</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>25.5</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>278</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>usuarios</servicio><puerto>5102</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>28.5</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>100</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>productos</servicio><puerto>5103</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>32.4</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>91</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>pedidos</servicio><puerto>5104</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>25.8</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>263</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>entregas</servicio><puerto>5105</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>28</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>ok</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>113</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>planeacion</servicio><puerto>5106</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>32.5</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>ok</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>70</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>documentos</servicio><puerto>5107</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>28.5</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>ok</mongo><bucket>ok</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>47</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>zonas</servicio><puerto>5108</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>34.3</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>70</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>microhubs</servicio><puerto>5109</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>26.7</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>74</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>seguimiento</servicio><puerto>5110</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>34.1</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>ok</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>18</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>inventario</servicio><puerto>5111</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>27.6</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>125</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>precios</servicio><puerto>5112</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>27.8</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>44</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>proveedores</servicio><puerto>5113</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>28.1</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>28</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>abastecimiento</servicio><puerto>5114</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>24.6</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>37</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>demanda</servicio><puerto>5115</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>23.4</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>135</peticiones_hora><errores_5xx_hora>1</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>cobertura</servicio><puerto>5116</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>25.9</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>119</peticiones_hora><errores_5xx_hora>2</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>capacidad</servicio><puerto>5117</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>29.5</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>76</peticiones_hora><errores_5xx_hora>1</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>rutas</servicio><puerto>5118</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>33.2</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>75</peticiones_hora><errores_5xx_hora>2</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>costos</servicio><puerto>5119</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>33.3</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>142</peticiones_hora><errores_5xx_hora>1</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>punto-equilibrio</servicio><puerto>5120</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>32</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>90</peticiones_hora><errores_5xx_hora>3</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>simulacion</servicio><puerto>5121</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>30</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>119</peticiones_hora><errores_5xx_hora>3</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>surtido</servicio><puerto>5122</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>31.2</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>61</peticiones_hora><errores_5xx_hora>3</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>notificaciones</servicio><puerto>5124</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>28.5</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>22</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>reportes</servicio><puerto>5123</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>25.9</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>90</peticiones_hora><errores_5xx_hora>2</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>sincronizacion</servicio><puerto>5125</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>23.7</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>58</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio><servicio><servicio>auditoria-monitoreo</servicio><puerto>5126</puerto><estado>ok</estado><verificado_en>2026-11-26T15:23:53-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>20.4</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>ok</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>148</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>88.89</disponibilidad_24h_pct><bajo_objetivo>true</bajo_objetivo></servicio></servicios><dependencias_caidas /></monitoreo_estado>
```

### MNT-04 · Historial de un servicio · PASA

**Objetivo.** Serie de verificaciones, la más reciente primero.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/monitoreo/servicios/pedidos/historial?por_pagina=3`

```http
Accept: application/json
X-Traza-Id: 8562909c-6d6a-447a-9db5-b287c6e642ca
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 61 ms · traza `8562909c-6d6a-447a-9db5-b287c6e642ca`

```json
{
  "datos": [
    {
      "verificado_en": "2026-11-26T15:23:53-06:00",
      "estado": "ok",
      "http_status": 200,
      "tiempo_ms": 25.8,
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
      "verificado_en": "2026-11-26T15:23:48-06:00",
      "estado": "ok",
      "http_status": 200,
      "tiempo_ms": 29.1,
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
      "verificado_en": "2026-11-26T15:23:17-06:00",
      "estado": "ok",
      "http_status": 200,
      "tiempo_ms": 42.0,
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
    "total": 9,
    "paginas": 3
  }
}
```

### MNT-05 · Disponibilidad de las últimas 24 horas · PASA

**Objetivo.** Porcentaje disponible, salud plena y percentiles p50 y p95.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/monitoreo/disponibilidad?horas=24`

```http
Accept: application/json
X-Traza-Id: 65f09309-0106-41e0-b2a5-e10dbd4c7d48
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 56 ms · traza `65f09309-0106-41e0-b2a5-e10dbd4c7d48`

```json
{
  "horas": 24,
  "objetivo_pct": 99.0,
  "servicios": [
    {
      "servicio": "auth",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 32.1,
      "tiempo_p95_ms": 363.3,
      "tiempo_max_ms": 545.9,
      "bajo_objetivo": true
    },
    {
      "servicio": "usuarios",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 39.5,
      "tiempo_p95_ms": 129.0,
      "tiempo_max_ms": 161.2,
      "bajo_objetivo": true
    },
    {
      "servicio": "productos",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 32.4,
      "tiempo_p95_ms": 135.6,
      "tiempo_max_ms": 184.3,
      "bajo_objetivo": true
    },
    {
      "servicio": "pedidos",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 31.5,
      "tiempo_p95_ms": 116.7,
      "tiempo_max_ms": 151.7,
      "bajo_objetivo": true
    },
    {
      "servicio": "entregas",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 31.1,
      "tiempo_p95_ms": 140.5,
      "tiempo_max_ms": 150.9,
      "bajo_objetivo": true
    },
    {
      "servicio": "planeacion",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 37.4,
      "tiempo_p95_ms": 384.3,
      "tiempo_max_ms": 594.4,
      "bajo_objetivo": true
    },
    {
      "servicio": "documentos",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 36.2,
      "tiempo_p95_ms": 131.9,
      "tiempo_max_ms": 177.1,
      "bajo_objetivo": true
    },
    {
      "servicio": "zonas",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 34.3,
      "tiempo_p95_ms": 189.3,
      "tiempo_max_ms": 239.3,
      "bajo_objetivo": true
    },
    {
      "servicio": "microhubs",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 36.1,
      "tiempo_p95_ms": 98.1,
      "tiempo_max_ms": 127.8,
      "bajo_objetivo": true
    },
    {
      "servicio": "seguimiento",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 50.0,
      "tiempo_p95_ms": 284.9,
      "tiempo_max_ms": 432.6,
      "bajo_objetivo": true
    },
    {
      "servicio": "inventario",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 33.2,
      "tiempo_p95_ms": 102.7,
      "tiempo_max_ms": 135.0,
      "bajo_objetivo": true
    },
    {
      "servicio": "precios",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 34.2,
      "tiempo_p95_ms": 80.5,
      "tiempo_max_ms": 81.1,
      "bajo_objetivo": true
    },
    {
      "servicio": "proveedores",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 32.5,
      "tiempo_p95_ms": 84.3,
      "tiempo_max_ms": 99.7,
      "bajo_objetivo": true
    },
    {
      "servicio": "abastecimiento",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 32.0,
      "tiempo_p95_ms": 87.7,
      "tiempo_max_ms": 101.4,
      "bajo_objetivo": true
    },
    {
      "servicio": "demanda",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 30.4,
      "tiempo_p95_ms": 254.9,
      "tiempo_max_ms": 377.5,
      "bajo_objetivo": true
    },
    {
      "servicio": "cobertura",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 36.1,
      "tiempo_p95_ms": 84.8,
      "tiempo_max_ms": 90.4,
      "bajo_objetivo": true
    },
    {
      "servicio": "capacidad",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 29.4,
      "tiempo_p95_ms": 75.1,
      "tiempo_max_ms": 79.1,
      "bajo_objetivo": true
    },
    {
      "servicio": "rutas",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 39.8,
      "tiempo_p95_ms": 70.8,
      "tiempo_max_ms": 71.8,
      "bajo_objetivo": true
    },
    {
      "servicio": "costos",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 37.8,
      "tiempo_p95_ms": 88.6,
      "tiempo_max_ms": 95.1,
      "bajo_objetivo": true
    },
    {
      "servicio": "punto-equilibrio",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 33.4,
      "tiempo_p95_ms": 60.2,
      "tiempo_max_ms": 62.0,
      "bajo_objetivo": true
    },
    {
      "servicio": "simulacion",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 33.7,
      "tiempo_p95_ms": 74.5,
      "tiempo_max_ms": 86.6,
      "bajo_objetivo": true
    },
    {
      "servicio": "surtido",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 32.8,
      "tiempo_p95_ms": 64.8,
      "tiempo_max_ms": 71.0,
      "bajo_objetivo": true
    },
    {
      "servicio": "notificaciones",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 30.1,
      "tiempo_p95_ms": 96.0,
      "tiempo_max_ms": 133.2,
      "bajo_objetivo": true
    },
    {
      "servicio": "reportes",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 25.9,
      "tiempo_p95_ms": 75.4,
      "tiempo_max_ms": 101.6,
      "bajo_objetivo": true
    },
    {
      "servicio": "sincronizacion",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 31.9,
      "tiempo_p95_ms": 59.4,
      "tiempo_max_ms": 66.5,
      "bajo_objetivo": true
    },
    {
      "servicio": "auditoria-monitoreo",
      "verificaciones": 9,
      "caidas": 1,
      "disponibilidad_pct": 88.89,
      "salud_plena_pct": 88.89,
      "tiempo_p50_ms": 28.5,
      "tiempo_p95_ms": 60.8,
      "tiempo_max_ms": 72.6,
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
X-Traza-Id: 6f2f27a7-1005-4786-b6f7-1c1caa8409fa
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 36 ms · traza `6f2f27a7-1005-4786-b6f7-1c1caa8409fa`

```json
{
  "minutos": 60,
  "peticiones_total": 2496,
  "servicios": [
    {
      "servicio": "auth",
      "peticiones": 278,
      "errores_5xx": 0,
      "errores_4xx": 14,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 278,
      "duracion_p95_ms": 419,
      "duracion_p99_ms": 566
    },
    {
      "servicio": "usuarios",
      "peticiones": 100,
      "errores_5xx": 0,
      "errores_4xx": 65,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 24,
      "duracion_p95_ms": 155,
      "duracion_p99_ms": 175
    },
    {
      "servicio": "productos",
      "peticiones": 91,
      "errores_5xx": 0,
      "errores_4xx": 50,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 22,
      "duracion_p95_ms": 72,
      "duracion_p99_ms": 126
    },
    {
      "servicio": "pedidos",
      "peticiones": 263,
      "errores_5xx": 0,
      "errores_4xx": 53,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 79,
      "duracion_p95_ms": 203,
      "duracion_p99_ms": 321
    },
    {
      "servicio": "entregas",
      "peticiones": 113,
      "errores_5xx": 0,
      "errores_4xx": 27,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 58,
      "duracion_p95_ms": 135,
      "duracion_p99_ms": 171
    },
    {
      "servicio": "planeacion",
      "peticiones": 70,
      "errores_5xx": 0,
      "errores_4xx": 14,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 47,
      "duracion_p95_ms": 274,
      "duracion_p99_ms": 369
    },
    {
      "servicio": "documentos",
      "peticiones": 47,
      "errores_5xx": 0,
      "errores_4xx": 5,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 49,
      "duracion_p95_ms": 84,
      "duracion_p99_ms": 107
    },
    {
      "servicio": "zonas",
      "peticiones": 70,
      "errores_5xx": 0,
      "errores_4xx": 40,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 22,
      "duracion_p95_ms": 66,
      "duracion_p99_ms": 76
    },
    {
      "servicio": "microhubs",
      "peticiones": 74,
      "errores_5xx": 0,
      "errores_4xx": 35,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 28,
      "duracion_p95_ms": 80,
      "duracion_p99_ms": 236
    },
    {
      "servicio": "seguimiento",
      "peticiones": 18,
      "errores_5xx": 0,
      "errores_4xx": 2,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 28,
      "duracion_p95_ms": 73,
      "duracion_p99_ms": 73
    },
    {
      "servicio": "inventario",
      "peticiones": 125,
      "errores_5xx": 0,
      "errores_4xx": 11,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 64,
      "duracion_p95_ms": 115,
      "duracion_p99_ms": 205
    },
    {
      "servicio": "precios",
      "peticiones": 44,
      "errores_5xx": 0,
      "errores_4xx": 8,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 47,
      "duracion_p95_ms": 99,
      "duracion_p99_ms": 178
    },
    {
      "servicio": "proveedores",
      "peticiones": 28,
      "errores_5xx": 0,
      "errores_4xx": 7,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 57,
      "duracion_p95_ms": 128,
      "duracion_p99_ms": 132
    },
    {
      "servicio": "abastecimiento",
      "peticiones": 37,
      "errores_5xx": 0,
      "errores_4xx": 15,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 92,
      "duracion_p95_ms": 479,
      "duracion_p99_ms": 497
    },
    {
      "servicio": "demanda",
      "peticiones": 135,
      "errores_5xx": 1,
      "errores_4xx": 19,
      "tasa_5xx_pct": 0.74,
      "duracion_p50_ms": 104,
      "duracion_p95_ms": 175,
      "duracion_p99_ms": 345
    },
    {
      "servicio": "cobertura",
      "peticiones": 119,
      "errores_5xx": 2,
      "errores_4xx": 20,
      "tasa_5xx_pct": 1.68,
      "duracion_p50_ms": 45,
      "duracion_p95_ms": 120,
      "duracion_p99_ms": 181
    },
    {
      "servicio": "capacidad",
      "peticiones": 76,
      "errores_5xx": 1,
      "errores_4xx": 21,
      "tasa_5xx_pct": 1.32,
      "duracion_p50_ms": 47,
      "duracion_p95_ms": 141,
      "duracion_p99_ms": 202
    },
    {
      "servicio": "rutas",
      "peticiones": 75,
      "errores_5xx": 2,
      "errores_4xx": 30,
      "tasa_5xx_pct": 2.67,
      "duracion_p50_ms": 96,
      "duracion_p95_ms": 268,
      "duracion_p99_ms": 373
    },
    {
      "servicio": "costos",
      "peticiones": 142,
      "errores_5xx": 1,
      "errores_4xx": 25,
      "tasa_5xx_pct": 0.7,
      "duracion_p50_ms": 47,
      "duracion_p95_ms": 77,
      "duracion_p99_ms": 95
    },
    {
      "servicio": "punto-equilibrio",
      "peticiones": 90,
      "errores_5xx": 3,
      "errores_4xx": 13,
      "tasa_5xx_pct": 3.33,
      "duracion_p50_ms": 173,
      "duracion_p95_ms": 359,
      "duracion_p99_ms": 542
    },
    {
      "servicio": "simulacion",
      "peticiones": 119,
      "errores_5xx": 3,
      "errores_4xx": 31,
      "tasa_5xx_pct": 2.52,
      "duracion_p50_ms": 28,
      "duracion_p95_ms": 612,
      "duracion_p99_ms": 693
    },
    {
      "servicio": "surtido",
      "peticiones": 61,
      "errores_5xx": 3,
      "errores_4xx": 20,
      "tasa_5xx_pct": 4.92,
      "duracion_p50_ms": 41,
      "duracion_p95_ms": 483,
      "duracion_p99_ms": 1295
    },
    {
      "servicio": "notificaciones",
      "peticiones": 22,
      "errores_5xx": 0,
      "errores_4xx": 6,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 29,
      "duracion_p95_ms": 66,
      "duracion_p99_ms": 68
    },
    {
      "servicio": "reportes",
      "peticiones": 90,
      "errores_5xx": 2,
      "errores_4xx": 31,
      "tasa_5xx_pct": 2.22,
      "duracion_p50_ms": 83,
      "duracion_p95_ms": 608,
      "duracion_p99_ms": 976
    },
    {
      "servicio": "sincronizacion",
      "peticiones": 58,
      "errores_5xx": 0,
      "errores_4xx": 22,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 55,
      "duracion_p95_ms": 403,
      "duracion_p99_ms": 450
    },
    {
      "servicio": "auditoria-monitoreo",
      "peticiones": 151,
      "errores_5xx": 0,
      "errores_4xx": 59,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 46,
      "duracion_p95_ms": 129,
      "duracion_p99_ms": 290
    }
  ]
}
```

### MNT-07 · Umbrales y su justificación · PASA

**Objetivo.** Cada umbral con su origen y cómo se calibra.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/monitoreo/supuestos`

```http
Accept: application/json
X-Traza-Id: c515f1f9-e26b-4952-b75a-9cddde2fbdd6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 53 ms · traza `c515f1f9-e26b-4952-b75a-9cddde2fbdd6`

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
X-Traza-Id: c5334260-f1ef-4e17-a358-b9435c44c9a2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 74 ms · traza `c5334260-f1ef-4e17-a358-b9435c44c9a2`

```json
{
  "datos": [
    {
      "id": 261,
      "servicio": "zonas",
      "tipo": "latencia_alta",
      "severidad": "media",
      "detalle": "/salud de zonas tardó 21 ms (umbral 0 ms).",
      "abierta_en": "2026-11-26T15:23:53-06:00",
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
    "detalle": "/salud de zonas tardó 21 ms (umbral 0 ms)."
  }
]
```

### MNT-09 · Reconocer una alerta · PASA

**Objetivo.** Queda quién se hizo cargo y cuándo.

**Petición.** `POST http://auditoria-monitoreo:5126/api/v1/monitoreo/alertas/261/reconocer`

```http
Accept: application/json
X-Traza-Id: 59930635-55e5-43b0-84c2-797ed5f869b7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 137 ms · traza `59930635-55e5-43b0-84c2-797ed5f869b7`

```json
{
  "id": 261,
  "servicio": "zonas",
  "tipo": "latencia_alta",
  "severidad": "media",
  "detalle": "/salud de zonas tardó 21 ms (umbral 0 ms).",
  "abierta_en": "2026-11-26T15:23:53-06:00",
  "cerrada_en": null,
  "duracion_seg": 0,
  "reconocida": {
    "por": {
      "id": 1,
      "nombre": "Mauro Castillo Peña"
    },
    "en": "2026-11-26T15:23:54-06:00"
  }
}
```

**Evidencia en PostgreSQL.** `SELECT fecha, accion, detalle, usuario_id FROM auditoria WHERE entidad = 'monitoreo_alerta' AND entidad_id = %s ORDER BY id`

```json
[
  {
    "fecha": "2026-11-26 15:23:53.993016-06:00",
    "accion": "alta",
    "detalle": null,
    "usuario_id": 1
  },
  {
    "fecha": "2026-11-26 15:23:54.161644-06:00",
    "accion": "modificacion",
    "detalle": null,
    "usuario_id": 1
  }
]
```

### MNT-10 · Reconocer sin permiso · PASA

**Objetivo.** El auditor ve el monitoreo pero no lo opera.

**Petición.** `POST http://auditoria-monitoreo:5126/api/v1/monitoreo/alertas/261/reconocer`

```http
Accept: application/json
X-Traza-Id: 2d691613-f68f-404d-bd5b-0a7ff829194c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 403 (esperado 403) · 58 ms · traza `2d691613-f68f-404d-bd5b-0a7ff829194c`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "2d691613-f68f-404d-bd5b-0a7ff829194c"
  }
}
```

### MNT-11 · El operador no ve el monitoreo · PASA

**Objetivo.** Sin monitoreo.ver.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/monitoreo/estado`

```http
Accept: application/json
X-Traza-Id: 804f1a46-7847-484c-98e2-8abb9edb6e49
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 44 ms · traza `804f1a46-7847-484c-98e2-8abb9edb6e49`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "804f1a46-7847-484c-98e2-8abb9edb6e49"
  }
}
```

### AUD-01 · Bitácora con filtros · PASA

**Objetivo.** Quién cambió qué, cuándo y desde dónde.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria?modulo=pedidos&por_pagina=3`

```http
Accept: application/json
X-Traza-Id: ea80c80c-783a-4d24-9105-4cbe18be1b86
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 133 ms · traza `ea80c80c-783a-4d24-9105-4cbe18be1b86`

```json
{
  "datos": [
    {
      "id": 18715,
      "fecha": "2026-11-26T15:23:37-06:00",
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
        "id": "596"
      },
      "exitoso": true,
      "detalle": null,
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-26T15:23:34.042587-06:00",
          "nuevo": "2026-11-26T15:23:37.516175-06:00"
        },
        {
          "campo": "cerrado_en",
          "anterior": null,
          "nuevo": "2026-11-26T15:23:37.516175-06:00"
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
      "id": 18712,
      "fecha": "2026-11-26T15:23:37-06:00",
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
        "id": "595"
      },
      "exitoso": true,
      "detalle": null,
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-26T15:23:34.042587-06:00",
          "nuevo": "2026-11-26T15:23:37.516175-06:00"
        },
        {
          "campo": "cerrado_en",
          "anterior": null,
          "nuevo": "2026-11-26T15:23:37.516175-06:00"
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
      "id": 18709,
      "fecha": "2026-11-26T15:23:37-06:00",
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
        "id": "594"
      },
      "exitoso": true,
      "detalle": null,
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-26T15:23:34.042587-06:00",
          "nuevo": "2026-11-26T15:23:37.516175-06:00"
        },
        {
          "campo": "cerrado_en",
          "anterior": null,
          "nuevo": "2026-11-26T15:23:37.516175-06:00"
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
    "total": 4854,
    "paginas": 1618
  }
}
```

**Explicación.** La bitácora es de solo escritura (RN31); los valores de contraseñas nunca aparecen.

### AUD-02 · Accesos al sistema · PASA

**Objetivo.** Inicios, fallos, bloqueos y accesos denegados del periodo.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/accesos`

```http
Accept: application/json
X-Traza-Id: e1a6ec36-069b-4cd9-9f46-1ec202906e50
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 343 ms · traza `e1a6ec36-069b-4cd9-9f46-1ec202906e50`

```json
{
  "desde": "2026-11-19",
  "hasta": "2026-11-26",
  "totales": {
    "login_exitoso": 1023,
    "login_fallido": 36,
    "logout": 17,
    "bloqueo_cuenta": 1,
    "desbloqueo": 0,
    "acceso_denegado": 1116
  },
  "correos_con_mas_fallos": [
    {
      "correo": "repartidor1@codex.mx",
      "intentos": 7,
      "ultimo_intento": "2026-11-26T15:15:01-06:00"
    },
    {
      "correo": "planeador@codex.mx",
      "intentos": 7,
      "ultimo_intento": "2026-11-26T15:14:58-06:00"
    },
    {
      "correo": "auditor@codex.mx",
      "intentos": 4,
      "ultimo_intento": "2026-11-26T15:22:46-06:00"
    },
    {
      "correo": "no.existe.ola3@codex.mx",
      "intentos": 4,
      "ultimo_intento": "2026-11-25T15:46:41-06:00"
    },
    {
      "correo": "prueba.1113b59f@ejemplo.mx",
      "intentos": 1,
      "ultimo_intento": "2026-11-26T15:17:18-06:00"
    }
  ],
  "denegados_frecuentes": [
    {
      "detalle": "GET /api/v1/auditoria sin auditoria.ver",
      "veces": 59
    },
    {
      "detalle": "GET /api/v1/auditoria/accesos sin auditoria.ver",
      "veces": 56
    },
    {
      "detalle": "GET /api/v1/auditoria/trazabilidad/inventario sin auditoria.ver",
      "veces": 56
    },
    {
      "detalle": "GET /api/v1/auditoria/trazabilidad/pedido/1 sin auditoria.ver",
      "veces": 56
    },
    {
      "detalle": "GET /api/v1/monitoreo/estado sin monitoreo.ver",
      "veces": 52
    }
  ]
}
```

### AUD-03 · Línea de tiempo de un pedido · PASA

**Objetivo.** Une bitácora, cambios de estado, inventario y archivos del pedido.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/pedido/1`

```http
Accept: application/json
X-Traza-Id: d10d07c5-cbf2-4425-8cc8-1f5c9a34a405
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 209 ms · traza `d10d07c5-cbf2-4425-8cc8-1f5c9a34a405`

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
X-Traza-Id: 570fac9a-fd30-43e9-ac7c-e745c188397d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 91 ms · traza `570fac9a-fd30-43e9-ac7c-e745c188397d`

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
X-Traza-Id: d9d376b3-8538-4222-a490-639aa2c11c45
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 96 ms · traza `d9d376b3-8538-4222-a490-639aa2c11c45`

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
X-Traza-Id: 76932d89-78dc-4438-88d8-3257a7bac2a0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 44 ms · traza `76932d89-78dc-4438-88d8-3257a7bac2a0`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "76932d89-78dc-4438-88d8-3257a7bac2a0"
  }
}
```

**Evidencia en PostgreSQL.** `SELECT fecha, accion, detalle, exitoso FROM auditoria WHERE accion = 'acceso_denegado' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "fecha": "2026-11-26 15:23:55.824797-06:00",
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
X-Traza-Id: b1408eb5-4a7d-490a-b036-377e8c944ef8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 75 ms · traza `b1408eb5-4a7d-490a-b036-377e8c944ef8`

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
X-Traza-Id: 6f79c89a-4c5a-4961-bdd8-997381de1f23
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 794 ms · traza `6f79c89a-4c5a-4961-bdd8-997381de1f23`

```json
{
  "desde": "2026-08-28",
  "hasta": "2026-11-26",
  "indicadores": [
    {
      "clave": "********",
      "titulo": "Pedidos del periodo",
      "valor": 366,
      "unidad": "pedidos",
      "fuente": "pedidos"
    },
    {
      "clave": "********",
      "titulo": "Venta del periodo",
      "valor": 55933.2,
      "unidad": "MXN",
      "fuente": "pedidos"
    },
    {
      "clave": "********",
      "titulo": "Ticket promedio",
      "valor": 152.82,
      "unidad": "MXN",
      "fuente": "pedidos"
    },
    {
      "clave": "********",
      "titulo": "Demanda no atendida",
      "valor": 53,
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
X-Traza-Id: f171b8b1-ba76-4670-a8b9-0d68f3029ed7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 648 ms · traza `f171b8b1-ba76-4670-a8b9-0d68f3029ed7`

```json
{
  "reporte": "comparacion_microhubs",
  "familia": "comercial",
  "titulo": "Comparación entre microhubs",
  "generado_en": "2026-11-26T15:23:57-06:00",
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
        "141",
        "702",
        "22862.40",
        "162.14",
        "48.42"
      ]
    },
    {
      "celdas": [
        "Microhub San Bernabé Centro",
        "90",
        "436",
        "12771.40",
        "141.90",
        "27.05"
      ]
    },
    {
      "celdas": [
        "Microhub Poniente F-113",
        "71",
        "363",
        "10910.00",
        "153.66",
        "23.11"
      ]
    },
    {
      "celdas": [
        "Microhub C81FE",
        "1",
        "6",
        "336.00",
        "336.00",
        "0.71"
      ]
    },
    {
      "celdas": [
        "Microhub E0FDE",
        "1",
        "6",
        "336.00",
        "336.00",
        "0.71"
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
      "304",
      "1513",
      "47215.80",
      "155.32",
      "100.00"
    ]
  },
  "total_filas": 6
}
```

**Evidencia en PostgreSQL.** `SELECT m.nombre, count(*) AS pedidos, round(sum(p.subtotal), 2) AS venta FROM pedido p JOIN microhub m ON m.id = p.microhub_id WHERE p.estado <> 'cancelado' AND p.creado_en > now() - interval '90 days' GROUP BY m.nombre ORDER BY venta DESC`

```json
[
  {
    "nombre": "Microhub Valles",
    "pedidos": 141,
    "venta": "22862.40"
  },
  {
    "nombre": "Microhub San Bernabé Centro",
    "pedidos": 90,
    "venta": "12771.40"
  },
  {
    "nombre": "Microhub Poniente F-113",
    "pedidos": 71,
    "venta": "10910.00"
  },
  {
    "nombre": "Microhub E0FDE",
    "pedidos": 1,
    "venta": "336.00"
  },
  {
    "nombre": "Microhub C81FE",
    "pedidos": 1,
    "venta": "336.00"
  }
]
```

### REP-04 · Reporte en XML · PASA

**Objetivo.** El reporte financiero validado contra reportes.xsd.

**Petición.** `GET http://reportes:5123/api/v1/reportes/equilibrio_microhubs`

```http
Accept: application/xml
X-Traza-Id: d055f226-01b4-4710-98f9-de91b5c0d736
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 395 ms · traza `d055f226-01b4-4710-98f9-de91b5c0d736`

```xml
<?xml version='1.0' encoding='utf-8'?>
<reporte xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><reporte>equilibrio_microhubs</reporte><familia>financiero</familia><titulo>Punto de equilibrio por microhub</titulo><generado_en>2026-11-26T15:23:57-06:00</generado_en><filtros><desde>2026-10-28</desde><hasta>2026-11-26</hasta><zona_id xsi:nil="true" /><microhub_id xsi:nil="true" /></filtros><columnas><columna><clave>microhub</clave><titulo>Microhub</titulo><tipo>texto</tipo></columna><columna><clave>costos_fijos_mes</clave><titulo>Costos fijos del mes</titulo><tipo>dinero</tipo></columna><columna><clave>margen_pedido</clave><titulo>Margen por pedido</titulo><tipo>dinero</tipo></columna><columna><clave>equilibrio_diario</clave><titulo>Equilibrio (pedidos/día)</titulo><tipo>dinero</tipo></columna><columna><clave>pedidos_dia</clave><titulo>Pedidos/día esperados</titulo><tipo>dinero</tipo></columna><columna><clave>diferencia_pedidos_dia</clave><titulo>Diferencia (pedidos/día)</titulo><tipo>dinero</tipo></columna><columna><clave>utilidad_mes</clave><titulo>Utilidad del mes</titulo><tipo>dinero</tipo></columna><columna><clave>decision</clave><titulo>Decisión</titulo><tipo>texto</tipo></columna></columnas><filas><fila><celdas><celda>Microhub San Bernabé Centro</celda><celda>69500.00</celda><celda>5.14</celda><celda>450.50</celda><celda>23.60</celda><celda>-426.91</celda><celda>-65859.95</celda><celda>no_viable</celda></celdas></fila><fila><celdas><celda>Microhub Valles</celda><celda>66500.00</celda><celda>5.14</celda><celda>431.06</celda><celda>16.11</celda><celda>-414.95</celda><celda>-64014.68</celda><celda>no_viable</celda></celdas></fila><fila><celdas><celda>Microhub Poniente F-113</celda><celda>50000.00</celda><celda>5.14</celda><celda>324.10</celda><celda>9.79</celda><celda>-314.31</celda><celda>-48488.91</celda><celda>no_viable</celda></celdas></fila></filas><totales><celdas><celda>Total</celda><celda>186000.00</celda><celda /><celda /><celda /><celda /><celda>-178363.54</celda><celda /></celdas></totales><total_filas>3</total_filas></reporte>
```

### REP-05 · Datos para Highcharts · PASA

**Objetivo.** Categorías y series listas para graficar.

**Petición.** `GET http://reportes:5123/api/v1/reportes/pedidos_por_zona/grafica?desde=2026-08-28`

```http
Accept: application/json
X-Traza-Id: 33f04e58-a88d-4e75-b851-3d7e910b502a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 245 ms · traza `33f04e58-a88d-4e75-b851-3d7e910b502a`

```json
{
  "reporte": "pedidos_por_zona",
  "titulo": "Pedidos por zona",
  "tipo": "column",
  "unidad": "pedidos",
  "categorias": [
    "Valles de San Bernabé",
    "Paseo de San Bernabé",
    "San Bernabé X (F-113)",
    "San Bernabé Centro"
  ],
  "series": [
    {
      "nombre": "Pedidos",
      "datos": [
        134.0,
        82.0,
        75.0,
        75.0
      ]
    },
    {
      "nombre": "Demanda no atendida",
      "datos": [
        13.0,
        16.0,
        12.0,
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
X-Traza-Id: 6f3d8701-26c9-45e6-b57a-8803f0fd2806
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 274 ms · traza `6f3d8701-26c9-45e6-b57a-8803f0fd2806`

```json
﻿Zona,Pedidos,Unidades,Venta,Ticket promedio,Demanda no atendida,No atendida (%)
Valles de San Bernabé,134,625,19315.40,144.14,13,8.84
Paseo de San Bernabé,82,430,14789.90,180.36,16,16.33
San Bernabé X (F-113),75,380,11398.00,151.97,12,13.79
San Bernabé Centro,75,374,10429.90,139.07,12,13.79
Total,366,1809,55933.20,152.82,53,12.65

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
    "sha256": "ecba2b210686054b",
    "creado_por": 1
  }
]
```

### REP-07 · Bitácora de exportaciones · PASA

**Objetivo.** Quién exportó qué, con qué filtros.

**Petición.** `GET http://reportes:5123/api/v1/reportes/exportaciones?por_pagina=3`

```http
Accept: application/json
X-Traza-Id: 9bd93e79-220f-43bf-b9a7-c7e0328e1d5d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 89 ms · traza `9bd93e79-220f-43bf-b9a7-c7e0328e1d5d`

```json
{
  "datos": [
    {
      "id": 79,
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
      "sha256": "ecba2b210686054b3c74a633aff2f005ed2f4c359ab37040f933f9b9325de89a",
      "creado_por": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "creado_en": "2026-11-26T15:23:58-06:00"
    },
    {
      "id": 78,
      "reporte": "pedidos_por_dia",
      "formato": "csv",
      "filtros": {
        "desde": "2026-10-28",
        "hasta": "2026-11-26",
        "zona_id": null,
        "microhub_id": null
      },
      "filas": 2,
      "bytes": 176,
      "sha256": "69fd3140dcb85ebb6a234f3cce20838a0abf67adf075431a48d2a1b67f3ed2f1",
      "creado_por": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "creado_en": "2026-11-26T15:22:08-06:00"
    },
    {
      "id": 77,
      "reporte": "inventario_alertas",
      "formato": "csv",
      "filtros": {
        "desde": "2026-10-28",
        "hasta": "2026-11-26",
        "zona_id": null,
        "microhub_id": 1
      },
      "filas": 1,
      "bytes": 150,
      "sha256": "28899f8da0dcf3a043e7ee078df31c5fffb2a896d21a9f94e65220f7a3efe777",
      "creado_por": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "creado_en": "2026-11-26T15:22:05-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 3,
    "total": 79,
    "paginas": 27
  }
}
```

### REP-08 · Filtro que el reporte no admite · PASA

**Objetivo.** Se rechaza en lugar de ignorarse.

**Petición.** `GET http://reportes:5123/api/v1/reportes/carga_repartidores?zona_id=1`

```http
Accept: application/json
X-Traza-Id: 1737c8ad-c3d8-46cd-a542-b3152fd5948e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 7 ms · traza `1737c8ad-c3d8-46cd-a542-b3152fd5948e`

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
    "traza_id": "1737c8ad-c3d8-46cd-a542-b3152fd5948e"
  }
}
```

### REP-09 · El cliente no ve reportes · PASA

**Objetivo.** Sin reportes.ver.

**Petición.** `GET http://reportes:5123/api/v1/reportes`

```http
Accept: application/json
X-Traza-Id: 6837310a-cf66-47f9-814a-881cc3156262
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 27 ms · traza `6837310a-cf66-47f9-814a-881cc3156262`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "6837310a-cf66-47f9-814a-881cc3156262"
  }
}
```

## Servicio sincronizacion · puerto 5125

### SYN-01 · Enviar lo hecho sin conexión · PASA

**Objetivo.** La app manda el cierre y el recorrido; se aplican en el orden en que ocurrieron.

**Petición.** `POST http://sincronizacion:5125/api/v1/sincronizacion/lotes`

```http
Accept: application/json
X-Traza-Id: 1423a1f5-fc62-4bd6-9190-5824635d59ab
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "c644f0a2-8db1-4238-9bf9-a24aef094751",
  "dispositivo": "android-evidencia-0e84f5",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "95fbfc93-ef04-4388-b460-77f7f2ab54da",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-26T21:20:58.715826+00:00",
      "datos": {
        "entrega_id": 304,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "Cliente ausente",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b08a36e5ea8dba9ecdb0b0a"
        ],
        "capturado_en": "2026-11-26T21:20:58.715793+00:00"
      }
    },
    {
      "operacion_uuid": "a801713b-ec37-4f20-9293-a12b7071047f",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-26T21:11:58.715837+00:00",
      "datos": {
        "entrega_id": 304,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-26T21:11:58.715841+00:00"
          }
        ]
      }
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 403 ms · traza `1423a1f5-fc62-4bd6-9190-5824635d59ab`

```json
{
  "id": 176,
  "lote_uuid": "c644f0a2-8db1-4238-9bf9-a24aef094751",
  "dispositivo": "android-evidencia-0e84f5",
  "recibido_en": "2026-11-26T15:23:58-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 0,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "95fbfc93-ef04-4388-b460-77f7f2ab54da",
      "tipo": "entrega_resultado",
      "estado": "aplicada",
      "duplicada": false,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "a801713b-ec37-4f20-9293-a12b7071047f",
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
    "id": 304,
    "resultado": "fallida",
    "id_cliente_local": "95fbfc93-ef04-4388-b460-77f7f2ab54da",
    "estado": "entrega_fallida"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT operacion_uuid, tipo, estado, intentos FROM sync_operacion WHERE dispositivo = %s ORDER BY creada_en`

```json
[
  {
    "operacion_uuid": "a801713b-ec37-4f20-9293-a12b7071047f",
    "tipo": "ubicaciones",
    "estado": "aplicada",
    "intentos": 1
  },
  {
    "operacion_uuid": "95fbfc93-ef04-4388-b460-77f7f2ab54da",
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
X-Traza-Id: e8a94912-11b7-4fce-870a-bcf1484a55c4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "c644f0a2-8db1-4238-9bf9-a24aef094751",
  "dispositivo": "android-evidencia-0e84f5",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "95fbfc93-ef04-4388-b460-77f7f2ab54da",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-26T21:20:58.715826+00:00",
      "datos": {
        "entrega_id": 304,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "Cliente ausente",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b08a36e5ea8dba9ecdb0b0a"
        ],
        "capturado_en": "2026-11-26T21:20:58.715793+00:00"
      }
    },
    {
      "operacion_uuid": "a801713b-ec37-4f20-9293-a12b7071047f",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-26T21:11:58.715837+00:00",
      "datos": {
        "entrega_id": 304,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-26T21:11:58.715841+00:00"
          }
        ]
      }
    }
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 181 ms · traza `e8a94912-11b7-4fce-870a-bcf1484a55c4`

```json
{
  "id": 176,
  "lote_uuid": "c644f0a2-8db1-4238-9bf9-a24aef094751",
  "dispositivo": "android-evidencia-0e84f5",
  "recibido_en": "2026-11-26T15:23:58-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 2,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "95fbfc93-ef04-4388-b460-77f7f2ab54da",
      "tipo": "entrega_resultado",
      "estado": "aplicada",
      "duplicada": true,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "a801713b-ec37-4f20-9293-a12b7071047f",
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
X-Traza-Id: 62dfafd3-2a6c-44f2-8b4e-6587ef608507
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "fc5d1b54-c087-46da-b283-0fbe0365df0e",
  "dispositivo": "android-evidencia-0e84f5",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "fefcfadb-c7bf-446f-9128-f0e99119b23c",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-26T21:22:59.346914+00:00",
      "datos": {
        "entrega_id": 304,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "Cliente ausente",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b08a36e5ea8dba9ecdb0b0a"
        ],
        "capturado_en": "2026-11-26T21:20:58.715793+00:00"
      }
    }
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 282 ms · traza `62dfafd3-2a6c-44f2-8b4e-6587ef608507`

```json
{
  "id": 177,
  "lote_uuid": "fc5d1b54-c087-46da-b283-0fbe0365df0e",
  "dispositivo": "android-evidencia-0e84f5",
  "recibido_en": "2026-11-26T15:23:59-06:00",
  "total": 1,
  "aplicadas": 0,
  "duplicadas": 0,
  "conflictos": 1,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "fefcfadb-c7bf-446f-9128-f0e99119b23c",
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
X-Traza-Id: 018a77ee-f1f2-4d14-bd27-9c3716ac08d8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 66 ms · traza `018a77ee-f1f2-4d14-bd27-9c3716ac08d8`

```json
{
  "datos": [
    {
      "id": 193,
      "lote_uuid": "fc5d1b54-c087-46da-b283-0fbe0365df0e",
      "dispositivo": "android-evidencia-0e84f5",
      "operacion_uuid": "fefcfadb-c7bf-446f-9128-f0e99119b23c",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-26T15:22:59-06:00",
      "estado": "conflicto",
      "http_status": 409,
      "codigo": "CONFLICTO",
      "mensaje": "La entrega ya se cerró con otra operación.",
      "intentos": 1,
      "procesada_en": "2026-11-26T15:23:59-06:00",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      }
    },
    {
      "id": 174,
      "lote_uuid": "ba2fd331-5191-4d37-ac5d-70f11aed030d",
      "dispositivo": "android-prueba-ola3",
      "operacion_uuid": "bdb73429-96c2-4ab9-af41-4424a5a12693",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-26T14:21:53-06:00",
      "estado": "conflicto",
      "http_status": 409,
      "codigo": "CONFLICTO",
      "mensaje": "La entrega ya se cerró con otra operación.",
      "intentos": 1,
      "procesada_en": "2026-11-26T14:26:53-06:00",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      }
    },
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
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 3,
    "total": 13,
    "paginas": 5
  }
}
```

### SYN-05 · Mis lotes · PASA

**Objetivo.** El repartidor ve solo los suyos.

**Petición.** `GET http://sincronizacion:5125/api/v1/sincronizacion/lotes?por_pagina=3`

```http
Accept: application/json
X-Traza-Id: 103edb36-b073-4881-aaa1-ebfe718374fb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 54 ms · traza `103edb36-b073-4881-aaa1-ebfe718374fb`

```json
{
  "datos": [
    {
      "id": 177,
      "lote_uuid": "fc5d1b54-c087-46da-b283-0fbe0365df0e",
      "dispositivo": "android-evidencia-0e84f5",
      "cliente": "android",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "recibido_en": "2026-11-26T15:23:59-06:00",
      "total": 1,
      "aplicadas": 0,
      "duplicadas": 0,
      "conflictos": 1,
      "rechazadas": 0,
      "pendientes": 0
    },
    {
      "id": 176,
      "lote_uuid": "c644f0a2-8db1-4238-9bf9-a24aef094751",
      "dispositivo": "android-evidencia-0e84f5",
      "cliente": "android",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "recibido_en": "2026-11-26T15:23:58-06:00",
      "total": 2,
      "aplicadas": 2,
      "duplicadas": 2,
      "conflictos": 0,
      "rechazadas": 0,
      "pendientes": 0
    },
    {
      "id": 175,
      "lote_uuid": "831ee958-62f8-40f3-9192-86a4d4ec1cce",
      "dispositivo": "android-flujo-0921cf",
      "cliente": "android",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "recibido_en": "2026-11-26T15:22:07-06:00",
      "total": 2,
      "aplicadas": 2,
      "duplicadas": 2,
      "conflictos": 0,
      "rechazadas": 0,
      "pendientes": 0
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 3,
    "total": 151,
    "paginas": 51
  }
}
```

### SYN-06 · Un lote con sus operaciones · PASA

**Objetivo.** Cada operación con su resultado.

**Petición.** `GET http://sincronizacion:5125/api/v1/sincronizacion/lotes/176`

```http
Accept: application/json
X-Traza-Id: b615cdea-5fa3-49ff-ada9-820ad98e44c9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 66 ms · traza `b615cdea-5fa3-49ff-ada9-820ad98e44c9`

```json
{
  "id": 176,
  "lote_uuid": "c644f0a2-8db1-4238-9bf9-a24aef094751",
  "dispositivo": "android-evidencia-0e84f5",
  "cliente": "android",
  "usuario": {
    "id": 7,
    "nombre": "Ramiro Alanís Lozano"
  },
  "recibido_en": "2026-11-26T15:23:58-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 2,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "id": 191,
      "lote_uuid": "c644f0a2-8db1-4238-9bf9-a24aef094751",
      "dispositivo": "android-evidencia-0e84f5",
      "operacion_uuid": "a801713b-ec37-4f20-9293-a12b7071047f",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-26T15:11:58-06:00",
      "estado": "aplicada",
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "intentos": 1,
      "procesada_en": "2026-11-26T15:23:58-06:00",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      }
    },
    {
      "id": 192,
      "lote_uuid": "c644f0a2-8db1-4238-9bf9-a24aef094751",
      "dispositivo": "android-evidencia-0e84f5",
      "operacion_uuid": "95fbfc93-ef04-4388-b460-77f7f2ab54da",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-26T15:20:58-06:00",
      "estado": "aplicada",
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "intentos": 1,
      "procesada_en": "2026-11-26T15:23:59-06:00",
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
X-Traza-Id: 5dcd7026-e4df-42a8-8c2d-723af4cfc711
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 60 ms · traza `5dcd7026-e4df-42a8-8c2d-723af4cfc711`

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

**Petición.** `GET http://sincronizacion:5125/api/v1/sincronizacion/estado?dispositivo=android-evidencia-0e84f5`

```http
Accept: application/json
X-Traza-Id: 318db117-1d1c-4098-a605-23f9158b643f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 53 ms · traza `318db117-1d1c-4098-a605-23f9158b643f`

```json
{
  "dispositivo": "android-evidencia-0e84f5",
  "ultima_sincronizacion": "2026-11-26T15:23:59-06:00",
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
X-Traza-Id: 5a47bd6c-b3c2-4967-b5cb-da635eaec64a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 31 ms · traza `5a47bd6c-b3c2-4967-b5cb-da635eaec64a`

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
X-Traza-Id: 8d9f83f9-fcfd-4e6e-8754-2e2c3f9b97fc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "c644f0a2-8db1-4238-9bf9-a24aef094751",
  "dispositivo": "android-evidencia-0e84f5",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "95fbfc93-ef04-4388-b460-77f7f2ab54da",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-26T21:20:58.715826+00:00",
      "datos": {
        "entrega_id": 304,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "Cliente ausente",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b08a36e5ea8dba9ecdb0b0a"
        ],
        "capturado_en": "2026-11-26T21:20:58.715793+00:00"
      }
    },
    {
      "operacion_uuid": "a801713b-ec37-4f20-9293-a12b7071047f",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-26T21:11:58.715837+00:00",
      "datos": {
        "entrega_id": 304,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-26T21:11:58.715841+00:00"
          }
        ]
      }
    }
  ]
}
```

**Respuesta.** HTTP 403 (esperado 403) · 35 ms · traza `8d9f83f9-fcfd-4e6e-8754-2e2c3f9b97fc`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "8d9f83f9-fcfd-4e6e-8754-2e2c3f9b97fc"
  }
}
```

### SYN-11 · Lote mal formado · PASA

**Objetivo.** operaciones debe ser una lista.

**Petición.** `POST http://sincronizacion:5125/api/v1/sincronizacion/lotes`

```http
Accept: application/json
X-Traza-Id: ee8d9348-890f-4fd2-a697-5b368fbeb70c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "c644f0a2-8db1-4238-9bf9-a24aef094751",
  "dispositivo": "android-evidencia-0e84f5",
  "cliente": "android",
  "operaciones": "x"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 47 ms · traza `ee8d9348-890f-4fd2-a697-5b368fbeb70c`

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
    "traza_id": "ee8d9348-890f-4fd2-a697-5b368fbeb70c"
  }
}
```

### SYN-12 · Estado en XML · PASA

**Objetivo.** Validado contra sincronizacion.xsd.

**Petición.** `GET http://sincronizacion:5125/api/v1/sincronizacion/estado?dispositivo=android-evidencia-0e84f5`

```http
Accept: application/xml
X-Traza-Id: 43b0de68-c7ad-47af-9a63-c47a8935cb55
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 123 ms · traza `43b0de68-c7ad-47af-9a63-c47a8935cb55`

```xml
<?xml version='1.0' encoding='utf-8'?>
<sync_estado xmlns="urn:microhubs:v1" version="1"><dispositivo>android-evidencia-0e84f5</dispositivo><ultima_sincronizacion>2026-11-26T15:23:59-06:00</ultima_sincronizacion><lotes>2</lotes><aplicadas>2</aplicadas><conflictos>1</conflictos><rechazadas>0</rechazadas><pendientes>0</pendientes></sync_estado>
```

## Servicio productos · puerto 5103

### PRD-A1 · Alta de producto · PASA

**Objetivo.** Alta con permiso; queda en la bitácora y limpia la caché.

**Petición.** `POST http://productos:5103/api/v1/productos`

```http
Accept: application/json
X-Traza-Id: 819bee52-e2ba-48fe-bb77-4281bf696ae1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "clave_interna": "EV-D5F75A",
  "nombre": "Producto de evidencia D5F75A",
  "categoria_id": 1,
  "unidad": "pieza",
  "precio": 19.5
}
```

**Respuesta.** HTTP 201 (esperado 201) · 87 ms · traza `819bee52-e2ba-48fe-bb77-4281bf696ae1`

```json
{
  "id": 63,
  "clave_interna": "EV-D5F75A",
  "nombre": "Producto de evidencia D5F75A",
  "categoria": {
    "id": 1,
    "nombre": "Abarrote básico"
  },
  "unidad": "pieza",
  "presentacion": null,
  "precio": 19.5,
  "imagen_url": null,
  "estatus": "activo"
}
```

**Evidencia en PostgreSQL.** `SELECT accion, usuario_id, fecha FROM auditoria WHERE entidad = %s AND entidad_id = %s ORDER BY id`

```json
[
  {
    "accion": "alta",
    "usuario_id": 1,
    "fecha": "2026-11-26 15:24:01.549375-06:00"
  }
]
```

### PRD-A2 · Cambio de producto (PATCH) · PASA

**Objetivo.** Solo los campos enviados.

**Petición.** `PATCH http://productos:5103/api/v1/productos/63`

```http
Accept: application/json
X-Traza-Id: c79877eb-ed24-44a9-b23d-2e79b1132f82
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "precio": 21.0
}
```

**Respuesta.** HTTP 200 (esperado 200) · 70 ms · traza `c79877eb-ed24-44a9-b23d-2e79b1132f82`

```json
{
  "id": 63,
  "clave_interna": "EV-D5F75A",
  "nombre": "Producto de evidencia D5F75A",
  "categoria": {
    "id": 1,
    "nombre": "Abarrote básico"
  },
  "unidad": "pieza",
  "presentacion": null,
  "precio": 21.0,
  "imagen_url": null,
  "estatus": "activo"
}
```

### PRD-A3 · Cambio de producto (PUT) · PASA

**Objetivo.** PUT es alias de PATCH.

**Petición.** `PUT http://productos:5103/api/v1/productos/63`

```http
Accept: application/json
X-Traza-Id: ed2700cb-70b5-45de-97f4-f935953a63bf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "precio": 21.0
}
```

**Respuesta.** HTTP 200 (esperado 200) · 63 ms · traza `ed2700cb-70b5-45de-97f4-f935953a63bf`

```json
{
  "id": 63,
  "clave_interna": "EV-D5F75A",
  "nombre": "Producto de evidencia D5F75A",
  "categoria": {
    "id": 1,
    "nombre": "Abarrote básico"
  },
  "unidad": "pieza",
  "presentacion": null,
  "precio": 21.0,
  "imagen_url": null,
  "estatus": "activo"
}
```

### PRD-A4 · Alta de producto sin permiso · PASA

**Objetivo.** El operador no administra el catálogo.

**Petición.** `POST http://productos:5103/api/v1/productos`

```http
Accept: application/json
X-Traza-Id: 82b2df57-3c15-43d5-a462-54810ffe49f1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "clave_interna": "EV-D5F75A",
  "nombre": "Producto de evidencia D5F75A",
  "categoria_id": 1,
  "unidad": "pieza",
  "precio": 19.5
}
```

**Respuesta.** HTTP 403 (esperado 403) · 27 ms · traza `82b2df57-3c15-43d5-a462-54810ffe49f1`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "82b2df57-3c15-43d5-a462-54810ffe49f1"
  }
}
```

### PRD-A5 · Baja de producto · PASA

**Objetivo.** Baja lógica: se conserva su historia.

**Petición.** `DELETE http://productos:5103/api/v1/productos/63`

```http
Accept: application/json
X-Traza-Id: f91aa28f-4216-4a44-9cb4-d48b855fd24f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 47 ms · traza `f91aa28f-4216-4a44-9cb4-d48b855fd24f`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT id, estatus FROM producto WHERE id = %s`

```json
[
  {
    "id": 63,
    "estatus": "inactivo"
  }
]
```

## Servicio zonas · puerto 5108

### ZNA-A1 · Alta de zona · PASA

**Objetivo.** Alta con permiso; queda en la bitácora y limpia la caché.

**Petición.** `POST http://zonas:5108/api/v1/zonas`

```http
Accept: application/json
X-Traza-Id: 5b2dee41-91eb-4417-8e81-c5b76a1c443f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "clave": "********",
  "nombre": "Zona D5F75A",
  "colonia": "Colonia D5F75A",
  "codigo_postal": "64102",
  "latitud": 25.77,
  "longitud": -100.37
}
```

**Respuesta.** HTTP 201 (esperado 201) · 65 ms · traza `5b2dee41-91eb-4417-8e81-c5b76a1c443f`

```json
{
  "id": 11,
  "clave": "********",
  "nombre": "Zona D5F75A",
  "colonia": "Colonia D5F75A",
  "codigo_postal": "64102",
  "latitud": 25.77,
  "longitud": -100.37
}
```

**Evidencia en PostgreSQL.** `SELECT accion, usuario_id, fecha FROM auditoria WHERE entidad = %s AND entidad_id = %s ORDER BY id`

```json
[
  {
    "accion": "alta",
    "usuario_id": 1,
    "fecha": "2026-11-26 15:24:01.875536-06:00"
  }
]
```

### ZNA-A2 · Cambio de zona (PATCH) · PASA

**Objetivo.** Solo los campos enviados.

**Petición.** `PATCH http://zonas:5108/api/v1/zonas/11`

```http
Accept: application/json
X-Traza-Id: 120434fd-8199-4e86-829a-5494c2ead365
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Zona D5F75A renombrada"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 78 ms · traza `120434fd-8199-4e86-829a-5494c2ead365`

```json
{
  "id": 11,
  "clave": "********",
  "nombre": "Zona D5F75A renombrada",
  "colonia": "Colonia D5F75A",
  "codigo_postal": "64102",
  "latitud": 25.77,
  "longitud": -100.37
}
```

### ZNA-A3 · Cambio de zona (PUT) · PASA

**Objetivo.** PUT es alias de PATCH.

**Petición.** `PUT http://zonas:5108/api/v1/zonas/11`

```http
Accept: application/json
X-Traza-Id: c70a506c-4369-4152-b7cd-7dbe2e0ec002
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Zona D5F75A renombrada"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 83 ms · traza `c70a506c-4369-4152-b7cd-7dbe2e0ec002`

```json
{
  "id": 11,
  "clave": "********",
  "nombre": "Zona D5F75A renombrada",
  "colonia": "Colonia D5F75A",
  "codigo_postal": "64102",
  "latitud": 25.77,
  "longitud": -100.37
}
```

### ZNA-A4 · Alta de zona sin permiso · PASA

**Objetivo.** El operador no administra el catálogo.

**Petición.** `POST http://zonas:5108/api/v1/zonas`

```http
Accept: application/json
X-Traza-Id: 18d3a799-ddb4-471d-8968-219288d95627
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "clave": "********",
  "nombre": "Zona D5F75A",
  "colonia": "Colonia D5F75A",
  "codigo_postal": "64102",
  "latitud": 25.77,
  "longitud": -100.37
}
```

**Respuesta.** HTTP 403 (esperado 403) · 893 ms · traza `18d3a799-ddb4-471d-8968-219288d95627`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "18d3a799-ddb4-471d-8968-219288d95627"
  }
}
```

### ZNA-A5 · Baja de zona · PASA

**Objetivo.** Baja lógica: se conserva su historia.

**Petición.** `DELETE http://zonas:5108/api/v1/zonas/11`

```http
Accept: application/json
X-Traza-Id: f982b18c-53f2-45a9-9fca-89226401a254
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 48 ms · traza `f982b18c-53f2-45a9-9fca-89226401a254`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT id, estatus FROM zona WHERE id = %s`

```json
[
  {
    "id": 11,
    "estatus": "inactivo"
  }
]
```

## Servicio microhubs · puerto 5109

### MIC-A1 · Alta de microhub · PASA

**Objetivo.** Alta con permiso; queda en la bitácora y limpia la caché.

**Petición.** `POST http://microhubs:5109/api/v1/microhubs`

```http
Accept: application/json
X-Traza-Id: 17e15579-60fe-4a3f-8ee2-9688feb82b5d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "clave": "********",
  "nombre": "Microhub D5F75A",
  "direccion": "Calle de evidencia 1",
  "latitud": 25.7705,
  "longitud": -100.3705,
  "radio_km": 0.5,
  "capacidad_turno": 10
}
```

**Respuesta.** HTTP 201 (esperado 201) · 60 ms · traza `17e15579-60fe-4a3f-8ee2-9688feb82b5d`

```json
{
  "id": 10,
  "clave": "********",
  "nombre": "Microhub D5F75A",
  "latitud": 25.7705,
  "longitud": -100.3705,
  "radio_km": 0.5,
  "estatus": "activo"
}
```

**Evidencia en PostgreSQL.** `SELECT accion, usuario_id, fecha FROM auditoria WHERE entidad = %s AND entidad_id = %s ORDER BY id`

```json
[
  {
    "accion": "alta",
    "usuario_id": 1,
    "fecha": "2026-11-26 15:24:03.090155-06:00"
  }
]
```

### MIC-A2 · Cambio de microhub (PATCH) · PASA

**Objetivo.** Solo los campos enviados.

**Petición.** `PATCH http://microhubs:5109/api/v1/microhubs/10`

```http
Accept: application/json
X-Traza-Id: 179757fe-2165-400d-8f1f-f00ecfea63bc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "radio_km": 0.8
}
```

**Respuesta.** HTTP 200 (esperado 200) · 93 ms · traza `179757fe-2165-400d-8f1f-f00ecfea63bc`

```json
{
  "id": 10,
  "clave": "********",
  "nombre": "Microhub D5F75A",
  "latitud": 25.7705,
  "longitud": -100.3705,
  "radio_km": 0.8,
  "estatus": "activo"
}
```

### MIC-A3 · Cambio de microhub (PUT) · PASA

**Objetivo.** PUT es alias de PATCH.

**Petición.** `PUT http://microhubs:5109/api/v1/microhubs/10`

```http
Accept: application/json
X-Traza-Id: d0a6c78d-695c-402d-951b-0d1d51c919ca
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "radio_km": 0.8
}
```

**Respuesta.** HTTP 200 (esperado 200) · 92 ms · traza `d0a6c78d-695c-402d-951b-0d1d51c919ca`

```json
{
  "id": 10,
  "clave": "********",
  "nombre": "Microhub D5F75A",
  "latitud": 25.7705,
  "longitud": -100.3705,
  "radio_km": 0.8,
  "estatus": "activo"
}
```

### MIC-A4 · Alta de microhub sin permiso · PASA

**Objetivo.** El operador no administra el catálogo.

**Petición.** `POST http://microhubs:5109/api/v1/microhubs`

```http
Accept: application/json
X-Traza-Id: b9f9664b-493c-413b-a059-b15792b7afd1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "clave": "********",
  "nombre": "Microhub D5F75A",
  "direccion": "Calle de evidencia 1",
  "latitud": 25.7705,
  "longitud": -100.3705,
  "radio_km": 0.5,
  "capacidad_turno": 10
}
```

**Respuesta.** HTTP 403 (esperado 403) · 26 ms · traza `b9f9664b-493c-413b-a059-b15792b7afd1`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "b9f9664b-493c-413b-a059-b15792b7afd1"
  }
}
```

### MIC-A5 · Baja de microhub · PASA

**Objetivo.** Baja lógica: se conserva su historia.

**Petición.** `DELETE http://microhubs:5109/api/v1/microhubs/10`

```http
Accept: application/json
X-Traza-Id: 8eba4581-c99a-46b3-b3c6-9bcb1dc56f68
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 50 ms · traza `8eba4581-c99a-46b3-b3c6-9bcb1dc56f68`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT id, estatus FROM microhub WHERE id = %s`

```json
[
  {
    "id": 10,
    "estatus": "inactivo"
  }
]
```

## Servicio usuarios · puerto 5102

### USR-A1 · Crear una cuenta · PASA

**Objetivo.** La clave se guarda con bcrypt y no se devuelve.

**Petición.** `POST http://usuarios:5102/api/v1/usuarios`

```http
Accept: application/json
X-Traza-Id: b06ff831-5b33-4ec2-9214-413c817668e2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Cuenta",
  "apellidos": "De evidencia",
  "correo": "ev.d5f75a@ejemplo.mx",
  "clave": "********",
  "rol": "repartidor"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 191 ms · traza `b06ff831-5b33-4ec2-9214-413c817668e2`

```json
{
  "id": 60,
  "nombre": "Cuenta",
  "apellidos": "De evidencia",
  "correo": "ev.d5f75a@ejemplo.mx",
  "telefono": null,
  "rol": "repartidor",
  "microhub": null,
  "ultimo_acceso": null
}
```

**Evidencia en PostgreSQL.** `SELECT id, correo, left(hash_contrasena, 4) AS algoritmo, estatus FROM usuario WHERE id = %s`

```json
[
  {
    "id": 60,
    "correo": "ev.d5f75a@ejemplo.mx",
    "algoritmo": "$2b$",
    "estatus": "activo"
  }
]
```

### USR-A2 · Cambiar el perfil de una cuenta · PASA

**Objetivo.** Cierra sus sesiones.

**Petición.** `PATCH http://usuarios:5102/api/v1/usuarios/60`

```http
Accept: application/json
X-Traza-Id: 6669b9a2-54cd-4c98-8451-b8184df64ee4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "rol": "planeador"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 95 ms · traza `6669b9a2-54cd-4c98-8451-b8184df64ee4`

```json
{
  "id": 60,
  "nombre": "Cuenta",
  "apellidos": "De evidencia",
  "correo": "ev.d5f75a@ejemplo.mx",
  "telefono": null,
  "rol": "planeador",
  "microhub": null,
  "ultimo_acceso": null
}
```

### USR-A3 · Cambiar una cuenta (PUT) · PASA

**Objetivo.** PUT es alias de PATCH.

**Petición.** `PUT http://usuarios:5102/api/v1/usuarios/60`

```http
Accept: application/json
X-Traza-Id: affadf57-58e6-424d-af9d-23d1701b8e47
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "telefono": "8112223344"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 83 ms · traza `affadf57-58e6-424d-af9d-23d1701b8e47`

```json
{
  "id": 60,
  "nombre": "Cuenta",
  "apellidos": "De evidencia",
  "correo": "ev.d5f75a@ejemplo.mx",
  "telefono": "8112223344",
  "rol": "planeador",
  "microhub": null,
  "ultimo_acceso": null
}
```

### USR-A4 · Nadie se cambia a sí mismo · PASA

**Objetivo.** Protege al último administrador.

**Petición.** `DELETE http://usuarios:5102/api/v1/usuarios/1`

```http
Accept: application/json
X-Traza-Id: 67561c16-5894-46b3-9d1a-a6cb8bc67baa
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 409 (esperado 409) · 21 ms · traza `67561c16-5894-46b3-9d1a-a6cb8bc67baa`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "No puedes cambiar tu propio perfil ni darte de baja: pídeselo a otro administrador.",
    "traza_id": "67561c16-5894-46b3-9d1a-a6cb8bc67baa"
  }
}
```

### USR-A5 · Dar de baja una cuenta · PASA

**Objetivo.** Baja lógica y cierre de sesiones.

**Petición.** `DELETE http://usuarios:5102/api/v1/usuarios/60`

```http
Accept: application/json
X-Traza-Id: 17aff91b-6ef1-415a-9fc8-ad93a85bafda
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 38 ms · traza `17aff91b-6ef1-415a-9fc8-ad93a85bafda`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT id, estatus, fecha_baja IS NOT NULL AS con_fecha FROM usuario WHERE id = %s`

```json
[
  {
    "id": 60,
    "estatus": "baja",
    "con_fecha": true
  }
]
```

## Servicio pedidos · puerto 5104

### PED-A1 · Crear un pedido · PASA

**Objetivo.** Precio del servidor, ticket mínimo y asignación del motor.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: 373f3152-5891-4f5a-8b23-75ec75fd1c4d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
Content-Type: application/json
```

```json
{
  "lineas": [
    {
      "producto_id": 32,
      "cantidad": 3
    },
    {
      "producto_id": 51,
      "cantidad": 3
    }
  ],
  "operacion_uuid": "cc59ce38-4314-4a23-8949-6f314ced129f"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 271 ms · traza `373f3152-5891-4f5a-8b23-75ec75fd1c4d`

```json
{
  "id": 598,
  "folio": "PED-20261126-000598",
  "estado": "asignado",
  "zona_id": 3,
  "microhub_id": 2,
  "subtotal": 420.0,
  "costo_envio": 0.0,
  "total": 420.0,
  "asignado": true,
  "motivo": null,
  "duplicado": false
}
```

**Evidencia en PostgreSQL.** `SELECT pedido_id, producto_id, cantidad, precio_unitario FROM pedido_detalle WHERE pedido_id = %s`

```json
[
  {
    "pedido_id": 598,
    "producto_id": 32,
    "cantidad": 3,
    "precio_unitario": "72.00"
  },
  {
    "pedido_id": 598,
    "producto_id": 51,
    "cantidad": 3,
    "precio_unitario": "68.00"
  }
]
```

### PED-A2 · Reenviar el mismo pedido · PASA

**Objetivo.** Idempotente: no se duplica.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: 421a14e5-3008-40b8-aa25-bac2a69bbed0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
Content-Type: application/json
```

```json
{
  "lineas": [
    {
      "producto_id": 32,
      "cantidad": 3
    },
    {
      "producto_id": 51,
      "cantidad": 3
    }
  ],
  "operacion_uuid": "cc59ce38-4314-4a23-8949-6f314ced129f"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 50 ms · traza `421a14e5-3008-40b8-aa25-bac2a69bbed0`

```json
{
  "id": 598,
  "folio": "PED-20261126-000598",
  "estado": "asignado",
  "zona_id": 3,
  "microhub_id": 2,
  "subtotal": 420.0,
  "costo_envio": 0.0,
  "total": 420.0,
  "asignado": true,
  "motivo": null,
  "duplicado": true
}
```

### PED-A3 · Pedido bajo el mínimo · PASA

**Objetivo.** RN07: queda como demanda no atendida.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: 09a90079-d249-4198-ac75-f5ddeb0cbbfc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
Content-Type: application/json
```

```json
{
  "lineas": [
    {
      "producto_id": 28,
      "cantidad": 1
    }
  ]
}
```

**Respuesta.** HTTP 422 (esperado 422) · 127 ms · traza `09a90079-d249-4198-ac75-f5ddeb0cbbfc`

```json
{
  "error": {
    "codigo": "REGLA_NEGOCIO",
    "mensaje": "El subtotal (7.50) no alcanza el pedido mínimo de la zona (90.00).",
    "traza_id": "09a90079-d249-4198-ac75-f5ddeb0cbbfc"
  }
}
```

**Evidencia en PostgreSQL.** `SELECT tipo, zona_id, origen, fecha FROM demanda_no_atendida WHERE origen = 'api' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "tipo": "bajo_ticket_minimo",
    "zona_id": 3,
    "origen": "api",
    "fecha": "2026-11-26 15:24:04.411527-06:00"
  }
]
```

### PED-A4 · Marcar listo · PASA

**Objetivo.** El operador libera el pedido para despacho.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/598/listo`

```http
Accept: application/json
X-Traza-Id: 305d8670-ea0f-40cb-b640-bf04c2899f4b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 88 ms · traza `305d8670-ea0f-40cb-b640-bf04c2899f4b`

```json
{
  "id": 598,
  "estado": "en_preparacion",
  "listo_en": "2026-11-26T15:24:05-06:00"
}
```

## Servicio entregas · puerto 5105

### ENT-A1 · Asignar la entrega · PASA

**Objetivo.** Queda en ruta y el repartidor recibe el aviso.

**Petición.** `POST http://entregas:5105/api/v1/entregas`

```http
Accept: application/json
X-Traza-Id: d8993a5b-a5c6-4b95-b36f-8733b99e7b6f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 598,
  "repartidor_id": 7
}
```

**Respuesta.** HTTP 201 (esperado 201) · 88 ms · traza `d8993a5b-a5c6-4b95-b36f-8733b99e7b6f`

```json
{
  "entrega_id": 305,
  "pedido_id": 598,
  "repartidor_id": 7,
  "estado_pedido": "en_ruta"
}
```

**Evidencia en PostgreSQL.** `SELECT id, repartidor_id, turno_fecha, salida_en FROM entrega WHERE pedido_id = %s`

```json
[
  {
    "id": 305,
    "repartidor_id": 7,
    "turno_fecha": "2026-11-26",
    "salida_en": "2026-11-26 15:24:05.099448-06:00"
  }
]
```

### ENT-A2 · Asignar dos veces · PASA

**Objetivo.** El pedido ya tiene entrega.

**Petición.** `POST http://entregas:5105/api/v1/entregas`

```http
Accept: application/json
X-Traza-Id: 1be0e14a-c23d-4a6a-b5e6-f128d1205966
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 598,
  "repartidor_id": 7
}
```

**Respuesta.** HTTP 409 (esperado 409) · 31 ms · traza `1be0e14a-c23d-4a6a-b5e6-f128d1205966`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Ese pedido ya tiene una entrega asignada.",
    "traza_id": "1be0e14a-c23d-4a6a-b5e6-f128d1205966"
  }
}
```

### ENT-A3 · El repartidor no asigna · PASA

**Objetivo.** Sin entregas.asignar.

**Petición.** `POST http://entregas:5105/api/v1/entregas`

```http
Accept: application/json
X-Traza-Id: c1eabe68-2622-4245-91d8-b76b2d445cae
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 598,
  "repartidor_id": 7
}
```

**Respuesta.** HTTP 403 (esperado 403) · 31 ms · traza `c1eabe68-2622-4245-91d8-b76b2d445cae`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "c1eabe68-2622-4245-91d8-b76b2d445cae"
  }
}
```

## Servicio auth · puerto 5101

### SAL-AUT · Salud de auth · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://auth:5101/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 3de7e7de-a396-4aec-b00a-3ac5d868bdf3
```

**Respuesta.** HTTP 200 (esperado 200) · 31 ms · traza `3de7e7de-a396-4aec-b00a-3ac5d868bdf3`

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
  "tiempo_ms": 26.4
}
```

## Servicio usuarios · puerto 5102

### SAL-USU · Salud de usuarios · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://usuarios:5102/api/v1/health`

```http
Accept: application/json
X-Traza-Id: f01043e0-058b-445d-b424-f51c591593fc
```

**Respuesta.** HTTP 200 (esperado 200) · 23 ms · traza `f01043e0-058b-445d-b424-f51c591593fc`

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
  "tiempo_ms": 18.5
}
```

## Servicio productos · puerto 5103

### SAL-PRO · Salud de productos · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://productos:5103/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 7cc15831-c013-48a8-9f66-12f02942d54f
```

**Respuesta.** HTTP 200 (esperado 200) · 21 ms · traza `7cc15831-c013-48a8-9f66-12f02942d54f`

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
  "tiempo_ms": 18.4
}
```

## Servicio pedidos · puerto 5104

### SAL-PED · Salud de pedidos · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://pedidos:5104/api/v1/health`

```http
Accept: application/json
X-Traza-Id: e089b5d0-d1ee-41a6-9f39-8055e534a7d1
```

**Respuesta.** HTTP 200 (esperado 200) · 21 ms · traza `e089b5d0-d1ee-41a6-9f39-8055e534a7d1`

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
  "tiempo_ms": 17.2
}
```

## Servicio entregas · puerto 5105

### SAL-ENT · Salud de entregas · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://entregas:5105/api/v1/health`

```http
Accept: application/json
X-Traza-Id: dfed72f2-6e27-4443-8e0c-99f61881cd23
```

**Respuesta.** HTTP 200 (esperado 200) · 27 ms · traza `dfed72f2-6e27-4443-8e0c-99f61881cd23`

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
  "tiempo_ms": 23.3
}
```

## Servicio planeacion · puerto 5106

### SAL-PLA · Salud de planeacion · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://planeacion:5106/api/v1/health`

```http
Accept: application/json
X-Traza-Id: b9348a54-f3c7-456a-ac53-af8c25ed2e4e
```

**Respuesta.** HTTP 200 (esperado 200) · 24 ms · traza `b9348a54-f3c7-456a-ac53-af8c25ed2e4e`

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
  "tiempo_ms": 21.4
}
```

## Servicio documentos · puerto 5107

### SAL-DOC · Salud de documentos · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://documentos:5107/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 112143a1-585f-4dde-ae37-701bd84df0ef
```

**Respuesta.** HTTP 200 (esperado 200) · 20 ms · traza `112143a1-585f-4dde-ae37-701bd84df0ef`

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
  "tiempo_ms": 17.2
}
```

## Servicio zonas · puerto 5108

### SAL-ZON · Salud de zonas · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://zonas:5108/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 946a194d-24ef-4604-814f-ec30e4ea0009
```

**Respuesta.** HTTP 200 (esperado 200) · 20 ms · traza `946a194d-24ef-4604-814f-ec30e4ea0009`

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
  "tiempo_ms": 17.2
}
```

## Servicio microhubs · puerto 5109

### SAL-MIC · Salud de microhubs · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://microhubs:5109/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 6018770d-b156-4917-81ce-75b9d1855274
```

**Respuesta.** HTTP 200 (esperado 200) · 25 ms · traza `6018770d-b156-4917-81ce-75b9d1855274`

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
  "tiempo_ms": 22.3
}
```

## Servicio seguimiento · puerto 5110

### SAL-SEG · Salud de seguimiento · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://seguimiento:5110/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 41942237-4f16-40b6-9813-8b5ddda4e7e7
```

**Respuesta.** HTTP 200 (esperado 200) · 22 ms · traza `41942237-4f16-40b6-9813-8b5ddda4e7e7`

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
  "tiempo_ms": 19.6
}
```

## Servicio inventario · puerto 5111

### SAL-INV · Salud de inventario · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://inventario:5111/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 5cede3f7-9473-4b98-9570-f3b68e98f6da
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `5cede3f7-9473-4b98-9570-f3b68e98f6da`

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
  "tiempo_ms": 14.8
}
```

## Servicio precios · puerto 5112

### SAL-PRE · Salud de precios · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://precios:5112/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 0c4c9b16-5353-4804-8157-270fdca6de82
```

**Respuesta.** HTTP 200 (esperado 200) · 20 ms · traza `0c4c9b16-5353-4804-8157-270fdca6de82`

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
  "tiempo_ms": 18.0
}
```

## Servicio proveedores · puerto 5113

### SAL-PRO · Salud de proveedores · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://proveedores:5113/api/v1/health`

```http
Accept: application/json
X-Traza-Id: caec4cbc-12c6-47ad-b5fa-88ee3e09ba4f
```

**Respuesta.** HTTP 200 (esperado 200) · 21 ms · traza `caec4cbc-12c6-47ad-b5fa-88ee3e09ba4f`

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
  "tiempo_ms": 17.7
}
```

## Servicio abastecimiento · puerto 5114

### SAL-ABA · Salud de abastecimiento · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://abastecimiento:5114/api/v1/health`

```http
Accept: application/json
X-Traza-Id: a2a5c959-971c-4f67-a707-5af5c2f59dda
```

**Respuesta.** HTTP 200 (esperado 200) · 18 ms · traza `a2a5c959-971c-4f67-a707-5af5c2f59dda`

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
  "tiempo_ms": 15.8
}
```

## Servicio demanda · puerto 5115

### SAL-DEM · Salud de demanda · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://demanda:5115/api/v1/health`

```http
Accept: application/json
X-Traza-Id: f6b6aee8-6e05-49fb-b002-488d701f0275
```

**Respuesta.** HTTP 200 (esperado 200) · 24 ms · traza `f6b6aee8-6e05-49fb-b002-488d701f0275`

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
  "tiempo_ms": 21.2
}
```

## Servicio cobertura · puerto 5116

### SAL-COB · Salud de cobertura · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://cobertura:5116/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 80cfc9e8-4ec3-417b-9c29-eb16094dc493
```

**Respuesta.** HTTP 200 (esperado 200) · 21 ms · traza `80cfc9e8-4ec3-417b-9c29-eb16094dc493`

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
  "tiempo_ms": 18.2
}
```

## Servicio capacidad · puerto 5117

### SAL-CAP · Salud de capacidad · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://capacidad:5117/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 10648a5f-040a-4002-81c6-60f73d69b835
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `10648a5f-040a-4002-81c6-60f73d69b835`

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
  "tiempo_ms": 13.3
}
```

## Servicio rutas · puerto 5118

### SAL-RUT · Salud de rutas · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://rutas:5118/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 4f536d16-d470-4012-9bb2-e049f7b988e7
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `4f536d16-d470-4012-9bb2-e049f7b988e7`

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
  "tiempo_ms": 14.2
}
```

## Servicio costos · puerto 5119

### SAL-COS · Salud de costos · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://costos:5119/api/v1/health`

```http
Accept: application/json
X-Traza-Id: cbae1068-28ac-438a-9b6f-cf2e12036330
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `cbae1068-28ac-438a-9b6f-cf2e12036330`

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
  "tiempo_ms": 14.2
}
```

## Servicio punto-equilibrio · puerto 5120

### SAL-PUN · Salud de punto-equilibrio · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://punto-equilibrio:5120/api/v1/health`

```http
Accept: application/json
X-Traza-Id: f274684f-f2df-4cdb-bef9-1eea0c1190db
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `f274684f-f2df-4cdb-bef9-1eea0c1190db`

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
  "tiempo_ms": 13.9
}
```

## Servicio simulacion · puerto 5121

### SAL-SIM · Salud de simulacion · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://simulacion:5121/api/v1/health`

```http
Accept: application/json
X-Traza-Id: a3376aff-9e6d-49b6-a885-a3e85c9c373c
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `a3376aff-9e6d-49b6-a885-a3e85c9c373c`

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
  "tiempo_ms": 13.8
}
```

## Servicio surtido · puerto 5122

### SAL-SUR · Salud de surtido · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://surtido:5122/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 02528165-cd5e-47ec-bbef-8203770d66e2
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `02528165-cd5e-47ec-bbef-8203770d66e2`

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
  "tiempo_ms": 13.9
}
```

## Servicio notificaciones · puerto 5124

### SAL-NOT · Salud de notificaciones · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://notificaciones:5124/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 8f9dbf8a-ac45-43c1-abb5-844808f9cac0
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `8f9dbf8a-ac45-43c1-abb5-844808f9cac0`

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
  "tiempo_ms": 13.7
}
```

## Servicio reportes · puerto 5123

### SAL-REP · Salud de reportes · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://reportes:5123/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 4ab0d60d-9888-4155-af24-1dd3d5ea65d9
```

**Respuesta.** HTTP 200 (esperado 200) · 20 ms · traza `4ab0d60d-9888-4155-af24-1dd3d5ea65d9`

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
  "tiempo_ms": 17.3
}
```

## Servicio sincronizacion · puerto 5125

### SAL-SIN · Salud de sincronizacion · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://sincronizacion:5125/api/v1/health`

```http
Accept: application/json
X-Traza-Id: eb3816cb-5f48-4d0e-92ef-4d01be6fc1c9
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `eb3816cb-5f48-4d0e-92ef-4d01be6fc1c9`

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
  "tiempo_ms": 14.5
}
```

## Servicio auditoria-monitoreo · puerto 5126

### SAL-AUD · Salud de auditoria-monitoreo · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 1a7da6ae-39ac-40e9-9d6d-5f8b93881288
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `1a7da6ae-39ac-40e9-9d6d-5f8b93881288`

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
  "tiempo_ms": 14.3
}
```

## Servicio auth · puerto 5101

### MON-01 · Registro de actividad · PASA

**Objetivo.** Cada petición queda en MongoDB con su traza.

**Petición.** `GET http://auth:5101/api/v1/auth/validar`

```http
Accept: application/json
X-Traza-Id: 5aa8f0bf-755c-4eb6-a6ba-c25c801db1da
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 6 ms · traza `5aa8f0bf-755c-4eb6-a6ba-c25c801db1da`

```json
{
  "valido": true,
  "expira_en": 822,
  "usuario": {
    "id": 1,
    "rol": "administrador",
    "microhub_id": null
  }
}
```

**Explicación.** El X-Traza-Id de la petición se recupera en logs_tecnicos.correlacion_id.

**Evidencia en MongoDB.** `db.logs_tecnicos.findOne({correlacion_id: '5aa8f0bf-755c-4eb6-a6ba-c25c801db1da'})`

```json
{
  "nivel": "INFO",
  "componente": "auth",
  "registrado_en": "2026-11-26 21:24:05.971000+00:00",
  "correlacion_id": "5aa8f0bf-755c-4eb6-a6ba-c25c801db1da",
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
    "peticiones": 722,
    "ms_promedio": 108.71606648199446
  },
  {
    "_id": "auditoria-monitoreo",
    "peticiones": 2280,
    "ms_promedio": 54.694298245614036
  },
  {
    "_id": "auth",
    "peticiones": 2507,
    "ms_promedio": 271.3430394894296
  },
  {
    "_id": "capacidad",
    "peticiones": 935,
    "ms_promedio": 61.37754010695187
  },
  {
    "_id": "cobertura",
    "peticiones": 1528,
    "ms_promedio": 51.3684554973822
  },
  {
    "_id": "costos",
    "peticiones": 1813,
    "ms_promedio": 44.59404302261445
  },
  {
    "_id": "demanda",
    "peticiones": 1696,
    "ms_promedio": 101.6120283018868
  },
  {
    "_id": "documentos",
    "peticiones": 440,
    "ms_promedio": 29.727272727272727
  },
  {
    "_id": "entregas",
    "peticiones": 955,
    "ms_promedio": 75.76230366492146
  },
  {
    "_id": "inventario",
    "peticiones": 1854,
    "ms_promedio": 57.85976267529666
  },
  {
    "_id": "microhubs",
    "peticiones": 374,
    "ms_promedio": 20.9572192513369
  },
  {
    "_id": "notificaciones",
    "peticiones": 385,
    "ms_promedio": 30.802597402597403
  },
  {
    "_id": "pedidos",
    "peticiones": 2420,
    "ms_promedio": 84.3309917355372
  },
  {
    "_id": "planeacion",
    "peticiones": 781,
    "ms_promedio": 48.0371318822023
  },
  {
    "_id": "precios",
    "peticiones": 843,
    "ms_promedio": 48.69039145907473
  },
  {
    "_id": "productos",
    "peticiones": 309,
    "ms_promedio": 30.148867313915858
  },
  {
    "_id": "proveedores",
    "peticiones": 623,
    "ms_promedio": 51.22792937399679
  },
  {
    "_id": "punto-equilibrio",
    "peticiones": 1108,
    "ms_promedio": 174.5216606498195
  },
  {
    "_id": "reportes",
    "peticiones": 1061,
    "ms_promedio": 162.78605089538172
  },
  {
    "_id": "rutas",
    "peticiones": 943,
    "ms_promedio": 104.02332979851538
  },
  {
    "_id": "seguimiento",
    "peticiones": 180,
    "ms_promedio": 29.677777777777777
  },
  {
    "_id": "simulacion",
    "peticiones": 1426,
    "ms_promedio": 152.38849929873774
  },
  {
    "_id": "sincronizacion",
    "peticiones": 645,
    "ms_promedio": 98.69612403100776
  },
  {
    "_id": "surtido",
    "peticiones": 734,
    "ms_promedio": 187.18119891008175
  },
  {
    "_id": "usuarios",
    "peticiones": 221,
    "ms_promedio": 43.11764705882353
  },
  {
    "_id": "zonas",
    "peticiones": 2720,
    "ms_promedio": 3.0220588235294117
  }
]
```

## Servicio zonas · puerto 5108

### RAT-01 · Límite de consumo excedido · PASA

**Objetivo.** Más de 240 solicitudes por minuto desde la misma IP.

**Petición.** `GET http://zonas:5108/api/v1/zonas`

```http
Accept: application/json
X-Traza-Id: 2884dfb7-33af-466a-a291-04ee24f3c2c0
```

**Respuesta.** HTTP 429 (esperado 429) · 3 ms · traza `2884dfb7-33af-466a-a291-04ee24f3c2c0`

```json
{
  "error": {
    "codigo": "LIMITE_EXCEDIDO",
    "mensaje": "Máximo 240 solicitudes por minuto. Espera 52 segundos.",
    "traza_id": "2884dfb7-33af-466a-a291-04ee24f3c2c0"
  }
}
```

**Explicación.** Contador rate:zonas:{ip}:{minuto} en Redis (db 1) con TTL de 120 s; responde Retry-After.

**Evidencia en Redis.** `db1 GET rate:zonas:536eb84a13507f73:29928803; db1 TTL rate:zonas:536eb84a13507f73:29928803`

```json
[
  {
    "comando": "db1 GET rate:zonas:536eb84a13507f73:29928803",
    "valor": "1"
  },
  {
    "comando": "db1 TTL rate:zonas:536eb84a13507f73:29928803",
    "valor": 66
  }
]
```
