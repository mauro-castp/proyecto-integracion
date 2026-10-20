# Tercer Parcial · Ola 1: flujo de negocio

El profesor pidió ampliar la plataforma a 26 microservicios. La Ola 1 agrega los cinco que cierran el ciclo de una compra: de que falta un
producto hasta que llega y se avisa.

## Qué se agregó

| Servicio | Puerto | Para qué sirve |
|---|---|---|
| inventario | 5111 | Existencias por microhub, movimientos (recepción, merma, ajuste, conteo), transferencias, reservas y alertas de faltantes |
| precios | 5112 | Listas de precios por zona, promociones, historial, márgenes y sensibilidad al precio |
| proveedores | 5113 | Proveedores, catálogos mayoristas, ofertas comparables, cobertura y evaluación |
| abastecimiento | 5114 | Necesidades de reposición, solicitudes y órdenes de compra, recepción de mercancía |
| notificaciones | 5124 | Bandeja de avisos, envío por persona o por rol y preferencias |

Quedan 15 servicios. Los 11 restantes (demanda, cobertura, capacidad, rutas, costos, punto de equilibrio, simulación, surtido, reportes,
sincronización y auditoría-monitoreo) van en las Olas 2 y 3.

## Cómo se conectan

- Abastecimiento le pide a inventario las alertas y la entrada de mercancía, y a proveedores las ofertas. Las llamadas llevan el JWT de quien
  hizo la petición y el mismo `X-Traza-Id`; el otro servicio aplica sus propios permisos.
- Los avisos de faltante, de solicitud y de orden de compra los generan triggers de PostgreSQL y respetan las preferencias de cada persona.
- Una reserva de inventario ligada a un pedido se consume cuando el pedido se asigna y se libera cuando se cancela.

## Cambios en lo que ya existía

- `bloque_c/sql/09_ola1_flujo_negocio.sql` (idempotente) y `servicios/migrar.py` lo aplica a volúmenes existentes.
- `sistema_web/migrar_web.py` ya no vuelve a aplicar `07_web_ampliado.sql` en cada arranque. Antes lo hacía y deshacía los cambios de `08`: los
  avisos de cierre de pedido perdían su tipo y su referencia, y por eso la evidencia ENT-05 salía vacía.
- El tablero «Microservicios» del web vigila los 15 servicios.
- Las fechas «de hoy» usan la hora de Monterrey (`fn_hoy()`); con `current_date` de PostgreSQL (UTC) una lista que empieza hoy empezaba mañana
  después de las 6 de la tarde.

## Verificación

| Prueba | Resultado |
|---|---|
| Unitarias de los servicios | 36 |
| Contrato (15 servicios, JSON y XML) | 7 |
| El web contra los 15 servicios | 5 |
| Ola 1 contra PostgreSQL, Redis y MongoDB reales | 24 |
| Reglas SQL (`05_pruebas_reglas.sql`) | 26 de 26 |
| Web y planeación | 35 |
| Evidencias de petición y respuesta | 204 de 204 (`evidencias/ola1/`), más 3 complementarias |

Se levantó el sistema desde cero (scripts 01 a 09) y también sobre un volumen que ya tenía datos (la migración 09 se aplicó sin borrar nada).

## Pendiente para cerrar el parcial

Olas 2 y 3, seguridad de configuración y comportamiento ante fallos de Redis, flujo integrado de la planeación a la entrega, supuestos de
cobertura, costos y capacidad con escenarios, apps Android y de escritorio contra los nuevos servicios, y reporte técnico y presentación.
