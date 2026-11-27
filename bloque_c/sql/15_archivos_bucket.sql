-- 15_archivos_bucket.sql — La base de datos no guarda archivos.
-- Hasta la entrega final, la pantalla «Archivos» del portal guardaba el contenido en web_archivo. Ahora usa el almacén de objetos
-- (servicio de documentos). En una base anterior la tabla se retira si está vacía; si todavía tiene archivos se conserva hasta moverlos con
--   docker compose -f docker-compose.integrado.yml exec documentos python -m servicio.migrar_web_archivo
-- y volver a correr las migraciones. Es repetible.
SET search_path TO microhubs, public;

DO $$
BEGIN
    IF to_regclass('microhubs.web_archivo') IS NULL THEN
        RETURN;
    END IF;
    IF EXISTS (SELECT 1 FROM microhubs.web_archivo) THEN
        RAISE NOTICE 'web_archivo todavía tiene archivos: muévelos con servicio.migrar_web_archivo';
    ELSE
        DROP TABLE microhubs.web_archivo;
    END IF;
END $$;
