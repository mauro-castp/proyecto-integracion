package mx.microhubs.movil

import android.content.Context
import androidx.test.core.app.ActivityScenario
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText

@RunWith(AndroidJUnit4::class)
class DeviceTest {
    private val context: Context get() = ApplicationProvider.getApplicationContext()
    @Test fun tokensCifradosYRestaurados() {
        val store = SessionStore(context); store.clear()
        store.save(JSONObject().put("token_acceso","token-secreto-qa").put("token_renovacion","renovar-qa"))
        val raw = context.getSharedPreferences("session",Context.MODE_PRIVATE).all.toString()
        assertFalse(raw.contains("token-secreto-qa")); assertFalse(raw.contains("renovar-qa"))
        assertEquals("token-secreto-qa",SessionStore(context).load()!!.getString("token_acceso"))
        store.clear(); assertNull(store.load())
    }
    @Test fun datosCorruptosNoRestauranSesion() {
        val prefs = context.getSharedPreferences("session",Context.MODE_PRIVATE)
        prefs.edit().putString("data","no-es-cifrado").putString("iv","invalid").commit()
        assertNull(SessionStore(context).load()); assertTrue(prefs.all.isEmpty())
    }
    @Test fun inicioDeActivity() {
        ActivityScenario.launch(MainActivity::class.java).use { scenario ->
            scenario.onActivity { activity -> assertFalse(activity.isFinishing); assertNotNull(activity.findViewById<android.view.View>(android.R.id.content)) }
        }
    }
    private fun views(view: View): List<View> = listOf(view) + if (view is ViewGroup) (0 until view.childCount).flatMap { views(view.getChildAt(it)) } else emptyList()
    private fun waitButton(scenario: ActivityScenario<MainActivity>, text: String) {
        repeat(100) {
            var found=false
            scenario.onActivity { activity -> found=views(activity.findViewById(android.R.id.content)).any { it is Button && it.text.toString()==text } }
            if (found) return
            Thread.sleep(50)
        }
        fail("No apareció el botón: $text")
    }
    @Test fun loginEntregasPerfilYSalidaEnPantalla() {
        ActivityScenario.launch(MainActivity::class.java).use { scenario ->
            scenario.onActivity { activity ->
                val controls=views(activity.findViewById(android.R.id.content))
                controls.filterIsInstance<EditText>().first { it.hint.toString()=="Correo" }.setText("qa@example.com")
                controls.filterIsInstance<EditText>().first { it.hint.toString()=="Clave" }.setText("demo")
                controls.filterIsInstance<Button>().first { it.text.toString()=="Entrar" }.performClick()
            }
            waitButton(scenario,"Mis entregas")
            scenario.onActivity { activity -> views(activity.findViewById(android.R.id.content)).filterIsInstance<Button>().first { it.text.toString()=="Mis entregas" }.performClick() }
            waitButton(scenario,"Pedido 101 · asignada")
            scenario.onActivity { activity -> views(activity.findViewById(android.R.id.content)).filterIsInstance<Button>().first { it.text.toString()=="Menú" }.performClick() }
            waitButton(scenario,"Cerrar sesión")
            scenario.onActivity { activity -> views(activity.findViewById(android.R.id.content)).filterIsInstance<Button>().first { it.text.toString()=="Cerrar sesión" }.performClick() }
            waitButton(scenario,"Entrar")
        }
    }
}
