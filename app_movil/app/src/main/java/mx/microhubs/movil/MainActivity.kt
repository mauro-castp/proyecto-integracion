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
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicBoolean

class MainActivity : Activity() {
    private lateinit var api: Api
    private lateinit var entregas: Entregas
    private lateinit var usuarios: Usuarios
    private var sede: Sede? = null
    private lateinit var cola: ColaEnArchivos
    private lateinit var sync: Sincronizador
    private lateinit var avisos: Avisos
    private lateinit var tienda: Tienda
    private val carrito = Carrito()
    private var catalogo: Catalogo? = null
    private lateinit var ui: Estilo
    private lateinit var p: Pantalla
    private var atras: (() -> Unit)? = null
    private val executor = Executors.newSingleThreadExecutor()
    // Tareas que no bloquean la pantalla: sincronizar, contar avisos y guardar copias para trabajar sin red.
    private val fondo = Executors.newSingleThreadExecutor()
    private val sincronizando = AtomicBoolean(false)
    @Volatile private var ultimoIntento = 0L
    private var viendoCola = false
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
        cola = ColaEnArchivos(File(filesDir, "sin_red"))           // almacenamiento privado de la app; sobrevive a reinicios
        entregas = Entregas(api, PrefsBorradores(this), cola)
        usuarios = Usuarios(api)
        sync = Sincronizador(api, cola)
        avisos = Avisos(api, cola)
        tienda = Tienda(api, cola)
        ui = Estilo(this)
        loginScreen()
    }

    // ------------------------------------------------------------------------------------------ pantalla y conexión
    private fun nueva(titulo: String, subtitulo: String? = null, volver: (() -> Unit)? = null): Pantalla {
        atras = volver
        viendoCola = false
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
            private fun refrescar() = runOnUiThread {
                if (alive && ::p.isInitialized) p.conexion(redActual())
                if (alive && redActual() == Red.EN_LINEA) sincronizarEnFondo()      // volvió la red: se envía lo hecho sin conexión
            }
            override fun onAvailable(network: Network) = refrescar()
            override fun onLost(network: Network) = refrescar()
            override fun onCapabilitiesChanged(network: Network, caps: NetworkCapabilities) = refrescar()
        }
        try { cm.registerDefaultNetworkCallback(cb); callbackRed = cb } catch (_: Exception) {}
        if (::p.isInitialized) p.conexion(redActual())
        sincronizarEnFondo()
    }

    // ------------------------------------------------------------------------------------------ sincronización
    /**
     * Envía la cola sin bloquear la pantalla. Automática (al volver la red, al abrir la app o el menú) como mucho cada 30 s;
     * la del botón «Enviar ahora» va por [work] para mostrar el progreso.
     */
    private fun sincronizarEnFondo() {
        if (api.demo || api.session == null || redActual() != Red.EN_LINEA) return
        val t = System.currentTimeMillis()
        if (t - ultimoIntento < 30_000 || sync.porEnviar() == 0) return
        if (!sincronizando.compareAndSet(false, true)) return
        ultimoIntento = t
        fondo.execute {
            val r = try { Result.success(sync.sincronizar()) } catch (e: Exception) { Result.failure(e) } finally { sincronizando.set(false) }
            runOnUiThread {
                if (!alive) return@runOnUiThread
                r.onSuccess { informe -> if (informe.enviadas > 0) {
                    Toast.makeText(this, resumen(informe), Toast.LENGTH_LONG).show()
                    if (viendoCola) colaScreen() else if (::p.isInitialized && (informe.conflictos + informe.rechazadas) > 0) p.aviso(resumen(informe), Mensaje.ERROR)
                } }
                r.onFailure { if (api.session == null) { loginScreen(); error("La sesión terminó: entra de nuevo para enviar lo pendiente.") } }
            }
        }
    }

    private fun resumen(i: Informe): String = listOfNotNull(
        "${i.aplicadas} enviada(s)".takeIf { i.aplicadas > 0 },
        "${i.conflictos} en conflicto (gana el servidor)".takeIf { i.conflictos > 0 },
        "${i.rechazadas} rechazada(s)".takeIf { i.rechazadas > 0 },
        "${i.pendientes} se reintentará(n)".takeIf { i.pendientes > 0 },
        "${i.esperando} esperando subir su foto".takeIf { i.esperando > 0 }
    ).joinToString(" · ").ifEmpty { "No había nada por enviar" }

    private fun hora(ms: Long): String = DateTimeFormatter.ofPattern("HH:mm").format(Instant.ofEpochMilli(ms).atZone(ZoneId.systemDefault()))
    private fun fechaCorta(iso: String) = iso.take(16).replace('T', ' ')

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
        sede = null
        nueva("Microhubs", "Entregas de proximidad")
        p.agregar(ui.espacio(8))
        val email = ui.campo("Correo").apply { inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_EMAIL_ADDRESS }
        val password = ui.campo("Clave", secreto = true)
        val host = ui.campo("Servidor (en debug http://10.0.2.2; en la nube https://…/servicios)", api.host)
        val demo = CheckBox(this).apply { text = "Usar ejemplos locales (sin red)"; isChecked = api.demo; setTextColor(ui.tintaSec) }
        val ajustes = ui.tarjeta().apply { visibility = View.GONE }
        ajustes.addView(ui.etiqueta("Servidor")); ajustes.addView(host); ajustes.addView(demo)

        val acceso = ui.tarjeta()
        acceso.addView(ui.texto("Iniciar sesión", 20f, ui.tinta, true))
        acceso.addView(ui.texto("Entra con tu cuenta de repartidor o de cliente.", 14f, ui.tintaSec))
        acceso.addView(ui.etiqueta("Correo")); acceso.addView(email)
        acceso.addView(ui.etiqueta("Clave")); acceso.addView(password)
        acceso.addView(ui.espacio(8))
        acceso.addView(ui.boton("Entrar", Tipo.PRIMARIO) {
            if (!android.util.Patterns.EMAIL_ADDRESS.matcher(email.text.toString()).matches() || password.text.isEmpty()) { error("Ingresa correo válido y clave"); return@boton }
            val mail = email.text.toString().trim()
            val pass = password.text.toString()
            api.demo = demo.isChecked; api.host = host.text.toString().trim()
            if (!busy) work({ api.login(mail, pass) }) { password.text.clear(); ultimoIntento = 0; home() }
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

    /** Menú inferior siempre visible con las secciones de cada perfil (antes había que volver al inicio para cambiar de sección). */
    private fun menu(actual: String) {
        val secciones = when (role()) {
            "cliente" -> listOf(Triple("inicio", "🏠", "Inicio"), Triple("catalogo", "🛒", "Catálogo"), Triple("carrito", "🧺", "Carrito"),
                                Triple("pedidos", "🧾", "Pedidos"), Triple("avisos", "🔔", "Avisos"))
            else -> listOf(Triple("inicio", "🏠", "Inicio"), Triple("entregas", "📦", "Entregas"), Triple("avisos", "🔔", "Avisos"), Triple("perfil", "👤", "Perfil"))
        }
        p.navegacion(secciones.map { (clave, icono, nombre) ->
            Pestana(icono, nombre, clave == actual, if (clave == "carrito" && !carrito.vacio) carrito.piezas else null) { accion { ir(clave) }() }
        })
    }

    private fun ir(clave: String) = when (clave) {
        "entregas" -> deliveries(1); "avisos" -> avisosScreen(1); "perfil" -> profile(); "catalogo" -> catalogoScreen()
        "carrito" -> carritoScreen(); "pedidos" -> pedidosScreen(1); else -> home()
    }
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

    /** Por qué le toca ese microhub: la asignación es de su cuenta (RN41) y cada pedido se asigna al más cercano que puede surtirlo. */
    private fun textoSede(s: Sede) = "Cubre %.1f km a la redonda. Es el microhub asignado a tu cuenta: solo recibes sus pedidos, ".format(s.radioKm) +
        "que el sistema le asignó por ser el más cercano al domicilio con cobertura, existencia y capacidad."

    private fun home() {
        val u = api.session!!.getJSONObject("usuario")
        nueva("Hola, ${u.getString("nombre")}", rolLegible(u.getString("rol")))
        menu("inicio")
        if (role() == "repartidor") {
            // Cada repartidor pertenece a un microhub fijo y solo recibe entregas de ese microhub (RN41).
            val titulo = ui.texto(sede?.let { "${it.clave} · ${it.nombre}" }
                ?: if (u.isNull("microhub_id")) "Sin microhub asignado: pide a tu supervisor que te asigne uno" else "Microhub ${u.getInt("microhub_id")}", 16f, ui.tinta, true)
            val detalleSede = ui.texto(sede?.let { textoSede(it) } ?: "Solo recibes entregas de este microhub.", 13f, ui.tintaSec)
            val tarjeta = ui.tarjeta()
            tarjeta.addView(ui.fila(ui.circulo("🏪", ui.primario, 44), LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL; layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
                addView(ui.texto("Tu microhub", 13f, ui.tintaSec, true)); addView(titulo); addView(detalleSede)
            }))
            val mapa = ui.botonCompacto("🗺️ Ver mi microhub en el mapa", Tipo.SECUNDARIO) { sede?.let { navegar(it.destinoMapa) } }
                .apply { visibility = if (sede == null) View.GONE else View.VISIBLE }
            tarjeta.addView(mapa)
            p.agregar(tarjeta)
            if (!u.isNull("microhub_id") && redActual() != Red.SIN_RED) fondo.execute {
                val hallada = try { usuarios.sede(u.getInt("microhub_id")) } catch (_: Exception) { null }
                runOnUiThread {
                    if (alive && hallada != null) {
                        sede = hallada; titulo.text = "${hallada.clave} · ${hallada.nombre}"
                        detalleSede.text = textoSede(hallada); mapa.visibility = View.VISIBLE
                    }
                }
            }
        }
        p.agregar(ui.titulo("¿Qué quieres hacer?"))
        if (role() in listOf("repartidor", "administrador")) p.agregar(opcion("📦", "Mis entregas", "Paradas asignadas a tu turno") { deliveries(1) })
        if (role() == "cliente") {
            p.agregar(opcion("🛒", "Catálogo", "Elige productos; también funciona sin red con el catálogo guardado") { catalogoScreen() })
            val enCarrito = ui.chip("${carrito.piezas}", ui.primario).apply { visibility = if (carrito.vacio) View.GONE else View.VISIBLE }
            p.agregar(opcion("🧺", "Mi carrito", "Revisa y haz tu pedido", enCarrito) { carritoScreen() })
            p.agregar(opcion("🧾", "Mis pedidos", "Estatus de cada pedido y confirmar que lo recibiste") { pedidosScreen(1) })
        }
        val noLeidos = ui.chip("", ui.peligro).apply { visibility = View.GONE }
        p.agregar(opcion("🔔", "Avisos", "Entregas asignadas y mensajes del equipo", noLeidos) { avisosScreen(1) })
        val mias = sync.mias()
        if (mias.isNotEmpty()) {
            val porEnviar = mias.count { it.porEnviar }; val problemas = mias.size - porEnviar
            val desc = listOfNotNull("$porEnviar por enviar".takeIf { porEnviar > 0 }, "$problemas para revisar".takeIf { problemas > 0 }).joinToString(" · ")
            p.agregar(opcion("⇅", "Sin enviar", desc, ui.chip("${mias.size}", if (problemas > 0) ui.peligro else ui.alerta)) { colaScreen() })
        }
        p.agregar(opcion("👤", "Mi perfil", "Tus datos y teléfono de contacto") { profile() })
        p.conPie(ui.boton("Cerrar sesión", Tipo.PELIGRO) {
            if (busy) return@boton
            val pendientes = sync.porEnviar()
            fun salir() = work({ try { api.logout() } finally { cola.borrarCopias() } }) { resetEvidence(); detalle = null; sede = null; carrito.vaciar(); catalogo = null; loginScreen() }
            if (pendientes == 0) salir()
            else AlertDialog.Builder(this).setTitle("Hay $pendientes operación(es) sin enviar")
                .setMessage("Se quedan guardadas en el teléfono y se enviarán cuando vuelvas a entrar con esta misma cuenta y haya red.")
                .setPositiveButton("Salir") { _, _ -> salir() }.setNegativeButton("Cancelar", null).show()
        })
        if (redActual() != Red.SIN_RED) fondo.execute {
            val n = try { avisos.noLeidas() } catch (_: Exception) { 0 }
            runOnUiThread { if (alive && n > 0) { noLeidos.text = "$n"; noLeidos.visibility = View.VISIBLE } }
        }
        sincronizarEnFondo()
    }

    // ------------------------------------------------------------------------------------------ avisos
    private fun avisosScreen(pagina: Int) { work({ avisos.bandeja(pagina) }) { pintarAvisos(it) } }

    private fun pintarAvisos(r: Pagina<Aviso>) {
        val pagina = r.pagina
        nueva("Avisos", "${r.total} aviso(s) · página $pagina de ${maxOf(1, r.paginas)}") { home() }
        menu("avisos")
        if (r.items.isEmpty()) p.agregar(ui.tarjeta().apply {
            addView(ui.texto("No tienes avisos", 16f, ui.tinta, true))
            addView(ui.texto("Aquí llegan las entregas que te asignan y los mensajes del equipo.", 14f, ui.tintaSec)) })
        r.items.forEach { a ->
            val tarjeta = ui.tarjeta(accion { abrirAviso(a, pagina) })
            val textos = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL; layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
                addView(ui.texto(a.titulo, 16f, ui.tinta, !a.leida)); addView(ui.texto(a.mensaje, 14f, ui.tintaSec))
                addView(ui.texto(fechaCorta(a.creadaEn), 12f, ui.tintaSec))
            }
            tarjeta.addView(ui.fila(textos, *listOfNotNull(if (!a.leida) ui.chip("Nuevo", ui.info) else null).toTypedArray()))
            p.agregar(tarjeta)
        }
        paginacion(r.pagina, r.paginas) { avisosScreen(it) }
        if (r.items.any { !it.leida }) p.conPie(ui.boton("Marcar todos como leídos", Tipo.SECUNDARIO) {
            if (!busy) work({ avisos.marcarTodos() to avisos.bandeja(pagina) }) { (n, bandeja) ->
                pintarAvisos(bandeja); p.aviso("$n aviso(s) marcado(s) como leído(s)", Mensaje.EXITO) }
        })
    }

    /** Lo marca como leído (sin red queda en la cola) y, si habla de una entrega, la abre. */
    private fun abrirAviso(a: Aviso, pagina: Int) {
        work({ avisos.marcarLeido(a) }) {
            val entrega = a.referenciaId?.toIntOrNull()
            if (a.referenciaTipo == "entrega" && entrega != null && role() in listOf("repartidor", "administrador")) openDelivery(entrega)
            else avisosScreen(pagina)
        }
    }

    // ------------------------------------------------------------------------------------------ cola sin red
    private fun colaScreen() {
        val ops = sync.mias().sortedBy { it.creadaEn }
        nueva("Sin enviar", "${ops.size} operación(es) en el teléfono") { home() }
        viendoCola = true
        if (ops.isEmpty()) {
            p.agregar(ui.tarjeta().apply {
                addView(ui.texto("Todo está enviado", 16f, ui.tinta, true))
                addView(ui.texto("Lo que registres sin conexión aparecerá aquí hasta que vuelva la red.", 14f, ui.tintaSec)) })
            return
        }
        p.agregar(ui.texto("Lo que hiciste sin conexión se envía solo al volver la red. Si el servidor ya tenía otro dato, gana el servidor: " +
            "esas operaciones se marcan como conflicto y no se vuelven a enviar.", 13f, ui.tintaSec).apply { setPadding(0, 0, 0, ui.dp(8)) })
        ops.forEach { op ->
            val (rotulo, color) = when (op.estado) {
                Operacion.EN_COLA -> (if (op.necesitaFoto) "Por enviar · con foto" else "Por enviar") to ui.alerta
                Operacion.PENDIENTE -> "Reintentando (${op.intentos})" to ui.alerta
                Operacion.CONFLICTO -> "Conflicto" to ui.peligro
                else -> "Rechazada" to ui.peligro
            }
            val tarjeta = ui.tarjeta()
            val textos = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL; layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
                addView(ui.texto(op.descripcion.ifBlank { op.tipo }, 15f, ui.tinta, true))
                addView(ui.texto("Hecha: ${fechaCorta(op.creadaEn)}" + (op.entregaId?.let { " · entrega $it" } ?: ""), 13f, ui.tintaSec))
            }
            tarjeta.addView(ui.fila(textos, ui.chip(rotulo, color)))
            op.mensaje?.let { tarjeta.addView(ui.texto(it, 13f, if (op.porEnviar) ui.tintaSec else ui.peligro)) }
            if (op.estado == Operacion.CONFLICTO) tarjeta.addView(ui.texto("Se conserva lo que ya estaba en el servidor; esta operación no se volverá a enviar.", 13f, ui.tintaSec))
            if (op.estado == Operacion.RECHAZADA) tarjeta.addView(ui.texto("No se volverá a enviar. Si hace falta, registra de nuevo la entrega con red.", 13f, ui.tintaSec))
            if (!op.porEnviar) tarjeta.addView(ui.boton("Entendido, quitar de la lista", Tipo.TEXTO) { sync.descartar(op.uuid); colaScreen() })
            p.agregar(tarjeta)
        }
        if (ops.any { it.porEnviar }) p.conPie(ui.boton("Enviar ahora", Tipo.PRIMARIO) {
            if (busy) return@boton
            if (redActual() == Red.SIN_RED) { error("Sin conexión: se enviará solo cuando vuelva la red."); return@boton }
            work({ sync.sincronizar() }) { i -> colaScreen(); p.aviso(resumen(i), if (i.conflictos + i.rechazadas > 0) Mensaje.ERROR else Mensaje.EXITO) }
        })
    }

    // ------------------------------------------------------------------------------------------ navegar (repartidor)
    /** Abre la app de mapas instalada en el domicilio. Sin app de mapas no hay a dónde mandar: se avisa. */
    private fun navegar(destino: String) {
        try { startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(destino))) }
        catch (_: android.content.ActivityNotFoundException) { error("No hay una app de mapas en el teléfono para navegar.") }
    }

    // ------------------------------------------------------------------------------------------ cliente
    private fun catalogoScreen(categoria: String? = null, texto: String = "") {
        val actual = catalogo
        if (actual == null) { work({ tienda.catalogo() }) { catalogo = it; catalogoScreen(categoria, texto) }; return }
        nueva("Catálogo", "${actual.productos.size} productos" + (categoria?.let { " · $it" } ?: "")) { home() }
        menu("catalogo")
        actual.guardadoEn?.let { p.aviso("Sin conexión: catálogo guardado a las ${hora(it)}. Puedes armar tu pedido; se enviará al volver la red.", Mensaje.INFO) }
        val buscar = ui.campo("Buscar producto", texto)
        p.agregar(ui.fila(ui.flexible(buscar), ui.botonCompacto("Buscar", Tipo.SECUNDARIO) { catalogoScreen(categoria, buscar.text.toString()) }))
        val cats = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        cats.addView(ui.boton(if (categoria == null) "• Todas las categorías" else "Todas las categorías", Tipo.TEXTO) { catalogoScreen(null, buscar.text.toString()) })
        actual.categorias.forEach { c -> cats.addView(ui.boton(if (c == categoria) "• $c" else c, Tipo.TEXTO) { catalogoScreen(c, buscar.text.toString()) }) }
        p.agregar(cats)
        val lista = actual.buscar(texto, categoria)
        if (lista.isEmpty()) p.agregar(ui.texto("No hay productos con esa búsqueda.", 14f, ui.tintaSec))
        lista.take(60).forEach { prod ->
            val tarjeta = ui.tarjeta()
            val cuenta = ui.texto("${carrito.cantidad(prod.id)}", 18f, ui.tinta, true).apply { gravity = Gravity.CENTER; minWidth = ui.dp(36) }
            val textos = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL; layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
                addView(ui.texto(prod.nombre, 16f, ui.tinta, true)); addView(ui.texto(listOf(prod.presentacion, prod.unidad).filter { it.isNotBlank() }.joinToString(" · "), 13f, ui.tintaSec))
                addView(ui.texto("$%.2f".format(prod.precio), 15f, ui.tinta))
            }
            val menos = ui.botonCompacto("−", Tipo.SECUNDARIO) { carrito.quitar(prod.id); cuenta.text = "${carrito.cantidad(prod.id)}" }
            val mas = ui.botonCompacto("+", Tipo.SECUNDARIO) { carrito.agregar(prod.id); cuenta.text = "${carrito.cantidad(prod.id)}" }
            listOf(menos, mas).forEach { it.layoutParams = LinearLayout.LayoutParams(ui.dp(48), ui.dp(48)) }
            tarjeta.addView(ui.fila(textos, menos, cuenta, mas))
            p.agregar(tarjeta)
        }
        if (lista.size > 60) p.agregar(ui.texto("Se muestran 60 de ${lista.size}; usa la búsqueda o una categoría.", 13f, ui.tintaSec))
        p.conPie(ui.boton("Ver carrito", Tipo.PRIMARIO) { carritoScreen() })
    }

    private fun carritoScreen() {
        val c = catalogo
        nueva("Mi carrito", "${carrito.piezas} pieza(s)") { home() }
        menu("carrito")
        if (carrito.vacio || c == null) {
            p.agregar(ui.tarjeta().apply { addView(ui.texto("Tu carrito está vacío", 16f, ui.tinta, true)); addView(ui.texto("Agrega productos desde el catálogo.", 14f, ui.tintaSec)) })
            p.conPie(ui.boton("Ir al catálogo", Tipo.PRIMARIO) { catalogoScreen() })
            return
        }
        carrito.items().forEach { (id, n) ->
            val prod = c.productos.firstOrNull { it.id == id } ?: return@forEach
            val tarjeta = ui.tarjeta()
            tarjeta.addView(ui.fila(ui.flexible(ui.texto("$n × ${prod.nombre}", 15f, ui.tinta, true)), ui.texto("$%.2f".format(prod.precio * n), 15f, ui.tinta)))
            tarjeta.addView(ui.fila(ui.botonCompacto("Quitar uno", Tipo.TEXTO) { carrito.quitar(id); carritoScreen() }, ui.botonCompacto("Agregar uno", Tipo.TEXTO) { carrito.agregar(id); carritoScreen() }))
            p.agregar(tarjeta)
        }
        p.agregar(ui.tarjeta().apply {
            addView(ui.fila(ui.flexible(ui.texto("Total estimado", 14f, ui.tintaSec)), ui.texto("$%.2f".format(carrito.estimado(c)), 22f, ui.tinta, true)))
            addView(ui.texto("El total final (precio de tu zona y costo de envío) lo calcula el servidor al recibir el pedido.", 13f, ui.tintaSec))
        })
        val sinRed = redActual() == Red.SIN_RED
        p.conPie(ui.boton(if (sinRed) "Guardar pedido (sin red)" else "Hacer pedido", Tipo.PRIMARIO) {
            if (busy) return@boton
            work({ tienda.pedir(carrito, conRed = !sinRed) }) { r ->
                if (r.enCola) { home(); p.aviso("Sin conexión: tu pedido quedó guardado y se enviará solo al volver la red (lo ves en «Sin enviar»).", Mensaje.INFO) }
                else { pedidoScreen(r.id!!); p.aviso("Pedido ${r.folio} ${if (r.duplicado) "ya estaba registrado" else "recibido"} · total $%.2f".format(r.total ?: 0.0), Mensaje.EXITO) }
            }
        })
    }

    private fun pedidosScreen(pagina: Int) {
        work({ tienda.misPedidos(pagina) }) { r ->
            nueva("Mis pedidos", "${r.total} pedido(s) · página $pagina de ${maxOf(1, r.paginas)}") { home() }
            menu("pedidos")
            r.guardadaEn?.let { p.aviso("Sin conexión: lista guardada a las ${hora(it)}.", Mensaje.INFO) }
            if (r.items.isEmpty()) p.agregar(ui.tarjeta().apply { addView(ui.texto("Todavía no tienes pedidos", 16f, ui.tinta, true)) })
            r.items.forEach { ped ->
                val (_, color) = ui.estado(ped.estado)
                val tarjeta = ui.tarjeta(accion { pedidoScreen(ped.id) })
                val textos = LinearLayout(this).apply {
                    orientation = LinearLayout.VERTICAL; layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
                    addView(ui.texto(ped.folio, 16f, ui.tinta, true)); addView(ui.texto(fechaCorta(ped.creadoEn), 13f, ui.tintaSec))
                }
                tarjeta.addView(ui.fila(textos, ui.chip(Tienda.estadoLegible(ped.estado), color)))
                tarjeta.addView(ui.texto("$%.2f".format(ped.total), 18f, ui.tinta, true))
                p.agregar(tarjeta)
            }
            paginacion(r.pagina, r.paginas) { pedidosScreen(it) }
        }
    }

    private fun pedidoScreen(id: Int) {
        work({ tienda.detalle(id) }) { d ->
            nueva("Pedido", d.folio) { pedidosScreen(1) }
            d.guardadoEn?.let { p.aviso("Sin conexión: datos guardados a las ${hora(it)}.", Mensaje.INFO) }
            val (_, color) = ui.estado(d.estado)
            p.agregar(ui.tarjeta().apply {
                addView(ui.fila(ui.flexible(ui.texto("Estatus", 14f, ui.tintaSec)), ui.chip(Tienda.estadoLegible(d.estado), color)))
                addView(ui.espacio(8))
                d.lineas.forEach { l -> addView(ui.fila(ui.flexible(ui.texto("${l.cantidad} × ${l.nombre}", 14f, ui.tinta)), ui.texto("$%.2f".format(l.importe), 14f, ui.tinta))) }
                addView(ui.espacio(6))
                addView(ui.fila(ui.flexible(ui.texto("Envío", 13f, ui.tintaSec)), ui.texto("$%.2f".format(d.costoEnvio), 13f, ui.tintaSec)))
                addView(ui.fila(ui.flexible(ui.texto("Total", 15f, ui.tinta, true)), ui.texto("$%.2f".format(d.total), 20f, ui.tinta, true)))
            })
            if (d.eventos.isNotEmpty()) {
                p.agregar(ui.titulo("Seguimiento"))
                p.agregar(ui.tarjeta().apply { d.eventos.forEach { e ->
                    addView(ui.texto("${fechaCorta(e.fecha)} · ${Tienda.estadoLegible(e.estado)}" + (e.motivo?.let { " · $it" } ?: ""), 13f, ui.tintaSec)) } })
            }
            when {
                d.confirmable -> p.conPie(
                    ui.boton("Sí, lo recibí", Tipo.PRIMARIO) { if (!busy) work({ tienda.confirmarRecepcion(d.id, true) }) { p.aviso("Gracias: confirmaste que recibiste tu pedido.", Mensaje.EXITO) } },
                    ui.boton("No estoy conforme", Tipo.TEXTO) { if (!busy) work({ tienda.confirmarRecepcion(d.id, false) }) { p.aviso("Quedó registrado que no estás conforme; el microhub lo revisará.", Mensaje.INFO) } })
                d.cancelable -> p.conPie(ui.boton("Cancelar pedido", Tipo.PELIGRO) {
                    val motivo = ui.campo("Motivo")
                    AlertDialog.Builder(this).setTitle("¿Cancelar ${d.folio}?").setView(motivo)
                        .setPositiveButton("Cancelar pedido") { _, _ -> work({ tienda.cancelar(d.id, motivo.text.toString()) }) { pedidoScreen(d.id) } }
                        .setNegativeButton("Volver", null).show()
                })
            }
        }
    }

    // ------------------------------------------------------------------------------------------ perfil
    private fun profile() { work({ usuarios.yo() }) { profileForm(it) } }

    private fun profileForm(perfil: Perfil) {
        nueva("Mi perfil", perfil.correo) { home() }
        menu("perfil")
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
            menu("entregas")
            r.guardadaEn?.let { p.aviso("Sin conexión: lista guardada a las ${hora(it)}. Puedes cerrar entregas; se enviarán al volver la red.", Mensaje.INFO) }
            if (r.guardadaEn == null && !api.demo) fondo.execute { try { entregas.guardarParaSinRed(r.items) } catch (_: Exception) {} }
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
                val chip = if (entregas.cierreEnCola(parada.id) != null) ui.chip("Por enviar", ui.alerta) else ui.chip(rotulo, color)
                tarjeta.addView(ui.fila(ui.circulo("${parada.orden}", ui.primario, 38), texto, chip))
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
        val base = sede
        if (base != null && d.latitud != null && d.longitud != null) {
            val dentro = base.distanciaKm(d.latitud, d.longitud) <= base.radioKm
            cliente.addView(ui.texto(base.cobertura(d.latitud, d.longitud), 13f, if (dentro) ui.primario else ui.peligro, true))
        }
        d.destinoMapa?.let { destino -> cliente.addView(ui.botonCompacto("🧭 Navegar al domicilio", Tipo.SECUNDARIO) { navegar(destino) }) }
        cliente.addView(ui.espacio(10))
        cliente.addView(ui.fila(ui.flexible(ui.texto("Total a cobrar", 14f, ui.tintaSec)), ui.texto("$%.2f".format(d.total), 24f, ui.tinta, true).apply {
            layoutParams = LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT) }))
        p.agregar(cliente)
        val enCola = entregas.cierreEnCola(d.id)
        if (enCola != null) p.aviso("El cierre de esta entrega ya está guardado en el teléfono (${fechaCorta(enCola.creadaEn)}) y se enviará al volver la red.", Mensaje.INFO)
        else if (entregas.hayCierrePendiente(d.id)) p.aviso("Hay un cierre sin confirmar de esta entrega: se reintentará con el mismo identificador, sin duplicarse.", Mensaje.INFO)

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
        if (enCola == null) p.conPie(ui.boton(if (redActual() == Red.SIN_RED) "Guardar resultado (sin red)" else "Registrar resultado", Tipo.PRIMARIO) { if (!busy) register(d) })
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
        val conRed = redActual() != Red.SIN_RED
        work({ entregas.cerrar(d, datos, evidence, points, conRed) }) { r ->
            resetEvidence(); detalle = null
            if (r.enCola) {
                Toast.makeText(this, "Sin red: el cierre quedó guardado y se enviará solo al volver la conexión", Toast.LENGTH_LONG).show()
                deliveries(1)
                return@work
            }
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

    override fun onDestroy() { alive = false; resetEvidence(); executor.shutdownNow(); fondo.shutdown(); super.onDestroy() }
}
