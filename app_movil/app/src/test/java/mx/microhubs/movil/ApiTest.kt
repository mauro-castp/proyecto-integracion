package mx.microhubs.movil

import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
import java.net.HttpURLConnection
import java.net.URL
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream

class ApiTest {
    private class Memory : Sessions {
        var saved: JSONObject? = null
        override fun save(session: JSONObject) { saved = session }
        override fun load() = saved
        override fun clear() { saved = null }
    }
    private fun client(): Api = Api(Memory()).apply { login("qa@example.com", "demo") }
    @Test fun loginYPerfil() { val api=client(); assertEquals("repartidor",api.call("usuarios","usuarios/yo").getString("rol")) }
    @Test fun listaPaginada() { val r=client().call("entregas","entregas?pagina=1&por_pagina=20"); assertEquals(2,r.getJSONArray("datos").length()); assertEquals(2,r.getJSONObject("paginacion").getInt("total")) }
    @Test fun resultadoSeConserva() {
        val api=client(); api.call("entregas","entregas/1","PUT",JSONObject().put("resultado","entregado"))
        assertEquals("entregado",api.call("entregas","entregas").getJSONArray("datos").getJSONObject(0).getString("estado"))
    }
    @Test fun consultaPedido() { assertEquals(101,client().call("pedidos","pedidos/101").getInt("id")) }
    @Test fun documentoDevuelveId() { assertEquals("evidencia-demo",client().call("documentos","documentos","POST",JSONObject()).getString("id")) }
    @Test fun salirBorraSesionGuardada() { val m=Memory(); val api=Api(m); m.save(JSONObject().put("token_acceso","secreto")); api.clear(); assertNull(api.session); assertNull(m.load()) }
    @Test(expected=IllegalArgumentException::class) fun rutaDesconocidaFalla() { client().call("entregas","no-existe") }
    @Test fun demoNoPersisteTokens() { val m=Memory(); Api(m).login("qa@example.com","demo"); assertNull(m.load()) }
    private class Reply(url: URL, val code: Int, val mime: String, val body: String) : HttpURLConnection(url) {
        val sent = ByteArrayOutputStream()
        override fun connect() {}
        override fun disconnect() {}
        override fun usingProxy() = false
        override fun getResponseCode() = code
        override fun getContentType() = mime
        override fun getInputStream() = ByteArrayInputStream(body.toByteArray())
        override fun getErrorStream() = ByteArrayInputStream(body.toByteArray())
        override fun getOutputStream() = sent
    }
    @Test fun rutaYProtocoloJson() {
        var reply: Reply? = null
        val api=Api(Memory()) { url -> Reply(url,200,"application/json; charset=utf-8","{}").also { reply=it } }
        api.demo=false; api.host="https://microhubs.example"
        api.call("entregas","entregas?pagina=2")
        assertEquals(5105,reply!!.url.port); assertEquals("pagina=2",reply!!.url.query)
        assertEquals("application/json",reply!!.getRequestProperty("Accept"))
    }
    @Test fun renuevaUnaVezTras401() {
        val memory=Memory(); var requests=0
        val session=JSONObject("""{"token_acceso":"nuevo","token_renovacion":"renovado","usuario":{"rol":"repartidor"}}""")
        val api=Api(memory) { url ->
            requests++
            when(requests) {
                1 -> Reply(url,401,"application/json","{}")
                2 -> { assertEquals("/api/v1/auth/renovar",url.path); Reply(url,200,"application/json",session.toString()) }
                else -> Reply(url,200,"application/json","{}")
            }
        }
        api.demo=false; api.session=JSONObject().put("token_acceso","viejo").put("token_renovacion","refresh")
        api.call("entregas","entregas")
        assertEquals(3,requests); assertEquals("nuevo",api.session!!.getString("token_acceso")); assertNotNull(memory.saved)
    }
    @Test(expected=IllegalArgumentException::class) fun rechazaHttp() { val api=client(); api.demo=false; api.host="http://servidor"; api.call("entregas","entregas") }
    @Test(expected=IllegalArgumentException::class) fun rechazaXml() {
        val api=Api(Memory()) { url -> Reply(url,200,"application/xml","<lista/>") }; api.demo=false
        api.call("entregas","entregas")
    }
}
