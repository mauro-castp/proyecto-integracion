"""
generar.py — Genera los archivos de despliegue en GCP a partir de la lista REAL de servicios y puertos (servicios/comun/config.py):

  docker-compose.gcp.yml       ajustes para la nube sobre docker-compose.integrado.yml: los puertos 5000 y 5101-5124 se publican SOLO en
                               127.0.0.1 (nada queda abierto al exterior; entra Nginx por 80/443)
  nginx-microhubs.conf         Nginx como puerta unica: "/" es el portal web y "/servicios/<nombre>/" cada microservicio

  python deploy/gcp/generar.py        (desde la raiz del repositorio; se vuelve a correr cuando se agrega un servicio)
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "servicios"))
from comun import config  # noqa: E402

DESTINO = Path(__file__).resolve().parent
PUERTO_WEB = 5000

# ---------------------------------------------------------------- docker-compose.gcp.yml
base = (RAIZ / "docker-compose.integrado.yml").read_text(encoding="utf-8")
en_compose = {}                                   # servicio -> puerto publicado en el compose base
actual = None
for linea in base.splitlines():
    m = re.match(r"^  ([a-z0-9_-]+):\s*$", linea)
    if m:
        actual = m.group(1)
    p = re.search(r'ports:\s*\["(?:\$\{[^}]+\}|\d+):(\d+)"\]', linea)
    if p and actual:
        en_compose[actual] = int(p.group(1))

faltan = [n for n in config.PUERTOS if n not in en_compose]
if faltan:
    sys.exit(f"Servicios con puerto en config.py pero sin 'ports' en docker-compose.integrado.yml: {faltan}")

lineas = ["# docker-compose.gcp.yml — GENERADO por deploy/gcp/generar.py: no editar a mano.",
          "#",
          "# Ajustes para la nube. Se usa JUNTO con el compose base (los valores de ALMACEN, GCS_BUCKET, SECRET_KEY, etc. salen de .env):",
          "#   docker compose --env-file .env -f docker-compose.integrado.yml -f deploy/gcp/docker-compose.gcp.yml up -d --build",
          "#",
          "# Los puertos del portal (5000) y de los servicios (5101-5124) se publican solo en 127.0.0.1: desde Internet solo se llega a",
          "# Nginx (80/443). PostgreSQL, Redis y MongoDB no publican puertos (red interna).",
          "# `!override` reemplaza la lista de puertos del compose base (sin el, se sumaria y seguirian abiertos).",
          "",
          "services:",
          "  web:",
          f'    ports: !override ["127.0.0.1:{PUERTO_WEB}:5000"]']
for nombre, puerto in sorted(config.PUERTOS.items(), key=lambda kv: kv[1]):
    servicio = nombre.replace("-", "-")
    lineas += [f"  {servicio}:", f'    ports: !override ["127.0.0.1:{puerto}:{en_compose[nombre]}"]']
(DESTINO / "docker-compose.gcp.yml").write_text("\n".join(lineas) + "\n", encoding="utf-8", newline="\n")

# ---------------------------------------------------------------- nginx-microhubs.conf
nginx = ["# nginx-microhubs.conf — GENERADO por deploy/gcp/generar.py: no editar a mano.",
         "#",
         "# Nginx es la UNICA puerta publica (80/443). El portal web va en \"/\" y cada microservicio en \"/servicios/<nombre>/\":",
         "#   https://<host>/servicios/auth/api/v1/auth/login       ->  127.0.0.1:5101/api/v1/auth/login",
         "#   https://<host>/servicios/documentos/api/v1/docs       ->  Swagger de documentos (el prefijo viaja en X-Forwarded-Prefix)",
         "# __SERVER_NAME__ se sustituye al instalar (deploy/gcp/instalar_vm.sh). Certbot agrega el bloque 443 y la redireccion.",
         "",
         "limit_req_zone $binary_remote_addr zone=microhubs_api:10m rate=20r/s;",
         "",
         "server {",
         "    listen 80;",
         "    listen [::]:80;",
         "    server_name __SERVER_NAME__;",
         "    server_tokens off;",
         "    client_max_body_size 9m;            # los servicios aceptan hasta 8 MB (una evidencia de 5 MB en Base64)",
         "    add_header X-Content-Type-Options nosniff always;",
         "    add_header X-Frame-Options SAMEORIGIN always;",
         "",
         "    proxy_http_version 1.1;",
         "    proxy_set_header Host $host;",
         "    proxy_set_header X-Real-IP $remote_addr;",
         "    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;",
         "    proxy_set_header X-Forwarded-Proto $scheme;",
         "    proxy_read_timeout 60s;",
         "",
         "    # Portal web",
         "    location / {",
         f"        proxy_pass http://127.0.0.1:{PUERTO_WEB};",
         "    }",
         ""]
for nombre, puerto in sorted(config.PUERTOS.items(), key=lambda kv: kv[1]):
    nginx += [f"    # {nombre}",
              f"    location /servicios/{nombre}/ {{",
              "        limit_req zone=microhubs_api burst=40 nodelay;",
              f"        proxy_set_header X-Forwarded-Prefix /servicios/{nombre};",
              f"        proxy_pass http://127.0.0.1:{puerto}/;",
              "    }"]
nginx += ["}", ""]
(DESTINO / "nginx-microhubs.conf").write_text("\n".join(nginx), encoding="utf-8", newline="\n")
print(f"docker-compose.gcp.yml: {len(config.PUERTOS) + 1} servicios | nginx-microhubs.conf: {len(config.PUERTOS)} rutas de microservicios + portal")
