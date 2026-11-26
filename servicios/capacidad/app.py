"""
Servicio de capacidad · puerto 5117 · contrato v1

  GET /api/v1/capacidad/recursos                   personal de cada microhub
  GET /api/v1/capacidad/recursos/{microhub_id}     el de uno
  PUT /api/v1/capacidad/recursos/{microhub_id}     cambia operadores, repartidores o tope de espacio (capacidad.editar)
  GET /api/v1/capacidad/microhubs                  capacidad, carga, utilización y cuello de botella de cada microhub
  GET /api/v1/capacidad/microhubs/{id}             el detalle de uno, con el tiempo de cada etapa
  POST /api/v1/capacidad/simulaciones              qué pasaría con otra carga o con otro personal
  GET /api/v1/capacidad/cargas                     utilización a distintas cargas y el punto de saturación
  GET /api/v1/capacidad/supuestos                  de dónde sale cada valor y cómo se calibra

Responsabilidad única: cuántos pedidos puede procesar un microhub y qué tan cerca está de saturarse.
Usa las fórmulas de sistema_web/planeacion_calc.py (pc.capacidad), las mismas del portal y de planeación.

Modelo: cada operador hace picking, empaque y despacho uno tras otro, así que su ritmo combinado es
1 ÷ (1/picking + 1/empaque + 1/despacho). El reparto depende de cuántos repartidores hay, de la distancia y de las
paradas por viaje. La capacidad del microhub es la menor de las dos, limitada además por el espacio. La hora pico se
estima como el promedio horario por `cap_factor_pico`.
"""
import datetime as dt
import math

from flask import g, request

from comun import config, supuestos as sup
from comun.base import (crear_app, documentar, filtro_entero, leer_cuerpo, leer_paginacion, limitar_microhub, lista, paginacion, requiere,
                        responder)
from comun.base_errores import filtro_invalido, no_encontrado
from comun.calculo import pc
from comun.clientes import exigir, mapa
from comun.datos import conexion, consultar
from comun.formatos import ZONA, fecha
from comun.validar import Campo, validar

app = crear_app("capacidad", "Microhubs · Capacidad",
                "Capacidad por etapa, utilización, cuellos de botella y carga que soporta cada microhub.", 5117)
P = config.PREFIJO
DEFECTOS = {"picking_pedidos_hora": 10.0, "packing_pedidos_hora": 20.0, "despacho_pedidos_hora": 30.0, "umbral_utilizacion_estable": 70.0,
            "umbral_utilizacion_riesgo": 85.0, "velocidad_reparto_kmh": 22.0, "tiempo_servicio_min": 4.0, "paradas_por_viaje": 3.0,
            "horas_turno": 10.0, "cap_factor_pico": 1.35, "cap_distancia_entrega_km": 2.4}
CLAVES_SUPUESTOS = list(DEFECTOS)
DIAS_CARGA = 7


# --------------------------------------------------------------------
# Cálculo (funciones puras, sin bases de datos)
# --------------------------------------------------------------------
def evaluar(operadores, repartidores, distancia_km, capacidad_fisica, horas, carga_dia, p):
    """Capacidad del microhub y qué tan cargado está con `carga_dia` pedidos al día."""
    cap = pc.capacidad(operadores, repartidores, distancia_km, capacidad_fisica or None, horas, p)
    cap_dia, cap_hora = cap["capacidad_dia"], cap["capacidad_hora"]
    util = 100 * carga_dia / cap_dia if cap_dia else None
    pico_hora = carga_dia / horas * p["cap_factor_pico"] if horas else 0.0
    util_pico = 100 * pico_hora / cap_hora if cap_hora else None
    objetivo = p["umbral_utilizacion_riesgo"] / 100
    comb = 60 / cap["minutos_por_pedido_operacion"]
    ops_req = math.ceil(carga_dia / (comb * horas * objetivo)) if comb * horas else 0
    reps_req = math.ceil(carga_dia / (60 / cap["minutos_por_entrega"] * horas * objetivo)) if cap["minutos_por_entrega"] and horas else 0
    minutos = {"picking": 60 / p["picking_pedidos_hora"], "empaque": 60 / p["packing_pedidos_hora"], "despacho": 60 / p["despacho_pedidos_hora"]}
    total = sum(minutos.values())
    por_etapa = cap["por_etapa_hora"]
    etapas = [{"etapa": nombre, "minutos_por_pedido": round(m, 2), "pct_tiempo": round(100 * m / total, 1),
               "capacidad_hora": por_etapa["packing" if nombre == "empaque" else nombre]} for nombre, m in minutos.items()]
    etapas.append({"etapa": "reparto", "minutos_por_pedido": cap["minutos_por_entrega"], "pct_tiempo": None, "capacidad_hora": por_etapa["reparto"]})
    return {"operadores": operadores, "repartidores": repartidores, "capacidad_fisica": capacidad_fisica, "horas": horas, "distancia_km": distancia_km,
            "carga_dia": round(carga_dia, 1), "capacidad_hora": cap_hora, "capacidad_dia": cap_dia,
            "utilizacion_pct": None if util is None else round(util, 1), "nivel": None if util is None else pc.nivel_utilizacion(util, p),
            "utilizacion_pico_pct": None if util_pico is None else round(util_pico, 1),
            "nivel_pico": None if util_pico is None else pc.nivel_utilizacion(util_pico, p), "cuello_botella": cap["cuello_botella"],
            "minutos_por_pedido_operacion": cap["minutos_por_pedido_operacion"], "minutos_por_entrega": cap["minutos_por_entrega"],
            "etapas": etapas, "operadores_requeridos": ops_req, "repartidores_requeridos": reps_req,
            "holgura_pedidos_dia": round(cap_dia - carga_dia, 1), "formula": cap["formula"]}


def curva_de_carga(operadores, repartidores, distancia_km, capacidad_fisica, horas, cargas, p):
    """Utilización a distintas cargas. Lo que pasa de la capacidad se rechaza."""
    filas = []
    for c in cargas:
        e = evaluar(operadores, repartidores, distancia_km, capacidad_fisica, horas, c, p)
        cap = e["capacidad_dia"]
        filas.append({"pedidos_dia": round(c, 1), "utilizacion_pct": e["utilizacion_pct"], "nivel": e["nivel"],
                      "utilizacion_pico_pct": e["utilizacion_pico_pct"], "atendidos": round(min(c, cap), 1), "rechazados": round(max(c - cap, 0), 1)})
    return filas


# --------------------------------------------------------------------
# Datos
# --------------------------------------------------------------------
def parametros():
    return sup.valores(DEFECTOS)


def hoy():
    return dt.datetime.now(ZONA).date()


def recurso(f, hubs):
    h = hubs.get(f["microhub_id"])
    return {"microhub": {"id": f["microhub_id"], "nombre": h["nombre"] if h else None}, "operadores": f["operadores"],
            "repartidores": f["repartidores"], "capacidad_fisica": f["capacidad_fisica"], "actualizado_en": fecha(f["actualizado_en"])}


SQL_RECURSO = "SELECT microhub_id, operadores, repartidores, capacidad_fisica, actualizado_en FROM capacidad_recurso "


def _recurso(mid):
    f = consultar(SQL_RECURSO + "WHERE microhub_id = %s", (mid,), una=True)
    if not f:
        raise no_encontrado("Ese microhub no tiene recursos registrados.")
    return f


def carga_observada(mid):
    """Pedidos por día de los últimos 7 días del microhub, según el servicio de pedidos."""
    fin = hoy()
    total, pagina = 0, 1
    while pagina <= 5:
        r = exigir("pedidos", "GET", "pedidos/resumen", params={"microhub_id": mid, "desde": (fin - dt.timedelta(days=DIAS_CARGA - 1)).isoformat(),
                                                                "hasta": fin.isoformat(), "por_pagina": 100, "pagina": pagina})
        total += sum(x["pedidos"] for x in r["datos"])
        if pagina >= r["paginacion"]["paginas"]:
            break
        pagina += 1
    return total / DIAS_CARGA


def _numero(nombre, defecto, minimo, maximo):
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


def detalle(f, hubs, p, carga=None, distancia=None, horas=None):
    mid = f["microhub_id"]
    c = carga_observada(mid) if carga is None else carga
    e = evaluar(f["operadores"], f["repartidores"], distancia if distancia is not None else p["cap_distancia_entrega_km"],
                f["capacidad_fisica"], horas if horas is not None else p["horas_turno"], c, p)
    h = hubs.get(mid)
    return {"microhub": {"id": mid, "nombre": h["nombre"] if h else None}, **e}


def usados(p, modificados):
    return sup.usados({k: p[k] for k in ("umbral_utilizacion_estable", "umbral_utilizacion_riesgo", "cap_factor_pico", "picking_pedidos_hora",
                                         "packing_pedidos_hora", "despacho_pedidos_hora", "velocidad_reparto_kmh", "tiempo_servicio_min",
                                         "paradas_por_viaje")}, modificados)


def salida(d, modificados, p):
    return {**d, "supuestos_usados": usados(p, modificados)}


ITEMS = {"etapas": "etapa", "supuestos_usados": "supuesto"}


# --------------------------------------------------------------------
# Recursos
# --------------------------------------------------------------------
@app.get(f"{P}/capacidad/recursos")
@requiere("capacidad.ver")
def recursos():
    pagina, por, desde = leer_paginacion()
    hub = limitar_microhub(filtro_entero("microhub_id"))
    where, args = ("WHERE microhub_id = %s", [hub]) if hub else ("", [])
    total = consultar(f"SELECT count(*) AS n FROM capacidad_recurso {where}", args, una=True)["n"]
    filas = consultar(SQL_RECURSO + where + " ORDER BY microhub_id LIMIT %s OFFSET %s", (*args, por, desde))
    hubs = mapa("microhubs", "microhubs")
    return lista(filas, paginacion(pagina, por, total), "recurso", "recursos_capacidad", lambda f: recurso(f, hubs))


@app.get(f"{P}/capacidad/recursos/<int:mid>")
@requiere("capacidad.ver")
def recurso_uno(mid):
    limitar_microhub(mid)
    return responder(recurso(_recurso(mid), mapa("microhubs", "microhubs")), raiz="recurso_capacidad")


@app.put(f"{P}/capacidad/recursos/<int:mid>")
@requiere("capacidad.editar")
def fijar_recurso(mid):
    d = validar(leer_cuerpo("recurso_capacidad_nuevo"), [Campo("operadores", "int", minimo=1, maximo=50), Campo("repartidores", "int", minimo=1, maximo=50),
                                                         Campo("capacidad_fisica", "int", req=False, nulo=True, minimo=1, maximo=100000)])
    hubs = mapa("microhubs", "microhubs")
    if mid not in hubs:
        raise no_encontrado("No existe ese microhub.")
    with conexion() as con, con.cursor() as cur:
        cur.execute("INSERT INTO capacidad_recurso (microhub_id, operadores, repartidores, capacidad_fisica, actualizado_por) VALUES (%s,%s,%s,%s,%s) "
                    "ON CONFLICT (microhub_id) DO UPDATE SET operadores = EXCLUDED.operadores, repartidores = EXCLUDED.repartidores, "
                    "capacidad_fisica = EXCLUDED.capacidad_fisica, actualizado_por = EXCLUDED.actualizado_por, actualizado_en = now()",
                    (mid, d["operadores"], d["repartidores"], d.get("capacidad_fisica"), g.usuario["id"]))
    return responder(recurso(_recurso(mid), hubs), raiz="recurso_capacidad")


# --------------------------------------------------------------------
# Capacidad y utilización
# --------------------------------------------------------------------
@app.get(f"{P}/capacidad/microhubs")
@requiere("capacidad.ver")
def microhubs():
    pagina, por, desde = leer_paginacion()
    hub = limitar_microhub(filtro_entero("microhub_id"))
    p = parametros()
    carga, mod_c = _numero("carga_dia", None, 0, 100000)
    dist, mod_d = _numero("distancia_km", None, 0, 100)
    horas, mod_h = _numero("horas", None, 1, 24)
    where, args = ("WHERE microhub_id = %s", [hub]) if hub else ("", [])
    total = consultar(f"SELECT count(*) AS n FROM capacidad_recurso {where}", args, una=True)["n"]
    filas = consultar(SQL_RECURSO + where + " ORDER BY microhub_id LIMIT %s OFFSET %s", (*args, por, desde))
    hubs = mapa("microhubs", "microhubs")
    modificados = [n for n, m in (("carga_dia", mod_c), ("distancia_km", mod_d), ("horas", mod_h)) if m]
    return lista(filas, paginacion(pagina, por, total), "microhub", "capacidad_microhubs",
                 lambda f: salida(detalle(f, hubs, p, carga, dist, horas), modificados, p), items={**ITEMS, "valores_modificados": "clave"})


@app.get(f"{P}/capacidad/microhubs/<int:mid>")
@requiere("capacidad.ver")
def microhub_uno(mid):
    limitar_microhub(mid)
    p = parametros()
    carga, mod_c = _numero("carga_dia", None, 0, 100000)
    dist, mod_d = _numero("distancia_km", None, 0, 100)
    horas, mod_h = _numero("horas", None, 1, 24)
    d = detalle(_recurso(mid), mapa("microhubs", "microhubs"), p, carga, dist, horas)
    return responder(salida(d, [n for n, m in (("carga_dia", mod_c), ("distancia_km", mod_d), ("horas", mod_h)) if m], p),
                     raiz="capacidad_microhub", items=ITEMS)


@app.post(f"{P}/capacidad/simulaciones")
@requiere("capacidad.ver")
def simular():
    d = validar(leer_cuerpo("capacidad_simulacion_nueva"), [
        Campo("microhub_id", "int", minimo=1), Campo("pedidos_dia", "num", minimo=0, maximo=100000),
        Campo("operadores", "int", req=False, nulo=True, minimo=1, maximo=50), Campo("repartidores", "int", req=False, nulo=True, minimo=1, maximo=50),
        Campo("horas", "num", req=False, nulo=True, minimo=1, maximo=24), Campo("distancia_km", "num", req=False, nulo=True, minimo=0, maximo=100),
        Campo("capacidad_fisica", "int", req=False, nulo=True, minimo=1, maximo=100000)])
    mid = limitar_microhub(d["microhub_id"])
    base = _recurso(mid)
    p = parametros()
    hubs = mapa("microhubs", "microhubs")
    nombre = (hubs.get(mid) or {}).get("nombre")
    cambios = {k: d[k] for k in ("operadores", "repartidores", "capacidad_fisica") if d.get(k) is not None}
    escenario_recurso = {**base, **cambios}
    horas, dist = d.get("horas") or p["horas_turno"], d.get("distancia_km") if d.get("distancia_km") is not None else p["cap_distancia_entrega_km"]
    esc = evaluar(escenario_recurso["operadores"], escenario_recurso["repartidores"], dist, escenario_recurso["capacidad_fisica"], horas, d["pedidos_dia"], p)
    actual = evaluar(base["operadores"], base["repartidores"], p["cap_distancia_entrega_km"], base["capacidad_fisica"], p["horas_turno"], d["pedidos_dia"], p)
    modificados = [k for k in ("operadores", "repartidores", "capacidad_fisica", "horas", "distancia_km") if d.get(k) is not None]
    return responder({"microhub": {"id": mid, "nombre": nombre}, "pedidos_dia": d["pedidos_dia"], "escenario": esc, "actual": actual,
                      "diferencia_capacidad_dia": round(esc["capacidad_dia"] - actual["capacidad_dia"], 1),
                      "diferencia_utilizacion_pct": None if esc["utilizacion_pct"] is None or actual["utilizacion_pct"] is None
                      else round(esc["utilizacion_pct"] - actual["utilizacion_pct"], 1),
                      "valores_modificados": modificados, "supuestos_usados": usados(p, [])}, raiz="capacidad_simulacion", items={**ITEMS, "valores_modificados": "clave"})


@app.get(f"{P}/capacidad/cargas")
@requiere("capacidad.ver")
def cargas():
    mid = limitar_microhub(filtro_entero("microhub_id"))
    if not mid:
        raise filtro_invalido("microhub_id", "microhub_id es obligatorio.")
    f = _recurso(mid)
    p = parametros()
    dist, _ = _numero("distancia_km", p["cap_distancia_entrega_km"], 0, 100)
    horas, _ = _numero("horas", p["horas_turno"], 1, 24)
    pasos = int(_numero("pasos", 8, 2, 40)[0])
    cap_dia = pc.capacidad(f["operadores"], f["repartidores"], dist, f["capacidad_fisica"] or None, horas, p)["capacidad_dia"]
    minimo, _ = _numero("desde", round(cap_dia * 0.25, 1), 0, 100000)
    maximo, _ = _numero("hasta", round(cap_dia * 1.5, 1), 1, 100000)
    if maximo <= minimo:
        raise filtro_invalido("hasta", "hasta debe ser mayor que desde.")
    paso = (maximo - minimo) / (pasos - 1)
    filas = curva_de_carga(f["operadores"], f["repartidores"], dist, f["capacidad_fisica"], horas, [minimo + paso * i for i in range(pasos)], p)
    hubs = mapa("microhubs", "microhubs")
    return responder({"microhub": {"id": mid, "nombre": (hubs.get(mid) or {}).get("nombre")}, "capacidad_dia": cap_dia,
                      "carga_en_riesgo": round(cap_dia * p["umbral_utilizacion_riesgo"] / 100, 1),
                      "carga_estable": round(cap_dia * p["umbral_utilizacion_estable"] / 100, 1), "filas": filas,
                      "supuestos_usados": usados(p, [])}, raiz="capacidad_cargas", items={"filas": "fila", "supuestos_usados": "supuesto"})


@app.get(f"{P}/capacidad/supuestos")
@requiere("capacidad.ver")
def supuestos_capacidad():
    return responder({"datos": sup.listar(CLAVES_SUPUESTOS)}, raiz="supuestos_capacidad", items={"datos": "supuesto"})


# --------------------------------------------------------------------
# Documentación
# --------------------------------------------------------------------
PAG = [("pagina", "query", "integer", "Página (1…)"), ("por_pagina", "query", "integer", "1 a 100")]
HUB = ("microhub_id", "query", "integer", "Microhub. Operador y supervisor solo ven el suyo")
MID = [("mid", "path", "integer", "Id del microhub")]
SUPUESTOS_PETICION = [("carga_dia", "query", "number", "Pedidos por día; por omisión, el promedio de los últimos 7 días según pedidos"),
                      ("distancia_km", "query", "number", "Distancia de entrega, solo ida; por omisión `cap_distancia_entrega_km`"),
                      ("horas", "query", "number", "Horas de trabajo al día; por omisión `horas_turno`")]
documentar(app, "GET", f"{P}/capacidad/recursos", "Personal de los microhubs", permisos=["capacidad.ver"], parametros=PAG + [HUB],
           respuestas={200: ("Página de recursos", "RecursoCapacidadLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/capacidad/recursos/{{mid}}", "Personal de un microhub", permisos=["capacidad.ver"], parametros=MID,
           respuestas={200: ("Recursos del microhub", "RecursoCapacidad.ok")}, errores=[403, 404])
documentar(app, "PUT", f"{P}/capacidad/recursos/{{mid}}", "Cambiar el personal de un microhub", permisos=["capacidad.editar"], parametros=MID,
           cuerpo="RecursoCapacidadNuevo.ok", descripcion="Crea o sustituye los recursos. capacidad_fisica es el tope de pedidos por día que permite el espacio.",
           respuestas={200: ("Recursos guardados", "RecursoCapacidad.ok")}, errores=[400, 403, 404, 422])
documentar(app, "GET", f"{P}/capacidad/microhubs", "Capacidad de los microhubs", permisos=["capacidad.ver"], parametros=PAG + [HUB] + SUPUESTOS_PETICION,
           descripcion="Capacidad por hora y por día, utilización con la carga indicada (o la observada), nivel (estable, atención o riesgo), "
                       "utilización en hora pico, cuello de botella y personal requerido para quedar por debajo del umbral de riesgo.",
           respuestas={200: ("Página de microhubs", "CapacidadMicrohubLista.ok")}, errores=[400, 403, 503])
documentar(app, "GET", f"{P}/capacidad/microhubs/{{mid}}", "Capacidad de un microhub", permisos=["capacidad.ver"], parametros=MID + SUPUESTOS_PETICION,
           respuestas={200: ("Detalle con el tiempo de cada etapa", "CapacidadMicrohub.ok")}, errores=[400, 403, 404, 503])
documentar(app, "POST", f"{P}/capacidad/simulaciones", "Simular otra carga o con otro personal", permisos=["capacidad.ver"], cuerpo="CapacidadSimulacionNueva.ok",
           descripcion="Compara el escenario (con los cambios indicados) contra la situación actual a la misma carga. No guarda nada.",
           respuestas={200: ("Escenario y situación actual", "CapacidadSimulacion.ok")}, errores=[400, 403, 404, 422])
documentar(app, "GET", f"{P}/capacidad/cargas", "Utilización a distintas cargas", permisos=["capacidad.ver"],
           parametros=[HUB, ("desde", "query", "number", "Carga mínima, pedidos por día; por omisión 25 % de la capacidad"),
                       ("hasta", "query", "number", "Carga máxima; por omisión 150 % de la capacidad"), ("pasos", "query", "integer", "2 a 40 (8 por omisión)"),
                       ("distancia_km", "query", "number", "Distancia de entrega"), ("horas", "query", "number", "Horas de trabajo al día")],
           descripcion="Muestra en qué carga el microhub entra en riesgo y en cuál se satura; lo que pasa de la capacidad se rechaza.",
           respuestas={200: ("Curva de carga", "CapacidadCargas.ok")}, errores=[400, 403, 404])
documentar(app, "GET", f"{P}/capacidad/supuestos", "Supuestos del modelo de capacidad", permisos=["capacidad.ver"],
           descripcion="Valor, origen (medido, supuesto o normativo), justificación y cómo calibrarlo con datos reales.",
           respuestas={200: ("Supuestos documentados", "SupuestosCapacidad.ok")}, errores=[403])
