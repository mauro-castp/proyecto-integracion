"""
Servicio de pedidos · puerto 5104 · contrato v1

  GET  /api/v1/pedidos                    página de pedidos visibles (estado, q, desde, hasta, microhub_id, zona_id)
  GET  /api/v1/pedidos/{id}               detalle con cliente, domicilio y líneas
  GET  /api/v1/pedidos/{id}/historial     cambios de estado (historial_estatus)
  POST /api/v1/pedidos/{id}/estado        cambio de estado (solo JSON); el motor valida la transición
  GET  /api/v1/pedidos/resumen            pedidos, unidades, venta y clientes por día y zona (lo usa demanda)
  GET  /api/v1/pedidos/ventas             unidades y venta por producto (lo usa surtido)
  GET  /api/v1/pedidos/listos             pedidos listos para despachar, con coordenadas (lo usa rutas)

El ámbito de cada perfil lo decide PostgreSQL con fn_pedidos_visibles
(RN22: operador solo su microhub; RN25: repartidor solo sus entregas del
turno; cliente solo los suyos). Analista ve todo; supervisor, su microhub.
"""
import datetime as dt

from flask import g

from comun import config
from comun.base import (crear_app, documentar, filtro_entero, filtro_fecha, filtro_opcion, leer_cuerpo,
                        leer_paginacion, lista, paginacion, requiere, responder, texto_busqueda, tiene)
from comun.base_errores import ErrorApi, conflicto, filtro_invalido, no_encontrado, prohibido
from comun.datos import conexion, consultar, parametro
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


# --------------------------------------------------------------------
# Resúmenes para los servicios de análisis (demanda, surtido, rutas)
# --------------------------------------------------------------------
def hoy():
    return dt.datetime.now(ZONA).date()


def _rango(defecto_dias):
    f_desde, f_hasta = filtro_fecha("desde"), filtro_fecha("hasta")
    f_hasta = f_hasta or hoy()
    f_desde = f_desde or f_hasta - dt.timedelta(days=defecto_dias)
    if f_desde > f_hasta:
        raise ErrorApi(400, "FILTRO_INVALIDO", "desde no puede ser posterior a hasta.")
    if (f_hasta - f_desde).days > 400:
        raise ErrorApi(400, "FILTRO_INVALIDO", "El rango no puede pasar de 400 días.")
    return f_desde, f_hasta


@app.get(f"{P}/pedidos/resumen")
@requiere("pedidos.ver", "reportes.ver")
def resumen():
    """Pedidos, unidades, venta y clientes por día y zona (o por día, zona y categoría). Sin pedidos cancelados."""
    pagina, por, desde = leer_paginacion(defecto=100)
    f_desde, f_hasta = _rango(30)
    agrupar = filtro_opcion("agrupar", ["dia_zona", "dia_zona_categoria"]) or "dia_zona"
    mh, zona = filtro_entero("microhub_id"), filtro_entero("zona_id")
    src, args = fuente()
    where = ["p.estado <> 'cancelado'", f"(p.creado_en AT TIME ZONE '{config.ZONA_HORARIA}')::date BETWEEN %s AND %s"]
    args = [*args, f_desde, f_hasta]
    if mh:
        where.append("p.microhub_id = %s"); args.append(mh)
    if zona:
        where.append("p.zona_id = %s"); args.append(zona)
    w = " AND ".join(where)
    dia = f"(p.creado_en AT TIME ZONE '{config.ZONA_HORARIA}')::date"
    if agrupar == "dia_zona":
        base = (f"SELECT {dia} AS fecha, p.zona_id, NULL::integer AS categoria_id, count(*) AS pedidos, "
                f"COALESCE(sum(d.unidades), 0)::integer AS unidades, COALESCE(sum(p.subtotal), 0) AS venta, "
                f"count(DISTINCT p.cliente_id) AS clientes FROM {src} p "
                f"LEFT JOIN (SELECT pedido_id, sum(cantidad) AS unidades FROM pedido_detalle GROUP BY pedido_id) d ON d.pedido_id = p.id "
                f"WHERE {w} GROUP BY 1, 2")
    else:
        base = (f"SELECT {dia} AS fecha, p.zona_id, pr.categoria_id, count(DISTINCT p.id) AS pedidos, "
                f"sum(d.cantidad)::integer AS unidades, sum(d.importe) AS venta, 0 AS clientes FROM {src} p "
                f"JOIN pedido_detalle d ON d.pedido_id = p.id JOIN producto pr ON pr.id = d.producto_id "
                f"WHERE {w} GROUP BY 1, 2, 3")
    total = consultar(f"SELECT count(*) AS n FROM ({base}) t", args, una=True)["n"]
    filas = consultar(f"SELECT * FROM ({base}) t ORDER BY fecha, zona_id, categoria_id NULLS FIRST LIMIT %s OFFSET %s", (*args, por, desde))
    sin_atender = {}
    if agrupar == "dia_zona" and filas and tiene("reportes.ver") and g.usuario["rol"] not in ("operador", "supervisor") and not mh:
        # La demanda que no se pudo atender no pertenece a un microhub: solo se suma en las consultas de toda la red.
        for r in consultar(f"SELECT (fecha AT TIME ZONE '{config.ZONA_HORARIA}')::date AS fecha, zona_id, count(*) AS n "
                           f"FROM demanda_no_atendida WHERE zona_id IS NOT NULL AND (fecha AT TIME ZONE '{config.ZONA_HORARIA}')::date "
                           f"BETWEEN %s AND %s GROUP BY 1, 2", (f_desde, f_hasta)):
            sin_atender[(r["fecha"], r["zona_id"])] = r["n"]
    return lista(filas, paginacion(pagina, por, total), "fila", "resumen_pedidos",
                 lambda f: {"fecha": f["fecha"].isoformat(), "zona_id": f["zona_id"], "categoria_id": f["categoria_id"],
                            "pedidos": f["pedidos"], "unidades": f["unidades"], "venta": dinero(f["venta"]),
                            "clientes": f["clientes"], "no_atendidos": sin_atender.get((f["fecha"], f["zona_id"]), 0)})


@app.get(f"{P}/pedidos/ventas")
@requiere("pedidos.ver", "reportes.ver")
def ventas():
    """Unidades y venta de cada producto en el rango (sin cancelados ni pedidos que aún no se asignan)."""
    pagina, por, desde = leer_paginacion(defecto=100)
    f_desde, f_hasta = _rango(int(parametro("ventana_analisis_dias", 90)))
    mh = filtro_entero("microhub_id")
    src, args = fuente()
    where = ["p.estado NOT IN ('cancelado', 'creado', 'pendiente_asignacion')",
             f"(p.creado_en AT TIME ZONE '{config.ZONA_HORARIA}')::date BETWEEN %s AND %s"]
    args = [*args, f_desde, f_hasta]
    if mh:
        where.append("p.microhub_id = %s"); args.append(mh)
    base = (f"SELECT d.producto_id, sum(d.cantidad)::integer AS unidades, sum(d.importe) AS venta, count(DISTINCT p.id) AS pedidos "
            f"FROM {src} p JOIN pedido_detalle d ON d.pedido_id = p.id WHERE {' AND '.join(where)} GROUP BY d.producto_id")
    total = consultar(f"SELECT count(*) AS n FROM ({base}) t", args, una=True)["n"]
    filas = consultar(f"SELECT * FROM ({base}) t ORDER BY unidades DESC, producto_id LIMIT %s OFFSET %s", (*args, por, desde))
    return lista(filas, paginacion(pagina, por, total), "producto", "ventas_pedidos",
                 lambda f: {"producto_id": f["producto_id"], "unidades": f["unidades"], "venta": dinero(f["venta"]), "pedidos": f["pedidos"]})


@app.get(f"{P}/pedidos/listos")
@requiere("entregas.asignar", "rutas.planear")
def listos():
    """Pedidos ya preparados de un microhub, con las coordenadas de entrega, para armar rutas."""
    pagina, por, desde = leer_paginacion(defecto=100)
    mh = filtro_entero("microhub_id")
    if not mh:
        raise filtro_invalido("microhub_id", "microhub_id es obligatorio.")
    src, args = fuente()
    base = (f"FROM {src} p JOIN domicilio dm ON dm.id = p.domicilio_id JOIN zona z ON z.id = p.zona_id "
            f"WHERE p.microhub_id = %s AND p.estado = 'en_preparacion' AND p.listo_en IS NOT NULL")
    total = consultar(f"SELECT count(*) AS n {base}", (*args, mh), una=True)["n"]
    filas = consultar(f"SELECT p.id, p.folio, p.zona_id, z.nombre AS zona, dm.latitud, dm.longitud, p.total, p.listo_en {base} "
                      f"ORDER BY p.listo_en, p.id LIMIT %s OFFSET %s", (*args, mh, por, desde))
    return lista(filas, paginacion(pagina, por, total), "pedido", "pedidos_listos",
                 lambda f: {"id": f["id"], "folio": f["folio"], "zona": {"id": f["zona_id"], "nombre": f["zona"]},
                            "latitud": numero(f["latitud"]), "longitud": numero(f["longitud"]), "total": dinero(f["total"]),
                            "listo_en": fecha(f["listo_en"])})


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
documentar(app, "GET", f"{P}/pedidos/resumen", "Resumen de pedidos por día y zona", permisos=["pedidos.ver", "reportes.ver"],
           parametros=[("pagina", "query", "integer", "Página"), ("por_pagina", "query", "integer", "1 a 100 (100 por omisión)"),
                       ("desde", "query", "string", "AAAA-MM-DD; por omisión, 30 días antes de «hasta»"), ("hasta", "query", "string", "AAAA-MM-DD; por omisión, hoy"),
                       ("agrupar", "query", "string", "dia_zona (por omisión) | dia_zona_categoria"),
                       ("microhub_id", "query", "integer", "Microhub"), ("zona_id", "query", "integer", "Zona")],
           descripcion="Lo consume el servicio de demanda. El día es el de Monterrey. No cuenta pedidos cancelados. La demanda no atendida solo se suma "
                       "en consultas de toda la red.",
           respuestas={200: ("Página de renglones", "ResumenPedidos.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/pedidos/ventas", "Ventas por producto", permisos=["pedidos.ver", "reportes.ver"],
           parametros=[("pagina", "query", "integer", "Página"), ("por_pagina", "query", "integer", "1 a 100"),
                       ("desde", "query", "string", "AAAA-MM-DD"), ("hasta", "query", "string", "AAAA-MM-DD"), ("microhub_id", "query", "integer", "Microhub")],
           descripcion="Lo consume el servicio de surtido. Sin cancelados ni pedidos que todavía no se asignan.",
           respuestas={200: ("Página de productos, los más vendidos primero", "VentasPedidos.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/pedidos/listos", "Pedidos listos para despachar", permisos=["entregas.asignar", "rutas.planear"],
           parametros=[("microhub_id", "query", "integer", "Microhub (obligatorio)"), ("pagina", "query", "integer", "Página"),
                       ("por_pagina", "query", "integer", "1 a 100")],
           descripcion="Pedidos en preparación que el operador ya marcó como listos, con las coordenadas de entrega. Lo consume el servicio de rutas.",
           respuestas={200: ("Página de pedidos listos", "PedidosListos.ok")}, errores=[400, 403])
