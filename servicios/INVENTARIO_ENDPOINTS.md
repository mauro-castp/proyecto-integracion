# Inventario vigente de microservicios

Fuente: servicios/*/app.py y docker-compose.integrado.yml.

45 pares método HTTP y ruta de negocio. Excluye salud, OpenAPI, Swagger, HEAD y OPTIONS.

La última columna indica los casos de petición y respuesta que ejercitan cada operación: la corrida principal (`evidencias/`, 93 casos) y la complementaria (`evidencias/complementarias/`, 3 casos: DOC-11, PLA-17 y USR-08).

| Servicio | Método | Ruta | Casos de evidencia |
|---|---|---|---|
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
| microhubs | GET | `/api/v1/microhubs` | MIC-01, MIC-03 |
| microhubs | GET | `/api/v1/microhubs/<int:mid>` | MIC-02 |
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
| productos | GET | `/api/v1/productos` | PRO-01, PRO-02, PRO-03, PRO-06, PRO-07 |
| productos | GET | `/api/v1/productos/<int:pid>` | PRO-04, PRO-05 |
| seguimiento | POST | `/api/v1/seguimiento/<int:eid>/ubicaciones` | SEG-01 |
| seguimiento | GET | `/api/v1/seguimiento/<int:eid>/recorrido` | SEG-02, SEG-03, SEG-04 |
| usuarios | GET | `/api/v1/usuarios/yo` | AUTH-11, USR-01, USR-02 |
| usuarios | PATCH | `/api/v1/usuarios/yo` | USR-03, USR-04 |
| usuarios | PUT | `/api/v1/usuarios/yo` | USR-08 |
| usuarios | GET | `/api/v1/usuarios` | USR-05, USR-06 |
| usuarios | GET | `/api/v1/usuarios/<int:uid>` | USR-07 |
| zonas | GET | `/api/v1/zonas` | RAT-01, ZON-01, ZON-04 |
| zonas | GET | `/api/v1/zonas/<int:zid>` | ZON-02, ZON-03 |

## Contratos y compatibilidad

Productos, Zonas y Microhubs conservan catalogos.xsd. Seguimiento utiliza estructuras de entregas.xsd. notificaciones.xsd se conserva como contrato histórico y no implica un servicio activo.

La ruta GPS antigua bajo entregas ya no se ofrece. El puerto 5108 corresponde a Zonas. Los avisos se gestionan mediante el portal web y triggers PostgreSQL.