package mx.microhubs.movil

import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.IOException

/**
 * Trabajo sin red: el cierre y el recorrido se guardan en el teléfono y, al volver la conexión, se envían con
 * POST /sincronizacion/lotes (5125) después de subir la foto a POST /documentos (5107). Contra un servidor simulado.
 */
class SincronizacionTest {
    @get:Rule val tmp = TemporaryFolder()

    private val ahora = 1_760_300_000_000L
    private val foto = byteArrayOf(0xFF.toByte(), 0xD8.toByte(), 0xFF.toByte(), 0xE0.toByte(), 9, 8, 7)
    private val detalle = Contrato.detalle(Ejemplos.json("EntregaDetalle.ok"))      // entrega 61, total 158.00
    private fun fix(edadMs: Long = 5_000) = Fix(25.7491, -100.3611, 8.5, ahora - edadMs)
    private fun entregado() = DatosCierre("entregado", 158.0, 0.0, "", emptyList(), fix())
    private val sinRed = Salida(0, fallo = IOException("sin red"))

    /** Responde el lote marcando cada operación con el estado que diga `estado(tipo)`. */
    private fun respuestaLote(p: Peticion, estado: (JSONObject) -> String = { "aplicada" }): Salida {
        val ops = p.json.getJSONArray("operaciones")
        val res = (0 until ops.length()).map { ops.getJSONObject(it) }.map { o ->
            val e = estado(o)
            JSONObject().put("operacion_uuid", o.getString("operacion_uuid")).put("tipo", o.getString("tipo")).put("estado", e).put("duplicada", false)
                .put("http_status", mapOf("aplicada" to 201, "conflicto" to 409, "rechazada" to 422).getOrDefault(e, 503))
                .put("codigo", if (e == "aplicada") JSONObject.NULL else e.uppercase()).put("mensaje", if (e == "aplicada") JSONObject.NULL else "motivo $e")
                .put("reintentar", e == "pendiente")
        }
        return Salida.ok(JSONObject().put("id", 8).put("lote_uuid", p.json.getString("lote_uuid")).put("operaciones", JSONArray(res)), 201)
    }

    private fun servidor(lote: (Peticion) -> Salida = { respuestaLote(it) }) = Servidor { p ->
        when {
            p.ruta.endsWith("/documentos") -> Salida.ok(Ejemplos.json("Documento.ok"), 201)
            p.ruta.endsWith("/sincronizacion/lotes") -> lote(p)
            else -> Salida(404)
        }
    }

    private fun cola() = ColaEnArchivos(tmp.root.resolve("sin_red")) { ahora }
    private class Piezas(val api: Api, val cola: ColaEnArchivos, val borradores: BorradoresEnMemoria, val entregas: Entregas, val sync: Sincronizador)
    private fun piezas(s: Servidor, c: ColaEnArchivos = cola()): Piezas {
        val api = clienteDe(s); val b = BorradoresEnMemoria()
        return Piezas(api, c, b, Entregas(api, b, c) { ahora }, Sincronizador(api, c))
    }

    // ------------------------------------------------------------------------------------------ guardar sin red
    @Test fun sinRedElCierreYElRecorridoQuedanEnElTelefono() {
        val s = Servidor { sinRed }
        val x = piezas(s)
        val r = x.entregas.cerrar(detalle, entregado(), foto, listOf(fix(60_000), fix(30_000)), conRed = false)
        assertEquals(Resultado("entregado", false, enCola = true), r)
        assertTrue("sin red no se intenta nada", s.peticiones.isEmpty())
        val ops = x.cola.todas()
        assertEquals(listOf(Operacion.UBICACIONES, Operacion.CIERRE), ops.map { it.tipo })
        val cierre = ops[1]
        assertTrue(cierre.uuid.matches(Regex("[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}")))
        assertTrue("creada_en con zona", cierre.creadaEn.matches(Regex("""\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d([+-]\d\d:\d\d|Z)""")))
        assertEquals(Contrato.fecha(ahora), cierre.creadaEn)
        assertEquals(7, cierre.usuarioId); assertEquals(61, cierre.entregaId)
        assertTrue(cierre.necesitaFoto)
        assertArrayEquals("la foto se guarda para subirla al volver la red", foto, x.cola.foto(cierre.uuid))
        val datos = JSONObject(cierre.datos)
        assertEquals(61, datos.getInt("entrega_id")); assertEquals("entregado", datos.getString("resultado"))
        assertFalse("el servicio pone id_cliente_local a partir del uuid", datos.has("id_cliente_local"))
        assertFalse("la evidencia aún no existe", datos.has("evidencia_ids"))
        assertEquals(2, JSONObject(ops[0].datos).getJSONArray("puntos").length())
        assertFalse("la cola es ahora la dueña del identificador", x.entregas.hayCierrePendiente(61))
        assertEquals(cierre, x.entregas.cierreEnCola(61))
    }

    @Test fun noSePuedeCerrarDosVecesLaMismaEntregaSinRed() {
        val x = piezas(Servidor { sinRed })
        x.entregas.cerrar(detalle, entregado(), foto, conRed = false)
        try { x.entregas.cerrar(detalle, entregado(), foto, conRed = false); fail() } catch (e: IllegalArgumentException) { assertTrue(e.message!!.contains("ya está guardado")) }
        assertEquals(1, x.cola.todas().size)
    }

    @Test fun siLaRedFallaAlSubirLaFotoElCierreSeGuardaConElMismoIdentificador() {
        val s = Servidor { sinRed }
        val x = piezas(s)
        x.borradores.guardar(61, Borrador("1c9a4f0e-5b7d-4e21-9c3a-8d6f2b1e0a47"))         // un intento anterior que no se confirmó
        val r = x.entregas.cerrar(detalle, entregado(), foto)
        assertTrue(r.enCola)
        assertEquals(listOf("POST /api/v1/documentos"), s.rutas())
        assertEquals("1c9a4f0e-5b7d-4e21-9c3a-8d6f2b1e0a47", x.cola.todas().single().uuid)
    }

    @Test fun siLaRedFallaAlCerrarSeGuardaYaConLaEvidenciaSubida() {
        val s = Servidor { p -> if (p.ruta.endsWith("/documentos")) Salida.ok(Ejemplos.json("Documento.ok"), 201) else sinRed }
        val x = piezas(s)
        val r = x.entregas.cerrar(detalle, entregado(), foto, listOf(fix(60_000)))
        assertTrue(r.enCola)
        assertEquals(listOf("POST /api/v1/documentos", "POST /api/v1/seguimiento/61/ubicaciones", "POST /api/v1/entregas/61/resultado"), s.rutas())
        val cierre = x.cola.todas().single { it.tipo == Operacion.CIERRE }
        assertEquals("665f1c2e8a3b4d0012a7c9e1", cierre.evidenciaId)
        assertNull("ya no hace falta guardar la foto", x.cola.foto(cierre.uuid))
        assertEquals("el recorrido que no salió también se guarda", 1, x.cola.todas().count { it.tipo == Operacion.UBICACIONES })
    }

    @Test fun conRedNoSeGuardaNadaEnLaCola() {
        val s = Servidor { p ->
            when {
                p.ruta.endsWith("/documentos") -> Salida.ok(Ejemplos.json("Documento.ok"), 201)
                p.ruta.endsWith("/ubicaciones") -> Salida.ok(Ejemplos.json("UbicacionesRecibidas.ok"), 201)
                else -> Salida.ok(Ejemplos.json("ResultadoEntregaRespuesta.ok"), 201)
            }
        }
        val x = piezas(s)
        assertFalse(x.entregas.cerrar(detalle, entregado(), foto, listOf(fix())).enCola)
        assertTrue(x.cola.todas().isEmpty())
    }

    // ------------------------------------------------------------------------------------------ sincronizar
    @Test fun alVolverLaRedSubePrimeroLaFotoYLuegoMandaElLote() {
        val x0 = piezas(Servidor { sinRed })
        x0.entregas.cerrar(detalle, entregado(), foto, listOf(fix(60_000)), conRed = false)
        val s = servidor()
        val x = piezas(s, x0.cola)
        val informe = x.sync.sincronizar()
        assertEquals(Informe(aplicadas = 2), informe)
        assertEquals(listOf("POST /api/v1/documentos", "POST /api/v1/sincronizacion/lotes"), s.rutas())
        val doc = s.peticiones[0].json
        assertEquals("entrega", doc.getJSONObject("referencia").getString("tipo")); assertEquals("61", doc.getJSONObject("referencia").getString("id"))
        assertArrayEquals(foto, java.util.Base64.getDecoder().decode(doc.getString("contenido_base64")))
        val lote = s.peticiones[1].json
        assertEquals("android", lote.getString("cliente")); assertEquals(x.cola.dispositivo, lote.getString("dispositivo"))
        assertTrue(lote.getString("lote_uuid").matches(Regex("[0-9a-f-]{36}")))
        val ops = lote.getJSONArray("operaciones")
        val cierre = (0 until ops.length()).map { ops.getJSONObject(it) }.single { it.getString("tipo") == "entrega_resultado" }
        assertEquals(JSONArray().put("665f1c2e8a3b4d0012a7c9e1").toString(), cierre.getJSONObject("datos").getJSONArray("evidencia_ids").toString())
        assertTrue("aplicadas: la cola queda vacía", x.cola.todas().isEmpty())
    }

    @Test fun elLoteTieneLaFormaDelEjemploOficial() {
        val x0 = piezas(Servidor { sinRed })
        x0.entregas.cerrar(detalle, entregado(), foto, listOf(fix(60_000)), conRed = false)
        val s = servidor(); piezas(s, x0.cola).sync.sincronizar()
        val enviado = s.peticiones.last().json
        val oficial = Ejemplos.json("SyncLoteNuevo.ok")
        assertEquals(llaves(oficial), llaves(enviado))
        fun op(o: JSONObject, tipo: String) = o.getJSONArray("operaciones").let { a -> (0 until a.length()).map { a.getJSONObject(it) }.single { it.getString("tipo") == tipo } }
        for (tipo in listOf("ubicaciones", "entrega_resultado")) {
            assertEquals(tipo, llaves(op(oficial, tipo)), llaves(op(enviado, tipo)))
            // el ejemplo oficial no trae precision_m; además de sus claves solo se agregan opcionales del contrato del servicio dueño
            assertTrue(tipo, llaves(op(enviado, tipo).getJSONObject("datos")).containsAll(llaves(op(oficial, tipo).getJSONObject("datos"))))
        }
    }

    @Test fun cadaEstadoSeTrataComoDiceElServicio() {
        val c = cola()
        val x0 = piezas(Servidor { sinRed }, c)
        listOf(61, 62, 63, 64).forEach { id ->
            x0.entregas.cerrar(Detalle(id, 20 + id, "PED-$id", "en_ruta", "Cliente", "", "Calle", 158.0, detalle.lineas), entregado(), foto, conRed = false)
        }
        val estados = mapOf(61 to "aplicada", 62 to "conflicto", 63 to "rechazada", 64 to "pendiente")
        val s = servidor { p -> respuestaLote(p) { o -> estados.getValue(o.getJSONObject("datos").getInt("entrega_id")) } }
        val x = piezas(s, c)
        assertEquals(Informe(aplicadas = 1, conflictos = 1, rechazadas = 1, pendientes = 1), x.sync.sincronizar())
        val quedan = c.todas().associateBy { it.entregaId }
        assertNull("aplicada: sale de la cola", quedan[61])
        assertEquals(Operacion.CONFLICTO, quedan[62]!!.estado); assertEquals("motivo conflicto", quedan[62]!!.mensaje)
        assertEquals(Operacion.RECHAZADA, quedan[63]!!.estado)
        assertEquals(Operacion.PENDIENTE, quedan[64]!!.estado); assertEquals(1, quedan[64]!!.intentos)
        val primerEnvio = s.peticiones.last().json.getJSONArray("operaciones").let { a -> (0 until a.length()).map { a.getJSONObject(it) } }
            .single { it.getJSONObject("datos").getInt("entrega_id") == 64 }

        // siguiente sincronización: solo se reenvía la pendiente, idéntica (mismo uuid, misma fecha, mismos datos y misma evidencia)
        s.peticiones.clear()
        x.sync.sincronizar()
        assertEquals(listOf("POST /api/v1/sincronizacion/lotes"), s.rutas())
        val reenvio = s.ultima().json.getJSONArray("operaciones")
        assertEquals(1, reenvio.length())
        assertEquals("el reenvío no cambia el contenido", canonico(primerEnvio), canonico(reenvio.getJSONObject(0)))
        assertEquals(2, c.todas().single { it.entregaId == 64 }.intentos)

        // conflicto y rechazo no se reintentan; se pueden descartar una vez vistos. Lo que aún se va a enviar, no.
        try { x.sync.descartar(quedan[64]!!.uuid); fail() } catch (_: IllegalArgumentException) {}
        x.sync.descartar(quedan[62]!!.uuid); x.sync.descartar(quedan[63]!!.uuid)
        assertEquals(listOf(64), c.todas().map { it.entregaId })
    }

    @Test fun sinRedLaSincronizacionNoTocaLaCola() {
        val c = cola()
        piezas(Servidor { sinRed }, c).entregas.cerrar(detalle, entregado(), foto, conRed = false)
        val antes = c.todas()
        try { piezas(Servidor { sinRed }, c).sync.sincronizar(); fail() } catch (_: IOException) {}
        assertEquals(antes, c.todas()); assertNotNull(c.foto(antes.single().uuid))
    }

    @Test fun siLaFotoNoSePuedeSubirTodaviaElCierreEspera() {
        val c = cola()
        piezas(Servidor { sinRed }, c).entregas.cerrar(detalle, entregado(), foto, listOf(fix()), conRed = false)
        var caido = true
        val s = Servidor { p ->
            when {
                p.ruta.endsWith("/documentos") -> if (caido) Salida.error(503, "Error.validacion") else Salida.ok(Ejemplos.json("Documento.ok"), 201)
                else -> respuestaLote(p)
            }
        }
        val x = piezas(s, c)
        assertEquals(Informe(aplicadas = 1, esperando = 1), x.sync.sincronizar())                  // el recorrido sí sale; el cierre no
        val lote = s.ultima().json.getJSONArray("operaciones")
        assertEquals(1, lote.length()); assertEquals("ubicaciones", lote.getJSONObject(0).getString("tipo"))
        assertEquals(Operacion.EN_COLA, c.todas().single().estado)
        caido = false
        assertEquals(Informe(aplicadas = 1), x.sync.sincronizar())
        assertTrue(c.todas().isEmpty())
    }

    @Test fun unaFotoQueElServicioNoAceptaRechazaElCierre() {
        val c = cola()
        piezas(Servidor { sinRed }, c).entregas.cerrar(detalle, entregado(), foto, conRed = false)
        val s = Servidor { p -> if (p.ruta.endsWith("/documentos")) Salida.error(422, "Error.validacion") else respuestaLote(p) }
        assertEquals(Informe(rechazadas = 1), piezas(s, c).sync.sincronizar())
        assertEquals(listOf("POST /api/v1/documentos"), s.rutas())
        assertEquals(Operacion.RECHAZADA, c.todas().single().estado)
        assertNull(c.foto(c.todas().single().uuid))
    }

    @Test fun soloSeEnvianLasOperacionesDeQuienTieneLaSesion() {
        val c = cola()
        c.guardar(Operacion("2f0c3a1b-4d5e-4f60-8a9b-0c1d2e3f4a5b", Operacion.LECTURA, Contrato.fecha(ahora), """{"id":9}""", usuarioId = 99))
        val s = servidor()
        assertEquals(Informe(), piezas(s, c).sync.sincronizar())
        assertTrue(s.peticiones.isEmpty())
        assertEquals(0, piezas(s, c).sync.porEnviar())
    }

    @Test fun losLotesNoPasanDelMaximoDelServicio() {
        val c = cola()
        repeat(5) { c.guardar(Operacion(java.util.UUID.randomUUID().toString(), Operacion.LECTURA, Contrato.fecha(ahora), """{"id":${it + 1}}""", 7)) }
        val s = servidor()
        val api = clienteDe(s)
        assertEquals(Informe(aplicadas = 5), Sincronizador(api, c, maxLote = 2).sincronizar())
        assertEquals(3, s.peticiones.size)
        assertEquals(listOf(2, 2, 1), s.peticiones.map { it.json.getJSONArray("operaciones").length() })
    }

    // ------------------------------------------------------------------------------------------ cola en archivos y copias
    @Test fun laColaSobreviveAReabrirLaApp() {
        val dir = tmp.root.resolve("persistente")
        val a = ColaEnArchivos(dir) { ahora }
        val op = Operacion("6a0f3b5c-1d2e-4f70-8a9b-0c1d2e3f4a5b", Operacion.CIERRE, "2026-11-25T10:30:00-06:00", """{"entrega_id":163}""", 7, 163, "x")
        a.guardar(op); a.guardarFoto(op.uuid, foto)
        val b = ColaEnArchivos(dir) { ahora }
        assertEquals(listOf(op), b.todas()); assertArrayEquals(foto, b.foto(op.uuid))
        assertEquals("el dispositivo es estable", a.dispositivo, b.dispositivo)
        assertTrue(a.dispositivo.matches(Regex("[A-Za-z0-9._:-]{3,60}")))
        b.borrar(op.uuid)
        assertTrue(ColaEnArchivos(dir).todas().isEmpty()); assertNull(ColaEnArchivos(dir).foto(op.uuid))
        assertFalse("no quedan temporales", dir.walk().any { it.name.endsWith(".tmp") })
    }

    @Test fun sinRedLaListaYElDetalleSalenDeLaUltimaCopia() {
        var red = true
        val s = Servidor { p ->
            when {
                !red -> sinRed
                p.ruta.contains("entregas/mias") -> Salida.ok(Ejemplos.json("EntregaLista.ok"))
                else -> Salida.ok(Ejemplos.json("EntregaDetalle.ok"))
            }
        }
        val x = piezas(s)
        val enLinea = x.entregas.mias(1)
        assertNull(enLinea.guardadaEn)
        assertEquals(1, x.entregas.guardarParaSinRed(enLinea.items))
        red = false
        val copia = x.entregas.mias(1)
        assertEquals(ahora, copia.guardadaEn); assertEquals(enLinea.items, copia.items)
        assertEquals(detalle, x.entregas.detalle(61))
        try { x.entregas.mias(2); fail("sin copia de la página 2") } catch (_: IOException) {}
        x.cola.borrarCopias()
        try { x.entregas.mias(1); fail() } catch (_: IOException) {}
    }

    @Test fun elModoDeEjemplosSincronizaSinRed() {
        val c = cola()
        val api = Api(Memoria(), Servidor()::abrir, "10.0.2.2"); api.demo = true; api.login("demo@example.com", "x")
        val e = Entregas(api, BorradoresEnMemoria(), c) { ahora }
        e.cerrar(e.detalle(61), entregado(), foto, conRed = false)
        assertEquals(Informe(aplicadas = 1), Sincronizador(api, c).sincronizar())
        assertTrue(c.todas().isEmpty())
    }
}

/** El org.json que ve Gradle al compilar es el de Android: no tiene keySet() ni similar(). */
private fun llaves(o: JSONObject): Set<String> = o.keys().asSequence().toSet()

private fun canonico(v: Any?): String = when (v) {
    is JSONObject -> llaves(v).sorted().joinToString(",", "{", "}") { "$it:" + canonico(v.get(it)) }
    is org.json.JSONArray -> (0 until v.length()).joinToString(",", "[", "]") { canonico(v.get(it)) }
    else -> v.toString()
}
