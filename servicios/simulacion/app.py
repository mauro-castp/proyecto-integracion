"""
Servicio de simulación · puerto 5121 · contrato v1

  POST /api/v1/simulacion/ejecuciones               pone en cola una simulación de la operación (202)
  GET  /api/v1/simulacion/ejecuciones               ejecuciones (estado, microhub_id, candidato_id)
  GET  /api/v1/simulacion/ejecuciones/{id}          una ejecución: entrada, resultados, huella y si se reproduce
  POST /api/v1/simulacion/ejecuciones/{id}/cancelar cancela una ejecución en cola o en curso
  POST /api/v1/simulacion/ejecuciones/{id}/repetir  la misma entrada y la misma semilla; debe dar la misma huella (202)
  GET  /api/v1/simulacion/comparacion               varias ejecuciones terminadas lado a lado
  GET  /api/v1/simulacion/supuestos                 de dónde sale cada valor y cómo se calibra

Responsabilidad única: qué tan estable es la operación de un microhub (o de una ubicación candidata) cuando la demanda varía
de un día a otro y falta personal. No calcula costos, demanda ni capacidad: al crear la ejecución pide esos números a
punto-equilibrio (que a su vez usa costos, demanda y cobertura) y a capacidad, y los guarda en la ejecución. Con esa foto de la
entrada y la semilla, el resultado es siempre el mismo.

Modelo (Monte Carlo, día por día, `replicas` repeticiones):
  · Demanda del día = pedidos_dia × índice del día de la semana × (1 + ruido normal de desviación `variacion_demanda`), y de ahí
    un conteo de Poisson. El índice semanal sale de demanda/patrones; si no hay historia suficiente, vale 1 todos los días.
  · Cada operador y cada repartidor falta ese día con probabilidad `ausentismo`. La capacidad del día sale de pc.capacidad con
    el personal presente.
  · Atendidos = menor de demanda y capacidad; lo demás se rechaza. Utilidad del día = atendidos × (ticket × margen bruto −
    costo variable) − costos fijos del mes ÷ días del mes.
  · Se reporta media y percentiles 10, 50 y 90 entre réplicas, la probabilidad de perder dinero y el porcentaje de días saturados.

Las ejecuciones corren en un hilo de fondo del propio servicio, que toma de la cola (FOR UPDATE SKIP LOCKED) una a la vez. Si el
proceso muere con una ejecución a medias, a los 5 minutos regresa a la cola (hasta 3 intentos) y luego queda como fallida.
La huella es el SHA-256 de los resultados: dos ejecuciones con la misma entrada y semilla tienen la misma huella.
"""
import datetime as dt
import hashlib
import json
import math
import os
import random
import threading
import time
import uuid

from flask import g, request

from comun import config, supuestos as sup
from comun.base import (crear_app, documentar, filtro_entero, filtro_opcion, leer_cuerpo, leer_paginacion, limitar_microhub, lista, paginacion,
                        requiere, responder)
from comun.base_errores import ErrorApi, conflicto, filtro_invalido, invalido, no_encontrado
from comun.calculo import pc
from comun.clientes import exigir, llamar, mapa
from comun.datos import auditar, como_json, conexion, consultar
from comun.formatos import ZONA, fecha
from comun.validar import Campo, validar

app = crear_app("simulacion", "Microhubs · Simulación",
                "Simulación Monte Carlo de la operación de un microhub o una ubicación candidata, con semilla, huella y ejecución en segundo plano.", 5121)
P = config.PREFIJO
VERSION_MODELO = "1.0"
DEFECTOS = {"sim_dias_defecto": 30.0, "sim_replicas_defecto": 200.0, "sim_ausentismo": 0.05, "sim_semilla_defecto": 2026.0, "sim_variacion_demanda": 0.10,
            "picking_pedidos_hora": 10.0, "packing_pedidos_hora": 20.0, "despacho_pedidos_hora": 30.0, "velocidad_reparto_kmh": 22.0,
            "tiempo_servicio_min": 4.0, "paradas_por_viaje": 3.0, "horas_turno": 10.0, "cap_distancia_entrega_km": 2.4, "umbral_utilizacion_riesgo": 85.0,
            "dias_operacion_mes": 30.0}
CLAVES_SUPUESTOS = list(DEFECTOS)
PARAMS_CAPACIDAD = ("picking_pedidos_hora", "packing_pedidos_hora", "despacho_pedidos_hora", "velocidad_reparto_kmh", "tiempo_servicio_min",
                    "paradas_por_viaje", "horas_turno")
MAX_TRABAJO = 200_000                  # días × réplicas por ejecución
ESTADOS = ["en_cola", "ejecutando", "terminada", "fallida", "cancelada"]
MINUTOS_PARA_RECUPERAR = 5
MAX_INTENTOS = 3
METRICAS = [("utilidad", "Utilidad del periodo", "MXN"), ("ingreso", "Ingreso del periodo", "MXN"), ("atendidos", "Pedidos atendidos", "pedidos"),
            ("rechazados", "Pedidos rechazados por falta de capacidad", "pedidos"), ("utilizacion_pct", "Utilización de la capacidad", "%"),
            ("dias_saturados", "Días saturados", "días")]
ITEMS = {"metricas": "metrica", "serie": "dia", "lectura": "motivo", "indice_semanal": "indice", "supuestos_usados": "supuesto", "datos": "ejecucion",
         "ejecuciones": "ejecucion", "origen_de_datos": "dato"}


# --------------------------------------------------------------------
# Modelo (funciones puras: misma entrada y semilla, mismo resultado)
# --------------------------------------------------------------------
def poisson(rng, media):
    """Conteo de Poisson. Knuth hasta 30; con más, aproximación normal (la diferencia ya es despreciable)."""
    if media <= 0:
        return 0
    if media >= 30:
        return max(int(round(rng.gauss(media, math.sqrt(media)))), 0)
    limite, k, p = math.exp(-media), 0, 1.0
    while True:
        p *= rng.random()
        if p <= limite:
            return k
        k += 1


def percentil(ordenados, q):
    """Percentil q (0 a 100) con interpolación lineal. `ordenados` ya viene de menor a mayor."""
    if not ordenados:
        return 0.0
    if len(ordenados) == 1:
        return float(ordenados[0])
    pos = (len(ordenados) - 1) * q / 100
    bajo, alto = int(math.floor(pos)), int(math.ceil(pos))
    return float(ordenados[bajo] + (ordenados[alto] - ordenados[bajo]) * (pos - bajo))


class Capacidades:
    """Capacidad diaria según el personal presente; se guarda lo ya calculado porque hay pocas combinaciones."""

    def __init__(self, e):
        self.e, self.cache = e, {}

    def dia(self, operadores, repartidores):
        k = (operadores, repartidores)
        if k not in self.cache:
            e = self.e
            self.cache[k] = pc.capacidad(operadores, repartidores, e["distancia_km"], e.get("capacidad_fisica"), e["horas"], e["modelo"])["capacidad_dia"]
        return self.cache[k]


def una_replica(rng, e, caps):
    """Simula `dias` días. Devuelve los totales y, día por día, demanda, atendidos y utilidad."""
    margen_pedido = e["ticket"] * e["margen_bruto"] - e["costo_variable_pedido"]
    fijo_dia = e["costos_fijos_mes"] / e["dias_mes"]
    riesgo = e["modelo"]["umbral_utilizacion_riesgo"] / 100
    tot = {"utilidad": 0.0, "ingreso": 0.0, "atendidos": 0, "rechazados": 0, "demanda": 0, "capacidad": 0.0, "dias_saturados": 0}
    por_dia = []
    for d in range(e["dias"]):
        indice = e["indice_semanal"][(e["dia_inicio"] - 1 + d) % 7]
        ruido = max(rng.gauss(1.0, e["variacion_demanda"]), 0.2) if e["variacion_demanda"] > 0 else 1.0
        demanda = poisson(rng, e["pedidos_dia"] * indice * ruido)
        ops = sum(1 for _ in range(e["operadores"]) if rng.random() >= e["ausentismo"])
        reps = sum(1 for _ in range(e["repartidores"]) if rng.random() >= e["ausentismo"])
        cap = caps.dia(ops, reps)
        atendidos = min(demanda, int(cap))
        utilidad = atendidos * margen_pedido - fijo_dia
        tot["utilidad"] += utilidad
        tot["ingreso"] += atendidos * e["ticket"]
        tot["atendidos"] += atendidos
        tot["rechazados"] += demanda - atendidos
        tot["demanda"] += demanda
        tot["capacidad"] += cap
        if demanda > 0 and (cap <= 0 or demanda > cap * riesgo):
            tot["dias_saturados"] += 1
        por_dia.append((demanda, atendidos, utilidad))
    tot["utilizacion_pct"] = 100 * tot["demanda"] / tot["capacidad"] if tot["capacidad"] > 0 else 100.0
    return tot, por_dia


def r4(x):
    return round(float(x), 4)


def simular(e, semilla, replicas, cancelada=None):
    """Corre todas las réplicas y resume. Cada réplica usa su propio generador (semilla, número de réplica): agregar
    réplicas no cambia las anteriores. `cancelada()` se consulta cada 25 réplicas; si responde True devuelve None."""
    caps = Capacidades(e)
    totales = []
    acum = [[0.0, 0.0, 0.0] for _ in range(e["dias"])]
    for r in range(replicas):
        if cancelada and r % 25 == 0 and cancelada():
            return None
        rng = random.Random(semilla * 1_000_003 + r)
        t, por_dia = una_replica(rng, e, caps)
        totales.append(t)
        corrida = 0.0
        for i, (dem, ate, ut) in enumerate(por_dia):
            corrida += ut
            acum[i][0] += dem; acum[i][1] += ate; acum[i][2] += corrida
    metricas = []
    for clave, etiqueta, unidad in METRICAS:
        v = sorted(t[clave] for t in totales)
        metricas.append({"clave": clave, "etiqueta": etiqueta, "unidad": unidad, "media": r4(sum(v) / len(v)), "p10": r4(percentil(v, 10)),
                         "p50": r4(percentil(v, 50)), "p90": r4(percentil(v, 90)), "minimo": r4(v[0]), "maximo": r4(v[-1])})
    por_clave = {m["clave"]: m for m in metricas}
    perdida = 100 * sum(1 for t in totales if t["utilidad"] < 0) / len(totales)
    saturados = 100 * por_clave["dias_saturados"]["media"] / e["dias"]
    # Contraste: el mismo escenario sin variación, sin ausentismo y con la demanda promedio.
    cap_plena = caps.dia(e["operadores"], e["repartidores"])
    margen_pedido = e["ticket"] * e["margen_bruto"] - e["costo_variable_pedido"]
    det = (min(e["pedidos_dia"], cap_plena) * margen_pedido - e["costos_fijos_mes"] / e["dias_mes"]) * e["dias"]
    media = por_clave["utilidad"]["media"]
    lectura = [f"En {replicas} réplicas de {e['dias']} días, la utilidad media fue de {media:,.0f} MXN (P10 {por_clave['utilidad']['p10']:,.0f}, "
               f"P90 {por_clave['utilidad']['p90']:,.0f}).",
               f"Hubo pérdida en {perdida:.1f} % de las réplicas y {saturados:.1f} % de los días estuvieron saturados.",
               (f"Faltó capacidad: se rechazaron en promedio {por_clave['rechazados']['media']:,.0f} pedidos en el periodo."
                if por_clave["rechazados"]["media"] >= 1 else "La capacidad alcanzó para casi toda la demanda.")]
    if perdida >= 50:
        lectura.append("Con estos supuestos, lo más probable es perder dinero.")
    elif perdida >= 10:
        lectura.append("La operación gana en promedio, pero con riesgo real de perder; conviene más margen de seguridad.")
    else:
        lectura.append("La operación es estable ante la variación de la demanda y el ausentismo supuestos.")
    serie = [{"dia": i + 1, "demanda_media": r4(a[0] / replicas), "atendidos_media": r4(a[1] / replicas), "utilidad_acumulada_media": r4(a[2] / replicas)}
             for i, a in enumerate(acum)]
    return {"dias": e["dias"], "replicas": replicas, "metricas": metricas, "prob_perdida_pct": r4(perdida), "dias_saturados_pct": r4(saturados),
            "contraste": {"utilidad_sin_variacion": r4(det), "utilidad_media": r4(media), "diferencia": r4(media - det),
                          "capacidad_dia_con_todo_el_personal": r4(cap_plena)},
            "lectura": lectura, "serie": serie}


def huella_de(resultados):
    return hashlib.sha256(json.dumps(resultados, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


# --------------------------------------------------------------------
# Entrada: se junta una sola vez, al crear la ejecución
# --------------------------------------------------------------------
def parametros():
    return sup.valores(DEFECTOS)


def hoy():
    return dt.datetime.now(ZONA).date()


def indice_semanal():
    """Índice de cada día de la semana (lunes = 1) de la demanda observada. Plano si no hay historia suficiente."""
    try:
        status, datos = llamar("demanda", "GET", "demanda/patrones")
    except ErrorApi:
        return [1.0] * 7, "plano_sin_servicio"
    if status != 200 or not isinstance(datos, dict) or not datos.get("suficiente"):
        return [1.0] * 7, "plano_sin_historia"
    por_dia = {x["dia"]: x["indice"] for x in datos["semanal"]}
    return [float(por_dia.get(i, 1.0)) for i in range(1, 8)], "demanda"


def reunir_entrada(d, p):
    """La foto completa de la entrada. Lo que el usuario escribe sustituye a lo que vendría de otro servicio."""
    mh, cand = d.get("microhub_id"), d.get("candidato_id")
    if mh and cand:
        raise invalido("candidato_id", "Indica microhub_id o candidato_id, no los dos.")
    origen, objeto = {}, {"tipo": "manual", "id": None, "nombre": None}
    if mh:
        hubs = mapa("microhubs", "microhubs")
        if mh not in hubs:
            raise no_encontrado("No existe ese microhub.")
        objeto = {"tipo": "microhub", "id": mh, "nombre": hubs[mh]["nombre"]}
    elif cand:
        objeto = {"tipo": "candidato", "id": cand, "nombre": None}
    e = {}
    campos_peq = ("pedidos_dia", "ticket", "margen_bruto", "costos_fijos", "costo_variable_pedido")
    if objeto["tipo"] == "manual":
        faltan = [c for c in ("pedidos_dia", "ticket", "costos_fijos", "costo_variable_pedido", "operadores", "repartidores") if d.get(c) is None]
        if faltan:
            raise ErrorApi(422, "VALIDACION", "Sin microhub ni candidato hay que indicar todos los datos del escenario.",
                           [{"campo": c, "mensaje": "Es obligatorio sin microhub ni candidato."} for c in faltan])
        e.update(pedidos_dia=float(d["pedidos_dia"]), ticket=float(d["ticket"]), costos_fijos_mes=float(d["costos_fijos"]),
                 costo_variable_pedido=float(d["costo_variable_pedido"]),
                 margen_bruto=float(d["margen_bruto"]) if d.get("margen_bruto") is not None else p.get("margen_bruto_default", 0.28), dias_mes=p["dias_operacion_mes"])
        origen.update({c: "manual" for c in campos_peq})
    else:
        cuerpo = {("microhub_id" if objeto["tipo"] == "microhub" else "candidato_id"): objeto["id"]}
        cuerpo.update({c: d[c] for c in campos_peq if d.get(c) is not None})
        calc = exigir("punto-equilibrio", "POST", "punto-equilibrio/calculos", cuerpo=cuerpo)
        ent = calc["entrada"]
        e.update(pedidos_dia=float(ent["pedidos_dia"]), ticket=float(ent["ticket"]), costos_fijos_mes=float(ent["costos_fijos_mes"]),
                 costo_variable_pedido=float(ent["costo_variable_pedido"]), margen_bruto=float(ent["margen_bruto"]), dias_mes=float(ent["dias_mes"]))
        origen.update({k: v for k, v in ent["origen"].items()})
        if not objeto["nombre"]:
            objeto["nombre"] = (calc.get("objeto") or {}).get("nombre")
    # Personal y capacidad
    recurso = None
    if objeto["tipo"] == "microhub" and (d.get("operadores") is None or d.get("repartidores") is None):
        recurso = exigir("capacidad", "GET", f"capacidad/microhubs/{objeto['id']}")
    for campo, fuente in (("operadores", "operadores"), ("repartidores", "repartidores")):
        if d.get(campo) is not None:
            e[campo], origen[campo] = int(d[campo]), "manual"
        elif recurso:
            e[campo], origen[campo] = int(recurso[fuente]), "capacidad"
        else:
            raise invalido(campo, "Una ubicación candidata necesita que indiques operadores y repartidores.")
    fisica = d.get("capacidad_fisica") if d.get("capacidad_fisica") is not None else (recurso or {}).get("capacidad_fisica")
    e["capacidad_fisica"] = int(fisica) if fisica else None
    origen["capacidad_fisica"] = "manual" if d.get("capacidad_fisica") is not None else ("capacidad" if recurso else "sin_dato")
    e["horas"] = float(d["horas"]) if d.get("horas") is not None else p["horas_turno"]
    e["distancia_km"] = float(d["distancia_km"]) if d.get("distancia_km") is not None else p["cap_distancia_entrega_km"]
    origen["horas"] = "manual" if d.get("horas") is not None else "configuracion"
    origen["distancia_km"] = "manual" if d.get("distancia_km") is not None else "configuracion"
    e["ausentismo"] = float(d["ausentismo"]) if d.get("ausentismo") is not None else p["sim_ausentismo"]
    e["variacion_demanda"] = float(d["variacion_demanda"]) if d.get("variacion_demanda") is not None else p["sim_variacion_demanda"]
    origen["ausentismo"] = "manual" if d.get("ausentismo") is not None else "configuracion"
    origen["variacion_demanda"] = "manual" if d.get("variacion_demanda") is not None else "configuracion"
    e["indice_semanal"], origen["indice_semanal"] = indice_semanal()
    e["dias"] = int(d["dias"]) if d.get("dias") else int(p["sim_dias_defecto"])
    e["dia_inicio"] = hoy().isoweekday()
    e["modelo"] = {k: p[k] for k in (*PARAMS_CAPACIDAD, "umbral_utilizacion_riesgo")}
    return objeto, e, origen


def entrada_salida(e, origen):
    return {"pedidos_dia": round(e["pedidos_dia"], 2), "ticket": e["ticket"], "margen_bruto": e["margen_bruto"], "costos_fijos_mes": e["costos_fijos_mes"],
            "costo_variable_pedido": e["costo_variable_pedido"], "dias_mes": e["dias_mes"], "operadores": e["operadores"], "repartidores": e["repartidores"],
            "capacidad_fisica": e["capacidad_fisica"], "horas": e["horas"], "distancia_km": e["distancia_km"], "ausentismo": e["ausentismo"],
            "variacion_demanda": e["variacion_demanda"], "indice_semanal": e["indice_semanal"], "dia_inicio": e["dia_inicio"],
            "origen_de_datos": [{"dato": k, "fuente": v} for k, v in (origen or {}).items()]}


# --------------------------------------------------------------------
# Ejecución en segundo plano
# --------------------------------------------------------------------
def recuperar_abandonadas():
    """Una ejecución que lleva más de 5 minutos 'ejecutando' perdió a su proceso: vuelve a la cola o, tras 3 intentos, falla."""
    with conexion() as con, con.cursor() as cur:
        cur.execute("UPDATE simulacion_ejecucion SET estado = 'en_cola', inicio_en = NULL WHERE estado = 'ejecutando' AND intentos < %s "
                    "AND inicio_en < now() - make_interval(mins => %s)", (MAX_INTENTOS, MINUTOS_PARA_RECUPERAR))
        cur.execute("UPDATE simulacion_ejecucion SET estado = 'fallida', fin_en = now(), error = 'El proceso se interrumpió y agotó los intentos.' "
                    "WHERE estado = 'ejecutando' AND intentos >= %s AND inicio_en < now() - make_interval(mins => %s)", (MAX_INTENTOS, MINUTOS_PARA_RECUPERAR))


def reclamar():
    with conexion() as con, con.cursor() as cur:
        cur.execute("UPDATE simulacion_ejecucion SET estado = 'ejecutando', inicio_en = now(), intentos = intentos + 1 "
                    "WHERE id = (SELECT id FROM simulacion_ejecucion WHERE estado = 'en_cola' ORDER BY creado_en FOR UPDATE SKIP LOCKED LIMIT 1) "
                    "RETURNING id, semilla, parametros")
        return cur.fetchone()


def esta_cancelada(eid):
    f = consultar("SELECT estado FROM simulacion_ejecucion WHERE id = %s", (eid,), una=True)
    return not f or f["estado"] != "ejecutando"


def ejecutar(f):
    eid = f["id"]
    try:
        snap = f["parametros"]
        res = simular(snap["entrada"], f["semilla"], snap["replicas"], lambda: esta_cancelada(eid))
        if res is None:
            return "cancelada"
        with conexion() as con, con.cursor() as cur:
            cur.execute("UPDATE simulacion_ejecucion SET estado = 'terminada', resultados = %s, huella = %s, fin_en = now(), error = NULL "
                        "WHERE id = %s AND estado = 'ejecutando'", (como_json(res), huella_de(res), eid))
        return "terminada"
    except Exception as ex:                                      # una ejecución mala no debe tumbar al trabajador
        with conexion() as con, con.cursor() as cur:
            cur.execute("UPDATE simulacion_ejecucion SET estado = 'fallida', fin_en = now(), error = %s WHERE id = %s AND estado = 'ejecutando'",
                        (f"{type(ex).__name__}: {ex}"[:500], eid))
        return "fallida"


def procesar_pendientes(maximo=50):
    """Corre las ejecuciones que están en cola. El hilo de fondo lo llama en ciclo; las pruebas lo llaman a mano."""
    recuperar_abandonadas()
    hechas = 0
    while hechas < maximo:
        f = reclamar()
        if not f:
            break
        ejecutar(f)
        hechas += 1
    return hechas


def _ciclo():
    while True:
        try:
            if procesar_pendientes() == 0:
                time.sleep(2)
        except Exception:                                        # base de datos caída: se reintenta sin ruido
            time.sleep(5)


if os.environ.get("SIM_TRABAJADOR", "1") == "1":
    threading.Thread(target=_ciclo, name="simulacion-trabajador", daemon=True).start()


# --------------------------------------------------------------------
# Presentación
# --------------------------------------------------------------------
SQL_EJECUCION = ("SELECT id, nombre, estado, microhub_id, candidato_id, semilla, version_modelo, parametros, resultados, huella, error, creado_por, "
                 "creado_en, inicio_en, fin_en FROM simulacion_ejecucion ")


def objeto_de(f):
    if f["microhub_id"]:
        return {"tipo": "microhub", "id": f["microhub_id"], "nombre": f["parametros"].get("objeto", {}).get("nombre")}
    if f["candidato_id"]:
        return {"tipo": "candidato", "id": f["candidato_id"], "nombre": f["parametros"].get("objeto", {}).get("nombre")}
    return {"tipo": "manual", "id": None, "nombre": None}


def reproducible(f):
    """Si esta ejecución repite a otra: ¿dieron la misma huella? None si no es repetición o falta alguna."""
    origen = f["parametros"].get("repeticion_de")
    if not origen or f["estado"] != "terminada":
        return None
    o = consultar("SELECT estado, huella FROM simulacion_ejecucion WHERE id = %s", (origen,), una=True)
    if not o or o["estado"] != "terminada":
        return None
    return o["huella"] == f["huella"]


def resumen_ejecucion(f):
    r = f["resultados"]
    utilidad = next((m for m in r["metricas"] if m["clave"] == "utilidad"), None) if r else None
    return {"id": str(f["id"]), "nombre": f["nombre"], "estado": f["estado"], "objeto": objeto_de(f), "semilla": f["semilla"],
            "dias": f["parametros"]["entrada"]["dias"], "replicas": f["parametros"]["replicas"],
            "utilidad_media": utilidad["media"] if utilidad else None, "prob_perdida_pct": r["prob_perdida_pct"] if r else None,
            "huella": f["huella"], "creado_en": fecha(f["creado_en"]), "fin_en": fecha(f["fin_en"])}


def ejecucion_completa(f):
    snap = f["parametros"]
    return {"id": str(f["id"]), "nombre": f["nombre"], "estado": f["estado"], "objeto": objeto_de(f), "semilla": f["semilla"], "version_modelo": f["version_modelo"],
            "dias": snap["entrada"]["dias"], "replicas": snap["replicas"], "entrada": entrada_salida(snap["entrada"], snap.get("origen")), "resultados": f["resultados"],
            "huella": f["huella"], "repeticion_de": snap.get("repeticion_de"), "reproducible": reproducible(f), "error": f["error"],
            "creado_por": f["creado_por"], "creado_en": fecha(f["creado_en"]), "inicio_en": fecha(f["inicio_en"]), "fin_en": fecha(f["fin_en"]),
            "supuestos_usados": snap.get("supuestos_usados", [])}


def _ejecucion(eid):
    try:
        uuid.UUID(str(eid))
    except ValueError:
        raise no_encontrado("No existe esa ejecución.")
    f = consultar(SQL_EJECUCION + "WHERE id = %s", (eid,), una=True)
    if not f:
        raise no_encontrado("No existe esa ejecución.")
    if f["microhub_id"]:
        limitar_microhub(f["microhub_id"])
    elif g.usuario["rol"] in ("operador", "supervisor"):
        raise ErrorApi(403, "PROHIBIDO", "Tu perfil solo puede ver simulaciones de su microhub.")
    return f


def encolar(nombre, objeto, e, origen, semilla, replicas, repeticion_de=None):
    p_sup = sup.usados({k: v for k, v in e["modelo"].items()} | {"sim_ausentismo": e["ausentismo"], "sim_variacion_demanda": e["variacion_demanda"]})
    snap = {"objeto": objeto, "entrada": e, "origen": origen, "replicas": replicas, "supuestos_usados": p_sup}
    if repeticion_de:
        snap["repeticion_de"] = str(repeticion_de)
    with conexion() as con, con.cursor() as cur:
        cur.execute("INSERT INTO simulacion_ejecucion (nombre, microhub_id, candidato_id, semilla, version_modelo, parametros, creado_por) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                    (nombre, objeto["id"] if objeto["tipo"] == "microhub" else None, objeto["id"] if objeto["tipo"] == "candidato" else None,
                     semilla, VERSION_MODELO, como_json(snap), g.usuario["id"]))
        eid = cur.fetchone()["id"]
    auditar("simulacion", "alta", f"Simulación en cola: semilla {semilla}, {replicas} réplicas, {e['dias']} días"
            + (f", repetición de {repeticion_de}." if repeticion_de else "."), "simulacion", str(eid))
    return eid


# --------------------------------------------------------------------
# Rutas
# --------------------------------------------------------------------
CAMPOS = [
    Campo("nombre", req=False, nulo=True, min_len=3, max_len=120), Campo("microhub_id", "int", req=False, nulo=True, minimo=1),
    Campo("candidato_id", "int", req=False, nulo=True, minimo=1), Campo("dias", "int", req=False, nulo=True, minimo=1, maximo=365),
    Campo("replicas", "int", req=False, nulo=True, minimo=10, maximo=2000), Campo("semilla", "int", req=False, nulo=True, minimo=0, maximo=2_147_483_647),
    Campo("pedidos_dia", "num", req=False, nulo=True, minimo=0, maximo=100000), Campo("ticket", "num", req=False, nulo=True, minimo=1, maximo=100000),
    Campo("margen_bruto", "num", req=False, nulo=True, minimo=0, maximo=1), Campo("costos_fijos", "num", req=False, nulo=True, minimo=0, maximo=100_000_000),
    Campo("costo_variable_pedido", "num", req=False, nulo=True, minimo=0, maximo=100000), Campo("operadores", "int", req=False, nulo=True, minimo=1, maximo=50),
    Campo("repartidores", "int", req=False, nulo=True, minimo=1, maximo=50), Campo("capacidad_fisica", "int", req=False, nulo=True, minimo=1, maximo=100000),
    Campo("horas", "num", req=False, nulo=True, minimo=1, maximo=24), Campo("distancia_km", "num", req=False, nulo=True, minimo=0, maximo=100),
    Campo("ausentismo", "num", req=False, nulo=True, minimo=0, maximo=0.5), Campo("variacion_demanda", "num", req=False, nulo=True, minimo=0, maximo=1)]


@app.post(f"{P}/simulacion/ejecuciones")
@requiere("simulacion.ejecutar")
def crear():
    d = validar(leer_cuerpo("simulacion_nueva"), CAMPOS)
    if d.get("microhub_id"):
        limitar_microhub(d["microhub_id"])
    elif g.usuario["rol"] in ("operador", "supervisor"):
        raise ErrorApi(403, "PROHIBIDO", "Tu perfil solo puede simular su propio microhub.")
    p = parametros()
    objeto, e, origen = reunir_entrada(d, p)
    replicas = int(d["replicas"]) if d.get("replicas") else int(p["sim_replicas_defecto"])
    if e["dias"] * replicas > MAX_TRABAJO:
        raise ErrorApi(422, "VALIDACION", f"Días × réplicas no puede pasar de {MAX_TRABAJO:,}; pediste {e['dias'] * replicas:,}.",
                       [{"campo": "replicas", "mensaje": f"Reduce los días o las réplicas (máximo {MAX_TRABAJO:,} entre las dos)."}])
    semilla = int(d["semilla"]) if d.get("semilla") is not None else int(p["sim_semilla_defecto"])
    nombre = d.get("nombre") or f"Simulación de {objeto['nombre'] or 'escenario manual'} {hoy().isoformat()}"
    eid = encolar(nombre, objeto, e, origen, semilla, replicas)
    return responder(ejecucion_completa(_ejecucion(eid)), 202, raiz="simulacion_ejecucion", items=ITEMS, encabezados={"Location": f"{P}/simulacion/ejecuciones/{eid}"})


@app.get(f"{P}/simulacion/ejecuciones")
@requiere("simulacion.ver")
def ejecuciones():
    pagina, por, desde = leer_paginacion()
    estado = filtro_opcion("estado", ESTADOS)
    mh, cand = filtro_entero("microhub_id"), filtro_entero("candidato_id")
    propio = limitar_microhub(mh)
    where, args = ["TRUE"], []
    if g.usuario["rol"] in ("operador", "supervisor"):
        where.append("microhub_id = %s"); args.append(propio)
    elif mh:
        where.append("microhub_id = %s"); args.append(mh)
    for cond, valor in (("estado = %s", estado), ("candidato_id = %s", cand)):
        if valor:
            where.append(cond); args.append(valor)
    w = " AND ".join(where)
    total = consultar(f"SELECT count(*) AS n FROM simulacion_ejecucion WHERE {w}", args, una=True)["n"]
    filas = consultar(SQL_EJECUCION + f"WHERE {w} ORDER BY creado_en DESC, id LIMIT %s OFFSET %s", (*args, por, desde))
    return lista(filas, paginacion(pagina, por, total), "ejecucion", "simulacion_ejecuciones", resumen_ejecucion, items=ITEMS)


@app.get(f"{P}/simulacion/ejecuciones/<eid>")
@requiere("simulacion.ver")
def ejecucion_una(eid):
    return responder(ejecucion_completa(_ejecucion(eid)), raiz="simulacion_ejecucion", items=ITEMS)


@app.post(f"{P}/simulacion/ejecuciones/<eid>/cancelar")
@requiere("simulacion.ejecutar")
def cancelar(eid):
    f = _ejecucion(eid)
    with conexion() as con, con.cursor() as cur:
        cur.execute("UPDATE simulacion_ejecucion SET estado = 'cancelada', fin_en = now() WHERE id = %s AND estado IN ('en_cola', 'ejecutando')", (f["id"],))
        if cur.rowcount == 0:
            raise conflicto(f"Solo se cancela una ejecución en cola o en curso; esta está {f['estado']}.")
    auditar("simulacion", "cambio_estado", "Simulación cancelada por el usuario.", "simulacion", str(f["id"]))
    return responder(ejecucion_completa(_ejecucion(eid)), raiz="simulacion_ejecucion", items=ITEMS)


@app.post(f"{P}/simulacion/ejecuciones/<eid>/repetir")
@requiere("simulacion.ejecutar")
def repetir(eid):
    f = _ejecucion(eid)
    if f["estado"] != "terminada":
        raise conflicto(f"Solo se repite una ejecución terminada; esta está {f['estado']}.")
    snap = f["parametros"]
    nueva = encolar(f"Repetición de {f['nombre']}"[:120], snap["objeto"], snap["entrada"], snap["origen"], f["semilla"], snap["replicas"], f["id"])
    return responder(ejecucion_completa(_ejecucion(nueva)), 202, raiz="simulacion_ejecucion", items=ITEMS, encabezados={"Location": f"{P}/simulacion/ejecuciones/{nueva}"})


@app.get(f"{P}/simulacion/comparacion")
@requiere("simulacion.ver")
def comparacion():
    crudo = [x.strip() for x in (request.args.get("ids") or "").split(",") if x.strip()]
    if not 2 <= len(crudo) <= 5 or len(set(crudo)) != len(crudo):
        raise filtro_invalido("ids", "ids debe traer de 2 a 5 ejecuciones distintas separadas por coma.")
    filas = []
    for eid in crudo:
        f = _ejecucion(eid)
        if f["estado"] != "terminada":
            raise conflicto(f"La ejecución {eid} está {f['estado']}; solo se comparan las terminadas.")
        m = {x["clave"]: x for x in f["resultados"]["metricas"]}
        filas.append({"id": str(f["id"]), "nombre": f["nombre"], "objeto": objeto_de(f), "dias": f["resultados"]["dias"], "replicas": f["resultados"]["replicas"],
                      "utilidad_media": m["utilidad"]["media"], "utilidad_p10": m["utilidad"]["p10"], "utilidad_p90": m["utilidad"]["p90"],
                      "prob_perdida_pct": f["resultados"]["prob_perdida_pct"], "atendidos_media": m["atendidos"]["media"],
                      "rechazados_media": m["rechazados"]["media"], "dias_saturados_pct": f["resultados"]["dias_saturados_pct"], "huella": f["huella"]})
    mejor = max(filas, key=lambda x: (x["prob_perdida_pct"] < 50, x["utilidad_media"]))
    return responder({"ejecuciones": filas, "mejor_id": mejor["id"],
                      "criterio": "Mayor utilidad media entre las que pierden dinero en menos de la mitad de las réplicas."}, raiz="simulacion_comparacion", items=ITEMS)


@app.get(f"{P}/simulacion/supuestos")
@requiere("simulacion.ver")
def supuestos_simulacion():
    return responder({"datos": sup.listar(CLAVES_SUPUESTOS)}, raiz="supuestos_simulacion", items={"datos": "supuesto"})


# --------------------------------------------------------------------
# Documentación
# --------------------------------------------------------------------
PAG = [("pagina", "query", "integer", "Página (1…)"), ("por_pagina", "query", "integer", "1 a 100")]
ID = [("id", "path", "string", "Id de la ejecución (uuid)")]
documentar(app, "POST", f"{P}/simulacion/ejecuciones", "Poner una simulación en cola", permisos=["simulacion.ejecutar"], cuerpo="SimulacionNueva.ok",
           descripcion="Junta la entrada (punto-equilibrio y capacidad, o los números que escribas), la guarda en la ejecución y responde 202 con estado en_cola. "
                       "Un hilo del servicio la corre; consulta GET /simulacion/ejecuciones/{id} hasta que esté terminada. "
                       "Misma entrada y misma semilla dan la misma huella. Días × réplicas, máximo 200,000.",
           respuestas={202: ("Ejecución en cola, con su entrada", "SimulacionEjecucion.ok")}, errores=[400, 403, 404, 422, 503])
documentar(app, "GET", f"{P}/simulacion/ejecuciones", "Ejecuciones", permisos=["simulacion.ver"],
           parametros=PAG + [("estado", "query", "string", "en_cola | ejecutando | terminada | fallida | cancelada"), ("microhub_id", "query", "integer", "Microhub"),
                             ("candidato_id", "query", "integer", "Ubicación candidata")],
           respuestas={200: ("Página de ejecuciones, la más reciente primero", "SimulacionLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/simulacion/ejecuciones/{{id}}", "Una ejecución", permisos=["simulacion.ver"], parametros=ID,
           descripcion="Con la entrada completa y de dónde salió cada dato, los resultados (media y percentiles), la huella y, si repite a otra, si dio lo mismo.",
           respuestas={200: ("Ejecución", "SimulacionEjecucion.ok")}, errores=[403, 404])
documentar(app, "POST", f"{P}/simulacion/ejecuciones/{{id}}/cancelar", "Cancelar", permisos=["simulacion.ejecutar"], parametros=ID,
           respuestas={200: ("Ejecución cancelada", "SimulacionEjecucion.ok")}, errores=[403, 404, 409])
documentar(app, "POST", f"{P}/simulacion/ejecuciones/{{id}}/repetir", "Repetir una ejecución", permisos=["simulacion.ejecutar"], parametros=ID,
           descripcion="Crea otra con la misma entrada y la misma semilla. Al terminar, `reproducible` dice si la huella coincide.",
           respuestas={202: ("Nueva ejecución en cola", "SimulacionEjecucion.ok")}, errores=[403, 404, 409])
documentar(app, "GET", f"{P}/simulacion/comparacion", "Comparar ejecuciones", permisos=["simulacion.ver"],
           parametros=[("ids", "query", "string", "De 2 a 5 ids de ejecuciones terminadas, separados por coma")],
           respuestas={200: ("Un renglón por ejecución y la mejor", "SimulacionComparacion.ok")}, errores=[400, 403, 404, 409])
documentar(app, "GET", f"{P}/simulacion/supuestos", "Supuestos del modelo de simulación", permisos=["simulacion.ver"],
           descripcion="Valor, origen (medido, supuesto o normativo), justificación y cómo calibrarlo con datos reales.",
           respuestas={200: ("Supuestos documentados", "SupuestosSimulacion.ok")}, errores=[403])
