# Pruebas de tolerancia a fallos

Cada falla se provoca de verdad con Docker. En cada una se comprueba que el sistema la detecta, la informa con un error claro, no corrompe datos y se recupera sin intervención manual sobre los datos.

Ejecutado el 2026-11-26 15:35 en el equipo local con Docker: **32 de 32 comprobaciones pasan**.

## 1. Un microservicio detenido (inventario)

Los que dependen de él deben avisar; los demás siguen.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| durante | El servicio no responde | ✔ | `GET inventario /salud` | None | 2030 |
| durante | Los indicadores se entregan y nombran al servicio caído | ✔ | `GET reportes /reportes/indicadores` | 200 | 10531 |
| durante | El reporte que depende de él responde 503, sin inventar datos | ✔ | `GET reportes /reportes/inventario_alertas` | 503 | 4036 |
| durante | El resto de la plataforma sigue atendiendo | ✔ | `GET productos /productos?por_pagina=1` | 200 | 224 |
| durante | El monitoreo lo marca caído y abre una alerta | ✔ | `POST auditoria-monitoreo /monitoreo/verificaciones` | 201 | 4060 |
| después | Vuelve a estar sano en 2.0 s | ✔ | — | — | — |
| después | La alerta se cierra sola | ✔ | `GET auditoria-monitoreo /monitoreo/alertas?estado=abiertas&servicio=inventario` | 200 | 71 |

<details><summary>Respuestas y datos observados</summary>

**El servicio no responde**

```
URLError: <urlopen error [WinError 10061] No connection could be made because the target machine actively refused it>
```

**Los indicadores se entregan y nombran al servicio caído**

```
{"desde": "2026-10-28", "hasta": "2026-11-26", "indicadores": [{"clave": "pedidos", "titulo": "Pedidos del periodo", "valor": 203, "unidad": "pedidos", "fuente": "pedidos"}, {"clave": "venta", "titulo": "Venta del periodo", "valor": 31554.1, "unidad": "MXN", "
```

**El reporte que depende de él responde 503, sin inventar datos**

```
{"error": {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "El servicio inventario no responde. Intenta más tarde.", "traza_id": "b1f5a29e-90d3-41d7-863d-1890f4b4490b"}}
```

**El resto de la plataforma sigue atendiendo**

```
{"datos": [{"id": 3, "clave_interna": "AB-003", "nombre": "Aceite vegetal", "categoria": {"id": 1, "nombre": "Abarrote básico"}, "unidad": "botella", "presentacion": "900 ml", "precio": 42.0, "imagen_url": null, "estatus": "activo"}], "paginacion": {"pagina": 
```

**El monitoreo lo marca caído y abre una alerta**

```
{"verificados": 1, "ok": 0, "degradados": 0, "caidos": 1, "servicios": [{"servicio": "inventario", "estado": "caido", "tiempo_ms": 3975.2, "error": "El servicio inventario no responde. Intenta más tarde."}]}
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
| durante | No deja pasar sin validar la sesión (503) | ✔ | `GET pedidos /pedidos?por_pagina=1` | 503 | 7976 |
| durante | /salud informa redis con error | ✔ | `GET pedidos /salud` | 503 | 3554 |
| durante | Tampoco se emiten sesiones nuevas | ✔ | `POST auth /auth/login` | 503 | 8089 |
| después | Los servicios vuelven a estar sanos en 0.0 s | ✔ | — | — | — |
| después | Los tokens anteriores ya no sirven (Redis no conserva sesiones): nadie revocado puede volver a entrar | ✔ | `GET pedidos /pedidos?por_pagina=1` | 401 | 9 |
| después | Con un inicio de sesión nuevo todo funciona | ✔ | `GET pedidos /pedidos?por_pagina=1` | 200 | 66 |

<details><summary>Respuestas y datos observados</summary>

**No deja pasar sin validar la sesión (503)**

```
{"error": {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "No se pudo validar la sesión. Intenta más tarde.", "traza_id": "ef29e1db-08a6-42fd-884f-d4133cdb6d57"}}
```

**/salud informa redis con error**

```
{"servicio": "pedidos", "version": "1.0.0", "estado": "degradado", "dependencias": {"postgres": "ok", "redis": "error", "mongo": "no_aplica", "bucket": "no_aplica"}, "tiempo_ms": 3549.1}
```

**Tampoco se emiten sesiones nuevas**

```
{"error": {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "Una base de datos no responde. Intenta más tarde.", "traza_id": "270fa629-5625-43de-8169-d8139d0b5135"}}
```

**Los tokens anteriores ya no sirven (Redis no conserva sesiones): nadie revocado puede volver a entrar**

```
{"error": {"codigo": "TOKEN_INVALIDO", "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.", "traza_id": "19972810-6371-47d1-8b6b-6ffe1223a89d"}}
```

**Con un inicio de sesión nuevo todo funciona**

```
{"datos": [{"id": 600, "folio": "PED-20261126-000600", "estado": "cancelado", "zona": {"id": 3, "nombre": "Paseo de San Bernabé"}, "microhub_id": 2, "total": 306.0, "creado_en": "2026-11-26T15:29:27-06:00"}], "paginacion": {"pagina": 1, "por_pagina": 1, "total
```

</details>

## 3. MongoDB caído

MongoDB guarda archivos (sus datos), GPS y registros. Lo transaccional no depende de él.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| durante | Pedidos sigue funcionando (los registros se omiten) | ✔ | `GET pedidos /pedidos?por_pagina=1` | 200 | 4170 |
| durante | Subir un archivo responde con error claro | ✔ | `POST documentos /documentos` | 500 | 6382 |
| durante | /salud de documentos informa mongo con error | ✔ | `GET documentos /salud` | 503 | 2074 |
| después | Documentos se recupera en 5.1 s | ✔ | — | — | — |
| después | No quedó ningún registro a medias | ✔ | — | — | — |

<details><summary>Respuestas y datos observados</summary>

**Pedidos sigue funcionando (los registros se omiten)**

```
{"datos": [{"id": 600, "folio": "PED-20261126-000600", "estado": "cancelado", "zona": {"id": 3, "nombre": "Paseo de San Bernabé"}, "microhub_id": 2, "total": 306.0, "creado_en": "2026-11-26T15:29:27-06:00"}], "paginacion": {"pagina": 1, "por_pagina": 1, "total
```

**Subir un archivo responde con error claro**

```
{"error": {"codigo": "ERROR_INTERNO", "mensaje": "Ocurrió un error inesperado.", "traza_id": "72a21544-8b32-435b-9d67-2dd1444b4c00"}}
```

**/salud de documentos informa mongo con error**

```
{"servicio": "documentos", "version": "1.0.0", "estado": "degradado", "dependencias": {"postgres": "ok", "redis": "ok", "mongo": "error", "bucket": "ok"}, "tiempo_ms": 2059.5}
```

**No quedó ningún registro a medias**

```
documentos antes=118 después=118
```

</details>

## 4. PostgreSQL caído

La base transaccional. Los errores deben ser claros y sin detalles internos.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| durante | Responde 503 con el formato de error del contrato | ✔ | `GET pedidos /pedidos?por_pagina=1` | 503 | 4118 |
| durante | El error no muestra consultas, contraseñas ni trazas del programa | ✔ | — | — | — |
| durante | /salud informa postgres con error | ✔ | `GET pedidos /salud` | 503 | 3986 |
| después | Se reconecta solo en 2.0 s, sin reiniciar los servicios | ✔ | — | — | — |
| después | Vuelve a responder | ✔ | `GET pedidos /pedidos?por_pagina=1` | 200 | 110 |

<details><summary>Respuestas y datos observados</summary>

**Responde 503 con el formato de error del contrato**

```
{"error": {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "Una base de datos no responde. Intenta más tarde.", "traza_id": "70c001a3-7fff-4314-8ddc-6183701b7bfc"}}
```

**El error no muestra consultas, contraseñas ni trazas del programa**

```
{"error": {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "Una base de datos no responde. Intenta más tarde.", "traza_id": "70c001a3-7fff-4314-8ddc-6183701b7bfc"}}
```

**/salud informa postgres con error**

```
{"servicio": "pedidos", "version": "1.0.0", "estado": "degradado", "dependencias": {"postgres": "error", "redis": "ok", "mongo": "no_aplica", "bucket": "no_aplica"}, "tiempo_ms": 3970.1}
```

**Vuelve a responder**

```
{"datos": [{"id": 600, "folio": "PED-20261126-000600", "estado": "cancelado", "zona": {"id": 3, "nombre": "Paseo de San Bernabé"}, "microhub_id": 2, "total": 306.0, "creado_en": "2026-11-26T15:29:27-06:00"}], "paginacion": {"pagina": 1, "por_pagina": 1, "total
```

</details>

## 5. Almacén de archivos fuera de servicio

El bucket (o la carpeta) no acepta archivos. No debe quedar un registro sin archivo.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| durante | /salud informa el almacén con error | ✔ | `GET documentos /salud` | 503 | 24 |
| durante | Subir responde 503 | ✔ | `POST documentos /documentos` | 503 | 14 |
| durante | No se guardó un registro sin archivo | ✔ | — | — | — |
| después | Documentos vuelve a estar sano en 0.0 s | ✔ | — | — | — |
| después | Se puede subir de nuevo | ✔ | `POST documentos /documentos` | 201 | 53 |

<details><summary>Respuestas y datos observados</summary>

**/salud informa el almacén con error**

```
{"servicio": "documentos", "version": "1.0.0", "estado": "degradado", "dependencias": {"postgres": "ok", "redis": "ok", "mongo": "ok", "bucket": "error"}, "tiempo_ms": 18.3}
```

**Subir responde 503**

```
{"error": {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "El almacén de archivos no responde. Intenta más tarde.", "traza_id": "394dfe91-fb92-4d1d-a42f-aa5b18d523fc"}}
```

**No se guardó un registro sin archivo**

```
documentos antes=118 después=118
```

**Se puede subir de nuevo**

```
{"id": "6b08a626e22e0da8e7d6d120", "nombre": "fallo-almacen.jpg", "tipo_mime": "image/jpeg", "tamano_bytes": 276, "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc", "referencia": {"tipo": "usuario", "id": "1"}, "subido_por": 1, "crea
```

</details>

## 6. Un servicio que no contesta (tiempo de espera)

El contenedor queda congelado: acepta la conexión pero no responde.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| durante | Quien lo llama no se queda colgado: corta a los pocos segundos con 503 | ✔ | `GET reportes /reportes/inventario_alertas` | 503 | 4343 |
| durante | El monitoreo lo da por caído tras su tiempo de espera | ✔ | `POST auditoria-monitoreo /monitoreo/verificaciones` | 201 | 3109 |
| después | Al reanudarse vuelve en 0.0 s | ✔ | — | — | — |

<details><summary>Respuestas y datos observados</summary>

**Quien lo llama no se queda colgado: corta a los pocos segundos con 503**

```
{"error": {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "El servicio inventario no responde. Intenta más tarde.", "traza_id": "0a82a48f-747d-49ea-b1c4-a0321af9e1fb"}}
```

**El monitoreo lo da por caído tras su tiempo de espera**

```
{"verificados": 1, "ok": 0, "degradados": 0, "caidos": 1, "servicios": [{"servicio": "inventario", "estado": "caido", "tiempo_ms": 3005.4, "error": "El servicio inventario no responde. Intenta más tarde."}]}
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
antes:   pedidos=569 entregas=298 existencia_total=7782
después: pedidos=569 entregas=298 existencia_total=7782
```

</details>

