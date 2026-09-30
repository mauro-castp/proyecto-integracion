# Cambios de la entrega: módulo de Planeación y viabilidad

Rama: `feature/planeacion-integrada` · Codex Innovations · Equipo 04

Responde a la retroalimentación del profesor: pasar de un sistema de pedidos a una plataforma que
evalúa **si conviene abrir un microhub**. Detalle completo en
[`reporte_tecnico/Reporte_Tecnico_Equipo04.docx`](reporte_tecnico/Reporte_Tecnico_Equipo04.docx).

## Qué se agregó

| Módulo de la retro | Dónde está |
|---|---|
| 1 Analizar demanda (día, hora, zona, categoría, no atendida, ticket, productos/pedido) | `/planeacion/demanda` |
| 2 Proponer ubicaciones (catálogo de candidatos, score con pesos configurables) | `/planeacion/candidatos` |
| Cobertura (hogares, demanda cubierta y fuera, última milla, solapamiento) y mapa | `/planeacion/cobertura` |
| 3 Simular operación · 4 Calcular capacidad · 7 Punto de equilibrio · sensibilidad · ficha de viabilidad | `/planeacion/simulacion` |
| 5 Planear surtido (ABC; Aumentar, Mantener, Reducir, Eliminar) | `/planeacion/surtido` |
| 6 Optimizar entregas (listos → zona → repartidor → ruta → paradas) | `/planeacion/entregas` |
| 8 Comparar escenarios (guardar, abrir, editar, comparar, CSV) | `/planeacion/escenarios` |
| Paneles por perfil | `/panel/operador`, `/panel/administrador`, `/planeacion/tablero` |
| Reporte técnico único (36 apartados) | `reporte_tecnico/` |

## Cambios en el código existente

- `bloque_c/sql/06_planeacion.sql` (nuevo, idempotente): tablas `ubicacion_candidata`, `escenario_planeacion`,
  `plan_ruta`, `plan_ruta_parada`; columnas nuevas en `producto`, `zona`, `entrega` y `pedido.listo_en`;
  26 parámetros con su justificación; permisos `planeacion.ver` y `planeacion.editar`; auditoría de las tablas nuevas.
- `sistema_web/docker-compose.yml`: la aplicación aplica la migración al iniciar (`migrar_planeacion.py`),
  así que funciona con volúmenes de PostgreSQL ya creados. Puerto configurable con `WEB_PORT`.
- `sistema_web/rutas.py` y `templates/operacion_pedido.html`: el detalle del pedido muestra repartidor, parada,
  distancia, tiempo y costo; el botón «Marcar listo para ruta» (que despachaba sin agrupar) pasa a
  «Marcar listo para despacho». El despacho directo sigue como excepción.
- `sistema_web/app.py`, `app_local.py`, `templates/base.html`: registro del módulo y opciones de menú.

## Integración con la versión de Vanessa (commit `d58cdb8`)

Dos implementaciones del mismo módulo coincidieron en nombres de archivo. Se fusionaron así:

- **Base:** la de 8 módulos; se conservan el nombre `planeacion_bp` y el registro en `app_local.py`.
- **Se rescató** el modo local de demostración con el ejemplo de la retro (82, 54 y 39 pedidos/día):
  ahora `python app_local.py` abre todas las pantallas sin Docker (`planeacion_demo.py`).
- **Se retiraron** `sistema_web/base.html` y `sistema_web/planeacion.html` (estaban fuera de `templates/`, por lo
  que Flask no los encontraba) y `06_planeacion.sql` de la raíz (Docker lo busca en `bloque_c/sql/`).

## Pruebas

| Prueba | Resultado |
|---|---|
| `test_planeacion.py` (cálculos, sin Flask) | 16 de 16 |
| `test_planeacion_local.py` (modo local) | 6 de 6 |
| `prueba_e2e_planeacion.py` (Docker, con despacho real) | 23 de 23 |
| `bloque_c/sql/05_pruebas_reglas.sql` (reglas del Primer Parcial) | 26 de 26 |

## Limitaciones conocidas

- Los datos históricos de demostración de Docker son pocos (~4 pedidos/día): con ellos ningún candidato resulta viable.
  El modo local sí reproduce el ejemplo de la retro.
- Cobertura por centroide y radio (sin polígonos GIS); capacidad lineal (sin colas M/M/c); reparto sin VRP completo.
- Pendientes del equipo: matrículas, participación individual, capturas de las pantallas nuevas y actualizar los
  diagramas del Bloque D.
