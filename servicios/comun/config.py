"""
config.py — Configuración compartida por los microservicios.

Los valores llegan por variables de entorno (docker-compose.integrado.yml).
SECRET_KEY y las claves de Redis son las mismas que usa el sistema web
(sistema_web/nucleo.py): la autenticación es común a todos los componentes.
"""
import os
from pathlib import Path

SECRET_KEY = os.environ.get("SECRET_KEY", "cambiar-en-produccion-RNF30")
JWT_ALG = "HS256"

PG_DSN = os.environ.get(
    "PG_DSN", "host=127.0.0.1 port=5432 dbname=microhubs_p1 user=postgres password=microhubs_dev")
REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379")
MONGO_URL = os.environ.get("MONGO_URL", "")
MONGO_DB = os.environ.get("MONGO_DB", "microhubs_eventos")

# XSD oficiales del contrato v1. En Docker se copian a /app/contratos; en
# desarrollo se leen de app_escritorio/contratos (una sola fuente).
_raiz = Path(__file__).resolve().parents[2]
CONTRATOS = Path(os.environ.get("CONTRATOS_DIR") or
                 (Path("/app/contratos") if Path("/app/contratos").is_dir() else _raiz / "app_escritorio" / "contratos"))

ZONA_HORARIA = os.environ.get("ZONA_HORARIA", "America/Monterrey")

# Límite de consumo por IP y minuto (Redis, base 1).
LIMITE_POR_MINUTO = int(os.environ.get("LIMITE_POR_MINUTO", "240"))
LIMITE_LOGIN_POR_MINUTO = int(os.environ.get("LIMITE_LOGIN_POR_MINUTO", "30"))

# Una evidencia de 5 MB en Base64 ocupa unos 6.7 MB.
MAX_CUERPO_BYTES = 8 * 1024 * 1024
MAX_ARCHIVO_BYTES = 5 * 1024 * 1024

# Almacén de archivos (ver comun/almacen.py). "gcs" en la nube; "local" (carpeta del contenedor) en desarrollo y pruebas.
ALMACEN = os.environ.get("ALMACEN", "local").strip().lower()
GCS_BUCKET = os.environ.get("GCS_BUCKET", "").strip()
ALMACEN_DIR = os.environ.get("ALMACEN_DIR", "/tmp/microhubs_almacen")
# Cuánto vive una URL firmada de descarga (segundos): corta a propósito; cada descarga pide una nueva.
URL_FIRMADA_SEGUNDOS = int(os.environ.get("URL_FIRMADA_SEGUNDOS", "300"))

VERSION = os.environ.get("VERSION_DESPLEGADA", "1.0.0")      # en la nube: etiqueta o commit desplegado
PREFIJO = "/api/v1"

# Puertos de los servicios que existen. Cada uno se llama por su nombre en la red de Docker.
PUERTOS = {"auth": 5101, "usuarios": 5102, "productos": 5103, "pedidos": 5104, "entregas": 5105,
           "planeacion": 5106, "documentos": 5107, "zonas": 5108, "microhubs": 5109, "seguimiento": 5110,
           "inventario": 5111, "precios": 5112, "proveedores": 5113, "abastecimiento": 5114,
           "demanda": 5115, "cobertura": 5116, "capacidad": 5117, "rutas": 5118, "costos": 5119,
           "punto-equilibrio": 5120, "simulacion": 5121, "surtido": 5122, "notificaciones": 5124,
           "reportes": 5123, "sincronizacion": 5125, "auditoria-monitoreo": 5126}
# Cómo un servicio llama a otro (el mismo patrón que usa el web) y cuánto espera la respuesta.
MICROSERVICIOS_URL = os.environ.get("MICROSERVICIOS_URL", "http://{servicio}:{puerto}")
MICROSERVICIOS_TIEMPO = float(os.environ.get("MICROSERVICIOS_TIEMPO", "4"))

# Ejemplos oficiales del contrato: XML (escritorio) y JSON (Android). Swagger los muestra tal cual.
EJEMPLOS_XML = CONTRATOS / "ejemplos"
EJEMPLOS_JSON = Path(os.environ.get("EJEMPLOS_JSON_DIR") or
                     (Path("/app/ejemplos_json") if Path("/app/ejemplos_json").is_dir()
                      else _raiz / "app_movil" / "app" / "src" / "test" / "resources" / "contratos"))

# Registro de cada petición en la salida estándar (los contenedores lo recogen).
LOG_STDOUT = os.environ.get("LOG_STDOUT", "1") == "1"
