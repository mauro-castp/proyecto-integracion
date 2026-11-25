#!/usr/bin/env bash
# instalar_vm.sh — Despliega la plataforma de Microhubs EN la VM de GCP (Ubuntu 24.04 con Docker, Compose y Nginx).
#
#   cd ~/microhubs && bash deploy/gcp/instalar_vm.sh [--sin-construir] [--https correo@ejemplo.com]
#
# Que hace (es repetible: correrlo otra vez actualiza):
#   1. Crea .env (permiso 600) con secretos ALEATORIOS si no existe y verifica que no queden los valores por defecto del repo
#      (cambiar-en-produccion, microhubs_dev). El .env vive solo en la VM: no se sube a Git.
#   2. Levanta los ~27 contenedores: compose base + deploy/gcp/docker-compose.gcp.yml (puertos solo en 127.0.0.1).
#   3. Instala la configuracion de Nginx (portal en "/", microservicios en "/servicios/<nombre>/") y recarga.
#   4. Con --https pide el certificado de Let's Encrypt (acepta sus terminos de servicio y registra el correo): solo si lo pides.
#
# Variables opcionales (ya con valor por omision): GCS_BUCKET, HOST_PUBLICO (IP.sslip.io), VERSION_DESPLEGADA.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
RAIZ="$PWD"
CONSTRUIR="--build"; HTTPS=""; CORREO=""
while [ $# -gt 0 ]; do
  case "$1" in
    --sin-construir) CONSTRUIR="";;
    --https) HTTPS=1; CORREO="${2:?--https necesita un correo}"; shift;;
    *) echo "Opcion desconocida: $1" >&2; exit 2;;
  esac; shift
done
decir() { printf '\n== %s\n' "$*"; }
morir() { echo "ERROR: $*" >&2; exit 1; }

IP="$(curl -fsS -H 'Metadata-Flavor: Google' http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip 2>/dev/null || true)"
HOST_PUBLICO="${HOST_PUBLICO:-$( [ -n "$IP" ] && echo "${IP//./-}.sslip.io" || echo _ )}"
PROYECTO="$(curl -fsS -H 'Metadata-Flavor: Google' http://metadata.google.internal/computeMetadata/v1/project/project-id 2>/dev/null || echo desconocido)"
GCS_BUCKET="${GCS_BUCKET:-microhubs-evidencias-637044}"
VERSION="${VERSION_DESPLEGADA:-$(git rev-parse --short HEAD 2>/dev/null || date +%Y%m%d-%H%M)}"

decir "1) .env con secretos aleatorios (permiso 600)"
if [ ! -f .env ]; then
  umask 077
  cat > .env <<EOF
# Generado por instalar_vm.sh en $(date -u +%FT%TZ). SOLO en esta VM: no se sube a Git.
SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -hex 16)
ALMACEN=gcs
GCS_BUCKET=$GCS_BUCKET
URL_FIRMADA_SEGUNDOS=300
VERSION_DESPLEGADA=$VERSION
EOF
  echo "   .env creado"
else
  sed -i "s/^VERSION_DESPLEGADA=.*/VERSION_DESPLEGADA=$VERSION/" .env
  echo "   .env ya existe: se conserva (solo se actualiza VERSION_DESPLEGADA)"
fi
chmod 600 .env
grep -q '^SECRET_KEY=.\{32,\}' .env || morir "SECRET_KEY ausente o corta en .env"
grep -qE '^(SECRET_KEY=cambiar|POSTGRES_PASSWORD=microhubs_dev)' .env && morir ".env trae los valores por defecto del repositorio."
grep -q '^POSTGRES_PASSWORD=.\{12,\}' .env || morir "POSTGRES_PASSWORD ausente o corta en .env"
grep -q '^ALMACEN=gcs' .env || morir "En la nube ALMACEN debe ser gcs"
echo "   .env verificado (permisos: $(stat -c %a .env), proyecto GCP: $PROYECTO, bucket: $GCS_BUCKET, version: $VERSION)"

decir "2) Contenedores"
docker compose --env-file .env -f docker-compose.integrado.yml -f deploy/gcp/docker-compose.gcp.yml up -d $CONSTRUIR --remove-orphans
echo "   esperando a que los servicios respondan..."
for i in $(seq 1 60); do
  malos=0
  for p in 5101 5102 5103 5104 5105 5106 5107 5108 5109 5110; do
    curl -fsS -m 3 -o /dev/null "http://127.0.0.1:$p/api/v1/salud" || malos=$((malos + 1))
  done
  [ "$malos" = 0 ] && break
  sleep 5
done
[ "$malos" = 0 ] && echo "   los 10 primeros servicios responden" || echo "   AVISO: $malos de 10 aun no responden (revisa: docker compose ps)"

decir "3) Nginx"
sudo install -m 644 deploy/gcp/nginx-microhubs.conf /etc/nginx/sites-available/microhubs
sudo sed -i "s/__SERVER_NAME__/$HOST_PUBLICO/" /etc/nginx/sites-available/microhubs
sudo ln -sf /etc/nginx/sites-available/microhubs /etc/nginx/sites-enabled/microhubs
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
echo "   Nginx sirve $HOST_PUBLICO"

if [ -n "$HTTPS" ]; then
  decir "4) HTTPS con Let's Encrypt (acepta los terminos de servicio y registra $CORREO)"
  sudo certbot --nginx -d "$HOST_PUBLICO" --non-interactive --agree-tos -m "$CORREO" --redirect
fi

decir "Listo"
echo "   Portal:   http${HTTPS:+s}://$HOST_PUBLICO/"
echo "   Servicios: http${HTTPS:+s}://$HOST_PUBLICO/servicios/<nombre>/api/v1/salud   (Swagger: .../api/v1/docs)"
