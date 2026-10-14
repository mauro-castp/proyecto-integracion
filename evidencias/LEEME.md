# Evidencias de petición y respuesta (anexo E1)

Ejecución completa de `servicios/pruebas/evidencias.py` contra los diez microservicios desplegados con
`docker-compose.integrado.yml`, sobre una base creada desde cero: **93 de 93 casos pasan** (13 de octubre de 2026,
21:27 en la hora UTC del contenedor).

| Archivo | Contenido |
|---|---|
| `evidencias.md` | De cada caso: URL y método, encabezados (el token se recorta y las claves se ocultan), cuerpo JSON o XML, respuesta completa, código HTTP, tiempo, `X-Traza-Id`, explicación y lo que quedó en PostgreSQL, MongoDB o Redis |
| `evidencias.html` | El mismo contenido listo para capturas de pantalla |
| `pruebas.md` | Tabla de casos con resultado esperado contra obtenido |
| `evidencias.json` | Datos crudos |

Se generan con (el script cambia datos: úsese en la base de demostración):

```bash
docker compose -f docker-compose.integrado.yml exec entregas python pruebas/evidencias.py
docker compose -f docker-compose.integrado.yml cp entregas:/tmp/evidencias ./evidencias
```

Cada ejecución crea sus propios datos, por eso los identificadores (entregas, pedidos, UUID) y las horas cambian entre ejecuciones.
Los tokens de renovación que aparecen son de un solo uso y de una base desechable.

## Evidencias complementarias (3 operaciones)

La corrida principal no ejercitaba tres operaciones. Se documentan aparte, en `complementarias/` (mismo formato: `evidencias.md`,
`evidencias.html`, `pruebas.md` y `evidencias.json`), para no alterar la corrida de 93 casos ni los identificadores que cita el reporte:

| Caso | Operación | Qué demuestra |
|---|---|---|
| DOC-11 | `GET /api/v1/documentos/resumen` | Agregación `$group` en MongoDB por tipo de referencia |
| PLA-17 | `GET /api/v1/escenarios` | Lista paginada de los escenarios compartidos con el web |
| USR-08 | `PUT /api/v1/usuarios/yo` | PUT como alias de PATCH (lo usa la app Android) |

Resultado: **3 de 3 casos pasan**. Se generan con:

```bash
docker compose -f docker-compose.integrado.yml exec entregas python pruebas/evidencias.py --complementarias
docker compose -f docker-compose.integrado.yml cp entregas:/tmp/evidencias_complementarias/. ./evidencias/complementarias
```

Con ellas, las 45 operaciones del código tienen evidencia; el cruce operación → casos está en `servicios/INVENTARIO_ENDPOINTS.md`.
