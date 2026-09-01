-- 03_extender_lock.lua — extensión de un bloqueo aún propio
-- KEYS[1] = clave del bloqueo   ARGV[1] = token   ARGV[2] = ms adicionales
--
-- Necesario cuando el descuento tarda más que el TTL inicial: extender es
-- correcto, pero solo si el bloqueo sigue siendo nuestro.
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("PEXPIRE", KEYS[1], ARGV[2])
else
    return 0
end
