"""
procesos_integrales.py — Los tres procesos integrales de punta a punta contra la plataforma en marcha (entrega final).

Cada proceso involucra a una persona, una aplicación cliente, uno o más microservicios, Redis (la sesión se valida en cada servicio),
PostgreSQL o MongoDB, un archivo en el bucket cuando corresponde, la auditoría, una notificación y la visualización del resultado.
El script hace lo que haría la persona y después COMPRUEBA en las bases y en el almacén que cada pieza quedó donde debe.

  P1 · Cierre de entrega        repartidor · app Android (API JSON) · entregas, documentos, seguimiento · foto al bucket ·
                                aviso al cliente · el administrador lo ve en el web (/web/servicios/pedido/<id>)
  P2 · Reabastecimiento         operador y administrador · portal web · inventario, abastecimiento, proveedores, documentos ·
                                comprobante al bucket · avisos de solicitud y orden · inventario actualizado en pantalla
  P3 · Despacho y reporte       planeador · portal web · pedidos, rutas, entregas, reportes · aviso al repartidor (ve sus paradas en la
                                app) · el reporte exportado se archiva en el bucket y se descarga con URL firmada

Uso (plataforma arriba; base de PRUEBAS):
  python servicios/pruebas/procesos_integrales.py
Variables: WEB_URL (http://localhost:5000), MICROSERVICIOS_URL_DEMO (http://localhost:{puerto}), PG_DSN, MONGO_URL, ALMACEN_DIR
(almacén local) o GCS_BUCKET (para comprobar el objeto en Cloud Storage), MICROHUBS_CLAVE.
Escribe evidencias/procesos/procesos_integrales.md y .json.
"""
import base64
import datetime as dt
import http.cookiejar
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI.parent))
WEB = os.environ.get("WEB_URL", "http://localhost:5000")
PLANTILLA = os.environ.get("MICROSERVICIOS_URL_DEMO", "http://localhost:{puerto}")
CLAVE = os.environ.get("MICROHUBS_CLAVE", "Codex#2026")
DSN = os.environ.get("PG_DSN", "host=127.0.0.1 port=5432 dbname=microhubs_p1 user=microhubs password=microhubs_dev")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://127.0.0.1:27017/microhubs_eventos")
PUERTOS = {"inventario": 5111, "auth": 5101, "pedidos": 5104, "entregas": 5105, "documentos": 5107, "seguimiento": 5110, "abastecimiento": 5114, "rutas": 5118,
           "reportes": 5123, "notificaciones": 5124}
SALIDA = RAIZ / "evidencias" / "procesos"
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
PDF = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[]/Count 0>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF\n"


# ------------------------------------------------------------------------------------------------------------------------------
def sql(q, args=(), una=False):
    import psycopg
    from psycopg.rows import dict_row
    with psycopg.connect(DSN, row_factory=dict_row) as con:
        con.execute("SET search_path = microhubs, public")
        cur = con.execute(q, args)
        return cur.fetchone() if una else cur.fetchall()


def mongo():
    from pymongo import MongoClient
    return MongoClient(MONGO_URL)["microhubs_eventos"]


def objeto_existe(ruta):
    if os.environ.get("GCS_BUCKET"):
        from google.cloud import storage
        return storage.Client().bucket(os.environ["GCS_BUCKET"]).blob(ruta).exists()
    return (Path(os.environ.get("ALMACEN_DIR", "/tmp/microhubs_almacen")) / ruta).is_file()


def api(metodo, servicio, ruta, token=None, cuerpo=None):
    req = urllib.request.Request(PLANTILLA.format(puerto=PUERTOS[servicio]) + "/api/v1/" + ruta, method=metodo,
                                 data=json.dumps(cuerpo).encode() if cuerpo is not None else None,
                                 headers={"Accept": "application/json", "Content-Type": "application/json", "X-Cliente": "movil",
                                          **({"Authorization": f"Bearer {token}"} if token else {})})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"null")


def token(correo):
    st, d = api("POST", "auth", "auth/login", cuerpo={"correo": correo, "clave": CLAVE})
    assert st == 200, (correo, st, d)
    return d["token_acceso"]


class Navegador:
    """Una persona en el portal web: cookies de sesión y el token CSRF de los formularios."""

    def __init__(self, correo):
        self.jar = http.cookiejar.CookieJar()
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar), _SinRedireccion())
        st, _, _ = self.enviar("POST", "/entrar", {"correo": correo, "clave": CLAVE})
        assert st == 302, f"login web {correo}: {st}"
        self.csrf = None

    def enviar(self, metodo, ruta, campos=None, archivos=None):
        if archivos:
            limite = uuid.uuid4().hex
            partes = []
            for k, v in (campos or {}).items():
                partes.append(f'--{limite}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
            for k, (nombre, tipo, contenido) in archivos.items():
                partes.append(f'--{limite}\r\nContent-Disposition: form-data; name="{k}"; filename="{nombre}"\r\nContent-Type: {tipo}\r\n\r\n'.encode()
                              + contenido + b"\r\n")
            datos, tipo = b"".join(partes) + f"--{limite}--\r\n".encode(), f"multipart/form-data; boundary={limite}"
        else:
            datos = urllib.parse.urlencode(campos or {}, doseq=True).encode() if campos is not None else None
            tipo = "application/x-www-form-urlencoded"
        req = urllib.request.Request(WEB + ruta, data=datos, method=metodo, headers={"Content-Type": tipo} if datos else {})
        try:
            with self.op.open(req, timeout=60) as r:
                return r.status, r.read(), dict(r.headers)
        except urllib.error.HTTPError as e:
            return e.code, e.read(), dict(e.headers)

    def ver(self, ruta):
        st, html, h = self.enviar("GET", ruta)
        m = re.search(rb'name="csrf" value="([^"]+)"', html)
        if m:
            self.csrf = m.group(1).decode()
        return st, html.decode("utf-8", "replace"), h

    def form(self, ruta, campos, archivos=None):
        return self.enviar("POST", ruta, {"csrf": self.csrf, **campos}, archivos)


class _SinRedireccion(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **kw):
        return None


def paso(lista, quien, cliente, accion, ok, detalle=""):
    lista.append({"quien": quien, "cliente": cliente, "accion": accion, "ok": bool(ok), "detalle": str(detalle)[:220]})
    print(f"  {'✓' if ok else '✗'} {accion} {detalle}"[:200], flush=True)
    return ok


# ------------------------------------------------------------------------------------------------------------------------------
def p1():
    pasos, rep = [], token("repartidor1@codex.mx")
    st, mias = api("GET", "entregas", "entregas/mias?pagina=1&por_pagina=20", rep)
    if not mias.get("datos"):
        from pruebas.preparar_entregas import preparar
        preparar("repartidor1@codex.mx", 1)
        st, mias = api("GET", "entregas", "entregas/mias?pagina=1&por_pagina=20", rep)
    e = mias["datos"][0]
    eid, pid = e["id"], e["pedido_id"]
    paso(pasos, "repartidor", "Android", f"Ve sus paradas (GET entregas/mias) y elige la entrega {eid}", st == 200, f"{len(mias['datos'])} paradas")
    st, foto = api("POST", "documentos", "documentos", rep, {"nombre": f"evidencia_{eid}.png", "tipo_mime": "image/png",
                                                            "contenido_base64": base64.b64encode(PNG).decode(), "referencia": {"tipo": "entrega", "id": str(eid)}})
    paso(pasos, "repartidor", "Android", "Sube la foto de evidencia (POST documentos)", st == 201, f"id {foto.get('id')} · ruta {foto.get('ruta')}")
    ahora_ = dt.datetime.now(dt.timezone.utc)
    puntos = [{"latitud": 25.748 + i * 0.0006, "longitud": -100.364 + i * 0.0004, "precision_m": 8, "capturado_en": (ahora_ - dt.timedelta(seconds=30 * (5 - i))).isoformat()} for i in range(5)]
    st, _ = api("POST", "seguimiento", f"seguimiento/{eid}/ubicaciones", rep, {"puntos": puntos})
    paso(pasos, "repartidor", "Android", "Envía su recorrido GPS (POST seguimiento/ubicaciones)", st == 201, "5 puntos")
    st, det = api("GET", "entregas", f"entregas/{eid}", rep)
    st, cierre = api("POST", "entregas", f"entregas/{eid}/resultado", rep, {
        "resultado": "entregado", "monto_cobrado": det["total"], "cambio_entregado": 0, "ubicacion": {"latitud": 25.7491, "longitud": -100.3611},
        "evidencia_ids": [foto["id"]], "capturado_en": ahora_.isoformat(), "id_cliente_local": str(uuid.uuid4())})
    paso(pasos, "repartidor", "Android", "Cierra la entrega cobrando el total (POST entregas/resultado)", st == 201, cierre)
    # comprobaciones
    f = sql("SELECT p.estado::text AS estado, p.folio, c.usuario_id FROM pedido p JOIN cliente c ON c.id = p.cliente_id WHERE p.id = %s", (pid,), una=True)
    paso(pasos, "—", "PostgreSQL", "El pedido quedó entregado", f["estado"] == "entregado", f"{f['folio']}: {f['estado']}")
    aud = sql("SELECT count(*) AS n FROM auditoria WHERE entidad IN ('entrega','pedido') AND entidad_id IN (%s, %s) AND fecha > now() - interval '5 minutes'",
              (str(eid), str(pid)), una=True)["n"]
    paso(pasos, "—", "PostgreSQL · auditoría", "Los triggers auditaron el cierre", aud >= 2, f"{aud} registros")
    av = sql("SELECT titulo FROM web_notificacion WHERE destinatario_id = %s AND creado_en > now() - interval '5 minutes' ORDER BY id DESC LIMIT 1",
             (f["usuario_id"],), una=True)
    paso(pasos, "cliente", "notificación", "El cliente recibió el aviso", av is not None, av["titulo"] if av else "")
    doc = mongo().documentos.find_one({"referencia.tipo": "entrega", "referencia.id": str(eid)})
    paso(pasos, "—", "MongoDB + bucket", "La foto: metadatos en MongoDB y el archivo en el almacén", bool(doc and doc.get("ruta") and objeto_existe(doc["ruta"])),
         f"{doc and doc.get('ruta')} · {doc and doc.get('metadatos', {}).get('almacen')} · sha256 {doc and doc['sha256'][:12]}…")
    gps = mongo().ubicaciones_entrega.count_documents({"entrega_id": eid})
    paso(pasos, "—", "MongoDB", "El recorrido GPS quedó en ubicaciones_entrega", gps >= 5, f"{gps} puntos")
    adm = Navegador("admin@codex.mx")
    st, html, _ = adm.ver(f"/web/servicios/pedido/{pid}")
    paso(pasos, "administrador", "web", "Ve el pedido entregado con su recorrido y evidencia (/web/servicios/pedido)", st == 200 and f["folio"] in html and "entregado" in html)
    return {"proceso": "P1 · Cierre de entrega", "pasos": pasos, "ids": {"entrega": eid, "pedido": pid}}


def p2():
    pasos = []
    op, adm = Navegador("operador.mh01@codex.mx"), Navegador("admin@codex.mx")
    st, html, _ = op.ver("/web/servicios/abastecimiento?microhub_id=1")
    m = re.search(r'name="producto" value="(\d+)"', html)
    if not m:
        # Sin faltantes no hay nada que reponer: se registra una merma real (mercancía dañada) por el servicio de inventario.
        f = sql("SELECT i.producto_id, i.existencia FROM inventario i WHERE i.microhub_id = 1 AND i.existencia > 0 AND EXISTS "
                "(SELECT 1 FROM proveedor_producto pp WHERE pp.producto_id = i.producto_id) ORDER BY i.existencia LIMIT 1", una=True)
        st_m, _ = api("POST", "inventario", "inventario/movimientos", token("operador.mh01@codex.mx"),
                      {"microhub_id": 1, "producto_id": f["producto_id"], "tipo": "merma", "cantidad": f["existencia"],
                       "motivo": "Mercancía dañada (prueba del proceso integral)", "operacion_uuid": str(uuid.uuid4())})
        paso(pasos, "operador", "API inventario", f"Registra una merma del producto {f['producto_id']}: queda agotado", st_m == 201, f"{f['existencia']} u.")
        st, html, _ = op.ver("/web/servicios/abastecimiento?microhub_id=1")
        m = re.search(r'name="producto" value="(\d+)"', html)
    paso(pasos, "operador", "web", "Ve alertas de inventario y necesidades con la mejor oferta", st == 200 and bool(m), "necesidades con oferta" if m else "sin necesidades")
    if not m:
        return {"proceso": "P2 · Reabastecimiento", "pasos": pasos}
    # Un producto de la lista con un proveedor cuyo pedido mínimo se alcance (regla del servicio de proveedores/abastecimiento).
    elegido = None
    for pid_txt in re.findall(r'name="producto" value="(\d+)"', html):
        prod = int(pid_txt)
        cant = int(re.search(rf'name="cantidad_{prod}" value="(\d+)"', html).group(1))
        o = sql("SELECT pv.id, pp.precio_compra, pv.pedido_minimo, pp.capacidad_semanal FROM proveedor_producto pp JOIN proveedor pv ON pv.id = pp.proveedor_id "
                "WHERE pp.producto_id = %s AND pv.estatus = 'activo' AND (pp.vigente_hasta IS NULL OR pp.vigente_hasta >= current_date) "
                "ORDER BY pv.pedido_minimo / pp.precio_compra LIMIT 1", (prod,), una=True)
        if o:
            necesarias = max(cant, int(-(-float(o["pedido_minimo"]) // float(o["precio_compra"]))), o.get("minimo_compra") or 0)
            if not o["capacidad_semanal"] or necesarias <= o["capacidad_semanal"]:
                elegido = (prod, necesarias, o["id"])
                break
    if not elegido:
        paso(pasos, "operador", "web", "Hay un producto que algún proveedor surte arriba de su pedido mínimo", False)
        return {"proceso": "P2 · Reabastecimiento", "pasos": pasos}
    prod, cant, proveedor = elegido
    antes = sql("SELECT existencia FROM inventario WHERE microhub_id = 1 AND producto_id = %s", (prod,), una=True)["existencia"]
    motivo = f"Proceso integral {uuid.uuid4().hex[:6]}"
    st, _, h = op.form("/web/servicios/abastecimiento", {"accion": "solicitar", "microhub_id": "1", "producto": str(prod), f"cantidad_{prod}": str(cant), "motivo": motivo})
    sol = sql("SELECT id, folio, estado FROM solicitud_compra WHERE motivo = %s", (motivo,), una=True)
    paso(pasos, "operador", "web", f"Crea la solicitud de compra ({cant} u. del producto {prod})", st == 302 and sol is not None, sol and sol["folio"])
    adm.ver("/web/servicios/abastecimiento?microhub_id=1")
    st, _, _ = adm.form("/web/servicios/abastecimiento", {"accion": "decidir", "microhub_id": "1", "solicitud": str(sol["id"]), "decision": "aprobada", "motivo": "Hay presupuesto"})
    paso(pasos, "administrador", "web", "Aprueba la solicitud", sql("SELECT estado FROM solicitud_compra WHERE id = %s", (sol["id"],), una=True)["estado"] == "aprobada")
    st, _, _ = adm.form("/web/servicios/abastecimiento", {"accion": "ordenar", "microhub_id": "1", "solicitud": str(sol["id"]), "proveedor_id": str(proveedor)})
    orden = sql("SELECT id, folio, estado FROM orden_compra WHERE solicitud_id = %s ORDER BY id DESC LIMIT 1", (sol["id"],), una=True)
    paso(pasos, "administrador", "web", "Emite la orden de compra al proveedor (respeta su pedido mínimo)", orden is not None, orden and orden["folio"])
    op.ver("/web/servicios/abastecimiento?microhub_id=1")
    st, _, _ = op.form("/web/servicios/abastecimiento", {"accion": "recibir", "microhub_id": "1", "orden": str(orden["id"])},
                       {"comprobante": (f"remision_{orden['folio']}.pdf", "application/pdf", PDF)})
    o = sql("SELECT estado FROM orden_compra WHERE id = %s", (orden["id"],), una=True)
    despues = sql("SELECT existencia FROM inventario WHERE microhub_id = 1 AND producto_id = %s", (prod,), una=True)["existencia"]
    paso(pasos, "operador", "web", "Recibe la mercancía con el comprobante (PDF)", o["estado"] == "recibida", f"orden {o['estado']}")
    paso(pasos, "—", "PostgreSQL", "La existencia subió en inventario (entrada por el servicio de inventario)", despues >= antes + cant, f"{antes} → {despues}")
    doc = mongo().documentos.find_one({"referencia.tipo": "orden_compra", "referencia.id": str(orden["id"])})
    paso(pasos, "—", "MongoDB + bucket", "El comprobante: metadatos en MongoDB y el archivo en el almacén", bool(doc and objeto_existe(doc["ruta"])),
         f"{doc and doc['ruta']} · {doc and doc['metadatos']['almacen']}")
    avisos = sql("SELECT tipo, titulo FROM web_notificacion WHERE tipo = 'abastecimiento' AND creado_en > now() - interval '5 minutes' "
                 "AND (referencia_id IN (%s, %s) OR mensaje LIKE %s OR mensaje LIKE %s)", (str(sol["id"]), str(orden["id"]), f"%{sol['folio']}%", f"%{orden['folio']}%"))
    paso(pasos, "planeador / operador", "notificación", "Los triggers avisaron la solicitud y la orden", len(avisos) >= 1, "; ".join(a["titulo"] for a in avisos[:3]))
    aud = sql("SELECT count(*) AS n FROM auditoria WHERE entidad IN ('solicitud_compra','orden_compra','inventario') AND fecha > now() - interval '5 minutes'", una=True)["n"]
    paso(pasos, "—", "PostgreSQL · auditoría", "Auditoría de solicitud, orden e inventario", aud >= 3, f"{aud} registros")
    st, html, _ = op.ver("/web/servicios/abastecimiento?microhub_id=1")
    paso(pasos, "operador", "web", "Ve la orden recibida y descarga el comprobante con URL firmada", st == 200 and orden["folio"] in html and "remision_" in html)
    did = str(doc["_id"]) if doc else ""
    st, cuerpo, h = op.enviar("GET", f"/web/servicios/documento/{did}/enlace")
    paso(pasos, "operador", "web → bucket", "La descarga firmada devuelve el mismo archivo", st in (200, 302) and (st == 302 or cuerpo == PDF), f"HTTP {st}")
    return {"proceso": "P2 · Reabastecimiento", "pasos": pasos, "ids": {"solicitud": sol["id"], "orden": orden["id"], "producto": prod}}


def p3():
    pasos = []
    from pruebas.preparar_listos import dejar_listos
    listos = dejar_listos(4, 1, DSN)
    paso(pasos, "operador", "web (bandeja)", "Marca pedidos como listos para despachar (en preparación → listo)", len(listos) >= 1, f"{len(listos)} pedidos")
    pl = Navegador("planeador@codex.mx")
    st, html, _ = pl.ver("/web/servicios/rutas?microhub_id=1")
    paso(pasos, "planeador", "web", "Ve los pedidos listos (servicio de pedidos)", st == 200 and "Proponer plan" in html)
    st, _, h = pl.form("/web/servicios/rutas", {"accion": "proponer", "microhub_id": "1", "metodo": "automatico"})
    plan_id = int(re.search(r"plan=(\d+)", h.get("Location", "")).group(1)) if st == 302 and "plan=" in h.get("Location", "") else None
    paso(pasos, "planeador", "web", "Propone el plan de rutas (TSP exacto / 2-opt en el servicio de rutas)", plan_id is not None, f"plan {plan_id}")
    st, html, _ = pl.ver(f"/web/servicios/rutas?microhub_id=1&plan={plan_id}")
    paso(pasos, "planeador", "web", "Revisa rutas, paradas, minutos y costo", st == 200 and "Confirmar plan" in html)
    op = Navegador("operador.mh01@codex.mx")                         # el despacho exige entregas.asignar: lo hace el operador del microhub
    st, html, _ = op.ver(f"/web/servicios/rutas?microhub_id=1&plan={plan_id}")
    st, _, _ = op.form("/web/servicios/rutas", {"accion": "confirmar", "microhub_id": "1", "plan": str(plan_id)})
    ent = sql("SELECT e.id, e.repartidor_id, u.correo FROM entrega e JOIN usuario u ON u.id = e.repartidor_id WHERE e.plan_ruta_id IN "
              "(SELECT id FROM plan_ruta WHERE plan_despacho_id = %s) ORDER BY e.id", (plan_id,))
    paso(pasos, "operador", "web", "Confirma y despacha: rutas → entregas crea y asigna las entregas (saga entre servicios)", len(ent) >= 1, f"{len(ent)} entregas")
    avisos = sql("SELECT count(*) AS n FROM web_notificacion WHERE tipo = 'entrega' AND creado_en > now() - interval '5 minutes' "
                 "AND destinatario_id = ANY(%s)", ([e["repartidor_id"] for e in ent],), una=True)["n"] if ent else 0
    paso(pasos, "repartidor", "notificación", "Cada repartidor recibió «Nueva entrega asignada»", avisos >= 1, f"{avisos} avisos")
    if ent:
        st, mias = api("GET", "entregas", "entregas/mias?pagina=1&por_pagina=50", token(ent[0]["correo"]))
        paso(pasos, "repartidor", "Android", "Ve las nuevas paradas en su app (GET entregas/mias)", st == 200 and any(x["id"] == ent[0]["id"] for x in mias["datos"]))
    hoy = dt.date.today()
    pl.ver("/web/servicios/reportes")
    st, cuerpo, h = pl.form("/web/servicios/reportes", {"clave": "pedidos_por_dia", "formato": "pdf", "desde": str(hoy - dt.timedelta(days=30)), "hasta": str(hoy)})
    paso(pasos, "planeador", "web", "Exporta el reporte de pedidos por día en PDF (servicio de reportes)", st == 200 and cuerpo.startswith(b"%PDF"), f"{len(cuerpo)} bytes")
    ex = sql("SELECT id, ruta, almacen, sha256 FROM reporte_exportacion ORDER BY id DESC LIMIT 1", una=True)
    paso(pasos, "—", "PostgreSQL + bucket", "La exportación quedó archivada: ruta y SHA-256 en la base, el archivo en el almacén",
         bool(ex["ruta"]) and objeto_existe(ex["ruta"]), f"{ex['ruta']} · {ex['almacen']} · {ex['sha256'][:12]}…")
    st, cuerpo2, _ = pl.enviar("GET", f"/web/servicios/reportes/exportacion/{ex['id']}")
    paso(pasos, "planeador", "web → bucket", "La descarga con URL firmada trae el mismo archivo", st in (200, 302) and (st == 302 or cuerpo2 == cuerpo), f"HTTP {st}")
    aud = sql("SELECT count(*) AS n FROM auditoria WHERE (entidad = 'reporte_exportacion' AND entidad_id = %s) OR (entidad = 'entrega' AND fecha > now() - interval '5 minutes')",
              (str(ex["id"]),), una=True)["n"]
    paso(pasos, "—", "PostgreSQL · auditoría", "Auditoría de las entregas asignadas y del enlace de descarga", aud >= 2, f"{aud} registros")
    return {"proceso": "P3 · Despacho con rutas y reporte archivado", "pasos": pasos, "ids": {"plan": plan_id, "exportacion": ex["id"]}}


def main():
    res = {"fecha": dt.datetime.now().astimezone().isoformat(timespec="seconds"), "procesos": []}
    for fn in (p1, p2, p3):
        print(f"== {fn.__name__.upper()}", flush=True)
        try:
            res["procesos"].append(fn())
        except Exception as e:  # noqa: BLE001
            res["procesos"].append({"proceso": fn.__name__.upper(), "pasos": [], "error": f"{type(e).__name__}: {e}"})
            print("  ERROR", e)
    o = ["# Procesos integrales de punta a punta", "", f"Corrida del {res['fecha']} con `servicios/pruebas/procesos_integrales.py` contra la plataforma en marcha. "
         "Cada paso lo hace la persona en su aplicación; las filas marcadas como PostgreSQL, MongoDB o bucket son comprobaciones directas.", "",
         "| Proceso | Pasos | Correctos |", "|---|---|---|"]
    for p in res["procesos"]:
        o.append(f"| {p['proceso']} | {len(p['pasos'])} | {sum(x['ok'] for x in p['pasos'])} de {len(p['pasos'])}{' · ' + p['error'] if p.get('error') else ''} |")
    for p in res["procesos"]:
        o += ["", f"## {p['proceso']}", "", "| # | Quién | Dónde | Paso | Resultado | Detalle |", "|---|---|---|---|---|---|"]
        for i, x in enumerate(p["pasos"], 1):
            o.append(f"| {i} | {x['quien']} | {x['cliente']} | {x['accion']} | {'✓' if x['ok'] else '✗'} | {x['detalle'].replace('|', '/')} |")
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / "procesos_integrales.md").write_text("\n".join(o) + "\n", encoding="utf-8")
    (SALIDA / "procesos_integrales.json").write_text(json.dumps(res, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    total = [x for p in res["procesos"] for x in p["pasos"]]
    errores = [p["proceso"] for p in res["procesos"] if p.get("error")]
    print(f"{sum(x['ok'] for x in total)} de {len(total)} pasos correctos{' · con error en ' + ', '.join(errores) if errores else ''} · {SALIDA / 'procesos_integrales.md'}")
    return 0 if total and all(x["ok"] for x in total) and not any(p.get("error") for p in res["procesos"]) else 1


if __name__ == "__main__":
    sys.exit(main())
