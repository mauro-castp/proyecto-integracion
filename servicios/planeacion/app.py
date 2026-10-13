"""
Servicio de planeación · puerto 5106 · contrato v1

  GET  /api/v1/candidatos                     ubicaciones candidatas (q, decision, zona_id)
  GET  /api/v1/candidatos/{id}                un candidato
  POST /api/v1/candidatos                     alta (planeacion.editar); costo fijo calculado por PostgreSQL
  PUT  /api/v1/candidatos/{id}                modificación (planeacion.editar)
  POST /api/v1/candidatos/{id}/decision       decisión HUMANA de apertura con motivo (queda en la bitácora)
  POST /api/v1/candidatos/{id}/simular        simulación con los datos del candidato (+ supuestos opcionales)
  POST /api/v1/simulaciones                   simulación libre con supuestos explícitos
  GET  /api/v1/simulaciones/resumen           agregación en MongoDB de las simulaciones ejecutadas
  GET  /api/v1/escenarios[/{id}]              escenarios guardados
  POST /api/v1/escenarios                     guardar escenario (planeacion.editar)

No duplica fórmulas: usa planeacion_calc.py (funciones puras y probadas) y
las consultas de planeacion.py del sistema web. Por eso el portal, este
servicio y la app de escritorio dan exactamente los mismos números.
Cada simulación deja su rastro en MongoDB (ejecuciones_analiticas).
"""
import importlib.util
import json
import sys
import time
from pathlib import Path

from flask import g

from comun import config
from comun.base import (crear_app, documentar, filtro_entero, filtro_opcion, leer_cuerpo, leer_paginacion, lista,
                        paginacion, requiere, responder, texto_busqueda)
from comun.base_errores import ErrorApi, invalido, no_encontrado
from comun.datos import ahora, conexion, consultar, mongo, mongo_insertar
from comun.formatos import dinero, fecha, numero
from comun.validar import Campo, validar

# Código del sistema web: en Docker se copia a /app/web; en desarrollo se lee de sistema_web/.
_web = Path("/app/web") if Path("/app/web").is_dir() else Path(__file__).resolve().parents[2] / "sistema_web"
sys.path.insert(0, str(_web))
import planeacion_calc as pc          # noqa: E402

# planeacion.py del web se carga con otro nombre: este paquete también se llama «planeacion».
_spec = importlib.util.spec_from_file_location("web_planeacion", _web / "planeacion.py")
web_plan = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(web_plan)

app = crear_app("planeacion", "Microhubs · Planeación",
                "Ubicaciones candidatas, simulación, punto de equilibrio y escenarios.", 5106,
                dependencias=("postgres", "redis", "mongo"))
P = config.PREFIJO
DECISIONES = ["pendiente", "aceptado", "rechazado", "condicionado"]
DINERO_SUP = ("ticket", "costo_entrega", "renta", "nomina", "servicios", "otros")

CAMPOS_CANDIDATO = [
    Campo("clave", min_len=1, max_len=20), Campo("nombre", min_len=3, max_len=120),
    Campo("latitud", "num", minimo=20, maximo=33), Campo("longitud", "num", minimo=-118, maximo=-86),
    Campo("renta_estimada", "num", minimo=0, decimales=2), Campo("nomina_estimada", "num", minimo=0, decimales=2),
    Campo("servicios_estimados", "num", minimo=0, decimales=2), Campo("otros_costos", "num", minimo=0, decimales=2),
    Campo("superficie_m2", "num", minimo=1), Campo("capacidad_fisica", "int", minimo=1),
    Campo("accesibilidad_vial", "int", minimo=1, maximo=10), Campo("zona_id", "int", minimo=1),
    Campo("poblacion_cubierta", "int", minimo=0), Campo("radio_km", "num", minimo=0.1, maximo=10)]


def campos_supuestos(req=True):
    return [Campo("demanda_diaria", "num", req, minimo=0), Campo("operadores", "int", req, minimo=1),
            Campo("repartidores", "int", req, minimo=1), Campo("ticket", "num", req, minimo=0, decimales=2),
            Campo("costo_entrega", "num", req, minimo=0, decimales=2),
            Campo("margen_bruto", "num", req, minimo=0, maximo=1),
            Campo("renta", "num", req, minimo=0, decimales=2), Campo("nomina", "num", req, minimo=0, decimales=2),
            Campo("servicios", "num", req, minimo=0, decimales=2), Campo("otros", "num", req, minimo=0, decimales=2),
            Campo("distancia_km", "num", req, minimo=0), Campo("capacidad_fisica", "int", False, minimo=1),
            Campo("horas", "num", False, minimo=1, maximo=24)]


# --------------------------------------------------------------------
# Proyecciones al contrato
# --------------------------------------------------------------------
def candidato(f):
    return {"id": f["id"], "clave": f["clave"], "nombre": f["nombre"], "latitud": numero(f["latitud"]),
            "longitud": numero(f["longitud"]), "renta_estimada": dinero(f["renta_estimada"]),
            "nomina_estimada": dinero(f["nomina_estimada"]), "servicios_estimados": dinero(f["servicios_estimados"]),
            "otros_costos": dinero(f["otros_costos"]), "costo_fijo": dinero(f["costo_fijo"]),
            "superficie_m2": numero(f["superficie_m2"]), "capacidad_fisica": f["capacidad_fisica"],
            "accesibilidad_vial": f["accesibilidad_vial"], "zona_id": f["zona_id"],
            "poblacion_cubierta": f["poblacion_cubierta"], "radio_km": numero(f["radio_km"]),
            "decision": f["decision"], "decision_motivo": f["decision_motivo"]}


def supuestos(s):
    """dict de supuestos (API o guardado por el web) → TSupuestos en el orden del XSD."""
    base = {**pc.SUPUESTOS_BASE, **{k: v for k, v in (s or {}).items() if v is not None}}
    out = {}
    for c in campos_supuestos():
        v = base.get(c.nombre)
        if v is None:
            continue
        if c.tipo == "int":
            out[c.nombre] = int(float(v))
        elif c.nombre in DINERO_SUP:
            out[c.nombre] = dinero(v)
        else:
            out[c.nombre] = float(v)
    return out


def resultados(r):
    """Salida de planeacion_calc.simular() → TResultados (decisión y explicación de la ficha)."""
    ficha = r.get("ficha") or {}
    eq = r.get("equilibrio") or {}
    return {"atendidos": float(r["atendidos"]), "rechazados": float(r["rechazados"]),
            "utilizacion": float(r["utilizacion"]), "nivel": r["nivel"],
            "tiempo_estimado_min": float(r["tiempo_estimado_min"]),
            "operadores_requeridos": int(r["operadores_requeridos"]),
            "repartidores_requeridos": int(r["repartidores_requeridos"]),
            "ingreso_dia": dinero(r["ingreso_dia"]), "margen_dia": dinero(r["margen_dia"]),
            "costo_por_pedido": dinero(r.get("costo_por_pedido")),
            "equilibrio": {"margen_pedido": dinero(eq.get("margen_pedido", 0)), "mensual": eq.get("mensual"),
                           "diario": eq.get("diario")},
            "decision": ficha.get("decision", "NO VIABLE CON LOS SUPUESTOS ACTUALES"),
            "explicacion": list(ficha.get("explicacion", [])) + list(ficha.get("acciones", []))}


def escenario(f):
    res = f["resultados"] if isinstance(f["resultados"], dict) else json.loads(f["resultados"])
    sup = f["supuestos"] if isinstance(f["supuestos"], dict) else json.loads(f["supuestos"])
    return {"id": f["id"], "nombre": f["nombre"], "candidato_id": f["ubicacion_candidata_id"],
            "supuestos": supuestos(sup), "resultados": resultados(res), "creado_en": fecha(f["creado_en"])}


# --------------------------------------------------------------------
# Candidatos
# --------------------------------------------------------------------
def _candidato(cid):
    f = consultar("SELECT * FROM ubicacion_candidata WHERE id = %s", (cid,), una=True)
    if not f:
        raise no_encontrado("No existe el candidato.")
    return f


def _validar_candidato():
    d = validar(leer_cuerpo("candidato_nuevo"), CAMPOS_CANDIDATO)
    if not consultar("SELECT 1 FROM zona WHERE id = %s", (d["zona_id"],), una=True):
        raise invalido("zona_id", "No existe esa zona.")
    return d


@app.get(f"{P}/candidatos")
@requiere("planeacion.ver")
def candidatos():
    pagina, por, desde = leer_paginacion()
    q, dec, zona = texto_busqueda(), filtro_opcion("decision", DECISIONES), filtro_entero("zona_id")
    where, args = ["estatus = 'activo'"], []
    if q:
        where.append("(nombre ILIKE %s OR clave ILIKE %s)"); args += [f"%{q}%"] * 2
    if dec:
        where.append("decision = %s"); args.append(dec)
    if zona:
        where.append("zona_id = %s"); args.append(zona)
    w = " AND ".join(where)
    total = consultar(f"SELECT count(*) AS n FROM ubicacion_candidata WHERE {w}", args, una=True)["n"]
    filas = consultar(f"SELECT * FROM ubicacion_candidata WHERE {w} ORDER BY id LIMIT %s OFFSET %s", (*args, por, desde))
    return lista(filas, paginacion(pagina, por, total), "candidato", "candidatos", candidato)


@app.get(f"{P}/candidatos/<int:cid>")
@requiere("planeacion.ver")
def candidato_uno(cid):
    return responder(candidato(_candidato(cid)), raiz="candidato")


COLUMNAS = [c.nombre for c in CAMPOS_CANDIDATO]


@app.post(f"{P}/candidatos")
@requiere("planeacion.editar")
def candidato_crear():
    d = _validar_candidato()
    with conexion() as con, con.cursor() as cur:
        cur.execute(f"INSERT INTO ubicacion_candidata ({', '.join(COLUMNAS)}) VALUES ({', '.join(['%s'] * len(COLUMNAS))}) "
                    "RETURNING *", [d[c] for c in COLUMNAS])
        f = cur.fetchone()
    return responder(candidato(f), 201, raiz="candidato")


@app.put(f"{P}/candidatos/<int:cid>")
@requiere("planeacion.editar")
def candidato_editar(cid):
    _candidato(cid)
    d = _validar_candidato()
    with conexion() as con, con.cursor() as cur:
        cur.execute(f"UPDATE ubicacion_candidata SET {', '.join(f'{c} = %s' for c in COLUMNAS)} WHERE id = %s RETURNING *",
                    [d[c] for c in COLUMNAS] + [cid])
        f = cur.fetchone()
    return responder(candidato(f), raiz="candidato")


@app.post(f"{P}/candidatos/<int:cid>/decision")
@requiere("planeacion.editar")
def decidir(cid):
    _candidato(cid)
    d = validar(leer_cuerpo("decision"), [Campo("decision", opciones=["aceptado", "rechazado", "condicionado"]),
                                          Campo("motivo", min_len=3, max_len=300)])
    with conexion() as con, con.cursor() as cur:
        cur.execute("UPDATE ubicacion_candidata SET decision = %s, decision_motivo = %s, decision_por = %s, "
                    "decision_en = now() WHERE id = %s RETURNING *", (d["decision"], d["motivo"], g.usuario["id"], cid))
        f = cur.fetchone()
    return responder(candidato(f), raiz="candidato")


# --------------------------------------------------------------------
# Simulación
# --------------------------------------------------------------------
def _supuestos_candidato(cid):
    """Supuestos iniciales del candidato: demanda cubierta, costos fijos, distancia y capacidad física."""
    p = web_plan.parametros()
    hist = web_plan.historial(p)
    c = web_plan.get_candidato(cid)
    if not c:
        raise no_encontrado("No existe el candidato.")
    ev = web_plan.evaluar_candidatos(p, hist, [c])[0]
    return web_plan.supuestos_de(ev, hist, p), p, hist


def _simular(sup, p, escenario_id, nombre, datos_suficientes=True):
    inicio = time.perf_counter()
    r = pc.simular(sup, p)
    salida = resultados(r)
    mongo_insertar("ejecuciones_analiticas", {
        "escenario_id": escenario_id, "nombre_escenario": nombre, "tipo_analisis": "punto_equilibrio",
        "ejecutado_en": ahora(), "usuario_id": int(g.usuario["id"]), "version_modelo": "planeacion_calc 2.1",
        "parametros_entrada": {k: float(v) for k, v in supuestos(sup).items()},
        "supuestos": [f"{k} = {v}" for k, v in supuestos(sup).items()],
        "resultados": {"decision": salida["decision"], "utilizacion": salida["utilizacion"],
                       "atendidos": salida["atendidos"], "equilibrio_diario": salida["equilibrio"]["diario"],
                       "costo_por_pedido": float(salida["costo_por_pedido"]) if salida["costo_por_pedido"] is not None else None},
        "recomendacion": salida["decision"], "datos_suficientes": bool(datos_suficientes),
        "duracion_ms": int((time.perf_counter() - inicio) * 1000), "aplicado_por": None})
    return r, salida


@app.post(f"{P}/candidatos/<int:cid>/simular")
@requiere("simulacion.ejecutar")
def simular_candidato(cid):
    _candidato(cid)
    cuerpo = leer_cuerpo("simular", obligatorio=False)
    extra = cuerpo.get("supuestos") if isinstance(cuerpo.get("supuestos"), dict) else {}
    base, p, hist = _supuestos_candidato(cid)
    sup = {**base, **validar(extra, campos_supuestos(req=False), prefijo="supuestos.")}
    _, salida = _simular(sup, p, f"candidato-{cid}", f"Candidato {cid}", datos_suficientes=hist["pedidos"] > 0)
    return responder(salida, raiz="resultados")


@app.post(f"{P}/simulaciones")
@requiere("simulacion.ejecutar")
def simulacion_libre():
    cuerpo = leer_cuerpo("simulacion")
    d = validar(cuerpo, [Campo("candidato_id", "int", req=False, minimo=1), Campo("supuestos", "obj")])
    sup = validar(d["supuestos"], campos_supuestos(), prefijo="supuestos.")
    if d.get("candidato_id"):
        _candidato(d["candidato_id"])
    _, salida = _simular(sup, web_plan.parametros(), f"candidato-{d['candidato_id']}" if d.get("candidato_id") else "libre",
                         "Simulación libre")
    return responder(salida, raiz="resultados")


@app.get(f"{P}/simulaciones/resumen")
@requiere("planeacion.ver")
def resumen():
    db = mongo()
    if db is None:
        raise ErrorApi(503, "SERVICIO_NO_DISPONIBLE", "MongoDB no está disponible para el resumen.")
    grupos = list(db.ejecuciones_analiticas.aggregate([
        {"$match": {"tipo_analisis": "punto_equilibrio"}},
        {"$group": {"_id": "$resultados.decision", "cantidad": {"$sum": 1},
                    "utilizacion_promedio": {"$avg": "$resultados.utilizacion"}}},
        {"$sort": {"cantidad": -1}}]))
    validas = {"VIABLE", "VIABLE CON RIESGO DE CAPACIDAD", "NO VIABLE CON LOS SUPUESTOS ACTUALES"}
    por = [{"decision": x["_id"], "cantidad": int(x["cantidad"]),
            "utilizacion_promedio": round(float(x["utilizacion_promedio"] or 0), 1)} for x in grupos if x["_id"] in validas]
    return responder({"total": sum(x["cantidad"] for x in por), "por_decision": por}, raiz="simulaciones_resumen")


# --------------------------------------------------------------------
# Escenarios (PostgreSQL, compartidos con el portal web)
# --------------------------------------------------------------------
@app.get(f"{P}/escenarios")
@requiere("planeacion.ver")
def escenarios():
    pagina, por, desde = leer_paginacion()
    q, cand = texto_busqueda(), filtro_entero("candidato_id")
    where, args = ["TRUE"], []
    if q:
        where.append("nombre ILIKE %s"); args.append(f"%{q}%")
    if cand:
        where.append("ubicacion_candidata_id = %s"); args.append(cand)
    w = " AND ".join(where)
    total = consultar(f"SELECT count(*) AS n FROM escenario_planeacion WHERE {w}", args, una=True)["n"]
    filas = consultar(f"SELECT * FROM escenario_planeacion WHERE {w} ORDER BY id DESC LIMIT %s OFFSET %s",
                      (*args, por, desde))
    return lista(filas, paginacion(pagina, por, total), "escenario", "escenarios", escenario)


@app.get(f"{P}/escenarios/<int:eid>")
@requiere("planeacion.ver")
def escenario_uno(eid):
    f = consultar("SELECT * FROM escenario_planeacion WHERE id = %s", (eid,), una=True)
    if not f:
        raise no_encontrado("No existe el escenario.")
    return responder(escenario(f), raiz="escenario")


@app.post(f"{P}/escenarios")
@requiere("planeacion.editar")
def escenario_crear():
    d = validar(leer_cuerpo("escenario_nuevo"), [Campo("nombre", min_len=3, max_len=120),
                                                 Campo("candidato_id", "int", req=False, minimo=1), Campo("supuestos", "obj")])
    sup = validar(d["supuestos"], campos_supuestos(), prefijo="supuestos.")
    if d.get("candidato_id"):
        _candidato(d["candidato_id"])
    r, _ = _simular(sup, web_plan.parametros(), "escenario-nuevo", d["nombre"])
    guardado = {**sup, **({"candidato_id": d["candidato_id"]} if d.get("candidato_id") else {})}
    with conexion() as con, con.cursor() as cur:
        cur.execute("INSERT INTO escenario_planeacion (nombre, ubicacion_candidata_id, supuestos, resultados, creado_por) "
                    "VALUES (%s,%s,%s,%s,%s) RETURNING *",
                    (d["nombre"], d.get("candidato_id"), json.dumps(guardado), json.dumps(r, default=float),
                     g.usuario["id"]))
        f = cur.fetchone()
    return responder(escenario(f), 201, raiz="escenario")


# --------------------------------------------------------------------
PAG = [("pagina", "query", "integer", "Página"), ("por_pagina", "query", "integer", "1 a 100"),
       ("q", "query", "string", "Texto a buscar")]
ID = [("id", "path", "integer", "Id")]
documentar(app, "GET", f"{P}/candidatos", "Ubicaciones candidatas", permisos=["planeacion.ver"], parametros=PAG + [
           ("decision", "query", "string", "pendiente|aceptado|rechazado|condicionado"), ("zona_id", "query", "integer", "Zona")],
           respuestas={200: ("Página de candidatos", "CandidatoLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/candidatos/{{id}}", "Un candidato", permisos=["planeacion.ver"], parametros=ID,
           respuestas={200: ("Candidato", "Candidato.ok")}, errores=[403, 404])
documentar(app, "POST", f"{P}/candidatos", "Registrar candidato", permisos=["planeacion.editar"], cuerpo="CandidatoNuevo.ok",
           descripcion="14 campos. costo_fijo = renta + nómina + servicios + otros, calculado por PostgreSQL (columna "
                       "generada). Clave repetida → 409.",
           respuestas={201: ("Candidato creado", "Candidato.ok")}, errores=[400, 403, 409, 422])
documentar(app, "PUT", f"{P}/candidatos/{{id}}", "Modificar candidato", permisos=["planeacion.editar"], parametros=ID,
           cuerpo="CandidatoNuevo.ok", respuestas={200: ("Candidato actualizado", "Candidato.ok")},
           errores=[400, 403, 404, 409, 422])
documentar(app, "POST", f"{P}/candidatos/{{id}}/decision", "Decisión de apertura", permisos=["planeacion.editar"],
           parametros=ID, cuerpo="Decision.ok",
           descripcion="La decisión es humana: aceptado, rechazado o condicionado, con motivo de al menos 3 caracteres. "
                       "Se guarda quién y cuándo, y el trigger de auditoría la registra.",
           respuestas={200: ("Candidato con la decisión", "Candidato.ok")}, errores=[400, 403, 404, 422])
documentar(app, "POST", f"{P}/candidatos/{{id}}/simular", "Simular candidato", permisos=["simulacion.ejecutar"],
           parametros=ID, cuerpo="Simular.ok",
           descripcion="Toma demanda cubierta, distancia, capacidad física y costos fijos del candidato; los supuestos "
                       "enviados reemplazan a los calculados. Devuelve la ficha de viabilidad (recomendación, no decisión).",
           respuestas={200: ("Resultados", "Resultados.ok")}, errores=[400, 403, 404, 422])
documentar(app, "POST", f"{P}/simulaciones", "Simulación libre", permisos=["simulacion.ejecutar"], cuerpo="Simulacion.ok",
           respuestas={200: ("Resultados", "Resultados.ok")}, errores=[400, 403, 404, 422])
documentar(app, "GET", f"{P}/simulaciones/resumen", "Resumen de simulaciones (MongoDB)", permisos=["planeacion.ver"],
           descripcion="Agregación $group sobre ejecuciones_analiticas: cuántas simulaciones por decisión y su utilización promedio.",
           respuestas={200: ("Resumen", "SimulacionesResumen.ok")}, errores=[403])
documentar(app, "GET", f"{P}/escenarios", "Escenarios guardados", permisos=["planeacion.ver"],
           parametros=PAG + [("candidato_id", "query", "integer", "Candidato")],
           respuestas={200: ("Página de escenarios", "EscenarioLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/escenarios/{{id}}", "Un escenario", permisos=["planeacion.ver"], parametros=ID,
           respuestas={200: ("Escenario", "Escenario.ok")}, errores=[403, 404])
documentar(app, "POST", f"{P}/escenarios", "Guardar escenario", permisos=["planeacion.editar"], cuerpo="EscenarioNuevo.ok",
           descripcion="Ejecuta la simulación y guarda supuestos y resultados en PostgreSQL; el portal web lo puede abrir.",
           respuestas={201: ("Escenario guardado", "Escenario.ok")}, errores=[400, 403, 404, 422])
