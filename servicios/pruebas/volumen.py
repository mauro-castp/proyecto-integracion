"""
volumen.py — Datos de alto volumen: cuánto tarda insertar y consultar millones de registros, qué cambian los índices y qué cambia la caché.

Trabaja en un esquema aparte de PostgreSQL (`volumen`) y en una base aparte de MongoDB (`microhubs_volumen`), con la misma forma que los datos
reales, y los borra al terminar: los datos de la demostración no se tocan.

  servicios/pruebas/correr.sh volumen ola4/volumen                     (200 000 pedidos)
  VOLUMEN_PEDIDOS=1000000 servicios/pruebas/correr.sh volumen nube/volumen
"""
import argparse
import datetime as dt
import json
import os
import platform
import random
import statistics
import sys
import time
from pathlib import Path

import psycopg
import redis
from pymongo import MongoClient

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
from comun import config  # noqa: E402

REPETICIONES = 5


def cronometro(fn):
    t = time.perf_counter()
    r = fn()
    return (time.perf_counter() - t) * 1000, r


def mediana_ms(fn, n=REPETICIONES):
    return round(statistics.median(cronometro(fn)[0] for _ in range(n)), 2)


# ------------------------------------------------------------------ PostgreSQL
DDL = """
DROP SCHEMA IF EXISTS volumen CASCADE;
CREATE SCHEMA volumen;
CREATE UNLOGGED TABLE volumen.pedido (
    id bigint PRIMARY KEY, cliente_id integer NOT NULL, zona_id integer NOT NULL, microhub_id integer NOT NULL,
    estado varchar(20) NOT NULL, subtotal numeric(12,2) NOT NULL, creado_en timestamptz NOT NULL);
CREATE UNLOGGED TABLE volumen.pedido_detalle (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, pedido_id bigint NOT NULL, producto_id integer NOT NULL,
    cantidad integer NOT NULL, precio_unitario numeric(10,2) NOT NULL);
"""
INSERT_PEDIDOS = """
INSERT INTO volumen.pedido
SELECT g, 1 + (random() * 19999)::int, 1 + (random() * 3)::int, 1 + (random() * 3)::int,
       (ARRAY['entregado','entregado','entregado','entregado','cancelado','en_ruta','en_preparacion','asignado'])[1 + (random() * 7)::int],
       round((40 + random() * 460)::numeric, 2), now() - (random() * 365 || ' days')::interval
  FROM generate_series(%s, %s) g
"""
INSERT_DETALLE = """
INSERT INTO volumen.pedido_detalle (pedido_id, producto_id, cantidad, precio_unitario)
SELECT p.id, 1 + (random() * 50)::int, 1 + (random() * 5)::int, round((8 + random() * 90)::numeric, 2)
  FROM volumen.pedido p CROSS JOIN generate_series(1, 3)
"""
CONSULTAS = [
    ("Pedidos de un cliente", "SELECT id, estado, subtotal, creado_en FROM volumen.pedido WHERE cliente_id = 4321 ORDER BY creado_en DESC LIMIT 20"),
    ("Pedidos abiertos de un microhub", "SELECT count(*) FROM volumen.pedido WHERE microhub_id = 2 AND estado IN ('asignado','en_preparacion','en_ruta') "
                                        "AND creado_en >= now() - interval '2 days'"),
    ("Venta por día de los últimos 30 días", "SELECT creado_en::date, count(*), sum(subtotal) FROM volumen.pedido WHERE creado_en >= now() - interval '30 days' "
                                             "AND estado <> 'cancelado' GROUP BY 1 ORDER BY 1"),
    ("Líneas de un pedido", "SELECT producto_id, cantidad, precio_unitario FROM volumen.pedido_detalle WHERE pedido_id = 123456"),
    ("10 productos más vendidos de la semana", "SELECT d.producto_id, sum(d.cantidad) AS u FROM volumen.pedido p JOIN volumen.pedido_detalle d ON d.pedido_id = p.id "
                                               "WHERE p.creado_en >= now() - interval '7 days' AND p.estado <> 'cancelado' GROUP BY 1 ORDER BY u DESC LIMIT 10"),
]
INDICES = [
    "CREATE INDEX ix_v_cliente ON volumen.pedido (cliente_id, creado_en DESC)",
    "CREATE INDEX ix_v_abiertos ON volumen.pedido (microhub_id, creado_en) WHERE estado IN ('asignado','en_preparacion','en_ruta')",
    "CREATE INDEX ix_v_fecha ON volumen.pedido (creado_en) INCLUDE (subtotal, estado)",
    "CREATE INDEX ix_v_detalle ON volumen.pedido_detalle (pedido_id) INCLUDE (producto_id, cantidad, precio_unitario)",
]


def plan(cur, sql):
    cur.execute("EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) " + sql)
    p = cur.fetchone()[0][0]
    nodos = []

    def recorrer(n):
        nodos.append(n["Node Type"] + (f" ({n['Index Name']})" if n.get("Index Name") else ""))
        for h in n.get("Plans", []):
            recorrer(h)
    recorrer(p["Plan"])
    return {"ejecucion_ms": round(p["Execution Time"], 2), "nodos": nodos}


def postgres(n):
    res = {"pedidos": n}
    with psycopg.connect(config.PG_DSN, autocommit=True) as con, con.cursor() as cur:
        cur.execute(DDL)
        ms, _ = cronometro(lambda: cur.execute(INSERT_PEDIDOS, (1, n)))
        res["insercion_masiva_pedidos"] = {"filas": n, "ms": round(ms), "filas_por_segundo": round(n / ms * 1000)}
        ms, _ = cronometro(lambda: cur.execute(INSERT_DETALLE))
        res["insercion_masiva_detalle"] = {"filas": cur.rowcount, "ms": round(ms), "filas_por_segundo": round(cur.rowcount / ms * 1000)}
        # una por una, como lo haría una aplicación sin agrupar
        k = 2000
        t = time.perf_counter()
        for i in range(n + 1, n + k + 1):
            cur.execute("INSERT INTO volumen.pedido VALUES (%s, 1, 1, 1, 'asignado', 100, now())", (i,))
        ms = (time.perf_counter() - t) * 1000
        res["insercion_fila_por_fila"] = {"filas": k, "ms": round(ms), "filas_por_segundo": round(k / ms * 1000)}
        cur.execute("ANALYZE volumen.pedido; ANALYZE volumen.pedido_detalle")
        sin = {nombre: plan(cur, sql) for nombre, sql in CONSULTAS}
        t_idx = []
        for sql in INDICES:
            ms, _ = cronometro(lambda: cur.execute(sql))
            t_idx.append({"indice": sql.split()[2], "ms": round(ms)})
        cur.execute("VACUUM ANALYZE volumen.pedido"); cur.execute("VACUUM ANALYZE volumen.pedido_detalle")
        con_idx = {nombre: plan(cur, sql) for nombre, sql in CONSULTAS}
        res["creacion_de_indices"] = t_idx
        res["consultas"] = [{"consulta": nombre, "sin_indice_ms": sin[nombre]["ejecucion_ms"], "con_indice_ms": con_idx[nombre]["ejecucion_ms"],
                             "veces_mas_rapida": round(sin[nombre]["ejecucion_ms"] / max(con_idx[nombre]["ejecucion_ms"], 0.01), 1),
                             "plan_sin": sin[nombre]["nodos"], "plan_con": con_idx[nombre]["nodos"], "sql": sql} for nombre, sql in CONSULTAS]
        cur.execute("SELECT pg_size_pretty(sum(pg_total_relation_size(c.oid))) FROM pg_class c JOIN pg_namespace s ON s.oid = c.relnamespace "
                    "WHERE s.nspname = 'volumen' AND c.relkind = 'r'")
        res["tamano_en_disco"] = cur.fetchone()[0]

        # caché: la consulta del reporte contra la misma respuesta guardada en Redis
        r = redis.Redis.from_url(config.REDIS_URL, db=1, decode_responses=True)
        sql = CONSULTAS[2][1]

        def sin_cache():
            cur.execute(sql)
            return cur.fetchall()
        r.setex("volumen:venta30", 120, json.dumps(sin_cache(), default=str))
        res["cache"] = {"consulta": CONSULTAS[2][0], "base_ms": mediana_ms(sin_cache, 30),
                        "redis_ms": mediana_ms(lambda: json.loads(r.get("volumen:venta30")), 30)}
        res["cache"]["veces_mas_rapida"] = round(res["cache"]["base_ms"] / max(res["cache"]["redis_ms"], 0.01), 1)
        r.delete("volumen:venta30")
        cur.execute("DROP SCHEMA volumen CASCADE")
    return res


# ------------------------------------------------------------------ MongoDB
def mongo(n_gps, n_eventos):
    cli = MongoClient(config.MONGO_URL, serverSelectionTimeoutMS=3000, tz_aware=True)
    db = cli["microhubs_volumen"]
    cli.drop_database("microhubs_volumen")
    ahora = dt.datetime.now(dt.timezone.utc)
    res = {}

    def punto(i):
        return {"entrega_id": i // 100, "usuario_id": 7, "capturado_en": ahora - dt.timedelta(seconds=i),
                "posicion": {"type": "Point", "coordinates": [-100.36 + random.random() / 50, 25.74 + random.random() / 50]}}

    def evento(i):
        return {"momento": ahora - dt.timedelta(seconds=i), "zona_id": 1 + i % 4, "producto_id": 1 + i % 50, "tipo": random.choice(["busqueda", "carrito", "pedido"])}
    for nombre, coleccion, total, crear in (("puntos GPS", db.ubicaciones, n_gps, punto), ("eventos de demanda", db.eventos, n_eventos, evento)):
        t = time.perf_counter()
        for ini in range(0, total, 10000):
            coleccion.insert_many([crear(i) for i in range(ini, min(ini + 10000, total))], ordered=False)
        ms = (time.perf_counter() - t) * 1000
        res[nombre] = {"documentos": total, "ms": round(ms), "documentos_por_segundo": round(total / ms * 1000)}
    consultas = [
        ("Recorrido de una entrega", lambda: list(db.ubicaciones.find({"entrega_id": n_gps // 200}).sort("capturado_en", 1))),
        ("Puntos a 100 m de un microhub", lambda: db.ubicaciones.count_documents({"posicion": {"$geoWithin": {"$centerSphere": [[-100.355, 25.75], 0.1 / 6371]}}})),
        ("Eventos de una zona en la última hora", lambda: list(db.eventos.aggregate([{"$match": {"zona_id": 2, "momento": {"$gte": ahora - dt.timedelta(hours=1)}}},
                                                                                    {"$group": {"_id": "$tipo", "n": {"$sum": 1}}}]))),
    ]
    sin = {n: mediana_ms(f) for n, f in consultas}
    db.ubicaciones.create_index([("entrega_id", 1), ("capturado_en", 1)])
    db.ubicaciones.create_index([("posicion", "2dsphere")])
    db.eventos.create_index([("zona_id", 1), ("momento", -1)])
    con = {n: mediana_ms(f) for n, f in consultas}
    res["consultas"] = [{"consulta": n, "sin_indice_ms": sin[n], "con_indice_ms": con[n], "veces_mas_rapida": round(sin[n] / max(con[n], 0.01), 1)} for n, _ in consultas]
    cli.drop_database("microhubs_volumen")
    return res


def informe(r):
    pg, mg = r["postgresql"], r["mongodb"]
    out = ["# Datos de alto volumen", "", f"Corrida del {r['fecha']} en `{r['equipo']}`. Esquema y base aparte, borrados al terminar.", "",
           "## PostgreSQL: inserción", "", "| Forma | Filas | Tiempo | Filas por segundo |", "|---|---|---|---|"]
    for nombre, clave in (("Masiva (pedidos)", "insercion_masiva_pedidos"), ("Masiva (líneas de pedido)", "insercion_masiva_detalle"), ("Una por una", "insercion_fila_por_fila")):
        x = pg[clave]
        out.append(f"| {nombre} | {x['filas']:,} | {x['ms']:,} ms | {x['filas_por_segundo']:,} |")
    out += ["", f"Tamaño en disco de las tablas: **{pg['tamano_en_disco']}**.", "", "## PostgreSQL: consultas con y sin índices (EXPLAIN ANALYZE)", "",
            "| Consulta | Sin índice | Con índice | Mejora | Plan con índice |", "|---|---|---|---|---|"]
    for c in pg["consultas"]:
        out.append(f"| {c['consulta']} | {c['sin_indice_ms']} ms | {c['con_indice_ms']} ms | {c['veces_mas_rapida']}× | {' → '.join(c['plan_con'][:3])} |")
    lentas = [c["consulta"] for c in pg["consultas"] if c["veces_mas_rapida"] < 1]
    if lentas:
        out += ["", f"**Cuando un índice no ayuda.** En {', '.join('«' + x + '»' for x in lentas)} la consulta recorre una parte grande de la tabla y el plan con "
                "índice salió más lento que la lectura completa en paralelo. Un índice sirve para consultas selectivas (un cliente, un pedido, lo abierto de un "
                "microhub); para agregados amplios conviene la caché de Redis (abajo) o una tabla de resúmenes."]
    k = pg["cache"]
    out += ["", "## Con y sin Redis", "", f"«{k['consulta']}»: calculada en PostgreSQL **{k['base_ms']} ms**; leída de Redis **{k['redis_ms']} ms** ({k['veces_mas_rapida']}×; "
            "mediana de 30 repeticiones).", "", "## MongoDB", "", "| Colección | Documentos | Tiempo de inserción | Documentos por segundo |", "|---|---|---|---|"]
    for n in ("puntos GPS", "eventos de demanda"):
        out.append(f"| {n} | {mg[n]['documentos']:,} | {mg[n]['ms']:,} ms | {mg[n]['documentos_por_segundo']:,} |")
    out += ["", "| Consulta | Sin índice | Con índice | Mejora |", "|---|---|---|---|"]
    for c in mg["consultas"]:
        out.append(f"| {c['consulta']} | {c['sin_indice_ms']} ms | {c['con_indice_ms']} ms | {c['veces_mas_rapida']}× |")
    out += ["", "## Consultas medidas", ""] + [f"- **{c['consulta']}:** `{c['sql']}`" for c in pg["consultas"]]
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", default="/tmp/volumen")
    ap.add_argument("--pedidos", type=int, default=int(os.environ.get("VOLUMEN_PEDIDOS", "200000")))
    a = ap.parse_args()
    if a.pedidos < 150000:
        ap.error("usa al menos 150000 pedidos")
    print(f"PostgreSQL: {a.pedidos:,} pedidos…", flush=True)
    r = {"fecha": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "equipo": f"{platform.machine()} · {os.cpu_count()} CPU", "postgresql": postgres(a.pedidos)}
    print("MongoDB…", flush=True)
    r["mongodb"] = mongo(a.pedidos * 2, a.pedidos)
    salida = Path(a.salida)
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "volumen.json").write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    (salida / "volumen.md").write_text(informe(r), encoding="utf-8")
    print(informe(r))


if __name__ == "__main__":
    main()
