"""
Servicio de abastecimiento · puerto 5114 · contrato v1

  GET  /api/v1/abastecimiento/necesidades                  qué hay que reponer en un microhub y a qué costo
  GET  /api/v1/abastecimiento/solicitudes                  solicitudes de compra (microhub_id, estado)
  POST /api/v1/abastecimiento/solicitudes                  un microhub pide mercancía (abastecimiento.solicitar)
  GET  /api/v1/abastecimiento/solicitudes/{id}             una solicitud con sus líneas
  POST /api/v1/abastecimiento/solicitudes/{id}/decision    aprueba o rechaza (abastecimiento.aprobar)
  POST /api/v1/abastecimiento/solicitudes/{id}/ordenar     convierte una solicitud aprobada en órdenes a proveedores
  GET  /api/v1/abastecimiento/ordenes                      órdenes de compra (microhub_id, proveedor_id, estado, atrasadas)
  GET  /api/v1/abastecimiento/ordenes/{id}                 una orden con lo recibido de cada línea
  POST /api/v1/abastecimiento/ordenes/{id}/recepcion       registra la mercancía que llegó (abastecimiento.recibir)
  POST /api/v1/abastecimiento/ordenes/{id}/cancelar        cancela una orden sin recepciones
  GET  /api/v1/abastecimiento/seguimiento                  cuántas solicitudes y órdenes hay en cada estado

Responsabilidad única: el ciclo de reposición, desde que falta un producto hasta que llega.
No guarda existencias ni precios de compra: pide las alertas al servicio de inventario, las ofertas al
de proveedores, y cuando llega mercancía le manda a inventario la entrada.

Recepción sin pérdidas: cada recepción se guarda ANTES de llamar a inventario y lleva una
operacion_uuid; inventario ignora una entrada repetida. Si inventario no responde, la recepción queda
«pendiente» (respuesta 202) y se reintenta con el mismo POST sin líneas, sin duplicar existencias.
"""
import datetime as dt
import math
import uuid as uuidlib
from decimal import Decimal

from flask import g

from comun import config
from comun.base import (crear_app, documentar, filtro_entero, filtro_opcion, leer_cuerpo, leer_paginacion, lista,
                        limitar_microhub, microhub_del_usuario, paginacion, requiere, responder)
from comun.base_errores import ErrorApi, conflicto, filtro_invalido, invalido, no_encontrado
from comun.clientes import exigir, mapa
from comun.datos import conexion, consultar, parametro
from comun.formatos import ZONA, dinero, fecha
from comun.validar import Campo, validar

app = crear_app("abastecimiento", "Microhubs · Abastecimiento",
                "Necesidades de reposición, solicitudes de compra, órdenes a proveedores y recepción de mercancía.", 5114)
P = config.PREFIJO
ESTADOS_SOLICITUD = ["pendiente", "aprobada", "rechazada", "ordenada"]
ESTADOS_ORDEN = ["emitida", "parcial", "recibida", "cancelada"]


# --------------------------------------------------------------------
# Cálculo (funciones puras, sin bases de datos)
# --------------------------------------------------------------------
def D(valor):
    return Decimal(str(valor))


def cantidad_sugerida(disponible, minimo, en_camino, solicitado, factor):
    """Unidades que faltan para llegar al nivel objetivo (mínimo × factor), sin contar lo que ya viene en camino
    ni lo que ya se pidió."""
    objetivo = math.ceil(D(minimo) * D(factor))
    return max(int(objetivo) - disponible - en_camino - solicitado, 0)


def estado_orden(lineas):
    """lineas: [(cantidad, cantidad_recibida)]. recibida si todo llegó, parcial si llegó algo, emitida si nada."""
    if lineas and all(r >= c for c, r in lineas):
        return "recibida"
    return "parcial" if any(r > 0 for _, r in lineas) else "emitida"


def planear_ordenes(lineas, ofertas, proveedor_id=None):
    """Reparte las líneas de una solicitud entre proveedores.

    Para cada línea elige la oferta más barata (a igual precio, la de entrega más rápida) que alcance la cantidad
    pedida y respete la compra mínima. Con `proveedor_id` solo considera a ese proveedor. Las líneas del mismo
    proveedor forman una orden, que debe alcanzar su pedido mínimo.
    Devuelve ({proveedor_id: grupo}, [problemas])."""
    por_producto = {}
    for o in ofertas:
        if proveedor_id and o["proveedor"]["id"] != proveedor_id:
            continue
        por_producto.setdefault(o["producto"]["id"], []).append(o)
    grupos, problemas = {}, []
    for l in lineas:
        candidatas = sorted(por_producto.get(l["producto_id"], []), key=lambda o: (D(o["precio_compra"]), o["dias_entrega"]))
        elegida = next((o for o in candidatas if o["capacidad_semanal"] >= l["cantidad"] and o["minimo_compra"] <= l["cantidad"]), None)
        if elegida is None:
            motivo = ("Ningún proveedor lo surte." if not candidatas else
                      "Ninguna oferta alcanza la cantidad pedida o respeta la compra mínima.")
            problemas.append({"campo": f"producto {l['producto_id']}", "mensaje": motivo})
            continue
        grupo = grupos.setdefault(elegida["proveedor"]["id"], {
            "proveedor": elegida["proveedor"], "dias_entrega": elegida["dias_entrega"], "pedido_minimo": D(elegida["pedido_minimo"]), "lineas": []})
        grupo["lineas"].append({"producto_id": l["producto_id"], "cantidad": l["cantidad"], "precio_compra": D(elegida["precio_compra"])})
    for grupo in grupos.values():
        grupo["total"] = sum((l["precio_compra"] * l["cantidad"] for l in grupo["lineas"]), Decimal(0))
        if grupo["total"] < grupo["pedido_minimo"]:
            problemas.append({"campo": f"proveedor {grupo['proveedor']['nombre']}",
                              "mensaje": f"Su pedido mínimo es de {grupo['pedido_minimo']:.2f} y la orden suma {grupo['total']:.2f}. "
                                         "Indica proveedor_id para concentrar las líneas en uno."})
    return grupos, problemas


def hoy():
    return dt.datetime.now(ZONA).date()


# --------------------------------------------------------------------
# Presentación
# --------------------------------------------------------------------
def productos():
    return mapa("productos", "productos")


def nombre_producto(prod, pid):
    p = prod.get(pid)
    return {"id": pid, "nombre": p["nombre"] if p else None}


def lineas_de(tabla, campo, ids):
    """{id: [filas]} de las líneas de varias solicitudes u órdenes en una sola consulta."""
    if not ids:
        return {}
    extra = ", precio_compra, cantidad_recibida" if tabla == "orden_compra_linea" else ""
    filas = consultar(f"SELECT {campo}, producto_id, cantidad{extra} FROM {tabla} WHERE {campo} = ANY(%s) ORDER BY {campo}, producto_id",
                      (list(ids),))
    salida = {}
    for f in filas:
        salida.setdefault(f[campo], []).append(f)
    return salida


def solicitud(f, lineas, prod):
    return {"id": f["id"], "folio": f["folio"], "microhub_id": f["microhub_id"], "estado": f["estado"], "motivo": f["motivo"],
            "solicitada_por": f["solicitada_por"], "decidida_por": f["decidida_por"], "decision_motivo": f["decision_motivo"],
            "decidida_en": fecha(f["decidida_en"]), "creada_en": fecha(f["creada_en"]),
            "lineas": [{"producto": nombre_producto(prod, l["producto_id"]), "cantidad": l["cantidad"]} for l in lineas]}


def orden(f, lineas, pendientes, prod, provs):
    pv = provs.get(f["proveedor_id"])
    return {"id": f["id"], "folio": f["folio"], "solicitud_id": f["solicitud_id"],
            "proveedor": {"id": f["proveedor_id"], "nombre": pv["nombre"] if pv else None}, "microhub_id": f["microhub_id"],
            "estado": f["estado"], "fecha_esperada": f["fecha_esperada"].isoformat(), "total": dinero(f["total"]),
            "creada_en": fecha(f["creada_en"]), "cerrada_en": fecha(f["cerrada_en"]),
            "lineas": [{"producto": nombre_producto(prod, l["producto_id"]), "cantidad": l["cantidad"],
                        "precio_compra": dinero(l["precio_compra"]), "cantidad_recibida": l["cantidad_recibida"],
                        "pendiente_inventario": pendientes.get((f["id"], l["producto_id"]), 0)} for l in lineas]}


SQL_SOLICITUD = ("SELECT id, folio, microhub_id, estado, motivo, solicitada_por, decidida_por, decision_motivo, decidida_en, creada_en "
                 "FROM solicitud_compra ")
SQL_ORDEN = ("SELECT id, folio, solicitud_id, proveedor_id, microhub_id, estado, fecha_esperada, total, creada_en, cerrada_en "
             "FROM orden_compra ")


def armar_solicitudes(filas):
    prod, lineas = productos(), lineas_de("solicitud_compra_linea", "solicitud_id", [f["id"] for f in filas])
    return [solicitud(f, lineas.get(f["id"], []), prod) for f in filas]


def armar_ordenes(filas):
    prod, provs = productos(), mapa("proveedores", "proveedores")
    ids = [f["id"] for f in filas]
    lineas = lineas_de("orden_compra_linea", "orden_id", ids)
    pendientes = {}
    if ids:
        for r in consultar("SELECT orden_id, producto_id, sum(cantidad)::integer AS n FROM orden_compra_recepcion "
                           "WHERE orden_id = ANY(%s) AND NOT aplicada GROUP BY orden_id, producto_id", (ids,)):
            pendientes[(r["orden_id"], r["producto_id"])] = r["n"]
    return [orden(f, lineas.get(f["id"], []), pendientes, prod, provs) for f in filas]


def _solicitud(sid):
    f = consultar(SQL_SOLICITUD + "WHERE id = %s", (sid,), una=True)
    if not f or _ajeno(f["microhub_id"]):
        raise no_encontrado("No existe esa solicitud de compra.")
    return f


def _orden(oid):
    f = consultar(SQL_ORDEN + "WHERE id = %s", (oid,), una=True)
    if not f or _ajeno(f["microhub_id"]):
        raise no_encontrado("No existe esa orden de compra.")
    return f


def _ajeno(microhub_id):
    propio = microhub_del_usuario()
    return g.usuario["rol"] in ("operador", "supervisor") and propio != microhub_id


# --------------------------------------------------------------------
# Necesidades
# --------------------------------------------------------------------
@app.get(f"{P}/abastecimiento/necesidades")
@requiere("abastecimiento.ver")
def necesidades():
    pagina, por, desde = leer_paginacion()
    hub = limitar_microhub(filtro_entero("microhub_id"))
    if not hub:
        raise filtro_invalido("microhub_id", "microhub_id es obligatorio.")
    alertas, p = [], 1
    while p <= 5:                                           # hasta 500 alertas del microhub
        pag = exigir("inventario", "GET", "inventario/alertas", params={"microhub_id": hub, "por_pagina": 100, "pagina": p})
        alertas += pag["datos"]
        if p >= pag["paginacion"]["paginas"]:
            break
        p += 1
    pids = [a["producto"]["id"] for a in alertas]
    en_camino = {r["producto_id"]: r["n"] for r in consultar(
        "SELECT l.producto_id, sum(l.cantidad - l.cantidad_recibida)::integer AS n FROM orden_compra_linea l "
        "JOIN orden_compra o ON o.id = l.orden_id WHERE o.microhub_id = %s AND o.estado IN ('emitida', 'parcial') "
        "AND l.producto_id = ANY(%s) GROUP BY l.producto_id", (hub, pids))} if pids else {}
    pedido = {r["producto_id"]: r["n"] for r in consultar(
        "SELECT l.producto_id, sum(l.cantidad)::integer AS n FROM solicitud_compra_linea l "
        "JOIN solicitud_compra s ON s.id = l.solicitud_id WHERE s.microhub_id = %s AND s.estado IN ('pendiente', 'aprobada') "
        "AND l.producto_id = ANY(%s) GROUP BY l.producto_id", (hub, pids))} if pids else {}
    factor = float(parametro("reposicion_factor_objetivo", 3))
    filas = []
    for a in alertas:
        pid = a["producto"]["id"]
        falta = cantidad_sugerida(a["disponible"], a["minimo"], en_camino.get(pid, 0), pedido.get(pid, 0), factor)
        if falta > 0:
            filas.append((a, falta))
    ofertas = {}
    if filas:
        try:
            todas = exigir("proveedores", "GET", "proveedores/ofertas",
                           params={"producto_ids": ",".join(str(a["producto"]["id"]) for a, _ in filas), "mejor": "true", "por_pagina": 100})
            ofertas = {o["producto"]["id"]: o for o in todas["datos"]}
        except ErrorApi as e:
            if e.status != 503:
                raise                                       # sin proveedores se muestran las necesidades, sin oferta
    total = len(filas)
    pagina_filas = filas[desde:desde + por]

    def necesidad(par):
        a, falta = par
        pid = a["producto"]["id"]
        o = ofertas.get(pid)
        comprar = max(falta, o["minimo_compra"]) if o else falta
        return {"producto": {"id": pid, "nombre": a["producto"]["nombre"]}, "existencia": a["existencia"], "minimo": a["minimo"],
                "disponible": a["disponible"],
                "en_camino": en_camino.get(pid, 0), "solicitado": pedido.get(pid, 0), "cantidad_sugerida": falta,
                "cantidad_a_comprar": comprar,
                "mejor_oferta": ({"proveedor": {"id": o["proveedor"]["id"], "nombre": o["proveedor"]["nombre"]},
                                  "precio_compra": dinero(o["precio_compra"]), "dias_entrega": o["dias_entrega"],
                                  "capacidad_semanal": o["capacidad_semanal"], "minimo_compra": o["minimo_compra"]} if o else None),
                "costo_estimado": dinero(D(o["precio_compra"]) * comprar) if o else None}
    return responder({"microhub_id": hub, "factor_objetivo": factor, "datos": [necesidad(x) for x in pagina_filas],
                      "paginacion": paginacion(pagina, por, total)}, raiz="necesidades", items={"datos": "necesidad"})


# --------------------------------------------------------------------
# Solicitudes
# --------------------------------------------------------------------
@app.get(f"{P}/abastecimiento/solicitudes")
@requiere("abastecimiento.ver")
def solicitudes():
    pagina, por, desde = leer_paginacion()
    estado, hub = filtro_opcion("estado", ESTADOS_SOLICITUD), limitar_microhub(filtro_entero("microhub_id"))
    where, args = ["TRUE"], []
    for cond, valor in (("microhub_id = %s", hub), ("estado = %s", estado)):
        if valor:
            where.append(cond); args.append(valor)
    w = " AND ".join(where)
    total = consultar(f"SELECT count(*) AS n FROM solicitud_compra WHERE {w}", args, una=True)["n"]
    filas = consultar(SQL_SOLICITUD + f"WHERE {w} ORDER BY id DESC LIMIT %s OFFSET %s", (*args, por, desde))
    return responder({"datos": armar_solicitudes(filas), "paginacion": paginacion(pagina, por, total)},
                     raiz="solicitudes", items={"datos": "solicitud"})


@app.post(f"{P}/abastecimiento/solicitudes")
@requiere("abastecimiento.solicitar")
def pedir():
    d = validar(leer_cuerpo("solicitud_nueva"), [Campo("microhub_id", "int", minimo=1), Campo("motivo", req=False, nulo=True, max_len=300),
                                                 Campo("lineas", "lista")])
    hub = limitar_microhub(d["microhub_id"])
    if not 1 <= len(d["lineas"]) <= 100:
        raise invalido("lineas", "Envía entre 1 y 100 líneas.")
    campos = [Campo("producto_id", "int", minimo=1), Campo("cantidad", "int", minimo=1, maximo=100000)]
    lineas = [validar(l if isinstance(l, dict) else {}, campos, prefijo=f"lineas[{i}].") for i, l in enumerate(d["lineas"])]
    if len({l["producto_id"] for l in lineas}) != len(lineas):
        raise invalido("lineas", "Un producto no puede aparecer dos veces en la misma solicitud.")
    with conexion() as con, con.cursor() as cur:
        cur.execute("INSERT INTO solicitud_compra (microhub_id, motivo, solicitada_por) VALUES (%s, %s, %s) RETURNING id",
                    (hub, d.get("motivo"), g.usuario["id"]))
        sid = cur.fetchone()["id"]
        for l in lineas:
            cur.execute("INSERT INTO solicitud_compra_linea (solicitud_id, producto_id, cantidad) VALUES (%s, %s, %s)",
                        (sid, l["producto_id"], l["cantidad"]))
    return responder(armar_solicitudes([_solicitud(sid)])[0], 201, raiz="solicitud", items={"lineas": "linea"})


@app.get(f"{P}/abastecimiento/solicitudes/<int:sid>")
@requiere("abastecimiento.ver")
def solicitud_una(sid):
    return responder(armar_solicitudes([_solicitud(sid)])[0], raiz="solicitud", items={"lineas": "linea"})


@app.post(f"{P}/abastecimiento/solicitudes/<int:sid>/decision")
@requiere("abastecimiento.aprobar")
def decidir(sid):
    d = validar(leer_cuerpo("decision_compra"), [Campo("decision", opciones=["aprobada", "rechazada"]),
                                                  Campo("motivo", req=False, nulo=True, max_len=300)])
    if d["decision"] == "rechazada" and not (d.get("motivo") or "").strip():
        raise invalido("motivo", "Rechazar una solicitud exige el motivo.")
    _solicitud(sid)
    with conexion() as con, con.cursor() as cur:
        cur.execute("SELECT estado FROM solicitud_compra WHERE id = %s FOR UPDATE", (sid,))
        if cur.fetchone()["estado"] != "pendiente":
            raise conflicto("La solicitud ya fue decidida.")
        cur.execute("UPDATE solicitud_compra SET estado = %s, decision_motivo = %s, decidida_por = %s, decidida_en = now() WHERE id = %s",
                    (d["decision"], (d.get("motivo") or "").strip() or None, g.usuario["id"], sid))
    return responder(armar_solicitudes([_solicitud(sid)])[0], raiz="solicitud", items={"lineas": "linea"})


def traer_ofertas(pids):
    """Todas las ofertas vigentes de los productos, página por página."""
    ofertas, p = [], 1
    while p <= 10:
        pag = exigir("proveedores", "GET", "proveedores/ofertas",
                     params={"producto_ids": ",".join(map(str, pids)), "por_pagina": 100, "pagina": p})
        ofertas += pag["datos"]
        if p >= pag["paginacion"]["paginas"]:
            break
        p += 1
    return ofertas


@app.post(f"{P}/abastecimiento/solicitudes/<int:sid>/ordenar")
@requiere("abastecimiento.aprobar")
def ordenar(sid):
    d = validar(leer_cuerpo("ordenar_nuevo", obligatorio=False), [Campo("proveedor_id", "int", req=False, nulo=True, minimo=1)])
    s = _solicitud(sid)
    lineas = [{"producto_id": l["producto_id"], "cantidad": l["cantidad"]}
              for l in lineas_de("solicitud_compra_linea", "solicitud_id", [sid]).get(sid, [])]
    if s["estado"] != "aprobada":
        raise conflicto(f"Solo se ordena una solicitud aprobada; esta está {s['estado']}.")
    grupos, problemas = planear_ordenes(lineas, traer_ofertas([l["producto_id"] for l in lineas]), d.get("proveedor_id"))
    if problemas:
        raise ErrorApi(422, "VALIDACION", "No se pudo armar la orden con esas ofertas.", problemas)
    creadas = []
    with conexion() as con, con.cursor() as cur:
        cur.execute("SELECT estado FROM solicitud_compra WHERE id = %s FOR UPDATE", (sid,))
        if cur.fetchone()["estado"] != "aprobada":
            raise conflicto("La solicitud ya se ordenó.")
        for grupo in grupos.values():
            cur.execute("INSERT INTO orden_compra (solicitud_id, proveedor_id, microhub_id, fecha_esperada, total, creada_por) "
                        "VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
                        (sid, grupo["proveedor"]["id"], s["microhub_id"], hoy() + dt.timedelta(days=grupo["dias_entrega"]),
                         grupo["total"], g.usuario["id"]))
            oid = cur.fetchone()["id"]
            creadas.append(oid)
            for l in grupo["lineas"]:
                cur.execute("INSERT INTO orden_compra_linea (orden_id, producto_id, cantidad, precio_compra) VALUES (%s,%s,%s,%s)",
                            (oid, l["producto_id"], l["cantidad"], l["precio_compra"]))
        cur.execute("UPDATE solicitud_compra SET estado = 'ordenada' WHERE id = %s", (sid,))
    filas = consultar(SQL_ORDEN + "WHERE id = ANY(%s) ORDER BY id", (creadas,))
    return responder({"solicitud_id": sid, "ordenes": armar_ordenes(filas)}, 201, raiz="ordenes_generadas",
                     items={"ordenes": "orden", "lineas": "linea"})


# --------------------------------------------------------------------
# Órdenes
# --------------------------------------------------------------------
@app.get(f"{P}/abastecimiento/ordenes")
@requiere("abastecimiento.ver")
def ordenes():
    pagina, por, desde = leer_paginacion()
    estado, hub = filtro_opcion("estado", ESTADOS_ORDEN), limitar_microhub(filtro_entero("microhub_id"))
    atrasadas = filtro_opcion("atrasadas", ["true", "false"]) == "true"
    where, args = ["TRUE"], []
    for cond, valor in (("microhub_id = %s", hub), ("estado = %s", estado), ("proveedor_id = %s", filtro_entero("proveedor_id")),
                        ("solicitud_id = %s", filtro_entero("solicitud_id"))):
        if valor:
            where.append(cond); args.append(valor)
    if atrasadas:
        where.append("estado IN ('emitida', 'parcial') AND fecha_esperada < %s"); args.append(hoy())
    w = " AND ".join(where)
    total = consultar(f"SELECT count(*) AS n FROM orden_compra WHERE {w}", args, una=True)["n"]
    filas = consultar(SQL_ORDEN + f"WHERE {w} ORDER BY id DESC LIMIT %s OFFSET %s", (*args, por, desde))
    return responder({"datos": armar_ordenes(filas), "paginacion": paginacion(pagina, por, total)},
                     raiz="ordenes", items={"datos": "orden", "lineas": "linea"})


@app.get(f"{P}/abastecimiento/ordenes/<int:oid>")
@requiere("abastecimiento.ver")
def orden_una(oid):
    return responder(armar_ordenes([_orden(oid)])[0], raiz="orden", items={"lineas": "linea"})


def aplicar_pendientes(oid):
    """Manda a inventario las entradas que faltan. Devuelve (aplicadas, pendientes, aviso)."""
    pendientes = consultar("SELECT r.id, r.producto_id, r.cantidad, r.operacion_uuid, r.nota, o.microhub_id, o.folio, o.id AS orden_id "
                           "FROM orden_compra_recepcion r JOIN orden_compra o ON o.id = r.orden_id "
                           "WHERE r.orden_id = %s AND NOT r.aplicada ORDER BY r.id", (oid,))
    aplicadas, aviso = 0, None
    for r in pendientes:
        try:
            exigir("inventario", "POST", "inventario/movimientos", ok=(200, 201), cuerpo={
                "microhub_id": r["microhub_id"], "producto_id": r["producto_id"], "tipo": "recepcion", "cantidad": r["cantidad"],
                "motivo": f"Recepción de la orden {r['folio']}" + (f": {r['nota']}" if r["nota"] else ""),
                "referencia": {"tipo": "orden_compra", "id": str(r["orden_id"])}, "operacion_uuid": r["operacion_uuid"]})
        except ErrorApi as e:
            aviso = f"Inventario no registró la entrada: {e.mensaje}"
            break
        with conexion() as con, con.cursor() as cur:
            cur.execute("UPDATE orden_compra_recepcion SET aplicada = true, aplicada_en = now() WHERE id = %s AND NOT aplicada "
                        "RETURNING cantidad", (r["id"],))
            if cur.fetchone():                              # solo una vez aunque dos reintentos coincidan
                cur.execute("UPDATE orden_compra_linea SET cantidad_recibida = cantidad_recibida + %s WHERE orden_id = %s AND producto_id = %s",
                            (r["cantidad"], oid, r["producto_id"]))
                aplicadas += 1
    with conexion() as con, con.cursor() as cur:
        cur.execute("SELECT cantidad, cantidad_recibida FROM orden_compra_linea WHERE orden_id = %s", (oid,))
        nuevo = estado_orden([(f["cantidad"], f["cantidad_recibida"]) for f in cur.fetchall()])
        cur.execute("UPDATE orden_compra SET estado = %s, cerrada_en = CASE WHEN %s = 'recibida' THEN now() ELSE NULL END "
                    "WHERE id = %s AND estado IN ('emitida', 'parcial', 'recibida')", (nuevo, nuevo, oid))
        cur.execute("SELECT count(*) AS n FROM orden_compra_recepcion WHERE orden_id = %s AND NOT aplicada", (oid,))
        faltan = cur.fetchone()["n"]
    return aplicadas, faltan, aviso


@app.post(f"{P}/abastecimiento/ordenes/<int:oid>/recepcion")
@requiere("abastecimiento.recibir")
def recibir(oid):
    d = validar(leer_cuerpo("recepcion_nueva"), [Campo("operacion_uuid", req=False, nulo=True, min_len=8, max_len=60),
                                                 Campo("nota", req=False, nulo=True, max_len=300), Campo("lineas", "lista", req=False, nulo=True)])
    campos = [Campo("producto_id", "int", minimo=1), Campo("cantidad", "int", minimo=1, maximo=100000)]
    lineas = [validar(l if isinstance(l, dict) else {}, campos, prefijo=f"lineas[{i}].") for i, l in enumerate(d.get("lineas") or [])]
    if len({l["producto_id"] for l in lineas}) != len(lineas):
        raise invalido("lineas", "Un producto no puede aparecer dos veces en la misma recepción.")
    _orden(oid)                                             # sin líneas es un reintento de las entradas pendientes
    lote = d.get("operacion_uuid") or str(uuidlib.uuid4())
    with conexion() as con, con.cursor() as cur:
        cur.execute("SELECT estado FROM orden_compra WHERE id = %s FOR UPDATE", (oid,))
        estado = cur.fetchone()["estado"]
        if lineas and estado not in ("emitida", "parcial"):
            raise conflicto(f"La orden está {estado}; ya no recibe mercancía.")
        for i, l in enumerate(lineas):
            clave = f"{lote}:{l['producto_id']}"
            cur.execute("SELECT 1 FROM orden_compra_recepcion WHERE operacion_uuid = %s", (clave,))
            if cur.fetchone():
                continue                                    # mismo envío repetido: no se guarda otra vez
            cur.execute("SELECT l.cantidad, l.cantidad_recibida, COALESCE((SELECT sum(r.cantidad) FROM orden_compra_recepcion r "
                        "WHERE r.orden_id = l.orden_id AND r.producto_id = l.producto_id AND NOT r.aplicada), 0)::integer AS pendiente "
                        "FROM orden_compra_linea l WHERE l.orden_id = %s AND l.producto_id = %s", (oid, l["producto_id"]))
            linea = cur.fetchone()
            if not linea:
                raise ErrorApi(422, "VALIDACION", "Revisa los datos enviados.",
                               [{"campo": f"lineas[{i}].producto_id", "mensaje": "Ese producto no está en la orden."}])
            falta = linea["cantidad"] - linea["cantidad_recibida"] - linea["pendiente"]
            if l["cantidad"] > falta:
                raise ErrorApi(422, "VALIDACION", "Revisa los datos enviados.",
                               [{"campo": f"lineas[{i}].cantidad", "mensaje": f"Solo faltan {max(falta, 0)} por recibir de ese producto."}])
            cur.execute("INSERT INTO orden_compra_recepcion (orden_id, producto_id, cantidad, operacion_uuid, nota, recibido_por) "
                        "VALUES (%s,%s,%s,%s,%s,%s)", (oid, l["producto_id"], l["cantidad"], clave, d.get("nota"), g.usuario["id"]))
    aplicadas, faltan, aviso = aplicar_pendientes(oid)
    cuerpo = {"orden": armar_ordenes([_orden(oid)])[0], "aplicadas": aplicadas, "pendientes": faltan, "aviso": aviso}
    return responder(cuerpo, 202 if faltan else 201, raiz="recepcion", items={"lineas": "linea"})


@app.post(f"{P}/abastecimiento/ordenes/<int:oid>/cancelar")
@requiere("abastecimiento.aprobar")
def cancelar(oid):
    d = validar(leer_cuerpo("cancelacion_nueva"), [Campo("motivo", min_len=3, max_len=300)])
    _orden(oid)
    with conexion() as con, con.cursor() as cur:
        cur.execute("SELECT estado FROM orden_compra WHERE id = %s FOR UPDATE", (oid,))
        estado = cur.fetchone()["estado"]
        cur.execute("SELECT count(*) AS n FROM orden_compra_recepcion WHERE orden_id = %s", (oid,))
        if estado != "emitida" or cur.fetchone()["n"]:
            raise conflicto("Solo se cancela una orden emitida que todavía no recibió mercancía.")
        cur.execute("UPDATE orden_compra SET estado = 'cancelada', motivo_cancelacion = %s, cerrada_en = now() WHERE id = %s",
                    (d["motivo"], oid))
    return responder(armar_ordenes([_orden(oid)])[0], raiz="orden", items={"lineas": "linea"})


# --------------------------------------------------------------------
# Seguimiento
# --------------------------------------------------------------------
@app.get(f"{P}/abastecimiento/seguimiento")
@requiere("abastecimiento.ver")
def seguimiento():
    hub = limitar_microhub(filtro_entero("microhub_id"))
    cond, args = ("WHERE microhub_id = %s", [hub]) if hub else ("", [])
    sol = {f["estado"]: f["n"] for f in consultar(f"SELECT estado, count(*)::integer AS n FROM solicitud_compra {cond} GROUP BY estado", args)}
    ord_ = {f["estado"]: f["n"] for f in consultar(f"SELECT estado, count(*)::integer AS n FROM orden_compra {cond} GROUP BY estado", args)}
    abiertas = ("estado IN ('emitida', 'parcial')" + (" AND microhub_id = %s" if hub else ""))
    atrasadas = consultar(f"SELECT count(*)::integer AS n, min(fecha_esperada) AS proxima FROM orden_compra WHERE {abiertas} AND fecha_esperada < %s",
                          [*args, hoy()], una=True)
    proxima = consultar(f"SELECT min(fecha_esperada) AS d FROM orden_compra WHERE {abiertas} AND fecha_esperada >= %s", [*args, hoy()], una=True)
    pend = consultar("SELECT count(*)::integer AS n FROM orden_compra_recepcion r JOIN orden_compra o ON o.id = r.orden_id "
                     "WHERE NOT r.aplicada" + (" AND o.microhub_id = %s" if hub else ""), args, una=True)
    return responder({"microhub_id": hub, "solicitudes": {e: sol.get(e, 0) for e in ESTADOS_SOLICITUD},
                      "ordenes": {e: ord_.get(e, 0) for e in ESTADOS_ORDEN}, "atrasadas": atrasadas["n"],
                      "pendientes_inventario": pend["n"],
                      "proxima_entrega": proxima["d"].isoformat() if proxima["d"] else None}, raiz="seguimiento_abastecimiento")


# --------------------------------------------------------------------
# Documentación
# --------------------------------------------------------------------
PAG = [("pagina", "query", "integer", "Página (1…)"), ("por_pagina", "query", "integer", "1 a 100")]
HUB = ("microhub_id", "query", "integer", "Microhub. Operador y supervisor solo ven el suyo")
documentar(app, "GET", f"{P}/abastecimiento/necesidades", "Necesidades de reposición", permisos=["abastecimiento.ver"],
           parametros=PAG + [("microhub_id", "query", "integer", "Microhub (obligatorio salvo para operador y supervisor)")],
           descripcion="Pide las alertas al servicio de inventario y la mejor oferta al de proveedores. Sugiere llegar a "
                       "`reposicion_factor_objetivo` × mínimo, sin contar lo que ya viene en camino ni lo ya solicitado.",
           respuestas={200: ("Página de necesidades", "NecesidadLista.ok")}, errores=[400, 403, 503])
documentar(app, "GET", f"{P}/abastecimiento/solicitudes", "Solicitudes de compra", permisos=["abastecimiento.ver"],
           parametros=PAG + [HUB, ("estado", "query", "string", "pendiente | aprobada | rechazada | ordenada")],
           respuestas={200: ("Página de solicitudes", "SolicitudCompraLista.ok")}, errores=[400, 403])
documentar(app, "POST", f"{P}/abastecimiento/solicitudes", "Pedir mercancía", permisos=["abastecimiento.solicitar"], cuerpo="SolicitudCompraNueva.ok",
           descripcion="Un producto no se repite en la solicitud. Avisa a los administradores.",
           respuestas={201: ("Solicitud creada, pendiente", "SolicitudCompra.ok")}, errores=[400, 403, 422])
documentar(app, "GET", f"{P}/abastecimiento/solicitudes/{{id}}", "Una solicitud", permisos=["abastecimiento.ver"],
           parametros=[("id", "path", "integer", "Id de la solicitud")],
           respuestas={200: ("Solicitud con sus líneas", "SolicitudCompra.ok")}, errores=[403, 404])
documentar(app, "POST", f"{P}/abastecimiento/solicitudes/{{id}}/decision", "Aprobar o rechazar", permisos=["abastecimiento.aprobar"],
           parametros=[("id", "path", "integer", "Id de la solicitud")], cuerpo="DecisionCompra.ok",
           descripcion="Solo una solicitud pendiente. Rechazar exige motivo. Avisa a quien la pidió.",
           respuestas={200: ("Solicitud decidida", "SolicitudCompra.ok")}, errores=[400, 403, 404, 409, 422])
documentar(app, "POST", f"{P}/abastecimiento/solicitudes/{{id}}/ordenar", "Emitir las órdenes de compra", permisos=["abastecimiento.aprobar"],
           parametros=[("id", "path", "integer", "Id de la solicitud")], cuerpo="OrdenarNuevo.ok",
           descripcion="Solo una solicitud aprobada. Cada línea va al proveedor más barato que alcance la cantidad y la compra mínima; "
                       "las líneas del mismo proveedor forman una orden, que debe alcanzar su pedido mínimo. Con proveedor_id se "
                       "concentra todo en ese proveedor.",
           respuestas={201: ("Órdenes generadas", "OrdenesGeneradas.ok")}, errores=[400, 403, 404, 409, 422, 503])
documentar(app, "GET", f"{P}/abastecimiento/ordenes", "Órdenes de compra", permisos=["abastecimiento.ver"],
           parametros=PAG + [HUB, ("proveedor_id", "query", "integer", "Proveedor"), ("solicitud_id", "query", "integer", "Solicitud de origen"),
                             ("estado", "query", "string", "emitida | parcial | recibida | cancelada"),
                             ("atrasadas", "query", "string", "true: abiertas con fecha esperada vencida")],
           respuestas={200: ("Página de órdenes", "OrdenCompraLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/abastecimiento/ordenes/{{id}}", "Una orden", permisos=["abastecimiento.ver"],
           parametros=[("id", "path", "integer", "Id de la orden")],
           respuestas={200: ("Orden con lo recibido de cada línea", "OrdenCompra.ok")}, errores=[403, 404])
documentar(app, "POST", f"{P}/abastecimiento/ordenes/{{id}}/recepcion", "Recibir mercancía", permisos=["abastecimiento.recibir"],
           parametros=[("id", "path", "integer", "Id de la orden")], cuerpo="RecepcionNueva.ok",
           descripcion="Guarda la recepción y manda la entrada al servicio de inventario con una operacion_uuid por línea. Responde 201 si "
                       "todas las entradas quedaron aplicadas y 202 si alguna sigue pendiente porque inventario no respondió; se reintenta "
                       "con el mismo POST sin líneas. No se puede recibir más de lo pedido.",
           respuestas={201: ("Recepción aplicada", "RecepcionResultado.ok")}, errores=[400, 403, 404, 409, 422])
documentar(app, "POST", f"{P}/abastecimiento/ordenes/{{id}}/cancelar", "Cancelar una orden", permisos=["abastecimiento.aprobar"],
           parametros=[("id", "path", "integer", "Id de la orden")], cuerpo="CancelacionNueva.ok",
           descripcion="Solo una orden emitida que todavía no recibió mercancía.",
           respuestas={200: ("Orden cancelada", "OrdenCompra.ok")}, errores=[400, 403, 404, 409, 422])
documentar(app, "GET", f"{P}/abastecimiento/seguimiento", "Tablero de abastecimiento", permisos=["abastecimiento.ver"], parametros=[HUB],
           descripcion="Cuántas solicitudes y órdenes hay en cada estado, las atrasadas, las entradas pendientes de aplicar en inventario y la "
                       "próxima entrega esperada.",
           respuestas={200: ("Conteos", "SeguimientoAbastecimiento.ok")}, errores=[403])
