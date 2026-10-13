"""Pruebas de los XSD oficiales con un validador independiente (lxml).

    python -m pip install lxml
    python -m unittest discover -s pruebas -v

Comprueba que los ejemplos XML de contratos/ejemplos validan contra el XSD de su servicio y que los XML incorrectos
se rechazan. Son los mismos esquemas que carga la app (Api.cs) y que usan los microservicios.
"""
from pathlib import Path
import unittest

from lxml import etree

RAIZ = Path(__file__).resolve().parents[1] / 'contratos'
NS = '{urn:microhubs:v1}'


def esquemas():
    return {x.stem: etree.XMLSchema(etree.parse(str(x))) for x in sorted(RAIZ.glob('*.xsd'))}


class Contratos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.esq = esquemas()

    def valido(self, arbol):
        return any(e.validate(arbol) for e in self.esq.values())

    def ejemplo(self, nombre):
        return etree.parse(str(RAIZ / 'ejemplos' / nombre))

    def test_hay_un_xsd_por_servicio_mas_comun(self):
        self.assertEqual(set(self.esq), {'comun', 'auth', 'usuarios', 'catalogos', 'pedidos', 'entregas', 'planeacion', 'documentos', 'notificaciones'})

    def test_todos_los_ejemplos_validan(self):
        ejemplos = sorted((RAIZ / 'ejemplos').glob('*.xml'))
        self.assertGreaterEqual(len(ejemplos), 46)
        for ruta in ejemplos:
            with self.subTest(ejemplo=ruta.name):
                self.assertTrue(self.valido(etree.parse(str(ruta))))

    def test_rechaza_sesion_incompleta(self):
        arbol = self.ejemplo('Sesion.ok.xml')
        raiz = arbol.getroot()
        raiz.remove(raiz.find(NS + 'token_renovacion'))
        self.assertFalse(self.valido(arbol))

    def test_rechaza_espacio_de_nombres_incorrecto(self):
        crudo = (RAIZ / 'ejemplos' / 'PedidoLista.ok.xml').read_bytes().replace(b'urn:microhubs:v1', b'urn:otro')
        self.assertFalse(self.valido(etree.fromstring(crudo).getroottree()))

    def test_rechaza_id_como_texto(self):
        arbol = self.ejemplo('PedidoLista.ok.xml')
        arbol.find('.//' + NS + 'id').text = 'abc'
        self.assertFalse(self.valido(arbol))

    def test_rechaza_estado_fuera_del_catalogo(self):
        arbol = self.ejemplo('PedidoLista.ok.xml')
        arbol.find('.//' + NS + 'estado').text = 'inventado'
        self.assertFalse(self.valido(arbol))

    def test_rechaza_resultado_con_decision_invalida(self):
        arbol = self.ejemplo('Resultados.ok.xml')
        arbol.find(NS + 'decision').text = 'quizas'
        self.assertFalse(self.valido(arbol))

    def test_rechaza_accesibilidad_fuera_de_rango(self):
        arbol = self.ejemplo('CandidatoNuevo.ok.xml')
        arbol.find(NS + 'accesibilidad_vial').text = '11'
        self.assertFalse(self.valido(arbol))

    def test_rechaza_motivo_corto_en_la_decision(self):
        arbol = self.ejemplo('Decision.ok.xml')
        arbol.find(NS + 'motivo').text = 'ok'
        self.assertFalse(self.valido(arbol))

    def test_rechaza_elemento_no_definido(self):
        arbol = self.ejemplo('Decision.ok.xml')
        etree.SubElement(arbol.getroot(), NS + 'extra').text = 'x'
        self.assertFalse(self.valido(arbol))


if __name__ == '__main__':
    unittest.main()
