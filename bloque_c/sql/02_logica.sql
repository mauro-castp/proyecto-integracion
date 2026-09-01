-- =====================================================================
-- 02_logica.sql — Funciones, triggers, vistas y roles de base
-- Codex Innovations · Equipo 04
--
-- Aquí las reglas de negocio dejan de ser prosa y pasan a ser motor.
-- Convención de sesión: la aplicación fija, por transacción,
--     SET LOCAL app.usuario_id = '<id>';
--     SET LOCAL app.rol        = '<clave_rol>';
-- Los triggers leen esas variables. Si no están, el actor es 'sistema'.
-- =====================================================================

SET search_path TO microhubs, public;

-- ---------------------------------------------------------------------
-- 1. Contexto de sesión
-- ---------------------------------------------------------------------

CREATE OR REPLACE FUNCTION ctx_usuario_id() RETURNS integer
LANGUAGE sql STABLE AS $$
    SELECT NULLIF(current_setting('app.usuario_id', true), '')::integer;
$$;

CREATE OR REPLACE FUNCTION ctx_rol() RETURNS varchar
LANGUAGE sql STABLE AS $$
    SELECT COALESCE(NULLIF(current_setting('app.rol', true), ''), 'sistema');
$$;

-- ---------------------------------------------------------------------
-- 2. Cobertura geográfica — RNF11
-- Toda verificación de cobertura del sistema entra por fn_cubre.
-- Migrar de radio a polígono (PostGIS) significa reescribir SOLO esta
-- función; ninguna otra consulta cambia.
-- ---------------------------------------------------------------------

CREATE OR REPLACE FUNCTION fn_distancia_km(
    lat1 numeric, lng1 numeric, lat2 numeric, lng2 numeric
) RETURNS numeric
LANGUAGE plpgsql IMMUTABLE AS $$
DECLARE
    r  constant double precision := 6371.0088;  -- radio medio terrestre
    p1 double precision := radians(lat1::double precision);
    p2 double precision := radians(lat2::double precision);
    dp double precision := radians((lat2 - lat1)::double precision);
    dl double precision := radians((lng2 - lng1)::double precision);
    a  double precision;
BEGIN
    a := sin(dp / 2) ^ 2 + cos(p1) * cos(p2) * sin(dl / 2) ^ 2;
    RETURN round((2 * r * asin(sqrt(a)))::numeric, 4);
END;
$$;
COMMENT ON FUNCTION fn_distancia_km IS 'Haversine. Única fuente de distancia del proyecto (HU03 CA1).';

CREATE OR REPLACE FUNCTION fn_cubre(p_microhub_id integer, p_lat numeric, p_lng numeric)
RETURNS boolean
LANGUAGE plpgsql STABLE AS $$
DECLARE
    v_mh    record;
    v_radio numeric;
BEGIN
    SELECT latitud, longitud, radio_km, estatus INTO v_mh
      FROM microhub WHERE id = p_microhub_id;

    -- RN05 / HU17 CA3: solo un microhub activo puede cubrir.
    IF NOT FOUND OR v_mh.estatus <> 'activo' THEN
        RETURN false;
    END IF;

    v_radio := COALESCE(v_mh.radio_km, fn_config_num('radio_cobertura_km', 'microhub', p_microhub_id));

    -- HU03 CA2: cubierto es distancia <= radio, no menor estricto.
    RETURN fn_distancia_km(v_mh.latitud, v_mh.longitud, p_lat, p_lng) <= v_radio;
END;
$$;
COMMENT ON FUNCTION fn_cubre IS 'RNF11, RN05, HU03. Punto único de cobertura del sistema.';

-- ---------------------------------------------------------------------
-- 3. Resolución de parámetros — RN40
-- Precedencia: valor específico del ámbito -> valor global.
-- Ninguna regla lee una constante literal.
-- ---------------------------------------------------------------------

CREATE OR REPLACE FUNCTION fn_config_num(
    p_clave varchar, p_ambito ambito_config DEFAULT 'global', p_ambito_id integer DEFAULT NULL
) RETURNS numeric
LANGUAGE plpgsql STABLE AS $$
DECLARE v_valor varchar;
BEGIN
    IF p_ambito <> 'global' AND p_ambito_id IS NOT NULL THEN
        SELECT valor INTO v_valor FROM configuracion
         WHERE clave = p_clave AND ambito = p_ambito AND ambito_id = p_ambito_id;
        IF FOUND THEN RETURN v_valor::numeric; END IF;
    END IF;

    SELECT valor INTO v_valor FROM configuracion
     WHERE clave = p_clave AND ambito = 'global';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'RN40: parámetro % no existe en configuracion. Ningún valor puede quedar como constante en el código.', p_clave
            USING ERRCODE = 'no_data_found';
    END IF;
    RETURN v_valor::numeric;
END;
$$;

-- Ticket mínimo y costo de envío: la zona sobrescribe, el global respalda.
CREATE OR REPLACE FUNCTION fn_ticket_minimo(p_zona_id integer) RETURNS numeric
LANGUAGE sql STABLE AS $$
    SELECT COALESCE((SELECT z.ticket_minimo FROM zona z WHERE z.id = p_zona_id),
                    fn_config_num('ticket_minimo', 'zona', p_zona_id));
$$;

CREATE OR REPLACE FUNCTION fn_costo_envio(p_zona_id integer, p_subtotal numeric) RETURNS numeric
LANGUAGE plpgsql STABLE AS $$
DECLARE v_costo numeric; v_gratis numeric;
BEGIN
    SELECT COALESCE(z.costo_envio,        fn_config_num('costo_envio', 'zona', p_zona_id)),
           COALESCE(z.envio_gratis_desde, fn_config_num('envio_gratis_desde', 'zona', p_zona_id))
      INTO v_costo, v_gratis
      FROM zona z WHERE z.id = p_zona_id;

    -- Umbral de envío gratuito: parámetro documentado en la sección 4.6 del
    -- entregable de reglas. NO tiene una RN propia; queda señalado como
    -- hueco a resolver (ver hallazgo 12 de la revisión de consistencia).
    IF v_gratis IS NOT NULL AND p_subtotal >= v_gratis THEN
        RETURN 0;
    END IF;
    RETURN v_costo;
END;
$$;

-- ---------------------------------------------------------------------
-- 4. Bitácora inmutable — RN31
-- ---------------------------------------------------------------------

CREATE OR REPLACE FUNCTION fn_auditoria_inmutable() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'RN31: la bitácora es de solo escritura. Ningún perfil, incluido el Administrador, puede % una entrada de auditoría.', lower(TG_OP)
        USING ERRCODE = 'insufficient_privilege';
END;
$$;

CREATE OR REPLACE TRIGGER trg_auditoria_inmutable
    BEFORE UPDATE OR DELETE ON auditoria
    FOR EACH ROW EXECUTE FUNCTION fn_auditoria_inmutable();
COMMENT ON TRIGGER trg_auditoria_inmutable ON auditoria IS 'RN31, HU14 CA3, VR-15. Defensa en profundidad: además de revocar el privilegio al rol de aplicación, el motor rechaza la operación aunque alguien se conecte como propietario.';

CREATE OR REPLACE FUNCTION fn_auditar(
    p_modulo varchar, p_accion accion_auditoria, p_entidad varchar DEFAULT NULL,
    p_entidad_id varchar DEFAULT NULL, p_anteriores jsonb DEFAULT NULL,
    p_nuevos jsonb DEFAULT NULL, p_detalle varchar DEFAULT NULL,
    p_exitoso boolean DEFAULT true
) RETURNS bigint
LANGUAGE sql AS $$
    INSERT INTO auditoria (usuario_id, modulo, accion, entidad, entidad_id,
                           valores_anteriores, valores_nuevos, detalle, exitoso,
                           ip_origen)
    VALUES (ctx_usuario_id(), p_modulo, p_accion, p_entidad, p_entidad_id,
            p_anteriores, p_nuevos, p_detalle, p_exitoso,
            NULLIF(current_setting('app.ip_origen', true), '')::inet)
    RETURNING id;
$$;

-- ---------------------------------------------------------------------
-- 5. Máquina de estados — RN20, RN21, RN23, RN32
-- ---------------------------------------------------------------------

CREATE OR REPLACE FUNCTION fn_valida_transicion() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    v_rol    varchar := ctx_rol();
    v_regla  record;
BEGIN
    IF NEW.estado = OLD.estado THEN
        RETURN NEW;
    END IF;

    SELECT * INTO v_regla FROM transicion_permitida t
     WHERE t.estado_origen  = OLD.estado
       AND t.estado_destino = NEW.estado
       AND t.rol_clave IN (v_rol, 'sistema')
     ORDER BY (t.rol_clave = v_rol) DESC
     LIMIT 1;

    IF NOT FOUND THEN
        -- HU20 CA2 / VR-10: se rechaza sin alterar el estado actual.
        RAISE EXCEPTION 'RN20: transición ilegal % -> % para el rol %. El pedido % conserva su estado.',
            OLD.estado, NEW.estado, v_rol, OLD.folio
            USING ERRCODE = 'check_violation';
    END IF;

    IF v_regla.requiere_motivo
       AND COALESCE(NEW.motivo_cancelacion, NEW.motivo_no_asignacion) IS NULL THEN
        RAISE EXCEPTION 'RN24: la transición % -> % exige motivo.', OLD.estado, NEW.estado
            USING ERRCODE = 'check_violation';
    END IF;

    NEW.actualizado_en := now();
    IF NEW.estado IN ('entregado','entrega_parcial','entrega_fallida','cancelado') THEN
        NEW.cerrado_en := COALESCE(NEW.cerrado_en, now());
    END IF;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER trg_pedido_transicion
    BEFORE UPDATE OF estado ON pedido
    FOR EACH ROW EXECUTE FUNCTION fn_valida_transicion();

-- RN32: el historial no depende de que la aplicación se acuerde de escribirlo.
CREATE OR REPLACE FUNCTION fn_registra_historial() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO historial_estatus (pedido_id, estado_anterior, estado_nuevo, usuario_id, proceso)
        VALUES (NEW.id, NULL, NEW.estado, ctx_usuario_id(),
                CASE WHEN ctx_usuario_id() IS NULL THEN 'alta_pedido' END);
    ELSIF NEW.estado IS DISTINCT FROM OLD.estado THEN
        INSERT INTO historial_estatus (pedido_id, estado_anterior, estado_nuevo, usuario_id, proceso, motivo)
        VALUES (NEW.id, OLD.estado, NEW.estado, ctx_usuario_id(),
                CASE WHEN ctx_usuario_id() IS NULL THEN 'motor_asignacion' END,
                COALESCE(NEW.motivo_cancelacion, NEW.motivo_no_asignacion));
    END IF;
    RETURN NULL;
END;
$$;

CREATE OR REPLACE TRIGGER trg_pedido_historial
    AFTER INSERT OR UPDATE OF estado ON pedido
    FOR EACH ROW EXECUTE FUNCTION fn_registra_historial();
COMMENT ON TRIGGER trg_pedido_historial ON pedido IS 'RN32. Historial garantizado por el motor: es imposible cambiar un estado sin dejar rastro.';

-- ---------------------------------------------------------------------
-- 6. Límite de unidades por línea — RN09 (parámetro, no constante)
-- ---------------------------------------------------------------------

CREATE OR REPLACE FUNCTION fn_valida_limite_linea() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE v_limite integer := fn_config_num('limite_unidades_linea')::integer;
BEGIN
    IF NEW.cantidad > v_limite THEN
        RAISE EXCEPTION 'RN09: la línea solicita % unidades y el límite configurado es %.',
            NEW.cantidad, v_limite
            USING ERRCODE = 'check_violation';
    END IF;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER trg_detalle_limite
    BEFORE INSERT OR UPDATE OF cantidad ON pedido_detalle
    FOR EACH ROW EXECUTE FUNCTION fn_valida_limite_linea();
COMMENT ON TRIGGER trg_detalle_limite ON pedido_detalle IS 'RN09 + RN40 juntas: la regla se cumple en la base pero el número vive en configuracion. Cambiar el límite es un UPDATE, no un despliegue (VR-16).';

-- ---------------------------------------------------------------------
-- 7. Historial de precios — HU16 CA2
-- ---------------------------------------------------------------------

CREATE OR REPLACE FUNCTION fn_historia_precio() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.precio IS DISTINCT FROM OLD.precio THEN
        INSERT INTO producto_precio_historico (producto_id, precio_anterior, precio_nuevo, usuario_id)
        VALUES (NEW.id, OLD.precio, NEW.precio, ctx_usuario_id());
        PERFORM fn_auditar('catalogo', 'modificacion', 'producto', NEW.id::varchar,
                           jsonb_build_object('precio', OLD.precio),
                           jsonb_build_object('precio', NEW.precio));
    END IF;
    NEW.actualizado_en := now();
    RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER trg_producto_precio
    BEFORE UPDATE ON producto
    FOR EACH ROW EXECUTE FUNCTION fn_historia_precio();

-- ---------------------------------------------------------------------
-- 8. Folio
-- ---------------------------------------------------------------------

CREATE OR REPLACE FUNCTION fn_nuevo_folio() RETURNS varchar
LANGUAGE sql VOLATILE AS $$
    SELECT 'PED-' || to_char(now(), 'YYYYMMDD') || '-' ||
           lpad(nextval('seq_folio_pedido')::text, 6, '0');
$$;
ALTER TABLE pedido ALTER COLUMN folio SET DEFAULT fn_nuevo_folio();
COMMENT ON FUNCTION fn_nuevo_folio IS 'El folio se genera con una secuencia de PostgreSQL, NO con un contador de Redis: Redis no es durable y un folio duplicado tras un reinicio sería un incidente contable.';

-- ---------------------------------------------------------------------
-- 9. Capacidad y elegibilidad — RN12, RN13
-- ---------------------------------------------------------------------

CREATE OR REPLACE VIEW v_ocupacion_microhub AS
SELECT m.id  AS microhub_id,
       m.clave,
       m.nombre,
       COALESCE(m.capacidad_turno, fn_config_num('capacidad_turno')::integer) AS capacidad_turno,
       count(p.id) FILTER (
           WHERE p.estado IN ('asignado','en_preparacion','en_ruta')
             AND p.creado_en::date = current_date
       ) AS pedidos_en_turno,
       COALESCE(m.capacidad_turno, fn_config_num('capacidad_turno')::integer)
         - count(p.id) FILTER (
               WHERE p.estado IN ('asignado','en_preparacion','en_ruta')
                 AND p.creado_en::date = current_date
           ) AS capacidad_libre
  FROM microhub m
  LEFT JOIN pedido p ON p.microhub_id = m.id
 WHERE m.estatus = 'activo'
 GROUP BY m.id, m.clave, m.nombre, m.capacidad_turno;

CREATE OR REPLACE FUNCTION fn_microhubs_elegibles(p_pedido_id bigint)
RETURNS TABLE (
    microhub_id integer, clave varchar, distancia_km numeric,
    cubre boolean, stock_completo boolean, capacidad_libre integer, elegible boolean,
    motivo_descarte varchar
)
LANGUAGE plpgsql STABLE AS $$
DECLARE v_lat numeric; v_lng numeric;
BEGIN
    SELECT d.latitud, d.longitud INTO v_lat, v_lng
      FROM pedido p JOIN domicilio d ON d.id = p.domicilio_id
     WHERE p.id = p_pedido_id;

    RETURN QUERY
    WITH lineas AS (
        SELECT pd.producto_id, pd.cantidad
          FROM pedido_detalle pd WHERE pd.pedido_id = p_pedido_id
    ),
    eval AS (
        SELECT m.id, m.clave,
               fn_distancia_km(m.latitud, m.longitud, v_lat, v_lng) AS dist,
               fn_cubre(m.id, v_lat, v_lng)                          AS cub,
               NOT EXISTS (
                   SELECT 1 FROM lineas l
                    LEFT JOIN inventario i
                           ON i.microhub_id = m.id AND i.producto_id = l.producto_id
                    WHERE COALESCE(i.existencia, 0) < l.cantidad
               ) AS stock,
               o.capacidad_libre
          FROM microhub m
          JOIN v_ocupacion_microhub o ON o.microhub_id = m.id
         WHERE m.estatus = 'activo'
    )
    SELECT e.id, e.clave, e.dist, e.cub, e.stock, e.capacidad_libre::integer,
           (e.cub AND e.stock AND e.capacidad_libre > 0) AS elegible,
           CASE WHEN NOT e.cub                 THEN 'fuera_de_cobertura'
                WHEN NOT e.stock               THEN 'sin_existencia_completa'
                WHEN e.capacidad_libre <= 0    THEN 'sin_capacidad_en_turno'
           END::varchar
      FROM eval e
     ORDER BY (e.cub AND e.stock AND e.capacidad_libre > 0) DESC,
              e.dist ASC, e.capacidad_libre DESC;
END;
$$;
COMMENT ON FUNCTION fn_microhubs_elegibles IS 'RN12. Devuelve TODOS los candidatos con su veredicto, no solo el ganador: es lo que RN15 exige conservar para auditar el algoritmo.';

-- ---------------------------------------------------------------------
-- 10. Asignación atómica con descuento de inventario
--     RN12, RN13, RN14, RN15, RN16, RN17, RNF08
-- ---------------------------------------------------------------------

CREATE OR REPLACE FUNCTION fn_asignar_pedido(p_pedido_id bigint)
RETURNS TABLE (asignado boolean, microhub_id integer, criterio varchar, motivo varchar)
LANGUAGE plpgsql AS $$
DECLARE
    v_ganador   record;
    v_empate    integer;
    v_criterio  varchar;
    v_linea     record;
    v_nueva_ex  integer;
    v_pedido    record;
    v_decision  bigint;
    v_n         smallint;
BEGIN
    SELECT * INTO v_pedido FROM pedido WHERE id = p_pedido_id FOR UPDATE;
    IF v_pedido.estado NOT IN ('creado', 'pendiente_asignacion') THEN
        RAISE EXCEPTION 'El pedido % está en estado % y no admite asignación.',
            v_pedido.folio, v_pedido.estado USING ERRCODE = 'check_violation';
    END IF;

    -- Candidatos elegibles ordenados por RN13: menor distancia primero.
    CREATE TEMP TABLE IF NOT EXISTS tmp_cand ON COMMIT DROP AS
        SELECT * FROM fn_microhubs_elegibles(p_pedido_id) WITH NO DATA;
    DELETE FROM tmp_cand;
    INSERT INTO tmp_cand SELECT * FROM fn_microhubs_elegibles(p_pedido_id);

    SELECT count(*) INTO v_n FROM tmp_cand;

    SELECT * INTO v_ganador FROM tmp_cand c
     WHERE c.elegible ORDER BY c.distancia_km ASC, c.capacidad_libre DESC LIMIT 1;

    -- RN14: ningún microhub cumple cobertura + existencia + capacidad.
    IF NOT FOUND THEN
        UPDATE pedido pe
           SET estado = 'pendiente_asignacion',
               motivo_no_asignacion = 'RN14: ningún microhub activo cumple simultáneamente cobertura, existencia completa y capacidad disponible en el turno.'
         WHERE pe.id = p_pedido_id;

        INSERT INTO decision_asignacion (pedido_id, microhub_ganador_id, criterio,
                                         candidatos_evaluados, motivo)
        VALUES (p_pedido_id, NULL, 'sin_elegible', v_n,
                'Sin candidato elegible; el pedido queda pendiente para revisión del Planeador (RN24).');

        RETURN QUERY SELECT false, NULL::integer, 'sin_elegible'::varchar,
                            'sin microhub elegible'::varchar;
        RETURN;
    END IF;

    -- RN13: criterio de desempate registrado explícitamente.
    SELECT count(*) INTO v_empate FROM tmp_cand c
     WHERE c.elegible AND c.distancia_km = v_ganador.distancia_km;
    v_criterio := CASE WHEN v_empate > 1 THEN 'mayor_capacidad_libre' ELSE 'menor_distancia' END;

    -- RN16/RN17: descuento atómico. El bloqueo se toma en orden ascendente
    -- de producto_id para que dos transacciones concurrentes sobre el mismo
    -- microhub no puedan entrelazarse y producir un interbloqueo.
    FOR v_linea IN
        SELECT pd.producto_id, pd.cantidad
          FROM pedido_detalle pd WHERE pd.pedido_id = p_pedido_id
         ORDER BY pd.producto_id
    LOOP
        SELECT i.existencia INTO v_nueva_ex
          FROM inventario i
         WHERE i.microhub_id = v_ganador.microhub_id
           AND i.producto_id = v_linea.producto_id
           FOR UPDATE;                       -- <- serializa a los competidores

        IF v_nueva_ex < v_linea.cantidad THEN
            -- Otro pedido ganó la carrera entre la evaluación y el bloqueo.
            RAISE EXCEPTION 'RN17: existencia insuficiente del producto % al momento del descuento; la transacción completa se revierte.', v_linea.producto_id
                USING ERRCODE = 'check_violation';
        END IF;

        v_nueva_ex := v_nueva_ex - v_linea.cantidad;

        UPDATE inventario i SET existencia = v_nueva_ex, actualizado_en = now()
         WHERE i.microhub_id = v_ganador.microhub_id
           AND i.producto_id = v_linea.producto_id;

        INSERT INTO movimiento_inventario (microhub_id, producto_id, tipo, cantidad,
                                           existencia_resultante, referencia_tipo,
                                           referencia_id, usuario_id)
        VALUES (v_ganador.microhub_id, v_linea.producto_id, 'salida_pedido',
                -v_linea.cantidad, v_nueva_ex, 'pedido', p_pedido_id, ctx_usuario_id());
    END LOOP;

    UPDATE pedido pe
       SET microhub_id = v_ganador.microhub_id,
           estado = 'asignado',
           asignado_en = now(),
           motivo_no_asignacion = NULL
     WHERE pe.id = p_pedido_id;

    INSERT INTO decision_asignacion (pedido_id, microhub_ganador_id, criterio,
                                     candidatos_evaluados)
    VALUES (p_pedido_id, v_ganador.microhub_id, v_criterio, v_n)
    RETURNING id INTO v_decision;

    RETURN QUERY SELECT true, v_ganador.microhub_id, v_criterio, NULL::varchar;
END;
$$;
COMMENT ON FUNCTION fn_asignar_pedido IS 'RN12-RN17 y RNF08 en una sola transacción. Si algo falla dentro, no queda ni inventario descontado ni pedido asignado (CU03 A6).';

-- ---------------------------------------------------------------------
-- 11. Devolución de inventario — RN18, RN28
-- ---------------------------------------------------------------------

CREATE OR REPLACE FUNCTION fn_devolver_inventario(
    p_pedido_id bigint, p_tipo tipo_movimiento, p_motivo varchar DEFAULT NULL
) RETURNS integer
LANGUAGE plpgsql AS $$
DECLARE v_hub integer; v_l record; v_ex integer; v_c integer := 0;
BEGIN
    SELECT microhub_id INTO v_hub FROM pedido WHERE id = p_pedido_id;
    IF v_hub IS NULL THEN RETURN 0; END IF;   -- nunca se descontó nada

    FOR v_l IN
        SELECT pd.producto_id,
               CASE WHEN p_tipo = 'devolucion_parcial'
                    THEN COALESCE(el.cantidad_devuelta, 0)
                    ELSE pd.cantidad END AS cant
          FROM pedido_detalle pd
          LEFT JOIN entrega e  ON e.pedido_id = pd.pedido_id
          LEFT JOIN entrega_linea el ON el.pedido_detalle_id = pd.id AND el.entrega_id = e.id
         WHERE pd.pedido_id = p_pedido_id
         ORDER BY pd.producto_id
    LOOP
        CONTINUE WHEN v_l.cant = 0;

        SELECT i.existencia INTO v_ex FROM inventario i
         WHERE i.microhub_id = v_hub AND i.producto_id = v_l.producto_id FOR UPDATE;

        v_ex := v_ex + v_l.cant;
        UPDATE inventario i SET existencia = v_ex, actualizado_en = now()
         WHERE i.microhub_id = v_hub AND i.producto_id = v_l.producto_id;

        INSERT INTO movimiento_inventario (microhub_id, producto_id, tipo, cantidad,
                                           existencia_resultante, referencia_tipo,
                                           referencia_id, motivo, usuario_id)
        VALUES (v_hub, v_l.producto_id, p_tipo, v_l.cant, v_ex, 'pedido',
                p_pedido_id, p_motivo, ctx_usuario_id());
        v_c := v_c + 1;
    END LOOP;
    RETURN v_c;
END;
$$;
COMMENT ON FUNCTION fn_devolver_inventario IS 'RN18. Una sola función para cancelación y entrega parcial, para que no existan dos caminos que devuelvan cantidades distintas (HU21 CA3: sin duplicar movimientos).';

-- ---------------------------------------------------------------------
-- 12. Indicadores — RF19, HU25 CA1 (datos transaccionales, no simulados)
-- ---------------------------------------------------------------------

CREATE OR REPLACE VIEW v_indicadores_zona AS
SELECT z.id AS zona_id, z.nombre AS zona, z.colonia,
       date_trunc('day', p.creado_en)::date AS dia,
       count(*)                                            AS pedidos,
       count(*) FILTER (WHERE p.estado = 'entregado')       AS entregados,
       count(*) FILTER (WHERE p.estado = 'cancelado')       AS cancelados,
       count(*) FILTER (WHERE p.estado = 'entrega_fallida') AS fallidos,
       round(avg(p.subtotal), 2)                            AS ticket_promedio,
       round(sum(p.total), 2)                               AS venta_total
  FROM pedido p JOIN zona z ON z.id = p.zona_id
 GROUP BY z.id, z.nombre, z.colonia, date_trunc('day', p.creado_en);

CREATE OR REPLACE VIEW v_tasa_entrega AS
SELECT m.id AS microhub_id, m.clave,
       count(*) AS pedidos_cerrados,
       count(*) FILTER (WHERE p.estado = 'entregado') AS entregados,
       round(100.0 * count(*) FILTER (WHERE p.estado = 'entregado')
             / NULLIF(count(*), 0), 2) AS tasa_entrega_pct
  FROM pedido p JOIN microhub m ON m.id = p.microhub_id
 WHERE p.estado IN ('entregado','entrega_parcial','entrega_fallida')
 GROUP BY m.id, m.clave;

-- ---------------------------------------------------------------------
-- 13. Roles de base de datos — RNF23, Matriz de Perfiles
-- El ámbito se resuelve en la consulta; estos roles son la red de abajo.
-- ---------------------------------------------------------------------

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_microhubs') THEN
        CREATE ROLE app_microhubs NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'auditor_microhubs') THEN
        CREATE ROLE auditor_microhubs NOLOGIN;
    END IF;
END $$;

GRANT USAGE ON SCHEMA microhubs TO app_microhubs, auditor_microhubs;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA microhubs TO app_microhubs;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA microhubs TO app_microhubs;

-- RN31: ni la aplicación puede tocar la bitácora una vez escrita.
REVOKE UPDATE, DELETE ON auditoria FROM app_microhubs;

-- El Auditor es de solo lectura por privilegio, no por buena intención
-- del código (recomendación de la Matriz de Perfiles).
GRANT SELECT ON ALL TABLES IN SCHEMA microhubs TO auditor_microhubs;

-- ---------------------------------------------------------------------
-- 14. Ámbito de acceso resuelto en la consulta — RN33, RN26, RNF23
-- La Matriz de Perfiles es explícita: ocultar opciones en pantalla NO es
-- control de acceso. Estas funciones son el punto donde el ámbito se
-- aplica sobre los datos.
-- ---------------------------------------------------------------------

CREATE OR REPLACE FUNCTION fn_pedidos_visibles(p_usuario_id integer)
RETURNS SETOF pedido
LANGUAGE plpgsql STABLE AS $$
DECLARE v_rol varchar; v_hub integer; v_cli integer;
BEGIN
    SELECT r.clave, u.microhub_id INTO v_rol, v_hub
      FROM usuario u JOIN rol r ON r.id = u.rol_id WHERE u.id = p_usuario_id;

    IF v_rol IN ('administrador', 'auditor', 'planeador') THEN
        RETURN QUERY SELECT p.* FROM pedido p;                 -- ámbito total

    ELSIF v_rol = 'operador' THEN
        -- RN22: únicamente los microhubs que tenga asignados.
        RETURN QUERY SELECT p.* FROM pedido p WHERE p.microhub_id = v_hub;

    ELSIF v_rol = 'cliente' THEN
        SELECT c.id INTO v_cli FROM cliente c WHERE c.usuario_id = p_usuario_id;
        RETURN QUERY SELECT p.* FROM pedido p WHERE p.cliente_id = v_cli;

    ELSIF v_rol = 'repartidor' THEN
        -- RN25: solo las entregas de su turno vigente.
        RETURN QUERY SELECT p.* FROM pedido p JOIN entrega e ON e.pedido_id = p.id
                      WHERE e.repartidor_id = p_usuario_id
                        AND e.turno_fecha = current_date
                        AND e.cierre_en IS NULL;
    ELSE
        RETURN;                                                -- sin ámbito
    END IF;
END;
$$;

CREATE OR REPLACE FUNCTION fn_domicilio_entrega(p_entrega_id bigint, p_usuario_id integer)
RETURNS varchar
LANGUAGE plpgsql AS $$
DECLARE v_e record; v_dir varchar;
BEGIN
    SELECT e.repartidor_id, e.cierre_en, e.turno_fecha, e.pedido_id INTO v_e
      FROM entrega e WHERE e.id = p_entrega_id;

    -- RN26: la ventana es la entrega ACTIVA. Cerrada la entrega o el turno,
    -- el domicilio completo deja de estar disponible para ese perfil.
    IF NOT FOUND OR v_e.repartidor_id IS DISTINCT FROM p_usuario_id
       OR v_e.cierre_en IS NOT NULL OR v_e.turno_fecha <> current_date THEN
        PERFORM fn_auditar('entregas', 'acceso_denegado', 'entrega', p_entrega_id::varchar,
                           NULL, NULL, 'RN26: acceso al domicilio fuera de la ventana de entrega activa.', false);
        RETURN NULL;
    END IF;

    SELECT d.calle || ' ' || d.numero_ext || ', ' || d.colonia || ', CP ' || d.codigo_postal
      INTO v_dir
      FROM pedido p JOIN domicilio d ON d.id = p.domicilio_id WHERE p.id = v_e.pedido_id;

    -- RN26: el acceso concedido también queda auditado.
    PERFORM fn_auditar('entregas', 'modificacion', 'entrega', p_entrega_id::varchar,
                       NULL, NULL, 'Acceso autorizado al domicilio durante entrega activa.');
    RETURN v_dir;
END;
$$;
COMMENT ON FUNCTION fn_domicilio_entrega IS 'RN26, RNF19, VR-14. El ámbito del Repartidor es el único con dimensión temporal del sistema.';

-- ---------------------------------------------------------------------
-- 15. Auditoría garantizada por el motor — RN30
--
-- Hallazgo durante la validación: con fn_auditar como única vía, la
-- bitácora quedaba vacía porque depende de que la aplicación se acuerde
-- de invocarla. RN30 dice "TODA operación de escritura deberá generar un
-- registro de auditoría", y una regla que depende de la disciplina del
-- programador no es una garantía.
--
-- Se aplica el mismo criterio que ya se usó con historial_estatus: el
-- trigger lo hace, no el código de aplicación. fn_auditar sigue
-- existiendo para los eventos que NO son escrituras de tabla (login,
-- logout, acceso denegado), donde no hay fila que observar.
-- ---------------------------------------------------------------------

CREATE OR REPLACE FUNCTION fn_auditar_cambio() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER AS $$
DECLARE
    v_accion accion_auditoria;
    v_ant    jsonb;
    v_nue    jsonb;
    v_id     text;
    v_modulo varchar := COALESCE(TG_ARGV[0], TG_TABLE_NAME);
BEGIN
    IF TG_OP = 'INSERT' THEN
        v_accion := 'alta';       v_nue := to_jsonb(NEW);
    ELSIF TG_OP = 'UPDATE' THEN
        v_ant := to_jsonb(OLD);   v_nue := to_jsonb(NEW);
        -- Solo se guardan los campos que efectivamente cambiaron: una
        -- bitácora que copia la fila entera en cada UPDATE es ilegible.
        SELECT jsonb_object_agg(k, v_ant -> k) INTO v_ant
          FROM jsonb_each(v_nue) AS e(k, v)
         WHERE v_ant -> k IS DISTINCT FROM v_nue -> k;
        SELECT jsonb_object_agg(k, v) INTO v_nue
          FROM jsonb_each(to_jsonb(NEW)) AS e(k, v)
         WHERE to_jsonb(OLD) -> k IS DISTINCT FROM v;
        IF v_nue IS NULL THEN
            RETURN NULL;                       -- UPDATE que no cambió nada
        END IF;
        v_accion := CASE
            WHEN v_nue ? 'estado'  THEN 'cambio_estado'
            WHEN v_nue ? 'fecha_baja' OR v_nue ? 'estatus' THEN 'baja_logica'
            ELSE 'modificacion' END;
    ELSE
        v_accion := 'baja_logica'; v_ant := to_jsonb(OLD);
    END IF;

    -- RNF34: la bitácora nunca conserva material de credenciales.
    v_ant := v_ant - 'hash_contrasena';
    v_nue := v_nue - 'hash_contrasena';

    v_id := COALESCE((to_jsonb(COALESCE(NEW, OLD)) ->> 'id'),
                     (to_jsonb(COALESCE(NEW, OLD)) ->> 'microhub_id'));

    INSERT INTO auditoria (usuario_id, fecha, ip_origen, modulo, accion,
                           entidad, entidad_id, valores_anteriores, valores_nuevos)
    VALUES (ctx_usuario_id(), now(),
            NULLIF(current_setting('app.ip_origen', true), '')::inet,
            v_modulo, v_accion, TG_TABLE_NAME, v_id, v_ant, v_nue);
    RETURN NULL;
END;
$$;
COMMENT ON FUNCTION fn_auditar_cambio IS 'RN30. Auditoría automática por trigger. Diferencial: guarda solo los campos que cambiaron.';

-- Tablas bajo auditoría obligatoria. Se excluyen a propósito:
--   auditoria (recursión), historial_estatus y movimiento_inventario
--   (ya son bitácoras de por sí; auditarlas duplicaría el mismo hecho).
DO $$
DECLARE t text; m text;
BEGIN
    FOR t, m IN
        SELECT * FROM (VALUES
            ('usuario','usuarios'), ('rol','roles'), ('rol_permiso','roles'),
            ('cliente','clientes'), ('domicilio','clientes'),
            ('zona','zonas'), ('microhub','microhubs'),
            ('categoria','catalogo'), ('producto','catalogo'),
            ('inventario','inventario'),
            ('pedido','pedidos'), ('pedido_detalle','pedidos'),
            ('decision_asignacion','pedidos'),
            ('entrega','entregas'), ('entrega_linea','entregas'),
            ('configuracion','configuracion'),
            ('transicion_permitida','configuracion')
        ) AS x(tabla, modulo)
    LOOP
        EXECUTE format(
            'CREATE OR REPLACE TRIGGER trg_aud_%1$s AFTER INSERT OR UPDATE OR DELETE ON %1$I '
            'FOR EACH ROW EXECUTE FUNCTION fn_auditar_cambio(%2$L)', t, m);
    END LOOP;
END $$;
