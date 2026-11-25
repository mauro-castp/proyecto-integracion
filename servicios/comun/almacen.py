"""
almacen.py — Almacén de archivos de los microservicios.

La base de datos NO guarda archivos: guarda solo sus datos (id, ruta, tipo, tamaño, propietario, fecha, hash, privacidad,
estado y metadatos). El contenido vive en un almacén de objetos:

  ALMACEN=gcs    Google Cloud Storage (en la nube). Bucket privado: GCS_BUCKET. Credenciales: la cuenta de servicio de
                 la VM (sin llaves descargadas). Las URLs firmadas V4 se firman con IAM (signBlob).
  ALMACEN=local  Carpeta del contenedor (ALMACEN_DIR). Para desarrollo y pruebas. La URL "firmada" la firma el propio
                 servicio con HMAC (SECRET_KEY) y caduca igual que la de GCS.

Los dos tienen la misma interfaz: guardar, leer, borrar, disponible y url_firmada. Así el servicio no sabe dónde está el archivo.
"""
import base64
import hashlib
import hmac
import os
import time
from datetime import timedelta
from pathlib import Path
from urllib.parse import quote

from . import config

EXTENSIONES = {"image/jpeg": "jpg", "image/png": "png", "application/pdf": "pdf"}


class ErrorAlmacen(Exception):
    """El almacén no respondió o rechazó la operación (el servicio lo traduce a 503)."""


def clave_objeto(doc_id, tipo_mime, cuando=None):
    """Ruta del objeto en el bucket: documentos/AAAA/MM/<id>.<ext>. Nunca usa el nombre que escribió la persona."""
    t = time.gmtime(cuando if cuando is not None else time.time())
    return f"documentos/{t.tm_year:04d}/{t.tm_mon:02d}/{doc_id}.{EXTENSIONES.get(tipo_mime, 'bin')}"


# --------------------------------------------------------------------
# Carpeta local (desarrollo y pruebas)
# --------------------------------------------------------------------
class AlmacenLocal:
    nombre = "local"

    def __init__(self, carpeta, secreto=None):
        self.carpeta = Path(carpeta)
        self.secreto = (secreto or config.SECRET_KEY).encode()

    def _ruta(self, clave):
        destino = (self.carpeta / clave).resolve()
        if self.carpeta.resolve() not in destino.parents:           # nada de ../ ni rutas absolutas
            raise ErrorAlmacen("Ruta de objeto no permitida.")
        return destino

    def guardar(self, clave, contenido, tipo_mime, sha256=None):
        try:
            destino = self._ruta(clave)
            destino.parent.mkdir(parents=True, exist_ok=True)
            with open(destino, "xb") as f:                            # "x": nunca sobrescribe un objeto existente
                f.write(contenido)
        except FileExistsError:
            raise ErrorAlmacen("El objeto ya existe.")
        except OSError as e:
            raise ErrorAlmacen(f"No se pudo escribir en el almacén local: {e}")

    def leer(self, clave):
        try:
            return self._ruta(clave).read_bytes()
        except FileNotFoundError:
            raise ErrorAlmacen("El objeto no existe en el almacén.")
        except OSError as e:
            raise ErrorAlmacen(f"No se pudo leer del almacén local: {e}")

    def borrar(self, clave):
        try:
            self._ruta(clave).unlink(missing_ok=True)
        except OSError as e:
            raise ErrorAlmacen(f"No se pudo borrar del almacén local: {e}")

    def existe(self, clave):
        try:
            return self._ruta(clave).is_file()
        except ErrorAlmacen:
            return False

    def disponible(self):
        try:
            self.carpeta.mkdir(parents=True, exist_ok=True)
            return os.access(self.carpeta, os.W_OK)
        except OSError:
            return False

    # --- URL firmada por el propio servicio (HMAC) ---
    def _firma(self, clave, expira, nombre, tipo_mime):
        mensaje = "\n".join([clave, str(int(expira)), nombre, tipo_mime]).encode()
        return base64.urlsafe_b64encode(hmac.new(self.secreto, mensaje, hashlib.sha256).digest()).decode().rstrip("=")

    def url_firmada(self, clave, segundos, nombre, tipo_mime):
        """Devuelve (ruta relativa con la firma, momento en que caduca). El servicio le antepone su dirección."""
        expira = int(time.time()) + int(segundos)
        firma = self._firma(clave, expira, nombre, tipo_mime)
        return (f"{config.PREFIJO}/documentos/descarga?k={quote(clave, safe='')}&e={expira}&n={quote(nombre, safe='')}"
                f"&t={quote(tipo_mime, safe='')}&s={firma}"), expira

    def firma_valida(self, clave, expira, nombre, tipo_mime, firma):
        try:
            if int(expira) < time.time():
                return False
        except (TypeError, ValueError):
            return False
        return hmac.compare_digest(self._firma(clave, expira, nombre, tipo_mime), firma or "")


# --------------------------------------------------------------------
# Google Cloud Storage
# --------------------------------------------------------------------
class AlmacenGcs:
    nombre = "gcs"

    def __init__(self, bucket, cliente=None):
        if not bucket:
            raise ErrorAlmacen("Falta GCS_BUCKET: el almacén gcs necesita el nombre del bucket.")
        if cliente is None:
            from google.cloud import storage                         # solo se importa cuando de verdad se usa GCS
            cliente = storage.Client()
        self.cliente = cliente
        self.bucket = cliente.bucket(bucket)
        self.nombre_bucket = bucket

    def guardar(self, clave, contenido, tipo_mime, sha256=None):
        try:
            blob = self.bucket.blob(clave)
            if sha256:
                blob.metadata = {"sha256": sha256}
            blob.upload_from_string(contenido, content_type=tipo_mime, if_generation_match=0)   # 0 = solo si no existe
        except Exception as e:
            raise ErrorAlmacen(f"No se pudo subir al bucket: {e}")

    def leer(self, clave):
        try:
            return self.bucket.blob(clave).download_as_bytes()
        except Exception as e:
            raise ErrorAlmacen(f"No se pudo leer del bucket: {e}")

    def borrar(self, clave):
        try:
            self.bucket.blob(clave).delete()
        except Exception as e:
            if "404" in str(e) or "Not Found" in str(e):
                return
            raise ErrorAlmacen(f"No se pudo borrar del bucket: {e}")

    def existe(self, clave):
        try:
            return bool(self.bucket.blob(clave).exists())
        except Exception:
            return False

    def disponible(self):
        """Lista a lo más un objeto: solo exige permiso de lectura de objetos, no de administrar el bucket."""
        try:
            list(self.cliente.list_blobs(self.nombre_bucket, max_results=1))
            return True
        except Exception:
            return False

    def url_firmada(self, clave, segundos, nombre, tipo_mime):
        """URL V4 firmada con la identidad de la VM (IAM signBlob): no hay llave privada en ningún archivo."""
        try:
            import google.auth.transport.requests as peticiones
            credenciales = self.cliente._credentials
            if not getattr(credenciales, "token", None) or getattr(credenciales, "expired", False):
                credenciales.refresh(peticiones.Request())
            url = self.bucket.blob(clave).generate_signed_url(
                version="v4", expiration=timedelta(seconds=int(segundos)), method="GET",
                service_account_email=getattr(credenciales, "service_account_email", None),
                access_token=credenciales.token,
                response_disposition=f"attachment; filename*=UTF-8''{quote(nombre)}", response_type=tipo_mime)
        except Exception as e:
            raise ErrorAlmacen(f"No se pudo firmar la URL: {e}")
        return url, int(time.time()) + int(segundos)


# --------------------------------------------------------------------
# Selección del almacén
# --------------------------------------------------------------------
_actual = None


def obtener():
    """El almacén configurado por entorno (se crea una vez por proceso)."""
    global _actual
    if _actual is None:
        if config.ALMACEN == "gcs":
            _actual = AlmacenGcs(config.GCS_BUCKET)
        elif config.ALMACEN == "local":
            _actual = AlmacenLocal(config.ALMACEN_DIR)
        else:
            raise ErrorAlmacen(f"ALMACEN debe ser 'gcs' o 'local' (llegó {config.ALMACEN!r}).")
    return _actual


def usar(almacen):
    """Sustituye el almacén (pruebas). Con None se vuelve a elegir por entorno."""
    global _actual
    _actual = almacen
