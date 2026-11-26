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
| DOC-07 | documentos | Documento en XML, sin contenido. | `GET /api/v1/documentos/6ad6c46d86a22ebc8612b586` | 200 | 200 | PASA |
| DOC-08 | documentos | Recuperar el archivo. | `GET /api/v1/documentos/6ad6c46d86a22ebc8612b586/contenido` | 200 | 200 | PASA |
| DOC-09 | documentos | Borrar un documento propio. | `DELETE /api/v1/documentos/6ad6c46d86a22ebc8612b590` | 204 | 204 | PASA |
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
| INV-01 | inventario | Existencia física, reservada y disponible de cada producto. | `GET /api/v1/inventario?por_pagina=5` | 200 | 200 | PASA |
| INV-02 | inventario | La app de escritorio recibe XML que cumple inventario.xsd. | `GET /api/v1/inventario?por_pagina=3` | 200 | 200 | PASA |
| INV-03 | inventario | Un filtro desconocido se rechaza. | `GET /api/v1/inventario?estado=inventado` | 400 | 400 | PASA |
| INV-04 | inventario | Ámbito por microhub del perfil operador. | `GET /api/v1/inventario?por_pagina=100` | 200 | 200 | PASA |
| INV-05 | inventario | No puede consultar el inventario de otro microhub. | `GET /api/v1/inventario?microhub_id=2` | 403 | 403 | PASA |
| INV-06 | inventario | Existencia, apartado y disponible de un producto en un microhub. | `GET /api/v1/inventario/1/6` | 200 | 200 | PASA |
| INV-07 | inventario | Suma al inventario y deja el movimiento con la referencia. | `POST /api/v1/inventario/movimientos` | 201 | 201 | PASA |
| INV-08 | inventario | Idempotencia: la misma entrada no se aplica dos veces. | `POST /api/v1/inventario/movimientos` | 200 | 200 | PASA |
| INV-09 | inventario | Un ajuste, merma o conteo necesita el motivo. | `POST /api/v1/inventario/movimientos` | 422 | 422 | PASA |
| INV-10 | inventario | Más de 25 unidades lo autoriza un administrador. | `POST /api/v1/inventario/movimientos` | 403 | 403 | PASA |
| INV-11 | inventario | El administrador sí puede. | `POST /api/v1/inventario/movimientos` | 201 | 201 | PASA |
| INV-12 | inventario | Resta del origen y suma al destino en una sola transacción. | `POST /api/v1/inventario/transferencias` | 201 | 201 | PASA |
| INV-13 | inventario | No se puede mandar lo que no hay. | `POST /api/v1/inventario/transferencias` | 409 | 409 | PASA |
| INV-14 | inventario | Una reserva resta de lo disponible sin tocar la existencia física. | `POST /api/v1/inventario/reservas` | 201 | 201 | PASA |
| INV-15 | inventario | Responde 409 si no alcanza. | `POST /api/v1/inventario/reservas` | 409 | 409 | PASA |
| INV-16 | inventario | Filtro por producto, estado y referencia. | `GET /api/v1/inventario/reservas?producto_id=8&estado=activa&referencia_id=evidencia-1c83ea` | 200 | 200 | PASA |
| INV-17 | inventario | Lo apartado vuelve a estar disponible. | `POST /api/v1/inventario/reservas/1/liberar` | 200 | 200 | PASA |
| INV-18 | inventario | Solo un administrador cambia el mínimo de un producto. | `PATCH /api/v1/inventario/1/9/minimo` | 200 | 200 | PASA |
| INV-23 | inventario | PUT es alias de PATCH: lo usa la app Android cuando la JVM no admite PATCH. | `PUT /api/v1/inventario/1/9/minimo` | 200 | 200 | PASA |
| INV-19 | inventario | Sin inventario.ajuste. | `PATCH /api/v1/inventario/1/9/minimo` | 403 | 403 | PASA |
| INV-20 | inventario | El trigger avisa del faltante al operador y al administrador. | `POST /api/v1/inventario/movimientos` | 201 | 201 | PASA |
| INV-21 | inventario | Productos agotados o bajo su mínimo, los más graves primero. | `GET /api/v1/inventario/alertas?microhub_id=1&por_pagina=100` | 200 | 200 | PASA |
| INV-22 | inventario | Bitácora del producto con sus referencias. | `GET /api/v1/inventario/movimientos?microhub_id=1&producto_id=6&tipo=recepcion` | 200 | 200 | PASA |
| NOT-01 | notificaciones | El administrador avisa a los operadores de un microhub. | `POST /api/v1/notificaciones` | 201 | 201 | PASA |
| NOT-02 | notificaciones | Sin notificaciones.crear. | `POST /api/v1/notificaciones` | 403 | 403 | PASA |
| NOT-03 | notificaciones | Un rol sin personas activas se rechaza. | `POST /api/v1/notificaciones` | 422 | 422 | PASA |
| NOT-04 | notificaciones | Los avisos de la persona, el más reciente primero. | `GET /api/v1/notificaciones?solo_no_leidas=true&por_pagina=20` | 200 | 200 | PASA |
| NOT-05 | notificaciones | Respuesta XML que cumple notificaciones.xsd. | `GET /api/v1/notificaciones?por_pagina=3` | 200 | 200 | PASA |
| NOT-06 | notificaciones | Conteo para la insignia de la app. | `GET /api/v1/notificaciones/conteo` | 200 | 200 | PASA |
| NOT-07 | notificaciones | El aviso queda leído. | `POST /api/v1/notificaciones/7/leer` | 200 | 200 | PASA |
| NOT-08 | notificaciones | Un aviso ajeno no se puede marcar. | `POST /api/v1/notificaciones/7/leer` | 404 | 404 | PASA |
| NOT-09 | notificaciones | Confirma la lectura de todos los pendientes. | `POST /api/v1/notificaciones/leer-todas` | 200 | 200 | PASA |
| NOT-10 | notificaciones | Qué tipos de aviso recibe la persona. | `GET /api/v1/notificaciones/preferencias` | 200 | 200 | PASA |
| NOT-11 | notificaciones | El operador deja de recibir avisos de inventario. | `PUT /api/v1/notificaciones/preferencias/inventario` | 200 | 200 | PASA |
| NOT-12 | notificaciones | Quien apagó el tipo no lo recibe y se cuenta como omitido. | `POST /api/v1/notificaciones` | 200 | 200 | PASA |
| NOT-13 | notificaciones | El tipo sistema siempre llega. | `PUT /api/v1/notificaciones/preferencias/sistema` | 409 | 409 | PASA |
| NOT-14 | notificaciones | Quita el aviso de la bandeja propia. | `DELETE /api/v1/notificaciones/7` | 204 | 204 | PASA |
| PRV-01 | proveedores | Lista con cobertura y calificación. | `GET /api/v1/proveedores?por_pagina=10` | 200 | 200 | PASA |
| PRV-02 | proveedores | Respuesta XML que cumple proveedores.xsd. | `GET /api/v1/proveedores?por_pagina=3` | 200 | 200 | PASA |
| PRV-03 | proveedores | El perfil cliente no tiene proveedores.ver. | `GET /api/v1/proveedores` | 403 | 403 | PASA |
| PRV-04 | proveedores | Con las zonas que cubre y su calificación. | `GET /api/v1/proveedores/2` | 200 | 200 | PASA |
| PRV-05 | proveedores | Alta con su cobertura por zonas. | `POST /api/v1/proveedores` | 201 | 201 | PASA |
| PRV-06 | proveedores | Dos proveedores no comparten clave. | `POST /api/v1/proveedores` | 409 | 409 | PASA |
| PRV-07 | proveedores | Validación con detalle por campo. | `POST /api/v1/proveedores` | 422 | 422 | PASA |
| PRV-08 | proveedores | Sin proveedores.editar. | `POST /api/v1/proveedores` | 403 | 403 | PASA |
| PRV-09 | proveedores | Cambia el plazo y la cobertura; la clave no se toca. | `PUT /api/v1/proveedores/7` | 200 | 200 | PASA |
| PRV-21 | proveedores | PATCH cambia solo los campos enviados; también acepta PUT. | `PATCH /api/v1/proveedores/7` | 200 | 200 | PASA |
| PRV-10 | proveedores | Alta del precio de compra de un producto. | `PUT /api/v1/proveedores/7/catalogo/6` | 200 | 200 | PASA |
| PRV-11 | proveedores | La llave foránea rechaza el producto. | `PUT /api/v1/proveedores/7/catalogo/999999` | 422 | 422 | PASA |
| PRV-12 | proveedores | Sus ofertas, con el nombre del producto. | `GET /api/v1/proveedores/7/catalogo` | 200 | 200 | PASA |
| PRV-13 | proveedores | Un operador califica puntualidad, calidad y precio. | `POST /api/v1/proveedores/7/evaluaciones` | 201 | 201 | PASA |
| PRV-14 | proveedores | Calificaciones recibidas y su promedio. | `GET /api/v1/proveedores/7/evaluaciones` | 200 | 200 | PASA |
| PRV-15 | proveedores | El auditor solo consulta. | `POST /api/v1/proveedores/7/evaluaciones` | 403 | 403 | PASA |
| PRV-16 | proveedores | De la más barata a la más cara. | `GET /api/v1/proveedores/ofertas?producto_id=6` | 200 | 200 | PASA |
| PRV-17 | proveedores | Una oferta, la más barata, por producto. | `GET /api/v1/proveedores/ofertas?producto_ids=6,7&mejor=true` | 200 | 200 | PASA |
| PRV-18 | proveedores | Falta producto_id o producto_ids. | `GET /api/v1/proveedores/ofertas` | 400 | 400 | PASA |
| PRV-19 | proveedores | Baja lógica: ya no aparece en las ofertas. | `DELETE /api/v1/proveedores/7` | 204 | 204 | PASA |
| PRV-20 | proveedores | El proveedor dado de baja no ofrece. | `GET /api/v1/proveedores/ofertas?producto_id=6` | 200 | 200 | PASA |
| PRE-01 | precios | Listas por zona y su vigencia. | `GET /api/v1/precios/listas` | 200 | 200 | PASA |
| PRE-02 | precios | Respuesta XML que cumple precios.xsd. | `GET /api/v1/precios/listas` | 200 | 200 | PASA |
| PRE-03 | precios | Sin precios.ver. | `GET /api/v1/precios/listas` | 403 | 403 | PASA |
| PRE-04 | precios | Lista de una zona con un precio y su costo. | `POST /api/v1/precios/listas` | 201 | 201 | PASA |
| PRE-05 | precios | Una zona no tiene dos listas vigentes a la vez. | `POST /api/v1/precios/listas` | 409 | 409 | PASA |
| PRE-06 | precios | Sube el precio de 50 a 52; el costo se conserva. | `PUT /api/v1/precios/listas/3/items/2` | 200 | 200 | PASA |
| PRE-07 | precios | Cada cambio de precio queda registrado por un trigger. | `GET /api/v1/precios/historial?lista_id=3&producto_id=2` | 200 | 200 | PASA |
| PRE-08 | precios | Precios, costos y margen de cada renglón. | `GET /api/v1/precios/listas/3` | 200 | 200 | PASA |
| PRE-09 | precios | Rige el precio de la lista de la zona. | `GET /api/v1/precios/vigente?producto_id=2&zona_id=3&fecha=2027-01-15` | 200 | 200 | PASA |
| PRE-10 | precios | Sin lista vigente rige el precio base del catálogo. | `GET /api/v1/precios/vigente?producto_id=2&zona_id=3&fecha=2026-10-19` | 200 | 200 | PASA |
| PRE-11 | precios | Precio base, lista, promoción y margen de un producto. | `GET /api/v1/precios/vigente?producto_id=1&zona_id=1` | 200 | 200 | PASA |
| PRE-12 | precios | Bebidas con 10 % de descuento. | `GET /api/v1/precios/vigente?producto_id=21&zona_id=1` | 200 | 200 | PASA |
| PRE-13 | precios | Precio final, descuento e importe de cada línea. | `POST /api/v1/precios/calcular` | 200 | 200 | PASA |
| PRE-14 | precios | Validación con detalle por línea. | `POST /api/v1/precios/calcular` | 422 | 422 | PASA |
| PRE-15 | precios | Un porcentaje mayor al tope de la configuración se rechaza. | `POST /api/v1/precios/promociones` | 422 | 422 | PASA |
| PRE-16 | precios | Descuento de $2 en un producto. | `POST /api/v1/precios/promociones` | 201 | 201 | PASA |
| PRE-17 | precios | Filtro por producto. | `GET /api/v1/precios/promociones?vigente=true&producto_id=1` | 200 | 200 | PASA |
| PRE-18 | precios | Baja lógica. | `DELETE /api/v1/precios/promociones/2` | 204 | 204 | PASA |
| PRE-19 | precios | Renglones con costo, del margen más bajo al más alto. | `GET /api/v1/precios/margenes?por_pagina=5` | 200 | 200 | PASA |
| PRE-20 | precios | Qué pasa con ingreso y margen si el precio sube o baja. | `GET /api/v1/precios/sensibilidad?producto_id=1&zona_id=1&volumen_base=100&elasticidad=-1.2` | 200 | 200 | PASA |
| PRE-21 | precios | La elasticidad va de −10 a 0. | `GET /api/v1/precios/sensibilidad?producto_id=1&elasticidad=1` | 400 | 400 | PASA |
| ABA-01 | abastecimiento | Productos bajo su mínimo, con la mejor oferta. | `GET /api/v1/abastecimiento/necesidades?por_pagina=100` | 200 | 200 | PASA |
| ABA-02 | abastecimiento | El administrador debe elegir un microhub. | `GET /api/v1/abastecimiento/necesidades` | 400 | 400 | PASA |
| ABA-03 | abastecimiento | El operador pide reposición de su microhub. | `POST /api/v1/abastecimiento/solicitudes` | 201 | 201 | PASA |
| ABA-04 | abastecimiento | El operador solo trabaja con el suyo. | `POST /api/v1/abastecimiento/solicitudes` | 403 | 403 | PASA |
| ABA-05 | abastecimiento | Un producto aparece una sola vez. | `POST /api/v1/abastecimiento/solicitudes` | 422 | 422 | PASA |
| ABA-06 | abastecimiento | Otro operador no la ve. | `GET /api/v1/abastecimiento/solicitudes/1` | 404 | 404 | PASA |
| ABA-07 | abastecimiento | Solo el administrador decide. | `POST /api/v1/abastecimiento/solicitudes/1/decision` | 403 | 403 | PASA |
| ABA-08 | abastecimiento | Rechazar exige el motivo. | `POST /api/v1/abastecimiento/solicitudes/1/decision` | 422 | 422 | PASA |
| ABA-09 | abastecimiento | Solo se ordena una solicitud aprobada. | `POST /api/v1/abastecimiento/solicitudes/1/ordenar` | 409 | 409 | PASA |
| ABA-10 | abastecimiento | El administrador aprueba y quien pidió recibe el aviso. | `POST /api/v1/abastecimiento/solicitudes/1/decision` | 200 | 200 | PASA |
| ABA-11 | abastecimiento | Cada línea va al proveedor indicado; el total es piezas × precio de compra. | `POST /api/v1/abastecimiento/solicitudes/1/ordenar` | 201 | 201 | PASA |
| ABA-12 | abastecimiento | La solicitud ya quedó ordenada. | `POST /api/v1/abastecimiento/solicitudes/1/ordenar` | 409 | 409 | PASA |
| ABA-13 | abastecimiento | La mercancía que llegó entra al inventario. | `POST /api/v1/abastecimiento/ordenes/1/recepcion` | 201 | 201 | PASA |
| ABA-14 | abastecimiento | No entra dos veces al inventario. | `POST /api/v1/abastecimiento/ordenes/1/recepcion` | 201 | 201 | PASA |
| ABA-15 | abastecimiento | Solo falta lo que no ha llegado. | `POST /api/v1/abastecimiento/ordenes/1/recepcion` | 422 | 422 | PASA |
| ABA-16 | abastecimiento | Solo se cancela una orden sin recepciones. | `POST /api/v1/abastecimiento/ordenes/1/cancelar` | 409 | 409 | PASA |
| ABA-17 | abastecimiento | Llega el resto: la orden queda recibida y avisa. | `POST /api/v1/abastecimiento/ordenes/1/recepcion` | 201 | 201 | PASA |
| ABA-18 | abastecimiento | Una orden recibida no admite más mercancía. | `POST /api/v1/abastecimiento/ordenes/1/recepcion` | 409 | 409 | PASA |
| ABA-19 | abastecimiento | Con lo recibido de cada línea. | `GET /api/v1/abastecimiento/ordenes/1` | 200 | 200 | PASA |
| ABA-20 | abastecimiento | Respuesta XML que cumple abastecimiento.xsd. | `GET /api/v1/abastecimiento/ordenes?estado=recibida` | 200 | 200 | PASA |
| ABA-21 | abastecimiento | Solicitudes y órdenes por estado. | `GET /api/v1/abastecimiento/seguimiento` | 200 | 200 | PASA |
| ABA-22 | abastecimiento | Cancelar una orden es del administrador. | `POST /api/v1/abastecimiento/ordenes/2/cancelar` | 403 | 403 | PASA |
| ABA-23 | abastecimiento | Una orden sin recepciones se puede cancelar con motivo. | `POST /api/v1/abastecimiento/ordenes/2/cancelar` | 200 | 200 | PASA |
| ABA-24 | abastecimiento | No recibe mercancía. | `POST /api/v1/abastecimiento/ordenes/2/recepcion` | 409 | 409 | PASA |
| ABA-25 | abastecimiento | Respuesta XML que cumple abastecimiento.xsd. | `GET /api/v1/abastecimiento/solicitudes?por_pagina=3` | 200 | 200 | PASA |
| ABA-26 | abastecimiento | El auditor ve las solicitudes sin poder crear. | `GET /api/v1/abastecimiento/solicitudes` | 200 | 200 | PASA |
| ABA-27 | abastecimiento | El cliente no tiene abastecimiento.ver. | `GET /api/v1/abastecimiento/solicitudes` | 403 | 403 | PASA |
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
| SAL-INV | inventario | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| SAL-PRE | precios | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| SAL-PRO | proveedores | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| SAL-ABA | abastecimiento | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| SAL-NOT | notificaciones | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| MON-01 | auth | Cada petición queda en MongoDB con su traza. | `GET /api/v1/auth/validar` | 200 | 200 | PASA |
| RAT-01 | zonas | Más de 240 solicitudes por minuto desde la misma IP. | `GET /api/v1/zonas` | 429 | 429 | PASA |

**Total:** 204 casos · 204 pasan · 0 fallan.