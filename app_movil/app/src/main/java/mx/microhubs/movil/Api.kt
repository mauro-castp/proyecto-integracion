package mx.microhubs.movil

import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URI
import java.net.URL

class Api(private val store: SessionStore) {
    var session: JSONObject? = null
    var demo = true
    var host = "https://localhost"
    private val ports = mapOf("auth" to 5101, "usuarios" to 5102, "pedidos" to 5104, "entregas" to 5105, "documentos" to 5107, "notificaciones" to 5108)
    private val deliveries = JSONArray("""[{"id":1,"pedido_id":101,"estado":"asignada"},{"id":2,"pedido_id":102,"estado":"asignada"}]""")
    fun login(email: String, password: String) {
        clear()
        val result = call("auth", "auth/login", "POST", JSONObject().put("correo", email).put("clave", password))
        require(result.optString("token_acceso").isNotBlank() && result.optString("token_renovacion").isNotBlank()) { "Sesión inválida" }
        result.getJSONObject("usuario").getString("rol")
        if (!demo) store.save(result)
        session = result
    }
    fun clear() { session = null; store.clear() }
    fun restore() { if (!demo) session = store.load() }
    fun call(service: String, path: String, method: String = "GET", body: JSONObject? = null, retry: Boolean = true): JSONObject {
        if (demo) return example(path, method, body)
        val base = URI(host)
        require(base.scheme == "https" && base.host != null && base.userInfo == null) { "Configura un host HTTPS válido" }
        val url = URI("https", null, base.host, ports.getValue(service), "/api/v1/" + path.substringBefore('?'), path.substringAfter('?', "").ifEmpty { null }, null).toURL()
        val connection = url.openConnection() as HttpURLConnection
        try {
            connection.requestMethod = method; connection.connectTimeout = 15000; connection.readTimeout = 20000
            connection.setRequestProperty("Accept", "application/json")
            session?.optString("token_acceso")?.let { connection.setRequestProperty("Authorization", "Bearer $it") }
            if (body != null) {
                connection.doOutput = true; connection.setRequestProperty("Content-Type", "application/json; charset=utf-8")
                connection.outputStream.use { it.write(body.toString().toByteArray(Charsets.UTF_8)) }
            }
            val code = connection.responseCode
            if (code == 401 && retry && session != null && !path.startsWith("auth/")) {
                try {
                    val renewed = call("auth", "auth/renovar", "POST", JSONObject().put("token_renovacion", session!!.getString("token_renovacion")), false)
                    require(renewed.optString("token_acceso").isNotBlank())
                    store.save(renewed); session = renewed
                } catch (e: Exception) { clear(); throw e }
                return call(service, path, method, body, false)
            }
            if (code == 204) return JSONObject()
            require(connection.contentType?.substringBefore(';') == "application/json") { "El servicio no devolvió JSON (HTTP $code)" }
            val stream = if (code in 200..299) connection.inputStream else connection.errorStream
            val result = JSONObject(stream?.bufferedReader(Charsets.UTF_8)?.use { it.readText() } ?: "{}")
            if (code !in 200..299) throw IllegalStateException(result.optJSONObject("error")?.optString("mensaje") ?: "HTTP $code")
            return result
        } finally { connection.disconnect() }
    }
    private fun example(path: String, method: String, body: JSONObject?): JSONObject = when {
        path == "auth/login" || path == "auth/renovar" -> JSONObject("""{"token_acceso":"demo","token_renovacion":"demo","expira_en":900,"usuario":{"id":1,"nombre":"Repartidor demo","rol":"repartidor","microhub_id":1}}""")
        path == "usuarios/yo" -> session!!.getJSONObject("usuario")
        path == "auth/salir" -> JSONObject()
        path == "documentos" -> JSONObject().put("id", "evidencia-demo")
        path.startsWith("entregas/") && method == "PUT" -> {
            val id = path.split('/')[1].toInt()
            val item = (0 until deliveries.length()).map { deliveries.getJSONObject(it) }.first { it.getInt("id") == id }
            item.put("estado", body!!.getString("resultado")); JSONObject(item.toString())
        }
        path.startsWith("entregas") -> JSONObject().put("datos", deliveries).put("paginacion", JSONObject().put("pagina", 1).put("por_pagina", 20).put("total", deliveries.length()).put("paginas", 1))
        path.startsWith("pedidos/") -> JSONObject().put("id", path.substringAfter('/').toInt()).put("estado", "en_ruta")
        else -> throw IllegalArgumentException("Ruta de ejemplo no disponible: $path")
    }
}
