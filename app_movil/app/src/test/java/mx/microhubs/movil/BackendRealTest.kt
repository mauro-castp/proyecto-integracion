package mx.microhubs.movil

import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Test

/**
 * Recorre el flujo del repartidor contra los microservicios REALES (JWT, Redis, PostgreSQL, MongoDB).
 * Solo corre si se definen las variables de entorno; si no, se omite:
 *
 *   MICROHUBS_BACKEND_HOST=127.0.0.1   MICROHUBS_CLAVE=<clave de las cuentas de demostración>
 *   MICROHUBS_CORREO=repartidor1@codex.mx (opcional)
 *   MICROHUBS_BACKEND_RUTA=:8088/servicios (opcional: probar por una puerta que reparte por nombre, como en la nube)
 *
 * Necesita al menos una entrega en ruta asignada a esa cuenta (se cierra como «entregado»; no se puede repetir con la misma).
 */
class BackendRealTest {
    private val backend = System.getenv("MICROHUBS_BACKEND_HOST")
    private val servidor get() = "http://$backend" + (System.getenv("MICROHUBS_BACKEND_RUTA") ?: "")
    private val clave = System.getenv("MICROHUBS_CLAVE")
    private val correo = System.getenv("MICROHUBS_CORREO") ?: "repartidor1@codex.mx"
    private val jpeg = byteArrayOf(0xFF.toByte(), 0xD8.toByte(), 0xFF.toByte(), 0xE0.toByte(), 0, 16, 74, 70, 73, 70, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0) + ByteArray(256) { it.toByte() }

    @Test fun flujoCompletoDelRepartidor() {
        assumeTrue("Define MICROHUBS_BACKEND_HOST y MICROHUBS_CLAVE para probar contra el backend real", !backend.isNullOrBlank() && !clave.isNullOrBlank())
        val memoria = Memoria()
        val api = Api(memoria, httpHost = backend!!).apply { this.host = servidor }

        // sesión
        api.login(correo, clave!!)
        assertEquals("repartidor", api.session!!.getJSONObject("usuario").getString("rol"))
        assertNotNull(memoria.saved)
        val perfil = api.call("usuarios", "usuarios/yo")
        assertEquals(correo, perfil.getString("correo"))
        try { Api(Memoria(), httpHost = backend!!).apply { this.host = servidor }.login(correo, "clave-incorrecta"); fail() } catch (e: ApiError) { assertEquals(401, e.status); assertTrue(e.message!!.contains("Intento")) }

        // entregas
        val borradores = BorradoresEnMemoria()
        val entregas = Entregas(api, borradores)
        val parada = entregas.mias(1).items.firstOrNull { it.estado == "en_ruta" }
        assumeTrue("No hay entregas en ruta asignadas a $correo: crea una (portal web o servicios/pruebas) y repite", parada != null)
        val detalle = entregas.detalle(parada!!.id)
        assertEquals(parada.pedidoId, detalle.pedidoId); assertTrue(detalle.lineas.isNotEmpty())
        assertEquals("pedido propio visible", detalle.pedidoId, api.call("pedidos", "pedidos/${detalle.pedidoId}").getInt("id"))

        // cierre con evidencia (MongoDB), recorrido GPS e idempotencia
        val fix = Fix(25.7491, -100.3611, 8.5, System.currentTimeMillis() - 2000)
        val recorrido = listOf(fix.copy(tiempoMs = fix.tiempoMs - 120_000), fix.copy(latitud = 25.7495, tiempoMs = fix.tiempoMs - 60_000), fix)
        val datos = DatosCierre("entregado", detalle.total, 0.0, "", emptyList(), fix)
        val primero = entregas.cerrar(detalle, datos, jpeg, recorrido)
        assertEquals(Resultado("entregado", false), primero)
        assertFalse("el éxito borra el borrador", entregas.hayCierrePendiente(detalle.id))

        // un segundo cierre con otro identificador es un conflicto: la entrega ya está cerrada
        assertEquals("cierre ya aplicado con otro UUID", 409, try { entregas.cerrar(detalle, datos, jpeg); 0 } catch (e: ApiError) { e.status })
        assertFalse(entregas.hayCierrePendiente(detalle.id))
        assertFalse(entregas.mias(1).items.any { it.id == detalle.id })        // ya no aparece en «Mis entregas»

        // cerrar sesión: el servidor revoca el acceso y la renovación
        val viejo = JSONObject(api.session.toString())
        api.logout()
        assertNull(api.session); assertNull(memoria.saved)
        val intruso = Api(Memoria(), httpHost = backend!!).apply { this.host = servidor; session = viejo }
        try { intruso.call("usuarios", "usuarios/yo"); fail("la sesión cerrada sigue valiendo") } catch (e: ApiError) { assertEquals(401, e.status) }
    }

    /**
     * Sin red y de vuelta: el cierre y el recorrido se guardan en la cola, y la sincronización sube la foto (documentos) y manda el lote
     * (sincronizacion → entregas y seguimiento). Reenviar la misma operación es «duplicada»; otro cierre de la misma entrega, «conflicto».
     */
    @Test fun elCierreSinRedSeEnviaConLaSincronizacion() {
        assumeTrue("Define MICROHUBS_BACKEND_HOST y MICROHUBS_CLAVE para probar contra el backend real", !backend.isNullOrBlank() && !clave.isNullOrBlank())
        val api = Api(Memoria(), httpHost = backend!!).apply { this.host = servidor }
        api.login(correo, clave!!)
        val base = ColaEnArchivos(java.nio.file.Files.createTempDirectory("cola_sin_red").toFile())
        val vistas = mutableListOf<Operacion>()                          // lo que la sincronización fue guardando (para reenviarlo igual)
        val cola = object : ColaSinRed by base { override fun guardar(op: Operacion) { vistas.add(op); base.guardar(op) } }
        val entregas = Entregas(api, BorradoresEnMemoria(), cola)
        val parada = entregas.mias(1).items.firstOrNull { it.estado == "en_ruta" }
        assumeTrue("No hay otra entrega en ruta para esta prueba", parada != null)
        val detalle = entregas.detalle(parada!!.id)
        val fix = Fix(25.7491, -100.3611, 7.0, System.currentTimeMillis() - 1500)
        val datos = DatosCierre("entregado", detalle.total, 0.0, "", emptyList(), fix)
        val r = entregas.cerrar(detalle, datos, jpeg, listOf(fix.copy(tiempoMs = fix.tiempoMs - 60_000), fix), conRed = false)
        assertTrue(r.enCola); assertEquals(2, cola.todas().size)

        val sync = Sincronizador(api, cola)
        assertEquals(Informe(aplicadas = 2), sync.sincronizar())
        assertTrue(cola.todas().isEmpty())
        assertFalse("ya no aparece en «Mis entregas»", entregas.mias(1).items.any { it.id == detalle.id })

        // reenviar exactamente lo mismo (como si la respuesta del lote se hubiera perdido): duplicada → aplicada, sin repetir nada
        val cierre = vistas.last { it.tipo == Operacion.CIERRE && it.evidenciaId != null }
        cola.guardar(cierre)
        assertEquals("el servicio lo reconoce como el mismo cierre", Informe(aplicadas = 1), sync.sincronizar())
        assertTrue(cola.todas().isEmpty())

        // el mismo uuid con otro contenido (otra evidencia) no es un reintento: el servicio lo rechaza y no se vuelve a mandar
        cola.guardar(cierre.copy(evidenciaId = "0123456789abcdef01234567"))
        assertEquals(Informe(rechazadas = 1), sync.sincronizar())
        assertTrue(cola.todas().single().mensaje!!.contains("uuid"))

        // otro cierre (otro uuid) de la misma entrega ya cerrada: gana el servidor
        cola.borrar(cierre.uuid)
        entregas.cerrar(detalle, datos, jpeg, conRed = false)
        val conflicto = sync.sincronizar()
        assertEquals(1, conflicto.conflictos)
        val op = cola.todas().single()
        assertEquals(Operacion.CONFLICTO, op.estado); assertTrue(op.mensaje!!.isNotBlank())
        sync.descartar(op.uuid)
        api.logout()
    }

    /** La bandeja de avisos del repartidor: la asignación de la entrega deja un aviso. */
    @Test fun losAvisosSeLeenYSeMarcan() {
        assumeTrue("Define MICROHUBS_BACKEND_HOST y MICROHUBS_CLAVE para probar contra el backend real", !backend.isNullOrBlank() && !clave.isNullOrBlank())
        val api = Api(Memoria(), httpHost = backend!!).apply { this.host = servidor }
        api.login(correo, clave!!)
        val avisos = Avisos(api)
        val antes = avisos.noLeidas()
        val bandeja = avisos.bandeja(1)
        assertTrue("hay avisos (las entregas asignadas generan uno)", bandeja.total > 0)
        val pendiente = avisos.bandeja(1, soloNoLeidas = true).items.firstOrNull()
        if (pendiente != null) {
            assertTrue(avisos.marcarLeido(pendiente).leida)
            assertEquals(antes - 1, avisos.noLeidas())
        }
        api.logout()
    }

    /** Edita el teléfono contra el servicio real y lo deja como estaba. */
    @Test fun elPerfilSeActualizaYSeRestaura() {
        assumeTrue("Define MICROHUBS_BACKEND_HOST y MICROHUBS_CLAVE para probar contra el backend real", !backend.isNullOrBlank() && !clave.isNullOrBlank())
        val api = Api(Memoria(), httpHost = backend!!).apply { this.host = servidor }
        api.login(correo, clave!!)
        val usuarios = Usuarios(api)
        val original = usuarios.yo()
        val otro = if (original.telefono == "8112345678") "8119876543" else "8112345678"
        val cambiado = usuarios.actualizar(original, original.nombre, original.apellidos, otro)
        assertEquals(otro, cambiado.telefono); assertEquals(otro, usuarios.yo().telefono)
        try { usuarios.actualizar(cambiado, cambiado.nombre, cambiado.apellidos, "123"); fail() } catch (e: IllegalArgumentException) { assertTrue(e.message!!.contains("10 dígitos")) }
        usuarios.actualizar(cambiado, original.nombre, original.apellidos, original.telefono)
        assertEquals(original.telefono, usuarios.yo().telefono)
        api.logout()
    }

    /** Idempotencia real: mismo UUID y misma evidencia, aunque el primer intento «se perdió» para el cliente. */
    @Test fun elReintentoConElMismoIdentificadorEsDuplicado() {
        assumeTrue("Define MICROHUBS_BACKEND_HOST y MICROHUBS_CLAVE para probar contra el backend real", !backend.isNullOrBlank() && !clave.isNullOrBlank())
        val api = Api(Memoria(), httpHost = backend!!).apply { this.host = servidor }
        api.login(correo, clave!!)
        val b = BorradoresEnMemoria()
        val conservador = object : Borradores by b {                          // simula que la app murió justo antes de borrar el borrador
            override fun borrar(entregaId: Int) {}
        }
        val entregas = Entregas(api, conservador)
        val parada = entregas.mias(1).items.firstOrNull { it.estado == "en_ruta" }
        assumeTrue("No hay una segunda entrega en ruta para esta prueba", parada != null)
        val detalle = entregas.detalle(parada!!.id)
        val datos = DatosCierre("entregado", detalle.total, 0.0, "", emptyList(), Fix(25.7491, -100.3611, 8.0, System.currentTimeMillis() - 1000))
        val primero = entregas.cerrar(detalle, datos, jpeg)
        val reintento = entregas.cerrar(detalle, datos.let { DatosCierre(it.resultado, it.montoCobrado, it.cambio, it.incidencia, it.lineas, it.fix) }, null)
        assertFalse(primero.duplicado); assertTrue("el reintento debe ser duplicado", reintento.duplicado)
        assertEquals(primero.estadoPedido, reintento.estadoPedido)
        api.logout()
    }
}
