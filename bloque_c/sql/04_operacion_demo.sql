-- =====================================================================
-- 04_operacion_demo.sql — Operación histórica para indicadores y pruebas
-- Codex Innovations · Equipo 04
--
-- Los pedidos NO se insertan ya resueltos: se crean y se pasan por
-- fn_asignar_pedido y por la máquina de estados real. Si una regla está
-- mal implementada, este script falla en lugar de producir datos bonitos
-- que esconden el error.
--
-- Requisito de HU25 CA1: los indicadores deben calcularse desde datos
-- transaccionales reales, no desde valores simulados en la interfaz.
-- =====================================================================

SET search_path TO microhubs, public;

DO $$
DECLARE
    N_PEDIDOS constant integer := 180;
    N_DIAS    constant integer := 45;

    v_cli        record;
    v_prod       record;
    v_pedido_id  bigint;
    v_zona       integer;
    v_subtotal   numeric;
    v_ticket     numeric;
    v_lineas     integer;
    v_res        record;
    v_dado       numeric;
    v_fecha      timestamptz;
    v_rep        integer;
    v_entrega    bigint;
    v_total      numeric;
    v_pagado     numeric;
    v_devueltas  integer;
    i            integer;
    v_creados    integer := 0;
    v_rechazados integer := 0;
    v_pendientes integer := 0;
BEGIN
    PERFORM setseed(0.2604);
    SELECT u.id INTO v_rep FROM usuario u JOIN rol r ON r.id = u.rol_id
     WHERE r.clave = 'repartidor' ORDER BY u.id LIMIT 1;

    FOR i IN 1..N_PEDIDOS LOOP
        -- Cliente al azar con su domicilio activo (RN03).
        SELECT c.id AS cliente_id, d.id AS domicilio_id, d.zona_id
          INTO v_cli
          FROM cliente c
          JOIN domicilio d ON d.cliente_id = c.id AND d.activo
         ORDER BY random() LIMIT 1;

        v_zona := v_cli.zona_id;
        v_fecha := now() - (random() * N_DIAS || ' days')::interval
                         - (random() * 12 || ' hours')::interval;

        -- Carrito: 1 a 5 líneas distintas. Se arma FUERA del pedido, igual
        -- que en la aplicación: un carrito no es un pedido, y un pedido que
        -- no pasó validaciones nunca debe llegar a existir. La FK del
        -- historial de estatus lo garantiza: un pedido creado ya no se puede
        -- borrar sin destruir trazabilidad (RN32).
        v_lineas := 2 + floor(random() * 5)::integer;

        DROP TABLE IF EXISTS tmp_carrito;
        CREATE TEMP TABLE tmp_carrito AS
        SELECT p.id AS producto_id, p.precio,
               (1 + floor(random() * 5))::integer AS cantidad
          FROM producto p WHERE p.estatus = 'activo'
         ORDER BY random() LIMIT v_lineas;

        SELECT COALESCE(sum(precio * cantidad), 0) INTO v_subtotal FROM tmp_carrito;
        v_ticket := fn_ticket_minimo(v_zona);

        -- RN07/RN08: el ticket mínimo se valida contra el subtotal de
        -- productos, nunca contra el total con envío. Si no alcanza, el
        -- pedido no se confirma y la intención se conserva como demanda
        -- no atendida (RN06).
        IF v_subtotal < v_ticket THEN
            INSERT INTO demanda_no_atendida (tipo, zona_id, cliente_id, origen, fecha)
            VALUES ('bajo_ticket_minimo', v_zona, v_cli.cliente_id, 'web', v_fecha);
            v_rechazados := v_rechazados + 1;
            CONTINUE;
        END IF;

        INSERT INTO pedido (cliente_id, domicilio_id, zona_id, estado, subtotal, costo_envio)
        VALUES (v_cli.cliente_id, v_cli.domicilio_id, v_zona, 'creado',
                v_subtotal, fn_costo_envio(v_zona, v_subtotal))
        RETURNING id INTO v_pedido_id;

        -- RN04: el precio se copia, no se referencia.
        INSERT INTO pedido_detalle (pedido_id, producto_id, cantidad, precio_unitario)
        SELECT v_pedido_id, producto_id, cantidad, precio FROM tmp_carrito;

        -- Motor real de asignación (RN12-RN17).
        SELECT * INTO v_res FROM fn_asignar_pedido(v_pedido_id);

        IF NOT v_res.asignado THEN
            -- RN14: queda pendiente con motivo, sin descontar inventario.
            INSERT INTO demanda_no_atendida (tipo, zona_id, cliente_id, origen, fecha)
            VALUES ('sin_microhub_elegible', v_zona, v_cli.cliente_id, 'web', v_fecha);
            v_pendientes := v_pendientes + 1;
            UPDATE pedido SET creado_en = v_fecha WHERE id = v_pedido_id;
            CONTINUE;
        END IF;

        v_creados := v_creados + 1;
        v_dado := random();

        -- 10% se quedan vivos para poblar la bandeja del operador.
        IF v_dado < 0.10 THEN
            UPDATE pedido SET creado_en = v_fecha, asignado_en = v_fecha
             WHERE id = v_pedido_id;
            CONTINUE;
        END IF;

        -- 7% cancelados por el cliente estando asignados (RN21) con
        -- devolución de inventario (RN18).
        IF v_dado < 0.17 THEN
            PERFORM set_config('app.rol', 'cliente', true);
            UPDATE pedido SET estado = 'cancelado',
                              motivo_cancelacion = 'El cliente canceló antes de la preparación.'
             WHERE id = v_pedido_id;
            PERFORM fn_devolver_inventario(v_pedido_id, 'devolucion_cancelacion',
                                           'Cancelación del cliente (RN18).');
            UPDATE pedido SET creado_en = v_fecha, asignado_en = v_fecha, cerrado_en = v_fecha
             WHERE id = v_pedido_id;
            CONTINUE;
        END IF;

        -- El resto recorre el ciclo completo.
        PERFORM set_config('app.rol', 'operador', true);
        UPDATE pedido SET estado = 'en_preparacion' WHERE id = v_pedido_id;
        UPDATE pedido SET estado = 'en_ruta'        WHERE id = v_pedido_id;

        SELECT total INTO v_total FROM pedido WHERE id = v_pedido_id;

        INSERT INTO entrega (pedido_id, repartidor_id, turno_fecha, asignada_en, salida_en)
        VALUES (v_pedido_id, v_rep, v_fecha::date, v_fecha, v_fecha)
        RETURNING id INTO v_entrega;

        PERFORM set_config('app.rol', 'repartidor', true);

        IF v_dado < 0.25 THEN
            -- Entrega parcial (RN28): se identifican líneas devueltas.
            v_devueltas := 0;
            INSERT INTO entrega_linea (entrega_id, pedido_detalle_id, cantidad_entregada,
                                       cantidad_devuelta, motivo)
            SELECT v_entrega, pd.id, 0, pd.cantidad, 'El cliente rechazó la línea al momento de la entrega.'
              FROM pedido_detalle pd
             WHERE pd.pedido_id = v_pedido_id
             ORDER BY pd.id LIMIT 1;

            SELECT COALESCE(sum(el.cantidad_devuelta * pd.precio_unitario), 0)
              INTO v_pagado
              FROM entrega_linea el JOIN pedido_detalle pd ON pd.id = el.pedido_detalle_id
             WHERE el.entrega_id = v_entrega;

            v_pagado := v_total - v_pagado;

            UPDATE pedido SET estado = 'entrega_parcial' WHERE id = v_pedido_id;
            UPDATE entrega
               SET resultado = 'parcial', confirmacion_recepcion = true,
                   monto_cobrado = v_pagado, cambio_entregado = 0,
                   cierre_en = v_fecha,
                   incidencia = 'Entrega parcial: línea rechazada por el cliente.'
             WHERE id = v_entrega;

            PERFORM fn_devolver_inventario(v_pedido_id, 'devolucion_parcial',
                                           'Líneas no entregadas (RN28).');

        ELSIF v_dado < 0.31 THEN
            -- Entrega fallida (RN29): motivo obligatorio.
            UPDATE pedido SET estado = 'entrega_fallida',
                              motivo_cancelacion = 'Cliente ausente en dos intentos.'
             WHERE id = v_pedido_id;
            UPDATE entrega
               SET resultado = 'fallida', confirmacion_recepcion = false,
                   monto_cobrado = 0, cambio_entregado = 0, cierre_en = v_fecha,
                   incidencia = 'Cliente ausente; domicilio localizado sin respuesta.'
             WHERE id = v_entrega;
            PERFORM fn_devolver_inventario(v_pedido_id, 'devolucion_cancelacion',
                                           'Entrega fallida: la mercancía regresa al microhub.');
        ELSE
            -- Entrega completa con cobro en efectivo y cambio (RN27).
            v_pagado := ceil(v_total / 50.0) * 50.0;
            UPDATE pedido SET estado = 'entregado' WHERE id = v_pedido_id;
            UPDATE entrega
               SET resultado = 'entregado', confirmacion_recepcion = true,
                   monto_cobrado = v_pagado, cambio_entregado = v_pagado - v_total,
                   cierre_en = v_fecha
             WHERE id = v_entrega;
        END IF;

        -- Retrofecha coherente: pedido, historial, movimientos y entrega.
        UPDATE pedido SET creado_en = v_fecha, asignado_en = v_fecha, cerrado_en = v_fecha
         WHERE id = v_pedido_id;
        UPDATE historial_estatus SET fecha = v_fecha WHERE pedido_id = v_pedido_id;
        UPDATE movimiento_inventario SET fecha = v_fecha
         WHERE referencia_tipo = 'pedido' AND referencia_id = v_pedido_id;
    END LOOP;

    PERFORM set_config('app.rol', '', true);

    RAISE NOTICE 'Pedidos confirmados: %  | rechazados por ticket mínimo: %  | pendientes de asignación: %',
        v_creados, v_rechazados, v_pendientes;
END $$;

-- ---------------------------------------------------------------------
-- Caso RN14 con datos reales: un producto agotado en TODOS los microhubs
-- deja sin candidato elegible a cualquier pedido que lo incluya. Sin este
-- bloque el estado 'pendiente_asignacion' no aparecería en la base y la
-- bandeja del Planeador estaría vacía en la demostración.
-- ---------------------------------------------------------------------
DO $$
DECLARE
    v_prod integer;
    v_cli  record;
    v_ped  bigint;
    v_res  record;
    i      integer;
BEGIN
    SELECT p.id INTO v_prod FROM producto p WHERE p.clave_interna = 'BE-001';

    -- Merma total documentada (CU07: los ajustes exigen motivo).
    UPDATE inventario i SET existencia = 0 WHERE i.producto_id = v_prod;
    INSERT INTO movimiento_inventario (microhub_id, producto_id, tipo, cantidad,
                                       existencia_resultante, motivo)
    SELECT i.microhub_id, i.producto_id, 'merma', -1, 0,
           'Agotamiento total de garrafón por falla del proveedor.'
      FROM inventario i WHERE i.producto_id = v_prod;

    FOR i IN 1..3 LOOP
        SELECT c.id AS cliente_id, d.id AS domicilio_id, d.zona_id INTO v_cli
          FROM cliente c JOIN domicilio d ON d.cliente_id = c.id AND d.activo
         ORDER BY random() LIMIT 1;

        INSERT INTO pedido (cliente_id, domicilio_id, zona_id, estado, subtotal, costo_envio)
        VALUES (v_cli.cliente_id, v_cli.domicilio_id, v_cli.zona_id, 'creado', 0, 0)
        RETURNING id INTO v_ped;

        INSERT INTO pedido_detalle (pedido_id, producto_id, cantidad, precio_unitario)
        SELECT v_ped, p.id, 2, p.precio FROM producto p WHERE p.id = v_prod;
        INSERT INTO pedido_detalle (pedido_id, producto_id, cantidad, precio_unitario)
        SELECT v_ped, p.id, 2, p.precio FROM producto p WHERE p.clave_interna = 'AB-001';

        UPDATE pedido pe SET subtotal = (SELECT sum(importe) FROM pedido_detalle d
                                          WHERE d.pedido_id = v_ped),
                             costo_envio = fn_costo_envio(v_cli.zona_id,
                                 (SELECT sum(importe) FROM pedido_detalle d WHERE d.pedido_id = v_ped))
         WHERE pe.id = v_ped;

        SELECT * INTO v_res FROM fn_asignar_pedido(v_ped);
        IF v_res.asignado THEN
            RAISE EXCEPTION 'RN14 no se cumplió: el pedido % se asignó pese a no haber existencia.', v_ped;
        END IF;
    END LOOP;

    RAISE NOTICE 'Casos RN14 generados: 3 pedidos pendientes de asignación con motivo.';
END $$;

-- Comprobación de coherencia: ninguna existencia negativa, ningún total
-- descuadrado, ningún pedido asignado sin movimiento de inventario.
SELECT 'existencias negativas'   AS control, count(*) FROM inventario WHERE existencia < 0
UNION ALL
SELECT 'totales descuadrados',   count(*) FROM pedido p
 WHERE p.total <> p.subtotal + p.costo_envio
UNION ALL
SELECT 'subtotal vs detalle',    count(*) FROM pedido p
 WHERE p.estado <> 'creado'
   AND p.subtotal <> (SELECT COALESCE(sum(importe),0) FROM pedido_detalle d WHERE d.pedido_id = p.id)
UNION ALL
SELECT 'asignados sin movimiento', count(*) FROM pedido p
 WHERE p.microhub_id IS NOT NULL
   AND NOT EXISTS (SELECT 1 FROM movimiento_inventario m
                    WHERE m.referencia_tipo='pedido' AND m.referencia_id = p.id)
UNION ALL
SELECT 'pendientes sin motivo',  count(*) FROM pedido
 WHERE estado = 'pendiente_asignacion' AND motivo_no_asignacion IS NULL
UNION ALL
SELECT 'transiciones sin historial', count(*) FROM pedido p
 WHERE NOT EXISTS (SELECT 1 FROM historial_estatus h WHERE h.pedido_id = p.id);
