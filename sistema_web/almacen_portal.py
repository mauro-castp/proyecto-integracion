"""
almacen_portal.py — Dónde guarda el portal los archivos que suben las personas («Mis archivos»).

La base de datos NO guarda el archivo: guarda sus datos (ruta, tipo, tamaño, propietario, fecha, huella, privacidad y estado).
El contenido va a un almacén de objetos que el portal usa directamente, sin pasar por ningún microservicio:

  ALMACEN=gcs     Google Cloud Storage (en la nube): bucket privado GCS_BUCKET, con la cuenta de servicio de la VM.
  ALMACEN=local   Carpeta del contenedor (ALMACEN_DIR). Para desarrollo y pruebas.
"""
import os
import time
from pathlib import Path

EXTENSIONES = {"application/pdf": "pdf", "image/png": "png", "image/jpeg": "jpg"}


class ErrorAlmacen(Exception):
    """El almacén no respondió o rechazó la operación."""


def clave_objeto(identificador, tipo):
    """Ruta del objeto: web/AAAA/MM/<id>.<ext>. Nunca usa el nombre que escribió la persona."""
    t = time.gmtime()
    return f"web/{t.tm_year:04d}/{t.tm_mon:02d}/{identificador}.{EXTENSIONES.get(tipo, 'bin')}"


def nombre():
    return os.environ.get("ALMACEN", "local")


def _bucket():
    cubeta = os.environ.get("GCS_BUCKET", "")
    if not cubeta:
        raise ErrorAlmacen("Falta GCS_BUCKET.")
    from google.cloud import storage                              # solo se importa cuando de verdad se usa GCS
    return storage.Client().bucket(cubeta)


def _local(ruta):
    carpeta = Path(os.environ.get("ALMACEN_DIR", "almacen_web")).resolve()
    destino = (carpeta / ruta).resolve()
    if carpeta not in destino.parents:                            # nada de ../ ni rutas absolutas
        raise ErrorAlmacen("Ruta de objeto no permitida.")
    return destino


def guardar(ruta, contenido, tipo):
    try:
        if nombre() == "gcs":
            _bucket().blob(ruta).upload_from_string(contenido, content_type=tipo, if_generation_match=0)   # solo si no existe
        else:
            destino = _local(ruta)
            destino.parent.mkdir(parents=True, exist_ok=True)
            with open(destino, "xb") as f:                        # "x": nunca sobrescribe
                f.write(contenido)
    except ErrorAlmacen:
        raise
    except Exception as e:
        raise ErrorAlmacen(f"No se pudo guardar el archivo: {e}")


def leer(ruta):
    try:
        return _bucket().blob(ruta).download_as_bytes() if nombre() == "gcs" else _local(ruta).read_bytes()
    except ErrorAlmacen:
        raise
    except Exception as e:
        raise ErrorAlmacen(f"No se pudo leer el archivo: {e}")


def borrar(ruta):
    """Se usa para no dejar un objeto huérfano si la base rechaza sus datos. No falla si ya no está."""
    try:
        if nombre() == "gcs":
            _bucket().blob(ruta).delete()
        else:
            _local(ruta).unlink(missing_ok=True)
    except Exception:
        pass
