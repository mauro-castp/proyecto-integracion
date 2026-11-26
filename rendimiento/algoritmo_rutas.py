"""
algoritmo_rutas.py — Mide el algoritmo de asignación y ordenamiento de rutas (las funciones que usa el servicio de rutas y el portal) y escribe
entrega/ALGORITMO_RUTAS.md: problema, entradas, salidas, variables, restricciones, complejidad, pseudocódigo, casos de prueba, métricas,
limitaciones y tiempos medidos.

  python rendimiento/algoritmo_rutas.py          (desde la raíz; no necesita bases de datos)
"""
import datetime as dt
import math
import platform
import random
import statistics
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "sistema_web"))
import planeacion_calc as pc  # noqa: E402

ORIGEN = (25.7491, -100.3611)                    # Microhub San Bernabé Centro (aprox.)
TAMANOS = [3, 5, 7, 8, 9, 12, 20, 30, 50]
INSTANCIAS = 20


def instancia(n, semilla):
    rnd = random.Random(semilla)
    return [{"id": i, "zona_id": 1 + i % 4, "zona": f"Z{1 + i % 4}", "lat": ORIGEN[0] + rnd.uniform(-0.012, 0.012), "lng": ORIGEN[1] + rnd.uniform(-0.012, 0.012)}
            for i in range(n)]


def medir(fn):
    t = time.perf_counter()
    r = fn()
    return (time.perf_counter() - t) * 1000, r


def correr():
    filas = []
    for n in TAMANOS:
        reps = INSTANCIAS if n <= 20 else 5
        acumulado = {m: {"ms": [], "km": []} for m in ("llegada", "vecino", "2opt", "exacto")}
        for s in range(reps):
            p = instancia(n, 1000 * n + s)
            metodos = {"llegada": lambda: list(range(n)), "vecino": lambda: pc.vecino_mas_cercano(ORIGEN, p),
                       "2opt": lambda: pc.dos_opt(ORIGEN, p, pc.vecino_mas_cercano(ORIGEN, p))}
            if n <= 9 and (n < 9 or s < 3):
                metodos["exacto"] = lambda: pc.tsp_exacto(ORIGEN, p)
            for nombre, f in metodos.items():
                ms, orden = medir(f)
                assert sorted(orden) == list(range(n)), "cada parada se visita exactamente una vez"
                acumulado[nombre]["ms"].append(ms)
                acumulado[nombre]["km"].append(pc.distancia_ruta(ORIGEN, p, orden)[0])
        fila = {"n": n, "instancias": reps}
        for m, v in acumulado.items():
            if v["ms"]:
                fila[m] = {"ms": statistics.median(v["ms"]), "km": statistics.mean(v["km"][: len(v["ms"])]), "k": len(v["ms"])}
        # brecha contra el óptimo en las MISMAS instancias que se resolvieron exactas
        if "exacto" in fila:
            k = fila["exacto"]["k"]
            for m in ("vecino", "2opt"):
                brechas = [100 * (a - b) / b for a, b in zip(acumulado[m]["km"][:k], acumulado["exacto"]["km"][:k])]
                assert min(brechas) > -1e-6, "ningún método puede mejorar al exacto"
                fila[m]["brecha"] = statistics.mean(brechas)
                fila[m]["optimas"] = sum(b < 1e-6 for b in brechas)
        filas.append(fila)
        print(f"  n={n} listo", flush=True)
    return filas


def casos_de_prueba():
    """Casos con resultado conocido; se comprueban cada vez que se genera el documento."""
    linea = [{"lat": ORIGEN[0] + 0.001 * k, "lng": ORIGEN[1], "id": k, "zona_id": 1, "zona": "Z"} for k in (3, 1, 4, 2)]
    casos = []

    def caso(nombre, esperado, obtenido):
        casos.append((nombre, esperado, obtenido, esperado == obtenido))
    caso("Sin paradas", [], pc.tsp_exacto(ORIGEN, []) or [])
    caso("Una parada", [0], pc.tsp_exacto(ORIGEN, linea[:1]))
    caso("Cuatro paradas en línea recta: se visitan de la más cercana a la más lejana (exacto)", [1, 3, 0, 2], pc.tsp_exacto(ORIGEN, linea))
    caso("Las mismas con vecino más cercano", [1, 3, 0, 2], pc.vecino_mas_cercano(ORIGEN, linea))
    caso("2-opt corrige un orden malo hasta el óptimo", [1, 3, 0, 2], pc.dos_opt(ORIGEN, linea, [2, 1, 0, 3]))
    pedidos = instancia(23, 7)
    r = pc.asignar_repartidores(pedidos, [{"id": 1, "nombre": "A"}, {"id": 2, "nombre": "B"}], ORIGEN, {"max_paradas_repartidor": 10})
    asignadas = [x["id"] for ruta in r["rutas"] for x in ruta["paradas"]]
    caso("Reparto: ningún repartidor pasa del tope de 10 paradas", True, all(len(x["paradas"]) <= 10 for x in r["rutas"]))
    caso("Reparto: 23 pedidos y 2 repartidores dejan 3 sin asignar", 3, len(r["sin_asignar"]))
    caso("Reparto: ningún pedido se pierde ni se duplica", 23, len(set(asignadas) | {x["id"] for x in r["sin_asignar"]}))
    caso("Sin repartidores todo queda sin asignar", 23, len(pc.asignar_repartidores(pedidos, [], ORIGEN)["sin_asignar"]))
    return casos


def f(v, d=2):
    return f"{v:,.{d}f}"


def documento(filas, casos):
    out = ["# Algoritmo de asignación y ordenamiento de rutas de reparto", "",
           f"Generado por `rendimiento/algoritmo_rutas.py` el {dt.date.today().isoformat()} en {platform.machine()}, Python {platform.python_version()}. "
           "El código medido es `sistema_web/planeacion_calc.py`, el mismo que usan el servicio de rutas (puerto 5118) y el portal.", "",
           "## 1. Problema", "",
           "Un microhub tiene pedidos listos para salir y varios repartidores. Hay que decidir **qué repartidor lleva cada pedido** y **en qué orden visita** "
           "sus domicilios para recorrer poca distancia, sin pasar del máximo de paradas por repartidor. Ordenar las paradas es el problema del agente viajero "
           "(ruta abierta: no se regresa al microhub); asignar y ordenar a la vez es un problema de ruteo de vehículos, que es NP-difícil.", "",
           "## 2. Entradas", "", "| Entrada | Origen |", "|---|---|",
           "| Punto de salida (latitud, longitud) del microhub | servicio de microhubs |", "| Pedidos listos: id, zona y coordenadas del domicilio | pedidos (`/pedidos/listos`) |",
           "| Repartidores activos | entregas (`/entregas/repartidores`) |", "| Parámetros: tope de paradas, velocidad, tiempo por parada, factor de rodeo, costos | `configuracion` (con su justificación en `supuesto_documentado`) |", "",
           "## 3. Salidas", "", "Por repartidor: orden de las paradas, distancia por tramo y total (km), minutos acumulados por parada, costo y zonas. Además, los pedidos que no cupieron (`sin_asignar`).", "",
           "## 4. Variables", "", "| Símbolo | Significado | Valor por omisión |", "|---|---|---|", "| n | paradas de un repartidor | — |", "| P | pedidos listos | — |", "| R | repartidores | — |",
           f"| T | tope de paradas por repartidor (`max_paradas_repartidor`) | {int(pc.con_defecto(None)['max_paradas_repartidor'])} |",
           f"| v | velocidad de reparto (km/h) | {pc.con_defecto(None)['velocidad_reparto_kmh']} |", f"| s | minutos por parada | {pc.con_defecto(None)['tiempo_servicio_min']} |",
           "| ρ | factor de rodeo: distancia por calle ÷ línea recta | 1.3 |", "| d(a, b) | distancia de haversine entre dos puntos | — |", "",
           "Distancia de una ruta: `ρ · Σ d(parada anterior, parada)`. Minutos: `distancia ÷ v · 60 + n · s`. Costo: `km · costo_km + n · costo_base_entrega`.", "",
           "## 5. Restricciones", "", "1. Cada pedido se asigna a lo sumo a un repartidor y se visita una sola vez.", "2. Ningún repartidor recibe más de T paradas; lo que no cabe queda sin asignar y se informa.",
           "3. Los pedidos de una misma zona se mantienen juntos mientras quepan en un repartidor.", "4. La ruta empieza en el microhub y no incluye el regreso.",
           "5. El método exacto solo se permite hasta 9 paradas (422 con más).", "",
           "## 6. Método y pseudocódigo", "", "```text", "asignar(pedidos, repartidores, T):",
           "    trozos ← agrupar pedidos por zona y partir cada grupo en bloques de a lo sumo T", "    ordenar trozos de mayor a menor",
           "    para cada trozo:", "        r ← repartidor con menos paradas donde quepa completo", "        si existe: darle el trozo",
           "        si no: repartir sus pedidos uno por uno entre los menos cargados con lugar; el resto queda sin asignar",
           "    para cada repartidor con paradas: orden ← ordenar(sus paradas)", "",
           "ordenar(paradas):", "    si n ≤ 8: devolver exacto(paradas)", "    si no:    devolver dos_opt(vecino_mas_cercano(paradas))", "",
           "exacto(paradas):                    # prueba las n! permutaciones", "    mejor ← permutación de menor distancia", "",
           "vecino_mas_cercano(paradas):", "    actual ← microhub", "    mientras queden pendientes:", "        j ← pendiente más cercano a actual; agregar j; actual ← j", "",
           "dos_opt(orden):", "    repetir", "        para cada par i < j:", "            candidato ← orden con el tramo i..j invertido",
           "            si distancia(candidato) < distancia(orden): orden ← candidato", "    hasta que una pasada completa no mejore", "```", "",
           "## 7. Complejidad", "", "| Paso | Tiempo | Espacio |", "|---|---|---|", "| Agrupar y repartir | O(P log P + P·R log R) | O(P) |",
           "| Exacto | O(n! · n) | O(n) |", "| Vecino más cercano | O(n²) | O(n) |", "| 2-opt | O(k · n³): cada pasada prueba O(n²) inversiones y mide cada una en O(n); k = pasadas hasta no mejorar | O(n) |", "",
           "El umbral de 8 paradas sale de las mediciones de abajo: el exacto crece de forma factorial y a partir de 9 deja de ser razonable para responder una petición.", "",
           "## 8. Casos de prueba", "", "| Caso | Esperado | Obtenido | Resultado |", "|---|---|---|---|"]
    out += [f"| {n} | {e} | {o} | {'✔' if ok else '✘'} |" for n, e, o, ok in casos]
    out += ["", "Además, en cada instancia medida se comprueba que cada parada aparece exactamente una vez y que ningún método mejora al exacto. Las pruebas automáticas del "
            "servicio están en `servicios/pruebas/test_unitarias_ola2.py` y `test_ola2.py`.", "",
            "## 9. Métricas", "", "- **Distancia total (km)** frente al orden de llegada (lo que se haría sin algoritmo) y frente al óptimo (brecha %).",
            "- **Instancias resueltas óptimamente.**", "- **Tiempo de cálculo (ms, mediana).**", "- En operación: minutos de la ruta, costo y pedidos sin asignar.", "",
            "## 10. Tiempos y calidad medidos", "", f"Domicilios aleatorios (semilla fija) a menos de 1.4 km del microhub; {INSTANCIAS} instancias por tamaño (5 desde 30 paradas; 3 en el exacto con 9).", "",
            "| Paradas | Exacto (ms) | Vecino (ms) | Vecino + 2-opt (ms) | Km llegada | Km 2-opt | Ahorro vs llegada | Brecha vecino | Brecha 2-opt | 2-opt óptimo |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for r in filas:
        ex, ve, op, ll = r.get("exacto"), r["vecino"], r["2opt"], r["llegada"]
        out.append(f"| {r['n']} | {f(ex['ms']) if ex else '—'} | {f(ve['ms'], 3)} | {f(op['ms'], 3)} | {f(ll['km'])} | {f(op['km'])} | {f(100 * (ll['km'] - op['km']) / ll['km'], 1)} % | "
                   f"{(f(ve['brecha'], 1) + ' %') if ex else '—'} | {(f(op['brecha'], 1) + ' %') if ex else '—'} | {(str(op['optimas']) + ' de ' + str(ex['k'])) if ex else '—'} |")
    con = [r for r in filas if r.get("exacto")]
    out += ["", "**Lectura.**", "",
            f"- Con {con[-1]['n']} paradas el exacto tarda {f(con[-1]['exacto']['ms'], 0)} ms y 2-opt {f(con[-1]['2opt']['ms'])} ms: "
            f"unas {f(con[-1]['exacto']['ms'] / max(con[-1]['2opt']['ms'], 0.001), 0)} veces menos.",
            f"- La brecha media de vecino + 2-opt respecto del óptimo está entre {f(min(r['2opt']['brecha'] for r in con), 1)} % y {f(max(r['2opt']['brecha'] for r in con), 1)} %.",
            f"- Frente a visitar en orden de llegada, ordenar ahorra {f(100 * (filas[-1]['llegada']['km'] - filas[-1]['2opt']['km']) / filas[-1]['llegada']['km'], 0)} % de distancia con {filas[-1]['n']} paradas.",
            "", "## 11. Limitaciones", "",
            "- Las distancias son de línea recta por un factor de rodeo: no usa calles, sentidos ni tráfico.", "- No considera ventanas de horario, capacidad en peso o volumen ni prioridades.",
            "- La asignación a repartidores es voraz: agrupa por zona y balancea, no optimiza la suma de las rutas.", "- 2-opt es una búsqueda local: puede quedarse en un óptimo local y su costo cúbico lo limita a decenas de paradas.",
            "- No incluye el regreso al microhub ni reoptimiza solo cuando cambia algo: los ajustes se piden (`/rutas/planes/{id}/ajustes`).", "",
            "**Mejoras posibles:** distancias reales con un motor de calles, evaluar el cambio de cada inversión en O(1) (2-opt incremental), Or-opt o 3-opt y optimizar la asignación entre repartidores.", ""]
    return "\n".join(out)


def main():
    casos = casos_de_prueba()
    if not all(c[3] for c in casos):
        for c in casos:
            print(c)
        raise SystemExit("Un caso de prueba falló.")
    filas = correr()
    destino = RAIZ / "entrega"
    destino.mkdir(exist_ok=True)
    (destino / "ALGORITMO_RUTAS.md").write_text(documento(filas, casos), encoding="utf-8")
    print("escrito", destino / "ALGORITMO_RUTAS.md")


if __name__ == "__main__":
    main()
