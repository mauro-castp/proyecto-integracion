"""
Servicio de notificaciones · puerto 5124 · contrato v1

  GET    /api/v1/notificaciones                    bandeja propia (solo_no_leidas, tipo)
  GET    /api/v1/notificaciones/conteo             avisos sin leer
  POST   /api/v1/notificaciones/{id}/leer          confirma la lectura de un aviso
  POST   /api/v1/notificaciones/leer-todas         confirma la lectura de todos los pendientes
  DELETE /api/v1/notificaciones/{id}               borra un aviso de la bandeja propia
  POST   /api/v1/notificaciones                    envía un aviso a una persona o a todo un rol (solo JSON)
  GET    /api/v1/notificaciones/preferencias       qué tipos de aviso recibe la persona
  PUT    /api/v1/notificaciones/preferencias/{tipo}   enciende o apaga un tipo

Responsabilidad única: que cada persona reciba, lea y administre sus avisos. Usa la misma tabla
que el portal web (web_notificacion): un aviso enviado desde el web aparece aquí y al revés.
Los avisos automáticos (entrega asignada, pedido cerrado, faltante de inventario, solicitud u
orden de compra) los generan triggers de PostgreSQL, así que llegan sin importar qué componente
cambió el dato, y todos respetan las preferencias de quien los recibe. Los avisos del sistema no
se pueden apagar.
"""
from flask import g, request

from comun import config
from comun.base import (crear_app, documentar, filtro_opcion, leer_cuerpo, leer_paginacion, lista, paginacion,
                        requiere, responder)
from comun.base_errores import ErrorApi, conflicto, filtro_invalido, invalido, no_encontrado
from comun.datos import conexion, consultar
from comun.formatos import fecha
from comun.validar import Campo, validar

app = crear_app("notificaciones", "Microhubs · Notificaciones",
                "Bandeja de avisos compartida con el portal web, envío por persona o por rol y preferencias.", 5124)
P = config.PREFIJO
TIPOS = ["pedido", "entrega", "sistema", "planeacion", "inventario", "abastecimiento"]
REFERENCIAS = ["pedido", "entrega", "candidato", "sistema", "producto", "solicitud", "orden"]
TIPOS_PREFERENCIA = [t for t in TIPOS if t != "sistema"]
CAMPOS = "id, tipo, titulo, mensaje, leido_en, referencia_tipo, referencia_id, creado_en"


def aviso(f):
    return {"id": f["id"], "tipo": f["tipo"], "titulo": f["titulo"], "mensaje": f["mensaje"],
            "leida": f["leido_en"] is not None,
            "referencia": {"tipo": f["referencia_tipo"], "id": f["referencia_id"]} if f["referencia_tipo"] else None,
            "creada_en": fecha(f["creado_en"])}


# --------------------------------------------------------------------
# Bandeja
# --------------------------------------------------------------------
@app.get(f"{P}/notificaciones")
@requiere("notificaciones.ver")
def bandeja():
    pagina, por, desde = leer_paginacion()
    solo = (request.args.get("solo_no_leidas") or "false").lower()
    if solo not in ("true", "false"):
        raise filtro_invalido("solo_no_leidas", "solo_no_leidas debe ser true o false.")
    tipo = filtro_opcion("tipo", TIPOS)
    where, args = ["destinatario_id = %s"], [g.usuario["id"]]
    if solo == "true":
        where.append("leido_en IS NULL")
    if tipo:
        where.append("tipo = %s"); args.append(tipo)
    w = " AND ".join(where)
    total = consultar(f"SELECT count(*) AS n FROM web_notificacion WHERE {w}", args, una=True)["n"]
    filas = consultar(f"SELECT {CAMPOS} FROM web_notificacion WHERE {w} ORDER BY creado_en DESC, id DESC LIMIT %s OFFSET %s",
                      (*args, por, desde))
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


@app.post(f"{P}/notificaciones/leer-todas")
@requiere("notificaciones.ver")
def leer_todas():
    with conexion() as con, con.cursor() as cur:
        cur.execute("UPDATE web_notificacion SET leido_en = now() WHERE destinatario_id = %s AND leido_en IS NULL",
                    (g.usuario["id"],))
        n = cur.rowcount
    return responder({"marcadas": n}, raiz="lectura")


@app.delete(f"{P}/notificaciones/<int:nid>")
@requiere("notificaciones.ver")
def borrar(nid):
    with conexion() as con, con.cursor() as cur:
        cur.execute("DELETE FROM web_notificacion WHERE id = %s AND destinatario_id = %s", (nid, g.usuario["id"]))
        if cur.rowcount == 0:
            raise no_encontrado("No existe ese aviso en tu bandeja.")
    return responder(None, 204)


# --------------------------------------------------------------------
# Envío
# --------------------------------------------------------------------
@app.post(f"{P}/notificaciones")
@requiere("notificaciones.crear")
def enviar():
    d = validar(leer_cuerpo(), [Campo("usuario_id", "int", req=False, nulo=True, minimo=1),
                                Campo("rol", req=False, nulo=True, min_len=1, max_len=40),
                                Campo("microhub_id", "int", req=False, nulo=True, minimo=1),
                                Campo("tipo", opciones=TIPOS), Campo("titulo", min_len=1, max_len=120),
                                Campo("mensaje", min_len=1, max_len=400), Campo("referencia", "obj", req=False, nulo=True)])
    if bool(d.get("usuario_id")) == bool(d.get("rol")):
        raise invalido("usuario_id", "Indica una persona (usuario_id) o un rol, pero no las dos cosas ni ninguna.")
    if d.get("microhub_id") and not d.get("rol"):
        raise invalido("microhub_id", "El microhub solo se usa junto con un rol.")
    ref = None
    if d.get("referencia"):
        ref = validar(d["referencia"], [Campo("tipo", opciones=REFERENCIAS), Campo("id", min_len=1, max_len=40)],
                      prefijo="referencia.")
    if d.get("rol"):
        filtro, args_filtro = "r.clave = %s" + (" AND u.microhub_id = %s" if d.get("microhub_id") else ""), \
            [d["rol"]] + ([d["microhub_id"]] if d.get("microhub_id") else [])
    else:
        filtro, args_filtro = "u.id = %s", [d["usuario_id"]]
    base = f"FROM usuario u JOIN rol r ON r.id = u.rol_id WHERE u.estatus = 'activo' AND {filtro}"
    with conexion() as con, con.cursor() as cur:
        cur.execute(f"SELECT count(*) AS n {base}", args_filtro)
        destinatarios = cur.fetchone()["n"]
        if not destinatarios:
            raise ErrorApi(422, "VALIDACION", "Revisa los datos enviados.",
                           [{"campo": "rol" if d.get("rol") else "usuario_id", "mensaje": "No hay personas activas con ese destino."}])
        cur.execute(f"INSERT INTO web_notificacion (destinatario_id, emisor_id, titulo, mensaje, tipo, referencia_tipo, referencia_id) "
                    f"SELECT u.id, %s, %s, %s, %s, %s, %s {base} AND fn_notif_activa(u.id, %s) RETURNING id",
                    (g.usuario["id"], d["titulo"], d["mensaje"], d["tipo"], ref["tipo"] if ref else None,
                     ref["id"] if ref else None, *args_filtro, d["tipo"]))
        ids = [f["id"] for f in cur.fetchall()]
    return responder({"enviadas": len(ids), "omitidas": destinatarios - len(ids), "ids": ids},
                     201 if ids else 200, raiz="envio")


# --------------------------------------------------------------------
# Preferencias
# --------------------------------------------------------------------
@app.get(f"{P}/notificaciones/preferencias")
@requiere("notificaciones.ver")
def preferencias():
    filas = {f["tipo"]: f["activa"] for f in consultar(
        "SELECT tipo, activa FROM notificacion_preferencia WHERE usuario_id = %s", (g.usuario["id"],))}
    return responder({"datos": [{"tipo": t, "activa": filas.get(t, True)} for t in TIPOS_PREFERENCIA]},
                     raiz="preferencias", items={"datos": "preferencia"})


@app.put(f"{P}/notificaciones/preferencias/<tipo>")
@requiere("notificaciones.ver")
def cambiar_preferencia(tipo):
    if tipo == "sistema":
        raise conflicto("Los avisos del sistema no se pueden apagar.")
    if tipo not in TIPOS_PREFERENCIA:
        raise no_encontrado("Ese tipo de aviso no existe.")
    d = validar(leer_cuerpo("preferencia_nueva"), [Campo("activa", "bool")])
    with conexion() as con, con.cursor() as cur:
        cur.execute("INSERT INTO notificacion_preferencia (usuario_id, tipo, activa) VALUES (%s, %s, %s) "
                    "ON CONFLICT (usuario_id, tipo) DO UPDATE SET activa = EXCLUDED.activa, actualizada_en = now()",
                    (g.usuario["id"], tipo, d["activa"]))
    return responder({"tipo": tipo, "activa": d["activa"]}, raiz="preferencia")


# --------------------------------------------------------------------
# Documentación
# --------------------------------------------------------------------
documentar(app, "GET", f"{P}/notificaciones", "Mi bandeja", permisos=["notificaciones.ver"],
           parametros=[("pagina", "query", "integer", "Página"), ("por_pagina", "query", "integer", "1 a 100"),
                       ("solo_no_leidas", "query", "boolean", "true para ver solo las pendientes"),
                       ("tipo", "query", "string", "pedido | entrega | sistema | planeacion | inventario | abastecimiento")],
           respuestas={200: ("Página de avisos", "NotificacionLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/notificaciones/conteo", "Avisos sin leer", permisos=["notificaciones.ver"],
           respuestas={200: ("Conteo", "Conteo.ok")}, errores=[403])
documentar(app, "POST", f"{P}/notificaciones/{{id}}/leer", "Confirmar la lectura de un aviso", permisos=["notificaciones.ver"],
           parametros=[("id", "path", "integer", "Id del aviso")],
           respuestas={200: ("Aviso marcado", "Notificacion.ok")}, errores=[403, 404])
documentar(app, "POST", f"{P}/notificaciones/leer-todas", "Confirmar la lectura de todos", permisos=["notificaciones.ver"],
           respuestas={200: ("Cuántos avisos se marcaron", "Lectura.ok")}, errores=[403])
documentar(app, "DELETE", f"{P}/notificaciones/{{id}}", "Borrar un aviso de mi bandeja", permisos=["notificaciones.ver"],
           parametros=[("id", "path", "integer", "Id del aviso")],
           respuestas={204: ("Borrado, sin cuerpo", None)}, errores=[403, 404])
documentar(app, "POST", f"{P}/notificaciones", "Enviar un aviso", permisos=["notificaciones.crear"],
           cuerpo="NotificacionNueva.ok", solo_json=True,
           descripcion="A una persona (usuario_id) o a todas las personas activas de un rol (rol, y microhub_id para limitarlo a un "
                       "microhub). Quien apagó ese tipo en sus preferencias no lo recibe y se cuenta en `omitidas`.",
           respuestas={201: ("Cuántos avisos se enviaron", "Envio.ok")}, errores=[400, 403, 422])
documentar(app, "GET", f"{P}/notificaciones/preferencias", "Mis preferencias", permisos=["notificaciones.ver"],
           respuestas={200: ("Un renglón por tipo de aviso", "Preferencias.ok")}, errores=[403])
documentar(app, "PUT", f"{P}/notificaciones/preferencias/{{tipo}}", "Encender o apagar un tipo de aviso", permisos=["notificaciones.ver"],
           parametros=[("tipo", "path", "string", "pedido | entrega | planeacion | inventario | abastecimiento")],
           cuerpo="PreferenciaNueva.ok", descripcion="Los avisos del sistema no se pueden apagar (409).",
           respuestas={200: ("Preferencia guardada", "Preferencia.ok")}, errores=[400, 403, 404, 409, 422])
