package mx.microhubs.movil

import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
import java.io.File

/** Los ejemplos oficiales del contrato v1 (los mismos que validan los servicios) pasan por el código de la app. */
class ContratoTest {
    private val ejemplos: List<File> = File(ContratoTest::class.java.classLoader!!.getResource("contratos")!!.toURI()).listFiles { f -> f.name.endsWith(".json") }!!.sortedBy { it.name }

    @Test fun losEjemplosSonJsonValidoYSeCargaronTodos() {
        assertTrue("faltan ejemplos: ${ejemplos.size}", ejemplos.size >= 53)
        ejemplos.forEach { JSONObject(it.readText(Charsets.UTF_8)) }
    }

    @Test fun laSesionTraeLoQueLaAppNecesita() {
        val s = Ejemplos.json("Sesion.ok")
        listOf("token_acceso", "token_renovacion", "tipo", "expira_en", "usuario").forEach { assertTrue(it, s.has(it)) }
        val u = s.getJSONObject("usuario")
        listOf("id", "nombre", "apellidos", "correo", "rol", "permisos").forEach { assertTrue(it, u.has(it)) }
        assertEquals("Bearer", s.getString("tipo"))
    }

    @Test fun laRenovacionSoloTraeTokens() {
        val t = Ejemplos.json("Tokens.ok")
        assertFalse(t.has("usuario"))                           // por eso la app conserva el `usuario` de la sesión anterior
        listOf("token_acceso", "token_renovacion", "tipo", "expira_en").forEach { assertTrue(it, t.has(it)) }
    }

    @Test fun lasEntregasSeLeenConLosCamposDelContrato() {
        val p = Contrato.parada(Ejemplos.json("Entrega.ok"))
        assertEquals(61, p.id); assertEquals(20, p.pedidoId); assertEquals("en_ruta", p.estado); assertEquals(3, p.orden); assertEquals(158.0, p.total, 0.0)
        val d = Contrato.detalle(Ejemplos.json("EntregaDetalle.ok"))
        assertEquals(51, d.lineas[0].pedidoDetalleId); assertEquals("Arroz", d.lineas[0].nombre); assertEquals(4, d.lineas[1].cantidad)
        assertTrue(d.direccion.startsWith("Av. Rodrigo Gómez 1420"))
    }

    @Test fun lasNotificacionesSeLeenConLosCamposDelContrato() {
        val a = Contrato.aviso(Ejemplos.json("Notificacion.ok"))
        assertEquals(310, a.id); assertFalse(a.leida); assertEquals("Nueva entrega asignada", a.titulo)
        assertEquals(1, Ejemplos.json("Conteo.ok").length())
    }

    @Test fun losErroresDelContratoTienenLaEstructuraQueLaAppInterpreta() {
        listOf("Error.validacion", "Error.no_encontrado", "Error.token_invalido").forEach {
            val e = Ejemplos.json(it).getJSONObject("error")
            listOf("codigo", "mensaje", "traza_id").forEach { campo -> assertTrue("$it/$campo", e.has(campo)) }
        }
        assertEquals("cantidad", Ejemplos.json("Error.validacion").getJSONObject("error").getJSONArray("detalles").getJSONObject(0).getString("campo"))
    }

    @Test fun lasFechasSalenEnIso8601ConZonaYSegundos() {
        val f = Contrato.fecha(1_760_300_000_000L)
        assertTrue(f, f.matches(Regex("""\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d\d:\d\d""")))
        assertEquals(1_760_300_000L, java.time.OffsetDateTime.parse(f).toEpochSecond())
    }

    @Test fun elResultadoParcialOficialEsCoherenteConLasReglasDeLaApp() {
        val r = Ejemplos.json("ResultadoEntrega.parcial")
        val lineas = r.getJSONArray("lineas")
        val detalle = Contrato.detalle(Ejemplos.json("EntregaDetalle.ok"))
        val cierre = DatosCierre("parcial", r.getDouble("monto_cobrado"), r.getDouble("cambio_entregado"), r.getString("incidencia"),
            (0 until lineas.length()).map { i -> lineas.getJSONObject(i).let { l ->
                LineaCierre(detalle.lineas.first { it.pedidoDetalleId == l.getInt("pedido_detalle_id") }, l.getInt("cantidad_devuelta"), l.optString("motivo")) } },
            Fix(25.7491, -100.3611, 8.5, 1_000))
        Entregas(clienteDe(Servidor()), BorradoresEnMemoria()) { 1_000 }.validar(detalle, cierre)    // no lanza
    }
}
