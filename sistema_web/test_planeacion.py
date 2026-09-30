"""Pruebas de los cálculos de planeación (sin base de datos): python -m unittest -v test_planeacion.py"""
import unittest

import planeacion_calc as pc


class Equilibrio(unittest.TestCase):
    def test_ejemplo_de_la_retro(self):
        # 72,000 de costos fijos y $24 de margen por pedido → 3,000/mes ≈ 100/día.
        eq = pc.punto_equilibrio(72000, ticket=100, margen_bruto=0.46, costo_entrega=22, dias_mes=30)
        self.assertEqual(eq["margen_pedido"], 24.0)
        self.assertEqual(eq["mensual"], 3000.0)
        self.assertEqual(eq["diario"], 100.0)
        self.assertGreaterEqual(len(eq["pasos"]), 3)

    def test_margen_no_positivo(self):
        eq = pc.punto_equilibrio(50000, ticket=60, margen_bruto=0.2, costo_entrega=22)
        self.assertIsNone(eq["diario"])


class Ubicacion(unittest.TestCase):
    def test_score_formula(self):
        r = pc.score_ubicacion(100, 18000, 2.0, 9)
        # 100*1 - 18*1.2 - 2*4 + 9*3 = 100 - 21.6 - 8 + 27
        self.assertEqual(r["score"], 97.4)

    def test_pesos_configurables(self):
        a = pc.score_ubicacion(100, 18000, 2.0, 9)["score"]
        b = pc.score_ubicacion(100, 18000, 2.0, 9, {"peso_score_renta": 3})["score"]
        self.assertLess(b, a)

    def test_cobertura_radio_y_solapamiento(self):
        zonas = [{"id": 1, "nombre": "A", "lat": 25.750, "lng": -100.360, "demanda_dia": 80, "poblacion": 1},
                 {"id": 2, "nombre": "B", "lat": 25.850, "lng": -100.360, "demanda_dia": 40, "poblacion": 1}]
        cand = {"latitud": 25.751, "longitud": -100.360, "radio_km": 1.5, "poblacion_cubierta": 7200}
        hubs = [{"clave": "MH-01", "lat": 25.749, "lng": -100.361, "radio_km": 1.5}]
        c = pc.cobertura_candidato(cand, zonas, hubs)
        self.assertEqual(c["demanda_cubierta"], 80)
        self.assertEqual(c["demanda_fuera"], 40)
        self.assertEqual(c["hogares"], 2000)
        self.assertEqual(c["solapamiento"][0]["pct"], 100.0)


class CapacidadSimulacion(unittest.TestCase):
    def test_capacidad_y_umbrales(self):
        c = pc.capacidad(3, 4, 2.4)
        self.assertAlmostEqual(c["minutos_por_pedido_operacion"], 11.0, 1)
        self.assertGreater(c["capacidad_dia"], 0)
        self.assertEqual(pc.nivel_utilizacion(69.9), "estable")
        self.assertEqual(pc.nivel_utilizacion(70), "atencion")
        self.assertEqual(pc.nivel_utilizacion(85), "atencion")
        self.assertEqual(pc.nivel_utilizacion(85.1), "riesgo")

    def test_saturacion_rechaza_pedidos(self):
        r = pc.simular({"demanda_diaria": 400, "operadores": 1, "repartidores": 1})
        self.assertGreater(r["rechazados"], 0)
        self.assertEqual(r["nivel"], "riesgo")
        self.assertLessEqual(r["atendidos"], r["capacidad"]["capacidad_dia"])

    def test_tope_de_espacio_fisico(self):
        r = pc.simular({"demanda_diaria": 120, "operadores": 6, "repartidores": 8, "capacidad_fisica": 50})
        self.assertEqual(r["capacidad"]["cuello_botella"], "espacio físico")
        self.assertEqual(r["capacidad"]["capacidad_dia"], 50)

    def test_decisiones_de_viabilidad(self):
        viable = pc.simular({"demanda_diaria": 110, "operadores": 4, "repartidores": 6, "ticket": 150,
                             "renta": 15000, "nomina": 30000, "servicios": 5000, "otros": 3000})
        self.assertIn(viable["ficha"]["decision"], ("VIABLE", "VIABLE CON RIESGO DE CAPACIDAD"))
        no = pc.simular({"demanda_diaria": 20, "operadores": 3, "repartidores": 3})
        self.assertEqual(no["ficha"]["decision"], "NO VIABLE CON LOS SUPUESTOS ACTUALES")
        riesgo = pc.simular({"demanda_diaria": 150, "operadores": 3, "repartidores": 6, "ticket": 200,
                             "margen_bruto": 0.35, "horas": 10})
        if riesgo["nivel"] == "riesgo":
            self.assertEqual(riesgo["ficha"]["decision"], "VIABLE CON RIESGO DE CAPACIDAD")

    def test_sensibilidad_ticket(self):
        s = pc.sensibilidad({"demanda_diaria": 120})
        filas = [f for f in s["filas"] if f["clave"] == "ticket"]
        bajo = next(f for f in filas if f["cambio"] == -0.2)
        alto = next(f for f in filas if f["cambio"] == 0.2)
        self.assertGreater(bajo["equilibrio_diario"], alto["equilibrio_diario"])
        self.assertEqual(len({f["clave"] for f in s["filas"]}), 8)


class Surtido(unittest.TestCase):
    def test_abc_pareto(self):
        items = [{"id": i, "unidades": u} for i, u in enumerate([500, 300, 100, 50, 30, 15, 5, 0], 1)]
        r = {x["id"]: x["clase"] for x in pc.clasificar_abc(items)}
        self.assertEqual(r[1], "A")
        self.assertEqual(r[2], "A")
        self.assertEqual(r[8], "C")

    def test_recomendaciones(self):
        base = {"unidades": 90, "existencia": 200, "minimo": 10, "quiebres": 0, "clase": "A",
                "margen_unit": 5, "espacio": 1}
        self.assertEqual(pc.recomendar_surtido({**base, "quiebres": 2}, 90)["recomendacion"], "Aumentar")
        self.assertEqual(pc.recomendar_surtido(base, 90)["recomendacion"], "Reducir")
        self.assertEqual(pc.recomendar_surtido({**base, "existencia": 8, "minimo": 5}, 90)["recomendacion"], "Mantener")
        self.assertEqual(pc.recomendar_surtido({**base, "unidades": 0, "clase": "C"}, 90)["recomendacion"], "Eliminar")


class Rutas(unittest.TestCase):
    ORIGEN = (25.748, -100.364)
    PARADAS = [{"lat": 25.7600, "lng": -100.3600}, {"lat": 25.7490, "lng": -100.3650},
               {"lat": 25.7550, "lng": -100.3700}, {"lat": 25.7520, "lng": -100.3580}]

    def test_haversine(self):
        self.assertAlmostEqual(pc.haversine_km(25.0, -100.0, 25.0, -100.0), 0.0)
        self.assertAlmostEqual(pc.haversine_km(25.0, -100.0, 26.0, -100.0), 111.2, delta=0.5)

    def test_exacto_no_peor_que_vecino(self):
        nn = pc.vecino_mas_cercano(self.ORIGEN, self.PARADAS)
        ex = pc.tsp_exacto(self.ORIGEN, self.PARADAS)
        self.assertLessEqual(pc.distancia_ruta(self.ORIGEN, self.PARADAS, ex)[0],
                             pc.distancia_ruta(self.ORIGEN, self.PARADAS, nn)[0] + 1e-9)
        self.assertEqual(sorted(ex), [0, 1, 2, 3])

    def test_ruta_larga_usa_heuristica(self):
        paradas = [{"lat": 25.74 + i * 0.002, "lng": -100.37 + (i % 3) * 0.003} for i in range(10)]
        r = pc.planear_ruta(self.ORIGEN, paradas)
        self.assertIn("2-opt", r["metodo"])
        self.assertEqual(sorted(r["orden"]), list(range(10)))
        self.assertGreater(r["minutos"], 0)

    def test_asignacion_agrupa_y_respeta_tope(self):
        pedidos = [{"id": i, "zona_id": 1 + i % 2, "zona": f"Z{1 + i % 2}",
                    "lat": 25.75 + i * 0.001, "lng": -100.365} for i in range(12)]
        reps = [{"id": 10, "nombre": "A"}, {"id": 11, "nombre": "B"}]
        r = pc.asignar_repartidores(pedidos, reps, self.ORIGEN, {"max_paradas_repartidor": 8})
        self.assertEqual(sum(len(x["paradas"]) for x in r["rutas"]), 12)
        self.assertTrue(all(len(x["paradas"]) <= 8 for x in r["rutas"]))
        self.assertEqual(r["sin_asignar"], [])


if __name__ == "__main__":
    unittest.main()
