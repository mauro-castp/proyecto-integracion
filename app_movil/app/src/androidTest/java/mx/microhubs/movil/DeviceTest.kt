package mx.microhubs.movil

import android.content.Context
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.CheckBox
import android.widget.EditText
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
 * (el emulador ve el equipo como 10.0.2.2).
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
        val grande = android.graphics.Bitmap.createBitmap(3000, 2000, android.graphics.Bitmap.Config.ARGB_8888).apply { eraseColor(android.graphics.Color.rgb(30, 120, 200)) }
        val archivo = java.io.File(context.cacheDir, "prueba-foto.jpg")
        archivo.outputStream().use { grande.compress(android.graphics.Bitmap.CompressFormat.JPEG, 95, it) }
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

    private fun views(view: View): List<View> = listOf(view) + if (view is ViewGroup) (0 until view.childCount).flatMap { views(view.getChildAt(it)) } else emptyList()
    private fun ActivityScenario<MainActivity>.vistas(): List<View> { var v = emptyList<View>(); onActivity { v = views(it.findViewById(android.R.id.content)) }; return v }
    private fun ActivityScenario<MainActivity>.espera(etiqueta: String, exacto: Boolean = true) {
        repeat(200) {
            if (vistas().any { it is Button && (if (exacto) it.text.toString() == etiqueta else it.text.toString().startsWith(etiqueta)) }) return
            Thread.sleep(50)
        }
        fail("No apareció el botón: $etiqueta")
    }
    private fun ActivityScenario<MainActivity>.pulsa(etiqueta: String, exacto: Boolean = true) {
        espera(etiqueta, exacto)
        onActivity { a -> views(a.findViewById(android.R.id.content)).filterIsInstance<Button>().first { if (exacto) it.text.toString() == etiqueta else it.text.toString().startsWith(etiqueta) }.performClick() }
        Thread.sleep(100); libre()
    }
    /** La app ignora los toques mientras procesa una petición: se espera a que termine antes de seguir. */
    private fun ActivityScenario<MainActivity>.libre() {
        repeat(300) {
            if (vistas().filterIsInstance<TextView>().none { it.text.toString() == "Procesando…" }) return
            Thread.sleep(50)
        }
        fail("La petición no terminó")
    }
    private fun ActivityScenario<MainActivity>.escribe(pista: String, texto: String) {
        onActivity { a -> views(a.findViewById(android.R.id.content)).filterIsInstance<EditText>().first { it.hint.toString().startsWith(pista) }.setText(texto) }
    }
    private fun ActivityScenario<MainActivity>.textos() = vistas().filterIsInstance<TextView>().joinToString("\n") { it.text.toString() }

    /** Guarda lo que muestra la pantalla; Gradle las copia a app/build/outputs/connected_android_test_additional_output/. */
    private fun captura(nombre: String) {
        val imagen = InstrumentationRegistry.getInstrumentation().uiAutomation.takeScreenshot() ?: return
        val dir = (InstrumentationRegistry.getArguments().getString("additionalTestOutputDir")?.let(::File) ?: File(context.getExternalFilesDir(null), "capturas")).apply { mkdirs() }
        File(dir, "$nombre.png").outputStream().use { imagen.compress(android.graphics.Bitmap.CompressFormat.PNG, 100, it) }
    }

    @Test fun recorridoConEjemplosLocalesYSalida() {
        ActivityScenario.launch(MainActivity::class.java).use { s ->
            s.onActivity { a -> views(a.findViewById(android.R.id.content)).filterIsInstance<CheckBox>().first().isChecked = true }
            s.escribe("Correo", "qa@example.com"); s.escribe("Clave", "demo")
            s.pulsa("Entrar")
            s.pulsa("Mis entregas")
            s.pulsa("Parada 1 · PED-DEMO-000101", exacto = false)
            s.espera("Registrar resultado")
            assertTrue(s.textos(), s.textos().contains("Total a cobrar: $158.00"))
            captura("entrega")
            s.onActivity { a -> views(a.findViewById(android.R.id.content)).filterIsInstance<android.widget.Spinner>().first().setSelection(1) }
            Thread.sleep(300)
            s.onActivity { a -> (a.findViewById<View>(android.R.id.content) as ViewGroup).getChildAt(0).let { (it as android.widget.ScrollView).fullScroll(View.FOCUS_DOWN) } }
            Thread.sleep(500); captura("entrega_parcial")
            s.onActivity { a -> views(a.findViewById(android.R.id.content)).filterIsInstance<android.widget.Spinner>().first().setSelection(0) }
            s.pulsa("Registrar resultado")
            assertTrue("debe exigir el QR antes de registrar", s.textos().contains("Escanea el QR del pedido 101"))
            s.pulsa("Volver a mis entregas")
            s.pulsa("Menú")
            s.pulsa("Notificaciones", exacto = false)
            s.pulsa("● Nueva entrega asignada", exacto = false)
            s.pulsa("Menú")
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
            s.pulsa("Mi perfil")
            s.pulsa("Mis entregas")
            s.espera("Menú")
            assertFalse(s.textos(), s.textos().contains("EJEMPLOS LOCALES"))
            s.pulsa("Menú")
            s.pulsa("Notificaciones", exacto = false)
            s.espera("Menú")
            s.pulsa("Menú")
            s.pulsa("Cerrar sesión")
            s.espera("Entrar")
        }
    }
}
