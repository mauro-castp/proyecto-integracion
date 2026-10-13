"""Regresión funcional y permisos con SQLite aislado, sin servicios externos."""
import io
import re
import tempfile
import unittest
from pathlib import Path
from flask import g

from app_local import app
import catalogos_crud as catalogos
import productos_crud as productos
from web_ampliado import inicializar_local, db_local, celda_csv


@app.before_request
def actor_prueba():
    if app.config.get('TESTING') and 'TEST_ACTOR' in app.config:
        g.usuario = app.config['TEST_ACTOR']


class WebAmpliado(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent, prefix='.test-web-')
        self.prev = (catalogos.DB_LOCAL, productos.DB_LOCAL, app.config['WEB_DB_LOCAL'])
        ruta = Path(self.temp.name) / 'test.db'
        catalogos.DB_LOCAL = productos.DB_LOCAL = ruta
        app.config.update(TESTING=True, WEB_DB_LOCAL=str(ruta), TEST_ACTOR={'id': 1, 'rol': 'administrador', 'nombre': 'Admin', 'microhub_id': None})
        productos.inicializar_local(); catalogos.inicializar_local()
        with app.app_context():
            inicializar_local()
        self.c = app.test_client()
        self.c.get('/web/archivos')
        with self.c.session_transaction() as s:
            self.csrf = s['web_csrf']

    def tearDown(self):
        catalogos.DB_LOCAL, productos.DB_LOCAL, app.config['WEB_DB_LOCAL'] = self.prev
        app.config.pop('TEST_ACTOR', None); app.config['TESTING'] = False
        import gc
        gc.collect()
        self.temp.cleanup()

    def actor(self, rol, uid=2, hub=None):
        app.config['TEST_ACTOR'] = {'id': uid, 'rol': rol, 'nombre': 'Prueba', 'microhub_id': hub}

    def post(self, ruta, **data):
        return self.c.post(ruta, data={'csrf': self.csrf, **data}, follow_redirects=True)

    def test_pantallas_y_graficas(self):
        for ruta in ('/web/reportes','/web/roles','/web/archivos','/web/notificaciones'):
            self.assertEqual(self.c.get(ruta).status_code, 200)
        html = self.c.get('/web/reportes').get_data(as_text=True)
        self.assertIn('highcharts.com/12.4.0', html)
        self.assertIn('65', html)
        self.assertIn('Página 1 de 4', html)
        self.assertRegex(html, r'"dia": "\d{4}-\d{2}-\d{2}"')

    def test_paginacion_estable_y_filtros(self):
        primera = self.c.get('/web/reportes?por_pagina=10&q=DEMO').get_data(as_text=True)
        segunda = self.c.get('/web/reportes?por_pagina=10&q=DEMO&pagina=2').get_data(as_text=True)
        ids1 = re.findall(r'>(DEMO-\d+)</a>', primera)
        ids2 = re.findall(r'>(DEMO-\d+)</a>', segunda)
        self.assertEqual(len(ids1), 10); self.assertFalse(set(ids1) & set(ids2))
        self.assertIn('q=DEMO', primera)
        html = self.c.get('/web/reportes?q=DEMO-0001').get_data(as_text=True)
        self.assertEqual(re.findall(r'>(DEMO-\d+)</a>', html), ['DEMO-0001'])

    def test_filtros_invalidos(self):
        for query in ('pagina=0', 'por_pagina=999', 'pagina=abc', 'desde=2026-02-30', 'desde=2026-10-12&hasta=2026-10-01', 'estado=hack', 'microhub_id=0'):
            self.assertEqual(self.c.get('/web/reportes?' + query).status_code, 400, query)

    def test_exporta_todo_el_filtro(self):
        r = self.c.get('/web/reportes.csv?estado=entregado&por_pagina=10')
        self.assertEqual(r.status_code, 200)
        self.assertIn('attachment', r.headers['Content-Disposition'])
        texto = r.get_data(as_text=True)
        self.assertIn('entregado', texto); self.assertNotIn('en_ruta', texto)
        self.assertTrue(celda_csv(' =SUM(1)').startswith("'"))

    def test_ambito_supervisor_no_se_puede_ampliar(self):
        self.actor('supervisor', hub=1)
        r = self.c.get('/web/reportes.csv')
        self.assertEqual(r.status_code, 200)
        import csv
        filas = list(csv.reader(io.StringIO(r.get_data(as_text=True))))[1:]
        self.assertTrue(filas); self.assertTrue(all(row[5] == '1' for row in filas))
        ajeno = self.c.get('/web/reportes.csv?microhub_id=2').get_data(as_text=True)
        self.assertEqual(len(ajeno.splitlines()), 1)
        self.actor('supervisor')
        self.assertEqual(self.c.get('/web/reportes').status_code, 403)

    def test_permisos_en_rutas(self):
        self.actor('operador', hub=1)
        for ruta in ('/web/reportes','/web/reportes.csv','/web/roles'):
            self.assertEqual(self.c.get(ruta).status_code, 403)
        self.assertEqual(self.post('/web/notificaciones', titulo='Prueba', mensaje='Texto', destinatario_id=1).status_code, 403)
        app.config['TEST_ACTOR'] = None
        self.assertEqual(self.c.get('/web/archivos').status_code, 401)

    def test_csrf_obligatorio(self):
        self.assertEqual(self.c.post('/web/notificaciones', data={'titulo':'X'}).status_code, 400)

    def test_subida_descarga_privada(self):
        contenido = b'%PDF-1.4\nPrueba'
        r = self.post('/web/archivos', archivo=(io.BytesIO(contenido), '../../evidencia.pdf'))
        self.assertEqual(r.status_code, 200)
        with app.app_context():
            with db_local() as con:
                archivo = con.execute('SELECT id,nombre FROM web_archivo').fetchone()
        self.assertEqual(archivo['nombre'], 'evidencia.pdf')
        r = self.c.get('/web/archivos/' + archivo['id'])
        self.assertEqual(r.data, contenido)
        self.assertEqual(r.headers['X-Content-Type-Options'], 'nosniff')
        self.actor('operador', hub=1)
        self.assertEqual(self.c.get('/web/archivos/' + archivo['id']).status_code, 404)

    def test_rechaza_archivos_falsos_grandes_y_activos(self):
        for contenido, nombre in ((b'<script>bad</script>', 'foto.jpg'), (b'<svg/>', 'foto.svg')):
            r = self.post('/web/archivos', archivo=(io.BytesIO(contenido), nombre))
            self.assertEqual(r.status_code, 400)
        from web_ampliado import validar_archivo
        from werkzeug.exceptions import BadRequest
        with self.assertRaises(BadRequest):
            validar_archivo('grande.pdf', b'%PDF-'+b'x'*(5*1024*1024))

    def test_notificacion_y_lectura_por_destinatario(self):
        r = self.post('/web/notificaciones', titulo='<b>Privado</b>', mensaje='Solo destinatario', destinatario_id=2)
        self.assertEqual(r.status_code, 200)
        self.assertNotIn('Solo destinatario', r.get_data(as_text=True))
        self.assertEqual(self.post('/web/notificaciones/1/leer').status_code, 404)
        self.actor('operador', hub=1)
        html = self.c.get('/web/notificaciones').get_data(as_text=True)
        self.assertIn('Solo destinatario', html); self.assertIn('&lt;b&gt;Privado&lt;/b&gt;', html)
        self.assertEqual(self.post('/web/notificaciones/1/leer').status_code, 200)
        self.assertNotIn('Solo destinatario', self.c.get('/web/notificaciones?lectura=pendientes').get_data(as_text=True))

    def test_edicion_de_roles_y_persistencia(self):
        with app.app_context():
            with db_local() as con:
                rid = con.execute("SELECT id FROM rol WHERE clave='analista'").fetchone()[0]
        self.assertEqual(self.post('/web/roles', rol_id=rid, permisos=['archivos.ver']).status_code, 200)
        with app.app_context():
            inicializar_local()
        self.actor('analista')
        self.assertEqual(self.c.get('/web/reportes').status_code, 403)
        self.assertEqual(self.c.get('/web/archivos').status_code, 200)

    def test_no_modifica_admin_ni_delega_administracion(self):
        self.assertEqual(self.post('/web/roles', rol_id=1, permisos=[]).status_code, 403)
        self.assertEqual(self.post('/web/roles', rol_id=2, permisos=['roles.editar']).status_code, 400)

    def test_paginacion_cruds_anteriores(self):
        for ruta in ('/admin/categorias','/admin/microhubs','/admin/zonas','/admin/gestion-usuarios','/admin/productos'):
            self.assertEqual(self.c.get(ruta + '?q=imposible&por_pagina=10').status_code, 200, ruta)
            self.assertEqual(self.c.get(ruta + '?pagina=-1').status_code, 400, ruta)
        self.assertIn('Arroz', self.c.get('/admin/productos?q=Arroz').get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
