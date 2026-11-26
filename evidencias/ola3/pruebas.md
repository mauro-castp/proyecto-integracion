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
| PED-03 | pedidos | Cliente, domicilio y líneas del pedido. | `GET /api/v1/pedidos/534` | 200 | 200 | PASA |
| PED-04 | pedidos | Cambios de estado con usuario y fecha. | `GET /api/v1/pedidos/534/historial` | 200 | 200 | PASA |
| PED-05 | pedidos | Un estado que no existe se rechaza. | `GET /api/v1/pedidos?estado=inventado` | 400 | 400 | PASA |
| PED-06 | pedidos | El operador del MH-01 no ve pedidos de otro microhub (RN22). | `GET /api/v1/pedidos/1` | 404 | 404 | PASA |
| PED-07 | pedidos | Los cierres de entrega solo se registran en el servicio de entregas. | `POST /api/v1/pedidos/534/estado` | 409 | 409 | PASA |
| PED-08 | pedidos | Un pedido entregado no puede regresar a preparación. | `PATCH /api/v1/pedidos/2/estado` | 422 | 422 | PASA |
| DOC-01 | documentos | Guardar la foto en MongoDB ligada a la entrega. | `POST /api/v1/documentos` | 201 | 201 | PASA |
| DOC-02 | documentos | Evidencia para el cierre parcial. | `POST /api/v1/documentos` | 201 | 201 | PASA |
| DOC-03 | documentos | Un PDF declarado como JPEG se rechaza por su firma. | `POST /api/v1/documentos` | 422 | 422 | PASA |
| DOC-04 | documentos | Un repartidor no adjunta a entregas de otro. | `POST /api/v1/documentos` | 403 | 403 | PASA |
| DOC-05 | documentos | Documento que después se elimina. | `POST /api/v1/documentos` | 201 | 201 | PASA |
| DOC-06 | documentos | Filtro por referencia. | `GET /api/v1/documentos?referencia_tipo=entrega&referencia_id=277` | 200 | 200 | PASA |
| DOC-07 | documentos | Documento en XML, sin contenido. | `GET /api/v1/documentos/6b089453cc73360fa2e7f17a` | 200 | 200 | PASA |
| DOC-08 | documentos | Recuperar el archivo. | `GET /api/v1/documentos/6b089453cc73360fa2e7f17a/contenido` | 200 | 200 | PASA |
| DOC-09 | documentos | Borrar un documento propio. | `DELETE /api/v1/documentos/6b089454cc73360fa2e7f184` | 204 | 204 | PASA |
| DOC-10 | documentos | Registro que no existe. | `GET /api/v1/documentos/ffffffffffffffffffffffff` | 404 | 404 | PASA |
| SEG-01 | seguimiento | Guardar el recorrido del repartidor en MongoDB. | `POST /api/v1/seguimiento/277/ubicaciones` | 201 | 201 | PASA |
| SEG-02 | seguimiento | Agregación en MongoDB sobre los puntos GPS. | `GET /api/v1/seguimiento/277/recorrido` | 200 | 200 | PASA |
| SEG-03 | seguimiento | El repartidor 2 no ve el rastro de la entrega del repartidor 1. | `GET /api/v1/seguimiento/277/recorrido` | 404 | 404 | PASA |
| SEG-04 | seguimiento | Todo endpoint protegido exige Authorization: Bearer. | `GET /api/v1/seguimiento/277/recorrido` | 401 | 401 | PASA |
| ENT-01 | entregas | Paradas abiertas del repartidor en el turno de hoy (RN25). | `GET /api/v1/entregas/mias?pagina=1&por_pagina=20` | 200 | 200 | PASA |
| ENT-02 | entregas | Cliente, domicilio y líneas. | `GET /api/v1/entregas/277` | 200 | 200 | PASA |
| ENT-03 | entregas | El repartidor 2 no ve la entrega del repartidor 1. | `GET /api/v1/entregas/277` | 404 | 404 | PASA |
| ENT-04 | entregas | Una entrega completa cobra el total (RN27). | `POST /api/v1/entregas/277/resultado` | 422 | 422 | PASA |
| ENT-05 | entregas | Registrar el resultado con evidencia y ubicación. | `POST /api/v1/entregas/277/resultado` | 201 | 201 | PASA |
| ENT-06 | entregas | Idempotencia: el cierre no se aplica dos veces. | `POST /api/v1/entregas/277/resultado` | 200 | 200 | PASA |
| ENT-07 | entregas | Conflicto: ya estaba cerrada con otra operación. | `POST /api/v1/entregas/277/resultado` | 409 | 409 | PASA |
| ENT-08 | entregas | El repartidor deja de ver el domicilio (RN26). | `GET /api/v1/entregas/277` | 404 | 404 | PASA |
| ENT-09 | entregas | Cada línea devuelta necesita motivo (RN28). | `POST /api/v1/entregas/278/resultado` | 422 | 422 | PASA |
| ENT-10 | entregas | Devolver al inventario lo que no se entregó. | `POST /api/v1/entregas/278/resultado` | 201 | 201 | PASA |
| ENT-11 | entregas | Consulta por pedido para el portal web. | `GET /api/v1/entregas?pedido_id=542` | 200 | 200 | PASA |
| PLA-01 | planeacion | Lista de ubicaciones candidatas. | `GET /api/v1/candidatos?pagina=1&por_pagina=3` | 200 | 200 | PASA |
| PLA-02 | planeacion | Alta con costo fijo calculado por PostgreSQL. | `POST /api/v1/candidatos` | 201 | 201 | PASA |
| PLA-03 | planeacion | No se repite la clave de un candidato. | `POST /api/v1/candidatos` | 409 | 409 | PASA |
| PLA-04 | planeacion | Cambiar la renta recalcula el costo fijo. | `PUT /api/v1/candidatos/139` | 200 | 200 | PASA |
| PLA-05 | planeacion | Viabilidad con los costos del candidato. | `POST /api/v1/candidatos/139/simular` | 200 | 200 | PASA |
| PLA-06 | planeacion | La decisión humana exige motivo. | `POST /api/v1/candidatos/139/decision` | 422 | 422 | PASA |
| PLA-07 | planeacion | Registrar la decisión con motivo. | `POST /api/v1/candidatos/139/decision` | 200 | 200 | PASA |
| PLA-08 | planeacion | Punto de equilibrio del caso de la retroalimentación. | `POST /api/v1/simulaciones` | 200 | 200 | PASA |
| PLA-09 | planeacion | Escenario compartido con el portal web. | `POST /api/v1/escenarios` | 201 | 201 | PASA |
| PLA-10 | planeacion | Escenario con supuestos y resultados. | `GET /api/v1/escenarios/24` | 200 | 200 | PASA |
| PLA-11 | planeacion | Agregación $group en MongoDB por decisión. | `GET /api/v1/simulaciones/resumen` | 200 | 200 | PASA |
| PLA-12 | planeacion | El auditor solo consulta (RN-E01). | `POST /api/v1/candidatos` | 403 | 403 | PASA |
| PLA-13 | planeacion | Sin simulacion.ejecutar. | `POST /api/v1/candidatos/139/simular` | 403 | 403 | PASA |
| PLA-14 | planeacion | Borrar un escenario. | `DELETE /api/v1/escenarios/24` | 204 | 204 | PASA |
| PLA-15 | planeacion | Baja lógica: se conserva su historia. | `DELETE /api/v1/candidatos/139` | 204 | 204 | PASA |
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
| INV-16 | inventario | Filtro por producto, estado y referencia. | `GET /api/v1/inventario/reservas?producto_id=8&estado=activa&referencia_id=evidencia-fa7fde` | 200 | 200 | PASA |
| INV-17 | inventario | Lo apartado vuelve a estar disponible. | `POST /api/v1/inventario/reservas/18/liberar` | 200 | 200 | PASA |
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
| NOT-07 | notificaciones | El aviso queda leído. | `POST /api/v1/notificaciones/751/leer` | 200 | 200 | PASA |
| NOT-08 | notificaciones | Un aviso ajeno no se puede marcar. | `POST /api/v1/notificaciones/751/leer` | 404 | 404 | PASA |
| NOT-09 | notificaciones | Confirma la lectura de todos los pendientes. | `POST /api/v1/notificaciones/leer-todas` | 200 | 200 | PASA |
| NOT-10 | notificaciones | Qué tipos de aviso recibe la persona. | `GET /api/v1/notificaciones/preferencias` | 200 | 200 | PASA |
| NOT-11 | notificaciones | El operador deja de recibir avisos de inventario. | `PUT /api/v1/notificaciones/preferencias/inventario` | 200 | 200 | PASA |
| NOT-12 | notificaciones | Quien apagó el tipo no lo recibe y se cuenta como omitido. | `POST /api/v1/notificaciones` | 200 | 200 | PASA |
| NOT-13 | notificaciones | El tipo sistema siempre llega. | `PUT /api/v1/notificaciones/preferencias/sistema` | 409 | 409 | PASA |
| NOT-14 | notificaciones | Quita el aviso de la bandeja propia. | `DELETE /api/v1/notificaciones/751` | 204 | 204 | PASA |
| PRV-01 | proveedores | Lista con cobertura y calificación. | `GET /api/v1/proveedores?por_pagina=10` | 200 | 200 | PASA |
| PRV-02 | proveedores | Respuesta XML que cumple proveedores.xsd. | `GET /api/v1/proveedores?por_pagina=3` | 200 | 200 | PASA |
| PRV-03 | proveedores | El perfil cliente no tiene proveedores.ver. | `GET /api/v1/proveedores` | 403 | 403 | PASA |
| PRV-04 | proveedores | Con las zonas que cubre y su calificación. | `GET /api/v1/proveedores/2` | 200 | 200 | PASA |
| PRV-05 | proveedores | Alta con su cobertura por zonas. | `POST /api/v1/proveedores` | 201 | 201 | PASA |
| PRV-06 | proveedores | Dos proveedores no comparten clave. | `POST /api/v1/proveedores` | 409 | 409 | PASA |
| PRV-07 | proveedores | Validación con detalle por campo. | `POST /api/v1/proveedores` | 422 | 422 | PASA |
| PRV-08 | proveedores | Sin proveedores.editar. | `POST /api/v1/proveedores` | 403 | 403 | PASA |
| PRV-09 | proveedores | Cambia el plazo y la cobertura; la clave no se toca. | `PUT /api/v1/proveedores/72` | 200 | 200 | PASA |
| PRV-21 | proveedores | PATCH cambia solo los campos enviados; también acepta PUT. | `PATCH /api/v1/proveedores/72` | 200 | 200 | PASA |
| PRV-10 | proveedores | Alta del precio de compra de un producto. | `PUT /api/v1/proveedores/72/catalogo/6` | 200 | 200 | PASA |
| PRV-11 | proveedores | La llave foránea rechaza el producto. | `PUT /api/v1/proveedores/72/catalogo/999999` | 422 | 422 | PASA |
| PRV-12 | proveedores | Sus ofertas, con el nombre del producto. | `GET /api/v1/proveedores/72/catalogo` | 200 | 200 | PASA |
| PRV-13 | proveedores | Un operador califica puntualidad, calidad y precio. | `POST /api/v1/proveedores/72/evaluaciones` | 201 | 201 | PASA |
| PRV-14 | proveedores | Calificaciones recibidas y su promedio. | `GET /api/v1/proveedores/72/evaluaciones` | 200 | 200 | PASA |
| PRV-15 | proveedores | El auditor solo consulta. | `POST /api/v1/proveedores/72/evaluaciones` | 403 | 403 | PASA |
| PRV-16 | proveedores | De la más barata a la más cara. | `GET /api/v1/proveedores/ofertas?producto_id=6` | 200 | 200 | PASA |
| PRV-17 | proveedores | Una oferta, la más barata, por producto. | `GET /api/v1/proveedores/ofertas?producto_ids=6,7&mejor=true` | 200 | 200 | PASA |
| PRV-18 | proveedores | Falta producto_id o producto_ids. | `GET /api/v1/proveedores/ofertas` | 400 | 400 | PASA |
| PRV-19 | proveedores | Baja lógica: ya no aparece en las ofertas. | `DELETE /api/v1/proveedores/72` | 204 | 204 | PASA |
| PRV-20 | proveedores | El proveedor dado de baja no ofrece. | `GET /api/v1/proveedores/ofertas?producto_id=6` | 200 | 200 | PASA |
| PRE-01 | precios | Listas por zona y su vigencia. | `GET /api/v1/precios/listas` | 200 | 200 | PASA |
| PRE-02 | precios | Respuesta XML que cumple precios.xsd. | `GET /api/v1/precios/listas` | 200 | 200 | PASA |
| PRE-03 | precios | Sin precios.ver. | `GET /api/v1/precios/listas` | 403 | 403 | PASA |
| PRE-04 | precios | Lista de una zona con un precio y su costo. | `POST /api/v1/precios/listas` | 201 | 201 | PASA |
| PRE-05 | precios | Una zona no tiene dos listas vigentes a la vez. | `POST /api/v1/precios/listas` | 409 | 409 | PASA |
| PRE-06 | precios | Sube el precio de 50 a 52; el costo se conserva. | `PUT /api/v1/precios/listas/35/items/2` | 200 | 200 | PASA |
| PRE-07 | precios | Cada cambio de precio queda registrado por un trigger. | `GET /api/v1/precios/historial?lista_id=35&producto_id=2` | 200 | 200 | PASA |
| PRE-08 | precios | Precios, costos y margen de cada renglón. | `GET /api/v1/precios/listas/35` | 200 | 200 | PASA |
| PRE-09 | precios | Rige el precio de la lista de la zona. | `GET /api/v1/precios/vigente?producto_id=2&zona_id=3&fecha=2027-01-15` | 200 | 200 | PASA |
| PRE-10 | precios | Sin lista vigente rige el precio base del catálogo. | `GET /api/v1/precios/vigente?producto_id=2&zona_id=3&fecha=2026-10-19` | 200 | 200 | PASA |
| PRE-11 | precios | Precio base, lista, promoción y margen de un producto. | `GET /api/v1/precios/vigente?producto_id=1&zona_id=1` | 200 | 200 | PASA |
| PRE-12 | precios | Bebidas con 10 % de descuento. | `GET /api/v1/precios/vigente?producto_id=21&zona_id=1` | 200 | 200 | PASA |
| PRE-13 | precios | Precio final, descuento e importe de cada línea. | `POST /api/v1/precios/calcular` | 200 | 200 | PASA |
| PRE-14 | precios | Validación con detalle por línea. | `POST /api/v1/precios/calcular` | 422 | 422 | PASA |
| PRE-15 | precios | Un porcentaje mayor al tope de la configuración se rechaza. | `POST /api/v1/precios/promociones` | 422 | 422 | PASA |
| PRE-16 | precios | Descuento de $2 en un producto. | `POST /api/v1/precios/promociones` | 201 | 201 | PASA |
| PRE-17 | precios | Filtro por producto. | `GET /api/v1/precios/promociones?vigente=true&producto_id=1` | 200 | 200 | PASA |
| PRE-18 | precios | Baja lógica. | `DELETE /api/v1/precios/promociones/15` | 204 | 204 | PASA |
| PRE-19 | precios | Renglones con costo, del margen más bajo al más alto. | `GET /api/v1/precios/margenes?por_pagina=5` | 200 | 200 | PASA |
| PRE-20 | precios | Qué pasa con ingreso y margen si el precio sube o baja. | `GET /api/v1/precios/sensibilidad?producto_id=1&zona_id=1&volumen_base=100&elasticidad=-1.2` | 200 | 200 | PASA |
| PRE-21 | precios | La elasticidad va de −10 a 0. | `GET /api/v1/precios/sensibilidad?producto_id=1&elasticidad=1` | 400 | 400 | PASA |
| ABA-01 | abastecimiento | Productos bajo su mínimo, con la mejor oferta. | `GET /api/v1/abastecimiento/necesidades?por_pagina=100` | 200 | 200 | PASA |
| ABA-02 | abastecimiento | El administrador debe elegir un microhub. | `GET /api/v1/abastecimiento/necesidades` | 400 | 400 | PASA |
| ABA-03 | abastecimiento | El operador pide reposición de su microhub. | `POST /api/v1/abastecimiento/solicitudes` | 201 | 201 | PASA |
| ABA-04 | abastecimiento | El operador solo trabaja con el suyo. | `POST /api/v1/abastecimiento/solicitudes` | 403 | 403 | PASA |
| ABA-05 | abastecimiento | Un producto aparece una sola vez. | `POST /api/v1/abastecimiento/solicitudes` | 422 | 422 | PASA |
| ABA-06 | abastecimiento | Otro operador no la ve. | `GET /api/v1/abastecimiento/solicitudes/53` | 404 | 404 | PASA |
| ABA-07 | abastecimiento | Solo el administrador decide. | `POST /api/v1/abastecimiento/solicitudes/53/decision` | 403 | 403 | PASA |
| ABA-08 | abastecimiento | Rechazar exige el motivo. | `POST /api/v1/abastecimiento/solicitudes/53/decision` | 422 | 422 | PASA |
| ABA-09 | abastecimiento | Solo se ordena una solicitud aprobada. | `POST /api/v1/abastecimiento/solicitudes/53/ordenar` | 409 | 409 | PASA |
| ABA-10 | abastecimiento | El administrador aprueba y quien pidió recibe el aviso. | `POST /api/v1/abastecimiento/solicitudes/53/decision` | 200 | 200 | PASA |
| ABA-11 | abastecimiento | Cada línea va al proveedor indicado; el total es piezas × precio de compra. | `POST /api/v1/abastecimiento/solicitudes/53/ordenar` | 201 | 201 | PASA |
| ABA-12 | abastecimiento | La solicitud ya quedó ordenada. | `POST /api/v1/abastecimiento/solicitudes/53/ordenar` | 409 | 409 | PASA |
| ABA-13 | abastecimiento | La mercancía que llegó entra al inventario. | `POST /api/v1/abastecimiento/ordenes/33/recepcion` | 201 | 201 | PASA |
| ABA-14 | abastecimiento | No entra dos veces al inventario. | `POST /api/v1/abastecimiento/ordenes/33/recepcion` | 201 | 201 | PASA |
| ABA-15 | abastecimiento | Solo falta lo que no ha llegado. | `POST /api/v1/abastecimiento/ordenes/33/recepcion` | 422 | 422 | PASA |
| ABA-16 | abastecimiento | Solo se cancela una orden sin recepciones. | `POST /api/v1/abastecimiento/ordenes/33/cancelar` | 409 | 409 | PASA |
| ABA-17 | abastecimiento | Llega el resto: la orden queda recibida y avisa. | `POST /api/v1/abastecimiento/ordenes/33/recepcion` | 201 | 201 | PASA |
| ABA-18 | abastecimiento | Una orden recibida no admite más mercancía. | `POST /api/v1/abastecimiento/ordenes/33/recepcion` | 409 | 409 | PASA |
| ABA-19 | abastecimiento | Con lo recibido de cada línea. | `GET /api/v1/abastecimiento/ordenes/33` | 200 | 200 | PASA |
| ABA-20 | abastecimiento | Respuesta XML que cumple abastecimiento.xsd. | `GET /api/v1/abastecimiento/ordenes?estado=recibida` | 200 | 200 | PASA |
| ABA-21 | abastecimiento | Solicitudes y órdenes por estado. | `GET /api/v1/abastecimiento/seguimiento` | 200 | 200 | PASA |
| ABA-22 | abastecimiento | Cancelar una orden es del administrador. | `POST /api/v1/abastecimiento/ordenes/34/cancelar` | 403 | 403 | PASA |
| ABA-23 | abastecimiento | Una orden sin recepciones se puede cancelar con motivo. | `POST /api/v1/abastecimiento/ordenes/34/cancelar` | 200 | 200 | PASA |
| ABA-24 | abastecimiento | No recibe mercancía. | `POST /api/v1/abastecimiento/ordenes/34/recepcion` | 409 | 409 | PASA |
| ABA-25 | abastecimiento | Respuesta XML que cumple abastecimiento.xsd. | `GET /api/v1/abastecimiento/solicitudes?por_pagina=3` | 200 | 200 | PASA |
| ABA-26 | abastecimiento | El auditor ve las solicitudes sin poder crear. | `GET /api/v1/abastecimiento/solicitudes` | 200 | 200 | PASA |
| ABA-27 | abastecimiento | El cliente no tiene abastecimiento.ver. | `GET /api/v1/abastecimiento/solicitudes` | 403 | 403 | PASA |
| ALI-01 | pedidos | Lo consume el servicio de demanda: pedidos, unidades, venta y clientes por día y zona. | `GET /api/v1/pedidos/resumen?por_pagina=5` | 200 | 200 | PASA |
| ALI-02 | pedidos | Un valor desconocido de «agrupar» se rechaza. | `GET /api/v1/pedidos/resumen?agrupar=otra` | 400 | 400 | PASA |
| ALI-03 | pedidos | Lo consume surtido: unidades y venta de cada producto, sin cancelados. | `GET /api/v1/pedidos/ventas?por_pagina=5` | 200 | 200 | PASA |
| ALI-04 | pedidos | El microhub es obligatorio. | `GET /api/v1/pedidos/listos` | 400 | 400 | PASA |
| ALI-05 | pedidos | Con las coordenadas de entrega: lo que rutas agrupa y ordena. | `GET /api/v1/pedidos/listos?microhub_id=1` | 200 | 200 | PASA |
| ALI-06 | entregas | Con las entregas que tienen abiertas hoy; lo consume rutas. | `GET /api/v1/entregas/repartidores` | 200 | 200 | PASA |
| ALI-07 | inventario | Veces que una salida dejó el producto en cero y si hoy está agotado; lo consume surtido. | `GET /api/v1/inventario/quiebres?microhub_id=1&por_pagina=5` | 200 | 200 | PASA |
| ALI-08 | inventario | dias debe estar entre 1 y 365. | `GET /api/v1/inventario/quiebres?dias=0` | 400 | 400 | PASA |
| DEM-01 | demanda | Pedidos por día, zona y categoría, con la fuente de cada dato. | `GET /api/v1/demanda/observaciones?nivel=total&por_pagina=5` | 200 | 200 | PASA |
| DEM-02 | demanda | Respuesta XML que cumple demanda.xsd. | `GET /api/v1/demanda/observaciones?por_pagina=3` | 200 | 200 | PASA |
| DEM-03 | demanda | Un filtro desconocido se rechaza. | `GET /api/v1/demanda/observaciones?fuente=inventada` | 400 | 400 | PASA |
| DEM-04 | demanda | Sin demanda.ver. | `GET /api/v1/demanda/observaciones` | 403 | 403 | PASA |
| DEM-05 | demanda | Pedidos, ticket promedio, pedidos por cliente y demanda no atendida. | `GET /api/v1/demanda/resumen` | 200 | 200 | PASA |
| DEM-06 | demanda | Índice de cada día de la semana y venta por categoría. | `GET /api/v1/demanda/patrones` | 200 | 200 | PASA |
| DEM-07 | demanda | 14 días con mínimo y máximo; la banda sale del error del propio ajuste. | `GET /api/v1/demanda/proyeccion` | 200 | 200 | PASA |
| DEM-08 | demanda | El otro método: nivel de los últimos 7 días, sin tendencia. | `GET /api/v1/demanda/proyeccion?metodo=promedio_movil&horizonte=7` | 200 | 200 | PASA |
| DEM-09 | demanda | Solo existen dos métodos. | `GET /api/v1/demanda/proyeccion?metodo=magico` | 400 | 400 | PASA |
| DEM-10 | demanda | Se ocultan los últimos 7 días, se proyectan y se miden el error y el sesgo. | `GET /api/v1/demanda/comparacion` | 200 | 200 | PASA |
| DEM-11 | demanda | Hogares × penetración × pedidos por hogar, contra lo observado. | `GET /api/v1/demanda/potencial` | 200 | 200 | PASA |
| DEM-12 | demanda | El cálculo no cambia la configuración: solo la consulta. | `GET /api/v1/demanda/potencial?penetracion=0.2` | 200 | 200 | PASA |
| DEM-13 | demanda | Traer la demanda real exige demanda.editar. | `POST /api/v1/demanda/sincronizacion` | 403 | 403 | PASA |
| DEM-14 | demanda | Lo sintético del rango se reemplaza por lo real. | `POST /api/v1/demanda/sincronizacion` | 201 | 201 | PASA |
| DEM-15 | demanda | desde no puede ser posterior a hasta. | `POST /api/v1/demanda/sincronizacion` | 422 | 422 | PASA |
| DEM-16 | demanda | El cuerpo XML se valida contra demanda.xsd antes de procesarse. | `POST /api/v1/demanda/sincronizacion` | 201 | 201 | PASA |
| DEM-17 | demanda | Valor, origen (medido, supuesto o normativo), justificación y cómo calibrarlo. | `GET /api/v1/demanda/supuestos` | 200 | 200 | PASA |
| COB-01 | cobertura | Qué microhubs cubren cada zona, a cuántos minutos y si hay traslape. | `GET /api/v1/cobertura/zonas` | 200 | 200 | PASA |
| COB-02 | cobertura | Porcentaje de zonas y hogares cubiertos, tiempo promedio y zonas traslapadas. | `GET /api/v1/cobertura/resumen` | 200 | 200 | PASA |
| COB-03 | cobertura | Respuesta XML que cumple cobertura.xsd. | `GET /api/v1/cobertura/resumen` | 200 | 200 | PASA |
| COB-04 | cobertura | Qué microhubs lo cubren y a qué distancia. | `GET /api/v1/cobertura/punto?latitud=25.748&longitud=-100.364` | 200 | 200 | PASA |
| COB-05 | cobertura | Nadie lo cubre; se dice cuál es la zona más cercana. | `GET /api/v1/cobertura/punto?latitud=26.9&longitud=-101.4` | 200 | 200 | PASA |
| COB-06 | cobertura | La latitud debe estar entre 20 y 33. | `GET /api/v1/cobertura/punto?latitud=95&longitud=10` | 400 | 400 | PASA |
| COB-07 | cobertura | Cada candidata de planeación frente a la red actual. | `GET /api/v1/cobertura/candidatos` | 200 | 200 | PASA |
| COB-08 | cobertura | Zonas nuevas, hogares nuevos, traslape y costo de la última milla. | `POST /api/v1/cobertura/evaluaciones` | 200 | 200 | PASA |
| COB-09 | cobertura | Guardar exige planeacion.editar. | `POST /api/v1/cobertura/evaluaciones` | 403 | 403 | PASA |
| COB-10 | cobertura | Queda en cobertura_evaluacion con su resultado completo. | `POST /api/v1/cobertura/evaluaciones` | 201 | 201 | PASA |
| COB-17 | cobertura | Lista de lo que el planeador ha evaluado. | `GET /api/v1/cobertura/evaluaciones?por_pagina=5` | 200 | 200 | PASA |
| COB-18 | cobertura | Con el resultado completo con que se guardó. | `GET /api/v1/cobertura/evaluaciones/22` | 200 | 200 | PASA |
| COB-11 | cobertura | Todo se traslapa: se avisa de canibalización. | `POST /api/v1/cobertura/evaluaciones` | 200 | 200 | PASA |
| COB-12 | cobertura | Hace falta un candidato o una coordenada. | `POST /api/v1/cobertura/evaluaciones` | 422 | 422 | PASA |
| COB-13 | cobertura | Cuánto cubre la red con otros radios y otro factor de calle. | `GET /api/v1/cobertura/escenarios?radios=0.5,1,1.5,2&rodeos=1.2,1.5` | 200 | 200 | PASA |
| COB-14 | cobertura | La población de cada zona se corrige con el dato de INEGI; hay que decir de dónde sale. | `PUT /api/v1/cobertura/zonas/1/poblacion` | 200 | 200 | PASA |
| COB-15 | cobertura | Es del planeador. | `PUT /api/v1/cobertura/zonas/1/poblacion` | 403 | 403 | PASA |
| COB-16 | cobertura | Rodeo, velocidad, tiempo de servicio, promesa de entrega y tamaño del hogar. | `GET /api/v1/cobertura/supuestos` | 200 | 200 | PASA |
| CAP-01 | capacidad | Operadores, repartidores y tope de espacio. | `GET /api/v1/capacidad/recursos` | 200 | 200 | PASA |
| CAP-02 | capacidad | Solo ve los recursos del suyo. | `GET /api/v1/capacidad/recursos/2` | 403 | 403 | PASA |
| CAP-03 | capacidad | Capacidad por etapa, utilización, cuello de botella y personal requerido. | `GET /api/v1/capacidad/microhubs/1?carga_dia=60` | 200 | 200 | PASA |
| CAP-13 | capacidad | Una fila por microhub con su utilización y su nivel; el operador solo ve el suyo. | `GET /api/v1/capacidad/microhubs?carga_dia=40&por_pagina=100` | 200 | 200 | PASA |
| CAP-04 | capacidad | Con 95 % de la capacidad el nivel es de riesgo (umbral 85 %). | `GET /api/v1/capacidad/microhubs/1?carga_dia=140` | 200 | 200 | PASA |
| CAP-05 | capacidad | horas va de 1 a 24. | `GET /api/v1/capacidad/microhubs/1?horas=99` | 400 | 400 | PASA |
| CAP-06 | capacidad | Respuesta XML que cumple capacidad.xsd. | `GET /api/v1/capacidad/microhubs/1?carga_dia=60` | 200 | 200 | PASA |
| CAP-07 | capacidad | Qué pasa con 120 pedidos al día y 6 operadores y 6 repartidores. | `POST /api/v1/capacidad/simulaciones` | 200 | 200 | PASA |
| CAP-08 | capacidad | Utilización a distintas cargas y el punto donde se pasa del umbral. | `GET /api/v1/capacidad/cargas?microhub_id=1` | 200 | 200 | PASA |
| CAP-09 | capacidad | El planeador corrige operadores y repartidores del microhub. | `PUT /api/v1/capacidad/recursos/1` | 200 | 200 | PASA |
| CAP-10 | capacidad | El operador no tiene capacidad.editar. | `PUT /api/v1/capacidad/recursos/1` | 403 | 403 | PASA |
| CAP-11 | capacidad | Al menos un operador. | `PUT /api/v1/capacidad/recursos/1` | 422 | 422 | PASA |
| CAP-12 | capacidad | Productividad por etapa, umbrales y horas del turno. | `GET /api/v1/capacidad/supuestos` | 200 | 200 | PASA |
| COS-01 | costos | Los globales (pago al repartidor, empaque, comisión) y los propios (renta, nómina…). | `GET /api/v1/costos/conceptos?microhub_id=1&por_pagina=100` | 200 | 200 | PASA |
| COS-02 | costos | Fijos del mes por categoría y variables por unidad. | `GET /api/v1/costos/resumen?microhub_id=1` | 200 | 200 | PASA |
| COS-03 | costos | Costo fijo ÷ pedidos del mes + variable + comisión + entrega. | `GET /api/v1/costos/unitarios?microhub_id=1&pedidos_mes=1000&ticket=150` | 200 | 200 | PASA |
| COS-04 | costos | Margen de contribución, utilidad del mes y margen operativo. | `GET /api/v1/costos/rentabilidad?microhub_id=1&pedidos_mes=1500` | 200 | 200 | PASA |
| COS-05 | costos | Cada palanca sube y baja 10 y 20 %; se dice cuál mueve más la utilidad. | `GET /api/v1/costos/sensibilidad?microhub_id=1&pedidos_mes=1500` | 200 | 200 | PASA |
| COS-06 | costos | Respuesta XML que cumple costos.xsd. | `GET /api/v1/costos/unitarios?microhub_id=1` | 200 | 200 | PASA |
| COS-07 | costos | Sin costos.ver. | `GET /api/v1/costos/conceptos` | 403 | 403 | PASA |
| COS-08 | costos | Un auditor consulta, no edita. | `POST /api/v1/costos/conceptos` | 403 | 403 | PASA |
| COS-09 | costos | Costo fijo de un microhub con su justificación. | `POST /api/v1/costos/conceptos` | 201 | 201 | PASA |
| COS-10 | costos | Cualquier subconjunto de campos; el ámbito no cambia. | `PUT /api/v1/costos/conceptos/63` | 200 | 200 | PASA |
| COS-16 | costos | PATCH es alias de PUT: lo usa la app Android cuando la JVM no admite PUT con cuerpo parcial. | `PATCH /api/v1/costos/conceptos/63` | 200 | 200 | PASA |
| COS-11 | costos | Baja lógica: el renglón se conserva para la historia. | `DELETE /api/v1/costos/conceptos/63` | 204 | 204 | PASA |
| COS-12 | costos | Un costo fijo se da por mes. | `POST /api/v1/costos/conceptos` | 422 | 422 | PASA |
| COS-13 | costos | El ámbito debe existir. | `POST /api/v1/costos/conceptos` | 422 | 422 | PASA |
| COS-14 | costos | Sin conceptos propios toma renta, nómina y servicios de la ubicación (planeación). | `GET /api/v1/costos/resumen?candidato_id=3` | 200 | 200 | PASA |
| COS-15 | costos | Volumen y ticket de referencia, paradas por viaje y margen por omisión; los montos de cada costo son conceptos con su propia justificación. | `GET /api/v1/costos/supuestos` | 200 | 200 | PASA |
| EQU-01 | punto-equilibrio | 45 pedidos al día, ticket 135, margen 28 %, fijos 60,000 y entrega 32.60. | `POST /api/v1/punto-equilibrio/calculos` | 200 | 200 | PASA |
| EQU-02 | punto-equilibrio | Con 70 pedidos al día el equilibrio es 53.3. | `POST /api/v1/punto-equilibrio/calculos` | 200 | 200 | PASA |
| EQU-03 | punto-equilibrio | Con 55 pedidos al día el equilibrio es 53.3. | `POST /api/v1/punto-equilibrio/calculos` | 200 | 200 | PASA |
| EQU-04 | punto-equilibrio | Con 40 pedidos al día el equilibrio es 53.3. | `POST /api/v1/punto-equilibrio/calculos` | 200 | 200 | PASA |
| EQU-05 | punto-equilibrio | Costos de costos, ticket y demanda de demanda, personal de cobertura. | `POST /api/v1/punto-equilibrio/calculos` | 200 | 200 | PASA |
| EQU-06 | punto-equilibrio | Con ticket = 200 el origen del ticket es «manual». | `POST /api/v1/punto-equilibrio/calculos` | 200 | 200 | PASA |
| EQU-07 | punto-equilibrio | Sin microhub ni candidato hay que dar los datos. | `POST /api/v1/punto-equilibrio/calculos` | 422 | 422 | PASA |
| EQU-08 | punto-equilibrio | Cada variable sube y baja 10 y 20 %; se ordenan por lo que mueven la utilidad. | `POST /api/v1/punto-equilibrio/sensibilidad` | 200 | 200 | PASA |
| EQU-09 | punto-equilibrio | Entrada y salida en XML, validadas contra punto_equilibrio.xsd. | `POST /api/v1/punto-equilibrio/calculos` | 200 | 200 | PASA |
| EQU-10 | punto-equilibrio | Guardar un escenario exige equilibrio.editar. | `POST /api/v1/punto-equilibrio/calculos` | 403 | 403 | PASA |
| EQU-11 | punto-equilibrio | Queda en equilibrio_escenario con su cálculo completo. | `POST /api/v1/punto-equilibrio/calculos` | 201 | 201 | PASA |
| EQU-12 | punto-equilibrio | Queda en equilibrio_escenario con su cálculo completo. | `POST /api/v1/punto-equilibrio/calculos` | 201 | 201 | PASA |
| EQU-13 | punto-equilibrio | Abrir la lista de escenarios. | `GET /api/v1/punto-equilibrio/escenarios?por_pagina=100` | 200 | 200 | PASA |
| EQU-14 | punto-equilibrio | Lado a lado: decisión, equilibrio, diferencia y utilidad. | `GET /api/v1/punto-equilibrio/comparacion?ids=42,43` | 200 | 200 | PASA |
| EQU-15 | punto-equilibrio | Con su cálculo paso a paso. | `GET /api/v1/punto-equilibrio/escenarios/42` | 200 | 200 | PASA |
| EQU-16 | punto-equilibrio | Borrar es de equilibrio.editar. | `DELETE /api/v1/punto-equilibrio/escenarios/42` | 403 | 403 | PASA |
| EQU-17 | punto-equilibrio | Se elimina el escenario. | `DELETE /api/v1/punto-equilibrio/escenarios/42` | 204 | 204 | PASA |
| EQU-18 | punto-equilibrio | Una fila por microhub activo con sus datos reales. | `GET /api/v1/punto-equilibrio/microhubs` | 200 | 200 | PASA |
| EQU-19 | punto-equilibrio | Margen de seguridad mínimo y margen bruto por omisión. | `GET /api/v1/punto-equilibrio/supuestos` | 200 | 200 | PASA |
| SUR-01 | surtido | A hasta 80 % acumulado de unidades, B hasta 95 %, C el resto. | `GET /api/v1/surtido/abc?microhub_id=1` | 200 | 200 | PASA |
| SUR-02 | surtido | Clase, rotación, cobertura, margen, quiebres y recomendación por producto. | `GET /api/v1/surtido/analisis?microhub_id=1` | 200 | 200 | PASA |
| SUR-03 | surtido | Sin microhub no hay restricciones de espacio ni de presupuesto. | `GET /api/v1/surtido/analisis` | 200 | 200 | PASA |
| SUR-04 | surtido | Filtro por clase. | `GET /api/v1/surtido/analisis?microhub_id=1&clase=A` | 200 | 200 | PASA |
| SUR-05 | surtido | Solo A, B o C. | `GET /api/v1/surtido/analisis?microhub_id=1&clase=Z` | 400 | 400 | PASA |
| SUR-06 | surtido | Respuesta XML que cumple surtido.xsd. | `GET /api/v1/surtido/analisis?microhub_id=1` | 200 | 200 | PASA |
| SUR-07 | surtido | Operador y supervisor solo trabajan con el suyo. | `GET /api/v1/surtido/analisis?microhub_id=1` | 200 | 200 | PASA |
| SUR-08 | surtido | No puede. | `GET /api/v1/surtido/analisis?microhub_id=2` | 403 | 403 | PASA |
| SUR-09 | surtido | Espacio y presupuesto. | `GET /api/v1/surtido/restricciones/1` | 200 | 200 | PASA |
| SUR-10 | surtido | El planeador fija otro espacio y presupuesto. | `PUT /api/v1/surtido/restricciones/1` | 200 | 200 | PASA |
| SUR-19 | surtido | PATCH es alias de PUT. | `PATCH /api/v1/surtido/restricciones/1` | 200 | 200 | PASA |
| SUR-11 | surtido | Solo surtido.editar. | `PUT /api/v1/surtido/restricciones/1` | 403 | 403 | PASA |
| SUR-12 | surtido | Mayor que cero. | `PUT /api/v1/surtido/restricciones/1` | 422 | 422 | PASA |
| SUR-13 | surtido | Queda con sus líneas y los supuestos usados, para compararla después. | `POST /api/v1/surtido/recomendaciones` | 201 | 201 | PASA |
| SUR-18 | surtido | Para compararlas con el tiempo. | `GET /api/v1/surtido/recomendaciones?microhub_id=1` | 200 | 200 | PASA |
| SUR-14 | surtido | Con el mismo resumen con que se guardó. | `GET /api/v1/surtido/recomendaciones/34` | 200 | 200 | PASA |
| SUR-15 | surtido | El operador de otro microhub no la ve. | `GET /api/v1/surtido/recomendaciones/34` | 403 | 403 | PASA |
| SUR-16 | surtido | El operador no tiene surtido.editar. | `POST /api/v1/surtido/recomendaciones` | 403 | 403 | PASA |
| SUR-17 | surtido | Cortes ABC, días de cobertura y ventana de análisis. | `GET /api/v1/surtido/supuestos` | 200 | 200 | PASA |
| RUT-01 | pedidos | Los que rutas va a agrupar: en preparación y marcados como listos. | `GET /api/v1/pedidos/listos?microhub_id=1&por_pagina=100` | 200 | 200 | PASA |
| RUT-02 | rutas | Agrupa por zona, reparte entre repartidores, ordena las paradas, y calcula distancia, tiempo y costo. | `POST /api/v1/rutas/planes` | 200 | 200 | PASA |
| RUT-03 | rutas | Las mismas paradas con orden de llegada, vecino más cercano, 2-opt y exacto. | `POST /api/v1/rutas/comparaciones` | 200 | 200 | PASA |
| RUT-04 | rutas | El exacto con un solo repartidor. | `POST /api/v1/rutas/planes` | 200 | 200 | PASA |
| RUT-05 | rutas | Queda en plan_despacho como «propuesto»; todavía no escribe rutas. | `POST /api/v1/rutas/planes` | 201 | 201 | PASA |
| RUT-06 | rutas | Suma minutos a su ruta y dice qué paradas quedan fuera de la promesa de 30 minutos. | `POST /api/v1/rutas/planes/93/ajustes` | 200 | 200 | PASA |
| RUT-07 | rutas | Recalcula la ruta afectada con el mismo método. | `POST /api/v1/rutas/planes/93/ajustes` | 200 | 200 | PASA |
| RUT-08 | rutas | Lo pone en la ruta con menos paradas, sin pasar del tope de 8. | `POST /api/v1/rutas/planes/93/ajustes` | 200 | 200 | PASA |
| RUT-09 | rutas | Operador y supervisor solo trabajan con el suyo. | `GET /api/v1/rutas/planes/93` | 403 | 403 | PASA |
| RUT-10 | rutas | Comprueba que los pedidos sigan listos y deja las rutas en plan_ruta. | `POST /api/v1/rutas/planes/93/confirmar` | 200 | 200 | PASA |
| RUT-11 | rutas | Un plan confirmado no se vuelve a confirmar. | `POST /api/v1/rutas/planes/93/confirmar` | 409 | 409 | PASA |
| RUT-12 | rutas | Lista con estado, rutas, paradas, distancia y costo. | `GET /api/v1/rutas/planes?microhub_id=1` | 200 | 200 | PASA |
| RUT-13 | rutas | Un plan que no se confirmó se cancela. | `POST /api/v1/rutas/planes/94/cancelar` | 200 | 200 | PASA |
| RUT-14 | rutas | No hay nada que despachar. | `POST /api/v1/rutas/planes` | 422 | 422 | PASA |
| RUT-15 | rutas | Un pedido ajeno o no listo se rechaza. | `POST /api/v1/rutas/planes` | 422 | 422 | PASA |
| RUT-16 | rutas | No puede. | `POST /api/v1/rutas/planes` | 403 | 403 | PASA |
| RUT-17 | rutas | Consulta, no planea. | `POST /api/v1/rutas/planes` | 403 | 403 | PASA |
| RUT-18 | rutas | El cuerpo XML lleva la lista de pedidos y se valida contra rutas.xsd. | `POST /api/v1/rutas/planes` | 200 | 200 | PASA |
| RUT-19 | rutas | Velocidad, tiempo por parada, costo por km, tope de paradas y rodeo. | `GET /api/v1/rutas/supuestos` | 200 | 200 | PASA |
| SIM-01 | simulacion | Junta la entrada de otros servicios, la guarda y responde 202 sin esperar el resultado. | `POST /api/v1/simulacion/ejecuciones` | 202 | 202 | PASA |
| SIM-02 | simulacion | Media y percentiles 10, 50 y 90 de utilidad, pedidos atendidos y rechazados; probabilidad de perder. | `GET /api/v1/simulacion/ejecuciones/25c5f9b3-04b6-4b10-be41-6d47a2c79f96` | 200 | 200 | PASA |
| SIM-03 | simulacion | Debe dar exactamente lo mismo. | `POST /api/v1/simulacion/ejecuciones/25c5f9b3-04b6-4b10-be41-6d47a2c79f96/repetir` | 202 | 202 | PASA |
| SIM-04 | simulacion | Misma huella: la simulación es reproducible. | `GET /api/v1/simulacion/ejecuciones/357fa160-4fff-4b90-8c4e-28c9cf1b62e1` | 200 | 200 | PASA |
| SIM-05 | simulacion | Misma entrada con semilla 12: la huella cambia. | `GET /api/v1/simulacion/ejecuciones/a15b01d8-c9d3-4cb1-84e8-aa39e1553e66` | 200 | 200 | PASA |
| SIM-06 | simulacion | Utilidad media, P10, P90, probabilidad de pérdida y días saturados lado a lado. | `GET /api/v1/simulacion/comparacion?ids=25c5f9b3-04b6-4b10-be41-6d47a2c79f96,a15b01d8-c9d3-4cb1-84e8-aa39e1553e66` | 200 | 200 | PASA |
| SIM-07 | simulacion | Sin microhub ni candidato, con todos los datos escritos (el escenario A). | `POST /api/v1/simulacion/ejecuciones` | 202 | 202 | PASA |
| SIM-08 | simulacion | 100 % de las réplicas terminan en pérdida: lo que ya decía el punto de equilibrio. | `GET /api/v1/simulacion/ejecuciones/d663c0c3-2ffb-49ff-b440-3eed2ebe44b1` | 200 | 200 | PASA |
| SIM-09 | simulacion | Sin microhub hay que dar todos los datos. | `POST /api/v1/simulacion/ejecuciones` | 422 | 422 | PASA |
| SIM-10 | simulacion | Días × réplicas no puede pasar de 200,000. | `POST /api/v1/simulacion/ejecuciones` | 422 | 422 | PASA |
| SIM-11 | simulacion | Una ejecución en cola o en curso se puede cancelar. | `POST /api/v1/simulacion/ejecuciones/602f3dd1-335b-4487-a893-e6820eac4d90/cancelar` | 200 | 200 | PASA |
| SIM-12 | simulacion | Solo se cancela lo que está en cola o en curso. | `POST /api/v1/simulacion/ejecuciones/602f3dd1-335b-4487-a893-e6820eac4d90/cancelar` | 409 | 409 | PASA |
| SIM-13 | simulacion | Lista paginada, la más reciente primero. | `GET /api/v1/simulacion/ejecuciones?por_pagina=5` | 200 | 200 | PASA |
| SIM-14 | simulacion | Sin simulacion.ver. | `GET /api/v1/simulacion/ejecuciones` | 403 | 403 | PASA |
| SIM-15 | simulacion | Sin simulacion.ejecutar. | `POST /api/v1/simulacion/ejecuciones` | 403 | 403 | PASA |
| SIM-16 | simulacion | Entrada y salida en XML, validadas contra simulacion.xsd. | `POST /api/v1/simulacion/ejecuciones` | 202 | 202 | PASA |
| SIM-17 | simulacion | Un identificador que no existe. | `GET /api/v1/simulacion/ejecuciones/054be617-6510-4792-aae6-ba1181c4657d` | 404 | 404 | PASA |
| SIM-18 | simulacion | Réplicas, ausentismo, variación de la demanda y semilla. | `GET /api/v1/simulacion/supuestos` | 200 | 200 | PASA |
| ENL-01 | documentos | URL de un solo método y con caducidad para bajar el archivo del almacén. | `GET /api/v1/documentos/6b08947e14ec03b218378d3f/enlace` | 200 | 200 | PASA |
| ENL-02 | documentos | El enlace funciona sin token: la firma es el permiso. | `GET /api/v1/documentos/descarga?k=documentos%2F2026%2F11%2F6b08947e14ec03b218378d3f.pdf&e=1795724714&n=evidencia-enlace.pdf&t=application%2Fpdf&s=Zx3fIbbP9gRII5QKr7HKXMGyKahBV_5PPz6hh-2SKjw` | 200 | 200 | PASA |
| ENL-03 | documentos | Cambiar un carácter de la firma lo invalida. | `GET /api/v1/documentos/descarga?k=documentos%2F2026%2F11%2F6b08947e14ec03b218378d3f.pdf&e=1795724714&n=evidencia-enlace.pdf&t=application%2Fpdf&s=Zx3fIbbP9gRII5QKr7HKXMGyKahBV_5PPz6hh-2SKAA` | 403 | 403 | PASA |
| MNT-01 | auditoria-monitoreo | Pregunta la salud de cada servicio y guarda el resultado. | `POST /api/v1/monitoreo/verificaciones` | 201 | 201 | PASA |
| MNT-02 | auditoria-monitoreo | Estado, última verificación, tiempo, versión, dependencias, errores y disponibilidad de cada servicio. | `GET /api/v1/monitoreo/estado` | 200 | 200 | PASA |
| MNT-03 | auditoria-monitoreo | El mismo panel validado contra auditoria_monitoreo.xsd. | `GET /api/v1/monitoreo/estado` | 200 | 200 | PASA |
| MNT-04 | auditoria-monitoreo | Serie de verificaciones, la más reciente primero. | `GET /api/v1/monitoreo/servicios/pedidos/historial?por_pagina=3` | 200 | 200 | PASA |
| MNT-05 | auditoria-monitoreo | Porcentaje disponible, salud plena y percentiles p50 y p95. | `GET /api/v1/monitoreo/disponibilidad?horas=24` | 200 | 200 | PASA |
| MNT-06 | auditoria-monitoreo | Peticiones, errores y percentiles de duración por servicio, desde MongoDB. | `GET /api/v1/monitoreo/metricas?minutos=60` | 200 | 200 | PASA |
| MNT-07 | auditoria-monitoreo | Cada umbral con su origen y cómo se calibra. | `GET /api/v1/monitoreo/supuestos` | 200 | 200 | PASA |
| MNT-08 | auditoria-monitoreo | Con el umbral de latencia en 0 ms, la verificación abre una alerta real. | `GET /api/v1/monitoreo/alertas?estado=abiertas&servicio=zonas` | 200 | 200 | PASA |
| MNT-09 | auditoria-monitoreo | Queda quién se hizo cargo y cuándo. | `POST /api/v1/monitoreo/alertas/195/reconocer` | 200 | 200 | PASA |
| MNT-10 | auditoria-monitoreo | El auditor ve el monitoreo pero no lo opera. | `POST /api/v1/monitoreo/alertas/195/reconocer` | 403 | 403 | PASA |
| MNT-11 | auditoria-monitoreo | Sin monitoreo.ver. | `GET /api/v1/monitoreo/estado` | 403 | 403 | PASA |
| AUD-01 | auditoria-monitoreo | Quién cambió qué, cuándo y desde dónde. | `GET /api/v1/auditoria?modulo=pedidos&por_pagina=3` | 200 | 200 | PASA |
| AUD-02 | auditoria-monitoreo | Inicios, fallos, bloqueos y accesos denegados del periodo. | `GET /api/v1/auditoria/accesos` | 200 | 200 | PASA |
| AUD-03 | auditoria-monitoreo | Une bitácora, cambios de estado, inventario y archivos del pedido. | `GET /api/v1/auditoria/trazabilidad/pedido/1` | 200 | 200 | PASA |
| AUD-04 | auditoria-monitoreo | Bitácora y archivos de la entrega. | `GET /api/v1/auditoria/trazabilidad/entrega/1` | 200 | 200 | PASA |
| AUD-05 | auditoria-monitoreo | Trazabilidad del inventario. | `GET /api/v1/auditoria/trazabilidad/inventario?microhub_id=1&producto_id=1` | 200 | 200 | PASA |
| AUD-06 | auditoria-monitoreo | El planeador no tiene auditoria.ver; el intento queda registrado. | `GET /api/v1/auditoria` | 403 | 403 | PASA |
| REP-01 | reportes | Cuatro familias y los filtros que admite cada uno. | `GET /api/v1/reportes` | 200 | 200 | PASA |
| REP-02 | reportes | Pedidos, venta, ticket, alertas, repartidores y microhubs no viables. | `GET /api/v1/reportes/indicadores?desde=2026-08-28` | 200 | 200 | PASA |
| REP-03 | reportes | Pedidos, venta y participación de cada microhub. | `GET /api/v1/reportes/comparacion_microhubs?desde=2026-08-28` | 200 | 200 | PASA |
| REP-04 | reportes | El reporte financiero validado contra reportes.xsd. | `GET /api/v1/reportes/equilibrio_microhubs` | 200 | 200 | PASA |
| REP-05 | reportes | Categorías y series listas para graficar. | `GET /api/v1/reportes/pedidos_por_zona/grafica?desde=2026-08-28` | 200 | 200 | PASA |
| REP-06 | reportes | Descarga con SHA-256 y registro en la bitácora de exportaciones. | `GET /api/v1/reportes/pedidos_por_zona/exportar?formato=csv&desde=2026-08-28` | 200 | 200 | PASA |
| REP-07 | reportes | Quién exportó qué, con qué filtros. | `GET /api/v1/reportes/exportaciones?por_pagina=3` | 200 | 200 | PASA |
| REP-08 | reportes | Se rechaza en lugar de ignorarse. | `GET /api/v1/reportes/carga_repartidores?zona_id=1` | 400 | 400 | PASA |
| REP-09 | reportes | Sin reportes.ver. | `GET /api/v1/reportes` | 403 | 403 | PASA |
| SYN-01 | sincronizacion | La app manda el cierre y el recorrido; se aplican en el orden en que ocurrieron. | `POST /api/v1/sincronizacion/lotes` | 201 | 201 | PASA |
| SYN-02 | sincronizacion | Idempotencia: nada se repite. | `POST /api/v1/sincronizacion/lotes` | 200 | 200 | PASA |
| SYN-03 | sincronizacion | Gana el servidor y queda para revisión. | `POST /api/v1/sincronizacion/lotes` | 200 | 200 | PASA |
| SYN-04 | sincronizacion | Los ve quien tiene sincronizacion.ver. | `GET /api/v1/sincronizacion/conflictos?por_pagina=3` | 200 | 200 | PASA |
| SYN-05 | sincronizacion | El repartidor ve solo los suyos. | `GET /api/v1/sincronizacion/lotes?por_pagina=3` | 200 | 200 | PASA |
| SYN-06 | sincronizacion | Cada operación con su resultado. | `GET /api/v1/sincronizacion/lotes/157` | 200 | 200 | PASA |
| SYN-07 | sincronizacion | Lo que no se pudo aplicar porque un servicio no respondió. | `GET /api/v1/sincronizacion/pendientes` | 200 | 200 | PASA |
| SYN-08 | sincronizacion | Última sincronización y pendientes. | `GET /api/v1/sincronizacion/estado?dispositivo=android-evidencia-64d972` | 200 | 200 | PASA |
| SYN-09 | sincronizacion | Tamaño de lote, antigüedad y reloj. | `GET /api/v1/sincronizacion/supuestos` | 200 | 200 | PASA |
| SYN-10 | sincronizacion | Sin sincronizacion.usar. | `POST /api/v1/sincronizacion/lotes` | 403 | 403 | PASA |
| SYN-11 | sincronizacion | operaciones debe ser una lista. | `POST /api/v1/sincronizacion/lotes` | 422 | 422 | PASA |
| SYN-12 | sincronizacion | Validado contra sincronizacion.xsd. | `GET /api/v1/sincronizacion/estado?dispositivo=android-evidencia-64d972` | 200 | 200 | PASA |
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
| SAL-DEM | demanda | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| SAL-COB | cobertura | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| SAL-CAP | capacidad | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| SAL-RUT | rutas | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| SAL-COS | costos | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| SAL-PUN | punto-equilibrio | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| SAL-SIM | simulacion | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| SAL-SUR | surtido | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| SAL-NOT | notificaciones | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| SAL-REP | reportes | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| SAL-SIN | sincronizacion | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| SAL-AUD | auditoria-monitoreo | Estado del servicio y de sus dependencias. | `GET /api/v1/health` | 200 | 200 | PASA |
| MON-01 | auth | Cada petición queda en MongoDB con su traza. | `GET /api/v1/auth/validar` | 200 | 200 | PASA |
| RAT-01 | zonas | Más de 240 solicitudes por minuto desde la misma IP. | `GET /api/v1/zonas` | 429 | 429 | PASA |

**Total:** 403 casos · 403 pasan · 0 fallan.