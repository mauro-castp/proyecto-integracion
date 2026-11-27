"""
Pruebas unitarias de comun/ubicacion_calc.py (sin base de datos), con números que se pueden revisar a mano.

  cd servicios && python -m unittest -v pruebas.test_unitarias_ubicacion
"""
import filecmp
import unittest
from pathlib import Path

from comun import ubicacion_calc as uc

RAIZ = Path(__file__).resolve().parents[2]


def colonia(cve, lat, lng, poblacion, grado):
    return {"cve": cve, "nombre": cve, "lat": lat, "lng": lng, "poblacion": poblacion, "grado": grado}


class Ubicacion(unittest.TestCase):
    def test_portal_y_servicio_usan_la_misma_funcion(self):
        self.assertTrue(filecmp.cmp(RAIZ / "servicios/comun/ubicacion_calc.py", RAIZ / "sistema_web/ubicacion_calc.py", shallow=False))

    def test_demanda_esperada_a_mano(self):
        # 3 600 habitantes ÷ 3.6 = 1 000 hogares × 8 % × 1.2 pedidos/semana ÷ 7 = 13.714 pedidos/día
        p = uc.con_defecto()
        self.assertAlmostEqual(uc.demanda_esperada(colonia("A", 0, 0, 3600, "Medio"), p), 1000 * 0.08 * 1.2 / 7, places=6)

    def test_equilibrio_a_mano(self):
        # margen = 135 × 0.28 − 22 = 15.80; 72 000 ÷ 15.80 ÷ 30 = 151.90 pedidos/día
        margen, eq = uc.equilibrio_diario(uc.con_defecto())
        self.assertAlmostEqual(margen, 15.8, places=6)
        self.assertAlmostEqual(eq, 72000 / 15.8 / 30, places=6)
        self.assertIsNone(uc.equilibrio_diario(uc.con_defecto({"costo_entrega": 100}))[1])

    def test_solo_bajos_ingresos_son_demanda(self):
        cols = [colonia("rica", 25.75, -100.36, 50000, "Muy bajo"), colonia("pobre", 25.75, -100.36, 3600, "Alto")]
        r = uc.proponer(cols, parametros={"p": 1})
        self.assertEqual(r["resumen"]["colonias_bajos_ingresos"], 1)
        self.assertEqual(r["propuestas"][0]["colonias_atendidas"], 1)

    def test_cobertura_maxima_elige_el_grupo_grande(self):
        # Dos grupos separados ~5.5 km: uno con 3 colonias de 10 000 hab. y otro con una de 2 000. Con p = 1 gana el grande.
        cols = [colonia("g1", 25.750, -100.370, 10000, "Medio"), colonia("g2", 25.752, -100.371, 10000, "Alto"),
                colonia("g3", 25.751, -100.369, 10000, "Medio"), colonia("solo", 25.700, -100.370, 2000, "Muy alto")]
        r = uc.proponer(cols, parametros={"p": 1})
        self.assertIn(r["propuestas"][0]["cve_col"], ("g1", "g2", "g3"))
        self.assertEqual(r["propuestas"][0]["colonias_atendidas"], 3)
        r2 = uc.proponer(cols, parametros={"p": 2})
        self.assertEqual(r2["resumen"]["cobertura_pct"], 100.0)

    def test_reproducible_y_veredicto(self):
        cols = [colonia(f"c{i}", 25.75 + i * 0.001, -100.37, 8000, "Medio") for i in range(5)]
        a, b = uc.proponer(cols, parametros={"p": 1}), uc.proponer(cols, parametros={"p": 1})
        self.assertEqual(a, b)
        x = a["propuestas"][0]
        self.assertIn(x["veredicto"], ("VIABLE", "VIABLE AJUSTADO", "NO VIABLE"))
        self.assertLessEqual(x["demanda_simulada"]["p90"], uc.PARAMS["capacidad_diaria"])
        poca = uc.proponer(cols, parametros={"p": 1, "penetracion": 0.005})["propuestas"][0]
        self.assertEqual(poca["veredicto"], "NO VIABLE")
        self.assertGreater(poca["penetracion_minima"], 0.005)


if __name__ == "__main__":
    unittest.main()
