package mx.microhubs.movil

import org.json.JSONObject
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL

/** Respuestas de los ejemplos oficiales del contrato (app/src/test/resources/contratos). */
object Ejemplos {
    fun texto(nombre: String): String =
        Ejemplos::class.java.classLoader!!.getResourceAsStream("contratos/$nombre.json")!!.bufferedReader(Charsets.UTF_8).use { it.readText() }
    fun json(nombre: String) = JSONObject(texto(nombre))
}

class Memoria : Sessions {
    var saved: JSONObject? = null
    var guardados = 0
    override fun save(session: JSONObject) { saved = session; guardados++ }
    override fun load() = saved
    override fun clear() { saved = null }
}

class Peticion(val metodo: String, val ruta: String, val cuerpo: String, private val cabeceras: Map<String, String?>) {
    val json: JSONObject get() = JSONObject(cuerpo)
    fun cabecera(nombre: String) = cabeceras[nombre]
    override fun toString() = "$metodo $ruta"
}

class Salida(val codigo: Int, val tipo: String = "application/json; charset=utf-8", val cuerpo: String = "{}",
             val cabeceras: Map<String, String> = emptyMap(), val fallo: IOException? = null) {
    companion object {
        fun ok(json: JSONObject, codigo: Int = 200) = Salida(codigo, cuerpo = json.toString())
        fun error(codigo: Int, ejemplo: String, cabeceras: Map<String, String> = emptyMap()) = Salida(codigo, cuerpo = Ejemplos.texto(ejemplo), cabeceras = cabeceras)
    }
}

/** Servidor simulado: registra cada petición y contesta con lo que diga `manejador`. */
class Servidor(var manejador: (Peticion) -> Salida = { Salida(200) }) {
    val peticiones = mutableListOf<Peticion>()
    fun abrir(url: URL): HttpURLConnection = Conexion(url, this)
    fun rutas() = peticiones.map { it.toString() }
    fun ultima() = peticiones.last()

    private class Conexion(url: URL, val servidor: Servidor) : HttpURLConnection(url) {
        val enviado = ByteArrayOutputStream()
        // La respuesta se calcula al pedir el código: para entonces ya se fijaron método, cabeceras y cuerpo.
        private val salida: Salida by lazy {
            val cabeceras = listOf("Accept", "Content-Type", "Authorization").associateWith { getRequestProperty(it) }
            val p = Peticion(requestMethod, url.path + (url.query?.let { "?$it" } ?: ""), enviado.toString("UTF-8"), cabeceras)
            servidor.peticiones.add(p)
            servidor.manejador(p).also { it.fallo?.let { e -> throw e } }
        }
        override fun connect() {}
        override fun disconnect() {}
        override fun usingProxy() = false
        override fun getResponseCode() = salida.codigo
        override fun getContentType(): String? = salida.tipo
        override fun getHeaderField(name: String?): String? = salida.cabeceras[name]
        override fun getInputStream() = ByteArrayInputStream(salida.cuerpo.toByteArray())
        override fun getErrorStream() = ByteArrayInputStream(salida.cuerpo.toByteArray())
        override fun getOutputStream() = enviado
    }
}

/** Api lista para probar contra un servidor simulado, con sesión de repartidor ya iniciada. */
fun clienteDe(servidor: Servidor, memoria: Memoria = Memoria(), httpHost: String = "10.0.2.2", conSesion: Boolean = true): Api {
    val api = Api(memoria, servidor::abrir, httpHost)
    if (conSesion) api.session = Ejemplos.json("Sesion.ok")
    return api
}
