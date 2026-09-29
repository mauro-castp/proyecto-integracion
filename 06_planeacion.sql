-- Módulo de planeación y viabilidad. Idempotente para bases ya inicializadas.
SET search_path TO microhubs, public;

CREATE TABLE IF NOT EXISTS ubicacion_candidata (
 id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 clave varchar(20) NOT NULL UNIQUE, nombre varchar(120) NOT NULL,
 latitud numeric(9,6) NOT NULL CHECK(latitud BETWEEN 20 AND 33),
 longitud numeric(9,6) NOT NULL CHECK(longitud BETWEEN -118 AND -86),
 renta_estimada numeric(12,2) NOT NULL CHECK(renta_estimada>=0),
 superficie_m2 numeric(10,2) NOT NULL CHECK(superficie_m2>0),
 capacidad_fisica integer NOT NULL CHECK(capacidad_fisica>0),
 accesibilidad_vial smallint NOT NULL CHECK(accesibilidad_vial BETWEEN 1 AND 10),
 zona_id integer NOT NULL REFERENCES zona(id), poblacion_cubierta integer NOT NULL CHECK(poblacion_cubierta>=0),
 costo_fijo numeric(12,2) NOT NULL CHECK(costo_fijo>=0),
 demanda_cubierta numeric(10,2) NOT NULL CHECK(demanda_cubierta>=0),
 distancia_promedio numeric(8,2) NOT NULL CHECK(distancia_promedio>=0),
 estatus estatus_registro NOT NULL DEFAULT 'activo', creado_en timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS escenario_planeacion (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, nombre varchar(120) NOT NULL,
 ubicacion_candidata_id integer REFERENCES ubicacion_candidata(id), creado_por integer REFERENCES usuario(id),
 supuestos jsonb NOT NULL, resultados jsonb NOT NULL, creado_en timestamptz NOT NULL DEFAULT now()
);

INSERT INTO ubicacion_candidata(clave,nombre,latitud,longitud,renta_estimada,superficie_m2,capacidad_fisica,
 accesibilidad_vial,zona_id,poblacion_cubierta,costo_fijo,demanda_cubierta,distancia_promedio)
SELECT 'CAND-01','San Bernabé Centro',25.748,-100.364,18000,130,150,9,z.id,8420,72000,126,2.4
FROM zona z WHERE z.clave='ZN-SB01' ON CONFLICT(clave) DO NOTHING;
INSERT INTO ubicacion_candidata(clave,nombre,latitud,longitud,renta_estimada,superficie_m2,capacidad_fisica,
 accesibilidad_vial,zona_id,poblacion_cubierta,costo_fijo,demanda_cubierta,distancia_promedio)
SELECT 'CAND-02','Valles Poniente',25.755,-100.372,15500,105,120,7,z.id,6180,65500,93,3.1
FROM zona z WHERE z.clave='ZN-SB02' ON CONFLICT(clave) DO NOTHING;

INSERT INTO configuracion(clave,valor,tipo_dato,ambito,unidad,descripcion) VALUES
 ('peso_score_demanda','1.0','numerico','global','peso','Peso configurable de demanda cubierta'),
 ('peso_score_renta','1.2','numerico','global','peso','Peso configurable de renta mensual'),
 ('peso_score_distancia','4.0','numerico','global','peso','Peso configurable de distancia promedio'),
 ('peso_score_accesibilidad','3.0','numerico','global','peso','Peso configurable de accesibilidad vial'),
 ('pedidos_operador_hora','5','numerico','global','pedidos/hora','Productividad usada para capacidad'),
 ('umbral_utilizacion_estable','70','numerico','global','porcentaje','Menor a 70% se considera estable'),
 ('umbral_utilizacion_riesgo','85','numerico','global','porcentaje','Mayor a 85% indica saturación')
ON CONFLICT(clave,ambito,ambito_id) DO NOTHING;

GRANT SELECT,INSERT,UPDATE ON ubicacion_candidata,escenario_planeacion TO app_microhubs;
GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA microhubs TO app_microhubs;
