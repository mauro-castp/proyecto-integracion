"""
Servicio de reportes · puerto 5123 · contrato v1

  GET  /api/v1/reportes                          catálogo: cada reporte con su familia y los filtros que admite
  GET  /api/v1/reportes/indicadores              indicadores clave del periodo (si un servicio no responde, solo falta su indicador)
  GET  /api/v1/reportes/exportaciones            bitácora de exportaciones (cada persona ve las suyas; el administrador y el auditor, todas)
  GET  /api/v1/reportes/{clave}                  el reporte como tabla (columnas, filas y totales)
  GET  /api/v1/reportes/{clave}/grafica          los mismos datos listos para Highcharts (categorías y series)
  GET  /api/v1/reportes/{clave}/exportar         descarga en CSV, Excel (xlsx) o PDF (formato=csv|xlsx|pdf); queda archivado en el bucket
  GET  /api/v1/reportes/exportaciones/{id}/enlace  URL firmada y con caducidad del archivo archivado (quien lo exportó, administrador, auditor)

Familias y reportes
  operativo   pedidos_por_dia, pedidos_por_zona
  logistico   inventario_alertas, quiebres_inventario, carga_repartidores
  comercial   ventas_por_producto, comparacion_microhubs
  financiero  equilibrio_microhubs

Filtros: desde y hasta (AAAA-MM-DD, el periodo por omisión lo da configuracion.rep_periodo_dias), zona_id y microhub_id. Un reporte que no
admite un filtro lo rechaza (400) en lugar de ignorarlo en silencio.

Responsabilidad única: armar, comparar y entregar reportes. No tiene datos propios de negocio: cada reporte se arma con las respuestas de los
servicios dueños (pedidos, inventario, entregas, punto-equilibrio, zonas, productos, microhubs) con el MISMO JWT de quien lo pide, así que
cada servicio aplica el alcance del perfil (un supervisor solo ve su microhub) y los permisos. Su única tabla, reporte_exportacion, guarda
quién exportó qué, con qué filtros y la huella SHA-256 del archivo. Desde la entrega final el archivo además se archiva en el almacén de objetos
(Google Cloud Storage en la nube: reportes/AAAA/MM/<id>.<ext>) y la tabla guarda solo su ruta: nunca el archivo. Si el bucket no responde, la
descarga se entrega igual y la exportación queda sin archivo (X-Reporte-Archivado: no).

Seguridad de las exportaciones: una celda de texto que empieza con = + - @ se neutraliza (inyección de fórmulas en Excel y CSV) y el archivo
trae el SHA-256 en el encabezado X-Reporte-SHA256.
"""
import csv
import datetime as dt
import hashlib
import io

from flask import Response, g, request

from comun import almacen, config, supuestos as sup
from comun.base import (crear_app, documentar, filtro_entero, filtro_fecha, filtro_opcion, leer_paginacion, lista, paginacion, requiere,
                        responder, tiene)
from comun.base_errores import ErrorApi, filtro_invalido
from comun.clientes import exigir, mapa
from comun.datos import ahora, auditar, como_json, conexion, consultar
from comun.formatos import ZONA, fecha

app = crear_app("reportes", "Microhubs · Reportes",
                "Reportes operativos, logísticos, comerciales y financieros con indicadores, gráficas y exportación a CSV, Excel y PDF.",
                5123)
P = config.PREFIJO
DEFECTOS = {"rep_filas_max": 50000.0, "rep_periodo_dias": 30.0}
MAX_DIAS = 366
FAMILIAS = ["operativo", "logistico", "comercial", "financiero"]
FORMATOS = {"csv": "text/csv; charset=utf-8", "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "pdf": "application/pdf"}
TIPOS_COLUMNA = ["texto", "entero", "dinero", "porcentaje", "fecha"]
CLAVES_SUPUESTOS = list(DEFECTOS)


# --------------------------------------------------------------------
# Lógica pura (se prueba sin base de datos ni servicios)
# --------------------------------------------------------------------
def pct(parte, todo):
    """Porcentaje con dos decimales; None si no hay con qué dividir."""
    return round(100.0 * parte / todo, 2) if todo else None


def dividir(a, b):
    return round(a / b, 2) if b else None


def celda(valor, tipo):
    """Valor → texto del contrato. Lo vacío es una cadena vacía (una celda sin dato)."""
    if valor is None:
        return ""
    if isinstance(valor, bool):
        return "sí" if valor else "no"
    if tipo == "entero":
        return str(int(valor))
    if tipo in ("dinero", "porcentaje"):
        return f"{float(valor):.2f}"
    return str(valor)


def neutralizar(texto):
    """Texto que Excel o una hoja de cálculo tomaría como fórmula (= + - @ o tabulador al inicio) se vuelve texto literal."""
    return "'" + texto if texto and texto[0] in ("=", "+", "-", "@", "\t", "\r") else texto


def agrupar_por_dia(filas):
    """Filas de pedidos/resumen (día y zona) → una por día: pedidos, unidades, venta, ticket y no atendidos."""
    dias = {}
    for f in filas:
        d = dias.setdefault(f["fecha"], {"pedidos": 0, "unidades": 0, "venta": 0.0, "no_atendidos": 0})
        d["pedidos"] += f.get("pedidos", 0) or 0
        d["unidades"] += f.get("unidades", 0) or 0
        d["venta"] += float(f.get("venta", 0) or 0)
        d["no_atendidos"] += f.get("no_atendidos", 0) or 0
    return [[dia, d["pedidos"], d["unidades"], round(d["venta"], 2), dividir(d["venta"], d["pedidos"]), d["no_atendidos"]]
            for dia, d in sorted(dias.items())]


def agrupar_por_zona(filas, nombres):
    zonas = {}
    for f in filas:
        z = zonas.setdefault(f["zona_id"], {"pedidos": 0, "unidades": 0, "venta": 0.0, "no_atendidos": 0})
        z["pedidos"] += f.get("pedidos", 0) or 0
        z["unidades"] += f.get("unidades", 0) or 0
        z["venta"] += float(f.get("venta", 0) or 0)
        z["no_atendidos"] += f.get("no_atendidos", 0) or 0
    salida = [[(nombres.get(i) or {}).get("nombre") or f"Zona {i}", z["pedidos"], z["unidades"], round(z["venta"], 2),
               dividir(z["venta"], z["pedidos"]), z["no_atendidos"], pct(z["no_atendidos"], z["pedidos"] + z["no_atendidos"])]
              for i, z in zonas.items()]
    return sorted(salida, key=lambda r: (-r[3], r[0]))


def totales_de(columnas, filas, suma):
    """Fila de totales: suma las columnas indicadas (por posición); el resto queda vacío y la primera dice «Total»."""
    if not filas:
        return None
    t = ["Total"] + [None] * (len(columnas) - 1)
    for i in suma:
        t[i] = round(sum((f[i] or 0) for f in filas), 2)
    return t


def csv_bytes(columnas, filas, totales=None):
    """CSV en UTF-8 con BOM (Excel lo abre bien) y celdas neutralizadas contra inyección de fórmulas."""
    sal = io.StringIO(newline="")
    w = csv.writer(sal, lineterminator="\r\n")
    w.writerow([neutralizar(c["titulo"]) for c in columnas])
    for f in filas + ([totales] if totales else []):
        w.writerow([neutralizar(celda(v, c["tipo"])) for v, c in zip(f, columnas)])
    return b"\xef\xbb\xbf" + sal.getvalue().encode("utf-8")


def xlsx_bytes(titulo, columnas, filas, totales=None):
    from openpyxl import Workbook
    from openpyxl.styles import Font
    wb = Workbook()
    ws = wb.active
    ws.title = "".join(c for c in titulo if c not in "[]:*?/\\")[:31] or "Reporte"
    ws.append([neutralizar(c["titulo"]) for c in columnas])
    for c in ws[1]:
        c.font = Font(bold=True)

    def valor(v, tipo):
        if v is None or v == "":
            return None
        if tipo == "entero":
            return int(v)
        if tipo in ("dinero", "porcentaje"):
            return float(v)
        return neutralizar(str(v)) if not isinstance(v, bool) else celda(v, tipo)
    for f in filas + ([totales] if totales else []):
        ws.append([valor(v, c["tipo"]) for v, c in zip(f, columnas)])
    if totales:
        for c in ws[ws.max_row]:
            c.font = Font(bold=True)
    for i, c in enumerate(columnas, 1):
        ancho = max([len(c["titulo"])] + [len(celda(f[i - 1], c["tipo"])) for f in filas[:200]])
        ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = min(max(ancho + 2, 10), 48)
    ws.freeze_panes = "A2"
    sal = io.BytesIO()
    wb.save(sal)
    return sal.getvalue()


def pdf_bytes(titulo, subtitulo, columnas, filas, totales=None):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    est = getSampleStyleSheet()
    celda_est = est["BodyText"].clone("celda", fontSize=7.5, leading=9)
    sal = io.BytesIO()
    doc = SimpleDocTemplate(sal, pagesize=landscape(A4), leftMargin=1.2 * cm, rightMargin=1.2 * cm, topMargin=1.2 * cm, bottomMargin=1.4 * cm,
                            title=titulo, author="Microhubs · Codex Innovations")
    cuerpo = [[Paragraph(f"<b>{_esc(c['titulo'])}</b>", celda_est) for c in columnas]]
    for f in filas + ([totales] if totales else []):
        cuerpo.append([Paragraph(("<b>%s</b>" if f is totales else "%s") % _esc(celda(v, c["tipo"])), celda_est) for v, c in zip(f, columnas)])
    t = Table(cuerpo, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e6e6e6")), ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                           ("VALIGN", (0, 0), (-1, -1), "TOP"), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f6f6")])]))

    def pie(canvas, d):
        canvas.setFont("Helvetica", 7)
        canvas.drawString(1.2 * cm, 0.8 * cm, "Microhubs · Codex Innovations")
        canvas.drawRightString(landscape(A4)[0] - 1.2 * cm, 0.8 * cm, f"Página {d.page}")
    doc.build([Paragraph(_esc(titulo), est["Title"]), Paragraph(_esc(subtitulo), est["BodyText"]), Spacer(1, 8), t], onFirstPage=pie, onLaterPages=pie)
    return sal.getvalue()


def _esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# --------------------------------------------------------------------
# Datos de los otros servicios
# --------------------------------------------------------------------
def limites():
    return sup.valores(DEFECTOS)


def todas(servicio, ruta, params=None):
    """Todas las filas de un listado paginado de otro servicio. Rechaza lo que pasa de rep_filas_max."""
    tope = int(limites()["rep_filas_max"])
    salida, pagina = [], 1
    while True:
        d = exigir(servicio, "GET", ruta, params={**(params or {}), "pagina": pagina, "por_pagina": 100})
        salida += d.get("datos", [])
        if len(salida) > tope:
            raise ErrorApi(422, "REPORTE_DEMASIADO_GRANDE", f"El reporte pasa de {tope} filas. Acota el periodo, la zona o el microhub.")
        if pagina >= (d.get("paginacion") or {}).get("paginas", 1):
            return salida
        pagina += 1


def filtros_de_la_peticion(admitidos):
    """desde, hasta, zona_id y microhub_id de la petición. Uno que el reporte no admite → 400."""
    for nombre in ("zona_id", "microhub_id"):
        if request.args.get(nombre) and nombre not in admitidos:
            raise filtro_invalido(nombre, f"Este reporte no admite el filtro {nombre}.")
    for nombre in ("desde", "hasta"):
        if request.args.get(nombre) and nombre not in admitidos:
            raise filtro_invalido(nombre, f"Este reporte no depende del periodo: no admite {nombre}.")
    hoy = ahora().astimezone(ZONA).date()
    hasta = filtro_fecha("hasta") or hoy
    desde = filtro_fecha("desde") or hasta - dt.timedelta(days=int(limites()["rep_periodo_dias"]) - 1)
    if desde > hasta:
        raise filtro_invalido("desde", "desde no puede ser posterior a hasta.")
    if (hasta - desde).days + 1 > MAX_DIAS:
        raise filtro_invalido("desde", f"El periodo no puede pasar de {MAX_DIAS} días.")
    return {"desde": desde, "hasta": hasta, "zona_id": filtro_entero("zona_id"), "microhub_id": filtro_entero("microhub_id")}


def _p(f, *claves):
    """Parámetros de consulta para otro servicio: solo los que traen valor."""
    salida = {}
    for k in claves:
        v = f.get(k)
        if v is not None:
            salida[k] = v.isoformat() if isinstance(v, dt.date) else v
    return salida


def _col(clave, titulo, tipo="texto"):
    return {"clave": clave, "titulo": titulo, "tipo": tipo}


# --------------------------------------------------------------------
# Reportes. Cada uno devuelve columnas, filas, totales y cómo graficarlos (x = columna de categorías, y = columnas de series).
# --------------------------------------------------------------------
def r_pedidos_por_dia(f):
    filas = agrupar_por_dia(todas("pedidos", "pedidos/resumen", _p(f, "desde", "hasta", "zona_id", "microhub_id")))
    cols = [_col("fecha", "Día", "fecha"), _col("pedidos", "Pedidos", "entero"), _col("unidades", "Unidades", "entero"), _col("venta", "Venta", "dinero"),
            _col("ticket_promedio", "Ticket promedio", "dinero"), _col("no_atendidos", "Demanda no atendida", "entero")]
    tot = totales_de(cols, filas, [1, 2, 3, 5])
    if tot:
        tot[4] = dividir(tot[3], tot[1])
    return {"columnas": cols, "filas": filas, "totales": tot, "grafica": {"tipo": "line", "x": 0, "y": [1, 3], "unidad": "pedidos / MXN"}}


def r_pedidos_por_zona(f):
    filas = agrupar_por_zona(todas("pedidos", "pedidos/resumen", _p(f, "desde", "hasta", "zona_id", "microhub_id")), mapa("zonas", "zonas"))
    cols = [_col("zona", "Zona"), _col("pedidos", "Pedidos", "entero"), _col("unidades", "Unidades", "entero"), _col("venta", "Venta", "dinero"),
            _col("ticket_promedio", "Ticket promedio", "dinero"), _col("no_atendidos", "Demanda no atendida", "entero"),
            _col("no_atendidos_pct", "No atendida (%)", "porcentaje")]
    tot = totales_de(cols, filas, [1, 2, 3, 5])
    if tot:
        tot[4], tot[6] = dividir(tot[3], tot[1]), pct(tot[5], tot[1] + tot[5])
    return {"columnas": cols, "filas": filas, "totales": tot, "grafica": {"tipo": "column", "x": 0, "y": [1, 5], "unidad": "pedidos"}}


def r_ventas_por_producto(f):
    ventas = todas("pedidos", "pedidos/ventas", _p(f, "desde", "hasta", "microhub_id"))
    nombres = mapa("productos", "productos")
    total = sum(float(v["venta"]) for v in ventas)
    filas = sorted(([v["producto_id"], (nombres.get(v["producto_id"]) or {}).get("nombre") or f"Producto {v['producto_id']}", v["unidades"],
                     round(float(v["venta"]), 2), v["pedidos"], pct(float(v["venta"]), total)] for v in ventas), key=lambda r: (-r[3], r[0]))
    cols = [_col("producto_id", "Id", "entero"), _col("producto", "Producto"), _col("unidades", "Unidades", "entero"), _col("venta", "Venta", "dinero"),
            _col("pedidos", "Pedidos", "entero"), _col("participacion_pct", "Participación (%)", "porcentaje")]
    tot = totales_de(cols, filas, [2, 3])
    if tot:
        tot[0], tot[1] = None, "Total"
    return {"columnas": cols, "filas": filas, "totales": tot, "grafica": {"tipo": "column", "x": 1, "y": [3], "unidad": "MXN", "top": 10}}


def r_comparacion_microhubs(f):
    hubs = mapa("microhubs", "microhubs")
    if f["microhub_id"] and f["microhub_id"] not in hubs:
        raise ErrorApi(404, "NO_ENCONTRADO", "No existe ese microhub.")
    filas = []
    for hid, h in sorted(hubs.items()):
        if f["microhub_id"] and hid != f["microhub_id"]:
            continue
        d = agrupar_por_dia(todas("pedidos", "pedidos/resumen", {**_p(f, "desde", "hasta", "zona_id"), "microhub_id": hid}))
        pedidos, unidades, venta = sum(r[1] for r in d), sum(r[2] for r in d), round(sum(r[3] for r in d), 2)
        filas.append([h.get("nombre") or f"Microhub {hid}", pedidos, unidades, venta, dividir(venta, pedidos), None])
    total_venta = sum(r[3] for r in filas)
    for r in filas:
        r[5] = pct(r[3], total_venta)
    filas.sort(key=lambda r: (-r[3], r[0]))
    cols = [_col("microhub", "Microhub"), _col("pedidos", "Pedidos", "entero"), _col("unidades", "Unidades", "entero"), _col("venta", "Venta", "dinero"),
            _col("ticket_promedio", "Ticket promedio", "dinero"), _col("participacion_venta_pct", "Participación en la venta (%)", "porcentaje")]
    tot = totales_de(cols, filas, [1, 2, 3, 5])
    if tot:
        tot[4] = dividir(tot[3], tot[1])
    return {"columnas": cols, "filas": filas, "totales": tot, "grafica": {"tipo": "column", "x": 0, "y": [1, 3], "unidad": "pedidos / MXN"}}


def r_inventario_alertas(f):
    datos = todas("inventario", "inventario/alertas", _p(f, "microhub_id"))
    filas = [[(a["microhub"] or {}).get("nombre"), (a["producto"] or {}).get("nombre"), a["existencia"], a["minimo"], a["disponible"], a["faltante"],
              a["severidad"]] for a in datos]
    cols = [_col("microhub", "Microhub"), _col("producto", "Producto"), _col("existencia", "Existencia", "entero"), _col("minimo", "Mínimo", "entero"),
            _col("disponible", "Disponible", "entero"), _col("faltante", "Faltante", "entero"), _col("severidad", "Severidad")]
    return {"columnas": cols, "filas": filas, "totales": totales_de(cols, filas, [5]),
            "grafica": {"tipo": "column", "x": 0, "y": [5], "unidad": "unidades faltantes", "agrupar_por_x": True}}


def r_quiebres_inventario(f):
    dias = max(1, min(365, (f["hasta"] - f["desde"]).days + 1))
    datos = todas("inventario", "inventario/quiebres", {**_p(f, "microhub_id"), "dias": dias})
    hubs, prods = mapa("microhubs", "microhubs"), mapa("productos", "productos")
    filas = sorted(([(hubs.get(q["microhub_id"]) or {}).get("nombre") or f"Microhub {q['microhub_id']}",
                     (prods.get(q["producto_id"]) or {}).get("nombre") or f"Producto {q['producto_id']}", q["quiebres"], q["ultimo"], q["agotado_hoy"]]
                    for q in datos), key=lambda r: (-r[2], r[0], r[1]))
    cols = [_col("microhub", "Microhub"), _col("producto", "Producto"), _col("quiebres", "Quiebres", "entero"), _col("ultimo", "Último quiebre"),
            _col("agotado_hoy", "Agotado hoy")]
    return {"columnas": cols, "filas": filas, "totales": totales_de(cols, filas, [2]), "grafica": {"tipo": "column", "x": 1, "y": [2], "unidad": "quiebres", "top": 10}}


def r_carga_repartidores(f):
    datos = todas("entregas", "entregas/repartidores")
    filas = sorted(([r["id"], r["nombre"], r["entregas_abiertas"]] for r in datos), key=lambda r: (-r[2], r[1]))
    cols = [_col("id", "Id", "entero"), _col("repartidor", "Repartidor"), _col("entregas_abiertas", "Entregas abiertas hoy", "entero")]
    tot = totales_de(cols, filas, [2])
    if tot:
        tot[0] = None
    return {"columnas": cols, "filas": filas, "totales": tot, "grafica": {"tipo": "column", "x": 1, "y": [2], "unidad": "entregas"}}


def r_equilibrio_microhubs(f):
    datos = todas("punto-equilibrio", "punto-equilibrio/microhubs", _p(f, "microhub_id"))
    filas = [[(e["microhub"] or {}).get("nombre"), e["costos_fijos_mes"], e["margen_pedido"], e["equilibrio_diario"], e["pedidos_dia"],
              e["diferencia_pedidos_dia"], e["utilidad_mes"], e["decision"]] for e in datos]
    cols = [_col("microhub", "Microhub"), _col("costos_fijos_mes", "Costos fijos del mes", "dinero"), _col("margen_pedido", "Margen por pedido", "dinero"),
            _col("equilibrio_diario", "Equilibrio (pedidos/día)", "dinero"), _col("pedidos_dia", "Pedidos/día esperados", "dinero"),
            _col("diferencia_pedidos_dia", "Diferencia (pedidos/día)", "dinero"), _col("utilidad_mes", "Utilidad del mes", "dinero"), _col("decision", "Decisión")]
    return {"columnas": cols, "filas": filas, "totales": totales_de(cols, filas, [1, 6]), "grafica": {"tipo": "column", "x": 0, "y": [6], "unidad": "MXN"}}


REPORTES = {
    "pedidos_por_dia": ("operativo", "Pedidos por día", "Pedidos, unidades, venta, ticket promedio y demanda no atendida de cada día, sin pedidos cancelados.",
                        ["desde", "hasta", "zona_id", "microhub_id"], r_pedidos_por_dia),
    "pedidos_por_zona": ("operativo", "Pedidos por zona", "Lo mismo agrupado por zona, con el porcentaje de demanda que no se pudo atender.",
                         ["desde", "hasta", "zona_id", "microhub_id"], r_pedidos_por_zona),
    "inventario_alertas": ("logistico", "Alertas de inventario", "Productos agotados o por debajo de su mínimo en cada microhub y cuántas unidades faltan.",
                           ["microhub_id"], r_inventario_alertas),
    "quiebres_inventario": ("logistico", "Quiebres de inventario", "Veces que una salida dejó un producto en cero dentro del periodo.",
                            ["desde", "hasta", "microhub_id"], r_quiebres_inventario),
    "carga_repartidores": ("logistico", "Carga de repartidores", "Repartidores activos y entregas que tienen abiertas hoy.", [], r_carga_repartidores),
    "ventas_por_producto": ("comercial", "Ventas por producto", "Unidades, venta y participación de cada producto en el periodo.",
                            ["desde", "hasta", "microhub_id"], r_ventas_por_producto),
    "comparacion_microhubs": ("comercial", "Comparación entre microhubs", "Pedidos, venta, ticket y participación de cada microhub, lado a lado.",
                              ["desde", "hasta", "zona_id", "microhub_id"], r_comparacion_microhubs),
    "equilibrio_microhubs": ("financiero", "Punto de equilibrio por microhub", "Costos fijos, equilibrio, demanda esperada, utilidad y decisión de cada microhub.",
                             ["microhub_id"], r_equilibrio_microhubs),
}


def armar(clave):
    """Corre el reporte con los filtros de la petición. Devuelve (clave, definición, filtros, resultado)."""
    if clave not in REPORTES:
        raise ErrorApi(404, "NO_ENCONTRADO", "No existe ese reporte.")
    familia, titulo, descripcion, admitidos, fn = REPORTES[clave]
    f = filtros_de_la_peticion(admitidos)
    return familia, titulo, f, fn(f)


def _filtros_json(f):
    return {"desde": f["desde"].isoformat(), "hasta": f["hasta"].isoformat(), "zona_id": f["zona_id"], "microhub_id": f["microhub_id"]}


def _con_celdas(resultado):
    cols = resultado["columnas"]
    filas = [{"celdas": [celda(v, c["tipo"]) for v, c in zip(f, cols)]} for f in resultado["filas"]]
    tot = resultado["totales"]
    return filas, ({"celdas": [celda(v, c["tipo"]) for v, c in zip(tot, cols)]} if tot else None)


# --------------------------------------------------------------------
# Rutas
# --------------------------------------------------------------------
@app.get(f"{P}/reportes")
@requiere("reportes.ver")
def catalogo():
    return responder({"datos": [{"clave": k, "familia": v[0], "titulo": v[1], "descripcion": v[2], "filtros": v[3]} for k, v in REPORTES.items()]},
                     raiz="reportes_catalogo", items={"datos": "reporte", "filtros": "filtro"})


@app.get(f"{P}/reportes/<clave>")
@requiere("reportes.ver")
def reporte(clave):
    familia, titulo, f, r = armar(clave)
    filas, tot = _con_celdas(r)
    return responder({"reporte": clave, "familia": familia, "titulo": titulo, "generado_en": fecha(ahora()), "filtros": _filtros_json(f),
                      "columnas": r["columnas"], "filas": filas, "totales": tot, "total_filas": len(filas)},
                     raiz="reporte", items={"columnas": "columna", "filas": "fila", "celdas": "celda"})


@app.get(f"{P}/reportes/<clave>/grafica")
@requiere("reportes.ver")
def grafica(clave):
    familia, titulo, f, r = armar(clave)
    g_ = r["grafica"]
    filas = r["filas"]
    if g_.get("agrupar_por_x"):                                   # varias filas por categoría: se suman
        suma = {}
        for fila in filas:
            suma[fila[g_["x"]]] = [a + (b or 0) for a, b in zip(suma.get(fila[g_["x"]], [0] * len(g_["y"])), (fila[i] for i in g_["y"]))]
        filas = [[k] + v for k, v in suma.items()]
        g_ = {**g_, "x": 0, "y": list(range(1, len(g_["y"]) + 1))}
    if g_.get("top"):
        filas = filas[:g_["top"]]
    cols = r["columnas"]
    return responder({"reporte": clave, "titulo": titulo, "tipo": g_["tipo"], "unidad": g_["unidad"],
                      "categorias": [celda(fila[g_["x"]], cols[g_["x"]]["tipo"]) for fila in filas],
                      "series": [{"nombre": cols[i]["titulo"], "datos": [float(fila[i] or 0) for fila in filas]} for i in g_["y"]]},
                     raiz="grafica", items={"categorias": "categoria", "series": "serie", "datos": "dato"})


@app.get(f"{P}/reportes/<clave>/exportar")
@requiere("reportes.ver")
def exportar(clave):
    formato = filtro_opcion("formato", list(FORMATOS)) or "csv"
    familia, titulo, f, r = armar(clave)
    cols, filas, tot = r["columnas"], r["filas"], r["totales"]
    subtitulo = (f"Periodo {f['desde']} a {f['hasta']}" + (f" · zona {f['zona_id']}" if f["zona_id"] else "") +
                 (f" · microhub {f['microhub_id']}" if f["microhub_id"] else "") + f" · generado {fecha(ahora())} · {len(filas)} filas")
    if formato == "csv":
        cuerpo = csv_bytes(cols, filas, tot)
    elif formato == "xlsx":
        cuerpo = xlsx_bytes(titulo, cols, filas, tot)
    else:
        cuerpo = pdf_bytes(titulo, subtitulo, cols, filas, tot)
    huella = hashlib.sha256(cuerpo).hexdigest()
    with conexion() as con, con.cursor() as cur:
        cur.execute("INSERT INTO reporte_exportacion (reporte, formato, filtros, filas, bytes, sha256, creado_por) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                    (clave, formato, como_json(_filtros_json(f)), len(filas), len(cuerpo), huella, g.usuario["id"]))
        eid = cur.fetchone()["id"]
    archivado = _archivar(eid, formato, cuerpo, huella)
    nombre = f"{clave}_{f['desde']}_{f['hasta']}.{formato}"
    resp = Response(cuerpo, content_type=FORMATOS[formato])
    resp.headers["Content-Disposition"] = f'attachment; filename="{nombre}"'
    resp.headers["X-Reporte-SHA256"] = huella
    resp.headers["X-Reporte-Filas"] = str(len(filas))
    resp.headers["X-Reporte-Id"] = str(eid)
    resp.headers["X-Reporte-Archivado"] = "si" if archivado else "no"
    return resp


EXTENSION = {"csv": "csv", "xlsx": "xlsx", "pdf": "pdf"}


def _archivar(eid, formato, cuerpo, huella):
    """Guarda el archivo en el almacén (bucket) y su ruta en reporte_exportacion. Si el almacén falla, la descarga sigue."""
    t = dt.datetime.now(dt.timezone.utc)
    ruta = f"reportes/{t:%Y}/{t:%m}/{eid}.{EXTENSION[formato]}"
    alm = almacen.obtener()
    try:
        alm.guardar(ruta, cuerpo, FORMATOS[formato].split(";")[0], huella)
    except almacen.ErrorAlmacen as e:
        print(f'{{"nivel": "WARN", "mensaje": "reporte {eid} sin archivar: {e}"}}', flush=True)
        return False
    with conexion() as con, con.cursor() as cur:
        cur.execute("UPDATE reporte_exportacion SET ruta = %s, almacen = %s WHERE id = %s", (ruta, alm.nombre, eid))
    return True


@app.get(f"{P}/reportes/exportaciones/<int:eid>/enlace")
@requiere("reportes.ver")
def enlace_exportacion(eid):
    """URL firmada (GET, caduca en URL_FIRMADA_SEGUNDOS) del archivo de una exportación. Solo quien la hizo, el administrador o el auditor."""
    f = consultar("SELECT id, reporte, formato, filtros, ruta, creado_por FROM reporte_exportacion WHERE id = %s", (eid,), una=True)
    if not f or (f["creado_por"] != g.usuario["id"] and not (tiene("auditoria.ver") or g.usuario["rol"] == "administrador")):
        raise ErrorApi(404, "NO_ENCONTRADO", "No existe esa exportación.")
    if not f["ruta"]:
        raise ErrorApi(409, "CONFLICTO", "Esa exportación no se archivó (el almacén no respondía al exportar).")
    nombre = f"{f['reporte']}_{f['id']}.{f['formato']}"
    tipo = FORMATOS[f["formato"]].split(";")[0]
    alm = almacen.obtener()
    segundos = config.URL_FIRMADA_SEGUNDOS
    if alm.nombre == "gcs":
        url, expira = alm.url_firmada(f["ruta"], segundos, nombre, tipo)
    else:                                                     # almacén local: el propio servicio sirve la descarga firmada
        expira = int(dt.datetime.now(dt.timezone.utc).timestamp()) + segundos
        from urllib.parse import quote
        url = (request.host_url.rstrip("/") + f"{P}/reportes/descarga?k={quote(f['ruta'], safe='')}&e={expira}&n={quote(nombre, safe='')}"
               f"&t={quote(tipo, safe='')}&s={alm._firma(f['ruta'], expira, nombre, tipo)}")
    auditar("reportes", "descarga", f"Enlace del reporte {f['reporte']} #{eid} (caduca en {segundos} s).", entidad="reporte_exportacion", entidad_id=str(eid))
    return responder({"id": eid, "nombre": nombre, "url_firmada": url, "metodo": "GET", "segundos": segundos,
                      "expira_en": fecha(dt.datetime.fromtimestamp(expira, tz=dt.timezone.utc))}, raiz="exportacion_enlace")


@app.get(f"{P}/reportes/descarga")
def descarga_local():
    """Solo con el almacén local (desarrollo): descarga con la firma HMAC que dio /enlace. En la nube la URL es de Cloud Storage."""
    alm = almacen.obtener()
    a = request.args
    k = a.get("k", "")
    if alm.nombre == "gcs" or not k.startswith("reportes/") or not alm.firma_valida(k, a.get("e"), a.get("n", ""), a.get("t", ""), a.get("s")):
        raise ErrorApi(403, "PROHIBIDO", "El enlace de descarga no es válido o ya caducó.")
    resp = Response(alm.leer(k), content_type=a.get("t") or "application/octet-stream")
    resp.headers["Content-Disposition"] = f"attachment; filename=\"{a.get('n', 'reporte')}\""
    return resp


def _exportacion(f):
    return {"id": f["id"], "reporte": f["reporte"], "formato": f["formato"], "filtros": f["filtros"], "filas": f["filas"], "bytes": f["bytes"],
            "sha256": f["sha256"], "creado_por": {"id": f["creado_por"], "nombre": (f["nombre"] or "").strip() or None} if f["creado_por"] else None,
            "creado_en": fecha(f["creado_en"])}


@app.get(f"{P}/reportes/exportaciones")
@requiere("reportes.ver")
def exportaciones():
    pagina, por, salto = leer_paginacion()
    todas_ = tiene("auditoria.ver") or g.usuario["rol"] == "administrador"
    donde, args = ("", []) if todas_ else (" WHERE e.creado_por = %s", [g.usuario["id"]])
    total = consultar(f"SELECT count(*) AS n FROM reporte_exportacion e{donde}", args, una=True)["n"]
    filas = consultar("SELECT e.id, e.reporte, e.formato, e.filtros, e.filas, e.bytes, e.sha256, e.creado_por, e.creado_en, "
                      "trim(u.nombre || ' ' || COALESCE(u.apellidos, '')) AS nombre FROM reporte_exportacion e "
                      f"LEFT JOIN usuario u ON u.id = e.creado_por{donde} ORDER BY e.creado_en DESC, e.id DESC LIMIT %s OFFSET %s", (*args, por, salto))
    return lista(filas, paginacion(pagina, por, total), "exportacion", "reportes_exportaciones", _exportacion)


@app.get(f"{P}/reportes/indicadores")
@requiere("reportes.ver")
def indicadores():
    f = filtros_de_la_peticion(["desde", "hasta", "zona_id", "microhub_id"])
    caidas, ind = [], []

    def fuente(servicio, fn):
        try:
            return fn()
        except ErrorApi as e:
            if e.status == 403:
                return None                                        # el perfil no ve ese servicio: no es una falla
            if servicio not in caidas:
                caidas.append(servicio)
            return None

    resumen = fuente("pedidos", lambda: todas("pedidos", "pedidos/resumen", _p(f, "desde", "hasta", "zona_id", "microhub_id")))
    if resumen is not None:
        d = agrupar_por_dia(resumen)
        pedidos, venta = sum(r[1] for r in d), round(sum(r[3] for r in d), 2)
        ind += [("pedidos", "Pedidos del periodo", pedidos, "pedidos", "pedidos"), ("venta", "Venta del periodo", venta, "MXN", "pedidos"),
                ("ticket_promedio", "Ticket promedio", dividir(venta, pedidos), "MXN", "pedidos"),
                ("no_atendidos", "Demanda no atendida", sum(r[5] for r in d), "pedidos", "pedidos")]
    alertas = fuente("inventario", lambda: exigir("inventario", "GET", "inventario/alertas", params={**_p(f, "microhub_id"), "por_pagina": 1}))
    if alertas is not None:
        ind.append(("alertas_inventario", "Productos en alerta de inventario", alertas["paginacion"]["total"], "productos", "inventario"))
    reps = fuente("entregas", lambda: exigir("entregas", "GET", "entregas/repartidores", params={"por_pagina": 100}))
    if reps is not None:
        ind += [("repartidores_activos", "Repartidores activos", reps["paginacion"]["total"], "personas", "entregas"),
                ("entregas_abiertas", "Entregas abiertas hoy", sum(r["entregas_abiertas"] for r in reps["datos"]), "entregas", "entregas")]
    eq = fuente("punto-equilibrio", lambda: exigir("punto-equilibrio", "GET", "punto-equilibrio/microhubs", params={**_p(f, "microhub_id"), "por_pagina": 100}))
    if eq is not None:
        ind.append(("microhubs_no_viables", "Microhubs que no alcanzan su equilibrio", sum(1 for e in eq["datos"] if e["decision"] == "no_viable"),
                    "microhubs", "punto-equilibrio"))
    return responder({"desde": f["desde"].isoformat(), "hasta": f["hasta"].isoformat(),
                      "indicadores": [{"clave": c, "titulo": t, "valor": v, "unidad": u, "fuente": s} for c, t, v, u, s in ind],
                      "fuentes_no_disponibles": caidas}, raiz="indicadores", items={"indicadores": "indicador", "fuentes_no_disponibles": "servicio"})


# --------------------------------------------------------------------
# Documentación
# --------------------------------------------------------------------
FILTROS = [("desde", "query", "string", "AAAA-MM-DD (por omisión, hace rep_periodo_dias días)"), ("hasta", "query", "string", "AAAA-MM-DD (por omisión, hoy)"),
           ("zona_id", "query", "integer", "Zona"), ("microhub_id", "query", "integer", "Microhub")]
RUTA_CLAVE = ("clave", "path", "string", "pedidos_por_dia | pedidos_por_zona | inventario_alertas | quiebres_inventario | carga_repartidores | "
              "ventas_por_producto | comparacion_microhubs | equilibrio_microhubs")
documentar(app, "GET", f"{P}/reportes", "Catálogo de reportes", permisos=["reportes.ver"], respuestas={200: ("Reportes, familia y filtros que admite cada uno", "ReportesCatalogo.ok")},
           errores=[403])
documentar(app, "GET", f"{P}/reportes/indicadores", "Indicadores clave del periodo", permisos=["reportes.ver"], parametros=FILTROS,
           descripcion="Si un servicio no responde, solo falta su indicador y el servicio se nombra en `fuentes_no_disponibles`; los demás se entregan.",
           respuestas={200: ("Indicadores", "ReportesIndicadores.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/reportes/{{clave}}", "Un reporte como tabla", permisos=["reportes.ver"], parametros=[RUTA_CLAVE] + FILTROS,
           descripcion="Cada celda es texto en el formato del contrato (los números con punto decimal); una celda sin dato va vacía. Un filtro que el reporte no "
                       "admite responde 400.",
           respuestas={200: ("Columnas, filas y totales", "Reporte.ok")}, errores=[400, 403, 404, 422])
documentar(app, "GET", f"{P}/reportes/{{clave}}/grafica", "Datos listos para Highcharts", permisos=["reportes.ver"], parametros=[RUTA_CLAVE] + FILTROS,
           descripcion="`tipo` es el de Highcharts (column, line); `categorias` va en xAxis.categories y cada elemento de `series` es una serie ({name, data}).",
           respuestas={200: ("Categorías y series", "ReporteGrafica.ok")}, errores=[400, 403, 404, 422])
documentar(app, "GET", f"{P}/reportes/{{clave}}/exportar", "Descargar el reporte (CSV, Excel o PDF)", permisos=["reportes.ver"],
           parametros=[RUTA_CLAVE, ("formato", "query", "string", "csv (por omisión) | xlsx | pdf")] + FILTROS,
           descripcion="Devuelve el archivo (no JSON ni XML) con Content-Disposition; el SHA-256 va en X-Reporte-SHA256. Queda registrado en la bitácora de "
                       "exportaciones y el archivo se archiva en el almacén de objetos (se vuelve a descargar con /reportes/exportaciones/{id}/enlace).",
           respuestas={200: ("El archivo", None)}, errores=[400, 403, 404, 422])
documentar(app, "GET", f"{P}/reportes/exportaciones", "Bitácora de exportaciones", permisos=["reportes.ver"],
           parametros=[("pagina", "query", "integer", "Página"), ("por_pagina", "query", "integer", "1 a 100")],
           descripcion="Cada persona ve sus exportaciones; el administrador y el auditor ven todas.",
           respuestas={200: ("Página de exportaciones", "ReportesExportacionLista.ok")}, errores=[400, 403])
