"""
Servicio de autenticación · puerto 5101 · contrato v1

  POST /api/v1/auth/login     credenciales → sesión (token de acceso + renovación + usuario y permisos)
  POST /api/v1/auth/renovar   token de renovación → tokens nuevos (rotación)
  POST /api/v1/auth/salir     revoca el acceso del encabezado y, si viene, la renovación
  GET  /api/v1/auth/validar   valida el token del encabezado contra la firma y contra Redis

Claves de Redis (base 0, las mismas que usa el web):
  auth:sesion:{usuario_id}        conjunto de jti de acceso activos
  auth:jti:revocado:{jti}         revocación con TTL = vida restante del token
  auth:refresh:{sha256(token)}    renovación (se guarda el hash, nunca el token)
  auth:intentos:{correo}          intentos fallidos; auth:bloqueo:{correo} bloqueo temporal
"""
import datetime as dt
import hashlib
import secrets
import uuid

import bcrypt
import jwt
from flask import g

from comun import config
from comun.base import (SESION_INVALIDA, crear_app, documentar, leer_acceso, leer_cuerpo, responder,
                        token_de_cabecera)
from comun.base_errores import ErrorApi
from comun.datos import auditar, conexion, consultar, parametro, permisos_de, r_sesion
from comun.validar import CORREO, Campo, validar

app = crear_app("auth", "Microhubs · Autenticación",
                "Inicio, renovación, validación y cierre de sesión con JWT y Redis.", 5101)
P = config.PREFIJO


def _usuario(where, valor):
    return consultar(
        "SELECT u.id, u.nombre, COALESCE(u.apellidos,'') AS apellidos, u.correo, u.hash_contrasena, "
        "u.estatus::text AS estatus, u.microhub_id, r.clave AS rol "
        f"FROM usuario u JOIN rol r ON r.id = u.rol_id WHERE {where}", (valor,), una=True)


def _hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


def _tokens(u):
    """Emite acceso (JWT) + renovación (opaco) y registra la sesión en Redis."""
    minutos = int(parametro("jwt_acceso_minutos", 15))
    dias = int(parametro("jwt_refresh_dias", 7))
    ahora = dt.datetime.now(dt.timezone.utc)
    exp = ahora + dt.timedelta(minutes=minutos)
    jti = uuid.uuid4().hex
    acceso = jwt.encode({"sub": str(u["id"]), "rol": u["rol"], "nombre": u["nombre"],
                         "microhub_id": u["microhub_id"], "jti": jti, "typ": "acceso", "iat": ahora, "exp": exp},
                        config.SECRET_KEY, algorithm=config.JWT_ALG)
    renovacion = "rt_" + secrets.token_hex(16)
    pipe = r_sesion.pipeline()
    pipe.sadd(f"auth:sesion:{u['id']}", jti)
    pipe.expire(f"auth:sesion:{u['id']}", max(minutos * 60, r_sesion.ttl(f"auth:sesion:{u['id']}") or 0))
    pipe.hset(f"auth:refresh:{_hash(renovacion)}",
              mapping={"usuario_id": u["id"], "acceso_jti": jti, "acceso_exp": int(exp.timestamp())})
    pipe.expire(f"auth:refresh:{_hash(renovacion)}", dias * 86400)
    pipe.execute()
    return {"token_acceso": acceso, "token_renovacion": renovacion, "tipo": "Bearer", "expira_en": minutos * 60}


def _revocar_acceso(uid, jti, exp):
    restante = int(exp - dt.datetime.now(dt.timezone.utc).timestamp())
    if restante > 0:
        r_sesion.setex(f"auth:jti:revocado:{jti}", restante, "1")
    r_sesion.srem(f"auth:sesion:{uid}", jti)


def _consumir_renovacion(token):
    """Lee y ELIMINA el registro de renovación (un token de renovación sirve una sola vez)."""
    if not isinstance(token, str) or not token.startswith("rt_") or len(token) > 80:
        return None
    llave = f"auth:refresh:{_hash(token)}"
    pipe = r_sesion.pipeline()
    pipe.hgetall(llave)
    pipe.delete(llave)
    registro, _ = pipe.execute()
    return registro or None


# --------------------------------------------------------------------
@app.post(f"{P}/auth/login")
def login():
    d = validar(leer_cuerpo("login"), [
        Campo("correo", patron=CORREO, max_len=120, mensaje="Ingresa un correo válido."),
        Campo("clave", min_len=1, max_len=200), Campo("dispositivo", req=False, max_len=120)])
    correo = d["correo"].lower()
    maximo = int(parametro("intentos_fallidos_max", 5))
    bloqueo = int(parametro("bloqueo_minutos", 15))
    if r_sesion.exists(f"auth:bloqueo:{correo}"):
        auditar("auth", "login_fallido", "API: intento sobre cuenta bloqueada.", exitoso=False, correo=correo)
        raise ErrorApi(423, "CUENTA_BLOQUEADA", f"Cuenta bloqueada temporalmente. Intenta en {bloqueo} minutos.")
    u = _usuario("lower(u.correo) = %s", correo)
    valido = False
    if u and u["estatus"] == "activo":
        try:
            valido = bcrypt.checkpw(d["clave"].encode(), u["hash_contrasena"].encode())
        except ValueError:
            valido = False
    if not valido:
        fallos = r_sesion.incr(f"auth:intentos:{correo}")
        r_sesion.expire(f"auth:intentos:{correo}", bloqueo * 60)
        if u:
            with conexion({"id": u["id"], "rol": "sistema"}) as con, con.cursor() as cur:
                cur.execute("UPDATE usuario SET intentos_fallidos = intentos_fallidos + 1 WHERE id = %s", (u["id"],))
        if fallos >= maximo:
            r_sesion.setex(f"auth:bloqueo:{correo}", bloqueo * 60, "1")
            auditar("auth", "bloqueo_cuenta", f"API: {maximo} intentos fallidos.", exitoso=False, correo=correo)
            raise ErrorApi(423, "CUENTA_BLOQUEADA",
                           f"Intento {fallos} de {maximo}: la cuenta queda bloqueada {bloqueo} minutos.")
        auditar("auth", "login_fallido", f"API: intento {fallos} de {maximo}.", exitoso=False, correo=correo)
        raise ErrorApi(401, "CREDENCIALES_INVALIDAS", f"Correo o clave incorrectos. Intento {fallos} de {maximo}.")
    r_sesion.delete(f"auth:intentos:{correo}")
    with conexion({"id": u["id"], "rol": u["rol"]}) as con, con.cursor() as cur:
        cur.execute("UPDATE usuario SET intentos_fallidos = 0, ultimo_acceso = now() WHERE id = %s", (u["id"],))
    sesion = _tokens(u)
    sesion["usuario"] = {"id": u["id"], "nombre": u["nombre"], "apellidos": u["apellidos"], "correo": u["correo"],
                         "rol": u["rol"], "microhub_id": u["microhub_id"], "permisos": sorted(permisos_de(u["rol"]))}
    g.usuario = {"id": u["id"], "rol": u["rol"]}
    auditar("auth", "login_exitoso", "Inicio de sesión por API" + (f" ({d['dispositivo']})" if d.get("dispositivo") else "") + ".")
    return responder(sesion, raiz="sesion")


@app.post(f"{P}/auth/renovar")
def renovar():
    d = validar(leer_cuerpo("renovar"), [Campo("token_renovacion", max_len=80)])
    registro = _consumir_renovacion(d["token_renovacion"])
    if not registro:
        raise ErrorApi(401, "TOKEN_INVALIDO", SESION_INVALIDA)
    u = _usuario("u.id = %s", int(registro["usuario_id"]))
    _revocar_acceso(int(registro["usuario_id"]), registro["acceso_jti"], int(registro["acceso_exp"]))
    if not u or u["estatus"] != "activo":
        raise ErrorApi(401, "TOKEN_INVALIDO", "La cuenta ya no está activa.")
    return responder(_tokens(u), raiz="tokens")


@app.post(f"{P}/auth/salir")
def salir():
    """Revoca el acceso del encabezado; si el cuerpo trae la renovación, también la revoca."""
    d = validar(leer_cuerpo("salir", obligatorio=False), [Campo("token_renovacion", req=False, max_len=80)])
    revocado = False
    token = token_de_cabecera(obligatorio=False)
    if token:
        try:
            u = leer_acceso(token)
            _revocar_acceso(u["id"], u["jti"], u["exp"])
            g.usuario, revocado = u, True
        except ErrorApi:
            pass
    if d.get("token_renovacion"):
        registro = _consumir_renovacion(d["token_renovacion"])
        if registro:
            _revocar_acceso(int(registro["usuario_id"]), registro["acceso_jti"], int(registro["acceso_exp"]))
            revocado = True
            g.setdefault("usuario", {"id": int(registro["usuario_id"]), "rol": None})
    if not revocado:
        raise ErrorApi(401, "TOKEN_INVALIDO", SESION_INVALIDA)
    auditar("auth", "logout", "Cierre de sesión por API.")
    return responder(None, 204)


@app.get(f"{P}/auth/validar")
def validar_token():
    u = g.usuario = leer_acceso(token_de_cabecera())
    restante = max(0, u["exp"] - int(dt.datetime.now(dt.timezone.utc).timestamp()))
    return responder({"valido": True, "expira_en": restante,
                      "usuario": {"id": u["id"], "rol": u["rol"], "microhub_id": u["microhub_id"]}},
                     raiz="validacion")


# --------------------------------------------------------------------
documentar(app, "POST", f"{P}/auth/login", "Iniciar sesión", publico=True, cuerpo="Login.ok",
           descripcion="Valida correo y clave (bcrypt). Cada intento fallido se cuenta en Redis; al llegar a "
                       "`intentos_fallidos_max` la cuenta se bloquea `bloqueo_minutos` (tabla configuracion). "
                       "La sesión incluye los permisos del perfil. Límite: 30 solicitudes por minuto por IP.",
           respuestas={200: ("Sesión iniciada", "Sesion.ok")}, errores=[400, 401, 415, 422, 423])
documentar(app, "POST", f"{P}/auth/renovar", "Renovar sesión", publico=True, cuerpo="Renovar.ok",
           descripcion="Entrega tokens nuevos. El token de renovación usado y su acceso anterior quedan "
                       "inservibles (rotación): un token de renovación sirve una sola vez.",
           respuestas={200: ("Tokens nuevos", "Tokens.ok")}, errores=[400, 401, 422])
documentar(app, "POST", f"{P}/auth/salir", "Cerrar sesión", publico=True, cuerpo="Salir.ok",
           descripcion="Revoca el token de acceso del encabezado (auth:jti:revocado) y, si se envía, el token de "
                       "renovación. Funciona aunque el acceso ya haya vencido, si se manda la renovación.",
           respuestas={204: ("Sesión cerrada, sin cuerpo", None)}, errores=[400, 401, 422])
documentar(app, "GET", f"{P}/auth/validar", "Validar token",
           descripcion="Comprueba firma, vigencia y que la sesión siga activa en Redis. Útil para otros componentes.",
           respuestas={200: ("Token válido", "Validacion.ok")})
