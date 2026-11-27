"""
test_apps_cliente.py — Lo que se agregó al cerrar la entrega final para las apps: el cliente en Android (pedido hecho sin red que llega por
sincronización y confirmación de recepción) y la operación desde el escritorio en XML (cambio de estado y asignación de paradas).

Contra PostgreSQL y Redis reales, con los servicios en proceso (igual que test_ola2). Cada prueba deja los datos como estaban o cancela lo
que creó.

  cd servicios && python -m unittest -v pruebas.test_apps_cliente
"""
import datetime as dt
import uuid

from pruebas.test_ola2 import Base, ejecutar, setUpModule, tearDownModule, uno  # noqa: F401  (setUp/tearDownModule los usa unittest)
from pruebas.test_contrato import ejemplo, mismas_llaves, xml

CLIENTE = "juan.chapa1@correo.mx"
LINEAS = [{"producto_id": 3, "cantidad": 3}]          # pasa el pedido mínimo de la zona (90)


class T1ClienteMovil(Base):
    def lote(self, cliente, ops):
        r, d = cliente.llamar("sincronizacion", "POST", "sincronizacion/lotes",
                              {"lote_uuid": str(uuid.uuid4()), "dispositivo": "android-cliente-prueba", "cliente": "android", "operaciones": ops})
        self.assertIn(r.status_code, (200, 201), r.data[:300])
        return d

    def test_pedido_sin_red_llega_por_sincronizacion_y_no_se_duplica(self):
        u = str(uuid.uuid4())
        op = {"operacion_uuid": u, "tipo": "pedido_nuevo", "creada_en": dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds"),
              "datos": {"lineas": LINEAS}}
        r = self.lote(self.cli, [op])
        self.assertEqual((r["aplicadas"], r["operaciones"][0]["estado"], r["operaciones"][0]["http_status"]), (1, "aplicada", 201))
        pedido = uno("SELECT id, estado::text AS estado FROM pedido WHERE operacion_uuid = %s", (u,))
        try:
            self.assertIsNotNone(pedido)
            otra = self.lote(self.cli, [op])                                   # el mismo uuid otra vez: el servicio de pedidos no lo duplica
            self.assertEqual(otra["operaciones"][0]["estado"], "aplicada")
            self.assertTrue(otra["operaciones"][0]["duplicada"] or otra["operaciones"][0]["http_status"] == 200)
            self.assertEqual(uno("SELECT count(*) AS n FROM pedido WHERE operacion_uuid = %s", (u,))["n"], 1)
            sin_lineas = self.lote(self.cli, [{**op, "operacion_uuid": str(uuid.uuid4()), "datos": {}}])
            self.assertEqual(sin_lineas["operaciones"][0]["estado"], "rechazada")
        finally:
            if pedido and pedido["estado"] not in ("cancelado", "entregado"):
                self.cli.llamar("pedidos", "POST", f"pedidos/{pedido['id']}/estado", {"estado": "cancelado", "motivo": "Prueba automática"}, estado=200)

    def test_confirmar_recepcion_solo_el_cliente_dueno_y_ya_entregado(self):
        f = uno("SELECT p.id, e.id AS entrega_id, e.confirmacion_recepcion FROM pedido p JOIN cliente c ON c.id = p.cliente_id "
                "JOIN usuario us ON us.id = c.usuario_id JOIN entrega e ON e.pedido_id = p.id "
                "WHERE us.correo = %s AND p.estado IN ('entregado', 'entrega_parcial') AND e.cierre_en IS NOT NULL ORDER BY p.id DESC LIMIT 1", (CLIENTE,))
        if not f:
            self.skipTest("El cliente de prueba no tiene pedidos entregados")
        try:
            _, r = self.cli.llamar("entregas", "POST", "entregas/recepciones", {"pedido_id": f["id"], "conforme": False}, estado=200)
            mismas_llaves(self, r, ejemplo("RecepcionCliente.ok"))
            self.assertFalse(uno("SELECT confirmacion_recepcion FROM entrega WHERE id = %s", (f["entrega_id"],))["confirmacion_recepcion"])
            self.cli.llamar("entregas", "POST", "entregas/recepciones", {"pedido_id": f["id"], "conforme": True}, estado=200)
            self.assertTrue(uno("SELECT confirmacion_recepcion FROM entrega WHERE id = %s", (f["entrega_id"],))["confirmacion_recepcion"])
            self.assertEqual(self.http(self.op1, "entregas", "POST", "entregas/recepciones", {"pedido_id": f["id"], "conforme": True}), 403)
            ajeno = uno("SELECT p.id FROM pedido p JOIN cliente c ON c.id = p.cliente_id JOIN usuario us ON us.id = c.usuario_id "
                        "WHERE us.correo <> %s LIMIT 1", (CLIENTE,))
            self.assertEqual(self.http(self.cli, "entregas", "POST", "entregas/recepciones", {"pedido_id": ajeno["id"], "conforme": True}), 404)
            self.assertEqual(self.http(self.cli, "entregas", "POST", "entregas/recepciones", {"pedido_id": f["id"]}), 422)
        finally:
            ejecutar("UPDATE entrega SET confirmacion_recepcion = %s WHERE id = %s", (f["confirmacion_recepcion"], f["entrega_id"]))

    def test_no_se_confirma_un_pedido_que_no_se_entrega(self):
        _, creado = self.cli.llamar("pedidos", "POST", "pedidos", {"lineas": LINEAS}, estado=201)
        try:
            self.assertEqual(self.http(self.cli, "entregas", "POST", "entregas/recepciones", {"pedido_id": creado["id"], "conforme": True}), 409)
        finally:
            self.cli.llamar("pedidos", "POST", f"pedidos/{creado['id']}/estado", {"estado": "cancelado", "motivo": "Prueba automática"}, estado=200)


class T2OperacionXml(Base):
    def test_cambio_de_estado_y_asignacion_en_xml(self):
        """El escritorio solo habla XML: pasa un pedido a preparación, intenta despacharlo antes de tiempo (409) y lo marca listo.
        El pedido queda listo en su microhub (no hay transición de regreso); sirve para las pruebas de rutas."""
        _, creado = self.cli.llamar("pedidos", "POST", "pedidos", {"lineas": LINEAS}, estado=201)
        pid = creado["id"]
        clave = (uno("SELECT clave FROM microhub WHERE id = %s", (creado["microhub_id"],)) or {}).get("clave", "")
        correo = "operador." + clave.replace("-", "").lower() + "@codex.mx"            # MH-02 → operador.mh02@codex.mx
        if creado["estado"] != "asignado" or not uno("SELECT 1 AS x FROM usuario WHERE correo = %s", (correo,)):
            self.cli.llamar("pedidos", "POST", f"pedidos/{pid}/estado", {"estado": "cancelado", "motivo": "Prueba automática"})
            self.skipTest(f"El pedido quedó {creado['estado']} en el microhub {creado['microhub_id']}, sin operador de prueba")
        op_xml = self.entrar(correo, "xml")
        op_xml.caso = self
        _, (raiz, p) = op_xml.llamar("pedidos", "POST", f"pedidos/{pid}/estado", xml("pedido_estado_cambio", {"estado": "en_preparacion"}), estado=200)
        self.assertEqual((raiz, p["estado"]), ("pedido", "en_preparacion"))
        op_xml.llamar("pedidos", "POST", f"pedidos/{pid}/estado", xml("pedido_estado_cambio", {"estado": "entregado"}), estado=422)   # el XSD no deja cerrar
        rep = uno("SELECT u.id FROM usuario u JOIN rol r ON r.id = u.rol_id WHERE r.clave = 'repartidor' AND u.estatus = 'activo' ORDER BY u.id LIMIT 1")
        cuerpo = xml("asignacion_nueva", {"paradas": {"parada": {"pedido_id": pid, "repartidor_id": rep["id"], "orden_parada": 1}}})
        op_xml.llamar("entregas", "POST", "entregas/asignaciones", cuerpo, estado=409)               # aún no está listo
        _, (raiz, l) = op_xml.llamar("pedidos", "POST", f"pedidos/{pid}/listo", estado=200)
        self.assertEqual(raiz, "pedido_listo")
        self.assertEqual(uno("SELECT estado::text AS e FROM pedido WHERE id = %s", (pid,))["e"], "en_preparacion")
