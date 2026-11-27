"""
calculo.py — Las fórmulas de planeación (capacidad, punto de equilibrio, sensibilidad, ABC, rutas…) de los microservicios.

comun/planeacion_calc.py son funciones puras. El portal tiene su propia copia (sistema_web/planeacion_calc.py) y la prueba
test_unitarias_ola2.IndependenciaDelPortal exige que sean idénticas: mismos números sin que los servicios dependan del web.
"""
from . import planeacion_calc as pc  # noqa: F401
