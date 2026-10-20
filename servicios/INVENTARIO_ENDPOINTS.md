# Inventario vigente de microservicios

Fuente: servicios/*/app.py y docker-compose.integrado.yml.

98 pares método HTTP y ruta de negocio. Excluye salud, OpenAPI, Swagger, HEAD y OPTIONS.

La última columna indica los casos de petición y respuesta que ejercitan cada operación: la corrida principal (`evidencias/ola1/`) y la complementaria (`evidencias/ola1/complementarias/`). Este archivo lo escribe `servicios/pruebas/generar_inventario.py` a partir del código y de esos casos.

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
| auth | POST | `/api/v1/auth/login` | AUTH-01, AUTH-02, AUTH-03, AUTH-04, AUTH-05 |
| auth | POST | `/api/v1/auth/renovar` | AUTH-08, AUTH-09 |
| auth | POST | `/api/v1/auth/salir` | AUTH-10 |
| auth | GET | `/api/v1/auth/validar` | AUTH-06, AUTH-07, MON-01 |
| documentos | POST | `/api/v1/documentos` | DOC-01, DOC-02, DOC-03, DOC-04, DOC-05 |
| documentos | GET | `/api/v1/documentos` | DOC-06 |
| documentos | GET | `/api/v1/documentos/resumen` | DOC-11 |
| documentos | GET | `/api/v1/documentos/<did>` | DOC-07, DOC-10 |
| documentos | GET | `/api/v1/documentos/<did>/contenido` | DOC-08 |
| documentos | DELETE | `/api/v1/documentos/<did>` | DOC-09 |
| entregas | GET | `/api/v1/entregas/mias` | ENT-01 |
| entregas | GET | `/api/v1/entregas` | ENT-11 |
| entregas | GET | `/api/v1/entregas/<int:eid>` | ENT-02, ENT-03, ENT-08 |
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
| seguimiento | POST | `/api/v1/seguimiento/<int:eid>/ubicaciones` | SEG-01 |
| seguimiento | GET | `/api/v1/seguimiento/<int:eid>/recorrido` | SEG-02, SEG-03, SEG-04 |
| usuarios | GET | `/api/v1/usuarios/yo` | AUTH-11, USR-01, USR-02 |
| usuarios | PATCH | `/api/v1/usuarios/yo` | USR-03, USR-04 |
| usuarios | PUT | `/api/v1/usuarios/yo` | USR-08 |
| usuarios | GET | `/api/v1/usuarios` | USR-05, USR-06 |
| usuarios | GET | `/api/v1/usuarios/<int:uid>` | USR-07 |
| zonas | GET | `/api/v1/zonas` | ZON-01, ZON-04, RAT-01 |
| zonas | GET | `/api/v1/zonas/<int:zid>` | ZON-02, ZON-03 |

## Contratos y compatibilidad

Productos, Zonas y Microhubs conservan catalogos.xsd. Seguimiento utiliza estructuras de entregas.xsd. Inventario, Precios, Proveedores, Abastecimiento y Notificaciones tienen su propio XSD, generado con `servicios/contratos/generar.py`; las referencias que comparten están en comun_ola1.xsd.

La ruta GPS antigua bajo entregas ya no se ofrece. El puerto 5108 corresponde a Zonas y el 5124 a Notificaciones, que vuelve como servicio de la Ola 1 con su propia bandeja, envío por rol y preferencias.
