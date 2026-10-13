-- 08_microservicios.sql · Segundo parcial · microservicios (contrato v1)
-- Codex Innovations · Equipo 04
--
-- Idempotente: se puede aplicar sobre una base existente cuantas veces se
-- quiera (servicios/migrar.py lo hace al levantar docker-compose.integrado.yml).
-- No modifica datos existentes ni retira permisos.
--
-- 1. entrega: cierre idempotente desde la app móvil (id_cliente_local) y
--    datos del cierre (ubicación, hora de captura, evidencias en MongoDB).
-- 2. web_notificacion: tipo y referencia que pide el contrato v1. La misma
--    tabla sirve al portal web y al servicio de notificaciones.
-- 3. Aviso automático al repartidor cuando se le asigna una entrega, desde
--    el componente que sea (web, servicio o script), igual que el aviso de
--    cierre al cliente del SQL 07.
BEGIN;
SET LOCAL search_path TO microhubs, public;

-- 1. Entrega ------------------------------------------------------------
ALTER TABLE entrega ADD COLUMN IF NOT EXISTS id_cliente_local   varchar(64);
ALTER TABLE entrega ADD COLUMN IF NOT EXISTS evidencia_ids      text[];
ALTER TABLE entrega ADD COLUMN IF NOT EXISTS cierre_latitud     numeric(9,6);
ALTER TABLE entrega ADD COLUMN IF NOT EXISTS cierre_longitud    numeric(9,6);
ALTER TABLE entrega ADD COLUMN IF NOT EXISTS cierre_precision_m numeric(8,2);
ALTER TABLE entrega ADD COLUMN IF NOT EXISTS capturado_en       timestamptz;
CREATE UNIQUE INDEX IF NOT EXISTS uq_entrega_id_cliente_local
    ON entrega (id_cliente_local) WHERE id_cliente_local IS NOT NULL;
COMMENT ON COLUMN entrega.id_cliente_local IS
    'UUID que genera la app móvil por operación de cierre: un reintento con el mismo valor no se aplica dos veces.';
COMMENT ON COLUMN entrega.evidencia_ids IS
    'Identificadores (ObjectId) de las evidencias guardadas en MongoDB, colección documentos.';

-- 2. Notificaciones -------------------------------------------------------
ALTER TABLE web_notificacion ADD COLUMN IF NOT EXISTS tipo varchar(12) NOT NULL DEFAULT 'sistema';
ALTER TABLE web_notificacion ADD COLUMN IF NOT EXISTS referencia_tipo varchar(12);
ALTER TABLE web_notificacion ADD COLUMN IF NOT EXISTS referencia_id varchar(40);
DO $$ BEGIN
  ALTER TABLE web_notificacion ADD CONSTRAINT ck_notif_tipo
    CHECK (tipo IN ('pedido', 'entrega', 'sistema', 'planeacion'));
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
  ALTER TABLE web_notificacion ADD CONSTRAINT ck_notif_referencia
    CHECK ((referencia_tipo IS NULL AND referencia_id IS NULL) OR
           (referencia_tipo IN ('pedido', 'entrega', 'candidato', 'sistema') AND referencia_id IS NOT NULL));
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
CREATE INDEX IF NOT EXISTS ix_web_notificacion_no_leidas
    ON web_notificacion (destinatario_id) WHERE leido_en IS NULL;

-- El aviso de cierre del SQL 07 ahora indica tipo y referencia.
CREATE OR REPLACE FUNCTION fn_web_notificar_cierre() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.estado IS DISTINCT FROM OLD.estado AND NEW.estado IN ('entregado','entrega_parcial','entrega_fallida','cancelado') THEN
    INSERT INTO web_notificacion(destinatario_id, emisor_id, titulo, mensaje, tipo, referencia_tipo, referencia_id)
    SELECT c.usuario_id, ctx_usuario_id(), 'Pedido ' || NEW.folio,
           'El pedido cambió a ' || NEW.estado::text || '.', 'pedido', 'pedido', NEW.id::text
      FROM cliente c WHERE c.id = NEW.cliente_id;
  END IF;
  RETURN NEW;
END $$;

-- 3. Aviso de asignación al repartidor ------------------------------------
CREATE OR REPLACE FUNCTION fn_notificar_asignacion() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE v_folio varchar;
BEGIN
  IF NEW.repartidor_id IS NOT NULL AND NEW.cierre_en IS NULL
     AND (TG_OP = 'INSERT' OR NEW.repartidor_id IS DISTINCT FROM OLD.repartidor_id) THEN
    SELECT folio INTO v_folio FROM pedido WHERE id = NEW.pedido_id;
    INSERT INTO web_notificacion(destinatario_id, emisor_id, titulo, mensaje, tipo, referencia_tipo, referencia_id)
    VALUES (NEW.repartidor_id, ctx_usuario_id(), 'Nueva entrega asignada',
            'Se te asignó el pedido ' || v_folio ||
            COALESCE(' (parada ' || NEW.orden_parada || ')', '') || '.',
            'entrega', 'entrega', NEW.id::text);
  END IF;
  RETURN NEW;
END $$;
CREATE OR REPLACE TRIGGER trg_notificar_asignacion
  AFTER INSERT OR UPDATE OF repartidor_id ON entrega
  FOR EACH ROW EXECUTE FUNCTION fn_notificar_asignacion();

-- 4. Registro de la migración ----------------------------------------------
CREATE TABLE IF NOT EXISTS web_migracion(clave varchar(40) PRIMARY KEY, aplicado_en timestamptz NOT NULL DEFAULT now());
INSERT INTO web_migracion(clave) VALUES ('microservicios_v1') ON CONFLICT DO NOTHING;
COMMIT;
