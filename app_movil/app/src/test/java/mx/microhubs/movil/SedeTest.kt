package mx.microhubs.movil

import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class SedeTest {
    private val sede = Sede.leer(JSONObject("""{"id":1,"clave":"MH-01","nombre":"Microhub San Bernabé Centro","latitud":25.748,"longitud":-100.364,"radio_km":1.5,"estatus":"activo"}"""))

    @Test fun `un domicilio cercano queda dentro de la cobertura`() {
        assertEquals(0.32, sede.distanciaKm(25.749, -100.361), 0.05)
        assertTrue(sede.cobertura(25.749, -100.361).startsWith("Dentro de la cobertura"))
    }

    @Test fun `un domicilio lejano queda fuera`() {
        assertTrue(sede.distanciaKm(25.80, -100.30) > sede.radioKm)
        assertTrue(sede.cobertura(25.80, -100.30).startsWith("Fuera de la cobertura"))
    }

    @Test fun `el mapa apunta al microhub`() {
        assertTrue(sede.destinoMapa.startsWith("geo:25.748,-100.364"))
    }
}
