"""
Servicio de punto de equilibrio · puerto 5120 · contrato v1

  POST   /api/v1/punto-equilibrio/calculos            equilibrio paso a paso de un microhub, un candidato o números manuales
  GET    /api/v1/punto-equilibrio/microhubs           el equilibrio de cada microhub con sus datos reales
  POST   /api/v1/punto-equilibrio/sensibilidad        qué variable mueve más la utilidad (±10 y ±20 %, una por una)
  GET    /api/v1/punto-equilibrio/escenarios          escenarios guardados
  GET    /api/v1/punto-equilibrio/escenarios/{id}     un escenario con su cálculo completo
  DELETE /api/v1/punto-equilibrio/escenarios/{id}     borra un escenario (equilibrio.editar)
  GET    /api/v1/punto-equilibrio/comparacion         varios escenarios lado a lado
  GET    /api/v1/punto-equilibrio/supuestos           de dónde sale cada valor y cómo se calibra

Responsabilidad única: cuántos pedidos hacen falta para no perder dinero y si la demanda esperada los alcanza.
No guarda costos ni demanda: los pide a costos, demanda, cobertura y precios, y todo dato que el usuario escriba a mano
sustituye al que vendría de ahí (el cálculo dice de dónde salió cada número).

Cuenta (la misma de planeacion_calc.punto_equilibrio, que usa el portal):
  margen por pedido = ticket × margen bruto − costo variable por pedido (entrega, empaque y comisión)
  equilibrio mensual = costos fijos del mes ÷ margen por pedido        equilibrio diario = mensual ÷ días del mes
  margen de seguridad = demanda esperada ÷ equilibrio − 1
  VIABLE si el margen de seguridad llega al mínimo (`peq_margen_seguridad_pct`); VIABLE AJUSTADO si supera el equilibrio
  pero no llega; NO VIABLE si la demanda esperada no alcanza el equilibrio o el margen por pedido no es positivo.

Demanda esperada cuando no se indica: la demanda observada de las zonas que cubre el microhub (o la ubicación candidata),
repartida a partes iguales entre los microhubs que ya cubren cada zona más el nuevo.
"""
import datetime as dt

from flask import g, request

from comun import config, supuestos as sup
from comun.base import crear_app, documentar, leer_cuerpo, leer_paginacion, lista, paginacion, requiere, responder, tiene
from comun.base_errores import ErrorApi, filtro_invalido, invalido, no_encontrado
from comun.calculo import pc
from comun.clientes import exigir, mapa
from comun.datos import como_json, conexion, consultar
from comun.formatos import ZONA, fecha
from comun.validar import Campo, validar

app = crear_app("punto-equilibrio", "Microhubs · Punto de equilibrio",
                "Cálculo del punto de equilibrio paso a paso, sensibilidad y escenarios comparables.", 5120)
P = config.PREFIJO
RUTA = f"{P}/punto-equilibrio"
DEFECTOS = {"peq_margen_seguridad_pct": 15.0, "dias_operacion_mes": 30.0, "margen_bruto_default": 0.28, "cos_ticket_ref": 135.0}
CLAVES_SUPUESTOS = list(DEFECTOS)
VARIABLES = [("ticket", "Ticket promedio"), ("pedidos_dia", "Pedidos por día"), ("costos_fijos", "Costos fijos del mes"),
             ("costo_variable_pedido", "Costo variable por pedido"), ("margen_bruto", "Margen bruto")]
VARIACIONES = [-0.2, -0.1, 0.1, 0.2]
DECISIONES = {"viable": "VIABLE", "viable_ajustado": "VIABLE AJUSTADO", "no_viable": "NO VIABLE"}


# --------------------------------------------------------------------
# Cálculo (funciones puras, sin bases de datos)
# --------------------------------------------------------------------
def demanda_atribuible(zonas):
    """Pedidos por día que le tocan a un microhub: cada zona se reparte a partes iguales entre quienes la cubren.
    zonas: [{pedidos_dia, cubren}] donde `cubren` cuenta a todos los microhubs que la cubrirían, incluido este."""
    return sum(z["pedidos_dia"] / max(z["cubren"], 1) for z in zonas)


def calcular(costos_fijos, ticket, margen_bruto, costo_variable, pedidos_dia, dias_mes, seguridad_min_pct):
    eq = pc.punto_equilibrio(costos_fijos, ticket, margen_bruto, costo_variable, dias_mes)          # eq["pasos"]: el cálculo en palabras
    margen_pedido = ticket * margen_bruto - costo_variable                                         # las cuentas sin redondear
    mensual = costos_fijos / margen_pedido if margen_pedido > 0 else None
    diario = mensual / dias_mes if mensual is not None else None
    utilidad_dia = (ticket * margen_bruto - costo_variable) * pedidos_dia - costos_fijos / dias_mes
    explicacion = []
    if diario is None:
        decision = "no_viable"
        diferencia = seguridad = None
        explicacion.append("el margen por pedido no es positivo: el costo variable absorbe lo que deja el ticket")
    else:
        diferencia = pedidos_dia - diario
        seguridad = 100 * (pedidos_dia / diario - 1) if diario else None
        if pedidos_dia < diario:
            decision = "no_viable"
            explicacion.append(f"la demanda esperada ({pedidos_dia:.1f} pedidos/día) no alcanza el equilibrio ({diario:.1f} pedidos/día)")
        elif seguridad is not None and seguridad < seguridad_min_pct:
            decision = "viable_ajustado"
            explicacion.append(f"supera el equilibrio por {seguridad:.1f} %, menos del {seguridad_min_pct:g} % de margen de seguridad que pide el equipo")
        else:
            decision = "viable"
            explicacion.append(f"supera el equilibrio por {seguridad:.1f} % (mínimo {seguridad_min_pct:g} %)" if seguridad is not None else "supera el equilibrio")
    return {"margen_pedido": margen_pedido, "equilibrio_mensual": mensual, "equilibrio_diario": diario,
            "ingresos_equilibrio_mes": None if mensual is None else mensual * ticket, "diferencia_pedidos_dia": diferencia,
            "margen_seguridad_pct": seguridad, "utilidad_dia": utilidad_dia, "utilidad_mes": utilidad_dia * dias_mes, "decision": decision,
            "explicacion": explicacion, "pasos": eq["pasos"]}


def sensibilidad(entrada, dias_mes, seguridad_min_pct, variaciones=VARIACIONES):
    """Mueve una variable a la vez y recalcula. Devuelve las filas y el ranking por el rango de utilidad que recorre cada una."""
    base = calcular(entrada["costos_fijos"], entrada["ticket"], entrada["margen_bruto"], entrada["costo_variable_pedido"], entrada["pedidos_dia"],
                    dias_mes, seguridad_min_pct)
    filas, rangos = [], {}
    for clave, etiqueta in VARIABLES:
        utilidades = []
        for v in variaciones:
            e = dict(entrada)
            e[clave] = entrada[clave] * (1 + v)
            if clave == "margen_bruto":
                e[clave] = min(e[clave], 1.0)
            r = calcular(e["costos_fijos"], e["ticket"], e["margen_bruto"], e["costo_variable_pedido"], e["pedidos_dia"], dias_mes, seguridad_min_pct)
            utilidades.append(r["utilidad_mes"])
            filas.append({"variable": clave, "etiqueta": etiqueta, "cambio_pct": round(v * 100), "valor": e[clave], "equilibrio_diario": r["equilibrio_diario"],
                          "utilidad_mes": r["utilidad_mes"], "cambio_utilidad": r["utilidad_mes"] - base["utilidad_mes"], "decision": r["decision"]})
        rangos[clave] = (etiqueta, max(utilidades) - min(utilidades))
    ranking = sorted(({"variable": k, "etiqueta": e, "rango_utilidad_mes": r} for k, (e, r) in rangos.items()), key=lambda x: -x["rango_utilidad_mes"])
    return base, filas, ranking


# --------------------------------------------------------------------
# Datos de entrada (de otros servicios o de la petición)
# --------------------------------------------------------------------
def parametros():
    return sup.valores(DEFECTOS)


def objeto_de(d):
    mh, cand = d.get("microhub_id"), d.get("candidato_id")
    if mh and cand:
        raise invalido("candidato_id", "Indica microhub_id o candidato_id, no los dos.")
    if mh:
        hubs = mapa("microhubs", "microhubs")
        if mh not in hubs:
            raise no_encontrado("No existe ese microhub.")
        return "microhub", mh, hubs[mh]["nombre"]
    if cand:
        return "candidato", cand, None
    return "manual", None, None


def pedidos_dia_esperados(tipo, oid, zonas_demanda=None, cobertura=None, evaluacion=None):
    """Demanda esperada a partir de cobertura (qué zonas) y demanda (cuánto piden). Lista de zonas ya ponderadas."""
    pedidos = {x["zona"]["id"]: x["pedidos_dia"] for x in zonas_demanda}
    if tipo == "microhub":
        zonas = [{"pedidos_dia": pedidos.get(z["zona"]["id"], 0.0), "cubren": len(z["cubierta_por"])}
                 for z in cobertura if any(o["microhub"]["id"] == oid for o in z["cubierta_por"])]
    else:
        zonas = [{"pedidos_dia": pedidos.get(z["zona"]["id"], 0.0), "cubren": z["microhubs_que_ya_cubren"] + 1} for z in evaluacion["zonas"]]
    return demanda_atribuible(zonas), zonas


def traer_todo(servicio, ruta, params=None):
    datos, pagina = [], 1
    while pagina <= 10:
        r = exigir(servicio, "GET", ruta, params={**(params or {}), "por_pagina": 100, "pagina": pagina})
        datos += r["datos"]
        if pagina >= r["paginacion"]["paginas"]:
            break
        pagina += 1
    return datos


def resolver(d, p, compartido=None):
    """Arma la entrada del cálculo y dice de dónde salió cada número. `compartido` evita pedir lo mismo para cada microhub."""
    tipo, oid, nombre = objeto_de(d)
    compartido = compartido if compartido is not None else {}
    origen, e = {}, {}
    e["dias_mes"] = float(d["dias_mes"]) if d.get("dias_mes") else p["dias_operacion_mes"]

    def demanda():
        if "resumen_demanda" not in compartido:
            compartido["resumen_demanda"] = exigir("demanda", "GET", "demanda/resumen")
        return compartido["resumen_demanda"]

    if d.get("ticket") is not None:
        e["ticket"], origen["ticket"] = float(d["ticket"]), "manual"
    else:
        t = demanda()["total"]["ticket_promedio"]
        e["ticket"], origen["ticket"] = (float(t), "demanda") if t else (p["cos_ticket_ref"], "referencia")

    if d.get("margen_bruto") is not None:
        e["margen_bruto"], origen["margen_bruto"] = float(d["margen_bruto"]), "manual"
    elif d.get("margen_desde_precios"):
        filas = traer_todo("precios", "precios/margenes")
        if not filas:
            raise ErrorApi(422, "VALIDACION", "Precios no tiene renglones con costo para calcular el margen.")
        e["margen_bruto"], origen["margen_bruto"] = sum(f["margen_pct"] for f in filas) / len(filas) / 100, "precios"
    else:
        e["margen_bruto"], origen["margen_bruto"] = p["margen_bruto_default"], "configuracion"

    if d.get("costos_fijos") is not None and d.get("costo_variable_pedido") is not None:
        e["costos_fijos"], origen["costos_fijos"] = float(d["costos_fijos"]), "manual"
        e["costo_variable_pedido"], origen["costo_variable_pedido"] = float(d["costo_variable_pedido"]), "manual"
    else:
        if tipo == "manual":
            raise invalido("costos_fijos", "Sin microhub ni candidato hay que indicar costos_fijos y costo_variable_pedido.")
        u = exigir("costos", "GET", "costos/unitarios", params={f"{tipo}_id": oid, "ticket": e["ticket"]})
        e["costos_fijos"] = float(d["costos_fijos"]) if d.get("costos_fijos") is not None else float(u["fijos_mes"])
        origen["costos_fijos"] = "manual" if d.get("costos_fijos") is not None else "costos"
        e["costo_variable_pedido"] = float(d["costo_variable_pedido"]) if d.get("costo_variable_pedido") is not None else float(u["costo_variable_pedido"])
        origen["costo_variable_pedido"] = "manual" if d.get("costo_variable_pedido") is not None else "costos"

    if d.get("pedidos_dia") is not None:
        e["pedidos_dia"], origen["pedidos_dia"] = float(d["pedidos_dia"]), "manual"
    else:
        if tipo == "manual":
            raise invalido("pedidos_dia", "Sin microhub ni candidato hay que indicar pedidos_dia.")
        zonas_demanda = demanda()["zonas"]
        if tipo == "microhub":
            if "cobertura" not in compartido:
                compartido["cobertura"] = traer_todo("cobertura", "cobertura/zonas")
            e["pedidos_dia"], _ = pedidos_dia_esperados(tipo, oid, zonas_demanda, cobertura=compartido["cobertura"])
        else:
            ev = exigir("cobertura", "POST", "cobertura/evaluaciones", cuerpo={"candidato_id": oid}, ok=(200, 201))
            e["pedidos_dia"], _ = pedidos_dia_esperados(tipo, oid, zonas_demanda, evaluacion=ev)
        origen["pedidos_dia"] = "demanda_repartida"
    return tipo, oid, nombre, e, origen


def entrada_salida(e, origen, p):
    return {"costos_fijos_mes": e["costos_fijos"], "costo_variable_pedido": e["costo_variable_pedido"], "ticket": e["ticket"], "margen_bruto": e["margen_bruto"],
            "pedidos_dia": round(e["pedidos_dia"], 2), "dias_mes": e["dias_mes"], "margen_seguridad_minimo_pct": p["peq_margen_seguridad_pct"],
            "origen": {k: origen[k] for k in ("costos_fijos", "costo_variable_pedido", "ticket", "margen_bruto", "pedidos_dia")}}


def r2(x):
    return None if x is None else round(x, 2)


def calculo_salida(tipo, oid, nombre, e, origen, p, nombre_escenario=None, eid=None):
    r = calcular(e["costos_fijos"], e["ticket"], e["margen_bruto"], e["costo_variable_pedido"], e["pedidos_dia"], e["dias_mes"], p["peq_margen_seguridad_pct"])
    return {"id": eid, "nombre": nombre_escenario, "objeto": {"tipo": tipo, "id": oid, "nombre": nombre}, "entrada": entrada_salida(e, origen, p),
            "margen_pedido": r2(r["margen_pedido"]), "equilibrio_mensual": r2(r["equilibrio_mensual"]), "equilibrio_diario": r2(r["equilibrio_diario"]),
            "ingresos_equilibrio_mes": r2(r["ingresos_equilibrio_mes"]), "diferencia_pedidos_dia": r2(r["diferencia_pedidos_dia"]),
            "margen_seguridad_pct": r2(r["margen_seguridad_pct"]), "utilidad_dia": r2(r["utilidad_dia"]), "utilidad_mes": r2(r["utilidad_mes"]),
            "decision": r["decision"], "explicacion": r["explicacion"], "pasos": r["pasos"],
            "supuestos_usados": sup.usados({k: p[k] for k in ("peq_margen_seguridad_pct", "dias_operacion_mes", "margen_bruto_default")},
                                           [k for k, v in origen.items() if v == "manual"])}


ITEMS = {"explicacion": "motivo", "pasos": "paso", "supuestos_usados": "supuesto", "filas": "fila", "ranking": "variable"}
CAMPOS_ENTRADA = [
    Campo("nombre", req=False, nulo=True, min_len=3, max_len=120), Campo("microhub_id", "int", req=False, nulo=True, minimo=1),
    Campo("candidato_id", "int", req=False, nulo=True, minimo=1), Campo("pedidos_dia", "num", req=False, nulo=True, minimo=0, maximo=100000),
    Campo("ticket", "num", req=False, nulo=True, minimo=1, maximo=100000), Campo("margen_bruto", "num", req=False, nulo=True, minimo=0, maximo=1),
    Campo("costos_fijos", "num", req=False, nulo=True, minimo=0, maximo=100_000_000), Campo("costo_variable_pedido", "num", req=False, nulo=True, minimo=0, maximo=100000),
    Campo("dias_mes", "num", req=False, nulo=True, minimo=1, maximo=31), Campo("margen_desde_precios", "bool", req=False)]


# --------------------------------------------------------------------
# Cálculos y escenarios
# --------------------------------------------------------------------
@app.post(f"{RUTA}/calculos")
@requiere("equilibrio.ver")
def calculo():
    d = validar(leer_cuerpo("equilibrio_calculo_nuevo"), CAMPOS_ENTRADA + [Campo("guardar", "bool", req=False)])
    if d.get("guardar") and not tiene("equilibrio.editar"):
        raise ErrorApi(403, "PROHIBIDO", "Guardar un escenario exige el permiso equilibrio.editar.")
    p = parametros()
    tipo, oid, nombre, e, origen = resolver(d, p)
    eid = None
    nombre_esc = d.get("nombre") or (f"Equilibrio de {nombre}" if nombre else f"Equilibrio {dt.datetime.now(ZONA).date().isoformat()}")
    if d.get("guardar"):
        salida = calculo_salida(tipo, oid, nombre, e, origen, p, nombre_esc, None)
        with conexion() as con, con.cursor() as cur:
            cur.execute("INSERT INTO equilibrio_escenario (nombre, microhub_id, candidato_id, supuestos, resultados, creado_por) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
                        (nombre_esc, oid if tipo == "microhub" else None, oid if tipo == "candidato" else None, como_json(salida["entrada"]), como_json(salida), g.usuario["id"]))
            eid = cur.fetchone()["id"]
    return responder(calculo_salida(tipo, oid, nombre, e, origen, p, nombre_esc if eid else d.get("nombre"), eid), 201 if eid else 200,
                     raiz="equilibrio_calculo", items=ITEMS)


@app.get(f"{RUTA}/microhubs")
@requiere("equilibrio.ver")
def microhubs():
    p = parametros()
    compartido, filas = {}, []
    hubs = [h for h in sorted(mapa("microhubs", "microhubs").values(), key=lambda h: h["id"]) if h["estatus"] == "activo"]
    for h in hubs:
        tipo, oid, nombre, e, origen = resolver({"microhub_id": h["id"]}, p, compartido)
        r = calcular(e["costos_fijos"], e["ticket"], e["margen_bruto"], e["costo_variable_pedido"], e["pedidos_dia"], e["dias_mes"], p["peq_margen_seguridad_pct"])
        filas.append({"microhub": {"id": h["id"], "nombre": nombre}, "costos_fijos_mes": e["costos_fijos"], "margen_pedido": r2(r["margen_pedido"]),
                      "equilibrio_diario": r2(r["equilibrio_diario"]), "pedidos_dia": round(e["pedidos_dia"], 2), "diferencia_pedidos_dia": r2(r["diferencia_pedidos_dia"]),
                      "utilidad_mes": r2(r["utilidad_mes"]), "decision": r["decision"]})
    return responder({"datos": filas, "supuestos_usados": sup.usados({k: p[k] for k in ("peq_margen_seguridad_pct", "dias_operacion_mes")})},
                     raiz="equilibrio_microhubs", items={"datos": "microhub", "supuestos_usados": "supuesto"})


@app.post(f"{RUTA}/sensibilidad")
@requiere("equilibrio.ver")
def sensibilidad_ruta():
    d = validar(leer_cuerpo("equilibrio_sensibilidad_nueva"), CAMPOS_ENTRADA)
    p = parametros()
    tipo, oid, nombre, e, origen = resolver(d, p)
    base, filas, ranking = sensibilidad(e, e["dias_mes"], p["peq_margen_seguridad_pct"])
    return responder({"objeto": {"tipo": tipo, "id": oid, "nombre": nombre}, "entrada": entrada_salida(e, origen, p), "decision_base": base["decision"],
                      "utilidad_mes_base": r2(base["utilidad_mes"]), "equilibrio_diario_base": r2(base["equilibrio_diario"]),
                      "variable_mas_sensible": ranking[0]["etiqueta"],
                      "ranking": [{"variable": x["variable"], "etiqueta": x["etiqueta"], "rango_utilidad_mes": r2(x["rango_utilidad_mes"])} for x in ranking],
                      "filas": [{**f, "valor": round(f["valor"], 4), "equilibrio_diario": r2(f["equilibrio_diario"]), "utilidad_mes": r2(f["utilidad_mes"]),
                                 "cambio_utilidad": r2(f["cambio_utilidad"])} for f in filas],
                      "supuestos_usados": sup.usados({k: p[k] for k in ("peq_margen_seguridad_pct", "dias_operacion_mes")})},
                     raiz="equilibrio_sensibilidad", items=ITEMS)


@app.get(f"{RUTA}/escenarios")
@requiere("equilibrio.ver")
def escenarios():
    pagina, por, desde = leer_paginacion()
    total = consultar("SELECT count(*) AS n FROM equilibrio_escenario", una=True)["n"]
    filas = consultar("SELECT id, nombre, microhub_id, candidato_id, resultados, creado_por, creado_en FROM equilibrio_escenario ORDER BY id DESC LIMIT %s OFFSET %s", (por, desde))
    return lista(filas, paginacion(pagina, por, total), "escenario", "equilibrio_escenarios",
                 lambda f: {"id": f["id"], "nombre": f["nombre"], "microhub_id": f["microhub_id"], "candidato_id": f["candidato_id"],
                            "decision": f["resultados"]["decision"], "equilibrio_diario": f["resultados"]["equilibrio_diario"],
                            "pedidos_dia": f["resultados"]["entrada"]["pedidos_dia"], "utilidad_mes": f["resultados"]["utilidad_mes"],
                            "creado_por": f["creado_por"], "creado_en": fecha(f["creado_en"])})


def _escenario(eid):
    f = consultar("SELECT id, resultados FROM equilibrio_escenario WHERE id = %s", (eid,), una=True)
    if not f:
        raise no_encontrado("No existe ese escenario.")
    return {**f["resultados"], "id": f["id"]}


@app.get(f"{RUTA}/escenarios/<int:eid>")
@requiere("equilibrio.ver")
def escenario_uno(eid):
    return responder(_escenario(eid), raiz="equilibrio_calculo", items=ITEMS)


@app.delete(f"{RUTA}/escenarios/<int:eid>")
@requiere("equilibrio.editar")
def escenario_borrar(eid):
    with conexion() as con, con.cursor() as cur:
        cur.execute("DELETE FROM equilibrio_escenario WHERE id = %s", (eid,))
        if cur.rowcount == 0:
            raise no_encontrado("No existe ese escenario.")
    return responder(None, 204)


@app.get(f"{RUTA}/comparacion")
@requiere("equilibrio.ver")
def comparacion():
    crudo = (request.args.get("ids") or "").strip()
    try:
        ids = [int(x) for x in crudo.split(",") if x.strip()]
    except ValueError:
        raise filtro_invalido("ids", "ids es una lista de enteros separados por coma.")
    if not 2 <= len(ids) <= 8 or len(set(ids)) != len(ids):
        raise filtro_invalido("ids", "Indica entre 2 y 8 escenarios distintos.")
    esc = [_escenario(i) for i in ids]
    filas = [{"id": e["id"], "nombre": e["nombre"], "decision": e["decision"], "pedidos_dia": e["entrada"]["pedidos_dia"], "equilibrio_diario": e["equilibrio_diario"],
              "diferencia_pedidos_dia": e["diferencia_pedidos_dia"], "margen_seguridad_pct": e["margen_seguridad_pct"], "utilidad_mes": e["utilidad_mes"]} for e in esc]
    mejor = max(filas, key=lambda f: f["utilidad_mes"] if f["utilidad_mes"] is not None else float("-inf"))
    return responder({"filas": filas, "mejor_utilidad_id": mejor["id"], "mejor_utilidad_nombre": mejor["nombre"]}, raiz="equilibrio_comparacion", items={"filas": "escenario"})


@app.get(f"{RUTA}/supuestos")
@requiere("equilibrio.ver")
def supuestos_equilibrio():
    return responder({"datos": sup.listar(CLAVES_SUPUESTOS)}, raiz="supuestos_equilibrio", items={"datos": "supuesto"})


# --------------------------------------------------------------------
# Documentación
# --------------------------------------------------------------------
PAG = [("pagina", "query", "integer", "Página (1…)"), ("por_pagina", "query", "integer", "1 a 100")]
documentar(app, "POST", f"{RUTA}/calculos", "Calcular el punto de equilibrio", permisos=["equilibrio.ver"], cuerpo="EquilibrioCalculoNuevo.ok",
           descripcion="Con microhub_id o candidato_id toma costos de costos, ticket de demanda y la demanda esperada de demanda y cobertura; cualquier dato escrito a mano "
                       "los sustituye. Responde la cuenta paso a paso, de dónde salió cada número y la decisión. Con guardar=true (equilibrio.editar) deja el escenario y responde 201.",
           respuestas={200: ("Cálculo", "EquilibrioCalculo.ok")}, errores=[400, 403, 404, 422, 503])
documentar(app, "GET", f"{RUTA}/microhubs", "Equilibrio de cada microhub", permisos=["equilibrio.ver"],
           descripcion="Para cada microhub activo, con sus costos reales y la demanda de las zonas que cubre repartida entre los microhubs que las cubren.",
           respuestas={200: ("Tabla de microhubs", "EquilibrioMicrohubs.ok")}, errores=[403, 503])
documentar(app, "POST", f"{RUTA}/sensibilidad", "Sensibilidad del equilibrio", permisos=["equilibrio.ver"], cuerpo="EquilibrioSensibilidadNueva.ok",
           descripcion="Mueve ticket, pedidos por día, costos fijos, costo variable y margen bruto ±10 y ±20 %, uno por uno, y ordena las variables por cuánto mueven la utilidad.",
           respuestas={200: ("Filas y ranking", "EquilibrioSensibilidad.ok")}, errores=[400, 403, 404, 422, 503])
documentar(app, "GET", f"{RUTA}/escenarios", "Escenarios guardados", permisos=["equilibrio.ver"], parametros=PAG,
           respuestas={200: ("Página de escenarios", "EquilibrioEscenarioLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{RUTA}/escenarios/{{id}}", "Un escenario guardado", permisos=["equilibrio.ver"], parametros=[("id", "path", "integer", "Id")],
           respuestas={200: ("Cálculo completo", "EquilibrioCalculo.ok")}, errores=[403, 404])
documentar(app, "DELETE", f"{RUTA}/escenarios/{{id}}", "Borrar un escenario", permisos=["equilibrio.editar"], parametros=[("id", "path", "integer", "Id")],
           respuestas={204: ("Sin cuerpo", None)}, errores=[403, 404])
documentar(app, "GET", f"{RUTA}/comparacion", "Comparar escenarios", permisos=["equilibrio.ver"], parametros=[("ids", "query", "string", "Dos a ocho ids separados por coma")],
           respuestas={200: ("Escenarios lado a lado", "EquilibrioComparacion.ok")}, errores=[400, 403, 404])
documentar(app, "GET", f"{RUTA}/supuestos", "Supuestos del modelo de equilibrio", permisos=["equilibrio.ver"],
           descripcion="Valor, origen (medido, supuesto o normativo), justificación y cómo calibrarlo con datos reales.",
           respuestas={200: ("Supuestos documentados", "SupuestosEquilibrio.ok")}, errores=[403])
