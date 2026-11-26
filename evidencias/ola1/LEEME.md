# Evidencias de petición y respuesta con los quince servicios (Tercer Parcial · Ola 1)

Ejecución completa de `servicios/pruebas/evidencias.py` contra los quince microservicios desplegados con `docker-compose.integrado.yml`, sobre una
base creada desde cero (scripts 01 a 09): **204 de 204 casos pasan** (19 de octubre de 2026, 19:31 hora de Monterrey; 01:31 UTC del contenedor).

| Archivo | Contenido |
|---|---|
| `evidencias.md`, `evidencias.html`, `pruebas.md`, `evidencias.json` | Lo mismo que en la corrida del Segundo Parcial: petición, respuesta, explicación y lo que quedó en PostgreSQL, MongoDB o Redis |
| `complementarias/` | Los tres casos que la corrida principal no ejercita (`DOC-11`, `PLA-17`, `USR-08`) |
| `fallo_inventario.md` | Recorrido con contenedores reales: se apaga inventario, llega mercancía, se vuelve a encender y se reintenta |

Los casos son los 93 de la corrida del 13 de octubre (con otros identificadores, porque cada corrida crea sus datos), 5 de salud de los servicios nuevos y
106 de la Ola 1: `INV-*` (inventario), `PRE-*` (precios), `PRV-*` (proveedores), `ABA-*` (abastecimiento) y `NOT-*` (notificaciones).

```bash
docker compose -f docker-compose.integrado.yml exec entregas python pruebas/evidencias.py
docker compose -f docker-compose.integrado.yml exec entregas python pruebas/evidencias.py --complementarias
docker compose -f docker-compose.integrado.yml cp entregas:/tmp/evidencias ./evidencias/ola1
python servicios/pruebas/demo_fallo_inventario.py        # escribe fallo_inventario.md
python servicios/pruebas/generar_inventario.py           # cruza operaciones y casos en servicios/INVENTARIO_ENDPOINTS.md
```

Con estos casos las 98 operaciones del código tienen evidencia (`servicios/INVENTARIO_ENDPOINTS.md`).
