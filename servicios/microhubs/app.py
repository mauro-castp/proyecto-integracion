"""
Servicio de microhubs · puerto 5109 · contrato v1

  GET /api/v1/microhubs[/{id}]   microhubs con coordenadas, radio de cobertura y estatus

Responsabilidad única: la red de microhubs (puntos de servicio). Los productos y las
zonas son otros servicios.

Solo lectura. La lista se guarda en caché de Redis (base 1, cache:catalogo:microhubs:*)
durante `cache_catalogo_segundos` (300 s por omisión).
"""
from comun import config
from comun.base import (crear_app, documentar, filtro_opcion, leer_cuerpo, leer_paginacion, paginacion, requiere, responder,
                        texto_busqueda)
from comun.base_errores import conflicto, invalido, no_encontrado
from comun.catalogo import con_cache, invalidar, responder_con_cache
from comun.datos import conexion, consultar
from comun.validar import Campo, validar
from comun.formatos import numero

app = crear_app("microhubs", "Microhubs · Red de microhubs", "Red de microhubs: ubicación, radio de cobertura y estatus, con caché Redis.", 5109)
P = config.PREFIJO


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
    datos, estado = con_cache("microhubs", construir)
    return responder_con_cache(datos, "microhubs", "microhub", estado)


@app.get(f"{P}/microhubs/<int:mid>")
@requiere()
def microhub_uno(mid):
    f = consultar("SELECT id, clave, nombre, latitud, longitud, radio_km, estatus::text AS estatus "
                  "FROM microhub WHERE id = %s", (mid,), una=True)
    if not f:
        raise no_encontrado()
    return responder(microhub(f), raiz="microhub")


HORA = r"([01][0-9]|2[0-3]):[0-5][0-9]"


def _campos(req):
    return [Campo("clave", req=req, min_len=1, max_len=20), Campo("nombre", req=req, min_len=1, max_len=120),
            Campo("direccion", req=req, min_len=3, max_len=200),
            Campo("latitud", "num", req=req, minimo=20, maximo=33, decimales=6), Campo("longitud", "num", req=req, minimo=-118, maximo=-86, decimales=6),
            Campo("radio_km", "num", req=False, nulo=True, minimo=0.1, maximo=50, decimales=2),
            Campo("capacidad_turno", "int", req=False, nulo=True, minimo=1, maximo=100000),
            Campo("hora_apertura", req=False, patron=HORA, mensaje="Usa HH:MM."), Campo("hora_cierre", req=False, patron=HORA, mensaje="Usa HH:MM.")]


def _actual(mid):
    return microhub(consultar("SELECT id, clave, nombre, latitud, longitud, radio_km, estatus::text AS estatus FROM microhub WHERE id = %s", (mid,), una=True))


def _sin_pedidos_abiertos(cur, mid):
    cur.execute("SELECT count(*) AS n FROM pedido WHERE microhub_id = %s AND estado IN ('asignado', 'en_preparacion', 'en_ruta')", (mid,))
    n = cur.fetchone()["n"]
    if n:
        raise conflicto(f"El microhub tiene {n} pedidos abiertos: ciérralos o reasígnalos antes de darlo de baja.")


@app.post(f"{P}/microhubs")
@requiere("microhubs.crear")
def alta():
    d = validar(leer_cuerpo("microhub_nuevo"), _campos(True))
    with conexion() as con, con.cursor() as cur:
        cur.execute(f"INSERT INTO microhub ({', '.join(d)}) VALUES ({', '.join(['%s'] * len(d))}) RETURNING id", tuple(d.values()))
        mid = cur.fetchone()["id"]
    invalidar("microhubs", "microhub")
    return responder(_actual(mid), 201, raiz="microhub")


@app.route(f"{P}/microhubs/<int:mid>", methods=["PATCH", "PUT"])
@requiere("microhubs.editar")
def cambio(mid):
    d = validar(leer_cuerpo("microhub_cambio"), _campos(False) + [Campo("estatus", req=False, opciones=["activo", "inactivo"])])
    if not d:
        raise invalido("cuerpo", "Indica al menos un campo.")
    with conexion() as con, con.cursor() as cur:
        if d.get("estatus") == "inactivo":
            _sin_pedidos_abiertos(cur, mid)
        cur.execute(f"UPDATE microhub SET {', '.join(f'{k} = %s' for k in d)}, actualizado_en = now() WHERE id = %s", (*d.values(), mid))
        if cur.rowcount == 0:
            raise no_encontrado()
    invalidar("microhubs", "microhub")
    return responder(_actual(mid), raiz="microhub")


@app.delete(f"{P}/microhubs/<int:mid>")
@requiere("microhubs.baja")
def baja(mid):
    with conexion() as con, con.cursor() as cur:
        _sin_pedidos_abiertos(cur, mid)
        cur.execute("UPDATE microhub SET estatus = 'inactivo', actualizado_en = now() WHERE id = %s", (mid,))
        if cur.rowcount == 0:
            raise no_encontrado()
    invalidar("microhubs", "microhub")
    return responder(None, 204)


PAG = [("pagina", "query", "integer", "Página (1…)"), ("por_pagina", "query", "integer", "1 a 100"),
       ("q", "query", "string", "Texto a buscar")]
documentar(app, "GET", f"{P}/microhubs", "Lista de microhubs", parametros=PAG + [("estatus", "query", "string", "activo|inactivo")],
           descripcion="Cualquier perfil autenticado. Encabezado X-Cache: HIT si la respuesta vino de Redis.",
           respuestas={200: ("Página de microhubs", "MicrohubLista.ok")}, errores=[400])
documentar(app, "GET", f"{P}/microhubs/{{id}}", "Un microhub", parametros=[("id", "path", "integer", "Id")],
           respuestas={200: ("Microhub", "Microhub.ok")}, errores=[404])
documentar(app, "POST", f"{P}/microhubs", "Dar de alta un microhub", permisos=["microhubs.crear"], cuerpo="MicrohubNuevo.ok",
           respuestas={201: ("Microhub creado", "Microhub.ok")}, errores=[400, 403, 409, 422])
documentar(app, "PATCH", f"{P}/microhubs/{{id}}", "Cambiar un microhub", permisos=["microhubs.editar"], cuerpo="MicrohubCambio.ok",
           parametros=[("id", "path", "integer", "Id")], respuestas={200: ("Microhub actualizado", "Microhub.ok")}, errores=[400, 403, 404, 409, 422])
documentar(app, "PUT", f"{P}/microhubs/{{id}}", "Cambiar un microhub (alias de PATCH)", permisos=["microhubs.editar"], cuerpo="MicrohubCambio.ok",
           parametros=[("id", "path", "integer", "Id")], respuestas={200: ("Microhub actualizado", "Microhub.ok")}, errores=[400, 403, 404, 409, 422])
documentar(app, "DELETE", f"{P}/microhubs/{{id}}", "Dar de baja un microhub", permisos=["microhubs.baja"], parametros=[("id", "path", "integer", "Id")],
           descripcion="Con pedidos abiertos responde 409.", respuestas={204: ("Baja hecha, sin cuerpo", None)}, errores=[403, 404, 409])
