"""
escenarios_ola2.py — Qué pasa con las conclusiones cuando cambian los supuestos.

Cada modelo de la Ola 2 descansa en supuestos (velocidad del reparto, rodeo de las calles, productividad del personal, costo por
kilómetro, penetración de la demanda, ausentismo…). Este script cambia uno a la vez en la tabla `configuracion`, vuelve a pedir el
resultado al servicio que lo usa y anota si la conclusión cambia. Al terminar deja cada valor como estaba.

  python pruebas/escenarios_ola2.py --salida /salida          (con los servicios arriba; escribe escenarios.md)

El resultado no dice cuál supuesto es el cierto: dice a cuáles es sensible cada decisión, que es lo que hay que medir primero.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("LOG_STDOUT", "0")

from comun import datos as bd  # noqa: E402

PUERTOS = {"auth": 5101, "pedidos": 5104, "entregas": 5105, "demanda": 5115, "cobertura": 5116, "capacidad": 5117, "rutas": 5118, "costos": 5119,
           "punto-equilibrio": 5120, "simulacion": 5121, "surtido": 5122}
PLANTILLA = os.environ.get("MICROSERVICIOS_URL", "http://{servicio}:{puerto}")
CLAVE = os.environ.get("MICROHUBS_CLAVE", "Codex#2026")
TOKEN = {}


def http(servicio, metodo, ruta, cuerpo=None, params=None):
    url = PLANTILLA.format(servicio=servicio, puerto=PUERTOS[servicio]) + "/api/v1/" + ruta
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    enc = {"Accept": "application/json", "Content-Type": "application/json"}
    if TOKEN.get("t"):
        enc["Authorization"] = f"Bearer {TOKEN['t']}"
    req = urllib.request.Request(url, data=json.dumps(cuerpo).encode() if cuerpo is not None else None, headers=enc, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read() or "null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or "null")


def pedir(servicio, ruta, **params):
    st, d = http(servicio, "GET", ruta, params=params or None)
    if st != 200:
        raise SystemExit(f"{servicio}/{ruta} respondió {st}: {d}")
    return d


def configuracion(clave):
    return float(bd.consultar("SELECT valor FROM configuracion WHERE clave = %s AND ambito = 'global'", (clave,), una=True)["valor"])


def fijar(clave, valor):
    with bd.conexion() as con, con.cursor() as cur:
        cur.execute("UPDATE configuracion SET valor = %s WHERE clave = %s AND ambito = 'global'", (str(valor), clave))


class Barrido:
    """Cambia una clave de configuración por una lista de valores y la deja como estaba."""

    def __init__(self, clave):
        self.clave, self.original = clave, configuracion(clave)

    def corre(self, valores):
        try:
            for v in valores:
                fijar(self.clave, v)
                yield v
        finally:
            fijar(self.clave, int(self.original) if self.original == int(self.original) else self.original)


def tabla(encabezados, filas):
    t = ["| " + " | ".join(encabezados) + " |", "|" + "---|" * len(encabezados)]
    t += ["| " + " | ".join("no existe" if c is None else str(c) for c in f) + " |" for f in filas]
    return "\n".join(t)


def marca(valor, original):
    return f"**{valor:g}** (vigente)" if valor == original else f"{valor:g}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--salida", default="/tmp/escenarios")
    a = ap.parse_args()
    st, d = http("auth", "POST", "auth/login", {"correo": "admin@codex.mx", "clave": CLAVE, "dispositivo": "escenarios"})
    TOKEN["t"] = d["token_acceso"]
    hub1 = bd.consultar("SELECT id FROM microhub WHERE clave = 'MH-01'", una=True)["id"]
    out = ["# Escenarios: qué cambia cuando cambia un supuesto", "",
           f"Corrida del {time.strftime('%Y-%m-%d %H:%M')} contra los servicios desplegados. Cada bloque cambia **un** supuesto de la tabla `configuracion`, "
           "pide de nuevo el resultado y lo deja como estaba. En negritas, el valor vigente. De dónde sale cada supuesto y cómo se calibra: "
           "`GET /<servicio>/supuestos` y [`SUPUESTOS.md`](../../servicios/SUPUESTOS.md).", ""]

    # ---------------- Cobertura ----------------
    out += ["## Cobertura (servicio cobertura)", "",
            "La cobertura se decide por el radio en línea recta (igual que `fn_cubre`); el rodeo de las calles y la velocidad solo estiman el **tiempo**. "
            "Lo que se juega es si el tiempo promedio cabe en la promesa de entrega (`cob_tiempo_max_min`).", ""]
    filas = []
    b = Barrido("factor_rodeo_distancia")
    for v in b.corre([1.0, 1.2, 1.3, 1.5, 1.8, 2.2]):
        r = pedir("cobertura", "cobertura/resumen")
        filas.append([marca(v, b.original), f"{r['pct_hogares']} %", r["tiempo_promedio_min"], f"{r['dentro_promesa_pct']} %"])
    out += ["### Rodeo de las calles (distancia por calle ÷ distancia en línea recta)", "", tabla(["factor_rodeo_distancia", "Hogares cubiertos", "Minutos promedio", "Dentro de la promesa"], filas), ""]
    filas = []
    b = Barrido("velocidad_reparto_kmh")
    for v in b.corre([10, 15, 18, 22, 28, 35]):
        r = pedir("cobertura", "cobertura/resumen")
        filas.append([marca(v, b.original), f"{r['pct_hogares']} %", r["tiempo_promedio_min"], f"{r['dentro_promesa_pct']} %"])
    out += ["### Velocidad del reparto", "", tabla(["velocidad_reparto_kmh", "Hogares cubiertos", "Minutos promedio", "Dentro de la promesa"], filas), ""]
    e = pedir("cobertura", "cobertura/escenarios", radios="0.5,1,1.5,2,2.5,3", rodeos="1.3")
    out += ["### Radio de cobertura de cada microhub", "", tabla(["Radio (km)", "Zonas cubiertas", "Hogares cubiertos", "Minutos promedio"],
                                                                [[f["radio_km"], f"{f['pct_zonas']} %", f"{f['pct_hogares']} %", f["tiempo_promedio_min"]] for f in e["filas"]]), ""]

    # ---------------- Capacidad ----------------
    out += ["## Capacidad (servicio capacidad)", "",
            "Con el personal real del microhub 1 y una carga de 60 pedidos al día: ¿en qué nivel queda y cuál es el cuello de botella?", ""]
    for clave, valores in (("picking_pedidos_hora", [6, 8, 10, 12, 15]), ("packing_pedidos_hora", [10, 15, 20, 25, 30]), ("horas_turno", [6, 8, 10, 12])):
        filas = []
        b = Barrido(clave)
        for v in b.corre(valores):
            r = pedir("capacidad", f"capacidad/microhubs/{hub1}", carga_dia=60)
            filas.append([marca(v, b.original), r["capacidad_dia"], f"{r['utilizacion_pct']} %", r["nivel"], r["cuello_botella"], r["operadores_requeridos"]])
        out += [f"### {clave}", "", tabla([clave, "Capacidad al día", "Utilización", "Nivel", "Cuello de botella", "Operadores para 85 %"], filas), ""]
    filas = []
    b = Barrido("cap_factor_pico")
    for v in b.corre([1.0, 1.2, 1.35, 1.6, 2.0]):
        r = pedir("capacidad", f"capacidad/microhubs/{hub1}", carga_dia=60)
        filas.append([marca(v, b.original), f"{r['utilizacion_pct']} %", f"{r['utilizacion_pico_pct']} %", r["nivel_pico"]])
    out += ["### Factor de la hora pico", "", tabla(["cap_factor_pico", "Utilización promedio", "Utilización en la hora pico", "Nivel en la hora pico"], filas), ""]

    # ---------------- Costos y punto de equilibrio ----------------
    out += ["## Costos y punto de equilibrio (servicios costos y punto-equilibrio)", "",
            "Microhub 1 con 1,500 pedidos al mes: costo por pedido y utilidad mensual al cambiar lo que cuesta repartir.", ""]
    for nombre, valores in (("Combustible y desgaste", [3.0, 4.5, 6.0, 8.0]), ("Pago base al repartidor", [12, 18, 24, 30])):
        filas = []
        concepto = bd.consultar("SELECT id, monto FROM costo_concepto WHERE ambito = 'global' AND nombre = %s", (nombre,), una=True)
        original = float(concepto["monto"])
        try:
            for v in valores:
                with bd.conexion() as con, con.cursor() as cur:
                    cur.execute("UPDATE costo_concepto SET monto = %s WHERE id = %s", (v, concepto["id"]))
                u = pedir("costos", "costos/unitarios", microhub_id=hub1, pedidos_mes=1500)
                r = pedir("costos", "costos/rentabilidad", microhub_id=hub1, pedidos_mes=1500)
                filas.append([marca(v, original), u["costo_entrega"], r["costo_por_pedido"], f"{r['utilidad_mes']:,.0f}", "sí" if r["cubre_costos"] else "no"])
        finally:
            with bd.conexion() as con, con.cursor() as cur:
                cur.execute("UPDATE costo_concepto SET monto = %s WHERE id = %s", (original, concepto["id"]))
        out += [f"### Concepto «{nombre}» (servicio costos)", "", tabla(["Monto", "Costo de entrega", "Costo por pedido", "Utilidad del mes", "Cubre costos"], filas), ""]
    filas = []
    b = Barrido("paradas_por_viaje")
    for v in b.corre([1, 2, 3, 4, 6]):
        u = pedir("costos", "costos/unitarios", microhub_id=hub1, pedidos_mes=1500)
        r = pedir("costos", "costos/rentabilidad", microhub_id=hub1, pedidos_mes=1500)
        filas.append([marca(v, b.original), u["costo_entrega"], r["costo_por_pedido"], f"{r['utilidad_mes']:,.0f}", "sí" if r["cubre_costos"] else "no"])
    out += ["### paradas_por_viaje (reparte el regreso al microhub entre las paradas del viaje)", "", tabla(["paradas_por_viaje", "Costo de entrega", "Costo por pedido", "Utilidad del mes", "Cubre costos"], filas), ""]
    filas = []
    b = Barrido("margen_bruto_default")
    for v in b.corre([0.18, 0.22, 0.28, 0.32, 0.36, 0.40]):
        r = http("punto-equilibrio", "POST", "punto-equilibrio/calculos", {"microhub_id": hub1})[1]
        filas.append([marca(v, b.original), r["entrada"]["pedidos_dia"], r["equilibrio_diario"], r["margen_seguridad_pct"], r["decision"]])
    out += ["### Margen bruto sobre la venta (cuando no se conoce el costo del producto)", "",
            tabla(["margen_bruto_default", "Pedidos al día esperados", "Equilibrio diario", "Margen de seguridad %", "Decisión"], filas), ""]
    filas = []
    for ticket in (110, 130, 150, 170, 200):
        fila = [ticket]
        for mb in (0.22, 0.28, 0.34, 0.40):
            r = http("punto-equilibrio", "POST", "punto-equilibrio/calculos", {"pedidos_dia": 60, "ticket": ticket, "margen_bruto": mb, "costos_fijos": 60000, "costo_variable_pedido": 32.6})[1]
            fila.append(f"{r['equilibrio_diario']} ({r['decision']})" if r["equilibrio_diario"] is not None else "sin equilibrio")
        filas.append(fila)
    out += ["### Ticket y margen: equilibrio diario con costos fijos de 60,000 y entrega de 32.60, para 60 pedidos al día", "",
            tabla(["Ticket \\ margen bruto", "22 %", "28 %", "34 %", "40 %"], filas), ""]

    # ---------------- Rutas ----------------
    from pruebas.preparar_listos import dejar_listos, retirar
    listos = dejar_listos(6, microhub_id=hub1)
    ids = [p["pedido_id"] for p in listos]
    try:
        rep = pedir("entregas", "entregas/repartidores")["datos"][0]["id"]
        promesa = configuracion("cob_tiempo_max_min")
        out += ["## Rutas (servicio rutas)", "",
                f"Los mismos {len(ids)} pedidos listos del microhub 1 en una sola ruta (un repartidor, método exacto): distancia, tiempo y costo. "
                f"«Fuera de la promesa» cuenta las paradas que se entregarían después de {promesa:g} minutos.", ""]
        for clave, valores in (("velocidad_reparto_kmh", [12, 18, 22, 30]), ("tiempo_servicio_min", [2, 4, 6, 8]), ("factor_rodeo_distancia", [1.0, 1.3, 1.6, 2.0]),
                               ("costo_km_reparto", [3.0, 4.5, 6.0])):
            filas = []
            b = Barrido(clave)
            for v in b.corre(valores):
                st, p = http("rutas", "POST", "rutas/planes", {"microhub_id": hub1, "pedido_ids": ids, "repartidor_ids": [rep], "metodo": "exacto"})
                if st != 200:
                    raise SystemExit(f"rutas respondió {st}: {p}")
                ruta = p["rutas"][0]
                fuera = sum(1 for x in ruta["paradas"] if x["minutos_acum"] > promesa)
                filas.append([marca(v, b.original), ruta["distancia_km"], ruta["minutos"], ruta["costo"], f"{fuera} de {len(ruta['paradas'])}"])
            out += [f"### {clave}", "", tabla([clave, "Distancia (km)", "Minutos", "Costo", "Fuera de la promesa"], filas), ""]
        filas = []
        for metodo in ("vecino", "2opt", "exacto"):
            st, p = http("rutas", "POST", "rutas/planes", {"microhub_id": hub1, "pedido_ids": ids, "repartidor_ids": [rep], "metodo": metodo})
            filas.append([p["rutas"][0]["metodo"], p["total"]["distancia_km"], p["total"]["minutos_maximo"], p["total"]["costo"]])
        out += ["### Método de ordenamiento de las paradas", "", tabla(["Método", "Distancia (km)", "Minutos", "Costo"], filas), ""]
    finally:
        retirar([p["pedido_id"] for p in listos if p["nuevo"]])

    # ---------------- Demanda ----------------
    out += ["## Demanda potencial (servicio demanda)", "",
            "Qué parte de la demanda posible captura hoy la red según la penetración y la frecuencia de compra supuestas.", ""]
    filas = []
    pen0, hog0 = configuracion("dem_penetracion"), configuracion("dem_pedidos_hogar_mes")
    try:
        for pen in (0.06, 0.08, 0.12, 0.16, 0.20):
            for hog in (2.0, 2.5, 3.0):
                fijar("dem_penetracion", pen); fijar("dem_pedidos_hogar_mes", hog)
                r = pedir("demanda", "demanda/potencial")
                vigente = " (vigente)" if (pen, hog) == (pen0, hog0) else ""
                filas.append([f"{pen:g}{vigente}", f"{hog:g}", r["pedidos_dia_potencial"], r["pedidos_dia_observados"], f"{r['cuota_capturada_pct']} %"])
    finally:
        fijar("dem_penetracion", pen0); fijar("dem_pedidos_hogar_mes", hog0)
    out += [tabla(["Penetración", "Pedidos por hogar al mes", "Pedidos al día posibles", "Pedidos al día observados", "Cuota capturada"], filas), ""]

    # ---------------- Surtido ----------------
    out += ["## Surtido (servicio surtido)", "", "Microhub 1: cuántos productos cambian de recomendación al mover los cortes.", ""]
    filas = []
    b = Barrido("abc_a_pct")
    for v in b.corre([60, 70, 80, 90]):
        r = pedir("surtido", "surtido/analisis", microhub_id=hub1)["resumen"]
        filas.append([marca(v, b.original), r["clase_a"], r["clase_b"], r["clase_c"], r["aumentar"], r["reducir"], r["eliminar"]])
    out += ["### Corte de la clase A", "", tabla(["abc_a_pct", "Productos A", "B", "C", "Aumentar", "Reducir", "Eliminar"], filas), ""]
    filas = []
    b = Barrido("cobertura_dias_exceso")
    for v in b.corre([30, 120, 365, 1000, 3000, 9000]):
        r = pedir("surtido", "surtido/analisis", microhub_id=hub1)["resumen"]
        filas.append([marca(v, b.original), r["aumentar"], r["mantener"], r["reducir"], r["eliminar"]])
    out += ["Con las ventas reales de la demostración (pocos pedidos en 90 días) la mayoría de los productos tiene años de cobertura, así que casi todo "
            "sale como «Reducir»; el umbral solo muerde cuando se sube a valores de varios cientos de días.", "",
            "### Días de cobertura a partir de los cuales hay exceso", "", tabla(["cobertura_dias_exceso", "Aumentar", "Mantener", "Reducir", "Eliminar"], filas), ""]

    # ---------------- Simulación ----------------
    out += ["## Simulación (servicio simulacion)", "",
            "Microhub 1, 30 días y 200 réplicas con la misma semilla. Cambiar el ausentismo o la variación de la demanda mueve la probabilidad de perder dinero.", ""]
    filas = []
    for aus in (0.0, 0.05, 0.10, 0.20):
        for var in (0.0, 0.10, 0.30):
            st, e = http("simulacion", "POST", "simulacion/ejecuciones", {"microhub_id": hub1, "dias": 30, "replicas": 200, "semilla": 2026, "ausentismo": aus, "variacion_demanda": var})
            for _ in range(60):
                time.sleep(0.5)
                st, r = http("simulacion", "GET", f"simulacion/ejecuciones/{e['id']}")
                if r["estado"] in ("terminada", "fallida", "cancelada"):
                    break
            m = {x["clave"]: x for x in r["resultados"]["metricas"]}
            filas.append([f"{aus:g}", f"{var:g}", f"{m['utilidad']['media']:,.0f}", f"{m['utilidad']['p10']:,.0f}", f"{m['utilidad']['p90']:,.0f}", f"{r['resultados']['prob_perdida_pct']} %",
                          f"{r['resultados']['dias_saturados_pct']} %"])
            with bd.conexion() as con, con.cursor() as cur:
                cur.execute("DELETE FROM simulacion_ejecucion WHERE id = %s", (e["id"],))
    out += [tabla(["Ausentismo", "Variación de la demanda", "Utilidad media", "P10", "P90", "Probabilidad de pérdida", "Días saturados"], filas), ""]

    salida = Path(a.salida)
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "escenarios.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Escenarios en {salida / 'escenarios.md'}")


if __name__ == "__main__":
    main()
