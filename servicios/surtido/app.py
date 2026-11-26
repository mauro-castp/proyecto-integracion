"""
Servicio de surtido · puerto 5122 · contrato v1

  GET /api/v1/surtido/abc                      clasificación ABC de los productos (por unidades vendidas)
  GET /api/v1/surtido/analisis                 clase, rotación, margen, quiebres y recomendación por producto
  GET /api/v1/surtido/recomendaciones          recomendaciones guardadas
  POST /api/v1/surtido/recomendaciones         calcula y guarda la recomendación de un microhub (surtido.editar)
  GET /api/v1/surtido/recomendaciones/{id}     una recomendación guardada, con sus líneas
  GET /api/v1/surtido/restricciones/{microhub_id}   espacio y presupuesto de un microhub
  PUT /api/v1/surtido/restricciones/{microhub_id}   cambia espacio y presupuesto (surtido.editar)
  GET /api/v1/surtido/supuestos                de dónde sale cada valor y cómo se calibra

Responsabilidad única: qué productos tener y cuántos. Las ventas las pide a pedidos (GET /pedidos/ventas), las existencias y los
quiebres a inventario, los nombres y la categoría a productos y el costo a precios (lista de precios general). No lee sus tablas.

Cómo se decide cada producto (mismas funciones del portal, planeacion_calc):
  1. ABC por unidades vendidas en la ventana: A hasta `abc_a_pct` % acumulado, B hasta `abc_b_pct` %, C el resto.
  2. Demanda diaria = unidades ÷ días de la ventana. Cobertura = existencia ÷ demanda diaria. Rotación = unidades ÷ existencia.
  3. Aumentar si hubo quiebres, la existencia está en el mínimo o la cobertura de un A o B es menos de la mitad del objetivo
     (`cobertura_dias_a/b/c`). Reducir si la cobertura pasa de `cobertura_dias_exceso` días. Eliminar si no se movió o si es C con
     margen no positivo. Mantener en los demás casos.
  4. Lo que se sugiere aumentar se limita al espacio y al presupuesto del microhub, empezando por la clase A y el mejor margen por
     espacio. Si no cabe nada, la recomendación pasa a «Excluir».
"""
import math

from flask import g

from comun import config, supuestos as sup
from comun.base import (crear_app, documentar, filtro_entero, filtro_opcion, leer_cuerpo, leer_paginacion, lista, limitar_microhub, paginacion,
                        requiere, responder)
from comun.base_errores import ErrorApi, filtro_invalido, invalido, no_encontrado
from comun.calculo import pc
from comun.clientes import exigir, mapa
from comun.datos import como_json, conexion, consultar
from comun.formatos import ZONA, fecha
from comun.validar import Campo, validar

import datetime as dt

app = crear_app("surtido", "Microhubs · Surtido",
                "Clasificación ABC, rotación, margen y quiebres por producto, recomendaciones de surtido y restricciones de espacio y presupuesto.", 5122)
P = config.PREFIJO
DEFECTOS = {"abc_a_pct": 80.0, "abc_b_pct": 95.0, "cobertura_dias_a": 7.0, "cobertura_dias_b": 5.0, "cobertura_dias_c": 3.0,
            "cobertura_dias_exceso": 30.0, "ventana_analisis_dias": 90.0, "margen_bruto_default": 0.28}
CLAVES_SUPUESTOS = list(DEFECTOS)
ACCIONES = ["Aumentar", "Mantener", "Reducir", "Eliminar", "Excluir"]
ORDEN_CLASE = {"A": 0, "B": 1, "C": 2}
ITEMS = {"filas": "fila", "lineas": "linea", "clases": "clase", "supuestos_usados": "supuesto", "datos": "supuesto"}


# --------------------------------------------------------------------
# Cálculo (funciones puras, sin bases de datos)
# --------------------------------------------------------------------
def construir_filas(productos, existencias, ventas, quiebres, costos, espacios, margen_defecto):
    """Un renglón por producto activo con todo lo que hace falta para clasificar y recomendar.

    productos {id: catálogo} · existencias {id: {existencia, minimo}} · ventas {id: {unidades, venta}} · quiebres {id: n}
    costos {id: costo} · espacios {id: unidades de anaquel por unidad}
    """
    filas = []
    for pid, pr in productos.items():
        if pr.get("estatus") != "activo":
            continue
        precio = float(pr["precio"])
        costo = costos.get(pid)
        estimado = costo is None
        if estimado:
            costo = round(precio * (1 - margen_defecto), 2)
        inv, v = existencias.get(pid, {}), ventas.get(pid, {})
        filas.append({"id": pid, "clave_interna": pr.get("clave_interna"), "nombre": pr.get("nombre"), "categoria": (pr.get("categoria") or {}).get("nombre"),
                      "precio": precio, "costo": float(costo), "costo_estimado": estimado, "espacio": float(espacios.get(pid, 1.0)),
                      "unidades": int(v.get("unidades", 0)), "ventas": float(v.get("venta", 0)),
                      "existencia": int(inv.get("existencia", 0)), "minimo": int(inv.get("minimo", 0)), "quiebres": int(quiebres.get(pid, 0))})
    return filas


def aplicar_restricciones(lineas, espacio_total, presupuesto):
    """Limita lo que se sugiere aumentar al espacio y al presupuesto libres. Modifica las líneas y devuelve el resumen.

    Orden de prioridad: clase A antes que B y C; dentro de la clase, el mayor margen por unidad de espacio.
    """
    ocupado = sum(l["existencia"] * l["espacio"] for l in lineas)
    libre = None if espacio_total is None else espacio_total - ocupado
    por_gastar = presupuesto
    candidatos = [l for l in lineas if l["recomendacion"] == "Aumentar" and l["sugerido"] > 0]
    candidatos.sort(key=lambda l: (ORDEN_CLASE[l["clase"]], -(l["margen_unit"] / l["espacio"]), l["id"]))
    for l in candidatos:
        unidades, limite = l["sugerido"], None
        if libre is not None:
            cabe = max(int(math.floor(libre / l["espacio"])), 0)
            if cabe < unidades:
                unidades, limite = cabe, "espacio"
        if por_gastar is not None and l["costo"] > 0:
            alcanza = max(int(math.floor(por_gastar / l["costo"])), 0)
            if alcanza < unidades:
                unidades, limite = alcanza, "presupuesto"
        if libre is not None:
            libre -= unidades * l["espacio"]
        if por_gastar is not None:
            por_gastar -= unidades * l["costo"]
        l["sugerido"], l["limitado_por"] = unidades, limite
        if unidades == 0:
            l["recomendacion"] = "Excluir"
            l["motivo"] = "no cabe en el espacio o el presupuesto del microhub"
    necesario = sum(l["sugerido"] * l["espacio"] for l in lineas)
    requerido = sum(l["sugerido"] * l["costo"] for l in lineas)
    return {"espacio": {"total": None if espacio_total is None else round(espacio_total, 1), "ocupado": round(ocupado, 1), "sugerido": round(necesario, 1),
                        "ocupacion_pct": None if not espacio_total else round(100 * (ocupado + necesario) / espacio_total, 1)},
            "presupuesto": {"total": None if presupuesto is None else round(presupuesto, 2), "requerido": round(requerido, 2),
                            "uso_pct": None if not presupuesto else round(100 * requerido / presupuesto, 1)}}


def analizar(filas, dias, p, espacio_total=None, presupuesto=None):
    """Clasifica, recomienda y aplica las restricciones. Devuelve (líneas ordenadas, resumen)."""
    params = {k: p[k] for k in ("abc_a_pct", "abc_b_pct", "cobertura_dias_a", "cobertura_dias_b", "cobertura_dias_c", "cobertura_dias_exceso")}
    clases = {x["id"]: x for x in pc.clasificar_abc([{"id": f["id"], "unidades": f["unidades"]} for f in filas], params)}
    lineas = []
    for f in filas:
        cl = clases[f["id"]]
        margen = f["precio"] - f["costo"]
        r = pc.recomendar_surtido({**f, "clase": cl["clase"], "margen_unit": margen}, dias, params)
        lineas.append({**f, "clase": cl["clase"], "pct_acum": cl["pct_acum"], "margen_unit": round(margen, 2), "margen_total": round(margen * f["unidades"], 2),
                       "demanda_dia": r["demanda_dia"], "cobertura_dias": r["cobertura_dias"], "rotacion": r["rotacion"], "recomendacion": r["recomendacion"],
                       "motivo": r["motivo"], "sugerido": r["sugerido"], "limitado_por": None})
    limites = aplicar_restricciones(lineas, espacio_total, presupuesto)
    lineas.sort(key=lambda l: (ORDEN_CLASE[l["clase"]], -l["unidades"], l["id"]))
    por_accion = {a: sum(1 for l in lineas if l["recomendacion"] == a) for a in ACCIONES}
    por_clase = {c: sum(1 for l in lineas if l["clase"] == c) for c in "ABC"}
    resumen = {"productos": len(lineas), "aumentar": por_accion["Aumentar"], "mantener": por_accion["Mantener"], "reducir": por_accion["Reducir"],
               "eliminar": por_accion["Eliminar"], "excluir": por_accion["Excluir"], "clase_a": por_clase["A"], "clase_b": por_clase["B"],
               "clase_c": por_clase["C"], "unidades_a_comprar": sum(l["sugerido"] for l in lineas),
               "con_costo_estimado": sum(1 for l in lineas if l["costo_estimado"]), **limites}
    return lineas, resumen


def resumen_abc(lineas):
    """Por clase: cuántos productos, qué parte de las unidades y de la venta representan."""
    total_u = sum(l["unidades"] for l in lineas) or 1
    total_v = sum(l["ventas"] for l in lineas) or 1
    salida = []
    for c in "ABC":
        g_ = [l for l in lineas if l["clase"] == c]
        salida.append({"clase": c, "productos": len(g_), "unidades": sum(l["unidades"] for l in g_), "venta": round(sum(l["ventas"] for l in g_), 2),
                       "pct_unidades": round(100 * sum(l["unidades"] for l in g_) / total_u, 1),
                       "pct_venta": round(100 * sum(l["ventas"] for l in g_) / total_v, 1)})
    return salida


# --------------------------------------------------------------------
# Datos de otros servicios
# --------------------------------------------------------------------
def parametros():
    return sup.valores(DEFECTOS)


def hoy():
    return dt.datetime.now(ZONA).date()


def traer_todo(servicio, ruta, params=None):
    datos, pagina = [], 1
    while pagina <= 20:
        r = exigir(servicio, "GET", ruta, params={**(params or {}), "por_pagina": 100, "pagina": pagina})
        datos += r["datos"]
        if pagina >= r["paginacion"]["paginas"]:
            break
        pagina += 1
    return datos


def microhub(mid):
    hubs = mapa("microhubs", "microhubs")
    if mid not in hubs:
        raise no_encontrado("No existe ese microhub.")
    return {"id": mid, "nombre": hubs[mid]["nombre"]}


def costos_de_lista():
    """{producto_id: costo} de la lista de precios general vigente. Vacío si no hay."""
    listas = traer_todo("precios", "precios/listas", {"vigente": "true", "estatus": "activo"})
    general = next((l for l in listas if l["zona_id"] is None), None)
    if not general:
        return {}
    detalle = exigir("precios", "GET", f"precios/listas/{general['id']}")
    return {i["producto"]["id"]: float(i["costo"]) for i in detalle["items"] if i.get("costo") is not None}


def datos_del_hub(mid, dias, p):
    """Junta lo que cada servicio sabe de los productos. Si falta uno, se responde 503 (no se inventa)."""
    productos = mapa("productos", "productos")
    if not productos:
        raise ErrorApi(503, "SERVICIO_NO_DISPONIBLE", "El servicio de productos no responde; sin el catálogo no se puede analizar el surtido.")
    filtro = {"microhub_id": mid} if mid else {}
    existencias = {}
    for e in traer_todo("inventario", "inventario", filtro):
        a = existencias.setdefault(e["producto"]["id"], {"existencia": 0, "minimo": 0})
        a["existencia"] += e["existencia"]; a["minimo"] += e["minimo"]
    fin = hoy()
    ventas = {v["producto_id"]: {"unidades": v["unidades"], "venta": v["venta"]}
              for v in traer_todo("pedidos", "pedidos/ventas", {**filtro, "desde": (fin - dt.timedelta(days=dias - 1)).isoformat(), "hasta": fin.isoformat()})}
    quiebres = {}
    for q in traer_todo("inventario", "inventario/quiebres", {**filtro, "dias": dias}):
        quiebres[q["producto_id"]] = quiebres.get(q["producto_id"], 0) + q["quiebres"] + (1 if q["agotado_hoy"] else 0)
    try:
        costos = costos_de_lista()
    except ErrorApi:
        costos = {}                                        # sin precios se estima con el margen por omisión y se avisa en cada línea
    espacios = {f["producto_id"]: float(f["espacio_unidades"]) for f in consultar("SELECT producto_id, espacio_unidades FROM surtido_producto_param")}
    return construir_filas(productos, existencias, ventas, quiebres, costos, espacios, p["margen_bruto_default"])


def restriccion(mid):
    f = consultar("SELECT microhub_id, espacio_total, presupuesto, actualizado_en FROM surtido_restriccion WHERE microhub_id = %s", (mid,), una=True)
    return f


def usados(p):
    return sup.usados({k: p[k] for k in ("abc_a_pct", "abc_b_pct", "cobertura_dias_a", "cobertura_dias_b", "cobertura_dias_c", "cobertura_dias_exceso",
                                          "ventana_analisis_dias")})


def fila_salida(l):
    return {"producto": {"id": l["id"], "clave_interna": l["clave_interna"], "nombre": l["nombre"]}, "categoria": l["categoria"], "clase": l["clase"],
            "pct_acum": l["pct_acum"], "unidades": l["unidades"], "venta": round(l["ventas"], 2), "margen_unitario": l["margen_unit"],
            "margen_total": l["margen_total"], "costo_estimado": l["costo_estimado"], "existencia": l["existencia"], "minimo": l["minimo"],
            "quiebres": l["quiebres"], "demanda_dia": l["demanda_dia"], "cobertura_dias": l["cobertura_dias"], "rotacion": l["rotacion"],
            "recomendacion": l["recomendacion"], "motivo": l["motivo"], "sugerido": l["sugerido"], "limitado_por": l["limitado_por"]}


def calcular(mid):
    """Todo el análisis de un microhub (o de la red si mid es None)."""
    p = parametros()
    dias = max(int(p["ventana_analisis_dias"]), 1)
    filas = datos_del_hub(mid, dias, p)
    r = restriccion(mid) if mid else None
    espacio = float(r["espacio_total"]) if r else None
    presupuesto = float(r["presupuesto"]) if r and r["presupuesto"] is not None else None
    lineas, resumen = analizar(filas, dias, p, espacio, presupuesto)
    return p, dias, lineas, resumen


def hub_pedido(obligatorio=False):
    mid = limitar_microhub(filtro_entero("microhub_id"))
    if obligatorio and not mid:
        raise filtro_invalido("microhub_id", "microhub_id es obligatorio.")
    return mid


# --------------------------------------------------------------------
# Consultas
# --------------------------------------------------------------------
@app.get(f"{P}/surtido/abc")
@requiere("surtido.ver")
def abc():
    mid = hub_pedido()
    p, dias, lineas, _ = calcular(mid)
    return responder({"microhub": microhub(mid) if mid else None, "ventana_dias": dias, "clases": resumen_abc(lineas),
                      "filas": [{"producto": {"id": l["id"], "clave_interna": l["clave_interna"], "nombre": l["nombre"]}, "clase": l["clase"], "unidades": l["unidades"],
                                 "venta": round(l["ventas"], 2), "pct_acum": l["pct_acum"]} for l in lineas],
                      "supuestos_usados": usados(p)}, raiz="surtido_abc", items=ITEMS)


@app.get(f"{P}/surtido/analisis")
@requiere("surtido.ver")
def analisis():
    mid = hub_pedido()
    clase = filtro_opcion("clase", ["A", "B", "C"])
    accion = filtro_opcion("recomendacion", ACCIONES)
    p, dias, lineas, resumen = calcular(mid)
    filas = [fila_salida(l) for l in lineas if (not clase or l["clase"] == clase) and (not accion or l["recomendacion"] == accion)]
    return responder({"microhub": microhub(mid) if mid else None, "ventana_dias": dias, "resumen": resumen, "filas": filas, "supuestos_usados": usados(p)},
                     raiz="surtido_analisis", items=ITEMS)


# --------------------------------------------------------------------
# Recomendaciones guardadas
# --------------------------------------------------------------------
def recomendacion_completa(rid):
    f = consultar("SELECT id, microhub_id, parametros, resumen, creado_por, creado_en FROM surtido_recomendacion WHERE id = %s", (rid,), una=True)
    if not f:
        raise no_encontrado("No existe esa recomendación.")
    limitar_microhub(f["microhub_id"])
    lineas = consultar("SELECT producto_id, clase, accion, unidades, existencia, sugerido, margen_unitario, rotacion, motivo FROM surtido_recomendacion_linea "
                       "WHERE recomendacion_id = %s ORDER BY clase, unidades DESC, producto_id", (rid,))
    prod = mapa("productos", "productos")
    return {"id": f["id"], "microhub": microhub(f["microhub_id"]), "ventana_dias": f["parametros"]["ventana_dias"], "nota": f["parametros"].get("nota"),
            "resumen": f["resumen"], "creado_por": f["creado_por"], "creado_en": fecha(f["creado_en"]),
            "lineas": [{"producto": {"id": l["producto_id"], "clave_interna": (prod.get(l["producto_id"]) or {}).get("clave_interna"),
                                     "nombre": (prod.get(l["producto_id"]) or {}).get("nombre")},
                        "clase": l["clase"], "recomendacion": l["accion"], "unidades": l["unidades"], "existencia": l["existencia"], "sugerido": l["sugerido"],
                        "margen_unitario": None if l["margen_unitario"] is None else float(l["margen_unitario"]),
                        "rotacion": None if l["rotacion"] is None else float(l["rotacion"]), "motivo": l["motivo"]} for l in lineas],
            "supuestos_usados": f["parametros"]["supuestos_usados"]}


@app.post(f"{P}/surtido/recomendaciones")
@requiere("surtido.editar")
def guardar():
    d = validar(leer_cuerpo("surtido_recomendacion_nueva"), [Campo("microhub_id", "int", minimo=1), Campo("nota", req=False, nulo=True, max_len=300)])
    mid = limitar_microhub(d["microhub_id"])
    microhub(mid)
    p, dias, lineas, resumen = calcular(mid)
    snapshot = {"microhub_id": mid, "ventana_dias": dias, "nota": d.get("nota"), "supuestos_usados": usados(p)}
    with conexion() as con, con.cursor() as cur:
        cur.execute("INSERT INTO surtido_recomendacion (microhub_id, parametros, resumen, creado_por) VALUES (%s,%s,%s,%s) RETURNING id",
                    (mid, como_json(snapshot), como_json(resumen), g.usuario["id"]))
        rid = cur.fetchone()["id"]
        for l in lineas:
            cur.execute("INSERT INTO surtido_recomendacion_linea (recomendacion_id, producto_id, clase, accion, unidades, existencia, sugerido, margen_unitario, "
                        "rotacion, motivo) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (rid, l["id"], l["clase"], l["recomendacion"], l["unidades"], l["existencia"], l["sugerido"], l["margen_unit"], l["rotacion"],
                         (l["motivo"] or "")[:200]))
    return responder(recomendacion_completa(rid), 201, raiz="surtido_recomendacion", items=ITEMS)


@app.get(f"{P}/surtido/recomendaciones")
@requiere("surtido.ver")
def recomendaciones():
    pagina, por, desde = leer_paginacion()
    mid = hub_pedido()
    where, args = ["TRUE"], []
    if mid:
        where.append("microhub_id = %s"); args.append(mid)
    w = " AND ".join(where)
    total = consultar(f"SELECT count(*) AS n FROM surtido_recomendacion WHERE {w}", args, una=True)["n"]
    filas = consultar(f"SELECT id, microhub_id, parametros, resumen, creado_por, creado_en FROM surtido_recomendacion WHERE {w} "
                      f"ORDER BY id DESC LIMIT %s OFFSET %s", (*args, por, desde))
    hubs = mapa("microhubs", "microhubs")
    return lista(filas, paginacion(pagina, por, total), "recomendacion", "surtido_recomendaciones",
                 lambda f: {"id": f["id"], "microhub": {"id": f["microhub_id"], "nombre": (hubs.get(f["microhub_id"]) or {}).get("nombre")},
                            "ventana_dias": f["parametros"]["ventana_dias"], "nota": f["parametros"].get("nota"), "resumen": f["resumen"],
                            "creado_por": f["creado_por"], "creado_en": fecha(f["creado_en"])}, items=ITEMS)


@app.get(f"{P}/surtido/recomendaciones/<int:rid>")
@requiere("surtido.ver")
def recomendacion_una(rid):
    return responder(recomendacion_completa(rid), raiz="surtido_recomendacion", items=ITEMS)


# --------------------------------------------------------------------
# Restricciones
# --------------------------------------------------------------------
def restriccion_salida(mid, f):
    hub = microhub(mid)
    ocupado = None
    return {"microhub": hub, "espacio_total": float(f["espacio_total"]), "presupuesto": None if f["presupuesto"] is None else float(f["presupuesto"]),
            "actualizado_en": fecha(f["actualizado_en"])}


@app.get(f"{P}/surtido/restricciones/<int:mid>")
@requiere("surtido.ver")
def restriccion_una(mid):
    limitar_microhub(mid)
    f = restriccion(mid)
    if not f:
        raise no_encontrado("Ese microhub no tiene restricciones de surtido.")
    return responder(restriccion_salida(mid, f), raiz="surtido_restriccion")


@app.route(f"{P}/surtido/restricciones/<int:mid>", methods=["PUT", "PATCH"])
@requiere("surtido.editar")
def cambiar_restriccion(mid):
    d = validar(leer_cuerpo("surtido_restriccion_cambio"), [
        Campo("espacio_total", "num", minimo=1, maximo=1000000, decimales=1), Campo("presupuesto", "num", req=False, nulo=True, minimo=1, maximo=100000000, decimales=2)])
    limitar_microhub(mid)
    microhub(mid)
    with conexion() as con, con.cursor() as cur:
        cur.execute("INSERT INTO surtido_restriccion (microhub_id, espacio_total, presupuesto, actualizado_por, actualizado_en) VALUES (%s,%s,%s,%s,now()) "
                    "ON CONFLICT (microhub_id) DO UPDATE SET espacio_total = EXCLUDED.espacio_total, presupuesto = EXCLUDED.presupuesto, "
                    "actualizado_por = EXCLUDED.actualizado_por, actualizado_en = now()",
                    (mid, d["espacio_total"], d.get("presupuesto"), g.usuario["id"]))
    return responder(restriccion_salida(mid, restriccion(mid)), raiz="surtido_restriccion")


@app.get(f"{P}/surtido/supuestos")
@requiere("surtido.ver")
def supuestos_surtido():
    return responder({"datos": sup.listar(CLAVES_SUPUESTOS)}, raiz="supuestos_surtido", items={"datos": "supuesto"})


# --------------------------------------------------------------------
# Documentación
# --------------------------------------------------------------------
PAG = [("pagina", "query", "integer", "Página (1…)"), ("por_pagina", "query", "integer", "1 a 100")]
HUB = ("microhub_id", "query", "integer", "Microhub. Operador y supervisor solo ven el suyo; sin microhub se analiza toda la red, sin restricciones")
documentar(app, "GET", f"{P}/surtido/abc", "Clasificación ABC", permisos=["surtido.ver"], parametros=[HUB],
           descripcion="Por unidades vendidas en la ventana de análisis (`ventana_analisis_dias`): A hasta `abc_a_pct` % acumulado, B hasta `abc_b_pct` %, C el resto.",
           respuestas={200: ("Resumen por clase y detalle por producto", "SurtidoAbc.ok")}, errores=[400, 403, 503])
documentar(app, "GET", f"{P}/surtido/analisis", "Análisis y recomendación de surtido", permisos=["surtido.ver"],
           parametros=[HUB, ("clase", "query", "string", "A | B | C"), ("recomendacion", "query", "string", "Aumentar | Mantener | Reducir | Eliminar | Excluir")],
           descripcion="Clase, rotación, cobertura, margen, quiebres y recomendación de cada producto. Con microhub, lo que se sugiere aumentar se limita al espacio y al "
                       "presupuesto de ese microhub; el costo sale de la lista de precios general y, si falta, se estima con `margen_bruto_default` (costo_estimado = true).",
           respuestas={200: ("Resumen y un renglón por producto", "SurtidoAnalisis.ok")}, errores=[400, 403, 503])
documentar(app, "GET", f"{P}/surtido/recomendaciones", "Recomendaciones guardadas", permisos=["surtido.ver"], parametros=PAG + [HUB],
           respuestas={200: ("Página de recomendaciones", "SurtidoRecomendacionLista.ok")}, errores=[400, 403])
documentar(app, "POST", f"{P}/surtido/recomendaciones", "Guardar la recomendación de un microhub", permisos=["surtido.editar"], cuerpo="SurtidoRecomendacionNueva.ok",
           descripcion="Calcula el análisis en este momento y lo guarda tal cual, con los supuestos usados, para poder compararlo después.",
           respuestas={201: ("Recomendación guardada", "SurtidoRecomendacion.ok")}, errores=[400, 403, 404, 422, 503])
documentar(app, "GET", f"{P}/surtido/recomendaciones/{{id}}", "Una recomendación guardada", permisos=["surtido.ver"], parametros=[("id", "path", "integer", "Id")],
           respuestas={200: ("Recomendación con sus líneas", "SurtidoRecomendacion.ok")}, errores=[403, 404])
documentar(app, "GET", f"{P}/surtido/restricciones/{{microhub_id}}", "Restricciones de un microhub", permisos=["surtido.ver"],
           parametros=[("microhub_id", "path", "integer", "Id del microhub")],
           respuestas={200: ("Espacio y presupuesto", "SurtidoRestriccion.ok")}, errores=[403, 404])
documentar(app, "PUT", f"{P}/surtido/restricciones/{{microhub_id}}", "Cambiar las restricciones", permisos=["surtido.editar"], cuerpo="SurtidoRestriccionCambio.ok",
           parametros=[("microhub_id", "path", "integer", "Id del microhub")],
           respuestas={200: ("Restricciones guardadas", "SurtidoRestriccion.ok")}, errores=[400, 403, 404, 422])
documentar(app, "GET", f"{P}/surtido/supuestos", "Supuestos del modelo de surtido", permisos=["surtido.ver"],
           descripcion="Valor, origen (medido, supuesto o normativo), justificación y cómo calibrarlo con datos reales.",
           respuestas={200: ("Supuestos documentados", "SupuestosSurtido.ok")}, errores=[403])
