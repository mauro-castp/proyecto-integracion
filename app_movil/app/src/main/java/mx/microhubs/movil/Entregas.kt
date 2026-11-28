package mx.microhubs.movil

import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.UUID
import kotlin.math.abs
import kotlin.math.roundToLong

// Modelos de lo que la app lee del contrato v1 (entregas y perfil). Sin dependencias de Android: se prueban en la JVM.
/** `guardadaEn` ≠ null: no hubo red y se muestra la última copia guardada en el teléfono (hora en milisegundos). */
data class Pagina<T>(val items: List<T>, val pagina: Int, val paginas: Int, val total: Int, val guardadaEn: Long? = null)
data class Parada(
    val id: Int, val pedidoId: Int, val folio: String, val estado: String, val orden: Int, val direccion: String, val zona: String,
    val total: Double, val distanciaKm: Double = 0.0, val minutos: Double = 0.0
)
data class Linea(val pedidoDetalleId: Int, val nombre: String, val cantidad: Int)

/** El microhub del repartidor (servicio de microhubs): dónde está y hasta dónde cubre. Solo informa: la regla la aplica el servidor. */
data class Sede(val clave: String, val nombre: String, val latitud: Double, val longitud: Double, val radioKm: Double) {
    /** Distancia en línea recta (Haversine, km), la misma medida con la que el sistema calcula la cobertura. */
    fun distanciaKm(lat: Double, lng: Double): Double {
        val dLat = Math.toRadians(lat - latitud); val dLng = Math.toRadians(lng - longitud)
        val h = Math.sin(dLat / 2).let { it * it } +
            Math.cos(Math.toRadians(latitud)) * Math.cos(Math.toRadians(lat)) * Math.sin(dLng / 2).let { it * it }
        return 2 * 6371.0088 * Math.asin(Math.sqrt(h))
    }

    fun cobertura(lat: Double, lng: Double): String {
        val d = distanciaKm(lat, lng)
        val estado = if (d <= radioKm) "Dentro de la cobertura" else "Fuera de la cobertura"
        return "$estado: a %.2f km de tu microhub %s (cubre %.1f km)".format(d, clave, radioKm)
    }

    val destinoMapa: String get() = "geo:$latitud,$longitud?q=$latitud,$longitud(" + java.net.URLEncoder.encode("$clave $nombre", "UTF-8") + ")"

    companion object {
        fun leer(o: JSONObject) = Sede(o.getString("clave"), o.getString("nombre"), o.getDouble("latitud"), o.getDouble("longitud"), o.getDouble("radio_km"))
    }
}
data class Detalle(
    val id: Int, val pedidoId: Int, val folio: String, val estado: String, val cliente: String, val telefono: String,
    val direccion: String, val total: Double, val lineas: List<Linea>, val latitud: Double? = null, val longitud: Double? = null
) {
    /** Para «Navegar»: abre la app de mapas del teléfono en el domicilio (geo: lo entiende cualquier app de mapas). */
    val destinoMapa: String? get() = if (latitud == null || longitud == null) null
        else "geo:$latitud,$longitud?q=$latitud,$longitud(" + java.net.URLEncoder.encode(folio, "UTF-8") + ")"
}

/** Posición GPS capturada en el teléfono. `tiempoMs` es la hora del fix (época), no la del envío. */
data class Fix(val latitud: Double, val longitud: Double, val precisionM: Double?, val tiempoMs: Long)
class LineaCierre(val linea: Linea, val devueltas: Int, val motivo: String)
class DatosCierre(
    val resultado: String, val montoCobrado: Double, val cambio: Double, val incidencia: String,
    val lineas: List<LineaCierre>, val fix: Fix
)
/** `enCola` = no había red: el cierre quedó guardado en el teléfono y se enviará con la sincronización (estadoPedido es el esperado). */
data class Resultado(val estadoPedido: String, val duplicado: Boolean, val enCola: Boolean = false)

/** Lo necesario para reintentar un cierre sin duplicarlo: el UUID de la operación y la evidencia ya subida. */
class Borrador(val idClienteLocal: String, var evidenciaId: String? = null)
interface Borradores {
    fun cargar(entregaId: Int): Borrador?
    fun guardar(entregaId: Int, borrador: Borrador)
    fun borrar(entregaId: Int)
}
class BorradoresEnMemoria : Borradores {
    private val datos = mutableMapOf<Int, Borrador>()
    override fun cargar(entregaId: Int) = datos[entregaId]
    override fun guardar(entregaId: Int, borrador: Borrador) { datos[entregaId] = borrador }
    override fun borrar(entregaId: Int) { datos.remove(entregaId) }
}

private fun leerPagina(r: JSONObject): Triple<Int, Int, Int> {
    val p = r.getJSONObject("paginacion")
    return Triple(p.getInt("pagina"), p.getInt("paginas"), p.getInt("total"))
}

private fun dinero(v: Double) = (v * 100).roundToLong() / 100.0

object Contrato {
    fun parada(o: JSONObject) = Parada(
        o.getInt("id"), o.getInt("pedido_id"), o.getString("folio"), o.getString("estado_pedido"), o.getInt("orden_parada"),
        o.getString("direccion"), o.getString("zona"), o.getDouble("total"), o.optDouble("distancia_km", 0.0), o.optDouble("minutos_estimados", 0.0)
    )

    fun detalle(o: JSONObject): Detalle {
        val d = o.getJSONObject("domicilio")
        val c = o.getJSONObject("cliente")
        val ls = o.getJSONArray("lineas")
        return Detalle(
            o.getInt("id"), o.getInt("pedido_id"), o.getString("folio"), o.getString("estado_pedido"), c.getString("nombre"),
            c.optString("telefono"), "${d.getString("calle")} ${d.getString("numero_ext")}, ${d.getString("colonia")}", o.getDouble("total"),
            (0 until ls.length()).map { ls.getJSONObject(it).let { l -> Linea(l.getInt("pedido_detalle_id"), l.getString("nombre"), l.getInt("cantidad")) } },
            d.optDouble("latitud").takeUnless { it.isNaN() }, d.optDouble("longitud").takeUnless { it.isNaN() }
        )
    }

    /** Fecha ISO 8601 con zona y segundos (`2026-10-12T18:30:00-06:00`), como pide el contrato. */
    fun fecha(ms: Long): String =
        DateTimeFormatter.ISO_OFFSET_DATE_TIME.format(Instant.ofEpochMilli(ms).atZone(ZoneId.systemDefault()).withNano(0))
}

/**
 * Entregas del repartidor: consulta, validación previa al envío y cierre idempotente.
 * Con `cola` la app también trabaja sin red: muestra la última copia de la lista y del detalle, y un cierre que no puede salir
 * queda guardado (con su foto y su recorrido GPS) para enviarse con [Sincronizador] al volver la conexión.
 */
class Entregas(
    private val api: Api,
    private val borradores: Borradores,
    private val cola: ColaSinRed? = null,
    private val ahora: () -> Long = { System.currentTimeMillis() }
) {
    fun mias(pagina: Int): Pagina<Parada> {
        val (r, guardada) = conCopia("mias-$pagina") { api.call("entregas", "entregas/mias?pagina=$pagina&por_pagina=20") }
        val datos = r.getJSONArray("datos")
        val (p, paginas, total) = leerPagina(r)
        return Pagina((0 until datos.length()).map { Contrato.parada(datos.getJSONObject(it)) }, p, paginas, total, guardada)
    }

    fun detalle(id: Int) = Contrato.detalle(conCopia("detalle-$id") { api.call("entregas", "entregas/$id") }.first)

    /** Con red guarda la respuesta; sin red (IOException) devuelve la última copia, si la hay. El modo de ejemplos no guarda nada. */
    private fun conCopia(clave: String, leer: () -> JSONObject): Pair<JSONObject, Long?> = try {
        leer().also { if (!api.demo) cola?.guardarCopia(clave, it) } to null
    } catch (e: IOException) {
        val (json, cuando) = cola?.copia(clave) ?: throw e
        json to cuando
    }

    /** Deja en el teléfono el detalle de las paradas en ruta, para poder abrirlas y cerrarlas si después se pierde la señal. */
    fun guardarParaSinRed(paradas: List<Parada>): Int {
        if (cola == null || api.demo) return 0
        var n = 0
        for (p in paradas.filter { it.estado == "en_ruta" }) {
            try { detalle(p.id); n++ } catch (_: IOException) { break } catch (_: ApiError) {}
        }
        return n
    }

    fun hayCierrePendiente(entregaId: Int) = borradores.cargar(entregaId) != null

    /** Cierre guardado sin red que todavía no se envía (o que el servicio dejó pendiente). */
    fun cierreEnCola(entregaId: Int): Operacion? =
        cola?.todas()?.firstOrNull { it.tipo == Operacion.CIERRE && it.entregaId == entregaId && it.porEnviar }

    /** La foto de este cierre ya se subió en un intento anterior: no hace falta volver a tomarla ni a enviarla. */
    fun tieneEvidencia(entregaId: Int) = borradores.cargar(entregaId)?.evidenciaId != null

    /** Las mismas reglas que aplica el servidor (RN28/RN29): se avisa en pantalla antes de gastar una petición. */
    fun validar(detalle: Detalle, d: DatosCierre) {
        val f = d.fix
        require(ahora() - f.tiempoMs <= 120_000) { "Actualiza la posición GPS (tiene más de 2 minutos)." }
        require(f.latitud in -90.0..90.0 && f.longitud in -180.0..180.0) { "La posición GPS no es válida." }
        require(d.cambio >= 0) { "El cambio entregado no puede ser negativo." }
        when (d.resultado) {
            "entregado" -> require(abs(d.montoCobrado - detalle.total) <= 0.01) { "El monto cobrado debe ser igual al total ($${"%.2f".format(detalle.total)})." }
            "parcial" -> {
                require(d.lineas.any { it.devueltas > 0 }) { "Indica qué líneas no se entregaron y cuántas unidades regresan." }
                require(d.montoCobrado in 0.0..detalle.total + 0.01) { "El monto cobrado no puede superar el total." }
                d.lineas.forEach {
                    require(it.devueltas in 0..it.linea.cantidad) { "${it.linea.nombre}: las unidades devueltas deben estar entre 0 y ${it.linea.cantidad}." }
                    require(it.devueltas == 0 || it.motivo.isNotBlank()) { "${it.linea.nombre}: explica por qué regresan unidades." }
                }
            }
            "fallida" -> {
                require(d.incidencia.isNotBlank()) { "Describe por qué no se pudo entregar." }
                require(d.montoCobrado == 0.0) { "Una entrega fallida no cobra nada." }
            }
            else -> throw IllegalArgumentException("Resultado desconocido: ${d.resultado}")
        }
    }

    /**
     * Cierra la entrega. El UUID de la operación se genera una vez y se conserva hasta el éxito: si falla la red o el
     * servidor, un nuevo intento usa el mismo UUID (y la misma evidencia ya subida), así que nunca se aplica dos veces.
     * 201 = aplicada; 200 con `duplicado` = ya estaba aplicada: ambas son éxito.
     */
    fun cerrar(detalle: Detalle, d: DatosCierre, foto: ByteArray?, recorrido: List<Fix> = emptyList(), conRed: Boolean = true): Resultado {
        validar(detalle, d)
        require(cierreEnCola(detalle.id) == null) { "El cierre de esta entrega ya está guardado en el teléfono y se enviará al volver la red." }
        val borrador = borradores.cargar(detalle.id) ?: Borrador(UUID.randomUUID().toString()).also { borradores.guardar(detalle.id, it) }
        if (cola != null && !conRed) return guardarSinRed(detalle, d, foto, recorrido, borrador)
        if (borrador.evidenciaId == null) {
            require(foto != null && foto.isNotEmpty()) { "Falta la foto de evidencia." }
            val doc = try { api.call("documentos", "documentos", "POST", Evidencia.cuerpo(detalle.id, foto)) } catch (e: IOException) {
                if (cola == null) throw e
                return guardarSinRed(detalle, d, foto, recorrido, borrador)
            }
            borrador.evidenciaId = doc.getString("id")
            borradores.guardar(detalle.id, borrador)
        }
        val sinEnviar = enviarRecorrido(detalle.id, recorrido)
        try {
            val r = api.call("entregas", "entregas/${detalle.id}/resultado", "POST", cuerpoCierre(d, borrador.evidenciaId!!).put("id_cliente_local", borrador.idClienteLocal))
            borradores.borrar(detalle.id)
            if (sinEnviar.isNotEmpty()) cola?.let { encolarRecorrido(detalle.id, sinEnviar) }
            return Resultado(r.getString("estado_pedido"), r.optBoolean("duplicado"))
        } catch (e: ApiError) {
            if (e.status == 409) borradores.borrar(detalle.id)   // otra operación ya cerró la entrega: no hay nada que reintentar
            throw e
        } catch (e: IOException) {
            if (cola == null) throw e
            // Mismo identificador: si el servidor sí alcanzó a aplicarlo, la sincronización lo verá como duplicado, no como otro cierre.
            return guardarSinRed(detalle, d, null, sinEnviar, borrador)
        }
    }

    /** Cuerpo de `POST /entregas/{id}/resultado` sin `id_cliente_local` (en el lote lo pone el servicio a partir del `operacion_uuid`). */
    private fun cuerpoCierre(d: DatosCierre, evidenciaId: String?): JSONObject {
        val cuerpo = JSONObject()
            .put("resultado", d.resultado).put("monto_cobrado", dinero(d.montoCobrado)).put("cambio_entregado", dinero(d.cambio))
            .put("ubicacion", JSONObject().put("latitud", d.fix.latitud).put("longitud", d.fix.longitud).apply { d.fix.precisionM?.let { put("precision_m", it) } })
            .put("capturado_en", Contrato.fecha(d.fix.tiempoMs))
        if (evidenciaId != null) cuerpo.put("evidencia_ids", JSONArray().put(evidenciaId))
        if (d.incidencia.isNotBlank()) cuerpo.put("incidencia", d.incidencia.trim())
        if (d.resultado == "parcial") {
            cuerpo.put("lineas", JSONArray(d.lineas.map {
                JSONObject().put("pedido_detalle_id", it.linea.pedidoDetalleId).put("cantidad_entregada", it.linea.cantidad - it.devueltas)
                    .put("cantidad_devuelta", it.devueltas).apply { if (it.devueltas > 0) put("motivo", it.motivo.trim()) }
            }))
        }
        return cuerpo
    }

    /**
     * Guarda el cierre para enviarlo después. El `operacion_uuid` es el mismo `id_cliente_local` del borrador, así que un intento en línea
     * que sí llegó al servidor y este envío posterior cuentan como una sola operación. La foto se guarda antes que la operación:
     * nunca queda un cierre en la cola sin su evidencia. Desde aquí la cola es la dueña del identificador y el borrador se borra.
     */
    private fun guardarSinRed(detalle: Detalle, d: DatosCierre, foto: ByteArray?, recorrido: List<Fix>, borrador: Borrador): Resultado {
        val c = cola!!
        val usuario = usuarioId()
        if (borrador.evidenciaId == null) {
            require(foto != null && foto.isNotEmpty()) { "Falta la foto de evidencia." }
            c.guardarFoto(borrador.idClienteLocal, foto)
        }
        encolarRecorrido(detalle.id, recorrido)
        val datos = cuerpoCierre(d, null).put("entrega_id", detalle.id)
        c.guardar(Operacion(borrador.idClienteLocal, Operacion.CIERRE, Contrato.fecha(ahora()), datos.toString(), usuario, detalle.id,
            "Cierre ${d.resultado} · ${detalle.folio}", borrador.evidenciaId))
        borradores.borrar(detalle.id)
        return Resultado(ESTADO_ESPERADO.getValue(d.resultado), false, enCola = true)
    }

    private fun encolarRecorrido(entregaId: Int, puntos: List<Fix>) {
        val c = cola ?: return
        puntos.chunked(500).forEach { lote ->
            c.guardar(Operacion(UUID.randomUUID().toString(), Operacion.UBICACIONES, Contrato.fecha(lote.maxOf { it.tiempoMs }),
                JSONObject().put("entrega_id", entregaId).put("puntos", puntosJson(lote)).toString(), usuarioId(), entregaId,
                "${lote.size} punto(s) GPS"))
        }
    }

    private fun usuarioId() = api.session?.optJSONObject("usuario")?.optInt("id")?.takeIf { it > 0 } ?: throw IllegalStateException("La sesión terminó; vuelve a entrar")

    private fun puntosJson(lote: List<Fix>) = JSONArray(lote.map {
        JSONObject().put("latitud", it.latitud).put("longitud", it.longitud).put("capturado_en", Contrato.fecha(it.tiempoMs))
            .apply { it.precisionM?.let { p -> put("precision_m", p) } }
    })

    /**
     * Puntos GPS de la ruta (lotes de hasta 500). Es un dato accesorio: si el servicio lo rechaza no impide cerrar la entrega.
     * Devuelve los puntos que no salieron por falta de red, para guardarlos en la cola.
     */
    private fun enviarRecorrido(entregaId: Int, puntos: List<Fix>): List<Fix> {
        val lotes = puntos.chunked(500)
        lotes.forEachIndexed { i, lote ->
            try {
                api.call("seguimiento", "seguimiento/$entregaId/ubicaciones", "POST", JSONObject().put("puntos", puntosJson(lote)))
            } catch (_: ApiError) {
            } catch (_: IOException) {
                return lotes.drop(i).flatten()
            }
        }
        return emptyList()
    }

    companion object {
        private val ESTADO_ESPERADO = mapOf("entregado" to "entregado", "parcial" to "entrega_parcial", "fallida" to "entrega_fallida")
    }
}

data class Perfil(
    val id: Int, val nombre: String, val apellidos: String, val correo: String, val telefono: String,
    val rol: String, val microhub: String?, val ultimoAcceso: String
) {
    val iniciales get() = (nombre.take(1) + apellidos.take(1)).uppercase()
}

/** Perfil de la persona que inició sesión: lectura y edición de nombre, apellidos y teléfono (PATCH usuarios/yo). */
class Usuarios(private val api: Api) {
    fun yo(): Perfil = leer(api.call("usuarios", "usuarios/yo"))

    fun sede(microhubId: Int): Sede = Sede.leer(api.call("microhubs", "microhubs/$microhubId"))

    /** Solo se envía lo que cambió; las mismas reglas del servicio (nombre y apellidos obligatorios, teléfono de 10 dígitos). */
    fun actualizar(actual: Perfil, nombre: String, apellidos: String, telefono: String): Perfil {
        val n = nombre.trim(); val a = apellidos.trim(); val t = telefono.trim()
        require(n.isNotEmpty() && n.length <= 80) { "El nombre es obligatorio (máximo 80 caracteres)." }
        require(a.isNotEmpty() && a.length <= 120) { "Los apellidos son obligatorios (máximo 120 caracteres)." }
        require(Regex("[0-9]{10}").matches(t)) { "El teléfono debe tener 10 dígitos." }
        val cambios = JSONObject()
        if (n != actual.nombre) cambios.put("nombre", n)
        if (a != actual.apellidos) cambios.put("apellidos", a)
        if (t != actual.telefono) cambios.put("telefono", t)
        require(cambios.length() > 0) { "No hay cambios que guardar." }
        val r = api.call("usuarios", "usuarios/yo", "PATCH", cambios)
        api.actualizarUsuarioLocal(r)
        return leer(r)
    }

    companion object {
        fun leer(o: JSONObject) = Perfil(
            o.getInt("id"), o.getString("nombre"), o.getString("apellidos"), o.getString("correo"), o.optString("telefono"),
            o.getString("rol"), o.optJSONObject("microhub")?.optString("nombre"), o.optString("ultimo_acceso")
        )
    }
}
