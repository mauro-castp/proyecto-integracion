"""Planeación cuantitativa de microhubs: cálculos transparentes y rutas web."""
from __future__ import annotations

import math
import os
import csv
import io
import json
from flask import Blueprint, Response, abort, flash, g, redirect, render_template, request, url_for

planeacion_bp = Blueprint("planeacion", __name__, url_prefix="/planeacion")
MODO_LOCAL = os.environ.get("MODO_LOCAL", "0") == "1"


def distancia_km(lat1, lng1, lat2, lng2):
    """Haversine; suficiente para comparar candidatos y rutas urbanas."""
    r = 6371.0
    p1, p2 = math.radians(float(lat1)), math.radians(float(lat2))
    dp = math.radians(float(lat2) - float(lat1))
    dl = math.radians(float(lng2) - float(lng1))
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return round(2 * r * math.asin(math.sqrt(a)), 2)


def calcular_score(demanda, renta, distancia, accesibilidad, pesos):
    """Normaliza magnitudes para que los cuatro pesos sean comparables."""
    return round(
        float(demanda) * pesos["demanda"]
        - (float(renta) / 1000) * pesos["renta"]
        - float(distancia) * pesos["distancia"]
        + float(accesibilidad) * pesos["accesibilidad"], 2)


def simular(datos):
    demanda = max(0, float(datos["demanda_diaria"]))
    operadores = max(1, int(datos["operadores"]))
    horas = max(1, float(datos.get("horas_turno", 8)))
    productividad = max(.1, float(datos.get("pedidos_operador_hora", 3)))
    capacidad = operadores * horas * productividad
    atendidos = min(demanda, capacidad)
    rechazados = max(0, demanda - capacidad)
    utilizacion = 100 * demanda / capacidad if capacidad else 0
    ticket = float(datos["ticket_promedio"])
    costo_entrega = float(datos["costo_entrega"])
    margen_pct = float(datos.get("margen_pct", 30)) / 100
    costos_fijos = sum(float(datos.get(k, 0)) for k in ("renta_mensual", "nomina_mensual", "servicios_mensuales", "otros_fijos"))
    margen_pedido = ticket * margen_pct - costo_entrega
    pe_mes = math.ceil(costos_fijos / margen_pedido) if margen_pedido > 0 else None
    dias = max(1, int(datos.get("dias_operacion", 30)))
    ingreso = atendidos * ticket
    costo_diario = costos_fijos / dias + atendidos * costo_entrega
    costo_pedido = costo_diario / atendidos if atendidos else 0
    utilidad = ingreso * margen_pct - costo_diario
    if utilizacion < 70:
        nivel, clase = "Estable", "ok"
    elif utilizacion <= 85:
        nivel, clase = "Atención", "medio"
    else:
        nivel, clase = "Riesgo de saturación", "alto"
    viable = pe_mes is not None and demanda >= pe_mes / dias
    decision = "VIABLE" if viable else "NO VIABLE CON LOS SUPUESTOS ACTUALES"
    if viable and utilizacion > 85:
        decision = "VIABLE CON RIESGO DE CAPACIDAD"
    return {
        "capacidad_diaria": round(capacidad, 1), "pedidos_atendidos": round(atendidos, 1),
        "pedidos_rechazados": round(rechazados, 1), "utilizacion": round(utilizacion, 1),
        "nivel": nivel, "clase": clase, "ingreso_diario": round(ingreso, 2),
        "costo_diario": round(costo_diario, 2), "costo_pedido": round(costo_pedido, 2),
        "margen_pedido": round(margen_pedido, 2), "punto_equilibrio_mes": pe_mes,
        "punto_equilibrio_dia": round(pe_mes / dias, 1) if pe_mes else None,
        "utilidad_diaria": round(utilidad, 2), "decision": decision,
    }


def clasificar_abc(items):
    total = sum(float(x["movimiento"]) for x in items) or 1
    acumulado, salida = 0, []
    for item in sorted(items, key=lambda x: float(x["movimiento"]), reverse=True):
        acumulado += float(item["movimiento"])
        pct = acumulado / total * 100
        clase = "A" if pct <= 80 or not salida else ("B" if pct <= 95 else "C")
        stock, minimo = int(item.get("stock", 0)), int(item.get("minimo", 0))
        rec = "Aumentar stock" if stock <= minimo or clase == "A" and stock < minimo * 2 else ("Reducir" if clase == "C" and stock > minimo * 3 else "Mantener")
        salida.append({**item, "abc": clase, "participacion_acum": round(pct, 1), "recomendacion": rec})
    return salida


def ruta_vecino_mas_cercano(origen, paradas):
    actual, pendientes, ruta, total = origen, list(paradas), [], 0.0
    while pendientes:
        sig = min(pendientes, key=lambda p: distancia_km(actual[0], actual[1], p["latitud"], p["longitud"]))
        tramo = distancia_km(actual[0], actual[1], sig["latitud"], sig["longitud"])
        ruta.append({**sig, "tramo_km": tramo})
        total += tramo
        actual = (sig["latitud"], sig["longitud"])
        pendientes.remove(sig)
    return ruta, round(total, 2)


DEMO_ZONAS = [
    {"zona":"San Bernabé", "pedidos_dia":82, "ticket":142, "no_atendidos":14, "pico":"18–20 h", "productos_pedido":3.4},
    {"zona":"Valles", "pedidos_dia":54, "ticket":118, "no_atendidos":21, "pico":"19–21 h", "productos_pedido":2.8},
    {"zona":"Paseo", "pedidos_dia":39, "ticket":126, "no_atendidos":18, "pico":"17–20 h", "productos_pedido":3.1},
]
DEMO_CANDIDATOS = [
    {"id":1,"clave":"CAND-01","nombre":"San Bernabé Centro","latitud":25.748,"longitud":-100.364,"renta_estimada":18000,"superficie_m2":130,"capacidad_fisica":150,"accesibilidad_vial":9,"zona":"San Bernabé","poblacion_cubierta":8420,"costo_fijo":72000,"demanda_cubierta":126,"distancia_promedio":2.4},
    {"id":2,"clave":"CAND-02","nombre":"Valles Poniente","latitud":25.755,"longitud":-100.372,"renta_estimada":15500,"superficie_m2":105,"capacidad_fisica":120,"accesibilidad_vial":7,"zona":"Valles","poblacion_cubierta":6180,"costo_fijo":65500,"demanda_cubierta":93,"distancia_promedio":3.1},
]


def _permiso():
    if MODO_LOCAL:
        return
    from nucleo import permisos_de
    if not getattr(g, "usuario", None) or not ({"simulacion.ver", "simulacion.ejecutar"} & permisos_de(g.usuario["rol"])):
        abort(403)


def _datos_reales():
    from nucleo import consultar
    zonas = consultar("""
      WITH dias AS (SELECT GREATEST(1, count(DISTINCT creado_en::date)) AS n FROM pedido),
      pz AS (SELECT z.id,z.nombre AS zona,count(p.id)::numeric/(SELECT n FROM dias) pedidos_dia,
             round(avg(p.subtotal),2) ticket,
             round(avg((SELECT sum(pd.cantidad) FROM pedido_detalle pd WHERE pd.pedido_id=p.id)),1) productos_pedido,
             concat(min(extract(hour from p.creado_en)) FILTER (WHERE extract(hour from p.creado_en) IN
               (SELECT extract(hour from p2.creado_en) FROM pedido p2 WHERE p2.zona_id=z.id GROUP BY 1 ORDER BY count(*) DESC LIMIT 1))::int,'–',
               (min(extract(hour from p.creado_en)) FILTER (WHERE extract(hour from p.creado_en) IN
               (SELECT extract(hour from p2.creado_en) FROM pedido p2 WHERE p2.zona_id=z.id GROUP BY 1 ORDER BY count(*) DESC LIMIT 1))+2)::int,' h') pico
        FROM zona z LEFT JOIN pedido p ON p.zona_id=z.id GROUP BY z.id,z.nombre),
      na AS (SELECT zona_id,count(*) no_atendidos FROM demanda_no_atendida GROUP BY zona_id)
      SELECT pz.*,coalesce(na.no_atendidos,0) no_atendidos FROM pz LEFT JOIN na ON na.zona_id=pz.id ORDER BY pedidos_dia DESC""")
    horas = consultar("SELECT extract(hour from creado_en)::int hora,count(*) pedidos FROM pedido GROUP BY 1 ORDER BY 1")
    candidatos = consultar("SELECT c.*,z.nombre zona FROM ubicacion_candidata c JOIN zona z ON z.id=c.zona_id WHERE c.estatus='activo' ORDER BY c.clave")
    surtido = consultar("""SELECT p.clave_interna clave,p.nombre,coalesce(sum(pd.cantidad),0) movimiento,
      coalesce(sum(i.existencia),0) stock,coalesce(sum(i.minimo),0) minimo
      FROM producto p LEFT JOIN pedido_detalle pd ON pd.producto_id=p.id LEFT JOIN inventario i ON i.producto_id=p.id
      GROUP BY p.id,p.clave_interna,p.nombre ORDER BY movimiento DESC""")
    hubs = consultar("SELECT id,nombre,latitud,longitud FROM microhub WHERE estatus='activo' ORDER BY id LIMIT 1")
    paradas = consultar("""SELECT p.folio,d.latitud,d.longitud,z.nombre zona FROM pedido p
      JOIN domicilio d ON d.id=p.domicilio_id JOIN zona z ON z.id=p.zona_id
      WHERE p.estado IN ('asignado','en_preparacion','en_ruta') ORDER BY p.creado_en LIMIT 10""")
    if hubs and paradas:
        ruta, distancia = ruta_vecino_mas_cercano((hubs[0]["latitud"],hubs[0]["longitud"]), [dict(x) for x in paradas])
    else:
        ruta, distancia = [], 0
    parametros = consultar("SELECT clave,valor FROM configuracion WHERE clave LIKE 'peso_score_%'")
    pesos = {x["clave"].replace("peso_score_",""):float(x["valor"]) for x in parametros}
    escenarios = consultar("SELECT id,nombre,resultados,creado_en FROM escenario_planeacion ORDER BY creado_en DESC LIMIT 10")
    zonas_catalogo = consultar("SELECT id,nombre FROM zona WHERE estatus='activo' ORDER BY nombre")
    return zonas, horas, candidatos, clasificar_abc(surtido), ruta, distancia, pesos, escenarios, zonas_catalogo


@planeacion_bp.route("", methods=["GET", "POST"])
def tablero():
    _permiso()
    entrada = {
        "nombre":"Escenario base", "demanda_diaria":120, "operadores":3, "repartidores":4,
        "horas_turno":8, "pedidos_operador_hora":5, "ticket_promedio":135,
        "costo_entrega":22, "margen_pct":35, "renta_mensual":18000,
        "nomina_mensual":42000, "servicios_mensuales":7000, "otros_fijos":5000,
        "dias_operacion":30,
    }
    if request.method == "POST":
        for k in entrada:
            if k in request.form:
                entrada[k] = request.form[k]
    resultado = simular(entrada)
    pesos = {"demanda":1.0,"renta":1.2,"distancia":4.0,"accesibilidad":3.0}
    if MODO_LOCAL:
        zonas, horas, candidatos = DEMO_ZONAS, [{"hora":h,"pedidos":n} for h,n in [(9,7),(12,13),(17,22),(18,31),(19,28),(20,19)]], DEMO_CANDIDATOS
        surtido = clasificar_abc([{"clave":"AB-001","nombre":"Arroz","movimiento":125,"stock":24,"minimo":20},{"clave":"BE-002","nombre":"Agua","movimiento":80,"stock":12,"minimo":15},{"clave":"LI-003","nombre":"Detergente","movimiento":22,"stock":40,"minimo":8}])
        ruta, distancia = ruta_vecino_mas_cercano((25.748,-100.364), [{"folio":"PED-001","zona":"San Bernabé","latitud":25.751,"longitud":-100.365},{"folio":"PED-002","zona":"Valles","latitud":25.756,"longitud":-100.372},{"folio":"PED-003","zona":"Paseo","latitud":25.759,"longitud":-100.375}])
        escenarios=[]; zonas_catalogo=[{"id":1,"nombre":"San Bernabé"},{"id":2,"nombre":"Valles"},{"id":3,"nombre":"Paseo"}]
    else:
        zonas, horas, candidatos, surtido, ruta, distancia, pesos_db, escenarios, zonas_catalogo = _datos_reales()
        pesos.update(pesos_db)
    comparacion = []
    for c in candidatos:
        c = dict(c)
        c["score"] = calcular_score(c["demanda_cubierta"], c["renta_estimada"], c["distancia_promedio"], c["accesibilidad_vial"], pesos)
        comparacion.append(c)
    comparacion.sort(key=lambda x:x["score"], reverse=True)
    if request.method == "POST" and request.form.get("accion") == "guardar" and not MODO_LOCAL:
        from nucleo import con_actual
        with con_actual() as con, con.cursor() as cur:
            cur.execute("INSERT INTO escenario_planeacion(nombre,creado_por,supuestos,resultados) VALUES(%s,%s,%s::jsonb,%s::jsonb)",
                        (str(entrada["nombre"]),g.usuario["id"],json.dumps(entrada),json.dumps(resultado)))
        flash("Escenario guardado para comparación.","ok")
        return redirect(url_for("planeacion.tablero")+"#equilibrio")
    return render_template("planeacion.html", zonas=zonas, horas=horas, candidatos=comparacion,
                           pesos=pesos, entrada=entrada, resultado=resultado, surtido=surtido,
                           ruta=ruta, distancia_ruta=distancia, escenarios=escenarios, zonas_catalogo=zonas_catalogo)


@planeacion_bp.get("/escenarios.csv")
def exportar_escenarios():
    _permiso()
    if MODO_LOCAL:
        filas=[]
    else:
        from nucleo import consultar
        filas=consultar("SELECT nombre,resultados,creado_en FROM escenario_planeacion ORDER BY creado_en DESC")
    out=io.StringIO(); w=csv.writer(out); w.writerow(["escenario","decision","demanda_equilibrio_dia","utilizacion_pct","costo_pedido","fecha"])
    for f in filas:
        r=f["resultados"]; w.writerow([f["nombre"],r.get("decision"),r.get("punto_equilibrio_dia"),r.get("utilizacion"),r.get("costo_pedido"),f["creado_en"]])
    return Response(out.getvalue(),mimetype="text/csv",headers={"Content-Disposition":"attachment; filename=escenarios_microhubs.csv"})


@planeacion_bp.post("/candidatos")
def candidato_crear():
    _permiso()
    if MODO_LOCAL:
        flash("En modo local los candidatos son demostrativos; en PostgreSQL el registro sí se guarda.", "info")
        return redirect(url_for("planeacion.tablero")+"#ubicaciones")
    from nucleo import con_actual, mensaje_de_error
    f=request.form
    try:
        with con_actual() as con, con.cursor() as cur:
            cur.execute("""INSERT INTO ubicacion_candidata(clave,nombre,latitud,longitud,renta_estimada,superficie_m2,
              capacidad_fisica,accesibilidad_vial,zona_id,poblacion_cubierta,costo_fijo,demanda_cubierta,distancia_promedio)
              VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
              (f["clave"],f["nombre"],f["latitud"],f["longitud"],f["renta_estimada"],f["superficie_m2"],
               f["capacidad_fisica"],f["accesibilidad_vial"],f["zona_id"],f["poblacion_cubierta"],f["costo_fijo"],f["demanda_cubierta"],f["distancia_promedio"]))
        flash("Ubicación candidata registrada.","ok")
    except Exception as e:
        flash(mensaje_de_error(e),"alto")
    return redirect(url_for("planeacion.tablero")+"#ubicaciones")
