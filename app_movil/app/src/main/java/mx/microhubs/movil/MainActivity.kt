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
import android.net.NetworkCapabilities
import android.net.Uri
import android.os.Bundle
import android.provider.MediaStore
import android.text.InputType
import android.view.View
import android.widget.*
import com.google.zxing.integration.android.IntentIntegrator
import java.io.File
import java.util.concurrent.Executors

class MainActivity : Activity() {
    private lateinit var api: Api
    private lateinit var entregas: Entregas
    private lateinit var avisos: Notificaciones
    private lateinit var layout: LinearLayout
    private lateinit var status: TextView
    private val executor = Executors.newSingleThreadExecutor()
    private var busy = false
    private var alive = true

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
    private val formDevueltas = mutableMapOf<Int, String>()
    private val formMotivos = mutableMapOf<Int, String>()
    private var fResultado: Spinner? = null
    private var fMonto: EditText? = null
    private var fCambio: EditText? = null
    private var fNota: EditText? = null
    private val fLineas = mutableMapOf<Int, Pair<EditText, EditText>>()

    override fun onCreate(state: Bundle?) {
        super.onCreate(state)
        api = Api(SessionStore(this))
        entregas = Entregas(api, PrefsBorradores(this))
        avisos = Notificaciones(api)
        loginScreen()
    }

    // ------------------------------------------------------------------------------------------ utilidades de pantalla
    private fun screen(title: String) {
        layout = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(24, 48, 24, 24) }
        setContentView(ScrollView(this).apply { addView(layout) })
        layout.addView(TextView(this).apply { text = title; textSize = 24f })
        status = TextView(this).apply { text = connectionLabel() }
        layout.addView(status)
    }

    private fun connectionLabel(): String {
        if (api.demo) return "EJEMPLOS LOCALES · sin conexión al backend"
        val cm = getSystemService(ConnectivityManager::class.java)
        return if (cm.getNetworkCapabilities(cm.activeNetwork)?.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED) == true) "Red disponible" else "Sin conexión"
    }

    override fun onResume() { super.onResume(); if (::status.isInitialized) status.text = connectionLabel() }

    private fun text(content: String) = TextView(this).apply { text = content; setPadding(0, 16, 0, 8) }.also { layout.addView(it) }

    private fun field(hint: String, secret: Boolean = false, number: Boolean = false, value: String = ""): EditText = EditText(this).apply {
        this.hint = hint
        setText(value)
        if (secret) inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_PASSWORD
        if (number) inputType = InputType.TYPE_CLASS_NUMBER or InputType.TYPE_NUMBER_FLAG_DECIMAL
        this@MainActivity.layout.addView(this)
    }

    private fun button(label: String, action: () -> Unit) {
        layout.addView(Button(this).apply { text = label; setOnClickListener { if (!busy) action() } })
    }

    private fun describe(e: Exception): String {
        if (e !is ApiError) return e.message ?: "Error de conexión"
        val campos = e.fields.entries.joinToString("\n") { "• ${it.key}: ${it.value}" }
        return listOf(e.message ?: "", campos, if (e.trace.isNotEmpty()) "Traza: ${e.trace}" else "").filter { it.isNotEmpty() }.joinToString("\n")
    }

    private fun error(message: String) { status.text = message; Toast.makeText(this, message, Toast.LENGTH_LONG).show() }

    private fun <T> work(task: () -> T, done: (T) -> Unit) {
        if (busy) return
        busy = true; status.text = "Procesando…"
        executor.execute {
            try {
                val result = task()
                runOnUiThread { if (alive) { busy = false; status.text = connectionLabel(); done(result) } }
            } catch (e: Exception) {
                runOnUiThread { if (alive) { busy = false; if (api.session == null) loginScreen(); error(describe(e)) } }
            }
        }
    }

    // ------------------------------------------------------------------------------------------ acceso
    private fun loginScreen() {
        screen("Microhubs · Acceso")
        val host = field("Servidor (en debug http://10.0.2.2; en producción https://…)", value = api.host)
        val demo = CheckBox(this).apply { text = "Usar ejemplos locales"; isChecked = api.demo }
        layout.addView(demo)
        val email = field("Correo")
        val password = field("Clave", secret = true)
        button("Entrar") {
            if (!android.util.Patterns.EMAIL_ADDRESS.matcher(email.text.toString()).matches() || password.text.isEmpty()) { error("Ingresa correo válido y clave"); return@button }
            val mail = email.text.toString().trim()
            val pass = password.text.toString()
            api.demo = demo.isChecked; api.host = host.text.toString().trim()
            work({ api.login(mail, pass) }) { password.text.clear(); home() }
        }
        button("Restaurar sesión segura") {
            api.demo = demo.isChecked; api.host = host.text.toString().trim()
            if (api.demo) { error("La sesión demo no se guarda"); return@button }
            work({ api.restore(); require(api.session != null) { "No hay sesión guardada" }; api.call("usuarios", "usuarios/yo") }) { home() }
        }
    }

    private fun role() = api.session!!.getJSONObject("usuario").getString("rol")

    private fun home() {
        screen("Microhubs · ${role()}")
        button("Mi perfil") {
            work({ api.call("usuarios", "usuarios/yo") }) { p ->
                AlertDialog.Builder(this).setTitle("Perfil")
                    .setMessage("${p.getString("nombre")} ${p.getString("apellidos")}\n${p.getString("correo")}\nTeléfono: ${p.optString("telefono", "—")}\nRol: ${p.getString("rol")}")
                    .setPositiveButton("Cerrar", null).show()
            }
        }
        if (role() in listOf("repartidor", "administrador")) button("Mis entregas") { deliveries(1) }
        val notif = Button(this).apply { text = "Notificaciones"; setOnClickListener { if (!busy) notifications(1) } }
        layout.addView(notif)
        executor.execute { try { val n = avisos.noLeidas(); runOnUiThread { if (alive && n > 0) notif.text = "Notificaciones ($n sin leer)" } } catch (_: Exception) {} }
        button("Cerrar sesión") {
            work({ api.logout() }) { resetEvidence(); detalle = null; loginScreen() }
        }
    }

    // ------------------------------------------------------------------------------------------ notificaciones
    private fun notifications(page: Int) {
        work({ avisos.lista(page) }) { r ->
            screen("Notificaciones · página $page")
            if (r.items.isEmpty()) text("No tienes notificaciones.")
            r.items.forEach { a ->
                button((if (a.leida) "" else "● ") + a.titulo) {
                    work({ if (!a.leida) avisos.leer(a.id); a }) {
                        AlertDialog.Builder(this).setTitle(a.titulo).setMessage("${a.mensaje}\n\n${a.creadaEn}")
                            .setPositiveButton("Cerrar") { _, _ -> notifications(page) }.show()
                    }
                }
            }
            if (page > 1) button("Anterior") { notifications(page - 1) }
            if (page < r.paginas) button("Siguiente") { notifications(page + 1) }
            button("Menú") { home() }
        }
    }

    // ------------------------------------------------------------------------------------------ entregas
    private fun deliveries(page: Int) {
        work({ entregas.mias(page) }) { r ->
            screen("Mis entregas · página $page")
            if (r.items.isEmpty()) text("No tienes entregas pendientes.")
            r.items.forEach { p ->
                button("Parada ${p.orden} · ${p.folio}\n${p.direccion}\n${p.estado} · $${"%.2f".format(p.total)}") { openDelivery(p.id) }
            }
            if (page > 1) button("Anterior") { deliveries(page - 1) }
            if (page < r.paginas) button("Siguiente") { deliveries(page + 1) }
            button("Menú") { home() }
        }
    }

    private fun openDelivery(id: Int) {
        work({ entregas.detalle(id) }) { d ->
            resetEvidence()
            detalle = d
            formResultado = "entregado"; formMonto = "%.2f".format(d.total); formCambio = "0"; formNota = ""
            formDevueltas.clear(); formMotivos.clear()
            deliveryForm()
        }
    }

    private fun number(text: String) = text.trim().replace(',', '.').toDoubleOrNull()

    /** Guarda lo escrito en el formulario antes de que una acción (QR, foto, GPS) reconstruya la pantalla. */
    private fun saveForm() {
        fResultado?.selectedItem?.toString()?.let { formResultado = it }
        fMonto?.let { formMonto = it.text.toString() }
        fCambio?.let { formCambio = it.text.toString() }
        fNota?.let { formNota = it.text.toString() }
        fLineas.forEach { (id, v) -> formDevueltas[id] = v.first.text.toString(); formMotivos[id] = v.second.text.toString() }
    }

    private fun deliveryForm() {
        val d = detalle ?: return home()
        screen("Entrega · ${d.folio}")
        text("Cliente: ${d.cliente}${if (d.telefono.isNotBlank()) " · ${d.telefono}" else ""}\nDirección: ${d.direccion}\nTotal a cobrar: $${"%.2f".format(d.total)}")
        if (entregas.hayCierrePendiente(d.id)) text("Hay un cierre sin confirmar de esta entrega: se reintentará con el mismo identificador, sin duplicarse.")
        text("QR: ${scannedOrder?.let { if (it == d.pedidoId) "correcto" else "no corresponde (pedido $it)" } ?: "pendiente"}\n" +
            "Foto: ${if (photo == null) (if (entregas.tieneEvidencia(d.id)) "ya subida" else "pendiente") else "capturada (${photo!!.size / 1024} KB)"}\n" +
            "GPS: ${position?.let { "%.5f, %.5f (±%.0f m) · %d puntos".format(it.latitude, it.longitude, it.accuracy, route.size) } ?: "pendiente"}")
        button("Consultar pedido") {
            work({ api.call("pedidos", "pedidos/${d.pedidoId}") }) { p ->
                AlertDialog.Builder(this).setTitle("Pedido ${p.optString("folio", d.folio)}").setMessage("Estado: ${p.optString("estado")}\nTotal: ${p.optString("total")}")
                    .setPositiveButton("Cerrar", null).show()
            }
        }
        button("Escanear QR del pedido") {
            saveForm()
            if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) { requestPermissions(arrayOf(Manifest.permission.CAMERA), 10); status.text = "Concede el permiso y vuelve a pulsar."; return@button }
            @Suppress("DEPRECATION")
            IntentIntegrator(this).setDesiredBarcodeFormats(IntentIntegrator.QR_CODE).setPrompt("Escanea el ID numérico del pedido").setBeepEnabled(false).initiateScan()
        }
        button("Foto de evidencia") { capturePhoto() }
        button("Obtener GPS") { saveForm(); gps() }

        fResultado = Spinner(this).apply {
            val options = listOf("entregado", "parcial", "fallida")
            adapter = ArrayAdapter(this@MainActivity, android.R.layout.simple_spinner_dropdown_item, options)
            setSelection(options.indexOf(formResultado).coerceAtLeast(0))
        }.also { layout.addView(it) }
        text("Monto cobrado")
        fMonto = field("Monto cobrado", number = true, value = formMonto)
        text("Cambio entregado")
        fCambio = field("Cambio entregado", number = true, value = formCambio)
        text("Observaciones / incidencia (obligatoria si es fallida)")
        fNota = field("Observaciones", value = formNota)
        val parcial = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }.also { layout.addView(it) }
        fLineas.clear()
        parcial.addView(TextView(this).apply { text = "Líneas del pedido: indica cuántas unidades regresan y por qué" })
        d.lineas.forEach { l ->
            parcial.addView(TextView(this).apply { text = "${l.nombre} · pedidas ${l.cantidad}"; setPadding(0, 12, 0, 0) })
            val devueltas = EditText(this).apply { hint = "Unidades devueltas"; inputType = InputType.TYPE_CLASS_NUMBER; setText(formDevueltas[l.pedidoDetalleId] ?: "0") }
            val motivo = EditText(this).apply { hint = "Motivo de la devolución"; setText(formMotivos[l.pedidoDetalleId] ?: "") }
            parcial.addView(devueltas); parcial.addView(motivo)
            fLineas[l.pedidoDetalleId] = devueltas to motivo
        }
        fun refresh() {
            val r = fResultado!!.selectedItem.toString()
            parcial.visibility = if (r == "parcial") View.VISIBLE else View.GONE
            fMonto!!.isEnabled = r != "fallida"
            if (r == "fallida") fMonto!!.setText("0")
            else if (r == "entregado" && number(fMonto!!.text.toString()) == 0.0) fMonto!!.setText("%.2f".format(d.total))
        }
        fResultado!!.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(p: AdapterView<*>?, v: View?, pos: Int, id: Long) = refresh()
            override fun onNothingSelected(p: AdapterView<*>?) {}
        }
        refresh()
        button("Registrar resultado") { register(d) }
        button("Volver a mis entregas") { resetEvidence(); detalle = null; deliveries(1) }
    }

    private fun register(d: Detalle) {
        saveForm()
        val gps = position
        if (scannedOrder != d.pedidoId) { error("Escanea el QR del pedido ${d.pedidoId}"); return }
        if (gps == null) { error("Obtén el GPS antes de registrar"); return }
        if (photo == null && !entregas.tieneEvidencia(d.id)) { error("Toma la foto de evidencia"); return }
        val monto = number(formMonto); val cambio = number(formCambio)
        if (monto == null || cambio == null) { error("Escribe montos válidos (número con punto decimal)"); return }
        val lineas = d.lineas.map { l -> LineaCierre(l, formDevueltas[l.pedidoDetalleId]?.trim()?.toIntOrNull() ?: 0, formMotivos[l.pedidoDetalleId] ?: "") }
        val datos = DatosCierre(formResultado, monto, cambio, formNota, lineas, Fix(gps.latitude, gps.longitude, gps.accuracy.toDouble(), gps.time))
        try { entregas.validar(d, datos) } catch (e: IllegalArgumentException) { error(e.message ?: "Revisa los datos"); return }
        val evidence = photo
        val points = route.toList()
        work({ entregas.cerrar(d, datos, evidence, points) }) { r ->
            resetEvidence(); detalle = null
            Toast.makeText(this, "Entrega ${if (r.duplicado) "ya registrada" else "registrada"}: ${r.estadoPedido}", Toast.LENGTH_LONG).show()
            deliveries(1)
        }
    }

    // ------------------------------------------------------------------------------------------ cámara, QR y GPS
    private fun capturePhoto() {
        saveForm()
        val d = detalle ?: return
        if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) { requestPermissions(arrayOf(Manifest.permission.CAMERA), 10); status.text = "Concede el permiso y vuelve a pulsar."; return }
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
                try { photo = Fotos.preparar(file) } catch (e: Exception) { error(e.message ?: "No se pudo leer la foto") }
            }
            file?.delete()
            deliveryForm()
        }
    }

    private fun gps() {
        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(arrayOf(Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION), 11)
            status.text = "Concede el permiso y vuelve a pulsar."
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
        status.text = "Esperando señal GPS…"
    }

    private fun resetEvidence() {
        photo = null; photoFile?.delete(); photoFile = null; position = null; scannedOrder = null; route.clear()
        listener?.let { manager?.removeUpdates(it) }; listener = null
        fResultado = null; fMonto = null; fCambio = null; fNota = null; fLineas.clear()
    }

    override fun onDestroy() { alive = false; resetEvidence(); executor.shutdownNow(); super.onDestroy() }
}
