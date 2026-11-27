"""
medir_volumen.py — Mide el comportamiento de la plataforma con datos de alto volumen (Tercer Parcial).

Se corre después de cada etapa de `bloque_c/scripts/generar_volumen.py` (10 k, 50 k, 100 k pedidos) y guarda
evidencias/volumen/medicion_<etiqueta>.json. Con --reporte junta todas las etapas en evidencias/volumen/RESULTADOS.md.

Qué mide:
  1. Tamaño: filas y espacio en disco de las tablas grandes, documentos e índices de MongoDB, memoria de Redis.
  2. Consultas SQL (EXPLAIN ANALYZE): las mismas que hacen los servicios, con su índice y SIN él (el índice se borra dentro
     de una transacción que se deshace: la base queda igual).
  3. Consultas de MongoDB (explain executionStats): recorrido de una entrega y búsqueda geográfica, con índice y con recorrido
     completo de la colección.
  4. API: mediana, p95 y máximo de los endpoints que leen mucho (listas, resúmenes, reportes, auditoría, recorrido GPS) y el
     tiempo de procesamiento de POST /demanda/sincronizacion sobre todo el histórico.
  5. Caché de Redis: el mismo endpoint de catálogo con la caché caliente y borrando la caché antes de cada petición.
  6. Recursos: memoria (RSS) de PostgreSQL, MongoDB, Redis y los servicios, y CPU durante la medición.

Uso:
  python pruebas/medir_volumen.py --etiqueta 010k
  python pruebas/medir_volumen.py --reporte
Variables: PG_DSN, MONGO_URL, REDIS_URL, MICROSERVICIOS_URL, MICROHUBS_CLAVE.
"""
import argparse
import datetime as dt
import json
import os
import statistics
import time
import urllib.error
import urllib.request
from pathlib import Path

import psycopg
import redis

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = Path(os.environ.get("SALIDA_VOLUMEN", RAIZ / "evidencias" / "volumen"))
DSN = os.environ.get("PG_DSN", "host=127.0.0.1 port=5432 dbname=microhubs_p1 user=microhubs password=microhubs_dev")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://127.0.0.1:27017/microhubs_eventos")
REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379")
PLANTILLA = os.environ.get("MICROSERVICIOS_URL", "http://{servicio}:{puerto}")
CLAVE = os.environ.get("MICROHUBS_CLAVE", "Codex#2026")
PUERTOS = {"auth": 5101, "productos": 5103, "pedidos": 5104, "seguimiento": 5110, "demanda": 5115, "reportes": 5123,
           "auditoria-monitoreo": 5126}
REPETICIONES = int(os.environ.get("REPETICIONES", "15"))


# ---------------------------------------------------------------------------------------------------------------------------
def url(servicio, ruta):
    return PLANTILLA.format(servicio=servicio, puerto=PUERTOS[servicio]) + ruta


def http(metodo, servicio, ruta, token=None, cuerpo=None, timeout=120):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(url(servicio, ruta), data=datos, method=metodo,
                                 headers={"Accept": "application/json", "Content-Type": "application/json",
                                          **({"Authorization": f"Bearer {token}"} if token else {})})
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            cuerpo = r.read()
            return r.status, (time.perf_counter() - t0) * 1000, cuerpo
    except urllib.error.HTTPError as e:
        return e.code, (time.perf_counter() - t0) * 1000, e.read()


def limpiar_limites(r1):
    for k in r1.scan_iter("rate:*"):
        r1.delete(k)


def login(correo):
    st, _, c = http("POST", "auth", "/api/v1/auth/login", cuerpo={"correo": correo, "clave": CLAVE})
    if st != 200:
        raise SystemExit(f"No se pudo iniciar sesión con {correo}: {st} {c[:200]}")
    return json.loads(c)["token_acceso"]


def resumir(tiempos):
    t = sorted(tiempos)
    p95 = t[min(len(t) - 1, max(0, round(0.95 * len(t)) - 1))]
    return {"n": len(t), "mediana_ms": round(statistics.median(t), 1), "p95_ms": round(p95, 1), "max_ms": round(t[-1], 1),
            "min_ms": round(t[0], 1)}


# ---------------------------------------------------------------------------------------------------------------------------
def tamanos(con, db, r0):
    tablas = ["pedido", "pedido_detalle", "historial_estatus", "entrega", "auditoria", "usuario", "cliente", "domicilio"]
    pg = {}
    for t in tablas:
        n, total, idx = con.execute(f"SELECT count(*), pg_total_relation_size('microhubs.{t}'), pg_indexes_size('microhubs.{t}') "
                                    f"FROM microhubs.{t}").fetchone()
        pg[t] = {"filas": n, "mb_total": round(total / 2 ** 20, 1), "mb_indices": round(idx / 2 ** 20, 1)}
    pg["_base_mb"] = round(con.execute("SELECT pg_database_size(current_database())").fetchone()[0] / 2 ** 20, 1)
    mg = {}
    for c in ["ubicaciones_entrega", "logs_tecnicos", "documentos"]:
        s = db.command("collStats", c)
        mg[c] = {"documentos": s["count"], "mb_datos": round(s["size"] / 2 ** 20, 1), "mb_indices": round(s["totalIndexSize"] / 2 ** 20, 1)}
    info = r0.info("memory")
    return {"postgres": pg, "mongo": mg, "redis_mb": round(info["used_memory"] / 2 ** 20, 2)}


def explain(con, sql, args=(), sin_indice=None):
    """(ms de ejecución, nodos principales del plan). Si sin_indice, lo borra en una transacción que se deshace."""
    with con.transaction(force_rollback=True):
        if sin_indice:
            for i in sin_indice:
                con.execute(f"DROP INDEX microhubs.{i}")
        plan = con.execute("EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) " + sql, args).fetchone()[0][0]
    nodos = []

    def recorrer(n):
        etiqueta = n["Node Type"] + (f" ({n['Index Name']})" if "Index Name" in n else "") + \
            (f" on {n['Relation Name']}" if "Relation Name" in n and "Index Name" not in n else "")
        nodos.append(etiqueta)
        for h in n.get("Plans", []):
            recorrer(h)
    recorrer(plan["Plan"])
    return round(plan["Execution Time"], 2), [x for x in nodos if "Scan" in x][:4]


def consultas_sql(con, ids):
    hoy = dt.date.today()
    zona = "America/Monterrey"
    casos = [
        ("Lista de pedidos del administrador (servicio pedidos, fn_pedidos_visibles)",
         "SELECT p.id FROM fn_pedidos_visibles(%s) p JOIN microhubs.zona z ON z.id = p.zona_id WHERE p.estado = 'entregado' "
         "ORDER BY p.creado_en DESC, p.id DESC LIMIT 20", (ids["admin"],), None),
        ("Lista de pedidos del administrador como la arma ahora el servicio (tabla directa, ámbito total)",
         "SELECT p.id FROM microhubs.pedido p JOIN microhubs.zona z ON z.id = p.zona_id WHERE p.estado = 'entregado' "
         "ORDER BY p.creado_en DESC, p.id DESC LIMIT 20", (), ["ix_web_pedido_fecha"]),
        ("Buscar un pedido por id dentro del ámbito (fn_pedidos_visibles … WHERE id = ?)",
         "SELECT 1 FROM fn_pedidos_visibles(%s) WHERE id = %s", (ids["admin"], ids["pedido"]), None),
        ("Lista de pedidos de un operador (su microhub)",
         "SELECT p.id FROM fn_pedidos_visibles(%s) p WHERE TRUE ORDER BY p.creado_en DESC, p.id DESC LIMIT 20", (ids["operador"],), None),
        ("Pedidos de un cliente, más recientes primero", "SELECT id FROM microhubs.pedido WHERE cliente_id = %s ORDER BY creado_en DESC LIMIT 20",
         (ids["cliente"],), ["ix_pedido_cliente"]),
        ("Pedidos de una zona en una semana", "SELECT count(*) FROM microhubs.pedido WHERE zona_id = 1 AND creado_en >= %s AND creado_en < %s",
         (hoy - dt.timedelta(days=14), hoy - dt.timedelta(days=7)), ["ix_pedido_zona_fecha"]),
        ("Historial de estados de un pedido", "SELECT * FROM microhubs.historial_estatus WHERE pedido_id = %s ORDER BY fecha",
         (ids["pedido"],), ["ix_hist_pedido"]),
        ("Líneas de un pedido", "SELECT * FROM microhubs.pedido_detalle WHERE pedido_id = %s", (ids["pedido"],), ["ix_detalle_pedido", "ix_detalle_pedido_cubriente"]),
        ("Auditoría de una entidad (trazabilidad)", "SELECT * FROM microhubs.auditoria WHERE entidad = 'pedido' AND entidad_id = %s",
         (str(ids["pedido"]),), ["ix_aud_entidad"]),
        ("Auditoría por módulo y acción, últimos 7 días",
         "SELECT id FROM microhubs.auditoria WHERE modulo = 'pedidos' AND accion = 'alta' AND fecha >= now() - interval '7 days' "
         "ORDER BY fecha DESC LIMIT 50", (), ["ix_aud_modulo_accion", "ix_aud_fecha"]),
        ("Resumen por día y zona, 30 días (servicio pedidos/resumen)",
         f"SELECT (p.creado_en AT TIME ZONE '{zona}')::date, p.zona_id, count(*), sum(d.unidades), sum(p.subtotal) "
         f"FROM fn_pedidos_visibles(%s) p LEFT JOIN (SELECT pedido_id, sum(cantidad) AS unidades FROM microhubs.pedido_detalle GROUP BY pedido_id) d "
         f"ON d.pedido_id = p.id WHERE p.estado <> 'cancelado' AND (p.creado_en AT TIME ZONE '{zona}')::date BETWEEN %s AND %s GROUP BY 1, 2",
         (ids["admin"], hoy - dt.timedelta(days=30), hoy), None),
        ("Resumen por día y zona, 30 días, con rango de creado_en (como ahora el servicio)",
         f"SELECT (p.creado_en AT TIME ZONE '{zona}')::date, p.zona_id, count(*), sum(d.unidades), sum(p.subtotal) "
         f"FROM microhubs.pedido p LEFT JOIN (SELECT pedido_id, sum(cantidad) AS unidades FROM microhubs.pedido_detalle GROUP BY pedido_id) d "
         f"ON d.pedido_id = p.id WHERE p.estado <> 'cancelado' AND p.creado_en >= %s AND p.creado_en < %s GROUP BY 1, 2",
         (dt.datetime.combine(hoy - dt.timedelta(days=30), dt.time(), dt.timezone(dt.timedelta(hours=-6))),
          dt.datetime.combine(hoy + dt.timedelta(days=1), dt.time(), dt.timezone(dt.timedelta(hours=-6)))), None),
        ("Ventas por producto, 90 días (servicio pedidos/ventas)",
         f"SELECT d.producto_id, sum(d.cantidad), sum(d.importe) FROM fn_pedidos_visibles(%s) p JOIN microhubs.pedido_detalle d ON d.pedido_id = p.id "
         f"WHERE p.estado NOT IN ('cancelado','creado','pendiente_asignacion') AND (p.creado_en AT TIME ZONE '{zona}')::date BETWEEN %s AND %s "
         f"GROUP BY d.producto_id", (ids["admin"], hoy - dt.timedelta(days=90), hoy), None),
    ]
    res = []
    for titulo, sql, args, indices in casos:
        con_ms, con_plan = explain(con, sql, args)
        fila = {"consulta": titulo, "con_indice_ms": con_ms, "plan": con_plan}
        if indices:
            sin_ms, sin_plan = explain(con, sql, args, indices)
            fila.update({"indice": ", ".join(indices), "sin_indice_ms": sin_ms, "plan_sin_indice": sin_plan})
        res.append(fila)
    return res


def consultas_mongo(db, ids):
    from bson.int64 import Int64
    col = db.ubicaciones_entrega
    res = []
    filtro = {"entrega_id": Int64(ids["entrega"])}

    def ex(cursor_fn, hint):
        e = cursor_fn().hint(hint).explain()["executionStats"]
        return {"ms": e["executionTimeMillis"], "docs_examinados": e["totalDocsExamined"], "devueltos": e["nReturned"]}
    con = ex(lambda: col.find(filtro).sort("capturado_en", 1), "ix_entrega_tiempo")
    sin = ex(lambda: col.find(filtro).sort("capturado_en", 1), {"$natural": 1})
    res.append({"consulta": "Recorrido GPS de una entrega", "con_indice": con, "sin_indice": sin, "indice": "ix_entrega_tiempo"})
    geo = {"posicion": {"$geoWithin": {"$centerSphere": [[-100.364, 25.748], 0.3 / 6378.1]}}}
    con = ex(lambda: col.find(geo, {"_id": 1}), "ix_posicion")
    sin = ex(lambda: col.find(geo, {"_id": 1}), {"$natural": 1})
    res.append({"consulta": "Puntos GPS a 300 m del MH-01", "con_indice": con, "sin_indice": sin, "indice": "ix_posicion (2dsphere)"})
    t0 = time.perf_counter()
    agg = list(db.logs_tecnicos.aggregate([{"$match": {"registrado_en": {"$gte": dt.datetime.now(dt.timezone.utc).replace(tzinfo=None) - dt.timedelta(days=30)}}},
                                          {"$group": {"_id": "$nivel", "n": {"$sum": 1}}}]))
    res.append({"consulta": "Registros técnicos por nivel, 30 días ($group)", "ms": round((time.perf_counter() - t0) * 1000, 1),
                "grupos": {a["_id"]: a["n"] for a in agg}})
    return res


def endpoints(tok, ids, r1):
    hoy = dt.date.today()
    d30, d90, d170 = [(hoy - dt.timedelta(days=n)).isoformat() for n in (30, 90, 170)]
    casos = [
        ("GET pedidos (entregados, página 1)", "pedidos", f"/api/v1/pedidos?estado=entregado&pagina=1&por_pagina=20"),
        ("GET pedidos (página 200)", "pedidos", f"/api/v1/pedidos?pagina=200&por_pagina=20"),
        ("GET pedidos/resumen (30 días)", "pedidos", f"/api/v1/pedidos/resumen?desde={d30}&hasta={hoy}&por_pagina=100"),
        ("GET pedidos/resumen (170 días)", "pedidos", f"/api/v1/pedidos/resumen?desde={d170}&hasta={hoy}&por_pagina=100"),
        ("GET pedidos/ventas (90 días)", "pedidos", f"/api/v1/pedidos/ventas?desde={d90}&hasta={hoy}"),
        ("GET reportes/pedidos_por_dia (90 días)", "reportes", f"/api/v1/reportes/pedidos_por_dia?desde={d90}&hasta={hoy}"),
        ("GET reportes/ventas_por_producto (90 días)", "reportes", f"/api/v1/reportes/ventas_por_producto?desde={d90}&hasta={hoy}"),
        ("GET auditoria (módulo pedidos)", "auditoria-monitoreo", "/api/v1/auditoria?modulo=pedidos&por_pagina=50"),
        ("GET auditoria/trazabilidad/pedido", "auditoria-monitoreo", f"/api/v1/auditoria/trazabilidad/pedido/{ids['pedido']}"),
        ("GET seguimiento/{id}/recorrido", "seguimiento", f"/api/v1/seguimiento/{ids['entrega']}/recorrido"),
    ]
    res = []
    for titulo, svc, ruta in casos:
        limpiar_limites(r1)
        for k in r1.scan_iter("cache:pedidos:*"):           # el primer llamado calcula (sin caché de resultados)
            r1.delete(k)
        st, primero, _ = http("GET", svc, ruta, tok)
        tiempos, codigos = [], set()
        for _ in range(REPETICIONES):
            st, ms, _ = http("GET", svc, ruta, tok)
            tiempos.append(ms)
            codigos.add(st)
        res.append({"endpoint": titulo, "ruta": ruta, "codigos": sorted(codigos), "primer_llamado_ms": round(primero, 1), **resumir(tiempos)})
    limpiar_limites(r1)
    for k in r1.scan_iter("cache:pedidos:*"):
        r1.delete(k)
    st, ms, c = http("POST", "demanda", "/api/v1/demanda/sincronizacion", tok, {"desde": d170, "hasta": hoy.isoformat(), "por_categoria": True},
                     timeout=600)
    cuerpo = json.loads(c) if st < 300 else {"error": c[:300].decode(errors="replace")}
    res.append({"endpoint": "POST demanda/sincronizacion (170 días, por categoría)", "codigos": [st], "n": 1, "mediana_ms": round(ms, 1),
                "p95_ms": round(ms, 1), "max_ms": round(ms, 1), "min_ms": round(ms, 1), "detalle": cuerpo})
    return res


def cache_redis(tok, r1, n=200):
    """El catálogo se guarda en Redis (base 1). Sin caché = se borra antes de cada petición (también la de permisos)."""
    ruta = "/api/v1/productos?q=a&pagina=1&por_pagina=50"
    limpiar_limites(r1)
    http("GET", "productos", ruta, tok)
    caliente = []
    for _ in range(n):
        caliente.append(http("GET", "productos", ruta, tok)[1])
    limpiar_limites(r1)
    fria = []
    for _ in range(n):
        for k in list(r1.scan_iter("cache:*")):
            r1.delete(k)
        fria.append(http("GET", "productos", ruta, tok)[1])
    limpiar_limites(r1)
    return {"endpoint": "GET productos?q=a&por_pagina=50", "con_cache": resumir(caliente), "sin_cache": resumir(fria)}


def recursos():
    import psutil
    grupos = {"postgres": 0, "mongod": 0, "redis-server": 0, "servicios (gunicorn)": 0}
    for p in psutil.process_iter(["name", "cmdline", "memory_info"]):
        try:
            nombre, cmd = p.info["name"] or "", " ".join(p.info["cmdline"] or [])
            rss = p.info["memory_info"].rss if p.info["memory_info"] else 0
        except Exception:
            continue
        if nombre.startswith("postgres"):
            grupos["postgres"] += rss
        elif nombre == "mongod":
            grupos["mongod"] += rss
        elif nombre.startswith("redis-server"):
            grupos["redis-server"] += rss
        elif "gunicorn" in cmd:
            grupos["servicios (gunicorn)"] += rss
    return {k: round(v / 2 ** 20) for k, v in grupos.items()}


def identificadores(con):
    q = lambda s, *a: con.execute(s, a).fetchone()[0]
    return {"admin": q("SELECT id FROM microhubs.usuario WHERE correo = 'admin@codex.mx'"),
            "operador": q("SELECT id FROM microhubs.usuario WHERE correo = 'operador.mh01@codex.mx'"),
            "cliente": q("SELECT cliente_id FROM microhubs.pedido WHERE folio LIKE 'VOL-%%' GROUP BY 1 ORDER BY count(*) DESC LIMIT 1"),
            "pedido": q("SELECT id FROM microhubs.pedido WHERE folio LIKE 'VOL-%%' ORDER BY id DESC LIMIT 1"),
            "entrega": q("SELECT e.id FROM microhubs.entrega e JOIN microhubs.pedido p ON p.id = e.pedido_id WHERE p.folio LIKE 'VOL-%%' "
                         "ORDER BY e.id DESC LIMIT 1")}


def medir(etiqueta):
    import psutil
    from pymongo import MongoClient
    r0, r1 = redis.Redis.from_url(REDIS_URL, db=0), redis.Redis.from_url(REDIS_URL, db=1)
    db = MongoClient(MONGO_URL)["microhubs_eventos"]
    psutil.cpu_percent(None)
    with psycopg.connect(DSN, autocommit=True) as con:
        ids = identificadores(con)
        limpiar_limites(r1)
        tok = login("admin@codex.mx")
        r = {"etiqueta": etiqueta, "fecha": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "ids": ids,
             "tamanos": tamanos(con, db, r0)}
        print("tamaños listos", flush=True)
        r["sql"] = consultas_sql(con, ids)
        print("SQL listo", flush=True)
        r["mongo"] = consultas_mongo(db, ids)
        print("MongoDB listo", flush=True)
        r["api"] = endpoints(tok, ids, r1)
        print("API lista", flush=True)
        r["cache"] = cache_redis(tok, r1)
        r["recursos_mb"] = recursos()
        r["cpu_promedio_pct"] = psutil.cpu_percent(None)
        r["cpu_nucleos"] = psutil.cpu_count()
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / f"medicion_{etiqueta}.json").write_text(json.dumps(r, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"Guardado {SALIDA / f'medicion_{etiqueta}.json'}")


# ---------------------------------------------------------------------------------------------------------------------------
def reporte():
    med = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(SALIDA.glob("medicion_*.json"))]
    ins = json.loads((SALIDA / "insercion.json").read_text(encoding="utf-8")) if (SALIDA / "insercion.json").exists() else []
    o = ["# Procesamiento de grandes volúmenes · resultados", "",
         f"Generado por `servicios/pruebas/medir_volumen.py --reporte` el {dt.date.today().isoformat()}. Datos crudos en `medicion_*.json` e `insercion.json`.", ""]
    if med:
        o += ["## Volumen cargado por etapa", "", "| Etapa | Pedidos | Líneas | Historial | Auditoría | Entregas | Puntos GPS | Logs técnicos | Base PG (MB) | GPS en MongoDB (MB datos + índices) |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for m in med:
            pg, mg = m["tamanos"]["postgres"], m["tamanos"]["mongo"]
            g = mg["ubicaciones_entrega"]
            o.append(f"| {m['etiqueta']} | {pg['pedido']['filas']:,} | {pg['pedido_detalle']['filas']:,} | {pg['historial_estatus']['filas']:,} | "
                     f"{pg['auditoria']['filas']:,} | {pg['entrega']['filas']:,} | {g['documentos']:,} | {mg['logs_tecnicos']['documentos']:,} | "
                     f"{pg['_base_mb']} | {g['mb_datos']} + {g['mb_indices']} |")
        o.append("")
    if ins:
        o += ["## Tiempo de inserción", "", "| Etapa | Método | Registros | Segundos | Registros/s |", "|---|---|---|---|---|"]
        for e in ins:
            et = f"{e['pedidos_antes']:,} → {e['pedidos_despues']:,}"
            for metodo, d, n in [("PostgreSQL · INSERT fila por fila (pedido + líneas, con triggers)", e["postgres"]["fila_por_fila"], "pedidos"),
                                 ("PostgreSQL · COPY por lotes (pedido + líneas, con triggers)", e["postgres"]["copy"], "pedidos"),
                                 ("PostgreSQL · COPY de entregas históricas (sin triggers)", e["postgres"]["entregas_copy_sin_triggers"], "filas"),
                                 ("MongoDB · insert_one (GPS)", e["mongo"]["insert_one"], "docs"),
                                 ("MongoDB · insert_many lotes de 5 000 (GPS)", e["mongo"]["insert_many"], "docs"),
                                 ("MongoDB · insert_many (logs técnicos)", e["mongo"]["logs_tecnicos"], "docs")]:
                if d.get(n):
                    o.append(f"| {et} | {metodo} | {d[n]:,} | {d['segundos']} | {d[n] / d['segundos']:,.0f} |" if d["segundos"] else
                             f"| {et} | {metodo} | {d[n]:,} | {d['segundos']} | — |")
        o.append("")
    for m in med:
        o += [f"## Etapa {m['etiqueta']} ({m['tamanos']['postgres']['pedido']['filas']:,} pedidos)", "",
              "### Consultas SQL (EXPLAIN ANALYZE)", "", "| Consulta | Con índice (ms) | Plan | Sin índice (ms) | Plan sin índice | Índice |", "|---|---|---|---|---|---|"]
        for s in m["sql"]:
            o.append(f"| {s['consulta']} | {s['con_indice_ms']} | {' → '.join(s['plan'])} | {s.get('sin_indice_ms', '—')} | "
                     f"{' → '.join(s.get('plan_sin_indice', [])) or '—'} | {s.get('indice', '—')} |")
        o += ["", "### MongoDB (explain executionStats)", "", "| Consulta | Con índice (ms / docs examinados) | Sin índice (ms / docs examinados) | Índice |", "|---|---|---|---|"]
        for s in m["mongo"]:
            if "con_indice" in s:
                c, si = s["con_indice"], s["sin_indice"]
                o.append(f"| {s['consulta']} | {c['ms']} / {c['docs_examinados']:,} | {si['ms']} / {si['docs_examinados']:,} | {s['indice']} |")
            else:
                o.append(f"| {s['consulta']} | {s['ms']} | — | — |")
        o += ["", "### API (milisegundos, cliente en la misma máquina)", "", "| Endpoint | HTTP | Primer llamado | Mediana | p95 | Máx |", "|---|---|---|---|---|---|"]
        for a in m["api"]:
            o.append(f"| {a['endpoint']} | {', '.join(map(str, a['codigos']))} | {a.get('primer_llamado_ms', '—')} | {a['mediana_ms']} | {a['p95_ms']} | {a['max_ms']} |")
        c = m["cache"]
        o += ["", "### Caché de Redis", "", "| Endpoint | Con caché: mediana / p95 | Sin caché: mediana / p95 | Mejora de la mediana |", "|---|---|---|---|",
              f"| {c['endpoint']} | {c['con_cache']['mediana_ms']} / {c['con_cache']['p95_ms']} ms | {c['sin_cache']['mediana_ms']} / {c['sin_cache']['p95_ms']} ms | "
              f"{c['sin_cache']['mediana_ms'] / c['con_cache']['mediana_ms']:.1f}× |", "",
              f"Recursos (RSS en MB): " + ", ".join(f"{k} {v}" for k, v in m["recursos_mb"].items()) +
              f" · CPU promedio durante la medición: {m['cpu_promedio_pct']} % de {m['cpu_nucleos']} núcleos · Redis: {m['tamanos']['redis_mb']} MB.", ""]
    if len(med) > 1:
        o += ["## Escalabilidad (mediana de la API en ms por etapa)", "", "| Endpoint | " + " | ".join(m["etiqueta"] for m in med) + " |",
              "|---|" + "---|" * len(med)]
        for i, a in enumerate(med[0]["api"]):
            o.append(f"| {a['endpoint']} | " + " | ".join(str(next((x["mediana_ms"] for x in m["api"] if x["endpoint"] == a["endpoint"]), "—")) for m in med) + " |")
        o.append("")
    (SALIDA / "RESULTADOS.md").write_text("\n".join(o) + "\n", encoding="utf-8")
    print(f"Escrito {SALIDA / 'RESULTADOS.md'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--etiqueta")
    ap.add_argument("--reporte", action="store_true")
    a = ap.parse_args()
    if a.reporte:
        reporte()
    else:
        medir(a.etiqueta or dt.datetime.now().strftime("%H%M"))
