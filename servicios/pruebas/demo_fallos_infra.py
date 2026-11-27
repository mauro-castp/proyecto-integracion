"""
demo_fallos_infra.py — Qué pasa cuando falla una pieza de infraestructura (Tercer Parcial · recuperación ante fallos).

Seis casos, cada uno en cuatro tiempos: antes → se provoca la falla → peticiones durante la falla → se restablece y se mide la recuperación.

  1. Un microservicio se detiene         (inventario)
  2. Redis no responde
  3. MongoDB no responde
  4. PostgreSQL no responde
  5. El servicio de archivos (bucket) no está disponible
  6. Una petición excede el tiempo máximo (costos congelado: el que llama corta a los MICROSERVICIOS_TIEMPO segundos)

De cada petición guarda método, ruta, HTTP, código de error, mensaje, traza y tiempo. También comprueba que no queden datos a medias
(conteos antes y después en PostgreSQL), lo que dijo el monitoreo y el registro técnico de MongoDB que corresponde a la traza del error.
Escribe evidencias/fallos/fallos_infraestructura.md y .json.

Cómo se provoca cada falla (plantillas; {d} = postgres | redis | mongo | <servicio>):
  DETENER   por omisión  docker compose -f docker-compose.integrado.yml stop {d}
  INICIAR   por omisión  docker compose -f docker-compose.integrado.yml start {d}
  PAUSAR    por omisión  docker compose -f docker-compose.integrado.yml pause {d}
  REANUDAR  por omisión  docker compose -f docker-compose.integrado.yml unpause {d}
  Para el bucket: DETENER_BUCKET / INICIAR_BUCKET (sin ellos el caso 5 remite a evidencias/nube/pruebas_bucket.txt, que lo prueba
  contra Google Cloud Storage real).

Uso (base de PRUEBAS; desde la raíz, con la plataforma arriba y puertos 51xx accesibles):
  python servicios/pruebas/demo_fallos_infra.py
  python servicios/pruebas/demo_fallos_infra.py --casos redis,timeout
Necesita al menos una entrega en ruta del repartidor1 (servicios/pruebas/preparar_entregas.py --cantidad 2).
"""
import argparse
import datetime as dt
import json
import os
import shlex
import subprocess
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
PLANTILLA = os.environ.get("MICROSERVICIOS_URL_DEMO", "http://localhost:{puerto}")
CLAVE = os.environ.get("MICROHUBS_CLAVE", "Codex#2026")
DSN = os.environ.get("PG_DSN", "host=127.0.0.1 port=5432 dbname=microhubs_p1 user=microhubs password=microhubs_dev")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://127.0.0.1:27017/microhubs_eventos")
COMPOSE = f"docker compose -f {RAIZ / 'docker-compose.integrado.yml'}"
CMD = {"detener": os.environ.get("DETENER", COMPOSE + " stop {d}"), "iniciar": os.environ.get("INICIAR", COMPOSE + " start {d}"),
       "pausar": os.environ.get("PAUSAR", COMPOSE + " pause {d}"), "reanudar": os.environ.get("REANUDAR", COMPOSE + " unpause {d}")}
PUERTOS = {"auth": 5101, "usuarios": 5102, "productos": 5103, "pedidos": 5104, "entregas": 5105, "documentos": 5107, "seguimiento": 5110,
           "inventario": 5111, "abastecimiento": 5114, "costos": 5119, "punto-equilibrio": 5120, "auditoria-monitoreo": 5126}
SALIDA = RAIZ / "evidencias" / "fallos"
PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="


def sh(accion, d):
    plantilla = os.environ.get(f"{accion.upper()}_BUCKET") if d == "bucket" else CMD[accion]
    if not plantilla:
        return False
    subprocess.run(plantilla.format(d=d), shell=True, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    return True


def http(metodo, servicio, ruta, token=None, cuerpo=None, timeout=30):
    req = urllib.request.Request(PLANTILLA.format(servicio=servicio, puerto=PUERTOS[servicio]) + "/api/v1/" + ruta, method=metodo,
                                 data=json.dumps(cuerpo).encode() if cuerpo is not None else None,
                                 headers={"Accept": "application/json", "Content-Type": "application/json",
                                          **({"Authorization": f"Bearer {token}"} if token else {})})
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            st, crudo = r.status, r.read()
    except urllib.error.HTTPError as e:
        st, crudo = e.code, e.read()
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
        return {"http": None, "error": f"sin conexión: {getattr(e, 'reason', e)}", "ms": round((time.perf_counter() - t0) * 1000)}
    ms = round((time.perf_counter() - t0) * 1000)
    try:
        cuerpo = json.loads(crudo) if crudo else {}
    except ValueError:
        cuerpo = {"crudo": crudo[:200].decode(errors="replace")}
    err = cuerpo.get("error") if isinstance(cuerpo, dict) else None
    if err and err.get("detalles"):
        err = {**err, "mensaje": f"{err.get('mensaje')} " + "; ".join(f"{d.get('campo')}: {d.get('mensaje')}" for d in err["detalles"])}
    return {"http": st, "codigo": err.get("codigo") if err else None, "mensaje": err.get("mensaje") if err else None,
            "traza_id": err.get("traza_id") if err else None, "ms": ms, "cuerpo": cuerpo}


def login(correo):
    r = http("POST", "auth", "auth/login", cuerpo={"correo": correo, "clave": CLAVE})
    return r["cuerpo"]["token_acceso"] if r["http"] == 200 else None


def sql(q, args=()):
    import psycopg
    try:
        with psycopg.connect(DSN, connect_timeout=3) as con:
            con.execute("SET search_path = microhubs, public")
            return con.execute(q, args).fetchall()
    except psycopg.OperationalError as e:
        return f"PostgreSQL no responde: {str(e).splitlines()[0]}"


def log_de(traza):
    if not traza:
        return None
    try:
        from pymongo import MongoClient
        doc = MongoClient(MONGO_URL, serverSelectionTimeoutMS=2000)["microhubs_eventos"].logs_tecnicos.find_one({"correlacion_id": traza})
    except Exception as e:  # noqa: BLE001
        return {"error": f"MongoDB no responde: {type(e).__name__}"}
    if not doc:
        return None
    return {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in doc.items() if k in ("nivel", "componente", "mensaje", "ruta", "duracion_ms", "contexto", "excepcion", "registrado_en")}


def esperar(cond, maximo=90, cada=1.0):
    t0 = time.time()
    while time.time() - t0 < maximo:
        if cond():
            return round(time.time() - t0, 1)
        time.sleep(cada)
    return None


def paso(lista, titulo, r, esperado=None):
    fila = {"paso": titulo, **{k: r.get(k) for k in ("http", "codigo", "mensaje", "traza_id", "ms", "error")}}
    if esperado is not None:
        fila["esperado"] = esperado
        fila["cumple"] = r.get("http") in (esperado if isinstance(esperado, (list, tuple)) else [esperado])
    lista.append(fila)
    print(f"  {titulo}: {r.get('http')} {r.get('codigo') or ''} {r.get('ms')} ms", flush=True)
    return r


def entrega_abierta(tok):
    r = http("GET", "entregas", "entregas/mias?pagina=1&por_pagina=20", tok)
    datos = (r.get("cuerpo") or {}).get("datos") or []
    return datos[0]["id"] if datos else None


# ---------------------------------------------------------------------------------------------------------------------------
def caso_servicio(t):
    pasos, svc = [], "inventario"
    paso(pasos, "Antes: GET inventario (operador)", http("GET", "inventario", "inventario?microhub_id=1&por_pagina=5", t["operador"]), 200)
    sh("detener", svc)
    time.sleep(2)
    paso(pasos, "Durante: GET inventario directo", http("GET", "inventario", "inventario?microhub_id=1&por_pagina=5", t["operador"]))
    paso(pasos, "Durante: GET abastecimiento/necesidades (necesita inventario)", http("GET", "abastecimiento", "abastecimiento/necesidades?microhub_id=1", t["operador"]), 503)
    paso(pasos, "Durante: GET productos (no depende de inventario)", http("GET", "productos", "productos?por_pagina=5", t["operador"]), 200)
    v = paso(pasos, "Durante: el monitoreo verifica (POST monitoreo/verificaciones)", http("POST", "auditoria-monitoreo", "monitoreo/verificaciones", t["admin"], {"servicio": svc}), 201)
    estado = ((v.get("cuerpo") or {}).get("servicios") or [{}])[0]
    alertas = sql("SELECT tipo, severidad, detalle FROM monitoreo_alerta WHERE servicio = %s AND cerrada_en IS NULL", (svc,))
    sh("iniciar", svc)
    rec = esperar(lambda: http("GET", "inventario", "inventario?microhub_id=1&por_pagina=5", t["operador"])["http"] == 200)
    paso(pasos, "Después: GET inventario", http("GET", "inventario", "inventario?microhub_id=1&por_pagina=5", t["operador"]), 200)
    http("POST", "auditoria-monitoreo", "monitoreo/verificaciones", t["admin"], {"servicio": svc})
    cerradas = sql("SELECT tipo, abierta_en::text, cerrada_en::text FROM monitoreo_alerta WHERE servicio = %s ORDER BY id DESC LIMIT 1", (svc,))
    return {"caso": "Un microservicio se detiene (inventario)", "pasos": pasos, "recuperacion_s": rec,
            "monitoreo": {"estado_verificado": estado.get("estado"), "error": estado.get("error"), "alertas_abiertas": alertas, "ultima_alerta_tras_volver": cerradas},
            "log": log_de(next((p["traza_id"] for p in pasos if p.get("http") == 503), None))}


def caso_redis(t):
    pasos = []
    paso(pasos, "Antes: GET productos (con sesión en Redis)", http("GET", "productos", "productos?por_pagina=5", t["operador"]), 200)
    antes = sql("SELECT count(*) FROM monitoreo_verificacion")
    sh("detener", "redis")
    time.sleep(2)
    paso(pasos, "Durante: GET productos con un token válido", http("GET", "productos", "productos?por_pagina=5", t["operador"]), 503)
    paso(pasos, "Durante: POST auth/login", http("POST", "auth", "auth/login", cuerpo={"correo": "admin@codex.mx", "clave": CLAVE}), 503)
    s = paso(pasos, "Durante: GET /salud de productos", http("GET", "productos", "salud"), 503)
    time.sleep(35)                                            # una ronda del verificador automático (30 s)
    despues = sql("SELECT count(*) FROM monitoreo_verificacion")
    ultima = sql("SELECT servicio, estado, dependencias::text FROM monitoreo_verificacion WHERE servicio = 'productos' ORDER BY id DESC LIMIT 1")
    sh("iniciar", "redis")
    rec = esperar(lambda: http("GET", "productos", "salud")["http"] == 200)
    paso(pasos, "Después: el token anterior", http("GET", "productos", "productos?por_pagina=5", t["operador"]), 401)
    for k, correo in (("operador", "operador.mh01@codex.mx"), ("admin", "admin@codex.mx"), ("planeador", "planeador@codex.mx"),
                      ("repartidor", "repartidor1@codex.mx")):
        t[k] = login(correo)                                   # Redis sin persistencia: todas las sesiones se perdieron
    paso(pasos, "Después: se vuelve a iniciar sesión y GET productos", http("GET", "productos", "productos?por_pagina=5", t["operador"]), 200)
    return {"caso": "Redis no responde", "pasos": pasos, "recuperacion_s": rec, "salud_durante": (s.get("cuerpo") or {}).get("dependencias"),
            "monitoreo": {"verificaciones_guardadas_durante_la_falla": (despues[0][0] - antes[0][0]) if isinstance(despues, list) and isinstance(antes, list) else None,
                          "ultima_de_productos": ultima},
            "log": log_de(next((p["traza_id"] for p in pasos if p.get("http") == 503 and p.get("traza_id")), None))}


def caso_mongo(t):
    pasos = []
    eid = entrega_abierta(t["repartidor"])
    paso(pasos, "Antes: GET documentos (resumen en MongoDB)", http("GET", "documentos", "documentos/resumen", t["admin"]), 200)
    evidencia = None
    if eid:   # la app sube la foto cuando la toma; el cierre llega después
        r = paso(pasos, f"Antes: el repartidor sube la foto de evidencia de la entrega {eid}",
                 http("POST", "documentos", "documentos", t["repartidor"], {"nombre": "evidencia_demo.png", "tipo_mime": "image/png",
                      "contenido_base64": PNG, "referencia": {"tipo": "entrega", "id": str(eid)}}), 201)
        evidencia = (r.get("cuerpo") or {}).get("id")
    sh("detener", "mongo")
    time.sleep(2)
    paso(pasos, "Durante: GET documentos/resumen", http("GET", "documentos", "documentos/resumen", t["admin"]), 503)
    if eid:
        paso(pasos, f"Durante: GET seguimiento/{eid}/recorrido", http("GET", "seguimiento", f"seguimiento/{eid}/recorrido", t["repartidor"]), 503)
        cierre = {"resultado": "fallida", "monto_cobrado": 0, "cambio_entregado": 0, "incidencia": "Cliente ausente (demostración: MongoDB caído)",
                  "ubicacion": {"latitud": 25.7491, "longitud": -100.3611}, "capturado_en": dt.datetime.now(dt.timezone.utc).isoformat(),
                  "id_cliente_local": str(uuid.uuid4()), "evidencia_ids": [evidencia] if evidencia else []}
        paso(pasos, f"Durante: POST entregas/{eid}/resultado (cierre en PostgreSQL)", http("POST", "entregas", f"entregas/{eid}/resultado", t["repartidor"], cierre), 201)
        pg = sql("SELECT e.resultado::text, p.estado::text FROM entrega e JOIN pedido p ON p.id = e.pedido_id WHERE e.id = %s", (eid,))
    else:
        pg = "No había entregas en ruta: correr preparar_entregas.py"
    for i in range(1, 4):   # la 1.ª petición de cada proceso espera la selección de servidor; después el cortacircuitos ya no lo intenta
        paso(pasos, f"Durante: GET productos (no usa MongoDB) #{i}", http("GET", "productos", "productos?por_pagina=5", t["admin"]), 200)
    sh("iniciar", "mongo")
    rec = esperar(lambda: http("GET", "documentos", "documentos/resumen", t["admin"])["http"] == 200)
    paso(pasos, "Después: GET documentos/resumen", http("GET", "documentos", "documentos/resumen", t["admin"]), 200)
    return {"caso": "MongoDB no responde", "pasos": pasos, "recuperacion_s": rec, "entrega_cerrada_en_postgres": pg,
            "log": log_de(next((p["traza_id"] for p in pasos if p.get("http") == 503 and p.get("traza_id")), None))}


def caso_postgres(t):
    pasos = []
    paso(pasos, "Antes: GET pedidos", http("GET", "pedidos", "pedidos?por_pagina=5", t["admin"]), 200)
    sh("detener", "postgres")
    time.sleep(2)
    paso(pasos, "Durante: GET pedidos", http("GET", "pedidos", "pedidos?por_pagina=5", t["admin"]), 503)
    paso(pasos, "Durante: POST auth/login", http("POST", "auth", "auth/login", cuerpo={"correo": "admin@codex.mx", "clave": CLAVE}), 503)
    paso(pasos, "Durante: POST abastecimiento/solicitudes (escritura)", http("POST", "abastecimiento", "abastecimiento/solicitudes", t["operador"],
                                                                        {"microhub_id": 1, "motivo": "Demostración: PostgreSQL caído", "lineas": [{"producto_id": 4, "cantidad": 2}]}), 503)
    s = paso(pasos, "Durante: GET /salud de pedidos", http("GET", "pedidos", "salud"), 503)
    sh("iniciar", "postgres")
    rec = esperar(lambda: http("GET", "pedidos", "pedidos?por_pagina=5", t["admin"])["http"] == 200)
    paso(pasos, "Después: GET pedidos (sin reiniciar el servicio)", http("GET", "pedidos", "pedidos?por_pagina=5", t["admin"]), 200)
    quedo = sql("SELECT count(*) FROM solicitud_compra WHERE motivo = 'Demostración: PostgreSQL caído'")
    return {"caso": "PostgreSQL no responde", "pasos": pasos, "recuperacion_s": rec, "salud_durante": (s.get("cuerpo") or {}).get("dependencias"),
            "datos_a_medias": {"solicitudes_guardadas_durante_la_falla": quedo},
            "log": log_de(next((p["traza_id"] for p in pasos if p.get("http") == 503 and p.get("traza_id")), None))}


def caso_bucket(t):
    if not os.environ.get("DETENER_BUCKET"):
        return {"caso": "El servicio de archivos no está disponible", "omitido": "Sin DETENER_BUCKET; ver evidencias/nube/pruebas_bucket.txt (Cloud Storage real)."}
    pasos = []
    doc = {"nombre": "demo_fallo.png", "tipo_mime": "image/png", "contenido_base64": PNG, "referencia": {"tipo": "pedido", "id": "1"}}
    antes = sql("SELECT 1")
    n0 = _docs()
    paso(pasos, "Antes: GET documentos/resumen", http("GET", "documentos", "documentos/resumen", t["admin"]), 200)
    sh("detener", "bucket")
    paso(pasos, "Durante: GET /salud de documentos", http("GET", "documentos", "salud"), 503)
    paso(pasos, "Durante: POST documentos (subir una imagen)", http("POST", "documentos", "documentos", t["admin"], doc), 503)
    n1 = _docs()
    sh("iniciar", "bucket")
    rec = esperar(lambda: http("GET", "documentos", "salud")["http"] == 200)
    paso(pasos, "Después: POST documentos", http("POST", "documentos", "documentos", t["admin"], doc), 201)
    return {"caso": "El servicio de archivos no está disponible", "pasos": pasos, "recuperacion_s": rec,
            "datos_a_medias": {"documentos_en_mongo_antes": n0, "documentos_en_mongo_durante": n1, "ok": n0 == n1 and antes is not None},
            "log": log_de(next((p["traza_id"] for p in pasos if p.get("http") == 503 and p.get("traza_id")), None))}


def _docs():
    try:
        from pymongo import MongoClient
        return MongoClient(MONGO_URL, serverSelectionTimeoutMS=2000)["microhubs_eventos"].documentos.count_documents({})
    except Exception:  # noqa: BLE001
        return None


def caso_timeout(t):
    pasos = []
    cuerpo = {"microhub_id": 1, "nombre": "Demostración: tiempo excedido", "guardar": True}
    n0 = sql("SELECT count(*) FROM equilibrio_escenario WHERE nombre = %s", (cuerpo["nombre"],))
    paso(pasos, "Antes: POST punto-equilibrio/calculos (pide datos a costos, demanda y cobertura)",
         http("POST", "punto-equilibrio", "punto-equilibrio/calculos", t["planeador"], {**cuerpo, "guardar": False}), 200)
    sh("pausar", "costos")
    r = paso(pasos, "Durante: el mismo cálculo con costos congelado (guardar = true)",
             http("POST", "punto-equilibrio", "punto-equilibrio/calculos", t["planeador"], cuerpo, timeout=60), 503)
    n1 = sql("SELECT count(*) FROM equilibrio_escenario WHERE nombre = %s", (cuerpo["nombre"],))
    sh("reanudar", "costos")
    rec = esperar(lambda: http("POST", "punto-equilibrio", "punto-equilibrio/calculos", t["planeador"], {**cuerpo, "guardar": False})["http"] == 200)
    paso(pasos, "Después: el cálculo", http("POST", "punto-equilibrio", "punto-equilibrio/calculos", t["planeador"], {**cuerpo, "guardar": False}), 200)
    return {"caso": "Una petición excede el tiempo máximo (costos congelado)", "pasos": pasos, "recuperacion_s": rec,
            "tiempo_maximo_s": float(os.environ.get("MICROSERVICIOS_TIEMPO", "4")), "respuesta_ms": r.get("ms"),
            "datos_a_medias": {"escenarios_antes": n0, "escenarios_despues": n1}, "log": log_de(r.get("traza_id"))}


CASOS = {"servicio": caso_servicio, "redis": caso_redis, "mongo": caso_mongo, "postgres": caso_postgres, "bucket": caso_bucket, "timeout": caso_timeout}


def reporte(res):
    o = ["# Fallos de infraestructura: qué pasa y cómo se recupera", "",
         f"Corrida del {res['fecha']} con `servicios/pruebas/demo_fallos_infra.py` ({res['entorno']}). Datos crudos: `fallos_infraestructura.json`.", "",
         "«Recuperación» es el tiempo desde que termina el comando que restablece la pieza hasta la primera respuesta correcta, sin "
         "reiniciar ningún otro servicio (los servicios reconectan solos a PostgreSQL, Redis y MongoDB en la siguiente petición).", "",
         "| Caso | Peticiones | Cumplen lo esperado | Recuperación |", "|---|---|---|---|"]
    for c in res["casos"]:
        if "omitido" in c:
            o.append(f"| {c['caso']} | — | — | {c['omitido']} |")
            continue
        p = [x for x in c["pasos"] if "cumple" in x]
        o.append(f"| {c['caso']} | {len(c['pasos'])} | {sum(x['cumple'] for x in p)} de {len(p)} | "
                 f"{str(c['recuperacion_s']) + ' s' if c.get('recuperacion_s') is not None else '—'} |")
    for c in res["casos"]:
        o += ["", f"## {c['caso']}", ""]
        if "omitido" in c:
            o.append(c["omitido"])
            continue
        o += ["| Paso | HTTP | Esperado | Código | Mensaje | ms | Traza |", "|---|---|---|---|---|---|---|"]
        for x in c["pasos"]:
            marca = "" if "cumple" not in x else (" ✓" if x["cumple"] else " ✗")
            o.append(f"| {x['paso']} | {x.get('http') or x.get('error')}{marca} | {x.get('esperado', '—')} | {x.get('codigo') or '—'} | "
                     f"{(x.get('mensaje') or '—')[:110]} | {x.get('ms')} | {(x.get('traza_id') or '—')[:8]} |")
        extra = {k: v for k, v in c.items() if k not in ("caso", "pasos", "log")}
        if extra:
            o += ["", "```json", json.dumps(extra, ensure_ascii=False, indent=2, default=str), "```"]
        if c.get("log"):
            o += ["", "Registro técnico de la traza del error (MongoDB `logs_tecnicos`):", "", "```json", json.dumps(c["log"], ensure_ascii=False, indent=2, default=str), "```"]
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / "fallos_infraestructura.md").write_text("\n".join(o) + "\n", encoding="utf-8")
    (SALIDA / "fallos_infraestructura.json").write_text(json.dumps(res, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--casos", default=",".join(CASOS))
    ap.add_argument("--entorno", default=os.environ.get("ENTORNO_DEMO", "docker compose local"))
    a = ap.parse_args()
    t = {"admin": login("admin@codex.mx"), "operador": login("operador.mh01@codex.mx"), "planeador": login("planeador@codex.mx"),
         "repartidor": login("repartidor1@codex.mx")}
    if not all(t.values()):
        raise SystemExit(f"No se pudo iniciar sesión con todas las cuentas: {[k for k, v in t.items() if not v]}")
    res = {"fecha": dt.datetime.now().astimezone().isoformat(timespec="seconds"), "entorno": a.entorno, "casos": []}
    for nombre in a.casos.split(","):
        print(f"== {nombre}", flush=True)
        res["casos"].append(CASOS[nombre](t))
        time.sleep(3)
    reporte(res)
    print(f"Escrito {SALIDA / 'fallos_infraestructura.md'}")


if __name__ == "__main__":
    main()
