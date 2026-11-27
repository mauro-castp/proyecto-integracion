#!/usr/bin/env bash
# correr_locust.sh — Corre la prueba de carga con el sistema arriba y deja el informe.
#
#   bash rendimiento/correr_locust.sh evidencias/ola4/carga                      en local
#   NUBE=1 bash rendimiento/correr_locust.sh evidencias/nube/carga               en la VM (usa .env y el compose de la nube)
#
# Todas las peticiones salen de una sola IP, así que mientras dura la prueba se sube el límite de consumo por IP (240 por minuto y por
# servicio) y se RESTAURA al terminar, aunque la prueba falle. El generador corre en la misma máquina que la plataforma y compite por CPU.
set -euo pipefail
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && (pwd -W 2>/dev/null || pwd))"
cd "$RAIZ"
SALIDA="${1:?falta la carpeta de salida}"
export MSYS_NO_PATHCONV=1
COMPOSE=(docker compose -f docker-compose.integrado.yml)
if [ "${NUBE:-}" = "1" ]; then COMPOSE=(docker compose --env-file .env -f docker-compose.integrado.yml -f deploy/gcp/docker-compose.gcp.yml); fi
CLAVE="${MICROHUBS_CLAVE:-Codex#2026}"
mkdir -p "$SALIDA" && chmod 777 "$SALIDA" 2>/dev/null || true

esperar() {
  for _ in $(seq 1 60); do
    [ "$("${COMPOSE[@]}" ps --format '{{.Health}}' | grep -cE '^(starting|unhealthy)$')" = "0" ] && return 0
    sleep 3
  done
  echo "AVISO: hay contenedores que no están sanos" >&2
}

MUESTRAS=""
restaurar() {
  [ -n "$MUESTRAS" ] && kill "$MUESTRAS" 2>/dev/null || true
  "${COMPOSE[@]}" up -d >/dev/null 2>&1 && echo "== límites de consumo restaurados"
}
trap restaurar EXIT

echo "== subiendo el límite de consumo para la prueba"
LIMITE_POR_MINUTO=1000000 LIMITE_LOGIN_POR_MINUTO=1000000 "${COMPOSE[@]}" up -d >/dev/null 2>&1
esperar
: > "$SALIDA/recursos.csv"
( while true; do docker stats --no-stream --format '{{.Name}};{{.CPUPerc}};{{.MemUsage}}' | grep '^microhubs-' >> "$SALIDA/recursos.csv" || true; sleep 8; done ) &
MUESTRAS=$!

echo "== Locust"
docker run --rm --name microhubs-locust --network microhubs-integrado_publica -v "$RAIZ/rendimiento:/mnt/rend:ro" -v "$RAIZ/$SALIDA:/salida" \
  -e MICROHUBS_CLAVE="$CLAVE" -e ESCALONES="${ESCALONES:-10,25,50,100,150,10}" -e ESCALON_SEGUNDOS="${ESCALON_SEGUNDOS:-60}" \
  locustio/locust:2.32.4 -f /mnt/rend/locustfile.py --headless --csv /salida/carga --html /salida/carga.html --only-summary 2>&1 | tail -5 || true

kill "$MUESTRAS" 2>/dev/null || true; MUESTRAS=""
PY="$(command -v python3 || command -v python)"
"$PY" rendimiento/resumen.py "$SALIDA" "${ENTORNO:-equipo local con Docker}"
