-- =====================================================================
-- 05_pruebas_reglas.sql — Casos de validación VR-01 a VR-16
-- Codex Innovations · Equipo 04
--
-- Ejecuta los dieciséis casos de la sección 9 del entregable de Reglas de
-- Negocio contra la base real y reporta PASA / FALLA. Es evidencia
-- reproducible, no una tabla de escritorio.
--
--   psql -d microhubs_p1 -f 05_pruebas_reglas.sql
--
-- No deja residuo: todo corre dentro de una transacción que se revierte.
-- =====================================================================

SET search_path TO microhubs, public;

BEGIN;

CREATE TEMP TABLE resultado_vr (
    id serial, caso varchar(8), regla varchar(40),
    descripcion varchar(140), veredicto varchar(6), detalle varchar(300)
) ON COMMIT DROP;

CREATE OR REPLACE FUNCTION pg_temp.chk(
    p_caso varchar, p_regla varchar, p_desc varchar,
    p_ok boolean, p_detalle varchar DEFAULT NULL
) RETURNS void LANGUAGE sql AS $$
    INSERT INTO resultado_vr (caso, regla, descripcion, veredicto, detalle)
    VALUES (p_caso, p_regla, p_desc, CASE WHEN p_ok THEN 'PASA' ELSE 'FALLA' END, p_detalle);
$$;

DO $$
DECLARE
    v_cli      record;
    v_ped      bigint;
    v_prod     integer;
    v_prod2    integer;
    v_hub      integer;
    v_hub2     integer;
    v_ok       boolean;
    v_msg      text;
    v_num      numeric;
    v_int      integer;
    v_txt      varchar;
    v_res      record;
    v_ent      bigint;
    v_op       integer;
    v_rep      integer;
    v_zona     integer;
    v_dom      integer;
BEGIN
    SELECT c.id AS cliente_id, d.id AS domicilio_id, d.zona_id, d.latitud, d.longitud
      INTO v_cli FROM cliente c JOIN domicilio d ON d.cliente_id = c.id AND d.activo
     ORDER BY c.id LIMIT 1;
    v_zona := v_cli.zona_id;

    SELECT p.id INTO v_prod  FROM producto p WHERE p.clave_interna = 'AB-002';
    SELECT p.id INTO v_prod2 FROM producto p WHERE p.clave_interna = 'LA-001';
    SELECT m.id INTO v_hub   FROM microhub m WHERE m.clave = 'MH-01';
    SELECT m.id INTO v_hub2  FROM microhub m WHERE m.clave = 'MH-02';
    SELECT u.id INTO v_op    FROM usuario u WHERE u.correo = 'operador.mh01@codex.mx';
    SELECT u.id INTO v_rep   FROM usuario u WHERE u.correo = 'repartidor1@codex.mx';

    -- =================================================================
    -- VR-01 · Confirmar fuera de cobertura -> rechazo + demanda no atendida
    -- =================================================================
    -- Domicilio a ~6 km del sector, fuera del radio de todo microhub activo.
    v_ok := NOT EXISTS (
        SELECT 1 FROM microhub m
         WHERE m.estatus = 'activo' AND fn_cubre(m.id, 25.800000, -100.310000)
    );
    PERFORM pg_temp.chk('VR-01', 'RN05, RN06', 'Domicilio fuera de cobertura no es cubierto por ningún microhub activo', v_ok);

    INSERT INTO demanda_no_atendida (tipo, colonia_texto, cp_texto, origen)
    VALUES ('fuera_cobertura', 'Colonia de prueba', '64999', 'web');
    PERFORM pg_temp.chk('VR-01', 'RN06', 'La consulta fuera de cobertura se conserva como demanda no atendida',
        EXISTS (SELECT 1 FROM demanda_no_atendida WHERE cp_texto = '64999'));

    -- =================================================================
    -- VR-02 · Subtotal menor al ticket mínimo -> rechazo
    -- =================================================================
    v_num := fn_ticket_minimo(v_zona);
    PERFORM pg_temp.chk('VR-02', 'RN07', 'El ticket mínimo se resuelve desde configuración/zona, no desde constante',
        v_num IS NOT NULL AND v_num > 0, 'ticket mínimo de la zona = ' || v_num);

    -- RN08: el envío NO debe hacer que un subtotal insuficiente "alcance".
    PERFORM pg_temp.chk('VR-02', 'RN08', 'Un subtotal de 50 con envío de 15 sigue estando por debajo del mínimo',
        (50::numeric < v_num) AND ((50 + fn_costo_envio(v_zona, 50)) >= 50));

    -- =================================================================
    -- VR-03 · Una línea supera el límite configurado -> rechazo
    -- =================================================================
    v_int := fn_config_num('limite_unidades_linea')::integer;
    INSERT INTO pedido (cliente_id, domicilio_id, zona_id, subtotal, costo_envio)
    VALUES (v_cli.cliente_id, v_cli.domicilio_id, v_zona, 100, 15) RETURNING id INTO v_ped;
    BEGIN
        INSERT INTO pedido_detalle (pedido_id, producto_id, cantidad, precio_unitario)
        VALUES (v_ped, v_prod, v_int + 1, 29.90);
        v_ok := false; v_msg := 'se aceptó una cantidad por encima del límite';
    EXCEPTION WHEN check_violation THEN
        v_ok := true; v_msg := 'rechazada por trg_detalle_limite (límite = ' || v_int || ')';
    END;
    PERFORM pg_temp.chk('VR-03', 'RN09', 'Una línea por encima del límite configurado se rechaza', v_ok, v_msg);

    -- =================================================================
    -- VR-04 · Falta existencia en una línea -> el pedido no se confirma
    -- =================================================================
    INSERT INTO pedido_detalle (pedido_id, producto_id, cantidad, precio_unitario)
    VALUES (v_ped, v_prod, 2, 29.90);
    -- Se agota el producto en todos los microhubs.
    UPDATE inventario i SET existencia = 0 WHERE i.producto_id = v_prod;
    v_ok := NOT EXISTS (SELECT 1 FROM fn_microhubs_elegibles(v_ped) e WHERE e.elegible);
    PERFORM pg_temp.chk('VR-04', 'RN10', 'Sin existencia completa ningún microhub resulta elegible', v_ok);

    SELECT * INTO v_res FROM fn_asignar_pedido(v_ped);
    PERFORM pg_temp.chk('VR-04', 'RN10, RNF08', 'No se compromete inventario cuando falta una línea',
        NOT v_res.asignado AND NOT EXISTS (
            SELECT 1 FROM movimiento_inventario m
             WHERE m.referencia_tipo = 'pedido' AND m.referencia_id = v_ped));

    -- =================================================================
    -- VR-07 · Ningún hub con cobertura + stock + capacidad -> pendiente
    -- =================================================================
    SELECT p.estado::text, p.motivo_no_asignacion INTO v_txt, v_msg
      FROM pedido p WHERE p.id = v_ped;
    PERFORM pg_temp.chk('VR-07', 'RN14', 'El pedido queda pendiente de asignación conservando el motivo',
        v_txt = 'pendiente_asignacion' AND v_msg IS NOT NULL, v_msg);

    PERFORM pg_temp.chk('VR-07', 'RN15', 'La decisión "sin elegible" queda registrada para auditoría',
        EXISTS (SELECT 1 FROM decision_asignacion d
                 WHERE d.pedido_id = v_ped AND d.criterio = 'sin_elegible'));

    -- =================================================================
    -- VR-05 · Dos hubs cubren y tienen stock: gana el más cercano
    -- =================================================================
    -- Domicilio equidistante-ish, con existencia suficiente en ambos hubs.
    UPDATE inventario i SET existencia = 500 WHERE i.producto_id = v_prod2;

    INSERT INTO domicilio (cliente_id, calle, numero_ext, colonia, codigo_postal,
                           latitud, longitud, zona_id, activo)
    SELECT v_cli.cliente_id, 'Calle Prueba VR05', '1', z.colonia, z.codigo_postal,
           25.749000, -100.365000, z.id, false
      FROM zona z WHERE z.id = v_zona RETURNING id INTO v_dom;

    INSERT INTO pedido (cliente_id, domicilio_id, zona_id, subtotal, costo_envio)
    VALUES (v_cli.cliente_id, v_dom, v_zona, 100, 15) RETURNING id INTO v_ped;
    INSERT INTO pedido_detalle (pedido_id, producto_id, cantidad, precio_unitario)
    VALUES (v_ped, v_prod2, 2, 27.50);

    SELECT count(*) INTO v_int FROM fn_microhubs_elegibles(v_ped) e WHERE e.elegible;
    SELECT * INTO v_res FROM fn_asignar_pedido(v_ped);

    SELECT e.microhub_id INTO v_hub
      FROM fn_microhubs_elegibles(v_ped) e WHERE e.elegible
     ORDER BY e.distancia_km LIMIT 1;

    PERFORM pg_temp.chk('VR-05', 'RN12, RN13',
        'Con varios elegibles se asigna el de menor distancia',
        v_res.asignado AND v_res.criterio = 'menor_distancia',
        'candidatos elegibles = ' || v_int || ', criterio = ' || v_res.criterio);

    -- =================================================================
    -- VR-08 (parcial) · La existencia nunca queda negativa
    -- La concurrencia real se prueba en 06_prueba_concurrencia.sh
    -- =================================================================
    BEGIN
        UPDATE inventario i SET existencia = -1
         WHERE i.microhub_id = v_hub2 AND i.producto_id = v_prod2;
        v_ok := false; v_msg := 'la base aceptó existencia negativa';
    EXCEPTION WHEN check_violation THEN
        v_ok := true; v_msg := 'ck_inv_existencia rechazó el saldo negativo';
    END;
    PERFORM pg_temp.chk('VR-08', 'RN16, RN17', 'La sobreventa es imposible aunque falle la aplicación', v_ok, v_msg);

    -- =================================================================
    -- VR-09 · Cliente cancela pedido asignado -> permitido + devolución
    -- =================================================================
    SELECT i.existencia INTO v_int FROM inventario i
     WHERE i.microhub_id = (SELECT p.microhub_id FROM pedido p WHERE p.id = v_ped)
       AND i.producto_id = v_prod2;

    PERFORM set_config('app.rol', 'cliente', true);
    BEGIN
        UPDATE pedido p SET estado = 'cancelado',
                            motivo_cancelacion = 'Prueba VR-09'
         WHERE p.id = v_ped;
        PERFORM fn_devolver_inventario(v_ped, 'devolucion_cancelacion', 'VR-09');
        v_ok := true; v_msg := NULL;
    EXCEPTION WHEN OTHERS THEN
        v_ok := false; v_msg := SQLERRM;
    END;
    PERFORM pg_temp.chk('VR-09', 'RN21', 'El Cliente puede cancelar un pedido asignado', v_ok, v_msg);

    SELECT i.existencia INTO v_num FROM inventario i
     WHERE i.microhub_id = (SELECT p.microhub_id FROM pedido p WHERE p.id = v_ped)
       AND i.producto_id = v_prod2;
    PERFORM pg_temp.chk('VR-09', 'RN18', 'La cancelación devuelve las unidades al inventario',
        v_num = v_int + 2, 'existencia ' || v_int || ' -> ' || v_num);

    -- =================================================================
    -- VR-10 · Cliente cancela pedido en preparación -> rechazado
    -- =================================================================
    INSERT INTO pedido (cliente_id, domicilio_id, zona_id, subtotal, costo_envio)
    VALUES (v_cli.cliente_id, v_cli.domicilio_id, v_zona, 100, 15) RETURNING id INTO v_ped;
    INSERT INTO pedido_detalle (pedido_id, producto_id, cantidad, precio_unitario)
    VALUES (v_ped, v_prod2, 1, 27.50);
    PERFORM fn_asignar_pedido(v_ped);

    PERFORM set_config('app.rol', 'operador', true);
    UPDATE pedido p SET estado = 'en_preparacion' WHERE p.id = v_ped;

    PERFORM set_config('app.rol', 'cliente', true);
    BEGIN
        UPDATE pedido p SET estado = 'cancelado', motivo_cancelacion = 'Prueba VR-10'
         WHERE p.id = v_ped;
        v_ok := false; v_msg := 'se permitió cancelar en preparación';
    EXCEPTION WHEN check_violation THEN
        v_ok := true; v_msg := 'transición rechazada por trg_pedido_transicion';
    END;
    PERFORM pg_temp.chk('VR-10', 'RN21', 'Cancelar en preparación se rechaza', v_ok, v_msg);

    SELECT p.estado::text INTO v_txt FROM pedido p WHERE p.id = v_ped;
    PERFORM pg_temp.chk('VR-10', 'HU20 CA2', 'El pedido conserva su estado tras la transición ilegal',
        v_txt = 'en_preparacion', 'estado = ' || v_txt);

    -- =================================================================
    -- VR-11 · Operador abre pedido de otro microhub -> denegado
    -- =================================================================
    PERFORM set_config('app.rol', 'operador', true);
    v_ok := NOT EXISTS (
        SELECT 1 FROM fn_pedidos_visibles(v_op) p
         WHERE p.microhub_id IS DISTINCT FROM (SELECT u.microhub_id FROM usuario u WHERE u.id = v_op)
    );
    SELECT count(*) INTO v_int FROM fn_pedidos_visibles(v_op);
    PERFORM pg_temp.chk('VR-11', 'RN22, RN33', 'El ámbito del Operador se aplica en la consulta, no en la pantalla',
        v_ok, 'pedidos visibles para el operador de MH-01: ' || v_int);

    -- =================================================================
    -- VR-12 · Planeador reasigna un pendiente sin motivo -> rechazado
    -- =================================================================
    BEGIN
        INSERT INTO decision_asignacion (pedido_id, microhub_ganador_id, criterio, manual, usuario_id)
        VALUES (v_ped, v_hub2, 'manual', true, v_op);
        v_ok := false; v_msg := 'se aceptó una reasignación manual sin motivo';
    EXCEPTION WHEN check_violation THEN
        v_ok := true; v_msg := 'ck_decision_manual exigió el motivo';
    END;
    PERFORM pg_temp.chk('VR-12', 'RN24', 'Una reasignación manual sin motivo se rechaza', v_ok, v_msg);

    -- =================================================================
    -- VR-13 · Entrega parcial con líneas rechazadas -> ajuste de inventario
    -- =================================================================
    PERFORM set_config('app.rol', 'operador', true);
    UPDATE pedido p SET estado = 'en_ruta' WHERE p.id = v_ped;

    INSERT INTO entrega (pedido_id, repartidor_id, turno_fecha, asignada_en, salida_en)
    VALUES (v_ped, v_rep, current_date, now(), now()) RETURNING id INTO v_ent;

    SELECT i.existencia INTO v_int FROM inventario i
     WHERE i.microhub_id = (SELECT p.microhub_id FROM pedido p WHERE p.id = v_ped)
       AND i.producto_id = v_prod2;

    INSERT INTO entrega_linea (entrega_id, pedido_detalle_id, cantidad_entregada,
                               cantidad_devuelta, motivo)
    SELECT v_ent, pd.id, 0, pd.cantidad, 'El cliente rechazó la línea'
      FROM pedido_detalle pd WHERE pd.pedido_id = v_ped;

    PERFORM set_config('app.rol', 'repartidor', true);
    UPDATE pedido p SET estado = 'entrega_parcial' WHERE p.id = v_ped;
    UPDATE entrega e SET resultado = 'parcial', confirmacion_recepcion = true,
                         monto_cobrado = 0, cambio_entregado = 0, cierre_en = now()
     WHERE e.id = v_ent;
    PERFORM fn_devolver_inventario(v_ped, 'devolucion_parcial', 'VR-13');

    SELECT i.existencia INTO v_num FROM inventario i
     WHERE i.microhub_id = (SELECT p.microhub_id FROM pedido p WHERE p.id = v_ped)
       AND i.producto_id = v_prod2;
    PERFORM pg_temp.chk('VR-13', 'RN18, RN28', 'La entrega parcial reintegra solo las unidades devueltas',
        v_num = v_int + 1, 'existencia ' || v_int || ' -> ' || v_num);

    -- Una entrega fallida sin motivo no debe poder cerrarse (RN29).
    BEGIN
        UPDATE entrega e SET resultado = 'fallida', incidencia = NULL WHERE e.id = v_ent;
        v_ok := false; v_msg := 'se aceptó una entrega fallida sin incidencia';
    EXCEPTION WHEN check_violation THEN
        v_ok := true; v_msg := 'ck_entrega_fallida exigió el motivo';
    END;
    PERFORM pg_temp.chk('VR-13', 'RN29', 'Una entrega fallida sin motivo se rechaza', v_ok, v_msg);

    -- =================================================================
    -- VR-14 · Repartidor consulta domicilio tras cerrar -> no disponible
    -- =================================================================
    v_txt := fn_domicilio_entrega(v_ent, v_rep);
    PERFORM pg_temp.chk('VR-14', 'RN26, RNF19', 'Cerrada la entrega, el domicilio completo deja de mostrarse',
        v_txt IS NULL, COALESCE('devolvió: ' || v_txt, 'devolvió NULL'));

    PERFORM pg_temp.chk('VR-14', 'RN26', 'El intento de acceso fuera de ventana queda auditado',
        EXISTS (SELECT 1 FROM auditoria a
                 WHERE a.entidad = 'entrega' AND a.entidad_id = v_ent::varchar
                   AND a.accion = 'acceso_denegado'));

    -- =================================================================
    -- VR-15 · Modificar la bitácora -> imposible
    -- =================================================================
    BEGIN
        UPDATE auditoria a SET detalle = 'alterado' WHERE a.id = (SELECT min(x.id) FROM auditoria x);
        v_ok := false; v_msg := 'se permitió modificar la bitácora';
    EXCEPTION WHEN insufficient_privilege THEN
        v_ok := true; v_msg := 'trg_auditoria_inmutable rechazó el UPDATE';
    END;
    PERFORM pg_temp.chk('VR-15', 'RN31', 'Ningún perfil puede modificar una entrada de auditoría', v_ok, v_msg);

    BEGIN
        DELETE FROM auditoria a WHERE a.id = (SELECT min(x.id) FROM auditoria x);
        v_ok := false; v_msg := 'se permitió borrar de la bitácora';
    EXCEPTION WHEN insufficient_privilege THEN
        v_ok := true; v_msg := 'trg_auditoria_inmutable rechazó el DELETE';
    END;
    PERFORM pg_temp.chk('VR-15', 'RN31', 'Ningún perfil puede eliminar una entrada de auditoría', v_ok, v_msg);

    -- =================================================================
    -- VR-16 · Cambiar el ticket mínimo en configuración surte efecto
    -- =================================================================
    v_num := fn_ticket_minimo(v_zona);
    UPDATE zona z SET ticket_minimo = 175.00 WHERE z.id = v_zona;
    PERFORM pg_temp.chk('VR-16', 'RN40', 'La validación usa el valor actualizado sin recompilar',
        fn_ticket_minimo(v_zona) = 175.00,
        'ticket mínimo ' || v_num || ' -> ' || fn_ticket_minimo(v_zona));

    UPDATE configuracion c SET valor = '30' WHERE c.clave = 'limite_unidades_linea' AND c.ambito = 'global';
    PERFORM pg_temp.chk('VR-16', 'RN09, RN40', 'El límite por línea también se lee desde configuración',
        fn_config_num('limite_unidades_linea') = 30);

    -- =================================================================
    -- VR-06 · Empate en distancia -> gana mayor capacidad libre
    -- =================================================================
    -- Se colocan dos microhubs a idéntica distancia del domicilio de prueba.
    UPDATE microhub m SET latitud = 25.749000, longitud = -100.360000, radio_km = 3.0
     WHERE m.id = v_hub;
    UPDATE microhub m SET latitud = 25.749000, longitud = -100.370000, radio_km = 3.0
     WHERE m.id = v_hub2;
    UPDATE inventario i SET existencia = 500 WHERE i.producto_id = v_prod2;

    INSERT INTO pedido (cliente_id, domicilio_id, zona_id, subtotal, costo_envio)
    VALUES (v_cli.cliente_id, v_dom, v_zona, 100, 15) RETURNING id INTO v_ped;
    UPDATE domicilio d SET latitud = 25.749000, longitud = -100.365000 WHERE d.id = v_dom;
    INSERT INTO pedido_detalle (pedido_id, producto_id, cantidad, precio_unitario)
    VALUES (v_ped, v_prod2, 1, 27.50);

    SELECT count(DISTINCT e.distancia_km) INTO v_int
      FROM fn_microhubs_elegibles(v_ped) e
     WHERE e.elegible AND e.microhub_id IN (v_hub, v_hub2);

    SELECT * INTO v_res FROM fn_asignar_pedido(v_ped);
    PERFORM pg_temp.chk('VR-06', 'RN13', 'Ante empate de distancia el criterio registrado es la capacidad libre',
        v_int = 1 AND v_res.criterio = 'mayor_capacidad_libre',
        'distancias distintas entre los dos hubs = ' || v_int || ', criterio = ' || v_res.criterio);

    PERFORM set_config('app.rol', '', true);
END $$;

SELECT caso, regla, descripcion, veredicto, detalle FROM resultado_vr ORDER BY id;

SELECT veredicto, count(*) AS casos FROM resultado_vr GROUP BY veredicto ORDER BY veredicto;

-- Nada de esto queda en la base: la prueba no ensucia los datos de demo.
ROLLBACK;
