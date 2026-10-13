"""
formatos.py — Serialización del contrato v1 (JSON y XML urn:microhubs:v1).

Un mismo endpoint atiende a la app Android (JSON) y a la de escritorio
(XML validado contra los XSD oficiales). Accept decide el formato de la
respuesta y Content-Type el de la solicitud.

Reglas del XML (las impone el XSD):
  · Todo en el espacio de nombres urn:microhubs:v1.
  · El orden de los elementos es el de las llaves (xs:sequence).
  · null → xsi:nil="true" (solo donde el XSD dice nillable; los campos
    opcionales que no son nillable se omiten antes de serializar).
  · Dinero (xs:decimal con 2 decimales) viaja como Decimal: "67000.00".
  · Booleanos en minúsculas; fechas ISO 8601 con zona.
  · La entrada se lee sin DTD ni entidades externas (defusedxml).
"""
import datetime as dt
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET

from defusedxml.ElementTree import fromstring as xml_seguro

from . import config

NS = "urn:microhubs:v1"
XSI = "http://www.w3.org/2001/XMLSchema-instance"
ET.register_namespace("", NS)
ET.register_namespace("xsi", XSI)
ZONA = ZoneInfo(config.ZONA_HORARIA)

# Nombre del elemento hijo cuando el valor es una lista (según los XSD).
ITEMS = {"lineas": "linea", "eventos": "evento", "explicacion": "motivo", "permisos": "permiso",
         "por_decision": "grupo", "por_tipo": "grupo", "evidencia_ids": "evidencia_id",
         "puntos": "punto", "detalles": "detalle"}


def dinero(valor):
    """Importe con dos decimales exactos (xs:decimal fractionDigits=2)."""
    if valor is None:
        return None
    return Decimal(str(valor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def fecha(valor):
    """Fecha y hora local de Monterrey con zona: 2026-10-12T18:30:04-06:00."""
    if valor is None:
        return None
    if valor.tzinfo is None:
        valor = valor.replace(tzinfo=dt.timezone.utc)
    return valor.astimezone(ZONA).replace(microsecond=0).isoformat()


def numero(valor, decimales=None):
    if valor is None:
        return None
    v = float(valor)
    return round(v, decimales) if decimales is not None else v


def _texto(valor):
    if isinstance(valor, bool):
        return "true" if valor else "false"
    if isinstance(valor, float):
        if valor == int(valor) and abs(valor) < 1e15:
            return str(int(valor))
        return repr(valor)
    if isinstance(valor, Decimal):
        return format(valor, "f")
    if isinstance(valor, (dt.datetime, dt.date)):
        return valor.isoformat()
    return str(valor)


def _llenar(padre, nombre, valor, items):
    el = ET.SubElement(padre, f"{{{NS}}}{nombre}")
    if valor is None:
        el.set(f"{{{XSI}}}nil", "true")
    elif isinstance(valor, dict):
        for k, v in valor.items():
            _llenar(el, k, v, items)
    elif isinstance(valor, (list, tuple)):
        hijo = items.get(nombre) or ITEMS.get(nombre) or "elemento"
        for v in valor:
            _llenar(el, hijo, v, items)
    else:
        el.text = _texto(valor)
    return el


def a_xml(raiz, datos, items=None):
    """dict → bytes XML (UTF-8 con declaración). items: nombre del hijo por lista."""
    items = items or {}
    el = ET.Element(f"{{{NS}}}{raiz}", {"version": "1"})
    for k, v in (datos or {}).items():
        _llenar(el, k, v, items)
    return ET.tostring(el, encoding="utf-8", xml_declaration=True)


def _a_dict(el):
    hijos = list(el)
    if not hijos:
        if el.get(f"{{{XSI}}}nil") == "true":
            return None
        return (el.text or "").strip()
    out = {}
    for h in hijos:
        nombre = h.tag.split("}", 1)[-1]
        valor = _a_dict(h)
        if nombre in out:
            if not isinstance(out[nombre], list):
                out[nombre] = [out[nombre]]
            out[nombre].append(valor)
        else:
            out[nombre] = valor
    return out


def leer_xml(cuerpo):
    """bytes → (raíz, espacio de nombres, dict). Rechaza DTD y entidades."""
    el = xml_seguro(cuerpo, forbid_dtd=True, forbid_entities=True, forbid_external=True)
    if el.tag.startswith("{"):
        ns, nombre = el.tag[1:].split("}", 1)
    else:
        ns, nombre = "", el.tag
    datos = _a_dict(el)
    return nombre, ns, (datos if isinstance(datos, dict) else {})


def sin_nulos(d, *llaves):
    """Quita las llaves opcionales (no nillable) cuyo valor es None."""
    return {k: v for k, v in d.items() if not (k in llaves and v is None)}
