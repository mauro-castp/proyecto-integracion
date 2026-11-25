"""
test_ola3.py — Los servicios de la Ola 3: auditoría y monitoreo (5126), reportes (5123) y sincronización (5125), contra PostgreSQL, Redis
y MongoDB reales con el modelo 01 a 11 cargado.

Los servicios se llaman entre sí como en producción (mismo JWT, misma traza) pero en proceso. Una prueba puede «apagar» un servicio o hacerlo
responder degradado para ver qué hace el monitoreo. Cada prueba que cambia datos los deja como estaban.

  servicios/pruebas/correr.sh test pruebas.test_ola3 -v
"""
import base64
import datetime as dt
import json
import os
import sys
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
os.environ.setdefault("LOG_STDOUT", "0")
os.environ.setdefault("MONITOR_AUTO", "0")

from comun import clientes, config, datos  # noqa: E402
from pruebas.test_contrato import APPS, JPEG, Cliente, ejemplo, mismas_llaves, xml  # noqa: E402

mon = sys.modules["auditoria_monitoreo.app"]
APAGADOS = set()
DEGRADADOS = {}
LIMITE = {}


def transporte(servicio, metodo, ruta, cuerpo, params, token, traza):
    if servicio in APAGADOS:
        raise ConnectionError(f"{servicio} apagado por la prueba")
    if servicio in DEGRADADOS and ruta.strip("/") == "salud":
        return 503, {"servicio": servicio, "version": "1.0.0", "estado": "degradado", "dependencias": DEGRADADOS[servicio], "tiempo_ms": 1.0}
    enc = {"Accept": "application/json", "Content-Type": "application/json"}
    if token:
        enc["Authorization"] = f"Bearer {token}"
    if traza:
        enc["X-Traza-Id"] = traza
    r = APPS[servicio].test_client().open(f"/api/v1/{ruta}", method=metodo, query_string=params or None, headers=enc,
                                          data=json.dumps(cuerpo) if cuerpo is not None else None)
    return r.status_code, (r.get_json(silent=True) if r.data else None)


def uno(sql, args=()):
    return datos.consultar(sql, args, una=True)


def todos(sql, args=()):
    return datos.consultar(sql, args)


def ejecutar(sql, args=()):
    with datos.conexion() as con, con.cursor() as cur:
        cur.execute(sql, args)


def limpiar_monitoreo():
    ejecutar("DELETE FROM monitoreo_alerta")
    ejecutar("DELETE FROM monitoreo_verificacion")


def setUpModule():
    clientes.usar_transporte(transporte)
    LIMITE["antes"], LIMITE["login"] = config.LIMITE_POR_MINUTO, config.LIMITE_LOGIN_POR_MINUTO
    config.LIMITE_POR_MINUTO = config.LIMITE_LOGIN_POR_MINUTO = 1_000_000
    limpiar_monitoreo()


def tearDownModule():
    clientes.usar_transporte(None)
    config.LIMITE_POR_MINUTO, config.LIMITE_LOGIN_POR_MINUTO = LIMITE["antes"], LIMITE["login"]
    limpiar_monitoreo()


class Apagado:
    """with Apagado('inventario'): … — el servicio no responde dentro del bloque."""

    def __init__(self, *servicios):
        self.s = servicios

    def __enter__(self):
        APAGADOS.update(self.s)

    def __exit__(self, *a):
        APAGADOS.difference_update(self.s)


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._caso = unittest.TestCase()
        cls.adm = cls.entrar("admin@codex.mx")
        cls.aud = cls.entrar("auditor@codex.mx")
        cls.plan = cls.entrar("planeador@codex.mx")
        cls.op1 = cls.entrar("operador.mh01@codex.mx")
        cls.rep = cls.entrar("repartidor1@codex.mx")
        cls.cli = cls.entrar("juan.chapa1@correo.mx")
        cls.adm_xml = cls.entrar("admin@codex.mx", "xml")

    @classmethod
    def entrar(cls, correo, formato="json"):
        c = Cliente(cls._caso, formato)
        c.entrar(correo)
        return c

    def setUp(self):
        for c in (self.adm, self.aud, self.plan, self.op1, self.rep, self.cli, self.adm_xml):
            c.caso = self

    def ambos_formatos(self, servicio, ruta):
        """El mismo GET en JSON y en XML: el XML cumple el XSD (lo comprueba el cliente)."""
        _, j = self.adm.llamar(servicio, "GET", ruta, estado=200)
        _, (raiz, x) = self.adm_xml.llamar(servicio, "GET", ruta, estado=200)
        return j, raiz, x

    def error(self, cliente, servicio, metodo, ruta, cuerpo, estado, codigo=None):
        r, d = cliente.llamar(servicio, metodo, ruta, cuerpo, estado=estado)
        if codigo:
            self.assertEqual(d["error"]["codigo"], codigo)
        return d["error"]


AM = "auditoria-monitoreo"
M = "monitoreo"


# ====================================================================
# Lógica pura del monitoreo
# ====================================================================
class T0Logica(unittest.TestCase):
    U = {"mon_latencia_ms": 1000.0, "mon_errores_pct": 20.0, "mon_errores_min_peticiones": 20.0, "mon_errores_ventana_min": 10.0}

    def test_clasificar(self):
        dep = {"postgres": "ok", "redis": "ok", "mongo": "ok", "bucket": "no_aplica"}
        self.assertEqual(mon.clasificar(200, {"estado": "ok", "version": "1.2", "dependencias": dep}), ("ok", "1.2", dep, None))
        self.assertEqual(mon.clasificar(503, {"estado": "degradado", "dependencias": {**dep, "redis": "error"}})[0], "degradado")
        self.assertEqual(mon.clasificar(None, None, "refused")[0], "caido")
        self.assertEqual(mon.clasificar(502, None)[0], "caido", "un 5xx sin estado de salud es caído")
        self.assertEqual(mon.clasificar(404, {})[0], "degradado", "responde, pero no como /salud")

    def test_alertas_deseadas(self):
        dep = {"postgres": "ok", "redis": "error", "mongo": "ok", "bucket": "error"}
        a = mon.alertas_deseadas("x", "degradado", 10, None, dep, None, self.U)
        self.assertEqual(set(a), {"servicio_degradado", "dependencia_caida"})
        self.assertIn("redis, bucket", a["dependencia_caida"][1])
        self.assertEqual(set(mon.alertas_deseadas("x", "caido", 3000, "no responde", None, None, self.U)), {"servicio_caido"},
                         "un servicio caído no genera alerta de latencia")
        self.assertEqual(set(mon.alertas_deseadas("x", "ok", 1500, None, None, None, self.U)), {"latencia_alta"})
        self.assertEqual(mon.alertas_deseadas("x", "ok", 10, None, None, None, self.U), {})

    def test_errores_altos_pide_volumen_minimo(self):
        poco = {"peticiones": 5, "errores_5xx": 5}
        self.assertEqual(mon.alertas_deseadas("x", "ok", 1, None, None, poco, self.U), {}, "5 de 5 es 100 %, pero es poca muestra")
        mucho = {"peticiones": 100, "errores_5xx": 25}
        self.assertEqual(set(mon.alertas_deseadas("x", "ok", 1, None, None, mucho, self.U)), {"errores_altos"})
        bien = {"peticiones": 100, "errores_5xx": 19}
        self.assertEqual(mon.alertas_deseadas("x", "ok", 1, None, None, bien, self.U), {}, "19 % está por debajo del 20 %")

    def test_percentil(self):
        self.assertIsNone(mon.percentil([], 95))
        self.assertEqual(mon.percentil([5], 99), 5)
        v = list(range(1, 101))
        self.assertEqual((mon.percentil(v, 50), mon.percentil(v, 95), mon.percentil(v, 99)), (50, 95, 99))

    def test_dependencias_caidas_se_agrupan(self):
        s = [{"servicio": "a", "dependencias": {"postgres": "error", "redis": "ok", "mongo": "ok", "bucket": "no_aplica"}},
             {"servicio": "b", "dependencias": {"postgres": "error", "redis": "error", "mongo": "ok", "bucket": "no_aplica"}},
             {"servicio": "c", "dependencias": None}]
        self.assertEqual(mon.agrupar_dependencias_caidas(s), [{"dependencia": "postgres", "afectados": ["a", "b"]},
                                                              {"dependencia": "redis", "afectados": ["b"]}])

    def test_cambios_nunca_muestra_credenciales(self):
        c = mon.cambios({"nombre": "Ana", "hash_contrasena": "x"}, {"nombre": "Ana María", "hash_contrasena": "y", "contrasena_temporal": "z"})
        self.assertEqual([x["campo"] for x in c], ["nombre"])
        self.assertEqual(c[0], {"campo": "nombre", "anterior": "Ana", "nuevo": "Ana María"})


# ====================================================================
# Monitoreo
# ====================================================================
class T1Monitoreo(Base):
    def setUp(self):
        super().setUp()
        APAGADOS.clear()
        DEGRADADOS.clear()
        limpiar_monitoreo()

    def tearDown(self):
        APAGADOS.clear()
        DEGRADADOS.clear()
        ejecutar("UPDATE configuracion SET valor = '1000' WHERE clave = 'mon_latencia_ms' AND ambito = 'global'")
        datos.mongo().metricas_servicio.delete_many({"prueba": "ola3"})
        limpiar_monitoreo()

    def ronda(self, servicio=None):
        cuerpo = {"servicio": servicio} if servicio else {}
        _, d = self.adm.llamar(AM, "POST", f"{M}/verificaciones", cuerpo, estado=201)
        return d

    def abiertas(self, servicio=None):
        ruta = f"{M}/alertas?estado=abiertas&por_pagina=100" + (f"&servicio={servicio}" if servicio else "")
        return self.adm.llamar(AM, "GET", ruta, estado=200)[1]["datos"]

    def test_una_ronda_verifica_a_todos_y_guarda_el_resultado(self):
        d = self.ronda()
        self.assertEqual(d["verificados"], len(config.PUERTOS))
        self.assertEqual((d["caidos"], d["degradados"]), (0, 0), d)
        self.assertEqual(uno("SELECT count(*) AS n FROM monitoreo_verificacion")["n"], len(config.PUERTOS))
        mismas_llaves(self, d, ejemplo("MonitoreoVerificacion.ok"))
        fila = uno("SELECT * FROM monitoreo_verificacion WHERE servicio = 'pedidos'")
        self.assertEqual((fila["estado"], fila["http_status"], fila["version"]), ("ok", 200, config.VERSION))
        self.assertEqual(set(fila["dependencias"]), {"postgres", "redis", "mongo", "bucket"})
        self.assertEqual(self.abiertas(), [], "una plataforma sana no tiene alertas")

    def test_el_panel_muestra_cada_servicio_y_cumple_el_contrato(self):
        self.ronda()
        j, raiz, x = self.ambos_formatos(AM, f"{M}/estado")
        self.assertEqual(raiz, "monitoreo_estado")
        mismas_llaves(self, j, ejemplo("MonitoreoEstado.ok"), opcionales=("afectados",))
        self.assertEqual(j["resumen"]["total"], len(config.PUERTOS))
        self.assertEqual(j["resumen"]["ok"], len(config.PUERTOS))
        self.assertTrue(j["resumen"]["monitor_activo"])
        s = {x["servicio"]: x for x in j["servicios"]}["pedidos"]
        self.assertEqual((s["puerto"], s["estado"], s["bajo_objetivo"]), (5104, "ok", False))
        self.assertEqual(s["disponibilidad_24h_pct"], 100.0)
        self.assertIsNotNone(s["tiempo_ms"])
        self.assertEqual(j["dependencias_caidas"], [])

    def test_sin_verificaciones_el_panel_dice_sin_datos_y_monitor_inactivo(self):
        j = self.adm.llamar(AM, "GET", f"{M}/estado", estado=200)[1]
        self.assertEqual(j["resumen"]["sin_datos"], len(config.PUERTOS))
        self.assertFalse(j["resumen"]["monitor_activo"], "si nadie verifica, el panel lo dice")
        self.assertTrue(all(s["estado"] == "sin_datos" and s["verificado_en"] is None for s in j["servicios"]))

    def test_servicio_caido_abre_alerta_y_al_volver_se_cierra_sola(self):
        with Apagado("inventario"):
            d = self.ronda()
        self.assertEqual(d["caidos"], 1)
        caido = [s for s in d["servicios"] if s["servicio"] == "inventario"][0]
        self.assertEqual(caido["estado"], "caido")
        self.assertTrue(caido["error"])
        al = self.abiertas("inventario")
        self.assertEqual([(a["tipo"], a["severidad"]) for a in al], [("servicio_caido", "critica")])
        mismas_llaves(self, al[0], ejemplo("MonitoreoAlerta.ok"), opcionales=("por", "en", "nombre"))
        e = self.adm.llamar(AM, "GET", f"{M}/estado", estado=200)[1]
        self.assertEqual((e["resumen"]["caidos"], e["resumen"]["alertas_abiertas"]), (1, 1))
        self.ronda()                                                        # el servicio volvió
        self.assertEqual(self.abiertas("inventario"), [])
        cerradas = self.adm.llamar(AM, "GET", f"{M}/alertas?estado=cerradas&servicio=inventario", estado=200)[1]["datos"]
        self.assertEqual(len(cerradas), 1)
        self.assertIsNotNone(cerradas[0]["cerrada_en"])
        self.error(self.adm, AM, "POST", f"{M}/alertas/{cerradas[0]['id']}/reconocer", {}, 409, "CONFLICTO")

    def test_una_alerta_abierta_no_se_duplica_en_la_siguiente_ronda(self):
        with Apagado("zonas"):
            self.ronda("zonas")
            self.ronda("zonas")
            self.ronda("zonas")
        self.assertEqual(len(self.abiertas("zonas")), 1)
        self.assertEqual(uno("SELECT count(*) AS n FROM monitoreo_verificacion WHERE servicio = 'zonas'")["n"], 3)

    def test_dependencia_caida_se_agrupa_por_dependencia(self):
        DEGRADADOS["zonas"] = {"postgres": "ok", "redis": "error", "mongo": "ok", "bucket": "no_aplica"}
        DEGRADADOS["precios"] = {"postgres": "ok", "redis": "error", "mongo": "ok", "bucket": "no_aplica"}
        d = self.ronda()
        self.assertEqual((d["degradados"], d["caidos"]), (2, 0))
        tipos = sorted(a["tipo"] for a in self.abiertas("zonas"))
        self.assertEqual(tipos, ["dependencia_caida", "servicio_degradado"])
        e = self.adm.llamar(AM, "GET", f"{M}/estado", estado=200)[1]
        self.assertEqual(e["dependencias_caidas"], [{"dependencia": "redis", "afectados": ["zonas", "precios"]}])
        self.assertEqual({s["servicio"]: s["estado"] for s in e["servicios"]}["zonas"], "degradado")
        j, raiz, x = self.ambos_formatos(AM, f"{M}/estado")                  # también en XML (cumple el XSD)
        self.assertEqual(x["dependencias_caidas"]["dependencia"]["dependencia"], "redis")

    def test_latencia_alta_usa_el_umbral_de_configuracion(self):
        ejecutar("UPDATE configuracion SET valor = '0' WHERE clave = 'mon_latencia_ms' AND ambito = 'global'")
        self.ronda("pedidos")
        self.assertEqual([a["tipo"] for a in self.abiertas("pedidos")], ["latencia_alta"])
        ejecutar("UPDATE configuracion SET valor = '1000' WHERE clave = 'mon_latencia_ms' AND ambito = 'global'")
        self.ronda("pedidos")
        self.assertEqual(self.abiertas("pedidos"), [])

    def test_errores_5xx_altos_en_mongodb_abren_alerta(self):
        db = datos.mongo()
        ahora = datos.ahora()
        db.metricas_servicio.insert_many([{"momento": ahora, "duracion_ms": 5, "prueba": "ola3",
                                           "etiquetas": {"servicio": "zonas", "ruta": "/x", "metodo": "GET", "status": 500 if i < 8 else 200}}
                                          for i in range(24)])
        self.ronda("zonas")
        al = self.abiertas("zonas")
        self.assertEqual([a["tipo"] for a in al], ["errores_altos"], al)
        self.assertIn("5xx", al[0]["detalle"])
        m = self.adm.llamar(AM, "GET", f"{M}/metricas?minutos=5", estado=200)[1]
        z = {s["servicio"]: s for s in m["servicios"]}["zonas"]
        self.assertGreaterEqual(z["errores_5xx"], 8)
        self.assertGreater(z["tasa_5xx_pct"], 20)

    def test_reconocer_alerta_exige_permiso_y_es_idempotente(self):
        with Apagado("zonas"):
            self.ronda("zonas")
        aid = self.abiertas("zonas")[0]["id"]
        self.error(self.aud, AM, "POST", f"{M}/alertas/{aid}/reconocer", {}, 403, "PROHIBIDO")
        r1 = self.adm.llamar(AM, "POST", f"{M}/alertas/{aid}/reconocer", {}, estado=200)[1]
        self.assertEqual(r1["reconocida"]["por"]["id"], self.adm.usuario["id"])
        r2 = self.adm.llamar(AM, "POST", f"{M}/alertas/{aid}/reconocer", {}, estado=200)[1]
        self.assertEqual(r2["reconocida"], r1["reconocida"])
        self.error(self.adm, AM, "POST", f"{M}/alertas/99999999/reconocer", {}, 404)
        # reconocer una alerta queda en la bitácora (trigger del motor)
        self.assertGreaterEqual(uno("SELECT count(*) AS n FROM auditoria WHERE entidad = 'monitoreo_alerta' AND entidad_id = %s", (str(aid),))["n"], 2)

    def test_historial_y_disponibilidad(self):
        self.ronda("pedidos")
        with Apagado("pedidos"):
            self.ronda("pedidos")
        self.ronda("pedidos")
        h = self.adm.llamar(AM, "GET", f"{M}/servicios/pedidos/historial", estado=200)[1]
        self.assertEqual([x["estado"] for x in h["datos"]], ["ok", "caido", "ok"], "la más reciente primero")
        mismas_llaves(self, h, ejemplo("MonitoreoHistorial.ok"))
        solo = self.adm.llamar(AM, "GET", f"{M}/servicios/pedidos/historial?estado=caido", estado=200)[1]
        self.assertEqual(solo["paginacion"]["total"], 1)
        self.assertIsNone(solo["datos"][0]["dependencias"], "de un servicio caído no se conocen sus dependencias")
        j, raiz, x = self.ambos_formatos(AM, f"{M}/disponibilidad")
        mismas_llaves(self, j, ejemplo("MonitoreoDisponibilidad.ok"))
        p = {s["servicio"]: s for s in j["servicios"]}["pedidos"]
        self.assertEqual((p["verificaciones"], p["caidas"]), (3, 1))
        self.assertEqual(p["disponibilidad_pct"], 66.67)
        self.assertTrue(p["bajo_objetivo"], "66 % está por debajo del objetivo de 99 %")
        self.assertEqual(j["objetivo_pct"], 99.0)
        self.assertLessEqual(p["tiempo_p50_ms"], p["tiempo_p95_ms"])
        sin = {s["servicio"]: s for s in j["servicios"]}["zonas"]
        self.assertEqual((sin["verificaciones"], sin["disponibilidad_pct"], sin["bajo_objetivo"]), (0, None, False))

    def test_filtros_invalidos_y_servicio_inexistente(self):
        self.error(self.adm, AM, "GET", f"{M}/servicios/noexiste/historial", None, 404)
        self.error(self.adm, AM, "GET", f"{M}/servicios/pedidos/historial?horas=0", None, 400, "FILTRO_INVALIDO")
        self.error(self.adm, AM, "GET", f"{M}/servicios/pedidos/historial?estado=raro", None, 400)
        self.error(self.adm, AM, "GET", f"{M}/disponibilidad?horas=99999", None, 400)
        self.error(self.adm, AM, "GET", f"{M}/metricas?minutos=abc", None, 400)
        self.error(self.adm, AM, "GET", f"{M}/alertas?estado=quizas", None, 400)
        self.error(self.adm, AM, "GET", f"{M}/alertas?servicio=noexiste", None, 404)
        self.error(self.adm, AM, "POST", f"{M}/verificaciones", {"servicio": "noexiste"}, 404)
        self.error(self.adm, AM, "POST", f"{M}/verificaciones", {"servicio": "x" * 40}, 422, "VALIDACION")

    def test_verificar_acepta_el_cuerpo_xml(self):
        r, (raiz, d) = self.adm_xml.llamar(AM, "POST", f"{M}/verificaciones", xml("verificacion_nueva", {"servicio": "pedidos"}), estado=201)
        self.assertEqual((raiz, d["verificados"]), ("monitoreo_verificacion", "1"))

    def test_metricas_y_supuestos(self):
        self.adm.llamar("zonas", "GET", "zonas")                           # genera tráfico
        j, raiz, x = self.ambos_formatos(AM, f"{M}/metricas")
        mismas_llaves(self, j, ejemplo("MonitoreoMetricas.ok"))
        self.assertGreater(j["peticiones_total"], 0)
        s, raiz, _ = self.ambos_formatos(AM, f"{M}/supuestos")[0:3]
        mismas_llaves(self, s, ejemplo("SupuestosMonitoreo.ok"))
        claves = {x["clave"] for x in s["datos"]}
        self.assertEqual(claves, set(mon.DEFECTOS))
        self.assertTrue(all(x["origen"] in ("medido", "supuesto", "normativo") and x["justificacion"] for x in s["datos"]))

    def test_purga_borra_lo_mas_viejo_que_la_retencion(self):
        self.ronda("pedidos")
        ejecutar("INSERT INTO monitoreo_verificacion (servicio, verificado_en, estado, tiempo_ms) VALUES "
                 "('pedidos', now() - interval '8 days', 'ok', 5), ('pedidos', now() - interval '6 days', 'ok', 5)")
        mon.purgar(mon.umbrales())
        self.assertEqual(uno("SELECT count(*) AS n FROM monitoreo_verificacion")["n"], 2, "quedan la de hoy y la de hace 6 días")

    def test_permisos_del_monitoreo(self):
        for ruta in (f"{M}/estado", f"{M}/disponibilidad", f"{M}/alertas", f"{M}/metricas", f"{M}/supuestos"):
            self.adm.llamar(AM, "GET", ruta, estado=200)
            self.aud.llamar(AM, "GET", ruta, estado=200)
            self.plan.llamar(AM, "GET", ruta, estado=200)
            for quien in (self.op1, self.rep, self.cli):
                self.error(quien, AM, "GET", ruta, None, 403, "PROHIBIDO")
        self.error(self.plan, AM, "POST", f"{M}/verificaciones", {}, 403)
        self.error(self.aud, AM, "POST", f"{M}/verificaciones", {}, 403)
        r, _ = Cliente(self, "json").llamar(AM, "GET", f"{M}/estado", token=False, estado=401)

    def test_el_verificador_toma_turno_una_sola_vez_por_ronda(self):
        datos.r_cache.delete("monitoreo:ronda:prueba")
        self.assertTrue(mon._tomar_turno("monitoreo:ronda:prueba", 30))
        self.assertFalse(mon._tomar_turno("monitoreo:ronda:prueba", 30), "el segundo proceso espera a la siguiente ronda")
        datos.r_cache.delete("monitoreo:ronda:prueba")


# ====================================================================
# Auditoría
# ====================================================================
class T2Auditoria(Base):
    def test_la_bitacora_se_consulta_con_filtros_y_cumple_el_contrato(self):
        j, raiz, x = self.ambos_formatos(AM, "auditoria?por_pagina=5")
        self.assertEqual(raiz, "bitacora")
        mismas_llaves(self, j, ejemplo("BitacoraLista.ok"), opcionales=("cambio",))
        self.assertLessEqual(len(j["datos"]), 5)
        fechas = [e["fecha"] for e in j["datos"]]
        self.assertEqual(fechas, sorted(fechas, reverse=True), "lo más reciente primero")
        for quien in (self.adm, self.aud):
            quien.llamar(AM, "GET", "auditoria?por_pagina=1", estado=200)

    def test_un_inicio_de_sesion_fallido_queda_y_se_encuentra(self):
        correo = "no.existe.ola3@codex.mx"
        Cliente(self, "json").llamar("auth", "POST", "auth/login", {"correo": correo, "clave": "mal", "dispositivo": "t"}, token=False, estado=401)
        j = self.aud.llamar(AM, "GET", f"auditoria?accion=login_fallido&q=no.existe.ola3", estado=200)[1]
        self.assertGreaterEqual(j["paginacion"]["total"], 1)
        e = j["datos"][0]
        self.assertEqual((e["accion"], e["correo_intento"], e["usuario"], e["exitoso"]), ("login_fallido", correo, None, False))
        a = self.aud.llamar(AM, "GET", "auditoria/accesos", estado=200)[1]
        self.assertIn(correo, [c["correo"] for c in a["correos_con_mas_fallos"]])
        self.assertGreaterEqual(a["totales"]["login_fallido"], 1)

    def test_filtros_por_modulo_entidad_usuario_y_fechas(self):
        hoy = dt.date.today().isoformat()
        j = self.aud.llamar(AM, "GET", f"auditoria?entidad=pedido&modulo=pedidos&desde=2000-01-01&hasta={hoy}&por_pagina=3", estado=200)[1]
        for e in j["datos"]:
            self.assertEqual((e["entidad"]["tipo"], e["modulo"]), ("pedido", "pedidos"))
        uid = uno("SELECT usuario_id FROM auditoria WHERE usuario_id IS NOT NULL LIMIT 1")["usuario_id"]
        j = self.aud.llamar(AM, "GET", f"auditoria?usuario_id={uid}&por_pagina=10", estado=200)[1]
        self.assertTrue(all(e["usuario"]["id"] == uid for e in j["datos"]))
        futuro = self.aud.llamar(AM, "GET", "auditoria?desde=2999-01-01", estado=200)[1]
        self.assertEqual(futuro["paginacion"]["total"], 0)
        con = self.aud.llamar(AM, "GET", "auditoria?exitoso=false&por_pagina=5", estado=200)[1]
        self.assertTrue(all(e["exitoso"] is False for e in con["datos"]))

    def test_filtros_invalidos(self):
        for q in ("exitoso=quizas", "accion=inventada", "desde=ayer", "usuario_id=abc", "por_pagina=0", "pagina=0", "q=" + "x" * 81):
            with self.subTest(q):
                self.error(self.aud, AM, "GET", f"auditoria?{q}", None, 400, "FILTRO_INVALIDO")
        self.error(self.aud, AM, "GET", "auditoria/accesos?desde=2026-02-01&hasta=2026-01-01", None, 400)

    def test_los_cambios_nunca_traen_credenciales(self):
        j = self.aud.llamar(AM, "GET", "auditoria?entidad=usuario&por_pagina=100", estado=200)[1]
        for e in j["datos"]:
            for c in e["cambios"]:
                self.assertNotIn("hash", c["campo"])
                self.assertNotIn("contrasena", c["campo"])
        self.assertNotIn("$2b$", json.dumps(j))

    def test_solo_auditoria_ver_y_el_intento_queda_auditado(self):
        antes = uno("SELECT count(*) AS n FROM auditoria WHERE accion = 'acceso_denegado' AND detalle LIKE %s", ("%auditoria%",))["n"]
        for ruta in ("auditoria", "auditoria/accesos", "auditoria/trazabilidad/pedido/1", "auditoria/trazabilidad/inventario?microhub_id=1&producto_id=1"):
            for quien in (self.plan, self.op1, self.rep, self.cli):
                self.error(quien, AM, "GET", ruta, None, 403, "PROHIBIDO")
        despues = uno("SELECT count(*) AS n FROM auditoria WHERE accion = 'acceso_denegado' AND detalle LIKE %s", ("%auditoria%",))["n"]
        self.assertEqual(despues - antes, 16)
        a = self.aud.llamar(AM, "GET", "auditoria/accesos", estado=200)[1]
        mismas_llaves(self, a, ejemplo("Accesos.ok"))
        self.assertGreaterEqual(a["totales"]["acceso_denegado"], 16)
        propios = self.aud.llamar(AM, "GET", "auditoria?accion=acceso_denegado&q=auditoria&por_pagina=1", estado=200)[1]
        self.assertGreaterEqual(propios["paginacion"]["total"], 16, "el auditor encuentra los intentos prohibidos en la bitácora")
        Cliente(self, "json").llamar(AM, "GET", "auditoria", token=False, estado=401)

    def test_accesos_en_xml(self):
        j, raiz, x = self.ambos_formatos(AM, "auditoria/accesos")
        self.assertEqual(raiz, "accesos")
        self.assertEqual(set(j["totales"]), {"login_exitoso", "login_fallido", "logout", "bloqueo_cuenta", "desbloqueo", "acceso_denegado"})

    def test_trazabilidad_de_un_pedido_une_estados_bitacora_e_inventario(self):
        f = uno("SELECT h.pedido_id FROM historial_estatus h GROUP BY h.pedido_id ORDER BY count(*) DESC, h.pedido_id LIMIT 1")
        pid = f["pedido_id"]
        j, raiz, x = self.ambos_formatos(AM, f"auditoria/trazabilidad/pedido/{pid}")
        self.assertEqual(raiz, "trazabilidad")
        mismas_llaves(self, j, ejemplo("Trazabilidad.ok"), opcionales=("cambio",))
        self.assertEqual(j["objeto"], {"tipo": "pedido", "id": str(pid)})
        self.assertEqual(j["total"], len(j["eventos"]))
        origenes = {e["origen"] for e in j["eventos"]}
        self.assertIn("estados", origenes)
        fechas = [e["fecha"] for e in j["eventos"]]
        self.assertEqual(fechas, sorted(fechas), "en orden de fecha")
        n_estados = uno("SELECT count(*) AS n FROM historial_estatus WHERE pedido_id = %s", (pid,))["n"]
        self.assertEqual(sum(1 for e in j["eventos"] if e["origen"] == "estados"), n_estados)
        self.assertTrue(all("→" in e["descripcion"] for e in j["eventos"] if e["origen"] == "estados"))

    def test_trazabilidad_incluye_los_archivos_del_bucket_sin_el_archivo(self):
        pid = uno("SELECT id FROM pedido ORDER BY id LIMIT 1")["id"]
        b64 = base64.b64encode(JPEG).decode()
        _, d = self.adm.llamar("documentos", "POST", "documentos", {
            "nombre": "evidencia_ola3.jpg", "tipo_mime": "image/jpeg", "contenido_base64": b64,
            "referencia": {"tipo": "pedido", "id": str(pid)}}, estado=201)
        try:
            j = self.aud.llamar(AM, "GET", f"auditoria/trazabilidad/pedido/{pid}", estado=200)[1]
            docs = [e for e in j["eventos"] if e["origen"] == "documentos"]
            mios = [e for e in docs if e["entidad"]["id"] == d["id"]]
            self.assertEqual(len(mios), 1)
            self.assertIn("sha256", mios[0]["descripcion"])
            self.assertEqual(mios[0]["entidad"], {"tipo": "documento", "id": d["id"]})
            self.assertNotIn(b64[:40], json.dumps(j), "la línea de tiempo no lleva el contenido del archivo")
            self.adm.llamar("documentos", "DELETE", f"documentos/{d['id']}", estado=204)
            j = self.aud.llamar(AM, "GET", f"auditoria/trazabilidad/pedido/{pid}", estado=200)[1]
            borrado = [e for e in j["eventos"] if e["origen"] == "documentos" and e["entidad"]["id"] == d["id"]]
            self.assertIn("[eliminado]", borrado[0]["descripcion"], "el borrado lógico no borra la historia")
        finally:
            datos.mongo().documentos.delete_many({"nombre": "evidencia_ola3.jpg"})

    def test_trazabilidad_de_entrega_e_inventario(self):
        eid = uno("SELECT id FROM entrega ORDER BY id LIMIT 1")["id"]
        j = self.aud.llamar(AM, "GET", f"auditoria/trazabilidad/entrega/{eid}", estado=200)[1]
        self.assertEqual(j["objeto"], {"tipo": "entrega", "id": str(eid)})
        m = uno("SELECT microhub_id, producto_id FROM movimiento_inventario ORDER BY id LIMIT 1")
        j = self.aud.llamar(AM, "GET", f"auditoria/trazabilidad/inventario?microhub_id={m['microhub_id']}&producto_id={m['producto_id']}", estado=200)[1]
        self.assertGreaterEqual(j["total"], 1)
        self.assertTrue(all(e["origen"] == "inventario" for e in j["eventos"]))
        self.assertEqual(j["objeto"]["id"], f"{m['microhub_id']}-{m['producto_id']}")

    def test_trazabilidad_de_algo_que_no_existe(self):
        self.error(self.aud, AM, "GET", "auditoria/trazabilidad/pedido/99999999", None, 404, "NO_ENCONTRADO")
        self.error(self.aud, AM, "GET", "auditoria/trazabilidad/entrega/99999999", None, 404)
        self.error(self.aud, AM, "GET", "auditoria/trazabilidad/inventario?microhub_id=1", None, 400, "FILTRO_INVALIDO")
        self.error(self.aud, AM, "GET", "auditoria/trazabilidad/inventario?microhub_id=99999&producto_id=99999", None, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
