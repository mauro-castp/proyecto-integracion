# Evidencias

| Carpeta | Qué contiene |
|---|---|
| [`ola3/`](ola3/) (vigente), [`ola1/`](ola1/), [`ola2/`](ola2/) | Petición y respuesta por caso: 403 casos con los 26 servicios |
| [`nube/`](nube/LEEME.md) | Lo comprobado en Google Cloud: salud de los 26 servicios, contenedores, puertos, bucket, Cloud Logging, 401 casos |
| [`volumen/`](volumen/LEEME.md) | **Entrega final**: 100 000 pedidos y 1.4 M de puntos GPS; inserción, índices, caché, escalabilidad y recursos |
| [`carga/`](carga/RESULTADOS.md) | **Entrega final**: Locust (normal, alta, estrés y recuperación, protección), con HTML y CSV |
| [`fallos/`](fallos/fallos_infraestructura.md) | **Entrega final**: servicio, Redis, MongoDB, PostgreSQL, bucket y tiempo excedido |
| [`procesos/`](procesos/procesos_integrales.md) | **Entrega final**: los tres procesos integrales de punta a punta |
| [`algoritmos/`](algoritmos/benchmark.md) | **Entrega final**: calidad y tiempo de rutas y Monte Carlo |
| esta carpeta (raíz) | La corrida del Segundo Parcial (93 casos), que cita el reporte v4.3 |

# Evidencias de petición y respuesta (anexo E1)

> Esta carpeta es la corrida del 13 de octubre de 2026 (Segundo Parcial, 93 casos); el reporte técnico v4.3 cita sus números. La corrida con los 15 servicios (204 casos) está en [`ola1/`](ola1/), la de la Ola 2 en
> [`ola2/`](ola2/), la **vigente con los 26 servicios (403 casos, 403 aprobados, 26 de noviembre de 2026)** en [`ola3/`](ola3/) y lo comprobado en Google
> Cloud en [`nube/`](nube/).

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
