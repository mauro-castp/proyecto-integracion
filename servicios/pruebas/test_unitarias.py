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

from comun import clientes, config  # noqa: E402
from comun.base_errores import ErrorApi  # noqa: E402
from comun.esquemas import errores_xml  # noqa: E402
from comun.formatos import a_xml, dinero, fecha, leer_xml, sin_nulos  # noqa: E402
from comun.validar import Campo, validar  # noqa: E402

SERVICIOS = ["auth", "usuarios", "productos", "pedidos", "entregas", "planeacion", "documentos", "zonas", "microhubs", "seguimiento",
             "inventario", "precios", "proveedores", "abastecimiento", "notificaciones",
             "demanda", "cobertura", "capacidad", "rutas", "costos", "punto-equilibrio", "simulacion", "surtido",
             "auditoria-monitoreo"]


def cargar(nombre):
    spec = importlib.util.spec_from_file_location(f"u_{nombre}", AQUI.parent / nombre.replace("-", "_") / "app.py")
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
    def test_los_ejemplos_oficiales_cumplen_los_xsd(self):
        ejemplos = sorted(config.EJEMPLOS_XML.glob("*.xml"))
        self.assertGreaterEqual(len(ejemplos), 170, "46 del contrato original, 54 de la Ola 1 y 71 de la Ola 2")
        for f in ejemplos:
            self.assertEqual(errores_xml(f.read_bytes()), [], f.name)

    def test_openapi_de_todos_los_servicios(self):
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


D = Decimal


class Precios(unittest.TestCase):
    """Las reglas de precio, sin base de datos."""

    @classmethod
    def setUpClass(cls):
        cls.pre = cargar("precios")

    def test_aplica_una_sola_promocion_la_de_mayor_descuento(self):
        promos = [{"tipo": "porcentaje", "valor": 10, "id": 1}, {"tipo": "monto", "valor": 8, "id": 2}]
        descuento, promo, limitado = self.pre.aplicar_promocion(100, promos, 30)
        self.assertEqual((descuento, promo["id"], limitado), (D("10.00"), 1, False), "10 % gana a $8 y no se suman")

    def test_el_descuento_no_pasa_del_tope(self):
        descuento, _, limitado = self.pre.aplicar_promocion(100, [{"tipo": "porcentaje", "valor": 50, "id": 1}], 30)
        self.assertEqual((descuento, limitado), (D("30.00"), True))

    def test_un_monto_no_deja_el_precio_en_negativo(self):
        descuento, _, _ = self.pre.aplicar_promocion(5, [{"tipo": "monto", "valor": 8, "id": 1}], 100)
        self.assertEqual(descuento, D("5.00"))

    def test_sin_promocion_no_hay_descuento(self):
        self.assertEqual(self.pre.aplicar_promocion(100, [], 30), (D("0.00"), None, False))

    def test_margen(self):
        self.assertEqual(self.pre.margen_pct(80, 60), 25.0)
        self.assertEqual(self.pre.margen_pct(50, 60), -20.0)
        self.assertIsNone(self.pre.margen_pct(80, None))

    def test_sensibilidad_con_elasticidad_supuesta(self):
        filas = self.pre.sensibilidad(100, 60, 100, -1.2, [10, -10])
        subida, bajada = filas
        # +10 % de precio con elasticidad -1.2: el volumen baja 12 %
        self.assertEqual((subida["precio"], subida["volumen_estimado"], subida["ingreso"]), (D("110.00"), 88.0, D("9680.00")))
        self.assertEqual((subida["ingreso_vs_base_pct"], subida["margen_total"]), (-3.2, D("4400.00")))
        self.assertEqual(subida["volumen_para_igualar_margen"], 80.0, "margen base 4,000 entre $50 de margen por unidad")
        self.assertEqual((bajada["precio"], bajada["volumen_estimado"], bajada["margen_total"]), (D("90.00"), 112.0, D("3360.00")))
        self.assertEqual(bajada["volumen_para_igualar_margen"], 133.3)

    def test_sensibilidad_sin_elasticidad_y_sin_costo(self):
        fila = self.pre.sensibilidad(100, None, 50, 0, [20])[0]
        self.assertEqual((fila["volumen_estimado"], fila["ingreso"]), (50.0, D("6000.00")))
        self.assertIsNone(fila["margen_total"])
        self.assertIsNone(fila["volumen_para_igualar_margen"])

    def test_si_el_precio_cae_bajo_el_costo_no_hay_volumen_que_iguale_el_margen(self):
        fila = self.pre.sensibilidad(100, 95, 100, -1, [-10])[0]
        self.assertIsNone(fila["volumen_para_igualar_margen"], "a $90 con costo $95 cada venta pierde")


class Abastecimiento(unittest.TestCase):
    """Las reglas de reposición, sin base de datos."""

    @classmethod
    def setUpClass(cls):
        cls.aba = cargar("abastecimiento")

    def test_cantidad_sugerida_llega_al_nivel_objetivo(self):
        f = self.aba.cantidad_sugerida
        self.assertEqual(f(disponible=4, minimo=10, en_camino=0, solicitado=0, factor=3), 26, "objetivo 30 - 4")
        self.assertEqual(f(4, 10, 10, 0, 3), 16, "lo que ya viene en camino no se vuelve a pedir")
        self.assertEqual(f(4, 10, 0, 12, 3), 14, "ni lo ya solicitado")
        self.assertEqual(f(4, 10, 40, 0, 3), 0, "nunca negativa")
        self.assertEqual(f(0, 10, 0, 0, 2.5), 25)

    def test_estado_de_la_orden(self):
        e = self.aba.estado_orden
        self.assertEqual(e([(10, 10), (4, 4)]), "recibida")
        self.assertEqual(e([(10, 5), (4, 0)]), "parcial")
        self.assertEqual(e([(10, 0)]), "emitida")

    @staticmethod
    def oferta(prov, prod, precio, dias, capacidad, minimo, pedido_minimo=0):
        return {"proveedor": {"id": prov, "clave": f"PV-{prov}", "nombre": f"Proveedor {prov}"}, "producto": {"id": prod, "nombre": "x"},
                "precio_compra": precio, "dias_entrega": dias, "capacidad_semanal": capacidad, "minimo_compra": minimo, "pedido_minimo": pedido_minimo}

    def test_elige_la_oferta_mas_barata_que_alcanza(self):
        ofertas = [self.oferta(1, 10, 7.0, 2, 500, 6), self.oferta(2, 10, 6.5, 1, 100, 12)]
        grupos, problemas = self.aba.planear_ordenes([{"producto_id": 10, "cantidad": 50}], ofertas)
        self.assertEqual((list(grupos), problemas), ([2], []), "50 unidades alcanzan en el proveedor 2, que es más barato")
        grupos, _ = self.aba.planear_ordenes([{"producto_id": 10, "cantidad": 200}], ofertas)
        self.assertEqual(list(grupos), [1], "200 rebasan la capacidad del proveedor 2")

    def test_a_igual_precio_gana_la_entrega_mas_rapida(self):
        ofertas = [self.oferta(1, 10, 7.0, 3, 500, 1), self.oferta(2, 10, 7.0, 1, 500, 1)]
        grupos, _ = self.aba.planear_ordenes([{"producto_id": 10, "cantidad": 20}], ofertas)
        self.assertEqual(list(grupos), [2])

    def test_respeta_la_compra_minima_y_avisa_si_nadie_surte(self):
        ofertas = [self.oferta(1, 10, 7.0, 2, 500, 6)]
        _, problemas = self.aba.planear_ordenes([{"producto_id": 10, "cantidad": 3}, {"producto_id": 11, "cantidad": 10}], ofertas)
        self.assertEqual(len(problemas), 2)
        self.assertIn("compra mínima", problemas[0]["mensaje"])
        self.assertIn("Ningún proveedor", problemas[1]["mensaje"])

    def test_la_orden_debe_alcanzar_el_pedido_minimo_del_proveedor(self):
        ofertas = [self.oferta(1, 10, 7.0, 2, 500, 1, pedido_minimo=800)]
        _, problemas = self.aba.planear_ordenes([{"producto_id": 10, "cantidad": 20}], ofertas)
        self.assertIn("pedido mínimo", problemas[0]["mensaje"])
        grupos, problemas = self.aba.planear_ordenes([{"producto_id": 10, "cantidad": 200}], ofertas)
        self.assertEqual((problemas, grupos[1]["total"]), ([], D("1400.0")))

    def test_con_proveedor_indicado_solo_cuenta_ese(self):
        ofertas = [self.oferta(1, 10, 7.0, 2, 500, 1), self.oferta(2, 10, 6.0, 1, 500, 1)]
        grupos, _ = self.aba.planear_ordenes([{"producto_id": 10, "cantidad": 20}], ofertas, proveedor_id=1)
        self.assertEqual(list(grupos), [1])


class Clientes(unittest.TestCase):
    """Un servicio llama a otro con el mismo JWT y la misma traza, y lo que responde se maneja sin red."""

    def tearDown(self):
        clientes.usar_transporte(None)

    def test_llamar_pasa_token_y_traza_al_otro_servicio(self):
        vistos = []
        clientes.usar_transporte(lambda *a: (vistos.append(a), (200, {"ok": True}))[1])
        status, datos = clientes.llamar("inventario", "GET", "inventario/alertas", params={"microhub_id": 1}, token="T")
        self.assertEqual((status, datos), (200, {"ok": True}))
        servicio, metodo, ruta, cuerpo, params, token, _ = vistos[0]
        self.assertEqual((servicio, metodo, ruta, params, token), ("inventario", "GET", "inventario/alertas", {"microhub_id": 1}, "T"))

    def test_un_servicio_caido_se_vuelve_503(self):
        def cae(*a):
            raise ConnectionError("sin respuesta")
        clientes.usar_transporte(cae)
        with self.assertRaises(ErrorApi) as e:
            clientes.llamar("proveedores", "GET", "proveedores/ofertas")
        self.assertEqual((e.exception.status, e.exception.codigo), (503, "SERVICIO_NO_DISPONIBLE"))

    def test_exigir_conserva_el_error_del_otro_servicio(self):
        error = {"error": {"codigo": "CONFLICTO", "mensaje": "No hay existencia suficiente.", "traza_id": "x"}}
        clientes.usar_transporte(lambda *a: (409, error))
        with self.assertRaises(ErrorApi) as e:
            clientes.exigir("inventario", "POST", "inventario/movimientos", cuerpo={})
        self.assertEqual((e.exception.status, e.exception.codigo), (409, "CONFLICTO"))
        clientes.usar_transporte(lambda *a: (500, None))
        with self.assertRaises(ErrorApi) as e:
            clientes.exigir("inventario", "GET", "inventario/alertas")
        self.assertEqual(e.exception.status, 503, "un fallo del otro servicio no se presenta como error propio")

    def test_mapa_junta_las_paginas_y_se_indexa_por_id(self):
        def pagina(servicio, metodo, ruta, cuerpo, params, token, traza):
            n = params["pagina"]
            return 200, {"datos": [{"id": n * 10 + i, "nombre": f"p{n}{i}"} for i in range(2)],
                         "paginacion": {"pagina": n, "por_pagina": 2, "total": 4, "paginas": 2}}
        clientes.usar_transporte(pagina)
        m = clientes.mapa("productos", "productos-sin-cache")
        self.assertEqual(sorted(m), [10, 11, 20, 21])

    def test_mapa_vacio_si_el_servicio_no_responde(self):
        def cae(*a):
            raise ConnectionError()
        clientes.usar_transporte(cae)
        self.assertEqual(clientes.mapa("productos", "otro-recurso"), {})


@unittest.skipUnless((AQUI.parent / "contratos").is_dir(), "el generador de contratos no está en esta imagen")
class GeneradorDeContratos(unittest.TestCase):
    """Cada ejemplo de las olas 1 y 2 existe en JSON y XML y es el que describe el generador."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(AQUI.parent / "contratos"))
        import ola1, ola2
        cls.olas = {"ola1": ola1, "ola2": ola2}

    def test_cada_ejemplo_esta_en_json_y_en_xml_y_el_xml_cumple_el_xsd(self):
        for ola, modulo in self.olas.items():
            for nombre, (raiz, datos) in modulo.EJEMPLOS.items():
                with self.subTest(f"{ola}: {nombre}"):
                    js = config.EJEMPLOS_JSON / f"{nombre}.ok.json"
                    self.assertTrue(js.exists(), js)
                    if raiz is not None:
                        xml_ej = config.EJEMPLOS_XML / f"{nombre}.ok.xml"
                        self.assertEqual(errores_xml(xml_ej.read_bytes()), [], xml_ej.name)
                        self.assertEqual(leer_xml(xml_ej.read_bytes())[0], raiz)

    def test_los_xsd_declaran_todas_las_raices(self):
        for ola, modulo in self.olas.items():
            for archivo, d in modulo.ARCHIVOS.items():
                texto = (config.CONTRATOS / f"{archivo}.xsd").read_text(encoding="utf-8")
                for raiz in d["raices"]:
                    with self.subTest(f"{ola}: {archivo}.{raiz}"):
                        self.assertIn(f'<xs:element name="{raiz}">', texto)

    def test_toda_respuesta_documentada_tiene_ejemplo(self):
        """Lo que la documentación (Swagger) promete con «Nombre.ok» existe como ejemplo JSON y XML."""
        faltan = []
        for s in SERVICIOS:
            app = cargar(s).app
            spec = app.test_client().get("/api/v1/openapi.json").get_json()
            for ruta, ops in spec["paths"].items():
                for metodo, op in ops.items():
                    for estado, r in op.get("responses", {}).items():
                        for tipo, c in (r.get("content") or {}).items() if estado.startswith("2") else ():
                            if tipo == "application/json" and "example" not in c and "examples" not in c:
                                faltan.append(f"{s} {metodo.upper()} {ruta} {estado}")
        self.assertEqual(faltan, [], "respuestas 2xx sin ejemplo en Swagger")


if __name__ == "__main__":
    unittest.main(verbosity=2)
