"""
benchmark_algoritmos.py — Tiempo de ejecución y calidad de los algoritmos documentados en docs/ALGORITMOS.md.

  python servicios/pruebas/benchmark_algoritmos.py            (no necesita bases de datos)

1. Ruteo de paradas (servicio rutas, sistema_web/planeacion_calc.py):
   · para n = 3…9 paradas: TSP exacto, vecino más cercano y vecino + 2-opt; tiempo y diferencia contra el óptimo;
   · para n = 10…60: vecino y vecino + 2-opt (el exacto ya no es posible: 10! = 3.6 millones de órdenes).
   Las paradas son puntos al azar dentro de 2 km del MH-01, como los domicilios reales.
2. Simulación Monte Carlo (servicio simulacion): tiempo contra número de réplicas y días, estabilidad del resultado (cuánto se
   mueve la utilidad media al cambiar la semilla) y reproducibilidad (misma semilla → misma huella).

Escribe evidencias/algoritmos/benchmark.json y benchmark.md.
"""
import importlib.util
import json
import math
import os
import random
import statistics
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI.parent))
sys.path.append(str(RAIZ / "sistema_web"))
os.environ.setdefault("LOG_STDOUT", "0")
os.environ.setdefault("SIM_TRABAJADOR", "0")
os.environ.setdefault("MONITOR_AUTO", "0")

import planeacion_calc as pc  # noqa: E402

SALIDA = RAIZ / "evidencias" / "algoritmos"
MH01 = (25.748, -100.364)


def cargar(nombre):
    spec = importlib.util.spec_from_file_location(f"b_{nombre}", AQUI.parent / nombre / "app.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def paradas_al_azar(rng, n, radio_km=2.0):
    out = []
    for _ in range(n):
        r, a = radio_km * math.sqrt(rng.random()), rng.uniform(0, 2 * math.pi)
        out.append({"lat": MH01[0] + r * math.cos(a) / 111.0, "lng": MH01[1] + r * math.sin(a) / (111.0 * math.cos(math.radians(MH01[0])))})
    return out


def medir(fn):
    t0 = time.perf_counter()
    r = fn()
    return r, (time.perf_counter() - t0) * 1000


def rutas():
    rng = random.Random(20261126)
    filas = []
    for n in list(range(3, 10)) + [10, 12, 15, 20, 30, 40, 50, 60]:
        casos = 20 if n <= 8 else (5 if n == 9 else 20)
        t_ex, t_nn, t_2o, gap_nn, gap_2o, mejora_2o, opt_2o = [], [], [], [], [], [], 0
        for _ in range(casos):
            p = paradas_al_azar(rng, n)
            o_nn, ms = medir(lambda: pc.vecino_mas_cercano(MH01, p))
            t_nn.append(ms)
            o_2o, ms = medir(lambda: pc.dos_opt(MH01, p, pc.vecino_mas_cercano(MH01, p)))
            t_2o.append(ms)
            d_nn, d_2o = pc.distancia_ruta(MH01, p, o_nn)[0], pc.distancia_ruta(MH01, p, o_2o)[0]
            mejora_2o.append(100 * (d_nn - d_2o) / d_nn)
            if n <= 9:
                o_ex, ms = medir(lambda: pc.tsp_exacto(MH01, p))
                t_ex.append(ms)
                d_ex = pc.distancia_ruta(MH01, p, o_ex)[0]
                gap_nn.append(100 * (d_nn - d_ex) / d_ex)
                gap_2o.append(100 * (d_2o - d_ex) / d_ex)
                opt_2o += abs(d_2o - d_ex) < 1e-9
        fila = {"paradas": n, "casos": casos, "vecino_ms": round(statistics.median(t_nn), 3), "dos_opt_ms": round(statistics.median(t_2o), 3),
                "mejora_2opt_sobre_vecino_pct": round(statistics.mean(mejora_2o), 2)}
        if t_ex:
            fila.update({"exacto_ms": round(statistics.median(t_ex), 2), "brecha_vecino_pct": round(statistics.mean(gap_nn), 2),
                         "brecha_vecino_max_pct": round(max(gap_nn), 2), "brecha_2opt_pct": round(statistics.mean(gap_2o), 2),
                         "brecha_2opt_max_pct": round(max(gap_2o), 2), "2opt_optimo_pct": round(100 * opt_2o / casos)})
        filas.append(fila)
        print("rutas", fila, flush=True)
    return filas


def monte_carlo():
    sim = cargar("simulacion")

    def escenario(**c):
        e = {"pedidos_dia": 60.0, "ticket": 135.0, "margen_bruto": 0.28, "costos_fijos_mes": 60000.0, "costo_variable_pedido": 32.6, "dias_mes": 30.0,
             "operadores": 3, "repartidores": 3, "capacidad_fisica": None, "horas": 10.0, "distancia_km": 2.4, "ausentismo": 0.05,
             "variacion_demanda": 0.10, "indice_semanal": [0.9, 0.9, 0.95, 1.0, 1.15, 1.25, 0.85], "dia_inicio": 1, "dias": 30,
             "modelo": {k: sim.DEFECTOS[k] for k in (*sim.PARAMS_CAPACIDAD, "umbral_utilizacion_riesgo")}}
        e.update(c)
        return e

    tiempos = []
    for replicas in (50, 100, 200, 500, 1000, 2000):
        for dias in (30, 90):
            r, ms = medir(lambda: sim.simular(escenario(dias=dias), 2026, replicas))
            tiempos.append({"replicas": replicas, "dias": dias, "ms": round(ms, 1), "us_por_replica_dia": round(1000 * ms / (replicas * dias), 2)})
            print("mc", tiempos[-1], flush=True)
    estabilidad = []
    for replicas in (50, 200, 1000):
        medias = [next(m["media"] for m in sim.simular(escenario(), s, replicas)["metricas"] if m["clave"] == "utilidad") for s in range(1, 11)]
        estabilidad.append({"replicas": replicas, "semillas": 10, "utilidad_media_promedio": round(statistics.mean(medias), 0),
                            "desviacion_entre_semillas": round(statistics.pstdev(medias), 0),
                            "variacion_pct": round(100 * statistics.pstdev(medias) / abs(statistics.mean(medias)), 2)})
        print("estabilidad", estabilidad[-1], flush=True)
    a, b = sim.simular(escenario(), 2026, 200), sim.simular(escenario(), 2026, 200)
    repro = {"misma_semilla_misma_huella": sim.huella_de(a) == sim.huella_de(b), "huella": sim.huella_de(a)[:16] + "…",
             "otra_semilla_otra_huella": sim.huella_de(sim.simular(escenario(), 2027, 200)) != sim.huella_de(a)}
    casos = []
    for nombre, cambios in [("Base del equipo (60 pedidos/día, ticket 135, margen 28 %)", {}),
                            ("Demanda en el equilibrio estimado (385 pedidos/día)", {"pedidos_dia": 385.0}),
                            ("Sin ausentismo ni variación", {"ausentismo": 0.0, "variacion_demanda": 0.0}),
                            ("Ausentismo alto (20 %)", {"ausentismo": 0.20}),
                            ("Margen bruto 40 % y 150 pedidos/día", {"margen_bruto": 0.40, "pedidos_dia": 150.0})]:
        r = sim.simular(escenario(**cambios), 2026, 500)
        u = next(m for m in r["metricas"] if m["clave"] == "utilidad")
        casos.append({"escenario": nombre, "utilidad_media": u["media"], "p10": u["p10"], "p90": u["p90"], "prob_perdida_pct": r["prob_perdida_pct"],
                      "dias_saturados_pct": r["dias_saturados_pct"], "capacidad_dia": r["contraste"]["capacidad_dia_con_todo_el_personal"]})
    return {"tiempos": tiempos, "estabilidad": estabilidad, "reproducibilidad": repro, "casos": casos}


def escribir(res):
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / "benchmark.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    o = ["# Benchmark de algoritmos", "", f"Generado por `servicios/pruebas/benchmark_algoritmos.py`. Equipo: {res['equipo']}.", "",
         "## Ruteo de paradas", "", "Tiempo (mediana, ms) y distancia contra el óptimo (TSP exacto). Paradas al azar dentro de 2 km del MH-01.", "",
         "| Paradas | Casos | Exacto (ms) | Vecino (ms) | Vecino + 2-opt (ms) | Brecha vecino (prom / máx) | Brecha 2-opt (prom / máx) | 2-opt da el óptimo | 2-opt mejora al vecino |",
         "|---|---|---|---|---|---|---|---|---|"]
    for f in res["rutas"]:
        o.append(f"| {f['paradas']} | {f['casos']} | {f.get('exacto_ms', '—')} | {f['vecino_ms']} | {f['dos_opt_ms']} | "
                 + (f"{f['brecha_vecino_pct']} % / {f['brecha_vecino_max_pct']} % | {f['brecha_2opt_pct']} % / {f['brecha_2opt_max_pct']} % | {f['2opt_optimo_pct']} % |"
                    if "exacto_ms" in f else "— | — | — |") + f" {f['mejora_2opt_sobre_vecino_pct']} % |")
    mc = res["monte_carlo"]
    o += ["", "## Simulación Monte Carlo", "", "### Tiempo de ejecución", "", "| Réplicas | Días | Tiempo (ms) | µs por réplica-día |", "|---|---|---|---|"]
    for t in mc["tiempos"]:
        o.append(f"| {t['replicas']} | {t['dias']} | {t['ms']} | {t['us_por_replica_dia']} |")
    o += ["", "### Estabilidad (10 semillas distintas)", "", "| Réplicas | Utilidad media (promedio) | Desviación entre semillas | Variación |", "|---|---|---|---|"]
    for e in mc["estabilidad"]:
        o.append(f"| {e['replicas']} | {e['utilidad_media_promedio']:,.0f} | {e['desviacion_entre_semillas']:,.0f} | {e['variacion_pct']} % |")
    r = mc["reproducibilidad"]
    o += ["", f"Reproducibilidad: misma entrada y semilla → misma huella: **{'sí' if r['misma_semilla_misma_huella'] else 'NO'}** ({r['huella']}); "
          f"otra semilla → otra huella: **{'sí' if r['otra_semilla_otra_huella'] else 'NO'}**.", "",
          "### Casos de prueba (500 réplicas de 30 días)", "", "| Escenario | Utilidad media | P10 | P90 | Prob. de pérdida | Días saturados | Capacidad/día |", "|---|---|---|---|---|---|---|"]
    for c in mc["casos"]:
        o.append(f"| {c['escenario']} | {c['utilidad_media']:,.0f} | {c['p10']:,.0f} | {c['p90']:,.0f} | {c['prob_perdida_pct']:.1f} % | {c['dias_saturados_pct']:.1f} % | {c['capacidad_dia']:.0f} |")
    (SALIDA / "benchmark.md").write_text("\n".join(o) + "\n", encoding="utf-8")


if __name__ == "__main__":
    import platform
    res = {"equipo": f"{platform.processor() or platform.machine()}, Python {platform.python_version()}, {os.cpu_count()} CPU",
           "rutas": rutas(), "monte_carlo": monte_carlo()}
    escribir(res)
    print(f"Escrito {SALIDA / 'benchmark.md'}")
