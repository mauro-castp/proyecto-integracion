# Procesos integrales de punta a punta

Corrida del 2026-11-27T17:32:58+00:00 con `servicios/pruebas/procesos_integrales.py` contra la plataforma en marcha. Cada paso lo hace la persona en su aplicación; las filas marcadas como PostgreSQL, MongoDB o bucket son comprobaciones directas.

| Proceso | Pasos | Correctos |
|---|---|---|
| P1 · Cierre de entrega | 10 | 10 de 10 |
| P2 · Reabastecimiento | 11 | 11 de 11 |
| P3 · Despacho con rutas y reporte archivado | 11 | 11 de 11 |

## P1 · Cierre de entrega

| # | Quién | Dónde | Paso | Resultado | Detalle |
|---|---|---|---|---|---|
| 1 | repartidor | Android | Ve sus paradas (GET entregas/mias) y elige la entrega 467 | ✓ | 5 paradas |
| 2 | repartidor | Android | Sube la foto de evidencia (POST documentos) | ✓ | id 6b09beca1bec79631659466f · ruta documentos/2026/11/6b09beca1bec79631659466f.png |
| 3 | repartidor | Android | Envía su recorrido GPS (POST seguimiento/ubicaciones) | ✓ | 5 puntos |
| 4 | repartidor | Android | Cierra la entrega cobrando el total (POST entregas/resultado) | ✓ | {'entrega_id': 467, 'pedido_id': 806, 'estado_pedido': 'entregado', 'cerrado_en': '2026-11-27T11:32:59-06:00', 'duplicado': False} |
| 5 | — | PostgreSQL | El pedido quedó entregado | ✓ | PED-20261127-000806: entregado |
| 6 | — | PostgreSQL · auditoría | Los triggers auditaron el cierre | ✓ | 2 registros |
| 7 | cliente | notificación | El cliente recibió el aviso | ✓ | Pedido PED-20261127-000806 |
| 8 | — | MongoDB + bucket | La foto: metadatos en MongoDB y el archivo en el almacén | ✓ | documentos/2026/11/6b09beca1bec79631659466f.png · local · sha256 c414cd0e204d… |
| 9 | — | MongoDB | El recorrido GPS quedó en ubicaciones_entrega | ✓ | 5 puntos |
| 10 | administrador | web | Ve el pedido entregado con su recorrido y evidencia (/web/servicios/pedido) | ✓ |  |

## P2 · Reabastecimiento

| # | Quién | Dónde | Paso | Resultado | Detalle |
|---|---|---|---|---|---|
| 1 | operador | web | Ve alertas de inventario y necesidades con la mejor oferta | ✓ | necesidades con oferta |
| 2 | operador | web | Crea la solicitud de compra (28 u. del producto 7) | ✓ | SC-20261127-000115 |
| 3 | administrador | web | Aprueba la solicitud | ✓ |  |
| 4 | administrador | web | Emite la orden de compra al proveedor (respeta su pedido mínimo) | ✓ | OC-20261127-000074 |
| 5 | operador | web | Recibe la mercancía con el comprobante (PDF) | ✓ | orden recibida |
| 6 | — | PostgreSQL | La existencia subió en inventario (entrada por el servicio de inventario) | ✓ | 10 → 38 |
| 7 | — | MongoDB + bucket | El comprobante: metadatos en MongoDB y el archivo en el almacén | ✓ | documentos/2026/11/6b09bed0c9b0068a77315104.pdf · local |
| 8 | planeador / operador | notificación | Los triggers avisaron la solicitud y la orden | ✓ | Orden de compra OC-20261127-000074; Solicitud de compra SC-20261127-000115; Orden de compra OC-20261127-000074 |
| 9 | — | PostgreSQL · auditoría | Auditoría de solicitud, orden e inventario | ✓ | 206 registros |
| 10 | operador | web | Ve la orden recibida y descarga el comprobante con URL firmada | ✓ |  |
| 11 | operador | web → bucket | La descarga firmada devuelve el mismo archivo | ✓ | HTTP 200 |

## P3 · Despacho con rutas y reporte archivado

| # | Quién | Dónde | Paso | Resultado | Detalle |
|---|---|---|---|---|---|
| 1 | operador | web (bandeja) | Marca pedidos como listos para despachar (en preparación → listo) | ✓ | 4 pedidos |
| 2 | planeador | web | Ve los pedidos listos (servicio de pedidos) | ✓ |  |
| 3 | planeador | web | Propone el plan de rutas (TSP exacto / 2-opt en el servicio de rutas) | ✓ | plan 160 |
| 4 | planeador | web | Revisa rutas, paradas, minutos y costo | ✓ |  |
| 5 | operador | web | Confirma y despacha: rutas → entregas crea y asigna las entregas (saga entre servicios) | ✓ | 4 entregas |
| 6 | repartidor | notificación | Cada repartidor recibió «Nueva entrega asignada» | ✓ | 21 avisos |
| 7 | repartidor | Android | Ve las nuevas paradas en su app (GET entregas/mias) | ✓ |  |
| 8 | planeador | web | Exporta el reporte de pedidos por día en PDF (servicio de reportes) | ✓ | 2412 bytes |
| 9 | — | PostgreSQL + bucket | La exportación quedó archivada: ruta y SHA-256 en la base, el archivo en el almacén | ✓ | reportes/2026/11/153.pdf · local · 672df25a0115… |
| 10 | planeador | web → bucket | La descarga con URL firmada trae el mismo archivo | ✓ | HTTP 200 |
| 11 | — | PostgreSQL · auditoría | Auditoría de las entregas asignadas y del enlace de descarga | ✓ | 42 registros |
