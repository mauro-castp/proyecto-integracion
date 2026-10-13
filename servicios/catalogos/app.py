"""
Servicio de catálogos · puerto 5103 · contrato v1

  GET /api/v1/productos[/{id}]   productos con categoría (búsqueda q, categoria_id, estatus)
  GET /api/v1/zonas[/{id}]       colonias atendidas con su centroide
  GET /api/v1/microhubs[/{id}]   microhubs con coordenadas y radio

Solo lectura. Las respuestas se guardan en caché de Redis (base 1,
cache:catalogo:*) durante `cache_catalogo_segundos` (tabla configuracion,
300 s por omisión): el catálogo cambia poco y se consulta mucho. Los CRUD
del portal web siguen siendo la única vía de alta y modificación.
"""
import hashlib
import json

import redis
from flask import request

from comun import config
from comun.base import (crear_app, documentar, filtro_entero, filtro_opcion, leer_paginacion, paginacion,
                        requiere, responder, texto_busqueda)
from comun.base_errores import no_encontrado
from comun.datos import consultar, parametro, r_cache
from comun.formatos import dinero, numero

app = crear_app("catalogos", "Microhubs · Catálogos", "Productos, zonas y microhubs (solo lectura, con caché Redis).", 5103)
P = config.PREFIJO


def _cache(recurso, construir):
    """Devuelve (datos, 'HIT'|'MISS'). La llave incluye la consulta completa."""
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


def _responder(datos, raiz, item, estado):
    from decimal import Decimal
    # La caché guarda JSON: los importes regresan como texto y se reconvierten a Decimal para el XML.
    def fijar(p):
        if "precio" in p:
            p["precio"] = Decimal(str(p["precio"])).quantize(Decimal("0.01"))
        return p
    if "datos" in datos:
        datos["datos"] = [fijar(p) for p in datos["datos"]]
        return responder(datos, raiz=raiz, items={"datos": item}, encabezados={"X-Cache": estado})
    return responder(fijar(datos), raiz=item, encabezados={"X-Cache": estado})


# --------------------------------------------------------------------
def producto(f):
    return {"id": f["id"], "clave_interna": f["clave_interna"], "nombre": f["nombre"],
            "categoria": {"id": f["categoria_id"], "nombre": f["categoria"]}, "unidad": f["unidad"],
            "presentacion": f["presentacion"], "precio": dinero(f["precio"]), "imagen_url": f["imagen_url"],
            "estatus": f["estatus"]}


SQL_PRODUCTO = ("SELECT p.id, p.clave_interna, p.nombre, p.categoria_id, c.nombre AS categoria, p.unidad, "
                "p.presentacion, p.precio, p.imagen_url, p.estatus::text AS estatus "
                "FROM producto p JOIN categoria c ON c.id = p.categoria_id ")


@app.get(f"{P}/productos")
@requiere()
def productos():
    pagina, por, desde = leer_paginacion()
    q, cat, est = texto_busqueda(), filtro_entero("categoria_id"), filtro_opcion("estatus", ["activo", "inactivo"])

    def construir():
        where, args = ["TRUE"], []
        if q:
            where.append("(p.nombre ILIKE %s OR p.clave_interna ILIKE %s OR c.nombre ILIKE %s)")
            args += [f"%{q}%"] * 3
        if cat:
            where.append("p.categoria_id = %s"); args.append(cat)
        if est:
            where.append("p.estatus = %s"); args.append(est)
        w = " AND ".join(where)
        total = consultar("SELECT count(*) AS n FROM producto p JOIN categoria c ON c.id = p.categoria_id "
                          f"WHERE {w}", args, una=True)["n"]
        filas = consultar(SQL_PRODUCTO + f"WHERE {w} ORDER BY c.orden, p.nombre LIMIT %s OFFSET %s", (*args, por, desde))
        return {"datos": [producto(f) for f in filas], "paginacion": paginacion(pagina, por, total)}
    datos, estado = _cache("productos", construir)
    return _responder(datos, "productos", "producto", estado)


@app.get(f"{P}/productos/<int:pid>")
@requiere()
def producto_uno(pid):
    def construir():
        f = consultar(SQL_PRODUCTO + "WHERE p.id = %s", (pid,), una=True)
        return producto(f) if f else None
    datos, estado = _cache(f"producto:{pid}", construir)
    if not datos:
        raise no_encontrado()
    return _responder(datos, None, "producto", estado)


# --------------------------------------------------------------------
def zona(f):
    return {"id": f["id"], "clave": f["clave"], "nombre": f["nombre"], "colonia": f["colonia"],
            "codigo_postal": f["codigo_postal"], "latitud": numero(f["centroide_lat"]),
            "longitud": numero(f["centroide_lng"])}


@app.get(f"{P}/zonas")
@requiere()
def zonas():
    pagina, por, desde = leer_paginacion()
    q = texto_busqueda()

    def construir():
        w, args = ("(nombre ILIKE %s OR colonia ILIKE %s OR codigo_postal LIKE %s)", [f"%{q}%"] * 3) if q else ("TRUE", [])
        total = consultar(f"SELECT count(*) AS n FROM zona WHERE {w}", args, una=True)["n"]
        filas = consultar(f"SELECT * FROM zona WHERE {w} ORDER BY clave LIMIT %s OFFSET %s", (*args, por, desde))
        return {"datos": [zona(f) for f in filas], "paginacion": paginacion(pagina, por, total)}
    datos, estado = _cache("zonas", construir)
    return _responder(datos, "zonas", "zona", estado)


@app.get(f"{P}/zonas/<int:zid>")
@requiere()
def zona_una(zid):
    f = consultar("SELECT * FROM zona WHERE id = %s", (zid,), una=True)
    if not f:
        raise no_encontrado()
    return responder(zona(f), raiz="zona")


# --------------------------------------------------------------------
def microhub(f):
    return {"id": f["id"], "clave": f["clave"], "nombre": f["nombre"], "latitud": numero(f["latitud"]),
            "longitud": numero(f["longitud"]), "radio_km": numero(f["radio_km"]), "estatus": f["estatus"]}


@app.get(f"{P}/microhubs")
@requiere()
def microhubs():
    pagina, por, desde = leer_paginacion()
    q, est = texto_busqueda(), filtro_opcion("estatus", ["activo", "inactivo"])

    def construir():
        where, args = ["TRUE"], []
        if q:
            where.append("(nombre ILIKE %s OR clave ILIKE %s)"); args += [f"%{q}%"] * 2
        if est:
            where.append("estatus = %s"); args.append(est)
        w = " AND ".join(where)
        total = consultar(f"SELECT count(*) AS n FROM microhub WHERE {w}", args, una=True)["n"]
        filas = consultar(f"SELECT id, clave, nombre, latitud, longitud, radio_km, estatus::text AS estatus "
                          f"FROM microhub WHERE {w} ORDER BY clave LIMIT %s OFFSET %s", (*args, por, desde))
        return {"datos": [microhub(f) for f in filas], "paginacion": paginacion(pagina, por, total)}
    datos, estado = _cache("microhubs", construir)
    return _responder(datos, "microhubs", "microhub", estado)


@app.get(f"{P}/microhubs/<int:mid>")
@requiere()
def microhub_uno(mid):
    f = consultar("SELECT id, clave, nombre, latitud, longitud, radio_km, estatus::text AS estatus "
                  "FROM microhub WHERE id = %s", (mid,), una=True)
    if not f:
        raise no_encontrado()
    return responder(microhub(f), raiz="microhub")


PAG = [("pagina", "query", "integer", "Página (1…)"), ("por_pagina", "query", "integer", "1 a 100"),
       ("q", "query", "string", "Texto a buscar")]
documentar(app, "GET", f"{P}/productos", "Lista de productos", parametros=PAG + [
           ("categoria_id", "query", "integer", "Filtra por categoría"), ("estatus", "query", "string", "activo|inactivo")],
           descripcion="Cualquier perfil autenticado. Encabezado X-Cache: HIT si la respuesta vino de Redis.",
           respuestas={200: ("Página de productos", "ProductoLista.ok")}, errores=[400])
documentar(app, "GET", f"{P}/productos/{{id}}", "Un producto", parametros=[("id", "path", "integer", "Id")],
           respuestas={200: ("Producto", "Producto.ok")}, errores=[404])
documentar(app, "GET", f"{P}/zonas", "Lista de zonas", parametros=PAG,
           respuestas={200: ("Página de zonas", "ZonaLista.ok")}, errores=[400])
documentar(app, "GET", f"{P}/zonas/{{id}}", "Una zona", parametros=[("id", "path", "integer", "Id")],
           respuestas={200: ("Zona", "Zona.ok")}, errores=[404])
documentar(app, "GET", f"{P}/microhubs", "Lista de microhubs", parametros=PAG + [("estatus", "query", "string", "activo|inactivo")],
           respuestas={200: ("Página de microhubs", "MicrohubLista.ok")}, errores=[400])
documentar(app, "GET", f"{P}/microhubs/{{id}}", "Un microhub", parametros=[("id", "path", "integer", "Id")],
           respuestas={200: ("Microhub", "Microhub.ok")}, errores=[404])
