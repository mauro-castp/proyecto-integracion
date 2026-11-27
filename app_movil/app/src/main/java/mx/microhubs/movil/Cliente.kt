package mx.microhubs.movil

import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException
import java.util.UUID
import kotlin.math.roundToLong

// Perfil cliente: catálogo (también guardado en el teléfono, en versión ligera), carrito, pedido (también sin red), estatus y confirmación
// de recepción. Sin dependencias de Android: se prueba en la JVM.

data class Producto(val id: Int, val nombre: String, val categoria: String, val unidad: String, val presentacion: String, val precio: Double)

/** `guardadoEn` ≠ null: no hubo red y es la copia ligera guardada en el teléfono (hora en milisegundos). */
data class Catalogo(val productos: List<Producto>, val guardadoEn: Long? = null) {
    val categorias get() = productos.map { it.categoria }.distinct().sorted()
    fun buscar(texto: String, categoria: String? = null): List<Producto> {
        val t = texto.trim().lowercase()
        return productos.filter { (categoria == null || it.categoria == categoria) && (t.isEmpty() || it.nombre.lowercase().contains(t)) }
    }
}

data class PedidoResumen(val id: Int, val folio: String, val estado: String, val total: Double, val creadoEn: String)
data class LineaPedido(val nombre: String, val cantidad: Int, val precio: Double, val importe: Double)
data class Evento(val estado: String, val fecha: String, val motivo: String?)
data class DetallePedido(
    val id: Int, val folio: String, val estado: String, val subtotal: Double, val costoEnvio: Double, val total: Double, val creadoEn: String,
    val lineas: List<LineaPedido>, val eventos: List<Evento>, val guardadoEn: Long? = null
) {
    /** El cliente puede cancelar mientras nadie lo prepara (transiciones de la base: creado o asignado → cancelado). */
    val cancelable get() = estado in setOf("creado", "asignado")
    /** Ya se entregó (completo o en parte): puede confirmar que lo recibió. */
    val confirmable get() = estado in setOf("entregado", "entrega_parcial")
}

/** Resultado de pedir: con red trae folio y total del servidor; sin red queda en cola (`enCola`) y sale al volver la conexión. */
data class PedidoHecho(val id: Int?, val folio: String?, val estado: String, val total: Double?, val duplicado: Boolean, val enCola: Boolean)

private fun dinero(v: Double) = (v * 100).roundToLong() / 100.0

/** Productos y cantidades elegidos. Las cantidades son enteras de 1 a 50 por producto (el servicio valida el límite de su zona). */
class Carrito {
    private val cantidades = linkedMapOf<Int, Int>()
    fun agregar(productoId: Int, n: Int = 1) {
        val nueva = ((cantidades[productoId] ?: 0) + n).coerceIn(0, MAX)
        if (nueva == 0) cantidades.remove(productoId) else cantidades[productoId] = nueva
    }
    fun quitar(productoId: Int) { agregar(productoId, -1) }
    fun cantidad(productoId: Int) = cantidades[productoId] ?: 0
    fun vaciar() = cantidades.clear()
    val vacio get() = cantidades.isEmpty()
    val piezas get() = cantidades.values.sum()
    fun items(): Map<Int, Int> = LinkedHashMap(cantidades)
    /** Total estimado con los precios del catálogo; el servidor calcula el definitivo (precio de la zona y costo de envío). */
    fun estimado(c: Catalogo): Double = dinero(cantidades.entries.sumOf { (id, n) -> (c.productos.firstOrNull { it.id == id }?.precio ?: 0.0) * n })
    fun lineas(): JSONArray = JSONArray(cantidades.map { (id, n) -> JSONObject().put("producto_id", id).put("cantidad", n) })

    companion object { const val MAX = 50 }
}

class Tienda(
    private val api: Api,
    private val cola: ColaSinRed? = null,
    private val ahora: () -> Long = { System.currentTimeMillis() }
) {
    /** Todo el catálogo activo (de 100 en 100). Con red guarda la copia ligera; sin red (IOException) devuelve la última copia. */
    fun catalogo(): Catalogo = try {
        val todos = mutableListOf<Producto>()
        var pagina = 1
        while (true) {
            val r = api.call("productos", "productos?estatus=activo&por_pagina=100&pagina=$pagina")
            val datos = r.getJSONArray("datos")
            for (i in 0 until datos.length()) todos += producto(datos.getJSONObject(i))
            if (pagina >= r.getJSONObject("paginacion").getInt("paginas") || pagina >= 20) break
            pagina++
        }
        Catalogo(todos.sortedWith(compareBy({ it.categoria }, { it.nombre }))).also { if (!api.demo) cola?.guardarCopia(CLAVE_CATALOGO, ligero(it)) }
    } catch (e: IOException) {
        guardado() ?: throw e
    }

    /** La copia ligera del teléfono, si hay. */
    fun guardado(): Catalogo? = cola?.copia(CLAVE_CATALOGO)?.let { (json, cuando) -> desdeLigero(json).copy(guardadoEn = cuando) }

    /**
     * Pide lo del carrito. El `operacion_uuid` se fija antes del primer intento: si la red se cae a medias y el pedido sí llegó, reenviarlo
     * no lo duplica. Sin red el pedido queda en la cola y lo manda la sincronización (tipo pedido_nuevo) con el mismo uuid.
     */
    fun pedir(carrito: Carrito, conRed: Boolean = true): PedidoHecho {
        require(!carrito.vacio) { "Agrega al menos un producto." }
        val uuid = UUID.randomUUID().toString()
        val datos = JSONObject().put("lineas", carrito.lineas())
        if (conRed) {
            try {
                val r = api.call("pedidos", "pedidos", "POST", JSONObject(datos.toString()).put("operacion_uuid", uuid))
                carrito.vaciar()
                return PedidoHecho(r.getInt("id"), r.getString("folio"), r.getString("estado"), r.getDouble("total"), r.optBoolean("duplicado"), false)
            } catch (e: IOException) {
                if (cola == null) throw e
            }
        }
        val c = cola ?: throw IOException("Sin conexión")
        val usuario = api.session?.optJSONObject("usuario")?.optInt("id")?.takeIf { it > 0 } ?: throw IllegalStateException("La sesión terminó; vuelve a entrar")
        c.guardar(Operacion(uuid, PEDIDO, Contrato.fecha(ahora()), datos.toString(), usuario, null, "Pedido de ${carrito.piezas} pieza(s)"))
        carrito.vaciar()
        return PedidoHecho(null, null, "en_cola", null, false, true)
    }

    fun misPedidos(pagina: Int): Pagina<PedidoResumen> {
        val (r, guardada) = conCopia("pedidos-$pagina") { api.call("pedidos", "pedidos?pagina=$pagina&por_pagina=20") }
        val datos = r.getJSONArray("datos")
        val p = r.getJSONObject("paginacion")
        return Pagina((0 until datos.length()).map { resumen(datos.getJSONObject(it)) }, p.getInt("pagina"), p.getInt("paginas"), p.getInt("total"), guardada)
    }

    fun detalle(id: Int): DetallePedido {
        val (d, guardada) = conCopia("pedido-$id") { api.call("pedidos", "pedidos/$id") }
        val historial = try { conCopia("historial-$id") { api.call("pedidos", "pedidos/$id/historial") }.first } catch (_: IOException) { JSONObject().put("eventos", JSONArray()) }
        return detalle(d, historial).copy(guardadoEn = guardada)
    }

    fun cancelar(id: Int, motivo: String): DetallePedido {
        require(motivo.trim().length >= 3) { "Escribe por qué cancelas." }
        api.call("pedidos", "pedidos/$id/estado", "POST", JSONObject().put("estado", "cancelado").put("motivo", motivo.trim()))
        return detalle(id)
    }

    /** Confirma (o no) que recibió el pedido. Solo con el pedido ya entregado; el servidor lo vuelve a revisar. */
    fun confirmarRecepcion(id: Int, conforme: Boolean): JSONObject =
        api.call("entregas", "entregas/recepciones", "POST", JSONObject().put("pedido_id", id).put("conforme", conforme))

    private fun conCopia(clave: String, leer: () -> JSONObject): Pair<JSONObject, Long?> = try {
        leer().also { if (!api.demo) cola?.guardarCopia(clave, it) } to null
    } catch (e: IOException) {
        val (json, cuando) = cola?.copia(clave) ?: throw e
        json to cuando
    }

    companion object {
        const val PEDIDO = "pedido_nuevo"
        const val CLAVE_CATALOGO = "catalogo-ligero"

        fun producto(o: JSONObject) = Producto(o.getInt("id"), o.getString("nombre"), o.optJSONObject("categoria")?.optString("nombre") ?: "Otros",
            o.optString("unidad"), if (o.isNull("presentacion")) "" else o.optString("presentacion"), o.getDouble("precio"))

        /** Solo lo que hace falta para elegir sin red: sin imágenes, claves internas ni estatus (cabe en unos pocos KB). */
        fun ligero(c: Catalogo): JSONObject = JSONObject().put("version", 1).put("productos", JSONArray(c.productos.map {
            JSONArray().put(it.id).put(it.nombre).put(it.categoria).put(it.unidad).put(it.presentacion).put(it.precio)
        }))

        fun desdeLigero(o: JSONObject): Catalogo {
            val a = o.getJSONArray("productos")
            return Catalogo((0 until a.length()).map { a.getJSONArray(it).let { p -> Producto(p.getInt(0), p.getString(1), p.getString(2), p.getString(3), p.getString(4), p.getDouble(5)) } })
        }

        fun resumen(o: JSONObject) = PedidoResumen(o.getInt("id"), o.getString("folio"), o.getString("estado"), o.getDouble("total"), o.optString("creado_en"))

        fun detalle(o: JSONObject, historial: JSONObject): DetallePedido {
            val ls = o.optJSONArray("lineas") ?: JSONArray()
            val ev = historial.optJSONArray("eventos") ?: JSONArray()
            return DetallePedido(o.getInt("id"), o.getString("folio"), o.getString("estado"), o.optDouble("subtotal", 0.0), o.optDouble("costo_envio", 0.0),
                o.getDouble("total"), o.optString("creado_en"),
                (0 until ls.length()).map { ls.getJSONObject(it).let { l -> LineaPedido(l.getString("nombre"), l.getInt("cantidad"), l.optDouble("precio_unitario", 0.0), l.optDouble("importe", 0.0)) } },
                (0 until ev.length()).map { ev.getJSONObject(it).let { e -> Evento(e.getString("estado_nuevo"), e.getString("fecha"), if (e.isNull("motivo")) null else e.optString("motivo")) } })
        }

        /** Nombre del estado para el cliente. */
        fun estadoLegible(e: String) = when (e) {
            "creado", "pendiente_asignacion" -> "Recibido"; "asignado" -> "Confirmado"; "en_preparacion" -> "En preparación"; "en_ruta" -> "En camino"
            "entregado" -> "Entregado"; "entrega_parcial" -> "Entregado en parte"; "entrega_fallida" -> "No se pudo entregar"; "cancelado" -> "Cancelado"
            "en_cola" -> "Por enviar (sin red)"; else -> e
        }
    }
}
