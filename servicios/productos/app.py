"""
Servicio de productos · puerto 5103 · contrato v1

  GET    /api/v1/productos[/{id}]   productos con categoría (búsqueda q, categoria_id, estatus)
  POST   /api/v1/productos          alta (productos.crear)
  PATCH  /api/v1/productos/{id}     cambio; PUT es alias (productos.editar)
  DELETE /api/v1/productos/{id}     baja lógica: queda inactivo y conserva su historia (productos.baja)

Responsabilidad única: el catálogo comercial. Las zonas de cobertura y la red de
microhubs son otros servicios (zonas, microhubs).

Las consultas son para cualquier perfil; altas, cambios y bajas, para quien tiene el permiso. Las respuestas se guardan en caché de Redis (base 1,
cache:catalogo:productos:*) durante `cache_catalogo_segundos` (tabla configuracion,
300 s por omisión): el catálogo cambia poco y se consulta mucho. Cada alta, cambio o baja borra esa caché.
Los cambios quedan en la bitácora (trigger del motor).
"""
from comun import config
from comun.base import (crear_app, documentar, filtro_entero, filtro_opcion, leer_cuerpo, leer_paginacion, paginacion, requiere, responder,
                        texto_busqueda)
from comun.base_errores import invalido, no_encontrado
from comun.catalogo import con_cache, invalidar, responder_con_cache
from comun.datos import conexion, consultar
from comun.validar import Campo, validar
from comun.formatos import dinero

app = crear_app("productos", "Microhubs · Productos", "Catálogo comercial de productos con su categoría, con caché Redis.", 5103)
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


def _campos(req):
    return [Campo("clave_interna", req=req, min_len=1, max_len=30), Campo("nombre", req=req, min_len=1, max_len=160),
            Campo("categoria_id", "int", req=req, minimo=1), Campo("unidad", req=req, min_len=1, max_len=20),
            Campo("presentacion", req=False, nulo=True, max_len=60), Campo("precio", "num", req=req, minimo=0.01, maximo=999999, decimales=2),
            Campo("imagen_url", req=False, nulo=True, max_len=300)]


def _actual(pid):
    return producto(consultar(SQL_PRODUCTO + "WHERE p.id = %s", (pid,), una=True))


@app.post(f"{P}/productos")
@requiere("productos.crear")
def alta():
    d = validar(leer_cuerpo("producto_nuevo"), _campos(True))
    with conexion() as con, con.cursor() as cur:
        cur.execute(f"INSERT INTO producto ({', '.join(d)}) VALUES ({', '.join(['%s'] * len(d))}) RETURNING id", tuple(d.values()))
        pid = cur.fetchone()["id"]
    invalidar("productos", "producto")
    return responder(_actual(pid), 201, raiz="producto")


@app.route(f"{P}/productos/<int:pid>", methods=["PATCH", "PUT"])
@requiere("productos.editar")
def cambio(pid):
    d = validar(leer_cuerpo("producto_cambio"), _campos(False) + [Campo("estatus", req=False, opciones=["activo", "inactivo"])])
    if not d:
        raise invalido("cuerpo", "Indica al menos un campo.")
    with conexion() as con, con.cursor() as cur:
        cur.execute(f"UPDATE producto SET {', '.join(f'{k} = %s' for k in d)}, actualizado_en = now() WHERE id = %s", (*d.values(), pid))
        if cur.rowcount == 0:
            raise no_encontrado()
    invalidar("productos", "producto")
    return responder(_actual(pid), raiz="producto")


@app.delete(f"{P}/productos/<int:pid>")
@requiere("productos.baja")
def baja(pid):
    with conexion() as con, con.cursor() as cur:
        cur.execute("UPDATE producto SET estatus = 'inactivo', actualizado_en = now() WHERE id = %s", (pid,))
        if cur.rowcount == 0:
            raise no_encontrado()
    invalidar("productos", "producto")
    return responder(None, 204)


PAG = [("pagina", "query", "integer", "Página (1…)"), ("por_pagina", "query", "integer", "1 a 100"),
       ("q", "query", "string", "Texto a buscar")]
documentar(app, "GET", f"{P}/productos", "Lista de productos", parametros=PAG + [
           ("categoria_id", "query", "integer", "Filtra por categoría"), ("estatus", "query", "string", "activo|inactivo")],
           descripcion="Cualquier perfil autenticado. Encabezado X-Cache: HIT si la respuesta vino de Redis.",
           respuestas={200: ("Página de productos", "ProductoLista.ok")}, errores=[400])
documentar(app, "GET", f"{P}/productos/{{id}}", "Un producto", parametros=[("id", "path", "integer", "Id")],
           respuestas={200: ("Producto", "Producto.ok")}, errores=[404])
documentar(app, "POST", f"{P}/productos", "Dar de alta un producto", permisos=["productos.crear"], cuerpo="ProductoNuevo.ok",
           respuestas={201: ("Producto creado", "Producto.ok")}, errores=[400, 403, 409, 422])
documentar(app, "PATCH", f"{P}/productos/{{id}}", "Cambiar un producto", permisos=["productos.editar"], cuerpo="ProductoCambio.ok",
           parametros=[("id", "path", "integer", "Id")], descripcion="Solo los campos que se mandan. PUT es alias.",
           respuestas={200: ("Producto actualizado", "Producto.ok")}, errores=[400, 403, 404, 409, 422])
documentar(app, "PUT", f"{P}/productos/{{id}}", "Cambiar un producto (alias de PATCH)", permisos=["productos.editar"], cuerpo="ProductoCambio.ok",
           parametros=[("id", "path", "integer", "Id")], respuestas={200: ("Producto actualizado", "Producto.ok")}, errores=[400, 403, 404, 409, 422])
documentar(app, "DELETE", f"{P}/productos/{{id}}", "Dar de baja un producto", permisos=["productos.baja"], parametros=[("id", "path", "integer", "Id")],
           descripcion="Baja lógica: deja de venderse y conserva sus pedidos.", respuestas={204: ("Baja hecha, sin cuerpo", None)}, errores=[403, 404])
