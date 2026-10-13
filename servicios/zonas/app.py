"""
Servicio de zonas · puerto 5108 · contrato v1

  GET /api/v1/zonas[/{id}]   colonias atendidas con su centroide

Responsabilidad única: las zonas de cobertura geográfica (colonias, código postal y
centroide). Los productos y los microhubs son otros servicios.

Solo lectura. La lista se guarda en caché de Redis (base 1, cache:catalogo:zonas:*)
durante `cache_catalogo_segundos` (300 s por omisión).
"""
from comun import config
from comun.base import crear_app, documentar, leer_paginacion, paginacion, requiere, responder, texto_busqueda
from comun.base_errores import no_encontrado
from comun.catalogo import con_cache, responder_con_cache
from comun.datos import consultar
from comun.formatos import numero

app = crear_app("zonas", "Microhubs · Zonas", "Zonas de cobertura: colonias atendidas con su centroide (solo lectura, con caché Redis).", 5108)
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


PAG = [("pagina", "query", "integer", "Página (1…)"), ("por_pagina", "query", "integer", "1 a 100"),
       ("q", "query", "string", "Texto a buscar")]
documentar(app, "GET", f"{P}/zonas", "Lista de zonas", parametros=PAG,
           descripcion="Cualquier perfil autenticado. Encabezado X-Cache: HIT si la respuesta vino de Redis.",
           respuestas={200: ("Página de zonas", "ZonaLista.ok")}, errores=[400])
documentar(app, "GET", f"{P}/zonas/{{id}}", "Una zona", parametros=[("id", "path", "integer", "Id")],
           respuestas={200: ("Zona", "Zona.ok")}, errores=[404])
