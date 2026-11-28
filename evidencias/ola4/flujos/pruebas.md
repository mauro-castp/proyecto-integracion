# Pruebas ejecutadas · microservicios v1

| ID | Servicio | Objetivo | Entrada | Esperado | Obtenido | Estado |
|---|---|---|---|---|---|---|
| F1-01 | planeacion | Planeación de ubicación. | `POST /api/v1/candidatos` | 201 | 201 | PASA |
| F1-02 | planeacion | Capacidad, utilización y decisión sugerida (MongoDB). | `POST /api/v1/candidatos/422/simular` | 200 | 200 | PASA |
| F1-03 | punto-equilibrio | Viabilidad financiera antes de decidir. | `POST /api/v1/punto-equilibrio/calculos` | 200 | 200 | PASA |
| F1-04 | planeacion | La decisión queda con motivo y en la bitácora. | `POST /api/v1/candidatos/422/decision` | 200 | 200 | PASA |
| F1-05 | microhubs | La candidata viable se vuelve microhub activo. | `POST /api/v1/microhubs` | 201 | 201 | PASA |
| F1-06 | capacidad | Operadores, repartidores y capacidad física. | `PUT /api/v1/capacidad/recursos/31` | 200 | 200 | PASA |
| F1-07 | usuarios | Cuenta nueva con su perfil y su microhub. | `POST /api/v1/usuarios` | 201 | 201 | PASA |
| F1-08a | inventario | Transferencia atómica desde MH-01. | `POST /api/v1/inventario/transferencias` | 201 | 201 | PASA |
| F1-08b | inventario | Transferencia atómica desde MH-01. | `POST /api/v1/inventario/transferencias` | 201 | 201 | PASA |
| F1-09 | pedidos | El motor lo asigna al microhub más cercano que tiene todo: el nuevo. | `POST /api/v1/pedidos` | 201 | 201 | PASA |
| F1-10 | pedidos | La transición la valida el motor. | `POST /api/v1/pedidos/1081/estado` | 200 | 200 | PASA |
| F1-11 | pedidos | Queda disponible para despacho. | `POST /api/v1/pedidos/1081/listo` | 200 | 200 | PASA |
| F1-07b | usuarios | RN41: cada repartidor pertenece a un microhub. | `POST /api/v1/usuarios` | 201 | 201 | PASA |
| F1-12 | rutas | Agrupa, asigna repartidor y ordena las paradas (algoritmo de rutas). | `POST /api/v1/rutas/planes` | 201 | 201 | PASA |
| F1-13 | entregas | El pedido pasa a ruta y el repartidor recibe el aviso. | `POST /api/v1/entregas` | 201 | 201 | PASA |
| F1-14 | entregas | Sesión validada en Redis. | `GET /api/v1/entregas/mias?por_pagina=50` | 200 | 200 | PASA |
| F1-15 | seguimiento | Puntos GPS en MongoDB (2dsphere). | `POST /api/v1/seguimiento/517/ubicaciones` | 201 | 201 | PASA |
| F1-16 | documentos | En la base solo sus datos; se descarga con un enlace firmado. | `GET /api/v1/documentos/6b0a3c51e768f05cdb023a98/enlace` | 200 | 200 | PASA |
| F1-17 | entregas | Cobro, ubicación y evidencia; idempotente. | `POST /api/v1/entregas/517/resultado` | 201 | 201 | PASA |
| F1-18 | notificaciones | Aviso generado por el motor. | `GET /api/v1/notificaciones?por_pagina=5` | 200 | 200 | PASA |
| F1-19 | auditoria-monitoreo | Bitácora, estados, inventario y archivos en una línea de tiempo. | `GET /api/v1/auditoria/trazabilidad/pedido/1081` | 200 | 200 | PASA |
| F1-20 | reportes | Datos listos para Highcharts. | `GET /api/v1/reportes/comparacion_microhubs/grafica?microhub_id=31` | 200 | 200 | PASA |
| F1-21 | microhubs | Baja lógica; conserva su historia. | `DELETE /api/v1/microhubs/31` | 204 | 204 | PASA |
| F2-01 | pedidos | El motor descuenta inventario en la misma transacción. | `POST /api/v1/pedidos` | 201 | 201 | PASA |
| F2-02 | inventario | El trigger avisa del faltante. | `PATCH /api/v1/inventario/1/31/minimo` | 200 | 200 | PASA |
| F2-03 | inventario | Qué producto, cuánto falta y qué tan grave es. | `GET /api/v1/inventario/alertas?microhub_id=1&por_pagina=100` | 200 | 200 | PASA |
| F2-04 | abastecimiento | Solicitud con sus líneas. | `POST /api/v1/abastecimiento/solicitudes` | 201 | 201 | PASA |
| F2-05 | abastecimiento | Quien pidió recibe el aviso. | `POST /api/v1/abastecimiento/solicitudes/130/decision` | 200 | 200 | PASA |
| F2-06 | abastecimiento | Al proveedor con la mejor oferta. | `POST /api/v1/abastecimiento/solicitudes/130/ordenar` | 201 | 201 | PASA |
| F2-07 | abastecimiento | Sube el inventario una sola vez (idempotente). | `POST /api/v1/abastecimiento/ordenes/85/recepcion` | 201 | 201 | PASA |
| F2-08 | documentos | Archivo con enlace firmado. | `GET /api/v1/documentos/6b0a3c55e768f05cdb023a9d/enlace` | 200 | 200 | PASA |
| F2-09 | auditoria-monitoreo | Salida por pedido y recepción por orden. | `GET /api/v1/auditoria/trazabilidad/inventario?microhub_id=1&producto_id=31` | 200 | 200 | PASA |
| F2-10 | reportes | Visualización y archivo descargable con huella. | `GET /api/v1/reportes/inventario_alertas/exportar?formato=csv&microhub_id=1` | 200 | 200 | PASA |
| F3-01 | pedidos | Punto de partida del recorrido. | `POST /api/v1/pedidos` | 201 | 201 | PASA |
| F3-02 | entregas | El repartidor la descarga antes de salir. | `POST /api/v1/entregas` | 201 | 201 | PASA |
| F3-03 | sincronizacion | Se aplica en el orden en que ocurrió. | `POST /api/v1/sincronizacion/lotes` | 201 | 201 | PASA |
| F3-04 | sincronizacion | No se repite nada. | `POST /api/v1/sincronizacion/lotes` | 200 | 200 | PASA |
| F3-05 | notificaciones | Aviso del motor. | `GET /api/v1/notificaciones?por_pagina=5` | 200 | 200 | PASA |
| F3-06 | auditoria-monitoreo | Bitácora y archivos de la entrega. | `GET /api/v1/auditoria/trazabilidad/entrega/518` | 200 | 200 | PASA |
| F3-07 | inventario | La devolución la hizo el motor. | `GET /api/v1/inventario/movimientos?microhub_id=2&por_pagina=5` | 200 | 200 | PASA |
| F3-08 | reportes | La entrega ya cuenta en los reportes. | `GET /api/v1/reportes/pedidos_por_dia/exportar?formato=csv` | 200 | 200 | PASA |

**Total:** 41 casos · 41 pasan · 0 fallan.