"""
Servicio de cobertura · puerto 5116 · contrato v1

  GET  /api/v1/cobertura/zonas                     qué microhubs cubren cada zona y en cuánto tiempo llegan
  GET  /api/v1/cobertura/resumen                   porcentaje de zonas y de hogares cubiertos, zonas desatendidas
  GET  /api/v1/cobertura/punto                     qué microhubs cubren una coordenada
  POST /api/v1/cobertura/evaluaciones              qué agregaría un microhub en una coordenada nueva (guardar = planeacion.editar)
  GET  /api/v1/cobertura/evaluaciones[/{id}]       evaluaciones guardadas
  GET  /api/v1/cobertura/candidatos                las ubicaciones candidatas de planeación, de la que más hogares suma o acerca a la que menos
  GET  /api/v1/cobertura/escenarios                cómo cambia la cobertura si cambia el radio o el factor de rodeo
  PUT  /api/v1/cobertura/zonas/{id}/poblacion      corrige la población de una zona (planeacion.editar)
  GET  /api/v1/cobertura/supuestos                 de dónde sale cada valor y cómo se calibra

Responsabilidad única: qué parte del territorio atiende la red y cuánto agregaría una ubicación nueva.
Las zonas y los microhubs se piden a sus servicios; la población es dato de este servicio (cobertura_zona_dato).

Reglas:
  · Una zona está cubierta por un microhub si la distancia en línea recta entre su centro y el microhub es menor o igual
    que el radio del microhub (la misma regla de fn_cubre, RN05).
  · El tiempo de llegada usa la distancia por calle = línea recta × factor de rodeo, la velocidad de reparto y el tiempo
    por parada. «Dentro de la promesa» significa que llega en `cob_tiempo_max_min` minutos o menos.
  · Hogares = población ÷ personas por hogar. La cobertura se mide en zonas y en hogares.
  · Una ubicación nueva «canibaliza» si más de `cob_solape_max_pct` por ciento de las zonas que cubre ya las cubre otro microhub.
"""
from flask import g, request

from comun import config, supuestos as sup
from comun.base import crear_app, documentar, leer_cuerpo, leer_paginacion, lista, paginacion, requiere, responder, tiene
from comun.base_errores import ErrorApi, filtro_invalido, invalido, no_encontrado
from comun.calculo import pc
from comun.clientes import llamar, mapa
from comun.datos import como_json, conexion, consultar
from comun.formatos import fecha
from comun.validar import Campo, validar

app = crear_app("cobertura", "Microhubs · Cobertura",
                "Cobertura territorial de la red de microhubs, evaluación de ubicaciones nuevas y escenarios de radio.", 5116)
P = config.PREFIJO
DEFECTOS = {"factor_rodeo_distancia": 1.3, "velocidad_reparto_kmh": 22.0, "tiempo_servicio_min": 4.0, "cob_tiempo_max_min": 30.0,
            "cob_solape_max_pct": 40.0, "tamano_hogar": 3.6, "costo_base_entrega": 18.0, "costo_km_reparto": 4.5, "paradas_por_viaje": 3.0}
CLAVES_SUPUESTOS = list(DEFECTOS)
RADIO_DEFECTO = 1.5


# --------------------------------------------------------------------
# Cálculo (funciones puras, sin bases de datos)
# --------------------------------------------------------------------
def opcion(h, z, p, rodeo=None, radio=None):
    """Un microhub frente a una zona: distancia en línea recta, distancia por calle, minutos y si la cubre."""
    rodeo = p["factor_rodeo_distancia"] if rodeo is None else rodeo
    recta = pc.haversine_km(h["lat"], h["lng"], z["lat"], z["lng"])
    calle = recta * rodeo
    minutos = calle / p["velocidad_reparto_kmh"] * 60 + p["tiempo_servicio_min"]
    r = h["radio_km"] if radio is None else radio
    return {"h": h, "distancia_km": recta, "distancia_calle_km": calle, "minutos": minutos, "cubre": recta <= r,
            "dentro_promesa": minutos <= p["cob_tiempo_max_min"]}


def cobertura_de_zonas(zonas, hubs, p, rodeo=None, radio=None):
    """Para cada zona, los microhubs que la cubren (de más cerca a más lejos) y el más cercano de todos."""
    salida = []
    for z in zonas:
        opciones = sorted((opcion(h, z, p, rodeo, radio) for h in hubs), key=lambda o: o["distancia_km"])
        cubren = [o for o in opciones if o["cubre"]]
        salida.append({"zona": z, "cubren": cubren, "mas_cercano": opciones[0] if opciones else None,
                       "mejor": cubren[0] if cubren else None})
    return salida


def resumen_red(cobertura):
    n = len(cobertura)
    hogares = sum(c["zona"]["hogares"] for c in cobertura)
    cub = [c for c in cobertura if c["mejor"]]
    h_cub = sum(c["zona"]["hogares"] for c in cub)
    minutos = (sum(c["mejor"]["minutos"] * c["zona"]["hogares"] for c in cub) / h_cub) if h_cub else None
    dentro = sum(c["zona"]["hogares"] for c in cub if c["mejor"]["dentro_promesa"])
    return {"zonas": n, "zonas_cubiertas": len(cub), "pct_zonas": round(100 * len(cub) / n, 1) if n else 0.0,
            "hogares": hogares, "hogares_cubiertos": h_cub, "pct_hogares": round(100 * h_cub / hogares, 1) if hogares else 0.0,
            "tiempo_promedio_min": None if minutos is None else round(minutos, 1),
            "dentro_promesa_pct": round(100 * dentro / h_cub, 1) if h_cub else None,
            "zonas_solapadas": sum(1 for c in cub if len(c["cubren"]) > 1)}


def evaluar_ubicacion(lat, lng, radio, cobertura_actual, zonas, p):
    """Qué sumaría un microhub en (lat, lng) con ese radio frente a la red actual."""
    cand = {"id": 0, "clave": "NUEVO", "nombre": "Ubicación evaluada", "lat": lat, "lng": lng, "radio_km": radio}
    ya = {c["zona"]["id"]: len(c["cubren"]) for c in cobertura_actual}
    mejor_actual = {c["zona"]["id"]: (c["mejor"]["minutos"] if c["mejor"] else None) for c in cobertura_actual}
    dentro = []
    for z in zonas:
        o = opcion(cand, z, p)
        if o["cubre"]:
            dentro.append({"zona": z, "o": o, "ya_cubren": ya.get(z["id"], 0)})
    nuevas = [d for d in dentro if d["ya_cubren"] == 0]
    # Zonas que ya tenían cobertura pero a las que esta ubicación llegaría al menos un minuto antes.
    mejoran = [d for d in dentro if mejor_actual.get(d["zona"]["id"]) is not None and d["o"]["minutos"] <= mejor_actual[d["zona"]["id"]] - 1]
    h_mejoran = sum(d["zona"]["hogares"] for d in mejoran)
    ahorro = (sum((mejor_actual[d["zona"]["id"]] - d["o"]["minutos"]) * d["zona"]["hogares"] for d in mejoran) / h_mejoran) if h_mejoran else 0.0
    h_dentro = sum(d["zona"]["hogares"] for d in dentro)
    h_nuevos = sum(d["zona"]["hogares"] for d in nuevas)
    solape = 100 * (len(dentro) - len(nuevas)) / len(dentro) if dentro else 0.0
    dist = (sum(d["o"]["distancia_calle_km"] * d["zona"]["hogares"] for d in dentro) / h_dentro) if h_dentro else \
        (sum(d["o"]["distancia_calle_km"] for d in dentro) / len(dentro) if dentro else 0.0)
    minutos = dist / p["velocidad_reparto_kmh"] * 60 + p["tiempo_servicio_min"]
    costo = p["costo_base_entrega"] + 2 * dist * p["costo_km_reparto"] / max(p["paradas_por_viaje"], 1)
    n, hog = len(zonas), sum(z["hogares"] for z in zonas)
    antes = resumen_red(cobertura_actual)
    despues_c = sum(1 for c in cobertura_actual if c["mejor"]) + len(nuevas)
    despues_h = antes["hogares_cubiertos"] + h_nuevos
    return {"dentro": dentro, "zonas_nuevas": len(nuevas), "hogares_en_radio": h_dentro, "hogares_nuevos": h_nuevos,
            "hogares_con_mejor_tiempo": h_mejoran, "minutos_ahorrados": round(ahorro, 1),
            "solapamiento_pct": round(solape, 1), "canibaliza": solape > p["cob_solape_max_pct"],
            "distancia_promedio_km": round(dist, 2), "minutos_promedio": round(minutos, 1), "costo_ultima_milla": round(costo, 2),
            "antes": {"pct_zonas": antes["pct_zonas"], "pct_hogares": antes["pct_hogares"]},
            "despues": {"pct_zonas": round(100 * despues_c / n, 1) if n else 0.0, "pct_hogares": round(100 * despues_h / hog, 1) if hog else 0.0}}


def escenarios_de_radio(zonas, hubs, radios, rodeos, p):
    filas = []
    for rodeo in rodeos:
        for radio in radios:
            r = resumen_red(cobertura_de_zonas(zonas, hubs, p, rodeo, radio))
            filas.append({"radio_km": radio, "rodeo": rodeo, "zonas_cubiertas": r["zonas_cubiertas"], "pct_zonas": r["pct_zonas"],
                          "pct_hogares": r["pct_hogares"], "tiempo_promedio_min": r["tiempo_promedio_min"],
                          "dentro_promesa_pct": r["dentro_promesa_pct"]})
    return filas


# --------------------------------------------------------------------
# Datos
# --------------------------------------------------------------------
def parametros():
    return sup.valores(DEFECTOS)


def red(p):
    """Zonas (con hogares) y microhubs activos, pedidos a sus servicios; la población es de este servicio."""
    zs, hs = mapa("zonas", "zonas"), mapa("microhubs", "microhubs")
    if not zs or not hs:
        raise ErrorApi(503, "SERVICIO_NO_DISPONIBLE", "No se pudieron consultar las zonas o los microhubs; sin ellos no se calcula la cobertura.")
    pob = {f["zona_id"]: f["poblacion"] for f in consultar("SELECT zona_id, poblacion FROM cobertura_zona_dato")}
    zonas = [{"id": z["id"], "nombre": z["nombre"], "lat": float(z["latitud"]), "lng": float(z["longitud"]),
              "poblacion": pob.get(z["id"], 0), "hogares": round(pob.get(z["id"], 0) / p["tamano_hogar"]) if p["tamano_hogar"] else 0}
             for z in sorted(zs.values(), key=lambda z: z["id"])]
    hubs = [{"id": h["id"], "clave": h["clave"], "nombre": h["nombre"], "lat": float(h["latitud"]), "lng": float(h["longitud"]),
             "radio_km": float(h["radio_km"] or RADIO_DEFECTO)} for h in sorted(hs.values(), key=lambda h: h["id"]) if h["estatus"] == "activo"]
    return zonas, hubs


def ref(x):
    return {"id": x["id"], "nombre": x["nombre"]}


def opcion_salida(o):
    return {"microhub": ref(o["h"]), "distancia_km": round(o["distancia_km"], 2), "distancia_calle_km": round(o["distancia_calle_km"], 2),
            "minutos": round(o["minutos"], 1), "cubre": o["cubre"], "dentro_promesa": o["dentro_promesa"]}


def zona_salida(c):
    z = c["zona"]
    return {"zona": ref(z), "hogares": z["hogares"], "estado": "cubierta" if c["mejor"] else "sin_cobertura",
            "solapada": len(c["cubren"]) > 1, "cubierta_por": [opcion_salida(o) for o in c["cubren"]],
            "mas_cercano": opcion_salida(c["mas_cercano"]) if c["mas_cercano"] else None,
            "minutos_mejor": round(c["mejor"]["minutos"], 1) if c["mejor"] else None}


def usados(p, modificados=()):
    return sup.usados({k: p[k] for k in ("factor_rodeo_distancia", "velocidad_reparto_kmh", "tiempo_servicio_min", "cob_tiempo_max_min",
                                          "cob_solape_max_pct", "tamano_hogar")}, modificados)


ITEMS = {"cubierta_por": "opcion", "supuestos_usados": "supuesto", "valores_modificados": "clave", "zonas": "zona_evaluada"}


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


def _lista_numeros(nombre, defecto, minimo, maximo, maximo_n=6):
    crudo = (request.args.get(nombre) or "").strip()
    if not crudo:
        return defecto
    try:
        v = [float(x) for x in crudo.split(",") if x.strip()]
    except ValueError:
        raise filtro_invalido(nombre, f"{nombre} es una lista de números separados por coma.")
    if not 1 <= len(v) <= maximo_n or any(not minimo <= x <= maximo for x in v):
        raise filtro_invalido(nombre, f"{nombre}: entre 1 y {maximo_n} valores, cada uno de {minimo:g} a {maximo:g}.")
    return v


# --------------------------------------------------------------------
# Consultas
# --------------------------------------------------------------------
@app.get(f"{P}/cobertura/zonas")
@requiere("cobertura.ver")
def zonas_cobertura():
    pagina, por, desde = leer_paginacion()
    p = parametros()
    zonas, hubs = red(p)
    cob = cobertura_de_zonas(zonas, hubs, p)
    pagina_c = cob[desde:desde + por]
    return lista(pagina_c, paginacion(pagina, por, len(cob)), "zona_cobertura", "cobertura_zonas", zona_salida, items=ITEMS)


@app.get(f"{P}/cobertura/resumen")
@requiere("cobertura.ver")
def resumen():
    p = parametros()
    zonas, hubs = red(p)
    cob = cobertura_de_zonas(zonas, hubs, p)
    r = resumen_red(cob)
    sin = [{"zona": ref(c["zona"]), "hogares": c["zona"]["hogares"], "microhub_mas_cercano": ref(c["mas_cercano"]["h"]) if c["mas_cercano"] else None,
            "distancia_km": round(c["mas_cercano"]["distancia_km"], 2) if c["mas_cercano"] else None} for c in cob if not c["mejor"]]
    return responder({**r, "zonas_sin_cobertura": sin, "microhubs_activos": len(hubs), "supuestos_usados": usados(p)}, raiz="cobertura_resumen",
                     items={"zonas_sin_cobertura": "zona_sin_cobertura", "supuestos_usados": "supuesto"})


@app.get(f"{P}/cobertura/punto")
@requiere("cobertura.ver")
def punto():
    lat, _ = _numero("latitud", None, 20, 33)
    lng, _ = _numero("longitud", None, -118, -86)
    if lat is None or lng is None:
        raise filtro_invalido("latitud", "latitud y longitud son obligatorias.")
    p = parametros()
    zonas, hubs = red(p)
    z0 = {"id": 0, "nombre": "Punto consultado", "lat": lat, "lng": lng, "hogares": 0}
    opciones = sorted((opcion(h, z0, p) for h in hubs), key=lambda o: o["distancia_km"])
    cercana = min(zonas, key=lambda z: pc.haversine_km(lat, lng, z["lat"], z["lng"])) if zonas else None
    return responder({"latitud": lat, "longitud": lng, "cubierto": any(o["cubre"] for o in opciones),
                      "zona_mas_cercana": ({**ref(cercana), "distancia_km": round(pc.haversine_km(lat, lng, cercana["lat"], cercana["lng"]), 2)}
                                           if cercana else None),
                      "opciones": [opcion_salida(o) for o in opciones], "supuestos_usados": usados(p)}, raiz="cobertura_punto",
                     items={"opciones": "opcion", "supuestos_usados": "supuesto"})


# --------------------------------------------------------------------
# Evaluar una ubicación
# --------------------------------------------------------------------
def evaluacion_salida(r, nombre, lat, lng, radio, p, eid=None, candidato=None):
    return {"id": eid, "nombre": nombre, "candidato": candidato, "latitud": lat, "longitud": lng, "radio_km": radio,
            "zonas": [{"zona": ref(d["zona"]), "hogares": d["zona"]["hogares"], "distancia_km": round(d["o"]["distancia_km"], 2),
                       "distancia_calle_km": round(d["o"]["distancia_calle_km"], 2), "minutos": round(d["o"]["minutos"], 1),
                       "microhubs_que_ya_cubren": d["ya_cubren"]} for d in r["dentro"]],
            "zonas_nuevas": r["zonas_nuevas"], "hogares_en_radio": r["hogares_en_radio"], "hogares_nuevos": r["hogares_nuevos"],
            "hogares_con_mejor_tiempo": r["hogares_con_mejor_tiempo"], "minutos_ahorrados": r["minutos_ahorrados"],
            "solapamiento_pct": r["solapamiento_pct"], "canibaliza": r["canibaliza"], "distancia_promedio_km": r["distancia_promedio_km"],
            "minutos_promedio": r["minutos_promedio"], "costo_ultima_milla": r["costo_ultima_milla"], "antes": r["antes"], "despues": r["despues"],
            "supuestos_usados": usados(p)}


def candidato_de_planeacion(cid):
    status, d = llamar("planeacion", "GET", f"candidatos/{cid}")
    if status == 404:
        raise no_encontrado("No existe esa ubicación candidata.")
    if status in (401, 403):
        raise ErrorApi(403, "PROHIBIDO", "Tu perfil no puede consultar ubicaciones candidatas en planeación.")
    if status != 200 or not isinstance(d, dict):
        raise ErrorApi(503, "SERVICIO_NO_DISPONIBLE", "El servicio de planeación no pudo atender la solicitud.")
    return d


@app.post(f"{P}/cobertura/evaluaciones")
@requiere("cobertura.ver")
def evaluar():
    d = validar(leer_cuerpo("cobertura_evaluacion_nueva"), [
        Campo("nombre", req=False, nulo=True, min_len=3, max_len=120), Campo("latitud", "num", req=False, nulo=True, minimo=20, maximo=33),
        Campo("longitud", "num", req=False, nulo=True, minimo=-118, maximo=-86), Campo("radio_km", "num", req=False, nulo=True, minimo=0.1, maximo=20),
        Campo("candidato_id", "int", req=False, nulo=True, minimo=1), Campo("guardar", "bool", req=False)])
    candidato = None
    if d.get("candidato_id"):
        c = candidato_de_planeacion(d["candidato_id"])
        lat, lng, radio = float(c["latitud"]), float(c["longitud"]), float(d.get("radio_km") or c.get("radio_km") or RADIO_DEFECTO)
        nombre = d.get("nombre") or f"Evaluación de {c['clave']}"
        candidato = {"id": c["id"], "clave": c["clave"], "nombre": c["nombre"]}
    else:
        if d.get("latitud") is None or d.get("longitud") is None:
            raise invalido("latitud", "Indica latitud y longitud, o un candidato_id.")
        lat, lng, radio = d["latitud"], d["longitud"], float(d.get("radio_km") or RADIO_DEFECTO)
        nombre = d.get("nombre") or "Evaluación de una coordenada"
    p = parametros()
    zonas, hubs = red(p)
    r = evaluar_ubicacion(lat, lng, radio, cobertura_de_zonas(zonas, hubs, p), zonas, p)
    eid = None
    if d.get("guardar"):
        if not tiene("planeacion.editar"):
            raise ErrorApi(403, "PROHIBIDO", "Guardar una evaluación exige el permiso planeacion.editar.")
        salida = evaluacion_salida(r, nombre, lat, lng, radio, p, None, candidato)
        with conexion() as con, con.cursor() as cur:
            cur.execute("INSERT INTO cobertura_evaluacion (nombre, parametros, resultado, creado_por) VALUES (%s, %s, %s, %s) RETURNING id",
                        (nombre, como_json({"latitud": lat, "longitud": lng, "radio_km": radio, "candidato_id": d.get("candidato_id")}),
                         como_json(salida), g.usuario["id"]))
            eid = cur.fetchone()["id"]
    return responder(evaluacion_salida(r, nombre, lat, lng, radio, p, eid, candidato), 201 if eid else 200, raiz="cobertura_evaluacion", items=ITEMS)


@app.get(f"{P}/cobertura/evaluaciones")
@requiere("cobertura.ver")
def evaluaciones():
    pagina, por, desde = leer_paginacion()
    total = consultar("SELECT count(*) AS n FROM cobertura_evaluacion", una=True)["n"]
    filas = consultar("SELECT id, nombre, resultado, creado_por, creado_en FROM cobertura_evaluacion ORDER BY id DESC LIMIT %s OFFSET %s", (por, desde))
    return lista(filas, paginacion(pagina, por, total), "evaluacion", "cobertura_evaluaciones",
                 lambda f: {"id": f["id"], "nombre": f["nombre"], "zonas_nuevas": f["resultado"]["zonas_nuevas"], "hogares_nuevos": f["resultado"]["hogares_nuevos"],
                            "solapamiento_pct": f["resultado"]["solapamiento_pct"], "canibaliza": f["resultado"]["canibaliza"],
                            "creado_por": f["creado_por"], "creado_en": fecha(f["creado_en"])})


@app.get(f"{P}/cobertura/evaluaciones/<int:eid>")
@requiere("cobertura.ver")
def evaluacion_una(eid):
    f = consultar("SELECT id, resultado FROM cobertura_evaluacion WHERE id = %s", (eid,), una=True)
    if not f:
        raise no_encontrado("No existe esa evaluación.")
    return responder({**f["resultado"], "id": f["id"]}, raiz="cobertura_evaluacion", items=ITEMS)


@app.get(f"{P}/cobertura/candidatos")
@requiere("cobertura.ver")
def candidatos():
    p = parametros()
    zonas, hubs = red(p)
    actual = cobertura_de_zonas(zonas, hubs, p)
    status, d = llamar("planeacion", "GET", "candidatos", params={"por_pagina": 100})
    if status in (401, 403):
        raise ErrorApi(403, "PROHIBIDO", "Tu perfil no puede consultar ubicaciones candidatas en planeación.")
    if status != 200 or not isinstance(d, dict):
        raise ErrorApi(503, "SERVICIO_NO_DISPONIBLE", "El servicio de planeación no pudo atender la solicitud.")
    filas = []
    for c in d["datos"]:
        radio = float(c.get("radio_km") or RADIO_DEFECTO)
        r = evaluar_ubicacion(float(c["latitud"]), float(c["longitud"]), radio, actual, zonas, p)
        filas.append({"candidato": {"id": c["id"], "clave": c["clave"], "nombre": c["nombre"]}, "latitud": float(c["latitud"]),
                      "longitud": float(c["longitud"]), "radio_km": radio, "zonas_nuevas": r["zonas_nuevas"], "hogares_nuevos": r["hogares_nuevos"],
                      "hogares_con_mejor_tiempo": r["hogares_con_mejor_tiempo"], "minutos_ahorrados": r["minutos_ahorrados"],
                      "solapamiento_pct": r["solapamiento_pct"], "canibaliza": r["canibaliza"], "minutos_promedio": r["minutos_promedio"],
                      "costo_ultima_milla": r["costo_ultima_milla"]})
    filas.sort(key=lambda f: (-f["hogares_nuevos"], -f["hogares_con_mejor_tiempo"], f["solapamiento_pct"], f["candidato"]["clave"]))
    for i, f in enumerate(filas, 1):
        f["ranking"] = i
    return responder({"datos": filas, "red_actual": {"pct_zonas": resumen_red(actual)["pct_zonas"], "pct_hogares": resumen_red(actual)["pct_hogares"]},
                      "supuestos_usados": usados(p)}, raiz="cobertura_candidatos", items={"datos": "candidato_cobertura", "supuestos_usados": "supuesto"})


@app.get(f"{P}/cobertura/escenarios")
@requiere("cobertura.ver")
def escenarios():
    p = parametros()
    zonas, hubs = red(p)
    radios = _lista_numeros("radios", [1.0, 1.5, 2.0, 2.5], 0.1, 20)
    rodeos = _lista_numeros("rodeos", [p["factor_rodeo_distancia"]], 1.0, 3.0, 4)
    filas = escenarios_de_radio(zonas, hubs, radios, rodeos, p)
    return responder({"filas": filas, "supuestos_usados": usados(p, ["factor_rodeo_distancia"] if request.args.get("rodeos") else [])},
                     raiz="cobertura_escenarios", items={"filas": "fila", "supuestos_usados": "supuesto"})


@app.put(f"{P}/cobertura/zonas/<int:zid>/poblacion")
@requiere("planeacion.editar")
def poblacion(zid):
    d = validar(leer_cuerpo("poblacion_nueva"), [Campo("poblacion", "int", minimo=0, maximo=10_000_000), Campo("fuente", min_len=5, max_len=200)])
    zs = mapa("zonas", "zonas")
    if zid not in zs:
        raise no_encontrado("No existe esa zona.")
    with conexion() as con, con.cursor() as cur:
        cur.execute("INSERT INTO cobertura_zona_dato (zona_id, poblacion, fuente) VALUES (%s, %s, %s) ON CONFLICT (zona_id) DO UPDATE "
                    "SET poblacion = EXCLUDED.poblacion, fuente = EXCLUDED.fuente, actualizado_en = now()", (zid, d["poblacion"], d["fuente"]))
    p = parametros()
    return responder({"zona": ref(zs[zid]), "poblacion": d["poblacion"], "hogares": round(d["poblacion"] / p["tamano_hogar"]), "fuente": d["fuente"]},
                     raiz="poblacion_zona")


@app.get(f"{P}/cobertura/supuestos")
@requiere("cobertura.ver")
def supuestos_cobertura():
    return responder({"datos": sup.listar(CLAVES_SUPUESTOS)}, raiz="supuestos_cobertura", items={"datos": "supuesto"})


# --------------------------------------------------------------------
# Documentación
# --------------------------------------------------------------------
PAG = [("pagina", "query", "integer", "Página (1…)"), ("por_pagina", "query", "integer", "1 a 100")]
documentar(app, "GET", f"{P}/cobertura/zonas", "Cobertura de cada zona", permisos=["cobertura.ver"], parametros=PAG,
           descripcion="Para cada zona: hogares, microhubs que la cubren (radio en línea recta), minutos de llegada y si cae dentro de la promesa.",
           respuestas={200: ("Página de zonas", "CoberturaZonaLista.ok")}, errores=[400, 403, 503])
documentar(app, "GET", f"{P}/cobertura/resumen", "Resumen de cobertura de la red", permisos=["cobertura.ver"],
           respuestas={200: ("Porcentajes, zonas desatendidas y supuestos usados", "CoberturaResumen.ok")}, errores=[403, 503])
documentar(app, "GET", f"{P}/cobertura/punto", "Qué microhubs cubren una coordenada", permisos=["cobertura.ver"],
           parametros=[("latitud", "query", "number", "20 a 33"), ("longitud", "query", "number", "-118 a -86")],
           respuestas={200: ("Opciones de menor a mayor distancia", "CoberturaPunto.ok")}, errores=[400, 403, 503])
documentar(app, "POST", f"{P}/cobertura/evaluaciones", "Evaluar una ubicación nueva", permisos=["cobertura.ver"], cuerpo="CoberturaEvaluacionNueva.ok",
           descripcion="Con latitud y longitud, o con candidato_id (ubicación candidata de planeación). Devuelve las zonas que cubriría, cuántas son nuevas, a cuántos hogares ya cubiertos llegaría antes, "
                       "cuánto se traslapa con los microhubs actuales, el tiempo y el costo de última milla, y la cobertura antes y después. "
                       "Con guardar=true (planeacion.editar) la deja registrada y responde 201.",
           respuestas={200: ("Evaluación", "CoberturaEvaluacion.ok")}, errores=[400, 403, 404, 422, 503])
documentar(app, "GET", f"{P}/cobertura/evaluaciones", "Evaluaciones guardadas", permisos=["cobertura.ver"], parametros=PAG,
           respuestas={200: ("Página de evaluaciones", "CoberturaEvaluacionLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/cobertura/evaluaciones/{{id}}", "Una evaluación guardada", permisos=["cobertura.ver"], parametros=[("id", "path", "integer", "Id")],
           respuestas={200: ("Evaluación completa", "CoberturaEvaluacion.ok")}, errores=[403, 404])
documentar(app, "GET", f"{P}/cobertura/candidatos", "Ranking de ubicaciones candidatas", permisos=["cobertura.ver"],
           descripcion="Evalúa cada candidato de planeación contra la red actual; primero el que suma más hogares nuevos y, a igualdad, el que acerca el servicio a más hogares que ya tenían cobertura.",
           respuestas={200: ("Ranking", "CoberturaCandidatos.ok")}, errores=[403, 503])
documentar(app, "GET", f"{P}/cobertura/escenarios", "Cobertura con otros radios o factores de rodeo", permisos=["cobertura.ver"],
           parametros=[("radios", "query", "string", "Radios en km separados por coma (1,1.5,2,2.5 por omisión; máximo 6)"),
                       ("rodeos", "query", "string", "Factores de rodeo separados por coma (el de la configuración por omisión; máximo 4)")],
           descripcion="Aplica el mismo radio a todos los microhubs y muestra qué porcentaje de zonas y de hogares quedaría cubierto, y en cuánto tiempo.",
           respuestas={200: ("Matriz de escenarios", "CoberturaEscenarios.ok")}, errores=[400, 403, 503])
documentar(app, "PUT", f"{P}/cobertura/zonas/{{id}}/poblacion", "Corregir la población de una zona", permisos=["planeacion.editar"],
           parametros=[("id", "path", "integer", "Id de la zona")], cuerpo="PoblacionNueva.ok", descripcion="Indica la fuente del dato.",
           respuestas={200: ("Población y hogares", "PoblacionZona.ok")}, errores=[400, 403, 404, 422])
documentar(app, "GET", f"{P}/cobertura/supuestos", "Supuestos del modelo de cobertura", permisos=["cobertura.ver"],
           descripcion="Valor, origen (medido, supuesto o normativo), justificación y cómo calibrarlo con datos reales.",
           respuestas={200: ("Supuestos documentados", "SupuestosCobertura.ok")}, errores=[403])
