package mx.microhubs.movil

import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.IOException

/** Bandeja de avisos (servicio de notificaciones, 5124), con los ejemplos oficiales del contrato. */
class AvisosTest {
    @get:Rule val tmp = TemporaryFolder()
    private val ahora = 1_760_300_000_000L

    @Test fun leeLaBandejaYElConteoDelContrato() {
        val s = Servidor { p -> if (p.ruta.endsWith("/conteo")) Salida.ok(Ejemplos.json("Conteo.ok")) else Salida.ok(Ejemplos.json("NotificacionLista.ok")) }
        val avisos = Avisos(clienteDe(s))
        val pagina = avisos.bandeja(1)
        assertEquals("GET /api/v1/notificaciones?pagina=1&por_pagina=20", s.ultima().toString())
        assertEquals(Aviso(310, "entrega", "Nueva entrega asignada", "Se te asignó el pedido PED-20260930-000020 (parada 3).", false,
            "2026-10-12T17:55:00-06:00", "entrega", "61"), pagina.items.single())
        avisos.bandeja(2, soloNoLeidas = true)
        assertEquals("GET /api/v1/notificaciones?pagina=2&por_pagina=20&solo_no_leidas=true", s.ultima().toString())
        assertEquals(3, avisos.noLeidas())
        assertEquals("GET /api/v1/notificaciones/conteo", s.ultima().toString())
    }

    @Test fun elPuertoEsElDelServicioDeNotificaciones() {
        var puerto = -1
        val s = Servidor { Salida.ok(Ejemplos.json("Conteo.ok")) }
        val api = Api(Memoria(), { u -> puerto = u.port; s.abrir(u) }, "10.0.2.2").apply { session = Ejemplos.json("Sesion.ok") }
        Avisos(api).noLeidas(); assertEquals(5124, puerto)
        try { api.call("sincronizacion", "sincronizacion/estado?dispositivo=x") } catch (_: Exception) {}
        assertEquals(5125, puerto)
    }

    @Test fun marcarLeidoConRed() {
        val s = Servidor { Salida.ok(JSONObject(Ejemplos.texto("Notificacion.ok")).put("leida", true)) }
        val a = Avisos.leer(Ejemplos.json("Notificacion.ok"))
        val leido = Avisos(clienteDe(s)).marcarLeido(a)
        assertTrue(leido.leida)
        assertEquals("POST /api/v1/notificaciones/310/leer", s.ultima().toString())
        Avisos(clienteDe(s)).marcarLeido(leido)
        assertEquals("un aviso ya leído no se vuelve a enviar", 1, s.peticiones.size)
    }

    @Test fun marcarLeidoSinRedSeGuardaYSeEnviaConLaSincronizacion() {
        val cola = ColaEnArchivos(tmp.root) { ahora }
        val sinRed = Servidor { Salida(0, fallo = IOException("sin red")) }
        val a = Avisos.leer(Ejemplos.json("Notificacion.ok"))
        val avisos = Avisos(clienteDe(sinRed), cola) { ahora }
        assertTrue(avisos.marcarLeido(a).leida)
        avisos.marcarLeido(a)
        val op = cola.todas().single()
        assertEquals(Operacion.LECTURA, op.tipo); assertEquals(310, JSONObject(op.datos).getInt("id")); assertEquals(7, op.usuarioId)

        // con red: la bandeja y el conteo ya lo cuentan como leído aunque no se haya sincronizado
        val s = Servidor { p ->
            when {
                p.ruta.endsWith("/conteo") -> Salida.ok(Ejemplos.json("Conteo.ok"))
                p.ruta.endsWith("/lotes") -> Salida.ok(JSONObject().put("operaciones", org.json.JSONArray().put(JSONObject()
                    .put("operacion_uuid", op.uuid).put("tipo", op.tipo).put("estado", "aplicada").put("duplicada", false).put("http_status", 200)
                    .put("codigo", JSONObject.NULL).put("mensaje", JSONObject.NULL).put("reintentar", false))), 201)
                else -> Salida.ok(Ejemplos.json("NotificacionLista.ok"))
            }
        }
        val enLinea = Avisos(clienteDe(s), cola)
        assertTrue(enLinea.bandeja(1).items.single().leida)
        assertEquals(2, enLinea.noLeidas())
        assertEquals(Informe(aplicadas = 1), Sincronizador(clienteDe(s), cola).sincronizar())
        val enviado = s.ultima().json.getJSONArray("operaciones").getJSONObject(0)
        assertEquals("notificacion_leida", enviado.getString("tipo")); assertEquals(310, enviado.getJSONObject("datos").getInt("id"))
        assertTrue(cola.todas().isEmpty())
    }

    @Test fun elModoDeEjemplosTieneBandeja() {
        val api = Api(Memoria(), Servidor()::abrir, "10.0.2.2"); api.demo = true; api.login("demo@example.com", "x")
        val avisos = Avisos(api)
        val b = avisos.bandeja(1)
        assertEquals(2, b.items.size); assertEquals(1, avisos.noLeidas())
        assertTrue(avisos.marcarLeido(b.items.first { !it.leida }).leida)
        assertEquals(1, avisos.marcarTodos())
    }
}
