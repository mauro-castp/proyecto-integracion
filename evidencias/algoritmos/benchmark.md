# Benchmark de algoritmos

Generado por `servicios/pruebas/benchmark_algoritmos.py`. Equipo: x86_64, Python 3.13.18, 2 CPU.

## Ruteo de paradas

Tiempo (mediana, ms) y distancia contra el óptimo (TSP exacto). Paradas al azar dentro de 2 km del MH-01.

| Paradas | Casos | Exacto (ms) | Vecino (ms) | Vecino + 2-opt (ms) | Brecha vecino (prom / máx) | Brecha 2-opt (prom / máx) | 2-opt da el óptimo | 2-opt mejora al vecino |
|---|---|---|---|---|---|---|---|---|
| 3 | 20 | 0.01 | 0.004 | 0.014 | 2.18 % / 11.16 % | 0.0 % / 0.0 % | 100 % | 2.03 % |
| 4 | 20 | 0.04 | 0.006 | 0.033 | 6.3 % / 21.34 % | 0.0 % / 0.0 % | 100 % | 5.46 % |
| 5 | 20 | 0.28 | 0.009 | 0.062 | 5.05 % / 26.43 % | 1.0 % / 4.4 % | 60 % | 3.49 % |
| 6 | 20 | 1.99 | 0.012 | 0.103 | 7.57 % / 16.45 % | 1.96 % / 10.46 % | 60 % | 5.01 % |
| 7 | 20 | 16.57 | 0.019 | 0.131 | 5.9 % / 23.23 % | 0.07 % / 0.97 % | 90 % | 5.06 % |
| 8 | 20 | 154.17 | 0.028 | 0.259 | 6.74 % / 28.29 % | 1.27 % / 9.76 % | 65 % | 4.85 % |
| 9 | 5 | 1646.72 | 0.035 | 0.295 | 8.19 % / 16.4 % | 2.51 % / 6.28 % | 60 % | 5.02 % |
| 10 | 20 | — | 0.029 | 0.538 | — | — | — | 7.62 % |
| 12 | 20 | — | 0.04 | 0.859 | — | — | — | 3.97 % |
| 15 | 20 | — | 0.06 | 1.699 | — | — | — | 6.61 % |
| 20 | 20 | — | 0.102 | 5.853 | — | — | — | 7.12 % |
| 30 | 20 | — | 0.229 | 19.95 | — | — | — | 7.94 % |
| 40 | 20 | — | 0.367 | 44.227 | — | — | — | 10.97 % |
| 50 | 20 | — | 0.552 | 109.378 | — | — | — | 9.58 % |
| 60 | 20 | — | 0.848 | 179.149 | — | — | — | 8.83 % |

## Simulación Monte Carlo

### Tiempo de ejecución

| Réplicas | Días | Tiempo (ms) | µs por réplica-día |
|---|---|---|---|
| 50 | 30 | 3.5 | 2.35 |
| 50 | 90 | 9.6 | 2.13 |
| 100 | 30 | 8.2 | 2.72 |
| 100 | 90 | 22.8 | 2.54 |
| 200 | 30 | 16.4 | 2.74 |
| 200 | 90 | 48.9 | 2.71 |
| 500 | 30 | 43.4 | 2.89 |
| 500 | 90 | 113.9 | 2.53 |
| 1000 | 30 | 80.7 | 2.69 |
| 1000 | 90 | 265.4 | 2.95 |
| 2000 | 30 | 172.0 | 2.87 |
| 2000 | 90 | 451.4 | 2.51 |

### Estabilidad (10 semillas distintas)

| Réplicas | Utilidad media (promedio) | Desviación entre semillas | Variación |
|---|---|---|---|
| 50 | -50,716 | 41 | 0.08 % |
| 200 | -50,715 | 22 | 0.04 % |
| 1000 | -50,711 | 10 | 0.02 % |

Reproducibilidad: misma entrada y semilla → misma huella: **sí** (c94e5cd8c00a78c1…); otra semilla → otra huella: **sí**.

### Casos de prueba (500 réplicas de 30 días)

| Escenario | Utilidad media | P10 | P90 | Prob. de pérdida | Días saturados | Capacidad/día |
|---|---|---|---|---|---|---|
| Base del equipo (60 pedidos/día, ticket 135, margen 28 %) | -50,732 | -51,103 | -50,364 | 100.0 % | 1.0 % | 164 |
| Demanda en el equilibrio estimado (385 pedidos/día) | -36,288 | -37,058 | -35,550 | 100.0 % | 100.0 % | 164 |
| Sin ausentismo ni variación | -50,716 | -50,999 | -50,411 | 100.0 % | 0.0 % | 164 |
| Ausentismo alto (20 %) | -50,996 | -51,467 | -50,572 | 100.0 % | 13.6 % | 164 |
| Margen bruto 40 % y 150 pedidos/día | 27,391 | 24,442 | 30,439 | 0.0 % | 67.4 % | 164 |
