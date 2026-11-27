-- 20_portal_archivos.sql — Archivos que cada usuario sube en el portal («Mis archivos»).
-- El portal (monolito) solo habla con sus bases de datos: ya no le pide al servicio de documentos que los guarde.
-- Los archivos de las apps (evidencias de entrega, comprobantes) siguen en el bucket por medio del servicio de documentos.
CREATE TABLE IF NOT EXISTS web_archivo (
    id             varchar(32)  PRIMARY KEY,
    propietario_id integer      NOT NULL REFERENCES usuario (id),
    nombre         varchar(160) NOT NULL,
    tipo           varchar(60)  NOT NULL,
    contenido      bytea        NOT NULL,
    tamano         integer      NOT NULL CHECK (tamano BETWEEN 1 AND 5242880),
    creado_en      timestamptz  NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_web_archivo_propietario ON web_archivo (propietario_id, creado_en DESC);
COMMENT ON TABLE web_archivo IS 'Mis archivos del portal: PDF, PNG o JPEG de hasta 5 MB, visibles solo para su dueño.';
