"""
Pruebas del módulo de Planeación en modo local (Flask + datos de demostración, sin base de datos).
Requiere las dependencias de requirements.txt:  python -m unittest -v test_planeacion_local.py
"""
import os
import unittest

os.environ["MODO_LOCAL"] = "1"

from app_local import app  # noqa: E402  (MODO_LOCAL debe fijarse antes)


class PlaneacionLocal(unittest.TestCase):
    def setUp(self):
        self.c = app.test_client()

    def texto(self, ruta, esperado=200):
        r = self.c.get(ruta, follow_redirects=True)
        self.assertEqual(r.status_code, esperado, ruta)
        return r.get_data(as_text=True)

    def test_paginas_de_los_ocho_modulos(self):
        casos = {
            "/planeacion/tablero": "Tablero del planeador",
            "/planeacion/demanda": "Demanda por categoría",
            "/planeacion/candidatos": "score =",
            "/planeacion/cobertura": "Solapamiento",
            "/planeacion/simulacion": "Punto de equilibrio",
            "/planeacion/surtido": "Eliminar",
            "/planeacion/entregas": "Rutas propuestas",
            "/planeacion/escenarios": "Comparar escenarios",
            "/panel/operador": "Listos para despacho",
            "/panel/administrador": "Salud",
        }
        for ruta, marca in casos.items():
            self.assertIn(marca, self.texto(ruta), ruta)

    def test_ejemplo_de_la_retro(self):
        html = self.texto("/planeacion/demanda")
        for dato in ("82.0", "54.0", "39.0", "18–20 h", "19–21 h", "17–20 h"):
            self.assertIn(dato, html)

    def test_equilibrio_muestra_el_calculo(self):
        html = self.texto("/planeacion/simulacion?candidato_id=1&demanda_diaria=100&ticket=100&costo_entrega=22"
                          "&margen_bruto=46&renta=18000&nomina=42000&servicios=7000&otros=5000")
        self.assertIn("3,000 pedidos/mes", html)
        self.assertIn("100.0 pedidos/día", html)

    def test_guardar_comparar_y_exportar_escenarios(self):
        base = {"candidato_id": "1", "demanda_diaria": "120", "operadores": "3", "repartidores": "4",
                "ticket": "135", "costo_entrega": "22", "margen_bruto": "0.28", "renta": "18000",
                "nomina": "42000", "servicios": "7000", "otros": "5000", "distancia_km": "2.4"}
        for nombre, ticket in (("Local A", "135"), ("Local B", "100")):
            r = self.c.post("/planeacion/escenarios/guardar", data={**base, "ticket": ticket, "nombre": nombre},
                            follow_redirects=True)
            self.assertIn("Escenario guardado", r.get_data(as_text=True))
        lista = self.texto("/planeacion/escenarios")
        self.assertIn("Local A", lista)
        ids = [i for i in range(1, 30) if f'value="{i}"' in lista][:2]
        self.assertIn("Comparación", self.texto(f"/planeacion/escenarios/comparar?ids={ids[0]}&ids={ids[1]}"))
        csv = self.c.get("/planeacion/escenarios.csv")
        self.assertEqual(csv.status_code, 200)
        self.assertIn("Local A", csv.get_data(as_text=True))

    def test_candidato_y_decision_humana(self):
        r = self.c.post("/planeacion/candidatos/nuevo", data={
            "clave": "cand-99", "nombre": "Prueba local", "latitud": "25.75", "longitud": "-100.37",
            "renta_estimada": "10000", "nomina_estimada": "30000", "servicios_estimados": "5000",
            "otros_costos": "2000", "superficie_m2": "80", "capacidad_fisica": "90", "accesibilidad_vial": "6",
            "zona_id": "1", "poblacion_cubierta": "3000", "radio_km": "1.5"}, follow_redirects=True)
        html = r.get_data(as_text=True)
        self.assertIn("CAND-99", html)
        self.assertIn("Ficha de viabilidad", html)
        r = self.c.post("/planeacion/candidatos/1/decision", data={"decision": "aceptado", "motivo": ""},
                        follow_redirects=True)
        self.assertIn("es humana", r.get_data(as_text=True))
        r = self.c.post("/planeacion/candidatos/1/decision", data={"decision": "condicionado", "motivo": "Renegociar renta"},
                        follow_redirects=True)
        self.assertIn("Renegociar renta", r.get_data(as_text=True))

    def test_entregas_agrupa_por_zona_y_asigna_repartidores(self):
        html = self.texto("/planeacion/entregas")
        self.assertIn("(demo)", html)
        self.assertIn("TSP exacto", html)
        r = self.c.post("/planeacion/entregas/confirmar", data={}, follow_redirects=True)
        self.assertIn("Modo local", r.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
