"""
Servicio de rutas · puerto 5118 · contrato v1

  POST /api/v1/rutas/planes                    propone rutas para los pedidos listos de un microhub (guardar = deja el plan)
  GET  /api/v1/rutas/planes[/{id}]             planes guardados
  POST /api/v1/rutas/planes/{id}/confirmar     confirma un plan propuesto y deja sus rutas en plan_ruta
  POST /api/v1/rutas/planes/{id}/cancelar      cancela un plan que no se ha confirmado
  POST /api/v1/rutas/planes/{id}/ajustes       quita o agrega un pedido, o registra un retraso, y recalcula
  POST /api/v1/rutas/comparaciones             el mismo conjunto de paradas con cuatro métodos de recorrido
  GET  /api/v1/rutas/supuestos                 de dónde sale cada valor y cómo se calibra

Responsabilidad única: en qué orden y con quién sale cada pedido. Los pedidos listos con sus coordenadas los pide a pedidos
(GET /pedidos/listos), los repartidores a entregas (GET /entregas/repartidores) y el punto de salida a microhubs.

Cómo arma las rutas (las mismas funciones del portal, planeacion_calc):
  1. Agrupa los pedidos por zona y reparte los grupos entre los repartidores, sin pasar de `max_paradas_repartidor` paradas.
  2. Ordena las paradas de cada repartidor: exacto (prueba todos los órdenes) hasta 8 paradas; con más, vecino más cercano
     mejorado con 2-opt. Se puede pedir otro método.
  3. Distancia por calle = línea recta × `factor_rodeo_distancia`. Minutos = distancia ÷ velocidad + `tiempo_servicio_min` por
     parada. Costo = km × `costo_km_reparto` + `costo_base_entrega` por entrega. No incluye el regreso al microhub.
"""
import datetime as dt

from flask import g, request

from comun import config, supuestos as sup
from comun.base import (crear_app, documentar, filtro_entero, filtro_opcion, leer_cuerpo, leer_paginacion, lista, limitar_microhub, paginacion,
                        requiere, responder)
from comun.base_errores import ErrorApi, conflicto, filtro_invalido, invalido, no_encontrado
from comun.calculo import pc
from comun.clientes import exigir, mapa
from comun.datos import como_json, conexion, consultar
from comun.formatos import ZONA, fecha
from comun.validar import Campo, validar

app = crear_app("rutas", "Microhubs · Rutas",
                "Planes de ruta: agrupar pedidos por zona, asignar repartidores, ordenar paradas, comparar recorridos y ajustar ante incidencias.", 5118)
P = config.PREFIJO
DEFECTOS = {"velocidad_reparto_kmh": 22.0, "tiempo_servicio_min": 4.0, "costo_km_reparto": 4.5, "costo_base_entrega": 18.0, "max_paradas_repartidor": 8.0,
            "factor_rodeo_distancia": 1.3, "cob_tiempo_max_min": 30.0, "paradas_por_viaje": 3.0}
CLAVES_SUPUESTOS = list(DEFECTOS)
METODOS = ["automatico", "vecino", "2opt", "exacto"]
NOMBRE_METODO = {"orden_llegada": "Orden de llegada", "vecino": "Vecino más cercano", "2opt": "Vecino más cercano + 2-opt", "exacto": "TSP exacto"}
MAX_EXACTO = 9


# --------------------------------------------------------------------
# Cálculo (funciones puras, sin bases de datos)
# --------------------------------------------------------------------
def ordenar(origen, paradas, metodo):
    """Índices de las paradas en el orden de visita."""
    n = len(paradas)
    if n == 0:
        return [], "Sin paradas"
    if metodo == "orden_llegada":
        return list(range(n)), NOMBRE_METODO["orden_llegada"]
    if metodo == "vecino":
        return pc.vecino_mas_cercano(origen, paradas), NOMBRE_METODO["vecino"]
    if metodo == "2opt":
        return pc.dos_opt(origen, paradas, pc.vecino_mas_cercano(origen, paradas)), NOMBRE_METODO["2opt"]
    if metodo == "exacto" or (metodo == "automatico" and n <= 8):
        if n > MAX_EXACTO:
            raise ErrorApi(422, "VALIDACION", f"El método exacto prueba todos los órdenes y solo se usa hasta {MAX_EXACTO} paradas; hay {n}.")
        return pc.tsp_exacto(origen, paradas), NOMBRE_METODO["exacto"]
    return pc.dos_opt(origen, paradas, pc.vecino_mas_cercano(origen, paradas)), NOMBRE_METODO["2opt"]


def metricas(origen, paradas, orden, p):
    """Distancia por calle, minutos acumulados por parada y costo de recorrer las paradas en ese orden."""
    rodeo = p["factor_rodeo_distancia"]
    recta, tramos = pc.distancia_ruta(origen, paradas, orden)
    acum, detalle = 0.0, []
    for k, (i, t) in enumerate(zip(orden, tramos), 1):
        calle = t * rodeo
        acum += calle / p["velocidad_reparto_kmh"] * 60 + p["tiempo_servicio_min"]
        detalle.append({"orden": k, "indice": i, "tramo_km": round(calle, 2), "minutos_acum": round(acum, 1)})
    distancia = recta * rodeo
    return {"distancia_km": round(distancia, 2), "minutos": round(acum, 1),
            "costo": round(distancia * p["costo_km_reparto"] + p["costo_base_entrega"] * len(paradas), 2), "tramos": detalle}


def ruta_de(origen, repartidor, paradas, metodo, p, zonas=None):
    orden, nombre = ordenar(origen, paradas, metodo)
    ordenadas = [paradas[i] for i in orden]
    m = metricas(origen, ordenadas, list(range(len(ordenadas))), p)
    return {"repartidor": {"id": repartidor["id"], "nombre": repartidor["nombre"]}, "metodo": nombre,
            "zonas": zonas if zonas is not None else sorted({x["zona"] for x in ordenadas}),
            "paradas": [{"orden": t["orden"], "pedido": {"id": x["id"], "folio": x["folio"]}, "zona": {"id": x["zona_id"], "nombre": x["zona"]},
                         "latitud": x["lat"], "longitud": x["lng"], "tramo_km": t["tramo_km"], "minutos_acum": t["minutos_acum"]}
                        for x, t in zip(ordenadas, m["tramos"])],
            "distancia_km": m["distancia_km"], "minutos": m["minutos"], "costo": m["costo"]}


def armar_plan(origen, pedidos, repartidores, metodo, p):
    """Reparte con las funciones del portal y reordena cada ruta con el método pedido."""
    asignacion = pc.asignar_repartidores(pedidos, repartidores, origen, {**p})
    rutas = []
    for r in asignacion["rutas"]:
        rep = next(x for x in repartidores if x["id"] == r["repartidor_id"])
        rutas.append(ruta_de(origen, rep, r["paradas"], "automatico" if metodo == "automatico" else metodo, p, r["zonas"]))
    return rutas, [{"id": x["id"], "folio": x["folio"], "zona": {"id": x["zona_id"], "nombre": x["zona"]}} for x in asignacion["sin_asignar"]]


def totales(rutas):
    return {"rutas": len(rutas), "paradas": sum(len(r["paradas"]) for r in rutas), "distancia_km": round(sum(r["distancia_km"] for r in rutas), 2),
            "minutos_maximo": max((r["minutos"] for r in rutas), default=0.0), "costo": round(sum(r["costo"] for r in rutas), 2)}


def comparar_metodos(origen, paradas, p):
    """Las mismas paradas, una sola ruta, con cada método. La mejora se mide contra el orden de llegada."""
    filas = []
    for clave in ("orden_llegada", "vecino", "2opt", "exacto"):
        if clave == "exacto" and len(paradas) > MAX_EXACTO:
            continue
        orden, nombre = ordenar(origen, paradas, clave)
        m = metricas(origen, [paradas[i] for i in orden], list(range(len(paradas))), p)
        filas.append({"metodo": nombre, "distancia_km": m["distancia_km"], "minutos": m["minutos"], "costo": m["costo"]})
    base = filas[0]["distancia_km"]
    for f in filas:
        f["mejora_pct"] = round(100 * (base - f["distancia_km"]) / base, 1) if base else 0.0
    return filas


def ajustar_ruta(origen, ruta, pedidos_ruta, metodo_clave, p):
    rep = {"id": ruta["repartidor"]["id"], "nombre": ruta["repartidor"]["nombre"]}
    return ruta_de(origen, rep, pedidos_ruta, metodo_clave, p)


def pedidos_de_ruta(ruta):
    return [{"id": x["pedido"]["id"], "folio": x["pedido"]["folio"], "zona_id": x["zona"]["id"], "zona": x["zona"]["nombre"], "lat": x["latitud"],
             "lng": x["longitud"]} for x in ruta["paradas"]]


# --------------------------------------------------------------------
# Datos de otros servicios
# --------------------------------------------------------------------
def parametros():
    return sup.valores(DEFECTOS)


def hoy():
    return dt.datetime.now(ZONA).date()


def traer_todo(servicio, ruta, params=None):
    datos, pagina = [], 1
    while pagina <= 10:
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
    h = hubs[mid]
    return {"id": mid, "nombre": h["nombre"], "lat": float(h["latitud"]), "lng": float(h["longitud"])}


def listos(mid, ids=None):
    filas = traer_todo("pedidos", "pedidos/listos", {"microhub_id": mid})
    pedidos = [{"id": f["id"], "folio": f["folio"], "zona_id": f["zona"]["id"], "zona": f["zona"]["nombre"], "lat": f["latitud"], "lng": f["longitud"]} for f in filas]
    if ids:
        faltan = sorted(set(ids) - {x["id"] for x in pedidos})
        if faltan:
            raise ErrorApi(422, "VALIDACION", "Algunos pedidos no están listos para despachar en ese microhub.",
                           [{"campo": "pedido_ids", "mensaje": f"El pedido {i} no está listo o no es de ese microhub."} for i in faltan])
        pedidos = [x for x in pedidos if x["id"] in set(ids)]
    return pedidos


def repartidores_de(ids=None):
    filas = traer_todo("entregas", "entregas/repartidores")
    reps = [{"id": f["id"], "nombre": f["nombre"]} for f in filas]
    if ids:
        faltan = sorted(set(ids) - {r["id"] for r in reps})
        if faltan:
            raise ErrorApi(422, "VALIDACION", "Algunos repartidores no existen o no están activos.",
                           [{"campo": "repartidor_ids", "mensaje": f"El repartidor {i} no existe o no está activo."} for i in faltan])
        reps = [r for r in reps if r["id"] in set(ids)]
    return reps


def usados(p, modificados=()):
    return sup.usados({k: p[k] for k in ("velocidad_reparto_kmh", "tiempo_servicio_min", "costo_km_reparto", "costo_base_entrega", "max_paradas_repartidor",
                                          "factor_rodeo_distancia")}, modificados)


ITEMS = {"rutas": "ruta", "paradas": "parada", "zonas": "nombre_zona", "sin_asignar": "pedido", "supuestos_usados": "supuesto", "filas": "fila",
         "cambios": "cambio", "paradas_fuera_de_promesa": "folio"}


def plan_salida(pid, estado, version, mh, dia, metodo_pedido, rutas, sin_asignar, p, cambios=None, extra=None):
    return {"id": pid, "estado": estado, "version": version, "microhub": {"id": mh["id"], "nombre": mh["nombre"]}, "fecha": dia, "metodo_pedido": metodo_pedido,
            "rutas": rutas, "sin_asignar": sin_asignar, "total": totales(rutas), "cambios": cambios or [], "supuestos_usados": usados(p), **(extra or {})}


# --------------------------------------------------------------------
# Planes
# --------------------------------------------------------------------
@app.post(f"{P}/rutas/planes")
@requiere("rutas.planear")
def proponer():
    d = validar(leer_cuerpo("ruta_plan_nuevo"), [
        Campo("microhub_id", "int", minimo=1), Campo("pedido_ids", "lista", req=False, nulo=True), Campo("repartidor_ids", "lista", req=False, nulo=True),
        Campo("metodo", req=False, opciones=METODOS), Campo("guardar", "bool", req=False)])
    mid = limitar_microhub(d["microhub_id"])
    ids = _enteros(d.get("pedido_ids"), "pedido_ids")
    rep_ids = _enteros(d.get("repartidor_ids"), "repartidor_ids")
    p = parametros()
    mh = microhub(mid)
    pedidos = listos(mid, ids)
    if not pedidos:
        raise ErrorApi(422, "VALIDACION", "No hay pedidos listos para despachar en ese microhub.")
    reps = repartidores_de(rep_ids)
    if not reps:
        raise ErrorApi(422, "VALIDACION", "No hay repartidores activos.")
    metodo = d.get("metodo") or "automatico"
    rutas, sin = armar_plan((mh["lat"], mh["lng"]), pedidos, reps, metodo, p)
    dia = hoy().isoformat()
    pid = None
    if d.get("guardar"):
        salida = plan_salida(None, "propuesto", 1, mh, dia, metodo, rutas, sin, p)
        with conexion() as con, con.cursor() as cur:
            cur.execute("INSERT INTO plan_despacho (microhub_id, fecha, parametros, resultado, creado_por) VALUES (%s,%s,%s,%s,%s) RETURNING id",
                        (mid, dia, como_json({"microhub_id": mid, "pedido_ids": [x["id"] for x in pedidos], "repartidor_ids": [r["id"] for r in reps], "metodo": metodo}),
                         como_json(salida), g.usuario["id"]))
            pid = cur.fetchone()["id"]
    return responder(plan_salida(pid, "propuesto" if pid else "calculo", 1, mh, dia, metodo, rutas, sin, p), 201 if pid else 200, raiz="ruta_plan", items=ITEMS)


def _enteros(valor, campo):
    if valor in (None, ""):
        return None
    if isinstance(valor, dict) and len(valor) == 1:                 # XML: <pedido_ids><id>1</id><id>2</id></pedido_ids>
        valor = next(iter(valor.values()))
    if not isinstance(valor, list):
        valor = [valor]
    salida = []
    for i, v in enumerate(valor):
        try:
            n = int(v)
        except (TypeError, ValueError):
            raise invalido(f"{campo}[{i}]", "Debe ser un entero.")
        if n < 1:
            raise invalido(f"{campo}[{i}]", "Debe ser mayor que cero.")
        salida.append(n)
    if len(salida) > 100 or len(set(salida)) != len(salida):
        raise invalido(campo, "Hasta 100 valores, sin repetir.")
    return salida


def _plan(pid):
    f = consultar("SELECT id, microhub_id, fecha, estado, version, parametros, resultado FROM plan_despacho WHERE id = %s", (pid,), una=True)
    if not f:
        raise no_encontrado("No existe ese plan.")
    limitar_microhub(f["microhub_id"])
    return f


def _del_plan(f):
    return {**f["resultado"], "id": f["id"], "estado": f["estado"], "version": f["version"]}


@app.get(f"{P}/rutas/planes")
@requiere("rutas.ver")
def planes():
    pagina, por, desde = leer_paginacion()
    hub = limitar_microhub(filtro_entero("microhub_id"))
    estado = filtro_opcion("estado", ["propuesto", "confirmado", "cancelado"])
    where, args = ["TRUE"], []
    for cond, valor in (("microhub_id = %s", hub), ("estado = %s", estado)):
        if valor:
            where.append(cond); args.append(valor)
    w = " AND ".join(where)
    total = consultar(f"SELECT count(*) AS n FROM plan_despacho WHERE {w}", args, una=True)["n"]
    filas = consultar(f"SELECT id, microhub_id, fecha, estado, version, resultado, creado_por, creado_en FROM plan_despacho WHERE {w} "
                      f"ORDER BY id DESC LIMIT %s OFFSET %s", (*args, por, desde))
    return lista(filas, paginacion(pagina, por, total), "plan", "ruta_planes",
                 lambda f: {"id": f["id"], "estado": f["estado"], "version": f["version"], "microhub": f["resultado"]["microhub"], "fecha": f["fecha"].isoformat(),
                            "rutas": f["resultado"]["total"]["rutas"], "paradas": f["resultado"]["total"]["paradas"],
                            "distancia_km": f["resultado"]["total"]["distancia_km"], "costo": f["resultado"]["total"]["costo"],
                            "creado_por": f["creado_por"], "creado_en": fecha(f["creado_en"])})


@app.get(f"{P}/rutas/planes/<int:pid>")
@requiere("rutas.ver")
def plan_uno(pid):
    return responder(_del_plan(_plan(pid)), raiz="ruta_plan", items=ITEMS)


def _guardar_rutas(cur, f, plan):
    """Escribe las rutas del plan en plan_ruta / plan_ruta_parada (las mismas tablas que usa el portal)."""
    cur.execute("DELETE FROM plan_ruta WHERE plan_despacho_id = %s", (f["id"],))
    for r in plan["rutas"]:
        cur.execute("INSERT INTO plan_ruta (microhub_id, repartidor_id, fecha, metodo, paradas, distancia_km, minutos, costo_estimado, creado_por, plan_despacho_id) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                    (f["microhub_id"], r["repartidor"]["id"], f["fecha"], r["metodo"], len(r["paradas"]), r["distancia_km"], r["minutos"], r["costo"],
                     g.usuario["id"], f["id"]))
        rid = cur.fetchone()["id"]
        for x in r["paradas"]:
            cur.execute("INSERT INTO plan_ruta_parada (plan_ruta_id, orden, pedido_id, tramo_km, minutos_acum) VALUES (%s,%s,%s,%s,%s)",
                        (rid, x["orden"], x["pedido"]["id"], x["tramo_km"], x["minutos_acum"]))


@app.post(f"{P}/rutas/planes/<int:pid>/confirmar")
@requiere("rutas.planear")
def confirmar(pid):
    f = _plan(pid)
    if f["estado"] != "propuesto":
        raise conflicto(f"Solo se confirma un plan propuesto; este está {f['estado']}.")
    ids = [x["pedido"]["id"] for r in f["resultado"]["rutas"] for x in r["paradas"]]
    vigentes = {x["id"] for x in listos(f["microhub_id"])}
    ya_no = sorted(set(ids) - vigentes)
    if ya_no:
        raise ErrorApi(409, "CONFLICTO", "Algunos pedidos del plan ya no están listos para despachar; calcula el plan de nuevo.",
                       [{"campo": "pedido_ids", "mensaje": f"El pedido {i} ya no está listo."} for i in ya_no])
    with conexion() as con, con.cursor() as cur:
        cur.execute("SELECT estado FROM plan_despacho WHERE id = %s FOR UPDATE", (pid,))
        if cur.fetchone()["estado"] != "propuesto":
            raise conflicto("El plan ya se confirmó o se canceló.")
        cur.execute("UPDATE plan_despacho SET estado = 'confirmado', confirmado_por = %s, confirmado_en = now() WHERE id = %s", (g.usuario["id"], pid))
        _guardar_rutas(cur, f, f["resultado"])
    return responder(_del_plan(_plan(pid)), raiz="ruta_plan", items=ITEMS)


@app.post(f"{P}/rutas/planes/<int:pid>/cancelar")
@requiere("rutas.planear")
def cancelar(pid):
    f = _plan(pid)
    if f["estado"] != "propuesto":
        raise conflicto(f"Solo se cancela un plan propuesto; este está {f['estado']}.")
    with conexion() as con, con.cursor() as cur:
        cur.execute("UPDATE plan_despacho SET estado = 'cancelado' WHERE id = %s AND estado = 'propuesto'", (pid,))
    return responder(_del_plan(_plan(pid)), raiz="ruta_plan", items=ITEMS)


# --------------------------------------------------------------------
# Comparar métodos y ajustar ante incidencias
# --------------------------------------------------------------------
@app.post(f"{P}/rutas/comparaciones")
@requiere("rutas.ver")
def comparar():
    d = validar(leer_cuerpo("ruta_comparacion_nueva"), [Campo("microhub_id", "int", minimo=1), Campo("pedido_ids", "lista", req=False, nulo=True)])
    mid = limitar_microhub(d["microhub_id"])
    p = parametros()
    mh = microhub(mid)
    pedidos = listos(mid, _enteros(d.get("pedido_ids"), "pedido_ids"))
    if len(pedidos) < 2:
        raise ErrorApi(422, "VALIDACION", "Hacen falta al menos dos pedidos listos para comparar recorridos.")
    filas = comparar_metodos((mh["lat"], mh["lng"]), pedidos, p)
    mejor = min(filas, key=lambda f: f["distancia_km"])
    return responder({"microhub": {"id": mh["id"], "nombre": mh["nombre"]}, "paradas": len(pedidos), "filas": filas, "mejor_metodo": mejor["metodo"],
                      "nota": ("El método exacto se omite con más de 9 paradas." if len(pedidos) > MAX_EXACTO else "Una sola ruta con todas las paradas."),
                      "supuestos_usados": usados(p)}, raiz="ruta_comparacion", items=ITEMS)


@app.post(f"{P}/rutas/planes/<int:pid>/ajustes")
@requiere("rutas.planear")
def ajustar(pid):
    d = validar(leer_cuerpo("ruta_ajuste_nuevo"), [
        Campo("tipo", opciones=["quitar_pedido", "agregar_pedido", "retraso"]), Campo("pedido_id", "int", req=False, nulo=True, minimo=1),
        Campo("repartidor_id", "int", req=False, nulo=True, minimo=1), Campo("minutos", "num", req=False, nulo=True, minimo=1, maximo=600)])
    f = _plan(pid)
    if f["estado"] == "cancelado":
        raise conflicto("Un plan cancelado no se ajusta.")
    plan = f["resultado"]
    p = parametros()
    mh = microhub(f["microhub_id"])
    origen = (mh["lat"], mh["lng"])
    tipo, cambios, extra = d["tipo"], [], {}
    rutas = plan["rutas"]
    metodo = (f["parametros"] or {}).get("metodo", "automatico")

    def ruta_de_pedido(pedido_id):
        return next((r for r in rutas if any(x["pedido"]["id"] == pedido_id for x in r["paradas"])), None)

    if tipo == "quitar_pedido":
        if not d.get("pedido_id"):
            raise invalido("pedido_id", "Indica el pedido que se quita.")
        r = ruta_de_pedido(d["pedido_id"])
        if not r:
            raise no_encontrado("Ese pedido no está en ninguna ruta del plan.")
        restantes = [x for x in pedidos_de_ruta(r) if x["id"] != d["pedido_id"]]
        folio = next(x["pedido"]["folio"] for x in r["paradas"] if x["pedido"]["id"] == d["pedido_id"])
        if restantes:
            rutas[rutas.index(r)] = ajustar_ruta(origen, r, restantes, metodo, p)
        else:
            rutas.remove(r)
        cambios.append(f"Se quitó el pedido {folio}; la ruta de {r['repartidor']['nombre']} se recalculó con {len(restantes)} paradas.")
    elif tipo == "agregar_pedido":
        if not d.get("pedido_id"):
            raise invalido("pedido_id", "Indica el pedido que se agrega.")
        if ruta_de_pedido(d["pedido_id"]):
            raise conflicto("Ese pedido ya está en una ruta del plan.")
        nuevo = next((x for x in listos(f["microhub_id"]) if x["id"] == d["pedido_id"]), None)
        if not nuevo:
            raise ErrorApi(422, "VALIDACION", "Ese pedido no está listo para despachar en este microhub.")
        tope = int(p["max_paradas_repartidor"])
        if d.get("repartidor_id"):
            r = next((r for r in rutas if r["repartidor"]["id"] == d["repartidor_id"]), None)
            if not r:
                raise no_encontrado("Ese repartidor no tiene ruta en el plan.")
        else:
            r = min(rutas, key=lambda r: len(r["paradas"]), default=None)
        if not r or len(r["paradas"]) >= tope:
            raise conflicto(f"La ruta no admite más de {tope} paradas; elige otro repartidor.")
        lista_nueva = pedidos_de_ruta(r) + [nuevo]
        rutas[rutas.index(r)] = ajustar_ruta(origen, r, lista_nueva, metodo, p)
        cambios.append(f"Se agregó el pedido {nuevo['folio']} a la ruta de {r['repartidor']['nombre']}; ahora tiene {len(lista_nueva)} paradas.")
    else:
        if not d.get("repartidor_id") or not d.get("minutos"):
            raise invalido("repartidor_id", "Un retraso necesita repartidor_id y minutos.")
        r = next((r for r in rutas if r["repartidor"]["id"] == d["repartidor_id"]), None)
        if not r:
            raise no_encontrado("Ese repartidor no tiene ruta en el plan.")
        for x in r["paradas"]:
            x["minutos_acum"] = round(x["minutos_acum"] + d["minutos"], 1)
        r["minutos"] = round(r["minutos"] + d["minutos"], 1)
        fuera = [x["pedido"]["folio"] for x in r["paradas"] if x["minutos_acum"] > p["cob_tiempo_max_min"]]
        extra = {"paradas_fuera_de_promesa": fuera}
        cambios.append(f"Retraso de {d['minutos']:g} minutos en la ruta de {r['repartidor']['nombre']}: {len(fuera)} de {len(r['paradas'])} paradas "
                       f"quedan fuera de la promesa de {p['cob_tiempo_max_min']:g} minutos.")
    plan_nuevo = plan_salida(f["id"], f["estado"], f["version"] + 1, mh, plan["fecha"], plan.get("metodo_pedido", metodo), rutas, plan["sin_asignar"], p, cambios, extra)
    with conexion() as con, con.cursor() as cur:
        cur.execute("UPDATE plan_despacho SET resultado = %s, version = version + 1 WHERE id = %s", (como_json(plan_nuevo), pid))
        if f["estado"] == "confirmado":
            _guardar_rutas(cur, f, plan_nuevo)
    plan_nuevo["version"] = f["version"] + 1
    if "paradas_fuera_de_promesa" not in plan_nuevo:
        plan_nuevo["paradas_fuera_de_promesa"] = []
    return responder(plan_nuevo, raiz="ruta_plan", items=ITEMS)


@app.get(f"{P}/rutas/supuestos")
@requiere("rutas.ver")
def supuestos_rutas():
    return responder({"datos": sup.listar(CLAVES_SUPUESTOS)}, raiz="supuestos_rutas", items={"datos": "supuesto"})


# --------------------------------------------------------------------
# Documentación
# --------------------------------------------------------------------
PAG = [("pagina", "query", "integer", "Página (1…)"), ("por_pagina", "query", "integer", "1 a 100")]
ID = [("id", "path", "integer", "Id del plan")]
documentar(app, "POST", f"{P}/rutas/planes", "Proponer rutas", permisos=["rutas.planear"], cuerpo="RutaPlanNuevo.ok",
           descripcion="Toma los pedidos listos del microhub (o los indicados) y los repartidores activos (o los indicados), agrupa por zona, reparte y ordena las paradas. "
                       "Con guardar=true deja el plan como «propuesto» y responde 201; si no, solo calcula. Operador y supervisor solo planean su microhub.",
           respuestas={200: ("Plan calculado", "RutaPlan.ok")}, errores=[400, 403, 404, 422, 503])
documentar(app, "GET", f"{P}/rutas/planes", "Planes guardados", permisos=["rutas.ver"],
           parametros=PAG + [("microhub_id", "query", "integer", "Microhub"), ("estado", "query", "string", "propuesto | confirmado | cancelado")],
           respuestas={200: ("Página de planes", "RutaPlanLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/rutas/planes/{{id}}", "Un plan", permisos=["rutas.ver"], parametros=ID,
           respuestas={200: ("Plan con sus rutas y paradas", "RutaPlan.ok")}, errores=[403, 404])
documentar(app, "POST", f"{P}/rutas/planes/{{id}}/confirmar", "Confirmar un plan", permisos=["rutas.planear"], parametros=ID,
           descripcion="Comprueba que los pedidos sigan listos, deja las rutas en plan_ruta y plan_ruta_parada y marca el plan como confirmado.",
           respuestas={200: ("Plan confirmado", "RutaPlan.ok")}, errores=[403, 404, 409, 503])
documentar(app, "POST", f"{P}/rutas/planes/{{id}}/cancelar", "Cancelar un plan propuesto", permisos=["rutas.planear"], parametros=ID,
           respuestas={200: ("Plan cancelado", "RutaPlan.ok")}, errores=[403, 404, 409])
documentar(app, "POST", f"{P}/rutas/planes/{{id}}/ajustes", "Ajustar un plan ante una incidencia", permisos=["rutas.planear"], parametros=ID, cuerpo="RutaAjusteNuevo.ok",
           descripcion="quitar_pedido y agregar_pedido recalculan la ruta afectada con el mismo método; retraso suma minutos a una ruta y dice qué paradas quedan fuera de la promesa. "
                       "En un plan confirmado también se reescriben plan_ruta y plan_ruta_parada.",
           respuestas={200: ("Plan ajustado, con la lista de cambios", "RutaPlan.ok")}, errores=[400, 403, 404, 409, 422, 503])
documentar(app, "POST", f"{P}/rutas/comparaciones", "Comparar métodos de recorrido", permisos=["rutas.ver"], cuerpo="RutaComparacionNueva.ok",
           descripcion="Las mismas paradas en una sola ruta con orden de llegada, vecino más cercano, 2-opt y exacto (hasta 9 paradas). La mejora se mide contra el orden de llegada.",
           respuestas={200: ("Un renglón por método", "RutaComparacion.ok")}, errores=[400, 403, 404, 422, 503])
documentar(app, "GET", f"{P}/rutas/supuestos", "Supuestos del modelo de rutas", permisos=["rutas.ver"],
           descripcion="Valor, origen (medido, supuesto o normativo), justificación y cómo calibrarlo con datos reales.",
           respuestas={200: ("Supuestos documentados", "SupuestosRutas.ok")}, errores=[403])
