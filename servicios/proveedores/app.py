"""
Servicio de proveedores · puerto 5113 · contrato v1

  GET    /api/v1/proveedores                       proveedores (q, estatus, zona_id, producto_id)
  POST   /api/v1/proveedores                       alta (proveedores.editar)
  GET    /api/v1/proveedores/{id}                  un proveedor con su cobertura y su calificación
  PUT    /api/v1/proveedores/{id}                  modificación (también PATCH)
  DELETE /api/v1/proveedores/{id}                  baja lógica
  GET    /api/v1/proveedores/{id}/catalogo         productos que surte, con precio de compra y capacidad
  PUT    /api/v1/proveedores/{id}/catalogo/{producto_id}   alta o cambio de una oferta
  GET    /api/v1/proveedores/ofertas               ofertas de uno o varios productos, de la más barata a la más cara
  GET    /api/v1/proveedores/{id}/evaluaciones     calificaciones recibidas y su promedio
  POST   /api/v1/proveedores/{id}/evaluaciones     califica puntualidad, calidad y precio (1 a 5)

Responsabilidad única: quién nos surte, qué, a qué precio, en cuánto tiempo y qué tan bien cumple.
No hace compras: abastecimiento consulta las ofertas de aquí para emitir sus órdenes. Los nombres
de los productos se piden al servicio de productos.

Calificación general de un proveedor = promedio de las tres calificaciones (puntualidad, calidad y
precio) de todas sus evaluaciones. Una oferta vencida (vigente_hasta pasada) o de un proveedor dado
de baja no aparece en las ofertas.
"""
import datetime as dt

from flask import g, request

from comun import config
from comun.base import (crear_app, documentar, filtro_entero, filtro_opcion, leer_cuerpo, leer_paginacion, lista,
                        paginacion, requiere, responder, texto_busqueda)
from comun.base_errores import ErrorApi, conflicto, filtro_invalido, invalido, no_encontrado
from comun.clientes import mapa
from comun.datos import conexion, consultar
from comun.formatos import dinero, fecha, numero
from comun.validar import CORREO, Campo, validar

app = crear_app("proveedores", "Microhubs · Proveedores",
                "Proveedores, catálogos mayoristas, ofertas por producto, cobertura y evaluación.", 5113)
P = config.PREFIJO
PATRON_FECHA = r"\d{4}-\d{2}-\d{2}"
CAMPOS_PROVEEDOR = [
    Campo("clave", min_len=2, max_len=20), Campo("nombre", min_len=3, max_len=120),
    Campo("contacto", req=False, nulo=True, max_len=120), Campo("correo", req=False, nulo=True, patron=CORREO, max_len=160,
                                                                  mensaje="Debe ser un correo válido."),
    Campo("telefono", req=False, nulo=True, max_len=20), Campo("dias_entrega", "int", req=False, minimo=0, maximo=60),
    Campo("pedido_minimo", "num", req=False, minimo=0, decimales=2), Campo("condiciones_pago", req=False, nulo=True, max_len=120),
    Campo("zonas", "lista", req=False, nulo=True)]

SQL_PROVEEDOR = (
    "SELECT p.id, p.clave, p.nombre, p.contacto, p.correo, p.telefono, p.dias_entrega, p.pedido_minimo, p.condiciones_pago, "
    "p.estatus::text AS estatus, "
    "COALESCE((SELECT array_agg(z.zona_id ORDER BY z.zona_id) FROM proveedor_zona z WHERE z.proveedor_id = p.id), '{}') AS zonas, "
    "(SELECT count(*) FROM proveedor_evaluacion e WHERE e.proveedor_id = p.id) AS evaluaciones, "
    "(SELECT round(avg((e.puntualidad + e.calidad + e.precio) / 3.0), 1) FROM proveedor_evaluacion e WHERE e.proveedor_id = p.id) AS calificacion "
    "FROM proveedor p ")


def proveedor(f):
    return {"id": f["id"], "clave": f["clave"], "nombre": f["nombre"], "contacto": f["contacto"], "correo": f["correo"],
            "telefono": f["telefono"], "dias_entrega": f["dias_entrega"], "pedido_minimo": dinero(f["pedido_minimo"]),
            "condiciones_pago": f["condiciones_pago"], "estatus": f["estatus"], "zonas": list(f["zonas"]),
            "calificacion": numero(f["calificacion"]), "evaluaciones": f["evaluaciones"]}


def _proveedor(pid):
    f = consultar(SQL_PROVEEDOR + "WHERE p.id = %s", (pid,), una=True)
    if not f:
        raise no_encontrado("No existe ese proveedor.")
    return f


def validar_zonas(zonas):
    campo = [Campo("zona", "int", minimo=1)]
    return sorted({validar({"zona": z}, campo, prefijo=f"zonas[{i}].")["zona"] for i, z in enumerate(zonas)})


def oferta_item(f, prod):
    p = prod.get(f["producto_id"])
    return {"producto": {"id": f["producto_id"], "nombre": p["nombre"] if p else None}, "precio_compra": dinero(f["precio_compra"]),
            "unidad_compra": f["unidad_compra"], "capacidad_semanal": f["capacidad_semanal"], "minimo_compra": f["minimo_compra"],
            "vigente_hasta": f["vigente_hasta"].isoformat() if f["vigente_hasta"] else None}


# --------------------------------------------------------------------
# Proveedores
# --------------------------------------------------------------------
@app.get(f"{P}/proveedores")
@requiere("proveedores.ver")
def proveedores():
    pagina, por, desde = leer_paginacion()
    q, estatus = texto_busqueda(), filtro_opcion("estatus", ["activo", "inactivo"])
    zona, pid = filtro_entero("zona_id"), filtro_entero("producto_id")
    where, args = ["TRUE"], []
    if q:
        where.append("(p.nombre ILIKE %s OR p.clave ILIKE %s)"); args += [f"%{q}%"] * 2
    if estatus:
        where.append("p.estatus = %s"); args.append(estatus)
    if zona:
        where.append("EXISTS (SELECT 1 FROM proveedor_zona z WHERE z.proveedor_id = p.id AND z.zona_id = %s)"); args.append(zona)
    if pid:
        where.append("EXISTS (SELECT 1 FROM proveedor_producto x WHERE x.proveedor_id = p.id AND x.producto_id = %s)"); args.append(pid)
    w = " AND ".join(where)
    total = consultar(f"SELECT count(*) AS n FROM proveedor p WHERE {w}", args, una=True)["n"]
    filas = consultar(SQL_PROVEEDOR + f"WHERE {w} ORDER BY p.clave LIMIT %s OFFSET %s", (*args, por, desde))
    return lista(filas, paginacion(pagina, por, total), "proveedor", "proveedores", proveedor)


@app.post(f"{P}/proveedores")
@requiere("proveedores.editar")
def alta():
    d = validar(leer_cuerpo("proveedor_nuevo"), CAMPOS_PROVEEDOR)
    zonas = validar_zonas(d["zonas"]) if d.get("zonas") else []
    if consultar("SELECT 1 FROM proveedor WHERE clave = %s", (d["clave"],), una=True):
        raise conflicto(f"Ya existe un proveedor con la clave {d['clave']}.")
    with conexion() as con, con.cursor() as cur:
        cur.execute("INSERT INTO proveedor (clave, nombre, contacto, correo, telefono, dias_entrega, pedido_minimo, condiciones_pago) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                    (d["clave"], d["nombre"], d.get("contacto"), d.get("correo"), d.get("telefono"), d.get("dias_entrega", 2),
                     d.get("pedido_minimo", 0), d.get("condiciones_pago")))
        pid = cur.fetchone()["id"]
        for z in zonas:
            cur.execute("INSERT INTO proveedor_zona (proveedor_id, zona_id) VALUES (%s, %s)", (pid, z))
    return responder(proveedor(_proveedor(pid)), 201, raiz="proveedor", items={"zonas": "zona_id"})


@app.get(f"{P}/proveedores/<int:pid>")
@requiere("proveedores.ver")
def uno(pid):
    return responder(proveedor(_proveedor(pid)), raiz="proveedor", items={"zonas": "zona_id"})


@app.route(f"{P}/proveedores/<int:pid>", methods=["PUT", "PATCH"])
@requiere("proveedores.editar")
def modificar(pid):
    campos = [Campo(c.nombre, c.tipo, req=False, minimo=c.minimo, maximo=c.maximo, min_len=c.min_len, max_len=c.max_len,
                    patron=c.patron, nulo=c.nulo, decimales=c.decimales, mensaje=c.mensaje) for c in CAMPOS_PROVEEDOR]
    d = validar(leer_cuerpo("proveedor_cambio"), campos)
    actual = _proveedor(pid)
    if not d:
        raise invalido("cuerpo", "Envía al menos un campo para modificar.")
    if "clave" in d and d["clave"] != actual["clave"]:
        raise conflicto("La clave de un proveedor no se puede cambiar.")
    zonas = validar_zonas(d["zonas"]) if d.get("zonas") else (None if "zonas" not in d else [])
    sets = [(k, d[k]) for k in ("nombre", "contacto", "correo", "telefono", "dias_entrega", "pedido_minimo", "condiciones_pago") if k in d]
    with conexion() as con, con.cursor() as cur:
        if sets:
            cur.execute("UPDATE proveedor SET " + ", ".join(f"{k} = %s" for k, _ in sets) + ", actualizado_en = now() WHERE id = %s",
                        [v for _, v in sets] + [pid])
        if zonas is not None:
            cur.execute("DELETE FROM proveedor_zona WHERE proveedor_id = %s", (pid,))
            for z in zonas:
                cur.execute("INSERT INTO proveedor_zona (proveedor_id, zona_id) VALUES (%s, %s)", (pid, z))
    return responder(proveedor(_proveedor(pid)), raiz="proveedor", items={"zonas": "zona_id"})


@app.delete(f"{P}/proveedores/<int:pid>")
@requiere("proveedores.editar")
def baja(pid):
    with conexion() as con, con.cursor() as cur:
        cur.execute("UPDATE proveedor SET estatus = 'inactivo', actualizado_en = now() WHERE id = %s", (pid,))
        if cur.rowcount == 0:
            raise no_encontrado("No existe ese proveedor.")
    return responder(None, 204)


# --------------------------------------------------------------------
# Catálogo y ofertas
# --------------------------------------------------------------------
@app.get(f"{P}/proveedores/<int:pid>/catalogo")
@requiere("proveedores.ver")
def catalogo(pid):
    _proveedor(pid)
    pagina, por, desde = leer_paginacion()
    total = consultar("SELECT count(*) AS n FROM proveedor_producto WHERE proveedor_id = %s", (pid,), una=True)["n"]
    filas = consultar("SELECT producto_id, precio_compra, unidad_compra, capacidad_semanal, minimo_compra, vigente_hasta "
                      "FROM proveedor_producto WHERE proveedor_id = %s ORDER BY producto_id LIMIT %s OFFSET %s", (pid, por, desde))
    prod = mapa("productos", "productos")
    return lista(filas, paginacion(pagina, por, total), "item", "catalogo", lambda f: oferta_item(f, prod))


@app.put(f"{P}/proveedores/<int:pid>/catalogo/<int:producto_id>")
@requiere("proveedores.editar")
def fijar_oferta(pid, producto_id):
    d = validar(leer_cuerpo("oferta_nueva"), [
        Campo("precio_compra", "num", minimo=0.01, decimales=2), Campo("unidad_compra", req=False, min_len=1, max_len=20),
        Campo("capacidad_semanal", "int", minimo=1, maximo=10000000), Campo("minimo_compra", "int", req=False, minimo=1, maximo=100000),
        Campo("vigente_hasta", req=False, nulo=True, patron=PATRON_FECHA, mensaje="Usa el formato AAAA-MM-DD.")])
    if d.get("vigente_hasta"):
        try:
            dt.date.fromisoformat(d["vigente_hasta"])
        except ValueError:
            raise invalido("vigente_hasta", "Debe ser una fecha AAAA-MM-DD válida.")
    _proveedor(pid)
    with conexion() as con, con.cursor() as cur:
        cur.execute("INSERT INTO proveedor_producto (proveedor_id, producto_id, precio_compra, unidad_compra, capacidad_semanal, "
                    "minimo_compra, vigente_hasta) VALUES (%s,%s,%s,%s,%s,%s,%s) "
                    "ON CONFLICT (proveedor_id, producto_id) DO UPDATE SET precio_compra = EXCLUDED.precio_compra, "
                    "unidad_compra = EXCLUDED.unidad_compra, capacidad_semanal = EXCLUDED.capacidad_semanal, "
                    "minimo_compra = EXCLUDED.minimo_compra, vigente_hasta = EXCLUDED.vigente_hasta, actualizado_en = now() "
                    "RETURNING producto_id, precio_compra, unidad_compra, capacidad_semanal, minimo_compra, vigente_hasta",
                    (pid, producto_id, d["precio_compra"], d.get("unidad_compra", "pieza"), d["capacidad_semanal"],
                     d.get("minimo_compra", 1), d.get("vigente_hasta")))
        fila = cur.fetchone()
    return responder(oferta_item(fila, mapa("productos", "productos")), raiz="item_catalogo")


@app.get(f"{P}/proveedores/ofertas")
@requiere("proveedores.ver", "abastecimiento.ver")
def ofertas():
    pagina, por, desde = leer_paginacion()
    ids = set()
    uno_solo = filtro_entero("producto_id")
    if uno_solo:
        ids.add(uno_solo)
    for t in (request.args.get("producto_ids") or "").split(","):
        if t.strip():
            if not t.strip().isdigit():
                raise filtro_invalido("producto_ids", "producto_ids es una lista de enteros separados por coma.")
            ids.add(int(t))
    if not ids:
        raise filtro_invalido("producto_id", "Indica producto_id o producto_ids.")
    if len(ids) > 100:
        raise filtro_invalido("producto_ids", "Máximo 100 productos por consulta.")
    zona, mejor = filtro_entero("zona_id"), filtro_opcion("mejor", ["true", "false"]) == "true"
    where = ["pr.estatus = 'activo'", "pp.producto_id = ANY(%s)", "(pp.vigente_hasta IS NULL OR pp.vigente_hasta >= fn_hoy())"]
    args = [sorted(ids)]
    if zona:
        where.append("EXISTS (SELECT 1 FROM proveedor_zona z WHERE z.proveedor_id = pr.id AND z.zona_id = %s)"); args.append(zona)
    cal = ("(SELECT round(avg((e.puntualidad + e.calidad + e.precio) / 3.0), 1) FROM proveedor_evaluacion e WHERE e.proveedor_id = pr.id)")
    base = (f"SELECT {'DISTINCT ON (pp.producto_id)' if mejor else ''} pr.id AS proveedor_id, pr.clave, pr.nombre AS proveedor, pp.producto_id, "
            f"pp.precio_compra, pp.unidad_compra, pp.capacidad_semanal, pp.minimo_compra, pr.dias_entrega, pr.pedido_minimo, "
            f"pp.vigente_hasta, {cal} AS calificacion FROM proveedor_producto pp JOIN proveedor pr ON pr.id = pp.proveedor_id "
            f"WHERE {' AND '.join(where)} ORDER BY pp.producto_id, pp.precio_compra, pr.dias_entrega, {cal} DESC NULLS LAST")
    total = consultar(f"SELECT count(*) AS n FROM ({base}) o", args, una=True)["n"]
    filas = consultar(f"SELECT * FROM ({base}) o ORDER BY producto_id, precio_compra, dias_entrega LIMIT %s OFFSET %s", (*args, por, desde))
    prod = mapa("productos", "productos")

    def oferta(f):
        p = prod.get(f["producto_id"])
        return {"proveedor": {"id": f["proveedor_id"], "clave": f["clave"], "nombre": f["proveedor"]},
                "producto": {"id": f["producto_id"], "nombre": p["nombre"] if p else None},
                "precio_compra": dinero(f["precio_compra"]), "unidad_compra": f["unidad_compra"],
                "capacidad_semanal": f["capacidad_semanal"], "minimo_compra": f["minimo_compra"], "dias_entrega": f["dias_entrega"],
                "pedido_minimo": dinero(f["pedido_minimo"]),
                "vigente_hasta": f["vigente_hasta"].isoformat() if f["vigente_hasta"] else None, "calificacion": numero(f["calificacion"])}
    return lista(filas, paginacion(pagina, por, total), "oferta", "ofertas", oferta)


# --------------------------------------------------------------------
# Evaluaciones
# --------------------------------------------------------------------
def evaluacion(f):
    return {"id": f["id"], "proveedor_id": f["proveedor_id"], "puntualidad": f["puntualidad"], "calidad": f["calidad"],
            "precio": f["precio"], "comentario": f["comentario"], "evaluado_por": f["evaluado_por"], "evaluado_en": fecha(f["evaluado_en"])}


@app.get(f"{P}/proveedores/<int:pid>/evaluaciones")
@requiere("proveedores.ver")
def evaluaciones(pid):
    _proveedor(pid)
    pagina, por, desde = leer_paginacion()
    r = consultar("SELECT count(*) AS n, round(avg(puntualidad), 1) AS p, round(avg(calidad), 1) AS c, round(avg(precio), 1) AS pr, "
                  "round(avg((puntualidad + calidad + precio) / 3.0), 1) AS g FROM proveedor_evaluacion WHERE proveedor_id = %s",
                  (pid,), una=True)
    filas = consultar("SELECT id, proveedor_id, puntualidad, calidad, precio, comentario, evaluado_por, evaluado_en "
                      "FROM proveedor_evaluacion WHERE proveedor_id = %s ORDER BY evaluado_en DESC, id DESC LIMIT %s OFFSET %s",
                      (pid, por, desde))
    promedio = ({"puntualidad": numero(r["p"]), "calidad": numero(r["c"]), "precio": numero(r["pr"]), "general": numero(r["g"])}
                if r["n"] else None)
    return responder({"datos": [evaluacion(f) for f in filas], "promedio": promedio, "paginacion": paginacion(pagina, por, r["n"])},
                     raiz="evaluaciones", items={"datos": "evaluacion"})


@app.post(f"{P}/proveedores/<int:pid>/evaluaciones")
@requiere("proveedores.editar", "abastecimiento.recibir")
def evaluar(pid):
    d = validar(leer_cuerpo("evaluacion_nueva"), [
        Campo("puntualidad", "int", minimo=1, maximo=5), Campo("calidad", "int", minimo=1, maximo=5),
        Campo("precio", "int", minimo=1, maximo=5), Campo("comentario", req=False, nulo=True, max_len=300)])
    _proveedor(pid)
    with conexion() as con, con.cursor() as cur:
        cur.execute("INSERT INTO proveedor_evaluacion (proveedor_id, puntualidad, calidad, precio, comentario, evaluado_por) "
                    "VALUES (%s,%s,%s,%s,%s,%s) RETURNING id, proveedor_id, puntualidad, calidad, precio, comentario, evaluado_por, evaluado_en",
                    (pid, d["puntualidad"], d["calidad"], d["precio"], d.get("comentario"), g.usuario["id"]))
        fila = cur.fetchone()
    return responder(evaluacion(fila), 201, raiz="evaluacion")


# --------------------------------------------------------------------
# Documentación
# --------------------------------------------------------------------
PAG = [("pagina", "query", "integer", "Página (1…)"), ("por_pagina", "query", "integer", "1 a 100")]
ID = [("id", "path", "integer", "Id del proveedor")]
documentar(app, "GET", f"{P}/proveedores", "Proveedores", permisos=["proveedores.ver"],
           parametros=PAG + [("q", "query", "string", "Nombre o clave"), ("estatus", "query", "string", "activo | inactivo"),
                             ("zona_id", "query", "integer", "Que cubra esta zona"), ("producto_id", "query", "integer", "Que surta este producto")],
           respuestas={200: ("Página de proveedores", "ProveedorLista.ok")}, errores=[400, 403])
documentar(app, "POST", f"{P}/proveedores", "Dar de alta un proveedor", permisos=["proveedores.editar"], cuerpo="ProveedorNuevo.ok",
           descripcion="La clave no se repite (409). Las zonas son las que cubre.",
           respuestas={201: ("Proveedor creado", "Proveedor.ok")}, errores=[400, 403, 409, 422])
documentar(app, "GET", f"{P}/proveedores/{{id}}", "Un proveedor", permisos=["proveedores.ver"], parametros=ID,
           respuestas={200: ("Proveedor con cobertura y calificación", "Proveedor.ok")}, errores=[403, 404])
documentar(app, "PUT", f"{P}/proveedores/{{id}}", "Modificar un proveedor", permisos=["proveedores.editar"], parametros=ID,
           cuerpo="ProveedorCambio.ok", descripcion="Cualquier subconjunto de campos; si se envía `zonas`, sustituye la cobertura. La clave no cambia.",
           respuestas={200: ("Proveedor actualizado", "Proveedor.ok")}, errores=[400, 403, 404, 409, 422])
documentar(app, "DELETE", f"{P}/proveedores/{{id}}", "Dar de baja un proveedor", permisos=["proveedores.editar"], parametros=ID,
           descripcion="Baja lógica: sigue en la historia, pero ya no aparece en las ofertas.",
           respuestas={204: ("Baja lógica, sin cuerpo", None)}, errores=[403, 404])
documentar(app, "GET", f"{P}/proveedores/{{id}}/catalogo", "Catálogo de un proveedor", permisos=["proveedores.ver"], parametros=ID + PAG,
           respuestas={200: ("Página del catálogo", "CatalogoLista.ok")}, errores=[400, 403, 404])
documentar(app, "PUT", f"{P}/proveedores/{{id}}/catalogo/{{producto_id}}", "Fijar una oferta", permisos=["proveedores.editar"],
           parametros=ID + [("producto_id", "path", "integer", "Id del producto")], cuerpo="OfertaNueva.ok",
           descripcion="Crea la oferta o cambia su precio, capacidad semanal y compra mínima.",
           respuestas={200: ("Renglón del catálogo", "ItemCatalogo.ok")}, errores=[400, 403, 404, 422])
documentar(app, "GET", f"{P}/proveedores/ofertas", "Comparar ofertas", permisos=["proveedores.ver", "abastecimiento.ver"],
           parametros=PAG + [("producto_id", "query", "integer", "Un producto"), ("producto_ids", "query", "string", "Varios, separados por coma (máximo 100)"),
                             ("zona_id", "query", "integer", "Solo proveedores que cubran la zona"),
                             ("mejor", "query", "string", "true: solo la oferta más barata de cada producto")],
           descripcion="De la más barata a la más cara; a igual precio, la de entrega más rápida. Sin ofertas vencidas ni proveedores de baja.",
           respuestas={200: ("Página de ofertas", "OfertaLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/proveedores/{{id}}/evaluaciones", "Evaluaciones de un proveedor", permisos=["proveedores.ver"], parametros=ID + PAG,
           respuestas={200: ("Evaluaciones y promedios", "EvaluacionLista.ok")}, errores=[400, 403, 404])
documentar(app, "POST", f"{P}/proveedores/{{id}}/evaluaciones", "Evaluar a un proveedor", permisos=["proveedores.editar", "abastecimiento.recibir"],
           parametros=ID, cuerpo="EvaluacionNueva.ok", respuestas={201: ("Evaluación registrada", "Evaluacion.ok")}, errores=[400, 403, 404, 422])
