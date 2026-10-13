"""
Servicio de microhubs · puerto 5109 · contrato v1

  GET /api/v1/microhubs[/{id}]   microhubs con coordenadas, radio de cobertura y estatus

Responsabilidad única: la red de microhubs (puntos de servicio). Los productos y las
zonas son otros servicios.

Solo lectura. La lista se guarda en caché de Redis (base 1, cache:catalogo:microhubs:*)
durante `cache_catalogo_segundos` (300 s por omisión).
"""
from comun import config
from comun.base import crear_app, documentar, filtro_opcion, leer_paginacion, paginacion, requiere, responder, texto_busqueda
from comun.base_errores import no_encontrado
from comun.catalogo import con_cache, responder_con_cache
from comun.datos import consultar
from comun.formatos import numero

app = crear_app("microhubs", "Microhubs · Red de microhubs", "Red de microhubs: ubicación, radio de cobertura y estatus (solo lectura, con caché Redis).", 5109)
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


PAG = [("pagina", "query", "integer", "Página (1…)"), ("por_pagina", "query", "integer", "1 a 100"),
       ("q", "query", "string", "Texto a buscar")]
documentar(app, "GET", f"{P}/microhubs", "Lista de microhubs", parametros=PAG + [("estatus", "query", "string", "activo|inactivo")],
           descripcion="Cualquier perfil autenticado. Encabezado X-Cache: HIT si la respuesta vino de Redis.",
           respuestas={200: ("Página de microhubs", "MicrohubLista.ok")}, errores=[400])
documentar(app, "GET", f"{P}/microhubs/{{id}}", "Un microhub", parametros=[("id", "path", "integer", "Id")],
           respuestas={200: ("Microhub", "Microhub.ok")}, errores=[404])
