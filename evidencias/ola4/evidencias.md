# Evidencias de petición y respuesta · microservicios v1

Generado el 2026-11-27 05:21 contra los servicios en ejecución. 439 de 439 casos pasan.

## Servicio auth · puerto 5101

### AUTH-01 · Iniciar sesión (JSON) · PASA

**Objetivo.** Emitir el JWT de acceso y el token de renovación del repartidor.

**Petición.** `POST http://auth:5101/api/v1/auth/login`

```http
Accept: application/json
X-Traza-Id: 4f060e75-bd0f-41a8-8180-40fcd7b7b085
Content-Type: application/json
```

```json
{
  "correo": "repartidor1@codex.mx",
  "clave": "********",
  "dispositivo": "Pixel 7"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 294 ms · traza `4f060e75-bd0f-41a8-8180-40fcd7b7b085`

```json
{
  "token_acceso": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwicm9sIjo…(291 caracteres)",
  "token_renovacion": "rt_042486925ef497b0a5ebbf4a33b06f14",
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

**Evidencia en Redis.** `SMEMBERS auth:sesion:7; TTL auth:sesion:7; TTL auth:refresh:03642894758c8e1654a2b0c7a19a99554edac8e4f28f391df58e54add2004da2`

```json
[
  {
    "comando": "SMEMBERS auth:sesion:7",
    "valor": [
      "0901f01fed074e28a755b384f44021ea",
      "0c36f57b71d24cdc8ec8f7c840c68fa9",
      "0f3797b84d7b4809a31cce23aac92e80",
      "107f32345b8a4e93abca926ba0df3858",
      "24c079d56ccd43c89ad5333f436ac9f3",
      "3765306b0cb24ded9c1c387b3e5a2390",
      "46a96f306b87452b949ca1bc1647ec67",
      "4a87c255c9c14a3c8dd4d184ca29b44d",
      "4ee5ea3403c3496f85737fb7395871a0",
      "65bcbd2ce5ef4427a24e472573f18627",
      "69c2d3bb58f84504a0c387bd9f8ab348",
      "74347588215d45b5a0d7f9913a91e3b0",
      "79fec9e046584360bea8beca258a95c7",
      "7c3d858324e14362828a37722e77a3a0",
      "7c408cc19e1e4360a1bbcddc434c3ddd",
      "853a8f29ca994c6c85d8795be0fafe0c",
      "8e539d9ac47c46d1ba45a7bf8adc95e8",
      "97ef3d3fc8f74667b4589f6767b3f2c2",
      "a080c0ed48cd4c9594e36894b718265f",
      "a25e07aad64846f39f78fa0cf0754d6e",
      "abdbf969cd3245a1876e9e65d7c82260",
      "addad99d34a0478c8c9ccd2f13fdc1b8",
      "b092f566bdad425682af3576ac9be677",
      "b0d269c1aab94f2fa8e74c850b21da9a",
      "b15c6401f4334d22803249c8a6f50779",
      "b71393c895bf404599ebffc5641e52af",
      "b7d8edae763d4988bfd41acff1e1bb2f",
      "be2d90dcd1974defb7f0a2ae9ea2fdee",
      "c55a74e245e54995b01e584bb80e6222",
      "cae0fcf0bea94a4da27f0c7b12f62993",
      "cea76a475b964ab1b06d15a97dd2c15e",
      "dfd273b4182b4a35b3e3a73d0fb39c39",
      "ebef07d4caf54ff38feaf7cffe9565e2",
      "eca25e2ee24a46ab9f75d1af8be3b5ee",
      "f0fc575f490f4a459677929a92c71b58",
      "f52448bb721b4962894fbd874acdba38",
      "f9f3b3ec9cb441158ad0f9d86a6db538"
    ]
  },
  {
    "comando": "TTL auth:sesion:7",
    "valor": 900
  },
  {
    "comando": "TTL auth:refresh:03642894758c8e1654a2b0c7a19a99554edac8e4f28f391df58e54add2004da2",
    "valor": 604800
  }
]
```

**Evidencia en PostgreSQL.** `SELECT fecha, modulo, accion, detalle FROM auditoria WHERE correo_intento IS NULL AND usuario_id = 7 AND modulo = 'auth' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "fecha": "2026-11-26 23:20:23.521385-06:00",
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
X-Traza-Id: c6b60dd3-8337-4359-b664-397ab282d1b2
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><login xmlns="urn:microhubs:v1"><correo>planeador@codex.mx</correo><clave>********</clave></login>
```

**Respuesta.** HTTP 200 (esperado 200) · 272 ms · traza `c6b60dd3-8337-4359-b664-397ab282d1b2`

```xml
<?xml version='1.0' encoding='utf-8'?>
<sesion xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><token_acceso>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwicm9sIjo…(291 caracteres)</token_acceso><token_renovacion>rt_3d763b29ba8e39fe255b5053d9689735</token_renovacion><tipo>Bearer</tipo><expira_en>900</expira_en><usuario><id>5</id><nombre>Vanessa</nombre><apellidos>Morante López</apellidos><correo>planeador@codex.mx</correo><rol>planeador</rol><microhub_id xsi:nil="true" /><permisos><permiso>abastecimiento.ver</permiso><permiso>archivos.crear</permiso><permiso>archivos.ver</permiso><permiso>capacidad.editar</permiso><permiso>capacidad.ver</permiso><permiso>catalogo_publico.ver</permiso><permiso>cobertura.ver</permiso><permiso>configuracion.ver</permiso><permiso>costos.editar</permiso><permiso>costos.ver</permiso><permiso>demanda.editar</permiso><permiso>demanda.ver</permiso><permiso>equilibrio.editar</permiso><permiso>equilibrio.ver</permiso><permiso>indicadores.ver</permiso><permiso>inventario.ver</permiso><permiso>microhubs.ver</permiso><permiso>monitoreo.ver</permiso><permiso>notificaciones.ver</permiso><permiso>pedidos.reasignar</permiso><permiso>pedidos.ver</permiso><permiso>planeacion.editar</permiso><permiso>planeacion.ver</permiso><permiso>precios.ver</permiso><permiso>productos.ver</permiso><permiso>proveedores.ver</permiso><permiso>reportes.exportar</permiso><permiso>reportes.ver</permiso><permiso>rutas.planear</permiso><permiso>rutas.ver</permiso><permiso>simulacion.ejecutar</permiso><permiso>simulacion.ver</permiso><permiso>surtido.editar</permiso><permiso>surtido.ver</permiso><permiso>zonas.ver</permiso></permisos></usuario></sesion>
```

**Explicación.** El cuerpo XML se valida contra los XSD antes de procesarse; la respuesta <sesion> también cumple el XSD.

### AUTH-03 · Clave incorrecta · PASA

**Objetivo.** Rechazar credenciales y contar el intento.

**Petición.** `POST http://auth:5101/api/v1/auth/login`

```http
Accept: application/json
X-Traza-Id: b4554a8b-a957-41a3-add3-28e1b5d3c647
Content-Type: application/json
```

```json
{
  "correo": "auditor@codex.mx",
  "clave": "********"
}
```

**Respuesta.** HTTP 401 (esperado 401) · 231 ms · traza `b4554a8b-a957-41a3-add3-28e1b5d3c647`

```json
{
  "error": {
    "codigo": "CREDENCIALES_INVALIDAS",
    "mensaje": "Correo o clave incorrectos. Intento 1 de 5.",
    "traza_id": "b4554a8b-a957-41a3-add3-28e1b5d3c647"
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
X-Traza-Id: 8a979af6-c227-4322-9b22-85f90626b519
Content-Type: application/json
```

```json
{
  "correo": "sin-arroba",
  "clave": "********"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 5 ms · traza `8a979af6-c227-4322-9b22-85f90626b519`

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
    "traza_id": "8a979af6-c227-4322-9b22-85f90626b519"
  }
}
```

### AUTH-05 · XML con DTD (ataque XXE) · PASA

**Objetivo.** Rechazar entidades externas y DTD.

**Petición.** `POST http://auth:5101/api/v1/auth/login`

```http
Accept: application/xml
X-Traza-Id: fb50d608-8b25-48ae-8e39-488f7ce6160b
Content-Type: application/xml
```

```xml
<?xml version="1.0"?><!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]><login xmlns="urn:microhubs:v1"><correo>&e;</correo><clave>********</clave></login>
```

**Respuesta.** HTTP 400 (esperado 400) · 5 ms · traza `fb50d608-8b25-48ae-8e39-488f7ce6160b`

```xml
<?xml version='1.0' encoding='utf-8'?>
<error xmlns="urn:microhubs:v1" version="1"><codigo>XML_INVALIDO</codigo><mensaje>El cuerpo XML no está bien formado o contiene DTD/entidades.</mensaje><traza_id>fb50d608-8b25-48ae-8e39-488f7ce6160b</traza_id></error>
```

**Explicación.** El lector XML (defusedxml) prohíbe DTD y entidades; el error también llega en XML.

### AUTH-06 · Validar token · PASA

**Objetivo.** Comprobar firma, vigencia y sesión activa en Redis.

**Petición.** `GET http://auth:5101/api/v1/auth/validar`

```http
Accept: application/json
X-Traza-Id: 48c71811-7808-44e4-a35d-956c9d3209b5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 7 ms · traza `48c71811-7808-44e4-a35d-956c9d3209b5`

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
X-Traza-Id: e2474e01-e689-473f-a7a2-50f7427ef416
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 401 (esperado 401) · 5 ms · traza `e2474e01-e689-473f-a7a2-50f7427ef416`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.",
    "traza_id": "e2474e01-e689-473f-a7a2-50f7427ef416"
  }
}
```

### AUTH-08 · Renovar sesión · PASA

**Objetivo.** Obtener tokens nuevos con el token de renovación (rotación).

**Petición.** `POST http://auth:5101/api/v1/auth/renovar`

```http
Accept: application/json
X-Traza-Id: 4fd6dfdb-0551-4212-b03d-c110a0fb56b8
Content-Type: application/json
```

```json
{
  "token_renovacion": "rt_fb8d6e7809987a6cf69b8471bffbd938"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 71 ms · traza `4fd6dfdb-0551-4212-b03d-c110a0fb56b8`

```json
{
  "token_acceso": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwicm9sIjo…(291 caracteres)",
  "token_renovacion": "rt_98539305471d33edde1a4e6a579a886d",
  "tipo": "Bearer",
  "expira_en": 900
}
```

**Explicación.** El token de renovación usado se borra de Redis y su acceso anterior queda revocado.

**Evidencia en Redis.** `EXISTS auth:refresh:7ff0509bfdb1cad439bf4614f4bbbbfb6e3a4a8c3371161bff782940a988e117`

```json
[
  {
    "comando": "EXISTS auth:refresh:7ff0509bfdb1cad439bf4614f4bbbbfb6e3a4a8c3371161bff782940a988e117",
    "valor": 0
  }
]
```

### AUTH-09 · Reusar un token de renovación · PASA

**Objetivo.** Un token de renovación sirve una sola vez.

**Petición.** `POST http://auth:5101/api/v1/auth/renovar`

```http
Accept: application/json
X-Traza-Id: 7d7a3a10-6b59-42c9-b8c1-3280625d20dd
Content-Type: application/json
```

```json
{
  "token_renovacion": "rt_fb8d6e7809987a6cf69b8471bffbd938"
}
```

**Respuesta.** HTTP 401 (esperado 401) · 14 ms · traza `7d7a3a10-6b59-42c9-b8c1-3280625d20dd`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.",
    "traza_id": "7d7a3a10-6b59-42c9-b8c1-3280625d20dd"
  }
}
```

### AUTH-10 · Cerrar sesión · PASA

**Objetivo.** Revocar el acceso del encabezado y la renovación del cuerpo.

**Petición.** `POST http://auth:5101/api/v1/auth/salir`

```http
Accept: application/json
X-Traza-Id: b95867ce-ed74-4247-8a91-8b12eb42ed4b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "token_renovacion": "rt_98539305471d33edde1a4e6a579a886d"
}
```

**Respuesta.** HTTP 204 (esperado 204) · 37 ms · traza `b95867ce-ed74-4247-8a91-8b12eb42ed4b`

```json
(sin cuerpo)
```

**Explicación.** El jti se agrega a la lista de revocados con TTL igual a su vida restante y sale del conjunto de sesión.

**Evidencia en Redis.** `TTL auth:jti:revocado:1a4ef87ab9af4b749b41758e89f471a7; SISMEMBER auth:sesion:7 1a4ef87ab9af4b749b41758e89f471a7`

```json
[
  {
    "comando": "TTL auth:jti:revocado:1a4ef87ab9af4b749b41758e89f471a7",
    "valor": 899
  },
  {
    "comando": "SISMEMBER auth:sesion:7 1a4ef87ab9af4b749b41758e89f471a7",
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
X-Traza-Id: 0ca306f1-9707-4a95-9fe8-2c307d715e98
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 401 (esperado 401) · 9 ms · traza `0ca306f1-9707-4a95-9fe8-2c307d715e98`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.",
    "traza_id": "0ca306f1-9707-4a95-9fe8-2c307d715e98"
  }
}
```

**Explicación.** El servicio de usuarios consulta auth:jti:revocado en Redis: la revocación es común a todos.

### USR-01 · Mi perfil (JSON) · PASA

**Objetivo.** Consultar el perfil de quien inició sesión.

**Petición.** `GET http://usuarios:5102/api/v1/usuarios/yo`

```http
Accept: application/json
X-Traza-Id: 6166492d-2c0e-4534-8ef2-6a0694b56787
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 29 ms · traza `6166492d-2c0e-4534-8ef2-6a0694b56787`

```json
{
  "id": 7,
  "nombre": "Ramiro",
  "apellidos": "Alanís Lozano",
  "correo": "repartidor1@codex.mx",
  "telefono": "8112345678",
  "rol": "repartidor",
  "microhub": null,
  "ultimo_acceso": "2026-11-26T23:20:24-06:00"
}
```

### USR-02 · Mi perfil (XML) · PASA

**Objetivo.** El mismo recurso en XML según Accept.

**Petición.** `GET http://usuarios:5102/api/v1/usuarios/yo`

```http
Accept: application/xml
X-Traza-Id: 8299d103-a912-4c2d-88f6-6ac4336cf160
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 43 ms · traza `8299d103-a912-4c2d-88f6-6ac4336cf160`

```xml
<?xml version='1.0' encoding='utf-8'?>
<usuario xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>5</id><nombre>Vanessa</nombre><apellidos>Morante López</apellidos><correo>planeador@codex.mx</correo><telefono>8178109897</telefono><rol>planeador</rol><microhub xsi:nil="true" /><ultimo_acceso>2026-11-26T23:20:24-06:00</ultimo_acceso></usuario>
```

### USR-03 · Actualizar mi teléfono (PATCH) · PASA

**Objetivo.** Modificar un dato del perfil.

**Petición.** `PATCH http://usuarios:5102/api/v1/usuarios/yo`

```http
Accept: application/json
X-Traza-Id: cab49f40-865f-41bb-8d08-2319195ce002
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "telefono": "8112345678"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 62 ms · traza `cab49f40-865f-41bb-8d08-2319195ce002`

```json
{
  "id": 7,
  "nombre": "Ramiro",
  "apellidos": "Alanís Lozano",
  "correo": "repartidor1@codex.mx",
  "telefono": "8112345678",
  "rol": "repartidor",
  "microhub": null,
  "ultimo_acceso": "2026-11-26T23:20:24-06:00"
}
```

**Explicación.** El trigger de auditoría registra el cambio con el usuario que actuó.

**Evidencia en PostgreSQL.** `SELECT id, telefono, actualizado_en FROM usuario WHERE id = 7`

```json
[
  {
    "id": 7,
    "telefono": "8112345678",
    "actualizado_en": "2026-11-26 23:20:25.449845-06:00"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT fecha, accion, entidad, detalle FROM auditoria WHERE entidad = 'usuario' AND entidad_id = '7' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "fecha": "2026-11-26 23:20:25.449845-06:00",
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
X-Traza-Id: 57a34a95-2dbc-4117-b9a6-a35831fa46b1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "telefono": "12ab"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 10 ms · traza `57a34a95-2dbc-4117-b9a6-a35831fa46b1`

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
    "traza_id": "57a34a95-2dbc-4117-b9a6-a35831fa46b1"
  }
}
```

### USR-05 · Lista de usuarios (administrador) · PASA

**Objetivo.** Búsqueda y paginación.

**Petición.** `GET http://usuarios:5102/api/v1/usuarios?q=codex&rol=operador&pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: fcea0c7c-3191-4859-bdb5-8895dc2185a4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 55 ms · traza `fcea0c7c-3191-4859-bdb5-8895dc2185a4`

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
      "ultimo_acceso": "2026-11-26T23:20:02-06:00"
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
      "ultimo_acceso": "2026-11-26T23:20:06-06:00"
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
      "ultimo_acceso": "2026-11-26T23:19:08-06:00"
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
X-Traza-Id: 1b1572ca-4510-4ad8-bdd0-a1fd7f6b78a7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 35 ms · traza `1b1572ca-4510-4ad8-bdd0-a1fd7f6b78a7`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "1b1572ca-4510-4ad8-bdd0-a1fd7f6b78a7"
  }
}
```

**Evidencia en PostgreSQL.** `SELECT fecha, modulo, accion, detalle, exitoso FROM auditoria WHERE accion = 'acceso_denegado' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "fecha": "2026-11-26 23:20:25.631298-06:00",
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
X-Traza-Id: 39701be8-6ded-4b03-a871-d2b332d6866e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 54 ms · traza `39701be8-6ded-4b03-a871-d2b332d6866e`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "39701be8-6ded-4b03-a871-d2b332d6866e"
  }
}
```

## Servicio productos · puerto 5103

### PRO-01 · Productos con búsqueda (caché vacía) · PASA

**Objetivo.** Consultar productos; la respuesta se guarda en Redis.

**Petición.** `GET http://productos:5103/api/v1/productos?q=arroz&pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 7fc7dbcf-29df-4f4e-873e-34a3ca5a9aff
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 106 ms · traza `7fc7dbcf-29df-4f4e-873e-34a3ca5a9aff`

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
X-Traza-Id: f28eb38e-f2e1-4ede-ab89-516414c865b2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 8 ms · traza `f28eb38e-f2e1-4ede-ab89-516414c865b2`

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
X-Traza-Id: 7f2decdc-c943-4d0b-9628-c1b69135a055
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 100 ms · traza `7f2decdc-c943-4d0b-9628-c1b69135a055`

```xml
<?xml version='1.0' encoding='utf-8'?>
<productos xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><datos><producto><id>3</id><clave_interna>AB-003</clave_interna><nombre>Aceite vegetal</nombre><categoria><id>1</id><nombre>Abarrote básico</nombre></categoria><unidad>botella</unidad><presentacion>900 ml</presentacion><precio>42.00</precio><imagen_url xsi:nil="true" /><estatus>activo</estatus></producto><producto><id>2</id><clave_interna>AB-002</clave_interna><nombre>Arroz superextra</nombre><categoria><id>1</id><nombre>Abarrote básico</nombre></categoria><unidad>kg</unidad><presentacion>1 kg</presentacion><precio>29.90</precio><imagen_url xsi:nil="true" /><estatus>activo</estatus></producto></datos><paginacion><pagina>1</pagina><por_pagina>2</por_pagina><total>54</total><paginas>27</paginas></paginacion></productos>
```

### PRO-04 · Un producto · PASA

**Objetivo.** Detalle por id.

**Petición.** `GET http://productos:5103/api/v1/productos/3`

```http
Accept: application/json
X-Traza-Id: f47900f8-2639-45e1-b953-41ce95be6f9b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 88 ms · traza `f47900f8-2639-45e1-b953-41ce95be6f9b`

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
X-Traza-Id: 7dfcf6d9-ee2b-4a7f-ac49-91becc28a5d0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 53 ms · traza `7dfcf6d9-ee2b-4a7f-ac49-91becc28a5d0`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "7dfcf6d9-ee2b-4a7f-ac49-91becc28a5d0"
  }
}
```

### PRO-06 · Paginación fuera de rango · PASA

**Objetivo.** por_pagina máximo 100.

**Petición.** `GET http://productos:5103/api/v1/productos?por_pagina=500`

```http
Accept: application/json
X-Traza-Id: e96807aa-a401-484f-99ae-7d134a9f81c1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 8 ms · traza `e96807aa-a401-484f-99ae-7d134a9f81c1`

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
    "traza_id": "e96807aa-a401-484f-99ae-7d134a9f81c1"
  }
}
```

### PRO-07 · Sin token · PASA

**Objetivo.** Todo endpoint protegido exige Authorization: Bearer.

**Petición.** `GET http://productos:5103/api/v1/productos`

```http
Accept: application/json
X-Traza-Id: bc18f238-2ebe-439f-9113-00e3c868215c
```

**Respuesta.** HTTP 401 (esperado 401) · 6 ms · traza `bc18f238-2ebe-439f-9113-00e3c868215c`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "Falta el encabezado Authorization: Bearer <token>.",
    "traza_id": "bc18f238-2ebe-439f-9113-00e3c868215c"
  }
}
```

## Servicio zonas · puerto 5108

### ZON-01 · Zonas (XML) · PASA

**Objetivo.** Colonias atendidas con centroide, válidas contra catalogos.xsd.

**Petición.** `GET http://zonas:5108/api/v1/zonas`

```http
Accept: application/xml
X-Traza-Id: 100aa6cb-05f1-4eda-a633-6384dce3d1d2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 109 ms · traza `100aa6cb-05f1-4eda-a633-6384dce3d1d2`

```xml
<?xml version='1.0' encoding='utf-8'?>
<zonas xmlns="urn:microhubs:v1" version="1"><datos><zona><id>15</id><clave>EV1FF3C5</clave><nombre>Zona 1FF3C5 renombrada</nombre><colonia>Colonia 1FF3C5</colonia><codigo_postal>64102</codigo_postal><latitud>25.77</latitud><longitud>-100.37</longitud></zona><zona><id>14</id><clave>EV97A5B6</clave><nombre>Zona 97A5B6 renombrada</nombre><colonia>Colonia 97A5B6</colonia><codigo_postal>64102</codigo_postal><latitud>25.77</latitud><longitud>-100.37</longitud></zona><zona><id>11</id><clave>EVD5F75A</clave><nombre>Zona D5F75A renombrada</nombre><colonia>Colonia D5F75A</colonia><codigo_postal>64102</codigo_postal><latitud>25.77</latitud><longitud>-100.37</longitud></zona><zona><id>1</id><clave>ZN-SB01</clave><nombre>San Bernabé Centro</nombre><colonia>San Bernabé</colonia><codigo_postal>64100</codigo_postal><latitud>25.7455</latitud><longitud>-100.3585</longitud></zona><zona><id>2</id><clave>ZN-SB02</clave><nombre>Valles de San Bernabé</nombre><colonia>Valles de San Bernabé</colonia><codigo_postal>64103</codigo_postal><latitud>25.753</latitud><longitud>-100.369</longitud></zona><zona><id>3</id><clave>ZN-SB03</clave><nombre>Paseo de San Bernabé</nombre><colonia>Paseo de San Bernabé</colonia><codigo_postal>64103</codigo_postal><latitud>25.758</latitud><longitud>-100.3745</longitud></zona><zona><id>4</id><clave>ZN-SB04</clave><nombre>San Bernabé X (F-113)</nombre><colonia>San Bernabé X (F-113)</colonia><codigo_postal>64105</codigo_postal><latitud>25.7495</latitud><longitud>-100.38</longitud></zona></datos><paginacion><pagina>1</pagina><por_pagina>20</por_pagina><total>7</total><paginas>1</paginas></paginacion></zonas>
```

### ZON-02 · Una zona · PASA

**Objetivo.** Detalle por id.

**Petición.** `GET http://zonas:5108/api/v1/zonas/1`

```http
Accept: application/json
X-Traza-Id: 135273c8-8ca3-4394-95c8-0005726cb35f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 29 ms · traza `135273c8-8ca3-4394-95c8-0005726cb35f`

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
X-Traza-Id: af31b408-0b7f-46ea-aa84-4e2dd65f3cea
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 24 ms · traza `af31b408-0b7f-46ea-aa84-4e2dd65f3cea`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "af31b408-0b7f-46ea-aa84-4e2dd65f3cea"
  }
}
```

### ZON-04 · Sin token · PASA

**Objetivo.** Todo endpoint protegido exige Authorization: Bearer.

**Petición.** `GET http://zonas:5108/api/v1/zonas`

```http
Accept: application/json
X-Traza-Id: 8091edd9-fc49-493c-b685-85198d05ec80
```

**Respuesta.** HTTP 401 (esperado 401) · 4 ms · traza `8091edd9-fc49-493c-b685-85198d05ec80`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "Falta el encabezado Authorization: Bearer <token>.",
    "traza_id": "8091edd9-fc49-493c-b685-85198d05ec80"
  }
}
```

## Servicio microhubs · puerto 5109

### MIC-01 · Microhubs activos · PASA

**Objetivo.** Microhubs con coordenadas y radio.

**Petición.** `GET http://microhubs:5109/api/v1/microhubs?estatus=activo`

```http
Accept: application/json
X-Traza-Id: 7d308056-c4ae-46a1-a129-120c39611eed
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 80 ms · traza `7d308056-c4ae-46a1-a129-120c39611eed`

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
X-Traza-Id: bd9f6914-95ff-4ce4-a4c2-d1f656ffd21f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 27 ms · traza `bd9f6914-95ff-4ce4-a4c2-d1f656ffd21f`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "bd9f6914-95ff-4ce4-a4c2-d1f656ffd21f"
  }
}
```

### MIC-03 · Sin token · PASA

**Objetivo.** Todo endpoint protegido exige Authorization: Bearer.

**Petición.** `GET http://microhubs:5109/api/v1/microhubs`

```http
Accept: application/json
X-Traza-Id: 8fb0f645-8370-430f-b90b-07d9c0126743
```

**Respuesta.** HTTP 401 (esperado 401) · 5 ms · traza `8fb0f645-8370-430f-b90b-07d9c0126743`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "Falta el encabezado Authorization: Bearer <token>.",
    "traza_id": "8fb0f645-8370-430f-b90b-07d9c0126743"
  }
}
```

## Servicio pedidos · puerto 5104

### PED-01 · Pedidos entregados (JSON) · PASA

**Objetivo.** Lista filtrada por estado y fechas.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos?estado=entregado&pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: e04ddb25-b8fd-4ece-9ed8-32ada49090b6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 60 ms · traza `e04ddb25-b8fd-4ece-9ed8-32ada49090b6`

```json
{
  "datos": [
    {
      "id": 700,
      "folio": "PED-20261126-000700",
      "estado": "entregado",
      "zona": {
        "id": 3,
        "nombre": "Paseo de San Bernabé"
      },
      "microhub_id": 2,
      "total": 420.0,
      "creado_en": "2026-11-26T23:20:05-06:00"
    },
    {
      "id": 683,
      "folio": "PED-20261126-000683",
      "estado": "entregado",
      "zona": {
        "id": 3,
        "nombre": "Paseo de San Bernabé"
      },
      "microhub_id": 2,
      "total": 304.5,
      "creado_en": "2026-11-26T23:19:03-06:00"
    },
    {
      "id": 678,
      "folio": "PED-20261126-000678",
      "estado": "entregado",
      "zona": {
        "id": 4,
        "nombre": "San Bernabé X (F-113)"
      },
      "microhub_id": 3,
      "total": 117.0,
      "creado_en": "2026-11-26T23:15:49-06:00"
    },
    {
      "id": 677,
      "folio": "PED-20261126-000677",
      "estado": "entregado",
      "zona": {
        "id": 3,
        "nombre": "Paseo de San Bernabé"
      },
      "microhub_id": 2,
      "total": 420.0,
      "creado_en": "2026-11-26T23:12:52-06:00"
    },
    {
      "id": 672,
      "folio": "PED-20261126-000672",
      "estado": "entregado",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "microhub_id": 2,
      "total": 129.0,
      "creado_en": "2026-11-26T23:11:55-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 175,
    "paginas": 35
  }
}
```

### PED-02 · Pedidos (XML) · PASA

**Objetivo.** La misma lista en XML.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos?estado=entregado&por_pagina=2`

```http
Accept: application/xml
X-Traza-Id: 219d900a-4236-4325-b61f-d5bafb228fc8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 60 ms · traza `219d900a-4236-4325-b61f-d5bafb228fc8`

```xml
<?xml version='1.0' encoding='utf-8'?>
<pedidos xmlns="urn:microhubs:v1" version="1"><datos><pedido><id>700</id><folio>PED-20261126-000700</folio><estado>entregado</estado><zona><id>3</id><nombre>Paseo de San Bernabé</nombre></zona><microhub_id>2</microhub_id><total>420.00</total><creado_en>2026-11-26T23:20:05-06:00</creado_en></pedido><pedido><id>683</id><folio>PED-20261126-000683</folio><estado>entregado</estado><zona><id>3</id><nombre>Paseo de San Bernabé</nombre></zona><microhub_id>2</microhub_id><total>304.50</total><creado_en>2026-11-26T23:19:03-06:00</creado_en></pedido></datos><paginacion><pagina>1</pagina><por_pagina>2</por_pagina><total>175</total><paginas>88</paginas></paginacion></pedidos>
```

### PED-03 · Detalle con líneas · PASA

**Objetivo.** Cliente, domicilio y líneas del pedido.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/700`

```http
Accept: application/json
X-Traza-Id: 89d6f14e-28d1-405d-80ef-649534d546cb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 84 ms · traza `89d6f14e-28d1-405d-80ef-649534d546cb`

```json
{
  "id": 700,
  "folio": "PED-20261126-000700",
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
  "microhub_id": 2,
  "subtotal": 420.0,
  "costo_envio": 0.0,
  "total": 420.0,
  "creado_en": "2026-11-26T23:20:05-06:00",
  "lineas": [
    {
      "id": 1719,
      "producto_id": 32,
      "nombre": "Queso Oaxaca",
      "cantidad": 3,
      "precio_unitario": 72.0,
      "importe": 216.0
    },
    {
      "id": 1720,
      "producto_id": 51,
      "nombre": "Pañal etapa 3",
      "cantidad": 3,
      "precio_unitario": 68.0,
      "importe": 204.0
    }
  ]
}
```

### PED-04 · Historial de estados · PASA

**Objetivo.** Cambios de estado con usuario y fecha.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/700/historial`

```http
Accept: application/json
X-Traza-Id: d27fbb19-1fbe-4568-b427-131e86ebf27a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 56 ms · traza `d27fbb19-1fbe-4568-b427-131e86ebf27a`

```json
{
  "pedido_id": 700,
  "eventos": [
    {
      "estado_anterior": null,
      "estado_nuevo": "creado",
      "usuario": "juan.chapa1@correo.mx",
      "motivo": null,
      "fecha": "2026-11-26T23:20:05-06:00"
    },
    {
      "estado_anterior": "creado",
      "estado_nuevo": "asignado",
      "usuario": "juan.chapa1@correo.mx",
      "motivo": null,
      "fecha": "2026-11-26T23:20:05-06:00"
    },
    {
      "estado_anterior": "asignado",
      "estado_nuevo": "en_preparacion",
      "usuario": "operador.mh02@codex.mx",
      "motivo": null,
      "fecha": "2026-11-26T23:20:06-06:00"
    },
    {
      "estado_anterior": "en_preparacion",
      "estado_nuevo": "en_ruta",
      "usuario": "operador.mh02@codex.mx",
      "motivo": null,
      "fecha": "2026-11-26T23:20:06-06:00"
    },
    {
      "estado_anterior": "en_ruta",
      "estado_nuevo": "entregado",
      "usuario": "repartidor1@codex.mx",
      "motivo": null,
      "fecha": "2026-11-26T23:20:06-06:00"
    }
  ]
}
```

**Evidencia en PostgreSQL.** `SELECT fecha, estado_anterior, estado_nuevo, usuario_id FROM historial_estatus WHERE pedido_id = %s ORDER BY fecha, id`

```json
[
  {
    "fecha": "2026-11-26 23:20:05.526822-06:00",
    "estado_anterior": null,
    "estado_nuevo": "creado",
    "usuario_id": 9
  },
  {
    "fecha": "2026-11-26 23:20:05.526822-06:00",
    "estado_anterior": "creado",
    "estado_nuevo": "asignado",
    "usuario_id": 9
  },
  {
    "fecha": "2026-11-26 23:20:06.450785-06:00",
    "estado_anterior": "asignado",
    "estado_nuevo": "en_preparacion",
    "usuario_id": 3
  },
  {
    "fecha": "2026-11-26 23:20:06.613662-06:00",
    "estado_anterior": "en_preparacion",
    "estado_nuevo": "en_ruta",
    "usuario_id": 3
  },
  {
    "fecha": "2026-11-26 23:20:06.849407-06:00",
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
X-Traza-Id: c535dec4-ed95-4118-b8d1-ca0ba87b5bf4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 5 ms · traza `c535dec4-ed95-4118-b8d1-ca0ba87b5bf4`

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
    "traza_id": "c535dec4-ed95-4118-b8d1-ca0ba87b5bf4"
  }
}
```

### PED-06 · Pedido fuera del ámbito · PASA

**Objetivo.** El operador del MH-01 no ve pedidos de otro microhub (RN22).

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/1`

```http
Accept: application/json
X-Traza-Id: 5b130a0f-789b-4ce0-aa1c-8253810777ca
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 49 ms · traza `5b130a0f-789b-4ce0-aa1c-8253810777ca`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el pedido o no está en tu ámbito.",
    "traza_id": "5b130a0f-789b-4ce0-aa1c-8253810777ca"
  }
}
```

**Explicación.** El ámbito lo decide PostgreSQL con fn_pedidos_visibles; el servicio no lo puede saltar.

### PED-07 · Cerrar desde pedidos · PASA

**Objetivo.** Los cierres de entrega solo se registran en el servicio de entregas.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/700/estado`

```http
Accept: application/json
X-Traza-Id: 72cbe709-409e-478d-ae27-d30fcbc8d4b1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "estado": "entregado"
}
```

**Respuesta.** HTTP 409 (esperado 409) · 8 ms · traza `72cbe709-409e-478d-ae27-d30fcbc8d4b1`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "El cierre de una entrega se registra con POST /api/v1/entregas/{id}/resultado.",
    "traza_id": "72cbe709-409e-478d-ae27-d30fcbc8d4b1"
  }
}
```

### PED-08 · Transición ilegal (regla del motor) · PASA

**Objetivo.** Un pedido entregado no puede regresar a preparación.

**Petición.** `PATCH http://pedidos:5104/api/v1/pedidos/2/estado`

```http
Accept: application/json
X-Traza-Id: 42c19b66-d329-4637-af10-55d19c6c4dc7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0Iiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "estado": "en_preparacion"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 90 ms · traza `42c19b66-d329-4637-af10-55d19c6c4dc7`

```json
{
  "error": {
    "codigo": "REGLA_NEGOCIO",
    "mensaje": "RN20: transición ilegal entregado -> en_preparacion para el rol operador. El pedido PED-20261020-000002 conserva su estado.",
    "traza_id": "42c19b66-d329-4637-af10-55d19c6c4dc7"
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
X-Traza-Id: e94a6414-ebb8-4bf0-a865-091fbf2ca63a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "evidencia-entrega-389.jpg",
  "tipo_mime": "image/jpeg",
  "contenido_base64": "/9j/4AAQSkZJRgABAQAAAQABAAAAAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcY…(368 caracteres)",
  "referencia": {
    "tipo": "entrega",
    "id": "389"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 94 ms · traza `e94a6414-ebb8-4bf0-a865-091fbf2ca63a`

```json
{
  "id": "6b09131bf796dcc0841d6cce",
  "nombre": "evidencia-entrega-389.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "389"
  },
  "subido_por": 7,
  "creado_en": "2026-11-26T23:20:27-06:00",
  "ruta": "documentos/2026/11/6b09131bf796dcc0841d6cce.jpg",
  "privacidad": "privado",
  "estado": "activo",
  "metadatos": {
    "almacen": "local",
    "origen": "api"
  }
}
```

**Explicación.** Se valida que el contenido sea JPEG real, se calcula su SHA-256 y que la entrega sea del repartidor.

**Evidencia en MongoDB.** `db.documentos.findOne({_id: ObjectId('6b09131bf796dcc0841d6cce')}, {contenido: 0})`

```json
{
  "_id": "6b09131bf796dcc0841d6cce",
  "nombre": "evidencia-entrega-389.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "389"
  },
  "subido_por": 7,
  "creado_en": "2026-11-27 05:20:27.563000+00:00",
  "ruta": "documentos/2026/11/6b09131bf796dcc0841d6cce.jpg",
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
X-Traza-Id: 29cd56bf-179f-46af-8a75-baba94bf0fef
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "evidencia-entrega-390.jpg",
  "tipo_mime": "image/jpeg",
  "contenido_base64": "/9j/4AAQSkZJRgABAQAAAQABAAAAAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcY…(368 caracteres)",
  "referencia": {
    "tipo": "entrega",
    "id": "390"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 54 ms · traza `29cd56bf-179f-46af-8a75-baba94bf0fef`

```json
{
  "id": "6b09131bf796dcc0841d6cd1",
  "nombre": "evidencia-entrega-390.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "390"
  },
  "subido_por": 7,
  "creado_en": "2026-11-26T23:20:27-06:00",
  "ruta": "documentos/2026/11/6b09131bf796dcc0841d6cd1.jpg",
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
X-Traza-Id: 62180457-2c80-462c-9f64-1534b556e90b
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
    "id": "389"
  }
}
```

**Respuesta.** HTTP 422 (esperado 422) · 8 ms · traza `62180457-2c80-462c-9f64-1534b556e90b`

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
    "traza_id": "62180457-2c80-462c-9f64-1534b556e90b"
  }
}
```

### DOC-04 · Evidencia en entrega ajena · PASA

**Objetivo.** Un repartidor no adjunta a entregas de otro.

**Petición.** `POST http://documentos:5107/api/v1/documentos`

```http
Accept: application/json
X-Traza-Id: 59e5e4f1-67a1-47b2-b0cd-8834c7d4ca2a
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
    "id": "389"
  }
}
```

**Respuesta.** HTTP 403 (esperado 403) · 49 ms · traza `59e5e4f1-67a1-47b2-b0cd-8834c7d4ca2a`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Solo puedes adjuntar evidencia a tus entregas.",
    "traza_id": "59e5e4f1-67a1-47b2-b0cd-8834c7d4ca2a"
  }
}
```

### DOC-05 · Documento temporal · PASA

**Objetivo.** Documento que después se elimina.

**Petición.** `POST http://documentos:5107/api/v1/documentos`

```http
Accept: application/json
X-Traza-Id: 07779392-4407-4663-9573-d60861b84191
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

**Respuesta.** HTTP 201 (esperado 201) · 46 ms · traza `07779392-4407-4663-9573-d60861b84191`

```json
{
  "id": "6b09131c5f817588ebd63c2c",
  "nombre": "borrador.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "usuario",
    "id": "7"
  },
  "subido_por": 7,
  "creado_en": "2026-11-26T23:20:28-06:00",
  "ruta": "documentos/2026/11/6b09131c5f817588ebd63c2c.jpg",
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

**Petición.** `GET http://documentos:5107/api/v1/documentos?referencia_tipo=entrega&referencia_id=389`

```http
Accept: application/json
X-Traza-Id: 0c8d8032-4254-4b5e-8d8c-ba3f4491e1b4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 10 ms · traza `0c8d8032-4254-4b5e-8d8c-ba3f4491e1b4`

```json
{
  "datos": [
    {
      "id": "6b09131bf796dcc0841d6cce",
      "nombre": "evidencia-entrega-389.jpg",
      "tipo_mime": "image/jpeg",
      "tamano_bytes": 276,
      "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
      "referencia": {
        "tipo": "entrega",
        "id": "389"
      },
      "subido_por": 7,
      "creado_en": "2026-11-26T23:20:27-06:00",
      "ruta": "documentos/2026/11/6b09131bf796dcc0841d6cce.jpg",
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

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b09131bf796dcc0841d6cce`

```http
Accept: application/xml
X-Traza-Id: b2dc3585-0716-4247-8744-9c0a7da5f5c6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 10 ms · traza `b2dc3585-0716-4247-8744-9c0a7da5f5c6`

```xml
<?xml version='1.0' encoding='utf-8'?>
<documento xmlns="urn:microhubs:v1" version="1"><id>6b09131bf796dcc0841d6cce</id><nombre>evidencia-entrega-389.jpg</nombre><tipo_mime>image/jpeg</tipo_mime><tamano_bytes>276</tamano_bytes><sha256>7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc</sha256><referencia><tipo>entrega</tipo><id>389</id></referencia><subido_por>7</subido_por><creado_en>2026-11-26T23:20:27-06:00</creado_en><ruta>documentos/2026/11/6b09131bf796dcc0841d6cce.jpg</ruta><privacidad>privado</privacidad><estado>activo</estado><metadatos><almacen>local</almacen><origen>api</origen></metadatos></documento>
```

### DOC-08 · Contenido en Base64 · PASA

**Objetivo.** Recuperar el archivo.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b09131bf796dcc0841d6cce/contenido`

```http
Accept: application/json
X-Traza-Id: ee9d899c-b3f6-4d62-ba0a-883d48d216dc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 10 ms · traza `ee9d899c-b3f6-4d62-ba0a-883d48d216dc`

```json
{
  "id": "6b09131bf796dcc0841d6cce",
  "nombre": "evidencia-entrega-389.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "389"
  },
  "subido_por": 7,
  "creado_en": "2026-11-26T23:20:27-06:00",
  "ruta": "documentos/2026/11/6b09131bf796dcc0841d6cce.jpg",
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

**Petición.** `DELETE http://documentos:5107/api/v1/documentos/6b09131c5f817588ebd63c2c`

```http
Accept: application/json
X-Traza-Id: 4e5baf96-ade7-4273-a3a3-ef6078e4e7c9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 68 ms · traza `4e5baf96-ade7-4273-a3a3-ef6078e4e7c9`

```json
(sin cuerpo)
```

**Evidencia en MongoDB.** `db.documentos.countDocuments({_id: ObjectId('6b09131c5f817588ebd63c2c')})`

```json
1
```

### DOC-10 · Id inexistente · PASA

**Objetivo.** Registro que no existe.

**Petición.** `GET http://documentos:5107/api/v1/documentos/ffffffffffffffffffffffff`

```http
Accept: application/json
X-Traza-Id: a6d2f301-c425-46c4-b11d-963a381166a2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 10 ms · traza `a6d2f301-c425-46c4-b11d-963a381166a2`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "a6d2f301-c425-46c4-b11d-963a381166a2"
  }
}
```

## Servicio seguimiento · puerto 5110

### SEG-01 · Enviar puntos GPS · PASA

**Objetivo.** Guardar el recorrido del repartidor en MongoDB.

**Petición.** `POST http://seguimiento:5110/api/v1/seguimiento/389/ubicaciones`

```http
Accept: application/json
X-Traza-Id: f6ad13cd-59a8-453e-bdd6-421eb0fdc56d
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
      "capturado_en": "2026-11-27T05:14:28+00:00"
    },
    {
      "latitud": 25.7486,
      "longitud": -100.3606,
      "precision_m": 8.0,
      "capturado_en": "2026-11-27T05:16:28+00:00"
    },
    {
      "latitud": 25.7491,
      "longitud": -100.3611,
      "precision_m": 8.5,
      "capturado_en": "2026-11-27T05:18:28+00:00"
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 49 ms · traza `f6ad13cd-59a8-453e-bdd6-421eb0fdc56d`

```json
{
  "recibidos": 3
}
```

**Evidencia en MongoDB.** `db.ubicaciones_entrega.find({entrega_id: NumberLong(389)}).sort({capturado_en: 1})`

```json
[
  {
    "entrega_id": 389,
    "usuario_id": 7,
    "posicion": {
      "type": "Point",
      "coordinates": [
        -100.36,
        25.748
      ]
    },
    "precision_m": 9.0,
    "capturado_en": "2026-11-27 05:14:28+00:00",
    "recibido_en": "2026-11-27 05:20:28.469000+00:00"
  },
  {
    "entrega_id": 389,
    "usuario_id": 7,
    "posicion": {
      "type": "Point",
      "coordinates": [
        -100.3606,
        25.7486
      ]
    },
    "precision_m": 8.0,
    "capturado_en": "2026-11-27 05:16:28+00:00",
    "recibido_en": "2026-11-27 05:20:28.469000+00:00"
  },
  {
    "entrega_id": 389,
    "usuario_id": 7,
    "posicion": {
      "type": "Point",
      "coordinates": [
        -100.3611,
        25.7491
      ]
    },
    "precision_m": 8.5,
    "capturado_en": "2026-11-27 05:18:28+00:00",
    "recibido_en": "2026-11-27 05:20:28.469000+00:00"
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

**Petición.** `GET http://seguimiento:5110/api/v1/seguimiento/389/recorrido`

```http
Accept: application/json
X-Traza-Id: 6133af66-0c8a-4647-a7d4-f5bc9b030b50
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 46 ms · traza `6133af66-0c8a-4647-a7d4-f5bc9b030b50`

```json
{
  "entrega_id": 389,
  "puntos": 3,
  "distancia_km": 0.16,
  "inicio": "2026-11-26T23:14:28-06:00",
  "fin": "2026-11-26T23:18:28-06:00",
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

**Petición.** `GET http://seguimiento:5110/api/v1/seguimiento/389/recorrido`

```http
Accept: application/json
X-Traza-Id: 4c2aae33-7b30-4747-90c9-43d1486306ca
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4Iiwi…(296 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 57 ms · traza `4c2aae33-7b30-4747-90c9-43d1486306ca`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe la entrega o no está asignada a ti.",
    "traza_id": "4c2aae33-7b30-4747-90c9-43d1486306ca"
  }
}
```

### SEG-04 · Recorrido sin token · PASA

**Objetivo.** Todo endpoint protegido exige Authorization: Bearer.

**Petición.** `GET http://seguimiento:5110/api/v1/seguimiento/389/recorrido`

```http
Accept: application/json
X-Traza-Id: b634b10b-f3fb-430e-a0db-cc39cab82791
```

**Respuesta.** HTTP 401 (esperado 401) · 14 ms · traza `b634b10b-f3fb-430e-a0db-cc39cab82791`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "Falta el encabezado Authorization: Bearer <token>.",
    "traza_id": "b634b10b-f3fb-430e-a0db-cc39cab82791"
  }
}
```

## Servicio entregas · puerto 5105

### ENT-01 · Mis entregas · PASA

**Objetivo.** Paradas abiertas del repartidor en el turno de hoy (RN25).

**Petición.** `GET http://entregas:5105/api/v1/entregas/mias?pagina=1&por_pagina=20`

```http
Accept: application/json
X-Traza-Id: c0d74301-f6a7-4dd5-aa38-78489fa1d29e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 89 ms · traza `c0d74301-f6a7-4dd5-aa38-78489fa1d29e`

```json
{
  "datos": [
    {
      "id": 377,
      "pedido_id": 680,
      "folio": "PED-20261126-000680",
      "estado_pedido": "en_ruta",
      "orden_parada": 1,
      "direccion": "Emiliano Zapata 231, Valles de San Bernabé",
      "zona": "Valles de San Bernabé",
      "distancia_km": 0.67,
      "minutos_estimados": 5.8,
      "total": 117.0
    },
    {
      "id": 389,
      "pedido_id": 701,
      "folio": "PED-20261126-000701",
      "estado_pedido": "en_ruta",
      "orden_parada": 1,
      "direccion": "Los Ángeles 3558, Valles de San Bernabé",
      "zona": "Valles de San Bernabé",
      "distancia_km": 0.36,
      "minutos_estimados": 10.0,
      "total": 141.0
    },
    {
      "id": 374,
      "pedido_id": 637,
      "folio": "PED-20261126-000637",
      "estado_pedido": "en_ruta",
      "orden_parada": 2,
      "direccion": "Valle Alto 2774, Valles de San Bernabé",
      "zona": "Valles de San Bernabé",
      "distancia_km": 0.93,
      "minutos_estimados": 12.6,
      "total": 143.0
    },
    {
      "id": 378,
      "pedido_id": 682,
      "folio": "PED-20261126-000682",
      "estado_pedido": "en_ruta",
      "orden_parada": 2,
      "direccion": "Emiliano Zapata 231, Valles de San Bernabé",
      "zona": "Valles de San Bernabé",
      "distancia_km": 0.0,
      "minutos_estimados": 9.8,
      "total": 277.5
    },
    {
      "id": 390,
      "pedido_id": 702,
      "folio": "PED-20261126-000702",
      "estado_pedido": "en_ruta",
      "orden_parada": 2,
      "direccion": "Rodrigo Gómez 1934, Paseo de San Bernabé",
      "zona": "Paseo de San Bernabé",
      "distancia_km": 1.17,
      "minutos_estimados": 16.0,
      "total": 166.0
    },
    {
      "id": 379,
      "pedido_id": 681,
      "folio": "PED-20261126-000681",
      "estado_pedido": "en_ruta",
      "orden_parada": 3,
      "direccion": "Valle Alto 2774, Valles de San Bernabé",
      "zona": "Valles de San Bernabé",
      "distancia_km": 0.93,
      "minutos_estimados": 16.4,
      "total": 147.0
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

### ENT-02 · Detalle de la entrega · PASA

**Objetivo.** Cliente, domicilio y líneas.

**Petición.** `GET http://entregas:5105/api/v1/entregas/389`

```http
Accept: application/json
X-Traza-Id: 1c17a2f0-de0e-47e2-8e59-c43ed967b2d6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 106 ms · traza `1c17a2f0-de0e-47e2-8e59-c43ed967b2d6`

```json
{
  "id": 389,
  "pedido_id": 701,
  "folio": "PED-20261126-000701",
  "estado_pedido": "en_ruta",
  "cliente": {
    "nombre": "Alejandro Sepúlveda Villarreal",
    "telefono": "8143577291"
  },
  "domicilio": {
    "calle": "Los Ángeles",
    "numero_ext": "3558",
    "colonia": "Valles de San Bernabé",
    "latitud": 25.753133,
    "longitud": -100.371504
  },
  "orden_parada": 1,
  "distancia_km": 0.36,
  "minutos_estimados": 10.0,
  "total": 141.0,
  "lineas": [
    {
      "pedido_detalle_id": 1721,
      "nombre": "Leche deslactosada",
      "cantidad": 2
    },
    {
      "pedido_detalle_id": 1722,
      "nombre": "Servilletas",
      "cantidad": 2
    }
  ]
}
```

### ENT-03 · Entrega de otro repartidor · PASA

**Objetivo.** El repartidor 2 no ve la entrega del repartidor 1.

**Petición.** `GET http://entregas:5105/api/v1/entregas/389`

```http
Accept: application/json
X-Traza-Id: ccc6c54b-5ea8-483a-9053-088c11c0b067
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4Iiwi…(296 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 36 ms · traza `ccc6c54b-5ea8-483a-9053-088c11c0b067`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe la entrega o no está asignada a ti.",
    "traza_id": "ccc6c54b-5ea8-483a-9053-088c11c0b067"
  }
}
```

### ENT-04 · Monto incorrecto (regla de negocio) · PASA

**Objetivo.** Una entrega completa cobra el total (RN27).

**Petición.** `POST http://entregas:5105/api/v1/entregas/389/resultado`

```http
Accept: application/json
X-Traza-Id: 0f04d78c-47c6-49e3-a487-01d47b646d5f
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
    "6b09131bf796dcc0841d6cce"
  ],
  "capturado_en": "2026-11-27T05:20:28+00:00",
  "id_cliente_local": "a3194d79-5c42-4c58-8bbb-f591e8e6c0bf"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 89 ms · traza `0f04d78c-47c6-49e3-a487-01d47b646d5f`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "monto_cobrado",
        "mensaje": "Una entrega completa cobra el total del pedido (141.00)."
      }
    ],
    "traza_id": "0f04d78c-47c6-49e3-a487-01d47b646d5f"
  }
}
```

### ENT-05 · Cerrar entrega como entregado · PASA

**Objetivo.** Registrar el resultado con evidencia y ubicación.

**Petición.** `POST http://entregas:5105/api/v1/entregas/389/resultado`

```http
Accept: application/json
X-Traza-Id: cd8ee9fd-cdd6-4f7d-b882-05f757148402
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 141.0,
  "cambio_entregado": 0.0,
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611,
    "precision_m": 8.5
  },
  "evidencia_ids": [
    "6b09131bf796dcc0841d6cce"
  ],
  "capturado_en": "2026-11-27T05:20:28+00:00",
  "id_cliente_local": "a3194d79-5c42-4c58-8bbb-f591e8e6c0bf"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 104 ms · traza `cd8ee9fd-cdd6-4f7d-b882-05f757148402`

```json
{
  "entrega_id": 389,
  "pedido_id": 701,
  "estado_pedido": "entregado",
  "cerrado_en": "2026-11-26T23:20:29-06:00",
  "duplicado": false
}
```

**Explicación.** Una sola transacción: cierra la entrega, cambia el pedido (el trigger valida la transición y escribe historial y bitácora) y el trigger de cierre avisa al cliente. La operación se registra en MongoDB.

**Evidencia en PostgreSQL.** `SELECT id, cierre_en, resultado, monto_cobrado, id_cliente_local, evidencia_ids, cierre_latitud, cierre_longitud FROM entrega WHERE id = %s`

```json
[
  {
    "id": 389,
    "cierre_en": "2026-11-26 23:20:29.065343-06:00",
    "resultado": "entregado",
    "monto_cobrado": "141.00",
    "id_cliente_local": "a3194d79-5c42-4c58-8bbb-f591e8e6c0bf",
    "evidencia_ids": [
      "6b09131bf796dcc0841d6cce"
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
    "fecha": "2026-11-26 23:20:29.065343-06:00"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT destinatario_id, tipo, titulo, mensaje, referencia_tipo, referencia_id FROM web_notificacion WHERE referencia_tipo = 'pedido' AND referencia_id = %s ORDER BY id DESC LIMIT 1`

```json
[
  {
    "destinatario_id": 41,
    "tipo": "pedido",
    "titulo": "Pedido PED-20261126-000701",
    "mensaje": "El pedido cambió a entregado.",
    "referencia_tipo": "pedido",
    "referencia_id": "701"
  }
]
```

**Evidencia en MongoDB.** `db.sincronizaciones_moviles.findOne({operacion_uuid: 'a3194d79-5c42-4c58-8bbb-f591e8e6c0bf'})`

```json
{
  "operacion_uuid": "a3194d79-5c42-4c58-8bbb-f591e8e6c0bf",
  "capturado_en": "2026-11-27 05:20:28+00:00",
  "carga": {
    "entrega_id": 389,
    "resultado": "entregado",
    "monto_cobrado": 141.0,
    "evidencia_ids": [
      "6b09131bf796dcc0841d6cce"
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
  "pedido_id": 701,
  "sincronizado_en": "2026-11-27 05:20:29.116000+00:00",
  "tipo_operacion": "cierre_entrega",
  "usuario_id": 7
}
```

### ENT-06 · Reintento con el mismo UUID · PASA

**Objetivo.** Idempotencia: el cierre no se aplica dos veces.

**Petición.** `POST http://entregas:5105/api/v1/entregas/389/resultado`

```http
Accept: application/json
X-Traza-Id: 23786eab-35e7-4a8a-9928-cb3a4f9c821d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 141.0,
  "cambio_entregado": 0.0,
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611,
    "precision_m": 8.5
  },
  "evidencia_ids": [
    "6b09131bf796dcc0841d6cce"
  ],
  "capturado_en": "2026-11-27T05:20:28+00:00",
  "id_cliente_local": "a3194d79-5c42-4c58-8bbb-f591e8e6c0bf"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 70 ms · traza `23786eab-35e7-4a8a-9928-cb3a4f9c821d`

```json
{
  "entrega_id": 389,
  "pedido_id": 701,
  "estado_pedido": "entregado",
  "cerrado_en": "2026-11-26T23:20:29-06:00",
  "duplicado": true
}
```

**Explicación.** La respuesta es la misma con duplicado=true. MongoDB actualiza el documento de la operación (intentos = 2).

**Evidencia en MongoDB.** `db.sincronizaciones_moviles.findOne({operacion_uuid: 'a3194d79-5c42-4c58-8bbb-f591e8e6c0bf'}, {estado: 1, intentos: 1})`

```json
{
  "estado": "aplicada",
  "intentos": 2,
  "sincronizado_en": "2026-11-27 05:20:29.244000+00:00"
}
```

### ENT-07 · Otro cierre sobre la misma entrega · PASA

**Objetivo.** Conflicto: ya estaba cerrada con otra operación.

**Petición.** `POST http://entregas:5105/api/v1/entregas/389/resultado`

```http
Accept: application/json
X-Traza-Id: 889fcd4b-3c5b-4b8c-b242-f8dbd0d2f7f1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 141.0,
  "cambio_entregado": 0.0,
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611,
    "precision_m": 8.5
  },
  "evidencia_ids": [
    "6b09131bf796dcc0841d6cce"
  ],
  "capturado_en": "2026-11-27T05:20:28+00:00",
  "id_cliente_local": "f1fad097-6d44-440c-8e78-68cc6fb38603"
}
```

**Respuesta.** HTTP 409 (esperado 409) · 71 ms · traza `889fcd4b-3c5b-4b8c-b242-f8dbd0d2f7f1`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "La entrega ya se cerró con otra operación.",
    "traza_id": "889fcd4b-3c5b-4b8c-b242-f8dbd0d2f7f1"
  }
}
```

### ENT-08 · Detalle tras el cierre · PASA

**Objetivo.** El repartidor deja de ver el domicilio (RN26).

**Petición.** `GET http://entregas:5105/api/v1/entregas/389`

```http
Accept: application/json
X-Traza-Id: e9fe1a36-137b-46d5-b522-ab8beb6ef2c3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 37 ms · traza `e9fe1a36-137b-46d5-b522-ab8beb6ef2c3`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "La entrega ya se cerró; su información ya no está disponible.",
    "traza_id": "e9fe1a36-137b-46d5-b522-ab8beb6ef2c3"
  }
}
```

### ENT-09 · Parcial sin motivo · PASA

**Objetivo.** Cada línea devuelta necesita motivo (RN28).

**Petición.** `POST http://entregas:5105/api/v1/entregas/390/resultado`

```http
Accept: application/json
X-Traza-Id: 37021403-9377-4637-8727-4299021c1615
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
      "pedido_detalle_id": 1723,
      "cantidad_entregada": 2,
      "cantidad_devuelta": 0
    },
    {
      "pedido_detalle_id": 1724,
      "cantidad_entregada": 0,
      "cantidad_devuelta": 2
    }
  ],
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611
  },
  "evidencia_ids": [
    "6b09131bf796dcc0841d6cd1"
  ],
  "capturado_en": "2026-11-27T05:20:28+00:00",
  "id_cliente_local": "c554ec43-4b7e-4289-be67-0292fdae7753"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 92 ms · traza `37021403-9377-4637-8727-4299021c1615`

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
    "traza_id": "37021403-9377-4637-8727-4299021c1615"
  }
}
```

### ENT-10 · Cerrar como entrega parcial · PASA

**Objetivo.** Devolver al inventario lo que no se entregó.

**Petición.** `POST http://entregas:5105/api/v1/entregas/390/resultado`

```http
Accept: application/json
X-Traza-Id: e00e6e2d-6ca9-4581-a579-7fa5d65af88a
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
      "pedido_detalle_id": 1723,
      "cantidad_entregada": 2,
      "cantidad_devuelta": 0
    },
    {
      "pedido_detalle_id": 1724,
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
    "6b09131bf796dcc0841d6cd1"
  ],
  "capturado_en": "2026-11-27T05:20:28+00:00",
  "id_cliente_local": "c554ec43-4b7e-4289-be67-0292fdae7753"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 115 ms · traza `e00e6e2d-6ca9-4581-a579-7fa5d65af88a`

```json
{
  "entrega_id": 390,
  "pedido_id": 702,
  "estado_pedido": "entrega_parcial",
  "cerrado_en": "2026-11-26T23:20:29-06:00",
  "duplicado": false
}
```

**Explicación.** fn_devolver_inventario (la misma función que usa el web) regresa las unidades devueltas.

**Evidencia en PostgreSQL.** `SELECT entrega_id, pedido_detalle_id, cantidad_entregada, cantidad_devuelta, motivo FROM entrega_linea WHERE entrega_id = %s`

```json
[
  {
    "entrega_id": 390,
    "pedido_detalle_id": 1723,
    "cantidad_entregada": 2,
    "cantidad_devuelta": 0,
    "motivo": null
  },
  {
    "entrega_id": 390,
    "pedido_detalle_id": 1724,
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
    "producto_id": 3,
    "cantidad": 2,
    "existencia_resultante": 52,
    "motivo": "Entrega parcial: regresan las unidades devueltas (RN28)."
  }
]
```

### ENT-11 · Entregas de un pedido (administrador) · PASA

**Objetivo.** Consulta por pedido para el portal web.

**Petición.** `GET http://entregas:5105/api/v1/entregas?pedido_id=701`

```http
Accept: application/json
X-Traza-Id: 975d2a33-ed31-48f8-a3e1-4e93f9b221c7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 56 ms · traza `975d2a33-ed31-48f8-a3e1-4e93f9b221c7`

```json
{
  "datos": [
    {
      "id": 389,
      "pedido_id": 701,
      "folio": "PED-20261126-000701",
      "estado_pedido": "entregado",
      "orden_parada": 1,
      "direccion": "Los Ángeles 3558, Valles de San Bernabé",
      "zona": "Valles de San Bernabé",
      "distancia_km": 0.36,
      "minutos_estimados": 10.0,
      "total": 141.0
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
X-Traza-Id: 973807d8-5076-463b-b598-37852ef935e0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 66 ms · traza `973807d8-5076-463b-b598-37852ef935e0`

```xml
<?xml version='1.0' encoding='utf-8'?>
<candidatos xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><datos><candidato><id>1</id><clave>CAND-01</clave><nombre>San Bernabé Norte</nombre><latitud>25.752</latitud><longitud>-100.361</longitud><renta_estimada>18000.00</renta_estimada><nomina_estimada>42000.00</nomina_estimada><servicios_estimados>7000.00</servicios_estimados><otros_costos>5000.00</otros_costos><costo_fijo>72000.00</costo_fijo><superficie_m2>130</superficie_m2><capacidad_fisica>150</capacidad_fisica><accesibilidad_vial>9</accesibilidad_vial><zona_id>1</zona_id><poblacion_cubierta>8420</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato><candidato><id>2</id><clave>CAND-02</clave><nombre>Valles Poniente</nombre><latitud>25.7555</latitud><longitud>-100.376</longitud><renta_estimada>15500.00</renta_estimada><nomina_estimada>42000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><costo_fijo>68500.00</costo_fijo><superficie_m2>105</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>2</zona_id><poblacion_cubierta>6180</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato><candidato><id>3</id><clave>CAND-05</clave><nombre>Alianza Real</nombre><latitud>25.7625</latitud><longitud>-100.353</longitud><renta_estimada>21000.00</renta_estimada><nomina_estimada>46000.00</nomina_estimada><servicios_estimados>8000.00</servicios_estimados><otros_costos>6000.00</otros_costos><costo_fijo>81000.00</costo_fijo><superficie_m2>150</superficie_m2><capacidad_fisica>180</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>3900</poblacion_cubierta><radio_km>1.6</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>25</total><paginas>9</paginas></paginacion></candidatos>
```

### PLA-02 · Registrar candidato (XML) · PASA

**Objetivo.** Alta con costo fijo calculado por PostgreSQL.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos`

```http
Accept: application/xml
X-Traza-Id: 7f6e03f2-510d-4597-8e65-8473803d641c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><candidato_nuevo xmlns="urn:microhubs:v1"><clave>********</clave><nombre>Alianza Norte</nombre><latitud>25.7601</latitud><longitud>-100.3555</longitud><renta_estimada>16000.00</renta_estimada><nomina_estimada>40000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><superficie_m2>110</superficie_m2><capacidad_fisica>130</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km></candidato_nuevo>
```

**Respuesta.** HTTP 201 (esperado 201) · 78 ms · traza `7f6e03f2-510d-4597-8e65-8473803d641c`

```xml
<?xml version='1.0' encoding='utf-8'?>
<candidato xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>275</id><clave>EV-952D8C</clave><nombre>Alianza Norte</nombre><latitud>25.7601</latitud><longitud>-100.3555</longitud><renta_estimada>16000.00</renta_estimada><nomina_estimada>40000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><costo_fijo>67000.00</costo_fijo><superficie_m2>110</superficie_m2><capacidad_fisica>130</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato>
```

**Evidencia en PostgreSQL.** `SELECT id, clave, nombre, renta_estimada, costo_fijo, decision FROM ubicacion_candidata WHERE clave = %s`

```json
[
  {
    "id": 275,
    "clave": "EV-952D8C",
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
X-Traza-Id: 3125dfcc-9cde-4dd8-8d0b-24211cad7b16
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><candidato_nuevo xmlns="urn:microhubs:v1"><clave>********</clave><nombre>Alianza Norte</nombre><latitud>25.7601</latitud><longitud>-100.3555</longitud><renta_estimada>16000.00</renta_estimada><nomina_estimada>40000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><superficie_m2>110</superficie_m2><capacidad_fisica>130</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km></candidato_nuevo>
```

**Respuesta.** HTTP 409 (esperado 409) · 57 ms · traza `3125dfcc-9cde-4dd8-8d0b-24211cad7b16`

```xml
<?xml version='1.0' encoding='utf-8'?>
<error xmlns="urn:microhubs:v1" version="1"><codigo>CONFLICTO</codigo><mensaje>Ya existe un registro con esos datos.</mensaje><traza_id>3125dfcc-9cde-4dd8-8d0b-24211cad7b16</traza_id></error>
```

### PLA-04 · Modificar candidato (PUT) · PASA

**Objetivo.** Cambiar la renta recalcula el costo fijo.

**Petición.** `PUT http://planeacion:5106/api/v1/candidatos/275`

```http
Accept: application/json
X-Traza-Id: e2cd1084-0e39-4e81-9da1-48df899e408f
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

**Respuesta.** HTTP 200 (esperado 200) · 84 ms · traza `e2cd1084-0e39-4e81-9da1-48df899e408f`

```json
{
  "id": 275,
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

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/275/simular`

```http
Accept: application/xml
X-Traza-Id: 042a5765-6e40-438e-8e4a-dbadac213a33
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<simular xmlns="urn:microhubs:v1"/>
```

**Respuesta.** HTTP 200 (esperado 200) · 292 ms · traza `042a5765-6e40-438e-8e4a-dbadac213a33`

```xml
<?xml version='1.0' encoding='utf-8'?>
<resultados xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><atendidos>0</atendidos><rechazados>0</rechazados><utilizacion>0</utilizacion><nivel>estable</nivel><tiempo_estimado_min>18.6</tiempo_estimado_min><operadores_requeridos>0</operadores_requeridos><repartidores_requeridos>0</repartidores_requeridos><ingreso_dia>0.00</ingreso_dia><margen_dia>-2300.00</margen_dia><costo_por_pedido xsi:nil="true" /><equilibrio><margen_pedido>25.84</margen_pedido><mensual>2670.3</mensual><diario>89</diario></equilibrio><decision>NO VIABLE CON LOS SUPUESTOS ACTUALES</decision><explicacion><motivo>la demanda atendida (0/día) no alcanza el equilibrio (89/día)</motivo><motivo>reducir costos fijos, aumentar ticket o buscar una ubicación con más demanda</motivo></explicacion></resultados>
```

**Explicación.** Usa planeacion_calc.py (las mismas fórmulas del web) y guarda la ejecución en MongoDB.

**Evidencia en MongoDB.** `db.ejecuciones_analiticas.find().sort({ejecutado_en: -1}).limit(1)`

```json
{
  "escenario_id": "candidato-275",
  "nombre_escenario": "Candidato 275",
  "tipo_analisis": "punto_equilibrio",
  "ejecutado_en": "2026-11-27 05:20:30.258000+00:00",
  "usuario_id": 5,
  "version_modelo": "planeacion_calc 2.1",
  "parametros_entrada": {
    "demanda_diaria": 0.0,
    "operadores": 3.0,
    "repartidores": 3.0,
    "ticket": 156.57,
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
    "ticket = 156.57",
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
    "equilibrio_diario": 89.0,
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

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/275/decision`

```http
Accept: application/json
X-Traza-Id: bf02ee1a-8a5b-4eb7-b732-42962871e208
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aceptado",
  "motivo": "ok"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 23 ms · traza `bf02ee1a-8a5b-4eb7-b732-42962871e208`

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
    "traza_id": "bf02ee1a-8a5b-4eb7-b732-42962871e208"
  }
}
```

### PLA-07 · Decisión humana de apertura · PASA

**Objetivo.** Registrar la decisión con motivo.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/275/decision`

```http
Accept: application/json
X-Traza-Id: aea2bcf8-c3e3-4685-b8fc-7c22e644ff9f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "condicionado",
  "motivo": "Renegociar la renta antes de firmar."
}
```

**Respuesta.** HTTP 200 (esperado 200) · 51 ms · traza `aea2bcf8-c3e3-4685-b8fc-7c22e644ff9f`

```json
{
  "id": 275,
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
    "id": 275,
    "decision": "condicionado",
    "decision_motivo": "Renegociar la renta antes de firmar.",
    "decision_por": 5,
    "decision_en": "2026-11-26 23:20:30.321038-06:00"
  }
]
```

### PLA-08 · Simulación libre: Escenario A · PASA

**Objetivo.** Punto de equilibrio del caso de la retroalimentación.

**Petición.** `POST http://planeacion:5106/api/v1/simulaciones`

```http
Accept: application/json
X-Traza-Id: 70275161-fa5e-4e55-805b-52e8276a38bd
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

**Respuesta.** HTTP 200 (esperado 200) · 37 ms · traza `70275161-fa5e-4e55-805b-52e8276a38bd`

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
X-Traza-Id: a2e0bde5-0fee-4ee6-9174-3577abb86628
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Escenario A - evidencias",
  "candidato_id": 275,
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

**Respuesta.** HTTP 201 (esperado 201) · 102 ms · traza `a2e0bde5-0fee-4ee6-9174-3577abb86628`

```json
{
  "id": 36,
  "nombre": "Escenario A - evidencias",
  "candidato_id": 275,
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
  "creado_en": "2026-11-26T23:20:30-06:00"
}
```

### PLA-10 · Abrir escenario (XML) · PASA

**Objetivo.** Escenario con supuestos y resultados.

**Petición.** `GET http://planeacion:5106/api/v1/escenarios/36`

```http
Accept: application/xml
X-Traza-Id: f1752962-18ff-4c8e-8c6d-71e33f984e4b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 35 ms · traza `f1752962-18ff-4c8e-8c6d-71e33f984e4b`

```xml
<?xml version='1.0' encoding='utf-8'?>
<escenario xmlns="urn:microhubs:v1" version="1"><id>36</id><nombre>Escenario A - evidencias</nombre><candidato_id>275</candidato_id><supuestos><demanda_diaria>120</demanda_diaria><operadores>3</operadores><repartidores>4</repartidores><ticket>135.00</ticket><costo_entrega>22.00</costo_entrega><margen_bruto>0.28</margen_bruto><renta>18000.00</renta><nomina>42000.00</nomina><servicios>7000.00</servicios><otros>5000.00</otros><distancia_km>2.4</distancia_km><capacidad_fisica>150</capacidad_fisica></supuestos><resultados><atendidos>120</atendidos><rechazados>0</rechazados><utilizacion>80</utilizacion><nivel>atencion</nivel><tiempo_estimado_min>19.4</tiempo_estimado_min><operadores_requeridos>3</operadores_requeridos><repartidores_requeridos>2</repartidores_requeridos><ingreso_dia>16200.00</ingreso_dia><margen_dia>-504.00</margen_dia><costo_por_pedido>42.00</costo_por_pedido><equilibrio><margen_pedido>15.80</margen_pedido><mensual>4557</mensual><diario>151.9</diario></equilibrio><decision>NO VIABLE CON LOS SUPUESTOS ACTUALES</decision><explicacion><motivo>la demanda atendida (120/día) no alcanza el equilibrio (152/día)</motivo><motivo>el espacio físico del local limita la capacidad</motivo><motivo>reducir costos fijos, aumentar ticket o buscar una ubicación con más demanda</motivo></explicacion></resultados><creado_en>2026-11-26T23:20:30-06:00</creado_en></escenario>
```

### PLA-11 · Resumen de simulaciones · PASA

**Objetivo.** Agregación $group en MongoDB por decisión.

**Petición.** `GET http://planeacion:5106/api/v1/simulaciones/resumen`

```http
Accept: application/json
X-Traza-Id: 9445b29b-e40d-4503-b7af-9e93e25d4492
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 23 ms · traza `9445b29b-e40d-4503-b7af-9e93e25d4492`

```json
{
  "total": 99,
  "por_decision": [
    {
      "decision": "NO VIABLE CON LOS SUPUESTOS ACTUALES",
      "cantidad": 97,
      "utilizacion_promedio": 54.5
    },
    {
      "decision": "VIABLE",
      "cantidad": 2,
      "utilizacion_promedio": 83.3
    }
  ]
}
```

**Evidencia en MongoDB.** `db.ejecuciones_analiticas.aggregate([{$match:{tipo_analisis:'punto_equilibrio'}}, {$group:{_id:'$resultados.decision', cantidad:{$sum:1}, utilizacion_promedio:{$avg:'$resultados.utilizacion'}}}])`

```json
[
  {
    "_id": "NO VIABLE CON LOS SUPUESTOS ACTUALES",
    "cantidad": 97,
    "utilizacion_promedio": 54.46907216494845
  },
  {
    "_id": "VIABLE",
    "cantidad": 2,
    "utilizacion_promedio": 83.3
  }
]
```

### PLA-12 · Auditor intenta registrar · PASA

**Objetivo.** El auditor solo consulta (RN-E01).

**Petición.** `POST http://planeacion:5106/api/v1/candidatos`

```http
Accept: application/json
X-Traza-Id: 27ad9e54-ec16-4e5a-be03-84aea1282683
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

**Respuesta.** HTTP 403 (esperado 403) · 33 ms · traza `27ad9e54-ec16-4e5a-be03-84aea1282683`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "27ad9e54-ec16-4e5a-be03-84aea1282683"
  }
}
```

### PLA-13 · Auditor intenta simular · PASA

**Objetivo.** Sin simulacion.ejecutar.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/275/simular`

```http
Accept: application/json
X-Traza-Id: 257d430a-5248-4589-8b5a-cd825c5f478f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 403 (esperado 403) · 29 ms · traza `257d430a-5248-4589-8b5a-cd825c5f478f`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "257d430a-5248-4589-8b5a-cd825c5f478f"
  }
}
```

### PLA-14 · Eliminar escenario (DELETE) · PASA

**Objetivo.** Borrar un escenario.

**Petición.** `DELETE http://planeacion:5106/api/v1/escenarios/36`

```http
Accept: application/json
X-Traza-Id: 2a4fdec4-fd61-476d-b035-36cc23139a47
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 41 ms · traza `2a4fdec4-fd61-476d-b035-36cc23139a47`

```json
(sin cuerpo)
```

### PLA-15 · Dar de baja candidato (DELETE) · PASA

**Objetivo.** Baja lógica: se conserva su historia.

**Petición.** `DELETE http://planeacion:5106/api/v1/candidatos/275`

```http
Accept: application/json
X-Traza-Id: 1c4aeb4a-5fc3-4508-9547-0fd8aed1df9a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 61 ms · traza `1c4aeb4a-5fc3-4508-9547-0fd8aed1df9a`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT id, clave, estatus, decision FROM ubicacion_candidata WHERE id = %s`

```json
[
  {
    "id": 275,
    "clave": "EV-952D8C",
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
X-Traza-Id: 4c297b7f-c9c1-4a9a-89d9-322e803df106
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 30 ms · traza `4c297b7f-c9c1-4a9a-89d9-322e803df106`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el candidato.",
    "traza_id": "4c297b7f-c9c1-4a9a-89d9-322e803df106"
  }
}
```

## Servicio inventario · puerto 5111

### INV-01 · Existencias por microhub · PASA

**Objetivo.** Existencia física, reservada y disponible de cada producto.

**Petición.** `GET http://inventario:5111/api/v1/inventario?por_pagina=5`

```http
Accept: application/json
X-Traza-Id: e1f5e8a7-3aad-47f2-a1ae-ed23d017f1c3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 279 ms · traza `e1f5e8a7-3aad-47f2-a1ae-ed23d017f1c3`

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
      "existencia": 24,
      "minimo": 5,
      "reservado": 0,
      "disponible": 24,
      "estado": "normal",
      "actualizado_en": "2026-11-26T23:17:16-06:00"
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
      "actualizado_en": "2026-11-26T23:12:48-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 159,
    "paginas": 32
  }
}
```

**Explicación.** Lee la vista v_inventario_disponible (existencia − reservas activas y vigentes). Los nombres de producto y microhub los pide a los servicios de productos y microhubs, no los lee de sus tablas.

**Evidencia en PostgreSQL.** `SELECT count(*) AS filas, sum(existencia) AS unidades, sum(reservado) AS reservado FROM v_inventario_disponible`

```json
[
  {
    "filas": 159,
    "unidades": 7995,
    "reservado": 0
  }
]
```

### INV-02 · Existencias (XML) · PASA

**Objetivo.** La app de escritorio recibe XML que cumple inventario.xsd.

**Petición.** `GET http://inventario:5111/api/v1/inventario?por_pagina=3`

```http
Accept: application/xml
X-Traza-Id: d7ba97ef-c7d5-45a2-a199-573f48f8e070
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 60 ms · traza `d7ba97ef-c7d5-45a2-a199-573f48f8e070`

```xml
<?xml version='1.0' encoding='utf-8'?>
<existencias xmlns="urn:microhubs:v1" version="1"><datos><existencia><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><producto><id>1</id><clave_interna>AB-001</clave_interna><nombre>Frijol negro a granel</nombre></producto><existencia>58</existencia><minimo>10</minimo><reservado>0</reservado><disponible>58</disponible><estado>normal</estado><actualizado_en>2026-11-25T15:47:14-06:00</actualizado_en></existencia><existencia><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><producto><id>2</id><clave_interna>AB-002</clave_interna><nombre>Arroz superextra</nombre></producto><existencia>36</existencia><minimo>10</minimo><reservado>0</reservado><disponible>36</disponible><estado>normal</estado><actualizado_en>2026-11-26T14:26:53-06:00</actualizado_en></existencia><existencia><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><producto><id>3</id><clave_interna>AB-003</clave_interna><nombre>Aceite vegetal</nombre></producto><existencia>24</existencia><minimo>5</minimo><reservado>0</reservado><disponible>24</disponible><estado>normal</estado><actualizado_en>2026-11-26T23:17:16-06:00</actualizado_en></existencia></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>159</total><paginas>53</paginas></paginacion></existencias>
```

### INV-03 · Filtro de estado inválido · PASA

**Objetivo.** Un filtro desconocido se rechaza.

**Petición.** `GET http://inventario:5111/api/v1/inventario?estado=inventado`

```http
Accept: application/json
X-Traza-Id: f69a8560-a889-48db-bda5-2be55f0b4465
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 6 ms · traza `f69a8560-a889-48db-bda5-2be55f0b4465`

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
    "traza_id": "f69a8560-a889-48db-bda5-2be55f0b4465"
  }
}
```

### INV-04 · El operador ve solo su microhub · PASA

**Objetivo.** Ámbito por microhub del perfil operador.

**Petición.** `GET http://inventario:5111/api/v1/inventario?por_pagina=100`

```http
Accept: application/json
X-Traza-Id: 37b398aa-0e7b-4ef6-b68c-93404f1d9683
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 54 ms · traza `37b398aa-0e7b-4ef6-b68c-93404f1d9683`

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
      "existencia": 24,
      "minimo": 5,
      "reservado": 0,
      "disponible": 24,
      "estado": "normal",
      "actualizado_en": "2026-11-26T23:17:16-06:00"
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
      "actualizado_en": "2026-11-26T23:12:48-06:00"
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
      "existencia": 88,
      "minimo": 10,
      "reservado": 0,
      "disponible": 88,
      "estado": "normal",
      "actualizado_en": "2026-11-26T23:19:41-06:00"
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
      "actualizado_en": "2026-11-26T23:19:41-06:00"
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
      "existencia": 16,
      "minimo": 10,
      "reservado": 0,
      "disponible": 16,
      "estado": "normal",
      "actualizado_en": "2026-11-26T23:17:17-06:00"
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
      "actualizado_en": "2026-11-26T23:19:41-06:00"
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
      "existencia": 920,
      "minimo": 10,
      "reservado": 0,
      "disponible": 920,
      "estado": "normal",
      "actualizado_en": "2026-11-26T23:19:23-06:00"
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
      "existencia": 25,
      "minimo": 10,
      "reservado": 0,
      "disponible": 25,
      "estado": "normal",
      "actualizado_en": "2026-11-26T23:17:17-06:00"
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
      "existencia": 515,
      "minimo": 8,
      "reservado": 0,
      "disponible": 515,
      "estado": "normal",
      "actualizado_en": "2026-11-26T23:10:55-06:00"
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
      "actualizado_en": "2026-11-26T23:09:37-06:00"
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
      "actualizado_en": "2026-11-26T23:19:21-06:00"
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
      "existencia": 75,
      "minimo": 8,
      "reservado": 0,
      "disponible": 75,
      "estado": "normal",
      "actualizado_en": "2026-11-26T23:19:03-06:00"
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
      "actualizado_en": "2026-11-26T23:19:41-06:00"
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
      "actualizado_en": "2026-11-26T23:19:41-06:00"
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
      "existencia": 30,
      "minimo": 10,
      "reservado": 0,
      "disponible": 30,
      "estado": "normal",
      "actualizado_en": "2026-11-26T23:19:10-06:00"
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
      "existencia": 66,
      "minimo": 8,
      "reservado": 0,
      "disponible": 66,
      "estado": "normal",
      "actualizado_en": "2026-11-26T23:17:17-06:00"
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
      "actualizado_en": "2026-11-26T15:23:37-06:00"
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
      "actualizado_en": "2026-11-26T23:20:05-06:00"
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
      "existencia": 78,
      "minimo": 5,
      "reservado": 0,
      "disponible": 78,
      "estado": "normal",
      "actualizado_en": "2026-11-26T23:17:17-06:00"
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
      "existencia": 15,
      "minimo": 10,
      "reservado": 0,
      "disponible": 15,
      "estado": "normal",
      "actualizado_en": "2026-11-26T23:12:32-06:00"
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
      "actualizado_en": "2026-11-26T23:20:05-06:00"
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
      "existencia": 45,
      "minimo": 10,
      "reservado": 0,
      "disponible": 45,
      "estado": "normal",
      "actualizado_en": "2026-11-26T23:17:17-06:00"
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
      "actualizado_en": "2026-11-26T15:23:37-06:00"
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
      "existencia": 217,
      "minimo": 5,
      "reservado": 0,
      "disponible": 217,
      "estado": "normal",
      "actualizado_en": "2026-11-26T23:11:46-06:00"
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
      "existencia": 78,
      "minimo": 5,
      "reservado": 0,
      "disponible": 78,
      "estado": "normal",
      "actualizado_en": "2026-11-26T23:09:37-06:00"
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
      "actualizado_en": "2026-11-26T23:07:45-06:00"
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
      "existencia": 30,
      "minimo": 8,
      "reservado": 0,
      "disponible": 30,
      "estado": "normal",
      "actualizado_en": "2026-11-26T23:19:41-06:00"
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
      "existencia": 12,
      "minimo": 5,
      "reservado": 0,
      "disponible": 12,
      "estado": "normal",
      "actualizado_en": "2026-11-26T21:41:13-06:00"
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
      "existencia": 45,
      "minimo": 5,
      "reservado": 0,
      "disponible": 45,
      "estado": "normal",
      "actualizado_en": "2026-11-26T23:19:41-06:00"
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
      "existencia": 12,
      "minimo": 8,
      "reservado": 0,
      "disponible": 12,
      "estado": "normal",
      "actualizado_en": "2026-11-26T21:45:24-06:00"
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
      "actualizado_en": "2026-11-26T23:19:41-06:00"
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
      "actualizado_en": "2026-11-26T23:09:37-06:00"
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
      "actualizado_en": "2026-11-26T23:20:05-06:00"
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
      "actualizado_en": "2026-11-26T23:12:32-06:00"
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
      "actualizado_en": "2026-11-26T15:23:37-06:00"
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
      "actualizado_en": "2026-11-26T23:10:51-06:00"
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
X-Traza-Id: 12d124f1-4cab-4ba7-9b37-9afd16e75734
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 5 ms · traza `12d124f1-4cab-4ba7-9b37-9afd16e75734`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "12d124f1-4cab-4ba7-9b37-9afd16e75734"
  }
}
```

### INV-06 · Una existencia · PASA

**Objetivo.** Existencia, apartado y disponible de un producto en un microhub.

**Petición.** `GET http://inventario:5111/api/v1/inventario/1/6`

```http
Accept: application/json
X-Traza-Id: 0077b359-eb49-4e5f-b8cd-b4a3f0bb9b59
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 29 ms · traza `0077b359-eb49-4e5f-b8cd-b4a3f0bb9b59`

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
  "existencia": 88,
  "minimo": 10,
  "reservado": 0,
  "disponible": 88,
  "estado": "normal",
  "actualizado_en": "2026-11-26T23:19:41-06:00"
}
```

### INV-07 · Recibir mercancía · PASA

**Objetivo.** Suma al inventario y deja el movimiento con la referencia.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: 67f9ca2d-a8eb-4091-9bd7-8dc24379877c
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
  "operacion_uuid": "be51324a-3bdd-4689-9923-aac030644589",
  "referencia": {
    "tipo": "orden_compra",
    "id": "1"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 90 ms · traza `67f9ca2d-a8eb-4091-9bd7-8dc24379877c`

```json
{
  "movimiento": {
    "id": 2736,
    "microhub_id": 1,
    "producto_id": 6,
    "tipo": "recepcion",
    "cantidad": 5,
    "existencia_resultante": 93,
    "referencia": {
      "tipo": "orden_compra",
      "id": "1"
    },
    "motivo": "Llegada de mercancía",
    "usuario_id": 2,
    "fecha": "2026-11-26T23:20:33-06:00"
  },
  "duplicado": false
}
```

**Explicación.** Bloquea la fila del inventario, suma, y guarda el movimiento con la existencia resultante. La operacion_uuid hace el movimiento idempotente.

**Evidencia en PostgreSQL.** `SELECT id, tipo, cantidad, existencia_resultante, referencia_tipo, referencia_id, operacion_uuid FROM movimiento_inventario WHERE operacion_uuid = %s`

```json
[
  {
    "id": 2736,
    "tipo": "recepcion",
    "cantidad": 5,
    "existencia_resultante": 93,
    "referencia_tipo": "orden_compra",
    "referencia_id": 1,
    "operacion_uuid": "be51324a-3bdd-4689-9923-aac030644589"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT existencia FROM inventario WHERE microhub_id = %s AND producto_id = %s`

```json
[
  {
    "existencia": 93
  }
]
```

### INV-08 · Reintento con la misma operación · PASA

**Objetivo.** Idempotencia: la misma entrada no se aplica dos veces.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: 1c8ec39d-b67d-444c-8f43-9e08cb0bb1be
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
  "operacion_uuid": "be51324a-3bdd-4689-9923-aac030644589",
  "referencia": {
    "tipo": "orden_compra",
    "id": "1"
  }
}
```

**Respuesta.** HTTP 200 (esperado 200) · 27 ms · traza `1c8ec39d-b67d-444c-8f43-9e08cb0bb1be`

```json
{
  "movimiento": {
    "id": 2736,
    "microhub_id": 1,
    "producto_id": 6,
    "tipo": "recepcion",
    "cantidad": 5,
    "existencia_resultante": 93,
    "referencia": {
      "tipo": "orden_compra",
      "id": "1"
    },
    "motivo": "Llegada de mercancía",
    "usuario_id": 2,
    "fecha": "2026-11-26T23:20:33-06:00"
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
    "existencia": 93
  }
]
```

### INV-09 · Ajuste sin motivo · PASA

**Objetivo.** Un ajuste, merma o conteo necesita el motivo.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: 702ef86b-06e0-4ad7-a7d7-7d3f26756549
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

**Respuesta.** HTTP 422 (esperado 422) · 12 ms · traza `702ef86b-06e0-4ad7-a7d7-7d3f26756549`

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
    "traza_id": "702ef86b-06e0-4ad7-a7d7-7d3f26756549"
  }
}
```

### INV-10 · Ajuste grande por un operador · PASA

**Objetivo.** Más de 25 unidades lo autoriza un administrador.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: b9b89b25-84ee-49ae-9dbe-0347e245b1e5
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

**Respuesta.** HTTP 403 (esperado 403) · 45 ms · traza `b9b89b25-84ee-49ae-9dbe-0347e245b1e5`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Un movimiento de más de 25 unidades lo autoriza un administrador.",
    "traza_id": "b9b89b25-84ee-49ae-9dbe-0347e245b1e5"
  }
}
```

**Explicación.** El umbral viene de configuracion.umbral_ajuste_inventario, no de una constante en el código.

### INV-11 · Ajuste grande por un administrador · PASA

**Objetivo.** El administrador sí puede.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: d5044d0a-a21a-4d58-b79f-f78e67cfd1f2
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

**Respuesta.** HTTP 201 (esperado 201) · 69 ms · traza `d5044d0a-a21a-4d58-b79f-f78e67cfd1f2`

```json
{
  "movimiento": {
    "id": 2737,
    "microhub_id": 1,
    "producto_id": 6,
    "tipo": "ajuste",
    "cantidad": 30,
    "existencia_resultante": 123,
    "referencia": null,
    "motivo": "Ajuste grande de prueba",
    "usuario_id": 1,
    "fecha": "2026-11-26T23:20:33-06:00"
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
    "existencia_resultante": 123,
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
X-Traza-Id: 2e3d7274-7b92-4635-84f8-bc22188623a3
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
  "operacion_uuid": "b5deef75-1f14-47a5-b219-55aea5ee7058"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 88 ms · traza `2e3d7274-7b92-4635-84f8-bc22188623a3`

```json
{
  "producto_id": 7,
  "cantidad": 2,
  "duplicado": false,
  "origen": {
    "microhub_id": 1,
    "existencia": 12,
    "movimiento_id": 2740
  },
  "destino": {
    "microhub_id": 2,
    "existencia": 76,
    "movimiento_id": 2741
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
    "existencia_resultante": 76,
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
X-Traza-Id: 33b87d71-3b47-4937-810f-747b2773b337
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
  "operacion_uuid": "5cf51173-6862-4946-9397-52add9b701ae"
}
```

**Respuesta.** HTTP 409 (esperado 409) · 76 ms · traza `33b87d71-3b47-4937-810f-747b2773b337`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "En el microhub de origen hay 12 disponibles y se piden 1014.",
    "traza_id": "33b87d71-3b47-4937-810f-747b2773b337"
  }
}
```

### INV-14 · Apartar existencia · PASA

**Objetivo.** Una reserva resta de lo disponible sin tocar la existencia física.

**Petición.** `POST http://inventario:5111/api/v1/inventario/reservas`

```http
Accept: application/json
X-Traza-Id: 26bc65fd-1c26-4a87-a23a-5b060c864717
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
    "id": "evidencia-c68623"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 60 ms · traza `26bc65fd-1c26-4a87-a23a-5b060c864717`

```json
{
  "id": 26,
  "microhub_id": 1,
  "producto_id": 8,
  "cantidad": 3,
  "estado": "activa",
  "vigente": true,
  "referencia": {
    "tipo": "manual",
    "id": "evidencia-c68623"
  },
  "creada_en": "2026-11-26T23:20:33-06:00",
  "vence_en": "2026-11-26T23:50:33-06:00",
  "cerrada_en": null
}
```

**Evidencia en PostgreSQL.** `SELECT existencia, reservado, disponible FROM v_inventario_disponible WHERE microhub_id = %s AND producto_id = %s`

```json
[
  {
    "existencia": 16,
    "reservado": 3,
    "disponible": 13
  }
]
```

### INV-15 · Reservar más de lo disponible · PASA

**Objetivo.** Responde 409 si no alcanza.

**Petición.** `POST http://inventario:5111/api/v1/inventario/reservas`

```http
Accept: application/json
X-Traza-Id: b8f81177-1585-4cd2-bbad-11711dbfa134
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "producto_id": 8,
  "cantidad": 116,
  "referencia": {
    "tipo": "manual",
    "id": "evidencia-c68623"
  }
}
```

**Respuesta.** HTTP 409 (esperado 409) · 48 ms · traza `b8f81177-1585-4cd2-bbad-11711dbfa134`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "No hay existencia disponible: hay 13 sin apartar y se piden 116.",
    "traza_id": "b8f81177-1585-4cd2-bbad-11711dbfa134"
  }
}
```

### INV-16 · Reservas activas · PASA

**Objetivo.** Filtro por producto, estado y referencia.

**Petición.** `GET http://inventario:5111/api/v1/inventario/reservas?producto_id=8&estado=activa&referencia_id=evidencia-c68623`

```http
Accept: application/json
X-Traza-Id: e5a3e8ba-0e17-4fda-9e98-18ecf16d5e5a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 47 ms · traza `e5a3e8ba-0e17-4fda-9e98-18ecf16d5e5a`

```json
{
  "datos": [
    {
      "id": 26,
      "microhub_id": 1,
      "producto_id": 8,
      "cantidad": 3,
      "estado": "activa",
      "vigente": true,
      "referencia": {
        "tipo": "manual",
        "id": "evidencia-c68623"
      },
      "creada_en": "2026-11-26T23:20:33-06:00",
      "vence_en": "2026-11-26T23:50:33-06:00",
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

**Petición.** `POST http://inventario:5111/api/v1/inventario/reservas/26/liberar`

```http
Accept: application/json
X-Traza-Id: d34057f1-11c1-4778-bbe8-3e3a5b2593ed
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 35 ms · traza `d34057f1-11c1-4778-bbe8-3e3a5b2593ed`

```json
{
  "id": 26,
  "microhub_id": 1,
  "producto_id": 8,
  "cantidad": 3,
  "estado": "liberada",
  "vigente": false,
  "referencia": {
    "tipo": "manual",
    "id": "evidencia-c68623"
  },
  "creada_en": "2026-11-26T23:20:33-06:00",
  "vence_en": "2026-11-26T23:50:33-06:00",
  "cerrada_en": "2026-11-26T23:20:34-06:00"
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
    "existencia": 16,
    "reservado": 0,
    "disponible": 16
  }
]
```

### INV-18 · Cambiar el mínimo · PASA

**Objetivo.** Solo un administrador cambia el mínimo de un producto.

**Petición.** `PATCH http://inventario:5111/api/v1/inventario/1/9/minimo`

```http
Accept: application/json
X-Traza-Id: 203cdd94-1de9-472a-9c4e-1044fadcbd91
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "minimo": 41
}
```

**Respuesta.** HTTP 200 (esperado 200) · 57 ms · traza `203cdd94-1de9-472a-9c4e-1044fadcbd91`

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
  "actualizado_en": "2026-11-26T23:20:34-06:00"
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
X-Traza-Id: 779a03a0-1ec8-42f9-ae87-22594124d619
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "minimo": 41
}
```

**Respuesta.** HTTP 200 (esperado 200) · 59 ms · traza `779a03a0-1ec8-42f9-ae87-22594124d619`

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
  "actualizado_en": "2026-11-26T23:20:34-06:00"
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
      "actualizado_en": "2026-11-26T23:20:34.221715-06:00"
    }
  }
]
```

### INV-19 · El operador intenta cambiar el mínimo · PASA

**Objetivo.** Sin inventario.ajuste.

**Petición.** `PATCH http://inventario:5111/api/v1/inventario/1/9/minimo`

```http
Accept: application/json
X-Traza-Id: 629dc5cf-0e86-4299-b5e3-afe2297e4e3e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "minimo": 1
}
```

**Respuesta.** HTTP 403 (esperado 403) · 27 ms · traza `629dc5cf-0e86-4299-b5e3-afe2297e4e3e`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "629dc5cf-0e86-4299-b5e3-afe2297e4e3e"
  }
}
```

### INV-20 · Una merma cruza el mínimo · PASA

**Objetivo.** El trigger avisa del faltante al operador y al administrador.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: 19222970-d2ce-4cad-8baa-e8b31e6913e9
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

**Respuesta.** HTTP 201 (esperado 201) · 71 ms · traza `19222970-d2ce-4cad-8baa-e8b31e6913e9`

```json
{
  "movimiento": {
    "id": 2744,
    "microhub_id": 1,
    "producto_id": 9,
    "tipo": "merma",
    "cantidad": -2,
    "existencia_resultante": 40,
    "referencia": null,
    "motivo": "Se rompieron dos",
    "usuario_id": 1,
    "fecha": "2026-11-26T23:20:34-06:00"
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
X-Traza-Id: bb9beac9-b30a-4f1a-929b-99ca7b5c2fe9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 75 ms · traza `bb9beac9-b30a-4f1a-929b-99ca7b5c2fe9`

```json
{
  "datos": [
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
    "total": 1,
    "paginas": 1
  }
}
```

### INV-22 · Movimientos de un producto · PASA

**Objetivo.** Bitácora del producto con sus referencias.

**Petición.** `GET http://inventario:5111/api/v1/inventario/movimientos?microhub_id=1&producto_id=6&tipo=recepcion`

```http
Accept: application/json
X-Traza-Id: 0ac54377-1977-484a-981c-f55fbc9ed9f9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 55 ms · traza `0ac54377-1977-484a-981c-f55fbc9ed9f9`

```json
{
  "datos": [
    {
      "id": 2736,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 5,
      "existencia_resultante": 93,
      "referencia": {
        "tipo": "orden_compra",
        "id": "1"
      },
      "motivo": "Llegada de mercancía",
      "usuario_id": 2,
      "fecha": "2026-11-26T23:20:33-06:00"
    },
    {
      "id": 2665,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 5,
      "existencia_resultante": 93,
      "referencia": {
        "tipo": "orden_compra",
        "id": "1"
      },
      "motivo": "Llegada de mercancía",
      "usuario_id": 2,
      "fecha": "2026-11-26T23:19:14-06:00"
    },
    {
      "id": 2621,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 5,
      "existencia_resultante": 96,
      "referencia": {
        "tipo": "orden_compra",
        "id": "1"
      },
      "motivo": "Llegada de mercancía",
      "usuario_id": 2,
      "fecha": "2026-11-26T23:12:05-06:00"
    },
    {
      "id": 2498,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 5,
      "existencia_resultante": 91,
      "referencia": {
        "tipo": "orden_compra",
        "id": "1"
      },
      "motivo": "Prueba de recepción",
      "usuario_id": 2,
      "fecha": "2026-11-26T23:06:53-06:00"
    },
    {
      "id": 2496,
      "microhub_id": 1,
      "producto_id": 6,
      "tipo": "recepcion",
      "cantidad": 3,
      "existencia_resultante": 89,
      "referencia": null,
      "motivo": "Prueba XML",
      "usuario_id": 2,
      "fecha": "2026-11-26T23:06:53-06:00"
    },
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
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 28,
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
X-Traza-Id: 56adaf4a-1fa3-4afc-a1cf-0a25d07b2e9f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "rol": "operador",
  "microhub_id": 1,
  "tipo": "sistema",
  "titulo": "Evidencia ddd8ca",
  "mensaje": "Aviso de prueba para el microhub 1",
  "referencia": {
    "tipo": "sistema",
    "id": "evidencia"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 46 ms · traza `56adaf4a-1fa3-4afc-a1cf-0a25d07b2e9f`

```json
{
  "enviadas": 1,
  "omitidas": 0,
  "ids": [
    1101
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
    "titulo": "Evidencia ddd8ca",
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
X-Traza-Id: 41b1d14c-974f-4daa-930c-39dbbc909f64
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

**Respuesta.** HTTP 403 (esperado 403) · 35 ms · traza `41b1d14c-974f-4daa-930c-39dbbc909f64`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "41b1d14c-974f-4daa-930c-39dbbc909f64"
  }
}
```

### NOT-03 · Destino inexistente · PASA

**Objetivo.** Un rol sin personas activas se rechaza.

**Petición.** `POST http://notificaciones:5124/api/v1/notificaciones`

```http
Accept: application/json
X-Traza-Id: 1f138de1-b0e0-43ce-b90f-006d489751fc
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

**Respuesta.** HTTP 422 (esperado 422) · 64 ms · traza `1f138de1-b0e0-43ce-b90f-006d489751fc`

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
    "traza_id": "1f138de1-b0e0-43ce-b90f-006d489751fc"
  }
}
```

### NOT-04 · Mi bandeja · PASA

**Objetivo.** Los avisos de la persona, el más reciente primero.

**Petición.** `GET http://notificaciones:5124/api/v1/notificaciones?solo_no_leidas=true&por_pagina=20`

```http
Accept: application/json
X-Traza-Id: 26f9d08e-731b-473b-9652-c1f6a130a831
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 45 ms · traza `26f9d08e-731b-473b-9652-c1f6a130a831`

```json
{
  "datos": [
    {
      "id": 1101,
      "tipo": "sistema",
      "titulo": "Evidencia ddd8ca",
      "mensaje": "Aviso de prueba para el microhub 1",
      "leida": false,
      "referencia": {
        "tipo": "sistema",
        "id": "evidencia"
      },
      "creada_en": "2026-11-26T23:20:34-06:00"
    },
    {
      "id": 1099,
      "tipo": "inventario",
      "titulo": "Faltante en Microhub San Bernabé Centro",
      "mensaje": "Atún en agua: quedan 40 (mínimo 41).",
      "leida": false,
      "referencia": {
        "tipo": "producto",
        "id": "9"
      },
      "creada_en": "2026-11-26T23:20:34-06:00"
    },
    {
      "id": 1073,
      "tipo": "abastecimiento",
      "titulo": "Orden de compra OC-20261126-000050",
      "mensaje": "La orden quedó cancelada.",
      "leida": false,
      "referencia": {
        "tipo": "orden",
        "id": "50"
      },
      "creada_en": "2026-11-26T23:19:24-06:00"
    },
    {
      "id": 1072,
      "tipo": "abastecimiento",
      "titulo": "Solicitud de compra SC-20261126-000079",
      "mensaje": "Tu solicitud fue aprobada.",
      "leida": false,
      "referencia": {
        "tipo": "solicitud",
        "id": "79"
      },
      "creada_en": "2026-11-26T23:19:23-06:00"
    },
    {
      "id": 1069,
      "tipo": "abastecimiento",
      "titulo": "Orden de compra OC-20261126-000049",
      "mensaje": "La orden quedó recibida.",
      "leida": false,
      "referencia": {
        "tipo": "orden",
        "id": "49"
      },
      "creada_en": "2026-11-26T23:19:23-06:00"
    },
    {
      "id": 1068,
      "tipo": "abastecimiento",
      "titulo": "Solicitud de compra SC-20261126-000078",
      "mensaje": "Tu solicitud fue aprobada.",
      "leida": false,
      "referencia": {
        "tipo": "solicitud",
        "id": "78"
      },
      "creada_en": "2026-11-26T23:19:21-06:00"
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
X-Traza-Id: b4e9ac94-3890-4a69-a3e4-5a75c9db8c13
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 56 ms · traza `b4e9ac94-3890-4a69-a3e4-5a75c9db8c13`

```xml
<?xml version='1.0' encoding='utf-8'?>
<notificaciones xmlns="urn:microhubs:v1" version="1"><datos><notificacion><id>1101</id><tipo>sistema</tipo><titulo>Evidencia ddd8ca</titulo><mensaje>Aviso de prueba para el microhub 1</mensaje><leida>false</leida><referencia><tipo>sistema</tipo><id>evidencia</id></referencia><creada_en>2026-11-26T23:20:34-06:00</creada_en></notificacion><notificacion><id>1099</id><tipo>inventario</tipo><titulo>Faltante en Microhub San Bernabé Centro</titulo><mensaje>Atún en agua: quedan 40 (mínimo 41).</mensaje><leida>false</leida><referencia><tipo>producto</tipo><id>9</id></referencia><creada_en>2026-11-26T23:20:34-06:00</creada_en></notificacion><notificacion><id>1073</id><tipo>abastecimiento</tipo><titulo>Orden de compra OC-20261126-000050</titulo><mensaje>La orden quedó cancelada.</mensaje><leida>false</leida><referencia><tipo>orden</tipo><id>50</id></referencia><creada_en>2026-11-26T23:19:24-06:00</creada_en></notificacion></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>179</total><paginas>60</paginas></paginacion></notificaciones>
```

### NOT-06 · Avisos sin leer · PASA

**Objetivo.** Conteo para la insignia de la app.

**Petición.** `GET http://notificaciones:5124/api/v1/notificaciones/conteo`

```http
Accept: application/json
X-Traza-Id: 9fb957b0-29f6-41bd-b1e3-3837ac515fcb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 28 ms · traza `9fb957b0-29f6-41bd-b1e3-3837ac515fcb`

```json
{
  "no_leidas": 6
}
```

### NOT-07 · Confirmar la lectura · PASA

**Objetivo.** El aviso queda leído.

**Petición.** `POST http://notificaciones:5124/api/v1/notificaciones/1101/leer`

```http
Accept: application/json
X-Traza-Id: d95df5f7-497e-40c8-9545-617dbf367a30
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 31 ms · traza `d95df5f7-497e-40c8-9545-617dbf367a30`

```json
{
  "id": 1101,
  "tipo": "sistema",
  "titulo": "Evidencia ddd8ca",
  "mensaje": "Aviso de prueba para el microhub 1",
  "leida": true,
  "referencia": {
    "tipo": "sistema",
    "id": "evidencia"
  },
  "creada_en": "2026-11-26T23:20:34-06:00"
}
```

**Evidencia en PostgreSQL.** `SELECT id, leido_en IS NOT NULL AS leido FROM web_notificacion WHERE id = %s`

```json
[
  {
    "id": 1101,
    "leido": true
  }
]
```

### NOT-08 · Leído por otra persona · PASA

**Objetivo.** Un aviso ajeno no se puede marcar.

**Petición.** `POST http://notificaciones:5124/api/v1/notificaciones/1101/leer`

```http
Accept: application/json
X-Traza-Id: c548e367-7494-4622-8fa2-98e31752cfd7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 24 ms · traza `c548e367-7494-4622-8fa2-98e31752cfd7`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe ese aviso en tu bandeja.",
    "traza_id": "c548e367-7494-4622-8fa2-98e31752cfd7"
  }
}
```

### NOT-09 · Marcar todos como leídos · PASA

**Objetivo.** Confirma la lectura de todos los pendientes.

**Petición.** `POST http://notificaciones:5124/api/v1/notificaciones/leer-todas`

```http
Accept: application/json
X-Traza-Id: a7570c2c-6069-48ad-9eb5-e2a8eb059f5e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 31 ms · traza `a7570c2c-6069-48ad-9eb5-e2a8eb059f5e`

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
X-Traza-Id: 614b2ab9-b57f-44b9-86a6-d33ab00fb818
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 24 ms · traza `614b2ab9-b57f-44b9-86a6-d33ab00fb818`

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
X-Traza-Id: 555e39c1-d21a-47ff-aaff-aa965d654b62
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "activa": false
}
```

**Respuesta.** HTTP 200 (esperado 200) · 39 ms · traza `555e39c1-d21a-47ff-aaff-aa965d654b62`

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
X-Traza-Id: 2353c7b3-e1ce-4811-bc54-8ee959dca758
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "rol": "operador",
  "microhub_id": 1,
  "tipo": "inventario",
  "titulo": "Evidencia ddd8ca",
  "mensaje": "Faltante de prueba"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 34 ms · traza `2353c7b3-e1ce-4811-bc54-8ee959dca758`

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
X-Traza-Id: d828fb5a-05e1-4be1-a2c2-c49cf71e0767
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "activa": false
}
```

**Respuesta.** HTTP 409 (esperado 409) · 6 ms · traza `d828fb5a-05e1-4be1-a2c2-c49cf71e0767`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Los avisos del sistema no se pueden apagar.",
    "traza_id": "d828fb5a-05e1-4be1-a2c2-c49cf71e0767"
  }
}
```

### NOT-14 · Borrar un aviso · PASA

**Objetivo.** Quita el aviso de la bandeja propia.

**Petición.** `DELETE http://notificaciones:5124/api/v1/notificaciones/1101`

```http
Accept: application/json
X-Traza-Id: 957fc3b0-c351-4f4d-8e6c-79c33a3a7023
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 26 ms · traza `957fc3b0-c351-4f4d-8e6c-79c33a3a7023`

```json
(sin cuerpo)
```

## Servicio proveedores · puerto 5113

### PRV-01 · Proveedores · PASA

**Objetivo.** Lista con cobertura y calificación.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores?por_pagina=10`

```http
Accept: application/json
X-Traza-Id: 091b95f7-052a-43fe-b300-b75ec60543db
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 56 ms · traza `091b95f7-052a-43fe-b300-b75ec60543db`

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
        4,
        11,
        14
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
        4,
        11,
        14
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
        4,
        11,
        14
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
X-Traza-Id: c704dc38-ec45-4aff-a6b1-0f06573aed8c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 68 ms · traza `c704dc38-ec45-4aff-a6b1-0f06573aed8c`

```xml
<?xml version='1.0' encoding='utf-8'?>
<proveedores xmlns="urn:microhubs:v1" version="1"><datos><proveedor><id>1</id><clave>PV-01</clave><nombre>Abarrotes del Norte</nombre><contacto>Rosa Garza</contacto><correo>ventas@abarrotesdelnorte.example</correo><telefono>8181000101</telefono><dias_entrega>2</dias_entrega><pedido_minimo>800.00</pedido_minimo><condiciones_pago>Contado</condiciones_pago><estatus>activo</estatus><zonas><zona_id>1</zona_id><zona_id>2</zona_id><zona_id>3</zona_id><zona_id>4</zona_id><zona_id>11</zona_id><zona_id>14</zona_id></zonas><calificacion>4</calificacion><evaluaciones>1</evaluaciones></proveedor><proveedor><id>2</id><clave>PV-02</clave><nombre>Distribuidora Regia</nombre><contacto>Luis Treviño</contacto><correo>pedidos@distregia.example</correo><telefono>8181000102</telefono><dias_entrega>1</dias_entrega><pedido_minimo>500.00</pedido_minimo><condiciones_pago>Crédito a 7 días</condiciones_pago><estatus>activo</estatus><zonas><zona_id>1</zona_id><zona_id>2</zona_id><zona_id>3</zona_id><zona_id>4</zona_id><zona_id>11</zona_id><zona_id>14</zona_id></zonas><calificacion>4</calificacion><evaluaciones>1</evaluaciones></proveedor><proveedor><id>3</id><clave>PV-03</clave><nombre>Mayorista San Nicolás</nombre><contacto>Elena Cantú</contacto><correo>compras@mayoristasn.example</correo><telefono>8181000103</telefono><dias_entrega>4</dias_entrega><pedido_minimo>1500.00</pedido_minimo><condiciones_pago>Crédito a 15 días</condiciones_pago><estatus>activo</estatus><zonas><zona_id>1</zona_id><zona_id>2</zona_id><zona_id>3</zona_id><zona_id>4</zona_id><zona_id>11</zona_id><zona_id>14</zona_id></zonas><calificacion>4</calificacion><evaluaciones>1</evaluaciones></proveedor></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>3</total><paginas>1</paginas></paginacion></proveedores>
```

### PRV-03 · Un cliente intenta ver proveedores · PASA

**Objetivo.** El perfil cliente no tiene proveedores.ver.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores`

```http
Accept: application/json
X-Traza-Id: 0ee08d55-17c8-4178-bc60-b3134715577a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 33 ms · traza `0ee08d55-17c8-4178-bc60-b3134715577a`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "0ee08d55-17c8-4178-bc60-b3134715577a"
  }
}
```

### PRV-04 · Un proveedor · PASA

**Objetivo.** Con las zonas que cubre y su calificación.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/2`

```http
Accept: application/json
X-Traza-Id: 7a90630b-2740-4456-b0dc-f68d6aaaea6f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 30 ms · traza `7a90630b-2740-4456-b0dc-f68d6aaaea6f`

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
    4,
    11,
    14
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
X-Traza-Id: c04b65f1-9ad0-4fc6-9479-111b4ec4d43c
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

**Respuesta.** HTTP 201 (esperado 201) · 201 ms · traza `c04b65f1-9ad0-4fc6-9479-111b4ec4d43c`

```json
{
  "id": 145,
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
    "id": 145,
    "clave": "EV-13C8BA",
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
X-Traza-Id: 7442f15b-b21e-4477-ac34-03ebc38d7c4e
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

**Respuesta.** HTTP 409 (esperado 409) · 37 ms · traza `7442f15b-b21e-4477-ac34-03ebc38d7c4e`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Ya existe un proveedor con la clave EV-13C8BA.",
    "traza_id": "7442f15b-b21e-4477-ac34-03ebc38d7c4e"
  }
}
```

### PRV-07 · Correo inválido · PASA

**Objetivo.** Validación con detalle por campo.

**Petición.** `POST http://proveedores:5113/api/v1/proveedores`

```http
Accept: application/json
X-Traza-Id: 8f163342-8661-4494-a505-94641c9c1de4
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

**Respuesta.** HTTP 422 (esperado 422) · 7 ms · traza `8f163342-8661-4494-a505-94641c9c1de4`

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
    "traza_id": "8f163342-8661-4494-a505-94641c9c1de4"
  }
}
```

### PRV-08 · Un planeador intenta dar de alta · PASA

**Objetivo.** Sin proveedores.editar.

**Petición.** `POST http://proveedores:5113/api/v1/proveedores`

```http
Accept: application/json
X-Traza-Id: 2e5e5bcd-d43a-415c-8ec8-b77af1b0df48
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

**Respuesta.** HTTP 403 (esperado 403) · 35 ms · traza `2e5e5bcd-d43a-415c-8ec8-b77af1b0df48`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "2e5e5bcd-d43a-415c-8ec8-b77af1b0df48"
  }
}
```

### PRV-09 · Modificar un proveedor · PASA

**Objetivo.** Cambia el plazo y la cobertura; la clave no se toca.

**Petición.** `PUT http://proveedores:5113/api/v1/proveedores/145`

```http
Accept: application/json
X-Traza-Id: aac0a01e-7620-47d6-a470-430d231f6dba
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

**Respuesta.** HTTP 200 (esperado 200) · 134 ms · traza `aac0a01e-7620-47d6-a470-430d231f6dba`

```json
{
  "id": 145,
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

**Petición.** `PATCH http://proveedores:5113/api/v1/proveedores/145`

```http
Accept: application/json
X-Traza-Id: fdc54819-9419-4bae-a568-4fa8b7aae771
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "contacto": "Luis Prueba"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 92 ms · traza `fdc54819-9419-4bae-a568-4fa8b7aae771`

```json
{
  "id": 145,
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
    "clave": "EV-13C8BA",
    "contacto": "Luis Prueba",
    "dias_entrega": 5
  }
]
```

### PRV-10 · Fijar una oferta · PASA

**Objetivo.** Alta del precio de compra de un producto.

**Petición.** `PUT http://proveedores:5113/api/v1/proveedores/145/catalogo/6`

```http
Accept: application/json
X-Traza-Id: 30b23329-ee65-4094-a4db-f027a8743032
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

**Respuesta.** HTTP 200 (esperado 200) · 69 ms · traza `30b23329-ee65-4094-a4db-f027a8743032`

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
    "proveedor_id": 145,
    "producto_id": 6,
    "precio_compra": "0.05",
    "capacidad_semanal": 100,
    "minimo_compra": 5
  }
]
```

### PRV-11 · Producto inexistente en la oferta · PASA

**Objetivo.** La llave foránea rechaza el producto.

**Petición.** `PUT http://proveedores:5113/api/v1/proveedores/145/catalogo/999999`

```http
Accept: application/json
X-Traza-Id: 2dc35775-5dbc-498d-8e2f-0683c865a6fb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "precio_compra": 1,
  "capacidad_semanal": 10
}
```

**Respuesta.** HTTP 422 (esperado 422) · 66 ms · traza `2dc35775-5dbc-498d-8e2f-0683c865a6fb`

```json
{
  "error": {
    "codigo": "REGLA_NEGOCIO",
    "mensaje": "El producto no existe.",
    "traza_id": "2dc35775-5dbc-498d-8e2f-0683c865a6fb"
  }
}
```

### PRV-12 · Catálogo del proveedor · PASA

**Objetivo.** Sus ofertas, con el nombre del producto.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/145/catalogo`

```http
Accept: application/json
X-Traza-Id: 72b4c60b-7b99-4ed6-b7fd-09205f4c3809
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 70 ms · traza `72b4c60b-7b99-4ed6-b7fd-09205f4c3809`

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

**Petición.** `POST http://proveedores:5113/api/v1/proveedores/145/evaluaciones`

```http
Accept: application/json
X-Traza-Id: 0584a0a1-a288-42d0-b039-8301ea12e1e9
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

**Respuesta.** HTTP 201 (esperado 201) · 61 ms · traza `0584a0a1-a288-42d0-b039-8301ea12e1e9`

```json
{
  "id": 30,
  "proveedor_id": 145,
  "puntualidad": 5,
  "calidad": 4,
  "precio": 3,
  "comentario": "Llegó a tiempo",
  "evaluado_por": 2,
  "evaluado_en": "2026-11-26T23:20:36-06:00"
}
```

**Evidencia en PostgreSQL.** `SELECT proveedor_id, puntualidad, calidad, precio, evaluado_por FROM proveedor_evaluacion WHERE proveedor_id = %s`

```json
[
  {
    "proveedor_id": 145,
    "puntualidad": 5,
    "calidad": 4,
    "precio": 3,
    "evaluado_por": 2
  }
]
```

### PRV-14 · Evaluaciones y promedio · PASA

**Objetivo.** Calificaciones recibidas y su promedio.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/145/evaluaciones`

```http
Accept: application/json
X-Traza-Id: a699f29c-cfa9-4a8b-8445-eab8fcb0072e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 78 ms · traza `a699f29c-cfa9-4a8b-8445-eab8fcb0072e`

```json
{
  "datos": [
    {
      "id": 30,
      "proveedor_id": 145,
      "puntualidad": 5,
      "calidad": 4,
      "precio": 3,
      "comentario": "Llegó a tiempo",
      "evaluado_por": 2,
      "evaluado_en": "2026-11-26T23:20:36-06:00"
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

**Petición.** `POST http://proveedores:5113/api/v1/proveedores/145/evaluaciones`

```http
Accept: application/json
X-Traza-Id: a19fd3b5-0582-4b14-aa8f-d69471d810ce
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

**Respuesta.** HTTP 403 (esperado 403) · 28 ms · traza `a19fd3b5-0582-4b14-aa8f-d69471d810ce`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "a19fd3b5-0582-4b14-aa8f-d69471d810ce"
  }
}
```

### PRV-16 · Ofertas de un producto · PASA

**Objetivo.** De la más barata a la más cara.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/ofertas?producto_id=6`

```http
Accept: application/json
X-Traza-Id: 35adab26-7d52-4846-8f36-85d7bc0b348b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 76 ms · traza `35adab26-7d52-4846-8f36-85d7bc0b348b`

```json
{
  "datos": [
    {
      "proveedor": {
        "id": 145,
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
X-Traza-Id: 177e9369-7d24-4f30-9209-c5a6da3e828a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 77 ms · traza `177e9369-7d24-4f30-9209-c5a6da3e828a`

```json
{
  "datos": [
    {
      "proveedor": {
        "id": 145,
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
X-Traza-Id: 915df578-86f3-4044-a202-e6aa2848baee
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 6 ms · traza `915df578-86f3-4044-a202-e6aa2848baee`

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
    "traza_id": "915df578-86f3-4044-a202-e6aa2848baee"
  }
}
```

### PRV-19 · Dar de baja un proveedor · PASA

**Objetivo.** Baja lógica: ya no aparece en las ofertas.

**Petición.** `DELETE http://proveedores:5113/api/v1/proveedores/145`

```http
Accept: application/json
X-Traza-Id: 6dc21c36-2f3d-4a77-873d-9655a24cd130
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 37 ms · traza `6dc21c36-2f3d-4a77-873d-9655a24cd130`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT clave, estatus FROM proveedor WHERE id = %s`

```json
[
  {
    "clave": "EV-13C8BA",
    "estatus": "inactivo"
  }
]
```

### PRV-20 · Ofertas sin el proveedor de baja · PASA

**Objetivo.** El proveedor dado de baja no ofrece.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/ofertas?producto_id=6`

```http
Accept: application/json
X-Traza-Id: c7b1d6a6-8124-43f5-8e8a-e5730f4930e2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 64 ms · traza `c7b1d6a6-8124-43f5-8e8a-e5730f4930e2`

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
X-Traza-Id: 980338f6-88f7-4cce-a005-0481dd4184a4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 47 ms · traza `980338f6-88f7-4cce-a005-0481dd4184a4`

```json
{
  "datos": [
    {
      "id": 85,
      "nombre": "Lista de evidencias 5b17dd",
      "zona_id": 3,
      "vigente_desde": "2027-01-01",
      "vigente_hasta": "2027-01-31",
      "estatus": "inactivo",
      "productos": 1
    },
    {
      "id": 82,
      "nombre": "Lista de evidencias bca875",
      "zona_id": 3,
      "vigente_desde": "2027-01-01",
      "vigente_hasta": "2027-01-31",
      "estatus": "inactivo",
      "productos": 1
    },
    {
      "id": 79,
      "nombre": "Lista de prueba 1286b043",
      "zona_id": 3,
      "vigente_desde": "2027-01-01",
      "vigente_hasta": "2027-01-31",
      "estatus": "inactivo",
      "productos": 1
    },
    {
      "id": 40,
      "nombre": "Lista de evidencias a7a59e",
      "zona_id": 3,
      "vigente_desde": "2027-01-01",
      "vigente_hasta": "2027-01-31",
      "estatus": "inactivo",
      "productos": 1
    },
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
      "productos": 22
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

### PRE-02 · Listas (XML) · PASA

**Objetivo.** Respuesta XML que cumple precios.xsd.

**Petición.** `GET http://precios:5112/api/v1/precios/listas`

```http
Accept: application/xml
X-Traza-Id: 4556cec8-0978-45e1-ba15-ae09e5d9adb8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 51 ms · traza `4556cec8-0978-45e1-ba15-ae09e5d9adb8`

```xml
<?xml version='1.0' encoding='utf-8'?>
<listas xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><datos><lista><id>85</id><nombre>Lista de evidencias 5b17dd</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>82</id><nombre>Lista de evidencias bca875</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>79</id><nombre>Lista de prueba 1286b043</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>40</id><nombre>Lista de evidencias a7a59e</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>36</id><nombre>Lista de prueba cf2a1ce6</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>35</id><nombre>Lista de evidencias 41a205</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>34</id><nombre>Lista de evidencias f9009f</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>33</id><nombre>Lista de evidencias 3fdd2e</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>29</id><nombre>Lista de prueba 994bc9b6</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>25</id><nombre>Lista de prueba 53ef8464</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>23</id><nombre>Lista de prueba 6efd002d</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>20</id><nombre>Lista de evidencias dba9cd</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>17</id><nombre>Lista de evidencias 4ccd1c</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>16</id><nombre>Lista de evidencias 6ddeea</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>15</id><nombre>Lista de evidencias 962abe</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>14</id><nombre>Lista de evidencias fa981b</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>11</id><nombre>Lista de prueba a8dad7c8</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>4</id><nombre>Lista de prueba 8a4e607d</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>3</id><nombre>Lista de evidencias 0c58f9</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>1</id><nombre>Lista San Bernabé Centro</nombre><zona_id>1</zona_id><vigente_desde>2026-10-19</vigente_desde><vigente_hasta xsi:nil="true" /><estatus>activo</estatus><productos>22</productos></lista></datos><paginacion><pagina>1</pagina><por_pagina>20</por_pagina><total>20</total><paginas>1</paginas></paginacion></listas>
```

### PRE-03 · Un cliente intenta ver las listas · PASA

**Objetivo.** Sin precios.ver.

**Petición.** `GET http://precios:5112/api/v1/precios/listas`

```http
Accept: application/json
X-Traza-Id: f0354920-239c-4aad-b015-69fae0bd8c9a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 30 ms · traza `f0354920-239c-4aad-b015-69fae0bd8c9a`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "f0354920-239c-4aad-b015-69fae0bd8c9a"
  }
}
```

### PRE-04 · Crear una lista · PASA

**Objetivo.** Lista de una zona con un precio y su costo.

**Petición.** `POST http://precios:5112/api/v1/precios/listas`

```http
Accept: application/json
X-Traza-Id: b203334a-0f0b-4abf-9dad-db464754b0e6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Lista de evidencias df2943",
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

**Respuesta.** HTTP 201 (esperado 201) · 83 ms · traza `b203334a-0f0b-4abf-9dad-db464754b0e6`

```json
{
  "id": 86,
  "nombre": "Lista de evidencias df2943",
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
      "actualizado_en": "2026-11-26T23:20:37-06:00"
    }
  ]
}
```

**Explicación.** Margen = (precio − costo) / precio = (50 − 30) / 50 = 40 %.

**Evidencia en PostgreSQL.** `SELECT l.id, l.nombre, l.zona_id, l.vigente_desde, l.vigente_hasta, i.producto_id, i.precio, i.costo FROM lista_precio l JOIN lista_precio_item i ON i.lista_id = l.id WHERE l.nombre = %s`

```json
[
  {
    "id": 86,
    "nombre": "Lista de evidencias df2943",
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
X-Traza-Id: 36b03cbc-3b76-403a-9a86-64cbe47a70b0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Lista de evidencias df2943 bis",
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

**Respuesta.** HTTP 409 (esperado 409) · 28 ms · traza `36b03cbc-3b76-403a-9a86-64cbe47a70b0`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "La lista «Lista de evidencias df2943» ya rige en esa zona durante esas fechas.",
    "traza_id": "36b03cbc-3b76-403a-9a86-64cbe47a70b0"
  }
}
```

### PRE-06 · Cambiar el precio de un producto · PASA

**Objetivo.** Sube el precio de 50 a 52; el costo se conserva.

**Petición.** `PUT http://precios:5112/api/v1/precios/listas/86/items/2`

```http
Accept: application/json
X-Traza-Id: 3cdaf40a-a977-4fb3-aa73-9180074f5f6c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "precio": 52.0
}
```

**Respuesta.** HTTP 200 (esperado 200) · 49 ms · traza `3cdaf40a-a977-4fb3-aa73-9180074f5f6c`

```json
{
  "producto": {
    "id": 2,
    "nombre": "Arroz superextra"
  },
  "precio": 52.0,
  "costo": 30.0,
  "margen_pct": 42.3,
  "actualizado_en": "2026-11-26T23:20:37-06:00"
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

**Petición.** `GET http://precios:5112/api/v1/precios/historial?lista_id=86&producto_id=2`

```http
Accept: application/json
X-Traza-Id: 30ea982a-07ad-4e0c-a199-5ba91162e1b3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 49 ms · traza `30ea982a-07ad-4e0c-a199-5ba91162e1b3`

```json
{
  "datos": [
    {
      "id": 62,
      "lista_id": 86,
      "producto_id": 2,
      "precio_anterior": 50.0,
      "precio_nuevo": 52.0,
      "usuario_id": 1,
      "fecha": "2026-11-26T23:20:37-06:00"
    },
    {
      "id": 61,
      "lista_id": 86,
      "producto_id": 2,
      "precio_anterior": null,
      "precio_nuevo": 50.0,
      "usuario_id": 1,
      "fecha": "2026-11-26T23:20:37-06:00"
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

**Petición.** `GET http://precios:5112/api/v1/precios/listas/86`

```http
Accept: application/json
X-Traza-Id: d82a134f-0c5d-41d6-a827-c6bb1a0b3672
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 89 ms · traza `d82a134f-0c5d-41d6-a827-c6bb1a0b3672`

```json
{
  "id": 86,
  "nombre": "Lista de evidencias df2943",
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
      "actualizado_en": "2026-11-26T23:20:37-06:00"
    }
  ]
}
```

### PRE-09 · Precio dentro de la vigencia · PASA

**Objetivo.** Rige el precio de la lista de la zona.

**Petición.** `GET http://precios:5112/api/v1/precios/vigente?producto_id=2&zona_id=3&fecha=2027-01-15`

```http
Accept: application/json
X-Traza-Id: d8f1d474-12a7-4db2-8593-9ee9c6b6a843
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 134 ms · traza `d8f1d474-12a7-4db2-8593-9ee9c6b6a843`

```json
{
  "producto_id": 2,
  "zona_id": 3,
  "fecha": "2027-01-15",
  "precio_base": 29.9,
  "lista": {
    "id": 86,
    "nombre": "Lista de evidencias df2943"
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
X-Traza-Id: 4aed7c57-86b5-4200-a941-802604d060ec
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 109 ms · traza `4aed7c57-86b5-4200-a941-802604d060ec`

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
X-Traza-Id: 728ee7a3-8526-406f-b70c-1a0cd98c5152
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 81 ms · traza `728ee7a3-8526-406f-b70c-1a0cd98c5152`

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
X-Traza-Id: a51ae58e-b079-45e8-8a43-213c88ac1d3c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 76 ms · traza `a51ae58e-b079-45e8-8a43-213c88ac1d3c`

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
X-Traza-Id: 5b2ba38c-d270-4cf9-8993-50ed40bb7d5c
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

**Respuesta.** HTTP 200 (esperado 200) · 73 ms · traza `5b2ba38c-d270-4cf9-8993-50ed40bb7d5c`

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
X-Traza-Id: 001b640a-0974-40bb-8827-1cd675a93a0e
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

**Respuesta.** HTTP 422 (esperado 422) · 5 ms · traza `001b640a-0974-40bb-8827-1cd675a93a0e`

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
    "traza_id": "001b640a-0974-40bb-8827-1cd675a93a0e"
  }
}
```

### PRE-15 · Promoción que pasa del descuento máximo · PASA

**Objetivo.** Un porcentaje mayor al tope de la configuración se rechaza.

**Petición.** `POST http://precios:5112/api/v1/precios/promociones`

```http
Accept: application/json
X-Traza-Id: c58a195a-e423-4578-be9f-1e215fc8c82c
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

**Respuesta.** HTTP 422 (esperado 422) · 22 ms · traza `c58a195a-e423-4578-be9f-1e215fc8c82c`

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
    "traza_id": "c58a195a-e423-4578-be9f-1e215fc8c82c"
  }
}
```

### PRE-16 · Crear una promoción · PASA

**Objetivo.** Descuento de $2 en un producto.

**Petición.** `POST http://precios:5112/api/v1/precios/promociones`

```http
Accept: application/json
X-Traza-Id: 2e31857c-010a-4afd-a742-c3b2c184d384
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Promoción de evidencias dd3c",
  "tipo": "monto",
  "valor": 2.0,
  "producto_id": 1,
  "vigente_hasta": "2030-12-31"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 149 ms · traza `2e31857c-010a-4afd-a742-c3b2c184d384`

```json
{
  "id": 21,
  "nombre": "Promoción de evidencias dd3c",
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
    "id": 21,
    "nombre": "Promoción de evidencias dd3c",
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
X-Traza-Id: f8836fd3-dd73-4511-bc5c-0f6ca46a3d28
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 51 ms · traza `f8836fd3-dd73-4511-bc5c-0f6ca46a3d28`

```json
{
  "datos": [
    {
      "id": 21,
      "nombre": "Promoción de evidencias dd3c",
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

**Petición.** `DELETE http://precios:5112/api/v1/precios/promociones/21`

```http
Accept: application/json
X-Traza-Id: caf7b9c9-549e-4f53-aa0a-ba4a3896117f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 39 ms · traza `caf7b9c9-549e-4f53-aa0a-ba4a3896117f`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT id, estatus FROM promocion WHERE id = %s`

```json
[
  {
    "id": 21,
    "estatus": "inactivo"
  }
]
```

### PRE-19 · Márgenes · PASA

**Objetivo.** Renglones con costo, del margen más bajo al más alto.

**Petición.** `GET http://precios:5112/api/v1/precios/margenes?por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 67890702-df0b-4096-89e2-60a71cf6b444
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 98 ms · traza `67890702-df0b-4096-89e2-60a71cf6b444`

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
    "total": 22,
    "paginas": 5
  }
}
```

### PRE-20 · Sensibilidad al precio · PASA

**Objetivo.** Qué pasa con ingreso y margen si el precio sube o baja.

**Petición.** `GET http://precios:5112/api/v1/precios/sensibilidad?producto_id=1&zona_id=1&volumen_base=100&elasticidad=-1.2`

```http
Accept: application/json
X-Traza-Id: 3a0073e9-057d-4841-87f0-8de3e53c726e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 193 ms · traza `3a0073e9-057d-4841-87f0-8de3e53c726e`

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
X-Traza-Id: b6c24eea-e2dd-44d9-8168-458ae7dd8f63
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 13 ms · traza `b6c24eea-e2dd-44d9-8168-458ae7dd8f63`

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
    "traza_id": "b6c24eea-e2dd-44d9-8168-458ae7dd8f63"
  }
}
```

## Servicio abastecimiento · puerto 5114

### ABA-01 · Necesidades de reposición · PASA

**Objetivo.** Productos bajo su mínimo, con la mejor oferta.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/necesidades?por_pagina=100`

```http
Accept: application/json
X-Traza-Id: c331a0db-3bc4-4fdf-9516-174801883e7d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 271 ms · traza `c331a0db-3bc4-4fdf-9516-174801883e7d`

```json
{
  "microhub_id": 1,
  "factor_objetivo": 3.0,
  "datos": [
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
    "total": 1,
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
X-Traza-Id: 264aa9dc-5c0e-4596-b48f-1acc8ff7f066
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 8 ms · traza `264aa9dc-5c0e-4596-b48f-1acc8ff7f066`

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
    "traza_id": "264aa9dc-5c0e-4596-b48f-1acc8ff7f066"
  }
}
```

### ABA-03 · Pedir mercancía · PASA

**Objetivo.** El operador pide reposición de su microhub.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: c5f35f39-573f-4bef-b4c0-8f9b06942a86
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

**Respuesta.** HTTP 201 (esperado 201) · 138 ms · traza `c5f35f39-573f-4bef-b4c0-8f9b06942a86`

```json
{
  "id": 80,
  "folio": "SC-20261126-000080",
  "microhub_id": 1,
  "estado": "pendiente",
  "motivo": "Se acabó el producto el fin de semana",
  "solicitada_por": 2,
  "decidida_por": null,
  "decision_motivo": null,
  "decidida_en": null,
  "creada_en": "2026-11-26T23:20:39-06:00",
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
    "id": 80,
    "folio": "SC-20261126-000080",
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
    "titulo": "Solicitud de compra SC-20261126-000080",
    "referencia_tipo": "solicitud"
  }
]
```

### ABA-04 · Pedir para otro microhub · PASA

**Objetivo.** El operador solo trabaja con el suyo.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: 73533b85-2773-40bc-9b90-187f81923f36
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

**Respuesta.** HTTP 403 (esperado 403) · 12 ms · traza `73533b85-2773-40bc-9b90-187f81923f36`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "73533b85-2773-40bc-9b90-187f81923f36"
  }
}
```

### ABA-05 · Producto repetido en la solicitud · PASA

**Objetivo.** Un producto aparece una sola vez.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: a9ae4a5a-cf6d-4271-a525-970ad94c09db
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

**Respuesta.** HTTP 422 (esperado 422) · 7 ms · traza `a9ae4a5a-cf6d-4271-a525-970ad94c09db`

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
    "traza_id": "a9ae4a5a-cf6d-4271-a525-970ad94c09db"
  }
}
```

### ABA-06 · Solicitud de otro microhub · PASA

**Objetivo.** Otro operador no la ve.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/80`

```http
Accept: application/json
X-Traza-Id: 161dbd18-153d-4f3b-8ec0-2ada418f415e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 28 ms · traza `161dbd18-153d-4f3b-8ec0-2ada418f415e`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe esa solicitud de compra.",
    "traza_id": "161dbd18-153d-4f3b-8ec0-2ada418f415e"
  }
}
```

### ABA-07 · Aprobar sin permiso · PASA

**Objetivo.** Solo el administrador decide.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/80/decision`

```http
Accept: application/json
X-Traza-Id: ea078462-5721-478f-b33c-0ee98edb088c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aprobada"
}
```

**Respuesta.** HTTP 403 (esperado 403) · 29 ms · traza `ea078462-5721-478f-b33c-0ee98edb088c`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "ea078462-5721-478f-b33c-0ee98edb088c"
  }
}
```

### ABA-08 · Rechazar sin motivo · PASA

**Objetivo.** Rechazar exige el motivo.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/80/decision`

```http
Accept: application/json
X-Traza-Id: bbc234db-9803-4dd5-a9c7-3fc792c772d9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "rechazada"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 7 ms · traza `bbc234db-9803-4dd5-a9c7-3fc792c772d9`

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
    "traza_id": "bbc234db-9803-4dd5-a9c7-3fc792c772d9"
  }
}
```

### ABA-09 · Ordenar antes de aprobar · PASA

**Objetivo.** Solo se ordena una solicitud aprobada.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/80/ordenar`

```http
Accept: application/json
X-Traza-Id: 87157e1e-5a20-4ad0-a550-6ac4267c7b1c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "proveedor_id": 1
}
```

**Respuesta.** HTTP 409 (esperado 409) · 44 ms · traza `87157e1e-5a20-4ad0-a550-6ac4267c7b1c`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Solo se ordena una solicitud aprobada; esta está pendiente.",
    "traza_id": "87157e1e-5a20-4ad0-a550-6ac4267c7b1c"
  }
}
```

### ABA-10 · Aprobar la solicitud · PASA

**Objetivo.** El administrador aprueba y quien pidió recibe el aviso.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/80/decision`

```http
Accept: application/json
X-Traza-Id: c0f8430f-5033-45de-b1ac-66eac474b58a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aprobada",
  "motivo": "Hay presupuesto"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 104 ms · traza `c0f8430f-5033-45de-b1ac-66eac474b58a`

```json
{
  "id": 80,
  "folio": "SC-20261126-000080",
  "microhub_id": 1,
  "estado": "aprobada",
  "motivo": "Se acabó el producto el fin de semana",
  "solicitada_por": 2,
  "decidida_por": 1,
  "decision_motivo": "Hay presupuesto",
  "decidida_en": "2026-11-26T23:20:39-06:00",
  "creada_en": "2026-11-26T23:20:39-06:00",
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
    "titulo": "Solicitud de compra SC-20261126-000080",
    "mensaje": "Tu solicitud fue aprobada."
  }
]
```

### ABA-11 · Emitir la orden de compra · PASA

**Objetivo.** Cada línea va al proveedor indicado; el total es piezas × precio de compra.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/80/ordenar`

```http
Accept: application/json
X-Traza-Id: bff6d278-db2a-4c3e-a55d-ffe19142a759
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "proveedor_id": 1
}
```

**Respuesta.** HTTP 201 (esperado 201) · 211 ms · traza `bff6d278-db2a-4c3e-a55d-ffe19142a759`

```json
{
  "solicitud_id": 80,
  "ordenes": [
    {
      "id": 51,
      "folio": "OC-20261126-000051",
      "solicitud_id": 80,
      "proveedor": {
        "id": 1,
        "nombre": "Abarrotes del Norte"
      },
      "microhub_id": 1,
      "estado": "emitida",
      "fecha_esperada": "2026-11-28",
      "total": 853.3,
      "creada_en": "2026-11-26T23:20:39-06:00",
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
    "id": 51,
    "folio": "OC-20261126-000051",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/80/ordenar`

```http
Accept: application/json
X-Traza-Id: 48263f4e-fa6d-4861-9959-534ef21e34c6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "proveedor_id": 1
}
```

**Respuesta.** HTTP 409 (esperado 409) · 43 ms · traza `48263f4e-fa6d-4861-9959-534ef21e34c6`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Solo se ordena una solicitud aprobada; esta está ordenada.",
    "traza_id": "48263f4e-fa6d-4861-9959-534ef21e34c6"
  }
}
```

### ABA-13 · Recepción parcial · PASA

**Objetivo.** La mercancía que llegó entra al inventario.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/51/recepcion`

```http
Accept: application/json
X-Traza-Id: 394c0d63-0809-434c-914c-db32f414ef67
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "operacion_uuid": "3f433edd-de18-41df-8dd2-2da80e13c66f",
  "nota": "Llegó la primera caja",
  "lineas": [
    {
      "producto_id": 10,
      "cantidad": 23
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 285 ms · traza `394c0d63-0809-434c-914c-db32f414ef67`

```json
{
  "orden": {
    "id": 51,
    "folio": "OC-20261126-000051",
    "solicitud_id": 80,
    "proveedor": {
      "id": 1,
      "nombre": "Abarrotes del Norte"
    },
    "microhub_id": 1,
    "estado": "parcial",
    "fecha_esperada": "2026-11-28",
    "total": 853.3,
    "creada_en": "2026-11-26T23:20:39-06:00",
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
    "operacion_uuid": "3f433edd-de18-41df-8dd2-2da80e13c66f:10",
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
    "existencia_resultante": 943,
    "referencia_tipo": "orden_compra",
    "referencia_id": 51
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/51/recepcion`

```http
Accept: application/json
X-Traza-Id: ba08dc27-d104-4032-83b6-dab4031eea31
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "operacion_uuid": "3f433edd-de18-41df-8dd2-2da80e13c66f",
  "nota": "Llegó la primera caja",
  "lineas": [
    {
      "producto_id": 10,
      "cantidad": 23
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 218 ms · traza `ba08dc27-d104-4032-83b6-dab4031eea31`

```json
{
  "orden": {
    "id": 51,
    "folio": "OC-20261126-000051",
    "solicitud_id": 80,
    "proveedor": {
      "id": 1,
      "nombre": "Abarrotes del Norte"
    },
    "microhub_id": 1,
    "estado": "parcial",
    "fecha_esperada": "2026-11-28",
    "total": 853.3,
    "creada_en": "2026-11-26T23:20:39-06:00",
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
    "existencia": 943
  }
]
```

### ABA-15 · Recibir más de lo pedido · PASA

**Objetivo.** Solo falta lo que no ha llegado.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/51/recepcion`

```http
Accept: application/json
X-Traza-Id: 27b46f4c-8feb-4ff4-a02b-3ddce756e1bc
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

**Respuesta.** HTTP 422 (esperado 422) · 62 ms · traza `27b46f4c-8feb-4ff4-a02b-3ddce756e1bc`

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
    "traza_id": "27b46f4c-8feb-4ff4-a02b-3ddce756e1bc"
  }
}
```

### ABA-16 · Cancelar una orden con mercancía recibida · PASA

**Objetivo.** Solo se cancela una orden sin recepciones.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/51/cancelar`

```http
Accept: application/json
X-Traza-Id: e31fa25f-8fb7-45cc-9ade-bf602d6f0d65
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "motivo": "Ya llegó"
}
```

**Respuesta.** HTTP 409 (esperado 409) · 49 ms · traza `e31fa25f-8fb7-45cc-9ade-bf602d6f0d65`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Solo se cancela una orden emitida que todavía no recibió mercancía.",
    "traza_id": "e31fa25f-8fb7-45cc-9ade-bf602d6f0d65"
  }
}
```

### ABA-17 · Recepción final · PASA

**Objetivo.** Llega el resto: la orden queda recibida y avisa.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/51/recepcion`

```http
Accept: application/json
X-Traza-Id: ba9d9651-f744-43cc-9cfb-66efca133764
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

**Respuesta.** HTTP 201 (esperado 201) · 307 ms · traza `ba9d9651-f744-43cc-9cfb-66efca133764`

```json
{
  "orden": {
    "id": 51,
    "folio": "OC-20261126-000051",
    "solicitud_id": 80,
    "proveedor": {
      "id": 1,
      "nombre": "Abarrotes del Norte"
    },
    "microhub_id": 1,
    "estado": "recibida",
    "fecha_esperada": "2026-11-28",
    "total": 853.3,
    "creada_en": "2026-11-26T23:20:39-06:00",
    "cerrada_en": "2026-11-26T23:20:40-06:00",
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
    "existencia": 966
  }
]
```

**Evidencia en PostgreSQL.** `SELECT destinatario_id, titulo, mensaje FROM web_notificacion WHERE referencia_tipo = 'orden' AND referencia_id = %s`

```json
[
  {
    "destinatario_id": 2,
    "titulo": "Orden de compra OC-20261126-000051",
    "mensaje": "La orden quedó recibida."
  },
  {
    "destinatario_id": 1,
    "titulo": "Orden de compra OC-20261126-000051",
    "mensaje": "La orden quedó recibida."
  }
]
```

### ABA-18 · Recibir en una orden ya recibida · PASA

**Objetivo.** Una orden recibida no admite más mercancía.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/51/recepcion`

```http
Accept: application/json
X-Traza-Id: 14948382-701b-40bf-8452-f3e8169dc636
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

**Respuesta.** HTTP 409 (esperado 409) · 42 ms · traza `14948382-701b-40bf-8452-f3e8169dc636`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "La orden está recibida; ya no recibe mercancía.",
    "traza_id": "14948382-701b-40bf-8452-f3e8169dc636"
  }
}
```

### ABA-19 · Una orden · PASA

**Objetivo.** Con lo recibido de cada línea.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/ordenes/51`

```http
Accept: application/json
X-Traza-Id: f7446ac7-4f0b-472e-9031-e390a83bea1e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 65 ms · traza `f7446ac7-4f0b-472e-9031-e390a83bea1e`

```json
{
  "id": 51,
  "folio": "OC-20261126-000051",
  "solicitud_id": 80,
  "proveedor": {
    "id": 1,
    "nombre": "Abarrotes del Norte"
  },
  "microhub_id": 1,
  "estado": "recibida",
  "fecha_esperada": "2026-11-28",
  "total": 853.3,
  "creada_en": "2026-11-26T23:20:39-06:00",
  "cerrada_en": "2026-11-26T23:20:40-06:00",
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
X-Traza-Id: dd5a199e-86ea-4705-94ef-3ed6f5ebe2c0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 87 ms · traza `dd5a199e-86ea-4705-94ef-3ed6f5ebe2c0`

```xml
<?xml version='1.0' encoding='utf-8'?>
<ordenes xmlns="urn:microhubs:v1" version="1"><datos><orden><id>51</id><folio>OC-20261126-000051</folio><solicitud_id>80</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>853.30</total><creada_en>2026-11-26T23:20:39-06:00</creada_en><cerrada_en>2026-11-26T23:20:40-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>49</id><folio>OC-20261126-000049</folio><solicitud_id>78</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>853.30</total><creada_en>2026-11-26T23:19:22-06:00</creada_en><cerrada_en>2026-11-26T23:19:23-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>48</id><folio>OC-20261126-000048</folio><solicitud_id>77</solicitud_id><proveedor><id>2</id><nombre>Distribuidora Regia</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-27</fecha_esperada><total>745.92</total><creada_en>2026-11-26T23:17:15-06:00</creada_en><cerrada_en>2026-11-26T23:17:16-06:00</cerrada_en><lineas><linea><producto><id>3</id><nombre>Aceite vegetal</nombre></producto><cantidad>24</cantidad><precio_compra>31.08</precio_compra><cantidad_recibida>24</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>47</id><folio>OC-20261126-000047</folio><solicitud_id>76</solicitud_id><proveedor><id>2</id><nombre>Distribuidora Regia</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-27</fecha_esperada><total>843.60</total><creada_en>2026-11-26T23:15:54-06:00</creada_en><cerrada_en>2026-11-26T23:15:55-06:00</cerrada_en><lineas><linea><producto><id>21</id><nombre>Agua purificada</nombre></producto><cantidad>30</cantidad><precio_compra>28.12</precio_compra><cantidad_recibida>30</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>45</id><folio>OC-20261126-000045</folio><solicitud_id>74</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>853.30</total><creada_en>2026-11-26T23:12:13-06:00</creada_en><cerrada_en>2026-11-26T23:12:14-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>44</id><folio>OC-20261126-000044</folio><solicitud_id>73</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>4060.00</total><creada_en>2026-11-26T23:11:45-06:00</creada_en><cerrada_en>2026-11-26T23:11:46-06:00</cerrada_en><lineas><linea><producto><id>31</id><nombre>Queso fresco</nombre></producto><cantidad>100</cantidad><precio_compra>40.60</precio_compra><cantidad_recibida>100</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>43</id><folio>OC-20261126-000043</folio><solicitud_id>71</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>859.95</total><creada_en>2026-11-26T23:07:20-06:00</creada_en><cerrada_en>2026-11-26T23:07:21-06:00</cerrada_en><lineas><linea><producto><id>12</id><nombre>Chiles jalapeños en escabeche</nombre></producto><cantidad>63</cantidad><precio_compra>13.65</precio_compra><cantidad_recibida>63</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>42</id><folio>OC-20261126-000042</folio><solicitud_id>69</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>853.30</total><creada_en>2026-11-26T23:07:16-06:00</creada_en><cerrada_en>2026-11-26T23:07:17-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>39</id><folio>OC-20261126-000039</folio><solicitud_id>64</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>853.30</total><creada_en>2026-11-26T15:23:08-06:00</creada_en><cerrada_en>2026-11-26T15:23:09-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>38</id><folio>OC-20261126-000038</folio><solicitud_id>63</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>4060.00</total><creada_en>2026-11-26T15:22:04-06:00</creada_en><cerrada_en>2026-11-26T15:22:04-06:00</cerrada_en><lineas><linea><producto><id>31</id><nombre>Queso fresco</nombre></producto><cantidad>100</cantidad><precio_compra>40.60</precio_compra><cantidad_recibida>100</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>37</id><folio>OC-20261126-000037</folio><solicitud_id>60</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>859.95</total><creada_en>2026-11-26T14:22:19-06:00</creada_en><cerrada_en>2026-11-26T14:22:21-06:00</cerrada_en><lineas><linea><producto><id>12</id><nombre>Chiles jalapeños en escabeche</nombre></producto><cantidad>63</cantidad><precio_compra>13.65</precio_compra><cantidad_recibida>63</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>36</id><folio>OC-20261126-000036</folio><solicitud_id>58</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>853.30</total><creada_en>2026-11-26T14:22:16-06:00</creada_en><cerrada_en>2026-11-26T14:22:17-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>33</id><folio>OC-20261126-000033</folio><solicitud_id>53</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>853.30</total><creada_en>2026-11-26T14:19:44-06:00</creada_en><cerrada_en>2026-11-26T14:19:45-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>31</id><folio>OC-20261126-000031</folio><solicitud_id>51</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>853.30</total><creada_en>2026-11-26T14:04:57-06:00</creada_en><cerrada_en>2026-11-26T14:04:58-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>29</id><folio>OC-20261126-000029</folio><solicitud_id>49</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>853.30</total><creada_en>2026-11-26T13:51:34-06:00</creada_en><cerrada_en>2026-11-26T13:51:35-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>28</id><folio>OC-20261126-000028</folio><solicitud_id>47</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>859.95</total><creada_en>2026-11-26T00:32:05-06:00</creada_en><cerrada_en>2026-11-26T00:32:06-06:00</cerrada_en><lineas><linea><producto><id>12</id><nombre>Chiles jalapeños en escabeche</nombre></producto><cantidad>63</cantidad><precio_compra>13.65</precio_compra><cantidad_recibida>63</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>27</id><folio>OC-20261126-000027</folio><solicitud_id>45</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-11-28</fecha_esperada><total>853.30</total><creada_en>2026-11-26T00:32:01-06:00</creada_en><cerrada_en>2026-11-26T00:32:03-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>25</id><folio>OC-20261020-000025</folio><solicitud_id>40</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>859.95</total><creada_en>2026-10-20T08:13:53-06:00</creada_en><cerrada_en>2026-10-20T08:13:54-06:00</cerrada_en><lineas><linea><producto><id>12</id><nombre>Chiles jalapeños en escabeche</nombre></producto><cantidad>63</cantidad><precio_compra>13.65</precio_compra><cantidad_recibida>63</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>24</id><folio>OC-20261020-000024</folio><solicitud_id>38</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>853.30</total><creada_en>2026-10-20T08:13:49-06:00</creada_en><cerrada_en>2026-10-20T08:13:51-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>22</id><folio>OC-20261020-000022</folio><solicitud_id>33</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>859.95</total><creada_en>2026-10-20T00:50:20-06:00</creada_en><cerrada_en>2026-10-20T00:50:21-06:00</cerrada_en><lineas><linea><producto><id>12</id><nombre>Chiles jalapeños en escabeche</nombre></producto><cantidad>63</cantidad><precio_compra>13.65</precio_compra><cantidad_recibida>63</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden></datos><paginacion><pagina>1</pagina><por_pagina>20</por_pagina><total>32</total><paginas>2</paginas></paginacion></ordenes>
```

### ABA-21 · Tablero de abastecimiento · PASA

**Objetivo.** Solicitudes y órdenes por estado.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/seguimiento`

```http
Accept: application/json
X-Traza-Id: 092ff439-1f3b-4afc-ba7f-964dfd54296e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 102 ms · traza `092ff439-1f3b-4afc-ba7f-964dfd54296e`

```json
{
  "microhub_id": 1,
  "solicitudes": {
    "pendiente": 0,
    "aprobada": 1,
    "rechazada": 21,
    "ordenada": 51
  },
  "ordenes": {
    "emitida": 0,
    "parcial": 0,
    "recibida": 32,
    "cancelada": 19
  },
  "atrasadas": 0,
  "pendientes_inventario": 0,
  "proxima_entrega": null
}
```

### ABA-22 · Cancelar sin permiso · PASA

**Objetivo.** Cancelar una orden es del administrador.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/52/cancelar`

```http
Accept: application/json
X-Traza-Id: e3636655-176d-4b1e-a433-ca6fc0d56e7a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "motivo": "No hace falta"
}
```

**Respuesta.** HTTP 403 (esperado 403) · 32 ms · traza `e3636655-176d-4b1e-a433-ca6fc0d56e7a`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "e3636655-176d-4b1e-a433-ca6fc0d56e7a"
  }
}
```

### ABA-23 · Cancelar una orden emitida · PASA

**Objetivo.** Una orden sin recepciones se puede cancelar con motivo.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/52/cancelar`

```http
Accept: application/json
X-Traza-Id: b2799ada-9e71-4550-bf76-61ec6bce95f7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "motivo": "El proveedor ya no surte"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 130 ms · traza `b2799ada-9e71-4550-bf76-61ec6bce95f7`

```json
{
  "id": 52,
  "folio": "OC-20261126-000052",
  "solicitud_id": 81,
  "proveedor": {
    "id": 1,
    "nombre": "Abarrotes del Norte"
  },
  "microhub_id": 1,
  "estado": "cancelada",
  "fecha_esperada": "2026-11-28",
  "total": 853.3,
  "creada_en": "2026-11-26T23:20:41-06:00",
  "cerrada_en": "2026-11-26T23:20:41-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/52/recepcion`

```http
Accept: application/json
X-Traza-Id: f8b1cd9c-9453-43db-a842-b7a7eed5f321
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

**Respuesta.** HTTP 409 (esperado 409) · 52 ms · traza `f8b1cd9c-9453-43db-a842-b7a7eed5f321`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "La orden está cancelada; ya no recibe mercancía.",
    "traza_id": "f8b1cd9c-9453-43db-a842-b7a7eed5f321"
  }
}
```

### ABA-25 · Solicitudes (XML) · PASA

**Objetivo.** Respuesta XML que cumple abastecimiento.xsd.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/solicitudes?por_pagina=3`

```http
Accept: application/xml
X-Traza-Id: 9f2203ee-bb13-46cf-9845-771e75220622
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 68 ms · traza `9f2203ee-bb13-46cf-9845-771e75220622`

```xml
<?xml version='1.0' encoding='utf-8'?>
<solicitudes xmlns="urn:microhubs:v1" version="1"><datos><solicitud><id>81</id><folio>SC-20261126-000081</folio><microhub_id>1</microhub_id><estado>ordenada</estado><motivo>Compra para cancelar</motivo><solicitada_por>2</solicitada_por><decidida_por>1</decidida_por><decision_motivo>Hay presupuesto</decision_motivo><decidida_en>2026-11-26T23:20:41-06:00</decidida_en><creada_en>2026-11-26T23:20:41-06:00</creada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad></linea></lineas></solicitud><solicitud><id>80</id><folio>SC-20261126-000080</folio><microhub_id>1</microhub_id><estado>ordenada</estado><motivo>Se acabó el producto el fin de semana</motivo><solicitada_por>2</solicitada_por><decidida_por>1</decidida_por><decision_motivo>Hay presupuesto</decision_motivo><decidida_en>2026-11-26T23:20:39-06:00</decidida_en><creada_en>2026-11-26T23:20:39-06:00</creada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad></linea></lineas></solicitud><solicitud><id>79</id><folio>SC-20261126-000079</folio><microhub_id>1</microhub_id><estado>ordenada</estado><motivo>Compra para cancelar</motivo><solicitada_por>2</solicitada_por><decidida_por>1</decidida_por><decision_motivo>Hay presupuesto</decision_motivo><decidida_en>2026-11-26T23:19:23-06:00</decidida_en><creada_en>2026-11-26T23:19:23-06:00</creada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad></linea></lineas></solicitud></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>74</total><paginas>25</paginas></paginacion></solicitudes>
```

### ABA-26 · Un auditor consulta · PASA

**Objetivo.** El auditor ve las solicitudes sin poder crear.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: 4ceda55b-e8b8-4245-8c58-e4861f088ee4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 65 ms · traza `4ceda55b-e8b8-4245-8c58-e4861f088ee4`

```json
{
  "datos": [
    {
      "id": 81,
      "folio": "SC-20261126-000081",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Compra para cancelar",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-11-26T23:20:41-06:00",
      "creada_en": "2026-11-26T23:20:41-06:00",
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
      "id": 80,
      "folio": "SC-20261126-000080",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Se acabó el producto el fin de semana",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-11-26T23:20:39-06:00",
      "creada_en": "2026-11-26T23:20:39-06:00",
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
      "id": 79,
      "folio": "SC-20261126-000079",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Compra para cancelar",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-11-26T23:19:23-06:00",
      "creada_en": "2026-11-26T23:19:23-06:00",
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
      "id": 78,
      "folio": "SC-20261126-000078",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Se acabó el producto el fin de semana",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-11-26T23:19:21-06:00",
      "creada_en": "2026-11-26T23:19:21-06:00",
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
      "id": 77,
      "folio": "SC-20261126-000077",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Proceso integral b84e26",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-11-26T23:17:15-06:00",
      "creada_en": "2026-11-26T23:17:14-06:00",
      "lineas": [
        {
          "producto": {
            "id": 3,
            "nombre": "Aceite vegetal"
          },
          "cantidad": 24
        }
      ]
    },
    {
      "id": 76,
      "folio": "SC-20261126-000076",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Proceso integral 5514e1",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-11-26T23:15:54-06:00",
      "creada_en": "2026-11-26T23:15:53-06:00",
      "lineas": [
        {
          "producto": {
            "id": 21,
            "nombre": "Agua purificada"
          },
          "cantidad": 30
        }
      ]
    },
    {
      "id": 75,
      "folio": "SC-20261126-000075",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Compra para cancelar",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-11-26T23:12:15-06:00",
      "creada_en": "2026-11-26T23:12:15-06:00",
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
      "id": 74,
      "folio": "SC-20261126-000074",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Se acabó el producto el fin de semana",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-11-26T23:12:13-06:00",
      "creada_en": "2026-11-26T23:12:13-06:00",
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
      "id": 73,
      "folio": "SC-20261126-000073",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Faltante detectado por el sistema",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Con presupuesto",
      "decidida_en": "2026-11-26T23:11:45-06:00",
      "creada_en": "2026-11-26T23:11:45-06:00",
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
      "id": 72,
      "folio": "SC-20261126-000072",
      "microhub_id": 1,
      "estado": "rechazada",
      "motivo": "Prueba XML",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Prueba XML",
      "decidida_en": "2026-11-26T23:07:21-06:00",
      "creada_en": "2026-11-26T23:07:21-06:00",
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
      "id": 71,
      "folio": "SC-20261126-000071",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-11-26T23:07:20-06:00",
      "creada_en": "2026-11-26T23:07:19-06:00",
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
      "id": 70,
      "folio": "SC-20261126-000070",
      "microhub_id": 1,
      "estado": "rechazada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": null,
      "decision_motivo": "Limpieza de la prueba",
      "decidida_en": null,
      "creada_en": "2026-11-26T23:07:19-06:00",
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
      "id": 69,
      "folio": "SC-20261126-000069",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "ok",
      "decidida_en": "2026-11-26T23:07:15-06:00",
      "creada_en": "2026-11-26T23:07:15-06:00",
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
      "id": 67,
      "folio": "SC-20261126-000067",
      "microhub_id": 1,
      "estado": "rechazada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Todavía hay existencia",
      "decidida_en": "2026-11-26T23:07:14-06:00",
      "creada_en": "2026-11-26T23:07:14-06:00",
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
      "id": 66,
      "folio": "SC-20261126-000066",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-11-26T23:07:13-06:00",
      "creada_en": "2026-11-26T23:07:13-06:00",
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
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 74,
    "paginas": 4
  }
}
```

### ABA-27 · Un cliente consulta · PASA

**Objetivo.** El cliente no tiene abastecimiento.ver.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: 1c3c8bc4-63a5-414c-a4e6-d54089652785
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 27 ms · traza `1c3c8bc4-63a5-414c-a4e6-d54089652785`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "1c3c8bc4-63a5-414c-a4e6-d54089652785"
  }
}
```

## Servicio pedidos · puerto 5104

### ALI-01 · Resumen de pedidos por día y zona · PASA

**Objetivo.** Lo consume el servicio de demanda: pedidos, unidades, venta y clientes por día y zona.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/resumen?por_pagina=5`

```http
Accept: application/json
X-Traza-Id: a62a26b0-d3cf-4de7-8595-0c2b655739bb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 81 ms · traza `a62a26b0-d3cf-4de7-8595-0c2b655739bb`

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
      "pedidos": 47,
      "unidades": 246,
      "venta": 6664.1,
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
X-Traza-Id: eca8abea-843e-4f45-bfb7-a26120ba5749
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 8 ms · traza `eca8abea-843e-4f45-bfb7-a26120ba5749`

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
    "traza_id": "eca8abea-843e-4f45-bfb7-a26120ba5749"
  }
}
```

### ALI-03 · Ventas por producto · PASA

**Objetivo.** Lo consume surtido: unidades y venta de cada producto, sin cancelados.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/ventas?por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 0a23ec1b-ecf3-423c-b4a5-1f8e8d2f5142
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 85 ms · traza `0a23ec1b-ecf3-423c-b4a5-1f8e8d2f5142`

```json
{
  "datos": [
    {
      "producto_id": 28,
      "unidades": 78,
      "venta": 585.0,
      "pedidos": 20
    },
    {
      "producto_id": 16,
      "unidades": 58,
      "venta": 957.0,
      "pedidos": 26
    },
    {
      "producto_id": 51,
      "unidades": 54,
      "venta": 3672.0,
      "pedidos": 32
    },
    {
      "producto_id": 31,
      "unidades": 53,
      "venta": 3074.0,
      "pedidos": 26
    },
    {
      "producto_id": 45,
      "unidades": 52,
      "venta": 936.0,
      "pedidos": 28
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
X-Traza-Id: 7865d47f-3720-4462-8cb7-1cc911fa76e1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 5 ms · traza `7865d47f-3720-4462-8cb7-1cc911fa76e1`

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
    "traza_id": "7865d47f-3720-4462-8cb7-1cc911fa76e1"
  }
}
```

### ALI-05 · Pedidos listos de un microhub · PASA

**Objetivo.** Con las coordenadas de entrega: lo que rutas agrupa y ordena.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/listos?microhub_id=1`

```http
Accept: application/json
X-Traza-Id: 9be0cc43-eed2-41e7-94da-7ab623c5eef8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 67 ms · traza `9be0cc43-eed2-41e7-94da-7ab623c5eef8`

```json
{
  "datos": [],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 100,
    "total": 0,
    "paginas": 0
  }
}
```

**Evidencia en PostgreSQL.** `SELECT count(*) AS listos FROM pedido WHERE microhub_id = %s AND estado = 'en_preparacion' AND listo_en IS NOT NULL`

```json
[
  {
    "listos": 0
  }
]
```

## Servicio entregas · puerto 5105

### ALI-06 · Repartidores activos · PASA

**Objetivo.** Con las entregas que tienen abiertas hoy; lo consume rutas.

**Petición.** `GET http://entregas:5105/api/v1/entregas/repartidores`

```http
Accept: application/json
X-Traza-Id: 85a9e03f-b5a2-4b28-83d3-ded2eae8fd5e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 75 ms · traza `85a9e03f-b5a2-4b28-83d3-ded2eae8fd5e`

```json
{
  "datos": [
    {
      "id": 7,
      "nombre": "Ramiro Alanís Lozano",
      "entregas_abiertas": 4
    },
    {
      "id": 8,
      "nombre": "Diana Sepúlveda Ibarra",
      "entregas_abiertas": 3
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
X-Traza-Id: 246c68d8-613c-4939-9bac-fdd94f3a275d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 91 ms · traza `246c68d8-613c-4939-9bac-fdd94f3a275d`

```json
{
  "datos": [
    {
      "microhub_id": 1,
      "producto_id": 3,
      "quiebres": 1,
      "ultimo": "2026-11-26T23:17:13-06:00",
      "agotado_hoy": false
    },
    {
      "microhub_id": 1,
      "producto_id": 21,
      "quiebres": 1,
      "ultimo": "2026-10-19T19:30:44-06:00",
      "agotado_hoy": false
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

### ALI-08 · Quiebres con ventana inválida · PASA

**Objetivo.** dias debe estar entre 1 y 365.

**Petición.** `GET http://inventario:5111/api/v1/inventario/quiebres?dias=0`

```http
Accept: application/json
X-Traza-Id: 0da179a4-76b8-452a-bf11-129f248c2064
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 6 ms · traza `0da179a4-76b8-452a-bf11-129f248c2064`

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
    "traza_id": "0da179a4-76b8-452a-bf11-129f248c2064"
  }
}
```

## Servicio demanda · puerto 5115

### DEM-01 · Observaciones de demanda · PASA

**Objetivo.** Pedidos por día, zona y categoría, con la fuente de cada dato.

**Petición.** `GET http://demanda:5115/api/v1/demanda/observaciones?nivel=total&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 3388b5d5-7d15-4025-88b1-ccc20b6fe108
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 227 ms · traza `3388b5d5-7d15-4025-88b1-ccc20b6fe108`

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
X-Traza-Id: 8711aa77-2847-47d7-9543-dd2e2181a11c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 111 ms · traza `8711aa77-2847-47d7-9543-dd2e2181a11c`

```xml
<?xml version='1.0' encoding='utf-8'?>
<observaciones_demanda xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><datos><observacion><fecha>2026-11-25</fecha><zona><id>1</id><nombre>San Bernabé Centro</nombre></zona><categoria xsi:nil="true" /><pedidos>17</pedidos><unidades>88</unidades><venta>2423.70</venta><clientes>14</clientes><no_atendidos>1</no_atendidos><fuente>sintetica</fuente></observacion><observacion><fecha>2026-11-25</fecha><zona><id>1</id><nombre>San Bernabé Centro</nombre></zona><categoria><id>1</id><nombre>Abarrote básico</nombre></categoria><pedidos>17</pedidos><unidades>40</unidades><venta>1090.67</venta><clientes>0</clientes><no_atendidos>0</no_atendidos><fuente>sintetica</fuente></observacion><observacion><fecha>2026-11-25</fecha><zona><id>1</id><nombre>San Bernabé Centro</nombre></zona><categoria><id>2</id><nombre>Bebidas</nombre></categoria><pedidos>7</pedidos><unidades>18</unidades><venta>484.74</venta><clientes>0</clientes><no_atendidos>0</no_atendidos><fuente>sintetica</fuente></observacion></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>1440</total><paginas>480</paginas></paginacion></observaciones_demanda>
```

### DEM-03 · Fuente desconocida · PASA

**Objetivo.** Un filtro desconocido se rechaza.

**Petición.** `GET http://demanda:5115/api/v1/demanda/observaciones?fuente=inventada`

```http
Accept: application/json
X-Traza-Id: c03db0cc-d7c4-46c1-895a-d1982f13c3cf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 48 ms · traza `c03db0cc-d7c4-46c1-895a-d1982f13c3cf`

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
    "traza_id": "c03db0cc-d7c4-46c1-895a-d1982f13c3cf"
  }
}
```

### DEM-04 · El operador consulta la demanda · PASA

**Objetivo.** Sin demanda.ver.

**Petición.** `GET http://demanda:5115/api/v1/demanda/observaciones`

```http
Accept: application/json
X-Traza-Id: 9c5cf605-b39a-4ee7-b557-4fda84916fc0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 26 ms · traza `9c5cf605-b39a-4ee7-b557-4fda84916fc0`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "9c5cf605-b39a-4ee7-b557-4fda84916fc0"
  }
}
```

### DEM-05 · Resumen por zona · PASA

**Objetivo.** Pedidos, ticket promedio, pedidos por cliente y demanda no atendida.

**Petición.** `GET http://demanda:5115/api/v1/demanda/resumen`

```http
Accept: application/json
X-Traza-Id: 5e7befe0-1322-4edc-94be-317fb86d27ca
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 106 ms · traza `5e7befe0-1322-4edc-94be-317fb86d27ca`

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
X-Traza-Id: bb108d3f-c92e-4263-808f-c79304bf8124
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 119 ms · traza `bb108d3f-c92e-4263-808f-c79304bf8124`

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
X-Traza-Id: 43e05a12-46c0-40aa-b4a9-53d3ec8d41b1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 72 ms · traza `43e05a12-46c0-40aa-b4a9-53d3ec8d41b1`

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
X-Traza-Id: 8ad5544d-9c26-4201-81af-57ceb6d41352
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 71 ms · traza `8ad5544d-9c26-4201-81af-57ceb6d41352`

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
X-Traza-Id: f9e19ddd-54fb-4e8f-8b9e-ff29c8fe77e8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 29 ms · traza `f9e19ddd-54fb-4e8f-8b9e-ff29c8fe77e8`

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
    "traza_id": "f9e19ddd-54fb-4e8f-8b9e-ff29c8fe77e8"
  }
}
```

### DEM-10 · Comparación contra lo observado · PASA

**Objetivo.** Se ocultan los últimos 7 días, se proyectan y se miden el error y el sesgo.

**Petición.** `GET http://demanda:5115/api/v1/demanda/comparacion`

```http
Accept: application/json
X-Traza-Id: e7731983-bcb9-4fa2-9575-88a246ede4f2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 72 ms · traza `e7731983-bcb9-4fa2-9575-88a246ede4f2`

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
X-Traza-Id: 30de0559-040f-4b82-87e4-8a530e1c585f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 144 ms · traza `30de0559-040f-4b82-87e4-8a530e1c585f`

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
X-Traza-Id: 027c80cc-ba06-46bc-9a3e-7d10a40a6b6d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 268 ms · traza `027c80cc-ba06-46bc-9a3e-7d10a40a6b6d`

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
X-Traza-Id: 4bd1301e-b064-499a-8fa1-250b67d93029
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{
  "desde": "2026-11-25",
  "hasta": "2026-11-27"
}
```

**Respuesta.** HTTP 403 (esperado 403) · 28 ms · traza `4bd1301e-b064-499a-8fa1-250b67d93029`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "4bd1301e-b064-499a-8fa1-250b67d93029"
  }
}
```

### DEM-14 · Sincronizar con pedidos reales · PASA

**Objetivo.** Lo sintético del rango se reemplaza por lo real.

**Petición.** `POST http://demanda:5115/api/v1/demanda/sincronizacion`

```http
Accept: application/json
X-Traza-Id: 9a5940bb-9bda-435a-9c44-72e1e98db845
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "desde": "2026-11-25",
  "hasta": "2026-11-27"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 112 ms · traza `9a5940bb-9bda-435a-9c44-72e1e98db845`

```json
{
  "desde": "2026-11-25",
  "hasta": "2026-11-27",
  "filas_escritas": 8,
  "pedidos_leidos": 255,
  "sinteticas_reemplazadas": 24
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
X-Traza-Id: 64d691ef-4001-4650-b982-01409a242b0b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "desde": "2026-10-10",
  "hasta": "2026-10-01"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 8 ms · traza `64d691ef-4001-4650-b982-01409a242b0b`

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
    "traza_id": "64d691ef-4001-4650-b982-01409a242b0b"
  }
}
```

### DEM-16 · Sincronizar (XML) · PASA

**Objetivo.** El cuerpo XML se valida contra demanda.xsd antes de procesarse.

**Petición.** `POST http://demanda:5115/api/v1/demanda/sincronizacion`

```http
Accept: application/xml
X-Traza-Id: d959c0d4-fa97-47fa-b5e4-a9ad2263fd56
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><sincronizacion_nueva xmlns="urn:microhubs:v1"><desde>2026-11-27</desde><hasta>2026-11-27</hasta></sincronizacion_nueva>
```

**Respuesta.** HTTP 201 (esperado 201) · 90 ms · traza `d959c0d4-fa97-47fa-b5e4-a9ad2263fd56`

```xml
<?xml version='1.0' encoding='utf-8'?>
<sincronizacion xmlns="urn:microhubs:v1" version="1"><desde>2026-11-27</desde><hasta>2026-11-27</hasta><filas_escritas>0</filas_escritas><pedidos_leidos>0</pedidos_leidos><sinteticas_reemplazadas>0</sinteticas_reemplazadas></sincronizacion>
```

### DEM-17 · Supuestos de la demanda · PASA

**Objetivo.** Valor, origen (medido, supuesto o normativo), justificación y cómo calibrarlo.

**Petición.** `GET http://demanda:5115/api/v1/demanda/supuestos`

```http
Accept: application/json
X-Traza-Id: e88ef8f5-1a7d-4c45-a392-24c78940e6bf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 34 ms · traza `e88ef8f5-1a7d-4c45-a392-24c78940e6bf`

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
X-Traza-Id: e7a08fb2-43f3-4f74-b92b-e5bf42ef7b80
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 50 ms · traza `e7a08fb2-43f3-4f74-b92b-e5bf42ef7b80`

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
    },
    {
      "zona": {
        "id": 11,
        "nombre": "Zona D5F75A renombrada"
      },
      "hogares": 0,
      "estado": "sin_cobertura",
      "solapada": false,
      "cubierta_por": [],
      "mas_cercano": {
        "microhub": {
          "id": 2,
          "nombre": "Microhub Valles"
        },
        "distancia_km": 1.62,
        "distancia_calle_km": 2.11,
        "minutos": 9.8,
        "cubre": false,
        "dentro_promesa": true
      },
      "minutos_mejor": null
    },
    {
      "zona": {
        "id": 14,
        "nombre": "Zona 97A5B6 renombrada"
      },
      "hogares": 0,
      "estado": "sin_cobertura",
      "solapada": false,
      "cubierta_por": [],
      "mas_cercano": {
        "microhub": {
          "id": 2,
          "nombre": "Microhub Valles"
        },
        "distancia_km": 1.62,
        "distancia_calle_km": 2.11,
        "minutos": 9.8,
        "cubre": false,
        "dentro_promesa": true
      },
      "minutos_mejor": null
    },
    {
      "zona": {
        "id": 15,
        "nombre": "Zona 1FF3C5 renombrada"
      },
      "hogares": 0,
      "estado": "sin_cobertura",
      "solapada": false,
      "cubierta_por": [],
      "mas_cercano": {
        "microhub": {
          "id": 2,
          "nombre": "Microhub Valles"
        },
        "distancia_km": 1.62,
        "distancia_calle_km": 2.11,
        "minutos": 9.8,
        "cubre": false,
        "dentro_promesa": true
      },
      "minutos_mejor": null
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 7,
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
X-Traza-Id: 818dc8dc-50f5-427d-a873-7f768396d85c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 61 ms · traza `818dc8dc-50f5-427d-a873-7f768396d85c`

```json
{
  "zonas": 7,
  "zonas_cubiertas": 4,
  "pct_zonas": 57.1,
  "hogares": 6709,
  "hogares_cubiertos": 6709,
  "pct_hogares": 100.0,
  "tiempo_promedio_min": 5.5,
  "dentro_promesa_pct": 100.0,
  "zonas_solapadas": 3,
  "zonas_sin_cobertura": [
    {
      "zona": {
        "id": 11,
        "nombre": "Zona D5F75A renombrada"
      },
      "hogares": 0,
      "microhub_mas_cercano": {
        "id": 2,
        "nombre": "Microhub Valles"
      },
      "distancia_km": 1.62
    },
    {
      "zona": {
        "id": 14,
        "nombre": "Zona 97A5B6 renombrada"
      },
      "hogares": 0,
      "microhub_mas_cercano": {
        "id": 2,
        "nombre": "Microhub Valles"
      },
      "distancia_km": 1.62
    },
    {
      "zona": {
        "id": 15,
        "nombre": "Zona 1FF3C5 renombrada"
      },
      "hogares": 0,
      "microhub_mas_cercano": {
        "id": 2,
        "nombre": "Microhub Valles"
      },
      "distancia_km": 1.62
    }
  ],
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
X-Traza-Id: a06138e1-d92a-4605-9a71-0a484f00bee0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 54 ms · traza `a06138e1-d92a-4605-9a71-0a484f00bee0`

```xml
<?xml version='1.0' encoding='utf-8'?>
<cobertura_resumen xmlns="urn:microhubs:v1" version="1"><zonas>7</zonas><zonas_cubiertas>4</zonas_cubiertas><pct_zonas>57.1</pct_zonas><hogares>6709</hogares><hogares_cubiertos>6709</hogares_cubiertos><pct_hogares>100</pct_hogares><tiempo_promedio_min>5.5</tiempo_promedio_min><dentro_promesa_pct>100</dentro_promesa_pct><zonas_solapadas>3</zonas_solapadas><zonas_sin_cobertura><zona_sin_cobertura><zona><id>11</id><nombre>Zona D5F75A renombrada</nombre></zona><hogares>0</hogares><microhub_mas_cercano><id>2</id><nombre>Microhub Valles</nombre></microhub_mas_cercano><distancia_km>1.62</distancia_km></zona_sin_cobertura><zona_sin_cobertura><zona><id>14</id><nombre>Zona 97A5B6 renombrada</nombre></zona><hogares>0</hogares><microhub_mas_cercano><id>2</id><nombre>Microhub Valles</nombre></microhub_mas_cercano><distancia_km>1.62</distancia_km></zona_sin_cobertura><zona_sin_cobertura><zona><id>15</id><nombre>Zona 1FF3C5 renombrada</nombre></zona><hogares>0</hogares><microhub_mas_cercano><id>2</id><nombre>Microhub Valles</nombre></microhub_mas_cercano><distancia_km>1.62</distancia_km></zona_sin_cobertura></zonas_sin_cobertura><microhubs_activos>3</microhubs_activos><supuestos_usados><supuesto><clave>factor_rodeo_distancia</clave><valor>1.3</valor><modificado>false</modificado></supuesto><supuesto><clave>velocidad_reparto_kmh</clave><valor>22</valor><modificado>false</modificado></supuesto><supuesto><clave>tiempo_servicio_min</clave><valor>4</valor><modificado>false</modificado></supuesto><supuesto><clave>cob_tiempo_max_min</clave><valor>30</valor><modificado>false</modificado></supuesto><supuesto><clave>cob_solape_max_pct</clave><valor>40</valor><modificado>false</modificado></supuesto><supuesto><clave>tamano_hogar</clave><valor>3.6</valor><modificado>false</modificado></supuesto></supuestos_usados></cobertura_resumen>
```

### COB-04 · Un punto junto a un microhub · PASA

**Objetivo.** Qué microhubs lo cubren y a qué distancia.

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/punto?latitud=25.748&longitud=-100.364`

```http
Accept: application/json
X-Traza-Id: 806c98d6-a4af-44d8-920f-1fde613a04c9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 49 ms · traza `806c98d6-a4af-44d8-920f-1fde613a04c9`

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
X-Traza-Id: 4ed6b0c6-4cb2-4dd2-a654-85403c9debb1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 57 ms · traza `4ed6b0c6-4cb2-4dd2-a654-85403c9debb1`

```json
{
  "latitud": 26.9,
  "longitud": -101.4,
  "cubierto": false,
  "zona_mas_cercana": {
    "id": 11,
    "nombre": "Zona D5F75A renombrada",
    "distancia_km": 162.24
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
X-Traza-Id: 79df538e-45be-4e08-be05-3a819c6d626d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 7 ms · traza `79df538e-45be-4e08-be05-3a819c6d626d`

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
    "traza_id": "79df538e-45be-4e08-be05-3a819c6d626d"
  }
}
```

### COB-07 · Ubicaciones candidatas con ranking · PASA

**Objetivo.** Cada candidata de planeación frente a la red actual.

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/candidatos`

```http
Accept: application/json
X-Traza-Id: d4837b00-9ceb-4e05-abc5-d4ef23884967
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 240 ms · traza `d4837b00-9ceb-4e05-abc5-d4ef23884967`

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
        "id": 189,
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
        "id": 234,
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
        "id": 236,
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
      "ranking": 7
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
      "ranking": 8
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
      "ranking": 9
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
      "ranking": 10
    },
    {
      "candidato": {
        "id": 248,
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
      "ranking": 12
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
      "ranking": 13
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
      "ranking": 14
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
      "ranking": 15
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
      "ranking": 16
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
      "ranking": 17
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
      "ranking": 18
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
      "zonas_nuevas": 3,
      "hogares_nuevos": 0,
      "hogares_con_mejor_tiempo": 0,
      "minutos_ahorrados": 0.0,
      "solapamiento_pct": 50.0,
      "canibaliza": true,
      "minutos_promedio": 6.6,
      "costo_ultima_milla": 20.89,
      "ranking": 19
    },
    {
      "candidato": {
        "id": 260,
        "clave": "********",
        "nombre": "Ubicación del flujo AB350"
      },
      "latitud": 25.760195,
      "longitud": -100.370891,
      "radio_km": 1.5,
      "zonas_nuevas": 3,
      "hogares_nuevos": 0,
      "hogares_con_mejor_tiempo": 0,
      "minutos_ahorrados": 0.0,
      "solapamiento_pct": 50.0,
      "canibaliza": true,
      "minutos_promedio": 7.1,
      "costo_ultima_milla": 21.43,
      "ranking": 20
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
      "zonas_nuevas": 3,
      "hogares_nuevos": 0,
      "hogares_con_mejor_tiempo": 0,
      "minutos_ahorrados": 0.0,
      "solapamiento_pct": 50.0,
      "canibaliza": true,
      "minutos_promedio": 7.1,
      "costo_ultima_milla": 21.43,
      "ranking": 21
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
      "zonas_nuevas": 3,
      "hogares_nuevos": 0,
      "hogares_con_mejor_tiempo": 0,
      "minutos_ahorrados": 0.0,
      "solapamiento_pct": 50.0,
      "canibaliza": true,
      "minutos_promedio": 7.1,
      "costo_ultima_milla": 21.43,
      "ranking": 22
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
      "ranking": 23
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
      "ranking": 24
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
      "ranking": 25
    }
  ],
  "red_actual": {
    "pct_zonas": 57.1,
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
X-Traza-Id: 79a9fa47-b67d-406c-82df-68f85cc1afc5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "candidato_id": 3
}
```

**Respuesta.** HTTP 200 (esperado 200) · 79 ms · traza `79a9fa47-b67d-406c-82df-68f85cc1afc5`

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
    "pct_zonas": 57.1,
    "pct_hogares": 100.0
  },
  "despues": {
    "pct_zonas": 57.1,
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
X-Traza-Id: cc0ef5ae-bf94-4099-b96d-1f6bb68c89a4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{
  "candidato_id": 3,
  "guardar": true
}
```

**Respuesta.** HTTP 403 (esperado 403) · 87 ms · traza `cc0ef5ae-bf94-4099-b96d-1f6bb68c89a4`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Guardar una evaluación exige el permiso planeacion.editar.",
    "traza_id": "cc0ef5ae-bf94-4099-b96d-1f6bb68c89a4"
  }
}
```

### COB-10 · Guardar la evaluación · PASA

**Objetivo.** Queda en cobertura_evaluacion con su resultado completo.

**Petición.** `POST http://cobertura:5116/api/v1/cobertura/evaluaciones`

```http
Accept: application/json
X-Traza-Id: 85d6f4fd-d9a8-49be-bc20-128bf52ec2ec
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

**Respuesta.** HTTP 201 (esperado 201) · 116 ms · traza `85d6f4fd-d9a8-49be-bc20-128bf52ec2ec`

```json
{
  "id": 28,
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
    "pct_zonas": 57.1,
    "pct_hogares": 100.0
  },
  "despues": {
    "pct_zonas": 57.1,
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
    "id": 28,
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
X-Traza-Id: b2d6545e-a9ef-48e4-8763-f915d6d3473a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 46 ms · traza `b2d6545e-a9ef-48e4-8763-f915d6d3473a`

```json
{
  "datos": [
    {
      "id": 28,
      "nombre": "Evidencia Ola 2",
      "zonas_nuevas": 0,
      "hogares_nuevos": 0,
      "solapamiento_pct": 0.0,
      "canibaliza": false,
      "creado_por": 5,
      "creado_en": "2026-11-26T23:20:47-06:00"
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

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/evaluaciones/28`

```http
Accept: application/json
X-Traza-Id: 46cb9696-1ac9-46f3-b408-52cc0fbd75b8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 25 ms · traza `46cb9696-1ac9-46f3-b408-52cc0fbd75b8`

```json
{
  "id": 28,
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
    "pct_zonas": 57.1,
    "pct_hogares": 100.0
  },
  "despues": {
    "pct_zonas": 57.1,
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
X-Traza-Id: a93f3f61-6208-4cf6-96ed-c90e721d4b35
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

**Respuesta.** HTTP 200 (esperado 200) · 55 ms · traza `a93f3f61-6208-4cf6-96ed-c90e721d4b35`

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
    "pct_zonas": 57.1,
    "pct_hogares": 100.0
  },
  "despues": {
    "pct_zonas": 57.1,
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
X-Traza-Id: fea350b1-59a4-4bfc-881e-e2d99a5f713a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "radio_km": 2
}
```

**Respuesta.** HTTP 422 (esperado 422) · 6 ms · traza `fea350b1-59a4-4bfc-881e-e2d99a5f713a`

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
    "traza_id": "fea350b1-59a4-4bfc-881e-e2d99a5f713a"
  }
}
```

### COB-13 · Escenarios de radio y de rodeo · PASA

**Objetivo.** Cuánto cubre la red con otros radios y otro factor de calle.

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/escenarios?radios=0.5,1,1.5,2&rodeos=1.2,1.5`

```http
Accept: application/json
X-Traza-Id: a594bd77-a033-4d04-b718-bdb7a6e2eb81
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 49 ms · traza `a594bd77-a033-4d04-b718-bdb7a6e2eb81`

```json
{
  "filas": [
    {
      "radio_km": 0.5,
      "rodeo": 1.2,
      "zonas_cubiertas": 3,
      "pct_zonas": 42.9,
      "pct_hogares": 65.1,
      "tiempo_promedio_min": 5.0,
      "dentro_promesa_pct": 100.0
    },
    {
      "radio_km": 1.0,
      "rodeo": 1.2,
      "zonas_cubiertas": 4,
      "pct_zonas": 57.1,
      "pct_hogares": 100.0,
      "tiempo_promedio_min": 5.4,
      "dentro_promesa_pct": 100.0
    },
    {
      "radio_km": 1.5,
      "rodeo": 1.2,
      "zonas_cubiertas": 4,
      "pct_zonas": 57.1,
      "pct_hogares": 100.0,
      "tiempo_promedio_min": 5.4,
      "dentro_promesa_pct": 100.0
    },
    {
      "radio_km": 2.0,
      "rodeo": 1.2,
      "zonas_cubiertas": 7,
      "pct_zonas": 100.0,
      "pct_hogares": 100.0,
      "tiempo_promedio_min": 5.4,
      "dentro_promesa_pct": 100.0
    },
    {
      "radio_km": 0.5,
      "rodeo": 1.5,
      "zonas_cubiertas": 3,
      "pct_zonas": 42.9,
      "pct_hogares": 65.1,
      "tiempo_promedio_min": 5.3,
      "dentro_promesa_pct": 100.0
    },
    {
      "radio_km": 1.0,
      "rodeo": 1.5,
      "zonas_cubiertas": 4,
      "pct_zonas": 57.1,
      "pct_hogares": 100.0,
      "tiempo_promedio_min": 5.7,
      "dentro_promesa_pct": 100.0
    },
    {
      "radio_km": 1.5,
      "rodeo": 1.5,
      "zonas_cubiertas": 4,
      "pct_zonas": 57.1,
      "pct_hogares": 100.0,
      "tiempo_promedio_min": 5.7,
      "dentro_promesa_pct": 100.0
    },
    {
      "radio_km": 2.0,
      "rodeo": 1.5,
      "zonas_cubiertas": 7,
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
X-Traza-Id: 9a7f9371-c020-4585-bd34-31438bfe0925
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "poblacion": 8520,
  "fuente": "INEGI, Censo 2020, AGEB de prueba"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 69 ms · traza `9a7f9371-c020-4585-bd34-31438bfe0925`

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
      "actualizado_en": "2026-11-26T23:19:30.643451-06:00"
    },
    "valores_nuevos": {
      "fuente": "INEGI, Censo 2020, AGEB de prueba",
      "poblacion": 8520,
      "actualizado_en": "2026-11-26T23:20:48.038202-06:00"
    }
  }
]
```

### COB-15 · Corregir la población sin permiso · PASA

**Objetivo.** Es del planeador.

**Petición.** `PUT http://cobertura:5116/api/v1/cobertura/zonas/1/poblacion`

```http
Accept: application/json
X-Traza-Id: 648a9f48-2bb9-49d8-afb1-c438c7864f44
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "poblacion": 1,
  "fuente": "Sin permiso"
}
```

**Respuesta.** HTTP 403 (esperado 403) · 31 ms · traza `648a9f48-2bb9-49d8-afb1-c438c7864f44`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "648a9f48-2bb9-49d8-afb1-c438c7864f44"
  }
}
```

### COB-16 · Supuestos de la cobertura · PASA

**Objetivo.** Rodeo, velocidad, tiempo de servicio, promesa de entrega y tamaño del hogar.

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/supuestos`

```http
Accept: application/json
X-Traza-Id: e67b81b7-d0a6-4a50-8e2f-cf91ba126d9a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 48 ms · traza `e67b81b7-d0a6-4a50-8e2f-cf91ba126d9a`

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
X-Traza-Id: 294204d2-1460-48bf-b74c-2352e2c40509
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 55 ms · traza `294204d2-1460-48bf-b74c-2352e2c40509`

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
      "actualizado_en": "2026-11-26T23:19:31-06:00"
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
    },
    {
      "microhub": {
        "id": 12,
        "nombre": "Microhub AB350"
      },
      "operadores": 2,
      "repartidores": 2,
      "capacidad_fisica": 120,
      "actualizado_en": "2026-11-26T23:11:40-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 7,
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
  },
  {
    "microhub_id": 12,
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
X-Traza-Id: 8e982c85-993c-446d-8bde-648a46c7d05c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 10 ms · traza `8e982c85-993c-446d-8bde-648a46c7d05c`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "8e982c85-993c-446d-8bde-648a46c7d05c"
  }
}
```

### CAP-03 · Capacidad con una carga dada · PASA

**Objetivo.** Capacidad por etapa, utilización, cuello de botella y personal requerido.

**Petición.** `GET http://capacidad:5117/api/v1/capacidad/microhubs/1?carga_dia=60`

```http
Accept: application/json
X-Traza-Id: b7d43a24-5186-450d-a3e0-60fc3eede43b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 62 ms · traza `b7d43a24-5186-450d-a3e0-60fc3eede43b`

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
X-Traza-Id: 4a077c14-f4f1-426b-8e11-1e1d633fc750
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 86 ms · traza `4a077c14-f4f1-426b-8e11-1e1d633fc750`

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
    },
    {
      "microhub": {
        "id": 12,
        "nombre": "Microhub AB350"
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
    "total": 7,
    "paginas": 1
  }
}
```

### CAP-04 · Un microhub saturado · PASA

**Objetivo.** Con 95 % de la capacidad el nivel es de riesgo (umbral 85 %).

**Petición.** `GET http://capacidad:5117/api/v1/capacidad/microhubs/1?carga_dia=140`

```http
Accept: application/json
X-Traza-Id: 6a25f7a2-48cc-4d76-b37b-8d9bc0023af7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 78 ms · traza `6a25f7a2-48cc-4d76-b37b-8d9bc0023af7`

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
X-Traza-Id: 6f61cbd3-3a0f-4002-a75b-c1d787e34180
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 50 ms · traza `6f61cbd3-3a0f-4002-a75b-c1d787e34180`

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
    "traza_id": "6f61cbd3-3a0f-4002-a75b-c1d787e34180"
  }
}
```

### CAP-06 · Capacidad (XML) · PASA

**Objetivo.** Respuesta XML que cumple capacidad.xsd.

**Petición.** `GET http://capacidad:5117/api/v1/capacidad/microhubs/1?carga_dia=60`

```http
Accept: application/xml
X-Traza-Id: f3f8df08-f5d6-4839-9988-0ed795f9e7de
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 68 ms · traza `f3f8df08-f5d6-4839-9988-0ed795f9e7de`

```xml
<?xml version='1.0' encoding='utf-8'?>
<capacidad_microhub xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><operadores>3</operadores><repartidores>3</repartidores><capacidad_fisica>150</capacidad_fisica><horas>10</horas><distancia_km>2.4</distancia_km><carga_dia>60</carga_dia><capacidad_hora>16.36</capacidad_hora><capacidad_dia>150</capacidad_dia><utilizacion_pct>40</utilizacion_pct><nivel>estable</nivel><utilizacion_pico_pct>49.5</utilizacion_pico_pct><nivel_pico>estable</nivel_pico><cuello_botella>espacio físico</cuello_botella><minutos_por_pedido_operacion>11</minutos_por_pedido_operacion><minutos_por_entrega>8.4</minutos_por_entrega><etapas><etapa><etapa>picking</etapa><minutos_por_pedido>6</minutos_por_pedido><pct_tiempo>54.5</pct_tiempo><capacidad_hora>30</capacidad_hora></etapa><etapa><etapa>empaque</etapa><minutos_por_pedido>3</minutos_por_pedido><pct_tiempo>27.3</pct_tiempo><capacidad_hora>60</capacidad_hora></etapa><etapa><etapa>despacho</etapa><minutos_por_pedido>2</minutos_por_pedido><pct_tiempo>18.2</pct_tiempo><capacidad_hora>90</capacidad_hora></etapa><etapa><etapa>reparto</etapa><minutos_por_pedido>8.4</minutos_por_pedido><pct_tiempo xsi:nil="true" /><capacidad_hora>21.5</capacidad_hora></etapa></etapas><operadores_requeridos>2</operadores_requeridos><repartidores_requeridos>1</repartidores_requeridos><holgura_pedidos_dia>90</holgura_pedidos_dia><formula>3 operadores × 5.45 pedidos/h combinados; 3 repartidores × 7.17 entregas/h</formula><supuestos_usados><supuesto><clave>umbral_utilizacion_estable</clave><valor>70</valor><modificado>false</modificado></supuesto><supuesto><clave>umbral_utilizacion_riesgo</clave><valor>85</valor><modificado>false</modificado></supuesto><supuesto><clave>cap_factor_pico</clave><valor>1.35</valor><modificado>false</modificado></supuesto><supuesto><clave>picking_pedidos_hora</clave><valor>10</valor><modificado>false</modificado></supuesto><supuesto><clave>packing_pedidos_hora</clave><valor>20</valor><modificado>false</modificado></supuesto><supuesto><clave>despacho_pedidos_hora</clave><valor>30</valor><modificado>false</modificado></supuesto><supuesto><clave>velocidad_reparto_kmh</clave><valor>22</valor><modificado>false</modificado></supuesto><supuesto><clave>tiempo_servicio_min</clave><valor>4</valor><modificado>false</modificado></supuesto><supuesto><clave>paradas_por_viaje</clave><valor>3</valor><modificado>false</modificado></supuesto></supuestos_usados></capacidad_microhub>
```

### CAP-07 · Simular más personal · PASA

**Objetivo.** Qué pasa con 120 pedidos al día y 6 operadores y 6 repartidores.

**Petición.** `POST http://capacidad:5117/api/v1/capacidad/simulaciones`

```http
Accept: application/json
X-Traza-Id: 47e7dab1-4e72-4789-bc83-ae9c1e722abb
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

**Respuesta.** HTTP 200 (esperado 200) · 48 ms · traza `47e7dab1-4e72-4789-bc83-ae9c1e722abb`

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
X-Traza-Id: 59d10480-cf8e-4031-ba65-bbb381662429
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 47 ms · traza `59d10480-cf8e-4031-ba65-bbb381662429`

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
X-Traza-Id: b75d5cc0-a6a5-47d0-8930-17c50f4edd06
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

**Respuesta.** HTTP 200 (esperado 200) · 59 ms · traza `b75d5cc0-a6a5-47d0-8930-17c50f4edd06`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "operadores": 4,
  "repartidores": 3,
  "capacidad_fisica": 150,
  "actualizado_en": "2026-11-26T23:20:48-06:00"
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
      "actualizado_en": "2026-11-26T23:19:31.556784-06:00"
    },
    "valores_nuevos": {
      "operadores": 4,
      "actualizado_en": "2026-11-26T23:20:48.817675-06:00"
    }
  }
]
```

### CAP-10 · Cambiar el personal sin permiso · PASA

**Objetivo.** El operador no tiene capacidad.editar.

**Petición.** `PUT http://capacidad:5117/api/v1/capacidad/recursos/1`

```http
Accept: application/json
X-Traza-Id: c28beca4-6bab-4ac5-b7c1-63dfadf5e4df
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "operadores": 9,
  "repartidores": 9
}
```

**Respuesta.** HTTP 403 (esperado 403) · 29 ms · traza `c28beca4-6bab-4ac5-b7c1-63dfadf5e4df`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "c28beca4-6bab-4ac5-b7c1-63dfadf5e4df"
  }
}
```

### CAP-11 · Personal inválido · PASA

**Objetivo.** Al menos un operador.

**Petición.** `PUT http://capacidad:5117/api/v1/capacidad/recursos/1`

```http
Accept: application/json
X-Traza-Id: 42a7c1a0-199d-4027-b27d-581465400a25
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "operadores": 0,
  "repartidores": 3
}
```

**Respuesta.** HTTP 422 (esperado 422) · 5 ms · traza `42a7c1a0-199d-4027-b27d-581465400a25`

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
    "traza_id": "42a7c1a0-199d-4027-b27d-581465400a25"
  }
}
```

### CAP-12 · Supuestos de la capacidad · PASA

**Objetivo.** Productividad por etapa, umbrales y horas del turno.

**Petición.** `GET http://capacidad:5117/api/v1/capacidad/supuestos`

```http
Accept: application/json
X-Traza-Id: 6e8e177a-9d71-44c2-9dc4-6d38aab8e49c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 29 ms · traza `6e8e177a-9d71-44c2-9dc4-6d38aab8e49c`

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
X-Traza-Id: 488e0b0f-e6f0-4f7b-b403-e14eae9111eb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 56 ms · traza `488e0b0f-e6f0-4f7b-b403-e14eae9111eb`

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
      "id": 68,
      "ambito": "microhub",
      "ambito_id": 1,
      "nombre": "Prueba escritorio 1795750906",
      "categoria": "otros",
      "tipo": "fijo",
      "unidad": "mes",
      "monto": 10.0,
      "vigente_desde": "2026-10-01",
      "vigente_hasta": null,
      "estatus": "inactivo",
      "fuente": "contrato",
      "justificacion": "Contrato de arrendamiento firmado en septiembre"
    },
    {
      "id": 69,
      "ambito": "microhub",
      "ambito_id": 1,
      "nombre": "Prueba escritorio 1795751146",
      "categoria": "otros",
      "tipo": "fijo",
      "unidad": "mes",
      "monto": 10.0,
      "vigente_desde": "2026-10-01",
      "vigente_hasta": null,
      "estatus": "inactivo",
      "fuente": "contrato",
      "justificacion": "Contrato de arrendamiento firmado en septiembre"
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
    "total": 10,
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
X-Traza-Id: 4a4f2a77-899b-48f6-a158-577b7edf570d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 29 ms · traza `4a4f2a77-899b-48f6-a158-577b7edf570d`

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
X-Traza-Id: 128f8476-e6be-4add-b475-5e723a977cb0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 58 ms · traza `128f8476-e6be-4add-b475-5e723a977cb0`

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
X-Traza-Id: 2c003cd6-720c-4bfe-b4f7-d8bccf7d1d04
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 54 ms · traza `2c003cd6-720c-4bfe-b4f7-d8bccf7d1d04`

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
X-Traza-Id: 2f7e8928-1375-4188-b6eb-cb4f7b6e9e4b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 70 ms · traza `2f7e8928-1375-4188-b6eb-cb4f7b6e9e4b`

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
X-Traza-Id: a1e2789d-ac66-406f-8cc9-2695459e1c5f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 63 ms · traza `a1e2789d-ac66-406f-8cc9-2695459e1c5f`

```xml
<?xml version='1.0' encoding='utf-8'?>
<costos_unitarios xmlns="urn:microhubs:v1" version="1"><entrada><ambito>microhub</ambito><ambito_id>1</ambito_id><origen>costos</origen><pedidos_mes>1800</pedidos_mes><ticket>135.00</ticket><margen_bruto>0.28</margen_bruto><distancia_km>2.4</distancia_km><paradas_por_viaje>3</paradas_por_viaje><valores_modificados /></entrada><fijos_mes>69500.00</fijos_mes><costo_fijo_pedido>38.61</costo_fijo_pedido><variable_pedido>3.50</variable_pedido><comision_pedido>3.92</comision_pedido><costo_entrega>25.20</costo_entrega><costo_variable_pedido>32.62</costo_variable_pedido><costo_por_pedido>71.23</costo_por_pedido><supuestos_usados><supuesto><clave>pedidos_mes</clave><valor>1800</valor><modificado>false</modificado></supuesto><supuesto><clave>ticket</clave><valor>135</valor><modificado>false</modificado></supuesto><supuesto><clave>margen_bruto</clave><valor>0.28</valor><modificado>false</modificado></supuesto><supuesto><clave>distancia_km</clave><valor>2.4</valor><modificado>false</modificado></supuesto><supuesto><clave>paradas_por_viaje</clave><valor>3</valor><modificado>false</modificado></supuesto><supuesto><clave>costo_base_entrega</clave><valor>18</valor><modificado>false</modificado></supuesto><supuesto><clave>costo_km_reparto</clave><valor>4.5</valor><modificado>false</modificado></supuesto></supuestos_usados></costos_unitarios>
```

### COS-07 · El operador consulta costos · PASA

**Objetivo.** Sin costos.ver.

**Petición.** `GET http://costos:5119/api/v1/costos/conceptos`

```http
Accept: application/json
X-Traza-Id: 98482907-a0fe-4436-88c4-411d293e2dec
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 30 ms · traza `98482907-a0fe-4436-88c4-411d293e2dec`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "98482907-a0fe-4436-88c4-411d293e2dec"
  }
}
```

### COS-08 · Alta de un concepto sin permiso · PASA

**Objetivo.** Un auditor consulta, no edita.

**Petición.** `POST http://costos:5119/api/v1/costos/conceptos`

```http
Accept: application/json
X-Traza-Id: b83181e5-ae59-43f9-88a7-b925826fe694
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

**Respuesta.** HTTP 403 (esperado 403) · 25 ms · traza `b83181e5-ae59-43f9-88a7-b925826fe694`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "b83181e5-ae59-43f9-88a7-b925826fe694"
  }
}
```

### COS-09 · Alta de un concepto · PASA

**Objetivo.** Costo fijo de un microhub con su justificación.

**Petición.** `POST http://costos:5119/api/v1/costos/conceptos`

```http
Accept: application/json
X-Traza-Id: 45df5b00-2867-44fa-a70c-6a4e89e4f4a8
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

**Respuesta.** HTTP 201 (esperado 201) · 62 ms · traza `45df5b00-2867-44fa-a70c-6a4e89e4f4a8`

```json
{
  "id": 75,
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
    "id": 75,
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

**Petición.** `PUT http://costos:5119/api/v1/costos/conceptos/75`

```http
Accept: application/json
X-Traza-Id: ba18e2f8-d657-40e1-91d9-d65c58fb7829
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "monto": 1800.0,
  "justificacion": "Se ajustó el monto en la evidencia"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 84 ms · traza `ba18e2f8-d657-40e1-91d9-d65c58fb7829`

```json
{
  "id": 75,
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

**Petición.** `PATCH http://costos:5119/api/v1/costos/conceptos/75`

```http
Accept: application/json
X-Traza-Id: 2a1bde88-d643-4764-853f-1865237537a2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "monto": 1900.0,
  "justificacion": "Segundo ajuste del monto en la evidencia"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 80 ms · traza `2a1bde88-d643-4764-853f-1865237537a2`

```json
{
  "id": 75,
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

**Petición.** `DELETE http://costos:5119/api/v1/costos/conceptos/75`

```http
Accept: application/json
X-Traza-Id: afedbcbf-cb30-49f4-81b3-40dabecfc9f2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 40 ms · traza `afedbcbf-cb30-49f4-81b3-40dabecfc9f2`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT id, estatus FROM costo_concepto WHERE id = %s`

```json
[
  {
    "id": 75,
    "estatus": "inactivo"
  }
]
```

### COS-12 · Fijo con unidad variable · PASA

**Objetivo.** Un costo fijo se da por mes.

**Petición.** `POST http://costos:5119/api/v1/costos/conceptos`

```http
Accept: application/json
X-Traza-Id: e00c074a-c0d0-4f9a-acb9-6eb855723b54
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

**Respuesta.** HTTP 422 (esperado 422) · 7 ms · traza `e00c074a-c0d0-4f9a-acb9-6eb855723b54`

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
    "traza_id": "e00c074a-c0d0-4f9a-acb9-6eb855723b54"
  }
}
```

### COS-13 · Microhub inexistente · PASA

**Objetivo.** El ámbito debe existir.

**Petición.** `POST http://costos:5119/api/v1/costos/conceptos`

```http
Accept: application/json
X-Traza-Id: 86e2b4e4-09dc-48f3-b450-9e15ed9170fa
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

**Respuesta.** HTTP 422 (esperado 422) · 6 ms · traza `86e2b4e4-09dc-48f3-b450-9e15ed9170fa`

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
    "traza_id": "86e2b4e4-09dc-48f3-b450-9e15ed9170fa"
  }
}
```

### COS-14 · Costos de una ubicación candidata · PASA

**Objetivo.** Sin conceptos propios toma renta, nómina y servicios de la ubicación (planeación).

**Petición.** `GET http://costos:5119/api/v1/costos/resumen?candidato_id=3`

```http
Accept: application/json
X-Traza-Id: 15dc9b82-1bc0-4a0f-acfe-5a6440eca3e1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 71 ms · traza `15dc9b82-1bc0-4a0f-acfe-5a6440eca3e1`

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
X-Traza-Id: fa3bedc8-2264-42e8-a10f-c34a7c903e31
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 33 ms · traza `fa3bedc8-2264-42e8-a10f-c34a7c903e31`

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
X-Traza-Id: 746777d3-b9ec-419b-9013-1697f9026e3c
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

**Respuesta.** HTTP 200 (esperado 200) · 35 ms · traza `746777d3-b9ec-419b-9013-1697f9026e3c`

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
X-Traza-Id: c994db95-b557-43a8-93a4-4f90c156b85a
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

**Respuesta.** HTTP 200 (esperado 200) · 29 ms · traza `c994db95-b557-43a8-93a4-4f90c156b85a`

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
X-Traza-Id: 828af057-40d8-4bd2-9028-d5ba7259be6b
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

**Respuesta.** HTTP 200 (esperado 200) · 33 ms · traza `828af057-40d8-4bd2-9028-d5ba7259be6b`

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
X-Traza-Id: fb78408c-2d14-4ce0-9265-8d025773221f
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

**Respuesta.** HTTP 200 (esperado 200) · 30 ms · traza `fb78408c-2d14-4ce0-9265-8d025773221f`

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
X-Traza-Id: ff46d947-a974-400e-8cd4-d592def42c9a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1
}
```

**Respuesta.** HTTP 200 (esperado 200) · 296 ms · traza `ff46d947-a974-400e-8cd4-d592def42c9a`

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
X-Traza-Id: df80c1b9-08d1-493a-8d2d-2579f4ea90d7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "ticket": 200
}
```

**Respuesta.** HTTP 200 (esperado 200) · 275 ms · traza `df80c1b9-08d1-493a-8d2d-2579f4ea90d7`

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
X-Traza-Id: 18a7fc90-6945-4ecf-93ae-e214eb69bbf1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "pedidos_dia": 10
}
```

**Respuesta.** HTTP 422 (esperado 422) · 153 ms · traza `18a7fc90-6945-4ecf-93ae-e214eb69bbf1`

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
    "traza_id": "18a7fc90-6945-4ecf-93ae-e214eb69bbf1"
  }
}
```

### EQU-08 · Sensibilidad · PASA

**Objetivo.** Cada variable sube y baja 10 y 20 %; se ordenan por lo que mueven la utilidad.

**Petición.** `POST http://punto-equilibrio:5120/api/v1/punto-equilibrio/sensibilidad`

```http
Accept: application/json
X-Traza-Id: 94ecc787-8c19-4706-9c72-f4a21c9150d6
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

**Respuesta.** HTTP 200 (esperado 200) · 28 ms · traza `94ecc787-8c19-4706-9c72-f4a21c9150d6`

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
X-Traza-Id: 276e89cd-3e9f-44af-ba60-8b368c6775be
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><equilibrio_calculo_nuevo xmlns="urn:microhubs:v1"><pedidos_dia>45</pedidos_dia><ticket>135</ticket><margen_bruto>0.28</margen_bruto><costos_fijos>60000</costos_fijos><costo_variable_pedido>32.6</costo_variable_pedido></equilibrio_calculo_nuevo>
```

**Respuesta.** HTTP 200 (esperado 200) · 37 ms · traza `276e89cd-3e9f-44af-ba60-8b368c6775be`

```xml
<?xml version='1.0' encoding='utf-8'?>
<equilibrio_calculo xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id xsi:nil="true" /><nombre xsi:nil="true" /><objeto><tipo>manual</tipo><id xsi:nil="true" /><nombre xsi:nil="true" /></objeto><entrada><costos_fijos_mes>60000</costos_fijos_mes><costo_variable_pedido>32.6</costo_variable_pedido><ticket>135</ticket><margen_bruto>0.28</margen_bruto><pedidos_dia>45</pedidos_dia><dias_mes>30</dias_mes><margen_seguridad_minimo_pct>15</margen_seguridad_minimo_pct><origen><costos_fijos>manual</costos_fijos><costo_variable_pedido>manual</costo_variable_pedido><ticket>manual</ticket><margen_bruto>manual</margen_bruto><pedidos_dia>manual</pedidos_dia></origen></entrada><margen_pedido>5.2</margen_pedido><equilibrio_mensual>11538.46</equilibrio_mensual><equilibrio_diario>384.62</equilibrio_diario><ingresos_equilibrio_mes>1557692.31</ingresos_equilibrio_mes><diferencia_pedidos_dia>-339.62</diferencia_pedidos_dia><margen_seguridad_pct>-88.3</margen_seguridad_pct><utilidad_dia>-1766</utilidad_dia><utilidad_mes>-52980</utilidad_mes><decision>no_viable</decision><explicacion><motivo>la demanda esperada (45.0 pedidos/día) no alcanza el equilibrio (384.6 pedidos/día)</motivo></explicacion><pasos><paso>Margen por pedido = ticket × margen bruto − costo de entrega = 135.00 × 28.00% − 32.60 = 5.20</paso><paso>Punto de equilibrio mensual = costos fijos ÷ margen por pedido = 60,000.00 ÷ 5.20 = 11,538 pedidos/mes</paso><paso>Punto de equilibrio diario = 11,538 ÷ 30 días = 384.6 pedidos/día</paso></pasos><supuestos_usados><supuesto><clave>peq_margen_seguridad_pct</clave><valor>15</valor><modificado>false</modificado></supuesto><supuesto><clave>dias_operacion_mes</clave><valor>30</valor><modificado>false</modificado></supuesto><supuesto><clave>margen_bruto_default</clave><valor>0.28</valor><modificado>false</modificado></supuesto></supuestos_usados></equilibrio_calculo>
```

### EQU-10 · Guardar sin permiso · PASA

**Objetivo.** Guardar un escenario exige equilibrio.editar.

**Petición.** `POST http://punto-equilibrio:5120/api/v1/punto-equilibrio/calculos`

```http
Accept: application/json
X-Traza-Id: c3671b50-c614-41fb-94a2-8b3a946396b4
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

**Respuesta.** HTTP 403 (esperado 403) · 8 ms · traza `c3671b50-c614-41fb-94a2-8b3a946396b4`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Guardar un escenario exige el permiso equilibrio.editar.",
    "traza_id": "c3671b50-c614-41fb-94a2-8b3a946396b4"
  }
}
```

### EQU-11 · Guardar «Evidencia equilibrio A» · PASA

**Objetivo.** Queda en equilibrio_escenario con su cálculo completo.

**Petición.** `POST http://punto-equilibrio:5120/api/v1/punto-equilibrio/calculos`

```http
Accept: application/json
X-Traza-Id: 01cd8ffd-fd12-4881-b3e8-855a16e8ab04
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

**Respuesta.** HTTP 201 (esperado 201) · 59 ms · traza `01cd8ffd-fd12-4881-b3e8-855a16e8ab04`

```json
{
  "id": 58,
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
    "id": 58,
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
X-Traza-Id: 6a95b72f-c58f-4940-89f9-9f57d1458ee3
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

**Respuesta.** HTTP 201 (esperado 201) · 57 ms · traza `6a95b72f-c58f-4940-89f9-9f57d1458ee3`

```json
{
  "id": 59,
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
    "id": 59,
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
X-Traza-Id: 3b58e191-de74-4b18-88fd-fa7fb74047c0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 52 ms · traza `3b58e191-de74-4b18-88fd-fa7fb74047c0`

```json
{
  "datos": [
    {
      "id": 59,
      "nombre": "Evidencia equilibrio B",
      "microhub_id": null,
      "candidato_id": null,
      "decision": "viable",
      "equilibrio_diario": 53.33,
      "pedidos_dia": 80.0,
      "utilidad_mes": 20000.0,
      "creado_por": 5,
      "creado_en": "2026-11-26T23:20:50-06:00"
    },
    {
      "id": 58,
      "nombre": "Evidencia equilibrio A",
      "microhub_id": null,
      "candidato_id": null,
      "decision": "no_viable",
      "equilibrio_diario": 53.33,
      "pedidos_dia": 45.0,
      "utilidad_mes": -6250.0,
      "creado_por": 5,
      "creado_en": "2026-11-26T23:20:50-06:00"
    },
    {
      "id": 51,
      "nombre": "Prueba escritorio B 1795751142",
      "microhub_id": null,
      "candidato_id": null,
      "decision": "no_viable",
      "equilibrio_diario": 384.62,
      "pedidos_dia": 60.0,
      "utilidad_mes": -50640.0,
      "creado_por": 5,
      "creado_en": "2026-11-26T21:45:42-06:00"
    },
    {
      "id": 50,
      "nombre": "Prueba escritorio A 1795751142",
      "microhub_id": null,
      "candidato_id": null,
      "decision": "no_viable",
      "equilibrio_diario": 384.62,
      "pedidos_dia": 45.0,
      "utilidad_mes": -52980.0,
      "creado_por": 5,
      "creado_en": "2026-11-26T21:45:42-06:00"
    },
    {
      "id": 49,
      "nombre": "Prueba escritorio B 1795750901",
      "microhub_id": null,
      "candidato_id": null,
      "decision": "no_viable",
      "equilibrio_diario": 384.62,
      "pedidos_dia": 60.0,
      "utilidad_mes": -50640.0,
      "creado_por": 5,
      "creado_en": "2026-11-26T21:41:41-06:00"
    },
    {
      "id": 48,
      "nombre": "Prueba escritorio A 1795750900",
      "microhub_id": null,
      "candidato_id": null,
      "decision": "no_viable",
      "equilibrio_diario": 384.62,
      "pedidos_dia": 45.0,
      "utilidad_mes": -52980.0,
      "creado_por": 5,
      "creado_en": "2026-11-26T21:41:40-06:00"
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

### EQU-14 · Comparar escenarios · PASA

**Objetivo.** Lado a lado: decisión, equilibrio, diferencia y utilidad.

**Petición.** `GET http://punto-equilibrio:5120/api/v1/punto-equilibrio/comparacion?ids=58,59`

```http
Accept: application/json
X-Traza-Id: f8b85b33-1ea5-4827-95f4-859bdb5ffe68
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 41 ms · traza `f8b85b33-1ea5-4827-95f4-859bdb5ffe68`

```json
{
  "filas": [
    {
      "id": 58,
      "nombre": "Evidencia equilibrio A",
      "decision": "no_viable",
      "pedidos_dia": 45.0,
      "equilibrio_diario": 53.33,
      "diferencia_pedidos_dia": -8.33,
      "margen_seguridad_pct": -15.62,
      "utilidad_mes": -6250.0
    },
    {
      "id": 59,
      "nombre": "Evidencia equilibrio B",
      "decision": "viable",
      "pedidos_dia": 80.0,
      "equilibrio_diario": 53.33,
      "diferencia_pedidos_dia": 26.67,
      "margen_seguridad_pct": 50.0,
      "utilidad_mes": 20000.0
    }
  ],
  "mejor_utilidad_id": 59,
  "mejor_utilidad_nombre": "Evidencia equilibrio B"
}
```

### EQU-15 · Abrir un escenario · PASA

**Objetivo.** Con su cálculo paso a paso.

**Petición.** `GET http://punto-equilibrio:5120/api/v1/punto-equilibrio/escenarios/58`

```http
Accept: application/json
X-Traza-Id: d92d447f-31a5-4a76-a09e-ae3b5f67dfbb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 31 ms · traza `d92d447f-31a5-4a76-a09e-ae3b5f67dfbb`

```json
{
  "id": 58,
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

**Petición.** `DELETE http://punto-equilibrio:5120/api/v1/punto-equilibrio/escenarios/58`

```http
Accept: application/json
X-Traza-Id: 0a74341f-fc47-424c-9edf-a941d8255c93
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 31 ms · traza `0a74341f-fc47-424c-9edf-a941d8255c93`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "0a74341f-fc47-424c-9edf-a941d8255c93"
  }
}
```

### EQU-17 · Borrar un escenario · PASA

**Objetivo.** Se elimina el escenario.

**Petición.** `DELETE http://punto-equilibrio:5120/api/v1/punto-equilibrio/escenarios/58`

```http
Accept: application/json
X-Traza-Id: 9528da78-b8d6-49fc-984a-91b1b263bdc1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 34 ms · traza `9528da78-b8d6-49fc-984a-91b1b263bdc1`

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
X-Traza-Id: 40ef87bc-8f2b-4dbc-815a-30d603ee6123
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 348 ms · traza `40ef87bc-8f2b-4dbc-815a-30d603ee6123`

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
X-Traza-Id: 4ad309c0-40f5-4133-be92-97618047dc4f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 29 ms · traza `4ad309c0-40f5-4133-be92-97618047dc4f`

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
X-Traza-Id: 54cb212c-c49c-4be3-aa1c-8e310b08824a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 350 ms · traza `54cb212c-c49c-4be3-aa1c-8e310b08824a`

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
      "productos": 33,
      "unidades": 430,
      "venta": 11317.4,
      "pct_unidades": 80.5,
      "pct_venta": 73.4
    },
    {
      "clase": "B",
      "productos": 12,
      "unidades": 79,
      "venta": 3143.0,
      "pct_unidades": 14.8,
      "pct_venta": 20.4
    },
    {
      "clase": "C",
      "productos": 6,
      "unidades": 25,
      "venta": 966.5,
      "pct_unidades": 4.7,
      "pct_venta": 6.3
    }
  ],
  "filas": [
    {
      "producto": {
        "id": 45,
        "clave_interna": "LI-009",
        "nombre": "Fibra para trastes"
      },
      "clase": "A",
      "unidades": 25,
      "venta": 450.0,
      "pct_acum": 4.7
    },
    {
      "producto": {
        "id": 28,
        "clave_interna": "BE-008",
        "nombre": "Polvo para agua de sabor"
      },
      "clase": "A",
      "unidades": 22,
      "venta": 165.0,
      "pct_acum": 8.8
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
      "pct_acum": 12.5
    },
    {
      "producto": {
        "id": 7,
        "clave_interna": "AB-007",
        "nombre": "Harina de trigo"
      },
      "clase": "A",
      "unidades": 18,
      "venta": 441.0,
      "pct_acum": 15.9
    },
    {
      "producto": {
        "id": 36,
        "clave_interna": "LA-008",
        "nombre": "Jamón de pavo"
      },
      "clase": "A",
      "unidades": 18,
      "venta": 828.0,
      "pct_acum": 19.3
    },
    {
      "producto": {
        "id": 8,
        "clave_interna": "AB-008",
        "nombre": "Pasta para sopa surtida"
      },
      "clase": "A",
      "unidades": 17,
      "venta": 161.5,
      "pct_acum": 22.5
    },
    {
      "producto": {
        "id": 25,
        "clave_interna": "BE-005",
        "nombre": "Jugo de naranja"
      },
      "clase": "A",
      "unidades": 17,
      "venta": 476.0,
      "pct_acum": 25.7
    },
    {
      "producto": {
        "id": 34,
        "clave_interna": "LA-006",
        "nombre": "Yogur natural"
      },
      "clase": "A",
      "unidades": 16,
      "venta": 704.0,
      "pct_acum": 28.7
    },
    {
      "producto": {
        "id": 12,
        "clave_interna": "AB-012",
        "nombre": "Chiles jalapeños en escabeche"
      },
      "clase": "A",
      "unidades": 15,
      "venta": 292.5,
      "pct_acum": 31.5
    },
    {
      "producto": {
        "id": 20,
        "clave_interna": "AB-020",
        "nombre": "Lenteja"
      },
      "clase": "A",
      "unidades": 15,
      "venta": 360.0,
      "pct_acum": 34.3
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
      "pct_acum": 36.9
    },
    {
      "producto": {
        "id": 11,
        "clave_interna": "AB-011",
        "nombre": "Frijoles refritos"
      },
      "clase": "A",
      "unidades": 13,
      "venta": 299.0,
      "pct_acum": 39.3
    },
    {
      "producto": {
        "id": 24,
        "clave_interna": "BE-004",
        "nombre": "Refresco sabor manzana"
      },
      "clase": "A",
      "unidades": 13,
      "venta": 468.0,
      "pct_acum": 41.8
    },
    {
      "producto": {
        "id": 26,
        "clave_interna": "BE-006",
        "nombre": "Bebida de soya"
      },
      "clase": "A",
      "unidades": 13,
      "venta": 416.0,
      "pct_acum": 44.2
    },
    {
      "producto": {
        "id": 29,
        "clave_interna": "LA-001",
        "nombre": "Leche entera"
      },
      "clase": "A",
      "unidades": 13,
      "venta": 357.5,
      "pct_acum": 46.6
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
      "pct_acum": 48.9
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
      "pct_acum": 51.1
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
      "pct_acum": 53.2
    },
    {
      "producto": {
        "id": 6,
        "clave_interna": "AB-006",
        "nombre": "Harina de maíz nixtamalizado"
      },
      "clase": "A",
      "unidades": 11,
      "venta": 286.0,
      "pct_acum": 55.2
    },
    {
      "producto": {
        "id": 16,
        "clave_interna": "AB-016",
        "nombre": "Galletas María"
      },
      "clase": "A",
      "unidades": 11,
      "venta": 181.5,
      "pct_acum": 57.3
    },
    {
      "producto": {
        "id": 22,
        "clave_interna": "BE-002",
        "nombre": "Agua embotellada"
      },
      "clase": "A",
      "unidades": 11,
      "venta": 165.0,
      "pct_acum": 59.4
    },
    {
      "producto": {
        "id": 27,
        "clave_interna": "BE-007",
        "nombre": "Té helado de limón"
      },
      "clase": "A",
      "unidades": 11,
      "venta": 187.0,
      "pct_acum": 61.4
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
      "pct_acum": 63.5
    },
    {
      "producto": {
        "id": 3,
        "clave_interna": "AB-003",
        "nombre": "Aceite vegetal"
      },
      "clase": "A",
      "unidades": 10,
      "venta": 420.0,
      "pct_acum": 65.4
    },
    {
      "producto": {
        "id": 5,
        "clave_interna": "AB-005",
        "nombre": "Sal de mesa"
      },
      "clase": "A",
      "unidades": 10,
      "venta": 140.0,
      "pct_acum": 67.2
    },
    {
      "producto": {
        "id": 40,
        "clave_interna": "LI-004",
        "nombre": "Limpiador multiusos"
      },
      "clase": "A",
      "unidades": 10,
      "venta": 280.0,
      "pct_acum": 69.1
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
      "pct_acum": 71.0
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
      "pct_acum": 72.7
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
      "pct_acum": 74.3
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
      "pct_acum": 76.0
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
      "pct_acum": 77.5
    },
    {
      "producto": {
        "id": 9,
        "clave_interna": "AB-009",
        "nombre": "Atún en agua"
      },
      "clase": "A",
      "unidades": 8,
      "venta": 168.0,
      "pct_acum": 79.0
    },
    {
      "producto": {
        "id": 33,
        "clave_interna": "LA-005",
        "nombre": "Crema ácida"
      },
      "clase": "A",
      "unidades": 8,
      "venta": 288.0,
      "pct_acum": 80.5
    },
    {
      "producto": {
        "id": 50,
        "clave_interna": "HI-005",
        "nombre": "Toallas femeninas"
      },
      "clase": "B",
      "unidades": 8,
      "venta": 288.0,
      "pct_acum": 82.0
    },
    {
      "producto": {
        "id": 51,
        "clave_interna": "HI-006",
        "nombre": "Pañal etapa 3"
      },
      "clase": "B",
      "unidades": 8,
      "venta": 544.0,
      "pct_acum": 83.5
    },
    {
      "producto": {
        "id": 10,
        "clave_interna": "AB-010",
        "nombre": "Sardina en salsa de tomate"
      },
      "clase": "B",
      "unidades": 7,
      "venta": 185.5,
      "pct_acum": 84.8
    },
    {
      "producto": {
        "id": 14,
        "clave_interna": "AB-014",
        "nombre": "Café soluble"
      },
      "clase": "B",
      "unidades": 7,
      "venta": 364.0,
      "pct_acum": 86.1
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
      "pct_acum": 87.5
    },
    {
      "producto": {
        "id": 38,
        "clave_interna": "LI-002",
        "nombre": "Jabón para trastes"
      },
      "clase": "B",
      "unidades": 7,
      "venta": 182.0,
      "pct_acum": 88.8
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
      "pct_acum": 90.1
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
      "pct_acum": 91.4
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
      "pct_acum": 92.5
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
      "pct_acum": 93.4
    },
    {
      "producto": {
        "id": 37,
        "clave_interna": "LI-001",
        "nombre": "Detergente en polvo"
      },
      "clase": "B",
      "unidades": 5,
      "venta": 210.0,
      "pct_acum": 94.4
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
      "pct_acum": 95.3
    },
    {
      "producto": {
        "id": 46,
        "clave_interna": "HI-001",
        "nombre": "Jabón de tocador"
      },
      "clase": "C",
      "unidades": 5,
      "venta": 72.5,
      "pct_acum": 96.3
    },
    {
      "producto": {
        "id": 4,
        "clave_interna": "AB-004",
        "nombre": "Azúcar estándar"
      },
      "clase": "C",
      "unidades": 4,
      "venta": 114.0,
      "pct_acum": 97.0
    },
    {
      "producto": {
        "id": 15,
        "clave_interna": "AB-015",
        "nombre": "Avena en hojuelas"
      },
      "clase": "C",
      "unidades": 4,
      "venta": 108.0,
      "pct_acum": 97.8
    },
    {
      "producto": {
        "id": 21,
        "clave_interna": "BE-001",
        "nombre": "Agua purificada"
      },
      "clase": "C",
      "unidades": 4,
      "venta": 152.0,
      "pct_acum": 98.5
    },
    {
      "producto": {
        "id": 31,
        "clave_interna": "LA-003",
        "nombre": "Queso fresco"
      },
      "clase": "C",
      "unidades": 4,
      "venta": 232.0,
      "pct_acum": 99.3
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
X-Traza-Id: b273589e-cec8-4bcc-8f1c-96d735325f60
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 332 ms · traza `b273589e-cec8-4bcc-8f1c-96d735325f60`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "ventana_dias": 90,
  "resumen": {
    "productos": 51,
    "aumentar": 2,
    "mantener": 0,
    "reducir": 49,
    "eliminar": 0,
    "excluir": 0,
    "clase_a": 33,
    "clase_b": 12,
    "clase_c": 6,
    "unidades_a_comprar": 0,
    "con_costo_estimado": 51,
    "espacio": {
      "total": 3600.0,
      "ocupado": 3835.0,
      "sugerido": 0.0,
      "ocupacion_pct": 106.5
    },
    "presupuesto": {
      "total": 120000.0,
      "requerido": 0.0,
      "uso_pct": 0.0
    }
  },
  "filas": [
    {
      "producto": {
        "id": 45,
        "clave_interna": "LI-009",
        "nombre": "Fibra para trastes"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 4.7,
      "unidades": 25,
      "venta": 450.0,
      "margen_unitario": 5.04,
      "margen_total": 126.0,
      "costo_estimado": true,
      "existencia": 43,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.28,
      "cobertura_dias": 154.8,
      "rotacion": 0.58,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 155 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 28,
        "clave_interna": "BE-008",
        "nombre": "Polvo para agua de sabor"
      },
      "categoria": "Bebidas",
      "clase": "A",
      "pct_acum": 8.8,
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
      "pct_acum": 12.5,
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
        "id": 7,
        "clave_interna": "AB-007",
        "nombre": "Harina de trigo"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 15.9,
      "unidades": 18,
      "venta": 441.0,
      "margen_unitario": 6.86,
      "margen_total": 123.48,
      "costo_estimado": true,
      "existencia": 14,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.2,
      "cobertura_dias": 70.0,
      "rotacion": 1.29,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 70 días, exceso de stock",
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
      "pct_acum": 19.3,
      "unidades": 18,
      "venta": 828.0,
      "margen_unitario": 12.88,
      "margen_total": 231.84,
      "costo_estimado": true,
      "existencia": 30,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.2,
      "cobertura_dias": 150.0,
      "rotacion": 0.6,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 150 días, exceso de stock",
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
      "pct_acum": 22.5,
      "unidades": 17,
      "venta": 161.5,
      "margen_unitario": 2.66,
      "margen_total": 45.22,
      "costo_estimado": true,
      "existencia": 16,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.19,
      "cobertura_dias": 84.7,
      "rotacion": 1.06,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 85 días, exceso de stock",
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
      "pct_acum": 25.7,
      "unidades": 17,
      "venta": 476.0,
      "margen_unitario": 7.84,
      "margen_total": 133.28,
      "costo_estimado": true,
      "existencia": 78,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.19,
      "cobertura_dias": 412.9,
      "rotacion": 0.22,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 413 días, exceso de stock",
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
      "pct_acum": 28.7,
      "unidades": 16,
      "venta": 704.0,
      "margen_unitario": 12.32,
      "margen_total": 197.12,
      "costo_estimado": true,
      "existencia": 10,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.18,
      "cobertura_dias": 56.2,
      "rotacion": 1.6,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 56 días, exceso de stock",
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
      "pct_acum": 31.5,
      "unidades": 15,
      "venta": 292.5,
      "margen_unitario": 5.46,
      "margen_total": 81.9,
      "costo_estimado": true,
      "existencia": 515,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.17,
      "cobertura_dias": 3090.0,
      "rotacion": 0.03,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 3090 días, exceso de stock",
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
      "pct_acum": 34.3,
      "unidades": 15,
      "venta": 360.0,
      "margen_unitario": 6.72,
      "margen_total": 100.8,
      "costo_estimado": true,
      "existencia": 73,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.17,
      "cobertura_dias": 438.0,
      "rotacion": 0.21,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 438 días, exceso de stock",
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
      "pct_acum": 36.9,
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
        "id": 11,
        "clave_interna": "AB-011",
        "nombre": "Frijoles refritos"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 39.3,
      "unidades": 13,
      "venta": 299.0,
      "margen_unitario": 6.44,
      "margen_total": 83.72,
      "costo_estimado": true,
      "existencia": 25,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.14,
      "cobertura_dias": 173.1,
      "rotacion": 0.52,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 173 días, exceso de stock",
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
      "pct_acum": 41.8,
      "unidades": 13,
      "venta": 468.0,
      "margen_unitario": 10.08,
      "margen_total": 131.04,
      "costo_estimado": true,
      "existencia": 39,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.14,
      "cobertura_dias": 270.0,
      "rotacion": 0.33,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 270 días, exceso de stock",
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
      "pct_acum": 44.2,
      "unidades": 13,
      "venta": 416.0,
      "margen_unitario": 8.96,
      "margen_total": 116.48,
      "costo_estimado": true,
      "existencia": 15,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.14,
      "cobertura_dias": 103.8,
      "rotacion": 0.87,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 104 días, exceso de stock",
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
      "pct_acum": 46.6,
      "unidades": 13,
      "venta": 357.5,
      "margen_unitario": 7.7,
      "margen_total": 100.1,
      "costo_estimado": true,
      "existencia": 45,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.14,
      "cobertura_dias": 311.5,
      "rotacion": 0.29,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 312 días, exceso de stock",
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
      "pct_acum": 48.9,
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
        "id": 42,
        "clave_interna": "LI-006",
        "nombre": "Papel higiénico"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 51.1,
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
      "pct_acum": 53.2,
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
        "id": 6,
        "clave_interna": "AB-006",
        "nombre": "Harina de maíz nixtamalizado"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 55.2,
      "unidades": 11,
      "venta": 286.0,
      "margen_unitario": 7.28,
      "margen_total": 80.08,
      "costo_estimado": true,
      "existencia": 88,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.12,
      "cobertura_dias": 720.0,
      "rotacion": 0.12,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 720 días, exceso de stock",
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
      "pct_acum": 57.3,
      "unidades": 11,
      "venta": 181.5,
      "margen_unitario": 4.62,
      "margen_total": 50.82,
      "costo_estimado": true,
      "existencia": 75,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.12,
      "cobertura_dias": 613.6,
      "rotacion": 0.15,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 614 días, exceso de stock",
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
      "pct_acum": 59.4,
      "unidades": 11,
      "venta": 165.0,
      "margen_unitario": 4.2,
      "margen_total": 46.2,
      "costo_estimado": true,
      "existencia": 66,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.12,
      "cobertura_dias": 540.0,
      "rotacion": 0.17,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 540 días, exceso de stock",
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
      "pct_acum": 61.4,
      "unidades": 11,
      "venta": 187.0,
      "margen_unitario": 4.76,
      "margen_total": 52.36,
      "costo_estimado": true,
      "existencia": 84,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.12,
      "cobertura_dias": 687.3,
      "rotacion": 0.13,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 687 días, exceso de stock",
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
      "pct_acum": 63.5,
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
        "id": 3,
        "clave_interna": "AB-003",
        "nombre": "Aceite vegetal"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 65.4,
      "unidades": 10,
      "venta": 420.0,
      "margen_unitario": 11.76,
      "margen_total": 117.6,
      "costo_estimado": true,
      "existencia": 24,
      "minimo": 5,
      "quiebres": 1,
      "demanda_dia": 0.11,
      "cobertura_dias": 216.0,
      "rotacion": 0.42,
      "recomendacion": "Aumentar",
      "motivo": "hubo quiebres",
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
      "pct_acum": 67.2,
      "unidades": 10,
      "venta": 140.0,
      "margen_unitario": 3.92,
      "margen_total": 39.2,
      "costo_estimado": true,
      "existencia": 30,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.11,
      "cobertura_dias": 270.0,
      "rotacion": 0.33,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 270 días, exceso de stock",
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
      "pct_acum": 69.1,
      "unidades": 10,
      "venta": 280.0,
      "margen_unitario": 7.84,
      "margen_total": 78.4,
      "costo_estimado": true,
      "existencia": 12,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.11,
      "cobertura_dias": 108.0,
      "rotacion": 0.83,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 108 días, exceso de stock",
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
      "pct_acum": 71.0,
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
        "id": 18,
        "clave_interna": "AB-018",
        "nombre": "Pan de caja blanco"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 72.7,
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
      "pct_acum": 74.3,
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
      "pct_acum": 76.0,
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
      "pct_acum": 77.5,
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
        "id": 9,
        "clave_interna": "AB-009",
        "nombre": "Atún en agua"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 79.0,
      "unidades": 8,
      "venta": 168.0,
      "margen_unitario": 5.88,
      "margen_total": 47.04,
      "costo_estimado": true,
      "existencia": 42,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 472.5,
      "rotacion": 0.19,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 472 días, exceso de stock",
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
      "pct_acum": 80.5,
      "unidades": 8,
      "venta": 288.0,
      "margen_unitario": 10.08,
      "margen_total": 80.64,
      "costo_estimado": true,
      "existencia": 78,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 877.5,
      "rotacion": 0.1,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 878 días, exceso de stock",
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
      "pct_acum": 82.0,
      "unidades": 8,
      "venta": 288.0,
      "margen_unitario": 10.08,
      "margen_total": 80.64,
      "costo_estimado": true,
      "existencia": 76,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 855.0,
      "rotacion": 0.11,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 855 días, exceso de stock",
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
      "clase": "B",
      "pct_acum": 83.5,
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
        "id": 10,
        "clave_interna": "AB-010",
        "nombre": "Sardina en salsa de tomate"
      },
      "categoria": "Abarrote básico",
      "clase": "B",
      "pct_acum": 84.8,
      "unidades": 7,
      "venta": 185.5,
      "margen_unitario": 7.42,
      "margen_total": 51.94,
      "costo_estimado": true,
      "existencia": 966,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 12420.0,
      "rotacion": 0.01,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 12420 días, exceso de stock",
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
      "pct_acum": 86.1,
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
      "pct_acum": 87.5,
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
        "id": 38,
        "clave_interna": "LI-002",
        "nombre": "Jabón para trastes"
      },
      "categoria": "Limpieza del hogar",
      "clase": "B",
      "pct_acum": 88.8,
      "unidades": 7,
      "venta": 182.0,
      "margen_unitario": 7.28,
      "margen_total": 50.96,
      "costo_estimado": true,
      "existencia": 45,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 578.6,
      "rotacion": 0.16,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 579 días, exceso de stock",
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
      "pct_acum": 90.1,
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
      "pct_acum": 91.4,
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
        "id": 17,
        "clave_interna": "AB-017",
        "nombre": "Tortillas de maíz"
      },
      "categoria": "Abarrote básico",
      "clase": "B",
      "pct_acum": 92.5,
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
        "id": 23,
        "clave_interna": "BE-003",
        "nombre": "Refresco de cola"
      },
      "categoria": "Bebidas",
      "clase": "B",
      "pct_acum": 93.4,
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
        "id": 37,
        "clave_interna": "LI-001",
        "nombre": "Detergente en polvo"
      },
      "categoria": "Limpieza del hogar",
      "clase": "B",
      "pct_acum": 94.4,
      "unidades": 5,
      "venta": 210.0,
      "margen_unitario": 11.76,
      "margen_total": 58.8,
      "costo_estimado": true,
      "existencia": 12,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 216.0,
      "rotacion": 0.42,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 216 días, exceso de stock",
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
      "pct_acum": 95.3,
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
      "clase": "C",
      "pct_acum": 96.3,
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
        "id": 4,
        "clave_interna": "AB-004",
        "nombre": "Azúcar estándar"
      },
      "categoria": "Abarrote básico",
      "clase": "C",
      "pct_acum": 97.0,
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
      "clase": "C",
      "pct_acum": 97.8,
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
        "id": 21,
        "clave_interna": "BE-001",
        "nombre": "Agua purificada"
      },
      "categoria": "Bebidas",
      "clase": "C",
      "pct_acum": 98.5,
      "unidades": 4,
      "venta": 152.0,
      "margen_unitario": 10.64,
      "margen_total": 42.56,
      "costo_estimado": true,
      "existencia": 30,
      "minimo": 10,
      "quiebres": 1,
      "demanda_dia": 0.04,
      "cobertura_dias": 675.0,
      "rotacion": 0.13,
      "recomendacion": "Aumentar",
      "motivo": "hubo quiebres",
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
      "pct_acum": 99.3,
      "unidades": 4,
      "venta": 232.0,
      "margen_unitario": 16.24,
      "margen_total": 64.96,
      "costo_estimado": true,
      "existencia": 217,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.04,
      "cobertura_dias": 4882.5,
      "rotacion": 0.02,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 4882 días, exceso de stock",
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
      "pct_acum": 100.0,
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
X-Traza-Id: 833308ff-b8dc-4a49-bc3e-7846e462e754
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 349 ms · traza `833308ff-b8dc-4a49-bc3e-7846e462e754`

```json
{
  "microhub": null,
  "ventana_dias": 90,
  "resumen": {
    "productos": 51,
    "aumentar": 6,
    "mantener": 0,
    "reducir": 45,
    "eliminar": 0,
    "excluir": 0,
    "clase_a": 36,
    "clase_b": 10,
    "clase_c": 5,
    "unidades_a_comprar": 0,
    "con_costo_estimado": 51,
    "espacio": {
      "total": null,
      "ocupado": 8041.0,
      "sugerido": 0.0,
      "ocupacion_pct": null
    },
    "presupuesto": {
      "total": null,
      "requerido": 0.0,
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
      "pct_acum": 4.3,
      "unidades": 78,
      "venta": 585.0,
      "margen_unitario": 2.1,
      "margen_total": 163.8,
      "costo_estimado": true,
      "existencia": 154,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.87,
      "cobertura_dias": 177.7,
      "rotacion": 0.51,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 178 días, exceso de stock",
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
      "pct_acum": 7.6,
      "unidades": 58,
      "venta": 957.0,
      "margen_unitario": 4.62,
      "margen_total": 267.96,
      "costo_estimado": true,
      "existencia": 142,
      "minimo": 21,
      "quiebres": 0,
      "demanda_dia": 0.64,
      "cobertura_dias": 220.3,
      "rotacion": 0.41,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 220 días, exceso de stock",
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
      "pct_acum": 10.6,
      "unidades": 54,
      "venta": 3672.0,
      "margen_unitario": 19.04,
      "margen_total": 1028.16,
      "costo_estimado": true,
      "existencia": 116,
      "minimo": 20,
      "quiebres": 0,
      "demanda_dia": 0.6,
      "cobertura_dias": 193.3,
      "rotacion": 0.47,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 193 días, exceso de stock",
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
      "pct_acum": 13.5,
      "unidades": 53,
      "venta": 3074.0,
      "margen_unitario": 16.24,
      "margen_total": 860.72,
      "costo_estimado": true,
      "existencia": 368,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.59,
      "cobertura_dias": 624.9,
      "rotacion": 0.14,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 625 días, exceso de stock",
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
      "pct_acum": 16.4,
      "unidades": 52,
      "venta": 936.0,
      "margen_unitario": 5.04,
      "margen_total": 262.08,
      "costo_estimado": true,
      "existencia": 164,
      "minimo": 26,
      "quiebres": 0,
      "demanda_dia": 0.58,
      "cobertura_dias": 283.8,
      "rotacion": 0.32,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 284 días, exceso de stock",
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
      "pct_acum": 19.2,
      "unidades": 50,
      "venta": 2100.0,
      "margen_unitario": 11.76,
      "margen_total": 588.0,
      "costo_estimado": true,
      "existencia": 147,
      "minimo": 21,
      "quiebres": 0,
      "demanda_dia": 0.56,
      "cobertura_dias": 264.6,
      "rotacion": 0.34,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 265 días, exceso de stock",
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
      "pct_acum": 21.8,
      "unidades": 46,
      "venta": 1127.0,
      "margen_unitario": 6.86,
      "margen_total": 315.56,
      "costo_estimado": true,
      "existencia": 154,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.51,
      "cobertura_dias": 301.3,
      "rotacion": 0.3,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 301 días, exceso de stock",
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
      "pct_acum": 24.3,
      "unidades": 46,
      "venta": 3312.0,
      "margen_unitario": 20.16,
      "margen_total": 927.36,
      "costo_estimado": true,
      "existencia": 105,
      "minimo": 28,
      "quiebres": 0,
      "demanda_dia": 0.51,
      "cobertura_dias": 205.4,
      "rotacion": 0.44,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 205 días, exceso de stock",
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
      "pct_acum": 26.8,
      "unidades": 44,
      "venta": 1188.0,
      "margen_unitario": 7.56,
      "margen_total": 332.64,
      "costo_estimado": true,
      "existencia": 153,
      "minimo": 15,
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
        "id": 23,
        "clave_interna": "BE-003",
        "nombre": "Refresco de cola"
      },
      "categoria": "Bebidas",
      "clase": "A",
      "pct_acum": 29.2,
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
        "id": 33,
        "clave_interna": "LA-005",
        "nombre": "Crema ácida"
      },
      "categoria": "Lácteos y huevo",
      "clase": "A",
      "pct_acum": 31.5,
      "unidades": 42,
      "venta": 1512.0,
      "margen_unitario": 10.08,
      "margen_total": 423.36,
      "costo_estimado": true,
      "existencia": 189,
      "minimo": 20,
      "quiebres": 0,
      "demanda_dia": 0.47,
      "cobertura_dias": 405.0,
      "rotacion": 0.22,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 405 días, exceso de stock",
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
      "pct_acum": 33.8,
      "unidades": 41,
      "venta": 1225.9,
      "margen_unitario": 8.37,
      "margen_total": 343.17,
      "costo_estimado": true,
      "existencia": 106,
      "minimo": 25,
      "quiebres": 0,
      "demanda_dia": 0.46,
      "cobertura_dias": 232.7,
      "rotacion": 0.39,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 233 días, exceso de stock",
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
      "pct_acum": 36.1,
      "unidades": 41,
      "venta": 1886.0,
      "margen_unitario": 12.88,
      "margen_total": 528.08,
      "costo_estimado": true,
      "existencia": 86,
      "minimo": 18,
      "quiebres": 0,
      "demanda_dia": 0.46,
      "cobertura_dias": 188.8,
      "rotacion": 0.48,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 189 días, exceso de stock",
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
      "pct_acum": 38.3,
      "unidades": 39,
      "venta": 429.0,
      "margen_unitario": 3.08,
      "margen_total": 120.12,
      "costo_estimado": true,
      "existencia": 82,
      "minimo": 20,
      "quiebres": 2,
      "demanda_dia": 0.43,
      "cobertura_dias": 189.2,
      "rotacion": 0.48,
      "recomendacion": "Aumentar",
      "motivo": "hubo quiebres",
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
      "pct_acum": 40.4,
      "unidades": 39,
      "venta": 1209.0,
      "margen_unitario": 8.68,
      "margen_total": 338.52,
      "costo_estimado": true,
      "existencia": 56,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.43,
      "cobertura_dias": 129.2,
      "rotacion": 0.7,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 129 días, exceso de stock",
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
      "pct_acum": 42.6,
      "unidades": 39,
      "venta": 1716.0,
      "margen_unitario": 12.32,
      "margen_total": 480.48,
      "costo_estimado": true,
      "existencia": 84,
      "minimo": 21,
      "quiebres": 2,
      "demanda_dia": 0.43,
      "cobertura_dias": 193.8,
      "rotacion": 0.46,
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
      "pct_acum": 44.8,
      "unidades": 39,
      "venta": 1092.0,
      "margen_unitario": 7.84,
      "margen_total": 305.76,
      "costo_estimado": true,
      "existencia": 67,
      "minimo": 24,
      "quiebres": 0,
      "demanda_dia": 0.43,
      "cobertura_dias": 154.6,
      "rotacion": 0.58,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 155 días, exceso de stock",
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
      "pct_acum": 46.9,
      "unidades": 38,
      "venta": 1463.0,
      "margen_unitario": 10.78,
      "margen_total": 409.64,
      "costo_estimado": true,
      "existencia": 155,
      "minimo": 25,
      "quiebres": 0,
      "demanda_dia": 0.42,
      "cobertura_dias": 367.1,
      "rotacion": 0.25,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 367 días, exceso de stock",
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
      "pct_acum": 49.0,
      "unidades": 38,
      "venta": 1216.0,
      "margen_unitario": 8.96,
      "margen_total": 340.48,
      "costo_estimado": true,
      "existencia": 49,
      "minimo": 28,
      "quiebres": 1,
      "demanda_dia": 0.42,
      "cobertura_dias": 116.1,
      "rotacion": 0.78,
      "recomendacion": "Aumentar",
      "motivo": "hubo quiebres",
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
      "pct_acum": 51.1,
      "unidades": 37,
      "venta": 888.0,
      "margen_unitario": 6.72,
      "margen_total": 248.64,
      "costo_estimado": true,
      "existencia": 97,
      "minimo": 18,
      "quiebres": 0,
      "demanda_dia": 0.41,
      "cobertura_dias": 235.9,
      "rotacion": 0.38,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 236 días, exceso de stock",
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
      "pct_acum": 53.1,
      "unidades": 37,
      "venta": 1036.0,
      "margen_unitario": 7.84,
      "margen_total": 290.08,
      "costo_estimado": true,
      "existencia": 196,
      "minimo": 15,
      "quiebres": 0,
      "demanda_dia": 0.41,
      "cobertura_dias": 476.8,
      "rotacion": 0.19,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 477 días, exceso de stock",
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
      "pct_acum": 55.2,
      "unidades": 36,
      "venta": 702.0,
      "margen_unitario": 5.46,
      "margen_total": 196.56,
      "costo_estimado": true,
      "existencia": 602,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.4,
      "cobertura_dias": 1505.0,
      "rotacion": 0.06,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1505 días, exceso de stock",
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
      "pct_acum": 57.2,
      "unidades": 36,
      "venta": 612.0,
      "margen_unitario": 4.76,
      "margen_total": 171.36,
      "costo_estimado": true,
      "existencia": 149,
      "minimo": 28,
      "quiebres": 0,
      "demanda_dia": 0.4,
      "cobertura_dias": 372.5,
      "rotacion": 0.24,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 372 días, exceso de stock",
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
      "pct_acum": 59.2,
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
        "id": 8,
        "clave_interna": "AB-008",
        "nombre": "Pasta para sopa surtida"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 61.1,
      "unidades": 35,
      "venta": 332.5,
      "margen_unitario": 2.66,
      "margen_total": 93.1,
      "costo_estimado": true,
      "existencia": 102,
      "minimo": 28,
      "quiebres": 0,
      "demanda_dia": 0.39,
      "cobertura_dias": 262.3,
      "rotacion": 0.34,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 262 días, exceso de stock",
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
      "pct_acum": 63.0,
      "unidades": 34,
      "venta": 1088.0,
      "margen_unitario": 8.96,
      "margen_total": 304.64,
      "costo_estimado": true,
      "existencia": 112,
      "minimo": 25,
      "quiebres": 0,
      "demanda_dia": 0.38,
      "cobertura_dias": 296.5,
      "rotacion": 0.3,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 296 días, exceso de stock",
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
      "pct_acum": 64.9,
      "unidades": 34,
      "venta": 1224.0,
      "margen_unitario": 10.08,
      "margen_total": 342.72,
      "costo_estimado": true,
      "existencia": 148,
      "minimo": 21,
      "quiebres": 0,
      "demanda_dia": 0.38,
      "cobertura_dias": 391.8,
      "rotacion": 0.23,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 392 días, exceso de stock",
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
      "pct_acum": 66.7,
      "unidades": 33,
      "venta": 907.5,
      "margen_unitario": 7.7,
      "margen_total": 254.1,
      "costo_estimado": true,
      "existencia": 127,
      "minimo": 25,
      "quiebres": 0,
      "demanda_dia": 0.37,
      "cobertura_dias": 346.4,
      "rotacion": 0.26,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 346 días, exceso de stock",
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
      "clase": "A",
      "pct_acum": 68.6,
      "unidades": 33,
      "venta": 1386.0,
      "margen_unitario": 11.76,
      "margen_total": 388.08,
      "costo_estimado": true,
      "existencia": 46,
      "minimo": 21,
      "quiebres": 2,
      "demanda_dia": 0.37,
      "cobertura_dias": 125.5,
      "rotacion": 0.72,
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
      "clase": "A",
      "pct_acum": 70.4,
      "unidades": 32,
      "venta": 1344.0,
      "margen_unitario": 11.76,
      "margen_total": 376.32,
      "costo_estimado": true,
      "existencia": 110,
      "minimo": 15,
      "quiebres": 1,
      "demanda_dia": 0.36,
      "cobertura_dias": 309.4,
      "rotacion": 0.29,
      "recomendacion": "Aumentar",
      "motivo": "hubo quiebres",
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
      "pct_acum": 72.1,
      "unidades": 32,
      "venta": 768.0,
      "margen_unitario": 6.72,
      "margen_total": 215.04,
      "costo_estimado": true,
      "existencia": 196,
      "minimo": 20,
      "quiebres": 0,
      "demanda_dia": 0.36,
      "cobertura_dias": 551.2,
      "rotacion": 0.16,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 551 días, exceso de stock",
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
      "pct_acum": 73.9,
      "unidades": 31,
      "venta": 821.5,
      "margen_unitario": 7.42,
      "margen_total": 230.02,
      "costo_estimado": true,
      "existencia": 1072,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.34,
      "cobertura_dias": 3112.3,
      "rotacion": 0.03,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 3112 días, exceso de stock",
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
      "pct_acum": 75.6,
      "unidades": 31,
      "venta": 713.0,
      "margen_unitario": 6.44,
      "margen_total": 199.64,
      "costo_estimado": true,
      "existencia": 126,
      "minimo": 20,
      "quiebres": 0,
      "demanda_dia": 0.34,
      "cobertura_dias": 365.8,
      "rotacion": 0.25,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 366 días, exceso de stock",
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
      "pct_acum": 77.3,
      "unidades": 31,
      "venta": 465.0,
      "margen_unitario": 4.2,
      "margen_total": 130.2,
      "costo_estimado": true,
      "existencia": 170,
      "minimo": 26,
      "quiebres": 0,
      "demanda_dia": 0.34,
      "cobertura_dias": 493.5,
      "rotacion": 0.18,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 494 días, exceso de stock",
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
      "pct_acum": 79.1,
      "unidades": 31,
      "venta": 1674.0,
      "margen_unitario": 15.12,
      "margen_total": 468.72,
      "costo_estimado": true,
      "existencia": 147,
      "minimo": 25,
      "quiebres": 0,
      "demanda_dia": 0.34,
      "cobertura_dias": 426.8,
      "rotacion": 0.21,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 427 días, exceso de stock",
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
      "pct_acum": 80.7,
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
        "id": 41,
        "clave_interna": "LI-005",
        "nombre": "Suavizante de telas"
      },
      "categoria": "Limpieza del hogar",
      "clase": "B",
      "pct_acum": 82.3,
      "unidades": 29,
      "venta": 957.0,
      "margen_unitario": 9.24,
      "margen_total": 267.96,
      "costo_estimado": true,
      "existencia": 140,
      "minimo": 24,
      "quiebres": 0,
      "demanda_dia": 0.32,
      "cobertura_dias": 434.5,
      "rotacion": 0.21,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 434 días, exceso de stock",
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
      "clase": "B",
      "pct_acum": 83.9,
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
        "id": 5,
        "clave_interna": "AB-005",
        "nombre": "Sal de mesa"
      },
      "categoria": "Abarrote básico",
      "clase": "B",
      "pct_acum": 85.5,
      "unidades": 28,
      "venta": 392.0,
      "margen_unitario": 3.92,
      "margen_total": 109.76,
      "costo_estimado": true,
      "existencia": 113,
      "minimo": 21,
      "quiebres": 0,
      "demanda_dia": 0.31,
      "cobertura_dias": 363.2,
      "rotacion": 0.25,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 363 días, exceso de stock",
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
      "clase": "B",
      "pct_acum": 87.0,
      "unidades": 28,
      "venta": 728.0,
      "margen_unitario": 7.28,
      "margen_total": 203.84,
      "costo_estimado": true,
      "existencia": 143,
      "minimo": 18,
      "quiebres": 0,
      "demanda_dia": 0.31,
      "cobertura_dias": 459.6,
      "rotacion": 0.2,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 460 días, exceso de stock",
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
      "clase": "B",
      "pct_acum": 88.5,
      "unidades": 27,
      "venta": 1188.0,
      "margen_unitario": 12.32,
      "margen_total": 332.64,
      "costo_estimado": true,
      "existencia": 157,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.3,
      "cobertura_dias": 523.3,
      "rotacion": 0.17,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 523 días, exceso de stock",
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
      "pct_acum": 90.0,
      "unidades": 27,
      "venta": 594.0,
      "margen_unitario": 6.16,
      "margen_total": 166.32,
      "costo_estimado": true,
      "existencia": 152,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.3,
      "cobertura_dias": 506.7,
      "rotacion": 0.18,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 507 días, exceso de stock",
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
      "clase": "B",
      "pct_acum": 91.5,
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
        "id": 9,
        "clave_interna": "AB-009",
        "nombre": "Atún en agua"
      },
      "categoria": "Abarrote básico",
      "clase": "B",
      "pct_acum": 92.8,
      "unidades": 24,
      "venta": 504.0,
      "margen_unitario": 5.88,
      "margen_total": 141.12,
      "costo_estimado": true,
      "existencia": 129,
      "minimo": 20,
      "quiebres": 0,
      "demanda_dia": 0.27,
      "cobertura_dias": 483.8,
      "rotacion": 0.19,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 484 días, exceso de stock",
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
      "pct_acum": 94.1,
      "unidades": 23,
      "venta": 828.0,
      "margen_unitario": 10.08,
      "margen_total": 231.84,
      "costo_estimado": true,
      "existencia": 91,
      "minimo": 25,
      "quiebres": 0,
      "demanda_dia": 0.26,
      "cobertura_dias": 356.1,
      "rotacion": 0.25,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 356 días, exceso de stock",
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
      "unidades": 23,
      "venta": 333.5,
      "margen_unitario": 4.06,
      "margen_total": 93.38,
      "costo_estimado": true,
      "existencia": 177,
      "minimo": 21,
      "quiebres": 0,
      "demanda_dia": 0.26,
      "cobertura_dias": 692.6,
      "rotacion": 0.13,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 693 días, exceso de stock",
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
      "clase": "C",
      "pct_acum": 96.6,
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
        "id": 6,
        "clave_interna": "AB-006",
        "nombre": "Harina de maíz nixtamalizado"
      },
      "categoria": "Abarrote básico",
      "clase": "C",
      "pct_acum": 97.7,
      "unidades": 20,
      "venta": 520.0,
      "margen_unitario": 7.28,
      "margen_total": 145.6,
      "costo_estimado": true,
      "existencia": 203,
      "minimo": 30,
      "quiebres": 0,
      "demanda_dia": 0.22,
      "cobertura_dias": 913.5,
      "rotacion": 0.1,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 914 días, exceso de stock",
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
      "clase": "C",
      "pct_acum": 98.8,
      "unidades": 20,
      "venta": 960.0,
      "margen_unitario": 13.44,
      "margen_total": 268.8,
      "costo_estimado": true,
      "existencia": 93,
      "minimo": 15,
      "quiebres": 0,
      "demanda_dia": 0.22,
      "cobertura_dias": 418.5,
      "rotacion": 0.22,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 418 días, exceso de stock",
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
      "pct_acum": 99.4,
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
      "unidades": 10,
      "venta": 380.0,
      "margen_unitario": 10.64,
      "margen_total": 106.4,
      "costo_estimado": true,
      "existencia": 30,
      "minimo": 30,
      "quiebres": 5,
      "demanda_dia": 0.11,
      "cobertura_dias": 270.0,
      "rotacion": 0.33,
      "recomendacion": "Aumentar",
      "motivo": "hubo quiebres",
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

### SUR-04 · Solo clase A · PASA

**Objetivo.** Filtro por clase.

**Petición.** `GET http://surtido:5122/api/v1/surtido/analisis?microhub_id=1&clase=A`

```http
Accept: application/json
X-Traza-Id: 04e07cc7-b54b-4585-91d4-d83c24f7f2bd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 386 ms · traza `04e07cc7-b54b-4585-91d4-d83c24f7f2bd`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "ventana_dias": 90,
  "resumen": {
    "productos": 51,
    "aumentar": 2,
    "mantener": 0,
    "reducir": 49,
    "eliminar": 0,
    "excluir": 0,
    "clase_a": 33,
    "clase_b": 12,
    "clase_c": 6,
    "unidades_a_comprar": 0,
    "con_costo_estimado": 51,
    "espacio": {
      "total": 3600.0,
      "ocupado": 3835.0,
      "sugerido": 0.0,
      "ocupacion_pct": 106.5
    },
    "presupuesto": {
      "total": 120000.0,
      "requerido": 0.0,
      "uso_pct": 0.0
    }
  },
  "filas": [
    {
      "producto": {
        "id": 45,
        "clave_interna": "LI-009",
        "nombre": "Fibra para trastes"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 4.7,
      "unidades": 25,
      "venta": 450.0,
      "margen_unitario": 5.04,
      "margen_total": 126.0,
      "costo_estimado": true,
      "existencia": 43,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.28,
      "cobertura_dias": 154.8,
      "rotacion": 0.58,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 155 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 28,
        "clave_interna": "BE-008",
        "nombre": "Polvo para agua de sabor"
      },
      "categoria": "Bebidas",
      "clase": "A",
      "pct_acum": 8.8,
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
      "pct_acum": 12.5,
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
        "id": 7,
        "clave_interna": "AB-007",
        "nombre": "Harina de trigo"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 15.9,
      "unidades": 18,
      "venta": 441.0,
      "margen_unitario": 6.86,
      "margen_total": 123.48,
      "costo_estimado": true,
      "existencia": 14,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.2,
      "cobertura_dias": 70.0,
      "rotacion": 1.29,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 70 días, exceso de stock",
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
      "pct_acum": 19.3,
      "unidades": 18,
      "venta": 828.0,
      "margen_unitario": 12.88,
      "margen_total": 231.84,
      "costo_estimado": true,
      "existencia": 30,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.2,
      "cobertura_dias": 150.0,
      "rotacion": 0.6,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 150 días, exceso de stock",
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
      "pct_acum": 22.5,
      "unidades": 17,
      "venta": 161.5,
      "margen_unitario": 2.66,
      "margen_total": 45.22,
      "costo_estimado": true,
      "existencia": 16,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.19,
      "cobertura_dias": 84.7,
      "rotacion": 1.06,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 85 días, exceso de stock",
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
      "pct_acum": 25.7,
      "unidades": 17,
      "venta": 476.0,
      "margen_unitario": 7.84,
      "margen_total": 133.28,
      "costo_estimado": true,
      "existencia": 78,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.19,
      "cobertura_dias": 412.9,
      "rotacion": 0.22,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 413 días, exceso de stock",
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
      "pct_acum": 28.7,
      "unidades": 16,
      "venta": 704.0,
      "margen_unitario": 12.32,
      "margen_total": 197.12,
      "costo_estimado": true,
      "existencia": 10,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.18,
      "cobertura_dias": 56.2,
      "rotacion": 1.6,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 56 días, exceso de stock",
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
      "pct_acum": 31.5,
      "unidades": 15,
      "venta": 292.5,
      "margen_unitario": 5.46,
      "margen_total": 81.9,
      "costo_estimado": true,
      "existencia": 515,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.17,
      "cobertura_dias": 3090.0,
      "rotacion": 0.03,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 3090 días, exceso de stock",
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
      "pct_acum": 34.3,
      "unidades": 15,
      "venta": 360.0,
      "margen_unitario": 6.72,
      "margen_total": 100.8,
      "costo_estimado": true,
      "existencia": 73,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.17,
      "cobertura_dias": 438.0,
      "rotacion": 0.21,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 438 días, exceso de stock",
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
      "pct_acum": 36.9,
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
        "id": 11,
        "clave_interna": "AB-011",
        "nombre": "Frijoles refritos"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 39.3,
      "unidades": 13,
      "venta": 299.0,
      "margen_unitario": 6.44,
      "margen_total": 83.72,
      "costo_estimado": true,
      "existencia": 25,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.14,
      "cobertura_dias": 173.1,
      "rotacion": 0.52,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 173 días, exceso de stock",
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
      "pct_acum": 41.8,
      "unidades": 13,
      "venta": 468.0,
      "margen_unitario": 10.08,
      "margen_total": 131.04,
      "costo_estimado": true,
      "existencia": 39,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.14,
      "cobertura_dias": 270.0,
      "rotacion": 0.33,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 270 días, exceso de stock",
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
      "pct_acum": 44.2,
      "unidades": 13,
      "venta": 416.0,
      "margen_unitario": 8.96,
      "margen_total": 116.48,
      "costo_estimado": true,
      "existencia": 15,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.14,
      "cobertura_dias": 103.8,
      "rotacion": 0.87,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 104 días, exceso de stock",
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
      "pct_acum": 46.6,
      "unidades": 13,
      "venta": 357.5,
      "margen_unitario": 7.7,
      "margen_total": 100.1,
      "costo_estimado": true,
      "existencia": 45,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.14,
      "cobertura_dias": 311.5,
      "rotacion": 0.29,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 312 días, exceso de stock",
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
      "pct_acum": 48.9,
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
        "id": 42,
        "clave_interna": "LI-006",
        "nombre": "Papel higiénico"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 51.1,
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
      "pct_acum": 53.2,
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
        "id": 6,
        "clave_interna": "AB-006",
        "nombre": "Harina de maíz nixtamalizado"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 55.2,
      "unidades": 11,
      "venta": 286.0,
      "margen_unitario": 7.28,
      "margen_total": 80.08,
      "costo_estimado": true,
      "existencia": 88,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.12,
      "cobertura_dias": 720.0,
      "rotacion": 0.12,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 720 días, exceso de stock",
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
      "pct_acum": 57.3,
      "unidades": 11,
      "venta": 181.5,
      "margen_unitario": 4.62,
      "margen_total": 50.82,
      "costo_estimado": true,
      "existencia": 75,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.12,
      "cobertura_dias": 613.6,
      "rotacion": 0.15,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 614 días, exceso de stock",
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
      "pct_acum": 59.4,
      "unidades": 11,
      "venta": 165.0,
      "margen_unitario": 4.2,
      "margen_total": 46.2,
      "costo_estimado": true,
      "existencia": 66,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.12,
      "cobertura_dias": 540.0,
      "rotacion": 0.17,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 540 días, exceso de stock",
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
      "pct_acum": 61.4,
      "unidades": 11,
      "venta": 187.0,
      "margen_unitario": 4.76,
      "margen_total": 52.36,
      "costo_estimado": true,
      "existencia": 84,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.12,
      "cobertura_dias": 687.3,
      "rotacion": 0.13,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 687 días, exceso de stock",
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
      "pct_acum": 63.5,
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
        "id": 3,
        "clave_interna": "AB-003",
        "nombre": "Aceite vegetal"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 65.4,
      "unidades": 10,
      "venta": 420.0,
      "margen_unitario": 11.76,
      "margen_total": 117.6,
      "costo_estimado": true,
      "existencia": 24,
      "minimo": 5,
      "quiebres": 1,
      "demanda_dia": 0.11,
      "cobertura_dias": 216.0,
      "rotacion": 0.42,
      "recomendacion": "Aumentar",
      "motivo": "hubo quiebres",
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
      "pct_acum": 67.2,
      "unidades": 10,
      "venta": 140.0,
      "margen_unitario": 3.92,
      "margen_total": 39.2,
      "costo_estimado": true,
      "existencia": 30,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.11,
      "cobertura_dias": 270.0,
      "rotacion": 0.33,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 270 días, exceso de stock",
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
      "pct_acum": 69.1,
      "unidades": 10,
      "venta": 280.0,
      "margen_unitario": 7.84,
      "margen_total": 78.4,
      "costo_estimado": true,
      "existencia": 12,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.11,
      "cobertura_dias": 108.0,
      "rotacion": 0.83,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 108 días, exceso de stock",
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
      "pct_acum": 71.0,
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
        "id": 18,
        "clave_interna": "AB-018",
        "nombre": "Pan de caja blanco"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 72.7,
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
      "pct_acum": 74.3,
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
      "pct_acum": 76.0,
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
      "pct_acum": 77.5,
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
        "id": 9,
        "clave_interna": "AB-009",
        "nombre": "Atún en agua"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 79.0,
      "unidades": 8,
      "venta": 168.0,
      "margen_unitario": 5.88,
      "margen_total": 47.04,
      "costo_estimado": true,
      "existencia": 42,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 472.5,
      "rotacion": 0.19,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 472 días, exceso de stock",
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
      "pct_acum": 80.5,
      "unidades": 8,
      "venta": 288.0,
      "margen_unitario": 10.08,
      "margen_total": 80.64,
      "costo_estimado": true,
      "existencia": 78,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 877.5,
      "rotacion": 0.1,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 878 días, exceso de stock",
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
X-Traza-Id: 2a4f0d9f-93c1-4f92-9142-f40ee9839b41
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 6 ms · traza `2a4f0d9f-93c1-4f92-9142-f40ee9839b41`

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
    "traza_id": "2a4f0d9f-93c1-4f92-9142-f40ee9839b41"
  }
}
```

### SUR-06 · Análisis (XML) · PASA

**Objetivo.** Respuesta XML que cumple surtido.xsd.

**Petición.** `GET http://surtido:5122/api/v1/surtido/analisis?microhub_id=1`

```http
Accept: application/xml
X-Traza-Id: 4b1c27b5-68ce-4e3e-9b07-3cb44269461f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 326 ms · traza `4b1c27b5-68ce-4e3e-9b07-3cb44269461f`

```xml
<?xml version='1.0' encoding='utf-8'?>
<surtido_analisis xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><ventana_dias>90</ventana_dias><resumen><productos>51</productos><aumentar>2</aumentar><mantener>0</mantener><reducir>49</reducir><eliminar>0</eliminar><excluir>0</excluir><clase_a>33</clase_a><clase_b>12</clase_b><clase_c>6</clase_c><unidades_a_comprar>0</unidades_a_comprar><con_costo_estimado>51</con_costo_estimado><espacio><total>3600</total><ocupado>3835</ocupado><sugerido>0</sugerido><ocupacion_pct>106.5</ocupacion_pct></espacio><presupuesto><total>120000</total><requerido>0</requerido><uso_pct>0</uso_pct></presupuesto></resumen><filas><fila><producto><id>45</id><clave_interna>LI-009</clave_interna><nombre>Fibra para trastes</nombre></producto><categoria>Limpieza del hogar</categoria><clase>A</clase><pct_acum>4.7</pct_acum><unidades>25</unidades><venta>450</venta><margen_unitario>5.04</margen_unitario><margen_total>126</margen_total><costo_estimado>true</costo_estimado><existencia>43</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.28</demanda_dia><cobertura_dias>154.8</cobertura_dias><rotacion>0.58</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 155 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>28</id><clave_interna>BE-008</clave_interna><nombre>Polvo para agua de sabor</nombre></producto><categoria>Bebidas</categoria><clase>A</clase><pct_acum>8.8</pct_acum><unidades>22</unidades><venta>165</venta><margen_unitario>2.1</margen_unitario><margen_total>46.2</margen_total><costo_estimado>true</costo_estimado><existencia>30</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.24</demanda_dia><cobertura_dias>122.7</cobertura_dias><rotacion>0.73</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 123 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>48</id><clave_interna>HI-003</clave_interna><nombre>Pasta dental</nombre></producto><categoria>Higiene personal</categoria><clase>A</clase><pct_acum>12.5</pct_acum><unidades>20</unidades><venta>640</venta><margen_unitario>8.96</margen_unitario><margen_total>179.2</margen_total><costo_estimado>true</costo_estimado><existencia>74</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.22</demanda_dia><cobertura_dias>333</cobertura_dias><rotacion>0.27</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 333 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>7</id><clave_interna>AB-007</clave_interna><nombre>Harina de trigo</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>15.9</pct_acum><unidades>18</unidades><venta>441</venta><margen_unitario>6.86</margen_unitario><margen_total>123.48</margen_total><costo_estimado>true</costo_estimado><existencia>14</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.2</demanda_dia><cobertura_dias>70</cobertura_dias><rotacion>1.29</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 70 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>36</id><clave_interna>LA-008</clave_interna><nombre>Jamón de pavo</nombre></producto><categoria>Lácteos y huevo</categoria><clase>A</clase><pct_acum>19.3</pct_acum><unidades>18</unidades><venta>828</venta><margen_unitario>12.88</margen_unitario><margen_total>231.84</margen_total><costo_estimado>true</costo_estimado><existencia>30</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.2</demanda_dia><cobertura_dias>150</cobertura_dias><rotacion>0.6</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 150 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>8</id><clave_interna>AB-008</clave_interna><nombre>Pasta para sopa surtida</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>22.5</pct_acum><unidades>17</unidades><venta>161.5</venta><margen_unitario>2.66</margen_unitario><margen_total>45.22</margen_total><costo_estimado>true</costo_estimado><existencia>16</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.19</demanda_dia><cobertura_dias>84.7</cobertura_dias><rotacion>1.06</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 85 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>25</id><clave_interna>BE-005</clave_interna><nombre>Jugo de naranja</nombre></producto><categoria>Bebidas</categoria><clase>A</clase><pct_acum>25.7</pct_acum><unidades>17</unidades><venta>476</venta><margen_unitario>7.84</margen_unitario><margen_total>133.28</margen_total><costo_estimado>true</costo_estimado><existencia>78</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.19</demanda_dia><cobertura_dias>412.9</cobertura_dias><rotacion>0.22</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 413 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>34</id><clave_interna>LA-006</clave_interna><nombre>Yogur natural</nombre></producto><categoria>Lácteos y huevo</categoria><clase>A</clase><pct_acum>28.7</pct_acum><unidades>16</unidades><venta>704</venta><margen_unitario>12.32</margen_unitario><margen_total>197.12</margen_total><costo_estimado>true</costo_estimado><existencia>10</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.18</demanda_dia><cobertura_dias>56.2</cobertura_dias><rotacion>1.6</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 56 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>12</id><clave_interna>AB-012</clave_interna><nombre>Chiles jalapeños en escabeche</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>31.5</pct_acum><unidades>15</unidades><venta>292.5</venta><margen_unitario>5.46</margen_unitario><margen_total>81.9</margen_total><costo_estimado>true</costo_estimado><existencia>515</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.17</demanda_dia><cobertura_dias>3090</cobertura_dias><rotacion>0.03</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 3090 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>20</id><clave_interna>AB-020</clave_interna><nombre>Lenteja</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>34.3</pct_acum><unidades>15</unidades><venta>360</venta><margen_unitario>6.72</margen_unitario><margen_total>100.8</margen_total><costo_estimado>true</costo_estimado><existencia>73</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.17</demanda_dia><cobertura_dias>438</cobertura_dias><rotacion>0.21</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 438 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>13</id><clave_interna>AB-013</clave_interna><nombre>Puré de tomate</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>36.9</pct_acum><unidades>14</unidades><venta>154</venta><margen_unitario>3.08</margen_unitario><margen_total>43.12</margen_total><costo_estimado>true</costo_estimado><existencia>56</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.16</demanda_dia><cobertura_dias>360</cobertura_dias><rotacion>0.25</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 360 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>11</id><clave_interna>AB-011</clave_interna><nombre>Frijoles refritos</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>39.3</pct_acum><unidades>13</unidades><venta>299</venta><margen_unitario>6.44</margen_unitario><margen_total>83.72</margen_total><costo_estimado>true</costo_estimado><existencia>25</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.14</demanda_dia><cobertura_dias>173.1</cobertura_dias><rotacion>0.52</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 173 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>24</id><clave_interna>BE-004</clave_interna><nombre>Refresco sabor manzana</nombre></producto><categoria>Bebidas</categoria><clase>A</clase><pct_acum>41.8</pct_acum><unidades>13</unidades><venta>468</venta><margen_unitario>10.08</margen_unitario><margen_total>131.04</margen_total><costo_estimado>true</costo_estimado><existencia>39</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.14</demanda_dia><cobertura_dias>270</cobertura_dias><rotacion>0.33</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 270 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>26</id><clave_interna>BE-006</clave_interna><nombre>Bebida de soya</nombre></producto><categoria>Bebidas</categoria><clase>A</clase><pct_acum>44.2</pct_acum><unidades>13</unidades><venta>416</venta><margen_unitario>8.96</margen_unitario><margen_total>116.48</margen_total><costo_estimado>true</costo_estimado><existencia>15</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.14</demanda_dia><cobertura_dias>103.8</cobertura_dias><rotacion>0.87</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 104 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>29</id><clave_interna>LA-001</clave_interna><nombre>Leche entera</nombre></producto><categoria>Lácteos y huevo</categoria><clase>A</clase><pct_acum>46.6</pct_acum><unidades>13</unidades><venta>357.5</venta><margen_unitario>7.7</margen_unitario><margen_total>100.1</margen_total><costo_estimado>true</costo_estimado><existencia>45</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.14</demanda_dia><cobertura_dias>311.5</cobertura_dias><rotacion>0.29</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 312 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>30</id><clave_interna>LA-002</clave_interna><nombre>Leche deslactosada</nombre></producto><categoria>Lácteos y huevo</categoria><clase>A</clase><pct_acum>48.9</pct_acum><unidades>12</unidades><venta>372</venta><margen_unitario>8.68</margen_unitario><margen_total>104.16</margen_total><costo_estimado>true</costo_estimado><existencia>12</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.13</demanda_dia><cobertura_dias>90</cobertura_dias><rotacion>1</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 90 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>42</id><clave_interna>LI-006</clave_interna><nombre>Papel higiénico</nombre></producto><categoria>Limpieza del hogar</categoria><clase>A</clase><pct_acum>51.1</pct_acum><unidades>12</unidades><venta>456</venta><margen_unitario>10.64</margen_unitario><margen_total>127.68</margen_total><costo_estimado>true</costo_estimado><existencia>64</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.13</demanda_dia><cobertura_dias>480</cobertura_dias><rotacion>0.19</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 480 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>2</id><clave_interna>AB-002</clave_interna><nombre>Arroz superextra</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>53.2</pct_acum><unidades>11</unidades><venta>328.9</venta><margen_unitario>8.37</margen_unitario><margen_total>92.07</margen_total><costo_estimado>true</costo_estimado><existencia>36</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.12</demanda_dia><cobertura_dias>294.5</cobertura_dias><rotacion>0.31</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 295 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>6</id><clave_interna>AB-006</clave_interna><nombre>Harina de maíz nixtamalizado</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>55.2</pct_acum><unidades>11</unidades><venta>286</venta><margen_unitario>7.28</margen_unitario><margen_total>80.08</margen_total><costo_estimado>true</costo_estimado><existencia>88</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.12</demanda_dia><cobertura_dias>720</cobertura_dias><rotacion>0.12</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 720 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>16</id><clave_interna>AB-016</clave_interna><nombre>Galletas María</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>57.3</pct_acum><unidades>11</unidades><venta>181.5</venta><margen_unitario>4.62</margen_unitario><margen_total>50.82</margen_total><costo_estimado>true</costo_estimado><existencia>75</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.12</demanda_dia><cobertura_dias>613.6</cobertura_dias><rotacion>0.15</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 614 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>22</id><clave_interna>BE-002</clave_interna><nombre>Agua embotellada</nombre></producto><categoria>Bebidas</categoria><clase>A</clase><pct_acum>59.4</pct_acum><unidades>11</unidades><venta>165</venta><margen_unitario>4.2</margen_unitario><margen_total>46.2</margen_total><costo_estimado>true</costo_estimado><existencia>66</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.12</demanda_dia><cobertura_dias>540</cobertura_dias><rotacion>0.17</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 540 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>27</id><clave_interna>BE-007</clave_interna><nombre>Té helado de limón</nombre></producto><categoria>Bebidas</categoria><clase>A</clase><pct_acum>61.4</pct_acum><unidades>11</unidades><venta>187</venta><margen_unitario>4.76</margen_unitario><margen_total>52.36</margen_total><costo_estimado>true</costo_estimado><existencia>84</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.12</demanda_dia><cobertura_dias>687.3</cobertura_dias><rotacion>0.13</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 687 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>39</id><clave_interna>LI-003</clave_interna><nombre>Cloro</nombre></producto><categoria>Limpieza del hogar</categoria><clase>A</clase><pct_acum>63.5</pct_acum><unidades>11</unidades><venta>214.5</venta><margen_unitario>5.46</margen_unitario><margen_total>60.06</margen_total><costo_estimado>true</costo_estimado><existencia>44</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.12</demanda_dia><cobertura_dias>360</cobertura_dias><rotacion>0.25</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 360 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>3</id><clave_interna>AB-003</clave_interna><nombre>Aceite vegetal</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>65.4</pct_acum><unidades>10</unidades><venta>420</venta><margen_unitario>11.76</margen_unitario><margen_total>117.6</margen_total><costo_estimado>true</costo_estimado><existencia>24</existencia><minimo>5</minimo><quiebres>1</quiebres><demanda_dia>0.11</demanda_dia><cobertura_dias>216</cobertura_dias><rotacion>0.42</rotacion><recomendacion>Aumentar</recomendacion><motivo>hubo quiebres</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>5</id><clave_interna>AB-005</clave_interna><nombre>Sal de mesa</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>67.2</pct_acum><unidades>10</unidades><venta>140</venta><margen_unitario>3.92</margen_unitario><margen_total>39.2</margen_total><costo_estimado>true</costo_estimado><existencia>30</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.11</demanda_dia><cobertura_dias>270</cobertura_dias><rotacion>0.33</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 270 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>40</id><clave_interna>LI-004</clave_interna><nombre>Limpiador multiusos</nombre></producto><categoria>Limpieza del hogar</categoria><clase>A</clase><pct_acum>69.1</pct_acum><unidades>10</unidades><venta>280</venta><margen_unitario>7.84</margen_unitario><margen_total>78.4</margen_total><costo_estimado>true</costo_estimado><existencia>12</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.11</demanda_dia><cobertura_dias>108</cobertura_dias><rotacion>0.83</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 108 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>43</id><clave_interna>LI-007</clave_interna><nombre>Servilletas</nombre></producto><categoria>Limpieza del hogar</categoria><clase>A</clase><pct_acum>71</pct_acum><unidades>10</unidades><venta>320</venta><margen_unitario>8.96</margen_unitario><margen_total>89.6</margen_total><costo_estimado>true</costo_estimado><existencia>65</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.11</demanda_dia><cobertura_dias>585</cobertura_dias><rotacion>0.15</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 585 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>18</id><clave_interna>AB-018</clave_interna><nombre>Pan de caja blanco</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>72.7</pct_acum><unidades>9</unidades><venta>396</venta><margen_unitario>12.32</margen_unitario><margen_total>110.88</margen_total><costo_estimado>true</costo_estimado><existencia>78</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.1</demanda_dia><cobertura_dias>780</cobertura_dias><rotacion>0.12</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 780 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>19</id><clave_interna>AB-019</clave_interna><nombre>Huevo blanco</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>74.3</pct_acum><unidades>9</unidades><venta>378</venta><margen_unitario>11.76</margen_unitario><margen_total>105.84</margen_total><costo_estimado>true</costo_estimado><existencia>49</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.1</demanda_dia><cobertura_dias>490</cobertura_dias><rotacion>0.18</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 490 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>44</id><clave_interna>LI-008</clave_interna><nombre>Bolsas para basura</nombre></producto><categoria>Limpieza del hogar</categoria><clase>A</clase><pct_acum>76</pct_acum><unidades>9</unidades><venta>216</venta><margen_unitario>6.72</margen_unitario><margen_total>60.48</margen_total><costo_estimado>true</costo_estimado><existencia>26</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.1</demanda_dia><cobertura_dias>260</cobertura_dias><rotacion>0.35</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 260 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>1</id><clave_interna>AB-001</clave_interna><nombre>Frijol negro a granel</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>77.5</pct_acum><unidades>8</unidades><venta>308</venta><margen_unitario>10.78</margen_unitario><margen_total>86.24</margen_total><costo_estimado>true</costo_estimado><existencia>58</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.09</demanda_dia><cobertura_dias>652.5</cobertura_dias><rotacion>0.14</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 652 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>9</id><clave_interna>AB-009</clave_interna><nombre>Atún en agua</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>79</pct_acum><unidades>8</unidades><venta>168</venta><margen_unitario>5.88</margen_unitario><margen_total>47.04</margen_total><costo_estimado>true</costo_estimado><existencia>42</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.09</demanda_dia><cobertura_dias>472.5</cobertura_dias><rotacion>0.19</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 472 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>33</id><clave_interna>LA-005</clave_interna><nombre>Crema ácida</nombre></producto><categoria>Lácteos y huevo</categoria><clase>A</clase><pct_acum>80.5</pct_acum><unidades>8</unidades><venta>288</venta><margen_unitario>10.08</margen_unitario><margen_total>80.64</margen_total><costo_estimado>true</costo_estimado><existencia>78</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.09</demanda_dia><cobertura_dias>877.5</cobertura_dias><rotacion>0.1</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 878 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>50</id><clave_interna>HI-005</clave_interna><nombre>Toallas femeninas</nombre></producto><categoria>Higiene personal</categoria><clase>B</clase><pct_acum>82</pct_acum><unidades>8</unidades><venta>288</venta><margen_unitario>10.08</margen_unitario><margen_total>80.64</margen_total><costo_estimado>true</costo_estimado><existencia>76</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.09</demanda_dia><cobertura_dias>855</cobertura_dias><rotacion>0.11</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 855 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>51</id><clave_interna>HI-006</clave_interna><nombre>Pañal etapa 3</nombre></producto><categoria>Higiene personal</categoria><clase>B</clase><pct_acum>83.5</pct_acum><unidades>8</unidades><venta>544</venta><margen_unitario>19.04</margen_unitario><margen_total>152.32</margen_total><costo_estimado>true</costo_estimado><existencia>29</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.09</demanda_dia><cobertura_dias>326.2</cobertura_dias><rotacion>0.28</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 326 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>10</id><clave_interna>AB-010</clave_interna><nombre>Sardina en salsa de tomate</nombre></producto><categoria>Abarrote básico</categoria><clase>B</clase><pct_acum>84.8</pct_acum><unidades>7</unidades><venta>185.5</venta><margen_unitario>7.42</margen_unitario><margen_total>51.94</margen_total><costo_estimado>true</costo_estimado><existencia>966</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.08</demanda_dia><cobertura_dias>12420</cobertura_dias><rotacion>0.01</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 12420 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>14</id><clave_interna>AB-014</clave_interna><nombre>Café soluble</nombre></producto><categoria>Abarrote básico</categoria><clase>B</clase><pct_acum>86.1</pct_acum><unidades>7</unidades><venta>364</venta><margen_unitario>14.56</margen_unitario><margen_total>101.92</margen_total><costo_estimado>true</costo_estimado><existencia>33</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.08</demanda_dia><cobertura_dias>424.3</cobertura_dias><rotacion>0.21</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 424 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>35</id><clave_interna>LA-007</clave_interna><nombre>Mantequilla</nombre></producto><categoria>Lácteos y huevo</categoria><clase>B</clase><pct_acum>87.5</pct_acum><unidades>7</unidades><venta>154</venta><margen_unitario>6.16</margen_unitario><margen_total>43.12</margen_total><costo_estimado>true</costo_estimado><existencia>64</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.08</demanda_dia><cobertura_dias>822.9</cobertura_dias><rotacion>0.11</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 823 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>38</id><clave_interna>LI-002</clave_interna><nombre>Jabón para trastes</nombre></producto><categoria>Limpieza del hogar</categoria><clase>B</clase><pct_acum>88.8</pct_acum><unidades>7</unidades><venta>182</venta><margen_unitario>7.28</margen_unitario><margen_total>50.96</margen_total><costo_estimado>true</costo_estimado><existencia>45</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.08</demanda_dia><cobertura_dias>578.6</cobertura_dias><rotacion>0.16</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 579 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>47</id><clave_interna>HI-002</clave_interna><nombre>Shampoo</nombre></producto><categoria>Higiene personal</categoria><clase>B</clase><pct_acum>90.1</pct_acum><unidades>7</unidades><venta>378</venta><margen_unitario>15.12</margen_unitario><margen_total>105.84</margen_total><costo_estimado>true</costo_estimado><existencia>36</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.08</demanda_dia><cobertura_dias>462.9</cobertura_dias><rotacion>0.19</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 463 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>49</id><clave_interna>HI-004</clave_interna><nombre>Desodorante</nombre></producto><categoria>Higiene personal</categoria><clase>B</clase><pct_acum>91.4</pct_acum><unidades>7</unidades><venta>336</venta><margen_unitario>13.44</margen_unitario><margen_total>94.08</margen_total><costo_estimado>true</costo_estimado><existencia>36</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.08</demanda_dia><cobertura_dias>462.9</cobertura_dias><rotacion>0.19</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 463 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>17</id><clave_interna>AB-017</clave_interna><nombre>Tortillas de maíz</nombre></producto><categoria>Abarrote básico</categoria><clase>B</clase><pct_acum>92.5</pct_acum><unidades>6</unidades><venta>144</venta><margen_unitario>6.72</margen_unitario><margen_total>40.32</margen_total><costo_estimado>true</costo_estimado><existencia>21</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.07</demanda_dia><cobertura_dias>315</cobertura_dias><rotacion>0.29</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 315 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>23</id><clave_interna>BE-003</clave_interna><nombre>Refresco de cola</nombre></producto><categoria>Bebidas</categoria><clase>B</clase><pct_acum>93.4</pct_acum><unidades>5</unidades><venta>192.5</venta><margen_unitario>10.78</margen_unitario><margen_total>53.9</margen_total><costo_estimado>true</costo_estimado><existencia>54</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>972</cobertura_dias><rotacion>0.09</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 972 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>37</id><clave_interna>LI-001</clave_interna><nombre>Detergente en polvo</nombre></producto><categoria>Limpieza del hogar</categoria><clase>B</clase><pct_acum>94.4</pct_acum><unidades>5</unidades><venta>210</venta><margen_unitario>11.76</margen_unitario><margen_total>58.8</margen_total><costo_estimado>true</costo_estimado><existencia>12</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>216</cobertura_dias><rotacion>0.42</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 216 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>41</id><clave_interna>LI-005</clave_interna><nombre>Suavizante de telas</nombre></producto><categoria>Limpieza del hogar</categoria><clase>B</clase><pct_acum>95.3</pct_acum><unidades>5</unidades><venta>165</venta><margen_unitario>9.24</margen_unitario><margen_total>46.2</margen_total><costo_estimado>true</costo_estimado><existencia>69</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>1242</cobertura_dias><rotacion>0.07</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1242 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>46</id><clave_interna>HI-001</clave_interna><nombre>Jabón de tocador</nombre></producto><categoria>Higiene personal</categoria><clase>C</clase><pct_acum>96.3</pct_acum><unidades>5</unidades><venta>72.5</venta><margen_unitario>4.06</margen_unitario><margen_total>20.3</margen_total><costo_estimado>true</costo_estimado><existencia>63</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>1134</cobertura_dias><rotacion>0.08</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1134 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>4</id><clave_interna>AB-004</clave_interna><nombre>Azúcar estándar</nombre></producto><categoria>Abarrote básico</categoria><clase>C</clase><pct_acum>97</pct_acum><unidades>4</unidades><venta>114</venta><margen_unitario>7.98</margen_unitario><margen_total>31.92</margen_total><costo_estimado>true</costo_estimado><existencia>18</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.04</demanda_dia><cobertura_dias>405</cobertura_dias><rotacion>0.22</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 405 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>15</id><clave_interna>AB-015</clave_interna><nombre>Avena en hojuelas</nombre></producto><categoria>Abarrote básico</categoria><clase>C</clase><pct_acum>97.8</pct_acum><unidades>4</unidades><venta>108</venta><margen_unitario>7.56</margen_unitario><margen_total>30.24</margen_total><costo_estimado>true</costo_estimado><existencia>52</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.04</demanda_dia><cobertura_dias>1170</cobertura_dias><rotacion>0.08</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1170 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>21</id><clave_interna>BE-001</clave_interna><nombre>Agua purificada</nombre></producto><categoria>Bebidas</categoria><clase>C</clase><pct_acum>98.5</pct_acum><unidades>4</unidades><venta>152</venta><margen_unitario>10.64</margen_unitario><margen_total>42.56</margen_total><costo_estimado>true</costo_estimado><existencia>30</existencia><minimo>10</minimo><quiebres>1</quiebres><demanda_dia>0.04</demanda_dia><cobertura_dias>675</cobertura_dias><rotacion>0.13</rotacion><recomendacion>Aumentar</recomendacion><motivo>hubo quiebres</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>31</id><clave_interna>LA-003</clave_interna><nombre>Queso fresco</nombre></producto><categoria>Lácteos y huevo</categoria><clase>C</clase><pct_acum>99.3</pct_acum><unidades>4</unidades><venta>232</venta><margen_unitario>16.24</margen_unitario><margen_total>64.96</margen_total><costo_estimado>true</costo_estimado><existencia>217</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.04</demanda_dia><cobertura_dias>4882.5</cobertura_dias><rotacion>0.02</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 4882 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>32</id><clave_interna>LA-004</clave_interna><nombre>Queso Oaxaca</nombre></producto><categoria>Lácteos y huevo</categoria><clase>C</clase><pct_acum>100</pct_acum><unidades>4</unidades><venta>288</venta><margen_unitario>20.16</margen_unitario><margen_total>80.64</margen_total><costo_estimado>true</costo_estimado><existencia>20</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.04</demanda_dia><cobertura_dias>450</cobertura_dias><rotacion>0.2</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 450 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila></filas><supuestos_usados><supuesto><clave>abc_a_pct</clave><valor>80</valor><modificado>false</modificado></supuesto><supuesto><clave>abc_b_pct</clave><valor>95</valor><modificado>false</modificado></supuesto><supuesto><clave>cobertura_dias_a</clave><valor>7</valor><modificado>false</modificado></supuesto><supuesto><clave>cobertura_dias_b</clave><valor>5</valor><modificado>false</modificado></supuesto><supuesto><clave>cobertura_dias_c</clave><valor>3</valor><modificado>false</modificado></supuesto><supuesto><clave>cobertura_dias_exceso</clave><valor>30</valor><modificado>false</modificado></supuesto><supuesto><clave>ventana_analisis_dias</clave><valor>90</valor><modificado>false</modificado></supuesto></supuestos_usados></surtido_analisis>
```

### SUR-07 · El operador analiza su microhub · PASA

**Objetivo.** Operador y supervisor solo trabajan con el suyo.

**Petición.** `GET http://surtido:5122/api/v1/surtido/analisis?microhub_id=1`

```http
Accept: application/json
X-Traza-Id: 7068dff6-f5a2-4c37-a693-5a4edf63484e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 315 ms · traza `7068dff6-f5a2-4c37-a693-5a4edf63484e`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "ventana_dias": 90,
  "resumen": {
    "productos": 51,
    "aumentar": 2,
    "mantener": 0,
    "reducir": 49,
    "eliminar": 0,
    "excluir": 0,
    "clase_a": 33,
    "clase_b": 12,
    "clase_c": 6,
    "unidades_a_comprar": 0,
    "con_costo_estimado": 51,
    "espacio": {
      "total": 3600.0,
      "ocupado": 3835.0,
      "sugerido": 0.0,
      "ocupacion_pct": 106.5
    },
    "presupuesto": {
      "total": 120000.0,
      "requerido": 0.0,
      "uso_pct": 0.0
    }
  },
  "filas": [
    {
      "producto": {
        "id": 45,
        "clave_interna": "LI-009",
        "nombre": "Fibra para trastes"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 4.7,
      "unidades": 25,
      "venta": 450.0,
      "margen_unitario": 5.04,
      "margen_total": 126.0,
      "costo_estimado": true,
      "existencia": 43,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.28,
      "cobertura_dias": 154.8,
      "rotacion": 0.58,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 155 días, exceso de stock",
      "sugerido": 0,
      "limitado_por": null
    },
    {
      "producto": {
        "id": 28,
        "clave_interna": "BE-008",
        "nombre": "Polvo para agua de sabor"
      },
      "categoria": "Bebidas",
      "clase": "A",
      "pct_acum": 8.8,
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
      "pct_acum": 12.5,
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
        "id": 7,
        "clave_interna": "AB-007",
        "nombre": "Harina de trigo"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 15.9,
      "unidades": 18,
      "venta": 441.0,
      "margen_unitario": 6.86,
      "margen_total": 123.48,
      "costo_estimado": true,
      "existencia": 14,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.2,
      "cobertura_dias": 70.0,
      "rotacion": 1.29,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 70 días, exceso de stock",
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
      "pct_acum": 19.3,
      "unidades": 18,
      "venta": 828.0,
      "margen_unitario": 12.88,
      "margen_total": 231.84,
      "costo_estimado": true,
      "existencia": 30,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.2,
      "cobertura_dias": 150.0,
      "rotacion": 0.6,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 150 días, exceso de stock",
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
      "pct_acum": 22.5,
      "unidades": 17,
      "venta": 161.5,
      "margen_unitario": 2.66,
      "margen_total": 45.22,
      "costo_estimado": true,
      "existencia": 16,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.19,
      "cobertura_dias": 84.7,
      "rotacion": 1.06,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 85 días, exceso de stock",
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
      "pct_acum": 25.7,
      "unidades": 17,
      "venta": 476.0,
      "margen_unitario": 7.84,
      "margen_total": 133.28,
      "costo_estimado": true,
      "existencia": 78,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.19,
      "cobertura_dias": 412.9,
      "rotacion": 0.22,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 413 días, exceso de stock",
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
      "pct_acum": 28.7,
      "unidades": 16,
      "venta": 704.0,
      "margen_unitario": 12.32,
      "margen_total": 197.12,
      "costo_estimado": true,
      "existencia": 10,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.18,
      "cobertura_dias": 56.2,
      "rotacion": 1.6,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 56 días, exceso de stock",
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
      "pct_acum": 31.5,
      "unidades": 15,
      "venta": 292.5,
      "margen_unitario": 5.46,
      "margen_total": 81.9,
      "costo_estimado": true,
      "existencia": 515,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.17,
      "cobertura_dias": 3090.0,
      "rotacion": 0.03,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 3090 días, exceso de stock",
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
      "pct_acum": 34.3,
      "unidades": 15,
      "venta": 360.0,
      "margen_unitario": 6.72,
      "margen_total": 100.8,
      "costo_estimado": true,
      "existencia": 73,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.17,
      "cobertura_dias": 438.0,
      "rotacion": 0.21,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 438 días, exceso de stock",
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
      "pct_acum": 36.9,
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
        "id": 11,
        "clave_interna": "AB-011",
        "nombre": "Frijoles refritos"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 39.3,
      "unidades": 13,
      "venta": 299.0,
      "margen_unitario": 6.44,
      "margen_total": 83.72,
      "costo_estimado": true,
      "existencia": 25,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.14,
      "cobertura_dias": 173.1,
      "rotacion": 0.52,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 173 días, exceso de stock",
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
      "pct_acum": 41.8,
      "unidades": 13,
      "venta": 468.0,
      "margen_unitario": 10.08,
      "margen_total": 131.04,
      "costo_estimado": true,
      "existencia": 39,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.14,
      "cobertura_dias": 270.0,
      "rotacion": 0.33,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 270 días, exceso de stock",
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
      "pct_acum": 44.2,
      "unidades": 13,
      "venta": 416.0,
      "margen_unitario": 8.96,
      "margen_total": 116.48,
      "costo_estimado": true,
      "existencia": 15,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.14,
      "cobertura_dias": 103.8,
      "rotacion": 0.87,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 104 días, exceso de stock",
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
      "pct_acum": 46.6,
      "unidades": 13,
      "venta": 357.5,
      "margen_unitario": 7.7,
      "margen_total": 100.1,
      "costo_estimado": true,
      "existencia": 45,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.14,
      "cobertura_dias": 311.5,
      "rotacion": 0.29,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 312 días, exceso de stock",
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
      "pct_acum": 48.9,
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
        "id": 42,
        "clave_interna": "LI-006",
        "nombre": "Papel higiénico"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 51.1,
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
      "pct_acum": 53.2,
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
        "id": 6,
        "clave_interna": "AB-006",
        "nombre": "Harina de maíz nixtamalizado"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 55.2,
      "unidades": 11,
      "venta": 286.0,
      "margen_unitario": 7.28,
      "margen_total": 80.08,
      "costo_estimado": true,
      "existencia": 88,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.12,
      "cobertura_dias": 720.0,
      "rotacion": 0.12,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 720 días, exceso de stock",
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
      "pct_acum": 57.3,
      "unidades": 11,
      "venta": 181.5,
      "margen_unitario": 4.62,
      "margen_total": 50.82,
      "costo_estimado": true,
      "existencia": 75,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.12,
      "cobertura_dias": 613.6,
      "rotacion": 0.15,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 614 días, exceso de stock",
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
      "pct_acum": 59.4,
      "unidades": 11,
      "venta": 165.0,
      "margen_unitario": 4.2,
      "margen_total": 46.2,
      "costo_estimado": true,
      "existencia": 66,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.12,
      "cobertura_dias": 540.0,
      "rotacion": 0.17,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 540 días, exceso de stock",
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
      "pct_acum": 61.4,
      "unidades": 11,
      "venta": 187.0,
      "margen_unitario": 4.76,
      "margen_total": 52.36,
      "costo_estimado": true,
      "existencia": 84,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.12,
      "cobertura_dias": 687.3,
      "rotacion": 0.13,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 687 días, exceso de stock",
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
      "pct_acum": 63.5,
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
        "id": 3,
        "clave_interna": "AB-003",
        "nombre": "Aceite vegetal"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 65.4,
      "unidades": 10,
      "venta": 420.0,
      "margen_unitario": 11.76,
      "margen_total": 117.6,
      "costo_estimado": true,
      "existencia": 24,
      "minimo": 5,
      "quiebres": 1,
      "demanda_dia": 0.11,
      "cobertura_dias": 216.0,
      "rotacion": 0.42,
      "recomendacion": "Aumentar",
      "motivo": "hubo quiebres",
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
      "pct_acum": 67.2,
      "unidades": 10,
      "venta": 140.0,
      "margen_unitario": 3.92,
      "margen_total": 39.2,
      "costo_estimado": true,
      "existencia": 30,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.11,
      "cobertura_dias": 270.0,
      "rotacion": 0.33,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 270 días, exceso de stock",
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
      "pct_acum": 69.1,
      "unidades": 10,
      "venta": 280.0,
      "margen_unitario": 7.84,
      "margen_total": 78.4,
      "costo_estimado": true,
      "existencia": 12,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.11,
      "cobertura_dias": 108.0,
      "rotacion": 0.83,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 108 días, exceso de stock",
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
      "pct_acum": 71.0,
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
        "id": 18,
        "clave_interna": "AB-018",
        "nombre": "Pan de caja blanco"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 72.7,
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
      "pct_acum": 74.3,
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
      "pct_acum": 76.0,
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
      "pct_acum": 77.5,
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
        "id": 9,
        "clave_interna": "AB-009",
        "nombre": "Atún en agua"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 79.0,
      "unidades": 8,
      "venta": 168.0,
      "margen_unitario": 5.88,
      "margen_total": 47.04,
      "costo_estimado": true,
      "existencia": 42,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 472.5,
      "rotacion": 0.19,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 472 días, exceso de stock",
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
      "pct_acum": 80.5,
      "unidades": 8,
      "venta": 288.0,
      "margen_unitario": 10.08,
      "margen_total": 80.64,
      "costo_estimado": true,
      "existencia": 78,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 877.5,
      "rotacion": 0.1,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 878 días, exceso de stock",
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
      "pct_acum": 82.0,
      "unidades": 8,
      "venta": 288.0,
      "margen_unitario": 10.08,
      "margen_total": 80.64,
      "costo_estimado": true,
      "existencia": 76,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 855.0,
      "rotacion": 0.11,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 855 días, exceso de stock",
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
      "clase": "B",
      "pct_acum": 83.5,
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
        "id": 10,
        "clave_interna": "AB-010",
        "nombre": "Sardina en salsa de tomate"
      },
      "categoria": "Abarrote básico",
      "clase": "B",
      "pct_acum": 84.8,
      "unidades": 7,
      "venta": 185.5,
      "margen_unitario": 7.42,
      "margen_total": 51.94,
      "costo_estimado": true,
      "existencia": 966,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 12420.0,
      "rotacion": 0.01,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 12420 días, exceso de stock",
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
      "pct_acum": 86.1,
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
      "pct_acum": 87.5,
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
        "id": 38,
        "clave_interna": "LI-002",
        "nombre": "Jabón para trastes"
      },
      "categoria": "Limpieza del hogar",
      "clase": "B",
      "pct_acum": 88.8,
      "unidades": 7,
      "venta": 182.0,
      "margen_unitario": 7.28,
      "margen_total": 50.96,
      "costo_estimado": true,
      "existencia": 45,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 578.6,
      "rotacion": 0.16,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 579 días, exceso de stock",
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
      "pct_acum": 90.1,
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
      "pct_acum": 91.4,
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
        "id": 17,
        "clave_interna": "AB-017",
        "nombre": "Tortillas de maíz"
      },
      "categoria": "Abarrote básico",
      "clase": "B",
      "pct_acum": 92.5,
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
        "id": 23,
        "clave_interna": "BE-003",
        "nombre": "Refresco de cola"
      },
      "categoria": "Bebidas",
      "clase": "B",
      "pct_acum": 93.4,
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
        "id": 37,
        "clave_interna": "LI-001",
        "nombre": "Detergente en polvo"
      },
      "categoria": "Limpieza del hogar",
      "clase": "B",
      "pct_acum": 94.4,
      "unidades": 5,
      "venta": 210.0,
      "margen_unitario": 11.76,
      "margen_total": 58.8,
      "costo_estimado": true,
      "existencia": 12,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 216.0,
      "rotacion": 0.42,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 216 días, exceso de stock",
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
      "pct_acum": 95.3,
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
      "clase": "C",
      "pct_acum": 96.3,
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
        "id": 4,
        "clave_interna": "AB-004",
        "nombre": "Azúcar estándar"
      },
      "categoria": "Abarrote básico",
      "clase": "C",
      "pct_acum": 97.0,
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
      "clase": "C",
      "pct_acum": 97.8,
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
        "id": 21,
        "clave_interna": "BE-001",
        "nombre": "Agua purificada"
      },
      "categoria": "Bebidas",
      "clase": "C",
      "pct_acum": 98.5,
      "unidades": 4,
      "venta": 152.0,
      "margen_unitario": 10.64,
      "margen_total": 42.56,
      "costo_estimado": true,
      "existencia": 30,
      "minimo": 10,
      "quiebres": 1,
      "demanda_dia": 0.04,
      "cobertura_dias": 675.0,
      "rotacion": 0.13,
      "recomendacion": "Aumentar",
      "motivo": "hubo quiebres",
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
      "pct_acum": 99.3,
      "unidades": 4,
      "venta": 232.0,
      "margen_unitario": 16.24,
      "margen_total": 64.96,
      "costo_estimado": true,
      "existencia": 217,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.04,
      "cobertura_dias": 4882.5,
      "rotacion": 0.02,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 4882 días, exceso de stock",
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
      "pct_acum": 100.0,
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
X-Traza-Id: f6ef2439-845c-4b82-a03a-20162388e6ba
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 6 ms · traza `f6ef2439-845c-4b82-a03a-20162388e6ba`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "f6ef2439-845c-4b82-a03a-20162388e6ba"
  }
}
```

### SUR-09 · Restricciones de un microhub · PASA

**Objetivo.** Espacio y presupuesto.

**Petición.** `GET http://surtido:5122/api/v1/surtido/restricciones/1`

```http
Accept: application/json
X-Traza-Id: 0e42e725-96b5-4172-b48b-8eadbb0dba2e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 25 ms · traza `0e42e725-96b5-4172-b48b-8eadbb0dba2e`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "espacio_total": 3600.0,
  "presupuesto": 120000.0,
  "actualizado_en": "2026-11-26T23:19:37-06:00"
}
```

### SUR-10 · Cambiar las restricciones · PASA

**Objetivo.** El planeador fija otro espacio y presupuesto.

**Petición.** `PUT http://surtido:5122/api/v1/surtido/restricciones/1`

```http
Accept: application/json
X-Traza-Id: 83bd76aa-27b7-4305-b29b-0d376cfddba4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "espacio_total": 3700.0,
  "presupuesto": 120000.0
}
```

**Respuesta.** HTTP 200 (esperado 200) · 72 ms · traza `83bd76aa-27b7-4305-b29b-0d376cfddba4`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "espacio_total": 3700.0,
  "presupuesto": 120000.0,
  "actualizado_en": "2026-11-26T23:20:53-06:00"
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
      "actualizado_en": "2026-11-26T23:19:37.390629-06:00"
    },
    "valores_nuevos": {
      "espacio_total": 3700.0,
      "actualizado_en": "2026-11-26T23:20:53.791388-06:00"
    }
  }
]
```

### SUR-19 · Cambiar las restricciones con PATCH · PASA

**Objetivo.** PATCH es alias de PUT.

**Petición.** `PATCH http://surtido:5122/api/v1/surtido/restricciones/1`

```http
Accept: application/json
X-Traza-Id: fcbc90ea-232f-4d3a-979f-626214b3b516
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "espacio_total": 3650.0,
  "presupuesto": 120000.0
}
```

**Respuesta.** HTTP 200 (esperado 200) · 51 ms · traza `fcbc90ea-232f-4d3a-979f-626214b3b516`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "espacio_total": 3650.0,
  "presupuesto": 120000.0,
  "actualizado_en": "2026-11-26T23:20:53-06:00"
}
```

### SUR-11 · Cambiar restricciones sin permiso · PASA

**Objetivo.** Solo surtido.editar.

**Petición.** `PUT http://surtido:5122/api/v1/surtido/restricciones/1`

```http
Accept: application/json
X-Traza-Id: 606b835c-7d57-40b0-bf37-b40185cbf2f1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{
  "espacio_total": 10
}
```

**Respuesta.** HTTP 403 (esperado 403) · 29 ms · traza `606b835c-7d57-40b0-bf37-b40185cbf2f1`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "606b835c-7d57-40b0-bf37-b40185cbf2f1"
  }
}
```

### SUR-12 · Espacio inválido · PASA

**Objetivo.** Mayor que cero.

**Petición.** `PUT http://surtido:5122/api/v1/surtido/restricciones/1`

```http
Accept: application/json
X-Traza-Id: 0a37603d-e0fc-44e8-88c2-d968293831ff
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "espacio_total": 0
}
```

**Respuesta.** HTTP 422 (esperado 422) · 6 ms · traza `0a37603d-e0fc-44e8-88c2-d968293831ff`

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
    "traza_id": "0a37603d-e0fc-44e8-88c2-d968293831ff"
  }
}
```

### SUR-13 · Guardar la recomendación · PASA

**Objetivo.** Queda con sus líneas y los supuestos usados, para compararla después.

**Petición.** `POST http://surtido:5122/api/v1/surtido/recomendaciones`

```http
Accept: application/json
X-Traza-Id: 4c9321c0-cda4-4e5f-b10c-14868211c835
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "nota": "Evidencia de la Ola 2"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 453 ms · traza `4c9321c0-cda4-4e5f-b10c-14868211c835`

```json
{
  "id": 42,
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "ventana_dias": 90,
  "nota": "Evidencia de la Ola 2",
  "resumen": {
    "productos": 51,
    "aumentar": 2,
    "mantener": 0,
    "reducir": 49,
    "eliminar": 0,
    "excluir": 0,
    "clase_a": 33,
    "clase_b": 12,
    "clase_c": 6,
    "unidades_a_comprar": 0,
    "con_costo_estimado": 51,
    "espacio": {
      "total": 3600.0,
      "ocupado": 3835.0,
      "sugerido": 0.0,
      "ocupacion_pct": 106.5
    },
    "presupuesto": {
      "total": 120000.0,
      "requerido": 0.0,
      "uso_pct": 0.0
    }
  },
  "creado_por": 5,
  "creado_en": "2026-11-26T23:20:54-06:00",
  "lineas": [
    {
      "producto": {
        "id": 45,
        "clave_interna": "LI-009",
        "nombre": "Fibra para trastes"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 25,
      "existencia": 43,
      "sugerido": 0,
      "margen_unitario": 5.04,
      "rotacion": 0.58,
      "motivo": "cobertura de 155 días, exceso de stock"
    },
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
        "id": 7,
        "clave_interna": "AB-007",
        "nombre": "Harina de trigo"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 18,
      "existencia": 14,
      "sugerido": 0,
      "margen_unitario": 6.86,
      "rotacion": 1.29,
      "motivo": "cobertura de 70 días, exceso de stock"
    },
    {
      "producto": {
        "id": 36,
        "clave_interna": "LA-008",
        "nombre": "Jamón de pavo"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 18,
      "existencia": 30,
      "sugerido": 0,
      "margen_unitario": 12.88,
      "rotacion": 0.6,
      "motivo": "cobertura de 150 días, exceso de stock"
    },
    {
      "producto": {
        "id": 8,
        "clave_interna": "AB-008",
        "nombre": "Pasta para sopa surtida"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 17,
      "existencia": 16,
      "sugerido": 0,
      "margen_unitario": 2.66,
      "rotacion": 1.06,
      "motivo": "cobertura de 85 días, exceso de stock"
    },
    {
      "producto": {
        "id": 25,
        "clave_interna": "BE-005",
        "nombre": "Jugo de naranja"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 17,
      "existencia": 78,
      "sugerido": 0,
      "margen_unitario": 7.84,
      "rotacion": 0.22,
      "motivo": "cobertura de 413 días, exceso de stock"
    },
    {
      "producto": {
        "id": 34,
        "clave_interna": "LA-006",
        "nombre": "Yogur natural"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 16,
      "existencia": 10,
      "sugerido": 0,
      "margen_unitario": 12.32,
      "rotacion": 1.6,
      "motivo": "cobertura de 56 días, exceso de stock"
    },
    {
      "producto": {
        "id": 12,
        "clave_interna": "AB-012",
        "nombre": "Chiles jalapeños en escabeche"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 15,
      "existencia": 515,
      "sugerido": 0,
      "margen_unitario": 5.46,
      "rotacion": 0.03,
      "motivo": "cobertura de 3090 días, exceso de stock"
    },
    {
      "producto": {
        "id": 20,
        "clave_interna": "AB-020",
        "nombre": "Lenteja"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 15,
      "existencia": 73,
      "sugerido": 0,
      "margen_unitario": 6.72,
      "rotacion": 0.21,
      "motivo": "cobertura de 438 días, exceso de stock"
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
        "id": 11,
        "clave_interna": "AB-011",
        "nombre": "Frijoles refritos"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 13,
      "existencia": 25,
      "sugerido": 0,
      "margen_unitario": 6.44,
      "rotacion": 0.52,
      "motivo": "cobertura de 173 días, exceso de stock"
    },
    {
      "producto": {
        "id": 24,
        "clave_interna": "BE-004",
        "nombre": "Refresco sabor manzana"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 13,
      "existencia": 39,
      "sugerido": 0,
      "margen_unitario": 10.08,
      "rotacion": 0.33,
      "motivo": "cobertura de 270 días, exceso de stock"
    },
    {
      "producto": {
        "id": 26,
        "clave_interna": "BE-006",
        "nombre": "Bebida de soya"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 13,
      "existencia": 15,
      "sugerido": 0,
      "margen_unitario": 8.96,
      "rotacion": 0.87,
      "motivo": "cobertura de 104 días, exceso de stock"
    },
    {
      "producto": {
        "id": 29,
        "clave_interna": "LA-001",
        "nombre": "Leche entera"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 13,
      "existencia": 45,
      "sugerido": 0,
      "margen_unitario": 7.7,
      "rotacion": 0.29,
      "motivo": "cobertura de 312 días, exceso de stock"
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
        "id": 6,
        "clave_interna": "AB-006",
        "nombre": "Harina de maíz nixtamalizado"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 11,
      "existencia": 88,
      "sugerido": 0,
      "margen_unitario": 7.28,
      "rotacion": 0.12,
      "motivo": "cobertura de 720 días, exceso de stock"
    },
    {
      "producto": {
        "id": 16,
        "clave_interna": "AB-016",
        "nombre": "Galletas María"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 11,
      "existencia": 75,
      "sugerido": 0,
      "margen_unitario": 4.62,
      "rotacion": 0.15,
      "motivo": "cobertura de 614 días, exceso de stock"
    },
    {
      "producto": {
        "id": 22,
        "clave_interna": "BE-002",
        "nombre": "Agua embotellada"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 11,
      "existencia": 66,
      "sugerido": 0,
      "margen_unitario": 4.2,
      "rotacion": 0.17,
      "motivo": "cobertura de 540 días, exceso de stock"
    },
    {
      "producto": {
        "id": 27,
        "clave_interna": "BE-007",
        "nombre": "Té helado de limón"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 11,
      "existencia": 84,
      "sugerido": 0,
      "margen_unitario": 4.76,
      "rotacion": 0.13,
      "motivo": "cobertura de 687 días, exceso de stock"
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
        "id": 3,
        "clave_interna": "AB-003",
        "nombre": "Aceite vegetal"
      },
      "clase": "A",
      "recomendacion": "Aumentar",
      "unidades": 10,
      "existencia": 24,
      "sugerido": 0,
      "margen_unitario": 11.76,
      "rotacion": 0.42,
      "motivo": "hubo quiebres"
    },
    {
      "producto": {
        "id": 5,
        "clave_interna": "AB-005",
        "nombre": "Sal de mesa"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 10,
      "existencia": 30,
      "sugerido": 0,
      "margen_unitario": 3.92,
      "rotacion": 0.33,
      "motivo": "cobertura de 270 días, exceso de stock"
    },
    {
      "producto": {
        "id": 40,
        "clave_interna": "LI-004",
        "nombre": "Limpiador multiusos"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 10,
      "existencia": 12,
      "sugerido": 0,
      "margen_unitario": 7.84,
      "rotacion": 0.83,
      "motivo": "cobertura de 108 días, exceso de stock"
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
        "id": 9,
        "clave_interna": "AB-009",
        "nombre": "Atún en agua"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 8,
      "existencia": 42,
      "sugerido": 0,
      "margen_unitario": 5.88,
      "rotacion": 0.19,
      "motivo": "cobertura de 472 días, exceso de stock"
    },
    {
      "producto": {
        "id": 33,
        "clave_interna": "LA-005",
        "nombre": "Crema ácida"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 8,
      "existencia": 78,
      "sugerido": 0,
      "margen_unitario": 10.08,
      "rotacion": 0.1,
      "motivo": "cobertura de 878 días, exceso de stock"
    },
    {
      "producto": {
        "id": 50,
        "clave_interna": "HI-005",
        "nombre": "Toallas femeninas"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 8,
      "existencia": 76,
      "sugerido": 0,
      "margen_unitario": 10.08,
      "rotacion": 0.11,
      "motivo": "cobertura de 855 días, exceso de stock"
    },
    {
      "producto": {
        "id": 51,
        "clave_interna": "HI-006",
        "nombre": "Pañal etapa 3"
      },
      "clase": "B",
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
        "id": 10,
        "clave_interna": "AB-010",
        "nombre": "Sardina en salsa de tomate"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 966,
      "sugerido": 0,
      "margen_unitario": 7.42,
      "rotacion": 0.01,
      "motivo": "cobertura de 12420 días, exceso de stock"
    },
    {
      "producto": {
        "id": 14,
        "clave_interna": "AB-014",
        "nombre": "Café soluble"
      },
      "clase": "B",
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
        "id": 38,
        "clave_interna": "LI-002",
        "nombre": "Jabón para trastes"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 45,
      "sugerido": 0,
      "margen_unitario": 7.28,
      "rotacion": 0.16,
      "motivo": "cobertura de 579 días, exceso de stock"
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
        "id": 37,
        "clave_interna": "LI-001",
        "nombre": "Detergente en polvo"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 12,
      "sugerido": 0,
      "margen_unitario": 11.76,
      "rotacion": 0.42,
      "motivo": "cobertura de 216 días, exceso de stock"
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
      "clase": "C",
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
        "id": 4,
        "clave_interna": "AB-004",
        "nombre": "Azúcar estándar"
      },
      "clase": "C",
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
      "clase": "C",
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
        "id": 21,
        "clave_interna": "BE-001",
        "nombre": "Agua purificada"
      },
      "clase": "C",
      "recomendacion": "Aumentar",
      "unidades": 4,
      "existencia": 30,
      "sugerido": 0,
      "margen_unitario": 10.64,
      "rotacion": 0.13,
      "motivo": "hubo quiebres"
    },
    {
      "producto": {
        "id": 31,
        "clave_interna": "LA-003",
        "nombre": "Queso fresco"
      },
      "clase": "C",
      "recomendacion": "Reducir",
      "unidades": 4,
      "existencia": 217,
      "sugerido": 0,
      "margen_unitario": 16.24,
      "rotacion": 0.02,
      "motivo": "cobertura de 4882 días, exceso de stock"
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
    "id": 42,
    "microhub_id": 1,
    "resumen": {
      "productos": 51,
      "aumentar": 2,
      "mantener": 0,
      "reducir": 49,
      "eliminar": 0,
      "excluir": 0,
      "clase_a": 33,
      "clase_b": 12,
      "clase_c": 6,
      "unidades_a_comprar": 0,
      "con_costo_estimado": 51,
      "espacio": {
        "total": 3600.0,
        "ocupado": 3835.0,
        "sugerido": 0.0,
        "ocupacion_pct": 106.5
      },
      "presupuesto": {
        "total": 120000.0,
        "requerido": 0.0,
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
    "lineas": 2,
    "sugerido": 0
  },
  {
    "accion": "Reducir",
    "lineas": 49,
    "sugerido": 0
  }
]
```

### SUR-18 · Recomendaciones guardadas · PASA

**Objetivo.** Para compararlas con el tiempo.

**Petición.** `GET http://surtido:5122/api/v1/surtido/recomendaciones?microhub_id=1`

```http
Accept: application/json
X-Traza-Id: ba6434f1-c9c4-4732-aa76-18ee3afa8190
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 66 ms · traza `ba6434f1-c9c4-4732-aa76-18ee3afa8190`

```json
{
  "datos": [
    {
      "id": 42,
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "ventana_dias": 90,
      "nota": "Evidencia de la Ola 2",
      "resumen": {
        "productos": 51,
        "aumentar": 2,
        "mantener": 0,
        "reducir": 49,
        "eliminar": 0,
        "excluir": 0,
        "clase_a": 33,
        "clase_b": 12,
        "clase_c": 6,
        "unidades_a_comprar": 0,
        "con_costo_estimado": 51,
        "espacio": {
          "total": 3600.0,
          "ocupado": 3835.0,
          "sugerido": 0.0,
          "ocupacion_pct": 106.5
        },
        "presupuesto": {
          "total": 120000.0,
          "requerido": 0.0,
          "uso_pct": 0.0
        }
      },
      "creado_por": 5,
      "creado_en": "2026-11-26T23:20:54-06:00"
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

**Petición.** `GET http://surtido:5122/api/v1/surtido/recomendaciones/42`

```http
Accept: application/json
X-Traza-Id: c7fc654c-36de-45b1-afde-5d1e71e736f9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 51 ms · traza `c7fc654c-36de-45b1-afde-5d1e71e736f9`

```json
{
  "id": 42,
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "ventana_dias": 90,
  "nota": "Evidencia de la Ola 2",
  "resumen": {
    "productos": 51,
    "aumentar": 2,
    "mantener": 0,
    "reducir": 49,
    "eliminar": 0,
    "excluir": 0,
    "clase_a": 33,
    "clase_b": 12,
    "clase_c": 6,
    "unidades_a_comprar": 0,
    "con_costo_estimado": 51,
    "espacio": {
      "total": 3600.0,
      "ocupado": 3835.0,
      "sugerido": 0.0,
      "ocupacion_pct": 106.5
    },
    "presupuesto": {
      "total": 120000.0,
      "requerido": 0.0,
      "uso_pct": 0.0
    }
  },
  "creado_por": 5,
  "creado_en": "2026-11-26T23:20:54-06:00",
  "lineas": [
    {
      "producto": {
        "id": 45,
        "clave_interna": "LI-009",
        "nombre": "Fibra para trastes"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 25,
      "existencia": 43,
      "sugerido": 0,
      "margen_unitario": 5.04,
      "rotacion": 0.58,
      "motivo": "cobertura de 155 días, exceso de stock"
    },
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
        "id": 7,
        "clave_interna": "AB-007",
        "nombre": "Harina de trigo"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 18,
      "existencia": 14,
      "sugerido": 0,
      "margen_unitario": 6.86,
      "rotacion": 1.29,
      "motivo": "cobertura de 70 días, exceso de stock"
    },
    {
      "producto": {
        "id": 36,
        "clave_interna": "LA-008",
        "nombre": "Jamón de pavo"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 18,
      "existencia": 30,
      "sugerido": 0,
      "margen_unitario": 12.88,
      "rotacion": 0.6,
      "motivo": "cobertura de 150 días, exceso de stock"
    },
    {
      "producto": {
        "id": 8,
        "clave_interna": "AB-008",
        "nombre": "Pasta para sopa surtida"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 17,
      "existencia": 16,
      "sugerido": 0,
      "margen_unitario": 2.66,
      "rotacion": 1.06,
      "motivo": "cobertura de 85 días, exceso de stock"
    },
    {
      "producto": {
        "id": 25,
        "clave_interna": "BE-005",
        "nombre": "Jugo de naranja"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 17,
      "existencia": 78,
      "sugerido": 0,
      "margen_unitario": 7.84,
      "rotacion": 0.22,
      "motivo": "cobertura de 413 días, exceso de stock"
    },
    {
      "producto": {
        "id": 34,
        "clave_interna": "LA-006",
        "nombre": "Yogur natural"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 16,
      "existencia": 10,
      "sugerido": 0,
      "margen_unitario": 12.32,
      "rotacion": 1.6,
      "motivo": "cobertura de 56 días, exceso de stock"
    },
    {
      "producto": {
        "id": 12,
        "clave_interna": "AB-012",
        "nombre": "Chiles jalapeños en escabeche"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 15,
      "existencia": 515,
      "sugerido": 0,
      "margen_unitario": 5.46,
      "rotacion": 0.03,
      "motivo": "cobertura de 3090 días, exceso de stock"
    },
    {
      "producto": {
        "id": 20,
        "clave_interna": "AB-020",
        "nombre": "Lenteja"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 15,
      "existencia": 73,
      "sugerido": 0,
      "margen_unitario": 6.72,
      "rotacion": 0.21,
      "motivo": "cobertura de 438 días, exceso de stock"
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
        "id": 11,
        "clave_interna": "AB-011",
        "nombre": "Frijoles refritos"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 13,
      "existencia": 25,
      "sugerido": 0,
      "margen_unitario": 6.44,
      "rotacion": 0.52,
      "motivo": "cobertura de 173 días, exceso de stock"
    },
    {
      "producto": {
        "id": 24,
        "clave_interna": "BE-004",
        "nombre": "Refresco sabor manzana"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 13,
      "existencia": 39,
      "sugerido": 0,
      "margen_unitario": 10.08,
      "rotacion": 0.33,
      "motivo": "cobertura de 270 días, exceso de stock"
    },
    {
      "producto": {
        "id": 26,
        "clave_interna": "BE-006",
        "nombre": "Bebida de soya"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 13,
      "existencia": 15,
      "sugerido": 0,
      "margen_unitario": 8.96,
      "rotacion": 0.87,
      "motivo": "cobertura de 104 días, exceso de stock"
    },
    {
      "producto": {
        "id": 29,
        "clave_interna": "LA-001",
        "nombre": "Leche entera"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 13,
      "existencia": 45,
      "sugerido": 0,
      "margen_unitario": 7.7,
      "rotacion": 0.29,
      "motivo": "cobertura de 312 días, exceso de stock"
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
        "id": 6,
        "clave_interna": "AB-006",
        "nombre": "Harina de maíz nixtamalizado"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 11,
      "existencia": 88,
      "sugerido": 0,
      "margen_unitario": 7.28,
      "rotacion": 0.12,
      "motivo": "cobertura de 720 días, exceso de stock"
    },
    {
      "producto": {
        "id": 16,
        "clave_interna": "AB-016",
        "nombre": "Galletas María"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 11,
      "existencia": 75,
      "sugerido": 0,
      "margen_unitario": 4.62,
      "rotacion": 0.15,
      "motivo": "cobertura de 614 días, exceso de stock"
    },
    {
      "producto": {
        "id": 22,
        "clave_interna": "BE-002",
        "nombre": "Agua embotellada"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 11,
      "existencia": 66,
      "sugerido": 0,
      "margen_unitario": 4.2,
      "rotacion": 0.17,
      "motivo": "cobertura de 540 días, exceso de stock"
    },
    {
      "producto": {
        "id": 27,
        "clave_interna": "BE-007",
        "nombre": "Té helado de limón"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 11,
      "existencia": 84,
      "sugerido": 0,
      "margen_unitario": 4.76,
      "rotacion": 0.13,
      "motivo": "cobertura de 687 días, exceso de stock"
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
        "id": 3,
        "clave_interna": "AB-003",
        "nombre": "Aceite vegetal"
      },
      "clase": "A",
      "recomendacion": "Aumentar",
      "unidades": 10,
      "existencia": 24,
      "sugerido": 0,
      "margen_unitario": 11.76,
      "rotacion": 0.42,
      "motivo": "hubo quiebres"
    },
    {
      "producto": {
        "id": 5,
        "clave_interna": "AB-005",
        "nombre": "Sal de mesa"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 10,
      "existencia": 30,
      "sugerido": 0,
      "margen_unitario": 3.92,
      "rotacion": 0.33,
      "motivo": "cobertura de 270 días, exceso de stock"
    },
    {
      "producto": {
        "id": 40,
        "clave_interna": "LI-004",
        "nombre": "Limpiador multiusos"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 10,
      "existencia": 12,
      "sugerido": 0,
      "margen_unitario": 7.84,
      "rotacion": 0.83,
      "motivo": "cobertura de 108 días, exceso de stock"
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
        "id": 9,
        "clave_interna": "AB-009",
        "nombre": "Atún en agua"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 8,
      "existencia": 42,
      "sugerido": 0,
      "margen_unitario": 5.88,
      "rotacion": 0.19,
      "motivo": "cobertura de 472 días, exceso de stock"
    },
    {
      "producto": {
        "id": 33,
        "clave_interna": "LA-005",
        "nombre": "Crema ácida"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 8,
      "existencia": 78,
      "sugerido": 0,
      "margen_unitario": 10.08,
      "rotacion": 0.1,
      "motivo": "cobertura de 878 días, exceso de stock"
    },
    {
      "producto": {
        "id": 50,
        "clave_interna": "HI-005",
        "nombre": "Toallas femeninas"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 8,
      "existencia": 76,
      "sugerido": 0,
      "margen_unitario": 10.08,
      "rotacion": 0.11,
      "motivo": "cobertura de 855 días, exceso de stock"
    },
    {
      "producto": {
        "id": 51,
        "clave_interna": "HI-006",
        "nombre": "Pañal etapa 3"
      },
      "clase": "B",
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
        "id": 10,
        "clave_interna": "AB-010",
        "nombre": "Sardina en salsa de tomate"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 966,
      "sugerido": 0,
      "margen_unitario": 7.42,
      "rotacion": 0.01,
      "motivo": "cobertura de 12420 días, exceso de stock"
    },
    {
      "producto": {
        "id": 14,
        "clave_interna": "AB-014",
        "nombre": "Café soluble"
      },
      "clase": "B",
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
        "id": 38,
        "clave_interna": "LI-002",
        "nombre": "Jabón para trastes"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 45,
      "sugerido": 0,
      "margen_unitario": 7.28,
      "rotacion": 0.16,
      "motivo": "cobertura de 579 días, exceso de stock"
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
        "id": 37,
        "clave_interna": "LI-001",
        "nombre": "Detergente en polvo"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 12,
      "sugerido": 0,
      "margen_unitario": 11.76,
      "rotacion": 0.42,
      "motivo": "cobertura de 216 días, exceso de stock"
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
      "clase": "C",
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
        "id": 4,
        "clave_interna": "AB-004",
        "nombre": "Azúcar estándar"
      },
      "clase": "C",
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
      "clase": "C",
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
        "id": 21,
        "clave_interna": "BE-001",
        "nombre": "Agua purificada"
      },
      "clase": "C",
      "recomendacion": "Aumentar",
      "unidades": 4,
      "existencia": 30,
      "sugerido": 0,
      "margen_unitario": 10.64,
      "rotacion": 0.13,
      "motivo": "hubo quiebres"
    },
    {
      "producto": {
        "id": 31,
        "clave_interna": "LA-003",
        "nombre": "Queso fresco"
      },
      "clase": "C",
      "recomendacion": "Reducir",
      "unidades": 4,
      "existencia": 217,
      "sugerido": 0,
      "margen_unitario": 16.24,
      "rotacion": 0.02,
      "motivo": "cobertura de 4882 días, exceso de stock"
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

**Petición.** `GET http://surtido:5122/api/v1/surtido/recomendaciones/42`

```http
Accept: application/json
X-Traza-Id: c27c6721-8eba-4335-b642-a4afd43263ec
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 23 ms · traza `c27c6721-8eba-4335-b642-a4afd43263ec`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "c27c6721-8eba-4335-b642-a4afd43263ec"
  }
}
```

### SUR-16 · Guardar sin permiso · PASA

**Objetivo.** El operador no tiene surtido.editar.

**Petición.** `POST http://surtido:5122/api/v1/surtido/recomendaciones`

```http
Accept: application/json
X-Traza-Id: 5d1344d9-bd54-4a54-b6bb-ffb27df098fd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1
}
```

**Respuesta.** HTTP 403 (esperado 403) · 28 ms · traza `5d1344d9-bd54-4a54-b6bb-ffb27df098fd`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "5d1344d9-bd54-4a54-b6bb-ffb27df098fd"
  }
}
```

### SUR-17 · Supuestos del surtido · PASA

**Objetivo.** Cortes ABC, días de cobertura y ventana de análisis.

**Petición.** `GET http://surtido:5122/api/v1/surtido/supuestos`

```http
Accept: application/json
X-Traza-Id: 03fcf2f4-e900-4e5b-bbbd-9db2be6a380f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 32 ms · traza `03fcf2f4-e900-4e5b-bbbd-9db2be6a380f`

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
X-Traza-Id: cbf9c440-4610-485f-87e3-2a29738c304e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 73 ms · traza `cbf9c440-4610-485f-87e3-2a29738c304e`

```json
{
  "datos": [
    {
      "id": 703,
      "folio": "PED-20261126-000703",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "latitud": 25.748439,
      "longitud": -100.369944,
      "total": 189.0,
      "listo_en": "2026-11-26T23:20:54-06:00"
    },
    {
      "id": 704,
      "folio": "PED-20261126-000704",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "latitud": 25.751679,
      "longitud": -100.366615,
      "total": 175.0,
      "listo_en": "2026-11-26T23:20:54-06:00"
    },
    {
      "id": 705,
      "folio": "PED-20261126-000705",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "latitud": 25.753225,
      "longitud": -100.365213,
      "total": 103.0,
      "listo_en": "2026-11-26T23:20:54-06:00"
    },
    {
      "id": 706,
      "folio": "PED-20261126-000706",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "latitud": 25.751679,
      "longitud": -100.366615,
      "total": 157.5,
      "listo_en": "2026-11-26T23:20:54-06:00"
    },
    {
      "id": 707,
      "folio": "PED-20261126-000707",
      "zona": {
        "id": 1,
        "nombre": "San Bernabé Centro"
      },
      "latitud": 25.745527,
      "longitud": -100.362981,
      "total": 145.0,
      "listo_en": "2026-11-26T23:20:54-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 100,
    "total": 5,
    "paginas": 1
  }
}
```

**Evidencia en PostgreSQL.** `SELECT id, folio, estado, zona_id, listo_en IS NOT NULL AS listo FROM pedido WHERE id = ANY(%s) ORDER BY id`

```json
[
  {
    "id": 703,
    "folio": "PED-20261126-000703",
    "estado": "en_preparacion",
    "zona_id": 2,
    "listo": true
  },
  {
    "id": 704,
    "folio": "PED-20261126-000704",
    "estado": "en_preparacion",
    "zona_id": 2,
    "listo": true
  },
  {
    "id": 705,
    "folio": "PED-20261126-000705",
    "estado": "en_preparacion",
    "zona_id": 2,
    "listo": true
  },
  {
    "id": 706,
    "folio": "PED-20261126-000706",
    "estado": "en_preparacion",
    "zona_id": 2,
    "listo": true
  },
  {
    "id": 707,
    "folio": "PED-20261126-000707",
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
X-Traza-Id: 7754914d-d060-4b64-9c77-a3570df1ab41
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "pedido_ids": [
    703,
    704,
    705,
    706,
    707
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 175 ms · traza `7754914d-d060-4b64-9c77-a3570df1ab41`

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
            "id": 705,
            "folio": "PED-20261126-000705"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.77,
          "minutos_acum": 6.1
        },
        {
          "orden": 2,
          "pedido": {
            "id": 704,
            "folio": "PED-20261126-000704"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.751679,
          "longitud": -100.366615,
          "tramo_km": 0.29,
          "minutos_acum": 10.9
        },
        {
          "orden": 3,
          "pedido": {
            "id": 706,
            "folio": "PED-20261126-000706"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.751679,
          "longitud": -100.366615,
          "tramo_km": 0.0,
          "minutos_acum": 14.9
        },
        {
          "orden": 4,
          "pedido": {
            "id": 703,
            "folio": "PED-20261126-000703"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.748439,
          "longitud": -100.369944,
          "tramo_km": 0.64,
          "minutos_acum": 20.6
        }
      ],
      "distancia_km": 1.7,
      "minutos": 20.6,
      "costo": 79.64
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
            "id": 707,
            "folio": "PED-20261126-000707"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.745527,
          "longitud": -100.362981,
          "tramo_km": 0.38,
          "minutos_acum": 5.0
        }
      ],
      "distancia_km": 0.38,
      "minutos": 5.0,
      "costo": 19.72
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 2,
    "paradas": 5,
    "distancia_km": 2.08,
    "minutos_maximo": 20.6,
    "costo": 99.36
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
    "planes": 2
  }
]
```

### RUT-03 · Comparar métodos de recorrido · PASA

**Objetivo.** Las mismas paradas con orden de llegada, vecino más cercano, 2-opt y exacto.

**Petición.** `POST http://rutas:5118/api/v1/rutas/comparaciones`

```http
Accept: application/json
X-Traza-Id: cb44f68d-9549-46c4-b271-a8c2d1743fc6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "pedido_ids": [
    703,
    704,
    705,
    706,
    707
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 98 ms · traza `cb44f68d-9549-46c4-b271-a8c2d1743fc6`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "paradas": 5,
  "filas": [
    {
      "metodo": "Orden de llegada",
      "distancia_km": 3.0,
      "minutos": 28.2,
      "costo": 103.5,
      "mejora_pct": 0.0
    },
    {
      "metodo": "Vecino más cercano",
      "distancia_km": 2.31,
      "minutos": 26.3,
      "costo": 100.38,
      "mejora_pct": 23.0
    },
    {
      "metodo": "Vecino más cercano + 2-opt",
      "distancia_km": 2.31,
      "minutos": 26.3,
      "costo": 100.38,
      "mejora_pct": 23.0
    },
    {
      "metodo": "TSP exacto",
      "distancia_km": 2.31,
      "minutos": 26.3,
      "costo": 100.38,
      "mejora_pct": 23.0
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
X-Traza-Id: 5840c76c-e7c8-43a0-8166-fc343c24d6a1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "pedido_ids": [
    703,
    704,
    705,
    706,
    707
  ],
  "metodo": "exacto"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 215 ms · traza `5840c76c-e7c8-43a0-8166-fc343c24d6a1`

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
            "id": 705,
            "folio": "PED-20261126-000705"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.77,
          "minutos_acum": 6.1
        },
        {
          "orden": 2,
          "pedido": {
            "id": 704,
            "folio": "PED-20261126-000704"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.751679,
          "longitud": -100.366615,
          "tramo_km": 0.29,
          "minutos_acum": 10.9
        },
        {
          "orden": 3,
          "pedido": {
            "id": 706,
            "folio": "PED-20261126-000706"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.751679,
          "longitud": -100.366615,
          "tramo_km": 0.0,
          "minutos_acum": 14.9
        },
        {
          "orden": 4,
          "pedido": {
            "id": 703,
            "folio": "PED-20261126-000703"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.748439,
          "longitud": -100.369944,
          "tramo_km": 0.64,
          "minutos_acum": 20.6
        }
      ],
      "distancia_km": 1.7,
      "minutos": 20.6,
      "costo": 79.64
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
            "id": 707,
            "folio": "PED-20261126-000707"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.745527,
          "longitud": -100.362981,
          "tramo_km": 0.38,
          "minutos_acum": 5.0
        }
      ],
      "distancia_km": 0.38,
      "minutos": 5.0,
      "costo": 19.72
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 2,
    "paradas": 5,
    "distancia_km": 2.08,
    "minutos_maximo": 20.6,
    "costo": 99.36
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
X-Traza-Id: a7e174c8-8992-409b-a02d-0e3f355fd24f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "pedido_ids": [
    703,
    704,
    705,
    706,
    707
  ],
  "guardar": true
}
```

**Respuesta.** HTTP 201 (esperado 201) · 266 ms · traza `a7e174c8-8992-409b-a02d-0e3f355fd24f`

```json
{
  "id": 119,
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
            "id": 705,
            "folio": "PED-20261126-000705"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.77,
          "minutos_acum": 6.1
        },
        {
          "orden": 2,
          "pedido": {
            "id": 704,
            "folio": "PED-20261126-000704"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.751679,
          "longitud": -100.366615,
          "tramo_km": 0.29,
          "minutos_acum": 10.9
        },
        {
          "orden": 3,
          "pedido": {
            "id": 706,
            "folio": "PED-20261126-000706"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.751679,
          "longitud": -100.366615,
          "tramo_km": 0.0,
          "minutos_acum": 14.9
        },
        {
          "orden": 4,
          "pedido": {
            "id": 703,
            "folio": "PED-20261126-000703"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.748439,
          "longitud": -100.369944,
          "tramo_km": 0.64,
          "minutos_acum": 20.6
        }
      ],
      "distancia_km": 1.7,
      "minutos": 20.6,
      "costo": 79.64
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
            "id": 707,
            "folio": "PED-20261126-000707"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.745527,
          "longitud": -100.362981,
          "tramo_km": 0.38,
          "minutos_acum": 5.0
        }
      ],
      "distancia_km": 0.38,
      "minutos": 5.0,
      "costo": 19.72
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 2,
    "paradas": 5,
    "distancia_km": 2.08,
    "minutos_maximo": 20.6,
    "costo": 99.36
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
    "id": 119,
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

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes/119/ajustes`

```http
Accept: application/json
X-Traza-Id: 4e210643-0f4f-4536-935d-8e01e20d6eb2
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

**Respuesta.** HTTP 200 (esperado 200) · 92 ms · traza `4e210643-0f4f-4536-935d-8e01e20d6eb2`

```json
{
  "id": 119,
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
            "id": 705,
            "folio": "PED-20261126-000705"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.77,
          "minutos_acum": 31.1
        },
        {
          "orden": 2,
          "pedido": {
            "id": 704,
            "folio": "PED-20261126-000704"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.751679,
          "longitud": -100.366615,
          "tramo_km": 0.29,
          "minutos_acum": 35.9
        },
        {
          "orden": 3,
          "pedido": {
            "id": 706,
            "folio": "PED-20261126-000706"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.751679,
          "longitud": -100.366615,
          "tramo_km": 0.0,
          "minutos_acum": 39.9
        },
        {
          "orden": 4,
          "pedido": {
            "id": 703,
            "folio": "PED-20261126-000703"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.748439,
          "longitud": -100.369944,
          "tramo_km": 0.64,
          "minutos_acum": 45.6
        }
      ],
      "distancia_km": 1.7,
      "minutos": 45.6,
      "costo": 79.64
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
            "id": 707,
            "folio": "PED-20261126-000707"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.745527,
          "longitud": -100.362981,
          "tramo_km": 0.38,
          "minutos_acum": 5.0
        }
      ],
      "distancia_km": 0.38,
      "minutos": 5.0,
      "costo": 19.72
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 2,
    "paradas": 5,
    "distancia_km": 2.08,
    "minutos_maximo": 45.6,
    "costo": 99.36
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
    "PED-20261126-000705",
    "PED-20261126-000704",
    "PED-20261126-000706",
    "PED-20261126-000703"
  ]
}
```

### RUT-07 · Quitar un pedido · PASA

**Objetivo.** Recalcula la ruta afectada con el mismo método.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes/119/ajustes`

```http
Accept: application/json
X-Traza-Id: 7f55e79b-9335-4e49-ad83-a4e16fc21b19
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "tipo": "quitar_pedido",
  "pedido_id": 705
}
```

**Respuesta.** HTTP 200 (esperado 200) · 87 ms · traza `7f55e79b-9335-4e49-ad83-a4e16fc21b19`

```json
{
  "id": 119,
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
            "id": 704,
            "folio": "PED-20261126-000704"
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
            "id": 706,
            "folio": "PED-20261126-000706"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.751679,
          "longitud": -100.366615,
          "tramo_km": 0.0,
          "minutos_acum": 9.7
        },
        {
          "orden": 3,
          "pedido": {
            "id": 703,
            "folio": "PED-20261126-000703"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.748439,
          "longitud": -100.369944,
          "tramo_km": 0.64,
          "minutos_acum": 15.5
        }
      ],
      "distancia_km": 1.27,
      "minutos": 15.5,
      "costo": 59.71
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
            "id": 707,
            "folio": "PED-20261126-000707"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.745527,
          "longitud": -100.362981,
          "tramo_km": 0.38,
          "minutos_acum": 5.0
        }
      ],
      "distancia_km": 0.38,
      "minutos": 5.0,
      "costo": 19.72
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 2,
    "paradas": 4,
    "distancia_km": 1.65,
    "minutos_maximo": 15.5,
    "costo": 79.43
  },
  "cambios": [
    "Se quitó el pedido PED-20261126-000705; la ruta de Ramiro Alanís Lozano se recalculó con 3 paradas."
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

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes/119/ajustes`

```http
Accept: application/json
X-Traza-Id: 67f55d3b-33f3-440d-affc-6e00976323be
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "tipo": "agregar_pedido",
  "pedido_id": 705
}
```

**Respuesta.** HTTP 200 (esperado 200) · 146 ms · traza `67f55d3b-33f3-440d-affc-6e00976323be`

```json
{
  "id": 119,
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
            "id": 704,
            "folio": "PED-20261126-000704"
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
            "id": 706,
            "folio": "PED-20261126-000706"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.751679,
          "longitud": -100.366615,
          "tramo_km": 0.0,
          "minutos_acum": 9.7
        },
        {
          "orden": 3,
          "pedido": {
            "id": 703,
            "folio": "PED-20261126-000703"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.748439,
          "longitud": -100.369944,
          "tramo_km": 0.64,
          "minutos_acum": 15.5
        }
      ],
      "distancia_km": 1.27,
      "minutos": 15.5,
      "costo": 59.71
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
            "id": 707,
            "folio": "PED-20261126-000707"
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
            "id": 705,
            "folio": "PED-20261126-000705"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 1.15,
          "minutos_acum": 12.2
        }
      ],
      "distancia_km": 1.53,
      "minutos": 12.2,
      "costo": 42.89
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 2,
    "paradas": 5,
    "distancia_km": 2.8,
    "minutos_maximo": 15.5,
    "costo": 102.6
  },
  "cambios": [
    "Se agregó el pedido PED-20261126-000705 a la ruta de Diana Sepúlveda Ibarra; ahora tiene 2 paradas."
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

**Petición.** `GET http://rutas:5118/api/v1/rutas/planes/119`

```http
Accept: application/json
X-Traza-Id: 29638203-758a-4516-94d1-cfb953fe15ae
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 25 ms · traza `29638203-758a-4516-94d1-cfb953fe15ae`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "29638203-758a-4516-94d1-cfb953fe15ae"
  }
}
```

### RUT-10 · Confirmar el plan · PASA

**Objetivo.** Comprueba que los pedidos sigan listos y deja las rutas en plan_ruta.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes/119/confirmar`

```http
Accept: application/json
X-Traza-Id: 8b1a37d0-1156-4115-90f2-90c71ba07657
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 222 ms · traza `8b1a37d0-1156-4115-90f2-90c71ba07657`

```json
{
  "id": 119,
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
            "id": 704,
            "folio": "PED-20261126-000704"
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
            "id": 706,
            "folio": "PED-20261126-000706"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.751679,
          "longitud": -100.366615,
          "tramo_km": 0.0,
          "minutos_acum": 9.7
        },
        {
          "orden": 3,
          "pedido": {
            "id": 703,
            "folio": "PED-20261126-000703"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.748439,
          "longitud": -100.369944,
          "tramo_km": 0.64,
          "minutos_acum": 15.5
        }
      ],
      "distancia_km": 1.27,
      "minutos": 15.5,
      "costo": 59.71
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
            "id": 707,
            "folio": "PED-20261126-000707"
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
            "id": 705,
            "folio": "PED-20261126-000705"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 1.15,
          "minutos_acum": 12.2
        }
      ],
      "distancia_km": 1.53,
      "minutos": 12.2,
      "costo": 42.89
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 2,
    "paradas": 5,
    "distancia_km": 2.8,
    "minutos_maximo": 15.5,
    "costo": 102.6
  },
  "cambios": [
    "Se agregó el pedido PED-20261126-000705 a la ruta de Diana Sepúlveda Ibarra; ahora tiene 2 paradas."
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
    "id": 114,
    "repartidor_id": 7,
    "metodo": "TSP exacto",
    "paradas": 3,
    "distancia_km": "1.27",
    "minutos": "15.5",
    "costo_estimado": "59.71"
  },
  {
    "id": 115,
    "repartidor_id": 8,
    "metodo": "TSP exacto",
    "paradas": 2,
    "distancia_km": "1.53",
    "minutos": "12.2",
    "costo_estimado": "42.89"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT count(*) AS paradas FROM plan_ruta_parada WHERE plan_ruta_id IN (SELECT id FROM plan_ruta WHERE plan_despacho_id = %s)`

```json
[
  {
    "paradas": 5
  }
]
```

### RUT-11 · Confirmar otra vez · PASA

**Objetivo.** Un plan confirmado no se vuelve a confirmar.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes/119/confirmar`

```http
Accept: application/json
X-Traza-Id: e6c7f1fe-81ed-40ba-b665-2a2b77257ce7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 409 (esperado 409) · 25 ms · traza `e6c7f1fe-81ed-40ba-b665-2a2b77257ce7`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Solo se confirma un plan propuesto; este está confirmado.",
    "traza_id": "e6c7f1fe-81ed-40ba-b665-2a2b77257ce7"
  }
}
```

### RUT-12 · Planes guardados · PASA

**Objetivo.** Lista con estado, rutas, paradas, distancia y costo.

**Petición.** `GET http://rutas:5118/api/v1/rutas/planes?microhub_id=1`

```http
Accept: application/json
X-Traza-Id: 5ca59c6c-6a86-49ec-8c6d-9ffea1d32f43
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 40 ms · traza `5ca59c6c-6a86-49ec-8c6d-9ffea1d32f43`

```json
{
  "datos": [
    {
      "id": 119,
      "estado": "confirmado",
      "version": 4,
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "fecha": "2026-11-26",
      "rutas": 2,
      "paradas": 5,
      "distancia_km": 2.8,
      "costo": 102.6,
      "creado_por": 5,
      "creado_en": "2026-11-26T23:20:56-06:00"
    },
    {
      "id": 116,
      "estado": "confirmado",
      "version": 1,
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "fecha": "2026-11-26",
      "rutas": 2,
      "paradas": 4,
      "distancia_km": 2.42,
      "costo": 82.86,
      "creado_por": 5,
      "creado_en": "2026-11-26T23:17:19-06:00"
    },
    {
      "id": 115,
      "estado": "confirmado",
      "version": 1,
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "fecha": "2026-11-26",
      "rutas": 2,
      "paradas": 4,
      "distancia_km": 2.52,
      "costo": 83.32,
      "creado_por": 5,
      "creado_en": "2026-11-26T23:15:57-06:00"
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

### RUT-13 · Cancelar un plan propuesto · PASA

**Objetivo.** Un plan que no se confirmó se cancela.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes/120/cancelar`

```http
Accept: application/json
X-Traza-Id: 7b45ede0-0dd8-469d-8fab-1d5f31071652
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 76 ms · traza `7b45ede0-0dd8-469d-8fab-1d5f31071652`

```json
{
  "id": 120,
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
            "id": 705,
            "folio": "PED-20261126-000705"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.77,
          "minutos_acum": 6.1
        },
        {
          "orden": 2,
          "pedido": {
            "id": 704,
            "folio": "PED-20261126-000704"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.751679,
          "longitud": -100.366615,
          "tramo_km": 0.29,
          "minutos_acum": 10.9
        },
        {
          "orden": 3,
          "pedido": {
            "id": 706,
            "folio": "PED-20261126-000706"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.751679,
          "longitud": -100.366615,
          "tramo_km": 0.0,
          "minutos_acum": 14.9
        },
        {
          "orden": 4,
          "pedido": {
            "id": 703,
            "folio": "PED-20261126-000703"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.748439,
          "longitud": -100.369944,
          "tramo_km": 0.64,
          "minutos_acum": 20.6
        }
      ],
      "distancia_km": 1.7,
      "minutos": 20.6,
      "costo": 79.64
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
            "id": 707,
            "folio": "PED-20261126-000707"
          },
          "zona": {
            "id": 1,
            "nombre": "San Bernabé Centro"
          },
          "latitud": 25.745527,
          "longitud": -100.362981,
          "tramo_km": 0.38,
          "minutos_acum": 5.0
        }
      ],
      "distancia_km": 0.38,
      "minutos": 5.0,
      "costo": 19.72
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 2,
    "paradas": 5,
    "distancia_km": 2.08,
    "minutos_maximo": 20.6,
    "costo": 99.36
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
X-Traza-Id: e4cf143f-e65e-46fe-a4bb-68db857e26f9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 3
}
```

**Respuesta.** HTTP 422 (esperado 422) · 92 ms · traza `e4cf143f-e65e-46fe-a4bb-68db857e26f9`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "No hay pedidos listos para despachar en ese microhub.",
    "traza_id": "e4cf143f-e65e-46fe-a4bb-68db857e26f9"
  }
}
```

### RUT-15 · Pedidos que no están listos · PASA

**Objetivo.** Un pedido ajeno o no listo se rechaza.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/json
X-Traza-Id: 360e122a-d8fa-401a-b03b-3e79b64d8b9f
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

**Respuesta.** HTTP 422 (esperado 422) · 93 ms · traza `360e122a-d8fa-401a-b03b-3e79b64d8b9f`

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
    "traza_id": "360e122a-d8fa-401a-b03b-3e79b64d8b9f"
  }
}
```

### RUT-16 · El operador planea otro microhub · PASA

**Objetivo.** No puede.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/json
X-Traza-Id: 235825a4-ff3c-4fd4-b057-d9f9b84d376c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "pedido_ids": [
    703,
    704,
    705,
    706,
    707
  ]
}
```

**Respuesta.** HTTP 403 (esperado 403) · 9 ms · traza `235825a4-ff3c-4fd4-b057-d9f9b84d376c`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "235825a4-ff3c-4fd4-b057-d9f9b84d376c"
  }
}
```

### RUT-17 · El auditor intenta planear · PASA

**Objetivo.** Consulta, no planea.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/json
X-Traza-Id: 36154dcf-9165-4951-89ae-6e33d68334cf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1
}
```

**Respuesta.** HTTP 403 (esperado 403) · 28 ms · traza `36154dcf-9165-4951-89ae-6e33d68334cf`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "36154dcf-9165-4951-89ae-6e33d68334cf"
  }
}
```

### RUT-18 · Plan en XML con lista de pedidos · PASA

**Objetivo.** El cuerpo XML lleva la lista de pedidos y se valida contra rutas.xsd.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/xml
X-Traza-Id: a4b06c62-a03e-45b1-89b4-e45dc8a9c03f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><ruta_plan_nuevo xmlns="urn:microhubs:v1"><microhub_id>1</microhub_id><pedido_ids><id>703</id><id>704</id><id>705</id></pedido_ids><metodo>exacto</metodo></ruta_plan_nuevo>
```

**Respuesta.** HTTP 200 (esperado 200) · 164 ms · traza `a4b06c62-a03e-45b1-89b4-e45dc8a9c03f`

```xml
<?xml version='1.0' encoding='utf-8'?>
<ruta_plan xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id xsi:nil="true" /><estado>calculo</estado><version>1</version><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><fecha>2026-11-26</fecha><metodo_pedido>exacto</metodo_pedido><rutas><ruta><repartidor><id>7</id><nombre>Ramiro Alanís Lozano</nombre></repartidor><metodo>TSP exacto</metodo><zonas><nombre_zona>Valles de San Bernabé</nombre_zona></zonas><paradas><parada><orden>1</orden><pedido><id>705</id><folio>PED-20261126-000705</folio></pedido><zona><id>2</id><nombre>Valles de San Bernabé</nombre></zona><latitud>25.753225</latitud><longitud>-100.365213</longitud><tramo_km>0.77</tramo_km><minutos_acum>6.1</minutos_acum></parada><parada><orden>2</orden><pedido><id>704</id><folio>PED-20261126-000704</folio></pedido><zona><id>2</id><nombre>Valles de San Bernabé</nombre></zona><latitud>25.751679</latitud><longitud>-100.366615</longitud><tramo_km>0.29</tramo_km><minutos_acum>10.9</minutos_acum></parada><parada><orden>3</orden><pedido><id>703</id><folio>PED-20261126-000703</folio></pedido><zona><id>2</id><nombre>Valles de San Bernabé</nombre></zona><latitud>25.748439</latitud><longitud>-100.369944</longitud><tramo_km>0.64</tramo_km><minutos_acum>16.6</minutos_acum></parada></paradas><distancia_km>1.7</distancia_km><minutos>16.6</minutos><costo>61.64</costo></ruta></rutas><sin_asignar /><total><rutas>1</rutas><paradas>3</paradas><distancia_km>1.7</distancia_km><minutos_maximo>16.6</minutos_maximo><costo>61.64</costo></total><cambios /><supuestos_usados><supuesto><clave>velocidad_reparto_kmh</clave><valor>22</valor><modificado>false</modificado></supuesto><supuesto><clave>tiempo_servicio_min</clave><valor>4</valor><modificado>false</modificado></supuesto><supuesto><clave>costo_km_reparto</clave><valor>4.5</valor><modificado>false</modificado></supuesto><supuesto><clave>costo_base_entrega</clave><valor>18</valor><modificado>false</modificado></supuesto><supuesto><clave>max_paradas_repartidor</clave><valor>8</valor><modificado>false</modificado></supuesto><supuesto><clave>factor_rodeo_distancia</clave><valor>1.3</valor><modificado>false</modificado></supuesto></supuestos_usados></ruta_plan>
```

### RUT-19 · Supuestos de las rutas · PASA

**Objetivo.** Velocidad, tiempo por parada, costo por km, tope de paradas y rodeo.

**Petición.** `GET http://rutas:5118/api/v1/rutas/supuestos`

```http
Accept: application/json
X-Traza-Id: 64c92693-8e7d-485b-9784-7632c10ce3db
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 35 ms · traza `64c92693-8e7d-485b-9784-7632c10ce3db`

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
X-Traza-Id: 9e71dac0-e65d-49da-92ca-23680dc54282
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

**Respuesta.** HTTP 202 (esperado 202) · 734 ms · traza `9e71dac0-e65d-49da-92ca-23680dc54282`

```json
{
  "id": "493db2f2-6f63-437e-928d-29ee4bcf0ca3",
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
  "creado_en": "2026-11-26T23:20:58-06:00",
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
    "id": "493db2f2-6f63-437e-928d-29ee4bcf0ca3",
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

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones/493db2f2-6f63-437e-928d-29ee4bcf0ca3`

```http
Accept: application/json
X-Traza-Id: 49420006-8f35-4608-850a-af024482b0a0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 36 ms · traza `49420006-8f35-4608-850a-af024482b0a0`

```json
{
  "id": "493db2f2-6f63-437e-928d-29ee4bcf0ca3",
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
  "creado_en": "2026-11-26T23:20:58-06:00",
  "inicio_en": "2026-11-26T23:20:59-06:00",
  "fin_en": "2026-11-26T23:20:59-06:00",
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

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones/493db2f2-6f63-437e-928d-29ee4bcf0ca3/repetir`

```http
Accept: application/json
X-Traza-Id: 0101e620-b5f5-4497-b916-fe83b8344f7d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 202 (esperado 202) · 106 ms · traza `0101e620-b5f5-4497-b916-fe83b8344f7d`

```json
{
  "id": "959217d7-2907-41b8-996e-03d74628cc7b",
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
  "repeticion_de": "493db2f2-6f63-437e-928d-29ee4bcf0ca3",
  "reproducible": null,
  "error": null,
  "creado_por": 5,
  "creado_en": "2026-11-26T23:20:59-06:00",
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

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones/959217d7-2907-41b8-996e-03d74628cc7b`

```http
Accept: application/json
X-Traza-Id: 8d40cb8e-0ba1-441d-9280-ed3f3f652945
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 58 ms · traza `8d40cb8e-0ba1-441d-9280-ed3f3f652945`

```json
{
  "id": "959217d7-2907-41b8-996e-03d74628cc7b",
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
  "repeticion_de": "493db2f2-6f63-437e-928d-29ee4bcf0ca3",
  "reproducible": true,
  "error": null,
  "creado_por": 5,
  "creado_en": "2026-11-26T23:20:59-06:00",
  "inicio_en": "2026-11-26T23:21:01-06:00",
  "fin_en": "2026-11-26T23:21:01-06:00",
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
    "id": "493db2f2-6f63-437e-928d-29ee4bcf0ca3",
    "estado": "terminada",
    "huella": "7b88bea8fcb6e15b0dc9714e258549fc8ff623fb13d10d91c72f63b04deb0054",
    "repite_a": null
  },
  {
    "id": "959217d7-2907-41b8-996e-03d74628cc7b",
    "estado": "terminada",
    "huella": "7b88bea8fcb6e15b0dc9714e258549fc8ff623fb13d10d91c72f63b04deb0054",
    "repite_a": "493db2f2-6f63-437e-928d-29ee4bcf0ca3"
  }
]
```

### SIM-05 · Otra semilla, otro resultado · PASA

**Objetivo.** Misma entrada con semilla 12: la huella cambia.

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones/fd0bc377-587d-4bb6-881f-6950fcf5a3f0`

```http
Accept: application/json
X-Traza-Id: 043c0df4-7750-4cb9-b7f8-5668925808a8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 25 ms · traza `043c0df4-7750-4cb9-b7f8-5668925808a8`

```json
{
  "id": "fd0bc377-587d-4bb6-881f-6950fcf5a3f0",
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
  "creado_en": "2026-11-26T23:21:02-06:00",
  "inicio_en": "2026-11-26T23:21:03-06:00",
  "fin_en": "2026-11-26T23:21:03-06:00",
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

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/comparacion?ids=493db2f2-6f63-437e-928d-29ee4bcf0ca3,fd0bc377-587d-4bb6-881f-6950fcf5a3f0`

```http
Accept: application/json
X-Traza-Id: 8e1ae7f5-11ef-463c-be4c-77e81bc65309
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 46 ms · traza `8e1ae7f5-11ef-463c-be4c-77e81bc65309`

```json
{
  "ejecuciones": [
    {
      "id": "493db2f2-6f63-437e-928d-29ee4bcf0ca3",
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
      "id": "fd0bc377-587d-4bb6-881f-6950fcf5a3f0",
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
  "mejor_id": "493db2f2-6f63-437e-928d-29ee4bcf0ca3",
  "criterio": "Mayor utilidad media entre las que pierden dinero en menos de la mitad de las réplicas."
}
```

### SIM-07 · Escenario manual · PASA

**Objetivo.** Sin microhub ni candidato, con todos los datos escritos (el escenario A).

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones`

```http
Accept: application/json
X-Traza-Id: 4460ed24-12ef-44e4-954d-47ef3d6af546
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

**Respuesta.** HTTP 202 (esperado 202) · 181 ms · traza `4460ed24-12ef-44e4-954d-47ef3d6af546`

```json
{
  "id": "86b21c00-943d-42f0-b1c4-f42f0b15125a",
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
  "creado_en": "2026-11-26T23:21:04-06:00",
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

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones/86b21c00-943d-42f0-b1c4-f42f0b15125a`

```http
Accept: application/json
X-Traza-Id: a2478bc0-c2a5-4075-ab5d-c3632a792820
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 31 ms · traza `a2478bc0-c2a5-4075-ab5d-c3632a792820`

```json
{
  "id": "86b21c00-943d-42f0-b1c4-f42f0b15125a",
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
  "creado_en": "2026-11-26T23:21:04-06:00",
  "inicio_en": "2026-11-26T23:21:05-06:00",
  "fin_en": "2026-11-26T23:21:05-06:00",
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
X-Traza-Id: 71ee8cf0-415d-4420-966e-52c4da286521
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "pedidos_dia": 45
}
```

**Respuesta.** HTTP 422 (esperado 422) · 40 ms · traza `71ee8cf0-415d-4420-966e-52c4da286521`

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
    "traza_id": "71ee8cf0-415d-4420-966e-52c4da286521"
  }
}
```

### SIM-10 · Demasiado trabajo · PASA

**Objetivo.** Días × réplicas no puede pasar de 200,000.

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones`

```http
Accept: application/json
X-Traza-Id: 61c97b48-67dd-4f65-95a0-7d4b3e19ee4d
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

**Respuesta.** HTTP 422 (esperado 422) · 536 ms · traza `61c97b48-67dd-4f65-95a0-7d4b3e19ee4d`

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
    "traza_id": "61c97b48-67dd-4f65-95a0-7d4b3e19ee4d"
  }
}
```

### SIM-11 · Cancelar una ejecución · PASA

**Objetivo.** Una ejecución en cola o en curso se puede cancelar.

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones/1685cb65-6b1b-4173-be8e-2227d9a6c223/cancelar`

```http
Accept: application/json
X-Traza-Id: cdd6761d-9796-42e4-82a6-043f4b379e7e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 98 ms · traza `cdd6761d-9796-42e4-82a6-043f4b379e7e`

```json
{
  "id": "1685cb65-6b1b-4173-be8e-2227d9a6c223",
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
  "creado_en": "2026-11-26T23:21:07-06:00",
  "inicio_en": null,
  "fin_en": "2026-11-26T23:21:07-06:00",
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
    "id": "1685cb65-6b1b-4173-be8e-2227d9a6c223",
    "estado": "cancelada",
    "fin": true,
    "sin_resultados": true
  }
]
```

### SIM-12 · Cancelar una cancelada · PASA

**Objetivo.** Solo se cancela lo que está en cola o en curso.

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones/1685cb65-6b1b-4173-be8e-2227d9a6c223/cancelar`

```http
Accept: application/json
X-Traza-Id: 48b42e4a-90c5-41fd-a18e-5b5d389f2fa5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 409 (esperado 409) · 47 ms · traza `48b42e4a-90c5-41fd-a18e-5b5d389f2fa5`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Solo se cancela una ejecución en cola o en curso; esta está cancelada.",
    "traza_id": "48b42e4a-90c5-41fd-a18e-5b5d389f2fa5"
  }
}
```

### SIM-13 · Ejecuciones · PASA

**Objetivo.** Lista paginada, la más reciente primero.

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones?por_pagina=5`

```http
Accept: application/json
X-Traza-Id: e874c42a-6c76-4894-9a52-bc3126b1b5d7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 54 ms · traza `e874c42a-6c76-4894-9a52-bc3126b1b5d7`

```json
{
  "datos": [
    {
      "id": "1685cb65-6b1b-4173-be8e-2227d9a6c223",
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
      "creado_en": "2026-11-26T23:21:07-06:00",
      "fin_en": "2026-11-26T23:21:07-06:00"
    },
    {
      "id": "86b21c00-943d-42f0-b1c4-f42f0b15125a",
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
      "creado_en": "2026-11-26T23:21:04-06:00",
      "fin_en": "2026-11-26T23:21:05-06:00"
    },
    {
      "id": "fd0bc377-587d-4bb6-881f-6950fcf5a3f0",
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
      "creado_en": "2026-11-26T23:21:02-06:00",
      "fin_en": "2026-11-26T23:21:03-06:00"
    },
    {
      "id": "959217d7-2907-41b8-996e-03d74628cc7b",
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
      "creado_en": "2026-11-26T23:20:59-06:00",
      "fin_en": "2026-11-26T23:21:01-06:00"
    },
    {
      "id": "493db2f2-6f63-437e-928d-29ee4bcf0ca3",
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
      "creado_en": "2026-11-26T23:20:58-06:00",
      "fin_en": "2026-11-26T23:20:59-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 13,
    "paginas": 3
  }
}
```

### SIM-14 · El auditor consulta simulaciones · PASA

**Objetivo.** Sin simulacion.ver.

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones`

```http
Accept: application/json
X-Traza-Id: 822a2901-40c6-4d6e-883b-4c011a47ba5c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 25 ms · traza `822a2901-40c6-4d6e-883b-4c011a47ba5c`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "822a2901-40c6-4d6e-883b-4c011a47ba5c"
  }
}
```

### SIM-15 · El operador simula · PASA

**Objetivo.** Sin simulacion.ejecutar.

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones`

```http
Accept: application/json
X-Traza-Id: 2a3c4af2-6c01-49c2-bc3c-3179156ef239
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1
}
```

**Respuesta.** HTTP 403 (esperado 403) · 26 ms · traza `2a3c4af2-6c01-49c2-bc3c-3179156ef239`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "2a3c4af2-6c01-49c2-bc3c-3179156ef239"
  }
}
```

### SIM-16 · Poner en cola (XML) · PASA

**Objetivo.** Entrada y salida en XML, validadas contra simulacion.xsd.

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones`

```http
Accept: application/xml
X-Traza-Id: 1e1c2914-e85a-4a37-9753-24f7a2e2ceb5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><simulacion_nueva xmlns="urn:microhubs:v1"><microhub_id>1</microhub_id><dias>5</dias><replicas>20</replicas><semilla>3</semilla></simulacion_nueva>
```

**Respuesta.** HTTP 202 (esperado 202) · 640 ms · traza `1e1c2914-e85a-4a37-9753-24f7a2e2ceb5`

```xml
<?xml version='1.0' encoding='utf-8'?>
<simulacion_ejecucion xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>f0c0e84e-f6d6-4ac7-a654-8f7899fd9907</id><nombre>Simulación de Microhub San Bernabé Centro 2026-11-26</nombre><estado>en_cola</estado><objeto><tipo>microhub</tipo><id>1</id><nombre>Microhub San Bernabé Centro</nombre></objeto><semilla>3</semilla><version_modelo>1.0</version_modelo><dias>5</dias><replicas>20</replicas><entrada><pedidos_dia>23.6</pedidos_dia><ticket>134.83</ticket><margen_bruto>0.28</margen_bruto><costos_fijos_mes>69500</costos_fijos_mes><costo_variable_pedido>32.61</costo_variable_pedido><dias_mes>30</dias_mes><operadores>3</operadores><repartidores>3</repartidores><capacidad_fisica>150</capacidad_fisica><horas>10</horas><distancia_km>2.4</distancia_km><ausentismo>0.05</ausentismo><variacion_demanda>0.1</variacion_demanda><indice_semanal><indice>0.893</indice><indice>0.844</indice><indice>0.884</indice><indice>0.937</indice><indice>1.154</indice><indice>1.303</indice><indice>1.028</indice></indice_semanal><dia_inicio>4</dia_inicio><origen_de_datos><dato><dato>costos_fijos</dato><fuente>costos</fuente></dato><dato><dato>costo_variable_pedido</dato><fuente>costos</fuente></dato><dato><dato>ticket</dato><fuente>demanda</fuente></dato><dato><dato>margen_bruto</dato><fuente>configuracion</fuente></dato><dato><dato>pedidos_dia</dato><fuente>demanda_repartida</fuente></dato><dato><dato>operadores</dato><fuente>capacidad</fuente></dato><dato><dato>repartidores</dato><fuente>capacidad</fuente></dato><dato><dato>capacidad_fisica</dato><fuente>capacidad</fuente></dato><dato><dato>horas</dato><fuente>configuracion</fuente></dato><dato><dato>distancia_km</dato><fuente>configuracion</fuente></dato><dato><dato>ausentismo</dato><fuente>configuracion</fuente></dato><dato><dato>variacion_demanda</dato><fuente>configuracion</fuente></dato><dato><dato>indice_semanal</dato><fuente>demanda</fuente></dato></origen_de_datos></entrada><resultados xsi:nil="true" /><huella xsi:nil="true" /><repeticion_de xsi:nil="true" /><reproducible xsi:nil="true" /><error xsi:nil="true" /><creado_por>5</creado_por><creado_en>2026-11-26T23:21:08-06:00</creado_en><inicio_en xsi:nil="true" /><fin_en xsi:nil="true" /><supuestos_usados><supuesto><clave>picking_pedidos_hora</clave><valor>10</valor><modificado>false</modificado></supuesto><supuesto><clave>packing_pedidos_hora</clave><valor>20</valor><modificado>false</modificado></supuesto><supuesto><clave>despacho_pedidos_hora</clave><valor>30</valor><modificado>false</modificado></supuesto><supuesto><clave>velocidad_reparto_kmh</clave><valor>22</valor><modificado>false</modificado></supuesto><supuesto><clave>tiempo_servicio_min</clave><valor>4</valor><modificado>false</modificado></supuesto><supuesto><clave>paradas_por_viaje</clave><valor>3</valor><modificado>false</modificado></supuesto><supuesto><clave>horas_turno</clave><valor>10</valor><modificado>false</modificado></supuesto><supuesto><clave>umbral_utilizacion_riesgo</clave><valor>85</valor><modificado>false</modificado></supuesto><supuesto><clave>sim_ausentismo</clave><valor>0.05</valor><modificado>false</modificado></supuesto><supuesto><clave>sim_variacion_demanda</clave><valor>0.1</valor><modificado>false</modificado></supuesto></supuestos_usados></simulacion_ejecucion>
```

### SIM-17 · Una ejecución inexistente · PASA

**Objetivo.** Un identificador que no existe.

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones/144afe3c-1072-488b-9857-c52952129149`

```http
Accept: application/json
X-Traza-Id: aab697d8-5fdb-4bfe-9852-da61ff69d2ae
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 28 ms · traza `aab697d8-5fdb-4bfe-9852-da61ff69d2ae`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe esa ejecución.",
    "traza_id": "aab697d8-5fdb-4bfe-9852-da61ff69d2ae"
  }
}
```

### SIM-18 · Supuestos de la simulación · PASA

**Objetivo.** Réplicas, ausentismo, variación de la demanda y semilla.

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/supuestos`

```http
Accept: application/json
X-Traza-Id: 56570263-1486-49d4-a2f3-ce712cb91565
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 37 ms · traza `56570263-1486-49d4-a2f3-ce712cb91565`

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

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b091347f796dcc0841d6cde/enlace`

```http
Accept: application/json
X-Traza-Id: 9a302d82-7c81-4ab2-84d6-62196f996ec1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 29 ms · traza `9a302d82-7c81-4ab2-84d6-62196f996ec1`

```json
{
  "id": "6b091347f796dcc0841d6cde",
  "nombre": "evidencia-enlace.pdf",
  "url_firmada": "http://documentos:5107/api/v1/documentos/descarga?k=document…(207 caracteres)",
  "metodo": "GET",
  "segundos": 300,
  "expira_en": "2026-11-26T23:26:11-06:00"
}
```

**Explicación.** En la nube la URL es una firmada V4 de Cloud Storage; en local apunta al propio servicio. La base de datos no guarda el archivo.

**Evidencia en PostgreSQL.** `SELECT fecha, modulo, accion, detalle FROM auditoria WHERE entidad = 'documento' AND entidad_id = %s ORDER BY id`

```json
[
  {
    "fecha": "2026-11-26 23:21:11.712119-06:00",
    "modulo": "documentos",
    "accion": "alta",
    "detalle": "evidencia-enlace.pdf (42 bytes) a usuario 7."
  },
  {
    "fecha": "2026-11-26 23:21:11.742911-06:00",
    "modulo": "documentos",
    "accion": "descarga",
    "detalle": "Enlace de descarga de evidencia-enlace.pdf (caduca en 300 s)."
  }
]
```

### ENL-02 · Descargar con el enlace firmado · PASA

**Objetivo.** El enlace funciona sin token: la firma es el permiso.

**Petición.** `GET http://documentos:5107/api/v1/documentos/descarga?k=documentos%2F2026%2F11%2F6b091347f796dcc0841d6cde.pdf&e=1795757171&n=evidencia-enlace.pdf&t=application%2Fpdf&s=on96CJ3DppIRm4LIPsHQbRjahZOaq0GMZMiJ3NCYjAE`

```http
Accept: application/json
X-Traza-Id: da1d0e82-5d7d-4d8f-81f4-29967df0fe4a
```

**Respuesta.** HTTP 200 (esperado 200) · 10 ms · traza `da1d0e82-5d7d-4d8f-81f4-29967df0fe4a`

```json
%PDF-1.4 evidencia de enlace firmado %%EOF
```

### ENL-03 · Enlace manipulado · PASA

**Objetivo.** Cambiar un carácter de la firma lo invalida.

**Petición.** `GET http://documentos:5107/api/v1/documentos/descarga?k=documentos%2F2026%2F11%2F6b091347f796dcc0841d6cde.pdf&e=1795757171&n=evidencia-enlace.pdf&t=application%2Fpdf&s=on96CJ3DppIRm4LIPsHQbRjahZOaq0GMZMiJ3NCYjAA`

```http
Accept: application/json
X-Traza-Id: 837c701d-a054-494a-95e7-0d32a7374563
```

**Respuesta.** HTTP 403 (esperado 403) · 7 ms · traza `837c701d-a054-494a-95e7-0d32a7374563`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "El enlace de descarga no es válido o ya caducó.",
    "traza_id": "837c701d-a054-494a-95e7-0d32a7374563"
  }
}
```

## Servicio auditoria-monitoreo · puerto 5126

### MNT-01 · Forzar una verificación de todos los servicios · PASA

**Objetivo.** Pregunta la salud de cada servicio y guarda el resultado.

**Petición.** `POST http://auditoria-monitoreo:5126/api/v1/monitoreo/verificaciones`

```http
Accept: application/json
X-Traza-Id: 65d2e57f-52eb-4b6f-8b7e-f572cd7030d6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 201 (esperado 201) · 202 ms · traza `65d2e57f-52eb-4b6f-8b7e-f572cd7030d6`

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
      "tiempo_ms": 26.2,
      "error": null
    },
    {
      "servicio": "usuarios",
      "estado": "ok",
      "tiempo_ms": 23.0,
      "error": null
    },
    {
      "servicio": "productos",
      "estado": "ok",
      "tiempo_ms": 29.1,
      "error": null
    },
    {
      "servicio": "pedidos",
      "estado": "ok",
      "tiempo_ms": 28.6,
      "error": null
    },
    {
      "servicio": "entregas",
      "estado": "ok",
      "tiempo_ms": 34.6,
      "error": null
    },
    {
      "servicio": "planeacion",
      "estado": "ok",
      "tiempo_ms": 30.3,
      "error": null
    },
    {
      "servicio": "documentos",
      "estado": "ok",
      "tiempo_ms": 30.2,
      "error": null
    },
    {
      "servicio": "zonas",
      "estado": "ok",
      "tiempo_ms": 30.0,
      "error": null
    },
    {
      "servicio": "microhubs",
      "estado": "ok",
      "tiempo_ms": 25.3,
      "error": null
    },
    {
      "servicio": "seguimiento",
      "estado": "ok",
      "tiempo_ms": 30.3,
      "error": null
    },
    {
      "servicio": "inventario",
      "estado": "ok",
      "tiempo_ms": 27.5,
      "error": null
    },
    {
      "servicio": "precios",
      "estado": "ok",
      "tiempo_ms": 25.2,
      "error": null
    },
    {
      "servicio": "proveedores",
      "estado": "ok",
      "tiempo_ms": 26.2,
      "error": null
    },
    {
      "servicio": "abastecimiento",
      "estado": "ok",
      "tiempo_ms": 24.4,
      "error": null
    },
    {
      "servicio": "demanda",
      "estado": "ok",
      "tiempo_ms": 26.4,
      "error": null
    },
    {
      "servicio": "cobertura",
      "estado": "ok",
      "tiempo_ms": 26.6,
      "error": null
    },
    {
      "servicio": "capacidad",
      "estado": "ok",
      "tiempo_ms": 22.8,
      "error": null
    },
    {
      "servicio": "rutas",
      "estado": "ok",
      "tiempo_ms": 31.6,
      "error": null
    },
    {
      "servicio": "costos",
      "estado": "ok",
      "tiempo_ms": 22.6,
      "error": null
    },
    {
      "servicio": "punto-equilibrio",
      "estado": "ok",
      "tiempo_ms": 20.2,
      "error": null
    },
    {
      "servicio": "simulacion",
      "estado": "ok",
      "tiempo_ms": 27.5,
      "error": null
    },
    {
      "servicio": "surtido",
      "estado": "ok",
      "tiempo_ms": 25.5,
      "error": null
    },
    {
      "servicio": "notificaciones",
      "estado": "ok",
      "tiempo_ms": 23.6,
      "error": null
    },
    {
      "servicio": "reportes",
      "estado": "ok",
      "tiempo_ms": 23.8,
      "error": null
    },
    {
      "servicio": "sincronizacion",
      "estado": "ok",
      "tiempo_ms": 22.9,
      "error": null
    },
    {
      "servicio": "auditoria-monitoreo",
      "estado": "ok",
      "tiempo_ms": 23.9,
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
X-Traza-Id: 47e48311-18a6-4b5e-9013-22d8cc7fc122
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 105 ms · traza `47e48311-18a6-4b5e-9013-22d8cc7fc122`

```json
{
  "generado_en": "2026-11-26T23:21:12-06:00",
  "resumen": {
    "total": 26,
    "ok": 26,
    "degradados": 0,
    "caidos": 0,
    "sin_datos": 0,
    "alertas_abiertas": 0,
    "monitor_activo": true,
    "intervalo_seg": 30,
    "ultima_ronda": "2026-11-26T23:21:12-06:00"
  },
  "servicios": [
    {
      "servicio": "auth",
      "puerto": 5101,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 26.2,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 384,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "usuarios",
      "puerto": 5102,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 23.0,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 68,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "productos",
      "puerto": 5103,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 29.1,
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
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "pedidos",
      "puerto": 5104,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 28.6,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 422,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "entregas",
      "puerto": 5105,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 34.6,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "ok",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 189,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "planeacion",
      "puerto": 5106,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 30.3,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "ok",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 110,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "documentos",
      "puerto": 5107,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 30.2,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "ok",
        "bucket": "ok"
      },
      "error": null,
      "peticiones_hora": 122,
      "errores_5xx_hora": 1,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "zonas",
      "puerto": 5108,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
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
      "peticiones_hora": 538,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "microhubs",
      "puerto": 5109,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 25.3,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 61,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "seguimiento",
      "puerto": 5110,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 30.3,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "ok",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 40,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "inventario",
      "puerto": 5111,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 27.5,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 358,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "precios",
      "puerto": 5112,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
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
      "peticiones_hora": 156,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "proveedores",
      "puerto": 5113,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 26.2,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 142,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "abastecimiento",
      "puerto": 5114,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 24.4,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 210,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "demanda",
      "puerto": 5115,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 26.4,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 212,
      "errores_5xx_hora": 1,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "cobertura",
      "puerto": 5116,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 26.6,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 188,
      "errores_5xx_hora": 2,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "capacidad",
      "puerto": 5117,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 22.8,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 111,
      "errores_5xx_hora": 1,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "rutas",
      "puerto": 5118,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 31.6,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 126,
      "errores_5xx_hora": 2,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "costos",
      "puerto": 5119,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 22.6,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 233,
      "errores_5xx_hora": 1,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "punto-equilibrio",
      "puerto": 5120,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 20.2,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 150,
      "errores_5xx_hora": 3,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "simulacion",
      "puerto": 5121,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 27.5,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 185,
      "errores_5xx_hora": 3,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "surtido",
      "puerto": 5122,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
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
      "peticiones_hora": 99,
      "errores_5xx_hora": 3,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "notificaciones",
      "puerto": 5124,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 23.6,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 96,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "reportes",
      "puerto": 5123,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 23.8,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "no_aplica",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 208,
      "errores_5xx_hora": 4,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "sincronizacion",
      "puerto": 5125,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 22.9,
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
      "servicio": "auditoria-monitoreo",
      "puerto": 5126,
      "estado": "ok",
      "verificado_en": "2026-11-26T23:21:12-06:00",
      "antiguedad_seg": 0,
      "tiempo_ms": 23.9,
      "version": "1.0.0",
      "dependencias": {
        "postgres": "ok",
        "redis": "ok",
        "mongo": "ok",
        "bucket": "no_aplica"
      },
      "error": null,
      "peticiones_hora": 336,
      "errores_5xx_hora": 0,
      "disponibilidad_24h_pct": 100.0,
      "bajo_objetivo": false
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
X-Traza-Id: f38ef958-a660-4d21-8b89-1fa12dcc9137
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 116 ms · traza `f38ef958-a660-4d21-8b89-1fa12dcc9137`

```xml
<?xml version='1.0' encoding='utf-8'?>
<monitoreo_estado xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><generado_en>2026-11-26T23:21:12-06:00</generado_en><resumen><total>26</total><ok>26</ok><degradados>0</degradados><caidos>0</caidos><sin_datos>0</sin_datos><alertas_abiertas>0</alertas_abiertas><monitor_activo>true</monitor_activo><intervalo_seg>30</intervalo_seg><ultima_ronda>2026-11-26T23:21:12-06:00</ultima_ronda></resumen><servicios><servicio><servicio>auth</servicio><puerto>5101</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>26.2</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>384</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>usuarios</servicio><puerto>5102</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>23</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>68</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>productos</servicio><puerto>5103</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>29.1</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>70</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>pedidos</servicio><puerto>5104</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>28.6</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>422</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>entregas</servicio><puerto>5105</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>34.6</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>ok</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>189</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>planeacion</servicio><puerto>5106</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>30.3</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>ok</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>110</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>documentos</servicio><puerto>5107</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>30.2</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>ok</mongo><bucket>ok</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>122</peticiones_hora><errores_5xx_hora>1</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>zonas</servicio><puerto>5108</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>30</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>538</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>microhubs</servicio><puerto>5109</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>25.3</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>61</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>seguimiento</servicio><puerto>5110</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>30.3</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>ok</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>40</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>inventario</servicio><puerto>5111</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>27.5</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>358</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>precios</servicio><puerto>5112</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>25.2</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>156</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>proveedores</servicio><puerto>5113</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>26.2</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>142</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>abastecimiento</servicio><puerto>5114</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>24.4</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>210</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>demanda</servicio><puerto>5115</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>26.4</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>212</peticiones_hora><errores_5xx_hora>1</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>cobertura</servicio><puerto>5116</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>26.6</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>188</peticiones_hora><errores_5xx_hora>2</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>capacidad</servicio><puerto>5117</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>22.8</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>111</peticiones_hora><errores_5xx_hora>1</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>rutas</servicio><puerto>5118</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>31.6</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>126</peticiones_hora><errores_5xx_hora>2</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>costos</servicio><puerto>5119</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>22.6</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>233</peticiones_hora><errores_5xx_hora>1</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>punto-equilibrio</servicio><puerto>5120</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>20.2</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>150</peticiones_hora><errores_5xx_hora>3</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>simulacion</servicio><puerto>5121</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>27.5</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>185</peticiones_hora><errores_5xx_hora>3</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>surtido</servicio><puerto>5122</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>25.5</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>99</peticiones_hora><errores_5xx_hora>3</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>notificaciones</servicio><puerto>5124</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>23.6</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>96</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>reportes</servicio><puerto>5123</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>23.8</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>208</peticiones_hora><errores_5xx_hora>4</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>sincronizacion</servicio><puerto>5125</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>22.9</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>no_aplica</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>134</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio><servicio><servicio>auditoria-monitoreo</servicio><puerto>5126</puerto><estado>ok</estado><verificado_en>2026-11-26T23:21:12-06:00</verificado_en><antiguedad_seg>0</antiguedad_seg><tiempo_ms>23.9</tiempo_ms><version>1.0.0</version><dependencias><postgres>ok</postgres><redis>ok</redis><mongo>ok</mongo><bucket>no_aplica</bucket></dependencias><error xsi:nil="true" /><peticiones_hora>337</peticiones_hora><errores_5xx_hora>0</errores_5xx_hora><disponibilidad_24h_pct>100</disponibilidad_24h_pct><bajo_objetivo>false</bajo_objetivo></servicio></servicios><dependencias_caidas /></monitoreo_estado>
```

### MNT-04 · Historial de un servicio · PASA

**Objetivo.** Serie de verificaciones, la más reciente primero.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/monitoreo/servicios/pedidos/historial?por_pagina=3`

```http
Accept: application/json
X-Traza-Id: 24594317-6269-476b-9082-d86e3161f03f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 54 ms · traza `24594317-6269-476b-9082-d86e3161f03f`

```json
{
  "datos": [
    {
      "verificado_en": "2026-11-26T23:21:12-06:00",
      "estado": "ok",
      "http_status": 200,
      "tiempo_ms": 28.6,
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
      "verificado_en": "2026-11-26T23:20:59-06:00",
      "estado": "ok",
      "http_status": 200,
      "tiempo_ms": 46.6,
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
      "verificado_en": "2026-11-26T23:20:29-06:00",
      "estado": "ok",
      "http_status": 200,
      "tiempo_ms": 22.2,
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
    "total": 25,
    "paginas": 9
  }
}
```

### MNT-05 · Disponibilidad de las últimas 24 horas · PASA

**Objetivo.** Porcentaje disponible, salud plena y percentiles p50 y p95.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/monitoreo/disponibilidad?horas=24`

```http
Accept: application/json
X-Traza-Id: 0e5ae558-2960-4c4f-bdb9-cd253ab5c4b8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 54 ms · traza `0e5ae558-2960-4c4f-bdb9-cd253ab5c4b8`

```json
{
  "horas": 24,
  "objetivo_pct": 99.0,
  "servicios": [
    {
      "servicio": "auth",
      "verificaciones": 25,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 26.2,
      "tiempo_p95_ms": 65.1,
      "tiempo_max_ms": 121.2,
      "bajo_objetivo": false
    },
    {
      "servicio": "usuarios",
      "verificaciones": 25,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 25.9,
      "tiempo_p95_ms": 61.8,
      "tiempo_max_ms": 94.3,
      "bajo_objetivo": false
    },
    {
      "servicio": "productos",
      "verificaciones": 25,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 35.5,
      "tiempo_p95_ms": 88.7,
      "tiempo_max_ms": 99.0,
      "bajo_objetivo": false
    },
    {
      "servicio": "pedidos",
      "verificaciones": 25,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 28.9,
      "tiempo_p95_ms": 69.2,
      "tiempo_max_ms": 93.2,
      "bajo_objetivo": false
    },
    {
      "servicio": "entregas",
      "verificaciones": 25,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 38.0,
      "tiempo_p95_ms": 74.3,
      "tiempo_max_ms": 76.1,
      "bajo_objetivo": false
    },
    {
      "servicio": "planeacion",
      "verificaciones": 25,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 34.1,
      "tiempo_p95_ms": 71.0,
      "tiempo_max_ms": 82.3,
      "bajo_objetivo": false
    },
    {
      "servicio": "documentos",
      "verificaciones": 25,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 32.0,
      "tiempo_p95_ms": 64.4,
      "tiempo_max_ms": 123.3,
      "bajo_objetivo": false
    },
    {
      "servicio": "zonas",
      "verificaciones": 27,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 30.3,
      "tiempo_p95_ms": 73.8,
      "tiempo_max_ms": 137.8,
      "bajo_objetivo": false
    },
    {
      "servicio": "microhubs",
      "verificaciones": 25,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 31.4,
      "tiempo_p95_ms": 61.0,
      "tiempo_max_ms": 70.5,
      "bajo_objetivo": false
    },
    {
      "servicio": "seguimiento",
      "verificaciones": 25,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 34.0,
      "tiempo_p95_ms": 70.4,
      "tiempo_max_ms": 84.1,
      "bajo_objetivo": false
    },
    {
      "servicio": "inventario",
      "verificaciones": 25,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 28.4,
      "tiempo_p95_ms": 56.9,
      "tiempo_max_ms": 100.6,
      "bajo_objetivo": false
    },
    {
      "servicio": "precios",
      "verificaciones": 25,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 30.8,
      "tiempo_p95_ms": 55.4,
      "tiempo_max_ms": 150.3,
      "bajo_objetivo": false
    },
    {
      "servicio": "proveedores",
      "verificaciones": 25,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 32.1,
      "tiempo_p95_ms": 58.9,
      "tiempo_max_ms": 70.1,
      "bajo_objetivo": false
    },
    {
      "servicio": "abastecimiento",
      "verificaciones": 25,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 30.4,
      "tiempo_p95_ms": 64.5,
      "tiempo_max_ms": 149.6,
      "bajo_objetivo": false
    },
    {
      "servicio": "demanda",
      "verificaciones": 25,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 30.0,
      "tiempo_p95_ms": 58.7,
      "tiempo_max_ms": 86.1,
      "bajo_objetivo": false
    },
    {
      "servicio": "cobertura",
      "verificaciones": 25,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 28.6,
      "tiempo_p95_ms": 46.2,
      "tiempo_max_ms": 65.9,
      "bajo_objetivo": false
    },
    {
      "servicio": "capacidad",
      "verificaciones": 25,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 31.3,
      "tiempo_p95_ms": 57.8,
      "tiempo_max_ms": 92.1,
      "bajo_objetivo": false
    },
    {
      "servicio": "rutas",
      "verificaciones": 25,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 31.0,
      "tiempo_p95_ms": 51.9,
      "tiempo_max_ms": 65.7,
      "bajo_objetivo": false
    },
    {
      "servicio": "costos",
      "verificaciones": 25,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 29.9,
      "tiempo_p95_ms": 50.0,
      "tiempo_max_ms": 52.1,
      "bajo_objetivo": false
    },
    {
      "servicio": "punto-equilibrio",
      "verificaciones": 25,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 32.6,
      "tiempo_p95_ms": 49.1,
      "tiempo_max_ms": 53.5,
      "bajo_objetivo": false
    },
    {
      "servicio": "simulacion",
      "verificaciones": 25,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 30.2,
      "tiempo_p95_ms": 65.8,
      "tiempo_max_ms": 77.8,
      "bajo_objetivo": false
    },
    {
      "servicio": "surtido",
      "verificaciones": 25,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 27.5,
      "tiempo_p95_ms": 58.8,
      "tiempo_max_ms": 95.1,
      "bajo_objetivo": false
    },
    {
      "servicio": "notificaciones",
      "verificaciones": 25,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 29.7,
      "tiempo_p95_ms": 45.7,
      "tiempo_max_ms": 67.5,
      "bajo_objetivo": false
    },
    {
      "servicio": "reportes",
      "verificaciones": 25,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 30.4,
      "tiempo_p95_ms": 78.8,
      "tiempo_max_ms": 144.2,
      "bajo_objetivo": false
    },
    {
      "servicio": "sincronizacion",
      "verificaciones": 25,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 28.3,
      "tiempo_p95_ms": 50.4,
      "tiempo_max_ms": 90.9,
      "bajo_objetivo": false
    },
    {
      "servicio": "auditoria-monitoreo",
      "verificaciones": 25,
      "caidas": 0,
      "disponibilidad_pct": 100.0,
      "salud_plena_pct": 100.0,
      "tiempo_p50_ms": 28.5,
      "tiempo_p95_ms": 68.6,
      "tiempo_max_ms": 129.2,
      "bajo_objetivo": false
    }
  ]
}
```

### MNT-06 · Tráfico y errores · PASA

**Objetivo.** Peticiones, errores y percentiles de duración por servicio, desde MongoDB.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/monitoreo/metricas?minutos=60`

```http
Accept: application/json
X-Traza-Id: 0ddc6552-a417-4907-8f85-8220b88bfaf3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 51 ms · traza `0ddc6552-a417-4907-8f85-8220b88bfaf3`

```json
{
  "minutos": 60,
  "peticiones_total": 4952,
  "servicios": [
    {
      "servicio": "auth",
      "peticiones": 384,
      "errores_5xx": 0,
      "errores_4xx": 23,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 275,
      "duracion_p95_ms": 391,
      "duracion_p99_ms": 477
    },
    {
      "servicio": "usuarios",
      "peticiones": 68,
      "errores_5xx": 0,
      "errores_4xx": 35,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 26,
      "duracion_p95_ms": 151,
      "duracion_p99_ms": 170
    },
    {
      "servicio": "productos",
      "peticiones": 70,
      "errores_5xx": 0,
      "errores_4xx": 27,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 37,
      "duracion_p95_ms": 92,
      "duracion_p99_ms": 132
    },
    {
      "servicio": "pedidos",
      "peticiones": 422,
      "errores_5xx": 0,
      "errores_4xx": 43,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 62,
      "duracion_p95_ms": 117,
      "duracion_p99_ms": 226
    },
    {
      "servicio": "entregas",
      "peticiones": 189,
      "errores_5xx": 0,
      "errores_4xx": 37,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 62,
      "duracion_p95_ms": 141,
      "duracion_p99_ms": 172
    },
    {
      "servicio": "planeacion",
      "peticiones": 110,
      "errores_5xx": 0,
      "errores_4xx": 23,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 36,
      "duracion_p95_ms": 161,
      "duracion_p99_ms": 304
    },
    {
      "servicio": "documentos",
      "peticiones": 122,
      "errores_5xx": 1,
      "errores_4xx": 17,
      "tasa_5xx_pct": 0.82,
      "duracion_p50_ms": 29,
      "duracion_p95_ms": 84,
      "duracion_p99_ms": 131
    },
    {
      "servicio": "zonas",
      "peticiones": 538,
      "errores_5xx": 0,
      "errores_4xx": 498,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 0,
      "duracion_p95_ms": 24,
      "duracion_p99_ms": 71
    },
    {
      "servicio": "microhubs",
      "peticiones": 61,
      "errores_5xx": 0,
      "errores_4xx": 19,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 25,
      "duracion_p95_ms": 81,
      "duracion_p99_ms": 99
    },
    {
      "servicio": "seguimiento",
      "peticiones": 40,
      "errores_5xx": 0,
      "errores_4xx": 6,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 29,
      "duracion_p95_ms": 50,
      "duracion_p99_ms": 82
    },
    {
      "servicio": "inventario",
      "peticiones": 358,
      "errores_5xx": 0,
      "errores_4xx": 53,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 57,
      "duracion_p95_ms": 110,
      "duracion_p99_ms": 216
    },
    {
      "servicio": "precios",
      "peticiones": 156,
      "errores_5xx": 0,
      "errores_4xx": 50,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 46,
      "duracion_p95_ms": 121,
      "duracion_p99_ms": 147
    },
    {
      "servicio": "proveedores",
      "peticiones": 142,
      "errores_5xx": 0,
      "errores_4xx": 44,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 57,
      "duracion_p95_ms": 94,
      "duracion_p99_ms": 130
    },
    {
      "servicio": "abastecimiento",
      "peticiones": 210,
      "errores_5xx": 0,
      "errores_4xx": 72,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 83,
      "duracion_p95_ms": 293,
      "duracion_p99_ms": 340
    },
    {
      "servicio": "demanda",
      "peticiones": 212,
      "errores_5xx": 1,
      "errores_4xx": 29,
      "tasa_5xx_pct": 0.47,
      "duracion_p50_ms": 102,
      "duracion_p95_ms": 174,
      "duracion_p99_ms": 303
    },
    {
      "servicio": "cobertura",
      "peticiones": 188,
      "errores_5xx": 2,
      "errores_4xx": 28,
      "tasa_5xx_pct": 1.06,
      "duracion_p50_ms": 45,
      "duracion_p95_ms": 121,
      "duracion_p99_ms": 236
    },
    {
      "servicio": "capacidad",
      "peticiones": 111,
      "errores_5xx": 1,
      "errores_4xx": 29,
      "tasa_5xx_pct": 0.9,
      "duracion_p50_ms": 48,
      "duracion_p95_ms": 136,
      "duracion_p99_ms": 163
    },
    {
      "servicio": "rutas",
      "peticiones": 126,
      "errores_5xx": 2,
      "errores_4xx": 42,
      "tasa_5xx_pct": 1.59,
      "duracion_p50_ms": 82,
      "duracion_p95_ms": 227,
      "duracion_p99_ms": 446
    },
    {
      "servicio": "costos",
      "peticiones": 233,
      "errores_5xx": 1,
      "errores_4xx": 33,
      "tasa_5xx_pct": 0.43,
      "duracion_p50_ms": 46,
      "duracion_p95_ms": 72,
      "duracion_p99_ms": 83
    },
    {
      "servicio": "punto-equilibrio",
      "peticiones": 150,
      "errores_5xx": 3,
      "errores_4xx": 19,
      "tasa_5xx_pct": 2.0,
      "duracion_p50_ms": 158,
      "duracion_p95_ms": 365,
      "duracion_p99_ms": 523
    },
    {
      "servicio": "simulacion",
      "peticiones": 185,
      "errores_5xx": 3,
      "errores_4xx": 43,
      "tasa_5xx_pct": 1.62,
      "duracion_p50_ms": 30,
      "duracion_p95_ms": 598,
      "duracion_p99_ms": 747
    },
    {
      "servicio": "surtido",
      "peticiones": 99,
      "errores_5xx": 3,
      "errores_4xx": 32,
      "tasa_5xx_pct": 3.03,
      "duracion_p50_ms": 47,
      "duracion_p95_ms": 453,
      "duracion_p99_ms": 578
    },
    {
      "servicio": "notificaciones",
      "peticiones": 96,
      "errores_5xx": 0,
      "errores_4xx": 31,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 31,
      "duracion_p95_ms": 104,
      "duracion_p99_ms": 151
    },
    {
      "servicio": "reportes",
      "peticiones": 208,
      "errores_5xx": 4,
      "errores_4xx": 68,
      "tasa_5xx_pct": 1.92,
      "duracion_p50_ms": 50,
      "duracion_p95_ms": 609,
      "duracion_p99_ms": 717
    },
    {
      "servicio": "sincronizacion",
      "peticiones": 134,
      "errores_5xx": 0,
      "errores_4xx": 48,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 53,
      "duracion_p95_ms": 353,
      "duracion_p99_ms": 435
    },
    {
      "servicio": "auditoria-monitoreo",
      "peticiones": 340,
      "errores_5xx": 0,
      "errores_4xx": 124,
      "tasa_5xx_pct": 0.0,
      "duracion_p50_ms": 48,
      "duracion_p95_ms": 180,
      "duracion_p99_ms": 316
    }
  ]
}
```

### MNT-07 · Umbrales y su justificación · PASA

**Objetivo.** Cada umbral con su origen y cómo se calibra.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/monitoreo/supuestos`

```http
Accept: application/json
X-Traza-Id: 7b686e36-4208-4d54-9c42-e21c8b402b48
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 39 ms · traza `7b686e36-4208-4d54-9c42-e21c8b402b48`

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
X-Traza-Id: 7a814ecc-73c1-4b79-b457-dfc20701e863
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 62 ms · traza `7a814ecc-73c1-4b79-b457-dfc20701e863`

```json
{
  "datos": [
    {
      "id": 508,
      "servicio": "zonas",
      "tipo": "latencia_alta",
      "severidad": "media",
      "detalle": "/salud de zonas tardó 20 ms (umbral 0 ms).",
      "abierta_en": "2026-11-26T23:21:12-06:00",
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
    "detalle": "/salud de zonas tardó 20 ms (umbral 0 ms)."
  }
]
```

### MNT-09 · Reconocer una alerta · PASA

**Objetivo.** Queda quién se hizo cargo y cuándo.

**Petición.** `POST http://auditoria-monitoreo:5126/api/v1/monitoreo/alertas/508/reconocer`

```http
Accept: application/json
X-Traza-Id: 8ef6006f-7177-44ca-b875-d8eccd07c0d2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 62 ms · traza `8ef6006f-7177-44ca-b875-d8eccd07c0d2`

```json
{
  "id": 508,
  "servicio": "zonas",
  "tipo": "latencia_alta",
  "severidad": "media",
  "detalle": "/salud de zonas tardó 20 ms (umbral 0 ms).",
  "abierta_en": "2026-11-26T23:21:12-06:00",
  "cerrada_en": null,
  "duracion_seg": 0,
  "reconocida": {
    "por": {
      "id": 1,
      "nombre": "Mauro Castillo Peña"
    },
    "en": "2026-11-26T23:21:12-06:00"
  }
}
```

**Evidencia en PostgreSQL.** `SELECT fecha, accion, detalle, usuario_id FROM auditoria WHERE entidad = 'monitoreo_alerta' AND entidad_id = %s ORDER BY id`

```json
[
  {
    "fecha": "2026-11-26 23:21:12.624814-06:00",
    "accion": "alta",
    "detalle": null,
    "usuario_id": 1
  },
  {
    "fecha": "2026-11-26 23:21:12.759889-06:00",
    "accion": "modificacion",
    "detalle": null,
    "usuario_id": 1
  }
]
```

### MNT-10 · Reconocer sin permiso · PASA

**Objetivo.** El auditor ve el monitoreo pero no lo opera.

**Petición.** `POST http://auditoria-monitoreo:5126/api/v1/monitoreo/alertas/508/reconocer`

```http
Accept: application/json
X-Traza-Id: a8a029a5-45f5-4913-8cea-ef8115715372
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 403 (esperado 403) · 36 ms · traza `a8a029a5-45f5-4913-8cea-ef8115715372`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "a8a029a5-45f5-4913-8cea-ef8115715372"
  }
}
```

### MNT-11 · El operador no ve el monitoreo · PASA

**Objetivo.** Sin monitoreo.ver.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/monitoreo/estado`

```http
Accept: application/json
X-Traza-Id: f50f0c6e-1446-4c48-93ea-fbd993b5c422
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 27 ms · traza `f50f0c6e-1446-4c48-93ea-fbd993b5c422`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "f50f0c6e-1446-4c48-93ea-fbd993b5c422"
  }
}
```

### AUD-01 · Bitácora con filtros · PASA

**Objetivo.** Quién cambió qué, cuándo y desde dónde.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria?modulo=pedidos&por_pagina=3`

```http
Accept: application/json
X-Traza-Id: 67b5b97a-ce33-4142-b751-0f7ea347a9ef
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 57 ms · traza `67b5b97a-ce33-4142-b751-0f7ea347a9ef`

```json
{
  "datos": [
    {
      "id": 22219,
      "fecha": "2026-11-26T23:20:57-06:00",
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
        "id": "707"
      },
      "exitoso": true,
      "detalle": null,
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-26T23:20:54.782629-06:00",
          "nuevo": "2026-11-26T23:20:57.649605-06:00"
        },
        {
          "campo": "cerrado_en",
          "anterior": null,
          "nuevo": "2026-11-26T23:20:57.649605-06:00"
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
      "id": 22216,
      "fecha": "2026-11-26T23:20:57-06:00",
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
        "id": "706"
      },
      "exitoso": true,
      "detalle": null,
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-26T23:20:54.782629-06:00",
          "nuevo": "2026-11-26T23:20:57.649605-06:00"
        },
        {
          "campo": "cerrado_en",
          "anterior": null,
          "nuevo": "2026-11-26T23:20:57.649605-06:00"
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
      "id": 22213,
      "fecha": "2026-11-26T23:20:57-06:00",
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
        "id": "705"
      },
      "exitoso": true,
      "detalle": null,
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-26T23:20:54.782629-06:00",
          "nuevo": "2026-11-26T23:20:57.649605-06:00"
        },
        {
          "campo": "cerrado_en",
          "anterior": null,
          "nuevo": "2026-11-26T23:20:57.649605-06:00"
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
    "total": 5543,
    "paginas": 1848
  }
}
```

**Explicación.** La bitácora es de solo escritura (RN31); los valores de contraseñas nunca aparecen.

### AUD-02 · Accesos al sistema · PASA

**Objetivo.** Inicios, fallos, bloqueos y accesos denegados del periodo.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/accesos`

```http
Accept: application/json
X-Traza-Id: be4d8a79-1162-4b5d-9af2-d1f45fd25b2b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 89 ms · traza `be4d8a79-1162-4b5d-9af2-d1f45fd25b2b`

```json
{
  "desde": "2026-11-19",
  "hasta": "2026-11-26",
  "totales": {
    "login_exitoso": 1433,
    "login_fallido": 53,
    "logout": 31,
    "bloqueo_cuenta": 2,
    "desbloqueo": 0,
    "acceso_denegado": 1426
  },
  "correos_con_mas_fallos": [
    {
      "correo": "planeador@codex.mx",
      "intentos": 11,
      "ultimo_intento": "2026-11-26T23:06:21-06:00"
    },
    {
      "correo": "repartidor1@codex.mx",
      "intentos": 9,
      "ultimo_intento": "2026-11-26T23:06:24-06:00"
    },
    {
      "correo": "auditor@codex.mx",
      "intentos": 7,
      "ultimo_intento": "2026-11-26T23:20:24-06:00"
    },
    {
      "correo": "nadie.c4423816@codex.mx",
      "intentos": 5,
      "ultimo_intento": "2026-11-26T15:32:48-06:00"
    },
    {
      "correo": "no.existe.ola3@codex.mx",
      "intentos": 4,
      "ultimo_intento": "2026-11-25T15:46:41-06:00"
    }
  ],
  "denegados_frecuentes": [
    {
      "detalle": "GET /api/v1/auditoria sin auditoria.ver",
      "veces": 71
    },
    {
      "detalle": "GET /api/v1/auditoria/accesos sin auditoria.ver",
      "veces": 64
    },
    {
      "detalle": "GET /api/v1/auditoria/trazabilidad/inventario sin auditoria.ver",
      "veces": 64
    },
    {
      "detalle": "GET /api/v1/auditoria/trazabilidad/pedido/1 sin auditoria.ver",
      "veces": 64
    },
    {
      "detalle": "GET /api/v1/monitoreo/estado sin monitoreo.ver",
      "veces": 61
    }
  ]
}
```

### AUD-03 · Línea de tiempo de un pedido · PASA

**Objetivo.** Une bitácora, cambios de estado, inventario y archivos del pedido.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/pedido/1`

```http
Accept: application/json
X-Traza-Id: 1211d83b-ffe5-4a33-872c-1410eddc45a5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 109 ms · traza `1211d83b-ffe5-4a33-872c-1410eddc45a5`

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
X-Traza-Id: 93a85ad2-c897-413b-9965-8574705ac128
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 54 ms · traza `93a85ad2-c897-413b-9965-8574705ac128`

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
X-Traza-Id: a84dd672-8179-4efc-a98d-bafeff4ce447
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 48 ms · traza `a84dd672-8179-4efc-a98d-bafeff4ce447`

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
X-Traza-Id: 6336e185-9362-45f4-9941-711ff41461e4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 30 ms · traza `6336e185-9362-45f4-9941-711ff41461e4`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "6336e185-9362-45f4-9941-711ff41461e4"
  }
}
```

**Evidencia en PostgreSQL.** `SELECT fecha, accion, detalle, exitoso FROM auditoria WHERE accion = 'acceso_denegado' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "fecha": "2026-11-26 23:21:13.568887-06:00",
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
X-Traza-Id: 7a092bb9-6b8f-4b6c-822f-39e3d35e1529
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 6 ms · traza `7a092bb9-6b8f-4b6c-822f-39e3d35e1529`

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

**Petición.** `GET http://reportes:5123/api/v1/reportes/indicadores?desde=2026-08-29`

```http
Accept: application/json
X-Traza-Id: 529ac01c-7c5c-4a8e-b184-da2d5dff6c5f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 636 ms · traza `529ac01c-7c5c-4a8e-b184-da2d5dff6c5f`

```json
{
  "desde": "2026-08-29",
  "hasta": "2026-11-26",
  "indicadores": [
    {
      "clave": "********",
      "titulo": "Pedidos del periodo",
      "valor": 421,
      "unidad": "pedidos",
      "fuente": "pedidos"
    },
    {
      "clave": "********",
      "titulo": "Venta del periodo",
      "valor": 65948.8,
      "unidad": "MXN",
      "fuente": "pedidos"
    },
    {
      "clave": "********",
      "titulo": "Ticket promedio",
      "valor": 156.65,
      "unidad": "MXN",
      "fuente": "pedidos"
    },
    {
      "clave": "********",
      "titulo": "Demanda no atendida",
      "valor": 57,
      "unidad": "pedidos",
      "fuente": "pedidos"
    },
    {
      "clave": "********",
      "titulo": "Productos en alerta de inventario",
      "valor": 7,
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
      "valor": 7,
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

**Petición.** `GET http://reportes:5123/api/v1/reportes/comparacion_microhubs?desde=2026-08-29`

```http
Accept: application/json
X-Traza-Id: 4287163e-9e0a-417d-a9b5-88871af1c414
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 1064 ms · traza `4287163e-9e0a-417d-a9b5-88871af1c414`

```json
{
  "reporte": "comparacion_microhubs",
  "familia": "comercial",
  "titulo": "Comparación entre microhubs",
  "generado_en": "2026-11-26T23:21:15-06:00",
  "filtros": {
    "desde": "2026-08-29",
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
        "163",
        "830",
        "27852.00",
        "170.87",
        "49.21"
      ]
    },
    {
      "celdas": [
        "Microhub San Bernabé Centro",
        "109",
        "534",
        "15426.90",
        "141.53",
        "27.25"
      ]
    },
    {
      "celdas": [
        "Microhub Poniente F-113",
        "81",
        "413",
        "12339.50",
        "152.34",
        "21.80"
      ]
    },
    {
      "celdas": [
        "Microhub C81FE",
        "1",
        "6",
        "336.00",
        "336.00",
        "0.59"
      ]
    },
    {
      "celdas": [
        "Microhub E0FDE",
        "1",
        "6",
        "336.00",
        "336.00",
        "0.59"
      ]
    },
    {
      "celdas": [
        "Microhub AB350",
        "1",
        "6",
        "312.00",
        "312.00",
        "0.55"
      ]
    },
    {
      "celdas": [
        "Microhub 1FF3C5",
        "0",
        "0",
        "0.00",
        "",
        "0.00"
      ]
    },
    {
      "celdas": [
        "Microhub 97A5B6",
        "0",
        "0",
        "0.00",
        "",
        "0.00"
      ]
    },
    {
      "celdas": [
        "Microhub D5F75A",
        "0",
        "0",
        "0.00",
        "",
        "0.00"
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
      "356",
      "1795",
      "56602.40",
      "159.00",
      "99.99"
    ]
  },
  "total_filas": 10
}
```

**Evidencia en PostgreSQL.** `SELECT m.nombre, count(*) AS pedidos, round(sum(p.subtotal), 2) AS venta FROM pedido p JOIN microhub m ON m.id = p.microhub_id WHERE p.estado <> 'cancelado' AND p.creado_en > now() - interval '90 days' GROUP BY m.nombre ORDER BY venta DESC`

```json
[
  {
    "nombre": "Microhub Valles",
    "pedidos": 163,
    "venta": "27852.00"
  },
  {
    "nombre": "Microhub San Bernabé Centro",
    "pedidos": 109,
    "venta": "15426.90"
  },
  {
    "nombre": "Microhub Poniente F-113",
    "pedidos": 81,
    "venta": "12339.50"
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
  },
  {
    "nombre": "Microhub AB350",
    "pedidos": 1,
    "venta": "312.00"
  }
]
```

### REP-04 · Reporte en XML · PASA

**Objetivo.** El reporte financiero validado contra reportes.xsd.

**Petición.** `GET http://reportes:5123/api/v1/reportes/equilibrio_microhubs`

```http
Accept: application/xml
X-Traza-Id: 5422abba-0089-4c20-9073-82cfb6309666
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 492 ms · traza `5422abba-0089-4c20-9073-82cfb6309666`

```xml
<?xml version='1.0' encoding='utf-8'?>
<reporte xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><reporte>equilibrio_microhubs</reporte><familia>financiero</familia><titulo>Punto de equilibrio por microhub</titulo><generado_en>2026-11-26T23:21:15-06:00</generado_en><filtros><desde>2026-10-28</desde><hasta>2026-11-26</hasta><zona_id xsi:nil="true" /><microhub_id xsi:nil="true" /></filtros><columnas><columna><clave>microhub</clave><titulo>Microhub</titulo><tipo>texto</tipo></columna><columna><clave>costos_fijos_mes</clave><titulo>Costos fijos del mes</titulo><tipo>dinero</tipo></columna><columna><clave>margen_pedido</clave><titulo>Margen por pedido</titulo><tipo>dinero</tipo></columna><columna><clave>equilibrio_diario</clave><titulo>Equilibrio (pedidos/día)</titulo><tipo>dinero</tipo></columna><columna><clave>pedidos_dia</clave><titulo>Pedidos/día esperados</titulo><tipo>dinero</tipo></columna><columna><clave>diferencia_pedidos_dia</clave><titulo>Diferencia (pedidos/día)</titulo><tipo>dinero</tipo></columna><columna><clave>utilidad_mes</clave><titulo>Utilidad del mes</titulo><tipo>dinero</tipo></columna><columna><clave>decision</clave><titulo>Decisión</titulo><tipo>texto</tipo></columna></columnas><filas><fila><celdas><celda>Microhub San Bernabé Centro</celda><celda>69500.00</celda><celda>5.14</celda><celda>450.50</celda><celda>23.60</celda><celda>-426.91</celda><celda>-65859.95</celda><celda>no_viable</celda></celdas></fila><fila><celdas><celda>Microhub Valles</celda><celda>66500.00</celda><celda>5.14</celda><celda>431.06</celda><celda>16.11</celda><celda>-414.95</celda><celda>-64014.68</celda><celda>no_viable</celda></celdas></fila><fila><celdas><celda>Microhub Poniente F-113</celda><celda>50000.00</celda><celda>5.14</celda><celda>324.10</celda><celda>9.79</celda><celda>-314.31</celda><celda>-48488.91</celda><celda>no_viable</celda></celdas></fila></filas><totales><celdas><celda>Total</celda><celda>186000.00</celda><celda /><celda /><celda /><celda /><celda>-178363.54</celda><celda /></celdas></totales><total_filas>3</total_filas></reporte>
```

### REP-05 · Datos para Highcharts · PASA

**Objetivo.** Categorías y series listas para graficar.

**Petición.** `GET http://reportes:5123/api/v1/reportes/pedidos_por_zona/grafica?desde=2026-08-29`

```http
Accept: application/json
X-Traza-Id: e82160a0-1f6a-484b-90a5-6d7ef41d1721
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 173 ms · traza `e82160a0-1f6a-484b-90a5-6d7ef41d1721`

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
        153.0,
        96.0,
        84.0,
        88.0
      ]
    },
    {
      "nombre": "Demanda no atendida",
      "datos": [
        13.0,
        20.0,
        12.0,
        12.0
      ]
    }
  ]
}
```

### REP-06 · Exportar a CSV · PASA

**Objetivo.** Descarga con SHA-256 y registro en la bitácora de exportaciones.

**Petición.** `GET http://reportes:5123/api/v1/reportes/pedidos_por_zona/exportar?formato=csv&desde=2026-08-29`

```http
Accept: application/json
X-Traza-Id: 0c73cffe-d8d8-42d6-9a60-5b4aa319809e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 189 ms · traza `0c73cffe-d8d8-42d6-9a60-5b4aa319809e`

```json
﻿Zona,Pedidos,Unidades,Venta,Ticket promedio,Demanda no atendida,No atendida (%)
Valles de San Bernabé,153,723,22157.50,144.82,13,7.83
Paseo de San Bernabé,96,524,18819.40,196.04,20,17.24
San Bernabé X (F-113),84,428,12731.50,151.57,12,12.50
San Bernabé Centro,88,438,12240.40,139.10,12,12.00
Total,421,2113,65948.80,156.65,57,11.92

```

**Explicación.** Excel (xlsx) y PDF usan la misma ruta con formato=xlsx|pdf. El archivo se genera al momento y queda archivado en el almacén de objetos.

**Evidencia en PostgreSQL.** `SELECT reporte, formato, filas, bytes, left(sha256, 16) AS sha256, creado_por FROM reporte_exportacion ORDER BY id DESC LIMIT 1`

```json
[
  {
    "reporte": "pedidos_por_zona",
    "formato": "csv",
    "filas": 4,
    "bytes": 345,
    "sha256": "883f7c8c451fb91a",
    "creado_por": 1
  }
]
```

### REP-07 · Bitácora de exportaciones · PASA

**Objetivo.** Quién exportó qué, con qué filtros.

**Petición.** `GET http://reportes:5123/api/v1/reportes/exportaciones?por_pagina=3`

```http
Accept: application/json
X-Traza-Id: 12b7b230-1842-481a-810d-b31a95746280
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 66 ms · traza `12b7b230-1842-481a-810d-b31a95746280`

```json
{
  "datos": [
    {
      "id": 107,
      "reporte": "pedidos_por_zona",
      "formato": "csv",
      "filtros": {
        "desde": "2026-08-29",
        "hasta": "2026-11-26",
        "zona_id": null,
        "microhub_id": null
      },
      "filas": 4,
      "bytes": 345,
      "sha256": "883f7c8c451fb91a040f04d771290318fb3afcbd725774f0d5aeb77b185f3ee6",
      "creado_por": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "creado_en": "2026-11-26T23:21:16-06:00"
    },
    {
      "id": 106,
      "reporte": "pedidos_por_dia",
      "formato": "csv",
      "filtros": {
        "desde": "2026-10-28",
        "hasta": "2026-11-27",
        "zona_id": null,
        "microhub_id": null
      },
      "filas": 2,
      "bytes": 177,
      "sha256": "5523faecc487f14bf0b9e55a04383afa35283150ee9d5b4aaedf99888ca646d6",
      "creado_por": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "creado_en": "2026-11-26T23:20:04-06:00"
    },
    {
      "id": 105,
      "reporte": "pedidos_por_zona",
      "formato": "csv",
      "filtros": {
        "desde": "2026-08-29",
        "hasta": "2026-11-26",
        "zona_id": null,
        "microhub_id": null
      },
      "filas": 4,
      "bytes": 345,
      "sha256": "a747a8eb8811a19cd1bdf3403afb8972030bdec9713241b566db68edd910a8e5",
      "creado_por": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "creado_en": "2026-11-26T23:19:59-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 3,
    "total": 107,
    "paginas": 36
  }
}
```

### REP-08 · Filtro que el reporte no admite · PASA

**Objetivo.** Se rechaza en lugar de ignorarse.

**Petición.** `GET http://reportes:5123/api/v1/reportes/carga_repartidores?zona_id=1`

```http
Accept: application/json
X-Traza-Id: a7f4e5d9-c5ce-453b-b32c-b5d17c1f0f76
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 6 ms · traza `a7f4e5d9-c5ce-453b-b32c-b5d17c1f0f76`

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
    "traza_id": "a7f4e5d9-c5ce-453b-b32c-b5d17c1f0f76"
  }
}
```

### REP-09 · El cliente no ve reportes · PASA

**Objetivo.** Sin reportes.ver.

**Petición.** `GET http://reportes:5123/api/v1/reportes`

```http
Accept: application/json
X-Traza-Id: 0a0982e9-53bb-4400-9edd-e4f314b03644
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 37 ms · traza `0a0982e9-53bb-4400-9edd-e4f314b03644`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "0a0982e9-53bb-4400-9edd-e4f314b03644"
  }
}
```

## Servicio sincronizacion · puerto 5125

### SYN-01 · Enviar lo hecho sin conexión · PASA

**Objetivo.** La app manda el cierre y el recorrido; se aplican en el orden en que ocurrieron.

**Petición.** `POST http://sincronizacion:5125/api/v1/sincronizacion/lotes`

```http
Accept: application/json
X-Traza-Id: 5f050392-7b82-4977-ad84-5c67d83f9aa7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "5b857751-8f85-4281-9544-82403837393b",
  "dispositivo": "android-evidencia-efe107",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "af5f2c71-af9d-4d06-b6e9-78c9bc16501b",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-27T05:18:16.515885+00:00",
      "datos": {
        "entrega_id": 391,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "Cliente ausente",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b09134c5f817588ebd63c39"
        ],
        "capturado_en": "2026-11-27T05:18:16.515813+00:00"
      }
    },
    {
      "operacion_uuid": "168e7285-09c8-457e-a328-f70fbbe83b3b",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-27T05:09:16.515908+00:00",
      "datos": {
        "entrega_id": 391,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-27T05:09:16.515916+00:00"
          }
        ]
      }
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 555 ms · traza `5f050392-7b82-4977-ad84-5c67d83f9aa7`

```json
{
  "id": 217,
  "lote_uuid": "5b857751-8f85-4281-9544-82403837393b",
  "dispositivo": "android-evidencia-efe107",
  "recibido_en": "2026-11-26T23:21:16-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 0,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "af5f2c71-af9d-4d06-b6e9-78c9bc16501b",
      "tipo": "entrega_resultado",
      "estado": "aplicada",
      "duplicada": false,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "168e7285-09c8-457e-a328-f70fbbe83b3b",
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
    "id": 391,
    "resultado": "fallida",
    "id_cliente_local": "af5f2c71-af9d-4d06-b6e9-78c9bc16501b",
    "estado": "entrega_fallida"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT operacion_uuid, tipo, estado, intentos FROM sync_operacion WHERE dispositivo = %s ORDER BY creada_en`

```json
[
  {
    "operacion_uuid": "168e7285-09c8-457e-a328-f70fbbe83b3b",
    "tipo": "ubicaciones",
    "estado": "aplicada",
    "intentos": 1
  },
  {
    "operacion_uuid": "af5f2c71-af9d-4d06-b6e9-78c9bc16501b",
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
X-Traza-Id: 33bacc5c-1a15-448a-8c09-37b16b026663
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "5b857751-8f85-4281-9544-82403837393b",
  "dispositivo": "android-evidencia-efe107",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "af5f2c71-af9d-4d06-b6e9-78c9bc16501b",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-27T05:18:16.515885+00:00",
      "datos": {
        "entrega_id": 391,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "Cliente ausente",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b09134c5f817588ebd63c39"
        ],
        "capturado_en": "2026-11-27T05:18:16.515813+00:00"
      }
    },
    {
      "operacion_uuid": "168e7285-09c8-457e-a328-f70fbbe83b3b",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-27T05:09:16.515908+00:00",
      "datos": {
        "entrega_id": 391,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-27T05:09:16.515916+00:00"
          }
        ]
      }
    }
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 147 ms · traza `33bacc5c-1a15-448a-8c09-37b16b026663`

```json
{
  "id": 217,
  "lote_uuid": "5b857751-8f85-4281-9544-82403837393b",
  "dispositivo": "android-evidencia-efe107",
  "recibido_en": "2026-11-26T23:21:16-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 2,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "af5f2c71-af9d-4d06-b6e9-78c9bc16501b",
      "tipo": "entrega_resultado",
      "estado": "aplicada",
      "duplicada": true,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "168e7285-09c8-457e-a328-f70fbbe83b3b",
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
X-Traza-Id: ee43d215-8674-458e-97e4-9908e59d222a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "7e16814f-0a55-4f3f-9e75-f966c498e132",
  "dispositivo": "android-evidencia-efe107",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "6cc83d87-ee5d-4483-a035-f1ca5e877ae4",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-27T05:20:17.263330+00:00",
      "datos": {
        "entrega_id": 391,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "Cliente ausente",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b09134c5f817588ebd63c39"
        ],
        "capturado_en": "2026-11-27T05:18:16.515813+00:00"
      }
    }
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 230 ms · traza `ee43d215-8674-458e-97e4-9908e59d222a`

```json
{
  "id": 218,
  "lote_uuid": "7e16814f-0a55-4f3f-9e75-f966c498e132",
  "dispositivo": "android-evidencia-efe107",
  "recibido_en": "2026-11-26T23:21:17-06:00",
  "total": 1,
  "aplicadas": 0,
  "duplicadas": 0,
  "conflictos": 1,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "6cc83d87-ee5d-4483-a035-f1ca5e877ae4",
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
X-Traza-Id: bad696a5-e79c-4c8c-9102-4bce5af94103
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 58 ms · traza `bad696a5-e79c-4c8c-9102-4bce5af94103`

```json
{
  "datos": [
    {
      "id": 239,
      "lote_uuid": "7e16814f-0a55-4f3f-9e75-f966c498e132",
      "dispositivo": "android-evidencia-efe107",
      "operacion_uuid": "6cc83d87-ee5d-4483-a035-f1ca5e877ae4",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-26T23:20:17-06:00",
      "estado": "conflicto",
      "http_status": 409,
      "codigo": "CONFLICTO",
      "mensaje": "La entrega ya se cerró con otra operación.",
      "intentos": 1,
      "procesada_en": "2026-11-26T23:21:17-06:00",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      }
    },
    {
      "id": 236,
      "lote_uuid": "6ff0c0d1-e1d8-4238-afb7-7bc4eb5b9fe3",
      "dispositivo": "android-evidencia-9dcc4a",
      "operacion_uuid": "6369ce06-26be-4e13-af22-389abd8ad790",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-26T23:19:00-06:00",
      "estado": "conflicto",
      "http_status": 409,
      "codigo": "CONFLICTO",
      "mensaje": "La entrega ya se cerró con otra operación.",
      "intentos": 1,
      "procesada_en": "2026-11-26T23:20:01-06:00",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      }
    },
    {
      "id": 233,
      "lote_uuid": "ecd04e56-ea26-4490-b36f-4feec7cdb10d",
      "dispositivo": "android-evidencia-d61494",
      "operacion_uuid": "b9ec4f7d-8288-4c4b-9d93-c796d134fbc9",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-26T23:11:48-06:00",
      "estado": "conflicto",
      "http_status": 409,
      "codigo": "CONFLICTO",
      "mensaje": "La entrega ya se cerró con otra operación.",
      "intentos": 1,
      "procesada_en": "2026-11-26T23:12:48-06:00",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      }
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 3,
    "total": 19,
    "paginas": 7
  }
}
```

### SYN-05 · Mis lotes · PASA

**Objetivo.** El repartidor ve solo los suyos.

**Petición.** `GET http://sincronizacion:5125/api/v1/sincronizacion/lotes?por_pagina=3`

```http
Accept: application/json
X-Traza-Id: 8ca0e2fb-a763-4ce1-b1ff-22b802e0d857
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 109 ms · traza `8ca0e2fb-a763-4ce1-b1ff-22b802e0d857`

```json
{
  "datos": [
    {
      "id": 218,
      "lote_uuid": "7e16814f-0a55-4f3f-9e75-f966c498e132",
      "dispositivo": "android-evidencia-efe107",
      "cliente": "android",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "recibido_en": "2026-11-26T23:21:17-06:00",
      "total": 1,
      "aplicadas": 0,
      "duplicadas": 0,
      "conflictos": 1,
      "rechazadas": 0,
      "pendientes": 0
    },
    {
      "id": 217,
      "lote_uuid": "5b857751-8f85-4281-9544-82403837393b",
      "dispositivo": "android-evidencia-efe107",
      "cliente": "android",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "recibido_en": "2026-11-26T23:21:16-06:00",
      "total": 2,
      "aplicadas": 2,
      "duplicadas": 2,
      "conflictos": 0,
      "rechazadas": 0,
      "pendientes": 0
    },
    {
      "id": 216,
      "lote_uuid": "6ff0c0d1-e1d8-4238-afb7-7bc4eb5b9fe3",
      "dispositivo": "android-evidencia-9dcc4a",
      "cliente": "android",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "recibido_en": "2026-11-26T23:20:00-06:00",
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
    "total": 188,
    "paginas": 63
  }
}
```

### SYN-06 · Un lote con sus operaciones · PASA

**Objetivo.** Cada operación con su resultado.

**Petición.** `GET http://sincronizacion:5125/api/v1/sincronizacion/lotes/217`

```http
Accept: application/json
X-Traza-Id: fb4f768a-4d47-4ad8-bbc9-3b1af6922d82
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 56 ms · traza `fb4f768a-4d47-4ad8-bbc9-3b1af6922d82`

```json
{
  "id": 217,
  "lote_uuid": "5b857751-8f85-4281-9544-82403837393b",
  "dispositivo": "android-evidencia-efe107",
  "cliente": "android",
  "usuario": {
    "id": 7,
    "nombre": "Ramiro Alanís Lozano"
  },
  "recibido_en": "2026-11-26T23:21:16-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 2,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "id": 237,
      "lote_uuid": "5b857751-8f85-4281-9544-82403837393b",
      "dispositivo": "android-evidencia-efe107",
      "operacion_uuid": "168e7285-09c8-457e-a328-f70fbbe83b3b",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-26T23:09:16-06:00",
      "estado": "aplicada",
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "intentos": 1,
      "procesada_en": "2026-11-26T23:21:16-06:00",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      }
    },
    {
      "id": 238,
      "lote_uuid": "5b857751-8f85-4281-9544-82403837393b",
      "dispositivo": "android-evidencia-efe107",
      "operacion_uuid": "af5f2c71-af9d-4d06-b6e9-78c9bc16501b",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-26T23:18:16-06:00",
      "estado": "aplicada",
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "intentos": 1,
      "procesada_en": "2026-11-26T23:21:16-06:00",
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
X-Traza-Id: 9468d5bf-05df-4bbb-9161-7d53c149bf8b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 55 ms · traza `9468d5bf-05df-4bbb-9161-7d53c149bf8b`

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

**Petición.** `GET http://sincronizacion:5125/api/v1/sincronizacion/estado?dispositivo=android-evidencia-efe107`

```http
Accept: application/json
X-Traza-Id: f14eb216-6f7a-45cd-b094-bc357f7ceb4d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 51 ms · traza `f14eb216-6f7a-45cd-b094-bc357f7ceb4d`

```json
{
  "dispositivo": "android-evidencia-efe107",
  "ultima_sincronizacion": "2026-11-26T23:21:17-06:00",
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
X-Traza-Id: befe9be1-e586-47d9-ab73-223a25a9a2c3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 31 ms · traza `befe9be1-e586-47d9-ab73-223a25a9a2c3`

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
X-Traza-Id: d990fe90-c5a2-4073-b8a5-6b31d040b58c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "5b857751-8f85-4281-9544-82403837393b",
  "dispositivo": "android-evidencia-efe107",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "af5f2c71-af9d-4d06-b6e9-78c9bc16501b",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-27T05:18:16.515885+00:00",
      "datos": {
        "entrega_id": 391,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "Cliente ausente",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b09134c5f817588ebd63c39"
        ],
        "capturado_en": "2026-11-27T05:18:16.515813+00:00"
      }
    },
    {
      "operacion_uuid": "168e7285-09c8-457e-a328-f70fbbe83b3b",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-27T05:09:16.515908+00:00",
      "datos": {
        "entrega_id": 391,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-27T05:09:16.515916+00:00"
          }
        ]
      }
    }
  ]
}
```

**Respuesta.** HTTP 403 (esperado 403) · 27 ms · traza `d990fe90-c5a2-4073-b8a5-6b31d040b58c`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "d990fe90-c5a2-4073-b8a5-6b31d040b58c"
  }
}
```

### SYN-11 · Lote mal formado · PASA

**Objetivo.** operaciones debe ser una lista.

**Petición.** `POST http://sincronizacion:5125/api/v1/sincronizacion/lotes`

```http
Accept: application/json
X-Traza-Id: 32277404-6c9e-40d4-bb7a-709bdca386db
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "5b857751-8f85-4281-9544-82403837393b",
  "dispositivo": "android-evidencia-efe107",
  "cliente": "android",
  "operaciones": "x"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 31 ms · traza `32277404-6c9e-40d4-bb7a-709bdca386db`

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
    "traza_id": "32277404-6c9e-40d4-bb7a-709bdca386db"
  }
}
```

### SYN-12 · Estado en XML · PASA

**Objetivo.** Validado contra sincronizacion.xsd.

**Petición.** `GET http://sincronizacion:5125/api/v1/sincronizacion/estado?dispositivo=android-evidencia-efe107`

```http
Accept: application/xml
X-Traza-Id: 2e6d4b89-ca7a-41e4-9164-e6404478f842
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 52 ms · traza `2e6d4b89-ca7a-41e4-9164-e6404478f842`

```xml
<?xml version='1.0' encoding='utf-8'?>
<sync_estado xmlns="urn:microhubs:v1" version="1"><dispositivo>android-evidencia-efe107</dispositivo><ultima_sincronizacion>2026-11-26T23:21:17-06:00</ultima_sincronizacion><lotes>2</lotes><aplicadas>2</aplicadas><conflictos>1</conflictos><rechazadas>0</rechazadas><pendientes>0</pendientes></sync_estado>
```

## Servicio productos · puerto 5103

### PRD-A1 · Alta de producto · PASA

**Objetivo.** Alta con permiso; queda en la bitácora y limpia la caché.

**Petición.** `POST http://productos:5103/api/v1/productos`

```http
Accept: application/json
X-Traza-Id: e8bd1c99-03b3-4214-8a21-29bd6fab0332
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "clave_interna": "EV-184C3B",
  "nombre": "Producto de evidencia 184C3B",
  "categoria_id": 1,
  "unidad": "pieza",
  "precio": 19.5
}
```

**Respuesta.** HTTP 201 (esperado 201) · 83 ms · traza `e8bd1c99-03b3-4214-8a21-29bd6fab0332`

```json
{
  "id": 70,
  "clave_interna": "EV-184C3B",
  "nombre": "Producto de evidencia 184C3B",
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
    "fecha": "2026-11-26 23:21:19.240136-06:00"
  }
]
```

### PRD-A2 · Cambio de producto (PATCH) · PASA

**Objetivo.** Solo los campos enviados.

**Petición.** `PATCH http://productos:5103/api/v1/productos/70`

```http
Accept: application/json
X-Traza-Id: 7169d2b8-1c39-4d5d-a5c9-1ec2aa718a83
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "precio": 21.0
}
```

**Respuesta.** HTTP 200 (esperado 200) · 127 ms · traza `7169d2b8-1c39-4d5d-a5c9-1ec2aa718a83`

```json
{
  "id": 70,
  "clave_interna": "EV-184C3B",
  "nombre": "Producto de evidencia 184C3B",
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

**Petición.** `PUT http://productos:5103/api/v1/productos/70`

```http
Accept: application/json
X-Traza-Id: 1c02bedc-4a9f-4428-86c4-5cb6ca6202fe
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "precio": 21.0
}
```

**Respuesta.** HTTP 200 (esperado 200) · 65 ms · traza `1c02bedc-4a9f-4428-86c4-5cb6ca6202fe`

```json
{
  "id": 70,
  "clave_interna": "EV-184C3B",
  "nombre": "Producto de evidencia 184C3B",
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
X-Traza-Id: 750fe366-10dc-4333-9315-fdeee778eb99
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "clave_interna": "EV-184C3B",
  "nombre": "Producto de evidencia 184C3B",
  "categoria_id": 1,
  "unidad": "pieza",
  "precio": 19.5
}
```

**Respuesta.** HTTP 403 (esperado 403) · 36 ms · traza `750fe366-10dc-4333-9315-fdeee778eb99`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "750fe366-10dc-4333-9315-fdeee778eb99"
  }
}
```

### PRD-A5 · Baja de producto · PASA

**Objetivo.** Baja lógica: se conserva su historia.

**Petición.** `DELETE http://productos:5103/api/v1/productos/70`

```http
Accept: application/json
X-Traza-Id: ba000728-bc74-4bb0-852e-1a660d339ce0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 47 ms · traza `ba000728-bc74-4bb0-852e-1a660d339ce0`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT id, estatus FROM producto WHERE id = %s`

```json
[
  {
    "id": 70,
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
X-Traza-Id: bef63881-321e-47f9-b8e4-9833c3925e2a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "clave": "********",
  "nombre": "Zona 184C3B",
  "colonia": "Colonia 184C3B",
  "codigo_postal": "64102",
  "latitud": 25.77,
  "longitud": -100.37
}
```

**Respuesta.** HTTP 201 (esperado 201) · 66 ms · traza `bef63881-321e-47f9-b8e4-9833c3925e2a`

```json
{
  "id": 16,
  "clave": "********",
  "nombre": "Zona 184C3B",
  "colonia": "Colonia 184C3B",
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
    "fecha": "2026-11-26 23:21:19.634362-06:00"
  }
]
```

### ZNA-A2 · Cambio de zona (PATCH) · PASA

**Objetivo.** Solo los campos enviados.

**Petición.** `PATCH http://zonas:5108/api/v1/zonas/16`

```http
Accept: application/json
X-Traza-Id: 813afa62-75f4-42d1-8e8f-3627bfe6e08b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Zona 184C3B renombrada"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 67 ms · traza `813afa62-75f4-42d1-8e8f-3627bfe6e08b`

```json
{
  "id": 16,
  "clave": "********",
  "nombre": "Zona 184C3B renombrada",
  "colonia": "Colonia 184C3B",
  "codigo_postal": "64102",
  "latitud": 25.77,
  "longitud": -100.37
}
```

### ZNA-A3 · Cambio de zona (PUT) · PASA

**Objetivo.** PUT es alias de PATCH.

**Petición.** `PUT http://zonas:5108/api/v1/zonas/16`

```http
Accept: application/json
X-Traza-Id: b8b6afdc-208f-4b58-bfa1-96c7a8e6871a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Zona 184C3B renombrada"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 66 ms · traza `b8b6afdc-208f-4b58-bfa1-96c7a8e6871a`

```json
{
  "id": 16,
  "clave": "********",
  "nombre": "Zona 184C3B renombrada",
  "colonia": "Colonia 184C3B",
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
X-Traza-Id: 422a0aad-9c9b-483e-a12e-e83adaa3967a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "clave": "********",
  "nombre": "Zona 184C3B",
  "colonia": "Colonia 184C3B",
  "codigo_postal": "64102",
  "latitud": 25.77,
  "longitud": -100.37
}
```

**Respuesta.** HTTP 403 (esperado 403) · 32 ms · traza `422a0aad-9c9b-483e-a12e-e83adaa3967a`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "422a0aad-9c9b-483e-a12e-e83adaa3967a"
  }
}
```

### ZNA-A5 · Baja de zona · PASA

**Objetivo.** Baja lógica: se conserva su historia.

**Petición.** `DELETE http://zonas:5108/api/v1/zonas/16`

```http
Accept: application/json
X-Traza-Id: c494f687-8a80-4fdf-8630-b6873d1fe0c7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 46 ms · traza `c494f687-8a80-4fdf-8630-b6873d1fe0c7`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT id, estatus FROM zona WHERE id = %s`

```json
[
  {
    "id": 16,
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
X-Traza-Id: 580210d5-a1b5-4553-9c72-3885d17ca79d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "clave": "********",
  "nombre": "Microhub 184C3B",
  "direccion": "Calle de evidencia 1",
  "latitud": 25.7705,
  "longitud": -100.3705,
  "radio_km": 0.5,
  "capacidad_turno": 10
}
```

**Respuesta.** HTTP 201 (esperado 201) · 93 ms · traza `580210d5-a1b5-4553-9c72-3885d17ca79d`

```json
{
  "id": 15,
  "clave": "********",
  "nombre": "Microhub 184C3B",
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
    "fecha": "2026-11-26 23:21:19.969175-06:00"
  }
]
```

### MIC-A2 · Cambio de microhub (PATCH) · PASA

**Objetivo.** Solo los campos enviados.

**Petición.** `PATCH http://microhubs:5109/api/v1/microhubs/15`

```http
Accept: application/json
X-Traza-Id: bd23caa7-fec2-4274-b1b9-64d14bd66a22
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "radio_km": 0.8
}
```

**Respuesta.** HTTP 200 (esperado 200) · 65 ms · traza `bd23caa7-fec2-4274-b1b9-64d14bd66a22`

```json
{
  "id": 15,
  "clave": "********",
  "nombre": "Microhub 184C3B",
  "latitud": 25.7705,
  "longitud": -100.3705,
  "radio_km": 0.8,
  "estatus": "activo"
}
```

### MIC-A3 · Cambio de microhub (PUT) · PASA

**Objetivo.** PUT es alias de PATCH.

**Petición.** `PUT http://microhubs:5109/api/v1/microhubs/15`

```http
Accept: application/json
X-Traza-Id: 8e3e9130-0b72-4690-a7a6-2c1ac2ca033c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "radio_km": 0.8
}
```

**Respuesta.** HTTP 200 (esperado 200) · 63 ms · traza `8e3e9130-0b72-4690-a7a6-2c1ac2ca033c`

```json
{
  "id": 15,
  "clave": "********",
  "nombre": "Microhub 184C3B",
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
X-Traza-Id: 25108069-2900-4457-9081-1e37025c7b7e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "clave": "********",
  "nombre": "Microhub 184C3B",
  "direccion": "Calle de evidencia 1",
  "latitud": 25.7705,
  "longitud": -100.3705,
  "radio_km": 0.5,
  "capacidad_turno": 10
}
```

**Respuesta.** HTTP 403 (esperado 403) · 27 ms · traza `25108069-2900-4457-9081-1e37025c7b7e`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "25108069-2900-4457-9081-1e37025c7b7e"
  }
}
```

### MIC-A5 · Baja de microhub · PASA

**Objetivo.** Baja lógica: se conserva su historia.

**Petición.** `DELETE http://microhubs:5109/api/v1/microhubs/15`

```http
Accept: application/json
X-Traza-Id: 914494d4-42e6-43cf-8a79-8d7e6ea3334c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 50 ms · traza `914494d4-42e6-43cf-8a79-8d7e6ea3334c`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT id, estatus FROM microhub WHERE id = %s`

```json
[
  {
    "id": 15,
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
X-Traza-Id: 1fbea4b0-05dd-4856-ab75-c581a710c7e1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Cuenta",
  "apellidos": "De evidencia",
  "correo": "ev.184c3b@ejemplo.mx",
  "clave": "********",
  "rol": "repartidor"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 195 ms · traza `1fbea4b0-05dd-4856-ab75-c581a710c7e1`

```json
{
  "id": 67,
  "nombre": "Cuenta",
  "apellidos": "De evidencia",
  "correo": "ev.184c3b@ejemplo.mx",
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
    "id": 67,
    "correo": "ev.184c3b@ejemplo.mx",
    "algoritmo": "$2b$",
    "estatus": "activo"
  }
]
```

### USR-A2 · Cambiar el perfil de una cuenta · PASA

**Objetivo.** Cierra sus sesiones.

**Petición.** `PATCH http://usuarios:5102/api/v1/usuarios/67`

```http
Accept: application/json
X-Traza-Id: fab2fe82-5907-4976-8c7a-8cd9ae1b5921
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "rol": "planeador"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 68 ms · traza `fab2fe82-5907-4976-8c7a-8cd9ae1b5921`

```json
{
  "id": 67,
  "nombre": "Cuenta",
  "apellidos": "De evidencia",
  "correo": "ev.184c3b@ejemplo.mx",
  "telefono": null,
  "rol": "planeador",
  "microhub": null,
  "ultimo_acceso": null
}
```

### USR-A3 · Cambiar una cuenta (PUT) · PASA

**Objetivo.** PUT es alias de PATCH.

**Petición.** `PUT http://usuarios:5102/api/v1/usuarios/67`

```http
Accept: application/json
X-Traza-Id: a6bc577d-e2e7-4e83-9f01-28192eaa5bf7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "telefono": "8112223344"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 63 ms · traza `a6bc577d-e2e7-4e83-9f01-28192eaa5bf7`

```json
{
  "id": 67,
  "nombre": "Cuenta",
  "apellidos": "De evidencia",
  "correo": "ev.184c3b@ejemplo.mx",
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
X-Traza-Id: 1abbdc66-f70e-454d-a21d-c3afbb0226a6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 409 (esperado 409) · 23 ms · traza `1abbdc66-f70e-454d-a21d-c3afbb0226a6`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "No puedes cambiar tu propio perfil ni darte de baja: pídeselo a otro administrador.",
    "traza_id": "1abbdc66-f70e-454d-a21d-c3afbb0226a6"
  }
}
```

### USR-A5 · Dar de baja una cuenta · PASA

**Objetivo.** Baja lógica y cierre de sesiones.

**Petición.** `DELETE http://usuarios:5102/api/v1/usuarios/67`

```http
Accept: application/json
X-Traza-Id: 223b2e00-5de4-49ac-aa61-28afe6b1c469
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 47 ms · traza `223b2e00-5de4-49ac-aa61-28afe6b1c469`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT id, estatus, fecha_baja IS NOT NULL AS con_fecha FROM usuario WHERE id = %s`

```json
[
  {
    "id": 67,
    "estatus": "baja",
    "con_fecha": true
  }
]
```

## Servicio reportes · puerto 5123

### REP-A1 · Enlace firmado de un reporte archivado · PASA

**Objetivo.** El archivo vive en el almacén; la base guarda su ruta y su SHA-256.

**Petición.** `GET http://reportes:5123/api/v1/reportes/exportaciones/108/enlace`

```http
Accept: application/json
X-Traza-Id: 323c0093-f0f6-41d3-9926-bae47912a5d1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 46 ms · traza `323c0093-f0f6-41d3-9926-bae47912a5d1`

```json
{
  "id": 108,
  "nombre": "pedidos_por_dia_108.csv",
  "url_firmada": "http://reportes:5123/api/v1/reportes/descarga?k=reportes%2F2…(176 caracteres)",
  "metodo": "GET",
  "segundos": 300,
  "expira_en": "2026-11-26T23:26:21-06:00"
}
```

**Evidencia en PostgreSQL.** `SELECT id, ruta, almacen, left(sha256, 16) AS sha256, bytes FROM reporte_exportacion WHERE id = %s`

```json
[
  {
    "id": 108,
    "ruta": "reportes/2026/11/108.csv",
    "almacen": "local",
    "sha256": "a600d6797106c4d8",
    "bytes": 177
  }
]
```

### REP-A2 · El enlace de otra persona · PASA

**Objetivo.** Solo quien exportó, el administrador o el auditor.

**Petición.** `GET http://reportes:5123/api/v1/reportes/exportaciones/108/enlace`

```http
Accept: application/json
X-Traza-Id: 4f54356e-a423-46bc-8419-0819ad7c3490
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 27 ms · traza `4f54356e-a423-46bc-8419-0819ad7c3490`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe esa exportación.",
    "traza_id": "4f54356e-a423-46bc-8419-0819ad7c3490"
  }
}
```

### REP-A3 · Descargar con la URL firmada · PASA

**Objetivo.** La firma sustituye al token y caduca.

**Petición.** `GET http://reportes:5123/api/v1/reportes/descarga?k=reportes%2F2026%2F11%2F108.csv&e=1795757181&n=pedidos_por_dia_108.csv&t=text%2Fcsv&s=MyVdeQdhNoybwRsnXze_nL9ZTRiSfE6BOAiSPggXrUg`

```http
Accept: application/json
X-Traza-Id: 69dbaf60-3cf0-47b5-b377-15fce6a60393
```

**Respuesta.** HTTP 200 (esperado 200) · 5 ms · traza `69dbaf60-3cf0-47b5-b377-15fce6a60393`

```json
﻿Día,Pedidos,Unidades,Venta,Ticket promedio,Demanda no atendida
2026-11-25,56,282,8032.40,143.44,0
2026-11-26,201,1046,33143.30,164.89,7
Total,257,1328,41175.70,160.22,7

```

### REP-A4 · Firma alterada · PASA

**Objetivo.** Sin una firma válida no se entrega el archivo.

**Petición.** `GET http://reportes:5123/api/v1/reportes/descarga?k=reportes/otro.csv&e=1&n=otro.csv&t=text/csv&s=alterada`

```http
Accept: application/json
X-Traza-Id: 308e1e8a-963d-4f2f-9140-1ef5cdefa438
```

**Respuesta.** HTTP 403 (esperado 403) · 4 ms · traza `308e1e8a-963d-4f2f-9140-1ef5cdefa438`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "El enlace de descarga no es válido o ya caducó.",
    "traza_id": "308e1e8a-963d-4f2f-9140-1ef5cdefa438"
  }
}
```

## Servicio entregas · puerto 5105

### ENT-B1 · El repartidor no despacha · PASA

**Objetivo.** Sin entregas.asignar.

**Petición.** `POST http://entregas:5105/api/v1/entregas/asignaciones`

```http
Accept: application/json
X-Traza-Id: 8893ed7c-bfe4-44f5-a185-853686e12a75
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "paradas": [
    {
      "pedido_id": 716,
      "repartidor_id": 7,
      "orden_parada": 1
    },
    {
      "pedido_id": 717,
      "repartidor_id": 7,
      "orden_parada": 2
    }
  ]
}
```

**Respuesta.** HTTP 403 (esperado 403) · 28 ms · traza `8893ed7c-bfe4-44f5-a185-853686e12a75`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "8893ed7c-bfe4-44f5-a185-853686e12a75"
  }
}
```

### ENT-B2 · Una parada que no existe anula el despacho · PASA

**Objetivo.** Todas o ninguna.

**Petición.** `POST http://entregas:5105/api/v1/entregas/asignaciones`

```http
Accept: application/json
X-Traza-Id: b1c087cb-7a58-4c9b-aa82-94444eca4bf7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "paradas": [
    {
      "pedido_id": 716,
      "repartidor_id": 7,
      "orden_parada": 1
    },
    {
      "pedido_id": 717,
      "repartidor_id": 7,
      "orden_parada": 2
    },
    {
      "pedido_id": 999999999,
      "repartidor_id": 7,
      "orden_parada": 3
    }
  ]
}
```

**Respuesta.** HTTP 404 (esperado 404) · 87 ms · traza `b1c087cb-7a58-4c9b-aa82-94444eca4bf7`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el pedido 999999999.",
    "traza_id": "b1c087cb-7a58-4c9b-aa82-94444eca4bf7"
  }
}
```

**Evidencia en PostgreSQL.** `SELECT id, estado::text AS estado FROM pedido WHERE id = ANY(%s) ORDER BY id`

```json
[
  {
    "id": 716,
    "estado": "en_preparacion"
  },
  {
    "id": 717,
    "estado": "en_preparacion"
  }
]
```

### ENT-B3 · Despachar las paradas de una ruta · PASA

**Objetivo.** Crea las entregas, pone los pedidos en ruta y avisa al repartidor.

**Petición.** `POST http://entregas:5105/api/v1/entregas/asignaciones`

```http
Accept: application/json
X-Traza-Id: d0b63460-db88-49e7-b110-0de3feff814d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "paradas": [
    {
      "pedido_id": 716,
      "repartidor_id": 7,
      "orden_parada": 1
    },
    {
      "pedido_id": 717,
      "repartidor_id": 7,
      "orden_parada": 2
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 87 ms · traza `d0b63460-db88-49e7-b110-0de3feff814d`

```json
{
  "asignadas": 2,
  "entregas": [
    {
      "entrega_id": 394,
      "pedido_id": 716,
      "repartidor_id": 7,
      "orden_parada": 1
    },
    {
      "entrega_id": 395,
      "pedido_id": 717,
      "repartidor_id": 7,
      "orden_parada": 2
    }
  ]
}
```

**Evidencia en PostgreSQL.** `SELECT pedido_id, repartidor_id, orden_parada, salida_en FROM entrega WHERE pedido_id = ANY(%s) ORDER BY orden_parada`

```json
[
  {
    "pedido_id": 716,
    "repartidor_id": 7,
    "orden_parada": 1,
    "salida_en": "2026-11-26 23:21:21.545561-06:00"
  },
  {
    "pedido_id": 717,
    "repartidor_id": 7,
    "orden_parada": 2,
    "salida_en": "2026-11-26 23:21:21.545561-06:00"
  }
]
```

### ENT-B4 · Cerrar una parada despachada · PASA

**Objetivo.** El cliente no estaba: se registra la incidencia (RN29).

**Petición.** `POST http://entregas:5105/api/v1/entregas/394/resultado`

```http
Accept: application/json
X-Traza-Id: 7c49e46a-0771-4f31-9e94-0a6f33e40969
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "fallida",
  "incidencia": "Cliente ausente (corrida de evidencias)",
  "monto_cobrado": 0,
  "cambio_entregado": 0,
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611
  },
  "evidencia_ids": [
    "6b0913515f817588ebd63c3c"
  ],
  "capturado_en": "2026-11-27T05:21:21.687843+00:00",
  "id_cliente_local": "690796c5-04f8-4eea-b380-f15724a8ba0a"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 111 ms · traza `7c49e46a-0771-4f31-9e94-0a6f33e40969`

```json
{
  "entrega_id": 394,
  "pedido_id": 716,
  "estado_pedido": "entrega_fallida",
  "cerrado_en": "2026-11-26T23:21:21-06:00",
  "duplicado": false
}
```

### ENT-B5 · Cerrar una parada despachada · PASA

**Objetivo.** El cliente no estaba: se registra la incidencia (RN29).

**Petición.** `POST http://entregas:5105/api/v1/entregas/395/resultado`

```http
Accept: application/json
X-Traza-Id: 77f1fd1e-7f6a-4dba-bf21-1ef7591240de
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "fallida",
  "incidencia": "Cliente ausente (corrida de evidencias)",
  "monto_cobrado": 0,
  "cambio_entregado": 0,
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611
  },
  "evidencia_ids": [
    "6b0913515f817588ebd63c3f"
  ],
  "capturado_en": "2026-11-27T05:21:21.857448+00:00",
  "id_cliente_local": "0484d7de-7035-494b-aa90-59d1598399a9"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 125 ms · traza `77f1fd1e-7f6a-4dba-bf21-1ef7591240de`

```json
{
  "entrega_id": 395,
  "pedido_id": 717,
  "estado_pedido": "entrega_fallida",
  "cerrado_en": "2026-11-26T23:21:21-06:00",
  "duplicado": false
}
```

## Servicio pedidos · puerto 5104

### PED-A1 · Crear un pedido · PASA

**Objetivo.** Precio del servidor, ticket mínimo y asignación del motor.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: 767f1e82-ee30-445e-bdee-8d2117b0b2c1
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
  "operacion_uuid": "0ff9edc4-a765-41eb-a168-10787aa54331"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 248 ms · traza `767f1e82-ee30-445e-bdee-8d2117b0b2c1`

```json
{
  "id": 718,
  "folio": "PED-20261126-000718",
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
    "pedido_id": 718,
    "producto_id": 32,
    "cantidad": 3,
    "precio_unitario": "72.00"
  },
  {
    "pedido_id": 718,
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
X-Traza-Id: de4fe6d7-26da-4117-b4ef-8405c5836d90
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
  "operacion_uuid": "0ff9edc4-a765-41eb-a168-10787aa54331"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 47 ms · traza `de4fe6d7-26da-4117-b4ef-8405c5836d90`

```json
{
  "id": 718,
  "folio": "PED-20261126-000718",
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
X-Traza-Id: d5d7b306-9ff7-4571-806d-766a564f971c
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

**Respuesta.** HTTP 422 (esperado 422) · 109 ms · traza `d5d7b306-9ff7-4571-806d-766a564f971c`

```json
{
  "error": {
    "codigo": "REGLA_NEGOCIO",
    "mensaje": "El subtotal (7.50) no alcanza el pedido mínimo de la zona (90.00).",
    "traza_id": "d5d7b306-9ff7-4571-806d-766a564f971c"
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
    "fecha": "2026-11-26 23:21:22.435703-06:00"
  }
]
```

### PED-A4 · Marcar listo · PASA

**Objetivo.** El operador libera el pedido para despacho.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/718/listo`

```http
Accept: application/json
X-Traza-Id: c94a938d-612d-4d48-a1ff-cbe1e291ef30
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 72 ms · traza `c94a938d-612d-4d48-a1ff-cbe1e291ef30`

```json
{
  "id": 718,
  "estado": "en_preparacion",
  "listo_en": "2026-11-26T23:21:22-06:00"
}
```

## Servicio entregas · puerto 5105

### ENT-A1 · Asignar la entrega · PASA

**Objetivo.** Queda en ruta y el repartidor recibe el aviso.

**Petición.** `POST http://entregas:5105/api/v1/entregas`

```http
Accept: application/json
X-Traza-Id: ffaf0e4a-fc62-45e6-8ea5-43a2c635e472
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 718,
  "repartidor_id": 7
}
```

**Respuesta.** HTTP 201 (esperado 201) · 60 ms · traza `ffaf0e4a-fc62-45e6-8ea5-43a2c635e472`

```json
{
  "entrega_id": 396,
  "pedido_id": 718,
  "repartidor_id": 7,
  "estado_pedido": "en_ruta"
}
```

**Evidencia en PostgreSQL.** `SELECT id, repartidor_id, turno_fecha, salida_en FROM entrega WHERE pedido_id = %s`

```json
[
  {
    "id": 396,
    "repartidor_id": 7,
    "turno_fecha": "2026-11-26",
    "salida_en": "2026-11-26 23:21:22.988723-06:00"
  }
]
```

### ENT-A2 · Asignar dos veces · PASA

**Objetivo.** El pedido ya tiene entrega.

**Petición.** `POST http://entregas:5105/api/v1/entregas`

```http
Accept: application/json
X-Traza-Id: a795486a-b65e-478b-b69a-6148d4cd5a2c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 718,
  "repartidor_id": 7
}
```

**Respuesta.** HTTP 409 (esperado 409) · 28 ms · traza `a795486a-b65e-478b-b69a-6148d4cd5a2c`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Ese pedido ya tiene una entrega asignada.",
    "traza_id": "a795486a-b65e-478b-b69a-6148d4cd5a2c"
  }
}
```

### ENT-A3 · El repartidor no asigna · PASA

**Objetivo.** Sin entregas.asignar.

**Petición.** `POST http://entregas:5105/api/v1/entregas`

```http
Accept: application/json
X-Traza-Id: e785e034-3343-4542-a88f-312fc5dfa49e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 718,
  "repartidor_id": 7
}
```

**Respuesta.** HTTP 403 (esperado 403) · 31 ms · traza `e785e034-3343-4542-a88f-312fc5dfa49e`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "e785e034-3343-4542-a88f-312fc5dfa49e"
  }
}
```

## Servicio auth · puerto 5101

### SAL-AUT · Salud de auth · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://auth:5101/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 1cdbaed3-04bc-438d-8487-87c0d7eaf98a
```

**Respuesta.** HTTP 200 (esperado 200) · 15 ms · traza `1cdbaed3-04bc-438d-8487-87c0d7eaf98a`

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
  "tiempo_ms": 12.4
}
```

## Servicio usuarios · puerto 5102

### SAL-USU · Salud de usuarios · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://usuarios:5102/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 27f3876a-f822-46a7-8add-c202695f1c84
```

**Respuesta.** HTTP 200 (esperado 200) · 19 ms · traza `27f3876a-f822-46a7-8add-c202695f1c84`

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
  "tiempo_ms": 16.5
}
```

## Servicio productos · puerto 5103

### SAL-PRO · Salud de productos · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://productos:5103/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 75b88bbb-9a34-4e38-a9e4-066cea2081c5
```

**Respuesta.** HTTP 200 (esperado 200) · 15 ms · traza `75b88bbb-9a34-4e38-a9e4-066cea2081c5`

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
  "tiempo_ms": 12.8
}
```

## Servicio pedidos · puerto 5104

### SAL-PED · Salud de pedidos · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://pedidos:5104/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 44b14a87-fb64-4995-a2d5-635efb1a85ca
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `44b14a87-fb64-4995-a2d5-635efb1a85ca`

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
  "tiempo_ms": 14.8
}
```

## Servicio entregas · puerto 5105

### SAL-ENT · Salud de entregas · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://entregas:5105/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 0ad2161c-8527-4641-b731-57fc118cf814
```

**Respuesta.** HTTP 200 (esperado 200) · 25 ms · traza `0ad2161c-8527-4641-b731-57fc118cf814`

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
  "tiempo_ms": 13.5
}
```

## Servicio planeacion · puerto 5106

### SAL-PLA · Salud de planeacion · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://planeacion:5106/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 96f21e62-448f-497b-b6ec-daf748d272db
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `96f21e62-448f-497b-b6ec-daf748d272db`

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
  "tiempo_ms": 13.9
}
```

## Servicio documentos · puerto 5107

### SAL-DOC · Salud de documentos · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://documentos:5107/api/v1/health`

```http
Accept: application/json
X-Traza-Id: badf49bb-feac-4348-ae2d-0f0be6549cdd
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `badf49bb-feac-4348-ae2d-0f0be6549cdd`

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
  "tiempo_ms": 14.7
}
```

## Servicio zonas · puerto 5108

### SAL-ZON · Salud de zonas · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://zonas:5108/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 6af8e91e-e09b-4d88-b66b-09c95dcb3a35
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `6af8e91e-e09b-4d88-b66b-09c95dcb3a35`

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
  "tiempo_ms": 14.2
}
```

## Servicio microhubs · puerto 5109

### SAL-MIC · Salud de microhubs · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://microhubs:5109/api/v1/health`

```http
Accept: application/json
X-Traza-Id: f7f16ee8-c4fc-48ec-8246-f7579343506a
```

**Respuesta.** HTTP 200 (esperado 200) · 15 ms · traza `f7f16ee8-c4fc-48ec-8246-f7579343506a`

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
  "tiempo_ms": 13.1
}
```

## Servicio seguimiento · puerto 5110

### SAL-SEG · Salud de seguimiento · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://seguimiento:5110/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 336b0dff-50cf-4ae2-8d97-47a50d52de43
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `336b0dff-50cf-4ae2-8d97-47a50d52de43`

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
  "tiempo_ms": 13.7
}
```

## Servicio inventario · puerto 5111

### SAL-INV · Salud de inventario · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://inventario:5111/api/v1/health`

```http
Accept: application/json
X-Traza-Id: e0230c7b-e4a7-4d1e-b27f-a2f3ea10415b
```

**Respuesta.** HTTP 200 (esperado 200) · 22 ms · traza `e0230c7b-e4a7-4d1e-b27f-a2f3ea10415b`

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
  "tiempo_ms": 12.5
}
```

## Servicio precios · puerto 5112

### SAL-PRE · Salud de precios · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://precios:5112/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 5be9c895-f4c6-4f05-80df-2e8bf9931474
```

**Respuesta.** HTTP 200 (esperado 200) · 15 ms · traza `5be9c895-f4c6-4f05-80df-2e8bf9931474`

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
  "tiempo_ms": 12.5
}
```

## Servicio proveedores · puerto 5113

### SAL-PRO · Salud de proveedores · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://proveedores:5113/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 61df6c1f-fbc1-4031-80f8-8cc087a4cfba
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `61df6c1f-fbc1-4031-80f8-8cc087a4cfba`

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
  "tiempo_ms": 13.6
}
```

## Servicio abastecimiento · puerto 5114

### SAL-ABA · Salud de abastecimiento · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://abastecimiento:5114/api/v1/health`

```http
Accept: application/json
X-Traza-Id: dca40d4c-187e-4435-a6b7-bf46d00e2baa
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `dca40d4c-187e-4435-a6b7-bf46d00e2baa`

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
  "tiempo_ms": 13.9
}
```

## Servicio demanda · puerto 5115

### SAL-DEM · Salud de demanda · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://demanda:5115/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 0a1f3f04-ea1c-468f-aaa1-ac1a54aa26d1
```

**Respuesta.** HTTP 200 (esperado 200) · 20 ms · traza `0a1f3f04-ea1c-468f-aaa1-ac1a54aa26d1`

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
  "tiempo_ms": 17.0
}
```

## Servicio cobertura · puerto 5116

### SAL-COB · Salud de cobertura · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://cobertura:5116/api/v1/health`

```http
Accept: application/json
X-Traza-Id: b2f1a6c2-ad3b-436d-a77d-e0d49989562d
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `b2f1a6c2-ad3b-436d-a77d-e0d49989562d`

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
X-Traza-Id: 2e849d64-a48b-45be-b242-e6d8c56c5ff7
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `2e849d64-a48b-45be-b242-e6d8c56c5ff7`

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
  "tiempo_ms": 14.7
}
```

## Servicio rutas · puerto 5118

### SAL-RUT · Salud de rutas · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://rutas:5118/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 22848a14-6160-48dc-a3b7-0cde919643b5
```

**Respuesta.** HTTP 200 (esperado 200) · 19 ms · traza `22848a14-6160-48dc-a3b7-0cde919643b5`

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
  "tiempo_ms": 16.0
}
```

## Servicio costos · puerto 5119

### SAL-COS · Salud de costos · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://costos:5119/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 84241e1f-60ea-4394-9c67-38f1fe06a10e
```

**Respuesta.** HTTP 200 (esperado 200) · 18 ms · traza `84241e1f-60ea-4394-9c67-38f1fe06a10e`

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
  "tiempo_ms": 14.8
}
```

## Servicio punto-equilibrio · puerto 5120

### SAL-PUN · Salud de punto-equilibrio · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://punto-equilibrio:5120/api/v1/health`

```http
Accept: application/json
X-Traza-Id: af91b63b-d574-4472-a348-5dd77ed82ce4
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `af91b63b-d574-4472-a348-5dd77ed82ce4`

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
  "tiempo_ms": 14.3
}
```

## Servicio simulacion · puerto 5121

### SAL-SIM · Salud de simulacion · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://simulacion:5121/api/v1/health`

```http
Accept: application/json
X-Traza-Id: f9c6f094-7ce0-4692-ba99-8100368db073
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `f9c6f094-7ce0-4692-ba99-8100368db073`

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
  "tiempo_ms": 14.3
}
```

## Servicio surtido · puerto 5122

### SAL-SUR · Salud de surtido · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://surtido:5122/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 67174904-8ba2-4601-a669-df0eeed3a631
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `67174904-8ba2-4601-a669-df0eeed3a631`

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
  "tiempo_ms": 13.6
}
```

## Servicio notificaciones · puerto 5124

### SAL-NOT · Salud de notificaciones · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://notificaciones:5124/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 5c8f0eb9-61c1-4cdd-b550-55eeb9b271e7
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `5c8f0eb9-61c1-4cdd-b550-55eeb9b271e7`

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
  "tiempo_ms": 13.6
}
```

## Servicio reportes · puerto 5123

### SAL-REP · Salud de reportes · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://reportes:5123/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 70048cbc-52b0-4fb1-8921-ffef1c99996d
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `70048cbc-52b0-4fb1-8921-ffef1c99996d`

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
  "tiempo_ms": 14.2
}
```

## Servicio sincronizacion · puerto 5125

### SAL-SIN · Salud de sincronizacion · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://sincronizacion:5125/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 639b67a1-58c0-4c0c-8a68-da33b0ce6b41
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `639b67a1-58c0-4c0c-8a68-da33b0ce6b41`

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
  "tiempo_ms": 13.3
}
```

## Servicio auditoria-monitoreo · puerto 5126

### SAL-AUD · Salud de auditoria-monitoreo · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/health`

```http
Accept: application/json
X-Traza-Id: c26c8ed9-1d9d-481f-87bb-8ca72b309542
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `c26c8ed9-1d9d-481f-87bb-8ca72b309542`

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
  "tiempo_ms": 14.6
}
```

## Servicio auth · puerto 5101

### MON-01 · Registro de actividad · PASA

**Objetivo.** Cada petición queda en MongoDB con su traza.

**Petición.** `GET http://auth:5101/api/v1/auth/validar`

```http
Accept: application/json
X-Traza-Id: 46f69440-8ce9-49c3-89f8-da4dce73a6d1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 6 ms · traza `46f69440-8ce9-49c3-89f8-da4dce73a6d1`

```json
{
  "valido": true,
  "expira_en": 841,
  "usuario": {
    "id": 1,
    "rol": "administrador",
    "microhub_id": null
  }
}
```

**Explicación.** El X-Traza-Id de la petición se recupera en logs_tecnicos.correlacion_id.

**Evidencia en MongoDB.** `db.logs_tecnicos.findOne({correlacion_id: '46f69440-8ce9-49c3-89f8-da4dce73a6d1'})`

```json
{
  "nivel": "INFO",
  "componente": "auth",
  "registrado_en": "2026-11-27 05:21:23.746000+00:00",
  "correlacion_id": "46f69440-8ce9-49c3-89f8-da4dce73a6d1",
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
    "peticiones": 932,
    "ms_promedio": 107.53648068669528
  },
  {
    "_id": "auditoria-monitoreo",
    "peticiones": 2679,
    "ms_promedio": 59.20007465472191
  },
  {
    "_id": "auth",
    "peticiones": 2976,
    "ms_promedio": 273.95766129032256
  },
  {
    "_id": "capacidad",
    "peticiones": 1062,
    "ms_promedio": 63.931261770244824
  },
  {
    "_id": "cobertura",
    "peticiones": 1759,
    "ms_promedio": 52.37748720864127
  },
  {
    "_id": "costos",
    "peticiones": 2119,
    "ms_promedio": 44.94572911750826
  },
  {
    "_id": "demanda",
    "peticiones": 1938,
    "ms_promedio": 101.90918472652218
  },
  {
    "_id": "documentos",
    "peticiones": 591,
    "ms_promedio": 31.839255499153975
  },
  {
    "_id": "entregas",
    "peticiones": 1234,
    "ms_promedio": 75.77390599675851
  },
  {
    "_id": "inventario",
    "peticiones": 2282,
    "ms_promedio": 59.537248028045575
  },
  {
    "_id": "microhubs",
    "peticiones": 450,
    "ms_promedio": 24.413333333333334
  },
  {
    "_id": "notificaciones",
    "peticiones": 510,
    "ms_promedio": 32.19607843137255
  },
  {
    "_id": "pedidos",
    "peticiones": 3082,
    "ms_promedio": 86.53277092796885
  },
  {
    "_id": "planeacion",
    "peticiones": 948,
    "ms_promedio": 51.12658227848101
  },
  {
    "_id": "precios",
    "peticiones": 999,
    "ms_promedio": 49.23723723723724
  },
  {
    "_id": "productos",
    "peticiones": 483,
    "ms_promedio": 29.041407867494826
  },
  {
    "_id": "proveedores",
    "peticiones": 765,
    "ms_promedio": 51.26143790849673
  },
  {
    "_id": "punto-equilibrio",
    "peticiones": 1291,
    "ms_promedio": 179.20604182804027
  },
  {
    "_id": "reportes",
    "peticiones": 1355,
    "ms_promedio": 187.15867158671585
  },
  {
    "_id": "rutas",
    "peticiones": 1083,
    "ms_promedio": 103.79224376731302
  },
  {
    "_id": "seguimiento",
    "peticiones": 225,
    "ms_promedio": 30.897777777777776
  },
  {
    "_id": "simulacion",
    "peticiones": 1642,
    "ms_promedio": 150.3721071863581
  },
  {
    "_id": "sincronizacion",
    "peticiones": 809,
    "ms_promedio": 99.59332509270705
  },
  {
    "_id": "surtido",
    "peticiones": 833,
    "ms_promedio": 184.17166866746697
  },
  {
    "_id": "usuarios",
    "peticiones": 303,
    "ms_promedio": 43.722772277227726
  },
  {
    "_id": "zonas",
    "peticiones": 3778,
    "ms_promedio": 3.1431974589730016
  }
]
```

## Servicio zonas · puerto 5108

### RAT-01 · Límite de consumo excedido · PASA

**Objetivo.** Más de 240 solicitudes por minuto desde la misma IP.

**Petición.** `GET http://zonas:5108/api/v1/zonas`

```http
Accept: application/json
X-Traza-Id: 183e9918-a5d9-480f-bb00-bba3f16eff48
```

**Respuesta.** HTTP 429 (esperado 429) · 5 ms · traza `183e9918-a5d9-480f-bb00-bba3f16eff48`

```json
{
  "error": {
    "codigo": "LIMITE_EXCEDIDO",
    "mensaje": "Máximo 240 solicitudes por minuto. Espera 34 segundos.",
    "traza_id": "183e9918-a5d9-480f-bb00-bba3f16eff48"
  }
}
```

**Explicación.** Contador rate:zonas:{ip}:{minuto} en Redis (db 1) con TTL de 120 s; responde Retry-After.

**Evidencia en Redis.** `db1 GET rate:zonas:2b30bb50d78e82c5:29929281; db1 TTL rate:zonas:2b30bb50d78e82c5:29929281`

```json
[
  {
    "comando": "db1 GET rate:zonas:2b30bb50d78e82c5:29929281",
    "valor": "242"
  },
  {
    "comando": "db1 TTL rate:zonas:2b30bb50d78e82c5:29929281",
    "valor": 115
  }
]
```
