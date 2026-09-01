-- 02_liberar_lock.lua — liberación segura de un bloqueo de inventario (RN17)
-- Codex Innovations · Equipo 04
--
-- KEYS[1] = lock:inv:{microhub_id}:{producto_id}
-- ARGV[1] = token de propietario entregado al adquirir el bloqueo
--
-- Un DEL directo es incorrecto: si el bloqueo del proceso A expiró por TTL
-- y B ya lo adquirió, el DEL de A borraría el bloqueo de B y dos
-- transacciones descontarían la misma unidad. Comparar y borrar debe ser
-- una sola operación atómica, y en Redis eso significa Lua.
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
else
    return 0
end
