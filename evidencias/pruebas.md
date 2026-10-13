# Pruebas ejecutadas · microservicios v1

| ID | Servicio | Objetivo | Entrada | Esperado | Obtenido | Estado |
|---|---|---|---|---|---|---|
| AUTH-01 | auth | Emitir el JWT de acceso y el token de renovación del repartidor. | `POST /api/v1/auth/login` | 200 | 200 | PASA |
| AUTH-02 | auth | La app de escritorio entra con XML validado por auth.xsd. | `POST /api/v1/auth/login` | 200 | 200 | PASA |
| AUTH-03 | auth | Rechazar credenciales y contar el intento. | `POST /api/v1/auth/login` | 401 | 401 | PASA |
| AUTH-04 | auth | Validación de entrada con detalle por campo. | `POST /api/v1/auth/login` | 422 | 422 | PASA |
| AUTH-05 | auth | Rechazar entidades externas y DTD. | `POST /api/v1/auth/login` | 400 | 400 | PASA |
| AUTH-06 | auth | Comprobar firma, vigencia y sesión activa en Redis. | `GET /api/v1/auth/validar` | 200 | 200 | PASA |
| AUTH-07 | auth | Un token con la firma modificada no pasa. | `GET /api/v1/auth/validar` | 401 | 401 | PASA |
| AUTH-08 | auth | Obtener tokens nuevos con el token de renovación (rotación). | `POST /api/v1/auth/renovar` | 200 | 200 | PASA |
| AUTH-09 | auth | Un token de renovación sirve una sola vez. | `POST /api/v1/auth/renovar` | 401 | 401 | PASA |
| AUTH-10 | auth | Revocar el acceso del encabezado y la renovación del cuerpo. | `POST /api/v1/auth/salir` | 204 | 204 | PASA |
| AUTH-11 | usuarios | Una sesión cerrada ya no entra a ningún servicio. | `GET /api/v1/usuarios/yo` | 401 | 401 | PASA |
| USR-01 | usuarios | Consultar el perfil de quien inició sesión. | `GET /api/v1/usuarios/yo` | 200 | 200 | PASA |
| USR-02 | usuarios | El mismo recurso en XML según Accept. | `GET /api/v1/usuarios/yo` | 200 | 200 | PASA |
| USR-03 | usuarios | Modificar un dato del perfil. | `PATCH /api/v1/usuarios/yo` | 200 | 200 | PASA |
| USR-04 | usuarios | Validación de patrón (10 dígitos). | `PATCH /api/v1/usuarios/yo` | 422 | 422 | PASA |
| USR-05 | usuarios | Búsqueda y paginación. | `GET /api/v1/usuarios?q=codex&rol=operador&pagina=1&por_pagina=5` | 200 | 200 | PASA |
| USR-06 | usuarios | Un repartidor no tiene usuarios.ver. | `GET /api/v1/usuarios` | 403 | 403 | PASA |
| USR-07 | usuarios | Registro que no existe. | `GET /api/v1/usuarios/999999` | 404 | 404 | PASA |
| PRO-01 | productos | Consultar productos; la respuesta se guarda en Redis. | `GET /api/v1/productos?q=arroz&pagina=1&por_pagina=5` | 200 | 200 | PASA |
| PRO-02 | productos | La segunda consulta no toca PostgreSQL. | `GET /api/v1/productos?q=arroz&pagina=1&por_pagina=5` | 200 | 200 | PASA |
| PRO-03 | productos | Lista en XML válida contra catalogos.xsd. | `GET /api/v1/productos?pagina=1&por_pagina=2` | 200 | 200 | PASA |
| PRO-04 | productos | Detalle por id. | `GET /api/v1/productos/3` | 200 | 200 | PASA |
| PRO-05 | productos | Registro que no existe. | `GET /api/v1/productos/999999` | 404 | 404 | PASA |
| PRO-06 | productos | por_pagina máximo 100. | `GET /api/v1/productos?por_pagina=500` | 400 | 400 | PASA |
| PRO-07 | productos | Todo endpoint protegido exige Authorization: Bearer. | `GET /api/v1/productos` | 401 | 401 | PASA |
| ZON-01 | zonas | Colonias atendidas con centroide, válidas contra catalogos.xsd. | `GET /api/v1/zonas` | 200 | 200 | PASA |
| ZON-02 | zonas | Detalle por id. | `GET /api/v1/zonas/1` | 200 | 200 | PASA |
| ZON-03 | zonas | Registro que no existe. | `GET /api/v1/zonas/999999` | 404 | 404 | PASA |
| ZON-04 | zonas | Todo endpoint protegido exige Authorization: Bearer. | `GET /api/v1/zonas` | 401 | 401 | PASA |
| MIC-01 | microhubs | Microhubs con coordenadas y radio. | `GET /api/v1/microhubs?estatus=activo` | 200 | 200 | PASA |
| MIC-02 | microhubs | Registro que no existe. | `GET /api/v1/microhubs/999999` | 404 | 404 | PASA |
| MIC-03 | microhubs | Todo endpoint protegido exige Authorization: Bearer. | `GET /api/v1/microhubs` | 401 | 401 | PASA |
| PED-01 | pedidos | Lista filtrada por estado y fechas. | `GET /api/v1/pedidos?estado=entregado&pagina=1&por_pagina=5` | 200 | 200 | PASA |
| PED-02 | pedidos | La misma lista en XML. | `GET /api/v1/pedidos?estado=entregado&por_pagina=2` | 200 | 200 | PASA |
| PED-03 | pedidos | Cliente, domicilio y líneas del pedido. | `GET /api/v1/pedidos/105` | 200 | 200 | PASA |
| PED-04 | pedidos | Cambios de estado con usuario y fecha. | `GET /api/v1/pedidos/105/historial` | 200 | 200 | PASA |
| PED-05 | pedidos | Un estado que no existe se rechaza. | `GET /api/v1/pedidos?estado=inventado` | 400 | 400 | PASA |
| PED-06 | pedidos | El operador del MH-01 no ve pedidos de otro microhub (RN22). | `GET /api/v1/pedidos/1` | 404 | 404 | PASA |
| PED-07 | pedidos | Los cierres de entrega solo se registran en el servicio de entregas. | `POST /api/v1/pedidos/105/estado` | 409 | 409 | PASA |
| PED-08 | pedidos | Un pedido entregado no puede regresar a preparación. | `PATCH /api/v1/pedidos/2/estado` | 422 | 422 | PASA |
| DOC-01 | documentos | Guardar la foto en MongoDB ligada a la entrega. | `POST /api/v1/documentos` | 201 | 201 | PASA |
| DOC-02 | documentos | Evidencia para el cierre parcial. | `POST /api/v1/documentos` | 201 | 201 | PASA |
| DOC-03 | documentos | Un PDF declarado como JPEG se rechaza por su firma. | `POST /api/v1/documentos` | 422 | 422 | PASA |
| DOC-04 | documentos | Un repartidor no adjunta a entregas de otro. | `POST /api/v1/documentos` | 403 | 403 | PASA |
| DOC-05 | documentos | Documento que después se elimina. | `POST /api/v1/documentos` | 201 | 201 | PASA |
| DOC-06 | documentos | Filtro por referencia. | `GET /api/v1/documentos?referencia_tipo=entrega&referencia_id=129` | 200 | 200 | PASA |
| DOC-07 | documentos | Documento en XML, sin contenido. | `GET /api/v1/documentos/6acea24bbf5616d8602a1205` | 200 | 200 | PASA |
| DOC-08 | documentos | Recuperar el archivo. | `GET /api/v1/documentos/6acea24bbf5616d8602a1205/contenido` | 200 | 200 | PASA |
| DOC-09 | documentos | Borrar un documento propio. | `DELETE /api/v1/documentos/6acea24c114e5b7d09dc7612` | 204 | 204 | PASA |
| DOC-10 | documentos | Registro que no existe. | `GET /api/v1/documentos/ffffffffffffffffffffffff` | 404 | 404 | PASA |
| SEG-01 | seguimiento | Guardar el recorrido del repartidor en MongoDB. | `POST /api/v1/seguimiento/129/ubicaciones` | 201 | 201 | PASA |
| SEG-02 | seguimiento | Agregación en MongoDB sobre los puntos GPS. | `GET /api/v1/seguimiento/129/recorrido` | 200 | 200 | PASA |
| SEG-03 | seguimiento | El repartidor 2 no ve el rastro de la entrega del repartidor 1. | `GET /api/v1/seguimiento/129/recorrido` | 404 | 404 | PASA |
| SEG-04 | seguimiento | Todo endpoint protegido exige Authorization: Bearer. | `GET /api/v1/seguimiento/129/recorrido` | 401 | 401 | PASA |
| ENT-01 | entregas | Paradas abiertas del repartidor en el turno de hoy (RN25). | `GET /api/v1/entregas/mias?pagina=1&por_pagina=20` | 200 | 200 | PASA |
| ENT-02 | entregas | Cliente, domicilio y líneas. | `GET /api/v1/entregas/129` | 200 | 200 | PASA |
| ENT-03 | entregas | El repartidor 2 no ve la entrega del repartidor 1. | `GET /api/v1/entregas/129` | 404 | 404 | PASA |
| ENT-04 | entregas | Una entrega completa cobra el total (RN27). | `POST /api/v1/entregas/129/resultado` | 422 | 422 | PASA |
| ENT-05 | entregas | Registrar el resultado con evidencia y ubicación. | `POST /api/v1/entregas/129/resultado` | 201 | 201 | PASA |
| ENT-06 | entregas | Idempotencia: el cierre no se aplica dos veces. | `POST /api/v1/entregas/129/resultado` | 200 | 200 | PASA |
| ENT-07 | entregas | Conflicto: ya estaba cerrada con otra operación. | `POST /api/v1/entregas/129/resultado` | 409 | 409 | PASA |
| ENT-08 | entregas | El repartidor deja de ver el domicilio (RN26). | `GET /api/v1/entregas/129` | 404 | 404 | PASA |
| ENT-09 | entregas | Cada línea devuelta necesita motivo (RN28). | `POST /api/v1/entregas/130/resultado` | 422 | 422 | PASA |
| ENT-10 | entregas | Devolver al inventario lo que no se entregó. | `POST /api/v1/entregas/130/resultado` | 201 | 201 | PASA |
| ENT-11 | entregas | Consulta por pedido para el portal web. | `GET /api/v1/entregas?pedido_id=153` | 200 | 200 | PASA |
| PLA-01 | planeacion | Lista de ubicaciones candidatas. | `GET /api/v1/candidatos?pagina=1&por_pagina=3` | 200 | 200 | PASA |
| PLA-02 | planeacion | Alta con costo fijo calculado por PostgreSQL. | `POST /api/v1/candidatos` | 201 | 201 | PASA |
| PLA-03 | planeacion | No se repite la clave de un candidato. | `POST /api/v1/candidatos` | 409 | 409 | PASA |
| PLA-04 | planeacion | Cambiar la renta recalcula el costo fijo. | `PUT /api/v1/candidatos/16` | 200 | 200 | PASA |
| PLA-05 | planeacion | Viabilidad con los costos del candidato. | `POST /api/v1/candidatos/16/simular` | 200 | 200 | PASA |
| PLA-06 | planeacion | La decisión humana exige motivo. | `POST /api/v1/candidatos/16/decision` | 422 | 422 | PASA |
| PLA-07 | planeacion | Registrar la decisión con motivo. | `POST /api/v1/candidatos/16/decision` | 200 | 200 | PASA |
| PLA-08 | planeacion | Punto de equilibrio del caso de la retroalimentación. | `POST /api/v1/simulaciones` | 200 | 200 | PASA |
| PLA-09 | planeacion | Escenario compartido con el portal web. | `POST /api/v1/escenarios` | 201 | 201 | PASA |
| PLA-10 | planeacion | Escenario con supuestos y resultados. | `GET /api/v1/escenarios/1` | 200 | 200 | PASA |
| PLA-11 | planeacion | Agregación $group en MongoDB por decisión. | `GET /api/v1/simulaciones/resumen` | 200 | 200 | PASA |
| PLA-12 | planeacion | El auditor solo consulta (RN-E01). | `POST /api/v1/candidatos` | 403 | 403 | PASA |
| PLA-13 | planeacion | Sin simulacion.ejecutar. | `POST /api/v1/candidatos/16/simular` | 403 | 403 | PASA |
| PLA-14 | planeacion | Borrar un escenario. | `DELETE /api/v1/escenarios/1` | 204 | 204 | PASA |
| PLA-15 | planeacion | Baja lógica: se conserva su historia. | `DELETE /api/v1/candidatos/16` | 204 | 204 | PASA |
| PLA-16 | planeacion | Registro que no existe. | `GET /api/v1/candidatos/999999` | 404 | 404 | PASA |
| SAL-AUT | auth | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| SAL-USU | usuarios | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| SAL-PRO | productos | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| SAL-PED | pedidos | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| SAL-ENT | entregas | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| SAL-PLA | planeacion | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| SAL-DOC | documentos | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| SAL-ZON | zonas | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| SAL-MIC | microhubs | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| SAL-SEG | seguimiento | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| MON-01 | auth | Cada petición queda en MongoDB con su traza. | `GET /api/v1/auth/validar` | 200 | 200 | PASA |
| RAT-01 | zonas | Más de 240 solicitudes por minuto desde la misma IP. | `GET /api/v1/zonas` | 429 | 429 | PASA |

**Total:** 93 casos · 93 pasan · 0 fallan.