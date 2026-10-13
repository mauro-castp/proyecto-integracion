package mx.microhubs.movil

import android.Manifest
import android.app.Activity
import android.app.AlertDialog
import android.content.ClipData
import android.content.Intent
import android.content.pm.PackageManager
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import android.net.Uri
import android.os.Bundle
import android.provider.MediaStore
import android.text.InputType
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.widget.CheckBox
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import com.google.zxing.integration.android.IntentIntegrator
import java.io.File
import java.util.concurrent.Executors

class MainActivity : Activity() {
    private lateinit var api: Api
    private lateinit var entregas: Entregas
    private lateinit var avisos: Notificaciones
    private lateinit var usuarios: Usuarios
    private lateinit var ui: Estilo
    private lateinit var p: Pantalla
    private var atras: (() -> Unit)? = null
    private val executor = Executors.newSingleThreadExecutor()
    private var busy = false
    private var alive = true
    private var callbackRed: ConnectivityManager.NetworkCallback? = null

    // Entrega abierta y su evidencia. Nada de esto se conserva si la Activity se recrea (solo el UUID del cierre pendiente).
    private var detalle: Detalle? = null
    private var scannedOrder: Int? = null
    private var photo: ByteArray? = null
    private var photoFile: File? = null
    private var position: Location? = null
    private val route = mutableListOf<Fix>()
    private var listener: LocationListener? = null
    private var manager: LocationManager? = null

    // Valores del formulario de cierre: se leen de las vistas antes de reconstruir la pantalla (QR, foto o GPS la rehacen).
    private var formResultado = "entregado"
    private var formMonto = ""
    private var formCambio = "0"
    private var formNota = ""
    private var scrollY = 0
    private val formDevueltas = mutableMapOf<Int, Int>()
    private val formMotivos = mutableMapOf<Int, String>()
    private var fMonto: EditText? = null
    private var fCambio: EditText? = null
    private var fNota: EditText? = null
    private val fMotivos = mutableMapOf<Int, EditText>()

    override fun onCreate(state: Bundle?) {
        super.onCreate(state)
        api = Api(SessionStore(this))
        entregas = Entregas(api, PrefsBorradores(this))
        avisos = Notificaciones(api)
        usuarios = Usuarios(api)
        ui = Estilo(this)
        loginScreen()
    }

    // ------------------------------------------------------------------------------------------ pantalla y conexión
    private fun nueva(titulo: String, subtitulo: String? = null, volver: (() -> Unit)? = null): Pantalla {
        atras = volver
        p = Pantalla(ui, this, titulo, subtitulo, volver)
        p.conexion(redActual())
        p.mostrar()
        return p
    }

    private fun redActual(): Red {
        if (api.demo) return Red.EJEMPLOS
        val cm = getSystemService(ConnectivityManager::class.java)
        return if (cm.getNetworkCapabilities(cm.activeNetwork)?.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED) == true) Red.EN_LINEA else Red.SIN_RED
    }

    /** El indicador de conexión de la barra se actualiza en vivo, no solo al abrir una pantalla. */
    override fun onStart() {
        super.onStart()
        val cm = getSystemService(ConnectivityManager::class.java)
        val cb = object : ConnectivityManager.NetworkCallback() {
            private fun refrescar() = runOnUiThread { if (alive && ::p.isInitialized) p.conexion(redActual()) }
            override fun onAvailable(network: Network) = refrescar()
            override fun onLost(network: Network) = refrescar()
            override fun onCapabilitiesChanged(network: Network, caps: NetworkCapabilities) = refrescar()
        }
        try { cm.registerDefaultNetworkCallback(cb); callbackRed = cb } catch (_: Exception) {}
        if (::p.isInitialized) p.conexion(redActual())
    }

    override fun onStop() {
        callbackRed?.let { try { getSystemService(ConnectivityManager::class.java).unregisterNetworkCallback(it) } catch (_: Exception) {} }
        callbackRed = null
        super.onStop()
    }

    @Deprecated("Se usa el retroceso clásico: cada pantalla define a dónde vuelve")
    override fun onBackPressed() { val destino = atras; if (destino != null) destino() else @Suppress("DEPRECATION") super.onBackPressed() }

    private fun describe(ex: Exception): String {
        if (ex !is ApiError) return ex.message ?: "Error de conexión"
        val campos = ex.fields.entries.joinToString("\n") { "• ${it.key}: ${it.value}" }
        return listOf(ex.message ?: "", campos, if (ex.trace.isNotEmpty()) "Traza: ${ex.trace}" else "").filter { it.isNotEmpty() }.joinToString("\n")
    }

    private fun error(message: String) { p.aviso(message, Mensaje.ERROR); Toast.makeText(this, message.lineSequence().first(), Toast.LENGTH_LONG).show() }

    private fun <T> work(task: () -> T, done: (T) -> Unit) {
        if (busy) return
        busy = true; p.ocupado(true); p.aviso(null)
        executor.execute {
            try {
                val result = task()
                runOnUiThread { if (alive) { busy = false; p.ocupado(false); done(result) } }
            } catch (ex: Exception) {
                runOnUiThread { if (alive) { busy = false; if (api.session == null) loginScreen(); p.ocupado(false); error(describe(ex)) } }
            }
        }
    }

    private fun accion(action: () -> Unit): () -> Unit = { if (!busy) action() }

    // ------------------------------------------------------------------------------------------ acceso
    private fun loginScreen() {
        nueva("Microhubs", "Entregas de proximidad")
        p.agregar(ui.espacio(8))
        val email = ui.campo("Correo").apply { inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_EMAIL_ADDRESS }
        val password = ui.campo("Clave", secreto = true)
        val host = ui.campo("Servidor (en debug http://10.0.2.2; en producción https://…)", api.host)
        val demo = CheckBox(this).apply { text = "Usar ejemplos locales (sin red)"; isChecked = api.demo; setTextColor(ui.tintaSec) }
        val ajustes = ui.tarjeta().apply { visibility = View.GONE }
        ajustes.addView(ui.etiqueta("Servidor")); ajustes.addView(host); ajustes.addView(demo)

        val acceso = ui.tarjeta()
        acceso.addView(ui.texto("Iniciar sesión", 20f, ui.tinta, true))
        acceso.addView(ui.texto("Entra con tu cuenta de repartidor.", 14f, ui.tintaSec))
        acceso.addView(ui.etiqueta("Correo")); acceso.addView(email)
        acceso.addView(ui.etiqueta("Clave")); acceso.addView(password)
        acceso.addView(ui.espacio(8))
        acceso.addView(ui.boton("Entrar", Tipo.PRIMARIO) {
            if (!android.util.Patterns.EMAIL_ADDRESS.matcher(email.text.toString()).matches() || password.text.isEmpty()) { error("Ingresa correo válido y clave"); return@boton }
            val mail = email.text.toString().trim()
            val pass = password.text.toString()
            api.demo = demo.isChecked; api.host = host.text.toString().trim()
            if (!busy) work({ api.login(mail, pass) }) { password.text.clear(); home() }
        })
        acceso.addView(ui.boton("Restaurar sesión segura", Tipo.TEXTO) {
            api.demo = demo.isChecked; api.host = host.text.toString().trim()
            if (api.demo) { error("La sesión demo no se guarda"); return@boton }
            if (!busy) work({ api.restore(); require(api.session != null) { "No hay sesión guardada" }; api.call("usuarios", "usuarios/yo") }) { home() }
        })
        p.agregar(acceso)
        p.agregar(ui.boton("Configuración del servidor", Tipo.TEXTO) { ajustes.visibility = if (ajustes.visibility == View.GONE) View.VISIBLE else View.GONE })
        p.agregar(ajustes)
    }

    private fun role() = api.session!!.getJSONObject("usuario").getString("rol")
    private fun rolLegible(r: String) = r.replaceFirstChar { it.uppercase() }

    // ------------------------------------------------------------------------------------------ menú
    private fun opcion(icono: String, titulo: String, descripcion: String, insignia: TextView? = null, clic: () -> Unit): LinearLayout {
        val texto = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL; layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
            addView(ui.texto(titulo, 17f, ui.tinta, true)); addView(ui.texto(descripcion, 13f, ui.tintaSec))
        }
        val tarjeta = ui.tarjeta(accion(clic))
        tarjeta.addView(ui.fila(ui.circulo(icono, ui.primario, 44), texto, *listOfNotNull(insignia, ui.texto("›", 26f, ui.tintaSec).apply {
            layoutParams = LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT).apply { marginStart = ui.dp(8) } }).toTypedArray()))
        return tarjeta
    }

    private fun home() {
        val u = api.session!!.getJSONObject("usuario")
        nueva("Hola, ${u.getString("nombre")}", rolLegible(u.getString("rol")))
        p.agregar(ui.titulo("¿Qué quieres hacer?"))
        if (role() in listOf("repartidor", "administrador")) p.agregar(opcion("📦", "Mis entregas", "Paradas asignadas a tu turno") { deliveries(1) })
        val badge = ui.chip("", ui.alerta).apply { visibility = View.GONE }
        p.agregar(opcion("🔔", "Notificaciones", "Avisos de entregas nuevas y cambios", badge) { notifications(1) })
        p.agregar(opcion("👤", "Mi perfil", "Tus datos y teléfono de contacto") { profile() })
        executor.execute { try { val n = avisos.noLeidas(); runOnUiThread { if (alive && n > 0) { badge.text = "$n sin leer"; badge.visibility = View.VISIBLE } } } catch (_: Exception) {} }
        p.conPie(ui.boton("Cerrar sesión", Tipo.PELIGRO) {
            if (!busy) work({ api.logout() }) { resetEvidence(); detalle = null; loginScreen() }
        })
    }

    // ------------------------------------------------------------------------------------------ perfil
    private fun profile() { work({ usuarios.yo() }) { profileForm(it) } }

    private fun profileForm(perfil: Perfil) {
        nueva("Mi perfil", perfil.correo) { home() }
        val cabecera = ui.tarjeta()
        val datos = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL; layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
            addView(ui.texto("${perfil.nombre} ${perfil.apellidos}", 18f, ui.tinta, true))
            addView(ui.texto(perfil.correo, 13f, ui.tintaSec))
            addView(ui.chip(rolLegible(perfil.rol) + (perfil.microhub?.let { " · $it" } ?: ""), ui.primario).apply {
                (layoutParams as LinearLayout.LayoutParams).topMargin = ui.dp(6) })
        }
        cabecera.addView(ui.fila(ui.circulo(perfil.iniciales, ui.primario, 56), datos))
        p.agregar(cabecera)
        val form = ui.tarjeta()
        val nombre = ui.campo("Nombre", perfil.nombre)
        val apellidos = ui.campo("Apellidos", perfil.apellidos)
        val telefono = ui.campo("Teléfono (10 dígitos)", perfil.telefono, entero = true)
        form.addView(ui.texto("Datos de contacto", 16f, ui.tinta, true))
        form.addView(ui.etiqueta("Nombre")); form.addView(nombre)
        form.addView(ui.etiqueta("Apellidos")); form.addView(apellidos)
        form.addView(ui.etiqueta("Teléfono")); form.addView(telefono)
        p.agregar(form)
        p.conPie(ui.boton("Guardar cambios", Tipo.PRIMARIO) {
            if (busy) return@boton
            val n = nombre.text.toString(); val a = apellidos.text.toString(); val t = telefono.text.toString()
            work({ usuarios.actualizar(perfil, n, a, t) }) { nuevo -> profileForm(nuevo); p.aviso("Perfil actualizado", Mensaje.EXITO) }
        })
    }

    // ------------------------------------------------------------------------------------------ notificaciones
    private fun notifications(page: Int) {
        work({ avisos.lista(page) }) { r ->
            nueva("Notificaciones", "${r.total} en total · página $page de ${maxOf(1, r.paginas)}") { home() }
            if (r.items.isEmpty()) p.agregar(ui.tarjeta().apply {
                addView(ui.texto("No tienes notificaciones", 16f, ui.tinta, true)); addView(ui.texto("Aquí aparecerán los avisos de entregas nuevas.", 14f, ui.tintaSec)) })
            r.items.forEach { a ->
                val tarjeta = ui.tarjeta(accion {
                    work({ if (!a.leida) avisos.leer(a.id); a }) {
                        AlertDialog.Builder(this).setTitle(a.titulo).setMessage("${a.mensaje}\n\n${a.creadaEn}").setPositiveButton("Cerrar") { _, _ -> notifications(page) }.show()
                    }
                })
                val punto = ui.texto(if (a.leida) "" else "●", 14f, ui.primario).apply { layoutParams = LinearLayout.LayoutParams(ui.dp(18), ViewGroup.LayoutParams.WRAP_CONTENT) }
                tarjeta.addView(ui.fila(punto, ui.flexible(ui.texto(a.titulo, 16f, ui.tinta, !a.leida))))
                tarjeta.addView(ui.texto(a.mensaje, 14f, ui.tintaSec).apply { maxLines = 3; (layoutParams as LinearLayout.LayoutParams).marginStart = ui.dp(18) })
                tarjeta.addView(ui.texto(a.creadaEn.replace('T', ' ').take(16), 12f, ui.tintaSec).apply { (layoutParams as LinearLayout.LayoutParams).apply { marginStart = ui.dp(18); topMargin = ui.dp(4) } })
                p.agregar(tarjeta)
            }
            paginacion(r.pagina, r.paginas) { notifications(it) }
        }
    }

    private fun paginacion(pagina: Int, paginas: Int, ir: (Int) -> Unit) {
        if (paginas <= 1) return
        val fila = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; layoutParams = LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT) }
        if (pagina > 1) fila.addView(ui.boton("‹ Anterior") { ir(pagina - 1) }.apply { layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f).apply { marginEnd = ui.dp(6) } })
        if (pagina < paginas) fila.addView(ui.boton("Siguiente ›") { ir(pagina + 1) }.apply { layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f).apply { marginStart = ui.dp(6) } })
        p.agregar(fila)
    }

    // ------------------------------------------------------------------------------------------ entregas
    private fun deliveries(page: Int) {
        work({ entregas.mias(page) }) { r ->
            nueva("Mis entregas", "${r.total} parada(s) · página $page de ${maxOf(1, r.paginas)}") { home() }
            if (r.items.isEmpty()) p.agregar(ui.tarjeta().apply {
                addView(ui.texto("Sin entregas pendientes", 16f, ui.tinta, true))
                addView(ui.texto("Cuando el operador te asigne una, aparecerá aquí y recibirás una notificación.", 14f, ui.tintaSec)) })
            r.items.forEach { parada ->
                val (rotulo, color) = ui.estado(parada.estado)
                val texto = LinearLayout(this).apply {
                    orientation = LinearLayout.VERTICAL; layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
                    addView(ui.texto(parada.folio, 16f, ui.tinta, true)); addView(ui.texto(parada.direccion, 14f, ui.tintaSec))
                    if (!parada.direccion.contains(parada.zona)) addView(ui.texto(parada.zona, 13f, ui.tintaSec))
                }
                val tarjeta = ui.tarjeta(accion { openDelivery(parada.id) })
                tarjeta.addView(ui.fila(ui.circulo("${parada.orden}", ui.primario, 38), texto, ui.chip(rotulo, color)))
                tarjeta.addView(ui.espacio(10))
                tarjeta.addView(ui.fila(ui.flexible(ui.texto("$%.2f".format(parada.total), 20f, ui.tinta, true)),
                    ui.texto("%.1f km · %.0f min".format(parada.distanciaKm, parada.minutos), 13f, ui.tintaSec).apply {
                        layoutParams = LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT) }))
                p.agregar(tarjeta)
            }
            paginacion(r.pagina, r.paginas) { deliveries(it) }
        }
    }

    private fun openDelivery(id: Int) {
        work({ entregas.detalle(id) }) { d ->
            resetEvidence()
            detalle = d
            formResultado = "entregado"; formMonto = "%.2f".format(d.total); formCambio = "0"; formNota = ""; scrollY = 0
            formDevueltas.clear(); formMotivos.clear()
            deliveryForm()
        }
    }

    private fun number(text: String) = text.trim().replace(',', '.').toDoubleOrNull()

    /** Guarda lo escrito en el formulario antes de que una acción (QR, foto, GPS) reconstruya la pantalla. */
    private fun saveForm() {
        fMonto?.let { formMonto = it.text.toString() }
        fCambio?.let { formCambio = it.text.toString() }
        fNota?.let { formNota = it.text.toString() }
        fMotivos.forEach { (id, campo) -> formMotivos[id] = campo.text.toString() }
        if (::p.isInitialized) scrollY = p.scroll.scrollY
    }

    private fun filaEvidencia(titulo: String, estado: String, color: Int, boton: String, accion: () -> Unit): LinearLayout {
        val texto = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL; layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
            addView(ui.texto(titulo, 15f, ui.tinta, true)); addView(ui.texto(estado, 13f, color))
        }
        return ui.fila(texto, ui.botonCompacto(boton, Tipo.SECUNDARIO) { if (!busy) accion() }).apply {
            setPadding(0, ui.dp(6), 0, ui.dp(6))
        }
    }

    private fun deliveryForm() {
        val d = detalle ?: return home()
        nueva("Entrega", "${d.folio} · ${d.cliente}") { resetEvidence(); detalle = null; deliveries(1) }
        val (rotulo, colorEstado) = ui.estado(d.estado)

        // Cliente, dirección y total
        val cliente = ui.tarjeta()
        val datos = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL; layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
            addView(ui.texto(d.cliente, 18f, ui.tinta, true)); addView(ui.texto(d.direccion, 14f, ui.tintaSec))
            if (d.telefono.isNotBlank()) addView(ui.texto("Tel. ${d.telefono}", 14f, ui.tintaSec))
        }
        cliente.addView(ui.fila(datos, ui.chip(rotulo, colorEstado)))
        cliente.addView(ui.espacio(10))
        cliente.addView(ui.fila(ui.flexible(ui.texto("Total a cobrar", 14f, ui.tintaSec)), ui.texto("$%.2f".format(d.total), 24f, ui.tinta, true).apply {
            layoutParams = LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT) }))
        p.agregar(cliente)
        if (entregas.hayCierrePendiente(d.id)) p.aviso("Hay un cierre sin confirmar de esta entrega: se reintentará con el mismo identificador, sin duplicarse.", Mensaje.INFO)

        // Evidencia
        p.agregar(ui.titulo("Evidencia"))
        val evidencia = ui.tarjeta()
        val qr = scannedOrder
        evidencia.addView(filaEvidencia("QR del pedido",
            when { qr == null -> "Pendiente"; qr == d.pedidoId -> "✓ Correcto · pedido $qr"; else -> "✗ No corresponde · pedido $qr" },
            when { qr == null -> ui.tintaSec; qr == d.pedidoId -> ui.ok; else -> ui.peligro }, "Escanear") { scanQr() })
        evidencia.addView(filaEvidencia("Foto de evidencia",
            if (photo != null) "✓ Capturada · ${photo!!.size / 1024} KB" else if (entregas.tieneEvidencia(d.id)) "✓ Ya subida" else "Pendiente",
            if (photo != null || entregas.tieneEvidencia(d.id)) ui.ok else ui.tintaSec, "Tomar foto") { capturePhoto() })
        val gps = position
        evidencia.addView(filaEvidencia("Ubicación GPS",
            gps?.let { "✓ %.5f, %.5f · ±%.0f m · %d punto(s)".format(it.latitude, it.longitude, it.accuracy, route.size) } ?: "Pendiente",
            if (gps != null) ui.ok else ui.tintaSec, "Obtener GPS") { saveForm(); gps() })
        evidencia.addView(ui.boton("Consultar pedido", Tipo.TEXTO) {
            if (!busy) work({ api.call("pedidos", "pedidos/${d.pedidoId}") }) { r ->
                AlertDialog.Builder(this).setTitle("Pedido ${r.optString("folio", d.folio)}").setMessage("Estado: ${ui.estado(r.optString("estado")).first}\nTotal: $${r.optString("total")}")
                    .setPositiveButton("Cerrar", null).show()
            }
        })
        p.agregar(evidencia)

        // Resultado
        p.agregar(ui.titulo("Resultado"))
        val resultado = ui.tarjeta()
        val lineasTarjeta = ui.tarjeta().apply { visibility = if (formResultado == "parcial") View.VISIBLE else View.GONE }
        fMonto = ui.campo("Monto cobrado", formMonto, numerico = true)
        fCambio = ui.campo("Cambio entregado", formCambio, numerico = true)
        fNota = ui.campo("Observaciones", formNota)
        fun ajustar() { fMonto!!.isEnabled = formResultado != "fallida"; fMonto!!.alpha = if (formResultado == "fallida") 0.5f else 1f }
        resultado.addView(ui.segmentos(listOf("entregado" to "Entregado", "parcial" to "Parcial", "fallida" to "Fallida"), formResultado) { nuevo ->
            saveForm(); formResultado = nuevo
            when (nuevo) { "fallida" -> { formMonto = "0"; fMonto!!.setText("0") }; "entregado" -> { formMonto = "%.2f".format(d.total); fMonto!!.setText(formMonto) } }
            lineasTarjeta.visibility = if (nuevo == "parcial") View.VISIBLE else View.GONE
            ajustar()
        })
        resultado.addView(ui.etiqueta("Monto cobrado")); resultado.addView(fMonto!!)
        resultado.addView(ui.etiqueta("Cambio entregado")); resultado.addView(fCambio!!)
        resultado.addView(ui.etiqueta("Observaciones / incidencia (obligatoria si es fallida)")); resultado.addView(fNota!!)
        ajustar()
        p.agregar(resultado)

        // Líneas (solo entrega parcial)
        lineasTarjeta.addView(ui.texto("Líneas del pedido", 16f, ui.tinta, true))
        lineasTarjeta.addView(ui.texto("Indica cuántas unidades regresan y por qué.", 13f, ui.tintaSec))
        fMotivos.clear()
        d.lineas.forEach { l ->
            val cuenta = ui.texto("${formDevueltas[l.pedidoDetalleId] ?: 0}", 18f, ui.tinta, true).apply { gravity = Gravity.CENTER; layoutParams = LinearLayout.LayoutParams(ui.dp(36), ViewGroup.LayoutParams.WRAP_CONTENT) }
            val motivo = ui.campo("Motivo de la devolución", formMotivos[l.pedidoDetalleId] ?: "")
            fMotivos[l.pedidoDetalleId] = motivo
            fun refrescar() { val n = formDevueltas[l.pedidoDetalleId] ?: 0; cuenta.text = "$n"; motivo.visibility = if (n > 0) View.VISIBLE else View.GONE }
            val menos = ui.botonCompacto("−") { formDevueltas[l.pedidoDetalleId] = maxOf(0, (formDevueltas[l.pedidoDetalleId] ?: 0) - 1); refrescar() }
            val mas = ui.botonCompacto("+") { formDevueltas[l.pedidoDetalleId] = minOf(l.cantidad, (formDevueltas[l.pedidoDetalleId] ?: 0) + 1); refrescar() }
            val nombre = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL; layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
                addView(ui.texto(l.nombre, 15f, ui.tinta, true)); addView(ui.texto("Pedidas: ${l.cantidad} · devueltas:", 13f, ui.tintaSec))
            }
            listOf(menos, mas).forEach { it.layoutParams = LinearLayout.LayoutParams(ui.dp(48), ui.dp(48)) }
            lineasTarjeta.addView(ui.espacio(8)); lineasTarjeta.addView(ui.fila(nombre, menos, cuenta, mas)); lineasTarjeta.addView(motivo)
            refrescar()
        }
        p.agregar(lineasTarjeta)
        p.conPie(ui.boton("Registrar resultado", Tipo.PRIMARIO) { if (!busy) register(d) })
        val y = scrollY
        p.scroll.post { p.scroll.scrollTo(0, y) }
    }

    private fun register(d: Detalle) {
        saveForm()
        val gps = position
        if (scannedOrder != d.pedidoId) { error("Escanea el QR del pedido ${d.pedidoId}"); return }
        if (gps == null) { error("Obtén el GPS antes de registrar"); return }
        if (photo == null && !entregas.tieneEvidencia(d.id)) { error("Toma la foto de evidencia"); return }
        val monto = number(formMonto); val cambio = number(formCambio)
        if (monto == null || cambio == null) { error("Escribe montos válidos (número con punto decimal)"); return }
        val lineas = d.lineas.map { l -> LineaCierre(l, formDevueltas[l.pedidoDetalleId] ?: 0, formMotivos[l.pedidoDetalleId] ?: "") }
        val datos = DatosCierre(formResultado, monto, cambio, formNota, lineas, Fix(gps.latitude, gps.longitude, gps.accuracy.toDouble(), gps.time))
        try { entregas.validar(d, datos) } catch (ex: IllegalArgumentException) { error(ex.message ?: "Revisa los datos"); return }
        val evidence = photo
        val points = route.toList()
        work({ entregas.cerrar(d, datos, evidence, points) }) { r ->
            resetEvidence(); detalle = null
            Toast.makeText(this, "Entrega ${if (r.duplicado) "ya registrada" else "registrada"}: ${ui.estado(r.estadoPedido).first}", Toast.LENGTH_LONG).show()
            deliveries(1)
            p.aviso("Entrega ${if (r.duplicado) "ya estaba registrada" else "registrada"} · ${ui.estado(r.estadoPedido).first}", Mensaje.EXITO)
        }
    }

    // ------------------------------------------------------------------------------------------ cámara, QR y GPS
    private fun scanQr() {
        saveForm()
        if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) { requestPermissions(arrayOf(Manifest.permission.CAMERA), 10); p.aviso("Concede el permiso de cámara y vuelve a pulsar.", Mensaje.INFO); return }
        @Suppress("DEPRECATION")
        IntentIntegrator(this).setDesiredBarcodeFormats(IntentIntegrator.QR_CODE).setPrompt("Escanea el ID numérico del pedido").setBeepEnabled(false).initiateScan()
    }

    private fun capturePhoto() {
        saveForm()
        val d = detalle ?: return
        if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) { requestPermissions(arrayOf(Manifest.permission.CAMERA), 10); p.aviso("Concede el permiso de cámara y vuelve a pulsar.", Mensaje.INFO); return }
        val file = File(File(cacheDir, "fotos").apply { mkdirs() }, "evidencia-${d.id}.jpg").also { it.delete(); it.createNewFile() }
        photoFile = file
        val uri = Uri.parse("content://$packageName.fotos/${file.name}")
        val intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE).putExtra(MediaStore.EXTRA_OUTPUT, uri)
            .addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION or Intent.FLAG_GRANT_READ_URI_PERMISSION)
        intent.clipData = ClipData.newRawUri("evidencia", uri)
        try { @Suppress("DEPRECATION") startActivityForResult(intent, 20) } catch (_: Exception) { error("No hay aplicación de cámara disponible") }
    }

    @Suppress("DEPRECATION")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        val scan = IntentIntegrator.parseActivityResult(requestCode, resultCode, data)
        if (scan != null) {
            if (scan.contents != null) { scannedOrder = scan.contents.toIntOrNull(); deliveryForm(); if (scannedOrder != detalle?.pedidoId) error("El QR no corresponde al pedido") }
            return
        }
        if (requestCode == 20) {
            val file = photoFile
            if (resultCode == RESULT_OK && file != null && file.length() > 0) {
                try { photo = Fotos.preparar(file) } catch (ex: Exception) { file.delete(); deliveryForm(); error(ex.message ?: "No se pudo leer la foto"); return }
            }
            file?.delete()
            deliveryForm()
        }
    }

    private fun gps() {
        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(arrayOf(Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION), 11)
            p.aviso("Concede el permiso de ubicación y vuelve a pulsar.", Mensaje.INFO)
            return
        }
        manager = getSystemService(LocationManager::class.java)
        if (manager?.isProviderEnabled(LocationManager.GPS_PROVIDER) != true) { error("Activa el GPS del dispositivo"); return }
        listener?.let { manager?.removeUpdates(it) }
        listener = object : LocationListener {
            override fun onLocationChanged(location: Location) {
                position = location
                route.add(Fix(location.latitude, location.longitude, location.accuracy.toDouble(), location.time))
                manager?.removeUpdates(this); listener = null; deliveryForm()
            }
            override fun onProviderEnabled(provider: String) {}
            override fun onProviderDisabled(provider: String) { error("GPS desactivado") }
            @Deprecated("API anterior") override fun onStatusChanged(provider: String?, status: Int, extras: Bundle?) {}
        }
        manager!!.requestLocationUpdates(LocationManager.GPS_PROVIDER, 1000, 0f, listener!!)
        p.aviso("Esperando señal GPS…", Mensaje.INFO)
    }

    private fun resetEvidence() {
        photo = null; photoFile?.delete(); photoFile = null; position = null; scannedOrder = null; route.clear()
        listener?.let { manager?.removeUpdates(it) }; listener = null
        fMonto = null; fCambio = null; fNota = null; fMotivos.clear()
    }

    override fun onDestroy() { alive = false; resetEvidence(); executor.shutdownNow(); super.onDestroy() }
}
