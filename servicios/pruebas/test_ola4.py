"""
test_ola4.py — Entrega final: altas, cambios y bajas de productos, zonas, microhubs y usuarios; alta de pedidos y asignación de entregas, contra
PostgreSQL, Redis y MongoDB reales. Cada prueba usa claves únicas y retira lo que se puede borrar (las cuentas quedan dadas de baja porque
la bitácora, que es de solo escritura, las referencia).

  servicios/pruebas/correr.sh test pruebas.test_ola4 -v
"""
import base64
import datetime as dt
import json
import os
import sys
import unittest
import uuid
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
os.environ.setdefault("LOG_STDOUT", "0")
os.environ.setdefault("MONITOR_AUTO", "0")

from comun import clientes, config, datos  # noqa: E402
from pruebas.test_contrato import APPS, JPEG, Cliente, ejemplo, mismas_llaves, xml  # noqa: E402

LIMITE = {}


def transporte(servicio, metodo, ruta, cuerpo, params, token, traza):
    enc = {"Accept": "application/json", "Content-Type": "application/json"}
    if token:
        enc["Authorization"] = f"Bearer {token}"
    r = APPS[servicio].test_client().open(f"/api/v1/{ruta}", method=metodo, query_string=params or None, headers=enc,
                                          data=json.dumps(cuerpo) if cuerpo is not None else None)
    return r.status_code, (r.get_json(silent=True) if r.data else None)


def setUpModule():
    clientes.usar_transporte(transporte)
    LIMITE["antes"], LIMITE["login"] = config.LIMITE_POR_MINUTO, config.LIMITE_LOGIN_POR_MINUTO
    config.LIMITE_POR_MINUTO = config.LIMITE_LOGIN_POR_MINUTO = 1_000_000


def tearDownModule():
    clientes.usar_transporte(None)
    config.LIMITE_POR_MINUTO, config.LIMITE_LOGIN_POR_MINUTO = LIMITE["antes"], LIMITE["login"]


def uno(sql, args=()):
    return datos.consultar(sql, args, una=True)


def todos(sql, args=()):
    return datos.consultar(sql, args)


def ejecutar(sql, args=()):
    with datos.conexion() as con, con.cursor() as cur:
        cur.execute(sql, args)


def sufijo():
    return uuid.uuid4().hex[:8].upper()


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._caso = unittest.TestCase()
        cls.adm = cls.entrar("admin@codex.mx")
        cls.adm_xml = cls.entrar("admin@codex.mx", "xml")
        cls.plan = cls.entrar("planeador@codex.mx")
        cls.op1 = cls.entrar("operador.mh01@codex.mx")
        cls.rep = cls.entrar("repartidor1@codex.mx")
        cls.cli = cls.entrar("juan.chapa1@correo.mx")

    @classmethod
    def entrar(cls, correo, formato="json"):
        c = Cliente(cls._caso, formato)
        c.entrar(correo)
        return c

    def setUp(self):
        for c in (self.adm, self.adm_xml, self.plan, self.op1, self.rep, self.cli):
            c.caso = self

    def error(self, cliente, servicio, metodo, ruta, cuerpo, estado, codigo=None):
        r, d = cliente.llamar(servicio, metodo, ruta, cuerpo, estado=estado)
        if codigo:
            self.assertEqual(d["error"]["codigo"], codigo)
        return d["error"]

    def bitacora(self, entidad, ident):
        return [f["accion"] for f in todos("SELECT accion::text AS accion FROM auditoria WHERE entidad = %s AND entidad_id = %s ORDER BY id", (entidad, str(ident)))]


# ====================================================================
class T1Catalogos(Base):
    def test_producto_alta_cambio_y_baja(self):
        clave = "T-" + sufijo()
        nuevo = {"clave_interna": clave, "nombre": f"Producto de prueba {clave}", "categoria_id": 1, "unidad": "pieza", "precio": 21.5}
        # la lista queda en caché antes del alta: después debe verse el producto
        self.adm.llamar("productos", "GET", f"productos?q={clave}", estado=200)
        _, p = self.adm.llamar("productos", "POST", "productos", nuevo, estado=201)
        try:
            mismas_llaves(self, p, ejemplo("Producto.ok"))
            self.assertEqual((p["clave_interna"], float(p["precio"]), p["estatus"]), (clave, 21.5, "activo"))
            _, l = self.adm.llamar("productos", "GET", f"productos?q={clave}", estado=200)
            self.assertEqual(l["paginacion"]["total"], 1, "el alta borra la caché del catálogo")
            _, c = self.adm.llamar("productos", "PATCH", f"productos/{p['id']}", {"precio": 25}, estado=200)
            self.assertEqual(float(c["precio"]), 25.0)
            self.assertEqual(float(self.adm.llamar("productos", "GET", f"productos/{p['id']}", estado=200)[1]["precio"]), 25.0)
            self.adm.llamar("productos", "DELETE", f"productos/{p['id']}", estado=204)
            self.assertEqual(self.adm.llamar("productos", "GET", f"productos/{p['id']}", estado=200)[1]["estatus"], "inactivo", "baja lógica")
            self.assertEqual(self.bitacora("producto", p["id"])[0], "alta")
            self.assertGreaterEqual(len(self.bitacora("producto", p["id"])), 3, "alta, cambio de precio y baja quedan en la bitácora")
            self.error(self.adm, "productos", "POST", "productos", nuevo, 409, "CONFLICTO")
        finally:
            ejecutar("DELETE FROM producto_precio_historico WHERE producto_id = %s", (p["id"],))
            ejecutar("DELETE FROM producto WHERE id = %s", (p["id"],))

    def test_producto_en_xml_y_validaciones(self):
        clave = "T-" + sufijo()
        cuerpo = xml("producto_nuevo", {"clave_interna": clave, "nombre": "Producto XML", "categoria_id": 1, "unidad": "pieza", "precio": "10.00"})
        _, (raiz, p) = self.adm_xml.llamar("productos", "POST", "productos", cuerpo, estado=201)
        try:
            self.assertEqual((raiz, p["clave_interna"]), ("producto", clave))
        finally:
            ejecutar("DELETE FROM producto WHERE id = %s", (int(p["id"]),))
        base = {"clave_interna": "T-" + sufijo(), "nombre": "X", "categoria_id": 1, "unidad": "pieza", "precio": 5}
        for nombre, malo in {"precio cero": {**base, "precio": 0}, "sin nombre": {k: v for k, v in base.items() if k != "nombre"},
                             "categoria inexistente": {**base, "categoria_id": 999999}, "tres decimales": {**base, "precio": 1.234}}.items():
            with self.subTest(nombre):
                self.error(self.adm, "productos", "POST", "productos", malo, 422)
        self.error(self.adm, "productos", "PATCH", "productos/999999", {"precio": 3}, 404)
        self.error(self.adm, "productos", "PATCH", "productos/1", {}, 422)

    def test_zona_alta_cambio_y_baja(self):
        clave = "Z" + sufijo()
        nueva = {"clave": clave, "nombre": "Zona de prueba", "colonia": f"Colonia {clave}", "codigo_postal": "64102", "latitud": 25.76, "longitud": -100.37,
                 "ticket_minimo": 80}
        _, z = self.adm.llamar("zonas", "POST", "zonas", nueva, estado=201)
        try:
            mismas_llaves(self, z, ejemplo("Zona.ok"))
            _, c = self.adm.llamar("zonas", "PATCH", f"zonas/{z['id']}", {"nombre": "Zona renombrada", "latitud": 25.7612}, estado=200)
            self.assertEqual((c["nombre"], c["latitud"]), ("Zona renombrada", 25.7612))
            self.adm.llamar("zonas", "DELETE", f"zonas/{z['id']}", estado=204)
            self.assertEqual(uno("SELECT estatus::text AS e FROM zona WHERE id = %s", (z["id"],))["e"], "inactivo")
            self.error(self.adm, "zonas", "POST", "zonas", nueva, 409)
            self.error(self.adm, "zonas", "POST", "zonas", {**nueva, "clave": "Z" + sufijo(), "codigo_postal": "ABC"}, 422)
        finally:
            ejecutar("DELETE FROM zona WHERE id = %s", (z["id"],))

    def test_microhub_alta_cambio_y_baja_protegida(self):
        clave = "MH" + sufijo()
        nuevo = {"clave": clave, "nombre": "Microhub de prueba", "direccion": "Calle 1 número 2", "latitud": 25.7601, "longitud": -100.3555, "radio_km": 1.2,
                 "capacidad_turno": 80, "hora_apertura": "08:00", "hora_cierre": "20:00"}
        _, m = self.adm.llamar("microhubs", "POST", "microhubs", nuevo, estado=201)
        try:
            mismas_llaves(self, m, ejemplo("Microhub.ok"))
            _, c = self.adm.llamar("microhubs", "PATCH", f"microhubs/{m['id']}", {"radio_km": 2.5}, estado=200)
            self.assertEqual(c["radio_km"], 2.5)
            self.error(self.adm, "microhubs", "PATCH", f"microhubs/{m['id']}", {"hora_cierre": "07:00"}, 422)
            self.adm.llamar("microhubs", "DELETE", f"microhubs/{m['id']}", estado=204)
            con_pedidos = uno("SELECT microhub_id AS id FROM pedido WHERE estado IN ('asignado','en_preparacion','en_ruta') LIMIT 1")
            if con_pedidos:
                e = self.error(self.adm, "microhubs", "DELETE", f"microhubs/{con_pedidos['id']}", None, 409, "CONFLICTO")
                self.assertIn("pedidos abiertos", e["mensaje"])
        finally:
            ejecutar("DELETE FROM microhub WHERE id = %s", (m["id"],))

    def test_solo_con_permiso(self):
        for servicio, ruta, cuerpo in (("productos", "productos", ejemplo("ProductoNuevo.ok")), ("zonas", "zonas", ejemplo("ZonaNueva.ok")),
                                       ("microhubs", "microhubs", ejemplo("MicrohubNuevo.ok")), ("usuarios", "usuarios", ejemplo("UsuarioNuevo.ok"))):
            with self.subTest(servicio):
                for quien in (self.op1, self.rep, self.cli, self.plan):
                    self.error(quien, servicio, "POST", ruta, cuerpo, 403, "PROHIBIDO")
                    self.error(quien, servicio, "DELETE", f"{ruta}/1", None, 403)
                Cliente(self, "json").llamar(servicio, "POST", ruta, cuerpo, token=False, estado=401)


# ====================================================================
class T2Usuarios(Base):
    CLAVE = "Clave-de-prueba-2026"

    def nueva(self, rol="repartidor", **extra):
        correo = f"prueba.{sufijo().lower()}@ejemplo.mx"
        _, u = self.adm.llamar("usuarios", "POST", "usuarios", {"nombre": "Prueba", "apellidos": "Automática", "correo": correo, "clave": self.CLAVE,
                                                              "rol": rol, **extra}, estado=201)
        self.addCleanup(lambda: self.adm.llamar("usuarios", "DELETE", f"usuarios/{u['id']}"))
        return u, correo

    def iniciar(self, correo, clave=None):
        c = Cliente(self, "json")
        r, d = c.llamar("auth", "POST", "auth/login", {"correo": correo, "clave": clave or self.CLAVE, "dispositivo": "t"}, token=False)
        if r.status_code == 200:
            c.token = d["token_acceso"]
        return c, r.status_code

    def test_crear_una_cuenta_que_puede_entrar_y_no_expone_la_clave(self):
        u, correo = self.nueva()
        mismas_llaves(self, u, ejemplo("Perfil.ok"))
        self.assertNotIn(self.CLAVE, json.dumps(u))
        h = uno("SELECT hash_contrasena AS h FROM usuario WHERE id = %s", (u["id"],))["h"]
        self.assertTrue(h.startswith("$2b$"), "la clave se guarda con bcrypt")
        self.assertEqual(self.iniciar(correo)[1], 200)
        self.assertIn("alta", self.bitacora("usuario", u["id"]))
        e = self.error(self.adm, "usuarios", "POST", "usuarios", {"nombre": "a", "apellidos": "b", "correo": correo, "clave": self.CLAVE, "rol": "repartidor"}, 409)

    def test_cambiar_el_perfil_cierra_las_sesiones_y_la_baja_impide_entrar(self):
        u, correo = self.nueva()
        sesion, _ = self.iniciar(correo)
        sesion.llamar("usuarios", "GET", "usuarios/yo", estado=200)
        _, c = self.adm.llamar("usuarios", "PATCH", f"usuarios/{u['id']}", {"rol": "planeador"}, estado=200)
        self.assertEqual(c["rol"], "planeador")
        sesion.llamar("usuarios", "GET", "usuarios/yo", estado=401)
        nueva_sesion, s = self.iniciar(correo)
        self.assertEqual(s, 200)
        self.adm.llamar("usuarios", "DELETE", f"usuarios/{u['id']}", estado=204)
        nueva_sesion.llamar("usuarios", "GET", "usuarios/yo", estado=401)
        self.assertNotEqual(self.iniciar(correo)[1], 200)
        self.assertEqual(uno("SELECT estatus::text AS e, fecha_baja IS NOT NULL AS f FROM usuario WHERE id = %s", (u["id"],)), {"e": "baja", "f": True})
        self.adm.llamar("usuarios", "DELETE", f"usuarios/{u['id']}", estado=204)            # repetirla no falla
        self.error(self.adm, "usuarios", "PATCH", f"usuarios/{u['id']}", {"nombre": "x"}, 409)

    def test_validaciones_y_proteccion_de_la_propia_cuenta(self):
        base = {"nombre": "a", "apellidos": "b", "correo": f"x.{sufijo().lower()}@ejemplo.mx", "clave": self.CLAVE, "rol": "repartidor"}
        for nombre, malo in {"clave corta": {**base, "clave": "corta"}, "correo": {**base, "correo": "sin-arroba"}, "rol": {**base, "rol": "jefe"},
                             "telefono": {**base, "telefono": "12"}}.items():
            with self.subTest(nombre):
                self.error(self.adm, "usuarios", "POST", "usuarios", malo, 422, "VALIDACION")
        yo = self.adm.usuario["id"]
        self.error(self.adm, "usuarios", "DELETE", f"usuarios/{yo}", None, 409, "CONFLICTO")
        self.error(self.adm, "usuarios", "PATCH", f"usuarios/{yo}", {"rol": "cliente"}, 409)
        self.error(self.adm, "usuarios", "DELETE", "usuarios/999999", None, 404)


# ====================================================================
class T3PedidoYEntrega(Base):
    def lineas(self, factor=1):
        """Dos productos con existencia en todos los microhubs, en cantidad suficiente para el pedido mínimo."""
        p = todos("SELECT p.id, p.precio FROM producto p WHERE p.estatus = 'activo' AND (SELECT count(*) FROM inventario i WHERE i.producto_id = p.id "
                  "AND i.existencia > 30) >= (SELECT count(*) FROM microhub WHERE estatus = 'activo') ORDER BY p.precio DESC LIMIT 2")
        if len(p) < 2:
            p = todos("SELECT p.id, p.precio FROM producto p WHERE p.estatus = 'activo' AND EXISTS (SELECT 1 FROM inventario i WHERE i.producto_id = p.id "
                      "AND i.existencia > 30) ORDER BY p.precio DESC LIMIT 2")
        return [{"producto_id": x["id"], "cantidad": 3 * factor} for x in p]

    def pedir(self, **extra):
        cuerpo = {"lineas": self.lineas(), **extra}
        return self.cli.llamar("pedidos", "POST", "pedidos", cuerpo)

    def test_un_pedido_se_crea_con_el_precio_del_servidor_y_no_se_duplica(self):
        op = str(uuid.uuid4())
        r, p = self.pedir(operacion_uuid=op)
        self.assertEqual(r.status_code, 201, p)
        mismas_llaves(self, p, ejemplo("PedidoCreado.ok"))
        esperado = sum(float(uno("SELECT precio FROM producto WHERE id = %s", (l["producto_id"],))["precio"]) * l["cantidad"] for l in self.lineas())
        self.assertAlmostEqual(float(p["subtotal"]), esperado, places=2)
        self.assertAlmostEqual(float(p["total"]), float(p["subtotal"]) + float(p["costo_envio"]), places=2)
        self.assertEqual(p["asignado"], p["microhub_id"] is not None)
        r2, d = self.cli.llamar("pedidos", "POST", "pedidos", {"lineas": self.lineas(), "operacion_uuid": op}, estado=200)
        self.assertEqual((d["id"], d["duplicado"]), (p["id"], True))
        self.assertEqual(uno("SELECT count(*) AS n FROM pedido WHERE operacion_uuid = %s", (op,))["n"], 1)

    def test_reglas_del_pedido(self):
        antes = uno("SELECT count(*) AS n FROM demanda_no_atendida WHERE origen = 'api'")["n"]
        barato = uno("SELECT id FROM producto WHERE estatus = 'activo' ORDER BY precio LIMIT 1")["id"]
        e = self.error(self.cli, "pedidos", "POST", "pedidos", {"lineas": [{"producto_id": barato, "cantidad": 1}]}, 422, "REGLA_NEGOCIO")
        self.assertIn("mínimo", e["mensaje"])
        self.assertEqual(uno("SELECT count(*) AS n FROM demanda_no_atendida WHERE origen = 'api'")["n"], antes + 1, "la demanda no atendida queda registrada")
        limite = int(datos.parametro("limite_unidades_linea", 20))
        e = self.error(self.cli, "pedidos", "POST", "pedidos", {"lineas": [{"producto_id": self.lineas()[0]["producto_id"], "cantidad": limite + 1}]}, 422)
        for nombre, cuerpo in {"sin líneas": {"lineas": []}, "producto repetido": {"lineas": [self.lineas()[0]] * 2},
                               "producto inexistente": {"lineas": [{"producto_id": 999999, "cantidad": 99}]},
                               "cantidad cero": {"lineas": [{"producto_id": 1, "cantidad": 0}]}, "uuid": {"lineas": self.lineas(), "operacion_uuid": "x"},
                               "domicilio ajeno": {"lineas": self.lineas(), "domicilio_id": 999999}}.items():
            with self.subTest(nombre):
                self.error(self.cli, "pedidos", "POST", "pedidos", cuerpo, 422)
        otro = uno("SELECT c.id FROM cliente c JOIN usuario u ON u.id = c.usuario_id WHERE u.correo <> 'juan.chapa1@correo.mx' ORDER BY c.id LIMIT 1")["id"]
        self.error(self.cli, "pedidos", "POST", "pedidos", {"cliente_id": otro, "lineas": self.lineas()}, 403, "PROHIBIDO")
        self.error(self.rep, "pedidos", "POST", "pedidos", {"lineas": self.lineas()}, 403)
        self.error(self.adm, "pedidos", "POST", "pedidos", {"lineas": self.lineas()}, 422, "VALIDACION")

    def test_del_pedido_a_la_entrega_solo_por_la_api(self):
        _, p = self.cli.llamar("pedidos", "POST", "pedidos", {"lineas": self.lineas()}, estado=201)
        self.assertTrue(p["asignado"], p)
        operador = self.entrar(uno("SELECT u.correo FROM usuario u JOIN rol r ON r.id = u.rol_id WHERE r.clave = 'operador' AND u.microhub_id = %s "
                                   "AND u.estatus = 'activo' ORDER BY u.id LIMIT 1", (p["microhub_id"],))["correo"])
        operador.caso = self
        entrega = {"pedido_id": p["id"], "repartidor_id": self.rep.usuario["id"]}
        self.error(operador, "entregas", "POST", "entregas", entrega, 409, "CONFLICTO")                       # todavía no está listo
        self.error(operador, "pedidos", "POST", f"pedidos/{p['id']}/listo", None, 409)
        operador.llamar("pedidos", "POST", f"pedidos/{p['id']}/estado", {"estado": "en_preparacion"}, estado=200)
        _, l = operador.llamar("pedidos", "POST", f"pedidos/{p['id']}/listo", estado=200)
        mismas_llaves(self, l, ejemplo("PedidoListo.ok"))
        self.error(operador, "entregas", "POST", "entregas", {**entrega, "repartidor_id": self.cli.usuario["id"]}, 422)
        self.error(self.rep, "entregas", "POST", "entregas", entrega, 403)
        ajeno = uno("SELECT u.correo FROM usuario u JOIN rol r ON r.id = u.rol_id WHERE r.clave = 'operador' AND u.microhub_id <> %s AND u.estatus = 'activo' LIMIT 1",
                    (p["microhub_id"],))
        if ajeno:
            otro = self.entrar(ajeno["correo"]); otro.caso = self
            self.error(otro, "entregas", "POST", "entregas", entrega, 403)
        _, e = operador.llamar("entregas", "POST", "entregas", entrega, estado=201)
        mismas_llaves(self, e, ejemplo("EntregaCreada.ok"))
        self.error(operador, "entregas", "POST", "entregas", entrega, 409)
        _, mias = self.rep.llamar("entregas", "GET", "entregas/mias?por_pagina=100", estado=200)
        self.assertIn(e["entrega_id"], [x["id"] for x in mias["datos"]])
        self.assertTrue(uno("SELECT 1 AS x FROM web_notificacion WHERE destinatario_id = %s AND referencia_id = %s", (self.rep.usuario["id"], str(e["entrega_id"]))),
                        "el repartidor recibe el aviso")
        _, doc = self.rep.llamar("documentos", "POST", "documentos", {"nombre": "flujo_ola4.jpg", "tipo_mime": "image/jpeg",
                                 "contenido_base64": base64.b64encode(JPEG).decode(), "referencia": {"tipo": "entrega", "id": str(e["entrega_id"])}}, estado=201)
        self.rep.llamar("entregas", "POST", f"entregas/{e['entrega_id']}/resultado", {
            "resultado": "entregado", "monto_cobrado": p["total"], "cambio_entregado": 0, "ubicacion": {"latitud": 25.7491, "longitud": -100.3611},
            "evidencia_ids": [doc["id"]], "capturado_en": dt.datetime.now(dt.timezone.utc).isoformat(), "id_cliente_local": str(uuid.uuid4())}, estado=201)
        self.assertEqual(uno("SELECT estado::text AS e FROM pedido WHERE id = %s", (p["id"],))["e"], "entregado")
        estados = [f["e"] for f in todos("SELECT estado_nuevo::text AS e FROM historial_estatus WHERE pedido_id = %s ORDER BY id", (p["id"],))]
        self.assertEqual(estados[-3:], ["en_preparacion", "en_ruta", "entregado"])

    def test_un_pedido_en_xml(self):
        lineas = "".join(f"<linea><producto_id>{l['producto_id']}</producto_id><cantidad>{l['cantidad']}</cantidad></linea>" for l in self.lineas())
        cliente = uno("SELECT c.id FROM cliente c JOIN usuario u ON u.id = c.usuario_id WHERE u.correo = 'juan.chapa1@correo.mx'")["id"]
        cuerpo = f'<pedido_nuevo xmlns="urn:microhubs:v1"><cliente_id>{cliente}</cliente_id><lineas>{lineas}</lineas></pedido_nuevo>'
        _, (raiz, d) = self.adm_xml.llamar("pedidos", "POST", "pedidos", cuerpo, estado=201)
        self.assertEqual(raiz, "pedido_creado")
        self.adm.llamar("pedidos", "POST", f"pedidos/{d['id']}/estado", {"estado": "cancelado", "motivo": "Prueba XML"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
