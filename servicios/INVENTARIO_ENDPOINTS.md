# Inventario vigente de microservicios

Fuente: servicios/*/app.py y docker-compose.integrado.yml del ZIP recibido.

45 pares método HTTP y ruta de negocio. Excluye salud, OpenAPI, Swagger, HEAD y OPTIONS.

| Servicio | Método | Ruta |
|---|---|---|
| auth | POST | `/api/v1/auth/login` |
| auth | POST | `/api/v1/auth/renovar` |
| auth | POST | `/api/v1/auth/salir` |
| auth | GET | `/api/v1/auth/validar` |
| documentos | POST | `/api/v1/documentos` |
| documentos | GET | `/api/v1/documentos` |
| documentos | GET | `/api/v1/documentos/resumen` |
| documentos | GET | `/api/v1/documentos/<did>` |
| documentos | GET | `/api/v1/documentos/<did>/contenido` |
| documentos | DELETE | `/api/v1/documentos/<did>` |
| entregas | GET | `/api/v1/entregas/mias` |
| entregas | GET | `/api/v1/entregas` |
| entregas | GET | `/api/v1/entregas/<int:eid>` |
| entregas | POST | `/api/v1/entregas/<int:eid>/resultado` |
| microhubs | GET | `/api/v1/microhubs` |
| microhubs | GET | `/api/v1/microhubs/<int:mid>` |
| pedidos | GET | `/api/v1/pedidos` |
| pedidos | GET | `/api/v1/pedidos/<int:pid>` |
| pedidos | GET | `/api/v1/pedidos/<int:pid>/historial` |
| pedidos | POST | `/api/v1/pedidos/<int:pid>/estado` |
| pedidos | PATCH | `/api/v1/pedidos/<int:pid>/estado` |
| planeacion | GET | `/api/v1/candidatos` |
| planeacion | GET | `/api/v1/candidatos/<int:cid>` |
| planeacion | POST | `/api/v1/candidatos` |
| planeacion | PUT | `/api/v1/candidatos/<int:cid>` |
| planeacion | POST | `/api/v1/candidatos/<int:cid>/decision` |
| planeacion | DELETE | `/api/v1/candidatos/<int:cid>` |
| planeacion | POST | `/api/v1/candidatos/<int:cid>/simular` |
| planeacion | POST | `/api/v1/simulaciones` |
| planeacion | GET | `/api/v1/simulaciones/resumen` |
| planeacion | GET | `/api/v1/escenarios` |
| planeacion | GET | `/api/v1/escenarios/<int:eid>` |
| planeacion | POST | `/api/v1/escenarios` |
| planeacion | DELETE | `/api/v1/escenarios/<int:eid>` |
| productos | GET | `/api/v1/productos` |
| productos | GET | `/api/v1/productos/<int:pid>` |
| seguimiento | POST | `/api/v1/seguimiento/<int:eid>/ubicaciones` |
| seguimiento | GET | `/api/v1/seguimiento/<int:eid>/recorrido` |
| usuarios | GET | `/api/v1/usuarios/yo` |
| usuarios | PATCH | `/api/v1/usuarios/yo` |
| usuarios | PUT | `/api/v1/usuarios/yo` |
| usuarios | GET | `/api/v1/usuarios` |
| usuarios | GET | `/api/v1/usuarios/<int:uid>` |
| zonas | GET | `/api/v1/zonas` |
| zonas | GET | `/api/v1/zonas/<int:zid>` |

## Contratos y compatibilidad

Productos, Zonas y Microhubs conservan catalogos.xsd. Seguimiento utiliza estructuras de entregas.xsd. notificaciones.xsd se conserva como contrato histórico y no implica un servicio activo.

La ruta GPS antigua bajo entregas ya no se ofrece. El puerto 5108 corresponde a Zonas. Los avisos se gestionan mediante el portal web y triggers PostgreSQL.