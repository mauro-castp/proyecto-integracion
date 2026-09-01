"""
app.py — Punto de entrada de la aplicación web
Plataforma de Microhubs · Codex Innovations · Equipo 04

    flask --app app run --debug        (desarrollo)
    gunicorn -b 0.0.0.0:5000 app:app   (contenedor)
"""
from flask import Flask, g, request, render_template

from nucleo import Config, leer_token, permisos_de
from rutas import publico, auth, cliente, operacion, admin

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(publico)
app.register_blueprint(auth)
app.register_blueprint(cliente)
app.register_blueprint(operacion)
app.register_blueprint(admin)


@app.before_request
def cargar_usuario():
    g.usuario = leer_token(request.cookies.get("sesion"))


@app.context_processor
def contexto():
    """El menú se construye desde la tabla de permisos (RF02).

    Ojo: esto solo decide qué ENLACES se dibujan. El cierre real de cada
    ruta lo hace el decorador @requiere. Entrar por URL a una función
    retirada devuelve 403 aunque la opción ya no aparezca (HU10 CA2).
    """
    u = getattr(g, "usuario", None)
    return {"usuario": u, "permisos": permisos_de(u["rol"]) if u else set()}


@app.route("/salud")
def salud():
    """RF47. Endpoint de diagnóstico: informa si el proceso responde y si
    alcanza sus dependencias críticas. No expone detalle interno."""
    from nucleo import consultar, r_sesion
    estado = {"servicio": "web", "postgres": "no", "redis": "no"}
    try:
        consultar("SELECT 1 AS v", una=True)
        estado["postgres"] = "si"
    except Exception:
        pass
    try:
        r_sesion.ping()
        estado["redis"] = "si"
    except Exception:
        pass
    listo = estado["postgres"] == "si" and estado["redis"] == "si"
    return estado, (200 if listo else 503)


@app.errorhandler(403)
def prohibido(_):
    return render_template("403.html"), 403


@app.errorhandler(404)
def no_encontrado(_):
    return render_template("404.html"), 404


@app.template_filter("dinero")
def dinero(v):
    return f"${float(v or 0):,.2f}"


@app.template_filter("fecha")
def fecha(v):
    return v.strftime("%d/%m/%Y %H:%M") if v else ""


ESTADOS = {
    "creado": ("Creado", "info"),
    "pendiente_asignacion": ("Pendiente de asignación", "pend"),
    "asignado": ("Asignado", "asig"),
    "en_preparacion": ("En preparación", "prep"),
    "en_ruta": ("En ruta", "ruta"),
    "entregado": ("Entregado", "ent"),
    "entrega_parcial": ("Entrega parcial", "ruta"),
    "entrega_fallida": ("No entregado", "fall"),
    "cancelado": ("Cancelado", "pend"),
}


@app.template_filter("estado")
def estado(v):
    return ESTADOS.get(v, (v, "info"))[0]


@app.template_filter("clase_estado")
def clase_estado(v):
    return ESTADOS.get(v, (v, "info"))[1]


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
