package mx.microhubs.movil

import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.nio.file.Files
import java.nio.file.StandardCopyOption
import java.util.UUID

/**
 * Una acción hecha sin red, en la forma que pide `POST /api/v1/sincronizacion/lotes` (servicio 5125).
 *
 * Lo que identifica a la operación se fija UNA vez al crearla y no cambia nunca: `uuid`, `tipo`, `creadaEn` (con zona) y `datos`.
 * El servicio guarda una huella de ese contenido y rechaza (UUID_REUTILIZADO) un uuid ya visto con otro contenido.
 * La única pieza que se completa después es `evidenciaId` (el id que devuelve `POST /documentos` al subir la foto); se fija una sola vez
 * y ANTES del primer envío, porque una operación que aún necesita foto no sale en ningún lote.
 */
data class Operacion(
    val uuid: String,
    val tipo: String,
    val creadaEn: String,
    val datos: String,
    val usuarioId: Int,
    val entregaId: Int? = null,
    val descripcion: String = "",
    val evidenciaId: String? = null,
    val estado: String = EN_COLA,
    val mensaje: String? = null,
    val intentos: Int = 0
) {
    /** El cierre de entrega no puede salir sin el id de su foto de evidencia. */
    val necesitaFoto get() = tipo == CIERRE && evidenciaId == null
    /** En cola (nunca enviada) o pendiente (el servicio no pudo atenderla): se manda tal cual en el siguiente lote. */
    val porEnviar get() = estado == EN_COLA || estado == PENDIENTE

    /** El sobre de la operación dentro del lote. Siempre el mismo para el mismo uuid. */
    fun sobre(): JSONObject {
        val d = JSONObject(datos)
        if (tipo == CIERRE) d.put("evidencia_ids", JSONArray().put(evidenciaId))
        return JSONObject().put("operacion_uuid", uuid).put("tipo", tipo).put("creada_en", creadaEn).put("datos", d)
    }

    fun json(): JSONObject = JSONObject().put("uuid", uuid).put("tipo", tipo).put("creada_en", creadaEn).put("datos", datos)
        .put("usuario_id", usuarioId).put("entrega_id", entregaId ?: JSONObject.NULL).put("descripcion", descripcion)
        .put("evidencia_id", evidenciaId ?: JSONObject.NULL).put("estado", estado).put("mensaje", mensaje ?: JSONObject.NULL).put("intentos", intentos)

    companion object {
        const val CIERRE = "entrega_resultado"
        const val UBICACIONES = "ubicaciones"
        const val LECTURA = "notificacion_leida"
        const val EN_COLA = "en_cola"
        const val PENDIENTE = "pendiente"
        const val CONFLICTO = "conflicto"
        const val RECHAZADA = "rechazada"

        private fun texto(o: JSONObject, k: String) = if (o.isNull(k)) null else o.getString(k)
        fun leer(o: JSONObject) = Operacion(
            o.getString("uuid"), o.getString("tipo"), o.getString("creada_en"), o.getString("datos"), o.getInt("usuario_id"),
            if (o.isNull("entrega_id")) null else o.getInt("entrega_id"), o.optString("descripcion"), texto(o, "evidencia_id"),
            o.getString("estado"), texto(o, "mensaje"), o.optInt("intentos")
        )
    }
}

/** Dónde vive lo hecho sin red: operaciones, fotos de evidencia aún no subidas y la última copia de lo consultado. */
interface ColaSinRed {
    /** Identificador estable de esta instalación: el servicio deduplica por (dispositivo, operacion_uuid). */
    val dispositivo: String
    fun todas(): List<Operacion>
    fun guardar(op: Operacion)
    fun borrar(uuid: String)
    fun guardarFoto(uuid: String, foto: ByteArray)
    fun foto(uuid: String): ByteArray?
    fun borrarFoto(uuid: String)
    fun guardarCopia(clave: String, json: JSONObject)
    /** La copia guardada y cuándo se guardó (milisegundos). */
    fun copia(clave: String): Pair<JSONObject, Long>?
    fun borrarCopias()
}

/**
 * Cola en archivos dentro del almacenamiento privado de la app (en Android, `filesDir/sin_red`): sobrevive a que el sistema cierre la app
 * o se reinicie el teléfono. Cada escritura va a un archivo temporal y se renombra, así que un corte a la mitad no deja la cola corrupta.
 * Solo usa java.io/java.nio, así que también se prueba en la JVM.
 */
class ColaEnArchivos(private val dir: File, private val ahora: () -> Long = { System.currentTimeMillis() }) : ColaSinRed {
    private val ops = File(dir, "operaciones.json")
    private val fotos = File(dir, "fotos")
    private val copias = File(dir, "copias")

    init { dir.mkdirs(); fotos.mkdirs(); copias.mkdirs() }

    override val dispositivo: String by lazy {
        synchronized(this) {
            val f = File(dir, "dispositivo")
            f.takeIf { it.exists() }?.readText()?.trim()?.takeIf { it.matches(Regex("[A-Za-z0-9._:-]{3,60}")) }
                ?: ("android-" + UUID.randomUUID().toString().replace("-", "").take(12)).also { escribir(f, it.toByteArray()) }
        }
    }

    @Synchronized override fun todas(): List<Operacion> {
        if (!ops.exists()) return emptyList()
        val a = JSONArray(ops.readText(Charsets.UTF_8))
        return (0 until a.length()).map { Operacion.leer(a.getJSONObject(it)) }
    }

    @Synchronized override fun guardar(op: Operacion) {
        val lista = todas().toMutableList()
        val i = lista.indexOfFirst { it.uuid == op.uuid }
        if (i >= 0) lista[i] = op else lista.add(op)
        escribirOps(lista)
    }

    @Synchronized override fun borrar(uuid: String) {
        escribirOps(todas().filter { it.uuid != uuid })
        borrarFoto(uuid)
    }

    @Synchronized override fun guardarFoto(uuid: String, foto: ByteArray) = escribir(archivoFoto(uuid), foto)
    @Synchronized override fun foto(uuid: String): ByteArray? = archivoFoto(uuid).takeIf { it.exists() }?.readBytes()
    @Synchronized override fun borrarFoto(uuid: String) { archivoFoto(uuid).delete() }

    @Synchronized override fun guardarCopia(clave: String, json: JSONObject) =
        escribir(archivoCopia(clave), JSONObject().put("guardada_en", ahora()).put("datos", json).toString().toByteArray(Charsets.UTF_8))

    @Synchronized override fun copia(clave: String): Pair<JSONObject, Long>? {
        val f = archivoCopia(clave).takeIf { it.exists() } ?: return null
        return try { JSONObject(f.readText(Charsets.UTF_8)).let { it.getJSONObject("datos") to it.getLong("guardada_en") } } catch (_: Exception) { null }
    }

    @Synchronized override fun borrarCopias() { copias.listFiles()?.forEach { it.delete() } }

    private fun archivoFoto(uuid: String): File {
        require(uuid.matches(Regex("[0-9a-fA-F-]{36}"))) { "Identificador de operación no válido" }
        return File(fotos, "$uuid.jpg")
    }

    private fun archivoCopia(clave: String): File {
        require(clave.matches(Regex("[a-z0-9-]{1,60}"))) { "Clave de copia no válida" }
        return File(copias, "$clave.json")
    }

    private fun escribirOps(lista: List<Operacion>) = escribir(ops, JSONArray(lista.map { it.json() }).toString().toByteArray(Charsets.UTF_8))

    private fun escribir(destino: File, bytes: ByteArray) {
        val tmp = File(destino.parentFile, destino.name + ".tmp")
        tmp.writeBytes(bytes)
        Files.move(tmp.toPath(), destino.toPath(), StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE)
    }
}

/** Resultado de una sincronización. `esperando` = operaciones que no salieron (p. ej. la foto no se pudo subir todavía). */
data class Informe(val aplicadas: Int = 0, val conflictos: Int = 0, val rechazadas: Int = 0, val pendientes: Int = 0, val esperando: Int = 0) {
    val enviadas get() = aplicadas + conflictos + rechazadas + pendientes
}

/**
 * Envía lo hecho sin red cuando vuelve la conexión.
 *  1. Sube primero cada foto de evidencia pendiente (`POST /documentos`, 5107) y guarda el id que devuelve.
 *  2. Manda las operaciones listas en lotes (`POST /sincronizacion/lotes`, 5125) de hasta `maxLote`.
 *  3. Interpreta cada resultado: aplicada → sale de la cola; conflicto → gana el servidor, se muestra y no se reintenta;
 *     rechazada → se muestra y no se reintenta; pendiente → se reenvía igual en la siguiente sincronización.
 * Solo manda las operaciones de quien tiene la sesión: el servicio las aplica con su JWT.
 */
class Sincronizador(private val api: Api, private val cola: ColaSinRed, private val maxLote: Int = 200) {
    private val candado = Any()

    private fun usuario(): Int? = api.session?.optJSONObject("usuario")?.optInt("id")?.takeIf { it > 0 }

    /** Lo que sigue en el teléfono para la persona con sesión: por enviar, en conflicto y rechazado. */
    fun mias(): List<Operacion> { val u = usuario() ?: return emptyList(); return cola.todas().filter { it.usuarioId == u } }
    fun porEnviar() = mias().count { it.porEnviar }

    /** Quita de la lista un conflicto o un rechazo ya visto. Lo que aún se va a enviar no se puede descartar. */
    fun descartar(uuid: String) {
        val op = cola.todas().firstOrNull { it.uuid == uuid } ?: return
        require(!op.porEnviar) { "Esa operación todavía se va a enviar." }
        cola.borrar(uuid)
    }

    fun sincronizar(): Informe = synchronized(candado) {
        val u = usuario() ?: return Informe()
        if (cola.todas().none { it.usuarioId == u && it.porEnviar }) return Informe()
        var rechazadas = 0

        // 1. Evidencias: la foto no viaja en el lote; se sube antes y su id va en evidencia_ids.
        for (op in cola.todas().filter { it.usuarioId == u && it.porEnviar && it.necesitaFoto }) {
            val foto = cola.foto(op.uuid)
            if (foto == null) {
                cola.guardar(op.copy(estado = Operacion.RECHAZADA, mensaje = "Se perdió la foto de evidencia guardada; registra de nuevo la entrega."))
                rechazadas++; continue
            }
            try {
                val doc = api.call("documentos", "documentos", "POST", Evidencia.cuerpo(op.entregaId!!, foto))
                cola.guardar(op.copy(evidenciaId = doc.getString("id")))
                cola.borrarFoto(op.uuid)
            } catch (e: ApiError) {
                if (e.status == 401) throw e
                if (e.status in RECHAZOS) {
                    cola.guardar(op.copy(estado = Operacion.RECHAZADA, mensaje = "La foto de evidencia no se aceptó: ${e.message}"))
                    cola.borrarFoto(op.uuid); rechazadas++
                }
                // 5xx o 429: la foto se queda y se intenta en la siguiente sincronización
                if (e.status == 429) break
            }
        }

        // 2. Lotes con lo que ya está completo
        var aplicadas = 0; var conflictos = 0; var pendientes = 0
        val listas = cola.todas().filter { it.usuarioId == u && it.porEnviar && !it.necesitaFoto }
        for (lote in listas.chunked(maxLote)) {
            val cuerpo = JSONObject().put("lote_uuid", UUID.randomUUID().toString()).put("dispositivo", cola.dispositivo).put("cliente", "android")
                .put("operaciones", JSONArray(lote.map { it.sobre() }))
            val r = try { api.call("sincronizacion", "sincronizacion/lotes", "POST", cuerpo) } catch (e: ApiError) {
                if (e.status == 401 || e.status == 429) throw e
                lote.forEach { cola.guardar(it.copy(mensaje = "El servicio de sincronización respondió ${e.status}: ${e.message}")) }
                continue
            }
            val res = r.getJSONArray("operaciones").let { a -> (0 until a.length()).map { a.getJSONObject(it) } }.associateBy { it.getString("operacion_uuid").lowercase() }
            for (op in lote) {
                val o = res[op.uuid.lowercase()] ?: continue
                val mensaje = if (o.isNull("mensaje")) null else o.getString("mensaje")
                when (o.getString("estado")) {
                    "aplicada" -> { cola.borrar(op.uuid); aplicadas++ }
                    "conflicto" -> { cola.guardar(op.copy(estado = Operacion.CONFLICTO, mensaje = mensaje ?: "Ya cambió en el servidor; se conserva lo del servidor.")); conflictos++ }
                    "rechazada" -> { cola.guardar(op.copy(estado = Operacion.RECHAZADA, mensaje = mensaje ?: "El servidor no la aceptó.")); rechazadas++ }
                    else -> { cola.guardar(op.copy(estado = Operacion.PENDIENTE, mensaje = mensaje, intentos = op.intentos + 1)); pendientes++ }
                }
            }
        }
        val esperando = cola.todas().count { it.usuarioId == u && it.porEnviar && it.necesitaFoto }
        return Informe(aplicadas, conflictos, rechazadas, pendientes, esperando)
    }

    companion object {
        /** Los mismos códigos que el servicio trata como «rechazada»: reintentar el mismo contenido da lo mismo. */
        val RECHAZOS = setOf(400, 403, 404, 413, 415, 422)
    }
}

/** Cuerpo de `POST /documentos` para la foto de evidencia de una entrega (lo usan el cierre en línea y la sincronización). */
object Evidencia {
    fun cuerpo(entregaId: Int, foto: ByteArray): JSONObject = JSONObject()
        .put("nombre", "evidencia-entrega-$entregaId.jpg").put("tipo_mime", "image/jpeg")
        .put("contenido_base64", java.util.Base64.getEncoder().encodeToString(foto))   // sin saltos de línea; existe desde API 26
        .put("referencia", JSONObject().put("tipo", "entrega").put("id", entregaId.toString()))
}
