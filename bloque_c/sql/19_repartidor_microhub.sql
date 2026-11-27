-- 19_repartidor_microhub.sql — Cada repartidor pertenece a UN microhub y solo recibe entregas de pedidos de ese microhub.
-- Antes el repartidor recibía el pedido que le tocara, de cualquier microhub. Idempotente.

-- 1. Repartidores de la demostración con su microhub fijo (uno por microhub activo).
UPDATE usuario u SET microhub_id = m.id
  FROM microhub m
 WHERE u.correo = 'repartidor1@codex.mx' AND m.clave = 'MH-01' AND u.microhub_id IS NULL;
UPDATE usuario u SET microhub_id = m.id
  FROM microhub m
 WHERE u.correo = 'repartidor2@codex.mx' AND m.clave = 'MH-02' AND u.microhub_id IS NULL;
INSERT INTO usuario (nombre, apellidos, correo, telefono, hash_contrasena, rol_id, microhub_id)
SELECT 'Óscar', 'Treviño Garza', 'repartidor3@codex.mx', '8117302281', u.hash_contrasena, u.rol_id, m.id
  FROM usuario u, microhub m
 WHERE u.correo = 'repartidor1@codex.mx' AND m.clave = 'MH-03'
ON CONFLICT DO NOTHING;

-- Cualquier otro repartidor sin microhub (datos de volumen o dados de alta antes) queda en el microhub activo con menos repartidores.
DO $$
DECLARE r record; destino integer;
BEGIN
  FOR r IN SELECT u.id FROM usuario u JOIN rol ro ON ro.id = u.rol_id
            WHERE ro.clave = 'repartidor' AND u.microhub_id IS NULL ORDER BY u.id LOOP
    SELECT m.id INTO destino FROM microhub m
      LEFT JOIN usuario x ON x.microhub_id = m.id AND x.rol_id = (SELECT id FROM rol WHERE clave = 'repartidor')
     WHERE m.estatus = 'activo' GROUP BY m.id ORDER BY count(x.id), m.id LIMIT 1;
    UPDATE usuario SET microhub_id = destino WHERE id = r.id;
  END LOOP;
END $$;

UPDATE rol SET requiere_microhub = true WHERE clave = 'repartidor';
COMMENT ON COLUMN rol.requiere_microhub IS 'Perfiles con ámbito por microhub (Operador y Repartidor).';

-- 2. Regla en la base (vale para el portal, los servicios y cualquier script): la entrega solo se asigna a un repartidor del microhub del pedido.
CREATE OR REPLACE FUNCTION fn_entrega_repartidor_microhub() RETURNS trigger AS $$
DECLARE mh_rep integer; mh_ped integer;
BEGIN
  SELECT microhub_id INTO mh_rep FROM usuario WHERE id = NEW.repartidor_id;
  SELECT microhub_id INTO mh_ped FROM pedido WHERE id = NEW.pedido_id;
  IF mh_rep IS NULL THEN
    RAISE EXCEPTION 'RN41: el repartidor no tiene microhub asignado; asígnale uno antes de darle entregas.' USING ERRCODE = 'check_violation';
  END IF;
  IF mh_ped IS DISTINCT FROM mh_rep THEN
    RAISE EXCEPTION 'RN41: el repartidor pertenece a otro microhub; solo recibe pedidos del suyo.' USING ERRCODE = 'check_violation';
  END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_entrega_repartidor_microhub ON entrega;
CREATE TRIGGER trg_entrega_repartidor_microhub
  BEFORE INSERT OR UPDATE OF repartidor_id ON entrega
  FOR EACH ROW EXECUTE FUNCTION fn_entrega_repartidor_microhub();
COMMENT ON FUNCTION fn_entrega_repartidor_microhub() IS 'RN41. Cada repartidor tiene un microhub fijo y solo recibe entregas de pedidos de ese microhub.';
