# Evidencia de seguridad

Cada control se ejercita contra los servicios en marcha.

Ejecutado el 2026-11-26 22:00 en la VM de Google Cloud: **23 de 23 comprobaciones pasan**.

## Autenticación

JWT firmado y sesión activa en Redis.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| — | Sin token no se entra (401 y WWW-Authenticate) | ✔ | `GET pedidos /pedidos` | 401 | 4 |
| — | Un token alterado se rechaza | ✔ | `GET pedidos /pedidos` | 401 | 3 |
| — | Un token revocado al salir ya no sirve en ningún servicio | ✔ | `GET zonas /zonas` | 401 | 4 |
| — | Cinco intentos fallidos bloquean la cuenta 15 minutos (423) | ✔ | `POST auth /auth/login` | 423 | 45 |

<details><summary>Respuestas y datos observados</summary>

**Sin token no se entra (401 y WWW-Authenticate)**

```
{"error": {"codigo": "TOKEN_INVALIDO", "mensaje": "Falta el encabezado Authorization: Bearer <token>.", "traza_id": "02340b43-9256-4167-9abf-1f6c9b0b8ca4"}}
```

**Un token alterado se rechaza**

```
{"error": {"codigo": "TOKEN_INVALIDO", "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.", "traza_id": "023bf2b0-3947-49b3-bd2c-1d188cf3d399"}}
```

**Un token revocado al salir ya no sirve en ningún servicio**

```
{"error": {"codigo": "TOKEN_INVALIDO", "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.", "traza_id": "35faed93-688c-4bd2-902b-049db9a25bf4"}}
```

**Cinco intentos fallidos bloquean la cuenta 15 minutos (423)**

```
{"error": {"codigo": "CUENTA_BLOQUEADA", "mensaje": "Cuenta bloqueada temporalmente. Intenta en 15 minutos.", "traza_id": "106449e8-2b5d-4b00-b0e0-47afc2bfd5e1"}}
```

</details>

## Autorización

Permisos por perfil, comprobados por cada servicio.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| — | El operador no puede ver la bitácora (403) | ✔ | `GET auditoria-monitoreo /auditoria` | 403 | 19 |
| — | El operador no puede crear un administrador (403) | ✔ | `POST usuarios /usuarios` | 403 | 19 |
| — | Los intentos denegados quedan en la bitácora | ✔ | — | — | — |
| — | La bitácora no se puede modificar, ni siquiera desde la base (RN31) | ✔ | — | — | — |
| — | Las contraseñas se guardan con bcrypt, nunca en claro | ✔ | — | — | — |

<details><summary>Respuestas y datos observados</summary>

**El operador no puede ver la bitácora (403)**

```
{"error": {"codigo": "PROHIBIDO", "mensaje": "Tu perfil no tiene permiso para esta operación.", "traza_id": "4aea5da7-43b8-4d71-a4a9-df85888defb3"}}
```

**El operador no puede crear un administrador (403)**

```
{"error": {"codigo": "PROHIBIDO", "mensaje": "Tu perfil no tiene permiso para esta operación.", "traza_id": "61a22cd9-4b86-4244-bd55-44aef4555865"}}
```

**Los intentos denegados quedan en la bitácora**

```
accesos denegados registrados en los últimos 2 minutos: 24
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
| — | JSON mal formado: 400 sin detalles internos | ✔ | `POST auth /auth/login` | 400 | 3 |
| — | Inyección SQL en la búsqueda: se trata como texto | ✔ | `GET productos /productos?q=%27%3B%20DROP%20TABLE%20producto%3B--` | 200 | 77 |
| — | Un archivo que dice ser imagen pero no lo es se rechaza (se revisa su firma) | ✔ | `POST documentos /documentos` | 422 | 7 |
| — | Un archivo de más de 5 MB se rechaza con el motivo | ✔ | `POST documentos /documentos` | 422 | 83 |
| — | Los errores usan el formato del contrato, con traza y sin rutas internas | ✔ | `GET zonas /zonas/no-existe` | 404 | 4 |

<details><summary>Respuestas y datos observados</summary>

**XML con entidad externa (XXE) se rechaza**

```
{"error": {"codigo": "XML_INVALIDO", "mensaje": "El cuerpo XML no está bien formado o contiene DTD/entidades.", "traza_id": "b562be83-2638-4985-885d-17b61f55dd81"}}
```

**JSON mal formado: 400 sin detalles internos**

```
{"error": {"codigo": "JSON_INVALIDO", "mensaje": "El cuerpo JSON no está bien formado.", "traza_id": "a1933093-7c7a-419b-a21e-86335e13ff34"}}
```

**Inyección SQL en la búsqueda: se trata como texto**

```
{"datos": [], "paginacion": {"pagina": 1, "por_pagina": 20, "total": 0, "paginas": 0}}
```

**Un archivo que dice ser imagen pero no lo es se rechaza (se revisa su firma)**

```
{"error": {"codigo": "VALIDACION", "mensaje": "Revisa los datos enviados.", "detalles": [{"campo": "tipo_mime", "mensaje": "El contenido no corresponde al tipo declarado."}], "traza_id": "b46602c0-c3d3-4743-94b3-11c0b3ea9a5f"}}
```

**Un archivo de más de 5 MB se rechaza con el motivo**

```
{"error": {"codigo": "VALIDACION", "mensaje": "Revisa los datos enviados.", "detalles": [{"campo": "contenido_base64", "mensaje": "El archivo debe pesar entre 1 byte y 5 MB."}], "traza_id": "49f4d356-7075-46b9-bc5d-46f9cac454cf"}}
```

**Los errores usan el formato del contrato, con traza y sin rutas internas**

```
{"error": {"codigo": "NO_ENCONTRADO", "mensaje": "No existe el recurso solicitado.", "traza_id": "c5739fa2-a605-47cf-9a39-56ebc9944ab7"}}
```

</details>

## Archivos privados y cabeceras

Enlaces firmados con caducidad y cabeceras de protección.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| — | El archivo se entrega con un enlace firmado que caduca | ✔ | — | — | — |
| — | Otra persona no obtiene el enlace de un documento privado | ✔ | `GET documentos /documentos/6b08ac0aaacade590e1e5e05/enlace` | 404 | 5 |
| — | Un enlace alterado no sirve | ✔ | — | — | — |
| — | Respuestas con X-Content-Type-Options: nosniff y Cache-Control: no-store | ✔ | `GET zonas /zonas` | 200 | 45 |

<details><summary>Respuestas y datos observados</summary>

**El archivo se entrega con un enlace firmado que caduca**

```
https://storage.googleapis.com/microhubs-evidencias-637044/documentos/2026/11/6b08ac0aaacade590e1e5e05.jpg?…(firma omitida)
```

**Otra persona no obtiene el enlace de un documento privado**

```
{"error": {"codigo": "NO_ENCONTRADO", "mensaje": "No existe el recurso solicitado.", "traza_id": "969dcb58-14d6-4a15-82c3-8dc5458c46a6"}}
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
| — | Al pasar el límite responde 429 con Retry-After | ✔ | `GET zonas /zonas?por_pagina=1` | 429 | 4 |

<details><summary>Respuestas y datos observados</summary>

**Al pasar el límite responde 429 con Retry-After**

```
{"error": {"codigo": "LIMITE_EXCEDIDO", "mensaje": "Máximo 240 solicitudes por minuto. Espera 16 segundos.", "traza_id": "49818346-257c-4ed7-96f0-3238dde17ba1"}}
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

