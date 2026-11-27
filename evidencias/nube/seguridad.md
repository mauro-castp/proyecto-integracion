# Evidencia de seguridad

Cada control se ejercita contra los servicios en marcha.

Ejecutado el 2026-11-27 05:39 en la VM de Google Cloud: **23 de 23 comprobaciones pasan**.

## Autenticación

JWT firmado y sesión activa en Redis.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| — | Sin token no se entra (401 y WWW-Authenticate) | ✔ | `GET pedidos /pedidos` | 401 | 28 |
| — | Un token alterado se rechaza | ✔ | `GET pedidos /pedidos` | 401 | 46 |
| — | Un token revocado al salir ya no sirve en ningún servicio | ✔ | `GET zonas /zonas` | 401 | 73 |
| — | Cinco intentos fallidos bloquean la cuenta 15 minutos (423) | ✔ | `POST auth /auth/login` | 423 | 181 |

<details><summary>Respuestas y datos observados</summary>

**Sin token no se entra (401 y WWW-Authenticate)**

```
{"error": {"codigo": "TOKEN_INVALIDO", "mensaje": "Falta el encabezado Authorization: Bearer <token>.", "traza_id": "e9de748b-2e8f-4b57-ac33-998f089d9f97"}}
```

**Un token alterado se rechaza**

```
{"error": {"codigo": "TOKEN_INVALIDO", "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.", "traza_id": "6ff3dd20-5f38-4fdd-891e-f35b0b409195"}}
```

**Un token revocado al salir ya no sirve en ningún servicio**

```
{"error": {"codigo": "TOKEN_INVALIDO", "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.", "traza_id": "71c6ce8d-3534-4ae7-abb0-a15c9c2ec3ad"}}
```

**Cinco intentos fallidos bloquean la cuenta 15 minutos (423)**

```
{"error": {"codigo": "CUENTA_BLOQUEADA", "mensaje": "Cuenta bloqueada temporalmente. Intenta en 15 minutos.", "traza_id": "3eeb9e63-2586-4d5f-b0ea-264d5add0d3e"}}
```

</details>

## Autorización

Permisos por perfil, comprobados por cada servicio.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| — | El operador no puede ver la bitácora (403) | ✔ | `GET auditoria-monitoreo /auditoria` | 403 | 81 |
| — | El operador no puede crear un administrador (403) | ✔ | `POST usuarios /usuarios` | 403 | 109 |
| — | Los intentos denegados quedan en la bitácora | ✔ | — | — | — |
| — | La bitácora no se puede modificar, ni siquiera desde la base (RN31) | ✔ | — | — | — |
| — | Las contraseñas se guardan con bcrypt, nunca en claro | ✔ | — | — | — |

<details><summary>Respuestas y datos observados</summary>

**El operador no puede ver la bitácora (403)**

```
{"error": {"codigo": "PROHIBIDO", "mensaje": "Tu perfil no tiene permiso para esta operación.", "traza_id": "6b0f9267-4b59-4027-9cc0-7d2cd6199999"}}
```

**El operador no puede crear un administrador (403)**

```
{"error": {"codigo": "PROHIBIDO", "mensaje": "Tu perfil no tiene permiso para esta operación.", "traza_id": "707b58f6-4cd5-48c2-9b61-a5a115cf0927"}}
```

**Los intentos denegados quedan en la bitácora**

```
accesos denegados registrados en los últimos 2 minutos: 2
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
| — | XML con entidad externa (XXE) se rechaza | ✔ | `POST auth /auth/login` | 400 | 15 |
| — | JSON mal formado: 400 sin detalles internos | ✔ | `POST auth /auth/login` | 400 | 6 |
| — | Inyección SQL en la búsqueda: se trata como texto | ✔ | `GET productos /productos?q=%27%3B%20DROP%20TABLE%20producto%3B--` | 200 | 81 |
| — | Un archivo que dice ser imagen pero no lo es se rechaza (se revisa su firma) | ✔ | `POST documentos /documentos` | 422 | 9 |
| — | Un archivo de más de 5 MB se rechaza con el motivo | ✔ | `POST documentos /documentos` | 422 | 107 |
| — | Los errores usan el formato del contrato, con traza y sin rutas internas | ✔ | `GET zonas /zonas/no-existe` | 404 | 43 |

<details><summary>Respuestas y datos observados</summary>

**XML con entidad externa (XXE) se rechaza**

```
{"error": {"codigo": "XML_INVALIDO", "mensaje": "El cuerpo XML no está bien formado o contiene DTD/entidades.", "traza_id": "fa619818-deb2-4045-b280-533c28b2c4aa"}}
```

**JSON mal formado: 400 sin detalles internos**

```
{"error": {"codigo": "JSON_INVALIDO", "mensaje": "El cuerpo JSON no está bien formado.", "traza_id": "16809368-c3ff-47d2-9c96-95f099e82dad"}}
```

**Inyección SQL en la búsqueda: se trata como texto**

```
{"datos": [], "paginacion": {"pagina": 1, "por_pagina": 20, "total": 0, "paginas": 0}}
```

**Un archivo que dice ser imagen pero no lo es se rechaza (se revisa su firma)**

```
{"error": {"codigo": "VALIDACION", "mensaje": "Revisa los datos enviados.", "detalles": [{"campo": "tipo_mime", "mensaje": "El contenido no corresponde al tipo declarado."}], "traza_id": "9280b479-6c1d-4367-af88-9c602465fc47"}}
```

**Un archivo de más de 5 MB se rechaza con el motivo**

```
{"error": {"codigo": "VALIDACION", "mensaje": "Revisa los datos enviados.", "detalles": [{"campo": "contenido_base64", "mensaje": "El archivo debe pesar entre 1 byte y 5 MB."}], "traza_id": "abc77e31-4b5b-4a6a-9f80-e48ae7305d15"}}
```

**Los errores usan el formato del contrato, con traza y sin rutas internas**

```
{"error": {"codigo": "NO_ENCONTRADO", "mensaje": "No existe el recurso solicitado.", "traza_id": "1c9fd6b6-c8ec-42eb-a085-9e6b58e4f1e1"}}
```

</details>

## Archivos privados y cabeceras

Enlaces firmados con caducidad y cabeceras de protección.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| — | El archivo se entrega con un enlace firmado que caduca | ✔ | — | — | — |
| — | Otra persona no obtiene el enlace de un documento privado | ✔ | `GET documentos /documentos/6b09179d3da0be5c7ecec13f/enlace` | 404 | 9 |
| — | Un enlace alterado no sirve | ✔ | — | — | — |
| — | Respuestas con X-Content-Type-Options: nosniff y Cache-Control: no-store | ✔ | `GET zonas /zonas` | 200 | 48 |

<details><summary>Respuestas y datos observados</summary>

**El archivo se entrega con un enlace firmado que caduca**

```
https://storage.googleapis.com/microhubs-evidencias-637044/documentos/2026/11/6b09179d3da0be5c7ecec13f.jpg?…(firma omitida)
```

**Otra persona no obtiene el enlace de un documento privado**

```
{"error": {"codigo": "NO_ENCONTRADO", "mensaje": "No existe el recurso solicitado.", "traza_id": "89366930-f0d3-4b52-8ffb-54b278cd9fe9"}}
```

**Un enlace alterado no sirve**

```
HTTP 403
```

**Respuestas con X-Content-Type-Options: nosniff y Cache-Control: no-store**

```
{"datos": [{"id": 5, "clave": "EVF5B692", "nombre": "Zona F5B692 renombrada", "colonia": "Colonia F5B692", "codigo_postal": "64102", "latitud": 25.77, "longitud": -100.37}, {"id": 1, "clave": "ZN-SB01", "nombre": "San Bernabé Centro", "colonia": "San Bernabé",
```

</details>

## Límite de consumo

240 solicitudes por minuto por IP y servicio.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| — | Al pasar el límite responde 429 con Retry-After | ✔ | `GET zonas /zonas?por_pagina=1` | 429 | 3 |

<details><summary>Respuestas y datos observados</summary>

**Al pasar el límite responde 429 con Retry-After**

```
{"error": {"codigo": "LIMITE_EXCEDIDO", "mensaje": "Máximo 240 solicitudes por minuto. Espera 17 segundos.", "traza_id": "8d7de846-08e5-4f91-8ddb-ab7d356b3031"}}
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

