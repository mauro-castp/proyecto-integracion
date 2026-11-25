# Escenarios: qué cambia cuando cambia un supuesto

Corrida del 2026-10-20 06:41 contra los servicios desplegados. Cada bloque cambia **un** supuesto de la tabla `configuracion`, pide de nuevo el resultado y lo deja como estaba. En negritas, el valor vigente. De dónde sale cada supuesto y cómo se calibra: `GET /<servicio>/supuestos` y [`SUPUESTOS.md`](../../servicios/SUPUESTOS.md).

## Cobertura (servicio cobertura)

La cobertura se decide por el radio en línea recta (igual que `fn_cubre`); el rodeo de las calles y la velocidad solo estiman el **tiempo**. Lo que se juega es si el tiempo promedio cabe en la promesa de entrega (`cob_tiempo_max_min`).

### Rodeo de las calles (distancia por calle ÷ distancia en línea recta)

| factor_rodeo_distancia | Hogares cubiertos | Minutos promedio | Dentro de la promesa |
|---|---|---|---|
| 1 | 100.0 % | 5.1 | 100.0 % |
| 1.2 | 100.0 % | 5.4 | 100.0 % |
| **1.3** (vigente) | 100.0 % | 5.5 | 100.0 % |
| 1.5 | 100.0 % | 5.7 | 100.0 % |
| 1.8 | 100.0 % | 6.1 | 100.0 % |
| 2.2 | 100.0 % | 6.5 | 100.0 % |

### Velocidad del reparto

| velocidad_reparto_kmh | Hogares cubiertos | Minutos promedio | Dentro de la promesa |
|---|---|---|---|
| 10 | 100.0 % | 7.3 | 100.0 % |
| 15 | 100.0 % | 6.2 | 100.0 % |
| 18 | 100.0 % | 5.8 | 100.0 % |
| **22** (vigente) | 100.0 % | 5.5 | 100.0 % |
| 28 | 100.0 % | 5.2 | 100.0 % |
| 35 | 100.0 % | 4.9 | 100.0 % |

### Radio de cobertura de cada microhub

| Radio (km) | Zonas cubiertas | Hogares cubiertos | Minutos promedio |
|---|---|---|---|
| 0.5 | 75.0 % | 65.1 % | 5.1 |
| 1.0 | 100.0 % | 100.0 % | 5.5 |
| 1.5 | 100.0 % | 100.0 % | 5.5 |
| 2.0 | 100.0 % | 100.0 % | 5.5 |
| 2.5 | 100.0 % | 100.0 % | 5.5 |
| 3.0 | 100.0 % | 100.0 % | 5.5 |

## Capacidad (servicio capacidad)

Con el personal real del microhub 1 y una carga de 60 pedidos al día: ¿en qué nivel queda y cuál es el cuello de botella?

### picking_pedidos_hora

| picking_pedidos_hora | Capacidad al día | Utilización | Nivel | Cuello de botella | Operadores para 85 % |
|---|---|---|---|---|---|
| 6 | 120.0 | 50.0 % | estable | operacion | 2 |
| 8 | 144.0 | 41.7 % | estable | operacion | 2 |
| **10** (vigente) | 150 | 40.0 % | estable | espacio físico | 2 |
| 12 | 150 | 40.0 % | estable | espacio físico | 2 |
| 15 | 150 | 40.0 % | estable | espacio físico | 2 |

### packing_pedidos_hora

| packing_pedidos_hora | Capacidad al día | Utilización | Nivel | Cuello de botella | Operadores para 85 % |
|---|---|---|---|---|---|
| 10 | 128.6 | 46.7 % | estable | operacion | 2 |
| 15 | 150.0 | 40.0 % | estable | operacion | 2 |
| **20** (vigente) | 150 | 40.0 % | estable | espacio físico | 2 |
| 25 | 150 | 40.0 % | estable | espacio físico | 2 |
| 30 | 150 | 40.0 % | estable | espacio físico | 2 |

### horas_turno

| horas_turno | Capacidad al día | Utilización | Nivel | Cuello de botella | Operadores para 85 % |
|---|---|---|---|---|---|
| 6 | 98.2 | 61.1 % | estable | operacion | 3 |
| 8 | 130.9 | 45.8 % | estable | operacion | 2 |
| **10** (vigente) | 150 | 40.0 % | estable | espacio físico | 2 |
| 12 | 150 | 40.0 % | estable | espacio físico | 2 |

### Factor de la hora pico

| cap_factor_pico | Utilización promedio | Utilización en la hora pico | Nivel en la hora pico |
|---|---|---|---|
| 1 | 40.0 % | 36.7 % | estable |
| 1.2 | 40.0 % | 44.0 % | estable |
| **1.35** (vigente) | 40.0 % | 49.5 % | estable |
| 1.6 | 40.0 % | 58.7 % | estable |
| 2 | 40.0 % | 73.3 % | atencion |

## Costos y punto de equilibrio (servicios costos y punto-equilibrio)

Microhub 1 con 1,500 pedidos al mes: costo por pedido y utilidad mensual al cambiar lo que cuesta repartir.

### Concepto «Combustible y desgaste» (servicio costos)

| Monto | Costo de entrega | Costo por pedido | Utilidad del mes | Cubre costos |
|---|---|---|---|---|
| 3 | 22.8 | 76.55 | -58,122 | no |
| **4.5** (vigente) | 25.2 | 78.95 | -61,722 | no |
| 6 | 27.6 | 81.35 | -65,322 | no |
| 8 | 30.8 | 84.55 | -70,122 | no |

### Concepto «Pago base al repartidor» (servicio costos)

| Monto | Costo de entrega | Costo por pedido | Utilidad del mes | Cubre costos |
|---|---|---|---|---|
| 12 | 19.2 | 72.95 | -52,722 | no |
| **18** (vigente) | 25.2 | 78.95 | -61,722 | no |
| 24 | 31.2 | 84.95 | -70,722 | no |
| 30 | 37.2 | 90.95 | -79,722 | no |

### paradas_por_viaje (reparte el regreso al microhub entre las paradas del viaje)

| paradas_por_viaje | Costo de entrega | Costo por pedido | Utilidad del mes | Cubre costos |
|---|---|---|---|---|
| 1 | 39.6 | 93.35 | -83,322 | no |
| 2 | 28.8 | 82.55 | -67,122 | no |
| **3** (vigente) | 25.2 | 78.95 | -61,722 | no |
| 4 | 23.4 | 77.15 | -59,022 | no |
| 6 | 21.6 | 75.35 | -56,322 | no |

### Margen bruto sobre la venta (cuando no se conoce el costo del producto)

| margen_bruto_default | Pedidos al día esperados | Equilibrio diario | Margen de seguridad % | Decisión |
|---|---|---|---|---|
| 0.18 | 22.95 | no existe | no existe | no_viable |
| 0.22 | 22.95 | no existe | no existe | no_viable |
| **0.28** (vigente) | 22.95 | 456.07 | -94.97 | no_viable |
| 0.32 | 22.95 | 221.43 | -89.63 | no_viable |
| 0.36 | 22.95 | 146.21 | -84.3 | no_viable |
| 0.4 | 22.95 | 109.13 | -78.97 | no_viable |

### Ticket y margen: equilibrio diario con costos fijos de 60,000 y entrega de 32.60, para 60 pedidos al día

| Ticket \ margen bruto | 22 % | 28 % | 34 % | 40 % |
|---|---|---|---|---|
| 110 | sin equilibrio | sin equilibrio | 416.67 (no_viable) | 175.44 (no_viable) |
| 130 | sin equilibrio | 526.32 (no_viable) | 172.41 (no_viable) | 103.09 (no_viable) |
| 150 | 5000.0 (no_viable) | 212.77 (no_viable) | 108.7 (no_viable) | 72.99 (no_viable) |
| 170 | 416.67 (no_viable) | 133.33 (no_viable) | 79.37 (no_viable) | 56.5 (viable_ajustado) |
| 200 | 175.44 (no_viable) | 85.47 (no_viable) | 56.5 (viable_ajustado) | 42.19 (viable) |

## Rutas (servicio rutas)

Los mismos 6 pedidos listos del microhub 1 en una sola ruta (un repartidor, método exacto): distancia, tiempo y costo. «Fuera de la promesa» cuenta las paradas que se entregarían después de 30 minutos.

### velocidad_reparto_kmh

| velocidad_reparto_kmh | Distancia (km) | Minutos | Costo | Fuera de la promesa |
|---|---|---|---|---|
| 12 | 3.0 | 39.0 | 121.51 | 2 de 6 |
| 18 | 3.0 | 34.0 | 121.51 | 1 de 6 |
| **22** (vigente) | 3.0 | 32.2 | 121.51 | 1 de 6 |
| 30 | 3.0 | 30.0 | 121.51 | 0 de 6 |

### tiempo_servicio_min

| tiempo_servicio_min | Distancia (km) | Minutos | Costo | Fuera de la promesa |
|---|---|---|---|---|
| 2 | 3.0 | 20.2 | 121.51 | 0 de 6 |
| **4** (vigente) | 3.0 | 32.2 | 121.51 | 1 de 6 |
| 6 | 3.0 | 44.2 | 121.51 | 2 de 6 |
| 8 | 3.0 | 56.2 | 121.51 | 3 de 6 |

### factor_rodeo_distancia

| factor_rodeo_distancia | Distancia (km) | Minutos | Costo | Fuera de la promesa |
|---|---|---|---|---|
| 1 | 2.31 | 30.3 | 118.39 | 1 de 6 |
| **1.3** (vigente) | 3.0 | 32.2 | 121.51 | 1 de 6 |
| 1.6 | 3.69 | 34.1 | 124.62 | 2 de 6 |
| 2 | 4.62 | 36.6 | 128.78 | 2 de 6 |

### costo_km_reparto

| costo_km_reparto | Distancia (km) | Minutos | Costo | Fuera de la promesa |
|---|---|---|---|---|
| 3 | 3.0 | 32.2 | 117.0 | 1 de 6 |
| **4.5** (vigente) | 3.0 | 32.2 | 121.51 | 1 de 6 |
| 6 | 3.0 | 32.2 | 126.01 | 1 de 6 |

### Método de ordenamiento de las paradas

| Método | Distancia (km) | Minutos | Costo |
|---|---|---|---|
| Vecino más cercano | 3.26 | 32.9 | 122.66 |
| Vecino más cercano + 2-opt | 3.0 | 32.2 | 121.51 |
| TSP exacto | 3.0 | 32.2 | 121.51 |

## Demanda potencial (servicio demanda)

Qué parte de la demanda posible captura hoy la red según la penetración y la frecuencia de compra supuestas.

| Penetración | Pedidos por hogar al mes | Pedidos al día posibles | Pedidos al día observados | Cuota capturada |
|---|---|---|---|---|
| 0.06 | 2 | 26.8 | 50.0 | 186.4 % |
| 0.06 | 2.5 | 33.5 | 50.0 | 149.2 % |
| 0.06 | 3 | 40.3 | 50.0 | 124.3 % |
| 0.08 | 2 | 35.8 | 50.0 | 139.8 % |
| 0.08 | 2.5 | 44.7 | 50.0 | 111.9 % |
| 0.08 | 3 | 53.7 | 50.0 | 93.2 % |
| 0.12 | 2 | 53.7 | 50.0 | 93.2 % |
| 0.12 (vigente) | 2.5 | 67.1 | 50.0 | 74.6 % |
| 0.12 | 3 | 80.5 | 50.0 | 62.1 % |
| 0.16 | 2 | 71.6 | 50.0 | 69.9 % |
| 0.16 | 2.5 | 89.5 | 50.0 | 55.9 % |
| 0.16 | 3 | 107.3 | 50.0 | 46.6 % |
| 0.2 | 2 | 89.5 | 50.0 | 55.9 % |
| 0.2 | 2.5 | 111.8 | 50.0 | 44.7 % |
| 0.2 | 3 | 134.2 | 50.0 | 37.3 % |

## Surtido (servicio surtido)

Microhub 1: cuántos productos cambian de recomendación al mover los cortes.

### Corte de la clase A

| abc_a_pct | Productos A | B | C | Aumentar | Reducir | Eliminar |
|---|---|---|---|---|---|---|
| 60 | 20 | 23 | 8 | 1 | 49 | 1 |
| 70 | 25 | 18 | 8 | 1 | 49 | 1 |
| **80** (vigente) | 30 | 13 | 8 | 1 | 49 | 1 |
| 90 | 37 | 6 | 8 | 1 | 49 | 1 |

Con las ventas reales de la demostración (pocos pedidos en 90 días) la mayoría de los productos tiene años de cobertura, así que casi todo sale como «Reducir»; el umbral solo muerde cuando se sube a valores de varios cientos de días.

### Días de cobertura a partir de los cuales hay exceso

| cobertura_dias_exceso | Aumentar | Mantener | Reducir | Eliminar |
|---|---|---|---|---|
| **30** (vigente) | 1 | 0 | 49 | 1 |
| 120 | 1 | 0 | 49 | 1 |
| 365 | 1 | 6 | 43 | 1 |
| 1000 | 1 | 24 | 25 | 1 |
| 3000 | 1 | 38 | 11 | 1 |
| 9000 | 1 | 43 | 6 | 1 |

## Simulación (servicio simulacion)

Microhub 1, 30 días y 200 réplicas con la misma semilla. Cambiar el ausentismo o la variación de la demanda mueve la probabilidad de perder dinero.

| Ausentismo | Variación de la demanda | Utilidad media | P10 | P90 | Probabilidad de pérdida | Días saturados |
|---|---|---|---|---|---|---|
| 0 | 0 | -66,053 | -66,224 | -65,888 | 100.0 % | 0.0 % |
| 0 | 0.1 | -66,042 | -66,214 | -65,843 | 100.0 % | 0.0 % |
| 0 | 0.3 | -66,063 | -66,336 | -65,800 | 100.0 % | 0.0 % |
| 0.05 | 0 | -66,053 | -66,224 | -65,888 | 100.0 % | 0.0 % |
| 0.05 | 0.1 | -66,043 | -66,220 | -65,843 | 100.0 % | 0.0333 % |
| 0.05 | 0.3 | -66,065 | -66,343 | -65,800 | 100.0 % | 0.0333 % |
| 0.1 | 0 | -66,062 | -66,239 | -65,893 | 100.0 % | 0.25 % |
| 0.1 | 0.1 | -66,051 | -66,240 | -65,847 | 100.0 % | 0.25 % |
| 0.1 | 0.3 | -66,071 | -66,361 | -65,812 | 100.0 % | 0.2333 % |
| 0.2 | 0 | -66,108 | -66,315 | -65,899 | 100.0 % | 1.6 % |
| 0.2 | 0.1 | -66,086 | -66,285 | -65,883 | 100.0 % | 1.35 % |
| 0.2 | 0.3 | -66,107 | -66,397 | -65,817 | 100.0 % | 1.3833 % |

