"""
ubicacion_calc.py — Dónde poner los microhubs. Funciones puras (sin base de datos), las mismas en el servicio de ubicación y en el portal
(sistema_web/ubicacion_calc.py es una copia idéntica; test_unitarias_ubicacion lo comprueba).

Integra los tres algoritmos que pide el proyecto en un solo recorrido:

  1. Simulación de demanda (Monte Carlo):
       hogares de la colonia = población ÷ personas por hogar
       pedidos esperados al día = hogares × penetración × pedidos por hogar a la semana ÷ 7
       Cada día simulado, los pedidos de la colonia son Poisson con esa media, multiplicada por el índice del día de la semana.
  2. Facility location — problema de cobertura máxima (MCLP) con p microhubs:
       Puntos de demanda: SOLO las colonias de bajos ingresos (grado de marginación CONAPO 2020 Medio, Alto o Muy alto).
       Candidatos: el centro de cada colonia de la zona de estudio.
       Una colonia queda cubierta si su centro está a `radio_km` o menos del microhub (la regla RN05 del sistema).
       Algoritmo: voraz (se agrega el candidato que más demanda nueva cubre) y después intercambio de Teitz y Bart
       (se cambia un elegido por un no elegido mientras aumente la demanda cubierta o, empatada, baje la distancia ponderada).
       Cada colonia cubierta se asigna al microhub elegido más cercano (asignación de p-mediana).
  3. Punto de equilibrio (break-even) de cada microhub propuesto:
       margen por pedido = ticket × margen bruto − costo de entrega; equilibrio diario = costos fijos del mes ÷ margen ÷ días.
       Se compara con la demanda simulada del microhub (limitada por su capacidad diaria):
       VIABLE si la mediana simulada supera el equilibrio con el margen de seguridad mínimo; VIABLE AJUSTADO si solo lo supera;
       NO VIABLE si no lo alcanza. También se da la penetración mínima con la que llegaría al equilibrio.
"""
import math
import random

GRADOS_BAJOS_INGRESOS = ("Medio", "Alto", "Muy alto")

PARAMS = {
    "p": 3,                          # microhubs a proponer
    "radio_km": 1.5,                 # RN05: radio de cobertura
    "personas_por_hogar": 3.6,       # INEGI, Censo 2020 (promedio de Nuevo León)
    "penetracion": 0.08,             # hogares de la colonia que piden (supuesto, se calibra con pedidos reales)
    "pedidos_semana_hogar": 1.2,     # pedidos por hogar que pide, a la semana (supuesto)
    "indice_semanal": [0.9, 0.95, 0.95, 1.0, 1.1, 1.25, 0.85],   # lunes a domingo; promedio 1
    "dias_simulados": 90,
    "semilla": 2026,
    "capacidad_diaria": 160,         # pedidos al día que atiende un microhub (servicio de capacidad)
    "ticket": 135.0,
    "margen_bruto": 0.28,
    "costo_entrega": 22.0,
    "costo_variable_completo": 32.6,  # todos los costos por pedido (servicio de costos): reparto, empaque 3.50 y comisión de tarjeta 2.9 %
    "costos_fijos_mes": 72000.0,     # renta 18 000 + nómina 42 000 + servicios 7 000 + otros 5 000
    "dias_mes": 30,
    "margen_seguridad_min": 0.10,
}


def con_defecto(parametros=None):
    p = dict(PARAMS)
    for k, v in (parametros or {}).items():
        if v is not None and k in p:
            p[k] = v
    return p


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0088
    f1, f2 = math.radians(lat1), math.radians(lat2)
    df, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    h = math.sin(df / 2) ** 2 + math.cos(f1) * math.cos(f2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def es_bajos_ingresos(colonia):
    return colonia["grado"] in GRADOS_BAJOS_INGRESOS


def demanda_esperada(colonia, p):
    """Pedidos esperados al día de una colonia (media de la simulación)."""
    hogares = colonia["poblacion"] / p["personas_por_hogar"]
    return hogares * p["penetracion"] * p["pedidos_semana_hogar"] / 7.0


def _poisson(rnd, media):
    if media <= 0:
        return 0
    if media < 30:                                   # Knuth
        limite, k, prod = math.exp(-media), 0, rnd.random()
        while prod > limite:
            k += 1
            prod *= rnd.random()
        return k
    return max(0, int(round(rnd.gauss(media, math.sqrt(media)))))   # aproximación normal


def _cubre(cands, demanda, radio):
    """Para cada candidato, el conjunto de puntos de demanda que cubre."""
    return [{j for j, d in enumerate(demanda) if haversine_km(c["lat"], c["lng"], d["lat"], d["lng"]) <= radio} for c in cands]


def _valor(elegidos, cubre, cands, demanda):
    cubiertos = set().union(*(cubre[i] for i in elegidos)) if elegidos else set()
    peso = sum(demanda[j]["peso"] for j in cubiertos)
    dist = 0.0
    for j in cubiertos:
        dist += demanda[j]["peso"] * min(haversine_km(cands[i]["lat"], cands[i]["lng"], demanda[j]["lat"], demanda[j]["lng"])
                                         for i in elegidos if j in cubre[i])
    return peso, dist


def cobertura_maxima(cands, demanda, p_sitios, radio):
    """MCLP: voraz + intercambio (Teitz y Bart). Devuelve los índices elegidos y la historia del cálculo."""
    cubre = _cubre(cands, demanda, radio)
    elegidos, pasos = [], []
    for _ in range(min(p_sitios, len(cands))):
        base = set().union(*(cubre[i] for i in elegidos)) if elegidos else set()
        mejor = max((i for i in range(len(cands)) if i not in elegidos),
                    key=lambda i: (sum(demanda[j]["peso"] for j in cubre[i] - base), -i))
        elegidos.append(mejor)
        pasos.append(f"Voraz: se agrega «{cands[mejor]['nombre']}» (+{sum(demanda[j]['peso'] for j in cubre[mejor] - base):.1f} pedidos/día cubiertos).")
    peso, dist = _valor(elegidos, cubre, cands, demanda)
    mejoro = True
    while mejoro:
        mejoro = False
        for a in range(len(elegidos)):
            for b in range(len(cands)):
                if b in elegidos:
                    continue
                prueba = elegidos[:a] + [b] + elegidos[a + 1:]
                pp, dd = _valor(prueba, cubre, cands, demanda)
                if pp > peso + 1e-9 or (abs(pp - peso) <= 1e-9 and dd < dist - 1e-9):
                    pasos.append(f"Intercambio: «{cands[elegidos[a]]['nombre']}» → «{cands[b]['nombre']}» "
                                 f"(cubre {pp:.1f} pedidos/día, distancia ponderada {dd:.1f}).")
                    elegidos, peso, dist, mejoro = prueba, pp, dd, True
                    break
            if mejoro:
                break
    return elegidos, cubre, pasos


def simular_demanda(medias, p, semilla_extra=0):
    """Monte Carlo: pedidos diarios del microhub sumando las colonias que atiende. Devuelve la serie de días."""
    rnd = random.Random(p["semilla"] + semilla_extra)
    serie = []
    for d in range(p["dias_simulados"]):
        indice = p["indice_semanal"][d % 7]
        serie.append(sum(_poisson(rnd, m * indice) for m in medias))
    return serie


def _percentil(valores, q):
    v = sorted(valores)
    if not v:
        return 0
    k = (len(v) - 1) * q
    i = int(k)
    return v[i] if i + 1 >= len(v) else v[i] + (v[i + 1] - v[i]) * (k - i)


def equilibrio_diario(p):
    margen = p["ticket"] * p["margen_bruto"] - p["costo_entrega"]
    if margen <= 0:
        return margen, None
    return margen, p["costos_fijos_mes"] / margen / p["dias_mes"]


def escenario_todos_los_costos(p, propuestas):
    """El mismo resultado si cada pedido carga todos sus costos, no solo el reparto, y qué margen bruto haría falta con esa capacidad."""
    margen = p["ticket"] * p["margen_bruto"] - p["costo_variable_completo"]
    eq = None if margen <= 0 else p["costos_fijos_mes"] / margen / p["dias_mes"]
    necesario = (p["costo_variable_completo"] + p["costos_fijos_mes"] / p["dias_mes"] / p["capacidad_diaria"]) / p["ticket"]
    return {"costo_variable_pedido": p["costo_variable_completo"], "margen_pedido": round(margen, 2),
            "equilibrio_diario": None if eq is None else round(eq, 1),
            "viables": 0 if eq is None else sum(1 for x in propuestas if x["demanda_simulada"]["p50"] >= eq),
            "margen_bruto_necesario": round(necesario, 4)}


def proponer(colonias, microhubs_actuales=(), parametros=None):
    """Recorrido completo: demanda → ubicación → simulación → equilibrio. `colonias`: dicts con cve, nombre, lat, lng, poblacion, grado."""
    p = con_defecto(parametros)
    demanda = [{**c, "peso": demanda_esperada(c, p)} for c in colonias if es_bajos_ingresos(c)]
    cands = [{"cve": c["cve"], "nombre": c["nombre"], "lat": c["lat"], "lng": c["lng"]} for c in colonias]
    if not demanda or not cands:
        return {"parametros": p, "propuestas": [], "pasos": ["No hay colonias de bajos ingresos en la zona."], "resumen": {}}
    elegidos, cubre, pasos = cobertura_maxima(cands, demanda, int(p["p"]), p["radio_km"])
    margen, eq = equilibrio_diario(p)
    asignacion = {i: [] for i in elegidos}
    for j, d in enumerate(demanda):
        opciones = [i for i in elegidos if j in cubre[i]]
        if opciones:
            i = min(opciones, key=lambda i: haversine_km(cands[i]["lat"], cands[i]["lng"], d["lat"], d["lng"]))
            asignacion[i].append(j)
    propuestas = []
    for n, i in enumerate(elegidos, 1):
        js = asignacion[i]
        medias = [demanda[j]["peso"] for j in js]
        serie = [min(x, p["capacidad_diaria"]) for x in simular_demanda(medias, p, n)]
        media, p10, p50, p90 = sum(serie) / len(serie), _percentil(serie, .1), _percentil(serie, .5), _percentil(serie, .9)
        poblacion = sum(demanda[j]["poblacion"] for j in js)
        if eq is None:
            veredicto, margen_seg, pen_min, prob = "NO VIABLE", None, None, 0.0
        else:
            margen_seg = media / eq - 1
            prob = sum(1 for x in serie if x >= eq) / len(serie)
            esperado = sum(medias)
            pen_min = p["penetracion"] * eq / esperado if esperado else None
            veredicto = ("VIABLE" if p50 >= eq * (1 + p["margen_seguridad_min"]) else "VIABLE AJUSTADO" if p50 >= eq else "NO VIABLE")
        cercano = min(microhubs_actuales, key=lambda m: haversine_km(m["lat"], m["lng"], cands[i]["lat"], cands[i]["lng"]), default=None)
        propuestas.append({
            "orden": n, "colonia_sede": cands[i]["nombre"], "cve_col": cands[i]["cve"],
            "latitud": round(cands[i]["lat"], 6), "longitud": round(cands[i]["lng"], 6),
            "colonias_atendidas": len(js), "poblacion_atendida": round(poblacion), "hogares_atendidos": round(poblacion / p["personas_por_hogar"]),
            "demanda_esperada_dia": round(sum(medias), 1),
            "demanda_simulada": {"media": round(media, 1), "p10": round(p10, 1), "p50": round(p50, 1), "p90": round(p90, 1),
                                 "dias": p["dias_simulados"], "tope_capacidad": p["capacidad_diaria"]},
            "equilibrio_diario": None if eq is None else round(eq, 1),
            "margen_seguridad": None if margen_seg is None else round(margen_seg, 3),
            "probabilidad_cubrir_equilibrio": round(prob, 3),
            "penetracion_minima": None if pen_min is None else round(pen_min, 4),
            "veredicto": veredicto,
            "microhub_actual_mas_cercano": None if not cercano else {
                "clave": cercano["clave"], "distancia_km": round(haversine_km(cercano["lat"], cercano["lng"], cands[i]["lat"], cands[i]["lng"]), 2)},
            "colonias": [{"cve_col": demanda[j]["cve"], "colonia": demanda[j]["nombre"], "grado": demanda[j]["grado"],
                          "poblacion": demanda[j]["poblacion"], "pedidos_dia": round(demanda[j]["peso"], 1)} for j in js],
        })
    total_dem = sum(d["peso"] for d in demanda)
    cubierta = sum(pr["demanda_esperada_dia"] for pr in propuestas)
    pob_bi = sum(d["poblacion"] for d in demanda)
    pasos.append(f"Equilibrio: margen por pedido = {p['ticket']:.2f} × {p['margen_bruto']:.0%} − {p['costo_entrega']:.2f} = {margen:.2f}; "
                 + ("ningún volumen recupera los costos fijos." if eq is None else
                    f"{p['costos_fijos_mes']:,.0f} ÷ {margen:.2f} ÷ {p['dias_mes']} = {eq:.1f} pedidos/día por microhub."))
    return {
        "parametros": p,
        "resumen": {
            "colonias_zona": len(colonias), "colonias_bajos_ingresos": len(demanda), "poblacion_bajos_ingresos": round(pob_bi),
            "demanda_bajos_ingresos_dia": round(total_dem, 1), "demanda_cubierta_dia": round(cubierta, 1),
            "cobertura_pct": round(100 * cubierta / total_dem, 1) if total_dem else 0.0,
            "equilibrio_diario": None if eq is None else round(eq, 1),
            "viables": sum(1 for pr in propuestas if pr["veredicto"] != "NO VIABLE"),
            "todos_los_costos": escenario_todos_los_costos(p, propuestas),
        },
        "propuestas": propuestas,
        "pasos": pasos,
    }
