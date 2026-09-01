-- 04_revocar_sesion.lua — revocación inmediata de un token (RF04, HU12)
-- KEYS[1] = auth:jti:revocado:{jti}
-- KEYS[2] = auth:sesion:{usuario_id}
-- ARGV[1] = jti     ARGV[2] = segundos de vida restante del token
--
-- El TTL es la vida RESTANTE del token, no un valor fijo: una vez que el
-- token expira por sí solo, la entrada de revocación ya no aporta nada.
redis.call("SET", KEYS[1], "1", "EX", tonumber(ARGV[2]))
redis.call("SREM", KEYS[2], ARGV[1])
return 1
