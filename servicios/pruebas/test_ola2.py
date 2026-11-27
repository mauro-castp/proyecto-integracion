"""
test_ola2.py — Los ocho servicios de análisis de la Ola 2 (demanda, cobertura, capacidad, rutas, costos, punto de
equilibrio, simulación y surtido) y lo que ganaron pedidos, entregas e inventario, contra PostgreSQL y Redis reales con el
modelo 01 a 10 cargado.

Los servicios se llaman entre sí como en producción (mismo JWT, misma traza) pero en proceso. Una prueba puede «apagar» un
servicio para ver qué hace el que depende de él. Cada prueba que cambia datos los deja como estaban.

  cd servicios && python -m unittest -v pruebas.test_ola2
"""
import datetime as dt
import json
import os
import sys
import time
import unittest
import uuid
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
os.environ.setdefault("LOG_STDOUT", "0")
os.environ.setdefault("SIM_TRABAJADOR", "0")

from comun import clientes, config, datos  # noqa: E402
from pruebas import preparar_listos  # noqa: E402
from pruebas.test_contrato import APPS, Cliente, NS, ejemplo, mismas_llaves, xml  # noqa: E402

sim = sys.modules["simulacion.app"]
rutas_mod = sys.modules["rutas.app"]
APAGADOS = set()
LIMITE = {}


def transporte(servicio, metodo, ruta, cuerpo, params, token, traza):
    if servicio in APAGADOS:
        raise ConnectionError(f"{servicio} apagado por la prueba")
    enc = {"Accept": "application/json", "Content-Type": "application/json"}
    if token:
        enc["Authorization"] = f"Bearer {token}"
    if traza:
        enc["X-Traza-Id"] = traza
    r = APPS[servicio].test_client().open(f"/api/v1/{ruta}", method=metodo, query_string=params or None, headers=enc,
                                          data=json.dumps(cuerpo) if cuerpo is not None else None)
    return r.status_code, (r.get_json(silent=True) if r.data else None)


def setUpModule():
    clientes.usar_transporte(transporte)
    LIMITE["antes"] = config.LIMITE_POR_MINUTO
    LIMITE["login"] = config.LIMITE_LOGIN_POR_MINUTO
    config.LIMITE_POR_MINUTO = config.LIMITE_LOGIN_POR_MINUTO = 1_000_000
    for k in datos.r_cache.keys("cache:mapa:*") or []:
        datos.r_cache.delete(k)


def tearDownModule():
    clientes.usar_transporte(None)
    config.LIMITE_POR_MINUTO, config.LIMITE_LOGIN_POR_MINUTO = LIMITE["antes"], LIMITE["login"]


def uno(sql, args=()):
    return datos.consultar(sql, args, una=True)


def todos(sql, args=()):
    return datos.consultar(sql, args)


def ejecutar(sql, args=()):
    with datos.conexion() as con, con.cursor() as cur:
        cur.execute(sql, args)


def microhub(clave):
    return uno("SELECT id FROM microhub WHERE clave = %s", (clave,))["id"]


class Apagado:
    """with Apagado('inventario'): … — el servicio no responde dentro del bloque."""

    def __init__(self, *servicios):
        self.s = servicios

    def __enter__(self):
        APAGADOS.update(self.s)
        for k in datos.r_cache.keys("cache:mapa:*") or []:           # sin caché, el servicio caído se nota
            datos.r_cache.delete(k)

    def __exit__(self, *a):
        APAGADOS.difference_update(self.s)


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._caso = unittest.TestCase()
        cls.HUB1, cls.HUB2, cls.HUB3 = microhub("MH-01"), microhub("MH-02"), microhub("MH-03")
        cls.adm = cls.entrar("admin@codex.mx")
        cls.plan = cls.entrar("planeador@codex.mx")
        cls.op1 = cls.entrar("operador.mh01@codex.mx")
        cls.op2 = cls.entrar("operador.mh02@codex.mx")
        cls.aud = cls.entrar("auditor@codex.mx")
        cls.rep = cls.entrar("repartidor1@codex.mx")
        cls.cli = cls.entrar("juan.chapa1@correo.mx")
        cls.adm_xml = cls.entrar("admin@codex.mx", "xml")
        cls.plan_xml = cls.entrar("planeador@codex.mx", "xml")

    @classmethod
    def entrar(cls, correo, formato="json"):
        c = Cliente(cls._caso, formato)
        c.entrar(correo)
        return c

    def setUp(self):
        for c in (self.adm, self.plan, self.op1, self.op2, self.aud, self.rep, self.cli, self.adm_xml, self.plan_xml):
            c.caso = self

    def http(self, cliente, servicio, metodo, ruta, cuerpo=None):
        return cliente.llamar(servicio, metodo, ruta, cuerpo)[0].status_code

    def error(self, cliente, servicio, metodo, ruta, cuerpo, estado, codigo=None):
        r, d = cliente.llamar(servicio, metodo, ruta, cuerpo, estado=estado)
        if codigo:
            self.assertEqual(d["error"]["codigo"], codigo)
        return d["error"]

    def ambos_formatos(self, servicio, ruta, **kw):
        """El mismo GET en JSON y en XML: el XML cumple el XSD (lo comprueba el cliente) y trae los mismos valores de primer nivel."""
        _, j = self.adm.llamar(servicio, "GET", ruta, estado=200)
        _, (raiz, x) = self.adm_xml.llamar(servicio, "GET", ruta, estado=200)
        return j, raiz, x


# ====================================================================
# Pedidos, entregas e inventario: lo que ganaron para alimentar el análisis
# ====================================================================
class T1Alimentadores(Base):
    def test_resumen_de_pedidos_por_dia_y_zona(self):
        _, r = self.adm.llamar("pedidos", "GET", "pedidos/resumen?por_pagina=100", estado=200)
        mismas_llaves(self, r, ejemplo("ResumenPedidos.ok"), opcionales=("categoria_id",))
        self.assertTrue(all(f["pedidos"] > 0 for f in r["datos"]))
        _, cat = self.adm.llamar("pedidos", "GET", "pedidos/resumen?agrupar=dia_zona_categoria&por_pagina=100", estado=200)
        self.assertTrue(all(f["categoria_id"] for f in cat["datos"]))
        self.assertGreaterEqual(cat["paginacion"]["total"], r["paginacion"]["total"])
        self.assertEqual(self.http(self.adm, "pedidos", "GET", "pedidos/resumen?agrupar=otra"), 400)
        self.assertEqual(self.http(self.adm, "pedidos", "GET", "pedidos/resumen?desde=2026-10-10&hasta=2026-10-01"), 400)
        # un cliente solo ve sus propios pedidos y nunca la demanda no atendida de la red
        _, mio = self.cli.llamar("pedidos", "GET", "pedidos/resumen?desde=2026-01-01&por_pagina=100", estado=200)
        self.assertLessEqual(sum(f["pedidos"] for f in mio["datos"]), sum(f["pedidos"] for f in r["datos"]))
        self.assertEqual({f["no_atendidos"] for f in mio["datos"]}, {0} if mio["datos"] else set())
        self.adm_xml.llamar("pedidos", "GET", "pedidos/resumen?por_pagina=5", estado=200)

    def test_el_resumen_no_cuenta_cancelados(self):
        hoy = dt.date.today().isoformat()
        filas, pagina = [], 1
        while True:
            _, r = self.adm.llamar("pedidos", "GET", f"pedidos/resumen?por_pagina=100&pagina={pagina}&desde=2026-01-01&hasta={hoy}", estado=200)
            filas += r["datos"]
            if pagina >= r["paginacion"]["paginas"]:
                break
            pagina += 1
        reales = uno("SELECT count(*) AS n FROM pedido WHERE estado <> 'cancelado' AND (creado_en AT TIME ZONE 'America/Monterrey')::date BETWEEN '2026-01-01' AND %s", (hoy,))["n"]
        self.assertEqual(sum(f["pedidos"] for f in filas), reales)

    def test_ventas_por_producto(self):
        _, v = self.adm.llamar("pedidos", "GET", "pedidos/ventas?por_pagina=100", estado=200)
        mismas_llaves(self, v, ejemplo("VentasPedidos.ok"))
        unidades = [f["unidades"] for f in v["datos"]]
        self.assertEqual(unidades, sorted(unidades, reverse=True))
        _, hub = self.adm.llamar("pedidos", "GET", f"pedidos/ventas?por_pagina=100&microhub_id={self.HUB1}", estado=200)
        self.assertLessEqual(sum(f["unidades"] for f in hub["datos"]), sum(unidades))
        self.adm_xml.llamar("pedidos", "GET", "pedidos/ventas?por_pagina=5", estado=200)

    def test_pedidos_listos_exige_microhub_y_respeta_el_alcance(self):
        self.error(self.adm, "pedidos", "GET", "pedidos/listos", None, 400, "FILTRO_INVALIDO")
        self.assertEqual(self.http(self.op1, "pedidos", "GET", f"pedidos/listos?microhub_id={self.HUB1}"), 200)
        # el operador de otro microhub no ve los pedidos de este (la visibilidad la aplica PostgreSQL)
        _, d = self.op2.llamar("pedidos", "GET", f"pedidos/listos?microhub_id={self.HUB1}", estado=200)
        self.assertEqual(d["datos"], [])
        self.assertEqual(self.http(self.cli, "pedidos", "GET", f"pedidos/listos?microhub_id={self.HUB1}"), 403)

    def test_repartidores_activos(self):
        _, r = self.adm.llamar("entregas", "GET", "entregas/repartidores", estado=200)
        mismas_llaves(self, r, ejemplo("Repartidores.ok"))
        correos = {x["nombre"] for x in r["datos"]}
        self.assertGreaterEqual(len(correos), 2)
        self.assertTrue(all(x["entregas_abiertas"] >= 0 for x in r["datos"]))
        self.assertEqual(self.http(self.op1, "entregas", "GET", "entregas/repartidores"), 200)
        self.assertEqual(self.http(self.rep, "entregas", "GET", "entregas/repartidores"), 403)
        self.adm_xml.llamar("entregas", "GET", "entregas/repartidores", estado=200)

    def test_quiebres_de_inventario(self):
        hub = self.HUB1
        pid = uno("SELECT producto_id FROM inventario WHERE microhub_id = %s AND existencia > 30 ORDER BY producto_id LIMIT 1", (hub,))["producto_id"]
        orig = uno("SELECT existencia, minimo FROM inventario WHERE microhub_id = %s AND producto_id = %s", (hub, pid))
        try:
            ejecutar("INSERT INTO movimiento_inventario (microhub_id, producto_id, tipo, cantidad, existencia_resultante, motivo) "
                     "VALUES (%s,%s,'merma',%s,0,'prueba de quiebre')", (hub, pid, -orig["existencia"]))
            _, q = self.adm.llamar("inventario", "GET", f"inventario/quiebres?microhub_id={hub}&por_pagina=100", estado=200)
            mismas_llaves(self, q, ejemplo("QuiebreLista.ok"))
            fila = next(f for f in q["datos"] if f["producto_id"] == pid)
            self.assertGreaterEqual(fila["quiebres"], 1)
            self.assertIsNotNone(fila["ultimo"])
            self.error(self.adm, "inventario", "GET", "inventario/quiebres?dias=0", None, 400, "FILTRO_INVALIDO")
            self.assertEqual(self.http(self.op2, "inventario", "GET", f"inventario/quiebres?microhub_id={hub}"), 403)
            self.adm_xml.llamar("inventario", "GET", f"inventario/quiebres?microhub_id={hub}", estado=200)
        finally:
            ejecutar("DELETE FROM movimiento_inventario WHERE microhub_id = %s AND producto_id = %s AND motivo = 'prueba de quiebre'", (hub, pid))


# ====================================================================
# Demanda
# ====================================================================
class T2Demanda(Base):
    def test_observaciones_traen_su_fuente_y_se_filtran(self):
        _, o = self.adm.llamar("demanda", "GET", "demanda/observaciones?por_pagina=50", estado=200)
        mismas_llaves(self, o, ejemplo("ObservacionDemandaLista.ok"))
        self.assertTrue(o["datos"])
        self.assertEqual({f["fuente"] for f in o["datos"]} - {"pedidos", "sintetica", "manual"}, set())
        _, s = self.adm.llamar("demanda", "GET", "demanda/observaciones?fuente=sintetica&nivel=total&por_pagina=100", estado=200)
        self.assertTrue(all(f["fuente"] == "sintetica" and f["categoria"] is None for f in s["datos"]))
        _, c = self.adm.llamar("demanda", "GET", "demanda/observaciones?nivel=categoria&por_pagina=10", estado=200)
        self.assertTrue(all(f["categoria"] for f in c["datos"]))
        self.assertEqual(self.http(self.adm, "demanda", "GET", "demanda/observaciones?fuente=inventada"), 400)
        self.assertEqual(self.http(self.adm, "demanda", "GET", "demanda/observaciones?desde=2026-10-10&hasta=2026-10-01"), 400)
        self.assertEqual(self.http(self.op1, "demanda", "GET", "demanda/observaciones"), 403)
        self.assertEqual(self.http(self.aud, "demanda", "GET", "demanda/observaciones"), 200)
        self.ambos_formatos("demanda", "demanda/observaciones?por_pagina=5")

    def test_resumen_suma_lo_mismo_por_zona_que_en_total(self):
        _, r = self.adm.llamar("demanda", "GET", "demanda/resumen", estado=200)
        mismas_llaves(self, r, ejemplo("DemandaResumen.ok"))
        self.assertEqual(r["total"]["pedidos"], sum(z["pedidos"] for z in r["zonas"]))
        self.assertAlmostEqual(r["total"]["pedidos_dia"], r["total"]["pedidos"] / r["dias"], delta=0.01)
        self.assertGreater(r["observaciones_por_fuente"]["sintetica"] + r["observaciones_por_fuente"]["pedidos"], 0)
        zona = r["zonas"][0]["zona"]["id"]
        _, z = self.adm.llamar("demanda", "GET", f"demanda/resumen?zona_id={zona}", estado=200)
        self.assertEqual(z["total"]["pedidos"], r["zonas"][0]["pedidos"])
        self.assertEqual(self.http(self.adm, "demanda", "GET", "demanda/resumen?zona_id=99999"), 404)
        self.ambos_formatos("demanda", "demanda/resumen")

    def test_patrones_semanales(self):
        _, p = self.adm.llamar("demanda", "GET", "demanda/patrones", estado=200)
        mismas_llaves(self, p, ejemplo("DemandaPatrones.ok"))
        self.assertEqual([d["dia"] for d in p["semanal"]], [1, 2, 3, 4, 5, 6, 7])
        self.assertTrue(p["suficiente"])
        self.assertAlmostEqual(sum(d["indice"] for d in p["semanal"]) / 7, 1.0, delta=0.01)
        pico = max(p["semanal"], key=lambda d: d["indice"])["nombre"]
        self.assertEqual(p["dia_pico"], pico)
        self.assertGreater(p["fuerza_estacional"], 1.0)
        self.assertAlmostEqual(sum(c["pct_venta"] for c in p["categorias"]), 100.0, delta=0.5)
        self.ambos_formatos("demanda", "demanda/patrones")

    def test_proyeccion_con_banda_y_metodos(self):
        _, p = self.adm.llamar("demanda", "GET", "demanda/proyeccion", estado=200)
        mismas_llaves(self, p, ejemplo("DemandaProyeccion.ok"), opcionales=("zona",))
        self.assertEqual(len(p["serie"]), p["horizonte"])
        self.assertEqual(p["horizonte"], 14)
        self.assertTrue(all(d["minimo"] <= d["pedidos"] <= d["maximo"] for d in p["serie"]))
        self.assertAlmostEqual(p["total_pedidos"], sum(d["pedidos"] for d in p["serie"]), delta=0.2)
        _, m = self.adm.llamar("demanda", "GET", "demanda/proyeccion?metodo=promedio_movil&horizonte=7", estado=200)
        self.assertEqual((m["metodo"], len(m["serie"]), m["pendiente_pedidos_dia"]), ("promedio_movil", 7, 0.0))
        self.assertEqual(self.http(self.adm, "demanda", "GET", "demanda/proyeccion?metodo=magico"), 400)
        self.assertEqual(self.http(self.adm, "demanda", "GET", "demanda/proyeccion?horizonte=500"), 400)
        self.assertEqual(self.http(self.adm, "demanda", "GET", "demanda/proyeccion?zona_id=99999"), 404)
        self.ambos_formatos("demanda", "demanda/proyeccion?horizonte=3")

    def test_comparacion_contra_lo_observado(self):
        _, c = self.adm.llamar("demanda", "GET", "demanda/comparacion", estado=200)
        mismas_llaves(self, c, ejemplo("DemandaComparacion.ok"), opcionales=("zona",))
        self.assertEqual(c["dias_prueba"], 7)
        self.assertEqual(len(c["filas"]), 7)
        self.assertGreater(c["dias_entrenamiento"], 14)
        self.assertGreaterEqual(c["dentro_banda_pct"], 0)
        self.assertLess(c["mape_pct"], 60.0, "el modelo no debe errar más de 60 % en una serie con patrón claro")
        self.ambos_formatos("demanda", "demanda/comparacion")

    def test_potencial_de_hogares(self):
        _, p = self.adm.llamar("demanda", "GET", "demanda/potencial", estado=200)
        mismas_llaves(self, p, ejemplo("DemandaPotencial.ok"), opcionales=("zona",))
        self.assertAlmostEqual(p["pedidos_mes_potencial"], p["hogares"] * p["penetracion"] * p["pedidos_hogar_mes"], delta=0.2)
        self.assertAlmostEqual(p["pedidos_dia_potencial"], p["pedidos_mes_potencial"] / 30, delta=0.1)
        self.assertEqual(len(p["escenarios"]), 5)
        self.assertEqual(p["brecha_pedidos_dia"], round(p["pedidos_dia_potencial"] - p["pedidos_dia_observados"], 1))
        _, otra = self.adm.llamar("demanda", "GET", "demanda/potencial?penetracion=0.2", estado=200)
        self.assertGreater(otra["pedidos_dia_potencial"], p["pedidos_dia_potencial"])
        self.assertEqual(otra["penetracion"], 0.2)
        self.ambos_formatos("demanda", "demanda/potencial")

    def test_sincronizar_reemplaza_lo_sintetico_por_lo_real_y_pide_permiso(self):
        hoy = dt.date.today()
        desde, hasta = hoy - dt.timedelta(days=2), hoy
        antes = todos("SELECT * FROM demanda_observacion WHERE fecha BETWEEN %s AND %s", (desde, hasta))
        cuerpo = {"desde": desde.isoformat(), "hasta": hasta.isoformat()}
        try:
            self.assertEqual(self.http(self.aud, "demanda", "POST", "demanda/sincronizacion", cuerpo), 403)
            self.assertEqual(self.http(self.op1, "demanda", "POST", "demanda/sincronizacion", cuerpo), 403)
            r, s = self.plan.llamar("demanda", "POST", "demanda/sincronizacion", cuerpo, estado=201)
            mismas_llaves(self, s, ejemplo("Sincronizacion.ok"))
            despues = todos("SELECT fuente, count(*) AS n FROM demanda_observacion WHERE fecha BETWEEN %s AND %s GROUP BY 1", (desde, hasta))
            self.assertEqual({f["fuente"] for f in despues} - {"pedidos"}, set(), "en el rango solo queda lo real")
            self.assertEqual(sum(f["n"] for f in despues), s["filas_escritas"])
            # idempotente: repetirlo deja lo mismo
            _, otra = self.plan.llamar("demanda", "POST", "demanda/sincronizacion", cuerpo, estado=201)
            self.assertEqual((otra["filas_escritas"], otra["pedidos_leidos"]), (s["filas_escritas"], s["pedidos_leidos"]))
            self.error(self.plan, "demanda", "POST", "demanda/sincronizacion", {"desde": "2026-10-10", "hasta": "2026-10-01"}, 422, "VALIDACION")
            self.error(self.plan, "demanda", "POST", "demanda/sincronizacion", {"desde": "ayer", "hasta": "hoy"}, 422, "VALIDACION")
            self.plan_xml.llamar("demanda", "POST", "demanda/sincronizacion", xml("sincronizacion_nueva", cuerpo), estado=201)
            with Apagado("pedidos"):
                self.error(self.plan, "demanda", "POST", "demanda/sincronizacion", cuerpo, 503, "SERVICIO_NO_DISPONIBLE")
        finally:
            ejecutar("DELETE FROM demanda_observacion WHERE fecha BETWEEN %s AND %s", (desde, hasta))
            for f in antes:
                ejecutar("INSERT INTO demanda_observacion (fecha, zona_id, categoria_id, pedidos, unidades, venta, clientes, no_atendidos, fuente) "
                         "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                         (f["fecha"], f["zona_id"], f["categoria_id"], f["pedidos"], f["unidades"], f["venta"], f["clientes"], f["no_atendidos"], f["fuente"]))
        self.assertEqual(len(todos("SELECT 1 FROM demanda_observacion WHERE fecha BETWEEN %s AND %s", (desde, hasta))), len(antes), "se restauró la historia")

    def test_con_poca_historia_no_proyecta(self):
        ayer = (dt.date.today() - dt.timedelta(days=1)).isoformat()
        self.error(self.adm, "demanda", "GET", f"demanda/proyeccion?desde={ayer}&hasta={ayer}", None, 422, "VALIDACION")


# ====================================================================
# Cobertura
# ====================================================================
class T3Cobertura(Base):
    def test_zonas_y_resumen_de_la_red(self):
        _, z = self.adm.llamar("cobertura", "GET", "cobertura/zonas?por_pagina=100", estado=200)
        mismas_llaves(self, z, ejemplo("CoberturaZonaLista.ok"))
        _, r = self.adm.llamar("cobertura", "GET", "cobertura/resumen", estado=200)
        mismas_llaves(self, r, ejemplo("CoberturaResumen.ok"))
        self.assertEqual(r["zonas"], z["paginacion"]["total"])
        self.assertEqual(r["zonas_cubiertas"], sum(1 for x in z["datos"] if x["estado"] == "cubierta"))
        self.assertEqual(r["hogares"], sum(x["hogares"] for x in z["datos"]))
        self.assertEqual(r["zonas_solapadas"], sum(1 for x in z["datos"] if x["solapada"]))
        for x in z["datos"]:
            minutos = [o["minutos"] for o in x["cubierta_por"]]
            self.assertEqual(minutos, sorted(minutos) if all(o["distancia_km"] >= 0 for o in x["cubierta_por"]) else minutos)
            if x["estado"] == "cubierta":
                self.assertEqual(x["minutos_mejor"], x["cubierta_por"][0]["minutos"])
        self.ambos_formatos("cobertura", "cobertura/zonas?por_pagina=5")
        self.ambos_formatos("cobertura", "cobertura/resumen")

    def test_el_rodeo_de_las_calles_alarga_los_tiempos_sin_cambiar_la_cobertura(self):
        _, e = self.adm.llamar("cobertura", "GET", "cobertura/escenarios?radios=1.5&rodeos=1.0,2.0", estado=200)
        recto, calle = e["filas"]
        self.assertEqual((recto["rodeo"], calle["rodeo"]), (1.0, 2.0))
        self.assertGreater(calle["tiempo_promedio_min"], recto["tiempo_promedio_min"])
        self.assertEqual(calle["pct_hogares"], recto["pct_hogares"], "la regla de cobertura es el radio en línea recta")
        self.assertEqual(self.http(self.adm, "cobertura", "GET", "cobertura/escenarios?rodeos=0.5"), 400)
        self.assertEqual(self.http(self.adm, "cobertura", "GET", "cobertura/escenarios?radios=abc"), 400)

    def test_un_punto_cerca_de_un_microhub_esta_cubierto_y_uno_lejano_no(self):
        h = uno("SELECT latitud::float AS lat, longitud::float AS lng FROM microhub WHERE id = %s", (self.HUB1,))
        _, cerca = self.adm.llamar("cobertura", "GET", f"cobertura/punto?latitud={h['lat']}&longitud={h['lng']}", estado=200)
        mismas_llaves(self, cerca, ejemplo("CoberturaPunto.ok"), opcionales=("zona_mas_cercana",))
        self.assertTrue(cerca["cubierto"])
        self.assertEqual(cerca["opciones"][0]["distancia_km"], 0.0)
        _, lejos = self.adm.llamar("cobertura", "GET", "cobertura/punto?latitud=26.9&longitud=-101.4", estado=200)
        self.assertFalse(lejos["cubierto"])
        self.assertTrue(all(not o["cubre"] for o in lejos["opciones"]))
        self.assertEqual(self.http(self.adm, "cobertura", "GET", "cobertura/punto?latitud=95&longitud=10"), 400)
        self.assertEqual(self.http(self.adm, "cobertura", "GET", "cobertura/punto"), 400)
        self.ambos_formatos("cobertura", f"cobertura/punto?latitud={h['lat']}&longitud={h['lng']}")

    def test_candidatos_con_ranking(self):
        _, c = self.adm.llamar("cobertura", "GET", "cobertura/candidatos", estado=200)
        mismas_llaves(self, c, ejemplo("CoberturaCandidatos.ok"))
        self.assertTrue(c["datos"])
        self.assertEqual([f["ranking"] for f in c["datos"]], list(range(1, len(c["datos"]) + 1)))
        clave = [(-f["hogares_nuevos"], -f["hogares_con_mejor_tiempo"], f["solapamiento_pct"]) for f in c["datos"]]
        self.assertEqual(clave, sorted(clave), "primero el que más hogares suma, después el que más acerca el servicio")
        self.ambos_formatos("cobertura", "cobertura/candidatos")
        with Apagado("planeacion"):
            self.error(self.adm, "cobertura", "GET", "cobertura/candidatos", None, 503, "SERVICIO_NO_DISPONIBLE")

    def test_evaluar_una_ubicacion_candidata_y_guardarla(self):
        _, cands = self.adm.llamar("cobertura", "GET", "cobertura/candidatos", estado=200)
        cid = cands["datos"][0]["candidato"]["id"]
        _, e = self.adm.llamar("cobertura", "POST", "cobertura/evaluaciones", {"candidato_id": cid}, estado=200)
        mismas_llaves(self, e, ejemplo("CoberturaEvaluacion.ok"), opcionales=("candidato",))
        self.assertIsNone(e["id"], "sin guardar no se crea nada")
        self.assertEqual(e["candidato"]["id"], cid)
        self.assertEqual(e["despues"]["pct_hogares"] >= e["antes"]["pct_hogares"], True)
        self.assertEqual(self.http(self.aud, "cobertura", "POST", "cobertura/evaluaciones", {"candidato_id": cid, "guardar": True}), 403)
        antes = uno("SELECT count(*) AS n FROM cobertura_evaluacion")["n"]
        try:
            _, g = self.plan.llamar("cobertura", "POST", "cobertura/evaluaciones", {"candidato_id": cid, "guardar": True, "nombre": "Prueba Ola 2"}, estado=201)
            self.assertEqual(uno("SELECT count(*) AS n FROM cobertura_evaluacion")["n"], antes + 1)
            _, lista = self.adm.llamar("cobertura", "GET", "cobertura/evaluaciones?por_pagina=100", estado=200)
            mismas_llaves(self, lista, ejemplo("CoberturaEvaluacionLista.ok"))
            self.assertIn(g["id"], [f["id"] for f in lista["datos"]])
            _, uno_ = self.adm.llamar("cobertura", "GET", f"cobertura/evaluaciones/{g['id']}", estado=200)
            self.assertEqual(uno_["nombre"], "Prueba Ola 2")
            self.assertEqual(self.http(self.adm, "cobertura", "GET", "cobertura/evaluaciones/999999"), 404)
        finally:
            ejecutar("DELETE FROM cobertura_evaluacion WHERE nombre = 'Prueba Ola 2'")

    def test_evaluar_una_coordenada_y_validar_la_entrada(self):
        h = uno("SELECT latitud::float AS lat, longitud::float AS lng FROM microhub WHERE id = %s", (self.HUB1,))
        _, e = self.adm.llamar("cobertura", "POST", "cobertura/evaluaciones", {"latitud": h["lat"], "longitud": h["lng"], "radio_km": 2}, estado=200)
        self.assertEqual(e["solapamiento_pct"], 100.0, "encima de un microhub existente todo se traslapa")
        self.assertTrue(e["canibaliza"])
        self.assertEqual(e["hogares_nuevos"], 0)
        self.assertGreater(len(e["zonas"]), 0)
        self.assertEqual(self.http(self.adm, "cobertura", "POST", "cobertura/evaluaciones", {"radio_km": 2}), 422)
        self.assertEqual(self.http(self.adm, "cobertura", "POST", "cobertura/evaluaciones", {"latitud": 10, "longitud": 10}), 422)
        self.assertEqual(self.http(self.adm, "cobertura", "POST", "cobertura/evaluaciones", {"candidato_id": 99999}), 404)
        self.plan_xml.llamar("cobertura", "POST", "cobertura/evaluaciones", xml("cobertura_evaluacion_nueva", {"latitud": h["lat"], "longitud": h["lng"], "radio_km": 2}), estado=200)

    def test_escenarios_de_radio_nunca_cubren_menos_con_un_radio_mayor(self):
        _, e = self.adm.llamar("cobertura", "GET", "cobertura/escenarios?radios=0.5,1,2,3&rodeos=1.3", estado=200)
        mismas_llaves(self, e, ejemplo("CoberturaEscenarios.ok"))
        pct = [f["pct_hogares"] for f in e["filas"]]
        self.assertEqual(pct, sorted(pct))
        self.assertEqual(self.http(self.adm, "cobertura", "GET", "cobertura/escenarios?radios=0,5"), 400)
        self.ambos_formatos("cobertura", "cobertura/escenarios")

    def test_la_poblacion_se_corrige_con_su_fuente(self):
        zona = uno("SELECT zona_id, poblacion FROM cobertura_zona_dato ORDER BY zona_id LIMIT 1")
        ruta = f"cobertura/zonas/{zona['zona_id']}/poblacion"
        try:
            self.assertEqual(self.http(self.aud, "cobertura", "PUT", ruta, {"poblacion": 5000, "fuente": "INEGI, Censo 2020"}), 403)
            self.assertEqual(self.http(self.op1, "cobertura", "PUT", ruta, {"poblacion": 5000, "fuente": "INEGI, Censo 2020"}), 403)
            _, r = self.plan.llamar("cobertura", "PUT", ruta, {"poblacion": 5040, "fuente": "INEGI, Censo 2020, AGEB de prueba"}, estado=200)
            mismas_llaves(self, r, ejemplo("PoblacionZona.ok"))
            self.assertEqual(r["hogares"], round(5040 / 3.6))
            _, res = self.adm.llamar("cobertura", "GET", "cobertura/zonas?por_pagina=100", estado=200)
            self.assertEqual(next(z for z in res["datos"] if z["zona"]["id"] == zona["zona_id"])["hogares"], r["hogares"])
            self.assertEqual(self.http(self.plan, "cobertura", "PUT", ruta, {"poblacion": -1, "fuente": "x"}), 422)
            self.assertEqual(self.http(self.plan, "cobertura", "PUT", "cobertura/zonas/99999/poblacion", {"poblacion": 10, "fuente": "Fuente de prueba"}), 404)
            self.plan_xml.llamar("cobertura", "PUT", ruta, xml("poblacion_nueva", {"poblacion": 5040, "fuente": "INEGI, Censo 2020, AGEB de prueba"}), estado=200)
        finally:
            ejecutar("UPDATE cobertura_zona_dato SET poblacion = %s, fuente = 'Estimación del equipo (06_planeacion.sql); sustituir por el dato de INEGI de cada colonia' "
                     "WHERE zona_id = %s", (zona["poblacion"], zona["zona_id"]))

    def test_sin_el_servicio_de_zonas_no_hay_cobertura(self):
        with Apagado("zonas"):
            self.error(self.adm, "cobertura", "GET", "cobertura/resumen", None, 503, "SERVICIO_NO_DISPONIBLE")

    def test_supuestos_documentados(self):
        _, s = self.adm.llamar("cobertura", "GET", "cobertura/supuestos", estado=200)
        mismas_llaves(self, s, ejemplo("SupuestosCobertura.ok"))
        claves = {x["clave"] for x in s["datos"]}
        self.assertTrue({"factor_rodeo_distancia", "velocidad_reparto_kmh", "cob_tiempo_max_min", "tamano_hogar"} <= claves)


# ====================================================================
# Capacidad
# ====================================================================
class T4Capacidad(Base):
    def test_recursos_por_microhub(self):
        _, r = self.adm.llamar("capacidad", "GET", "capacidad/recursos?por_pagina=100", estado=200)
        mismas_llaves(self, r, ejemplo("RecursoCapacidadLista.ok"), opcionales=("capacidad_fisica",))
        self.assertGreaterEqual(r["paginacion"]["total"], 3)
        _, u = self.adm.llamar("capacidad", "GET", f"capacidad/recursos/{self.HUB1}", estado=200)
        mismas_llaves(self, u, ejemplo("RecursoCapacidad.ok"), opcionales=("capacidad_fisica",))
        self.assertEqual(u["microhub"]["id"], self.HUB1)
        self.assertEqual(self.http(self.op1, "capacidad", "GET", f"capacidad/recursos/{self.HUB2}"), 403)
        self.assertEqual(self.http(self.adm, "capacidad", "GET", "capacidad/recursos/99999"), 404)
        self.assertEqual(self.http(self.cli, "capacidad", "GET", "capacidad/recursos"), 403)

    def test_cambiar_los_recursos_exige_permiso_y_se_restaura(self):
        antes = uno("SELECT operadores, repartidores, capacidad_fisica FROM capacidad_recurso WHERE microhub_id = %s", (self.HUB1,))
        ruta = f"capacidad/recursos/{self.HUB1}"
        try:
            self.assertEqual(self.http(self.aud, "capacidad", "PUT", ruta, {"operadores": 5, "repartidores": 4}), 403)
            self.assertEqual(self.http(self.op1, "capacidad", "PUT", ruta, {"operadores": 5, "repartidores": 4}), 403)
            _, r = self.plan.llamar("capacidad", "PUT", ruta, {"operadores": 5, "repartidores": 4, "capacidad_fisica": None}, estado=200)
            self.assertEqual((r["operadores"], r["repartidores"], r["capacidad_fisica"]), (5, 4, None))
            _, m = self.adm.llamar("capacidad", "GET", f"capacidad/microhubs/{self.HUB1}?carga_dia=50", estado=200)
            self.assertEqual(m["operadores"], 5)
            self.assertEqual(self.http(self.plan, "capacidad", "PUT", ruta, {"operadores": 0, "repartidores": 4}), 422)
            self.assertEqual(self.http(self.plan, "capacidad", "PUT", ruta, {"operadores": 5}), 422)
            self.assertEqual(self.http(self.plan, "capacidad", "PUT", "capacidad/recursos/99999", {"operadores": 5, "repartidores": 4}), 404)
            self.plan_xml.llamar("capacidad", "PUT", ruta, xml("recurso_capacidad_nuevo", {"operadores": 5, "repartidores": 4}), estado=200)
        finally:
            ejecutar("UPDATE capacidad_recurso SET operadores = %s, repartidores = %s, capacidad_fisica = %s WHERE microhub_id = %s",
                     (antes["operadores"], antes["repartidores"], antes["capacidad_fisica"], self.HUB1))

    def test_utilizacion_y_nivel_de_un_microhub(self):
        _, m = self.adm.llamar("capacidad", "GET", f"capacidad/microhubs/{self.HUB1}?carga_dia=60", estado=200)
        mismas_llaves(self, m, ejemplo("CapacidadMicrohub.ok"), opcionales=("capacidad_fisica",))
        self.assertAlmostEqual(m["utilizacion_pct"], round(100 * 60 / m["capacidad_dia"], 1), delta=0.1)
        self.assertEqual(m["carga_dia"], 60)
        self.assertEqual([e["etapa"] for e in m["etapas"]], ["picking", "empaque", "despacho", "reparto"])
        self.assertAlmostEqual(m["holgura_pedidos_dia"], round(m["capacidad_dia"] - 60, 1), delta=0.1)
        _, saturado = self.adm.llamar("capacidad", "GET", f"capacidad/microhubs/{self.HUB1}?carga_dia={m['capacidad_dia'] * 0.95}", estado=200)
        self.assertEqual(saturado["nivel"], "riesgo")
        _, holgado = self.adm.llamar("capacidad", "GET", f"capacidad/microhubs/{self.HUB1}?carga_dia=1", estado=200)
        self.assertEqual(holgado["nivel"], "estable")
        self.assertEqual(self.http(self.adm, "capacidad", "GET", f"capacidad/microhubs/{self.HUB1}?horas=99"), 400)
        self.assertEqual(self.http(self.adm, "capacidad", "GET", f"capacidad/microhubs/{self.HUB1}?carga_dia=-3"), 400)
        self.assertEqual(self.http(self.op1, "capacidad", "GET", f"capacidad/microhubs/{self.HUB1}"), 200)
        self.assertEqual(self.http(self.op1, "capacidad", "GET", f"capacidad/microhubs/{self.HUB2}"), 403)
        self.ambos_formatos("capacidad", f"capacidad/microhubs/{self.HUB1}?carga_dia=60")

    def test_la_carga_observada_viene_de_pedidos_y_sin_ellos_se_puede_indicar(self):
        with Apagado("pedidos"):
            self.error(self.adm, "capacidad", "GET", f"capacidad/microhubs/{self.HUB1}", None, 503, "SERVICIO_NO_DISPONIBLE")
            self.assertEqual(self.http(self.adm, "capacidad", "GET", f"capacidad/microhubs/{self.HUB1}?carga_dia=40"), 200,
                             "con la carga indicada no depende de pedidos")

    def test_lista_de_microhubs_limitada_al_alcance(self):
        _, t = self.adm.llamar("capacidad", "GET", "capacidad/microhubs?carga_dia=30&por_pagina=100", estado=200)
        mismas_llaves(self, t, ejemplo("CapacidadMicrohubLista.ok"), opcionales=("capacidad_fisica",))
        _, o = self.op1.llamar("capacidad", "GET", "capacidad/microhubs?carga_dia=30", estado=200)
        self.assertEqual([f["microhub"]["id"] for f in o["datos"]], [self.HUB1])

    def test_simulacion_de_mas_personal(self):
        base = {"microhub_id": self.HUB1, "pedidos_dia": 120}
        _, s = self.adm.llamar("capacidad", "POST", "capacidad/simulaciones", {**base, "operadores": 6, "repartidores": 6, "capacidad_fisica": 1000}, estado=200)
        mismas_llaves(self, s, ejemplo("CapacidadSimulacion.ok"), opcionales=("capacidad_fisica",))
        self.assertGreater(s["diferencia_capacidad_dia"], 0)
        self.assertLessEqual(s["escenario"]["utilizacion_pct"], s["actual"]["utilizacion_pct"])
        self.assertEqual(s["escenario"]["operadores"], 6)
        self.assertEqual(sorted(s["valores_modificados"]), ["capacidad_fisica", "operadores", "repartidores"])
        _, igual = self.adm.llamar("capacidad", "POST", "capacidad/simulaciones", base, estado=200)
        self.assertEqual(igual["diferencia_capacidad_dia"], 0)
        self.assertEqual(self.http(self.adm, "capacidad", "POST", "capacidad/simulaciones", {"pedidos_dia": 10}), 422)
        self.assertEqual(self.http(self.adm, "capacidad", "POST", "capacidad/simulaciones", {**base, "operadores": 0}), 422)
        self.assertEqual(self.http(self.op2, "capacidad", "POST", "capacidad/simulaciones", base), 403)
        self.plan_xml.llamar("capacidad", "POST", "capacidad/simulaciones", xml("capacidad_simulacion_nueva", {**base, "operadores": 4}), estado=200)

    def test_curva_de_carga_y_punto_de_saturacion(self):
        _, c = self.adm.llamar("capacidad", "GET", f"capacidad/cargas?microhub_id={self.HUB1}", estado=200)
        mismas_llaves(self, c, ejemplo("CapacidadCargas.ok"))
        util = [f["utilizacion_pct"] for f in c["filas"]]
        self.assertEqual(util, sorted(util))
        self.assertAlmostEqual(c["carga_en_riesgo"], c["capacidad_dia"] * 0.85, delta=1.0)
        self.assertLess(c["carga_estable"], c["carga_en_riesgo"])
        self.assertEqual(self.http(self.adm, "capacidad", "GET", "capacidad/cargas"), 400)
        self.ambos_formatos("capacidad", f"capacidad/cargas?microhub_id={self.HUB1}")

    def test_colas_mm1_y_mmc(self):
        _, r = self.plan.llamar("capacidad", "POST", "capacidad/colas", {"llegadas_hora": 10, "servicio_hora": 4, "servidores": 3,
                                                                         "espera_objetivo_min": 5}, estado=200)
        mismas_llaves(self, r, ejemplo("ColaCalculo.ok"), opcionales=("microhub",))
        self.assertEqual((r["modelo"], r["servidores_requeridos"], r["origen"]), ("M/M/c", 4, "indicado"))
        self.assertAlmostEqual(r["wq_min"], 21.067, places=2)
        _, uno = self.plan.llamar("capacidad", "POST", "capacidad/colas", {"llegadas_hora": 8, "servicio_hora": 10, "servidores": 1}, estado=200)
        self.assertEqual(uno["modelo"], "M/M/1")
        self.assertAlmostEqual(uno["wq_min"], 24.0)
        _, hub = self.op1.llamar("capacidad", "POST", "capacidad/colas", {"microhub_id": self.HUB1, "llegadas_hora": 12}, estado=200)
        self.assertEqual((hub["origen"], hub["microhub"]["id"]), ("microhub", self.HUB1))
        self.assertGreater(hub["servicio_hora"], 0)
        _, lleno = self.plan.llamar("capacidad", "POST", "capacidad/colas", {"llegadas_hora": 30, "servicio_hora": 4, "servidores": 3}, estado=200)
        self.assertFalse(lleno["estable"])
        self.assertIsNone(lleno["wq_min"])
        self.assertGreaterEqual(lleno["servidores_requeridos"], 8)
        self.assertEqual(self.http(self.plan, "capacidad", "POST", "capacidad/colas", {"llegadas_hora": 5}), 422)
        self.assertEqual(self.http(self.op2, "capacidad", "POST", "capacidad/colas", {"microhub_id": self.HUB1}), 403)
        self.assertEqual(self.http(self.cli, "capacidad", "POST", "capacidad/colas", {"llegadas_hora": 5, "servicio_hora": 4, "servidores": 2}), 403)
        _, (raiz, x) = self.plan_xml.llamar("capacidad", "POST", "capacidad/colas", xml("cola_calculo_nuevo", {"llegadas_hora": 10, "servicio_hora": 4,
                                                                                                           "servidores": 3}), estado=200)
        self.assertEqual(raiz, "cola_calculo")

    def test_supuestos_documentados(self):
        _, s = self.adm.llamar("capacidad", "GET", "capacidad/supuestos", estado=200)
        mismas_llaves(self, s, ejemplo("SupuestosCapacidad.ok"))
        self.assertTrue({"picking_pedidos_hora", "umbral_utilizacion_riesgo", "horas_turno"} <= {x["clave"] for x in s["datos"]})


# ====================================================================
# Costos
# ====================================================================
class T5Costos(Base):
    def test_conceptos_del_microhub_incluyen_los_globales(self):
        _, c = self.adm.llamar("costos", "GET", f"costos/conceptos?microhub_id={self.HUB1}&por_pagina=100", estado=200)
        mismas_llaves(self, c, ejemplo("ConceptoCostoLista.ok"), opcionales=("ambito_id", "vigente_hasta"))
        ambitos = {x["ambito"] for x in c["datos"]}
        self.assertEqual(ambitos, {"global", "microhub"})
        self.assertTrue(all(x["ambito_id"] in (None, self.HUB1) for x in c["datos"]))
        self.assertTrue(all(x["tipo"] == "fijo" and x["unidad"] == "mes" or x["tipo"] == "variable" and x["unidad"] != "mes" for x in c["datos"]))
        self.assertEqual(self.http(self.op1, "costos", "GET", "costos/conceptos"), 403)
        self.assertEqual(self.http(self.aud, "costos", "GET", "costos/conceptos"), 200)
        self.assertEqual(self.http(self.adm, "costos", "GET", "costos/conceptos?microhub_id=1&candidato_id=1"), 400)
        self.ambos_formatos("costos", f"costos/conceptos?microhub_id={self.HUB1}&por_pagina=5")

    def test_resumen_suma_los_fijos_y_separa_los_variables(self):
        _, r = self.adm.llamar("costos", "GET", f"costos/resumen?microhub_id={self.HUB1}", estado=200)
        mismas_llaves(self, r, ejemplo("ResumenCostos.ok"), opcionales=("ambito_id",))
        self.assertAlmostEqual(r["fijos_mes"], sum(c["monto"] for c in r["por_categoria"]), delta=0.05)
        _, lista = self.adm.llamar("costos", "GET", f"costos/conceptos?microhub_id={self.HUB1}&por_pagina=100", estado=200)
        fijos = sum(x["monto"] for x in lista["datos"] if x["tipo"] == "fijo" and x["estatus"] == "activo")
        self.assertAlmostEqual(r["fijos_mes"], fijos, delta=0.05)
        self.assertGreater(r["variable_entrega"], 0)
        _, g = self.adm.llamar("costos", "GET", "costos/resumen", estado=200)
        self.assertEqual(g["ambito"], "global")
        self.assertLess(g["fijos_mes"], r["fijos_mes"])
        self.ambos_formatos("costos", f"costos/resumen?microhub_id={self.HUB1}")

    def test_costo_unitario_cuadra_con_la_formula(self):
        costos = sys.modules["costos.app"]
        _, r = self.adm.llamar("costos", "GET", f"costos/resumen?microhub_id={self.HUB1}", estado=200)
        _, u = self.adm.llamar("costos", "GET", f"costos/unitarios?microhub_id={self.HUB1}&pedidos_mes=1000&ticket=150&distancia_km=2.4", estado=200)
        mismas_llaves(self, u, ejemplo("CostosUnitarios.ok"), opcionales=("ambito_id",))
        esperado = costos.unitarios({"fijos_mes": r["fijos_mes"], "variable_pedido": r["variable_pedido"], "variable_entrega": r["variable_entrega"],
                                     "variable_km": r["variable_km"], "comision_pct": r["comision_pct"]}, 1000, 150, 2.4, u["entrada"]["paradas_por_viaje"])
        self.assertAlmostEqual(u["costo_por_pedido"], esperado["costo_por_pedido"], delta=0.02)
        self.assertAlmostEqual(u["costo_fijo_pedido"], r["fijos_mes"] / 1000, delta=0.02)
        self.assertEqual(sorted(u["entrada"]["valores_modificados"]), ["distancia_km", "pedidos_mes", "ticket"])
        self.assertEqual(self.http(self.adm, "costos", "GET", f"costos/unitarios?microhub_id={self.HUB1}&pedidos_mes=0"), 400)
        self.ambos_formatos("costos", f"costos/unitarios?microhub_id={self.HUB1}")

    def test_mas_pedidos_diluyen_el_costo_fijo(self):
        _, poco = self.adm.llamar("costos", "GET", f"costos/unitarios?microhub_id={self.HUB1}&pedidos_mes=500", estado=200)
        _, mucho = self.adm.llamar("costos", "GET", f"costos/unitarios?microhub_id={self.HUB1}&pedidos_mes=3000", estado=200)
        self.assertGreater(poco["costo_por_pedido"], mucho["costo_por_pedido"])
        self.assertEqual(poco["costo_variable_pedido"], mucho["costo_variable_pedido"])

    def test_rentabilidad_y_sensibilidad(self):
        _, r = self.adm.llamar("costos", "GET", f"costos/rentabilidad?microhub_id={self.HUB1}&pedidos_mes=1500", estado=200)
        mismas_llaves(self, r, ejemplo("Rentabilidad.ok"), opcionales=("ambito_id",))
        self.assertAlmostEqual(r["utilidad_mes"], r["margen_contribucion_mes"] - r["costos_fijos_mes"], delta=0.05)
        self.assertEqual(r["cubre_costos"], r["utilidad_mes"] >= 0)
        _, s = self.adm.llamar("costos", "GET", f"costos/sensibilidad?microhub_id={self.HUB1}&pedidos_mes=1500", estado=200)
        mismas_llaves(self, s, ejemplo("SensibilidadCostos.ok"), opcionales=("ambito_id",))
        palancas = {f["palanca"] for f in s["filas"]}
        self.assertEqual(len(s["filas"]), len(palancas) * 4)
        self.assertIn(s["palanca_mas_sensible"], palancas)
        self.assertEqual(sorted({f["cambio_pct"] for f in s["filas"]}), [-20, -10, 10, 20])
        self.ambos_formatos("costos", f"costos/rentabilidad?microhub_id={self.HUB1}")
        self.ambos_formatos("costos", f"costos/sensibilidad?microhub_id={self.HUB1}")

    def test_alta_cambio_y_baja_de_un_concepto(self):
        cuerpo = {"ambito": "microhub", "ambito_id": self.HUB1, "nombre": "Prueba de vigilancia", "categoria": "servicios", "tipo": "fijo", "unidad": "mes",
                  "monto": 1234.5, "justificacion": "Concepto creado por la prueba automática"}
        try:
            self.assertEqual(self.http(self.aud, "costos", "POST", "costos/conceptos", cuerpo), 403)
            self.assertEqual(self.http(self.op1, "costos", "POST", "costos/conceptos", cuerpo), 403)
            _, base = self.adm.llamar("costos", "GET", f"costos/resumen?microhub_id={self.HUB1}", estado=200)
            r, c = self.plan.llamar("costos", "POST", "costos/conceptos", cuerpo, estado=201)
            mismas_llaves(self, c, ejemplo("ConceptoCosto.ok"), opcionales=("ambito_id", "vigente_hasta"))
            self.assertEqual((c["ambito"], c["monto"], c["estatus"]), ("microhub", 1234.5, "activo"))
            _, antes = self.adm.llamar("costos", "GET", f"costos/resumen?microhub_id={self.HUB1}", estado=200)
            self.assertAlmostEqual(antes["fijos_mes"] - base["fijos_mes"], 1234.5, delta=0.05)
            _, cambiado = self.plan.llamar("costos", "PUT", f"costos/conceptos/{c['id']}", {"monto": 2000, "justificacion": "Se corrigió el monto en la prueba"}, estado=200)
            self.assertEqual(cambiado["monto"], 2000)
            _, despues = self.adm.llamar("costos", "GET", f"costos/resumen?microhub_id={self.HUB1}", estado=200)
            self.assertAlmostEqual(despues["fijos_mes"] - antes["fijos_mes"], 2000 - 1234.5, delta=0.05)
            self.assertEqual(self.http(self.plan, "costos", "DELETE", f"costos/conceptos/{c['id']}"), 204)
            _, baja = self.adm.llamar("costos", "GET", f"costos/resumen?microhub_id={self.HUB1}", estado=200)
            self.assertAlmostEqual(baja["fijos_mes"], base["fijos_mes"], delta=0.05, msg="al dar de baja el concepto deja de contar")
            self.assertEqual(uno("SELECT estatus::text AS e FROM costo_concepto WHERE id = %s", (c["id"],))["e"], "inactivo", "baja lógica: el renglón se conserva")
            self.assertEqual(self.http(self.plan, "costos", "PUT", "costos/conceptos/999999", {"monto": 1}), 404)
        finally:
            ejecutar("DELETE FROM costo_concepto WHERE nombre = 'Prueba de vigilancia'")

    def test_validaciones_de_un_concepto(self):
        base = {"ambito": "global", "nombre": "Prueba inválida", "categoria": "otros", "tipo": "fijo", "unidad": "mes", "monto": 10, "justificacion": "Texto suficiente para pasar"}
        for cambio in ({"tipo": "variable"},                                  # un variable no puede ser «mes»
                       {"tipo": "fijo", "unidad": "pedido"},                  # un fijo es siempre «mes»
                       {"ambito": "microhub"},                                # falta ambito_id
                       {"ambito_id": 5},                                      # un global no lleva ambito_id
                       {"ambito": "microhub", "ambito_id": 99999},            # el microhub no existe
                       {"monto": -1}, {"categoria": "magia"}, {"justificacion": "corta"}, {"nombre": "ab"}, {"vigente_desde": "2026-12-01", "vigente_hasta": "2026-11-01"}):
            with self.subTest(cambio):
                self.assertIn(self.http(self.plan, "costos", "POST", "costos/conceptos", {**base, **cambio}), (404, 422))
        self.assertEqual(uno("SELECT count(*) AS n FROM costo_concepto WHERE nombre = 'Prueba inválida'")["n"], 0)

    def test_alta_en_xml(self):
        cuerpo = {"ambito": "global", "nombre": "Prueba XML de costo", "categoria": "otros", "tipo": "fijo", "unidad": "mes", "monto": 10,
                  "justificacion": "Concepto creado por la prueba XML"}
        try:
            _, (raiz, c) = self.plan_xml.llamar("costos", "POST", "costos/conceptos", xml("concepto_costo_nuevo", cuerpo), estado=201)
            self.assertEqual(raiz, "concepto_costo")
            self.assertEqual(c["nombre"], "Prueba XML de costo")
        finally:
            ejecutar("DELETE FROM costo_concepto WHERE nombre = 'Prueba XML de costo'")

    def test_costos_de_una_ubicacion_candidata(self):
        _, cands = self.adm.llamar("cobertura", "GET", "cobertura/candidatos", estado=200)
        cid = cands["datos"][0]["candidato"]["id"]
        _, r = self.adm.llamar("costos", "GET", f"costos/resumen?candidato_id={cid}", estado=200)
        self.assertEqual(r["ambito"], "candidato")
        self.assertGreater(r["fijos_mes"], 0, "toma renta, nómina y servicios de la ubicación candidata")
        with Apagado("planeacion"):
            self.assertEqual(self.http(self.adm, "costos", "GET", f"costos/resumen?candidato_id={cid}"), 503)
        self.assertEqual(self.http(self.adm, "costos", "GET", "costos/resumen?candidato_id=99999"), 404)

    def test_supuestos_documentados(self):
        _, s = self.adm.llamar("costos", "GET", "costos/supuestos", estado=200)
        mismas_llaves(self, s, ejemplo("SupuestosCostos.ok"))
        claves = {x["clave"] for x in s["datos"]}
        self.assertTrue({"cos_pedidos_mes_ref", "paradas_por_viaje"} <= claves)
        self.assertFalse({"costo_km_reparto", "costo_base_entrega"} & claves, "esos dos son de rutas y cobertura; costos guarda los suyos como conceptos")


# ====================================================================
# Punto de equilibrio
# ====================================================================
class T6PuntoDeEquilibrio(Base):
    ESCENARIO_A = {"pedidos_dia": 45, "ticket": 135, "margen_bruto": 0.28, "costos_fijos": 60000, "costo_variable_pedido": 32.6}

    def test_el_escenario_a_de_la_retroalimentacion(self):
        _, e = self.adm.llamar("punto-equilibrio", "POST", "punto-equilibrio/calculos", self.ESCENARIO_A, estado=200)
        mismas_llaves(self, e, ejemplo("EquilibrioCalculo.ok"), opcionales=("id", "nombre"))
        self.assertAlmostEqual(e["margen_pedido"], 5.2, places=2)
        self.assertAlmostEqual(e["equilibrio_mensual"], 60000 / 5.2, delta=0.01)
        self.assertAlmostEqual(e["equilibrio_diario"], 60000 / 5.2 / 30, delta=0.01)
        self.assertEqual(e["decision"], "no_viable")
        self.assertAlmostEqual(e["utilidad_mes"], 5.2 * 45 * 30 - 60000, delta=0.05)
        self.assertTrue(e["pasos"] and e["explicacion"])
        self.assertEqual({v for v in e["entrada"]["origen"].values()}, {"manual"})
        self.assertEqual(e["objeto"]["tipo"], "manual")
        self.assertEqual([s for s in e["supuestos_usados"] if s["modificado"]], [])

    def test_viable_viable_ajustado_y_no_viable(self):
        base = {"ticket": 150, "margen_bruto": 0.30, "costos_fijos": 40000, "costo_variable_pedido": 20}
        decisiones = {}
        for pedidos in (70, 55, 40):
            _, e = self.adm.llamar("punto-equilibrio", "POST", "punto-equilibrio/calculos", {**base, "pedidos_dia": pedidos}, estado=200)
            decisiones[pedidos] = e["decision"]
        self.assertEqual(decisiones, {70: "viable", 55: "viable_ajustado", 40: "no_viable"})

    def test_un_microhub_toma_sus_datos_de_costos_y_demanda(self):
        _, e = self.adm.llamar("punto-equilibrio", "POST", "punto-equilibrio/calculos", {"microhub_id": self.HUB1}, estado=200)
        o = e["entrada"]["origen"]
        self.assertEqual((o["costos_fijos"], o["costo_variable_pedido"], o["pedidos_dia"]), ("costos", "costos", "demanda_repartida"))
        self.assertIn(o["ticket"], ("demanda", "referencia"))
        _, r = self.adm.llamar("costos", "GET", f"costos/resumen?microhub_id={self.HUB1}", estado=200)
        self.assertEqual(e["entrada"]["costos_fijos_mes"], r["fijos_mes"])
        self.assertEqual(e["objeto"], {"tipo": "microhub", "id": self.HUB1, "nombre": e["objeto"]["nombre"]})
        _, otro = self.adm.llamar("punto-equilibrio", "POST", "punto-equilibrio/calculos", {"microhub_id": self.HUB1, "ticket": 200}, estado=200)
        self.assertEqual(otro["entrada"]["origen"]["ticket"], "manual")
        self.assertEqual(otro["entrada"]["ticket"], 200)
        self.assertGreater(otro["margen_pedido"], e["margen_pedido"])
        self.assertEqual(self.http(self.adm, "punto-equilibrio", "POST", "punto-equilibrio/calculos", {"microhub_id": 99999}), 404)
        self.assertEqual(self.http(self.adm, "punto-equilibrio", "POST", "punto-equilibrio/calculos", {"microhub_id": 1, "candidato_id": 1}), 422)
        self.assertEqual(self.http(self.adm, "punto-equilibrio", "POST", "punto-equilibrio/calculos", {"pedidos_dia": 10}), 422)

    def test_el_equilibrio_de_una_ubicacion_candidata(self):
        _, cands = self.adm.llamar("cobertura", "GET", "cobertura/candidatos", estado=200)
        cid = cands["datos"][0]["candidato"]["id"]
        _, e = self.adm.llamar("punto-equilibrio", "POST", "punto-equilibrio/calculos", {"candidato_id": cid}, estado=200)
        self.assertEqual(e["objeto"]["tipo"], "candidato")
        self.assertEqual(e["entrada"]["origen"]["pedidos_dia"], "demanda_repartida")

    def test_sin_los_servicios_de_apoyo_solo_sirve_lo_manual(self):
        with Apagado("costos"):
            self.error(self.adm, "punto-equilibrio", "POST", "punto-equilibrio/calculos", {"microhub_id": self.HUB1}, 503, "SERVICIO_NO_DISPONIBLE")
            self.assertEqual(self.http(self.adm, "punto-equilibrio", "POST", "punto-equilibrio/calculos",
                                       {**self.ESCENARIO_A}), 200, "con todos los datos escritos no depende de nadie")
        with Apagado("demanda"):
            self.assertEqual(self.http(self.adm, "punto-equilibrio", "POST", "punto-equilibrio/calculos", {"microhub_id": self.HUB1}), 503)

    def test_sensibilidad_ordena_las_variables(self):
        _, s = self.adm.llamar("punto-equilibrio", "POST", "punto-equilibrio/sensibilidad", {**self.ESCENARIO_A, "ticket": 150}, estado=200)
        mismas_llaves(self, s, ejemplo("EquilibrioSensibilidad.ok"), opcionales=("equilibrio_diario",))
        self.assertEqual(len(s["filas"]), 20)
        rangos = [r["rango_utilidad_mes"] for r in s["ranking"]]
        self.assertEqual(rangos, sorted(rangos, reverse=True))
        self.assertEqual(s["variable_mas_sensible"], s["ranking"][0]["etiqueta"])
        self.assertEqual({r["variable"] for r in s["ranking"]}, {"ticket", "pedidos_dia", "costos_fijos", "costo_variable_pedido", "margen_bruto"})
        self.plan_xml.llamar("punto-equilibrio", "POST", "punto-equilibrio/sensibilidad", xml("equilibrio_sensibilidad_nueva", {"microhub_id": self.HUB1}), estado=200)

    def test_guardar_comparar_y_borrar_escenarios(self):
        nombres = ("Prueba equilibrio A", "Prueba equilibrio B")
        ids = []
        try:
            self.assertEqual(self.http(self.aud, "punto-equilibrio", "POST", "punto-equilibrio/calculos", {**self.ESCENARIO_A, "guardar": True}), 403)
            for nombre, pedidos in zip(nombres, (45, 80)):
                _, e = self.plan.llamar("punto-equilibrio", "POST", "punto-equilibrio/calculos",
                                        {**self.ESCENARIO_A, "ticket": 150, "pedidos_dia": pedidos, "guardar": True, "nombre": nombre}, estado=201)
                ids.append(e["id"])
            _, lista = self.adm.llamar("punto-equilibrio", "GET", "punto-equilibrio/escenarios?por_pagina=100", estado=200)
            mismas_llaves(self, lista, ejemplo("EquilibrioEscenarioLista.ok"), opcionales=("microhub_id", "candidato_id"))
            self.assertTrue(set(ids) <= {x["id"] for x in lista["datos"]})
            _, uno_ = self.adm.llamar("punto-equilibrio", "GET", f"punto-equilibrio/escenarios/{ids[0]}", estado=200)
            self.assertEqual(uno_["nombre"], nombres[0])
            self.assertTrue(uno_["pasos"])
            _, comp = self.adm.llamar("punto-equilibrio", "GET", f"punto-equilibrio/comparacion?ids={ids[0]},{ids[1]}", estado=200)
            mismas_llaves(self, comp, ejemplo("EquilibrioComparacion.ok"))
            self.assertEqual(comp["mejor_utilidad_id"], ids[1], "más pedidos por día deja más utilidad")
            self.assertEqual(self.http(self.adm, "punto-equilibrio", "GET", f"punto-equilibrio/comparacion?ids={ids[0]}"), 400)
            self.assertEqual(self.http(self.aud, "punto-equilibrio", "DELETE", f"punto-equilibrio/escenarios/{ids[0]}"), 403)
            self.assertEqual(self.http(self.plan, "punto-equilibrio", "DELETE", f"punto-equilibrio/escenarios/{ids[0]}"), 204)
            self.assertEqual(self.http(self.adm, "punto-equilibrio", "GET", f"punto-equilibrio/escenarios/{ids[0]}"), 404)
            self.assertEqual(self.http(self.plan, "punto-equilibrio", "DELETE", f"punto-equilibrio/escenarios/{ids[0]}"), 404)
        finally:
            ejecutar("DELETE FROM equilibrio_escenario WHERE nombre = ANY(%s)", (list(nombres),))

    def test_equilibrio_de_todos_los_microhubs(self):
        _, m = self.adm.llamar("punto-equilibrio", "GET", "punto-equilibrio/microhubs", estado=200)
        mismas_llaves(self, m, ejemplo("EquilibrioMicrohubs.ok"), opcionales=("equilibrio_diario", "diferencia_pedidos_dia"))
        activos = uno("SELECT count(*) AS n FROM microhub WHERE estatus = 'activo'")["n"]
        self.assertEqual(len(m["datos"]), activos)
        self.assertTrue(all(f["decision"] in ("viable", "viable_ajustado", "no_viable") for f in m["datos"]))
        self.ambos_formatos("punto-equilibrio", "punto-equilibrio/microhubs")

    def test_xml_de_entrada_y_de_salida(self):
        cuerpo = xml("equilibrio_calculo_nuevo", {"pedidos_dia": 45, "ticket": 135, "margen_bruto": 0.28, "costos_fijos": 60000, "costo_variable_pedido": 32.6})
        _, (raiz, e) = self.plan_xml.llamar("punto-equilibrio", "POST", "punto-equilibrio/calculos", cuerpo, estado=200)
        self.assertEqual(raiz, "equilibrio_calculo")
        self.assertEqual(e["decision"], "no_viable")

    def test_supuestos_documentados(self):
        _, s = self.adm.llamar("punto-equilibrio", "GET", "punto-equilibrio/supuestos", estado=200)
        mismas_llaves(self, s, ejemplo("SupuestosEquilibrio.ok"))
        self.assertTrue({"peq_margen_seguridad_pct", "margen_bruto_default"} <= {x["clave"] for x in s["datos"]})


# ====================================================================
# Surtido
# ====================================================================
class T7Surtido(Base):
    def test_clasificacion_abc(self):
        _, a = self.adm.llamar("surtido", "GET", f"surtido/abc?microhub_id={self.HUB1}", estado=200)
        mismas_llaves(self, a, ejemplo("SurtidoAbc.ok"))
        self.assertEqual([c["clase"] for c in a["clases"]], ["A", "B", "C"])
        self.assertEqual(sum(c["productos"] for c in a["clases"]), len(a["filas"]))
        self.assertAlmostEqual(sum(c["pct_unidades"] for c in a["clases"]), 100.0, delta=0.5)
        acum = [f["pct_acum"] for f in a["filas"] if f["unidades"] > 0]
        self.assertEqual(acum, sorted(acum), "el acumulado solo crece")
        # los A son los primeros y acumulan alrededor de 80 % de las unidades
        self.assertEqual({f["clase"] for f in a["filas"][:3]}, {"A"})
        self.assertGreaterEqual(a["clases"][0]["pct_unidades"], 70)
        self.ambos_formatos("surtido", f"surtido/abc?microhub_id={self.HUB1}")

    def test_toda_la_red_sin_restricciones(self):
        _, red = self.adm.llamar("surtido", "GET", "surtido/analisis", estado=200)
        self.assertIsNone(red["microhub"])
        self.assertIsNone(red["resumen"]["espacio"]["total"])
        self.assertIsNone(red["resumen"]["presupuesto"]["total"])
        self.ambos_formatos("surtido", "surtido/analisis")

    def test_analisis_con_recomendacion_por_producto(self):
        _, a = self.adm.llamar("surtido", "GET", f"surtido/analisis?microhub_id={self.HUB1}", estado=200)
        mismas_llaves(self, a, ejemplo("SurtidoAnalisis.ok"))
        activos = uno("SELECT count(*) AS n FROM producto WHERE estatus = 'activo'")["n"]
        self.assertEqual(a["resumen"]["productos"], activos)
        self.assertEqual(len(a["filas"]), activos)
        r = a["resumen"]
        self.assertEqual(r["aumentar"] + r["mantener"] + r["reducir"] + r["eliminar"] + r["excluir"], activos)
        self.assertEqual(r["clase_a"] + r["clase_b"] + r["clase_c"], activos)
        for f in a["filas"]:
            self.assertIn(f["recomendacion"], ("Aumentar", "Mantener", "Reducir", "Eliminar", "Excluir"))
            if f["recomendacion"] != "Aumentar":
                self.assertEqual(f["sugerido"], 0)
            self.assertAlmostEqual(f["margen_total"], round(f["margen_unitario"] * f["unidades"], 2), delta=0.05)
        self.assertEqual(r["unidades_a_comprar"], sum(f["sugerido"] for f in a["filas"]))
        _, solo_a = self.adm.llamar("surtido", "GET", f"surtido/analisis?microhub_id={self.HUB1}&clase=A", estado=200)
        self.assertTrue(solo_a["filas"] and {f["clase"] for f in solo_a["filas"]} == {"A"})
        _, solo_r = self.adm.llamar("surtido", "GET", f"surtido/analisis?microhub_id={self.HUB1}&recomendacion=Reducir", estado=200)
        self.assertEqual({f["recomendacion"] for f in solo_r["filas"]} - {"Reducir"}, set())
        self.assertEqual(self.http(self.adm, "surtido", "GET", f"surtido/analisis?microhub_id={self.HUB1}&clase=Z"), 400)

    def test_el_espacio_y_el_presupuesto_limitan_lo_que_se_sugiere(self):
        antes = uno("SELECT espacio_total, presupuesto FROM surtido_restriccion WHERE microhub_id = %s", (self.HUB1,))
        producto = uno("SELECT producto_id FROM inventario WHERE microhub_id = %s ORDER BY producto_id LIMIT 1", (self.HUB1,))["producto_id"]
        orig = uno("SELECT existencia, minimo FROM inventario WHERE microhub_id = %s AND producto_id = %s", (self.HUB1, producto))
        try:
            ejecutar("UPDATE inventario SET existencia = 0, minimo = 10 WHERE microhub_id = %s AND producto_id = %s", (self.HUB1, producto))
            ejecutar("UPDATE surtido_restriccion SET espacio_total = 100000, presupuesto = 100000000 WHERE microhub_id = %s", (self.HUB1,))
            _, holgado = self.adm.llamar("surtido", "GET", f"surtido/analisis?microhub_id={self.HUB1}", estado=200)
            self.assertGreater(holgado["resumen"]["unidades_a_comprar"], 0)
            limite = round(holgado["resumen"]["presupuesto"]["requerido"] / 2, 2)      # la mitad de lo que pide sin límite
            ejecutar("UPDATE surtido_restriccion SET presupuesto = %s WHERE microhub_id = %s", (limite, self.HUB1))
            _, justo = self.adm.llamar("surtido", "GET", f"surtido/analisis?microhub_id={self.HUB1}", estado=200)
            self.assertLessEqual(justo["resumen"]["presupuesto"]["requerido"], limite)
            self.assertLess(justo["resumen"]["unidades_a_comprar"], holgado["resumen"]["unidades_a_comprar"])
            self.assertTrue(any(f["limitado_por"] == "presupuesto" for f in justo["filas"]))
            self.assertTrue(any(f["recomendacion"] == "Excluir" for f in justo["filas"]) or justo["resumen"]["unidades_a_comprar"] > 0)
        finally:
            ejecutar("UPDATE inventario SET existencia = %s, minimo = %s WHERE microhub_id = %s AND producto_id = %s", (orig["existencia"], orig["minimo"], self.HUB1, producto))
            ejecutar("UPDATE surtido_restriccion SET espacio_total = %s, presupuesto = %s WHERE microhub_id = %s", (antes["espacio_total"], antes["presupuesto"], self.HUB1))

    def test_restricciones_se_consultan_y_se_cambian_con_permiso(self):
        antes = uno("SELECT espacio_total, presupuesto FROM surtido_restriccion WHERE microhub_id = %s", (self.HUB1,))
        ruta = f"surtido/restricciones/{self.HUB1}"
        try:
            _, r = self.adm.llamar("surtido", "GET", ruta, estado=200)
            mismas_llaves(self, r, ejemplo("SurtidoRestriccion.ok"))
            self.assertEqual(self.http(self.aud, "surtido", "PUT", ruta, {"espacio_total": 3000}), 403)
            self.assertEqual(self.http(self.op1, "surtido", "PUT", ruta, {"espacio_total": 3000}), 403)
            _, n = self.plan.llamar("surtido", "PUT", ruta, {"espacio_total": 3000, "presupuesto": None}, estado=200)
            self.assertEqual((n["espacio_total"], n["presupuesto"]), (3000.0, None))
            self.assertEqual(self.http(self.plan, "surtido", "PUT", ruta, {"espacio_total": 0}), 422)
            self.assertEqual(self.http(self.plan, "surtido", "PUT", "surtido/restricciones/99999", {"espacio_total": 10}), 404)
            self.plan_xml.llamar("surtido", "PUT", ruta, xml("surtido_restriccion_cambio", {"espacio_total": 3100}), estado=200)
            self.assertEqual(self.http(self.op1, "surtido", "GET", ruta), 200)
            self.assertEqual(self.http(self.op1, "surtido", "GET", f"surtido/restricciones/{self.HUB2}"), 403)
        finally:
            ejecutar("UPDATE surtido_restriccion SET espacio_total = %s, presupuesto = %s WHERE microhub_id = %s", (antes["espacio_total"], antes["presupuesto"], self.HUB1))

    def test_guardar_una_recomendacion_y_abrirla(self):
        antes = uno("SELECT count(*) AS n FROM surtido_recomendacion")["n"]
        try:
            self.assertEqual(self.http(self.aud, "surtido", "POST", "surtido/recomendaciones", {"microhub_id": self.HUB1}), 403)
            self.assertEqual(self.http(self.op1, "surtido", "POST", "surtido/recomendaciones", {"microhub_id": self.HUB1}), 403)
            _, rec = self.plan.llamar("surtido", "POST", "surtido/recomendaciones", {"microhub_id": self.HUB1, "nota": "Prueba Ola 2"}, estado=201)
            mismas_llaves(self, rec, ejemplo("SurtidoRecomendacion.ok"), opcionales=("nota",))
            self.assertEqual(uno("SELECT count(*) AS n FROM surtido_recomendacion")["n"], antes + 1)
            self.assertEqual(uno("SELECT count(*) AS n FROM surtido_recomendacion_linea WHERE recomendacion_id = %s", (rec["id"],))["n"], len(rec["lineas"]))
            _, lista = self.adm.llamar("surtido", "GET", "surtido/recomendaciones?por_pagina=100", estado=200)
            mismas_llaves(self, lista, ejemplo("SurtidoRecomendacionLista.ok"), opcionales=("nota",))
            self.assertIn(rec["id"], [f["id"] for f in lista["datos"]])
            _, igual = self.adm.llamar("surtido", "GET", f"surtido/recomendaciones/{rec['id']}", estado=200)
            self.assertEqual(igual["resumen"], rec["resumen"])
            self.assertEqual(igual["nota"], "Prueba Ola 2")
            self.assertEqual(self.http(self.op2, "surtido", "GET", f"surtido/recomendaciones/{rec['id']}"), 403, "el operador de otro microhub no la abre")
            self.assertEqual(self.http(self.adm, "surtido", "GET", "surtido/recomendaciones/99999999"), 404)
            self.plan_xml.llamar("surtido", "POST", "surtido/recomendaciones", xml("surtido_recomendacion_nueva", {"microhub_id": self.HUB1}), estado=201)
        finally:
            ejecutar("DELETE FROM surtido_recomendacion WHERE microhub_id = %s", (self.HUB1,))

    def test_un_operador_solo_analiza_su_microhub(self):
        self.assertEqual(self.http(self.op1, "surtido", "GET", f"surtido/analisis?microhub_id={self.HUB1}"), 200)
        self.assertEqual(self.http(self.op1, "surtido", "GET", f"surtido/analisis?microhub_id={self.HUB2}"), 403)
        _, propio = self.op1.llamar("surtido", "GET", "surtido/analisis", estado=200)
        self.assertEqual(propio["microhub"]["id"], self.HUB1, "sin indicar microhub se usa el suyo")
        self.assertEqual(self.http(self.cli, "surtido", "GET", "surtido/abc"), 403)

    def test_si_precios_no_responde_se_estima_el_costo(self):
        _, normal = self.adm.llamar("surtido", "GET", f"surtido/analisis?microhub_id={self.HUB1}", estado=200)
        with Apagado("precios"):
            _, sin = self.adm.llamar("surtido", "GET", f"surtido/analisis?microhub_id={self.HUB1}", estado=200)
        self.assertEqual(sin["resumen"]["con_costo_estimado"], sin["resumen"]["productos"])
        self.assertLessEqual(normal["resumen"]["con_costo_estimado"], sin["resumen"]["con_costo_estimado"])
        self.assertTrue(all(f["costo_estimado"] for f in sin["filas"]))

    def test_sin_inventario_pedidos_o_productos_no_hay_analisis(self):
        for servicio in ("inventario", "pedidos", "productos"):
            with self.subTest(servicio), Apagado(servicio):
                self.error(self.adm, "surtido", "GET", f"surtido/analisis?microhub_id={self.HUB1}", None, 503, "SERVICIO_NO_DISPONIBLE")

    def test_supuestos_documentados(self):
        _, s = self.adm.llamar("surtido", "GET", "surtido/supuestos", estado=200)
        mismas_llaves(self, s, ejemplo("SupuestosSurtido.ok"))
        self.assertTrue({"abc_a_pct", "abc_b_pct", "cobertura_dias_a", "ventana_analisis_dias"} <= {x["clave"] for x in s["datos"]})


# ====================================================================
# Rutas
# ====================================================================
class T8Rutas(Base):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.listos = preparar_listos.dejar_listos(6, microhub_id=microhub("MH-01"))        # los que ya hay cuentan
        if len(cls.listos) < 4:
            raise unittest.SkipTest("no se pudieron preparar pedidos listos")
        cls.ids = [p["pedido_id"] for p in cls.listos]

    @classmethod
    def tearDownClass(cls):
        planes = [f["id"] for f in todos(
            "SELECT pd.id FROM plan_despacho pd WHERE pd.microhub_id = %s AND NOT EXISTS "
            "(SELECT 1 FROM plan_ruta pr JOIN entrega e ON e.plan_ruta_id = pr.id WHERE pr.plan_despacho_id = pd.id)", (microhub("MH-01"),))]
        ejecutar("DELETE FROM plan_ruta_parada WHERE plan_ruta_id IN (SELECT id FROM plan_ruta WHERE plan_despacho_id = ANY(%s))", (planes,))
        ejecutar("DELETE FROM plan_ruta WHERE plan_despacho_id = ANY(%s)", (planes,))
        ejecutar("DELETE FROM plan_despacho WHERE id = ANY(%s)", (planes,))
        preparar_listos.retirar([p["pedido_id"] for p in cls.listos if p["nuevo"]])    # los que ya había se dejan como estaban

    def paradas(self, plan):
        return [x["pedido"]["id"] for r in plan["rutas"] for x in r["paradas"]]

    def test_se_listan_los_pedidos_listos(self):
        _, l = self.adm.llamar("pedidos", "GET", f"pedidos/listos?microhub_id={self.HUB1}&por_pagina=100", estado=200)
        mismas_llaves(self, l, ejemplo("PedidosListos.ok"))
        self.assertTrue(set(self.ids) <= {p["id"] for p in l["datos"]})
        self.assertTrue(all(p["latitud"] and p["longitud"] for p in l["datos"]))

    def test_cada_pedido_listo_queda_en_una_sola_ruta(self):
        antes = uno("SELECT count(*) AS n FROM plan_despacho WHERE microhub_id = %s", (self.HUB1,))["n"]
        r, p = self.plan.llamar("rutas", "POST", "rutas/planes", {"microhub_id": self.HUB1, "pedido_ids": self.ids}, estado=200)
        mismas_llaves(self, p, ejemplo("RutaPlan.ok"), opcionales=("id", "paradas_fuera_de_promesa"))
        self.assertIsNone(p["id"], "sin guardar no se crea nada")
        self.assertEqual(p["estado"], "calculo")
        self.assertEqual(sorted(self.paradas(p)), sorted(self.ids))
        self.assertEqual(p["sin_asignar"], [])
        self.assertEqual(p["total"]["paradas"], len(self.ids))
        self.assertAlmostEqual(p["total"]["distancia_km"], sum(r["distancia_km"] for r in p["rutas"]), delta=0.02)
        for ruta in p["rutas"]:
            self.assertLessEqual(len(ruta["paradas"]), 8)
            self.assertEqual([x["orden"] for x in ruta["paradas"]], list(range(1, len(ruta["paradas"]) + 1)))
            minutos = [x["minutos_acum"] for x in ruta["paradas"]]
            self.assertEqual(minutos, sorted(minutos))
            self.assertEqual(ruta["minutos"], minutos[-1])
        reps = [r["repartidor"]["id"] for r in p["rutas"]]
        self.assertEqual(len(reps), len(set(reps)), "un repartidor, una ruta")
        self.assertEqual(uno("SELECT count(*) AS n FROM plan_despacho WHERE microhub_id = %s", (self.HUB1,))["n"], antes, "calcular no guarda nada")

    def test_los_metodos_de_orden_y_el_exacto_nunca_pierde(self):
        km = {}
        for metodo in ("vecino", "2opt", "exacto"):
            _, p = self.plan.llamar("rutas", "POST", "rutas/planes", {"microhub_id": self.HUB1, "pedido_ids": self.ids, "repartidor_ids": [self.reps()[0]], "metodo": metodo}, estado=200)
            km[metodo] = p["total"]["distancia_km"]
        self.assertLessEqual(km["exacto"], km["2opt"] + 0.01)
        self.assertLessEqual(km["2opt"], km["vecino"] + 0.01)

    def reps(self):
        _, r = self.adm.llamar("entregas", "GET", "entregas/repartidores", estado=200)
        return [x["id"] for x in r["datos"]]

    def test_comparar_metodos_de_recorrido(self):
        _, c = self.plan.llamar("rutas", "POST", "rutas/comparaciones", {"microhub_id": self.HUB1, "pedido_ids": self.ids}, estado=200)
        mismas_llaves(self, c, ejemplo("RutaComparacion.ok"))
        self.assertEqual([f["metodo"] for f in c["filas"]], ["Orden de llegada", "Vecino más cercano", "Vecino más cercano + 2-opt", "TSP exacto"])
        self.assertEqual(c["filas"][0]["mejora_pct"], 0.0)
        mejor = min(c["filas"], key=lambda f: f["distancia_km"])
        self.assertEqual(c["mejor_metodo"], mejor["metodo"])
        self.assertGreaterEqual(min(f["mejora_pct"] for f in c["filas"]), 0.0)
        self.error(self.plan, "rutas", "POST", "rutas/comparaciones", {"microhub_id": self.HUB1, "pedido_ids": self.ids[:1]}, 422, "VALIDACION")
        self.plan_xml.llamar("rutas", "POST", "rutas/comparaciones", xml("ruta_comparacion_nueva", {"microhub_id": self.HUB1}), estado=200)

    def test_proponer_guardar_confirmar_y_dejar_las_rutas_en_la_base(self):
        _, p = self.plan.llamar("rutas", "POST", "rutas/planes", {"microhub_id": self.HUB1, "pedido_ids": self.ids, "guardar": True}, estado=201)
        pid = p["id"]
        self.assertEqual((p["estado"], p["version"]), ("propuesto", 1))
        self.assertEqual(uno("SELECT count(*) AS n FROM plan_ruta WHERE plan_despacho_id = %s", (pid,))["n"], 0, "una propuesta todavía no escribe rutas")
        _, lista = self.adm.llamar("rutas", "GET", f"rutas/planes?microhub_id={self.HUB1}&por_pagina=100", estado=200)
        mismas_llaves(self, lista, ejemplo("RutaPlanLista.ok"))
        self.assertIn(pid, [f["id"] for f in lista["datos"]])
        _, c = self.plan.llamar("rutas", "POST", f"rutas/planes/{pid}/confirmar", {}, estado=200)
        self.assertEqual(c["estado"], "confirmado")
        filas = todos("SELECT id, paradas, distancia_km FROM plan_ruta WHERE plan_despacho_id = %s", (pid,))
        self.assertEqual(len(filas), len(p["rutas"]))
        self.assertEqual(sum(f["paradas"] for f in filas), len(self.ids))
        n = uno("SELECT count(*) AS n FROM plan_ruta_parada WHERE plan_ruta_id = ANY(%s)", ([f["id"] for f in filas],))["n"]
        self.assertEqual(n, len(self.ids))
        self.error(self.plan, "rutas", "POST", f"rutas/planes/{pid}/confirmar", {}, 409, "CONFLICTO")
        self.error(self.plan, "rutas", "POST", f"rutas/planes/{pid}/cancelar", {}, 409, "CONFLICTO")
        _, g = self.adm.llamar("rutas", "GET", f"rutas/planes/{pid}", estado=200)
        self.assertEqual(g["estado"], "confirmado")

    def test_cancelar_un_plan_propuesto(self):
        _, p = self.plan.llamar("rutas", "POST", "rutas/planes", {"microhub_id": self.HUB1, "pedido_ids": self.ids, "guardar": True}, estado=201)
        _, c = self.plan.llamar("rutas", "POST", f"rutas/planes/{p['id']}/cancelar", {}, estado=200)
        self.assertEqual(c["estado"], "cancelado")
        self.error(self.plan, "rutas", "POST", f"rutas/planes/{p['id']}/confirmar", {}, 409, "CONFLICTO")
        self.assertEqual(self.http(self.adm, "rutas", "GET", "rutas/planes/99999999"), 404)

    def test_ajustes_ante_incidencias(self):
        _, p = self.plan.llamar("rutas", "POST", "rutas/planes", {"microhub_id": self.HUB1, "pedido_ids": self.ids, "guardar": True}, estado=201)
        pid, total = p["id"], len(self.ids)
        quitado = p["rutas"][0]["paradas"][0]["pedido"]["id"]
        _, q = self.plan.llamar("rutas", "POST", f"rutas/planes/{pid}/ajustes", {"tipo": "quitar_pedido", "pedido_id": quitado}, estado=200)
        self.assertEqual(q["total"]["paradas"], total - 1)
        self.assertNotIn(quitado, self.paradas(q))
        self.assertEqual(q["version"], 2)
        self.assertTrue(q["cambios"])
        _, a = self.plan.llamar("rutas", "POST", f"rutas/planes/{pid}/ajustes", {"tipo": "agregar_pedido", "pedido_id": quitado}, estado=200)
        self.assertEqual(a["total"]["paradas"], total)
        self.assertEqual(a["version"], 3)
        rep = a["rutas"][0]["repartidor"]["id"]
        _, t = self.plan.llamar("rutas", "POST", f"rutas/planes/{pid}/ajustes", {"tipo": "retraso", "repartidor_id": rep, "minutos": 90}, estado=200)
        self.assertIn("paradas_fuera_de_promesa", t)
        self.assertEqual(len(t["paradas_fuera_de_promesa"]), len(a["rutas"][0]["paradas"]), "con 90 minutos de retraso todas pasan de los 30 minutos")
        self.assertGreater(t["rutas"][0]["minutos"], a["rutas"][0]["minutos"])
        self.assertEqual(self.http(self.plan, "rutas", "POST", f"rutas/planes/{pid}/ajustes", {"tipo": "quitar_pedido", "pedido_id": 999999}), 404)
        self.assertEqual(self.http(self.plan, "rutas", "POST", f"rutas/planes/{pid}/ajustes", {"tipo": "agregar_pedido", "pedido_id": self.paradas(t)[0]}), 409)
        self.assertEqual(self.http(self.plan, "rutas", "POST", f"rutas/planes/{pid}/ajustes", {"tipo": "retraso", "minutos": 10}), 422)
        self.assertEqual(self.http(self.plan, "rutas", "POST", f"rutas/planes/{pid}/ajustes", {"tipo": "otro"}), 422)

    def test_ajustar_un_plan_confirmado_reescribe_las_rutas(self):
        _, p = self.plan.llamar("rutas", "POST", "rutas/planes", {"microhub_id": self.HUB1, "pedido_ids": self.ids, "guardar": True}, estado=201)
        self.plan.llamar("rutas", "POST", f"rutas/planes/{p['id']}/confirmar", {}, estado=200)
        quitado = self.paradas(p)[0]
        self.plan.llamar("rutas", "POST", f"rutas/planes/{p['id']}/ajustes", {"tipo": "quitar_pedido", "pedido_id": quitado}, estado=200)
        n = uno("SELECT coalesce(sum(paradas), 0)::int AS n FROM plan_ruta WHERE plan_despacho_id = %s", (p["id"],))["n"]
        self.assertEqual(n, len(self.ids) - 1)

    def test_los_pedidos_que_cambian_antes_de_confirmar_se_detectan(self):
        _, p = self.plan.llamar("rutas", "POST", "rutas/planes", {"microhub_id": self.HUB1, "pedido_ids": self.ids, "guardar": True}, estado=201)
        pedido = self.paradas(p)[0]
        listo = uno("SELECT listo_en FROM pedido WHERE id = %s", (pedido,))["listo_en"]
        ejecutar("UPDATE pedido SET listo_en = NULL WHERE id = %s", (pedido,))
        try:
            e = self.error(self.plan, "rutas", "POST", f"rutas/planes/{p['id']}/confirmar", {}, 409, "CONFLICTO")
            self.assertTrue(any(str(pedido) in d["mensaje"] for d in e["detalles"]))
        finally:
            ejecutar("UPDATE pedido SET listo_en = %s WHERE id = %s", (listo, pedido))

    def test_validaciones_y_permisos(self):
        self.assertEqual(self.http(self.plan, "rutas", "POST", "rutas/planes", {"microhub_id": self.HUB3}), 422, "no hay pedidos listos en ese microhub")
        self.assertEqual(self.http(self.plan, "rutas", "POST", "rutas/planes", {"microhub_id": self.HUB1, "pedido_ids": [999999]}), 422)
        self.assertEqual(self.http(self.plan, "rutas", "POST", "rutas/planes", {"microhub_id": self.HUB1, "repartidor_ids": [999999]}), 422)
        self.assertEqual(self.http(self.plan, "rutas", "POST", "rutas/planes", {"microhub_id": self.HUB1, "metodo": "magico"}), 422)
        self.assertEqual(self.http(self.plan, "rutas", "POST", "rutas/planes", {"microhub_id": 99999}), 404)
        self.assertEqual(self.http(self.plan, "rutas", "POST", "rutas/planes", {"microhub_id": self.HUB1, "pedido_ids": ["a"]}), 422)
        self.assertEqual(self.http(self.aud, "rutas", "POST", "rutas/planes", {"microhub_id": self.HUB1}), 403, "el auditor consulta, no planea")
        self.assertEqual(self.http(self.aud, "rutas", "GET", "rutas/planes"), 200)
        self.assertEqual(self.http(self.cli, "rutas", "GET", "rutas/planes"), 403)
        self.assertEqual(self.http(self.rep, "rutas", "POST", "rutas/planes", {"microhub_id": self.HUB1}), 403)

    def test_el_operador_planea_solo_su_microhub(self):
        self.assertEqual(self.http(self.op1, "rutas", "POST", "rutas/planes", {"microhub_id": self.HUB1, "pedido_ids": self.ids}), 200)
        self.assertEqual(self.http(self.op2, "rutas", "POST", "rutas/planes", {"microhub_id": self.HUB1, "pedido_ids": self.ids}), 403)
        _, p = self.plan.llamar("rutas", "POST", "rutas/planes", {"microhub_id": self.HUB1, "pedido_ids": self.ids, "guardar": True}, estado=201)
        self.assertEqual(self.http(self.op2, "rutas", "GET", f"rutas/planes/{p['id']}"), 403)
        self.assertEqual(self.http(self.op2, "rutas", "POST", f"rutas/planes/{p['id']}/confirmar", {}), 403)
        _, lista = self.op2.llamar("rutas", "GET", "rutas/planes?por_pagina=100", estado=200)
        self.assertNotIn(p["id"], [f["id"] for f in lista["datos"]])

    def test_xml_con_lista_de_pedidos(self):
        pedidos = "<pedido_ids>" + "".join(f"<id>{i}</id>" for i in self.ids[:3]) + "</pedido_ids>"
        cuerpo = f'<ruta_plan_nuevo xmlns="{NS}"><microhub_id>{self.HUB1}</microhub_id>{pedidos}<metodo>exacto</metodo></ruta_plan_nuevo>'
        _, (raiz, p) = self.plan_xml.llamar("rutas", "POST", "rutas/planes", cuerpo, estado=200)
        self.assertEqual(raiz, "ruta_plan")
        solo = f'<ruta_plan_nuevo xmlns="{NS}"><microhub_id>{self.HUB1}</microhub_id><pedido_ids><id>{self.ids[0]}</id></pedido_ids></ruta_plan_nuevo>'
        self.plan_xml.llamar("rutas", "POST", "rutas/planes", solo, estado=200)

    def test_sin_pedidos_o_entregas_no_hay_plan(self):
        with Apagado("pedidos"):
            self.error(self.plan, "rutas", "POST", "rutas/planes", {"microhub_id": self.HUB1}, 503, "SERVICIO_NO_DISPONIBLE")
        with Apagado("entregas"):
            self.error(self.plan, "rutas", "POST", "rutas/planes", {"microhub_id": self.HUB1}, 503, "SERVICIO_NO_DISPONIBLE")

    def test_supuestos_documentados(self):
        _, s = self.adm.llamar("rutas", "GET", "rutas/supuestos", estado=200)
        mismas_llaves(self, s, ejemplo("SupuestosRutas.ok"))
        self.assertTrue({"velocidad_reparto_kmh", "max_paradas_repartidor", "factor_rodeo_distancia"} <= {x["clave"] for x in s["datos"]})


# ====================================================================
# Simulación
# ====================================================================
class T9Simulacion(Base):
    creadas = set()

    @classmethod
    def tearDownClass(cls):
        if cls.creadas:
            ejecutar("DELETE FROM simulacion_ejecucion WHERE id = ANY(%s::uuid[])", (list(cls.creadas),))

    def crear(self, cliente=None, estado=202, **cuerpo):
        cuerpo = {"microhub_id": self.HUB1, "dias": 10, "replicas": 40, "semilla": 5, **cuerpo}
        r, e = (cliente or self.plan).llamar("simulacion", "POST", "simulacion/ejecuciones", cuerpo, estado=estado)
        if estado == 202:
            self.creadas.add(e["id"])
        return r, e

    def terminar(self, eid, esperado="terminada"):
        for _ in range(30):
            sim.procesar_pendientes()
            _, e = self.adm.llamar("simulacion", "GET", f"simulacion/ejecuciones/{eid}", estado=200)
            if e["estado"] in ("terminada", "fallida", "cancelada"):
                break
            time.sleep(0.3)
        self.assertEqual(e["estado"], esperado, e.get("error"))
        return e

    def test_se_encola_se_ejecuta_y_deja_resultados_con_huella(self):
        r, e = self.crear()
        mismas_llaves(self, e, ejemplo("SimulacionEjecucion.ok"), opcionales=("resultados", "huella", "repeticion_de", "reproducible", "error", "inicio_en", "fin_en"))
        self.assertIn(e["estado"], ("en_cola", "ejecutando"))
        self.assertTrue(r.headers["Location"].endswith(e["id"]))
        self.assertIsNone(e["resultados"])
        t = self.terminar(e["id"])
        self.assertEqual(len(t["huella"]), 64)
        res = t["resultados"]
        self.assertEqual((res["dias"], res["replicas"]), (10, 40))
        self.assertEqual([m["clave"] for m in res["metricas"]], ["utilidad", "ingreso", "atendidos", "rechazados", "utilizacion_pct", "dias_saturados"])
        for m in res["metricas"]:
            self.assertLessEqual(m["minimo"], m["p10"]); self.assertLessEqual(m["p10"], m["p50"]); self.assertLessEqual(m["p50"], m["p90"]); self.assertLessEqual(m["p90"], m["maximo"])
        self.assertEqual(len(res["serie"]), 10)
        self.assertTrue(res["lectura"])
        self.assertEqual(t["version_modelo"], sim.VERSION_MODELO)
        self.assertEqual(t["semilla"], 5)

    def test_la_entrada_queda_guardada_con_el_origen_de_cada_dato(self):
        _, e = self.crear(ticket=140)
        o = {x["dato"]: x["fuente"] for x in e["entrada"]["origen_de_datos"]}
        self.assertEqual(o["ticket"], "manual")
        self.assertEqual((o["costos_fijos"], o["operadores"], o["capacidad_fisica"]), ("costos", "capacidad", "capacidad"))
        self.assertEqual(e["entrada"]["ticket"], 140)
        self.assertEqual(len(e["entrada"]["indice_semanal"]), 7)
        self.assertIn(o["indice_semanal"], ("demanda", "plano_sin_historia"))
        self.terminar(e["id"])

    def test_misma_entrada_y_semilla_dan_la_misma_huella_y_otra_semilla_no(self):
        _, a = self.crear(semilla=77)
        a = self.terminar(a["id"])
        r, rep = self.plan.llamar("simulacion", "POST", f"simulacion/ejecuciones/{a['id']}/repetir", {}, estado=202)
        self.creadas.add(rep["id"])
        self.assertEqual(rep["repeticion_de"], a["id"])
        self.assertIsNone(rep["reproducible"], "mientras no termine no se sabe")
        b = self.terminar(rep["id"])
        self.assertEqual(b["huella"], a["huella"])
        self.assertIs(b["reproducible"], True)
        self.assertEqual(b["resultados"], a["resultados"])
        _, c = self.crear(semilla=78)
        c = self.terminar(c["id"])
        self.assertNotEqual(c["huella"], a["huella"])

    def test_la_foto_de_la_entrada_hace_reproducible_aunque_cambien_los_datos(self):
        _, a = self.crear(semilla=31)
        a = self.terminar(a["id"])
        antes = uno("SELECT operadores FROM capacidad_recurso WHERE microhub_id = %s", (self.HUB1,))["operadores"]
        try:
            ejecutar("UPDATE capacidad_recurso SET operadores = %s WHERE microhub_id = %s", (antes + 3, self.HUB1))
            _, rep = self.plan.llamar("simulacion", "POST", f"simulacion/ejecuciones/{a['id']}/repetir", {}, estado=202)
            self.creadas.add(rep["id"])
            b = self.terminar(rep["id"])
            self.assertEqual(b["huella"], a["huella"], "la repetición usa la entrada guardada, no los datos de hoy")
            _, nueva = self.crear(semilla=31)
            nueva = self.terminar(nueva["id"])
            self.assertNotEqual(nueva["huella"], a["huella"], "una ejecución nueva sí ve el personal nuevo")
        finally:
            ejecutar("UPDATE capacidad_recurso SET operadores = %s WHERE microhub_id = %s", (antes, self.HUB1))

    def test_escenario_manual_y_validaciones_de_la_entrada(self):
        completo = {"pedidos_dia": 45, "ticket": 135, "costos_fijos": 60000, "costo_variable_pedido": 32.6, "operadores": 3, "repartidores": 2, "dias": 10, "replicas": 30}
        _, e = self.plan.llamar("simulacion", "POST", "simulacion/ejecuciones", completo, estado=202)
        self.creadas.add(e["id"])
        self.assertEqual(e["objeto"]["tipo"], "manual")
        t = self.terminar(e["id"])
        self.assertEqual(t["resultados"]["prob_perdida_pct"], 100.0, "con el escenario A se pierde dinero en todas las réplicas")
        faltan = self.error(self.plan, "simulacion", "POST", "simulacion/ejecuciones", {"pedidos_dia": 45}, 422, "VALIDACION")
        self.assertTrue({"ticket", "costos_fijos", "operadores"} <= {d["campo"] for d in faltan["detalles"]})
        for cambio in ({"dias": 400}, {"replicas": 5}, {"semilla": -1}, {"ausentismo": 0.9}, {"microhub_id": 99999}, {"microhub_id": self.HUB1, "candidato_id": 1}):
            with self.subTest(cambio):
                self.assertIn(self.http(self.plan, "simulacion", "POST", "simulacion/ejecuciones", {**completo, **cambio}), (404, 422))
        self.assertEqual(self.http(self.plan, "simulacion", "POST", "simulacion/ejecuciones", {**completo, "dias": 365, "replicas": 2000}), 422, "demasiado trabajo")

    def test_una_ubicacion_candidata_necesita_su_personal(self):
        _, cands = self.adm.llamar("cobertura", "GET", "cobertura/candidatos", estado=200)
        cid = cands["datos"][0]["candidato"]["id"]
        self.assertEqual(self.http(self.plan, "simulacion", "POST", "simulacion/ejecuciones", {"candidato_id": cid}), 422)
        _, e = self.plan.llamar("simulacion", "POST", "simulacion/ejecuciones", {"candidato_id": cid, "operadores": 3, "repartidores": 2, "dias": 7, "replicas": 20}, estado=202)
        self.creadas.add(e["id"])
        self.assertEqual(e["objeto"]["tipo"], "candidato")
        self.terminar(e["id"])

    def test_cancelar(self):
        _, e = self.crear(dias=300, replicas=600)
        r, c = self.plan.llamar("simulacion", "POST", f"simulacion/ejecuciones/{e['id']}/cancelar", {}, estado=200)
        self.assertEqual(c["estado"], "cancelada")
        sim.procesar_pendientes()
        _, otra = self.adm.llamar("simulacion", "GET", f"simulacion/ejecuciones/{e['id']}", estado=200)
        self.assertEqual(otra["estado"], "cancelada", "una cancelada no se ejecuta")
        self.assertIsNone(otra["resultados"])
        self.error(self.plan, "simulacion", "POST", f"simulacion/ejecuciones/{e['id']}/cancelar", {}, 409, "CONFLICTO")
        self.error(self.plan, "simulacion", "POST", f"simulacion/ejecuciones/{e['id']}/repetir", {}, 409, "CONFLICTO")

    def test_una_terminada_no_se_cancela(self):
        _, e = self.crear()
        self.terminar(e["id"])
        self.error(self.plan, "simulacion", "POST", f"simulacion/ejecuciones/{e['id']}/cancelar", {}, 409, "CONFLICTO")

    def test_una_ejecucion_dañada_queda_fallida_con_su_motivo(self):
        _, buena = self.crear(dias=3, replicas=10)
        self.terminar(buena["id"])
        snap = uno("SELECT parametros FROM simulacion_ejecucion WHERE id = %s", (buena["id"],))["parametros"]
        snap["entrada"]["indice_semanal"] = []                     # sin índice semanal el modelo no puede correr
        eid = str(uuid.uuid4())
        self.creadas.add(eid)
        ejecutar("INSERT INTO simulacion_ejecucion (id, nombre, estado, semilla, version_modelo, parametros) VALUES (%s, 'dañada', 'en_cola', 1, '1.0', %s)",
                 (eid, json.dumps(snap)))
        e = self.terminar(eid, "fallida")
        self.assertIn("IndexError", e["error"])
        self.assertIsNone(e["resultados"])
        # y el trabajador sigue vivo: la siguiente ejecución corre normal
        _, otra = self.crear(dias=3, replicas=10)
        self.terminar(otra["id"])

    def test_una_ejecucion_abandonada_regresa_a_la_cola_y_luego_falla(self):
        _, e = self.crear(dias=3, replicas=10)
        self.terminar(e["id"])
        ejecutar("UPDATE simulacion_ejecucion SET estado = 'ejecutando', inicio_en = now() - interval '10 minutes', intentos = 1, resultados = NULL, huella = NULL WHERE id = %s", (e["id"],))
        sim.recuperar_abandonadas()
        self.assertEqual(uno("SELECT estado FROM simulacion_ejecucion WHERE id = %s", (e["id"],))["estado"], "en_cola")
        ejecutar("UPDATE simulacion_ejecucion SET estado = 'ejecutando', inicio_en = now() - interval '10 minutes', intentos = 3 WHERE id = %s", (e["id"],))
        sim.recuperar_abandonadas()
        f = uno("SELECT estado, error FROM simulacion_ejecucion WHERE id = %s", (e["id"],))
        self.assertEqual(f["estado"], "fallida")
        self.assertIn("intentos", f["error"])

    def test_una_ejecucion_reciente_en_curso_no_se_toca(self):
        _, e = self.crear(dias=3, replicas=10)
        self.terminar(e["id"])
        ejecutar("UPDATE simulacion_ejecucion SET estado = 'ejecutando', inicio_en = now(), intentos = 1 WHERE id = %s", (e["id"],))
        sim.recuperar_abandonadas()
        self.assertEqual(uno("SELECT estado FROM simulacion_ejecucion WHERE id = %s", (e["id"],))["estado"], "ejecutando")
        ejecutar("UPDATE simulacion_ejecucion SET estado = 'terminada' WHERE id = %s", (e["id"],))

    def test_listar_y_filtrar(self):
        _, e = self.crear(dias=3, replicas=10)
        self.terminar(e["id"])
        _, l = self.adm.llamar("simulacion", "GET", "simulacion/ejecuciones?por_pagina=100", estado=200)
        mismas_llaves(self, l, ejemplo("SimulacionLista.ok"), opcionales=("utilidad_media", "prob_perdida_pct", "huella", "fin_en"))
        self.assertIn(e["id"], [f["id"] for f in l["datos"]])
        _, t = self.adm.llamar("simulacion", "GET", "simulacion/ejecuciones?estado=terminada&por_pagina=100", estado=200)
        self.assertEqual({f["estado"] for f in t["datos"]}, {"terminada"})
        self.assertEqual(self.http(self.adm, "simulacion", "GET", "simulacion/ejecuciones?estado=inventado"), 400)
        self.assertEqual(self.http(self.adm, "simulacion", "GET", "simulacion/ejecuciones/no-es-uuid"), 404)
        self.assertEqual(self.http(self.adm, "simulacion", "GET", f"simulacion/ejecuciones/{uuid.uuid4()}"), 404)

    def test_comparar_ejecuciones_terminadas(self):
        _, a = self.crear(semilla=1)
        _, b = self.crear(semilla=2, operadores=6, repartidores=6)
        self.terminar(a["id"]); self.terminar(b["id"])
        _, c = self.adm.llamar("simulacion", "GET", f"simulacion/comparacion?ids={a['id']},{b['id']}", estado=200)
        mismas_llaves(self, c, ejemplo("SimulacionComparacion.ok"))
        self.assertEqual(len(c["ejecuciones"]), 2)
        self.assertIn(c["mejor_id"], (a["id"], b["id"]))
        _, pendiente = self.crear(dias=300, replicas=600)
        self.error(self.adm, "simulacion", "GET", f"simulacion/comparacion?ids={a['id']},{pendiente['id']}", None, 409, "CONFLICTO")
        self.plan.llamar("simulacion", "POST", f"simulacion/ejecuciones/{pendiente['id']}/cancelar", {}, estado=200)
        self.assertEqual(self.http(self.adm, "simulacion", "GET", f"simulacion/comparacion?ids={a['id']}"), 400)
        self.assertEqual(self.http(self.adm, "simulacion", "GET", f"simulacion/comparacion?ids={a['id']},{a['id']}"), 400)
        self.ambos_formatos("simulacion", f"simulacion/comparacion?ids={a['id']},{b['id']}")

    def test_permisos_por_perfil(self):
        self.assertEqual(self.http(self.aud, "simulacion", "GET", "simulacion/ejecuciones"), 403, "el auditor no tiene simulacion.ver")
        self.assertEqual(self.http(self.op1, "simulacion", "GET", "simulacion/ejecuciones"), 403)
        self.assertEqual(self.http(self.op1, "simulacion", "POST", "simulacion/ejecuciones", {"microhub_id": self.HUB1}), 403)
        self.assertEqual(self.http(self.cli, "simulacion", "GET", "simulacion/ejecuciones"), 403)
        self.assertEqual(self.http(Cliente(self, "json"), "simulacion", "GET", "simulacion/ejecuciones"), 401)

    def test_xml_de_entrada_y_de_salida(self):
        cuerpo = xml("simulacion_nueva", {"microhub_id": self.HUB1, "dias": 5, "replicas": 20, "semilla": 3})
        _, (raiz, e) = self.plan_xml.llamar("simulacion", "POST", "simulacion/ejecuciones", cuerpo, estado=202)
        self.creadas.add(e["id"])
        self.assertEqual(raiz, "simulacion_ejecucion")
        self.terminar(e["id"])
        _, (raiz, t) = self.adm_xml.llamar("simulacion", "GET", f"simulacion/ejecuciones/{e['id']}", estado=200)
        self.assertEqual(t["estado"], "terminada")
        self.adm_xml.llamar("simulacion", "GET", "simulacion/ejecuciones", estado=200)

    def test_si_falla_un_servicio_de_apoyo_no_se_encola_nada(self):
        antes = uno("SELECT count(*) AS n FROM simulacion_ejecucion")["n"]
        for servicio in ("punto-equilibrio", "capacidad", "costos"):
            with self.subTest(servicio), Apagado(servicio):
                self.error(self.plan, "simulacion", "POST", "simulacion/ejecuciones", {"microhub_id": self.HUB1}, 503, "SERVICIO_NO_DISPONIBLE")
        self.assertEqual(uno("SELECT count(*) AS n FROM simulacion_ejecucion")["n"], antes)

    def test_sin_el_servicio_de_demanda_el_patron_semanal_es_plano_y_se_dice(self):
        with Apagado("demanda"):
            r, e = self.plan.llamar("simulacion", "POST", "simulacion/ejecuciones", {"pedidos_dia": 30, "ticket": 135, "costos_fijos": 60000, "costo_variable_pedido": 30,
                                                                                    "operadores": 3, "repartidores": 3, "dias": 7, "replicas": 20}, estado=202)
        self.creadas.add(e["id"])
        self.assertEqual(e["entrada"]["indice_semanal"], [1.0] * 7)
        self.assertEqual({x["dato"]: x["fuente"] for x in e["entrada"]["origen_de_datos"]}["indice_semanal"], "plano_sin_servicio")
        self.terminar(e["id"])

    def test_supuestos_documentados(self):
        _, s = self.plan.llamar("simulacion", "GET", "simulacion/supuestos", estado=200)
        mismas_llaves(self, s, ejemplo("SupuestosSimulacion.ok"))
        self.assertTrue({"sim_ausentismo", "sim_replicas_defecto", "sim_semilla_defecto", "sim_variacion_demanda"} <= {x["clave"] for x in s["datos"]})


# ====================================================================
# Transversal: supuestos, auditoría y contrato
# ====================================================================
class T10Transversal(Base):
    SERVICIOS = ["demanda", "cobertura", "capacidad", "rutas", "costos", "punto-equilibrio", "simulacion", "surtido"]

    def test_todo_supuesto_dice_de_donde_sale_y_como_se_calibra(self):
        for s in self.SERVICIOS:
            with self.subTest(s):
                _, d = self.adm.llamar(s, "GET", f"{s}/supuestos", estado=200)
                self.assertTrue(d["datos"], "cada servicio publica sus supuestos")
                for x in d["datos"]:
                    self.assertIn(x["origen"], ("medido", "supuesto", "normativo"), x["clave"])
                    self.assertGreater(len(x["justificacion"]), 25, f"{x['clave']} sin justificación")
                    self.assertTrue(x["como_calibrar"], f"{x['clave']} sin forma de calibrarlo")

    def test_ningun_supuesto_numerico_esta_solo_en_el_codigo(self):
        """Los valores por omisión de cada servicio existen en la configuración (RN40): el código solo es el respaldo."""
        for modulo in ("demanda", "cobertura", "capacidad", "rutas", "costos", "punto_equilibrio", "simulacion", "surtido"):
            m = sys.modules[f"{modulo}.app"]
            claves = list(getattr(m, "DEFECTOS"))
            existen = {f["clave"] for f in todos("SELECT clave FROM configuracion WHERE ambito = 'global' AND clave = ANY(%s)", (claves,))}
            self.assertEqual(set(claves) - existen, set(), f"{modulo}: claves sin fila en configuracion")
            documentadas = {f["clave"] for f in todos("SELECT clave FROM supuesto_documentado WHERE clave = ANY(%s)", (claves,))}
            self.assertEqual(set(m.CLAVES_SUPUESTOS) - documentadas, set(), f"{modulo}: supuestos sin documentar")

    def test_el_valor_de_la_configuracion_manda_sobre_el_del_codigo(self):
        antes = uno("SELECT valor FROM configuracion WHERE clave = 'dem_penetracion' AND ambito = 'global'")["valor"]
        try:
            ejecutar("UPDATE configuracion SET valor = '0.2' WHERE clave = 'dem_penetracion' AND ambito = 'global'")
            _, p = self.adm.llamar("demanda", "GET", "demanda/potencial", estado=200)
            self.assertEqual(p["penetracion"], 0.2)
        finally:
            ejecutar("UPDATE configuracion SET valor = %s WHERE clave = 'dem_penetracion' AND ambito = 'global'", (antes,))

    def test_las_escrituras_dejan_rastro_en_la_auditoria(self):
        antes = uno("SELECT count(*) AS n FROM auditoria WHERE modulo = 'costos'")["n"]
        try:
            self.plan.llamar("costos", "POST", "costos/conceptos", {"ambito": "global", "nombre": "Prueba de auditoría", "categoria": "otros", "tipo": "fijo", "unidad": "mes",
                                                                     "monto": 1, "justificacion": "Concepto para comprobar la auditoría"}, estado=201)
            despues = uno("SELECT count(*) AS n FROM auditoria WHERE modulo = 'costos'")["n"]
            self.assertGreater(despues, antes)
        finally:
            ejecutar("DELETE FROM costo_concepto WHERE nombre = 'Prueba de auditoría'")

    def test_documentacion_y_salud_de_los_ocho_servicios(self):
        for s in self.SERVICIOS:
            with self.subTest(s):
                c = APPS[s].test_client()
                self.assertEqual(c.get("/api/v1/salud").status_code, 200)
                spec = c.get("/api/v1/openapi.json").get_json()
                self.assertGreaterEqual(len([1 for p in spec["paths"].values() for _ in p]), 5)
                self.assertIn(b"swagger-ui", c.get("/api/v1/docs").data)

    def test_cada_servicio_exige_sesion(self):
        sin = Cliente(self, "json")
        for s in self.SERVICIOS:
            with self.subTest(s):
                self.assertEqual(self.http(sin, s, "GET", f"{s}/supuestos"), 401)

    def test_el_cliente_no_entra_a_ningun_servicio_de_analisis(self):
        for s in self.SERVICIOS:
            with self.subTest(s):
                self.assertEqual(self.http(self.cli, s, "GET", f"{s}/supuestos"), 403)

    def test_error_estandar_con_traza(self):
        e = self.error(self.adm, "costos", "GET", "costos/resumen?microhub_id=99999", None, 404, "NO_ENCONTRADO")
        self.assertTrue(e["traza_id"])
        e = self.error(self.plan, "costos", "POST", "costos/conceptos", {"ambito": "global"}, 422, "VALIDACION")
        self.assertTrue(e["detalles"] and all("campo" in d and "mensaje" in d for d in e["detalles"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
