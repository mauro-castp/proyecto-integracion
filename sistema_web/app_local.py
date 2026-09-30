"""Modo de demostración: Flask + SQLite, sin Docker/PostgreSQL/Redis."""
import os
os.environ["MODO_LOCAL"] = "1"

from flask import Blueprint, Flask, redirect, url_for
from productos_crud import inicializar_local, productos_bp
from catalogos_crud import catalogos_bp, inicializar_local as inicializar_catalogos
from planeacion import planeacion_bp

app = Flask(__name__)
app.config["SECRET_KEY"] = "solo-desarrollo-local"
app.register_blueprint(productos_bp)
app.register_blueprint(catalogos_bp)
app.register_blueprint(planeacion_bp)

publico = Blueprint("publico", __name__)
auth = Blueprint("auth", __name__)

@publico.route("/")
def catalogo():
    return redirect(url_for("productos.lista"))

@publico.route("/cobertura")
def cobertura():
    return redirect(url_for("productos.lista"))

@auth.route("/salir", methods=["POST"])
def salir():
    return redirect(url_for("productos.lista"))

app.register_blueprint(publico)
app.register_blueprint(auth)

@app.context_processor
def contexto_local():
    permisos = {"productos.ver", "productos.crear", "productos.editar", "productos.baja",
                "microhubs.ver", "microhubs.crear", "microhubs.editar", "microhubs.baja",
                "zonas.ver", "zonas.crear", "zonas.editar", "zonas.baja",
                "usuarios.ver", "usuarios.crear", "usuarios.editar", "usuarios.baja",
                "simulacion.ver", "simulacion.ejecutar"}
    return {"usuario": {"nombre": "Modo local", "rol": "administrador"}, "permisos": permisos}

@app.template_filter("dinero")
def dinero(v):
    return f"${float(v or 0):,.2f}"

inicializar_local()
inicializar_catalogos()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
