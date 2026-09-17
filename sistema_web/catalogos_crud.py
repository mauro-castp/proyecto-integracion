"""CRUD administrativos adicionales, compatibles con PostgreSQL y SQLite local."""
import os
import sqlite3
from pathlib import Path

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

catalogos_bp = Blueprint("catalogos", __name__, url_prefix="/admin")
MODO_LOCAL = os.environ.get("MODO_LOCAL", "0") == "1"
DB_LOCAL = Path(__file__).with_name("microhubs_local.db")


def _db():
    con = sqlite3.connect(DB_LOCAL)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con


def inicializar_local():
    with _db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS microhub(
          id INTEGER PRIMARY KEY AUTOINCREMENT, clave TEXT UNIQUE NOT NULL,
          nombre TEXT NOT NULL, direccion TEXT NOT NULL, latitud REAL NOT NULL,
          longitud REAL NOT NULL, radio_km REAL, capacidad_turno INTEGER,
          hora_apertura TEXT NOT NULL DEFAULT '08:00', hora_cierre TEXT NOT NULL DEFAULT '20:00',
          estatus TEXT NOT NULL DEFAULT 'activo');
        CREATE TABLE IF NOT EXISTS zona(
          id INTEGER PRIMARY KEY AUTOINCREMENT, clave TEXT UNIQUE NOT NULL,
          nombre TEXT NOT NULL, colonia TEXT NOT NULL, codigo_postal TEXT NOT NULL,
          municipio TEXT NOT NULL DEFAULT 'Monterrey', estado TEXT NOT NULL DEFAULT 'Nuevo León',
          centroide_lat REAL NOT NULL, centroide_lng REAL NOT NULL,
          ticket_minimo REAL, costo_envio REAL, envio_gratis_desde REAL,
          estatus TEXT NOT NULL DEFAULT 'activo', UNIQUE(colonia,codigo_postal));
        CREATE TABLE IF NOT EXISTS rol(
          id INTEGER PRIMARY KEY AUTOINCREMENT, clave TEXT UNIQUE NOT NULL,
          nombre TEXT NOT NULL, requiere_microhub INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS usuario(
          id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, apellidos TEXT NOT NULL,
          correo TEXT UNIQUE NOT NULL, telefono TEXT, hash_contrasena TEXT NOT NULL,
          rol_id INTEGER NOT NULL REFERENCES rol(id), microhub_id INTEGER REFERENCES microhub(id),
          estatus TEXT NOT NULL DEFAULT 'activo', ultimo_acceso TEXT, fecha_baja TEXT);
        """)
        if con.execute("SELECT count(*) FROM microhub").fetchone()[0] == 0:
            con.executemany("INSERT INTO microhub(clave,nombre,direccion,latitud,longitud,radio_km,capacidad_turno) VALUES(?,?,?,?,?,?,?)", [
                ("MH-01","Microhub San Bernabé","Monterrey, N.L.",25.755,-100.410,4.5,12),
                ("MH-02","Microhub Cumbres","Monterrey, N.L.",25.735,-100.398,5.0,15)])
        if con.execute("SELECT count(*) FROM zona").fetchone()[0] == 0:
            con.executemany("INSERT INTO zona(clave,nombre,colonia,codigo_postal,centroide_lat,centroide_lng,ticket_minimo,costo_envio) VALUES(?,?,?,?,?,?,?,?)", [
                ("ZN-01","San Bernabé","San Bernabé","64100",25.757,-100.414,80,15),
                ("ZN-02","Valles de San Bernabé","Valles de San Bernabé","64103",25.765,-100.420,100,20)])
        if con.execute("SELECT count(*) FROM rol").fetchone()[0] == 0:
            con.executemany("INSERT INTO rol(clave,nombre,requiere_microhub) VALUES(?,?,?)", [
                ("administrador","Administrador",0),("operador","Operador de microhub",1),
                ("planeador","Planeador",0),("auditor","Auditor",0)])
        if con.execute("SELECT count(*) FROM usuario").fetchone()[0] == 0:
            con.executemany("INSERT INTO usuario(nombre,apellidos,correo,telefono,hash_contrasena,rol_id,microhub_id) VALUES(?,?,?,?,?,?,?)", [
                ("Ana","Administradora","admin@microhubs.local","8110000000","local",1,None),
                ("Óscar","Operador","operador@microhubs.local","8110000001","local",2,1)])


def _permiso(clave):
    if MODO_LOCAL:
        return
    from nucleo import permisos_de
    u = getattr(g, "usuario", None)
    if not u or clave not in permisos_de(u["rol"]):
        abort(403)


def _consulta(sql_local, sql_pg=None, args=(), una=False):
    if MODO_LOCAL:
        with _db() as con:
            cur = con.execute(sql_local, args)
            return cur.fetchone() if una else cur.fetchall()
    from nucleo import consultar
    return consultar(sql_pg or sql_local.replace("?", "%s"), args, una=una)


def _ejecutar(sql_local, sql_pg, args):
    if MODO_LOCAL:
        with _db() as con:
            con.execute(sql_local, args)
    else:
        from nucleo import con_actual
        with con_actual() as con, con.cursor() as cur:
            cur.execute(sql_pg, args)


def _estado(modulo, pid, valor, permiso):
    _permiso(permiso)
    tabla = {"categorias":"categoria", "microhubs":"microhub", "zonas":"zona"}[modulo]
    _ejecutar(f"UPDATE {tabla} SET estatus=? WHERE id=?", f"UPDATE {tabla} SET estatus=%s, actualizado_en=now() WHERE id=%s" if tabla != "categoria" else "UPDATE categoria SET estatus=%s WHERE id=%s", (valor, pid))
    flash("Registro reactivado." if valor == "activo" else "Registro dado de baja; su historial se conserva.", "ok")
    return redirect(url_for(f"catalogos.{modulo}"))


# ----------------------------- Categorías -----------------------------
@catalogos_bp.route("/categorias")
def categorias():
    _permiso("productos.ver")
    filas = _consulta("SELECT id,nombre,orden,estatus FROM categoria ORDER BY orden,nombre")
    return render_template("crud_lista.html", titulo="Categorías", descripcion="Organiza los productos del catálogo.", filas=filas,
        columnas=[("nombre","Nombre"),("orden","Orden"),("estatus","Estatus")], nuevo="catalogos.categoria_nueva", editar="catalogos.categoria_editar", modulo="categorias", permiso_crear="productos.crear", permiso_editar="productos.editar", permiso_baja="productos.baja")


@catalogos_bp.route("/categorias/nueva", methods=["GET","POST"])
def categoria_nueva():
    _permiso("productos.crear")
    if request.method == "POST":
        try:
            _ejecutar("INSERT INTO categoria(nombre,orden) VALUES(?,?)", "INSERT INTO categoria(nombre,orden) VALUES(%s,%s)", (request.form["nombre"].strip(), int(request.form.get("orden") or 0)))
            flash("Categoría creada.", "ok"); return redirect(url_for("catalogos.categorias"))
        except Exception: flash("No se pudo crear; revisa que el nombre no esté repetido.", "alto")
    return _form("Nueva categoría", "catalogos.categorias", [("nombre","Nombre","text",True),("orden","Orden","number",False)])


@catalogos_bp.route("/categorias/<int:pid>/editar", methods=["GET","POST"])
def categoria_editar(pid):
    _permiso("productos.editar"); fila=_consulta("SELECT * FROM categoria WHERE id=?", args=(pid,), una=True)
    if not fila: abort(404)
    if request.method == "POST":
        try:
            _ejecutar("UPDATE categoria SET nombre=?,orden=? WHERE id=?", "UPDATE categoria SET nombre=%s,orden=%s WHERE id=%s", (request.form["nombre"].strip(), int(request.form.get("orden") or 0), pid))
            flash("Categoría actualizada.", "ok"); return redirect(url_for("catalogos.categorias"))
        except Exception: flash("No se pudo actualizar la categoría.", "alto")
    return _form("Editar categoría", "catalogos.categorias", [("nombre","Nombre","text",True),("orden","Orden","number",False)], fila)


@catalogos_bp.post("/categorias/<int:pid>/baja")
def categorias_baja(pid): return _estado("categorias",pid,"inactivo","productos.baja")
@catalogos_bp.post("/categorias/<int:pid>/activar")
def categorias_activar(pid): return _estado("categorias",pid,"activo","productos.editar")


# ----------------------------- Microhubs ------------------------------
MH_FIELDS=[("clave","Clave","text",True),("nombre","Nombre","text",True),("direccion","Dirección","text",True),("latitud","Latitud","number",True),("longitud","Longitud","number",True),("radio_km","Radio (km)","number",False),("capacidad_turno","Capacidad por turno","number",False),("hora_apertura","Apertura","time",True),("hora_cierre","Cierre","time",True)]

@catalogos_bp.route("/microhubs")
def microhubs():
    _permiso("microhubs.ver"); filas=_consulta("SELECT id,clave,nombre,direccion,capacidad_turno,hora_apertura,hora_cierre,estatus FROM microhub ORDER BY nombre")
    return render_template("crud_lista.html", titulo="Microhubs", descripcion="Ubicaciones que preparan y surten pedidos.", filas=filas, columnas=[("clave","Clave"),("nombre","Nombre"),("direccion","Dirección"),("capacidad_turno","Capacidad"),("estatus","Estatus")], nuevo="catalogos.microhub_nuevo", editar="catalogos.microhub_editar", modulo="microhubs", permiso_crear="microhubs.crear", permiso_editar="microhubs.editar", permiso_baja="microhubs.baja")

def _datos_mh(f):
    return (f["clave"].strip().upper(),f["nombre"].strip(),f["direccion"].strip(),float(f["latitud"]),float(f["longitud"]),float(f["radio_km"]) if f.get("radio_km") else None,int(f["capacidad_turno"]) if f.get("capacidad_turno") else None,f["hora_apertura"],f["hora_cierre"])

@catalogos_bp.route("/microhubs/nuevo", methods=["GET","POST"])
def microhub_nuevo():
    _permiso("microhubs.crear")
    if request.method=="POST":
        try:
            d=_datos_mh(request.form); _ejecutar("INSERT INTO microhub(clave,nombre,direccion,latitud,longitud,radio_km,capacidad_turno,hora_apertura,hora_cierre) VALUES(?,?,?,?,?,?,?,?,?)","INSERT INTO microhub(clave,nombre,direccion,latitud,longitud,radio_km,capacidad_turno,hora_apertura,hora_cierre) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",d); flash("Microhub creado.","ok"); return redirect(url_for("catalogos.microhubs"))
        except Exception: flash("No se pudo crear. Revisa clave, coordenadas, capacidad y horario.","alto")
    return _form("Nuevo microhub","catalogos.microhubs",MH_FIELDS)

@catalogos_bp.route("/microhubs/<int:pid>/editar", methods=["GET","POST"])
def microhub_editar(pid):
    _permiso("microhubs.editar"); fila=_consulta("SELECT * FROM microhub WHERE id=?",args=(pid,),una=True)
    if not fila: abort(404)
    if request.method=="POST":
        try:
            d=_datos_mh(request.form)+(pid,); _ejecutar("UPDATE microhub SET clave=?,nombre=?,direccion=?,latitud=?,longitud=?,radio_km=?,capacidad_turno=?,hora_apertura=?,hora_cierre=? WHERE id=?","UPDATE microhub SET clave=%s,nombre=%s,direccion=%s,latitud=%s,longitud=%s,radio_km=%s,capacidad_turno=%s,hora_apertura=%s,hora_cierre=%s,actualizado_en=now() WHERE id=%s",d); flash("Microhub actualizado.","ok"); return redirect(url_for("catalogos.microhubs"))
        except Exception: flash("No se pudo actualizar el microhub.","alto")
    return _form("Editar microhub","catalogos.microhubs",MH_FIELDS,fila)

@catalogos_bp.post("/microhubs/<int:pid>/baja")
def microhubs_baja(pid): return _estado("microhubs",pid,"inactivo","microhubs.baja")
@catalogos_bp.post("/microhubs/<int:pid>/activar")
def microhubs_activar(pid): return _estado("microhubs",pid,"activo","microhubs.editar")


# ------------------------------- Zonas --------------------------------
Z_FIELDS=[("clave","Clave","text",True),("nombre","Nombre","text",True),("colonia","Colonia","text",True),("codigo_postal","Código postal","text",True),("municipio","Municipio","text",True),("estado","Estado","text",True),("centroide_lat","Latitud","number",True),("centroide_lng","Longitud","number",True),("ticket_minimo","Ticket mínimo","number",False),("costo_envio","Costo de envío","number",False),("envio_gratis_desde","Envío gratis desde","number",False)]

@catalogos_bp.route("/zonas")
def zonas():
    _permiso("zonas.ver"); filas=_consulta("SELECT id,clave,nombre,colonia,codigo_postal,municipio,estatus FROM zona ORDER BY colonia")
    return render_template("crud_lista.html",titulo="Zonas de cobertura",descripcion="Colonias, códigos postales y condiciones comerciales.",filas=filas,columnas=[("clave","Clave"),("colonia","Colonia"),("codigo_postal","CP"),("municipio","Municipio"),("estatus","Estatus")],nuevo="catalogos.zona_nueva",editar="catalogos.zona_editar",modulo="zonas",permiso_crear="zonas.crear",permiso_editar="zonas.editar",permiso_baja="zonas.baja")

def _optfloat(f,k): return float(f[k]) if f.get(k) else None
def _datos_z(f): return (f["clave"].strip().upper(),f["nombre"].strip(),f["colonia"].strip(),f["codigo_postal"].strip(),f["municipio"].strip(),f["estado"].strip(),float(f["centroide_lat"]),float(f["centroide_lng"]),_optfloat(f,"ticket_minimo"),_optfloat(f,"costo_envio"),_optfloat(f,"envio_gratis_desde"))

@catalogos_bp.route("/zonas/nueva",methods=["GET","POST"])
def zona_nueva():
    _permiso("zonas.crear")
    if request.method=="POST":
        try:
            d=_datos_z(request.form); _ejecutar("INSERT INTO zona(clave,nombre,colonia,codigo_postal,municipio,estado,centroide_lat,centroide_lng,ticket_minimo,costo_envio,envio_gratis_desde) VALUES(?,?,?,?,?,?,?,?,?,?,?)","INSERT INTO zona(clave,nombre,colonia,codigo_postal,municipio,estado,centroide_lat,centroide_lng,ticket_minimo,costo_envio,envio_gratis_desde) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",d); flash("Zona creada.","ok"); return redirect(url_for("catalogos.zonas"))
        except Exception: flash("No se pudo crear. Revisa CP, coordenadas y valores.","alto")
    return _form("Nueva zona","catalogos.zonas",Z_FIELDS,defaults={"municipio":"Monterrey","estado":"Nuevo León"})

@catalogos_bp.route("/zonas/<int:pid>/editar",methods=["GET","POST"])
def zona_editar(pid):
    _permiso("zonas.editar"); fila=_consulta("SELECT * FROM zona WHERE id=?",args=(pid,),una=True)
    if not fila: abort(404)
    if request.method=="POST":
        try:
            d=_datos_z(request.form)+(pid,); _ejecutar("UPDATE zona SET clave=?,nombre=?,colonia=?,codigo_postal=?,municipio=?,estado=?,centroide_lat=?,centroide_lng=?,ticket_minimo=?,costo_envio=?,envio_gratis_desde=? WHERE id=?","UPDATE zona SET clave=%s,nombre=%s,colonia=%s,codigo_postal=%s,municipio=%s,estado=%s,centroide_lat=%s,centroide_lng=%s,ticket_minimo=%s,costo_envio=%s,envio_gratis_desde=%s,actualizado_en=now() WHERE id=%s",d); flash("Zona actualizada.","ok"); return redirect(url_for("catalogos.zonas"))
        except Exception: flash("No se pudo actualizar la zona.","alto")
    return _form("Editar zona","catalogos.zonas",Z_FIELDS,fila)

@catalogos_bp.post("/zonas/<int:pid>/baja")
def zonas_baja(pid): return _estado("zonas",pid,"inactivo","zonas.baja")
@catalogos_bp.post("/zonas/<int:pid>/activar")
def zonas_activar(pid): return _estado("zonas",pid,"activo","zonas.editar")


# ------------------------------ Usuarios ------------------------------
def _roles(): return _consulta("SELECT id,nombre,requiere_microhub FROM rol WHERE estatus='activo' ORDER BY nombre","SELECT id,nombre,requiere_microhub FROM rol WHERE estatus='activo' ORDER BY nombre") if not MODO_LOCAL else _consulta("SELECT id,nombre,requiere_microhub FROM rol ORDER BY nombre")
def _hubs(): return _consulta("SELECT id,nombre FROM microhub WHERE estatus='activo' ORDER BY nombre")

@catalogos_bp.route("/gestion-usuarios")
def usuarios():
    _permiso("usuarios.ver")
    filas=_consulta("SELECT u.id,u.nombre||' '||u.apellidos AS nombre_completo,u.correo,r.nombre AS rol,COALESCE(m.clave,'—') AS microhub,u.estatus FROM usuario u JOIN rol r ON r.id=u.rol_id LEFT JOIN microhub m ON m.id=u.microhub_id ORDER BY u.apellidos", "SELECT u.id,concat(u.nombre,' ',u.apellidos) AS nombre_completo,u.correo,r.nombre AS rol,COALESCE(m.clave,'—') AS microhub,u.estatus::text AS estatus FROM usuario u JOIN rol r ON r.id=u.rol_id LEFT JOIN microhub m ON m.id=u.microhub_id ORDER BY u.apellidos")
    return render_template("crud_lista.html",titulo="Usuarios",descripcion="Personas, roles y ámbito de operación.",filas=filas,columnas=[("nombre_completo","Nombre"),("correo","Correo"),("rol","Rol"),("microhub","Microhub"),("estatus","Estatus")],nuevo="catalogos.usuario_nuevo",editar="catalogos.usuario_editar",modulo="usuarios",permiso_crear="usuarios.crear",permiso_editar="usuarios.editar",permiso_baja="usuarios.baja")

def _user_fields(password_required):
    return [("nombre","Nombre","text",True),("apellidos","Apellidos","text",True),("correo","Correo","email",True),("telefono","Teléfono","text",False),("rol_id","Rol","select",True),("microhub_id","Microhub (si aplica)","select",False),("clave","Contraseña" if password_required else "Nueva contraseña (opcional)","password",password_required)]
def _user_options(): return {"rol_id":[(x["id"],x["nombre"]) for x in _roles()],"microhub_id":[("","Sin microhub")]+[(x["id"],x["nombre"]) for x in _hubs()]}
def _hash(clave):
    if MODO_LOCAL: return "local:"+clave
    from nucleo import hashear
    return hashear(clave)

@catalogos_bp.route("/gestion-usuarios/nuevo",methods=["GET","POST"])
def usuario_nuevo():
    _permiso("usuarios.crear")
    if request.method=="POST":
        try:
            f=request.form; d=(f["nombre"].strip(),f["apellidos"].strip(),f["correo"].strip().lower(),f.get("telefono") or None,_hash(f["clave"]),int(f["rol_id"]),int(f["microhub_id"]) if f.get("microhub_id") else None)
            _ejecutar("INSERT INTO usuario(nombre,apellidos,correo,telefono,hash_contrasena,rol_id,microhub_id) VALUES(?,?,?,?,?,?,?)","INSERT INTO usuario(nombre,apellidos,correo,telefono,hash_contrasena,rol_id,microhub_id) VALUES(%s,%s,%s,%s,%s,%s,%s)",d); flash("Usuario creado.","ok"); return redirect(url_for("catalogos.usuarios"))
        except Exception: flash("No se pudo crear. Revisa el correo, rol y microhub.","alto")
    return _form("Nuevo usuario","catalogos.usuarios",_user_fields(True),opciones=_user_options())

@catalogos_bp.route("/gestion-usuarios/<int:pid>/editar",methods=["GET","POST"])
def usuario_editar(pid):
    _permiso("usuarios.editar"); fila=_consulta("SELECT * FROM usuario WHERE id=?",args=(pid,),una=True)
    if not fila: abort(404)
    if request.method=="POST":
        try:
            f=request.form; d=(f["nombre"].strip(),f["apellidos"].strip(),f["correo"].strip().lower(),f.get("telefono") or None,int(f["rol_id"]),int(f["microhub_id"]) if f.get("microhub_id") else None)
            _ejecutar("UPDATE usuario SET nombre=?,apellidos=?,correo=?,telefono=?,rol_id=?,microhub_id=? WHERE id=?","UPDATE usuario SET nombre=%s,apellidos=%s,correo=%s,telefono=%s,rol_id=%s,microhub_id=%s,actualizado_en=now() WHERE id=%s",d+(pid,))
            if f.get("clave"): _ejecutar("UPDATE usuario SET hash_contrasena=? WHERE id=?","UPDATE usuario SET hash_contrasena=%s WHERE id=%s",(_hash(f["clave"]),pid))
            flash("Usuario actualizado.","ok"); return redirect(url_for("catalogos.usuarios"))
        except Exception: flash("No se pudo actualizar el usuario.","alto")
    return _form("Editar usuario","catalogos.usuarios",_user_fields(False),fila,opciones=_user_options())

@catalogos_bp.post("/usuarios/<int:pid>/baja")
def usuarios_baja(pid):
    _permiso("usuarios.baja"); _ejecutar("UPDATE usuario SET estatus='baja',fecha_baja=CURRENT_TIMESTAMP WHERE id=?","UPDATE usuario SET estatus='baja',fecha_baja=now(),actualizado_en=now() WHERE id=%s",(pid,)); flash("Usuario dado de baja.","ok"); return redirect(url_for("catalogos.usuarios"))
@catalogos_bp.post("/usuarios/<int:pid>/activar")
def usuarios_activar(pid):
    _permiso("usuarios.editar"); _ejecutar("UPDATE usuario SET estatus='activo',fecha_baja=NULL WHERE id=?","UPDATE usuario SET estatus='activo',fecha_baja=NULL,actualizado_en=now() WHERE id=%s",(pid,)); flash("Usuario reactivado.","ok"); return redirect(url_for("catalogos.usuarios"))


def _form(titulo, volver, campos, fila=None, defaults=None, opciones=None):
    return render_template("crud_form.html",titulo=titulo,volver=volver,campos=campos,fila=fila,defaults=defaults or {},opciones=opciones or {})
