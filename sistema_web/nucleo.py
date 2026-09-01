"""
nucleo.py — Configuración, acceso a datos y autenticación
Plataforma de Microhubs · Codex Innovations · Equipo 04

Principio de esta capa: la aplicación NO reimplementa reglas de negocio.
Las invariantes viven en PostgreSQL como restricciones, funciones y triggers.
Aquí solo se abre la transacción, se declara quién actúa y se traduce el
error del motor a un mensaje que la persona pueda entender.

Por eso no hay ORM: con toda la lógica en funciones del motor, un ORM
añadiría una capa de traducción sin resolver nada.
"""
import os
import uuid
import datetime as dt
from contextlib import contextmanager

import bcrypt
import jwt
import psycopg
import redis
from psycopg.rows import dict_row
from flask import g, request, redirect, url_for, flash


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "cambiar-en-produccion-RNF30")
    PG_DSN = os.environ.get(
        "PG_DSN", "host=127.0.0.1 port=5432 dbname=microhubs_p1 "
                  "user=postgres password=microhubs_dev")
    REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379")
    MONGO_URL = os.environ.get("MONGO_URL")          # opcional: RNF13
    JWT_ALG = "HS256"


# --------------------------------------------------------------------
# Redis. db 0 = sesión y bloqueos (noeviction). db 1 = caché y carrito.
# La separación es la del entregable de claves: una política de expulsión
# compartida podría descartar un bloqueo de inventario activo.
# --------------------------------------------------------------------
r_sesion = redis.Redis.from_url(Config.REDIS_URL, db=0, decode_responses=True)
r_cache = redis.Redis.from_url(Config.REDIS_URL, db=1, decode_responses=True)


@contextmanager
def conexion(usuario_id=None, rol=None, autocommit=False):
    """Abre una conexión declarando el actor de la transacción.

    Los triggers de auditoría e historial leen app.usuario_id y app.rol.
    Si no se fijan, la bitácora queda sin autor y el trigger de transición
    no puede validar el rol. Es el punto de integración más importante
    entre la aplicación y el modelo.
    """
    con = psycopg.connect(Config.PG_DSN, row_factory=dict_row, autocommit=autocommit)
    try:
        with con.cursor() as cur:
            cur.execute("SET search_path TO microhubs, public")
            if usuario_id is not None:
                cur.execute("SELECT set_config('app.usuario_id', %s, false)", (str(usuario_id),))
            cur.execute("SELECT set_config('app.rol', %s, false)", (rol or "sistema",))
            cur.execute("SELECT set_config('app.ip_origen', %s, false)",
                        (request.remote_addr or "127.0.0.1",))
        yield con
        if not autocommit:
            con.commit()
    except Exception:
        if not autocommit:
            con.rollback()
        raise
    finally:
        con.close()


def con_actual(autocommit=False):
    u = getattr(g, "usuario", None)
    return conexion(u["id"] if u else None, u["rol"] if u else None, autocommit)


def consultar(sql, params=(), una=False):
    """Consulta de solo lectura, sin actor: no escribe nada."""
    with conexion() as con, con.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone() if una else cur.fetchall()


# --------------------------------------------------------------------
# Contraseñas y tokens
# --------------------------------------------------------------------
def hashear(clave: str) -> str:
    return bcrypt.hashpw(clave.encode(), bcrypt.gensalt(rounds=10)).decode()


def verificar(clave: str, hash_guardado: str) -> bool:
    try:
        return bcrypt.checkpw(clave.encode(), hash_guardado.encode())
    except (ValueError, TypeError):
        return False


def parametro(clave, defecto=None):
    """Lee un parámetro operativo desde la base (RN40). Nunca una constante."""
    fila = consultar(
        "SELECT valor FROM configuracion WHERE clave=%s AND ambito='global'",
        (clave,), una=True)
    return fila["valor"] if fila else defecto


def emitir_token(usuario):
    minutos = int(parametro("jwt_acceso_minutos", 15))
    jti = uuid.uuid4().hex
    ahora = dt.datetime.now(dt.timezone.utc)
    carga = {
        "sub": str(usuario["id"]),
        "rol": usuario["rol"],
        "nombre": usuario["nombre"],
        "microhub_id": usuario.get("microhub_id"),
        "jti": jti,
        "iat": ahora,
        "exp": ahora + dt.timedelta(minutes=minutos),
    }
    r_sesion.sadd(f"auth:sesion:{usuario['id']}", jti)
    r_sesion.expire(f"auth:sesion:{usuario['id']}", minutos * 60)
    return jwt.encode(carga, Config.SECRET_KEY, algorithm=Config.JWT_ALG)


def revocar_token(token):
    """RF04, HU12. El TTL es la vida RESTANTE: una vez que el token expira
    solo, la entrada de revocación ya no aporta nada y ocuparía memoria."""
    try:
        carga = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.JWT_ALG])
    except jwt.PyJWTError:
        return
    restante = int(carga["exp"] - dt.datetime.now(dt.timezone.utc).timestamp())
    if restante > 0:
        r_sesion.setex(f"auth:jti:revocado:{carga['jti']}", restante, "1")
    r_sesion.srem(f"auth:sesion:{carga['sub']}", carga["jti"])


def leer_token(token):
    if not token:
        return None
    try:
        carga = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.JWT_ALG])
    except jwt.PyJWTError:
        return None
    if r_sesion.exists(f"auth:jti:revocado:{carga['jti']}"):
        return None                      # revocado antes de expirar
    return {
        "id": int(carga["sub"]), "rol": carga["rol"], "nombre": carga["nombre"],
        "microhub_id": carga.get("microhub_id"), "jti": carga["jti"],
    }


# --------------------------------------------------------------------
# Permisos
# --------------------------------------------------------------------
def permisos_de(rol_clave):
    llave = f"cache:permisos:{rol_clave}"
    guardado = r_cache.smembers(llave)
    if guardado:
        return guardado
    filas = consultar(
        "SELECT p.clave FROM permiso p "
        "JOIN rol_permiso rp ON rp.permiso_id = p.id "
        "JOIN rol r ON r.id = rp.rol_id WHERE r.clave = %s", (rol_clave,))
    claves = {f["clave"] for f in filas}
    if claves:
        r_cache.sadd(llave, *claves)
        r_cache.expire(llave, 300)
    return claves


def auditar(modulo, accion, detalle=None, entidad=None, entidad_id=None, exitoso=True):
    """Para eventos que NO son escrituras de tabla: login, logout, 403.
    Las escrituras las audita el trigger del motor (RN30)."""
    with con_actual(autocommit=True) as con, con.cursor() as cur:
        cur.execute(
            "INSERT INTO auditoria (usuario_id, modulo, accion, entidad, entidad_id, "
            "detalle, exitoso, ip_origen, correo_intento) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (getattr(g, "usuario", {}).get("id") if getattr(g, "usuario", None) else None,
             modulo, accion, entidad, entidad_id, detalle, exitoso,
             request.remote_addr, getattr(g, "correo_intento", None)))


def requiere(*permisos):
    """Verifica permiso en CADA ruta protegida.

    RNF23 y HU10 CA2: ocultar la opción del menú no es control de acceso.
    Aunque el enlace desaparezca, entrar por URL debe devolver 403.
    """
    from functools import wraps

    def decorador(f):
        @wraps(f)
        def envoltura(*a, **kw):
            if not getattr(g, "usuario", None):
                flash("Inicia sesión para continuar.", "info")
                return redirect(url_for("auth.entrar", siguiente=request.path))
            tiene = permisos_de(g.usuario["rol"])
            if permisos and not any(p in tiene for p in permisos):
                auditar("acceso", "acceso_denegado",
                        f"Ruta {request.path} sin el permiso requerido.",
                        exitoso=False)
                return render_403()
            return f(*a, **kw)
        return envoltura
    return decorador


def render_403():
    from flask import render_template
    return render_template("403.html"), 403


# --------------------------------------------------------------------
# Traducción de errores del motor a lenguaje de persona
# --------------------------------------------------------------------
TRADUCCIONES = [
    ("ck_inv_existencia", "No hay existencia suficiente para completar la operación."),
    ("RN09", None),   # el mensaje del motor ya es claro; se usa tal cual
    ("RN14", None),
    ("RN17", "Alguien tomó la última unidad mientras confirmabas. Vuelve a intentarlo."),
    ("RN20", None),
    ("RN24", "Falta el motivo. La reasignación manual siempre lo exige."),
    ("RN31", "La bitácora no se puede modificar. Ningún perfil tiene esa facultad."),
    ("ck_entrega_cierre", "Para cerrar hace falta el resultado, el monto cobrado y el cambio."),
    ("ck_entrega_fallida", "Una entrega fallida necesita el motivo."),
    ("ck_decision_manual", "Falta el motivo de la reasignación."),
    ("uq_domicilio_activo", "Ya tienes un domicilio registrado. En esta etapa se maneja uno solo."),
    ("uq_usuario_correo", "Ese correo ya está registrado."),
]


def mensaje_de_error(exc) -> str:
    texto = str(exc)
    for marca, humano in TRADUCCIONES:
        if marca in texto:
            if humano:
                return humano
            # El motor ya explica la regla; se limpia el prefijo técnico.
            limpio = texto.split("CONTEXT:")[0].strip()
            return limpio.replace("ERROR:", "").strip()
    return "No se pudo completar la operación. Revisa los datos e intenta de nuevo."
