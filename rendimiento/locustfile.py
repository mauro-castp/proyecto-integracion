"""
locustfile.py — Carga con los perfiles reales de la plataforma, llamando a los microservicios por HTTP.

  Cliente (Android)       catálogo con caché, sus pedidos, avisos y, de vez en cuando, un pedido que luego cancela
  Repartidor (Android)    sus paradas, puntos GPS y estado de sincronización
  Operador (portal)       inventario, alertas y pedidos de su microhub
  Planeador (escritorio)  reportes y planeación en XML
  Administrador           panel de monitoreo, indicadores y bitácora
  Proceso automático      pone simulaciones en cola

Escalones de usuarios y un descenso final para ver la recuperación (ver ESCALONES). Se corre con rendimiento/correr_locust.sh.
"""
import os
import random
import uuid
import datetime as dt

from locust import FastHttpUser, LoadTestShape, between, task

CLAVE = os.environ.get("MICROHUBS_CLAVE", "Codex#2026")
PUERTOS = {"auth": 5101, "productos": 5103, "pedidos": 5104, "entregas": 5105, "planeacion": 5106, "zonas": 5108, "seguimiento": 5110,
           "inventario": 5111, "demanda": 5115, "cobertura": 5116, "rutas": 5118, "simulacion": 5121, "reportes": 5123, "notificaciones": 5124,
           "sincronizacion": 5125, "auditoria-monitoreo": 5126, "usuarios": 5102, "documentos": 5107, "microhubs": 5109, "precios": 5112,
           "proveedores": 5113, "abastecimiento": 5114, "capacidad": 5117, "costos": 5119, "punto-equilibrio": 5120, "surtido": 5122}
DURACION = int(os.environ.get("ESCALON_SEGUNDOS", "60"))
ESCALONES = [int(x) for x in os.environ.get("ESCALONES", "10,25,50,100,150,10").split(",")]


class Perfil(FastHttpUser):
    abstract = True
    host = "http://localhost"
    wait_time = between(1, 3)
    correo = ""
    formato = "json"

    def on_start(self):
        self.token = None
        with self.client.post(self.url("auth", "auth/login"), json={"correo": self.correo, "clave": CLAVE, "dispositivo": "locust"},
                              name="auth  POST login", catch_response=True) as r:
            if r.status_code != 200:
                r.failure(f"no pudo entrar: {r.status_code}")
                return
            self.token = r.json()["token_acceso"]
        self.preparar()

    def preparar(self):
        pass

    def url(self, servicio, ruta):
        return f"http://{servicio}:{PUERTOS[servicio]}/api/v1/{ruta}"

    def pedir(self, servicio, ruta, nombre=None, metodo="GET", esperados=(200,), **kw):
        if not self.token:
            return None
        cabeceras = {"Authorization": f"Bearer {self.token}", "Accept": "application/xml" if self.formato == "xml" else "application/json"}
        with self.client.request(metodo, self.url(servicio, ruta), headers=cabeceras, name=f"{servicio}  {metodo} {nombre or ruta.split('?')[0]}",
                                 catch_response=True, **kw) as r:
            if r.status_code in esperados:
                r.success()
                return r
            r.failure(f"HTTP {r.status_code}")
        return None


class Cliente(Perfil):
    weight = 5
    correo = "juan.chapa1@correo.mx"

    def preparar(self):
        r = self.pedir("productos", "productos?por_pagina=50&estatus=activo")
        datos = r.json()["datos"] if r else []
        self.productos = sorted(datos, key=lambda p: -float(p["precio"]))[:12]

    @task(10)
    def catalogo(self):
        self.pedir("productos", f"productos?pagina={random.randint(1, 3)}", "productos")

    @task(3)
    def zonas(self):
        self.pedir("zonas", "zonas")

    @task(5)
    def mis_pedidos(self):
        self.pedir("pedidos", "pedidos?por_pagina=10", "pedidos")

    @task(4)
    def avisos(self):
        self.pedir("notificaciones", "notificaciones/conteo")

    @task(1)
    def comprar_y_cancelar(self):
        if not getattr(self, "productos", None):
            return
        lineas = [{"producto_id": p["id"], "cantidad": 3} for p in random.sample(self.productos, 2)]
        r = self.pedir("pedidos", "pedidos", metodo="POST", esperados=(201, 422), json={"lineas": lineas, "operacion_uuid": str(uuid.uuid4())})
        if r is not None and r.status_code == 201:
            pid = r.json()["id"]
            self.pedir("pedidos", f"pedidos/{pid}/estado", "pedidos/{id}/estado", metodo="POST", esperados=(200, 409, 422),
                       json={"estado": "cancelado", "motivo": "Prueba de carga"})


class Repartidor(Perfil):
    weight = 3
    correo = "repartidor1@codex.mx"

    def preparar(self):
        self.entregas = []

    @task(6)
    def mis_entregas(self):
        r = self.pedir("entregas", "entregas/mias?por_pagina=20", "entregas/mias")
        if r:
            self.entregas = [e["id"] for e in r.json()["datos"]]

    @task(5)
    def gps(self):
        if not self.entregas:
            return
        punto = {"latitud": 25.74 + random.random() / 100, "longitud": -100.36 + random.random() / 100, "capturado_en": dt.datetime.now(dt.timezone.utc).isoformat()}
        self.pedir("seguimiento", f"seguimiento/{random.choice(self.entregas)}/ubicaciones", "seguimiento/{id}/ubicaciones", metodo="POST",
                   esperados=(201, 403, 404), json={"puntos": [punto]})

    @task(2)
    def sincronizacion(self):
        self.pedir("sincronizacion", "sincronizacion/estado?dispositivo=locust-1", "sincronizacion/estado")


class Operador(Perfil):
    weight = 2
    correo = "operador.mh01@codex.mx"

    @task(4)
    def existencias(self):
        self.pedir("inventario", f"inventario?pagina={random.randint(1, 3)}", "inventario")

    @task(2)
    def alertas(self):
        self.pedir("inventario", "inventario/alertas")

    @task(3)
    def pedidos(self):
        self.pedir("pedidos", "pedidos?estado=asignado", "pedidos?estado")

    @task(1)
    def rutas(self):
        self.pedir("rutas", "rutas/planes")

    @task(2)
    def abasto(self):
        self.pedir("abastecimiento", "abastecimiento/necesidades?microhub_id=1", "abastecimiento/necesidades")

    @task(1)
    def proveedores(self):
        self.pedir("proveedores", "proveedores")

    @task(1)
    def archivos(self):
        self.pedir("documentos", "documentos?por_pagina=10", "documentos")

    @task(1)
    def perfil(self):
        self.pedir("usuarios", "usuarios/yo")


class PlaneadorEscritorio(Perfil):
    weight = 1
    correo = "planeador@codex.mx"
    formato = "xml"

    @task(3)
    def reporte(self):
        self.pedir("reportes", "reportes/pedidos_por_dia")

    @task(2)
    def comparacion(self):
        self.pedir("reportes", "reportes/comparacion_microhubs")

    @task(3)
    def candidatos(self):
        self.pedir("planeacion", "candidatos")

    @task(2)
    def demanda(self):
        self.pedir("demanda", "demanda/resumen")

    @task(1)
    def cobertura(self):
        self.pedir("cobertura", "cobertura/zonas")

    @task(1)
    def capacidad(self):
        self.pedir("capacidad", "capacidad/microhubs")

    @task(1)
    def colas(self):
        self.pedir("capacidad", "capacidad/colas?microhub_id=1", "capacidad/colas")

    @task(1)
    def costos(self):
        self.pedir("costos", "costos/resumen")

    @task(1)
    def equilibrio(self):
        self.pedir("punto-equilibrio", "punto-equilibrio/microhubs")

    @task(1)
    def surtido(self):
        self.pedir("surtido", "surtido/analisis?microhub_id=1", "surtido/analisis")

    @task(1)
    def precios(self):
        self.pedir("precios", "precios/listas")


class Administrador(Perfil):
    weight = 1
    correo = "admin@codex.mx"

    @task(4)
    def panel(self):
        self.pedir("auditoria-monitoreo", "monitoreo/estado")

    @task(2)
    def indicadores(self):
        self.pedir("reportes", "reportes/indicadores")

    @task(2)
    def bitacora(self):
        self.pedir("auditoria-monitoreo", "auditoria?por_pagina=20", "auditoria")

    @task(1)
    def red(self):
        self.pedir("microhubs", "microhubs")


class ProcesoAutomatico(Perfil):
    fixed_count = 1
    correo = "planeador@codex.mx"
    wait_time = between(20, 30)

    @task
    def simular(self):
        self.pedir("simulacion", "simulacion/ejecuciones", metodo="POST", esperados=(202, 409, 422),
                   json={"pedidos_dia": 45, "ticket": 135, "costos_fijos": 60000, "costo_variable_pedido": 32.6, "operadores": 3, "repartidores": 2,
                         "dias": 7, "replicas": 50})


class Escalones(LoadTestShape):
    def tick(self):
        paso = int(self.get_run_time() // DURACION)
        if paso >= len(ESCALONES):
            return None
        return ESCALONES[paso], 20
