"""
planeacion_calc.py — Cálculos de planeación y viabilidad (sin Flask ni base de datos)
Plataforma de Microhubs · Codex Innovations · Equipo 04

Todas las funciones son puras: reciben números y devuelven números o
estructuras. Los parámetros (pesos, umbrales, productividades) llegan desde
la tabla configuracion; aquí solo hay valores por omisión para las pruebas.
"""
import itertools
import math

# Valores por omisión: espejo de 06_planeacion.sql. En producción se leen de
# configuracion (RN40); estos existen para las pruebas y para que el módulo
# no falle si una clave se borra.
PARAMS = {
    "peso_score_demanda": 1.0, "peso_score_renta": 1.2,
    "peso_score_distancia": 4.0, "peso_score_accesibilidad": 3.0,
    "picking_pedidos_hora": 10.0, "packing_pedidos_hora": 20.0,
    "despacho_pedidos_hora": 30.0,
    "umbral_utilizacion_estable": 70.0, "umbral_utilizacion_riesgo": 85.0,
    "velocidad_reparto_kmh": 22.0, "tiempo_servicio_min": 4.0,
    "paradas_por_viaje": 3.0, "max_paradas_repartidor": 8.0,
    "costo_km_reparto": 4.5, "costo_base_entrega": 18.0, "tamano_hogar": 3.6, "dias_operacion_mes": 30.0,
    "horas_turno": 10.0, "margen_bruto_default": 0.28,
    "abc_a_pct": 80.0, "abc_b_pct": 95.0,
    "cobertura_dias_a": 7.0, "cobertura_dias_b": 5.0, "cobertura_dias_c": 3.0,
    "cobertura_dias_exceso": 30.0, "ventana_analisis_dias": 90.0,
}


def con_defecto(parametros=None):
    p = dict(PARAMS)
    p.update({k: float(v) for k, v in (parametros or {}).items() if k in PARAMS})
    return p


def _f(v, d=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


# ====================================================================
# Distancia
# ====================================================================
def haversine_km(lat1, lon1, lat2, lon2):
    """Distancia sobre la esfera terrestre entre dos coordenadas (km)."""
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


# ====================================================================
# 2. Ubicación: score
# ====================================================================
def score_ubicacion(demanda_cubierta, renta_mensual, distancia_promedio_km,
                    accesibilidad, params=None):
    """score = demanda × p1 − renta(miles) × p2 − distancia × p3 + accesibilidad × p4"""
    p = con_defecto(params)
    t = {
        "demanda": demanda_cubierta * p["peso_score_demanda"],
        "renta": (renta_mensual / 1000.0) * p["peso_score_renta"],
        "distancia": distancia_promedio_km * p["peso_score_distancia"],
        "accesibilidad": accesibilidad * p["peso_score_accesibilidad"],
    }
    total = t["demanda"] - t["renta"] - t["distancia"] + t["accesibilidad"]
    return {"score": round(total, 2), "terminos": {k: round(v, 2) for k, v in t.items()}}


# ====================================================================
# Cobertura
# ====================================================================
def cobertura_candidato(cand, zonas, hubs, params=None):
    """Cobertura de un candidato (o microhub) con radio + población + demanda.

    cand : dict latitud, longitud, radio_km, poblacion_cubierta
    zonas: lista de dict {id, nombre, lat, lng, demanda_dia, poblacion}
           (demanda_dia incluye lo atendido más la demanda no atendida)
    hubs : microhubs existentes [{clave, lat, lng, radio_km}]
    """
    p = con_defecto(params)
    radio = _f(cand["radio_km"], 1.5)
    dentro, fuera = [], []
    for z in zonas:
        d = haversine_km(_f(cand["latitud"]), _f(cand["longitud"]), z["lat"], z["lng"])
        (dentro if d <= radio else fuera).append({**z, "dist_km": round(d, 2)})
    demanda_cub = sum(z["demanda_dia"] for z in dentro)
    demanda_fuera = sum(z["demanda_dia"] for z in fuera)
    dist_prom = (sum(z["dist_km"] * z["demanda_dia"] for z in dentro) / demanda_cub
                 if demanda_cub else (sum(z["dist_km"] for z in dentro) / len(dentro) if dentro else 0.0))
    pob = _f(cand.get("poblacion_cubierta"))
    hogares = round(pob / p["tamano_hogar"]) if p["tamano_hogar"] else 0
    solap = []
    ids_dentro = {z["id"] for z in dentro}
    for h in hubs:
        cubre = {z["id"] for z in zonas
                 if haversine_km(h["lat"], h["lng"], z["lat"], z["lng"]) <= _f(h["radio_km"], 1.5)}
        comun = ids_dentro & cubre
        dem = sum(z["demanda_dia"] for z in dentro if z["id"] in comun)
        solap.append({"clave": h["clave"], "zonas": len(comun), "demanda_dia": round(dem, 1),
                      "pct": round(100 * dem / demanda_cub, 1) if demanda_cub else 0.0})
    return {
        "zonas_dentro": dentro, "zonas_fuera": fuera,
        "demanda_cubierta": round(demanda_cub, 1),
        "demanda_fuera": round(demanda_fuera, 1),
        "distancia_promedio": round(dist_prom, 2),
        "poblacion": int(pob), "hogares": hogares,
        "tiempo_estimado_min": round(dist_prom / p["velocidad_reparto_kmh"] * 60 + p["tiempo_servicio_min"], 1),
        "costo_ultima_milla": round(p["costo_base_entrega"]
                                    + 2 * dist_prom * p["costo_km_reparto"] / max(p["paradas_por_viaje"], 1), 2),
        "solapamiento": solap,
    }


# ====================================================================
# 4. Capacidad
# ====================================================================
def capacidad(operadores, repartidores, distancia_km, capacidad_fisica=None, horas=None, params=None):
    """Capacidad por etapa, cuello de botella y pedidos/día.

    Cada operador realiza picking, packing y despacho en secuencia, de modo
    que su tasa combinada es 1 / (1/pick + 1/pack + 1/desp). La capacidad
    de cada etapa se muestra como si todos los operadores estuvieran
    dedicados a ella. El reparto depende de repartidores, distancia y
    paradas por viaje.
    """
    p = con_defecto(params)
    horas = _f(horas, p["horas_turno"])
    pick, pack, desp = (p["picking_pedidos_hora"], p["packing_pedidos_hora"],
                        p["despacho_pedidos_hora"])
    min_pedido = 60 / pick + 60 / pack + 60 / desp
    combinada = 60 / min_pedido
    cap_op_h = operadores * combinada
    min_entrega = ((2 * distancia_km / p["velocidad_reparto_kmh"] * 60) / max(p["paradas_por_viaje"], 1)
                   + p["tiempo_servicio_min"])
    cap_rep_h = repartidores * 60 / min_entrega if min_entrega > 0 else 0.0
    etapas = {
        "picking": operadores * pick, "packing": operadores * pack,
        "despacho": operadores * desp, "operación (combinada)": cap_op_h,
        "reparto": cap_rep_h,
    }
    limitantes = {"operacion": cap_op_h, "reparto": cap_rep_h}
    cuello = min(limitantes, key=limitantes.get)
    cap_hora = limitantes[cuello]
    cap_dia = cap_hora * horas
    if capacidad_fisica:
        if capacidad_fisica < cap_dia:
            cuello = "espacio físico"
        cap_dia = min(cap_dia, capacidad_fisica)
    return {
        "por_etapa_hora": {k: round(v, 1) for k, v in etapas.items()},
        "minutos_por_pedido_operacion": round(min_pedido, 1),
        "minutos_por_entrega": round(min_entrega, 1),
        "capacidad_hora": round(cap_hora, 2), "capacidad_dia": round(cap_dia, 1),
        "cuello_botella": cuello, "horas": horas,
        "formula": (f"{operadores:g} operadores × {combinada:.2f} pedidos/h combinados; "
                    f"{repartidores:g} repartidores × {60 / min_entrega:.2f} entregas/h"
                    if min_entrega > 0 else ""),
    }


def nivel_utilizacion(pct, params=None):
    p = con_defecto(params)
    if pct < p["umbral_utilizacion_estable"]:
        return "estable"
    if pct <= p["umbral_utilizacion_riesgo"]:
        return "atencion"
    return "riesgo"


# ====================================================================
# 7. Punto de equilibrio
# ====================================================================
def punto_equilibrio(costos_fijos_mes, ticket, margen_bruto, costo_entrega, dias_mes=30):
    """Punto de equilibrio con el detalle del cálculo (el sistema muestra la cuenta)."""
    margen_ped = ticket * margen_bruto - costo_entrega
    pasos = [
        f"Margen por pedido = ticket × margen bruto − costo de entrega = "
        f"{ticket:,.2f} × {margen_bruto:.2%} − {costo_entrega:,.2f} = {margen_ped:,.2f}",
    ]
    if margen_ped <= 0:
        pasos.append("El margen por pedido no es positivo: ningún volumen recupera los costos fijos.")
        return {"margen_pedido": round(margen_ped, 2), "mensual": None, "diario": None,
                "costos_fijos": costos_fijos_mes, "pasos": pasos}
    mensual = costos_fijos_mes / margen_ped
    diario = mensual / dias_mes
    pasos += [
        f"Punto de equilibrio mensual = costos fijos ÷ margen por pedido = "
        f"{costos_fijos_mes:,.2f} ÷ {margen_ped:,.2f} = {mensual:,.0f} pedidos/mes",
        f"Punto de equilibrio diario = {mensual:,.0f} ÷ {dias_mes:g} días = {diario:,.1f} pedidos/día",
    ]
    return {"margen_pedido": round(margen_ped, 2), "mensual": round(mensual, 1),
            "diario": round(diario, 1), "costos_fijos": costos_fijos_mes, "pasos": pasos}


# ====================================================================
# 3. Simulación de operación + ficha de viabilidad
# ====================================================================
SUPUESTOS_BASE = {
    "demanda_diaria": 120, "operadores": 3, "repartidores": 4, "ticket": 135.0,
    "costo_entrega": 22.0, "margen_bruto": 0.28, "renta": 18000.0, "nomina": 42000.0,
    "servicios": 7000.0, "otros": 5000.0, "distancia_km": 2.4,
    "capacidad_fisica": None, "poblacion": 0, "horas": None,
}


def simular(s, params=None):
    """Ejecuta el escenario y devuelve resultados, equilibrio y ficha de viabilidad."""
    p = con_defecto(params)
    s = {**SUPUESTOS_BASE, **{k: v for k, v in s.items() if v is not None or k in ("capacidad_fisica", "horas")}}
    demanda = _f(s["demanda_diaria"])
    dias = p["dias_operacion_mes"]
    cap = capacidad(_f(s["operadores"]), _f(s["repartidores"]), _f(s["distancia_km"]),
                    _f(s["capacidad_fisica"]) or None, s.get("horas"), p)
    cap_dia = cap["capacidad_dia"]
    atendidos = min(demanda, cap_dia)
    rechazados = max(demanda - cap_dia, 0)
    util = 100 * demanda / cap_dia if cap_dia else 999.0
    costos_fijos = _f(s["renta"]) + _f(s["nomina"]) + _f(s["servicios"]) + _f(s["otros"])
    costo_fijo_dia = costos_fijos / dias
    ingreso = atendidos * _f(s["ticket"])
    margen_bruto_total = ingreso * _f(s["margen_bruto"])
    costo_entregas = atendidos * _f(s["costo_entrega"])
    utilidad = margen_bruto_total - costo_entregas - costo_fijo_dia
    costo_pedido = (costo_fijo_dia / atendidos + _f(s["costo_entrega"])) if atendidos else None
    eq = punto_equilibrio(costos_fijos, _f(s["ticket"]), _f(s["margen_bruto"]),
                          _f(s["costo_entrega"]), dias)
    # Capacidad requerida para operar por debajo del umbral de riesgo.
    objetivo = p["umbral_utilizacion_riesgo"] / 100
    comb = 60 / cap["minutos_por_pedido_operacion"]
    horas = cap["horas"]
    ops_req = math.ceil(demanda / (comb * horas * objetivo)) if comb * horas else 0
    reps_req = (math.ceil(demanda / (60 / cap["minutos_por_entrega"] * horas * objetivo))
                if cap["minutos_por_entrega"] and horas else 0)
    tiempo = cap["minutos_por_pedido_operacion"] + cap["minutos_por_entrega"]
    nivel = nivel_utilizacion(util, p)
    res = {
        "capacidad": cap, "atendidos": round(atendidos, 1), "rechazados": round(rechazados, 1),
        "utilizacion": round(util, 1), "nivel": nivel,
        "tiempo_estimado_min": round(tiempo, 1),
        "operadores_requeridos": ops_req, "repartidores_requeridos": reps_req,
        "ingreso_dia": round(ingreso, 2), "margen_dia": round(utilidad, 2),
        "margen_bruto_dia": round(margen_bruto_total, 2),
        "costo_fijo_dia": round(costo_fijo_dia, 2),
        "costo_por_pedido": round(costo_pedido, 2) if costo_pedido is not None else None,
        "costos_fijos_mes": round(costos_fijos, 2),
        "equilibrio": eq,
    }
    res["ficha"] = ficha_viabilidad(s, res, p)
    return res


def ficha_viabilidad(s, r, p):
    eq = r["equilibrio"]["diario"]
    demanda = _f(s["demanda_diaria"])
    cap_dia = r["capacidad"]["capacidad_dia"]
    exp, acciones = [], []
    if eq is None:
        decision = "NO VIABLE CON LOS SUPUESTOS ACTUALES"
        exp.append("el margen por pedido no es positivo: el costo de entrega absorbe la utilidad del ticket")
        acciones.append("subir el ticket, el margen bruto o reducir el costo de entrega")
        diferencia = None
    else:
        diferencia = round(r["atendidos"] - eq, 1)
        if r["atendidos"] < eq:
            decision = "NO VIABLE CON LOS SUPUESTOS ACTUALES"
            exp.append(f"la demanda atendida ({r['atendidos']:.0f}/día) no alcanza el equilibrio ({eq:.0f}/día)")
            acciones.append("reducir costos fijos, aumentar ticket o buscar una ubicación con más demanda")
            if r["rechazados"] > 0:
                exp.append(f"además se rechazan {r['rechazados']:.0f} pedidos/día por falta de capacidad")
                acciones.append(f"ampliar capacidad (operadores requeridos: {r['operadores_requeridos']})")
        else:
            exp.append(f"la demanda atendida supera el equilibrio en {diferencia:+.0f} pedidos/día")
            if r["nivel"] == "riesgo":
                decision = "VIABLE CON RIESGO DE CAPACIDAD"
                exp.append(f"la utilización es {r['utilizacion']:.0f}%, por encima de "
                           f"{p['umbral_utilizacion_riesgo']:.0f}%")
                acciones.append(f"agregar personal en horario pico (operadores sugeridos: "
                                f"{r['operadores_requeridos']}, repartidores: {r['repartidores_requeridos']})")
            else:
                decision = "VIABLE"
                exp.append(f"la utilización es {r['utilizacion']:.0f}% ({r['nivel']})")
    if r["capacidad"]["cuello_botella"] == "espacio físico" and r["utilizacion"] >= p["umbral_utilizacion_estable"]:
        exp.append("el espacio físico del local limita la capacidad")
    return {"decision": decision, "explicacion": exp, "acciones": acciones,
            "demanda": demanda, "capacidad": cap_dia, "equilibrio_diario": eq,
            "demanda_menos_equilibrio": diferencia,
            "poblacion": int(_f(s.get("poblacion"))), "ticket": _f(s["ticket"]),
            "costo_por_pedido": r["costo_por_pedido"], "utilizacion": r["utilizacion"]}


VARIABLES_SENSIBILIDAD = [
    ("ticket", "Ticket promedio"), ("demanda_diaria", "Pedidos/día"), ("renta", "Renta"),
    ("nomina", "Nómina"), ("costo_entrega", "Costo de entrega"),
    ("margen_bruto", "Margen bruto"), ("operadores", "Operadores"),
    ("repartidores", "Repartidores"),
]


def sensibilidad(s, variacion=(-0.2, -0.1, 0.1, 0.2), params=None):
    """Recalcula el escenario variando de una en una las 8 variables de decisión."""
    base = simular(s, params)
    filas = []
    s0 = {**SUPUESTOS_BASE, **s}
    for clave, etiqueta in VARIABLES_SENSIBILIDAD:
        for v in variacion:
            valor = _f(s0[clave]) * (1 + v)
            if clave in ("operadores", "repartidores"):
                valor = max(1, round(valor))
            r = simular({**s0, clave: valor}, params)
            filas.append({"variable": etiqueta, "clave": clave, "cambio": v, "valor": round(valor, 2),
                          "equilibrio_diario": r["equilibrio"]["diario"],
                          "utilizacion": r["utilizacion"], "costo_por_pedido": r["costo_por_pedido"],
                          "utilidad_dia": r["margen_dia"], "decision": r["ficha"]["decision"]})
    return {"base": base, "filas": filas}


# ====================================================================
# 5. Surtido: ABC + recomendación
# ====================================================================
def clasificar_abc(items, params=None):
    """items: [{id, unidades}] → mismo listado con clase y % acumulado."""
    p = con_defecto(params)
    orden = sorted(items, key=lambda x: (-_f(x["unidades"]), x.get("id", 0)))
    total = sum(_f(x["unidades"]) for x in orden)
    acum, out = 0.0, []
    for x in orden:
        previo = acum
        acum += _f(x["unidades"])
        pct = 100 * acum / total if total else 100.0
        pct_previo = 100 * previo / total if total else 100.0
        if _f(x["unidades"]) <= 0:
            clase = "C"
        elif pct_previo < p["abc_a_pct"]:
            clase = "A"
        elif pct_previo < p["abc_b_pct"]:
            clase = "B"
        else:
            clase = "C"
        out.append({**x, "clase": clase, "pct_acum": round(pct, 1)})
    return out


def recomendar_surtido(sku, dias_ventana, params=None):
    """sku: {unidades, existencia, minimo, quiebres, clase, margen_unit, espacio}."""
    p = con_defecto(params)
    unidades, exist = _f(sku["unidades"]), _f(sku["existencia"])
    minimo, quiebres = _f(sku.get("minimo")), _f(sku.get("quiebres"))
    dem_dia = unidades / dias_ventana if dias_ventana else 0.0
    cobertura = exist / dem_dia if dem_dia > 0 else None
    objetivo = p[f"cobertura_dias_{sku['clase'].lower()}"]
    rotacion = unidades / exist if exist > 0 else (None if unidades == 0 else float("inf"))
    sugerido = max(math.ceil(dem_dia * objetivo) - exist, 0)
    if unidades == 0 and quiebres == 0:
        rec, motivo, sugerido = "Eliminar", "sin movimiento en la ventana de análisis", 0
    elif sku["clase"] == "C" and _f(sku.get("margen_unit")) <= 0:
        rec, motivo, sugerido = "Eliminar", "baja rotación y margen no positivo", 0
    elif quiebres > 0 or exist <= minimo or (cobertura is not None and cobertura < objetivo / 2
                                            and sku["clase"] in ("A", "B")):
        rec = "Aumentar"
        motivo = ("hubo quiebres" if quiebres > 0 else
                  "existencia en o bajo el mínimo" if exist <= minimo else
                  f"cobertura de {cobertura:.1f} días, menor a la mitad del objetivo ({objetivo:g})")
    elif cobertura is not None and cobertura > p["cobertura_dias_exceso"] or (
            sku["clase"] == "C" and cobertura is not None and cobertura > objetivo * 3):
        rec, motivo, sugerido = "Reducir", f"cobertura de {cobertura:.0f} días, exceso de stock", 0
    else:
        rec, motivo, sugerido = "Mantener", "cobertura dentro del objetivo", 0
    return {"demanda_dia": round(dem_dia, 2), "cobertura_dias": None if cobertura is None else round(cobertura, 1),
            "rotacion": None if rotacion is None else (round(rotacion, 2) if rotacion != float("inf") else 99.0),
            "recomendacion": rec, "motivo": motivo, "sugerido": int(sugerido),
            "espacio": round(exist * _f(sku.get("espacio"), 1), 1)}


# ====================================================================
# 6. Entregas: agrupar, asignar, rutear
# ====================================================================
def distancia_ruta(origen, paradas, orden):
    """Suma de tramos origen → paradas[orden[0]] → … (km) y lista de tramos."""
    tramos, actual = [], origen
    for i in orden:
        d = haversine_km(actual[0], actual[1], paradas[i]["lat"], paradas[i]["lng"])
        tramos.append(d)
        actual = (paradas[i]["lat"], paradas[i]["lng"])
    return sum(tramos), tramos


def vecino_mas_cercano(origen, paradas):
    pendientes, orden, actual = list(range(len(paradas))), [], origen
    while pendientes:
        j = min(pendientes, key=lambda i: haversine_km(actual[0], actual[1], paradas[i]["lat"], paradas[i]["lng"]))
        orden.append(j)
        pendientes.remove(j)
        actual = (paradas[j]["lat"], paradas[j]["lng"])
    return orden


def dos_opt(origen, paradas, orden):
    mejor, mejor_d = list(orden), distancia_ruta(origen, paradas, orden)[0]
    mejora = True
    while mejora:
        mejora = False
        for i in range(len(mejor) - 1):
            for j in range(i + 1, len(mejor)):
                cand = mejor[:i] + mejor[i:j + 1][::-1] + mejor[j + 1:]
                d = distancia_ruta(origen, paradas, cand)[0]
                if d < mejor_d - 1e-9:
                    mejor, mejor_d, mejora = cand, d, True
    return mejor


def tsp_exacto(origen, paradas):
    mejor, mejor_d = None, float("inf")
    for perm in itertools.permutations(range(len(paradas))):
        d = distancia_ruta(origen, paradas, perm)[0]
        if d < mejor_d:
            mejor, mejor_d = list(perm), d
    return mejor or []


def planear_ruta(origen, paradas, params=None):
    """Orden de paradas, distancia y tiempo. TSP exacto hasta 8 paradas; si no,
    vecino más cercano mejorado con 2-opt."""
    p = con_defecto(params)
    if not paradas:
        return {"metodo": "sin paradas", "orden": [], "distancia_km": 0.0, "minutos": 0.0,
                "costo": 0.0, "tramos": []}
    if len(paradas) <= 8:
        orden, metodo = tsp_exacto(origen, paradas), "TSP exacto"
    else:
        orden, metodo = dos_opt(origen, paradas, vecino_mas_cercano(origen, paradas)), "Vecino más cercano + 2-opt"
    total, tramos = distancia_ruta(origen, paradas, orden)
    minutos, acum, detalle = 0.0, 0.0, []
    for k, (i, t) in enumerate(zip(orden, tramos), 1):
        acum += t / p["velocidad_reparto_kmh"] * 60 + p["tiempo_servicio_min"]
        detalle.append({"orden": k, "indice": i, "tramo_km": round(t, 2), "minutos_acum": round(acum, 1)})
    minutos = acum
    return {"metodo": metodo, "orden": orden, "distancia_km": round(total, 2),
            "minutos": round(minutos, 1),
            "costo": round(total * p["costo_km_reparto"] + p["costo_base_entrega"] * len(paradas), 2),
            "tramos": detalle}


def agrupar_por_zona(pedidos):
    grupos = {}
    for pe in pedidos:
        grupos.setdefault(pe["zona_id"], []).append(pe)
    return grupos


def asignar_repartidores(pedidos, repartidores, origen, params=None):
    """Agrupa por zona, reparte los grupos entre repartidores balanceando carga
    (tope de paradas por repartidor) y calcula la ruta de cada uno.

    pedidos: [{id, zona_id, zona, lat, lng}]  ·  repartidores: [{id, nombre}]
    """
    p = con_defecto(params)
    tope = int(p["max_paradas_repartidor"])
    if not repartidores:
        return {"rutas": [], "sin_asignar": list(pedidos)}
    trozos = []
    for zid, lista in agrupar_por_zona(pedidos).items():
        for i in range(0, len(lista), tope):
            trozos.append(lista[i:i + tope])
    trozos.sort(key=len, reverse=True)
    carga = {r["id"]: [] for r in repartidores}
    sin_asignar = []
    for t in trozos:
        # Repartidor con menos paradas al que aún le cabe el trozo completo;
        # si no cabe en ninguno, se parte entre los menos cargados.
        candidatos = sorted(carga, key=lambda r: len(carga[r]))
        elegido = next((r for r in candidatos if len(carga[r]) + len(t) <= tope), None)
        if elegido is not None:
            carga[elegido].extend(t)
        else:
            for pe in t:
                libre = next((r for r in sorted(carga, key=lambda r: len(carga[r]))
                              if len(carga[r]) < tope), None)
                (carga[libre].append(pe) if libre is not None else sin_asignar.append(pe))
    nombres = {r["id"]: r["nombre"] for r in repartidores}
    rutas = []
    for rid, lista in carga.items():
        if not lista:
            continue
        plan = planear_ruta(origen, lista, p)
        rutas.append({"repartidor_id": rid, "repartidor": nombres[rid], "plan": plan,
                      "paradas": [lista[i] for i in plan["orden"]],
                      "zonas": sorted({x["zona"] for x in lista})})
    return {"rutas": rutas, "sin_asignar": sin_asignar}
