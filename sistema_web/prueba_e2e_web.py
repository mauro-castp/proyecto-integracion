"""Pruebas con PostgreSQL/Redis reales. SOLO usar en proyecto Docker de prueba.

docker compose -p microhubs-web-prueba exec -e WEB_PRUEBA_AISLADA=1 web python prueba_e2e_web.py
"""
import io
import os
import re
import uuid
from pathlib import Path
import unittest

if os.environ.get('WEB_PRUEBA_AISLADA') != '1':
    raise SystemExit('Usa WEB_PRUEBA_AISLADA=1 exclusivamente con una base de pruebas aislada.')

from app import app
from nucleo import consultar, con_actual, hashear
from flask import g


class IntegracionWeb(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        cls.c = app.test_client()
        r = cls.c.post('/entrar', data={'correo':'admin@codex.mx','clave':'Codex#2026'})
        assert r.status_code == 302, r.status_code
        cls.c.get('/web/archivos')
        with cls.c.session_transaction() as s:
            cls.csrf = s['web_csrf']

    def test_01_salud_y_listas_reales(self):
        self.assertEqual(self.c.get('/salud').status_code, 200)
        for ruta in ('/web/reportes','/web/roles','/web/archivos','/web/notificaciones','/admin/productos','/admin/categorias','/admin/microhubs','/admin/zonas','/admin/gestion-usuarios','/mis-pedidos','/operacion','/bitacora','/admin/pendientes'):
            self.assertEqual(self.c.get(ruta + '?por_pagina=10').status_code, 200, ruta)
        self.assertEqual(self.c.get('/admin/categorias?estatus=baja').status_code, 200)

    def test_02_reporte_exportacion_historial(self):
        csv = self.c.get('/web/reportes.csv?estado=entregado')
        self.assertEqual(csv.status_code, 200)
        self.assertIn('entregado', csv.get_data(as_text=True))
        with app.test_request_context():
            pedido = consultar("SELECT id FROM pedido WHERE estado='entregado' ORDER BY creado_en DESC LIMIT 1", una=True)
        self.assertEqual(self.c.get(f"/web/pedidos/{pedido['id']}?desde=2020-01-01&hasta=2020-01-02").status_code, 404)
        from datetime import date,timedelta
        hoy = date.today()
        self.assertEqual(self.c.get(f"/web/pedidos/{pedido['id']}?desde={hoy-timedelta(days=90)}&hasta={hoy}").status_code, 200)

    def test_03_archivo_en_el_almacen_y_aislamiento(self):
        data = b'%PDF-1.4\nDocumento de prueba'
        r = self.c.post('/web/archivos', data={'csrf':self.csrf,'archivo':(io.BytesIO(data),'prueba.pdf')})
        self.assertEqual(r.status_code, 302)
        with app.test_request_context():
            fila = consultar("SELECT contenido IS NULL AS sin_contenido, ruta, almacen, sha256, tamano FROM web_archivo "
                             "WHERE nombre='prueba.pdf' ORDER BY creado_en DESC, id DESC LIMIT 1", una=True)
        self.assertTrue(fila['sin_contenido'], 'la base no debe guardar el contenido del archivo')
        self.assertTrue(fila['ruta'].startswith('web/'))
        self.assertEqual((len(fila['sha256']), fila['tamano']), (64, len(data)))
        html = self.c.get('/web/archivos').get_data(as_text=True)
        self.assertIn('prueba.pdf', html)
        url = re.search(r'/web/archivos/[0-9a-f]{32}', html).group(0)         # el más reciente va primero
        self.assertEqual(self.c.get(url).data, data)
        otro = app.test_client()
        self.assertEqual(otro.post('/entrar',data={'correo':'operador.mh01@codex.mx','clave':'Codex#2026'}).status_code, 302)
        self.assertEqual(otro.get(url).status_code, 404)

    def test_04_notificaciones_reales(self):
        with app.test_request_context():
            usuario = consultar("SELECT id FROM usuario WHERE correo='operador.mh01@codex.mx'", una=True)
        r = self.c.post('/web/notificaciones',data={'csrf':self.csrf,'destinatario_id':usuario['id'],'titulo':'Aviso E2E','mensaje':'Solo para operador E2E'})
        self.assertEqual(r.status_code, 302)
        self.assertNotIn('Solo para operador E2E',self.c.get('/web/notificaciones').get_data(as_text=True))
        otro = app.test_client(); otro.post('/entrar',data={'correo':'operador.mh01@codex.mx','clave':'Codex#2026'})
        self.assertIn('Solo para operador E2E', otro.get('/web/notificaciones').get_data(as_text=True))
        self.assertEqual(otro.get('/web/roles').status_code, 403)

    def test_05_cierre_notifica_en_transaccion(self):
        class RollbackPrueba(Exception): pass
        with app.test_request_context():
            admin = consultar("SELECT id FROM usuario WHERE correo='admin@codex.mx'",una=True)
            g.usuario = {'id':admin['id'],'rol':'administrador'}
            try:
                with con_actual() as con, con.cursor() as cur:
                    cur.execute("SELECT id,folio FROM pedido WHERE estado='asignado' LIMIT 1")
                    pedido = cur.fetchone(); self.assertIsNotNone(pedido)
                    cur.execute("UPDATE pedido SET estado='cancelado',motivo_cancelacion='Ensayo transaccional' WHERE id=%s",(pedido['id'],))
                    cur.execute("SELECT count(*) AS n FROM web_notificacion WHERE titulo=%s",('Pedido '+pedido['folio'],))
                    self.assertGreater(cur.fetchone()['n'],0)
                    raise RollbackPrueba()
            except RollbackPrueba:
                pass

    def test_06_migracion_no_restituye_permisos(self):
        with app.test_request_context():
            class RollbackPrueba(Exception): pass
            try:
                with con_actual() as con, con.cursor() as cur:
                    cur.execute("DELETE FROM rol_permiso WHERE rol_id=(SELECT id FROM rol WHERE clave='analista') AND permiso_id=(SELECT id FROM permiso WHERE clave='reportes.exportar')")
                    ruta = Path('/app/07_web_ampliado.sql')
                    # Eliminar solo el marco transaccional para mantener la prueba reversible.
                    sql = ruta.read_text().replace('BEGIN;\n','',1).rsplit('COMMIT;',1)[0]
                    cur.execute(sql)
                    cur.execute("SELECT count(*) AS n FROM rol_permiso rp JOIN rol r ON r.id=rp.rol_id JOIN permiso p ON p.id=rp.permiso_id WHERE r.clave='analista' AND p.clave='reportes.exportar'")
                    self.assertEqual(cur.fetchone()['n'],0)
                    raise RollbackPrueba()
            except RollbackPrueba:
                pass


class RecuperacionYProveedor(unittest.TestCase):
    """Recuperación de contraseña y perfil de proveedor, contra PostgreSQL y Redis reales."""

    def csrf(self, cliente, ruta):
        html = cliente.get(ruta).get_data(as_text=True)
        return re.search(r'name="csrf" value="([^"]+)"', html).group(1)

    def entrar(self, correo, clave):
        c = app.test_client()
        return c, c.post('/entrar', data={'correo': correo, 'clave': clave}).status_code

    def test_07_recuperacion_de_contrasena(self):
        correo = f'recupera.{uuid.uuid4().hex[:8]}@ejemplo.mx'
        with app.test_request_context():
            with con_actual() as con, con.cursor() as cur:
                cur.execute("INSERT INTO usuario (nombre, apellidos, correo, hash_contrasena, rol_id) SELECT 'Prueba', 'Recuperación', %s, %s, id "
                            "FROM rol WHERE clave = 'cliente' RETURNING id", (correo, hashear('Anterior123')))
                uid = cur.fetchone()['id']
        try:
            sesion, estado = self.entrar(correo, 'Anterior123')
            self.assertEqual(estado, 302)
            self.assertEqual(sesion.get('/mis-pedidos').status_code, 200)
            c = app.test_client()
            token_f = self.csrf(c, '/recuperar')
            self.assertEqual(c.post('/recuperar', data={'correo': correo}).status_code, 400, 'sin CSRF no se acepta')
            r = c.post('/recuperar', data={'csrf': token_f, 'correo': correo}, follow_redirects=True)
            self.assertIn('Si la cuenta existe', r.get_data(as_text=True))
            otra = c.post('/recuperar', data={'csrf': token_f, 'correo': 'nadie@ejemplo.mx'}, follow_redirects=True)
            self.assertIn('Si la cuenta existe', otra.get_data(as_text=True), 'no revela qué cuentas existen')
            with app.test_request_context():
                aviso = consultar("SELECT mensaje FROM web_notificacion WHERE emisor_id = %s ORDER BY id DESC LIMIT 1", (uid,), una=True)
            ruta = re.search(r'/restablecer/[\w-]+', aviso['mensaje']).group(0)
            token_f = self.csrf(c, ruta)
            corta = c.post(ruta, data={'csrf': token_f, 'clave': 'corta1', 'repetida': 'corta1'})
            self.assertEqual(corta.status_code, 422)
            r = c.post(ruta, data={'csrf': token_f, 'clave': 'Nueva12345', 'repetida': 'Nueva12345'})
            self.assertEqual(r.status_code, 302)
            self.assertEqual(self.entrar(correo, 'Anterior123')[1], 401)
            self.assertEqual(self.entrar(correo, 'Nueva12345')[1], 302)
            self.assertNotEqual(sesion.get('/mis-pedidos').status_code, 200, 'la sesión anterior quedó cerrada')
            self.assertIn('/recuperar', c.get(ruta).headers.get('Location', ''), 'el enlace sirve una sola vez')
        finally:
            with app.test_request_context():
                with con_actual() as con, con.cursor() as cur:
                    cur.execute("UPDATE usuario SET estatus = 'baja', fecha_baja = now() WHERE id = %s", (uid,))

    def test_08_portal_del_proveedor(self):
        prov, estado = self.entrar('proveedor@codex.mx', 'Codex#2026')
        self.assertEqual(estado, 302)
        html = prov.get('/proveedor').get_data(as_text=True)
        self.assertIn('Mi catálogo y mi oferta', html)
        self.assertEqual(prov.get('/proveedor/ordenes').status_code, 200)
        self.assertEqual(prov.get('/admin/usuarios').status_code, 403)
        with app.test_request_context():
            f = consultar("SELECT pp.proveedor_id, pp.producto_id, pp.precio_compra, pp.capacidad_semanal FROM proveedor_producto pp "
                          "JOIN proveedor p ON p.id = pp.proveedor_id JOIN usuario u ON u.id = p.usuario_id WHERE u.correo = 'proveedor@codex.mx' "
                          "ORDER BY pp.producto_id LIMIT 1", una=True)
            ajeno = consultar("SELECT id FROM producto WHERE id NOT IN (SELECT producto_id FROM proveedor_producto WHERE proveedor_id = %s) "
                              "ORDER BY id LIMIT 1", (f['proveedor_id'],), una=True)
        token_f = self.csrf(prov, '/proveedor')
        datos_f = {'csrf': token_f, 'producto_id': f['producto_id'], 'precio_compra': '12.34', 'capacidad_semanal': '77'}
        self.assertEqual(prov.post('/proveedor', data=datos_f).status_code, 302)
        leer = "SELECT precio_compra, capacidad_semanal FROM proveedor_producto WHERE proveedor_id = %s AND producto_id = %s"
        with app.test_request_context():
            nuevo = consultar(leer, (f['proveedor_id'], f['producto_id']), una=True)
        self.assertEqual((str(nuevo['precio_compra']), nuevo['capacidad_semanal']), ('12.34', 77))
        if ajeno:
            self.assertEqual(prov.post('/proveedor', data={**datos_f, 'producto_id': ajeno['id']}).status_code, 404)
        prov.post('/proveedor', data={**datos_f, 'precio_compra': str(f['precio_compra']), 'capacidad_semanal': str(f['capacidad_semanal'])})
        admin, _ = self.entrar('admin@codex.mx', 'Codex#2026')
        self.assertEqual(admin.get('/proveedor').status_code, 403, 'el portal es del proveedor')


if __name__ == '__main__':
    unittest.main(verbosity=2)
