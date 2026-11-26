-- 11_ola3_observabilidad.sql · Entrega final · Ola 3 (auditoría, monitoreo, reportes y sincronización)
-- Codex Innovations · Equipo 04
--
-- Idempotente: se puede aplicar sobre una base existente cuantas veces se quiera
-- (servicios/migrar.py lo hace al levantar docker-compose.integrado.yml).
--
-- Servicios que usan estas tablas (cada una tiene un solo dueño):
--   auditoria-monitoreo (5126)  monitoreo_verificacion, monitoreo_alerta  (y consulta la bitácora `auditoria`, que ya existía)
--   reportes            (5123)  reporte_exportacion
--   sincronizacion      (5125)  sync_lote, sync_operacion
-- Acción de bitácora para la entrega de un enlace firmado de descarga (servicio de documentos). Va fuera de la transacción.
ALTER TYPE microhubs.accion_auditoria ADD VALUE IF NOT EXISTS 'descarga';

BEGIN;
SET LOCAL search_path TO microhubs, public;

-- 1. Monitoreo ------------------------------------------------------------------------------------------
-- Una fila por servicio y por ronda de verificación. Es la serie de tiempo de la que salen la disponibilidad,
-- los tiempos de respuesta y el historial del panel. Se purga según mon_retencion_dias.
CREATE TABLE IF NOT EXISTS monitoreo_verificacion (
    id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    servicio      varchar(30)  NOT NULL,
    verificado_en timestamptz  NOT NULL DEFAULT now(),
    estado        varchar(10)  NOT NULL,
    http_status   smallint,
    tiempo_ms     numeric(9,1) NOT NULL,
    version       varchar(40),
    dependencias  json,
    error         varchar(200),
    CONSTRAINT ck_mv_estado CHECK (estado IN ('ok', 'degradado', 'caido')),
    CONSTRAINT ck_mv_tiempo CHECK (tiempo_ms >= 0)
);
CREATE INDEX IF NOT EXISTS ix_mv_servicio_fecha ON monitoreo_verificacion (servicio, verificado_en DESC);
CREATE INDEX IF NOT EXISTS ix_mv_fecha ON monitoreo_verificacion (verificado_en DESC);
COMMENT ON COLUMN monitoreo_verificacion.estado IS 'ok = responde y todas sus dependencias están bien; degradado = responde pero una dependencia falla (503 con cuerpo); caido = no responde.';

-- Alertas: una abierta por servicio y tipo. Se abren y se cierran solas según la verificación; una persona puede reconocerlas.
CREATE TABLE IF NOT EXISTS monitoreo_alerta (
    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    servicio       varchar(30)  NOT NULL,
    tipo           varchar(20)  NOT NULL,
    severidad      varchar(10)  NOT NULL,
    detalle        varchar(300) NOT NULL,
    abierta_en     timestamptz  NOT NULL DEFAULT now(),
    cerrada_en     timestamptz,
    reconocida_por integer REFERENCES usuario (id),
    reconocida_en  timestamptz,
    CONSTRAINT ck_ma_tipo CHECK (tipo IN ('servicio_caido', 'servicio_degradado', 'dependencia_caida', 'latencia_alta', 'errores_altos')),
    CONSTRAINT ck_ma_severidad CHECK (severidad IN ('critica', 'alta', 'media')),
    CONSTRAINT ck_ma_cierre CHECK (cerrada_en IS NULL OR cerrada_en >= abierta_en)
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_ma_abierta ON monitoreo_alerta (servicio, tipo) WHERE cerrada_en IS NULL;
CREATE INDEX IF NOT EXISTS ix_ma_fecha ON monitoreo_alerta (abierta_en DESC);

DO $$
BEGIN
  EXECUTE 'CREATE OR REPLACE TRIGGER trg_aud_monitoreo_alerta AFTER INSERT OR UPDATE OR DELETE ON monitoreo_alerta '
          'FOR EACH ROW EXECUTE FUNCTION fn_auditar_cambio(''monitoreo'')';
END $$;

-- 2. Reportes -------------------------------------------------------------------------------------------
-- Bitácora de lo que se exportó (quién, qué reporte, con qué filtros, en qué formato y con qué huella). El archivo
-- exportado se genera al momento y se entrega en la respuesta: no se guarda en la base de datos.
CREATE TABLE IF NOT EXISTS reporte_exportacion (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    reporte     varchar(30)  NOT NULL,
    formato     varchar(5)   NOT NULL,
    filtros     json         NOT NULL,
    filas       integer      NOT NULL,
    bytes       integer      NOT NULL,
    sha256      char(64)     NOT NULL,
    creado_por  integer      REFERENCES usuario (id),
    creado_en   timestamptz  NOT NULL DEFAULT now(),
    CONSTRAINT ck_re_formato CHECK (formato IN ('csv', 'xlsx', 'pdf', 'json')),
    CONSTRAINT ck_re_valores CHECK (filas >= 0 AND bytes >= 0)
);
CREATE INDEX IF NOT EXISTS ix_re_fecha ON reporte_exportacion (creado_en DESC);

-- 3. Sincronización -------------------------------------------------------------------------------------
-- Un lote es lo que una app (Android o escritorio) manda al volver a tener red; cada operación lleva el uuid con el que
-- la app la creó sin conexión. (dispositivo, operacion_uuid) único = idempotencia: reenviar un lote no duplica nada.
CREATE TABLE IF NOT EXISTS sync_lote (
    id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lote_uuid     varchar(80)  NOT NULL,
    dispositivo   varchar(60)  NOT NULL,
    cliente       varchar(12)  NOT NULL,
    usuario_id    integer      NOT NULL REFERENCES usuario (id),
    recibido_en   timestamptz  NOT NULL DEFAULT now(),
    total         integer      NOT NULL,
    aplicadas     integer      NOT NULL DEFAULT 0,
    duplicadas    integer      NOT NULL DEFAULT 0,
    conflictos    integer      NOT NULL DEFAULT 0,
    rechazadas    integer      NOT NULL DEFAULT 0,
    CONSTRAINT uq_sync_lote UNIQUE (dispositivo, lote_uuid),
    CONSTRAINT ck_sl_cliente CHECK (cliente IN ('android', 'escritorio', 'web'))
);
CREATE TABLE IF NOT EXISTS sync_operacion (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lote_id         bigint       NOT NULL REFERENCES sync_lote (id),
    dispositivo     varchar(60)  NOT NULL,
    operacion_uuid  varchar(80)  NOT NULL,
    tipo            varchar(30)  NOT NULL,
    creada_en       timestamptz  NOT NULL,
    estado          varchar(10)  NOT NULL,
    codigo          varchar(30),
    mensaje         varchar(300),
    resultado       json,
    huella          char(64)     NOT NULL,
    intentos        smallint     NOT NULL DEFAULT 1,
    procesada_en    timestamptz  NOT NULL DEFAULT now(),
    CONSTRAINT uq_sync_op UNIQUE (dispositivo, operacion_uuid),
    CONSTRAINT ck_so_estado CHECK (estado IN ('aplicada', 'conflicto', 'rechazada', 'pendiente'))
);
-- Para una base que ya tenía la tabla sin la huella (SHA-256 de tipo, datos y fecha: detecta un uuid reutilizado con otro contenido).
ALTER TABLE sync_operacion ADD COLUMN IF NOT EXISTS huella char(64);
CREATE INDEX IF NOT EXISTS ix_so_lote ON sync_operacion (lote_id);
CREATE INDEX IF NOT EXISTS ix_so_estado ON sync_operacion (estado, procesada_en DESC);

-- 4. Parámetros (RN40) ----------------------------------------------------------------------------------
INSERT INTO configuracion (clave, valor, tipo_dato, ambito, unidad, descripcion) VALUES
 ('mon_intervalo_seg', '30', 'entero', 'global', 'segundos', 'Cada cuánto el servicio de monitoreo pregunta la salud de todos los servicios.'),
 ('mon_timeout_seg', '3', 'numerico', 'global', 'segundos', 'Cuánto espera la respuesta de /salud antes de dar al servicio por caído.'),
 ('mon_latencia_ms', '1000', 'entero', 'global', 'ms', 'Un servicio que tarda más de esto en responder /salud genera una alerta de latencia.'),
 ('mon_errores_pct', '20', 'numerico', 'global', '%', 'Si más de este porcentaje de las peticiones de un servicio terminan en error 5xx en la ventana, se alerta.'),
 ('mon_errores_ventana_min', '10', 'entero', 'global', 'minutos', 'Ventana en la que se cuentan las peticiones para el porcentaje de errores.'),
 ('mon_errores_min_peticiones', '20', 'entero', 'global', 'peticiones', 'Con menos peticiones que esto en la ventana no se calcula el porcentaje de errores (un solo error sería 100 %).'),
 ('mon_retencion_dias', '7', 'entero', 'global', 'días', 'Días que se conservan las verificaciones; las más antiguas se borran.'),
 ('mon_disponibilidad_objetivo_pct', '99', 'numerico', 'global', '%', 'Objetivo de disponibilidad; el panel marca en rojo al servicio que queda por debajo.'),
 ('rep_filas_max', '50000', 'entero', 'global', 'filas', 'Máximo de filas que se exporta en un reporte; con más se pide acotar por zona o periodo.'),
 ('rep_periodo_dias', '30', 'entero', 'global', 'días', 'Periodo de un reporte cuando no se indican fechas.'),
 ('sync_lote_max', '200', 'entero', 'global', 'operaciones', 'Máximo de operaciones en un lote de sincronización.'),
 ('sync_antiguedad_max_dias', '14', 'entero', 'global', 'días', 'Una operación creada sin conexión hace más días que esto se rechaza: el dato ya no es confiable.'),
 ('sync_reloj_tolerancia_min', '10', 'entero', 'global', 'minutos', 'Cuánto puede adelantarse el reloj del dispositivo respecto del servidor antes de rechazar la operación.')
ON CONFLICT DO NOTHING;

INSERT INTO supuesto_documentado (clave, servicio, origen, justificacion, como_calibrar) VALUES
 ('mon_intervalo_seg', 'auditoria-monitoreo', 'supuesto', '30 segundos detecta una caída en menos de un minuto y genera unas 2 880 verificaciones al día por servicio, que PostgreSQL absorbe sin problema.', 'Subirlo si el panel carga demasiado la base; bajarlo si se exige detectar caídas en menos de medio minuto.'),
 ('mon_timeout_seg', 'auditoria-monitoreo', 'supuesto', '3 segundos es más de lo que tarda un /salud sano; un servicio que no contesta en ese tiempo ya no atiende a nadie en la práctica.', 'Subirlo si hay falsos «caído» por picos de carga; bajarlo para detectar antes.'),
 ('mon_errores_ventana_min', 'auditoria-monitoreo', 'supuesto', '10 minutos son suficientes peticiones para distinguir una falla de un error aislado sin tardar en avisar.', 'Alargarla si el tráfico es muy bajo; acortarla si se quiere avisar más rápido.'),
 ('mon_errores_min_peticiones', 'auditoria-monitoreo', 'supuesto', 'Con menos de 20 peticiones un solo error ya sería 5 % o más; se exige una muestra mínima para no alertar por casualidad.', 'Ajustar al tráfico real: debe ser una fracción pequeña de lo que recibe un servicio en la ventana.'),
 ('mon_retencion_dias', 'auditoria-monitoreo', 'supuesto', 'Una semana alcanza para ver tendencias y revisar un incidente reciente; a 30 s por servicio son unas 600 mil filas por semana.', 'Alargarla si se exige historial más largo y el volumen de la base lo permite.'),
 ('mon_latencia_ms', 'auditoria-monitoreo', 'supuesto', 'Un /salud sano responde en decenas de milisegundos; 1 s ya indica saturación de alguna dependencia.', 'Tomar el p95 de tiempo_ms de monitoreo_verificacion en una semana normal y poner el umbral al doble.'),
 ('mon_errores_pct', 'auditoria-monitoreo', 'supuesto', '20 % de errores del servidor en 10 minutos es una falla clara y no un error aislado.', 'Revisar las alertas falsas del primer mes y ajustar.'),
 ('mon_disponibilidad_objetivo_pct', 'auditoria-monitoreo', 'normativo', '99 % es el objetivo razonable para una VM única sin alta disponibilidad (unas 7 horas de caída al mes).', 'Cambiar si el acuerdo de servicio con el cliente pide otro valor.'),
 ('sync_lote_max', 'sincronizacion', 'supuesto', 'Un lote de 200 operaciones cabe en una petición de menos de 1 MB y se aplica en pocos segundos; un teléfono que estuvo días sin red rara vez junta más.', 'Medir cuántas operaciones junta un repartidor en una jornada sin conexión y poner el límite al doble.'),
 ('rep_filas_max', 'reportes', 'supuesto', 'Un reporte de 50 000 filas todavía se arma y se exporta en segundos; más allá conviene acotar por zona o periodo.', 'Medir el tiempo de armado y de exportación con el volumen real y bajar el límite si pasa de unos 10 segundos.'),
 ('rep_periodo_dias', 'reportes', 'normativo', '30 días es el periodo de cierre que usa la operación para comparar microhubs.', 'Cambiarlo si el corte de la operación es otro.'),
 ('sync_antiguedad_max_dias', 'sincronizacion', 'supuesto', 'Un repartidor sin red por dos semanas ya no tiene datos vigentes: precios, inventario y pedidos habrán cambiado.', 'Medir cuántos días pasan realmente sin conexión en la operación.'),
 ('sync_reloj_tolerancia_min', 'sincronizacion', 'supuesto', 'Los relojes de los teléfonos se desvían minutos; una operación fechada en el futuro lejano es un reloj mal puesto o un intento de manipulación.', 'Comparar la hora de creación de las operaciones con la hora de recepción.')
ON CONFLICT (clave) DO UPDATE SET servicio = EXCLUDED.servicio, origen = EXCLUDED.origen, justificacion = EXCLUDED.justificacion,
                                  como_calibrar = EXCLUDED.como_calibrar, actualizado_en = now();

-- 5. Permisos ----------------------------------------------------------------------------------------------
INSERT INTO permiso (clave, modulo, accion, descripcion) VALUES
 ('auditoria.ver', 'auditoria', 'ver', 'Consultar la bitácora de auditoría, los accesos y la trazabilidad de pedidos, entregas e inventario'),
 ('monitoreo.ver', 'monitoreo', 'ver', 'Ver el estado, el historial de disponibilidad y las alertas de los servicios'),
 ('monitoreo.operar', 'monitoreo', 'operar', 'Forzar una verificación y reconocer alertas'),
 ('reportes.ver', 'reportes', 'ver', 'Consultar y exportar reportes operativos, logísticos, comerciales y financieros'),
 ('sincronizacion.usar', 'sincronizacion', 'usar', 'Enviar lotes de operaciones hechas sin conexión y ver su estado'),
 ('sincronizacion.ver', 'sincronizacion', 'ver', 'Ver todos los lotes y conflictos de sincronización')
ON CONFLICT (clave) DO NOTHING;

-- Una migración reaplicada no restaura permisos que el administrador retiró.
INSERT INTO rol_permiso (rol_id, permiso_id)
SELECT r.id, p.id FROM rol r CROSS JOIN permiso p
 WHERE NOT EXISTS (SELECT 1 FROM web_migracion WHERE clave = 'ola3_v1')
   AND ((r.clave = 'administrador' AND p.clave IN ('auditoria.ver','monitoreo.ver','monitoreo.operar','reportes.ver','sincronizacion.usar','sincronizacion.ver'))
     OR (r.clave = 'auditor' AND p.clave IN ('auditoria.ver','monitoreo.ver','reportes.ver','sincronizacion.ver'))
     OR (r.clave IN ('planeador', 'analista') AND p.clave IN ('monitoreo.ver','reportes.ver'))
     OR (r.clave = 'supervisor' AND p.clave IN ('monitoreo.ver','reportes.ver','sincronizacion.usar','sincronizacion.ver'))
     OR (r.clave IN ('operador', 'repartidor') AND p.clave IN ('sincronizacion.usar')))
ON CONFLICT DO NOTHING;

INSERT INTO web_migracion (clave) VALUES ('ola3_v1') ON CONFLICT DO NOTHING;
COMMIT;
