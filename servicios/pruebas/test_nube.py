"""
test_nube.py — Archivos y URLs firmadas contra Google Cloud Storage REAL (solo corren con ALMACEN=gcs y GCS_BUCKET; si no, se omiten).
Usan PostgreSQL, Redis y MongoDB reales y las cuentas de demostración del proyecto.

  # en la VM de GCP (con el sistema arriba):
  set -a; . ~/microhubs/.env; set +a; cd ~/microhubs && servicios/pruebas/correr.sh test pruebas.test_nube -v

Demuestra: el archivo va al bucket y MongoDB conserva solo sus datos; la URL firmada descarga sin credenciales, caduca y no se puede
alterar; borrar quita el objeto; y cuando el bucket no responde el servicio informa 503, queda degradado en /salud y NO deja registros
a medias.
"""
import base64
import hashlib
import json
import os
import sys
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
os.environ.setdefault("LOG_STDOUT", "0")

from bson import ObjectId  # noqa: E402

from comun import almacen, config, datos  # noqa: E402
from pruebas.preparar_entregas import preparar  # noqa: E402
from pruebas.test_contrato import APPS, JPEG, Cliente, ejemplo, mismas_llaves  # noqa: E402

EN_LA_NUBE = config.ALMACEN == "gcs" and bool(config.GCS_BUCKET)


def bajar(url, esperar_error=False):
    """Descarga con una petición sin credenciales (como lo haría un cliente con la URL firmada)."""
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            return r.status, r.read(), r.headers.get("Content-Type")
    except urllib.error.HTTPError as e:
        if not esperar_error:
            raise
        return e.code, e.read(), e.headers.get("Content-Type")


@unittest.skipUnless(EN_LA_NUBE, "Necesita ALMACEN=gcs y GCS_BUCKET (corren en la VM de GCP).")
class ArchivosEnLaNube(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        almacen.usar(None)
        cls.preparadas = preparar("repartidor1@codex.mx", 1)
        cls.entrega = str(cls.preparadas[0]["entrega_id"])

    def setUp(self):
        self.api = Cliente(self, "json")
        self.api.entrar("repartidor1@codex.mx")
        self.creados = []

    def tearDown(self):
        for did in self.creados:                                    # no dejar objetos de prueba en el bucket
            d = datos.mongo().documentos.find_one({"_id": ObjectId(did)})
            if d and d.get("ruta"):
                almacen.obtener().borrar(d["ruta"])
            datos.mongo().documentos.delete_one({"_id": ObjectId(did)})
        almacen.usar(None)

    def subir(self):
        _, doc = self.api.llamar("documentos", "POST", "documentos", {
            "nombre": "evidencia de prueba.jpg", "tipo_mime": "image/jpeg", "contenido_base64": base64.b64encode(JPEG).decode(),
            "referencia": {"tipo": "entrega", "id": self.entrega}}, estado=201)
        self.creados.append(doc["id"])
        return doc

    def test_el_archivo_va_al_bucket_y_la_base_solo_guarda_sus_datos(self):
        doc = self.subir()
        mismas_llaves(self, doc, ejemplo("Documento.ok"))
        self.assertEqual((doc["privacidad"], doc["estado"], doc["metadatos"]["almacen"]), ("privado", "activo", "gcs"))
        self.assertTrue(doc["ruta"].startswith("documentos/") and doc["ruta"].endswith(".jpg"))
        self.assertNotIn("evidencia", doc["ruta"])                               # la ruta no usa el nombre que escribió la persona
        crudo = datos.mongo().documentos.find_one({"_id": ObjectId(doc["id"])})
        self.assertNotIn("contenido", crudo, "MongoDB no debe guardar el archivo")
        self.assertEqual(crudo["sha256"], hashlib.sha256(JPEG).hexdigest())
        self.assertTrue(almacen.obtener().existe(doc["ruta"]), "el objeto existe en el bucket")

    def test_url_firmada_descarga_sin_credenciales(self):
        doc = self.subir()
        _, enlace = self.api.llamar("documentos", "GET", f"documentos/{doc['id']}/enlace", estado=200)
        mismas_llaves(self, enlace, ejemplo("DocumentoEnlace.ok"))
        self.assertTrue(enlace["url_firmada"].startswith("https://storage.googleapis.com/"))
        self.assertIn("X-Goog-Signature", enlace["url_firmada"])
        self.assertIn("X-Goog-Expires=300", enlace["url_firmada"])
        estado, cuerpo, tipo = bajar(enlace["url_firmada"])
        self.assertEqual((estado, cuerpo, tipo), (200, JPEG, "image/jpeg"))

    def test_url_alterada_o_sin_firma_no_sirve(self):
        doc = self.subir()
        _, enlace = self.api.llamar("documentos", "GET", f"documentos/{doc['id']}/enlace", estado=200)
        url = enlace["url_firmada"]
        firma = url.split("X-Goog-Signature=")[1].split("&")[0]
        alterada = url.replace(firma, firma[:-4] + ("0000" if not firma.endswith("0000") else "1111"))
        self.assertIn(bajar(alterada, True)[0], (400, 403))
        self.assertIn(bajar(url.split("?")[0], True)[0], (400, 401, 403))      # el objeto sin firma tampoco (el bucket es privado)

    def test_la_url_firmada_caduca(self):
        doc = self.subir()
        with mock.patch.object(config, "URL_FIRMADA_SEGUNDOS", 2):
            _, enlace = self.api.llamar("documentos", "GET", f"documentos/{doc['id']}/enlace", estado=200)
        self.assertEqual(enlace["segundos"], 2)
        self.assertEqual(bajar(enlace["url_firmada"])[0], 200)
        time.sleep(4)
        self.assertIn(bajar(enlace["url_firmada"], True)[0], (400, 403), "ya caducó")

    def test_contenido_en_base64_se_verifica_contra_el_sha256(self):
        doc = self.subir()
        _, c = self.api.llamar("documentos", "GET", f"documentos/{doc['id']}/contenido", estado=200)
        self.assertEqual(base64.b64decode(c["contenido_base64"]), JPEG)

    def test_borrar_quita_el_objeto_y_deja_el_registro_eliminado(self):
        doc = self.subir()
        ruta = doc["ruta"]
        r, _ = self.api.llamar("documentos", "DELETE", f"documentos/{doc['id']}")
        self.assertEqual(r.status_code, 204)
        self.assertFalse(almacen.obtener().existe(ruta), "el objeto ya no está en el bucket")
        self.assertEqual(datos.mongo().documentos.find_one({"_id": ObjectId(doc["id"])})["estado"], "eliminado")
        self.assertEqual(self.api.llamar("documentos", "GET", f"documentos/{doc['id']}")[0].status_code, 404)
        self.assertEqual(self.api.llamar("documentos", "GET", f"documentos/{doc['id']}/enlace")[0].status_code, 404)

    def test_otra_persona_no_obtiene_el_enlace_de_un_documento_privado(self):
        doc = self.subir()
        otro = Cliente(self, "json")
        otro.entrar("operador.mh01@codex.mx")
        self.assertEqual(otro.llamar("documentos", "GET", f"documentos/{doc['id']}/enlace")[0].status_code, 404)
        self.assertEqual(otro.llamar("documentos", "GET", f"documentos/{doc['id']}")[0].status_code, 404)

    def test_salud_de_documentos_reporta_el_bucket(self):
        r = APPS["documentos"].test_client().get("/api/v1/salud")
        cuerpo = r.get_json()
        self.assertEqual((r.status_code, cuerpo["estado"], cuerpo["dependencias"]["bucket"]), (200, "ok", "ok"))
        self.assertGreater(cuerpo["tiempo_ms"], 0)

    def test_si_el_bucket_no_responde_hay_503_sin_registros_a_medias(self):
        antes = datos.mongo().documentos.count_documents({})
        almacen.usar(almacen.AlmacenGcs("microhubs-bucket-que-no-existe-0000000000"))
        r, err = self.api.llamar("documentos", "POST", "documentos", {
            "nombre": "x.jpg", "tipo_mime": "image/jpeg", "contenido_base64": base64.b64encode(JPEG).decode(),
            "referencia": {"tipo": "entrega", "id": self.entrega}})
        self.assertEqual(r.status_code, 503)
        self.assertEqual(err["error"]["codigo"], "SERVICIO_NO_DISPONIBLE")
        self.assertEqual(datos.mongo().documentos.count_documents({}), antes, "no queda un registro sin archivo")
        s = APPS["documentos"].test_client().get("/api/v1/salud")
        self.assertEqual((s.status_code, s.get_json()["estado"], s.get_json()["dependencias"]["bucket"]), (503, "degradado", "error"))
        almacen.usar(None)                                                            # se restablece el bucket real
        s = APPS["documentos"].test_client().get("/api/v1/salud")
        self.assertEqual((s.status_code, s.get_json()["estado"]), (200, "ok"))       # y el servicio se recupera solo


if __name__ == "__main__":
    unittest.main()
