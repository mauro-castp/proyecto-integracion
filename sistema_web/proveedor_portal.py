"""
proveedor_portal.py — Portal del perfil «proveedor».

Cada cuenta de proveedor está ligada a un proveedor (proveedor.usuario_id) y solo ve y cambia lo suyo:
  /proveedor              sus datos, su catálogo (precio de compra y capacidad semanal, que puede actualizar) y sus evaluaciones
  /proveedor/ordenes      las órdenes de compra que se le han emitido, con sus líneas y cuánto se ha recibido
"""
from decimal import Decimal, InvalidOperation

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from nucleo import con_actual, consultar, requiere
from web_ampliado import csrf

proveedor_bp = Blueprint("proveedor", __name__, url_prefix="/proveedor")


def _mi_proveedor():
    p = consultar("SELECT id, clave, nombre, contacto, correo, telefono, dias_entrega, pedido_minimo, condiciones_pago, estatus::text AS estatus "
                  "FROM proveedor WHERE usuario_id = %s", (g.usuario["id"],), una=True)
    if not p:
        abort(403, "Tu cuenta todavía no está ligada a un proveedor. Pide a quien administra que la ligue.")
    return p


@proveedor_bp.route("", methods=["GET", "POST"])
@requiere("proveedor.portal")
def inicio():
    p = _mi_proveedor()
    if request.method == "POST":
        if request.form.get("csrf", "") != csrf():
            abort(400, "Formulario vencido; recarga la página.")
        try:
            producto = int(request.form["producto_id"])
            precio = Decimal(request.form["precio_compra"])
            capacidad = int(request.form["capacidad_semanal"])
            if not (Decimal("0.01") <= precio <= Decimal("100000") and 1 <= capacidad <= 1_000_000) or precio != precio.quantize(Decimal("0.01")):
                raise ValueError
        except (KeyError, ValueError, InvalidOperation):
            flash("Revisa el precio (dos decimales, mayor que cero) y la capacidad semanal (entero mayor que cero).", "alto")
            return redirect(url_for("proveedor.inicio"))
        with con_actual() as con, con.cursor() as cur:
            cur.execute("UPDATE proveedor_producto SET precio_compra = %s, capacidad_semanal = %s, actualizado_en = now() "
                        "WHERE proveedor_id = %s AND producto_id = %s RETURNING producto_id", (precio, capacidad, p["id"], producto))
            if not cur.fetchone():
                abort(404)                                  # no es un producto de su catálogo
            cur.execute("INSERT INTO auditoria (usuario_id, modulo, accion, entidad, entidad_id, detalle, exitoso, ip_origen) "
                        "VALUES (%s, 'proveedores', 'modificacion', 'proveedor_producto', %s, %s, true, %s)",
                        (g.usuario["id"], f"{p['id']}-{producto}", f"El proveedor fijó precio {precio} y capacidad {capacidad}.", request.remote_addr))
        flash("Oferta actualizada.", "ok")
        return redirect(url_for("proveedor.inicio"))
    catalogo = consultar("SELECT pp.producto_id, pr.clave_interna, pr.nombre, pp.precio_compra, pp.unidad_compra, pp.capacidad_semanal, "
                         "pp.minimo_compra, pp.vigente_hasta, pp.actualizado_en FROM proveedor_producto pp JOIN producto pr ON pr.id = pp.producto_id "
                         "WHERE pp.proveedor_id = %s ORDER BY pr.nombre", (p["id"],))
    resumen = consultar("SELECT count(*) FILTER (WHERE estado IN ('emitida', 'parcial')) AS abiertas, count(*) AS total "
                        "FROM orden_compra WHERE proveedor_id = %s", (p["id"],), una=True)
    return render_template("proveedor_inicio.html", p=p, catalogo=catalogo, resumen=resumen, token_formulario=csrf())


@proveedor_bp.get("/ordenes")
@requiere("proveedor.portal")
def ordenes():
    p = _mi_proveedor()
    filas = consultar("SELECT o.id, o.folio, o.estado, o.fecha_esperada, o.total, o.creada_en, m.nombre AS microhub, m.direccion "
                      "FROM orden_compra o JOIN microhub m ON m.id = o.microhub_id WHERE o.proveedor_id = %s ORDER BY o.creada_en DESC LIMIT 100",
                      (p["id"],))
    lineas = {}
    if filas:
        for l in consultar("SELECT l.orden_id, pr.nombre, l.cantidad, l.cantidad_recibida, l.precio_compra FROM orden_compra_linea l "
                           "JOIN producto pr ON pr.id = l.producto_id WHERE l.orden_id = ANY(%s) ORDER BY pr.nombre", ([f["id"] for f in filas],)):
            lineas.setdefault(l["orden_id"], []).append(l)
    return render_template("proveedor_ordenes.html", p=p, ordenes=filas, lineas=lineas)
