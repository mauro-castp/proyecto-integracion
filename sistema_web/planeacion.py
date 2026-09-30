"""
planeacion.py — Módulo de planeación y viabilidad de microhubs
Plataforma de Microhubs · Codex Innovations · Equipo 04

Responde: ¿conviene abrir un microhub aquí?, ¿cuántos pedidos necesita?,
¿qué capacidad y surtido requiere?, ¿cuánto cuesta la última milla?
Las fórmulas viven en planeacion_calc.py (puras y probadas); este archivo
solo consulta datos, arma los supuestos y presenta resultados.

Funciona en dos modos:
  · Docker (PostgreSQL): datos reales, candidatos y escenarios persistentes.
  · MODO_LOCAL=1 (app_local.py): datos de demostración en memoria
    (planeacion_demo.py), sin base de datos, para probar las pantallas.
"""
import csv
import io
import json
import os
from collections import defaultdict

from flask import (Blueprint, Response, abort, current_app, flash, g, redirect,
                   render_template, request, url_for)

import planeacion_calc as pc

MODO_LOCAL = os.environ.get("MODO_LOCAL", "0") == "1"

if MODO_LOCAL:
    import planeacion_demo as demo

    def requiere(*_permisos):
        return lambda f: f

    def auditar(*_a, **_k):
        return None

    def consultar(*_a, **_k):
        raise RuntimeError("Sin base de datos en modo local")

    con_actual = mensaje_de_error = r_sesion = None
else:
    from nucleo import auditar, con_actual, consultar, mensaje_de_error, r_sesion, requiere

planeacion_bp = plan = Blueprint("planeacion", __name__)
TZ = "America/Monterrey"
USUARIO_LOCAL = {"id": 0, "nombre": "Modo local", "rol": "administrador", "microhub_id": None}


def actor():
    return getattr(g, "usuario", None) or USUARIO_LOCAL


@plan.app_template_global("hay")
def hay(endpoint):
    """True si la ruta existe en esta aplicación (app_local no las tiene todas)."""
    return endpoint in current_app.view_functions


# --------------------------------------------------------------------
# Configuración e historial
# --------------------------------------------------------------------
def parametros():
    if MODO_LOCAL:
        return pc.con_defecto()
    filas = consultar("SELECT clave, valor FROM configuracion "
                      "WHERE ambito = 'global' AND clave = ANY(%s)", (list(pc.PARAMS),))
    return pc.con_defecto({f["clave"]: f["valor"] for f in filas})


def _num(v, d=0.0):
    try:
        return float(str(v).replace(",", "").replace("$", "").strip())
    except (TypeError, ValueError):
        return d


def historial(p):
    """Demanda histórica agregada: zona, hora, categoría, no atendida."""
    if MODO_LOCAL:
        return demo.historial()
    dias_ventana = int(p["ventana_analisis_dias"])
    filtro = "p.estado <> 'cancelado' AND p.creado_en >= now() - make_interval(days => %s)"
    dias = consultar(
        f"SELECT GREATEST(1, COALESCE(max(p.creado_en)::date - min(p.creado_en)::date, 0) + 1) AS dias "
        f"FROM pedido p WHERE {filtro}", (dias_ventana,), una=True)["dias"]
    zonas = consultar(
        f"SELECT z.id, z.clave, z.nombre, z.centroide_lat::float AS lat, z.centroide_lng::float AS lng, "
        f"       COALESCE(z.poblacion, 0) AS poblacion, count(p.id) AS pedidos, "
        f"       COALESCE(avg(p.subtotal), 0)::float AS ticket, "
        f"       COALESCE(sum(d.items), 0)::float / NULLIF(count(p.id), 0) AS productos_pedido "
        f"  FROM zona z LEFT JOIN pedido p ON p.zona_id = z.id AND {filtro} "
        f"  LEFT JOIN (SELECT pedido_id, sum(cantidad) AS items FROM pedido_detalle GROUP BY pedido_id) d "
        f"       ON d.pedido_id = p.id "
        f" WHERE z.estatus = 'activo' GROUP BY z.id ORDER BY z.id", (dias_ventana,))
    horas = consultar(
        f"SELECT p.zona_id, extract(hour FROM p.creado_en AT TIME ZONE '{TZ}')::int AS hora, count(*) AS n "
        f"  FROM pedido p WHERE {filtro} GROUP BY 1, 2", (dias_ventana,))
    no_at = {f["zona_id"]: f["n"] for f in consultar(
        "SELECT zona_id, count(*) AS n FROM demanda_no_atendida "
        "WHERE fecha >= now() - make_interval(days => %s) AND zona_id IS NOT NULL GROUP BY 1",
        (dias_ventana,))}
    no_at_tipo = consultar(
        "SELECT tipo::text AS tipo, count(*) AS n FROM demanda_no_atendida "
        "WHERE fecha >= now() - make_interval(days => %s) GROUP BY 1 ORDER BY 2 DESC", (dias_ventana,))
    categorias = consultar(
        f"SELECT c.nombre, sum(d.cantidad) AS unidades, sum(d.importe)::float AS ventas, "
        f"       count(DISTINCT p.id) AS pedidos "
        f"  FROM pedido p JOIN pedido_detalle d ON d.pedido_id = p.id "
        f"  JOIN producto pr ON pr.id = d.producto_id JOIN categoria c ON c.id = pr.categoria_id "
        f" WHERE {filtro} GROUP BY c.nombre ORDER BY 2 DESC", (dias_ventana,))
    por_zona_hora = defaultdict(lambda: [0] * 24)
    total_hora = [0] * 24
    for f in horas:
        por_zona_hora[f["zona_id"]][f["hora"]] += f["n"]
        total_hora[f["hora"]] += f["n"]

    def pico(h):
        if not any(h):
            return "—"
        i = max(range(23), key=lambda k: h[k] + h[k + 1])
        return f"{i}–{i + 2} h"

    filas = []
    for z in zonas:
        n_no = no_at.get(z["id"], 0)
        filas.append({**z, "pedidos_dia": round(z["pedidos"] / dias, 2),
                      "no_atendidos": n_no, "no_atendidos_dia": round(n_no / dias, 2),
                      "demanda_dia": z["pedidos"] / dias + n_no / dias,
                      "pico": pico(por_zona_hora[z["id"]]),
                      "productos_pedido": round(z["productos_pedido"] or 0, 1)})
    tot_p = sum(z["pedidos"] for z in zonas)
    ticket = (sum(z["ticket"] * z["pedidos"] for z in zonas) / tot_p) if tot_p else 0.0
    prod_ped = (sum((z["productos_pedido"] or 0) * z["pedidos"] for z in zonas) / tot_p) if tot_p else 0.0
    return {"dias": dias, "zonas": filas, "horas": total_hora, "pico": pico(total_hora),
            "no_atendida_tipo": no_at_tipo, "categorias": categorias,
            "pedidos": tot_p, "pedidos_dia": round(tot_p / dias, 2), "ticket": round(ticket, 2),
            "productos_pedido": round(prod_ped, 1),
            "no_atendidos": sum(no_at.values()), "ventana": dias_ventana}


def microhubs_activos():
    if MODO_LOCAL:
        return demo.HUBS
    return consultar("SELECT id, clave, nombre, latitud::float AS lat, longitud::float AS lng, "
                     "COALESCE(radio_km, 1.5)::float AS radio_km FROM microhub "
                     "WHERE estatus = 'activo' ORDER BY clave")


def candidatos(solo_activos=True):
    if MODO_LOCAL:
        return [c for c in demo.candidatos() if c["estatus"] == "activo" or not solo_activos]
    return consultar(
        "SELECT c.*, z.nombre AS zona, c.latitud::float AS lat, c.longitud::float AS lng "
        "FROM ubicacion_candidata c JOIN zona z ON z.id = c.zona_id "
        + ("WHERE c.estatus = 'activo' " if solo_activos else "") + "ORDER BY c.clave")


def get_candidato(cid):
    return next((c for c in candidatos(False) if c["id"] == cid), None)


def zonas_catalogo():
    if MODO_LOCAL:
        return [{"id": z["id"], "nombre": z["nombre"]} for z in demo.historial()["zonas"]]
    return consultar("SELECT id, nombre FROM zona WHERE estatus='activo' ORDER BY nombre")


def evaluar_candidatos(p, hist, cands=None):
    """Cobertura + score de cada candidato, ordenado de mejor a peor."""
    hubs = microhubs_activos()
    zonas = [{"id": z["id"], "nombre": z["nombre"], "lat": z["lat"], "lng": z["lng"],
              "demanda_dia": z["demanda_dia"], "poblacion": z["poblacion"]} for z in hist["zonas"]]
    out = []
    for c in (cands if cands is not None else candidatos()):
        cob = pc.cobertura_candidato(c, zonas, hubs, p)
        sc = pc.score_ubicacion(cob["demanda_cubierta"], float(c["renta_estimada"]),
                                cob["distancia_promedio"], c["accesibilidad_vial"], p)
        out.append({**c, "cob": cob, "score": sc["score"], "terminos": sc["terminos"]})
    out.sort(key=lambda x: x["score"], reverse=True)
    for i, c in enumerate(out, 1):
        c["ranking"] = i
    return out


def supuestos_de(c, hist, p):
    """Supuestos iniciales de un escenario a partir de un candidato evaluado."""
    dist = c["cob"]["distancia_promedio"] or 2.0
    return {
        "candidato_id": c["id"], "demanda_diaria": round(c["cob"]["demanda_cubierta"], 1),
        "operadores": 3, "repartidores": 3, "ticket": round(hist["ticket"] or 135, 2),
        "costo_entrega": round(max(c["cob"]["costo_ultima_milla"], 1), 2),
        "margen_bruto": p["margen_bruto_default"], "renta": float(c["renta_estimada"]),
        "nomina": float(c["nomina_estimada"]), "servicios": float(c["servicios_estimados"]),
        "otros": float(c["otros_costos"]), "distancia_km": dist,
        "capacidad_fisica": c["capacidad_fisica"], "poblacion": c["poblacion_cubierta"],
    }


CAMPOS = ["demanda_diaria", "operadores", "repartidores", "ticket", "costo_entrega", "margen_bruto",
          "renta", "nomina", "servicios", "otros", "distancia_km", "capacidad_fisica", "poblacion", "horas"]


def supuestos_de_form(args):
    s = {}
    for k in CAMPOS:
        v = args.get(k, "")
        if str(v).strip() == "":
            continue
        n = _num(v)
        if k == "margen_bruto" and n > 1:
            n = n / 100
        s[k] = n
    if args.get("candidato_id"):
        s["candidato_id"] = int(args["candidato_id"])
    return s


# ====================================================================
# Entrada y tablero del planeador
# ====================================================================
@plan.route("/planeacion")
@requiere("planeacion.ver")
def inicio():
    return redirect(url_for("planeacion.tablero"))


@plan.route("/panel")
@requiere()
def panel():
    destino = {"planeador": "planeacion.tablero", "operador": "planeacion.panel_operador",
               "administrador": "planeacion.panel_admin"}.get(actor()["rol"], "admin.indicadores")
    return redirect(url_for(destino))


@plan.route("/planeacion/tablero")
@requiere("planeacion.ver")
def tablero():
    p = parametros()
    hist = historial(p)
    ev = evaluar_candidatos(p, hist)
    mejor = ev[0] if ev else None
    sim = pc.simular(supuestos_de(mejor, hist, p), p) if mejor else None
    return render_template("plan_tablero.html", p=p, hist=hist, ev=ev, mejor=mejor, sim=sim,
                           hubs=microhubs_activos())


# ====================================================================
# 1. Demanda
# ====================================================================
@plan.route("/planeacion/demanda")
@requiere("planeacion.ver")
def demanda():
    p = parametros()
    return render_template("plan_demanda.html", hist=historial(p), p=p)


# ====================================================================
# 2. Ubicaciones candidatas
# ====================================================================
@plan.route("/planeacion/candidatos")
@requiere("planeacion.ver")
def candidatos_lista():
    p = parametros()
    hist = historial(p)
    return render_template("plan_candidatos.html", ev=evaluar_candidatos(p, hist, candidatos(False)), p=p)


def _leer_candidato(f):
    campos = {"clave": f["clave"].strip().upper(), "nombre": f["nombre"].strip(),
              "latitud": _num(f["latitud"]), "longitud": _num(f["longitud"]),
              "renta_estimada": _num(f["renta_estimada"]), "nomina_estimada": _num(f.get("nomina_estimada")),
              "servicios_estimados": _num(f.get("servicios_estimados")), "otros_costos": _num(f.get("otros_costos")),
              "superficie_m2": _num(f["superficie_m2"]), "capacidad_fisica": int(_num(f["capacidad_fisica"])),
              "accesibilidad_vial": int(_num(f["accesibilidad_vial"])), "zona_id": int(f["zona_id"]),
              "poblacion_cubierta": int(_num(f["poblacion_cubierta"])), "radio_km": _num(f.get("radio_km"), 1.5)}
    if not campos["clave"] or not campos["nombre"]:
        raise ValueError("La clave y el nombre son obligatorios.")
    if not 1 <= campos["accesibilidad_vial"] <= 10:
        raise ValueError("La accesibilidad vial va de 1 a 10.")
    return campos


@plan.route("/planeacion/candidatos/nuevo", methods=["GET", "POST"])
@plan.route("/planeacion/candidatos/<int:cid>/editar", methods=["GET", "POST"])
@requiere("planeacion.editar")
def candidato_form(cid=None):
    actual = get_candidato(cid) if cid else None
    if cid and not actual:
        abort(404)
    if request.method == "POST":
        try:
            d = _leer_candidato(request.form)
            if MODO_LOCAL:
                if cid:
                    actual.update(d, lat=d["latitud"], lng=d["longitud"],
                                  costo_fijo=d["renta_estimada"] + d["nomina_estimada"]
                                  + d["servicios_estimados"] + d["otros_costos"])
                else:
                    cid = demo.nuevo_candidato(d)
                flash("Candidato guardado (en memoria: en modo local no persiste).", "ok")
                return redirect(url_for("planeacion.candidato", cid=cid))
            cols = list(d)
            with con_actual() as con, con.cursor() as cur:
                if cid:
                    cur.execute(f"UPDATE ubicacion_candidata SET {', '.join(c + '=%s' for c in cols)} WHERE id=%s",
                                [d[c] for c in cols] + [cid])
                else:
                    cur.execute(f"INSERT INTO ubicacion_candidata ({', '.join(cols)}) "
                                f"VALUES ({', '.join(['%s'] * len(cols))}) RETURNING id", [d[c] for c in cols])
                    cid = cur.fetchone()["id"]
            flash("Candidato guardado.", "ok")
            return redirect(url_for("planeacion.candidato", cid=cid))
        except ValueError as e:
            flash(str(e), "alto")
        except Exception as e:
            texto = str(e)
            flash("Esa clave ya existe." if "ubicacion_candidata_clave_key" in texto else mensaje_de_error(e), "alto")
        actual = {**request.form}
    return render_template("plan_candidato_form.html", c=actual, zonas=zonas_catalogo(), cid=cid)


@plan.route("/planeacion/candidatos/<int:cid>")
@requiere("planeacion.ver")
def candidato(cid):
    p = parametros()
    hist = historial(p)
    fila = get_candidato(cid)
    if not fila:
        abort(404)
    todos = evaluar_candidatos(p, hist)
    c = next((x for x in todos if x["id"] == cid), None) or evaluar_candidatos(p, hist, [fila])[0]
    sup = supuestos_de(c, hist, p)
    return render_template("plan_candidato.html", c=c, sim=pc.simular(sup, p), sup=sup, p=p, total=len(todos))


@plan.route("/planeacion/candidatos/<int:cid>/decision", methods=["POST"])
@requiere("planeacion.editar")
def candidato_decision(cid):
    decision, motivo = request.form.get("decision"), request.form.get("motivo", "").strip()
    if decision not in ("aceptado", "rechazado", "condicionado") or not motivo:
        flash("Elige la decisión y escribe el motivo: la decisión de apertura es humana y se audita.", "alto")
        return redirect(url_for("planeacion.candidato", cid=cid))
    if MODO_LOCAL:
        c = get_candidato(cid)
        if not c:
            abort(404)
        c.update(decision=decision, decision_motivo=motivo)
        flash(f"Decisión registrada: {decision}.", "ok")
        return redirect(url_for("planeacion.candidato", cid=cid))
    try:
        with con_actual() as con, con.cursor() as cur:
            cur.execute("UPDATE ubicacion_candidata SET decision=%s, decision_motivo=%s, decision_por=%s, "
                        "decision_en=now() WHERE id=%s", (decision, motivo, g.usuario["id"], cid))
        flash(f"Decisión registrada: {decision}.", "ok")
    except Exception as e:
        flash(mensaje_de_error(e), "alto")
    return redirect(url_for("planeacion.candidato", cid=cid))


# ====================================================================
# Cobertura y mapa
# ====================================================================
@plan.route("/planeacion/cobertura")
@requiere("planeacion.ver")
def cobertura():
    p = parametros()
    hist = historial(p)
    hubs_ev = evaluar_candidatos(p, hist, [
        {"id": h["id"], "clave": h["clave"], "nombre": h["nombre"], "latitud": h["lat"], "longitud": h["lng"],
         "lat": h["lat"], "lng": h["lng"], "radio_km": h["radio_km"], "renta_estimada": 0,
         "accesibilidad_vial": 0, "poblacion_cubierta": 0} for h in microhubs_activos()])
    ev = evaluar_candidatos(p, hist)
    mapa = {
        "zonas": [{"nombre": z["nombre"], "lat": z["lat"], "lng": z["lng"], "pedidos_dia": z["pedidos_dia"],
                   "no_atendidos": z["no_atendidos"]} for z in hist["zonas"]],
        "hubs": [{"clave": h["clave"], "nombre": h["nombre"], "lat": h["lat"], "lng": h["lng"],
                  "radio": h["radio_km"]} for h in microhubs_activos()],
        "cands": [{"clave": c["clave"], "nombre": c["nombre"], "lat": c["lat"], "lng": c["lng"],
                   "radio": float(c["radio_km"]), "score": c["score"], "decision": c["decision"]} for c in ev],
    }
    return render_template("plan_cobertura.html", hubs_ev=hubs_ev, ev=ev, mapa=json.dumps(mapa), hist=hist)


# ====================================================================
# 3, 4, 7, 8. Simulación, capacidad, equilibrio, sensibilidad, ficha
# ====================================================================
def get_escenario(eid):
    if MODO_LOCAL:
        return next((e for e in demo.escenarios_mem if e["id"] == int(eid)), None)
    return consultar("SELECT * FROM escenario_planeacion WHERE id=%s", (eid,), una=True)


@plan.route("/planeacion/simulacion")
@requiere("planeacion.ver")
def simulacion():
    p = parametros()
    hist = historial(p)
    ev = evaluar_candidatos(p, hist)
    esc = None
    if request.args.get("escenario_id"):
        esc = get_escenario(request.args["escenario_id"])
        if not esc:
            abort(404)
    if esc:
        sup = dict(esc["supuestos"])
        if esc["ubicacion_candidata_id"]:
            sup["candidato_id"] = esc["ubicacion_candidata_id"]
    else:
        sup = supuestos_de_form(request.args)
        base_c = next((c for c in ev if str(c["id"]) == str(sup.get("candidato_id"))), ev[0] if ev else None)
        if base_c:
            sup = {**supuestos_de(base_c, hist, p), **sup, "candidato_id": base_c["id"]}
    cand = next((c for c in ev if c["id"] == sup.get("candidato_id")), None)
    res = pc.simular(sup, p)
    sens = pc.sensibilidad(sup, params=p) if request.args.get("sensibilidad") == "1" else None
    return render_template("plan_simulacion.html", sup=sup, res=res, ev=ev, cand=cand, esc=esc, sens=sens,
                           p=p, hist=hist, campos=CAMPOS)


@plan.route("/planeacion/escenarios/guardar", methods=["POST"])
@requiere("planeacion.editar")
def escenario_guardar():
    p = parametros()
    sup = supuestos_de_form(request.form)
    nombre = request.form.get("nombre", "").strip()
    if not nombre:
        flash("Ponle nombre al escenario para guardarlo.", "alto")
        return redirect(url_for("planeacion.simulacion", **{k: v for k, v in request.form.items() if k != "nombre"}))
    res = pc.simular(sup, p)
    cand = sup.get("candidato_id")
    esc_id = request.form.get("escenario_id")
    if MODO_LOCAL:
        esc_id = demo.escenario_nuevo(nombre, cand, sup, json.loads(json.dumps(res, default=float)), esc_id)
        flash("Escenario guardado (en memoria: en modo local no persiste).", "ok")
        return redirect(url_for("planeacion.simulacion", escenario_id=esc_id))
    try:
        with con_actual() as con, con.cursor() as cur:
            args = (nombre, cand, json.dumps(sup), json.dumps(res, default=float), g.usuario["id"])
            if esc_id:
                cur.execute("UPDATE escenario_planeacion SET nombre=%s, ubicacion_candidata_id=%s, supuestos=%s, "
                            "resultados=%s, actualizado_por=%s, actualizado_en=now() WHERE id=%s RETURNING id",
                            args + (esc_id,))
            else:
                cur.execute("INSERT INTO escenario_planeacion (nombre, ubicacion_candidata_id, supuestos, "
                            "resultados, creado_por) VALUES (%s,%s,%s,%s,%s) RETURNING id", args)
            esc_id = cur.fetchone()["id"]
        flash("Escenario guardado.", "ok")
    except Exception as e:
        flash(mensaje_de_error(e), "alto")
        return redirect(url_for("planeacion.simulacion", **{k: v for k, v in request.form.items() if k != "nombre"}))
    return redirect(url_for("planeacion.simulacion", escenario_id=esc_id))


def _escenarios(ids=None):
    if MODO_LOCAL:
        filas = [e for e in demo.escenarios_mem if not ids or e["id"] in ids]
        return sorted(filas, key=lambda e: e["id"], reverse=True)
    filtro, args = ("WHERE e.id = ANY(%s)", (ids,)) if ids else ("", ())
    return consultar(
        "SELECT e.id, e.nombre, e.supuestos, e.resultados, e.creado_en, e.actualizado_en, "
        "       c.clave AS candidato, u.nombre AS autor "
        "  FROM escenario_planeacion e LEFT JOIN ubicacion_candidata c ON c.id = e.ubicacion_candidata_id "
        f"  LEFT JOIN usuario u ON u.id = e.creado_por {filtro} ORDER BY e.id DESC", args)


@plan.route("/planeacion/escenarios")
@requiere("planeacion.ver")
def escenarios():
    return render_template("plan_escenarios.html", escenarios=_escenarios(), comparar=None)


@plan.route("/planeacion/escenarios/comparar")
@requiere("planeacion.ver")
def escenarios_comparar():
    ids = [int(i) for i in request.args.getlist("ids") if i.isdigit()]
    if len(ids) < 2:
        flash("Elige al menos dos escenarios para compararlos.", "medio")
        return redirect(url_for("planeacion.escenarios"))
    return render_template("plan_escenarios.html", escenarios=_escenarios(), comparar=_escenarios(ids))


@plan.route("/planeacion/escenarios.csv")
@requiere("planeacion.ver")
def escenarios_csv():
    ids = [int(i) for i in request.args.getlist("ids") if i.isdigit()]
    salida = io.StringIO()
    w = csv.writer(salida)
    w.writerow(["id", "escenario", "candidato", "demanda_dia", "operadores", "repartidores", "ticket",
                "costo_entrega", "renta", "atendidos", "rechazados", "utilizacion_pct", "equilibrio_dia",
                "costo_por_pedido", "utilidad_dia", "decision", "autor", "fecha"])
    for e in reversed(_escenarios(ids or None)):
        s, r = e["supuestos"], e["resultados"]
        w.writerow([e["id"], e["nombre"], e["candidato"], s.get("demanda_diaria"), s.get("operadores"),
                    s.get("repartidores"), s.get("ticket"), s.get("costo_entrega"), s.get("renta"),
                    r["atendidos"], r["rechazados"], r["utilizacion"], r["equilibrio"]["diario"],
                    r["costo_por_pedido"], r["margen_dia"], r["ficha"]["decision"], e["autor"],
                    e["creado_en"].strftime("%Y-%m-%d %H:%M")])
    auditar("planeacion", "modificacion", "Exportación de escenarios a CSV.", "escenario_planeacion")
    return Response("﻿" + salida.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=escenarios_microhubs.csv"})


# ====================================================================
# 5. Surtido
# ====================================================================
def _surtido_filas(p, hub, dias):
    if MODO_LOCAL:
        return demo.surtido_filas(p["margen_bruto_default"])
    filtro_hub = "AND p.microhub_id = %(hub)s" if hub else ""
    filtro_inv = "AND i.microhub_id = %(hub)s" if hub else ""
    filtro_mov = "AND m.microhub_id = %(hub)s" if hub else ""
    return consultar(f"""
        SELECT pr.id, pr.clave_interna, pr.nombre, c.nombre AS categoria, pr.precio::float AS precio,
               COALESCE(pr.costo_unitario, pr.precio * (1 - %(mb)s))::float AS costo,
               pr.espacio_unidades::float AS espacio,
               COALESCE(v.unidades, 0) AS unidades, COALESCE(v.ventas, 0)::float AS ventas,
               COALESCE(inv.existencia, 0) AS existencia, COALESCE(inv.minimo, 0) AS minimo,
               COALESCE(q.quiebres, 0) + CASE WHEN COALESCE(inv.existencia, 0) = 0 THEN 1 ELSE 0 END AS quiebres
          FROM producto pr JOIN categoria c ON c.id = pr.categoria_id
          LEFT JOIN (SELECT d.producto_id, sum(d.cantidad) AS unidades, sum(d.importe) AS ventas
                       FROM pedido_detalle d JOIN pedido p ON p.id = d.pedido_id
                      WHERE p.estado NOT IN ('cancelado','creado','pendiente_asignacion')
                        AND p.creado_en >= now() - make_interval(days => %(dias)s) {filtro_hub}
                      GROUP BY d.producto_id) v ON v.producto_id = pr.id
          LEFT JOIN (SELECT i.producto_id, sum(i.existencia) AS existencia, sum(i.minimo) AS minimo
                       FROM inventario i WHERE true {filtro_inv} GROUP BY i.producto_id) inv ON inv.producto_id = pr.id
          LEFT JOIN (SELECT m.producto_id, count(*) AS quiebres FROM movimiento_inventario m
                      WHERE m.existencia_resultante = 0
                        AND m.fecha >= now() - make_interval(days => %(dias)s) {filtro_mov}
                      GROUP BY m.producto_id) q ON q.producto_id = pr.id
         WHERE pr.estatus = 'activo' ORDER BY pr.nombre""",
        {"hub": hub, "dias": dias, "mb": p["margen_bruto_default"]})


@plan.route("/planeacion/surtido")
@requiere("planeacion.ver")
def surtido():
    p = parametros()
    hub = request.args.get("microhub_id", type=int)
    dias = int(p["ventana_analisis_dias"])
    filas = _surtido_filas(p, hub, dias)
    clases = {x["id"]: x for x in pc.clasificar_abc([{"id": f["id"], "unidades": f["unidades"]} for f in filas], p)}
    salida, resumen = [], defaultdict(int)
    for f in filas:
        cl = clases[f["id"]]
        r = pc.recomendar_surtido({**f, "clase": cl["clase"], "margen_unit": f["precio"] - f["costo"]}, dias, p)
        salida.append({**f, "clase": cl["clase"], "pct_acum": cl["pct_acum"],
                       "margen_unit": round(f["precio"] - f["costo"], 2),
                       "margen_total": round((f["precio"] - f["costo"]) * f["unidades"], 2), **r})
        resumen[r["recomendacion"]] += 1
    salida.sort(key=lambda x: (x["clase"], -x["unidades"]))
    return render_template("plan_surtido.html", filas=salida, resumen=resumen, p=p, hub=hub,
                           hubs=microhubs_activos(), espacio=round(sum(s["espacio"] for s in salida), 1),
                           dias=dias)


# ====================================================================
# 6. Optimización de entregas (pedidos listos → zona → repartidor → ruta)
# ====================================================================
def _hub_de_entregas():
    if MODO_LOCAL:
        return 1
    hub = g.usuario["microhub_id"] or request.values.get("microhub_id", type=int)
    if not hub:
        h = consultar("SELECT id FROM microhub WHERE estatus='activo' ORDER BY clave LIMIT 1", una=True)
        hub = h["id"] if h else None
    return hub


def _propuesta(hub, p, seleccion=None):
    if MODO_LOCAL:
        mh = next(h for h in demo.HUBS if h["id"] == hub)
        pedidos = [{"id": i, "folio": f, "zona_id": z, "zona": zn, "lat": la, "lng": lo, "total": t}
                   for i, (f, z, zn, la, lo, t) in enumerate(demo.PEDIDOS_LISTOS, 1)]
        reps = demo.REPARTIDORES
    else:
        mh = consultar("SELECT id, clave, nombre, latitud::float AS lat, longitud::float AS lng "
                       "FROM microhub WHERE id=%s", (hub,), una=True)
        pedidos = consultar(
            "SELECT p.id, p.folio, p.zona_id, z.nombre AS zona, d.latitud::float AS lat, d.longitud::float AS lng, "
            "       p.total::float AS total FROM pedido p JOIN domicilio d ON d.id = p.domicilio_id "
            "  JOIN zona z ON z.id = p.zona_id WHERE p.microhub_id = %s AND p.estado = 'en_preparacion' "
            "   AND p.listo_en IS NOT NULL ORDER BY p.listo_en", (hub,))
        reps = consultar("SELECT u.id, u.nombre || ' ' || u.apellidos AS nombre FROM usuario u "
                         "JOIN rol r ON r.id = u.rol_id WHERE r.clave = 'repartidor' AND u.estatus = 'activo' "
                         "ORDER BY u.id")
    if seleccion is not None:
        pedidos = [x for x in pedidos if x["id"] in seleccion]
    res = pc.asignar_repartidores(pedidos, reps, (mh["lat"], mh["lng"]), p)
    return mh, pedidos, reps, res


@plan.route("/planeacion/entregas")
@requiere("entregas.asignar")
def entregas():
    p = parametros()
    hub = _hub_de_entregas()
    if not hub:
        abort(404)
    mh, pedidos, reps, res = _propuesta(hub, p)
    zonas = defaultdict(list)
    for x in pedidos:
        zonas[x["zona"]].append(x)
    total_km = sum(r["plan"]["distancia_km"] for r in res["rutas"])
    en_prep = 0
    if not MODO_LOCAL:
        en_prep = consultar("SELECT count(*) AS n FROM pedido WHERE microhub_id=%s AND estado='en_preparacion' "
                            "AND listo_en IS NULL", (hub,), una=True)["n"]
    return render_template("plan_entregas.html", mh=mh, pedidos=pedidos, zonas=dict(zonas), reps=reps, res=res,
                           total_km=round(total_km, 2), hubs=microhubs_activos(), p=p, en_prep=en_prep,
                           local=MODO_LOCAL, usuario_hub=actor().get("microhub_id"),
                           total_costo=round(sum(r["plan"]["costo"] for r in res["rutas"]), 2))


@plan.route("/operacion/pedido/<int:pid>/listo", methods=["POST"])
@requiere("pedidos.cambiar_estado")
def marcar_listo(pid):
    """El pedido terminó de prepararse: queda disponible para agrupar y despachar."""
    try:
        with con_actual() as con, con.cursor() as cur:
            cur.execute("SELECT id FROM fn_pedidos_visibles(%s) WHERE id=%s AND estado='en_preparacion'",
                        (g.usuario["id"], pid))
            if not cur.fetchone():
                abort(403)
            cur.execute("UPDATE pedido SET listo_en = COALESCE(listo_en, now()) WHERE id=%s", (pid,))
        flash("Pedido listo para despacho. Aparece en Entregas para agruparlo y asignar repartidor.", "ok")
    except Exception as e:
        if getattr(e, "code", None) == 403:
            raise
        flash(mensaje_de_error(e), "alto")
    return redirect(url_for("operacion.detalle", pid=pid))


@plan.route("/planeacion/entregas/confirmar", methods=["POST"])
@requiere("entregas.asignar")
def entregas_confirmar():
    if MODO_LOCAL:
        flash("Modo local: la ruta se calcula pero no se guarda ni cambia pedidos.", "info")
        return redirect(url_for("planeacion.entregas"))
    p = parametros()
    hub = _hub_de_entregas()
    seleccion = {int(i) for i in request.form.getlist("pedido")} or None
    mh, pedidos, reps, res = _propuesta(hub, p, seleccion)
    if not res["rutas"]:
        flash("No hay pedidos listos o repartidores disponibles.", "medio")
        return redirect(url_for("planeacion.entregas", microhub_id=hub))
    try:
        with con_actual() as con, con.cursor() as cur:
            for r in res["rutas"]:
                plan_r = r["plan"]
                cur.execute(
                    "INSERT INTO plan_ruta (microhub_id, repartidor_id, metodo, paradas, distancia_km, minutos, "
                    "costo_estimado, creado_por) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                    (hub, r["repartidor_id"], plan_r["metodo"], len(r["paradas"]), plan_r["distancia_km"],
                     plan_r["minutos"], plan_r["costo"], g.usuario["id"]))
                rid = cur.fetchone()["id"]
                for t, parada in zip(plan_r["tramos"], r["paradas"]):
                    cur.execute("INSERT INTO plan_ruta_parada (plan_ruta_id, orden, pedido_id, tramo_km, minutos_acum) "
                                "VALUES (%s,%s,%s,%s,%s)", (rid, t["orden"], parada["id"], t["tramo_km"], t["minutos_acum"]))
                    costo = round(t["tramo_km"] * p["costo_km_reparto"] + p["costo_base_entrega"], 2)
                    cur.execute(
                        "INSERT INTO entrega (pedido_id, repartidor_id, turno_fecha, asignada_en, salida_en, plan_ruta_id, "
                        "orden_parada, distancia_km, minutos_estimados, costo_entrega_estimado) "
                        "VALUES (%s,%s,current_date,now(),now(),%s,%s,%s,%s,%s) "
                        "ON CONFLICT (pedido_id) DO UPDATE SET repartidor_id=EXCLUDED.repartidor_id, "
                        "  plan_ruta_id=EXCLUDED.plan_ruta_id, orden_parada=EXCLUDED.orden_parada, "
                        "  distancia_km=EXCLUDED.distancia_km, minutos_estimados=EXCLUDED.minutos_estimados, "
                        "  costo_entrega_estimado=EXCLUDED.costo_entrega_estimado",
                        (parada["id"], r["repartidor_id"], rid, t["orden"], t["tramo_km"], t["minutos_acum"], costo))
                    cur.execute("UPDATE pedido SET estado='en_ruta' WHERE id=%s", (parada["id"],))
        flash(f"Se despacharon {sum(len(r['paradas']) for r in res['rutas'])} pedidos en "
              f"{len(res['rutas'])} ruta(s).", "ok")
    except Exception as e:
        flash(mensaje_de_error(e), "alto")
    return redirect(url_for("planeacion.entregas", microhub_id=hub))


# ====================================================================
# Paneles por perfil
# ====================================================================
@plan.route("/panel/operador")
@requiere("pedidos.cambiar_estado")
def panel_operador():
    p = parametros()
    if MODO_LOCAL:
        conteo = {"pendientes": 4, "preparando": 3, "listos": 6, "en_ruta": 2}
        criticos = [{"nombre": s["nombre"], "existencia": s["existencia"], "minimo": s["minimo"]}
                    for s in demo.surtido_filas(p["margen_bruto_default"]) if s["existencia"] <= s["minimo"]]
        return render_template("panel_operador.html", c=conteo, criticos=criticos,
                               quiebres=sum(1 for c in criticos if c["existencia"] == 0),
                               ocup={"pedidos_en_turno": 9, "capacidad_turno": 12},
                               mh={"clave": "MH-01", "nombre": "Microhub San Bernabé Centro (demo)"}, p=p)
    hub = g.usuario["microhub_id"]
    if not hub:
        h = consultar("SELECT id FROM microhub WHERE estatus='activo' ORDER BY clave LIMIT 1", una=True)
        hub = h["id"]
    conteo = consultar(
        "SELECT count(*) FILTER (WHERE estado='asignado') AS pendientes, "
        "       count(*) FILTER (WHERE estado='en_preparacion' AND listo_en IS NULL) AS preparando, "
        "       count(*) FILTER (WHERE estado='en_preparacion' AND listo_en IS NOT NULL) AS listos, "
        "       count(*) FILTER (WHERE estado='en_ruta') AS en_ruta FROM pedido WHERE microhub_id=%s", (hub,), una=True)
    criticos = consultar(
        "SELECT pr.nombre, i.existencia, i.minimo FROM inventario i JOIN producto pr ON pr.id=i.producto_id "
        "WHERE i.microhub_id=%s AND i.existencia <= i.minimo AND pr.estatus='activo' "
        "ORDER BY i.existencia, pr.nombre LIMIT 15", (hub,))
    quiebres = consultar("SELECT count(*) AS n FROM inventario i JOIN producto pr ON pr.id=i.producto_id "
                         "WHERE i.microhub_id=%s AND i.existencia = 0 AND pr.estatus='activo'", (hub,), una=True)["n"]
    ocup = consultar("SELECT * FROM v_ocupacion_microhub WHERE microhub_id=%s", (hub,), una=True)
    mh = consultar("SELECT clave, nombre FROM microhub WHERE id=%s", (hub,), una=True)
    return render_template("panel_operador.html", c=conteo, criticos=criticos, quiebres=quiebres, ocup=ocup, mh=mh,
                           p=p)


@plan.route("/panel/administrador")
@requiere("usuarios.ver")
def panel_admin():
    if MODO_LOCAL:
        return render_template("panel_admin.html", redis_ok=True, recientes=[],
                               c={"usuarios": 12, "bloqueados": 0, "microhubs": 3, "parametros": 51,
                                  "auditoria_24h": 0, "seguridad_7d": 0})
    conteos = consultar(
        "SELECT (SELECT count(*) FROM usuario WHERE estatus='activo') AS usuarios, "
        "       (SELECT count(*) FROM usuario WHERE estatus='bloqueado') AS bloqueados, "
        "       (SELECT count(*) FROM microhub WHERE estatus='activo') AS microhubs, "
        "       (SELECT count(*) FROM configuracion) AS parametros, "
        "       (SELECT count(*) FROM auditoria WHERE fecha >= now() - interval '24 hours') AS auditoria_24h, "
        "       (SELECT count(*) FROM auditoria WHERE fecha >= now() - interval '7 days' "
        "          AND accion IN ('acceso_denegado','login_fallido','bloqueo_cuenta')) AS seguridad_7d", una=True)
    recientes = consultar("SELECT a.fecha, a.modulo, a.accion::text AS accion, a.entidad, u.correo "
                          "FROM auditoria a LEFT JOIN usuario u ON u.id=a.usuario_id ORDER BY a.id DESC LIMIT 8")
    redis_ok = True
    try:
        r_sesion.ping()
    except Exception:
        redis_ok = False
    return render_template("panel_admin.html", c=conteos, recientes=recientes, redis_ok=redis_ok)
