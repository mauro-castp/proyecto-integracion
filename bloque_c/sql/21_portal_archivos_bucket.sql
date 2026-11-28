-- 21_portal_archivos_bucket.sql — «Mis archivos» del portal: el contenido va al almacén de objetos y la base guarda solo sus datos.
-- El portal escribe en el almacén directamente (sistema_web/almacen_portal.py), sin pasar por los microservicios. Las filas antiguas
-- que todavía tengan el contenido en la base se mueven al arrancar el portal (migrar_web.py). Es repetible.
SET search_path TO microhubs, public;

ALTER TABLE web_archivo ALTER COLUMN contenido DROP NOT NULL;
ALTER TABLE web_archivo ADD COLUMN IF NOT EXISTS ruta       varchar(200);
ALTER TABLE web_archivo ADD COLUMN IF NOT EXISTS almacen    varchar(10);
ALTER TABLE web_archivo ADD COLUMN IF NOT EXISTS sha256     char(64);
ALTER TABLE web_archivo ADD COLUMN IF NOT EXISTS privacidad varchar(12) NOT NULL DEFAULT 'privado';
ALTER TABLE web_archivo ADD COLUMN IF NOT EXISTS estado     varchar(12) NOT NULL DEFAULT 'activo';

CREATE UNIQUE INDEX IF NOT EXISTS ux_web_archivo_ruta ON web_archivo (ruta) WHERE ruta IS NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_web_archivo_donde' AND conrelid = 'microhubs.web_archivo'::regclass) THEN
        ALTER TABLE microhubs.web_archivo ADD CONSTRAINT ck_web_archivo_donde CHECK (ruta IS NOT NULL OR contenido IS NOT NULL);
    END IF;
END $$;

COMMENT ON TABLE web_archivo IS 'Datos de «Mis archivos» del portal. El contenido está en el almacén de objetos (columna ruta), no en la base.';
