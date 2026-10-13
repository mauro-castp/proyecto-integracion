package mx.microhubs.movil

import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
import java.util.concurrent.CountDownLatch
import java.util.concurrent.atomic.AtomicInteger
import kotlin.concurrent.thread

/** Protocolo del cliente: rutas, cabeceras, sesión, renovación, errores y límites; contra un servidor simulado. */
class ApiTest {
    @Test fun loginGuardaLaSesionCifrada() {
        val memoria = Memoria()
        val servidor = Servidor { Salida.ok(Ejemplos.json("Sesion.ok")) }
        val api = clienteDe(servidor, memoria, conSesion = false)
        api.login("repartidor1@codex.mx", "clave")
        assertEquals("repartidor", api.session!!.getJSONObject("usuario").getString("rol"))
        assertNotNull(memoria.saved)
        val p = servidor.ultima()
        assertEquals("POST /api/v1/auth/login", p.toString())
        assertEquals("repartidor1@codex.mx", p.json.getString("correo"))
    }

    @Test fun loginRechazaUnaSesionIncompleta() {
        val servidor = Servidor { Salida.ok(JSONObject().put("token_acceso", "x")) }
        val api = clienteDe(servidor, conSesion = false)
        try { api.login("a@b.mx", "x"); fail() } catch (_: IllegalArgumentException) {}
        assertNull(api.session)
    }

    @Test fun loginFallidoMuestraElMensajeDelServidor() {
        val api = clienteDe(Servidor { Salida(401, cuerpo = """{"error":{"codigo":"CREDENCIALES_INVALIDAS","mensaje":"Correo o contraseña incorrectos. Intento 1 de 5.","traza_id":"t-1"}}""") }, conSesion = false)
        try { api.login("a@b.mx", "mala"); fail() } catch (e: ApiError) {
            assertEquals(401, e.status); assertEquals("CREDENCIALES_INVALIDAS", e.code); assertTrue(e.message!!.contains("Intento 1 de 5")); assertEquals("t-1", e.trace)
        }
        assertNull(api.session)
    }

    @Test fun cabecerasRutaPuertoYConsulta() {
        val servidor = Servidor { Salida.ok(Ejemplos.json("EntregaLista.ok")) }
        val api = clienteDe(servidor)
        api.call("entregas", "entregas/mias?pagina=2&por_pagina=20")
        val p = servidor.ultima()
        assertEquals("GET /api/v1/entregas/mias?pagina=2&por_pagina=20", p.toString())
        assertEquals("application/json", p.cabecera("Accept")); assertEquals("application/json", p.cabecera("Content-Type"))
        assertTrue(p.cabecera("Authorization")!!.startsWith("Bearer eyJ"))
        val puertos = mapOf("auth" to 5101, "usuarios" to 5102, "pedidos" to 5104, "entregas" to 5105, "documentos" to 5107, "seguimiento" to 5110)
        puertos.forEach { (servicio, puerto) ->
            var visto = -1
            val otro = Servidor { Salida(200) }
            val api2 = Api(Memoria(), { u -> visto = u.port; otro.abrir(u) }, "10.0.2.2")
            api2.session = Ejemplos.json("Sesion.ok")
            api2.call(servicio, "salud")
            assertEquals(servicio, puerto, visto)
        }
    }

    @Test fun erroresDelContratoLlegaConCamposYTraza() {
        val api = clienteDe(Servidor { Salida.error(422, "Error.validacion") })
        try { api.call("entregas", "entregas/61/resultado", "POST", JSONObject()); fail() } catch (e: ApiError) {
            assertEquals(422, e.status); assertEquals("VALIDACION", e.code)
            assertEquals("Debe ser mayor a 0.", e.fields["cantidad"]); assertEquals("9f2c1e7a-6b1d-4c1b-9d4e-2a7f0f6e1a10", e.trace)
        }
    }

    @Test fun un401RenuevaUnaVezYConservaElUsuario() {
        val memoria = Memoria(); var viejoUsado = false
        val servidor = Servidor { p ->
            when {
                p.ruta.endsWith("/auth/renovar") -> Salida.ok(Ejemplos.json("Tokens.ok"))
                p.cabecera("Authorization")!!.endsWith("firma2") -> Salida.ok(Ejemplos.json("EntregaLista.ok"))
                else -> { viejoUsado = true; Salida.error(401, "Error.token_invalido") }
            }
        }
        val api = clienteDe(servidor, memoria)
        val usuarioAntes = api.session!!.getJSONObject("usuario").toString()
        api.call("entregas", "entregas/mias")
        assertTrue(viejoUsado)
        assertEquals(listOf("GET /api/v1/entregas/mias", "POST /api/v1/auth/renovar", "GET /api/v1/entregas/mias"), servidor.rutas())
        assertEquals("rt_8f3b2c71a0d94e5f9b6a1c2d3e4f5a6b", servidor.peticiones[1].json.getString("token_renovacion"))
        assertEquals("rt_1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d", api.session!!.getString("token_renovacion"))
        assertEquals(usuarioAntes, api.session!!.getJSONObject("usuario").toString())
        assertEquals("rt_1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d", memoria.saved!!.getString("token_renovacion"))
    }

    @Test fun siLaRenovacionFallaSeBorraLaSesion() {
        val memoria = Memoria().also { it.saved = JSONObject().put("x", 1) }
        val api = clienteDe(Servidor { Salida.error(401, "Error.token_invalido") }, memoria)
        try { api.call("entregas", "entregas/mias"); fail() } catch (e: ApiError) { assertEquals(401, e.status) }
        assertNull(api.session); assertNull(memoria.saved)
    }

    @Test fun variasPeticionesConElTokenVencidoRenuevanUnaSolaVez() {
        val renovaciones = AtomicInteger()
        val servidor = Servidor { p ->
            when {
                p.ruta.endsWith("/auth/renovar") -> { renovaciones.incrementAndGet(); Thread.sleep(80); Salida.ok(Ejemplos.json("Tokens.ok")) }
                p.cabecera("Authorization")!!.endsWith("firma2") -> Salida.ok(Ejemplos.json("EntregaLista.ok"))
                else -> { Thread.sleep(40); Salida.error(401, "Error.token_invalido") }
            }
        }
        val api = clienteDe(servidor)
        val salida = CountDownLatch(4); val ok = AtomicInteger()
        repeat(4) { thread { try { api.call("entregas", "entregas/mias"); ok.incrementAndGet() } catch (_: Exception) {} finally { salida.countDown() } } }
        salida.await()
        assertEquals(1, renovaciones.get()); assertEquals(4, ok.get())
    }

    @Test fun un429RespetaRetryAfter() {
        val servidor = Servidor { Salida.error(429, "Error.validacion", mapOf("Retry-After" to "30")) }
        val api = clienteDe(servidor)
        try { api.call("entregas", "entregas/mias"); fail() } catch (e: ApiError) { assertEquals(429, e.status); assertEquals(30, e.retryAfter) }
        val antes = servidor.peticiones.size
        try { api.call("entregas", "entregas/mias"); fail() } catch (e: IllegalArgumentException) { assertTrue(e.message!!.startsWith("Espera")) }
        assertEquals(antes, servidor.peticiones.size)
    }

    @Test fun elHostHttpSoloEsElDeLaCompilacionDebug() {
        val api = clienteDe(Servidor { Salida(200) })
        api.host = "http://10.0.2.2"; api.call("entregas", "salud")
        api.host = "https://servidor.ejemplo.com"; api.call("entregas", "salud")
        for (host in listOf("http://otro-servidor", "http://10.0.2.3", "ftp://10.0.2.2", "https://usuario:clave@servidor.ejemplo.com")) {
            api.host = host
            try { api.call("entregas", "salud"); fail(host) } catch (_: IllegalArgumentException) {}
        }
        val release = Api(Memoria(), Servidor { Salida(200) }::abrir, "")
        assertEquals("https://localhost", release.host)
        release.host = "http://10.0.2.2"
        try { release.call("entregas", "salud"); fail() } catch (_: IllegalArgumentException) {}
    }

    @Test fun rechazaRespuestasQueNoSonJson() {
        val api = clienteDe(Servidor { Salida(200, tipo = "application/xml", cuerpo = "<lista/>") })
        try { api.call("entregas", "entregas/mias"); fail() } catch (e: IllegalArgumentException) { assertTrue(e.message!!.contains("JSON")) }
    }

    @Test fun salirRevocaEnElServidorYBorraLasCredenciales() {
        val memoria = Memoria().also { it.saved = JSONObject().put("x", 1) }
        val servidor = Servidor { Salida(204, cuerpo = "") }
        val api = clienteDe(servidor, memoria)
        api.logout()
        assertEquals("POST /api/v1/auth/salir", servidor.ultima().toString())
        assertEquals("rt_8f3b2c71a0d94e5f9b6a1c2d3e4f5a6b", servidor.ultima().json.getString("token_renovacion"))
        assertNull(api.session); assertNull(memoria.saved)
    }

    @Test fun salirBorraLasCredencialesAunqueFalleLaRed() {
        val memoria = Memoria().also { it.saved = JSONObject().put("x", 1) }
        val api = clienteDe(Servidor { Salida(0, fallo = java.io.IOException("sin red")) }, memoria)
        try { api.logout(); fail() } catch (_: java.io.IOException) {}
        assertNull(api.session); assertNull(memoria.saved)
    }

    @Test fun elModoDemoNoGuardaTokensYUsaLaFormaDelContrato() {
        val memoria = Memoria(); val api = Api(memoria, Servidor()::abrir, "10.0.2.2"); api.demo = true
        api.login("demo@example.com", "x")
        assertNull(memoria.saved)
        val mias = api.call("entregas", "entregas/mias")
        Contrato.parada(mias.getJSONArray("datos").getJSONObject(0))
        Contrato.detalle(api.call("entregas", "entregas/61"))
    }

    @Test(expected = IllegalArgumentException::class) fun elModoDemoRechazaRutasDesconocidas() {
        val api = Api(Memoria(), Servidor()::abrir, "10.0.2.2"); api.demo = true; api.call("entregas", "no-existe")
    }
}
