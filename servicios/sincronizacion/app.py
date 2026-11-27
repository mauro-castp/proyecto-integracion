"""
Servicio de sincronización · puerto 5125 · contrato v1

  POST /api/v1/sincronizacion/lotes             recibe un lote de operaciones hechas sin conexión y las aplica (solo JSON)
  GET  /api/v1/sincronizacion/lotes             lotes recibidos (cada persona ve los suyos; sincronizacion.ver, todos)
  GET  /api/v1/sincronizacion/lotes/{id}        un lote con cada una de sus operaciones
  GET  /api/v1/sincronizacion/pendientes        operaciones que no se pudieron aplicar todavía y hay que reintentar
  GET  /api/v1/sincronizacion/conflictos        operaciones que chocaron con el estado actual (sincronizacion.ver)
  GET  /api/v1/sincronizacion/estado            resumen de un dispositivo (dispositivo=...): última sincronización y pendientes
  GET  /api/v1/sincronizacion/supuestos         de dónde sale cada límite y cómo se calibra

Qué hace una app cuando no hay red: guarda cada acción con un uuid propio (`operacion_uuid`), la fecha en que ocurrió (`creada_en`) y
sus datos, y al volver la red manda todo junto en un lote. Este servicio las aplica EN EL ORDEN EN QUE OCURRIERON llamando al servicio dueño
de cada cosa con el JWT de quien las hizo, de modo que cada servicio sigue aplicando sus reglas y permisos:

  entrega_resultado        cierra una entrega            → entregas   POST /entregas/{entrega_id}/resultado
  ubicaciones              puntos GPS del recorrido      → seguimiento POST /seguimiento/{entrega_id}/ubicaciones
  movimiento_inventario    recepción, merma, ajuste      → inventario POST /inventario/movimientos
  transferencia_inventario traslado entre microhubs      → inventario POST /inventario/transferencias
  notificacion_leida       confirma la lectura           → notificaciones POST /notificaciones/{id}/leer
  pedido_nuevo             pedido del cliente sin red    → pedidos    POST /pedidos (operacion_uuid = el uuid: reenviar no duplica)

Resultado de cada operación
  aplicada   el servicio dueño la aceptó (2xx).
  conflicto  chocó con el estado actual (409), p. ej. la entrega ya la cerró otra persona o con otro uuid. Gana el servidor: no se
             reintenta ni se pisa nada; queda en /conflictos para que una persona decida.
  rechazada  no es válida (400, 403, 404, 413, 415 o 422): datos mal formados, sin permiso, algo que ya no existe, una regla de negocio.
             Reintentar el mismo contenido da lo mismo, así que no se reintenta.
  pendiente  el servicio dueño no respondió o está saturado (5xx, 429, red): NO se da por procesada; reenviar la misma operación la vuelve
             a intentar y cuenta el reintento.

Idempotencia: (dispositivo, operacion_uuid) es único. Reenviar una operación ya resuelta devuelve su resultado guardado sin volver a
llamar a nadie (`duplicada` = true); reenviar un lote completo no duplica nada. Un uuid reutilizado con otro contenido se rechaza
(UUID_REUTILIZADO). Cada operación se guarda apenas se resuelve, así que una caída a la mitad de un lote no pierde lo ya aplicado.

Responsabilidad única: recibir, ordenar, aplicar y registrar lo que las apps hicieron sin conexión. No tiene reglas de negocio propias.
"""
import datetime as dt
import hashlib
import json
import re
import uuid

from flask import g, request

from comun import config, supuestos as sup
from comun.base import (crear_app, documentar, filtro_entero, filtro_opcion, leer_cuerpo, leer_paginacion, lista, paginacion, requiere,
                        responder, tiene)
from comun.base_errores import ErrorApi, filtro_invalido, invalido, no_encontrado
from comun.clientes import llamar
from comun.datos import ahora, como_json, conexion, consultar
from comun.formatos import fecha
from comun.validar import Campo, validar

app = crear_app("sincronizacion", "Microhubs · Sincronización",
                "Recibe lotes de operaciones hechas sin conexión desde Android y escritorio y las aplica de forma idempotente.", 5125)
P = config.PREFIJO
CLIENTES = ["android", "escritorio", "web"]
ESTADOS = ["aplicada", "conflicto", "rechazada", "pendiente"]
DEFECTOS = {"sync_lote_max": 200.0, "sync_antiguedad_max_dias": 14.0, "sync_reloj_tolerancia_min": 10.0}
UUID = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
RECHAZOS = {400, 403, 404, 413, 415, 422}
CLAVES_SUPUESTOS = list(DEFECTOS)


# --------------------------------------------------------------------
# Operaciones: a qué servicio va cada una (lógica pura)
# --------------------------------------------------------------------
def _sin(datos, *llaves):
    return {k: v for k, v in datos.items() if k not in llaves}


# tipo → (servicio, llaves obligatorias en `datos`, ruta, cuerpo). La ruta y el cuerpo reciben (datos, operacion_uuid).
OPERACIONES = {
    "entrega_resultado": ("entregas", ["entrega_id"], lambda d, u: f"entregas/{int(d['entrega_id'])}/resultado",
                          lambda d, u: {**_sin(d, "entrega_id"), "id_cliente_local": u}),
    "ubicaciones": ("seguimiento", ["entrega_id", "puntos"], lambda d, u: f"seguimiento/{int(d['entrega_id'])}/ubicaciones",
                    lambda d, u: {"puntos": d["puntos"]}),
    "movimiento_inventario": ("inventario", [], lambda d, u: "inventario/movimientos", lambda d, u: {**d, "operacion_uuid": u}),
    "transferencia_inventario": ("inventario", [], lambda d, u: "inventario/transferencias", lambda d, u: {**d, "operacion_uuid": u}),
    "notificacion_leida": ("notificaciones", ["id"], lambda d, u: f"notificaciones/{int(d['id'])}/leer", lambda d, u: {}),
    "pedido_nuevo": ("pedidos", ["lineas"], lambda d, u: "pedidos", lambda d, u: {**d, "operacion_uuid": u}),
}


def huella(tipo, datos, creada_en):
    """SHA-256 del contenido de la operación: el mismo uuid con otro contenido es un error, no un reintento."""
    canon = json.dumps({"tipo": tipo, "datos": datos, "creada_en": creada_en.astimezone(dt.timezone.utc).isoformat()},
                       sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def interpretar(status, datos):
    """Respuesta del servicio dueño → (estado, código, mensaje). Ver la regla en el encabezado de este archivo."""
    err = (datos or {}).get("error") if isinstance(datos, dict) else None
    codigo, mensaje = (err or {}).get("codigo"), (err or {}).get("mensaje")
    if status is not None and 200 <= status < 300:
        ya = isinstance(datos, dict) and datos.get("duplicado") is True
        return "aplicada", None, "Ya estaba aplicada en el servicio (reintento de una operación anterior)." if ya else None
    if status == 409:
        return "conflicto", codigo or "CONFLICTO", mensaje or "Chocó con el estado actual; gana el servidor."
    if status in RECHAZOS:
        return "rechazada", codigo or "RECHAZADA", mensaje or "El servicio no aceptó la operación."
    return "pendiente", codigo or "SERVICIO_NO_DISPONIBLE", mensaje or "El servicio no pudo atenderla ahora; vuelve a enviarla."


def validar_operacion(op, u):
    """Valida el sobre de una operación. Devuelve (operacion normalizada, None) o (None, mensaje de rechazo)."""
    if not isinstance(op, dict):
        return None, "La operación debe ser un objeto."
    try:
        d = validar(op, [Campo("operacion_uuid", patron=UUID.pattern, mensaje="Debe ser un UUID."), Campo("tipo", opciones=list(OPERACIONES)),
                         Campo("creada_en", "fecha"), Campo("datos", "obj")])
    except ErrorApi as e:
        return None, "; ".join(f"{x['campo']}: {x['mensaje']}" for x in (e.detalles or [])) or e.mensaje
    datos = d["datos"]
    faltan = [k for k in OPERACIONES[d["tipo"]][1] if datos.get(k) in (None, "", [])]
    if faltan:
        return None, f"Faltan en datos: {', '.join(faltan)}."
    for k in ("entrega_id", "id"):
        if k in OPERACIONES[d["tipo"]][1] and (not isinstance(datos[k], int) or isinstance(datos[k], bool) or datos[k] < 1):
            return None, f"datos.{k} debe ser un entero positivo."
    creada = d["creada_en"]
    ahora_ = ahora()
    if creada > ahora_ + dt.timedelta(minutes=u["sync_reloj_tolerancia_min"]):
        return None, "creada_en está en el futuro: revisa el reloj del dispositivo."
    if creada < ahora_ - dt.timedelta(days=u["sync_antiguedad_max_dias"]):
        return None, f"La operación tiene más de {int(u['sync_antiguedad_max_dias'])} días sin sincronizar y ya no es confiable."
    return {"operacion_uuid": d["operacion_uuid"].lower(), "tipo": d["tipo"], "creada_en": creada, "datos": datos}, None


def ordenar(operaciones):
    """Se aplican en el orden en que ocurrieron (empate: el de llegada), pero el resultado se entrega en el orden recibido."""
    def clave(i):
        try:
            return (dt.datetime.fromisoformat(str(operaciones[i].get("creada_en", "")).replace("Z", "+00:00")).astimezone(dt.timezone.utc), i)
        except (ValueError, AttributeError):
            return (dt.datetime.max.replace(tzinfo=dt.timezone.utc), i)
    return sorted(range(len(operaciones)), key=clave)


# --------------------------------------------------------------------
# Aplicación
# --------------------------------------------------------------------
def despachar(op):
    """Llama al servicio dueño. Devuelve (estado, http_status, código, mensaje)."""
    servicio, _, ruta, cuerpo = OPERACIONES[op["tipo"]]
    try:
        status, datos = llamar(servicio, "POST", ruta(op["datos"], op["operacion_uuid"]), cuerpo=cuerpo(op["datos"], op["operacion_uuid"]))
    except ErrorApi as e:
        return "pendiente", None, e.codigo, e.mensaje
    estado, codigo, mensaje = interpretar(status, datos)
    return estado, status, codigo, mensaje


def guardar(cur, lote_id, dispositivo, op, h, estado, http_status, codigo, mensaje):
    cur.execute(
        "INSERT INTO sync_operacion (lote_id, dispositivo, operacion_uuid, tipo, creada_en, estado, codigo, mensaje, resultado, huella) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
        "ON CONFLICT (dispositivo, operacion_uuid) DO UPDATE SET estado = EXCLUDED.estado, codigo = EXCLUDED.codigo, mensaje = EXCLUDED.mensaje, "
        "resultado = EXCLUDED.resultado, intentos = sync_operacion.intentos + 1, procesada_en = now()",
        (lote_id, dispositivo, op["operacion_uuid"], op["tipo"], op["creada_en"], estado, codigo, (mensaje or "")[:300] or None,
         como_json({"http_status": http_status}), h))


def aplicar_lote(lote, u):
    """Aplica las operaciones de un lote ya validado. Devuelve la lista de resultados en el orden recibido."""
    usuario = g.usuario["id"]
    with conexion() as con, con.cursor() as cur:
        cur.execute("SELECT id, usuario_id FROM sync_lote WHERE dispositivo = %s AND lote_uuid = %s FOR UPDATE", (lote["dispositivo"], lote["lote_uuid"]))
        f = cur.fetchone()
        if f and f["usuario_id"] != usuario:
            raise ErrorApi(409, "CONFLICTO", "Ese lote ya lo envió otra persona desde ese dispositivo.")
        if f:
            lote_id = f["id"]
            cur.execute("UPDATE sync_lote SET total = GREATEST(total, %s) WHERE id = %s", (len(lote["operaciones"]), lote_id))
        else:
            cur.execute("INSERT INTO sync_lote (lote_uuid, dispositivo, cliente, usuario_id, total) VALUES (%s,%s,%s,%s,%s) RETURNING id",
                        (lote["lote_uuid"], lote["dispositivo"], lote["cliente"], usuario, len(lote["operaciones"])))
            lote_id = cur.fetchone()["id"]
    resultados = [None] * len(lote["operaciones"])
    duplicadas = 0
    for i in ordenar(lote["operaciones"]):
        crudo = lote["operaciones"][i]
        op, rechazo = validar_operacion(crudo, u)
        sobre = crudo if isinstance(crudo, dict) else {}
        base = {"operacion_uuid": str(sobre.get("operacion_uuid", ""))[:80], "tipo": str(sobre.get("tipo", ""))[:30]}
        if rechazo:                                               # un sobre mal formado no se guarda: no hay con qué calcular su huella
            resultados[i] = {**base, "estado": "rechazada", "duplicada": False, "http_status": None, "codigo": "VALIDACION", "mensaje": rechazo,
                             "reintentar": False}
            continue
        h = huella(op["tipo"], op["datos"], op["creada_en"])
        with conexion() as con, con.cursor() as cur:
            cur.execute("SELECT o.estado, o.codigo, o.mensaje, o.huella, o.resultado, l.usuario_id FROM sync_operacion o JOIN sync_lote l ON l.id = o.lote_id "
                        "WHERE o.dispositivo = %s AND o.operacion_uuid = %s FOR UPDATE OF o", (lote["dispositivo"], op["operacion_uuid"]))
            previa = cur.fetchone()
            if previa and previa["usuario_id"] != usuario:
                resultados[i] = {**base, "estado": "rechazada", "duplicada": False, "http_status": None, "codigo": "OPERACION_AJENA",
                                 "mensaje": "Ese uuid ya lo usó otra persona en este dispositivo.", "reintentar": False}
                continue
            if previa and previa["huella"] and previa["huella"] != h:
                resultados[i] = {**base, "estado": "rechazada", "duplicada": False, "http_status": None, "codigo": "UUID_REUTILIZADO",
                                 "mensaje": "Ese uuid ya se usó con otro contenido; cada operación nueva necesita su propio uuid.", "reintentar": False}
                continue
            if previa and previa["estado"] != "pendiente":
                resultados[i] = {**base, "estado": previa["estado"], "duplicada": True, "http_status": (previa["resultado"] or {}).get("http_status"),
                                 "codigo": previa["codigo"], "mensaje": previa["mensaje"], "reintentar": False}
                duplicadas += 1
                continue
        estado, http_status, codigo, mensaje = despachar(op)
        with conexion() as con, con.cursor() as cur:
            guardar(cur, lote_id, lote["dispositivo"], op, h, estado, http_status, codigo, mensaje)
        resultados[i] = {**base, "estado": estado, "duplicada": False, "http_status": http_status, "codigo": codigo, "mensaje": mensaje,
                         "reintentar": estado == "pendiente"}
    with conexion() as con, con.cursor() as cur:
        cur.execute("UPDATE sync_lote SET duplicadas = duplicadas + %s, "
                    "aplicadas = (SELECT count(*) FROM sync_operacion WHERE lote_id = %s AND estado = 'aplicada'), "
                    "conflictos = (SELECT count(*) FROM sync_operacion WHERE lote_id = %s AND estado = 'conflicto'), "
                    "rechazadas = (SELECT count(*) FROM sync_operacion WHERE lote_id = %s AND estado = 'rechazada') WHERE id = %s",
                    (duplicadas, lote_id, lote_id, lote_id, lote_id))
    return lote_id, resultados


# --------------------------------------------------------------------
# Presentación
# --------------------------------------------------------------------
SQL_LOTE = ("SELECT l.id, l.lote_uuid, l.dispositivo, l.cliente, l.usuario_id, trim(u.nombre || ' ' || COALESCE(u.apellidos, '')) AS usuario_nombre, "
            "l.recibido_en, l.total, l.aplicadas, l.duplicadas, l.conflictos, l.rechazadas, "
            "(SELECT count(*) FROM sync_operacion o WHERE o.lote_id = l.id AND o.estado = 'pendiente') AS pendientes "
            "FROM sync_lote l LEFT JOIN usuario u ON u.id = l.usuario_id ")
SQL_OPERACION = ("SELECT o.id, l.lote_uuid, o.dispositivo, o.operacion_uuid, o.tipo, o.creada_en, o.estado, o.resultado, o.codigo, o.mensaje, o.intentos, "
                 "o.procesada_en, l.usuario_id, trim(u.nombre || ' ' || COALESCE(u.apellidos, '')) AS usuario_nombre "
                 "FROM sync_operacion o JOIN sync_lote l ON l.id = o.lote_id LEFT JOIN usuario u ON u.id = l.usuario_id ")


def lote(f):
    return {"id": f["id"], "lote_uuid": f["lote_uuid"], "dispositivo": f["dispositivo"], "cliente": f["cliente"],
            "usuario": {"id": f["usuario_id"], "nombre": (f["usuario_nombre"] or "").strip() or None}, "recibido_en": fecha(f["recibido_en"]),
            "total": f["total"], "aplicadas": f["aplicadas"], "duplicadas": f["duplicadas"], "conflictos": f["conflictos"],
            "rechazadas": f["rechazadas"], "pendientes": f["pendientes"]}


def operacion(f):
    return {"id": f["id"], "lote_uuid": f["lote_uuid"], "dispositivo": f["dispositivo"], "operacion_uuid": f["operacion_uuid"], "tipo": f["tipo"],
            "creada_en": fecha(f["creada_en"]), "estado": f["estado"], "http_status": (f["resultado"] or {}).get("http_status"), "codigo": f["codigo"],
            "mensaje": f["mensaje"], "intentos": f["intentos"], "procesada_en": fecha(f["procesada_en"]),
            "usuario": {"id": f["usuario_id"], "nombre": (f["usuario_nombre"] or "").strip() or None}}


def _ambito(alias_lote="l"):
    """Quien solo puede usar la sincronización ve únicamente lo suyo; sincronizacion.ver ve todo."""
    if tiene("sincronizacion.ver"):
        return "", []
    return f" AND {alias_lote}.usuario_id = %s", [g.usuario["id"]]


# --------------------------------------------------------------------
# Rutas
# --------------------------------------------------------------------
@app.post(f"{P}/sincronizacion/lotes")
@requiere("sincronizacion.usar")
def recibir():
    u = sup.valores(DEFECTOS)
    crudo = leer_cuerpo()
    if not isinstance(crudo.get("operaciones"), list):         # validar() vuelve lista cualquier valor suelto (por el XML); aquí no
        raise invalido("operaciones", "operaciones debe ser una lista.")
    d = validar(crudo, [Campo("lote_uuid", patron=UUID.pattern, mensaje="Debe ser un UUID."),
                                Campo("dispositivo", min_len=3, max_len=60, patron=r"[A-Za-z0-9._:\-]+", mensaje="Solo letras, números y . _ : -"),
                                Campo("cliente", opciones=CLIENTES), Campo("operaciones", "lista")])
    if not isinstance(d["operaciones"], list) or not 1 <= len(d["operaciones"]) <= int(u["sync_lote_max"]):
        raise invalido("operaciones", f"Un lote lleva entre 1 y {int(u['sync_lote_max'])} operaciones.")
    d["lote_uuid"] = d["lote_uuid"].lower()
    lote_id, res = aplicar_lote(d, u)
    f = consultar(SQL_LOTE + "WHERE l.id = %s", (lote_id,), una=True)
    nuevas = any(r["estado"] == "aplicada" and not r["duplicada"] for r in res)
    cuerpo = {"id": lote_id, "lote_uuid": d["lote_uuid"], "dispositivo": d["dispositivo"], "recibido_en": fecha(f["recibido_en"]), "total": len(res),
              "aplicadas": sum(1 for r in res if r["estado"] == "aplicada"), "duplicadas": sum(1 for r in res if r["duplicada"]), "conflictos": sum(1 for r in res if r["estado"] == "conflicto"),
              "rechazadas": sum(1 for r in res if r["estado"] == "rechazada"), "pendientes": sum(1 for r in res if r["estado"] == "pendiente"),
              "operaciones": [{"operacion_uuid": r["operacion_uuid"], "tipo": r["tipo"], "estado": r["estado"], "duplicada": r["duplicada"],
                               "http_status": r["http_status"], "codigo": r["codigo"], "mensaje": r["mensaje"], "reintentar": r["reintentar"]} for r in res]}
    return responder(cuerpo, 201 if nuevas else 200, raiz="sync_lote_resultado", items={"operaciones": "operacion"})


@app.get(f"{P}/sincronizacion/lotes")
@requiere("sincronizacion.usar", "sincronizacion.ver")
def lotes():
    pagina, por, salto = leer_paginacion()
    amb, args = _ambito()
    where, args = ["true" + amb], list(args)
    uid = filtro_entero("usuario_id")
    if uid is not None:
        where.append("l.usuario_id = %s"); args.append(uid)
    cli = filtro_opcion("cliente", CLIENTES)
    if cli:
        where.append("l.cliente = %s"); args.append(cli)
    disp = (request.args.get("dispositivo") or "").strip()
    if disp:
        where.append("l.dispositivo = %s"); args.append(disp)
    w = " AND ".join(where)
    total = consultar(f"SELECT count(*) AS n FROM sync_lote l WHERE {w}", args, una=True)["n"]
    filas = consultar(f"{SQL_LOTE}WHERE {w} ORDER BY l.recibido_en DESC, l.id DESC LIMIT %s OFFSET %s", (*args, por, salto))
    return lista(filas, paginacion(pagina, por, total), "lote", "sync_lotes", lote)


@app.get(f"{P}/sincronizacion/lotes/<int:lid>")
@requiere("sincronizacion.usar", "sincronizacion.ver")
def detalle(lid):
    amb, args = _ambito()
    f = consultar(f"{SQL_LOTE}WHERE l.id = %s{amb}", (lid, *args), una=True)
    if not f:
        raise no_encontrado("No existe ese lote.")
    ops = consultar(f"{SQL_OPERACION}WHERE o.lote_id = %s ORDER BY o.creada_en, o.id", (lid,))
    return responder({**lote(f), "operaciones": [operacion(o) for o in ops]}, raiz="sync_lote", items={"operaciones": "operacion"})


def _lista_operaciones(estado, raiz):
    pagina, por, salto = leer_paginacion()
    amb, args = _ambito()
    w = f"o.estado = %s{amb}"
    total = consultar(f"SELECT count(*) AS n FROM sync_operacion o JOIN sync_lote l ON l.id = o.lote_id WHERE {w}", (estado, *args), una=True)["n"]
    filas = consultar(f"{SQL_OPERACION}WHERE {w} ORDER BY o.procesada_en DESC, o.id DESC LIMIT %s OFFSET %s", (estado, *args, por, salto))
    return lista(filas, paginacion(pagina, por, total), "operacion", raiz, operacion)


@app.get(f"{P}/sincronizacion/pendientes")
@requiere("sincronizacion.usar", "sincronizacion.ver")
def pendientes():
    return _lista_operaciones("pendiente", "sync_operaciones")


@app.get(f"{P}/sincronizacion/conflictos")
@requiere("sincronizacion.ver")
def conflictos():
    return _lista_operaciones("conflicto", "sync_operaciones")


@app.get(f"{P}/sincronizacion/estado")
@requiere("sincronizacion.usar", "sincronizacion.ver")
def estado():
    disp = (request.args.get("dispositivo") or "").strip()
    if not disp:
        raise filtro_invalido("dispositivo", "Indica el dispositivo.")
    amb, args = _ambito()
    ls = consultar(f"SELECT count(*) AS lotes, max(l.recibido_en) AS ultimo FROM sync_lote l WHERE l.dispositivo = %s{amb}", (disp, *args), una=True)
    ops = {f["estado"]: f["n"] for f in consultar(
        f"SELECT o.estado, count(*) AS n FROM sync_operacion o JOIN sync_lote l ON l.id = o.lote_id WHERE o.dispositivo = %s{amb} GROUP BY o.estado",
        (disp, *args))}
    return responder({"dispositivo": disp, "ultima_sincronizacion": fecha(ls["ultimo"]), "lotes": ls["lotes"], "aplicadas": ops.get("aplicada", 0),
                      "conflictos": ops.get("conflicto", 0), "rechazadas": ops.get("rechazada", 0), "pendientes": ops.get("pendiente", 0)},
                     raiz="sync_estado")


@app.get(f"{P}/sincronizacion/supuestos")
@requiere("sincronizacion.usar", "sincronizacion.ver")
def supuestos():
    return responder({"datos": sup.listar(DEFECTOS)}, raiz="supuestos_sincronizacion", items={"datos": "supuesto"})


# --------------------------------------------------------------------
# Documentación
# --------------------------------------------------------------------
PAG = [("pagina", "query", "integer", "Página"), ("por_pagina", "query", "integer", "1 a 100")]
documentar(app, "POST", f"{P}/sincronizacion/lotes", "Enviar un lote de operaciones hechas sin conexión", permisos=["sincronizacion.usar"],
           cuerpo="SyncLoteNuevo.ok", solo_json=True,
           descripcion="Cada operación lleva su `operacion_uuid`, `tipo` (entrega_resultado, ubicaciones, movimiento_inventario, transferencia_inventario, pedido_nuevo, "
                       "notificacion_leida), `creada_en` y `datos` (el mismo cuerpo que recibiría el servicio dueño). Se aplican en el orden en que ocurrieron. "
                       "Estados: aplicada, conflicto (gana el servidor), rechazada (no reintentar) y pendiente (reenviar). Reenviar lo ya resuelto no repite nada: "
                       "`duplicada` = true. 201 si algo se aplicó, 200 si no.",
           respuestas={201: ("Resultado de cada operación", "SyncLoteResultado.ok")}, errores=[400, 403, 409, 415, 422])
documentar(app, "GET", f"{P}/sincronizacion/lotes", "Lotes recibidos", permisos=["sincronizacion.usar", "sincronizacion.ver"],
           parametros=PAG + [("usuario_id", "query", "integer", "Solo con sincronizacion.ver"), ("cliente", "query", "string", "android | escritorio | web"),
                             ("dispositivo", "query", "string", "Identificador del dispositivo")],
           respuestas={200: ("Página de lotes", "SyncLoteLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/sincronizacion/lotes/{{id}}", "Un lote con sus operaciones", permisos=["sincronizacion.usar", "sincronizacion.ver"],
           parametros=[("id", "path", "integer", "Id del lote")], respuestas={200: ("Lote y operaciones", "SyncLote.ok")}, errores=[403, 404])
documentar(app, "GET", f"{P}/sincronizacion/pendientes", "Operaciones por reintentar", permisos=["sincronizacion.usar", "sincronizacion.ver"], parametros=PAG,
           respuestas={200: ("Página de operaciones pendientes", "SyncOperacionLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/sincronizacion/conflictos", "Operaciones en conflicto", permisos=["sincronizacion.ver"], parametros=PAG,
           respuestas={200: ("Página de operaciones en conflicto", "SyncOperacionLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/sincronizacion/estado", "Estado de sincronización de un dispositivo", permisos=["sincronizacion.usar", "sincronizacion.ver"],
           parametros=[("dispositivo", "query", "string", "Identificador del dispositivo")], respuestas={200: ("Resumen del dispositivo", "SyncEstado.ok")},
           errores=[400, 403])
documentar(app, "GET", f"{P}/sincronizacion/supuestos", "Límites de la sincronización y su justificación", permisos=["sincronizacion.usar", "sincronizacion.ver"],
           respuestas={200: ("Valor, origen y cómo calibrar cada límite", "SupuestosSincronizacion.ok")}, errores=[403])
