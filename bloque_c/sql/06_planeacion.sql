-- =====================================================================
-- 06_planeacion.sql — Módulo de planeación y viabilidad de microhubs
-- Codex Innovations · Equipo 04
--
-- Idempotente: se ejecuta en el primer arranque (initdb) y de nuevo, sin
-- efectos duplicados, desde migrar_planeacion.py en volúmenes ya creados.
-- Convención de configuración (RN40): ningún peso, umbral ni productividad
-- vive como constante en el código; todo está en la tabla configuracion
-- con su justificación en la columna descripcion.
-- =====================================================================
SET search_path TO microhubs, public;

-- ---------- Extensiones a tablas existentes ----------
ALTER TABLE producto ADD COLUMN IF NOT EXISTS costo_unitario numeric(10,2)
    CHECK (costo_unitario IS NULL OR costo_unitario >= 0);
ALTER TABLE producto ADD COLUMN IF NOT EXISTS espacio_unidades numeric(6,2) NOT NULL DEFAULT 1
    CHECK (espacio_unidades > 0);
COMMENT ON COLUMN producto.costo_unitario IS 'Costo de adquisición. NULL = se estima con margen_bruto_default (configuracion). Base del margen por SKU en la planeación de surtido.';
COMMENT ON COLUMN producto.espacio_unidades IS 'Espacio que ocupa una unidad, en unidades de anaquel. Base de la restricción de espacio del surtido.';

ALTER TABLE pedido ADD COLUMN IF NOT EXISTS listo_en timestamptz;
COMMENT ON COLUMN pedido.listo_en IS 'El operador terminó de prepararlo. Un pedido en_preparacion con listo_en queda disponible para agrupar por zona, asignar repartidor y despachar (Planeación > Entregas).';

ALTER TABLE zona ADD COLUMN IF NOT EXISTS poblacion integer
    CHECK (poblacion IS NULL OR poblacion >= 0);
COMMENT ON COLUMN zona.poblacion IS 'Habitantes estimados de la zona. Alimenta cobertura (hogares potencialmente atendidos).';

-- ---------- Ubicaciones candidatas ----------
CREATE TABLE IF NOT EXISTS ubicacion_candidata (
    id                 integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    clave              varchar(20)  NOT NULL UNIQUE,
    nombre             varchar(120) NOT NULL,
    latitud            numeric(9,6) NOT NULL CHECK (latitud  BETWEEN 20 AND 33),
    longitud           numeric(9,6) NOT NULL CHECK (longitud BETWEEN -118 AND -86),
    renta_estimada     numeric(12,2) NOT NULL CHECK (renta_estimada >= 0),
    nomina_estimada    numeric(12,2) NOT NULL DEFAULT 0 CHECK (nomina_estimada >= 0),
    servicios_estimados numeric(12,2) NOT NULL DEFAULT 0 CHECK (servicios_estimados >= 0),
    otros_costos       numeric(12,2) NOT NULL DEFAULT 0 CHECK (otros_costos >= 0),
    costo_fijo         numeric(12,2) GENERATED ALWAYS AS
                       (renta_estimada + nomina_estimada + servicios_estimados + otros_costos) STORED,
    superficie_m2      numeric(10,2) NOT NULL CHECK (superficie_m2 > 0),
    capacidad_fisica   integer NOT NULL CHECK (capacidad_fisica > 0),
    accesibilidad_vial smallint NOT NULL CHECK (accesibilidad_vial BETWEEN 1 AND 10),
    zona_id            integer NOT NULL REFERENCES zona (id),
    poblacion_cubierta integer NOT NULL CHECK (poblacion_cubierta >= 0),
    radio_km           numeric(5,2) NOT NULL DEFAULT 1.5 CHECK (radio_km > 0),
    decision           varchar(12) NOT NULL DEFAULT 'pendiente'
                       CHECK (decision IN ('pendiente','aceptado','rechazado','condicionado')),
    decision_motivo    varchar(300),
    decision_por       integer REFERENCES usuario (id),
    decision_en        timestamptz,
    estatus            estatus_registro NOT NULL DEFAULT 'activo',
    creado_en          timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT ck_cand_decision_motivo CHECK (decision = 'pendiente' OR decision_motivo IS NOT NULL)
);
COMMENT ON TABLE ubicacion_candidata IS 'Catálogo de sitios posibles antes de ser microhub. costo_fijo es generado: renta + nómina + servicios + otros. La decisión de apertura es humana y exige motivo.';
COMMENT ON COLUMN ubicacion_candidata.capacidad_fisica IS 'Máximo de pedidos/día que el espacio físico permite preparar (tope independiente de operadores).';

-- ---------- Escenarios ----------
CREATE TABLE IF NOT EXISTS escenario_planeacion (
    id                     bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre                 varchar(120) NOT NULL,
    ubicacion_candidata_id integer REFERENCES ubicacion_candidata (id),
    creado_por             integer REFERENCES usuario (id),
    supuestos              jsonb NOT NULL,
    resultados             jsonb NOT NULL,
    creado_en              timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE escenario_planeacion ADD COLUMN IF NOT EXISTS actualizado_en timestamptz NOT NULL DEFAULT now();
ALTER TABLE escenario_planeacion ADD COLUMN IF NOT EXISTS actualizado_por integer REFERENCES usuario (id);
CREATE INDEX IF NOT EXISTS ix_escenario_candidata ON escenario_planeacion (ubicacion_candidata_id);

-- ---------- Rutas planeadas ----------
CREATE TABLE IF NOT EXISTS plan_ruta (
    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    microhub_id    integer NOT NULL REFERENCES microhub (id),
    repartidor_id  integer NOT NULL REFERENCES usuario (id),
    fecha          date    NOT NULL DEFAULT current_date,
    metodo         varchar(30) NOT NULL,
    paradas        integer NOT NULL CHECK (paradas > 0),
    distancia_km   numeric(8,2) NOT NULL CHECK (distancia_km >= 0),
    minutos        numeric(8,1) NOT NULL CHECK (minutos >= 0),
    costo_estimado numeric(10,2) NOT NULL CHECK (costo_estimado >= 0),
    creado_por     integer REFERENCES usuario (id),
    creado_en      timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS plan_ruta_parada (
    plan_ruta_id  bigint  NOT NULL REFERENCES plan_ruta (id) ON DELETE CASCADE,
    orden         integer NOT NULL CHECK (orden > 0),
    pedido_id     bigint  NOT NULL REFERENCES pedido (id),
    tramo_km      numeric(8,2) NOT NULL,
    minutos_acum  numeric(8,1) NOT NULL,
    PRIMARY KEY (plan_ruta_id, orden)
);
ALTER TABLE entrega ADD COLUMN IF NOT EXISTS plan_ruta_id bigint REFERENCES plan_ruta (id);
ALTER TABLE entrega ADD COLUMN IF NOT EXISTS orden_parada integer;
ALTER TABLE entrega ADD COLUMN IF NOT EXISTS distancia_km numeric(8,2);
ALTER TABLE entrega ADD COLUMN IF NOT EXISTS minutos_estimados numeric(8,1);
ALTER TABLE entrega ADD COLUMN IF NOT EXISTS costo_entrega_estimado numeric(10,2);

-- ---------- Candidatos de demostración (ON CONFLICT: idempotente) ----------
INSERT INTO ubicacion_candidata (clave, nombre, latitud, longitud, renta_estimada, nomina_estimada,
    servicios_estimados, otros_costos, superficie_m2, capacidad_fisica, accesibilidad_vial, zona_id,
    poblacion_cubierta, radio_km)
SELECT v.clave, v.nombre, v.lat, v.lng, v.renta, v.nomina, v.serv, v.otros, v.sup, v.cap, v.acc, z.id, v.pob, v.radio
  FROM (VALUES
    ('CAND-01','San Bernabé Norte',   25.752000,-100.361000, 18000,42000,7000,5000, 130,150,9, 'ZN-SB01', 8420,1.5),
    ('CAND-02','Valles Poniente',     25.755500,-100.376000, 15500,42000,6500,4500, 105,120,7, 'ZN-SB02', 6180,1.5),
    ('CAND-03','Paseo Sur',           25.759000,-100.372000, 14000,38000,6000,4000,  95,110,6, 'ZN-SB03', 5240,1.4),
    ('CAND-04','F-113 Oriente',       25.747000,-100.376500, 12500,38000,5500,4000,  90,100,5, 'ZN-SB04', 4310,1.3),
    ('CAND-05','Alianza Real',        25.762500,-100.353000, 21000,46000,8000,6000, 150,180,8, 'ZN-SB03', 3900,1.6)
  ) AS v(clave,nombre,lat,lng,renta,nomina,serv,otros,sup,cap,acc,zclave,pob,radio)
  JOIN zona z ON z.clave = v.zclave
ON CONFLICT (clave) DO NOTHING;

-- Población estimada de las zonas (solo si aún no se capturó).
UPDATE zona SET poblacion = CASE clave WHEN 'ZN-SB01' THEN 8420 WHEN 'ZN-SB02' THEN 6180
                                        WHEN 'ZN-SB03' THEN 5240 WHEN 'ZN-SB04' THEN 4310 END
 WHERE poblacion IS NULL AND clave IN ('ZN-SB01','ZN-SB02','ZN-SB03','ZN-SB04');

-- ---------- Parámetros configurables y su justificación ----------
INSERT INTO configuracion (clave, valor, tipo_dato, ambito, unidad, descripcion) VALUES
 ('peso_score_demanda','1.0','numerico','global','peso','Score de ubicación: multiplica la demanda cubierta (pedidos/día). Referencia de escala 1:1.'),
 ('peso_score_renta','1.2','numerico','global','peso','Score: multiplica la renta en miles de MXN. Un peso mayor a 1 castiga los costos fijos, principal riesgo de no llegar al equilibrio.'),
 ('peso_score_distancia','4.0','numerico','global','peso','Score: multiplica la distancia promedio ponderada (km). Cada km adicional encarece la última milla y alarga el tiempo de entrega.'),
 ('peso_score_accesibilidad','3.0','numerico','global','peso','Score: multiplica la accesibilidad vial (1-10). Facilita abasto y reparto.'),
 ('picking_pedidos_hora','10','numerico','global','pedidos/h','Productividad de picking por operador (6 min por pedido de ~5 líneas). Supuesto inicial a calibrar con tiempos reales.'),
 ('packing_pedidos_hora','20','numerico','global','pedidos/h','Productividad de empaque por operador (3 min por pedido).'),
 ('despacho_pedidos_hora','30','numerico','global','pedidos/h','Productividad de despacho por operador (2 min: verificar y entregar al repartidor).'),
 ('umbral_utilizacion_estable','70','numerico','global','porcentaje','Debajo de 70% hay holgura para absorber picos (los picos horarios suelen ser 1.3-1.4 veces el promedio).'),
 ('umbral_utilizacion_riesgo','85','numerico','global','porcentaje','Arriba de 85% la teoría de colas (M/M/c) muestra que la espera crece de forma no lineal: riesgo de saturación.'),
 ('velocidad_reparto_kmh','22','numerico','global','km/h','Velocidad urbana media de reparto en moto o bicicleta, con semáforos y esquinas.'),
 ('tiempo_servicio_min','4','numerico','global','minutos','Tiempo por parada: estacionar, entregar, cobrar y confirmar.'),
 ('paradas_por_viaje','3','entero','global','paradas','Paradas promedio por viaje de un repartidor al agrupar pedidos por zona.'),
 ('max_paradas_repartidor','8','entero','global','paradas','Tope de paradas por repartidor en una salida; con más, el TSP exacto deja de ser viable y las entregas se enfrían.'),
 ('costo_km_reparto','4.5','numerico','global','MXN/km','Costo variable por km de reparto (combustible, desgaste y seguro).'),
 ('costo_base_entrega','18','numerico','global','MXN','Pago base por entrega al repartidor; se suma al costo por distancia para obtener el costo de última milla.'),
 ('tamano_hogar','3.6','numerico','global','personas','Personas por hogar; convierte población cubierta en hogares potencialmente atendidos.'),
 ('dias_operacion_mes','30','entero','global','días','Días de operación al mes para convertir equilibrio mensual a diario.'),
 ('horas_turno','10','numerico','global','horas','Horas de operación del microhub por día.'),
 ('margen_bruto_default','0.28','numerico','global','fracción','Margen bruto sobre venta cuando el producto no tiene costo capturado. Abarrotes urbanos: 20-35%.'),
 ('abc_a_pct','80','numerico','global','porcentaje','Clasificación ABC: los SKU que acumulan hasta 80% del movimiento son clase A (regla de Pareto).'),
 ('abc_b_pct','95','numerico','global','porcentaje','Clasificación ABC: hasta 95% acumulado es clase B; el 5% restante es C.'),
 ('cobertura_dias_a','7','numerico','global','días','Días de cobertura objetivo para SKU clase A.'),
 ('cobertura_dias_b','5','numerico','global','días','Días de cobertura objetivo para SKU clase B.'),
 ('cobertura_dias_c','3','numerico','global','días','Días de cobertura objetivo para SKU clase C.'),
 ('cobertura_dias_exceso','30','numerico','global','días','Arriba de este número de días de cobertura el stock se considera excesivo.'),
 ('ventana_analisis_dias','90','entero','global','días','Ventana histórica para demanda, rotación y ABC.')
ON CONFLICT (clave, ambito, ambito_id) DO NOTHING;

-- ---------- Permisos ----------
INSERT INTO permiso (clave, modulo, accion) VALUES
 ('planeacion.ver','planeacion','ver'),
 ('planeacion.editar','planeacion','editar')
ON CONFLICT (clave) DO NOTHING;

INSERT INTO rol_permiso (rol_id, permiso_id)
SELECT r.id, p.id FROM rol r JOIN permiso p ON p.clave IN ('planeacion.ver','planeacion.editar')
 WHERE r.clave IN ('administrador','planeador')
ON CONFLICT DO NOTHING;
INSERT INTO rol_permiso (rol_id, permiso_id)
SELECT r.id, p.id FROM rol r JOIN permiso p ON p.clave = 'planeacion.ver'
 WHERE r.clave = 'auditor'
ON CONFLICT DO NOTHING;
INSERT INTO rol_permiso (rol_id, permiso_id)
SELECT r.id, p.id FROM rol r JOIN permiso p ON p.clave IN ('configuracion.ver','inventario.ver')
 WHERE r.clave = 'planeador'
ON CONFLICT DO NOTHING;

-- ---------- Auditoría (RN30) y permisos de la base ----------
DO $$
DECLARE t text;
BEGIN
    FOREACH t IN ARRAY ARRAY['ubicacion_candidata','escenario_planeacion','plan_ruta'] LOOP
        EXECUTE format(
            'CREATE OR REPLACE TRIGGER trg_aud_%1$s AFTER INSERT OR UPDATE OR DELETE ON %1$I '
            'FOR EACH ROW EXECUTE FUNCTION fn_auditar_cambio(%2$L)', t, 'planeacion');
    END LOOP;
END $$;

GRANT SELECT, INSERT, UPDATE ON ubicacion_candidata, escenario_planeacion, plan_ruta, plan_ruta_parada TO app_microhubs;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA microhubs TO app_microhubs;
GRANT SELECT ON ubicacion_candidata, escenario_planeacion, plan_ruta, plan_ruta_parada TO auditor_microhubs;
