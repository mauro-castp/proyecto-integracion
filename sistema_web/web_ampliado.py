"""Reportes, archivos, avisos y perfiles, sin dependencia de microservicios."""
import csv
import datetime as dt
import io
import secrets
import sqlite3
from zoneinfo import ZoneInfo
from functools import wraps
from contextlib import contextmanager
from pathlib import Path

from flask import (Blueprint, Response, abort, current_app, flash, g, redirect,
                   render_template, request, send_file, session, url_for)
from werkzeug.utils import secure_filename
from paginacion import paginar, enlace_pagina

web_bp = Blueprint('web', __name__, url_prefix='/web')
PERMISOS = ('reportes.ver', 'reportes.exportar', 'archivos.ver', 'archivos.crear',
            'notificaciones.ver', 'notificaciones.crear', 'roles.ver', 'roles.editar')
ESTADOS = ('creado', 'pendiente_asignacion', 'asignado', 'en_preparacion', 'en_ruta',
           'entregado', 'entrega_parcial', 'entrega_fallida', 'cancelado')


def local():
    return current_app.config.get('WEB_LOCAL', False)


@contextmanager
def db_local():
    con = sqlite3.connect(current_app.config['WEB_DB_LOCAL'])
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    try:
        with con:
            yield con
    finally:
        con.close()


def consulta(sql, args=(), una=False):
    if local():
        with db_local() as con:
            cursor = con.execute(sql.replace('%s', '?'), args)
            return cursor.fetchone() if una else cursor.fetchall()
    from nucleo import consultar
    return consultar(sql, args, una=una)


def ejecutar(sql, args=()):
    if local():
        with db_local() as con:
            con.execute(sql.replace('%s', '?'), args)
    else:
        from nucleo import con_actual
        with con_actual() as con, con.cursor() as cur:
            cur.execute(sql, args)


def permisos_usuario():
    u = getattr(g, 'usuario', None)
    if not u:
        return set()
    if local():
        return {r['clave'] for r in consulta('SELECT p.clave FROM permiso p JOIN rol_permiso rp ON rp.permiso_id=p.id JOIN rol r ON r.id=rp.rol_id WHERE r.clave=%s', (u['rol'],))}
    from nucleo import permisos_de
    return permisos_de(u['rol'])


def protegido(permiso):
    def decorar(fn):
        @wraps(fn)
        def ruta(*args, **kw):
            if not getattr(g, 'usuario', None):
                abort(401)
            if permiso not in permisos_usuario():
                abort(403)
            return fn(*args, **kw)
        return ruta
    return decorar


def csrf():
    if 'web_csrf' not in session:
        session['web_csrf'] = secrets.token_urlsafe(32)
    return session['web_csrf']


@web_bp.before_request
def proteger_formularios():
    if request.method == 'POST':
        esperado = session.get('web_csrf', '')
        recibido = request.form.get('csrf', '')
        if not esperado or not secrets.compare_digest(esperado, recibido):
            abort(400, 'Formulario vencido; recarga la página.')


def instalar(app, modo_local=False):
    app.config['WEB_LOCAL'] = modo_local
    app.config.setdefault('WEB_DB_LOCAL', str(Path(__file__).with_name('microhubs_local.db')))
    app.config.setdefault('MAX_CONTENT_LENGTH', 6 * 1024 * 1024)
    app.register_blueprint(web_bp)

    @app.context_processor
    def contexto_web():
        permisos = permisos_usuario() if getattr(g, 'usuario', None) else set()
        return dict(web_permisos=permisos, web_csrf=csrf, enlace_pagina=enlace_pagina)

    if modo_local:
        with app.app_context():
            inicializar_local()


def inicializar_local():
    with db_local() as con:
        con.executescript('''
          CREATE TABLE IF NOT EXISTS permiso(id INTEGER PRIMARY KEY,clave TEXT UNIQUE,modulo TEXT,accion TEXT);
          CREATE TABLE IF NOT EXISTS rol_permiso(rol_id INTEGER REFERENCES rol(id),permiso_id INTEGER REFERENCES permiso(id),PRIMARY KEY(rol_id,permiso_id));
          CREATE TABLE IF NOT EXISTS web_notificacion(id INTEGER PRIMARY KEY, destinatario_id INTEGER REFERENCES usuario(id),emisor_id INTEGER REFERENCES usuario(id),titulo TEXT,mensaje TEXT,creado_en TEXT DEFAULT CURRENT_TIMESTAMP,leido_en TEXT);
          CREATE TABLE IF NOT EXISTS web_archivo(id TEXT PRIMARY KEY,propietario_id INTEGER REFERENCES usuario(id),nombre TEXT,tipo TEXT,contenido BLOB,tamano INTEGER,creado_en TEXT DEFAULT CURRENT_TIMESTAMP);
          CREATE TABLE IF NOT EXISTS web_demo_pedido(id INTEGER PRIMARY KEY,folio TEXT,estado TEXT,total REAL,creado_en TEXT,microhub_id INTEGER,zona TEXT);
        ''')
        for clave in PERMISOS:
            modulo, accion = clave.split('.')
            con.execute('INSERT OR IGNORE INTO permiso(clave,modulo,accion) VALUES(?,?,?)', (clave, modulo, accion))
        for clave, nombre, ambito in [('analista', 'Analista de operación', 0), ('supervisor', 'Supervisor de microhub', 1)]:
            con.execute('INSERT OR IGNORE INTO rol(clave,nombre,requiere_microhub) VALUES(?,?,?)', (clave, nombre, ambito))
        # Solo siembra asignaciones al crear el módulo; no restituye permisos retirados.
        con.execute('CREATE TABLE IF NOT EXISTS web_migracion(clave TEXT PRIMARY KEY)')
        if not con.execute("SELECT 1 FROM web_migracion WHERE clave='v1'").fetchone():
            con.execute("INSERT OR IGNORE INTO rol_permiso SELECT r.id,p.id FROM rol r CROSS JOIN permiso p WHERE r.clave='administrador' OR (r.clave IN ('auditor','planeador','analista','supervisor') AND p.clave IN ('reportes.ver','reportes.exportar')) OR p.clave IN ('archivos.ver','archivos.crear','notificaciones.ver')")
            con.execute("INSERT INTO web_migracion VALUES('v1')")
        if not con.execute('SELECT 1 FROM web_demo_pedido LIMIT 1').fetchone():
            hoy = dt.date.today()
            con.executemany('INSERT INTO web_demo_pedido VALUES(?,?,?,?,?,?,?)', [
                (i, f'DEMO-{i:04}', ESTADOS[i % len(ESTADOS)], 80 + i * 3.5,
                 str(hoy - dt.timedelta(days=i % 30)) + ' 12:00:00', 1 + i % 2,
                 'San Bernabé' if i % 2 else 'Valles de San Bernabé') for i in range(1, 66)])


def filtro_reporte():
    hoy = dt.datetime.now(ZoneInfo('America/Mexico_City')).date()
    desde = request.args.get('desde', str(hoy - dt.timedelta(days=30)))
    hasta = request.args.get('hasta', str(hoy))
    try:
        inicio, fin = dt.date.fromisoformat(desde), dt.date.fromisoformat(hasta)
        if inicio > fin or (fin - inicio).days > 366:
            raise ValueError
        exclusivo = fin + dt.timedelta(days=1)
    except (ValueError, OverflowError):
        abort(400, 'Rango de fechas inválido (máximo 366 días).')
    estado = request.args.get('estado', '')
    if estado and estado not in ESTADOS:
        abort(400, 'Estado inválido.')
    condiciones = ['p.creado_en >= %s', 'p.creado_en < %s']
    args = [str(inicio), str(exclusivo)] if local() else [
        dt.datetime.combine(inicio, dt.time(), ZoneInfo('America/Mexico_City')),
        dt.datetime.combine(exclusivo, dt.time(), ZoneInfo('America/Mexico_City'))]
    usuario = g.usuario
    # Un perfil con ámbito nunca puede salir de su microhub mediante un filtro.
    rol = consulta('SELECT requiere_microhub FROM rol WHERE clave=%s', (usuario['rol'],), una=True)
    if not rol:
        abort(403)
    if not rol['requiere_microhub'] and usuario['rol'] not in ('administrador', 'auditor', 'planeador', 'analista'):
        abort(403)
    if rol['requiere_microhub']:
        if not usuario.get('microhub_id'):
            abort(403)
        condiciones.append('p.microhub_id=%s'); args.append(usuario['microhub_id'])
    hub = request.args.get('microhub_id', '')
    if hub:
        try:
            hub = int(hub)
            if hub < 1:
                raise ValueError
        except ValueError:
            abort(400, 'Microhub inválido.')
        condiciones.append('p.microhub_id=%s'); args.append(hub)
    if estado:
        condiciones.append('p.estado=%s'); args.append(estado)
    q = request.args.get('q', '').strip()[:120]
    if q:
        condiciones.append('lower(p.folio) LIKE %s'); args.append('%' + q.lower() + '%')
    tabla = 'web_demo_pedido p' if local() else 'pedido p JOIN zona z ON z.id=p.zona_id'
    zona = 'p.zona' if local() else 'z.colonia'
    sql = f'SELECT p.id,p.folio,CAST(p.estado AS TEXT) AS estado,p.total,p.creado_en,p.microhub_id,{zona} AS zona FROM {tabla} WHERE ' + ' AND '.join(condiciones)
    return sql, tuple(args), desde, hasta


@web_bp.get('/reportes')
@protegido('reportes.ver')
def reportes():
    sql, args, desde, hasta = filtro_reporte()
    pedidos = paginar(sql + ' ORDER BY p.creado_en DESC,p.id DESC', args, consulta, filtrar=False)
    resumen = consulta(f'SELECT count(*) AS pedidos,COALESCE(sum(total),0) AS importe FROM ({sql}) datos', args, una=True)
    estados = [dict(r) for r in consulta(f'SELECT estado,count(*) AS cantidad FROM ({sql}) datos GROUP BY estado ORDER BY estado', args)]
    dia = 'substr(creado_en,1,10)' if local() else "CAST(creado_en AT TIME ZONE 'America/Mexico_City' AS DATE)"
    diario = [dict(r) for r in consulta(f'SELECT {dia} AS dia,count(*) AS cantidad FROM ({sql}) datos GROUP BY {dia} ORDER BY dia', args)]
    for r in diario:
        r['dia'] = str(r['dia'])
    return render_template('web_reportes.html', pedidos=pedidos, resumen=resumen, estados=ESTADOS,
                           grafica_estados=estados, grafica_diaria=diario, desde=desde, hasta=hasta, modo_local=local())


def celda_csv(valor):
    texto = '' if valor is None else str(valor)
    return "'" + texto if texto.lstrip().startswith(('=', '+', '-', '@')) else texto


@web_bp.get('/reportes.csv')
@protegido('reportes.exportar')
def exportar():
    sql, args, _, _ = filtro_reporte()
    # Límite explícito: nunca exportar silenciosamente un subconjunto.
    total = consulta(f'SELECT count(*) AS total FROM ({sql}) datos', args, una=True)['total']
    if total > 10000:
        abort(422, 'Reduce los filtros: la exportación admite hasta 10 000 pedidos.')
    rows = consulta(sql + ' ORDER BY p.creado_en DESC,p.id DESC', args)
    output = io.StringIO(newline=''); output.write('\ufeff')
    writer = csv.writer(output)
    campos = ('id', 'folio', 'estado', 'total', 'creado_en', 'microhub_id', 'zona')
    writer.writerow(campos)
    writer.writerows([celda_csv(row[c]) for c in campos] for row in rows)
    return Response(output.getvalue(), content_type='text/csv; charset=utf-8', headers={'Content-Disposition': 'attachment; filename=pedidos.csv', 'Cache-Control': 'no-store'})


@web_bp.get('/pedidos/<int:pid>')
@protegido('reportes.ver')
def detalle_pedido(pid):
    sql, args, _, _ = filtro_reporte()
    pedido = consulta(f'SELECT * FROM ({sql}) visible WHERE id=%s', (*args, pid), una=True)
    if not pedido:
        abort(404)
    historial = [] if local() else consulta('SELECT h.fecha,h.estado_anterior,h.estado_nuevo,h.motivo,u.nombre FROM historial_estatus h LEFT JOIN usuario u ON u.id=h.usuario_id WHERE h.pedido_id=%s ORDER BY h.fecha,h.id', (pid,))
    return render_template('web_pedido.html', pedido=pedido, historial=historial, modo_local=local())


@web_bp.route('/notificaciones', methods=['GET', 'POST'])
@protegido('notificaciones.ver')
def notificaciones():
    if request.method == 'POST':
        if 'notificaciones.crear' not in permisos_usuario():
            abort(403)
        titulo = request.form.get('titulo', '').strip()
        mensaje = request.form.get('mensaje', '').strip()
        destino = request.form.get('destinatario_id', type=int)
        if not (1 <= len(titulo) <= 120 and 1 <= len(mensaje) <= 2000) or not destino:
            abort(400, 'Completa título, mensaje y destinatario.')
        if not consulta("SELECT id FROM usuario WHERE id=%s AND estatus='activo'", (destino,), una=True):
            abort(400, 'Destinatario no disponible.')
        ejecutar('INSERT INTO web_notificacion(destinatario_id,emisor_id,titulo,mensaje) VALUES(%s,%s,%s,%s)', (destino, g.usuario['id'], titulo, mensaje))
        flash('Notificación enviada.', 'ok')
        return redirect(url_for('web.notificaciones'))
    solo = request.args.get('lectura', '') == 'pendientes'
    sql = 'SELECT id,titulo,mensaje,creado_en,leido_en FROM web_notificacion WHERE destinatario_id=%s' + (' AND leido_en IS NULL' if solo else '') + ' ORDER BY creado_en DESC,id DESC'
    filas = paginar(sql, (g.usuario['id'],), consulta, filtrar=False)
    destinatarios = consulta("SELECT id,nombre,correo FROM usuario WHERE estatus='activo' ORDER BY nombre") if 'notificaciones.crear' in permisos_usuario() else []
    return render_template('web_notificaciones.html', filas=filas, destinatarios=destinatarios)


@web_bp.post('/notificaciones/<int:nid>/leer')
@protegido('notificaciones.ver')
def leer_notificacion(nid):
    if not consulta('SELECT id FROM web_notificacion WHERE id=%s AND destinatario_id=%s', (nid, g.usuario['id']), una=True):
        abort(404)
    ejecutar('UPDATE web_notificacion SET leido_en=COALESCE(leido_en,CURRENT_TIMESTAMP) WHERE id=%s AND destinatario_id=%s', (nid, g.usuario['id']))
    return redirect(url_for('web.notificaciones'))


def validar_archivo(nombre, contenido):
    nombre = secure_filename(nombre)[:160]
    extension = Path(nombre).suffix.lower()
    firmas = {'.pdf': ('application/pdf', b'%PDF-'), '.png': ('image/png', b'\x89PNG\r\n\x1a\n'), '.jpg': ('image/jpeg', b'\xff\xd8\xff'), '.jpeg': ('image/jpeg', b'\xff\xd8\xff')}
    if not nombre or extension not in firmas or not contenido.startswith(firmas[extension][1]):
        abort(400, 'Adjunta un PDF, PNG o JPEG cuyo contenido coincida con la extensión.')
    if not 1 <= len(contenido) <= 5 * 1024 * 1024:
        abort(400, 'El archivo debe medir entre 1 byte y 5 MB.')
    return nombre, firmas[extension][0]


@web_bp.route('/archivos', methods=['GET', 'POST'])
@protegido('archivos.ver')
def archivos():
    if request.method == 'POST':
        if 'archivos.crear' not in permisos_usuario():
            abort(403)
        archivo = request.files.get('archivo')
        if not archivo:
            abort(400, 'Selecciona un archivo.')
        contenido = archivo.read(5 * 1024 * 1024 + 1)
        nombre, tipo = validar_archivo(archivo.filename or '', contenido)
        ejecutar('INSERT INTO web_archivo(id,propietario_id,nombre,tipo,contenido,tamano) VALUES(%s,%s,%s,%s,%s,%s)',
                 (secrets.token_hex(16), g.usuario['id'], nombre, tipo, contenido, len(contenido)))
        flash('Archivo guardado.', 'ok')
        return redirect(url_for('web.archivos'))
    filas = paginar('SELECT id,nombre,tipo,tamano,creado_en FROM web_archivo WHERE propietario_id=%s ORDER BY creado_en DESC,id DESC', (g.usuario['id'],), consulta, filtrar=False)
    return render_template('web_archivos.html', filas=filas)


@web_bp.get('/archivos/<aid>')
@protegido('archivos.ver')
def descargar(aid):
    archivo = consulta('SELECT nombre,tipo,contenido FROM web_archivo WHERE id=%s AND propietario_id=%s', (aid, g.usuario['id']), una=True)
    if not archivo:
        abort(404)
    response = send_file(io.BytesIO(bytes(archivo['contenido'])), mimetype=archivo['tipo'], as_attachment=True, download_name=archivo['nombre'], max_age=0)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Cache-Control'] = 'private, no-store'
    return response


@web_bp.route('/roles', methods=['GET', 'POST'])
@protegido('roles.ver')
def roles():
    if request.method == 'POST':
        if 'roles.editar' not in permisos_usuario():
            abort(403)
        rid = request.form.get('rol_id', type=int)
        rol = consulta('SELECT id,clave FROM rol WHERE id=%s', (rid,), una=True)
        if not rol:
            abort(404)
        if rol['clave'] == 'administrador':
            abort(403, 'El perfil administrador se conserva para evitar perder acceso.')
        seleccion = set(request.form.getlist('permisos'))
        if not seleccion.issubset(set(PERMISOS) - {'roles.editar', 'roles.ver', 'notificaciones.crear'}):
            abort(400, 'Permisos no delegables.')
        if seleccion.intersection({'reportes.ver', 'reportes.exportar'}) and rol['clave'] not in ('auditor', 'planeador', 'analista', 'supervisor', 'operador'):
            abort(400, 'Este perfil no puede recibir acceso a reportes operativos.')
        # La actualización completa es atómica; nunca existe una ventana sin permisos.
        if local():
            with db_local() as con:
                guardar_permisos(con, rid, seleccion, '?')
        else:
            from nucleo import con_actual, r_cache
            with con_actual() as con, con.cursor() as cur:
                guardar_permisos(cur, rid, seleccion, '%s')
            r_cache.delete(f"cache:permisos:{rol['clave']}")
        flash('Permisos del módulo actualizados; los permisos previos de operación se conservan.', 'ok')
        return redirect(url_for('web.roles'))
    perfiles = [dict(r) for r in consulta('SELECT id,clave,nombre,requiere_microhub FROM rol ORDER BY nombre')]
    asignaciones = consulta('SELECT rp.rol_id,p.clave FROM rol_permiso rp JOIN permiso p ON p.id=rp.permiso_id')
    for r in perfiles:
        r['permisos_web'] = {p['clave'] for p in asignaciones if p['rol_id'] == r['id'] and p['clave'] in PERMISOS}
    return render_template('web_roles.html', perfiles=perfiles, delegables=[p for p in PERMISOS if p not in ('roles.ver', 'roles.editar', 'notificaciones.crear')])


def guardar_permisos(cur, rid, seleccion, marcador):
    claves = ','.join([marcador] * len(PERMISOS))
    cur.execute(f'DELETE FROM rol_permiso WHERE rol_id={marcador} AND permiso_id IN (SELECT id FROM permiso WHERE clave IN ({claves}))', (rid, *PERMISOS))
    for clave in sorted(seleccion):
        cur.execute(f'INSERT INTO rol_permiso(rol_id,permiso_id) SELECT {marcador},id FROM permiso WHERE clave={marcador}', (rid, clave))
