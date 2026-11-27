"""
resumir.py — Junta los CSV de Locust de evidencias/carga en evidencias/carga/RESULTADOS.md.

  python pruebas_carga/resumir.py [--carpeta evidencias/carga]

Por escenario: usuarios, peticiones, RPS, mediana, p95, p99, errores y los 5 endpoints más lentos (por p95). Para el de estrés
(…_stats_history.csv con varios niveles de usuarios): cada escalón con su RPS, p95 y errores, el punto de saturación (donde el RPS
deja de crecer o el p95 pasa de 1 s) y el tiempo de recuperación tras bajar la carga.
"""
import argparse
import csv
import statistics
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
NOMBRES = {"normal": "Carga normal", "alta": "Carga alta", "estres_recuperacion": "Estrés y recuperación",
           "proteccion_limites": "Protección: límites de consumo activos"}


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def escenario(carpeta, n):
    filas = list(csv.DictReader(open(carpeta / f"{n}_stats.csv", encoding="utf-8")))
    agg = next(r for r in filas if r["Name"] == "Aggregated")
    hist = list(csv.DictReader(open(carpeta / f"{n}_stats_history.csv", encoding="utf-8"))) if (carpeta / f"{n}_stats_history.csv").exists() else []
    hist = [h for h in hist if h["Name"] == "Aggregated"]
    usuarios = max((int(h["User Count"]) for h in hist), default=0)
    fallas = list(csv.DictReader(open(carpeta / f"{n}_failures.csv", encoding="utf-8"))) if (carpeta / f"{n}_failures.csv").exists() else []
    return filas, agg, hist, usuarios, fallas


def escalones(hist):
    """Agrupa la historia por número de usuarios (solo los tramos estables, sin los primeros 8 s de cada escalón)."""
    t0 = int(hist[0]["Timestamp"])
    tramos, actual, inicio = [], None, 0
    for h in hist:
        u, t = int(h["User Count"]), int(h["Timestamp"]) - t0
        if u != actual:
            actual, inicio = u, t
            tramos.append({"usuarios": u, "inicio": t, "muestras": []})
        if t - inicio >= 8 and num(h["Requests/s"]) is not None:
            tramos[-1]["muestras"].append(h)
    out = []
    for tr in tramos:
        m = tr["muestras"]
        if not m or tr["usuarios"] == 0:
            continue
        p95 = [num(x["95%"]) for x in m if num(x["95%"]) is not None]
        out.append({"usuarios": tr["usuarios"], "inicio_s": tr["inicio"], "rps": round(statistics.mean(num(x["Requests/s"]) for x in m), 1),
                    "p95_ms": round(statistics.median(p95)) if p95 else None,
                    "fallas_s": round(statistics.mean(num(x["Failures/s"]) or 0 for x in m), 2)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--carpeta", default=str(RAIZ / "evidencias" / "carga"))
    carpeta = Path(ap.parse_args().carpeta)
    nombres = [n for n in NOMBRES if (carpeta / f"{n}_stats.csv").exists()]
    o = ["# Pruebas de carga con Locust · resultados", "",
         "Generado por `pruebas_carga/resumir.py` a partir de los CSV de esta carpeta. Cómo se corrió y qué significa: "
         "[`pruebas_carga/LEEME.md`](../../pruebas_carga/LEEME.md). Reporte HTML de Locust de cada escenario: `<escenario>.html`.", "",
         "## Resumen por escenario", "",
         "| Escenario | Usuarios (máx.) | Peticiones | RPS promedio | Mediana (ms) | p95 (ms) | p99 (ms) | Máx. (ms) | Errores |", "|---|---|---|---|---|---|---|---|---|"]
    datos = {n: escenario(carpeta, n) for n in nombres}
    for n in nombres:
        _, a, _, u, _ = datos[n]
        pet, fal = int(a["Request Count"]), int(a["Failure Count"])
        o.append(f"| {NOMBRES[n]} | {u} | {pet:,} | {num(a['Requests/s']):.1f} | {a['50%']} | {a['95%']} | {a['99%']} | {num(a['Max Response Time']):,.0f} | "
                 f"{fal:,} ({100 * fal / max(pet, 1):.2f} %) |")
    for n in nombres:
        filas, a, hist, u, fallas = datos[n]
        o += ["", f"## {NOMBRES[n]}", "", "### Endpoints más lentos (p95)", "",
              "| Endpoint | Peticiones | Errores | Mediana | p95 | p99 | Máx. |", "|---|---|---|---|---|---|---|"]
        for r in sorted((r for r in filas if r["Name"] != "Aggregated"), key=lambda r: -(num(r["95%"]) or 0))[:5]:
            o.append(f"| {r['Type']} {r['Name']} | {int(r['Request Count']):,} | {r['Failure Count']} | {r['50%']} | {r['95%']} | {r['99%']} | "
                     f"{num(r['Max Response Time']):,.0f} |")
        if fallas:
            o += ["", "### Errores", "", "| Endpoint | Error | Veces |", "|---|---|---|"]
            agrupado = {}
            for f in fallas:
                err = f["Error"]
                if "login" in err and "HTTP" in err:
                    err = "HTTP " + err.rsplit("HTTP", 1)[1].strip(" ')\"")
                agrupado[(f["Method"] + " " + f["Name"], err)] = agrupado.get((f["Method"] + " " + f["Name"], err), 0) + int(f["Occurrences"])
            for (nom, err), v in sorted(agrupado.items(), key=lambda kv: -kv[1]):
                o.append(f"| {nom} | {err} | {v} |")
        esc = escalones(hist) if hist else []
        if len({e["usuarios"] for e in esc}) > 2:
            o += ["", "### Escalones", "", "| Desde (s) | Usuarios | RPS | p95 (ms) | Errores/s |", "|---|---|---|---|---|"]
            for e in esc:
                o.append(f"| {e['inicio_s']} | {e['usuarios']} | {e['rps']} | {e['p95_ms']} | {e['fallas_s']} |")
            pico = max(esc, key=lambda e: e["rps"])
            sat = next((e for e in esc if (e["p95_ms"] or 0) > 1000), None)
            base = esc[0]["p95_ms"] or 1
            bajada = next((i for i in range(1, len(esc)) if esc[i]["usuarios"] < esc[i - 1]["usuarios"]), None)
            o += ["", f"- **Rendimiento máximo:** {pico['rps']} peticiones/s con {pico['usuarios']} usuarios."]
            if sat:
                o.append(f"- **Saturación:** desde {sat['usuarios']} usuarios el p95 del tramo estable pasa de 1 s ({sat['p95_ms']} ms).")
            if bajada is not None:
                t_baja = esc[bajada]["inicio_s"]
                t0 = int(hist[0]["Timestamp"])
                rec = next((int(h["Timestamp"]) - t0 for h in hist if int(h["Timestamp"]) - t0 > t_baja and num(h["95%"]) is not None
                            and num(h["95%"]) <= 2 * base), None)
                if rec is not None:
                    o.append(f"- **Recuperación:** la carga baja a {esc[bajada]['usuarios']} usuarios en el segundo {t_baja}; el p95 vuelve a menos del "
                             f"doble del inicial ({base} ms) en el segundo {rec}, es decir **{rec - t_baja} s** después.")
    (carpeta / "RESULTADOS.md").write_text("\n".join(o) + "\n", encoding="utf-8")
    print(f"Escrito {carpeta / 'RESULTADOS.md'}")


if __name__ == "__main__":
    main()
