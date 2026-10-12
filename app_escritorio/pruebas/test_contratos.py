"""Ejecutar con Python y lxml: python -m unittest discover -s pruebas -v."""
from pathlib import Path
import unittest
from lxml import etree

ROOT = Path(__file__).resolve().parents[1] / 'contratos'

class Contratos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = etree.XMLSchema(etree.parse(str(ROOT / 'cliente.xsd')))

    def test_ejemplos(self):
        for path in ROOT.glob('*.xml'):
            with self.subTest(path=path.name):
                self.schema.assertValid(etree.parse(str(path)))

    def test_rechaza_sesion_incompleta(self):
        root = etree.parse(str(ROOT / 'sesion.xml'))
        root.getroot().remove(root.getroot()[0])
        self.assertFalse(self.schema.validate(root))

    def test_rechaza_namespace_incorrecto(self):
        root = etree.fromstring((ROOT / 'lista.xml').read_bytes().replace(b'urn:microhubs:v1', b'urn:otro'))
        self.assertFalse(self.schema.validate(root))

    def test_rechaza_id_negativo(self):
        root = etree.parse(str(ROOT / 'lista.xml'))
        root.find('.//{urn:microhubs:v1}id').text = '-1'
        self.assertFalse(self.schema.validate(root))

    def test_rechaza_viabilidad_invalida(self):
        root = etree.parse(str(ROOT / 'simulacion.xml'))
        root.find('.//{urn:microhubs:v1}viable').text = 'quizas'
        self.assertFalse(self.schema.validate(root))

if __name__ == '__main__':
    unittest.main()
