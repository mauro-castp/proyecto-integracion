package mx.microhubs.movil

import org.json.JSONArray
import org.json.JSONObject
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.UUID
import kotlin.math.abs
import kotlin.math.roundToLong

// Modelos de lo que la app lee del contrato v1 (entregas y perfil). Sin dependencias de Android: se prueban en la JVM.
data class Pagina<T>(val items: List<T>, val pagina: Int, val paginas: Int, val total: Int)
data class Parada(
    val id: Int, val pedidoId: Int, val folio: String, val estado: String, val orden: Int, val direccion: String, val zona: String,
    val total: Double, val distanciaKm: Double = 0.0, val minutos: Double = 0.0
)
data class Linea(val pedidoDetalleId: Int, val nombre: String, val cantidad: Int)
data class Detalle(
    val id: Int, val pedidoId: Int, val folio: String, val estado: String, val cliente: String, val telefono: String,
    val direccion: String, val total: Double, val lineas: List<Linea>
)

/** Posición GPS capturada en el teléfono. `tiempoMs` es la hora del fix (época), no la del envío. */
data class Fix(val latitud: Double, val longitud: Double, val precisionM: Double?, val tiempoMs: Long)
class LineaCierre(val linea: Linea, val devueltas: Int, val motivo: String)
class DatosCierre(
    val resultado: String, val montoCobrado: Double, val cambio: Double, val incidencia: String,
    val lineas: List<LineaCierre>, val fix: Fix
)
data class Resultado(val estadoPedido: String, val duplicado: Boolean)

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
            (0 until ls.length()).map { ls.getJSONObject(it).let { l -> Linea(l.getInt("pedido_detalle_id"), l.getString("nombre"), l.getInt("cantidad")) } }
        )
    }

    /** Fecha ISO 8601 con zona y segundos (`2026-10-12T18:30:00-06:00`), como pide el contrato. */
    fun fecha(ms: Long): String =
        DateTimeFormatter.ISO_OFFSET_DATE_TIME.format(Instant.ofEpochMilli(ms).atZone(ZoneId.systemDefault()).withNano(0))
}

/** Entregas del repartidor: consulta, validación previa al envío y cierre idempotente. */
class Entregas(
    private val api: Api,
    private val borradores: Borradores,
    private val ahora: () -> Long = { System.currentTimeMillis() }
) {
    fun mias(pagina: Int): Pagina<Parada> {
        val r = api.call("entregas", "entregas/mias?pagina=$pagina&por_pagina=20")
        val datos = r.getJSONArray("datos")
        val (p, paginas, total) = leerPagina(r)
        return Pagina((0 until datos.length()).map { Contrato.parada(datos.getJSONObject(it)) }, p, paginas, total)
    }

    fun detalle(id: Int) = Contrato.detalle(api.call("entregas", "entregas/$id"))

    fun hayCierrePendiente(entregaId: Int) = borradores.cargar(entregaId) != null

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
    fun cerrar(detalle: Detalle, d: DatosCierre, foto: ByteArray?, recorrido: List<Fix> = emptyList()): Resultado {
        validar(detalle, d)
        val borrador = borradores.cargar(detalle.id) ?: Borrador(UUID.randomUUID().toString()).also { borradores.guardar(detalle.id, it) }
        if (borrador.evidenciaId == null) {
            require(foto != null && foto.isNotEmpty()) { "Falta la foto de evidencia." }
            val doc = api.call("documentos", "documentos", "POST", JSONObject()
                .put("nombre", "evidencia-entrega-${detalle.id}.jpg").put("tipo_mime", "image/jpeg")
                .put("contenido_base64", android64(foto))
                .put("referencia", JSONObject().put("tipo", "entrega").put("id", detalle.id.toString())))
            borrador.evidenciaId = doc.getString("id")
            borradores.guardar(detalle.id, borrador)
        }
        enviarRecorrido(detalle.id, recorrido)
        val cuerpo = JSONObject()
            .put("resultado", d.resultado).put("monto_cobrado", dinero(d.montoCobrado)).put("cambio_entregado", dinero(d.cambio))
            .put("ubicacion", JSONObject().put("latitud", d.fix.latitud).put("longitud", d.fix.longitud).apply { d.fix.precisionM?.let { put("precision_m", it) } })
            .put("evidencia_ids", JSONArray().put(borrador.evidenciaId))
            .put("capturado_en", Contrato.fecha(d.fix.tiempoMs))
            .put("id_cliente_local", borrador.idClienteLocal)
        if (d.incidencia.isNotBlank()) cuerpo.put("incidencia", d.incidencia.trim())
        if (d.resultado == "parcial") {
            cuerpo.put("lineas", JSONArray(d.lineas.map {
                JSONObject().put("pedido_detalle_id", it.linea.pedidoDetalleId).put("cantidad_entregada", it.linea.cantidad - it.devueltas)
                    .put("cantidad_devuelta", it.devueltas).apply { if (it.devueltas > 0) put("motivo", it.motivo.trim()) }
            }))
        }
        try {
            val r = api.call("entregas", "entregas/${detalle.id}/resultado", "POST", cuerpo)
            borradores.borrar(detalle.id)
            return Resultado(r.getString("estado_pedido"), r.optBoolean("duplicado"))
        } catch (e: ApiError) {
            if (e.status == 409) borradores.borrar(detalle.id)   // otra operación ya cerró la entrega: no hay nada que reintentar
            throw e
        }
    }

    /** Puntos GPS de la ruta (lotes de hasta 500). Es un dato accesorio: si falla no impide cerrar la entrega. */
    private fun enviarRecorrido(entregaId: Int, puntos: List<Fix>) {
        puntos.chunked(500).forEach { lote ->
            try {
                api.call("seguimiento", "seguimiento/$entregaId/ubicaciones", "POST", JSONObject().put("puntos", JSONArray(lote.map {
                    JSONObject().put("latitud", it.latitud).put("longitud", it.longitud).put("capturado_en", Contrato.fecha(it.tiempoMs))
                        .apply { it.precisionM?.let { p -> put("precision_m", p) } }
                })))
            } catch (_: ApiError) {
            } catch (_: java.io.IOException) {
            }
        }
    }

    // Base64 sin saltos de línea. java.util.Base64 existe desde API 26 (minSdk) y también en las pruebas de la JVM.
    private fun android64(bytes: ByteArray): String = java.util.Base64.getEncoder().encodeToString(bytes)
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
