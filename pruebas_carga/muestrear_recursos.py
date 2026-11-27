"""
muestrear_recursos.py — Muestra cada N segundos la CPU y la memoria del equipo mientras corre Locust.

  python pruebas_carga/muestrear_recursos.py --salida evidencias/carga/normal_recursos.csv --cada 5 &
  locust ...
  kill %1

En la VM de GCP se corre dentro de la VM (o se usa Cloud Monitoring). Agrupa la memoria residente por componente:
PostgreSQL, MongoDB, Redis, los servicios y el web (gunicorn) y Locust.
"""
import argparse
import csv
import time

import psutil


def grupo(p):
    nombre, cmd = p.info["name"] or "", " ".join(p.info["cmdline"] or [])
    if nombre.startswith("postgres"):
        return "postgres"
    if nombre == "mongod":
        return "mongod"
    if nombre.startswith("redis-server"):
        return "redis"
    if "gunicorn" in cmd:
        return "servicios"
    if "locust" in cmd:
        return "locust"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", required=True)
    ap.add_argument("--cada", type=float, default=5)
    a = ap.parse_args()
    campos = ["t", "cpu_pct", "mem_usada_mb", "cpu_postgres", "cpu_mongod", "cpu_redis", "cpu_servicios", "cpu_locust",
              "rss_postgres", "rss_mongod", "rss_redis", "rss_servicios", "rss_locust"]
    procs = {}
    psutil.cpu_percent(None)
    t0 = time.time()
    with open(a.salida, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(campos)
        while True:
            time.sleep(a.cada)
            cpu = {k: 0.0 for k in ("postgres", "mongod", "redis", "servicios", "locust")}
            rss = dict(cpu)
            for p in psutil.process_iter(["name", "cmdline", "memory_info"]):
                g = grupo(p)
                if not g:
                    continue
                if p.pid not in procs:
                    procs[p.pid] = p
                    p.cpu_percent(None)
                    continue
                try:
                    cpu[g] += procs[p.pid].cpu_percent(None)
                    rss[g] += p.info["memory_info"].rss / 2 ** 20
                except psutil.Error:
                    pass
            w.writerow([round(time.time() - t0), psutil.cpu_percent(None), round(psutil.virtual_memory().used / 2 ** 20)] +
                       [round(cpu[k], 1) for k in cpu] + [round(rss[k]) for k in rss])
            f.flush()


if __name__ == "__main__":
    main()
