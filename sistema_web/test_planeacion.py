import os
import unittest
os.environ["MODO_LOCAL"] = "1"

from planeacion import calcular_score, clasificar_abc, distancia_km, ruta_vecino_mas_cercano, simular


class PruebasPlaneacion(unittest.TestCase):
    def test_simulacion_base(self):
        r=simular(dict(demanda_diaria=120,operadores=3,horas_turno=8,pedidos_operador_hora=5,
          ticket_promedio=135,costo_entrega=22,margen_pct=35,renta_mensual=18000,
          nomina_mensual=42000,servicios_mensuales=7000,otros_fijos=5000,dias_operacion=30))
        self.assertEqual(r["capacidad_diaria"],120)
        self.assertEqual(r["pedidos_rechazados"],0)
        self.assertEqual(r["punto_equilibrio_mes"],2852)
        self.assertEqual(r["decision"],"VIABLE CON RIESGO DE CAPACIDAD")

    def test_saturacion_y_rechazo(self):
        r=simular(dict(demanda_diaria=150,operadores=2,horas_turno=8,pedidos_operador_hora=5,
          ticket_promedio=120,costo_entrega=20,margen_pct=30,renta_mensual=10000,
          nomina_mensual=20000,servicios_mensuales=5000,otros_fijos=1000,dias_operacion=30))
        self.assertEqual((r["pedidos_atendidos"],r["pedidos_rechazados"]),(80,70))
        self.assertEqual(r["nivel"],"Riesgo de saturación")

    def test_score_abc_y_ruta(self):
        self.assertEqual(calcular_score(126,18000,2.4,9,{"demanda":1,"renta":1.2,"distancia":4,"accesibilidad":3}),121.8)
        abc=clasificar_abc([{"movimiento":80,"stock":5,"minimo":10},{"movimiento":15,"stock":20,"minimo":5},{"movimiento":5,"stock":30,"minimo":5}])
        self.assertEqual([x["abc"] for x in abc],["A","B","C"])
        ruta,total=ruta_vecino_mas_cercano((25.75,-100.36),[{"id":1,"latitud":25.751,"longitud":-100.361},{"id":2,"latitud":25.76,"longitud":-100.38}])
        self.assertEqual(ruta[0]["id"],1); self.assertGreater(total,0)
        self.assertEqual(distancia_km(25.75,-100.36,25.75,-100.36),0)

    def test_pagina_local(self):
        from app_local import app
        c=app.test_client(); r=c.get("/planeacion")
        self.assertEqual(r.status_code,200)
        texto=r.get_data(as_text=True)
        for titulo in ("Análisis de demanda", "Propuesta y comparación", "Capacidad y simulación", "Planeación de surtido", "Optimización de entregas", "Punto de equilibrio"):
            self.assertIn(titulo,texto)
        r=c.post("/planeacion",data={"demanda_diaria":200,"operadores":2,"repartidores":3,"horas_turno":8,"pedidos_operador_hora":5,"ticket_promedio":135,"costo_entrega":22,"margen_pct":35,"renta_mensual":18000,"nomina_mensual":42000,"servicios_mensuales":7000,"otros_fijos":5000})
        self.assertEqual(r.status_code,200); self.assertIn("120.0",r.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
