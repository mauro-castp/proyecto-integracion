"""
Servicio de zonas · puerto 5108 · contrato v1

  GET /api/v1/zonas[/{id}]   colonias atendidas con su centroide

Responsabilidad única: las zonas de cobertura geográfica (colonias, código postal y
centroide). Los productos y los microhubs son otros servicios.

Solo lectura. La lista se guarda en caché de Redis (base 1, cache:catalogo:zonas:*)
durante `cache_catalogo_segundos` (300 s por omisión).
"""
from comun import config
from comun.base import crear_app, documentar, leer_cuerpo, leer_paginacion, paginacion, requiere, responder, texto_busqueda
from comun.base_errores import invalido, no_encontrado
from comun.catalogo import con_cache, invalidar, responder_con_cache
from comun.datos import conexion, consultar
from comun.validar import Campo, validar
from comun.formatos import numero

app = crear_app("zonas", "Microhubs · Zonas", "Zonas de cobertura: colonias atendidas con su centroide, con caché Redis.", 5108)
P = config.PREFIJO


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
    datos, estado = con_cache("zonas", construir)
    return responder_con_cache(datos, "zonas", "zona", estado)


@app.get(f"{P}/zonas/<int:zid>")
@requiere()
def zona_una(zid):
    f = consultar("SELECT * FROM zona WHERE id = %s", (zid,), una=True)
    if not f:
        raise no_encontrado()
    return responder(zona(f), raiz="zona")


COLUMNAS = {"latitud": "centroide_lat", "longitud": "centroide_lng"}


def _campos(req):
    return [Campo("clave", req=req, min_len=1, max_len=20), Campo("nombre", req=req, min_len=1, max_len=120),
            Campo("colonia", req=req, min_len=1, max_len=120),
            Campo("codigo_postal", req=req, patron=r"[0-9]{5}", mensaje="Debe tener 5 dígitos."),
            Campo("latitud", "num", req=req, minimo=-90, maximo=90, decimales=6), Campo("longitud", "num", req=req, minimo=-180, maximo=180, decimales=6),
            Campo("ticket_minimo", "num", req=False, nulo=True, minimo=0, maximo=99999, decimales=2),
            Campo("costo_envio", "num", req=False, nulo=True, minimo=0, maximo=99999, decimales=2)]


def _actual(zid):
    return zona(consultar("SELECT * FROM zona WHERE id = %s", (zid,), una=True))


@app.post(f"{P}/zonas")
@requiere("zonas.crear")
def alta():
    d = validar(leer_cuerpo("zona_nueva"), _campos(True))
    columnas = [COLUMNAS.get(k, k) for k in d]
    with conexion() as con, con.cursor() as cur:
        cur.execute(f"INSERT INTO zona ({', '.join(columnas)}) VALUES ({', '.join(['%s'] * len(d))}) RETURNING id", tuple(d.values()))
        zid = cur.fetchone()["id"]
    invalidar("zonas", "zona")
    return responder(_actual(zid), 201, raiz="zona")


@app.route(f"{P}/zonas/<int:zid>", methods=["PATCH", "PUT"])
@requiere("zonas.editar")
def cambio(zid):
    d = validar(leer_cuerpo("zona_cambio"), _campos(False) + [Campo("estatus", req=False, opciones=["activo", "inactivo"])])
    if not d:
        raise invalido("cuerpo", "Indica al menos un campo.")
    with conexion() as con, con.cursor() as cur:
        cur.execute(f"UPDATE zona SET {', '.join(f'{COLUMNAS.get(k, k)} = %s' for k in d)}, actualizado_en = now() WHERE id = %s", (*d.values(), zid))
        if cur.rowcount == 0:
            raise no_encontrado()
    invalidar("zonas", "zona")
    return responder(_actual(zid), raiz="zona")


@app.delete(f"{P}/zonas/<int:zid>")
@requiere("zonas.baja")
def baja(zid):
    with conexion() as con, con.cursor() as cur:
        cur.execute("UPDATE zona SET estatus = 'inactivo', actualizado_en = now() WHERE id = %s", (zid,))
        if cur.rowcount == 0:
            raise no_encontrado()
    invalidar("zonas", "zona")
    return responder(None, 204)


PAG = [("pagina", "query", "integer", "Página (1…)"), ("por_pagina", "query", "integer", "1 a 100"),
       ("q", "query", "string", "Texto a buscar")]
documentar(app, "GET", f"{P}/zonas", "Lista de zonas", parametros=PAG,
           descripcion="Cualquier perfil autenticado. Encabezado X-Cache: HIT si la respuesta vino de Redis.",
           respuestas={200: ("Página de zonas", "ZonaLista.ok")}, errores=[400])
documentar(app, "GET", f"{P}/zonas/{{id}}", "Una zona", parametros=[("id", "path", "integer", "Id")],
           respuestas={200: ("Zona", "Zona.ok")}, errores=[404])
documentar(app, "POST", f"{P}/zonas", "Dar de alta una zona", permisos=["zonas.crear"], cuerpo="ZonaNueva.ok",
           respuestas={201: ("Zona creada", "Zona.ok")}, errores=[400, 403, 409, 422])
documentar(app, "PATCH", f"{P}/zonas/{{id}}", "Cambiar una zona", permisos=["zonas.editar"], cuerpo="ZonaCambio.ok", parametros=[("id", "path", "integer", "Id")],
           respuestas={200: ("Zona actualizada", "Zona.ok")}, errores=[400, 403, 404, 409, 422])
documentar(app, "PUT", f"{P}/zonas/{{id}}", "Cambiar una zona (alias de PATCH)", permisos=["zonas.editar"], cuerpo="ZonaCambio.ok",
           parametros=[("id", "path", "integer", "Id")], respuestas={200: ("Zona actualizada", "Zona.ok")}, errores=[400, 403, 404, 409, 422])
documentar(app, "DELETE", f"{P}/zonas/{{id}}", "Dar de baja una zona", permisos=["zonas.baja"], parametros=[("id", "path", "integer", "Id")],
           respuestas={204: ("Baja hecha, sin cuerpo", None)}, errores=[403, 404])
