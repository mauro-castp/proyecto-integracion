# Evidencias de petición y respuesta · microservicios v1

Generado el 2026-10-20 06:43 contra los servicios en ejecución. 359 de 359 casos pasan.

## Servicio auth · puerto 5101

### AUTH-01 · Iniciar sesión (JSON) · PASA

**Objetivo.** Emitir el JWT de acceso y el token de renovación del repartidor.

**Petición.** `POST http://auth:5101/api/v1/auth/login`

```http
Accept: application/json
X-Traza-Id: 588df9f7-2f01-41eb-bf16-495eb7c30272
Content-Type: application/json
```

```json
{
  "correo": "repartidor1@codex.mx",
  "clave": "********",
  "dispositivo": "Pixel 7"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 459 ms · traza `588df9f7-2f01-41eb-bf16-495eb7c30272`

```json
{
  "token_acceso": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwicm9sIjo…(291 caracteres)",
  "token_renovacion": "rt_eaad4ede624c92956569234b9318d76c",
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

**Evidencia en Redis.** `SMEMBERS auth:sesion:7; TTL auth:sesion:7; TTL auth:refresh:103db7bc48b61e9a072eb560bfd3f533d9317634ce2040836ce8f7bb574d5262`

```json
[
  {
    "comando": "SMEMBERS auth:sesion:7",
    "valor": [
      "0292470596944da99591d2ab14718b4d",
      "05a1ac568d4541798f152a24a2f111c0",
      "07d4c495e3d2474198428e4c397f0bae",
      "09ed9a314b75498d93d72260006e5872",
      "0a825f68b57a4dcc952d8360dcd6067e",
      "0de01dd472e54b71b65639d964f00236",
      "10a4fe58f6b244629bca06c81219a31e",
      "1253e89abc6741babb3aff37396e5c06",
      "1837e2789863487981325614fe715114",
      "1b6f2648595d4716b6fbc231446856ff",
      "23c0d59df8854a4eac58538525475b97",
      "23f9b5ddba10469a8299132f51e8a28b",
      "246bdff718c54656b5201ca705a72e84",
      "28b7526e82f84496b78b03c94e99c55f",
      "2d687e4136ec414e8bfafd3f6f714d5c",
      "30e19c509dbd45c69b1142f42908abc6",
      "3649894dedc94329a5ae77a711388f3f",
      "3a108ce7d7a2439e8e6208bffb909bd2",
      "3c5be45600734a58afca7d6b29b1d0f6",
      "43375be0c8834916a29e15348d5c0789",
      "438020b6443a405baadb5921491cf552",
      "51f87bcc17b74bb890833fbc2a57221d",
      "594bbce0724d41a5aa85580e9ca01dde",
      "5ca3105dad124883a7f3a231d8eec8d3",
      "60a6a7fadea84e9ca39fad6cf93f171a",
      "6af66583172544298792994c974adb79",
      "6f774853bbc44c898d204a1149100e43",
      "7075cc5f496c4ff18d0a544586befdde",
      "709f6d040a8948df86d1e2b0e40e2e16",
      "73de5c46546d4cab993488b38fc0a9f5",
      "75dc4227de7f4700ae6481883aaccf49",
      "79b469ff678c4549bf0c782062c2d676",
      "7c0e798c61cd4457a96a8443a72d1e98",
      "83437471b840471e8f70e9a06915f1b6",
      "8597f5d8e13e4091b97f9528aadf6f1e",
      "8d090168ea1c4065936967e22ef3dc52",
      "9158d29a8c074781aa7231a691485e4c",
      "97e8c2b2c7d040d2969c5ce298c2668f",
      "9dc214617496435095fd5d6ca2e1887e",
      "9fd79d11a60c40a28d3590eb7854e8dd",
      "a0d3a36ed64f4bf8a2a9a221a557556b",
      "b6e3c19051c44b32b8f56a55ff9c4023",
      "c4acbdb542364c208879964a30c9804d",
      "cd658a09e2a74d9ab4428da12538f36c",
      "d03a6a49e7af49d39bb8ba5bc012bbc6",
      "d46f9d7fe82c4db49932da5608c2e891",
      "d46fc381fe5d4e279fc5e8bbf7b23a16",
      "dbc4a703be814c37b26a758acca37314",
      "dd4e4b80ca2d467f86dd25abfd50547d",
      "ec69aaf779fa41429b3792d6b936b692",
      "f24b6a04ad454216b52f2d6097b11652",
      "f334aec904cd435aae5cf0100d77ee53",
      "f335bd7bb3674379920b8acd4f6d4f39",
      "f4228dee34284246a67a0b08f794bebb",
      "f720590fd68048a78fcb5e71028f5708",
      "fa1ccda5c36744f3b36b951be2304288",
      "faf5cf850e154d1b93152c186b94dc1f",
      "fb2f8ffc4aef4898b02aaf7588015ad2",
      "fccfd23174404bca9288e00a9ceeb2d5",
      "ffb1b0a7f5d34316a0538e4d622f72ab"
    ]
  },
  {
    "comando": "TTL auth:sesion:7",
    "valor": 900
  },
  {
    "comando": "TTL auth:refresh:103db7bc48b61e9a072eb560bfd3f533d9317634ce2040836ce8f7bb574d5262",
    "valor": 604800
  }
]
```

**Evidencia en PostgreSQL.** `SELECT fecha, modulo, accion, detalle FROM auditoria WHERE correo_intento IS NULL AND usuario_id = 7 AND modulo = 'auth' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "fecha": "2026-10-20 06:43:03.642274+00:00",
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
X-Traza-Id: 27f3eeba-5330-470c-905e-f7f971a93b9c
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><login xmlns="urn:microhubs:v1"><correo>planeador@codex.mx</correo><clave>********</clave></login>
```

**Respuesta.** HTTP 200 (esperado 200) · 356 ms · traza `27f3eeba-5330-470c-905e-f7f971a93b9c`

```xml
<?xml version='1.0' encoding='utf-8'?>
<sesion xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><token_acceso>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwicm9sIjo…(291 caracteres)</token_acceso><token_renovacion>rt_95b102955c7fcbfc47c7c61b627ba655</token_renovacion><tipo>Bearer</tipo><expira_en>900</expira_en><usuario><id>5</id><nombre>Vanessa</nombre><apellidos>Morante López</apellidos><correo>planeador@codex.mx</correo><rol>planeador</rol><microhub_id xsi:nil="true" /><permisos><permiso>abastecimiento.ver</permiso><permiso>archivos.crear</permiso><permiso>archivos.ver</permiso><permiso>capacidad.editar</permiso><permiso>capacidad.ver</permiso><permiso>catalogo_publico.ver</permiso><permiso>cobertura.ver</permiso><permiso>configuracion.ver</permiso><permiso>costos.editar</permiso><permiso>costos.ver</permiso><permiso>demanda.editar</permiso><permiso>demanda.ver</permiso><permiso>equilibrio.editar</permiso><permiso>equilibrio.ver</permiso><permiso>indicadores.ver</permiso><permiso>inventario.ver</permiso><permiso>microhubs.ver</permiso><permiso>notificaciones.ver</permiso><permiso>pedidos.reasignar</permiso><permiso>pedidos.ver</permiso><permiso>planeacion.editar</permiso><permiso>planeacion.ver</permiso><permiso>precios.ver</permiso><permiso>productos.ver</permiso><permiso>proveedores.ver</permiso><permiso>reportes.exportar</permiso><permiso>reportes.ver</permiso><permiso>rutas.planear</permiso><permiso>rutas.ver</permiso><permiso>simulacion.ejecutar</permiso><permiso>simulacion.ver</permiso><permiso>surtido.editar</permiso><permiso>surtido.ver</permiso><permiso>zonas.ver</permiso></permisos></usuario></sesion>
```

**Explicación.** El cuerpo XML se valida contra los XSD antes de procesarse; la respuesta <sesion> también cumple el XSD.

### AUTH-03 · Clave incorrecta · PASA

**Objetivo.** Rechazar credenciales y contar el intento.

**Petición.** `POST http://auth:5101/api/v1/auth/login`

```http
Accept: application/json
X-Traza-Id: 01380469-e61b-4b0b-beee-1dd12d7dd47d
Content-Type: application/json
```

```json
{
  "correo": "auditor@codex.mx",
  "clave": "********"
}
```

**Respuesta.** HTTP 401 (esperado 401) · 216 ms · traza `01380469-e61b-4b0b-beee-1dd12d7dd47d`

```json
{
  "error": {
    "codigo": "CREDENCIALES_INVALIDAS",
    "mensaje": "Correo o clave incorrectos. Intento 1 de 5.",
    "traza_id": "01380469-e61b-4b0b-beee-1dd12d7dd47d"
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
X-Traza-Id: 96394438-995e-4683-9921-a51843c28f99
Content-Type: application/json
```

```json
{
  "correo": "sin-arroba",
  "clave": "********"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 6 ms · traza `96394438-995e-4683-9921-a51843c28f99`

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
    "traza_id": "96394438-995e-4683-9921-a51843c28f99"
  }
}
```

### AUTH-05 · XML con DTD (ataque XXE) · PASA

**Objetivo.** Rechazar entidades externas y DTD.

**Petición.** `POST http://auth:5101/api/v1/auth/login`

```http
Accept: application/xml
X-Traza-Id: b0bf6c1c-0dc9-4347-a0b3-fea07957af0c
Content-Type: application/xml
```

```xml
<?xml version="1.0"?><!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]><login xmlns="urn:microhubs:v1"><correo>&e;</correo><clave>********</clave></login>
```

**Respuesta.** HTTP 400 (esperado 400) · 7 ms · traza `b0bf6c1c-0dc9-4347-a0b3-fea07957af0c`

```xml
<?xml version='1.0' encoding='utf-8'?>
<error xmlns="urn:microhubs:v1" version="1"><codigo>XML_INVALIDO</codigo><mensaje>El cuerpo XML no está bien formado o contiene DTD/entidades.</mensaje><traza_id>b0bf6c1c-0dc9-4347-a0b3-fea07957af0c</traza_id></error>
```

**Explicación.** El lector XML (defusedxml) prohíbe DTD y entidades; el error también llega en XML.

### AUTH-06 · Validar token · PASA

**Objetivo.** Comprobar firma, vigencia y sesión activa en Redis.

**Petición.** `GET http://auth:5101/api/v1/auth/validar`

```http
Accept: application/json
X-Traza-Id: 64206c61-42f9-4a4c-adbe-bc74e5889348
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 9 ms · traza `64206c61-42f9-4a4c-adbe-bc74e5889348`

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
X-Traza-Id: f98650c7-79eb-4857-a2fd-3a669126e569
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 401 (esperado 401) · 7 ms · traza `f98650c7-79eb-4857-a2fd-3a669126e569`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.",
    "traza_id": "f98650c7-79eb-4857-a2fd-3a669126e569"
  }
}
```

### AUTH-08 · Renovar sesión · PASA

**Objetivo.** Obtener tokens nuevos con el token de renovación (rotación).

**Petición.** `POST http://auth:5101/api/v1/auth/renovar`

```http
Accept: application/json
X-Traza-Id: a42f12a7-2104-48d5-8b44-e26f5d30bbde
Content-Type: application/json
```

```json
{
  "token_renovacion": "rt_eb292384f8d400705c5374bf3f51d819"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 68 ms · traza `a42f12a7-2104-48d5-8b44-e26f5d30bbde`

```json
{
  "token_acceso": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwicm9sIjo…(291 caracteres)",
  "token_renovacion": "rt_947c4e4f87ec9566d2e5f2af8bce44e2",
  "tipo": "Bearer",
  "expira_en": 900
}
```

**Explicación.** El token de renovación usado se borra de Redis y su acceso anterior queda revocado.

**Evidencia en Redis.** `EXISTS auth:refresh:baafee30e231198ed2ae606f031521e2316eadef9392a3f0793ef81c3bc9179d`

```json
[
  {
    "comando": "EXISTS auth:refresh:baafee30e231198ed2ae606f031521e2316eadef9392a3f0793ef81c3bc9179d",
    "valor": 0
  }
]
```

### AUTH-09 · Reusar un token de renovación · PASA

**Objetivo.** Un token de renovación sirve una sola vez.

**Petición.** `POST http://auth:5101/api/v1/auth/renovar`

```http
Accept: application/json
X-Traza-Id: ac294a2f-2d9f-4bca-9fd8-852a009e655c
Content-Type: application/json
```

```json
{
  "token_renovacion": "rt_eb292384f8d400705c5374bf3f51d819"
}
```

**Respuesta.** HTTP 401 (esperado 401) · 7 ms · traza `ac294a2f-2d9f-4bca-9fd8-852a009e655c`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.",
    "traza_id": "ac294a2f-2d9f-4bca-9fd8-852a009e655c"
  }
}
```

### AUTH-10 · Cerrar sesión · PASA

**Objetivo.** Revocar el acceso del encabezado y la renovación del cuerpo.

**Petición.** `POST http://auth:5101/api/v1/auth/salir`

```http
Accept: application/json
X-Traza-Id: d973813f-aa2b-4c3c-b1cf-317ecfc6a0d8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "token_renovacion": "rt_947c4e4f87ec9566d2e5f2af8bce44e2"
}
```

**Respuesta.** HTTP 204 (esperado 204) · 41 ms · traza `d973813f-aa2b-4c3c-b1cf-317ecfc6a0d8`

```json
(sin cuerpo)
```

**Explicación.** El jti se agrega a la lista de revocados con TTL igual a su vida restante y sale del conjunto de sesión.

**Evidencia en Redis.** `TTL auth:jti:revocado:1c69b4d64a9844cd9dce8ae0c1827c0c; SISMEMBER auth:sesion:7 1c69b4d64a9844cd9dce8ae0c1827c0c`

```json
[
  {
    "comando": "TTL auth:jti:revocado:1c69b4d64a9844cd9dce8ae0c1827c0c",
    "valor": 899
  },
  {
    "comando": "SISMEMBER auth:sesion:7 1c69b4d64a9844cd9dce8ae0c1827c0c",
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
X-Traza-Id: 51da1747-657f-4058-a1e0-e6cd04dba101
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 401 (esperado 401) · 19 ms · traza `51da1747-657f-4058-a1e0-e6cd04dba101`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.",
    "traza_id": "51da1747-657f-4058-a1e0-e6cd04dba101"
  }
}
```

**Explicación.** El servicio de usuarios consulta auth:jti:revocado en Redis: la revocación es común a todos.

### USR-01 · Mi perfil (JSON) · PASA

**Objetivo.** Consultar el perfil de quien inició sesión.

**Petición.** `GET http://usuarios:5102/api/v1/usuarios/yo`

```http
Accept: application/json
X-Traza-Id: b010e293-8928-4181-a1b5-822f7671c045
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 29 ms · traza `b010e293-8928-4181-a1b5-822f7671c045`

```json
{
  "id": 7,
  "nombre": "Ramiro",
  "apellidos": "Alanís Lozano",
  "correo": "repartidor1@codex.mx",
  "telefono": "8112345678",
  "rol": "repartidor",
  "microhub": null,
  "ultimo_acceso": "2026-10-20T00:43:04-06:00"
}
```

### USR-02 · Mi perfil (XML) · PASA

**Objetivo.** El mismo recurso en XML según Accept.

**Petición.** `GET http://usuarios:5102/api/v1/usuarios/yo`

```http
Accept: application/xml
X-Traza-Id: 6530803f-710f-4a60-a1b0-be2bfdbfdcf6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 31 ms · traza `6530803f-710f-4a60-a1b0-be2bfdbfdcf6`

```xml
<?xml version='1.0' encoding='utf-8'?>
<usuario xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>5</id><nombre>Vanessa</nombre><apellidos>Morante López</apellidos><correo>planeador@codex.mx</correo><telefono>8178109897</telefono><rol>planeador</rol><microhub xsi:nil="true" /><ultimo_acceso>2026-10-20T00:43:05-06:00</ultimo_acceso></usuario>
```

### USR-03 · Actualizar mi teléfono (PATCH) · PASA

**Objetivo.** Modificar un dato del perfil.

**Petición.** `PATCH http://usuarios:5102/api/v1/usuarios/yo`

```http
Accept: application/json
X-Traza-Id: bcdd00f5-9f8d-4238-8bdc-54c2609c8964
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "telefono": "8112345678"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 63 ms · traza `bcdd00f5-9f8d-4238-8bdc-54c2609c8964`

```json
{
  "id": 7,
  "nombre": "Ramiro",
  "apellidos": "Alanís Lozano",
  "correo": "repartidor1@codex.mx",
  "telefono": "8112345678",
  "rol": "repartidor",
  "microhub": null,
  "ultimo_acceso": "2026-10-20T00:43:04-06:00"
}
```

**Explicación.** El trigger de auditoría registra el cambio con el usuario que actuó.

**Evidencia en PostgreSQL.** `SELECT id, telefono, actualizado_en FROM usuario WHERE id = 7`

```json
[
  {
    "id": 7,
    "telefono": "8112345678",
    "actualizado_en": "2026-10-20 06:43:05.725034+00:00"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT fecha, accion, entidad, detalle FROM auditoria WHERE entidad = 'usuario' AND entidad_id = '7' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "fecha": "2026-10-20 06:43:05.725034+00:00",
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
X-Traza-Id: 33ff76a8-55ed-4467-bc54-cc2e9835583a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "telefono": "12ab"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 7 ms · traza `33ff76a8-55ed-4467-bc54-cc2e9835583a`

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
    "traza_id": "33ff76a8-55ed-4467-bc54-cc2e9835583a"
  }
}
```

### USR-05 · Lista de usuarios (administrador) · PASA

**Objetivo.** Búsqueda y paginación.

**Petición.** `GET http://usuarios:5102/api/v1/usuarios?q=codex&rol=operador&pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 5d57f6ab-33d9-4a67-a139-8bd2d7fa595b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 112 ms · traza `5d57f6ab-33d9-4a67-a139-8bd2d7fa595b`

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
      "ultimo_acceso": "2026-10-20T00:32:38-06:00"
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
      "ultimo_acceso": "2026-10-20T00:32:39-06:00"
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
      "ultimo_acceso": "2026-10-20T00:32:22-06:00"
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
X-Traza-Id: 7ee4f39a-dc4e-450b-a9c1-17414039183b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 1327 ms · traza `7ee4f39a-dc4e-450b-a9c1-17414039183b`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "7ee4f39a-dc4e-450b-a9c1-17414039183b"
  }
}
```

**Evidencia en PostgreSQL.** `SELECT fecha, modulo, accion, detalle, exitoso FROM auditoria WHERE accion = 'acceso_denegado' ORDER BY id DESC LIMIT 1`

```json
[
  {
    "fecha": "2026-10-20 06:43:07.260921+00:00",
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
X-Traza-Id: 1345549e-91ca-4d85-9cb6-d09120a7f30e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 29 ms · traza `1345549e-91ca-4d85-9cb6-d09120a7f30e`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "1345549e-91ca-4d85-9cb6-d09120a7f30e"
  }
}
```

## Servicio productos · puerto 5103

### PRO-01 · Productos con búsqueda (caché vacía) · PASA

**Objetivo.** Consultar productos; la respuesta se guarda en Redis.

**Petición.** `GET http://productos:5103/api/v1/productos?q=arroz&pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 31d01cdd-2118-4f4b-856c-e7b92077e061
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 95 ms · traza `31d01cdd-2118-4f4b-856c-e7b92077e061`

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
X-Traza-Id: 810cf22f-e45a-4f9a-926e-da466317d13d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 8 ms · traza `810cf22f-e45a-4f9a-926e-da466317d13d`

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
X-Traza-Id: e43c8108-0700-4067-8aac-fd15ed9fff50
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 78 ms · traza `e43c8108-0700-4067-8aac-fd15ed9fff50`

```xml
<?xml version='1.0' encoding='utf-8'?>
<productos xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><datos><producto><id>3</id><clave_interna>AB-003</clave_interna><nombre>Aceite vegetal</nombre><categoria><id>1</id><nombre>Abarrote básico</nombre></categoria><unidad>botella</unidad><presentacion>900 ml</presentacion><precio>42.00</precio><imagen_url xsi:nil="true" /><estatus>activo</estatus></producto><producto><id>2</id><clave_interna>AB-002</clave_interna><nombre>Arroz superextra</nombre><categoria><id>1</id><nombre>Abarrote básico</nombre></categoria><unidad>kg</unidad><presentacion>1 kg</presentacion><precio>29.90</precio><imagen_url xsi:nil="true" /><estatus>activo</estatus></producto></datos><paginacion><pagina>1</pagina><por_pagina>2</por_pagina><total>51</total><paginas>26</paginas></paginacion></productos>
```

### PRO-04 · Un producto · PASA

**Objetivo.** Detalle por id.

**Petición.** `GET http://productos:5103/api/v1/productos/3`

```http
Accept: application/json
X-Traza-Id: 65c8eff2-62bf-4f2e-80ea-2e13b4862c1e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 55 ms · traza `65c8eff2-62bf-4f2e-80ea-2e13b4862c1e`

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
X-Traza-Id: 041a8120-eccd-4c81-846b-e448fbfc0266
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 50 ms · traza `041a8120-eccd-4c81-846b-e448fbfc0266`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "041a8120-eccd-4c81-846b-e448fbfc0266"
  }
}
```

### PRO-06 · Paginación fuera de rango · PASA

**Objetivo.** por_pagina máximo 100.

**Petición.** `GET http://productos:5103/api/v1/productos?por_pagina=500`

```http
Accept: application/json
X-Traza-Id: 8f893835-7049-4aa3-b43a-d74b62428566
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 6 ms · traza `8f893835-7049-4aa3-b43a-d74b62428566`

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
    "traza_id": "8f893835-7049-4aa3-b43a-d74b62428566"
  }
}
```

### PRO-07 · Sin token · PASA

**Objetivo.** Todo endpoint protegido exige Authorization: Bearer.

**Petición.** `GET http://productos:5103/api/v1/productos`

```http
Accept: application/json
X-Traza-Id: 8ba06218-5b2c-42ba-b324-cfc56f67e6c6
```

**Respuesta.** HTTP 401 (esperado 401) · 4 ms · traza `8ba06218-5b2c-42ba-b324-cfc56f67e6c6`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "Falta el encabezado Authorization: Bearer <token>.",
    "traza_id": "8ba06218-5b2c-42ba-b324-cfc56f67e6c6"
  }
}
```

## Servicio zonas · puerto 5108

### ZON-01 · Zonas (XML) · PASA

**Objetivo.** Colonias atendidas con centroide, válidas contra catalogos.xsd.

**Petición.** `GET http://zonas:5108/api/v1/zonas`

```http
Accept: application/xml
X-Traza-Id: d5defb0f-be8c-47f1-9101-c05833103f5b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 67 ms · traza `d5defb0f-be8c-47f1-9101-c05833103f5b`

```xml
<?xml version='1.0' encoding='utf-8'?>
<zonas xmlns="urn:microhubs:v1" version="1"><datos><zona><id>1</id><clave>ZN-SB01</clave><nombre>San Bernabé Centro</nombre><colonia>San Bernabé</colonia><codigo_postal>64100</codigo_postal><latitud>25.7455</latitud><longitud>-100.3585</longitud></zona><zona><id>2</id><clave>ZN-SB02</clave><nombre>Valles de San Bernabé</nombre><colonia>Valles de San Bernabé</colonia><codigo_postal>64103</codigo_postal><latitud>25.753</latitud><longitud>-100.369</longitud></zona><zona><id>3</id><clave>ZN-SB03</clave><nombre>Paseo de San Bernabé</nombre><colonia>Paseo de San Bernabé</colonia><codigo_postal>64103</codigo_postal><latitud>25.758</latitud><longitud>-100.3745</longitud></zona><zona><id>4</id><clave>ZN-SB04</clave><nombre>San Bernabé X (F-113)</nombre><colonia>San Bernabé X (F-113)</colonia><codigo_postal>64105</codigo_postal><latitud>25.7495</latitud><longitud>-100.38</longitud></zona></datos><paginacion><pagina>1</pagina><por_pagina>20</por_pagina><total>4</total><paginas>1</paginas></paginacion></zonas>
```

### ZON-02 · Una zona · PASA

**Objetivo.** Detalle por id.

**Petición.** `GET http://zonas:5108/api/v1/zonas/1`

```http
Accept: application/json
X-Traza-Id: d55f6901-29e2-4428-8d57-d87812a7cd33
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 24 ms · traza `d55f6901-29e2-4428-8d57-d87812a7cd33`

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
X-Traza-Id: e49603c1-992b-44da-8fa8-d2f7db2be40b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 23 ms · traza `e49603c1-992b-44da-8fa8-d2f7db2be40b`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "e49603c1-992b-44da-8fa8-d2f7db2be40b"
  }
}
```

### ZON-04 · Sin token · PASA

**Objetivo.** Todo endpoint protegido exige Authorization: Bearer.

**Petición.** `GET http://zonas:5108/api/v1/zonas`

```http
Accept: application/json
X-Traza-Id: 0e18428e-cdb2-422e-8099-b1cc691ddcbc
```

**Respuesta.** HTTP 401 (esperado 401) · 10 ms · traza `0e18428e-cdb2-422e-8099-b1cc691ddcbc`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "Falta el encabezado Authorization: Bearer <token>.",
    "traza_id": "0e18428e-cdb2-422e-8099-b1cc691ddcbc"
  }
}
```

## Servicio microhubs · puerto 5109

### MIC-01 · Microhubs activos · PASA

**Objetivo.** Microhubs con coordenadas y radio.

**Petición.** `GET http://microhubs:5109/api/v1/microhubs?estatus=activo`

```http
Accept: application/json
X-Traza-Id: bb338273-4e2b-4c0d-ba09-d2bee9f7178b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 73 ms · traza `bb338273-4e2b-4c0d-ba09-d2bee9f7178b`

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
X-Traza-Id: d7ad7ba0-1e47-42e8-afc5-c467fef0d08e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 24 ms · traza `d7ad7ba0-1e47-42e8-afc5-c467fef0d08e`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "d7ad7ba0-1e47-42e8-afc5-c467fef0d08e"
  }
}
```

### MIC-03 · Sin token · PASA

**Objetivo.** Todo endpoint protegido exige Authorization: Bearer.

**Petición.** `GET http://microhubs:5109/api/v1/microhubs`

```http
Accept: application/json
X-Traza-Id: 6b23d1ce-7a5d-4a76-ac16-dbd914e1c527
```

**Respuesta.** HTTP 401 (esperado 401) · 15 ms · traza `6b23d1ce-7a5d-4a76-ac16-dbd914e1c527`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "Falta el encabezado Authorization: Bearer <token>.",
    "traza_id": "6b23d1ce-7a5d-4a76-ac16-dbd914e1c527"
  }
}
```

## Servicio pedidos · puerto 5104

### PED-01 · Pedidos entregados (JSON) · PASA

**Objetivo.** Lista filtrada por estado y fechas.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos?estado=entregado&pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 3e1457a1-6c9e-4d32-9760-39a99abcbac9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 67 ms · traza `3e1457a1-6c9e-4d32-9760-39a99abcbac9`

```json
{
  "datos": [
    {
      "id": 282,
      "folio": "PED-20261020-000282",
      "estado": "entregado",
      "zona": {
        "id": 4,
        "nombre": "San Bernabé X (F-113)"
      },
      "microhub_id": 3,
      "total": 149.0,
      "creado_en": "2026-10-20T00:32:18-06:00"
    },
    {
      "id": 261,
      "folio": "PED-20261020-000261",
      "estado": "entregado",
      "zona": {
        "id": 1,
        "nombre": "San Bernabé Centro"
      },
      "microhub_id": 1,
      "total": 109.0,
      "creado_en": "2026-10-20T00:29:26-06:00"
    },
    {
      "id": 200,
      "folio": "PED-20261020-000200",
      "estado": "entregado",
      "zona": {
        "id": 3,
        "nombre": "Paseo de San Bernabé"
      },
      "microhub_id": 2,
      "total": 160.0,
      "creado_en": "2026-10-20T00:21:30-06:00"
    },
    {
      "id": 196,
      "folio": "PED-20261020-000196",
      "estado": "entregado",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "microhub_id": 2,
      "total": 175.0,
      "creado_en": "2026-10-20T00:16:12-06:00"
    },
    {
      "id": 157,
      "folio": "PED-20261020-000157",
      "estado": "entregado",
      "zona": {
        "id": 1,
        "nombre": "San Bernabé Centro"
      },
      "microhub_id": 1,
      "total": 207.0,
      "creado_en": "2026-10-19T19:32:27-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 123,
    "paginas": 25
  }
}
```

### PED-02 · Pedidos (XML) · PASA

**Objetivo.** La misma lista en XML.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos?estado=entregado&por_pagina=2`

```http
Accept: application/xml
X-Traza-Id: c215c799-c3b4-4209-9cb1-8f2a43e79c09
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 73 ms · traza `c215c799-c3b4-4209-9cb1-8f2a43e79c09`

```xml
<?xml version='1.0' encoding='utf-8'?>
<pedidos xmlns="urn:microhubs:v1" version="1"><datos><pedido><id>282</id><folio>PED-20261020-000282</folio><estado>entregado</estado><zona><id>4</id><nombre>San Bernabé X (F-113)</nombre></zona><microhub_id>3</microhub_id><total>149.00</total><creado_en>2026-10-20T00:32:18-06:00</creado_en></pedido><pedido><id>261</id><folio>PED-20261020-000261</folio><estado>entregado</estado><zona><id>1</id><nombre>San Bernabé Centro</nombre></zona><microhub_id>1</microhub_id><total>109.00</total><creado_en>2026-10-20T00:29:26-06:00</creado_en></pedido></datos><paginacion><pagina>1</pagina><por_pagina>2</por_pagina><total>123</total><paginas>62</paginas></paginacion></pedidos>
```

### PED-03 · Detalle con líneas · PASA

**Objetivo.** Cliente, domicilio y líneas del pedido.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/282`

```http
Accept: application/json
X-Traza-Id: 91a145d3-1198-48d9-aea9-ac792e14be5a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 81 ms · traza `91a145d3-1198-48d9-aea9-ac792e14be5a`

```json
{
  "id": 282,
  "folio": "PED-20261020-000282",
  "estado": "entregado",
  "cliente": {
    "nombre": "Alejandro Alanís González",
    "telefono": "8171493899"
  },
  "domicilio": {
    "calle": "Emiliano Zapata",
    "numero_ext": "1761",
    "colonia": "San Bernabé X (F-113)",
    "latitud": 25.749051,
    "longitud": -100.385889
  },
  "zona": {
    "id": 4,
    "nombre": "San Bernabé X (F-113)"
  },
  "microhub_id": 3,
  "subtotal": 134.0,
  "costo_envio": 15.0,
  "total": 149.0,
  "creado_en": "2026-10-20T00:32:18-06:00",
  "lineas": [
    {
      "id": 923,
      "producto_id": 36,
      "nombre": "Jamón de pavo",
      "cantidad": 2,
      "precio_unitario": 46.0,
      "importe": 92.0
    },
    {
      "id": 924,
      "producto_id": 9,
      "nombre": "Atún en agua",
      "cantidad": 2,
      "precio_unitario": 21.0,
      "importe": 42.0
    }
  ]
}
```

### PED-04 · Historial de estados · PASA

**Objetivo.** Cambios de estado con usuario y fecha.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/282/historial`

```http
Accept: application/json
X-Traza-Id: 7ee44b32-ac3e-4b31-810f-f40545c175ff
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 58 ms · traza `7ee44b32-ac3e-4b31-810f-f40545c175ff`

```json
{
  "pedido_id": 282,
  "eventos": [
    {
      "estado_anterior": null,
      "estado_nuevo": "creado",
      "usuario": null,
      "motivo": null,
      "fecha": "2026-10-20T00:32:18-06:00"
    },
    {
      "estado_anterior": "creado",
      "estado_nuevo": "asignado",
      "usuario": null,
      "motivo": null,
      "fecha": "2026-10-20T00:32:18-06:00"
    },
    {
      "estado_anterior": "asignado",
      "estado_nuevo": "en_preparacion",
      "usuario": "operador.mh03@codex.mx",
      "motivo": null,
      "fecha": "2026-10-20T00:32:18-06:00"
    },
    {
      "estado_anterior": "en_preparacion",
      "estado_nuevo": "en_ruta",
      "usuario": "operador.mh03@codex.mx",
      "motivo": null,
      "fecha": "2026-10-20T00:32:18-06:00"
    },
    {
      "estado_anterior": "en_ruta",
      "estado_nuevo": "entregado",
      "usuario": "repartidor1@codex.mx",
      "motivo": null,
      "fecha": "2026-10-20T00:32:24-06:00"
    }
  ]
}
```

**Evidencia en PostgreSQL.** `SELECT fecha, estado_anterior, estado_nuevo, usuario_id FROM historial_estatus WHERE pedido_id = %s ORDER BY fecha, id`

```json
[
  {
    "fecha": "2026-10-20 06:32:18.985768+00:00",
    "estado_anterior": null,
    "estado_nuevo": "creado",
    "usuario_id": null
  },
  {
    "fecha": "2026-10-20 06:32:18.985768+00:00",
    "estado_anterior": "creado",
    "estado_nuevo": "asignado",
    "usuario_id": null
  },
  {
    "fecha": "2026-10-20 06:32:18.985768+00:00",
    "estado_anterior": "asignado",
    "estado_nuevo": "en_preparacion",
    "usuario_id": 4
  },
  {
    "fecha": "2026-10-20 06:32:18.985768+00:00",
    "estado_anterior": "en_preparacion",
    "estado_nuevo": "en_ruta",
    "usuario_id": 4
  },
  {
    "fecha": "2026-10-20 06:32:24.421672+00:00",
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
X-Traza-Id: d4182324-7f40-4881-aefe-06eec20e01d8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 7 ms · traza `d4182324-7f40-4881-aefe-06eec20e01d8`

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
    "traza_id": "d4182324-7f40-4881-aefe-06eec20e01d8"
  }
}
```

### PED-06 · Pedido fuera del ámbito · PASA

**Objetivo.** El operador del MH-01 no ve pedidos de otro microhub (RN22).

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/1`

```http
Accept: application/json
X-Traza-Id: 75fcb4ab-9999-4cd8-b212-edcccc49d4ad
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 36 ms · traza `75fcb4ab-9999-4cd8-b212-edcccc49d4ad`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el pedido o no está en tu ámbito.",
    "traza_id": "75fcb4ab-9999-4cd8-b212-edcccc49d4ad"
  }
}
```

**Explicación.** El ámbito lo decide PostgreSQL con fn_pedidos_visibles; el servicio no lo puede saltar.

### PED-07 · Cerrar desde pedidos · PASA

**Objetivo.** Los cierres de entrega solo se registran en el servicio de entregas.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/282/estado`

```http
Accept: application/json
X-Traza-Id: 6a1f9b0e-3fd4-4d11-915a-2940dce9900f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "estado": "entregado"
}
```

**Respuesta.** HTTP 409 (esperado 409) · 9 ms · traza `6a1f9b0e-3fd4-4d11-915a-2940dce9900f`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "El cierre de una entrega se registra con POST /api/v1/entregas/{id}/resultado.",
    "traza_id": "6a1f9b0e-3fd4-4d11-915a-2940dce9900f"
  }
}
```

### PED-08 · Transición ilegal (regla del motor) · PASA

**Objetivo.** Un pedido entregado no puede regresar a preparación.

**Petición.** `PATCH http://pedidos:5104/api/v1/pedidos/2/estado`

```http
Accept: application/json
X-Traza-Id: 4e8cc6ac-b9a3-4c1c-acdd-1d01cd52fa02
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0Iiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "estado": "en_preparacion"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 65 ms · traza `4e8cc6ac-b9a3-4c1c-acdd-1d01cd52fa02`

```json
{
  "error": {
    "codigo": "REGLA_NEGOCIO",
    "mensaje": "RN20: transición ilegal entregado -> en_preparacion para el rol operador. El pedido PED-20261020-000002 conserva su estado.",
    "traza_id": "4e8cc6ac-b9a3-4c1c-acdd-1d01cd52fa02"
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
X-Traza-Id: f8bc3dfb-59ab-406b-b5a8-db436b763d7a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "evidencia-entrega-152.jpg",
  "tipo_mime": "image/jpeg",
  "contenido_base64": "/9j/4AAQSkZJRgABAQAAAQABAAAAAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcY…(368 caracteres)",
  "referencia": {
    "tipo": "entrega",
    "id": "152"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 194 ms · traza `f8bc3dfb-59ab-406b-b5a8-db436b763d7a`

```json
{
  "id": "6ad70d7de371ef54ba21bd40",
  "nombre": "evidencia-entrega-152.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "152"
  },
  "subido_por": 7,
  "creado_en": "2026-10-20T00:43:09-06:00"
}
```

**Explicación.** Se valida que el contenido sea JPEG real, se calcula su SHA-256 y que la entrega sea del repartidor.

**Evidencia en MongoDB.** `db.documentos.findOne({_id: ObjectId('6ad70d7de371ef54ba21bd40')}, {contenido: 0})`

```json
{
  "_id": "6ad70d7de371ef54ba21bd40",
  "nombre": "evidencia-entrega-152.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "152"
  },
  "subido_por": 7,
  "creado_en": "2026-10-20 06:43:09.097000+00:00"
}
```

### DOC-02 · Subir evidencia de la segunda entrega · PASA

**Objetivo.** Evidencia para el cierre parcial.

**Petición.** `POST http://documentos:5107/api/v1/documentos`

```http
Accept: application/json
X-Traza-Id: a9830285-9f36-4967-a0af-cbd1ea7c57dd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "evidencia-entrega-153.jpg",
  "tipo_mime": "image/jpeg",
  "contenido_base64": "/9j/4AAQSkZJRgABAQAAAQABAAAAAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcY…(368 caracteres)",
  "referencia": {
    "tipo": "entrega",
    "id": "153"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 35 ms · traza `a9830285-9f36-4967-a0af-cbd1ea7c57dd`

```json
{
  "id": "6ad70d7de371ef54ba21bd43",
  "nombre": "evidencia-entrega-153.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "153"
  },
  "subido_por": 7,
  "creado_en": "2026-10-20T00:43:09-06:00"
}
```

### DOC-03 · Tipo de archivo falso · PASA

**Objetivo.** Un PDF declarado como JPEG se rechaza por su firma.

**Petición.** `POST http://documentos:5107/api/v1/documentos`

```http
Accept: application/json
X-Traza-Id: 7483300a-360b-4835-8cf3-bfcb2d8fd576
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
    "id": "152"
  }
}
```

**Respuesta.** HTTP 422 (esperado 422) · 8 ms · traza `7483300a-360b-4835-8cf3-bfcb2d8fd576`

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
    "traza_id": "7483300a-360b-4835-8cf3-bfcb2d8fd576"
  }
}
```

### DOC-04 · Evidencia en entrega ajena · PASA

**Objetivo.** Un repartidor no adjunta a entregas de otro.

**Petición.** `POST http://documentos:5107/api/v1/documentos`

```http
Accept: application/json
X-Traza-Id: aaad143b-ce27-42c1-b497-7aff0665d420
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
    "id": "152"
  }
}
```

**Respuesta.** HTTP 403 (esperado 403) · 31 ms · traza `aaad143b-ce27-42c1-b497-7aff0665d420`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Solo puedes adjuntar evidencia a tus entregas.",
    "traza_id": "aaad143b-ce27-42c1-b497-7aff0665d420"
  }
}
```

### DOC-05 · Documento temporal · PASA

**Objetivo.** Documento que después se elimina.

**Petición.** `POST http://documentos:5107/api/v1/documentos`

```http
Accept: application/json
X-Traza-Id: 97b8a12c-8ac5-44be-a1a7-dcbb4b8c633b
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

**Respuesta.** HTTP 201 (esperado 201) · 7 ms · traza `97b8a12c-8ac5-44be-a1a7-dcbb4b8c633b`

```json
{
  "id": "6ad70d7de371ef54ba21bd4a",
  "nombre": "borrador.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "usuario",
    "id": "7"
  },
  "subido_por": 7,
  "creado_en": "2026-10-20T00:43:09-06:00"
}
```

### DOC-06 · Mis documentos · PASA

**Objetivo.** Filtro por referencia.

**Petición.** `GET http://documentos:5107/api/v1/documentos?referencia_tipo=entrega&referencia_id=152`

```http
Accept: application/json
X-Traza-Id: 0a0de542-20c4-4101-908d-143260adb75f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 22 ms · traza `0a0de542-20c4-4101-908d-143260adb75f`

```json
{
  "datos": [
    {
      "id": "6ad70d7de371ef54ba21bd40",
      "nombre": "evidencia-entrega-152.jpg",
      "tipo_mime": "image/jpeg",
      "tamano_bytes": 276,
      "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
      "referencia": {
        "tipo": "entrega",
        "id": "152"
      },
      "subido_por": 7,
      "creado_en": "2026-10-20T00:43:09-06:00"
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

**Petición.** `GET http://documentos:5107/api/v1/documentos/6ad70d7de371ef54ba21bd40`

```http
Accept: application/xml
X-Traza-Id: fde105d0-b7c7-479b-9430-9b1ca0774a19
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 9 ms · traza `fde105d0-b7c7-479b-9430-9b1ca0774a19`

```xml
<?xml version='1.0' encoding='utf-8'?>
<documento xmlns="urn:microhubs:v1" version="1"><id>6ad70d7de371ef54ba21bd40</id><nombre>evidencia-entrega-152.jpg</nombre><tipo_mime>image/jpeg</tipo_mime><tamano_bytes>276</tamano_bytes><sha256>7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc</sha256><referencia><tipo>entrega</tipo><id>152</id></referencia><subido_por>7</subido_por><creado_en>2026-10-20T00:43:09-06:00</creado_en></documento>
```

### DOC-08 · Contenido en Base64 · PASA

**Objetivo.** Recuperar el archivo.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6ad70d7de371ef54ba21bd40/contenido`

```http
Accept: application/json
X-Traza-Id: d0abcdf5-f375-4438-b5d9-f98d4581e3bc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 8 ms · traza `d0abcdf5-f375-4438-b5d9-f98d4581e3bc`

```json
{
  "id": "6ad70d7de371ef54ba21bd40",
  "nombre": "evidencia-entrega-152.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "152"
  },
  "subido_por": 7,
  "creado_en": "2026-10-20T00:43:09-06:00",
  "contenido_base64": "/9j/4AAQSkZJRgABAQAAAQABAAAAAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcY…(368 caracteres)"
}
```

### DOC-09 · Eliminar documento (DELETE) · PASA

**Objetivo.** Borrar un documento propio.

**Petición.** `DELETE http://documentos:5107/api/v1/documentos/6ad70d7de371ef54ba21bd4a`

```http
Accept: application/json
X-Traza-Id: e126fdc2-e594-4ece-923b-a0976ef40cda
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 29 ms · traza `e126fdc2-e594-4ece-923b-a0976ef40cda`

```json
(sin cuerpo)
```

**Evidencia en MongoDB.** `db.documentos.countDocuments({_id: ObjectId('6ad70d7de371ef54ba21bd4a')})`

```json
0
```

### DOC-10 · Id inexistente · PASA

**Objetivo.** Registro que no existe.

**Petición.** `GET http://documentos:5107/api/v1/documentos/ffffffffffffffffffffffff`

```http
Accept: application/json
X-Traza-Id: accede44-3d61-499f-8c66-2a1c68e99def
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 7 ms · traza `accede44-3d61-499f-8c66-2a1c68e99def`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el recurso solicitado.",
    "traza_id": "accede44-3d61-499f-8c66-2a1c68e99def"
  }
}
```

## Servicio seguimiento · puerto 5110

### SEG-01 · Enviar puntos GPS · PASA

**Objetivo.** Guardar el recorrido del repartidor en MongoDB.

**Petición.** `POST http://seguimiento:5110/api/v1/seguimiento/152/ubicaciones`

```http
Accept: application/json
X-Traza-Id: f481c6c0-1b4d-4c6c-a861-d8cf9ae2d739
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
      "capturado_en": "2026-10-20T06:37:09+00:00"
    },
    {
      "latitud": 25.7486,
      "longitud": -100.3606,
      "precision_m": 8.0,
      "capturado_en": "2026-10-20T06:39:09+00:00"
    },
    {
      "latitud": 25.7491,
      "longitud": -100.3611,
      "precision_m": 8.5,
      "capturado_en": "2026-10-20T06:41:09+00:00"
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 38 ms · traza `f481c6c0-1b4d-4c6c-a861-d8cf9ae2d739`

```json
{
  "recibidos": 3
}
```

**Evidencia en MongoDB.** `db.ubicaciones_entrega.find({entrega_id: NumberLong(152)}).sort({capturado_en: 1})`

```json
[
  {
    "entrega_id": 152,
    "usuario_id": 7,
    "posicion": {
      "type": "Point",
      "coordinates": [
        -100.36,
        25.748
      ]
    },
    "precision_m": 9.0,
    "capturado_en": "2026-10-20 06:37:09+00:00",
    "recibido_en": "2026-10-20 06:43:09.693000+00:00"
  },
  {
    "entrega_id": 152,
    "usuario_id": 7,
    "posicion": {
      "type": "Point",
      "coordinates": [
        -100.3606,
        25.7486
      ]
    },
    "precision_m": 8.0,
    "capturado_en": "2026-10-20 06:39:09+00:00",
    "recibido_en": "2026-10-20 06:43:09.693000+00:00"
  },
  {
    "entrega_id": 152,
    "usuario_id": 7,
    "posicion": {
      "type": "Point",
      "coordinates": [
        -100.3611,
        25.7491
      ]
    },
    "precision_m": 8.5,
    "capturado_en": "2026-10-20 06:41:09+00:00",
    "recibido_en": "2026-10-20 06:43:09.693000+00:00"
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

**Petición.** `GET http://seguimiento:5110/api/v1/seguimiento/152/recorrido`

```http
Accept: application/json
X-Traza-Id: 5aae7598-055f-46ab-b8b0-b7c9fc117614
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 37 ms · traza `5aae7598-055f-46ab-b8b0-b7c9fc117614`

```json
{
  "entrega_id": 152,
  "puntos": 3,
  "distancia_km": 0.16,
  "inicio": "2026-10-20T00:37:09-06:00",
  "fin": "2026-10-20T00:41:09-06:00",
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

**Petición.** `GET http://seguimiento:5110/api/v1/seguimiento/152/recorrido`

```http
Accept: application/json
X-Traza-Id: fedce83f-0b31-48ea-bc3d-626fbbfb9cd8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4Iiwi…(296 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 29 ms · traza `fedce83f-0b31-48ea-bc3d-626fbbfb9cd8`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe la entrega o no está asignada a ti.",
    "traza_id": "fedce83f-0b31-48ea-bc3d-626fbbfb9cd8"
  }
}
```

### SEG-04 · Recorrido sin token · PASA

**Objetivo.** Todo endpoint protegido exige Authorization: Bearer.

**Petición.** `GET http://seguimiento:5110/api/v1/seguimiento/152/recorrido`

```http
Accept: application/json
X-Traza-Id: faec8a91-b8a1-407a-9b33-a7bc5146cd32
```

**Respuesta.** HTTP 401 (esperado 401) · 11 ms · traza `faec8a91-b8a1-407a-9b33-a7bc5146cd32`

```json
{
  "error": {
    "codigo": "TOKEN_INVALIDO",
    "mensaje": "Falta el encabezado Authorization: Bearer <token>.",
    "traza_id": "faec8a91-b8a1-407a-9b33-a7bc5146cd32"
  }
}
```

## Servicio entregas · puerto 5105

### ENT-01 · Mis entregas · PASA

**Objetivo.** Paradas abiertas del repartidor en el turno de hoy (RN25).

**Petición.** `GET http://entregas:5105/api/v1/entregas/mias?pagina=1&por_pagina=20`

```http
Accept: application/json
X-Traza-Id: 5595f677-0e7e-4fb8-abfa-0e0d67f2f468
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 55 ms · traza `5595f677-0e7e-4fb8-abfa-0e0d67f2f468`

```json
{
  "datos": [
    {
      "id": 152,
      "pedido_id": 296,
      "folio": "PED-20261020-000296",
      "estado_pedido": "en_ruta",
      "orden_parada": 1,
      "direccion": "Rodrigo Gómez 1934, Paseo de San Bernabé",
      "zona": "Paseo de San Bernabé",
      "distancia_km": 0.57,
      "minutos_estimados": 10.0,
      "total": 159.0
    },
    {
      "id": 153,
      "pedido_id": 297,
      "folio": "PED-20261020-000297",
      "estado_pedido": "en_ruta",
      "orden_parada": 2,
      "direccion": "Camino a San Bernabé 913, Valles de San Bernabé",
      "zona": "Valles de San Bernabé",
      "distancia_km": 1.32,
      "minutos_estimados": 16.0,
      "total": 135.0
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

**Petición.** `GET http://entregas:5105/api/v1/entregas/152`

```http
Accept: application/json
X-Traza-Id: 952889a2-57e9-48b9-8abe-cf4998f41794
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 78 ms · traza `952889a2-57e9-48b9-8abe-cf4998f41794`

```json
{
  "id": 152,
  "pedido_id": 296,
  "folio": "PED-20261020-000296",
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
  "distancia_km": 0.57,
  "minutos_estimados": 10.0,
  "total": 159.0,
  "lineas": [
    {
      "pedido_detalle_id": 951,
      "nombre": "Refresco de cola",
      "cantidad": 2
    },
    {
      "pedido_detalle_id": 952,
      "nombre": "Pasta dental",
      "cantidad": 2
    }
  ]
}
```

### ENT-03 · Entrega de otro repartidor · PASA

**Objetivo.** El repartidor 2 no ve la entrega del repartidor 1.

**Petición.** `GET http://entregas:5105/api/v1/entregas/152`

```http
Accept: application/json
X-Traza-Id: d283af6b-3b77-4afb-b8d6-41ac16e76625
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4Iiwi…(296 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 66 ms · traza `d283af6b-3b77-4afb-b8d6-41ac16e76625`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe la entrega o no está asignada a ti.",
    "traza_id": "d283af6b-3b77-4afb-b8d6-41ac16e76625"
  }
}
```

### ENT-04 · Monto incorrecto (regla de negocio) · PASA

**Objetivo.** Una entrega completa cobra el total (RN27).

**Petición.** `POST http://entregas:5105/api/v1/entregas/152/resultado`

```http
Accept: application/json
X-Traza-Id: 64a06417-866c-4fad-97b8-ba100dd037a8
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
    "6ad70d7de371ef54ba21bd40"
  ],
  "capturado_en": "2026-10-20T06:43:09+00:00",
  "id_cliente_local": "3601ae18-3525-45d8-bb09-2b9014473f23"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 98 ms · traza `64a06417-866c-4fad-97b8-ba100dd037a8`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "Revisa los datos enviados.",
    "detalles": [
      {
        "campo": "monto_cobrado",
        "mensaje": "Una entrega completa cobra el total del pedido (159.00)."
      }
    ],
    "traza_id": "64a06417-866c-4fad-97b8-ba100dd037a8"
  }
}
```

### ENT-05 · Cerrar entrega como entregado · PASA

**Objetivo.** Registrar el resultado con evidencia y ubicación.

**Petición.** `POST http://entregas:5105/api/v1/entregas/152/resultado`

```http
Accept: application/json
X-Traza-Id: d488b6c3-9ca0-4f72-ad7e-c5508fc1437e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 159.0,
  "cambio_entregado": 0.0,
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611,
    "precision_m": 8.5
  },
  "evidencia_ids": [
    "6ad70d7de371ef54ba21bd40"
  ],
  "capturado_en": "2026-10-20T06:43:09+00:00",
  "id_cliente_local": "3601ae18-3525-45d8-bb09-2b9014473f23"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 145 ms · traza `d488b6c3-9ca0-4f72-ad7e-c5508fc1437e`

```json
{
  "entrega_id": 152,
  "pedido_id": 296,
  "estado_pedido": "entregado",
  "cerrado_en": "2026-10-20T00:43:10-06:00",
  "duplicado": false
}
```

**Explicación.** Una sola transacción: cierra la entrega, cambia el pedido (el trigger valida la transición y escribe historial y bitácora) y el trigger de cierre avisa al cliente. La operación se registra en MongoDB.

**Evidencia en PostgreSQL.** `SELECT id, cierre_en, resultado, monto_cobrado, id_cliente_local, evidencia_ids, cierre_latitud, cierre_longitud FROM entrega WHERE id = %s`

```json
[
  {
    "id": 152,
    "cierre_en": "2026-10-20 06:43:10.269992+00:00",
    "resultado": "entregado",
    "monto_cobrado": "159.00",
    "id_cliente_local": "3601ae18-3525-45d8-bb09-2b9014473f23",
    "evidencia_ids": [
      "6ad70d7de371ef54ba21bd40"
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
    "fecha": "2026-10-20 06:43:10.269992+00:00"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT destinatario_id, tipo, titulo, mensaje, referencia_tipo, referencia_id FROM web_notificacion WHERE referencia_tipo = 'pedido' AND referencia_id = %s ORDER BY id DESC LIMIT 1`

```json
[
  {
    "destinatario_id": 24,
    "tipo": "pedido",
    "titulo": "Pedido PED-20261020-000296",
    "mensaje": "El pedido cambió a entregado.",
    "referencia_tipo": "pedido",
    "referencia_id": "296"
  }
]
```

**Evidencia en MongoDB.** `db.sincronizaciones_moviles.findOne({operacion_uuid: '3601ae18-3525-45d8-bb09-2b9014473f23'})`

```json
{
  "operacion_uuid": "3601ae18-3525-45d8-bb09-2b9014473f23",
  "capturado_en": "2026-10-20 06:43:09+00:00",
  "carga": {
    "entrega_id": 152,
    "resultado": "entregado",
    "monto_cobrado": 159.0,
    "evidencia_ids": [
      "6ad70d7de371ef54ba21bd40"
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
  "pedido_id": 296,
  "sincronizado_en": "2026-10-20 06:43:10.343000+00:00",
  "tipo_operacion": "cierre_entrega",
  "usuario_id": 7
}
```

### ENT-06 · Reintento con el mismo UUID · PASA

**Objetivo.** Idempotencia: el cierre no se aplica dos veces.

**Petición.** `POST http://entregas:5105/api/v1/entregas/152/resultado`

```http
Accept: application/json
X-Traza-Id: 3dcbbef8-bc1e-49ec-81bf-a855a1c1f2a9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 159.0,
  "cambio_entregado": 0.0,
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611,
    "precision_m": 8.5
  },
  "evidencia_ids": [
    "6ad70d7de371ef54ba21bd40"
  ],
  "capturado_en": "2026-10-20T06:43:09+00:00",
  "id_cliente_local": "3601ae18-3525-45d8-bb09-2b9014473f23"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 98 ms · traza `3dcbbef8-bc1e-49ec-81bf-a855a1c1f2a9`

```json
{
  "entrega_id": 152,
  "pedido_id": 296,
  "estado_pedido": "entregado",
  "cerrado_en": "2026-10-20T00:43:10-06:00",
  "duplicado": true
}
```

**Explicación.** La respuesta es la misma con duplicado=true. MongoDB actualiza el documento de la operación (intentos = 2).

**Evidencia en MongoDB.** `db.sincronizaciones_moviles.findOne({operacion_uuid: '3601ae18-3525-45d8-bb09-2b9014473f23'}, {estado: 1, intentos: 1})`

```json
{
  "estado": "aplicada",
  "intentos": 2,
  "sincronizado_en": "2026-10-20 06:43:10.516000+00:00"
}
```

### ENT-07 · Otro cierre sobre la misma entrega · PASA

**Objetivo.** Conflicto: ya estaba cerrada con otra operación.

**Petición.** `POST http://entregas:5105/api/v1/entregas/152/resultado`

```http
Accept: application/json
X-Traza-Id: 2ed1ed55-20a3-42d7-bb14-2921f0fc19ed
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 159.0,
  "cambio_entregado": 0.0,
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611,
    "precision_m": 8.5
  },
  "evidencia_ids": [
    "6ad70d7de371ef54ba21bd40"
  ],
  "capturado_en": "2026-10-20T06:43:09+00:00",
  "id_cliente_local": "fbac7d51-8fe4-49c4-a4ab-e3e731d672e7"
}
```

**Respuesta.** HTTP 409 (esperado 409) · 91 ms · traza `2ed1ed55-20a3-42d7-bb14-2921f0fc19ed`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "La entrega ya se cerró con otra operación.",
    "traza_id": "2ed1ed55-20a3-42d7-bb14-2921f0fc19ed"
  }
}
```

### ENT-08 · Detalle tras el cierre · PASA

**Objetivo.** El repartidor deja de ver el domicilio (RN26).

**Petición.** `GET http://entregas:5105/api/v1/entregas/152`

```http
Accept: application/json
X-Traza-Id: 32ef51b5-ac0f-41b0-a825-ee3a18a7cfd6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 37 ms · traza `32ef51b5-ac0f-41b0-a825-ee3a18a7cfd6`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "La entrega ya se cerró; su información ya no está disponible.",
    "traza_id": "32ef51b5-ac0f-41b0-a825-ee3a18a7cfd6"
  }
}
```

### ENT-09 · Parcial sin motivo · PASA

**Objetivo.** Cada línea devuelta necesita motivo (RN28).

**Petición.** `POST http://entregas:5105/api/v1/entregas/153/resultado`

```http
Accept: application/json
X-Traza-Id: 9de0e797-1c22-42ba-ba51-c305b2b5b247
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
      "pedido_detalle_id": 953,
      "cantidad_entregada": 2,
      "cantidad_devuelta": 0
    },
    {
      "pedido_detalle_id": 954,
      "cantidad_entregada": 0,
      "cantidad_devuelta": 2
    }
  ],
  "ubicacion": {
    "latitud": 25.7491,
    "longitud": -100.3611
  },
  "evidencia_ids": [
    "6ad70d7de371ef54ba21bd43"
  ],
  "capturado_en": "2026-10-20T06:43:09+00:00",
  "id_cliente_local": "d66d8e77-f951-433b-8039-29b2d538c009"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 64 ms · traza `9de0e797-1c22-42ba-ba51-c305b2b5b247`

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
    "traza_id": "9de0e797-1c22-42ba-ba51-c305b2b5b247"
  }
}
```

### ENT-10 · Cerrar como entrega parcial · PASA

**Objetivo.** Devolver al inventario lo que no se entregó.

**Petición.** `POST http://entregas:5105/api/v1/entregas/153/resultado`

```http
Accept: application/json
X-Traza-Id: cbe23eeb-aef1-42a4-8aa1-b1a586c3683d
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
      "pedido_detalle_id": 953,
      "cantidad_entregada": 2,
      "cantidad_devuelta": 0
    },
    {
      "pedido_detalle_id": 954,
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
    "6ad70d7de371ef54ba21bd43"
  ],
  "capturado_en": "2026-10-20T06:43:09+00:00",
  "id_cliente_local": "d66d8e77-f951-433b-8039-29b2d538c009"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 122 ms · traza `cbe23eeb-aef1-42a4-8aa1-b1a586c3683d`

```json
{
  "entrega_id": 153,
  "pedido_id": 297,
  "estado_pedido": "entrega_parcial",
  "cerrado_en": "2026-10-20T00:43:10-06:00",
  "duplicado": false
}
```

**Explicación.** fn_devolver_inventario (la misma función que usa el web) regresa las unidades devueltas.

**Evidencia en PostgreSQL.** `SELECT entrega_id, pedido_detalle_id, cantidad_entregada, cantidad_devuelta, motivo FROM entrega_linea WHERE entrega_id = %s`

```json
[
  {
    "entrega_id": 153,
    "pedido_detalle_id": 953,
    "cantidad_entregada": 2,
    "cantidad_devuelta": 0,
    "motivo": null
  },
  {
    "entrega_id": 153,
    "pedido_detalle_id": 954,
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
    "producto_id": 20,
    "cantidad": 2,
    "existencia_resultante": 55,
    "motivo": "Entrega parcial: regresan las unidades devueltas (RN28)."
  }
]
```

### ENT-11 · Entregas de un pedido (administrador) · PASA

**Objetivo.** Consulta por pedido para el portal web.

**Petición.** `GET http://entregas:5105/api/v1/entregas?pedido_id=296`

```http
Accept: application/json
X-Traza-Id: 60eccc7c-a74f-4cd1-8b2b-aad059926dec
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 66 ms · traza `60eccc7c-a74f-4cd1-8b2b-aad059926dec`

```json
{
  "datos": [
    {
      "id": 152,
      "pedido_id": 296,
      "folio": "PED-20261020-000296",
      "estado_pedido": "entregado",
      "orden_parada": 1,
      "direccion": "Rodrigo Gómez 1934, Paseo de San Bernabé",
      "zona": "Paseo de San Bernabé",
      "distancia_km": 0.57,
      "minutos_estimados": 10.0,
      "total": 159.0
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
X-Traza-Id: 738814a0-cdc7-4503-85c1-8d80601e00d4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 69 ms · traza `738814a0-cdc7-4503-85c1-8d80601e00d4`

```xml
<?xml version='1.0' encoding='utf-8'?>
<candidatos xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><datos><candidato><id>1</id><clave>CAND-01</clave><nombre>San Bernabé Norte</nombre><latitud>25.752</latitud><longitud>-100.361</longitud><renta_estimada>18000.00</renta_estimada><nomina_estimada>42000.00</nomina_estimada><servicios_estimados>7000.00</servicios_estimados><otros_costos>5000.00</otros_costos><costo_fijo>72000.00</costo_fijo><superficie_m2>130</superficie_m2><capacidad_fisica>150</capacidad_fisica><accesibilidad_vial>9</accesibilidad_vial><zona_id>1</zona_id><poblacion_cubierta>8420</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato><candidato><id>2</id><clave>CAND-02</clave><nombre>Valles Poniente</nombre><latitud>25.7555</latitud><longitud>-100.376</longitud><renta_estimada>15500.00</renta_estimada><nomina_estimada>42000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><costo_fijo>68500.00</costo_fijo><superficie_m2>105</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>2</zona_id><poblacion_cubierta>6180</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato><candidato><id>3</id><clave>CAND-05</clave><nombre>Alianza Real</nombre><latitud>25.7625</latitud><longitud>-100.353</longitud><renta_estimada>21000.00</renta_estimada><nomina_estimada>46000.00</nomina_estimada><servicios_estimados>8000.00</servicios_estimados><otros_costos>6000.00</otros_costos><costo_fijo>81000.00</costo_fijo><superficie_m2>150</superficie_m2><capacidad_fisica>180</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>3900</poblacion_cubierta><radio_km>1.6</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>8</total><paginas>3</paginas></paginacion></candidatos>
```

### PLA-02 · Registrar candidato (XML) · PASA

**Objetivo.** Alta con costo fijo calculado por PostgreSQL.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos`

```http
Accept: application/xml
X-Traza-Id: eb339eee-2586-48e6-a9c3-33c66ff96b9f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><candidato_nuevo xmlns="urn:microhubs:v1"><clave>********</clave><nombre>Alianza Norte</nombre><latitud>25.7601</latitud><longitud>-100.3555</longitud><renta_estimada>16000.00</renta_estimada><nomina_estimada>40000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><superficie_m2>110</superficie_m2><capacidad_fisica>130</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km></candidato_nuevo>
```

**Respuesta.** HTTP 201 (esperado 201) · 65 ms · traza `eb339eee-2586-48e6-a9c3-33c66ff96b9f`

```xml
<?xml version='1.0' encoding='utf-8'?>
<candidato xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>77</id><clave>EV-F76303</clave><nombre>Alianza Norte</nombre><latitud>25.7601</latitud><longitud>-100.3555</longitud><renta_estimada>16000.00</renta_estimada><nomina_estimada>40000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><costo_fijo>67000.00</costo_fijo><superficie_m2>110</superficie_m2><capacidad_fisica>130</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato>
```

**Evidencia en PostgreSQL.** `SELECT id, clave, nombre, renta_estimada, costo_fijo, decision FROM ubicacion_candidata WHERE clave = %s`

```json
[
  {
    "id": 77,
    "clave": "EV-F76303",
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
X-Traza-Id: 7d28e696-1e12-4dfd-a07c-34d9faecad6a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><candidato_nuevo xmlns="urn:microhubs:v1"><clave>********</clave><nombre>Alianza Norte</nombre><latitud>25.7601</latitud><longitud>-100.3555</longitud><renta_estimada>16000.00</renta_estimada><nomina_estimada>40000.00</nomina_estimada><servicios_estimados>6500.00</servicios_estimados><otros_costos>4500.00</otros_costos><superficie_m2>110</superficie_m2><capacidad_fisica>130</capacidad_fisica><accesibilidad_vial>7</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km></candidato_nuevo>
```

**Respuesta.** HTTP 409 (esperado 409) · 73 ms · traza `7d28e696-1e12-4dfd-a07c-34d9faecad6a`

```xml
<?xml version='1.0' encoding='utf-8'?>
<error xmlns="urn:microhubs:v1" version="1"><codigo>CONFLICTO</codigo><mensaje>Ya existe un registro con esos datos.</mensaje><traza_id>7d28e696-1e12-4dfd-a07c-34d9faecad6a</traza_id></error>
```

### PLA-04 · Modificar candidato (PUT) · PASA

**Objetivo.** Cambiar la renta recalcula el costo fijo.

**Petición.** `PUT http://planeacion:5106/api/v1/candidatos/77`

```http
Accept: application/json
X-Traza-Id: 2e794865-77c3-4ee6-afdc-1cc81483430a
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

**Respuesta.** HTTP 200 (esperado 200) · 78 ms · traza `2e794865-77c3-4ee6-afdc-1cc81483430a`

```json
{
  "id": 77,
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

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/77/simular`

```http
Accept: application/xml
X-Traza-Id: fef366cd-f8c9-4f92-be04-09c1edcbb43b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<simular xmlns="urn:microhubs:v1"/>
```

**Respuesta.** HTTP 200 (esperado 200) · 288 ms · traza `fef366cd-f8c9-4f92-be04-09c1edcbb43b`

```xml
<?xml version='1.0' encoding='utf-8'?>
<resultados xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><atendidos>0</atendidos><rechazados>0</rechazados><utilizacion>0</utilizacion><nivel>estable</nivel><tiempo_estimado_min>18.6</tiempo_estimado_min><operadores_requeridos>0</operadores_requeridos><repartidores_requeridos>0</repartidores_requeridos><ingreso_dia>0.00</ingreso_dia><margen_dia>-2300.00</margen_dia><costo_por_pedido xsi:nil="true" /><equilibrio><margen_pedido>24.27</margen_pedido><mensual>2842.8</mensual><diario>94.8</diario></equilibrio><decision>NO VIABLE CON LOS SUPUESTOS ACTUALES</decision><explicacion><motivo>la demanda atendida (0/día) no alcanza el equilibrio (95/día)</motivo><motivo>reducir costos fijos, aumentar ticket o buscar una ubicación con más demanda</motivo></explicacion></resultados>
```

**Explicación.** Usa planeacion_calc.py (las mismas fórmulas del web) y guarda la ejecución en MongoDB.

**Evidencia en MongoDB.** `db.ejecuciones_analiticas.find().sort({ejecutado_en: -1}).limit(1)`

```json
{
  "escenario_id": "candidato-77",
  "nombre_escenario": "Candidato 77",
  "tipo_analisis": "punto_equilibrio",
  "ejecutado_en": "2026-10-20 06:43:11.541000+00:00",
  "usuario_id": 5,
  "version_modelo": "planeacion_calc 2.1",
  "parametros_entrada": {
    "demanda_diaria": 0.0,
    "operadores": 3.0,
    "repartidores": 3.0,
    "ticket": 150.97,
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
    "ticket = 150.97",
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
    "equilibrio_diario": 94.8,
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

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/77/decision`

```http
Accept: application/json
X-Traza-Id: 878924a1-c959-4083-a4b9-d3088da6ef36
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aceptado",
  "motivo": "ok"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 25 ms · traza `878924a1-c959-4083-a4b9-d3088da6ef36`

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
    "traza_id": "878924a1-c959-4083-a4b9-d3088da6ef36"
  }
}
```

### PLA-07 · Decisión humana de apertura · PASA

**Objetivo.** Registrar la decisión con motivo.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/77/decision`

```http
Accept: application/json
X-Traza-Id: d9863acf-203e-4419-a3db-01dffb4f44de
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "condicionado",
  "motivo": "Renegociar la renta antes de firmar."
}
```

**Respuesta.** HTTP 200 (esperado 200) · 64 ms · traza `d9863acf-203e-4419-a3db-01dffb4f44de`

```json
{
  "id": 77,
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
    "id": 77,
    "decision": "condicionado",
    "decision_motivo": "Renegociar la renta antes de firmar.",
    "decision_por": 5,
    "decision_en": "2026-10-20 06:43:11.614917+00:00"
  }
]
```

### PLA-08 · Simulación libre: Escenario A · PASA

**Objetivo.** Punto de equilibrio del caso de la retroalimentación.

**Petición.** `POST http://planeacion:5106/api/v1/simulaciones`

```http
Accept: application/json
X-Traza-Id: 28aae466-1b74-46e0-b6f1-15117a6b22fc
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

**Respuesta.** HTTP 200 (esperado 200) · 30 ms · traza `28aae466-1b74-46e0-b6f1-15117a6b22fc`

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
X-Traza-Id: 0cf3a7ea-0b71-4df5-8c74-0dcd9c302c0b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Escenario A - evidencias",
  "candidato_id": 77,
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

**Respuesta.** HTTP 201 (esperado 201) · 85 ms · traza `0cf3a7ea-0b71-4df5-8c74-0dcd9c302c0b`

```json
{
  "id": 11,
  "nombre": "Escenario A - evidencias",
  "candidato_id": 77,
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
  "creado_en": "2026-10-20T00:43:11-06:00"
}
```

### PLA-10 · Abrir escenario (XML) · PASA

**Objetivo.** Escenario con supuestos y resultados.

**Petición.** `GET http://planeacion:5106/api/v1/escenarios/11`

```http
Accept: application/xml
X-Traza-Id: bc5765c5-f14d-41a4-94e0-228a21cdc1bf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 23 ms · traza `bc5765c5-f14d-41a4-94e0-228a21cdc1bf`

```xml
<?xml version='1.0' encoding='utf-8'?>
<escenario xmlns="urn:microhubs:v1" version="1"><id>11</id><nombre>Escenario A - evidencias</nombre><candidato_id>77</candidato_id><supuestos><demanda_diaria>120</demanda_diaria><operadores>3</operadores><repartidores>4</repartidores><ticket>135.00</ticket><costo_entrega>22.00</costo_entrega><margen_bruto>0.28</margen_bruto><renta>18000.00</renta><nomina>42000.00</nomina><servicios>7000.00</servicios><otros>5000.00</otros><distancia_km>2.4</distancia_km><capacidad_fisica>150</capacidad_fisica></supuestos><resultados><atendidos>120</atendidos><rechazados>0</rechazados><utilizacion>80</utilizacion><nivel>atencion</nivel><tiempo_estimado_min>19.4</tiempo_estimado_min><operadores_requeridos>3</operadores_requeridos><repartidores_requeridos>2</repartidores_requeridos><ingreso_dia>16200.00</ingreso_dia><margen_dia>-504.00</margen_dia><costo_por_pedido>42.00</costo_por_pedido><equilibrio><margen_pedido>15.80</margen_pedido><mensual>4557</mensual><diario>151.9</diario></equilibrio><decision>NO VIABLE CON LOS SUPUESTOS ACTUALES</decision><explicacion><motivo>la demanda atendida (120/día) no alcanza el equilibrio (152/día)</motivo><motivo>el espacio físico del local limita la capacidad</motivo><motivo>reducir costos fijos, aumentar ticket o buscar una ubicación con más demanda</motivo></explicacion></resultados><creado_en>2026-10-20T00:43:11-06:00</creado_en></escenario>
```

### PLA-11 · Resumen de simulaciones · PASA

**Objetivo.** Agregación $group en MongoDB por decisión.

**Petición.** `GET http://planeacion:5106/api/v1/simulaciones/resumen`

```http
Accept: application/json
X-Traza-Id: 28ca9a95-4302-4856-8a9b-0a4aa89d5095
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 11 ms · traza `28ca9a95-4302-4856-8a9b-0a4aa89d5095`

```json
{
  "total": 29,
  "por_decision": [
    {
      "decision": "NO VIABLE CON LOS SUPUESTOS ACTUALES",
      "cantidad": 29,
      "utilizacion_promedio": 55.2
    }
  ]
}
```

**Evidencia en MongoDB.** `db.ejecuciones_analiticas.aggregate([{$match:{tipo_analisis:'punto_equilibrio'}}, {$group:{_id:'$resultados.decision', cantidad:{$sum:1}, utilizacion_promedio:{$avg:'$resultados.utilizacion'}}}])`

```json
[
  {
    "_id": "NO VIABLE CON LOS SUPUESTOS ACTUALES",
    "cantidad": 29,
    "utilizacion_promedio": 55.172413793103445
  }
]
```

### PLA-12 · Auditor intenta registrar · PASA

**Objetivo.** El auditor solo consulta (RN-E01).

**Petición.** `POST http://planeacion:5106/api/v1/candidatos`

```http
Accept: application/json
X-Traza-Id: 7c26db7f-2a85-4172-aa0a-d630f430d9e3
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

**Respuesta.** HTTP 403 (esperado 403) · 25 ms · traza `7c26db7f-2a85-4172-aa0a-d630f430d9e3`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "7c26db7f-2a85-4172-aa0a-d630f430d9e3"
  }
}
```

### PLA-13 · Auditor intenta simular · PASA

**Objetivo.** Sin simulacion.ejecutar.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/77/simular`

```http
Accept: application/json
X-Traza-Id: 5364e3fe-1135-4a6c-a224-c08763bfccaa
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 403 (esperado 403) · 25 ms · traza `5364e3fe-1135-4a6c-a224-c08763bfccaa`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "5364e3fe-1135-4a6c-a224-c08763bfccaa"
  }
}
```

### PLA-14 · Eliminar escenario (DELETE) · PASA

**Objetivo.** Borrar un escenario.

**Petición.** `DELETE http://planeacion:5106/api/v1/escenarios/11`

```http
Accept: application/json
X-Traza-Id: d66d5a15-9039-462f-821e-01f70f364edd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 34 ms · traza `d66d5a15-9039-462f-821e-01f70f364edd`

```json
(sin cuerpo)
```

### PLA-15 · Dar de baja candidato (DELETE) · PASA

**Objetivo.** Baja lógica: se conserva su historia.

**Petición.** `DELETE http://planeacion:5106/api/v1/candidatos/77`

```http
Accept: application/json
X-Traza-Id: 00bef742-2fd8-4810-b95f-a2331ebac2b2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 60 ms · traza `00bef742-2fd8-4810-b95f-a2331ebac2b2`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT id, clave, estatus, decision FROM ubicacion_candidata WHERE id = %s`

```json
[
  {
    "id": 77,
    "clave": "EV-F76303",
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
X-Traza-Id: 534db7b8-be41-40fe-a2dc-78151fbda5f8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 25 ms · traza `534db7b8-be41-40fe-a2dc-78151fbda5f8`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe el candidato.",
    "traza_id": "534db7b8-be41-40fe-a2dc-78151fbda5f8"
  }
}
```

## Servicio inventario · puerto 5111

### INV-01 · Existencias por microhub · PASA

**Objetivo.** Existencia física, reservada y disponible de cada producto.

**Petición.** `GET http://inventario:5111/api/v1/inventario?por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 18c91b4a-c9c3-4145-99ca-49ceb456526a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 538 ms · traza `18c91b4a-c9c3-4145-99ca-49ceb456526a`

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
      "actualizado_en": "2026-10-20T00:32:53-06:00"
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
      "actualizado_en": "2026-10-20T00:32:06-06:00"
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
      "actualizado_en": "2026-10-20T00:31:43-06:00"
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
      "actualizado_en": "2026-10-20T00:41:25-06:00"
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
    "unidades": 7335,
    "reservado": 0
  }
]
```

### INV-02 · Existencias (XML) · PASA

**Objetivo.** La app de escritorio recibe XML que cumple inventario.xsd.

**Petición.** `GET http://inventario:5111/api/v1/inventario?por_pagina=3`

```http
Accept: application/xml
X-Traza-Id: 3174e8ab-be0e-4e14-8cd8-c87b490357bb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 50 ms · traza `3174e8ab-be0e-4e14-8cd8-c87b490357bb`

```xml
<?xml version='1.0' encoding='utf-8'?>
<existencias xmlns="urn:microhubs:v1" version="1"><datos><existencia><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><producto><id>1</id><clave_interna>AB-001</clave_interna><nombre>Frijol negro a granel</nombre></producto><existencia>60</existencia><minimo>10</minimo><reservado>0</reservado><disponible>60</disponible><estado>normal</estado><actualizado_en>2026-10-20T00:32:53-06:00</actualizado_en></existencia><existencia><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><producto><id>2</id><clave_interna>AB-002</clave_interna><nombre>Arroz superextra</nombre></producto><existencia>35</existencia><minimo>10</minimo><reservado>0</reservado><disponible>35</disponible><estado>normal</estado><actualizado_en>2026-10-20T00:32:06-06:00</actualizado_en></existencia><existencia><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><producto><id>3</id><clave_interna>AB-003</clave_interna><nombre>Aceite vegetal</nombre></producto><existencia>10</existencia><minimo>5</minimo><reservado>0</reservado><disponible>10</disponible><estado>normal</estado><actualizado_en>2026-10-20T00:31:43-06:00</actualizado_en></existencia></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>153</total><paginas>51</paginas></paginacion></existencias>
```

### INV-03 · Filtro de estado inválido · PASA

**Objetivo.** Un filtro desconocido se rechaza.

**Petición.** `GET http://inventario:5111/api/v1/inventario?estado=inventado`

```http
Accept: application/json
X-Traza-Id: a3621180-623d-48e7-be6e-375a2666a5b2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 7 ms · traza `a3621180-623d-48e7-be6e-375a2666a5b2`

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
    "traza_id": "a3621180-623d-48e7-be6e-375a2666a5b2"
  }
}
```

### INV-04 · El operador ve solo su microhub · PASA

**Objetivo.** Ámbito por microhub del perfil operador.

**Petición.** `GET http://inventario:5111/api/v1/inventario?por_pagina=100`

```http
Accept: application/json
X-Traza-Id: dfa27c66-43ea-4b87-be83-c3d617761c3a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 61 ms · traza `dfa27c66-43ea-4b87-be83-c3d617761c3a`

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
      "actualizado_en": "2026-10-20T00:32:53-06:00"
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
      "actualizado_en": "2026-10-20T00:32:06-06:00"
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
      "actualizado_en": "2026-10-20T00:31:43-06:00"
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
      "actualizado_en": "2026-10-20T00:41:25-06:00"
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
      "existencia": 66,
      "minimo": 10,
      "reservado": 0,
      "disponible": 66,
      "estado": "normal",
      "actualizado_en": "2026-10-20T00:32:53-06:00"
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
      "actualizado_en": "2026-10-20T00:32:53-06:00"
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
      "actualizado_en": "2026-10-20T00:41:25-06:00"
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
      "actualizado_en": "2026-10-20T00:32:29-06:00"
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
      "existencia": 371,
      "minimo": 10,
      "reservado": 0,
      "disponible": 371,
      "estado": "normal",
      "actualizado_en": "2026-10-20T00:41:25-06:00"
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
      "existencia": 31,
      "minimo": 10,
      "reservado": 0,
      "disponible": 31,
      "estado": "normal",
      "actualizado_en": "2026-10-20T00:29:26-06:00"
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
      "existencia": 206,
      "minimo": 8,
      "reservado": 0,
      "disponible": 206,
      "estado": "normal",
      "actualizado_en": "2026-10-20T00:31:43-06:00"
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
      "actualizado_en": "2026-10-20T00:32:06-06:00"
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
      "actualizado_en": "2026-10-20T00:32:34-06:00"
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
      "existencia": 84,
      "minimo": 8,
      "reservado": 0,
      "disponible": 84,
      "estado": "normal",
      "actualizado_en": "2026-10-20T00:32:06-06:00"
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
      "actualizado_en": "2026-10-20T00:41:25-06:00"
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
      "actualizado_en": "2026-10-20T00:31:43-06:00"
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
      "actualizado_en": "2026-10-20T00:32:53-06:00"
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
      "existencia": 79,
      "minimo": 5,
      "reservado": 0,
      "disponible": 79,
      "estado": "normal",
      "actualizado_en": "2026-10-20T00:32:53-06:00"
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
      "actualizado_en": "2026-10-20T00:31:43-06:00"
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
      "actualizado_en": "2026-10-20T00:41:25-06:00"
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
      "actualizado_en": "2026-10-20T00:41:25-06:00"
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
      "actualizado_en": "2026-10-20T00:31:43-06:00"
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
      "actualizado_en": "2026-10-20T00:32:06-06:00"
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
      "existencia": 36,
      "minimo": 5,
      "reservado": 0,
      "disponible": 36,
      "estado": "normal",
      "actualizado_en": "2026-10-19T19:32:27-06:00"
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
      "actualizado_en": "2026-10-20T00:41:25-06:00"
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
      "actualizado_en": "2026-10-20T00:32:06-06:00"
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
      "actualizado_en": "2026-10-20T00:31:43-06:00"
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
      "actualizado_en": "2026-10-20T00:32:53-06:00"
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
      "actualizado_en": "2026-10-20T00:31:43-06:00"
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
      "actualizado_en": "2026-10-20T00:32:53-06:00"
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
      "actualizado_en": "2026-10-20T00:41:25-06:00"
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
      "actualizado_en": "2026-10-20T00:32:06-06:00"
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
      "actualizado_en": "2026-10-20T00:31:43-06:00"
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
      "existencia": 47,
      "minimo": 10,
      "reservado": 0,
      "disponible": 47,
      "estado": "normal",
      "actualizado_en": "2026-10-20T00:32:18-06:00"
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
      "actualizado_en": "2026-10-20T00:32:06-06:00"
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
      "actualizado_en": "2026-10-20T00:31:43-06:00"
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
      "actualizado_en": "2026-10-20T00:32:53-06:00"
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
      "actualizado_en": "2026-10-20T00:32:06-06:00"
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
      "actualizado_en": "2026-10-20T00:41:25-06:00"
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
      "actualizado_en": "2026-10-20T00:41:25-06:00"
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
      "actualizado_en": "2026-10-20T00:32:53-06:00"
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
      "actualizado_en": "2026-10-20T00:41:25-06:00"
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
X-Traza-Id: b70dd484-16e8-4aa6-9f40-437f609f313d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 7 ms · traza `b70dd484-16e8-4aa6-9f40-437f609f313d`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "b70dd484-16e8-4aa6-9f40-437f609f313d"
  }
}
```

### INV-06 · Una existencia · PASA

**Objetivo.** Existencia, apartado y disponible de un producto en un microhub.

**Petición.** `GET http://inventario:5111/api/v1/inventario/1/6`

```http
Accept: application/json
X-Traza-Id: f6ef1254-2d20-4a26-9b37-63533274ceca
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 30 ms · traza `f6ef1254-2d20-4a26-9b37-63533274ceca`

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
  "existencia": 66,
  "minimo": 10,
  "reservado": 0,
  "disponible": 66,
  "estado": "normal",
  "actualizado_en": "2026-10-20T00:32:53-06:00"
}
```

### INV-07 · Recibir mercancía · PASA

**Objetivo.** Suma al inventario y deja el movimiento con la referencia.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: 1f6e4b14-abf3-4b64-87c3-c67dc2a09a61
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
  "operacion_uuid": "f1cdeffb-160c-4fc5-932d-7f6987a43418",
  "referencia": {
    "tipo": "orden_compra",
    "id": "1"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 86 ms · traza `1f6e4b14-abf3-4b64-87c3-c67dc2a09a61`

```json
{
  "movimiento": {
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
  "duplicado": false
}
```

**Explicación.** Bloquea la fila del inventario, suma, y guarda el movimiento con la existencia resultante. La operacion_uuid hace el movimiento idempotente.

**Evidencia en PostgreSQL.** `SELECT id, tipo, cantidad, existencia_resultante, referencia_tipo, referencia_id, operacion_uuid FROM movimiento_inventario WHERE operacion_uuid = %s`

```json
[
  {
    "id": 1465,
    "tipo": "recepcion",
    "cantidad": 5,
    "existencia_resultante": 71,
    "referencia_tipo": "orden_compra",
    "referencia_id": 1,
    "operacion_uuid": "f1cdeffb-160c-4fc5-932d-7f6987a43418"
  }
]
```

**Evidencia en PostgreSQL.** `SELECT existencia FROM inventario WHERE microhub_id = %s AND producto_id = %s`

```json
[
  {
    "existencia": 71
  }
]
```

### INV-08 · Reintento con la misma operación · PASA

**Objetivo.** Idempotencia: la misma entrada no se aplica dos veces.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: 06ad5dcd-8d7e-432a-a996-e7ead6c865bc
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
  "operacion_uuid": "f1cdeffb-160c-4fc5-932d-7f6987a43418",
  "referencia": {
    "tipo": "orden_compra",
    "id": "1"
  }
}
```

**Respuesta.** HTTP 200 (esperado 200) · 27 ms · traza `06ad5dcd-8d7e-432a-a996-e7ead6c865bc`

```json
{
  "movimiento": {
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
    "existencia": 71
  }
]
```

### INV-09 · Ajuste sin motivo · PASA

**Objetivo.** Un ajuste, merma o conteo necesita el motivo.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: e0f4eb19-a903-41d6-8c77-126f96bee502
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

**Respuesta.** HTTP 422 (esperado 422) · 8 ms · traza `e0f4eb19-a903-41d6-8c77-126f96bee502`

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
    "traza_id": "e0f4eb19-a903-41d6-8c77-126f96bee502"
  }
}
```

### INV-10 · Ajuste grande por un operador · PASA

**Objetivo.** Más de 25 unidades lo autoriza un administrador.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: b0e0715f-9de8-4cac-857a-bcefa960affb
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

**Respuesta.** HTTP 403 (esperado 403) · 46 ms · traza `b0e0715f-9de8-4cac-857a-bcefa960affb`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Un movimiento de más de 25 unidades lo autoriza un administrador.",
    "traza_id": "b0e0715f-9de8-4cac-857a-bcefa960affb"
  }
}
```

**Explicación.** El umbral viene de configuracion.umbral_ajuste_inventario, no de una constante en el código.

### INV-11 · Ajuste grande por un administrador · PASA

**Objetivo.** El administrador sí puede.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: 9416863a-35d4-4d8b-8060-d74b4d4a7749
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

**Respuesta.** HTTP 201 (esperado 201) · 62 ms · traza `9416863a-35d4-4d8b-8060-d74b4d4a7749`

```json
{
  "movimiento": {
    "id": 1466,
    "microhub_id": 1,
    "producto_id": 6,
    "tipo": "ajuste",
    "cantidad": 30,
    "existencia_resultante": 101,
    "referencia": null,
    "motivo": "Ajuste grande de prueba",
    "usuario_id": 1,
    "fecha": "2026-10-20T00:43:15-06:00"
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
    "existencia_resultante": 101,
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
X-Traza-Id: 45371d53-a5c7-4c13-b281-b71eac01eb1a
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
  "operacion_uuid": "d3b2fec0-4c44-4576-9821-aca14425e950"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 105 ms · traza `45371d53-a5c7-4c13-b281-b71eac01eb1a`

```json
{
  "producto_id": 7,
  "cantidad": 2,
  "duplicado": false,
  "origen": {
    "microhub_id": 1,
    "existencia": 12,
    "movimiento_id": 1469
  },
  "destino": {
    "microhub_id": 2,
    "existencia": 82,
    "movimiento_id": 1470
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
X-Traza-Id: 5155f84e-b35b-4d4c-b8ac-f1c4ce1e5110
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
  "operacion_uuid": "ed082639-0574-4a7c-8328-9513c8f4fc9c"
}
```

**Respuesta.** HTTP 409 (esperado 409) · 73 ms · traza `5155f84e-b35b-4d4c-b8ac-f1c4ce1e5110`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "En el microhub de origen hay 12 disponibles y se piden 1014.",
    "traza_id": "5155f84e-b35b-4d4c-b8ac-f1c4ce1e5110"
  }
}
```

### INV-14 · Apartar existencia · PASA

**Objetivo.** Una reserva resta de lo disponible sin tocar la existencia física.

**Petición.** `POST http://inventario:5111/api/v1/inventario/reservas`

```http
Accept: application/json
X-Traza-Id: 3b36e46e-d39e-4355-a848-6c18ed540518
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
    "id": "evidencia-7e6953"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 68 ms · traza `3b36e46e-d39e-4355-a848-6c18ed540518`

```json
{
  "id": 9,
  "microhub_id": 1,
  "producto_id": 8,
  "cantidad": 3,
  "estado": "activa",
  "vigente": true,
  "referencia": {
    "tipo": "manual",
    "id": "evidencia-7e6953"
  },
  "creada_en": "2026-10-20T00:43:15-06:00",
  "vence_en": "2026-10-20T01:13:15-06:00",
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
X-Traza-Id: be87093a-4b95-45d1-9eea-fd4464276152
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
    "id": "evidencia-7e6953"
  }
}
```

**Respuesta.** HTTP 409 (esperado 409) · 80 ms · traza `be87093a-4b95-45d1-9eea-fd4464276152`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "No hay existencia disponible: hay 18 sin apartar y se piden 121.",
    "traza_id": "be87093a-4b95-45d1-9eea-fd4464276152"
  }
}
```

### INV-16 · Reservas activas · PASA

**Objetivo.** Filtro por producto, estado y referencia.

**Petición.** `GET http://inventario:5111/api/v1/inventario/reservas?producto_id=8&estado=activa&referencia_id=evidencia-7e6953`

```http
Accept: application/json
X-Traza-Id: 734f2f83-c5f7-4529-a3b7-bdbfd5cdbee9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 89 ms · traza `734f2f83-c5f7-4529-a3b7-bdbfd5cdbee9`

```json
{
  "datos": [
    {
      "id": 9,
      "microhub_id": 1,
      "producto_id": 8,
      "cantidad": 3,
      "estado": "activa",
      "vigente": true,
      "referencia": {
        "tipo": "manual",
        "id": "evidencia-7e6953"
      },
      "creada_en": "2026-10-20T00:43:15-06:00",
      "vence_en": "2026-10-20T01:13:15-06:00",
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

**Petición.** `POST http://inventario:5111/api/v1/inventario/reservas/9/liberar`

```http
Accept: application/json
X-Traza-Id: ed1f125b-b363-4226-926a-cba6cad2f723
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 47 ms · traza `ed1f125b-b363-4226-926a-cba6cad2f723`

```json
{
  "id": 9,
  "microhub_id": 1,
  "producto_id": 8,
  "cantidad": 3,
  "estado": "liberada",
  "vigente": false,
  "referencia": {
    "tipo": "manual",
    "id": "evidencia-7e6953"
  },
  "creada_en": "2026-10-20T00:43:15-06:00",
  "vence_en": "2026-10-20T01:13:15-06:00",
  "cerrada_en": "2026-10-20T00:43:15-06:00"
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
X-Traza-Id: 0d8cee7c-e708-41ca-8691-46a1d21deb0c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "minimo": 41
}
```

**Respuesta.** HTTP 200 (esperado 200) · 66 ms · traza `0d8cee7c-e708-41ca-8691-46a1d21deb0c`

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
  "actualizado_en": "2026-10-20T00:43:16-06:00"
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
X-Traza-Id: 79b002e8-c6d2-40cb-84d2-91ba0fbbb7f4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "minimo": 41
}
```

**Respuesta.** HTTP 200 (esperado 200) · 73 ms · traza `79b002e8-c6d2-40cb-84d2-91ba0fbbb7f4`

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
  "actualizado_en": "2026-10-20T00:43:16-06:00"
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
      "actualizado_en": "2026-10-20T06:43:16.184834+00:00"
    }
  }
]
```

### INV-19 · El operador intenta cambiar el mínimo · PASA

**Objetivo.** Sin inventario.ajuste.

**Petición.** `PATCH http://inventario:5111/api/v1/inventario/1/9/minimo`

```http
Accept: application/json
X-Traza-Id: 4083d534-b1bd-4aa9-ad90-a05ff9da1236
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "minimo": 1
}
```

**Respuesta.** HTTP 403 (esperado 403) · 40 ms · traza `4083d534-b1bd-4aa9-ad90-a05ff9da1236`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "4083d534-b1bd-4aa9-ad90-a05ff9da1236"
  }
}
```

### INV-20 · Una merma cruza el mínimo · PASA

**Objetivo.** El trigger avisa del faltante al operador y al administrador.

**Petición.** `POST http://inventario:5111/api/v1/inventario/movimientos`

```http
Accept: application/json
X-Traza-Id: 645b05e8-6d60-416c-93e6-3e2e1de8852d
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

**Respuesta.** HTTP 201 (esperado 201) · 93 ms · traza `645b05e8-6d60-416c-93e6-3e2e1de8852d`

```json
{
  "movimiento": {
    "id": 1473,
    "microhub_id": 1,
    "producto_id": 9,
    "tipo": "merma",
    "cantidad": -2,
    "existencia_resultante": 40,
    "referencia": null,
    "motivo": "Se rompieron dos",
    "usuario_id": 1,
    "fecha": "2026-10-20T00:43:16-06:00"
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
X-Traza-Id: ec5a607b-d55f-42f3-837c-028790028564
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 81 ms · traza `ec5a607b-d55f-42f3-837c-028790028564`

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
X-Traza-Id: 12871e61-054e-4245-b019-ae1d84e2fce4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 52 ms · traza `12871e61-054e-4245-b019-ae1d84e2fce4`

```json
{
  "datos": [
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
    "total": 11,
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
X-Traza-Id: 4be1ffa0-ef96-4116-8326-279f10efee08
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "rol": "operador",
  "microhub_id": 1,
  "tipo": "sistema",
  "titulo": "Evidencia 2db176",
  "mensaje": "Aviso de prueba para el microhub 1",
  "referencia": {
    "tipo": "sistema",
    "id": "evidencia"
  }
}
```

**Respuesta.** HTTP 201 (esperado 201) · 60 ms · traza `4be1ffa0-ef96-4116-8326-279f10efee08`

```json
{
  "enviadas": 1,
  "omitidas": 0,
  "ids": [
    328
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
    "titulo": "Evidencia 2db176",
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
X-Traza-Id: 6a39c374-5ad0-48c9-91e9-aedef100537e
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

**Respuesta.** HTTP 403 (esperado 403) · 33 ms · traza `6a39c374-5ad0-48c9-91e9-aedef100537e`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "6a39c374-5ad0-48c9-91e9-aedef100537e"
  }
}
```

### NOT-03 · Destino inexistente · PASA

**Objetivo.** Un rol sin personas activas se rechaza.

**Petición.** `POST http://notificaciones:5124/api/v1/notificaciones`

```http
Accept: application/json
X-Traza-Id: bb34b2ff-a770-42e9-be48-a18ad52860f1
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

**Respuesta.** HTTP 422 (esperado 422) · 37 ms · traza `bb34b2ff-a770-42e9-be48-a18ad52860f1`

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
    "traza_id": "bb34b2ff-a770-42e9-be48-a18ad52860f1"
  }
}
```

### NOT-04 · Mi bandeja · PASA

**Objetivo.** Los avisos de la persona, el más reciente primero.

**Petición.** `GET http://notificaciones:5124/api/v1/notificaciones?solo_no_leidas=true&por_pagina=20`

```http
Accept: application/json
X-Traza-Id: 0e035b92-0be6-4410-a022-7baeaa92dda2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 49 ms · traza `0e035b92-0be6-4410-a022-7baeaa92dda2`

```json
{
  "datos": [
    {
      "id": 328,
      "tipo": "sistema",
      "titulo": "Evidencia 2db176",
      "mensaje": "Aviso de prueba para el microhub 1",
      "leida": false,
      "referencia": {
        "tipo": "sistema",
        "id": "evidencia"
      },
      "creada_en": "2026-10-20T00:43:16-06:00"
    },
    {
      "id": 326,
      "tipo": "inventario",
      "titulo": "Faltante en Microhub San Bernabé Centro",
      "mensaje": "Atún en agua: quedan 40 (mínimo 41).",
      "leida": false,
      "referencia": {
        "tipo": "producto",
        "id": "9"
      },
      "creada_en": "2026-10-20T00:43:16-06:00"
    },
    {
      "id": 308,
      "tipo": "abastecimiento",
      "titulo": "Orden de compra OC-20261020-000017",
      "mensaje": "La orden quedó cancelada.",
      "leida": false,
      "referencia": {
        "tipo": "orden",
        "id": "17"
      },
      "creada_en": "2026-10-20T00:32:37-06:00"
    },
    {
      "id": 307,
      "tipo": "abastecimiento",
      "titulo": "Solicitud de compra SC-20261020-000025",
      "mensaje": "Tu solicitud fue aprobada.",
      "leida": false,
      "referencia": {
        "tipo": "solicitud",
        "id": "25"
      },
      "creada_en": "2026-10-20T00:32:37-06:00"
    },
    {
      "id": 304,
      "tipo": "abastecimiento",
      "titulo": "Orden de compra OC-20261020-000016",
      "mensaje": "La orden quedó recibida.",
      "leida": false,
      "referencia": {
        "tipo": "orden",
        "id": "16"
      },
      "creada_en": "2026-10-20T00:32:36-06:00"
    },
    {
      "id": 303,
      "tipo": "abastecimiento",
      "titulo": "Solicitud de compra SC-20261020-000024",
      "mensaje": "Tu solicitud fue aprobada.",
      "leida": false,
      "referencia": {
        "tipo": "solicitud",
        "id": "24"
      },
      "creada_en": "2026-10-20T00:32:35-06:00"
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
X-Traza-Id: f96e298b-bef2-4825-9611-d2aca64b2f80
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 68 ms · traza `f96e298b-bef2-4825-9611-d2aca64b2f80`

```xml
<?xml version='1.0' encoding='utf-8'?>
<notificaciones xmlns="urn:microhubs:v1" version="1"><datos><notificacion><id>328</id><tipo>sistema</tipo><titulo>Evidencia 2db176</titulo><mensaje>Aviso de prueba para el microhub 1</mensaje><leida>false</leida><referencia><tipo>sistema</tipo><id>evidencia</id></referencia><creada_en>2026-10-20T00:43:16-06:00</creada_en></notificacion><notificacion><id>326</id><tipo>inventario</tipo><titulo>Faltante en Microhub San Bernabé Centro</titulo><mensaje>Atún en agua: quedan 40 (mínimo 41).</mensaje><leida>false</leida><referencia><tipo>producto</tipo><id>9</id></referencia><creada_en>2026-10-20T00:43:16-06:00</creada_en></notificacion><notificacion><id>308</id><tipo>abastecimiento</tipo><titulo>Orden de compra OC-20261020-000017</titulo><mensaje>La orden quedó cancelada.</mensaje><leida>false</leida><referencia><tipo>orden</tipo><id>17</id></referencia><creada_en>2026-10-20T00:32:37-06:00</creada_en></notificacion></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>62</total><paginas>21</paginas></paginacion></notificaciones>
```

### NOT-06 · Avisos sin leer · PASA

**Objetivo.** Conteo para la insignia de la app.

**Petición.** `GET http://notificaciones:5124/api/v1/notificaciones/conteo`

```http
Accept: application/json
X-Traza-Id: ac686484-bfa9-48df-9b18-eac5f4cf9889
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 1270 ms · traza `ac686484-bfa9-48df-9b18-eac5f4cf9889`

```json
{
  "no_leidas": 6
}
```

### NOT-07 · Confirmar la lectura · PASA

**Objetivo.** El aviso queda leído.

**Petición.** `POST http://notificaciones:5124/api/v1/notificaciones/328/leer`

```http
Accept: application/json
X-Traza-Id: 7ddeb788-fc63-4716-81b0-f43f91fb2a05
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 29 ms · traza `7ddeb788-fc63-4716-81b0-f43f91fb2a05`

```json
{
  "id": 328,
  "tipo": "sistema",
  "titulo": "Evidencia 2db176",
  "mensaje": "Aviso de prueba para el microhub 1",
  "leida": true,
  "referencia": {
    "tipo": "sistema",
    "id": "evidencia"
  },
  "creada_en": "2026-10-20T00:43:16-06:00"
}
```

**Evidencia en PostgreSQL.** `SELECT id, leido_en IS NOT NULL AS leido FROM web_notificacion WHERE id = %s`

```json
[
  {
    "id": 328,
    "leido": true
  }
]
```

### NOT-08 · Leído por otra persona · PASA

**Objetivo.** Un aviso ajeno no se puede marcar.

**Petición.** `POST http://notificaciones:5124/api/v1/notificaciones/328/leer`

```http
Accept: application/json
X-Traza-Id: 056eb81a-8d33-4f7a-be9c-ebe9295704a4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 28 ms · traza `056eb81a-8d33-4f7a-be9c-ebe9295704a4`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe ese aviso en tu bandeja.",
    "traza_id": "056eb81a-8d33-4f7a-be9c-ebe9295704a4"
  }
}
```

### NOT-09 · Marcar todos como leídos · PASA

**Objetivo.** Confirma la lectura de todos los pendientes.

**Petición.** `POST http://notificaciones:5124/api/v1/notificaciones/leer-todas`

```http
Accept: application/json
X-Traza-Id: 2a6fd96e-96c9-4810-88c9-27be3ef03b80
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 35 ms · traza `2a6fd96e-96c9-4810-88c9-27be3ef03b80`

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
X-Traza-Id: 38b56b28-191d-43f7-98f8-4d0543b544ad
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 24 ms · traza `38b56b28-191d-43f7-98f8-4d0543b544ad`

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
X-Traza-Id: d68edbe5-a7b9-4690-8788-17e4124933fc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "activa": false
}
```

**Respuesta.** HTTP 200 (esperado 200) · 38 ms · traza `d68edbe5-a7b9-4690-8788-17e4124933fc`

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
X-Traza-Id: fea34f59-164b-4c0c-b45e-d4ffa562f6eb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "rol": "operador",
  "microhub_id": 1,
  "tipo": "inventario",
  "titulo": "Evidencia 2db176",
  "mensaje": "Faltante de prueba"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 38 ms · traza `fea34f59-164b-4c0c-b45e-d4ffa562f6eb`

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
X-Traza-Id: 031862e3-f159-4416-ae91-cd301ef806ac
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "activa": false
}
```

**Respuesta.** HTTP 409 (esperado 409) · 6 ms · traza `031862e3-f159-4416-ae91-cd301ef806ac`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Los avisos del sistema no se pueden apagar.",
    "traza_id": "031862e3-f159-4416-ae91-cd301ef806ac"
  }
}
```

### NOT-14 · Borrar un aviso · PASA

**Objetivo.** Quita el aviso de la bandeja propia.

**Petición.** `DELETE http://notificaciones:5124/api/v1/notificaciones/328`

```http
Accept: application/json
X-Traza-Id: 1befa1c0-011c-4333-91fc-7109c5e72eb4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 28 ms · traza `1befa1c0-011c-4333-91fc-7109c5e72eb4`

```json
(sin cuerpo)
```

## Servicio proveedores · puerto 5113

### PRV-01 · Proveedores · PASA

**Objetivo.** Lista con cobertura y calificación.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores?por_pagina=10`

```http
Accept: application/json
X-Traza-Id: bd00e672-6f91-4223-9974-fe546a86666d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 61 ms · traza `bd00e672-6f91-4223-9974-fe546a86666d`

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
X-Traza-Id: d7089cf6-2286-40e9-8d00-6eb642bd5f74
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 51 ms · traza `d7089cf6-2286-40e9-8d00-6eb642bd5f74`

```xml
<?xml version='1.0' encoding='utf-8'?>
<proveedores xmlns="urn:microhubs:v1" version="1"><datos><proveedor><id>1</id><clave>PV-01</clave><nombre>Abarrotes del Norte</nombre><contacto>Rosa Garza</contacto><correo>ventas@abarrotesdelnorte.example</correo><telefono>8181000101</telefono><dias_entrega>2</dias_entrega><pedido_minimo>800.00</pedido_minimo><condiciones_pago>Contado</condiciones_pago><estatus>activo</estatus><zonas><zona_id>1</zona_id><zona_id>2</zona_id><zona_id>3</zona_id><zona_id>4</zona_id></zonas><calificacion>4</calificacion><evaluaciones>1</evaluaciones></proveedor><proveedor><id>2</id><clave>PV-02</clave><nombre>Distribuidora Regia</nombre><contacto>Luis Treviño</contacto><correo>pedidos@distregia.example</correo><telefono>8181000102</telefono><dias_entrega>1</dias_entrega><pedido_minimo>500.00</pedido_minimo><condiciones_pago>Crédito a 7 días</condiciones_pago><estatus>activo</estatus><zonas><zona_id>1</zona_id><zona_id>2</zona_id><zona_id>3</zona_id><zona_id>4</zona_id></zonas><calificacion>4</calificacion><evaluaciones>1</evaluaciones></proveedor><proveedor><id>3</id><clave>PV-03</clave><nombre>Mayorista San Nicolás</nombre><contacto>Elena Cantú</contacto><correo>compras@mayoristasn.example</correo><telefono>8181000103</telefono><dias_entrega>4</dias_entrega><pedido_minimo>1500.00</pedido_minimo><condiciones_pago>Crédito a 15 días</condiciones_pago><estatus>activo</estatus><zonas><zona_id>1</zona_id><zona_id>2</zona_id><zona_id>3</zona_id><zona_id>4</zona_id></zonas><calificacion>4</calificacion><evaluaciones>1</evaluaciones></proveedor></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>3</total><paginas>1</paginas></paginacion></proveedores>
```

### PRV-03 · Un cliente intenta ver proveedores · PASA

**Objetivo.** El perfil cliente no tiene proveedores.ver.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores`

```http
Accept: application/json
X-Traza-Id: b5016d02-afbe-4fa9-a948-3485372077af
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 27 ms · traza `b5016d02-afbe-4fa9-a948-3485372077af`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "b5016d02-afbe-4fa9-a948-3485372077af"
  }
}
```

### PRV-04 · Un proveedor · PASA

**Objetivo.** Con las zonas que cubre y su calificación.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/2`

```http
Accept: application/json
X-Traza-Id: 1f046583-df65-472e-80ad-5cc488131346
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 30 ms · traza `1f046583-df65-472e-80ad-5cc488131346`

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
X-Traza-Id: 20ac379c-a67a-47c5-ba05-2e605db30d0d
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

**Respuesta.** HTTP 201 (esperado 201) · 91 ms · traza `20ac379c-a67a-47c5-ba05-2e605db30d0d`

```json
{
  "id": 42,
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
    "id": 42,
    "clave": "EV-C81E52",
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
X-Traza-Id: 04afb9f3-0d6f-4d2c-ab50-838893b7b626
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

**Respuesta.** HTTP 409 (esperado 409) · 26 ms · traza `04afb9f3-0d6f-4d2c-ab50-838893b7b626`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Ya existe un proveedor con la clave EV-C81E52.",
    "traza_id": "04afb9f3-0d6f-4d2c-ab50-838893b7b626"
  }
}
```

### PRV-07 · Correo inválido · PASA

**Objetivo.** Validación con detalle por campo.

**Petición.** `POST http://proveedores:5113/api/v1/proveedores`

```http
Accept: application/json
X-Traza-Id: 653a0978-6606-4e4f-9d15-32a36e1d4653
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

**Respuesta.** HTTP 422 (esperado 422) · 7 ms · traza `653a0978-6606-4e4f-9d15-32a36e1d4653`

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
    "traza_id": "653a0978-6606-4e4f-9d15-32a36e1d4653"
  }
}
```

### PRV-08 · Un planeador intenta dar de alta · PASA

**Objetivo.** Sin proveedores.editar.

**Petición.** `POST http://proveedores:5113/api/v1/proveedores`

```http
Accept: application/json
X-Traza-Id: d910bf02-0ce1-446f-8dc6-5fd4c60b9cff
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

**Respuesta.** HTTP 403 (esperado 403) · 28 ms · traza `d910bf02-0ce1-446f-8dc6-5fd4c60b9cff`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "d910bf02-0ce1-446f-8dc6-5fd4c60b9cff"
  }
}
```

### PRV-09 · Modificar un proveedor · PASA

**Objetivo.** Cambia el plazo y la cobertura; la clave no se toca.

**Petición.** `PUT http://proveedores:5113/api/v1/proveedores/42`

```http
Accept: application/json
X-Traza-Id: ed8311b6-87b2-4851-8a6a-13c3d3159bc1
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

**Respuesta.** HTTP 200 (esperado 200) · 88 ms · traza `ed8311b6-87b2-4851-8a6a-13c3d3159bc1`

```json
{
  "id": 42,
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

**Petición.** `PATCH http://proveedores:5113/api/v1/proveedores/42`

```http
Accept: application/json
X-Traza-Id: 07c0ae47-b171-4e65-837f-0c1e9541e36a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "contacto": "Luis Prueba"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 105 ms · traza `07c0ae47-b171-4e65-837f-0c1e9541e36a`

```json
{
  "id": 42,
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
    "clave": "EV-C81E52",
    "contacto": "Luis Prueba",
    "dias_entrega": 5
  }
]
```

### PRV-10 · Fijar una oferta · PASA

**Objetivo.** Alta del precio de compra de un producto.

**Petición.** `PUT http://proveedores:5113/api/v1/proveedores/42/catalogo/6`

```http
Accept: application/json
X-Traza-Id: 4f077586-3dc6-49f1-9b59-08896d34895a
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

**Respuesta.** HTTP 200 (esperado 200) · 65 ms · traza `4f077586-3dc6-49f1-9b59-08896d34895a`

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
    "proveedor_id": 42,
    "producto_id": 6,
    "precio_compra": "0.05",
    "capacidad_semanal": 100,
    "minimo_compra": 5
  }
]
```

### PRV-11 · Producto inexistente en la oferta · PASA

**Objetivo.** La llave foránea rechaza el producto.

**Petición.** `PUT http://proveedores:5113/api/v1/proveedores/42/catalogo/999999`

```http
Accept: application/json
X-Traza-Id: 9569627f-ad53-46cc-b754-b9cb484fa338
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "precio_compra": 1,
  "capacidad_semanal": 10
}
```

**Respuesta.** HTTP 422 (esperado 422) · 51 ms · traza `9569627f-ad53-46cc-b754-b9cb484fa338`

```json
{
  "error": {
    "codigo": "REGLA_NEGOCIO",
    "mensaje": "El producto no existe.",
    "traza_id": "9569627f-ad53-46cc-b754-b9cb484fa338"
  }
}
```

### PRV-12 · Catálogo del proveedor · PASA

**Objetivo.** Sus ofertas, con el nombre del producto.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/42/catalogo`

```http
Accept: application/json
X-Traza-Id: 57b84a12-5b2f-450f-8c29-4202ae505c0c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 74 ms · traza `57b84a12-5b2f-450f-8c29-4202ae505c0c`

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

**Petición.** `POST http://proveedores:5113/api/v1/proveedores/42/evaluaciones`

```http
Accept: application/json
X-Traza-Id: 60cf61f6-9c8f-4461-a1d0-a6b56942ade0
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

**Respuesta.** HTTP 201 (esperado 201) · 79 ms · traza `60cf61f6-9c8f-4461-a1d0-a6b56942ade0`

```json
{
  "id": 13,
  "proveedor_id": 42,
  "puntualidad": 5,
  "calidad": 4,
  "precio": 3,
  "comentario": "Llegó a tiempo",
  "evaluado_por": 2,
  "evaluado_en": "2026-10-20T00:43:19-06:00"
}
```

**Evidencia en PostgreSQL.** `SELECT proveedor_id, puntualidad, calidad, precio, evaluado_por FROM proveedor_evaluacion WHERE proveedor_id = %s`

```json
[
  {
    "proveedor_id": 42,
    "puntualidad": 5,
    "calidad": 4,
    "precio": 3,
    "evaluado_por": 2
  }
]
```

### PRV-14 · Evaluaciones y promedio · PASA

**Objetivo.** Calificaciones recibidas y su promedio.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/42/evaluaciones`

```http
Accept: application/json
X-Traza-Id: 345cef91-281b-4d65-b8fe-c4b10d97ed36
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 71 ms · traza `345cef91-281b-4d65-b8fe-c4b10d97ed36`

```json
{
  "datos": [
    {
      "id": 13,
      "proveedor_id": 42,
      "puntualidad": 5,
      "calidad": 4,
      "precio": 3,
      "comentario": "Llegó a tiempo",
      "evaluado_por": 2,
      "evaluado_en": "2026-10-20T00:43:19-06:00"
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

**Petición.** `POST http://proveedores:5113/api/v1/proveedores/42/evaluaciones`

```http
Accept: application/json
X-Traza-Id: 27a83391-71c4-463c-8d98-c1cf13320786
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

**Respuesta.** HTTP 403 (esperado 403) · 37 ms · traza `27a83391-71c4-463c-8d98-c1cf13320786`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "27a83391-71c4-463c-8d98-c1cf13320786"
  }
}
```

### PRV-16 · Ofertas de un producto · PASA

**Objetivo.** De la más barata a la más cara.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/ofertas?producto_id=6`

```http
Accept: application/json
X-Traza-Id: 0bbfa28d-4eaf-4116-ac49-93809530c444
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 71 ms · traza `0bbfa28d-4eaf-4116-ac49-93809530c444`

```json
{
  "datos": [
    {
      "proveedor": {
        "id": 42,
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
X-Traza-Id: 61e29da6-c255-48ce-9ce2-5d18516a93fc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 68 ms · traza `61e29da6-c255-48ce-9ce2-5d18516a93fc`

```json
{
  "datos": [
    {
      "proveedor": {
        "id": 42,
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
X-Traza-Id: a85fc5c4-7fa0-4f37-a2dd-92275aa29250
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 7 ms · traza `a85fc5c4-7fa0-4f37-a2dd-92275aa29250`

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
    "traza_id": "a85fc5c4-7fa0-4f37-a2dd-92275aa29250"
  }
}
```

### PRV-19 · Dar de baja un proveedor · PASA

**Objetivo.** Baja lógica: ya no aparece en las ofertas.

**Petición.** `DELETE http://proveedores:5113/api/v1/proveedores/42`

```http
Accept: application/json
X-Traza-Id: 665e56b8-cb4d-427a-a672-9e7193668159
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 36 ms · traza `665e56b8-cb4d-427a-a672-9e7193668159`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT clave, estatus FROM proveedor WHERE id = %s`

```json
[
  {
    "clave": "EV-C81E52",
    "estatus": "inactivo"
  }
]
```

### PRV-20 · Ofertas sin el proveedor de baja · PASA

**Objetivo.** El proveedor dado de baja no ofrece.

**Petición.** `GET http://proveedores:5113/api/v1/proveedores/ofertas?producto_id=6`

```http
Accept: application/json
X-Traza-Id: a7376bc6-3e5f-4f45-84c4-c469c5fe72f4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 77 ms · traza `a7376bc6-3e5f-4f45-84c4-c469c5fe72f4`

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
X-Traza-Id: d360e464-ca00-4ad9-be58-6d1a939d89f4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 56 ms · traza `d360e464-ca00-4ad9-be58-6d1a939d89f4`

```json
{
  "datos": [
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
    "total": 8,
    "paginas": 1
  }
}
```

### PRE-02 · Listas (XML) · PASA

**Objetivo.** Respuesta XML que cumple precios.xsd.

**Petición.** `GET http://precios:5112/api/v1/precios/listas`

```http
Accept: application/xml
X-Traza-Id: 5cdab95e-481e-46c3-ab8e-b260f66a8049
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 46 ms · traza `5cdab95e-481e-46c3-ab8e-b260f66a8049`

```xml
<?xml version='1.0' encoding='utf-8'?>
<listas xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><datos><lista><id>17</id><nombre>Lista de evidencias 4ccd1c</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>16</id><nombre>Lista de evidencias 6ddeea</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>15</id><nombre>Lista de evidencias 962abe</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>14</id><nombre>Lista de evidencias fa981b</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>11</id><nombre>Lista de prueba a8dad7c8</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>4</id><nombre>Lista de prueba 8a4e607d</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>3</id><nombre>Lista de evidencias 0c58f9</nombre><zona_id>3</zona_id><vigente_desde>2027-01-01</vigente_desde><vigente_hasta>2027-01-31</vigente_hasta><estatus>inactivo</estatus><productos>1</productos></lista><lista><id>1</id><nombre>Lista San Bernabé Centro</nombre><zona_id>1</zona_id><vigente_desde>2026-10-19</vigente_desde><vigente_hasta xsi:nil="true" /><estatus>activo</estatus><productos>20</productos></lista></datos><paginacion><pagina>1</pagina><por_pagina>20</por_pagina><total>8</total><paginas>1</paginas></paginacion></listas>
```

### PRE-03 · Un cliente intenta ver las listas · PASA

**Objetivo.** Sin precios.ver.

**Petición.** `GET http://precios:5112/api/v1/precios/listas`

```http
Accept: application/json
X-Traza-Id: c8936108-f702-46eb-87b8-6f9ac1060c81
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 37 ms · traza `c8936108-f702-46eb-87b8-6f9ac1060c81`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "c8936108-f702-46eb-87b8-6f9ac1060c81"
  }
}
```

### PRE-04 · Crear una lista · PASA

**Objetivo.** Lista de una zona con un precio y su costo.

**Petición.** `POST http://precios:5112/api/v1/precios/listas`

```http
Accept: application/json
X-Traza-Id: 1a5605bf-cc2b-4bd7-ae00-368b46718567
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Lista de evidencias dba9cd",
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

**Respuesta.** HTTP 201 (esperado 201) · 92 ms · traza `1a5605bf-cc2b-4bd7-ae00-368b46718567`

```json
{
  "id": 20,
  "nombre": "Lista de evidencias dba9cd",
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
      "actualizado_en": "2026-10-20T00:43:20-06:00"
    }
  ]
}
```

**Explicación.** Margen = (precio − costo) / precio = (50 − 30) / 50 = 40 %.

**Evidencia en PostgreSQL.** `SELECT l.id, l.nombre, l.zona_id, l.vigente_desde, l.vigente_hasta, i.producto_id, i.precio, i.costo FROM lista_precio l JOIN lista_precio_item i ON i.lista_id = l.id WHERE l.nombre = %s`

```json
[
  {
    "id": 20,
    "nombre": "Lista de evidencias dba9cd",
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
X-Traza-Id: 517f66be-ed89-4b56-b1c1-85e62a51ceb4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Lista de evidencias dba9cd bis",
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

**Respuesta.** HTTP 409 (esperado 409) · 29 ms · traza `517f66be-ed89-4b56-b1c1-85e62a51ceb4`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "La lista «Lista de evidencias dba9cd» ya rige en esa zona durante esas fechas.",
    "traza_id": "517f66be-ed89-4b56-b1c1-85e62a51ceb4"
  }
}
```

### PRE-06 · Cambiar el precio de un producto · PASA

**Objetivo.** Sube el precio de 50 a 52; el costo se conserva.

**Petición.** `PUT http://precios:5112/api/v1/precios/listas/20/items/2`

```http
Accept: application/json
X-Traza-Id: 04820bd0-37b1-45b9-9c8b-a7161c294b41
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "precio": 52.0
}
```

**Respuesta.** HTTP 200 (esperado 200) · 44 ms · traza `04820bd0-37b1-45b9-9c8b-a7161c294b41`

```json
{
  "producto": {
    "id": 2,
    "nombre": "Arroz superextra"
  },
  "precio": 52.0,
  "costo": 30.0,
  "margen_pct": 42.3,
  "actualizado_en": "2026-10-20T00:43:20-06:00"
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

**Petición.** `GET http://precios:5112/api/v1/precios/historial?lista_id=20&producto_id=2`

```http
Accept: application/json
X-Traza-Id: 3a94dd98-2e91-4060-bbed-c65f49c13aa9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 47 ms · traza `3a94dd98-2e91-4060-bbed-c65f49c13aa9`

```json
{
  "datos": [
    {
      "id": 36,
      "lista_id": 20,
      "producto_id": 2,
      "precio_anterior": 50.0,
      "precio_nuevo": 52.0,
      "usuario_id": 1,
      "fecha": "2026-10-20T00:43:20-06:00"
    },
    {
      "id": 35,
      "lista_id": 20,
      "producto_id": 2,
      "precio_anterior": null,
      "precio_nuevo": 50.0,
      "usuario_id": 1,
      "fecha": "2026-10-20T00:43:20-06:00"
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

**Petición.** `GET http://precios:5112/api/v1/precios/listas/20`

```http
Accept: application/json
X-Traza-Id: a19c363c-a6d2-4849-ad69-b5c954e5f472
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 45 ms · traza `a19c363c-a6d2-4849-ad69-b5c954e5f472`

```json
{
  "id": 20,
  "nombre": "Lista de evidencias dba9cd",
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
      "actualizado_en": "2026-10-20T00:43:20-06:00"
    }
  ]
}
```

### PRE-09 · Precio dentro de la vigencia · PASA

**Objetivo.** Rige el precio de la lista de la zona.

**Petición.** `GET http://precios:5112/api/v1/precios/vigente?producto_id=2&zona_id=3&fecha=2027-01-15`

```http
Accept: application/json
X-Traza-Id: bd7c2c38-4ee6-4355-ab5a-060fbad1cc14
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 97 ms · traza `bd7c2c38-4ee6-4355-ab5a-060fbad1cc14`

```json
{
  "producto_id": 2,
  "zona_id": 3,
  "fecha": "2027-01-15",
  "precio_base": 29.9,
  "lista": {
    "id": 20,
    "nombre": "Lista de evidencias dba9cd"
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
X-Traza-Id: 43cf5243-7f20-4b1c-ad70-c07cd9181248
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 103 ms · traza `43cf5243-7f20-4b1c-ad70-c07cd9181248`

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
X-Traza-Id: b7a44e41-943c-4f1a-9798-164b1fd4fcc1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 113 ms · traza `b7a44e41-943c-4f1a-9798-164b1fd4fcc1`

```json
{
  "producto_id": 1,
  "zona_id": 1,
  "fecha": "2026-10-20",
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
X-Traza-Id: f21a665d-302b-4656-a945-2187cafb4160
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 98 ms · traza `f21a665d-302b-4656-a945-2187cafb4160`

```json
{
  "producto_id": 21,
  "zona_id": 1,
  "fecha": "2026-10-20",
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
X-Traza-Id: 9b60c2c7-4f5e-41a3-ab26-b5f9e19c400f
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

**Respuesta.** HTTP 200 (esperado 200) · 104 ms · traza `9b60c2c7-4f5e-41a3-ab26-b5f9e19c400f`

```json
{
  "zona_id": 1,
  "fecha": "2026-10-20",
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
X-Traza-Id: 69fcb8fa-1cb0-4439-ae90-bf8ebe7b40a9
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

**Respuesta.** HTTP 422 (esperado 422) · 8 ms · traza `69fcb8fa-1cb0-4439-ae90-bf8ebe7b40a9`

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
    "traza_id": "69fcb8fa-1cb0-4439-ae90-bf8ebe7b40a9"
  }
}
```

### PRE-15 · Promoción que pasa del descuento máximo · PASA

**Objetivo.** Un porcentaje mayor al tope de la configuración se rechaza.

**Petición.** `POST http://precios:5112/api/v1/precios/promociones`

```http
Accept: application/json
X-Traza-Id: f226f877-774a-46e3-b528-c5fff23188ea
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

**Respuesta.** HTTP 422 (esperado 422) · 32 ms · traza `f226f877-774a-46e3-b528-c5fff23188ea`

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
    "traza_id": "f226f877-774a-46e3-b528-c5fff23188ea"
  }
}
```

### PRE-16 · Crear una promoción · PASA

**Objetivo.** Descuento de $2 en un producto.

**Petición.** `POST http://precios:5112/api/v1/precios/promociones`

```http
Accept: application/json
X-Traza-Id: af480abc-46b2-4c20-9336-b16276ed6fc0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Promoción de evidencias e5eb",
  "tipo": "monto",
  "valor": 2.0,
  "producto_id": 1,
  "vigente_hasta": "2030-12-31"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 84 ms · traza `af480abc-46b2-4c20-9336-b16276ed6fc0`

```json
{
  "id": 9,
  "nombre": "Promoción de evidencias e5eb",
  "tipo": "monto",
  "valor": 2.0,
  "producto_id": 1,
  "categoria_id": null,
  "zona_id": null,
  "vigente_desde": "2026-10-20",
  "vigente_hasta": "2030-12-31",
  "estatus": "activo"
}
```

**Evidencia en PostgreSQL.** `SELECT id, nombre, tipo, valor, producto_id, vigente_hasta, estatus FROM promocion WHERE id = %s`

```json
[
  {
    "id": 9,
    "nombre": "Promoción de evidencias e5eb",
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
X-Traza-Id: bd14a7a1-caba-42f8-af01-ef80b436d5ef
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 49 ms · traza `bd14a7a1-caba-42f8-af01-ef80b436d5ef`

```json
{
  "datos": [
    {
      "id": 9,
      "nombre": "Promoción de evidencias e5eb",
      "tipo": "monto",
      "valor": 2.0,
      "producto_id": 1,
      "categoria_id": null,
      "zona_id": null,
      "vigente_desde": "2026-10-20",
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

**Petición.** `DELETE http://precios:5112/api/v1/precios/promociones/9`

```http
Accept: application/json
X-Traza-Id: a31b090b-6239-4ec7-8c00-53896bbd83f1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 44 ms · traza `a31b090b-6239-4ec7-8c00-53896bbd83f1`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT id, estatus FROM promocion WHERE id = %s`

```json
[
  {
    "id": 9,
    "estatus": "inactivo"
  }
]
```

### PRE-19 · Márgenes · PASA

**Objetivo.** Renglones con costo, del margen más bajo al más alto.

**Petición.** `GET http://precios:5112/api/v1/precios/margenes?por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 6d414bed-0267-4c5e-aaeb-1ac062a9e31d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 79 ms · traza `6d414bed-0267-4c5e-aaeb-1ac062a9e31d`

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
X-Traza-Id: 8294c29c-ff5a-4bff-8cdc-73247eb6ee81
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 119 ms · traza `8294c29c-ff5a-4bff-8cdc-73247eb6ee81`

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
X-Traza-Id: c5557ed5-8359-4a32-ad2a-d72b13ada395
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 7 ms · traza `c5557ed5-8359-4a32-ad2a-d72b13ada395`

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
    "traza_id": "c5557ed5-8359-4a32-ad2a-d72b13ada395"
  }
}
```

## Servicio abastecimiento · puerto 5114

### ABA-01 · Necesidades de reposición · PASA

**Objetivo.** Productos bajo su mínimo, con la mejor oferta.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/necesidades?por_pagina=100`

```http
Accept: application/json
X-Traza-Id: 1cd52d4d-af78-4bec-84d9-c02cdba96e10
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 261 ms · traza `1cd52d4d-af78-4bec-84d9-c02cdba96e10`

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
X-Traza-Id: 70a69d5c-5ccd-43cb-a5ed-feab52a28eb4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 8 ms · traza `70a69d5c-5ccd-43cb-a5ed-feab52a28eb4`

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
    "traza_id": "70a69d5c-5ccd-43cb-a5ed-feab52a28eb4"
  }
}
```

### ABA-03 · Pedir mercancía · PASA

**Objetivo.** El operador pide reposición de su microhub.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: 0beb3449-c054-4c9e-a40e-6f76623fbc91
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

**Respuesta.** HTTP 201 (esperado 201) · 87 ms · traza `0beb3449-c054-4c9e-a40e-6f76623fbc91`

```json
{
  "id": 26,
  "folio": "SC-20261020-000026",
  "microhub_id": 1,
  "estado": "pendiente",
  "motivo": "Se acabó el producto el fin de semana",
  "solicitada_por": 2,
  "decidida_por": null,
  "decision_motivo": null,
  "decidida_en": null,
  "creada_en": "2026-10-20T00:43:22-06:00",
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
    "id": 26,
    "folio": "SC-20261020-000026",
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
    "titulo": "Solicitud de compra SC-20261020-000026",
    "referencia_tipo": "solicitud"
  }
]
```

### ABA-04 · Pedir para otro microhub · PASA

**Objetivo.** El operador solo trabaja con el suyo.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: b5c32ae1-076c-462d-9ec6-c5e04af41fe4
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

**Respuesta.** HTTP 403 (esperado 403) · 18 ms · traza `b5c32ae1-076c-462d-9ec6-c5e04af41fe4`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "b5c32ae1-076c-462d-9ec6-c5e04af41fe4"
  }
}
```

### ABA-05 · Producto repetido en la solicitud · PASA

**Objetivo.** Un producto aparece una sola vez.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: 2753280a-3a2f-47bd-942b-999ee1a99524
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

**Respuesta.** HTTP 422 (esperado 422) · 6 ms · traza `2753280a-3a2f-47bd-942b-999ee1a99524`

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
    "traza_id": "2753280a-3a2f-47bd-942b-999ee1a99524"
  }
}
```

### ABA-06 · Solicitud de otro microhub · PASA

**Objetivo.** Otro operador no la ve.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/26`

```http
Accept: application/json
X-Traza-Id: ce15d5ad-7c32-4332-ac29-987aa6546c40
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 27 ms · traza `ce15d5ad-7c32-4332-ac29-987aa6546c40`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe esa solicitud de compra.",
    "traza_id": "ce15d5ad-7c32-4332-ac29-987aa6546c40"
  }
}
```

### ABA-07 · Aprobar sin permiso · PASA

**Objetivo.** Solo el administrador decide.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/26/decision`

```http
Accept: application/json
X-Traza-Id: b6fe6bcb-196f-4d30-9e5f-491e6fabb69f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aprobada"
}
```

**Respuesta.** HTTP 403 (esperado 403) · 39 ms · traza `b6fe6bcb-196f-4d30-9e5f-491e6fabb69f`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "b6fe6bcb-196f-4d30-9e5f-491e6fabb69f"
  }
}
```

### ABA-08 · Rechazar sin motivo · PASA

**Objetivo.** Rechazar exige el motivo.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/26/decision`

```http
Accept: application/json
X-Traza-Id: 6fba38d0-ebe5-4faf-a799-dfe7404c99f8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "rechazada"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 9 ms · traza `6fba38d0-ebe5-4faf-a799-dfe7404c99f8`

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
    "traza_id": "6fba38d0-ebe5-4faf-a799-dfe7404c99f8"
  }
}
```

### ABA-09 · Ordenar antes de aprobar · PASA

**Objetivo.** Solo se ordena una solicitud aprobada.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/26/ordenar`

```http
Accept: application/json
X-Traza-Id: 81764208-63d6-4431-87e1-f87e4564ece7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "proveedor_id": 1
}
```

**Respuesta.** HTTP 409 (esperado 409) · 44 ms · traza `81764208-63d6-4431-87e1-f87e4564ece7`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Solo se ordena una solicitud aprobada; esta está pendiente.",
    "traza_id": "81764208-63d6-4431-87e1-f87e4564ece7"
  }
}
```

### ABA-10 · Aprobar la solicitud · PASA

**Objetivo.** El administrador aprueba y quien pidió recibe el aviso.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/26/decision`

```http
Accept: application/json
X-Traza-Id: a6dc9a2e-c54e-4cc5-a030-7badbb2996ed
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aprobada",
  "motivo": "Hay presupuesto"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 94 ms · traza `a6dc9a2e-c54e-4cc5-a030-7badbb2996ed`

```json
{
  "id": 26,
  "folio": "SC-20261020-000026",
  "microhub_id": 1,
  "estado": "aprobada",
  "motivo": "Se acabó el producto el fin de semana",
  "solicitada_por": 2,
  "decidida_por": 1,
  "decision_motivo": "Hay presupuesto",
  "decidida_en": "2026-10-20T00:43:22-06:00",
  "creada_en": "2026-10-20T00:43:22-06:00",
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
    "titulo": "Solicitud de compra SC-20261020-000026",
    "mensaje": "Tu solicitud fue aprobada."
  }
]
```

### ABA-11 · Emitir la orden de compra · PASA

**Objetivo.** Cada línea va al proveedor indicado; el total es piezas × precio de compra.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/26/ordenar`

```http
Accept: application/json
X-Traza-Id: 78089b86-a207-43a6-aa7a-5fbcfc77e55f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "proveedor_id": 1
}
```

**Respuesta.** HTTP 201 (esperado 201) · 295 ms · traza `78089b86-a207-43a6-aa7a-5fbcfc77e55f`

```json
{
  "solicitud_id": 26,
  "ordenes": [
    {
      "id": 18,
      "folio": "OC-20261020-000018",
      "solicitud_id": 26,
      "proveedor": {
        "id": 1,
        "nombre": "Abarrotes del Norte"
      },
      "microhub_id": 1,
      "estado": "emitida",
      "fecha_esperada": "2026-10-22",
      "total": 853.3,
      "creada_en": "2026-10-20T00:43:22-06:00",
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
    "id": 18,
    "folio": "OC-20261020-000018",
    "estado": "emitida",
    "fecha_esperada": "2026-10-22",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/26/ordenar`

```http
Accept: application/json
X-Traza-Id: c9db2a3f-13bb-49d5-bb94-f1f8609950fe
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "proveedor_id": 1
}
```

**Respuesta.** HTTP 409 (esperado 409) · 53 ms · traza `c9db2a3f-13bb-49d5-bb94-f1f8609950fe`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Solo se ordena una solicitud aprobada; esta está ordenada.",
    "traza_id": "c9db2a3f-13bb-49d5-bb94-f1f8609950fe"
  }
}
```

### ABA-13 · Recepción parcial · PASA

**Objetivo.** La mercancía que llegó entra al inventario.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/18/recepcion`

```http
Accept: application/json
X-Traza-Id: 79dd1d6a-5332-458c-9852-cb43f6c57af9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "operacion_uuid": "9860dd81-e1e3-459b-95e0-920fd73b8ef2",
  "nota": "Llegó la primera caja",
  "lineas": [
    {
      "producto_id": 10,
      "cantidad": 23
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 285 ms · traza `79dd1d6a-5332-458c-9852-cb43f6c57af9`

```json
{
  "orden": {
    "id": 18,
    "folio": "OC-20261020-000018",
    "solicitud_id": 26,
    "proveedor": {
      "id": 1,
      "nombre": "Abarrotes del Norte"
    },
    "microhub_id": 1,
    "estado": "parcial",
    "fecha_esperada": "2026-10-22",
    "total": 853.3,
    "creada_en": "2026-10-20T00:43:22-06:00",
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
    "operacion_uuid": "9860dd81-e1e3-459b-95e0-920fd73b8ef2:10",
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
    "existencia_resultante": 394,
    "referencia_tipo": "orden_compra",
    "referencia_id": 18
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/18/recepcion`

```http
Accept: application/json
X-Traza-Id: baa2be10-b94b-406d-9431-a0dd9a1596a6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "operacion_uuid": "9860dd81-e1e3-459b-95e0-920fd73b8ef2",
  "nota": "Llegó la primera caja",
  "lineas": [
    {
      "producto_id": 10,
      "cantidad": 23
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 258 ms · traza `baa2be10-b94b-406d-9431-a0dd9a1596a6`

```json
{
  "orden": {
    "id": 18,
    "folio": "OC-20261020-000018",
    "solicitud_id": 26,
    "proveedor": {
      "id": 1,
      "nombre": "Abarrotes del Norte"
    },
    "microhub_id": 1,
    "estado": "parcial",
    "fecha_esperada": "2026-10-22",
    "total": 853.3,
    "creada_en": "2026-10-20T00:43:22-06:00",
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
    "existencia": 394
  }
]
```

### ABA-15 · Recibir más de lo pedido · PASA

**Objetivo.** Solo falta lo que no ha llegado.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/18/recepcion`

```http
Accept: application/json
X-Traza-Id: 4b8db74d-4e65-4053-9a2c-d1031d635a34
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

**Respuesta.** HTTP 422 (esperado 422) · 107 ms · traza `4b8db74d-4e65-4053-9a2c-d1031d635a34`

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
    "traza_id": "4b8db74d-4e65-4053-9a2c-d1031d635a34"
  }
}
```

### ABA-16 · Cancelar una orden con mercancía recibida · PASA

**Objetivo.** Solo se cancela una orden sin recepciones.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/18/cancelar`

```http
Accept: application/json
X-Traza-Id: c47297e5-63c1-4a08-a77c-3d09b729e360
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "motivo": "Ya llegó"
}
```

**Respuesta.** HTTP 409 (esperado 409) · 92 ms · traza `c47297e5-63c1-4a08-a77c-3d09b729e360`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Solo se cancela una orden emitida que todavía no recibió mercancía.",
    "traza_id": "c47297e5-63c1-4a08-a77c-3d09b729e360"
  }
}
```

### ABA-17 · Recepción final · PASA

**Objetivo.** Llega el resto: la orden queda recibida y avisa.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/18/recepcion`

```http
Accept: application/json
X-Traza-Id: eb27fa84-2581-47f0-84a5-a52d91b945d1
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

**Respuesta.** HTTP 201 (esperado 201) · 482 ms · traza `eb27fa84-2581-47f0-84a5-a52d91b945d1`

```json
{
  "orden": {
    "id": 18,
    "folio": "OC-20261020-000018",
    "solicitud_id": 26,
    "proveedor": {
      "id": 1,
      "nombre": "Abarrotes del Norte"
    },
    "microhub_id": 1,
    "estado": "recibida",
    "fecha_esperada": "2026-10-22",
    "total": 853.3,
    "creada_en": "2026-10-20T00:43:22-06:00",
    "cerrada_en": "2026-10-20T00:43:24-06:00",
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
    "existencia": 417
  }
]
```

**Evidencia en PostgreSQL.** `SELECT destinatario_id, titulo, mensaje FROM web_notificacion WHERE referencia_tipo = 'orden' AND referencia_id = %s`

```json
[
  {
    "destinatario_id": 2,
    "titulo": "Orden de compra OC-20261020-000018",
    "mensaje": "La orden quedó recibida."
  },
  {
    "destinatario_id": 1,
    "titulo": "Orden de compra OC-20261020-000018",
    "mensaje": "La orden quedó recibida."
  }
]
```

### ABA-18 · Recibir en una orden ya recibida · PASA

**Objetivo.** Una orden recibida no admite más mercancía.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/18/recepcion`

```http
Accept: application/json
X-Traza-Id: 35995f99-0524-4016-a60d-1936a14e78b3
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

**Respuesta.** HTTP 409 (esperado 409) · 50 ms · traza `35995f99-0524-4016-a60d-1936a14e78b3`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "La orden está recibida; ya no recibe mercancía.",
    "traza_id": "35995f99-0524-4016-a60d-1936a14e78b3"
  }
}
```

### ABA-19 · Una orden · PASA

**Objetivo.** Con lo recibido de cada línea.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/ordenes/18`

```http
Accept: application/json
X-Traza-Id: 787ae74b-1a30-45b1-bc10-71adaaf57e96
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 64 ms · traza `787ae74b-1a30-45b1-bc10-71adaaf57e96`

```json
{
  "id": 18,
  "folio": "OC-20261020-000018",
  "solicitud_id": 26,
  "proveedor": {
    "id": 1,
    "nombre": "Abarrotes del Norte"
  },
  "microhub_id": 1,
  "estado": "recibida",
  "fecha_esperada": "2026-10-22",
  "total": 853.3,
  "creada_en": "2026-10-20T00:43:22-06:00",
  "cerrada_en": "2026-10-20T00:43:24-06:00",
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
X-Traza-Id: b001e457-e384-47b0-baec-32544da06666
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 94 ms · traza `b001e457-e384-47b0-baec-32544da06666`

```xml
<?xml version='1.0' encoding='utf-8'?>
<ordenes xmlns="urn:microhubs:v1" version="1"><datos><orden><id>18</id><folio>OC-20261020-000018</folio><solicitud_id>26</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>853.30</total><creada_en>2026-10-20T00:43:22-06:00</creada_en><cerrada_en>2026-10-20T00:43:24-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>16</id><folio>OC-20261020-000016</folio><solicitud_id>24</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>853.30</total><creada_en>2026-10-20T00:32:35-06:00</creada_en><cerrada_en>2026-10-20T00:32:36-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>14</id><folio>OC-20261020-000014</folio><solicitud_id>22</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>853.30</total><creada_en>2026-10-20T00:29:44-06:00</creada_en><cerrada_en>2026-10-20T00:29:45-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>12</id><folio>OC-20261020-000012</folio><solicitud_id>20</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>853.30</total><creada_en>2026-10-20T00:21:44-06:00</creada_en><cerrada_en>2026-10-20T00:21:45-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>10</id><folio>OC-20261020-000010</folio><solicitud_id>18</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>853.30</total><creada_en>2026-10-20T00:20:38-06:00</creada_en><cerrada_en>2026-10-20T00:20:39-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>9</id><folio>OC-20261020-000009</folio><solicitud_id>16</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>859.95</total><creada_en>2026-10-20T00:16:49-06:00</creada_en><cerrada_en>2026-10-20T00:16:50-06:00</cerrada_en><lineas><linea><producto><id>12</id><nombre>Chiles jalapeños en escabeche</nombre></producto><cantidad>63</cantidad><precio_compra>13.65</precio_compra><cantidad_recibida>63</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>8</id><folio>OC-20261020-000008</folio><solicitud_id>14</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-22</fecha_esperada><total>853.30</total><creada_en>2026-10-20T00:16:46-06:00</creada_en><cerrada_en>2026-10-20T00:16:47-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>6</id><folio>OC-20261020-000006</folio><solicitud_id>10</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-21</fecha_esperada><total>854.70</total><creada_en>2026-10-19T19:33:42-06:00</creada_en><cerrada_en>2026-10-19T19:33:58-06:00</cerrada_en><lineas><linea><producto><id>16</id><nombre>Galletas María</nombre></producto><cantidad>74</cantidad><precio_compra>11.55</precio_compra><cantidad_recibida>74</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>5</id><folio>OC-20261020-000005</folio><solicitud_id>8</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-21</fecha_esperada><total>859.95</total><creada_en>2026-10-19T19:33:05-06:00</creada_en><cerrada_en>2026-10-19T19:33:06-06:00</cerrada_en><lineas><linea><producto><id>12</id><nombre>Chiles jalapeños en escabeche</nombre></producto><cantidad>63</cantidad><precio_compra>13.65</precio_compra><cantidad_recibida>63</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>4</id><folio>OC-20261020-000004</folio><solicitud_id>6</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-21</fecha_esperada><total>853.30</total><creada_en>2026-10-19T19:33:01-06:00</creada_en><cerrada_en>2026-10-19T19:33:03-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden><orden><id>1</id><folio>OC-20261020-000001</folio><solicitud_id>1</solicitud_id><proveedor><id>1</id><nombre>Abarrotes del Norte</nombre></proveedor><microhub_id>1</microhub_id><estado>recibida</estado><fecha_esperada>2026-10-21</fecha_esperada><total>853.30</total><creada_en>2026-10-19T19:31:38-06:00</creada_en><cerrada_en>2026-10-19T19:31:40-06:00</cerrada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad><precio_compra>18.55</precio_compra><cantidad_recibida>46</cantidad_recibida><pendiente_inventario>0</pendiente_inventario></linea></lineas></orden></datos><paginacion><pagina>1</pagina><por_pagina>20</por_pagina><total>11</total><paginas>1</paginas></paginacion></ordenes>
```

### ABA-21 · Tablero de abastecimiento · PASA

**Objetivo.** Solicitudes y órdenes por estado.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/seguimiento`

```http
Accept: application/json
X-Traza-Id: fb870c5c-a62f-498b-a1ee-473e63b4718c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 121 ms · traza `fb870c5c-a62f-498b-a1ee-473e63b4718c`

```json
{
  "microhub_id": 1,
  "solicitudes": {
    "pendiente": 0,
    "aprobada": 0,
    "rechazada": 6,
    "ordenada": 18
  },
  "ordenes": {
    "emitida": 0,
    "parcial": 0,
    "recibida": 11,
    "cancelada": 7
  },
  "atrasadas": 0,
  "pendientes_inventario": 0,
  "proxima_entrega": null
}
```

### ABA-22 · Cancelar sin permiso · PASA

**Objetivo.** Cancelar una orden es del administrador.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/19/cancelar`

```http
Accept: application/json
X-Traza-Id: 30e1f456-5d0e-413c-80d8-06cdebc08996
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "motivo": "No hace falta"
}
```

**Respuesta.** HTTP 403 (esperado 403) · 28 ms · traza `30e1f456-5d0e-413c-80d8-06cdebc08996`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "30e1f456-5d0e-413c-80d8-06cdebc08996"
  }
}
```

### ABA-23 · Cancelar una orden emitida · PASA

**Objetivo.** Una orden sin recepciones se puede cancelar con motivo.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/19/cancelar`

```http
Accept: application/json
X-Traza-Id: ad3c746f-704b-42bd-a69b-798b785de325
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "motivo": "El proveedor ya no surte"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 136 ms · traza `ad3c746f-704b-42bd-a69b-798b785de325`

```json
{
  "id": 19,
  "folio": "OC-20261020-000019",
  "solicitud_id": 27,
  "proveedor": {
    "id": 1,
    "nombre": "Abarrotes del Norte"
  },
  "microhub_id": 1,
  "estado": "cancelada",
  "fecha_esperada": "2026-10-22",
  "total": 853.3,
  "creada_en": "2026-10-20T00:43:24-06:00",
  "cerrada_en": "2026-10-20T00:43:25-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/19/recepcion`

```http
Accept: application/json
X-Traza-Id: dae057e4-391a-4739-97df-4f9e9d8de799
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

**Respuesta.** HTTP 409 (esperado 409) · 41 ms · traza `dae057e4-391a-4739-97df-4f9e9d8de799`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "La orden está cancelada; ya no recibe mercancía.",
    "traza_id": "dae057e4-391a-4739-97df-4f9e9d8de799"
  }
}
```

### ABA-25 · Solicitudes (XML) · PASA

**Objetivo.** Respuesta XML que cumple abastecimiento.xsd.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/solicitudes?por_pagina=3`

```http
Accept: application/xml
X-Traza-Id: fc382eef-b601-4682-8ed2-2c65793612e4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 67 ms · traza `fc382eef-b601-4682-8ed2-2c65793612e4`

```xml
<?xml version='1.0' encoding='utf-8'?>
<solicitudes xmlns="urn:microhubs:v1" version="1"><datos><solicitud><id>27</id><folio>SC-20261020-000027</folio><microhub_id>1</microhub_id><estado>ordenada</estado><motivo>Compra para cancelar</motivo><solicitada_por>2</solicitada_por><decidida_por>1</decidida_por><decision_motivo>Hay presupuesto</decision_motivo><decidida_en>2026-10-20T00:43:24-06:00</decidida_en><creada_en>2026-10-20T00:43:24-06:00</creada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad></linea></lineas></solicitud><solicitud><id>26</id><folio>SC-20261020-000026</folio><microhub_id>1</microhub_id><estado>ordenada</estado><motivo>Se acabó el producto el fin de semana</motivo><solicitada_por>2</solicitada_por><decidida_por>1</decidida_por><decision_motivo>Hay presupuesto</decision_motivo><decidida_en>2026-10-20T00:43:22-06:00</decidida_en><creada_en>2026-10-20T00:43:22-06:00</creada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad></linea></lineas></solicitud><solicitud><id>25</id><folio>SC-20261020-000025</folio><microhub_id>1</microhub_id><estado>ordenada</estado><motivo>Compra para cancelar</motivo><solicitada_por>2</solicitada_por><decidida_por>1</decidida_por><decision_motivo>Hay presupuesto</decision_motivo><decidida_en>2026-10-20T00:32:37-06:00</decidida_en><creada_en>2026-10-20T00:32:37-06:00</creada_en><lineas><linea><producto><id>10</id><nombre>Sardina en salsa de tomate</nombre></producto><cantidad>46</cantidad></linea></lineas></solicitud></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>25</total><paginas>9</paginas></paginacion></solicitudes>
```

### ABA-26 · Un auditor consulta · PASA

**Objetivo.** El auditor ve las solicitudes sin poder crear.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: 1e5b025c-effc-42e6-a7a4-6e278cf3a091
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 63 ms · traza `1e5b025c-effc-42e6-a7a4-6e278cf3a091`

```json
{
  "datos": [
    {
      "id": 27,
      "folio": "SC-20261020-000027",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Compra para cancelar",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-10-20T00:43:24-06:00",
      "creada_en": "2026-10-20T00:43:24-06:00",
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
      "id": 26,
      "folio": "SC-20261020-000026",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Se acabó el producto el fin de semana",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-10-20T00:43:22-06:00",
      "creada_en": "2026-10-20T00:43:22-06:00",
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
      "id": 25,
      "folio": "SC-20261020-000025",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Compra para cancelar",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-10-20T00:32:37-06:00",
      "creada_en": "2026-10-20T00:32:37-06:00",
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
      "id": 24,
      "folio": "SC-20261020-000024",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Se acabó el producto el fin de semana",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-10-20T00:32:35-06:00",
      "creada_en": "2026-10-20T00:32:34-06:00",
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
      "id": 23,
      "folio": "SC-20261020-000023",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Compra para cancelar",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-10-20T00:29:46-06:00",
      "creada_en": "2026-10-20T00:29:45-06:00",
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
      "id": 22,
      "folio": "SC-20261020-000022",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Se acabó el producto el fin de semana",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-10-20T00:29:43-06:00",
      "creada_en": "2026-10-20T00:29:43-06:00",
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
      "id": 21,
      "folio": "SC-20261020-000021",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Compra para cancelar",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-10-20T00:21:46-06:00",
      "creada_en": "2026-10-20T00:21:46-06:00",
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
      "id": 20,
      "folio": "SC-20261020-000020",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Se acabó el producto el fin de semana",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-10-20T00:21:44-06:00",
      "creada_en": "2026-10-20T00:21:43-06:00",
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
      "id": 19,
      "folio": "SC-20261020-000019",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Compra para cancelar",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-10-20T00:20:40-06:00",
      "creada_en": "2026-10-20T00:20:40-06:00",
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
      "id": 18,
      "folio": "SC-20261020-000018",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Se acabó el producto el fin de semana",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-10-20T00:20:38-06:00",
      "creada_en": "2026-10-20T00:20:38-06:00",
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
      "id": 17,
      "folio": "SC-20261020-000017",
      "microhub_id": 1,
      "estado": "rechazada",
      "motivo": "Prueba XML",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Prueba XML",
      "decidida_en": "2026-10-20T00:16:50-06:00",
      "creada_en": "2026-10-20T00:16:50-06:00",
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
      "id": 16,
      "folio": "SC-20261020-000016",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-10-20T00:16:49-06:00",
      "creada_en": "2026-10-20T00:16:49-06:00",
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
      "id": 15,
      "folio": "SC-20261020-000015",
      "microhub_id": 1,
      "estado": "rechazada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": null,
      "decision_motivo": "Limpieza de la prueba",
      "decidida_en": null,
      "creada_en": "2026-10-20T00:16:48-06:00",
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
      "id": 14,
      "folio": "SC-20261020-000014",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "ok",
      "decidida_en": "2026-10-20T00:16:45-06:00",
      "creada_en": "2026-10-20T00:16:45-06:00",
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
      "id": 12,
      "folio": "SC-20261020-000012",
      "microhub_id": 1,
      "estado": "rechazada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Todavía hay existencia",
      "decidida_en": "2026-10-20T00:16:45-06:00",
      "creada_en": "2026-10-20T00:16:44-06:00",
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
      "id": 11,
      "folio": "SC-20261020-000011",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-10-20T00:16:44-06:00",
      "creada_en": "2026-10-20T00:16:44-06:00",
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
      "id": 10,
      "folio": "SC-20261020-000010",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Demostración de fallo",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-10-19T19:33:42-06:00",
      "creada_en": "2026-10-19T19:33:41-06:00",
      "lineas": [
        {
          "producto": {
            "id": 16,
            "nombre": "Galletas María"
          },
          "cantidad": 74
        }
      ]
    },
    {
      "id": 9,
      "folio": "SC-20261020-000009",
      "microhub_id": 1,
      "estado": "rechazada",
      "motivo": "Prueba XML",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Prueba XML",
      "decidida_en": "2026-10-19T19:33:06-06:00",
      "creada_en": "2026-10-19T19:33:06-06:00",
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
      "id": 8,
      "folio": "SC-20261020-000008",
      "microhub_id": 1,
      "estado": "ordenada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": 1,
      "decision_motivo": "Hay presupuesto",
      "decidida_en": "2026-10-19T19:33:05-06:00",
      "creada_en": "2026-10-19T19:33:05-06:00",
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
      "id": 7,
      "folio": "SC-20261020-000007",
      "microhub_id": 1,
      "estado": "rechazada",
      "motivo": "Prueba de abastecimiento",
      "solicitada_por": 2,
      "decidida_por": null,
      "decision_motivo": "Limpieza de la prueba",
      "decidida_en": null,
      "creada_en": "2026-10-19T19:33:04-06:00",
      "lineas": [
        {
          "producto": {
            "id": 15,
            "nombre": "Avena en hojuelas"
          },
          "cantidad": 164
        }
      ]
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 20,
    "total": 25,
    "paginas": 2
  }
}
```

### ABA-27 · Un cliente consulta · PASA

**Objetivo.** El cliente no tiene abastecimiento.ver.

**Petición.** `GET http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: 0f6ee1b5-6a79-4c40-828b-b81f63744cf2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 25 ms · traza `0f6ee1b5-6a79-4c40-828b-b81f63744cf2`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "0f6ee1b5-6a79-4c40-828b-b81f63744cf2"
  }
}
```

## Servicio pedidos · puerto 5104

### ALI-01 · Resumen de pedidos por día y zona · PASA

**Objetivo.** Lo consume el servicio de demanda: pedidos, unidades, venta y clientes por día y zona.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/resumen?por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 5f949441-5f69-4f62-b113-2d246f7b218c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 103 ms · traza `5f949441-5f69-4f62-b113-2d246f7b218c`

```json
{
  "datos": [
    {
      "fecha": "2026-09-20",
      "zona_id": 2,
      "categoria_id": null,
      "pedidos": 2,
      "unidades": 8,
      "venta": 232.5,
      "clientes": 2,
      "no_atendidos": 1
    },
    {
      "fecha": "2026-09-20",
      "zona_id": 3,
      "categoria_id": null,
      "pedidos": 1,
      "unidades": 5,
      "venta": 126.0,
      "clientes": 1,
      "no_atendidos": 0
    },
    {
      "fecha": "2026-09-21",
      "zona_id": 1,
      "categoria_id": null,
      "pedidos": 1,
      "unidades": 4,
      "venta": 123.0,
      "clientes": 1,
      "no_atendidos": 1
    },
    {
      "fecha": "2026-09-21",
      "zona_id": 2,
      "categoria_id": null,
      "pedidos": 4,
      "unidades": 15,
      "venta": 476.0,
      "clientes": 4,
      "no_atendidos": 0
    },
    {
      "fecha": "2026-09-21",
      "zona_id": 3,
      "categoria_id": null,
      "pedidos": 1,
      "unidades": 4,
      "venta": 139.0,
      "clientes": 1,
      "no_atendidos": 3
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 71,
    "paginas": 15
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
X-Traza-Id: 858f286b-0a63-4508-ace2-53da00630830
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 7 ms · traza `858f286b-0a63-4508-ace2-53da00630830`

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
    "traza_id": "858f286b-0a63-4508-ace2-53da00630830"
  }
}
```

### ALI-03 · Ventas por producto · PASA

**Objetivo.** Lo consume surtido: unidades y venta de cada producto, sin cancelados.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/ventas?por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 4b6b8bd4-6f28-4ed3-8c90-ae465a1ec1f4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 104 ms · traza `4b6b8bd4-6f28-4ed3-8c90-ae465a1ec1f4`

```json
{
  "datos": [
    {
      "producto_id": 23,
      "unidades": 21,
      "venta": 808.5,
      "pedidos": 17
    },
    {
      "producto_id": 28,
      "unidades": 21,
      "venta": 157.5,
      "pedidos": 11
    },
    {
      "producto_id": 40,
      "unidades": 21,
      "venta": 588.0,
      "pedidos": 20
    },
    {
      "producto_id": 33,
      "unidades": 20,
      "venta": 720.0,
      "pedidos": 13
    },
    {
      "producto_id": 34,
      "unidades": 20,
      "venta": 880.0,
      "pedidos": 18
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
X-Traza-Id: 0cbb496b-ada2-4a6b-a0c9-90bdf5f30d1f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 5 ms · traza `0cbb496b-ada2-4a6b-a0c9-90bdf5f30d1f`

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
    "traza_id": "0cbb496b-ada2-4a6b-a0c9-90bdf5f30d1f"
  }
}
```

### ALI-05 · Pedidos listos de un microhub · PASA

**Objetivo.** Con las coordenadas de entrega: lo que rutas agrupa y ordena.

**Petición.** `GET http://pedidos:5104/api/v1/pedidos/listos?microhub_id=1`

```http
Accept: application/json
X-Traza-Id: e35d188d-fe7b-4a02-8dce-f0584db600ad
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 72 ms · traza `e35d188d-fe7b-4a02-8dce-f0584db600ad`

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
X-Traza-Id: 39e285be-5888-4200-969f-428285908c3c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 67 ms · traza `39e285be-5888-4200-969f-428285908c3c`

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
X-Traza-Id: 37bc565e-06b0-40b1-be16-5e095146f8ad
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 93 ms · traza `37bc565e-06b0-40b1-be16-5e095146f8ad`

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
X-Traza-Id: dab8ed33-9f8e-434f-9bd5-afc01b81f2f4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 7 ms · traza `dab8ed33-9f8e-434f-9bd5-afc01b81f2f4`

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
    "traza_id": "dab8ed33-9f8e-434f-9bd5-afc01b81f2f4"
  }
}
```

## Servicio demanda · puerto 5115

### DEM-01 · Observaciones de demanda · PASA

**Objetivo.** Pedidos por día, zona y categoría, con la fuente de cada dato.

**Petición.** `GET http://demanda:5115/api/v1/demanda/observaciones?nivel=total&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: c576af2e-c8d7-48d6-9575-c2476610dac0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 222 ms · traza `c576af2e-c8d7-48d6-9575-c2476610dac0`

```json
{
  "datos": [
    {
      "fecha": "2026-10-19",
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
      "fecha": "2026-10-19",
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
      "fecha": "2026-10-19",
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
      "fecha": "2026-10-19",
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
      "fecha": "2026-10-18",
      "zona": {
        "id": 1,
        "nombre": "San Bernabé Centro"
      },
      "categoria": null,
      "pedidos": 19,
      "unidades": 99,
      "venta": 2708.84,
      "clientes": 16,
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
    "observaciones": 1464,
    "desde": "2026-08-20",
    "hasta": "2026-10-19"
  }
]
```

### DEM-02 · Observaciones (XML) · PASA

**Objetivo.** Respuesta XML que cumple demanda.xsd.

**Petición.** `GET http://demanda:5115/api/v1/demanda/observaciones?por_pagina=3`

```http
Accept: application/xml
X-Traza-Id: f1e9a27a-aa96-4896-a3a9-2fd181f4ef81
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 109 ms · traza `f1e9a27a-aa96-4896-a3a9-2fd181f4ef81`

```xml
<?xml version='1.0' encoding='utf-8'?>
<observaciones_demanda xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><datos><observacion><fecha>2026-10-19</fecha><zona><id>1</id><nombre>San Bernabé Centro</nombre></zona><categoria xsi:nil="true" /><pedidos>17</pedidos><unidades>88</unidades><venta>2423.70</venta><clientes>14</clientes><no_atendidos>1</no_atendidos><fuente>sintetica</fuente></observacion><observacion><fecha>2026-10-19</fecha><zona><id>1</id><nombre>San Bernabé Centro</nombre></zona><categoria><id>1</id><nombre>Abarrote básico</nombre></categoria><pedidos>17</pedidos><unidades>40</unidades><venta>1090.67</venta><clientes>0</clientes><no_atendidos>0</no_atendidos><fuente>sintetica</fuente></observacion><observacion><fecha>2026-10-19</fecha><zona><id>1</id><nombre>San Bernabé Centro</nombre></zona><categoria><id>2</id><nombre>Bebidas</nombre></categoria><pedidos>7</pedidos><unidades>18</unidades><venta>484.74</venta><clientes>0</clientes><no_atendidos>0</no_atendidos><fuente>sintetica</fuente></observacion></datos><paginacion><pagina>1</pagina><por_pagina>3</por_pagina><total>1440</total><paginas>480</paginas></paginacion></observaciones_demanda>
```

### DEM-03 · Fuente desconocida · PASA

**Objetivo.** Un filtro desconocido se rechaza.

**Petición.** `GET http://demanda:5115/api/v1/demanda/observaciones?fuente=inventada`

```http
Accept: application/json
X-Traza-Id: 062ab90a-a228-4fa0-9d59-206bf3c44547
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 55 ms · traza `062ab90a-a228-4fa0-9d59-206bf3c44547`

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
    "traza_id": "062ab90a-a228-4fa0-9d59-206bf3c44547"
  }
}
```

### DEM-04 · El operador consulta la demanda · PASA

**Objetivo.** Sin demanda.ver.

**Petición.** `GET http://demanda:5115/api/v1/demanda/observaciones`

```http
Accept: application/json
X-Traza-Id: 8dc4cabd-330f-4490-a85b-0ff95dea6837
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 26 ms · traza `8dc4cabd-330f-4490-a85b-0ff95dea6837`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "8dc4cabd-330f-4490-a85b-0ff95dea6837"
  }
}
```

### DEM-05 · Resumen por zona · PASA

**Objetivo.** Pedidos, ticket promedio, pedidos por cliente y demanda no atendida.

**Petición.** `GET http://demanda:5115/api/v1/demanda/resumen`

```http
Accept: application/json
X-Traza-Id: ec53bb76-d3bc-4241-820f-bd7638eebc36
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 107 ms · traza `ec53bb76-d3bc-4241-820f-bd7638eebc36`

```json
{
  "desde": "2026-08-21",
  "hasta": "2026-10-19",
  "dias": 60,
  "total": {
    "pedidos": 2896,
    "pedidos_dia": 48.27,
    "unidades_por_pedido": 5.21,
    "venta": 389701.21,
    "ticket_promedio": 134.57,
    "pedidos_por_cliente": 1.16,
    "no_atendidos": 198,
    "pct_no_atendida": 6.4
  },
  "zonas": [
    {
      "zona": {
        "id": 1,
        "nombre": "San Bernabé Centro"
      },
      "pedidos": 1006,
      "pedidos_dia": 16.77,
      "unidades_por_pedido": 5.21,
      "venta": 136058.53,
      "ticket_promedio": 135.25,
      "pedidos_por_cliente": 1.17,
      "no_atendidos": 60,
      "pct_no_atendida": 5.6
    },
    {
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "pedidos": 742,
      "pedidos_dia": 12.37,
      "unidades_por_pedido": 5.2,
      "venta": 99564.62,
      "ticket_promedio": 134.18,
      "pedidos_por_cliente": 1.17,
      "no_atendidos": 60,
      "pct_no_atendida": 7.5
    },
    {
      "zona": {
        "id": 3,
        "nombre": "Paseo de San Bernabé"
      },
      "pedidos": 630,
      "pedidos_dia": 10.5,
      "unidades_por_pedido": 5.21,
      "venta": 84343.2,
      "ticket_promedio": 133.88,
      "pedidos_por_cliente": 1.16,
      "no_atendidos": 52,
      "pct_no_atendida": 7.6
    },
    {
      "zona": {
        "id": 4,
        "nombre": "San Bernabé X (F-113)"
      },
      "pedidos": 518,
      "pedidos_dia": 8.63,
      "unidades_por_pedido": 5.21,
      "venta": 69734.86,
      "ticket_promedio": 134.62,
      "pedidos_por_cliente": 1.15,
      "no_atendidos": 26,
      "pct_no_atendida": 4.8
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
    "pedidos": 1021,
    "ticket": "135.13"
  },
  {
    "zona_id": 2,
    "pedidos": 752,
    "ticket": "134.14"
  },
  {
    "zona_id": 3,
    "pedidos": 638,
    "ticket": "133.94"
  },
  {
    "zona_id": 4,
    "pedidos": 525,
    "ticket": "134.73"
  }
]
```

### DEM-06 · Patrones de la semana · PASA

**Objetivo.** Índice de cada día de la semana y venta por categoría.

**Petición.** `GET http://demanda:5115/api/v1/demanda/patrones`

```http
Accept: application/json
X-Traza-Id: 885414f8-6543-4429-b5c7-792f63a20308
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 95 ms · traza `885414f8-6543-4429-b5c7-792f63a20308`

```json
{
  "desde": "2026-08-21",
  "hasta": "2026-10-19",
  "dias": 60,
  "suficiente": true,
  "semanal": [
    {
      "dia": 1,
      "nombre": "lunes",
      "pedidos_promedio": 42.44,
      "indice": 0.879
    },
    {
      "dia": 2,
      "nombre": "martes",
      "pedidos_promedio": 40.12,
      "indice": 0.831
    },
    {
      "dia": 3,
      "nombre": "miércoles",
      "pedidos_promedio": 42.88,
      "indice": 0.888
    },
    {
      "dia": 4,
      "nombre": "jueves",
      "pedidos_promedio": 45.25,
      "indice": 0.938
    },
    {
      "dia": 5,
      "nombre": "viernes",
      "pedidos_promedio": 54.33,
      "indice": 1.126
    },
    {
      "dia": 6,
      "nombre": "sábado",
      "pedidos_promedio": 61.89,
      "indice": 1.282
    },
    {
      "dia": 7,
      "nombre": "domingo",
      "pedidos_promedio": 49.11,
      "indice": 1.017
    }
  ],
  "categorias": [
    {
      "categoria": {
        "id": 1,
        "nombre": "Abarrote básico"
      },
      "unidades": 6792,
      "venta": 175365.59,
      "pct_venta": 45.0
    },
    {
      "categoria": {
        "id": 2,
        "nombre": "Bebidas"
      },
      "unidades": 2997,
      "venta": 77940.3,
      "pct_venta": 20.0
    },
    {
      "categoria": {
        "id": 3,
        "nombre": "Lácteos y huevo"
      },
      "unidades": 2263,
      "venta": 58455.17,
      "pct_venta": 15.0
    },
    {
      "categoria": {
        "id": 4,
        "nombre": "Limpieza del hogar"
      },
      "unidades": 1805,
      "venta": 46764.14,
      "pct_venta": 12.0
    },
    {
      "categoria": {
        "id": 5,
        "nombre": "Higiene personal"
      },
      "unidades": 1211,
      "venta": 31176.18,
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
X-Traza-Id: bf0765dc-0d50-46c0-afc0-25d9693c32da
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 72 ms · traza `bf0765dc-0d50-46c0-afc0-25d9693c32da`

```json
{
  "metodo": "tendencia_estacional",
  "zona": null,
  "historia_desde": "2026-08-21",
  "historia_hasta": "2026-10-19",
  "historia_dias": 60,
  "horizonte": 14,
  "indices_confiables": true,
  "nivel_pedidos_dia": 52.07,
  "pendiente_pedidos_dia": 0.129,
  "desviacion_error": 1.41,
  "total_pedidos": 738.6,
  "promedio_dia": 52.76,
  "serie": [
    {
      "fecha": "2026-10-20",
      "pedidos": 43.4,
      "minimo": 41.6,
      "maximo": 45.2
    },
    {
      "fecha": "2026-10-21",
      "pedidos": 46.5,
      "minimo": 44.7,
      "maximo": 48.3
    },
    {
      "fecha": "2026-10-22",
      "pedidos": 49.2,
      "minimo": 47.4,
      "maximo": 51.0
    },
    {
      "fecha": "2026-10-23",
      "pedidos": 59.2,
      "minimo": 57.4,
      "maximo": 61.0
    },
    {
      "fecha": "2026-10-24",
      "pedidos": 67.6,
      "minimo": 65.8,
      "maximo": 69.4
    },
    {
      "fecha": "2026-10-25",
      "pedidos": 53.8,
      "minimo": 52.0,
      "maximo": 55.6
    },
    {
      "fecha": "2026-10-26",
      "pedidos": 46.6,
      "minimo": 44.8,
      "maximo": 48.4
    },
    {
      "fecha": "2026-10-27",
      "pedidos": 44.1,
      "minimo": 42.3,
      "maximo": 45.9
    },
    {
      "fecha": "2026-10-28",
      "pedidos": 47.3,
      "minimo": 45.5,
      "maximo": 49.1
    },
    {
      "fecha": "2026-10-29",
      "pedidos": 50.0,
      "minimo": 48.2,
      "maximo": 51.8
    },
    {
      "fecha": "2026-10-30",
      "pedidos": 60.2,
      "minimo": 58.4,
      "maximo": 62.0
    },
    {
      "fecha": "2026-10-31",
      "pedidos": 68.7,
      "minimo": 66.9,
      "maximo": 70.5
    },
    {
      "fecha": "2026-11-01",
      "pedidos": 54.7,
      "minimo": 52.9,
      "maximo": 56.5
    },
    {
      "fecha": "2026-11-02",
      "pedidos": 47.4,
      "minimo": 45.6,
      "maximo": 49.2
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
X-Traza-Id: f9298ef1-917e-4d18-8ae0-b682205af855
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 71 ms · traza `f9298ef1-917e-4d18-8ae0-b682205af855`

```json
{
  "metodo": "promedio_movil",
  "zona": null,
  "historia_desde": "2026-08-21",
  "historia_hasta": "2026-10-19",
  "historia_dias": 60,
  "horizonte": 7,
  "indices_confiables": true,
  "nivel_pedidos_dia": 51.53,
  "pendiente_pedidos_dia": 0.0,
  "desviacion_error": 1.47,
  "total_pedidos": 358.7,
  "promedio_dia": 51.25,
  "serie": [
    {
      "fecha": "2026-10-20",
      "pedidos": 42.8,
      "minimo": 40.9,
      "maximo": 44.7
    },
    {
      "fecha": "2026-10-21",
      "pedidos": 45.8,
      "minimo": 43.9,
      "maximo": 47.7
    },
    {
      "fecha": "2026-10-22",
      "pedidos": 48.3,
      "minimo": 46.4,
      "maximo": 50.2
    },
    {
      "fecha": "2026-10-23",
      "pedidos": 58.0,
      "minimo": 56.1,
      "maximo": 59.9
    },
    {
      "fecha": "2026-10-24",
      "pedidos": 66.1,
      "minimo": 64.2,
      "maximo": 68.0
    },
    {
      "fecha": "2026-10-25",
      "pedidos": 52.4,
      "minimo": 50.5,
      "maximo": 54.3
    },
    {
      "fecha": "2026-10-26",
      "pedidos": 45.3,
      "minimo": 43.4,
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
X-Traza-Id: e6e5a746-5551-43ff-bd31-41859ab0334c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 29 ms · traza `e6e5a746-5551-43ff-bd31-41859ab0334c`

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
    "traza_id": "e6e5a746-5551-43ff-bd31-41859ab0334c"
  }
}
```

### DEM-10 · Comparación contra lo observado · PASA

**Objetivo.** Se ocultan los últimos 7 días, se proyectan y se miden el error y el sesgo.

**Petición.** `GET http://demanda:5115/api/v1/demanda/comparacion`

```http
Accept: application/json
X-Traza-Id: d7d3bd24-a123-4f8d-80fc-3e27f871eea0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 67 ms · traza `d7d3bd24-a123-4f8d-80fc-3e27f871eea0`

```json
{
  "metodo": "tendencia_estacional",
  "zona": null,
  "dias_prueba": 7,
  "dias_entrenamiento": 53,
  "mape_pct": 2.7,
  "sesgo_pct": 0.4,
  "dentro_banda_pct": 71.4,
  "filas": [
    {
      "fecha": "2026-10-13",
      "observado": 43,
      "proyectado": 42.7,
      "error": -0.3,
      "error_pct": -0.8
    },
    {
      "fecha": "2026-10-14",
      "observado": 44,
      "proyectado": 46.0,
      "error": 2.0,
      "error_pct": 4.5
    },
    {
      "fecha": "2026-10-15",
      "observado": 49,
      "proyectado": 48.3,
      "error": -0.7,
      "error_pct": -1.5
    },
    {
      "fecha": "2026-10-16",
      "observado": 61,
      "proyectado": 57.9,
      "error": -3.1,
      "error_pct": -5.1
    },
    {
      "fecha": "2026-10-17",
      "observado": 65,
      "proyectado": 66.7,
      "error": 1.7,
      "error_pct": 2.7
    },
    {
      "fecha": "2026-10-18",
      "observado": 52,
      "proyectado": 53.0,
      "error": 1.0,
      "error_pct": 2.0
    },
    {
      "fecha": "2026-10-19",
      "observado": 45,
      "proyectado": 45.9,
      "error": 0.9,
      "error_pct": 2.1
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
X-Traza-Id: 684d40a2-be03-420b-bb57-f975571e5d5e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 129 ms · traza `684d40a2-be03-420b-bb57-f975571e5d5e`

```json
{
  "zona": null,
  "hogares": 6709,
  "penetracion": 0.12,
  "pedidos_hogar_mes": 2.5,
  "pedidos_mes_potencial": 2012.7,
  "pedidos_dia_potencial": 67.1,
  "pedidos_dia_observados": 50.0,
  "cuota_capturada_pct": 74.6,
  "brecha_pedidos_dia": 17.1,
  "escenarios": [
    {
      "penetracion": 0.04,
      "pedidos_mes": 670.9,
      "pedidos_dia": 22.4,
      "cuota_capturada_pct": 223.7,
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
      "brecha_pedidos_dia": 17.1
    },
    {
      "penetracion": 0.16,
      "pedidos_mes": 2683.6,
      "pedidos_dia": 89.5,
      "cuota_capturada_pct": 55.9,
      "brecha_pedidos_dia": 39.4
    },
    {
      "penetracion": 0.2,
      "pedidos_mes": 3354.5,
      "pedidos_dia": 111.8,
      "cuota_capturada_pct": 44.7,
      "brecha_pedidos_dia": 61.8
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
X-Traza-Id: cb6f218c-8304-431b-9a41-40edf92095c2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 186 ms · traza `cb6f218c-8304-431b-9a41-40edf92095c2`

```json
{
  "zona": null,
  "hogares": 6709,
  "penetracion": 0.2,
  "pedidos_hogar_mes": 2.5,
  "pedidos_mes_potencial": 3354.5,
  "pedidos_dia_potencial": 111.8,
  "pedidos_dia_observados": 50.0,
  "cuota_capturada_pct": 44.7,
  "brecha_pedidos_dia": 61.8,
  "escenarios": [
    {
      "penetracion": 0.04,
      "pedidos_mes": 670.9,
      "pedidos_dia": 22.4,
      "cuota_capturada_pct": 223.7,
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
      "brecha_pedidos_dia": 17.1
    },
    {
      "penetracion": 0.16,
      "pedidos_mes": 2683.6,
      "pedidos_dia": 89.5,
      "cuota_capturada_pct": 55.9,
      "brecha_pedidos_dia": 39.4
    },
    {
      "penetracion": 0.2,
      "pedidos_mes": 3354.5,
      "pedidos_dia": 111.8,
      "cuota_capturada_pct": 44.7,
      "brecha_pedidos_dia": 61.8
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
X-Traza-Id: 64858c85-e111-4757-b3e2-90b0075c1c4f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{
  "desde": "2026-10-18",
  "hasta": "2026-10-20"
}
```

**Respuesta.** HTTP 403 (esperado 403) · 56 ms · traza `64858c85-e111-4757-b3e2-90b0075c1c4f`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "64858c85-e111-4757-b3e2-90b0075c1c4f"
  }
}
```

### DEM-14 · Sincronizar con pedidos reales · PASA

**Objetivo.** Lo sintético del rango se reemplaza por lo real.

**Petición.** `POST http://demanda:5115/api/v1/demanda/sincronizacion`

```http
Accept: application/json
X-Traza-Id: e94e5da8-bfaa-4a05-ac97-7c5274b73d4d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "desde": "2026-10-18",
  "hasta": "2026-10-20"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 221 ms · traza `e94e5da8-bfaa-4a05-ac97-7c5274b73d4d`

```json
{
  "desde": "2026-10-18",
  "hasta": "2026-10-20",
  "filas_escritas": 11,
  "pedidos_leidos": 24,
  "sinteticas_reemplazadas": 48
}
```

**Explicación.** Lee pedidos/resumen y guarda las observaciones como propias (fuente = pedidos). Es idempotente: repetirlo deja lo mismo.

**Evidencia en PostgreSQL.** `SELECT fuente, count(*) AS observaciones FROM demanda_observacion WHERE fecha BETWEEN %s AND %s GROUP BY fuente`

```json
[
  {
    "fuente": "pedidos",
    "observaciones": 11
  }
]
```

### DEM-15 · Sincronizar con fechas inválidas · PASA

**Objetivo.** desde no puede ser posterior a hasta.

**Petición.** `POST http://demanda:5115/api/v1/demanda/sincronizacion`

```http
Accept: application/json
X-Traza-Id: 5acd8637-559b-4b62-a0cd-6b652a1802fc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "desde": "2026-10-10",
  "hasta": "2026-10-01"
}
```

**Respuesta.** HTTP 422 (esperado 422) · 6 ms · traza `5acd8637-559b-4b62-a0cd-6b652a1802fc`

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
    "traza_id": "5acd8637-559b-4b62-a0cd-6b652a1802fc"
  }
}
```

### DEM-16 · Sincronizar (XML) · PASA

**Objetivo.** El cuerpo XML se valida contra demanda.xsd antes de procesarse.

**Petición.** `POST http://demanda:5115/api/v1/demanda/sincronizacion`

```http
Accept: application/xml
X-Traza-Id: a1887ceb-8f70-44a2-80f1-060c43b64c88
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><sincronizacion_nueva xmlns="urn:microhubs:v1"><desde>2026-10-20</desde><hasta>2026-10-20</hasta></sincronizacion_nueva>
```

**Respuesta.** HTTP 201 (esperado 201) · 135 ms · traza `a1887ceb-8f70-44a2-80f1-060c43b64c88`

```xml
<?xml version='1.0' encoding='utf-8'?>
<sincronizacion xmlns="urn:microhubs:v1" version="1"><desde>2026-10-20</desde><hasta>2026-10-20</hasta><filas_escritas>4</filas_escritas><pedidos_leidos>13</pedidos_leidos><sinteticas_reemplazadas>0</sinteticas_reemplazadas></sincronizacion>
```

### DEM-17 · Supuestos de la demanda · PASA

**Objetivo.** Valor, origen (medido, supuesto o normativo), justificación y cómo calibrarlo.

**Petición.** `GET http://demanda:5115/api/v1/demanda/supuestos`

```http
Accept: application/json
X-Traza-Id: 9944f78e-bab5-46f2-8da4-a166d25a5182
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 37 ms · traza `9944f78e-bab5-46f2-8da4-a166d25a5182`

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
      "justificacion": "Parte de los hogares que pide a domicilio en un mes. 12 % es…(151 caracteres)",
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
X-Traza-Id: 7366643c-1e9a-47c0-9fc5-c0f822cdc5f7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 106 ms · traza `7366643c-1e9a-47c0-9fc5-c0f822cdc5f7`

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
X-Traza-Id: 73615b20-1448-4f3e-8428-968fcbaf43db
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 65 ms · traza `73615b20-1448-4f3e-8428-968fcbaf43db`

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
X-Traza-Id: 26900d5b-2f01-4f19-954b-4cd5c23c48e9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 72 ms · traza `26900d5b-2f01-4f19-954b-4cd5c23c48e9`

```xml
<?xml version='1.0' encoding='utf-8'?>
<cobertura_resumen xmlns="urn:microhubs:v1" version="1"><zonas>4</zonas><zonas_cubiertas>4</zonas_cubiertas><pct_zonas>100</pct_zonas><hogares>6709</hogares><hogares_cubiertos>6709</hogares_cubiertos><pct_hogares>100</pct_hogares><tiempo_promedio_min>5.5</tiempo_promedio_min><dentro_promesa_pct>100</dentro_promesa_pct><zonas_solapadas>3</zonas_solapadas><zonas_sin_cobertura /><microhubs_activos>3</microhubs_activos><supuestos_usados><supuesto><clave>factor_rodeo_distancia</clave><valor>1.3</valor><modificado>false</modificado></supuesto><supuesto><clave>velocidad_reparto_kmh</clave><valor>22</valor><modificado>false</modificado></supuesto><supuesto><clave>tiempo_servicio_min</clave><valor>4</valor><modificado>false</modificado></supuesto><supuesto><clave>cob_tiempo_max_min</clave><valor>30</valor><modificado>false</modificado></supuesto><supuesto><clave>cob_solape_max_pct</clave><valor>40</valor><modificado>false</modificado></supuesto><supuesto><clave>tamano_hogar</clave><valor>3.6</valor><modificado>false</modificado></supuesto></supuestos_usados></cobertura_resumen>
```

### COB-04 · Un punto junto a un microhub · PASA

**Objetivo.** Qué microhubs lo cubren y a qué distancia.

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/punto?latitud=25.748&longitud=-100.364`

```http
Accept: application/json
X-Traza-Id: 82e46d0f-9aba-4390-9d9f-fd53e87a0cf6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 47 ms · traza `82e46d0f-9aba-4390-9d9f-fd53e87a0cf6`

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
X-Traza-Id: 01253123-2c0e-4740-a5b1-718c045ce5ae
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 56 ms · traza `01253123-2c0e-4740-a5b1-718c045ce5ae`

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
X-Traza-Id: 6756529d-c1bb-4643-8763-dd7672f02754
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 6 ms · traza `6756529d-c1bb-4643-8763-dd7672f02754`

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
    "traza_id": "6756529d-c1bb-4643-8763-dd7672f02754"
  }
}
```

### COB-07 · Ubicaciones candidatas con ranking · PASA

**Objetivo.** Cada candidata de planeación frente a la red actual.

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/candidatos`

```http
Accept: application/json
X-Traza-Id: eccb71f2-d1f8-4264-b6d4-b29e94653276
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 113 ms · traza `eccb71f2-d1f8-4264-b6d4-b29e94653276`

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
      "ranking": 3
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
      "ranking": 4
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
      "ranking": 5
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
      "ranking": 6
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
      "ranking": 7
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
      "ranking": 8
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
X-Traza-Id: 1b7dd09f-1753-464f-9923-2e9e848eacf8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "candidato_id": 3
}
```

**Respuesta.** HTTP 200 (esperado 200) · 96 ms · traza `1b7dd09f-1753-464f-9923-2e9e848eacf8`

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
X-Traza-Id: 0c993a71-56c2-4e83-afb1-0033a80d3ab0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{
  "candidato_id": 3,
  "guardar": true
}
```

**Respuesta.** HTTP 403 (esperado 403) · 91 ms · traza `0c993a71-56c2-4e83-afb1-0033a80d3ab0`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Guardar una evaluación exige el permiso planeacion.editar.",
    "traza_id": "0c993a71-56c2-4e83-afb1-0033a80d3ab0"
  }
}
```

### COB-10 · Guardar la evaluación · PASA

**Objetivo.** Queda en cobertura_evaluacion con su resultado completo.

**Petición.** `POST http://cobertura:5116/api/v1/cobertura/evaluaciones`

```http
Accept: application/json
X-Traza-Id: a26f60bd-ca9a-4db2-82c8-1853f28d46b0
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

**Respuesta.** HTTP 201 (esperado 201) · 172 ms · traza `a26f60bd-ca9a-4db2-82c8-1853f28d46b0`

```json
{
  "id": 12,
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
    "id": 12,
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
X-Traza-Id: 71e0cd77-0970-4d90-81e9-e274fdb0b727
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 54 ms · traza `71e0cd77-0970-4d90-81e9-e274fdb0b727`

```json
{
  "datos": [
    {
      "id": 12,
      "nombre": "Evidencia Ola 2",
      "zonas_nuevas": 0,
      "hogares_nuevos": 0,
      "solapamiento_pct": 0.0,
      "canibaliza": false,
      "creado_por": 5,
      "creado_en": "2026-10-20T00:43:32-06:00"
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

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/evaluaciones/12`

```http
Accept: application/json
X-Traza-Id: b3e411ee-3a9b-4e4d-8e7a-7fa36f5d7e04
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 28 ms · traza `b3e411ee-3a9b-4e4d-8e7a-7fa36f5d7e04`

```json
{
  "id": 12,
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
X-Traza-Id: 104997c4-deb3-48a1-818b-4a62d80eda15
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

**Respuesta.** HTTP 200 (esperado 200) · 49 ms · traza `104997c4-deb3-48a1-818b-4a62d80eda15`

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
X-Traza-Id: 6f502a99-0c1f-4e9b-af50-81a0ec9cb4e6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "radio_km": 2
}
```

**Respuesta.** HTTP 422 (esperado 422) · 5 ms · traza `6f502a99-0c1f-4e9b-af50-81a0ec9cb4e6`

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
    "traza_id": "6f502a99-0c1f-4e9b-af50-81a0ec9cb4e6"
  }
}
```

### COB-13 · Escenarios de radio y de rodeo · PASA

**Objetivo.** Cuánto cubre la red con otros radios y otro factor de calle.

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/escenarios?radios=0.5,1,1.5,2&rodeos=1.2,1.5`

```http
Accept: application/json
X-Traza-Id: 22a6c48a-be03-44cc-b342-6eb2dfbe4bed
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 47 ms · traza `22a6c48a-be03-44cc-b342-6eb2dfbe4bed`

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
X-Traza-Id: f0c2a696-97c5-49b4-b162-6e8859017193
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "poblacion": 8520,
  "fuente": "INEGI, Censo 2020, AGEB de prueba"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 66 ms · traza `f0c2a696-97c5-49b4-b162-6e8859017193`

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
      "actualizado_en": "2026-10-20T06:32:44.511388+00:00"
    },
    "valores_nuevos": {
      "fuente": "INEGI, Censo 2020, AGEB de prueba",
      "poblacion": 8520,
      "actualizado_en": "2026-10-20T06:43:32.446923+00:00"
    }
  }
]
```

### COB-15 · Corregir la población sin permiso · PASA

**Objetivo.** Es del planeador.

**Petición.** `PUT http://cobertura:5116/api/v1/cobertura/zonas/1/poblacion`

```http
Accept: application/json
X-Traza-Id: cc4fae83-6bda-4819-b36a-e41c416460d0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "poblacion": 1,
  "fuente": "Sin permiso"
}
```

**Respuesta.** HTTP 403 (esperado 403) · 31 ms · traza `cc4fae83-6bda-4819-b36a-e41c416460d0`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "cc4fae83-6bda-4819-b36a-e41c416460d0"
  }
}
```

### COB-16 · Supuestos de la cobertura · PASA

**Objetivo.** Rodeo, velocidad, tiempo de servicio, promesa de entrega y tamaño del hogar.

**Petición.** `GET http://cobertura:5116/api/v1/cobertura/supuestos`

```http
Accept: application/json
X-Traza-Id: 3265c3ef-aeb5-4240-b943-d12a3732100f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 34 ms · traza `3265c3ef-aeb5-4240-b943-d12a3732100f`

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
X-Traza-Id: 49cb408a-5883-460c-8d99-e5d131b39606
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 40 ms · traza `49cb408a-5883-460c-8d99-e5d131b39606`

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
      "actualizado_en": "2026-10-20T00:32:45-06:00"
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
X-Traza-Id: e1c2af2f-a1d7-4d4f-aafe-b01876a17a3b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 6 ms · traza `e1c2af2f-a1d7-4d4f-aafe-b01876a17a3b`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "e1c2af2f-a1d7-4d4f-aafe-b01876a17a3b"
  }
}
```

### CAP-03 · Capacidad con una carga dada · PASA

**Objetivo.** Capacidad por etapa, utilización, cuello de botella y personal requerido.

**Petición.** `GET http://capacidad:5117/api/v1/capacidad/microhubs/1?carga_dia=60`

```http
Accept: application/json
X-Traza-Id: bc18668f-f249-43aa-88e2-1fc9d74c8c45
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 46 ms · traza `bc18668f-f249-43aa-88e2-1fc9d74c8c45`

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
X-Traza-Id: 0646f206-5e6c-4104-a923-80357543fe2f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 75 ms · traza `0646f206-5e6c-4104-a923-80357543fe2f`

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
X-Traza-Id: 6b07f919-439c-423c-9376-c61597e9d956
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 49 ms · traza `6b07f919-439c-423c-9376-c61597e9d956`

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
X-Traza-Id: 692d9f17-766c-46f7-b6a9-cfa8a9e63e07
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 28 ms · traza `692d9f17-766c-46f7-b6a9-cfa8a9e63e07`

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
    "traza_id": "692d9f17-766c-46f7-b6a9-cfa8a9e63e07"
  }
}
```

### CAP-06 · Capacidad (XML) · PASA

**Objetivo.** Respuesta XML que cumple capacidad.xsd.

**Petición.** `GET http://capacidad:5117/api/v1/capacidad/microhubs/1?carga_dia=60`

```http
Accept: application/xml
X-Traza-Id: bf4fe7e4-9f73-40bc-9ba9-c0c3a48aee8c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 55 ms · traza `bf4fe7e4-9f73-40bc-9ba9-c0c3a48aee8c`

```xml
<?xml version='1.0' encoding='utf-8'?>
<capacidad_microhub xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><operadores>3</operadores><repartidores>3</repartidores><capacidad_fisica>150</capacidad_fisica><horas>10</horas><distancia_km>2.4</distancia_km><carga_dia>60</carga_dia><capacidad_hora>16.36</capacidad_hora><capacidad_dia>150</capacidad_dia><utilizacion_pct>40</utilizacion_pct><nivel>estable</nivel><utilizacion_pico_pct>49.5</utilizacion_pico_pct><nivel_pico>estable</nivel_pico><cuello_botella>espacio físico</cuello_botella><minutos_por_pedido_operacion>11</minutos_por_pedido_operacion><minutos_por_entrega>8.4</minutos_por_entrega><etapas><etapa><etapa>picking</etapa><minutos_por_pedido>6</minutos_por_pedido><pct_tiempo>54.5</pct_tiempo><capacidad_hora>30</capacidad_hora></etapa><etapa><etapa>empaque</etapa><minutos_por_pedido>3</minutos_por_pedido><pct_tiempo>27.3</pct_tiempo><capacidad_hora>60</capacidad_hora></etapa><etapa><etapa>despacho</etapa><minutos_por_pedido>2</minutos_por_pedido><pct_tiempo>18.2</pct_tiempo><capacidad_hora>90</capacidad_hora></etapa><etapa><etapa>reparto</etapa><minutos_por_pedido>8.4</minutos_por_pedido><pct_tiempo xsi:nil="true" /><capacidad_hora>21.5</capacidad_hora></etapa></etapas><operadores_requeridos>2</operadores_requeridos><repartidores_requeridos>1</repartidores_requeridos><holgura_pedidos_dia>90</holgura_pedidos_dia><formula>3 operadores × 5.45 pedidos/h combinados; 3 repartidores × 7.17 entregas/h</formula><supuestos_usados><supuesto><clave>umbral_utilizacion_estable</clave><valor>70</valor><modificado>false</modificado></supuesto><supuesto><clave>umbral_utilizacion_riesgo</clave><valor>85</valor><modificado>false</modificado></supuesto><supuesto><clave>cap_factor_pico</clave><valor>1.35</valor><modificado>false</modificado></supuesto><supuesto><clave>picking_pedidos_hora</clave><valor>10</valor><modificado>false</modificado></supuesto><supuesto><clave>packing_pedidos_hora</clave><valor>20</valor><modificado>false</modificado></supuesto><supuesto><clave>despacho_pedidos_hora</clave><valor>30</valor><modificado>false</modificado></supuesto><supuesto><clave>velocidad_reparto_kmh</clave><valor>22</valor><modificado>false</modificado></supuesto><supuesto><clave>tiempo_servicio_min</clave><valor>4</valor><modificado>false</modificado></supuesto><supuesto><clave>paradas_por_viaje</clave><valor>3</valor><modificado>false</modificado></supuesto></supuestos_usados></capacidad_microhub>
```

### CAP-07 · Simular más personal · PASA

**Objetivo.** Qué pasa con 120 pedidos al día y 6 operadores y 6 repartidores.

**Petición.** `POST http://capacidad:5117/api/v1/capacidad/simulaciones`

```http
Accept: application/json
X-Traza-Id: e189147c-f60c-458b-99e9-782eee8b0038
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

**Respuesta.** HTTP 200 (esperado 200) · 45 ms · traza `e189147c-f60c-458b-99e9-782eee8b0038`

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
X-Traza-Id: ae2f8a71-2945-4930-9846-0d5effa75ac0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 55 ms · traza `ae2f8a71-2945-4930-9846-0d5effa75ac0`

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
X-Traza-Id: 62717109-ade1-435f-a131-022e8f4f03f3
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

**Respuesta.** HTTP 200 (esperado 200) · 61 ms · traza `62717109-ade1-435f-a131-022e8f4f03f3`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "operadores": 4,
  "repartidores": 3,
  "capacidad_fisica": 150,
  "actualizado_en": "2026-10-20T00:43:33-06:00"
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
      "actualizado_en": "2026-10-20T06:32:45.094659+00:00"
    },
    "valores_nuevos": {
      "operadores": 4,
      "actualizado_en": "2026-10-20T06:43:33.083843+00:00"
    }
  }
]
```

### CAP-10 · Cambiar el personal sin permiso · PASA

**Objetivo.** El operador no tiene capacidad.editar.

**Petición.** `PUT http://capacidad:5117/api/v1/capacidad/recursos/1`

```http
Accept: application/json
X-Traza-Id: 8efc87c1-4438-4ce8-96da-56ca02c59cf9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "operadores": 9,
  "repartidores": 9
}
```

**Respuesta.** HTTP 403 (esperado 403) · 30 ms · traza `8efc87c1-4438-4ce8-96da-56ca02c59cf9`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "8efc87c1-4438-4ce8-96da-56ca02c59cf9"
  }
}
```

### CAP-11 · Personal inválido · PASA

**Objetivo.** Al menos un operador.

**Petición.** `PUT http://capacidad:5117/api/v1/capacidad/recursos/1`

```http
Accept: application/json
X-Traza-Id: 14917aa3-c6e3-489c-9b83-b2cecc97c606
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "operadores": 0,
  "repartidores": 3
}
```

**Respuesta.** HTTP 422 (esperado 422) · 8 ms · traza `14917aa3-c6e3-489c-9b83-b2cecc97c606`

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
    "traza_id": "14917aa3-c6e3-489c-9b83-b2cecc97c606"
  }
}
```

### CAP-12 · Supuestos de la capacidad · PASA

**Objetivo.** Productividad por etapa, umbrales y horas del turno.

**Petición.** `GET http://capacidad:5117/api/v1/capacidad/supuestos`

```http
Accept: application/json
X-Traza-Id: 8cf9e53e-1952-4a84-ab1d-d99889b9347f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 61 ms · traza `8cf9e53e-1952-4a84-ab1d-d99889b9347f`

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
X-Traza-Id: c292db54-89e4-424d-85e0-96a557bd5f93
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 93 ms · traza `c292db54-89e4-424d-85e0-96a557bd5f93`

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
X-Traza-Id: 86eb9bb9-f509-4301-9deb-9931d878bba4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 39 ms · traza `86eb9bb9-f509-4301-9deb-9931d878bba4`

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
X-Traza-Id: 77e3a86e-2f99-44c3-ae74-0d74c5dd4d7e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 81 ms · traza `77e3a86e-2f99-44c3-ae74-0d74c5dd4d7e`

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
X-Traza-Id: e74b09ce-3853-4506-83e7-30c50f493876
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 75 ms · traza `e74b09ce-3853-4506-83e7-30c50f493876`

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
X-Traza-Id: 2ff46dca-cfb4-4aaf-b42c-8f7f4ed77f76
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 75 ms · traza `2ff46dca-cfb4-4aaf-b42c-8f7f4ed77f76`

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
X-Traza-Id: a7dbb91f-595c-42de-8bf0-e849f2842f7e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 121 ms · traza `a7dbb91f-595c-42de-8bf0-e849f2842f7e`

```xml
<?xml version='1.0' encoding='utf-8'?>
<costos_unitarios xmlns="urn:microhubs:v1" version="1"><entrada><ambito>microhub</ambito><ambito_id>1</ambito_id><origen>costos</origen><pedidos_mes>1800</pedidos_mes><ticket>135.00</ticket><margen_bruto>0.28</margen_bruto><distancia_km>2.4</distancia_km><paradas_por_viaje>3</paradas_por_viaje><valores_modificados /></entrada><fijos_mes>69500.00</fijos_mes><costo_fijo_pedido>38.61</costo_fijo_pedido><variable_pedido>3.50</variable_pedido><comision_pedido>3.92</comision_pedido><costo_entrega>25.20</costo_entrega><costo_variable_pedido>32.62</costo_variable_pedido><costo_por_pedido>71.23</costo_por_pedido><supuestos_usados><supuesto><clave>pedidos_mes</clave><valor>1800</valor><modificado>false</modificado></supuesto><supuesto><clave>ticket</clave><valor>135</valor><modificado>false</modificado></supuesto><supuesto><clave>margen_bruto</clave><valor>0.28</valor><modificado>false</modificado></supuesto><supuesto><clave>distancia_km</clave><valor>2.4</valor><modificado>false</modificado></supuesto><supuesto><clave>paradas_por_viaje</clave><valor>3</valor><modificado>false</modificado></supuesto><supuesto><clave>costo_base_entrega</clave><valor>18</valor><modificado>false</modificado></supuesto><supuesto><clave>costo_km_reparto</clave><valor>4.5</valor><modificado>false</modificado></supuesto></supuestos_usados></costos_unitarios>
```

### COS-07 · El operador consulta costos · PASA

**Objetivo.** Sin costos.ver.

**Petición.** `GET http://costos:5119/api/v1/costos/conceptos`

```http
Accept: application/json
X-Traza-Id: 7dcb15fb-1530-480d-90b7-5d1a39bcb9c1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 68 ms · traza `7dcb15fb-1530-480d-90b7-5d1a39bcb9c1`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "7dcb15fb-1530-480d-90b7-5d1a39bcb9c1"
  }
}
```

### COS-08 · Alta de un concepto sin permiso · PASA

**Objetivo.** Un auditor consulta, no edita.

**Petición.** `POST http://costos:5119/api/v1/costos/conceptos`

```http
Accept: application/json
X-Traza-Id: ea8ba2d9-d640-43c6-b659-a0f996ec1dfb
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

**Respuesta.** HTTP 403 (esperado 403) · 36 ms · traza `ea8ba2d9-d640-43c6-b659-a0f996ec1dfb`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "ea8ba2d9-d640-43c6-b659-a0f996ec1dfb"
  }
}
```

### COS-09 · Alta de un concepto · PASA

**Objetivo.** Costo fijo de un microhub con su justificación.

**Petición.** `POST http://costos:5119/api/v1/costos/conceptos`

```http
Accept: application/json
X-Traza-Id: 6052ff35-d20f-459c-b972-891da7691363
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

**Respuesta.** HTTP 201 (esperado 201) · 66 ms · traza `6052ff35-d20f-459c-b972-891da7691363`

```json
{
  "id": 39,
  "ambito": "microhub",
  "ambito_id": 1,
  "nombre": "Evidencia de vigilancia",
  "categoria": "servicios",
  "tipo": "fijo",
  "unidad": "mes",
  "monto": 1500.0,
  "vigente_desde": "2026-10-20",
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
    "id": 39,
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

**Petición.** `PUT http://costos:5119/api/v1/costos/conceptos/39`

```http
Accept: application/json
X-Traza-Id: 07d00c0e-2bc3-4653-b10c-33a6b717ea95
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "monto": 1800.0,
  "justificacion": "Se ajustó el monto en la evidencia"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 107 ms · traza `07d00c0e-2bc3-4653-b10c-33a6b717ea95`

```json
{
  "id": 39,
  "ambito": "microhub",
  "ambito_id": 1,
  "nombre": "Evidencia de vigilancia",
  "categoria": "servicios",
  "tipo": "fijo",
  "unidad": "mes",
  "monto": 1800.0,
  "vigente_desde": "2026-10-20",
  "vigente_hasta": null,
  "estatus": "activo",
  "fuente": "supuesto",
  "justificacion": "Se ajustó el monto en la evidencia"
}
```

### COS-16 · Cambiar con PATCH · PASA

**Objetivo.** PATCH es alias de PUT: lo usa la app Android cuando la JVM no admite PUT con cuerpo parcial.

**Petición.** `PATCH http://costos:5119/api/v1/costos/conceptos/39`

```http
Accept: application/json
X-Traza-Id: b5f15fda-d486-413f-b95b-7695a829ceab
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "monto": 1900.0,
  "justificacion": "Segundo ajuste del monto en la evidencia"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 85 ms · traza `b5f15fda-d486-413f-b95b-7695a829ceab`

```json
{
  "id": 39,
  "ambito": "microhub",
  "ambito_id": 1,
  "nombre": "Evidencia de vigilancia",
  "categoria": "servicios",
  "tipo": "fijo",
  "unidad": "mes",
  "monto": 1900.0,
  "vigente_desde": "2026-10-20",
  "vigente_hasta": null,
  "estatus": "activo",
  "fuente": "supuesto",
  "justificacion": "Segundo ajuste del monto en la evidencia"
}
```

### COS-11 · Dar de baja un concepto · PASA

**Objetivo.** Baja lógica: el renglón se conserva para la historia.

**Petición.** `DELETE http://costos:5119/api/v1/costos/conceptos/39`

```http
Accept: application/json
X-Traza-Id: ceedccb9-e4e7-474c-b64a-30b5ff1f3ccc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 43 ms · traza `ceedccb9-e4e7-474c-b64a-30b5ff1f3ccc`

```json
(sin cuerpo)
```

**Evidencia en PostgreSQL.** `SELECT id, estatus FROM costo_concepto WHERE id = %s`

```json
[
  {
    "id": 39,
    "estatus": "inactivo"
  }
]
```

### COS-12 · Fijo con unidad variable · PASA

**Objetivo.** Un costo fijo se da por mes.

**Petición.** `POST http://costos:5119/api/v1/costos/conceptos`

```http
Accept: application/json
X-Traza-Id: 8e2d0e18-fee6-47b1-bb69-56cef4c5df98
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

**Respuesta.** HTTP 422 (esperado 422) · 8 ms · traza `8e2d0e18-fee6-47b1-bb69-56cef4c5df98`

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
    "traza_id": "8e2d0e18-fee6-47b1-bb69-56cef4c5df98"
  }
}
```

### COS-13 · Microhub inexistente · PASA

**Objetivo.** El ámbito debe existir.

**Petición.** `POST http://costos:5119/api/v1/costos/conceptos`

```http
Accept: application/json
X-Traza-Id: 0bfdc589-4310-4020-a59f-1664b69feecf
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

**Respuesta.** HTTP 422 (esperado 422) · 7 ms · traza `0bfdc589-4310-4020-a59f-1664b69feecf`

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
    "traza_id": "0bfdc589-4310-4020-a59f-1664b69feecf"
  }
}
```

### COS-14 · Costos de una ubicación candidata · PASA

**Objetivo.** Sin conceptos propios toma renta, nómina y servicios de la ubicación (planeación).

**Petición.** `GET http://costos:5119/api/v1/costos/resumen?candidato_id=3`

```http
Accept: application/json
X-Traza-Id: de245afe-c1f0-4cd4-b563-d635715f288b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 57 ms · traza `de245afe-c1f0-4cd4-b563-d635715f288b`

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

**Objetivo.** Costo por km, pago por entrega, paradas por viaje y volumen de referencia.

**Petición.** `GET http://costos:5119/api/v1/costos/supuestos`

```http
Accept: application/json
X-Traza-Id: 977df95d-c5ad-45d1-933b-3be269bcfc6e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 31 ms · traza `977df95d-c5ad-45d1-933b-3be269bcfc6e`

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
X-Traza-Id: 6cbea276-e5a1-4971-9adb-a216a103157c
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

**Respuesta.** HTTP 200 (esperado 200) · 29 ms · traza `6cbea276-e5a1-4971-9adb-a216a103157c`

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
X-Traza-Id: d3b4be8e-9014-42f5-9528-663eb67b5665
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

**Respuesta.** HTTP 200 (esperado 200) · 37 ms · traza `d3b4be8e-9014-42f5-9528-663eb67b5665`

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
X-Traza-Id: c066a7ed-5eb9-473e-8a76-e08c5c3d9ed9
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

**Respuesta.** HTTP 200 (esperado 200) · 30 ms · traza `c066a7ed-5eb9-473e-8a76-e08c5c3d9ed9`

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
X-Traza-Id: 255217cb-311e-4ff2-9e54-c1ab0509bcf5
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

**Respuesta.** HTTP 200 (esperado 200) · 31 ms · traza `255217cb-311e-4ff2-9e54-c1ab0509bcf5`

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
X-Traza-Id: 3100280b-9e6b-4d53-b93d-282fb7df17ce
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1
}
```

**Respuesta.** HTTP 200 (esperado 200) · 245 ms · traza `3100280b-9e6b-4d53-b93d-282fb7df17ce`

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
    "costo_variable_pedido": 32.6,
    "ticket": 134.57,
    "margen_bruto": 0.28,
    "pedidos_dia": 22.95,
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
  "margen_pedido": 5.08,
  "equilibrio_mensual": 13682.18,
  "equilibrio_diario": 456.07,
  "ingresos_equilibrio_mes": 1841210.92,
  "diferencia_pedidos_dia": -433.12,
  "margen_seguridad_pct": -94.97,
  "utilidad_dia": -2200.06,
  "utilidad_mes": -66001.93,
  "decision": "no_viable",
  "explicacion": [
    "la demanda esperada (23.0 pedidos/día) no alcanza el equilibrio (456.1 pedidos/día)"
  ],
  "pasos": [
    "Margen por pedido = ticket × margen bruto − costo de entrega = 134.57 × 28.00% − 32.60 = 5.08",
    "Punto de equilibrio mensual = costos fijos ÷ margen por pedido = 69,500.00 ÷ 5.08 = 13,682 pedidos/mes",
    "Punto de equilibrio diario = 13,682 ÷ 30 días = 456.1 pedidos/día"
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
X-Traza-Id: fbb59bf9-0728-48ea-911f-272badd40e72
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "ticket": 200
}
```

**Respuesta.** HTTP 200 (esperado 200) · 237 ms · traza `fbb59bf9-0728-48ea-911f-272badd40e72`

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
    "pedidos_dia": 22.95,
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
  "diferencia_pedidos_dia": -84.8,
  "margen_seguridad_pct": -78.7,
  "utilidad_dia": -1823.13,
  "utilidad_mes": -54694.02,
  "decision": "no_viable",
  "explicacion": [
    "la demanda esperada (23.0 pedidos/día) no alcanza el equilibrio (107.8 pedidos/día)"
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
X-Traza-Id: 797a7f75-1ab1-44d8-b267-c877baf3e8b6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "pedidos_dia": 10
}
```

**Respuesta.** HTTP 422 (esperado 422) · 145 ms · traza `797a7f75-1ab1-44d8-b267-c877baf3e8b6`

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
    "traza_id": "797a7f75-1ab1-44d8-b267-c877baf3e8b6"
  }
}
```

### EQU-08 · Sensibilidad · PASA

**Objetivo.** Cada variable sube y baja 10 y 20 %; se ordenan por lo que mueven la utilidad.

**Petición.** `POST http://punto-equilibrio:5120/api/v1/punto-equilibrio/sensibilidad`

```http
Accept: application/json
X-Traza-Id: a5d29231-cbfb-4bb9-942b-637ff5c7f6fa
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

**Respuesta.** HTTP 200 (esperado 200) · 33 ms · traza `a5d29231-cbfb-4bb9-942b-637ff5c7f6fa`

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
X-Traza-Id: db45bfa2-6783-4856-b82c-9905c5cc1af1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><equilibrio_calculo_nuevo xmlns="urn:microhubs:v1"><pedidos_dia>45</pedidos_dia><ticket>135</ticket><margen_bruto>0.28</margen_bruto><costos_fijos>60000</costos_fijos><costo_variable_pedido>32.6</costo_variable_pedido></equilibrio_calculo_nuevo>
```

**Respuesta.** HTTP 200 (esperado 200) · 36 ms · traza `db45bfa2-6783-4856-b82c-9905c5cc1af1`

```xml
<?xml version='1.0' encoding='utf-8'?>
<equilibrio_calculo xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id xsi:nil="true" /><nombre xsi:nil="true" /><objeto><tipo>manual</tipo><id xsi:nil="true" /><nombre xsi:nil="true" /></objeto><entrada><costos_fijos_mes>60000</costos_fijos_mes><costo_variable_pedido>32.6</costo_variable_pedido><ticket>135</ticket><margen_bruto>0.28</margen_bruto><pedidos_dia>45</pedidos_dia><dias_mes>30</dias_mes><margen_seguridad_minimo_pct>15</margen_seguridad_minimo_pct><origen><costos_fijos>manual</costos_fijos><costo_variable_pedido>manual</costo_variable_pedido><ticket>manual</ticket><margen_bruto>manual</margen_bruto><pedidos_dia>manual</pedidos_dia></origen></entrada><margen_pedido>5.2</margen_pedido><equilibrio_mensual>11538.46</equilibrio_mensual><equilibrio_diario>384.62</equilibrio_diario><ingresos_equilibrio_mes>1557692.31</ingresos_equilibrio_mes><diferencia_pedidos_dia>-339.62</diferencia_pedidos_dia><margen_seguridad_pct>-88.3</margen_seguridad_pct><utilidad_dia>-1766</utilidad_dia><utilidad_mes>-52980</utilidad_mes><decision>no_viable</decision><explicacion><motivo>la demanda esperada (45.0 pedidos/día) no alcanza el equilibrio (384.6 pedidos/día)</motivo></explicacion><pasos><paso>Margen por pedido = ticket × margen bruto − costo de entrega = 135.00 × 28.00% − 32.60 = 5.20</paso><paso>Punto de equilibrio mensual = costos fijos ÷ margen por pedido = 60,000.00 ÷ 5.20 = 11,538 pedidos/mes</paso><paso>Punto de equilibrio diario = 11,538 ÷ 30 días = 384.6 pedidos/día</paso></pasos><supuestos_usados><supuesto><clave>peq_margen_seguridad_pct</clave><valor>15</valor><modificado>false</modificado></supuesto><supuesto><clave>dias_operacion_mes</clave><valor>30</valor><modificado>false</modificado></supuesto><supuesto><clave>margen_bruto_default</clave><valor>0.28</valor><modificado>false</modificado></supuesto></supuestos_usados></equilibrio_calculo>
```

### EQU-10 · Guardar sin permiso · PASA

**Objetivo.** Guardar un escenario exige equilibrio.editar.

**Petición.** `POST http://punto-equilibrio:5120/api/v1/punto-equilibrio/calculos`

```http
Accept: application/json
X-Traza-Id: 6579b79a-f06b-4f94-be7e-e3ad75c2ea21
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

**Respuesta.** HTTP 403 (esperado 403) · 5 ms · traza `6579b79a-f06b-4f94-be7e-e3ad75c2ea21`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Guardar un escenario exige el permiso equilibrio.editar.",
    "traza_id": "6579b79a-f06b-4f94-be7e-e3ad75c2ea21"
  }
}
```

### EQU-11 · Guardar «Evidencia equilibrio A» · PASA

**Objetivo.** Queda en equilibrio_escenario con su cálculo completo.

**Petición.** `POST http://punto-equilibrio:5120/api/v1/punto-equilibrio/calculos`

```http
Accept: application/json
X-Traza-Id: d7570ed3-e661-4899-a859-d551134f9520
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

**Respuesta.** HTTP 201 (esperado 201) · 74 ms · traza `d7570ed3-e661-4899-a859-d551134f9520`

```json
{
  "id": 22,
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
    "id": 22,
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
X-Traza-Id: a68edd84-dea4-4664-91dd-ab6ad9314a04
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

**Respuesta.** HTTP 201 (esperado 201) · 68 ms · traza `a68edd84-dea4-4664-91dd-ab6ad9314a04`

```json
{
  "id": 23,
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
    "id": 23,
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
X-Traza-Id: 9f302b05-9532-4a54-9fd4-86ed67299b16
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 43 ms · traza `9f302b05-9532-4a54-9fd4-86ed67299b16`

```json
{
  "datos": [
    {
      "id": 23,
      "nombre": "Evidencia equilibrio B",
      "microhub_id": null,
      "candidato_id": null,
      "decision": "viable",
      "equilibrio_diario": 53.33,
      "pedidos_dia": 80.0,
      "utilidad_mes": 20000.0,
      "creado_por": 5,
      "creado_en": "2026-10-20T00:43:35-06:00"
    },
    {
      "id": 22,
      "nombre": "Evidencia equilibrio A",
      "microhub_id": null,
      "candidato_id": null,
      "decision": "no_viable",
      "equilibrio_diario": 53.33,
      "pedidos_dia": 45.0,
      "utilidad_mes": -6250.0,
      "creado_por": 5,
      "creado_en": "2026-10-20T00:43:35-06:00"
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

**Petición.** `GET http://punto-equilibrio:5120/api/v1/punto-equilibrio/comparacion?ids=22,23`

```http
Accept: application/json
X-Traza-Id: f4486a82-7a4f-4140-908b-99c45289d5f4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 46 ms · traza `f4486a82-7a4f-4140-908b-99c45289d5f4`

```json
{
  "filas": [
    {
      "id": 22,
      "nombre": "Evidencia equilibrio A",
      "decision": "no_viable",
      "pedidos_dia": 45.0,
      "equilibrio_diario": 53.33,
      "diferencia_pedidos_dia": -8.33,
      "margen_seguridad_pct": -15.62,
      "utilidad_mes": -6250.0
    },
    {
      "id": 23,
      "nombre": "Evidencia equilibrio B",
      "decision": "viable",
      "pedidos_dia": 80.0,
      "equilibrio_diario": 53.33,
      "diferencia_pedidos_dia": 26.67,
      "margen_seguridad_pct": 50.0,
      "utilidad_mes": 20000.0
    }
  ],
  "mejor_utilidad_id": 23,
  "mejor_utilidad_nombre": "Evidencia equilibrio B"
}
```

### EQU-15 · Abrir un escenario · PASA

**Objetivo.** Con su cálculo paso a paso.

**Petición.** `GET http://punto-equilibrio:5120/api/v1/punto-equilibrio/escenarios/22`

```http
Accept: application/json
X-Traza-Id: b99f0c62-ff2e-4d35-83f2-0c2255ba1806
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 24 ms · traza `b99f0c62-ff2e-4d35-83f2-0c2255ba1806`

```json
{
  "id": 22,
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

**Petición.** `DELETE http://punto-equilibrio:5120/api/v1/punto-equilibrio/escenarios/22`

```http
Accept: application/json
X-Traza-Id: 5750fb16-5983-4210-aa27-0344e31ab763
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 29 ms · traza `5750fb16-5983-4210-aa27-0344e31ab763`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "5750fb16-5983-4210-aa27-0344e31ab763"
  }
}
```

### EQU-17 · Borrar un escenario · PASA

**Objetivo.** Se elimina el escenario.

**Petición.** `DELETE http://punto-equilibrio:5120/api/v1/punto-equilibrio/escenarios/22`

```http
Accept: application/json
X-Traza-Id: 7f832a93-cecc-411d-a12b-ff751fd7a2de
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 35 ms · traza `7f832a93-cecc-411d-a12b-ff751fd7a2de`

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
X-Traza-Id: c2ca98ad-3b74-44d8-90a9-5799a5b6e1d0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 426 ms · traza `c2ca98ad-3b74-44d8-90a9-5799a5b6e1d0`

```json
{
  "datos": [
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "costos_fijos_mes": 69500.0,
      "margen_pedido": 5.08,
      "equilibrio_diario": 456.07,
      "pedidos_dia": 22.95,
      "diferencia_pedidos_dia": -433.12,
      "utilidad_mes": -66001.93,
      "decision": "no_viable"
    },
    {
      "microhub": {
        "id": 2,
        "nombre": "Microhub Valles"
      },
      "costos_fijos_mes": 66500.0,
      "margen_pedido": 5.08,
      "equilibrio_diario": 436.39,
      "pedidos_dia": 15.75,
      "diferencia_pedidos_dia": -420.64,
      "utilidad_mes": -64099.89,
      "decision": "no_viable"
    },
    {
      "microhub": {
        "id": 3,
        "nombre": "Microhub Poniente F-113"
      },
      "costos_fijos_mes": 50000.0,
      "margen_pedido": 5.08,
      "equilibrio_diario": 328.11,
      "pedidos_dia": 9.57,
      "diferencia_pedidos_dia": -318.54,
      "utilidad_mes": -48542.41,
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
X-Traza-Id: 871cb105-a29e-40a6-96df-2f7aaf14a5a1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 31 ms · traza `871cb105-a29e-40a6-96df-2f7aaf14a5a1`

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
X-Traza-Id: d74d82ec-b202-4e19-a199-2391d314b407
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 353 ms · traza `d74d82ec-b202-4e19-a199-2391d314b407`

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
      "productos": 30,
      "unidades": 172,
      "venta": 4960.0,
      "pct_unidades": 81.1,
      "pct_venta": 78.3
    },
    {
      "clase": "B",
      "productos": 13,
      "unidades": 31,
      "venta": 1081.5,
      "pct_unidades": 14.6,
      "pct_venta": 17.1
    },
    {
      "clase": "C",
      "productos": 8,
      "unidades": 9,
      "venta": 297.0,
      "pct_unidades": 4.2,
      "pct_venta": 4.7
    }
  ],
  "filas": [
    {
      "producto": {
        "id": 7,
        "clave_interna": "AB-007",
        "nombre": "Harina de trigo"
      },
      "clase": "A",
      "unidades": 10,
      "venta": 245.0,
      "pct_acum": 4.7
    },
    {
      "producto": {
        "id": 28,
        "clave_interna": "BE-008",
        "nombre": "Polvo para agua de sabor"
      },
      "clase": "A",
      "unidades": 10,
      "venta": 75.0,
      "pct_acum": 9.4
    },
    {
      "producto": {
        "id": 13,
        "clave_interna": "AB-013",
        "nombre": "Puré de tomate"
      },
      "clase": "A",
      "unidades": 9,
      "venta": 99.0,
      "pct_acum": 13.7
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
      "pct_acum": 17.9
    },
    {
      "producto": {
        "id": 39,
        "clave_interna": "LI-003",
        "nombre": "Cloro"
      },
      "clase": "A",
      "unidades": 8,
      "venta": 156.0,
      "pct_acum": 21.7
    },
    {
      "producto": {
        "id": 48,
        "clave_interna": "HI-003",
        "nombre": "Pasta dental"
      },
      "clase": "A",
      "unidades": 7,
      "venta": 224.0,
      "pct_acum": 25.0
    },
    {
      "producto": {
        "id": 1,
        "clave_interna": "AB-001",
        "nombre": "Frijol negro a granel"
      },
      "clase": "A",
      "unidades": 6,
      "venta": 231.0,
      "pct_acum": 27.8
    },
    {
      "producto": {
        "id": 12,
        "clave_interna": "AB-012",
        "nombre": "Chiles jalapeños en escabeche"
      },
      "clase": "A",
      "unidades": 6,
      "venta": 117.0,
      "pct_acum": 30.7
    },
    {
      "producto": {
        "id": 29,
        "clave_interna": "LA-001",
        "nombre": "Leche entera"
      },
      "clase": "A",
      "unidades": 6,
      "venta": 165.0,
      "pct_acum": 33.5
    },
    {
      "producto": {
        "id": 30,
        "clave_interna": "LA-002",
        "nombre": "Leche deslactosada"
      },
      "clase": "A",
      "unidades": 6,
      "venta": 186.0,
      "pct_acum": 36.3
    },
    {
      "producto": {
        "id": 40,
        "clave_interna": "LI-004",
        "nombre": "Limpiador multiusos"
      },
      "clase": "A",
      "unidades": 6,
      "venta": 168.0,
      "pct_acum": 39.2
    },
    {
      "producto": {
        "id": 51,
        "clave_interna": "HI-006",
        "nombre": "Pañal etapa 3"
      },
      "clase": "A",
      "unidades": 6,
      "venta": 408.0,
      "pct_acum": 42.0
    },
    {
      "producto": {
        "id": 2,
        "clave_interna": "AB-002",
        "nombre": "Arroz superextra"
      },
      "clase": "A",
      "unidades": 5,
      "venta": 149.5,
      "pct_acum": 44.3
    },
    {
      "producto": {
        "id": 3,
        "clave_interna": "AB-003",
        "nombre": "Aceite vegetal"
      },
      "clase": "A",
      "unidades": 5,
      "venta": 210.0,
      "pct_acum": 46.7
    },
    {
      "producto": {
        "id": 11,
        "clave_interna": "AB-011",
        "nombre": "Frijoles refritos"
      },
      "clase": "A",
      "unidades": 5,
      "venta": 115.0,
      "pct_acum": 49.1
    },
    {
      "producto": {
        "id": 14,
        "clave_interna": "AB-014",
        "nombre": "Café soluble"
      },
      "clase": "A",
      "unidades": 5,
      "venta": 260.0,
      "pct_acum": 51.4
    },
    {
      "producto": {
        "id": 20,
        "clave_interna": "AB-020",
        "nombre": "Lenteja"
      },
      "clase": "A",
      "unidades": 5,
      "venta": 120.0,
      "pct_acum": 53.8
    },
    {
      "producto": {
        "id": 34,
        "clave_interna": "LA-006",
        "nombre": "Yogur natural"
      },
      "clase": "A",
      "unidades": 5,
      "venta": 220.0,
      "pct_acum": 56.1
    },
    {
      "producto": {
        "id": 35,
        "clave_interna": "LA-007",
        "nombre": "Mantequilla"
      },
      "clase": "A",
      "unidades": 5,
      "venta": 110.0,
      "pct_acum": 58.5
    },
    {
      "producto": {
        "id": 41,
        "clave_interna": "LI-005",
        "nombre": "Suavizante de telas"
      },
      "clase": "A",
      "unidades": 5,
      "venta": 165.0,
      "pct_acum": 60.8
    },
    {
      "producto": {
        "id": 44,
        "clave_interna": "LI-008",
        "nombre": "Bolsas para basura"
      },
      "clase": "A",
      "unidades": 5,
      "venta": 120.0,
      "pct_acum": 63.2
    },
    {
      "producto": {
        "id": 45,
        "clave_interna": "LI-009",
        "nombre": "Fibra para trastes"
      },
      "clase": "A",
      "unidades": 5,
      "venta": 90.0,
      "pct_acum": 65.6
    },
    {
      "producto": {
        "id": 46,
        "clave_interna": "HI-001",
        "nombre": "Jabón de tocador"
      },
      "clase": "A",
      "unidades": 5,
      "venta": 72.5,
      "pct_acum": 67.9
    },
    {
      "producto": {
        "id": 4,
        "clave_interna": "AB-004",
        "nombre": "Azúcar estándar"
      },
      "clase": "A",
      "unidades": 4,
      "venta": 114.0,
      "pct_acum": 69.8
    },
    {
      "producto": {
        "id": 5,
        "clave_interna": "AB-005",
        "nombre": "Sal de mesa"
      },
      "clase": "A",
      "unidades": 4,
      "venta": 56.0,
      "pct_acum": 71.7
    },
    {
      "producto": {
        "id": 6,
        "clave_interna": "AB-006",
        "nombre": "Harina de maíz nixtamalizado"
      },
      "clase": "A",
      "unidades": 4,
      "venta": 104.0,
      "pct_acum": 73.6
    },
    {
      "producto": {
        "id": 10,
        "clave_interna": "AB-010",
        "nombre": "Sardina en salsa de tomate"
      },
      "clase": "A",
      "unidades": 4,
      "venta": 106.0,
      "pct_acum": 75.5
    },
    {
      "producto": {
        "id": 17,
        "clave_interna": "AB-017",
        "nombre": "Tortillas de maíz"
      },
      "clase": "A",
      "unidades": 4,
      "venta": 96.0,
      "pct_acum": 77.4
    },
    {
      "producto": {
        "id": 25,
        "clave_interna": "BE-005",
        "nombre": "Jugo de naranja"
      },
      "clase": "A",
      "unidades": 4,
      "venta": 112.0,
      "pct_acum": 79.2
    },
    {
      "producto": {
        "id": 32,
        "clave_interna": "LA-004",
        "nombre": "Queso Oaxaca"
      },
      "clase": "A",
      "unidades": 4,
      "venta": 288.0,
      "pct_acum": 81.1
    },
    {
      "producto": {
        "id": 18,
        "clave_interna": "AB-018",
        "nombre": "Pan de caja blanco"
      },
      "clase": "B",
      "unidades": 3,
      "venta": 132.0,
      "pct_acum": 82.5
    },
    {
      "producto": {
        "id": 23,
        "clave_interna": "BE-003",
        "nombre": "Refresco de cola"
      },
      "clase": "B",
      "unidades": 3,
      "venta": 115.5,
      "pct_acum": 84.0
    },
    {
      "producto": {
        "id": 36,
        "clave_interna": "LA-008",
        "nombre": "Jamón de pavo"
      },
      "clase": "B",
      "unidades": 3,
      "venta": 138.0,
      "pct_acum": 85.4
    },
    {
      "producto": {
        "id": 47,
        "clave_interna": "HI-002",
        "nombre": "Shampoo"
      },
      "clase": "B",
      "unidades": 3,
      "venta": 162.0,
      "pct_acum": 86.8
    },
    {
      "producto": {
        "id": 49,
        "clave_interna": "HI-004",
        "nombre": "Desodorante"
      },
      "clase": "B",
      "unidades": 3,
      "venta": 144.0,
      "pct_acum": 88.2
    },
    {
      "producto": {
        "id": 8,
        "clave_interna": "AB-008",
        "nombre": "Pasta para sopa surtida"
      },
      "clase": "B",
      "unidades": 2,
      "venta": 19.0,
      "pct_acum": 89.2
    },
    {
      "producto": {
        "id": 15,
        "clave_interna": "AB-015",
        "nombre": "Avena en hojuelas"
      },
      "clase": "B",
      "unidades": 2,
      "venta": 54.0,
      "pct_acum": 90.1
    },
    {
      "producto": {
        "id": 16,
        "clave_interna": "AB-016",
        "nombre": "Galletas María"
      },
      "clase": "B",
      "unidades": 2,
      "venta": 33.0,
      "pct_acum": 91.0
    },
    {
      "producto": {
        "id": 22,
        "clave_interna": "BE-002",
        "nombre": "Agua embotellada"
      },
      "clase": "B",
      "unidades": 2,
      "venta": 30.0,
      "pct_acum": 92.0
    },
    {
      "producto": {
        "id": 24,
        "clave_interna": "BE-004",
        "nombre": "Refresco sabor manzana"
      },
      "clase": "B",
      "unidades": 2,
      "venta": 72.0,
      "pct_acum": 92.9
    },
    {
      "producto": {
        "id": 26,
        "clave_interna": "BE-006",
        "nombre": "Bebida de soya"
      },
      "clase": "B",
      "unidades": 2,
      "venta": 64.0,
      "pct_acum": 93.9
    },
    {
      "producto": {
        "id": 27,
        "clave_interna": "BE-007",
        "nombre": "Té helado de limón"
      },
      "clase": "B",
      "unidades": 2,
      "venta": 34.0,
      "pct_acum": 94.8
    },
    {
      "producto": {
        "id": 37,
        "clave_interna": "LI-001",
        "nombre": "Detergente en polvo"
      },
      "clase": "B",
      "unidades": 2,
      "venta": 84.0,
      "pct_acum": 95.8
    },
    {
      "producto": {
        "id": 42,
        "clave_interna": "LI-006",
        "nombre": "Papel higiénico"
      },
      "clase": "C",
      "unidades": 2,
      "venta": 76.0,
      "pct_acum": 96.7
    },
    {
      "producto": {
        "id": 43,
        "clave_interna": "LI-007",
        "nombre": "Servilletas"
      },
      "clase": "C",
      "unidades": 2,
      "venta": 64.0,
      "pct_acum": 97.6
    },
    {
      "producto": {
        "id": 9,
        "clave_interna": "AB-009",
        "nombre": "Atún en agua"
      },
      "clase": "C",
      "unidades": 1,
      "venta": 21.0,
      "pct_acum": 98.1
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
      "pct_acum": 98.6
    },
    {
      "producto": {
        "id": 33,
        "clave_interna": "LA-005",
        "nombre": "Crema ácida"
      },
      "clase": "C",
      "unidades": 1,
      "venta": 36.0,
      "pct_acum": 99.1
    },
    {
      "producto": {
        "id": 38,
        "clave_interna": "LI-002",
        "nombre": "Jabón para trastes"
      },
      "clase": "C",
      "unidades": 1,
      "venta": 26.0,
      "pct_acum": 99.5
    },
    {
      "producto": {
        "id": 50,
        "clave_interna": "HI-005",
        "nombre": "Toallas femeninas"
      },
      "clase": "C",
      "unidades": 1,
      "venta": 36.0,
      "pct_acum": 100.0
    },
    {
      "producto": {
        "id": 31,
        "clave_interna": "LA-003",
        "nombre": "Queso fresco"
      },
      "clase": "C",
      "unidades": 0,
      "venta": 0.0,
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
X-Traza-Id: 48c5208b-80c7-4640-9abc-5a2df13fa005
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 351 ms · traza `48c5208b-80c7-4640-9abc-5a2df13fa005`

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
    "reducir": 49,
    "eliminar": 1,
    "excluir": 0,
    "clase_a": 30,
    "clase_b": 13,
    "clase_c": 8,
    "unidades_a_comprar": 1,
    "con_costo_estimado": 51,
    "espacio": {
      "total": 3600.0,
      "ocupado": 2900.0,
      "sugerido": 1.0,
      "ocupacion_pct": 80.6
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
        "id": 7,
        "clave_interna": "AB-007",
        "nombre": "Harina de trigo"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 4.7,
      "unidades": 10,
      "venta": 245.0,
      "margen_unitario": 6.86,
      "margen_total": 68.6,
      "costo_estimado": true,
      "existencia": 14,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.11,
      "cobertura_dias": 126.0,
      "rotacion": 0.71,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 126 días, exceso de stock",
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
      "pct_acum": 9.4,
      "unidades": 10,
      "venta": 75.0,
      "margen_unitario": 2.1,
      "margen_total": 21.0,
      "costo_estimado": true,
      "existencia": 36,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.11,
      "cobertura_dias": 324.0,
      "rotacion": 0.28,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 324 días, exceso de stock",
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
      "pct_acum": 13.7,
      "unidades": 9,
      "venta": 99.0,
      "margen_unitario": 3.08,
      "margen_total": 27.72,
      "costo_estimado": true,
      "existencia": 56,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 560.0,
      "rotacion": 0.16,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 560 días, exceso de stock",
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
      "pct_acum": 17.9,
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
        "id": 39,
        "clave_interna": "LI-003",
        "nombre": "Cloro"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 21.7,
      "unidades": 8,
      "venta": 156.0,
      "margen_unitario": 5.46,
      "margen_total": 43.68,
      "costo_estimado": true,
      "existencia": 47,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 528.8,
      "rotacion": 0.17,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 529 días, exceso de stock",
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
      "pct_acum": 25.0,
      "unidades": 7,
      "venta": 224.0,
      "margen_unitario": 8.96,
      "margen_total": 62.72,
      "costo_estimado": true,
      "existencia": 80,
      "minimo": 10,
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
        "id": 1,
        "clave_interna": "AB-001",
        "nombre": "Frijol negro a granel"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 27.8,
      "unidades": 6,
      "venta": 231.0,
      "margen_unitario": 10.78,
      "margen_total": 64.68,
      "costo_estimado": true,
      "existencia": 60,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.07,
      "cobertura_dias": 900.0,
      "rotacion": 0.1,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 900 días, exceso de stock",
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
      "pct_acum": 30.7,
      "unidades": 6,
      "venta": 117.0,
      "margen_unitario": 5.46,
      "margen_total": 32.76,
      "costo_estimado": true,
      "existencia": 206,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.07,
      "cobertura_dias": 3090.0,
      "rotacion": 0.03,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 3090 días, exceso de stock",
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
      "pct_acum": 33.5,
      "unidades": 6,
      "venta": 165.0,
      "margen_unitario": 7.7,
      "margen_total": 46.2,
      "costo_estimado": true,
      "existencia": 48,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.07,
      "cobertura_dias": 720.0,
      "rotacion": 0.12,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 720 días, exceso de stock",
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
      "pct_acum": 36.3,
      "unidades": 6,
      "venta": 186.0,
      "margen_unitario": 8.68,
      "margen_total": 52.08,
      "costo_estimado": true,
      "existencia": 15,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.07,
      "cobertura_dias": 225.0,
      "rotacion": 0.4,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 225 días, exceso de stock",
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
      "pct_acum": 39.2,
      "unidades": 6,
      "venta": 168.0,
      "margen_unitario": 7.84,
      "margen_total": 47.04,
      "costo_estimado": true,
      "existencia": 16,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.07,
      "cobertura_dias": 240.0,
      "rotacion": 0.38,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 240 días, exceso de stock",
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
      "pct_acum": 42.0,
      "unidades": 6,
      "venta": 408.0,
      "margen_unitario": 19.04,
      "margen_total": 114.24,
      "costo_estimado": true,
      "existencia": 29,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.07,
      "cobertura_dias": 435.0,
      "rotacion": 0.21,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 435 días, exceso de stock",
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
      "pct_acum": 44.3,
      "unidades": 5,
      "venta": 149.5,
      "margen_unitario": 8.37,
      "margen_total": 41.85,
      "costo_estimado": true,
      "existencia": 35,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 630.0,
      "rotacion": 0.14,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 630 días, exceso de stock",
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
      "pct_acum": 46.7,
      "unidades": 5,
      "venta": 210.0,
      "margen_unitario": 11.76,
      "margen_total": 58.8,
      "costo_estimado": true,
      "existencia": 10,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 180.0,
      "rotacion": 0.5,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 180 días, exceso de stock",
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
      "pct_acum": 49.1,
      "unidades": 5,
      "venta": 115.0,
      "margen_unitario": 6.44,
      "margen_total": 32.2,
      "costo_estimado": true,
      "existencia": 31,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 558.0,
      "rotacion": 0.16,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 558 días, exceso de stock",
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
      "pct_acum": 51.4,
      "unidades": 5,
      "venta": 260.0,
      "margen_unitario": 14.56,
      "margen_total": 72.8,
      "costo_estimado": true,
      "existencia": 33,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 594.0,
      "rotacion": 0.15,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 594 días, exceso de stock",
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
      "pct_acum": 53.8,
      "unidades": 5,
      "venta": 120.0,
      "margen_unitario": 6.72,
      "margen_total": 33.6,
      "costo_estimado": true,
      "existencia": 79,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 1422.0,
      "rotacion": 0.06,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1422 días, exceso de stock",
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
      "pct_acum": 56.1,
      "unidades": 5,
      "venta": 220.0,
      "margen_unitario": 12.32,
      "margen_total": 61.6,
      "costo_estimado": true,
      "existencia": 13,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 234.0,
      "rotacion": 0.38,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 234 días, exceso de stock",
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
      "clase": "A",
      "pct_acum": 58.5,
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
      "clase": "A",
      "pct_acum": 60.8,
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
        "id": 44,
        "clave_interna": "LI-008",
        "nombre": "Bolsas para basura"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 63.2,
      "unidades": 5,
      "venta": 120.0,
      "margen_unitario": 6.72,
      "margen_total": 33.6,
      "costo_estimado": true,
      "existencia": 28,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 504.0,
      "rotacion": 0.18,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 504 días, exceso de stock",
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
      "pct_acum": 65.6,
      "unidades": 5,
      "venta": 90.0,
      "margen_unitario": 5.04,
      "margen_total": 25.2,
      "costo_estimado": true,
      "existencia": 46,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 828.0,
      "rotacion": 0.11,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 828 días, exceso de stock",
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
      "clase": "A",
      "pct_acum": 67.9,
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
      "clase": "A",
      "pct_acum": 69.8,
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
        "id": 5,
        "clave_interna": "AB-005",
        "nombre": "Sal de mesa"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 71.7,
      "unidades": 4,
      "venta": 56.0,
      "margen_unitario": 3.92,
      "margen_total": 15.68,
      "costo_estimado": true,
      "existencia": 30,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.04,
      "cobertura_dias": 675.0,
      "rotacion": 0.13,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 675 días, exceso de stock",
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
      "pct_acum": 73.6,
      "unidades": 4,
      "venta": 104.0,
      "margen_unitario": 7.28,
      "margen_total": 29.12,
      "costo_estimado": true,
      "existencia": 66,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.04,
      "cobertura_dias": 1485.0,
      "rotacion": 0.06,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1485 días, exceso de stock",
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
      "pct_acum": 75.5,
      "unidades": 4,
      "venta": 106.0,
      "margen_unitario": 7.42,
      "margen_total": 29.68,
      "costo_estimado": true,
      "existencia": 417,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.04,
      "cobertura_dias": 9382.5,
      "rotacion": 0.01,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 9382 días, exceso de stock",
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
      "pct_acum": 77.4,
      "unidades": 4,
      "venta": 96.0,
      "margen_unitario": 6.72,
      "margen_total": 26.88,
      "costo_estimado": true,
      "existencia": 21,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.04,
      "cobertura_dias": 472.5,
      "rotacion": 0.19,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 472 días, exceso de stock",
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
      "pct_acum": 79.2,
      "unidades": 4,
      "venta": 112.0,
      "margen_unitario": 7.84,
      "margen_total": 31.36,
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
        "id": 32,
        "clave_interna": "LA-004",
        "nombre": "Queso Oaxaca"
      },
      "categoria": "Lácteos y huevo",
      "clase": "A",
      "pct_acum": 81.1,
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
        "id": 18,
        "clave_interna": "AB-018",
        "nombre": "Pan de caja blanco"
      },
      "categoria": "Abarrote básico",
      "clase": "B",
      "pct_acum": 82.5,
      "unidades": 3,
      "venta": 132.0,
      "margen_unitario": 12.32,
      "margen_total": 36.96,
      "costo_estimado": true,
      "existencia": 80,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.03,
      "cobertura_dias": 2400.0,
      "rotacion": 0.04,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 2400 días, exceso de stock",
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
      "pct_acum": 84.0,
      "unidades": 3,
      "venta": 115.5,
      "margen_unitario": 10.78,
      "margen_total": 32.34,
      "costo_estimado": true,
      "existencia": 54,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.03,
      "cobertura_dias": 1620.0,
      "rotacion": 0.06,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1620 días, exceso de stock",
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
      "clase": "B",
      "pct_acum": 85.4,
      "unidades": 3,
      "venta": 138.0,
      "margen_unitario": 12.88,
      "margen_total": 38.64,
      "costo_estimado": true,
      "existencia": 47,
      "minimo": 8,
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
        "id": 47,
        "clave_interna": "HI-002",
        "nombre": "Shampoo"
      },
      "categoria": "Higiene personal",
      "clase": "B",
      "pct_acum": 86.8,
      "unidades": 3,
      "venta": 162.0,
      "margen_unitario": 15.12,
      "margen_total": 45.36,
      "costo_estimado": true,
      "existencia": 62,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.03,
      "cobertura_dias": 1860.0,
      "rotacion": 0.05,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1860 días, exceso de stock",
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
      "pct_acum": 88.2,
      "unidades": 3,
      "venta": 144.0,
      "margen_unitario": 13.44,
      "margen_total": 40.32,
      "costo_estimado": true,
      "existencia": 36,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.03,
      "cobertura_dias": 1080.0,
      "rotacion": 0.08,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1080 días, exceso de stock",
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
      "clase": "B",
      "pct_acum": 89.2,
      "unidades": 2,
      "venta": 19.0,
      "margen_unitario": 2.66,
      "margen_total": 5.32,
      "costo_estimado": true,
      "existencia": 21,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.02,
      "cobertura_dias": 945.0,
      "rotacion": 0.1,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 945 días, exceso de stock",
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
      "pct_acum": 90.1,
      "unidades": 2,
      "venta": 54.0,
      "margen_unitario": 7.56,
      "margen_total": 15.12,
      "costo_estimado": true,
      "existencia": 52,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.02,
      "cobertura_dias": 2340.0,
      "rotacion": 0.04,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 2340 días, exceso de stock",
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
      "pct_acum": 91.0,
      "unidades": 2,
      "venta": 33.0,
      "margen_unitario": 4.62,
      "margen_total": 9.24,
      "costo_estimado": true,
      "existencia": 84,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.02,
      "cobertura_dias": 3780.0,
      "rotacion": 0.02,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 3780 días, exceso de stock",
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
      "pct_acum": 92.0,
      "unidades": 2,
      "venta": 30.0,
      "margen_unitario": 4.2,
      "margen_total": 8.4,
      "costo_estimado": true,
      "existencia": 72,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.02,
      "cobertura_dias": 3240.0,
      "rotacion": 0.03,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 3240 días, exceso de stock",
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
      "pct_acum": 92.9,
      "unidades": 2,
      "venta": 72.0,
      "margen_unitario": 10.08,
      "margen_total": 20.16,
      "costo_estimado": true,
      "existencia": 40,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.02,
      "cobertura_dias": 1800.0,
      "rotacion": 0.05,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1800 días, exceso de stock",
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
      "pct_acum": 93.9,
      "unidades": 2,
      "venta": 64.0,
      "margen_unitario": 8.96,
      "margen_total": 17.92,
      "costo_estimado": true,
      "existencia": 19,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.02,
      "cobertura_dias": 855.0,
      "rotacion": 0.11,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 855 días, exceso de stock",
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
      "clase": "B",
      "pct_acum": 94.8,
      "unidades": 2,
      "venta": 34.0,
      "margen_unitario": 4.76,
      "margen_total": 9.52,
      "costo_estimado": true,
      "existencia": 87,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.02,
      "cobertura_dias": 3915.0,
      "rotacion": 0.02,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 3915 días, exceso de stock",
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
      "pct_acum": 95.8,
      "unidades": 2,
      "venta": 84.0,
      "margen_unitario": 11.76,
      "margen_total": 23.52,
      "costo_estimado": true,
      "existencia": 15,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.02,
      "cobertura_dias": 675.0,
      "rotacion": 0.13,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 675 días, exceso de stock",
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
      "clase": "C",
      "pct_acum": 96.7,
      "unidades": 2,
      "venta": 76.0,
      "margen_unitario": 10.64,
      "margen_total": 21.28,
      "costo_estimado": true,
      "existencia": 68,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.02,
      "cobertura_dias": 3060.0,
      "rotacion": 0.03,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 3060 días, exceso de stock",
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
      "clase": "C",
      "pct_acum": 97.6,
      "unidades": 2,
      "venta": 64.0,
      "margen_unitario": 8.96,
      "margen_total": 17.92,
      "costo_estimado": true,
      "existencia": 73,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.02,
      "cobertura_dias": 3285.0,
      "rotacion": 0.03,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 3285 días, exceso de stock",
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
      "pct_acum": 98.1,
      "unidades": 1,
      "venta": 21.0,
      "margen_unitario": 5.88,
      "margen_total": 5.88,
      "costo_estimado": true,
      "existencia": 42,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.01,
      "cobertura_dias": 3780.0,
      "rotacion": 0.02,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 3780 días, exceso de stock",
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
      "pct_acum": 98.6,
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
    },
    {
      "producto": {
        "id": 33,
        "clave_interna": "LA-005",
        "nombre": "Crema ácida"
      },
      "categoria": "Lácteos y huevo",
      "clase": "C",
      "pct_acum": 99.1,
      "unidades": 1,
      "venta": 36.0,
      "margen_unitario": 10.08,
      "margen_total": 10.08,
      "costo_estimado": true,
      "existencia": 85,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.01,
      "cobertura_dias": 7650.0,
      "rotacion": 0.01,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 7650 días, exceso de stock",
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
      "pct_acum": 99.5,
      "unidades": 1,
      "venta": 26.0,
      "margen_unitario": 7.28,
      "margen_total": 7.28,
      "costo_estimado": true,
      "existencia": 47,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.01,
      "cobertura_dias": 4230.0,
      "rotacion": 0.02,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 4230 días, exceso de stock",
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
      "clase": "C",
      "pct_acum": 100.0,
      "unidades": 1,
      "venta": 36.0,
      "margen_unitario": 10.08,
      "margen_total": 10.08,
      "costo_estimado": true,
      "existencia": 78,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.01,
      "cobertura_dias": 7020.0,
      "rotacion": 0.01,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 7020 días, exceso de stock",
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
      "pct_acum": 100.0,
      "unidades": 0,
      "venta": 0.0,
      "margen_unitario": 16.24,
      "margen_total": 0.0,
      "costo_estimado": true,
      "existencia": 57,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.0,
      "cobertura_dias": null,
      "rotacion": 0.0,
      "recomendacion": "Eliminar",
      "motivo": "sin movimiento en la ventana de análisis",
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
X-Traza-Id: d526b6b8-9573-4832-b095-cdd7f4b31053
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 381 ms · traza `d526b6b8-9573-4832-b095-cdd7f4b31053`

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
      "ocupado": 7381.0,
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
        "id": 23,
        "clave_interna": "BE-003",
        "nombre": "Refresco de cola"
      },
      "categoria": "Bebidas",
      "clase": "A",
      "pct_acum": 2.9,
      "unidades": 21,
      "venta": 808.5,
      "margen_unitario": 10.78,
      "margen_total": 226.38,
      "costo_estimado": true,
      "existencia": 185,
      "minimo": 21,
      "quiebres": 0,
      "demanda_dia": 0.23,
      "cobertura_dias": 792.9,
      "rotacion": 0.11,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 793 días, exceso de stock",
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
      "pct_acum": 5.8,
      "unidades": 21,
      "venta": 157.5,
      "margen_unitario": 2.1,
      "margen_total": 44.1,
      "costo_estimado": true,
      "existencia": 179,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.23,
      "cobertura_dias": 767.1,
      "rotacion": 0.12,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 767 días, exceso de stock",
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
      "pct_acum": 8.7,
      "unidades": 21,
      "venta": 588.0,
      "margen_unitario": 7.84,
      "margen_total": 164.64,
      "costo_estimado": true,
      "existencia": 77,
      "minimo": 24,
      "quiebres": 0,
      "demanda_dia": 0.23,
      "cobertura_dias": 330.0,
      "rotacion": 0.27,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 330 días, exceso de stock",
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
      "pct_acum": 11.5,
      "unidades": 20,
      "venta": 720.0,
      "margen_unitario": 10.08,
      "margen_total": 201.6,
      "costo_estimado": true,
      "existencia": 207,
      "minimo": 20,
      "quiebres": 0,
      "demanda_dia": 0.22,
      "cobertura_dias": 931.5,
      "rotacion": 0.1,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 932 días, exceso de stock",
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
      "pct_acum": 14.2,
      "unidades": 20,
      "venta": 880.0,
      "margen_unitario": 12.32,
      "margen_total": 246.4,
      "costo_estimado": true,
      "existencia": 89,
      "minimo": 21,
      "quiebres": 1,
      "demanda_dia": 0.22,
      "cobertura_dias": 400.5,
      "rotacion": 0.22,
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
      "pct_acum": 16.9,
      "unidades": 19,
      "venta": 568.1,
      "margen_unitario": 8.37,
      "margen_total": 159.03,
      "costo_estimado": true,
      "existencia": 113,
      "minimo": 25,
      "quiebres": 0,
      "demanda_dia": 0.21,
      "cobertura_dias": 535.3,
      "rotacion": 0.17,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 535 días, exceso de stock",
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
      "pct_acum": 19.4,
      "unidades": 18,
      "venta": 297.0,
      "margen_unitario": 4.62,
      "margen_total": 83.16,
      "costo_estimado": true,
      "existencia": 164,
      "minimo": 21,
      "quiebres": 0,
      "demanda_dia": 0.2,
      "cobertura_dias": 820.0,
      "rotacion": 0.11,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 820 días, exceso de stock",
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
      "pct_acum": 21.9,
      "unidades": 18,
      "venta": 576.0,
      "margen_unitario": 8.96,
      "margen_total": 161.28,
      "costo_estimado": true,
      "existencia": 52,
      "minimo": 28,
      "quiebres": 2,
      "demanda_dia": 0.2,
      "cobertura_dias": 260.0,
      "rotacion": 0.35,
      "recomendacion": "Aumentar",
      "motivo": "hubo quiebres",
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
      "pct_acum": 24.3,
      "unidades": 18,
      "venta": 1224.0,
      "margen_unitario": 19.04,
      "margen_total": 342.72,
      "costo_estimado": true,
      "existencia": 130,
      "minimo": 20,
      "quiebres": 0,
      "demanda_dia": 0.2,
      "cobertura_dias": 650.0,
      "rotacion": 0.14,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 650 días, exceso de stock",
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
      "pct_acum": 26.7,
      "unidades": 17,
      "venta": 654.5,
      "margen_unitario": 10.78,
      "margen_total": 183.26,
      "costo_estimado": true,
      "existencia": 172,
      "minimo": 25,
      "quiebres": 0,
      "demanda_dia": 0.19,
      "cobertura_dias": 910.6,
      "rotacion": 0.1,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 911 días, exceso de stock",
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
      "pct_acum": 29.0,
      "unidades": 17,
      "venta": 416.5,
      "margen_unitario": 6.86,
      "margen_total": 116.62,
      "costo_estimado": true,
      "existencia": 160,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.19,
      "cobertura_dias": 847.1,
      "rotacion": 0.11,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 847 días, exceso de stock",
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
      "pct_acum": 31.4,
      "unidades": 17,
      "venta": 714.0,
      "margen_unitario": 11.76,
      "margen_total": 199.92,
      "costo_estimado": true,
      "existencia": 177,
      "minimo": 21,
      "quiebres": 0,
      "demanda_dia": 0.19,
      "cobertura_dias": 937.1,
      "rotacion": 0.1,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 937 días, exceso de stock",
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
      "pct_acum": 33.7,
      "unidades": 17,
      "venta": 306.0,
      "margen_unitario": 5.04,
      "margen_total": 85.68,
      "costo_estimado": true,
      "existencia": 176,
      "minimo": 26,
      "quiebres": 0,
      "demanda_dia": 0.19,
      "cobertura_dias": 931.8,
      "rotacion": 0.1,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 932 días, exceso de stock",
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
      "pct_acum": 36.0,
      "unidades": 16,
      "venta": 672.0,
      "margen_unitario": 11.76,
      "margen_total": 188.16,
      "costo_estimado": true,
      "existencia": 97,
      "minimo": 15,
      "quiebres": 0,
      "demanda_dia": 0.18,
      "cobertura_dias": 545.6,
      "rotacion": 0.16,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 546 días, exceso de stock",
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
      "pct_acum": 38.2,
      "unidades": 16,
      "venta": 312.0,
      "margen_unitario": 5.46,
      "margen_total": 87.36,
      "costo_estimado": true,
      "existencia": 301,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.18,
      "cobertura_dias": 1693.1,
      "rotacion": 0.05,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1693 días, exceso de stock",
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
      "pct_acum": 40.4,
      "unidades": 16,
      "venta": 432.0,
      "margen_unitario": 7.56,
      "margen_total": 120.96,
      "costo_estimado": true,
      "existencia": 162,
      "minimo": 15,
      "quiebres": 0,
      "demanda_dia": 0.18,
      "cobertura_dias": 911.2,
      "rotacion": 0.1,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 911 días, exceso de stock",
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
      "pct_acum": 42.6,
      "unidades": 16,
      "venta": 384.0,
      "margen_unitario": 6.72,
      "margen_total": 107.52,
      "costo_estimado": true,
      "existencia": 208,
      "minimo": 20,
      "quiebres": 0,
      "demanda_dia": 0.18,
      "cobertura_dias": 1170.0,
      "rotacion": 0.08,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1170 días, exceso de stock",
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
      "pct_acum": 44.8,
      "unidades": 16,
      "venta": 496.0,
      "margen_unitario": 8.68,
      "margen_total": 138.88,
      "costo_estimado": true,
      "existencia": 69,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.18,
      "cobertura_dias": 388.1,
      "rotacion": 0.23,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 388 días, exceso de stock",
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
      "pct_acum": 47.0,
      "unidades": 16,
      "venta": 736.0,
      "margen_unitario": 12.88,
      "margen_total": 206.08,
      "costo_estimado": true,
      "existencia": 96,
      "minimo": 18,
      "quiebres": 0,
      "demanda_dia": 0.18,
      "cobertura_dias": 540.0,
      "rotacion": 0.17,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 540 días, exceso de stock",
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
      "pct_acum": 49.2,
      "unidades": 16,
      "venta": 512.0,
      "margen_unitario": 8.96,
      "margen_total": 143.36,
      "costo_estimado": true,
      "existencia": 126,
      "minimo": 25,
      "quiebres": 0,
      "demanda_dia": 0.18,
      "cobertura_dias": 708.8,
      "rotacion": 0.13,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 709 días, exceso de stock",
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
      "unidades": 15,
      "venta": 397.5,
      "margen_unitario": 7.42,
      "margen_total": 111.3,
      "costo_estimado": true,
      "existencia": 530,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.17,
      "cobertura_dias": 3180.0,
      "rotacion": 0.03,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 3180 días, exceso de stock",
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
      "pct_acum": 53.4,
      "unidades": 15,
      "venta": 345.0,
      "margen_unitario": 6.44,
      "margen_total": 96.6,
      "costo_estimado": true,
      "existencia": 136,
      "minimo": 20,
      "quiebres": 0,
      "demanda_dia": 0.17,
      "cobertura_dias": 816.0,
      "rotacion": 0.11,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 816 días, exceso de stock",
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
      "pct_acum": 55.5,
      "unidades": 15,
      "venta": 780.0,
      "margen_unitario": 14.56,
      "margen_total": 218.4,
      "costo_estimado": true,
      "existencia": 108,
      "minimo": 15,
      "quiebres": 0,
      "demanda_dia": 0.17,
      "cobertura_dias": 648.0,
      "rotacion": 0.14,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 648 días, exceso de stock",
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
      "pct_acum": 57.5,
      "unidades": 15,
      "venta": 360.0,
      "margen_unitario": 6.72,
      "margen_total": 100.8,
      "costo_estimado": true,
      "existencia": 103,
      "minimo": 18,
      "quiebres": 0,
      "demanda_dia": 0.17,
      "cobertura_dias": 618.0,
      "rotacion": 0.15,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 618 días, exceso de stock",
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
      "pct_acum": 59.6,
      "unidades": 15,
      "venta": 660.0,
      "margen_unitario": 12.32,
      "margen_total": 184.8,
      "costo_estimado": true,
      "existencia": 159,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.17,
      "cobertura_dias": 954.0,
      "rotacion": 0.09,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 954 días, exceso de stock",
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
      "pct_acum": 61.7,
      "unidades": 15,
      "venta": 420.0,
      "margen_unitario": 7.84,
      "margen_total": 117.6,
      "costo_estimado": true,
      "existencia": 204,
      "minimo": 15,
      "quiebres": 0,
      "demanda_dia": 0.17,
      "cobertura_dias": 1224.0,
      "rotacion": 0.07,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1224 días, exceso de stock",
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
      "pct_acum": 63.8,
      "unidades": 15,
      "venta": 810.0,
      "margen_unitario": 15.12,
      "margen_total": 226.8,
      "costo_estimado": true,
      "existencia": 157,
      "minimo": 25,
      "quiebres": 0,
      "demanda_dia": 0.17,
      "cobertura_dias": 942.0,
      "rotacion": 0.1,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 942 días, exceso de stock",
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
      "pct_acum": 65.7,
      "unidades": 14,
      "venta": 154.0,
      "margen_unitario": 3.08,
      "margen_total": 43.12,
      "costo_estimado": true,
      "existencia": 90,
      "minimo": 20,
      "quiebres": 2,
      "demanda_dia": 0.16,
      "cobertura_dias": 578.6,
      "rotacion": 0.16,
      "recomendacion": "Aumentar",
      "motivo": "hubo quiebres",
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
      "pct_acum": 67.6,
      "unidades": 14,
      "venta": 385.0,
      "margen_unitario": 7.7,
      "margen_total": 107.8,
      "costo_estimado": true,
      "existencia": 133,
      "minimo": 25,
      "quiebres": 0,
      "demanda_dia": 0.16,
      "cobertura_dias": 855.0,
      "rotacion": 0.11,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 855 días, exceso de stock",
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
      "pct_acum": 69.6,
      "unidades": 14,
      "venta": 1008.0,
      "margen_unitario": 20.16,
      "margen_total": 282.24,
      "costo_estimado": true,
      "existencia": 116,
      "minimo": 28,
      "quiebres": 0,
      "demanda_dia": 0.16,
      "cobertura_dias": 745.7,
      "rotacion": 0.12,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 746 días, exceso de stock",
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
      "clase": "A",
      "pct_acum": 71.5,
      "unidades": 14,
      "venta": 203.0,
      "margen_unitario": 4.06,
      "margen_total": 56.84,
      "costo_estimado": true,
      "existencia": 182,
      "minimo": 21,
      "quiebres": 0,
      "demanda_dia": 0.16,
      "cobertura_dias": 1170.0,
      "rotacion": 0.08,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1170 días, exceso de stock",
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
      "pct_acum": 73.4,
      "unidades": 14,
      "venta": 448.0,
      "margen_unitario": 8.96,
      "margen_total": 125.44,
      "costo_estimado": true,
      "existencia": 176,
      "minimo": 20,
      "quiebres": 0,
      "demanda_dia": 0.16,
      "cobertura_dias": 1131.4,
      "rotacion": 0.08,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1131 días, exceso de stock",
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
      "pct_acum": 75.2,
      "unidades": 13,
      "venta": 221.0,
      "margen_unitario": 4.76,
      "margen_total": 61.88,
      "costo_estimado": true,
      "existencia": 154,
      "minimo": 28,
      "quiebres": 0,
      "demanda_dia": 0.14,
      "cobertura_dias": 1066.2,
      "rotacion": 0.08,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1066 días, exceso de stock",
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
      "pct_acum": 77.0,
      "unidades": 13,
      "venta": 546.0,
      "margen_unitario": 11.76,
      "margen_total": 152.88,
      "costo_estimado": true,
      "existencia": 59,
      "minimo": 21,
      "quiebres": 2,
      "demanda_dia": 0.14,
      "cobertura_dias": 408.5,
      "rotacion": 0.22,
      "recomendacion": "Aumentar",
      "motivo": "hubo quiebres",
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
      "pct_acum": 78.8,
      "unidades": 13,
      "venta": 253.5,
      "margen_unitario": 5.46,
      "margen_total": 70.98,
      "costo_estimado": true,
      "existencia": 160,
      "minimo": 28,
      "quiebres": 0,
      "demanda_dia": 0.14,
      "cobertura_dias": 1107.7,
      "rotacion": 0.08,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1108 días, exceso de stock",
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
      "pct_acum": 80.6,
      "unidades": 13,
      "venta": 429.0,
      "margen_unitario": 9.24,
      "margen_total": 120.12,
      "costo_estimado": true,
      "existencia": 143,
      "minimo": 24,
      "quiebres": 0,
      "demanda_dia": 0.14,
      "cobertura_dias": 990.0,
      "rotacion": 0.09,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 990 días, exceso de stock",
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
      "pct_acum": 82.3,
      "unidades": 12,
      "venta": 432.0,
      "margen_unitario": 10.08,
      "margen_total": 120.96,
      "costo_estimado": true,
      "existencia": 91,
      "minimo": 25,
      "quiebres": 0,
      "demanda_dia": 0.13,
      "cobertura_dias": 682.5,
      "rotacion": 0.13,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 682 días, exceso de stock",
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
      "pct_acum": 84.0,
      "unidades": 12,
      "venta": 264.0,
      "margen_unitario": 6.16,
      "margen_total": 73.92,
      "costo_estimado": true,
      "existencia": 155,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.13,
      "cobertura_dias": 1162.5,
      "rotacion": 0.08,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1162 días, exceso de stock",
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
      "pct_acum": 85.5,
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
        "id": 44,
        "clave_interna": "LI-008",
        "nombre": "Bolsas para basura"
      },
      "categoria": "Limpieza del hogar",
      "clase": "B",
      "pct_acum": 87.0,
      "unidades": 11,
      "venta": 264.0,
      "margen_unitario": 6.72,
      "margen_total": 73.92,
      "costo_estimado": true,
      "existencia": 55,
      "minimo": 21,
      "quiebres": 0,
      "demanda_dia": 0.12,
      "cobertura_dias": 450.0,
      "rotacion": 0.2,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 450 días, exceso de stock",
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
      "pct_acum": 88.5,
      "unidades": 11,
      "venta": 396.0,
      "margen_unitario": 10.08,
      "margen_total": 110.88,
      "costo_estimado": true,
      "existencia": 153,
      "minimo": 21,
      "quiebres": 0,
      "demanda_dia": 0.12,
      "cobertura_dias": 1251.8,
      "rotacion": 0.07,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1252 días, exceso de stock",
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
      "pct_acum": 89.9,
      "unidades": 10,
      "venta": 140.0,
      "margen_unitario": 3.92,
      "margen_total": 39.2,
      "costo_estimado": true,
      "existencia": 122,
      "minimo": 21,
      "quiebres": 0,
      "demanda_dia": 0.11,
      "cobertura_dias": 1098.0,
      "rotacion": 0.08,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1098 días, exceso de stock",
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
      "clase": "B",
      "pct_acum": 91.3,
      "unidades": 10,
      "venta": 95.0,
      "margen_unitario": 2.66,
      "margen_total": 26.6,
      "costo_estimado": true,
      "existencia": 107,
      "minimo": 28,
      "quiebres": 0,
      "demanda_dia": 0.11,
      "cobertura_dias": 963.0,
      "rotacion": 0.09,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 963 días, exceso de stock",
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
      "pct_acum": 92.7,
      "unidades": 10,
      "venta": 580.0,
      "margen_unitario": 16.24,
      "margen_total": 162.4,
      "costo_estimado": true,
      "existencia": 205,
      "minimo": 23,
      "quiebres": 0,
      "demanda_dia": 0.11,
      "cobertura_dias": 1845.0,
      "rotacion": 0.05,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1845 días, exceso de stock",
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
      "pct_acum": 93.9,
      "unidades": 9,
      "venta": 135.0,
      "margen_unitario": 4.2,
      "margen_total": 37.8,
      "costo_estimado": true,
      "existencia": 183,
      "minimo": 26,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 1830.0,
      "rotacion": 0.05,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1830 días, exceso de stock",
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
      "pct_acum": 95.2,
      "unidades": 9,
      "venta": 432.0,
      "margen_unitario": 13.44,
      "margen_total": 120.96,
      "costo_estimado": true,
      "existencia": 95,
      "minimo": 15,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 950.0,
      "rotacion": 0.09,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 950 días, exceso de stock",
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
      "pct_acum": 96.3,
      "unidades": 8,
      "venta": 208.0,
      "margen_unitario": 7.28,
      "margen_total": 58.24,
      "costo_estimado": true,
      "existencia": 181,
      "minimo": 30,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 2036.2,
      "rotacion": 0.04,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 2036 días, exceso de stock",
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
      "pct_acum": 97.2,
      "unidades": 7,
      "venta": 147.0,
      "margen_unitario": 5.88,
      "margen_total": 41.16,
      "costo_estimado": true,
      "existencia": 135,
      "minimo": 20,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 1735.7,
      "rotacion": 0.05,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1736 días, exceso de stock",
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
      "pct_acum": 98.2,
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
    },
    {
      "producto": {
        "id": 38,
        "clave_interna": "LI-002",
        "nombre": "Jabón para trastes"
      },
      "categoria": "Limpieza del hogar",
      "clase": "C",
      "pct_acum": 99.2,
      "unidades": 7,
      "venta": 182.0,
      "margen_unitario": 7.28,
      "margen_total": 50.96,
      "costo_estimado": true,
      "existencia": 152,
      "minimo": 18,
      "quiebres": 0,
      "demanda_dia": 0.08,
      "cobertura_dias": 1954.3,
      "rotacion": 0.05,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1954 días, exceso de stock",
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
      "clase": "C",
      "pct_acum": 100.0,
      "unidades": 6,
      "venta": 228.0,
      "margen_unitario": 10.64,
      "margen_total": 63.84,
      "costo_estimado": true,
      "existencia": 149,
      "minimo": 18,
      "quiebres": 0,
      "demanda_dia": 0.07,
      "cobertura_dias": 2235.0,
      "rotacion": 0.04,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 2235 días, exceso de stock",
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
X-Traza-Id: 7954e59c-70ea-4fec-a168-4b763cee7c9e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 471 ms · traza `7954e59c-70ea-4fec-a168-4b763cee7c9e`

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
    "reducir": 49,
    "eliminar": 1,
    "excluir": 0,
    "clase_a": 30,
    "clase_b": 13,
    "clase_c": 8,
    "unidades_a_comprar": 1,
    "con_costo_estimado": 51,
    "espacio": {
      "total": 3600.0,
      "ocupado": 2900.0,
      "sugerido": 1.0,
      "ocupacion_pct": 80.6
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
        "id": 7,
        "clave_interna": "AB-007",
        "nombre": "Harina de trigo"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 4.7,
      "unidades": 10,
      "venta": 245.0,
      "margen_unitario": 6.86,
      "margen_total": 68.6,
      "costo_estimado": true,
      "existencia": 14,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.11,
      "cobertura_dias": 126.0,
      "rotacion": 0.71,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 126 días, exceso de stock",
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
      "pct_acum": 9.4,
      "unidades": 10,
      "venta": 75.0,
      "margen_unitario": 2.1,
      "margen_total": 21.0,
      "costo_estimado": true,
      "existencia": 36,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.11,
      "cobertura_dias": 324.0,
      "rotacion": 0.28,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 324 días, exceso de stock",
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
      "pct_acum": 13.7,
      "unidades": 9,
      "venta": 99.0,
      "margen_unitario": 3.08,
      "margen_total": 27.72,
      "costo_estimado": true,
      "existencia": 56,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 560.0,
      "rotacion": 0.16,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 560 días, exceso de stock",
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
      "pct_acum": 17.9,
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
        "id": 39,
        "clave_interna": "LI-003",
        "nombre": "Cloro"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 21.7,
      "unidades": 8,
      "venta": 156.0,
      "margen_unitario": 5.46,
      "margen_total": 43.68,
      "costo_estimado": true,
      "existencia": 47,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 528.8,
      "rotacion": 0.17,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 529 días, exceso de stock",
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
      "pct_acum": 25.0,
      "unidades": 7,
      "venta": 224.0,
      "margen_unitario": 8.96,
      "margen_total": 62.72,
      "costo_estimado": true,
      "existencia": 80,
      "minimo": 10,
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
        "id": 1,
        "clave_interna": "AB-001",
        "nombre": "Frijol negro a granel"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 27.8,
      "unidades": 6,
      "venta": 231.0,
      "margen_unitario": 10.78,
      "margen_total": 64.68,
      "costo_estimado": true,
      "existencia": 60,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.07,
      "cobertura_dias": 900.0,
      "rotacion": 0.1,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 900 días, exceso de stock",
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
      "pct_acum": 30.7,
      "unidades": 6,
      "venta": 117.0,
      "margen_unitario": 5.46,
      "margen_total": 32.76,
      "costo_estimado": true,
      "existencia": 206,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.07,
      "cobertura_dias": 3090.0,
      "rotacion": 0.03,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 3090 días, exceso de stock",
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
      "pct_acum": 33.5,
      "unidades": 6,
      "venta": 165.0,
      "margen_unitario": 7.7,
      "margen_total": 46.2,
      "costo_estimado": true,
      "existencia": 48,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.07,
      "cobertura_dias": 720.0,
      "rotacion": 0.12,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 720 días, exceso de stock",
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
      "pct_acum": 36.3,
      "unidades": 6,
      "venta": 186.0,
      "margen_unitario": 8.68,
      "margen_total": 52.08,
      "costo_estimado": true,
      "existencia": 15,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.07,
      "cobertura_dias": 225.0,
      "rotacion": 0.4,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 225 días, exceso de stock",
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
      "pct_acum": 39.2,
      "unidades": 6,
      "venta": 168.0,
      "margen_unitario": 7.84,
      "margen_total": 47.04,
      "costo_estimado": true,
      "existencia": 16,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.07,
      "cobertura_dias": 240.0,
      "rotacion": 0.38,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 240 días, exceso de stock",
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
      "pct_acum": 42.0,
      "unidades": 6,
      "venta": 408.0,
      "margen_unitario": 19.04,
      "margen_total": 114.24,
      "costo_estimado": true,
      "existencia": 29,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.07,
      "cobertura_dias": 435.0,
      "rotacion": 0.21,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 435 días, exceso de stock",
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
      "pct_acum": 44.3,
      "unidades": 5,
      "venta": 149.5,
      "margen_unitario": 8.37,
      "margen_total": 41.85,
      "costo_estimado": true,
      "existencia": 35,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 630.0,
      "rotacion": 0.14,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 630 días, exceso de stock",
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
      "pct_acum": 46.7,
      "unidades": 5,
      "venta": 210.0,
      "margen_unitario": 11.76,
      "margen_total": 58.8,
      "costo_estimado": true,
      "existencia": 10,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 180.0,
      "rotacion": 0.5,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 180 días, exceso de stock",
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
      "pct_acum": 49.1,
      "unidades": 5,
      "venta": 115.0,
      "margen_unitario": 6.44,
      "margen_total": 32.2,
      "costo_estimado": true,
      "existencia": 31,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 558.0,
      "rotacion": 0.16,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 558 días, exceso de stock",
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
      "pct_acum": 51.4,
      "unidades": 5,
      "venta": 260.0,
      "margen_unitario": 14.56,
      "margen_total": 72.8,
      "costo_estimado": true,
      "existencia": 33,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 594.0,
      "rotacion": 0.15,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 594 días, exceso de stock",
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
      "pct_acum": 53.8,
      "unidades": 5,
      "venta": 120.0,
      "margen_unitario": 6.72,
      "margen_total": 33.6,
      "costo_estimado": true,
      "existencia": 79,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 1422.0,
      "rotacion": 0.06,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1422 días, exceso de stock",
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
      "pct_acum": 56.1,
      "unidades": 5,
      "venta": 220.0,
      "margen_unitario": 12.32,
      "margen_total": 61.6,
      "costo_estimado": true,
      "existencia": 13,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 234.0,
      "rotacion": 0.38,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 234 días, exceso de stock",
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
      "clase": "A",
      "pct_acum": 58.5,
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
      "clase": "A",
      "pct_acum": 60.8,
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
        "id": 44,
        "clave_interna": "LI-008",
        "nombre": "Bolsas para basura"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 63.2,
      "unidades": 5,
      "venta": 120.0,
      "margen_unitario": 6.72,
      "margen_total": 33.6,
      "costo_estimado": true,
      "existencia": 28,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 504.0,
      "rotacion": 0.18,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 504 días, exceso de stock",
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
      "pct_acum": 65.6,
      "unidades": 5,
      "venta": 90.0,
      "margen_unitario": 5.04,
      "margen_total": 25.2,
      "costo_estimado": true,
      "existencia": 46,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 828.0,
      "rotacion": 0.11,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 828 días, exceso de stock",
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
      "clase": "A",
      "pct_acum": 67.9,
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
      "clase": "A",
      "pct_acum": 69.8,
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
        "id": 5,
        "clave_interna": "AB-005",
        "nombre": "Sal de mesa"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 71.7,
      "unidades": 4,
      "venta": 56.0,
      "margen_unitario": 3.92,
      "margen_total": 15.68,
      "costo_estimado": true,
      "existencia": 30,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.04,
      "cobertura_dias": 675.0,
      "rotacion": 0.13,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 675 días, exceso de stock",
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
      "pct_acum": 73.6,
      "unidades": 4,
      "venta": 104.0,
      "margen_unitario": 7.28,
      "margen_total": 29.12,
      "costo_estimado": true,
      "existencia": 66,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.04,
      "cobertura_dias": 1485.0,
      "rotacion": 0.06,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1485 días, exceso de stock",
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
      "pct_acum": 75.5,
      "unidades": 4,
      "venta": 106.0,
      "margen_unitario": 7.42,
      "margen_total": 29.68,
      "costo_estimado": true,
      "existencia": 417,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.04,
      "cobertura_dias": 9382.5,
      "rotacion": 0.01,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 9382 días, exceso de stock",
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
      "pct_acum": 77.4,
      "unidades": 4,
      "venta": 96.0,
      "margen_unitario": 6.72,
      "margen_total": 26.88,
      "costo_estimado": true,
      "existencia": 21,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.04,
      "cobertura_dias": 472.5,
      "rotacion": 0.19,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 472 días, exceso de stock",
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
      "pct_acum": 79.2,
      "unidades": 4,
      "venta": 112.0,
      "margen_unitario": 7.84,
      "margen_total": 31.36,
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
        "id": 32,
        "clave_interna": "LA-004",
        "nombre": "Queso Oaxaca"
      },
      "categoria": "Lácteos y huevo",
      "clase": "A",
      "pct_acum": 81.1,
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

### SUR-05 · Clase inventada · PASA

**Objetivo.** Solo A, B o C.

**Petición.** `GET http://surtido:5122/api/v1/surtido/analisis?microhub_id=1&clase=Z`

```http
Accept: application/json
X-Traza-Id: 19b2ebca-bfb5-4503-9c06-6c4f8c551a9d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 400 (esperado 400) · 9 ms · traza `19b2ebca-bfb5-4503-9c06-6c4f8c551a9d`

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
    "traza_id": "19b2ebca-bfb5-4503-9c06-6c4f8c551a9d"
  }
}
```

### SUR-06 · Análisis (XML) · PASA

**Objetivo.** Respuesta XML que cumple surtido.xsd.

**Petición.** `GET http://surtido:5122/api/v1/surtido/analisis?microhub_id=1`

```http
Accept: application/xml
X-Traza-Id: 71d4d306-d97e-47fa-b877-595b980e311d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 365 ms · traza `71d4d306-d97e-47fa-b877-595b980e311d`

```xml
<?xml version='1.0' encoding='utf-8'?>
<surtido_analisis xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><ventana_dias>90</ventana_dias><resumen><productos>51</productos><aumentar>1</aumentar><mantener>0</mantener><reducir>49</reducir><eliminar>1</eliminar><excluir>0</excluir><clase_a>30</clase_a><clase_b>13</clase_b><clase_c>8</clase_c><unidades_a_comprar>1</unidades_a_comprar><con_costo_estimado>51</con_costo_estimado><espacio><total>3600</total><ocupado>2900</ocupado><sugerido>1</sugerido><ocupacion_pct>80.6</ocupacion_pct></espacio><presupuesto><total>120000</total><requerido>27.36</requerido><uso_pct>0</uso_pct></presupuesto></resumen><filas><fila><producto><id>7</id><clave_interna>AB-007</clave_interna><nombre>Harina de trigo</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>4.7</pct_acum><unidades>10</unidades><venta>245</venta><margen_unitario>6.86</margen_unitario><margen_total>68.6</margen_total><costo_estimado>true</costo_estimado><existencia>14</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.11</demanda_dia><cobertura_dias>126</cobertura_dias><rotacion>0.71</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 126 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>28</id><clave_interna>BE-008</clave_interna><nombre>Polvo para agua de sabor</nombre></producto><categoria>Bebidas</categoria><clase>A</clase><pct_acum>9.4</pct_acum><unidades>10</unidades><venta>75</venta><margen_unitario>2.1</margen_unitario><margen_total>21</margen_total><costo_estimado>true</costo_estimado><existencia>36</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.11</demanda_dia><cobertura_dias>324</cobertura_dias><rotacion>0.28</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 324 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>13</id><clave_interna>AB-013</clave_interna><nombre>Puré de tomate</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>13.7</pct_acum><unidades>9</unidades><venta>99</venta><margen_unitario>3.08</margen_unitario><margen_total>27.72</margen_total><costo_estimado>true</costo_estimado><existencia>56</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.1</demanda_dia><cobertura_dias>560</cobertura_dias><rotacion>0.16</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 560 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>19</id><clave_interna>AB-019</clave_interna><nombre>Huevo blanco</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>17.9</pct_acum><unidades>9</unidades><venta>378</venta><margen_unitario>11.76</margen_unitario><margen_total>105.84</margen_total><costo_estimado>true</costo_estimado><existencia>49</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.1</demanda_dia><cobertura_dias>490</cobertura_dias><rotacion>0.18</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 490 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>39</id><clave_interna>LI-003</clave_interna><nombre>Cloro</nombre></producto><categoria>Limpieza del hogar</categoria><clase>A</clase><pct_acum>21.7</pct_acum><unidades>8</unidades><venta>156</venta><margen_unitario>5.46</margen_unitario><margen_total>43.68</margen_total><costo_estimado>true</costo_estimado><existencia>47</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.09</demanda_dia><cobertura_dias>528.8</cobertura_dias><rotacion>0.17</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 529 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>48</id><clave_interna>HI-003</clave_interna><nombre>Pasta dental</nombre></producto><categoria>Higiene personal</categoria><clase>A</clase><pct_acum>25</pct_acum><unidades>7</unidades><venta>224</venta><margen_unitario>8.96</margen_unitario><margen_total>62.72</margen_total><costo_estimado>true</costo_estimado><existencia>80</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.08</demanda_dia><cobertura_dias>1028.6</cobertura_dias><rotacion>0.09</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1029 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>1</id><clave_interna>AB-001</clave_interna><nombre>Frijol negro a granel</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>27.8</pct_acum><unidades>6</unidades><venta>231</venta><margen_unitario>10.78</margen_unitario><margen_total>64.68</margen_total><costo_estimado>true</costo_estimado><existencia>60</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.07</demanda_dia><cobertura_dias>900</cobertura_dias><rotacion>0.1</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 900 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>12</id><clave_interna>AB-012</clave_interna><nombre>Chiles jalapeños en escabeche</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>30.7</pct_acum><unidades>6</unidades><venta>117</venta><margen_unitario>5.46</margen_unitario><margen_total>32.76</margen_total><costo_estimado>true</costo_estimado><existencia>206</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.07</demanda_dia><cobertura_dias>3090</cobertura_dias><rotacion>0.03</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 3090 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>29</id><clave_interna>LA-001</clave_interna><nombre>Leche entera</nombre></producto><categoria>Lácteos y huevo</categoria><clase>A</clase><pct_acum>33.5</pct_acum><unidades>6</unidades><venta>165</venta><margen_unitario>7.7</margen_unitario><margen_total>46.2</margen_total><costo_estimado>true</costo_estimado><existencia>48</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.07</demanda_dia><cobertura_dias>720</cobertura_dias><rotacion>0.12</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 720 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>30</id><clave_interna>LA-002</clave_interna><nombre>Leche deslactosada</nombre></producto><categoria>Lácteos y huevo</categoria><clase>A</clase><pct_acum>36.3</pct_acum><unidades>6</unidades><venta>186</venta><margen_unitario>8.68</margen_unitario><margen_total>52.08</margen_total><costo_estimado>true</costo_estimado><existencia>15</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.07</demanda_dia><cobertura_dias>225</cobertura_dias><rotacion>0.4</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 225 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>40</id><clave_interna>LI-004</clave_interna><nombre>Limpiador multiusos</nombre></producto><categoria>Limpieza del hogar</categoria><clase>A</clase><pct_acum>39.2</pct_acum><unidades>6</unidades><venta>168</venta><margen_unitario>7.84</margen_unitario><margen_total>47.04</margen_total><costo_estimado>true</costo_estimado><existencia>16</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.07</demanda_dia><cobertura_dias>240</cobertura_dias><rotacion>0.38</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 240 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>51</id><clave_interna>HI-006</clave_interna><nombre>Pañal etapa 3</nombre></producto><categoria>Higiene personal</categoria><clase>A</clase><pct_acum>42</pct_acum><unidades>6</unidades><venta>408</venta><margen_unitario>19.04</margen_unitario><margen_total>114.24</margen_total><costo_estimado>true</costo_estimado><existencia>29</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.07</demanda_dia><cobertura_dias>435</cobertura_dias><rotacion>0.21</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 435 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>2</id><clave_interna>AB-002</clave_interna><nombre>Arroz superextra</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>44.3</pct_acum><unidades>5</unidades><venta>149.5</venta><margen_unitario>8.37</margen_unitario><margen_total>41.85</margen_total><costo_estimado>true</costo_estimado><existencia>35</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>630</cobertura_dias><rotacion>0.14</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 630 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>3</id><clave_interna>AB-003</clave_interna><nombre>Aceite vegetal</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>46.7</pct_acum><unidades>5</unidades><venta>210</venta><margen_unitario>11.76</margen_unitario><margen_total>58.8</margen_total><costo_estimado>true</costo_estimado><existencia>10</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>180</cobertura_dias><rotacion>0.5</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 180 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>11</id><clave_interna>AB-011</clave_interna><nombre>Frijoles refritos</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>49.1</pct_acum><unidades>5</unidades><venta>115</venta><margen_unitario>6.44</margen_unitario><margen_total>32.2</margen_total><costo_estimado>true</costo_estimado><existencia>31</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>558</cobertura_dias><rotacion>0.16</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 558 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>14</id><clave_interna>AB-014</clave_interna><nombre>Café soluble</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>51.4</pct_acum><unidades>5</unidades><venta>260</venta><margen_unitario>14.56</margen_unitario><margen_total>72.8</margen_total><costo_estimado>true</costo_estimado><existencia>33</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>594</cobertura_dias><rotacion>0.15</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 594 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>20</id><clave_interna>AB-020</clave_interna><nombre>Lenteja</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>53.8</pct_acum><unidades>5</unidades><venta>120</venta><margen_unitario>6.72</margen_unitario><margen_total>33.6</margen_total><costo_estimado>true</costo_estimado><existencia>79</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>1422</cobertura_dias><rotacion>0.06</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1422 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>34</id><clave_interna>LA-006</clave_interna><nombre>Yogur natural</nombre></producto><categoria>Lácteos y huevo</categoria><clase>A</clase><pct_acum>56.1</pct_acum><unidades>5</unidades><venta>220</venta><margen_unitario>12.32</margen_unitario><margen_total>61.6</margen_total><costo_estimado>true</costo_estimado><existencia>13</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>234</cobertura_dias><rotacion>0.38</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 234 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>35</id><clave_interna>LA-007</clave_interna><nombre>Mantequilla</nombre></producto><categoria>Lácteos y huevo</categoria><clase>A</clase><pct_acum>58.5</pct_acum><unidades>5</unidades><venta>110</venta><margen_unitario>6.16</margen_unitario><margen_total>30.8</margen_total><costo_estimado>true</costo_estimado><existencia>64</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>1152</cobertura_dias><rotacion>0.08</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1152 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>41</id><clave_interna>LI-005</clave_interna><nombre>Suavizante de telas</nombre></producto><categoria>Limpieza del hogar</categoria><clase>A</clase><pct_acum>60.8</pct_acum><unidades>5</unidades><venta>165</venta><margen_unitario>9.24</margen_unitario><margen_total>46.2</margen_total><costo_estimado>true</costo_estimado><existencia>69</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>1242</cobertura_dias><rotacion>0.07</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1242 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>44</id><clave_interna>LI-008</clave_interna><nombre>Bolsas para basura</nombre></producto><categoria>Limpieza del hogar</categoria><clase>A</clase><pct_acum>63.2</pct_acum><unidades>5</unidades><venta>120</venta><margen_unitario>6.72</margen_unitario><margen_total>33.6</margen_total><costo_estimado>true</costo_estimado><existencia>28</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>504</cobertura_dias><rotacion>0.18</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 504 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>45</id><clave_interna>LI-009</clave_interna><nombre>Fibra para trastes</nombre></producto><categoria>Limpieza del hogar</categoria><clase>A</clase><pct_acum>65.6</pct_acum><unidades>5</unidades><venta>90</venta><margen_unitario>5.04</margen_unitario><margen_total>25.2</margen_total><costo_estimado>true</costo_estimado><existencia>46</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>828</cobertura_dias><rotacion>0.11</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 828 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>46</id><clave_interna>HI-001</clave_interna><nombre>Jabón de tocador</nombre></producto><categoria>Higiene personal</categoria><clase>A</clase><pct_acum>67.9</pct_acum><unidades>5</unidades><venta>72.5</venta><margen_unitario>4.06</margen_unitario><margen_total>20.3</margen_total><costo_estimado>true</costo_estimado><existencia>63</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.06</demanda_dia><cobertura_dias>1134</cobertura_dias><rotacion>0.08</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1134 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>4</id><clave_interna>AB-004</clave_interna><nombre>Azúcar estándar</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>69.8</pct_acum><unidades>4</unidades><venta>114</venta><margen_unitario>7.98</margen_unitario><margen_total>31.92</margen_total><costo_estimado>true</costo_estimado><existencia>18</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.04</demanda_dia><cobertura_dias>405</cobertura_dias><rotacion>0.22</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 405 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>5</id><clave_interna>AB-005</clave_interna><nombre>Sal de mesa</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>71.7</pct_acum><unidades>4</unidades><venta>56</venta><margen_unitario>3.92</margen_unitario><margen_total>15.68</margen_total><costo_estimado>true</costo_estimado><existencia>30</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.04</demanda_dia><cobertura_dias>675</cobertura_dias><rotacion>0.13</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 675 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>6</id><clave_interna>AB-006</clave_interna><nombre>Harina de maíz nixtamalizado</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>73.6</pct_acum><unidades>4</unidades><venta>104</venta><margen_unitario>7.28</margen_unitario><margen_total>29.12</margen_total><costo_estimado>true</costo_estimado><existencia>66</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.04</demanda_dia><cobertura_dias>1485</cobertura_dias><rotacion>0.06</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1485 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>10</id><clave_interna>AB-010</clave_interna><nombre>Sardina en salsa de tomate</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>75.5</pct_acum><unidades>4</unidades><venta>106</venta><margen_unitario>7.42</margen_unitario><margen_total>29.68</margen_total><costo_estimado>true</costo_estimado><existencia>417</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.04</demanda_dia><cobertura_dias>9382.5</cobertura_dias><rotacion>0.01</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 9382 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>17</id><clave_interna>AB-017</clave_interna><nombre>Tortillas de maíz</nombre></producto><categoria>Abarrote básico</categoria><clase>A</clase><pct_acum>77.4</pct_acum><unidades>4</unidades><venta>96</venta><margen_unitario>6.72</margen_unitario><margen_total>26.88</margen_total><costo_estimado>true</costo_estimado><existencia>21</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.04</demanda_dia><cobertura_dias>472.5</cobertura_dias><rotacion>0.19</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 472 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>25</id><clave_interna>BE-005</clave_interna><nombre>Jugo de naranja</nombre></producto><categoria>Bebidas</categoria><clase>A</clase><pct_acum>79.2</pct_acum><unidades>4</unidades><venta>112</venta><margen_unitario>7.84</margen_unitario><margen_total>31.36</margen_total><costo_estimado>true</costo_estimado><existencia>82</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.04</demanda_dia><cobertura_dias>1845</cobertura_dias><rotacion>0.05</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1845 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>32</id><clave_interna>LA-004</clave_interna><nombre>Queso Oaxaca</nombre></producto><categoria>Lácteos y huevo</categoria><clase>A</clase><pct_acum>81.1</pct_acum><unidades>4</unidades><venta>288</venta><margen_unitario>20.16</margen_unitario><margen_total>80.64</margen_total><costo_estimado>true</costo_estimado><existencia>20</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.04</demanda_dia><cobertura_dias>450</cobertura_dias><rotacion>0.2</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 450 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>18</id><clave_interna>AB-018</clave_interna><nombre>Pan de caja blanco</nombre></producto><categoria>Abarrote básico</categoria><clase>B</clase><pct_acum>82.5</pct_acum><unidades>3</unidades><venta>132</venta><margen_unitario>12.32</margen_unitario><margen_total>36.96</margen_total><costo_estimado>true</costo_estimado><existencia>80</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.03</demanda_dia><cobertura_dias>2400</cobertura_dias><rotacion>0.04</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 2400 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>23</id><clave_interna>BE-003</clave_interna><nombre>Refresco de cola</nombre></producto><categoria>Bebidas</categoria><clase>B</clase><pct_acum>84</pct_acum><unidades>3</unidades><venta>115.5</venta><margen_unitario>10.78</margen_unitario><margen_total>32.34</margen_total><costo_estimado>true</costo_estimado><existencia>54</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.03</demanda_dia><cobertura_dias>1620</cobertura_dias><rotacion>0.06</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1620 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>36</id><clave_interna>LA-008</clave_interna><nombre>Jamón de pavo</nombre></producto><categoria>Lácteos y huevo</categoria><clase>B</clase><pct_acum>85.4</pct_acum><unidades>3</unidades><venta>138</venta><margen_unitario>12.88</margen_unitario><margen_total>38.64</margen_total><costo_estimado>true</costo_estimado><existencia>47</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.03</demanda_dia><cobertura_dias>1410</cobertura_dias><rotacion>0.06</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1410 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>47</id><clave_interna>HI-002</clave_interna><nombre>Shampoo</nombre></producto><categoria>Higiene personal</categoria><clase>B</clase><pct_acum>86.8</pct_acum><unidades>3</unidades><venta>162</venta><margen_unitario>15.12</margen_unitario><margen_total>45.36</margen_total><costo_estimado>true</costo_estimado><existencia>62</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.03</demanda_dia><cobertura_dias>1860</cobertura_dias><rotacion>0.05</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1860 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>49</id><clave_interna>HI-004</clave_interna><nombre>Desodorante</nombre></producto><categoria>Higiene personal</categoria><clase>B</clase><pct_acum>88.2</pct_acum><unidades>3</unidades><venta>144</venta><margen_unitario>13.44</margen_unitario><margen_total>40.32</margen_total><costo_estimado>true</costo_estimado><existencia>36</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.03</demanda_dia><cobertura_dias>1080</cobertura_dias><rotacion>0.08</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1080 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>8</id><clave_interna>AB-008</clave_interna><nombre>Pasta para sopa surtida</nombre></producto><categoria>Abarrote básico</categoria><clase>B</clase><pct_acum>89.2</pct_acum><unidades>2</unidades><venta>19</venta><margen_unitario>2.66</margen_unitario><margen_total>5.32</margen_total><costo_estimado>true</costo_estimado><existencia>21</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.02</demanda_dia><cobertura_dias>945</cobertura_dias><rotacion>0.1</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 945 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>15</id><clave_interna>AB-015</clave_interna><nombre>Avena en hojuelas</nombre></producto><categoria>Abarrote básico</categoria><clase>B</clase><pct_acum>90.1</pct_acum><unidades>2</unidades><venta>54</venta><margen_unitario>7.56</margen_unitario><margen_total>15.12</margen_total><costo_estimado>true</costo_estimado><existencia>52</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.02</demanda_dia><cobertura_dias>2340</cobertura_dias><rotacion>0.04</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 2340 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>16</id><clave_interna>AB-016</clave_interna><nombre>Galletas María</nombre></producto><categoria>Abarrote básico</categoria><clase>B</clase><pct_acum>91</pct_acum><unidades>2</unidades><venta>33</venta><margen_unitario>4.62</margen_unitario><margen_total>9.24</margen_total><costo_estimado>true</costo_estimado><existencia>84</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.02</demanda_dia><cobertura_dias>3780</cobertura_dias><rotacion>0.02</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 3780 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>22</id><clave_interna>BE-002</clave_interna><nombre>Agua embotellada</nombre></producto><categoria>Bebidas</categoria><clase>B</clase><pct_acum>92</pct_acum><unidades>2</unidades><venta>30</venta><margen_unitario>4.2</margen_unitario><margen_total>8.4</margen_total><costo_estimado>true</costo_estimado><existencia>72</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.02</demanda_dia><cobertura_dias>3240</cobertura_dias><rotacion>0.03</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 3240 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>24</id><clave_interna>BE-004</clave_interna><nombre>Refresco sabor manzana</nombre></producto><categoria>Bebidas</categoria><clase>B</clase><pct_acum>92.9</pct_acum><unidades>2</unidades><venta>72</venta><margen_unitario>10.08</margen_unitario><margen_total>20.16</margen_total><costo_estimado>true</costo_estimado><existencia>40</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.02</demanda_dia><cobertura_dias>1800</cobertura_dias><rotacion>0.05</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 1800 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>26</id><clave_interna>BE-006</clave_interna><nombre>Bebida de soya</nombre></producto><categoria>Bebidas</categoria><clase>B</clase><pct_acum>93.9</pct_acum><unidades>2</unidades><venta>64</venta><margen_unitario>8.96</margen_unitario><margen_total>17.92</margen_total><costo_estimado>true</costo_estimado><existencia>19</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.02</demanda_dia><cobertura_dias>855</cobertura_dias><rotacion>0.11</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 855 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>27</id><clave_interna>BE-007</clave_interna><nombre>Té helado de limón</nombre></producto><categoria>Bebidas</categoria><clase>B</clase><pct_acum>94.8</pct_acum><unidades>2</unidades><venta>34</venta><margen_unitario>4.76</margen_unitario><margen_total>9.52</margen_total><costo_estimado>true</costo_estimado><existencia>87</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.02</demanda_dia><cobertura_dias>3915</cobertura_dias><rotacion>0.02</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 3915 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>37</id><clave_interna>LI-001</clave_interna><nombre>Detergente en polvo</nombre></producto><categoria>Limpieza del hogar</categoria><clase>B</clase><pct_acum>95.8</pct_acum><unidades>2</unidades><venta>84</venta><margen_unitario>11.76</margen_unitario><margen_total>23.52</margen_total><costo_estimado>true</costo_estimado><existencia>15</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.02</demanda_dia><cobertura_dias>675</cobertura_dias><rotacion>0.13</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 675 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>42</id><clave_interna>LI-006</clave_interna><nombre>Papel higiénico</nombre></producto><categoria>Limpieza del hogar</categoria><clase>C</clase><pct_acum>96.7</pct_acum><unidades>2</unidades><venta>76</venta><margen_unitario>10.64</margen_unitario><margen_total>21.28</margen_total><costo_estimado>true</costo_estimado><existencia>68</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.02</demanda_dia><cobertura_dias>3060</cobertura_dias><rotacion>0.03</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 3060 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>43</id><clave_interna>LI-007</clave_interna><nombre>Servilletas</nombre></producto><categoria>Limpieza del hogar</categoria><clase>C</clase><pct_acum>97.6</pct_acum><unidades>2</unidades><venta>64</venta><margen_unitario>8.96</margen_unitario><margen_total>17.92</margen_total><costo_estimado>true</costo_estimado><existencia>73</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.02</demanda_dia><cobertura_dias>3285</cobertura_dias><rotacion>0.03</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 3285 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>9</id><clave_interna>AB-009</clave_interna><nombre>Atún en agua</nombre></producto><categoria>Abarrote básico</categoria><clase>C</clase><pct_acum>98.1</pct_acum><unidades>1</unidades><venta>21</venta><margen_unitario>5.88</margen_unitario><margen_total>5.88</margen_total><costo_estimado>true</costo_estimado><existencia>42</existencia><minimo>10</minimo><quiebres>0</quiebres><demanda_dia>0.01</demanda_dia><cobertura_dias>3780</cobertura_dias><rotacion>0.02</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 3780 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>21</id><clave_interna>BE-001</clave_interna><nombre>Agua purificada</nombre></producto><categoria>Bebidas</categoria><clase>C</clase><pct_acum>98.6</pct_acum><unidades>1</unidades><venta>38</venta><margen_unitario>10.64</margen_unitario><margen_total>10.64</margen_total><costo_estimado>true</costo_estimado><existencia>0</existencia><minimo>10</minimo><quiebres>2</quiebres><demanda_dia>0.01</demanda_dia><cobertura_dias>0</cobertura_dias><rotacion>99</rotacion><recomendacion>Aumentar</recomendacion><motivo>hubo quiebres</motivo><sugerido>1</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>33</id><clave_interna>LA-005</clave_interna><nombre>Crema ácida</nombre></producto><categoria>Lácteos y huevo</categoria><clase>C</clase><pct_acum>99.1</pct_acum><unidades>1</unidades><venta>36</venta><margen_unitario>10.08</margen_unitario><margen_total>10.08</margen_total><costo_estimado>true</costo_estimado><existencia>85</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.01</demanda_dia><cobertura_dias>7650</cobertura_dias><rotacion>0.01</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 7650 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>38</id><clave_interna>LI-002</clave_interna><nombre>Jabón para trastes</nombre></producto><categoria>Limpieza del hogar</categoria><clase>C</clase><pct_acum>99.5</pct_acum><unidades>1</unidades><venta>26</venta><margen_unitario>7.28</margen_unitario><margen_total>7.28</margen_total><costo_estimado>true</costo_estimado><existencia>47</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0.01</demanda_dia><cobertura_dias>4230</cobertura_dias><rotacion>0.02</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 4230 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>50</id><clave_interna>HI-005</clave_interna><nombre>Toallas femeninas</nombre></producto><categoria>Higiene personal</categoria><clase>C</clase><pct_acum>100</pct_acum><unidades>1</unidades><venta>36</venta><margen_unitario>10.08</margen_unitario><margen_total>10.08</margen_total><costo_estimado>true</costo_estimado><existencia>78</existencia><minimo>8</minimo><quiebres>0</quiebres><demanda_dia>0.01</demanda_dia><cobertura_dias>7020</cobertura_dias><rotacion>0.01</rotacion><recomendacion>Reducir</recomendacion><motivo>cobertura de 7020 días, exceso de stock</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila><fila><producto><id>31</id><clave_interna>LA-003</clave_interna><nombre>Queso fresco</nombre></producto><categoria>Lácteos y huevo</categoria><clase>C</clase><pct_acum>100</pct_acum><unidades>0</unidades><venta>0</venta><margen_unitario>16.24</margen_unitario><margen_total>0</margen_total><costo_estimado>true</costo_estimado><existencia>57</existencia><minimo>5</minimo><quiebres>0</quiebres><demanda_dia>0</demanda_dia><cobertura_dias xsi:nil="true" /><rotacion>0</rotacion><recomendacion>Eliminar</recomendacion><motivo>sin movimiento en la ventana de análisis</motivo><sugerido>0</sugerido><limitado_por xsi:nil="true" /></fila></filas><supuestos_usados><supuesto><clave>abc_a_pct</clave><valor>80</valor><modificado>false</modificado></supuesto><supuesto><clave>abc_b_pct</clave><valor>95</valor><modificado>false</modificado></supuesto><supuesto><clave>cobertura_dias_a</clave><valor>7</valor><modificado>false</modificado></supuesto><supuesto><clave>cobertura_dias_b</clave><valor>5</valor><modificado>false</modificado></supuesto><supuesto><clave>cobertura_dias_c</clave><valor>3</valor><modificado>false</modificado></supuesto><supuesto><clave>cobertura_dias_exceso</clave><valor>30</valor><modificado>false</modificado></supuesto><supuesto><clave>ventana_analisis_dias</clave><valor>90</valor><modificado>false</modificado></supuesto></supuestos_usados></surtido_analisis>
```

### SUR-07 · El operador analiza su microhub · PASA

**Objetivo.** Operador y supervisor solo trabajan con el suyo.

**Petición.** `GET http://surtido:5122/api/v1/surtido/analisis?microhub_id=1`

```http
Accept: application/json
X-Traza-Id: b91bc916-8ba0-4b43-b8de-16e153013414
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 320 ms · traza `b91bc916-8ba0-4b43-b8de-16e153013414`

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
    "reducir": 49,
    "eliminar": 1,
    "excluir": 0,
    "clase_a": 30,
    "clase_b": 13,
    "clase_c": 8,
    "unidades_a_comprar": 1,
    "con_costo_estimado": 51,
    "espacio": {
      "total": 3600.0,
      "ocupado": 2900.0,
      "sugerido": 1.0,
      "ocupacion_pct": 80.6
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
        "id": 7,
        "clave_interna": "AB-007",
        "nombre": "Harina de trigo"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 4.7,
      "unidades": 10,
      "venta": 245.0,
      "margen_unitario": 6.86,
      "margen_total": 68.6,
      "costo_estimado": true,
      "existencia": 14,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.11,
      "cobertura_dias": 126.0,
      "rotacion": 0.71,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 126 días, exceso de stock",
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
      "pct_acum": 9.4,
      "unidades": 10,
      "venta": 75.0,
      "margen_unitario": 2.1,
      "margen_total": 21.0,
      "costo_estimado": true,
      "existencia": 36,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.11,
      "cobertura_dias": 324.0,
      "rotacion": 0.28,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 324 días, exceso de stock",
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
      "pct_acum": 13.7,
      "unidades": 9,
      "venta": 99.0,
      "margen_unitario": 3.08,
      "margen_total": 27.72,
      "costo_estimado": true,
      "existencia": 56,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.1,
      "cobertura_dias": 560.0,
      "rotacion": 0.16,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 560 días, exceso de stock",
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
      "pct_acum": 17.9,
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
        "id": 39,
        "clave_interna": "LI-003",
        "nombre": "Cloro"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 21.7,
      "unidades": 8,
      "venta": 156.0,
      "margen_unitario": 5.46,
      "margen_total": 43.68,
      "costo_estimado": true,
      "existencia": 47,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.09,
      "cobertura_dias": 528.8,
      "rotacion": 0.17,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 529 días, exceso de stock",
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
      "pct_acum": 25.0,
      "unidades": 7,
      "venta": 224.0,
      "margen_unitario": 8.96,
      "margen_total": 62.72,
      "costo_estimado": true,
      "existencia": 80,
      "minimo": 10,
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
        "id": 1,
        "clave_interna": "AB-001",
        "nombre": "Frijol negro a granel"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 27.8,
      "unidades": 6,
      "venta": 231.0,
      "margen_unitario": 10.78,
      "margen_total": 64.68,
      "costo_estimado": true,
      "existencia": 60,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.07,
      "cobertura_dias": 900.0,
      "rotacion": 0.1,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 900 días, exceso de stock",
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
      "pct_acum": 30.7,
      "unidades": 6,
      "venta": 117.0,
      "margen_unitario": 5.46,
      "margen_total": 32.76,
      "costo_estimado": true,
      "existencia": 206,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.07,
      "cobertura_dias": 3090.0,
      "rotacion": 0.03,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 3090 días, exceso de stock",
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
      "pct_acum": 33.5,
      "unidades": 6,
      "venta": 165.0,
      "margen_unitario": 7.7,
      "margen_total": 46.2,
      "costo_estimado": true,
      "existencia": 48,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.07,
      "cobertura_dias": 720.0,
      "rotacion": 0.12,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 720 días, exceso de stock",
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
      "pct_acum": 36.3,
      "unidades": 6,
      "venta": 186.0,
      "margen_unitario": 8.68,
      "margen_total": 52.08,
      "costo_estimado": true,
      "existencia": 15,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.07,
      "cobertura_dias": 225.0,
      "rotacion": 0.4,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 225 días, exceso de stock",
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
      "pct_acum": 39.2,
      "unidades": 6,
      "venta": 168.0,
      "margen_unitario": 7.84,
      "margen_total": 47.04,
      "costo_estimado": true,
      "existencia": 16,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.07,
      "cobertura_dias": 240.0,
      "rotacion": 0.38,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 240 días, exceso de stock",
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
      "pct_acum": 42.0,
      "unidades": 6,
      "venta": 408.0,
      "margen_unitario": 19.04,
      "margen_total": 114.24,
      "costo_estimado": true,
      "existencia": 29,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.07,
      "cobertura_dias": 435.0,
      "rotacion": 0.21,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 435 días, exceso de stock",
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
      "pct_acum": 44.3,
      "unidades": 5,
      "venta": 149.5,
      "margen_unitario": 8.37,
      "margen_total": 41.85,
      "costo_estimado": true,
      "existencia": 35,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 630.0,
      "rotacion": 0.14,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 630 días, exceso de stock",
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
      "pct_acum": 46.7,
      "unidades": 5,
      "venta": 210.0,
      "margen_unitario": 11.76,
      "margen_total": 58.8,
      "costo_estimado": true,
      "existencia": 10,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 180.0,
      "rotacion": 0.5,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 180 días, exceso de stock",
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
      "pct_acum": 49.1,
      "unidades": 5,
      "venta": 115.0,
      "margen_unitario": 6.44,
      "margen_total": 32.2,
      "costo_estimado": true,
      "existencia": 31,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 558.0,
      "rotacion": 0.16,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 558 días, exceso de stock",
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
      "pct_acum": 51.4,
      "unidades": 5,
      "venta": 260.0,
      "margen_unitario": 14.56,
      "margen_total": 72.8,
      "costo_estimado": true,
      "existencia": 33,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 594.0,
      "rotacion": 0.15,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 594 días, exceso de stock",
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
      "pct_acum": 53.8,
      "unidades": 5,
      "venta": 120.0,
      "margen_unitario": 6.72,
      "margen_total": 33.6,
      "costo_estimado": true,
      "existencia": 79,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 1422.0,
      "rotacion": 0.06,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1422 días, exceso de stock",
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
      "pct_acum": 56.1,
      "unidades": 5,
      "venta": 220.0,
      "margen_unitario": 12.32,
      "margen_total": 61.6,
      "costo_estimado": true,
      "existencia": 13,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 234.0,
      "rotacion": 0.38,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 234 días, exceso de stock",
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
      "clase": "A",
      "pct_acum": 58.5,
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
      "clase": "A",
      "pct_acum": 60.8,
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
        "id": 44,
        "clave_interna": "LI-008",
        "nombre": "Bolsas para basura"
      },
      "categoria": "Limpieza del hogar",
      "clase": "A",
      "pct_acum": 63.2,
      "unidades": 5,
      "venta": 120.0,
      "margen_unitario": 6.72,
      "margen_total": 33.6,
      "costo_estimado": true,
      "existencia": 28,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 504.0,
      "rotacion": 0.18,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 504 días, exceso de stock",
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
      "pct_acum": 65.6,
      "unidades": 5,
      "venta": 90.0,
      "margen_unitario": 5.04,
      "margen_total": 25.2,
      "costo_estimado": true,
      "existencia": 46,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.06,
      "cobertura_dias": 828.0,
      "rotacion": 0.11,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 828 días, exceso de stock",
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
      "clase": "A",
      "pct_acum": 67.9,
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
      "clase": "A",
      "pct_acum": 69.8,
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
        "id": 5,
        "clave_interna": "AB-005",
        "nombre": "Sal de mesa"
      },
      "categoria": "Abarrote básico",
      "clase": "A",
      "pct_acum": 71.7,
      "unidades": 4,
      "venta": 56.0,
      "margen_unitario": 3.92,
      "margen_total": 15.68,
      "costo_estimado": true,
      "existencia": 30,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.04,
      "cobertura_dias": 675.0,
      "rotacion": 0.13,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 675 días, exceso de stock",
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
      "pct_acum": 73.6,
      "unidades": 4,
      "venta": 104.0,
      "margen_unitario": 7.28,
      "margen_total": 29.12,
      "costo_estimado": true,
      "existencia": 66,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.04,
      "cobertura_dias": 1485.0,
      "rotacion": 0.06,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1485 días, exceso de stock",
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
      "pct_acum": 75.5,
      "unidades": 4,
      "venta": 106.0,
      "margen_unitario": 7.42,
      "margen_total": 29.68,
      "costo_estimado": true,
      "existencia": 417,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.04,
      "cobertura_dias": 9382.5,
      "rotacion": 0.01,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 9382 días, exceso de stock",
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
      "pct_acum": 77.4,
      "unidades": 4,
      "venta": 96.0,
      "margen_unitario": 6.72,
      "margen_total": 26.88,
      "costo_estimado": true,
      "existencia": 21,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.04,
      "cobertura_dias": 472.5,
      "rotacion": 0.19,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 472 días, exceso de stock",
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
      "pct_acum": 79.2,
      "unidades": 4,
      "venta": 112.0,
      "margen_unitario": 7.84,
      "margen_total": 31.36,
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
        "id": 32,
        "clave_interna": "LA-004",
        "nombre": "Queso Oaxaca"
      },
      "categoria": "Lácteos y huevo",
      "clase": "A",
      "pct_acum": 81.1,
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
        "id": 18,
        "clave_interna": "AB-018",
        "nombre": "Pan de caja blanco"
      },
      "categoria": "Abarrote básico",
      "clase": "B",
      "pct_acum": 82.5,
      "unidades": 3,
      "venta": 132.0,
      "margen_unitario": 12.32,
      "margen_total": 36.96,
      "costo_estimado": true,
      "existencia": 80,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.03,
      "cobertura_dias": 2400.0,
      "rotacion": 0.04,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 2400 días, exceso de stock",
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
      "pct_acum": 84.0,
      "unidades": 3,
      "venta": 115.5,
      "margen_unitario": 10.78,
      "margen_total": 32.34,
      "costo_estimado": true,
      "existencia": 54,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.03,
      "cobertura_dias": 1620.0,
      "rotacion": 0.06,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1620 días, exceso de stock",
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
      "clase": "B",
      "pct_acum": 85.4,
      "unidades": 3,
      "venta": 138.0,
      "margen_unitario": 12.88,
      "margen_total": 38.64,
      "costo_estimado": true,
      "existencia": 47,
      "minimo": 8,
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
        "id": 47,
        "clave_interna": "HI-002",
        "nombre": "Shampoo"
      },
      "categoria": "Higiene personal",
      "clase": "B",
      "pct_acum": 86.8,
      "unidades": 3,
      "venta": 162.0,
      "margen_unitario": 15.12,
      "margen_total": 45.36,
      "costo_estimado": true,
      "existencia": 62,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.03,
      "cobertura_dias": 1860.0,
      "rotacion": 0.05,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1860 días, exceso de stock",
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
      "pct_acum": 88.2,
      "unidades": 3,
      "venta": 144.0,
      "margen_unitario": 13.44,
      "margen_total": 40.32,
      "costo_estimado": true,
      "existencia": 36,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.03,
      "cobertura_dias": 1080.0,
      "rotacion": 0.08,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1080 días, exceso de stock",
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
      "clase": "B",
      "pct_acum": 89.2,
      "unidades": 2,
      "venta": 19.0,
      "margen_unitario": 2.66,
      "margen_total": 5.32,
      "costo_estimado": true,
      "existencia": 21,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.02,
      "cobertura_dias": 945.0,
      "rotacion": 0.1,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 945 días, exceso de stock",
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
      "pct_acum": 90.1,
      "unidades": 2,
      "venta": 54.0,
      "margen_unitario": 7.56,
      "margen_total": 15.12,
      "costo_estimado": true,
      "existencia": 52,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.02,
      "cobertura_dias": 2340.0,
      "rotacion": 0.04,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 2340 días, exceso de stock",
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
      "pct_acum": 91.0,
      "unidades": 2,
      "venta": 33.0,
      "margen_unitario": 4.62,
      "margen_total": 9.24,
      "costo_estimado": true,
      "existencia": 84,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.02,
      "cobertura_dias": 3780.0,
      "rotacion": 0.02,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 3780 días, exceso de stock",
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
      "pct_acum": 92.0,
      "unidades": 2,
      "venta": 30.0,
      "margen_unitario": 4.2,
      "margen_total": 8.4,
      "costo_estimado": true,
      "existencia": 72,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.02,
      "cobertura_dias": 3240.0,
      "rotacion": 0.03,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 3240 días, exceso de stock",
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
      "pct_acum": 92.9,
      "unidades": 2,
      "venta": 72.0,
      "margen_unitario": 10.08,
      "margen_total": 20.16,
      "costo_estimado": true,
      "existencia": 40,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.02,
      "cobertura_dias": 1800.0,
      "rotacion": 0.05,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 1800 días, exceso de stock",
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
      "pct_acum": 93.9,
      "unidades": 2,
      "venta": 64.0,
      "margen_unitario": 8.96,
      "margen_total": 17.92,
      "costo_estimado": true,
      "existencia": 19,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.02,
      "cobertura_dias": 855.0,
      "rotacion": 0.11,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 855 días, exceso de stock",
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
      "clase": "B",
      "pct_acum": 94.8,
      "unidades": 2,
      "venta": 34.0,
      "margen_unitario": 4.76,
      "margen_total": 9.52,
      "costo_estimado": true,
      "existencia": 87,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.02,
      "cobertura_dias": 3915.0,
      "rotacion": 0.02,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 3915 días, exceso de stock",
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
      "pct_acum": 95.8,
      "unidades": 2,
      "venta": 84.0,
      "margen_unitario": 11.76,
      "margen_total": 23.52,
      "costo_estimado": true,
      "existencia": 15,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.02,
      "cobertura_dias": 675.0,
      "rotacion": 0.13,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 675 días, exceso de stock",
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
      "clase": "C",
      "pct_acum": 96.7,
      "unidades": 2,
      "venta": 76.0,
      "margen_unitario": 10.64,
      "margen_total": 21.28,
      "costo_estimado": true,
      "existencia": 68,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.02,
      "cobertura_dias": 3060.0,
      "rotacion": 0.03,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 3060 días, exceso de stock",
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
      "clase": "C",
      "pct_acum": 97.6,
      "unidades": 2,
      "venta": 64.0,
      "margen_unitario": 8.96,
      "margen_total": 17.92,
      "costo_estimado": true,
      "existencia": 73,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.02,
      "cobertura_dias": 3285.0,
      "rotacion": 0.03,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 3285 días, exceso de stock",
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
      "pct_acum": 98.1,
      "unidades": 1,
      "venta": 21.0,
      "margen_unitario": 5.88,
      "margen_total": 5.88,
      "costo_estimado": true,
      "existencia": 42,
      "minimo": 10,
      "quiebres": 0,
      "demanda_dia": 0.01,
      "cobertura_dias": 3780.0,
      "rotacion": 0.02,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 3780 días, exceso de stock",
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
      "pct_acum": 98.6,
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
    },
    {
      "producto": {
        "id": 33,
        "clave_interna": "LA-005",
        "nombre": "Crema ácida"
      },
      "categoria": "Lácteos y huevo",
      "clase": "C",
      "pct_acum": 99.1,
      "unidades": 1,
      "venta": 36.0,
      "margen_unitario": 10.08,
      "margen_total": 10.08,
      "costo_estimado": true,
      "existencia": 85,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.01,
      "cobertura_dias": 7650.0,
      "rotacion": 0.01,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 7650 días, exceso de stock",
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
      "pct_acum": 99.5,
      "unidades": 1,
      "venta": 26.0,
      "margen_unitario": 7.28,
      "margen_total": 7.28,
      "costo_estimado": true,
      "existencia": 47,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.01,
      "cobertura_dias": 4230.0,
      "rotacion": 0.02,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 4230 días, exceso de stock",
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
      "clase": "C",
      "pct_acum": 100.0,
      "unidades": 1,
      "venta": 36.0,
      "margen_unitario": 10.08,
      "margen_total": 10.08,
      "costo_estimado": true,
      "existencia": 78,
      "minimo": 8,
      "quiebres": 0,
      "demanda_dia": 0.01,
      "cobertura_dias": 7020.0,
      "rotacion": 0.01,
      "recomendacion": "Reducir",
      "motivo": "cobertura de 7020 días, exceso de stock",
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
      "pct_acum": 100.0,
      "unidades": 0,
      "venta": 0.0,
      "margen_unitario": 16.24,
      "margen_total": 0.0,
      "costo_estimado": true,
      "existencia": 57,
      "minimo": 5,
      "quiebres": 0,
      "demanda_dia": 0.0,
      "cobertura_dias": null,
      "rotacion": 0.0,
      "recomendacion": "Eliminar",
      "motivo": "sin movimiento en la ventana de análisis",
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
X-Traza-Id: df778de9-6360-404a-a252-52a253fe4e25
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 8 ms · traza `df778de9-6360-404a-a252-52a253fe4e25`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "df778de9-6360-404a-a252-52a253fe4e25"
  }
}
```

### SUR-09 · Restricciones de un microhub · PASA

**Objetivo.** Espacio y presupuesto.

**Petición.** `GET http://surtido:5122/api/v1/surtido/restricciones/1`

```http
Accept: application/json
X-Traza-Id: d7080e6a-e2cb-4953-aa94-77928e93927d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 30 ms · traza `d7080e6a-e2cb-4953-aa94-77928e93927d`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "espacio_total": 3600.0,
  "presupuesto": 120000.0,
  "actualizado_en": "2026-10-20T00:39:53-06:00"
}
```

### SUR-10 · Cambiar las restricciones · PASA

**Objetivo.** El planeador fija otro espacio y presupuesto.

**Petición.** `PUT http://surtido:5122/api/v1/surtido/restricciones/1`

```http
Accept: application/json
X-Traza-Id: 6ce78528-e042-4396-bc45-815d89672611
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "espacio_total": 3700.0,
  "presupuesto": 120000.0
}
```

**Respuesta.** HTTP 200 (esperado 200) · 62 ms · traza `6ce78528-e042-4396-bc45-815d89672611`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "espacio_total": 3700.0,
  "presupuesto": 120000.0,
  "actualizado_en": "2026-10-20T00:43:38-06:00"
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
      "actualizado_en": "2026-10-20T06:39:53.257638+00:00"
    },
    "valores_nuevos": {
      "espacio_total": 3700.0,
      "actualizado_en": "2026-10-20T06:43:38.518391+00:00"
    }
  }
]
```

### SUR-19 · Cambiar las restricciones con PATCH · PASA

**Objetivo.** PATCH es alias de PUT.

**Petición.** `PATCH http://surtido:5122/api/v1/surtido/restricciones/1`

```http
Accept: application/json
X-Traza-Id: 84c00e39-ee66-4a26-aae0-96957e72eb41
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "espacio_total": 3650.0,
  "presupuesto": 120000.0
}
```

**Respuesta.** HTTP 200 (esperado 200) · 54 ms · traza `84c00e39-ee66-4a26-aae0-96957e72eb41`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "espacio_total": 3650.0,
  "presupuesto": 120000.0,
  "actualizado_en": "2026-10-20T00:43:38-06:00"
}
```

### SUR-11 · Cambiar restricciones sin permiso · PASA

**Objetivo.** Solo surtido.editar.

**Petición.** `PUT http://surtido:5122/api/v1/surtido/restricciones/1`

```http
Accept: application/json
X-Traza-Id: 020ef34e-d08f-4f9c-816b-44f86bc994c9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{
  "espacio_total": 10
}
```

**Respuesta.** HTTP 403 (esperado 403) · 28 ms · traza `020ef34e-d08f-4f9c-816b-44f86bc994c9`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "020ef34e-d08f-4f9c-816b-44f86bc994c9"
  }
}
```

### SUR-12 · Espacio inválido · PASA

**Objetivo.** Mayor que cero.

**Petición.** `PUT http://surtido:5122/api/v1/surtido/restricciones/1`

```http
Accept: application/json
X-Traza-Id: 50562dd2-73b3-46db-a906-1bb039d40d4c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "espacio_total": 0
}
```

**Respuesta.** HTTP 422 (esperado 422) · 6 ms · traza `50562dd2-73b3-46db-a906-1bb039d40d4c`

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
    "traza_id": "50562dd2-73b3-46db-a906-1bb039d40d4c"
  }
}
```

### SUR-13 · Guardar la recomendación · PASA

**Objetivo.** Queda con sus líneas y los supuestos usados, para compararla después.

**Petición.** `POST http://surtido:5122/api/v1/surtido/recomendaciones`

```http
Accept: application/json
X-Traza-Id: 3a350c67-5387-417d-8f8e-b1372a476be9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "nota": "Evidencia de la Ola 2"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 439 ms · traza `3a350c67-5387-417d-8f8e-b1372a476be9`

```json
{
  "id": 17,
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
    "reducir": 49,
    "eliminar": 1,
    "excluir": 0,
    "clase_a": 30,
    "clase_b": 13,
    "clase_c": 8,
    "unidades_a_comprar": 1,
    "con_costo_estimado": 51,
    "espacio": {
      "total": 3600.0,
      "ocupado": 2900.0,
      "sugerido": 1.0,
      "ocupacion_pct": 80.6
    },
    "presupuesto": {
      "total": 120000.0,
      "requerido": 27.36,
      "uso_pct": 0.0
    }
  },
  "creado_por": 5,
  "creado_en": "2026-10-20T00:43:39-06:00",
  "lineas": [
    {
      "producto": {
        "id": 7,
        "clave_interna": "AB-007",
        "nombre": "Harina de trigo"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 10,
      "existencia": 14,
      "sugerido": 0,
      "margen_unitario": 6.86,
      "rotacion": 0.71,
      "motivo": "cobertura de 126 días, exceso de stock"
    },
    {
      "producto": {
        "id": 28,
        "clave_interna": "BE-008",
        "nombre": "Polvo para agua de sabor"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 10,
      "existencia": 36,
      "sugerido": 0,
      "margen_unitario": 2.1,
      "rotacion": 0.28,
      "motivo": "cobertura de 324 días, exceso de stock"
    },
    {
      "producto": {
        "id": 13,
        "clave_interna": "AB-013",
        "nombre": "Puré de tomate"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 9,
      "existencia": 56,
      "sugerido": 0,
      "margen_unitario": 3.08,
      "rotacion": 0.16,
      "motivo": "cobertura de 560 días, exceso de stock"
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
        "id": 39,
        "clave_interna": "LI-003",
        "nombre": "Cloro"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 8,
      "existencia": 47,
      "sugerido": 0,
      "margen_unitario": 5.46,
      "rotacion": 0.17,
      "motivo": "cobertura de 529 días, exceso de stock"
    },
    {
      "producto": {
        "id": 48,
        "clave_interna": "HI-003",
        "nombre": "Pasta dental"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 80,
      "sugerido": 0,
      "margen_unitario": 8.96,
      "rotacion": 0.09,
      "motivo": "cobertura de 1029 días, exceso de stock"
    },
    {
      "producto": {
        "id": 1,
        "clave_interna": "AB-001",
        "nombre": "Frijol negro a granel"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 6,
      "existencia": 60,
      "sugerido": 0,
      "margen_unitario": 10.78,
      "rotacion": 0.1,
      "motivo": "cobertura de 900 días, exceso de stock"
    },
    {
      "producto": {
        "id": 12,
        "clave_interna": "AB-012",
        "nombre": "Chiles jalapeños en escabeche"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 6,
      "existencia": 206,
      "sugerido": 0,
      "margen_unitario": 5.46,
      "rotacion": 0.03,
      "motivo": "cobertura de 3090 días, exceso de stock"
    },
    {
      "producto": {
        "id": 29,
        "clave_interna": "LA-001",
        "nombre": "Leche entera"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 6,
      "existencia": 48,
      "sugerido": 0,
      "margen_unitario": 7.7,
      "rotacion": 0.12,
      "motivo": "cobertura de 720 días, exceso de stock"
    },
    {
      "producto": {
        "id": 30,
        "clave_interna": "LA-002",
        "nombre": "Leche deslactosada"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 6,
      "existencia": 15,
      "sugerido": 0,
      "margen_unitario": 8.68,
      "rotacion": 0.4,
      "motivo": "cobertura de 225 días, exceso de stock"
    },
    {
      "producto": {
        "id": 40,
        "clave_interna": "LI-004",
        "nombre": "Limpiador multiusos"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 6,
      "existencia": 16,
      "sugerido": 0,
      "margen_unitario": 7.84,
      "rotacion": 0.38,
      "motivo": "cobertura de 240 días, exceso de stock"
    },
    {
      "producto": {
        "id": 51,
        "clave_interna": "HI-006",
        "nombre": "Pañal etapa 3"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 6,
      "existencia": 29,
      "sugerido": 0,
      "margen_unitario": 19.04,
      "rotacion": 0.21,
      "motivo": "cobertura de 435 días, exceso de stock"
    },
    {
      "producto": {
        "id": 2,
        "clave_interna": "AB-002",
        "nombre": "Arroz superextra"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 35,
      "sugerido": 0,
      "margen_unitario": 8.37,
      "rotacion": 0.14,
      "motivo": "cobertura de 630 días, exceso de stock"
    },
    {
      "producto": {
        "id": 3,
        "clave_interna": "AB-003",
        "nombre": "Aceite vegetal"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 10,
      "sugerido": 0,
      "margen_unitario": 11.76,
      "rotacion": 0.5,
      "motivo": "cobertura de 180 días, exceso de stock"
    },
    {
      "producto": {
        "id": 11,
        "clave_interna": "AB-011",
        "nombre": "Frijoles refritos"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 31,
      "sugerido": 0,
      "margen_unitario": 6.44,
      "rotacion": 0.16,
      "motivo": "cobertura de 558 días, exceso de stock"
    },
    {
      "producto": {
        "id": 14,
        "clave_interna": "AB-014",
        "nombre": "Café soluble"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 33,
      "sugerido": 0,
      "margen_unitario": 14.56,
      "rotacion": 0.15,
      "motivo": "cobertura de 594 días, exceso de stock"
    },
    {
      "producto": {
        "id": 20,
        "clave_interna": "AB-020",
        "nombre": "Lenteja"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 79,
      "sugerido": 0,
      "margen_unitario": 6.72,
      "rotacion": 0.06,
      "motivo": "cobertura de 1422 días, exceso de stock"
    },
    {
      "producto": {
        "id": 34,
        "clave_interna": "LA-006",
        "nombre": "Yogur natural"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 13,
      "sugerido": 0,
      "margen_unitario": 12.32,
      "rotacion": 0.38,
      "motivo": "cobertura de 234 días, exceso de stock"
    },
    {
      "producto": {
        "id": 35,
        "clave_interna": "LA-007",
        "nombre": "Mantequilla"
      },
      "clase": "A",
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
      "clase": "A",
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
        "id": 44,
        "clave_interna": "LI-008",
        "nombre": "Bolsas para basura"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 28,
      "sugerido": 0,
      "margen_unitario": 6.72,
      "rotacion": 0.18,
      "motivo": "cobertura de 504 días, exceso de stock"
    },
    {
      "producto": {
        "id": 45,
        "clave_interna": "LI-009",
        "nombre": "Fibra para trastes"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 46,
      "sugerido": 0,
      "margen_unitario": 5.04,
      "rotacion": 0.11,
      "motivo": "cobertura de 828 días, exceso de stock"
    },
    {
      "producto": {
        "id": 46,
        "clave_interna": "HI-001",
        "nombre": "Jabón de tocador"
      },
      "clase": "A",
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
      "clase": "A",
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
        "id": 5,
        "clave_interna": "AB-005",
        "nombre": "Sal de mesa"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 4,
      "existencia": 30,
      "sugerido": 0,
      "margen_unitario": 3.92,
      "rotacion": 0.13,
      "motivo": "cobertura de 675 días, exceso de stock"
    },
    {
      "producto": {
        "id": 6,
        "clave_interna": "AB-006",
        "nombre": "Harina de maíz nixtamalizado"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 4,
      "existencia": 66,
      "sugerido": 0,
      "margen_unitario": 7.28,
      "rotacion": 0.06,
      "motivo": "cobertura de 1485 días, exceso de stock"
    },
    {
      "producto": {
        "id": 10,
        "clave_interna": "AB-010",
        "nombre": "Sardina en salsa de tomate"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 4,
      "existencia": 417,
      "sugerido": 0,
      "margen_unitario": 7.42,
      "rotacion": 0.01,
      "motivo": "cobertura de 9382 días, exceso de stock"
    },
    {
      "producto": {
        "id": 17,
        "clave_interna": "AB-017",
        "nombre": "Tortillas de maíz"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 4,
      "existencia": 21,
      "sugerido": 0,
      "margen_unitario": 6.72,
      "rotacion": 0.19,
      "motivo": "cobertura de 472 días, exceso de stock"
    },
    {
      "producto": {
        "id": 25,
        "clave_interna": "BE-005",
        "nombre": "Jugo de naranja"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 4,
      "existencia": 82,
      "sugerido": 0,
      "margen_unitario": 7.84,
      "rotacion": 0.05,
      "motivo": "cobertura de 1845 días, exceso de stock"
    },
    {
      "producto": {
        "id": 32,
        "clave_interna": "LA-004",
        "nombre": "Queso Oaxaca"
      },
      "clase": "A",
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
        "id": 18,
        "clave_interna": "AB-018",
        "nombre": "Pan de caja blanco"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 3,
      "existencia": 80,
      "sugerido": 0,
      "margen_unitario": 12.32,
      "rotacion": 0.04,
      "motivo": "cobertura de 2400 días, exceso de stock"
    },
    {
      "producto": {
        "id": 23,
        "clave_interna": "BE-003",
        "nombre": "Refresco de cola"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 3,
      "existencia": 54,
      "sugerido": 0,
      "margen_unitario": 10.78,
      "rotacion": 0.06,
      "motivo": "cobertura de 1620 días, exceso de stock"
    },
    {
      "producto": {
        "id": 36,
        "clave_interna": "LA-008",
        "nombre": "Jamón de pavo"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 3,
      "existencia": 47,
      "sugerido": 0,
      "margen_unitario": 12.88,
      "rotacion": 0.06,
      "motivo": "cobertura de 1410 días, exceso de stock"
    },
    {
      "producto": {
        "id": 47,
        "clave_interna": "HI-002",
        "nombre": "Shampoo"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 3,
      "existencia": 62,
      "sugerido": 0,
      "margen_unitario": 15.12,
      "rotacion": 0.05,
      "motivo": "cobertura de 1860 días, exceso de stock"
    },
    {
      "producto": {
        "id": 49,
        "clave_interna": "HI-004",
        "nombre": "Desodorante"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 3,
      "existencia": 36,
      "sugerido": 0,
      "margen_unitario": 13.44,
      "rotacion": 0.08,
      "motivo": "cobertura de 1080 días, exceso de stock"
    },
    {
      "producto": {
        "id": 8,
        "clave_interna": "AB-008",
        "nombre": "Pasta para sopa surtida"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 2,
      "existencia": 21,
      "sugerido": 0,
      "margen_unitario": 2.66,
      "rotacion": 0.1,
      "motivo": "cobertura de 945 días, exceso de stock"
    },
    {
      "producto": {
        "id": 15,
        "clave_interna": "AB-015",
        "nombre": "Avena en hojuelas"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 2,
      "existencia": 52,
      "sugerido": 0,
      "margen_unitario": 7.56,
      "rotacion": 0.04,
      "motivo": "cobertura de 2340 días, exceso de stock"
    },
    {
      "producto": {
        "id": 16,
        "clave_interna": "AB-016",
        "nombre": "Galletas María"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 2,
      "existencia": 84,
      "sugerido": 0,
      "margen_unitario": 4.62,
      "rotacion": 0.02,
      "motivo": "cobertura de 3780 días, exceso de stock"
    },
    {
      "producto": {
        "id": 22,
        "clave_interna": "BE-002",
        "nombre": "Agua embotellada"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 2,
      "existencia": 72,
      "sugerido": 0,
      "margen_unitario": 4.2,
      "rotacion": 0.03,
      "motivo": "cobertura de 3240 días, exceso de stock"
    },
    {
      "producto": {
        "id": 24,
        "clave_interna": "BE-004",
        "nombre": "Refresco sabor manzana"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 2,
      "existencia": 40,
      "sugerido": 0,
      "margen_unitario": 10.08,
      "rotacion": 0.05,
      "motivo": "cobertura de 1800 días, exceso de stock"
    },
    {
      "producto": {
        "id": 26,
        "clave_interna": "BE-006",
        "nombre": "Bebida de soya"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 2,
      "existencia": 19,
      "sugerido": 0,
      "margen_unitario": 8.96,
      "rotacion": 0.11,
      "motivo": "cobertura de 855 días, exceso de stock"
    },
    {
      "producto": {
        "id": 27,
        "clave_interna": "BE-007",
        "nombre": "Té helado de limón"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 2,
      "existencia": 87,
      "sugerido": 0,
      "margen_unitario": 4.76,
      "rotacion": 0.02,
      "motivo": "cobertura de 3915 días, exceso de stock"
    },
    {
      "producto": {
        "id": 37,
        "clave_interna": "LI-001",
        "nombre": "Detergente en polvo"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 2,
      "existencia": 15,
      "sugerido": 0,
      "margen_unitario": 11.76,
      "rotacion": 0.13,
      "motivo": "cobertura de 675 días, exceso de stock"
    },
    {
      "producto": {
        "id": 42,
        "clave_interna": "LI-006",
        "nombre": "Papel higiénico"
      },
      "clase": "C",
      "recomendacion": "Reducir",
      "unidades": 2,
      "existencia": 68,
      "sugerido": 0,
      "margen_unitario": 10.64,
      "rotacion": 0.03,
      "motivo": "cobertura de 3060 días, exceso de stock"
    },
    {
      "producto": {
        "id": 43,
        "clave_interna": "LI-007",
        "nombre": "Servilletas"
      },
      "clase": "C",
      "recomendacion": "Reducir",
      "unidades": 2,
      "existencia": 73,
      "sugerido": 0,
      "margen_unitario": 8.96,
      "rotacion": 0.03,
      "motivo": "cobertura de 3285 días, exceso de stock"
    },
    {
      "producto": {
        "id": 9,
        "clave_interna": "AB-009",
        "nombre": "Atún en agua"
      },
      "clase": "C",
      "recomendacion": "Reducir",
      "unidades": 1,
      "existencia": 42,
      "sugerido": 0,
      "margen_unitario": 5.88,
      "rotacion": 0.02,
      "motivo": "cobertura de 3780 días, exceso de stock"
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
    },
    {
      "producto": {
        "id": 33,
        "clave_interna": "LA-005",
        "nombre": "Crema ácida"
      },
      "clase": "C",
      "recomendacion": "Reducir",
      "unidades": 1,
      "existencia": 85,
      "sugerido": 0,
      "margen_unitario": 10.08,
      "rotacion": 0.01,
      "motivo": "cobertura de 7650 días, exceso de stock"
    },
    {
      "producto": {
        "id": 38,
        "clave_interna": "LI-002",
        "nombre": "Jabón para trastes"
      },
      "clase": "C",
      "recomendacion": "Reducir",
      "unidades": 1,
      "existencia": 47,
      "sugerido": 0,
      "margen_unitario": 7.28,
      "rotacion": 0.02,
      "motivo": "cobertura de 4230 días, exceso de stock"
    },
    {
      "producto": {
        "id": 50,
        "clave_interna": "HI-005",
        "nombre": "Toallas femeninas"
      },
      "clase": "C",
      "recomendacion": "Reducir",
      "unidades": 1,
      "existencia": 78,
      "sugerido": 0,
      "margen_unitario": 10.08,
      "rotacion": 0.01,
      "motivo": "cobertura de 7020 días, exceso de stock"
    },
    {
      "producto": {
        "id": 31,
        "clave_interna": "LA-003",
        "nombre": "Queso fresco"
      },
      "clase": "C",
      "recomendacion": "Eliminar",
      "unidades": 0,
      "existencia": 57,
      "sugerido": 0,
      "margen_unitario": 16.24,
      "rotacion": 0.0,
      "motivo": "sin movimiento en la ventana de análisis"
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
    "id": 17,
    "microhub_id": 1,
    "resumen": {
      "productos": 51,
      "aumentar": 1,
      "mantener": 0,
      "reducir": 49,
      "eliminar": 1,
      "excluir": 0,
      "clase_a": 30,
      "clase_b": 13,
      "clase_c": 8,
      "unidades_a_comprar": 1,
      "con_costo_estimado": 51,
      "espacio": {
        "total": 3600.0,
        "ocupado": 2900.0,
        "sugerido": 1.0,
        "ocupacion_pct": 80.6
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
    "accion": "Eliminar",
    "lineas": 1,
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
X-Traza-Id: 70c03ea0-45dd-4567-ac01-8491516db92f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 50 ms · traza `70c03ea0-45dd-4567-ac01-8491516db92f`

```json
{
  "datos": [
    {
      "id": 17,
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
        "reducir": 49,
        "eliminar": 1,
        "excluir": 0,
        "clase_a": 30,
        "clase_b": 13,
        "clase_c": 8,
        "unidades_a_comprar": 1,
        "con_costo_estimado": 51,
        "espacio": {
          "total": 3600.0,
          "ocupado": 2900.0,
          "sugerido": 1.0,
          "ocupacion_pct": 80.6
        },
        "presupuesto": {
          "total": 120000.0,
          "requerido": 27.36,
          "uso_pct": 0.0
        }
      },
      "creado_por": 5,
      "creado_en": "2026-10-20T00:43:39-06:00"
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

**Petición.** `GET http://surtido:5122/api/v1/surtido/recomendaciones/17`

```http
Accept: application/json
X-Traza-Id: 2ca609d3-185c-43f1-b429-e8f0aa51e0ca
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 48 ms · traza `2ca609d3-185c-43f1-b429-e8f0aa51e0ca`

```json
{
  "id": 17,
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
    "reducir": 49,
    "eliminar": 1,
    "excluir": 0,
    "clase_a": 30,
    "clase_b": 13,
    "clase_c": 8,
    "unidades_a_comprar": 1,
    "con_costo_estimado": 51,
    "espacio": {
      "total": 3600.0,
      "ocupado": 2900.0,
      "sugerido": 1.0,
      "ocupacion_pct": 80.6
    },
    "presupuesto": {
      "total": 120000.0,
      "requerido": 27.36,
      "uso_pct": 0.0
    }
  },
  "creado_por": 5,
  "creado_en": "2026-10-20T00:43:39-06:00",
  "lineas": [
    {
      "producto": {
        "id": 7,
        "clave_interna": "AB-007",
        "nombre": "Harina de trigo"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 10,
      "existencia": 14,
      "sugerido": 0,
      "margen_unitario": 6.86,
      "rotacion": 0.71,
      "motivo": "cobertura de 126 días, exceso de stock"
    },
    {
      "producto": {
        "id": 28,
        "clave_interna": "BE-008",
        "nombre": "Polvo para agua de sabor"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 10,
      "existencia": 36,
      "sugerido": 0,
      "margen_unitario": 2.1,
      "rotacion": 0.28,
      "motivo": "cobertura de 324 días, exceso de stock"
    },
    {
      "producto": {
        "id": 13,
        "clave_interna": "AB-013",
        "nombre": "Puré de tomate"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 9,
      "existencia": 56,
      "sugerido": 0,
      "margen_unitario": 3.08,
      "rotacion": 0.16,
      "motivo": "cobertura de 560 días, exceso de stock"
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
        "id": 39,
        "clave_interna": "LI-003",
        "nombre": "Cloro"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 8,
      "existencia": 47,
      "sugerido": 0,
      "margen_unitario": 5.46,
      "rotacion": 0.17,
      "motivo": "cobertura de 529 días, exceso de stock"
    },
    {
      "producto": {
        "id": 48,
        "clave_interna": "HI-003",
        "nombre": "Pasta dental"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 7,
      "existencia": 80,
      "sugerido": 0,
      "margen_unitario": 8.96,
      "rotacion": 0.09,
      "motivo": "cobertura de 1029 días, exceso de stock"
    },
    {
      "producto": {
        "id": 1,
        "clave_interna": "AB-001",
        "nombre": "Frijol negro a granel"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 6,
      "existencia": 60,
      "sugerido": 0,
      "margen_unitario": 10.78,
      "rotacion": 0.1,
      "motivo": "cobertura de 900 días, exceso de stock"
    },
    {
      "producto": {
        "id": 12,
        "clave_interna": "AB-012",
        "nombre": "Chiles jalapeños en escabeche"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 6,
      "existencia": 206,
      "sugerido": 0,
      "margen_unitario": 5.46,
      "rotacion": 0.03,
      "motivo": "cobertura de 3090 días, exceso de stock"
    },
    {
      "producto": {
        "id": 29,
        "clave_interna": "LA-001",
        "nombre": "Leche entera"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 6,
      "existencia": 48,
      "sugerido": 0,
      "margen_unitario": 7.7,
      "rotacion": 0.12,
      "motivo": "cobertura de 720 días, exceso de stock"
    },
    {
      "producto": {
        "id": 30,
        "clave_interna": "LA-002",
        "nombre": "Leche deslactosada"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 6,
      "existencia": 15,
      "sugerido": 0,
      "margen_unitario": 8.68,
      "rotacion": 0.4,
      "motivo": "cobertura de 225 días, exceso de stock"
    },
    {
      "producto": {
        "id": 40,
        "clave_interna": "LI-004",
        "nombre": "Limpiador multiusos"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 6,
      "existencia": 16,
      "sugerido": 0,
      "margen_unitario": 7.84,
      "rotacion": 0.38,
      "motivo": "cobertura de 240 días, exceso de stock"
    },
    {
      "producto": {
        "id": 51,
        "clave_interna": "HI-006",
        "nombre": "Pañal etapa 3"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 6,
      "existencia": 29,
      "sugerido": 0,
      "margen_unitario": 19.04,
      "rotacion": 0.21,
      "motivo": "cobertura de 435 días, exceso de stock"
    },
    {
      "producto": {
        "id": 2,
        "clave_interna": "AB-002",
        "nombre": "Arroz superextra"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 35,
      "sugerido": 0,
      "margen_unitario": 8.37,
      "rotacion": 0.14,
      "motivo": "cobertura de 630 días, exceso de stock"
    },
    {
      "producto": {
        "id": 3,
        "clave_interna": "AB-003",
        "nombre": "Aceite vegetal"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 10,
      "sugerido": 0,
      "margen_unitario": 11.76,
      "rotacion": 0.5,
      "motivo": "cobertura de 180 días, exceso de stock"
    },
    {
      "producto": {
        "id": 11,
        "clave_interna": "AB-011",
        "nombre": "Frijoles refritos"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 31,
      "sugerido": 0,
      "margen_unitario": 6.44,
      "rotacion": 0.16,
      "motivo": "cobertura de 558 días, exceso de stock"
    },
    {
      "producto": {
        "id": 14,
        "clave_interna": "AB-014",
        "nombre": "Café soluble"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 33,
      "sugerido": 0,
      "margen_unitario": 14.56,
      "rotacion": 0.15,
      "motivo": "cobertura de 594 días, exceso de stock"
    },
    {
      "producto": {
        "id": 20,
        "clave_interna": "AB-020",
        "nombre": "Lenteja"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 79,
      "sugerido": 0,
      "margen_unitario": 6.72,
      "rotacion": 0.06,
      "motivo": "cobertura de 1422 días, exceso de stock"
    },
    {
      "producto": {
        "id": 34,
        "clave_interna": "LA-006",
        "nombre": "Yogur natural"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 13,
      "sugerido": 0,
      "margen_unitario": 12.32,
      "rotacion": 0.38,
      "motivo": "cobertura de 234 días, exceso de stock"
    },
    {
      "producto": {
        "id": 35,
        "clave_interna": "LA-007",
        "nombre": "Mantequilla"
      },
      "clase": "A",
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
      "clase": "A",
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
        "id": 44,
        "clave_interna": "LI-008",
        "nombre": "Bolsas para basura"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 28,
      "sugerido": 0,
      "margen_unitario": 6.72,
      "rotacion": 0.18,
      "motivo": "cobertura de 504 días, exceso de stock"
    },
    {
      "producto": {
        "id": 45,
        "clave_interna": "LI-009",
        "nombre": "Fibra para trastes"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 5,
      "existencia": 46,
      "sugerido": 0,
      "margen_unitario": 5.04,
      "rotacion": 0.11,
      "motivo": "cobertura de 828 días, exceso de stock"
    },
    {
      "producto": {
        "id": 46,
        "clave_interna": "HI-001",
        "nombre": "Jabón de tocador"
      },
      "clase": "A",
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
      "clase": "A",
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
        "id": 5,
        "clave_interna": "AB-005",
        "nombre": "Sal de mesa"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 4,
      "existencia": 30,
      "sugerido": 0,
      "margen_unitario": 3.92,
      "rotacion": 0.13,
      "motivo": "cobertura de 675 días, exceso de stock"
    },
    {
      "producto": {
        "id": 6,
        "clave_interna": "AB-006",
        "nombre": "Harina de maíz nixtamalizado"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 4,
      "existencia": 66,
      "sugerido": 0,
      "margen_unitario": 7.28,
      "rotacion": 0.06,
      "motivo": "cobertura de 1485 días, exceso de stock"
    },
    {
      "producto": {
        "id": 10,
        "clave_interna": "AB-010",
        "nombre": "Sardina en salsa de tomate"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 4,
      "existencia": 417,
      "sugerido": 0,
      "margen_unitario": 7.42,
      "rotacion": 0.01,
      "motivo": "cobertura de 9382 días, exceso de stock"
    },
    {
      "producto": {
        "id": 17,
        "clave_interna": "AB-017",
        "nombre": "Tortillas de maíz"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 4,
      "existencia": 21,
      "sugerido": 0,
      "margen_unitario": 6.72,
      "rotacion": 0.19,
      "motivo": "cobertura de 472 días, exceso de stock"
    },
    {
      "producto": {
        "id": 25,
        "clave_interna": "BE-005",
        "nombre": "Jugo de naranja"
      },
      "clase": "A",
      "recomendacion": "Reducir",
      "unidades": 4,
      "existencia": 82,
      "sugerido": 0,
      "margen_unitario": 7.84,
      "rotacion": 0.05,
      "motivo": "cobertura de 1845 días, exceso de stock"
    },
    {
      "producto": {
        "id": 32,
        "clave_interna": "LA-004",
        "nombre": "Queso Oaxaca"
      },
      "clase": "A",
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
        "id": 18,
        "clave_interna": "AB-018",
        "nombre": "Pan de caja blanco"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 3,
      "existencia": 80,
      "sugerido": 0,
      "margen_unitario": 12.32,
      "rotacion": 0.04,
      "motivo": "cobertura de 2400 días, exceso de stock"
    },
    {
      "producto": {
        "id": 23,
        "clave_interna": "BE-003",
        "nombre": "Refresco de cola"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 3,
      "existencia": 54,
      "sugerido": 0,
      "margen_unitario": 10.78,
      "rotacion": 0.06,
      "motivo": "cobertura de 1620 días, exceso de stock"
    },
    {
      "producto": {
        "id": 36,
        "clave_interna": "LA-008",
        "nombre": "Jamón de pavo"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 3,
      "existencia": 47,
      "sugerido": 0,
      "margen_unitario": 12.88,
      "rotacion": 0.06,
      "motivo": "cobertura de 1410 días, exceso de stock"
    },
    {
      "producto": {
        "id": 47,
        "clave_interna": "HI-002",
        "nombre": "Shampoo"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 3,
      "existencia": 62,
      "sugerido": 0,
      "margen_unitario": 15.12,
      "rotacion": 0.05,
      "motivo": "cobertura de 1860 días, exceso de stock"
    },
    {
      "producto": {
        "id": 49,
        "clave_interna": "HI-004",
        "nombre": "Desodorante"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 3,
      "existencia": 36,
      "sugerido": 0,
      "margen_unitario": 13.44,
      "rotacion": 0.08,
      "motivo": "cobertura de 1080 días, exceso de stock"
    },
    {
      "producto": {
        "id": 8,
        "clave_interna": "AB-008",
        "nombre": "Pasta para sopa surtida"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 2,
      "existencia": 21,
      "sugerido": 0,
      "margen_unitario": 2.66,
      "rotacion": 0.1,
      "motivo": "cobertura de 945 días, exceso de stock"
    },
    {
      "producto": {
        "id": 15,
        "clave_interna": "AB-015",
        "nombre": "Avena en hojuelas"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 2,
      "existencia": 52,
      "sugerido": 0,
      "margen_unitario": 7.56,
      "rotacion": 0.04,
      "motivo": "cobertura de 2340 días, exceso de stock"
    },
    {
      "producto": {
        "id": 16,
        "clave_interna": "AB-016",
        "nombre": "Galletas María"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 2,
      "existencia": 84,
      "sugerido": 0,
      "margen_unitario": 4.62,
      "rotacion": 0.02,
      "motivo": "cobertura de 3780 días, exceso de stock"
    },
    {
      "producto": {
        "id": 22,
        "clave_interna": "BE-002",
        "nombre": "Agua embotellada"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 2,
      "existencia": 72,
      "sugerido": 0,
      "margen_unitario": 4.2,
      "rotacion": 0.03,
      "motivo": "cobertura de 3240 días, exceso de stock"
    },
    {
      "producto": {
        "id": 24,
        "clave_interna": "BE-004",
        "nombre": "Refresco sabor manzana"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 2,
      "existencia": 40,
      "sugerido": 0,
      "margen_unitario": 10.08,
      "rotacion": 0.05,
      "motivo": "cobertura de 1800 días, exceso de stock"
    },
    {
      "producto": {
        "id": 26,
        "clave_interna": "BE-006",
        "nombre": "Bebida de soya"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 2,
      "existencia": 19,
      "sugerido": 0,
      "margen_unitario": 8.96,
      "rotacion": 0.11,
      "motivo": "cobertura de 855 días, exceso de stock"
    },
    {
      "producto": {
        "id": 27,
        "clave_interna": "BE-007",
        "nombre": "Té helado de limón"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 2,
      "existencia": 87,
      "sugerido": 0,
      "margen_unitario": 4.76,
      "rotacion": 0.02,
      "motivo": "cobertura de 3915 días, exceso de stock"
    },
    {
      "producto": {
        "id": 37,
        "clave_interna": "LI-001",
        "nombre": "Detergente en polvo"
      },
      "clase": "B",
      "recomendacion": "Reducir",
      "unidades": 2,
      "existencia": 15,
      "sugerido": 0,
      "margen_unitario": 11.76,
      "rotacion": 0.13,
      "motivo": "cobertura de 675 días, exceso de stock"
    },
    {
      "producto": {
        "id": 42,
        "clave_interna": "LI-006",
        "nombre": "Papel higiénico"
      },
      "clase": "C",
      "recomendacion": "Reducir",
      "unidades": 2,
      "existencia": 68,
      "sugerido": 0,
      "margen_unitario": 10.64,
      "rotacion": 0.03,
      "motivo": "cobertura de 3060 días, exceso de stock"
    },
    {
      "producto": {
        "id": 43,
        "clave_interna": "LI-007",
        "nombre": "Servilletas"
      },
      "clase": "C",
      "recomendacion": "Reducir",
      "unidades": 2,
      "existencia": 73,
      "sugerido": 0,
      "margen_unitario": 8.96,
      "rotacion": 0.03,
      "motivo": "cobertura de 3285 días, exceso de stock"
    },
    {
      "producto": {
        "id": 9,
        "clave_interna": "AB-009",
        "nombre": "Atún en agua"
      },
      "clase": "C",
      "recomendacion": "Reducir",
      "unidades": 1,
      "existencia": 42,
      "sugerido": 0,
      "margen_unitario": 5.88,
      "rotacion": 0.02,
      "motivo": "cobertura de 3780 días, exceso de stock"
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
    },
    {
      "producto": {
        "id": 33,
        "clave_interna": "LA-005",
        "nombre": "Crema ácida"
      },
      "clase": "C",
      "recomendacion": "Reducir",
      "unidades": 1,
      "existencia": 85,
      "sugerido": 0,
      "margen_unitario": 10.08,
      "rotacion": 0.01,
      "motivo": "cobertura de 7650 días, exceso de stock"
    },
    {
      "producto": {
        "id": 38,
        "clave_interna": "LI-002",
        "nombre": "Jabón para trastes"
      },
      "clase": "C",
      "recomendacion": "Reducir",
      "unidades": 1,
      "existencia": 47,
      "sugerido": 0,
      "margen_unitario": 7.28,
      "rotacion": 0.02,
      "motivo": "cobertura de 4230 días, exceso de stock"
    },
    {
      "producto": {
        "id": 50,
        "clave_interna": "HI-005",
        "nombre": "Toallas femeninas"
      },
      "clase": "C",
      "recomendacion": "Reducir",
      "unidades": 1,
      "existencia": 78,
      "sugerido": 0,
      "margen_unitario": 10.08,
      "rotacion": 0.01,
      "motivo": "cobertura de 7020 días, exceso de stock"
    },
    {
      "producto": {
        "id": 31,
        "clave_interna": "LA-003",
        "nombre": "Queso fresco"
      },
      "clase": "C",
      "recomendacion": "Eliminar",
      "unidades": 0,
      "existencia": 57,
      "sugerido": 0,
      "margen_unitario": 16.24,
      "rotacion": 0.0,
      "motivo": "sin movimiento en la ventana de análisis"
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

**Petición.** `GET http://surtido:5122/api/v1/surtido/recomendaciones/17`

```http
Accept: application/json
X-Traza-Id: 6a71791f-a0b7-4c59-b7a6-18c0849ac3a4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 22 ms · traza `6a71791f-a0b7-4c59-b7a6-18c0849ac3a4`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "6a71791f-a0b7-4c59-b7a6-18c0849ac3a4"
  }
}
```

### SUR-16 · Guardar sin permiso · PASA

**Objetivo.** El operador no tiene surtido.editar.

**Petición.** `POST http://surtido:5122/api/v1/surtido/recomendaciones`

```http
Accept: application/json
X-Traza-Id: 51ea96c6-d84f-48a7-bdbb-705b54a19b43
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1
}
```

**Respuesta.** HTTP 403 (esperado 403) · 27 ms · traza `51ea96c6-d84f-48a7-bdbb-705b54a19b43`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "51ea96c6-d84f-48a7-bdbb-705b54a19b43"
  }
}
```

### SUR-17 · Supuestos del surtido · PASA

**Objetivo.** Cortes ABC, días de cobertura y ventana de análisis.

**Petición.** `GET http://surtido:5122/api/v1/surtido/supuestos`

```http
Accept: application/json
X-Traza-Id: 93159c91-4ff2-41b7-8ced-fa2506600abc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 36 ms · traza `93159c91-4ff2-41b7-8ced-fa2506600abc`

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
X-Traza-Id: 53ff4234-3724-4c0b-8698-e65e33151e73
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 74 ms · traza `53ff4234-3724-4c0b-8698-e65e33151e73`

```json
{
  "datos": [
    {
      "id": 298,
      "folio": "PED-20261020-000298",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "latitud": 25.753225,
      "longitud": -100.365213,
      "total": 121.0,
      "listo_en": "2026-10-20T00:43:39-06:00"
    },
    {
      "id": 299,
      "folio": "PED-20261020-000299",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "latitud": 25.751679,
      "longitud": -100.366615,
      "total": 133.0,
      "listo_en": "2026-10-20T00:43:39-06:00"
    },
    {
      "id": 301,
      "folio": "PED-20261020-000301",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "latitud": 25.753225,
      "longitud": -100.365213,
      "total": 123.0,
      "listo_en": "2026-10-20T00:43:39-06:00"
    },
    {
      "id": 302,
      "folio": "PED-20261020-000302",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "latitud": 25.751679,
      "longitud": -100.366615,
      "total": 141.0,
      "listo_en": "2026-10-20T00:43:39-06:00"
    },
    {
      "id": 303,
      "folio": "PED-20261020-000303",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "latitud": 25.752587,
      "longitud": -100.364483,
      "total": 155.0,
      "listo_en": "2026-10-20T00:43:39-06:00"
    },
    {
      "id": 304,
      "folio": "PED-20261020-000304",
      "zona": {
        "id": 2,
        "nombre": "Valles de San Bernabé"
      },
      "latitud": 25.752587,
      "longitud": -100.364483,
      "total": 169.0,
      "listo_en": "2026-10-20T00:43:39-06:00"
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
    "id": 298,
    "folio": "PED-20261020-000298",
    "estado": "en_preparacion",
    "zona_id": 2,
    "listo": true
  },
  {
    "id": 299,
    "folio": "PED-20261020-000299",
    "estado": "en_preparacion",
    "zona_id": 2,
    "listo": true
  },
  {
    "id": 301,
    "folio": "PED-20261020-000301",
    "estado": "en_preparacion",
    "zona_id": 2,
    "listo": true
  },
  {
    "id": 302,
    "folio": "PED-20261020-000302",
    "estado": "en_preparacion",
    "zona_id": 2,
    "listo": true
  },
  {
    "id": 303,
    "folio": "PED-20261020-000303",
    "estado": "en_preparacion",
    "zona_id": 2,
    "listo": true
  },
  {
    "id": 304,
    "folio": "PED-20261020-000304",
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
X-Traza-Id: 60186d4c-bbfd-4a48-bb6b-4234b8423460
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "pedido_ids": [
    298,
    299,
    301,
    302,
    303,
    304
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 184 ms · traza `60186d4c-bbfd-4a48-bb6b-4234b8423460`

```json
{
  "id": null,
  "estado": "calculo",
  "version": 1,
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "fecha": "2026-10-20",
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
            "id": 299,
            "folio": "PED-20261020-000299"
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
            "id": 302,
            "folio": "PED-20261020-000302"
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
            "id": 298,
            "folio": "PED-20261020-000298"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.29,
          "minutos_acum": 14.5
        },
        {
          "orden": 4,
          "pedido": {
            "id": 301,
            "folio": "PED-20261020-000301"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.0,
          "minutos_acum": 18.5
        },
        {
          "orden": 5,
          "pedido": {
            "id": 303,
            "folio": "PED-20261020-000303"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.13,
          "minutos_acum": 22.9
        },
        {
          "orden": 6,
          "pedido": {
            "id": 304,
            "folio": "PED-20261020-000304"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.0,
          "minutos_acum": 26.9
        }
      ],
      "distancia_km": 1.05,
      "minutos": 26.9,
      "costo": 112.74
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 1,
    "paradas": 6,
    "distancia_km": 1.05,
    "minutos_maximo": 26.9,
    "costo": 112.74
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
X-Traza-Id: 8027c35d-bd45-4fd4-a03e-706b4de4078c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "pedido_ids": [
    298,
    299,
    301,
    302,
    303,
    304
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 123 ms · traza `8027c35d-bd45-4fd4-a03e-706b4de4078c`

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
      "distancia_km": 1.94,
      "minutos": 29.3,
      "costo": 116.75,
      "mejora_pct": 0.0
    },
    {
      "metodo": "Vecino más cercano",
      "distancia_km": 1.05,
      "minutos": 26.9,
      "costo": 112.74,
      "mejora_pct": 45.9
    },
    {
      "metodo": "Vecino más cercano + 2-opt",
      "distancia_km": 1.05,
      "minutos": 26.9,
      "costo": 112.74,
      "mejora_pct": 45.9
    },
    {
      "metodo": "TSP exacto",
      "distancia_km": 1.05,
      "minutos": 26.9,
      "costo": 112.74,
      "mejora_pct": 45.9
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
X-Traza-Id: 3988db76-c7fd-4ec8-b25a-e0bc4a23ad8b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "pedido_ids": [
    298,
    299,
    301,
    302,
    303,
    304
  ],
  "metodo": "exacto"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 172 ms · traza `3988db76-c7fd-4ec8-b25a-e0bc4a23ad8b`

```json
{
  "id": null,
  "estado": "calculo",
  "version": 1,
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "fecha": "2026-10-20",
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
            "id": 299,
            "folio": "PED-20261020-000299"
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
            "id": 302,
            "folio": "PED-20261020-000302"
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
            "id": 298,
            "folio": "PED-20261020-000298"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.29,
          "minutos_acum": 14.5
        },
        {
          "orden": 4,
          "pedido": {
            "id": 301,
            "folio": "PED-20261020-000301"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.0,
          "minutos_acum": 18.5
        },
        {
          "orden": 5,
          "pedido": {
            "id": 303,
            "folio": "PED-20261020-000303"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.13,
          "minutos_acum": 22.9
        },
        {
          "orden": 6,
          "pedido": {
            "id": 304,
            "folio": "PED-20261020-000304"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.0,
          "minutos_acum": 26.9
        }
      ],
      "distancia_km": 1.05,
      "minutos": 26.9,
      "costo": 112.74
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 1,
    "paradas": 6,
    "distancia_km": 1.05,
    "minutos_maximo": 26.9,
    "costo": 112.74
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
X-Traza-Id: f318ac22-f1b9-4029-b33c-8e9f5ef444a2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "pedido_ids": [
    298,
    299,
    301,
    302,
    303,
    304
  ],
  "guardar": true
}
```

**Respuesta.** HTTP 201 (esperado 201) · 202 ms · traza `f318ac22-f1b9-4029-b33c-8e9f5ef444a2`

```json
{
  "id": 51,
  "estado": "propuesto",
  "version": 1,
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "fecha": "2026-10-20",
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
            "id": 299,
            "folio": "PED-20261020-000299"
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
            "id": 302,
            "folio": "PED-20261020-000302"
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
            "id": 298,
            "folio": "PED-20261020-000298"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.29,
          "minutos_acum": 14.5
        },
        {
          "orden": 4,
          "pedido": {
            "id": 301,
            "folio": "PED-20261020-000301"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.0,
          "minutos_acum": 18.5
        },
        {
          "orden": 5,
          "pedido": {
            "id": 303,
            "folio": "PED-20261020-000303"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.13,
          "minutos_acum": 22.9
        },
        {
          "orden": 6,
          "pedido": {
            "id": 304,
            "folio": "PED-20261020-000304"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.0,
          "minutos_acum": 26.9
        }
      ],
      "distancia_km": 1.05,
      "minutos": 26.9,
      "costo": 112.74
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 1,
    "paradas": 6,
    "distancia_km": 1.05,
    "minutos_maximo": 26.9,
    "costo": 112.74
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
    "id": 51,
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

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes/51/ajustes`

```http
Accept: application/json
X-Traza-Id: 2a83ae7b-f7d9-4991-933d-375fa86e7a1d
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

**Respuesta.** HTTP 200 (esperado 200) · 79 ms · traza `2a83ae7b-f7d9-4991-933d-375fa86e7a1d`

```json
{
  "id": 51,
  "estado": "propuesto",
  "version": 2,
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "fecha": "2026-10-20",
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
            "id": 299,
            "folio": "PED-20261020-000299"
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
            "id": 302,
            "folio": "PED-20261020-000302"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.751679,
          "longitud": -100.366615,
          "tramo_km": 0.0,
          "minutos_acum": 34.7
        },
        {
          "orden": 3,
          "pedido": {
            "id": 298,
            "folio": "PED-20261020-000298"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.29,
          "minutos_acum": 39.5
        },
        {
          "orden": 4,
          "pedido": {
            "id": 301,
            "folio": "PED-20261020-000301"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.0,
          "minutos_acum": 43.5
        },
        {
          "orden": 5,
          "pedido": {
            "id": 303,
            "folio": "PED-20261020-000303"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.13,
          "minutos_acum": 47.9
        },
        {
          "orden": 6,
          "pedido": {
            "id": 304,
            "folio": "PED-20261020-000304"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.0,
          "minutos_acum": 51.9
        }
      ],
      "distancia_km": 1.05,
      "minutos": 51.9,
      "costo": 112.74
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 1,
    "paradas": 6,
    "distancia_km": 1.05,
    "minutos_maximo": 51.9,
    "costo": 112.74
  },
  "cambios": [
    "Retraso de 25 minutos en la ruta de Ramiro Alanís Lozano: 6 de 6 paradas quedan fuera de la promesa de 30 minutos."
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
    "PED-20261020-000299",
    "PED-20261020-000302",
    "PED-20261020-000298",
    "PED-20261020-000301",
    "PED-20261020-000303",
    "PED-20261020-000304"
  ]
}
```

### RUT-07 · Quitar un pedido · PASA

**Objetivo.** Recalcula la ruta afectada con el mismo método.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes/51/ajustes`

```http
Accept: application/json
X-Traza-Id: 350c6f51-b2e4-4697-adc6-d2db17135721
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "tipo": "quitar_pedido",
  "pedido_id": 299
}
```

**Respuesta.** HTTP 200 (esperado 200) · 81 ms · traza `350c6f51-b2e4-4697-adc6-d2db17135721`

```json
{
  "id": 51,
  "estado": "propuesto",
  "version": 3,
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "fecha": "2026-10-20",
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
            "id": 302,
            "folio": "PED-20261020-000302"
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
            "id": 298,
            "folio": "PED-20261020-000298"
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
            "id": 301,
            "folio": "PED-20261020-000301"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.0,
          "minutos_acum": 14.5
        },
        {
          "orden": 4,
          "pedido": {
            "id": 303,
            "folio": "PED-20261020-000303"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.13,
          "minutos_acum": 18.9
        },
        {
          "orden": 5,
          "pedido": {
            "id": 304,
            "folio": "PED-20261020-000304"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.0,
          "minutos_acum": 22.9
        }
      ],
      "distancia_km": 1.05,
      "minutos": 22.9,
      "costo": 94.74
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 1,
    "paradas": 5,
    "distancia_km": 1.05,
    "minutos_maximo": 22.9,
    "costo": 94.74
  },
  "cambios": [
    "Se quitó el pedido PED-20261020-000299; la ruta de Ramiro Alanís Lozano se recalculó con 5 paradas."
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

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes/51/ajustes`

```http
Accept: application/json
X-Traza-Id: 807c5c1e-35bc-4771-acc4-9ac95e9e9d33
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "tipo": "agregar_pedido",
  "pedido_id": 299
}
```

**Respuesta.** HTTP 200 (esperado 200) · 170 ms · traza `807c5c1e-35bc-4771-acc4-9ac95e9e9d33`

```json
{
  "id": 51,
  "estado": "propuesto",
  "version": 4,
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "fecha": "2026-10-20",
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
            "id": 302,
            "folio": "PED-20261020-000302"
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
            "id": 299,
            "folio": "PED-20261020-000299"
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
            "id": 298,
            "folio": "PED-20261020-000298"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.29,
          "minutos_acum": 14.5
        },
        {
          "orden": 4,
          "pedido": {
            "id": 301,
            "folio": "PED-20261020-000301"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.0,
          "minutos_acum": 18.5
        },
        {
          "orden": 5,
          "pedido": {
            "id": 303,
            "folio": "PED-20261020-000303"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.13,
          "minutos_acum": 22.9
        },
        {
          "orden": 6,
          "pedido": {
            "id": 304,
            "folio": "PED-20261020-000304"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.0,
          "minutos_acum": 26.9
        }
      ],
      "distancia_km": 1.05,
      "minutos": 26.9,
      "costo": 112.74
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 1,
    "paradas": 6,
    "distancia_km": 1.05,
    "minutos_maximo": 26.9,
    "costo": 112.74
  },
  "cambios": [
    "Se agregó el pedido PED-20261020-000299 a la ruta de Ramiro Alanís Lozano; ahora tiene 6 paradas."
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

**Petición.** `GET http://rutas:5118/api/v1/rutas/planes/51`

```http
Accept: application/json
X-Traza-Id: f62dd916-f395-4afc-bf14-603a731ebcfd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 26 ms · traza `f62dd916-f395-4afc-bf14-603a731ebcfd`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "f62dd916-f395-4afc-bf14-603a731ebcfd"
  }
}
```

### RUT-10 · Confirmar el plan · PASA

**Objetivo.** Comprueba que los pedidos sigan listos y deja las rutas en plan_ruta.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes/51/confirmar`

```http
Accept: application/json
X-Traza-Id: 699a655e-57e8-4bcd-b4ca-294974b440ce
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 163 ms · traza `699a655e-57e8-4bcd-b4ca-294974b440ce`

```json
{
  "id": 51,
  "estado": "confirmado",
  "version": 4,
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "fecha": "2026-10-20",
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
            "id": 302,
            "folio": "PED-20261020-000302"
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
            "id": 299,
            "folio": "PED-20261020-000299"
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
            "id": 298,
            "folio": "PED-20261020-000298"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.29,
          "minutos_acum": 14.5
        },
        {
          "orden": 4,
          "pedido": {
            "id": 301,
            "folio": "PED-20261020-000301"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.0,
          "minutos_acum": 18.5
        },
        {
          "orden": 5,
          "pedido": {
            "id": 303,
            "folio": "PED-20261020-000303"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.13,
          "minutos_acum": 22.9
        },
        {
          "orden": 6,
          "pedido": {
            "id": 304,
            "folio": "PED-20261020-000304"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.0,
          "minutos_acum": 26.9
        }
      ],
      "distancia_km": 1.05,
      "minutos": 26.9,
      "costo": 112.74
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 1,
    "paradas": 6,
    "distancia_km": 1.05,
    "minutos_maximo": 26.9,
    "costo": 112.74
  },
  "cambios": [
    "Se agregó el pedido PED-20261020-000299 a la ruta de Ramiro Alanís Lozano; ahora tiene 6 paradas."
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
    "id": 51,
    "repartidor_id": 7,
    "metodo": "TSP exacto",
    "paradas": 6,
    "distancia_km": "1.05",
    "minutos": "26.9",
    "costo_estimado": "112.74"
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

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes/51/confirmar`

```http
Accept: application/json
X-Traza-Id: 5b221b6d-ca1e-4237-b355-e3830a87b831
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 409 (esperado 409) · 22 ms · traza `5b221b6d-ca1e-4237-b355-e3830a87b831`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Solo se confirma un plan propuesto; este está confirmado.",
    "traza_id": "5b221b6d-ca1e-4237-b355-e3830a87b831"
  }
}
```

### RUT-12 · Planes guardados · PASA

**Objetivo.** Lista con estado, rutas, paradas, distancia y costo.

**Petición.** `GET http://rutas:5118/api/v1/rutas/planes?microhub_id=1`

```http
Accept: application/json
X-Traza-Id: 1a4d8f92-1578-49f7-8cba-168819df4f79
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 37 ms · traza `1a4d8f92-1578-49f7-8cba-168819df4f79`

```json
{
  "datos": [
    {
      "id": 51,
      "estado": "confirmado",
      "version": 4,
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "fecha": "2026-10-20",
      "rutas": 1,
      "paradas": 6,
      "distancia_km": 1.05,
      "costo": 112.74,
      "creado_por": 5,
      "creado_en": "2026-10-20T00:43:40-06:00"
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

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes/52/cancelar`

```http
Accept: application/json
X-Traza-Id: 242d171d-90df-4a9f-abda-c8a2abf9a5eb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 122 ms · traza `242d171d-90df-4a9f-abda-c8a2abf9a5eb`

```json
{
  "id": 52,
  "estado": "cancelado",
  "version": 1,
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "fecha": "2026-10-20",
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
            "id": 299,
            "folio": "PED-20261020-000299"
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
            "id": 302,
            "folio": "PED-20261020-000302"
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
            "id": 298,
            "folio": "PED-20261020-000298"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.29,
          "minutos_acum": 14.5
        },
        {
          "orden": 4,
          "pedido": {
            "id": 301,
            "folio": "PED-20261020-000301"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.753225,
          "longitud": -100.365213,
          "tramo_km": 0.0,
          "minutos_acum": 18.5
        },
        {
          "orden": 5,
          "pedido": {
            "id": 303,
            "folio": "PED-20261020-000303"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.13,
          "minutos_acum": 22.9
        },
        {
          "orden": 6,
          "pedido": {
            "id": 304,
            "folio": "PED-20261020-000304"
          },
          "zona": {
            "id": 2,
            "nombre": "Valles de San Bernabé"
          },
          "latitud": 25.752587,
          "longitud": -100.364483,
          "tramo_km": 0.0,
          "minutos_acum": 26.9
        }
      ],
      "distancia_km": 1.05,
      "minutos": 26.9,
      "costo": 112.74
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 1,
    "paradas": 6,
    "distancia_km": 1.05,
    "minutos_maximo": 26.9,
    "costo": 112.74
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
X-Traza-Id: 857d674c-8a1c-4c92-8263-9ca068921f49
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 3
}
```

**Respuesta.** HTTP 422 (esperado 422) · 486 ms · traza `857d674c-8a1c-4c92-8263-9ca068921f49`

```json
{
  "error": {
    "codigo": "VALIDACION",
    "mensaje": "No hay pedidos listos para despachar en ese microhub.",
    "traza_id": "857d674c-8a1c-4c92-8263-9ca068921f49"
  }
}
```

### RUT-15 · Pedidos que no están listos · PASA

**Objetivo.** Un pedido ajeno o no listo se rechaza.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/json
X-Traza-Id: 7f9e69df-ea7d-4f07-b7d4-685b350c12f2
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

**Respuesta.** HTTP 422 (esperado 422) · 415 ms · traza `7f9e69df-ea7d-4f07-b7d4-685b350c12f2`

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
    "traza_id": "7f9e69df-ea7d-4f07-b7d4-685b350c12f2"
  }
}
```

### RUT-16 · El operador planea otro microhub · PASA

**Objetivo.** No puede.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/json
X-Traza-Id: 83e86043-5321-4e57-9147-7082a751418b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "pedido_ids": [
    298,
    299,
    301,
    302,
    303,
    304
  ]
}
```

**Respuesta.** HTTP 403 (esperado 403) · 22 ms · traza `83e86043-5321-4e57-9147-7082a751418b`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil solo puede trabajar con su propio microhub.",
    "traza_id": "83e86043-5321-4e57-9147-7082a751418b"
  }
}
```

### RUT-17 · El auditor intenta planear · PASA

**Objetivo.** Consulta, no planea.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/json
X-Traza-Id: f0a0e6f5-1c90-4dc3-8697-2050daa92552
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1
}
```

**Respuesta.** HTTP 403 (esperado 403) · 77 ms · traza `f0a0e6f5-1c90-4dc3-8697-2050daa92552`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "f0a0e6f5-1c90-4dc3-8697-2050daa92552"
  }
}
```

### RUT-18 · Plan en XML con lista de pedidos · PASA

**Objetivo.** El cuerpo XML lleva la lista de pedidos y se valida contra rutas.xsd.

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/xml
X-Traza-Id: 42515a06-97b2-4cd2-bcf5-d790854c8070
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><ruta_plan_nuevo xmlns="urn:microhubs:v1"><microhub_id>1</microhub_id><pedido_ids><id>298</id><id>299</id><id>301</id></pedido_ids><metodo>exacto</metodo></ruta_plan_nuevo>
```

**Respuesta.** HTTP 200 (esperado 200) · 326 ms · traza `42515a06-97b2-4cd2-bcf5-d790854c8070`

```xml
<?xml version='1.0' encoding='utf-8'?>
<ruta_plan xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id xsi:nil="true" /><estado>calculo</estado><version>1</version><microhub><id>1</id><nombre>Microhub San Bernabé Centro</nombre></microhub><fecha>2026-10-20</fecha><metodo_pedido>exacto</metodo_pedido><rutas><ruta><repartidor><id>7</id><nombre>Ramiro Alanís Lozano</nombre></repartidor><metodo>TSP exacto</metodo><zonas><nombre_zona>Valles de San Bernabé</nombre_zona></zonas><paradas><parada><orden>1</orden><pedido><id>299</id><folio>PED-20261020-000299</folio></pedido><zona><id>2</id><nombre>Valles de San Bernabé</nombre></zona><latitud>25.751679</latitud><longitud>-100.366615</longitud><tramo_km>0.63</tramo_km><minutos_acum>5.7</minutos_acum></parada><parada><orden>2</orden><pedido><id>298</id><folio>PED-20261020-000298</folio></pedido><zona><id>2</id><nombre>Valles de San Bernabé</nombre></zona><latitud>25.753225</latitud><longitud>-100.365213</longitud><tramo_km>0.29</tramo_km><minutos_acum>10.5</minutos_acum></parada><parada><orden>3</orden><pedido><id>301</id><folio>PED-20261020-000301</folio></pedido><zona><id>2</id><nombre>Valles de San Bernabé</nombre></zona><latitud>25.753225</latitud><longitud>-100.365213</longitud><tramo_km>0</tramo_km><minutos_acum>14.5</minutos_acum></parada></paradas><distancia_km>0.92</distancia_km><minutos>14.5</minutos><costo>58.14</costo></ruta></rutas><sin_asignar /><total><rutas>1</rutas><paradas>3</paradas><distancia_km>0.92</distancia_km><minutos_maximo>14.5</minutos_maximo><costo>58.14</costo></total><cambios /><supuestos_usados><supuesto><clave>velocidad_reparto_kmh</clave><valor>22</valor><modificado>false</modificado></supuesto><supuesto><clave>tiempo_servicio_min</clave><valor>4</valor><modificado>false</modificado></supuesto><supuesto><clave>costo_km_reparto</clave><valor>4.5</valor><modificado>false</modificado></supuesto><supuesto><clave>costo_base_entrega</clave><valor>18</valor><modificado>false</modificado></supuesto><supuesto><clave>max_paradas_repartidor</clave><valor>8</valor><modificado>false</modificado></supuesto><supuesto><clave>factor_rodeo_distancia</clave><valor>1.3</valor><modificado>false</modificado></supuesto></supuestos_usados></ruta_plan>
```

### RUT-19 · Supuestos de las rutas · PASA

**Objetivo.** Velocidad, tiempo por parada, costo por km, tope de paradas y rodeo.

**Petición.** `GET http://rutas:5118/api/v1/rutas/supuestos`

```http
Accept: application/json
X-Traza-Id: 8de9be36-2284-46dd-a6c4-0b2b00d14bd3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 50 ms · traza `8de9be36-2284-46dd-a6c4-0b2b00d14bd3`

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
X-Traza-Id: 5ba1821a-02e0-4019-b4f5-7d1198d1788c
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

**Respuesta.** HTTP 202 (esperado 202) · 696 ms · traza `5ba1821a-02e0-4019-b4f5-7d1198d1788c`

```json
{
  "id": "21de5636-42b3-41c4-a0e8-989aed4f1be8",
  "nombre": "Simulación de Microhub San Bernabé Centro 2026-10-20",
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
    "pedidos_dia": 22.95,
    "ticket": 134.57,
    "margen_bruto": 0.28,
    "costos_fijos_mes": 69500.0,
    "costo_variable_pedido": 32.6,
    "dias_mes": 30.0,
    "operadores": 3,
    "repartidores": 3,
    "capacidad_fisica": 150,
    "horas": 10.0,
    "distancia_km": 2.4,
    "ausentismo": 0.05,
    "variacion_demanda": 0.1,
    "indice_semanal": [
      0.879,
      0.831,
      0.888,
      0.938,
      1.126,
      1.282,
      1.017
    ],
    "dia_inicio": 2,
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
  "creado_en": "2026-10-20T00:43:44-06:00",
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
    "id": "21de5636-42b3-41c4-a0e8-989aed4f1be8",
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

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones/21de5636-42b3-41c4-a0e8-989aed4f1be8`

```http
Accept: application/json
X-Traza-Id: 5d267ccd-f76e-440f-97e7-5231b145e351
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 25 ms · traza `5d267ccd-f76e-440f-97e7-5231b145e351`

```json
{
  "id": "21de5636-42b3-41c4-a0e8-989aed4f1be8",
  "nombre": "Simulación de Microhub San Bernabé Centro 2026-10-20",
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
    "pedidos_dia": 22.95,
    "ticket": 134.57,
    "margen_bruto": 0.28,
    "costos_fijos_mes": 69500.0,
    "costo_variable_pedido": 32.6,
    "dias_mes": 30.0,
    "operadores": 3,
    "repartidores": 3,
    "capacidad_fisica": 150,
    "horas": 10.0,
    "distancia_km": 2.4,
    "ausentismo": 0.05,
    "variacion_demanda": 0.1,
    "indice_semanal": [
      0.879,
      0.831,
      0.888,
      0.938,
      1.126,
      1.282,
      1.017
    ],
    "dia_inicio": 2,
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
        "media": -30802.8325,
        "p10": -30919.6125,
        "p50": -30807.8613,
        "p90": -30675.2838,
        "minimo": -31061.8413,
        "maximo": -30498.0057
      },
      {
        "clave": "********",
        "etiqueta": "Ingreso del periodo",
        "unidad": "MXN",
        "media": 43195.6243,
        "p10": 40101.86,
        "p50": 43062.4,
        "p90": 46574.677,
        "minimo": 36333.9,
        "maximo": 51271.17
      },
      {
        "clave": "********",
        "etiqueta": "Pedidos atendidos",
        "unidad": "pedidos",
        "media": 320.99,
        "p10": 298.0,
        "p50": 320.0,
        "p90": 346.1,
        "minimo": 270.0,
        "maximo": 381.0
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
        "media": 16.0008,
        "p10": 14.7111,
        "p50": 15.905,
        "p90": 17.4121,
        "minimo": 13.4278,
        "maximo": 19.742
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
      "utilidad_sin_variacion": -30801.2579,
      "utilidad_media": -30802.8325,
      "diferencia": -1.5746,
      "capacidad_dia_con_todo_el_personal": 150.0
    },
    "lectura": [
      "En 100 réplicas de 14 días, la utilidad media fue de -30,803 MXN (P10 -30,920, P90 -30,675).",
      "Hubo pérdida en 100.0 % de las réplicas y 0.0 % de los días estuvieron saturados.",
      "La capacidad alcanzó para casi toda la demanda.",
      "Con estos supuestos, lo más probable es perder dinero."
    ],
    "serie": [
      {
        "dia": 1,
        "demanda_media": 19.4,
        "atendidos_media": 19.4,
        "utilidad_acumulada_media": -2218.1224
      },
      {
        "dia": 2,
        "demanda_media": 20.36,
        "atendidos_media": 20.36,
        "utilidad_acumulada_media": -4431.3684
      },
      {
        "dia": 3,
        "demanda_media": 21.26,
        "atendidos_media": 21.26,
        "utilidad_acumulada_media": -6640.0428
      },
      {
        "dia": 4,
        "demanda_media": 25.47,
        "atendidos_media": 25.47,
        "utilidad_acumulada_media": -8827.3321
      },
      {
        "dia": 5,
        "demanda_media": 29.97,
        "atendidos_media": 29.97,
        "utilidad_acumulada_media": -10991.7631
      },
      {
        "dia": 6,
        "demanda_media": 24.62,
        "atendidos_media": 24.62,
        "utilidad_acumulada_media": -13183.37
      },
      {
        "dia": 7,
        "demanda_media": 19.89,
        "atendidos_media": 19.89,
        "utilidad_acumulada_media": -15399.0035
      },
      {
        "dia": 8,
        "demanda_media": 20.09,
        "atendidos_media": 20.09,
        "utilidad_acumulada_media": -17613.621
      },
      {
        "dia": 9,
        "demanda_media": 19.84,
        "atendidos_media": 19.84,
        "utilidad_acumulada_media": -19829.5084
      },
      {
        "dia": 10,
        "demanda_media": 21.51,
        "atendidos_media": 21.51,
        "utilidad_acumulada_media": -22036.9128
      },
      {
        "dia": 11,
        "demanda_media": 25.41,
        "atendidos_media": 25.41,
        "utilidad_acumulada_media": -24224.5069
      },
      {
        "dia": 12,
        "demanda_media": 28.74,
        "atendidos_media": 28.74,
        "utilidad_acumulada_media": -26395.1858
      },
      {
        "dia": 13,
        "demanda_media": 23.89,
        "atendidos_media": 23.89,
        "utilidad_acumulada_media": -28590.5008
      },
      {
        "dia": 14,
        "demanda_media": 20.54,
        "atendidos_media": 20.54,
        "utilidad_acumulada_media": -30802.8325
      }
    ]
  },
  "huella": "9abb61234c649a0afbdd0da56e5a7cbd08a8e26e859faa5e77f8ff637924f43a",
  "repeticion_de": null,
  "reproducible": null,
  "error": null,
  "creado_por": 5,
  "creado_en": "2026-10-20T00:43:44-06:00",
  "inicio_en": "2026-10-20T00:43:44-06:00",
  "fin_en": "2026-10-20T00:43:44-06:00",
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
    "huella": "9abb61234c649a0afbdd0da56e5a7cbd08a8e26e859faa5e77f8ff637924f43a",
    "inicio": true,
    "fin": true,
    "intentos": 1
  }
]
```

### SIM-03 · Repetir con la misma entrada y semilla · PASA

**Objetivo.** Debe dar exactamente lo mismo.

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones/21de5636-42b3-41c4-a0e8-989aed4f1be8/repetir`

```http
Accept: application/json
X-Traza-Id: 84d40b17-0071-4e2e-ac23-a002741f23d2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 202 (esperado 202) · 98 ms · traza `84d40b17-0071-4e2e-ac23-a002741f23d2`

```json
{
  "id": "789990ea-523d-4c9e-b6b0-f249e0bef626",
  "nombre": "Repetición de Simulación de Microhub San Bernabé Centro 2026-10-20",
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
    "pedidos_dia": 22.95,
    "ticket": 134.57,
    "margen_bruto": 0.28,
    "costos_fijos_mes": 69500.0,
    "costo_variable_pedido": 32.6,
    "dias_mes": 30.0,
    "operadores": 3,
    "repartidores": 3,
    "capacidad_fisica": 150,
    "horas": 10.0,
    "distancia_km": 2.4,
    "ausentismo": 0.05,
    "variacion_demanda": 0.1,
    "indice_semanal": [
      0.879,
      0.831,
      0.888,
      0.938,
      1.126,
      1.282,
      1.017
    ],
    "dia_inicio": 2,
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
  "repeticion_de": "21de5636-42b3-41c4-a0e8-989aed4f1be8",
  "reproducible": null,
  "error": null,
  "creado_por": 5,
  "creado_en": "2026-10-20T00:43:44-06:00",
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

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones/789990ea-523d-4c9e-b6b0-f249e0bef626`

```http
Accept: application/json
X-Traza-Id: 5b328957-8278-447d-9824-b8186856bc25
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 47 ms · traza `5b328957-8278-447d-9824-b8186856bc25`

```json
{
  "id": "789990ea-523d-4c9e-b6b0-f249e0bef626",
  "nombre": "Repetición de Simulación de Microhub San Bernabé Centro 2026-10-20",
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
    "pedidos_dia": 22.95,
    "ticket": 134.57,
    "margen_bruto": 0.28,
    "costos_fijos_mes": 69500.0,
    "costo_variable_pedido": 32.6,
    "dias_mes": 30.0,
    "operadores": 3,
    "repartidores": 3,
    "capacidad_fisica": 150,
    "horas": 10.0,
    "distancia_km": 2.4,
    "ausentismo": 0.05,
    "variacion_demanda": 0.1,
    "indice_semanal": [
      0.879,
      0.831,
      0.888,
      0.938,
      1.126,
      1.282,
      1.017
    ],
    "dia_inicio": 2,
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
        "media": -30802.8325,
        "p10": -30919.6125,
        "p50": -30807.8613,
        "p90": -30675.2838,
        "minimo": -31061.8413,
        "maximo": -30498.0057
      },
      {
        "clave": "********",
        "etiqueta": "Ingreso del periodo",
        "unidad": "MXN",
        "media": 43195.6243,
        "p10": 40101.86,
        "p50": 43062.4,
        "p90": 46574.677,
        "minimo": 36333.9,
        "maximo": 51271.17
      },
      {
        "clave": "********",
        "etiqueta": "Pedidos atendidos",
        "unidad": "pedidos",
        "media": 320.99,
        "p10": 298.0,
        "p50": 320.0,
        "p90": 346.1,
        "minimo": 270.0,
        "maximo": 381.0
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
        "media": 16.0008,
        "p10": 14.7111,
        "p50": 15.905,
        "p90": 17.4121,
        "minimo": 13.4278,
        "maximo": 19.742
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
      "utilidad_sin_variacion": -30801.2579,
      "utilidad_media": -30802.8325,
      "diferencia": -1.5746,
      "capacidad_dia_con_todo_el_personal": 150.0
    },
    "lectura": [
      "En 100 réplicas de 14 días, la utilidad media fue de -30,803 MXN (P10 -30,920, P90 -30,675).",
      "Hubo pérdida en 100.0 % de las réplicas y 0.0 % de los días estuvieron saturados.",
      "La capacidad alcanzó para casi toda la demanda.",
      "Con estos supuestos, lo más probable es perder dinero."
    ],
    "serie": [
      {
        "dia": 1,
        "demanda_media": 19.4,
        "atendidos_media": 19.4,
        "utilidad_acumulada_media": -2218.1224
      },
      {
        "dia": 2,
        "demanda_media": 20.36,
        "atendidos_media": 20.36,
        "utilidad_acumulada_media": -4431.3684
      },
      {
        "dia": 3,
        "demanda_media": 21.26,
        "atendidos_media": 21.26,
        "utilidad_acumulada_media": -6640.0428
      },
      {
        "dia": 4,
        "demanda_media": 25.47,
        "atendidos_media": 25.47,
        "utilidad_acumulada_media": -8827.3321
      },
      {
        "dia": 5,
        "demanda_media": 29.97,
        "atendidos_media": 29.97,
        "utilidad_acumulada_media": -10991.7631
      },
      {
        "dia": 6,
        "demanda_media": 24.62,
        "atendidos_media": 24.62,
        "utilidad_acumulada_media": -13183.37
      },
      {
        "dia": 7,
        "demanda_media": 19.89,
        "atendidos_media": 19.89,
        "utilidad_acumulada_media": -15399.0035
      },
      {
        "dia": 8,
        "demanda_media": 20.09,
        "atendidos_media": 20.09,
        "utilidad_acumulada_media": -17613.621
      },
      {
        "dia": 9,
        "demanda_media": 19.84,
        "atendidos_media": 19.84,
        "utilidad_acumulada_media": -19829.5084
      },
      {
        "dia": 10,
        "demanda_media": 21.51,
        "atendidos_media": 21.51,
        "utilidad_acumulada_media": -22036.9128
      },
      {
        "dia": 11,
        "demanda_media": 25.41,
        "atendidos_media": 25.41,
        "utilidad_acumulada_media": -24224.5069
      },
      {
        "dia": 12,
        "demanda_media": 28.74,
        "atendidos_media": 28.74,
        "utilidad_acumulada_media": -26395.1858
      },
      {
        "dia": 13,
        "demanda_media": 23.89,
        "atendidos_media": 23.89,
        "utilidad_acumulada_media": -28590.5008
      },
      {
        "dia": 14,
        "demanda_media": 20.54,
        "atendidos_media": 20.54,
        "utilidad_acumulada_media": -30802.8325
      }
    ]
  },
  "huella": "9abb61234c649a0afbdd0da56e5a7cbd08a8e26e859faa5e77f8ff637924f43a",
  "repeticion_de": "21de5636-42b3-41c4-a0e8-989aed4f1be8",
  "reproducible": true,
  "error": null,
  "creado_por": 5,
  "creado_en": "2026-10-20T00:43:44-06:00",
  "inicio_en": "2026-10-20T00:43:46-06:00",
  "fin_en": "2026-10-20T00:43:46-06:00",
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
    "id": "21de5636-42b3-41c4-a0e8-989aed4f1be8",
    "estado": "terminada",
    "huella": "9abb61234c649a0afbdd0da56e5a7cbd08a8e26e859faa5e77f8ff637924f43a",
    "repite_a": null
  },
  {
    "id": "789990ea-523d-4c9e-b6b0-f249e0bef626",
    "estado": "terminada",
    "huella": "9abb61234c649a0afbdd0da56e5a7cbd08a8e26e859faa5e77f8ff637924f43a",
    "repite_a": "21de5636-42b3-41c4-a0e8-989aed4f1be8"
  }
]
```

### SIM-05 · Otra semilla, otro resultado · PASA

**Objetivo.** Misma entrada con semilla 12: la huella cambia.

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones/a7f155af-3016-4e32-823b-7a7b01aae562`

```http
Accept: application/json
X-Traza-Id: 9a36b674-1402-40ba-8317-5e23d9c85ff7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 29 ms · traza `9a36b674-1402-40ba-8317-5e23d9c85ff7`

```json
{
  "id": "a7f155af-3016-4e32-823b-7a7b01aae562",
  "nombre": "Simulación de Microhub San Bernabé Centro 2026-10-20",
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
    "pedidos_dia": 22.95,
    "ticket": 134.57,
    "margen_bruto": 0.28,
    "costos_fijos_mes": 69500.0,
    "costo_variable_pedido": 32.6,
    "dias_mes": 30.0,
    "operadores": 3,
    "repartidores": 3,
    "capacidad_fisica": 150,
    "horas": 10.0,
    "distancia_km": 2.4,
    "ausentismo": 0.05,
    "variacion_demanda": 0.1,
    "indice_semanal": [
      0.879,
      0.831,
      0.888,
      0.938,
      1.126,
      1.282,
      1.017
    ],
    "dia_inicio": 2,
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
        "media": -30798.0069,
        "p10": -30925.2001,
        "p50": -30807.8613,
        "p90": -30654.4574,
        "minimo": -31092.3189,
        "maximo": -30538.6425
      },
      {
        "clave": "********",
        "etiqueta": "Ingreso del periodo",
        "unidad": "MXN",
        "media": 43323.4658,
        "p10": 39953.833,
        "p50": 43062.4,
        "p90": 47126.414,
        "minimo": 35526.48,
        "maximo": 50194.61
      },
      {
        "clave": "********",
        "etiqueta": "Pedidos atendidos",
        "unidad": "pedidos",
        "media": 321.94,
        "p10": 296.9,
        "p50": 320.0,
        "p90": 350.2,
        "minimo": 264.0,
        "maximo": 373.0
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
        "media": 16.1702,
        "p10": 14.7037,
        "p50": 16.2014,
        "p90": 17.5003,
        "minimo": 13.4845,
        "maximo": 18.5817
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
      "utilidad_sin_variacion": -30801.2579,
      "utilidad_media": -30798.0069,
      "diferencia": 3.251,
      "capacidad_dia_con_todo_el_personal": 150.0
    },
    "lectura": [
      "En 100 réplicas de 14 días, la utilidad media fue de -30,798 MXN (P10 -30,925, P90 -30,654).",
      "Hubo pérdida en 100.0 % de las réplicas y 0.0 % de los días estuvieron saturados.",
      "La capacidad alcanzó para casi toda la demanda.",
      "Con estos supuestos, lo más probable es perder dinero."
    ],
    "serie": [
      {
        "dia": 1,
        "demanda_media": 19.06,
        "atendidos_media": 19.06,
        "utilidad_acumulada_media": -2219.8495
      },
      {
        "dia": 2,
        "demanda_media": 21.27,
        "atendidos_media": 21.27,
        "utilidad_acumulada_media": -4428.4731
      },
      {
        "dia": 3,
        "demanda_media": 22.47,
        "atendidos_media": 22.47,
        "utilidad_acumulada_media": -6631.0011
      },
      {
        "dia": 4,
        "demanda_media": 26.13,
        "atendidos_media": 26.13,
        "utilidad_acumulada_media": -8814.9378
      },
      {
        "dia": 5,
        "demanda_media": 29.23,
        "atendidos_media": 29.23,
        "utilidad_acumulada_media": -10983.1278
      },
      {
        "dia": 6,
        "demanda_media": 23.15,
        "atendidos_media": 23.15,
        "utilidad_acumulada_media": -13182.2017
      },
      {
        "dia": 7,
        "demanda_media": 20.35,
        "atendidos_media": 20.35,
        "utilidad_acumulada_media": -15395.4985
      },
      {
        "dia": 8,
        "demanda_media": 18.82,
        "atendidos_media": 18.82,
        "utilidad_acumulada_media": -17616.5671
      },
      {
        "dia": 9,
        "demanda_media": 21.18,
        "atendidos_media": 21.18,
        "utilidad_acumulada_media": -19825.6479
      },
      {
        "dia": 10,
        "demanda_media": 21.35,
        "atendidos_media": 21.35,
        "utilidad_acumulada_media": -22033.8651
      },
      {
        "dia": 11,
        "demanda_media": 26.12,
        "atendidos_media": 26.12,
        "utilidad_acumulada_media": -24217.8526
      },
      {
        "dia": 12,
        "demanda_media": 29.54,
        "atendidos_media": 29.54,
        "utilidad_acumulada_media": -26384.4679
      },
      {
        "dia": 13,
        "demanda_media": 23.15,
        "atendidos_media": 23.15,
        "utilidad_acumulada_media": -28583.5418
      },
      {
        "dia": 14,
        "demanda_media": 20.12,
        "atendidos_media": 20.12,
        "utilidad_acumulada_media": -30798.0069
      }
    ]
  },
  "huella": "2f959677f051c0d62d991150583fdda02dc9bed677c12f2f0b017f6bebd988fd",
  "repeticion_de": null,
  "reproducible": null,
  "error": null,
  "creado_por": 5,
  "creado_en": "2026-10-20T00:43:47-06:00",
  "inicio_en": "2026-10-20T00:43:48-06:00",
  "fin_en": "2026-10-20T00:43:48-06:00",
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

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/comparacion?ids=21de5636-42b3-41c4-a0e8-989aed4f1be8,a7f155af-3016-4e32-823b-7a7b01aae562`

```http
Accept: application/json
X-Traza-Id: 050ce3ed-3ebe-46d6-b413-8a6c2a2940e8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 44 ms · traza `050ce3ed-3ebe-46d6-b413-8a6c2a2940e8`

```json
{
  "ejecuciones": [
    {
      "id": "21de5636-42b3-41c4-a0e8-989aed4f1be8",
      "nombre": "Simulación de Microhub San Bernabé Centro 2026-10-20",
      "objeto": {
        "tipo": "microhub",
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "dias": 14,
      "replicas": 100,
      "utilidad_media": -30802.8325,
      "utilidad_p10": -30919.6125,
      "utilidad_p90": -30675.2838,
      "prob_perdida_pct": 100.0,
      "atendidos_media": 320.99,
      "rechazados_media": 0.0,
      "dias_saturados_pct": 0.0,
      "huella": "9abb61234c649a0afbdd0da56e5a7cbd08a8e26e859faa5e77f8ff637924f43a"
    },
    {
      "id": "a7f155af-3016-4e32-823b-7a7b01aae562",
      "nombre": "Simulación de Microhub San Bernabé Centro 2026-10-20",
      "objeto": {
        "tipo": "microhub",
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "dias": 14,
      "replicas": 100,
      "utilidad_media": -30798.0069,
      "utilidad_p10": -30925.2001,
      "utilidad_p90": -30654.4574,
      "prob_perdida_pct": 100.0,
      "atendidos_media": 321.94,
      "rechazados_media": 0.0,
      "dias_saturados_pct": 0.0,
      "huella": "2f959677f051c0d62d991150583fdda02dc9bed677c12f2f0b017f6bebd988fd"
    }
  ],
  "mejor_id": "a7f155af-3016-4e32-823b-7a7b01aae562",
  "criterio": "Mayor utilidad media entre las que pierden dinero en menos de la mitad de las réplicas."
}
```

### SIM-07 · Escenario manual · PASA

**Objetivo.** Sin microhub ni candidato, con todos los datos escritos (el escenario A).

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones`

```http
Accept: application/json
X-Traza-Id: 8f6bc07b-0f7a-4294-86be-24d60b83b8ce
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

**Respuesta.** HTTP 202 (esperado 202) · 194 ms · traza `8f6bc07b-0f7a-4294-86be-24d60b83b8ce`

```json
{
  "id": "a79d8390-5f33-4a0c-ad04-25dc6b4fd583",
  "nombre": "Simulación de escenario manual 2026-10-20",
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
      0.879,
      0.831,
      0.888,
      0.938,
      1.126,
      1.282,
      1.017
    ],
    "dia_inicio": 2,
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
  "creado_en": "2026-10-20T00:43:48-06:00",
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

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones/a79d8390-5f33-4a0c-ad04-25dc6b4fd583`

```http
Accept: application/json
X-Traza-Id: 378b73e4-90c5-44fc-9953-f2724296ac8a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 31 ms · traza `378b73e4-90c5-44fc-9953-f2724296ac8a`

```json
{
  "id": "a79d8390-5f33-4a0c-ad04-25dc6b4fd583",
  "nombre": "Simulación de escenario manual 2026-10-20",
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
      0.879,
      0.831,
      0.888,
      0.938,
      1.126,
      1.282,
      1.017
    ],
    "dia_inicio": 2,
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
        "media": -24737.208,
        "p10": -24958.0,
        "p50": -24731.8,
        "p90": -24513.92,
        "minimo": -25124.4,
        "maximo": -24422.4
      },
      {
        "clave": "********",
        "etiqueta": "Ingreso del periodo",
        "unidad": "MXN",
        "media": 84707.1,
        "p10": 78975.0,
        "p50": 84847.5,
        "p90": 90504.0,
        "minimo": 74655.0,
        "maximo": 92880.0
      },
      {
        "clave": "********",
        "etiqueta": "Pedidos atendidos",
        "unidad": "pedidos",
        "media": 627.46,
        "p10": 585.0,
        "p50": 628.5,
        "p90": 670.4,
        "minimo": 553.0,
        "maximo": 688.0
      },
      {
        "clave": "********",
        "etiqueta": "Pedidos rechazados por falta de capacidad",
        "unidad": "pedidos",
        "media": 1.61,
        "p10": 0.0,
        "p50": 0.0,
        "p90": 0.0,
        "minimo": 0.0,
        "maximo": 54.0
      },
      {
        "clave": "********",
        "etiqueta": "Utilización de la capacidad",
        "unidad": "%",
        "media": 34.2607,
        "p10": 31.464,
        "p50": 34.2447,
        "p90": 36.9514,
        "minimo": 29.8038,
        "maximo": 39.5283
      },
      {
        "clave": "********",
        "etiqueta": "Días saturados",
        "unidad": "días",
        "media": 0.14,
        "p10": 0.0,
        "p50": 0.0,
        "p90": 1.0,
        "minimo": 0.0,
        "maximo": 1.0
      }
    ],
    "prob_perdida_pct": 100.0,
    "dias_saturados_pct": 1.0,
    "contraste": {
      "utilidad_sin_variacion": -24724.0,
      "utilidad_media": -24737.208,
      "diferencia": -13.208,
      "capacidad_dia_con_todo_el_personal": 143.5
    },
    "lectura": [
      "En 100 réplicas de 14 días, la utilidad media fue de -24,737 MXN (P10 -24,958, P90 -24,514).",
      "Hubo pérdida en 100.0 % de las réplicas y 1.0 % de los días estuvieron saturados.",
      "Faltó capacidad: se rechazaron en promedio 2 pedidos en el periodo.",
      "Con estos supuestos, lo más probable es perder dinero."
    ],
    "serie": [
      {
        "dia": 1,
        "demanda_media": 37.81,
        "atendidos_media": 37.81,
        "utilidad_acumulada_media": -1803.388
      },
      {
        "dia": 2,
        "demanda_media": 39.0,
        "atendidos_media": 39.0,
        "utilidad_acumulada_media": -3600.588
      },
      {
        "dia": 3,
        "demanda_media": 42.08,
        "atendidos_media": 41.63,
        "utilidad_acumulada_media": -5384.112
      },
      {
        "dia": 4,
        "demanda_media": 52.73,
        "atendidos_media": 52.73,
        "utilidad_acumulada_media": -7109.916
      },
      {
        "dia": 5,
        "demanda_media": 58.31,
        "atendidos_media": 58.09,
        "utilidad_acumulada_media": -8807.848
      },
      {
        "dia": 6,
        "demanda_media": 45.67,
        "atendidos_media": 45.67,
        "utilidad_acumulada_media": -10570.364
      },
      {
        "dia": 7,
        "demanda_media": 39.7,
        "atendidos_media": 39.7,
        "utilidad_acumulada_media": -12363.924
      },
      {
        "dia": 8,
        "demanda_media": 37.88,
        "atendidos_media": 37.51,
        "utilidad_acumulada_media": -14168.872
      },
      {
        "dia": 9,
        "demanda_media": 39.45,
        "atendidos_media": 39.45,
        "utilidad_acumulada_media": -15963.732
      },
      {
        "dia": 10,
        "demanda_media": 42.08,
        "atendidos_media": 42.08,
        "utilidad_acumulada_media": -17744.916
      },
      {
        "dia": 11,
        "demanda_media": 51.26,
        "atendidos_media": 51.26,
        "utilidad_acumulada_media": -19478.364
      },
      {
        "dia": 12,
        "demanda_media": 57.05,
        "atendidos_media": 57.03,
        "utilidad_acumulada_media": -21181.808
      },
      {
        "dia": 13,
        "demanda_media": 45.92,
        "atendidos_media": 45.38,
        "utilidad_acumulada_media": -22945.832
      },
      {
        "dia": 14,
        "demanda_media": 40.13,
        "atendidos_media": 40.12,
        "utilidad_acumulada_media": -24737.208
      }
    ]
  },
  "huella": "0dc01386cc4dbbffd4080692b4254d11eaff50dbae4c8fdff0fbc72e1bb712c2",
  "repeticion_de": null,
  "reproducible": null,
  "error": null,
  "creado_por": 5,
  "creado_en": "2026-10-20T00:43:48-06:00",
  "inicio_en": "2026-10-20T00:43:50-06:00",
  "fin_en": "2026-10-20T00:43:50-06:00",
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
X-Traza-Id: f1848c14-03fd-4674-a0c8-3a36bf727dd8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "pedidos_dia": 45
}
```

**Respuesta.** HTTP 422 (esperado 422) · 29 ms · traza `f1848c14-03fd-4674-a0c8-3a36bf727dd8`

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
    "traza_id": "f1848c14-03fd-4674-a0c8-3a36bf727dd8"
  }
}
```

### SIM-10 · Demasiado trabajo · PASA

**Objetivo.** Días × réplicas no puede pasar de 200,000.

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones`

```http
Accept: application/json
X-Traza-Id: 82a7482c-18e6-485f-9e22-9d51e1032004
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

**Respuesta.** HTTP 422 (esperado 422) · 511 ms · traza `82a7482c-18e6-485f-9e22-9d51e1032004`

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
    "traza_id": "82a7482c-18e6-485f-9e22-9d51e1032004"
  }
}
```

### SIM-11 · Cancelar una ejecución · PASA

**Objetivo.** Una ejecución en cola o en curso se puede cancelar.

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones/8fc2709d-2e86-4439-88f7-e22480ba5fc7/cancelar`

```http
Accept: application/json
X-Traza-Id: 2908aba9-9bfc-4987-8a87-fa5ae09f0335
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 88 ms · traza `2908aba9-9bfc-4987-8a87-fa5ae09f0335`

```json
{
  "id": "8fc2709d-2e86-4439-88f7-e22480ba5fc7",
  "nombre": "Simulación de Microhub San Bernabé Centro 2026-10-20",
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
    "pedidos_dia": 22.95,
    "ticket": 134.57,
    "margen_bruto": 0.28,
    "costos_fijos_mes": 69500.0,
    "costo_variable_pedido": 32.6,
    "dias_mes": 30.0,
    "operadores": 3,
    "repartidores": 3,
    "capacidad_fisica": 150,
    "horas": 10.0,
    "distancia_km": 2.4,
    "ausentismo": 0.05,
    "variacion_demanda": 0.1,
    "indice_semanal": [
      0.879,
      0.831,
      0.888,
      0.938,
      1.126,
      1.282,
      1.017
    ],
    "dia_inicio": 2,
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
  "creado_en": "2026-10-20T00:43:52-06:00",
  "inicio_en": null,
  "fin_en": "2026-10-20T00:43:52-06:00",
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
    "id": "8fc2709d-2e86-4439-88f7-e22480ba5fc7",
    "estado": "cancelada",
    "fin": true,
    "sin_resultados": true
  }
]
```

### SIM-12 · Cancelar una cancelada · PASA

**Objetivo.** Solo se cancela lo que está en cola o en curso.

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones/8fc2709d-2e86-4439-88f7-e22480ba5fc7/cancelar`

```http
Accept: application/json
X-Traza-Id: 98d19f8a-053d-43d7-afcb-855149640d4b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 409 (esperado 409) · 53 ms · traza `98d19f8a-053d-43d7-afcb-855149640d4b`

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "Solo se cancela una ejecución en cola o en curso; esta está cancelada.",
    "traza_id": "98d19f8a-053d-43d7-afcb-855149640d4b"
  }
}
```

### SIM-13 · Ejecuciones · PASA

**Objetivo.** Lista paginada, la más reciente primero.

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones?por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 3b231228-223d-482c-bbef-6c3e2dfb089c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 53 ms · traza `3b231228-223d-482c-bbef-6c3e2dfb089c`

```json
{
  "datos": [
    {
      "id": "8fc2709d-2e86-4439-88f7-e22480ba5fc7",
      "nombre": "Simulación de Microhub San Bernabé Centro 2026-10-20",
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
      "creado_en": "2026-10-20T00:43:52-06:00",
      "fin_en": "2026-10-20T00:43:52-06:00"
    },
    {
      "id": "a79d8390-5f33-4a0c-ad04-25dc6b4fd583",
      "nombre": "Simulación de escenario manual 2026-10-20",
      "estado": "terminada",
      "objeto": {
        "tipo": "manual",
        "id": null,
        "nombre": null
      },
      "semilla": 12,
      "dias": 14,
      "replicas": 100,
      "utilidad_media": -24737.208,
      "prob_perdida_pct": 100.0,
      "huella": "0dc01386cc4dbbffd4080692b4254d11eaff50dbae4c8fdff0fbc72e1bb712c2",
      "creado_en": "2026-10-20T00:43:48-06:00",
      "fin_en": "2026-10-20T00:43:50-06:00"
    },
    {
      "id": "a7f155af-3016-4e32-823b-7a7b01aae562",
      "nombre": "Simulación de Microhub San Bernabé Centro 2026-10-20",
      "estado": "terminada",
      "objeto": {
        "tipo": "microhub",
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "semilla": 12,
      "dias": 14,
      "replicas": 100,
      "utilidad_media": -30798.0069,
      "prob_perdida_pct": 100.0,
      "huella": "2f959677f051c0d62d991150583fdda02dc9bed677c12f2f0b017f6bebd988fd",
      "creado_en": "2026-10-20T00:43:47-06:00",
      "fin_en": "2026-10-20T00:43:48-06:00"
    },
    {
      "id": "789990ea-523d-4c9e-b6b0-f249e0bef626",
      "nombre": "Repetición de Simulación de Microhub San Bernabé Centro 2026-10-20",
      "estado": "terminada",
      "objeto": {
        "tipo": "microhub",
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "semilla": 11,
      "dias": 14,
      "replicas": 100,
      "utilidad_media": -30802.8325,
      "prob_perdida_pct": 100.0,
      "huella": "9abb61234c649a0afbdd0da56e5a7cbd08a8e26e859faa5e77f8ff637924f43a",
      "creado_en": "2026-10-20T00:43:44-06:00",
      "fin_en": "2026-10-20T00:43:46-06:00"
    },
    {
      "id": "21de5636-42b3-41c4-a0e8-989aed4f1be8",
      "nombre": "Simulación de Microhub San Bernabé Centro 2026-10-20",
      "estado": "terminada",
      "objeto": {
        "tipo": "microhub",
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "semilla": 11,
      "dias": 14,
      "replicas": 100,
      "utilidad_media": -30802.8325,
      "prob_perdida_pct": 100.0,
      "huella": "9abb61234c649a0afbdd0da56e5a7cbd08a8e26e859faa5e77f8ff637924f43a",
      "creado_en": "2026-10-20T00:43:44-06:00",
      "fin_en": "2026-10-20T00:43:44-06:00"
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
X-Traza-Id: 76409922-3959-4d38-8724-7735d94853fd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 403 (esperado 403) · 27 ms · traza `76409922-3959-4d38-8724-7735d94853fd`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "76409922-3959-4d38-8724-7735d94853fd"
  }
}
```

### SIM-15 · El operador simula · PASA

**Objetivo.** Sin simulacion.ejecutar.

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones`

```http
Accept: application/json
X-Traza-Id: 40dc5ccc-4515-441a-9ac7-0b8e80911923
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1
}
```

**Respuesta.** HTTP 403 (esperado 403) · 29 ms · traza `40dc5ccc-4515-441a-9ac7-0b8e80911923`

```json
{
  "error": {
    "codigo": "PROHIBIDO",
    "mensaje": "Tu perfil no tiene permiso para esta operación.",
    "traza_id": "40dc5ccc-4515-441a-9ac7-0b8e80911923"
  }
}
```

### SIM-16 · Poner en cola (XML) · PASA

**Objetivo.** Entrada y salida en XML, validadas contra simulacion.xsd.

**Petición.** `POST http://simulacion:5121/api/v1/simulacion/ejecuciones`

```http
Accept: application/xml
X-Traza-Id: b20ede04-cd5f-4c9f-8719-1428a912762a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><simulacion_nueva xmlns="urn:microhubs:v1"><microhub_id>1</microhub_id><dias>5</dias><replicas>20</replicas><semilla>3</semilla></simulacion_nueva>
```

**Respuesta.** HTTP 202 (esperado 202) · 604 ms · traza `b20ede04-cd5f-4c9f-8719-1428a912762a`

```xml
<?xml version='1.0' encoding='utf-8'?>
<simulacion_ejecucion xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>3d4558e4-d5a1-496b-a6a3-9efb81bf5b6b</id><nombre>Simulación de Microhub San Bernabé Centro 2026-10-20</nombre><estado>en_cola</estado><objeto><tipo>microhub</tipo><id>1</id><nombre>Microhub San Bernabé Centro</nombre></objeto><semilla>3</semilla><version_modelo>1.0</version_modelo><dias>5</dias><replicas>20</replicas><entrada><pedidos_dia>22.95</pedidos_dia><ticket>134.57</ticket><margen_bruto>0.28</margen_bruto><costos_fijos_mes>69500</costos_fijos_mes><costo_variable_pedido>32.6</costo_variable_pedido><dias_mes>30</dias_mes><operadores>3</operadores><repartidores>3</repartidores><capacidad_fisica>150</capacidad_fisica><horas>10</horas><distancia_km>2.4</distancia_km><ausentismo>0.05</ausentismo><variacion_demanda>0.1</variacion_demanda><indice_semanal><indice>0.879</indice><indice>0.831</indice><indice>0.888</indice><indice>0.938</indice><indice>1.126</indice><indice>1.282</indice><indice>1.017</indice></indice_semanal><dia_inicio>2</dia_inicio><origen_de_datos><dato><dato>costos_fijos</dato><fuente>costos</fuente></dato><dato><dato>costo_variable_pedido</dato><fuente>costos</fuente></dato><dato><dato>ticket</dato><fuente>demanda</fuente></dato><dato><dato>margen_bruto</dato><fuente>configuracion</fuente></dato><dato><dato>pedidos_dia</dato><fuente>demanda_repartida</fuente></dato><dato><dato>operadores</dato><fuente>capacidad</fuente></dato><dato><dato>repartidores</dato><fuente>capacidad</fuente></dato><dato><dato>capacidad_fisica</dato><fuente>capacidad</fuente></dato><dato><dato>horas</dato><fuente>configuracion</fuente></dato><dato><dato>distancia_km</dato><fuente>configuracion</fuente></dato><dato><dato>ausentismo</dato><fuente>configuracion</fuente></dato><dato><dato>variacion_demanda</dato><fuente>configuracion</fuente></dato><dato><dato>indice_semanal</dato><fuente>demanda</fuente></dato></origen_de_datos></entrada><resultados xsi:nil="true" /><huella xsi:nil="true" /><repeticion_de xsi:nil="true" /><reproducible xsi:nil="true" /><error xsi:nil="true" /><creado_por>5</creado_por><creado_en>2026-10-20T00:43:53-06:00</creado_en><inicio_en xsi:nil="true" /><fin_en xsi:nil="true" /><supuestos_usados><supuesto><clave>picking_pedidos_hora</clave><valor>10</valor><modificado>false</modificado></supuesto><supuesto><clave>packing_pedidos_hora</clave><valor>20</valor><modificado>false</modificado></supuesto><supuesto><clave>despacho_pedidos_hora</clave><valor>30</valor><modificado>false</modificado></supuesto><supuesto><clave>velocidad_reparto_kmh</clave><valor>22</valor><modificado>false</modificado></supuesto><supuesto><clave>tiempo_servicio_min</clave><valor>4</valor><modificado>false</modificado></supuesto><supuesto><clave>paradas_por_viaje</clave><valor>3</valor><modificado>false</modificado></supuesto><supuesto><clave>horas_turno</clave><valor>10</valor><modificado>false</modificado></supuesto><supuesto><clave>umbral_utilizacion_riesgo</clave><valor>85</valor><modificado>false</modificado></supuesto><supuesto><clave>sim_ausentismo</clave><valor>0.05</valor><modificado>false</modificado></supuesto><supuesto><clave>sim_variacion_demanda</clave><valor>0.1</valor><modificado>false</modificado></supuesto></supuestos_usados></simulacion_ejecucion>
```

### SIM-17 · Una ejecución inexistente · PASA

**Objetivo.** Un identificador que no existe.

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/ejecuciones/317f1bfe-ad9d-40dd-9156-c44299a35685`

```http
Accept: application/json
X-Traza-Id: 69c4db94-4725-4f6c-80b3-d1d551e3471f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 404 (esperado 404) · 24 ms · traza `69c4db94-4725-4f6c-80b3-d1d551e3471f`

```json
{
  "error": {
    "codigo": "NO_ENCONTRADO",
    "mensaje": "No existe esa ejecución.",
    "traza_id": "69c4db94-4725-4f6c-80b3-d1d551e3471f"
  }
}
```

### SIM-18 · Supuestos de la simulación · PASA

**Objetivo.** Réplicas, ausentismo, variación de la demanda y semilla.

**Petición.** `GET http://simulacion:5121/api/v1/simulacion/supuestos`

```http
Accept: application/json
X-Traza-Id: 0dc95180-044f-4bb8-8add-5d92b9c0e4d2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 33 ms · traza `0dc95180-044f-4bb8-8add-5d92b9c0e4d2`

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

## Servicio auth · puerto 5101

### SAL-AUT · Salud de auth · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://auth:5101/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 26eadaf9-aac6-48dd-b542-8505b323fc6e
```

**Respuesta.** HTTP 200 (esperado 200) · 19 ms · traza `26eadaf9-aac6-48dd-b542-8505b323fc6e`

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
X-Traza-Id: 5886efc6-f150-4825-bb17-3196cce37e8a
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `5886efc6-f150-4825-bb17-3196cce37e8a`

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
X-Traza-Id: ad338f30-7f00-493d-84f7-608f4c409f92
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `ad338f30-7f00-493d-84f7-608f4c409f92`

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
X-Traza-Id: a27c8b6e-4770-4848-97b9-d3e8ec78da51
```

**Respuesta.** HTTP 200 (esperado 200) · 15 ms · traza `a27c8b6e-4770-4848-97b9-d3e8ec78da51`

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
X-Traza-Id: e40ff157-cf59-46f8-8672-23fa1ef5d1c4
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `e40ff157-cf59-46f8-8672-23fa1ef5d1c4`

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
X-Traza-Id: c69bb8c4-45e6-4371-b89b-32f8b3bd0a85
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `c69bb8c4-45e6-4371-b89b-32f8b3bd0a85`

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
X-Traza-Id: 6dbcfa8b-f455-4595-a6e8-3f84525fe927
```

**Respuesta.** HTTP 200 (esperado 200) · 17 ms · traza `6dbcfa8b-f455-4595-a6e8-3f84525fe927`

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
X-Traza-Id: 4ac98874-3b49-45c7-b512-e2cea8d0cc17
```

**Respuesta.** HTTP 200 (esperado 200) · 15 ms · traza `4ac98874-3b49-45c7-b512-e2cea8d0cc17`

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
X-Traza-Id: 32023238-962c-4225-898d-b91b99d8bad8
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `32023238-962c-4225-898d-b91b99d8bad8`

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
X-Traza-Id: f3e38ccb-37e6-4b91-a02f-beb12b1348bd
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `f3e38ccb-37e6-4b91-a02f-beb12b1348bd`

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
X-Traza-Id: 855326f6-d860-4fc9-ba64-331645e853f5
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `855326f6-d860-4fc9-ba64-331645e853f5`

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
X-Traza-Id: 520d20a0-a61c-4fa7-93ab-7d80fa459858
```

**Respuesta.** HTTP 200 (esperado 200) · 15 ms · traza `520d20a0-a61c-4fa7-93ab-7d80fa459858`

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
X-Traza-Id: 09b4864b-d567-4d57-a3d4-1e8ef95ad7bd
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `09b4864b-d567-4d57-a3d4-1e8ef95ad7bd`

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
X-Traza-Id: 033d88e3-053e-4475-8684-21d7f4f56c47
```

**Respuesta.** HTTP 200 (esperado 200) · 15 ms · traza `033d88e3-053e-4475-8684-21d7f4f56c47`

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

## Servicio demanda · puerto 5115

### SAL-DEM · Salud de demanda · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://demanda:5115/api/v1/health`

```http
Accept: application/json
X-Traza-Id: ec66a437-add2-46d7-98c4-10f0b919258b
```

**Respuesta.** HTTP 200 (esperado 200) · 15 ms · traza `ec66a437-add2-46d7-98c4-10f0b919258b`

```json
{
  "servicio": "demanda",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica"
  }
}
```

## Servicio cobertura · puerto 5116

### SAL-COB · Salud de cobertura · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://cobertura:5116/api/v1/health`

```http
Accept: application/json
X-Traza-Id: f34efe10-abe1-40c9-a615-b96445c77846
```

**Respuesta.** HTTP 200 (esperado 200) · 15 ms · traza `f34efe10-abe1-40c9-a615-b96445c77846`

```json
{
  "servicio": "cobertura",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica"
  }
}
```

## Servicio capacidad · puerto 5117

### SAL-CAP · Salud de capacidad · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://capacidad:5117/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 16ac3ea3-d828-428d-9ff3-4ab97cf8af82
```

**Respuesta.** HTTP 200 (esperado 200) · 25 ms · traza `16ac3ea3-d828-428d-9ff3-4ab97cf8af82`

```json
{
  "servicio": "capacidad",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica"
  }
}
```

## Servicio rutas · puerto 5118

### SAL-RUT · Salud de rutas · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://rutas:5118/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 4a95c682-8b98-4fcb-ac81-8c3d67726c1e
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `4a95c682-8b98-4fcb-ac81-8c3d67726c1e`

```json
{
  "servicio": "rutas",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica"
  }
}
```

## Servicio costos · puerto 5119

### SAL-COS · Salud de costos · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://costos:5119/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 6e512fb1-7720-454c-a1c2-f69569ed2f38
```

**Respuesta.** HTTP 200 (esperado 200) · 15 ms · traza `6e512fb1-7720-454c-a1c2-f69569ed2f38`

```json
{
  "servicio": "costos",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica"
  }
}
```

## Servicio punto-equilibrio · puerto 5120

### SAL-PUN · Salud de punto-equilibrio · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://punto-equilibrio:5120/api/v1/health`

```http
Accept: application/json
X-Traza-Id: ac2d3c88-ffb7-4e9a-8974-cff0eb6bdd21
```

**Respuesta.** HTTP 200 (esperado 200) · 15 ms · traza `ac2d3c88-ffb7-4e9a-8974-cff0eb6bdd21`

```json
{
  "servicio": "punto-equilibrio",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica"
  }
}
```

## Servicio simulacion · puerto 5121

### SAL-SIM · Salud de simulacion · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://simulacion:5121/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 8c277ebf-14a7-491d-82af-3237ae12c8d9
```

**Respuesta.** HTTP 200 (esperado 200) · 15 ms · traza `8c277ebf-14a7-491d-82af-3237ae12c8d9`

```json
{
  "servicio": "simulacion",
  "version": "1.0.0",
  "estado": "ok",
  "dependencias": {
    "postgres": "ok",
    "redis": "ok",
    "mongo": "no_aplica"
  }
}
```

## Servicio surtido · puerto 5122

### SAL-SUR · Salud de surtido · PASA

**Objetivo.** Estado del servicio y de sus dependencias.

**Petición.** `GET http://surtido:5122/api/v1/health`

```http
Accept: application/json
X-Traza-Id: 47cb8e9c-fadc-42ba-9b28-723167906958
```

**Respuesta.** HTTP 200 (esperado 200) · 23 ms · traza `47cb8e9c-fadc-42ba-9b28-723167906958`

```json
{
  "servicio": "surtido",
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
X-Traza-Id: a3aa4b31-b0a8-4415-96d6-662ade61e8a3
```

**Respuesta.** HTTP 200 (esperado 200) · 16 ms · traza `a3aa4b31-b0a8-4415-96d6-662ade61e8a3`

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
X-Traza-Id: b872a74e-8255-4761-82ca-cfdaab1299d0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 5 ms · traza `b872a74e-8255-4761-82ca-cfdaab1299d0`

```json
{
  "valido": true,
  "expira_en": 850,
  "usuario": {
    "id": 1,
    "rol": "administrador",
    "microhub_id": null
  }
}
```

**Explicación.** El X-Traza-Id de la petición se recupera en logs_tecnicos.correlacion_id.

**Evidencia en MongoDB.** `db.logs_tecnicos.findOne({correlacion_id: 'b872a74e-8255-4761-82ca-cfdaab1299d0'})`

```json
{
  "nivel": "INFO",
  "componente": "auth",
  "registrado_en": "2026-10-20 06:43:55.131000+00:00",
  "correlacion_id": "b872a74e-8255-4761-82ca-cfdaab1299d0",
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
    "peticiones": 323,
    "ms_promedio": 119.12693498452012
  },
  {
    "_id": "auth",
    "peticiones": 782,
    "ms_promedio": 257.71099744245527
  },
  {
    "_id": "capacidad",
    "peticiones": 427,
    "ms_promedio": 64.37236533957845
  },
  {
    "_id": "cobertura",
    "peticiones": 661,
    "ms_promedio": 52.281391830559755
  },
  {
    "_id": "costos",
    "peticiones": 666,
    "ms_promedio": 45.069069069069066
  },
  {
    "_id": "demanda",
    "peticiones": 735,
    "ms_promedio": 102.52380952380952
  },
  {
    "_id": "documentos",
    "peticiones": 96,
    "ms_promedio": 17.020833333333332
  },
  {
    "_id": "entregas",
    "peticiones": 296,
    "ms_promedio": 62.2195945945946
  },
  {
    "_id": "inventario",
    "peticiones": 772,
    "ms_promedio": 53.55958549222798
  },
  {
    "_id": "microhubs",
    "peticiones": 129,
    "ms_promedio": 17.635658914728683
  },
  {
    "_id": "notificaciones",
    "peticiones": 162,
    "ms_promedio": 36.882716049382715
  },
  {
    "_id": "pedidos",
    "peticiones": 758,
    "ms_promedio": 77.03693931398416
  },
  {
    "_id": "planeacion",
    "peticiones": 293,
    "ms_promedio": 44.89078498293515
  },
  {
    "_id": "precios",
    "peticiones": 379,
    "ms_promedio": 49.189973614775724
  },
  {
    "_id": "productos",
    "peticiones": 94,
    "ms_promedio": 29.28723404255319
  },
  {
    "_id": "proveedores",
    "peticiones": 277,
    "ms_promedio": 48.15523465703971
  },
  {
    "_id": "punto-equilibrio",
    "peticiones": 472,
    "ms_promedio": 150.38983050847457
  },
  {
    "_id": "rutas",
    "peticiones": 484,
    "ms_promedio": 99.62603305785125
  },
  {
    "_id": "seguimiento",
    "peticiones": 34,
    "ms_promedio": 30.852941176470587
  },
  {
    "_id": "simulacion",
    "peticiones": 670,
    "ms_promedio": 145.40746268656716
  },
  {
    "_id": "surtido",
    "peticiones": 322,
    "ms_promedio": 190.36335403726707
  },
  {
    "_id": "usuarios",
    "peticiones": 58,
    "ms_promedio": 55.672413793103445
  },
  {
    "_id": "zonas",
    "peticiones": 1318,
    "ms_promedio": 1.8558421851289832
  }
]
```

## Servicio zonas · puerto 5108

### RAT-01 · Límite de consumo excedido · PASA

**Objetivo.** Más de 240 solicitudes por minuto desde la misma IP.

**Petición.** `GET http://zonas:5108/api/v1/zonas`

```http
Accept: application/json
X-Traza-Id: 98c1b1c6-e512-48a7-8b4d-693a4e05f3c0
```

**Respuesta.** HTTP 429 (esperado 429) · 4 ms · traza `98c1b1c6-e512-48a7-8b4d-693a4e05f3c0`

```json
{
  "error": {
    "codigo": "LIMITE_EXCEDIDO",
    "mensaje": "Máximo 240 solicitudes por minuto. Espera 3 segundos.",
    "traza_id": "98c1b1c6-e512-48a7-8b4d-693a4e05f3c0"
  }
}
```

**Explicación.** Contador rate:zonas:{ip}:{minuto} en Redis (db 1) con TTL de 120 s; responde Retry-After.

**Evidencia en Redis.** `db1 GET rate:zonas:44a242daeceec3ab:29874643; db1 TTL rate:zonas:44a242daeceec3ab:29874643`

```json
[
  {
    "comando": "db1 GET rate:zonas:44a242daeceec3ab:29874643",
    "valor": "242"
  },
  {
    "comando": "db1 TTL rate:zonas:44a242daeceec3ab:29874643",
    "valor": 71
  }
]
```
