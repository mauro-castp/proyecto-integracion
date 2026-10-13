"""
Servicio de pedidos · puerto 5104 · contrato v1

  GET  /api/v1/pedidos                    página de pedidos visibles (estado, q, desde, hasta, microhub_id, zona_id)
  GET  /api/v1/pedidos/{id}               detalle con cliente, domicilio y líneas
  GET  /api/v1/pedidos/{id}/historial     cambios de estado (historial_estatus)
  POST /api/v1/pedidos/{id}/estado        cambio de estado (solo JSON); el motor valida la transición

El ámbito de cada perfil lo decide PostgreSQL con fn_pedidos_visibles
(RN22: operador solo su microhub; RN25: repartidor solo sus entregas del
turno; cliente solo los suyos). Analista ve todo; supervisor, su microhub.
"""
import datetime as dt

from flask import g

from comun import config
from comun.base import (crear_app, documentar, filtro_entero, filtro_fecha, filtro_opcion, leer_cuerpo,
                        leer_paginacion, lista, paginacion, requiere, responder, texto_busqueda)
from comun.base_errores import ErrorApi, conflicto, no_encontrado, prohibido
from comun.datos import conexion, consultar
from comun.formatos import ZONA, dinero, fecha, numero
from comun.validar import Campo, validar

app = crear_app("pedidos", "Microhubs · Pedidos", "Consulta de pedidos, detalle, historial y cambio de estado.", 5104)
P = config.PREFIJO
ESTADOS = ["creado", "pendiente_asignacion", "asignado", "en_preparacion", "en_ruta", "entregado",
           "entrega_parcial", "entrega_fallida", "cancelado"]
CIERRES = {"entregado", "entrega_parcial", "entrega_fallida"}


def fuente():
    """Conjunto de pedidos que el perfil puede ver, como SQL + argumentos."""
    u = g.usuario
    if u["rol"] == "analista":
        return "pedido", []
    if u["rol"] == "supervisor":
        return "(SELECT * FROM pedido WHERE microhub_id = %s)", [u.get("microhub_id")]
    return "fn_pedidos_visibles(%s)", [u["id"]]


def pedido(f):
    return {"id": f["id"], "folio": f["folio"], "estado": f["estado"],
            "zona": {"id": f["zona_id"], "nombre": f["zona"]}, "microhub_id": f["microhub_id"],
            "total": dinero(f["total"]), "creado_en": fecha(f["creado_en"])}


def _visible(pid):
    src, args = fuente()
    f = consultar(f"SELECT p.*, p.estado::text AS estado, z.nombre AS zona FROM {src} p "
                  "JOIN zona z ON z.id = p.zona_id WHERE p.id = %s", (*args, pid), una=True)
    if not f:
        raise no_encontrado("No existe el pedido o no está en tu ámbito.")
    return f


@app.get(f"{P}/pedidos")
@requiere("pedidos.ver", "reportes.ver")
def pedidos():
    pagina, por, desde = leer_paginacion()
    q, estado = texto_busqueda(), filtro_opcion("estado", ESTADOS)
    f_desde, f_hasta = filtro_fecha("desde"), filtro_fecha("hasta")
    mh, zona = filtro_entero("microhub_id"), filtro_entero("zona_id")
    if f_desde and f_hasta and f_desde > f_hasta:
        raise ErrorApi(400, "FILTRO_INVALIDO", "desde no puede ser posterior a hasta.")
    src, args = fuente()
    where = ["TRUE"]
    if estado:
        where.append("p.estado = %s"); args.append(estado)
    if q:
        where.append("p.folio ILIKE %s"); args.append(f"%{q}%")
    if f_desde:
        where.append("p.creado_en >= %s"); args.append(dt.datetime.combine(f_desde, dt.time(), ZONA))
    if f_hasta:
        where.append("p.creado_en < %s"); args.append(dt.datetime.combine(f_hasta + dt.timedelta(days=1), dt.time(), ZONA))
    if mh:
        where.append("p.microhub_id = %s"); args.append(mh)
    if zona:
        where.append("p.zona_id = %s"); args.append(zona)
    w = " AND ".join(where)
    total = consultar(f"SELECT count(*) AS n FROM {src} p WHERE {w}", args, una=True)["n"]
    filas = consultar(f"SELECT p.id, p.folio, p.estado::text AS estado, p.zona_id, z.nombre AS zona, p.microhub_id, "
                      f"p.total, p.creado_en FROM {src} p JOIN zona z ON z.id = p.zona_id WHERE {w} "
                      f"ORDER BY p.creado_en DESC, p.id DESC LIMIT %s OFFSET %s", (*args, por, desde))
    return lista(filas, paginacion(pagina, por, total), "pedido", "pedidos", pedido)


@app.get(f"{P}/pedidos/<int:pid>")
@requiere("pedidos.ver", "reportes.ver")
def detalle(pid):
    f = _visible(pid)
    c = consultar("SELECT u.nombre || ' ' || COALESCE(u.apellidos,'') AS nombre, u.telefono, d.calle, d.numero_ext, "
                  "d.colonia, d.latitud, d.longitud FROM pedido p JOIN cliente cl ON cl.id = p.cliente_id "
                  "JOIN usuario u ON u.id = cl.usuario_id JOIN domicilio d ON d.id = p.domicilio_id WHERE p.id = %s",
                  (pid,), una=True)
    lineas = consultar("SELECT pd.id, pd.producto_id, pr.nombre, pd.cantidad, pd.precio_unitario, pd.importe "
                       "FROM pedido_detalle pd JOIN producto pr ON pr.id = pd.producto_id WHERE pd.pedido_id = %s "
                       "ORDER BY pd.id", (pid,))
    cuerpo = {"id": f["id"], "folio": f["folio"], "estado": f["estado"],
              "cliente": {"nombre": c["nombre"].strip(), "telefono": c["telefono"]},
              "domicilio": {"calle": c["calle"], "numero_ext": c["numero_ext"], "colonia": c["colonia"],
                            "latitud": numero(c["latitud"]), "longitud": numero(c["longitud"])},
              "zona": {"id": f["zona_id"], "nombre": f["zona"]}, "microhub_id": f["microhub_id"],
              "subtotal": dinero(f["subtotal"]), "costo_envio": dinero(f["costo_envio"]), "total": dinero(f["total"]),
              "creado_en": fecha(f["creado_en"]),
              "lineas": [{"id": l["id"], "producto_id": l["producto_id"], "nombre": l["nombre"], "cantidad": l["cantidad"],
                          "precio_unitario": dinero(l["precio_unitario"]), "importe": dinero(l["importe"])} for l in lineas]}
    return responder(cuerpo, raiz="pedido_detalle")


@app.get(f"{P}/pedidos/<int:pid>/historial")
@requiere("pedidos.ver", "reportes.ver")
def historial(pid):
    _visible(pid)
    eventos = consultar("SELECT h.estado_anterior::text AS estado_anterior, h.estado_nuevo::text AS estado_nuevo, "
                        "u.correo AS usuario, h.motivo, h.fecha FROM historial_estatus h "
                        "LEFT JOIN usuario u ON u.id = h.usuario_id WHERE h.pedido_id = %s ORDER BY h.fecha, h.id", (pid,))
    return responder({"pedido_id": pid, "eventos": [{**e, "fecha": fecha(e["fecha"])} for e in eventos]},
                     raiz="historial")


@app.route(f"{P}/pedidos/<int:pid>/estado", methods=["POST", "PATCH"])
@requiere("pedidos.cambiar_estado", "pedidos.cancelar", "pedidos.reasignar")
def cambiar_estado(pid):
    d = validar(leer_cuerpo(), [Campo("estado", opciones=ESTADOS), Campo("motivo", req=False, max_len=300)])
    if d["estado"] in CIERRES:
        raise conflicto("El cierre de una entrega se registra con POST /api/v1/entregas/{id}/resultado.")
    actual = _visible(pid) if g.usuario["rol"] != "cliente" else None
    with conexion() as con, con.cursor() as cur:
        if g.usuario["rol"] == "cliente":
            cur.execute("SELECT p.id FROM pedido p JOIN cliente c ON c.id = p.cliente_id "
                        "WHERE p.id = %s AND c.usuario_id = %s", (pid, g.usuario["id"]))
            if not cur.fetchone():
                raise prohibido("Solo puedes cambiar tus propios pedidos.")
        # El trigger fn_valida_transicion decide si el perfil puede hacer la transición (RN20 a RN24).
        cur.execute("UPDATE pedido SET estado = %s, motivo_cancelacion = COALESCE(%s, motivo_cancelacion) "
                    "WHERE id = %s", (d["estado"], d.get("motivo"), pid))
        if d["estado"] == "cancelado":
            cur.execute("SELECT fn_devolver_inventario(%s, 'devolucion_cancelacion', %s)",
                        (pid, d.get("motivo") or "Cancelación por API (RN18)."))
    f = consultar("SELECT p.id, p.folio, p.estado::text AS estado, p.zona_id, z.nombre AS zona, p.microhub_id, "
                  "p.total, p.creado_en FROM pedido p JOIN zona z ON z.id = p.zona_id WHERE p.id = %s", (pid,), una=True)
    return responder(pedido(f), raiz="pedido")


documentar(app, "GET", f"{P}/pedidos", "Lista de pedidos", permisos=["pedidos.ver", "reportes.ver"],
           parametros=[("pagina", "query", "integer", "Página"), ("por_pagina", "query", "integer", "1 a 100"),
                       ("q", "query", "string", "Folio"), ("estado", "query", "string", "Uno de los 9 estados; otro valor → 400"),
                       ("desde", "query", "string", "AAAA-MM-DD (hora de Monterrey)"), ("hasta", "query", "string", "AAAA-MM-DD"),
                       ("microhub_id", "query", "integer", "Microhub"), ("zona_id", "query", "integer", "Zona")],
           descripcion="El ámbito de cada perfil lo aplica PostgreSQL (fn_pedidos_visibles).",
           respuestas={200: ("Página de pedidos", "PedidoLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/pedidos/{{id}}", "Detalle de un pedido", permisos=["pedidos.ver", "reportes.ver"],
           parametros=[("id", "path", "integer", "Id del pedido")],
           respuestas={200: ("Detalle con líneas", "PedidoDetalle.ok")}, errores=[403, 404])
documentar(app, "GET", f"{P}/pedidos/{{id}}/historial", "Historial de estados", permisos=["pedidos.ver", "reportes.ver"],
           parametros=[("id", "path", "integer", "Id del pedido")],
           respuestas={200: ("Eventos en orden", "Historial.ok")}, errores=[403, 404])
documentar(app, "POST", f"{P}/pedidos/{{id}}/estado", "Cambiar estado", cuerpo="CambioEstado.ok", solo_json=True,
           permisos=["pedidos.cambiar_estado", "pedidos.cancelar", "pedidos.reasignar"],
           parametros=[("id", "path", "integer", "Id del pedido")],
           descripcion="El trigger del motor valida la transición según el rol (tabla transicion_permitida, RN20 a "
                       "RN24) y exige motivo cuando la regla lo pide. Cancelar devuelve el inventario (RN18). Los "
                       "cierres de entrega no se hacen aquí.",
           respuestas={200: ("Pedido con su nuevo estado", "Pedido.ok")}, errores=[400, 403, 404, 409, 422])
