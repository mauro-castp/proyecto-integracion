# Pruebas de tolerancia a fallos

Cada falla se provoca de verdad con Docker. En cada una se comprueba que el sistema la detecta, la informa con un error claro, no corrompe datos y se recupera sin intervención manual sobre los datos.

Ejecutado el 2026-11-27 05:41 en la VM de Google Cloud: **32 de 32 comprobaciones pasan**.

## 1. Un microservicio detenido (inventario)

Los que dependen de él deben avisar; los demás siguen.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| durante | El servicio no responde | ✔ | `GET inventario /salud` | None | 0 |
| durante | Los indicadores se entregan y nombran al servicio caído | ✔ | `GET reportes /reportes/indicadores` | 200 | 656 |
| durante | El reporte que depende de él responde 503, sin inventar datos | ✔ | `GET reportes /reportes/inventario_alertas` | 503 | 57 |
| durante | El resto de la plataforma sigue atendiendo | ✔ | `GET productos /productos?por_pagina=1` | 200 | 54 |
| durante | El monitoreo lo marca caído y abre una alerta | ✔ | `POST auditoria-monitoreo /monitoreo/verificaciones` | 201 | 70 |
| después | Vuelve a estar sano en 2.0 s | ✔ | — | — | — |
| después | La alerta se cierra sola | ✔ | `GET auditoria-monitoreo /monitoreo/alertas?estado=abiertas&servicio=inventario` | 200 | 43 |

<details><summary>Respuestas y datos observados</summary>

**El servicio no responde**

```
URLError: <urlopen error [Errno 111] Connection refused>
```

**Los indicadores se entregan y nombran al servicio caído**

```
{"desde": "2026-10-28", "hasta": "2026-11-26", "indicadores": [{"clave": "pedidos", "titulo": "Pedidos del periodo", "valor": 161, "unidad": "pedidos", "fuente": "pedidos"}, {"clave": "venta", "titulo": "Venta del periodo", "valor": 30625.3, "unidad": "MXN", "
```

**El reporte que depende de él responde 503, sin inventar datos**

```
{"error": {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "El servicio inventario no responde. Intenta más tarde.", "traza_id": "9e56936c-f779-4176-b80b-d9516b45eb44"}}
```

**El resto de la plataforma sigue atendiendo**

```
{"datos": [{"id": 3, "clave_interna": "AB-003", "nombre": "Aceite vegetal", "categoria": {"id": 1, "nombre": "Abarrote básico"}, "unidad": "botella", "presentacion": "900 ml", "precio": 42.0, "imagen_url": null, "estatus": "activo"}], "paginacion": {"pagina": 
```

**El monitoreo lo marca caído y abre una alerta**

```
{"verificados": 1, "ok": 0, "degradados": 0, "caidos": 1, "servicios": [{"servicio": "inventario", "estado": "caido", "tiempo_ms": 10.7, "error": "El servicio inventario no responde. Intenta más tarde."}]}
```

**La alerta se cierra sola**

```
{"datos": [], "paginacion": {"pagina": 1, "por_pagina": 20, "total": 0, "paginas": 0}}
```

</details>

## 2. Redis caído

Redis guarda las sesiones. Sin él no se puede saber si un token fue revocado: el sistema cierra el paso (503) en lugar de confiar.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| durante | No deja pasar sin validar la sesión (503) | ✔ | `GET pedidos /pedidos?por_pagina=1` | 503 | 30 |
| durante | /salud informa redis con error | ✔ | `GET pedidos /salud` | 503 | 24 |
| durante | Tampoco se emiten sesiones nuevas | ✔ | `POST auth /auth/login` | 503 | 53 |
| después | Los servicios vuelven a estar sanos en 0.0 s | ✔ | — | — | — |
| después | Los tokens anteriores ya no sirven (Redis no conserva sesiones): nadie revocado puede volver a entrar | ✔ | `GET pedidos /pedidos?por_pagina=1` | 401 | 5 |
| después | Con un inicio de sesión nuevo todo funciona | ✔ | `GET pedidos /pedidos?por_pagina=1` | 200 | 43 |

<details><summary>Respuestas y datos observados</summary>

**No deja pasar sin validar la sesión (503)**

```
{"error": {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "No se pudo validar la sesión. Intenta más tarde.", "traza_id": "d9e87e19-df03-49eb-8163-1174af6bf411"}}
```

**/salud informa redis con error**

```
{"servicio": "pedidos", "version": "fd85013", "estado": "degradado", "dependencias": {"postgres": "ok", "redis": "error", "mongo": "no_aplica", "bucket": "no_aplica"}, "tiempo_ms": 22.1}
```

**Tampoco se emiten sesiones nuevas**

```
{"error": {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "Una base de datos no responde. Intenta más tarde.", "traza_id": "503ce2fd-7f81-47d0-b279-fa0930d787d7"}}
```

**Los tokens anteriores ya no sirven (Redis no conserva sesiones): nadie revocado puede volver a entrar**

```
{"error": {"codigo": "TOKEN_INVALIDO", "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.", "traza_id": "7b7e7031-15f7-45f3-9f16-3d1d886a24c9"}}
```

**Con un inicio de sesión nuevo todo funciona**

```
{"datos": [{"id": 597, "folio": "PED-20261126-000597", "estado": "cancelado", "zona": {"id": 3, "nombre": "Paseo de San Bernabé"}, "microhub_id": 2, "total": 288.0, "creado_en": "2026-11-26T23:38:27-06:00"}], "paginacion": {"pagina": 1, "por_pagina": 1, "total
```

</details>

## 3. MongoDB caído

MongoDB guarda archivos (sus datos), GPS y registros. Lo transaccional no depende de él.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| durante | Pedidos sigue funcionando (los registros se omiten) | ✔ | `GET pedidos /pedidos?por_pagina=1` | 200 | 2434 |
| durante | Subir un archivo responde con error claro | ✔ | `POST documentos /documentos` | 503 | 4553 |
| durante | /salud de documentos informa mongo con error | ✔ | `GET documentos /salud` | 503 | 2061 |
| después | Documentos se recupera en 0.5 s | ✔ | — | — | — |
| después | No quedó ningún registro a medias | ✔ | — | — | — |

<details><summary>Respuestas y datos observados</summary>

**Pedidos sigue funcionando (los registros se omiten)**

```
{"datos": [{"id": 597, "folio": "PED-20261126-000597", "estado": "cancelado", "zona": {"id": 3, "nombre": "Paseo de San Bernabé"}, "microhub_id": 2, "total": 288.0, "creado_en": "2026-11-26T23:38:27-06:00"}], "paginacion": {"pagina": 1, "por_pagina": 1, "total
```

**Subir un archivo responde con error claro**

```
{"error": {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "MongoDB no responde. Intenta más tarde.", "traza_id": "1aa766d6-2d98-4b3b-9240-5b50bc78d4a0"}}
```

**/salud de documentos informa mongo con error**

```
{"servicio": "documentos", "version": "fd85013", "estado": "degradado", "dependencias": {"postgres": "ok", "redis": "ok", "mongo": "error", "bucket": "ok"}, "tiempo_ms": 2059.4}
```

**No quedó ningún registro a medias**

```
documentos antes=35 después=35
```

</details>

## 4. PostgreSQL caído

La base transaccional. Los errores deben ser claros y sin detalles internos.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| durante | Responde 503 con el formato de error del contrato | ✔ | `GET pedidos /pedidos?por_pagina=1` | 503 | 17 |
| durante | El error no muestra consultas, contraseñas ni trazas del programa | ✔ | — | — | — |
| durante | /salud informa postgres con error | ✔ | `GET pedidos /salud` | 503 | 13 |
| después | Se reconecta solo en 2.0 s, sin reiniciar los servicios | ✔ | — | — | — |
| después | Vuelve a responder | ✔ | `GET pedidos /pedidos?por_pagina=1` | 200 | 50 |

<details><summary>Respuestas y datos observados</summary>

**Responde 503 con el formato de error del contrato**

```
{"error": {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "Una base de datos no responde. Intenta más tarde.", "traza_id": "15c7b786-2649-4a51-bcee-77bb8ca5eb2f"}}
```

**El error no muestra consultas, contraseñas ni trazas del programa**

```
{"error": {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "Una base de datos no responde. Intenta más tarde.", "traza_id": "15c7b786-2649-4a51-bcee-77bb8ca5eb2f"}}
```

**/salud informa postgres con error**

```
{"servicio": "pedidos", "version": "fd85013", "estado": "degradado", "dependencias": {"postgres": "error", "redis": "ok", "mongo": "no_aplica", "bucket": "no_aplica"}, "tiempo_ms": 11.6}
```

**Vuelve a responder**

```
{"datos": [{"id": 597, "folio": "PED-20261126-000597", "estado": "cancelado", "zona": {"id": 3, "nombre": "Paseo de San Bernabé"}, "microhub_id": 2, "total": 288.0, "creado_en": "2026-11-26T23:38:27-06:00"}], "paginacion": {"pagina": 1, "por_pagina": 1, "total
```

</details>

## 5. Almacén de archivos fuera de servicio

El bucket (o la carpeta) no acepta archivos. No debe quedar un registro sin archivo.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| durante | /salud informa el almacén con error | ✔ | `GET documentos /salud` | 503 | 519 |
| durante | Subir responde 503 | ✔ | `POST documentos /documentos` | 503 | 282 |
| durante | No se guardó un registro sin archivo | ✔ | — | — | — |
| después | Documentos vuelve a estar sano en 2.3 s | ✔ | — | — | — |
| después | Se puede subir de nuevo | ✔ | `POST documentos /documentos` | 201 | 102 |

<details><summary>Respuestas y datos observados</summary>

**/salud informa el almacén con error**

```
{"servicio": "documentos", "version": "fd85013", "estado": "degradado", "dependencias": {"postgres": "ok", "redis": "ok", "mongo": "ok", "bucket": "error"}, "tiempo_ms": 515.9}
```

**Subir responde 503**

```
{"error": {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "El almacén de archivos no responde. Intenta más tarde.", "traza_id": "74ed2845-edca-4e3c-96f3-722888c00890"}}
```

**No se guardó un registro sin archivo**

```
documentos antes=35 después=35
```

**Se puede subir de nuevo**

```
{"id": "6b09180a8bc191fc4ce98c66", "nombre": "fallo-almacen.jpg", "tipo_mime": "image/jpeg", "tamano_bytes": 276, "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc", "referencia": {"tipo": "usuario", "id": "1"}, "subido_por": 1, "crea
```

</details>

## 6. Un servicio que no contesta (tiempo de espera)

El contenedor queda congelado: acepta la conexión pero no responde.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| durante | Quien lo llama no se queda colgado: corta a los pocos segundos con 503 | ✔ | `GET reportes /reportes/inventario_alertas` | 503 | 4046 |
| durante | El monitoreo lo da por caído tras su tiempo de espera | ✔ | `POST auditoria-monitoreo /monitoreo/verificaciones` | 201 | 3065 |
| después | Al reanudarse vuelve en 0.0 s | ✔ | — | — | — |

<details><summary>Respuestas y datos observados</summary>

**Quien lo llama no se queda colgado: corta a los pocos segundos con 503**

```
{"error": {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "El servicio inventario no responde. Intenta más tarde.", "traza_id": "c23662c4-5a2f-4b13-9685-489053471481"}}
```

**El monitoreo lo da por caído tras su tiempo de espera**

```
{"verificados": 1, "ok": 0, "degradados": 0, "caidos": 1, "servicios": [{"servicio": "inventario", "estado": "caido", "tiempo_ms": 3004.0, "error": "El servicio inventario no responde. Intenta más tarde."}]}
```

</details>

## 7. Integridad de los datos

Pedidos, entregas e inventario antes y después de todas las fallas.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| final | Ninguna falla creó, borró ni alteró datos | ✔ | — | — | — |

<details><summary>Respuestas y datos observados</summary>

**Ninguna falla creó, borró ni alteró datos**

```
antes:   pedidos=593 entregas=157 existencia_total=7245
después: pedidos=593 entregas=157 existencia_total=7245
```

</details>

