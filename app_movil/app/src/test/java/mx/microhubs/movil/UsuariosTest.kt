package mx.microhubs.movil

import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test

/** Perfil editable: validación previa, solo se envía lo que cambió y la sesión local queda al día. */
class UsuariosTest {
    private val perfil = Usuarios.leer(Ejemplos.json("Perfil.ok"))                   // Ramiro Alanís Lozano · 8114641034
    private fun servidor() = Servidor { p -> if (p.metodo == "PATCH" || p.metodo == "PUT") Salida.ok(Ejemplos.json("Perfil.ok").also { o -> p.json.keys().forEach { k -> o.put(k, p.json.get(k)) } }) else Salida.ok(Ejemplos.json("Perfil.ok")) }

    @Test fun leeElPerfilDelContrato() {
        assertEquals("Ramiro", perfil.nombre); assertEquals("RA", perfil.iniciales); assertEquals("repartidor", perfil.rol)
        assertNull(perfil.microhub); assertEquals("8114641034", perfil.telefono)
    }

    @Test fun soloEnviaLoQueCambio() {
        val s = servidor(); val api = clienteDe(s)
        val nuevo = Usuarios(api).actualizar(perfil, "Ramiro", "Alanís Lozano", "8112345678")
        assertEquals("PUT /api/v1/usuarios/yo", s.ultima().toString())             // la JVM no conoce PATCH: se cae a PUT con el mismo cuerpo parcial
        assertEquals(setOf("telefono"), s.ultima().json.keys().asSequence().toSet())
        assertEquals("8112345678", nuevo.telefono)
    }

    @Test fun conUnClienteQueConocePatchSeUsaPatch() {
        val s = servidor().also { it.permitePatch = true }
        Usuarios(clienteDe(s)).actualizar(perfil, "Ramiro", "Alanís Lozano", "8112345678")
        assertEquals("PATCH /api/v1/usuarios/yo", s.ultima().toString())
    }

    @Test fun recortaEspaciosYAceptaVariosCambios() {
        val s = servidor()
        Usuarios(clienteDe(s)).actualizar(perfil, "  Ramón ", "Alanís Lozano", "8114641034")
        assertEquals("Ramón", s.ultima().json.getString("nombre"))
        assertEquals(1, s.ultima().json.length())
    }

    private fun rechaza(nombre: String, apellidos: String, telefono: String, parte: String) {
        val s = servidor()
        try { Usuarios(clienteDe(s)).actualizar(perfil, nombre, apellidos, telefono); fail("debía rechazar: $parte") } catch (e: IllegalArgumentException) { assertTrue(e.message, e.message!!.contains(parte)) }
        assertTrue("no se debe llamar al servidor", s.peticiones.isEmpty())
    }
    @Test fun validaAntesDeEnviar() {
        rechaza("", "Alanís", "8114641034", "nombre es obligatorio")
        rechaza("Ramiro", "  ", "8114641034", "apellidos son obligatorios")
        rechaza("Ramiro", "Alanís", "123", "10 dígitos")
        rechaza("Ramiro", "Alanís", "81146410ab", "10 dígitos")
        rechaza("Ramiro", "Alanís Lozano", "8114641034", "No hay cambios")
        rechaza("x".repeat(81), "Alanís", "8114641034", "máximo 80")
    }

    @Test fun elErrorDelServicioLlegaConSuCampo() {
        val api = clienteDe(Servidor { Salida(422, cuerpo = """{"error":{"codigo":"VALIDACION","mensaje":"Revisa los datos enviados.","detalles":[{"campo":"telefono","mensaje":"Debe tener 10 dígitos."}],"traza_id":"t"}}""") })
        try { Usuarios(api).actualizar(perfil, "Ramiro", "Alanís Lozano", "8112345678"); fail() } catch (e: ApiError) { assertEquals("Debe tener 10 dígitos.", e.fields["telefono"]) }
    }

    @Test fun laSesionGuardadaConservaElNombreNuevo() {
        val memoria = Memoria(); val api = clienteDe(servidor(), memoria)
        Usuarios(api).actualizar(perfil, "Ramón", "Alanís Lozano", "8114641034")
        assertEquals("Ramón", api.session!!.getJSONObject("usuario").getString("nombre"))
        assertEquals("Ramón", memoria.saved!!.getJSONObject("usuario").getString("nombre"))       // y se guardó cifrada
        assertEquals("rt_8f3b2c71a0d94e5f9b6a1c2d3e4f5a6b", api.session!!.getString("token_renovacion"))
    }

    @Test fun elModoDemoActualizaSinTocarElAlmacenamiento() {
        val memoria = Memoria(); val api = Api(memoria, Servidor()::abrir, "10.0.2.2"); api.demo = true
        api.login("demo@example.com", "x")
        val nuevo = Usuarios(api).actualizar(Usuarios(api).yo(), "Ramón", "Alanís Lozano", "8114641034")
        assertEquals("Ramón", nuevo.nombre); assertNull(memoria.saved)
    }
}
