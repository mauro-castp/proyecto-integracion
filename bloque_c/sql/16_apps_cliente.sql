-- 16_apps_cliente.sql — La app Android también es del cliente (catálogo, pedido, estatus y recepción).
-- El cliente puede mandar pedidos hechos sin conexión por el servicio de sincronización (tipo pedido_nuevo), así que necesita
-- sincronizacion.usar. La confirmación de recepción (POST /entregas/recepciones) usa pedidos.ver, que ya tenía. Es repetible.
SET search_path TO microhubs, public;

-- Una migración reaplicada no restaura un permiso que el administrador retiró.
INSERT INTO rol_permiso (rol_id, permiso_id)
SELECT r.id, p.id FROM rol r CROSS JOIN permiso p
 WHERE NOT EXISTS (SELECT 1 FROM web_migracion WHERE clave = 'apps_cliente_v1')
   AND r.clave = 'cliente' AND p.clave = 'sincronizacion.usar'
ON CONFLICT DO NOTHING;

INSERT INTO web_migracion (clave) VALUES ('apps_cliente_v1') ON CONFLICT DO NOTHING;
