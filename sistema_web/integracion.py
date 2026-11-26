"""
integracion.py — El sistema web como cliente de los microservicios.

Flujo (sección 3 y diagrama de integración del Segundo Parcial):

    Sistema web ──HTTP + JWT del usuario──▶ microservicio /api/v1
         ▲                                      │ valida JWT y sesión en Redis
         │                                      │ aplica permisos y reglas
         └──── respuesta JSON o XML ◀───────────┘ PostgreSQL / MongoDB

El web reenvía el MISMO token de sesión del usuario (cookie «sesion»): los
servicios lo aceptan porque la llave y las claves de Redis son comunes, así
que cada servicio aplica el ámbito y los permisos de quien está en el web.
Cada llamada lleva un X-Traza-Id que se muestra en pantalla y queda en el
log del servicio en MongoDB (logs_tecnicos.correlacion_id).

Si un servicio no responde, la página lo dice y el resto del web sigue
funcionando: el sistema web es independiente de los microservicios.

Pantallas:
  /web/servicios                    estado de los servicios, resúmenes de MongoDB y una respuesta XML
  /web/servicios/pedido/<id>        pedido, historial, entrega, recorrido GPS y evidencias desde los servicios;
                                    adjuntar un documento al pedido (se guarda en MongoDB vía documentos)
  /web/servicios/documento/<id>     ver o descargar un documento guardado en MongoDB
"""
import base64
import io
import json
import os
import secrets
import time
import urllib.error
import urllib.request
import uuid

from flask import (Blueprint, Response, abort, flash, g, redirect, render_template, request, send_file, session,
                   url_for)

servicios_bp = Blueprint("servicios", __name__, url_prefix="/web/servicios")

PUERTOS = {"auth": 5101, "usuarios": 5102, "productos": 5103, "pedidos": 5104, "entregas": 5105,
           "planeacion": 5106, "documentos": 5107, "zonas": 5108, "microhubs": 5109, "seguimiento": 5110,
           "inventario": 5111, "precios": 5112, "proveedores": 5113, "abastecimiento": 5114,
           "demanda": 5115, "cobertura": 5116, "capacidad": 5117, "rutas": 5118, "costos": 5119,
           "punto-equilibrio": 5120, "simulacion": 5121, "surtido": 5122, "notificaciones": 5124,
           "reportes": 5123, "sincronizacion": 5125, "auditoria-monitoreo": 5126}
# Dentro de docker-compose.integrado.yml cada servicio se alcanza por su nombre en la red interna.
PLANTILLA = os.environ.get("MICROSERVICIOS_URL", "http://{servicio}:{puerto}")
TIEMPO_ESPERA = float(os.environ.get("MICROSERVICIOS_TIEMPO", "4"))


@servicios_bp.app_context_processor
def _contexto():
    return {"puertos": PUERTOS}


class Llamada:
    """Resultado de una petición a un servicio, con lo necesario para mostrarla como evidencia."""

    def __init__(self, servicio, metodo, ruta, status=None, datos=None, crudo=b"", traza="", ms=0, error=None):
        self.servicio, self.metodo, self.ruta = servicio, metodo, ruta
        self.status, self.datos, self.crudo, self.traza, self.ms, self.error = status, datos, crudo, traza, ms, error

    @property
    def ok(self):
        return self.status is not None and 200 <= self.status < 300

    @property
    def mensaje(self):
        if self.error:
            return self.error
        if isinstance(self.datos, dict) and "error" in self.datos:
            return self.datos["error"].get("mensaje", "")
        return ""


def url(servicio, ruta):
    return PLANTILLA.format(servicio=servicio, puerto=PUERTOS[servicio]) + "/api/v1/" + ruta.lstrip("/")


def llamar(servicio, metodo, ruta, cuerpo=None, xml=False, token=True):
    """Petición HTTP a un microservicio con el JWT del usuario del web."""
    traza = str(uuid.uuid4())
    enc = {"Accept": "application/xml" if xml else "application/json", "X-Traza-Id": traza}
    if token and request.cookies.get("sesion"):
        enc["Authorization"] = "Bearer " + request.cookies["sesion"]
    datos_envio = None
    if cuerpo is not None:
        datos_envio = json.dumps(cuerpo).encode("utf-8")
        enc["Content-Type"] = "application/json"
    req = urllib.request.Request(url(servicio, ruta), data=datos_envio, headers=enc, method=metodo)
    inicio = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=TIEMPO_ESPERA) as r:
            status, crudo = r.status, r.read()
    except urllib.error.HTTPError as e:
        status, crudo = e.code, e.read()
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return Llamada(servicio, metodo, ruta, traza=traza, ms=int((time.perf_counter() - inicio) * 1000),
                       error=f"El servicio {servicio} no responde ({getattr(e, 'reason', e)}).")
    ms = int((time.perf_counter() - inicio) * 1000)
    datos = None
    if crudo and not xml:
        try:
            datos = json.loads(crudo.decode("utf-8"))
        except ValueError:
            datos = None
    return Llamada(servicio, metodo, ruta, status, datos, crudo, traza, ms)


def _requiere_sesion():
    if not getattr(g, "usuario", None):
        return redirect(url_for("auth.entrar"))
    return None


def _csrf_valido():
    esperado = session.get("web_csrf", "")
    return esperado and secrets.compare_digest(esperado, request.form.get("csrf", ""))


# --------------------------------------------------------------------
@servicios_bp.get("")
def tablero():
    """Estado de los microservicios y datos de MongoDB obtenidos A TRAVÉS de ellos (solo administrador)."""
    if (r := _requiere_sesion()):
        return r
    from web_ampliado import permisos_usuario
    if "roles.ver" not in permisos_usuario():
        abort(403)
    salud = []
    for s in PUERTOS:
        ll = llamar(s, "GET", "salud", token=False)
        salud.append({"servicio": s, "puerto": PUERTOS[s], "llamada": ll,
                      "estado": (ll.datos or {}).get("estado", "sin respuesta"),
                      "dependencias": (ll.datos or {}).get("dependencias", {})})
    resumen_docs = llamar("documentos", "GET", "documentos/resumen")
    resumen_sim = llamar("planeacion", "GET", "simulaciones/resumen")
    ejemplo_xml = llamar("zonas", "GET", "zonas?pagina=1&por_pagina=2", xml=True)
    host = request.host.split(":")[0]
    return render_template("web_servicios.html", salud=salud, resumen_docs=resumen_docs, resumen_sim=resumen_sim,
                           ejemplo_xml=ejemplo_xml, host=host)


@servicios_bp.route("/monitoreo", methods=["GET", "POST"])
def monitoreo():
    """Panel central de monitoreo: lo que dice el servicio auditoria-monitoreo sobre la salud de todos los servicios."""
    if (r := _requiere_sesion()):
        return r
    from web_ampliado import permisos_usuario
    permisos = permisos_usuario()
    if "monitoreo.ver" not in permisos:
        abort(403)
    if request.method == "POST":
        if not _csrf_valido():
            abort(400, "Formulario vencido; recarga la página.")
        if "monitoreo.operar" not in permisos:
            abort(403)
        if request.form.get("accion") == "verificar":
            ll = llamar("auditoria-monitoreo", "POST", "monitoreo/verificaciones", {})
            flash(f"Verificación terminada: {ll.datos['ok']} ok, {ll.datos['degradados']} degradados, {ll.datos['caidos']} caídos." if ll.ok
                  else f"No se pudo verificar: {ll.mensaje or ll.status}", "ok" if ll.ok else "alto")
        elif request.form.get("accion") == "reconocer" and (request.form.get("alerta") or "").isdigit():
            ll = llamar("auditoria-monitoreo", "POST", f"monitoreo/alertas/{int(request.form['alerta'])}/reconocer", {})
            flash("Alerta reconocida." if ll.ok else f"No se pudo reconocer: {ll.mensaje or ll.status}", "ok" if ll.ok else "alto")
        return redirect(url_for("servicios.monitoreo"))
    estado = llamar("auditoria-monitoreo", "GET", "monitoreo/estado")
    alertas = llamar("auditoria-monitoreo", "GET", "monitoreo/alertas?estado=abiertas&por_pagina=50")
    cerradas = llamar("auditoria-monitoreo", "GET", "monitoreo/alertas?estado=cerradas&por_pagina=10")
    disponibilidad = llamar("auditoria-monitoreo", "GET", "monitoreo/disponibilidad?horas=24")
    if estado.status in (401, 403):
        abort(estado.status)
    return render_template("web_monitoreo.html", estado=estado, alertas=alertas, cerradas=cerradas, disponibilidad=disponibilidad,
                           puede_operar="monitoreo.operar" in permisos,
                           disp={s["servicio"]: s for s in (disponibilidad.datos or {}).get("servicios", [])} if disponibilidad.ok else {},
                           host=request.host.split(":")[0])


@servicios_bp.get("/monitoreo/<nombre>")
def monitoreo_historial(nombre):
    """Historial de disponibilidad de un servicio."""
    if (r := _requiere_sesion()):
        return r
    from web_ampliado import permisos_usuario
    if "monitoreo.ver" not in permisos_usuario():
        abort(403)
    if nombre not in PUERTOS:
        abort(404)
    horas = 6
    historial = llamar("auditoria-monitoreo", "GET", f"monitoreo/servicios/{nombre}/historial?horas={horas}&por_pagina=200")
    disponibilidad = llamar("auditoria-monitoreo", "GET", f"monitoreo/disponibilidad?horas={horas}")
    resumen = next((s for s in (disponibilidad.datos or {}).get("servicios", []) if s["servicio"] == nombre), None) if disponibilidad.ok else None
    return render_template("web_monitoreo_historial.html", nombre=nombre, horas=horas, historial=historial, resumen=resumen)


@servicios_bp.route("/pedido/<int:pid>", methods=["GET", "POST"])
def pedido(pid):
    """El pedido visto a través de los servicios de pedidos, entregas y documentos."""
    if (r := _requiere_sesion()):
        return r
    if request.method == "POST":
        if not _csrf_valido():
            abort(400, "Formulario vencido; recarga la página.")
        archivo = request.files.get("archivo")
        if not archivo:
            abort(400, "Selecciona un archivo.")
        contenido = archivo.read(5 * 1024 * 1024 + 1)
        from web_ampliado import validar_archivo
        nombre, tipo = validar_archivo(archivo.filename or "", contenido)
        ll = llamar("documentos", "POST", "documentos", {
            "nombre": nombre, "tipo_mime": tipo, "contenido_base64": base64.b64encode(contenido).decode(),
            "referencia": {"tipo": "pedido", "id": str(pid)}})
        if ll.ok:
            flash(f"Documento guardado en MongoDB por el servicio de documentos (id {ll.datos['id']}, "
                  f"traza {ll.traza}).", "ok")
        else:
            flash(f"El servicio de documentos respondió {ll.status or 'sin conexión'}: {ll.mensaje}", "alto")
        return redirect(url_for("servicios.pedido", pid=pid))

    llamadas = []
    det = llamar("pedidos", "GET", f"pedidos/{pid}")
    llamadas.append(det)
    if det.status in (403, 404):
        abort(det.status)
    hist = llamar("pedidos", "GET", f"pedidos/{pid}/historial")
    llamadas.append(hist)
    ent = llamar("entregas", "GET", f"entregas?pedido_id={pid}&por_pagina=1")
    llamadas.append(ent)
    entrega = (ent.datos or {}).get("datos", [None])[0] if ent.ok and (ent.datos or {}).get("datos") else None
    recorrido = docs_entrega = None
    if entrega:
        recorrido = llamar("seguimiento", "GET", f"seguimiento/{entrega['id']}/recorrido")
        docs_entrega = llamar("documentos", "GET", f"documentos?referencia_tipo=entrega&referencia_id={entrega['id']}")
        llamadas += [recorrido, docs_entrega]
    docs_pedido = llamar("documentos", "GET", f"documentos?referencia_tipo=pedido&referencia_id={pid}")
    llamadas.append(docs_pedido)
    return render_template("web_servicios_pedido.html", pid=pid, det=det, hist=hist, entrega=entrega,
                           recorrido=recorrido, docs_entrega=docs_entrega, docs_pedido=docs_pedido, llamadas=llamadas)


@servicios_bp.get("/documento/<did>")
def documento(did):
    """Contenido de un documento de MongoDB, servido por el web a partir del servicio de documentos."""
    if (r := _requiere_sesion()):
        return r
    if not (len(did) == 24 and all(c in "0123456789abcdef" for c in did)):
        abort(404)
    ll = llamar("documentos", "GET", f"documentos/{did}/contenido")
    if not ll.ok:
        abort(ll.status if ll.status in (403, 404) else 502)
    d = ll.datos
    contenido = base64.b64decode(d["contenido_base64"])
    resp = send_file(io.BytesIO(contenido), mimetype=d["tipo_mime"], as_attachment=request.args.get("ver") != "1",
                     download_name=d["nombre"], max_age=0)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Cache-Control"] = "private, no-store"
    return resp
