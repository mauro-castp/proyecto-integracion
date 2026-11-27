package mx.microhubs.movil

import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.IOException

/** Perfil cliente: catálogo ligero sin red, carrito, pedido idempotente (también sin red, por sincronización), estatus y recepción. */
class ClienteTest {
    @get:Rule val tmp = TemporaryFolder()
    private var ahora = 1_790_000_000_000L
    private val sinRed = Salida(0, fallo = IOException("sin red"))
    private fun cola() = ColaEnArchivos(tmp.root.resolve("sin_red")) { ahora }
    private fun producto(id: Int, nombre: String, cat: String, precio: Double) = JSONObject(Ejemplos.texto("ProductoLista.ok")).getJSONArray("datos").getJSONObject(0)
        .put("id", id).put("nombre", nombre).put("precio", precio).put("categoria", JSONObject().put("id", 1).put("nombre", cat))
    private fun pagina(productos: List<JSONObject>, pagina: Int, paginas: Int) = JSONObject().put("datos", JSONArray(productos))
        .put("paginacion", JSONObject().put("pagina", pagina).put("por_pagina", 100).put("total", 3).put("paginas", paginas))
    private val catalogoServidor = Servidor { p ->
        when {
            p.ruta.contains("/productos") && p.ruta.endsWith("&pagina=1") -> Salida.ok(pagina(listOf(producto(12, "Arroz", "Abarrote", 32.5), producto(3, "Frijol", "Abarrote", 42.0)), 1, 2))
            p.ruta.contains("/productos") && p.ruta.endsWith("&pagina=2") -> Salida.ok(pagina(listOf(producto(7, "Cloro", "Limpieza", 18.0)), 2, 2))
            else -> Salida(404)
        }
    }

    @Test fun elCatalogoSeLeeCompletoYQuedaUnaCopiaLigeraParaSinRed() {
        val c = cola()
        val cat = Tienda(clienteDe(catalogoServidor), c) { ahora }.catalogo()
        assertEquals(listOf("Arroz", "Frijol", "Cloro"), cat.productos.map { it.nombre })       // ordenado por categoría y nombre, las dos páginas
        assertTrue(catalogoServidor.rutas().all { it.startsWith("GET /api/v1/productos?estatus=activo&por_pagina=100") })
        val copia = c.copia(Tienda.CLAVE_CATALOGO)!!.first.toString()
        assertFalse("la copia ligera no lleva imágenes ni claves internas", copia.contains("imagen_url") || copia.contains("clave_interna"))
        ahora += 3_600_000
        val sin = Tienda(clienteDe(Servidor { sinRed }), c) { ahora }.catalogo()
        assertEquals(cat.productos, sin.productos)
        assertNotNull("sin red avisa de cuándo es la copia", sin.guardadoEn)
        assertEquals(listOf("Abarrote", "Limpieza"), sin.categorias)
        assertEquals(listOf("Cloro"), sin.buscar("clo").map { it.nombre })
        assertEquals(2, sin.buscar("", "Abarrote").size)
    }

    @Test fun sinRedYSinCopiaElCatalogoAvisaDelError() {
        try { Tienda(clienteDe(Servidor { sinRed }), cola()).catalogo(); fail("debía fallar") } catch (_: IOException) {}
    }

    @Test fun elCarritoSumaCantidadesYNoPasaDelLimite() {
        val k = Carrito()
        k.agregar(12, 2); k.agregar(3); k.quitar(3); k.quitar(3)
        assertEquals(mapOf(12 to 2), k.items())
        k.agregar(7, 80)
        assertEquals(Carrito.MAX, k.cantidad(7))
        val cat = Catalogo(listOf(Producto(12, "Arroz", "A", "pieza", "", 32.5), Producto(7, "Cloro", "L", "pieza", "", 18.0)))
        assertEquals(2 * 32.5 + 50 * 18.0, k.estimado(cat), 0.001)
        assertEquals(listOf(12 to 2, 7 to 50), (0 until k.lineas().length()).map { k.lineas().getJSONObject(it).let { l -> l.getInt("producto_id") to l.getInt("cantidad") } })
    }

    @Test fun conRedElPedidoLlevaSuOperacionUuidYVaciaElCarrito() {
        val s = Servidor { Salida.ok(Ejemplos.json("PedidoCreado.ok"), 201) }
        val k = Carrito().apply { agregar(3, 4); agregar(7, 2) }
        val r = Tienda(clienteDe(s), cola()).pedir(k)
        assertEquals(PedidoHecho(901, "PED-20261126-000901", "asignado", 201.0, false, false), r)
        val cuerpo = s.ultima().json
        assertEquals("POST /api/v1/pedidos", s.ultima().toString())
        assertEquals(36, cuerpo.getString("operacion_uuid").length)
        assertEquals(2, cuerpo.getJSONArray("lineas").length())
        assertTrue(k.vacio)
    }

    @Test fun sinRedElPedidoQuedaEnLaColaYLoMandaLaSincronizacionConElMismoUuid() {
        val c = cola()
        val k = Carrito().apply { agregar(3, 4) }
        val apiSin = clienteDe(Servidor { sinRed })
        val r = Tienda(apiSin, c) { ahora }.pedir(k)                    // intentó con red, se cayó: a la cola
        assertTrue(r.enCola); assertTrue(k.vacio)
        val op = c.todas().single()
        assertEquals(Tienda.PEDIDO, op.tipo)
        val datos = JSONObject(op.datos).getJSONArray("lineas").getJSONObject(0)
        assertEquals(3, datos.getInt("producto_id")); assertEquals(4, datos.getInt("cantidad")); assertEquals(1, JSONObject(op.datos).length())
        assertEquals("Pedido de 4 pieza(s)", op.descripcion)

        var enviado: JSONObject? = null
        val s = Servidor { p ->
            enviado = p.json
            val o = p.json.getJSONArray("operaciones").getJSONObject(0)
            Salida.ok(JSONObject().put("id", 1).put("lote_uuid", p.json.getString("lote_uuid")).put("total", 1).put("aplicadas", 1).put("operaciones", JSONArray().put(
                JSONObject().put("operacion_uuid", o.getString("operacion_uuid")).put("tipo", o.getString("tipo")).put("estado", "aplicada").put("duplicada", false)
                    .put("http_status", 201).put("codigo", JSONObject.NULL).put("mensaje", JSONObject.NULL).put("reintentar", false))), 201)
        }
        val i = Sincronizador(clienteDe(s), c).sincronizar()
        assertEquals(1, i.aplicadas)
        val sobre = enviado!!.getJSONArray("operaciones").getJSONObject(0)
        assertEquals(op.uuid, sobre.getString("operacion_uuid"))
        assertEquals("pedido_nuevo", sobre.getString("tipo"))
        assertTrue(c.todas().isEmpty())
    }

    @Test fun sinRedDeclaradaNiSiquieraIntenta() {
        val s = Servidor { Salida(500) }
        Tienda(clienteDe(s), cola()).pedir(Carrito().apply { agregar(3) }, conRed = false)
        assertTrue(s.peticiones.isEmpty())
    }

    @Test fun unCarritoVacioNoSePide() {
        try { Tienda(clienteDe(Servidor()), cola()).pedir(Carrito()); fail("debía rechazar") } catch (e: IllegalArgumentException) { assertTrue(e.message!!.contains("al menos un producto")) }
    }

    @Test fun misPedidosYSuDetalleConSeguimiento() {
        val s = Servidor { p ->
            when {
                p.ruta.endsWith("/historial") -> Salida.ok(Ejemplos.json("Historial.ok"))
                p.ruta.matches(Regex(".*/pedidos/[0-9]+")) -> Salida.ok(Ejemplos.json("PedidoDetalle.ok"))
                p.ruta.contains("/pedidos?") -> Salida.ok(Ejemplos.json("PedidoLista.ok"))
                else -> Salida(404)
            }
        }
        val c = cola(); val t = Tienda(clienteDe(s), c) { ahora }
        val lista = t.misPedidos(1)
        assertEquals("PED-20260930-000020", lista.items.single().folio)
        val d = t.detalle(20)
        assertEquals(158.0, d.total, 0.001); assertEquals(15.0, d.costoEnvio, 0.001)
        assertEquals("Arroz", d.lineas.first().nombre)
        assertEquals(listOf("creado", "asignado", "en_preparacion"), d.eventos.map { it.estado })
        assertFalse(d.cancelable); assertFalse(d.confirmable)
        assertEquals("En camino", Tienda.estadoLegible(d.estado))
        val sin = Tienda(clienteDe(Servidor { sinRed }), c) { ahora }.detalle(20)
        assertEquals(d.copy(guardadoEn = sin.guardadoEn), sin)
        assertNotNull(sin.guardadoEn)
    }

    @Test fun confirmarRecepcionYCancelar() {
        val s = Servidor { p ->
            when {
                p.ruta.endsWith("/recepciones") -> Salida.ok(Ejemplos.json("RecepcionCliente.ok"))
                p.ruta.endsWith("/historial") -> Salida.ok(Ejemplos.json("Historial.ok"))
                p.ruta.endsWith("/estado") -> Salida.ok(Ejemplos.json("PedidoLista.ok").getJSONArray("datos").getJSONObject(0).put("estado", "cancelado"))
                else -> Salida.ok(Ejemplos.json("PedidoDetalle.ok").put("estado", "cancelado"))
            }
        }
        val t = Tienda(clienteDe(s), cola())
        assertTrue(t.confirmarRecepcion(901, true).getBoolean("conforme"))
        assertEquals(901, s.ultima().json.getInt("pedido_id")); assertTrue(s.ultima().json.getBoolean("conforme")); assertEquals(2, s.ultima().json.length())
        assertEquals("POST /api/v1/entregas/recepciones", s.ultima().toString())
        try { t.cancelar(20, " "); fail("sin motivo no se cancela") } catch (_: IllegalArgumentException) {}
        assertEquals("cancelado", t.cancelar(20, "Ya no lo necesito").estado)
        assertTrue(s.rutas().contains("POST /api/v1/pedidos/20/estado"))
    }

    @Test fun lasReglasDeCancelarYConfirmarSiguenElEstado() {
        val base = Tienda.detalle(Ejemplos.json("PedidoDetalle.ok"), JSONObject())
        assertTrue(base.copy(estado = "asignado").cancelable); assertFalse(base.copy(estado = "en_preparacion").cancelable)
        assertTrue(base.copy(estado = "entrega_parcial").confirmable); assertFalse(base.copy(estado = "entrega_fallida").confirmable)
    }

    @Test fun navegarAbreElDomicilioEnLaAppDeMapas() {
        val d = Contrato.detalle(Ejemplos.json("EntregaDetalle.ok"))
        assertEquals("geo:25.749,-100.361?q=25.749,-100.361(PED-20260930-000020)", d.destinoMapa)
        assertNull(d.copy(latitud = null).destinoMapa)
    }
}
