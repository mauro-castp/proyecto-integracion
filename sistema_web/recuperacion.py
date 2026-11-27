"""
recuperacion.py — Recuperación de contraseña del portal.

  /recuperar                  la persona escribe su correo. La respuesta es la misma exista o no la cuenta.
  /restablecer/<token>        con el enlace recibido escribe una contraseña nueva.

El enlace es aleatorio, de un solo uso, vence a los 30 minutos y en Redis solo se guarda su huella SHA-256. Se entrega por correo si hay un
servidor SMTP configurado (SMTP_HOST, SMTP_PUERTO, SMTP_USUARIO, SMTP_CLAVE, SMTP_REMITENTE); si no, llega como aviso a las personas
administradoras, que comprueban la identidad y se lo hacen llegar. Al cambiar la contraseña se cierran todas las sesiones de la cuenta.
Todo queda en la bitácora.
"""
import hashlib
import os
import re
import secrets
import smtplib
from email.message import EmailMessage

from flask import Blueprint, abort, current_app, flash, g, redirect, render_template, request, url_for

from nucleo import conexion, consultar, hashear, r_sesion
from web_ampliado import csrf

recuperacion = Blueprint("recuperacion", __name__)
MINUTOS = 30
PEDIDOS_POR_CORREO = 3                     # solicitudes cada 15 minutos
RESPUESTA = ("Si la cuenta existe, generamos un enlace para cambiar la contraseña. Vence en 30 minutos. "
             "Si no te llega, pídeselo a quien administra el sistema.")


def _llave(token):
    return "auth:recuperar:" + hashlib.sha256(token.encode()).hexdigest()


def _csrf_valido():
    return secrets.compare_digest(csrf(), request.form.get("csrf", ""))


def _bitacora(usuario_id, detalle, exitoso=True, correo=None):
    with conexion(rol="sistema", autocommit=True) as con, con.cursor() as cur:
        cur.execute("INSERT INTO auditoria (usuario_id, modulo, accion, entidad, entidad_id, detalle, exitoso, ip_origen, correo_intento) "
                    "VALUES (%s, 'auth', 'modificacion', 'usuario', %s, %s, %s, %s, %s)",
                    (usuario_id, str(usuario_id) if usuario_id else None, detalle, exitoso, request.remote_addr, correo))


def _enviar_correo(destino, enlace):
    servidor = os.environ.get("SMTP_HOST")
    if not servidor:
        return False
    m = EmailMessage()
    m["Subject"] = "Cambia tu contraseña · Microhubs"
    m["From"] = os.environ.get("SMTP_REMITENTE", os.environ.get("SMTP_USUARIO", ""))
    m["To"] = destino
    m.set_content(f"Para cambiar tu contraseña entra en:\n\n{enlace}\n\nEl enlace vence en {MINUTOS} minutos y sirve una sola vez. "
                  "Si no lo pediste, ignora este mensaje.")
    try:
        with smtplib.SMTP(servidor, int(os.environ.get("SMTP_PUERTO", "587")), timeout=10) as s:
            s.starttls()
            if os.environ.get("SMTP_USUARIO"):
                s.login(os.environ["SMTP_USUARIO"], os.environ.get("SMTP_CLAVE", ""))
            s.send_message(m)
        return True
    except (smtplib.SMTPException, OSError) as e:
        current_app.logger.error("recuperación: no se pudo enviar el correo (%s)", type(e).__name__)
        return False


def _avisar_administradores(u, enlace):
    mensaje = (f"{u['nombre']} ({u['correo']}) pidió cambiar su contraseña. Comprueba que sea esa persona y envíale este enlace, que vence en "
               f"{MINUTOS} minutos y sirve una sola vez: {enlace}")
    with conexion(rol="sistema") as con, con.cursor() as cur:
        cur.execute("INSERT INTO web_notificacion (destinatario_id, emisor_id, titulo, mensaje) "
                    "SELECT a.id, %s, 'Recuperación de contraseña', %s FROM usuario a JOIN rol r ON r.id = a.rol_id "
                    "WHERE r.clave = 'administrador' AND a.estatus = 'activo'", (u["id"], mensaje[:2000]))


@recuperacion.route("/recuperar", methods=["GET", "POST"])
def recuperar():
    if request.method == "GET":
        return render_template("recuperar.html", token_formulario=csrf())
    if not _csrf_valido():
        abort(400, "Formulario vencido; recarga la página.")
    correo = (request.form.get("correo") or "").strip().lower()[:160]
    contador = "auth:recuperar:pedidos:" + hashlib.sha256(correo.encode()).hexdigest()[:24]
    pedidos = r_sesion.incr(contador)
    if pedidos == 1:
        r_sesion.expire(contador, 15 * 60)
    if pedidos > PEDIDOS_POR_CORREO:
        flash("Ya se pidieron varios enlaces para ese correo. Espera unos minutos.", "alto")
        return render_template("recuperar.html", token_formulario=csrf()), 429
    u = consultar("SELECT id, nombre, correo FROM usuario WHERE lower(correo) = %s AND estatus = 'activo'", (correo,), una=True)
    if u:
        token = secrets.token_urlsafe(32)
        r_sesion.setex(_llave(token), MINUTOS * 60, str(u["id"]))
        enlace = url_for("recuperacion.restablecer", token=token, _external=True)
        if not _enviar_correo(u["correo"], enlace):
            _avisar_administradores(u, enlace)
        _bitacora(u["id"], "Solicitud de recuperación de contraseña.", correo=correo)
    else:
        _bitacora(None, "Solicitud de recuperación para una cuenta que no existe o está inactiva.", exitoso=False, correo=correo)
    flash(RESPUESTA, "ok")
    return redirect(url_for("auth.entrar"))


def problema_de_clave(clave, repetida):
    if clave != repetida:
        return "Las dos contraseñas no coinciden."
    if len(clave) < 8 or len(clave.encode()) > 72:
        return "La contraseña debe tener de 8 a 72 caracteres."
    if not re.search(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]", clave) or not re.search(r"\d", clave):
        return "La contraseña necesita al menos una letra y un número."
    return None


def cerrar_sesiones(usuario_id):
    """Revoca los accesos vivos y borra las renovaciones de la cuenta: web, servicios y apps vuelven a pedir inicio de sesión."""
    for jti in r_sesion.smembers(f"auth:sesion:{usuario_id}"):
        r_sesion.setex(f"auth:jti:revocado:{jti}", 24 * 3600, "1")
    r_sesion.delete(f"auth:sesion:{usuario_id}")
    for llave in r_sesion.scan_iter("auth:refresh:*"):
        if r_sesion.hget(llave, "usuario_id") == str(usuario_id):
            r_sesion.delete(llave)


@recuperacion.route("/restablecer/<token>", methods=["GET", "POST"])
def restablecer(token):
    if len(token) > 100 or not r_sesion.exists(_llave(token)):
        flash("El enlace ya se usó o venció. Pide uno nuevo.", "alto")
        return redirect(url_for("recuperacion.recuperar"))
    if request.method == "GET":
        return render_template("restablecer.html", token_formulario=csrf())
    if not _csrf_valido():
        abort(400, "Formulario vencido; recarga la página.")
    clave = request.form.get("clave") or ""
    problema = problema_de_clave(clave, request.form.get("repetida") or "")
    if problema:
        flash(problema, "alto")
        return render_template("restablecer.html", token_formulario=csrf()), 422
    uid = r_sesion.getdel(_llave(token))                      # de un solo uso: quien llegue segundo ya no lo encuentra
    if not uid:
        flash("El enlace ya se usó o venció. Pide uno nuevo.", "alto")
        return redirect(url_for("recuperacion.recuperar"))
    u = consultar("SELECT id, correo FROM usuario WHERE id = %s AND estatus = 'activo'", (int(uid),), una=True)
    if not u:
        abort(404)
    with conexion(rol="sistema") as con, con.cursor() as cur:
        cur.execute("UPDATE usuario SET hash_contrasena = %s, intentos_fallidos = 0, actualizado_en = now() WHERE id = %s",
                    (hashear(clave), u["id"]))
    cerrar_sesiones(u["id"])
    r_sesion.delete(f"auth:bloqueo:{u['correo'].lower()}", f"auth:intentos:{u['correo'].lower()}")
    _bitacora(u["id"], "Contraseña cambiada con enlace de recuperación; sesiones cerradas.")
    g.usuario = None
    flash("Contraseña cambiada. Entra con la nueva.", "ok")
    return redirect(url_for("auth.entrar"))
