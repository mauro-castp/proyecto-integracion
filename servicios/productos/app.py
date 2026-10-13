"""
Servicio de productos · puerto 5103 · contrato v1

  GET /api/v1/productos[/{id}]   productos con categoría (búsqueda q, categoria_id, estatus)

Responsabilidad única: el catálogo comercial. Las zonas de cobertura y la red de
microhubs son otros servicios (zonas, microhubs).

Solo lectura. Las respuestas se guardan en caché de Redis (base 1,
cache:catalogo:productos:*) durante `cache_catalogo_segundos` (tabla configuracion,
300 s por omisión): el catálogo cambia poco y se consulta mucho. Los CRUD
del portal web siguen siendo la única vía de alta y modificación.
"""
from comun import config
from comun.base import crear_app, documentar, filtro_entero, filtro_opcion, leer_paginacion, paginacion, requiere, texto_busqueda
from comun.base_errores import no_encontrado
from comun.catalogo import con_cache, responder_con_cache
from comun.datos import consultar
from comun.formatos import dinero

app = crear_app("productos", "Microhubs · Productos", "Catálogo comercial de productos con su categoría (solo lectura, con caché Redis).", 5103)
P = config.PREFIJO


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
    datos, estado = con_cache("productos", construir)
    return responder_con_cache(datos, "productos", "producto", estado)


@app.get(f"{P}/productos/<int:pid>")
@requiere()
def producto_uno(pid):
    def construir():
        f = consultar(SQL_PRODUCTO + "WHERE p.id = %s", (pid,), una=True)
        return producto(f) if f else None
    datos, estado = con_cache(f"producto:{pid}", construir)
    if not datos:
        raise no_encontrado()
    return responder_con_cache(datos, None, "producto", estado)


PAG = [("pagina", "query", "integer", "Página (1…)"), ("por_pagina", "query", "integer", "1 a 100"),
       ("q", "query", "string", "Texto a buscar")]
documentar(app, "GET", f"{P}/productos", "Lista de productos", parametros=PAG + [
           ("categoria_id", "query", "integer", "Filtra por categoría"), ("estatus", "query", "string", "activo|inactivo")],
           descripcion="Cualquier perfil autenticado. Encabezado X-Cache: HIT si la respuesta vino de Redis.",
           respuestas={200: ("Página de productos", "ProductoLista.ok")}, errores=[400])
documentar(app, "GET", f"{P}/productos/{{id}}", "Un producto", parametros=[("id", "path", "integer", "Id")],
           respuestas={200: ("Producto", "Producto.ok")}, errores=[404])
