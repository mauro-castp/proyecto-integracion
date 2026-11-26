#!/usr/bin/env bash
# Corre pruebas, evidencias o cualquier módulo de servicios/pruebas dentro de la red de Docker del sistema integrado, con el código del
# repositorio montado (no hay que reconstruir las imágenes). Necesita Docker y el sistema arriba:
#
#   docker compose -f docker-compose.integrado.yml up -d --build
#
# Uso (desde la raíz del repositorio):
#   servicios/pruebas/correr.sh test pruebas.test_ola2              un módulo de unittest (agregar -v para ver cada prueba)
#   servicios/pruebas/correr.sh evidencias ola3                      corrida completa de evidencias (Olas 1 a 3) en evidencias/ola3
#   servicios/pruebas/correr.sh evidencias ola2/complementarias --complementarias
#   servicios/pruebas/correr.sh flujos ola4/flujos                   tres procesos de principio a fin
#   servicios/pruebas/correr.sh escenarios ola2                      qué cambia cuando cambia un supuesto (evidencias/ola2/escenarios.md)
#   servicios/pruebas/correr.sh modulo pruebas.generar_supuestos     cualquier módulo de Python (python -m ...)
#
# En la nube (archivos en Google Cloud Storage):
#   set -a; . ./.env; set +a; RED_EXTRA=microhubs-integrado_publica \
#     servicios/pruebas/correr.sh test pruebas.test_nube -v
#
# Cambia datos de la base de demostración y los deja como estaban en lo que se puede deshacer; usar una base de pruebas.
set -euo pipefail
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && (pwd -W 2>/dev/null || pwd))"
RED="${RED_DOCKER:-microhubs-integrado_datos}"
IMAGEN="${IMAGEN_PRUEBAS:-microhubs-integrado-auth}"
export MSYS_NO_PATHCONV=1

limpiar_limites() {      # 30 inicios de sesión por minuto y por IP: se borran los contadores para encadenar corridas
  docker exec microhubs-integrado-redis-1 sh -c 'redis-cli -n 1 --scan --pattern "rate:*" | xargs -r redis-cli -n 1 del' >/dev/null 2>&1 || true
}

correr() {               # correr <carpeta de salida o ""> comando...
  local salida="$1"; shift
  local montaje=()
  if [ -n "$salida" ]; then mkdir -p "$RAIZ/evidencias/$salida"; montaje=(-v "$RAIZ/evidencias/$salida:/salida"); fi
  local args=(--rm --network "$RED" \
    -e SECRET_KEY="${SECRET_KEY:-cambiar-en-produccion}" \
    -e "PG_DSN=host=postgres port=5432 dbname=microhubs_p1 user=microhubs password=${POSTGRES_PASSWORD:-microhubs_dev}" \
    -e REDIS_URL=redis://redis:6379 -e MONGO_URL=mongodb://mongo:27017/microhubs_eventos \
    -e "ALMACEN=${ALMACEN:-local}" -e "GCS_BUCKET=${GCS_BUCKET:-}" -e "MICROHUBS_CLAVE=${MICROHUBS_CLAVE:-Codex#2026}" \
    -e LOG_STDOUT=0 -e PYTHONPATH=/work -e PYTHONIOENCODING=utf-8 \
    -v "$RAIZ/servicios:/work" -v "$RAIZ/sistema_web:/app/web" -v "$RAIZ/sistema_web:/sistema_web" \
    -v "$RAIZ/app_escritorio/contratos:/app/contratos" -v "$RAIZ/app_movil/app/src/test/resources/contratos:/app/ejemplos_json" \
    "${montaje[@]}" -w /work "$IMAGEN" "$@")
  if [ -n "${RED_EXTRA:-}" ]; then
    # La red de datos es interna (sin salida a Internet). Para hablar con Google Cloud Storage el contenedor de pruebas tambien
    # se conecta a la red con salida:  RED_EXTRA=microhubs-integrado_publica
    local cid; cid="$(docker create "${args[@]}")"
    docker network connect "$RED_EXTRA" "$cid"
    docker start -a "$cid" 2>&1
  else
    docker run "${args[@]}" 2>&1
  fi
}

orden="${1:-}"; [ -n "$orden" ] || { sed -n '2,16p' "${BASH_SOURCE[0]}"; exit 2; }
shift
limpiar_limites
case "$orden" in
  test)        correr "" python -m unittest "$@" ;;
  evidencias)  carpeta="${1:?falta la carpeta de salida}"; shift; correr "$carpeta" python pruebas/evidencias.py --salida /salida "$@" ;;
  flujos)      carpeta="${1:?falta la carpeta de salida}"; correr "$carpeta" python pruebas/flujos_integrales.py --salida /salida ;;
  escenarios)  carpeta="${1:?falta la carpeta de salida}"; correr "$carpeta" python pruebas/escenarios_ola2.py --salida /salida ;;
  modulo)      correr "" python -m "$@" ;;
  *)           echo "Orden desconocida: $orden" >&2; exit 2 ;;
esac
