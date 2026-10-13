"""
catalogo.py — Caché de Redis y formato de respuesta de los servicios de consulta del catálogo
(productos, zonas y microhubs).

Cada uno de esos servicios tiene su propia responsabilidad; solo comparten esta mecánica de
caché (base 1 de Redis, llaves cache:catalogo:*) porque son consultas de lectura que cambian
poco y se piden mucho.
"""
import hashlib
import json
from decimal import Decimal

import redis
from flask import request

from .base import responder
from .datos import parametro, r_cache


def con_cache(recurso, construir):
    """Devuelve (datos, 'HIT'|'MISS'|'SIN_CACHE'). La llave incluye la consulta completa."""
    llave = f"cache:catalogo:{recurso}:" + hashlib.sha1(request.query_string).hexdigest()[:16]
    try:
        guardado = r_cache.get(llave)
        if guardado:
            return json.loads(guardado), "HIT"
    except redis.RedisError:
        return construir(), "SIN_CACHE"
    datos = construir()
    try:
        r_cache.setex(llave, int(parametro("cache_catalogo_segundos", 300)), json.dumps(datos, default=str))
    except redis.RedisError:
        pass
    return datos, "MISS"


def responder_con_cache(datos, raiz, item, estado):
    """Responde una lista (raíz + item) o un registro (item) e informa X-Cache."""
    # La caché guarda JSON: los importes regresan como texto y se reconvierten a Decimal para el XML.
    def fijar(p):
        if "precio" in p:
            p["precio"] = Decimal(str(p["precio"])).quantize(Decimal("0.01"))
        return p
    if "datos" in datos:
        datos["datos"] = [fijar(p) for p in datos["datos"]]
        return responder(datos, raiz=raiz, items={"datos": item}, encabezados={"X-Cache": estado})
    return responder(fijar(datos), raiz=item, encabezados={"X-Cache": estado})
