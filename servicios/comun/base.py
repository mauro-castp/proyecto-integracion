"""
base.py — Plantilla que comparten los ocho microservicios.

Cada servicio se crea con crear_app() y hereda, sin repetir código:
  · Rutas versionadas bajo /api/v1.
  · Respuesta JSON o XML según Accept; cuerpo JSON o XML según Content-Type.
    Todo cuerpo XML se valida contra los XSD oficiales antes de procesarse.
  · Autenticación común: JWT HS256 + sesión activa en Redis
    (auth:sesion:{usuario} y auth:jti:revocado:{jti}), las mismas claves
    que usa el sistema web.
  · Autorización por permiso (tabla rol_permiso, caché Redis 5 min).
  · Error estandarizado {codigo, mensaje, detalles, traza_id}.
  · Límite de consumo por IP y minuto (Redis) con Retry-After.
  · Registro de actividad en MongoDB (logs_tecnicos, metricas_servicio).
  · /salud y OpenAPI 3 con Swagger UI en /api/v1/docs.
"""
import hashlib
import json
import math
import sys
import time
import uuid
from functools import wraps

import jwt
import psycopg
import redis
from flask import Flask, Response, g, request
from werkzeug.exceptions import HTTPException

from . import config
from .base_errores import ErrorApi, filtro_invalido
from .datos import (ahora, auditar, conexion, mensaje_motor, mongo, mongo_disponible, mongo_insertar,
                    permisos_de, r_cache, r_sesion)
from .esquemas import errores_xml
from .formatos import NS, a_xml, leer_xml

CODIGOS_HTTP = {400: "SOLICITUD_INVALIDA", 401: "TOKEN_INVALIDO", 403: "PROHIBIDO", 404: "NO_ENCONTRADO",
                405: "METODO_NO_PERMITIDO", 409: "CONFLICTO", 413: "CUERPO_DEMASIADO_GRANDE",
                415: "FORMATO_NO_SOPORTADO", 422: "VALIDACION", 423: "CUENTA_BLOQUEADA",
                429: "LIMITE_EXCEDIDO", 500: "ERROR_INTERNO", 503: "SERVICIO_NO_DISPONIBLE"}
SESION_INVALIDA = "La sesión venció o fue cerrada. Inicia sesión de nuevo."


# --------------------------------------------------------------------
# Formatos
# --------------------------------------------------------------------
def quiere_xml():
    mejor = request.accept_mimetypes.best_match(["application/json", "application/xml", "text/xml"])
    return mejor in ("application/xml", "text/xml")


def responder(datos, status=200, raiz=None, xml=None, items=None, encabezados=None):
    """datos → JSON; en XML la raíz es `raiz` (o xml=(raiz, datos_xml) si la forma difiere)."""
    if status == 204:
        resp = Response(status=204)
    elif quiere_xml():
        r, cuerpo = xml if xml else (raiz or "respuesta", datos)
        resp = Response(a_xml(r, cuerpo, items), status=status, content_type="application/xml; charset=utf-8")
    else:
        resp = Response(json.dumps(datos, ensure_ascii=False, default=_json_default), status=status,
                        content_type="application/json; charset=utf-8")
    for k, v in (encabezados or {}).items():
        resp.headers[k] = v
    return resp


def lista(datos, pag, item, raiz, transformar=None):
    """Página del contrato: {datos: [...], paginacion: {...}}; en XML <raiz><datos><item/>…"""
    filas = [transformar(d) for d in datos] if transformar else datos
    return responder({"datos": filas, "paginacion": pag}, raiz=raiz, items={"datos": item})


def _json_default(v):
    from decimal import Decimal
    import datetime as dt
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (dt.datetime, dt.date)):
        return v.isoformat()
    return str(v)


def leer_cuerpo(raiz_xml=None, obligatorio=True):
    """Cuerpo JSON o XML como dict. El XML debe cumplir el XSD y tener la raíz esperada."""
    tipo = (request.mimetype or "").lower()
    crudo = request.get_data(cache=True)
    if not crudo:
        if obligatorio:
            raise ErrorApi(400, "SOLICITUD_INVALIDA", "Falta el cuerpo de la solicitud.")
        return {}
    if tipo in ("application/xml", "text/xml"):
        try:
            nombre, ns, datos = leer_xml(crudo)
        except Exception:
            raise ErrorApi(400, "XML_INVALIDO", "El cuerpo XML no está bien formado o contiene DTD/entidades.")
        if ns != NS:
            raise ErrorApi(400, "XML_INVALIDO", f"Se esperaba el espacio de nombres {NS}.")
        if raiz_xml and nombre != raiz_xml:
            raise ErrorApi(400, "XML_INVALIDO", f"Se esperaba el elemento raíz <{raiz_xml}>.")
        errores = errores_xml(crudo)
        if errores:
            raise ErrorApi(422, "VALIDACION", "El XML no cumple el contrato (XSD).",
                           [{"campo": "xml", "mensaje": e} for e in errores])
        return datos
    if tipo == "application/json" or not tipo:
        try:
            datos = json.loads(crudo.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            raise ErrorApi(400, "JSON_INVALIDO", "El cuerpo JSON no está bien formado.")
        if not isinstance(datos, dict):
            raise ErrorApi(400, "JSON_INVALIDO", "Se esperaba un objeto JSON.")
        return datos
    raise ErrorApi(415, "FORMATO_NO_SOPORTADO", "Usa Content-Type application/json o application/xml.")


# --------------------------------------------------------------------
# Paginación y filtros
# --------------------------------------------------------------------
def leer_paginacion(defecto=20, maximo=100):
    try:
        pagina = int(request.args.get("pagina", 1))
        por_pagina = int(request.args.get("por_pagina", defecto))
    except ValueError:
        raise filtro_invalido("pagina", "pagina y por_pagina deben ser enteros.")
    if pagina < 1:
        raise filtro_invalido("pagina", "pagina debe ser 1 o mayor.")
    if not 1 <= por_pagina <= maximo:
        raise filtro_invalido("por_pagina", f"por_pagina debe estar entre 1 y {maximo}.")
    return pagina, por_pagina, (pagina - 1) * por_pagina


def paginacion(pagina, por_pagina, total):
    return {"pagina": pagina, "por_pagina": por_pagina, "total": int(total),
            "paginas": math.ceil(total / por_pagina) if total else 0}


def texto_busqueda():
    q = (request.args.get("q") or "").strip()
    if len(q) > 80:
        raise filtro_invalido("q", "La búsqueda admite hasta 80 caracteres.")
    return q


def filtro_opcion(nombre, opciones):
    v = (request.args.get(nombre) or "").strip()
    if v and v not in opciones:
        raise filtro_invalido(nombre, f"Valor no permitido para {nombre}: {v}.")
    return v or None


def filtro_entero(nombre):
    v = (request.args.get(nombre) or "").strip()
    if not v:
        return None
    if not v.isdigit():
        raise filtro_invalido(nombre, f"{nombre} debe ser un entero.")
    return int(v)


def filtro_fecha(nombre):
    import datetime as dt
    v = (request.args.get(nombre) or "").strip()
    if not v:
        return None
    try:
        return dt.date.fromisoformat(v)
    except ValueError:
        raise filtro_invalido(nombre, f"{nombre} debe tener el formato AAAA-MM-DD.")


# --------------------------------------------------------------------
# Autenticación y autorización comunes
# --------------------------------------------------------------------
def leer_acceso(token):
    """Valida firma, vigencia y sesión activa en Redis. Devuelve el usuario."""
    try:
        carga = jwt.decode(token, config.SECRET_KEY, algorithms=[config.JWT_ALG],
                           options={"require": ["exp", "sub", "jti"]})
    except jwt.PyJWTError:
        raise ErrorApi(401, "TOKEN_INVALIDO", SESION_INVALIDA)
    if carga.get("typ") not in (None, "acceso"):
        raise ErrorApi(401, "TOKEN_INVALIDO", SESION_INVALIDA)
    try:
        if r_sesion.exists(f"auth:jti:revocado:{carga['jti']}"):
            raise ErrorApi(401, "TOKEN_INVALIDO", SESION_INVALIDA)
        if not r_sesion.sismember(f"auth:sesion:{carga['sub']}", carga["jti"]):
            raise ErrorApi(401, "TOKEN_INVALIDO", SESION_INVALIDA)
    except redis.RedisError:
        # Sin Redis no se sabe si el token fue revocado: se cierra el paso.
        raise ErrorApi(503, "SERVICIO_NO_DISPONIBLE", "No se pudo validar la sesión. Intenta más tarde.")
    return {"id": int(carga["sub"]), "rol": carga.get("rol"), "nombre": carga.get("nombre"),
            "microhub_id": carga.get("microhub_id"), "jti": carga["jti"], "exp": int(carga["exp"])}


def token_de_cabecera(obligatorio=True):
    cab = request.headers.get("Authorization", "")
    if cab.startswith("Bearer ") and cab[7:].strip():
        return cab[7:].strip()
    if obligatorio:
        raise ErrorApi(401, "TOKEN_INVALIDO", "Falta el encabezado Authorization: Bearer <token>.")
    return None


def requiere(*permisos):
    """Exige sesión válida y, si se indican, AL MENOS UNO de los permisos."""
    def decorador(f):
        @wraps(f)
        def envoltura(*a, **kw):
            g.usuario = leer_acceso(token_de_cabecera())
            if permisos and not set(permisos) & permisos_de(g.usuario["rol"]):
                auditar(g.servicio, "acceso_denegado",
                        f"{request.method} {request.path} sin {' o '.join(permisos)}", exitoso=False)
                raise ErrorApi(403, "PROHIBIDO", "Tu perfil no tiene permiso para esta operación.")
            return f(*a, **kw)
        return envoltura
    return decorador


def tiene(permiso):
    return permiso in permisos_de(g.usuario["rol"])


# --------------------------------------------------------------------
# Fábrica
# --------------------------------------------------------------------
def crear_app(servicio, titulo, descripcion, puerto, dependencias=("postgres", "redis")):
    app = Flask(servicio)
    app.config.update(MAX_CONTENT_LENGTH=config.MAX_CUERPO_BYTES, JSON_AS_ASCII=False)
    app.config["SERVICIO"] = servicio
    app.config["DOC"] = {"titulo": titulo, "descripcion": descripcion, "puerto": puerto, "rutas": []}

    @app.before_request
    def _antes():
        g.servicio = servicio
        g.inicio = time.perf_counter()
        traza = request.headers.get("X-Traza-Id", "")
        g.traza_id = traza if 8 <= len(traza) <= 64 and traza.replace("-", "").isalnum() else str(uuid.uuid4())
        if not request.path.endswith(("/salud", "/docs", "/openapi.json")):
            _limitar()

    @app.after_request
    def _despues(resp):
        resp.headers["X-Traza-Id"] = g.get("traza_id", "")
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers.setdefault("Cache-Control", "no-store")
        _registrar(resp.status_code)
        return resp

    @app.errorhandler(ErrorApi)
    def _error_api(e):
        return respuesta_error(e.status, e.codigo, e.mensaje, e.detalles, e.encabezados)

    @app.errorhandler(HTTPException)
    def _error_http(e):
        mensajes = {404: "No existe el recurso solicitado.", 405: "Método no permitido en esta ruta.",
                    413: "El cuerpo excede el tamaño máximo permitido (8 MB)."}
        return respuesta_error(e.code, CODIGOS_HTTP.get(e.code, "ERROR_HTTP"),
                               mensajes.get(e.code, e.description or "Error HTTP."))

    @app.errorhandler(psycopg.errors.RaiseException)
    @app.errorhandler(psycopg.errors.CheckViolation)
    @app.errorhandler(psycopg.errors.ForeignKeyViolation)
    @app.errorhandler(psycopg.errors.NotNullViolation)
    def _error_regla(e):
        return respuesta_error(422, "REGLA_NEGOCIO", mensaje_motor(e))

    @app.errorhandler(psycopg.errors.UniqueViolation)
    def _error_unico(e):
        return respuesta_error(409, "CONFLICTO", "Ya existe un registro con esos datos.")

    @app.errorhandler(psycopg.OperationalError)
    @app.errorhandler(redis.RedisError)
    def _error_infra(e):
        g.excepcion = f"{type(e).__name__}: {e}"
        return respuesta_error(503, "SERVICIO_NO_DISPONIBLE", "Una base de datos no responde. Intenta más tarde.")

    @app.errorhandler(Exception)
    def _error_interno(e):
        g.excepcion = f"{type(e).__name__}: {e}"
        print(json.dumps({"nivel": "ERROR", "traza_id": g.get("traza_id"), "error": g.excepcion}),
              file=sys.stderr, flush=True)
        return respuesta_error(500, "ERROR_INTERNO", "Ocurrió un error inesperado.")

    @app.get("/salud")
    @app.get(f"{config.PREFIJO}/salud")
    def salud():
        dep = {"postgres": "no_aplica", "redis": "no_aplica", "mongo": "no_aplica"}
        if "postgres" in dependencias:
            dep["postgres"] = "ok" if _probar(_pg) else "error"
        if "redis" in dependencias:
            dep["redis"] = "ok" if _probar(r_sesion.ping) else "error"
        if "mongo" in dependencias:
            dep["mongo"] = "ok" if mongo_disponible() else "error"
        estado = "ok" if "error" not in dep.values() else "degradado"
        cuerpo = {"servicio": servicio, "version": config.VERSION, "estado": estado, "dependencias": dep}
        return responder(cuerpo, 200 if estado == "ok" else 503, raiz="salud")

    @app.get(f"{config.PREFIJO}/openapi.json")
    def openapi():
        from .documentacion import especificacion
        return Response(json.dumps(especificacion(app), ensure_ascii=False, indent=2, default=_json_default),
                        content_type="application/json; charset=utf-8")

    @app.get(f"{config.PREFIJO}/docs")
    def docs():
        from .documentacion import pagina_swagger
        resp = Response(pagina_swagger(titulo), content_type="text/html; charset=utf-8")
        resp.headers["Cache-Control"] = "no-cache"
        return resp

    return app


def documentar(app, metodo, ruta, resumen, **kw):
    """Describe una ruta para OpenAPI (ver documentacion.py)."""
    app.config["DOC"]["rutas"].append({"metodo": metodo, "ruta": ruta, "resumen": resumen, **kw})


# --------------------------------------------------------------------
# Internos
# --------------------------------------------------------------------
def respuesta_error(status, codigo, mensaje, detalles=None, encabezados=None):
    g.codigo_error = codigo
    cuerpo = {"codigo": codigo, "mensaje": mensaje}
    if detalles:
        cuerpo["detalles"] = detalles
    cuerpo["traza_id"] = g.get("traza_id") or str(uuid.uuid4())
    enc = dict(encabezados or {})
    if status == 401:
        enc["WWW-Authenticate"] = 'Bearer realm="microhubs"'
    return responder({"error": cuerpo}, status, xml=("error", cuerpo), items={"detalles": "detalle"},
                     encabezados=enc)


def _limitar():
    ip = hashlib.sha256((request.remote_addr or "").encode()).hexdigest()[:16]
    ahora_s = time.time()
    minuto = int(ahora_s // 60)
    es_login = request.path.endswith("/auth/login")
    llave = f"rate:{'login' if es_login else g.servicio}:{ip}:{minuto}"
    limite = config.LIMITE_LOGIN_POR_MINUTO if es_login else config.LIMITE_POR_MINUTO
    try:
        n = r_cache.incr(llave)
        if n == 1:
            r_cache.expire(llave, 120)
    except redis.RedisError:
        return                                  # el límite no bloquea si Redis falla
    if n > limite:
        espera = max(1, int(60 - ahora_s % 60))
        raise ErrorApi(429, "LIMITE_EXCEDIDO", f"Máximo {limite} solicitudes por minuto. Espera {espera} segundos.",
                       encabezados={"Retry-After": str(espera)})


def _registrar(status):
    dur = int((time.perf_counter() - g.get("inicio", time.perf_counter())) * 1000)
    u = g.get("usuario")
    regla = request.url_rule.rule if request.url_rule else request.path
    nivel = "ERROR" if status >= 500 else "WARN" if status >= 400 else "INFO"
    linea = {"nivel": nivel, "componente": g.get("servicio", "?"), "registrado_en": ahora(),
             "correlacion_id": g.get("traza_id", ""), "mensaje": f"{request.method} {request.path} -> {status}",
             "usuario_id": int(u["id"]) if u and u.get("id") else None, "ruta": regla, "duracion_ms": dur,
             "contexto": {"metodo": request.method, "status": status, "formato": "xml" if quiere_xml() else "json",
                          "codigo_error": g.get("codigo_error")},
             "excepcion": {"detalle": g.excepcion} if g.get("excepcion") else None}
    if config.LOG_STDOUT:
        print(json.dumps({**linea, "registrado_en": linea["registrado_en"].isoformat()}, ensure_ascii=False), flush=True)
    if regla.endswith(("/salud", "/docs", "/openapi.json")):
        return
    mongo_insertar("logs_tecnicos", linea)
    mongo_insertar("metricas_servicio", {"momento": linea["registrado_en"], "duracion_ms": dur,
                                         "etiquetas": {"servicio": g.get("servicio", "?"), "ruta": regla,
                                                       "metodo": request.method, "status": status}})


def _probar(fn):
    try:
        fn()
        return True
    except Exception:
        return False


def _pg():
    with conexion(autocommit=True) as con, con.cursor() as cur:
        cur.execute("SELECT 1")
