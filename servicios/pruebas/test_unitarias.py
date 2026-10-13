"""
test_unitarias.py — Pruebas unitarias de los microservicios, sin bases de datos.

Cubren la lógica que no depende de PostgreSQL, Redis ni MongoDB: formatos
JSON/XML del contrato, validación de entradas, XSD, documentación OpenAPI,
proyección de la simulación al contrato y cálculo de distancias.

  cd servicios && python -m unittest -v pruebas.test_unitarias
"""
import datetime as dt
import importlib.util
import json
import os
import sys
import unittest
from decimal import Decimal
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
os.environ.setdefault("LOG_STDOUT", "0")

from comun import config  # noqa: E402
from comun.base_errores import ErrorApi  # noqa: E402
from comun.esquemas import errores_xml  # noqa: E402
from comun.formatos import a_xml, dinero, fecha, leer_xml, sin_nulos  # noqa: E402
from comun.validar import Campo, validar  # noqa: E402

SERVICIOS = ["auth", "usuarios", "productos", "pedidos", "entregas", "planeacion", "documentos", "zonas", "microhubs", "seguimiento"]


def cargar(nombre):
    spec = importlib.util.spec_from_file_location(f"u_{nombre}", AQUI.parent / nombre / "app.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Formatos(unittest.TestCase):
    def test_dinero_dos_decimales(self):
        self.assertEqual(str(dinero(16000)), "16000.00")
        self.assertEqual(str(dinero(0.125)), "0.13")
        self.assertIsNone(dinero(None))

    def test_fecha_con_zona_de_monterrey(self):
        utc = dt.datetime(2026, 10, 13, 0, 30, tzinfo=dt.timezone.utc)
        self.assertEqual(fecha(utc), "2026-10-12T18:30:00-06:00")

    def test_xml_nil_booleano_listas_y_version(self):
        x = a_xml("validacion", {"valido": True, "expira_en": 600,
                                 "usuario": {"id": 7, "rol": "repartidor", "microhub_id": None}})
        self.assertIn(b'version="1"', x)
        self.assertIn(b"<valido>true</valido>", x)
        self.assertIn(b'xsi:nil="true"', x)
        self.assertEqual(errores_xml(x), [], "cumple auth.xsd")
        lista = a_xml("conteo", {"no_leidas": 3})
        self.assertEqual(errores_xml(lista), [])

    def test_xml_que_no_cumple_el_xsd(self):
        self.assertTrue(errores_xml(a_xml("conteo", {"no_leidas": -1})), "minInclusive 0")
        self.assertTrue(errores_xml(a_xml("conteo", {"otro": 1})), "elemento no declarado")

    def test_leer_xml_rechaza_dtd_y_entidades(self):
        malicioso = b'<?xml version="1.0"?><!DOCTYPE a [<!ENTITY x "y">]><login xmlns="urn:microhubs:v1"><correo>&x;</correo></login>'
        with self.assertRaises(Exception):
            leer_xml(malicioso)

    def test_leer_xml_anidado_y_repetido(self):
        raiz, ns, d = leer_xml(b'<simulacion xmlns="urn:microhubs:v1"><supuestos><operadores>3</operadores></supuestos>'
                               b'<lineas><linea><a>1</a></linea><linea><a>2</a></linea></lineas></simulacion>')
        self.assertEqual((raiz, ns), ("simulacion", "urn:microhubs:v1"))
        self.assertEqual(d["supuestos"]["operadores"], "3")
        self.assertEqual(len(d["lineas"]["linea"]), 2)

    def test_sin_nulos_solo_quita_opcionales(self):
        self.assertEqual(sin_nulos({"a": None, "b": None}, "a"), {"b": None})


class Validacion(unittest.TestCase):
    CAMPOS = [Campo("nombre", min_len=3, max_len=10), Campo("cantidad", "int", minimo=1),
              Campo("monto", "num", minimo=0, decimales=2), Campo("activo", "bool", req=False),
              Campo("estado", opciones=["a", "b"], req=False), Campo("cuando", "fecha", req=False)]

    def test_convierte_texto_xml_a_tipos(self):
        d = validar({"nombre": "Arroz", "cantidad": "5", "monto": "12.50", "activo": "true",
                     "cuando": "2026-10-12T18:30:00-06:00"}, self.CAMPOS)
        self.assertEqual((d["cantidad"], d["monto"], d["activo"]), (5, 12.5, True))
        self.assertEqual(d["cuando"].utcoffset(), dt.timedelta(hours=-6))

    def test_junta_todos_los_errores(self):
        with self.assertRaises(ErrorApi) as e:
            validar({"nombre": "x", "cantidad": 0, "monto": 1.234, "estado": "z", "cuando": "2026-10-12T18:30:00"},
                    self.CAMPOS)
        self.assertEqual(e.exception.status, 422)
        campos = {d["campo"] for d in e.exception.detalles}
        self.assertEqual(campos, {"nombre", "cantidad", "monto", "estado", "cuando"})

    def test_obligatorio_y_booleano_no_es_entero(self):
        with self.assertRaises(ErrorApi) as e:
            validar({"cantidad": True, "monto": 1}, self.CAMPOS)
        self.assertEqual({d["campo"] for d in e.exception.detalles}, {"nombre", "cantidad"})


class Contrato(unittest.TestCase):
    def test_los_46_ejemplos_oficiales_cumplen_los_xsd(self):
        ejemplos = sorted(config.EJEMPLOS_XML.glob("*.xml"))
        self.assertGreaterEqual(len(ejemplos), 46)
        for f in ejemplos:
            self.assertEqual(errores_xml(f.read_bytes()), [], f.name)

    def test_openapi_de_los_diez_servicios(self):
        for s in SERVICIOS:
            with self.subTest(s):
                app = cargar(s).app
                spec = app.test_client().get("/api/v1/openapi.json").get_json()
                self.assertEqual(spec["openapi"], "3.0.3")
                self.assertIn("bearer", spec["components"]["securitySchemes"])
                self.assertIn("/api/v1/health", spec["paths"])
                metodos = {m for p in spec["paths"].values() for m in p}
                self.assertIn("get", metodos)
                xml = [op for p in spec["paths"].values() for op in p.values()
                       if any("application/xml" in (r.get("content") or {}) for r in op["responses"].values())]
                self.assertTrue(xml, "Swagger muestra ejemplos XML")

    def test_simulacion_del_escenario_a_igual_al_ejemplo_oficial(self):
        plan = cargar("planeacion")
        supuestos = json.loads((config.EJEMPLOS_JSON / "Supuestos.ok.json").read_text(encoding="utf-8"))
        oficial = json.loads((config.EJEMPLOS_JSON / "Resultados.ok.json").read_text(encoding="utf-8"))
        r = plan.resultados(plan.pc.simular(supuestos))
        for k in ("atendidos", "rechazados", "utilizacion", "nivel", "tiempo_estimado_min", "operadores_requeridos",
                  "repartidores_requeridos", "decision"):
            self.assertEqual(r[k], oficial[k], k)
        self.assertEqual((r["ingreso_dia"], r["margen_dia"], r["costo_por_pedido"]),
                         (Decimal("16200.00"), Decimal("-504.00"), Decimal("42.00")))
        self.assertEqual(r["equilibrio"], {"margen_pedido": Decimal("15.80"), "mensual": 4557.0, "diario": 151.9})
        self.assertEqual(errores_xml(a_xml("resultados", r)), [], "la salida cumple planeacion.xsd")

    def test_haversine(self):
        seg = cargar("seguimiento")
        # Un grado de latitud ≈ 111.2 km.
        self.assertAlmostEqual(seg._haversine([-100.0, 25.0], [-100.0, 26.0]), 111.2, delta=0.1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
