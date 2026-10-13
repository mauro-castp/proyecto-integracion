"""
datos.py — PostgreSQL, Redis y MongoDB para los microservicios.

Mismo principio que el sistema web: las reglas viven en PostgreSQL. Cada
servicio abre la transacción declarando quién actúa (app.usuario_id y
app.rol); los triggers del motor validan las transiciones de estado y
escriben la bitácora. Un pedido cerrado desde la app móvil queda auditado
y avisa al cliente igual que si se cerrara desde el portal web.

MongoDB guarda lo que no es transaccional: evidencias, puntos GPS, trazas de
simulaciones, sincronizaciones móviles y logs técnicos.
"""
import json
import sys
import datetime as dt
from contextlib import contextmanager

import psycopg
import redis
from flask import g, has_request_context, request
from psycopg.rows import dict_row

from . import config

# Redis: base 0 = sesión y seguridad (noeviction); base 1 = caché y límites.
r_sesion = redis.Redis.from_url(config.REDIS_URL, db=0, decode_responses=True,
                                socket_timeout=2, socket_connect_timeout=2)
r_cache = redis.Redis.from_url(config.REDIS_URL, db=1, decode_responses=True,
                               socket_timeout=2, socket_connect_timeout=2)

_mongo = {"db": None, "indices": False}


def actor():
    return g.get("usuario") if has_request_context() else None


@contextmanager
def conexion(usuario=None, autocommit=False):
    """Conexión con el actor declarado para los triggers de auditoría y transición."""
    u = usuario if usuario is not None else actor()
    con = psycopg.connect(config.PG_DSN, row_factory=dict_row, autocommit=autocommit, connect_timeout=5)
    try:
        with con.cursor() as cur:
            cur.execute("SET search_path TO microhubs, public")
            if u and u.get("id"):
                cur.execute("SELECT set_config('app.usuario_id', %s, false)", (str(u["id"]),))
            cur.execute("SELECT set_config('app.rol', %s, false)", ((u or {}).get("rol") or "sistema",))
            ip = request.remote_addr if has_request_context() else None
            cur.execute("SELECT set_config('app.ip_origen', %s, false)", (ip or "127.0.0.1",))
        yield con
        if not autocommit:
            con.commit()
    except Exception:
        if not autocommit:
            con.rollback()
        raise
    finally:
        con.close()


def consultar(sql, params=(), una=False):
    with conexion() as con, con.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone() if una else cur.fetchall()


def parametro(clave, defecto=None):
    fila = consultar("SELECT valor FROM configuracion WHERE clave=%s AND ambito='global'", (clave,), una=True)
    return fila["valor"] if fila else defecto


def auditar(modulo, accion, detalle=None, entidad=None, entidad_id=None, exitoso=True, correo=None, usuario_id=None):
    """Eventos que no son escrituras de tabla (login, logout, acceso denegado).
    Las escrituras las audita el trigger fn_auditar_cambio del motor."""
    try:
        with conexion(autocommit=True) as con, con.cursor() as cur:
            cur.execute(
                "INSERT INTO auditoria (usuario_id, modulo, accion, entidad, entidad_id, detalle, exitoso, "
                "ip_origen, correo_intento) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (usuario_id or (actor() or {}).get("id"), modulo, accion, entidad, entidad_id,
                 (detalle or "")[:500] or None, exitoso,
                 request.remote_addr if has_request_context() else None, correo))
    except Exception as e:                    # la auditoría nunca tumba la petición
        print(json.dumps({"nivel": "ERROR", "mensaje": f"auditoria: {e}"}), file=sys.stderr)


def permisos_de(rol):
    """Permisos del rol con la misma caché de Redis que usa el web (5 minutos)."""
    llave = f"cache:permisos:{rol}"
    try:
        guardado = r_cache.smembers(llave)
        if guardado:
            return guardado
    except redis.RedisError:
        pass
    filas = consultar("SELECT p.clave FROM permiso p JOIN rol_permiso rp ON rp.permiso_id = p.id "
                      "JOIN rol r ON r.id = rp.rol_id WHERE r.clave = %s", (rol,))
    claves = {f["clave"] for f in filas}
    if claves:
        try:
            r_cache.sadd(llave, *claves)
            r_cache.expire(llave, 300)
        except redis.RedisError:
            pass
    return claves


# --------------------------------------------------------------------
# MongoDB
# --------------------------------------------------------------------
def mongo():
    """Base de eventos, o None si MongoDB no está configurado."""
    if _mongo["db"] is None and config.MONGO_URL:
        from pymongo import MongoClient
        _mongo["db"] = MongoClient(config.MONGO_URL, serverSelectionTimeoutMS=2000, tz_aware=True)[config.MONGO_DB]
    if _mongo["db"] is not None and not _mongo["indices"]:
        _asegurar_indices(_mongo["db"])
    return _mongo["db"]


def usar_mongo(db):
    """Inyecta una base (pruebas con mongomock)."""
    _mongo["db"], _mongo["indices"] = db, False


def _asegurar_indices(db):
    """Los índices se crean también sobre volúmenes que ya existían (initdb no corre otra vez)."""
    try:
        db.documentos.create_index([("referencia.tipo", 1), ("referencia.id", 1)], name="ix_referencia")
        db.documentos.create_index([("subido_por", 1), ("creado_en", -1)], name="ix_autor")
        db.ubicaciones_entrega.create_index([("entrega_id", 1), ("capturado_en", 1)], name="ix_entrega_tiempo")
        db.ejecuciones_analiticas.create_index([("tipo_analisis", 1), ("ejecutado_en", -1)], name="ix_tipo")
        db.sincronizaciones_moviles.create_index("operacion_uuid", name="ix_uuid", unique=True)
        _mongo["indices"] = True
    except Exception as e:
        print(json.dumps({"nivel": "WARN", "mensaje": f"indices mongo: {e}"}), file=sys.stderr)


def mongo_disponible():
    db = mongo()
    if db is None:
        return False
    try:
        db.command("ping")
        return True
    except Exception:
        return False


def mongo_insertar(coleccion, documento):
    """Inserción accesoria (logs, métricas): si MongoDB falla, la petición sigue."""
    try:
        db = mongo()
        if db is None:
            return None
        return db[coleccion].insert_one(documento).inserted_id
    except Exception as e:
        print(json.dumps({"nivel": "WARN", "mensaje": f"mongo {coleccion}: {e}"}), file=sys.stderr)
        return None


def ahora():
    return dt.datetime.now(dt.timezone.utc)


# --------------------------------------------------------------------
# Errores del motor en lenguaje de persona
# --------------------------------------------------------------------
TRADUCCIONES = [
    ("ck_inv_existencia", "No hay existencia suficiente para completar la operación."),
    ("ck_entrega_cierre", "Para cerrar hace falta el resultado, el monto cobrado y el cambio."),
    ("ck_entrega_fallida", "Una entrega fallida necesita la incidencia."),
    ("ck_el_motivo", "Cada línea con unidades devueltas necesita su motivo."),
    ("ck_cand_decision_motivo", "La decisión sobre un candidato exige motivo."),
    ("uq_usuario_correo", "Ese correo ya está registrado."),
]


def mensaje_motor(exc):
    texto = str(exc)
    for marca, humano in TRADUCCIONES:
        if marca in texto:
            return humano
    primera = texto.split("CONTEXT:")[0].replace("ERROR:", "").strip()
    if primera.startswith("RN") or "transici" in primera.lower() or "rol" in primera.lower():
        return primera.splitlines()[0]
    return "La base de datos rechazó la operación. Revisa los datos e intenta de nuevo."
