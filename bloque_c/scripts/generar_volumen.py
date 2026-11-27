"""
generar_volumen.py — Carga de alto volumen para medir rendimiento (Tercer Parcial · procesamiento de grandes volúmenes).

Agrega a la base de pruebas, marcados como sintéticos para poder quitarlos después:

  · usuarios/clientes/domicilios  correo  vol.<n>@sintetico.microhubs.mx   (por omisión 5 000)
  · pedidos históricos            folio   VOL-<8 dígitos>                  (por omisión 100 000, en los últimos 170 días)
  · líneas de pedido              1 a 5 por pedido                         (~300 000)
  · historial y auditoría         los escriben los triggers del motor      (~1 000 000 de filas de auditoría)
  · entregas cerradas             una por pedido entregado
  · puntos GPS (MongoDB)          ubicaciones_entrega, N por entrega        (por omisión 15 → ~1.4 millones)
  · registros técnicos (MongoDB)  logs_tecnicos, componente "carga-sintetica"

Es incremental: si ya hay 10 000 pedidos VOL y se pide --pedidos 50000, agrega 40 000. Así se mide la escalabilidad por etapas
(10 k → 50 k → 100 k) con `medir_volumen.py` entre una y otra.

Además mide lo que cuesta escribir:
  · PostgreSQL: los primeros --fila-por-fila pedidos se insertan uno por uno (INSERT por pedido y por línea, como lo haría una
    aplicación ingenua); el resto con COPY. Ambos pasan por los triggers (historial, auditoría, límite por línea), así que
    el costo medido es el real del modelo.
  · MongoDB: los primeros puntos GPS con insert_one y el resto con insert_many en lotes (como lo hace el servicio de seguimiento).
  El resultado se agrega a evidencias/volumen/insercion.json.

Las entregas históricas se cargan con session_replication_role = replica (sin triggers): una carga histórica no debe mandar
100 000 avisos de «se te asignó una entrega» a los repartidores. Es la única tabla que se carga así y queda dicho en el resultado.

Uso (base de PRUEBAS, nunca la de la demostración en vivo):
  python bloque_c/scripts/generar_volumen.py --pedidos 10000
  python bloque_c/scripts/generar_volumen.py --pedidos 100000 --clientes 5000 --gps 15
  python bloque_c/scripts/generar_volumen.py --borrar            # quita todo lo sintético de PostgreSQL y MongoDB

Variables: PG_DSN, MONGO_URL (las mismas de los servicios).
"""
import argparse
import io
import json
import math
import os
import random
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import bcrypt
import psycopg

_p = Path(__file__).resolve().parents
RAIZ = _p[2] if len(_p) > 2 else Path.cwd()          # copiado a /tmp de un contenedor: se escribe en la carpeta actual
DSN = os.environ.get("PG_DSN", "host=127.0.0.1 port=5432 dbname=microhubs_p1 user=microhubs password=microhubs_dev")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://127.0.0.1:27017/microhubs_eventos")
DOMINIO = "sintetico.microhubs.mx"
PREFIJO = "VOL-"
CLAVE_DEMO = os.environ.get("MICROHUBS_CLAVE", "Codex#2026")     # los clientes sintéticos pueden iniciar sesión (Locust los usa)

NOMBRES = ["Ana", "Luis", "María", "José", "Sofía", "Carlos", "Valeria", "Jorge", "Fernanda", "Miguel", "Daniela", "Andrés",
           "Lucía", "Diego", "Paola", "Ricardo", "Ximena", "Héctor", "Regina", "Emilio"]
APELLIDOS = ["García", "Martínez", "López", "Hernández", "González", "Pérez", "Rodríguez", "Sánchez", "Ramírez", "Torres",
             "Flores", "Rivera", "Gómez", "Díaz", "Cruz", "Morales", "Reyes", "Gutiérrez", "Ortiz", "Castillo"]
CALLES = ["Av. San Bernabé", "Calle Topo Chico", "Calle Cerro de la Silla", "Calle Fresno", "Calle Encino", "Calle Nogal",
          "Calle Sabino", "Calle Álamo", "Calle Roble", "Calle Ébano"]


def ahora():
    return datetime.now(timezone.utc)


def conectar():
    con = psycopg.connect(DSN)
    con.execute("SET search_path = microhubs, public")
    return con


def mongo():
    from pymongo import MongoClient
    cli = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    return cli.get_default_database() if "/" in MONGO_URL.split("//", 1)[1] else cli["microhubs_eventos"]


# ---------------------------------------------------------------------------------------------------------------------------
# Datos de referencia
# ---------------------------------------------------------------------------------------------------------------------------
def referencia(con):
    zonas = con.execute("SELECT id, clave, colonia, codigo_postal, centroide_lat::float, centroide_lng::float, costo_envio::float "
                        "FROM zona WHERE estatus = 'activo' ORDER BY id").fetchall()
    hubs = con.execute("SELECT id, latitud::float, longitud::float FROM microhub WHERE estatus = 'activo' ORDER BY id").fetchall()
    productos = con.execute("SELECT id, precio::float FROM producto WHERE estatus = 'activo' ORDER BY id").fetchall()
    rep = con.execute("SELECT u.id FROM usuario u JOIN rol r ON r.id = u.rol_id WHERE r.clave = 'repartidor' "
                      "AND u.estatus = 'activo' ORDER BY u.id").fetchall()
    limite = con.execute("SELECT valor::int FROM configuracion WHERE clave = 'limite_unidades_linea'").fetchone()
    rol_cliente = con.execute("SELECT id FROM rol WHERE clave = 'cliente'").fetchone()[0]
    # Cada zona la atiende el microhub más cercano a su centroide.
    hub_de_zona = {}
    for z in zonas:
        hub_de_zona[z[0]] = min(hubs, key=lambda h: (h[1] - z[4]) ** 2 + (h[2] - z[5]) ** 2)
    return {"zonas": zonas, "hubs": hubs, "hub_de_zona": hub_de_zona, "productos": productos,
            "repartidores": [r[0] for r in rep], "limite_linea": min(limite[0] if limite else 10, 5), "rol_cliente": rol_cliente}


def copiar(cur, tabla, columnas, filas):
    with cur.copy(f"COPY {tabla} ({', '.join(columnas)}) FROM STDIN") as cp:
        for f in filas:
            cp.write_row(f)


# ---------------------------------------------------------------------------------------------------------------------------
# Clientes
# ---------------------------------------------------------------------------------------------------------------------------
def asegurar_clientes(con, ref, total, rnd):
    existentes = con.execute("SELECT count(*) FROM usuario WHERE correo LIKE %s", (f"vol.%@{DOMINIO}",)).fetchone()[0]
    faltan = total - existentes
    if faltan <= 0:
        return 0, 0.0
    hash_demo = bcrypt.hashpw(CLAVE_DEMO.encode(), bcrypt.gensalt(rounds=10)).decode()
    t0 = time.perf_counter()
    with con.cursor() as cur:
        usuarios = []
        for i in range(existentes + 1, total + 1):
            usuarios.append((rnd.choice(NOMBRES), f"{rnd.choice(APELLIDOS)} {rnd.choice(APELLIDOS)}", f"vol.{i:06d}@{DOMINIO}",
                             f"81{rnd.randint(10000000, 99999999)}", hash_demo, ref["rol_cliente"]))
        copiar(cur, "usuario", ["nombre", "apellidos", "correo", "telefono", "hash_contrasena", "rol_id"], usuarios)
        ids = cur.execute("SELECT id FROM usuario WHERE correo LIKE %s AND id NOT IN (SELECT usuario_id FROM cliente) ORDER BY id",
                          (f"vol.%@{DOMINIO}",)).fetchall()
        copiar(cur, "cliente", ["usuario_id", "aviso_privacidad_version", "aviso_privacidad_aceptado_en"],
               [(u[0], "AP-2026.1", ahora() - timedelta(days=rnd.randint(30, 400))) for u in ids])
        clientes = cur.execute("SELECT c.id FROM cliente c JOIN usuario u ON u.id = c.usuario_id "
                               "WHERE u.correo LIKE %s AND NOT EXISTS (SELECT 1 FROM domicilio d WHERE d.cliente_id = c.id) ORDER BY c.id",
                               (f"vol.%@{DOMINIO}",)).fetchall()
        doms = []
        for (cid,) in clientes:
            z = rnd.choice(ref["zonas"])
            doms.append((cid, rnd.choice(CALLES), str(rnd.randint(100, 4999)), z[2], z[3], "Carga sintética",
                         round(z[4] + rnd.uniform(-0.0055, 0.0055), 6), round(z[5] + rnd.uniform(-0.006, 0.006), 6), z[0]))
        copiar(cur, "domicilio", ["cliente_id", "calle", "numero_ext", "colonia", "codigo_postal", "referencia", "latitud",
                                  "longitud", "zona_id"], doms)
    con.commit()
    return faltan, time.perf_counter() - t0


def clientes_sinteticos(con):
    return con.execute("SELECT c.id, d.id, d.zona_id, d.latitud::float, d.longitud::float FROM cliente c "
                       "JOIN usuario u ON u.id = c.usuario_id JOIN domicilio d ON d.cliente_id = c.id AND d.activo "
                       "WHERE u.correo LIKE %s ORDER BY c.id", (f"vol.%@{DOMINIO}",)).fetchall()


# ---------------------------------------------------------------------------------------------------------------------------
# Pedidos
# ---------------------------------------------------------------------------------------------------------------------------
def armar_pedido(n, ref, clientes, rnd, dias):
    cli = rnd.choice(clientes)
    zona = next(z for z in ref["zonas"] if z[0] == cli[2])
    hub = ref["hub_de_zona"][zona[0]]
    # Más pedidos los fines de semana y en la tarde: así el patrón semanal y horario tiene algo que encontrar.
    while True:
        creado = ahora() - timedelta(days=rnd.uniform(1, dias))
        peso = 1.35 if creado.weekday() >= 5 else 1.0
        if rnd.random() < peso / 1.35:
            break
    creado = creado.replace(hour=rnd.choices(range(8, 22), weights=[2, 3, 4, 5, 6, 6, 5, 5, 6, 8, 9, 8, 6, 3])[0])
    lineas, usados = [], set()
    for _ in range(rnd.choices([1, 2, 3, 4, 5], weights=[15, 25, 30, 20, 10])[0]):
        p = rnd.choice(ref["productos"])
        if p[0] in usados:
            continue
        usados.add(p[0])
        lineas.append((p[0], rnd.randint(1, ref["limite_linea"]), p[1]))
    subtotal = round(sum(c * pr for _, c, pr in lineas), 2)
    estado = rnd.choices(["entregado", "entrega_parcial", "entrega_fallida", "cancelado"], weights=[86, 6, 3, 5])[0]
    asignado = creado + timedelta(minutes=rnd.randint(1, 6))
    listo = asignado + timedelta(minutes=rnd.randint(5, 20))
    cerrado = listo + timedelta(minutes=rnd.randint(10, 45))
    pedido = {"folio": f"{PREFIJO}{n:08d}", "cliente_id": cli[0], "domicilio_id": cli[1], "zona_id": zona[0], "microhub_id": hub[0],
              "estado": estado, "subtotal": subtotal, "costo_envio": zona[6] if subtotal < 300 else 0, "creado_en": creado,
              "asignado_en": asignado, "listo_en": None if estado == "cancelado" else listo, "cerrado_en": cerrado,
              "actualizado_en": cerrado, "motivo_cancelacion": "Carga sintética: cancelado por el cliente" if estado == "cancelado" else None,
              "lineas": lineas, "destino": (cli[3], cli[4]), "origen": (hub[1], hub[2])}
    return pedido


COLS_PEDIDO = ["folio", "cliente_id", "domicilio_id", "zona_id", "microhub_id", "estado", "subtotal", "costo_envio", "creado_en",
               "asignado_en", "listo_en", "cerrado_en", "actualizado_en", "motivo_cancelacion"]


def insertar_fila_por_fila(con, pedidos):
    t0 = time.perf_counter()
    with con.cursor() as cur:
        for p in pedidos:
            pid = cur.execute(f"INSERT INTO pedido ({', '.join(COLS_PEDIDO)}) VALUES ({', '.join(['%s'] * len(COLS_PEDIDO))}) RETURNING id",
                              [p[c] for c in COLS_PEDIDO]).fetchone()[0]
            p["id"] = pid
            for prod, cant, precio in p["lineas"]:
                cur.execute("INSERT INTO pedido_detalle (pedido_id, producto_id, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)",
                            (pid, prod, cant, precio))
    con.commit()
    return time.perf_counter() - t0


def insertar_copy(con, pedidos, lote=20000):
    t0 = time.perf_counter()
    for i in range(0, len(pedidos), lote):
        parte = pedidos[i:i + lote]
        with con.cursor() as cur:
            copiar(cur, "pedido", COLS_PEDIDO, ([p[c] for c in COLS_PEDIDO] for p in parte))
            ids = dict(cur.execute("SELECT folio, id FROM pedido WHERE folio = ANY(%s)", ([p["folio"] for p in parte],)).fetchall())
            for p in parte:
                p["id"] = ids[p["folio"]]
            copiar(cur, "pedido_detalle", ["pedido_id", "producto_id", "cantidad", "precio_unitario"],
                   ((p["id"], prod, cant, precio) for p in parte for prod, cant, precio in p["lineas"]))
        con.commit()
    return time.perf_counter() - t0


def insertar_entregas(con, pedidos, ref, rnd):
    resultado = {"entregado": "entregado", "entrega_parcial": "parcial", "entrega_fallida": "fallida"}
    filas = []
    for p in pedidos:
        if p["estado"] not in resultado:
            continue
        r = resultado[p["estado"]]
        dist = math.dist(p["origen"], p["destino"]) * 111
        cobrado = 0 if r == "fallida" else round((p["subtotal"] + p["costo_envio"]) * (rnd.uniform(.5, .9) if r == "parcial" else 1), 2)
        filas.append((p["id"], rnd.choice(ref["repartidores"]), p["creado_en"].date(), p["asignado_en"], p["listo_en"], p["cerrado_en"], r,
                      r != "fallida", cobrado, 0, "Cliente ausente (carga sintética)" if r == "fallida" else None,
                      round(dist * 1.3, 2), round(dist * 1.3 / 20 * 60 + 4, 1)))
    t0 = time.perf_counter()
    with con.cursor() as cur:
        cur.execute("SET LOCAL session_replication_role = replica")
        copiar(cur, "entrega", ["pedido_id", "repartidor_id", "turno_fecha", "asignada_en", "salida_en", "cierre_en", "resultado",
                                "confirmacion_recepcion", "monto_cobrado", "cambio_entregado", "incidencia", "distancia_km",
                                "minutos_estimados"], filas)
    con.commit()
    ids = dict(con.execute("SELECT e.pedido_id, e.id FROM entrega e JOIN pedido p ON p.id = e.pedido_id "
                           "WHERE p.folio = ANY(%s)", ([p["folio"] for p in pedidos],)).fetchall())
    for p in pedidos:
        p["entrega_id"] = ids.get(p["id"])
    rep =dict(con.execute("SELECT id, repartidor_id FROM entrega WHERE id = ANY(%s)", ([i for i in ids.values()],)).fetchall())
    for p in pedidos:
        if p["entrega_id"]:
            p["repartidor_id"] = rep[p["entrega_id"]]
    return len(filas), time.perf_counter() - t0


# ---------------------------------------------------------------------------------------------------------------------------
# MongoDB
# ---------------------------------------------------------------------------------------------------------------------------
def puntos_gps(p, n, rnd):
    from bson.int64 import Int64
    (la0, lo0), (la1, lo1) = p["origen"], p["destino"]
    salida = p["listo_en"]
    docs = []
    for k in range(n):
        f = k / max(n - 1, 1)
        t = salida + timedelta(seconds=30 * k)
        docs.append({"entrega_id": Int64(p["entrega_id"]), "usuario_id": int(p["repartidor_id"]),
                     "posicion": {"type": "Point", "coordinates": [round(lo0 + (lo1 - lo0) * f + rnd.uniform(-2e-4, 2e-4), 6),
                                                                   round(la0 + (la1 - la0) * f + rnd.uniform(-2e-4, 2e-4), 6)]},
                     "precision_m": float(rnd.randint(4, 25)), "capturado_en": t, "recibido_en": t + timedelta(seconds=rnd.randint(1, 20)),
                     "sintetico": True})
    return docs


def cargar_mongo(pedidos, gps, uno_a_uno, rnd):
    db = mongo()
    col = db.ubicaciones_entrega
    docs = [d for p in pedidos if p.get("entrega_id") for d in puntos_gps(p, gps, rnd)]
    res = {"puntos_gps": len(docs)}
    corte = min(uno_a_uno, len(docs))
    t0 = time.perf_counter()
    for d in docs[:corte]:
        col.insert_one(d)
    res["insert_one"] = {"docs": corte, "segundos": round(time.perf_counter() - t0, 3)}
    t0 = time.perf_counter()
    for i in range(corte, len(docs), 5000):
        col.insert_many(docs[i:i + 5000], ordered=False)
    res["insert_many"] = {"docs": len(docs) - corte, "segundos": round(time.perf_counter() - t0, 3)}
    logs = [{"nivel": rnd.choices(["INFO", "WARN", "ERROR"], weights=[90, 8, 2])[0], "componente": "carga-sintetica",
             "mensaje": f"GET /api/v1/pedidos/{p['id']}", "registrado_en": p["creado_en"], "correlacion_id": f"vol-{p['id']}",
             "ruta": "/api/v1/pedidos/<int:pid>", "duracion_ms": rnd.randint(5, 180), "contexto": {"sintetico": True}}
            for p in pedidos for _ in range(2)]
    t0 = time.perf_counter()
    for i in range(0, len(logs), 5000):
        db.logs_tecnicos.insert_many(logs[i:i + 5000], ordered=False)
    res["logs_tecnicos"] = {"docs": len(logs), "segundos": round(time.perf_counter() - t0, 3)}
    return res


# ---------------------------------------------------------------------------------------------------------------------------
def borrar():
    with conectar() as con:
        con.execute("SET session_replication_role = replica")     # sin auditar el borrado de un millón de filas sintéticas
        con.execute("CREATE TEMP TABLE vol_ped AS SELECT id FROM pedido WHERE folio LIKE %s", (PREFIJO + "%",))
        con.execute("CREATE TEMP TABLE vol_usr AS SELECT u.id AS usuario_id, c.id AS cliente_id FROM usuario u "
                    "LEFT JOIN cliente c ON c.usuario_id = u.id WHERE u.correo LIKE %s", (f"vol.%@{DOMINIO}",))
        n = con.execute("SELECT count(*) FROM vol_ped").fetchone()[0]
        con.execute("DELETE FROM auditoria a WHERE (a.entidad IN ('pedido', 'entrega') AND a.entidad_id IN (SELECT id::text FROM vol_ped)) "
                    "OR (a.entidad = 'pedido_detalle' AND (a.valores_nuevos->>'pedido_id') IN (SELECT id::text FROM vol_ped)) "
                    "OR (a.entidad = 'usuario' AND a.entidad_id IN (SELECT usuario_id::text FROM vol_usr)) "
                    "OR (a.entidad IN ('cliente') AND a.entidad_id IN (SELECT cliente_id::text FROM vol_usr)) "
                    "OR (a.entidad = 'domicilio' AND (a.valores_nuevos->>'cliente_id') IN (SELECT cliente_id::text FROM vol_usr))")
        con.execute("DELETE FROM entrega_linea WHERE entrega_id IN (SELECT id FROM entrega WHERE pedido_id IN (SELECT id FROM vol_ped))")
        con.execute("DELETE FROM entrega WHERE pedido_id IN (SELECT id FROM vol_ped)")
        con.execute("DELETE FROM historial_estatus WHERE pedido_id IN (SELECT id FROM vol_ped)")
        con.execute("DELETE FROM pedido_detalle WHERE pedido_id IN (SELECT id FROM vol_ped)")
        con.execute("DELETE FROM pedido WHERE id IN (SELECT id FROM vol_ped)")
        con.execute("DELETE FROM domicilio WHERE cliente_id IN (SELECT cliente_id FROM vol_usr)")
        con.execute("DELETE FROM cliente WHERE id IN (SELECT cliente_id FROM vol_usr)")
        con.execute("DELETE FROM usuario WHERE id IN (SELECT usuario_id FROM vol_usr)")
        con.commit()
    db = mongo()
    g = db.ubicaciones_entrega.delete_many({"sintetico": True}).deleted_count
    print(f"Borrados {n} pedidos sintéticos (con sus líneas, entregas, historial y auditoría), los clientes vol.* y {g} puntos GPS. "
          "logs_tecnicos es una colección capped: sus registros sintéticos salen solos al llenarse.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pedidos", type=int, default=100000, help="total de pedidos sintéticos que debe haber al terminar")
    ap.add_argument("--clientes", type=int, default=5000)
    ap.add_argument("--gps", type=int, default=15, help="puntos GPS por entrega")
    ap.add_argument("--dias", type=int, default=170, help="los pedidos caen en los últimos N días (TTL del GPS: 180)")
    ap.add_argument("--fila-por-fila", type=int, default=5000, help="cuántos pedidos insertar uno por uno para comparar con COPY")
    ap.add_argument("--insert-one", type=int, default=20000, help="cuántos puntos GPS con insert_one para comparar con insert_many")
    ap.add_argument("--semilla", type=int, default=20261126)
    ap.add_argument("--salida", default=str(RAIZ / "evidencias" / "volumen" / "insercion.json"))
    ap.add_argument("--borrar", action="store_true")
    a = ap.parse_args()
    if a.borrar:
        return borrar()

    with conectar() as con:
        ya = con.execute("SELECT count(*) FROM pedido WHERE folio LIKE %s", (PREFIJO + "%",)).fetchone()[0]
        rnd = random.Random(a.semilla + ya)
        ref = referencia(con)
        if not ref["repartidores"]:
            sys.exit("No hay repartidores activos: cargue primero la semilla (01 a 11).")
        n_cli, t_cli = asegurar_clientes(con, ref, a.clientes, rnd)
        clientes = clientes_sinteticos(con)
        faltan = a.pedidos - ya
        if faltan <= 0:
            print(f"Ya hay {ya} pedidos sintéticos; nada que agregar.")
            return
        print(f"Clientes nuevos: {n_cli} ({t_cli:.1f} s). Agregando {faltan} pedidos (hay {ya})…", flush=True)
        pedidos = [armar_pedido(ya + i + 1, ref, clientes, rnd, a.dias) for i in range(faltan)]
        uno = min(a.fila_por_fila, len(pedidos)) if ya == 0 else 0
        t_uno = insertar_fila_por_fila(con, pedidos[:uno]) if uno else 0.0
        t_copy = insertar_copy(con, pedidos[uno:])
        n_ent, t_ent = insertar_entregas(con, pedidos, ref, rnd)
        lineas = sum(len(p["lineas"]) for p in pedidos)
        con.execute("ANALYZE pedido; ANALYZE pedido_detalle; ANALYZE entrega; ANALYZE historial_estatus; ANALYZE auditoria")
        con.commit()
        total = con.execute("SELECT count(*) FROM pedido WHERE folio LIKE %s", (PREFIJO + "%",)).fetchone()[0]
    print(f"PostgreSQL listo: {faltan} pedidos, {lineas} líneas, {n_ent} entregas. Cargando MongoDB…", flush=True)
    m = cargar_mongo(pedidos, a.gps, a.insert_one if ya == 0 else 0, rnd)

    etapa = {"fecha": ahora().isoformat(timespec="seconds"), "pedidos_antes": ya, "pedidos_despues": total, "pedidos_agregados": faltan,
             "lineas_agregadas": lineas, "clientes_agregados": n_cli, "clientes_segundos": round(t_cli, 3),
             "postgres": {"fila_por_fila": {"pedidos": uno, "lineas": sum(len(p["lineas"]) for p in pedidos[:uno]), "segundos": round(t_uno, 3)},
                          "copy": {"pedidos": len(pedidos) - uno, "lineas": sum(len(p["lineas"]) for p in pedidos[uno:]), "segundos": round(t_copy, 3)},
                          "entregas_copy_sin_triggers": {"filas": n_ent, "segundos": round(t_ent, 3)}},
             "mongo": m}
    salida = Path(a.salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    historial = json.loads(salida.read_text(encoding="utf-8")) if salida.exists() else []
    historial.append(etapa)
    salida.write_text(json.dumps(historial, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(etapa, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
