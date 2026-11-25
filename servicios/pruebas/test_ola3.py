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
import uuid
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
os.environ.setdefault("LOG_STDOUT", "0")
os.environ.setdefault("MONITOR_AUTO", "0")

from comun import clientes, config, datos  # noqa: E402
from pruebas.test_contrato import APPS, JPEG, Cliente, ejemplo, mismas_llaves, xml  # noqa: E402

mon = sys.modules["auditoria_monitoreo.app"]
rep = sys.modules["reportes.app"]
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
        correo = f"no.existe.{uuid.uuid4().hex[:10]}@codex.mx"       # distinto en cada corrida: la cuenta se bloquea a los 5 intentos
        Cliente(self, "json").llamar("auth", "POST", "auth/login", {"correo": correo, "clave": "mal", "dispositivo": "t"}, token=False, estado=401)
        j = self.aud.llamar(AM, "GET", f"auditoria?accion=login_fallido&q={correo}", estado=200)[1]
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


# ====================================================================
# Reportes
# ====================================================================
RP = "reportes"
DESDE = "2026-01-01"
COLS = [{"clave": "a", "titulo": "Texto", "tipo": "texto"}, {"clave": "n", "titulo": "Cuántos", "tipo": "entero"},
        {"clave": "d", "titulo": "Importe", "tipo": "dinero"}]


class T3Logica(unittest.TestCase):
    def test_porcentajes_y_celdas(self):
        self.assertEqual((rep.pct(1, 8), rep.pct(1, 0), rep.dividir(10, 4), rep.dividir(1, 0)), (12.5, None, 2.5, None))
        self.assertEqual((rep.celda(None, "dinero"), rep.celda(3.0, "entero"), rep.celda(3.456, "dinero"), rep.celda(True, "texto"),
                          rep.celda("x", "texto")), ("", "3", "3.46", "sí", "x"))

    def test_neutraliza_formulas(self):
        for peligroso in ("=CMD()", "+1+1", "-2+3", "@SUM(A1)", "\tx"):
            self.assertEqual(rep.neutralizar(peligroso), "'" + peligroso)
        self.assertEqual((rep.neutralizar("normal"), rep.neutralizar("")), ("normal", ""))

    def test_agrupar_por_dia_y_zona(self):
        filas = [{"fecha": "2026-11-02", "zona_id": 1, "pedidos": 2, "unidades": 5, "venta": "100.5", "no_atendidos": 1},
                 {"fecha": "2026-11-01", "zona_id": 2, "pedidos": 1, "unidades": 2, "venta": 40, "no_atendidos": 0},
                 {"fecha": "2026-11-02", "zona_id": 2, "pedidos": 3, "unidades": 6, "venta": 60, "no_atendidos": 2}]
        self.assertEqual(rep.agrupar_por_dia(filas), [["2026-11-01", 1, 2, 40.0, 40.0, 0], ["2026-11-02", 5, 11, 160.5, 32.1, 3]])
        z = rep.agrupar_por_zona(filas, {1: {"nombre": "Centro"}})
        self.assertEqual(z[0], ["Centro", 2, 5, 100.5, 50.25, 1, 33.33])
        self.assertEqual(z[1][0], "Zona 2", "una zona sin nombre conocido no tumba el reporte")
        self.assertEqual(rep.totales_de(COLS, [["a", 1, 2.5], ["b", 2, 3.0]], [1, 2]), ["Total", 3, 5.5])
        self.assertIsNone(rep.totales_de(COLS, [], [1]))

    def test_csv_trae_bom_crlf_y_celdas_seguras(self):
        b = rep.csv_bytes(COLS, [["=CMD()", 2, 10.5], ["ok, con coma", None, None]], ["Total", 2, 10.5])
        self.assertTrue(b.startswith(b"\xef\xbb\xbf"))
        t = b.decode("utf-8-sig").split("\r\n")
        self.assertEqual(t[0], "Texto,Cuántos,Importe")
        self.assertEqual(t[1], "'=CMD(),2,10.50")
        self.assertEqual(t[2], '"ok, con coma",,')
        self.assertEqual(t[3], "Total,2,10.50")

    def test_xlsx_es_un_libro_valido_con_numeros_y_sin_formulas(self):
        import io
        from openpyxl import load_workbook
        b = rep.xlsx_bytes("Pedidos: por [día]", COLS, [["=1+1", 2, 10.5], ["ok", None, None]], ["Total", 2, 10.5])
        ws = load_workbook(io.BytesIO(b)).active
        self.assertEqual(ws.title, "Pedidos por día", "el nombre de la hoja no admite : [ ] ni más de 31 caracteres")
        self.assertEqual([c.value for c in ws[1]], ["Texto", "Cuántos", "Importe"])
        self.assertEqual((ws["A2"].value, ws["A2"].data_type), ("'=1+1", "s"), "lo que parece fórmula queda como texto")
        self.assertEqual((ws["B2"].value, ws["C2"].value), (2, 10.5))
        self.assertIsNone(ws["B3"].value)
        self.assertEqual([c.value for c in ws[4]], ["Total", 2, 10.5])

    def test_pdf_es_un_pdf_completo(self):
        b = rep.pdf_bytes("Pedidos <por> día", "Periodo X", COLS, [[f"fila {i} & más", i, i * 1.5] for i in range(200)], ["Total", 1, 2.0])
        self.assertTrue(b.startswith(b"%PDF-") and b.rstrip().endswith(b"%%EOF"))
        self.assertGreater(b.count(b"/Type /Page"), 2, "200 filas ocupan varias páginas")


class T4Reportes(Base):
    def setUp(self):
        super().setUp()
        APAGADOS.clear()

    def tearDown(self):
        APAGADOS.clear()
        ejecutar("UPDATE configuracion SET valor = '50000' WHERE clave = 'rep_filas_max' AND ambito = 'global'")

    def q(self, **kw):
        return "&".join(f"{k}={v}" for k, v in {"desde": DESDE, **kw}.items() if v is not None)

    def descargar(self, ruta, quien=None):
        return APPS[RP].test_client().get(f"/api/v1/{ruta}", headers={"Authorization": f"Bearer {(quien or self.adm).token}"})

    def test_catalogo_en_json_y_xml(self):
        j, raiz, x = self.ambos_formatos(RP, "reportes")
        self.assertEqual(raiz, "reportes_catalogo")
        mismas_llaves(self, j, ejemplo("ReportesCatalogo.ok"))
        self.assertEqual({r["clave"] for r in j["datos"]}, set(rep.REPORTES))
        self.assertEqual({r["familia"] for r in j["datos"]}, {"operativo", "logistico", "comercial", "financiero"})

    def test_cada_reporte_responde_en_json_y_en_xml_conforme_al_contrato(self):
        for clave in rep.REPORTES:
            with self.subTest(clave):
                ruta = f"reportes/{clave}" + ("?" + self.q() if "desde" in rep.REPORTES[clave][3] else "")
                j, raiz, x = self.ambos_formatos(RP, ruta)
                self.assertEqual(raiz, "reporte")
                mismas_llaves(self, j, ejemplo("Reporte.ok"))
                self.assertEqual(j["reporte"], clave)
                self.assertEqual(j["total_filas"], len(j["filas"]))
                ncol = len(j["columnas"])
                self.assertTrue(all(len(f["celdas"]) == ncol for f in j["filas"]), "toda fila trae una celda por columna")
                if j["totales"]:
                    self.assertEqual(len(j["totales"]["celdas"]), ncol)

    def test_pedidos_por_dia_coincide_con_la_base(self):
        hoy = dt.date.today().isoformat()
        j = self.adm.llamar(RP, "GET", f"reportes/pedidos_por_dia?desde={DESDE}&hasta={hoy}", estado=200)[1]
        esperado = uno("SELECT count(*) AS n, COALESCE(sum(subtotal), 0) AS venta FROM pedido WHERE estado <> 'cancelado' "
                       "AND (creado_en AT TIME ZONE 'America/Monterrey')::date BETWEEN %s AND %s", (DESDE, hoy))
        self.assertGreater(esperado["n"], 0, "la base de demostración tiene pedidos")
        self.assertEqual(int(j["totales"]["celdas"][1]), esperado["n"])
        self.assertAlmostEqual(float(j["totales"]["celdas"][3]), float(esperado["venta"]), places=2)
        dias = [f["celdas"][0] for f in j["filas"]]
        self.assertEqual(dias, sorted(dias), "un renglón por día, en orden")
        self.assertEqual(len(dias), len(set(dias)))

    def test_ventas_por_producto_suma_la_venta_y_su_participacion(self):
        hoy = dt.date.today().isoformat()
        j = self.adm.llamar(RP, "GET", f"reportes/ventas_por_producto?desde={DESDE}&hasta={hoy}", estado=200)[1]
        esperado = uno("SELECT COALESCE(sum(d.importe), 0) AS v FROM pedido p JOIN pedido_detalle d ON d.pedido_id = p.id "
                       "WHERE p.estado NOT IN ('cancelado', 'creado', 'pendiente_asignacion') "
                       "AND (p.creado_en AT TIME ZONE 'America/Monterrey')::date BETWEEN %s AND %s", (DESDE, hoy))["v"]
        self.assertAlmostEqual(float(j["totales"]["celdas"][3]), float(esperado), places=2)
        participacion = sum(float(f["celdas"][5]) for f in j["filas"])
        self.assertAlmostEqual(participacion, 100.0, delta=0.5 + 0.01 * len(j["filas"]), msg="las participaciones suman 100 %")
        ventas = [float(f["celdas"][3]) for f in j["filas"]]
        self.assertEqual(ventas, sorted(ventas, reverse=True), "el más vendido primero")

    def test_comparacion_entre_microhubs_y_un_solo_microhub(self):
        hoy = dt.date.today().isoformat()
        j = self.adm.llamar(RP, "GET", f"reportes/comparacion_microhubs?desde={DESDE}&hasta={hoy}", estado=200)[1]
        self.assertGreaterEqual(len(j["filas"]), 2)
        hub = uno("SELECT m.id, m.nombre FROM microhub m JOIN pedido p ON p.microhub_id = m.id WHERE p.estado <> 'cancelado' "
                  "GROUP BY m.id, m.nombre ORDER BY count(*) DESC LIMIT 1")
        fila = [f for f in j["filas"] if f["celdas"][0] == hub["nombre"]][0]["celdas"]
        n = uno("SELECT count(*) AS n FROM pedido WHERE microhub_id = %s AND estado <> 'cancelado' "
                "AND (creado_en AT TIME ZONE 'America/Monterrey')::date BETWEEN %s AND %s", (hub["id"], DESDE, hoy))["n"]
        self.assertEqual(int(fila[1]), n)
        self.assertAlmostEqual(sum(float(f["celdas"][5]) for f in j["filas"]), 100.0, delta=0.1)
        solo = self.adm.llamar(RP, "GET", f"reportes/comparacion_microhubs?desde={DESDE}&hasta={hoy}&microhub_id={hub['id']}", estado=200)[1]
        self.assertEqual([f["celdas"][0] for f in solo["filas"]], [hub["nombre"]])
        self.error(self.adm, RP, "GET", "reportes/comparacion_microhubs?microhub_id=999999", None, 404)

    def test_filtros_que_el_reporte_no_admite_se_rechazan(self):
        for ruta in ("carga_repartidores?zona_id=1", "carga_repartidores?desde=2026-01-01", "inventario_alertas?zona_id=1",
                     "inventario_alertas?desde=2026-01-01", "equilibrio_microhubs?hasta=2026-02-01", "ventas_por_producto?zona_id=1"):
            with self.subTest(ruta):
                self.error(self.adm, RP, "GET", f"reportes/{ruta}", None, 400, "FILTRO_INVALIDO")

    def test_filtros_invalidos(self):
        for q in ("desde=ayer", "hasta=31-12-2026", "desde=2026-05-01&hasta=2026-04-01", "desde=2020-01-01&hasta=2026-01-01", "zona_id=abc",
                  "microhub_id=1.5"):
            with self.subTest(q):
                self.error(self.adm, RP, "GET", f"reportes/pedidos_por_dia?{q}", None, 400, "FILTRO_INVALIDO")
        self.error(self.adm, RP, "GET", "reportes/no_existe", None, 404, "NO_ENCONTRADO")
        self.error(self.adm, RP, "GET", "reportes/pedidos_por_dia/exportar?formato=exe", None, 400)
        self.error(self.adm, RP, "GET", "reportes/no_existe/grafica", None, 404)

    def test_un_reporte_muy_grande_pide_acotar(self):
        ejecutar("UPDATE configuracion SET valor = '1' WHERE clave = 'rep_filas_max' AND ambito = 'global'")
        e = self.error(self.adm, RP, "GET", f"reportes/pedidos_por_dia?{self.q()}", None, 422, "REPORTE_DEMASIADO_GRANDE")
        self.assertIn("Acota", e["mensaje"])

    def test_grafica_para_highcharts(self):
        j, raiz, x = self.ambos_formatos(RP, f"reportes/pedidos_por_dia/grafica?{self.q()}")
        self.assertEqual(raiz, "grafica")
        mismas_llaves(self, j, ejemplo("ReporteGrafica.ok"))
        self.assertEqual((j["tipo"], [s["nombre"] for s in j["series"]]), ("line", ["Pedidos", "Venta"]))
        self.assertTrue(all(len(s["datos"]) == len(j["categorias"]) for s in j["series"]))
        top = self.adm.llamar(RP, "GET", f"reportes/ventas_por_producto/grafica?{self.q()}", estado=200)[1]
        self.assertLessEqual(len(top["categorias"]), 10, "la gráfica de productos muestra los 10 primeros")
        al = self.adm.llamar(RP, "GET", "reportes/inventario_alertas/grafica", estado=200)[1]
        self.assertEqual(len(al["categorias"]), len(set(al["categorias"])), "las alertas se suman por microhub")

    def test_exportar_csv_xlsx_y_pdf_con_huella_y_bitacora(self):
        import hashlib
        antes = uno("SELECT count(*) AS n FROM reporte_exportacion")["n"]
        tipos = {"csv": "text/csv", "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "pdf": "application/pdf"}
        for fmt, mime in tipos.items():
            with self.subTest(fmt):
                r = self.descargar(f"reportes/pedidos_por_dia/exportar?formato={fmt}&{self.q()}")
                self.assertEqual(r.status_code, 200, r.data[:300])
                self.assertEqual(r.mimetype, mime)
                self.assertIn(f'attachment; filename="pedidos_por_dia_{DESDE}_', r.headers["Content-Disposition"])
                self.assertEqual(r.headers["X-Reporte-SHA256"], hashlib.sha256(r.data).hexdigest())
                if fmt == "pdf":
                    self.assertTrue(r.data.startswith(b"%PDF-"))
                if fmt == "xlsx":
                    self.assertTrue(r.data.startswith(b"PK"))
        self.assertEqual(uno("SELECT count(*) AS n FROM reporte_exportacion")["n"] - antes, 3)
        fila = uno("SELECT * FROM reporte_exportacion ORDER BY id DESC LIMIT 1")
        self.assertEqual((fila["reporte"], fila["formato"], fila["creado_por"]), ("pedidos_por_dia", "pdf", self.adm.usuario["id"]))
        self.assertEqual(fila["filtros"]["desde"], DESDE)
        self.assertEqual(len(fila["sha256"]), 64)

    def test_por_omision_se_exporta_csv_y_sin_token_no_hay_archivo(self):
        r = self.descargar("reportes/carga_repartidores/exportar")
        self.assertEqual((r.status_code, r.mimetype), (200, "text/csv"))
        self.assertTrue(r.data.startswith(b"\xef\xbb\xbf"))
        self.assertEqual(APPS[RP].test_client().get("/api/v1/reportes/carga_repartidores/exportar").status_code, 401)

    def test_exportaciones_cada_quien_ve_las_suyas_y_el_administrador_todas(self):
        for quien in (self.adm, self.plan):
            self.assertEqual(self.descargar("reportes/carga_repartidores/exportar?formato=csv", quien).status_code, 200)
        j = self.plan.llamar(RP, "GET", "reportes/exportaciones?por_pagina=100", estado=200)[1]
        self.assertTrue(j["datos"] and all(e["creado_por"]["id"] == self.plan.usuario["id"] for e in j["datos"]))
        mismas_llaves(self, j, ejemplo("ReportesExportacionLista.ok"))
        a = self.adm.llamar(RP, "GET", "reportes/exportaciones?por_pagina=100", estado=200)[1]
        self.assertGreater(len({e["creado_por"]["id"] for e in a["datos"]}), 1, "el administrador ve las de todos")
        j, raiz, x = self.ambos_formatos(RP, "reportes/exportaciones")
        self.assertEqual(raiz, "reportes_exportaciones")

    def test_indicadores_y_un_servicio_caido_solo_quita_su_indicador(self):
        j, raiz, x = self.ambos_formatos(RP, f"reportes/indicadores?{self.q()}")
        mismas_llaves(self, j, ejemplo("ReportesIndicadores.ok"))
        claves = {i["clave"] for i in j["indicadores"]}
        self.assertEqual(claves, {"pedidos", "venta", "ticket_promedio", "no_atendidos", "alertas_inventario", "repartidores_activos",
                                  "entregas_abiertas", "microhubs_no_viables"})
        self.assertEqual(j["fuentes_no_disponibles"], [])
        with Apagado("inventario"):
            c = self.adm.llamar(RP, "GET", f"reportes/indicadores?{self.q()}", estado=200)[1]
        self.assertEqual(c["fuentes_no_disponibles"], ["inventario"])
        self.assertEqual({i["clave"] for i in c["indicadores"]}, claves - {"alertas_inventario"}, "los demás indicadores se entregan")
        with Apagado("pedidos", "entregas"):
            c = self.adm.llamar(RP, "GET", f"reportes/indicadores?{self.q()}", estado=200)[1]
        self.assertEqual(sorted(c["fuentes_no_disponibles"]), ["entregas", "pedidos"])

    def test_un_reporte_con_su_fuente_caida_responde_503_y_no_deja_rastro(self):
        n = uno("SELECT count(*) AS n FROM reporte_exportacion")["n"]
        with Apagado("pedidos"):
            self.error(self.adm, RP, "GET", f"reportes/pedidos_por_dia?{self.q()}", None, 503, "SERVICIO_NO_DISPONIBLE")
            self.error(self.adm, RP, "GET", f"reportes/pedidos_por_dia/exportar?{self.q()}", None, 503)
        self.assertEqual(uno("SELECT count(*) AS n FROM reporte_exportacion")["n"], n, "una exportación fallida no se registra")

    def test_permisos_de_reportes(self):
        for ruta in ("reportes", "reportes/indicadores", f"reportes/pedidos_por_dia?{self.q()}", "reportes/exportaciones"):
            for quien in (self.op1, self.rep, self.cli):
                self.error(quien, RP, "GET", ruta, None, 403, "PROHIBIDO")
            for quien in (self.adm, self.aud, self.plan):
                quien.llamar(RP, "GET", ruta, estado=200)
        Cliente(self, "json").llamar(RP, "GET", "reportes", token=False, estado=401)


if __name__ == "__main__":
    unittest.main(verbosity=2)
