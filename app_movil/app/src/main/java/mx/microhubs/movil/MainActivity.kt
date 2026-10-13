package mx.microhubs.movil

import android.Manifest
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.Bundle
import android.provider.MediaStore
import android.util.Base64
import android.widget.*
import com.google.zxing.integration.android.IntentIntegrator
import org.json.JSONObject
import java.io.ByteArrayOutputStream
import java.util.concurrent.Executors

class MainActivity : Activity() {
    private lateinit var api: Api
    private lateinit var layout: LinearLayout
    private lateinit var status: TextView
    private val executor = Executors.newSingleThreadExecutor()
    private var busy = false
    private var deliveryId = 0
    private var orderId = 0
    private var scannedOrder: Int? = null
    private var photo: String? = null
    private var position: Location? = null
    private var listener: LocationListener? = null
    private var manager: LocationManager? = null
    private var alive = true
    override fun onCreate(state: Bundle?) { super.onCreate(state); api = Api(SessionStore(this)); loginScreen() }
    private fun screen(title: String) {
        layout = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(24, 48, 24, 24) }
        val scroll = ScrollView(this).apply { addView(layout) }; setContentView(scroll)
        layout.addView(TextView(this).apply { text = title; textSize = 24f })
        status = TextView(this).apply { text = connectionLabel() }; layout.addView(status)
    }
    private fun connectionLabel(): String {
        if (api.demo) return "EJEMPLOS LOCALES · sin conexión al backend"
        val cm = getSystemService(ConnectivityManager::class.java)
        return if (cm.getNetworkCapabilities(cm.activeNetwork)?.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED) == true) "Red disponible" else "Sin conexión"
    }
    override fun onResume() { super.onResume(); if (::status.isInitialized) status.text = connectionLabel() }
    private fun field(hint: String, secret: Boolean = false): EditText = EditText(this).apply {
        this.hint = hint
        if (secret) inputType = 129
        this@MainActivity.layout.addView(this)
    }
    private fun button(label: String, action: () -> Unit) { layout.addView(Button(this).apply { text = label; setOnClickListener { if (!busy) action() } }) }
    private fun error(message: String) { status.text = message; Toast.makeText(this, message, Toast.LENGTH_LONG).show() }
    private fun <T> work(task: () -> T, done: (T) -> Unit) {
        if (busy) return
        busy = true; status.text = "Procesando…"
        executor.execute {
            try { val result = task(); runOnUiThread { if (alive) { busy = false; status.text = connectionLabel(); done(result) } } }
            catch (e: Exception) { runOnUiThread { if (alive) { busy = false; if (api.session == null) loginScreen(); error(e.message ?: "Error de conexión") } } }
        }
    }
    private fun loginScreen() {
        screen("Microhubs · Acceso")
        val host = field("Host HTTPS").apply { setText(api.host) }
        val demo = CheckBox(this).apply { text = "Usar ejemplos locales"; isChecked = api.demo }; layout.addView(demo)
        val email = field("Correo")
        val password = field("Clave", true)
        button("Entrar") {
            if (!android.util.Patterns.EMAIL_ADDRESS.matcher(email.text.toString()).matches() || password.text.isEmpty()) { error("Ingresa correo válido y clave"); return@button }
            val mail = email.text.toString().trim(); val pass = password.text.toString()
            api.demo = demo.isChecked; api.host = host.text.toString().trim()
            work({ api.login(mail, pass) }) { password.text.clear(); home() }
        }
        button("Restaurar sesión segura") {
            api.demo = demo.isChecked; api.host = host.text.toString().trim()
            if (api.demo) { error("La sesión demo no se guarda"); return@button }
            work({ api.restore(); require(api.session != null) { "No hay sesión guardada" }; api.call("usuarios", "usuarios/yo") }) { home() }
        }
    }
    private fun home() {
        screen("Microhubs · ${api.session!!.getJSONObject("usuario").getString("rol")}")
        button("Mi perfil") { work({ api.call("usuarios", "usuarios/yo") }) { result -> android.app.AlertDialog.Builder(this).setTitle("Perfil").setMessage(result.toString(2)).setPositiveButton("Cerrar", null).show() } }
        val role = api.session!!.getJSONObject("usuario").getString("rol")
        if (role in listOf("repartidor", "administrador")) button("Mis entregas") { deliveries(1) }
        button("Cerrar sesión") {
            work({ try { api.call("auth", "auth/salir", "POST", JSONObject().put("token_renovacion", api.session!!.getString("token_renovacion"))) } finally { api.clear() } }) { resetEvidence(); loginScreen() }
        }
    }
    private fun deliveries(page: Int) {
        work({ api.call("entregas", "entregas?pagina=$page&por_pagina=20") }) { response ->
            screen("Mis entregas · página $page")
            val data = response.getJSONArray("datos")
            for (i in 0 until data.length()) {
                val item = data.getJSONObject(i)
                button("Pedido ${item.getInt("pedido_id")} · ${item.getString("estado")}") {
                    resetEvidence(); deliveryId = item.getInt("id"); orderId = item.getInt("pedido_id"); deliveryForm()
                }
            }
            if (page > 1) button("Anterior") { deliveries(page - 1) }
            if (page < response.getJSONObject("paginacion").getInt("paginas")) button("Siguiente") { deliveries(page + 1) }
            button("Menú") { home() }
        }
    }
    private fun deliveryForm() {
        screen("Entrega $deliveryId · pedido $orderId")
        layout.addView(TextView(this).apply { text = "QR: ${scannedOrder ?: "pendiente"}\nFoto: ${if (photo == null) "pendiente" else "capturada"}\nGPS: ${position?.let { "${it.latitude}, ${it.longitude}" } ?: "pendiente"}" })
        button("Consultar pedido") { work({ api.call("pedidos", "pedidos/$orderId") }) { android.app.AlertDialog.Builder(this).setMessage(it.toString(2)).setPositiveButton("Cerrar", null).show() } }
        button("Escanear QR") {
            if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) { requestPermissions(arrayOf(Manifest.permission.CAMERA), 10); return@button }
            IntentIntegrator(this).setDesiredBarcodeFormats(IntentIntegrator.QR_CODE).setPrompt("Escanea el ID numérico del pedido").setBeepEnabled(false).initiateScan()
        }
        button("Foto de evidencia") {
            if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) { requestPermissions(arrayOf(Manifest.permission.CAMERA), 10); return@button }
            try { startActivityForResult(Intent(MediaStore.ACTION_IMAGE_CAPTURE), 20) } catch (_: Exception) { error("No hay aplicación de cámara disponible") }
        }
        button("Obtener GPS") { gps() }
        val results = Spinner(this).apply { adapter = ArrayAdapter(this@MainActivity, android.R.layout.simple_spinner_dropdown_item, listOf("entregado", "parcial", "fallido")) }; layout.addView(results)
        val note = field("Observaciones (obligatorias para parcial/fallido)")
        button("Registrar resultado") {
            val result = results.selectedItem.toString(); val observations = note.text.toString().trim()
            val gps = position
            if (scannedOrder != orderId || photo == null || gps == null) { error("Completa QR del pedido, foto y GPS"); return@button }
            if (System.currentTimeMillis() - gps.time > 120000) { error("Actualiza la posición GPS"); return@button }
            if (result != "entregado" && observations.isBlank()) { error("Describe el resultado de la entrega"); return@button }
            val evidence = photo!!
            work({
                val document = api.call("documentos", "documentos", "POST", JSONObject().put("nombre", "entrega-$deliveryId.jpg").put("tipo", "image/jpeg").put("contenido_base64", evidence))
                api.call("entregas", "entregas/$deliveryId", "PUT", JSONObject().put("resultado", result).put("pedido_id", orderId).put("observaciones", observations)
                    .put("evidencia_id", document.get("id")).put("gps", JSONObject().put("latitud", gps.latitude).put("longitud", gps.longitude).put("precision_m", gps.accuracy).put("capturada_en", java.time.Instant.ofEpochMilli(gps.time).toString())))
            }) { resetEvidence(); home(); Toast.makeText(this, "Entrega registrada", Toast.LENGTH_LONG).show() }
        }
        button("Volver") { resetEvidence(); home() }
    }
    @Suppress("DEPRECATION")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        val scan = IntentIntegrator.parseActivityResult(requestCode, resultCode, data)
        if (scan != null) {
            if (scan.contents != null) { scannedOrder = scan.contents.toIntOrNull(); deliveryForm(); if (scannedOrder != orderId) error("El QR no corresponde al pedido") }
            return
        }
        if (requestCode == 20 && resultCode == RESULT_OK) {
            val bitmap = data?.extras?.get("data") as? Bitmap
            if (bitmap == null) { error("La cámara no devolvió una imagen"); return }
            val bytes = ByteArrayOutputStream(); bitmap.compress(Bitmap.CompressFormat.JPEG, 85, bytes)
            photo = Base64.encodeToString(bytes.toByteArray(), Base64.NO_WRAP); deliveryForm()
        }
    }
    private fun gps() {
        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) { requestPermissions(arrayOf(Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION), 11); return }
        manager = getSystemService(LocationManager::class.java)
        if (manager?.isProviderEnabled(LocationManager.GPS_PROVIDER) != true) { error("Activa el GPS del dispositivo"); return }
        listener?.let { manager?.removeUpdates(it) }
        listener = object : LocationListener {
            override fun onLocationChanged(location: Location) { position = location; manager?.removeUpdates(this); listener = null; deliveryForm() }
            override fun onProviderEnabled(provider: String) {}
            override fun onProviderDisabled(provider: String) { error("GPS desactivado") }
            @Deprecated("API anterior") override fun onStatusChanged(provider: String?, status: Int, extras: Bundle?) {}
        }
        manager!!.requestLocationUpdates(LocationManager.GPS_PROVIDER, 1000, 0f, listener!!)
        status.text = "Esperando señal GPS…"
    }
    private fun resetEvidence() { photo = null; position = null; scannedOrder = null; listener?.let { manager?.removeUpdates(it) }; listener = null }
    override fun onDestroy() { alive = false; resetEvidence(); executor.shutdownNow(); super.onDestroy() }
}
