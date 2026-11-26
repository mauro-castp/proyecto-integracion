-- 12_entrega_final.sql · Entrega final · Alta de pedidos por API
-- Codex Innovations · Equipo 04 · Idempotente.
BEGIN;
SET LOCAL search_path TO microhubs, public;

-- La app guarda un uuid antes de enviar el pedido: si la respuesta se pierde y lo reenvía, no se crea otro.
ALTER TABLE pedido ADD COLUMN IF NOT EXISTS operacion_uuid varchar(36);
CREATE UNIQUE INDEX IF NOT EXISTS uq_pedido_operacion ON pedido (operacion_uuid) WHERE operacion_uuid IS NOT NULL;
COMMENT ON COLUMN pedido.operacion_uuid IS 'Idempotencia de POST /api/v1/pedidos.';
COMMIT;
