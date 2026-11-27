-- =====================================================================
-- 12_rendimiento.sql — Correcciones de rendimiento encontradas con datos de alto volumen (entrega final)
-- Codex Innovations · Equipo 04
--
-- Idempotente: se puede aplicar las veces que sea (servicios/migrar.py lo aplica a volúmenes existentes).
-- Medición antes y después: evidencias/volumen/RESULTADOS.md.
--
-- Hallazgo 1. fn_pedidos_visibles estaba escrita en PL/pgSQL. PostgreSQL no puede ver dentro de una función PL/pgSQL:
--   la ejecuta completa, materializa TODOS los pedidos del ámbito y hasta después aplica el filtro, el orden y el LIMIT.
--   Con 100 000 pedidos, «dame el pedido 5» o «la página 1 de entregados» leían los 100 000 cada vez (57 ms en la base y
--   128 ms en la API, creciendo en línea recta con la tabla).
--   Ahora es una función SQL de un solo SELECT (UNION ALL de las cuatro reglas de ámbito), que el planificador
--   «desenrolla» dentro de la consulta que la llama: el filtro y el LIMIT llegan hasta los índices de pedido.
--   El rol se resuelve una sola vez por consulta (InitPlan) y las ramas que no aplican ni se ejecutan.
--   Las reglas son exactamente las mismas (RN22, RN25, RN33): administrador, auditor y planeador ven todo; el operador
--   su microhub; el cliente los suyos; el repartidor las entregas abiertas de su turno; cualquier otro rol, nada.
-- =====================================================================
SET search_path = microhubs, public;

CREATE OR REPLACE FUNCTION fn_pedidos_visibles(p_usuario_id integer)
RETURNS SETOF pedido
LANGUAGE sql STABLE AS $$
    SELECT p.* FROM pedido p
     WHERE (SELECT r.clave FROM usuario u JOIN rol r ON r.id = u.rol_id WHERE u.id = p_usuario_id)
           IN ('administrador', 'auditor', 'planeador')                          -- ámbito total
    UNION ALL
    SELECT p.* FROM pedido p
     WHERE (SELECT r.clave FROM usuario u JOIN rol r ON r.id = u.rol_id WHERE u.id = p_usuario_id) = 'operador'
       AND p.microhub_id = (SELECT u.microhub_id FROM usuario u WHERE u.id = p_usuario_id)     -- RN22
    UNION ALL
    SELECT p.* FROM pedido p
     WHERE (SELECT r.clave FROM usuario u JOIN rol r ON r.id = u.rol_id WHERE u.id = p_usuario_id) = 'cliente'
       AND p.cliente_id = (SELECT c.id FROM cliente c WHERE c.usuario_id = p_usuario_id)
    UNION ALL
    SELECT p.* FROM pedido p
     WHERE (SELECT r.clave FROM usuario u JOIN rol r ON r.id = u.rol_id WHERE u.id = p_usuario_id) = 'repartidor'
       AND EXISTS (SELECT 1 FROM entrega e WHERE e.pedido_id = p.id AND e.repartidor_id = p_usuario_id
                      AND e.turno_fecha = current_date AND e.cierre_en IS NULL)                -- RN25
$$;
COMMENT ON FUNCTION fn_pedidos_visibles(integer) IS
    'RN33/RN22/RN25. Ámbito de pedidos por perfil. SQL (no PL/pgSQL) para que el planificador la integre a la consulta '
    'y use los índices de pedido; ver 12_rendimiento.sql.';

-- Hallazgo 2. Los resúmenes por día filtran con «(creado_en AT TIME ZONE zona)::date BETWEEN …» y agrupan por ese mismo día.
--   El servicio de pedidos ya filtra por rango de creado_en (que usa ix_pedido_zona_fecha e ix_web_pedido_fecha); este índice
--   de expresión cubre a quien todavía filtre o agrupe por el día local (reportes y vistas del web).
CREATE INDEX IF NOT EXISTS ix_pedido_dia_local ON pedido (((creado_en AT TIME ZONE 'America/Monterrey')::date));

-- Hallazgo 3. Las ventas por producto de un periodo leen todas las líneas de los pedidos del periodo; con este índice
--   cubriente PostgreSQL las suma sin ir a la tabla (index-only scan).
CREATE INDEX IF NOT EXISTS ix_detalle_pedido_cubriente ON pedido_detalle (pedido_id) INCLUDE (producto_id, cantidad, importe);

ANALYZE pedido;
ANALYZE pedido_detalle;
