"""
clientes.py — Llamadas de un microservicio a otro.

Un servicio no lee las tablas de otro para saber algo que no es suyo: se lo pregunta por HTTP.
La llamada lleva el mismo JWT de quien hizo la petición original y el mismo X-Traza-Id, así que
el otro servicio aplica sus permisos y la traza completa queda en los logs de los dos.

  llamar()  una petición; devuelve (status, datos) o responde 503 si el servicio no contesta.
  exigir()  igual, pero un error del otro servicio se vuelve error de este.
  mapa()    un catálogo completo (productos, microhubs…) indexado por id, con caché de Redis,
            para poner nombres a ids sin hacer una llamada por fila.

Las pruebas sustituyen el transporte con usar_transporte() para llamar a los servicios en
proceso, sin red.
"""
import json
import urllib.error
import urllib.parse
import urllib.request

import redis
from flask import g, has_request_context, request

from . import config
from .base_errores import ErrorApi
from .datos import parametro, r_cache

_transporte = {"fn": None}


def usar_transporte(fn):
    """fn(servicio, metodo, ruta, cuerpo, params, token, traza) -> (status, datos). None restaura la red."""
    _transporte["fn"] = fn


def _token_actual():
    if has_request_context():
        cab = request.headers.get("Authorization", "")
        if cab.startswith("Bearer "):
            return cab[7:].strip()
    return None


def llamar(servicio, metodo, ruta, *, cuerpo=None, params=None, token=None, timeout=None):
    """Devuelve (status, datos). Solo falla (503) cuando el servicio no responde."""
    token = token or _token_actual()
    traza = g.get("traza_id") if has_request_context() else None
    if _transporte["fn"]:
        try:
            return _transporte["fn"](servicio, metodo, ruta, cuerpo, params or {}, token, traza)
        except ErrorApi:
            raise
        except Exception:
            raise ErrorApi(503, "SERVICIO_NO_DISPONIBLE", f"El servicio {servicio} no responde. Intenta más tarde.")
    url = config.MICROSERVICIOS_URL.format(servicio=servicio, puerto=config.PUERTOS[servicio]) + config.PREFIJO + "/" + ruta.lstrip("/")
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    enc = {"Accept": "application/json"}
    if token:
        enc["Authorization"] = f"Bearer {token}"
    if traza:
        enc["X-Traza-Id"] = traza
    envio = None
    if cuerpo is not None:
        envio, enc["Content-Type"] = json.dumps(cuerpo, ensure_ascii=False).encode("utf-8"), "application/json"
    req = urllib.request.Request(url, data=envio, headers=enc, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=timeout or config.MICROSERVICIOS_TIEMPO) as r:
            crudo, status = r.read(), r.status
    except urllib.error.HTTPError as e:
        crudo, status = e.read(), e.code
    except (urllib.error.URLError, TimeoutError, OSError):
        raise ErrorApi(503, "SERVICIO_NO_DISPONIBLE", f"El servicio {servicio} no responde. Intenta más tarde.")
    try:
        return status, (json.loads(crudo.decode("utf-8")) if crudo else None)
    except ValueError:
        return status, None


def exigir(servicio, metodo, ruta, *, cuerpo=None, params=None, token=None, ok=(200, 201)):
    """Como llamar(), pero un error del otro servicio se devuelve tal cual (4xx) o como 503 (5xx)."""
    status, datos = llamar(servicio, metodo, ruta, cuerpo=cuerpo, params=params, token=token)
    if status in ok:
        return datos
    err = (datos or {}).get("error") if isinstance(datos, dict) else None
    if status < 500 and err:
        raise ErrorApi(status, err.get("codigo", "ERROR"), err.get("mensaje", "El servicio rechazó la operación."),
                       err.get("detalles"))
    raise ErrorApi(503, "SERVICIO_NO_DISPONIBLE", f"El servicio {servicio} no pudo atender la solicitud.")


def mapa(servicio, ruta, llave="id"):
    """Todos los registros de un listado paginado, indexados por `llave`. Vacío si el servicio no responde."""
    clave = f"cache:mapa:{servicio}:{ruta}"
    try:
        guardado = r_cache.get(clave)
        if guardado:
            return {int(k): v for k, v in json.loads(guardado).items()}
    except redis.RedisError:
        pass
    registros, pagina = {}, 1
    try:
        while pagina <= 20:
            status, datos = llamar(servicio, "GET", ruta, params={"pagina": pagina, "por_pagina": 100})
            if status != 200 or not isinstance(datos, dict):
                return {}
            for r in datos.get("datos", []):
                registros[int(r[llave])] = r
            if pagina >= datos.get("paginacion", {}).get("paginas", 1):
                break
            pagina += 1
    except ErrorApi:
        return {}
    try:
        r_cache.setex(clave, int(parametro("cache_catalogo_segundos", 300)), json.dumps(registros, default=str))
    except Exception:                       # la caché solo acelera: si falla, se responde sin ella
        pass
    return registros
