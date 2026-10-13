package mx.microhubs.movil

import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URI
import java.net.URL

/** Error estándar del contrato: `{"error": {"codigo", "mensaje", "detalles", "traza_id"}}`. */
class ApiError(
    val status: Int,
    val code: String,
    message: String,
    val fields: Map<String, String>,
    val trace: String,
    val retryAfter: Int = 0
) : Exception(message)

/**
 * Cliente JSON de los microservicios (contrato v1). Siempre `application/json`; solo HTTPS, salvo el host HTTP que se
 * habilita al compilar en modo debug (`httpHost`, por defecto 10.0.2.2 = el equipo desde el emulador).
 * Un 401 renueva la sesión una sola vez (el token de renovación rota) y repite la petición.
 */
class Api(
    private val store: Sessions,
    private val open: (URL) -> HttpURLConnection = { it.openConnection() as HttpURLConnection },
    private val httpHost: String = BuildConfig.HTTP_HOST
) {
    @Volatile var session: JSONObject? = null
    var demo = false
    var host = if (httpHost.isEmpty()) "https://localhost" else "http://$httpHost"
    var lastTrace = ""; private set
    private val renewal = Any()
    private var retryAt = 0L
    private val ports = mapOf(
        "auth" to 5101, "usuarios" to 5102, "pedidos" to 5104, "entregas" to 5105, "documentos" to 5107, "notificaciones" to 5108
    )

    fun login(email: String, password: String) {
        clear()
        val result = call("auth", "auth/login", "POST", JSONObject().put("correo", email).put("clave", password))
        require(result.optString("token_acceso").isNotBlank() && result.optString("token_renovacion").isNotBlank()) { "Sesión incompleta" }
        result.getJSONObject("usuario").getString("rol")
        session = result
        if (!demo) store.save(result)
    }

    fun clear() { session = null; store.clear() }

    fun restore() { if (!demo) session = store.load() }

    /** Revoca la sesión en el servidor (acceso y renovación) y borra las credenciales locales aunque falle la red. */
    fun logout() {
        try {
            val actual = session
            if (actual != null) call("auth", "auth/salir", "POST", JSONObject().put("token_renovacion", actual.getString("token_renovacion")))
        } finally {
            clear()
        }
    }

    fun call(service: String, path: String, method: String = "GET", body: JSONObject? = null, retry: Boolean = true): JSONObject {
        if (demo) return example(path, method, body)
        require(System.currentTimeMillis() >= retryAt) { "Espera ${(retryAt - System.currentTimeMillis()) / 1000 + 1} segundos antes de reintentar" }
        val base = URI(if (host.contains("://")) host else "https://$host")
        require(base.host != null && base.userInfo == null && (base.scheme == "https" || base.scheme == "http" && httpHost.isNotEmpty() && base.host == httpHost)) {
            "Usa HTTPS o el host HTTP habilitado en esta compilación debug: $httpHost"
        }
        val url = URI(base.scheme, null, base.host, ports.getValue(service), "/api/v1/" + path.substringBefore('?'),
            path.substringAfter('?', "").ifEmpty { null }, null).toURL()
        val sentToken = session?.optString("token_acceso")
        val connection = open(url)
        try {
            connection.requestMethod = method
            connection.connectTimeout = 15000
            connection.readTimeout = 20000
            connection.setRequestProperty("Accept", "application/json")
            connection.setRequestProperty("Content-Type", "application/json")
            sentToken?.let { connection.setRequestProperty("Authorization", "Bearer $it") }
            if (body != null) {
                connection.doOutput = true
                connection.outputStream.use { it.write(body.toString().toByteArray(Charsets.UTF_8)) }
            }
            val code = connection.responseCode
            if (code == 401 && retry && session != null && !path.startsWith("auth/")) {
                renew(sentToken)
                return call(service, path, method, body, false)
            }
            if (code == 204) return JSONObject()
            require(connection.contentType?.substringBefore(';') == "application/json") { "El servicio no devolvió JSON (HTTP $code)" }
            val stream = if (code in 200..299) connection.inputStream else connection.errorStream
            val result = parse(stream?.bufferedReader(Charsets.UTF_8)?.use { it.readText() } ?: "{}")
            if (code !in 200..299) throw toApiError(code, result, connection)
            return result
        } finally {
            connection.disconnect()
        }
    }

    /** Una sola renovación a la vez: quien llegue después ya encuentra los tokens nuevos y solo repite su petición. */
    private fun renew(sentToken: String?) = synchronized(renewal) {
        if (session?.optString("token_acceso") == sentToken) {
            try {
                val previous = session!!
                val tokens = call("auth", "auth/renovar", "POST", JSONObject().put("token_renovacion", previous.getString("token_renovacion")), false)
                require(tokens.optString("token_acceso").isNotBlank() && tokens.optString("token_renovacion").isNotBlank()) { "Renovación incompleta" }
                val merged = JSONObject(previous.toString())      // se conserva el `usuario`: la renovación solo trae tokens
                tokens.keys().forEach { merged.put(it, tokens.get(it)) }
                store.save(merged)
                session = merged
            } catch (e: Exception) {
                clear()
                throw e
            }
        }
        check(session != null) { "La sesión terminó; vuelve a entrar" }
    }

    private fun toApiError(code: Int, result: JSONObject, connection: HttpURLConnection): ApiError {
        val e = result.getJSONObject("error")
        val details = e.optJSONArray("detalles") ?: JSONArray()
        val fields = (0 until details.length()).associate { val d = details.getJSONObject(it); d.getString("campo") to d.getString("mensaje") }
        val seconds = if (code == 429) connection.getHeaderField("Retry-After")?.toIntOrNull()?.coerceAtLeast(0) ?: 60 else 0
        if (code == 429) retryAt = System.currentTimeMillis() + seconds.toLong() * 1000
        lastTrace = e.optString("traza_id")
        if (code == 401) clear()
        return ApiError(code, e.getString("codigo"), e.getString("mensaje"), fields, lastTrace, seconds)
    }

    companion object { fun parse(text: String) = JSONObject(text) }

    // Respuestas de ejemplo con la misma forma que el contrato v1 (modo «ejemplos locales», sin backend).
    private val demoLines = """[{"pedido_detalle_id":51,"nombre":"Arroz","cantidad":2},{"pedido_detalle_id":52,"nombre":"Agua purificada","cantidad":4}]"""
    private fun example(path: String, method: String, body: JSONObject?): JSONObject = when {
        path == "auth/login" || path == "auth/renovar" -> JSONObject("""{"token_acceso":"demo","token_renovacion":"demo","tipo":"Bearer","expira_en":900,"usuario":{"id":7,"nombre":"Ramiro","apellidos":"Alanís Lozano","correo":"repartidor1@codex.mx","rol":"repartidor","microhub_id":null,"permisos":["entregas.ver","entregas.cerrar","pedidos.ver"]}}""")
        path == "usuarios/yo" -> JSONObject("""{"id":7,"nombre":"Ramiro","apellidos":"Alanís Lozano","correo":"repartidor1@codex.mx","telefono":"8114641034","rol":"repartidor","microhub":null,"ultimo_acceso":"2026-10-12T08:02:11-06:00"}""")
        path == "auth/salir" -> JSONObject()
        path.startsWith("notificaciones/conteo") -> JSONObject().put("no_leidas", 1)
        path.matches(Regex("notificaciones/[0-9]+/leer")) -> JSONObject("""{"id":1,"tipo":"entrega","titulo":"Nueva entrega asignada","mensaje":"Tienes una entrega nueva.","leida":true,"referencia":{"tipo":"entrega","id":"61"},"creada_en":"2026-10-12T08:05:00-06:00"}""")
        path.startsWith("notificaciones") -> JSONObject("""{"datos":[{"id":1,"tipo":"entrega","titulo":"Nueva entrega asignada","mensaje":"Tienes una entrega nueva.","leida":false,"referencia":{"tipo":"entrega","id":"61"},"creada_en":"2026-10-12T08:05:00-06:00"}],"paginacion":{"pagina":1,"por_pagina":20,"total":1,"paginas":1}}""")
        path.startsWith("entregas/mias") -> JSONObject("""{"datos":[{"id":61,"pedido_id":101,"folio":"PED-DEMO-000101","estado_pedido":"en_ruta","orden_parada":1,"direccion":"Av. Rodrigo Gómez 1420, San Bernabé","zona":"San Bernabé Centro","distancia_km":0.21,"minutos_estimados":14.2,"total":158.0}],"paginacion":{"pagina":1,"por_pagina":20,"total":1,"paginas":1}}""")
        path.matches(Regex("entregas/[0-9]+")) -> JSONObject("""{"id":61,"pedido_id":101,"folio":"PED-DEMO-000101","estado_pedido":"en_ruta","cliente":{"nombre":"Laura Pérez","telefono":"8180001122"},"domicilio":{"calle":"Av. Rodrigo Gómez","numero_ext":"1420","colonia":"San Bernabé","latitud":25.749,"longitud":-100.361},"orden_parada":1,"distancia_km":0.21,"minutos_estimados":14.2,"total":158.0,"lineas":$demoLines}""")
        path.endsWith("/resultado") -> JSONObject().put("entrega_id", 61).put("pedido_id", 101).put("cerrado_en", "2026-10-12T18:30:04-06:00").put("duplicado", false)
            .put("estado_pedido", when (body!!.getString("resultado")) { "parcial" -> "entrega_parcial"; "fallida" -> "entrega_fallida"; else -> "entregado" })
        path.endsWith("/ubicaciones") -> JSONObject().put("recibidos", body!!.getJSONArray("puntos").length())
        path == "documentos" -> JSONObject("""{"id":"665f1c2e8a3b4d0012a7c9e1","nombre":"evidencia.jpg","tipo_mime":"image/jpeg","tamano_bytes":1024,"sha256":"0","referencia":{"tipo":"entrega","id":"61"},"subido_por":7,"creado_en":"2026-10-12T18:29:00-06:00"}""")
        path.matches(Regex("pedidos/[0-9]+")) -> JSONObject("""{"id":101,"folio":"PED-DEMO-000101","estado":"en_ruta","total":158.0,"lineas":$demoLines}""")
        else -> throw IllegalArgumentException("Ruta de ejemplo no disponible: $method $path")
    }
}
