"""
test_almacen.py — Pruebas del almacén de archivos (carpeta local y Google Cloud Storage con un cliente simulado), de las URLs firmadas
y del /salud con estado del bucket y tiempo de respuesta. No necesitan bases de datos ni conexión a Google.

  cd servicios && python -m unittest -v pruebas.test_almacen
"""
import base64
import hashlib
import os
import sys
import tempfile
import time
import unittest
from datetime import timedelta
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
os.environ.setdefault("LOG_STDOUT", "0")

from comun import almacen, config  # noqa: E402
from comun.almacen import AlmacenGcs, AlmacenLocal, ErrorAlmacen, clave_objeto  # noqa: E402

JPG = b"\xff\xd8\xff\xe0" + b"contenido de prueba" * 20


# ----------------------------------------------------------------------------- clave del objeto
class ClaveObjeto(unittest.TestCase):
    def test_ruta_por_fecha_con_id_y_extension_segun_el_tipo(self):
        t = time.mktime((2026, 10, 12, 12, 0, 0, 0, 0, 0))
        self.assertEqual(clave_objeto("665f1c2e8a3b4d0012a7c9e1", "image/jpeg", t), "documentos/2026/10/665f1c2e8a3b4d0012a7c9e1.jpg")
        self.assertTrue(clave_objeto("abc", "application/pdf", t).endswith(".pdf"))
        self.assertTrue(clave_objeto("abc", "image/png", t).endswith(".png"))

    def test_nunca_usa_el_nombre_que_escribio_la_persona(self):
        # la clave solo lleva el id y el tipo: "../../etc/passwd" no puede colarse porque no se usa
        self.assertNotIn("..", clave_objeto("665f1c2e8a3b4d0012a7c9e1", "image/jpeg"))


# ----------------------------------------------------------------------------- almacén local
class AlmacenLocalPruebas(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.alm = AlmacenLocal(self.dir.name, secreto="secreto-de-prueba")

    def tearDown(self):
        self.dir.cleanup()

    def test_guardar_leer_y_borrar(self):
        self.alm.guardar("documentos/2026/10/a.jpg", JPG, "image/jpeg")
        self.assertTrue(self.alm.existe("documentos/2026/10/a.jpg"))
        self.assertEqual(self.alm.leer("documentos/2026/10/a.jpg"), JPG)
        self.alm.borrar("documentos/2026/10/a.jpg")
        self.assertFalse(self.alm.existe("documentos/2026/10/a.jpg"))
        self.alm.borrar("documentos/2026/10/a.jpg")                 # borrar lo que no existe no falla
        with self.assertRaises(ErrorAlmacen):
            self.alm.leer("documentos/2026/10/a.jpg")

    def test_no_sobrescribe_un_objeto_existente(self):
        self.alm.guardar("documentos/x.jpg", JPG, "image/jpeg")
        with self.assertRaises(ErrorAlmacen):
            self.alm.guardar("documentos/x.jpg", b"otro", "image/jpeg")
        self.assertEqual(self.alm.leer("documentos/x.jpg"), JPG)

    def test_no_sale_de_su_carpeta(self):
        for clave in ("../fuera.jpg", "documentos/../../fuera.jpg", "/etc/passwd"):
            with self.assertRaises(ErrorAlmacen):
                self.alm.guardar(clave, JPG, "image/jpeg")

    def test_disponible(self):
        self.assertTrue(self.alm.disponible())
        archivo = Path(self.dir.name) / "es_un_archivo"
        archivo.write_text("no es una carpeta")
        self.assertFalse(AlmacenLocal(archivo / "dentro").disponible())     # no se puede crear una carpeta dentro de un archivo

    def test_url_firmada_valida_y_con_caducidad(self):
        url, expira = self.alm.url_firmada("documentos/a.jpg", 300, "evidencia 1.jpg", "image/jpeg")
        self.assertTrue(url.startswith(f"{config.PREFIJO}/documentos/descarga?k="))
        self.assertAlmostEqual(expira, time.time() + 300, delta=3)
        from urllib.parse import parse_qs, urlparse
        q = {k: v[0] for k, v in parse_qs(urlparse(url).query).items()}
        self.assertTrue(self.alm.firma_valida(q["k"], q["e"], q["n"], q["t"], q["s"]))
        with mock.patch("time.time", return_value=expira + 1):         # ya caducó
            self.assertFalse(self.alm.firma_valida(q["k"], q["e"], q["n"], q["t"], q["s"]))

    def test_url_firmada_alterada_o_de_otro_secreto_no_vale(self):
        url, _ = self.alm.url_firmada("documentos/a.jpg", 300, "a.jpg", "image/jpeg")
        from urllib.parse import parse_qs, urlparse
        q = {k: v[0] for k, v in parse_qs(urlparse(url).query).items()}
        self.assertFalse(self.alm.firma_valida("documentos/b.jpg", q["e"], q["n"], q["t"], q["s"]))     # otro objeto
        self.assertFalse(self.alm.firma_valida(q["k"], int(q["e"]) + 9999, q["n"], q["t"], q["s"]))     # más vigencia
        self.assertFalse(self.alm.firma_valida(q["k"], q["e"], "otro.jpg", q["t"], q["s"]))             # otro nombre
        self.assertFalse(self.alm.firma_valida(q["k"], q["e"], q["n"], "application/pdf", q["s"]))      # otro tipo
        self.assertFalse(self.alm.firma_valida(q["k"], q["e"], q["n"], q["t"], ""))                     # sin firma
        self.assertFalse(self.alm.firma_valida(q["k"], "no-es-numero", q["n"], q["t"], q["s"]))
        self.assertFalse(AlmacenLocal(self.dir.name, secreto="otro").firma_valida(q["k"], q["e"], q["n"], q["t"], q["s"]))


# ----------------------------------------------------------------------------- Google Cloud Storage (cliente simulado)
class BlobFalso:
    def __init__(self, bucket, clave):
        self.bucket, self.clave, self.metadata = bucket, clave, None

    def upload_from_string(self, contenido, content_type=None, if_generation_match=None):
        if self.bucket.falla:
            raise RuntimeError("503 Service Unavailable")
        if if_generation_match == 0 and self.clave in self.bucket.objetos:
            raise RuntimeError("412 Precondition Failed")
        self.bucket.objetos[self.clave] = (contenido, content_type, self.metadata, if_generation_match)

    def download_as_bytes(self):
        if self.clave not in self.bucket.objetos:
            raise RuntimeError("404 Not Found")
        return self.bucket.objetos[self.clave][0]

    def delete(self):
        if self.clave not in self.bucket.objetos:
            raise RuntimeError("404 Not Found")
        del self.bucket.objetos[self.clave]

    def exists(self):
        return self.clave in self.bucket.objetos

    def generate_signed_url(self, **kw):
        self.bucket.firmas.append(kw)
        if self.bucket.falla_firma:
            raise RuntimeError("signBlob denegado")
        return f"https://storage.googleapis.com/{self.bucket.nombre}/{self.clave}?X-Goog-Signature=firmada"


class BucketFalso:
    def __init__(self, nombre):
        self.nombre, self.objetos, self.firmas, self.falla, self.falla_firma = nombre, {}, [], False, False

    def blob(self, clave):
        return BlobFalso(self, clave)


class CredencialesFalsas:
    token = "token-de-acceso"
    expired = False
    service_account_email = "microhubs-vm@proyecto.iam.gserviceaccount.com"


class ClienteFalso:
    _credentials = CredencialesFalsas()

    def __init__(self):
        self.buckets = {}
        self.listado_falla = False

    def bucket(self, nombre):
        return self.buckets.setdefault(nombre, BucketFalso(nombre))

    def list_blobs(self, nombre, max_results=None):
        if self.listado_falla:
            raise RuntimeError("403 Forbidden")
        return iter([])


class AlmacenGcsPruebas(unittest.TestCase):
    def setUp(self):
        self.cli = ClienteFalso()
        self.alm = AlmacenGcs("mi-bucket", cliente=self.cli)
        self.bucket = self.cli.bucket("mi-bucket")

    def test_exige_nombre_de_bucket(self):
        with self.assertRaises(ErrorAlmacen):
            AlmacenGcs("", cliente=self.cli)

    def test_guardar_no_sobrescribe_y_lleva_el_sha256_como_metadato(self):
        sha = hashlib.sha256(JPG).hexdigest()
        self.alm.guardar("documentos/a.jpg", JPG, "image/jpeg", sha)
        contenido, tipo, meta, precondicion = self.bucket.objetos["documentos/a.jpg"]
        self.assertEqual((contenido, tipo, meta, precondicion), (JPG, "image/jpeg", {"sha256": sha}, 0))   # 0 = solo si no existe
        with self.assertRaises(ErrorAlmacen):                                                                # ya existe
            self.alm.guardar("documentos/a.jpg", b"otro", "image/jpeg", sha)

    def test_fallos_de_google_se_vuelven_error_del_almacen(self):
        self.bucket.falla = True
        with self.assertRaises(ErrorAlmacen):
            self.alm.guardar("documentos/a.jpg", JPG, "image/jpeg")

    def test_leer_y_borrar(self):
        self.alm.guardar("documentos/a.jpg", JPG, "image/jpeg")
        self.assertEqual(self.alm.leer("documentos/a.jpg"), JPG)
        self.assertTrue(self.alm.existe("documentos/a.jpg"))
        self.alm.borrar("documentos/a.jpg")
        self.alm.borrar("documentos/a.jpg")                         # ya no existe: 404 se tolera
        with self.assertRaises(ErrorAlmacen):
            self.alm.leer("documentos/a.jpg")

    def test_disponible_solo_pide_listar_objetos(self):
        self.assertTrue(self.alm.disponible())
        self.cli.listado_falla = True
        self.assertFalse(self.alm.disponible())

    def test_url_firmada_v4_con_la_identidad_de_la_vm_y_sin_llaves(self):
        url, expira = self.alm.url_firmada("documentos/a.jpg", 300, "evidencia 1.jpg", "image/jpeg")
        self.assertIn("X-Goog-Signature", url)
        self.assertAlmostEqual(expira, time.time() + 300, delta=3)
        kw = self.bucket.firmas[-1]
        self.assertEqual(kw["version"], "v4")
        self.assertEqual(kw["method"], "GET")
        self.assertEqual(kw["expiration"], timedelta(seconds=300))
        self.assertEqual(kw["service_account_email"], CredencialesFalsas.service_account_email)
        self.assertEqual(kw["access_token"], "token-de-acceso")                  # firma por IAM, no con una llave privada
        self.assertEqual(kw["response_type"], "image/jpeg")
        self.assertIn("attachment", kw["response_disposition"])
        self.assertIn("evidencia%201.jpg", kw["response_disposition"])           # el nombre va codificado

    def test_si_no_se_puede_firmar_es_error_del_almacen(self):
        self.bucket.falla_firma = True
        with self.assertRaises(ErrorAlmacen):
            self.alm.url_firmada("documentos/a.jpg", 300, "a.jpg", "image/jpeg")


# ----------------------------------------------------------------------------- selección por entorno
class SeleccionDelAlmacen(unittest.TestCase):
    def tearDown(self):
        almacen.usar(None)

    def test_local_por_omision_y_gcs_exige_bucket(self):
        almacen.usar(None)
        with mock.patch.object(config, "ALMACEN", "local"), mock.patch.object(config, "ALMACEN_DIR", tempfile.gettempdir()):
            self.assertEqual(almacen.obtener().nombre, "local")
        almacen.usar(None)
        with mock.patch.object(config, "ALMACEN", "gcs"), mock.patch.object(config, "GCS_BUCKET", ""):
            with self.assertRaises(ErrorAlmacen):
                almacen.obtener()

    def test_valor_desconocido_es_error(self):
        almacen.usar(None)
        with mock.patch.object(config, "ALMACEN", "s3"):
            with self.assertRaises(ErrorAlmacen):
                almacen.obtener()


# ----------------------------------------------------------------------------- /salud con bucket y tiempo de respuesta
class SaludConBucket(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from comun.base import crear_app
        cls.app = crear_app("prueba-bucket", "Prueba", "Prueba de salud.", 5999, dependencias=("bucket",))
        cls.app_sin = crear_app("prueba-sin-bucket", "Prueba", "Prueba de salud.", 5998, dependencias=())

    def tearDown(self):
        almacen.usar(None)

    def test_bucket_ok_tiempo_y_version(self):
        with tempfile.TemporaryDirectory() as d:
            almacen.usar(AlmacenLocal(d))
            r = self.app.test_client().get("/api/v1/salud")
        cuerpo = r.get_json()
        self.assertEqual(r.status_code, 200)
        self.assertEqual(cuerpo["estado"], "ok")
        self.assertEqual(cuerpo["dependencias"], {"postgres": "no_aplica", "redis": "no_aplica", "mongo": "no_aplica", "bucket": "ok"})
        self.assertIsInstance(cuerpo["tiempo_ms"], (int, float))
        self.assertGreaterEqual(cuerpo["tiempo_ms"], 0)
        self.assertEqual(cuerpo["version"], config.VERSION)

    def test_bucket_caido_deja_el_servicio_degradado_con_503(self):
        cli = ClienteFalso()
        cli.listado_falla = True
        almacen.usar(AlmacenGcs("mi-bucket", cliente=cli))
        r = self.app.test_client().get("/api/v1/salud")
        self.assertEqual(r.status_code, 503)
        self.assertEqual(r.get_json()["estado"], "degradado")
        self.assertEqual(r.get_json()["dependencias"]["bucket"], "error")

    def test_un_servicio_que_no_usa_el_bucket_no_se_degrada_si_el_bucket_cae(self):
        cli = ClienteFalso()
        cli.listado_falla = True
        almacen.usar(AlmacenGcs("mi-bucket", cliente=cli))
        r = self.app_sin.test_client().get("/api/v1/salud")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["dependencias"]["bucket"], "no_aplica")

    def test_mal_configurado_tambien_es_error_y_no_excepcion(self):
        with mock.patch.object(config, "ALMACEN", "gcs"), mock.patch.object(config, "GCS_BUCKET", ""):
            almacen.usar(None)
            r = self.app.test_client().get("/api/v1/salud")
        self.assertEqual(r.status_code, 503)
        self.assertEqual(r.get_json()["dependencias"]["bucket"], "error")


# ----------------------------------------------------------------------------- servicio de documentos (sin bases de datos)
class DocumentosSinBaseDeDatos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(AQUI.parent / "documentos"))
        import importlib.util
        spec = importlib.util.spec_from_file_location("documentos_app", AQUI.parent / "documentos" / "app.py")
        cls.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.alm = AlmacenLocal(self.dir.name, secreto="secreto-de-prueba")
        almacen.usar(self.alm)
        self.cli = self.mod.app.test_client()
        self.parche = mock.patch("comun.base._limitar", lambda: None)       # el límite de consumo usa Redis
        self.parche.start()

    def tearDown(self):
        self.parche.stop()
        almacen.usar(None)
        self.dir.cleanup()

    def test_descarga_con_enlace_firmado(self):
        self.alm.guardar("documentos/2026/10/a.jpg", JPG, "image/jpeg")
        url, _ = self.alm.url_firmada("documentos/2026/10/a.jpg", 300, "evidencia.jpg", "image/jpeg")
        r = self.cli.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data, JPG)
        self.assertEqual(r.headers["Content-Type"], "image/jpeg")
        self.assertIn("attachment", r.headers["Content-Disposition"])

    def test_descarga_rechaza_firma_alterada_o_vencida(self):
        self.alm.guardar("documentos/2026/10/a.jpg", JPG, "image/jpeg")
        url, expira = self.alm.url_firmada("documentos/2026/10/a.jpg", 300, "evidencia.jpg", "image/jpeg")
        self.assertEqual(self.cli.get(url[:-3] + "xxx").status_code, 403)
        self.assertEqual(self.cli.get(url.replace("a.jpg", "b.jpg")).status_code, 403)
        with mock.patch("time.time", return_value=expira + 5):
            r = self.cli.get(url)
        self.assertEqual(r.status_code, 403)
        self.assertEqual(r.get_json()["error"]["codigo"], "PROHIBIDO")

    def test_descarga_no_existe_cuando_el_almacen_es_gcs(self):
        almacen.usar(AlmacenGcs("mi-bucket", cliente=ClienteFalso()))
        r = self.cli.get(f"{config.PREFIJO}/documentos/descarga?k=documentos/a.jpg&e=9999999999&n=a&t=image/jpeg&s=x")
        self.assertEqual(r.status_code, 404)

    def test_metadatos_de_un_documento_antiguo_con_el_contenido_en_mongodb(self):
        import datetime as dt
        antiguo = {"_id": "665f1c2e8a3b4d0012a7c9e1", "nombre": "a.jpg", "tipo_mime": "image/jpeg", "tamano_bytes": 10, "sha256": "x" * 64,
                   "referencia": {"tipo": "entrega", "id": "61"}, "subido_por": 7, "creado_en": dt.datetime(2026, 10, 12, 18, 29, 30)}
        m = self.mod.metadatos(antiguo)
        self.assertEqual((m["ruta"], m["privacidad"], m["estado"]), ("", "privado", "activo"))
        self.assertEqual(m["metadatos"], {"almacen": "mongodb", "origen": "api"})

    def test_metadatos_nuevos_incluyen_ruta_privacidad_estado_y_almacen(self):
        import datetime as dt
        nuevo = {"_id": "665f1c2e8a3b4d0012a7c9e1", "nombre": "a.jpg", "tipo_mime": "image/jpeg", "tamano_bytes": len(JPG),
                 "sha256": hashlib.sha256(JPG).hexdigest(), "referencia": {"tipo": "pedido", "id": "5"}, "subido_por": 3,
                 "creado_en": dt.datetime(2026, 10, 12, 18, 29, 30), "ruta": "documentos/2026/10/665f1c2e8a3b4d0012a7c9e1.jpg",
                 "privacidad": "interno", "estado": "activo", "metadatos": {"almacen": "gcs", "origen": "movil"}}
        m = self.mod.metadatos(nuevo)
        self.assertEqual((m["ruta"], m["privacidad"], m["estado"]), (nuevo["ruta"], "interno", "activo"))
        self.assertEqual(m["metadatos"], {"almacen": "gcs", "origen": "movil"})
        self.assertNotIn("contenido", m)                                    # la base no devuelve ni guarda el archivo

    def test_filtro_de_visibilidad_por_rol_y_sin_eliminados(self):
        from flask import g
        with self.mod.app.test_request_context("/"):
            g.usuario = {"id": 7, "rol": "repartidor"}
            f = self.mod._filtro_visible()
            self.assertEqual(f["estado"], {"$ne": "eliminado"})
            self.assertEqual(f["$or"], [{"subido_por": 7}, {"privacidad": "interno"}])
            g.usuario = {"id": 1, "rol": "auditor"}
            self.assertEqual(self.mod._filtro_visible(), {"estado": {"$ne": "eliminado"}})


# ----------------------------------------------------------------------------- migracion de documentos antiguos (contenido en MongoDB)
class MigracionAlAlmacen(unittest.TestCase):
    def setUp(self):
        import datetime as dt
        import importlib.util
        try:
            import mongomock
        except ImportError:
            self.skipTest("Falta mongomock (en la nube estas pruebas se hacen con MongoDB real).")
        from bson import Binary
        spec = importlib.util.spec_from_file_location("migrar_a_almacen", AQUI.parent / "documentos" / "migrar_a_almacen.py")
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        self.dir = tempfile.TemporaryDirectory()
        self.alm = AlmacenLocal(self.dir.name)
        self.db = mongomock.MongoClient(tz_aware=True)["prueba"]
        base = {"nombre": "a.jpg", "tipo_mime": "image/jpeg", "tamano_bytes": len(JPG), "sha256": hashlib.sha256(JPG).hexdigest(),
                "referencia": {"tipo": "entrega", "id": "1"}, "subido_por": 7, "creado_en": dt.datetime(2026, 10, 12, 18, 0, tzinfo=dt.timezone.utc)}
        self.bueno = self.db.documentos.insert_one({**base, "contenido": Binary(JPG)}).inserted_id
        self.danado = self.db.documentos.insert_one({**base, "sha256": "0" * 64, "contenido": Binary(JPG)}).inserted_id
        self.nuevo = self.db.documentos.insert_one({**base, "ruta": "documentos/2026/10/ya.jpg"}).inserted_id

    def tearDown(self):
        self.dir.cleanup()

    def test_simular_no_cambia_nada(self):
        r = self.mod.migrar(simular=True, db=self.db, alm=self.alm)
        self.assertEqual((r["pendientes"], r["movidos"], r["sha_distinto"]), (1, 0, 1))
        self.assertIn("contenido", self.db.documentos.find_one({"_id": self.bueno}))

    def test_mueve_el_archivo_y_deja_solo_sus_datos(self):
        r = self.mod.migrar(db=self.db, alm=self.alm)
        self.assertEqual((r["movidos"], r["sha_distinto"], r["errores"]), (1, 1, 0))
        d = self.db.documentos.find_one({"_id": self.bueno})
        self.assertNotIn("contenido", d)                                       # la base ya no guarda el archivo
        self.assertEqual(d["ruta"], f"documentos/2026/10/{self.bueno}.jpg")
        self.assertEqual((d["privacidad"], d["estado"], d["metadatos"]["almacen"]), ("privado", "activo", "local"))
        self.assertEqual(self.alm.leer(d["ruta"]), JPG)

    def test_no_mueve_lo_que_esta_danado_y_es_repetible(self):
        self.mod.migrar(db=self.db, alm=self.alm)
        self.assertIn("contenido", self.db.documentos.find_one({"_id": self.danado}))   # SHA distinto: intacto
        otra = self.mod.migrar(db=self.db, alm=self.alm)
        self.assertEqual((otra["movidos"], otra["sha_distinto"]), (0, 1))                # ya no hay nada más que mover

    def test_una_corrida_interrumpida_se_retoma(self):
        ruta = f"documentos/2026/10/{self.bueno}.jpg"
        self.alm.guardar(ruta, JPG, "image/jpeg")                                         # el objeto ya estaba, el registro no
        r = self.mod.migrar(db=self.db, alm=self.alm)
        self.assertEqual((r["movidos"], r["ya_en_almacen"]), (1, 1))


if __name__ == "__main__":
    unittest.main()
