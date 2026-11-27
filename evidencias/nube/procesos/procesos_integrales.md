# Procesos integrales de punta a punta

Corrida del 2026-11-27T17:42:44+00:00 con `servicios/pruebas/procesos_integrales.py` contra la plataforma en marcha. Cada paso lo hace la persona en su aplicación; las filas marcadas como PostgreSQL, MongoDB o bucket son comprobaciones directas.

| Proceso | Pasos | Correctos |
|---|---|---|
| P1 · Cierre de entrega | 10 | 10 de 10 |
| P2 · Reabastecimiento | 12 | 12 de 12 |
| P3 · Despacho con rutas y reporte archivado | 11 | 11 de 11 |

## P1 · Cierre de entrega

| # | Quién | Dónde | Paso | Resultado | Detalle |
|---|---|---|---|---|---|
| 1 | repartidor | Android | Ve sus paradas (GET entregas/mias) y elige la entrega 181 | ✓ | 8 paradas |
| 2 | repartidor | Android | Sube la foto de evidencia (POST documentos) | ✓ | id 6b09c114be459ba76063a611 · ruta documentos/2026/11/6b09c114be459ba76063a611.png |
| 3 | repartidor | Android | Envía su recorrido GPS (POST seguimiento/ubicaciones) | ✓ | 5 puntos |
| 4 | repartidor | Android | Cierra la entrega cobrando el total (POST entregas/resultado) | ✓ | {'entrega_id': 181, 'pedido_id': 638, 'estado_pedido': 'entregado', 'cerrado_en': '2026-11-27T11:42:44-06:00', 'duplicado': False} |
| 5 | — | PostgreSQL | El pedido quedó entregado | ✓ | PED-20261127-000638: entregado |
| 6 | — | PostgreSQL · auditoría | Los triggers auditaron el cierre | ✓ | 2 registros |
| 7 | cliente | notificación | El cliente recibió el aviso | ✓ | Pedido PED-20261127-000638 |
| 8 | — | MongoDB + bucket | La foto: metadatos en MongoDB y el archivo en el almacén | ✓ | documentos/2026/11/6b09c114be459ba76063a611.png · gcs · sha256 c414cd0e204d… |
| 9 | — | MongoDB | El recorrido GPS quedó en ubicaciones_entrega | ✓ | 5 puntos |
| 10 | administrador | web | Ve el pedido entregado con su recorrido y evidencia (/web/servicios/pedido) | ✓ |  |

## P2 · Reabastecimiento

| # | Quién | Dónde | Paso | Resultado | Detalle |
|---|---|---|---|---|---|
| 1 | operador | API inventario | Registra una merma del producto 3: queda agotado | ✓ | 8 u. |
| 2 | operador | web | Ve alertas de inventario y necesidades con la mejor oferta | ✓ | necesidades con oferta |
| 3 | operador | web | Crea la solicitud de compra (24 u. del producto 3) | ✓ | SC-20261127-000028 |
| 4 | administrador | web | Aprueba la solicitud | ✓ |  |
| 5 | administrador | web | Emite la orden de compra al proveedor (respeta su pedido mínimo) | ✓ | OC-20261127-000024 |
| 6 | operador | web | Recibe la mercancía con el comprobante (PDF) | ✓ | orden recibida |
| 7 | — | PostgreSQL | La existencia subió en inventario (entrada por el servicio de inventario) | ✓ | 0 → 24 |
| 8 | — | MongoDB + bucket | El comprobante: metadatos en MongoDB y el archivo en el almacén | ✓ | documentos/2026/11/6b09c119be459ba76063a61c.pdf · gcs |
| 9 | planeador / operador | notificación | Los triggers avisaron la solicitud y la orden | ✓ | Solicitud de compra SC-20261127-000028; Solicitud de compra SC-20261127-000028; Orden de compra OC-20261127-000024 |
| 10 | — | PostgreSQL · auditoría | Auditoría de solicitud, orden e inventario | ✓ | 29 registros |
| 11 | operador | web | Ve la orden recibida y descarga el comprobante con URL firmada | ✓ |  |
| 12 | operador | web → bucket | La descarga firmada devuelve el mismo archivo | ✓ | HTTP 302 |

## P3 · Despacho con rutas y reporte archivado

| # | Quién | Dónde | Paso | Resultado | Detalle |
|---|---|---|---|---|---|
| 1 | operador | web (bandeja) | Marca pedidos como listos para despachar (en preparación → listo) | ✓ | 4 pedidos |
| 2 | planeador | web | Ve los pedidos listos (servicio de pedidos) | ✓ |  |
| 3 | planeador | web | Propone el plan de rutas (TSP exacto / 2-opt en el servicio de rutas) | ✓ | plan 27 |
| 4 | planeador | web | Revisa rutas, paradas, minutos y costo | ✓ |  |
| 5 | operador | web | Confirma y despacha: rutas → entregas crea y asigna las entregas (saga entre servicios) | ✓ | 4 entregas |
| 6 | repartidor | notificación | Cada repartidor recibió «Nueva entrega asignada» | ✓ | 6 avisos |
| 7 | repartidor | Android | Ve las nuevas paradas en su app (GET entregas/mias) | ✓ |  |
| 8 | planeador | web | Exporta el reporte de pedidos por día en PDF (servicio de reportes) | ✓ | 4843 bytes |
| 9 | — | PostgreSQL + bucket | La exportación quedó archivada: ruta y SHA-256 en la base, el archivo en el almacén | ✓ | reportes/2026/11/21.pdf · gcs · 5fe898c35a8d… |
| 10 | planeador | web → bucket | La descarga con URL firmada trae el mismo archivo | ✓ | HTTP 302 |
| 11 | — | PostgreSQL · auditoría | Auditoría de las entregas asignadas y del enlace de descarga | ✓ | 10 registros |
