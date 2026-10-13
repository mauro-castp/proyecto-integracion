"""
Servicio de entregas · puerto 5105 · contrato v1

  GET  /api/v1/entregas/mias                paradas abiertas del repartidor en su turno (RN25)
  GET  /api/v1/entregas                     entregas en el ámbito del perfil (estado_pedido, abiertas, repartidor_id)
  GET  /api/v1/entregas/{id}                detalle con cliente, domicilio y líneas (RN26)
  POST /api/v1/entregas/{id}/resultado      registra y cierra la entrega (solo JSON, idempotente)
  POST /api/v1/entregas/{id}/ubicaciones    lote de hasta 500 puntos GPS → MongoDB
  GET  /api/v1/entregas/{id}/recorrido      resumen del recorrido (agregación en MongoDB)

Cierre idempotente: cada cierre trae `id_cliente_local` (UUID que la app
conserva hasta el éxito). Si la entrega ya se cerró con ese mismo UUID la
respuesta es 200 con duplicado=true; si se cerró con otro, 409. El UUID se
guarda en entrega.id_cliente_local (índice único) y en MongoDB
(sincronizaciones_moviles, con cada reintento).

Las reglas que no dependen del motor se validan aquí y se devuelven todas
juntas (RN27 monto completo, RN28 parcial por líneas con motivo, RN29
fallida con incidencia). La transición en_ruta → cierre la valida el
trigger del motor según el rol; la devolución de inventario la hace
fn_devolver_inventario, la misma función que usa el web.
"""
import datetime as dt
import math
from decimal import Decimal

from bson import Int64, ObjectId
from flask import g, request
from pymongo.errors import DuplicateKeyError

from comun import config
from comun.base import (crear_app, documentar, filtro_entero, filtro_opcion, leer_cuerpo, leer_paginacion, lista,
                        paginacion, requiere, responder)
from comun.base_errores import ErrorApi, conflicto, invalido, no_encontrado
from comun.datos import ahora, conexion, consultar, mongo, mongo_disponible
from comun.formatos import dinero, fecha, numero
from comun.validar import Campo, unir_errores, validar

app = crear_app("entregas", "Microhubs · Entregas", "Entregas del repartidor, cierre con evidencia y recorrido GPS.",
                5105, dependencias=("postgres", "redis", "mongo"))
P = config.PREFIJO
ESTADOS = ["creado", "pendiente_asignacion", "asignado", "en_preparacion", "en_ruta", "entregado",
           "entrega_parcial", "entrega_fallida", "cancelado"]
NUEVO_ESTADO = {"entregado": "entregado", "parcial": "entrega_parcial", "fallida": "entrega_fallida"}
TIPO_OPERACION = {"entregado": "cierre_entrega", "parcial": "entrega_parcial", "fallida": "entrega_fallida"}

BASE = ("SELECT e.id, e.pedido_id, p.folio, p.estado::text AS estado_pedido, e.orden_parada, "
        "d.calle || ' ' || d.numero_ext || ', ' || d.colonia AS direccion, z.nombre AS zona, e.distancia_km, "
        "e.minutos_estimados, p.total, e.repartidor_id, e.cierre_en, e.turno_fecha, p.microhub_id, "
        "e.id_cliente_local, e.resultado::text AS resultado "
        "FROM entrega e JOIN pedido p ON p.id = e.pedido_id JOIN domicilio d ON d.id = p.domicilio_id "
        "JOIN zona z ON z.id = p.zona_id ")


def ambito():
    """Condición SQL del ámbito de cada perfil sobre entrega e / pedido p."""
    u = g.usuario
    if u["rol"] == "repartidor":
        return "e.repartidor_id = %s", [u["id"]]
    if u["rol"] in ("operador", "supervisor"):
        return "p.microhub_id = %s", [u.get("microhub_id")]
    return "TRUE", []


def parada(f):
    return {"id": f["id"], "pedido_id": f["pedido_id"], "folio": f["folio"], "estado_pedido": f["estado_pedido"],
            "orden_parada": f["orden_parada"], "direccion": f["direccion"], "zona": f["zona"],
            "distancia_km": numero(f["distancia_km"]), "minutos_estimados": numero(f["minutos_estimados"]),
            "total": dinero(f["total"])}


def _entrega(eid, para_cierre=False):
    w, args = ambito()
    f = consultar(BASE + f"WHERE e.id = %s AND {w}", (eid, *args), una=True)
    if not f:
        raise no_encontrado("No existe la entrega o no está asignada a ti.")
    # RN26: el repartidor ve el domicilio solo mientras la entrega está activa.
    if g.usuario["rol"] == "repartidor" and f["cierre_en"] is not None and not para_cierre:
        raise no_encontrado("La entrega ya se cerró; su información ya no está disponible.")
    return f


# --------------------------------------------------------------------
@app.get(f"{P}/entregas/mias")
@requiere("entregas.ver")
def mias():
    pagina, por, desde = leer_paginacion()
    cond = "e.repartidor_id = %s AND e.cierre_en IS NULL AND e.turno_fecha = current_date"
    total = consultar(f"SELECT count(*) AS n FROM entrega e WHERE {cond}", (g.usuario["id"],), una=True)["n"]
    filas = consultar(BASE + f"WHERE {cond} ORDER BY e.orden_parada NULLS LAST, e.id LIMIT %s OFFSET %s",
                      (g.usuario["id"], por, desde))
    return lista(filas, paginacion(pagina, por, total), "entrega", "entregas", parada)


@app.get(f"{P}/entregas")
@requiere("entregas.ver")
def entregas():
    pagina, por, desde = leer_paginacion()
    estado = filtro_opcion("estado_pedido", ESTADOS)
    abiertas = filtro_opcion("abiertas", ["true", "false"])
    rep = filtro_entero("repartidor_id")
    w, args = ambito()
    where = [w]
    if estado:
        where.append("p.estado = %s"); args.append(estado)
    if abiertas:
        where.append("e.cierre_en IS NULL" if abiertas == "true" else "e.cierre_en IS NOT NULL")
    if rep:
        where.append("e.repartidor_id = %s"); args.append(rep)
    cond = " AND ".join(where)
    total = consultar(f"SELECT count(*) AS n FROM entrega e JOIN pedido p ON p.id = e.pedido_id WHERE {cond}",
                      args, una=True)["n"]
    filas = consultar(BASE + f"WHERE {cond} ORDER BY e.id DESC LIMIT %s OFFSET %s", (*args, por, desde))
    return lista(filas, paginacion(pagina, por, total), "entrega", "entregas", parada)


@app.get(f"{P}/entregas/<int:eid>")
@requiere("entregas.ver")
def detalle(eid):
    f = _entrega(eid)
    c = consultar("SELECT u.nombre || ' ' || COALESCE(u.apellidos,'') AS nombre, u.telefono, d.calle, d.numero_ext, "
                  "d.colonia, d.latitud, d.longitud FROM pedido p JOIN cliente cl ON cl.id = p.cliente_id "
                  "JOIN usuario u ON u.id = cl.usuario_id JOIN domicilio d ON d.id = p.domicilio_id WHERE p.id = %s",
                  (f["pedido_id"],), una=True)
    lineas = consultar("SELECT pd.id AS pedido_detalle_id, pr.nombre, pd.cantidad FROM pedido_detalle pd "
                       "JOIN producto pr ON pr.id = pd.producto_id WHERE pd.pedido_id = %s ORDER BY pd.id",
                       (f["pedido_id"],))
    cuerpo = {"id": f["id"], "pedido_id": f["pedido_id"], "folio": f["folio"], "estado_pedido": f["estado_pedido"],
              "cliente": {"nombre": c["nombre"].strip(), "telefono": c["telefono"]},
              "domicilio": {"calle": c["calle"], "numero_ext": c["numero_ext"], "colonia": c["colonia"],
                            "latitud": numero(c["latitud"]), "longitud": numero(c["longitud"])},
              "orden_parada": f["orden_parada"], "distancia_km": numero(f["distancia_km"]),
              "minutos_estimados": numero(f["minutos_estimados"]), "total": dinero(f["total"]), "lineas": lineas}
    return responder(cuerpo, raiz="entrega_detalle")


# --------------------------------------------------------------------
# Cierre
# --------------------------------------------------------------------
CAMPOS_CIERRE = [
    Campo("resultado", opciones=["entregado", "parcial", "fallida"]),
    Campo("monto_cobrado", "num", minimo=0, decimales=2), Campo("cambio_entregado", "num", minimo=0, decimales=2),
    Campo("incidencia", req=False, max_len=400), Campo("lineas", "lista", req=False), Campo("ubicacion", "obj"),
    Campo("evidencia_ids", "lista", req=False), Campo("capturado_en", "fecha"),
    Campo("id_cliente_local", min_len=8, max_len=64)]
CAMPOS_UBICACION = [Campo("latitud", "num", minimo=-90, maximo=90), Campo("longitud", "num", minimo=-180, maximo=180),
                    Campo("precision_m", "num", req=False, minimo=0)]
CAMPOS_LINEA = [Campo("pedido_detalle_id", "int", minimo=1), Campo("cantidad_entregada", "int", minimo=0),
                Campo("cantidad_devuelta", "int", minimo=0), Campo("motivo", req=False, max_len=300)]


def _respuesta_cierre(f, duplicado, status):
    return responder({"entrega_id": f["id"], "pedido_id": f["pedido_id"], "estado_pedido": f["estado_pedido"],
                      "cerrado_en": fecha(f["cierre_en"]), "duplicado": duplicado}, status, raiz="resultado_entrega")


def _reglas(d, f, detalle_pedido):
    """RN27–RN29 y coherencia de las líneas; devuelve todos los errores juntos."""
    errores = []
    total, monto = Decimal(str(f["total"])), Decimal(str(d["monto_cobrado"]))
    incidencia = (d.get("incidencia") or "").strip()
    if d["resultado"] == "entregado" and abs(monto - total) > Decimal("0.01"):
        errores.append(("monto_cobrado", f"Una entrega completa cobra el total del pedido ({total:.2f})."))
    if d["resultado"] == "fallida":
        if not incidencia:
            errores.append(("incidencia", "Una entrega fallida necesita la incidencia (RN29)."))
        if monto != 0:
            errores.append(("monto_cobrado", "Una entrega fallida no cobra nada."))
    if d["resultado"] == "parcial":
        if monto > total:
            errores.append(("monto_cobrado", "El monto cobrado no puede superar el total."))
        if not d["lineas"]:
            errores.append(("lineas", "Una entrega parcial indica qué se entregó y qué regresa por línea (RN28)."))
        devueltas = 0
        for i, l in enumerate(d["lineas"]):
            cant = detalle_pedido.get(l["pedido_detalle_id"])
            if cant is None:
                errores.append((f"lineas[{i}].pedido_detalle_id", "La línea no pertenece a este pedido."))
                continue
            if l["cantidad_entregada"] + l["cantidad_devuelta"] != cant:
                errores.append((f"lineas[{i}]", f"Entregadas + devueltas debe sumar {cant}."))
            if l["cantidad_devuelta"] > 0 and not (l.get("motivo") or "").strip():
                errores.append((f"lineas[{i}].motivo", "Explica por qué regresan unidades."))
            devueltas += l["cantidad_devuelta"]
        if d["lineas"] and devueltas == 0:
            errores.append(("lineas", "Una entrega parcial devuelve al menos una unidad."))
    if d["capturado_en"] > ahora() + dt.timedelta(minutes=10):
        errores.append(("capturado_en", "La hora de captura está en el futuro."))
    if g.usuario["rol"] == "repartidor" and not d["evidencia_ids"]:
        errores.append(("evidencia_ids", "Adjunta la foto de evidencia (POST /api/v1/documentos)."))
    if errores:
        raise ErrorApi(422, "VALIDACION", "Revisa los datos enviados.",
                       [{"campo": c, "mensaje": m} for c, m in errores])


def _verificar_evidencias(ids, eid):
    malos = [i for i in ids if not (isinstance(i, str) and len(i) == 24 and ObjectId.is_valid(i))]
    if malos:
        raise invalido("evidencia_ids", "Cada evidencia es el id (24 caracteres) que devolvió el servicio de documentos.")
    db = mongo()
    if db is None or not mongo_disponible():
        return                                        # sin MongoDB no se bloquea el cierre; queda en el log
    encontrados = db.documentos.count_documents({"_id": {"$in": [ObjectId(i) for i in ids]},
                                                 "referencia.tipo": "entrega", "referencia.id": str(eid)})
    if encontrados != len(set(ids)):
        raise invalido("evidencia_ids", "Alguna evidencia no existe o no está adjunta a esta entrega.")


def _registrar_sincronizacion(d, f, estado, conflicto_info=None):
    """Bitácora móvil en MongoDB: una operación por UUID; los reintentos actualizan el mismo documento."""
    db = mongo()
    if db is None:
        return
    try:
        db.sincronizaciones_moviles.update_one(
            {"operacion_uuid": d["id_cliente_local"]},
            {"$setOnInsert": {"operacion_uuid": d["id_cliente_local"],
                              "dispositivo_id": (request.headers.get("X-Dispositivo") or "app-movil")[:80],
                              "usuario_id": int(g.usuario["id"]), "tipo_operacion": TIPO_OPERACION[d["resultado"]],
                              "pedido_id": Int64(f["pedido_id"]),
                              "capturado_en": d["capturado_en"].astimezone(dt.timezone.utc),
                              "carga": {"entrega_id": f["id"], "resultado": d["resultado"],
                                        "monto_cobrado": float(d["monto_cobrado"]),
                                        "evidencia_ids": d["evidencia_ids"], "ubicacion": d["ubicacion"]}},
             "$set": {"estado": estado, "sincronizado_en": ahora(), "conflicto": conflicto_info},
             "$inc": {"intentos": 1}}, upsert=True)
    except Exception:
        pass


@app.post(f"{P}/entregas/<int:eid>/resultado")
@requiere("entregas.cerrar")
def resultado(eid):
    cuerpo = leer_cuerpo()
    d, ubic = unir_errores(lambda: validar(cuerpo, CAMPOS_CIERRE),
                           lambda: validar(cuerpo.get("ubicacion") if isinstance(cuerpo.get("ubicacion"), dict) else {},
                                           CAMPOS_UBICACION, prefijo="ubicacion."))
    d["ubicacion"] = ubic
    d["lineas"] = [validar(l if isinstance(l, dict) else {}, CAMPOS_LINEA, prefijo=f"lineas[{i}].")
                   for i, l in enumerate(d.get("lineas") or [])]
    d["evidencia_ids"] = [str(x) for x in (d.get("evidencia_ids") or [])]
    _entrega(eid, para_cierre=True)                                  # 404 si no es suya
    _verificar_evidencias(d["evidencia_ids"], eid)
    w, args = ambito()
    with conexion() as con, con.cursor() as cur:
        cur.execute(BASE + f"WHERE e.id = %s AND {w} FOR UPDATE OF e", (eid, *args))
        f = cur.fetchone()
        if f["cierre_en"] is not None:
            if f["id_cliente_local"] == d["id_cliente_local"]:
                con.rollback()
                _registrar_sincronizacion(d, f, "aplicada")
                return _respuesta_cierre(f, True, 200)
            _registrar_sincronizacion(d, f, "conflicto", {"motivo": "La entrega ya estaba cerrada por otra operación.",
                                                          "estado_servidor": f["estado_pedido"],
                                                          "estado_dispositivo": NUEVO_ESTADO[d["resultado"]],
                                                          "resuelto_por": None, "resuelto_en": None})
            raise conflicto("La entrega ya se cerró con otra operación.")
        if f["estado_pedido"] != "en_ruta":
            raise conflicto(f"El pedido está en {f['estado_pedido']}: solo se cierra una entrega en ruta.")
        cur.execute("SELECT id, cantidad FROM pedido_detalle WHERE pedido_id = %s", (f["pedido_id"],))
        _reglas(d, f, {r["id"]: r["cantidad"] for r in cur.fetchall()})
        incidencia = (d.get("incidencia") or "").strip() or None
        cobrado = Decimal(str(d["monto_cobrado"]))
        cur.execute(
            "UPDATE entrega SET cierre_en = now(), resultado = %s, confirmacion_recepcion = %s, monto_cobrado = %s, "
            "cambio_entregado = %s, incidencia = %s, cerrada_por_usuario_id = %s, id_cliente_local = %s, "
            "evidencia_ids = %s, evidencia_url = %s, cierre_latitud = %s, cierre_longitud = %s, "
            "cierre_precision_m = %s, capturado_en = %s, salida_en = COALESCE(salida_en, asignada_en) "
            "WHERE id = %s",
            (d["resultado"], d["resultado"] != "fallida", cobrado, Decimal(str(d["cambio_entregado"])), incidencia,
             g.usuario["id"], d["id_cliente_local"], d["evidencia_ids"] or None,
             f"/api/v1/documentos/{d['evidencia_ids'][0]}" if d["evidencia_ids"] else None,
             round(d["ubicacion"]["latitud"], 6), round(d["ubicacion"]["longitud"], 6),
             d["ubicacion"].get("precision_m"), d["capturado_en"], eid))
        for l in d["lineas"]:
            cur.execute("INSERT INTO entrega_linea (entrega_id, pedido_detalle_id, cantidad_entregada, cantidad_devuelta, "
                        "motivo) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (entrega_id, pedido_detalle_id) DO UPDATE SET "
                        "cantidad_entregada = EXCLUDED.cantidad_entregada, cantidad_devuelta = EXCLUDED.cantidad_devuelta, "
                        "motivo = EXCLUDED.motivo",
                        (eid, l["pedido_detalle_id"], l["cantidad_entregada"], l["cantidad_devuelta"],
                         (l.get("motivo") or "").strip() or None))
        # El trigger fn_valida_transicion decide si este perfil puede cerrar (RN20).
        cur.execute("UPDATE pedido SET estado = %s, motivo_cancelacion = COALESCE(%s, motivo_cancelacion) WHERE id = %s",
                    (NUEVO_ESTADO[d["resultado"]], incidencia, f["pedido_id"]))
        if d["resultado"] == "fallida":
            cur.execute("SELECT fn_devolver_inventario(%s, 'devolucion_cancelacion', %s)",
                        (f["pedido_id"], "Entrega fallida: la mercancía regresa al microhub."))
        elif d["resultado"] == "parcial":
            cur.execute("SELECT fn_devolver_inventario(%s, 'devolucion_parcial', %s)",
                        (f["pedido_id"], "Entrega parcial: regresan las unidades devueltas (RN28)."))
        cur.execute(BASE + "WHERE e.id = %s", (eid,))
        final = cur.fetchone()
    _registrar_sincronizacion(d, final, "aplicada")
    return _respuesta_cierre(final, False, 201)


# --------------------------------------------------------------------
# Recorrido GPS (MongoDB)
# --------------------------------------------------------------------
def _ubicaciones():
    db = mongo()
    if db is None:
        raise ErrorApi(503, "SERVICIO_NO_DISPONIBLE", "El almacén de recorridos (MongoDB) no está disponible.")
    return db.ubicaciones_entrega


@app.post(f"{P}/entregas/<int:eid>/ubicaciones")
@requiere("entregas.cerrar", "entregas.ver")
def ubicaciones(eid):
    f = _entrega(eid, para_cierre=True)
    if g.usuario["rol"] == "repartidor" and f["repartidor_id"] != g.usuario["id"]:
        raise no_encontrado()
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


@app.get(f"{P}/entregas/<int:eid>/recorrido")
@requiere("entregas.ver")
def recorrido(eid):
    _entrega(eid, para_cierre=True)
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


# --------------------------------------------------------------------
PAG = [("pagina", "query", "integer", "Página"), ("por_pagina", "query", "integer", "1 a 100")]
ID = [("id", "path", "integer", "Id de la entrega")]
documentar(app, "GET", f"{P}/entregas/mias", "Mis entregas", permisos=["entregas.ver"], parametros=PAG,
           descripcion="Paradas abiertas del repartidor en el turno de hoy (RN25), en orden de ruta.",
           respuestas={200: ("Página de paradas", "EntregaLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/entregas", "Entregas del ámbito", permisos=["entregas.ver"], parametros=PAG + [
           ("estado_pedido", "query", "string", "Estado del pedido"), ("abiertas", "query", "boolean", "true|false"),
           ("repartidor_id", "query", "integer", "Repartidor")],
           descripcion="Repartidor: las suyas. Operador: las de su microhub. Administrador y auditor: todas.",
           respuestas={200: ("Página de entregas", "EntregaLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/entregas/{{id}}", "Detalle de la entrega", permisos=["entregas.ver"], parametros=ID,
           descripcion="Cliente, domicilio y líneas. El repartidor deja de ver el domicilio al cerrar (RN26).",
           respuestas={200: ("Detalle", "EntregaDetalle.ok")}, errores=[403, 404])
documentar(app, "POST", f"{P}/entregas/{{id}}/resultado", "Registrar y cerrar la entrega", permisos=["entregas.cerrar"],
           parametros=ID, cuerpo="ResultadoEntrega.parcial", solo_json=True,
           descripcion="Idempotente por `id_cliente_local`: mismo UUID → 200 con duplicado=true; la entrega ya "
                       "cerrada con otro UUID → 409. Reglas: entregado cobra el total (RN27); parcial indica líneas, "
                       "unidades devueltas y motivo (RN28); fallida exige incidencia y no cobra (RN29); el repartidor "
                       "adjunta evidencia. Devuelve inventario con fn_devolver_inventario y avisa al cliente.",
           respuestas={201: ("Cierre aplicado", "ResultadoEntregaRespuesta.ok"),
                       200: ("Reintento del mismo cierre (duplicado=true)", "ResultadoEntregaRespuesta.ok")},
           errores=[400, 403, 404, 409, 422])
documentar(app, "POST", f"{P}/entregas/{{id}}/ubicaciones", "Enviar puntos GPS", permisos=["entregas.cerrar", "entregas.ver"],
           parametros=ID, cuerpo="UbicacionesLote.ok", solo_json=True,
           descripcion="Hasta 500 puntos por lote; se guardan en MongoDB (ubicaciones_entrega, índice 2dsphere).",
           respuestas={201: ("Puntos guardados", "UbicacionesRecibidas.ok")}, errores=[400, 403, 404, 422])
documentar(app, "GET", f"{P}/entregas/{{id}}/recorrido", "Resumen del recorrido", permisos=["entregas.ver"],
           parametros=ID, descripcion="Agregación en MongoDB ($match, $sort, $group) sobre los puntos guardados.",
           respuestas={200: ("Recorrido", "Recorrido.ok")}, errores=[403, 404])
