"""
Servicio de notificaciones · puerto 5108 · contrato v1

  GET  /api/v1/notificaciones              bandeja propia (solo_no_leidas=true para filtrar)
  GET  /api/v1/notificaciones/conteo       número de avisos sin leer
  POST /api/v1/notificaciones/{id}/leer    marcar como leída
  POST /api/v1/notificaciones              enviar un aviso (notificaciones.crear; solo JSON)
  DELETE /api/v1/notificaciones/{id}       borrar un aviso de la bandeja propia

Usa la MISMA tabla que el portal web (web_notificacion): un aviso enviado
desde el web aparece en la app y al revés. Los avisos automáticos (entrega
asignada al repartidor, pedido cerrado para el cliente) los generan
triggers de PostgreSQL, así que llegan sin importar qué componente cambió
el dato.
"""
from flask import g, request

from comun import config
from comun.base import (crear_app, documentar, leer_cuerpo, leer_paginacion, lista, paginacion, requiere,
                        responder)
from comun.base_errores import ErrorApi, filtro_invalido, no_encontrado
from comun.datos import conexion, consultar
from comun.formatos import fecha
from comun.validar import Campo, validar

app = crear_app("notificaciones", "Microhubs · Notificaciones", "Bandeja de avisos compartida con el portal web.", 5108)
P = config.PREFIJO
TIPOS = ["pedido", "entrega", "sistema", "planeacion"]
REFERENCIAS = ["pedido", "entrega", "candidato", "sistema"]
CAMPOS = "id, tipo, titulo, mensaje, leido_en, referencia_tipo, referencia_id, creado_en"


def aviso(f):
    return {"id": f["id"], "tipo": f["tipo"], "titulo": f["titulo"], "mensaje": f["mensaje"],
            "leida": f["leido_en"] is not None,
            "referencia": {"tipo": f["referencia_tipo"], "id": f["referencia_id"]} if f["referencia_tipo"] else None,
            "creada_en": fecha(f["creado_en"])}


@app.get(f"{P}/notificaciones")
@requiere("notificaciones.ver")
def bandeja():
    pagina, por, desde = leer_paginacion()
    solo = (request.args.get("solo_no_leidas") or "false").lower()
    if solo not in ("true", "false"):
        raise filtro_invalido("solo_no_leidas", "solo_no_leidas debe ser true o false.")
    w = "destinatario_id = %s" + (" AND leido_en IS NULL" if solo == "true" else "")
    total = consultar(f"SELECT count(*) AS n FROM web_notificacion WHERE {w}", (g.usuario["id"],), una=True)["n"]
    filas = consultar(f"SELECT {CAMPOS} FROM web_notificacion WHERE {w} ORDER BY creado_en DESC, id DESC "
                      "LIMIT %s OFFSET %s", (g.usuario["id"], por, desde))
    return lista(filas, paginacion(pagina, por, total), "notificacion", "notificaciones", aviso)


@app.get(f"{P}/notificaciones/conteo")
@requiere("notificaciones.ver")
def conteo():
    n = consultar("SELECT count(*) AS n FROM web_notificacion WHERE destinatario_id = %s AND leido_en IS NULL",
                  (g.usuario["id"],), una=True)["n"]
    return responder({"no_leidas": n}, raiz="conteo")


@app.post(f"{P}/notificaciones/<int:nid>/leer")
@requiere("notificaciones.ver")
def leer(nid):
    with conexion() as con, con.cursor() as cur:
        cur.execute(f"UPDATE web_notificacion SET leido_en = COALESCE(leido_en, now()) "
                    f"WHERE id = %s AND destinatario_id = %s RETURNING {CAMPOS}", (nid, g.usuario["id"]))
        f = cur.fetchone()
    if not f:
        raise no_encontrado("No existe ese aviso en tu bandeja.")
    return responder(aviso(f), raiz="notificacion")


@app.delete(f"{P}/notificaciones/<int:nid>")
@requiere("notificaciones.ver")
def borrar(nid):
    with conexion() as con, con.cursor() as cur:
        cur.execute("DELETE FROM web_notificacion WHERE id = %s AND destinatario_id = %s", (nid, g.usuario["id"]))
        if cur.rowcount == 0:
            raise no_encontrado("No existe ese aviso en tu bandeja.")
    return responder(None, 204)


@app.post(f"{P}/notificaciones")
@requiere("notificaciones.crear")
def crear():
    cuerpo = leer_cuerpo()
    d = validar(cuerpo, [Campo("usuario_id", "int", minimo=1), Campo("tipo", opciones=TIPOS),
                         Campo("titulo", min_len=1, max_len=120), Campo("mensaje", min_len=1, max_len=400),
                         Campo("referencia", "obj", req=False, nulo=True)])
    ref = None
    if d.get("referencia"):
        ref = validar(d["referencia"], [Campo("tipo", opciones=REFERENCIAS), Campo("id", min_len=1, max_len=40)],
                      prefijo="referencia.")
    destino = consultar("SELECT id FROM usuario WHERE id = %s AND estatus = 'activo'", (d["usuario_id"],), una=True)
    if not destino:
        raise ErrorApi(422, "VALIDACION", "Revisa los datos enviados.",
                       [{"campo": "usuario_id", "mensaje": "No existe un usuario activo con ese id."}])
    with conexion() as con, con.cursor() as cur:
        cur.execute(f"INSERT INTO web_notificacion (destinatario_id, emisor_id, titulo, mensaje, tipo, referencia_tipo, "
                    f"referencia_id) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING {CAMPOS}",
                    (d["usuario_id"], g.usuario["id"], d["titulo"], d["mensaje"], d["tipo"],
                     ref["tipo"] if ref else None, ref["id"] if ref else None))
        f = cur.fetchone()
    return responder(aviso(f), 201, raiz="notificacion")


documentar(app, "GET", f"{P}/notificaciones", "Mi bandeja", permisos=["notificaciones.ver"],
           parametros=[("pagina", "query", "integer", "Página"), ("por_pagina", "query", "integer", "1 a 100"),
                       ("solo_no_leidas", "query", "boolean", "true para ver solo las pendientes")],
           respuestas={200: ("Página de avisos", "NotificacionLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/notificaciones/conteo", "Avisos sin leer", permisos=["notificaciones.ver"],
           respuestas={200: ("Conteo", "Conteo.ok")}, errores=[403])
documentar(app, "POST", f"{P}/notificaciones/{{id}}/leer", "Marcar como leída", permisos=["notificaciones.ver"],
           parametros=[("id", "path", "integer", "Id del aviso")],
           respuestas={200: ("Aviso marcado", "Notificacion.ok")}, errores=[403, 404])
documentar(app, "POST", f"{P}/notificaciones", "Enviar un aviso", permisos=["notificaciones.crear"],
           cuerpo="NotificacionNueva.ok", solo_json=True,
           descripcion="Aviso manual (administrador). Los avisos automáticos los generan triggers de PostgreSQL.",
           respuestas={201: ("Aviso creado", "Notificacion.ok")}, errores=[400, 403, 422])
documentar(app, "DELETE", f"{P}/notificaciones/{{id}}", "Borrar un aviso de mi bandeja", permisos=["notificaciones.ver"],
           parametros=[("id", "path", "integer", "Id del aviso")],
           respuestas={204: ("Borrado, sin cuerpo", None)}, errores=[403, 404])
