"""
consultas_planeacion.py — Demanda histórica, candidatos y supuestos que usa el servicio de planeación.

Es la parte de datos que antes se tomaba del módulo de pantallas del portal. Los microservicios no dependen del sistema web:
tienen aquí sus consultas y en planeacion_calc.py su copia de las fórmulas (una prueba comprueba que sea idéntica a la del
portal, para que ambos sigan dando los mismos números).
"""
from collections import defaultdict

from . import planeacion_calc as pc
from .datos import consultar

TZ = "America/Monterrey"


def parametros():
    filas = consultar("SELECT clave, valor FROM configuracion "
                      "WHERE ambito = 'global' AND clave = ANY(%s)", (list(pc.PARAMS),))
    return pc.con_defecto({f["clave"]: f["valor"] for f in filas})


def historial(p):
    """Demanda histórica agregada: zona, hora, categoría, no atendida."""
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
    return consultar("SELECT id, clave, nombre, latitud::float AS lat, longitud::float AS lng, "
                     "COALESCE(radio_km, 1.5)::float AS radio_km FROM microhub "
                     "WHERE estatus = 'activo' ORDER BY clave")


def candidatos(solo_activos=True):
    return consultar(
        "SELECT c.*, z.nombre AS zona, c.latitud::float AS lat, c.longitud::float AS lng "
        "FROM ubicacion_candidata c JOIN zona z ON z.id = c.zona_id "
        + ("WHERE c.estatus = 'activo' " if solo_activos else "") + "ORDER BY c.clave")


def get_candidato(cid):
    return next((c for c in candidatos(False) if c["id"] == cid), None)


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
