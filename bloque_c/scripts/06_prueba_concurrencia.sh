#!/bin/bash
# =====================================================================
# 06_prueba_concurrencia.sh — VR-08 con concurrencia real
# Codex Innovations · Equipo 04
#
# Dos sesiones intentan consumir la MISMA última unidad al mismo tiempo.
# Se espera que exactamente una descuente y la otra falle sin sobrevender.
#
# Una prueba dentro de una sola sesión no demuestra nada sobre RN17:
# el bloqueo solo se puede observar con dos transacciones vivas a la vez.
#
# Uso:  ./06_prueba_concurrencia.sh [nombre_bd]
# =====================================================================
set -u
BD="${1:-microhubs_concurrencia}"
PSQL="psql -h /tmp -d $BD -v ON_ERROR_STOP=1 -qtA"

echo "== Preparando escenario: una sola unidad disponible en un solo microhub =="

$PSQL <<'SQL'
SET search_path TO microhubs, public;
-- Deja exactamente 1 unidad del producto de prueba en MH-01 y 0 en el resto.
UPDATE inventario i SET existencia = 0
 WHERE i.producto_id = (SELECT p.id FROM producto p WHERE p.clave_interna = 'AB-003');
UPDATE inventario i SET existencia = 1
 WHERE i.producto_id = (SELECT p.id FROM producto p WHERE p.clave_interna = 'AB-003')
   AND i.microhub_id = (SELECT m.id FROM microhub m WHERE m.clave = 'MH-01');

DELETE FROM pedido_detalle WHERE pedido_id IN (SELECT id FROM pedido WHERE folio LIKE 'CONC-%');
DELETE FROM historial_estatus WHERE pedido_id IN (SELECT id FROM pedido WHERE folio LIKE 'CONC-%');
DELETE FROM decision_asignacion WHERE pedido_id IN (SELECT id FROM pedido WHERE folio LIKE 'CONC-%');
DELETE FROM pedido WHERE folio LIKE 'CONC-%';

-- Dos pedidos idénticos, cada uno pide la única unidad que existe.
-- El domicilio DEBE estar dentro del radio de MH-01: es el único microhub
-- con existencia, así que si no lo cubre, el escenario no prueba nada.
CREATE TEMP VIEW dom_cubierto AS
SELECT c.id AS cliente_id, d.id AS domicilio_id, d.zona_id
  FROM cliente c JOIN domicilio d ON d.cliente_id = c.id AND d.activo
 WHERE fn_cubre((SELECT m.id FROM microhub m WHERE m.clave = 'MH-01'),
                d.latitud, d.longitud)
 ORDER BY c.id LIMIT 1;

INSERT INTO pedido (folio, cliente_id, domicilio_id, zona_id, subtotal, costo_envio)
SELECT 'CONC-A', cliente_id, domicilio_id, zona_id, 100, 15 FROM dom_cubierto;
INSERT INTO pedido (folio, cliente_id, domicilio_id, zona_id, subtotal, costo_envio)
SELECT 'CONC-B', cliente_id, domicilio_id, zona_id, 100, 15 FROM dom_cubierto;

INSERT INTO pedido_detalle (pedido_id, producto_id, cantidad, precio_unitario)
SELECT p.id, pr.id, 1, pr.precio FROM pedido p, producto pr
 WHERE p.folio IN ('CONC-A','CONC-B') AND pr.clave_interna = 'AB-003';
SQL

EXISTENCIA_INICIAL=$($PSQL -c "SET search_path TO microhubs; SELECT i.existencia FROM inventario i JOIN producto p ON p.id=i.producto_id JOIN microhub m ON m.id=i.microhub_id WHERE p.clave_interna='AB-003' AND m.clave='MH-01';")
echo "   Existencia inicial en MH-01: $EXISTENCIA_INICIAL"
echo

echo "== Lanzando las dos sesiones =="

# Sesión A: toma el bloqueo y lo sostiene 4 segundos antes de confirmar.
(
  psql -h /tmp -d "$BD" -qtA <<'SQL' > /tmp/sesion_a.out 2>&1
SET search_path TO microhubs, public;
BEGIN;
SELECT 'A: ' || CASE WHEN asignado THEN 'asignó en microhub ' || microhub_id
                     ELSE 'no asignó' END
  FROM fn_asignar_pedido((SELECT id FROM pedido WHERE folio = 'CONC-A'));
SELECT pg_sleep(4);
COMMIT;
SELECT 'A: transacción confirmada';
SQL
) &
PID_A=$!

sleep 1

# Sesión B: entra cuando A todavía tiene el renglón bloqueado.
(
  psql -h /tmp -d "$BD" -qtA <<'SQL' > /tmp/sesion_b.out 2>&1
SET search_path TO microhubs, public;
BEGIN;
SELECT 'B: ' || CASE WHEN asignado THEN 'asignó en microhub ' || microhub_id
                     ELSE 'no asignó' END
  FROM fn_asignar_pedido((SELECT id FROM pedido WHERE folio = 'CONC-B'));
COMMIT;
SELECT 'B: transacción confirmada';
SQL
) &
PID_B=$!

wait $PID_A $PID_B

echo "--- Sesión A ---"; sed 's/^/   /' /tmp/sesion_a.out
echo "--- Sesión B ---"; sed 's/^/   /' /tmp/sesion_b.out
echo

echo "== Veredicto =="
$PSQL <<'SQL'
SET search_path TO microhubs, public;
\pset format aligned
\pset tuples_only off
SELECT
    (SELECT i.existencia FROM inventario i
      JOIN producto p ON p.id = i.producto_id
      JOIN microhub m ON m.id = i.microhub_id
     WHERE p.clave_interna = 'AB-003' AND m.clave = 'MH-01')       AS existencia_final,
    (SELECT count(*) FROM pedido WHERE folio LIKE 'CONC-%'
      AND estado = 'asignado')                                     AS pedidos_asignados,
    (SELECT count(*) FROM movimiento_inventario mi
      JOIN producto p ON p.id = mi.producto_id
     WHERE p.clave_interna = 'AB-003' AND mi.tipo = 'salida_pedido') AS salidas_registradas;
SQL

RES=$($PSQL <<'SQL'
SET search_path TO microhubs, public;
SELECT CASE
   WHEN (SELECT i.existencia FROM inventario i
          JOIN producto p ON p.id=i.producto_id JOIN microhub m ON m.id=i.microhub_id
         WHERE p.clave_interna='AB-003' AND m.clave='MH-01') = 0
    AND (SELECT count(*) FROM pedido WHERE folio LIKE 'CONC-%' AND estado='asignado') = 1
   THEN 'PASA' ELSE 'FALLA' END;
SQL
)

echo
if [ "$RES" = "PASA" ]; then
  echo "VR-08 PASA — RN16/RN17: exactamente un pedido descontó la última unidad."
  echo "            La existencia quedó en 0, nunca en -1."
  exit 0
else
  echo "VR-08 FALLA — se produjo sobreventa o ninguna sesión descontó."
  exit 1
fi
