# Pruebas de tolerancia a fallos

Cada falla se provoca de verdad con Docker. En cada una se comprueba que el sistema la detecta, la informa con un error claro, no corrompe datos y se recupera sin intervención manual sobre los datos.

Ejecutado el 2026-11-27 07:34 en la VM de Google Cloud: **32 de 32 comprobaciones pasan**.

## 1. Un microservicio detenido (inventario)

Los que dependen de él deben avisar; los demás siguen.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| durante | El servicio no responde | ✔ | `GET inventario /salud` | None | 0 |
| durante | Los indicadores se entregan y nombran al servicio caído | ✔ | `GET reportes /reportes/indicadores` | 200 | 430 |
| durante | El reporte que depende de él responde 503, sin inventar datos | ✔ | `GET reportes /reportes/inventario_alertas` | 503 | 54 |
| durante | El resto de la plataforma sigue atendiendo | ✔ | `GET productos /productos?por_pagina=1` | 200 | 43 |
| durante | El monitoreo lo marca caído y abre una alerta | ✔ | `POST auditoria-monitoreo /monitoreo/verificaciones` | 201 | 57 |
| después | Vuelve a estar sano en 2.2 s | ✔ | — | — | — |
| después | La alerta se cierra sola | ✔ | `GET auditoria-monitoreo /monitoreo/alertas?estado=abiertas&servicio=inventario` | 200 | 33 |

<details><summary>Respuestas y datos observados</summary>

**El servicio no responde**

```
URLError: <urlopen error [Errno 111] Connection refused>
```

**Los indicadores se entregan y nombran al servicio caído**

```
{"desde": "2026-10-29", "hasta": "2026-11-27", "indicadores": [{"clave": "pedidos", "titulo": "Pedidos del periodo", "valor": 175, "unidad": "pedidos", "fuente": "pedidos"}, {"clave": "venta", "titulo": "Venta del periodo", "valor": 34222.1, "unidad": "MXN", "
```

**El reporte que depende de él responde 503, sin inventar datos**

```
{"error": {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "El servicio inventario no responde. Intenta más tarde.", "traza_id": "953a0e59-7c0e-461c-92f6-53a52733de46"}}
```

**El resto de la plataforma sigue atendiendo**

```
{"datos": [{"id": 3, "clave_interna": "AB-003", "nombre": "Aceite vegetal", "categoria": {"id": 1, "nombre": "Abarrote básico"}, "unidad": "botella", "presentacion": "900 ml", "precio": 42.0, "imagen_url": null, "estatus": "activo"}], "paginacion": {"pagina": 
```

**El monitoreo lo marca caído y abre una alerta**

```
{"verificados": 1, "ok": 0, "degradados": 0, "caidos": 1, "servicios": [{"servicio": "inventario", "estado": "caido", "tiempo_ms": 11.9, "error": "El servicio inventario no responde. Intenta más tarde."}]}
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
| durante | No deja pasar sin validar la sesión (503) | ✔ | `GET pedidos /pedidos?por_pagina=1` | 503 | 36 |
| durante | /salud informa redis con error | ✔ | `GET pedidos /salud` | 503 | 49 |
| durante | Tampoco se emiten sesiones nuevas | ✔ | `POST auth /auth/login` | 503 | 85 |
| después | Los servicios vuelven a estar sanos en 0.0 s | ✔ | — | — | — |
| después | Los tokens anteriores ya no sirven (Redis no conserva sesiones): nadie revocado puede volver a entrar | ✔ | `GET pedidos /pedidos?por_pagina=1` | 401 | 5 |
| después | Con un inicio de sesión nuevo todo funciona | ✔ | `GET pedidos /pedidos?por_pagina=1` | 200 | 33 |

<details><summary>Respuestas y datos observados</summary>

**No deja pasar sin validar la sesión (503)**

```
{"error": {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "No se pudo validar la sesión. Intenta más tarde.", "traza_id": "c3a5fa2c-a764-4fb2-b1ce-1dfa4aaa9461"}}
```

**/salud informa redis con error**

```
{"servicio": "pedidos", "version": "dba94ea", "estado": "degradado", "dependencias": {"postgres": "ok", "redis": "error", "mongo": "ok", "bucket": "ok"}, "tiempo_ms": 44.5}
```

**Tampoco se emiten sesiones nuevas**

```
{"error": {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "Una base de datos no responde. Intenta más tarde.", "traza_id": "45906b3e-fc38-4447-82e9-b0744aeeb474"}}
```

**Los tokens anteriores ya no sirven (Redis no conserva sesiones): nadie revocado puede volver a entrar**

```
{"error": {"codigo": "TOKEN_INVALIDO", "mensaje": "La sesión venció o fue cerrada. Inicia sesión de nuevo.", "traza_id": "1c355de2-bbf0-4880-80fd-46c0a55391c2"}}
```

**Con un inicio de sesión nuevo todo funciona**

```
{"datos": [{"id": 641, "folio": "PED-20261127-000641", "estado": "en_ruta", "zona": {"id": 2, "nombre": "Valles de San Bernabé"}, "microhub_id": 2, "total": 155.0, "creado_en": "2026-11-27T01:31:16-06:00"}], "paginacion": {"pagina": 1, "por_pagina": 1, "total"
```

</details>

## 3. MongoDB caído

MongoDB guarda archivos (sus datos), GPS y registros. Lo transaccional no depende de él.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| durante | Pedidos sigue funcionando (los registros se omiten) | ✔ | `GET pedidos /pedidos?por_pagina=1` | 200 | 2442 |
| durante | Subir un archivo responde con error claro | ✔ | `POST documentos /documentos` | 503 | 4548 |
| durante | /salud de documentos informa mongo con error | ✔ | `GET documentos /salud` | 503 | 2514 |
| después | Documentos se recupera en 0.4 s | ✔ | — | — | — |
| después | No quedó ningún registro a medias | ✔ | — | — | — |

<details><summary>Respuestas y datos observados</summary>

**Pedidos sigue funcionando (los registros se omiten)**

```
{"datos": [{"id": 641, "folio": "PED-20261127-000641", "estado": "en_ruta", "zona": {"id": 2, "nombre": "Valles de San Bernabé"}, "microhub_id": 2, "total": 155.0, "creado_en": "2026-11-27T01:31:16-06:00"}], "paginacion": {"pagina": 1, "por_pagina": 1, "total"
```

**Subir un archivo responde con error claro**

```
{"error": {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "MongoDB no responde. Intenta más tarde.", "traza_id": "a5415a0b-8c23-409c-b23a-762b4431846b"}}
```

**/salud de documentos informa mongo con error**

```
{"servicio": "documentos", "version": "dba94ea", "estado": "degradado", "dependencias": {"postgres": "ok", "redis": "ok", "mongo": "error", "bucket": "ok"}, "tiempo_ms": 2512.7}
```

**No quedó ningún registro a medias**

```
documentos antes=64 después=64
```

</details>

## 4. PostgreSQL caído

La base transaccional. Los errores deben ser claros y sin detalles internos.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| durante | Responde 503 con el formato de error del contrato | ✔ | `GET pedidos /pedidos?por_pagina=1` | 503 | 486 |
| durante | El error no muestra consultas, contraseñas ni trazas del programa | ✔ | — | — | — |
| durante | /salud informa postgres con error | ✔ | `GET pedidos /salud` | 503 | 11 |
| después | Se reconecta solo en 2.0 s, sin reiniciar los servicios | ✔ | — | — | — |
| después | Vuelve a responder | ✔ | `GET pedidos /pedidos?por_pagina=1` | 200 | 39 |

<details><summary>Respuestas y datos observados</summary>

**Responde 503 con el formato de error del contrato**

```
{"error": {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "Una base de datos no responde. Intenta más tarde.", "traza_id": "0969ad4c-10fe-4da2-b408-5bab50c27089"}}
```

**El error no muestra consultas, contraseñas ni trazas del programa**

```
{"error": {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "Una base de datos no responde. Intenta más tarde.", "traza_id": "0969ad4c-10fe-4da2-b408-5bab50c27089"}}
```

**/salud informa postgres con error**

```
{"servicio": "pedidos", "version": "dba94ea", "estado": "degradado", "dependencias": {"postgres": "error", "redis": "ok", "mongo": "ok", "bucket": "ok"}, "tiempo_ms": 9.7}
```

**Vuelve a responder**

```
{"datos": [{"id": 641, "folio": "PED-20261127-000641", "estado": "en_ruta", "zona": {"id": 2, "nombre": "Valles de San Bernabé"}, "microhub_id": 2, "total": 155.0, "creado_en": "2026-11-27T01:31:16-06:00"}], "paginacion": {"pagina": 1, "por_pagina": 1, "total"
```

</details>

## 5. Almacén de archivos fuera de servicio

El bucket (o la carpeta) no acepta archivos. No debe quedar un registro sin archivo.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| durante | /salud informa el almacén con error | ✔ | `GET documentos /salud` | 503 | 90 |
| durante | Subir responde 503 | ✔ | `POST documentos /documentos` | 503 | 264 |
| durante | No se guardó un registro sin archivo | ✔ | — | — | — |
| después | Documentos vuelve a estar sano en 2.2 s | ✔ | — | — | — |
| después | Se puede subir de nuevo | ✔ | `POST documentos /documentos` | 201 | 92 |

<details><summary>Respuestas y datos observados</summary>

**/salud informa el almacén con error**

```
{"servicio": "documentos", "version": "dba94ea", "estado": "degradado", "dependencias": {"postgres": "ok", "redis": "ok", "mongo": "ok", "bucket": "error"}, "tiempo_ms": 88.4}
```

**Subir responde 503**

```
{"error": {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "El almacén de archivos no responde. Intenta más tarde.", "traza_id": "30428287-6787-4b86-94e2-ea1c62d9240c"}}
```

**No se guardó un registro sin archivo**

```
documentos antes=64 después=64
```

**Se puede subir de nuevo**

```
{"id": "6b0932698906de78e8c97834", "nombre": "fallo-almacen.jpg", "tipo_mime": "image/jpeg", "tamano_bytes": 276, "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc", "referencia": {"tipo": "usuario", "id": "1"}, "subido_por": 1, "crea
```

</details>

## 6. Un servicio que no contesta (tiempo de espera)

El contenedor queda congelado: acepta la conexión pero no responde.

| Momento | Comprobación | Resultado | Petición | HTTP | ms |
|---|---|---|---|---|---|
| durante | Quien lo llama no se queda colgado: corta a los pocos segundos con 503 | ✔ | `GET reportes /reportes/inventario_alertas` | 503 | 4039 |
| durante | El monitoreo lo da por caído tras su tiempo de espera | ✔ | `POST auditoria-monitoreo /monitoreo/verificaciones` | 201 | 3060 |
| después | Al reanudarse vuelve en 0.2 s | ✔ | — | — | — |

<details><summary>Respuestas y datos observados</summary>

**Quien lo llama no se queda colgado: corta a los pocos segundos con 503**

```
{"error": {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "El servicio inventario no responde. Intenta más tarde.", "traza_id": "2345569a-0b17-49d1-a00a-599a5715a43f"}}
```

**El monitoreo lo da por caído tras su tiempo de espera**

```
{"verificados": 1, "ok": 0, "degradados": 0, "caidos": 1, "servicios": [{"servicio": "inventario", "estado": "caido", "tiempo_ms": 3004.1, "error": "El servicio inventario no responde. Intenta más tarde."}]}
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
antes:   pedidos=637 entregas=180 existencia_total=7452
después: pedidos=637 entregas=180 existencia_total=7452
```

</details>

