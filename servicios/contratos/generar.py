"""
generar.py — XSD y ejemplos oficiales del contrato v1 a partir de una sola descripción.

Cada servicio nuevo se describe una vez (tipos y ejemplos, en servicios/contratos/olaN.py) y de ahí salen:

  · app_escritorio/contratos/<archivo>.xsd           el contrato XML
  · app_escritorio/contratos/ejemplos/<Nombre>.xml   el ejemplo XML (lo escribe la descripción, no a mano)
  · app_movil/app/src/test/resources/contratos/<Nombre>.json   el mismo ejemplo en JSON

El ejemplo XML se arma recorriendo el tipo, así que cumple el XSD por construcción; al final cada uno se
valida de verdad contra el conjunto completo de XSD. Un ejemplo que ya existe no se sobrescribe.

  cd servicios && python contratos/generar.py ola1
"""
import importlib
import json
import sys
from decimal import Decimal
from pathlib import Path
import xml.etree.ElementTree as ET

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "servicios"))

NS = "urn:microhubs:v1"
XSI = "http://www.w3.org/2001/XMLSchema-instance"
PRIMITIVOS = {"long": "xs:long", "int": "xs:int", "string": "xs:string", "bool": "xs:boolean", "dateTime": "xs:dateTime",
              "date": "xs:date", "num": "xs:decimal", "money": "xs:decimal"}


# Tipos que ya existen en comun.xsd y sirven para armar los ejemplos (no se vuelven a escribir en ningún XSD).
TIPOS_BASE = {"TPaginacion": []}


def F(nombre, tipo, **o):
    """Un campo: tipo primitivo, nombre de un tipo (TAlgo) o lista ([tipo]).
    Opciones: opt (puede faltar), nil (puede ir vacío), enum, max, min, maxv, item (nombre del hijo de una lista)."""
    return {"n": nombre, "t": tipo, **o}


# --------------------------------------------------------------------
# XSD
# --------------------------------------------------------------------
TIPOS_BASE["TPaginacion"] = [F("pagina", "long"), F("por_pagina", "long"), F("total", "long"), F("paginas", "long")]


def _atributos(c):
    a = ""
    if c.get("opt"):
        a += ' minOccurs="0"'
    if c.get("nil"):
        a += ' nillable="true"'
    return a


def _restriccion(c, base):
    r = []
    if c.get("enum"):
        r += [f'<xs:enumeration value="{v}"/>' for v in c["enum"]]
    if c.get("max") is not None:
        r.append(f'<xs:maxLength value="{c["max"]}"/>')
    if c.get("minlen") is not None:
        r.append(f'<xs:minLength value="{c["minlen"]}"/>')
    if c.get("min") is not None:
        r.append(f'<xs:minInclusive value="{c["min"]}"/>')
    if c.get("maxv") is not None:
        r.append(f'<xs:maxInclusive value="{c["maxv"]}"/>')
    if c["t"] == "money":
        r.append('<xs:fractionDigits value="2"/>')
    return r


def _elemento(c, sangria):
    sp = " " * sangria
    t, n = c["t"], c["n"]
    if isinstance(t, list):
        hijo = t[0]
        tipo = PRIMITIVOS[hijo] if hijo in PRIMITIVOS else f"tns:{hijo}"
        return [f'{sp}<xs:element name="{n}"{_atributos(c)}>', f"{sp}  <xs:complexType>", f"{sp}    <xs:sequence>",
                f'{sp}      <xs:element name="{c["item"]}" type="{tipo}" minOccurs="0" maxOccurs="unbounded"/>',
                f"{sp}    </xs:sequence>", f"{sp}  </xs:complexType>", f"{sp}</xs:element>"]
    if t in PRIMITIVOS:
        base = PRIMITIVOS[t]
        r = _restriccion(c, base)
        if not r:
            return [f'{sp}<xs:element name="{n}" type="{base}"{_atributos(c)}/>']
        return [f'{sp}<xs:element name="{n}"{_atributos(c)}>', f"{sp}  <xs:simpleType>", f'{sp}    <xs:restriction base="{base}">',
                *[f"{sp}      {x}" for x in r], f"{sp}    </xs:restriction>", f"{sp}  </xs:simpleType>", f"{sp}</xs:element>"]
    return [f'{sp}<xs:element name="{n}" type="tns:{t}"{_atributos(c)}/>']


def xsd(archivo, incluye, tipos, raices, titulo):
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           f"<!-- Contrato XML v1 · {titulo} · generado por servicios/contratos/generar.py: no editar a mano -->",
           '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:tns="urn:microhubs:v1" targetNamespace="urn:microhubs:v1"',
           '           elementFormDefault="qualified" attributeFormDefault="unqualified" version="1.0">']
    out += [f'  <xs:include schemaLocation="{i}.xsd"/>' for i in incluye] + [""]
    for nombre, campos in tipos.items():
        out += [f'  <xs:complexType name="{nombre}">', "    <xs:sequence>"]
        for c in campos:
            out += _elemento(c, 6)
        out += ["    </xs:sequence>", "  </xs:complexType>"]
    out.append("")
    for raiz, tipo in raices.items():
        out += [f'  <xs:element name="{raiz}">', "    <xs:complexType>", "      <xs:complexContent>", f'        <xs:extension base="tns:{tipo}">',
                '          <xs:attribute name="version" type="xs:string" use="optional" fixed="1"/>', "        </xs:extension>",
                "      </xs:complexContent>", "    </xs:complexType>", "  </xs:element>"]
    out.append("</xs:schema>")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------
# Ejemplos
# --------------------------------------------------------------------
def _texto(t, v):
    if t == "bool":
        return "true" if v else "false"
    if t == "money":
        return format(Decimal(str(v)).quantize(Decimal("0.01")), "f")
    if t == "num":
        return format(Decimal(str(v)), "f")
    if t in ("long", "int"):
        return str(int(v))
    return str(v)


def _llenar(padre, campos, datos, tipos, ruta):
    faltan = set(datos) - {c["n"] for c in campos}
    if faltan:
        raise ValueError(f"{ruta}: el ejemplo trae campos que el tipo no declara: {sorted(faltan)}")
    for c in campos:
        n, t = c["n"], c["t"]
        if n not in datos:
            if not c.get("opt"):
                raise ValueError(f"{ruta}.{n}: falta en el ejemplo")
            continue
        v = datos[n]
        el = ET.SubElement(padre, f"{{{NS}}}{n}")
        if v is None:
            if not c.get("nil") and not c.get("opt"):
                raise ValueError(f"{ruta}.{n}: no admite nulo")
            el.set(f"{{{XSI}}}nil", "true")
        elif isinstance(t, list):
            hijo = t[0]
            for x in v:
                h = ET.SubElement(el, f"{{{NS}}}{c['item']}")
                if hijo in PRIMITIVOS:
                    h.text = _texto(hijo, x)
                else:
                    _llenar(h, tipos[hijo], x, tipos, f"{ruta}.{n}[]")
        elif t in PRIMITIVOS:
            el.text = _texto(t, v)
        else:
            _llenar(el, tipos[t], v, tipos, f"{ruta}.{n}")


def ejemplo_xml(raiz, tipo, datos, tipos):
    ET.register_namespace("", NS)
    ET.register_namespace("xsi", XSI)
    el = ET.Element(f"{{{NS}}}{raiz}", {"version": "1"})
    _llenar(el, tipos[tipo], datos, tipos, raiz)
    ET.indent(el, space="  ")
    return ET.tostring(el, encoding="unicode", xml_declaration=False)


def main(nombre):
    sys.path.insert(0, str(Path(__file__).parent))
    spec = importlib.import_module(nombre)
    destino_xsd = RAIZ / "app_escritorio" / "contratos"
    destino_xml = destino_xsd / "ejemplos"
    destino_json = RAIZ / "app_movil" / "app" / "src" / "test" / "resources" / "contratos"
    todos = {}
    for archivo, d in spec.ARCHIVOS.items():
        (destino_xsd / f"{archivo}.xsd").write_text(xsd(archivo, d["incluye"], d["tipos"], d["raices"], d["titulo"]), encoding="utf-8", newline="\n")
        todos.update(d["tipos"])
        print(f"  {archivo}.xsd: {len(d['tipos'])} tipos, {len(d['raices'])} raíces")
    tipos_globales = {**TIPOS_BASE, **getattr(spec, "TIPOS_EXTERNOS", {}), **todos}
    raiz_de = {r: t for d in spec.ARCHIVOS.values() for r, t in d["raices"].items()}
    nuevos = 0
    for nombre_ej, (raiz, datos) in spec.EJEMPLOS.items():
        arch_xml = destino_xml / f"{nombre_ej}.ok.xml"
        arch_json = destino_json / f"{nombre_ej}.ok.json"
        if not arch_json.exists():
            arch_json.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
            nuevos += 1
        if raiz is not None and not arch_xml.exists():
            cuerpo = ejemplo_xml(raiz, raiz_de[raiz], datos, tipos_globales)
            arch_xml.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + cuerpo + "\n", encoding="utf-8", newline="\n")
    print(f"  ejemplos nuevos: {nuevos}")

    # Validación real contra el conjunto de XSD del repositorio
    import os
    os.environ.setdefault("LOG_STDOUT", "0")
    from comun.esquemas import errores_xml, esquema
    esquema.cache_clear()
    malos = 0
    for nombre_ej in spec.EJEMPLOS:
        f = destino_xml / f"{nombre_ej}.ok.xml"
        if f.exists():
            e = errores_xml(f.read_bytes())
            if e:
                malos += 1
                print(f"  NO VALIDA {f.name}: {e[:2]}")
    print(f"  ejemplos XML que no validan: {malos}")
    return 1 if malos else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "ola1"))
