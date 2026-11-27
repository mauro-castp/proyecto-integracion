package mx.microhubs.movil

import org.json.JSONObject
import java.io.IOException
import java.util.UUID

/** Un aviso de la bandeja (servicio de notificaciones, 5124). `referencia` es p. ej. «entrega 61». */
data class Aviso(
    val id: Int, val tipo: String, val titulo: String, val mensaje: String, val leida: Boolean, val creadaEn: String,
    val referenciaTipo: String? = null, val referenciaId: String? = null
)

/**
 * Bandeja de avisos de la persona con sesión: la misma que ve en el portal web.
 * Marcar como leído sin red no se pierde: queda en la cola como `notificacion_leida` y se envía con la sincronización.
 */
class Avisos(private val api: Api, private val cola: ColaSinRed? = null, private val ahora: () -> Long = { System.currentTimeMillis() }) {

    fun bandeja(pagina: Int, soloNoLeidas: Boolean = false): Pagina<Aviso> {
        val r = api.call("notificaciones", "notificaciones?pagina=$pagina&por_pagina=20" + if (soloNoLeidas) "&solo_no_leidas=true" else "")
        val datos = r.getJSONArray("datos")
        val p = r.getJSONObject("paginacion")
        val enCola = leidasEnCola()
        val items = (0 until datos.length()).map { leer(datos.getJSONObject(it)) }.map { if (it.id in enCola) it.copy(leida = true) else it }
        return Pagina(items, p.getInt("pagina"), p.getInt("paginas"), p.getInt("total"))
    }

    /** Cuántos avisos faltan por leer (descontando los que ya se leyeron sin red y aún no se envían). */
    fun noLeidas(): Int = maxOf(0, api.call("notificaciones", "notificaciones/conteo").getInt("no_leidas") - leidasEnCola().size)

    /** Confirma la lectura. Sin red, la guarda para después y devuelve el aviso como leído. */
    fun marcarLeido(a: Aviso): Aviso {
        if (a.leida) return a
        return try {
            leer(api.call("notificaciones", "notificaciones/${a.id}/leer", "POST", JSONObject()))
        } catch (e: IOException) {
            val c = cola ?: throw e
            val usuario = api.session?.optJSONObject("usuario")?.optInt("id")?.takeIf { it > 0 } ?: throw e
            if (a.id !in leidasEnCola()) {
                c.guardar(Operacion(UUID.randomUUID().toString(), Operacion.LECTURA, Contrato.fecha(ahora()),
                    JSONObject().put("id", a.id).toString(), usuario, null, "Aviso leído: ${a.titulo}"))
            }
            a.copy(leida = true)
        }
    }

    /** Marca todos como leídos (solo con red). Devuelve cuántos cambió el servidor. */
    fun marcarTodos(): Int = api.call("notificaciones", "notificaciones/leer-todas", "POST", JSONObject()).optInt("marcadas")

    private fun leidasEnCola(): Set<Int> =
        cola?.todas()?.filter { it.tipo == Operacion.LECTURA && it.porEnviar }?.map { JSONObject(it.datos).getInt("id") }?.toSet() ?: emptySet()

    companion object {
        fun leer(o: JSONObject): Aviso {
            val ref = o.optJSONObject("referencia")
            return Aviso(o.getInt("id"), o.getString("tipo"), o.getString("titulo"), o.getString("mensaje"), o.getBoolean("leida"),
                o.getString("creada_en"), ref?.optString("tipo"), ref?.let { if (it.isNull("id")) null else it.get("id").toString() })
        }
    }
}
