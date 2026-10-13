"""
esquemas.py — Validación XML contra los XSD oficiales del contrato v1.

Los nueve XSD (app_escritorio/contratos) se compilan en un solo conjunto,
igual que lo hace la app de escritorio. El servicio valida cada cuerpo XML
que recibe antes de procesarlo; las pruebas validan con el mismo conjunto
cada respuesta XML que el servicio produce.
"""
from functools import lru_cache

from lxml import etree

from . import config

ARCHIVOS = ["comun", "auth", "usuarios", "catalogos", "pedidos", "entregas",
            "planeacion", "documentos", "notificaciones"]


@lru_cache(maxsize=1)
def esquema():
    base = config.CONTRATOS.resolve()
    maestro = ('<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" targetNamespace="urn:microhubs:v1" '
               'elementFormDefault="qualified">'
               + "".join(f'<xs:include schemaLocation="{n}.xsd"/>' for n in ARCHIVOS) + "</xs:schema>")
    doc = etree.fromstring(maestro.encode(), base_url=(base / "_maestro.xsd").as_uri())
    return etree.XMLSchema(doc)


def errores_xml(cuerpo):
    """Lista de mensajes de validación (vacía si el XML cumple el contrato)."""
    parser = etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False)
    try:
        doc = etree.fromstring(cuerpo, parser)
    except etree.XMLSyntaxError as e:
        return [str(e)]
    s = esquema()
    if s.validate(doc):
        return []
    return [f"{e.message}" for e in s.error_log][:10]
