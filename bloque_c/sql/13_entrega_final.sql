-- =====================================================================
-- 13_entrega_final.sql — Cambios de esquema de la entrega final
-- Codex Innovations · Equipo 04 · idempotente (servicios/migrar.py lo aplica a volúmenes existentes)
-- =====================================================================
SET search_path = microhubs, public;

-- Las exportaciones de reportes se archivan en el almacén de objetos (Google Cloud Storage). La tabla guarda solo la ruta del objeto
-- y en qué almacén quedó; el archivo nunca entra a la base de datos (lineamiento: la base conserva identificador, ruta, tipo, tamaño,
-- propietario, fecha, hash y estado). Una exportación con ruta NULL es una que no se pudo archivar (el bucket no respondía).
ALTER TABLE reporte_exportacion ADD COLUMN IF NOT EXISTS ruta    varchar(300);
ALTER TABLE reporte_exportacion ADD COLUMN IF NOT EXISTS almacen varchar(10);
COMMENT ON COLUMN reporte_exportacion.ruta IS 'Clave del objeto en el bucket: reportes/AAAA/MM/<id>.<ext>. NULL si no se archivó.';
