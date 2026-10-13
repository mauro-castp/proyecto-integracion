"""Pruebas con PostgreSQL/Redis reales. SOLO usar en proyecto Docker de prueba.

docker compose -p microhubs-web-prueba exec -e WEB_PRUEBA_AISLADA=1 web python prueba_e2e_web.py
"""
import io
import os
from pathlib import Path
import unittest

if os.environ.get('WEB_PRUEBA_AISLADA') != '1':
    raise SystemExit('Usa WEB_PRUEBA_AISLADA=1 exclusivamente con una base de pruebas aislada.')

from app import app
from nucleo import consultar, con_actual
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

    def test_03_archivo_bytea_y_aislamiento(self):
        data = b'%PDF-1.4\nDocumento de prueba'
        r = self.c.post('/web/archivos', data={'csrf':self.csrf,'archivo':(io.BytesIO(data),'prueba.pdf')})
        self.assertEqual(r.status_code, 302)
        with app.test_request_context():
            archivo = consultar("SELECT id FROM web_archivo WHERE nombre='prueba.pdf' ORDER BY creado_en DESC LIMIT 1", una=True)
        url = '/web/archivos/' + archivo['id']
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


if __name__ == '__main__':
    unittest.main(verbosity=2)
