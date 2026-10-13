"""
config.py — Configuración compartida por los ocho microservicios.

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

VERSION = "1.0.0"
PREFIJO = "/api/v1"

# Ejemplos oficiales del contrato: XML (escritorio) y JSON (Android). Swagger los muestra tal cual.
EJEMPLOS_XML = CONTRATOS / "ejemplos"
EJEMPLOS_JSON = Path(os.environ.get("EJEMPLOS_JSON_DIR") or
                     (Path("/app/ejemplos_json") if Path("/app/ejemplos_json").is_dir()
                      else _raiz / "app_movil" / "app" / "src" / "test" / "resources" / "contratos"))

# Registro de cada petición en la salida estándar (los contenedores lo recogen).
LOG_STDOUT = os.environ.get("LOG_STDOUT", "1") == "1"
