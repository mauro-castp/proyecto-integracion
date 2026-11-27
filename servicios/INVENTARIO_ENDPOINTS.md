# Inventario vigente de microservicios

Fuente: servicios/*/app.py y docker-compose.integrado.yml.

202 pares método HTTP y ruta de negocio. Excluye salud, OpenAPI, Swagger, HEAD y OPTIONS.

La última columna indica los casos de petición y respuesta que ejercitan cada operación: la corrida principal (`evidencias/ola3/`) y la complementaria (`evidencias/ola3/complementarias/`). Este archivo lo escribe `servicios/pruebas/generar_inventario.py` a partir del código y de esos casos.

| Servicio | Método | Ruta | Casos de evidencia |
|---|---|---|---|
| abastecimiento | GET | `/api/v1/abastecimiento/necesidades` | ABA-01, ABA-02 |
| abastecimiento | GET | `/api/v1/abastecimiento/solicitudes` | ABA-25, ABA-26, ABA-27 |
| abastecimiento | POST | `/api/v1/abastecimiento/solicitudes` | ABA-03, ABA-04, ABA-05 |
| abastecimiento | GET | `/api/v1/abastecimiento/solicitudes/<int:sid>` | ABA-06 |
| abastecimiento | POST | `/api/v1/abastecimiento/solicitudes/<int:sid>/decision` | ABA-07, ABA-08, ABA-10 |
| abastecimiento | POST | `/api/v1/abastecimiento/solicitudes/<int:sid>/ordenar` | ABA-09, ABA-11, ABA-12 |
| abastecimiento | GET | `/api/v1/abastecimiento/ordenes` | ABA-20 |
| abastecimiento | GET | `/api/v1/abastecimiento/ordenes/<int:oid>` | ABA-19 |
| abastecimiento | POST | `/api/v1/abastecimiento/ordenes/<int:oid>/recepcion` | ABA-13, ABA-14, ABA-15, ABA-17, ABA-18 y 1 más |
| abastecimiento | POST | `/api/v1/abastecimiento/ordenes/<int:oid>/cancelar` | ABA-16, ABA-22, ABA-23 |
| abastecimiento | GET | `/api/v1/abastecimiento/seguimiento` | ABA-21 |
| auditoria-monitoreo | GET | `/api/v1/monitoreo/estado` | MNT-02, MNT-03, MNT-11 |
| auditoria-monitoreo | GET | `/api/v1/monitoreo/servicios/<nombre>/historial` | MNT-04 |
| auditoria-monitoreo | GET | `/api/v1/monitoreo/disponibilidad` | MNT-05 |
| auditoria-monitoreo | GET | `/api/v1/monitoreo/metricas` | MNT-06 |
| auditoria-monitoreo | GET | `/api/v1/monitoreo/alertas` | MNT-08 |
| auditoria-monitoreo | POST | `/api/v1/monitoreo/alertas/<int:aid>/reconocer` | MNT-09, MNT-10 |
| auditoria-monitoreo | POST | `/api/v1/monitoreo/verificaciones` | MNT-01 |
| auditoria-monitoreo | GET | `/api/v1/monitoreo/supuestos` | MNT-07 |
| auditoria-monitoreo | GET | `/api/v1/auditoria` | AUD-01, AUD-06 |
| auditoria-monitoreo | GET | `/api/v1/auditoria/accesos` | AUD-02 |
| auditoria-monitoreo | GET | `/api/v1/auditoria/trazabilidad/pedido/<int:pid>` | AUD-03 |
| auditoria-monitoreo | GET | `/api/v1/auditoria/trazabilidad/entrega/<int:eid>` | AUD-04 |
| auditoria-monitoreo | GET | `/api/v1/auditoria/trazabilidad/inventario` | AUD-05 |
| auth | POST | `/api/v1/auth/login` | AUTH-01, AUTH-02, AUTH-03, AUTH-04, AUTH-05 |
| auth | POST | `/api/v1/auth/renovar` | AUTH-08, AUTH-09 |
| auth | POST | `/api/v1/auth/salir` | AUTH-10 |
| auth | GET | `/api/v1/auth/validar` | AUTH-06, AUTH-07, MON-01 |
| capacidad | GET | `/api/v1/capacidad/recursos` | CAP-01 |
| capacidad | GET | `/api/v1/capacidad/recursos/<int:mid>` | CAP-02 |
| capacidad | PUT | `/api/v1/capacidad/recursos/<int:mid>` | CAP-09, CAP-10, CAP-11 |
| capacidad | GET | `/api/v1/capacidad/microhubs` | CAP-13 |
| capacidad | GET | `/api/v1/capacidad/microhubs/<int:mid>` | CAP-03, CAP-04, CAP-05, CAP-06 |
| capacidad | POST | `/api/v1/capacidad/simulaciones` | CAP-07 |
| capacidad | GET | `/api/v1/capacidad/cargas` | CAP-08 |
| capacidad | GET | `/api/v1/capacidad/supuestos` | CAP-12 |
| cobertura | GET | `/api/v1/cobertura/zonas` | COB-01 |
| cobertura | GET | `/api/v1/cobertura/resumen` | COB-02, COB-03 |
| cobertura | GET | `/api/v1/cobertura/punto` | COB-04, COB-05, COB-06 |
| cobertura | POST | `/api/v1/cobertura/evaluaciones` | COB-08, COB-09, COB-10, COB-11, COB-12 |
| cobertura | GET | `/api/v1/cobertura/evaluaciones` | COB-17 |
| cobertura | GET | `/api/v1/cobertura/evaluaciones/<int:eid>` | COB-18 |
| cobertura | GET | `/api/v1/cobertura/candidatos` | COB-07 |
| cobertura | GET | `/api/v1/cobertura/escenarios` | COB-13 |
| cobertura | PUT | `/api/v1/cobertura/zonas/<int:zid>/poblacion` | COB-14, COB-15 |
| cobertura | GET | `/api/v1/cobertura/supuestos` | COB-16 |
| costos | GET | `/api/v1/costos/conceptos` | COS-01, COS-07 |
| costos | POST | `/api/v1/costos/conceptos` | COS-08, COS-09, COS-12, COS-13 |
| costos | PATCH | `/api/v1/costos/conceptos/<int:cid>` | COS-16 |
| costos | PUT | `/api/v1/costos/conceptos/<int:cid>` | COS-10 |
| costos | DELETE | `/api/v1/costos/conceptos/<int:cid>` | COS-11 |
| costos | GET | `/api/v1/costos/resumen` | COS-02, COS-14 |
| costos | GET | `/api/v1/costos/unitarios` | COS-03, COS-06 |
| costos | GET | `/api/v1/costos/rentabilidad` | COS-04 |
| costos | GET | `/api/v1/costos/sensibilidad` | COS-05 |
| costos | GET | `/api/v1/costos/supuestos` | COS-15 |
| demanda | POST | `/api/v1/demanda/sincronizacion` | DEM-13, DEM-14, DEM-15, DEM-16 |
| demanda | GET | `/api/v1/demanda/observaciones` | DEM-01, DEM-02, DEM-03, DEM-04 |
| demanda | GET | `/api/v1/demanda/resumen` | DEM-05 |
| demanda | GET | `/api/v1/demanda/patrones` | DEM-06 |
| demanda | GET | `/api/v1/demanda/proyeccion` | DEM-07, DEM-08, DEM-09 |
| demanda | GET | `/api/v1/demanda/comparacion` | DEM-10 |
| demanda | GET | `/api/v1/demanda/potencial` | DEM-11, DEM-12 |
| demanda | GET | `/api/v1/demanda/supuestos` | DEM-17 |
| documentos | POST | `/api/v1/documentos` | DOC-01, DOC-02, DOC-03, DOC-04, DOC-05 |
| documentos | GET | `/api/v1/documentos` | DOC-06 |
| documentos | GET | `/api/v1/documentos/resumen` | DOC-11 |
| documentos | GET | `/api/v1/documentos/descarga` | ENL-02, ENL-03 |
| documentos | GET | `/api/v1/documentos/<did>` | DOC-07, DOC-10 |
| documentos | GET | `/api/v1/documentos/<did>/enlace` | ENL-01 |
| documentos | GET | `/api/v1/documentos/<did>/contenido` | DOC-08 |
| documentos | DELETE | `/api/v1/documentos/<did>` | DOC-09 |
| entregas | GET | `/api/v1/entregas/repartidores` | ALI-06 |
| entregas | GET | `/api/v1/entregas/mias` | ENT-01 |
| entregas | GET | `/api/v1/entregas` | ENT-11 |
| entregas | GET | `/api/v1/entregas/<int:eid>` | ENT-02, ENT-03, ENT-08 |
| entregas | POST | `/api/v1/entregas/asignaciones` |  |
| entregas | POST | `/api/v1/entregas/<int:eid>/resultado` | ENT-04, ENT-05, ENT-06, ENT-07, ENT-09 y 1 más |
| inventario | GET | `/api/v1/inventario` | INV-01, INV-02, INV-03, INV-04, INV-05 |
| inventario | GET | `/api/v1/inventario/<int:mid>/<int:pid>` | INV-06 |
| inventario | PATCH | `/api/v1/inventario/<int:mid>/<int:pid>/minimo` | INV-18, INV-19 |
| inventario | PUT | `/api/v1/inventario/<int:mid>/<int:pid>/minimo` | INV-23 |
| inventario | GET | `/api/v1/inventario/movimientos` | INV-22 |
| inventario | POST | `/api/v1/inventario/movimientos` | INV-07, INV-08, INV-09, INV-10, INV-11 y 1 más |
| inventario | POST | `/api/v1/inventario/transferencias` | INV-12, INV-13 |
| inventario | GET | `/api/v1/inventario/reservas` | INV-16 |
| inventario | POST | `/api/v1/inventario/reservas` | INV-14, INV-15 |
| inventario | POST | `/api/v1/inventario/reservas/<int:rid>/liberar` | INV-17 |
| inventario | GET | `/api/v1/inventario/alertas` | INV-21 |
| inventario | GET | `/api/v1/inventario/quiebres` | ALI-07, ALI-08 |
| microhubs | GET | `/api/v1/microhubs` | MIC-01, MIC-03 |
| microhubs | GET | `/api/v1/microhubs/<int:mid>` | MIC-02 |
| notificaciones | GET | `/api/v1/notificaciones` | NOT-04, NOT-05 |
| notificaciones | GET | `/api/v1/notificaciones/conteo` | NOT-06 |
| notificaciones | POST | `/api/v1/notificaciones/<int:nid>/leer` | NOT-07, NOT-08 |
| notificaciones | POST | `/api/v1/notificaciones/leer-todas` | NOT-09 |
| notificaciones | DELETE | `/api/v1/notificaciones/<int:nid>` | NOT-14 |
| notificaciones | POST | `/api/v1/notificaciones` | NOT-01, NOT-02, NOT-03, NOT-12 |
| notificaciones | GET | `/api/v1/notificaciones/preferencias` | NOT-10 |
| notificaciones | PUT | `/api/v1/notificaciones/preferencias/<tipo>` | NOT-11, NOT-13 |
| pedidos | GET | `/api/v1/pedidos` | PED-01, PED-02, PED-05 |
| pedidos | GET | `/api/v1/pedidos/<int:pid>` | PED-03, PED-06 |
| pedidos | GET | `/api/v1/pedidos/<int:pid>/historial` | PED-04 |
| pedidos | POST | `/api/v1/pedidos/<int:pid>/estado` | PED-07 |
| pedidos | PATCH | `/api/v1/pedidos/<int:pid>/estado` | PED-08 |
| pedidos | GET | `/api/v1/pedidos/resumen` | ALI-01, ALI-02 |
| pedidos | GET | `/api/v1/pedidos/ventas` | ALI-03 |
| pedidos | GET | `/api/v1/pedidos/listos` | ALI-04, ALI-05, RUT-01 |
| planeacion | GET | `/api/v1/candidatos` | PLA-01 |
| planeacion | GET | `/api/v1/candidatos/<int:cid>` | PLA-16 |
| planeacion | POST | `/api/v1/candidatos` | PLA-02, PLA-03, PLA-12 |
| planeacion | PUT | `/api/v1/candidatos/<int:cid>` | PLA-04 |
| planeacion | POST | `/api/v1/candidatos/<int:cid>/decision` | PLA-06, PLA-07 |
| planeacion | DELETE | `/api/v1/candidatos/<int:cid>` | PLA-15 |
| planeacion | POST | `/api/v1/candidatos/<int:cid>/simular` | PLA-05, PLA-13 |
| planeacion | POST | `/api/v1/simulaciones` | PLA-08 |
| planeacion | GET | `/api/v1/simulaciones/resumen` | PLA-11 |
| planeacion | GET | `/api/v1/escenarios` | PLA-17 |
| planeacion | GET | `/api/v1/escenarios/<int:eid>` | PLA-10 |
| planeacion | POST | `/api/v1/escenarios` | PLA-09 |
| planeacion | DELETE | `/api/v1/escenarios/<int:eid>` | PLA-14 |
| precios | GET | `/api/v1/precios/listas` | PRE-01, PRE-02, PRE-03 |
| precios | POST | `/api/v1/precios/listas` | PRE-04, PRE-05 |
| precios | GET | `/api/v1/precios/listas/<int:lid>` | PRE-08 |
| precios | PUT | `/api/v1/precios/listas/<int:lid>/items/<int:pid>` | PRE-06 |
| precios | GET | `/api/v1/precios/vigente` | PRE-09, PRE-10, PRE-11, PRE-12 |
| precios | POST | `/api/v1/precios/calcular` | PRE-13, PRE-14 |
| precios | GET | `/api/v1/precios/promociones` | PRE-17 |
| precios | POST | `/api/v1/precios/promociones` | PRE-15, PRE-16 |
| precios | DELETE | `/api/v1/precios/promociones/<int:pid>` | PRE-18 |
| precios | GET | `/api/v1/precios/historial` | PRE-07 |
| precios | GET | `/api/v1/precios/margenes` | PRE-19 |
| precios | GET | `/api/v1/precios/sensibilidad` | PRE-20, PRE-21 |
| productos | GET | `/api/v1/productos` | PRO-01, PRO-02, PRO-03, PRO-06, PRO-07 |
| productos | GET | `/api/v1/productos/<int:pid>` | PRO-04, PRO-05 |
| proveedores | GET | `/api/v1/proveedores` | PRV-01, PRV-02, PRV-03 |
| proveedores | POST | `/api/v1/proveedores` | PRV-05, PRV-06, PRV-07, PRV-08 |
| proveedores | GET | `/api/v1/proveedores/<int:pid>` | PRV-04 |
| proveedores | PATCH | `/api/v1/proveedores/<int:pid>` | PRV-21 |
| proveedores | PUT | `/api/v1/proveedores/<int:pid>` | PRV-09 |
| proveedores | DELETE | `/api/v1/proveedores/<int:pid>` | PRV-19 |
| proveedores | GET | `/api/v1/proveedores/<int:pid>/catalogo` | PRV-12 |
| proveedores | PUT | `/api/v1/proveedores/<int:pid>/catalogo/<int:producto_id>` | PRV-10, PRV-11 |
| proveedores | GET | `/api/v1/proveedores/ofertas` | PRV-16, PRV-17, PRV-18, PRV-20 |
| proveedores | GET | `/api/v1/proveedores/<int:pid>/evaluaciones` | PRV-14 |
| proveedores | POST | `/api/v1/proveedores/<int:pid>/evaluaciones` | PRV-13, PRV-15 |
| punto-equilibrio | POST | `/api/v1/punto-equilibrio/calculos` | EQU-01, EQU-02, EQU-03, EQU-04, EQU-05 y 6 más |
| punto-equilibrio | GET | `/api/v1/punto-equilibrio/microhubs` | EQU-18 |
| punto-equilibrio | POST | `/api/v1/punto-equilibrio/sensibilidad` | EQU-08 |
| punto-equilibrio | GET | `/api/v1/punto-equilibrio/escenarios` | EQU-13 |
| punto-equilibrio | GET | `/api/v1/punto-equilibrio/escenarios/<int:eid>` | EQU-15 |
| punto-equilibrio | DELETE | `/api/v1/punto-equilibrio/escenarios/<int:eid>` | EQU-16, EQU-17 |
| punto-equilibrio | GET | `/api/v1/punto-equilibrio/comparacion` | EQU-14 |
| punto-equilibrio | GET | `/api/v1/punto-equilibrio/supuestos` | EQU-19 |
| reportes | GET | `/api/v1/reportes` | REP-01, REP-09 |
| reportes | GET | `/api/v1/reportes/<clave>` | REP-03, REP-04, REP-08 |
| reportes | GET | `/api/v1/reportes/<clave>/grafica` | REP-05 |
| reportes | GET | `/api/v1/reportes/<clave>/exportar` | REP-06 |
| reportes | GET | `/api/v1/reportes/exportaciones/<int:eid>/enlace` |  |
| reportes | GET | `/api/v1/reportes/descarga` |  |
| reportes | GET | `/api/v1/reportes/exportaciones` | REP-07 |
| reportes | GET | `/api/v1/reportes/indicadores` | REP-02 |
| rutas | POST | `/api/v1/rutas/planes` | RUT-02, RUT-04, RUT-05, RUT-14, RUT-15 y 3 más |
| rutas | GET | `/api/v1/rutas/planes` | RUT-12 |
| rutas | GET | `/api/v1/rutas/planes/<int:pid>` | RUT-09 |
| rutas | POST | `/api/v1/rutas/planes/<int:pid>/confirmar` | RUT-10, RUT-11 |
| rutas | POST | `/api/v1/rutas/planes/<int:pid>/cancelar` | RUT-13 |
| rutas | POST | `/api/v1/rutas/comparaciones` | RUT-03 |
| rutas | POST | `/api/v1/rutas/planes/<int:pid>/ajustes` | RUT-06, RUT-07, RUT-08 |
| rutas | GET | `/api/v1/rutas/supuestos` | RUT-19 |
| seguimiento | POST | `/api/v1/seguimiento/<int:eid>/ubicaciones` | SEG-01 |
| seguimiento | GET | `/api/v1/seguimiento/<int:eid>/recorrido` | SEG-02, SEG-03, SEG-04 |
| simulacion | POST | `/api/v1/simulacion/ejecuciones` | SIM-01, SIM-07, SIM-09, SIM-10, SIM-15 y 1 más |
| simulacion | GET | `/api/v1/simulacion/ejecuciones` | SIM-13, SIM-14 |
| simulacion | GET | `/api/v1/simulacion/ejecuciones/<eid>` | SIM-02, SIM-04, SIM-05, SIM-08, SIM-17 |
| simulacion | POST | `/api/v1/simulacion/ejecuciones/<eid>/cancelar` | SIM-11, SIM-12 |
| simulacion | POST | `/api/v1/simulacion/ejecuciones/<eid>/repetir` | SIM-03 |
| simulacion | GET | `/api/v1/simulacion/comparacion` | SIM-06 |
| simulacion | GET | `/api/v1/simulacion/supuestos` | SIM-18 |
| sincronizacion | POST | `/api/v1/sincronizacion/lotes` | SYN-01, SYN-02, SYN-03, SYN-10, SYN-11 |
| sincronizacion | GET | `/api/v1/sincronizacion/lotes` | SYN-05 |
| sincronizacion | GET | `/api/v1/sincronizacion/lotes/<int:lid>` | SYN-06 |
| sincronizacion | GET | `/api/v1/sincronizacion/pendientes` | SYN-07 |
| sincronizacion | GET | `/api/v1/sincronizacion/conflictos` | SYN-04 |
| sincronizacion | GET | `/api/v1/sincronizacion/estado` | SYN-08, SYN-12 |
| sincronizacion | GET | `/api/v1/sincronizacion/supuestos` | SYN-09 |
| surtido | GET | `/api/v1/surtido/abc` | SUR-01 |
| surtido | GET | `/api/v1/surtido/analisis` | SUR-02, SUR-03, SUR-04, SUR-05, SUR-06 y 2 más |
| surtido | POST | `/api/v1/surtido/recomendaciones` | SUR-13, SUR-16 |
| surtido | GET | `/api/v1/surtido/recomendaciones` | SUR-18 |
| surtido | GET | `/api/v1/surtido/recomendaciones/<int:rid>` | SUR-14, SUR-15 |
| surtido | GET | `/api/v1/surtido/restricciones/<int:mid>` | SUR-09 |
| surtido | PATCH | `/api/v1/surtido/restricciones/<int:mid>` | SUR-19 |
| surtido | PUT | `/api/v1/surtido/restricciones/<int:mid>` | SUR-10, SUR-11, SUR-12 |
| surtido | GET | `/api/v1/surtido/supuestos` | SUR-17 |
| usuarios | GET | `/api/v1/usuarios/yo` | AUTH-11, USR-01, USR-02 |
| usuarios | PATCH | `/api/v1/usuarios/yo` | USR-03, USR-04 |
| usuarios | PUT | `/api/v1/usuarios/yo` | USR-08 |
| usuarios | GET | `/api/v1/usuarios` | USR-05, USR-06 |
| usuarios | GET | `/api/v1/usuarios/<int:uid>` | USR-07 |
| zonas | GET | `/api/v1/zonas` | ZON-01, ZON-04, RAT-01 |
| zonas | GET | `/api/v1/zonas/<int:zid>` | ZON-02, ZON-03 |

## Contratos y compatibilidad

Productos, Zonas y Microhubs conservan catalogos.xsd. Seguimiento utiliza estructuras de entregas.xsd. Inventario, Precios, Proveedores, Abastecimiento y Notificaciones (Ola 1) y Demanda, Cobertura, Capacidad, Rutas, Costos, Punto de equilibrio, Simulación y Surtido (Ola 2) tienen su propio XSD, generado con `servicios/contratos/generar.py` a partir de `contratos/ola1.py` y `contratos/ola2.py`; las referencias que comparten están en comun_ola1.xsd y comun_ola2.xsd. Lo que pedidos, entregas e inventario ganaron en la Ola 2 (resumen, ventas, listos, repartidores, quiebres) está en pedidos_ola2.xsd, entregas_ola2.xsd e inventario_ola2.xsd. Auditoría y monitoreo, Reportes y Sincronización (Ola 3) tienen auditoria_monitoreo.xsd, reportes.xsd y sincronizacion.xsd (`contratos/ola3.py`). El envío de un lote de sincronización es solo JSON, y la descarga de un reporte devuelve el archivo (CSV, Excel o PDF).

La ruta GPS antigua bajo entregas ya no se ofrece. El puerto 5108 corresponde a Zonas y el 5124 a Notificaciones, que vuelve como servicio de la Ola 1 con su propia bandeja, envío por rol y preferencias.

## Operaciones nuevas de la entrega final

Las ejercita el recorrido de punta a punta `servicios/pruebas/procesos_integrales.py`
([`evidencias/procesos/procesos_integrales.md`](../evidencias/procesos/procesos_integrales.md)), no la corrida de evidencias de la Ola 3:

| Servicio | Método | Ruta | Evidencia |
|---|---|---|---|
| entregas | POST | `/api/v1/entregas/asignaciones` | P3: confirmar y despachar (y la compensación con 403) |
| reportes | GET | `/api/v1/reportes/exportaciones/<int:eid>/enlace` | P3: descarga del reporte archivado |
| reportes | GET | `/api/v1/reportes/descarga` | P3: descarga firmada con el almacén local |
