package mx.microhubs.movil

import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
import java.io.IOException

/** Entregas: lectura del contrato, reglas previas al envío y cierre idempotente (reintentos sin duplicar). */
class EntregasTest {
    private val ahora = 1_760_300_000_000L
    private val fotoJpeg = byteArrayOf(0xFF.toByte(), 0xD8.toByte(), 0xFF.toByte(), 0xE0.toByte(), 1, 2, 3)
    private val detalle = Contrato.detalle(Ejemplos.json("EntregaDetalle.ok"))      // total 158.00, líneas 51 (x2) y 52 (x4)
    private fun fix(edadMs: Long = 5_000) = Fix(25.7491, -100.3611, 8.5, ahora - edadMs)
    private fun entregado() = DatosCierre("entregado", 158.0, 0.0, "", emptyList(), fix())
    private fun parcial(devueltas: Int = 4, motivo: String = "El cliente la rechazó.", monto: Double = 80.0) = DatosCierre("parcial", monto, 20.0, "Rechazó el agua.",
        listOf(LineaCierre(detalle.lineas[0], 0, ""), LineaCierre(detalle.lineas[1], devueltas, motivo)), fix())
    private fun fallida(nota: String = "Cliente ausente en dos intentos.", monto: Double = 0.0) = DatosCierre("fallida", monto, 0.0, nota, emptyList(), fix())

    /** Servidor que acepta documentos, ubicaciones y cierres; `resultado` decide la respuesta del cierre. */
    private fun servidor(resultado: (Peticion) -> Salida = { Salida.ok(Ejemplos.json("ResultadoEntregaRespuesta.ok"), 201) }) = Servidor { p ->
        when {
            p.ruta.endsWith("/documentos") -> Salida.ok(Ejemplos.json("Documento.ok"), 201)
            p.ruta.endsWith("/ubicaciones") -> Salida.ok(Ejemplos.json("UbicacionesRecibidas.ok"), 202)
            p.ruta.endsWith("/resultado") -> resultado(p)
            else -> Salida(404)
        }
    }
    private fun entregas(s: Servidor, b: Borradores = BorradoresEnMemoria()) = Entregas(clienteDe(s), b) { ahora }

    // ------------------------------------------------------------------------------------------ lectura
    @Test fun leeLaListaYElDetalleDelContrato() {
        val s = Servidor { p -> if (p.ruta.contains("entregas/mias")) Salida.ok(Ejemplos.json("EntregaLista.ok")) else Salida.ok(Ejemplos.json("EntregaDetalle.ok")) }
        val e = entregas(s)
        val pagina = e.mias(1)
        assertEquals("GET /api/v1/entregas/mias?pagina=1&por_pagina=20", s.ultima().toString())
        assertEquals(Parada(61, 20, "PED-20260930-000020", "en_ruta", 3, "Av. Rodrigo Gómez 1420, San Bernabé", "San Bernabé Centro", 158.0), pagina.items[0])
        assertEquals(1, pagina.paginas)
        val d = e.detalle(61)
        assertEquals(2, d.lineas.size); assertEquals("Laura Pérez", d.cliente); assertEquals(158.0, d.total, 0.0)
    }

    // ------------------------------------------------------------------------------------------ reglas previas al envío
    private fun rechaza(datos: DatosCierre, parte: String) {
        try { entregas(servidor()).validar(detalle, datos); fail("debía rechazar: $parte") } catch (e: IllegalArgumentException) { assertTrue(e.message, e.message!!.contains(parte)) }
    }
    @Test fun entregadoExigeElTotalExacto() { entregas(servidor()).validar(detalle, entregado()); rechaza(DatosCierre("entregado", 150.0, 0.0, "", emptyList(), fix()), "igual al total") }
    @Test fun parcialExigeLineasDevueltasConMotivo() {
        entregas(servidor()).validar(detalle, parcial())
        rechaza(parcial(devueltas = 0), "Indica qué líneas")
        rechaza(parcial(motivo = " "), "explica por qué")
        rechaza(parcial(devueltas = 9), "entre 0 y 4")
        rechaza(parcial(monto = 500.0), "superar el total")
    }
    @Test fun fallidaExigeIncidenciaYNoCobra() { entregas(servidor()).validar(detalle, fallida()); rechaza(fallida(nota = ""), "Describe por qué"); rechaza(fallida(monto = 10.0), "no cobra") }
    @Test fun elGpsDebeSerReciente() { rechaza(DatosCierre("entregado", 158.0, 0.0, "", emptyList(), fix(edadMs = 121_000)), "más de 2 minutos") }
    @Test fun elGpsDebeSerValido() { rechaza(DatosCierre("entregado", 158.0, 0.0, "", emptyList(), Fix(200.0, 0.0, null, ahora)), "no es válida") }
    @Test fun noAceptaResultadosDesconocidos() { rechaza(DatosCierre("quizas", 158.0, 0.0, "", emptyList(), fix()), "desconocido") }

    // ------------------------------------------------------------------------------------------ cierre
    @Test fun cierraLaEntregaConElOrdenYElCuerpoDelContrato() {
        val s = servidor(); val b = BorradoresEnMemoria()
        val r = entregas(s, b).cerrar(detalle, entregado(), fotoJpeg, listOf(fix(60_000), fix(30_000)))
        assertEquals(Resultado("entrega_parcial", false), r)
        assertEquals(listOf("POST /api/v1/documentos", "POST /api/v1/entregas/61/ubicaciones", "POST /api/v1/entregas/61/resultado"), s.rutas())
        val doc = s.peticiones[0].json
        assertEquals("image/jpeg", doc.getString("tipo_mime")); assertEquals("entrega", doc.getJSONObject("referencia").getString("tipo")); assertEquals("61", doc.getJSONObject("referencia").getString("id"))
        assertArrayEquals(fotoJpeg, java.util.Base64.getDecoder().decode(doc.getString("contenido_base64")))
        assertEquals(2, s.peticiones[1].json.getJSONArray("puntos").length())
        val cuerpo = s.peticiones[2].json
        assertEquals("entregado", cuerpo.getString("resultado")); assertEquals(158.0, cuerpo.getDouble("monto_cobrado"), 0.0)
        assertEquals("665f1c2e8a3b4d0012a7c9e1", cuerpo.getJSONArray("evidencia_ids").getString(0))
        assertEquals(25.7491, cuerpo.getJSONObject("ubicacion").getDouble("latitud"), 0.0)
        assertTrue(cuerpo.getString("capturado_en").matches(Regex("""\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d\d:\d\d""")))
        assertTrue(cuerpo.getString("id_cliente_local").matches(Regex("[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}")))
        assertFalse(cuerpo.has("lineas")); assertFalse(cuerpo.has("incidencia"))
        assertFalse(b.cargar(61) != null)                       // el éxito borra el borrador
    }

    @Test fun elCuerpoParcialTieneExactamenteLasClavesDelEjemploOficial() {
        val s = servidor(); entregas(s).cerrar(detalle, parcial(), fotoJpeg)
        val enviado = s.peticiones.last().json; val oficial = Ejemplos.json("ResultadoEntrega.parcial")
        fun claves(o: JSONObject): Set<String> = o.keys().asSequence().toSet()
        assertEquals(claves(oficial), claves(enviado))
        assertEquals(claves(oficial.getJSONObject("ubicacion")), claves(enviado.getJSONObject("ubicacion")))
        assertEquals(claves(oficial.getJSONArray("lineas").getJSONObject(1)), claves(enviado.getJSONArray("lineas").getJSONObject(1)))
        assertEquals(setOf("pedido_detalle_id", "cantidad_entregada", "cantidad_devuelta"), claves(enviado.getJSONArray("lineas").getJSONObject(0)))
        assertEquals(2, enviado.getJSONArray("lineas").getJSONObject(0).getInt("cantidad_entregada"))
        assertEquals(0, enviado.getJSONArray("lineas").getJSONObject(1).getInt("cantidad_entregada"))
    }

    @Test fun unFalloDeRedNoDuplicaNiPierdeLaEvidencia() {
        var intentos = 0
        val s = servidor { if (intentos++ == 0) Salida(0, fallo = IOException("tiempo de espera agotado")) else Salida.ok(Ejemplos.json("ResultadoEntregaRespuesta.ok"), 201) }
        val b = BorradoresEnMemoria(); val e = entregas(s, b)
        try { e.cerrar(detalle, entregado(), fotoJpeg); fail() } catch (_: IOException) {}
        val uuid = b.cargar(61)!!.idClienteLocal
        assertEquals("665f1c2e8a3b4d0012a7c9e1", b.cargar(61)!!.evidenciaId)
        assertTrue(e.hayCierrePendiente(61) && e.tieneEvidencia(61))
        e.cerrar(detalle, entregado(), null)                                      // el reintento ya no necesita la foto
        val cierres = s.peticiones.filter { it.ruta.endsWith("/resultado") }
        assertEquals(2, cierres.size)
        assertEquals(uuid, cierres[0].json.getString("id_cliente_local")); assertEquals(uuid, cierres[1].json.getString("id_cliente_local"))
        assertEquals(1, s.peticiones.count { it.ruta.endsWith("/documentos") })      // la foto se subió una sola vez
        assertNull(b.cargar(61))
    }

    @Test fun un200DuplicadoEsExito() {
        val s = servidor { Salida.ok(Ejemplos.json("ResultadoEntregaRespuesta.ok").put("duplicado", true), 200) }
        val b = BorradoresEnMemoria()
        val r = entregas(s, b).cerrar(detalle, entregado(), fotoJpeg)
        assertTrue(r.duplicado); assertNull(b.cargar(61))
    }

    @Test fun unError422ConservaElIdentificadorParaCorregirYReintentar() {
        var primero = true
        val s = servidor { if (primero) { primero = false; Salida.error(422, "Error.validacion") } else Salida.ok(Ejemplos.json("ResultadoEntregaRespuesta.ok"), 201) }
        val b = BorradoresEnMemoria(); val e = entregas(s, b)
        try { e.cerrar(detalle, entregado(), fotoJpeg); fail() } catch (x: ApiError) { assertEquals(422, x.status) }
        val uuid = b.cargar(61)!!.idClienteLocal
        e.cerrar(detalle, entregado(), null)
        assertEquals(uuid, s.peticiones.last().json.getString("id_cliente_local"))
    }

    @Test fun unError409DescartaElBorradorPorqueYaSeCerro() {
        val s = servidor { Salida(409, cuerpo = """{"error":{"codigo":"CONFLICTO","mensaje":"El pedido está en estado «entregado»; no se puede cerrar la entrega.","traza_id":"t"}}""") }
        val b = BorradoresEnMemoria()
        try { entregas(s, b).cerrar(detalle, entregado(), fotoJpeg); fail() } catch (x: ApiError) { assertEquals(409, x.status) }
        assertNull(b.cargar(61))
    }

    @Test fun sinFotoNiEvidenciaPreviaNoSeEnviaNada() {
        val s = servidor()
        try { entregas(s).cerrar(detalle, entregado(), null); fail() } catch (e: IllegalArgumentException) { assertTrue(e.message!!.contains("foto")) }
        assertTrue(s.peticiones.none { it.ruta.endsWith("/resultado") })
    }

    @Test fun losPuntosGpsSonAccesoriosYNoImpidenElCierre() {
        val s = Servidor { p ->
            when {
                p.ruta.endsWith("/documentos") -> Salida.ok(Ejemplos.json("Documento.ok"), 201)
                p.ruta.endsWith("/ubicaciones") -> Salida.error(422, "Error.validacion")
                else -> Salida.ok(Ejemplos.json("ResultadoEntregaRespuesta.ok"), 201)
            }
        }
        assertFalse(entregas(s).cerrar(detalle, entregado(), fotoJpeg, listOf(fix())).duplicado)
    }

    @Test fun losPuntosSeEnvianEnLotesDeMaximo500() {
        val s = servidor()
        entregas(s).cerrar(detalle, entregado(), fotoJpeg, List(1200) { fix() })
        assertEquals(listOf(500, 500, 200), s.peticiones.filter { it.ruta.endsWith("/ubicaciones") }.map { it.json.getJSONArray("puntos").length() })
    }
}
