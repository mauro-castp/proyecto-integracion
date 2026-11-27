"""
Servicio de entregas · puerto 5105 · contrato v1

  GET  /api/v1/entregas/mias                paradas abiertas del repartidor en su turno (RN25)
  GET  /api/v1/entregas/repartidores        repartidores activos y sus entregas abiertas (entregas.asignar, rutas.planear)
  GET  /api/v1/entregas                     entregas en el ámbito del perfil (estado_pedido, abiertas, repartidor_id)
  GET  /api/v1/entregas/{id}                detalle con cliente, domicilio y líneas (RN26)
  POST /api/v1/entregas/{id}/resultado      registra y cierra la entrega (solo JSON, idempotente)
  POST /api/v1/entregas/asignaciones        crea las entregas de una ruta confirmada y las asigna (entregas.asignar; lo llama rutas)

Responsabilidad única: la ejecución de la entrega (consulta de paradas y cierre con sus reglas).
El rastro GPS es del servicio de seguimiento; los archivos de evidencia, del servicio de
documentos; el estado del pedido lo cambia el trigger del motor en la misma transacción.

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
from decimal import Decimal

from bson import Int64, ObjectId
from flask import g, request
from pymongo.errors import DuplicateKeyError

from comun import config
from comun.base import (crear_app, documentar, filtro_entero, filtro_opcion, leer_cuerpo, leer_paginacion, limitar_microhub, lista,
                        paginacion, requiere, responder)
from comun.base_errores import ErrorApi, conflicto, invalido, no_encontrado
from comun.datos import ahora, conexion, consultar, mongo, mongo_disponible
from comun.formatos import dinero, fecha, numero
from comun.validar import Campo, unir_errores, validar

app = crear_app("entregas", "Microhubs · Entregas", "Entregas del repartidor y cierre idempotente con evidencia.",
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
@app.get(f"{P}/entregas/repartidores")
@requiere("entregas.asignar", "rutas.planear")
def repartidores():
    """Repartidores activos con las entregas que tienen abiertas hoy; lo consume el servicio de rutas."""
    pagina, por, desde = leer_paginacion(defecto=100)
    total = consultar("SELECT count(*) AS n FROM usuario u JOIN rol r ON r.id = u.rol_id WHERE r.clave = 'repartidor' AND u.estatus = 'activo'",
                      una=True)["n"]
    filas = consultar("SELECT u.id, u.nombre || ' ' || COALESCE(u.apellidos, '') AS nombre, "
                      "(SELECT count(*) FROM entrega e WHERE e.repartidor_id = u.id AND e.cierre_en IS NULL AND e.turno_fecha = fn_hoy()) AS abiertas "
                      "FROM usuario u JOIN rol r ON r.id = u.rol_id WHERE r.clave = 'repartidor' AND u.estatus = 'activo' "
                      "ORDER BY u.id LIMIT %s OFFSET %s", (por, desde))
    return lista(filas, paginacion(pagina, por, total), "repartidor", "repartidores",
                 lambda f: {"id": f["id"], "nombre": f["nombre"].strip(), "entregas_abiertas": f["abiertas"]})


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
    ped = filtro_entero("pedido_id")
    w, args = ambito()
    where = [w]
    if ped:
        where.append("e.pedido_id = %s"); args.append(ped)
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
# Asignación a un repartidor
# --------------------------------------------------------------------
@app.post(f"{P}/entregas")
@requiere("entregas.asignar")
def crear_entrega():
    """Crea la entrega de un pedido listo y lo pone en ruta. El trigger avisa al repartidor."""
    d = validar(leer_cuerpo("entrega_nueva"), [Campo("pedido_id", "int", minimo=1), Campo("repartidor_id", "int", minimo=1),
                                               Campo("orden_parada", "int", req=False, nulo=True, minimo=1, maximo=500)])
    with conexion() as con, con.cursor() as cur:
        cur.execute("SELECT id, microhub_id, estado::text AS estado, listo_en FROM pedido WHERE id = %s FOR UPDATE", (d["pedido_id"],))
        p = cur.fetchone()
        if not p:
            raise no_encontrado("No existe ese pedido.")
        limitar_microhub(p["microhub_id"])
        cur.execute("SELECT 1 AS x FROM entrega WHERE pedido_id = %s", (p["id"],))
        if cur.fetchone():
            raise conflicto("Ese pedido ya tiene una entrega asignada.")
        if p["estado"] != "en_preparacion" or not p["listo_en"]:
            raise conflicto("El pedido debe estar en preparación y marcado como listo.")
        cur.execute("SELECT 1 AS x FROM usuario u JOIN rol r ON r.id = u.rol_id WHERE u.id = %s AND r.clave = 'repartidor' AND u.estatus = 'activo'",
                    (d["repartidor_id"],))
        if not cur.fetchone():
            raise invalido("repartidor_id", "No es un repartidor activo.")
        cur.execute("INSERT INTO entrega (pedido_id, repartidor_id, turno_fecha, asignada_en, salida_en, orden_parada) "
                    "VALUES (%s, %s, current_date, now(), now(), %s) RETURNING id", (p["id"], d["repartidor_id"], d.get("orden_parada")))
        eid = cur.fetchone()["id"]
        cur.execute("UPDATE pedido SET estado = 'en_ruta' WHERE id = %s", (p["id"],))
    return responder({"entrega_id": eid, "pedido_id": p["id"], "repartidor_id": d["repartidor_id"], "estado_pedido": "en_ruta"}, 201,
                     raiz="entrega_creada")


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


# --------------------------------------------------------------------
# Asignación (despacho de una ruta confirmada) — entrega final
# --------------------------------------------------------------------
CAMPOS_PARADA = [Campo("pedido_id", "int", minimo=1), Campo("repartidor_id", "int", minimo=1), Campo("orden_parada", "int", minimo=1, maximo=200),
                 Campo("distancia_km", "num", req=False, nulo=True, minimo=0), Campo("minutos_estimados", "num", req=False, nulo=True, minimo=0),
                 Campo("costo_entrega_estimado", "num", req=False, nulo=True, minimo=0), Campo("plan_ruta_id", "int", req=False, nulo=True, minimo=1)]


@app.post(f"{P}/entregas/asignaciones")
@requiere("entregas.asignar")
def asignar():
    """Crea (o reasigna) la entrega de cada parada y pasa el pedido a en_ruta, TODO en una transacción: o se despachan todas las paradas
    o ninguna. El trigger trg_notificar_asignacion le manda a cada repartidor el aviso «Nueva entrega asignada» y los de auditoría dejan
    el rastro. El motor valida la transición en_preparacion → en_ruta."""
    d = validar(leer_cuerpo(), [Campo("paradas", "lista")])
    if not 1 <= len(d["paradas"]) <= 200:
        raise invalido("paradas", "Envía entre 1 y 200 paradas.")
    paradas = unir_errores(*[(lambda p=p, i=i: validar(p if isinstance(p, dict) else {}, CAMPOS_PARADA, prefijo=f"paradas[{i}]."))
                             for i, p in enumerate(d["paradas"])])
    if len({p["pedido_id"] for p in paradas}) != len(paradas):
        raise invalido("paradas", "Un pedido aparece dos veces.")
    hechas = []
    with conexion() as con, con.cursor() as cur:
        reps = {r["id"] for r in consultar("SELECT u.id FROM usuario u JOIN rol r ON r.id = u.rol_id WHERE r.clave = 'repartidor' "
                                           "AND u.estatus = 'activo' AND u.id = ANY(%s)", ([p["repartidor_id"] for p in paradas],))}
        for p in paradas:
            if p["repartidor_id"] not in reps:
                raise invalido("repartidor_id", f"El usuario {p['repartidor_id']} no es un repartidor activo.")
            cur.execute("SELECT estado::text AS estado, listo_en, microhub_id FROM pedido WHERE id = %s FOR UPDATE", (p["pedido_id"],))
            f = cur.fetchone()
            if not f:
                raise no_encontrado(f"No existe el pedido {p['pedido_id']}.")
            limitar_microhub(f["microhub_id"])                                  # el operador solo despacha su microhub (RN22)
            if f["estado"] != "en_preparacion" or f["listo_en"] is None:
                raise conflicto(f"El pedido {p['pedido_id']} no está listo para despachar (está {f['estado']}).")
            cur.execute("INSERT INTO entrega (pedido_id, repartidor_id, turno_fecha, asignada_en, salida_en, plan_ruta_id, orden_parada, distancia_km, "
                        "minutos_estimados, costo_entrega_estimado) VALUES (%s,%s,(now() AT TIME ZONE %s)::date,now(),now(),%s,%s,%s,%s,%s) "
                        "ON CONFLICT (pedido_id) DO UPDATE SET repartidor_id = EXCLUDED.repartidor_id, plan_ruta_id = EXCLUDED.plan_ruta_id, "
                        "orden_parada = EXCLUDED.orden_parada, distancia_km = EXCLUDED.distancia_km, minutos_estimados = EXCLUDED.minutos_estimados, "
                        "costo_entrega_estimado = EXCLUDED.costo_entrega_estimado, turno_fecha = EXCLUDED.turno_fecha RETURNING id",
                        (p["pedido_id"], p["repartidor_id"], config.ZONA_HORARIA, p.get("plan_ruta_id"), p["orden_parada"], p.get("distancia_km"),
                         p.get("minutos_estimados"), p.get("costo_entrega_estimado")))
            eid = cur.fetchone()["id"]
            cur.execute("UPDATE pedido SET estado = 'en_ruta' WHERE id = %s", (p["pedido_id"],))
            hechas.append({"entrega_id": eid, "pedido_id": p["pedido_id"], "repartidor_id": p["repartidor_id"], "orden_parada": p["orden_parada"]})
    return responder({"asignadas": len(hechas), "entregas": hechas}, 201, raiz="asignacion", items={"entregas": "entrega"})


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
PAG = [("pagina", "query", "integer", "Página"), ("por_pagina", "query", "integer", "1 a 100")]
ID = [("id", "path", "integer", "Id de la entrega")]
documentar(app, "GET", f"{P}/entregas/mias", "Mis entregas", permisos=["entregas.ver"], parametros=PAG,
           descripcion="Paradas abiertas del repartidor en el turno de hoy (RN25), en orden de ruta.",
           respuestas={200: ("Página de paradas", "EntregaLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/entregas", "Entregas del ámbito", permisos=["entregas.ver"], parametros=PAG + [
           ("estado_pedido", "query", "string", "Estado del pedido"), ("abiertas", "query", "boolean", "true|false"),
           ("repartidor_id", "query", "integer", "Repartidor"), ("pedido_id", "query", "integer", "Pedido")],
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
documentar(app, "GET", f"{P}/entregas/repartidores", "Repartidores disponibles", permisos=["entregas.asignar", "rutas.planear"],
           parametros=[("pagina", "query", "integer", "Página"), ("por_pagina", "query", "integer", "1 a 100")],
           descripcion="Repartidores activos y cuántas entregas tienen abiertas hoy. Lo consume el servicio de rutas.",
           respuestas={200: ("Página de repartidores", "Repartidores.ok")}, errores=[400, 403])
documentar(app, "POST", f"{P}/entregas", "Asignar una entrega", permisos=["entregas.asignar"], cuerpo="EntregaNueva.ok",
           descripcion="El pedido debe estar en preparación y listo; queda en ruta y el repartidor recibe el aviso. Un operador solo asigna los de su microhub.",
           respuestas={201: ("Entrega creada", "EntregaCreada.ok")}, errores=[400, 403, 404, 409, 422])
documentar(app, "POST", f"{P}/entregas/asignaciones", "Despachar las paradas de una ruta", permisos=["entregas.asignar"], solo_json=True,
           descripcion="Crea o reasigna la entrega de cada parada y pasa el pedido a en_ruta en una sola transacción (todas o ninguna). "
                       "Cada repartidor recibe el aviso por trigger. Lo llama el servicio de rutas al confirmar un plan con despachar=true.",
           respuestas={201: ("Paradas despachadas", None)}, errores=[400, 403, 404, 409, 422])
