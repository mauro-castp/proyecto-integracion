"""
calculo.py — Las fórmulas de planeación del portal web, para que servicio y portal den los mismos números.

sistema_web/planeacion_calc.py (funciones puras: capacidad, punto de equilibrio, sensibilidad, ABC, rutas…) es la
fuente única. En Docker el Dockerfile lo copia a /app/web; en desarrollo se lee de sistema_web/.
"""
import sys
from pathlib import Path

_web = Path("/app/web") if Path("/app/web").is_dir() else Path(__file__).resolve().parents[2] / "sistema_web"
if str(_web) not in sys.path:
    sys.path.append(str(_web))          # al final: el módulo «planeacion» del web no debe tapar al paquete del servicio

import planeacion_calc as pc            # noqa: E402,F401
