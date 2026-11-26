"""
Servicio de demanda · puerto 5115 · contrato v1

  POST /api/v1/demanda/sincronizacion        trae de pedidos los días indicados y los guarda como observaciones (demanda.editar)
  GET  /api/v1/demanda/observaciones         observaciones por día, zona y categoría
  GET  /api/v1/demanda/resumen               pedidos, venta, ticket, no atendidos por zona
  GET  /api/v1/demanda/patrones              índice de cada día de la semana y venta por categoría
  GET  /api/v1/demanda/proyeccion            proyección diaria con banda de error
  GET  /api/v1/demanda/comparacion           lo observado contra lo que el modelo habría proyectado
  GET  /api/v1/demanda/potencial             demanda posible según hogares y penetración, contra lo observado
  GET  /api/v1/demanda/supuestos             de dónde sale cada valor y cómo se calibra

Responsabilidad única: cuánto se pide, dónde y cuándo, y cuánto se podría pedir. Los pedidos reales los lee del servicio de
pedidos (GET /pedidos/resumen) y los guarda como observaciones propias; los hogares de cada zona los pide a cobertura.

Las observaciones traen su fuente: `pedidos` (reales), `sintetica` (historia de demostración que genera la migración; NO son
ventas reales) o `manual`. Al sincronizar un rango, lo sintético de ese rango se reemplaza por lo real. El resumen dice cuántas
observaciones hay de cada fuente para que nadie confunda una cosa con la otra.

Modelo de proyección:
  · Índice semanal: promedio de cada día de la semana ÷ promedio general (con menos de dos semanas completas vale 1).
  · Desestacionalizado = pedidos ÷ índice de su día de la semana.
  · promedio_movil: nivel = promedio de los últimos 7 días desestacionalizados; proyección = nivel × índice.
  · tendencia_estacional: recta de mínimos cuadrados sobre la serie desestacionalizada; proyección = recta × índice.
  · Banda = proyección ± z × desviación de los errores del propio ajuste (`dem_banda_z`).
  · Comparación (backtest): se ocultan los últimos días, se proyectan con lo anterior y se miden el error porcentual medio
    (MAPE), el sesgo y cuántos días reales cayeron dentro de la banda.
"""
import datetime as dt
import math
import statistics
from collections import defaultdict

from flask import g, request

from comun import config, supuestos as sup
from comun.base import (crear_app, documentar, filtro_entero, filtro_fecha, filtro_opcion, leer_cuerpo, leer_paginacion, lista, paginacion, requiere,
                        responder)
from comun.base_errores import ErrorApi, filtro_invalido, invalido, no_encontrado
from comun.clientes import exigir, mapa
from comun.datos import conexion, consultar
from comun.formatos import ZONA, dinero
from comun.validar import Campo, validar

app = crear_app("demanda", "Microhubs · Demanda",
                "Observaciones de demanda por zona y día, patrones, proyección con banda de error y demanda potencial.", 5115)
P = config.PREFIJO
DEFECTOS = {"dem_ventana_dias": 60.0, "dem_horizonte_dias": 14.0, "dem_backtest_dias": 7.0, "dem_banda_z": 1.28, "dem_penetracion": 0.12,
            "dem_pedidos_hogar_mes": 2.5, "dias_operacion_mes": 30.0, "tamano_hogar": 3.6}
CLAVES_SUPUESTOS = list(DEFECTOS)
METODOS = ["tendencia_estacional", "promedio_movil"]
DIAS_SEMANA = {1: "lunes", 2: "martes", 3: "miércoles", 4: "jueves", 5: "viernes", 6: "sábado", 7: "domingo"}
MIN_DIAS = 14


# --------------------------------------------------------------------
# Cálculo (funciones puras, sin bases de datos)
# --------------------------------------------------------------------
def serie_completa(por_fecha):
    """{fecha: valor} → lista ordenada de (fecha, valor) con ceros en los días sin observaciones entre el primero y el último."""
    if not por_fecha:
        return []
    ini, fin = min(por_fecha), max(por_fecha)
    return [(ini + dt.timedelta(days=i), por_fecha.get(ini + dt.timedelta(days=i), 0)) for i in range((fin - ini).days + 1)]


def indice_semanal(serie):
    """Índice de cada día de la semana (1 = lunes) y si hay datos suficientes (al menos dos de cada uno)."""
    por_dia = defaultdict(list)
    for f, v in serie:
        por_dia[f.isoweekday()].append(v)
    media = statistics.fmean(v for _, v in serie) if serie else 0.0
    suficiente = bool(serie) and media > 0 and all(len(por_dia[d]) >= 2 for d in range(1, 8))
    indices = {d: (statistics.fmean(por_dia[d]) / media if suficiente else 1.0) for d in range(1, 8)}
    return indices, suficiente


def minimos_cuadrados(puntos):
    """Recta y = a + b·t de mínimos cuadrados. Con un solo punto o t constante, pendiente 0."""
    n = len(puntos)
    if n == 0:
        return 0.0, 0.0
    mt, my = statistics.fmean(t for t, _ in puntos), statistics.fmean(y for _, y in puntos)
    sxx = sum((t - mt) ** 2 for t, _ in puntos)
    b = sum((t - mt) * (y - my) for t, y in puntos) / sxx if sxx else 0.0
    return my - b * mt, b


def ajustar(serie, metodo):
    """Ajusta el modelo a la serie. Devuelve una función fecha → pedidos, la desviación de los errores del ajuste y los parámetros."""
    if len(serie) < MIN_DIAS:
        raise ErrorApi(422, "VALIDACION", f"Hacen falta al menos {MIN_DIAS} días de historia y hay {len(serie)}.")
    indices, suficiente = indice_semanal(serie)
    ini = serie[0][0]
    desest = [((f - ini).days, v / indices[f.isoweekday()] if indices[f.isoweekday()] > 0 else v) for f, v in serie]
    if metodo == "promedio_movil":
        nivel = statistics.fmean(v for _, v in desest[-7:])
        residuos = []
        for i in range(7, len(serie)):                                         # error de pronosticar cada día con los 7 anteriores
            previo = statistics.fmean(v for _, v in desest[i - 7:i])
            residuos.append(serie[i][1] - previo * indices[serie[i][0].isoweekday()])
        parametros = {"nivel": nivel, "pendiente": 0.0}

        def predecir(fecha):
            return nivel * indices[fecha.isoweekday()]
    else:
        a, b = minimos_cuadrados(desest)
        residuos = [serie[i][1] - max(a + b * t, 0.0) * indices[serie[i][0].isoweekday()] for i, (t, _) in enumerate(desest)]
        parametros = {"nivel": a + b * desest[-1][0], "pendiente": b}

        def predecir(fecha):
            return max(a + b * (fecha - ini).days, 0.0) * indices[fecha.isoweekday()]
    sigma = statistics.stdev(residuos) if len(residuos) > 2 else 0.0
    return predecir, sigma, {**parametros, "indices": indices, "suficiente": suficiente}


def proyectar(serie, horizonte, metodo, z):
    predecir, sigma, par = ajustar(serie, metodo)
    ultimo = serie[-1][0]
    filas = []
    for i in range(1, horizonte + 1):
        f = ultimo + dt.timedelta(days=i)
        y = predecir(f)
        filas.append({"fecha": f, "pedidos": y, "minimo": max(y - z * sigma, 0.0), "maximo": y + z * sigma})
    return filas, sigma, par


def respaldo(serie, dias, metodo, z):
    """Proyecta los últimos `dias` con lo anterior y los compara con lo que pasó."""
    corte = serie[-1][0] - dt.timedelta(days=dias)
    entrena, prueba = [x for x in serie if x[0] <= corte], [x for x in serie if x[0] > corte]
    predecir, sigma, _ = ajustar(entrena, metodo)
    filas, ape, sesgo, dentro = [], [], 0.0, 0
    for f, y in prueba:
        yh = predecir(f)
        err = yh - y
        sesgo += err
        if y > 0:
            ape.append(abs(err) / y)
        dentro += 1 if abs(err) <= z * sigma else 0
        filas.append({"fecha": f, "observado": y, "proyectado": yh, "error": err, "error_pct": 100 * err / y if y else None})
    total = sum(y for _, y in prueba)
    return {"filas": filas, "mape_pct": 100 * statistics.fmean(ape) if ape else None, "sesgo_pct": 100 * sesgo / total if total else None,
            "dentro_banda_pct": 100 * dentro / len(prueba) if prueba else None, "dias_entrenamiento": len(entrena)}


def potencial(hogares, penetracion, pedidos_hogar_mes, dias_mes):
    mes = hogares * penetracion * pedidos_hogar_mes
    return mes, mes / dias_mes if dias_mes else 0.0


# --------------------------------------------------------------------
# Datos
# --------------------------------------------------------------------
def parametros():
    return sup.valores(DEFECTOS)


def hoy():
    return dt.datetime.now(ZONA).date()


def zonas_nombres():
    return {k: v["nombre"] for k, v in mapa("zonas", "zonas").items()}


def rango(p):
    d, h = filtro_fecha("desde"), filtro_fecha("hasta")
    if not h:
        h = (consultar("SELECT max(fecha) AS f FROM demanda_observacion", una=True)["f"]) or hoy()
    if not d:
        d = h - dt.timedelta(days=int(p["dem_ventana_dias"]) - 1)
    if d > h:
        raise ErrorApi(400, "FILTRO_INVALIDO", "desde no puede ser posterior a hasta.")
    if (h - d).days > 730:
        raise ErrorApi(400, "FILTRO_INVALIDO", "El rango no puede pasar de 730 días.")
    return d, h


def serie_de(zona_id, d, h):
    where, args = "categoria_id IS NULL AND fecha BETWEEN %s AND %s", [d, h]
    if zona_id:
        where += " AND zona_id = %s"; args.append(zona_id)
    filas = consultar(f"SELECT fecha, sum(pedidos)::integer AS pedidos FROM demanda_observacion WHERE {where} GROUP BY fecha ORDER BY fecha", args)
    return serie_completa({f["fecha"]: f["pedidos"] for f in filas})


def validar_zona(zona_id):
    if zona_id and zona_id not in zonas_nombres():
        raise no_encontrado("No existe esa zona.")


def usados(p, claves, modificados=()):
    return sup.usados({k: p[k] for k in claves}, modificados)


ITEMS = {"supuestos_usados": "supuesto", "valores_modificados": "clave"}


def kpi(f, dias):
    """Indicadores de un conjunto de renglones sumados (pedidos, unidades, venta, clientes, no_atendidos)."""
    pedidos, venta = int(f["pedidos"] or 0), float(f["venta"] or 0)
    clientes, no_at = int(f["clientes"] or 0), int(f["no_atendidos"] or 0)
    return {"pedidos": pedidos, "pedidos_dia": round(pedidos / dias, 2) if dias else 0.0,
            "unidades_por_pedido": round(int(f["unidades"] or 0) / pedidos, 2) if pedidos else None, "venta": dinero(venta),
            "ticket_promedio": dinero(venta / pedidos) if pedidos else None,
            "pedidos_por_cliente": round(pedidos / clientes, 2) if clientes else None, "no_atendidos": no_at,
            "pct_no_atendida": round(100 * no_at / (pedidos + no_at), 1) if pedidos + no_at else 0.0}


# --------------------------------------------------------------------
# Sincronización y observaciones
# --------------------------------------------------------------------
def traer(agrupar, d, h):
    filas, pagina = [], 1
    while pagina <= 100:
        r = exigir("pedidos", "GET", "pedidos/resumen",
                   params={"desde": d.isoformat(), "hasta": h.isoformat(), "agrupar": agrupar, "por_pagina": 100, "pagina": pagina})
        filas += r["datos"]
        if pagina >= r["paginacion"]["paginas"]:
            break
        pagina += 1
    return filas


@app.post(f"{P}/demanda/sincronizacion")
@requiere("demanda.editar")
def sincronizar():
    cuerpo = validar(leer_cuerpo("sincronizacion_nueva"), [
        Campo("desde", patron=r"\d{4}-\d{2}-\d{2}", mensaje="Usa el formato AAAA-MM-DD."), Campo("hasta", patron=r"\d{4}-\d{2}-\d{2}", mensaje="Usa el formato AAAA-MM-DD."),
        Campo("por_categoria", "bool", req=False)])
    try:
        d, h = dt.date.fromisoformat(cuerpo["desde"]), dt.date.fromisoformat(cuerpo["hasta"])
    except ValueError:
        raise invalido("desde", "Debe ser una fecha AAAA-MM-DD válida.")
    if d > h or (h - d).days > 400:
        raise invalido("hasta", "El rango va de desde a hasta, con 400 días como máximo.")
    totales = traer("dia_zona", d, h)
    por_cat = traer("dia_zona_categoria", d, h) if cuerpo.get("por_categoria") else []
    with conexion() as con, con.cursor() as cur:
        cur.execute("DELETE FROM demanda_observacion WHERE fuente = 'sintetica' AND fecha BETWEEN %s AND %s", (d, h))
        reemplazadas = cur.rowcount
        for f in totales + por_cat:
            cur.execute("INSERT INTO demanda_observacion (fecha, zona_id, categoria_id, pedidos, unidades, venta, clientes, no_atendidos, fuente) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'pedidos') ON CONFLICT (fecha, zona_id, categoria_id) DO UPDATE SET "
                        "pedidos = EXCLUDED.pedidos, unidades = EXCLUDED.unidades, venta = EXCLUDED.venta, clientes = EXCLUDED.clientes, "
                        "no_atendidos = EXCLUDED.no_atendidos, fuente = 'pedidos', actualizado_en = now()",
                        (f["fecha"], f["zona_id"], f["categoria_id"], f["pedidos"], f["unidades"], f["venta"], f["clientes"], f["no_atendidos"]))
    return responder({"desde": d.isoformat(), "hasta": h.isoformat(), "filas_escritas": len(totales) + len(por_cat),
                      "pedidos_leidos": sum(f["pedidos"] for f in totales), "sinteticas_reemplazadas": reemplazadas}, 201, raiz="sincronizacion")


@app.get(f"{P}/demanda/observaciones")
@requiere("demanda.ver")
def observaciones():
    pagina, por, desde_n = leer_paginacion()
    p = parametros()
    d, h = rango(p)
    zona, cat = filtro_entero("zona_id"), filtro_entero("categoria_id")
    nivel = filtro_opcion("nivel", ["total", "categoria"])
    fuente = filtro_opcion("fuente", ["pedidos", "sintetica", "manual"])
    where, args = ["fecha BETWEEN %s AND %s"], [d, h]
    for cond, valor in (("zona_id = %s", zona), ("categoria_id = %s", cat), ("fuente = %s", fuente)):
        if valor:
            where.append(cond); args.append(valor)
    if nivel == "total":
        where.append("categoria_id IS NULL")
    elif nivel == "categoria":
        where.append("categoria_id IS NOT NULL")
    w = " AND ".join(where)
    total = consultar(f"SELECT count(*) AS n FROM demanda_observacion WHERE {w}", args, una=True)["n"]
    filas = consultar(f"SELECT fecha, zona_id, categoria_id, pedidos, unidades, venta, clientes, no_atendidos, fuente FROM demanda_observacion "
                      f"WHERE {w} ORDER BY fecha DESC, zona_id, categoria_id NULLS FIRST LIMIT %s OFFSET %s", (*args, por, desde_n))
    zn = zonas_nombres()
    cats = {c["id"]: c["nombre"] for c in consultar("SELECT id, nombre FROM categoria")}
    return lista(filas, paginacion(pagina, por, total), "observacion", "observaciones_demanda",
                 lambda f: {"fecha": f["fecha"].isoformat(), "zona": {"id": f["zona_id"], "nombre": zn.get(f["zona_id"])},
                            "categoria": {"id": f["categoria_id"], "nombre": cats.get(f["categoria_id"])} if f["categoria_id"] else None,
                            "pedidos": f["pedidos"], "unidades": f["unidades"], "venta": dinero(f["venta"]), "clientes": f["clientes"],
                            "no_atendidos": f["no_atendidos"], "fuente": f["fuente"]})


# --------------------------------------------------------------------
# Resumen y patrones
# --------------------------------------------------------------------
@app.get(f"{P}/demanda/resumen")
@requiere("demanda.ver")
def resumen():
    p = parametros()
    d, h = rango(p)
    zona = filtro_entero("zona_id")
    validar_zona(zona)
    dias = (h - d).days + 1
    where, args = "categoria_id IS NULL AND fecha BETWEEN %s AND %s", [d, h]
    if zona:
        where += " AND zona_id = %s"; args.append(zona)
    por_zona = consultar(f"SELECT zona_id, sum(pedidos) AS pedidos, sum(unidades) AS unidades, sum(venta) AS venta, sum(clientes) AS clientes, "
                         f"sum(no_atendidos) AS no_atendidos FROM demanda_observacion WHERE {where} GROUP BY zona_id ORDER BY zona_id", args)
    total = consultar(f"SELECT sum(pedidos) AS pedidos, sum(unidades) AS unidades, sum(venta) AS venta, sum(clientes) AS clientes, "
                      f"sum(no_atendidos) AS no_atendidos FROM demanda_observacion WHERE {where}", args, una=True)
    fuentes = {f["fuente"]: f["n"] for f in consultar(f"SELECT fuente, count(*)::integer AS n FROM demanda_observacion WHERE {where} GROUP BY fuente", args)}
    zn = zonas_nombres()
    return responder({"desde": d.isoformat(), "hasta": h.isoformat(), "dias": dias, "total": kpi(total, dias),
                      "zonas": [{"zona": {"id": f["zona_id"], "nombre": zn.get(f["zona_id"])}, **kpi(f, dias)} for f in por_zona],
                      "observaciones_por_fuente": {k: fuentes.get(k, 0) for k in ("pedidos", "sintetica", "manual")}},
                     raiz="demanda_resumen", items={"zonas": "zona_demanda"})


@app.get(f"{P}/demanda/patrones")
@requiere("demanda.ver")
def patrones():
    p = parametros()
    d, h = rango(p)
    zona = filtro_entero("zona_id")
    validar_zona(zona)
    serie = serie_de(zona, d, h)
    if len(serie) < 7:
        raise ErrorApi(422, "VALIDACION", f"Hacen falta al menos 7 días de historia y hay {len(serie)}.")
    indices, suficiente = indice_semanal(serie)
    por_dia = defaultdict(list)
    for f, v in serie:
        por_dia[f.isoweekday()].append(v)
    semanal = [{"dia": i, "nombre": DIAS_SEMANA[i], "pedidos_promedio": round(statistics.fmean(por_dia[i]), 2) if por_dia[i] else 0.0,
                "indice": round(indices[i], 3)} for i in range(1, 8)]
    where, args = "categoria_id IS NOT NULL AND fecha BETWEEN %s AND %s", [d, h]
    if zona:
        where += " AND zona_id = %s"; args.append(zona)
    cats = consultar(f"SELECT o.categoria_id, c.nombre, sum(o.unidades)::integer AS unidades, sum(o.venta) AS venta FROM demanda_observacion o "
                     f"JOIN categoria c ON c.id = o.categoria_id WHERE {where} GROUP BY o.categoria_id, c.nombre ORDER BY sum(o.venta) DESC", args)
    venta_total = sum(float(c["venta"]) for c in cats)
    pico, valle = max(semanal, key=lambda x: x["indice"]), min(semanal, key=lambda x: x["indice"])
    return responder({"desde": d.isoformat(), "hasta": h.isoformat(), "dias": len(serie), "suficiente": suficiente, "semanal": semanal,
                      "categorias": [{"categoria": {"id": c["categoria_id"], "nombre": c["nombre"]}, "unidades": c["unidades"], "venta": dinero(c["venta"]),
                                      "pct_venta": round(100 * float(c["venta"]) / venta_total, 1) if venta_total else 0.0} for c in cats],
                      "dia_pico": pico["nombre"], "dia_valle": valle["nombre"],
                      "fuerza_estacional": round(pico["indice"] / valle["indice"], 2) if valle["indice"] else None},
                     raiz="demanda_patrones", items={"semanal": "dia_semana", "categorias": "categoria_venta"})


# --------------------------------------------------------------------
# Proyección, comparación y potencial
# --------------------------------------------------------------------
def _entero(nombre, defecto, minimo, maximo):
    crudo = (request.args.get(nombre) or "").strip()
    if not crudo:
        return int(defecto), False
    if not crudo.lstrip("-").isdigit() or not minimo <= int(crudo) <= maximo:
        raise filtro_invalido(nombre, f"{nombre} debe ser un entero entre {minimo} y {maximo}.")
    return int(crudo), True


def _modelo():
    p = parametros()
    metodo = filtro_opcion("metodo", METODOS) or "tendencia_estacional"
    zona = filtro_entero("zona_id")
    validar_zona(zona)
    return p, metodo, zona


@app.get(f"{P}/demanda/proyeccion")
@requiere("demanda.ver")
def proyeccion():
    p, metodo, zona = _modelo()
    d, h = rango(p)
    horizonte, mod = _entero("horizonte", p["dem_horizonte_dias"], 1, 90)
    serie = serie_de(zona, d, h)
    filas, sigma, par = proyectar(serie, horizonte, metodo, p["dem_banda_z"])
    zn = zonas_nombres()
    total = sum(f["pedidos"] for f in filas)
    return responder({"metodo": metodo, "zona": {"id": zona, "nombre": zn.get(zona)} if zona else None, "historia_desde": serie[0][0].isoformat(),
                      "historia_hasta": serie[-1][0].isoformat(), "historia_dias": len(serie), "horizonte": horizonte,
                      "indices_confiables": par["suficiente"], "nivel_pedidos_dia": round(par["nivel"], 2), "pendiente_pedidos_dia": round(par["pendiente"], 3),
                      "desviacion_error": round(sigma, 2), "total_pedidos": round(total, 1), "promedio_dia": round(total / horizonte, 2),
                      "serie": [{"fecha": f["fecha"].isoformat(), "pedidos": round(f["pedidos"], 1), "minimo": round(f["minimo"], 1),
                                 "maximo": round(f["maximo"], 1)} for f in filas],
                      "supuestos_usados": usados(p, ["dem_banda_z", "dem_ventana_dias"], ["horizonte"] if mod else [])},
                     raiz="demanda_proyeccion", items={"serie": "dia", **ITEMS})


@app.get(f"{P}/demanda/comparacion")
@requiere("demanda.ver")
def comparacion():
    p, metodo, zona = _modelo()
    d, h = rango(p)
    dias, mod = _entero("dias", p["dem_backtest_dias"], 3, 30)
    serie = serie_de(zona, d, h)
    if len(serie) < MIN_DIAS + dias:
        raise ErrorApi(422, "VALIDACION", f"Hacen falta al menos {MIN_DIAS + dias} días de historia para ocultar {dias} y entrenar con {MIN_DIAS}; hay {len(serie)}.")
    r = respaldo(serie, dias, metodo, p["dem_banda_z"])
    return responder({"metodo": metodo, "zona": {"id": zona, "nombre": zonas_nombres().get(zona)} if zona else None, "dias_prueba": dias,
                      "dias_entrenamiento": r["dias_entrenamiento"], "mape_pct": None if r["mape_pct"] is None else round(r["mape_pct"], 1),
                      "sesgo_pct": None if r["sesgo_pct"] is None else round(r["sesgo_pct"], 1),
                      "dentro_banda_pct": None if r["dentro_banda_pct"] is None else round(r["dentro_banda_pct"], 1),
                      "filas": [{"fecha": f["fecha"].isoformat(), "observado": f["observado"], "proyectado": round(f["proyectado"], 1),
                                 "error": round(f["error"], 1), "error_pct": None if f["error_pct"] is None else round(f["error_pct"], 1)} for f in r["filas"]],
                      "supuestos_usados": usados(p, ["dem_banda_z", "dem_backtest_dias"], ["dias"] if mod else [])},
                     raiz="demanda_comparacion", items={"filas": "dia", **ITEMS})


def _lista_penetraciones(defecto):
    crudo = (request.args.get("penetraciones") or "").strip()
    if not crudo:
        return [0.04, 0.08, 0.12, 0.16, 0.20] if defecto is None else defecto
    try:
        v = [float(x) for x in crudo.split(",") if x.strip()]
    except ValueError:
        raise filtro_invalido("penetraciones", "penetraciones es una lista de fracciones separadas por coma.")
    if not 1 <= len(v) <= 8 or any(not 0 < x <= 1 for x in v):
        raise filtro_invalido("penetraciones", "Entre 1 y 8 valores, cada uno mayor que 0 y hasta 1.")
    return v


@app.get(f"{P}/demanda/potencial")
@requiere("demanda.ver")
def potencial_zona():
    p = parametros()
    zona = filtro_entero("zona_id")
    validar_zona(zona)

    def numero(nombre, defecto, minimo, maximo):
        crudo = (request.args.get(nombre) or "").strip()
        if not crudo:
            return defecto, False
        try:
            v = float(crudo)
        except ValueError:
            raise filtro_invalido(nombre, f"{nombre} debe ser un número.")
        if not minimo < v <= maximo:
            raise filtro_invalido(nombre, f"{nombre} debe ser mayor que {minimo:g} y hasta {maximo:g}.")
        return v, True
    pen, m1 = numero("penetracion", p["dem_penetracion"], 0, 1)
    ph, m2 = numero("pedidos_hogar_mes", p["dem_pedidos_hogar_mes"], 0, 60)
    pagina, hogares_zona = 1, {}
    while pagina <= 5:                                                         # los hogares de cada zona son dato de cobertura
        r = exigir("cobertura", "GET", "cobertura/zonas", params={"por_pagina": 100, "pagina": pagina})
        hogares_zona.update({x["zona"]["id"]: x["hogares"] for x in r["datos"]})
        if pagina >= r["paginacion"]["paginas"]:
            break
        pagina += 1
    hogares = hogares_zona.get(zona, 0) if zona else sum(hogares_zona.values())
    d, h = rango(p)
    d = max(d, h - dt.timedelta(days=27))
    serie = serie_de(zona, d, h)
    observado = statistics.fmean(v for _, v in serie) if serie else 0.0
    dias_mes = p["dias_operacion_mes"]
    mes, dia = potencial(hogares, pen, ph, dias_mes)
    escenarios = []
    for e in _lista_penetraciones(None):
        m, dd = potencial(hogares, e, ph, dias_mes)
        escenarios.append({"penetracion": e, "pedidos_mes": round(m, 1), "pedidos_dia": round(dd, 1),
                           "cuota_capturada_pct": round(100 * observado / dd, 1) if dd else None, "brecha_pedidos_dia": round(dd - observado, 1)})
    return responder({"zona": {"id": zona, "nombre": zonas_nombres().get(zona)} if zona else None, "hogares": hogares, "penetracion": pen,
                      "pedidos_hogar_mes": ph, "pedidos_mes_potencial": round(mes, 1), "pedidos_dia_potencial": round(dia, 1),
                      "pedidos_dia_observados": round(observado, 1), "cuota_capturada_pct": round(100 * observado / dia, 1) if dia else None,
                      "brecha_pedidos_dia": round(dia - observado, 1), "escenarios": escenarios,
                      "supuestos_usados": usados(p, ["dem_penetracion", "dem_pedidos_hogar_mes", "tamano_hogar", "dias_operacion_mes"],
                                                 [n for n, m in (("dem_penetracion", m1), ("dem_pedidos_hogar_mes", m2)) if m])},
                     raiz="demanda_potencial", items={"escenarios": "escenario", **ITEMS})


@app.get(f"{P}/demanda/supuestos")
@requiere("demanda.ver")
def supuestos_demanda():
    return responder({"datos": sup.listar(CLAVES_SUPUESTOS)}, raiz="supuestos_demanda", items={"datos": "supuesto"})


# --------------------------------------------------------------------
# Documentación
# --------------------------------------------------------------------
PAG = [("pagina", "query", "integer", "Página (1…)"), ("por_pagina", "query", "integer", "1 a 100")]
RANGO = [("desde", "query", "string", "AAAA-MM-DD; por omisión, `dem_ventana_dias` días antes de «hasta»"),
         ("hasta", "query", "string", "AAAA-MM-DD; por omisión, la última fecha con observaciones")]
ZONA_Q = ("zona_id", "query", "integer", "Zona; sin ella, todas las zonas")
METODO_Q = ("metodo", "query", "string", "tendencia_estacional (por omisión) | promedio_movil")
documentar(app, "POST", f"{P}/demanda/sincronizacion", "Traer la demanda real desde pedidos", permisos=["demanda.editar"], cuerpo="SincronizacionNueva.ok",
           descripcion="Lee GET /pedidos/resumen del rango y lo guarda como observaciones de fuente `pedidos`. Lo sintético de ese rango se reemplaza por lo real. "
                       "Repetirlo no duplica nada.",
           respuestas={201: ("Cuántas filas se escribieron", "Sincronizacion.ok")}, errores=[400, 403, 422, 503])
documentar(app, "GET", f"{P}/demanda/observaciones", "Observaciones de demanda", permisos=["demanda.ver"],
           parametros=PAG + RANGO + [ZONA_Q, ("categoria_id", "query", "integer", "Categoría"), ("nivel", "query", "string", "total | categoria"),
                                     ("fuente", "query", "string", "pedidos | sintetica | manual")],
           respuestas={200: ("Página de observaciones", "ObservacionDemandaLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/demanda/resumen", "Resumen de demanda", permisos=["demanda.ver"], parametros=RANGO + [ZONA_Q],
           descripcion="Pedidos, pedidos por día, ticket promedio, pedidos por cliente (en el mismo día), no atendidos y cuántas observaciones hay de cada fuente.",
           respuestas={200: ("Totales y por zona", "DemandaResumen.ok")}, errores=[400, 403, 404])
documentar(app, "GET", f"{P}/demanda/patrones", "Patrones de consumo", permisos=["demanda.ver"], parametros=RANGO + [ZONA_Q],
           descripcion="Índice de cada día de la semana (1.00 = el promedio) y la venta por categoría.",
           respuestas={200: ("Patrón semanal y por categoría", "DemandaPatrones.ok")}, errores=[400, 403, 404, 422])
documentar(app, "GET", f"{P}/demanda/proyeccion", "Proyección de demanda", permisos=["demanda.ver"],
           parametros=RANGO + [ZONA_Q, METODO_Q, ("horizonte", "query", "integer", "Días a proyectar, 1 a 90 (`dem_horizonte_dias` por omisión)")],
           descripcion="Proyección diaria con banda (±`dem_banda_z` desviaciones del error del ajuste). Necesita al menos 14 días de historia.",
           respuestas={200: ("Serie proyectada", "DemandaProyeccion.ok")}, errores=[400, 403, 404, 422])
documentar(app, "GET", f"{P}/demanda/comparacion", "Demanda observada contra proyectada", permisos=["demanda.ver"],
           parametros=RANGO + [ZONA_Q, METODO_Q, ("dias", "query", "integer", "Días finales que se ocultan, 3 a 30 (`dem_backtest_dias` por omisión)")],
           descripcion="Proyecta los últimos días usando solo lo anterior y los compara con lo que pasó: error porcentual medio, sesgo y días dentro de la banda.",
           respuestas={200: ("Comparación día por día", "DemandaComparacion.ok")}, errores=[400, 403, 404, 422])
documentar(app, "GET", f"{P}/demanda/potencial", "Demanda potencial", permisos=["demanda.ver"],
           parametros=[ZONA_Q, ("penetracion", "query", "number", "Fracción de hogares que pide en un mes (`dem_penetracion` por omisión)"),
                       ("pedidos_hogar_mes", "query", "number", "Pedidos al mes de un hogar que usa el servicio (`dem_pedidos_hogar_mes`)"),
                       ("penetraciones", "query", "string", "Escenarios, separados por coma (0.04,0.08,0.12,0.16,0.2 por omisión)")],
           descripcion="Hogares (del servicio de cobertura) × penetración × pedidos por hogar y mes, contra el promedio observado en los últimos 28 días.",
           respuestas={200: ("Potencial, brecha y escenarios", "DemandaPotencial.ok")}, errores=[400, 403, 404, 503])
documentar(app, "GET", f"{P}/demanda/supuestos", "Supuestos del modelo de demanda", permisos=["demanda.ver"],
           descripcion="Valor, origen (medido, supuesto o normativo), justificación y cómo calibrarlo con datos reales.",
           respuestas={200: ("Supuestos documentados", "SupuestosDemanda.ok")}, errores=[403])
