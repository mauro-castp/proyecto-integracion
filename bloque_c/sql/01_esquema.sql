-- =====================================================================
-- Plataforma de Microhubs y Comercio de Proximidad
-- Codex Innovations · Equipo 04 · Primer Parcial
--
-- 01_esquema.sql — Modelo físico PostgreSQL (tablas, restricciones, índices)
-- Requiere PostgreSQL 16 o superior (usa UNIQUE NULLS NOT DISTINCT).
--
-- Trazabilidad: RF01-RF21, RN01-RN40, RNF08-RNF11
-- =====================================================================

DROP SCHEMA IF EXISTS microhubs CASCADE;
CREATE SCHEMA microhubs;
SET search_path TO microhubs, public;

-- ---------------------------------------------------------------------
-- 0. Tipos enumerados
-- Los nueve estados de RN19 se fijan como tipo porque son parte del
-- contrato del dominio. Las TRANSICIONES, en cambio, viven en tabla
-- (ver transicion_permitida) para cumplir RN40.
-- ---------------------------------------------------------------------

CREATE TYPE estado_pedido AS ENUM (
    'creado', 'pendiente_asignacion', 'asignado', 'en_preparacion',
    'en_ruta', 'entregado', 'entrega_parcial', 'entrega_fallida', 'cancelado'
);

CREATE TYPE estatus_registro AS ENUM ('activo', 'inactivo');

CREATE TYPE estatus_usuario AS ENUM ('activo', 'bloqueado', 'baja');

CREATE TYPE tipo_movimiento AS ENUM (
    'recepcion', 'salida_pedido', 'devolucion_cancelacion',
    'devolucion_parcial', 'merma', 'ajuste', 'conteo'
);

CREATE TYPE resultado_entrega AS ENUM ('entregado', 'parcial', 'fallida');

CREATE TYPE tipo_demanda AS ENUM (
    'fuera_cobertura', 'sin_existencia', 'bajo_ticket_minimo',
    'excede_limite_linea', 'sin_microhub_elegible'
);

CREATE TYPE ambito_config AS ENUM ('global', 'zona', 'microhub');

CREATE TYPE accion_auditoria AS ENUM (
    'alta', 'modificacion', 'baja_logica', 'login_exitoso', 'login_fallido',
    'logout', 'bloqueo_cuenta', 'desbloqueo', 'acceso_denegado',
    'cambio_estado', 'reasignacion', 'reversion_administrativa',
    'movimiento_inventario', 'cambio_configuracion'
);

-- ---------------------------------------------------------------------
-- 1. Territorio: zonas y microhubs
-- ---------------------------------------------------------------------

CREATE TABLE zona (
    id                  integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    clave               varchar(20)  NOT NULL,
    nombre              varchar(120) NOT NULL,
    colonia             varchar(120) NOT NULL,
    codigo_postal       char(5)      NOT NULL,
    municipio           varchar(80)  NOT NULL DEFAULT 'Monterrey',
    estado              varchar(80)  NOT NULL DEFAULT 'Nuevo León',
    centroide_lat       numeric(9,6) NOT NULL,
    centroide_lng       numeric(9,6) NOT NULL,
    -- Sobrescrituras por zona. NULL = usar el valor global de configuracion.
    ticket_minimo       numeric(10,2),
    costo_envio         numeric(10,2),
    envio_gratis_desde  numeric(10,2),
    estatus             estatus_registro NOT NULL DEFAULT 'activo',
    creado_en           timestamptz  NOT NULL DEFAULT now(),
    actualizado_en      timestamptz  NOT NULL DEFAULT now(),

    CONSTRAINT uq_zona_clave      UNIQUE (clave),
    CONSTRAINT uq_zona_colonia_cp UNIQUE (colonia, codigo_postal),
    CONSTRAINT ck_zona_cp         CHECK (codigo_postal ~ '^[0-9]{5}$'),
    CONSTRAINT ck_zona_lat        CHECK (centroide_lat  BETWEEN -90  AND 90),
    CONSTRAINT ck_zona_lng        CHECK (centroide_lng  BETWEEN -180 AND 180),
    CONSTRAINT ck_zona_ticket     CHECK (ticket_minimo      IS NULL OR ticket_minimo      >= 0),
    CONSTRAINT ck_zona_envio      CHECK (costo_envio        IS NULL OR costo_envio        >= 0),
    CONSTRAINT ck_zona_gratis     CHECK (envio_gratis_desde IS NULL OR envio_gratis_desde >= 0)
);
COMMENT ON TABLE  zona IS 'RN07, RN34. El código postal NO es único: en el sector San Bernabé varias colonias comparten el 64103, por eso la unicidad es (colonia, codigo_postal) y la consulta pública de cobertura acepta ambos.';
COMMENT ON COLUMN zona.ticket_minimo IS 'RN07/RN40. NULL delega en configuracion global; un valor aquí lo sobrescribe para la zona.';

CREATE INDEX ix_zona_cp      ON zona (codigo_postal) WHERE estatus = 'activo';
CREATE INDEX ix_zona_colonia ON zona (lower(colonia));

CREATE TABLE microhub (
    id                integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    clave             varchar(20)  NOT NULL,
    nombre            varchar(120) NOT NULL,
    -- RN34: la dirección exacta nunca se expone en la superficie pública.
    direccion         varchar(200) NOT NULL,
    latitud           numeric(9,6) NOT NULL,
    longitud          numeric(9,6) NOT NULL,
    radio_km          numeric(5,2),
    capacidad_turno   integer,
    hora_apertura     time         NOT NULL DEFAULT '08:00',
    hora_cierre       time         NOT NULL DEFAULT '20:00',
    estatus           estatus_registro NOT NULL DEFAULT 'activo',
    creado_en         timestamptz  NOT NULL DEFAULT now(),
    actualizado_en    timestamptz  NOT NULL DEFAULT now(),

    CONSTRAINT uq_microhub_clave UNIQUE (clave),
    -- HU17 CA2: evita latitud/longitud invertidas o fuera de rango.
    CONSTRAINT ck_mh_lat        CHECK (latitud  BETWEEN  20 AND  33),
    CONSTRAINT ck_mh_lng        CHECK (longitud BETWEEN -118 AND -86),
    CONSTRAINT ck_mh_radio      CHECK (radio_km        IS NULL OR radio_km        > 0),
    CONSTRAINT ck_mh_capacidad  CHECK (capacidad_turno IS NULL OR capacidad_turno > 0),
    CONSTRAINT ck_mh_horario    CHECK (hora_cierre > hora_apertura)
);
COMMENT ON TABLE  microhub IS 'RF10, RN05, RN12, RN34.';
COMMENT ON CONSTRAINT ck_mh_lat ON microhub IS 'HU17 CA2 / RNF09: rango continental de México. Una latitud de -100 (longitud escrita en el campo equivocado) queda rechazada por la base, no solo por el formulario.';

CREATE INDEX ix_microhub_activo ON microhub (estatus) WHERE estatus = 'activo';

CREATE TABLE microhub_zona (
    microhub_id integer NOT NULL REFERENCES microhub (id),
    zona_id     integer NOT NULL REFERENCES zona (id),
    PRIMARY KEY (microhub_id, zona_id)
);
COMMENT ON TABLE microhub_zona IS 'Zonas declaradas como atendidas por el microhub (RF10). La cobertura efectiva de un domicilio la resuelve fn_cubre por radio; esta tabla es la relación comercial, no la geométrica.';

-- ---------------------------------------------------------------------
-- 2. Identidad, roles y permisos
-- ---------------------------------------------------------------------

CREATE TABLE rol (
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    clave       varchar(40)  NOT NULL,
    nombre      varchar(80)  NOT NULL,
    descripcion varchar(300),
    requiere_microhub boolean NOT NULL DEFAULT false,
    estatus     estatus_registro NOT NULL DEFAULT 'activo',
    CONSTRAINT uq_rol_clave UNIQUE (clave)
);
COMMENT ON COLUMN rol.requiere_microhub IS 'Perfiles con ámbito por microhub (Operador). Lo usa ck_usuario_ambito.';

CREATE TABLE permiso (
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    clave       varchar(80)  NOT NULL,
    modulo      varchar(40)  NOT NULL,
    accion      varchar(40)  NOT NULL,
    descripcion varchar(300),
    CONSTRAINT uq_permiso_clave UNIQUE (clave)
);
COMMENT ON TABLE permiso IS 'RF02. El menú se construye desde esta tabla; retirar una fila de rol_permiso debe cerrar también la ruta (HU10 CA2).';

CREATE TABLE rol_permiso (
    rol_id     integer NOT NULL REFERENCES rol (id) ON DELETE CASCADE,
    permiso_id integer NOT NULL REFERENCES permiso (id) ON DELETE CASCADE,
    otorgado_en timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (rol_id, permiso_id)
);

CREATE TABLE usuario (
    id                  integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre              varchar(80)  NOT NULL,
    apellidos           varchar(120) NOT NULL,
    correo              varchar(160) NOT NULL,
    telefono            varchar(20),
    hash_contrasena     varchar(255) NOT NULL,
    rol_id              integer      NOT NULL REFERENCES rol (id),
    microhub_id         integer      REFERENCES microhub (id),
    estatus             estatus_usuario NOT NULL DEFAULT 'activo',
    intentos_fallidos   smallint     NOT NULL DEFAULT 0,
    bloqueado_hasta     timestamptz,
    ultimo_acceso       timestamptz,
    creado_en           timestamptz  NOT NULL DEFAULT now(),
    actualizado_en      timestamptz  NOT NULL DEFAULT now(),
    fecha_baja          timestamptz,

    CONSTRAINT ck_usuario_correo   CHECK (correo ~ '^[^@[:space:]]+@[^@[:space:]]+\.[a-zA-Z]{2,}$'),
    CONSTRAINT ck_usuario_intentos CHECK (intentos_fallidos >= 0),
    -- HU09 CA2: la baja es lógica; nunca se borra físicamente.
    CONSTRAINT ck_usuario_baja     CHECK ((estatus = 'baja') = (fecha_baja IS NOT NULL))
);
COMMENT ON COLUMN usuario.hash_contrasena IS 'RNF01 / HU11 CA2. Solo hash (argon2id o bcrypt). La contraseña en claro nunca se almacena ni se registra.';
COMMENT ON COLUMN usuario.intentos_fallidos IS 'RF06. El contador vive aquí para sobrevivir a un reinicio de Redis; el bloqueo operativo de ventana corta lo lleva Redis.';

CREATE UNIQUE INDEX uq_usuario_correo ON usuario (lower(correo));
CREATE INDEX ix_usuario_rol      ON usuario (rol_id);
CREATE INDEX ix_usuario_microhub ON usuario (microhub_id) WHERE microhub_id IS NOT NULL;

-- ---------------------------------------------------------------------
-- 3. Cliente y domicilio
-- ---------------------------------------------------------------------

CREATE TABLE cliente (
    id                         integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario_id                 integer NOT NULL REFERENCES usuario (id),
    aviso_privacidad_version   varchar(20)  NOT NULL,
    aviso_privacidad_aceptado_en timestamptz NOT NULL,
    creado_en                  timestamptz  NOT NULL DEFAULT now(),
    CONSTRAINT uq_cliente_usuario UNIQUE (usuario_id)
);
COMMENT ON TABLE cliente IS 'HU28 CA1: conserva la aceptación fechada del aviso de privacidad. RN38: no hay columna de precio ni de descuento por cliente; los precios diferenciados son imposibles por estructura, no por convención.';

CREATE TABLE domicilio (
    id            integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id    integer      NOT NULL REFERENCES cliente (id),
    calle         varchar(160) NOT NULL,
    numero_ext    varchar(20)  NOT NULL,
    numero_int    varchar(20),
    colonia       varchar(120) NOT NULL,
    codigo_postal char(5)      NOT NULL,
    referencia    varchar(240),
    latitud       numeric(9,6) NOT NULL,
    longitud      numeric(9,6) NOT NULL,
    zona_id       integer      REFERENCES zona (id),
    activo        boolean      NOT NULL DEFAULT true,
    creado_en     timestamptz  NOT NULL DEFAULT now(),

    CONSTRAINT ck_dom_cp   CHECK (codigo_postal ~ '^[0-9]{5}$'),
    CONSTRAINT ck_dom_lat  CHECK (latitud  BETWEEN  20 AND  33),
    CONSTRAINT ck_dom_lng  CHECK (longitud BETWEEN -118 AND -86)
);
-- RN03: un único domicilio activo por cliente durante el Primer Parcial.
-- Cuando P2 habilite varios domicilios, se elimina este índice y no cambia
-- ninguna otra estructura.
CREATE UNIQUE INDEX uq_domicilio_activo_por_cliente ON domicilio (cliente_id) WHERE activo;
CREATE INDEX ix_domicilio_zona ON domicilio (zona_id);
COMMENT ON INDEX uq_domicilio_activo_por_cliente IS 'RN03. La regla del Primer Parcial se implementa como índice parcial, no como columna, para que levantarla en P2 sea un DROP INDEX.';

-- ---------------------------------------------------------------------
-- 4. Catálogo
-- ---------------------------------------------------------------------

CREATE TABLE categoria (
    id      integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre  varchar(80) NOT NULL,
    orden   smallint    NOT NULL DEFAULT 0,
    estatus estatus_registro NOT NULL DEFAULT 'activo',
    CONSTRAINT uq_categoria_nombre UNIQUE (nombre)
);

CREATE TABLE producto (
    id            integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    clave_interna varchar(30)  NOT NULL,
    nombre        varchar(160) NOT NULL,
    categoria_id  integer      NOT NULL REFERENCES categoria (id),
    unidad        varchar(20)  NOT NULL,
    presentacion  varchar(60),
    precio        numeric(10,2) NOT NULL,
    imagen_url    varchar(300),
    estatus       estatus_registro NOT NULL DEFAULT 'activo',
    creado_en     timestamptz  NOT NULL DEFAULT now(),
    actualizado_en timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT uq_producto_clave UNIQUE (clave_interna),
    CONSTRAINT ck_producto_precio CHECK (precio > 0)
);
COMMENT ON COLUMN producto.precio IS 'Precio vigente. RN04: el pedido NO lee esta columna al consultarse; guarda su propio precio_unitario. RN38: el precio es del producto, no del par (producto, cliente).';

CREATE TABLE producto_precio_historico (
    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    producto_id    integer       NOT NULL REFERENCES producto (id),
    precio_anterior numeric(10,2) NOT NULL,
    precio_nuevo   numeric(10,2) NOT NULL,
    usuario_id     integer       REFERENCES usuario (id),
    fecha          timestamptz   NOT NULL DEFAULT now()
);
COMMENT ON TABLE producto_precio_historico IS 'HU16 CA2/CA3. Permite explicar por qué un pedido viejo tiene un precio distinto al del catálogo actual.';

CREATE INDEX ix_producto_categoria ON producto (categoria_id) WHERE estatus = 'activo';
CREATE INDEX ix_producto_nombre    ON producto (lower(nombre));
CREATE INDEX ix_pph_producto       ON producto_precio_historico (producto_id, fecha DESC);

-- ---------------------------------------------------------------------
-- 5. Inventario
-- ---------------------------------------------------------------------

CREATE TABLE inventario (
    microhub_id    integer NOT NULL REFERENCES microhub (id),
    producto_id    integer NOT NULL REFERENCES producto (id),
    existencia     integer NOT NULL DEFAULT 0,
    minimo         integer NOT NULL DEFAULT 0,
    actualizado_en timestamptz NOT NULL DEFAULT now(),

    PRIMARY KEY (microhub_id, producto_id),
    -- RN10/RN17: la última línea de defensa contra la sobreventa. Aunque
    -- fallara el bloqueo distribuido y el control de la aplicación, la base
    -- rechaza la existencia negativa.
    CONSTRAINT ck_inv_existencia CHECK (existencia >= 0),
    CONSTRAINT ck_inv_minimo     CHECK (minimo >= 0)
);
COMMENT ON CONSTRAINT ck_inv_existencia ON inventario IS 'RN10, RN17, RNF08. Invariante de sobreventa garantizada por el motor.';

CREATE TABLE movimiento_inventario (
    id                   bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    microhub_id          integer NOT NULL,
    producto_id          integer NOT NULL,
    tipo                 tipo_movimiento NOT NULL,
    cantidad             integer NOT NULL,
    existencia_resultante integer NOT NULL,
    referencia_tipo      varchar(30),
    referencia_id        bigint,
    motivo               varchar(300),
    usuario_id           integer REFERENCES usuario (id),
    fecha                timestamptz NOT NULL DEFAULT now(),

    FOREIGN KEY (microhub_id, producto_id) REFERENCES inventario (microhub_id, producto_id),
    CONSTRAINT ck_mov_cantidad  CHECK (cantidad <> 0),
    CONSTRAINT ck_mov_resultante CHECK (existencia_resultante >= 0),
    -- CU07 A3 / HU18 CA3: un ajuste o merma sin motivo no entra.
    CONSTRAINT ck_mov_motivo CHECK (
        tipo NOT IN ('ajuste', 'merma', 'conteo') OR motivo IS NOT NULL
    )
);
COMMENT ON COLUMN movimiento_inventario.existencia_resultante IS 'HU18 CA1. Se guarda el saldo posterior para poder reconstruir la línea de tiempo sin recalcular sumas.';

CREATE INDEX ix_mov_hub_prod_fecha ON movimiento_inventario (microhub_id, producto_id, fecha DESC);
CREATE INDEX ix_mov_referencia     ON movimiento_inventario (referencia_tipo, referencia_id);

-- ---------------------------------------------------------------------
-- 6. Configuración y máquina de estados (RN40)
-- ---------------------------------------------------------------------

CREATE TABLE configuracion (
    id             integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    clave          varchar(60)  NOT NULL,
    valor          varchar(200) NOT NULL,
    tipo_dato      varchar(20)  NOT NULL DEFAULT 'numerico',
    ambito         ambito_config NOT NULL DEFAULT 'global',
    ambito_id      integer,
    unidad         varchar(20),
    descripcion    varchar(300),
    actualizado_por integer     REFERENCES usuario (id),
    actualizado_en timestamptz  NOT NULL DEFAULT now(),

    CONSTRAINT uq_config UNIQUE NULLS NOT DISTINCT (clave, ambito, ambito_id),
    CONSTRAINT ck_config_ambito CHECK (
        (ambito = 'global' AND ambito_id IS NULL) OR
        (ambito <> 'global' AND ambito_id IS NOT NULL)
    ),
    CONSTRAINT ck_config_tipo CHECK (tipo_dato IN ('numerico','entero','texto','booleano','duracion'))
);
COMMENT ON TABLE configuracion IS 'RN40, RF21, HU26. Ningún parámetro operativo puede aparecer como constante literal en el código. UNIQUE NULLS NOT DISTINCT (PG15+) evita filas globales duplicadas.';

CREATE TABLE transicion_permitida (
    estado_origen  estado_pedido NOT NULL,
    estado_destino estado_pedido NOT NULL,
    rol_clave      varchar(40)   NOT NULL,
    requiere_motivo boolean      NOT NULL DEFAULT false,
    descripcion    varchar(200),
    PRIMARY KEY (estado_origen, estado_destino, rol_clave),
    CONSTRAINT ck_transicion_distinta CHECK (estado_origen <> estado_destino)
);
COMMENT ON TABLE transicion_permitida IS 'RN20, RN21, RN23, RN24. La máquina de estados es DATO, no código: agregar una transición en P2 es un INSERT, y el trigger trg_pedido_transicion la respeta sin recompilar.';

-- ---------------------------------------------------------------------
-- 7. Pedido
-- ---------------------------------------------------------------------

CREATE SEQUENCE seq_folio_pedido;

CREATE TABLE pedido (
    id                    bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    folio                 varchar(24) NOT NULL,
    cliente_id            integer NOT NULL REFERENCES cliente (id),
    domicilio_id          integer NOT NULL REFERENCES domicilio (id),
    zona_id               integer NOT NULL REFERENCES zona (id),
    microhub_id           integer REFERENCES microhub (id),
    estado                estado_pedido NOT NULL DEFAULT 'creado',
    subtotal              numeric(12,2) NOT NULL DEFAULT 0,
    costo_envio           numeric(12,2) NOT NULL DEFAULT 0,
    total                 numeric(12,2) GENERATED ALWAYS AS (subtotal + costo_envio) STORED,
    motivo_no_asignacion  varchar(300),
    motivo_cancelacion    varchar(300),
    creado_en             timestamptz NOT NULL DEFAULT now(),
    asignado_en           timestamptz,
    cerrado_en            timestamptz,
    actualizado_en        timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT uq_pedido_folio    UNIQUE (folio),
    CONSTRAINT ck_pedido_subtotal CHECK (subtotal    >= 0),
    CONSTRAINT ck_pedido_envio    CHECK (costo_envio >= 0),
    -- RN14: un pedido sin microhub solo es legal si es pendiente de
    -- asignación (con motivo), está recién creado o fue cancelado.
    CONSTRAINT ck_pedido_asignacion CHECK (
        (microhub_id IS NOT NULL)
        OR estado IN ('creado', 'pendiente_asignacion', 'cancelado')
    ),
    CONSTRAINT ck_pedido_motivo_pendiente CHECK (
        estado <> 'pendiente_asignacion' OR motivo_no_asignacion IS NOT NULL
    )
);
COMMENT ON COLUMN pedido.total IS 'RN08: columna generada = subtotal + costo_envio. El ticket mínimo se valida contra subtotal, nunca contra total; al ser generada, nadie puede guardar un total incoherente.';
COMMENT ON CONSTRAINT ck_pedido_motivo_pendiente ON pedido IS 'RN14. Un pendiente de asignación sin motivo no se puede insertar.';

CREATE INDEX ix_pedido_cliente   ON pedido (cliente_id, creado_en DESC);
CREATE INDEX ix_pedido_hub_estado ON pedido (microhub_id, estado);
CREATE INDEX ix_pedido_estado    ON pedido (estado);
CREATE INDEX ix_pedido_zona_fecha ON pedido (zona_id, creado_en);
-- Bandeja del operador (CU04): los pedidos vivos son pocos frente al histórico.
CREATE INDEX ix_pedido_activos ON pedido (microhub_id, creado_en)
    WHERE estado IN ('asignado', 'en_preparacion', 'en_ruta');

CREATE TABLE pedido_detalle (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pedido_id       bigint  NOT NULL REFERENCES pedido (id) ON DELETE CASCADE,
    producto_id     integer NOT NULL REFERENCES producto (id),
    cantidad        integer NOT NULL,
    precio_unitario numeric(10,2) NOT NULL,
    importe         numeric(12,2) GENERATED ALWAYS AS (cantidad * precio_unitario) STORED,

    CONSTRAINT uq_detalle_producto UNIQUE (pedido_id, producto_id),
    CONSTRAINT ck_detalle_cantidad CHECK (cantidad > 0),
    CONSTRAINT ck_detalle_precio   CHECK (precio_unitario > 0)
);
COMMENT ON COLUMN pedido_detalle.precio_unitario IS 'RN04. Copia congelada del precio al momento de la compra. No es un JOIN a producto.precio: un cambio de catálogo posterior no puede alterar un pedido histórico.';
CREATE INDEX ix_detalle_pedido   ON pedido_detalle (pedido_id);
CREATE INDEX ix_detalle_producto ON pedido_detalle (producto_id);

CREATE TABLE historial_estatus (
    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pedido_id      bigint NOT NULL REFERENCES pedido (id),
    estado_anterior estado_pedido,
    estado_nuevo   estado_pedido NOT NULL,
    usuario_id     integer REFERENCES usuario (id),
    proceso        varchar(40),
    motivo         varchar(300),
    fecha          timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT ck_hist_responsable CHECK (usuario_id IS NOT NULL OR proceso IS NOT NULL)
);
COMMENT ON TABLE historial_estatus IS 'RN32, HU20 CA3. Cada transición conserva estado anterior, nuevo, fecha y responsable. Si no hubo usuario, hubo proceso: nunca ambos nulos.';
CREATE INDEX ix_hist_pedido ON historial_estatus (pedido_id, fecha);

-- ---------------------------------------------------------------------
-- 8. Decisión de asignación (RN15)
-- ---------------------------------------------------------------------

CREATE TABLE decision_asignacion (
    id                bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pedido_id         bigint  NOT NULL REFERENCES pedido (id),
    microhub_ganador_id integer REFERENCES microhub (id),
    criterio          varchar(40) NOT NULL,
    candidatos_evaluados smallint NOT NULL DEFAULT 0,
    manual            boolean NOT NULL DEFAULT false,
    usuario_id        integer REFERENCES usuario (id),
    motivo            varchar(300),
    traza_mongo_id    varchar(48),
    fecha             timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT ck_decision_criterio CHECK (
        criterio IN ('menor_distancia','mayor_capacidad_libre','manual','sin_elegible')
    ),
    -- RN24: la reasignación manual exige motivo obligatorio.
    CONSTRAINT ck_decision_manual CHECK (
        NOT manual OR (usuario_id IS NOT NULL AND motivo IS NOT NULL)
    )
);
COMMENT ON TABLE decision_asignacion IS 'RN15, RN24. El resumen auditable vive en PostgreSQL por integridad referencial; la traza completa de candidatos evaluados vive en MongoDB (colección decisiones_asignacion) y se enlaza con traza_mongo_id, tal como RF15 declara los tres componentes.';
COMMENT ON CONSTRAINT ck_decision_manual ON decision_asignacion IS 'RN24 / VR-12: reasignar sin motivo es imposible a nivel de motor.';
CREATE INDEX ix_decision_pedido ON decision_asignacion (pedido_id);

-- ---------------------------------------------------------------------
-- 9. Entrega y cobro
-- ---------------------------------------------------------------------

CREATE TABLE entrega (
    id                     bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pedido_id              bigint  NOT NULL REFERENCES pedido (id),
    repartidor_id          integer REFERENCES usuario (id),
    turno_fecha            date,
    asignada_en            timestamptz,
    salida_en              timestamptz,
    cierre_en              timestamptz,
    resultado              resultado_entrega,
    confirmacion_recepcion boolean NOT NULL DEFAULT false,
    monto_cobrado          numeric(12,2),
    cambio_entregado       numeric(12,2),
    evidencia_url          varchar(300),
    incidencia             varchar(400),
    cerrada_por_usuario_id integer REFERENCES usuario (id),

    CONSTRAINT uq_entrega_pedido UNIQUE (pedido_id),
    CONSTRAINT ck_entrega_montos CHECK (
        (monto_cobrado    IS NULL OR monto_cobrado    >= 0) AND
        (cambio_entregado IS NULL OR cambio_entregado >= 0)
    ),
    -- RN27: cerrar exige el trío completo.
    CONSTRAINT ck_entrega_cierre CHECK (
        cierre_en IS NULL OR (resultado IS NOT NULL AND monto_cobrado IS NOT NULL
                              AND cambio_entregado IS NOT NULL)
    ),
    -- RN29: una entrega fallida sin motivo no se puede cerrar.
    CONSTRAINT ck_entrega_fallida CHECK (
        resultado IS DISTINCT FROM 'fallida' OR incidencia IS NOT NULL
    )
);
COMMENT ON CONSTRAINT ck_entrega_cierre  ON entrega IS 'RN27 / CU06 A3.';
COMMENT ON CONSTRAINT ck_entrega_fallida ON entrega IS 'RN29 / CU05 A3: motivo obligatorio.';
CREATE INDEX ix_entrega_repartidor ON entrega (repartidor_id, turno_fecha);

CREATE TABLE entrega_linea (
    id                bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    entrega_id        bigint NOT NULL REFERENCES entrega (id) ON DELETE CASCADE,
    pedido_detalle_id bigint NOT NULL REFERENCES pedido_detalle (id),
    cantidad_entregada integer NOT NULL DEFAULT 0,
    cantidad_devuelta  integer NOT NULL DEFAULT 0,
    motivo            varchar(300),
    CONSTRAINT uq_entrega_linea UNIQUE (entrega_id, pedido_detalle_id),
    CONSTRAINT ck_el_cantidades CHECK (cantidad_entregada >= 0 AND cantidad_devuelta >= 0),
    CONSTRAINT ck_el_motivo CHECK (cantidad_devuelta = 0 OR motivo IS NOT NULL)
);
COMMENT ON TABLE entrega_linea IS 'RN28, HU24 CA2. Identifica qué líneas no se entregaron y cuántas unidades regresan al inventario.';

-- ---------------------------------------------------------------------
-- 10. Demanda no atendida (RN06)
-- ---------------------------------------------------------------------

CREATE TABLE demanda_no_atendida (
    id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tipo          tipo_demanda NOT NULL,
    zona_id       integer REFERENCES zona (id),
    colonia_texto varchar(120),
    cp_texto      char(5),
    producto_id   integer REFERENCES producto (id),
    cantidad_solicitada integer,
    cliente_id    integer REFERENCES cliente (id),
    origen        varchar(20) NOT NULL DEFAULT 'web',
    fecha         timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT ck_dna_referencia CHECK (
        zona_id IS NOT NULL OR colonia_texto IS NOT NULL
        OR cp_texto IS NOT NULL OR producto_id IS NOT NULL
    )
);
COMMENT ON TABLE demanda_no_atendida IS 'RN06, HU01/HU08. cliente_id es opcional a propósito: el visitante no autenticado genera demanda válida y HU01 CA1 exige poder analizarla sin datos personales.';
CREATE INDEX ix_dna_zona_fecha ON demanda_no_atendida (zona_id, fecha);
CREATE INDEX ix_dna_tipo       ON demanda_no_atendida (tipo, fecha);

-- ---------------------------------------------------------------------
-- 11. Auditoría (RN30, RN31)
-- ---------------------------------------------------------------------

CREATE TABLE auditoria (
    id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario_id       integer REFERENCES usuario (id),
    correo_intento   varchar(160),
    fecha            timestamptz NOT NULL DEFAULT now(),
    ip_origen        inet,
    user_agent       varchar(300),
    modulo           varchar(40) NOT NULL,
    accion           accion_auditoria NOT NULL,
    entidad          varchar(40),
    entidad_id       varchar(40),
    valores_anteriores jsonb,
    valores_nuevos   jsonb,
    exitoso          boolean NOT NULL DEFAULT true,
    detalle          varchar(400)
);
COMMENT ON TABLE auditoria IS 'RF07, RN30, RN31, RNF10, RNF33. Bitácora de NEGOCIO, separada de los logs técnicos de MongoDB. Es append-only: ver trg_auditoria_inmutable en 02_logica.sql.';
COMMENT ON COLUMN auditoria.correo_intento IS 'Para login_fallido, donde todavía no hay usuario_id. Nunca guarda la contraseña intentada (HU13 CA3).';

CREATE INDEX ix_aud_usuario_fecha ON auditoria (usuario_id, fecha DESC);
CREATE INDEX ix_aud_modulo_accion ON auditoria (modulo, accion, fecha DESC);
CREATE INDEX ix_aud_entidad       ON auditoria (entidad, entidad_id);
CREATE INDEX ix_aud_fecha         ON auditoria (fecha DESC);
