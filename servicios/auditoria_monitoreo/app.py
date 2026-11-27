"""
Servicio de auditoría y monitoreo · puerto 5126 · contrato v1

Auditoría (permiso auditoria.ver: administrador y auditor)
  GET  /api/v1/auditoria                                 bitácora de negocio con filtros (usuario, módulo, acción, entidad, fechas)
  GET  /api/v1/auditoria/accesos                         inicios de sesión, fallos, bloqueos y accesos denegados del periodo
  GET  /api/v1/auditoria/trazabilidad/pedido/{id}        línea de tiempo de un pedido (bitácora, estados, inventario, evidencias)
  GET  /api/v1/auditoria/trazabilidad/entrega/{id}       línea de tiempo de una entrega
  GET  /api/v1/auditoria/trazabilidad/inventario         movimientos de un producto en un microhub (microhub_id, producto_id)

Monitoreo (permiso monitoreo.ver; forzar y reconocer: monitoreo.operar)
  GET  /api/v1/monitoreo/estado                          panel: estado de cada servicio, última verificación, tiempos y dependencias caídas
  GET  /api/v1/monitoreo/servicios/{nombre}/historial    historial de verificaciones de un servicio
  GET  /api/v1/monitoreo/disponibilidad                  disponibilidad y tiempos (p50, p95) por servicio en las últimas horas
  GET  /api/v1/monitoreo/metricas                        peticiones, errores y percentiles de duración por servicio (MongoDB)
  GET  /api/v1/monitoreo/alertas                         alertas abiertas y cerradas
  POST /api/v1/monitoreo/alertas/{id}/reconocer          una persona se hace cargo de una alerta abierta
  POST /api/v1/monitoreo/verificaciones                  fuerza una ronda de verificación (todos los servicios o uno)
  GET  /api/v1/monitoreo/supuestos                       de dónde sale cada umbral y cómo se calibra

Responsabilidad única: que se pueda saber quién hizo qué y si la plataforma está sana. Es dueño de `monitoreo_verificacion` y
`monitoreo_alerta`. La bitácora `auditoria` ya existía (la escriben los triggers del motor y la usa el portal); aquí solo se lee.
Para la línea de tiempo también se leen, solo para lectura, las otras dos bitácoras del motor (`historial_estatus` y
`movimiento_inventario`): son registros históricos que nadie modifica, no tablas de negocio de otro servicio.

Cada MON_INTERVALO segundos (configuracion.mon_intervalo_seg) un hilo pregunta /salud de todos los servicios (config.PUERTOS) y guarda
estado, tiempo, versión y dependencias. Con dos procesos en el contenedor, un candado en Redis hace que solo uno verifique por ronda; si
Redis falla igual se verifica (que Redis esté caído es justo lo que hay que ver). Una verificación abre y cierra alertas sola:
servicio caído, degradado, dependencia con falla, latencia alta y porcentaje alto de errores 5xx (MongoDB, metricas_servicio).
"""
import datetime as dt
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import redis
from flask import g, request

from comun import config, supuestos as sup
from comun.base import (crear_app, documentar, filtro_entero, filtro_fecha, filtro_opcion, leer_cuerpo, leer_paginacion, lista,
                        paginacion, requiere, responder)
from comun.base_errores import ErrorApi, conflicto, filtro_invalido, no_encontrado
from comun.clientes import llamar
from comun.datos import ahora, como_json, conexion, consultar, mongo, r_cache
from comun.formatos import ZONA, fecha
from comun.validar import Campo, validar

app = crear_app("auditoria-monitoreo", "Microhubs · Auditoría y monitoreo",
                "Bitácora de auditoría, trazabilidad de pedidos, entregas e inventario y monitoreo central de la salud de todos los servicios.",
                5126, dependencias=("postgres", "redis", "mongo"))
P = config.PREFIJO

ACCIONES = ["alta", "modificacion", "baja_logica", "login_exitoso", "login_fallido", "logout", "bloqueo_cuenta", "desbloqueo",
            "acceso_denegado", "cambio_estado", "reasignacion", "reversion_administrativa", "movimiento_inventario", "cambio_configuracion", "descarga"]
ACCESOS = ["login_exitoso", "login_fallido", "logout", "bloqueo_cuenta", "desbloqueo", "acceso_denegado"]
TIPOS_ALERTA = ["servicio_caido", "servicio_degradado", "dependencia_caida", "latencia_alta", "errores_altos"]
DEPENDENCIAS = ["postgres", "redis", "mongo", "bucket"]
DEFECTOS = {"mon_intervalo_seg": 30.0, "mon_timeout_seg": 3.0, "mon_latencia_ms": 1000.0, "mon_errores_pct": 20.0,
            "mon_errores_ventana_min": 10.0, "mon_errores_min_peticiones": 20.0, "mon_retencion_dias": 7.0,
            "mon_disponibilidad_objetivo_pct": 99.0}
MAX_HORAS = 24 * 30
CLAVES_SUPUESTOS = list(DEFECTOS)


# --------------------------------------------------------------------
# Lógica pura (se prueba sin base de datos)
# --------------------------------------------------------------------
def clasificar(status, datos, error=None):
    """Respuesta de /salud → (estado, versión, dependencias, error).
    ok = 200 con estado ok; degradado = responde pero declara una dependencia con falla; caido = no responde o responde un 5xx sin cuerpo."""
    if status is None:
        return "caido", None, None, (error or "No responde.")[:200]
    cuerpo = datos if isinstance(datos, dict) else {}
    dep = cuerpo.get("dependencias") if isinstance(cuerpo.get("dependencias"), dict) else None
    version = cuerpo.get("version")
    if status == 200 and cuerpo.get("estado", "ok") == "ok":
        return "ok", version, dep, None
    if cuerpo.get("estado") == "degradado":
        return "degradado", version, dep, None
    if status >= 500:
        return "caido", None, None, f"Respondió HTTP {status} sin estado de salud."
    return "degradado", version, dep, f"Respondió HTTP {status}."


def dependencias_con_error(dep):
    return [k for k in DEPENDENCIAS if (dep or {}).get(k) == "error"]


def alertas_deseadas(servicio, estado, tiempo_ms, error, dep, tasa, umbrales):
    """Alertas que deben estar abiertas dada la última verificación: {tipo: (severidad, detalle)}."""
    out = {}
    if estado == "caido":
        out["servicio_caido"] = ("critica", f"{servicio} no responde. {error or ''}".strip())
    if estado == "degradado":
        out["servicio_degradado"] = ("alta", f"{servicio} responde pero no está sano. {error or ''}".strip())
        malas = dependencias_con_error(dep)
        if malas:
            out["dependencia_caida"] = ("alta", f"{servicio} no alcanza: {', '.join(malas)}.")
    if estado != "caido" and tiempo_ms is not None and tiempo_ms > umbrales["mon_latencia_ms"]:
        out["latencia_alta"] = ("media", f"/salud de {servicio} tardó {tiempo_ms:.0f} ms (umbral {umbrales['mon_latencia_ms']:.0f} ms).")
    if tasa and tasa["peticiones"] >= umbrales["mon_errores_min_peticiones"]:
        pct = 100.0 * tasa["errores_5xx"] / tasa["peticiones"]
        if pct >= umbrales["mon_errores_pct"]:
            out["errores_altos"] = ("alta", f"{servicio}: {tasa['errores_5xx']} de {tasa['peticiones']} peticiones terminaron en 5xx "
                                            f"({pct:.0f} %, umbral {umbrales['mon_errores_pct']:.0f} %) en los últimos "
                                            f"{umbrales['mon_errores_ventana_min']:.0f} minutos.")
    return out


def percentil(valores, p):
    """Percentil por rango más cercano (p en 0..100). None si no hay datos."""
    if not valores:
        return None
    orden = sorted(valores)
    k = max(0, min(len(orden) - 1, -(-len(orden) * p // 100) - 1))
    return orden[int(k)]


def texto_fallo(f):
    """Qué pasó en la última verificación que no salió bien: la dependencia que falló o el error."""
    if not f:
        return None
    malas = dependencias_con_error(f.get("dependencias"))
    if malas:
        return f"{f['estado']}: falla {', '.join(malas)}"[:200]
    return f"{f['estado']}: {f.get('error') or 'sin detalle'}"[:200]


def agrupar_dependencias_caidas(servicios):
    """[{dependencia, afectados}]: qué dependencia falla y a quiénes alcanza (una caída de PostgreSQL se ve una vez, no 26)."""
    por_dep = {}
    for s in servicios:
        for d in dependencias_con_error(s.get("dependencias")):
            por_dep.setdefault(d, []).append(s["servicio"])
    return [{"dependencia": d, "afectados": por_dep[d]} for d in DEPENDENCIAS if d in por_dep]


# --------------------------------------------------------------------
# Verificación de los servicios
# --------------------------------------------------------------------
def umbrales():
    return sup.valores(DEFECTOS)


def sondear(servicio, timeout):
    """Una petición a /salud. Nunca lanza: un servicio que no contesta es un resultado (caído), no un error."""
    t0 = time.perf_counter()
    status = datos = error = None
    try:
        status, datos = llamar(servicio, "GET", "salud", timeout=timeout)
    except ErrorApi as e:
        error = e.mensaje
    except Exception as e:                                   # noqa: BLE001 - cualquier fallo de red es «caído»
        error = f"{type(e).__name__}: {e}"
    ms = round((time.perf_counter() - t0) * 1000, 1)
    estado, version, dep, err = clasificar(status, datos, error)
    return {"servicio": servicio, "estado": estado, "http_status": status, "tiempo_ms": ms, "version": version,
            "dependencias": dep, "error": err}


def tasas_errores(minutos):
    """{servicio: {peticiones, errores_5xx, errores_4xx}} de metricas_servicio en la ventana. {} si MongoDB no responde."""
    try:
        db = mongo()
        if db is None:
            return {}
        desde = ahora() - dt.timedelta(minutes=minutos)
        filas = db.metricas_servicio.aggregate([
            {"$match": {"momento": {"$gte": desde}}},
            {"$group": {"_id": "$etiquetas.servicio", "peticiones": {"$sum": 1},
                        "errores_5xx": {"$sum": {"$cond": [{"$gte": ["$etiquetas.status", 500]}, 1, 0]}},
                        "errores_4xx": {"$sum": {"$cond": [{"$and": [{"$gte": ["$etiquetas.status", 400]},
                                                                      {"$lt": ["$etiquetas.status", 500]}]}, 1, 0]}}}}])
        return {f["_id"]: {"peticiones": f["peticiones"], "errores_5xx": f["errores_5xx"], "errores_4xx": f["errores_4xx"]} for f in filas}
    except Exception:                                        # noqa: BLE001 - las métricas son un apoyo, no un requisito
        return {}


def guardar_ronda(resultados, u, tasas):
    with conexion() as con, con.cursor() as cur:
        for r in resultados:
            cur.execute("INSERT INTO monitoreo_verificacion (servicio, estado, http_status, tiempo_ms, version, dependencias, error) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                        (r["servicio"], r["estado"], r["http_status"], r["tiempo_ms"], r["version"],
                         como_json(r["dependencias"]) if r["dependencias"] is not None else None, r["error"]))
            deseadas = alertas_deseadas(r["servicio"], r["estado"], r["tiempo_ms"], r["error"], r["dependencias"],
                                        tasas.get(r["servicio"]), u)
            for tipo, (severidad, detalle) in deseadas.items():
                cur.execute("INSERT INTO monitoreo_alerta (servicio, tipo, severidad, detalle) VALUES (%s,%s,%s,%s) "
                            "ON CONFLICT (servicio, tipo) WHERE cerrada_en IS NULL DO NOTHING",
                            (r["servicio"], tipo, severidad, detalle[:300]))
            cur.execute("UPDATE monitoreo_alerta SET cerrada_en = now() WHERE servicio = %s AND cerrada_en IS NULL "
                        "AND NOT (tipo = ANY(%s))", (r["servicio"], list(deseadas)))


def purgar(u):
    with conexion() as con, con.cursor() as cur:
        cur.execute("DELETE FROM monitoreo_verificacion WHERE verificado_en < now() - make_interval(days => %s)",
                    (int(u["mon_retencion_dias"]),))


def ronda(solo=None):
    """Verifica todos los servicios (o `solo`), guarda el resultado y concilia las alertas. Devuelve los resultados."""
    u = umbrales()
    objetivos = [solo] if solo else list(config.PUERTOS)
    with ThreadPoolExecutor(max_workers=8) as pool:
        resultados = list(pool.map(lambda s: sondear(s, u["mon_timeout_seg"]), objetivos))
    guardar_ronda(resultados, u, tasas_errores(int(u["mon_errores_ventana_min"])))
    return resultados


def _tomar_turno(clave, segundos):
    """True si este proceso debe hacer el trabajo. Sin Redis nadie coordina: se hace (duplicar una verificación no daña nada)."""
    try:
        return bool(r_cache.set(clave, str(os.getpid()), nx=True, ex=max(1, int(segundos))))
    except redis.RedisError:
        return True


def _ciclo():
    time.sleep(8)                                    # los demás servicios todavía están arrancando
    while True:
        try:
            u = umbrales()
            if _tomar_turno("monitoreo:ronda", u["mon_intervalo_seg"] - 2):
                ronda()
                if _tomar_turno("monitoreo:purga", 3600):
                    purgar(u)
        except Exception as e:                       # noqa: BLE001 - base caída: se reintenta sin tumbar el hilo
            print(json.dumps({"nivel": "WARN", "componente": "auditoria-monitoreo", "mensaje": f"ronda de verificación: {e}"}), flush=True)
        time.sleep(5)


if os.environ.get("MONITOR_AUTO", "1") == "1":
    threading.Thread(target=_ciclo, name="monitoreo-verificador", daemon=True).start()


# --------------------------------------------------------------------
# Presentación
# --------------------------------------------------------------------
def _dep(d):
    """Las dependencias tal como las informa el servicio, con las cuatro llaves del contrato."""
    if d is None:
        return None
    return {k: d.get(k, "no_aplica") for k in DEPENDENCIAS}


def _num(v, dec=1):
    return None if v is None else round(float(v), dec)


def _periodo(defecto_dias=7):
    desde, hasta = filtro_fecha("desde"), filtro_fecha("hasta")
    hoy = ahora().astimezone(ZONA).date()
    hasta = hasta or hoy
    desde = desde or hasta - dt.timedelta(days=defecto_dias)
    if desde > hasta:
        raise filtro_invalido("desde", "desde no puede ser posterior a hasta.")
    return desde, hasta


def _horas(defecto=24):
    v = (request.args.get("horas") or "").strip()
    if not v:
        return defecto
    if not v.isdigit() or not 1 <= int(v) <= MAX_HORAS:
        raise filtro_invalido("horas", f"horas debe ser un entero entre 1 y {MAX_HORAS}.")
    return int(v)


def _nombre_servicio(nombre):
    if nombre not in config.PUERTOS:
        raise no_encontrado("No existe ese servicio.")
    return nombre


def verificacion(f):
    return {"verificado_en": fecha(f["verificado_en"]), "estado": f["estado"], "http_status": f["http_status"],
            "tiempo_ms": _num(f["tiempo_ms"]), "version": f["version"], "dependencias": _dep(f["dependencias"]), "error": f["error"]}


def alerta(f):
    cierre = f["cerrada_en"]
    fin = cierre or ahora()
    return {"id": f["id"], "servicio": f["servicio"], "tipo": f["tipo"], "severidad": f["severidad"], "detalle": f["detalle"],
            "abierta_en": fecha(f["abierta_en"]), "cerrada_en": fecha(cierre), "duracion_seg": int((fin - f["abierta_en"]).total_seconds()),
            "reconocida": ({"por": {"id": f["reconocida_por"], "nombre": f.get("reconocida_nombre")}, "en": fecha(f["reconocida_en"])}
                           if f["reconocida_por"] else None)}


SQL_ALERTA = ("SELECT a.id, a.servicio, a.tipo, a.severidad, a.detalle, a.abierta_en, a.cerrada_en, a.reconocida_por, a.reconocida_en, "
              "trim(u.nombre || ' ' || COALESCE(u.apellidos, '')) AS reconocida_nombre "
              "FROM monitoreo_alerta a LEFT JOIN usuario u ON u.id = a.reconocida_por ")


# --------------------------------------------------------------------
# Monitoreo
# --------------------------------------------------------------------
@app.get(f"{P}/monitoreo/estado")
@requiere("monitoreo.ver")
def estado():
    u = umbrales()
    ultimas = {f["servicio"]: f for f in consultar(
        "SELECT DISTINCT ON (servicio) servicio, verificado_en, estado, http_status, tiempo_ms, version, dependencias, error "
        "FROM monitoreo_verificacion ORDER BY servicio, verificado_en DESC")}
    disp = {f["servicio"]: f for f in consultar(
        "SELECT servicio, count(*) AS n, count(*) FILTER (WHERE estado <> 'caido') AS responde, "
        "avg(tiempo_ms) FILTER (WHERE estado <> 'caido') AS promedio FROM monitoreo_verificacion "
        "WHERE verificado_en >= now() - interval '24 hours' GROUP BY servicio")}
    fallos = {f["servicio"]: f for f in consultar(
        "SELECT DISTINCT ON (servicio) servicio, verificado_en, estado, error, dependencias FROM monitoreo_verificacion "
        "WHERE estado <> 'ok' AND verificado_en >= now() - interval '24 hours' ORDER BY servicio, verificado_en DESC")}
    tasas = tasas_errores(60)
    ahora_ = ahora()
    servicios = []
    for nombre, puerto in config.PUERTOS.items():
        f = ultimas.get(nombre)
        d = disp.get(nombre)
        pct = round(100.0 * d["responde"] / d["n"], 2) if d and d["n"] else None
        t = tasas.get(nombre)
        servicios.append({
            "servicio": nombre, "puerto": puerto, "estado": f["estado"] if f else "sin_datos",
            "verificado_en": fecha(f["verificado_en"]) if f else None,
            "antiguedad_seg": int((ahora_ - f["verificado_en"]).total_seconds()) if f else None,
            "tiempo_ms": _num(f["tiempo_ms"]) if f else None, "version": f["version"] if f else None,
            "dependencias": _dep(f["dependencias"]) if f else None, "error": f["error"] if f else None,
            "peticiones_hora": t["peticiones"] if t else None, "errores_5xx_hora": t["errores_5xx"] if t else None,
            "disponibilidad_24h_pct": pct,
            "bajo_objetivo": bool(pct is not None and pct < u["mon_disponibilidad_objetivo_pct"]),
            "tiempo_promedio_ms": _num(d["promedio"]) if d else None,
            "ultimo_error": texto_fallo(fallos.get(nombre)),
            "ultimo_error_en": fecha(fallos[nombre]["verificado_en"]) if nombre in fallos else None})
    ultima = max((f["verificado_en"] for f in ultimas.values()), default=None)
    activo = bool(ultima and (ahora_ - ultima).total_seconds() <= 3 * u["mon_intervalo_seg"] + 5)
    cuenta = {e: sum(1 for s in servicios if s["estado"] == e) for e in ("ok", "degradado", "caido", "sin_datos")}
    abiertas = consultar("SELECT count(*) AS n FROM monitoreo_alerta WHERE cerrada_en IS NULL", una=True)["n"]
    return responder({
        "generado_en": fecha(ahora_),
        "resumen": {"total": len(servicios), "ok": cuenta["ok"], "degradados": cuenta["degradado"], "caidos": cuenta["caido"],
                    "sin_datos": cuenta["sin_datos"], "alertas_abiertas": abiertas, "monitor_activo": activo,
                    "intervalo_seg": int(u["mon_intervalo_seg"]), "ultima_ronda": fecha(ultima)},
        "servicios": servicios, "dependencias_caidas": agrupar_dependencias_caidas(servicios)},
        raiz="monitoreo_estado", items={"servicios": "servicio", "dependencias_caidas": "dependencia", "afectados": "servicio"})


@app.get(f"{P}/monitoreo/servicios/<nombre>/historial")
@requiere("monitoreo.ver")
def historial(nombre):
    _nombre_servicio(nombre)
    pagina, por, salto = leer_paginacion(defecto=50, maximo=200)
    horas = _horas(24)
    solo = filtro_opcion("estado", ["ok", "degradado", "caido"])
    where, args = ["servicio = %s", "verificado_en >= now() - make_interval(hours => %s)"], [nombre, horas]
    if solo:
        where.append("estado = %s"); args.append(solo)
    w = " AND ".join(where)
    total = consultar(f"SELECT count(*) AS n FROM monitoreo_verificacion WHERE {w}", args, una=True)["n"]
    filas = consultar(f"SELECT verificado_en, estado, http_status, tiempo_ms, version, dependencias, error FROM monitoreo_verificacion "
                      f"WHERE {w} ORDER BY verificado_en DESC, id DESC LIMIT %s OFFSET %s", (*args, por, salto))
    return lista(filas, paginacion(pagina, por, total), "verificacion", "monitoreo_historial", verificacion)


@app.get(f"{P}/monitoreo/disponibilidad")
@requiere("monitoreo.ver")
def disponibilidad():
    horas = _horas(24)
    u = umbrales()
    filas = {f["servicio"]: f for f in consultar(
        "SELECT servicio, count(*) AS n, count(*) FILTER (WHERE estado <> 'caido') AS responde, count(*) FILTER (WHERE estado = 'ok') AS plenas, "
        "count(*) FILTER (WHERE estado = 'caido') AS caidas, percentile_cont(0.5) WITHIN GROUP (ORDER BY tiempo_ms) AS p50, "
        "percentile_cont(0.95) WITHIN GROUP (ORDER BY tiempo_ms) AS p95, max(tiempo_ms) AS maximo "
        "FROM monitoreo_verificacion WHERE verificado_en >= now() - make_interval(hours => %s) GROUP BY servicio", (horas,))}
    salida = []
    for nombre in config.PUERTOS:
        f = filas.get(nombre)
        pct = round(100.0 * f["responde"] / f["n"], 2) if f else None
        salida.append({"servicio": nombre, "verificaciones": f["n"] if f else 0, "caidas": f["caidas"] if f else 0,
                       "disponibilidad_pct": pct, "salud_plena_pct": round(100.0 * f["plenas"] / f["n"], 2) if f else None,
                       "tiempo_p50_ms": _num(f["p50"]) if f else None, "tiempo_p95_ms": _num(f["p95"]) if f else None,
                       "tiempo_max_ms": _num(f["maximo"]) if f else None,
                       "bajo_objetivo": bool(pct is not None and pct < u["mon_disponibilidad_objetivo_pct"])})
    return responder({"horas": horas, "objetivo_pct": u["mon_disponibilidad_objetivo_pct"], "servicios": salida},
                     raiz="monitoreo_disponibilidad", items={"servicios": "servicio"})


@app.get(f"{P}/monitoreo/metricas")
@requiere("monitoreo.ver")
def metricas():
    v = (request.args.get("minutos") or "60").strip()
    if not v.isdigit() or not 1 <= int(v) <= 1440:
        raise filtro_invalido("minutos", "minutos debe ser un entero entre 1 y 1440.")
    minutos = int(v)
    db = mongo()
    if db is None:
        raise ErrorApi(503, "SERVICIO_NO_DISPONIBLE", "MongoDB no está configurado: no hay métricas.")
    try:
        desde = ahora() - dt.timedelta(minutes=minutos)
        docs = list(db.metricas_servicio.find({"momento": {"$gte": desde}}, {"duracion_ms": 1, "etiquetas.servicio": 1, "etiquetas.status": 1,
                                                                             "_id": 0}).limit(200000))
    except Exception:                                        # noqa: BLE001
        raise ErrorApi(503, "SERVICIO_NO_DISPONIBLE", "MongoDB no responde. Intenta más tarde.")
    por = {}
    for d in docs:
        e = d.get("etiquetas", {})
        x = por.setdefault(e.get("servicio", "?"), {"d": [], "e5": 0, "e4": 0})
        x["d"].append(d.get("duracion_ms", 0))
        st = e.get("status", 0)
        x["e5"] += st >= 500
        x["e4"] += 400 <= st < 500
    salida = []
    for nombre in config.PUERTOS:
        x = por.get(nombre)
        n = len(x["d"]) if x else 0
        salida.append({"servicio": nombre, "peticiones": n, "errores_5xx": x["e5"] if x else 0, "errores_4xx": x["e4"] if x else 0,
                       "tasa_5xx_pct": round(100.0 * x["e5"] / n, 2) if n else None,
                       "duracion_p50_ms": percentil(x["d"], 50) if x else None, "duracion_p95_ms": percentil(x["d"], 95) if x else None,
                       "duracion_p99_ms": percentil(x["d"], 99) if x else None})
    total = sum(s["peticiones"] for s in salida)
    return responder({"minutos": minutos, "peticiones_total": total, "servicios": salida}, raiz="monitoreo_metricas",
                     items={"servicios": "servicio"})


@app.get(f"{P}/monitoreo/alertas")
@requiere("monitoreo.ver")
def alertas():
    pagina, por, salto = leer_paginacion()
    estado_f = filtro_opcion("estado", ["abiertas", "cerradas", "todas"]) or "abiertas"
    servicio = (request.args.get("servicio") or "").strip()
    tipo = filtro_opcion("tipo", TIPOS_ALERTA)
    if servicio:
        _nombre_servicio(servicio)
    where, args = [], []
    if estado_f == "abiertas":
        where.append("a.cerrada_en IS NULL")
    elif estado_f == "cerradas":
        where.append("a.cerrada_en IS NOT NULL")
    if servicio:
        where.append("a.servicio = %s"); args.append(servicio)
    if tipo:
        where.append("a.tipo = %s"); args.append(tipo)
    w = (" WHERE " + " AND ".join(where)) if where else ""
    total = consultar(f"SELECT count(*) AS n FROM monitoreo_alerta a{w}", args, una=True)["n"]
    filas = consultar(f"{SQL_ALERTA}{w} ORDER BY (a.cerrada_en IS NULL) DESC, a.abierta_en DESC, a.id DESC LIMIT %s OFFSET %s", (*args, por, salto))
    return lista(filas, paginacion(pagina, por, total), "alerta", "monitoreo_alertas", alerta)


@app.post(f"{P}/monitoreo/alertas/<int:aid>/reconocer")
@requiere("monitoreo.operar")
def reconocer(aid):
    with conexion() as con, con.cursor() as cur:
        cur.execute("SELECT id, cerrada_en, reconocida_por FROM monitoreo_alerta WHERE id = %s FOR UPDATE", (aid,))
        f = cur.fetchone()
        if not f:
            raise no_encontrado("No existe esa alerta.")
        if f["cerrada_en"]:
            raise conflicto("Esa alerta ya se cerró sola: el servicio se recuperó.")
        if not f["reconocida_por"]:
            cur.execute("UPDATE monitoreo_alerta SET reconocida_por = %s, reconocida_en = now() WHERE id = %s", (g.usuario["id"], aid))
    return responder(alerta(consultar(f"{SQL_ALERTA}WHERE a.id = %s", (aid,), una=True)), raiz="monitoreo_alerta")


@app.post(f"{P}/monitoreo/verificaciones")
@requiere("monitoreo.operar")
def verificar_ahora():
    d = validar(leer_cuerpo("verificacion_nueva", obligatorio=False), [Campo("servicio", req=False, nulo=True, min_len=1, max_len=30)])
    solo = d.get("servicio")
    if solo:
        _nombre_servicio(solo)
    resultados = ronda(solo)
    cuenta = {e: sum(1 for r in resultados if r["estado"] == e) for e in ("ok", "degradado", "caido")}
    return responder({"verificados": len(resultados), "ok": cuenta["ok"], "degradados": cuenta["degradado"], "caidos": cuenta["caido"],
                      "servicios": [{"servicio": r["servicio"], "estado": r["estado"], "tiempo_ms": _num(r["tiempo_ms"]), "error": r["error"]}
                                    for r in resultados]},
                     201, raiz="monitoreo_verificacion", items={"servicios": "servicio"})


@app.get(f"{P}/monitoreo/supuestos")
@requiere("monitoreo.ver")
def supuestos():
    return responder({"datos": sup.listar(DEFECTOS)}, raiz="supuestos_monitoreo", items={"datos": "supuesto"})


# --------------------------------------------------------------------
# Auditoría
# --------------------------------------------------------------------
def _txt(v):
    if v is None:
        return None
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (dict, list)):
        v = json.dumps(v, ensure_ascii=False)
    return str(v)[:120]


def cambios(anteriores, nuevos):
    """[{campo, anterior, nuevo}] de lo que cambió. Nunca incluye material de credenciales."""
    ant, nue = anteriores or {}, nuevos or {}
    campos = sorted({*ant, *nue} - {"hash_contrasena"})
    campos = [c for c in campos if "contrasena" not in c and "hash" not in c]
    return [{"campo": c, "anterior": _txt(ant.get(c)), "nuevo": _txt(nue.get(c))} for c in campos[:12]]


def _quien(uid, nombre):
    return {"id": uid, "nombre": (nombre or "").strip() or None} if uid else None


def evento(f):
    return {"id": f["id"], "fecha": fecha(f["fecha"]), "usuario": _quien(f["usuario_id"], f["usuario_nombre"]),
            "correo_intento": f["correo_intento"], "ip_origen": f["ip"], "modulo": f["modulo"], "accion": f["accion"],
            "entidad": {"tipo": f["entidad"], "id": f["entidad_id"]} if f["entidad"] else None, "exitoso": f["exitoso"],
            "detalle": f["detalle"], "cambios": cambios(f["valores_anteriores"], f["valores_nuevos"])}


SQL_AUDITORIA = ("SELECT a.id, a.fecha, a.usuario_id, trim(u.nombre || ' ' || COALESCE(u.apellidos, '')) AS usuario_nombre, a.correo_intento, "
                 "host(a.ip_origen) AS ip, a.modulo, a.accion::text AS accion, a.entidad, a.entidad_id, a.exitoso, a.detalle, "
                 "a.valores_anteriores, a.valores_nuevos FROM auditoria a LEFT JOIN usuario u ON u.id = a.usuario_id ")


def _texto_filtro(nombre, maximo=40):
    v = (request.args.get(nombre) or "").strip()
    if len(v) > maximo:
        raise filtro_invalido(nombre, f"{nombre} admite hasta {maximo} caracteres.")
    return v or None


def _limites(desde, hasta):
    """Rango [desde, hasta + 1 día) en la zona del negocio: «hasta» es inclusivo."""
    ini = dt.datetime.combine(desde, dt.time.min, tzinfo=ZONA)
    fin = dt.datetime.combine(hasta + dt.timedelta(days=1), dt.time.min, tzinfo=ZONA)
    return ini, fin


@app.get(f"{P}/auditoria")
@requiere("auditoria.ver")
def bitacora():
    pagina, por, salto = leer_paginacion()
    where, args = [], []
    uid = filtro_entero("usuario_id")
    if uid is not None:
        where.append("a.usuario_id = %s"); args.append(uid)
    accion = filtro_opcion("accion", ACCIONES)
    if accion:
        where.append("a.accion = %s::accion_auditoria"); args.append(accion)
    for nombre, col in (("modulo", "a.modulo"), ("entidad", "a.entidad"), ("entidad_id", "a.entidad_id")):
        v = _texto_filtro(nombre)
        if v:
            where.append(f"{col} = %s"); args.append(v)
    ok = (request.args.get("exitoso") or "").strip().lower()
    if ok:
        if ok not in ("true", "false"):
            raise filtro_invalido("exitoso", "exitoso debe ser true o false.")
        where.append("a.exitoso = %s"); args.append(ok == "true")
    q = _texto_filtro("q", 80)
    if q:
        where.append("(a.detalle ILIKE %s OR a.correo_intento ILIKE %s)"); args += [f"%{q}%"] * 2
    desde, hasta = filtro_fecha("desde"), filtro_fecha("hasta")
    if desde:
        where.append("a.fecha >= %s"); args.append(dt.datetime.combine(desde, dt.time.min, tzinfo=ZONA))
    if hasta:
        where.append("a.fecha < %s"); args.append(dt.datetime.combine(hasta + dt.timedelta(days=1), dt.time.min, tzinfo=ZONA))
    w = (" WHERE " + " AND ".join(where)) if where else ""
    total = consultar(f"SELECT count(*) AS n FROM auditoria a{w}", args, una=True)["n"]
    filas = consultar(f"{SQL_AUDITORIA}{w} ORDER BY a.fecha DESC, a.id DESC LIMIT %s OFFSET %s", (*args, por, salto))
    return lista(filas, paginacion(pagina, por, total), "evento", "bitacora", evento, items={"cambios": "cambio"})


@app.get(f"{P}/auditoria/accesos")
@requiere("auditoria.ver")
def accesos():
    desde, hasta = _periodo(7)
    ini, fin = _limites(desde, hasta)
    base = "FROM auditoria WHERE fecha >= %s AND fecha < %s"
    cuenta = {f["accion"]: f["n"] for f in consultar(
        f"SELECT accion::text AS accion, count(*) AS n {base} AND accion::text = ANY(%s) GROUP BY accion", (ini, fin, ACCESOS))}
    correos = consultar(f"SELECT correo_intento AS correo, count(*) AS intentos, max(fecha) AS ultimo {base} AND accion = 'login_fallido' "
                        f"AND correo_intento IS NOT NULL GROUP BY correo_intento ORDER BY intentos DESC, ultimo DESC LIMIT 5", (ini, fin))
    denegados = consultar(f"SELECT detalle, count(*) AS veces {base} AND accion = 'acceso_denegado' AND detalle IS NOT NULL "
                          f"GROUP BY detalle ORDER BY veces DESC, detalle LIMIT 5", (ini, fin))
    return responder({"desde": desde.isoformat(), "hasta": hasta.isoformat(), "totales": {a: cuenta.get(a, 0) for a in ACCESOS},
                      "correos_con_mas_fallos": [{"correo": c["correo"], "intentos": c["intentos"], "ultimo_intento": fecha(c["ultimo"])} for c in correos],
                      "denegados_frecuentes": [{"detalle": d["detalle"], "veces": d["veces"]} for d in denegados]},
                     raiz="accesos", items={"correos_con_mas_fallos": "correo", "denegados_frecuentes": "denegado"})


def _de_auditoria(f):
    e = evento(f)
    desc = f["detalle"] or "; ".join(f"{c['campo']}: {c['anterior']} → {c['nuevo']}" if c["anterior"] is not None else f"{c['campo']} = {c['nuevo']}"
                                      for c in e["cambios"][:4]) or f["accion"]
    return {"fecha": e["fecha"], "_t": f["fecha"], "origen": "auditoria", "accion": f["accion"], "descripcion": desc[:300],
            "usuario": e["usuario"], "entidad": e["entidad"], "cambios": e["cambios"]}


def _de_historial(f):
    quien = _quien(f["usuario_id"], f["usuario_nombre"])
    paso = f"{f['estado_anterior'] or 'nuevo'} → {f['estado_nuevo']}"
    por = "" if quien else f" (proceso {f['proceso']})"
    return {"fecha": fecha(f["fecha"]), "_t": f["fecha"], "origen": "estados", "accion": "cambio_estado",
            "descripcion": f"{paso}{por}" + (f". {f['motivo']}" if f["motivo"] else ""), "usuario": quien,
            "entidad": {"tipo": "pedido", "id": str(f["pedido_id"])}, "cambios": []}


def _de_movimiento(f):
    return {"fecha": fecha(f["fecha"]), "_t": f["fecha"], "origen": "inventario", "accion": "movimiento_inventario",
            "descripcion": f"{f['tipo']}: {f['cantidad']:+d} de producto {f['producto_id']} en microhub {f['microhub_id']} "
                           f"(existencia {f['existencia_resultante']})" + (f". {f['motivo']}" if f["motivo"] else ""),
            "usuario": _quien(f["usuario_id"], f["usuario_nombre"]),
            "entidad": {"tipo": "inventario", "id": f"{f['microhub_id']}-{f['producto_id']}"}, "cambios": []}


def _de_documentos(tipo, ident):
    """Metadatos de los archivos del bucket ligados al objeto (nunca el archivo)."""
    try:
        db = mongo()
        if db is None:
            return []
        docs = db.documentos.find({"referencia.tipo": tipo, "referencia.id": str(ident)},
                                  {"nombre": 1, "sha256": 1, "tamano_bytes": 1, "creado_en": 1, "subido_por": 1, "estado": 1}).limit(100)
        return [{"fecha": fecha(d["creado_en"]), "_t": d["creado_en"], "origen": "documentos", "accion": "documento_subido",
                 "descripcion": f"{d['nombre']} ({d.get('tamano_bytes', 0)} bytes, sha256 {d.get('sha256', '')[:12]}…)"
                                + (" [eliminado]" if d.get("estado") == "eliminado" else ""),
                 "usuario": _quien(d.get("subido_por"), None), "entidad": {"tipo": "documento", "id": str(d["_id"])}, "cambios": []}
                for d in docs]
    except Exception:                                        # noqa: BLE001 - sin MongoDB la línea de tiempo sigue sin las evidencias
        return []


def _linea_de_tiempo(tipo, ident, eventos):
    eventos.sort(key=lambda e: (e["_t"], e["origen"]))
    for e in eventos:
        e.pop("_t")
    return responder({"objeto": {"tipo": tipo, "id": str(ident)}, "total": len(eventos), "eventos": eventos[:500]},
                     raiz="trazabilidad", items={"eventos": "evento", "cambios": "cambio"})


NOMBRE_HIST = "trim(u.nombre || ' ' || COALESCE(u.apellidos, '')) AS usuario_nombre"


@app.get(f"{P}/auditoria/trazabilidad/pedido/<int:pid>")
@requiere("auditoria.ver")
def traza_pedido(pid):
    if not consultar("SELECT 1 AS x FROM pedido WHERE id = %s", (pid,), una=True):
        raise no_encontrado("No existe ese pedido.")
    ev = [_de_auditoria(f) for f in consultar(
        f"{SQL_AUDITORIA}WHERE (a.entidad = 'pedido' AND a.entidad_id = %s) OR (a.entidad = 'entrega' AND a.entidad_id IN "
        f"(SELECT id::text FROM entrega WHERE pedido_id = %s)) ORDER BY a.fecha, a.id LIMIT 500", (str(pid), pid))]
    ev += [_de_historial(f) for f in consultar(
        f"SELECT h.pedido_id, h.estado_anterior::text AS estado_anterior, h.estado_nuevo::text AS estado_nuevo, h.usuario_id, {NOMBRE_HIST}, "
        f"h.proceso, h.motivo, h.fecha FROM historial_estatus h LEFT JOIN usuario u ON u.id = h.usuario_id WHERE h.pedido_id = %s "
        f"ORDER BY h.fecha, h.id", (pid,))]
    ev += [_de_movimiento(f) for f in consultar(
        f"SELECT m.microhub_id, m.producto_id, m.tipo::text AS tipo, m.cantidad, m.existencia_resultante, m.motivo, m.usuario_id, m.fecha, "
        f"{NOMBRE_HIST} FROM movimiento_inventario m LEFT JOIN usuario u ON u.id = m.usuario_id "
        f"WHERE m.referencia_tipo = 'pedido' AND m.referencia_id = %s ORDER BY m.fecha, m.id LIMIT 500", (pid,))]
    ev += _de_documentos("pedido", pid)
    return _linea_de_tiempo("pedido", pid, ev)


@app.get(f"{P}/auditoria/trazabilidad/entrega/<int:eid>")
@requiere("auditoria.ver")
def traza_entrega(eid):
    f = consultar("SELECT pedido_id FROM entrega WHERE id = %s", (eid,), una=True)
    if not f:
        raise no_encontrado("No existe esa entrega.")
    ev = [_de_auditoria(x) for x in consultar(
        f"{SQL_AUDITORIA}WHERE a.entidad = 'entrega' AND a.entidad_id = %s ORDER BY a.fecha, a.id LIMIT 500", (str(eid),))]
    ev += _de_documentos("entrega", eid)
    return _linea_de_tiempo("entrega", eid, ev)


@app.get(f"{P}/auditoria/trazabilidad/inventario")
@requiere("auditoria.ver")
def traza_inventario():
    hub, prod = filtro_entero("microhub_id"), filtro_entero("producto_id")
    if hub is None or prod is None:
        raise filtro_invalido("microhub_id", "Indica microhub_id y producto_id.")
    if not consultar("SELECT 1 AS x FROM inventario WHERE microhub_id = %s AND producto_id = %s", (hub, prod), una=True):
        raise no_encontrado("Ese producto no tiene inventario en ese microhub.")
    ev = [_de_movimiento(f) for f in consultar(
        f"SELECT m.microhub_id, m.producto_id, m.tipo::text AS tipo, m.cantidad, m.existencia_resultante, m.motivo, m.usuario_id, m.fecha, "
        f"{NOMBRE_HIST} FROM movimiento_inventario m LEFT JOIN usuario u ON u.id = m.usuario_id "
        f"WHERE m.microhub_id = %s AND m.producto_id = %s ORDER BY m.fecha DESC, m.id DESC LIMIT 500", (hub, prod))]
    return _linea_de_tiempo("inventario", f"{hub}-{prod}", ev)


# --------------------------------------------------------------------
# Documentación
# --------------------------------------------------------------------
PAG = [("pagina", "query", "integer", "Página"), ("por_pagina", "query", "integer", "1 a 100 (200 en el historial)")]
documentar(app, "GET", f"{P}/auditoria", "Bitácora de auditoría", permisos=["auditoria.ver"], parametros=PAG + [
    ("usuario_id", "query", "integer", "Quién hizo el cambio"), ("modulo", "query", "string", "pedidos, inventario, usuarios…"),
    ("accion", "query", "string", "alta | modificacion | cambio_estado | login_fallido | acceso_denegado …"),
    ("entidad", "query", "string", "Tabla afectada: pedido, entrega, inventario…"), ("entidad_id", "query", "string", "Id del registro"),
    ("exitoso", "query", "boolean", "Solo los que salieron bien o mal"), ("q", "query", "string", "Texto en el detalle o en el correo del intento"),
    ("desde", "query", "string", "AAAA-MM-DD"), ("hasta", "query", "string", "AAAA-MM-DD, incluido")],
    descripcion="La bitácora es de solo escritura (RN31): ni el administrador puede cambiar una entrada. Los valores de contraseñas nunca aparecen.",
    respuestas={200: ("Página de eventos", "BitacoraLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/auditoria/accesos", "Accesos al sistema", permisos=["auditoria.ver"],
           parametros=[("desde", "query", "string", "AAAA-MM-DD (por omisión, hace 7 días)"), ("hasta", "query", "string", "AAAA-MM-DD (por omisión, hoy)")],
           respuestas={200: ("Totales del periodo, correos con más fallos y accesos denegados frecuentes", "Accesos.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/auditoria/trazabilidad/pedido/{{id}}", "Línea de tiempo de un pedido", permisos=["auditoria.ver"],
           parametros=[("id", "path", "integer", "Id del pedido")],
           descripcion="Une la bitácora del pedido y de sus entregas, los cambios de estado, los movimientos de inventario que causó y los archivos "
                       "guardados en el bucket (solo sus datos), en orden de fecha.",
           respuestas={200: ("Eventos en orden", "Trazabilidad.ok")}, errores=[403, 404])
documentar(app, "GET", f"{P}/auditoria/trazabilidad/entrega/{{id}}", "Línea de tiempo de una entrega", permisos=["auditoria.ver"],
           parametros=[("id", "path", "integer", "Id de la entrega")], respuestas={200: ("Eventos en orden", "Trazabilidad.ok")}, errores=[403, 404])
documentar(app, "GET", f"{P}/auditoria/trazabilidad/inventario", "Movimientos de un producto en un microhub", permisos=["auditoria.ver"],
           parametros=[("microhub_id", "query", "integer", "Microhub"), ("producto_id", "query", "integer", "Producto")],
           respuestas={200: ("Movimientos, el más reciente primero", "Trazabilidad.ok")}, errores=[400, 403, 404])
documentar(app, "GET", f"{P}/monitoreo/estado", "Panel de monitoreo", permisos=["monitoreo.ver"],
           descripcion="Último estado de cada servicio (ok, degradado, caído o sin datos), cuándo se verificó, cuánto tardó, su versión, sus dependencias, "
                       "peticiones y errores 5xx de la última hora y disponibilidad de 24 h. `dependencias_caidas` agrupa por dependencia a los servicios "
                       "alcanzados. `monitor_activo` es falso si el verificador dejó de correr.",
           respuestas={200: ("Estado de todos los servicios", "MonitoreoEstado.ok")}, errores=[403])
documentar(app, "GET", f"{P}/monitoreo/servicios/{{nombre}}/historial", "Historial de verificaciones de un servicio", permisos=["monitoreo.ver"],
           parametros=PAG + [("nombre", "path", "string", "Nombre del servicio, p. ej. pedidos"), ("horas", "query", "integer", "1 a 720 (24 por omisión)"),
                             ("estado", "query", "string", "ok | degradado | caido")],
           respuestas={200: ("Verificaciones, la más reciente primero", "MonitoreoHistorial.ok")}, errores=[400, 403, 404])
documentar(app, "GET", f"{P}/monitoreo/disponibilidad", "Disponibilidad por servicio", permisos=["monitoreo.ver"],
           parametros=[("horas", "query", "integer", "1 a 720 (24 por omisión)")],
           descripcion="disponibilidad_pct = verificaciones en las que el servicio respondió; salud_plena_pct = en las que además todas sus "
                       "dependencias estaban bien.",
           respuestas={200: ("Disponibilidad y tiempos de /salud", "MonitoreoDisponibilidad.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/monitoreo/metricas", "Métricas de tráfico y errores", permisos=["monitoreo.ver"],
           parametros=[("minutos", "query", "integer", "1 a 1440 (60 por omisión)")],
           respuestas={200: ("Peticiones, errores y percentiles de duración", "MonitoreoMetricas.ok")}, errores=[400, 403, 503])
documentar(app, "GET", f"{P}/monitoreo/alertas", "Alertas", permisos=["monitoreo.ver"],
           parametros=PAG + [("estado", "query", "string", "abiertas (por omisión) | cerradas | todas"), ("servicio", "query", "string", "Nombre del servicio"),
                             ("tipo", "query", "string", "servicio_caido | servicio_degradado | dependencia_caida | latencia_alta | errores_altos")],
           respuestas={200: ("Página de alertas", "MonitoreoAlertaLista.ok")}, errores=[400, 403])
documentar(app, "POST", f"{P}/monitoreo/alertas/{{id}}/reconocer", "Reconocer una alerta", permisos=["monitoreo.operar"],
           parametros=[("id", "path", "integer", "Id de la alerta")], descripcion="Reconocer dos veces no cambia quién la tomó. Una alerta cerrada responde 409.",
           respuestas={200: ("Alerta reconocida", "MonitoreoAlerta.ok")}, errores=[403, 404, 409])
documentar(app, "POST", f"{P}/monitoreo/verificaciones", "Forzar una verificación", permisos=["monitoreo.operar"], cuerpo="MonitoreoVerificacionNueva.ok",
           descripcion="Sin cuerpo (o sin `servicio`) verifica todos los servicios; con `servicio`, solo ese. Guarda el resultado y concilia las alertas.",
           respuestas={201: ("Resultado de la ronda", "MonitoreoVerificacion.ok")}, errores=[400, 403, 404, 422])
documentar(app, "GET", f"{P}/monitoreo/supuestos", "Umbrales del monitoreo y su justificación", permisos=["monitoreo.ver"],
           respuestas={200: ("Valor, origen y cómo calibrar cada umbral", "SupuestosMonitoreo.ok")}, errores=[403])
