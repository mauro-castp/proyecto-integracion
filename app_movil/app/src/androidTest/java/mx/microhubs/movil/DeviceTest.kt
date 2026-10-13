package mx.microhubs.movil

import android.content.Context
import android.graphics.Bitmap
import android.view.View
import android.view.ViewGroup
import android.widget.CheckBox
import android.widget.EditText
import android.widget.ProgressBar
import android.widget.ScrollView
import android.widget.TextView
import androidx.test.core.app.ActivityScenario
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File

/**
 * Pruebas en emulador o teléfono: cifrado de la sesión con Android Keystore, arranque y recorrido de pantallas.
 * `recorridoContraElBackendReal` solo corre si se pasa la clave:  -Pandroid.testInstrumentationRunnerArguments.clave=...
 * (el emulador ve el equipo como 10.0.2.2). Las capturas de cada pantalla quedan en
 * app/build/outputs/connected_android_test_additional_output/.
 */
@RunWith(AndroidJUnit4::class)
class DeviceTest {
    private val context: Context get() = ApplicationProvider.getApplicationContext()

    @Test fun tokensCifradosYRestaurados() {
        val store = SessionStore(context); store.clear()
        store.save(JSONObject().put("token_acceso", "token-secreto-qa").put("token_renovacion", "renovar-qa"))
        val raw = context.getSharedPreferences("session", Context.MODE_PRIVATE).all.toString()
        assertFalse(raw.contains("token-secreto-qa")); assertFalse(raw.contains("renovar-qa"))
        assertEquals("token-secreto-qa", SessionStore(context).load()!!.getString("token_acceso"))
        store.clear(); assertNull(store.load())
    }

    @Test fun datosCorruptosNoRestauranSesion() {
        val prefs = context.getSharedPreferences("session", Context.MODE_PRIVATE)
        prefs.edit().putString("data", "no-es-cifrado").putString("iv", "invalid").commit()
        assertNull(SessionStore(context).load()); assertTrue(prefs.all.isEmpty())
    }

    @Test fun elCierrePendienteSobreviveAlReinicioDeLaApp() {
        val a = PrefsBorradores(context); a.borrar(777)
        a.guardar(777, Borrador("9b2d1c3e-0a4f-4c8e-8d1b-5e6f7a8b9c0d", "665f1c2e8a3b4d0012a7c9e1"))
        val b = PrefsBorradores(context).cargar(777)!!
        assertEquals("9b2d1c3e-0a4f-4c8e-8d1b-5e6f7a8b9c0d", b.idClienteLocal); assertEquals("665f1c2e8a3b4d0012a7c9e1", b.evidenciaId)
        a.borrar(777); assertNull(PrefsBorradores(context).cargar(777))
    }

    @Test fun laFotoSeReduceYCabeEnElLimiteDelServicio() {
        val grande = Bitmap.createBitmap(3000, 2000, Bitmap.Config.ARGB_8888).apply { eraseColor(android.graphics.Color.rgb(30, 120, 200)) }
        val archivo = File(context.cacheDir, "prueba-foto.jpg")
        archivo.outputStream().use { grande.compress(Bitmap.CompressFormat.JPEG, 95, it) }
        val bytes = Fotos.preparar(archivo)
        archivo.delete()
        assertTrue(bytes.size in 1..Fotos.MAXIMO_BYTES)
        assertEquals(0xFF.toByte(), bytes[0]); assertEquals(0xD8.toByte(), bytes[1])           // sigue siendo JPEG (el servicio verifica la firma)
        val salida = android.graphics.BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
        assertEquals(1600, maxOf(salida.width, salida.height))
    }

    @Test fun inicioDeActivity() {
        ActivityScenario.launch(MainActivity::class.java).use { scenario ->
            scenario.onActivity { activity -> assertFalse(activity.isFinishing); assertNotNull(activity.findViewById<View>(android.R.id.content)) }
        }
    }

    // ------------------------------------------------------------------------------------------ ayudas de pantalla
    private fun views(view: View): List<View> = listOf(view) + if (view is ViewGroup) (0 until view.childCount).flatMap { views(view.getChildAt(it)) } else emptyList()
    private fun ActivityScenario<MainActivity>.vistas(): List<View> { var v = emptyList<View>(); onActivity { v = views(it.findViewById(android.R.id.content)) }; return v }
    private fun textoDe(v: View): String = when (v) {
        is TextView -> v.text.toString()
        is ViewGroup -> (0 until v.childCount).joinToString(" ") { textoDe(v.getChildAt(it)) }
        else -> ""
    }
    private fun coincide(texto: String, etiqueta: String, exacto: Boolean) = if (exacto) texto.trim() == etiqueta else texto.contains(etiqueta)
    /** Botones y tarjetas tocables que muestran esa etiqueta. */
    private fun ActivityScenario<MainActivity>.tocables(etiqueta: String, exacto: Boolean) =
        vistas().filter { it.hasOnClickListeners() && it.isShown && coincide(textoDe(it), etiqueta, exacto) }

    private fun ActivityScenario<MainActivity>.espera(etiqueta: String, exacto: Boolean = true) {
        repeat(200) { if (tocables(etiqueta, exacto).isNotEmpty()) return; Thread.sleep(50) }
        fail("No apareció: $etiqueta")
    }
    /** La app ignora los toques mientras procesa una petición: se espera a que termine (barra de progreso oculta). */
    private fun ActivityScenario<MainActivity>.libre() {
        repeat(300) { if (vistas().filterIsInstance<ProgressBar>().none { it.visibility == View.VISIBLE }) return; Thread.sleep(50) }
        fail("La petición no terminó")
    }
    private fun ActivityScenario<MainActivity>.pulsa(etiqueta: String, exacto: Boolean = true) {
        espera(etiqueta, exacto)
        var destino: View? = null
        onActivity { a -> destino = views(a.findViewById(android.R.id.content)).first { it.hasOnClickListeners() && it.isShown && coincide(textoDe(it), etiqueta, exacto) } }
        onActivity { destino!!.performClick() }
        Thread.sleep(100); libre()
    }
    private fun ActivityScenario<MainActivity>.volver() {
        var flecha: View? = null
        onActivity { a -> flecha = views(a.findViewById(android.R.id.content)).first { it.contentDescription == "Volver" } }
        onActivity { flecha!!.performClick() }
        Thread.sleep(100); libre()
    }
    private fun ActivityScenario<MainActivity>.escribe(pista: String, texto: String) {
        onActivity { a -> views(a.findViewById(android.R.id.content)).filterIsInstance<EditText>().first { it.hint.toString().startsWith(pista) }.setText(texto) }
    }
    private fun ActivityScenario<MainActivity>.textos() = vistas().filterIsInstance<TextView>().joinToString("\n") { it.text.toString() }
    private fun ActivityScenario<MainActivity>.desplazaAlFinal() {
        onActivity { a -> views(a.findViewById(android.R.id.content)).filterIsInstance<ScrollView>().first().fullScroll(View.FOCUS_DOWN) }
        Thread.sleep(400)
    }

    /** Guarda lo que muestra la pantalla; Gradle las copia a app/build/outputs/connected_android_test_additional_output/. */
    private fun captura(nombre: String) {
        Thread.sleep(300)
        val imagen = InstrumentationRegistry.getInstrumentation().uiAutomation.takeScreenshot() ?: return
        val dir = (InstrumentationRegistry.getArguments().getString("additionalTestOutputDir")?.let(::File) ?: File(context.getExternalFilesDir(null), "capturas")).apply { mkdirs() }
        File(dir, "$nombre.png").outputStream().use { imagen.compress(Bitmap.CompressFormat.PNG, 100, it) }
    }

    // ------------------------------------------------------------------------------------------ recorridos
    @Test fun recorridoConEjemplosLocalesYSalida() {
        ActivityScenario.launch(MainActivity::class.java).use { s ->
            captura("01_acceso")
            s.onActivity { a -> views(a.findViewById(android.R.id.content)).filterIsInstance<CheckBox>().first().isChecked = true }
            s.escribe("Correo", "qa@example.com"); s.escribe("Clave", "demo")
            s.pulsa("Entrar")
            s.espera("Mis entregas", exacto = false); captura("02_inicio")
            assertTrue(s.textos(), s.textos().contains("Ejemplos locales"))      // el indicador de conexión lo dice en la barra

            s.pulsa("Mis entregas", exacto = false)
            s.espera("PED-DEMO-000101", exacto = false); captura("03_entregas")
            s.pulsa("PED-DEMO-000101", exacto = false)
            s.espera("Registrar resultado")
            assertTrue(s.textos(), s.textos().contains("Total a cobrar") && s.textos().contains("$158.00"))
            captura("04_entrega")
            s.pulsa("Parcial")
            assertTrue("el modo parcial muestra las líneas", s.textos().contains("Líneas del pedido") && s.textos().contains("Agua purificada"))
            s.desplazaAlFinal(); captura("05_entrega_parcial")
            s.pulsa("Entregado")
            s.pulsa("Registrar resultado")
            assertTrue("debe exigir el QR antes de registrar", s.textos().contains("Escanea el QR del pedido 101"))
            captura("06_error_qr")
            s.volver(); s.espera("PED-DEMO-000101", exacto = false)
            s.volver(); s.espera("Mi perfil", exacto = false)

            s.pulsa("Mi perfil", exacto = false)
            s.espera("Guardar cambios"); captura("08_perfil")
            s.escribe("Teléfono", "8112345678")
            s.pulsa("Guardar cambios")
            assertTrue("el perfil se actualiza", s.textos().contains("Perfil actualizado"))
            s.escribe("Teléfono", "123")
            s.pulsa("Guardar cambios")
            assertTrue("rechaza un teléfono inválido", s.textos().contains("10 dígitos"))
            s.volver(); s.espera("Cerrar sesión")
            s.pulsa("Cerrar sesión")
            s.espera("Entrar")
        }
    }

    @Test fun recorridoContraElBackendReal() {
        val clave = InstrumentationRegistry.getArguments().getString("clave")
        assumeTrue("Pasa -Pandroid.testInstrumentationRunnerArguments.clave=... para probar contra el backend real", !clave.isNullOrBlank())
        ActivityScenario.launch(MainActivity::class.java).use { s ->
            s.escribe("Correo", "repartidor1@codex.mx"); s.escribe("Clave", clave!!)
            s.pulsa("Entrar")
            s.espera("Mis entregas", exacto = false)
            assertFalse(s.textos(), s.textos().contains("Ejemplos locales"))
            captura("10_inicio_real")
            s.pulsa("Mi perfil", exacto = false); s.espera("Guardar cambios"); captura("11_perfil_real"); s.volver()
            s.pulsa("Mis entregas", exacto = false)
            captura("12_entregas_real"); s.volver()
            s.pulsa("Cerrar sesión")
            s.espera("Entrar")
        }
    }
}
