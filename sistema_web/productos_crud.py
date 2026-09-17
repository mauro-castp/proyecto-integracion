"""CRUD de productos compatible con PostgreSQL (Docker) y SQLite (modo local)."""
import os
import sqlite3
from pathlib import Path

from flask import (Blueprint, abort, flash, g, redirect, render_template,
                   request, url_for)

productos_bp = Blueprint("productos", __name__, url_prefix="/admin/productos")
MODO_LOCAL = os.environ.get("MODO_LOCAL", "0") == "1"
DB_LOCAL = Path(__file__).with_name("microhubs_local.db")


def _permiso(clave):
    if MODO_LOCAL:
        return
    from nucleo import permisos_de
    usuario = getattr(g, "usuario", None)
    if not usuario:
        abort(403)
    if clave not in permisos_de(usuario["rol"]):
        abort(403)


def inicializar_local():
    """Crea una base pequeña para probar las pantallas sin infraestructura."""
    with sqlite3.connect(DB_LOCAL) as con:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS categoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                orden INTEGER NOT NULL DEFAULT 0,
                estatus TEXT NOT NULL DEFAULT 'activo'
            );
            CREATE TABLE IF NOT EXISTS producto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clave_interna TEXT NOT NULL UNIQUE,
                nombre TEXT NOT NULL,
                categoria_id INTEGER NOT NULL REFERENCES categoria(id),
                unidad TEXT NOT NULL,
                presentacion TEXT,
                precio REAL NOT NULL CHECK(precio > 0),
                imagen_url TEXT,
                estatus TEXT NOT NULL DEFAULT 'activo',
                creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        if con.execute("SELECT count(*) FROM categoria").fetchone()[0] == 0:
            con.executemany("INSERT INTO categoria(nombre, orden) VALUES (?, ?)", [
                ("Abarrotes", 1), ("Bebidas", 2), ("Limpieza", 3),
                ("Cuidado personal", 4)
            ])
        if con.execute("SELECT count(*) FROM producto").fetchone()[0] == 0:
            con.executemany(
                "INSERT INTO producto(clave_interna,nombre,categoria_id,unidad,presentacion,precio) "
                "VALUES (?,?,?,?,?,?)",
                [("PROD-001", "Arroz", 1, "pieza", "Bolsa 1 kg", 32.50),
                 ("PROD-002", "Agua purificada", 2, "pieza", "Botella 1.5 L", 18.00),
                 ("PROD-003", "Detergente", 3, "pieza", "Bolsa 850 g", 46.90)])


def _sqlite():
    con = sqlite3.connect(DB_LOCAL)
    con.row_factory = sqlite3.Row
    return con


def _categorias():
    if MODO_LOCAL:
        with _sqlite() as con:
            return con.execute("SELECT id,nombre FROM categoria WHERE estatus='activo' ORDER BY orden,nombre").fetchall()
    from nucleo import consultar
    return consultar("SELECT id,nombre FROM categoria WHERE estatus='activo' ORDER BY orden,nombre")


@productos_bp.route("")
def lista():
    _permiso("productos.ver")
    q = (request.args.get("q") or "").strip()
    estatus = request.args.get("estatus", "todos")
    if MODO_LOCAL:
        sql = ("SELECT p.id,p.clave_interna,p.nombre,c.nombre categoria,p.unidad,p.presentacion,"
               "p.precio,p.estatus FROM producto p JOIN categoria c ON c.id=p.categoria_id WHERE 1=1")
        args = []
        if q:
            sql += " AND (lower(p.nombre) LIKE ? OR lower(p.clave_interna) LIKE ?)"
            args += [f"%{q.lower()}%", f"%{q.lower()}%"]
        if estatus in ("activo", "inactivo"):
            sql += " AND p.estatus=?"; args.append(estatus)
        with _sqlite() as con:
            filas = con.execute(sql + " ORDER BY p.nombre", args).fetchall()
    else:
        from nucleo import consultar
        sql = ("SELECT p.id,p.clave_interna,p.nombre,c.nombre AS categoria,p.unidad,p.presentacion,"
               "p.precio,p.estatus::text AS estatus FROM producto p JOIN categoria c ON c.id=p.categoria_id WHERE true")
        args = []
        if q:
            sql += " AND (lower(p.nombre) LIKE %s OR lower(p.clave_interna) LIKE %s)"
            args += [f"%{q.lower()}%", f"%{q.lower()}%"]
        if estatus in ("activo", "inactivo"):
            sql += " AND p.estatus=%s"; args.append(estatus)
        filas = consultar(sql + " ORDER BY p.nombre", tuple(args))
    return render_template("productos.html", productos=filas, q=q, estatus=estatus)


def _guardar(producto_id=None):
    f = request.form
    datos = (f["clave_interna"].strip().upper(), f["nombre"].strip(),
             int(f["categoria_id"]), f["unidad"].strip(),
             f.get("presentacion", "").strip() or None, float(f["precio"]),
             f.get("imagen_url", "").strip() or None)
    if MODO_LOCAL:
        with _sqlite() as con:
            if producto_id:
                con.execute("UPDATE producto SET clave_interna=?,nombre=?,categoria_id=?,unidad=?,presentacion=?,precio=?,imagen_url=?,actualizado_en=CURRENT_TIMESTAMP WHERE id=?", datos + (producto_id,))
            else:
                con.execute("INSERT INTO producto(clave_interna,nombre,categoria_id,unidad,presentacion,precio,imagen_url) VALUES (?,?,?,?,?,?,?)", datos)
    else:
        from nucleo import con_actual
        with con_actual() as con, con.cursor() as cur:
            if producto_id:
                cur.execute("UPDATE producto SET clave_interna=%s,nombre=%s,categoria_id=%s,unidad=%s,presentacion=%s,precio=%s,imagen_url=%s,actualizado_en=now() WHERE id=%s", datos + (producto_id,))
            else:
                cur.execute("INSERT INTO producto(clave_interna,nombre,categoria_id,unidad,presentacion,precio,imagen_url) VALUES (%s,%s,%s,%s,%s,%s,%s)", datos)


@productos_bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    _permiso("productos.crear")
    if request.method == "POST":
        try:
            _guardar()
            flash("Producto creado correctamente.", "ok")
            return redirect(url_for("productos.lista"))
        except (ValueError, sqlite3.IntegrityError, Exception) as exc:
            flash("No se pudo crear. Revisa que la clave sea única y el precio mayor a cero.", "alto")
    return render_template("producto_form.html", producto=None, categorias=_categorias())


def _obtener(pid):
    if MODO_LOCAL:
        with _sqlite() as con:
            return con.execute("SELECT * FROM producto WHERE id=?", (pid,)).fetchone()
    from nucleo import consultar
    return consultar("SELECT * FROM producto WHERE id=%s", (pid,), una=True)


@productos_bp.route("/<int:pid>/editar", methods=["GET", "POST"])
def editar(pid):
    _permiso("productos.editar")
    producto = _obtener(pid)
    if not producto:
        abort(404)
    if request.method == "POST":
        try:
            _guardar(pid)
            flash("Producto actualizado correctamente.", "ok")
            return redirect(url_for("productos.lista"))
        except (ValueError, sqlite3.IntegrityError, Exception):
            flash("No se pudo actualizar. Revisa la clave y el precio.", "alto")
    return render_template("producto_form.html", producto=producto, categorias=_categorias())


def _cambiar_estatus(pid, estatus):
    if MODO_LOCAL:
        with _sqlite() as con:
            con.execute("UPDATE producto SET estatus=?,actualizado_en=CURRENT_TIMESTAMP WHERE id=?", (estatus, pid))
    else:
        from nucleo import con_actual
        with con_actual() as con, con.cursor() as cur:
            cur.execute("UPDATE producto SET estatus=%s,actualizado_en=now() WHERE id=%s", (estatus, pid))


@productos_bp.route("/<int:pid>/eliminar", methods=["POST"])
def eliminar(pid):
    _permiso("productos.baja")
    _cambiar_estatus(pid, "inactivo")
    flash("Producto dado de baja. Se conserva su historial.", "ok")
    return redirect(url_for("productos.lista"))


@productos_bp.route("/<int:pid>/activar", methods=["POST"])
def activar(pid):
    _permiso("productos.editar")
    _cambiar_estatus(pid, "activo")
    flash("Producto reactivado.", "ok")
    return redirect(url_for("productos.lista", estatus="todos"))
