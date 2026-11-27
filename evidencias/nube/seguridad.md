# Evidencia de seguridad

Cada control se ejercita contra los servicios en marcha.

Ejecutado el 2026-11-27 07:32 en la VM de Google Cloud: **23 de 23 comprobaciones pasan**.

## Autenticación

JWT firmado y sesión activa en Redis.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| — | Sin token no se entra (401 y WWW-Authenticate) | ✔ | `GET pedidos /pedidos` | 401 | 4 |
| — | Un token alterado se rechaza | ✔ | `GET pedidos /pedidos` | 401 | 5 |
| — | Un token revocado al salir ya no sirve en ningún servicio | ✔ | `GET zonas /zonas` | 401 | 4 |
| — | Cinco intentos fallidos bloquean la cuenta 15 minutos (423) | ✔ | `POST auth /auth/login` | 423 | 43 |

<details><summary>Respuestas y datos observados</summary>

**Sin token no se entra (401 y WWW-Authenticate)**

```
{"error": {"codigo": "TOKEN_INVALIDO", "mensaje": "Falta el encabezado Authorization: Bearer <token>.", "traza_id": "75094e57-0693-496d-8580-8b87836326be"}}
```

**Un token alterado se rechaza**

```
{"error": {"codigo": "TOKEN_INVALIDO", "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.", "traza_id": "837abb00-8e6c-4a7f-bece-f80da498d9da"}}
```

**Un token revocado al salir ya no sirve en ningún servicio**

```
{"error": {"codigo": "TOKEN_INVALIDO", "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.", "traza_id": "a13d607c-1b21-42ec-aa4b-15e6cf6ada85"}}
```

**Cinco intentos fallidos bloquean la cuenta 15 minutos (423)**

```
{"error": {"codigo": "CUENTA_BLOQUEADA", "mensaje": "Cuenta bloqueada temporalmente. Intenta en 15 minutos.", "traza_id": "c5567cb9-e8cc-4fc2-9cb9-f9fe64c37968"}}
```

</details>

## Autorización

Permisos por perfil, comprobados por cada servicio.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| — | El operador no puede ver la bitácora (403) | ✔ | `GET auditoria-monitoreo /auditoria` | 403 | 21 |
| — | El operador no puede crear un administrador (403) | ✔ | `POST usuarios /usuarios` | 403 | 24 |
| — | Los intentos denegados quedan en la bitácora | ✔ | — | — | — |
| — | La bitácora no se puede modificar, ni siquiera desde la base (RN31) | ✔ | — | — | — |
| — | Las contraseñas se guardan con bcrypt, nunca en claro | ✔ | — | — | — |

<details><summary>Respuestas y datos observados</summary>

**El operador no puede ver la bitácora (403)**

```
{"error": {"codigo": "PROHIBIDO", "mensaje": "Tu perfil no tiene permiso para esta operación.", "traza_id": "c9ac92d8-bed4-466f-87c8-756448b71975"}}
```

**El operador no puede crear un administrador (403)**

```
{"error": {"codigo": "PROHIBIDO", "mensaje": "Tu perfil no tiene permiso para esta operación.", "traza_id": "44d531a1-f37e-4cc9-8c2b-cc7f27ad8113"}}
```

**Los intentos denegados quedan en la bitácora**

```
accesos denegados registrados en los últimos 2 minutos: 36
```

**La bitácora no se puede modificar, ni siquiera desde la base (RN31)**

```
ERROR:  RN31: la bitácora es de solo escritura. Ningún perfil, incluido el Administrador, puede update una entrada de auditoría.
CONTEXT:  PL/pgSQL function fn_auditoria_inmutable() line 3 at RAISE
```

**Las contraseñas se guardan con bcrypt, nunca en claro**

```
inicio del hash: $2b$…
```

</details>

## Entradas maliciosas

Validación de JSON y XML, inyección y archivos.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| — | XML con entidad externa (XXE) se rechaza | ✔ | `POST auth /auth/login` | 400 | 4 |
| — | JSON mal formado: 400 sin detalles internos | ✔ | `POST auth /auth/login` | 400 | 4 |
| — | Inyección SQL en la búsqueda: se trata como texto | ✔ | `GET productos /productos?q=%27%3B%20DROP%20TABLE%20producto%3B--` | 200 | 43 |
| — | Un archivo que dice ser imagen pero no lo es se rechaza (se revisa su firma) | ✔ | `POST documentos /documentos` | 422 | 5 |
| — | Un archivo de más de 5 MB se rechaza con el motivo | ✔ | `POST documentos /documentos` | 422 | 93 |
| — | Los errores usan el formato del contrato, con traza y sin rutas internas | ✔ | `GET zonas /zonas/no-existe` | 404 | 5 |

<details><summary>Respuestas y datos observados</summary>

**XML con entidad externa (XXE) se rechaza**

```
{"error": {"codigo": "XML_INVALIDO", "mensaje": "El cuerpo XML no está bien formado o contiene DTD/entidades.", "traza_id": "1e02d275-2475-472b-80c9-d2ec0cbcfb85"}}
```

**JSON mal formado: 400 sin detalles internos**

```
{"error": {"codigo": "JSON_INVALIDO", "mensaje": "El cuerpo JSON no está bien formado.", "traza_id": "526d00f1-d1da-455d-a1c0-d9e492a1f55a"}}
```

**Inyección SQL en la búsqueda: se trata como texto**

```
{"datos": [], "paginacion": {"pagina": 1, "por_pagina": 20, "total": 0, "paginas": 0}}
```

**Un archivo que dice ser imagen pero no lo es se rechaza (se revisa su firma)**

```
{"error": {"codigo": "VALIDACION", "mensaje": "Revisa los datos enviados.", "detalles": [{"campo": "tipo_mime", "mensaje": "El contenido no corresponde al tipo declarado."}], "traza_id": "3e9c7ed8-fa61-4640-b5a2-d6007071a110"}}
```

**Un archivo de más de 5 MB se rechaza con el motivo**

```
{"error": {"codigo": "VALIDACION", "mensaje": "Revisa los datos enviados.", "detalles": [{"campo": "contenido_base64", "mensaje": "El archivo debe pesar entre 1 byte y 5 MB."}], "traza_id": "b10ca6c3-e603-4f86-98b1-221bbb86ad92"}}
```

**Los errores usan el formato del contrato, con traza y sin rutas internas**

```
{"error": {"codigo": "NO_ENCONTRADO", "mensaje": "No existe el recurso solicitado.", "traza_id": "0dc0539b-a2b7-448e-8367-59372d220a2b"}}
```

</details>

## Archivos privados y cabeceras

Enlaces firmados con caducidad y cabeceras de protección.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| — | El archivo se entrega con un enlace firmado que caduca | ✔ | — | — | — |
| — | Otra persona no obtiene el enlace de un documento privado | ✔ | `GET documentos /documentos/6b0931fcd92909927b4fc9b2/enlace` | 404 | 5 |
| — | Un enlace alterado no sirve | ✔ | — | — | — |
| — | Respuestas con X-Content-Type-Options: nosniff y Cache-Control: no-store | ✔ | `GET zonas /zonas` | 200 | 70 |

<details><summary>Respuestas y datos observados</summary>

**El archivo se entrega con un enlace firmado que caduca**

```
https://storage.googleapis.com/microhubs-evidencias-637044/documentos/2026/11/6b0931fcd92909927b4fc9b2.jpg?…(firma omitida)
```

**Otra persona no obtiene el enlace de un documento privado**

```
{"error": {"codigo": "NO_ENCONTRADO", "mensaje": "No existe el recurso solicitado.", "traza_id": "c9081cde-4dd6-43e0-a88e-f30c87ef5aac"}}
```

**Un enlace alterado no sirve**

```
HTTP 403
```

**Respuestas con X-Content-Type-Options: nosniff y Cache-Control: no-store**

```
{"datos": [{"id": 7, "clave": "EV45B7F5", "nombre": "Zona 45B7F5 renombrada", "colonia": "Colonia 45B7F5", "codigo_postal": "64102", "latitud": 25.77, "longitud": -100.37}, {"id": 6, "clave": "EV80FD0C", "nombre": "Zona 80FD0C renombrada", "colonia": "Colonia 
```

</details>

## Límite de consumo

240 solicitudes por minuto por IP y servicio.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| — | Al pasar el límite responde 429 con Retry-After | ✔ | `GET zonas /zonas?por_pagina=1` | 429 | 2 |

<details><summary>Respuestas y datos observados</summary>

**Al pasar el límite responde 429 con Retry-After**

```
{"error": {"codigo": "LIMITE_EXCEDIDO", "mensaje": "Máximo 240 solicitudes por minuto. Espera 46 segundos.", "traza_id": "564451eb-7a69-4cb0-9f5d-cf3192dad9ae"}}
```

</details>

## Infraestructura en la nube

Secretos y puertos de la VM.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| — | El archivo de secretos solo lo lee su dueño (600) | ✔ | — | — | — |
| — | No quedan los secretos por defecto del repositorio | ✔ | — | — | — |
| — | Ningún microservicio ni base de datos escucha hacia fuera | ✔ | — | — | — |

<details><summary>Respuestas y datos observados</summary>

**Ningún microservicio ni base de datos escucha hacia fuera**

```
*:20201, 0.0.0.0:20202, 0.0.0.0:22, 0.0.0.0:443, 0.0.0.0:80, [::]:22, [::]:443, [::]:80
```

</details>

