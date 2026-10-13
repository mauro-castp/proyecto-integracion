"""
Servicio de seguimiento · puerto 5110 · contrato v1

  POST /api/v1/seguimiento/{entrega_id}/ubicaciones   lote de hasta 500 puntos GPS → MongoDB
  GET  /api/v1/seguimiento/{entrega_id}/recorrido     resumen del recorrido (agregación en MongoDB)

Responsabilidad única: el rastro GPS de una entrega. El cierre de la entrega (monto, líneas,
incidencia, evidencia) es del servicio de entregas; los archivos de evidencia son del servicio
de documentos.

Los puntos viven solo en MongoDB (ubicaciones_entrega, índice 2dsphere, TTL de 180 días): son
datos de alta frecuencia que no necesitan la integridad transaccional del pedido. PostgreSQL
solo se consulta para saber si el perfil puede ver esa entrega (repartidor: la suya; operador y
supervisor: las de su microhub; el resto de los perfiles con permiso: todas).
"""
import datetime as dt
import math

from bson import Int64
from flask import g

from comun import config
from comun.base import crear_app, documentar, leer_cuerpo, requiere, responder
from comun.base_errores import ErrorApi, invalido, no_encontrado
from comun.datos import ahora, consultar, mongo
from comun.formatos import fecha
from comun.validar import Campo, unir_errores, validar

app = crear_app("seguimiento", "Microhubs · Seguimiento",
                "Seguimiento GPS de las entregas: puntos de ubicación y resumen del recorrido.",
                5110, dependencias=("postgres", "redis", "mongo"))
P = config.PREFIJO

CAMPOS_UBICACION = [Campo("latitud", "num", minimo=-90, maximo=90), Campo("longitud", "num", minimo=-180, maximo=180),
                    Campo("precision_m", "num", req=False, minimo=0)]


def _entrega_visible(eid):
    """404 si la entrega no existe o el perfil no puede verla (mismo ámbito que el servicio de entregas)."""
    u = g.usuario
    cond, args = "TRUE", []
    if u["rol"] == "repartidor":
        cond, args = "e.repartidor_id = %s", [u["id"]]
    elif u["rol"] in ("operador", "supervisor"):
        cond, args = "p.microhub_id = %s", [u.get("microhub_id")]
    f = consultar("SELECT e.id FROM entrega e JOIN pedido p ON p.id = e.pedido_id "
                  f"WHERE e.id = %s AND {cond}", (eid, *args), una=True)
    if not f:
        raise no_encontrado("No existe la entrega o no está asignada a ti.")


def _ubicaciones():
    db = mongo()
    if db is None:
        raise ErrorApi(503, "SERVICIO_NO_DISPONIBLE", "El almacén de recorridos (MongoDB) no está disponible.")
    return db.ubicaciones_entrega


@app.post(f"{P}/seguimiento/<int:eid>/ubicaciones")
@requiere("entregas.cerrar", "entregas.ver")
def ubicaciones(eid):
    _entrega_visible(eid)
    d = validar(leer_cuerpo(), [Campo("puntos", "lista")])
    if not 1 <= len(d["puntos"]) <= 500:
        raise invalido("puntos", "Envía entre 1 y 500 puntos por lote.")
    campos = CAMPOS_UBICACION + [Campo("capturado_en", "fecha")]
    puntos = unir_errores(*[(lambda p=p, i=i: validar(p if isinstance(p, dict) else {}, campos, prefijo=f"puntos[{i}]."))
                            for i, p in enumerate(d["puntos"])])
    recibido = ahora()
    docs = [{"entrega_id": Int64(eid), "usuario_id": int(g.usuario["id"]),
             "posicion": {"type": "Point", "coordinates": [p["longitud"], p["latitud"]]},
             "precision_m": p.get("precision_m"), "capturado_en": p["capturado_en"].astimezone(dt.timezone.utc),
             "recibido_en": recibido} for p in puntos]
    _ubicaciones().insert_many(docs, ordered=False)
    return responder({"recibidos": len(docs)}, 201, raiz="ubicaciones_recibidas")


def _haversine(a, b):
    (lng1, lat1), (lng2, lat2) = a, b
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lng2 - lng1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371.0088 * math.asin(math.sqrt(h))


@app.get(f"{P}/seguimiento/<int:eid>/recorrido")
@requiere("entregas.ver")
def recorrido(eid):
    _entrega_visible(eid)
    r = list(_ubicaciones().aggregate([
        {"$match": {"entrega_id": Int64(eid)}}, {"$sort": {"capturado_en": 1}},
        {"$group": {"_id": "$entrega_id", "puntos": {"$sum": 1}, "inicio": {"$first": "$capturado_en"},
                    "fin": {"$last": "$capturado_en"}, "precision": {"$avg": "$precision_m"},
                    "ruta": {"$push": "$posicion.coordinates"}, "ultima_precision": {"$last": "$precision_m"}}}]))
    if not r:
        return responder({"entrega_id": eid, "puntos": 0, "distancia_km": 0.0, "inicio": None, "fin": None,
                          "precision_promedio_m": None, "ultimo_punto": None}, raiz="recorrido")
    r = r[0]
    ruta = r["ruta"]
    ultimo = {"latitud": ruta[-1][1], "longitud": ruta[-1][0]}
    if r.get("ultima_precision") is not None:
        ultimo["precision_m"] = float(r["ultima_precision"])
    return responder({"entrega_id": eid, "puntos": int(r["puntos"]),
                      "distancia_km": round(sum(_haversine(ruta[i], ruta[i + 1]) for i in range(len(ruta) - 1)), 2),
                      "inicio": fecha(r["inicio"]), "fin": fecha(r["fin"]),
                      "precision_promedio_m": round(r["precision"], 1) if r.get("precision") is not None else None,
                      "ultimo_punto": ultimo}, raiz="recorrido")


ID = [("id", "path", "integer", "Id de la entrega")]
documentar(app, "POST", f"{P}/seguimiento/{{id}}/ubicaciones", "Enviar puntos GPS", permisos=["entregas.cerrar", "entregas.ver"],
           parametros=ID, cuerpo="UbicacionesLote.ok", solo_json=True,
           descripcion="Hasta 500 puntos por lote; se guardan en MongoDB (ubicaciones_entrega, índice 2dsphere).",
           respuestas={201: ("Puntos guardados", "UbicacionesRecibidas.ok")}, errores=[400, 403, 404, 422])
documentar(app, "GET", f"{P}/seguimiento/{{id}}/recorrido", "Resumen del recorrido", permisos=["entregas.ver"],
           parametros=ID, descripcion="Agregación en MongoDB ($match, $sort, $group) sobre los puntos guardados.",
           respuestas={200: ("Recorrido", "Recorrido.ok")}, errores=[403, 404])
