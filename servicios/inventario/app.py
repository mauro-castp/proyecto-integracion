"""
Servicio de inventario · puerto 5111 · contrato v1

  GET   /api/v1/inventario                           existencias por microhub y producto (estado, q, microhub_id)
  GET   /api/v1/inventario/{microhub_id}/{producto_id}   una existencia con lo reservado y lo disponible
  PATCH /api/v1/inventario/{microhub_id}/{producto_id}/minimo   cambia el mínimo (inventario.ajuste)
  GET   /api/v1/inventario/movimientos               bitácora de entradas y salidas
  POST  /api/v1/inventario/movimientos               recepción, merma, ajuste o conteo
  POST  /api/v1/inventario/transferencias            traslado atómico entre dos microhubs
  GET   /api/v1/inventario/reservas                  existencia apartada
  POST  /api/v1/inventario/reservas                  aparta existencia para una referencia
  POST  /api/v1/inventario/reservas/{id}/liberar     devuelve lo apartado a la existencia disponible
  GET   /api/v1/inventario/alertas                   faltantes: agotados, críticos y bajo el mínimo

Responsabilidad única: cuántas unidades hay de cada producto en cada microhub y cómo se mueven.
Los nombres de productos y microhubs se piden a sus servicios (clientes.mapa); este servicio no
lee sus tablas. Las salidas por pedido las hace la asignación del motor (fn_asignar_pedido) y quedan
en la misma bitácora; una reserva ligada a un pedido se consume o se libera sola cuando el pedido
se asigna o se cancela.

Disponible = existencia − reservas activas y vigentes. Un movimiento con operacion_uuid es
idempotente: repetirlo devuelve el original y no mueve la existencia dos veces.
"""
from flask import g, request

from comun import config
from comun.base import (crear_app, documentar, filtro_entero, filtro_fecha, filtro_opcion, leer_cuerpo,
                        leer_paginacion, lista, limitar_microhub, paginacion, requiere, responder, texto_busqueda, tiene)
from comun.base_errores import ErrorApi, conflicto, invalido, no_encontrado
from comun.clientes import mapa
from comun.datos import conexion, consultar, parametro
from comun.formatos import fecha
from comun.validar import Campo, validar

app = crear_app("inventario", "Microhubs · Inventario",
                "Existencias por microhub, movimientos, transferencias, reservas y alertas de faltantes.", 5111)
P = config.PREFIJO
TIPOS_MOVIMIENTO = ["recepcion", "merma", "ajuste", "conteo"]
REFERENCIAS_RESERVA = ["pedido", "transferencia", "abastecimiento", "manual"]
ESTADOS = {"agotado": "disponible <= 0",
           "bajo_minimo": "disponible > 0 AND minimo > 0 AND disponible <= minimo",
           "normal": "disponible > 0 AND (minimo = 0 OR disponible > minimo)"}


# --------------------------------------------------------------------
# Presentación
# --------------------------------------------------------------------
def nombres():
    return mapa("productos", "productos"), mapa("microhubs", "microhubs")


def refs(f, prod, hubs):
    p, m = prod.get(f["producto_id"]), hubs.get(f["microhub_id"])
    return {"microhub": {"id": f["microhub_id"], "nombre": m["nombre"] if m else None},
            "producto": {"id": f["producto_id"], "clave_interna": p["clave_interna"] if p else None,
                         "nombre": p["nombre"] if p else None}}


def estado_de(disponible, minimo):
    if disponible <= 0:
        return "agotado"
    return "bajo_minimo" if minimo > 0 and disponible <= minimo else "normal"


def existencia(f, prod, hubs):
    return {**refs(f, prod, hubs), "existencia": f["existencia"], "minimo": f["minimo"], "reservado": f["reservado"],
            "disponible": f["disponible"], "estado": estado_de(f["disponible"], f["minimo"]),
            "actualizado_en": fecha(f["actualizado_en"])}


def movimiento(f):
    return {"id": f["id"], "microhub_id": f["microhub_id"], "producto_id": f["producto_id"], "tipo": f["tipo"],
            "cantidad": f["cantidad"], "existencia_resultante": f["existencia_resultante"],
            "referencia": {"tipo": f["referencia_tipo"], "id": str(f["referencia_id"])} if f["referencia_tipo"] else None,
            "motivo": f["motivo"], "usuario_id": f["usuario_id"], "fecha": fecha(f["fecha"])}


def reserva(f):
    return {"id": f["id"], "microhub_id": f["microhub_id"], "producto_id": f["producto_id"], "cantidad": f["cantidad"],
            "estado": f["estado"], "vigente": bool(f["vigente"]),
            "referencia": {"tipo": f["referencia_tipo"], "id": f["referencia_id"]},
            "creada_en": fecha(f["creada_en"]), "vence_en": fecha(f["vence_en"]), "cerrada_en": fecha(f["cerrada_en"])}


SQL_MOVIMIENTO = ("id, microhub_id, producto_id, tipo::text AS tipo, cantidad, existencia_resultante, referencia_tipo, "
                  "referencia_id, motivo, usuario_id, fecha")
SQL_RESERVA = ("id, microhub_id, producto_id, cantidad, estado, referencia_tipo, referencia_id, creada_en, vence_en, "
               "cerrada_en, (estado = 'activa' AND vence_en > now()) AS vigente")


def productos_que_coinciden(q, prod):
    if not prod:
        raise ErrorApi(503, "SERVICIO_NO_DISPONIBLE", "No se pudo buscar por nombre: el servicio de productos no responde.")
    q = q.lower()
    return [pid for pid, p in prod.items() if q in p["nombre"].lower() or q in p["clave_interna"].lower()] or [0]


def validar_referencia(valor, opciones=None, numerica=False):
    ref = validar(valor, [Campo("tipo", opciones=opciones, max_len=30), Campo("id", min_len=1, max_len=40)], prefijo="referencia.")
    if numerica and not ref["id"].isdigit():
        raise invalido("referencia.id", "Debe ser un número entero.")
    return ref


def bloquear(cur, microhub_id, producto_id, crear=False):
    """Toma la fila de inventario con FOR UPDATE; si no existe y `crear`, la abre en cero."""
    if crear:
        cur.execute("INSERT INTO inventario (microhub_id, producto_id, existencia, minimo) VALUES (%s, %s, 0, 0) "
                    "ON CONFLICT DO NOTHING", (microhub_id, producto_id))
    cur.execute("SELECT existencia, minimo FROM inventario WHERE microhub_id = %s AND producto_id = %s FOR UPDATE",
                (microhub_id, producto_id))
    f = cur.fetchone()
    if not f:
        raise no_encontrado("Ese producto no tiene inventario en el microhub.")
    return f


def reservado_activo(cur, microhub_id, producto_id):
    cur.execute("SELECT COALESCE(sum(cantidad), 0)::integer AS n FROM inventario_reserva "
                "WHERE microhub_id = %s AND producto_id = %s AND estado = 'activa' AND vence_en > now()",
                (microhub_id, producto_id))
    return cur.fetchone()["n"]


def anotar(cur, microhub_id, producto_id, tipo, cantidad, resultante, ref=None, motivo=None, uuid=None):
    cur.execute(f"INSERT INTO movimiento_inventario (microhub_id, producto_id, tipo, cantidad, existencia_resultante, "
                f"referencia_tipo, referencia_id, motivo, usuario_id, operacion_uuid) "
                f"VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING {SQL_MOVIMIENTO}",
                (microhub_id, producto_id, tipo, cantidad, resultante, ref["tipo"] if ref else None,
                 int(ref["id"]) if ref else None, motivo, g.usuario["id"], uuid))
    return cur.fetchone()


# --------------------------------------------------------------------
# Existencias
# --------------------------------------------------------------------
@app.get(f"{P}/inventario")
@requiere("inventario.ver")
def existencias():
    pagina, por, desde = leer_paginacion()
    estado, q = filtro_opcion("estado", list(ESTADOS)), texto_busqueda()
    hub = limitar_microhub(filtro_entero("microhub_id"))
    pid = filtro_entero("producto_id")
    prod, hubs = nombres()
    where, args = ["TRUE"], []
    if hub:
        where.append("microhub_id = %s"); args.append(hub)
    if pid:
        where.append("producto_id = %s"); args.append(pid)
    if estado:
        where.append(f"({ESTADOS[estado]})")
    if q:
        where.append("producto_id = ANY(%s)"); args.append(productos_que_coinciden(q, prod))
    w = " AND ".join(where)
    total = consultar(f"SELECT count(*) AS n FROM v_inventario_disponible WHERE {w}", args, una=True)["n"]
    filas = consultar(f"SELECT * FROM v_inventario_disponible WHERE {w} ORDER BY microhub_id, producto_id LIMIT %s OFFSET %s",
                      (*args, por, desde))
    return lista(filas, paginacion(pagina, por, total), "existencia", "existencias", lambda f: existencia(f, prod, hubs))


def _una(mid, pid):
    limitar_microhub(mid)
    f = consultar("SELECT * FROM v_inventario_disponible WHERE microhub_id = %s AND producto_id = %s", (mid, pid), una=True)
    if not f:
        raise no_encontrado("Ese producto no tiene inventario en el microhub.")
    return f


@app.get(f"{P}/inventario/<int:mid>/<int:pid>")
@requiere("inventario.ver")
def existencia_una(mid, pid):
    prod, hubs = nombres()
    return responder(existencia(_una(mid, pid), prod, hubs), raiz="existencia")


@app.route(f"{P}/inventario/<int:mid>/<int:pid>/minimo", methods=["PATCH", "PUT"])
@requiere("inventario.ajuste")
def cambiar_minimo(mid, pid):
    d = validar(leer_cuerpo("minimo_nuevo"), [Campo("minimo", "int", minimo=0, maximo=100000)])
    limitar_microhub(mid)
    with conexion() as con, con.cursor() as cur:
        bloquear(cur, mid, pid)
        cur.execute("UPDATE inventario SET minimo = %s, actualizado_en = now() WHERE microhub_id = %s AND producto_id = %s",
                    (d["minimo"], mid, pid))
    prod, hubs = nombres()
    return responder(existencia(_una(mid, pid), prod, hubs), raiz="existencia")


# --------------------------------------------------------------------
# Movimientos
# --------------------------------------------------------------------
@app.get(f"{P}/inventario/movimientos")
@requiere("inventario.ver")
def movimientos():
    pagina, por, desde = leer_paginacion()
    tipo = filtro_opcion("tipo", ["recepcion", "salida_pedido", "devolucion_cancelacion", "devolucion_parcial", "merma",
                                  "ajuste", "conteo", "transferencia_salida", "transferencia_entrada"])
    hub, pid = limitar_microhub(filtro_entero("microhub_id")), filtro_entero("producto_id")
    f_desde, f_hasta = filtro_fecha("desde"), filtro_fecha("hasta")
    if f_desde and f_hasta and f_desde > f_hasta:
        raise ErrorApi(400, "FILTRO_INVALIDO", "desde no puede ser posterior a hasta.")
    where, args = ["TRUE"], []
    for cond, valor in (("microhub_id = %s", hub), ("producto_id = %s", pid), ("tipo = %s", tipo)):
        if valor:
            where.append(cond); args.append(valor)
    if f_desde:
        where.append("fecha >= %s::date"); args.append(f_desde)
    if f_hasta:
        where.append("fecha < %s::date + 1"); args.append(f_hasta)
    w = " AND ".join(where)
    total = consultar(f"SELECT count(*) AS n FROM movimiento_inventario WHERE {w}", args, una=True)["n"]
    filas = consultar(f"SELECT {SQL_MOVIMIENTO} FROM movimiento_inventario WHERE {w} "
                      f"ORDER BY fecha DESC, id DESC LIMIT %s OFFSET %s", (*args, por, desde))
    return lista(filas, paginacion(pagina, por, total), "movimiento", "movimientos", movimiento)


@app.post(f"{P}/inventario/movimientos")
@requiere("inventario.movimiento", "inventario.ajuste")
def registrar_movimiento():
    d = validar(leer_cuerpo("movimiento_nuevo"), [
        Campo("microhub_id", "int", minimo=1), Campo("producto_id", "int", minimo=1), Campo("tipo", opciones=TIPOS_MOVIMIENTO),
        Campo("cantidad", "int", minimo=-1000000, maximo=1000000), Campo("motivo", req=False, nulo=True, max_len=300),
        Campo("referencia", "obj", req=False, nulo=True), Campo("operacion_uuid", req=False, nulo=True, min_len=8, max_len=80)])
    tipo, cant = d["tipo"], d["cantidad"]
    if tipo in ("recepcion", "merma") and cant < 1:
        raise invalido("cantidad", "Debe ser mayor que cero.")
    if tipo == "ajuste" and cant == 0:
        raise invalido("cantidad", "Un ajuste no puede ser cero.")
    if tipo == "conteo" and cant < 0:
        raise invalido("cantidad", "La existencia contada no puede ser negativa.")
    if tipo != "recepcion" and not (d.get("motivo") or "").strip():
        raise invalido("motivo", f"Una {tipo} necesita el motivo.")
    ref = validar_referencia(d["referencia"], numerica=True) if d.get("referencia") else None
    mid, pid, uuid = limitar_microhub(d["microhub_id"]), d["producto_id"], d.get("operacion_uuid")

    if uuid:
        previo = consultar(f"SELECT {SQL_MOVIMIENTO} FROM movimiento_inventario WHERE operacion_uuid = %s", (uuid,), una=True)
        if previo:
            if (previo["microhub_id"], previo["producto_id"]) != (mid, pid):
                raise conflicto("Esa operacion_uuid ya se usó con otro microhub o producto.")
            return responder({"movimiento": movimiento(previo), "duplicado": True}, raiz="movimiento_registrado")

    with conexion() as con, con.cursor() as cur:
        actual = bloquear(cur, mid, pid, crear=(tipo == "recepcion"))["existencia"]
        nueva = {"recepcion": actual + cant, "merma": actual - cant, "ajuste": actual + cant, "conteo": cant}[tipo]
        delta = nueva - actual
        if nueva < 0:
            raise conflicto(f"No hay existencia suficiente: hay {actual} y la operación resta {-delta}.")
        if tipo == "conteo" and delta == 0:
            raise conflicto("El conteo coincide con la existencia registrada; no hay nada que ajustar.")
        umbral = int(parametro("umbral_ajuste_inventario", 25))
        if tipo != "recepcion" and abs(delta) > umbral and not tiene("inventario.ajuste"):
            raise ErrorApi(403, "PROHIBIDO", f"Un movimiento de más de {umbral} unidades lo autoriza un administrador.")
        cur.execute("UPDATE inventario SET existencia = %s, actualizado_en = now() WHERE microhub_id = %s AND producto_id = %s",
                    (nueva, mid, pid))
        fila = anotar(cur, mid, pid, tipo, delta, nueva, ref, (d.get("motivo") or "").strip() or None, uuid)
    return responder({"movimiento": movimiento(fila), "duplicado": False}, 201, raiz="movimiento_registrado")


@app.post(f"{P}/inventario/transferencias")
@requiere("inventario.movimiento", "inventario.ajuste")
def transferir():
    d = validar(leer_cuerpo("transferencia_nueva"), [
        Campo("origen_microhub_id", "int", minimo=1), Campo("destino_microhub_id", "int", minimo=1),
        Campo("producto_id", "int", minimo=1), Campo("cantidad", "int", minimo=1, maximo=1000000),
        Campo("motivo", min_len=3, max_len=300), Campo("operacion_uuid", req=False, nulo=True, min_len=8, max_len=80)])
    o, t, pid, cant, uuid = d["origen_microhub_id"], d["destino_microhub_id"], d["producto_id"], d["cantidad"], d.get("operacion_uuid")
    if o == t:
        raise invalido("destino_microhub_id", "El destino debe ser distinto del origen.")
    limitar_microhub(o)

    def resultado(salida, entrada, duplicado):
        return responder({"producto_id": pid, "cantidad": cant, "duplicado": duplicado,
                          "origen": {"microhub_id": o, "existencia": salida["existencia_resultante"], "movimiento_id": salida["id"]},
                          "destino": {"microhub_id": t, "existencia": entrada["existencia_resultante"], "movimiento_id": entrada["id"]}},
                         200 if duplicado else 201, raiz="transferencia")

    if uuid:
        s = consultar(f"SELECT {SQL_MOVIMIENTO} FROM movimiento_inventario WHERE operacion_uuid = %s", (uuid + ":salida",), una=True)
        e = consultar(f"SELECT {SQL_MOVIMIENTO} FROM movimiento_inventario WHERE operacion_uuid = %s", (uuid + ":entrada",), una=True)
        if s and e:
            return resultado(s, e, True)
    motivo = d["motivo"]
    with conexion() as con, con.cursor() as cur:
        cur.execute("INSERT INTO inventario (microhub_id, producto_id, existencia, minimo) VALUES (%s, %s, 0, 0) "
                    "ON CONFLICT DO NOTHING", (t, pid))
        filas = {}
        for mid in sorted((o, t)):                                  # mismo orden siempre: sin interbloqueos
            filas[mid] = bloquear(cur, mid, pid)
        disponible = filas[o]["existencia"] - reservado_activo(cur, o, pid)
        if disponible < cant:
            raise conflicto(f"En el microhub de origen hay {disponible} disponibles y se piden {cant}.")
        n_o, n_t = filas[o]["existencia"] - cant, filas[t]["existencia"] + cant
        cur.execute("UPDATE inventario SET existencia = %s, actualizado_en = now() WHERE microhub_id = %s AND producto_id = %s", (n_o, o, pid))
        cur.execute("UPDATE inventario SET existencia = %s, actualizado_en = now() WHERE microhub_id = %s AND producto_id = %s", (n_t, t, pid))
        ref_s, ref_e = {"tipo": "transferencia", "id": str(t)}, {"tipo": "transferencia", "id": str(o)}
        salida = anotar(cur, o, pid, "transferencia_salida", -cant, n_o, ref_s, motivo, uuid + ":salida" if uuid else None)
        entrada = anotar(cur, t, pid, "transferencia_entrada", cant, n_t, ref_e, motivo, uuid + ":entrada" if uuid else None)
    return resultado(salida, entrada, False)


# --------------------------------------------------------------------
# Reservas
# --------------------------------------------------------------------
@app.get(f"{P}/inventario/reservas")
@requiere("inventario.ver")
def reservas():
    pagina, por, desde = leer_paginacion()
    estado = filtro_opcion("estado", ["activa", "liberada", "consumida"])
    hub, pid = limitar_microhub(filtro_entero("microhub_id")), filtro_entero("producto_id")
    ref_tipo = filtro_opcion("referencia_tipo", REFERENCIAS_RESERVA)
    ref_id = (request.args.get("referencia_id") or "").strip()[:40]
    where, args = ["TRUE"], []
    for cond, valor in (("microhub_id = %s", hub), ("producto_id = %s", pid), ("estado = %s", estado),
                        ("referencia_tipo = %s", ref_tipo), ("referencia_id = %s", ref_id or None)):
        if valor:
            where.append(cond); args.append(valor)
    w = " AND ".join(where)
    total = consultar(f"SELECT count(*) AS n FROM inventario_reserva WHERE {w}", args, una=True)["n"]
    filas = consultar(f"SELECT {SQL_RESERVA} FROM inventario_reserva WHERE {w} ORDER BY id DESC LIMIT %s OFFSET %s",
                      (*args, por, desde))
    return lista(filas, paginacion(pagina, por, total), "reserva", "reservas", reserva)


@app.post(f"{P}/inventario/reservas")
@requiere("inventario.movimiento", "inventario.ajuste")
def reservar():
    d = validar(leer_cuerpo("reserva_nueva"), [
        Campo("microhub_id", "int", minimo=1), Campo("producto_id", "int", minimo=1),
        Campo("cantidad", "int", minimo=1, maximo=1000000), Campo("referencia", "obj"),
        Campo("minutos", "int", req=False, nulo=True, minimo=1, maximo=1440)])
    ref = validar_referencia(d["referencia"], REFERENCIAS_RESERVA)
    mid, pid, cant = limitar_microhub(d["microhub_id"]), d["producto_id"], d["cantidad"]
    minutos = d.get("minutos") or int(parametro("reserva_minutos", 30))
    with conexion() as con, con.cursor() as cur:
        fisica = bloquear(cur, mid, pid)["existencia"]
        disponible = fisica - reservado_activo(cur, mid, pid)
        if disponible < cant:
            raise conflicto(f"No hay existencia disponible: hay {disponible} sin apartar y se piden {cant}.")
        cur.execute(f"INSERT INTO inventario_reserva (microhub_id, producto_id, cantidad, referencia_tipo, referencia_id, "
                    f"creada_por, vence_en) VALUES (%s,%s,%s,%s,%s,%s, now() + make_interval(mins => %s)) RETURNING {SQL_RESERVA}",
                    (mid, pid, cant, ref["tipo"], ref["id"], g.usuario["id"], minutos))
        fila = cur.fetchone()
    return responder(reserva(fila), 201, raiz="reserva")


@app.post(f"{P}/inventario/reservas/<int:rid>/liberar")
@requiere("inventario.movimiento", "inventario.ajuste")
def liberar(rid):
    with conexion() as con, con.cursor() as cur:
        cur.execute("SELECT microhub_id, estado FROM inventario_reserva WHERE id = %s FOR UPDATE", (rid,))
        f = cur.fetchone()
        if not f:
            raise no_encontrado("No existe esa reserva.")
        limitar_microhub(f["microhub_id"])
        if f["estado"] != "activa":
            raise conflicto(f"La reserva ya estaba {f['estado']}.")
        cur.execute(f"UPDATE inventario_reserva SET estado = 'liberada', cerrada_en = now() WHERE id = %s RETURNING {SQL_RESERVA}", (rid,))
        fila = cur.fetchone()
    return responder(reserva(fila), raiz="reserva")


# --------------------------------------------------------------------
# Alertas
# --------------------------------------------------------------------
@app.get(f"{P}/inventario/alertas")
@requiere("inventario.ver")
def alertas():
    pagina, por, desde = leer_paginacion()
    sev = filtro_opcion("severidad", ["agotado", "critica", "baja"])
    hub = limitar_microhub(filtro_entero("microhub_id"))
    pct = int(parametro("alerta_critica_pct", 50))
    prod, hubs = nombres()
    caso = ("CASE WHEN disponible <= 0 THEN 'agotado' WHEN disponible * 100 < minimo * %s THEN 'critica' ELSE 'baja' END")
    base = (f"SELECT *, GREATEST(minimo - disponible, 0) AS faltante, {caso} AS severidad FROM v_inventario_disponible "
            f"WHERE (disponible <= 0 OR (minimo > 0 AND disponible <= minimo))" + (" AND microhub_id = %s" if hub else ""))
    args = [pct] + ([hub] if hub else [])
    envoltura = f"FROM ({base}) a" + (" WHERE severidad = %s" if sev else "")
    args_f = args + ([sev] if sev else [])
    total = consultar(f"SELECT count(*) AS n {envoltura}", args_f, una=True)["n"]
    filas = consultar(f"SELECT * {envoltura} ORDER BY CASE severidad WHEN 'agotado' THEN 0 WHEN 'critica' THEN 1 ELSE 2 END, "
                      f"faltante DESC, microhub_id, producto_id LIMIT %s OFFSET %s", (*args_f, por, desde))

    def alerta(f):
        return {**refs(f, prod, hubs), "existencia": f["existencia"], "minimo": f["minimo"], "disponible": f["disponible"],
                "faltante": f["faltante"], "severidad": f["severidad"]}
    return lista(filas, paginacion(pagina, por, total), "alerta", "alertas", alerta)


# --------------------------------------------------------------------
# Documentación
# --------------------------------------------------------------------
PAG = [("pagina", "query", "integer", "Página (1…)"), ("por_pagina", "query", "integer", "1 a 100")]
HUB = ("microhub_id", "query", "integer", "Microhub. Operador y supervisor solo ven el suyo")
ID_EXISTENCIA = [("mid", "path", "integer", "Id del microhub"), ("pid", "path", "integer", "Id del producto")]
documentar(app, "GET", f"{P}/inventario", "Existencias", permisos=["inventario.ver"],
           parametros=PAG + [HUB, ("producto_id", "query", "integer", "Producto"), ("q", "query", "string", "Nombre o clave del producto"),
                             ("estado", "query", "string", "agotado | bajo_minimo | normal")],
           descripcion="Existencia física, reservada y disponible. La búsqueda por nombre usa el servicio de productos.",
           respuestas={200: ("Página de existencias", "InventarioLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/inventario/{{mid}}/{{pid}}", "Una existencia", permisos=["inventario.ver"], parametros=ID_EXISTENCIA,
           respuestas={200: ("Existencia", "Existencia.ok")}, errores=[403, 404])
documentar(app, "PATCH", f"{P}/inventario/{{mid}}/{{pid}}/minimo", "Cambiar el mínimo", permisos=["inventario.ajuste"],
           parametros=ID_EXISTENCIA, cuerpo="MinimoNuevo.ok", respuestas={200: ("Existencia con el mínimo nuevo", "Existencia.ok")},
           errores=[400, 403, 404, 422])
documentar(app, "GET", f"{P}/inventario/movimientos", "Movimientos", permisos=["inventario.ver"],
           parametros=PAG + [HUB, ("producto_id", "query", "integer", "Producto"), ("tipo", "query", "string", "Tipo de movimiento"),
                             ("desde", "query", "string", "AAAA-MM-DD"), ("hasta", "query", "string", "AAAA-MM-DD")],
           respuestas={200: ("Página de movimientos, el más reciente primero", "MovimientoLista.ok")}, errores=[400, 403])
documentar(app, "POST", f"{P}/inventario/movimientos", "Registrar un movimiento", permisos=["inventario.movimiento", "inventario.ajuste"],
           cuerpo="MovimientoNuevo.ok",
           descripcion="recepcion suma, merma resta, ajuste suma o resta (cantidad con signo) y conteo fija la existencia contada. "
                       "Merma, ajuste y conteo piden motivo; más de `umbral_ajuste_inventario` unidades lo autoriza un administrador. "
                       "Con operacion_uuid el movimiento es idempotente: un reintento devuelve el original con duplicado=true.",
           respuestas={201: ("Movimiento registrado", "MovimientoRegistrado.ok")}, errores=[400, 403, 404, 409, 422])
documentar(app, "POST", f"{P}/inventario/transferencias", "Transferir entre microhubs", permisos=["inventario.movimiento", "inventario.ajuste"],
           cuerpo="TransferenciaNueva.ok",
           descripcion="Resta del origen y suma al destino en una sola transacción, con dos movimientos enlazados. "
                       "Solo se puede mover lo disponible (sin contar lo reservado).",
           respuestas={201: ("Transferencia hecha", "Transferencia.ok")}, errores=[400, 403, 404, 409, 422])
documentar(app, "GET", f"{P}/inventario/reservas", "Reservas", permisos=["inventario.ver"],
           parametros=PAG + [HUB, ("producto_id", "query", "integer", "Producto"), ("estado", "query", "string", "activa | liberada | consumida"),
                             ("referencia_tipo", "query", "string", "pedido | transferencia | abastecimiento | manual"),
                             ("referencia_id", "query", "string", "Id de la referencia")],
           respuestas={200: ("Página de reservas", "ReservaLista.ok")}, errores=[400, 403])
documentar(app, "POST", f"{P}/inventario/reservas", "Apartar existencia", permisos=["inventario.movimiento", "inventario.ajuste"],
           cuerpo="ReservaNueva.ok",
           descripcion="Vence a los `reserva_minutos` de la configuración. Si no alcanza lo disponible responde 409.",
           respuestas={201: ("Reserva creada", "Reserva.ok")}, errores=[400, 403, 404, 409, 422])
documentar(app, "POST", f"{P}/inventario/reservas/{{id}}/liberar", "Liberar una reserva", permisos=["inventario.movimiento", "inventario.ajuste"],
           parametros=[("id", "path", "integer", "Id de la reserva")],
           respuestas={200: ("Reserva liberada", "Reserva.ok")}, errores=[403, 404, 409])
documentar(app, "GET", f"{P}/inventario/alertas", "Faltantes", permisos=["inventario.ver"],
           parametros=PAG + [HUB, ("severidad", "query", "string", "agotado | critica | baja")],
           descripcion="Productos agotados o por debajo de su mínimo. Es crítica la que está por debajo de `alerta_critica_pct` % del mínimo.",
           respuestas={200: ("Página de alertas, las más graves primero", "AlertaLista.ok")}, errores=[400, 403])
