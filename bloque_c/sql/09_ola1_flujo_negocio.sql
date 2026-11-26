-- 09_ola1_flujo_negocio.sql · Tercer avance · Ola 1 (flujo de negocio)
-- Codex Innovations · Equipo 04
--
-- Idempotente: se puede aplicar sobre una base existente cuantas veces se
-- quiera (servicios/migrar.py lo hace al levantar docker-compose.integrado.yml).
-- No borra datos ni retira permisos.
--
-- Servicios que usan estas tablas (cada una tiene un solo dueño):
--   inventario     (5111)  inventario, movimiento_inventario, inventario_reserva
--   precios        (5112)  lista_precio, lista_precio_item, lista_precio_historico, promocion
--   proveedores    (5113)  proveedor, proveedor_zona, proveedor_producto, proveedor_evaluacion
--   abastecimiento (5114)  solicitud_compra(+linea), orden_compra(+linea), orden_compra_recepcion
--   notificaciones (5124)  web_notificacion, notificacion_preferencia

-- Valores nuevos del tipo de movimiento. Se agregan fuera de la transacción
-- principal porque un valor nuevo no se puede usar en la transacción que lo crea.
ALTER TYPE microhubs.tipo_movimiento ADD VALUE IF NOT EXISTS 'transferencia_salida';
ALTER TYPE microhubs.tipo_movimiento ADD VALUE IF NOT EXISTS 'transferencia_entrada';

BEGIN;
SET LOCAL search_path TO microhubs, public;

-- 0. La fecha de hoy es la de Monterrey. PostgreSQL trabaja en UTC y current_date ya es «mañana» desde las 6 de la
--    tarde; una lista de precios sembrada con esa fecha no regiría hoy.
CREATE OR REPLACE FUNCTION fn_hoy() RETURNS date
LANGUAGE sql STABLE AS $$ SELECT (now() AT TIME ZONE 'America/Monterrey')::date $$;

-- 1. Inventario ---------------------------------------------------------------
-- Llave de idempotencia: un reintento con el mismo valor no repite el movimiento.
ALTER TABLE movimiento_inventario ADD COLUMN IF NOT EXISTS operacion_uuid varchar(80);
CREATE UNIQUE INDEX IF NOT EXISTS uq_mov_operacion_uuid
    ON movimiento_inventario (operacion_uuid) WHERE operacion_uuid IS NOT NULL;

CREATE TABLE IF NOT EXISTS inventario_reserva (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    microhub_id     integer      NOT NULL,
    producto_id     integer      NOT NULL,
    cantidad        integer      NOT NULL,
    estado          varchar(10)  NOT NULL DEFAULT 'activa',
    referencia_tipo varchar(30)  NOT NULL,
    referencia_id   varchar(40)  NOT NULL,
    creada_por      integer      REFERENCES usuario (id),
    creada_en       timestamptz  NOT NULL DEFAULT now(),
    vence_en        timestamptz  NOT NULL,
    cerrada_en      timestamptz,
    CONSTRAINT fk_reserva_inventario FOREIGN KEY (microhub_id, producto_id)
        REFERENCES inventario (microhub_id, producto_id),
    CONSTRAINT ck_reserva_cantidad CHECK (cantidad > 0),
    CONSTRAINT ck_reserva_estado   CHECK (estado IN ('activa', 'liberada', 'consumida')),
    CONSTRAINT ck_reserva_cierre   CHECK ((estado = 'activa') = (cerrada_en IS NULL))
);
CREATE INDEX IF NOT EXISTS ix_reserva_activa
    ON inventario_reserva (microhub_id, producto_id) WHERE estado = 'activa';
CREATE INDEX IF NOT EXISTS ix_reserva_referencia
    ON inventario_reserva (referencia_tipo, referencia_id);
COMMENT ON TABLE inventario_reserva IS
    'Existencia apartada para una referencia (pedido, transferencia). Una reserva activa y vigente resta de la existencia disponible, no de la existencia física.';

-- Existencia física, apartada y disponible. Solo cuentan las reservas activas y vigentes.
CREATE OR REPLACE VIEW v_inventario_disponible AS
SELECT i.microhub_id, i.producto_id, i.existencia, i.minimo,
       COALESCE(r.reservado, 0)::integer                      AS reservado,
       (i.existencia - COALESCE(r.reservado, 0))::integer     AS disponible,
       i.actualizado_en
  FROM inventario i
  LEFT JOIN (SELECT microhub_id, producto_id, sum(cantidad) AS reservado
               FROM inventario_reserva
              WHERE estado = 'activa' AND vence_en > now()
              GROUP BY microhub_id, producto_id) r
         USING (microhub_id, producto_id);

-- Un pedido asignado consume su reserva (la asignación ya descontó la existencia);
-- un pedido cancelado la libera.
CREATE OR REPLACE FUNCTION fn_reserva_segun_pedido() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.estado IS DISTINCT FROM OLD.estado THEN
    IF NEW.estado = 'asignado' THEN
      UPDATE inventario_reserva SET estado = 'consumida', cerrada_en = now()
       WHERE estado = 'activa' AND referencia_tipo = 'pedido' AND referencia_id = NEW.id::text;
    ELSIF NEW.estado = 'cancelado' THEN
      UPDATE inventario_reserva SET estado = 'liberada', cerrada_en = now()
       WHERE estado = 'activa' AND referencia_tipo = 'pedido' AND referencia_id = NEW.id::text;
    END IF;
  END IF;
  RETURN NEW;
END $$;
CREATE OR REPLACE TRIGGER trg_reserva_segun_pedido
  AFTER UPDATE OF estado ON pedido FOR EACH ROW EXECUTE FUNCTION fn_reserva_segun_pedido();

-- 2. Notificaciones --------------------------------------------------------------
ALTER TABLE web_notificacion ALTER COLUMN tipo TYPE varchar(20);
ALTER TABLE web_notificacion ALTER COLUMN referencia_tipo TYPE varchar(20);
ALTER TABLE web_notificacion DROP CONSTRAINT IF EXISTS ck_notif_tipo;
ALTER TABLE web_notificacion ADD CONSTRAINT ck_notif_tipo
    CHECK (tipo IN ('pedido', 'entrega', 'sistema', 'planeacion', 'inventario', 'abastecimiento'));
ALTER TABLE web_notificacion DROP CONSTRAINT IF EXISTS ck_notif_referencia;
ALTER TABLE web_notificacion ADD CONSTRAINT ck_notif_referencia
    CHECK ((referencia_tipo IS NULL AND referencia_id IS NULL) OR
           (referencia_tipo IN ('pedido', 'entrega', 'candidato', 'sistema', 'producto', 'solicitud', 'orden')
            AND referencia_id IS NOT NULL));

CREATE TABLE IF NOT EXISTS notificacion_preferencia (
    usuario_id     integer     NOT NULL REFERENCES usuario (id),
    tipo           varchar(20) NOT NULL,
    activa         boolean     NOT NULL DEFAULT true,
    actualizada_en timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (usuario_id, tipo),
    CONSTRAINT ck_pref_tipo CHECK (tipo IN ('pedido', 'entrega', 'planeacion', 'inventario', 'abastecimiento'))
);
COMMENT ON TABLE notificacion_preferencia IS
    'Tipos de aviso que una persona decidió no recibir. Sin fila, el tipo está activo. Los avisos del sistema no se pueden apagar.';

CREATE OR REPLACE FUNCTION fn_notif_activa(p_usuario integer, p_tipo text) RETURNS boolean
LANGUAGE sql STABLE AS $$
  SELECT COALESCE((SELECT activa FROM notificacion_preferencia
                    WHERE usuario_id = p_usuario AND tipo = p_tipo), true);
$$;

-- Los avisos que ya generaba el motor ahora respetan las preferencias.
CREATE OR REPLACE FUNCTION fn_web_notificar_cierre() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.estado IS DISTINCT FROM OLD.estado AND NEW.estado IN ('entregado','entrega_parcial','entrega_fallida','cancelado') THEN
    INSERT INTO web_notificacion(destinatario_id, emisor_id, titulo, mensaje, tipo, referencia_tipo, referencia_id)
    SELECT c.usuario_id, ctx_usuario_id(), 'Pedido ' || NEW.folio,
           'El pedido cambió a ' || NEW.estado::text || '.', 'pedido', 'pedido', NEW.id::text
      FROM cliente c WHERE c.id = NEW.cliente_id AND fn_notif_activa(c.usuario_id, 'pedido');
  END IF;
  RETURN NEW;
END $$;

CREATE OR REPLACE FUNCTION fn_notificar_asignacion() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE v_folio varchar;
BEGIN
  IF NEW.repartidor_id IS NOT NULL AND NEW.cierre_en IS NULL
     AND (TG_OP = 'INSERT' OR NEW.repartidor_id IS DISTINCT FROM OLD.repartidor_id)
     AND fn_notif_activa(NEW.repartidor_id, 'entrega') THEN
    SELECT folio INTO v_folio FROM pedido WHERE id = NEW.pedido_id;
    INSERT INTO web_notificacion(destinatario_id, emisor_id, titulo, mensaje, tipo, referencia_tipo, referencia_id)
    VALUES (NEW.repartidor_id, ctx_usuario_id(), 'Nueva entrega asignada',
            'Se te asignó el pedido ' || v_folio ||
            COALESCE(' (parada ' || NEW.orden_parada || ')', '') || '.',
            'entrega', 'entrega', NEW.id::text);
  END IF;
  RETURN NEW;
END $$;

-- Aviso de faltante: la existencia cruza el mínimo hacia abajo.
CREATE OR REPLACE FUNCTION fn_notificar_faltante() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE v_prod text; v_hub text;
BEGIN
  IF NEW.minimo > 0 AND NEW.existencia <= NEW.minimo AND OLD.existencia > OLD.minimo THEN
    SELECT nombre INTO v_prod FROM producto WHERE id = NEW.producto_id;
    SELECT nombre INTO v_hub  FROM microhub WHERE id = NEW.microhub_id;
    INSERT INTO web_notificacion(destinatario_id, emisor_id, titulo, mensaje, tipo, referencia_tipo, referencia_id)
    SELECT u.id, ctx_usuario_id(), left('Faltante en ' || v_hub, 120),
           v_prod || ': quedan ' || NEW.existencia || ' (mínimo ' || NEW.minimo || ').',
           'inventario', 'producto', NEW.producto_id::text
      FROM usuario u JOIN rol r ON r.id = u.rol_id
     WHERE u.estatus = 'activo'
       AND ((r.clave = 'operador' AND u.microhub_id = NEW.microhub_id) OR r.clave = 'administrador')
       AND fn_notif_activa(u.id, 'inventario');
  END IF;
  RETURN NEW;
END $$;
CREATE OR REPLACE TRIGGER trg_notificar_faltante
  AFTER UPDATE OF existencia ON inventario FOR EACH ROW EXECUTE FUNCTION fn_notificar_faltante();

-- 3. Precios ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lista_precio (
    id             integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre         varchar(80)  NOT NULL,
    zona_id        integer      REFERENCES zona (id),
    vigente_desde  date         NOT NULL DEFAULT fn_hoy(),
    vigente_hasta  date,
    estatus        estatus_registro NOT NULL DEFAULT 'activo',
    creada_por     integer      REFERENCES usuario (id),
    creada_en      timestamptz  NOT NULL DEFAULT now(),
    CONSTRAINT uq_lista_precio_nombre UNIQUE (nombre),
    CONSTRAINT ck_lista_vigencia CHECK (vigente_hasta IS NULL OR vigente_hasta >= vigente_desde)
);
COMMENT ON COLUMN lista_precio.zona_id IS 'NULL = lista general. Una zona no puede tener dos listas activas con vigencias que se traslapen (lo valida el servicio).';

CREATE TABLE IF NOT EXISTS lista_precio_item (
    lista_id       integer       NOT NULL REFERENCES lista_precio (id),
    producto_id    integer       NOT NULL,
    precio         numeric(10,2) NOT NULL,
    costo          numeric(10,2),
    actualizado_en timestamptz   NOT NULL DEFAULT now(),
    actualizado_por integer      REFERENCES usuario (id),
    PRIMARY KEY (lista_id, producto_id),
    CONSTRAINT fk_lpi_producto FOREIGN KEY (producto_id) REFERENCES producto (id),
    CONSTRAINT ck_lpi_precio CHECK (precio > 0),
    CONSTRAINT ck_lpi_costo  CHECK (costo IS NULL OR costo >= 0)
);

CREATE TABLE IF NOT EXISTS lista_precio_historico (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lista_id        integer       NOT NULL REFERENCES lista_precio (id),
    producto_id     integer       NOT NULL,
    precio_anterior numeric(10,2),
    precio_nuevo    numeric(10,2) NOT NULL,
    usuario_id      integer       REFERENCES usuario (id),
    fecha           timestamptz   NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_lph_producto ON lista_precio_historico (producto_id, fecha DESC);
CREATE INDEX IF NOT EXISTS ix_lph_lista    ON lista_precio_historico (lista_id, fecha DESC);

CREATE OR REPLACE FUNCTION fn_historia_lista_precio() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF TG_OP = 'INSERT' OR NEW.precio IS DISTINCT FROM OLD.precio THEN
    INSERT INTO lista_precio_historico(lista_id, producto_id, precio_anterior, precio_nuevo, usuario_id)
    VALUES (NEW.lista_id, NEW.producto_id, CASE WHEN TG_OP = 'UPDATE' THEN OLD.precio END, NEW.precio, ctx_usuario_id());
  END IF;
  RETURN NEW;
END $$;
CREATE OR REPLACE TRIGGER trg_historia_lista_precio
  AFTER INSERT OR UPDATE ON lista_precio_item FOR EACH ROW EXECUTE FUNCTION fn_historia_lista_precio();

CREATE TABLE IF NOT EXISTS promocion (
    id             integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre         varchar(80)   NOT NULL,
    tipo           varchar(10)   NOT NULL,
    valor          numeric(10,2) NOT NULL,
    producto_id    integer,
    categoria_id   integer,
    zona_id        integer       REFERENCES zona (id),
    vigente_desde  date          NOT NULL DEFAULT fn_hoy(),
    vigente_hasta  date          NOT NULL,
    estatus        estatus_registro NOT NULL DEFAULT 'activo',
    creada_por     integer       REFERENCES usuario (id),
    creada_en      timestamptz   NOT NULL DEFAULT now(),
    CONSTRAINT fk_promo_producto  FOREIGN KEY (producto_id)  REFERENCES producto (id),
    CONSTRAINT fk_promo_categoria FOREIGN KEY (categoria_id) REFERENCES categoria (id),
    CONSTRAINT ck_promo_tipo     CHECK (tipo IN ('porcentaje', 'monto')),
    CONSTRAINT ck_promo_valor    CHECK (valor > 0 AND (tipo = 'monto' OR valor <= 100)),
    CONSTRAINT ck_promo_alcance  CHECK (NOT (producto_id IS NOT NULL AND categoria_id IS NOT NULL)),
    CONSTRAINT ck_promo_vigencia CHECK (vigente_hasta >= vigente_desde)
);
COMMENT ON TABLE promocion IS
    'RN38: el alcance es producto, categoría o zona; nunca una persona. Se aplica una sola promoción por línea: la de mayor descuento.';

-- 4. Proveedores -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS proveedor (
    id               integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    clave            varchar(20)  NOT NULL,
    nombre           varchar(120) NOT NULL,
    contacto         varchar(120),
    correo           varchar(160),
    telefono         varchar(20),
    dias_entrega     smallint     NOT NULL DEFAULT 2,
    pedido_minimo    numeric(10,2) NOT NULL DEFAULT 0,
    condiciones_pago varchar(120),
    estatus          estatus_registro NOT NULL DEFAULT 'activo',
    creado_en        timestamptz  NOT NULL DEFAULT now(),
    actualizado_en   timestamptz  NOT NULL DEFAULT now(),
    CONSTRAINT uq_proveedor_clave UNIQUE (clave),
    CONSTRAINT ck_proveedor_dias   CHECK (dias_entrega BETWEEN 0 AND 60),
    CONSTRAINT ck_proveedor_minimo CHECK (pedido_minimo >= 0),
    CONSTRAINT ck_proveedor_correo CHECK (correo IS NULL OR correo ~ '^[^@[:space:]]+@[^@[:space:]]+\.[a-zA-Z]{2,}$')
);

CREATE TABLE IF NOT EXISTS proveedor_zona (
    proveedor_id integer NOT NULL REFERENCES proveedor (id),
    zona_id      integer NOT NULL,
    PRIMARY KEY (proveedor_id, zona_id),
    CONSTRAINT fk_pz_zona FOREIGN KEY (zona_id) REFERENCES zona (id)
);

CREATE TABLE IF NOT EXISTS proveedor_producto (
    proveedor_id      integer       NOT NULL REFERENCES proveedor (id),
    producto_id       integer       NOT NULL,
    precio_compra     numeric(10,2) NOT NULL,
    unidad_compra     varchar(20)   NOT NULL DEFAULT 'pieza',
    capacidad_semanal integer       NOT NULL,
    minimo_compra     integer       NOT NULL DEFAULT 1,
    vigente_hasta     date,
    actualizado_en    timestamptz   NOT NULL DEFAULT now(),
    PRIMARY KEY (proveedor_id, producto_id),
    CONSTRAINT fk_pp_producto FOREIGN KEY (producto_id) REFERENCES producto (id),
    CONSTRAINT ck_pp_precio    CHECK (precio_compra > 0),
    CONSTRAINT ck_pp_capacidad CHECK (capacidad_semanal > 0),
    CONSTRAINT ck_pp_minimo    CHECK (minimo_compra >= 1)
);
CREATE INDEX IF NOT EXISTS ix_pp_producto ON proveedor_producto (producto_id);

CREATE TABLE IF NOT EXISTS proveedor_evaluacion (
    id           integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    proveedor_id integer     NOT NULL REFERENCES proveedor (id),
    puntualidad  smallint    NOT NULL,
    calidad      smallint    NOT NULL,
    precio       smallint    NOT NULL,
    comentario   varchar(300),
    evaluado_por integer     REFERENCES usuario (id),
    evaluado_en  timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT ck_pe_puntualidad CHECK (puntualidad BETWEEN 1 AND 5),
    CONSTRAINT ck_pe_calidad     CHECK (calidad BETWEEN 1 AND 5),
    CONSTRAINT ck_pe_precio      CHECK (precio BETWEEN 1 AND 5)
);
CREATE INDEX IF NOT EXISTS ix_pe_proveedor ON proveedor_evaluacion (proveedor_id, evaluado_en DESC);

-- 5. Abastecimiento ----------------------------------------------------------------
CREATE SEQUENCE IF NOT EXISTS seq_folio_solicitud;
CREATE SEQUENCE IF NOT EXISTS seq_folio_orden;

CREATE TABLE IF NOT EXISTS solicitud_compra (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    folio           varchar(24) NOT NULL DEFAULT ('SC-' || to_char(now(), 'YYYYMMDD') || '-' ||
                                                  lpad(nextval('seq_folio_solicitud')::text, 6, '0')),
    microhub_id     integer     NOT NULL REFERENCES microhub (id),
    estado          varchar(10) NOT NULL DEFAULT 'pendiente',
    motivo          varchar(300),
    solicitada_por  integer     REFERENCES usuario (id),
    decidida_por    integer     REFERENCES usuario (id),
    decision_motivo varchar(300),
    decidida_en     timestamptz,
    creada_en       timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_solicitud_folio UNIQUE (folio),
    CONSTRAINT ck_solicitud_estado CHECK (estado IN ('pendiente', 'aprobada', 'rechazada', 'ordenada')),
    CONSTRAINT ck_solicitud_rechazo CHECK (estado <> 'rechazada' OR decision_motivo IS NOT NULL)
);
CREATE INDEX IF NOT EXISTS ix_solicitud_hub_estado ON solicitud_compra (microhub_id, estado);

CREATE TABLE IF NOT EXISTS solicitud_compra_linea (
    solicitud_id bigint  NOT NULL REFERENCES solicitud_compra (id),
    producto_id  integer NOT NULL,
    cantidad     integer NOT NULL,
    PRIMARY KEY (solicitud_id, producto_id),
    CONSTRAINT fk_scl_producto FOREIGN KEY (producto_id) REFERENCES producto (id),
    CONSTRAINT ck_scl_cantidad CHECK (cantidad > 0)
);

CREATE TABLE IF NOT EXISTS orden_compra (
    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    folio          varchar(24) NOT NULL DEFAULT ('OC-' || to_char(now(), 'YYYYMMDD') || '-' ||
                                                 lpad(nextval('seq_folio_orden')::text, 6, '0')),
    solicitud_id   bigint      REFERENCES solicitud_compra (id),
    proveedor_id   integer     NOT NULL REFERENCES proveedor (id),
    microhub_id    integer     NOT NULL REFERENCES microhub (id),
    estado         varchar(10) NOT NULL DEFAULT 'emitida',
    fecha_esperada date        NOT NULL,
    total          numeric(12,2) NOT NULL DEFAULT 0,
    motivo_cancelacion varchar(300),
    creada_por     integer     REFERENCES usuario (id),
    creada_en      timestamptz NOT NULL DEFAULT now(),
    cerrada_en     timestamptz,
    CONSTRAINT uq_orden_folio UNIQUE (folio),
    CONSTRAINT ck_orden_estado CHECK (estado IN ('emitida', 'parcial', 'recibida', 'cancelada')),
    CONSTRAINT ck_orden_total  CHECK (total >= 0)
);
CREATE INDEX IF NOT EXISTS ix_orden_hub_estado ON orden_compra (microhub_id, estado);
CREATE INDEX IF NOT EXISTS ix_orden_proveedor  ON orden_compra (proveedor_id, estado);

CREATE TABLE IF NOT EXISTS orden_compra_linea (
    orden_id          bigint        NOT NULL REFERENCES orden_compra (id),
    producto_id       integer       NOT NULL,
    cantidad          integer       NOT NULL,
    precio_compra     numeric(10,2) NOT NULL,
    cantidad_recibida integer       NOT NULL DEFAULT 0,
    PRIMARY KEY (orden_id, producto_id),
    CONSTRAINT fk_ocl_producto FOREIGN KEY (producto_id) REFERENCES producto (id),
    CONSTRAINT ck_ocl_cantidad CHECK (cantidad > 0),
    CONSTRAINT ck_ocl_precio   CHECK (precio_compra > 0),
    CONSTRAINT ck_oc_recibida  CHECK (cantidad_recibida BETWEEN 0 AND cantidad)
);

-- Cada recepción se guarda antes de tocar el inventario; "aplicada" indica que el
-- servicio de inventario ya registró la entrada. operacion_uuid evita duplicarla.
CREATE TABLE IF NOT EXISTS orden_compra_recepcion (
    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    orden_id       bigint      NOT NULL REFERENCES orden_compra (id),
    producto_id    integer     NOT NULL,
    cantidad       integer     NOT NULL,
    operacion_uuid varchar(80) NOT NULL,
    aplicada       boolean     NOT NULL DEFAULT false,
    nota           varchar(300),
    recibido_por   integer     REFERENCES usuario (id),
    recibido_en    timestamptz NOT NULL DEFAULT now(),
    aplicada_en    timestamptz,
    CONSTRAINT uq_recepcion_operacion UNIQUE (operacion_uuid),
    CONSTRAINT fk_ocr_linea FOREIGN KEY (orden_id, producto_id) REFERENCES orden_compra_linea (orden_id, producto_id),
    CONSTRAINT ck_ocr_cantidad CHECK (cantidad > 0)
);
CREATE INDEX IF NOT EXISTS ix_ocr_pendientes ON orden_compra_recepcion (orden_id) WHERE NOT aplicada;

-- Avisos del flujo de abastecimiento (quien lo pide, quien lo aprueba, quien lo recibe).
CREATE OR REPLACE FUNCTION fn_notificar_solicitud() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE v_hub text;
BEGIN
  IF TG_OP = 'INSERT' THEN
    SELECT nombre INTO v_hub FROM microhub WHERE id = NEW.microhub_id;
    INSERT INTO web_notificacion(destinatario_id, emisor_id, titulo, mensaje, tipo, referencia_tipo, referencia_id)
    SELECT u.id, ctx_usuario_id(), 'Solicitud de compra ' || NEW.folio,
           left('El ' || v_hub || ' pidió reabastecimiento.', 400), 'abastecimiento', 'solicitud', NEW.id::text
      FROM usuario u JOIN rol r ON r.id = u.rol_id
     WHERE u.estatus = 'activo' AND r.clave = 'administrador' AND fn_notif_activa(u.id, 'abastecimiento');
  ELSIF NEW.estado IS DISTINCT FROM OLD.estado AND NEW.estado IN ('aprobada', 'rechazada')
        AND NEW.solicitada_por IS NOT NULL AND fn_notif_activa(NEW.solicitada_por, 'abastecimiento') THEN
    INSERT INTO web_notificacion(destinatario_id, emisor_id, titulo, mensaje, tipo, referencia_tipo, referencia_id)
    VALUES (NEW.solicitada_por, ctx_usuario_id(), 'Solicitud de compra ' || NEW.folio,
            'Tu solicitud fue ' || NEW.estado || '.', 'abastecimiento', 'solicitud', NEW.id::text);
  END IF;
  RETURN NEW;
END $$;
CREATE OR REPLACE TRIGGER trg_notificar_solicitud
  AFTER INSERT OR UPDATE OF estado ON solicitud_compra FOR EACH ROW EXECUTE FUNCTION fn_notificar_solicitud();

CREATE OR REPLACE FUNCTION fn_notificar_orden() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.estado IS DISTINCT FROM OLD.estado AND NEW.estado IN ('recibida', 'cancelada') THEN
    INSERT INTO web_notificacion(destinatario_id, emisor_id, titulo, mensaje, tipo, referencia_tipo, referencia_id)
    SELECT u.id, ctx_usuario_id(), 'Orden de compra ' || NEW.folio,
           'La orden quedó ' || NEW.estado || '.', 'abastecimiento', 'orden', NEW.id::text
      FROM usuario u JOIN rol r ON r.id = u.rol_id
     WHERE u.estatus = 'activo' AND fn_notif_activa(u.id, 'abastecimiento')
       AND (u.id = NEW.creada_por OR (r.clave = 'operador' AND u.microhub_id = NEW.microhub_id));
  END IF;
  RETURN NEW;
END $$;
CREATE OR REPLACE TRIGGER trg_notificar_orden
  AFTER UPDATE OF estado ON orden_compra FOR EACH ROW EXECUTE FUNCTION fn_notificar_orden();

-- 6. Auditoría de las tablas nuevas (RN30) -----------------------------------------
DO $$
DECLARE t text; m text;
BEGIN
  FOR t, m IN
    SELECT * FROM (VALUES
      ('inventario_reserva','inventario'),
      ('lista_precio','precios'), ('lista_precio_item','precios'), ('promocion','precios'),
      ('proveedor','proveedores'), ('proveedor_zona','proveedores'),
      ('proveedor_producto','proveedores'), ('proveedor_evaluacion','proveedores'),
      ('solicitud_compra','abastecimiento'), ('orden_compra','abastecimiento'),
      ('notificacion_preferencia','notificaciones')
    ) AS x(tabla, modulo)
  LOOP
    EXECUTE format('CREATE OR REPLACE TRIGGER trg_aud_%1$s AFTER INSERT OR UPDATE OR DELETE ON %1$I '
                   'FOR EACH ROW EXECUTE FUNCTION fn_auditar_cambio(%2$L)', t, m);
  END LOOP;
END $$;

-- 7. Parámetros (RN40: nada de constantes en el código) -------------------------------
INSERT INTO configuracion (clave, valor, tipo_dato, ambito, unidad, descripcion) VALUES
 ('reserva_minutos', '30', 'entero', 'global', 'minutos', 'Vigencia de una reserva de inventario. Pasado ese tiempo la existencia vuelve a estar disponible.'),
 ('alerta_critica_pct', '50', 'entero', 'global', '%', 'Una existencia por debajo de este porcentaje del mínimo se avisa como crítica.'),
 ('descuento_maximo_pct', '30', 'entero', 'global', '%', 'Tope del descuento que una promoción puede aplicar a una línea.'),
 ('margen_minimo_pct', '10', 'entero', 'global', '%', 'Margen bruto por debajo del cual un precio se marca como bajo.'),
 ('elasticidad_precio_defecto', '-1.2', 'numerico', 'global', NULL, 'Supuesto no medido: cambio porcentual del volumen por cada 1 % de cambio del precio. Debe calibrarse con ventas reales.'),
 ('sensibilidad_variaciones', '-20,-10,-5,5,10,20', 'texto', 'global', '%', 'Variaciones de precio que evalúa la sensibilidad.'),
 ('reposicion_factor_objetivo', '3', 'numerico', 'global', 'veces', 'Nivel al que se repone un producto: este múltiplo del mínimo del microhub.')
ON CONFLICT DO NOTHING;

-- 8. Permisos ---------------------------------------------------------------------------
INSERT INTO permiso (clave, modulo, accion, descripcion) VALUES
 ('precios.ver', 'precios', 'ver', 'Consultar listas, promociones, márgenes y sensibilidad de precios'),
 ('precios.editar', 'precios', 'editar', 'Crear listas y promociones y cambiar precios'),
 ('proveedores.ver', 'proveedores', 'ver', 'Consultar proveedores, catálogos y ofertas'),
 ('proveedores.editar', 'proveedores', 'editar', 'Dar de alta, modificar y evaluar proveedores'),
 ('abastecimiento.ver', 'abastecimiento', 'ver', 'Consultar necesidades, solicitudes y órdenes de compra'),
 ('abastecimiento.solicitar', 'abastecimiento', 'solicitar', 'Crear solicitudes de compra de un microhub'),
 ('abastecimiento.aprobar', 'abastecimiento', 'aprobar', 'Aprobar solicitudes y emitir o cancelar órdenes de compra'),
 ('abastecimiento.recibir', 'abastecimiento', 'recibir', 'Registrar la recepción de mercancía')
ON CONFLICT (clave) DO NOTHING;

-- Una migración reaplicada no restaura permisos que el administrador retiró.
INSERT INTO rol_permiso (rol_id, permiso_id)
SELECT r.id, p.id FROM rol r CROSS JOIN permiso p
 WHERE NOT EXISTS (SELECT 1 FROM web_migracion WHERE clave = 'ola1_v1')
   AND ((r.clave = 'administrador' AND p.clave IN ('precios.ver', 'precios.editar', 'proveedores.ver', 'proveedores.editar',
                                                   'abastecimiento.ver', 'abastecimiento.solicitar', 'abastecimiento.aprobar',
                                                   'abastecimiento.recibir'))
     OR (r.clave = 'operador' AND p.clave IN ('proveedores.ver', 'abastecimiento.ver', 'abastecimiento.solicitar', 'abastecimiento.recibir'))
     OR (r.clave = 'supervisor' AND p.clave IN ('precios.ver', 'proveedores.ver', 'abastecimiento.ver', 'inventario.ver'))
     OR (r.clave IN ('planeador', 'analista') AND p.clave IN ('precios.ver', 'proveedores.ver', 'abastecimiento.ver', 'inventario.ver'))
     OR (r.clave = 'auditor' AND p.clave IN ('precios.ver', 'proveedores.ver', 'abastecimiento.ver')))
ON CONFLICT DO NOTHING;

-- 9. Datos de demostración ---------------------------------------------------------------
-- Tres proveedores con ofertas distintas, para comparar precio, plazo y capacidad.
INSERT INTO proveedor (clave, nombre, contacto, correo, telefono, dias_entrega, pedido_minimo, condiciones_pago) VALUES
 ('PV-01', 'Abarrotes del Norte', 'Rosa Garza', 'ventas@abarrotesdelnorte.example', '8181000101', 2, 800.00, 'Contado'),
 ('PV-02', 'Distribuidora Regia', 'Luis Treviño', 'pedidos@distregia.example', '8181000102', 1, 500.00, 'Crédito a 7 días'),
 ('PV-03', 'Mayorista San Nicolás', 'Elena Cantú', 'compras@mayoristasn.example', '8181000103', 4, 1500.00, 'Crédito a 15 días')
ON CONFLICT DO NOTHING;

INSERT INTO proveedor_zona (proveedor_id, zona_id)
SELECT p.id, z.id FROM proveedor p CROSS JOIN zona z WHERE p.clave IN ('PV-01', 'PV-02', 'PV-03')
ON CONFLICT DO NOTHING;

-- PV-01 surte todo a 70 % del precio de venta; PV-02, abarrotes y bebidas a 74 % con entrega
-- al día siguiente; PV-03, un producto de cada tres a 68 %, con más capacidad y más plazo.
INSERT INTO proveedor_producto (proveedor_id, producto_id, precio_compra, unidad_compra, capacidad_semanal, minimo_compra)
SELECT pv.id, pr.id, round(pr.precio * 0.70, 2), 'pieza', 500, 6
  FROM proveedor pv CROSS JOIN producto pr WHERE pv.clave = 'PV-01'
ON CONFLICT DO NOTHING;
INSERT INTO proveedor_producto (proveedor_id, producto_id, precio_compra, unidad_compra, capacidad_semanal, minimo_compra)
SELECT pv.id, pr.id, round(pr.precio * 0.74, 2), 'pieza', 200, 12
  FROM proveedor pv CROSS JOIN producto pr JOIN categoria c ON c.id = pr.categoria_id
 WHERE pv.clave = 'PV-02' AND c.nombre IN ('Abarrote básico', 'Bebidas')
ON CONFLICT DO NOTHING;
INSERT INTO proveedor_producto (proveedor_id, producto_id, precio_compra, unidad_compra, capacidad_semanal, minimo_compra)
SELECT pv.id, pr.id, round(pr.precio * 0.68, 2), 'caja', 900, 24
  FROM proveedor pv CROSS JOIN producto pr WHERE pv.clave = 'PV-03' AND pr.id % 3 = 0
ON CONFLICT DO NOTHING;

INSERT INTO proveedor_evaluacion (proveedor_id, puntualidad, calidad, precio, comentario)
SELECT pv.id, e.p, e.c, e.pr, e.nota
  FROM proveedor pv
  JOIN (VALUES ('PV-01', 4, 4, 4, 'Entrega en tiempo y producto completo.'),
               ('PV-02', 5, 4, 3, 'Muy puntual; precio algo alto.'),
               ('PV-03', 3, 4, 5, 'Mejor precio, pero entrega con atraso.')) AS e(clave, p, c, pr, nota)
    ON e.clave = pv.clave
 WHERE NOT EXISTS (SELECT 1 FROM proveedor_evaluacion x WHERE x.proveedor_id = pv.id);

-- Una lista de precios para la primera zona y una promoción en bebidas.
INSERT INTO lista_precio (nombre, zona_id, vigente_desde)
SELECT 'Lista San Bernabé Centro', z.id, fn_hoy() FROM zona z WHERE z.clave = 'ZN-SB01'
ON CONFLICT DO NOTHING;
INSERT INTO lista_precio_item (lista_id, producto_id, precio, costo)
SELECT l.id, pr.id, round(pr.precio * 1.03, 2), round(pr.precio * 0.70, 2)
  FROM lista_precio l CROSS JOIN producto pr JOIN categoria c ON c.id = pr.categoria_id
 WHERE l.nombre = 'Lista San Bernabé Centro' AND c.nombre = 'Abarrote básico'
ON CONFLICT DO NOTHING;
INSERT INTO promocion (nombre, tipo, valor, categoria_id, vigente_desde, vigente_hasta)
SELECT 'Bebidas -10 %', 'porcentaje', 10, c.id, fn_hoy(), fn_hoy() + 365
  FROM categoria c WHERE c.nombre = 'Bebidas'
   AND NOT EXISTS (SELECT 1 FROM promocion WHERE nombre = 'Bebidas -10 %');

-- Bases que ya tenían el 09 con la fecha UTC: los valores por omisión y los datos de demostración se corrigen.
ALTER TABLE lista_precio ALTER COLUMN vigente_desde SET DEFAULT fn_hoy();
ALTER TABLE promocion    ALTER COLUMN vigente_desde SET DEFAULT fn_hoy();
UPDATE lista_precio SET vigente_desde = fn_hoy() WHERE nombre = 'Lista San Bernabé Centro' AND creada_por IS NULL AND vigente_desde > fn_hoy();
UPDATE promocion SET vigente_desde = fn_hoy() WHERE nombre = 'Bebidas -10 %' AND creada_por IS NULL AND vigente_desde > fn_hoy();

INSERT INTO web_migracion (clave) VALUES ('ola1_v1') ON CONFLICT DO NOTHING;
COMMIT;
