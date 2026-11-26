"""
Servicio de costos · puerto 5119 · contrato v1

  GET    /api/v1/costos/conceptos               renglones de costo (ambito, tipo, categoria, vigente)
  POST   /api/v1/costos/conceptos               alta de un concepto (costos.editar)
  PUT    /api/v1/costos/conceptos/{id}          cambio de un concepto (también PATCH)
  DELETE /api/v1/costos/conceptos/{id}          baja lógica
  GET    /api/v1/costos/resumen                 costos fijos y variables de un microhub o candidato
  GET    /api/v1/costos/unitarios               costo por pedido y por entrega a un volumen dado
  GET    /api/v1/costos/rentabilidad            margen de contribución, utilidad y margen operativo
  GET    /api/v1/costos/sensibilidad            qué pasa con el costo y la utilidad si cada palanca sube o baja
  GET    /api/v1/costos/supuestos               de dónde sale cada valor y cómo se calibra

Responsabilidad única: cuánto cuesta operar. No decide si conviene abrir (eso es punto-equilibrio) ni cuánto se vende
(demanda): recibe el volumen y el ticket como entrada o usa los de referencia de la configuración.

Cómo se arma el costo de un microhub o candidato:
  · Los conceptos globales (pago al repartidor, combustible, empaque, comisión) aplican a todos.
  · Los del microhub o candidato se suman; si tienen el mismo nombre que uno global, lo sustituyen.
  · Un candidato sin conceptos propios toma renta, nómina, servicios y otros costos de la ubicación candidata
    (servicio de planeación).
  · Costo de entrega = pago por entrega + 2 × distancia × costo por km ÷ paradas por viaje (ida y vuelta compartidos).
  · Costo por pedido = costos fijos ÷ pedidos del mes + variable por pedido + comisión × ticket + costo de entrega.
"""
import datetime as dt

from flask import g, request

from comun import config, supuestos as sup
from comun.base import (crear_app, documentar, filtro_entero, filtro_opcion, leer_cuerpo, leer_paginacion, lista, paginacion,
                        requiere, responder)
from comun.base_errores import ErrorApi, conflicto, filtro_invalido, invalido, no_encontrado
from comun.clientes import llamar, mapa
from comun.datos import conexion, consultar
from comun.formatos import ZONA, dinero, numero
from comun.validar import Campo, validar

app = crear_app("costos", "Microhubs · Costos",
                "Conceptos de costo fijos y variables, costo por pedido y por entrega, y rentabilidad de un microhub o una ubicación candidata.", 5119)
P = config.PREFIJO
DEFECTOS = {"cos_pedidos_mes_ref": 1800.0, "cos_ticket_ref": 135.0, "paradas_por_viaje": 3.0, "margen_bruto_default": 0.28,
            "dias_operacion_mes": 30.0, "cap_distancia_entrega_km": 2.4}
CLAVES_SUPUESTOS = ["cos_pedidos_mes_ref", "cos_ticket_ref", "paradas_por_viaje", "margen_bruto_default", "dias_operacion_mes", "cap_distancia_entrega_km"]
CATEGORIAS = ["renta", "personal", "servicios", "almacenamiento", "transporte", "operacion", "otros"]
UNIDADES_VARIABLES = ["pedido", "entrega", "km", "pct_venta"]
PALANCAS_VARIACION = (-0.2, -0.1, 0.1, 0.2)


# --------------------------------------------------------------------
# Cálculo (funciones puras, sin bases de datos)
# --------------------------------------------------------------------
def conceptos_que_rigen(conceptos, ambito, ambito_id, dia):
    """Globales + los del objeto, vigentes y activos; el del objeto sustituye al global del mismo nombre."""
    vigentes = [c for c in conceptos if c["estatus"] == "activo" and c["vigente_desde"] <= dia
                and (c["vigente_hasta"] is None or c["vigente_hasta"] >= dia)]
    elegidos = {c["nombre"]: c for c in vigentes if c["ambito"] == "global"}
    if ambito != "global":
        elegidos.update({c["nombre"]: c for c in vigentes if c["ambito"] == ambito and c["ambito_id"] == ambito_id})
    return sorted(elegidos.values(), key=lambda c: (c["tipo"], c["categoria"], c["nombre"]))


def resumir(conceptos):
    """Totales por tipo, categoría y unidad. Cada concepto: tipo, categoria, nombre, unidad, monto (número)."""
    fijos = sum(c["monto"] for c in conceptos if c["tipo"] == "fijo")
    por_categoria = {}
    for c in conceptos:
        if c["tipo"] == "fijo":
            por_categoria[c["categoria"]] = por_categoria.get(c["categoria"], 0.0) + c["monto"]
    por_unidad = {u: sum(c["monto"] for c in conceptos if c["tipo"] == "variable" and c["unidad"] == u) for u in UNIDADES_VARIABLES}
    return {"fijos_mes": round(fijos, 2), "por_categoria": [{"categoria": k, "monto": round(v, 2)} for k, v in sorted(por_categoria.items())],
            "variable_pedido": round(por_unidad["pedido"], 4), "variable_entrega": round(por_unidad["entrega"], 4),
            "variable_km": round(por_unidad["km"], 4), "comision_pct": round(por_unidad["pct_venta"], 4)}


def costo_entrega(resumen, distancia_km, paradas_por_viaje):
    """Pago por entrega + ida y vuelta por el costo del kilómetro, repartido entre las paradas del viaje."""
    return resumen["variable_entrega"] + 2 * distancia_km * resumen["variable_km"] / max(paradas_por_viaje, 1)


def unitarios(resumen, pedidos_mes, ticket, distancia_km, paradas_por_viaje):
    entrega = costo_entrega(resumen, distancia_km, paradas_por_viaje)
    comision = ticket * resumen["comision_pct"] / 100
    variable = resumen["variable_pedido"] + comision + entrega
    fijo_pedido = resumen["fijos_mes"] / pedidos_mes if pedidos_mes else None
    return {"costo_fijo_pedido": fijo_pedido, "variable_pedido": resumen["variable_pedido"], "comision_pedido": comision,
            "costo_entrega": entrega, "costo_variable_pedido": variable,
            "costo_por_pedido": None if fijo_pedido is None else fijo_pedido + variable}


def rentabilidad(resumen, pedidos_mes, ticket, margen_bruto, distancia_km, paradas_por_viaje):
    u = unitarios(resumen, pedidos_mes, ticket, distancia_km, paradas_por_viaje)
    contribucion = ticket * margen_bruto - u["costo_variable_pedido"]
    ingresos = ticket * pedidos_mes
    utilidad = contribucion * pedidos_mes - resumen["fijos_mes"]
    return {**u, "ingresos_mes": ingresos, "margen_bruto_mes": ingresos * margen_bruto,
            "costo_variable_mes": u["costo_variable_pedido"] * pedidos_mes, "margen_contribucion_pedido": contribucion,
            "margen_contribucion_mes": contribucion * pedidos_mes, "costos_fijos_mes": resumen["fijos_mes"], "utilidad_mes": utilidad,
            "margen_operativo_pct": 100 * utilidad / ingresos if ingresos else None, "cubre_costos": utilidad >= 0}


def sensibilidad_costos(resumen, pedidos_mes, ticket, margen_bruto, distancia_km, paradas_por_viaje, variaciones=PALANCAS_VARIACION):
    """Cada palanca (categoría fija, costo de entrega, variable por pedido) se mueve sola y se recalcula todo."""
    base = rentabilidad(resumen, pedidos_mes, ticket, margen_bruto, distancia_km, paradas_por_viaje)
    palancas = [(f"Fijo: {c['categoria']}", "fijo", c["categoria"]) for c in resumen["por_categoria"]]
    palancas += [("Pago y kilometraje de la entrega", "entrega", None), ("Costos variables por pedido", "pedido", None)]
    filas = []
    for etiqueta, clase, categoria in palancas:
        for v in variaciones:
            r = {**resumen, "por_categoria": [dict(c) for c in resumen["por_categoria"]]}
            if clase == "fijo":
                for c in r["por_categoria"]:
                    if c["categoria"] == categoria:
                        c["monto"] = c["monto"] * (1 + v)
                r["fijos_mes"] = sum(c["monto"] for c in r["por_categoria"])
            elif clase == "entrega":
                r["variable_entrega"] *= 1 + v
                r["variable_km"] *= 1 + v
            else:
                r["variable_pedido"] *= 1 + v
            n = rentabilidad(r, pedidos_mes, ticket, margen_bruto, distancia_km, paradas_por_viaje)
            filas.append({"palanca": etiqueta, "cambio_pct": round(v * 100), "costo_por_pedido": n["costo_por_pedido"],
                          "utilidad_mes": n["utilidad_mes"], "cambio_utilidad": n["utilidad_mes"] - base["utilidad_mes"]})
    return base, filas


# --------------------------------------------------------------------
# Datos
# --------------------------------------------------------------------
def hoy():
    return dt.datetime.now(ZONA).date()


SQL_CONCEPTO = ("SELECT id, ambito, ambito_id, nombre, categoria, tipo, unidad, monto, vigente_desde, vigente_hasta, estatus::text AS estatus, "
                "fuente, justificacion FROM costo_concepto ")


def concepto(f):
    return {"id": f["id"], "ambito": f["ambito"], "ambito_id": f["ambito_id"], "nombre": f["nombre"], "categoria": f["categoria"],
            "tipo": f["tipo"], "unidad": f["unidad"], "monto": dinero(f["monto"]), "vigente_desde": f["vigente_desde"].isoformat(),
            "vigente_hasta": f["vigente_hasta"].isoformat() if f["vigente_hasta"] else None, "estatus": f["estatus"], "fuente": f["fuente"],
            "justificacion": f["justificacion"]}


def objeto():
    """(ambito, id) pedido en la consulta: microhub_id, candidato_id o ninguno (solo conceptos globales)."""
    mh, cand = filtro_entero("microhub_id"), filtro_entero("candidato_id")
    if mh and cand:
        raise filtro_invalido("candidato_id", "Indica microhub_id o candidato_id, no los dos.")
    if mh:
        if mh not in mapa("microhubs", "microhubs"):
            raise no_encontrado("No existe ese microhub.")
        return "microhub", mh
    if cand:
        return "candidato", cand
    return "global", None


def candidato_de_planeacion(cid):
    status, d = llamar("planeacion", "GET", f"candidatos/{cid}")
    if status == 404:
        raise no_encontrado("No existe esa ubicación candidata.")
    if status in (401, 403):
        raise ErrorApi(403, "PROHIBIDO", "Tu perfil no puede consultar ubicaciones candidatas en planeación.")
    if status != 200 or not isinstance(d, dict):
        raise ErrorApi(503, "SERVICIO_NO_DISPONIBLE", "El servicio de planeación no pudo atender la solicitud.")
    return d


def conceptos_de(ambito, ambito_id):
    """Conceptos que rigen hoy para el objeto. Un candidato sin conceptos propios toma los de su ubicación candidata."""
    filas = consultar(SQL_CONCEPTO + "WHERE ambito = 'global' OR (ambito = %s AND ambito_id = %s)", (ambito, ambito_id))
    todos = [{**f, "monto": float(f["monto"])} for f in filas]
    rigen = conceptos_que_rigen(todos, ambito, ambito_id, hoy())
    origen = "costos"
    if ambito == "candidato" and not any(c["ambito"] == "candidato" for c in rigen):
        c = candidato_de_planeacion(ambito_id)
        propios = [("Renta del local", "renta", c.get("renta_estimada")), ("Nómina estimada", "personal", c.get("nomina_estimada")),
                   ("Servicios estimados", "servicios", c.get("servicios_estimados")), ("Otros costos estimados", "otros", c.get("otros_costos"))]
        rigen += [{"id": None, "ambito": "candidato", "ambito_id": ambito_id, "nombre": n, "categoria": cat, "tipo": "fijo", "unidad": "mes",
                   "monto": float(m or 0)} for n, cat, m in propios]
        origen = "planeacion"
    return rigen, origen


def parametros_calculo():
    """Pedidos al mes, ticket, margen, distancia y paradas: de la petición o de la configuración."""
    cfg = sup.valores(DEFECTOS)
    def num(nombre, defecto, minimo=0.0, maximo=1e9):
        crudo = (request.args.get(nombre) or "").strip()
        if not crudo:
            return defecto, False
        try:
            v = float(crudo)
        except ValueError:
            raise filtro_invalido(nombre, f"{nombre} debe ser un número.")
        if not minimo <= v <= maximo:
            raise filtro_invalido(nombre, f"{nombre} debe estar entre {minimo:g} y {maximo:g}.")
        return v, True
    pedidos, m1 = num("pedidos_mes", cfg["cos_pedidos_mes_ref"], 1, 1_000_000)
    ticket, m2 = num("ticket", cfg["cos_ticket_ref"], 1, 100_000)
    margen, m3 = num("margen_bruto", cfg["margen_bruto_default"], 0, 1)
    dist, m4 = num("distancia_km", cfg["cap_distancia_entrega_km"], 0, 100)
    paradas, m5 = num("paradas_por_viaje", cfg["paradas_por_viaje"], 1, 50)
    usados = {"pedidos_mes": pedidos, "ticket": ticket, "margen_bruto": margen, "distancia_km": dist, "paradas_por_viaje": paradas}
    modificados = [k for k, m in zip(usados, (m1, m2, m3, m4, m5)) if m]
    return usados, modificados


def entrada(ambito, ambito_id, origen, usados, modificados):
    return {"ambito": ambito, "ambito_id": ambito_id, "origen": origen, "pedidos_mes": usados["pedidos_mes"], "ticket": dinero(usados["ticket"]),
            "margen_bruto": usados["margen_bruto"], "distancia_km": usados["distancia_km"], "paradas_por_viaje": usados["paradas_por_viaje"],
            "valores_modificados": modificados}


def r2(x):
    return None if x is None else round(x, 2)


# --------------------------------------------------------------------
# Conceptos
# --------------------------------------------------------------------
@app.get(f"{P}/costos/conceptos")
@requiere("costos.ver")
def conceptos():
    pagina, por, desde = leer_paginacion()
    ambito = filtro_opcion("ambito", ["global", "microhub", "candidato"])
    tipo, cat = filtro_opcion("tipo", ["fijo", "variable"]), filtro_opcion("categoria", CATEGORIAS)
    est, vig = filtro_opcion("estatus", ["activo", "inactivo"]), filtro_opcion("vigente", ["true", "false"])
    aid = filtro_entero("ambito_id")
    objeto_ambito, objeto_id = objeto()
    where, args = ["TRUE"], []
    if objeto_ambito != "global":                    # microhub_id o candidato_id: lo que rige para ese objeto (globales y propios)
        where.append("(ambito = 'global' OR (ambito = %s AND ambito_id = %s))"); args += [objeto_ambito, objeto_id]
    for cond, valor in (("ambito = %s", ambito), ("ambito_id = %s", aid), ("tipo = %s", tipo), ("categoria = %s", cat), ("estatus = %s", est)):
        if valor:
            where.append(cond); args.append(valor)
    if vig:
        cond = "estatus = 'activo' AND vigente_desde <= %s AND (vigente_hasta IS NULL OR vigente_hasta >= %s)"
        where.append(cond if vig == "true" else f"NOT ({cond})"); args += [hoy(), hoy()]
    w = " AND ".join(where)
    total = consultar(f"SELECT count(*) AS n FROM costo_concepto WHERE {w}", args, una=True)["n"]
    filas = consultar(SQL_CONCEPTO + f"WHERE {w} ORDER BY ambito, ambito_id NULLS FIRST, tipo, nombre LIMIT %s OFFSET %s", (*args, por, desde))
    return lista(filas, paginacion(pagina, por, total), "concepto", "conceptos_costo", concepto)


def _validar_concepto(d, parcial=False):
    if d.get("tipo") and d.get("unidad"):
        if (d["tipo"] == "fijo") != (d["unidad"] == "mes"):
            raise invalido("unidad", "Un costo fijo se da por mes; uno variable, por pedido, entrega, km o porcentaje de la venta.")
    if d.get("unidad") == "pct_venta" and d.get("monto") is not None and d["monto"] > 100:
        raise invalido("monto", "Un porcentaje de la venta no puede pasar de 100.")


def _fechas(d):
    for k in ("vigente_desde", "vigente_hasta"):
        if d.get(k):
            try:
                d[k] = dt.date.fromisoformat(d[k])
            except ValueError:
                raise invalido(k, "Debe ser una fecha AAAA-MM-DD válida.")
    if d.get("vigente_desde") and d.get("vigente_hasta") and d["vigente_hasta"] < d["vigente_desde"]:
        raise invalido("vigente_hasta", "No puede ser anterior a vigente_desde.")


CAMPOS_CONCEPTO = [
    Campo("ambito", opciones=["global", "microhub", "candidato"]), Campo("ambito_id", "int", req=False, nulo=True, minimo=1),
    Campo("nombre", min_len=3, max_len=120), Campo("categoria", opciones=CATEGORIAS), Campo("tipo", opciones=["fijo", "variable"]),
    Campo("unidad", opciones=["mes", *UNIDADES_VARIABLES]), Campo("monto", "num", minimo=0, decimales=2),
    Campo("vigente_desde", req=False, nulo=True, patron=r"\d{4}-\d{2}-\d{2}", mensaje="Usa el formato AAAA-MM-DD."),
    Campo("vigente_hasta", req=False, nulo=True, patron=r"\d{4}-\d{2}-\d{2}", mensaje="Usa el formato AAAA-MM-DD."),
    Campo("fuente", req=False, opciones=["medido", "supuesto", "contrato"]), Campo("justificacion", min_len=10, max_len=300)]


def _existe_objeto(ambito, ambito_id):
    if ambito == "global":
        if ambito_id is not None:
            raise invalido("ambito_id", "Un concepto global no lleva ambito_id.")
        return
    if ambito_id is None:
        raise invalido("ambito_id", f"Un concepto de {ambito} necesita su ambito_id.")
    if ambito == "microhub" and ambito_id not in mapa("microhubs", "microhubs"):
        raise invalido("ambito_id", "No existe ese microhub.")
    if ambito == "candidato":
        candidato_de_planeacion(ambito_id)


@app.post(f"{P}/costos/conceptos")
@requiere("costos.editar")
def alta():
    d = validar(leer_cuerpo("concepto_costo_nuevo"), CAMPOS_CONCEPTO)
    _validar_concepto(d)
    _fechas(d)
    _existe_objeto(d["ambito"], d.get("ambito_id"))
    with conexion() as con, con.cursor() as cur:
        cur.execute("INSERT INTO costo_concepto (ambito, ambito_id, nombre, categoria, tipo, unidad, monto, vigente_desde, vigente_hasta, fuente, "
                    "justificacion, creado_por) VALUES (%s,%s,%s,%s,%s,%s,%s,COALESCE(%s, fn_hoy()),%s,%s,%s,%s) RETURNING id",
                    (d["ambito"], d.get("ambito_id"), d["nombre"], d["categoria"], d["tipo"], d["unidad"], d["monto"], d.get("vigente_desde"),
                     d.get("vigente_hasta"), d.get("fuente", "supuesto"), d["justificacion"], g.usuario["id"]))
        cid = cur.fetchone()["id"]
    return responder(concepto(consultar(SQL_CONCEPTO + "WHERE id = %s", (cid,), una=True)), 201, raiz="concepto_costo")


@app.route(f"{P}/costos/conceptos/<int:cid>", methods=["PUT", "PATCH"])
@requiere("costos.editar")
def cambiar(cid):
    campos = [Campo(c.nombre, c.tipo, req=False, minimo=c.minimo, maximo=c.maximo, min_len=c.min_len, max_len=c.max_len, opciones=c.opciones,
                    patron=c.patron, nulo=c.nulo, decimales=c.decimales, mensaje=c.mensaje)
              for c in CAMPOS_CONCEPTO if c.nombre not in ("ambito", "ambito_id")]
    d = validar(leer_cuerpo("concepto_costo_cambio"), campos)
    if not d:
        raise invalido("cuerpo", "Envía al menos un campo para modificar.")
    actual = consultar(SQL_CONCEPTO + "WHERE id = %s", (cid,), una=True)
    if not actual:
        raise no_encontrado("No existe ese concepto.")
    combinado = {"tipo": d.get("tipo", actual["tipo"]), "unidad": d.get("unidad", actual["unidad"]), "monto": d.get("monto", float(actual["monto"]))}
    _validar_concepto(combinado)
    _fechas(d)
    if d.get("vigente_hasta") and d["vigente_hasta"] < actual["vigente_desde"] and "vigente_desde" not in d:
        raise invalido("vigente_hasta", "No puede ser anterior a vigente_desde.")
    sets = [(k, d[k]) for k in ("nombre", "categoria", "tipo", "unidad", "monto", "vigente_desde", "vigente_hasta", "fuente", "justificacion") if k in d]
    with conexion() as con, con.cursor() as cur:
        cur.execute("UPDATE costo_concepto SET " + ", ".join(f"{k} = %s" for k, _ in sets) + " WHERE id = %s", [v for _, v in sets] + [cid])
    return responder(concepto(consultar(SQL_CONCEPTO + "WHERE id = %s", (cid,), una=True)), raiz="concepto_costo")


@app.delete(f"{P}/costos/conceptos/<int:cid>")
@requiere("costos.editar")
def baja(cid):
    with conexion() as con, con.cursor() as cur:
        cur.execute("UPDATE costo_concepto SET estatus = 'inactivo' WHERE id = %s", (cid,))
        if cur.rowcount == 0:
            raise no_encontrado("No existe ese concepto.")
    return responder(None, 204)


# --------------------------------------------------------------------
# Resumen, costos unitarios, rentabilidad y sensibilidad
# --------------------------------------------------------------------
@app.get(f"{P}/costos/resumen")
@requiere("costos.ver")
def resumen():
    ambito, aid = objeto()
    rigen, origen = conceptos_de(ambito, aid)
    r = resumir(rigen)
    variables = [{"nombre": c["nombre"], "unidad": c["unidad"], "monto": dinero(c["monto"])} for c in rigen if c["tipo"] == "variable"]
    return responder({"ambito": ambito, "ambito_id": aid, "origen": origen, "conceptos": len(rigen), "fijos_mes": dinero(r["fijos_mes"]),
                      "por_categoria": [{"categoria": c["categoria"], "monto": dinero(c["monto"])} for c in r["por_categoria"]],
                      "variables": variables, "variable_pedido": dinero(r["variable_pedido"]), "variable_entrega": dinero(r["variable_entrega"]),
                      "variable_km": dinero(r["variable_km"]), "comision_pct": r["comision_pct"]},
                     raiz="resumen_costos", items={"por_categoria": "categoria_costo", "variables": "variable"})


def _calculo():
    ambito, aid = objeto()
    rigen, origen = conceptos_de(ambito, aid)
    usados, modificados = parametros_calculo()
    return ambito, aid, origen, resumir(rigen), usados, modificados


def _supuestos_usados(resumen_c, usados, modificados):
    valores = {**{k: v for k, v in usados.items()}, "costo_base_entrega": resumen_c["variable_entrega"], "costo_km_reparto": resumen_c["variable_km"]}
    return sup.usados(valores, modificados)


@app.get(f"{P}/costos/unitarios")
@requiere("costos.ver")
def costos_unitarios():
    ambito, aid, origen, r, u, mod = _calculo()
    c = unitarios(r, u["pedidos_mes"], u["ticket"], u["distancia_km"], u["paradas_por_viaje"])
    return responder({"entrada": entrada(ambito, aid, origen, u, mod), "fijos_mes": dinero(r["fijos_mes"]), "costo_fijo_pedido": dinero(c["costo_fijo_pedido"]),
                      "variable_pedido": dinero(c["variable_pedido"]), "comision_pedido": dinero(c["comision_pedido"]),
                      "costo_entrega": dinero(c["costo_entrega"]), "costo_variable_pedido": dinero(c["costo_variable_pedido"]),
                      "costo_por_pedido": dinero(c["costo_por_pedido"]), "supuestos_usados": _supuestos_usados(r, u, mod)},
                     raiz="costos_unitarios", items={"valores_modificados": "clave", "supuestos_usados": "supuesto"})


@app.get(f"{P}/costos/rentabilidad")
@requiere("costos.ver")
def costos_rentabilidad():
    ambito, aid, origen, r, u, mod = _calculo()
    n = rentabilidad(r, u["pedidos_mes"], u["ticket"], u["margen_bruto"], u["distancia_km"], u["paradas_por_viaje"])
    return responder({"entrada": entrada(ambito, aid, origen, u, mod), "ingresos_mes": dinero(n["ingresos_mes"]),
                      "margen_bruto_mes": dinero(n["margen_bruto_mes"]), "costo_variable_mes": dinero(n["costo_variable_mes"]),
                      "margen_contribucion_pedido": dinero(n["margen_contribucion_pedido"]),
                      "margen_contribucion_mes": dinero(n["margen_contribucion_mes"]), "costos_fijos_mes": dinero(n["costos_fijos_mes"]),
                      "utilidad_mes": dinero(n["utilidad_mes"]), "margen_operativo_pct": r2(n["margen_operativo_pct"]),
                      "costo_por_pedido": dinero(n["costo_por_pedido"]), "cubre_costos": n["cubre_costos"],
                      "supuestos_usados": _supuestos_usados(r, u, mod)},
                     raiz="rentabilidad", items={"valores_modificados": "clave", "supuestos_usados": "supuesto"})


@app.get(f"{P}/costos/sensibilidad")
@requiere("costos.ver")
def costos_sensibilidad():
    ambito, aid, origen, r, u, mod = _calculo()
    base, filas = sensibilidad_costos(r, u["pedidos_mes"], u["ticket"], u["margen_bruto"], u["distancia_km"], u["paradas_por_viaje"])
    peor = max(filas, key=lambda f: abs(f["cambio_utilidad"]))
    return responder({"entrada": entrada(ambito, aid, origen, u, mod), "costo_por_pedido": dinero(base["costo_por_pedido"]),
                      "utilidad_mes": dinero(base["utilidad_mes"]), "palanca_mas_sensible": peor["palanca"],
                      "filas": [{"palanca": f["palanca"], "cambio_pct": f["cambio_pct"], "costo_por_pedido": dinero(f["costo_por_pedido"]),
                                 "utilidad_mes": dinero(f["utilidad_mes"]), "cambio_utilidad": dinero(f["cambio_utilidad"])} for f in filas],
                      "supuestos_usados": _supuestos_usados(r, u, mod)},
                     raiz="sensibilidad_costos", items={"valores_modificados": "clave", "supuestos_usados": "supuesto", "filas": "fila"})


@app.get(f"{P}/costos/supuestos")
@requiere("costos.ver")
def supuestos_costos():
    return responder({"datos": sup.listar(CLAVES_SUPUESTOS)}, raiz="supuestos_costos", items={"datos": "supuesto"})


# --------------------------------------------------------------------
# Documentación
# --------------------------------------------------------------------
PAG = [("pagina", "query", "integer", "Página (1…)"), ("por_pagina", "query", "integer", "1 a 100")]
OBJETO = [("microhub_id", "query", "integer", "Microhub"), ("candidato_id", "query", "integer", "Ubicación candidata (servicio de planeación)")]
CALCULO = OBJETO + [("pedidos_mes", "query", "number", "Pedidos al mes; por omisión `cos_pedidos_mes_ref`"),
                    ("ticket", "query", "number", "Ticket promedio; por omisión `cos_ticket_ref`"),
                    ("margen_bruto", "query", "number", "Margen bruto 0 a 1; por omisión `margen_bruto_default`"),
                    ("distancia_km", "query", "number", "Distancia de entrega, solo ida; por omisión `cap_distancia_entrega_km`"),
                    ("paradas_por_viaje", "query", "number", "Paradas por viaje; por omisión `paradas_por_viaje`")]
documentar(app, "GET", f"{P}/costos/conceptos", "Conceptos de costo", permisos=["costos.ver"],
           parametros=PAG + [("ambito", "query", "string", "global | microhub | candidato"), ("ambito_id", "query", "integer", "Id del microhub o candidato"),
                             ("tipo", "query", "string", "fijo | variable"), ("categoria", "query", "string", "renta | personal | servicios | …"),
                             ("estatus", "query", "string", "activo | inactivo"), ("vigente", "query", "string", "true | false: rige hoy o no"),
                             ("microhub_id", "query", "integer", "Solo los que aplican a ese microhub: los globales y los suyos"),
                             ("candidato_id", "query", "integer", "Solo los que aplican a esa ubicación candidata: los globales y los suyos")],
           respuestas={200: ("Página de conceptos", "ConceptoCostoLista.ok")}, errores=[400, 403, 404])
documentar(app, "POST", f"{P}/costos/conceptos", "Dar de alta un concepto de costo", permisos=["costos.editar"], cuerpo="ConceptoCostoNuevo.ok",
           descripcion="Fijo = monto por mes; variable = por pedido, entrega, km o porcentaje de la venta. Toda alta lleva su justificación.",
           respuestas={201: ("Concepto creado", "ConceptoCosto.ok")}, errores=[400, 403, 404, 422])
documentar(app, "PUT", f"{P}/costos/conceptos/{{id}}", "Cambiar un concepto", permisos=["costos.editar"], parametros=[("id", "path", "integer", "Id del concepto")],
           cuerpo="ConceptoCostoCambio.ok", descripcion="Cualquier subconjunto de campos. No cambia el ámbito.",
           respuestas={200: ("Concepto actualizado", "ConceptoCosto.ok")}, errores=[400, 403, 404, 422])
documentar(app, "DELETE", f"{P}/costos/conceptos/{{id}}", "Dar de baja un concepto", permisos=["costos.editar"],
           parametros=[("id", "path", "integer", "Id del concepto")], respuestas={204: ("Baja lógica, sin cuerpo", None)}, errores=[403, 404])
documentar(app, "GET", f"{P}/costos/resumen", "Resumen de costos", permisos=["costos.ver"], parametros=OBJETO,
           descripcion="Sin microhub_id ni candidato_id muestra solo los conceptos globales. Un candidato sin conceptos propios usa los de su ubicación en planeación.",
           respuestas={200: ("Costos fijos por categoría y variables", "ResumenCostos.ok")}, errores=[400, 403, 404, 503])
documentar(app, "GET", f"{P}/costos/unitarios", "Costo por pedido y por entrega", permisos=["costos.ver"], parametros=CALCULO,
           descripcion="Costo por pedido = fijos ÷ pedidos del mes + variable por pedido + comisión × ticket + costo de entrega.",
           respuestas={200: ("Costos unitarios y los supuestos usados", "CostosUnitarios.ok")}, errores=[400, 403, 404, 503])
documentar(app, "GET", f"{P}/costos/rentabilidad", "Rentabilidad", permisos=["costos.ver"], parametros=CALCULO,
           descripcion="Margen de contribución, utilidad del mes y margen operativo al volumen y ticket indicados.",
           respuestas={200: ("Rentabilidad", "Rentabilidad.ok")}, errores=[400, 403, 404, 503])
documentar(app, "GET", f"{P}/costos/sensibilidad", "Sensibilidad de los costos", permisos=["costos.ver"], parametros=CALCULO,
           descripcion="Cada palanca (categoría fija, pago y kilometraje de la entrega, variable por pedido) se mueve ±10 y ±20 % por separado.",
           respuestas={200: ("Efecto de cada palanca", "SensibilidadCostos.ok")}, errores=[400, 403, 404, 503])
documentar(app, "GET", f"{P}/costos/supuestos", "Supuestos del modelo de costos", permisos=["costos.ver"],
           descripcion="Valor, origen (medido, supuesto o normativo), justificación y cómo calibrarlo con datos reales.",
           respuestas={200: ("Supuestos documentados", "SupuestosCostos.ok")}, errores=[403])
