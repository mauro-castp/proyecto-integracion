# Algoritmos complejos de la plataforma

El proyecto tiene dos algoritmos principales. Cada uno se documenta con los 11 puntos que piden los lineamientos: problema,
entradas, salidas, variables, restricciones, complejidad, pseudocódigo, casos de prueba, métricas, limitaciones y tiempo de ejecución.

1. **Planeación de rutas de reparto** (servicio `rutas`, :5118). Agrupa los pedidos por zona, balancea la carga entre los repartidores
   y ordena las paradas con TSP exacto o con vecino más cercano + 2-opt. Es el principal.
2. **Simulación Monte Carlo de la operación** (servicio `simulacion`, :5121). Estima la utilidad y el riesgo de un microhub cuando
   varían la demanda y el personal.

Además hay otros algoritmos de apoyo que no se documentan aquí con el mismo detalle: clasificación ABC y recomendación de surtido con
restricciones de espacio y presupuesto (`surtido`), proyección de demanda con banda de error (`demanda`), cuello de botella de
capacidad (`capacidad`) y resolución de conflictos de sincronización (`sincronizacion`).

Para reproducir los números: `python servicios/pruebas/benchmark_algoritmos.py`. No necesita bases de datos. Resultados en
[`evidencias/algoritmos/benchmark.md`](../evidencias/algoritmos/benchmark.md).

---

## 1. Planeación de rutas de reparto

### 1.1 Problema que resuelve

Cada microhub tiene en un momento dado *n* pedidos listos para salir y *m* repartidores disponibles. Hay que decidir **quién lleva
qué** y **en qué orden**, para que la distancia total sea corta y ninguna ruta pase de la promesa de entrega (30 min). Es una variante
del problema de ruteo de vehículos (VRP). Ordenar las paradas de un repartidor es un **problema del agente viajero (TSP)** de camino
abierto: sale del microhub y no regresa. Ese problema es NP-difícil.

Sin este algoritmo, el repartidor saldría en el orden “de llegada” de los pedidos. Con 50 casos al azar dentro de 2 km del MH-01,
la ruta óptima recorre en promedio **24 % menos con 4 paradas, 36 % menos con 6 y 40 % menos con 8**, comparada con el orden de
llegada. El servicio reporta esta mejora en cada comparación (`POST /rutas/comparaciones`, campo `mejora_pct`).

### 1.2 Entradas

| Entrada | Origen | Ejemplo |
|---|---|---|
| Microhub de salida (lat, lng) | servicio `microhubs` | MH-01 (25.748, −100.364) |
| Pedidos listos: id, folio, zona, lat, lng | `GET pedidos/listos` (servicio `pedidos`) | 12 pedidos de 3 zonas |
| Repartidores activos: id, nombre | `GET entregas/repartidores` | 2 repartidores |
| Método (opcional) | quien planea | `automatico` (por omisión), `vecino`, `2opt`, `exacto` |
| Supuestos | `configuracion` + `supuesto_documentado` | ver 1.4 |

### 1.3 Salidas

Un **plan** (`POST /rutas/planes`), propuesto o guardado. Contiene:

- una **ruta** por repartidor, con sus paradas en orden, el tramo y los minutos acumulados de cada parada, la distancia, el tiempo y el costo;
- los pedidos **sin asignar** (no cupieron en los topes);
- los **totales** y los **supuestos usados**;
- al confirmar: las filas en `plan_ruta` y la asignación de la entrega a cada repartidor.

### 1.4 Variables y supuestos (todos en `configuracion`, documentados en `servicios/SUPUESTOS.md`)

| Variable | Valor | Uso |
|---|---|---|
| `max_paradas_repartidor` | 8 | tope de paradas por repartidor |
| `factor_rodeo_distancia` | 1.3 | distancia por calle = línea recta × 1.3 |
| `velocidad_reparto_kmh` | 22 km/h | minutos de cada tramo |
| `tiempo_servicio_min` | 4 min | tiempo en cada parada |
| `costo_km_reparto` | 4.5 MXN | costo variable por km |
| `costo_base_entrega` | 18 MXN | costo fijo por entrega |
| `cob_tiempo_max_min` | 30 min | promesa: paradas fuera de promesa |
| *d(a, b)* | Haversine | distancia en línea recta entre coordenadas |

### 1.5 Restricciones

- Cada pedido va **en una sola ruta** o queda en `sin_asignar`. Nunca va en dos.
- Ningún repartidor pasa de `max_paradas_repartidor` paradas.
- Se intenta que los pedidos de una **misma zona** vayan con el mismo repartidor, en trozos del tamaño del tope.
- El método exacto solo se acepta hasta **9 paradas** (`MAX_EXACTO`); en modo automático se usa hasta 8.
- Solo pedidos en estado listo del microhub que se planea. El operador solo planea su microhub (RN22).
- La ruta no incluye el regreso al microhub (camino abierto).

### 1.6 Pseudocódigo

```
PLANEAR(origen, pedidos, repartidores, método, p):
    // 1. Agrupar y balancear (planeacion_calc.asignar_repartidores)
    trozos ← []
    para cada zona z con sus pedidos L_z:
        partir L_z en trozos de tamaño ≤ p.max_paradas
    ordenar trozos de mayor a menor tamaño
    carga[r] ← [] para cada repartidor r ; sin_asignar ← []
    para cada trozo t:
        r ← repartidor con menos paradas tal que |carga[r]| + |t| ≤ tope
        si existe r: carga[r] ← carga[r] ∪ t
        si no: para cada pedido x de t:
                   r ← repartidor menos cargado con |carga[r]| < tope
                   si existe r: agregar x a carga[r]   si no: agregar x a sin_asignar

    // 2. Ordenar las paradas de cada repartidor
    para cada r con carga[r] ≠ ∅:
        n ← |carga[r]|
        si método = exacto o (automático y n ≤ 8): orden ← TSP_EXACTO(origen, carga[r])
        si método = vecino:                        orden ← VECINO(origen, carga[r])
        en otro caso:                              orden ← DOS_OPT(origen, carga[r], VECINO(origen, carga[r]))
        calcular distancia·rodeo, minutos acumulados (tramo/velocidad + servicio) y costo
    regresar rutas, sin_asignar, totales

VECINO(o, P):                          // vecino más cercano
    actual ← o ; orden ← []
    mientras queden paradas: j ← la más cercana a actual ; agregar j ; actual ← j
    regresar orden

DOS_OPT(o, P, orden):                  // mejora local
    repetir
        mejora ← falso
        para i en 0..n−2, para j en i+1..n−1:
            candidato ← orden con el segmento [i..j] invertido
            si D(candidato) < D(orden): orden ← candidato ; mejora ← verdadero
    hasta que no haya mejora
    regresar orden

TSP_EXACTO(o, P):
    regresar la permutación de P con menor D (prueba las n! permutaciones)
```

Código: `sistema_web/planeacion_calc.py` (`asignar_repartidores`, `vecino_mas_cercano`, `dos_opt`, `tsp_exacto`, `distancia_ruta`).
El servicio lo usa en `servicios/rutas/app.py` (`ordenar`, `metricas`, `armar_plan`), con las mismas funciones que el portal.

### 1.7 Complejidad

| Paso | Tiempo | Espacio |
|---|---|---|
| Agrupar y balancear | O(n log n + t · m log m), con t trozos ≈ n / tope | O(n + m) |
| Distancia de un orden `D` | O(n) | O(n) |
| Vecino más cercano | **O(n²)** | O(n) |
| 2-opt (esta implementación) | **O(n³) por pasada**: n²/2 candidatos × D en O(n); en la práctica se necesitan pocas pasadas | O(n) |
| TSP exacto | **O(n! · n)** | O(n) |

Con los topes del negocio (≤ 8 paradas por repartidor), el exacto se resuelve en ~170 ms. Por eso el modo automático da el óptimo en la
operación normal y solo usa la heurística cuando alguien sube el tope.

### 1.8 Casos de prueba

Pruebas automáticas:

- `servicios/pruebas/test_unitarias_ola2.py`, clase `Rutas` (sin base de datos):
  - el exacto nunca es peor que los demás;
  - 2-opt nunca empeora al vecino más cercano;
  - el exacto se rechaza con demasiadas paradas;
  - sin paradas;
  - las métricas aplican rodeo, velocidad, servicio y costo;
  - los minutos acumulados crecen parada a parada;
  - cada pedido va en una sola ruta;
  - lo que no cabe en los topes queda sin asignar;
  - la comparación mide la mejora contra el orden de llegada.
- `servicios/pruebas/test_ola2.py` (contra PostgreSQL real):
  - cada pedido listo queda en una sola ruta;
  - comparar métodos;
  - proponer, guardar, confirmar y dejar las rutas en la base;
  - cancelar;
  - ajustes ante incidencias;
  - ajustar un plan confirmado;
  - el operador planea solo su microhub.

Casos límite cubiertos:

| Caso | Resultado esperado |
|---|---|
| 0 paradas | ruta vacía, distancia 0 |
| 1 parada | un tramo, el único orden posible |
| Más pedidos que repartidores × tope | el excedente queda en `sin_asignar` (no se pierde) |
| `metodo=exacto` con 10 paradas | 422 «solo se usa hasta 9 paradas» |
| Sin repartidores | todo en `sin_asignar` |
| Pedido que no está listo o es de otro microhub | 422 con el pedido señalado |

### 1.9 Métricas

- **Calidad**: brecha contra el óptimo = (D(heurística) − D(exacto)) / D(exacto), y mejora contra el orden de llegada (la reporta el
  servicio en `mejora_pct`).
- **Servicio**: minutos de la última parada contra la promesa de 30 min (`paradas_fuera_de_promesa`).
- **Costo**: km × costo por km + costo base por entrega.
- **Tiempo de cómputo**: ver 1.11.

Resultados del benchmark (paradas al azar dentro de 2 km del MH-01; 20 casos por tamaño, 5 con 9 paradas):

| Paradas | Brecha del vecino (prom. / máx.) | Brecha del vecino + 2-opt (prom. / máx.) | 2-opt encuentra el óptimo |
|---|---|---|---|
| 4 | 6.3 % / 21.3 % | 0 % / 0 % | 100 % |
| 6 | 7.6 % / 16.5 % | 2.0 % / 10.5 % | 60 % |
| 8 | 6.7 % / 28.3 % | 1.3 % / 9.8 % | 65 % |
| 9 | 8.2 % / 16.4 % | 2.5 % / 6.3 % | 60 % |

Para 10 a 60 paradas, donde ya no hay óptimo con qué comparar, 2-opt acorta la ruta del vecino más cercano entre **4 % y 11 %**.

### 1.10 Limitaciones

- **Distancia en línea recta × factor de rodeo** (1.3). No usa calles reales, sentidos ni tráfico. Para eso habría que consultar una
  matriz de distancias (OSRM o Google Distance Matrix).
- El balanceo es **voraz** (primero los trozos grandes). No es un VRP óptimo y puede dejar a un repartidor con más km que otro aunque
  tengan el mismo número de paradas.
- No hay **ventanas de tiempo** por cliente ni capacidad de carga en kg o volumen. Las paradas solo se limitan por número.
- El 2-opt recalcula la distancia completa de cada candidato (O(n) cada uno). Con evaluación por diferencia, que solo cambia dos
  tramos, bajaría a O(n²) por pasada. Hoy no hace falta, porque con 60 paradas tarda 188 ms.
- El exacto crece factorialmente: 9 paradas tardan 1.65 s; 10 tardarían unos 18 s. Por eso hay un tope.

### 1.11 Tiempo de ejecución (mediana, Python 3.13, 1 núcleo)

| Paradas | Exacto | Vecino | Vecino + 2-opt |
|---|---|---|---|
| 5 | 0.3 ms | 0.01 ms | 0.06 ms |
| 7 | 19 ms | 0.02 ms | 0.13 ms |
| 8 | **171 ms** | 0.03 ms | 0.28 ms |
| 9 | **1 651 ms** | 0.03 ms | 0.32 ms |
| 20 | — | 0.10 ms | 6 ms |
| 40 | — | 0.39 ms | 56 ms |
| 60 | — | 0.86 ms | 188 ms |

El salto de 8 a 9 paradas (× 9.7) confirma el crecimiento factorial. El de 30 a 60 paradas en 2-opt (× 9.6 al duplicar *n*) es
consistente con O(n³) por pasada.

---

## 2. Simulación Monte Carlo de la operación de un microhub

### 2.1 Problema que resuelve

El punto de equilibrio dice cuántos pedidos hacen falta *en promedio*. Pero la demanda varía de un día a otro y el personal falta.
La simulación responde **qué tan probable es perder dinero** y **cuántos días se satura** el microhub con esa variación. Es la base
de la decisión humana de abrir o mantener un microhub.

### 2.2 Entradas

La “foto de entrada” que arma el servicio pidiendo datos a `punto-equilibrio` (que a su vez consulta costos, demanda y cobertura) y a
`capacidad`. Se guarda junto con la ejecución.

| Variable | Ejemplo |
|---|---|
| `pedidos_dia` (demanda esperada) | 60 |
| `indice_semanal[7]` (de `demanda/patrones`) | 0.9 … 1.25 |
| `variacion_demanda` (desviación del ruido) | 0.10 |
| `ticket`, `margen_bruto`, `costo_variable_pedido` | 135, 0.28, 32.6 |
| `costos_fijos_mes`, `dias_mes` | 60 000, 30 |
| `operadores`, `repartidores`, `ausentismo` | 3, 3, 0.05 |
| `distancia_km`, `horas`, `capacidad_fisica`, modelo de capacidad | 2.4, 10, —, tiempos de picking/empaque/despacho |
| `dias`, `replicas`, `semilla` | 30, 200, 2026 |

### 2.3 Salidas

- Por cada métrica (utilidad, ingreso, atendidos, rechazados, demanda, utilización y días saturados): media, P10, P50, P90, mínimo y máximo.
- **Probabilidad de pérdida** (% de réplicas con utilidad < 0) y **% de días saturados**.
- Una serie día por día (demanda media, atendidos y utilidad acumulada).
- El **contraste** contra el escenario sin variación.
- Una **lectura** en palabras.
- La **huella** SHA-256 de los resultados.

### 2.4 Variables internas

Para cada réplica *r* y día *d*:

- índice *I(d)*;
- ruido ε ~ N(1, σ), con un mínimo de 0.2;
- demanda D ~ Poisson(pedidos_dia · I(d) · ε);
- personal presente O, R ~ Binomial(n, 1 − ausentismo);
- capacidad C(O, R), guardada en una tabla porque hay pocas combinaciones;
- atendidos A = min(D, C);
- utilidad U = A · (ticket · margen − costo_variable) − fijos / días_mes.

### 2.5 Restricciones

- 1 ≤ `dias` ≤ 365; 10 ≤ `replicas` ≤ 2 000; 0 ≤ `ausentismo` ≤ 0.5; 0 ≤ `variacion_demanda` ≤ 1 (validados al recibir la petición).
- **Reproducible**: cada réplica usa su propio generador `Random(semilla · 1 000 003 + r)`. Así, la misma entrada con la misma semilla da
  la misma huella, y agregar réplicas no cambia las anteriores.
- **Asíncrona**: `POST /simulacion/ejecuciones` responde 202 y un hilo toma la ejecución de la cola (`FOR UPDATE SKIP LOCKED`). Si se
  queda a medias, regresa a la cola a los 5 min y falla tras 3 intentos. Se puede cancelar (se revisa cada 25 réplicas).
- Si un servicio de apoyo no responde, **no se encola nada** (503).

### 2.6 Pseudocódigo

```
SIMULAR(e, semilla, réplicas):
    caps ← tabla vacía                                   // capacidad por (operadores, repartidores)
    para r en 0..réplicas−1:
        rng ← Random(semilla · 1 000 003 + r)
        tot ← 0 ; serie_r ← []
        para d en 0..e.dias−1:
            I ← e.indice_semanal[(e.dia_inicio − 1 + d) mod 7]
            ε ← max(Normal(1, e.variacion), 0.2)
            D ← Poisson(e.pedidos_dia · I · ε)             // Knuth si media < 30; si no, aproximación normal
            O ← #{operadores que no faltan} ; R ← #{repartidores que no faltan}
            C ← caps[O,R] (o se calcula con capacidad(O, R, …) y se guarda)
            A ← min(D, C) ; U ← A·(ticket·margen − cv) − fijos/días_mes
            acumular tot y serie_r ; si D > C · umbral_riesgo: día saturado
        guardar tot
    para cada métrica: ordenar los valores de las réplicas → media, P10, P50, P90 (interpolación lineal)
    prob_pérdida ← % réplicas con utilidad < 0
    contraste ← utilidad con demanda media, sin ruido ni ausentismo
    huella ← SHA-256(JSON canónico de los resultados)
```

### 2.7 Complejidad

- Tiempo: **O(réplicas · días · (operadores + repartidores))** para simular, más **O(K · réplicas log réplicas)** para los percentiles
  de las K = 7 métricas.
- Memoria: O(réplicas + días).

Poisson con Knuth es O(media) para medias menores a 30. Arriba de eso se usa la aproximación normal, que es O(1).

### 2.8 Casos de prueba

Pruebas automáticas:

- `test_unitarias_ola2.py`, clase `Simulacion` (13 pruebas):
  - misma entrada y semilla, misma huella;
  - otra semilla, otro resultado;
  - cambiar un dato cambia la huella;
  - agregar réplicas no cambia las anteriores;
  - sin variación ni ausentismo, el resultado es el de la cuenta directa;
  - si falta capacidad, se rechaza;
  - si falta todo el personal, no se atiende nada;
  - los percentiles están ordenados;
  - se puede cancelar a la mitad;
  - el percentil se interpola;
  - Poisson tiene la media pedida;
  - la serie trae un renglón por día;
  - el contraste.
- `test_ola2.py`: la ejecución asíncrona, repetir, comparar y cancelar contra la base real.

Escenarios del benchmark (500 réplicas de 30 días):

| Escenario | Utilidad media del mes | P10 / P90 | Prob. de pérdida | Días saturados |
|---|---|---|---|---|
| Base del equipo (60 pedidos/día, ticket 135, margen 28 %) | −50 732 | −51 103 / −50 364 | 100 % | 1 % |
| Demanda de 385 pedidos/día (el equilibrio teórico) | −36 288 | −37 058 / −35 550 | 100 % | 100 % |
| Ausentismo de 20 % | −50 996 | −51 467 / −50 572 | 100 % | 13.6 % |
| Margen de 40 % y 150 pedidos/día | **+27 391** | 24 442 / 30 439 | **0 %** | 67.4 % |

Lectura: con los supuestos actuales el microhub no es viable. Aunque llegara la demanda del equilibrio teórico (385 pedidos), la
capacidad de 164 pedidos/día lo impide. Solo con más margen y cerca del tope de capacidad se vuelve rentable, a costa de saturarse dos
de cada tres días.

### 2.9 Métricas

- **Estabilidad**: con 10 semillas distintas, la utilidad media varía 0.08 % con 50 réplicas, 0.04 % con 200 y 0.02 % con 1 000. Por
  eso 200 réplicas (el valor por omisión) es un buen equilibrio entre precisión y tiempo.
- **Reproducibilidad**: la misma semilla da la misma huella (comprobado) y otra semilla da otra huella.
- **Contraste**: la diferencia entre la utilidad media simulada y la cuenta sin variación cuantifica el costo de la incertidumbre.

### 2.10 Limitaciones

- La demanda diaria es **independiente** entre días, salvo el índice semanal: no modela rachas ni estacionalidad mensual.
- El ausentismo es **independiente** por persona: no modela que falten varios el mismo día por una causa común.
- Los costos fijos se reparten por día del mes; no hay costos escalonados (por ejemplo, contratar un repartidor extra al saturarse).
- La capacidad es un número por día, sin horas pico. Un día puede no saturarse en total y aun así incumplir la promesa en la tarde.
- Los supuestos son “supuesto”, no “medido” (`supuesto_documentado`): el resultado es tan bueno como esos valores.

### 2.11 Tiempo de ejecución (Python 3.13, 1 núcleo)

| Réplicas | 30 días | 90 días |
|---|---|---|
| 50 | 4.5 ms | 10.5 ms |
| 200 | 17.6 ms | 47.3 ms |
| 1 000 | 84 ms | 239 ms |
| 2 000 | 176 ms | 475 ms |

Unos **2.6–2.9 µs por réplica-día**, lineal en réplicas × días, como predice el análisis. Corre en segundo plano, así que no bloquea la
petición: en la prueba de carga, `POST /simulacion/ejecuciones` responde 202 con una mediana de 160–230 ms.
