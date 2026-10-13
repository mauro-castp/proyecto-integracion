"""
test_web_integracion.py — El sistema web como cliente de los microservicios.

Levanta los ocho servicios en sus puertos reales (5101 a 5108, hilos de un
mismo proceso para compartir MongoDB en memoria) y recorre las pantallas del
web que los consumen con una sesión real de administrador:

  1. Un repartidor cierra una entrega por los servicios (foto, GPS, cierre).
  2. El web muestra el estado de los 8 servicios, agregaciones de MongoDB y
     una respuesta XML obtenida de catálogos.
  3. El web arma el detalle del pedido con pedidos, entregas y documentos:
     historial, recorrido GPS y la evidencia de la entrega.
  4. Desde el web se adjunta un documento al pedido; viaja al servicio de
     documentos y se guarda en MongoDB.
  5. Sin servicios, el web no se cae: muestra el aviso.

  cd servicios && python -m unittest -v pruebas.test_web_integracion
"""
import base64
import importlib
import importlib.util
import io
import os
import sys
import threading
import unittest
import uuid
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
os.environ.setdefault("LOG_STDOUT", "0")
os.environ.setdefault("SECRET_KEY", "prueba-integracion-web")
os.environ["MICROSERVICIOS_URL"] = "http://127.0.0.1:{puerto}"
# El web va primero en la ruta: su módulo «planeacion» no debe confundirse con la carpeta del servicio.
sys.path.insert(0, str(AQUI.parent))
sys.path.insert(0, str(RAIZ / "sistema_web"))

from werkzeug.serving import WSGIRequestHandler, make_server  # noqa: E402


class _Silencio(WSGIRequestHandler):
    def log_request(self, *a, **kw):
        pass

from comun import config, datos  # noqa: E402
from pruebas.preparar_entregas import preparar  # noqa: E402

if not config.MONGO_URL:
    import mongomock
    datos.usar_mongo(mongomock.MongoClient(tz_aware=True)[config.MONGO_DB])

PUERTOS = {"auth": 5101, "usuarios": 5102, "catalogos": 5103, "pedidos": 5104, "entregas": 5105,
           "planeacion": 5106, "documentos": 5107, "notificaciones": 5108}
JPEG = bytes([0xFF, 0xD8, 0xFF, 0xE0, 0, 16, 74, 70, 73, 70, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0]) + bytes(range(256))
_servidores = []
APPS = {}


def servicio(nombre):
    """Carga servicios/<nombre>/app.py con un nombre único (el web también tiene un módulo «planeacion»)."""
    if nombre not in APPS:
        spec = importlib.util.spec_from_file_location(f"svc_{nombre}", AQUI.parent / nombre / "app.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        APPS[nombre] = mod.app
    return APPS[nombre]


def setUpModule():
    for s, p in PUERTOS.items():
        app = servicio(s)
        srv = make_server("127.0.0.1", p, app, threaded=True, request_handler=_Silencio)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        _servidores.append(srv)


def tearDownModule():
    for srv in _servidores:
        srv.shutdown()


class WebConMicroservicios(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        import app as web
        import nucleo
        cls.web = web.app
        cls.web.config["TESTING"] = True
        with cls.web.test_request_context():
            cls.token_admin = nucleo.emitir_token({"id": 1, "rol": "administrador", "nombre": "Admin", "microhub_id": None})
        # Un repartidor cierra una entrega usando SOLO los servicios.
        ent = preparar("repartidor1@codex.mx", 1)[0]
        cls.pid, cls.eid = ent["pedido_id"], ent["entrega_id"]
        ap = {s: servicio(s).test_client() for s in PUERTOS}
        s = ap["auth"].post("/api/v1/auth/login", json={"correo": "repartidor1@codex.mx", "clave": "Codex#2026"}).get_json()
        h = {"Authorization": f"Bearer {s['token_acceso']}"}
        det = ap["entregas"].get(f"/api/v1/entregas/{cls.eid}", headers=h).get_json()
        doc = ap["documentos"].post("/api/v1/documentos", headers=h, json={
            "nombre": f"evidencia-entrega-{cls.eid}.jpg", "tipo_mime": "image/jpeg",
            "contenido_base64": base64.b64encode(JPEG).decode(), "referencia": {"tipo": "entrega", "id": str(cls.eid)}}).get_json()
        cls.doc_id = doc["id"]
        ap["entregas"].post(f"/api/v1/entregas/{cls.eid}/ubicaciones", headers=h, json={"puntos": [
            {"latitud": 25.7480, "longitud": -100.3600, "capturado_en": "2026-10-12T18:20:00-06:00"},
            {"latitud": 25.7491, "longitud": -100.3611, "capturado_en": "2026-10-12T18:25:00-06:00"}]})
        r = ap["entregas"].post(f"/api/v1/entregas/{cls.eid}/resultado", headers=h, json={
            "resultado": "entregado", "monto_cobrado": det["total"], "cambio_entregado": 0,
            "ubicacion": {"latitud": 25.7491, "longitud": -100.3611}, "evidencia_ids": [cls.doc_id],
            "capturado_en": "2026-10-12T18:25:00-06:00", "id_cliente_local": str(uuid.uuid4())})
        assert r.status_code == 201, r.data

    def cliente(self):
        c = self.web.test_client()
        c.set_cookie("sesion", self.token_admin)
        with c.session_transaction() as s:
            s["web_csrf"] = "csrf-de-prueba"
        return c

    def test_1_tablero_de_microservicios(self):
        r = self.cliente().get("/web/servicios")
        self.assertEqual(r.status_code, 200)
        html = r.get_data(as_text=True)
        self.assertEqual(html.count('<span class="pill verde">ok</span>'), 8, "los 8 servicios responden por HTTP")
        self.assertIn("urn:microhubs:v1", html, "el web recibe y muestra una respuesta XML del servicio")
        self.assertIn("Documentos por tipo", html)

    def test_2_pedido_armado_con_tres_servicios(self):
        r = self.cliente().get(f"/web/servicios/pedido/{self.pid}")
        self.assertEqual(r.status_code, 200)
        html = r.get_data(as_text=True)
        self.assertIn("entregado", html)
        self.assertIn("Puntos GPS (MongoDB)", html)
        self.assertIn(f"evidencia-entrega-{self.eid}.jpg", html, "la evidencia viene del servicio de documentos")
        self.assertIn("/api/v1/entregas/", html)
        self.assertNotIn('pill rojo', html, "todas las llamadas del web a los servicios responden 2xx")

    def test_3_adjuntar_desde_el_web_va_a_mongodb(self):
        c = self.cliente()
        r = c.post(f"/web/servicios/pedido/{self.pid}", data={
            "csrf": "csrf-de-prueba", "archivo": (io.BytesIO(JPEG), "comprobante.jpg")},
            content_type="multipart/form-data")
        self.assertEqual(r.status_code, 302)
        guardado = datos.mongo().documentos.find_one({"referencia.tipo": "pedido", "referencia.id": str(self.pid)})
        self.assertIsNotNone(guardado, "el documento quedó en MongoDB")
        self.assertEqual(guardado["subido_por"], 1)
        r = c.get(f"/web/servicios/documento/{guardado['_id']}?ver=1")
        self.assertEqual((r.status_code, r.mimetype, r.data), (200, "image/jpeg", JPEG))

    def test_4_csrf_y_sesion(self):
        c = self.cliente()
        self.assertEqual(c.post(f"/web/servicios/pedido/{self.pid}", data={"csrf": "otro"}).status_code, 400)
        anon = self.web.test_client()
        self.assertEqual(anon.get("/web/servicios").status_code, 302, "sin sesión manda al login")

    def test_5_sin_servicios_el_web_sigue(self):
        import integracion
        original = integracion.PLANTILLA
        integracion.PLANTILLA = "http://127.0.0.1:1{puerto}"            # puertos sin servicio
        try:
            r = self.cliente().get("/web/servicios")
            self.assertEqual(r.status_code, 200)
            self.assertIn("sin respuesta", r.get_data(as_text=True))
        finally:
            integracion.PLANTILLA = original


if __name__ == "__main__":
    unittest.main(verbosity=2)
