"""
Servicio de precios · puerto 5112 · contrato v1

  GET    /api/v1/precios/listas                      listas de precios (zona_id, estatus, vigente)
  POST   /api/v1/precios/listas                      crea una lista, con sus precios si se envían (precios.editar)
  GET    /api/v1/precios/listas/{id}                 una lista con sus precios y márgenes
  PUT    /api/v1/precios/listas/{id}/items/{producto_id}   fija el precio (y costo) de un producto en la lista
  GET    /api/v1/precios/vigente                     precio que rige hoy para un producto en una zona
  POST   /api/v1/precios/calcular                    precio final de las líneas de un pedido
  GET    /api/v1/precios/promociones                 promociones (estatus, vigente, producto, categoría, zona)
  POST   /api/v1/precios/promociones                 crea una promoción (precios.editar)
  DELETE /api/v1/precios/promociones/{id}            baja lógica de una promoción
  GET    /api/v1/precios/historial                   cambios de precio de las listas
  GET    /api/v1/precios/margenes                    margen de cada precio que tiene costo
  GET    /api/v1/precios/sensibilidad                qué pasa con ingreso y margen si el precio sube o baja

Responsabilidad única: la política de precios. El precio base y la categoría de cada producto se
piden al servicio de productos; este servicio no los modifica.

Cómo se decide el precio de un producto en una zona y fecha:
  1. Precio base: el del catálogo (productos).
  2. Lista de precios: si hay una lista activa y vigente de esa zona (o la general) que lo incluya,
     su precio sustituye al base. La de la zona gana sobre la general.
  3. Promoción: entre las activas, vigentes y de alcance aplicable (producto, categoría o toda la zona)
     se aplica UNA sola, la de mayor descuento; no se acumulan. El descuento no pasa de
     `descuento_maximo_pct` del precio (RN38: ninguna promoción es por persona).
  4. Margen: (precio final − costo) / precio final, si la lista guarda el costo.
"""
import datetime as dt
from decimal import ROUND_HALF_UP, Decimal

from flask import g, request

from comun import config
from comun.base import (crear_app, documentar, filtro_entero, filtro_fecha, filtro_opcion, leer_cuerpo, leer_paginacion,
                        lista, paginacion, requiere, responder)
from comun.base_errores import ErrorApi, conflicto, filtro_invalido, invalido, no_encontrado
from comun.clientes import mapa
from comun.datos import conexion, consultar, parametro
from comun.formatos import ZONA, dinero, fecha
from comun.validar import Campo, validar

app = crear_app("precios", "Microhubs · Precios",
                "Listas de precios por zona, promociones, historial, márgenes y sensibilidad al precio.", 5112)
P = config.PREFIJO
PATRON_FECHA = r"\d{4}-\d{2}-\d{2}"
CENT = Decimal("0.01")


# --------------------------------------------------------------------
# Cálculo (funciones puras, sin bases de datos)
# --------------------------------------------------------------------
def D(valor):
    return Decimal(str(valor))


def redondear(valor):
    return D(valor).quantize(CENT, rounding=ROUND_HALF_UP)


def aplicar_promocion(precio, promociones, maximo_pct):
    """Elige la promoción de mayor descuento (no se acumulan) y limita el descuento al tope.
    Devuelve (descuento, promoción o None, si el tope lo recortó)."""
    precio = D(precio)
    mejor, mejor_d = None, Decimal(0)
    for p in promociones:
        d = precio * D(p["valor"]) / 100 if p["tipo"] == "porcentaje" else D(p["valor"])
        if d > mejor_d:
            mejor, mejor_d = p, d
    tope = precio * D(maximo_pct) / 100
    return redondear(min(mejor_d, tope, precio)), mejor, mejor_d > tope


def margen_pct(precio, costo):
    """Margen bruto como porcentaje del precio, o None si no hay costo."""
    if costo is None or D(precio) <= 0:
        return None
    return float(((D(precio) - D(costo)) / D(precio) * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def sensibilidad(precio, costo, volumen_base, elasticidad, variaciones):
    """Escenarios de precio con una elasticidad supuesta.

    volumen = volumen_base × (1 + elasticidad × variación). Es un supuesto, no una medición: sirve para
    ver el orden de magnitud y para saber cuánto volumen hace falta para no perder margen total."""
    precio, e = D(precio), D(elasticidad)
    ingreso_base = precio * volumen_base
    margen_base = (precio - D(costo)) * volumen_base if costo is not None else None
    filas = []
    for v in variaciones:
        factor = D(v) / 100
        p = precio * (1 + factor)
        vol = max(D(volumen_base) * (1 + e * factor), Decimal(0))
        ingreso = p * vol
        fila = {"variacion_pct": v, "precio": redondear(p), "volumen_estimado": float(vol.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)),
                "ingreso": redondear(ingreso),
                "ingreso_vs_base_pct": float(((ingreso / ingreso_base - 1) * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)),
                "margen_total": None, "volumen_para_igualar_margen": None}
        if costo is not None:
            fila["margen_total"] = redondear((p - D(costo)) * vol)
            if p > D(costo) and margen_base is not None:
                fila["volumen_para_igualar_margen"] = float((margen_base / (p - D(costo))).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))
        filas.append(fila)
    return filas


def fecha_de(valor, campo):
    try:
        return dt.date.fromisoformat(valor)
    except ValueError:
        raise invalido(campo, "Debe ser una fecha AAAA-MM-DD válida.")


def hoy():
    return dt.datetime.now(ZONA).date()


# --------------------------------------------------------------------
# Datos
# --------------------------------------------------------------------
def catalogo():
    """Productos con precio base y categoría; si el servicio de productos no responde, no se puede calcular."""
    prod = mapa("productos", "productos")
    if not prod:
        raise ErrorApi(503, "SERVICIO_NO_DISPONIBLE", "El servicio de productos no responde; sin el precio base no se puede calcular.")
    return prod


def producto_o_404(prod, pid):
    if pid not in prod:
        raise no_encontrado("No existe ese producto.")
    return prod[pid]


def precios_de_lista(pids, zona_id, dia):
    """{producto_id: fila} con el precio de la lista que rige: la de la zona antes que la general."""
    filas = consultar(
        "SELECT DISTINCT ON (i.producto_id) i.producto_id, l.id AS lista_id, l.nombre AS lista, i.precio, i.costo "
        "FROM lista_precio l JOIN lista_precio_item i ON i.lista_id = l.id "
        "WHERE l.estatus = 'activo' AND l.vigente_desde <= %s AND (l.vigente_hasta IS NULL OR l.vigente_hasta >= %s) "
        "AND (l.zona_id IS NULL OR l.zona_id = %s) AND i.producto_id = ANY(%s) "
        "ORDER BY i.producto_id, (l.zona_id IS NULL), l.vigente_desde DESC", (dia, dia, zona_id, list(pids)))
    return {f["producto_id"]: f for f in filas}


def promociones_activas(zona_id, dia):
    return consultar("SELECT id, nombre, tipo, valor, producto_id, categoria_id FROM promocion WHERE estatus = 'activo' "
                     "AND vigente_desde <= %s AND vigente_hasta >= %s AND (zona_id IS NULL OR zona_id = %s)",
                     (dia, dia, zona_id))


def precio_de(prod_info, pid, de_lista, promos, maximo_pct, minimo_margen):
    """Aplica lista, promoción y margen a un producto. Devuelve el renglón de precio completo."""
    base = redondear(prod_info["precio"])
    fila = de_lista.get(pid)
    vigente = redondear(fila["precio"]) if fila else base
    costo = redondear(fila["costo"]) if fila and fila["costo"] is not None else None
    aplicables = [p for p in promos if p["producto_id"] == pid or
                  (p["producto_id"] is None and p["categoria_id"] == prod_info["categoria"]["id"]) or
                  (p["producto_id"] is None and p["categoria_id"] is None)]
    descuento, promo, limitado = aplicar_promocion(vigente, aplicables, maximo_pct)
    final = vigente - descuento
    margen = margen_pct(final, costo)
    return {"precio_base": base, "lista": {"id": fila["lista_id"], "nombre": fila["lista"]} if fila else None,
            "precio_vigente": vigente, "promocion": ({"id": promo["id"], "nombre": promo["nombre"], "tipo": promo["tipo"],
                                                      "valor": dinero(promo["valor"])} if promo and descuento > 0 else None),
            "descuento": descuento, "descuento_limitado": bool(limitado and descuento > 0), "precio_final": final,
            "costo": costo, "margen_pct": margen, "bajo_margen": margen is not None and margen < minimo_margen}


def parametros_precio():
    return int(parametro("descuento_maximo_pct", 30)), int(parametro("margen_minimo_pct", 10))


def vigencia_de(f):
    return {"vigente_desde": f["vigente_desde"].isoformat(), "vigente_hasta": f["vigente_hasta"].isoformat() if f["vigente_hasta"] else None}


def item(f, prod):
    p = prod.get(f["producto_id"])
    return {"producto": {"id": f["producto_id"], "nombre": p["nombre"] if p else None},
            "precio": dinero(f["precio"]), "costo": dinero(f["costo"]), "margen_pct": margen_pct(f["precio"], f["costo"]),
            "actualizado_en": fecha(f["actualizado_en"])}


SQL_LISTA = ("SELECT l.id, l.nombre, l.zona_id, l.vigente_desde, l.vigente_hasta, l.estatus::text AS estatus, "
             "(SELECT count(*) FROM lista_precio_item i WHERE i.lista_id = l.id) AS productos FROM lista_precio l ")


def lista_resumen(f):
    return {"id": f["id"], "nombre": f["nombre"], "zona_id": f["zona_id"], **vigencia_de(f), "estatus": f["estatus"],
            "productos": f["productos"]}


def lista_detalle(lid):
    f = consultar(SQL_LISTA + "WHERE l.id = %s", (lid,), una=True)
    if not f:
        raise no_encontrado("No existe esa lista de precios.")
    items = consultar("SELECT producto_id, precio, costo, actualizado_en FROM lista_precio_item WHERE lista_id = %s "
                      "ORDER BY producto_id LIMIT 500", (lid,))
    prod = mapa("productos", "productos")
    return {**lista_resumen(f), "items": [item(i, prod) for i in items]}


def traslape(cur, zona_id, desde, hasta, excepto=None):
    cur.execute("SELECT id, nombre FROM lista_precio WHERE estatus = 'activo' AND zona_id IS NOT DISTINCT FROM %s "
                "AND daterange(vigente_desde, COALESCE(vigente_hasta, 'infinity'::date), '[]') && "
                "daterange(%s, COALESCE(%s, 'infinity'::date), '[]') AND id <> COALESCE(%s, 0)", (zona_id, desde, hasta, excepto))
    return cur.fetchone()


# --------------------------------------------------------------------
# Listas
# --------------------------------------------------------------------
@app.get(f"{P}/precios/listas")
@requiere("precios.ver")
def listas():
    pagina, por, desde = leer_paginacion()
    zona, estatus = filtro_entero("zona_id"), filtro_opcion("estatus", ["activo", "inactivo"])
    vigente = filtro_opcion("vigente", ["true", "false"])
    where, args = ["TRUE"], []
    if zona:
        where.append("l.zona_id = %s"); args.append(zona)
    if estatus:
        where.append("l.estatus = %s"); args.append(estatus)
    if vigente:
        cond = "l.vigente_desde <= %s AND (l.vigente_hasta IS NULL OR l.vigente_hasta >= %s)"
        where.append(cond if vigente == "true" else f"NOT ({cond})"); args += [hoy(), hoy()]
    w = " AND ".join(where)
    total = consultar(f"SELECT count(*) AS n FROM lista_precio l WHERE {w}", args, una=True)["n"]
    filas = consultar(SQL_LISTA + f"WHERE {w} ORDER BY l.id DESC LIMIT %s OFFSET %s", (*args, por, desde))
    return lista(filas, paginacion(pagina, por, total), "lista", "listas", lista_resumen)


@app.post(f"{P}/precios/listas")
@requiere("precios.editar")
def crear_lista():
    d = validar(leer_cuerpo("lista_nueva"), [
        Campo("nombre", min_len=3, max_len=80), Campo("zona_id", "int", req=False, nulo=True, minimo=1),
        Campo("vigente_desde", req=False, nulo=True, patron=PATRON_FECHA, mensaje="Usa el formato AAAA-MM-DD."),
        Campo("vigente_hasta", req=False, nulo=True, patron=PATRON_FECHA, mensaje="Usa el formato AAAA-MM-DD."),
        Campo("items", "lista", req=False, nulo=True)])
    desde = fecha_de(d["vigente_desde"], "vigente_desde") if d.get("vigente_desde") else hoy()
    hasta = fecha_de(d["vigente_hasta"], "vigente_hasta") if d.get("vigente_hasta") else None
    if hasta and hasta < desde:
        raise invalido("vigente_hasta", "No puede ser anterior a vigente_desde.")
    items = d.get("items") or []
    if len(items) > 500:
        raise invalido("items", "Una lista admite hasta 500 productos por envío.")
    campos = [Campo("producto_id", "int", minimo=1), Campo("precio", "num", minimo=0.01, decimales=2),
              Campo("costo", "num", req=False, nulo=True, minimo=0, decimales=2)]
    filas = []
    for i, it in enumerate(items):
        filas.append(validar(it if isinstance(it, dict) else {}, campos, prefijo=f"items[{i}]."))
    with conexion() as con, con.cursor() as cur:
        cur.execute("SELECT pg_advisory_xact_lock(%s)", (7112,))      # dos altas a la vez no se traslapan
        otra = traslape(cur, d.get("zona_id"), desde, hasta)
        if otra:
            raise conflicto(f"La lista «{otra['nombre']}» ya rige en esa zona durante esas fechas.")
        cur.execute("INSERT INTO lista_precio (nombre, zona_id, vigente_desde, vigente_hasta, creada_por) "
                    "VALUES (%s, %s, %s, %s, %s) RETURNING id", (d["nombre"], d.get("zona_id"), desde, hasta, g.usuario["id"]))
        lid = cur.fetchone()["id"]
        for f in filas:
            cur.execute("INSERT INTO lista_precio_item (lista_id, producto_id, precio, costo, actualizado_por) VALUES (%s,%s,%s,%s,%s)",
                        (lid, f["producto_id"], f["precio"], f.get("costo"), g.usuario["id"]))
    return responder(lista_detalle(lid), 201, raiz="lista_detalle", items={"items": "item"})


@app.get(f"{P}/precios/listas/<int:lid>")
@requiere("precios.ver")
def lista_una(lid):
    return responder(lista_detalle(lid), raiz="lista_detalle", items={"items": "item"})


@app.put(f"{P}/precios/listas/<int:lid>/items/<int:pid>")
@requiere("precios.editar")
def fijar_precio(lid, pid):
    d = validar(leer_cuerpo("precio_nuevo"), [Campo("precio", "num", minimo=0.01, decimales=2),
                                              Campo("costo", "num", req=False, nulo=True, minimo=0, decimales=2)])
    with conexion() as con, con.cursor() as cur:
        cur.execute("SELECT estatus::text AS estatus FROM lista_precio WHERE id = %s FOR UPDATE", (lid,))
        l = cur.fetchone()
        if not l:
            raise no_encontrado("No existe esa lista de precios.")
        if l["estatus"] != "activo":
            raise conflicto("La lista está dada de baja; no se le pueden cambiar precios.")
        cur.execute("INSERT INTO lista_precio_item (lista_id, producto_id, precio, costo, actualizado_por) VALUES (%s,%s,%s,%s,%s) "
                    "ON CONFLICT (lista_id, producto_id) DO UPDATE SET precio = EXCLUDED.precio, "
                    "costo = CASE WHEN %s THEN EXCLUDED.costo ELSE lista_precio_item.costo END, "
                    "actualizado_en = now(), actualizado_por = EXCLUDED.actualizado_por "
                    "RETURNING producto_id, precio, costo, actualizado_en",
                    (lid, pid, d["precio"], d.get("costo"), g.usuario["id"], "costo" in d))
        fila = cur.fetchone()
    return responder(item(fila, mapa("productos", "productos")), raiz="item_precio")


# --------------------------------------------------------------------
# Precio vigente y cálculo
# --------------------------------------------------------------------
def dia_pedido(texto):
    return fecha_de(texto, "fecha") if texto else hoy()


@app.get(f"{P}/precios/vigente")
@requiere("precios.ver", "productos.ver")
def vigente():
    pid, zona = filtro_entero("producto_id"), filtro_entero("zona_id")
    if not pid:
        raise filtro_invalido("producto_id", "producto_id es obligatorio.")
    dia = filtro_fecha("fecha") or hoy()
    prod = catalogo()
    info = producto_o_404(prod, pid)
    maximo, minimo = parametros_precio()
    r = precio_de(info, pid, precios_de_lista([pid], zona, dia), promociones_activas(zona, dia), maximo, minimo)
    return responder({"producto_id": pid, "zona_id": zona, "fecha": dia.isoformat(), **r}, raiz="precio_vigente")


@app.post(f"{P}/precios/calcular")
@requiere("precios.ver", "productos.ver")
def calcular():
    d = validar(leer_cuerpo("calculo_nuevo"), [Campo("zona_id", "int", req=False, nulo=True, minimo=1),
                                               Campo("fecha", req=False, nulo=True, patron=PATRON_FECHA, mensaje="Usa el formato AAAA-MM-DD."),
                                               Campo("lineas", "lista")])
    lineas = d["lineas"]
    if not 1 <= len(lineas) <= 100:
        raise invalido("lineas", "Envía entre 1 y 100 líneas.")
    campos = [Campo("producto_id", "int", minimo=1), Campo("cantidad", "int", minimo=1, maximo=10000)]
    lineas = [validar(l if isinstance(l, dict) else {}, campos, prefijo=f"lineas[{i}].") for i, l in enumerate(lineas)]
    zona, dia = d.get("zona_id"), dia_pedido(d.get("fecha"))
    prod = catalogo()
    for i, l in enumerate(lineas):
        if l["producto_id"] not in prod:
            raise ErrorApi(422, "VALIDACION", "Revisa los datos enviados.",
                           [{"campo": f"lineas[{i}].producto_id", "mensaje": "No existe ese producto."}])
    maximo, minimo = parametros_precio()
    de_lista = precios_de_lista({l["producto_id"] for l in lineas}, zona, dia)
    promos = promociones_activas(zona, dia)
    salida, subtotal, descuento_total = [], Decimal(0), Decimal(0)
    for l in lineas:
        r = precio_de(prod[l["producto_id"]], l["producto_id"], de_lista, promos, maximo, minimo)
        n = l["cantidad"]
        subtotal += r["precio_vigente"] * n
        descuento_total += r["descuento"] * n
        salida.append({"producto_id": l["producto_id"], "cantidad": n, "precio_unitario": r["precio_final"],
                       "descuento_unitario": r["descuento"], "importe": r["precio_final"] * n,
                       "promocion_id": r["promocion"]["id"] if r["promocion"] else None, "bajo_margen": r["bajo_margen"]})
    return responder({"zona_id": zona, "fecha": dia.isoformat(), "lineas": salida, "subtotal": subtotal,
                      "descuento_total": descuento_total, "total": subtotal - descuento_total}, raiz="calculo")


# --------------------------------------------------------------------
# Promociones
# --------------------------------------------------------------------
def promocion(f):
    return {"id": f["id"], "nombre": f["nombre"], "tipo": f["tipo"], "valor": dinero(f["valor"]), "producto_id": f["producto_id"],
            "categoria_id": f["categoria_id"], "zona_id": f["zona_id"], **vigencia_de(f), "estatus": f["estatus"]}


SQL_PROMO = ("SELECT id, nombre, tipo, valor, producto_id, categoria_id, zona_id, vigente_desde, vigente_hasta, "
             "estatus::text AS estatus FROM promocion ")


@app.get(f"{P}/precios/promociones")
@requiere("precios.ver")
def promociones():
    pagina, por, desde = leer_paginacion()
    estatus, vig = filtro_opcion("estatus", ["activo", "inactivo"]), filtro_opcion("vigente", ["true", "false"])
    where, args = ["TRUE"], []
    for cond, valor in (("estatus = %s", estatus), ("producto_id = %s", filtro_entero("producto_id")),
                        ("categoria_id = %s", filtro_entero("categoria_id")), ("zona_id = %s", filtro_entero("zona_id"))):
        if valor:
            where.append(cond); args.append(valor)
    if vig:
        cond = "estatus = 'activo' AND vigente_desde <= %s AND vigente_hasta >= %s"
        where.append(cond if vig == "true" else f"NOT ({cond})"); args += [hoy(), hoy()]
    w = " AND ".join(where)
    total = consultar(f"SELECT count(*) AS n FROM promocion WHERE {w}", args, una=True)["n"]
    filas = consultar(SQL_PROMO + f"WHERE {w} ORDER BY id DESC LIMIT %s OFFSET %s", (*args, por, desde))
    return lista(filas, paginacion(pagina, por, total), "promocion", "promociones", promocion)


@app.post(f"{P}/precios/promociones")
@requiere("precios.editar")
def crear_promocion():
    d = validar(leer_cuerpo("promocion_nueva"), [
        Campo("nombre", min_len=3, max_len=80), Campo("tipo", opciones=["porcentaje", "monto"]),
        Campo("valor", "num", minimo=0.01, decimales=2), Campo("producto_id", "int", req=False, nulo=True, minimo=1),
        Campo("categoria_id", "int", req=False, nulo=True, minimo=1), Campo("zona_id", "int", req=False, nulo=True, minimo=1),
        Campo("vigente_desde", req=False, nulo=True, patron=PATRON_FECHA, mensaje="Usa el formato AAAA-MM-DD."),
        Campo("vigente_hasta", patron=PATRON_FECHA, mensaje="Usa el formato AAAA-MM-DD.")])
    if d.get("producto_id") and d.get("categoria_id"):
        raise invalido("categoria_id", "Una promoción es de un producto o de una categoría, no de las dos cosas.")
    maximo = int(parametro("descuento_maximo_pct", 30))
    if d["tipo"] == "porcentaje" and d["valor"] > maximo:
        raise invalido("valor", f"Un descuento porcentual no puede pasar de {maximo} %.")
    desde = fecha_de(d["vigente_desde"], "vigente_desde") if d.get("vigente_desde") else hoy()
    hasta = fecha_de(d["vigente_hasta"], "vigente_hasta")
    if hasta < desde:
        raise invalido("vigente_hasta", "No puede ser anterior a vigente_desde.")
    with conexion() as con, con.cursor() as cur:
        cur.execute(f"INSERT INTO promocion (nombre, tipo, valor, producto_id, categoria_id, zona_id, vigente_desde, vigente_hasta, creada_por) "
                    f"VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id", (d["nombre"], d["tipo"], d["valor"], d.get("producto_id"),
                                                                          d.get("categoria_id"), d.get("zona_id"), desde, hasta, g.usuario["id"]))
        pid = cur.fetchone()["id"]
    return responder(promocion(consultar(SQL_PROMO + "WHERE id = %s", (pid,), una=True)), 201, raiz="promocion")


@app.delete(f"{P}/precios/promociones/<int:pid>")
@requiere("precios.editar")
def baja_promocion(pid):
    with conexion() as con, con.cursor() as cur:
        cur.execute("UPDATE promocion SET estatus = 'inactivo' WHERE id = %s", (pid,))
        if cur.rowcount == 0:
            raise no_encontrado("No existe esa promoción.")
    return responder(None, 204)


# --------------------------------------------------------------------
# Historial, márgenes y sensibilidad
# --------------------------------------------------------------------
@app.get(f"{P}/precios/historial")
@requiere("precios.ver")
def historial():
    pagina, por, desde = leer_paginacion()
    f_desde, f_hasta = filtro_fecha("desde"), filtro_fecha("hasta")
    if f_desde and f_hasta and f_desde > f_hasta:
        raise ErrorApi(400, "FILTRO_INVALIDO", "desde no puede ser posterior a hasta.")
    where, args = ["TRUE"], []
    for cond, valor in (("producto_id = %s", filtro_entero("producto_id")), ("lista_id = %s", filtro_entero("lista_id"))):
        if valor:
            where.append(cond); args.append(valor)
    if f_desde:
        where.append("fecha >= %s::date"); args.append(f_desde)
    if f_hasta:
        where.append("fecha < %s::date + 1"); args.append(f_hasta)
    w = " AND ".join(where)
    total = consultar(f"SELECT count(*) AS n FROM lista_precio_historico WHERE {w}", args, una=True)["n"]
    filas = consultar(f"SELECT id, lista_id, producto_id, precio_anterior, precio_nuevo, usuario_id, fecha FROM lista_precio_historico "
                      f"WHERE {w} ORDER BY fecha DESC, id DESC LIMIT %s OFFSET %s", (*args, por, desde))
    return lista(filas, paginacion(pagina, por, total), "cambio", "historial_precios",
                 lambda f: {"id": f["id"], "lista_id": f["lista_id"], "producto_id": f["producto_id"],
                            "precio_anterior": dinero(f["precio_anterior"]), "precio_nuevo": dinero(f["precio_nuevo"]),
                            "usuario_id": f["usuario_id"], "fecha": fecha(f["fecha"])})


@app.get(f"{P}/precios/margenes")
@requiere("precios.ver")
def margenes():
    pagina, por, desde = leer_paginacion()
    solo_bajos = filtro_opcion("solo_bajos", ["true", "false"]) == "true"
    minimo = int(parametro("margen_minimo_pct", 10))
    where, args = ["i.costo IS NOT NULL", "l.estatus = 'activo'"], []
    for cond, valor in (("i.lista_id = %s", filtro_entero("lista_id")), ("l.zona_id = %s", filtro_entero("zona_id"))):
        if valor:
            where.append(cond); args.append(valor)
    if solo_bajos:
        where.append("(i.precio - i.costo) * 100 < i.precio * %s"); args.append(minimo)
    w = " AND ".join(where)
    base = f"FROM lista_precio_item i JOIN lista_precio l ON l.id = i.lista_id WHERE {w}"
    total = consultar(f"SELECT count(*) AS n {base}", args, una=True)["n"]
    filas = consultar(f"SELECT i.lista_id, l.nombre AS lista, i.producto_id, i.precio, i.costo {base} "
                      f"ORDER BY (i.precio - i.costo) / i.precio, i.lista_id, i.producto_id LIMIT %s OFFSET %s", (*args, por, desde))
    prod = mapa("productos", "productos")

    def renglon(f):
        m = margen_pct(f["precio"], f["costo"])
        p = prod.get(f["producto_id"])
        return {"lista": {"id": f["lista_id"], "nombre": f["lista"]}, "producto": {"id": f["producto_id"], "nombre": p["nombre"] if p else None},
                "precio": dinero(f["precio"]), "costo": dinero(f["costo"]), "margen_pct": m, "bajo_margen": m < minimo}
    return lista(filas, paginacion(pagina, por, total), "margen", "margenes", renglon)


@app.get(f"{P}/precios/sensibilidad")
@requiere("precios.ver")
def sensibilidad_precio():
    pid, zona = filtro_entero("producto_id"), filtro_entero("zona_id")
    if not pid:
        raise filtro_invalido("producto_id", "producto_id es obligatorio.")
    volumen = filtro_entero("volumen_base")
    volumen = 100 if volumen is None else volumen
    if not 1 <= volumen <= 1000000:
        raise filtro_invalido("volumen_base", "volumen_base debe estar entre 1 y 1,000,000.")
    crudo = (request.args.get("elasticidad") or "").strip()
    try:
        elasticidad = float(crudo) if crudo else float(parametro("elasticidad_precio_defecto", -1.2))
    except ValueError:
        raise filtro_invalido("elasticidad", "elasticidad debe ser un número.")
    if not -10 <= elasticidad <= 0:
        raise filtro_invalido("elasticidad", "elasticidad debe estar entre -10 y 0.")
    variaciones = [int(v) for v in str(parametro("sensibilidad_variaciones", "-20,-10,-5,5,10,20")).split(",") if v.strip()]
    prod = catalogo()
    info = producto_o_404(prod, pid)
    maximo, minimo = parametros_precio()
    dia = hoy()
    r = precio_de(info, pid, precios_de_lista([pid], zona, dia), promociones_activas(zona, dia), maximo, minimo)
    return responder({
        "producto_id": pid, "zona_id": zona, "precio_final": r["precio_final"], "costo": r["costo"], "volumen_base": volumen,
        "elasticidad": elasticidad,
        "supuestos": "La elasticidad es un supuesto, no una medición: indica cuánto cambia el volumen por cada 1 % que cambia el precio. "
                     "El volumen base lo fija quien consulta. Usa los resultados para comparar escenarios, no como pronóstico.",
        "escenarios": sensibilidad(r["precio_final"], r["costo"], volumen, elasticidad, variaciones)},
        raiz="sensibilidad", items={"escenarios": "escenario"})


# --------------------------------------------------------------------
# Documentación
# --------------------------------------------------------------------
PAG = [("pagina", "query", "integer", "Página (1…)"), ("por_pagina", "query", "integer", "1 a 100")]
documentar(app, "GET", f"{P}/precios/listas", "Listas de precios", permisos=["precios.ver"],
           parametros=PAG + [("zona_id", "query", "integer", "Zona"), ("estatus", "query", "string", "activo | inactivo"),
                             ("vigente", "query", "string", "true | false: rige hoy o no")],
           respuestas={200: ("Página de listas", "ListaLista.ok")}, errores=[400, 403])
documentar(app, "POST", f"{P}/precios/listas", "Crear una lista", permisos=["precios.editar"], cuerpo="ListaNueva.ok",
           descripcion="Sin zona_id la lista es general. Una zona no puede tener dos listas activas con fechas que se traslapen (409). "
                       "Si no se indica vigente_desde, rige desde hoy; sin vigente_hasta, no vence.",
           respuestas={201: ("Lista con sus precios", "ListaDetalle.ok")}, errores=[400, 403, 409, 422])
documentar(app, "GET", f"{P}/precios/listas/{{id}}", "Una lista", permisos=["precios.ver"],
           parametros=[("id", "path", "integer", "Id de la lista")],
           respuestas={200: ("Lista con sus precios y márgenes", "ListaDetalle.ok")}, errores=[403, 404])
documentar(app, "PUT", f"{P}/precios/listas/{{id}}/items/{{producto_id}}", "Fijar el precio de un producto", permisos=["precios.editar"],
           parametros=[("id", "path", "integer", "Id de la lista"), ("producto_id", "path", "integer", "Id del producto")],
           cuerpo="PrecioNuevo.ok", descripcion="Crea el renglón o cambia el precio; cada cambio queda en el historial.",
           respuestas={200: ("Renglón de la lista", "ItemPrecio.ok")}, errores=[400, 403, 404, 409, 422])
documentar(app, "GET", f"{P}/precios/vigente", "Precio vigente de un producto", permisos=["precios.ver", "productos.ver"],
           parametros=[("producto_id", "query", "integer", "Producto (obligatorio)"), ("zona_id", "query", "integer", "Zona"),
                       ("fecha", "query", "string", "AAAA-MM-DD; por omisión, hoy")],
           descripcion="Precio base, lista que rige, promoción aplicada, precio final y margen.",
           respuestas={200: ("Precio vigente", "PrecioVigente.ok")}, errores=[400, 403, 404, 503])
documentar(app, "POST", f"{P}/precios/calcular", "Calcular el precio de un pedido", permisos=["precios.ver", "productos.ver"],
           cuerpo="CalculoNuevo.ok", descripcion="Precio final, descuento e importe de cada línea, y los totales.",
           respuestas={200: ("Cálculo", "Calculo.ok")}, errores=[400, 403, 422, 503])
documentar(app, "GET", f"{P}/precios/promociones", "Promociones", permisos=["precios.ver"],
           parametros=PAG + [("estatus", "query", "string", "activo | inactivo"), ("vigente", "query", "string", "true | false"),
                             ("producto_id", "query", "integer", "Producto"), ("categoria_id", "query", "integer", "Categoría"),
                             ("zona_id", "query", "integer", "Zona")],
           respuestas={200: ("Página de promociones", "PromocionLista.ok")}, errores=[400, 403])
documentar(app, "POST", f"{P}/precios/promociones", "Crear una promoción", permisos=["precios.editar"], cuerpo="PromocionNueva.ok",
           descripcion="Sin producto ni categoría aplica a todo el catálogo de la zona (o de todas). No pasa de `descuento_maximo_pct` %.",
           respuestas={201: ("Promoción creada", "Promocion.ok")}, errores=[400, 403, 422])
documentar(app, "DELETE", f"{P}/precios/promociones/{{id}}", "Dar de baja una promoción", permisos=["precios.editar"],
           parametros=[("id", "path", "integer", "Id de la promoción")],
           respuestas={204: ("Baja lógica, sin cuerpo", None)}, errores=[403, 404])
documentar(app, "GET", f"{P}/precios/historial", "Historial de cambios de precio", permisos=["precios.ver"],
           parametros=PAG + [("producto_id", "query", "integer", "Producto"), ("lista_id", "query", "integer", "Lista"),
                             ("desde", "query", "string", "AAAA-MM-DD"), ("hasta", "query", "string", "AAAA-MM-DD")],
           respuestas={200: ("Página de cambios, el más reciente primero", "HistorialLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/precios/margenes", "Márgenes", permisos=["precios.ver"],
           parametros=PAG + [("lista_id", "query", "integer", "Lista"), ("zona_id", "query", "integer", "Zona"),
                             ("solo_bajos", "query", "string", "true: solo los de menos de `margen_minimo_pct` %")],
           descripcion="Solo los renglones que tienen costo. Ordenados del margen más bajo al más alto.",
           respuestas={200: ("Página de márgenes", "MargenLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/precios/sensibilidad", "Sensibilidad al precio", permisos=["precios.ver"],
           parametros=[("producto_id", "query", "integer", "Producto (obligatorio)"), ("zona_id", "query", "integer", "Zona"),
                       ("volumen_base", "query", "integer", "Unidades que se venden hoy (100 por omisión)"),
                       ("elasticidad", "query", "number", "-10 a 0; por omisión la de la configuración (supuesto, no medición)")],
           descripcion="Para cada variación de precio, el volumen estimado, el ingreso, el margen total y las unidades que harían falta "
                       "para igualar el margen actual. La elasticidad es un supuesto que se debe calibrar con ventas reales.",
           respuestas={200: ("Escenarios", "Sensibilidad.ok")}, errores=[400, 403, 404, 503])
