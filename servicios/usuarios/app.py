"""
Servicio de usuarios · puerto 5102 · contrato v1

  GET   /api/v1/usuarios/yo        perfil de quien inició sesión (cualquier perfil)
  PATCH /api/v1/usuarios/yo        actualizar nombre, apellidos o teléfono (solo JSON)
  GET   /api/v1/usuarios           página de usuarios con búsqueda y filtro por rol (usuarios.ver)
  GET   /api/v1/usuarios/{id}      un usuario (usuarios.ver, o el propio)
  POST  /api/v1/usuarios           crea una cuenta (usuarios.crear)
  PATCH /api/v1/usuarios/{id}      cambia perfil, microhub o estatus; PUT es alias (usuarios.editar)
  DELETE /api/v1/usuarios/{id}     baja lógica y cierre de sus sesiones (usuarios.baja)

El perfil viene de la tabla usuario de PostgreSQL; los cambios los audita el
trigger del motor con el usuario que actúa.
"""
import bcrypt
from flask import g

from comun import config
from comun.base import (crear_app, documentar, filtro_opcion, leer_cuerpo, leer_paginacion, lista, paginacion,
                        requiere, responder, texto_busqueda, tiene)
from comun.base_errores import ErrorApi, conflicto, invalido, no_encontrado
from comun.datos import conexion, consultar, r_sesion
from comun.formatos import fecha
from comun.validar import Campo, validar

app = crear_app("usuarios", "Microhubs · Usuarios", "Perfil del usuario autenticado y administración de cuentas.", 5102)
P = config.PREFIJO
ROLES = ["administrador", "operador", "planeador", "cliente", "repartidor", "auditor", "analista", "supervisor", "proveedor"]
SELECT = ("SELECT u.id, u.nombre, COALESCE(u.apellidos,'') AS apellidos, u.correo, u.telefono, r.clave AS rol, "
          "u.ultimo_acceso, m.id AS mh_id, m.clave AS mh_clave, m.nombre AS mh_nombre "
          "FROM usuario u JOIN rol r ON r.id = u.rol_id LEFT JOIN microhub m ON m.id = u.microhub_id ")


def perfil(f):
    return {"id": f["id"], "nombre": f["nombre"], "apellidos": f["apellidos"], "correo": f["correo"],
            "telefono": f["telefono"], "rol": f["rol"],
            "microhub": {"id": f["mh_id"], "clave": f["mh_clave"], "nombre": f["mh_nombre"]} if f["mh_id"] else None,
            "ultimo_acceso": fecha(f["ultimo_acceso"])}


def _uno(uid):
    f = consultar(SELECT + "WHERE u.id = %s", (uid,), una=True)
    if not f:
        raise no_encontrado()
    return f


@app.get(f"{P}/usuarios/yo")
@requiere()
def yo():
    return responder(perfil(_uno(g.usuario["id"])), raiz="usuario")


@app.route(f"{P}/usuarios/yo", methods=["PATCH", "PUT"])
@requiere()
def actualizar_yo():
    d = validar(leer_cuerpo(), [
        Campo("nombre", req=False, min_len=1, max_len=80), Campo("apellidos", req=False, min_len=1, max_len=120),
        Campo("telefono", req=False, nulo=True, patron=r"[0-9]{10}", mensaje="Debe tener 10 dígitos.")])
    if not d:
        raise ErrorApi(422, "VALIDACION", "Revisa los datos enviados.",
                       [{"campo": "cuerpo", "mensaje": "Indica nombre, apellidos o teléfono."}])
    sets = ", ".join(f"{k} = %s" for k in d)
    with conexion() as con, con.cursor() as cur:
        cur.execute(f"UPDATE usuario SET {sets}, actualizado_en = now() WHERE id = %s", (*d.values(), g.usuario["id"]))
    return responder(perfil(_uno(g.usuario["id"])), raiz="usuario")


@app.get(f"{P}/usuarios")
@requiere("usuarios.ver")
def usuarios():
    pagina, por, desde = leer_paginacion()
    q, rol = texto_busqueda(), filtro_opcion("rol", ROLES)
    where, args = ["TRUE"], []
    if q:
        where.append("(u.nombre ILIKE %s OR u.apellidos ILIKE %s OR u.correo ILIKE %s)")
        args += [f"%{q}%"] * 3
    if rol:
        where.append("r.clave = %s")
        args.append(rol)
    w = " AND ".join(where)
    total = consultar(f"SELECT count(*) AS n FROM usuario u JOIN rol r ON r.id = u.rol_id WHERE {w}", args, una=True)["n"]
    filas = consultar(SELECT + f"WHERE {w} ORDER BY u.id LIMIT %s OFFSET %s", (*args, por, desde))
    return lista(filas, paginacion(pagina, por, total), "usuario", "usuarios", perfil)


@app.get(f"{P}/usuarios/<int:uid>")
@requiere()
def usuario(uid):
    if uid != g.usuario["id"] and not tiene("usuarios.ver"):
        raise ErrorApi(403, "PROHIBIDO", "Solo puedes consultar tu propio perfil.")
    return responder(perfil(_uno(uid)), raiz="usuario")


# --------------------------------------------------------------------
# Administración de cuentas
# --------------------------------------------------------------------
CORREO = r"[^@\s]+@[^@\s]+\.[A-Za-z]{2,}"


def _datos_cuenta(req):
    return [Campo("nombre", req=req, min_len=1, max_len=80), Campo("apellidos", req=req, min_len=1, max_len=120),
            Campo("telefono", req=False, nulo=True, patron=r"[0-9]{10}", mensaje="Debe tener 10 dígitos."),
            Campo("rol", req=req, opciones=ROLES), Campo("microhub_id", "int", req=False, nulo=True, minimo=1)]


def _rol_id(cur, clave):
    cur.execute("SELECT id FROM rol WHERE clave = %s", (clave,))
    f = cur.fetchone()
    if not f:
        raise invalido("rol", "Ese perfil no existe en este sistema.")
    return f["id"]


def _cerrar_sesiones(uid):
    """Un cambio de perfil o una baja rigen de inmediato: los accesos emitidos dejan de servir."""
    r_sesion.delete(f"auth:sesion:{uid}")


def _proteger(cur, uid):
    if uid == g.usuario["id"]:
        raise conflicto("No puedes cambiar tu propio perfil ni darte de baja: pídeselo a otro administrador.")
    cur.execute("SELECT r.clave AS rol, u.estatus::text AS estatus FROM usuario u JOIN rol r ON r.id = u.rol_id WHERE u.id = %s FOR UPDATE OF u", (uid,))
    f = cur.fetchone()
    if not f:
        raise no_encontrado()
    return f


@app.post(f"{P}/usuarios")
@requiere("usuarios.crear")
def alta():
    d = validar(leer_cuerpo("usuario_nuevo"), _datos_cuenta(True) + [
        Campo("correo", max_len=160, patron=CORREO, mensaje="Correo no válido."), Campo("clave", min_len=10, max_len=72)])
    clave = d.pop("clave").encode("utf-8")
    rol = d.pop("rol")
    d["correo"] = d["correo"].lower()
    with conexion() as con, con.cursor() as cur:
        d["rol_id"] = _rol_id(cur, rol)
        d["hash_contrasena"] = bcrypt.hashpw(clave, bcrypt.gensalt(10)).decode()
        cur.execute(f"INSERT INTO usuario ({', '.join(d)}) VALUES ({', '.join(['%s'] * len(d))}) RETURNING id", tuple(d.values()))
        uid = cur.fetchone()["id"]
    return responder(perfil(_uno(uid)), 201, raiz="usuario")


@app.route(f"{P}/usuarios/<int:uid>", methods=["PATCH", "PUT"])
@requiere("usuarios.editar")
def cambio(uid):
    d = validar(leer_cuerpo("usuario_cambio"), _datos_cuenta(False) + [Campo("estatus", req=False, opciones=["activo", "bloqueado"])])
    if not d:
        raise invalido("cuerpo", "Indica al menos un campo.")
    with conexion() as con, con.cursor() as cur:
        antes_ = _proteger(cur, uid)
        if antes_["estatus"] == "baja":
            raise conflicto("La cuenta está dada de baja.")
        sensible = "rol" in d or "estatus" in d or "microhub_id" in d
        if "rol" in d:
            d["rol_id"] = _rol_id(cur, d.pop("rol"))
        cur.execute(f"UPDATE usuario SET {', '.join(f'{k} = %s' for k in d)}, actualizado_en = now() WHERE id = %s", (*d.values(), uid))
    if sensible:
        _cerrar_sesiones(uid)
    return responder(perfil(_uno(uid)), raiz="usuario")


@app.delete(f"{P}/usuarios/<int:uid>")
@requiere("usuarios.baja")
def baja(uid):
    with conexion() as con, con.cursor() as cur:
        if _proteger(cur, uid)["estatus"] != "baja":
            cur.execute("UPDATE usuario SET estatus = 'baja', fecha_baja = now(), actualizado_en = now() WHERE id = %s", (uid,))
    _cerrar_sesiones(uid)
    return responder(None, 204)


documentar(app, "GET", f"{P}/usuarios/yo", "Mi perfil", descripcion="Perfil de quien inició sesión.",
           respuestas={200: ("Perfil", "Perfil.ok")})
documentar(app, "PATCH", f"{P}/usuarios/yo", "Actualizar mi perfil", cuerpo="PerfilActualizar.ok", solo_json=True,
           descripcion="Cambia nombre, apellidos o teléfono (10 dígitos). Queda en la bitácora.",
           respuestas={200: ("Perfil actualizado", "Perfil.ok")}, errores=[400, 422])
documentar(app, "GET", f"{P}/usuarios", "Lista de usuarios", permisos=["usuarios.ver"],
           parametros=[("pagina", "query", "integer", "Página (1…)"), ("por_pagina", "query", "integer", "1 a 100"),
                       ("q", "query", "string", "Busca en nombre, apellidos y correo"),
                       ("rol", "query", "string", "Filtra por perfil")],
           respuestas={200: ("Página de usuarios", "PerfilLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/usuarios/{{id}}", "Un usuario", permisos=["usuarios.ver"],
           parametros=[("id", "path", "integer", "Id del usuario")],
           descripcion="Cualquier perfil puede consultar el suyo; los demás requieren usuarios.ver.",
           respuestas={200: ("Usuario", "Perfil.ok")}, errores=[403, 404])
documentar(app, "POST", f"{P}/usuarios", "Crear una cuenta", permisos=["usuarios.crear"], cuerpo="UsuarioNuevo.ok",
           descripcion="La clave (10 a 72 caracteres) se guarda con bcrypt y nunca se devuelve ni se registra.",
           respuestas={201: ("Cuenta creada", "Perfil.ok")}, errores=[400, 403, 409, 422])
documentar(app, "PATCH", f"{P}/usuarios/{{id}}", "Cambiar una cuenta", permisos=["usuarios.editar"], cuerpo="UsuarioCambio.ok",
           parametros=[("id", "path", "integer", "Id")], descripcion="Cambiar perfil, microhub o estatus cierra sus sesiones. Nadie cambia su propia cuenta por esta ruta.",
           respuestas={200: ("Cuenta actualizada", "Perfil.ok")}, errores=[400, 403, 404, 409, 422])
documentar(app, "PUT", f"{P}/usuarios/{{id}}", "Cambiar una cuenta (alias de PATCH)", permisos=["usuarios.editar"], cuerpo="UsuarioCambio.ok",
           parametros=[("id", "path", "integer", "Id")], respuestas={200: ("Cuenta actualizada", "Perfil.ok")}, errores=[400, 403, 404, 409, 422])
documentar(app, "DELETE", f"{P}/usuarios/{{id}}", "Dar de baja una cuenta", permisos=["usuarios.baja"], parametros=[("id", "path", "integer", "Id")],
           descripcion="Baja lógica: conserva su historia y cierra sus sesiones.", respuestas={204: ("Baja hecha, sin cuerpo", None)}, errores=[403, 404, 409])
