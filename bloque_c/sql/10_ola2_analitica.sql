-- 10_ola2_analitica.sql · Tercer avance · Ola 2 (análisis, planeación y viabilidad)
-- Codex Innovations · Equipo 04
--
-- Idempotente: se puede aplicar sobre una base existente cuantas veces se quiera
-- (servicios/migrar.py lo hace al levantar docker-compose.integrado.yml).
--
-- Servicios que usan estas tablas (cada una tiene un solo dueño):
--   demanda          (5115)  demanda_observacion
--   cobertura        (5116)  cobertura_zona_dato, cobertura_evaluacion
--   capacidad        (5117)  capacidad_recurso
--   rutas            (5118)  plan_despacho, plan_ruta, plan_ruta_parada
--   costos           (5119)  costo_concepto
--   punto-equilibrio (5120)  equilibrio_escenario
--   simulacion       (5121)  simulacion_ejecucion
--   surtido          (5122)  surtido_restriccion, surtido_producto_param, surtido_recomendacion(+linea)
-- Todos documentan sus supuestos en supuesto_documentado (de dónde sale cada valor y cómo se calibra).
BEGIN;
SET LOCAL search_path TO microhubs, public;

-- 1. Supuestos documentados ----------------------------------------------------------------
-- El valor vive en configuracion (RN40). Aquí se dice de dónde sale y cómo se corrige con datos reales.
CREATE TABLE IF NOT EXISTS supuesto_documentado (
    clave          varchar(60)  PRIMARY KEY,
    servicio       varchar(20)  NOT NULL,
    origen         varchar(10)  NOT NULL,
    justificacion  varchar(700) NOT NULL,
    como_calibrar  varchar(500),
    actualizado_en timestamptz  NOT NULL DEFAULT now(),
    CONSTRAINT ck_supuesto_origen CHECK (origen IN ('medido', 'supuesto', 'normativo'))
);
COMMENT ON TABLE supuesto_documentado IS
    'medido = sale de datos del propio sistema; normativo = decisión del equipo o regla del negocio; supuesto = valor razonable que aún no se ha medido y debe calibrarse.';

-- 2. Demanda -----------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS demanda_observacion (
    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fecha        date        NOT NULL,
    zona_id      integer     NOT NULL REFERENCES zona (id),
    categoria_id integer     REFERENCES categoria (id),
    pedidos      integer     NOT NULL DEFAULT 0,
    unidades     integer     NOT NULL DEFAULT 0,
    venta        numeric(12,2) NOT NULL DEFAULT 0,
    clientes     integer     NOT NULL DEFAULT 0,
    no_atendidos integer     NOT NULL DEFAULT 0,
    fuente       varchar(10) NOT NULL DEFAULT 'pedidos',
    actualizado_en timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_demanda_obs UNIQUE NULLS NOT DISTINCT (fecha, zona_id, categoria_id),
    CONSTRAINT ck_demanda_fuente CHECK (fuente IN ('pedidos', 'sintetica', 'manual')),
    CONSTRAINT ck_demanda_valores CHECK (pedidos >= 0 AND unidades >= 0 AND venta >= 0 AND clientes >= 0 AND no_atendidos >= 0)
);
CREATE INDEX IF NOT EXISTS ix_demanda_zona_fecha ON demanda_observacion (zona_id, fecha);
COMMENT ON COLUMN demanda_observacion.categoria_id IS 'NULL = total de la zona y el día. Con categoría, solo pedidos, unidades y venta de esa categoría.';
COMMENT ON COLUMN demanda_observacion.fuente IS 'pedidos = leído del servicio de pedidos; sintetica = historia de demostración generada por la migración (NO son ventas reales); manual = capturada a mano.';

-- 3. Cobertura ---------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cobertura_zona_dato (
    zona_id        integer PRIMARY KEY REFERENCES zona (id),
    poblacion      integer NOT NULL,
    fuente         varchar(200) NOT NULL,
    actualizado_en timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT ck_czd_poblacion CHECK (poblacion >= 0)
);
CREATE TABLE IF NOT EXISTS cobertura_evaluacion (
    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre     varchar(120) NOT NULL,
    parametros json NOT NULL,
    resultado  json NOT NULL,
    creado_por integer REFERENCES usuario (id),
    creado_en  timestamptz NOT NULL DEFAULT now()
);

-- 4. Capacidad ---------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS capacidad_recurso (
    microhub_id      integer PRIMARY KEY REFERENCES microhub (id),
    operadores       smallint NOT NULL,
    repartidores     smallint NOT NULL,
    capacidad_fisica integer,
    actualizado_por  integer REFERENCES usuario (id),
    actualizado_en   timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT ck_cap_operadores   CHECK (operadores BETWEEN 1 AND 50),
    CONSTRAINT ck_cap_repartidores CHECK (repartidores BETWEEN 1 AND 50),
    CONSTRAINT ck_cap_fisica       CHECK (capacidad_fisica IS NULL OR capacidad_fisica > 0)
);
COMMENT ON COLUMN capacidad_recurso.capacidad_fisica IS 'Tope de pedidos por día que permite el espacio del local, independiente de cuántas personas trabajen. NULL = sin tope de espacio.';

-- 5. Costos ------------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS costo_concepto (
    id            integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ambito        varchar(10) NOT NULL,
    ambito_id     integer,
    nombre        varchar(120) NOT NULL,
    categoria     varchar(15) NOT NULL,
    tipo          varchar(8)  NOT NULL,
    unidad        varchar(10) NOT NULL,
    monto         numeric(12,2) NOT NULL,
    vigente_desde date NOT NULL DEFAULT fn_hoy(),
    vigente_hasta date,
    estatus       estatus_registro NOT NULL DEFAULT 'activo',
    fuente        varchar(10) NOT NULL DEFAULT 'supuesto',
    justificacion varchar(300) NOT NULL,
    creado_por    integer REFERENCES usuario (id),
    creado_en     timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT ck_costo_ambito   CHECK (ambito IN ('global', 'microhub', 'candidato')),
    CONSTRAINT ck_costo_ambito_id CHECK ((ambito = 'global') = (ambito_id IS NULL)),
    CONSTRAINT ck_costo_categoria CHECK (categoria IN ('renta', 'personal', 'servicios', 'almacenamiento', 'transporte', 'operacion', 'otros')),
    CONSTRAINT ck_costo_tipo     CHECK (tipo IN ('fijo', 'variable')),
    CONSTRAINT ck_costo_unidad   CHECK (unidad IN ('mes', 'pedido', 'entrega', 'km', 'pct_venta')),
    CONSTRAINT ck_costo_tipo_unidad CHECK ((tipo = 'fijo') = (unidad = 'mes')),
    CONSTRAINT ck_costo_monto    CHECK (monto >= 0 AND (unidad <> 'pct_venta' OR monto <= 100)),
    CONSTRAINT ck_costo_fuente   CHECK (fuente IN ('medido', 'supuesto', 'contrato')),
    CONSTRAINT ck_costo_vigencia CHECK (vigente_hasta IS NULL OR vigente_hasta >= vigente_desde)
);
CREATE INDEX IF NOT EXISTS ix_costo_ambito ON costo_concepto (ambito, ambito_id) WHERE estatus = 'activo';
COMMENT ON TABLE costo_concepto IS
    'Un renglón de costo. Fijo = monto por mes; variable = por pedido, por entrega, por km o porcentaje de la venta. Un concepto de un microhub o candidato con el mismo nombre que uno global lo sustituye.';

-- 6. Punto de equilibrio -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS equilibrio_escenario (
    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre       varchar(120) NOT NULL,
    microhub_id  integer REFERENCES microhub (id),
    candidato_id integer,
    supuestos    json NOT NULL,
    resultados   json NOT NULL,
    creado_por   integer REFERENCES usuario (id),
    creado_en    timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT ck_equilibrio_objeto CHECK (microhub_id IS NULL OR candidato_id IS NULL)
);

-- 7. Simulación (ejecuciones asíncronas y reproducibles) ---------------------------------------
CREATE TABLE IF NOT EXISTS simulacion_ejecucion (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre        varchar(120) NOT NULL,
    estado        varchar(10)  NOT NULL DEFAULT 'en_cola',
    microhub_id   integer REFERENCES microhub (id),
    candidato_id  integer,
    semilla       integer NOT NULL,
    version_modelo varchar(10) NOT NULL,
    parametros    json NOT NULL,
    resultados    json,
    huella        varchar(64),
    error         varchar(500),
    intentos      smallint NOT NULL DEFAULT 0,
    creado_por    integer REFERENCES usuario (id),
    creado_en     timestamptz NOT NULL DEFAULT now(),
    inicio_en     timestamptz,
    fin_en        timestamptz,
    CONSTRAINT ck_sim_estado CHECK (estado IN ('en_cola', 'ejecutando', 'terminada', 'fallida', 'cancelada')),
    CONSTRAINT ck_sim_objeto CHECK (microhub_id IS NULL OR candidato_id IS NULL)
);
CREATE INDEX IF NOT EXISTS ix_sim_cola ON simulacion_ejecucion (creado_en) WHERE estado = 'en_cola';
COMMENT ON COLUMN simulacion_ejecucion.parametros IS 'Foto de todos los insumos al crear la ejecución (demanda, capacidad, costos, escenario). Con estos parámetros y la semilla el resultado es el mismo siempre.';
COMMENT ON COLUMN simulacion_ejecucion.huella IS 'SHA-256 de los resultados: sirve para comprobar que una repetición dio exactamente lo mismo.';

-- 8. Surtido -------------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS surtido_restriccion (
    microhub_id    integer PRIMARY KEY REFERENCES microhub (id),
    espacio_total  numeric(10,1) NOT NULL,
    presupuesto    numeric(12,2),
    actualizado_por integer REFERENCES usuario (id),
    actualizado_en timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT ck_sur_espacio CHECK (espacio_total > 0),
    CONSTRAINT ck_sur_presupuesto CHECK (presupuesto IS NULL OR presupuesto > 0)
);
CREATE TABLE IF NOT EXISTS surtido_producto_param (
    producto_id    integer PRIMARY KEY REFERENCES producto (id),
    espacio_unidades numeric(6,2) NOT NULL DEFAULT 1,
    actualizado_en timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT ck_spp_espacio CHECK (espacio_unidades > 0)
);
CREATE TABLE IF NOT EXISTS surtido_recomendacion (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    microhub_id integer NOT NULL REFERENCES microhub (id),
    parametros  json NOT NULL,
    resumen     json NOT NULL,
    creado_por  integer REFERENCES usuario (id),
    creado_en   timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS surtido_recomendacion_linea (
    recomendacion_id bigint  NOT NULL REFERENCES surtido_recomendacion (id) ON DELETE CASCADE,
    producto_id      integer NOT NULL REFERENCES producto (id),
    clase            char(1) NOT NULL,
    accion           varchar(12) NOT NULL,
    unidades         integer NOT NULL,
    existencia       integer NOT NULL,
    sugerido         integer NOT NULL,
    margen_unitario  numeric(10,2),
    rotacion         numeric(8,2),
    motivo           varchar(200),
    PRIMARY KEY (recomendacion_id, producto_id),
    CONSTRAINT ck_srl_clase CHECK (clase IN ('A', 'B', 'C')),
    CONSTRAINT ck_srl_accion CHECK (accion IN ('Aumentar', 'Mantener', 'Reducir', 'Eliminar', 'Excluir'))
);

-- 9. Rutas: un plan de despacho agrupa las rutas de un microhub ----------------------------------
CREATE TABLE IF NOT EXISTS plan_despacho (
    id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    microhub_id   integer NOT NULL REFERENCES microhub (id),
    fecha         date    NOT NULL DEFAULT fn_hoy(),
    estado        varchar(10) NOT NULL DEFAULT 'propuesto',
    version       smallint NOT NULL DEFAULT 1,
    parametros    json NOT NULL,
    resultado     json NOT NULL,
    creado_por    integer REFERENCES usuario (id),
    creado_en     timestamptz NOT NULL DEFAULT now(),
    confirmado_por integer REFERENCES usuario (id),
    confirmado_en timestamptz,
    CONSTRAINT ck_pd_estado CHECK (estado IN ('propuesto', 'confirmado', 'cancelado'))
);
CREATE INDEX IF NOT EXISTS ix_pd_hub ON plan_despacho (microhub_id, estado);
ALTER TABLE plan_ruta ADD COLUMN IF NOT EXISTS plan_despacho_id bigint REFERENCES plan_despacho (id);
ALTER TABLE plan_ruta ALTER COLUMN fecha SET DEFAULT fn_hoy();

-- 10. Auditoría de las tablas nuevas (RN30) --------------------------------------------------------
DO $$
DECLARE t text; m text;
BEGIN
  FOR t, m IN
    SELECT * FROM (VALUES
      ('cobertura_zona_dato','cobertura'), ('cobertura_evaluacion','cobertura'), ('capacidad_recurso','capacidad'),
      ('costo_concepto','costos'), ('equilibrio_escenario','punto-equilibrio'), ('surtido_restriccion','surtido'),
      ('surtido_recomendacion','surtido'), ('plan_despacho','rutas')
    ) AS x(tabla, modulo)
  LOOP
    EXECUTE format('CREATE OR REPLACE TRIGGER trg_aud_%1$s AFTER INSERT OR UPDATE OR DELETE ON %1$I '
                   'FOR EACH ROW EXECUTE FUNCTION fn_auditar_cambio(%2$L)', t, m);
  END LOOP;
END $$;

-- 11. Parámetros nuevos (RN40) ------------------------------------------------------------------------
INSERT INTO configuracion (clave, valor, tipo_dato, ambito, unidad, descripcion) VALUES
 ('factor_rodeo_distancia', '1.3', 'numerico', 'global', 'veces', 'La distancia por calle es mayor que la línea recta. Se multiplica la distancia en línea recta por este factor para estimar tiempos y costos de reparto.'),
 ('cob_tiempo_max_min', '30', 'numerico', 'global', 'minutos', 'Promesa de entrega: tiempo máximo desde que sale el repartidor hasta que llega al domicilio.'),
 ('cob_solape_max_pct', '40', 'numerico', 'global', '%', 'Si más de este porcentaje de las zonas de un microhub ya las cubre otro, se avisa de canibalización.'),
 ('cap_factor_pico', '1.35', 'numerico', 'global', 'veces', 'La hora pico recibe este múltiplo del promedio horario de pedidos.'),
 ('cap_distancia_entrega_km', '2.4', 'numerico', 'global', 'km', 'Distancia típica de entrega desde el microhub cuando no se indica otra.'),
 ('dem_ventana_dias', '60', 'entero', 'global', 'días', 'Días de historia que usan por omisión los patrones y las proyecciones de demanda.'),
 ('dem_horizonte_dias', '14', 'entero', 'global', 'días', 'Días a futuro que proyecta la demanda por omisión.'),
 ('dem_backtest_dias', '7', 'entero', 'global', 'días', 'Días finales que se ocultan para medir qué tan bien habría proyectado el modelo.'),
 ('dem_banda_z', '1.28', 'numerico', 'global', 'desviaciones', 'Amplitud de la banda de la proyección (1.28 desviaciones deja afuera 10 % por arriba y 10 % por abajo).'),
 ('dem_penetracion', '0.12', 'numerico', 'global', 'fracción', 'Parte de los hogares de una zona que pide a domicilio en un mes.'),
 ('dem_pedidos_hogar_mes', '2.5', 'numerico', 'global', 'pedidos', 'Pedidos al mes de un hogar que sí usa el servicio.'),
 ('cos_pedidos_mes_ref', '1800', 'entero', 'global', 'pedidos', 'Volumen mensual de referencia (60 al día) para costos unitarios cuando no se indica otro.'),
 ('cos_ticket_ref', '135', 'numerico', 'global', 'MXN', 'Ticket de referencia cuando no se indica otro.'),
 ('peq_margen_seguridad_pct', '15', 'numerico', 'global', '%', 'Un microhub se considera viable si la demanda esperada supera el equilibrio por al menos este porcentaje.'),
 ('sim_dias_defecto', '30', 'entero', 'global', 'días', 'Días que simula una ejecución si no se indican.'),
 ('sim_replicas_defecto', '200', 'entero', 'global', 'réplicas', 'Réplicas aleatorias de cada ejecución si no se indican.'),
 ('sim_ausentismo', '0.05', 'numerico', 'global', 'fracción', 'Probabilidad de que cada operador o repartidor falte un día.'),
 ('sim_variacion_demanda', '0.10', 'numerico', 'global', 'fracción', 'Desviación relativa de la demanda de un día respecto de su promedio, además de la variación natural de contar pedidos.'),
 ('sim_semilla_defecto', '2026', 'entero', 'global', 'semilla', 'Semilla del generador aleatorio cuando no se indica: misma semilla y mismos parámetros dan el mismo resultado.')
ON CONFLICT DO NOTHING;

-- 12. Cómo se justifica y se calibra cada supuesto ----------------------------------------------------
INSERT INTO supuesto_documentado (clave, servicio, origen, justificacion, como_calibrar) VALUES
 ('velocidad_reparto_kmh', 'rutas', 'supuesto', 'Velocidad media de un repartidor en moto o bicicleta dentro de las cuatro colonias, contando semáforos y esquinas. Es un valor típico de reparto urbano, no una medición del equipo.', 'Dividir la distancia del recorrido GPS entre su duración en cada entrega cerrada (servicio de seguimiento: inicio, fin y distancia_km) y promediar.'),
 ('tiempo_servicio_min', 'rutas', 'supuesto', 'Minutos que el repartidor pasa en cada parada: estacionar, entregar, cobrar y confirmar con el cliente.', 'Diferencia entre la llegada al domicilio y el cierre de la entrega en el recorrido GPS.'),
 ('paradas_por_viaje', 'costos', 'supuesto', 'Paradas promedio de una salida cuando los pedidos se agrupan por zona. Reparte el costo del regreso al microhub entre ellas.', 'Promedio de la columna paradas de plan_ruta.'),
 ('max_paradas_repartidor', 'rutas', 'normativo', 'Tope que fija el equipo: con más paradas el pedido llega frío y el cálculo exacto de la ruta deja de ser práctico (el exacto se usa hasta 8 paradas).', 'Se revisa si el tiempo promedio de entrega supera la promesa de cobertura.'),
 ('costo_km_reparto', 'rutas', 'supuesto', 'Combustible, mantenimiento y desgaste por kilómetro de una moto pequeña. Lo usan rutas y cobertura; el servicio de costos tiene su propio concepto «Combustible y desgaste», que arranca con el mismo valor.', 'Gasto real de combustible y mantenimiento entre los kilómetros recorridos del mismo periodo; al corregirlo, corregir también el concepto en costos.'),
 ('costo_base_entrega', 'rutas', 'supuesto', 'Pago fijo por entrega al repartidor; se suma al costo por distancia. Lo usan rutas y cobertura; costos tiene su propio concepto «Pago base al repartidor», que arranca con el mismo valor.', 'Lo que se paga de verdad por entrega en el contrato o en la nómina de repartidores; al corregirlo, corregir también el concepto en costos.'),
 ('picking_pedidos_hora', 'capacidad', 'supuesto', 'Un operador junta unos 10 pedidos por hora (6 minutos por pedido de cinco líneas aproximadamente).', 'Tiempo entre asignado y en_preparacion en historial_estatus, o cronometrar una muestra de pedidos.'),
 ('packing_pedidos_hora', 'capacidad', 'supuesto', 'Un operador empaca unos 20 pedidos por hora (3 minutos por pedido).', 'Cronometrar una muestra de pedidos en el área de empaque.'),
 ('despacho_pedidos_hora', 'capacidad', 'supuesto', 'Un operador despacha unos 30 pedidos por hora (2 minutos: verificar y entregar al repartidor).', 'Tiempo entre listo_en y la salida del repartidor.'),
 ('umbral_utilizacion_estable', 'capacidad', 'supuesto', 'Por debajo de 70 % queda holgura para los picos, que suelen ser de 1.3 a 1.4 veces el promedio.', 'Comparar la utilización por hora con los días en que hubo retrasos o rechazos.'),
 ('umbral_utilizacion_riesgo', 'capacidad', 'supuesto', 'Por encima de 85 % la espera en una fila crece muy rápido (teoría de colas), así que se considera riesgo de saturación.', 'Medir el tiempo de espera de los pedidos contra la utilización de cada día.'),
 ('horas_turno', 'capacidad', 'supuesto', 'El microhub abre 12 horas (8 a 20 h); se toman 10 de trabajo efectivo descontando comida y cierre.', 'Horas realmente trabajadas según la asistencia del personal.'),
 ('dias_operacion_mes', 'punto-equilibrio', 'normativo', 'El microhub opera todos los días del mes.', 'Cambiar si se decide cerrar un día a la semana.'),
 ('tamano_hogar', 'cobertura', 'supuesto', 'Personas por hogar para convertir población en hogares. Se usa 3.6, cercano al promedio nacional; no se ha confirmado para estas cuatro colonias.', 'Tomar el dato del Censo de Población y Vivienda (INEGI) de la AGEB de cada colonia.'),
 ('margen_bruto_default', 'punto-equilibrio', 'supuesto', 'Margen bruto sobre la venta cuando no se conoce el costo del producto. En abarrotes urbanos es de 20 a 35 %.', 'Margen real por producto: servicio de precios, GET /precios/margenes.'),
 ('abc_a_pct', 'surtido', 'normativo', 'Regla de Pareto: los productos que acumulan hasta 80 % del movimiento son clase A.', 'No se calibra; es una convención de clasificación.'),
 ('abc_b_pct', 'surtido', 'normativo', 'Los productos hasta 95 % acumulado son clase B; el resto, clase C.', 'No se calibra; es una convención de clasificación.'),
 ('cobertura_dias_a', 'surtido', 'supuesto', 'Días de existencia que se quiere tener de un producto clase A.', 'Comparar con los quiebres de inventario de los productos A.'),
 ('cobertura_dias_b', 'surtido', 'supuesto', 'Días de existencia que se quiere tener de un producto clase B.', 'Comparar con los quiebres de inventario de los productos B.'),
 ('cobertura_dias_c', 'surtido', 'supuesto', 'Días de existencia que se quiere tener de un producto clase C.', 'Comparar con los quiebres de inventario de los productos C.'),
 ('cobertura_dias_exceso', 'surtido', 'supuesto', 'Con más de 30 días de cobertura el producto se considera con exceso.', 'Revisar con la caducidad y la rotación real.'),
 ('factor_rodeo_distancia', 'cobertura', 'supuesto', 'La distancia por calle es mayor que la línea recta; en una retícula urbana suele ser de 1.2 a 1.5 veces. La regla de cobertura sigue siendo el radio en línea recta (como fn_cubre); el factor solo estima tiempos y costos.', 'Cociente entre la distancia del recorrido GPS y la distancia en línea recta entre el microhub y el domicilio, en entregas cerradas.'),
 ('cob_tiempo_max_min', 'cobertura', 'normativo', 'Promesa de entrega que fija el equipo: llegar en 30 minutos o menos desde que sale el repartidor.', 'Se revisa con el tiempo real de las entregas cerradas.'),
 ('cob_solape_max_pct', 'cobertura', 'supuesto', 'Si más del 40 % de las zonas de un microhub ya las cubre otro, los dos se reparten la misma demanda y se canibalizan.', 'Comparar la demanda de las zonas compartidas antes y después de abrir el segundo microhub.'),
 ('cap_factor_pico', 'capacidad', 'supuesto', 'La hora pico recibe de 1.3 a 1.4 veces el promedio horario.', 'Distribución de pedidos por hora de pedido.creado_en.'),
 ('cap_distancia_entrega_km', 'capacidad', 'supuesto', 'Distancia típica de entrega desde el microhub, ida solamente; es el valor del Escenario A de la retroalimentación.', 'Distancia promedio entre el microhub y los domicilios de las entregas cerradas.'),
 ('dem_ventana_dias', 'demanda', 'supuesto', 'Con 60 días hay ocho semanas completas, suficientes para ver el patrón de cada día de la semana.', 'Probar con otras ventanas y comparar el error del respaldo (backtest).'),
 ('dem_horizonte_dias', 'demanda', 'supuesto', 'Dos semanas: cubre el plazo de reposición y de contratación de personal.', 'Se ajusta al plazo de decisión que se quiera apoyar.'),
 ('dem_backtest_dias', 'demanda', 'supuesto', 'Se ocultan los últimos 7 días para medir el error del modelo contra lo que de verdad pasó.', 'Ninguna; es el tamaño de la prueba.'),
 ('dem_banda_z', 'demanda', 'supuesto', 'Con 1.28 desviaciones, la banda deja afuera 10 % por arriba y 10 % por abajo si los errores se reparten como una campana.', 'Revisar qué porcentaje de los días reales cae dentro de la banda.'),
 ('dem_penetracion', 'demanda', 'supuesto', 'Parte de los hogares que pide a domicilio en un mes. 12 % es un valor prudente para un servicio de barrio que apenas empieza; no se ha medido.', 'Clientes distintos por mes entre los hogares de la zona.'),
 ('dem_pedidos_hogar_mes', 'demanda', 'supuesto', 'Un hogar que usa el servicio pide unas dos veces y media al mes: la compra grande del súper no se sustituye, pero sí las de reposición.', 'Frecuencia de compra observada (pedidos entre clientes distintos).'),
 ('cos_pedidos_mes_ref', 'costos', 'supuesto', 'Volumen de referencia de 60 pedidos al día para repartir los costos fijos cuando no se indica otro.', 'Pedidos reales por mes del microhub.'),
 ('cos_ticket_ref', 'costos', 'supuesto', 'Ticket de referencia del escenario de la retroalimentación.', 'Ticket promedio real del servicio de demanda.'),
 ('peq_margen_seguridad_pct', 'punto-equilibrio', 'normativo', 'Decisión del equipo: un microhub es viable si la demanda esperada supera el equilibrio por al menos 15 %, como colchón ante la variación diaria.', 'Variación diaria de la demanda observada.'),
 ('sim_dias_defecto', 'simulacion', 'supuesto', 'Un mes de operación: el mismo plazo en que se miden los costos fijos y la utilidad.', 'Ninguna; es el horizonte de la simulación, se cambia según la decisión que se quiera apoyar.'),
 ('sim_replicas_defecto', 'simulacion', 'supuesto', 'Con 200 réplicas el promedio y los percentiles ya no cambian de forma notable entre corridas.', 'Aumentar las réplicas hasta que P10, P50 y P90 se estabilicen.'),
 ('sim_ausentismo', 'simulacion', 'supuesto', 'Cada operador o repartidor falta un día con probabilidad 5 %. No hay registros de asistencia todavía.', 'Faltas reales entre días laborables, cuando exista el registro de asistencia.'),
 ('sim_variacion_demanda', 'simulacion', 'supuesto', 'Un día cualquiera puede desviarse alrededor de 10 % de su promedio (clima, quincena, eventos del barrio), más allá del azar de contar pedidos.', 'Desviación estándar de pedidos reales dividida entre su promedio, por día de la semana.'),
 ('ventana_analisis_dias', 'surtido', 'supuesto', 'Tres meses de ventas para clasificar los productos: suficiente para ver la rotación sin arrastrar temporadas viejas.', 'Probar con 30 y 180 días y ver si cambian las clases A.'),
 ('sim_semilla_defecto', 'simulacion', 'normativo', 'La semilla fija el generador aleatorio: con los mismos parámetros se obtiene exactamente el mismo resultado.', 'Ninguna; cambiarla da otra corrida con la misma distribución, útil para comprobar que el resultado no depende del azar.')
ON CONFLICT (clave) DO UPDATE SET servicio = EXCLUDED.servicio, origen = EXCLUDED.origen, justificacion = EXCLUDED.justificacion,
                                  como_calibrar = EXCLUDED.como_calibrar, actualizado_en = now();

-- 13. Permisos ------------------------------------------------------------------------------------------
INSERT INTO permiso (clave, modulo, accion, descripcion) VALUES
 ('demanda.ver', 'demanda', 'ver', 'Consultar observaciones, patrones y proyecciones de demanda'),
 ('demanda.editar', 'demanda', 'editar', 'Sincronizar la demanda desde pedidos'),
 ('cobertura.ver', 'cobertura', 'ver', 'Consultar y evaluar la cobertura territorial'),
 ('capacidad.ver', 'capacidad', 'ver', 'Consultar y simular la capacidad de los microhubs'),
 ('capacidad.editar', 'capacidad', 'editar', 'Cambiar los recursos (personal) de un microhub'),
 ('rutas.ver', 'rutas', 'ver', 'Consultar planes de ruta'),
 ('rutas.planear', 'rutas', 'planear', 'Proponer, confirmar y ajustar planes de ruta'),
 ('costos.ver', 'costos', 'ver', 'Consultar costos, costos unitarios y rentabilidad'),
 ('costos.editar', 'costos', 'editar', 'Dar de alta y cambiar conceptos de costo'),
 ('equilibrio.ver', 'equilibrio', 'ver', 'Calcular y consultar el punto de equilibrio'),
 ('equilibrio.editar', 'equilibrio', 'editar', 'Guardar y borrar escenarios de equilibrio'),
 ('surtido.ver', 'surtido', 'ver', 'Consultar clasificación ABC, rotación y recomendaciones de surtido'),
 ('surtido.editar', 'surtido', 'editar', 'Guardar recomendaciones y cambiar restricciones de surtido')
ON CONFLICT (clave) DO NOTHING;

-- Una migración reaplicada no restaura permisos que el administrador retiró.
INSERT INTO rol_permiso (rol_id, permiso_id)
SELECT r.id, p.id FROM rol r CROSS JOIN permiso p
 WHERE NOT EXISTS (SELECT 1 FROM web_migracion WHERE clave = 'ola2_v1')
   AND ((r.clave = 'administrador' AND p.clave IN ('demanda.ver','demanda.editar','cobertura.ver','capacidad.ver','capacidad.editar','rutas.ver',
                                                   'rutas.planear','costos.ver','costos.editar','equilibrio.ver','equilibrio.editar','surtido.ver','surtido.editar'))
     OR (r.clave = 'planeador' AND p.clave IN ('demanda.ver','demanda.editar','cobertura.ver','capacidad.ver','capacidad.editar','rutas.ver',
                                               'rutas.planear','costos.ver','costos.editar','equilibrio.ver','equilibrio.editar','surtido.ver','surtido.editar'))
     OR (r.clave IN ('analista', 'supervisor', 'auditor') AND p.clave IN ('demanda.ver','cobertura.ver','capacidad.ver','rutas.ver','costos.ver',
                                                                         'equilibrio.ver','surtido.ver'))
     OR (r.clave = 'operador' AND p.clave IN ('capacidad.ver','rutas.ver','rutas.planear','surtido.ver')))
ON CONFLICT DO NOTHING;

-- 14. Datos de demostración -----------------------------------------------------------------------------------
INSERT INTO cobertura_zona_dato (zona_id, poblacion, fuente)
SELECT z.id, z.poblacion, 'Estimación del equipo (06_planeacion.sql); sustituir por el dato de INEGI de cada colonia'
  FROM zona z WHERE z.poblacion IS NOT NULL
ON CONFLICT DO NOTHING;

INSERT INTO capacidad_recurso (microhub_id, operadores, repartidores, capacidad_fisica)
SELECT m.id, v.operadores, v.repartidores, v.fisica
  FROM microhub m JOIN (VALUES ('MH-01', 3, 3, 150), ('MH-02', 3, 2, 120), ('MH-03', 2, 2, 100), ('MH-04', 2, 2, 110)) AS v(clave, operadores, repartidores, fisica)
    ON v.clave = m.clave
ON CONFLICT DO NOTHING;

-- Costos globales (aplican a todo microhub o candidato)
INSERT INTO costo_concepto (ambito, ambito_id, nombre, categoria, tipo, unidad, monto, fuente, justificacion)
SELECT 'global', NULL, v.nombre, v.categoria, v.tipo, v.unidad, v.monto, 'supuesto', v.justificacion
  FROM (VALUES
    ('Pago base al repartidor', 'transporte', 'variable', 'entrega', 18.00, 'Pago fijo por entrega; mismo valor que el parámetro costo_base_entrega.'),
    ('Combustible y desgaste', 'transporte', 'variable', 'km', 4.50, 'Combustible, mantenimiento y desgaste de una moto pequeña; mismo valor que costo_km_reparto.'),
    ('Empaque por pedido', 'operacion', 'variable', 'pedido', 3.50, 'Bolsa, sello y etiqueta de un pedido de unas cinco líneas. Estimación a confirmar con el proveedor de empaque.'),
    ('Comisión por pago con tarjeta', 'operacion', 'variable', 'pct_venta', 2.90, 'Comisión típica de un cobro con terminal o link de pago. Confirmar con el contrato del procesador.')
  ) AS v(nombre, categoria, tipo, unidad, monto, justificacion)
 WHERE NOT EXISTS (SELECT 1 FROM costo_concepto c WHERE c.ambito = 'global' AND c.nombre = v.nombre);

-- Costos fijos de cada microhub
INSERT INTO costo_concepto (ambito, ambito_id, nombre, categoria, tipo, unidad, monto, fuente, justificacion)
SELECT 'microhub', m.id, v.nombre, v.categoria, 'fijo', 'mes', v.monto, 'supuesto', v.justificacion
  FROM microhub m
  JOIN (VALUES
    ('MH-01', 'Renta del local', 'renta', 18000.00, 'Renta mensual estimada de un local comercial pequeño en el sector; sustituir por el contrato.'),
    ('MH-02', 'Renta del local', 'renta', 15500.00, 'Renta mensual estimada de un local comercial pequeño en el sector; sustituir por el contrato.'),
    ('MH-03', 'Renta del local', 'renta', 14000.00, 'Renta mensual estimada de un local comercial pequeño en el sector; sustituir por el contrato.'),
    ('MH-04', 'Renta del local', 'renta', 12500.00, 'Renta mensual estimada de un local comercial pequeño en el sector; sustituir por el contrato.'),
    ('MH-01', 'Nómina de operadores', 'personal', 42000.00, 'Tres operadores a 14,000 pesos mensuales con prestaciones; cuadra con los recursos de capacidad.'),
    ('MH-02', 'Nómina de operadores', 'personal', 42000.00, 'Tres operadores a 14,000 pesos mensuales con prestaciones; cuadra con los recursos de capacidad.'),
    ('MH-03', 'Nómina de operadores', 'personal', 28000.00, 'Dos operadores a 14,000 pesos mensuales con prestaciones; cuadra con los recursos de capacidad.'),
    ('MH-04', 'Nómina de operadores', 'personal', 28000.00, 'Dos operadores a 14,000 pesos mensuales con prestaciones; cuadra con los recursos de capacidad.'),
    ('MH-01', 'Servicios (luz, agua, internet)', 'servicios', 7000.00, 'Consumo estimado de un local con refrigeración básica.'),
    ('MH-02', 'Servicios (luz, agua, internet)', 'servicios', 6500.00, 'Consumo estimado de un local con refrigeración básica.'),
    ('MH-03', 'Servicios (luz, agua, internet)', 'servicios', 6000.00, 'Consumo estimado de un local con refrigeración básica.'),
    ('MH-04', 'Servicios (luz, agua, internet)', 'servicios', 6000.00, 'Consumo estimado de un local con refrigeración básica.'),
    ('MH-01', 'Mantenimiento y seguros', 'otros', 2500.00, 'Seguro del local y mantenimiento menor; estimación a confirmar con la aseguradora.'),
    ('MH-02', 'Mantenimiento y seguros', 'otros', 2500.00, 'Seguro del local y mantenimiento menor; estimación a confirmar con la aseguradora.'),
    ('MH-03', 'Mantenimiento y seguros', 'otros', 2000.00, 'Seguro del local y mantenimiento menor; estimación a confirmar con la aseguradora.'),
    ('MH-04', 'Mantenimiento y seguros', 'otros', 2000.00, 'Seguro del local y mantenimiento menor; estimación a confirmar con la aseguradora.')
  ) AS v(clave, nombre, categoria, monto, justificacion) ON v.clave = m.clave
 WHERE NOT EXISTS (SELECT 1 FROM costo_concepto c WHERE c.ambito = 'microhub' AND c.ambito_id = m.id AND c.nombre = v.nombre);

INSERT INTO surtido_restriccion (microhub_id, espacio_total, presupuesto)
SELECT m.id, v.espacio, v.presupuesto
  FROM microhub m JOIN (VALUES ('MH-01', 3600, 120000), ('MH-02', 3000, 100000), ('MH-03', 3200, 100000), ('MH-04', 2800, 90000)) AS v(clave, espacio, presupuesto)
    ON v.clave = m.clave
ON CONFLICT DO NOTHING;

INSERT INTO surtido_producto_param (producto_id, espacio_unidades)
SELECT id, espacio_unidades FROM producto
ON CONFLICT DO NOTHING;

-- Historia de demanda de DEMOSTRACIÓN: 60 días, determinista (sin random), con patrón semanal y tendencia suave.
-- Son datos sintéticos (fuente = 'sintetica'); no son ventas reales y se sustituyen al sincronizar con pedidos.
INSERT INTO demanda_observacion (fecha, zona_id, categoria_id, pedidos, unidades, venta, clientes, no_atendidos, fuente)
SELECT t.fecha, t.zona_id, NULL, t.pedidos,
       round(t.pedidos * 5.2)::int,
       round(t.pedidos * (135 + 8 * sin(t.n * 0.9 + t.zona_id))::numeric, 2),
       round(t.pedidos * 0.85)::int, round(t.pedidos * 0.06)::int, 'sintetica'
  FROM (SELECT d.n, fn_hoy() - d.n AS fecha, z.id AS zona_id,
               GREATEST(1, round(COALESCE(z.poblacion, 4000) * 0.0018
                 * (CASE extract(isodow FROM fn_hoy() - d.n) WHEN 1 THEN 0.90 WHEN 2 THEN 0.85 WHEN 3 THEN 0.90 WHEN 4 THEN 0.95
                                                              WHEN 5 THEN 1.15 WHEN 6 THEN 1.30 ELSE 1.03 END)
                 * (1 + 0.003 * (60 - d.n)) * (1 + 0.08 * sin(d.n * 1.7 + z.id)))::int) AS pedidos
          FROM zona z CROSS JOIN generate_series(1, 60) AS d(n) WHERE z.estatus = 'activo') t
ON CONFLICT DO NOTHING;

INSERT INTO demanda_observacion (fecha, zona_id, categoria_id, pedidos, unidades, venta, fuente)
SELECT o.fecha, o.zona_id, c.id,
       LEAST(o.pedidos, GREATEST(1, round(o.pedidos * LEAST(1, 2.2 * s.parte))::int)),
       round(o.unidades * s.parte)::int, round(o.venta * s.parte, 2), 'sintetica'
  FROM demanda_observacion o
  JOIN categoria c ON true
  JOIN (VALUES ('Abarrote básico', 0.45), ('Bebidas', 0.20), ('Lácteos y huevo', 0.15), ('Limpieza del hogar', 0.12), ('Higiene personal', 0.08)) AS s(nombre, parte)
    ON s.nombre = c.nombre
 WHERE o.categoria_id IS NULL AND o.fuente = 'sintetica'
ON CONFLICT DO NOTHING;

INSERT INTO web_migracion (clave) VALUES ('ola2_v1') ON CONFLICT DO NOTHING;
COMMIT;
