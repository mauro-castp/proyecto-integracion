# Algoritmo de asignación y ordenamiento de rutas de reparto

Generado por `rendimiento/algoritmo_rutas.py` el 2026-11-26 en AMD64, Python 3.12.10. El código medido es `sistema_web/planeacion_calc.py`, el mismo que usan el servicio de rutas (puerto 5118) y el portal.

## 1. Problema

Un microhub tiene pedidos listos para salir y varios repartidores. Hay que decidir **qué repartidor lleva cada pedido** y **en qué orden visita** sus domicilios para recorrer poca distancia, sin pasar del máximo de paradas por repartidor. Ordenar las paradas es el problema del agente viajero (ruta abierta: no se regresa al microhub); asignar y ordenar a la vez es un problema de ruteo de vehículos, que es NP-difícil.

## 2. Entradas

| Entrada | Origen |
|---|---|
| Punto de salida (latitud, longitud) del microhub | servicio de microhubs |
| Pedidos listos: id, zona y coordenadas del domicilio | pedidos (`/pedidos/listos`) |
| Repartidores activos | entregas (`/entregas/repartidores`) |
| Parámetros: tope de paradas, velocidad, tiempo por parada, factor de rodeo, costos | `configuracion` (con su justificación en `supuesto_documentado`) |

## 3. Salidas

Por repartidor: orden de las paradas, distancia por tramo y total (km), minutos acumulados por parada, costo y zonas. Además, los pedidos que no cupieron (`sin_asignar`).

## 4. Variables

| Símbolo | Significado | Valor por omisión |
|---|---|---|
| n | paradas de un repartidor | — |
| P | pedidos listos | — |
| R | repartidores | — |
| T | tope de paradas por repartidor (`max_paradas_repartidor`) | 8 |
| v | velocidad de reparto (km/h) | 22.0 |
| s | minutos por parada | 4.0 |
| ρ | factor de rodeo: distancia por calle ÷ línea recta | 1.3 |
| d(a, b) | distancia de haversine entre dos puntos | — |

Distancia de una ruta: `ρ · Σ d(parada anterior, parada)`. Minutos: `distancia ÷ v · 60 + n · s`. Costo: `km · costo_km + n · costo_base_entrega`.

## 5. Restricciones

1. Cada pedido se asigna a lo sumo a un repartidor y se visita una sola vez.
2. Ningún repartidor recibe más de T paradas; lo que no cabe queda sin asignar y se informa.
3. Los pedidos de una misma zona se mantienen juntos mientras quepan en un repartidor.
4. La ruta empieza en el microhub y no incluye el regreso.
5. El método exacto solo se permite hasta 9 paradas (422 con más).

## 6. Método y pseudocódigo

```text
asignar(pedidos, repartidores, T):
    trozos ← agrupar pedidos por zona y partir cada grupo en bloques de a lo sumo T
    ordenar trozos de mayor a menor
    para cada trozo:
        r ← repartidor con menos paradas donde quepa completo
        si existe: darle el trozo
        si no: repartir sus pedidos uno por uno entre los menos cargados con lugar; el resto queda sin asignar
    para cada repartidor con paradas: orden ← ordenar(sus paradas)

ordenar(paradas):
    si n ≤ 8: devolver exacto(paradas)
    si no:    devolver dos_opt(vecino_mas_cercano(paradas))

exacto(paradas):                    # prueba las n! permutaciones
    mejor ← permutación de menor distancia

vecino_mas_cercano(paradas):
    actual ← microhub
    mientras queden pendientes:
        j ← pendiente más cercano a actual; agregar j; actual ← j

dos_opt(orden):
    repetir
        para cada par i < j:
            candidato ← orden con el tramo i..j invertido
            si distancia(candidato) < distancia(orden): orden ← candidato
    hasta que una pasada completa no mejore
```

## 7. Complejidad

| Paso | Tiempo | Espacio |
|---|---|---|
| Agrupar y repartir | O(P log P + P·R log R) | O(P) |
| Exacto | O(n! · n) | O(n) |
| Vecino más cercano | O(n²) | O(n) |
| 2-opt | O(k · n³): cada pasada prueba O(n²) inversiones y mide cada una en O(n); k = pasadas hasta no mejorar | O(n) |

El umbral de 8 paradas sale de las mediciones de abajo: el exacto crece de forma factorial y a partir de 9 deja de ser razonable para responder una petición.

## 8. Casos de prueba

| Caso | Esperado | Obtenido | Resultado |
|---|---|---|---|
| Sin paradas | [] | [] | ✔ |
| Una parada | [0] | [0] | ✔ |
| Cuatro paradas en línea recta: se visitan de la más cercana a la más lejana (exacto) | [1, 3, 0, 2] | [1, 3, 0, 2] | ✔ |
| Las mismas con vecino más cercano | [1, 3, 0, 2] | [1, 3, 0, 2] | ✔ |
| 2-opt corrige un orden malo hasta el óptimo | [1, 3, 0, 2] | [1, 3, 0, 2] | ✔ |
| Reparto: ningún repartidor pasa del tope de 10 paradas | True | True | ✔ |
| Reparto: 23 pedidos y 2 repartidores dejan 3 sin asignar | 3 | 3 | ✔ |
| Reparto: ningún pedido se pierde ni se duplica | 23 | 23 | ✔ |
| Sin repartidores todo queda sin asignar | 23 | 23 | ✔ |

Además, en cada instancia medida se comprueba que cada parada aparece exactamente una vez y que ningún método mejora al exacto. Las pruebas automáticas del servicio están en `servicios/pruebas/test_unitarias_ola2.py` y `test_ola2.py`.

## 9. Métricas

- **Distancia total (km)** frente al orden de llegada (lo que se haría sin algoritmo) y frente al óptimo (brecha %).
- **Instancias resueltas óptimamente.**
- **Tiempo de cálculo (ms, mediana).**
- En operación: minutos de la ruta, costo y pedidos sin asignar.

## 10. Tiempos y calidad medidos

Domicilios aleatorios (semilla fija) a menos de 1.4 km del microhub; 20 instancias por tamaño (5 desde 30 paradas; 3 en el exacto con 9).

| Paradas | Exacto (ms) | Vecino (ms) | Vecino + 2-opt (ms) | Km llegada | Km 2-opt | Ahorro vs llegada | Brecha vecino | Brecha 2-opt | 2-opt óptimo |
|---|---|---|---|---|---|---|---|---|---|
| 3 | 0.02 | 0.009 | 0.025 | 3.10 | 2.72 | 12.4 % | 2.8 % | 0.2 % | 19 de 20 |
| 5 | 0.62 | 0.021 | 0.140 | 6.49 | 4.32 | 33.4 % | 7.6 % | 0.7 % | 16 de 20 |
| 7 | 39.25 | 0.042 | 0.286 | 9.34 | 5.46 | 41.5 % | 3.8 % | 1.3 % | 12 de 20 |
| 8 | 385.09 | 0.054 | 0.570 | 10.70 | 5.68 | 46.9 % | 10.0 % | 0.9 % | 16 de 20 |
| 9 | 3,913.01 | 0.090 | 1.291 | 10.17 | 6.14 | 39.7 % | 1.0 % | 0.2 % | 2 de 3 |
| 12 | — | 0.153 | 2.746 | 15.51 | 7.05 | 54.5 % | — | — | — |
| 20 | — | 0.273 | 12.663 | 25.77 | 9.47 | 63.2 % | — | — | — |
| 30 | — | 0.453 | 40.780 | 40.25 | 11.80 | 70.7 % | — | — | — |
| 50 | — | 1.206 | 265.676 | 65.72 | 14.28 | 78.3 % | — | — | — |

**Lectura.**

- Con 9 paradas el exacto tarda 3,913 ms y 2-opt 1.29 ms: unas 3,032 veces menos.
- La brecha media de vecino + 2-opt respecto del óptimo está entre 0.2 % y 1.3 %.
- Frente a visitar en orden de llegada, ordenar ahorra 78 % de distancia con 50 paradas.

## 11. Limitaciones

- Las distancias son de línea recta por un factor de rodeo: no usa calles, sentidos ni tráfico.
- No considera ventanas de horario, capacidad en peso o volumen ni prioridades.
- La asignación a repartidores es voraz: agrupa por zona y balancea, no optimiza la suma de las rutas.
- 2-opt es una búsqueda local: puede quedarse en un óptimo local y su costo cúbico lo limita a decenas de paradas.
- No incluye el regreso al microhub ni reoptimiza solo cuando cambia algo: los ajustes se piden (`/rutas/planes/{id}/ajustes`).

**Mejoras posibles:** distancias reales con un motor de calles, evaluar el cambio de cada inversión en O(1) (2-opt incremental), Or-opt o 3-opt y optimizar la asignación entre repartidores.
