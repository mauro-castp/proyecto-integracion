# Correcciones después de la retroalimentación del profesor (27 de noviembre de 2026)

Video con las correcciones: https://youtu.be/zwWkkMCn0qc

| Observación del profesor | Qué cambiamos | Dónde verlo |
|---|---|---|
| ¿Cómo identifican dónde poner los microhubs? | Algoritmo de **facility location** (cobertura máxima con p microhubs: voraz + intercambio de Teitz y Bart) que propone las sedes | Portal: Planeación → **★ Dónde poner microhubs** · servicio `ubicacion` (5127) `POST /api/v1/ubicacion/propuestas` · `servicios/comun/ubicacion_calc.py` |
| ¿Cuál es la comunidad de bajos ingresos y cómo lo saben? ¿Dónde está geográficamente? | Dato oficial: **índice de marginación urbana por colonia 2020 de CONAPO** (Censo 2020 del INEGI). Bajos ingresos = grado Medio, Alto o Muy alto: 82 de 173 colonias de San Bernabé y vecinas, 166,797 habitantes. Se ve en un **mapa** con cada colonia coloreada | `bloque_c/sql/18_marginacion_colonias.sql` (generado con `bloque_c/scripts/importar_marginacion.py` desde la cartografía de CONAPO) · mapa en el portal · `GET /api/v1/ubicacion/mapa` (GeoJSON) |
| Integrar forzosamente facility location, break-even y simulación de demanda | Un solo recorrido: simulación de demanda (Monte Carlo, Poisson por colonia) → facility location → punto de equilibrio de cada microhub propuesto, con veredicto y penetración mínima | Misma pantalla y servicio; pruebas en `servicios/pruebas/test_unitarias_ubicacion.py` |
| El monolito no debe apuntar jamás a los microservicios | Se quitaron `sistema_web/integracion.py` y `procesos.py`: el portal solo se conecta a PostgreSQL y Redis. «Mis archivos» se guarda en PostgreSQL (`20_portal_archivos.sql`) y el panel de monitoreo lee las tablas del monitor | `sistema_web/app.py`, `sistema_web/monitoreo_web.py`, `sistema_web/web_ampliado.py` |
| Faltan firewall, balanceador, API gateway y reverse proxy en los diagramas | Diagramas 2 (contenedores) y 18 (GCP) rehechos: firewall de VPC, Nginx como reverse proxy y API gateway, balanceo (gunicorn hoy; Cloud Load Balancing al escalar), monolito → solo sus bases | `bloque_d/fuentes/02_contenedores.puml`, `18_despliegue_gcp.puml` y sus PNG |
| Quitar términos como saga e idempotencia | La presentación lo explica con palabras simples | `presentacion/Microhubs · Presentación final.pptx` |
| Mostrar Locust, hasta dónde aguanta y qué le diríamos al cliente | Diapositiva con las gráficas reales del reporte de Locust en GCP: 0 errores hasta 100 usuarios simultáneos (p95 1.3 s); se satura con 200. Mensaje al cliente | `evidencias/nube/carga/carga.html` · diapositiva 18 |
| UI/UX de la app móvil: amontonada, no se entiende el menú | Menú inferior fijo con las secciones de cada perfil (cliente: Inicio, Catálogo, Carrito, Pedidos, Avisos; repartidor: Inicio, Entregas, Avisos, Perfil) | `app_movil/.../Ui.kt` (`navegacion`), `MainActivity.kt` (`menu`) |
| Cada repartidor debe tener un microhub asignado | `repartidor1` → MH-01, `repartidor2` → MH-02, `repartidor3@codex.mx` (nuevo) → MH-03. La base rechaza asignar un pedido de otro microhub (RN41, trigger `trg_entrega_repartidor_microhub`); el despacho y la lista de repartidores se filtran por microhub; la app muestra «Tu microhub» | `bloque_c/sql/19_repartidor_microhub.sql`, `servicios/entregas/app.py`, `servicios/rutas/app.py` |

Resultado con los supuestos de la pantalla (8 % de hogares que piden, 1.2 pedidos por semana, radio de 1.5 km, capacidad 160/día):
3 microhubs propuestos (Fomerrey 15, El Ranchito, Fomerrey 105) cubren el **94 %** de la demanda de bajos ingresos; cada uno necesita
**152 pedidos/día** para el equilibrio y los tres salen **viables ajustados**. La penetración mínima para llegar al equilibrio es de 4.6 a 7.7 % de los hogares.

Pruebas corridas después de los cambios (plataforma local con PostgreSQL, Redis y MongoDB reales), todas sin fallas: unitarias (117, incluidas
las 6 nuevas de ubicación), contrato de los 27 servicios, olas 1 a 4, almacén y apps cliente; Android: 85 pruebas en la JVM y compilación de todas las pantallas.
