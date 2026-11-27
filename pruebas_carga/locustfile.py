"""
locustfile.py — Pruebas de carga de la Plataforma de Microhubs (Tercer Parcial).

Seis perfiles que corresponden a quienes usan el sistema de verdad:

  Perfil (clase)            Peso  Quién y desde dónde                         Qué hace
  ClienteConsultando         40   cliente en el web o la app                  catálogo con búsqueda, detalle, zonas, sus pedidos, sus avisos
  RepartidorAndroid          20   repartidor con la app Android (JSON)        sus entregas, detalle, envía GPS en lotes de 10 puntos
  OperadorRegistrando        15   operador de microhub                        inventario, alertas, pide reposición (solicitud de compra)
  PlaneadorEscritorio        10   planeador con la app de escritorio (XML)    reportes en XML, punto de equilibrio, simulación Monte Carlo
  AdministradorPanel         10   administrador mirando el panel              estado y disponibilidad del monitoreo, bitácora
  ProcesoAutomatico           5   app que vuelve a tener red                  lotes de sincronización (GPS hecho sin conexión), reenvío idempotente

Dónde pega:
  · Local (puertos por servicio):   MICROHUBS_PLANTILLA="http://localhost:{puerto}"            (valor por omisión)
  · Nube (Nginx con prefijo):      MICROHUBS_PLANTILLA="https://34-51-89-253.sslip.io/servicios/{servicio}"
El parámetro --host de Locust no se usa (cada servicio tiene su URL); hay que pasarlo igual, por ejemplo --host http://localhost.

Cuentas: MICROHUBS_CLAVE (la de las cuentas de demostración; en la nube es la del .env de la VM). Los clientes son los sintéticos de
bloque_c/scripts/generar_volumen.py (vol.000001…vol.005000@sintetico.microhubs.mx); sin ellos se usan los clientes de la semilla.
Los repartidores necesitan entregas en ruta hoy: servicios/pruebas/preparar_entregas.py --correo repartidor1@codex.mx --cantidad 6.

Ejemplos (ver pruebas_carga/LEEME.md):
  locust -f pruebas_carga/locustfile.py --headless -u 50 -r 5 -t 3m --host http://localhost --csv evidencias/carga/normal
  locust -f pruebas_carga/locustfile.py --headless --host http://localhost --csv evidencias/carga/estres  (con FORMA=escalones)

Con FORMA=escalones la carga sube por escalones hasta romper y luego baja (prueba de estrés y de recuperación); ver EscalonesYRecuperacion.
"""
import datetime as dt
import os
import random
import time
import uuid

from locust import HttpUser, LoadTestShape, between, events, task

PLANTILLA = os.environ.get("MICROHUBS_PLANTILLA", "http://localhost:{puerto}")
CLAVE = os.environ.get("MICROHUBS_CLAVE", "Codex#2026")
CLIENTES_SINTETICOS = int(os.environ.get("CLIENTES_SINTETICOS", "5000"))
PUERTOS = {"auth": 5101, "usuarios": 5102, "productos": 5103, "pedidos": 5104, "entregas": 5105, "zonas": 5108, "microhubs": 5109,
           "seguimiento": 5110, "inventario": 5111, "abastecimiento": 5114, "punto-equilibrio": 5120, "simulacion": 5121,
           "reportes": 5123, "notificaciones": 5124, "sincronizacion": 5125, "auditoria-monitoreo": 5126}
BUSQUEDAS = ["arroz", "frijol", "leche", "aceite", "huevo", "azucar", "cafe", "jabon", "papel", "atun", "a", "pan"]
ZONA = dt.timezone(dt.timedelta(hours=-6))


def url(servicio, ruta):
    return PLANTILLA.format(servicio=servicio, puerto=PUERTOS[servicio]) + "/api/v1/" + ruta


def hace(segundos):
    return (dt.datetime.now(ZONA) - dt.timedelta(seconds=segundos)).isoformat(timespec="seconds")


class Base(HttpUser):
    abstract = True
    correo = None
    xml = False

    def on_start(self):
        self.token = None
        self.ultimo_intento = 0.0
        self.entrar()

    def cabeceras(self, xml=None):
        h = {"Accept": "application/xml" if (self.xml if xml is None else xml) else "application/json"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def entrar(self):
        self.ultimo_intento = time.time()
        correo = self.elegir_correo()
        with self.client.post(url("auth", "auth/login"), json={"correo": correo, "clave": CLAVE}, name="auth · POST login",
                              headers={"Accept": "application/json"}, catch_response=True) as r:
            if r.status_code == 200:
                self.token = r.json()["token_acceso"]
                self.refresh = r.json().get("token_renovacion")
                r.success()
            else:
                r.failure(f"login {correo}: HTTP {r.status_code}")

    def elegir_correo(self):
        return self.correo

    def pedir(self, metodo, servicio, ruta, nombre, cuerpo=None, xml=None, esperado=(200,)):
        if not self.token:
            # Sin sesión (p. ej. el login respondió 429): se reintenta como lo haría la app, respetando un minuto de espera.
            if time.time() - self.ultimo_intento >= 60:
                self.entrar()
            return None
        kw = {"headers": self.cabeceras(xml), "name": nombre, "catch_response": True}
        if cuerpo is not None:
            kw["json"] = cuerpo
        with self.client.request(metodo, url(servicio, ruta), **kw) as r:
            if r.status_code == 401:                    # el token de acceso dura 15 min: se vuelve a entrar como lo haría la app
                r.success()
                self.entrar()
                return None
            if r.status_code in esperado:
                r.success()
                return r
            r.failure(f"HTTP {r.status_code}")
            return None


# ------------------------------------------------------------------------------------------------------------------------------
class ClienteConsultando(Base):
    weight = 40
    wait_time = between(1, 4)

    def elegir_correo(self):
        return f"vol.{random.randint(1, CLIENTES_SINTETICOS):06d}@sintetico.microhubs.mx"

    @task(6)
    def buscar(self):
        self.pedir("GET", "productos", f"productos?q={random.choice(BUSQUEDAS)}&pagina=1&por_pagina=20", "productos · GET buscar")

    @task(3)
    def detalle(self):
        self.pedir("GET", "productos", f"productos/{random.randint(1, 51)}", "productos · GET {id}")

    @task(1)
    def zonas(self):
        self.pedir("GET", "zonas", "zonas", "zonas · GET lista")

    @task(1)
    def microhubs(self):
        self.pedir("GET", "microhubs", "microhubs?estatus=activo", "microhubs · GET lista")

    @task(2)
    def mis_pedidos(self):
        r = self.pedir("GET", "pedidos", "pedidos?pagina=1&por_pagina=10", "pedidos · GET mis pedidos")
        if r is not None and r.json().get("datos"):
            pid = random.choice(r.json()["datos"])["id"]
            self.pedir("GET", "pedidos", f"pedidos/{pid}", "pedidos · GET {id}")

    @task(1)
    def avisos(self):
        self.pedir("GET", "notificaciones", "notificaciones/conteo", "notificaciones · GET conteo")


class RepartidorAndroid(Base):
    weight = 20
    wait_time = between(2, 5)

    def elegir_correo(self):
        return random.choice(["repartidor1@codex.mx", "repartidor2@codex.mx"])

    def on_start(self):
        super().on_start()
        self.entregas = []
        self.actualizar()

    def actualizar(self):
        r = self.pedir("GET", "entregas", "entregas/mias?pagina=1&por_pagina=20", "entregas · GET mias")
        if r is not None:
            self.entregas = [e["id"] for e in r.json().get("datos", [])]

    @task(3)
    def mis_entregas(self):
        self.actualizar()

    @task(2)
    def detalle(self):
        if self.entregas:
            self.pedir("GET", "entregas", f"entregas/{random.choice(self.entregas)}", "entregas · GET {id}")

    @task(5)
    def gps(self):
        if not self.entregas:
            return
        eid = random.choice(self.entregas)
        puntos = [{"latitud": round(25.748 + random.uniform(-0.01, 0.01), 6), "longitud": round(-100.364 + random.uniform(-0.01, 0.01), 6),
                   "precision_m": random.randint(4, 20), "capturado_en": hace(30 * (10 - i))} for i in range(10)]
        self.pedir("POST", "seguimiento", f"seguimiento/{eid}/ubicaciones", "seguimiento · POST ubicaciones (10)", {"puntos": puntos},
                   esperado=(201,))

    @task(1)
    def perfil(self):
        self.pedir("GET", "usuarios", "usuarios/yo", "usuarios · GET yo")


class OperadorRegistrando(Base):
    weight = 15
    wait_time = between(2, 6)
    correo = "operador.mh01@codex.mx"

    @task(4)
    def inventario(self):
        self.pedir("GET", "inventario", "inventario?microhub_id=1&pagina=1&por_pagina=50", "inventario · GET lista")

    @task(2)
    def alertas(self):
        self.pedir("GET", "inventario", "inventario/alertas?microhub_id=1", "inventario · GET alertas")

    @task(2)
    def pedidos_hub(self):
        self.pedir("GET", "pedidos", "pedidos?estado=asignado&pagina=1&por_pagina=20", "pedidos · GET del microhub")

    @task(1)
    def solicitar(self):
        cuerpo = {"microhub_id": 1, "motivo": "Prueba de carga (Locust)",
                  "lineas": [{"producto_id": random.randint(1, 51), "cantidad": random.randint(1, 24)}]}
        self.pedir("POST", "abastecimiento", "abastecimiento/solicitudes", "abastecimiento · POST solicitud", cuerpo, esperado=(201,))


class PlaneadorEscritorio(Base):
    """La app de escritorio habla solo XML: las consultas piden application/xml (el cálculo se manda en JSON para no
    duplicar aquí el armado del XML; la validación XML de entrada la cubren las pruebas de contrato)."""
    weight = 10
    wait_time = between(3, 8)
    correo = "planeador@codex.mx"
    xml = True

    @task(3)
    def reporte_dia(self):
        hoy = dt.date.today()
        self.pedir("GET", "reportes", f"reportes/pedidos_por_dia?desde={hoy - dt.timedelta(days=30)}&hasta={hoy}", "reportes · GET pedidos_por_dia (XML)")

    @task(2)
    def reporte_ventas(self):
        self.pedir("GET", "reportes", "reportes/ventas_por_producto", "reportes · GET ventas_por_producto (XML)")

    @task(2)
    def equilibrio(self):
        cuerpo = {"nombre": "Locust", "pedidos_dia": random.randint(30, 200), "ticket": 135, "margen_bruto": 0.28, "costos_fijos": 60000,
                  "costo_variable_pedido": 32.6, "guardar": False}
        self.pedir("POST", "punto-equilibrio", "punto-equilibrio/calculos", "punto-equilibrio · POST calculo", cuerpo, xml=False,
                   esperado=(200, 201))

    @task(1)
    def simulacion(self):
        cuerpo = {"nombre": "Locust", "microhub_id": 1, "dias": 30, "replicas": 50, "semilla": random.randint(1, 10 ** 6), "ausentismo": 0.05}
        self.pedir("POST", "simulacion", "simulacion/ejecuciones", "simulacion · POST ejecucion (202)", cuerpo, xml=False, esperado=(202,))


class AdministradorPanel(Base):
    weight = 10
    wait_time = between(3, 8)
    correo = "admin@codex.mx"

    @task(3)
    def estado(self):
        self.pedir("GET", "auditoria-monitoreo", "monitoreo/estado", "monitoreo · GET estado")

    @task(1)
    def disponibilidad(self):
        self.pedir("GET", "auditoria-monitoreo", "monitoreo/disponibilidad", "monitoreo · GET disponibilidad")

    @task(2)
    def bitacora(self):
        self.pedir("GET", "auditoria-monitoreo", "auditoria?pagina=1&por_pagina=20", "auditoria · GET bitácora")


class ProcesoAutomatico(Base):
    """Una app que estuvo sin red y manda lo pendiente; la mitad de las veces reenvía el mismo lote (no debe duplicar)."""
    weight = 5
    wait_time = between(5, 10)
    correo = "repartidor2@codex.mx"

    def on_start(self):
        super().on_start()
        self.ultimo = None
        r = self.pedir("GET", "entregas", "entregas/mias?pagina=1&por_pagina=20", "entregas · GET mias")
        self.entregas = [e["id"] for e in r.json().get("datos", [])] if r is not None else []

    @task
    def sincronizar(self):
        if not self.entregas:
            return
        if self.ultimo and random.random() < 0.5:
            self.pedir("POST", "sincronizacion", "sincronizacion/lotes", "sincronizacion · POST lote (reenvío)", self.ultimo, esperado=(200, 201))
            return
        eid = random.choice(self.entregas)
        ops = [{"operacion_uuid": str(uuid.uuid4()), "tipo": "ubicaciones", "creada_en": hace(120 - 20 * i),
                "datos": {"entrega_id": eid, "puntos": [{"latitud": 25.749, "longitud": -100.361, "capturado_en": hace(120 - 20 * i)}]}}
               for i in range(5)]
        self.ultimo = {"lote_uuid": str(uuid.uuid4()), "dispositivo": f"locust-{id(self)}", "cliente": "android", "operaciones": ops}
        self.pedir("POST", "sincronizacion", "sincronizacion/lotes", "sincronizacion · POST lote", self.ultimo, esperado=(201,))


# ------------------------------------------------------------------------------------------------------------------------------
# Locust usa una forma de carga en cuanto existe la clase: por eso solo se define con FORMA=escalones.
if os.environ.get("FORMA") == "escalones":
    class EscalonesYRecuperacion(LoadTestShape):
        """Solo si FORMA=escalones. Sube de 25 en 25 usuarios cada ESCALON_S segundos hasta MAX_USUARIOS (estrés),
        se queda arriba un escalón y luego baja a 25 usuarios para ver cuánto tarda en recuperarse (recuperación)."""
        escalon = int(os.environ.get("ESCALON_S", "60"))
        maximo = int(os.environ.get("MAX_USUARIOS", "300"))
        paso = int(os.environ.get("PASO_USUARIOS", "25"))

        def tick(self):
            t = self.get_run_time()
            subidas = self.maximo // self.paso
            n = int(t // self.escalon)
            if n < subidas:
                return (self.paso * (n + 1), 10)
            if n == subidas:
                return (self.maximo, 10)
            if n <= subidas + 2:
                return (self.paso, 50)                 # baja de golpe: recuperación
            return None


@events.quitting.add_listener
def _criterio(environment, **_):
    """Falla la corrida (código de salida 1) si más del 1 % de las peticiones falló o si el p95 global pasa de UMBRAL_P95_MS."""
    s = environment.stats.total
    umbral = int(os.environ.get("UMBRAL_P95_MS", "800"))
    if s.num_requests and (s.fail_ratio > 0.01 or s.get_response_time_percentile(0.95) > umbral):
        environment.process_exit_code = 1
