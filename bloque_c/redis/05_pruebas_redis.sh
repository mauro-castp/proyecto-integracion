#!/bin/bash
# =====================================================================
# 05_pruebas_redis.sh — Verifica el diseño de claves y los scripts Lua
# Codex Innovations · Equipo 04
#
# Uso:  ./05_pruebas_redis.sh [host] [puerto]
# =====================================================================
set -u
H="${1:-127.0.0.1}"; P="${2:-6379}"
R="redis-cli -h $H -p $P"
OK=0; FALLA=0

chk () {  # chk "descripcion" "esperado" "obtenido"
  if [ "$2" = "$3" ]; then
    printf "  PASA  %-62s\n" "$1"; OK=$((OK+1))
  else
    printf "  FALLA %-62s esperado=[%s] obtenido=[%s]\n" "$1" "$2" "$3"; FALLA=$((FALLA+1))
  fi
}

echo "== Preparando =="
$R -n 0 FLUSHDB > /dev/null
$R -n 1 FLUSHDB > /dev/null
SHA_LIB=$($R -n 0 SCRIPT LOAD "$(cat 02_liberar_lock.lua)")
SHA_EXT=$($R -n 0 SCRIPT LOAD "$(cat 03_extender_lock.lua)")
SHA_REV=$($R -n 0 SCRIPT LOAD "$(cat 04_revocar_sesion.lua)")
echo "  scripts cargados"
echo

echo "== 1. Bloqueo de inventario (RN17) =="

# Adquisición exclusiva: el segundo intento debe fallar.
A=$($R -n 0 SET lock:inv:1:42 token-A NX PX 5000)
B=$($R -n 0 SET lock:inv:1:42 token-B NX PX 5000)
chk "Solo un proceso adquiere el bloqueo" "OK" "$A"
chk "El competidor NO adquiere el bloqueo" "" "$B"

# TTL presente: un proceso muerto no deja el producto bloqueado para siempre.
T=$($R -n 0 PTTL lock:inv:1:42)
chk "El bloqueo tiene expiración automática" "true" "$([ "$T" -gt 0 ] && echo true || echo false)"

# Liberación con token ajeno: debe ser rechazada.
L1=$($R -n 0 EVALSHA "$SHA_LIB" 1 lock:inv:1:42 token-B)
chk "Un token ajeno NO puede liberar el bloqueo" "0" "$L1"
chk "El bloqueo sigue vivo tras el intento ajeno" "1" "$($R -n 0 EXISTS lock:inv:1:42)"

# Extensión con token propio y con token ajeno.
E1=$($R -n 0 EVALSHA "$SHA_EXT" 1 lock:inv:1:42 token-A 9000)
E2=$($R -n 0 EVALSHA "$SHA_EXT" 1 lock:inv:1:42 token-B 9000)
chk "El propietario puede extender su bloqueo" "1" "$E1"
chk "Un tercero NO puede extender el bloqueo" "0" "$E2"

# Liberación legítima.
L2=$($R -n 0 EVALSHA "$SHA_LIB" 1 lock:inv:1:42 token-A)
chk "El propietario libera su bloqueo" "1" "$L2"
chk "La clave desaparece tras liberar" "0" "$($R -n 0 EXISTS lock:inv:1:42)"

# El escenario que motiva el script Lua: bloqueo expirado y reasignado.
$R -n 0 SET lock:inv:1:99 token-viejo PX 300 > /dev/null
sleep 0.6
$R -n 0 SET lock:inv:1:99 token-nuevo NX PX 5000 > /dev/null
L3=$($R -n 0 EVALSHA "$SHA_LIB" 1 lock:inv:1:99 token-viejo)
chk "Un proceso rezagado no borra el bloqueo de otro" "0" "$L3"
chk "El bloqueo nuevo sobrevive al rezagado" "token-nuevo" "$($R -n 0 GET lock:inv:1:99)"
echo

echo "== 2. Revocación de sesión (RF04, HU12) =="
$R -n 0 SADD auth:sesion:7 jti-web jti-movil > /dev/null
$R -n 0 EVALSHA "$SHA_REV" 2 auth:jti:revocado:jti-web auth:sesion:7 jti-web 900 > /dev/null
chk "El jti revocado queda marcado" "1" "$($R -n 0 EXISTS auth:jti:revocado:jti-web)"
chk "La revocación tiene TTL acotado" "true" \
    "$([ "$($R -n 0 TTL auth:jti:revocado:jti-web)" -gt 0 ] && echo true || echo false)"
chk "Cerrar la sesión web NO cierra la de la app" "1" "$($R -n 0 SCARD auth:sesion:7)"
chk "La sesión sobreviviente es la del móvil" "jti-movil" "$($R -n 0 SMEMBERS auth:sesion:7)"
echo

echo "== 3. Bloqueo por intentos fallidos (RF06) =="
LIMITE=5
for i in $(seq 1 $LIMITE); do $R -n 0 INCR auth:intentos:hash-correo > /dev/null; done
$R -n 0 EXPIRE auth:intentos:hash-correo 900 > /dev/null
chk "El contador llega al límite configurado" "$LIMITE" "$($R -n 0 GET auth:intentos:hash-correo)"
$R -n 0 SET auth:bloqueo:7 1 EX 900 > /dev/null
chk "El bloqueo temporal expira solo" "true" \
    "$([ "$($R -n 0 TTL auth:bloqueo:7)" -gt 0 ] && echo true || echo false)"
echo

echo "== 4. Caché e invalidación por versión (RNF07) =="
$R -n 1 SET cache:catalogo:version 1 > /dev/null
V=$($R -n 1 GET cache:catalogo:version)
$R -n 1 SET "cache:catalogo:v$V:bebidas:1" '{"items":[]}' EX 300 > /dev/null
chk "La entrada de caché nace con TTL" "true" \
    "$([ "$($R -n 1 TTL cache:catalogo:v$V:bebidas:1)" -gt 0 ] && echo true || echo false)"
V2=$($R -n 1 INCR cache:catalogo:version)
chk "Un cambio de catálogo invalida sin recorrer claves" "2" "$V2"
chk "La entrada vieja queda huérfana, no se borra en caliente" "1" \
    "$($R -n 1 EXISTS cache:catalogo:v1:bebidas:1)"
echo

echo "== 5. Separación de bases lógicas =="
chk "Los bloqueos viven en db 0" "1" "$($R -n 0 EXISTS lock:inv:1:99)"
chk "Los bloqueos NO están en db 1" "0" "$($R -n 1 EXISTS lock:inv:1:99)"
chk "La caché NO está en db 0" "0" "$($R -n 0 EXISTS cache:catalogo:version)"
echo

echo "== 6. Convención de nombres =="
MAL=$($R -n 0 KEYS '*' | grep -cE '[[:upper:][:space:]]' || true)
chk "Ninguna clave usa mayúsculas ni espacios" "0" "$MAL"
SIN_PREFIJO=$($R -n 0 KEYS '*' | grep -vcE '^(auth|lock|rate|cache|movil):' || true)
chk "Todas las claves usan un prefijo de dominio" "0" "$SIN_PREFIJO"
echo

echo "======================================================"
echo "  PASA: $OK   FALLA: $FALLA"
echo "======================================================"
[ "$FALLA" -eq 0 ] || exit 1
