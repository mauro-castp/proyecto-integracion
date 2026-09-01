"""
rutas.py — Blueprints de la aplicación
Plataforma de Microhubs · Codex Innovations · Equipo 04
"""
import json

from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, g, make_response, abort)

from nucleo import (con_actual, conexion, consultar, hashear, verificar,
                    emitir_token, revocar_token, parametro, permisos_de,
                    auditar, requiere, mensaje_de_error, r_sesion, r_cache)

publico = Blueprint("publico", __name__)
auth = Blueprint("auth", __name__)
cliente = Blueprint("cliente", __name__)
operacion = Blueprint("operacion", __name__)
admin = Blueprint("admin", __name__)


# ====================================================================
# PÚBLICO — RF12, RF13, RN01, RN11, RN34
# ====================================================================
@publico.route("/")
def catalogo():
    consulta = (request.args.get("q") or "").strip()
    categoria = request.args.get("categoria", type=int)

    sql = """
        SELECT p.id, p.clave_interna, p.nombre, p.presentacion, p.precio,
               c.nombre AS categoria,
               -- RN11 / HU27 CA2: disponibilidad general, jamás la cantidad.
               EXISTS (SELECT 1 FROM inventario i JOIN microhub m ON m.id = i.microhub_id
                        WHERE i.producto_id = p.id AND i.existencia > 0
                          AND m.estatus = 'activo') AS disponible
          FROM producto p JOIN categoria c ON c.id = p.categoria_id
         WHERE p.estatus = 'activo'
    """
    params = []
    if consulta:
        sql += " AND lower(p.nombre) LIKE %s"
        params.append(f"%{consulta.lower()}%")
    if categoria:
        sql += " AND c.id = %s"
        params.append(categoria)
    sql += " ORDER BY c.orden, p.nombre"

    return render_template("catalogo.html",
                           productos=consultar(sql, tuple(params)),
                           categorias=consultar(
                               "SELECT id, nombre FROM categoria "
                               "WHERE estatus='activo' ORDER BY orden"),
                           q=consulta, cat=categoria)


@publico.route("/cobertura")
def cobertura():
    termino = (request.args.get("zona") or "").strip()
    resultado = None
    if termino:
        zonas = consultar(
            "SELECT id, nombre, colonia, codigo_postal, "
            "       COALESCE(ticket_minimo, fn_config_num('ticket_minimo')) AS ticket, "
            "       COALESCE(costo_envio, fn_config_num('costo_envio')) AS envio, "
            "       COALESCE(envio_gratis_desde, fn_config_num('envio_gratis_desde')) AS gratis "
            "  FROM zona WHERE estatus='activo' "
            "   AND (codigo_postal = %s OR lower(colonia) LIKE %s)",
            (termino, f"%{termino.lower()}%"))

        if not zonas:
            # RN06: la consulta rechazada es dato valioso, no un callejón sin salida.
            with conexion() as con, con.cursor() as cur:
                cur.execute(
                    "INSERT INTO demanda_no_atendida (tipo, colonia_texto, cp_texto, origen) "
                    "VALUES ('fuera_cobertura', %s, %s, 'web')",
                    (termino[:120], termino[:5] if termino.isdigit() else None))
            resultado = {"estado": "fuera"}
        elif len(zonas) > 1:
            # Valles y Paseo comparten el 64103 y NO tienen las mismas
            # condiciones. Responder "sí hay cobertura" sin más sería mentir
            # sobre el ticket mínimo de una de las dos.
            resultado = {"estado": "ambiguo", "zonas": zonas}
        else:
            resultado = {"estado": "cubierto", "zona": zonas[0]}

    return render_template("cobertura.html", termino=termino, resultado=resultado)


# ====================================================================
# AUTENTICACIÓN — RF03, RF04, RF06
# ====================================================================
@auth.route("/entrar", methods=["GET", "POST"])
def entrar():
    if request.method == "GET":
        return render_template("entrar.html")

    correo = (request.form.get("correo") or "").strip().lower()
    clave = request.form.get("clave") or ""
    g.correo_intento = correo

    llave_intentos = f"auth:intentos:{correo}"
    maximo = int(parametro("intentos_fallidos_max", 5))
    bloqueo_min = int(parametro("bloqueo_minutos", 15))

    if r_sesion.exists(f"auth:bloqueo:{correo}"):
        auditar("auth", "login_fallido", "Intento sobre cuenta bloqueada.", exitoso=False)
        flash(f"Cuenta bloqueada temporalmente. Intenta en {bloqueo_min} minutos.", "alto")
        return render_template("entrar.html"), 423

    u = consultar(
        "SELECT u.id, u.nombre, u.apellidos, u.hash_contrasena, u.estatus, "
        "       u.microhub_id, r.clave AS rol "
        "  FROM usuario u JOIN rol r ON r.id = u.rol_id "
        " WHERE lower(u.correo) = %s", (correo,), una=True)

    if not u or u["estatus"] != "activo" or not verificar(clave, u["hash_contrasena"]):
        fallos = r_sesion.incr(llave_intentos)
        r_sesion.expire(llave_intentos, bloqueo_min * 60)
        if u:
            with conexion(rol="sistema") as con, con.cursor() as cur:
                cur.execute("UPDATE usuario SET intentos_fallidos = intentos_fallidos + 1 "
                            "WHERE id = %s", (u["id"],))
        if fallos >= maximo:
            r_sesion.setex(f"auth:bloqueo:{correo}", bloqueo_min * 60, "1")
            auditar("auth", "bloqueo_cuenta",
                    f"{maximo} intentos fallidos consecutivos.", exitoso=False)
            flash("Demasiados intentos. La cuenta queda bloqueada un momento.", "alto")
        else:
            auditar("auth", "login_fallido",
                    f"Intento {fallos} de {maximo}.", exitoso=False)
            flash(f"Correo o contraseña incorrectos. Intento {fallos} de {maximo}.", "alto")
        return render_template("entrar.html"), 401

    r_sesion.delete(llave_intentos)
    with conexion(u["id"], u["rol"]) as con, con.cursor() as cur:
        cur.execute("UPDATE usuario SET intentos_fallidos = 0, ultimo_acceso = now() "
                    "WHERE id = %s", (u["id"],))

    token = emitir_token(u)
    g.usuario = {"id": u["id"], "rol": u["rol"], "nombre": u["nombre"],
                 "microhub_id": u["microhub_id"]}
    auditar("auth", "login_exitoso")

    destino = request.args.get("siguiente") or url_for("publico.catalogo")
    resp = make_response(redirect(destino))
    resp.set_cookie("sesion", token, httponly=True, samesite="Lax",
                    max_age=int(parametro("jwt_acceso_minutos", 15)) * 60)
    return resp


@auth.route("/salir", methods=["POST"])
def salir():
    token = request.cookies.get("sesion")
    if getattr(g, "usuario", None):
        auditar("auth", "logout")
    revocar_token(token)
    resp = make_response(redirect(url_for("publico.catalogo")))
    resp.delete_cookie("sesion")
    flash("Sesión cerrada.", "ok")
    return resp


@auth.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "GET":
        return render_template("registro.html",
                               zonas=consultar("SELECT id, colonia, codigo_postal FROM zona "
                                               "WHERE estatus='activo' ORDER BY colonia"))
    f = request.form
    try:
        with conexion(rol="sistema") as con, con.cursor() as cur:
            cur.execute(
                "INSERT INTO usuario (nombre, apellidos, correo, telefono, hash_contrasena, rol_id) "
                "SELECT %s,%s,%s,%s,%s, r.id FROM rol r WHERE r.clave='cliente' RETURNING id",
                (f["nombre"], f["apellidos"], f["correo"].strip().lower(),
                 f.get("telefono"), hashear(f["clave"])))
            uid = cur.fetchone()["id"]
            cur.execute(
                "INSERT INTO cliente (usuario_id, aviso_privacidad_version, "
                "aviso_privacidad_aceptado_en) VALUES (%s,'AP-2026.1', now()) RETURNING id",
                (uid,))
            cid = cur.fetchone()["id"]
            z = consultar("SELECT centroide_lat, centroide_lng FROM zona WHERE id=%s",
                          (f["zona_id"],), una=True)
            cur.execute(
                "INSERT INTO domicilio (cliente_id, calle, numero_ext, colonia, codigo_postal, "
                "referencia, latitud, longitud, zona_id) "
                "SELECT %s,%s,%s, z.colonia, z.codigo_postal, %s, %s, %s, z.id "
                "  FROM zona z WHERE z.id = %s",
                (cid, f["calle"], f["numero"], f.get("referencia"),
                 z["centroide_lat"], z["centroide_lng"], f["zona_id"]))
    except Exception as e:
        flash(mensaje_de_error(e), "alto")
        return redirect(url_for("auth.registro"))

    flash("Cuenta creada. Ya puedes iniciar sesión.", "ok")
    return redirect(url_for("auth.entrar"))


# ====================================================================
# CLIENTE — RF14, RN02-RN10, RN21
# ====================================================================
def _carrito_llave():
    return f"carrito:{g.usuario['id']}"


def _carrito():
    """El carrito vive en Redis: perderlo solo cuesta volver a armarlo.
    Un pedido confirmado es otra cosa y por eso vive en PostgreSQL."""
    crudo = r_cache.get(_carrito_llave())
    return json.loads(crudo) if crudo else {}


def _guardar_carrito(c):
    if c:
        r_cache.setex(_carrito_llave(), 60 * 60 * 24, json.dumps(c))
    else:
        r_cache.delete(_carrito_llave())


@cliente.route("/carrito")
@requiere("pedidos.crear")
def carrito():
    c = _carrito()
    lineas, subtotal = [], 0
    if c:
        prods = consultar(
            "SELECT id, nombre, presentacion, precio FROM producto WHERE id = ANY(%s)",
            (list(map(int, c.keys())),))
        for p in prods:
            cant = c[str(p["id"])]
            importe = float(p["precio"]) * cant
            subtotal += importe
            lineas.append({**p, "cantidad": cant, "importe": importe})

    dom = consultar(
        "SELECT d.*, z.colonia, z.codigo_postal, z.id AS zid, "
        "       fn_ticket_minimo(z.id) AS ticket, "
        "       fn_costo_envio(z.id, %s::numeric) AS envio "
        "  FROM domicilio d JOIN zona z ON z.id = d.zona_id "
        "  JOIN cliente cl ON cl.id = d.cliente_id "
        " WHERE cl.usuario_id = %s AND d.activo", (subtotal, g.usuario["id"]), una=True)

    limite = int(parametro("limite_unidades_linea", 20))
    return render_template("carrito.html", lineas=lineas, subtotal=subtotal,
                           dom=dom, limite=limite)


@cliente.route("/carrito/agregar", methods=["POST"])
@requiere("pedidos.crear")
def agregar():
    pid = request.form["producto_id"]
    cant = max(1, int(request.form.get("cantidad", 1)))
    limite = int(parametro("limite_unidades_linea", 20))
    c = _carrito()
    nueva = c.get(pid, 0) + cant
    if nueva > limite:
        # RN09 se valida también aquí para dar el mensaje antes de confirmar,
        # pero la garantía real la impone el trigger del motor.
        flash(f"El máximo por producto es de {limite} unidades.", "medio")
        nueva = limite
    c[pid] = nueva
    _guardar_carrito(c)
    return redirect(request.referrer or url_for("publico.catalogo"))


@cliente.route("/carrito/quitar", methods=["POST"])
@requiere("pedidos.crear")
def quitar():
    c = _carrito()
    c.pop(request.form["producto_id"], None)
    _guardar_carrito(c)
    return redirect(url_for("cliente.carrito"))


@cliente.route("/pedido/confirmar", methods=["POST"])
@requiere("pedidos.crear")
def confirmar():
    c = _carrito()
    if not c:
        flash("Tu carrito está vacío.", "medio")
        return redirect(url_for("publico.catalogo"))

    try:
        with con_actual() as con, con.cursor() as cur:
            cur.execute(
                "SELECT cl.id AS cliente_id, d.id AS domicilio_id, d.zona_id "
                "  FROM cliente cl JOIN domicilio d ON d.cliente_id = cl.id AND d.activo "
                " WHERE cl.usuario_id = %s", (g.usuario["id"],))
            base = cur.fetchone()
            if not base:
                flash("Registra tu domicilio antes de pedir.", "medio")
                return redirect(url_for("cliente.carrito"))

            # Subtotal desde el precio VIGENTE, que se congelará en el detalle.
            cur.execute(
                "SELECT id, precio FROM producto WHERE id = ANY(%s) AND estatus='activo'",
                (list(map(int, c.keys())),))
            precios = {f["id"]: f["precio"] for f in cur.fetchall()}
            subtotal = sum(float(precios[int(k)]) * v for k, v in c.items() if int(k) in precios)

            cur.execute("SELECT fn_ticket_minimo(%s) AS t", (base["zona_id"],))
            ticket = float(cur.fetchone()["t"])
            if subtotal < ticket:
                # RN07/RN08. El pedido no llega a existir: un carrito no es
                # un pedido, y la FK del historial impide borrar uno creado.
                cur.execute(
                    "INSERT INTO demanda_no_atendida (tipo, zona_id, cliente_id, origen) "
                    "VALUES ('bajo_ticket_minimo', %s, %s, 'web')",
                    (base["zona_id"], base["cliente_id"]))
                con.commit()
                flash(f"Te faltan ${ticket - subtotal:,.2f} para alcanzar el mínimo "
                      f"de ${ticket:,.2f}. El envío no cuenta para ese total.", "medio")
                return redirect(url_for("cliente.carrito"))

            cur.execute("SELECT fn_costo_envio(%s, %s::numeric) AS e",
                        (base["zona_id"], subtotal))
            envio = cur.fetchone()["e"]

            cur.execute(
                "INSERT INTO pedido (cliente_id, domicilio_id, zona_id, subtotal, costo_envio) "
                "VALUES (%s,%s,%s,%s,%s) RETURNING id, folio",
                (base["cliente_id"], base["domicilio_id"], base["zona_id"], subtotal, envio))
            ped = cur.fetchone()

            for k, cant in c.items():
                if int(k) in precios:
                    cur.execute(
                        "INSERT INTO pedido_detalle (pedido_id, producto_id, cantidad, "
                        "precio_unitario) VALUES (%s,%s,%s,%s)",
                        (ped["id"], int(k), cant, precios[int(k)]))

            # El motor decide el microhub y descuenta inventario de forma atómica.
            cur.execute("SELECT * FROM fn_asignar_pedido(%s)", (ped["id"],))
            res = cur.fetchone()

        _guardar_carrito({})
        if res["asignado"]:
            flash(f"Pedido {ped['folio']} confirmado.", "ok")
        else:
            flash(f"Pedido {ped['folio']} registrado, pero ningún microhub puede "
                  f"surtirlo ahora. Queda pendiente y lo revisa un responsable.", "medio")
        return redirect(url_for("cliente.pedido", pid=ped["id"]))

    except Exception as e:
        flash(mensaje_de_error(e), "alto")
        return redirect(url_for("cliente.carrito"))


@cliente.route("/mis-pedidos")
@requiere("pedidos.ver")
def mis_pedidos():
    return render_template("mis_pedidos.html", pedidos=consultar(
        "SELECT p.id, p.folio, p.estado, p.subtotal, p.costo_envio, p.total, p.creado_en, "
        "       m.nombre AS microhub "
        "  FROM pedido p JOIN cliente c ON c.id = p.cliente_id "
        "  LEFT JOIN microhub m ON m.id = p.microhub_id "
        " WHERE c.usuario_id = %s ORDER BY p.creado_en DESC", (g.usuario["id"],)))


@cliente.route("/pedido/<int:pid>")
@requiere("pedidos.ver")
def pedido(pid):
    # RN33: el ámbito se aplica en la consulta, no ocultando el botón.
    p = consultar(
        "SELECT p.*, m.nombre AS microhub, z.colonia "
        "  FROM pedido p JOIN cliente c ON c.id = p.cliente_id "
        "  LEFT JOIN microhub m ON m.id = p.microhub_id "
        "  JOIN zona z ON z.id = p.zona_id "
        " WHERE p.id = %s AND c.usuario_id = %s", (pid, g.usuario["id"]), una=True)
    if not p:
        auditar("pedidos", "acceso_denegado", f"Pedido {pid} de otro cliente.",
                "pedido", str(pid), exitoso=False)
        abort(403)
    return render_template("pedido.html", p=p,
        lineas=consultar("SELECT pd.*, pr.nombre, pr.presentacion FROM pedido_detalle pd "
                         "JOIN producto pr ON pr.id = pd.producto_id "
                         "WHERE pd.pedido_id = %s ORDER BY pd.id", (pid,)),
        historial=consultar("SELECT h.*, u.nombre FROM historial_estatus h "
                            "LEFT JOIN usuario u ON u.id = h.usuario_id "
                            "WHERE h.pedido_id = %s ORDER BY h.fecha", (pid,)))


@cliente.route("/pedido/<int:pid>/cancelar", methods=["POST"])
@requiere("pedidos.cancelar")
def cancelar(pid):
    try:
        with con_actual() as con, con.cursor() as cur:
            cur.execute("SELECT p.id FROM pedido p JOIN cliente c ON c.id = p.cliente_id "
                        "WHERE p.id=%s AND c.usuario_id=%s", (pid, g.usuario["id"]))
            if not cur.fetchone():
                abort(403)
            # El trigger valida contra transicion_permitida: en preparación
            # o en ruta, esto se rechaza sin tocar el estado (RN21).
            cur.execute("UPDATE pedido SET estado='cancelado', "
                        "motivo_cancelacion='Cancelado por el cliente.' WHERE id=%s", (pid,))
            cur.execute("SELECT fn_devolver_inventario(%s,'devolucion_cancelacion',%s)",
                        (pid, "Cancelación del cliente (RN18)."))
        flash("Pedido cancelado. Las unidades regresaron al inventario.", "ok")
    except Exception as e:
        flash(mensaje_de_error(e), "alto")
    return redirect(url_for("cliente.pedido", pid=pid))


# ====================================================================
# OPERACIÓN — RF16, RF18, RN22, RN23, RN27
# ====================================================================
@operacion.route("/operacion")
@requiere("pedidos.cambiar_estado")
def bandeja():
    pedidos = consultar(
        "SELECT p.id, p.folio, p.estado, p.total, p.creado_en, "
        "       u.nombre || ' ' || u.apellidos AS cliente, "
        "       (SELECT count(*) FROM pedido_detalle d WHERE d.pedido_id = p.id) AS lineas "
        "  FROM fn_pedidos_visibles(%s) p "
        "  JOIN cliente c ON c.id = p.cliente_id JOIN usuario u ON u.id = c.usuario_id "
        " WHERE p.estado IN ('asignado','en_preparacion','en_ruta') "
        " ORDER BY p.creado_en", (g.usuario["id"],))
    ocupacion = consultar(
        "SELECT * FROM v_ocupacion_microhub WHERE microhub_id = %s",
        (g.usuario["microhub_id"],), una=True) if g.usuario["microhub_id"] else None
    return render_template("bandeja.html", pedidos=pedidos, ocupacion=ocupacion)


@operacion.route("/operacion/pedido/<int:pid>")
@requiere("pedidos.cambiar_estado")
def detalle(pid):
    p = consultar("SELECT p.*, u.nombre || ' ' || u.apellidos AS cliente, u.telefono, "
                  "       d.calle, d.numero_ext, d.colonia, m.nombre AS microhub "
                  "  FROM fn_pedidos_visibles(%s) p "
                  "  JOIN cliente c ON c.id = p.cliente_id JOIN usuario u ON u.id = c.usuario_id "
                  "  JOIN domicilio d ON d.id = p.domicilio_id "
                  "  LEFT JOIN microhub m ON m.id = p.microhub_id "
                  " WHERE p.id = %s", (g.usuario["id"], pid), una=True)
    if not p:
        auditar("pedidos", "acceso_denegado", f"Pedido {pid} fuera de su microhub.",
                "pedido", str(pid), exitoso=False)
        abort(403)
    return render_template("operacion_pedido.html", p=p,
        lineas=consultar("SELECT pd.*, pr.nombre, pr.presentacion FROM pedido_detalle pd "
                         "JOIN producto pr ON pr.id = pd.producto_id "
                         "WHERE pd.pedido_id=%s ORDER BY pr.nombre", (pid,)),
        decision=consultar("SELECT * FROM decision_asignacion WHERE pedido_id=%s "
                           "ORDER BY fecha DESC LIMIT 1", (pid,), una=True),
        historial=consultar("SELECT h.*, u.nombre FROM historial_estatus h "
                            "LEFT JOIN usuario u ON u.id=h.usuario_id "
                            "WHERE h.pedido_id=%s ORDER BY h.fecha", (pid,)))


@operacion.route("/operacion/pedido/<int:pid>/estado", methods=["POST"])
@requiere("pedidos.cambiar_estado")
def cambiar_estado(pid):
    try:
        with con_actual() as con, con.cursor() as cur:
            cur.execute("SELECT id FROM fn_pedidos_visibles(%s) WHERE id=%s",
                        (g.usuario["id"], pid))
            if not cur.fetchone():
                abort(403)
            cur.execute("UPDATE pedido SET estado=%s WHERE id=%s",
                        (request.form["estado"], pid))
        flash("Estado actualizado.", "ok")
    except Exception as e:
        flash(mensaje_de_error(e), "alto")
    return redirect(url_for("operacion.detalle", pid=pid))


@operacion.route("/operacion/pedido/<int:pid>/cerrar", methods=["POST"])
@requiere("entregas.cerrar")
def cerrar(pid):
    f = request.form
    resultado = f["resultado"]
    try:
        with con_actual() as con, con.cursor() as cur:
            cur.execute("SELECT id, total FROM fn_pedidos_visibles(%s) WHERE id=%s",
                        (g.usuario["id"], pid))
            p = cur.fetchone()
            if not p:
                abort(403)

            recibido = float(f.get("recibido") or 0)
            total = float(p["total"])
            if resultado == "entregado" and recibido < total:
                flash(f"El monto recibido (${recibido:,.2f}) no cubre el total "
                      f"(${total:,.2f}).", "alto")
                return redirect(url_for("operacion.detalle", pid=pid))

            cobrado = total if resultado == "entregado" else (
                0 if resultado == "fallida" else float(f.get("cobrado") or 0))
            cambio = max(0.0, recibido - cobrado)

            cur.execute(
                "INSERT INTO entrega (pedido_id, turno_fecha, asignada_en, salida_en, "
                "cierre_en, resultado, confirmacion_recepcion, monto_cobrado, "
                "cambio_entregado, incidencia, cerrada_por_usuario_id) "
                "VALUES (%s, current_date, now(), now(), now(), %s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (pedido_id) DO UPDATE SET resultado=EXCLUDED.resultado, "
                "  cierre_en=now(), monto_cobrado=EXCLUDED.monto_cobrado, "
                "  cambio_entregado=EXCLUDED.cambio_entregado, "
                "  incidencia=EXCLUDED.incidencia RETURNING id",
                (pid, resultado, resultado != "fallida", cobrado, cambio,
                 f.get("incidencia") or None, g.usuario["id"]))

            nuevo = {"entregado": "entregado", "parcial": "entrega_parcial",
                     "fallida": "entrega_fallida"}[resultado]
            cur.execute("UPDATE pedido SET estado=%s, motivo_cancelacion=%s WHERE id=%s",
                        (nuevo, f.get("incidencia") or None, pid))

            if resultado == "fallida":
                cur.execute("SELECT fn_devolver_inventario(%s,'devolucion_cancelacion',%s)",
                            (pid, "Entrega fallida: la mercancía regresa al microhub."))
        flash(f"Entrega cerrada. Cambio a devolver: ${cambio:,.2f}", "ok")
    except Exception as e:
        flash(mensaje_de_error(e), "alto")
    return redirect(url_for("operacion.detalle", pid=pid))


@operacion.route("/operacion/inventario", methods=["GET", "POST"])
@requiere("inventario.ver")
def inventario():
    if request.method == "POST":
        f = request.form
        try:
            with con_actual() as con, con.cursor() as cur:
                cur.execute("SELECT i.existencia FROM inventario i WHERE i.microhub_id=%s "
                            "AND i.producto_id=%s FOR UPDATE",
                            (g.usuario["microhub_id"], f["producto_id"]))
                fila = cur.fetchone()
                cantidad = int(f["cantidad"])
                if f["tipo"] in ("merma", "salida_pedido"):
                    cantidad = -abs(cantidad)
                nueva = fila["existencia"] + cantidad
                cur.execute("UPDATE inventario SET existencia=%s, actualizado_en=now() "
                            "WHERE microhub_id=%s AND producto_id=%s",
                            (nueva, g.usuario["microhub_id"], f["producto_id"]))
                cur.execute(
                    "INSERT INTO movimiento_inventario (microhub_id, producto_id, tipo, "
                    "cantidad, existencia_resultante, motivo, usuario_id) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (g.usuario["microhub_id"], f["producto_id"], f["tipo"], cantidad,
                     nueva, f.get("motivo") or None, g.usuario["id"]))
            flash("Movimiento registrado.", "ok")
        except Exception as e:
            flash(mensaje_de_error(e), "alto")
        return redirect(url_for("operacion.inventario"))

    # RN22: el operador solo ve el inventario de su microhub.
    return render_template("inventario.html", items=consultar(
        "SELECT p.id, p.clave_interna, p.nombre, p.presentacion, i.existencia, i.minimo "
        "  FROM inventario i JOIN producto p ON p.id = i.producto_id "
        " WHERE i.microhub_id = %s ORDER BY (i.existencia <= i.minimo) DESC, p.nombre",
        (g.usuario["microhub_id"],)))


# ====================================================================
# ADMINISTRACIÓN, INDICADORES Y BITÁCORA
# ====================================================================
@admin.route("/indicadores")
@requiere("indicadores.ver")
def indicadores():
    hub = g.usuario["microhub_id"]
    filtro = "WHERE p.microhub_id = %s" if hub else ""
    args = (hub,) if hub else ()
    resumen = consultar(
        f"SELECT count(*) AS pedidos, "
        f"       count(*) FILTER (WHERE p.estado='entregado') AS entregados, "
        f"       count(*) FILTER (WHERE p.estado='pendiente_asignacion') AS pendientes, "
        f"       round(avg(p.subtotal),2) AS ticket "
        f"  FROM pedido p {filtro}", args, una=True)
    return render_template("indicadores.html", resumen=resumen,
        tasa=consultar("SELECT * FROM v_tasa_entrega ORDER BY tasa_entrega_pct DESC"),
        zonas=consultar("SELECT zona, sum(pedidos) AS pedidos, "
                        "round(avg(ticket_promedio),2) AS ticket "
                        "FROM v_indicadores_zona GROUP BY zona ORDER BY 2 DESC"),
        demanda=consultar(
            "SELECT COALESCE(z.colonia, d.colonia_texto) AS lugar, d.tipo::text AS tipo, "
            "       count(*) AS eventos FROM demanda_no_atendida d "
            "  LEFT JOIN zona z ON z.id = d.zona_id "
            " GROUP BY 1,2 ORDER BY 3 DESC LIMIT 8"),
        ambito=hub)


@admin.route("/bitacora")
@requiere("bitacora.ver")
def bitacora():
    modulo = request.args.get("modulo") or ""
    sql = ("SELECT a.fecha, a.modulo, a.accion::text AS accion, a.entidad, a.entidad_id, "
           "       a.detalle, a.exitoso, COALESCE(u.correo, a.correo_intento) AS quien, "
           "       a.valores_anteriores, a.valores_nuevos "
           "  FROM auditoria a LEFT JOIN usuario u ON u.id = a.usuario_id ")
    args = ()
    if modulo:
        sql += " WHERE a.modulo = %s"
        args = (modulo,)
    sql += " ORDER BY a.fecha DESC LIMIT 120"
    return render_template("bitacora.html", filas=consultar(sql, args), modulo=modulo,
        modulos=consultar("SELECT DISTINCT modulo FROM auditoria ORDER BY modulo"),
        total=consultar("SELECT count(*) AS n FROM auditoria", una=True)["n"])


@admin.route("/admin/pendientes")
@requiere("pedidos.reasignar")
def pendientes():
    return render_template("pendientes.html", pedidos=consultar(
        "SELECT p.id, p.folio, p.total, p.motivo_no_asignacion, p.creado_en, z.colonia "
        "  FROM pedido p JOIN zona z ON z.id = p.zona_id "
        " WHERE p.estado = 'pendiente_asignacion' ORDER BY p.creado_en"))


@admin.route("/admin/pendientes/<int:pid>/reasignar", methods=["POST"])
@requiere("pedidos.reasignar")
def reasignar(pid):
    motivo = (request.form.get("motivo") or "").strip()
    if not motivo:
        # RN24 lo impone la restricción del motor; aquí se evita el viaje.
        flash("La reasignación manual exige un motivo.", "alto")
        return redirect(url_for("admin.pendientes"))
    try:
        with con_actual() as con, con.cursor() as cur:
            cur.execute("SELECT * FROM fn_asignar_pedido(%s)", (pid,))
            res = cur.fetchone()
            if not res["asignado"]:
                flash("Ningún microhub puede surtirlo todavía. Sigue pendiente.", "medio")
                return redirect(url_for("admin.pendientes"))
            cur.execute(
                "INSERT INTO decision_asignacion (pedido_id, microhub_ganador_id, criterio, "
                "manual, usuario_id, motivo) VALUES (%s,%s,'manual',true,%s,%s)",
                (pid, res["microhub_id"], g.usuario["id"], motivo))
        flash("Pedido reasignado.", "ok")
    except Exception as e:
        flash(mensaje_de_error(e), "alto")
    return redirect(url_for("admin.pendientes"))


@admin.route("/admin/parametros", methods=["GET", "POST"])
@requiere("configuracion.ver")
def parametros():
    if request.method == "POST":
        if "configuracion.editar" not in permisos_de(g.usuario["rol"]):
            abort(403)
        try:
            with con_actual() as con, con.cursor() as cur:
                cur.execute("UPDATE configuracion SET valor=%s, actualizado_por=%s, "
                            "actualizado_en=now() WHERE id=%s",
                            (request.form["valor"], g.usuario["id"], request.form["id"]))
            # HU26 CA3: la siguiente validación usa el valor nuevo sin recompilar.
            flash("Parámetro actualizado. Las validaciones ya usan el valor nuevo.", "ok")
        except Exception as e:
            flash(mensaje_de_error(e), "alto")
        return redirect(url_for("admin.parametros"))
    return render_template("parametros.html", params=consultar(
        "SELECT id, clave, valor, unidad, descripcion, actualizado_en FROM configuracion "
        "WHERE ambito='global' ORDER BY clave"))


@admin.route("/admin/usuarios")
@requiere("usuarios.ver")
def usuarios():
    return render_template("usuarios.html", usuarios=consultar(
        "SELECT u.id, u.nombre, u.apellidos, u.correo, u.estatus::text AS estatus, "
        "       r.nombre AS rol, m.clave AS microhub, u.ultimo_acceso "
        "  FROM usuario u JOIN rol r ON r.id = u.rol_id "
        "  LEFT JOIN microhub m ON m.id = u.microhub_id "
        " ORDER BY r.clave, u.apellidos LIMIT 60"))
