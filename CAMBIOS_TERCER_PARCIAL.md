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

Ola 3, seguridad de configuración y comportamiento ante fallos de Redis, flujo integrado de la planeación a la entrega, apps Android y de escritorio
contra los nuevos servicios, y reporte técnico y presentación. La Ola 2 está más abajo.

---

# Tercer Parcial · Ola 2: análisis, planeación y viabilidad

La Ola 2 agrega los ocho servicios que responden a la pregunta de fondo del proyecto: **¿conviene abrir (o seguir operando) un microhub, con qué personal y
con qué surtido?** Quedan 23 servicios; faltan los tres de la Ola 3 (reportes, sincronización y auditoría-monitoreo).

## Qué se agregó

| Servicio | Puerto | Para qué sirve |
|---|---|---|
| demanda | 5115 | Pedidos por día, zona y categoría; patrón de la semana; proyección con banda de error y su prueba contra lo observado; demanda potencial por hogares |
| cobertura | 5116 | Qué zonas y hogares cubre la red; qué sumaría una ubicación nueva (hogares nuevos, traslape, costo de la última milla); escenarios de radio |
| capacidad | 5117 | Pedidos por hora y por día de un microhub (picking, empaque, despacho y reparto), utilización, cuello de botella y personal requerido |
| rutas | 5118 | Pedidos listos → agrupar por zona → asignar repartidor → ordenar paradas (exacto, 2-opt o vecino más cercano); confirmar y ajustar ante una incidencia |
| costos | 5119 | Conceptos de costo fijos y variables con vigencia y justificación, costo por pedido y por entrega, rentabilidad y sensibilidad |
| punto-equilibrio | 5120 | Cuántos pedidos al día hacen falta, con el cálculo paso a paso, sensibilidad y escenarios que se guardan y se comparan |
| simulacion | 5121 | Monte Carlo día por día con ausentismo y variación de la demanda; corre en segundo plano, con semilla y huella para repetirla |
| surtido | 5122 | Clasificación ABC, rotación, margen y quiebres; recomendación (aumentar, mantener, reducir, eliminar) limitada por espacio y presupuesto |

También crecieron tres de los diez primeros: `pedidos` (`resumen`, `ventas`, `listos`), `entregas` (`repartidores`) e `inventario` (`quiebres`), porque los servicios nuevos no leen
sus tablas y necesitan que alguien les dé esos datos.

## Cómo se conectan

- **Ningún servicio lee las tablas de otro.** El punto de equilibrio pide los costos a `costos`, la demanda a `demanda` y la cobertura a `cobertura`; la simulación pide
  el equilibrio y la capacidad; rutas pide los pedidos listos, los repartidores y los microhubs. Todas las llamadas llevan el JWT de quien consulta y el mismo
  `X-Traza-Id`, así que cada servicio aplica sus propios permisos.
- **Si un servicio de apoyo no responde, el cálculo lo dice (503) y no guarda nada a medias.** Lo que tiene todos sus datos escritos sigue funcionando. Hay un recorrido con
  contenedores reales en `evidencias/ola2/fallo_servicios.md`.
- **La simulación es asíncrona y reproducible.** `POST /simulacion/ejecuciones` guarda una foto de toda la entrada y responde 202; un hilo la toma de la cola. Misma foto y
  misma semilla dan la misma huella (SHA-256 de los resultados). Una ejecución que se queda a medias regresa a la cola a los 5 minutos y falla tras 3 intentos.
- **Los supuestos son datos, no código.** Los 41 valores viven en `configuracion` y cada uno tiene en `supuesto_documentado` su origen (medido, supuesto o normativo), su
  justificación y cómo calibrarlo con datos reales. Ver [`servicios/SUPUESTOS.md`](servicios/SUPUESTOS.md). Cada resultado trae los `supuestos_usados`.

## Respuesta a las observaciones del profesor

| Observación | Qué se hizo |
|---|---|
| Justificar los supuestos de cobertura, rutas, costos, capacidad y punto de equilibrio | `supuesto_documentado` con origen, justificación y cómo calibrar cada uno; `GET /<servicio>/supuestos`; `servicios/SUPUESTOS.md` (lo escribe `generar_supuestos.py` desde la base de datos) |
| Probarlos con escenarios | `servicios/pruebas/escenarios_ola2.py` cambia un supuesto a la vez y pide de nuevo el resultado: `evidencias/ola2/escenarios.md` (rodeo, velocidad, productividad, costo por km, penetración, ausentismo…) |
| Pruebas reproducibles | `servicios/pruebas/correr.sh` corre cualquier módulo, las evidencias o los escenarios dentro de la red de Docker con una sola orden; la simulación es reproducible por semilla y huella |
| Ejecución real de los clientes | Las 64 comprobaciones de la app de escritorio (35 sin red y 29 contra el backend real) siguen pasando con los XSD nuevos |

## Lo que se encontró al probar

- **Cuántos pedidos faltan para no perder.** Con los supuestos del equipo (ticket 135, margen bruto 28 %, entrega 32.60) cada pedido deja 5.20 y el equilibrio de un microhub con 60,000 de
  costos fijos es de unos 385 pedidos al día, contra una capacidad de 150: **no es viable con esos supuestos**, y la simulación lo confirma (pérdida en el 100 % de las réplicas).
  Ni subiendo el margen bruto al 40 % se llega: la decisión es muy sensible al ticket, al margen y a los costos fijos (tabla de escenarios).
- **La capacidad de MH-01 la limita el espacio, no el personal.** Con 3 operadores y 3 repartidores el cuello de botella es el tope físico de 150 pedidos al día; mejorar la productividad no
  sube la capacidad.
- **La promesa de 30 minutos depende sobre todo del tiempo en cada parada.** Con 4 minutos por parada una ruta de 6 pedidos termina a los 32 minutos; con 2 minutos todas las paradas caben.
- **Un error propio que las pruebas de escenario destaparon.** Los costos por kilómetro y por entrega parecían configurables desde `configuracion` y no movían el servicio de costos, que
  tiene sus propios conceptos. Se separó: costos publica sus supuestos reales y la nota «Dos valores que se parecen» de `SUPUESTOS.md` explica la relación.
- **Cancelar un pedido en preparación no se puede** (lo prohíbe el motor, RN21), y eso obligó a que las pruebas que necesitan pedidos listos los regresen a «asignado» antes de
  cancelarlos. Además se descubrió que cancelar con un `UPDATE` directo no devuelve el inventario: lo hace quien cancela con `fn_devolver_inventario`. Las pruebas lo hacían mal y
  dejaron 84 pedidos cancelados sin devolución; se repuso el inventario y ahora el ayudante de pruebas lo devuelve.

## Cambios en lo que ya existía

- `bloque_c/sql/10_ola2_analitica.sql` (idempotente) y `servicios/migrar.py` lo aplica a volúmenes existentes. Las filas de `supuesto_documentado` se refrescan al reaplicar.
- `servicios/planeacion/app.py` ya no pone `sistema_web/` al principio de `sys.path`: su `rutas.py` tapaba al paquete del servicio de rutas.
- El tablero «Microservicios» del web vigila los 23 servicios.
- `pedidos/resumen` solo suma la demanda no atendida de toda la red para quien tiene `reportes.ver`.
- `inventario/quiebres` rechaza `dias=0` (antes lo tomaba como «sin indicar»).

## Verificación

| Prueba | Resultado |
|---|---|
| Unitarias de los servicios | 37 |
| Fórmulas de la Ola 2 (sin bases de datos) | 65 |
| Contrato (23 servicios, JSON y XML) | 7 |
| El web contra los 23 servicios | 5 |
| Ola 1 contra PostgreSQL, Redis y MongoDB reales | 24 |
| Ola 2 contra PostgreSQL, Redis y MongoDB reales | 102 |
| Reglas SQL (`05_pruebas_reglas.sql`) | 26 de 26 |
| Planeación del web (`sistema_web/test_planeacion.py`) | 16 |
| App de escritorio (sin red y contra el backend real) | 35 + 29 |
| Evidencias de petición y respuesta | 359 de 359 (`evidencias/ola2/`), más 3 complementarias; las 171 operaciones del código tienen caso |

Se levantó el sistema con la migración 10 aplicada sobre un volumen que ya tenía datos.

## Pendiente para cerrar el parcial

Ola 3 (reportes, sincronización y auditoría-monitoreo), las funciones que faltan a los diez primeros servicios (altas y cambios de usuarios, productos, zonas y microhubs; crear y asignar pedidos
y entregas), seguridad de configuración y comportamiento ante fallos de Redis, el flujo integrado de la planeación a la entrega, las apps Android y de escritorio contra los servicios nuevos, y el
reporte técnico y la presentación.


---

# Tercer Parcial · Ola 3: observabilidad, reportes y sincronización

La Ola 3 completa los 26 servicios con:

- **reportes** (5123): reportes operativos, logísticos, comerciales y financieros armados con los servicios dueños, con exportación a
  CSV, Excel y PDF;
- **sincronizacion** (5125): lotes hechos sin conexión, aplicados en orden, idempotentes, con conflictos y reintentos;
- **auditoria-monitoreo** (5126): bitácora y trazabilidad; salud de los 26 cada 30 s; alertas que se abren y cierran solas; panel
  central en el web.

Lo acompañan el despliegue en GCP (VM, Nginx, bucket con URL firmadas, Cloud Logging) y `11_ola3_observabilidad.sql`.
Evidencias: **403 de 403** casos (`evidencias/ola3/`) y **401 de 401** en la nube (`evidencias/nube/`).

Las secciones «Pendiente para cerrar el parcial» de las Olas 1 y 2 son históricas: lo que listaban quedó resuelto en la Ola 3 y en la
entrega final.

---

# Entrega final · estabilización, volumen, carga, fallos e integración

Se hizo con la plataforma corriendo completa: 26 servicios y web con PostgreSQL 16, MongoDB 7 y Redis 7. Todo lo que sigue tiene un
script que lo reproduce.

## Qué se agregó

| Tema | Qué | Dónde |
|---|---|---|
| Datos de alto volumen | Generador incremental y marcado: 5 000 clientes, 100 000 pedidos, 1.4 M de puntos GPS, 200 000 logs; medición por etapas (inserción, índices, caché, API, recursos) | `bloque_c/scripts/generar_volumen.py`, `servicios/pruebas/medir_volumen.py`, `evidencias/volumen/` |
| Pruebas de carga | Locust con 6 perfiles (cliente, repartidor Android, operador, planeador XML, administrador, proceso automático); normal, alta, estrés por escalones, recuperación y protección | `pruebas_carga/`, `evidencias/carga/` |
| Fallos de infraestructura | Servicio detenido, Redis, MongoDB, PostgreSQL, bucket y tiempo excedido, con comprobación de datos a medias, monitoreo y logs | `servicios/pruebas/demo_fallos_infra.py`, `evidencias/fallos/`, `docs/RUNBOOK_FALLOS.md` |
| Procesos integrales | P2 reabastecimiento y P3 despacho con rutas y reportes en el **portal web** a través de los servicios; recorrido de punta a punta de P1, P2 y P3 | `sistema_web/procesos.py`, `servicios/pruebas/procesos_integrales.py`, `evidencias/procesos/` |
| Despacho de rutas | `POST entregas/asignaciones` (todo o nada) y `rutas/planes/{id}/confirmar {despachar: true}` como saga con compensación | `servicios/entregas`, `servicios/rutas` |
| Archivos en el bucket | Comprobante de orden de compra (`orden_compra` en documentos, XSD y validador de MongoDB) y exportaciones de reportes archivadas con URL firmada | `servicios/documentos`, `servicios/reportes`, `bloque_c/sql/13_entrega_final.sql` |
| Algoritmos | Documento con los 11 elementos y benchmark de calidad y tiempo | `docs/ALGORITMOS.md`, `servicios/pruebas/benchmark_algoritmos.py` |
| Documentación | Expediente (31 secciones, también en Word), manuales de instalación, técnico y de usuario, plan de pruebas, incidencias, guía de estudio, guion, bitácora y plantilla de reflexión | `docs/`, `reporte_tecnico/Expediente_Tecnico_Final_Equipo04.docx` |
| Diagramas | 18 (despliegue GCP), 19 (26 servicios), 20 y 21 (procesos integrales) | `bloque_d/` |

## Qué se corrigió (detalle en `docs/REGISTRO_INCIDENCIAS.md`)

- **Rendimiento** (`12_rendimiento.sql`, pedidos, demanda): `fn_pedidos_visibles` en SQL que el planificador puede integrar; resúmenes
  con índice y un solo cálculo; copia en Redis para las páginas 2 en adelante; inserción por lotes. La sincronización de demanda bajó
  de 37.5 s a 1.1 s y los reportes de 1.1 s a 0.2 s.
- **IP real detrás de Nginx** (`DETRAS_DE_PROXY`): en la nube, el límite por IP era global y la bitácora guardaba la IP del proxy.
- **MongoDB caído**: devolvía 500 y frenaba 4.5 s a todos los servicios. Ahora responde 503 y hay un cortacircuitos de 30 s.
- **Compose**: `LIMITE_*` y `DETRAS_DE_PROXY` ahora llegan a los contenedores.
- **Prueba de XSD del escritorio**: seguía esperando los 9 XSD del Segundo Parcial.

## Verificación (26 de noviembre de 2026)

| Suite | Resultado |
|---|---|
| Unitarias, almacén, contrato | 37 + 65 + 31 + 7 OK |
| Olas 1, 2 y 3 contra las bases reales | 24 + 102 + 74 OK |
| Web ↔ servicios / portal | 8 · 16 + 13 + 6 OK |
| Reglas SQL | 26 de 26 |
| XSD (lxml) | 10 OK |
| Procesos integrales | 32 de 32 pasos |
| Fallos | 6 de 6 casos y 33 de 33 comprobaciones |
