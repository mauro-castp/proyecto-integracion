"""
resumen.py — Convierte los CSV de Locust y las muestras de `docker stats` en un informe legible.

  python3 rendimiento/resumen.py <carpeta con carga_stats.csv, carga_stats_history.csv, carga_failures.csv y recursos.csv> ["descripción del entorno"]
"""
import csv
import statistics
import sys
from pathlib import Path


def leer(p):
    return list(csv.DictReader(p.open(encoding="utf-8"))) if p.exists() else []


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def por_escalon(historia):
    """Agrupa la serie «Aggregated» en tramos seguidos con el mismo número de usuarios (se descarta la rampa)."""
    tramos = []
    for f in historia:
        if f.get("Name") != "Aggregated":
            continue
        u = int(num(f.get("User Count")))
        if not tramos or tramos[-1][0] != u:
            tramos.append((u, []))
        tramos[-1][1].append(f)
    salida = []
    for u, filas in tramos:
        if len(filas) < 15:                       # rampas y cambios de escalón
            continue
        utiles = filas[len(filas) // 4:]          # la primera cuarta parte todavía se está estabilizando
        ini, fin = utiles[0], utiles[-1]
        seg = max(1.0, num(fin["Timestamp"]) - num(ini["Timestamp"]))
        peticiones = num(fin["Total Request Count"]) - num(ini["Total Request Count"])
        fallos = num(fin["Total Failure Count"]) - num(ini["Total Failure Count"])
        salida.append({"usuarios": u, "rps": peticiones / seg, "media": _media_tramo(ini, fin),
                       "p50": statistics.median(num(x["50%"]) for x in utiles), "p95": statistics.median(num(x["95%"]) for x in utiles),
                       "p99": statistics.median(num(x["99%"]) for x in utiles), "errores": 100 * fallos / peticiones if peticiones else 0.0})
    return salida


def _media_tramo(ini, fin):
    n0, n1 = num(ini["Total Request Count"]), num(fin["Total Request Count"])
    if n1 <= n0:
        return num(fin["Total Average Response Time"])
    return (num(fin["Total Average Response Time"]) * n1 - num(ini["Total Average Response Time"]) * n0) / (n1 - n0)


def recursos(p):
    maximos = {}
    if not p.exists():
        return []
    for linea in p.read_text(encoding="utf-8", errors="replace").splitlines():
        partes = linea.split(";")
        if len(partes) != 3 or not partes[0].startswith("microhubs-"):
            continue
        nombre, cpu, mem = partes
        cpu = num(cpu.strip().rstrip("%"))
        previo = maximos.get(nombre, (0.0, "", []))
        previo[2].append(cpu)
        maximos[nombre] = (max(previo[0], cpu), mem.split("/")[0].strip(), previo[2])
    return sorted(((n.replace("microhubs-integrado-", "").rsplit("-", 1)[0] if n != "microhubs-locust" else "Locust (generador de carga)", m, statistics.mean(todas), mem) for n, (m, mem, todas) in maximos.items()),
                  key=lambda x: -x[1])


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    d = Path(sys.argv[1])
    entorno = sys.argv[2] if len(sys.argv) > 2 else "equipo local"
    stats, historia = leer(d / "carga_stats.csv"), leer(d / "carga_stats_history.csv")
    fallos = leer(d / "carga_failures.csv")
    total = next(f for f in stats if f["Name"] == "Aggregated")
    esc = por_escalon(historia)
    out = ["# Pruebas de carga con Locust", "", f"Entorno: {entorno}. Perfiles y escalones en `rendimiento/locustfile.py`. Tiempos en milisegundos.", "",
           f"**Total:** {int(num(total['Request Count'])):,} peticiones · {num(total['Requests/s']):.1f} por segundo · media {num(total['Average Response Time']):.0f} ms · "
           f"p95 {total['95%']} ms · p99 {total['99%']} ms · errores {int(num(total['Failure Count']))} "
           f"({100 * num(total['Failure Count']) / max(1, num(total['Request Count'])):.2f} %).", "",
           "## Por escalón de usuarios", "", "| Usuarios simultáneos | Peticiones/s | Media | p50 | p95 | p99 | Errores |", "|---|---|---|---|---|---|---|"]
    for e in esc:
        out.append(f"| {e['usuarios']} | {e['rps']:.1f} | {e['media']:.0f} | {e['p50']:.0f} | {e['p95']:.0f} | {e['p99']:.0f} | {e['errores']:.2f} % |")
    if esc:
        mejor = max(esc, key=lambda e: e["rps"])
        saturado = next((e for e in esc[1:] if e["errores"] > 1 or (e["p95"] > 1000 and e["p95"] > 2 * esc[0]["p95"])), None)
        pico = max(esc, key=lambda e: e["usuarios"])
        out += ["", "## Lectura", "",
                f"- Mayor rendimiento: **{mejor['rps']:.1f} peticiones por segundo** con {mejor['usuarios']} usuarios.",
                (f"- **Saturación:** a partir de {saturado['usuarios']} usuarios (p95 de {saturado['p95']:.0f} ms, {saturado['errores']:.2f} % de errores)."
                 if saturado else f"- No se alcanzó la saturación (errores ≤ 1 % y sin que el p95 se duplicara) hasta {pico['usuarios']} usuarios."),]
        if len(esc) > 1 and esc[-1]["usuarios"] < pico["usuarios"]:
            r = esc[-1]
            out.append(f"- **Recuperación:** al bajar a {r['usuarios']} usuarios el p95 volvió a {r['p95']:.0f} ms (con {esc[0]['usuarios']} al principio: {esc[0]['p95']:.0f} ms).")
    out += ["", "## Los 10 puntos más lentos (p95)", "", "| Petición | Veces | Media | p95 | p99 | Errores |", "|---|---|---|---|---|---|"]
    for f in sorted((x for x in stats if x["Name"] != "Aggregated"), key=lambda x: -num(x["95%"]))[:10]:
        out.append(f"| {f['Name']} | {int(num(f['Request Count']))} | {num(f['Average Response Time']):.0f} | {f['95%']} | {f['99%']} | {int(num(f['Failure Count']))} |")
    out += ["", "## Errores", ""]
    if fallos:
        out += ["| Petición | Error | Veces |", "|---|---|---|"] + [f"| {f['Name']} | {f['Error'][:90]} | {f['Occurrences']} |" for f in fallos[:15]]
    else:
        out.append("No hubo errores.")
    rec = recursos(d / "recursos.csv")
    if rec:
        out += ["", "## Recursos: los contenedores que más CPU usaron", "", "| Contenedor | CPU máxima | CPU media | Memoria |", "|---|---|---|---|"]
        out += [f"| {n} | {m:.0f} % | {med:.0f} % | {mem} |" for n, m, med, mem in rec[:10]]
        out += ["", "El 100 % equivale a un núcleo completo."]
    (d / "informe_carga.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
