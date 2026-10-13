# Evidencias de petición y respuesta (anexo E1)

Ejecución completa de `servicios/pruebas/evidencias.py` contra los ocho microservicios desplegados con
`docker-compose.integrado.yml`, sobre una base creada desde cero: **93 de 93 casos pasan** (13 de octubre de 2026,
14:12 en la hora UTC del contenedor).

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
