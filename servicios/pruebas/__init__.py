"""Pruebas de los microservicios. El trabajador de fondo de simulación no corre durante las pruebas: las pruebas lo invocan a mano."""
import os

os.environ.setdefault("SIM_TRABAJADOR", "0")
