"""
supuestos.py — Los supuestos de un modelo, con su valor, de dónde salen y cómo se corrigen con datos reales.

El valor vive en la tabla configuracion (RN40: ningún peso, umbral ni productividad es una constante en el código).
supuesto_documentado agrega el origen (medido, supuesto o normativo), la justificación y cómo calibrarlo. Cada
servicio de análisis publica los suyos en GET /<servicio>/supuestos y los demás cálculos devuelven cuáles usaron.
"""
from .datos import consultar


def valores(defectos):
    """{clave: float} con el valor global de cada clave; la que no existe usa el valor por omisión."""
    filas = consultar("SELECT clave, valor FROM configuracion WHERE ambito = 'global' AND clave = ANY(%s)", (list(defectos),))
    salida = dict(defectos)
    for f in filas:
        try:
            salida[f["clave"]] = float(f["valor"])
        except (TypeError, ValueError):
            pass
    return salida


def listar(claves):
    """Renglones documentados de las claves indicadas, en el formato del contrato."""
    filas = consultar(
        "SELECT c.clave, c.valor, c.unidad, COALESCE(d.origen, 'supuesto') AS origen, "
        "COALESCE(d.justificacion, c.descripcion, '') AS justificacion, d.como_calibrar "
        "FROM configuracion c LEFT JOIN supuesto_documentado d ON d.clave = c.clave "
        "WHERE c.ambito = 'global' AND c.clave = ANY(%s) ORDER BY c.clave", (list(claves),))
    return [{"clave": f["clave"], "valor": f["valor"], "unidad": f["unidad"], "origen": f["origen"],
             "justificacion": f["justificacion"], "como_calibrar": f["como_calibrar"]} for f in filas]


def usados(valores_usados, modificados=()):
    """[{clave, valor, modificado}]: qué valores usó un cálculo y cuáles se cambiaron en la petición."""
    return [{"clave": k, "valor": float(v), "modificado": k in modificados} for k, v in valores_usados.items()]
