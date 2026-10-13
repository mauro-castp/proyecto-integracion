-- Segundo parcial · Parte C. Idempotente; ejecutar después de 06_planeacion.sql.
BEGIN;
SET LOCAL search_path TO microhubs, public;
CREATE TABLE IF NOT EXISTS web_notificacion (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  destinatario_id integer NOT NULL REFERENCES usuario(id),
  emisor_id integer REFERENCES usuario(id),
  titulo varchar(120) NOT NULL CHECK (length(trim(titulo)) > 0),
  mensaje varchar(2000) NOT NULL CHECK (length(trim(mensaje)) > 0),
  creado_en timestamptz NOT NULL DEFAULT now(), leido_en timestamptz
);
CREATE INDEX IF NOT EXISTS ix_web_notificacion_destino ON web_notificacion(destinatario_id, creado_en DESC);
CREATE TABLE IF NOT EXISTS web_archivo (
  id varchar(32) PRIMARY KEY, propietario_id integer NOT NULL REFERENCES usuario(id),
  nombre varchar(160) NOT NULL, tipo varchar(80) NOT NULL,
  contenido bytea NOT NULL, tamano integer NOT NULL CHECK(tamano BETWEEN 1 AND 5242880),
  creado_en timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_web_archivo_propietario ON web_archivo(propietario_id, creado_en DESC);
INSERT INTO permiso(clave,modulo,accion,descripcion) VALUES
 ('reportes.ver','reportes','ver','Reportes filtrados y gráficas'),
 ('reportes.exportar','reportes','exportar','Exportación CSV de pedidos visibles'),
 ('archivos.ver','archivos','ver','Consultar archivos propios'),
 ('archivos.crear','archivos','crear','Adjuntar imágenes o PDF'),
 ('notificaciones.ver','notificaciones','ver','Consultar avisos propios'),
 ('notificaciones.crear','notificaciones','crear','Enviar avisos a personas activas'),
 ('roles.ver','roles','ver','Consultar perfiles y permisos'),
 ('roles.editar','roles','editar','Administrar permisos de perfiles no administradores')
ON CONFLICT(clave) DO NOTHING;
INSERT INTO rol(clave,nombre,descripcion,requiere_microhub) VALUES
 ('analista','Analista de operación','Consulta y exporta reportes sin modificar operación',false),
 ('supervisor','Supervisor de microhub','Reportes y avisos dentro del ámbito de su microhub',true)
ON CONFLICT(clave) DO NOTHING;
CREATE TABLE IF NOT EXISTS web_migracion(clave varchar(40) PRIMARY KEY, aplicado_en timestamptz NOT NULL DEFAULT now());
-- Una migración reaplicada no debe restaurar permisos que el administrador retiró.
INSERT INTO rol_permiso(rol_id,permiso_id)
SELECT r.id,p.id FROM rol r CROSS JOIN permiso p WHERE
NOT EXISTS (SELECT 1 FROM web_migracion WHERE clave='v1') AND (
 (r.clave='administrador' AND p.clave IN ('reportes.ver','reportes.exportar','archivos.ver','archivos.crear','notificaciones.ver','notificaciones.crear','roles.ver','roles.editar')) OR
 (r.clave IN ('auditor','planeador','analista','supervisor') AND p.clave IN ('reportes.ver','reportes.exportar')) OR
 (r.clave IN ('cliente','operador','repartidor','planeador','auditor','analista','supervisor') AND p.clave IN ('archivos.ver','archivos.crear','notificaciones.ver')))
ON CONFLICT DO NOTHING;
INSERT INTO web_migracion(clave) VALUES('v1') ON CONFLICT DO NOTHING;
CREATE INDEX IF NOT EXISTS ix_web_pedido_fecha ON pedido(creado_en DESC,id DESC);
-- Se ejecuta también cuando otro componente cierra un pedido en la misma base.
CREATE OR REPLACE FUNCTION fn_web_notificar_cierre() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.estado IS DISTINCT FROM OLD.estado AND NEW.estado IN ('entregado','entrega_parcial','entrega_fallida','cancelado') THEN
    INSERT INTO web_notificacion(destinatario_id,emisor_id,titulo,mensaje)
    SELECT c.usuario_id,ctx_usuario_id(),'Pedido ' || NEW.folio,
           'El pedido cambió a ' || NEW.estado::text || '.'
      FROM cliente c WHERE c.id=NEW.cliente_id;
  END IF;
  RETURN NEW;
END $$;
CREATE OR REPLACE TRIGGER trg_web_notificar_cierre AFTER UPDATE OF estado ON pedido
FOR EACH ROW EXECUTE FUNCTION fn_web_notificar_cierre();
COMMIT;
