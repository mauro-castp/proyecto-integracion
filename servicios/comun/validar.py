"""
validar.py — Validación declarativa de los cuerpos de entrada.

Las mismas restricciones que declara el XSD (tipos, rangos, longitudes,
enumeraciones) se aplican también a JSON, porque la app Android no pasa
por un XSD. Devuelve todos los errores juntos en `detalles`, con el campo y
el motivo, como pide el contrato (Error.validacion).
"""
import datetime as dt
import re
from decimal import Decimal, InvalidOperation

from .base_errores import ErrorApi

_FALTA = object()


class Campo:
    def __init__(self, nombre, tipo="str", req=True, minimo=None, maximo=None, min_len=None, max_len=None,
                 opciones=None, patron=None, nulo=False, decimales=None, mensaje=None):
        self.nombre, self.tipo, self.req = nombre, tipo, req
        self.minimo, self.maximo, self.min_len, self.max_len = minimo, maximo, min_len, max_len
        self.opciones, self.patron, self.nulo, self.decimales = opciones, patron, nulo, decimales
        self.mensaje = mensaje

    def convertir(self, v):
        t = self.tipo
        if t == "str":
            if not isinstance(v, (str, int, float)) or isinstance(v, bool):
                raise ValueError("Debe ser texto.")
            v = str(v).strip()
            if self.min_len is not None and len(v) < self.min_len:
                raise ValueError(f"Debe tener al menos {self.min_len} caracteres.")
            if self.max_len is not None and len(v) > self.max_len:
                raise ValueError(f"Debe tener como máximo {self.max_len} caracteres.")
            if self.patron and not re.fullmatch(self.patron, v):
                raise ValueError(self.mensaje or "No tiene el formato esperado.")
        elif t == "int":
            if isinstance(v, bool):
                raise ValueError("Debe ser un número entero.")
            try:
                f = float(v)
            except (TypeError, ValueError):
                raise ValueError("Debe ser un número entero.")
            if f != int(f):
                raise ValueError("Debe ser un número entero.")
            v = int(f)
        elif t == "num":
            if isinstance(v, bool):
                raise ValueError("Debe ser un número.")
            try:
                d = Decimal(str(v))
            except (InvalidOperation, ValueError):
                raise ValueError("Debe ser un número.")
            if not d.is_finite():
                raise ValueError("Debe ser un número.")
            if self.decimales is not None and -d.as_tuple().exponent > self.decimales:
                raise ValueError(f"Usa como máximo {self.decimales} decimales.")
            v = float(d)
        elif t == "bool":
            if isinstance(v, str) and v.lower() in ("true", "false", "1", "0"):
                v = v.lower() in ("true", "1")
            elif not isinstance(v, bool):
                raise ValueError("Debe ser verdadero o falso.")
        elif t == "fecha":
            try:
                v = dt.datetime.fromisoformat(str(v).replace("Z", "+00:00"))
            except ValueError:
                raise ValueError("Debe ser una fecha ISO 8601 con zona (2026-10-12T18:30:00-06:00).")
            if v.tzinfo is None:
                raise ValueError("La fecha debe incluir la zona horaria.")
        elif t == "obj":
            if not isinstance(v, dict):
                raise ValueError("Debe ser un objeto.")
        elif t == "lista":
            if isinstance(v, dict) and len(v) == 1:          # XML: <lineas><linea/>…</lineas>
                v = next(iter(v.values()))
            if v == "" or v is None:
                v = []
            if not isinstance(v, list):
                v = [v]
        if self.opciones is not None and v not in self.opciones:
            raise ValueError("Valor no permitido. Opciones: " + ", ".join(map(str, self.opciones)) + ".")
        if self.minimo is not None and v < self.minimo:
            raise ValueError(self.mensaje or f"Debe ser mayor o igual a {self.minimo}.")
        if self.maximo is not None and v > self.maximo:
            raise ValueError(self.mensaje or f"Debe ser menor o igual a {self.maximo}.")
        return v


def validar(datos, campos, prefijo=""):
    """Devuelve un dict con los valores convertidos o lanza ErrorApi 422 con todos los detalles."""
    salida, detalles = {}, []
    for c in campos:
        v = datos.get(c.nombre, _FALTA) if isinstance(datos, dict) else _FALTA
        if v is _FALTA or (v == "" and c.tipo != "str"):
            if c.req:
                detalles.append({"campo": prefijo + c.nombre, "mensaje": "Es obligatorio."})
            continue
        if v is None:
            if c.nulo or not c.req:
                salida[c.nombre] = None
            else:
                detalles.append({"campo": prefijo + c.nombre, "mensaje": "No puede ser nulo."})
            continue
        try:
            salida[c.nombre] = c.convertir(v)
        except ValueError as e:
            detalles.append({"campo": prefijo + c.nombre, "mensaje": str(e)})
    if detalles:
        raise ErrorApi(422, "VALIDACION", "Revisa los datos enviados.", detalles)
    return salida


def unir_errores(*funciones):
    """Ejecuta varias validaciones y junta los detalles de todas."""
    detalles, resultados = [], []
    for f in funciones:
        try:
            resultados.append(f())
        except ErrorApi as e:
            if e.status != 422:
                raise
            detalles += e.detalles
            resultados.append(None)
    if detalles:
        raise ErrorApi(422, "VALIDACION", "Revisa los datos enviados.", detalles)
    return resultados


CORREO = r"[^@\s]+@[^@\s]+\.[^@\s]+"
