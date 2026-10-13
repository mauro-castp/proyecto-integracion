"""
test_contrato.py — Los ocho microservicios contra PostgreSQL y Redis reales.

Reproduce los recorridos con los que se probaron las apps (BackendReal de
app_escritorio/pruebas/Pruebas.cs y BackendRealTest.kt de Android) y además
comprueba el contrato en sus dos formatos:
  · Cada respuesta XML se valida contra los 9 XSD oficiales.
  · Cada respuesta JSON tiene las mismas llaves que el ejemplo oficial.

MongoDB: se usa mongomock (en memoria) salvo que MONGO_URL apunte a un
servidor real. PostgreSQL y Redis deben estar arriba con el modelo cargado
(scripts 01 a 08). Las pruebas cambian datos: usar una base de pruebas.

  cd servicios && python -m unittest -v pruebas.test_contrato
"""
import base64
import importlib
import json
import os
import sys
import unittest
import uuid
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
os.environ.setdefault("LOG_STDOUT", "0")

from comun import config, datos  # noqa: E402
from comun.esquemas import errores_xml  # noqa: E402
from comun.formatos import leer_xml  # noqa: E402
from pruebas.preparar_entregas import preparar  # noqa: E402

if not config.MONGO_URL:
    import mongomock
    datos.usar_mongo(mongomock.MongoClient(tz_aware=True)[config.MONGO_DB])

SERVICIOS = ["auth", "usuarios", "catalogos", "pedidos", "entregas", "planeacion", "documentos", "notificaciones"]
APPS = {s: importlib.import_module(f"{s}.app").app for s in SERVICIOS}
CLAVE = os.environ.get("MICROHUBS_CLAVE", "Codex#2026")
EJEMPLOS = config.EJEMPLOS_JSON
JPEG = bytes([0xFF, 0xD8, 0xFF, 0xE0, 0, 16, 74, 70, 73, 70, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0]) + bytes(range(256))
NS = "urn:microhubs:v1"


def ejemplo(nombre):
    return json.loads((EJEMPLOS / f"{nombre}.json").read_text(encoding="utf-8"))


def mismas_llaves(caso, real, oficial, opcionales=(), ruta="$"):
    """Las llaves de la respuesta coinciden con las del ejemplo oficial (recursivo)."""
    if isinstance(oficial, dict):
        caso.assertIsInstance(real, dict, ruta)
        faltan = set(oficial) - set(real) - set(opcionales)
        sobran = set(real) - set(oficial) - set(opcionales)
        caso.assertFalse(faltan or sobran, f"{ruta}: faltan {faltan} sobran {sobran}")
        for k in oficial:
            if k in real and real[k] is not None and oficial[k] is not None:
                mismas_llaves(caso, real[k], oficial[k], opcionales, f"{ruta}.{k}")
    elif isinstance(oficial, list) and oficial and real:
        mismas_llaves(caso, real[0], oficial[0], opcionales, f"{ruta}[0]")


def xml(raiz, campos):
    def el(k, v):
        if isinstance(v, dict):
            return f"<{k}>" + "".join(el(a, b) for a, b in v.items()) + f"</{k}>"
        return f"<{k}>{v}</{k}>"
    return f'<{raiz} xmlns="{NS}">' + "".join(el(k, v) for k, v in campos.items()) + f"</{raiz}>"


class Cliente:
    """Simula una app: JSON (Android) o XML (escritorio), con su token."""

    def __init__(self, caso, formato):
        self.caso, self.formato, self.token, self.renovacion, self.usuario = caso, formato, None, None, None

    def llamar(self, servicio, metodo, ruta, cuerpo=None, token=True, estado=None):
        tipo = "application/xml" if self.formato == "xml" else "application/json"
        enc = {"Accept": tipo}
        if token and self.token:
            enc["Authorization"] = f"Bearer {self.token}"
        datos_envio = None
        if cuerpo is not None:
            datos_envio = cuerpo if isinstance(cuerpo, str) else json.dumps(cuerpo)
            enc["Content-Type"] = tipo if isinstance(cuerpo, str) or self.formato == "json" else "application/json"
        r = APPS[servicio].test_client().open(f"/api/v1/{ruta}", method=metodo, data=datos_envio, headers=enc)
        if estado is not None:
            self.caso.assertEqual(r.status_code, estado, f"{metodo} {ruta}: {r.data[:400]!r}")
        if r.status_code == 204:
            return r, None
        self.caso.assertTrue(r.mimetype == tipo, f"{metodo} {ruta} devolvió {r.mimetype}")
        if self.formato == "xml":
            errores = errores_xml(r.data)
            self.caso.assertEqual(errores, [], f"{metodo} {ruta} no cumple el XSD: {errores}\n{r.data[:600]!r}")
            raiz, _, d = leer_xml(r.data)
            return r, (raiz, d)
        return r, r.get_json()

    def entrar(self, correo):
        if self.formato == "xml":
            _, (raiz, d) = self.llamar("auth", "POST", "auth/login", xml("login", {"correo": correo, "clave": CLAVE}), estado=200)
            self.caso.assertEqual(raiz, "sesion")
        else:
            _, d = self.llamar("auth", "POST", "auth/login", {"correo": correo, "clave": CLAVE, "dispositivo": "Prueba"},
                               estado=200)
        self.token, self.renovacion, self.usuario = d["token_acceso"], d["token_renovacion"], d["usuario"]
        return d


class T1Escritorio(unittest.TestCase):
    """El recorrido BackendReal de la app de escritorio (solo XML)."""

    def test_recorrido_planeador_auditor_y_sesion(self):
        plan = Cliente(self, "xml")
        s = plan.entrar("planeador@codex.mx")
        self.assertEqual(s["usuario"]["rol"], "planeador")
        token_viejo, renov_vieja = plan.token, plan.renovacion
        mala = Cliente(self, "xml")
        r, (raiz, err) = mala.llamar("auth", "POST", "auth/login", xml("login", {"correo": "planeador@codex.mx", "clave": "mala"}))
        self.assertEqual((r.status_code, raiz), (401, "error"))
        self.assertIn("Intento", err["mensaje"])

        # catálogo
        _, (raiz, d) = plan.llamar("catalogos", "GET", "productos?pagina=1&por_pagina=5&q=arroz", estado=200)
        self.assertEqual(raiz, "productos")
        self.assertTrue(d["datos"])
        prod = d["datos"]["producto"]["id"] if isinstance(d["datos"]["producto"], dict) else d["datos"]["producto"][0]["id"]
        r1, _ = plan.llamar("catalogos", "GET", "productos?pagina=1&por_pagina=5&q=arroz", estado=200)
        self.assertEqual(r1.headers["X-Cache"], "HIT", "la segunda consulta sale de Redis")
        self.assertEqual(plan.llamar("catalogos", "GET", f"productos/{prod}", estado=200)[1][0], "producto")
        self.assertEqual(plan.llamar("catalogos", "GET", "zonas", estado=200)[1][0], "zonas")
        self.assertEqual(plan.llamar("catalogos", "GET", "microhubs", estado=200)[1][0], "microhubs")

        # pedidos
        _, (_, d) = plan.llamar("pedidos", "GET", "pedidos?pagina=1&por_pagina=5&estado=entregado", estado=200)
        pid = d["datos"]["pedido"][0]["id"]
        _, (raiz, det) = plan.llamar("pedidos", "GET", f"pedidos/{pid}", estado=200)
        self.assertEqual(raiz, "pedido_detalle")
        self.assertTrue(det["lineas"])
        self.assertEqual(plan.llamar("pedidos", "GET", f"pedidos/{pid}/historial", estado=200)[1][0], "historial")
        self.assertEqual(plan.llamar("pedidos", "GET", "pedidos?estado=inventado")[0].status_code, 400)
        self.assertEqual(plan.llamar("pedidos", "GET", "pedidos?desde=2026-13-40")[0].status_code, 400)

        # cada pantalla de lista trae filas con id
        for srv, recurso in [("catalogos", "productos"), ("catalogos", "zonas"), ("catalogos", "microhubs"),
                             ("pedidos", "pedidos"), ("planeacion", "candidatos")]:
            _, (raiz, d) = plan.llamar(srv, "GET", f"{recurso}?pagina=1&por_pagina=20&q=", estado=200)
            self.assertEqual(raiz, recurso)
            self.assertTrue(d["datos"], recurso)

        # candidatos: crear, duplicado, editar, simular, decidir, filtrar
        clave = "D-" + uuid.uuid4().hex[:8]
        nuevo = {"clave": clave, "nombre": "Alianza Norte", "latitud": "25.7601", "longitud": "-100.3555",
                 "renta_estimada": "16000.00", "nomina_estimada": "40000.00", "servicios_estimados": "6500.00",
                 "otros_costos": "4500.00", "superficie_m2": "110", "capacidad_fisica": "130", "accesibilidad_vial": "7",
                 "zona_id": "3", "poblacion_cubierta": "5200", "radio_km": "1.5"}
        _, (raiz, c) = plan.llamar("planeacion", "POST", "candidatos", xml("candidato_nuevo", nuevo), estado=201)
        self.assertEqual((raiz, c["clave"], c["costo_fijo"]), ("candidato", clave, "67000.00"))
        self.assertEqual(plan.llamar("planeacion", "POST", "candidatos", xml("candidato_nuevo", nuevo))[0].status_code, 409)
        nuevo.update(nombre="Alianza Norte (editado)", renta_estimada="18000.00")
        _, (_, c2) = plan.llamar("planeacion", "PUT", f"candidatos/{c['id']}", xml("candidato_nuevo", nuevo), estado=200)
        self.assertEqual((c2["nombre"], c2["costo_fijo"]), ("Alianza Norte (editado)", "69000.00"))
        _, (raiz, sim) = plan.llamar("planeacion", "POST", f"candidatos/{c['id']}/simular", f'<simular xmlns="{NS}"/>', estado=200)
        self.assertEqual(raiz, "resultados")
        margen, mensual = float(sim["equilibrio"]["margen_pedido"]), float(sim["equilibrio"]["mensual"])
        self.assertLessEqual(abs(margen * mensual - 69000), margen, "usa los costos fijos del candidato")
        self.assertTrue(sim["explicacion"])
        r, _ = plan.llamar("planeacion", "POST", f"candidatos/{c['id']}/decision",
                           xml("decision", {"decision": "aceptado", "motivo": "ok"}))
        self.assertEqual(r.status_code, 422, "motivo corto: lo rechaza el XSD y el servicio")
        _, (_, dec) = plan.llamar("planeacion", "POST", f"candidatos/{c['id']}/decision",
                                  xml("decision", {"decision": "condicionado", "motivo": "Renegociar la renta antes de firmar."}),
                                  estado=200)
        self.assertEqual(dec["decision"], "condicionado")
        _, (_, f) = plan.llamar("planeacion", "GET", "candidatos?decision=condicionado&q=editado", estado=200)
        self.assertTrue(f["datos"])

        # simulación libre, escenarios y resumen (MongoDB)
        sup = {"demanda_diaria": "120", "operadores": "3", "repartidores": "4", "ticket": "135.00", "costo_entrega": "22.00",
               "margen_bruto": "0.28", "renta": "18000.00", "nomina": "42000.00", "servicios": "7000.00",
               "otros": "5000.00", "distancia_km": "2.4", "capacidad_fisica": "150"}
        _, (_, libre) = plan.llamar("planeacion", "POST", "simulaciones", xml("simulacion", {"candidato_id": "1", "supuestos": sup}),
                                    estado=200)
        self.assertEqual((libre["equilibrio"]["margen_pedido"], libre["equilibrio"]["mensual"]), ("15.80", "4557"))
        self.assertEqual(libre["decision"], "NO VIABLE CON LOS SUPUESTOS ACTUALES")
        _, (raiz, esc) = plan.llamar("planeacion", "POST", "escenarios",
                                     xml("escenario_nuevo", {"nombre": "Escenario de prueba " + clave, "candidato_id": c["id"],
                                                             "supuestos": sup}), estado=201)
        self.assertEqual(raiz, "escenario")
        self.assertEqual(plan.llamar("planeacion", "GET", f"escenarios/{esc['id']}", estado=200)[1][0], "escenario")
        self.assertEqual(plan.llamar("planeacion", "GET", "escenarios?pagina=1&por_pagina=5", estado=200)[1][0], "escenarios")
        _, (raiz, res) = plan.llamar("planeacion", "GET", "simulaciones/resumen", estado=200)
        self.assertGreaterEqual(int(res["total"]), 2)

        # permisos del auditor
        aud = Cliente(self, "xml")
        aud.entrar("auditor@codex.mx")
        self.assertTrue(aud.llamar("planeacion", "GET", "candidatos", estado=200)[1][1]["datos"])
        self.assertEqual(aud.llamar("planeacion", "POST", "candidatos", xml("candidato_nuevo", nuevo))[0].status_code, 403)
        self.assertEqual(aud.llamar("planeacion", "POST", "candidatos/1/simular", f'<simular xmlns="{NS}"/>')[0].status_code, 403)

        # token inválido → 401; renovación; cierre de sesión revoca acceso y renovación
        otra = Cliente(self, "xml")
        otra.entrar("planeador@codex.mx")
        otra.token = "token.invalido.firma"
        self.assertEqual(otra.llamar("pedidos", "GET", "pedidos?por_pagina=1")[0].status_code, 401)
        _, (raiz, t) = otra.llamar("auth", "POST", "auth/renovar", xml("renovar", {"token_renovacion": otra.renovacion}),
                                   token=False, estado=200)
        self.assertEqual(raiz, "tokens")
        otra.token = t["token_acceso"]
        otra.llamar("pedidos", "GET", "pedidos?por_pagina=1", estado=200)
        plan.llamar("auth", "POST", "auth/salir", xml("salir", {"token_renovacion": plan.renovacion}), estado=204)
        plan.token = token_viejo
        self.assertEqual(plan.llamar("pedidos", "GET", "pedidos")[0].status_code, 401)
        self.assertEqual(plan.llamar("auth", "POST", "auth/renovar", xml("renovar", {"token_renovacion": renov_vieja}),
                                     token=False)[0].status_code, 401)


class T2Android(unittest.TestCase):
    """El recorrido BackendRealTest de Android (solo JSON) y la forma de cada respuesta."""

    @classmethod
    def setUpClass(cls):
        cls.preparadas = preparar("repartidor1@codex.mx", 2)

    def test_recorrido_del_repartidor(self):
        api = Cliente(self, "json")
        s = api.entrar("repartidor1@codex.mx")
        mismas_llaves(self, s, ejemplo("Sesion.ok"))
        self.assertIn("entregas.cerrar", s["usuario"]["permisos"])
        _, perfil = api.llamar("usuarios", "GET", "usuarios/yo", estado=200)
        mismas_llaves(self, perfil, ejemplo("Perfil.ok"))
        r, err = Cliente(self, "json").llamar("auth", "POST", "auth/login", {"correo": "repartidor1@codex.mx", "clave": "x"})
        self.assertEqual(r.status_code, 401)
        self.assertIn("Intento", err["error"]["mensaje"])
        mismas_llaves(self, err, ejemplo("Error.token_invalido"))

        _, mias = api.llamar("entregas", "GET", "entregas/mias?pagina=1&por_pagina=20", estado=200)
        mismas_llaves(self, mias, ejemplo("EntregaLista.ok"))
        ids = {p["entrega_id"] for p in self.preparadas}
        paradas = [p for p in mias["datos"] if p["id"] in ids]
        self.assertEqual(len(paradas), 2)
        self.assertTrue(all(p["estado_pedido"] == "en_ruta" for p in paradas))
        p1, p2 = paradas
        _, det = api.llamar("entregas", "GET", f"entregas/{p1['id']}", estado=200)
        mismas_llaves(self, det, ejemplo("EntregaDetalle.ok"))
        self.assertTrue(det["lineas"])
        _, ped = api.llamar("pedidos", "GET", f"pedidos/{det['pedido_id']}", estado=200)
        self.assertEqual(ped["id"], det["pedido_id"])
        mismas_llaves(self, ped, ejemplo("PedidoDetalle.ok"))

        # evidencia → MongoDB; recorrido GPS → MongoDB
        _, doc = api.llamar("documentos", "POST", "documentos", {
            "nombre": f"evidencia-entrega-{p1['id']}.jpg", "tipo_mime": "image/jpeg",
            "contenido_base64": base64.b64encode(JPEG).decode(), "referencia": {"tipo": "entrega", "id": str(p1["id"])}},
            estado=201)
        mismas_llaves(self, doc, ejemplo("Documento.ok"))
        self.assertEqual(len(doc["id"]), 24)
        r, _ = api.llamar("documentos", "POST", "documentos", {
            "nombre": "x.jpg", "tipo_mime": "image/jpeg", "contenido_base64": base64.b64encode(b"%PDF-1.4").decode(),
            "referencia": {"tipo": "entrega", "id": str(p1["id"])}})
        self.assertEqual(r.status_code, 422, "la firma del archivo no es JPEG")
        _, lote = api.llamar("entregas", "POST", f"entregas/{p1['id']}/ubicaciones", {"puntos": [
            {"latitud": 25.7488, "longitud": -100.3608, "precision_m": 9.0, "capturado_en": "2026-10-12T18:28:00-06:00"},
            {"latitud": 25.7495, "longitud": -100.3610, "capturado_en": "2026-10-12T18:29:00-06:00"},
            {"latitud": 25.7491, "longitud": -100.3611, "precision_m": 8.0, "capturado_en": "2026-10-12T18:30:00-06:00"}]},
            estado=201)
        self.assertEqual(lote, {"recibidos": 3})
        _, rec = api.llamar("entregas", "GET", f"entregas/{p1['id']}/recorrido", estado=200)
        mismas_llaves(self, rec, ejemplo("Recorrido.ok"))
        self.assertEqual(rec["puntos"], 3)
        self.assertGreater(rec["distancia_km"], 0)

        # cierre «entregado», reintento idéntico (200 duplicado) y otro UUID (409)
        uuid1 = str(uuid.uuid4())
        cierre = {"resultado": "entregado", "monto_cobrado": det["total"], "cambio_entregado": 0.0,
                  "ubicacion": {"latitud": 25.7491, "longitud": -100.3611, "precision_m": 8.5},
                  "evidencia_ids": [doc["id"]], "capturado_en": "2026-10-12T18:30:00-06:00", "id_cliente_local": uuid1}
        r, malo = api.llamar("entregas", "POST", f"entregas/{p1['id']}/resultado", {**cierre, "monto_cobrado": 1.0})
        self.assertEqual(r.status_code, 422)
        self.assertEqual(malo["error"]["detalles"][0]["campo"], "monto_cobrado")
        _, res = api.llamar("entregas", "POST", f"entregas/{p1['id']}/resultado", cierre, estado=201)
        mismas_llaves(self, res, ejemplo("ResultadoEntregaRespuesta.ok"))
        self.assertEqual((res["estado_pedido"], res["duplicado"]), ("entregado", False))
        _, dup = api.llamar("entregas", "POST", f"entregas/{p1['id']}/resultado", cierre, estado=200)
        self.assertEqual((dup["estado_pedido"], dup["duplicado"]), ("entregado", True))
        api.llamar("entregas", "POST", f"entregas/{p1['id']}/resultado", {**cierre, "id_cliente_local": str(uuid.uuid4())},
                   estado=409)
        _, mias = api.llamar("entregas", "GET", "entregas/mias", estado=200)
        self.assertNotIn(p1["id"], [p["id"] for p in mias["datos"]], "la entrega cerrada sale de «Mis entregas»")
        self.assertEqual(api.llamar("entregas", "GET", f"entregas/{p1['id']}")[0].status_code, 404, "RN26")
        sync = datos.mongo().sincronizaciones_moviles.find_one({"operacion_uuid": uuid1})
        self.assertEqual((sync["estado"], sync["intentos"]), ("aplicada", 2))

        # cierre parcial por líneas: el motor devuelve las unidades al inventario
        _, det2 = api.llamar("entregas", "GET", f"entregas/{p2['id']}", estado=200)
        _, doc2 = api.llamar("documentos", "POST", "documentos", {
            "nombre": "ev.jpg", "tipo_mime": "image/jpeg", "contenido_base64": base64.b64encode(JPEG).decode(),
            "referencia": {"tipo": "entrega", "id": str(p2["id"])}}, estado=201)
        l0, l1 = det2["lineas"][0], det2["lineas"][1]
        parcial = {"resultado": "parcial", "monto_cobrado": 10.0, "cambio_entregado": 0.0,
                   "incidencia": "El cliente rechazó una línea.",
                   "lineas": [{"pedido_detalle_id": l0["pedido_detalle_id"], "cantidad_entregada": l0["cantidad"],
                               "cantidad_devuelta": 0},
                              {"pedido_detalle_id": l1["pedido_detalle_id"], "cantidad_entregada": 0,
                               "cantidad_devuelta": l1["cantidad"]}],
                   "ubicacion": {"latitud": 25.7491, "longitud": -100.3611}, "evidencia_ids": [doc2["id"]],
                   "capturado_en": "2026-10-12T18:40:00-06:00", "id_cliente_local": str(uuid.uuid4())}
        sin_motivo, _ = api.llamar("entregas", "POST", f"entregas/{p2['id']}/resultado", parcial)
        self.assertEqual(sin_motivo.status_code, 422, "RN28: la línea devuelta necesita motivo")
        parcial["lineas"][1]["motivo"] = "El cliente la rechazó."
        _, res2 = api.llamar("entregas", "POST", f"entregas/{p2['id']}/resultado", parcial, estado=201)
        self.assertEqual(res2["estado_pedido"], "entrega_parcial")
        mov = datos.consultar("SELECT count(*) AS n FROM movimiento_inventario WHERE tipo = 'devolucion_parcial' "
                              "AND referencia_id = %s", (det2["pedido_id"],), una=True)["n"]
        self.assertEqual(mov, 1)

        # bandeja de notificaciones (misma tabla que el web)
        _, bandeja = api.llamar("notificaciones", "GET", "notificaciones?pagina=1&por_pagina=20", estado=200)
        mismas_llaves(self, bandeja, ejemplo("NotificacionLista.ok"))
        aviso = next(a for a in bandeja["datos"] if not a["leida"])
        _, antes = api.llamar("notificaciones", "GET", "notificaciones/conteo", estado=200)
        _, leida = api.llamar("notificaciones", "POST", f"notificaciones/{aviso['id']}/leer", estado=200)
        self.assertTrue(leida["leida"])
        _, despues = api.llamar("notificaciones", "GET", "notificaciones/conteo", estado=200)
        self.assertEqual(despues["no_leidas"], antes["no_leidas"] - 1)

        # cerrar sesión revoca el acceso
        viejo = api.token
        api.llamar("auth", "POST", "auth/salir", {"token_renovacion": api.renovacion}, estado=204)
        api.token = viejo
        self.assertEqual(api.llamar("usuarios", "GET", "usuarios/yo")[0].status_code, 401)


class T3Contrato(unittest.TestCase):
    """Forma de cada recurso en ambos formatos, errores, límites y documentación."""

    @classmethod
    def setUpClass(cls):
        cls.adm_json, cls.adm_xml = Cliente(cls, "json"), Cliente(cls, "xml")
        cls.adm_json.caso = cls.adm_xml.caso = None

    def setUp(self):
        self.adm_json.caso = self.adm_xml.caso = self
        if not self.adm_json.token:
            self.adm_json.entrar("admin@codex.mx")
            self.adm_xml.entrar("admin@codex.mx")

    def test_listas_y_detalles_json_igual_al_ejemplo_y_xml_valido(self):
        casos = [("usuarios", "usuarios", "PerfilLista.ok"), ("catalogos", "productos", "ProductoLista.ok"),
                 ("catalogos", "zonas", "ZonaLista.ok"), ("catalogos", "microhubs", "MicrohubLista.ok"),
                 ("pedidos", "pedidos", "PedidoLista.ok"), ("entregas", "entregas", "EntregaLista.ok"),
                 ("planeacion", "candidatos", "CandidatoLista.ok"), ("planeacion", "escenarios", "EscenarioLista.ok"),
                 ("notificaciones", "notificaciones", "NotificacionLista.ok"), ("documentos", "documentos", "DocumentoLista.ok")]
        for srv, ruta, ej in casos:
            with self.subTest(ruta):
                _, d = self.adm_json.llamar(srv, "GET", f"{ruta}?pagina=1&por_pagina=3", estado=200)
                mismas_llaves(self, d, ejemplo(ej))
                self.adm_xml.llamar(srv, "GET", f"{ruta}?pagina=1&por_pagina=3", estado=200)
        _, cand = self.adm_json.llamar("planeacion", "GET", "candidatos/1", estado=200)
        mismas_llaves(self, cand, ejemplo("Candidato.ok"))
        _, z = self.adm_json.llamar("catalogos", "GET", "zonas/1", estado=200)
        mismas_llaves(self, z, ejemplo("Zona.ok"))
        _, h = self.adm_json.llamar("pedidos", "GET", "pedidos/1/historial", estado=200)
        mismas_llaves(self, h, ejemplo("Historial.ok"))
        _, v = self.adm_json.llamar("auth", "GET", "auth/validar", estado=200)
        mismas_llaves(self, v, ejemplo("Validacion.ok"))
        _, res = self.adm_json.llamar("documentos", "GET", "documentos/resumen", estado=200)
        mismas_llaves(self, res, ejemplo("DocumentosResumen.ok"))
        self.adm_xml.llamar("documentos", "GET", "documentos/resumen", estado=200)
        _, sr = self.adm_json.llamar("planeacion", "GET", "simulaciones/resumen", estado=200)
        mismas_llaves(self, sr, ejemplo("SimulacionesResumen.ok"))

    def test_errores_y_validacion(self):
        r, d = self.adm_json.llamar("planeacion", "POST", "candidatos", {"clave": "", "nombre": "x", "latitud": 99})
        self.assertEqual(r.status_code, 422)
        campos = {x["campo"] for x in d["error"]["detalles"]}
        self.assertTrue({"clave", "nombre", "latitud", "zona_id"} <= campos, campos)
        mismas_llaves(self, d, ejemplo("Error.validacion"))
        r, (raiz, e) = self.adm_xml.llamar("planeacion", "GET", "candidatos/999999")
        self.assertEqual((r.status_code, raiz, e["codigo"]), (404, "error", "NO_ENCONTRADO"))
        dtd = f'<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "b">]><login xmlns="{NS}"><correo>&a;</correo></login>'
        self.assertEqual(self.adm_xml.llamar("auth", "POST", "auth/login", dtd, token=False)[0].status_code, 400)
        r, (_, e) = self.adm_xml.llamar("auth", "POST", "auth/login", xml("login", {"correo": "sin-arroba", "clave": "x"}),
                                        token=False)
        self.assertEqual((r.status_code, e["codigo"]), (422, "VALIDACION"), "lo rechaza el XSD")
        r, _ = self.adm_json.llamar("pedidos", "GET", "pedidos?por_pagina=500")
        self.assertEqual(r.status_code, 400)
        r, _ = self.adm_json.llamar("pedidos", "POST", "pedidos/1/estado", {"estado": "entregado"})
        self.assertEqual(r.status_code, 409, "los cierres van por entregas")

    def test_sin_token_y_limite_de_consumo(self):
        sin = Cliente(self, "json")
        r, d = sin.llamar("pedidos", "GET", "pedidos")
        self.assertEqual((r.status_code, d["error"]["codigo"]), (401, "TOKEN_INVALIDO"))
        limite = config.LIMITE_POR_MINUTO
        config.LIMITE_POR_MINUTO = 3
        try:
            codigos = [sin.llamar("catalogos", "GET", "zonas")[0] for _ in range(5)]
            ultimo = codigos[-1]
            self.assertEqual(ultimo.status_code, 429)
            self.assertTrue(int(ultimo.headers["Retry-After"]) >= 1)
        finally:
            config.LIMITE_POR_MINUTO = limite
            datos.r_cache.delete(*datos.r_cache.keys("rate:catalogos:*") or ["x"])

    def test_salud_y_swagger_de_los_ocho(self):
        for s in SERVICIOS:
            with self.subTest(s):
                c = APPS[s].test_client()
                r = c.get("/api/v1/salud")
                self.assertEqual(r.status_code, 200, r.data)
                mismas_llaves(self, r.get_json(), ejemplo("Salud.ok"))
                self.assertEqual(errores_xml(c.get("/api/v1/salud", headers={"Accept": "application/xml"}).data), [])
                spec = c.get("/api/v1/openapi.json").get_json()
                self.assertEqual(spec["openapi"], "3.0.3")
                ops = [op for p in spec["paths"].values() for op in p.values()]
                self.assertGreaterEqual(len(ops), 2)
                con_ejemplos = [op for op in ops if any("application/xml" in (x.get("content") or {})
                                                        for x in op["responses"].values())]
                self.assertTrue(con_ejemplos, "hay ejemplos XML en Swagger")
                self.assertIn(b"swagger-ui", c.get("/api/v1/docs").data)

    def test_mongo_guarda_logs_y_metricas(self):
        db = datos.mongo()
        self.assertGreater(db.logs_tecnicos.count_documents({}), 0)
        log = db.logs_tecnicos.find_one({"usuario_id": {"$ne": None}})
        self.assertIsInstance(log["usuario_id"], int)
        self.assertNotIn("token", log)
        self.assertGreater(db.metricas_servicio.count_documents({}), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
