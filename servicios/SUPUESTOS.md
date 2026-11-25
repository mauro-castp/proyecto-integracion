# Supuestos de los modelos de la Ola 2

Lo escribe `servicios/pruebas/generar_supuestos.py` a partir de las tablas `configuracion` y `supuesto_documentado`; no se edita a mano. Generado el 2026-10-20.

## Cómo se manejan

- **El valor vive en la base de datos**, en `configuracion` (RN40). Ningún peso, umbral ni productividad es una constante del código: el código solo trae un valor de respaldo para no caerse si una clave se borra. Cambiar un valor no requiere recompilar ni reiniciar.
- **Cada supuesto dice de dónde sale y cómo se corrige.** `supuesto_documentado` guarda el origen (medido, supuesto o normativo), la justificación y el dato real con el que habría que calibrarlo. Cada servicio lo publica en `GET /api/v1/<servicio>/supuestos`.
- **Cada resultado dice qué supuestos usó.** Las respuestas de los modelos traen `supuestos_usados` con la clave, el valor y si la petición lo cambió. Un dato que el usuario escribe a mano sustituye al que vendría de otro servicio, y la respuesta lo marca (`origen: manual`).
- **Las conclusiones se prueban contra otros valores.** [`evidencias/ola2/escenarios.md`](../evidencias/ola2/escenarios.md) cambia un supuesto a la vez y muestra si la decisión cambia; lo corre `servicios/pruebas/escenarios_ola2.py`.

## Qué quiere decir cada origen

- **medido.** Sale de datos reales del sistema.
- **supuesto.** Es un valor razonable que aún no se ha medido.
- **normativo.** Lo fija el equipo o es una convención; no se estima.

Hoy hay 41 supuestos documentados: 0 medidos, 34 supuestos y 7 normativos. Ninguno es «medido» todavía porque la operación real es chica (pocos pedidos); cada fila dice con qué dato real se mediría. Hasta entonces las decisiones de viabilidad deben leerse como «con estos supuestos», no como una predicción.

## Demanda (`demanda`)

| Clave | Valor | Origen | De dónde sale | Cómo se calibra | La usan |
|---|---|---|---|---|---|
| `dem_backtest_dias` | 7 días | supuesto | Se ocultan los últimos 7 días para medir el error del modelo contra lo que de verdad pasó. | Ninguna; es el tamaño de la prueba. | demanda |
| `dem_banda_z` | 1.28 desviaciones | supuesto | Con 1.28 desviaciones, la banda deja afuera 10 % por arriba y 10 % por abajo si los errores se reparten como una campana. | Revisar qué porcentaje de los días reales cae dentro de la banda. | demanda |
| `dem_horizonte_dias` | 14 días | supuesto | Dos semanas: cubre el plazo de reposición y de contratación de personal. | Se ajusta al plazo de decisión que se quiera apoyar. | demanda |
| `dem_pedidos_hogar_mes` | 2.5 pedidos | supuesto | Un hogar que usa el servicio pide unas dos veces y media al mes: la compra grande del súper no se sustituye, pero sí las de reposición. | Frecuencia de compra observada (pedidos entre clientes distintos). | demanda |
| `dem_penetracion` | 0.12 fracción | supuesto | Parte de los hogares que pide a domicilio en un mes. 12 % es un valor prudente para un servicio de barrio que apenas empieza; no se ha medido. | Clientes distintos por mes entre los hogares de la zona. | demanda |
| `dem_ventana_dias` | 60 días | supuesto | Con 60 días hay ocho semanas completas, suficientes para ver el patrón de cada día de la semana. | Probar con otras ventanas y comparar el error del respaldo (backtest). | demanda |

## Cobertura (`cobertura`)

| Clave | Valor | Origen | De dónde sale | Cómo se calibra | La usan |
|---|---|---|---|---|---|
| `cob_solape_max_pct` | 40 % | supuesto | Si más del 40 % de las zonas de un microhub ya las cubre otro, los dos se reparten la misma demanda y se canibalizan. | Comparar la demanda de las zonas compartidas antes y después de abrir el segundo microhub. | cobertura |
| `cob_tiempo_max_min` | 30 minutos | normativo | Promesa de entrega que fija el equipo: llegar en 30 minutos o menos desde que sale el repartidor. | Se revisa con el tiempo real de las entregas cerradas. | cobertura, rutas |
| `factor_rodeo_distancia` | 1.3 veces | supuesto | La distancia por calle es mayor que la línea recta; en una retícula urbana suele ser de 1.2 a 1.5 veces. La regla de cobertura sigue siendo el radio en línea recta (como fn_cubre); el factor solo estima tiempos y costos. | Cociente entre la distancia del recorrido GPS y la distancia en línea recta entre el microhub y el domicilio, en entregas cerradas. | cobertura, rutas |
| `tamano_hogar` | 3.6 personas | supuesto | Personas por hogar para convertir población en hogares. Se usa 3.6, cercano al promedio nacional; no se ha confirmado para estas cuatro colonias. | Tomar el dato del Censo de Población y Vivienda (INEGI) de la AGEB de cada colonia. | demanda, cobertura |

## Capacidad (`capacidad`)

| Clave | Valor | Origen | De dónde sale | Cómo se calibra | La usan |
|---|---|---|---|---|---|
| `cap_distancia_entrega_km` | 2.4 km | supuesto | Distancia típica de entrega desde el microhub, ida solamente; es el valor del Escenario A de la retroalimentación. | Distancia promedio entre el microhub y los domicilios de las entregas cerradas. | capacidad, costos, simulacion |
| `cap_factor_pico` | 1.35 veces | supuesto | La hora pico recibe de 1.3 a 1.4 veces el promedio horario. | Distribución de pedidos por hora de pedido.creado_en. | capacidad |
| `despacho_pedidos_hora` | 30 pedidos/h | supuesto | Un operador despacha unos 30 pedidos por hora (2 minutos: verificar y entregar al repartidor). | Tiempo entre listo_en y la salida del repartidor. | capacidad, simulacion |
| `horas_turno` | 10 horas | supuesto | El microhub abre 12 horas (8 a 20 h); se toman 10 de trabajo efectivo descontando comida y cierre. | Horas realmente trabajadas según la asistencia del personal. | capacidad, simulacion |
| `packing_pedidos_hora` | 20 pedidos/h | supuesto | Un operador empaca unos 20 pedidos por hora (3 minutos por pedido). | Cronometrar una muestra de pedidos en el área de empaque. | capacidad, simulacion |
| `picking_pedidos_hora` | 10 pedidos/h | supuesto | Un operador junta unos 10 pedidos por hora (6 minutos por pedido de cinco líneas aproximadamente). | Tiempo entre asignado y en_preparacion en historial_estatus, o cronometrar una muestra de pedidos. | capacidad, simulacion |
| `umbral_utilizacion_estable` | 70 porcentaje | supuesto | Por debajo de 70 % queda holgura para los picos, que suelen ser de 1.3 a 1.4 veces el promedio. | Comparar la utilización por hora con los días en que hubo retrasos o rechazos. | capacidad |
| `umbral_utilizacion_riesgo` | 85 porcentaje | supuesto | Por encima de 85 % la espera en una fila crece muy rápido (teoría de colas), así que se considera riesgo de saturación. | Medir el tiempo de espera de los pedidos contra la utilización de cada día. | capacidad, simulacion |

## Rutas (`rutas`)

| Clave | Valor | Origen | De dónde sale | Cómo se calibra | La usan |
|---|---|---|---|---|---|
| `costo_base_entrega` | 18 MXN | supuesto | Pago fijo por entrega al repartidor; se suma al costo por distancia. Lo usan rutas y cobertura; costos tiene su propio concepto «Pago base al repartidor», que arranca con el mismo valor. | Lo que se paga de verdad por entrega en el contrato o en la nómina de repartidores; al corregirlo, corregir también el concepto en costos. | cobertura, rutas |
| `costo_km_reparto` | 4.5 MXN/km | supuesto | Combustible, mantenimiento y desgaste por kilómetro de una moto pequeña. Lo usan rutas y cobertura; el servicio de costos tiene su propio concepto «Combustible y desgaste», que arranca con el mismo valor. | Gasto real de combustible y mantenimiento entre los kilómetros recorridos del mismo periodo; al corregirlo, corregir también el concepto en costos. | cobertura, rutas |
| `max_paradas_repartidor` | 8 paradas | normativo | Tope que fija el equipo: con más paradas el pedido llega frío y el cálculo exacto de la ruta deja de ser práctico (el exacto se usa hasta 8 paradas). | Se revisa si el tiempo promedio de entrega supera la promesa de cobertura. | rutas |
| `tiempo_servicio_min` | 4 minutos | supuesto | Minutos que el repartidor pasa en cada parada: estacionar, entregar, cobrar y confirmar con el cliente. | Diferencia entre la llegada al domicilio y el cierre de la entrega en el recorrido GPS. | cobertura, capacidad, rutas, simulacion |
| `velocidad_reparto_kmh` | 22 km/h | supuesto | Velocidad media de un repartidor en moto o bicicleta dentro de las cuatro colonias, contando semáforos y esquinas. Es un valor típico de reparto urbano, no una medición del equipo. | Dividir la distancia del recorrido GPS entre su duración en cada entrega cerrada (servicio de seguimiento: inicio, fin y distancia_km) y promediar. | cobertura, capacidad, rutas, simulacion |

## Costos (`costos`)

| Clave | Valor | Origen | De dónde sale | Cómo se calibra | La usan |
|---|---|---|---|---|---|
| `cos_pedidos_mes_ref` | 1800 pedidos | supuesto | Volumen de referencia de 60 pedidos al día para repartir los costos fijos cuando no se indica otro. | Pedidos reales por mes del microhub. | costos |
| `cos_ticket_ref` | 135 MXN | supuesto | Ticket de referencia del escenario de la retroalimentación. | Ticket promedio real del servicio de demanda. | costos, punto-equilibrio |
| `paradas_por_viaje` | 3 paradas | supuesto | Paradas promedio de una salida cuando los pedidos se agrupan por zona. Reparte el costo del regreso al microhub entre ellas. | Promedio de la columna paradas de plan_ruta. | cobertura, capacidad, rutas, costos, simulacion |

## Punto de equilibrio (`punto-equilibrio`)

| Clave | Valor | Origen | De dónde sale | Cómo se calibra | La usan |
|---|---|---|---|---|---|
| `dias_operacion_mes` | 30 días | normativo | El microhub opera todos los días del mes. | Cambiar si se decide cerrar un día a la semana. | demanda, costos, punto-equilibrio, simulacion |
| `margen_bruto_default` | 0.28 fracción | supuesto | Margen bruto sobre la venta cuando no se conoce el costo del producto. En abarrotes urbanos es de 20 a 35 %. | Margen real por producto: servicio de precios, GET /precios/margenes. | costos, punto-equilibrio, surtido |
| `peq_margen_seguridad_pct` | 15 % | normativo | Decisión del equipo: un microhub es viable si la demanda esperada supera el equilibrio por al menos 15 %, como colchón ante la variación diaria. | Variación diaria de la demanda observada. | punto-equilibrio |

## Simulación (`simulacion`)

| Clave | Valor | Origen | De dónde sale | Cómo se calibra | La usan |
|---|---|---|---|---|---|
| `sim_ausentismo` | 0.05 fracción | supuesto | Cada operador o repartidor falta un día con probabilidad 5 %. No hay registros de asistencia todavía. | Faltas reales entre días laborables, cuando exista el registro de asistencia. | simulacion |
| `sim_dias_defecto` | 30 días | supuesto | Un mes de operación: el mismo plazo en que se miden los costos fijos y la utilidad. | Ninguna; es el horizonte de la simulación, se cambia según la decisión que se quiera apoyar. | simulacion |
| `sim_replicas_defecto` | 200 réplicas | supuesto | Con 200 réplicas el promedio y los percentiles ya no cambian de forma notable entre corridas. | Aumentar las réplicas hasta que P10, P50 y P90 se estabilicen. | simulacion |
| `sim_semilla_defecto` | 2026 semilla | normativo | La semilla fija el generador aleatorio: con los mismos parámetros se obtiene exactamente el mismo resultado. | Ninguna; cambiarla da otra corrida con la misma distribución, útil para comprobar que el resultado no depende del azar. | simulacion |
| `sim_variacion_demanda` | 0.10 fracción | supuesto | Un día cualquiera puede desviarse alrededor de 10 % de su promedio (clima, quincena, eventos del barrio), más allá del azar de contar pedidos. | Desviación estándar de pedidos reales dividida entre su promedio, por día de la semana. | simulacion |

## Surtido (`surtido`)

| Clave | Valor | Origen | De dónde sale | Cómo se calibra | La usan |
|---|---|---|---|---|---|
| `abc_a_pct` | 80 porcentaje | normativo | Regla de Pareto: los productos que acumulan hasta 80 % del movimiento son clase A. | No se calibra; es una convención de clasificación. | surtido |
| `abc_b_pct` | 95 porcentaje | normativo | Los productos hasta 95 % acumulado son clase B; el resto, clase C. | No se calibra; es una convención de clasificación. | surtido |
| `cobertura_dias_a` | 7 días | supuesto | Días de existencia que se quiere tener de un producto clase A. | Comparar con los quiebres de inventario de los productos A. | surtido |
| `cobertura_dias_b` | 5 días | supuesto | Días de existencia que se quiere tener de un producto clase B. | Comparar con los quiebres de inventario de los productos B. | surtido |
| `cobertura_dias_c` | 3 días | supuesto | Días de existencia que se quiere tener de un producto clase C. | Comparar con los quiebres de inventario de los productos C. | surtido |
| `cobertura_dias_exceso` | 30 días | supuesto | Con más de 30 días de cobertura el producto se considera con exceso. | Revisar con la caducidad y la rotación real. | surtido |
| `ventana_analisis_dias` | 90 días | supuesto | Tres meses de ventas para clasificar los productos: suficiente para ver la rotación sin arrastrar temporadas viejas. | Probar con 30 y 180 días y ver si cambian las clases A. | surtido |

## Dos valores que se parecen

`costo_km_reparto` y `costo_base_entrega` los usan **rutas y cobertura** (costo del recorrido y de la última milla). El servicio de **costos** no los lee: guarda sus propios conceptos («Combustible y desgaste», «Pago base al repartidor») con vigencia, fuente y justificación. Hoy valen lo mismo (4.50 y 18.00), pero son dos lugares: si se corrige uno hay que corregir el otro. Se dejó así porque rutas la usan operadores, que no tienen permiso de costos, y el servicio de costos no puede responder con el JWT de ellos. Queda anotado como deuda técnica.

## Datos sintéticos

La historia de demanda de la demostración (60 días por zona) la genera `10_ola2_analitica.sql` con una fórmula determinista y está marcada `fuente = sintetica` en cada renglón (`GET /demanda/observaciones`) y contada aparte en `GET /demanda/resumen`. No son ventas reales. `POST /demanda/sincronizacion` la reemplaza por lo real, rango por rango, cuando haya pedidos suficientes. La población de cada zona (`cobertura_zona_dato`) es una estimación del equipo hasta que se capture el dato de INEGI con `PUT /cobertura/zonas/{id}/poblacion`.

