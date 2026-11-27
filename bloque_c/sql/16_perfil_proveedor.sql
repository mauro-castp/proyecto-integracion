-- 16_perfil_proveedor.sql — El perfil «proveedor» entra al portal: ve sus órdenes de compra y mantiene su oferta. Es repetible.
BEGIN;
SET LOCAL search_path TO microhubs, public;

INSERT INTO rol (clave, nombre, descripcion, requiere_microhub)
SELECT 'proveedor', 'Proveedor', 'Consulta sus órdenes de compra y mantiene su catálogo de oferta. Solo lo suyo.', false
 WHERE NOT EXISTS (SELECT 1 FROM rol WHERE clave = 'proveedor');

INSERT INTO permiso (clave, modulo, accion, descripcion)
SELECT 'proveedor.portal', 'proveedor', 'portal', 'Portal del proveedor: su catálogo, su oferta y sus órdenes'
 WHERE NOT EXISTS (SELECT 1 FROM permiso WHERE clave = 'proveedor.portal');

INSERT INTO rol_permiso (rol_id, permiso_id)
SELECT r.id, p.id FROM rol r JOIN permiso p ON p.clave IN ('proveedor.portal', 'notificaciones.ver', 'archivos.ver', 'archivos.crear')
 WHERE r.clave = 'proveedor' AND NOT EXISTS (SELECT 1 FROM rol_permiso x WHERE x.rol_id = r.id AND x.permiso_id = p.id);

-- cada cuenta de proveedor se liga a un proveedor
ALTER TABLE proveedor ADD COLUMN IF NOT EXISTS usuario_id integer REFERENCES usuario (id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_proveedor_usuario ON proveedor (usuario_id) WHERE usuario_id IS NOT NULL;

-- cuenta de demostración, con la misma clave que las demás (en la nube, la que generó el instalador)
INSERT INTO usuario (nombre, apellidos, correo, telefono, hash_contrasena, rol_id)
SELECT 'Proveedor', 'de demostración', 'proveedor@codex.mx', '8100000000', u.hash_contrasena, r.id
  FROM usuario u CROSS JOIN rol r
 WHERE u.correo = 'planeador@codex.mx' AND r.clave = 'proveedor'
   AND NOT EXISTS (SELECT 1 FROM usuario WHERE lower(correo) = 'proveedor@codex.mx');

UPDATE proveedor SET usuario_id = (SELECT id FROM usuario WHERE lower(correo) = 'proveedor@codex.mx')
 WHERE id = (SELECT p.id FROM proveedor p WHERE p.estatus = 'activo'
              ORDER BY (SELECT count(*) FROM orden_compra o WHERE o.proveedor_id = p.id) DESC,
                       (SELECT count(*) FROM proveedor_producto pp WHERE pp.proveedor_id = p.id) DESC, p.id LIMIT 1)
   AND NOT EXISTS (SELECT 1 FROM proveedor WHERE usuario_id IS NOT NULL);
COMMIT;
