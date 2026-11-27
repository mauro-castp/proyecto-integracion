# Evidencia de seguridad

Cada control se ejercita contra los servicios en marcha.

Ejecutado el 2026-11-26 15:32 en el equipo local con Docker: **20 de 20 comprobaciones pasan**.

## Autenticación

JWT firmado y sesión activa en Redis.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| — | Sin token no se entra (401 y WWW-Authenticate) | ✔ | `GET pedidos /pedidos` | 401 | 345 |
| — | Un token alterado se rechaza | ✔ | `GET pedidos /pedidos` | 401 | 7 |
| — | Un token revocado al salir ya no sirve en ningún servicio | ✔ | `GET zonas /zonas` | 401 | 287 |
| — | Cinco intentos fallidos bloquean la cuenta 15 minutos (423) | ✔ | `POST auth /auth/login` | 423 | 74 |

<details><summary>Respuestas y datos observados</summary>

**Sin token no se entra (401 y WWW-Authenticate)**

```
{"error": {"codigo": "TOKEN_INVALIDO", "mensaje": "Falta el encabezado Authorization: Bearer <token>.", "traza_id": "84a7655d-d00c-4069-a4e5-0ccfb5913556"}}
```

**Un token alterado se rechaza**

```
{"error": {"codigo": "TOKEN_INVALIDO", "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.", "traza_id": "6ee15bcb-51a9-4568-b6b9-31082f75c9ba"}}
```

**Un token revocado al salir ya no sirve en ningún servicio**

```
{"error": {"codigo": "TOKEN_INVALIDO", "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.", "traza_id": "15d1ac89-d58c-4090-84ed-6b54cb741512"}}
```

**Cinco intentos fallidos bloquean la cuenta 15 minutos (423)**

```
{"error": {"codigo": "CUENTA_BLOQUEADA", "mensaje": "Cuenta bloqueada temporalmente. Intenta en 15 minutos.", "traza_id": "00154b6c-7a5f-4fbe-9cfc-2407b23738f9"}}
```

</details>

## Autorización

Permisos por perfil, comprobados por cada servicio.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| — | El operador no puede ver la bitácora (403) | ✔ | `GET auditoria-monitoreo /auditoria` | 403 | 59 |
| — | El operador no puede crear un administrador (403) | ✔ | `POST usuarios /usuarios` | 403 | 376 |
| — | Los intentos denegados quedan en la bitácora | ✔ | — | — | — |
| — | La bitácora no se puede modificar, ni siquiera desde la base (RN31) | ✔ | — | — | — |
| — | Las contraseñas se guardan con bcrypt, nunca en claro | ✔ | — | — | — |

<details><summary>Respuestas y datos observados</summary>

**El operador no puede ver la bitácora (403)**

```
{"error": {"codigo": "PROHIBIDO", "mensaje": "Tu perfil no tiene permiso para esta operación.", "traza_id": "7391fbc6-e177-4030-bcea-af4b4bbd56ba"}}
```

**El operador no puede crear un administrador (403)**

```
{"error": {"codigo": "PROHIBIDO", "mensaje": "Tu perfil no tiene permiso para esta operación.", "traza_id": "d386d3e5-8a3e-44f9-99b1-e952f3eda325"}}
```

**Los intentos denegados quedan en la bitácora**

```
accesos denegados registrados en los últimos 2 minutos: 2
```

**La bitácora no se puede modificar, ni siquiera desde la base (RN31)**

```
ERROR:  RN31: la bitÃ¡cora es de solo escritura. NingÃºn perfil, incluido el Administrador, puede update una entrada de auditorÃ­a.
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
| — | XML con entidad externa (XXE) se rechaza | ✔ | `POST auth /auth/login` | 400 | 22 |
| — | JSON mal formado: 400 sin detalles internos | ✔ | `POST auth /auth/login` | 400 | 6 |
| — | Inyección SQL en la búsqueda: se trata como texto | ✔ | `GET productos /productos?q=%27%3B%20DROP%20TABLE%20producto%3B--` | 200 | 462 |
| — | Un archivo que dice ser imagen pero no lo es se rechaza (se revisa su firma) | ✔ | `POST documentos /documentos` | 422 | 22 |
| — | Un archivo demasiado grande se rechaza | ✔ | `POST documentos /documentos` | 413 | 22 |
| — | Los errores usan el formato del contrato, con traza y sin rutas internas | ✔ | `GET zonas /zonas/no-existe` | 404 | 18 |

<details><summary>Respuestas y datos observados</summary>

**XML con entidad externa (XXE) se rechaza**

```
{"error": {"codigo": "XML_INVALIDO", "mensaje": "El cuerpo XML no está bien formado o contiene DTD/entidades.", "traza_id": "7138d174-6360-4088-9277-11d3dee9f0f3"}}
```

**JSON mal formado: 400 sin detalles internos**

```
{"error": {"codigo": "JSON_INVALIDO", "mensaje": "El cuerpo JSON no está bien formado.", "traza_id": "63a77fb6-e62b-4bb6-8f1f-262c4eff5e7d"}}
```

**Inyección SQL en la búsqueda: se trata como texto**

```
{"datos": [], "paginacion": {"pagina": 1, "por_pagina": 20, "total": 0, "paginas": 0}}
```

**Un archivo que dice ser imagen pero no lo es se rechaza (se revisa su firma)**

```
{"error": {"codigo": "VALIDACION", "mensaje": "Revisa los datos enviados.", "detalles": [{"campo": "tipo_mime", "mensaje": "El contenido no corresponde al tipo declarado."}], "traza_id": "422d7af6-9091-4887-85b0-258234c51c59"}}
```

**Un archivo demasiado grande se rechaza**

```
{"error": {"codigo": "CUERPO_DEMASIADO_GRANDE", "mensaje": "El cuerpo excede el tamaño máximo permitido (8 MB).", "traza_id": "3149bd3c-9d34-430e-886a-d43740c63166"}}
```

**Los errores usan el formato del contrato, con traza y sin rutas internas**

```
{"error": {"codigo": "NO_ENCONTRADO", "mensaje": "No existe el recurso solicitado.", "traza_id": "47090685-2332-4669-ac3c-0ef826245d8c"}}
```

</details>

## Archivos privados y cabeceras

Enlaces firmados con caducidad y cabeceras de protección.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| — | El archivo se entrega con un enlace firmado que caduca | ✔ | — | — | — |
| — | Otra persona no obtiene el enlace de un documento privado | ✔ | `GET documentos /documentos/6b08a58398a92a8091addc6b/enlace` | 404 | 10 |
| — | Un enlace alterado no sirve | ✔ | — | — | — |
| — | Respuestas con X-Content-Type-Options: nosniff y Cache-Control: no-store | ✔ | `GET zonas /zonas` | 200 | 22 |

<details><summary>Respuestas y datos observados</summary>

**El archivo se entrega con un enlace firmado que caduca**

```
http://127.0.0.1:5107/api/v1/documentos/descarga?…(firma omitida)
```

**Otra persona no obtiene el enlace de un documento privado**

```
{"error": {"codigo": "NO_ENCONTRADO", "mensaje": "No existe el recurso solicitado.", "traza_id": "f838dc72-7e3e-48d2-aabe-b8a74a816a91"}}
```

**Un enlace alterado no sirve**

```
HTTP 403
```

**Respuestas con X-Content-Type-Options: nosniff y Cache-Control: no-store**

```
{"datos": [{"id": 11, "clave": "EVD5F75A", "nombre": "Zona D5F75A renombrada", "colonia": "Colonia D5F75A", "codigo_postal": "64102", "latitud": 25.77, "longitud": -100.37}, {"id": 1, "clave": "ZN-SB01", "nombre": "San Bernabé Centro", "colonia": "San Bernabé"
```

</details>

## Límite de consumo

240 solicitudes por minuto por IP y servicio.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| — | Al pasar el límite responde 429 con Retry-After | ✔ | `GET zonas /zonas?por_pagina=1` | 429 | 6 |

<details><summary>Respuestas y datos observados</summary>

**Al pasar el límite responde 429 con Retry-After**

```
{"error": {"codigo": "LIMITE_EXCEDIDO", "mensaje": "Máximo 240 solicitudes por minuto. Espera 4 segundos.", "traza_id": "ed7a9183-5274-4078-bde6-cf7a925ddf90"}}
```

</details>

