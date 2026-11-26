"""
test_ola1.py — Los cinco servicios de la Ola 1 (inventario, precios, proveedores, abastecimiento y
notificaciones) contra PostgreSQL y Redis reales, con el modelo 01 a 09 cargado.

Los servicios se llaman entre sí como en producción (mismo JWT, misma traza), pero en proceso: el cliente
común (comun.clientes) se conecta a las aplicaciones Flask sin pasar por la red. Una prueba puede
«apagar» un servicio para ver qué hace el que depende de él.

Las pruebas cambian datos de la base de demostración y dejan cada cosa como estaba (existencias, mínimos y
preferencias); usar una base de pruebas.

  cd servicios && python -m unittest -v pruebas.test_ola1
"""
import json
import math
import os
import sys
import unittest
import uuid
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
os.environ.setdefault("LOG_STDOUT", "0")

from comun import clientes, config, datos  # noqa: E402
from pruebas.test_contrato import APPS, Cliente, NS, ejemplo, mismas_llaves  # noqa: E402

APAGADOS = set()          # servicios que la prueba hace «no responder»
LIMITE = {}


def transporte(servicio, metodo, ruta, cuerpo, params, token, traza):
    if servicio in APAGADOS:
        raise ConnectionError(f"{servicio} apagado por la prueba")
    enc = {"Accept": "application/json", "Content-Type": "application/json"}
    if token:
        enc["Authorization"] = f"Bearer {token}"
    if traza:
        enc["X-Traza-Id"] = traza
    r = APPS[servicio].test_client().open(f"/api/v1/{ruta}", method=metodo, query_string=params or None, headers=enc,
                                          data=json.dumps(cuerpo) if cuerpo is not None else None)
    return r.status_code, (r.get_json(silent=True) if r.data else None)


def setUpModule():
    clientes.usar_transporte(transporte)
    LIMITE["antes"] = config.LIMITE_POR_MINUTO
    LIMITE["login"] = config.LIMITE_LOGIN_POR_MINUTO
    config.LIMITE_POR_MINUTO = config.LIMITE_LOGIN_POR_MINUTO = 1_000_000
    for k in datos.r_cache.keys("cache:mapa:*") or []:
        datos.r_cache.delete(k)


def tearDownModule():
    clientes.usar_transporte(None)
    config.LIMITE_POR_MINUTO, config.LIMITE_LOGIN_POR_MINUTO = LIMITE["antes"], LIMITE["login"]


def uno(sql, args=()):
    return datos.consultar(sql, args, una=True)


def producto(clave):
    return uno("SELECT id, precio, categoria_id FROM producto WHERE clave_interna = %s", (clave,))


def microhub(clave):
    return uno("SELECT id FROM microhub WHERE clave = %s", (clave,))["id"]


def usuario(correo):
    return uno("SELECT id FROM usuario WHERE correo = %s", (correo,))["id"]


def centavos(valor):
    return Decimal(str(valor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._caso = unittest.TestCase()
        cls.HUB1, cls.HUB2 = microhub("MH-01"), microhub("MH-02")
        cls.adm = cls.entrar("admin@codex.mx")
        cls.op1 = cls.entrar("operador.mh01@codex.mx")
        cls.op2 = cls.entrar("operador.mh02@codex.mx")
        cls.plan = cls.entrar("planeador@codex.mx")
        cls.aud = cls.entrar("auditor@codex.mx")
        cls.cli = cls.entrar("juan.chapa1@correo.mx")
        cls.adm_xml = cls.entrar("admin@codex.mx", "xml")
        cls.op1_xml = cls.entrar("operador.mh01@codex.mx", "xml")
        cls.cli_xml = cls.entrar("juan.chapa1@correo.mx", "xml")

    @classmethod
    def entrar(cls, correo, formato="json"):
        c = Cliente(cls._caso, formato)
        c.entrar(correo)
        return c

    def setUp(self):
        for c in (self.adm, self.op1, self.op2, self.plan, self.aud, self.cli, self.adm_xml, self.op1_xml, self.cli_xml):
            c.caso = self

    def estado_http(self, cliente, servicio, metodo, ruta, cuerpo=None):
        return cliente.llamar(servicio, metodo, ruta, cuerpo)[0].status_code

    def existencia(self, hub, pid):
        r, d = self.adm.llamar("inventario", "GET", f"inventario/{hub}/{pid}")
        return d if r.status_code == 200 else {"existencia": 0, "reservado": 0, "disponible": 0, "minimo": 0}


# ====================================================================
# Inventario
# ====================================================================
class T4Inventario(Base):
    def test_lectura_por_perfil_y_formato(self):
        _, lista = self.adm.llamar("inventario", "GET", "inventario?por_pagina=5", estado=200)
        mismas_llaves(self, lista, ejemplo("InventarioLista.ok"))
        self.assertGreater(lista["paginacion"]["total"], 50)
        self.assertIsNotNone(lista["datos"][0]["producto"]["nombre"], "los nombres los pide al servicio de productos")
        self.assertIsNotNone(lista["datos"][0]["microhub"]["nombre"])
        self.adm_xml.llamar("inventario", "GET", "inventario?por_pagina=5", estado=200)
        _, mio = self.op1.llamar("inventario", "GET", "inventario?por_pagina=100", estado=200)
        self.assertEqual({e["microhub"]["id"] for e in mio["datos"]}, {self.HUB1}, "el operador solo ve su microhub")
        self.assertEqual(self.estado_http(self.op1, "inventario", "GET", f"inventario?microhub_id={self.HUB2}"), 403)
        self.assertEqual(self.estado_http(self.cli, "inventario", "GET", "inventario"), 403)
        self.assertEqual(self.estado_http(self.plan, "inventario", "GET", "inventario?por_pagina=1"), 200)
        self.assertEqual(self.estado_http(self.adm, "inventario", "GET", "inventario?estado=inventado"), 400)
        self.assertEqual(self.estado_http(Cliente(self, "json"), "inventario", "GET", "inventario"), 401)
        _, q = self.adm.llamar("inventario", "GET", f"inventario?q=arroz&microhub_id={self.HUB1}", estado=200)
        self.assertTrue(q["datos"])
        self.assertTrue(all("arroz" in (e["producto"]["nombre"] + e["producto"]["clave_interna"]).lower() for e in q["datos"]))

    def test_movimientos_y_sus_reglas(self):
        pid = producto("AB-006")["id"]
        antes = self.existencia(self.HUB1, pid)["existencia"]
        uid = str(uuid.uuid4())
        cuerpo = {"microhub_id": self.HUB1, "producto_id": pid, "tipo": "recepcion", "cantidad": 5, "motivo": "Prueba de recepción",
                  "operacion_uuid": uid, "referencia": {"tipo": "orden_compra", "id": "1"}}
        _, d = self.op1.llamar("inventario", "POST", "inventario/movimientos", cuerpo, estado=201)
        mismas_llaves(self, d, ejemplo("MovimientoRegistrado.ok"))
        self.assertEqual((d["movimiento"]["existencia_resultante"], d["duplicado"]), (antes + 5, False))
        _, repetido = self.op1.llamar("inventario", "POST", "inventario/movimientos", cuerpo, estado=200)
        self.assertTrue(repetido["duplicado"])
        self.assertEqual(self.existencia(self.HUB1, pid)["existencia"], antes + 5, "el reintento no mueve la existencia")
        otro = producto("AB-007")["id"]
        self.assertEqual(self.estado_http(self.op1, "inventario", "POST", "inventario/movimientos", {**cuerpo, "producto_id": otro}), 409,
                         "la misma operacion_uuid con otro producto es un conflicto")

        sin_motivo = {"microhub_id": self.HUB1, "producto_id": pid, "tipo": "ajuste", "cantidad": 1}
        r, e = self.op1.llamar("inventario", "POST", "inventario/movimientos", sin_motivo)
        self.assertEqual((r.status_code, e["error"]["detalles"][0]["campo"]), (422, "motivo"))
        self.assertEqual(self.estado_http(self.op1, "inventario", "POST", "inventario/movimientos",
                                          {**sin_motivo, "tipo": "merma", "cantidad": 0, "motivo": "x"}), 422)
        r, e = self.op1.llamar("inventario", "POST", "inventario/movimientos",
                               {**sin_motivo, "tipo": "merma", "cantidad": antes + 1000, "motivo": "Se cayó la tarima"})
        self.assertEqual(r.status_code, 409, "no se puede dejar la existencia en negativo")

        umbral = int(datos.parametro("umbral_ajuste_inventario", 25))
        grande = {**sin_motivo, "cantidad": umbral + 5, "motivo": "Ajuste de inventario grande"}
        self.assertEqual(self.estado_http(self.op1, "inventario", "POST", "inventario/movimientos", grande), 403,
                         "más de lo permitido lo autoriza un administrador")
        self.assertEqual(self.estado_http(self.adm, "inventario", "POST", "inventario/movimientos", grande), 201)
        self.assertEqual(self.estado_http(self.adm, "inventario", "POST", "inventario/movimientos", {**grande, "cantidad": -(umbral + 5)}), 201)

        actual = self.existencia(self.HUB1, pid)["existencia"]
        _, cnt = self.adm.llamar("inventario", "POST", "inventario/movimientos",
                                 {**sin_motivo, "tipo": "conteo", "cantidad": actual + 2, "motivo": "Conteo del turno"}, estado=201)
        self.assertEqual((cnt["movimiento"]["cantidad"], cnt["movimiento"]["tipo"]), (2, "conteo"), "el conteo registra la diferencia")
        self.assertEqual(self.estado_http(self.adm, "inventario", "POST", "inventario/movimientos",
                                          {**sin_motivo, "tipo": "conteo", "cantidad": actual + 2, "motivo": "Mismo conteo"}), 409)
        self.adm.llamar("inventario", "POST", "inventario/movimientos",
                        {**sin_motivo, "cantidad": -2, "motivo": "Se regresa el conteo de prueba"}, estado=201)

        self.assertEqual(self.estado_http(self.op1, "inventario", "POST", "inventario/movimientos", {**cuerpo, "microhub_id": self.HUB2,
                                                                                                     "operacion_uuid": str(uuid.uuid4())}), 403)
        self.assertEqual(self.estado_http(self.adm, "inventario", "POST", "inventario/movimientos",
                                          {**cuerpo, "producto_id": 999999, "operacion_uuid": str(uuid.uuid4())}), 422)
        self.assertEqual(self.estado_http(self.aud, "inventario", "POST", "inventario/movimientos", cuerpo), 403)

        _, lista = self.adm.llamar("inventario", "GET", f"inventario/movimientos?microhub_id={self.HUB1}&producto_id={pid}&tipo=recepcion",
                                   estado=200)
        mismas_llaves(self, lista, ejemplo("MovimientoLista.ok"))
        self.assertTrue(any(m["referencia"] == {"tipo": "orden_compra", "id": "1"} for m in lista["datos"]))
        self.adm_xml.llamar("inventario", "GET", f"inventario/movimientos?microhub_id={self.HUB1}", estado=200)
        self.assertEqual(self.estado_http(self.adm, "inventario", "GET", "inventario/movimientos?tipo=inventado"), 400)
        self.assertEqual(self.estado_http(self.adm, "inventario", "GET", "inventario/movimientos?desde=2026-10-02&hasta=2026-10-01"), 400)

    def test_movimiento_en_xml(self):
        pid = producto("AB-006")["id"]
        antes = self.existencia(self.HUB1, pid)["existencia"]
        cuerpo = (f'<movimiento_nuevo xmlns="{NS}"><microhub_id>{self.HUB1}</microhub_id><producto_id>{pid}</producto_id>'
                  f'<tipo>recepcion</tipo><cantidad>3</cantidad><motivo>Prueba XML</motivo></movimiento_nuevo>')
        _, (raiz, d) = self.op1_xml.llamar("inventario", "POST", "inventario/movimientos", cuerpo, estado=201)
        self.assertEqual((raiz, d["duplicado"]), ("movimiento_registrado", "false"))
        self.adm.llamar("inventario", "POST", "inventario/movimientos",
                        {"microhub_id": self.HUB1, "producto_id": pid, "tipo": "merma", "cantidad": 3, "motivo": "Se regresa la prueba XML"},
                        estado=201)
        self.assertEqual(self.existencia(self.HUB1, pid)["existencia"], antes)

    def test_transferencia_entre_microhubs(self):
        pid = producto("AB-007")["id"]
        ao, ad = self.existencia(self.HUB1, pid)["existencia"], self.existencia(self.HUB2, pid)["existencia"]
        uid = str(uuid.uuid4())
        cuerpo = {"origen_microhub_id": self.HUB1, "destino_microhub_id": self.HUB2, "producto_id": pid, "cantidad": 2,
                  "motivo": "El microhub 2 se quedó sin producto", "operacion_uuid": uid}
        _, t = self.adm.llamar("inventario", "POST", "inventario/transferencias", cuerpo, estado=201)
        mismas_llaves(self, t, ejemplo("Transferencia.ok"))
        self.assertEqual((t["origen"]["existencia"], t["destino"]["existencia"]), (ao - 2, ad + 2))
        _, dup = self.adm.llamar("inventario", "POST", "inventario/transferencias", cuerpo, estado=200)
        self.assertTrue(dup["duplicado"])
        self.assertEqual((self.existencia(self.HUB1, pid)["existencia"], self.existencia(self.HUB2, pid)["existencia"]), (ao - 2, ad + 2))
        movs = datos.consultar("SELECT tipo::text AS tipo, cantidad FROM movimiento_inventario WHERE operacion_uuid LIKE %s ORDER BY id",
                               (uid + ":%",))
        self.assertEqual([(m["tipo"], m["cantidad"]) for m in movs], [("transferencia_salida", -2), ("transferencia_entrada", 2)])
        self.assertEqual(self.estado_http(self.adm, "inventario", "POST", "inventario/transferencias",
                                          {**cuerpo, "destino_microhub_id": self.HUB1, "operacion_uuid": str(uuid.uuid4())}), 422)
        self.assertEqual(self.estado_http(self.adm, "inventario", "POST", "inventario/transferencias",
                                          {**cuerpo, "cantidad": ao + 1000, "operacion_uuid": str(uuid.uuid4())}), 409)
        self.assertEqual(self.estado_http(self.op2, "inventario", "POST", "inventario/transferencias",
                                          {**cuerpo, "operacion_uuid": str(uuid.uuid4())}), 403, "solo se manda desde el propio microhub")
        # de regreso, y ahora en XML
        xml = (f'<transferencia_nueva xmlns="{NS}"><origen_microhub_id>{self.HUB2}</origen_microhub_id>'
               f'<destino_microhub_id>{self.HUB1}</destino_microhub_id><producto_id>{pid}</producto_id><cantidad>2</cantidad>'
               f'<motivo>Se regresa la transferencia de prueba</motivo></transferencia_nueva>')
        _, (raiz, _) = self.adm_xml.llamar("inventario", "POST", "inventario/transferencias", xml, estado=201)
        self.assertEqual(raiz, "transferencia")
        self.assertEqual((self.existencia(self.HUB1, pid)["existencia"], self.existencia(self.HUB2, pid)["existencia"]), (ao, ad))

    def test_reservas(self):
        pid = producto("AB-008")["id"]
        base = self.existencia(self.HUB1, pid)
        ref = {"tipo": "manual", "id": "prueba-" + uuid.uuid4().hex[:8]}
        _, res = self.op1.llamar("inventario", "POST", "inventario/reservas",
                                 {"microhub_id": self.HUB1, "producto_id": pid, "cantidad": 3, "referencia": ref}, estado=201)
        mismas_llaves(self, res, ejemplo("Reserva.ok"))
        self.assertEqual((res["estado"], res["vigente"], res["referencia"]), ("activa", True, ref))
        ahora = self.existencia(self.HUB1, pid)
        self.assertEqual((ahora["existencia"], ahora["reservado"], ahora["disponible"]),
                         (base["existencia"], base["reservado"] + 3, base["disponible"] - 3))
        r, e = self.op1.llamar("inventario", "POST", "inventario/reservas",
                               {"microhub_id": self.HUB1, "producto_id": pid, "cantidad": base["disponible"] + 100, "referencia": ref})
        self.assertEqual((r.status_code, e["error"]["codigo"]), (409, "CONFLICTO"))
        self.assertEqual(self.estado_http(self.op1, "inventario", "POST", "inventario/reservas",
                                          {"microhub_id": self.HUB1, "producto_id": pid, "cantidad": 1, "referencia": {"tipo": "otro", "id": "1"}}), 422)
        _, lista = self.adm.llamar("inventario", "GET", f"inventario/reservas?producto_id={pid}&estado=activa&referencia_id={ref['id']}", estado=200)
        mismas_llaves(self, lista, ejemplo("ReservaLista.ok"))
        self.assertEqual([r["id"] for r in lista["datos"]], [res["id"]])
        self.adm_xml.llamar("inventario", "GET", f"inventario/reservas?producto_id={pid}", estado=200)
        self.assertEqual(self.estado_http(self.op2, "inventario", "POST", f"inventario/reservas/{res['id']}/liberar"), 403)
        _, libre = self.op1.llamar("inventario", "POST", f"inventario/reservas/{res['id']}/liberar", estado=200)
        self.assertEqual((libre["estado"], libre["vigente"]), ("liberada", False))
        self.assertEqual(self.estado_http(self.op1, "inventario", "POST", f"inventario/reservas/{res['id']}/liberar"), 409)
        self.assertEqual(self.estado_http(self.op1, "inventario", "POST", "inventario/reservas/999999/liberar"), 404)
        self.assertEqual(self.existencia(self.HUB1, pid)["disponible"], base["disponible"])

    def test_cancelar_un_pedido_libera_su_reserva(self):
        f = uno("SELECT id FROM pedido WHERE estado IN ('pendiente_asignacion', 'creado', 'asignado') ORDER BY (estado = 'asignado'), id DESC LIMIT 1")
        if not f:
            self.skipTest("no hay un pedido cancelable en la base de demostración")
        pid = producto("AB-008")["id"]
        _, res = self.adm.llamar("inventario", "POST", "inventario/reservas",
                                 {"microhub_id": self.HUB1, "producto_id": pid, "cantidad": 1,
                                  "referencia": {"tipo": "pedido", "id": str(f["id"])}}, estado=201)
        self.adm.llamar("pedidos", "POST", f"pedidos/{f['id']}/estado", {"estado": "cancelado", "motivo": "Prueba de la reserva ligada al pedido"},
                        estado=200)
        _, lista = self.adm.llamar("inventario", "GET", f"inventario/reservas?referencia_tipo=pedido&referencia_id={f['id']}", estado=200)
        self.assertEqual([(r["id"], r["estado"]) for r in lista["datos"] if r["id"] == res["id"]], [(res["id"], "liberada")],
                         "el trigger libera la reserva cuando el pedido se cancela")

    def test_minimo_alertas_y_aviso_de_faltante(self):
        pid = producto("AB-009")["id"]
        e = self.existencia(self.HUB1, pid)
        original = e["minimo"]
        op_id = usuario("operador.mh01@codex.mx")
        try:
            self.assertEqual(self.estado_http(self.op1, "inventario", "PATCH", f"inventario/{self.HUB1}/{pid}/minimo", {"minimo": 5}), 403)
            self.assertEqual(self.estado_http(self.adm, "inventario", "PATCH", f"inventario/{self.HUB1}/{pid}/minimo", {"minimo": -1}), 422)
            self.adm.llamar("inventario", "PATCH", f"inventario/{self.HUB1}/{pid}/minimo", {"minimo": e["existencia"] - 1}, estado=200)
            avisos = lambda: uno("SELECT count(*) AS n FROM web_notificacion WHERE destinatario_id = %s AND tipo = 'inventario'", (op_id,))["n"]
            antes = avisos()
            self.adm.llamar("inventario", "POST", "inventario/movimientos",
                            {"microhub_id": self.HUB1, "producto_id": pid, "tipo": "merma", "cantidad": 2, "motivo": "Se rompieron dos"}, estado=201)
            self.assertEqual(avisos(), antes + 1, "al cruzar el mínimo el trigger avisa al operador del microhub")
            _, al = self.adm.llamar("inventario", "GET", f"inventario/alertas?microhub_id={self.HUB1}&por_pagina=100", estado=200)
            mismas_llaves(self, al, ejemplo("AlertaLista.ok"))
            fila = next(a for a in al["datos"] if a["producto"]["id"] == pid)
            self.assertEqual((fila["faltante"], fila["disponible"]), (1, e["existencia"] - 2))
            self.assertEqual(fila["severidad"], "baja")
            self.assertTrue(all(a["microhub"]["id"] == self.HUB1 for a in al["datos"]))
            self.adm_xml.llamar("inventario", "GET", f"inventario/alertas?microhub_id={self.HUB1}", estado=200)
            _, solo = self.adm.llamar("inventario", "GET", f"inventario/alertas?severidad=agotado&por_pagina=100", estado=200)
            self.assertTrue(all(a["severidad"] == "agotado" for a in solo["datos"]))
        finally:
            self.adm.llamar("inventario", "PATCH", f"inventario/{self.HUB1}/{pid}/minimo", {"minimo": original})
            actual = self.existencia(self.HUB1, pid)["existencia"]
            if actual < e["existencia"]:
                self.adm.llamar("inventario", "POST", "inventario/movimientos",
                                {"microhub_id": self.HUB1, "producto_id": pid, "tipo": "recepcion", "cantidad": e["existencia"] - actual})


# ====================================================================
# Notificaciones
# ====================================================================
class T5Notificaciones(Base):
    def test_bandeja_envio_y_lectura(self):
        marca = "Prueba " + uuid.uuid4().hex[:8]
        _, env = self.adm.llamar("notificaciones", "POST", "notificaciones",
                                 {"rol": "operador", "microhub_id": self.HUB1, "tipo": "sistema", "titulo": marca, "mensaje": "Aviso de prueba",
                                  "referencia": {"tipo": "sistema", "id": "x"}}, estado=201)
        mismas_llaves(self, env, ejemplo("Envio.ok"))
        self.assertEqual((env["enviadas"], env["omitidas"], len(env["ids"])), (1, 0, 1))
        _, b = self.op1.llamar("notificaciones", "GET", "notificaciones?solo_no_leidas=true&por_pagina=100", estado=200)
        mismas_llaves(self, b, ejemplo("NotificacionLista.ok"))
        aviso = next(a for a in b["datos"] if a["titulo"] == marca)
        self.assertEqual((aviso["leida"], aviso["tipo"], aviso["referencia"]), (False, "sistema", {"tipo": "sistema", "id": "x"}))
        _, otra = self.op2.llamar("notificaciones", "GET", "notificaciones?por_pagina=100", estado=200)
        self.assertNotIn(marca, [a["titulo"] for a in otra["datos"]], "el aviso solo llega a quien va dirigido")
        self.op1_xml.llamar("notificaciones", "GET", "notificaciones?por_pagina=5", estado=200)

        _, c0 = self.op1.llamar("notificaciones", "GET", "notificaciones/conteo", estado=200)
        mismas_llaves(self, c0, ejemplo("Conteo.ok"))
        self.assertEqual(self.estado_http(self.op2, "notificaciones", "POST", f"notificaciones/{aviso['id']}/leer"), 404)
        _, leido = self.op1.llamar("notificaciones", "POST", f"notificaciones/{aviso['id']}/leer", estado=200)
        mismas_llaves(self, leido, ejemplo("Notificacion.ok"))
        self.assertTrue(leido["leida"])
        _, c1 = self.op1.llamar("notificaciones", "GET", "notificaciones/conteo", estado=200)
        self.assertEqual(c1["no_leidas"], c0["no_leidas"] - 1)
        _, todas = self.op1.llamar("notificaciones", "POST", "notificaciones/leer-todas", estado=200)
        mismas_llaves(self, todas, ejemplo("Lectura.ok"))
        self.assertEqual(self.op1.llamar("notificaciones", "GET", "notificaciones/conteo")[1]["no_leidas"], 0)
        _, por_tipo = self.op1.llamar("notificaciones", "GET", "notificaciones?tipo=sistema&por_pagina=100", estado=200)
        self.assertTrue(all(a["tipo"] == "sistema" for a in por_tipo["datos"]))
        self.assertEqual(self.estado_http(self.op1, "notificaciones", "GET", "notificaciones?tipo=inventado"), 400)
        self.assertEqual(self.estado_http(self.op1, "notificaciones", "GET", "notificaciones?solo_no_leidas=quizas"), 400)
        self.assertEqual(self.estado_http(self.op1, "notificaciones", "DELETE", f"notificaciones/{aviso['id']}"), 204)
        self.assertEqual(self.estado_http(self.op1, "notificaciones", "DELETE", f"notificaciones/{aviso['id']}"), 404)

    def test_las_preferencias_se_respetan(self):
        _, antes = self.op1.llamar("notificaciones", "GET", "notificaciones/preferencias", estado=200)
        mismas_llaves(self, antes, ejemplo("Preferencias.ok"))
        self.assertEqual([p["tipo"] for p in antes["datos"]], ["pedido", "entrega", "planeacion", "inventario", "abastecimiento"])
        self.op1_xml.llamar("notificaciones", "GET", "notificaciones/preferencias", estado=200)
        try:
            _, p = self.op1.llamar("notificaciones", "PUT", "notificaciones/preferencias/inventario", {"activa": False}, estado=200)
            mismas_llaves(self, p, ejemplo("Preferencia.ok"))
            self.assertEqual(p, {"tipo": "inventario", "activa": False})
            marca = "Prueba " + uuid.uuid4().hex[:8]
            _, env = self.adm.llamar("notificaciones", "POST", "notificaciones",
                                     {"rol": "operador", "microhub_id": self.HUB1, "tipo": "inventario", "titulo": marca, "mensaje": "Faltante"},
                                     estado=200)
            self.assertEqual((env["enviadas"], env["omitidas"]), (0, 1), "quien apagó el tipo no lo recibe")
            self.assertEqual(self.estado_http(self.adm, "notificaciones", "POST", "notificaciones",
                                              {"rol": "operador", "microhub_id": self.HUB1, "tipo": "sistema", "titulo": marca, "mensaje": "Sistema"}), 201)
            self.assertEqual(self.estado_http(self.op1, "notificaciones", "PUT", "notificaciones/preferencias/sistema", {"activa": False}), 409)
            self.assertEqual(self.estado_http(self.op1, "notificaciones", "PUT", "notificaciones/preferencias/inventado", {"activa": False}), 404)
            self.assertEqual(self.estado_http(self.op1, "notificaciones", "PUT", "notificaciones/preferencias/pedido", {}), 422)
        finally:
            self.op1.llamar("notificaciones", "PUT", "notificaciones/preferencias/inventario", {"activa": True})
        _, despues = self.op1.llamar("notificaciones", "GET", "notificaciones/preferencias", estado=200)
        self.assertTrue(all(p["activa"] for p in despues["datos"]))

    def test_permisos_y_validacion_del_envio(self):
        base = {"tipo": "sistema", "titulo": "Prueba", "mensaje": "Texto"}
        self.assertEqual(self.estado_http(self.op1, "notificaciones", "POST", "notificaciones", {**base, "rol": "operador"}), 403)
        for cuerpo in ({**base}, {**base, "rol": "operador", "usuario_id": 1}, {**base, "usuario_id": 999999}, {**base, "rol": "no_existe"},
                       {**base, "usuario_id": 1, "tipo": "inventado"}, {**base, "usuario_id": 1, "microhub_id": 1}):
            with self.subTest(cuerpo):
                self.assertEqual(self.estado_http(self.adm, "notificaciones", "POST", "notificaciones", cuerpo), 422)
        self.assertEqual(self.estado_http(Cliente(self, "json"), "notificaciones", "GET", "notificaciones"), 401)


# ====================================================================
# Precios
# ====================================================================
class T6Precios(Base):
    def test_la_fecha_de_hoy_es_la_de_monterrey_y_no_la_utc(self):
        """PostgreSQL trabaja en UTC: desde las 6 de la tarde current_date ya es «mañana» en Monterrey."""
        import datetime as dt
        from comun.formatos import ZONA
        self.assertEqual(uno("SELECT fn_hoy() AS d")["d"], dt.datetime.now(ZONA).date())
        v = uno("SELECT vigente_desde FROM lista_precio WHERE nombre = 'Lista San Bernabé Centro'")["vigente_desde"]
        self.assertLessEqual(v, dt.datetime.now(ZONA).date(), "la lista sembrada ya rige hoy")

    def test_listas_y_permisos(self):
        _, listas = self.plan.llamar("precios", "GET", "precios/listas", estado=200)
        mismas_llaves(self, listas, ejemplo("ListaLista.ok"))
        self.assertGreaterEqual(listas["paginacion"]["total"], 1)
        self.adm_xml.llamar("precios", "GET", "precios/listas", estado=200)
        self.assertEqual(self.estado_http(self.aud, "precios", "GET", "precios/listas"), 200)
        self.assertEqual(self.estado_http(self.cli, "precios", "GET", "precios/listas"), 403, "el cliente no ve las listas")
        self.assertEqual(self.estado_http(self.adm, "precios", "GET", "precios/listas?estatus=inventado"), 400)
        _, vigentes = self.adm.llamar("precios", "GET", "precios/listas?vigente=true", estado=200)
        self.assertTrue(all(l["estatus"] == "activo" for l in vigentes["datos"]))

    def test_crear_una_lista_cambiar_precios_y_ver_el_historial(self):
        nombre = "Lista de prueba " + uuid.uuid4().hex[:8]
        pid = producto("AB-002")["id"]
        zona = 3
        cuerpo = {"nombre": nombre, "zona_id": zona, "vigente_desde": "2027-01-01", "vigente_hasta": "2027-01-31",
                  "items": [{"producto_id": pid, "precio": 50.0, "costo": 30.0}]}
        try:
            _, d = self.adm.llamar("precios", "POST", "precios/listas", cuerpo, estado=201)
            mismas_llaves(self, d, ejemplo("ListaDetalle.ok"))
            lid = d["id"]
            self.assertEqual((d["productos"], d["items"][0]["margen_pct"]), (1, 40.0))
            r, e = self.adm.llamar("precios", "POST", "precios/listas", {**cuerpo, "nombre": nombre + " bis", "vigente_desde": "2027-01-15",
                                                                             "vigente_hasta": "2027-02-15"})
            self.assertEqual(r.status_code, 409, "dos listas de la misma zona no pueden traslaparse")
            self.assertEqual(self.estado_http(self.adm, "precios", "POST", "precios/listas", {**cuerpo, "nombre": nombre + " fechas",
                                                                                              "vigente_hasta": "2026-12-31"}), 422)
            self.assertEqual(self.estado_http(self.adm, "precios", "POST", "precios/listas", {**cuerpo, "nombre": "ab"}), 422)
            self.assertEqual(self.estado_http(self.adm, "precios", "POST", "precios/listas", {"nombre": nombre + " zona", "zona_id": 99999}), 422)
            self.assertEqual(self.estado_http(self.plan, "precios", "POST", "precios/listas", {**cuerpo, "nombre": nombre + " x"}), 403)

            _, item = self.adm.llamar("precios", "PUT", f"precios/listas/{lid}/items/{pid}", {"precio": 52.0}, estado=200)
            mismas_llaves(self, item, ejemplo("ItemPrecio.ok"))
            self.assertEqual((item["precio"], item["costo"], item["margen_pct"]), (52.0, 30.0, 42.3), "sin costo en el cuerpo, se conserva el costo")
            _, h = self.adm.llamar("precios", "GET", f"precios/historial?lista_id={lid}&producto_id={pid}", estado=200)
            mismas_llaves(self, h, ejemplo("HistorialLista.ok"))
            self.assertEqual([(c["precio_anterior"], c["precio_nuevo"]) for c in h["datos"]], [(50.0, 52.0), (None, 50.0)])
            self.adm_xml.llamar("precios", "GET", f"precios/historial?lista_id={lid}", estado=200)
            self.assertEqual(self.estado_http(self.adm, "precios", "PUT", f"precios/listas/{lid}/items/{pid}", {"precio": 0}), 422)
            self.assertEqual(self.estado_http(self.adm, "precios", "PUT", f"precios/listas/999999/items/{pid}", {"precio": 5}), 404)
            self.assertEqual(self.estado_http(self.plan, "precios", "PUT", f"precios/listas/{lid}/items/{pid}", {"precio": 5}), 403)
            self.assertEqual(self.estado_http(self.adm, "precios", "PUT", f"precios/listas/{lid}/items/999999", {"precio": 5}), 422)

            _, uno = self.plan.llamar("precios", "GET", f"precios/listas/{lid}", estado=200)
            self.assertEqual(uno["items"][0]["precio"], 52.0)
            self.assertEqual(self.estado_http(self.plan, "precios", "GET", "precios/listas/999999"), 404)
            _, dentro = self.cli.llamar("precios", "GET", f"precios/vigente?producto_id={pid}&zona_id={zona}&fecha=2027-01-15", estado=200)
            self.assertEqual((dentro["precio_vigente"], dentro["lista"]["id"]), (52.0, lid))
            _, fuera = self.cli.llamar("precios", "GET", f"precios/vigente?producto_id={pid}&zona_id={zona}&fecha=2026-10-19", estado=200)
            self.assertIsNone(fuera["lista"])
            self.assertEqual(fuera["precio_vigente"], fuera["precio_base"], "fuera de las fechas rige el precio base")
        finally:
            datos.consultar("UPDATE lista_precio SET estatus = 'inactivo' WHERE nombre LIKE %s RETURNING id", (nombre + "%",))

    def test_precio_vigente_calculo_y_promociones(self):
        ab, be = producto("AB-001"), producto("BE-001")
        zona = uno("SELECT id FROM zona WHERE clave = 'ZN-SB01'")["id"]
        _, v = self.cli.llamar("precios", "GET", f"precios/vigente?producto_id={ab['id']}&zona_id={zona}", estado=200)
        mismas_llaves(self, v, ejemplo("PrecioVigente.ok"), opcionales=())
        self.assertEqual(centavos(v["precio_vigente"]), centavos(Decimal(str(ab["precio"])) * Decimal("1.03")), "rige la lista de la zona")
        self.assertEqual(v["lista"]["nombre"], "Lista San Bernabé Centro")
        self.cli_xml.llamar("precios", "GET", f"precios/vigente?producto_id={ab['id']}&zona_id={zona}", estado=200)
        _, b = self.cli.llamar("precios", "GET", f"precios/vigente?producto_id={be['id']}&zona_id={zona}", estado=200)
        self.assertEqual(b["promocion"]["nombre"], "Bebidas -10 %")
        self.assertEqual(centavos(b["descuento"]), centavos(Decimal(str(be["precio"])) * Decimal("0.10")))
        self.assertEqual(centavos(b["precio_final"]), centavos(b["precio_vigente"]) - centavos(b["descuento"]))
        self.assertEqual(self.estado_http(self.cli, "precios", "GET", "precios/vigente"), 400)
        self.assertEqual(self.estado_http(self.cli, "precios", "GET", "precios/vigente?producto_id=999999"), 404)
        self.assertEqual(self.estado_http(self.cli, "precios", "GET", f"precios/vigente?producto_id={ab['id']}&fecha=2026-13-40"), 400)

        cuerpo = {"zona_id": zona, "lineas": [{"producto_id": ab["id"], "cantidad": 2}, {"producto_id": be["id"], "cantidad": 3}]}
        _, c = self.cli.llamar("precios", "POST", "precios/calcular", cuerpo, estado=200)
        mismas_llaves(self, c, ejemplo("Calculo.ok"))
        self.assertEqual(sum(centavos(l["importe"]) for l in c["lineas"]), centavos(c["total"]))
        self.assertEqual(centavos(c["subtotal"]) - centavos(c["descuento_total"]), centavos(c["total"]))
        self.assertEqual(c["lineas"][1]["promocion_id"], b["promocion"]["id"])
        for malo in ({"lineas": []}, {"lineas": [{"producto_id": 999999, "cantidad": 1}]}, {"lineas": [{"producto_id": ab["id"], "cantidad": 0}]}):
            self.assertEqual(self.estado_http(self.cli, "precios", "POST", "precios/calcular", malo), 422)

        nombre = "Promoción de prueba " + uuid.uuid4().hex[:8]
        nueva = {"nombre": nombre, "tipo": "monto", "valor": 2.0, "producto_id": ab["id"], "vigente_hasta": "2030-12-31"}
        pid = None
        try:
            self.assertEqual(self.estado_http(self.adm, "precios", "POST", "precios/promociones",
                                              {**nueva, "tipo": "porcentaje", "valor": 31.0}), 422, "pasa del descuento máximo")
            self.assertEqual(self.estado_http(self.adm, "precios", "POST", "precios/promociones", {**nueva, "categoria_id": ab["categoria_id"]}), 422)
            self.assertEqual(self.estado_http(self.adm, "precios", "POST", "precios/promociones", {**nueva, "vigente_hasta": "2020-01-01"}), 422)
            self.assertEqual(self.estado_http(self.plan, "precios", "POST", "precios/promociones", nueva), 403)
            _, p = self.adm.llamar("precios", "POST", "precios/promociones", nueva, estado=201)
            mismas_llaves(self, p, ejemplo("Promocion.ok"))
            pid = p["id"]
            _, ls = self.plan.llamar("precios", "GET", f"precios/promociones?vigente=true&producto_id={ab['id']}", estado=200)
            mismas_llaves(self, ls, ejemplo("PromocionLista.ok"))
            self.assertIn(pid, [x["id"] for x in ls["datos"]])
            _, con = self.cli.llamar("precios", "GET", f"precios/vigente?producto_id={ab['id']}&zona_id={zona}", estado=200)
            self.assertEqual((con["promocion"]["id"], centavos(con["descuento"])), (pid, centavos(2)))
            self.adm_xml.llamar("precios", "GET", "precios/promociones", estado=200)
        finally:
            if pid:
                self.assertEqual(self.estado_http(self.adm, "precios", "DELETE", f"precios/promociones/{pid}"), 204)
        self.assertEqual(self.estado_http(self.adm, "precios", "DELETE", "precios/promociones/999999"), 404)
        _, despues = self.cli.llamar("precios", "GET", f"precios/vigente?producto_id={ab['id']}&zona_id={zona}", estado=200)
        self.assertIsNone(despues["promocion"], "una promoción dada de baja ya no se aplica")

    def test_margenes_y_sensibilidad(self):
        _, m = self.plan.llamar("precios", "GET", "precios/margenes?por_pagina=5", estado=200)
        mismas_llaves(self, m, ejemplo("MargenLista.ok"))
        self.assertTrue(m["datos"])
        margenes = [x["margen_pct"] for x in m["datos"]]
        self.assertEqual(margenes, sorted(margenes), "del margen más bajo al más alto")
        self.adm_xml.llamar("precios", "GET", "precios/margenes?solo_bajos=true", estado=200)
        _, bajos = self.adm.llamar("precios", "GET", "precios/margenes?solo_bajos=true&por_pagina=100", estado=200)
        self.assertTrue(all(x["bajo_margen"] for x in bajos["datos"]))

        ab = producto("AB-001")["id"]
        zona = uno("SELECT id FROM zona WHERE clave = 'ZN-SB01'")["id"]
        _, s = self.plan.llamar("precios", "GET", f"precios/sensibilidad?producto_id={ab}&zona_id={zona}&volumen_base=100&elasticidad=-1.2", estado=200)
        mismas_llaves(self, s, ejemplo("Sensibilidad.ok"))
        self.assertEqual([e["variacion_pct"] for e in s["escenarios"]], [-20, -10, -5, 5, 10, 20])
        subida = next(e for e in s["escenarios"] if e["variacion_pct"] == 10)
        self.assertEqual(subida["volumen_estimado"], 88.0)
        self.assertEqual(centavos(subida["precio"]), centavos(Decimal(str(s["precio_final"])) * Decimal("1.1")))
        self.assertIn("supuesto", s["supuestos"])
        self.adm_xml.llamar("precios", "GET", f"precios/sensibilidad?producto_id={ab}&zona_id={zona}", estado=200)
        for mala in ("", f"?producto_id={ab}&elasticidad=1", f"?producto_id={ab}&elasticidad=abc", f"?producto_id={ab}&volumen_base=0"):
            self.assertEqual(self.estado_http(self.plan, "precios", "GET", f"precios/sensibilidad{mala}"), 400, mala)
        self.assertEqual(self.estado_http(self.plan, "precios", "GET", "precios/sensibilidad?producto_id=999999"), 404)
        self.assertEqual(self.estado_http(self.cli, "precios", "GET", f"precios/sensibilidad?producto_id={ab}"), 403)
        self.assertEqual(self.estado_http(self.adm, "precios", "GET", "precios/historial?desde=2026-10-02&hasta=2026-10-01"), 400)


# ====================================================================
# Proveedores
# ====================================================================
class T7Proveedores(Base):
    def test_consulta(self):
        _, l = self.plan.llamar("proveedores", "GET", "proveedores?por_pagina=10", estado=200)
        mismas_llaves(self, l, ejemplo("ProveedorLista.ok"))
        self.assertGreaterEqual(l["paginacion"]["total"], 3)
        self.adm_xml.llamar("proveedores", "GET", "proveedores?por_pagina=10", estado=200)
        self.assertEqual(self.estado_http(self.cli, "proveedores", "GET", "proveedores"), 403)
        self.assertEqual(self.estado_http(self.adm, "proveedores", "GET", "proveedores?estatus=inventado"), 400)
        _, regia = self.adm.llamar("proveedores", "GET", "proveedores?q=regia", estado=200)
        self.assertEqual([p["clave"] for p in regia["datos"]], ["PV-02"])
        _, zona = self.adm.llamar("proveedores", "GET", "proveedores?zona_id=1", estado=200)
        self.assertGreaterEqual(len(zona["datos"]), 3)
        pv = regia["datos"][0]
        _, uno_ = self.op1.llamar("proveedores", "GET", f"proveedores/{pv['id']}", estado=200)
        mismas_llaves(self, uno_, ejemplo("Proveedor.ok"))
        self.assertEqual(self.estado_http(self.op1, "proveedores", "GET", "proveedores/999999"), 404)
        _, cat = self.op1.llamar("proveedores", "GET", f"proveedores/{pv['id']}/catalogo?por_pagina=5", estado=200)
        mismas_llaves(self, cat, ejemplo("CatalogoLista.ok"))
        self.assertIsNotNone(cat["datos"][0]["producto"]["nombre"])
        _, ev = self.op1.llamar("proveedores", "GET", f"proveedores/{pv['id']}/evaluaciones", estado=200)
        mismas_llaves(self, ev, ejemplo("EvaluacionLista.ok"))
        self.assertIsNotNone(ev["promedio"]["general"])
        self.adm_xml.llamar("proveedores", "GET", f"proveedores/{pv['id']}/catalogo", estado=200)
        self.adm_xml.llamar("proveedores", "GET", f"proveedores/{pv['id']}/evaluaciones", estado=200)

    def test_ofertas_de_la_mas_barata_a_la_mas_cara(self):
        p3 = uno("SELECT id FROM producto WHERE id %% 3 = 0 ORDER BY id LIMIT 1")["id"]
        _, o = self.op1.llamar("proveedores", "GET", f"proveedores/ofertas?producto_id={p3}", estado=200)
        mismas_llaves(self, o, ejemplo("OfertaLista.ok"))
        precios = [x["precio_compra"] for x in o["datos"]]
        self.assertGreaterEqual(len(precios), 2)
        self.assertEqual(precios, sorted(precios))
        _, mejor = self.op1.llamar("proveedores", "GET", f"proveedores/ofertas?producto_id={p3}&mejor=true", estado=200)
        self.assertEqual([x["proveedor"]["clave"] for x in mejor["datos"]], ["PV-03"], "PV-03 vende al 68 % del precio")
        p1 = producto("AB-001")["id"]
        _, varios = self.op1.llamar("proveedores", "GET", f"proveedores/ofertas?producto_ids={p1},{p3}&mejor=true", estado=200)
        self.assertEqual(sorted(x["producto"]["id"] for x in varios["datos"]), sorted([p1, p3]))
        self.adm_xml.llamar("proveedores", "GET", f"proveedores/ofertas?producto_id={p3}", estado=200)
        _, zona = self.op1.llamar("proveedores", "GET", f"proveedores/ofertas?producto_id={p3}&zona_id=1", estado=200)
        self.assertTrue(zona["datos"])
        for mala in ("", "?producto_ids=a,b", "?producto_ids=" + ",".join(str(i) for i in range(1, 102))):
            self.assertEqual(self.estado_http(self.op1, "proveedores", "GET", f"proveedores/ofertas{mala}"), 400, mala)
        self.assertEqual(self.estado_http(self.cli, "proveedores", "GET", f"proveedores/ofertas?producto_id={p3}"), 403)

    def test_alta_modificacion_oferta_y_baja(self):
        clave = "T-" + uuid.uuid4().hex[:8].upper()
        pid = producto("AB-003")["id"]
        nuevo = {"clave": clave, "nombre": "Proveedor de prueba", "contacto": "Ana Prueba", "correo": "ana@prueba.example", "telefono": "8180000000",
                 "dias_entrega": 3, "pedido_minimo": 250.0, "condiciones_pago": "Contado", "zonas": [1, 2]}
        _, p = self.adm.llamar("proveedores", "POST", "proveedores", nuevo, estado=201)
        mismas_llaves(self, p, ejemplo("Proveedor.ok"))
        self.assertEqual((p["zonas"], p["evaluaciones"], p["calificacion"], p["estatus"]), ([1, 2], 0, None, "activo"))
        sid = p["id"]
        try:
            self.assertEqual(self.estado_http(self.adm, "proveedores", "POST", "proveedores", nuevo), 409)
            self.assertEqual(self.estado_http(self.adm, "proveedores", "POST", "proveedores", {**nuevo, "clave": clave + "1", "correo": "sin-arroba"}), 422)
            self.assertEqual(self.estado_http(self.adm, "proveedores", "POST", "proveedores", {**nuevo, "clave": clave + "2", "zonas": [99999]}), 422)
            self.assertEqual(self.estado_http(self.plan, "proveedores", "POST", "proveedores", {**nuevo, "clave": clave + "3"}), 403)

            _, m = self.adm.llamar("proveedores", "PUT", f"proveedores/{sid}", {"dias_entrega": 5, "zonas": [3]}, estado=200)
            self.assertEqual((m["dias_entrega"], m["zonas"], m["nombre"]), (5, [3], "Proveedor de prueba"))
            _, m2 = self.adm.llamar("proveedores", "PATCH", f"proveedores/{sid}", {"contacto": None}, estado=200)
            self.assertIsNone(m2["contacto"])
            self.assertEqual(self.estado_http(self.adm, "proveedores", "PUT", f"proveedores/{sid}", {"clave": "OTRA"}), 409)
            self.assertEqual(self.estado_http(self.adm, "proveedores", "PUT", f"proveedores/{sid}", {}), 422)
            self.assertEqual(self.estado_http(self.adm, "proveedores", "PUT", "proveedores/999999", {"nombre": "Otro nombre"}), 404)

            oferta = {"precio_compra": 0.5, "capacidad_semanal": 100, "minimo_compra": 5, "unidad_compra": "caja"}
            _, it = self.adm.llamar("proveedores", "PUT", f"proveedores/{sid}/catalogo/{pid}", oferta, estado=200)
            mismas_llaves(self, it, ejemplo("ItemCatalogo.ok"))
            self.assertEqual((it["precio_compra"], it["unidad_compra"]), (0.5, "caja"))
            _, it2 = self.adm.llamar("proveedores", "PUT", f"proveedores/{sid}/catalogo/{pid}", {**oferta, "precio_compra": 0.05}, estado=200)
            self.assertEqual(it2["precio_compra"], 0.05, "la misma oferta se actualiza, no se duplica")
            self.assertEqual(self.estado_http(self.adm, "proveedores", "PUT", f"proveedores/{sid}/catalogo/999999", oferta), 422)
            self.assertEqual(self.estado_http(self.adm, "proveedores", "PUT", f"proveedores/{sid}/catalogo/{pid}", {**oferta, "precio_compra": 0}), 422)
            self.assertEqual(self.estado_http(self.adm, "proveedores", "PUT", f"proveedores/{sid}/catalogo/{pid}",
                                              {**oferta, "vigente_hasta": "2026-02-31"}), 422)
            _, of = self.op1.llamar("proveedores", "GET", f"proveedores/ofertas?producto_id={pid}&mejor=true", estado=200)
            self.assertEqual(of["datos"][0]["proveedor"]["id"], sid, "5 centavos es la oferta más barata de ese producto")
            xml = (f'<proveedor_nuevo xmlns="{NS}"><clave>{clave}X</clave><nombre>Proveedor en XML</nombre><dias_entrega>2</dias_entrega>'
                   f'<zonas><zona_id>1</zona_id></zonas></proveedor_nuevo>')
            _, (raiz, px) = self.adm_xml.llamar("proveedores", "POST", "proveedores", xml, estado=201)
            self.assertEqual(raiz, "proveedor")
            datos.consultar("UPDATE proveedor SET estatus = 'inactivo' WHERE clave = %s RETURNING id", (clave + "X",))
        finally:
            self.assertEqual(self.estado_http(self.adm, "proveedores", "DELETE", f"proveedores/{sid}"), 204)
        self.assertEqual(self.estado_http(self.adm, "proveedores", "DELETE", "proveedores/999999"), 404)
        _, baja = self.adm.llamar("proveedores", "GET", f"proveedores/{sid}", estado=200)
        self.assertEqual(baja["estatus"], "inactivo")
        _, despues = self.op1.llamar("proveedores", "GET", f"proveedores/ofertas?producto_id={pid}", estado=200)
        self.assertNotIn(sid, [x["proveedor"]["id"] for x in despues["datos"]], "un proveedor de baja ya no ofrece")
        for tabla in ("proveedor_zona", "proveedor_producto", "proveedor_evaluacion"):
            datos.consultar(f"DELETE FROM {tabla} WHERE proveedor_id IN (SELECT id FROM proveedor WHERE clave LIKE %s) RETURNING 1", (clave + "%",))
        datos.consultar("DELETE FROM proveedor WHERE clave LIKE %s RETURNING id", (clave + "%",))

    def test_evaluaciones(self):
        pv = self.adm.llamar("proveedores", "GET", "proveedores?q=PV-01", estado=200)[1]["datos"][0]
        _, antes = self.adm.llamar("proveedores", "GET", f"proveedores/{pv['id']}/evaluaciones", estado=200)
        _, ev = self.op1.llamar("proveedores", "POST", f"proveedores/{pv['id']}/evaluaciones",
                                {"puntualidad": 5, "calidad": 4, "precio": 3, "comentario": "Entrega puntual"}, estado=201)
        mismas_llaves(self, ev, ejemplo("Evaluacion.ok"))
        self.assertEqual(ev["evaluado_por"], usuario("operador.mh01@codex.mx"))
        _, despues = self.adm.llamar("proveedores", "GET", f"proveedores/{pv['id']}/evaluaciones", estado=200)
        self.assertEqual(despues["paginacion"]["total"], antes["paginacion"]["total"] + 1)
        for malo in ({"puntualidad": 6, "calidad": 4, "precio": 3}, {"puntualidad": 5, "calidad": 0, "precio": 3}, {"puntualidad": 5}):
            self.assertEqual(self.estado_http(self.op1, "proveedores", "POST", f"proveedores/{pv['id']}/evaluaciones", malo), 422)
        self.assertEqual(self.estado_http(self.aud, "proveedores", "POST", f"proveedores/{pv['id']}/evaluaciones",
                                          {"puntualidad": 5, "calidad": 4, "precio": 3}), 403)
        self.assertEqual(self.estado_http(self.op1, "proveedores", "POST", "proveedores/999999/evaluaciones",
                                          {"puntualidad": 5, "calidad": 4, "precio": 3}), 404)
        xml = f'<evaluacion_nueva xmlns="{NS}"><puntualidad>4</puntualidad><calidad>4</calidad><precio>4</precio></evaluacion_nueva>'
        _, (raiz, _) = self.op1_xml.llamar("proveedores", "POST", f"proveedores/{pv['id']}/evaluaciones", xml, estado=201)
        self.assertEqual(raiz, "evaluacion")
        datos.consultar("DELETE FROM proveedor_evaluacion WHERE proveedor_id = %s AND evaluado_por = %s RETURNING id",
                        (pv["id"], usuario("operador.mh01@codex.mx")))


# ====================================================================
# Abastecimiento
# ====================================================================
class T8Abastecimiento(Base):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PV01 = uno("SELECT id FROM proveedor WHERE clave = 'PV-01'")["id"]

    def cantidad_para_pedido_minimo(self, pid):
        """Piezas que rebasan el pedido mínimo de PV-01 (800) comprando a 70 % del precio."""
        unitario = Decimal(str(producto_por_id(pid)["precio"])) * Decimal("0.70")
        return max(12, math.ceil(Decimal(850) / unitario))

    def solicitar(self, pid, cantidad, cliente=None, hub=None):
        _, s = (cliente or self.op1).llamar("abastecimiento", "POST", "abastecimiento/solicitudes",
                                           {"microhub_id": hub or self.HUB1, "motivo": "Prueba de abastecimiento",
                                            "lineas": [{"producto_id": pid, "cantidad": cantidad}]}, estado=201)
        return s

    def aprobar(self, sid):
        return self.adm.llamar("abastecimiento", "POST", f"abastecimiento/solicitudes/{sid}/decision",
                               {"decision": "aprobada", "motivo": "Hay presupuesto"}, estado=200)[1]

    def ordenar(self, sid):
        return self.adm.llamar("abastecimiento", "POST", f"abastecimiento/solicitudes/{sid}/ordenar", {"proveedor_id": self.PV01}, estado=201)[1]

    def avisos(self, correo, tipo="abastecimiento"):
        return uno("SELECT count(*) AS n FROM web_notificacion WHERE destinatario_id = %s AND tipo = %s", (usuario(correo), tipo))["n"]

    def test_el_ciclo_completo_de_una_compra(self):
        pid = producto("AB-010")["id"]
        qty = self.cantidad_para_pedido_minimo(pid)
        antes = self.existencia(self.HUB1, pid)["existencia"]
        admin_avisos = self.avisos("admin@codex.mx")
        s = self.solicitar(pid, qty)
        mismas_llaves(self, s, ejemplo("SolicitudCompra.ok"))
        self.assertEqual((s["estado"], s["microhub_id"], s["lineas"][0]["cantidad"]), ("pendiente", self.HUB1, qty))
        self.assertEqual(self.avisos("admin@codex.mx"), admin_avisos + 1, "la solicitud avisa a los administradores")
        sid = s["id"]
        self.assertEqual(self.estado_http(self.op2, "abastecimiento", "GET", f"abastecimiento/solicitudes/{sid}"), 404, "es de otro microhub")
        self.assertEqual(self.estado_http(self.op1, "abastecimiento", "GET", f"abastecimiento/solicitudes/{sid}"), 200)
        _, ls = self.op1.llamar("abastecimiento", "GET", "abastecimiento/solicitudes?estado=pendiente", estado=200)
        mismas_llaves(self, ls, ejemplo("SolicitudCompraLista.ok"))
        self.assertIn(sid, [x["id"] for x in ls["datos"]])
        self.op1_xml.llamar("abastecimiento", "GET", "abastecimiento/solicitudes", estado=200)

        decision = {"decision": "aprobada", "motivo": "ok"}
        self.assertEqual(self.estado_http(self.op1, "abastecimiento", "POST", f"abastecimiento/solicitudes/{sid}/decision", decision), 403)
        self.assertEqual(self.estado_http(self.plan, "abastecimiento", "POST", f"abastecimiento/solicitudes/{sid}/decision", decision), 403)
        self.assertEqual(self.estado_http(self.adm, "abastecimiento", "POST", f"abastecimiento/solicitudes/{sid}/decision",
                                          {"decision": "rechazada"}), 422, "rechazar exige motivo")
        self.assertEqual(self.estado_http(self.adm, "abastecimiento", "POST", f"abastecimiento/solicitudes/{sid}/ordenar"), 409,
                         "solo se ordena lo aprobado")
        avisos_op = self.avisos("operador.mh01@codex.mx")
        _, ap = self.adm.llamar("abastecimiento", "POST", f"abastecimiento/solicitudes/{sid}/decision", decision, estado=200)
        self.assertEqual((ap["estado"], ap["decidida_por"]), ("aprobada", usuario("admin@codex.mx")))
        self.assertEqual(self.avisos("operador.mh01@codex.mx"), avisos_op + 1, "quien pidió recibe el aviso de la decisión")
        self.assertEqual(self.estado_http(self.adm, "abastecimiento", "POST", f"abastecimiento/solicitudes/{sid}/decision", decision), 409)

        gen = self.ordenar(sid)
        mismas_llaves(self, gen, ejemplo("OrdenesGeneradas.ok"))
        self.assertEqual(len(gen["ordenes"]), 1)
        o = gen["ordenes"][0]
        unitario = centavos(Decimal(str(producto_por_id(pid)["precio"])) * Decimal("0.70"))
        self.assertEqual((o["estado"], o["proveedor"]["id"], centavos(o["total"])), ("emitida", self.PV01, unitario * qty))
        self.assertEqual(self.adm.llamar("abastecimiento", "GET", f"abastecimiento/solicitudes/{sid}")[1]["estado"], "ordenada")
        self.assertEqual(self.estado_http(self.adm, "abastecimiento", "POST", f"abastecimiento/solicitudes/{sid}/ordenar"), 409)
        oid = o["id"]
        _, uno_ = self.op1.llamar("abastecimiento", "GET", f"abastecimiento/ordenes/{oid}", estado=200)
        mismas_llaves(self, uno_, ejemplo("OrdenCompra.ok"))
        self.assertEqual(self.estado_http(self.op2, "abastecimiento", "GET", f"abastecimiento/ordenes/{oid}"), 404)

        # recepción parcial → entra a inventario una sola vez
        mitad = qty // 2
        lote = str(uuid.uuid4())
        recep = {"operacion_uuid": lote, "nota": "Llegó la primera caja", "lineas": [{"producto_id": pid, "cantidad": mitad}]}
        _, r1 = self.op1.llamar("abastecimiento", "POST", f"abastecimiento/ordenes/{oid}/recepcion", recep, estado=201)
        mismas_llaves(self, r1, ejemplo("RecepcionResultado.ok"))
        self.assertEqual((r1["orden"]["estado"], r1["aplicadas"], r1["pendientes"], r1["aviso"]), ("parcial", 1, 0, None))
        self.assertEqual(self.existencia(self.HUB1, pid)["existencia"], antes + mitad)
        mov = uno("SELECT referencia_tipo, referencia_id, cantidad, tipo::text AS tipo FROM movimiento_inventario "
                  "WHERE operacion_uuid = %s", (f"{lote}:{pid}",))
        self.assertEqual((mov["tipo"], mov["referencia_tipo"], mov["referencia_id"], mov["cantidad"]), ("recepcion", "orden_compra", oid, mitad))
        _, r2 = self.op1.llamar("abastecimiento", "POST", f"abastecimiento/ordenes/{oid}/recepcion", recep, estado=201)
        self.assertEqual(r2["aplicadas"], 0, "el mismo envío repetido no vuelve a entrar")
        self.assertEqual(self.existencia(self.HUB1, pid)["existencia"], antes + mitad)

        resto = qty - mitad
        for malo, esperado in (({"lineas": [{"producto_id": pid, "cantidad": resto + 1}]}, 422),
                               ({"lineas": [{"producto_id": producto("AB-011")["id"], "cantidad": 1}]}, 422)):
            self.assertEqual(self.estado_http(self.op1, "abastecimiento", "POST", f"abastecimiento/ordenes/{oid}/recepcion", malo), esperado)
        self.assertEqual(self.estado_http(self.aud, "abastecimiento", "POST", f"abastecimiento/ordenes/{oid}/recepcion", recep), 403)
        self.assertEqual(self.estado_http(self.op2, "abastecimiento", "POST", f"abastecimiento/ordenes/{oid}/recepcion", recep), 404)
        self.assertEqual(self.estado_http(self.adm, "abastecimiento", "POST", f"abastecimiento/ordenes/{oid}/cancelar", {"motivo": "Ya llegó"}), 409)

        avisos_op = self.avisos("operador.mh01@codex.mx")
        _, r3 = self.op1.llamar("abastecimiento", "POST", f"abastecimiento/ordenes/{oid}/recepcion",
                                {"lineas": [{"producto_id": pid, "cantidad": resto}]}, estado=201)
        self.assertEqual((r3["orden"]["estado"], r3["orden"]["lineas"][0]["cantidad_recibida"]), ("recibida", qty))
        self.assertIsNotNone(r3["orden"]["cerrada_en"])
        self.assertEqual(self.existencia(self.HUB1, pid)["existencia"], antes + qty)
        self.assertEqual(self.avisos("operador.mh01@codex.mx"), avisos_op + 1, "la orden completa avisa al operador")
        self.assertEqual(self.estado_http(self.op1, "abastecimiento", "POST", f"abastecimiento/ordenes/{oid}/recepcion",
                                          {"lineas": [{"producto_id": pid, "cantidad": 1}]}), 409)

        _, seg = self.op1.llamar("abastecimiento", "GET", "abastecimiento/seguimiento", estado=200)
        mismas_llaves(self, seg, ejemplo("SeguimientoAbastecimiento.ok"))
        self.assertEqual(seg["microhub_id"], self.HUB1)
        self.assertGreaterEqual(seg["ordenes"]["recibida"], 1)
        self.assertGreaterEqual(seg["solicitudes"]["ordenada"], 1)
        self.op1_xml.llamar("abastecimiento", "GET", "abastecimiento/seguimiento", estado=200)
        _, hecha = self.op1.llamar("abastecimiento", "GET", "abastecimiento/ordenes?estado=recibida", estado=200)
        mismas_llaves(self, hecha, ejemplo("OrdenCompraLista.ok"))
        self.assertIn(oid, [x["id"] for x in hecha["datos"]])
        self.op1_xml.llamar("abastecimiento", "GET", "abastecimiento/ordenes", estado=200)
        self.assertEqual(self.estado_http(self.adm, "abastecimiento", "GET", "abastecimiento/ordenes?atrasadas=true"), 200)
        self.assertEqual(self.estado_http(self.adm, "abastecimiento", "GET", "abastecimiento/ordenes?estado=inventado"), 400)

    def test_si_inventario_no_responde_la_recepcion_queda_pendiente_y_no_se_duplica(self):
        pid = producto("AB-012")["id"]
        qty = self.cantidad_para_pedido_minimo(pid)
        antes = self.existencia(self.HUB1, pid)["existencia"]
        s = self.solicitar(pid, qty)
        self.aprobar(s["id"])
        oid = self.ordenar(s["id"])["ordenes"][0]["id"]
        APAGADOS.add("inventario")
        try:
            r, caido = self.op1.llamar("abastecimiento", "POST", f"abastecimiento/ordenes/{oid}/recepcion",
                                       {"lineas": [{"producto_id": pid, "cantidad": qty}]})
        finally:
            APAGADOS.discard("inventario")
        self.assertEqual(r.status_code, 202, "aceptada, pero la entrada a inventario quedó pendiente")
        self.assertEqual((caido["aplicadas"], caido["pendientes"]), (0, 1))
        self.assertIn("Inventario", caido["aviso"])
        linea = caido["orden"]["lineas"][0]
        self.assertEqual((caido["orden"]["estado"], linea["cantidad_recibida"], linea["pendiente_inventario"]), ("emitida", 0, qty))
        self.assertEqual(self.existencia(self.HUB1, pid)["existencia"], antes, "inventario no recibió nada")
        _, tablero = self.op1.llamar("abastecimiento", "GET", "abastecimiento/seguimiento", estado=200)
        self.assertGreaterEqual(tablero["pendientes_inventario"], 1)

        _, ok = self.op1.llamar("abastecimiento", "POST", f"abastecimiento/ordenes/{oid}/recepcion", {}, estado=201)
        self.assertEqual((ok["aplicadas"], ok["pendientes"], ok["orden"]["estado"]), (1, 0, "recibida"))
        self.assertEqual(self.existencia(self.HUB1, pid)["existencia"], antes + qty, "entró una sola vez")
        _, otra = self.op1.llamar("abastecimiento", "POST", f"abastecimiento/ordenes/{oid}/recepcion", {}, estado=201)
        self.assertEqual(otra["aplicadas"], 0, "reintentar otra vez no suma de nuevo")
        self.assertEqual(self.existencia(self.HUB1, pid)["existencia"], antes + qty)

    def test_cancelar_rechazar_y_permisos(self):
        pid = producto("AB-013")["id"]
        qty = self.cantidad_para_pedido_minimo(pid)
        s = self.solicitar(pid, qty)
        self.aprobar(s["id"])
        oid = self.ordenar(s["id"])["ordenes"][0]["id"]
        self.assertEqual(self.estado_http(self.op1, "abastecimiento", "POST", f"abastecimiento/ordenes/{oid}/cancelar", {"motivo": "No hace falta"}), 403)
        self.assertEqual(self.estado_http(self.adm, "abastecimiento", "POST", f"abastecimiento/ordenes/{oid}/cancelar", {"motivo": "x"}), 422)
        _, c = self.adm.llamar("abastecimiento", "POST", f"abastecimiento/ordenes/{oid}/cancelar", {"motivo": "El proveedor ya no surte"}, estado=200)
        self.assertEqual((c["estado"], c["cerrada_en"] is not None), ("cancelada", True))
        self.assertEqual(self.estado_http(self.adm, "abastecimiento", "POST", f"abastecimiento/ordenes/{oid}/cancelar", {"motivo": "Otra vez"}), 409)
        self.assertEqual(self.estado_http(self.op1, "abastecimiento", "POST", f"abastecimiento/ordenes/{oid}/recepcion",
                                          {"lineas": [{"producto_id": pid, "cantidad": 1}]}), 409, "una orden cancelada no recibe")

        s2 = self.solicitar(pid, qty)
        _, rech = self.adm.llamar("abastecimiento", "POST", f"abastecimiento/solicitudes/{s2['id']}/decision",
                                  {"decision": "rechazada", "motivo": "Todavía hay existencia"}, estado=200)
        self.assertEqual((rech["estado"], rech["decision_motivo"]), ("rechazada", "Todavía hay existencia"))
        self.assertEqual(self.estado_http(self.adm, "abastecimiento", "POST", f"abastecimiento/solicitudes/{s2['id']}/ordenar"), 409)

        malas = [{"microhub_id": self.HUB1, "lineas": []},
                 {"microhub_id": self.HUB1, "lineas": [{"producto_id": pid, "cantidad": 1}, {"producto_id": pid, "cantidad": 2}]},
                 {"microhub_id": self.HUB1, "lineas": [{"producto_id": 999999, "cantidad": 1}]},
                 {"microhub_id": self.HUB1, "lineas": [{"producto_id": pid, "cantidad": 0}]}]
        for malo in malas:
            self.assertEqual(self.estado_http(self.op1, "abastecimiento", "POST", "abastecimiento/solicitudes", malo), 422)
        self.assertEqual(self.estado_http(self.op1, "abastecimiento", "POST", "abastecimiento/solicitudes",
                                          {"microhub_id": self.HUB2, "lineas": [{"producto_id": pid, "cantidad": 5}]}), 403)
        self.assertEqual(self.estado_http(self.aud, "abastecimiento", "POST", "abastecimiento/solicitudes",
                                          {"microhub_id": self.HUB1, "lineas": [{"producto_id": pid, "cantidad": 5}]}), 403)
        self.assertEqual(self.estado_http(self.aud, "abastecimiento", "GET", "abastecimiento/solicitudes"), 200)
        self.assertEqual(self.estado_http(self.aud, "abastecimiento", "GET", "abastecimiento/ordenes"), 200)
        self.assertEqual(self.estado_http(self.cli, "abastecimiento", "GET", "abastecimiento/solicitudes"), 403)
        self.assertEqual(self.estado_http(Cliente(self, "json"), "abastecimiento", "GET", "abastecimiento/solicitudes"), 401)

    def test_una_solicitud_en_xml(self):
        pid = producto("AB-014")["id"]
        xml = (f'<solicitud_nueva xmlns="{NS}"><microhub_id>{self.HUB1}</microhub_id><motivo>Prueba XML</motivo>'
               f'<lineas><linea><producto_id>{pid}</producto_id><cantidad>12</cantidad></linea></lineas></solicitud_nueva>')
        _, (raiz, s) = self.op1_xml.llamar("abastecimiento", "POST", "abastecimiento/solicitudes", xml, estado=201)
        self.assertEqual((raiz, s["estado"]), ("solicitud", "pendiente"))
        decision = f'<decision_compra xmlns="{NS}"><decision>rechazada</decision><motivo>Prueba XML</motivo></decision_compra>'
        _, (raiz, d) = self.adm_xml.llamar("abastecimiento", "POST", f"abastecimiento/solicitudes/{s['id']}/decision", decision, estado=200)
        self.assertEqual(d["estado"], "rechazada")

    def test_necesidades_de_reposicion(self):
        pid = producto("AB-015")["id"]
        e = self.existencia(self.HUB1, pid)
        original = e["minimo"]
        factor = float(datos.parametro("reposicion_factor_objetivo", 3))
        try:
            self.adm.llamar("inventario", "PATCH", f"inventario/{self.HUB1}/{pid}/minimo", {"minimo": e["disponible"] + 20}, estado=200)
            _, n = self.op1.llamar("abastecimiento", "GET", "abastecimiento/necesidades?por_pagina=100", estado=200)
            mismas_llaves(self, n, ejemplo("NecesidadLista.ok"))
            self.assertEqual((n["microhub_id"], n["factor_objetivo"]), (self.HUB1, factor))
            fila = next(x for x in n["datos"] if x["producto"]["id"] == pid)
            objetivo = math.ceil((e["disponible"] + 20) * factor)
            self.assertEqual(fila["cantidad_sugerida"], objetivo - e["disponible"] - fila["en_camino"] - fila["solicitado"])
            self.assertGreaterEqual(fila["cantidad_a_comprar"], fila["cantidad_sugerida"])
            self.assertIsNotNone(fila["mejor_oferta"], "trae la oferta más barata de proveedores")
            self.assertEqual(centavos(fila["costo_estimado"]), centavos(Decimal(str(fila["mejor_oferta"]["precio_compra"])) * fila["cantidad_a_comprar"]))
            self.op1_xml.llamar("abastecimiento", "GET", "abastecimiento/necesidades", estado=200)

            # lo que ya se pidió deja de pedirse otra vez
            sugerida = fila["cantidad_sugerida"]
            self.solicitar(pid, sugerida)
            _, despues = self.op1.llamar("abastecimiento", "GET", "abastecimiento/necesidades?por_pagina=100", estado=200)
            nuevo = next((x for x in despues["datos"] if x["producto"]["id"] == pid), None)
            self.assertTrue(nuevo is None or nuevo["cantidad_sugerida"] == fila["cantidad_sugerida"] - sugerida)
            if nuevo:
                self.assertEqual(nuevo["solicitado"], fila["solicitado"] + sugerida)

            self.assertEqual(self.estado_http(self.adm, "abastecimiento", "GET", "abastecimiento/necesidades"), 400, "el administrador debe indicar el microhub")
            self.assertEqual(self.estado_http(self.op1, "abastecimiento", "GET", f"abastecimiento/necesidades?microhub_id={self.HUB2}"), 403)
            self.assertEqual(self.estado_http(self.adm, "abastecimiento", "GET", f"abastecimiento/necesidades?microhub_id={self.HUB1}"), 200)
        finally:
            self.adm.llamar("inventario", "PATCH", f"inventario/{self.HUB1}/{pid}/minimo", {"minimo": original})
            datos.consultar("UPDATE solicitud_compra SET estado = 'rechazada', decision_motivo = 'Limpieza de la prueba' "
                            "WHERE microhub_id = %s AND estado = 'pendiente' AND motivo = 'Prueba de abastecimiento' RETURNING id", (self.HUB1,))


def producto_por_id(pid):
    return uno("SELECT id, precio FROM producto WHERE id = %s", (pid,))


if __name__ == "__main__":
    unittest.main(verbosity=2)
