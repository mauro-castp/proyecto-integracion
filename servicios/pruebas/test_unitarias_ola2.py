"""
test_unitarias_ola2.py — Pruebas unitarias de los ocho servicios de la Ola 2 (demanda, cobertura, capacidad, rutas,
costos, punto de equilibrio, simulación y surtido), sin bases de datos.

Prueban las funciones de cálculo con números que se pueden verificar a mano: cada caso dice cuál es la cuenta.

  cd servicios && python -m unittest -v pruebas.test_unitarias_ola2
"""
import datetime as dt
import importlib.util
import math
import os
import random
import sys
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
os.environ.setdefault("LOG_STDOUT", "0")
os.environ.setdefault("SIM_TRABAJADOR", "0")

from comun.base_errores import ErrorApi  # noqa: E402


def cargar(nombre):
    spec = importlib.util.spec_from_file_location(f"u2_{nombre}", AQUI.parent / nombre / "app.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


costos, capacidad, cobertura, demanda = cargar("costos"), cargar("capacidad"), cargar("cobertura"), cargar("demanda")
equilibrio, rutas, surtido, simulacion = cargar("punto_equilibrio"), cargar("rutas"), cargar("surtido"), cargar("simulacion")
P_CAP = capacidad.DEFECTOS


# --------------------------------------------------------------------
# Costos
# --------------------------------------------------------------------
def concepto(nombre, ambito="global", ambito_id=None, tipo="fijo", categoria="otros", unidad="mes", monto=100.0, desde=dt.date(2026, 1, 1), hasta=None,
             estatus="activo"):
    return {"nombre": nombre, "ambito": ambito, "ambito_id": ambito_id, "tipo": tipo, "categoria": categoria, "unidad": unidad, "monto": monto,
            "vigente_desde": desde, "vigente_hasta": hasta, "estatus": estatus}


class Costos(unittest.TestCase):
    HOY = dt.date(2026, 10, 19)

    def test_el_concepto_del_microhub_sustituye_al_global_del_mismo_nombre(self):
        cs = [concepto("Seguro", monto=1000), concepto("Seguro", "microhub", 1, monto=2500), concepto("Renta", "microhub", 2, monto=9000)]
        r = costos.conceptos_que_rigen(cs, "microhub", 1, self.HOY)
        self.assertEqual([(c["nombre"], c["monto"]) for c in r], [("Seguro", 2500)])

    def test_no_rigen_los_vencidos_futuros_ni_inactivos(self):
        cs = [concepto("Vencido", hasta=dt.date(2026, 9, 30)), concepto("Futuro", desde=dt.date(2026, 11, 1)), concepto("Inactivo", estatus="inactivo"),
              concepto("Vigente", desde=dt.date(2026, 10, 19), hasta=dt.date(2026, 10, 19))]
        self.assertEqual([c["nombre"] for c in costos.conceptos_que_rigen(cs, "global", None, self.HOY)], ["Vigente"])

    def resumen(self):
        return costos.resumir([
            {"tipo": "fijo", "categoria": "renta", "nombre": "Renta", "unidad": "mes", "monto": 12000.0},
            {"tipo": "fijo", "categoria": "personal", "nombre": "Nómina", "unidad": "mes", "monto": 18000.0},
            {"tipo": "variable", "categoria": "operacion", "nombre": "Empaque", "unidad": "pedido", "monto": 3.5},
            {"tipo": "variable", "categoria": "transporte", "nombre": "Pago por entrega", "unidad": "entrega", "monto": 20.0},
            {"tipo": "variable", "categoria": "transporte", "nombre": "Combustible", "unidad": "km", "monto": 4.5},
            {"tipo": "variable", "categoria": "operacion", "nombre": "Comisión de pago", "unidad": "pct_venta", "monto": 2.0}])

    def test_resumen_separa_fijos_y_variables(self):
        r = self.resumen()
        self.assertEqual(r["fijos_mes"], 30000.0)
        self.assertEqual([(c["categoria"], c["monto"]) for c in r["por_categoria"]], [("personal", 18000.0), ("renta", 12000.0)])
        self.assertEqual((r["variable_pedido"], r["variable_entrega"], r["variable_km"], r["comision_pct"]), (3.5, 20.0, 4.5, 2.0))

    def test_costo_de_entrega_reparte_el_viaje_entre_las_paradas(self):
        # 20 de pago + 2 × 2.4 km × 4.5 por km ÷ 3 paradas = 20 + 7.2
        self.assertAlmostEqual(costos.costo_entrega(self.resumen(), 2.4, 3), 27.2)
        self.assertAlmostEqual(costos.costo_entrega(self.resumen(), 2.4, 0), 20 + 2 * 2.4 * 4.5)   # sin paradas se toma una

    def test_costo_por_pedido_suma_fijo_variable_comision_y_entrega(self):
        u = costos.unitarios(self.resumen(), 1000, 150.0, 2.4, 3)
        self.assertAlmostEqual(u["costo_fijo_pedido"], 30.0)                  # 30000 ÷ 1000
        self.assertAlmostEqual(u["comision_pedido"], 3.0)                     # 2 % de 150
        self.assertAlmostEqual(u["costo_variable_pedido"], 3.5 + 3.0 + 27.2)
        self.assertAlmostEqual(u["costo_por_pedido"], 30.0 + 33.7)

    def test_sin_pedidos_no_hay_costo_fijo_por_pedido(self):
        u = costos.unitarios(self.resumen(), 0, 150.0, 2.4, 3)
        self.assertIsNone(u["costo_fijo_pedido"])
        self.assertIsNone(u["costo_por_pedido"])

    def test_rentabilidad(self):
        r = costos.rentabilidad(self.resumen(), 1000, 150.0, 0.30, 2.4, 3)
        self.assertAlmostEqual(r["margen_contribucion_pedido"], 150 * 0.30 - 33.7)          # 11.3
        self.assertAlmostEqual(r["utilidad_mes"], 11.3 * 1000 - 30000)                      # -18700
        self.assertFalse(r["cubre_costos"])
        self.assertAlmostEqual(r["margen_operativo_pct"], 100 * -18700 / 150000)
        self.assertTrue(costos.rentabilidad(self.resumen(), 4000, 150.0, 0.30, 2.4, 3)["cubre_costos"])

    def test_sensibilidad_cuatro_variaciones_por_palanca(self):
        base, filas = costos.sensibilidad_costos(self.resumen(), 1000, 150.0, 0.30, 2.4, 3)
        palancas = {f["palanca"] for f in filas}
        self.assertEqual(len(palancas), 2 + 2)                                # dos categorías fijas + entrega + variable
        self.assertEqual(len(filas), len(palancas) * 4)
        subir = next(f for f in filas if f["palanca"] == "Fijo: renta" and f["cambio_pct"] == 10)
        self.assertAlmostEqual(subir["cambio_utilidad"], -1200.0)             # 10 % de 12000


# --------------------------------------------------------------------
# Capacidad
# --------------------------------------------------------------------
class Capacidad(unittest.TestCase):
    def test_utilizacion_es_carga_entre_capacidad(self):
        e = capacidad.evaluar(3, 2, 2.4, None, 10, 60, P_CAP)
        self.assertAlmostEqual(e["utilizacion_pct"], round(100 * 60 / e["capacidad_dia"], 1), places=1)
        self.assertEqual(e["holgura_pedidos_dia"], round(e["capacidad_dia"] - 60, 1))

    def test_sin_carga_la_utilizacion_es_cero(self):
        self.assertEqual(capacidad.evaluar(3, 2, 2.4, None, 10, 0, P_CAP)["utilizacion_pct"], 0.0)

    def test_el_cuello_de_botella_es_el_lado_con_menos_capacidad(self):
        poco_reparto = capacidad.evaluar(6, 1, 2.4, None, 10, 30, P_CAP)
        self.assertEqual(poco_reparto["cuello_botella"], "reparto")
        poca_operacion = capacidad.evaluar(1, 8, 2.4, None, 10, 30, P_CAP)
        self.assertEqual(poca_operacion["cuello_botella"], "operacion")

    def test_el_espacio_fisico_limita_la_capacidad(self):
        e = capacidad.evaluar(6, 6, 2.4, 40, 10, 30, P_CAP)
        self.assertEqual(e["capacidad_dia"], 40.0)
        self.assertEqual(e["cuello_botella"], "espacio físico")

    def test_el_personal_requerido_deja_la_utilizacion_bajo_el_umbral_de_riesgo(self):
        carga = 150
        e = capacidad.evaluar(1, 1, 2.4, None, 10, carga, P_CAP)
        mejor = capacidad.evaluar(e["operadores_requeridos"], e["repartidores_requeridos"], 2.4, None, 10, carga, P_CAP)
        self.assertLessEqual(mejor["utilizacion_pct"], P_CAP["umbral_utilizacion_riesgo"])

    def test_curva_de_carga_rechaza_lo_que_pasa_de_la_capacidad(self):
        cap = capacidad.evaluar(2, 2, 2.4, None, 10, 0, P_CAP)["capacidad_dia"]
        filas = capacidad.curva_de_carga(2, 2, 2.4, None, 10, [cap / 2, cap, cap * 1.5], P_CAP)
        self.assertEqual([f["rechazados"] for f in filas][:2], [0.0, 0.0])
        self.assertAlmostEqual(filas[2]["rechazados"], cap * 0.5, delta=0.2)
        self.assertAlmostEqual(filas[2]["atendidos"], cap, delta=0.2)


# --------------------------------------------------------------------
# Cobertura
# --------------------------------------------------------------------
P_COB = {**cobertura.DEFECTOS, "costo_base_entrega": 18.0}


def hub(i, lat, lng, radio=1.5):
    return {"id": i, "clave": f"MH-{i}", "nombre": f"Hub {i}", "lat": lat, "lng": lng, "radio_km": radio}


def zona(i, lat, lng, hogares):
    return {"id": i, "nombre": f"Zona {i}", "lat": lat, "lng": lng, "poblacion": int(hogares * 3.6), "hogares": hogares}


class Colas(unittest.TestCase):
    """M/M/1 y M/M/c con valores que se comprueban a mano con las fórmulas cerradas."""
    def setUp(self):
        from comun import colas
        self.mm = colas

    def test_mm1_coincide_con_las_formulas_cerradas(self):
        r = self.mm.mmc(8, 10, 1)                   # ρ = 0.8: Lq = ρ²/(1-ρ) = 3.2, Wq = ρ/(μ-λ) = 0.4 h, W = 1/(μ-λ) = 0.5 h
        self.assertEqual(r["modelo"], "M/M/1")
        self.assertAlmostEqual(r["p0"], 0.2)
        self.assertAlmostEqual(r["lq"], 3.2)
        self.assertAlmostEqual(r["wq_min"], 24.0)
        self.assertAlmostEqual(r["w_min"], 30.0)
        self.assertAlmostEqual(r["l"], 4.0)          # Little: L = λW

    def test_mmc_erlang_c_calculado_a_mano(self):
        r = self.mm.mmc(10, 4, 3)                   # a = 2.5, ρ = 0.833: P0 = 1/(1 + 2.5 + 3.125 + 15.625) = 0.0449, Lq = 3.511
        self.assertEqual(r["modelo"], "M/M/c")
        self.assertAlmostEqual(r["p0"], 0.044944, places=5)
        self.assertAlmostEqual(r["lq"], 3.5112, places=3)
        self.assertAlmostEqual(r["wq_min"], 21.067, places=2)
        self.assertAlmostEqual(r["prob_esperar"], 0.702247, places=5)

    def test_con_un_servidor_mmc_es_mm1(self):
        a, b = self.mm.mmc(6, 9, 1), self.mm.mmc(6, 9, 1)
        self.assertAlmostEqual(a["prob_esperar"], 6 / 9, places=5)  # en M/M/1 la probabilidad de esperar es ρ
        self.assertEqual(a, b)

    def test_saturada_no_es_estable_y_no_inventa_esperas(self):
        r = self.mm.mmc(12, 10, 1)
        self.assertFalse(r["estable"])
        self.assertIsNone(r["wq_min"])
        self.assertEqual(r["prob_esperar"], 1.0)

    def test_mas_operadores_menos_espera_y_minimo_que_cumple(self):
        filas = self.mm.tabla(10, 4, 5)
        esperas = [f["wq_min"] for f in filas]
        self.assertEqual(esperas, sorted(esperas, reverse=True))
        self.assertEqual(self.mm.servidores_minimos(10, 4, 5), 4)  # con 3 espera 21 min; con 4, 3.2 min
        self.assertTrue(next(f for f in filas if f["servidores"] == 4)["cumple"])

    def test_muchos_servidores_sin_desbordar(self):
        r = self.mm.mmc(400, 10, 50)                # 50! no se calcula directo
        self.assertTrue(r["estable"])
        self.assertGreaterEqual(r["wq_min"], 0)

    def test_tasas_invalidas(self):
        with self.assertRaises(ValueError):
            self.mm.mmc(0, 10, 1)
        with self.assertRaises(ValueError):
            self.mm.mmc(5, 10, 0)


class Cobertura(unittest.TestCase):
    ZONAS = [zona(1, 25.6700, -100.3100, 1000), zona(2, 25.6800, -100.3100, 800), zona(3, 25.7500, -100.3100, 500)]   # 1 y 2 cerca; 3 a 8 km
    HUBS = [hub(1, 25.6700, -100.3100)]

    def test_un_microhub_cubre_las_zonas_dentro_de_su_radio_en_linea_recta(self):
        cob = cobertura.cobertura_de_zonas(self.ZONAS, self.HUBS, P_COB)
        self.assertEqual([bool(c["mejor"]) for c in cob], [True, True, False])
        self.assertIsNotNone(cob[2]["mas_cercano"])                           # la zona 3 no está cubierta pero se sabe cuál es el más cercano

    def test_los_minutos_usan_el_rodeo_la_velocidad_y_el_servicio(self):
        o = cobertura.opcion(self.HUBS[0], self.ZONAS[1], P_COB)
        recta = o["distancia_km"]
        self.assertAlmostEqual(o["distancia_calle_km"], recta * 1.3)
        self.assertAlmostEqual(o["minutos"], recta * 1.3 / 22 * 60 + 4)

    def test_resumen_de_la_red(self):
        r = cobertura.resumen_red(cobertura.cobertura_de_zonas(self.ZONAS, self.HUBS, P_COB))
        self.assertEqual((r["zonas"], r["zonas_cubiertas"], r["hogares"], r["hogares_cubiertos"]), (3, 2, 2300, 1800))
        self.assertAlmostEqual(r["pct_hogares"], 78.3, places=1)
        self.assertEqual(r["zonas_solapadas"], 0)

    def test_una_ubicacion_encima_de_otra_solo_canibaliza(self):
        actual = cobertura.cobertura_de_zonas(self.ZONAS, self.HUBS, P_COB)
        r = cobertura.evaluar_ubicacion(25.6700, -100.3100, 1.5, actual, self.ZONAS, P_COB)
        self.assertEqual((r["zonas_nuevas"], r["hogares_nuevos"]), (0, 0))
        self.assertEqual(r["solapamiento_pct"], 100.0)
        self.assertTrue(r["canibaliza"])

    def test_una_ubicacion_junto_a_la_zona_sin_cobertura_suma_sus_hogares(self):
        actual = cobertura.cobertura_de_zonas(self.ZONAS, self.HUBS, P_COB)
        r = cobertura.evaluar_ubicacion(25.7500, -100.3100, 1.5, actual, self.ZONAS, P_COB)
        self.assertEqual((r["zonas_nuevas"], r["hogares_nuevos"]), (1, 500))
        self.assertEqual(r["solapamiento_pct"], 0.0)
        self.assertFalse(r["canibaliza"])
        self.assertAlmostEqual(r["despues"]["pct_hogares"], 100.0)
        self.assertGreater(r["despues"]["pct_hogares"], r["antes"]["pct_hogares"])

    def test_una_ubicacion_mas_cercana_acerca_el_servicio_a_hogares_ya_cubiertos(self):
        zonas = [zona(1, 25.6700, -100.3100, 1000)]
        lejos = [hub(1, 25.6820, -100.3100)]                                  # a 1.33 km de la zona
        actual = cobertura.cobertura_de_zonas(zonas, lejos, P_COB)
        r = cobertura.evaluar_ubicacion(25.6710, -100.3100, 1.5, actual, zonas, P_COB)
        self.assertEqual(r["hogares_nuevos"], 0)
        self.assertEqual(r["hogares_con_mejor_tiempo"], 1000)
        self.assertGreater(r["minutos_ahorrados"], 1.0)

    def test_escenarios_de_radio_mas_grande_cubre_igual_o_mas(self):
        filas = cobertura.escenarios_de_radio(self.ZONAS, self.HUBS, [0.5, 1.5, 12.0], [1.3], P_COB)
        pct = [f["pct_hogares"] for f in filas]
        self.assertEqual(pct, sorted(pct))
        self.assertEqual(filas[-1]["pct_hogares"], 100.0)


# --------------------------------------------------------------------
# Demanda
# --------------------------------------------------------------------
LUNES = dt.date(2026, 8, 3)                                                   # lunes


def serie_semanal(semanas, tendencia=0.0, base=(40, 40, 45, 50, 60, 70, 45)):
    out = []
    for i in range(semanas * 7):
        out.append((LUNES + dt.timedelta(days=i), base[i % 7] + tendencia * i))
    return out


INDICES = (0.80, 0.80, 0.90, 1.00, 1.20, 1.40, 0.90)                            # promedian 1.0


def serie_multiplicativa(semanas, nivel=50.0, tendencia=0.0):
    """Nivel con tendencia por el índice de su día de la semana: justo lo que supone el modelo."""
    return [(LUNES + dt.timedelta(days=i), (nivel + tendencia * i) * INDICES[i % 7]) for i in range(semanas * 7)]


class Demanda(unittest.TestCase):
    def test_serie_completa_rellena_con_ceros_los_dias_sin_observaciones(self):
        s = demanda.serie_completa({LUNES: 10, LUNES + dt.timedelta(days=3): 4})
        self.assertEqual([v for _, v in s], [10, 0, 0, 4])
        self.assertEqual(demanda.serie_completa({}), [])

    def test_el_indice_semanal_promedia_uno(self):
        idx, suficiente = demanda.indice_semanal(serie_semanal(8))
        self.assertTrue(suficiente)
        self.assertAlmostEqual(sum(idx.values()) / 7, 1.0, places=6)
        self.assertEqual(max(idx, key=idx.get), 6)                            # el sábado es el día fuerte
        self.assertGreater(idx[6], idx[1])

    def test_con_menos_de_dos_semanas_el_indice_es_plano(self):
        idx, suficiente = demanda.indice_semanal(serie_semanal(1))
        self.assertFalse(suficiente)
        self.assertEqual(set(idx.values()), {1.0})

    def test_minimos_cuadrados_recupera_una_recta_exacta(self):
        a, b = demanda.minimos_cuadrados([(t, 5 + 2 * t) for t in range(10)])
        self.assertAlmostEqual(a, 5.0)
        self.assertAlmostEqual(b, 2.0)
        self.assertEqual(demanda.minimos_cuadrados([]), (0.0, 0.0))
        self.assertEqual(demanda.minimos_cuadrados([(3, 7)]), (7.0, 0.0))

    def test_hacen_falta_catorce_dias(self):
        with self.assertRaises(ErrorApi) as c:
            demanda.ajustar(serie_semanal(1), "tendencia_estacional")
        self.assertEqual(c.exception.status, 422)

    def test_una_serie_sin_ruido_se_proyecta_sin_error(self):
        s = serie_multiplicativa(8, tendencia=0.2)
        filas, sigma, par = demanda.proyectar(s, 7, "tendencia_estacional", 1.28)
        self.assertLess(sigma, 1.5)
        esperado = [(50 + 0.2 * (len(s) + i)) * INDICES[(len(s) + i) % 7] for i in range(7)]
        for f, e in zip(filas, esperado):
            self.assertAlmostEqual(f["pedidos"], e, delta=0.05 * e)
            self.assertLessEqual(f["minimo"], f["pedidos"])
            self.assertGreaterEqual(f["maximo"], f["pedidos"])
        self.assertGreater(par["pendiente"], 0)

    def test_el_promedio_movil_no_tiene_pendiente(self):
        _, _, par = demanda.proyectar(serie_semanal(8, tendencia=0.5), 7, "promedio_movil", 1.28)
        self.assertEqual(par["pendiente"], 0.0)

    def test_el_respaldo_mide_el_error_contra_lo_que_paso(self):
        r = demanda.respaldo(serie_multiplicativa(8, tendencia=0.2), 7, "tendencia_estacional", 1.28)
        self.assertEqual(len(r["filas"]), 7)
        self.assertLess(r["mape_pct"], 5.0)
        self.assertEqual(r["dias_entrenamiento"], 49)

    def test_potencial_de_una_zona(self):
        mes, dia = demanda.potencial(1000, 0.12, 2.5, 30)
        self.assertAlmostEqual(mes, 300.0)
        self.assertAlmostEqual(dia, 10.0)
        self.assertEqual(demanda.potencial(1000, 0.12, 2.5, 0)[1], 0.0)


# --------------------------------------------------------------------
# Punto de equilibrio
# --------------------------------------------------------------------
class PuntoDeEquilibrio(unittest.TestCase):
    def test_la_cuenta_del_escenario_de_la_retroalimentacion_no_es_viable(self):
        # margen por pedido = 135 × 0.28 − 32.6 = 5.2 → 60,000 ÷ 5.2 = 11,538 pedidos al mes (385 al día) frente a 45 esperados
        r = equilibrio.calcular(60000, 135, 0.28, 32.6, 45, 30, 15)
        self.assertAlmostEqual(r["margen_pedido"], 5.2)
        self.assertAlmostEqual(r["equilibrio_mensual"], 11538.46, places=1)
        self.assertAlmostEqual(r["equilibrio_diario"], 384.6, places=1)
        self.assertEqual(r["decision"], "no_viable")
        self.assertTrue(r["pasos"])

    def test_las_tres_decisiones(self):
        # margen = 150 × 0.30 − 20 = 25; equilibrio = 40,000 ÷ 25 = 1,600 al mes = 53.33 al día
        viable = equilibrio.calcular(40000, 150, 0.30, 20, 70, 30, 15)
        ajustado = equilibrio.calcular(40000, 150, 0.30, 20, 55, 30, 15)
        perdida = equilibrio.calcular(40000, 150, 0.30, 20, 40, 30, 15)
        self.assertEqual((viable["decision"], ajustado["decision"], perdida["decision"]), ("viable", "viable_ajustado", "no_viable"))
        self.assertAlmostEqual(viable["margen_seguridad_pct"], 100 * (70 / (1600 / 30) - 1))
        self.assertAlmostEqual(perdida["diferencia_pedidos_dia"], 40 - 1600 / 30)

    def test_con_margen_negativo_no_hay_equilibrio(self):
        r = equilibrio.calcular(40000, 100, 0.20, 25, 500, 30, 15)         # 100 × 0.20 − 25 < 0
        self.assertIsNone(r["equilibrio_diario"])
        self.assertEqual(r["decision"], "no_viable")

    def test_utilidad_mensual_es_el_margen_por_los_pedidos_menos_los_fijos(self):
        r = equilibrio.calcular(40000, 150, 0.30, 20, 70, 30, 15)
        self.assertAlmostEqual(r["utilidad_mes"], 25 * 70 * 30 - 40000)

    def test_la_demanda_de_una_zona_cubierta_por_dos_se_reparte(self):
        zonas = [{"pedidos_dia": 30, "cubren": 1}, {"pedidos_dia": 40, "cubren": 2}, {"pedidos_dia": 12, "cubren": 3}]
        self.assertAlmostEqual(equilibrio.demanda_atribuible(zonas), 30 + 20 + 4)
        self.assertEqual(equilibrio.demanda_atribuible([]), 0)

    def test_sensibilidad_ordena_las_variables_por_el_rango_de_utilidad(self):
        entrada = {"costos_fijos": 40000, "ticket": 150, "margen_bruto": 0.30, "costo_variable_pedido": 20, "pedidos_dia": 70}
        base, filas, ranking = equilibrio.sensibilidad(entrada, 30, 15)
        self.assertEqual(len(filas), 5 * 4)
        self.assertEqual(len(ranking), 5)
        rangos = [r["rango_utilidad_mes"] for r in ranking]
        self.assertEqual(rangos, sorted(rangos, reverse=True))
        self.assertAlmostEqual(base["utilidad_mes"], 25 * 70 * 30 - 40000)
        # +10 % de pedidos por día suma 10 % × 70 × 25 × 30
        mas = next(f for f in filas if f["variable"] == "pedidos_dia" and f["cambio_pct"] == 10)
        self.assertAlmostEqual(mas["cambio_utilidad"], 0.10 * 70 * 25 * 30)


# --------------------------------------------------------------------
# Rutas
# --------------------------------------------------------------------
ORIGEN = (25.6866, -100.3161)
P_RUT = dict(rutas.DEFECTOS)


def parada(i, zona_id=1, dlat=0.0, dlng=0.0):
    return {"id": i, "folio": f"P-{i}", "zona_id": zona_id, "zona": f"Z{zona_id}", "lat": ORIGEN[0] + dlat, "lng": ORIGEN[1] + dlng}


PARADAS = [parada(1, 1, 0.020, 0.020), parada(2, 1, -0.010, 0.012), parada(3, 2, 0.015, -0.018), parada(4, 2, -0.020, -0.010),
           parada(5, 1, 0.004, 0.030), parada(6, 2, -0.012, 0.022)]


def km(orden, paradas=PARADAS):
    return rutas.metricas(ORIGEN, [paradas[i] for i in orden], list(range(len(orden))), P_RUT)["distancia_km"]


class Rutas(unittest.TestCase):
    def test_el_exacto_nunca_es_peor_que_los_demas(self):
        orden_ex, _ = rutas.ordenar(ORIGEN, PARADAS, "exacto")
        for metodo in ("vecino", "2opt", "orden_llegada"):
            otro, _ = rutas.ordenar(ORIGEN, PARADAS, metodo)
            self.assertLessEqual(km(orden_ex), km(otro) + 1e-9, metodo)
        self.assertEqual(sorted(orden_ex), list(range(len(PARADAS))))

    def test_2opt_no_empeora_al_vecino_mas_cercano(self):
        vecino, _ = rutas.ordenar(ORIGEN, PARADAS, "vecino")
        dos, _ = rutas.ordenar(ORIGEN, PARADAS, "2opt")
        self.assertLessEqual(km(dos), km(vecino) + 1e-9)

    def test_el_exacto_se_niega_con_demasiadas_paradas(self):
        muchas = [parada(i, 1, 0.001 * i, 0.001 * i) for i in range(1, 11)]
        with self.assertRaises(ErrorApi) as c:
            rutas.ordenar(ORIGEN, muchas, "exacto")
        self.assertEqual(c.exception.status, 422)
        orden, metodo = rutas.ordenar(ORIGEN, muchas, "automatico")           # el automático pasa a 2-opt
        self.assertIn("2-opt", metodo)
        self.assertEqual(len(orden), 10)

    def test_sin_paradas(self):
        self.assertEqual(rutas.ordenar(ORIGEN, [], "automatico")[0], [])

    def test_metricas_aplican_rodeo_velocidad_servicio_y_costo(self):
        un = [parada(1, 1, 0.02, 0.0)]
        m = rutas.metricas(ORIGEN, un, [0], P_RUT)
        recta = rutas.pc.haversine_km(ORIGEN[0], ORIGEN[1], un[0]["lat"], un[0]["lng"])
        self.assertAlmostEqual(m["distancia_km"], round(recta * 1.3, 2), places=2)
        self.assertAlmostEqual(m["minutos"], round(recta * 1.3 / 22 * 60 + 4, 1), places=1)
        self.assertAlmostEqual(m["costo"], round(recta * 1.3 * 4.5 + 18, 2), places=2)

    def test_los_minutos_acumulados_crecen_parada_a_parada(self):
        r = rutas.ruta_de(ORIGEN, {"id": 1, "nombre": "Ana"}, PARADAS, "automatico", P_RUT)
        acum = [p["minutos_acum"] for p in r["paradas"]]
        self.assertEqual(acum, sorted(acum))
        self.assertEqual(r["minutos"], acum[-1])
        self.assertEqual([p["orden"] for p in r["paradas"]], list(range(1, len(PARADAS) + 1)))

    def test_cada_pedido_va_en_una_sola_ruta(self):
        reps = [{"id": 1, "nombre": "Ana"}, {"id": 2, "nombre": "Luis"}]
        plan, sin = rutas.armar_plan(ORIGEN, PARADAS, reps, "automatico", P_RUT)
        ids = [p["pedido"]["id"] for r in plan for p in r["paradas"]]
        self.assertEqual(sorted(ids), sorted(p["id"] for p in PARADAS))
        self.assertEqual(sin, [])
        t = rutas.totales(plan)
        self.assertEqual(t["paradas"], len(PARADAS))
        self.assertAlmostEqual(t["distancia_km"], round(sum(r["distancia_km"] for r in plan), 2), places=2)

    def test_lo_que_no_cabe_en_los_topes_queda_sin_asignar(self):
        muchos = [parada(i, 1 + i % 3, 0.002 * i, -0.002 * i) for i in range(1, 21)]
        reps = [{"id": 1, "nombre": "Ana"}, {"id": 2, "nombre": "Luis"}]       # 2 repartidores × 8 paradas = 16
        plan, sin = rutas.armar_plan(ORIGEN, muchos, reps, "2opt", P_RUT)
        self.assertEqual(rutas.totales(plan)["paradas"], 16)
        self.assertEqual(len(sin), 4)
        self.assertTrue(all(len(r["paradas"]) <= 8 for r in plan))

    def test_comparacion_mide_la_mejora_contra_el_orden_de_llegada(self):
        filas = rutas.comparar_metodos(ORIGEN, PARADAS, P_RUT)
        self.assertEqual(filas[0]["metodo"], "Orden de llegada")
        self.assertEqual(filas[0]["mejora_pct"], 0.0)
        self.assertEqual(len(filas), 4)
        mejor = min(f["distancia_km"] for f in filas)
        self.assertEqual(next(f for f in filas if f["metodo"] == "TSP exacto")["distancia_km"], mejor)
        self.assertGreaterEqual(min(f["mejora_pct"] for f in filas), 0.0)
        con_muchas = rutas.comparar_metodos(ORIGEN, [parada(i, 1, 0.001 * i, 0.002 * (i % 4)) for i in range(1, 12)], P_RUT)
        self.assertEqual(len(con_muchas), 3)                                   # sin el exacto


# --------------------------------------------------------------------
# Surtido
# --------------------------------------------------------------------
def producto(i, precio=30.0, estatus="activo"):
    return {"id": i, "clave_interna": f"AB-{i:03d}", "nombre": f"Producto {i}", "categoria": {"id": 1, "nombre": "Abarrotes"}, "precio": precio, "estatus": estatus}


class Surtido(unittest.TestCase):
    P = dict(surtido.DEFECTOS)

    def filas(self):
        productos = {i: producto(i, 20 + i) for i in range(1, 8)}
        productos[8] = producto(8, estatus="inactivo")
        existencias = {1: {"existencia": 5, "minimo": 20}, 2: {"existencia": 300, "minimo": 10}, 3: {"existencia": 40, "minimo": 10},
                       4: {"existencia": 0, "minimo": 5}, 5: {"existencia": 12, "minimo": 5}, 6: {"existencia": 50, "minimo": 5}, 7: {"existencia": 9, "minimo": 3}}
        ventas = {1: {"unidades": 400, "venta": 8400}, 2: {"unidades": 120, "venta": 2900}, 3: {"unidades": 180, "venta": 4500},
                  4: {"unidades": 80, "venta": 2100}, 5: {"unidades": 30, "venta": 900}, 6: {"unidades": 8, "venta": 260}}
        return surtido.construir_filas(productos, existencias, ventas, {1: 3, 4: 2}, {1: 15.0, 2: 24.0, 3: 20.0}, {1: 1.5}, 0.28)

    def test_solo_entran_los_productos_activos_y_el_costo_faltante_se_estima(self):
        filas = self.filas()
        self.assertEqual(sorted(f["id"] for f in filas), [1, 2, 3, 4, 5, 6, 7])
        self.assertFalse(next(f for f in filas if f["id"] == 1)["costo_estimado"])
        cuatro = next(f for f in filas if f["id"] == 4)
        self.assertTrue(cuatro["costo_estimado"])
        self.assertAlmostEqual(cuatro["costo"], round(24 * (1 - 0.28), 2))
        self.assertEqual(next(f for f in filas if f["id"] == 2)["espacio"], 1.0)         # sin dato de espacio ocupa 1

    def test_clasificacion_abc_por_unidades(self):
        lineas, resumen = surtido.analizar(self.filas(), 90, self.P)
        clase = {l["id"]: l["clase"] for l in lineas}
        self.assertEqual(clase[1], "A")                                                 # 400 de 818 unidades
        self.assertEqual(clase[7], "C")                                                 # sin ventas
        self.assertEqual(resumen["clase_a"] + resumen["clase_b"] + resumen["clase_c"], resumen["productos"])
        self.assertEqual([l["clase"] for l in lineas], sorted(l["clase"] for l in lineas))

    def test_las_recomendaciones(self):
        lineas, _ = surtido.analizar(self.filas(), 90, self.P)
        rec = {l["id"]: l for l in lineas}
        self.assertEqual(rec[1]["recomendacion"], "Aumentar")                          # quiebres y existencia bajo el mínimo
        self.assertGreater(rec[1]["sugerido"], 0)
        self.assertEqual(rec[2]["recomendacion"], "Reducir")                           # 300 en existencia para 1.3 al día
        self.assertEqual(rec[7]["recomendacion"], "Eliminar")                          # no se movió en 90 días
        self.assertEqual(rec[1]["demanda_dia"], round(400 / 90, 2))

    def test_el_espacio_limita_lo_que_se_sugiere_aumentar(self):
        filas = self.filas()
        sin_limite, _ = surtido.analizar(filas, 90, self.P)
        pedido = sum(l["sugerido"] for l in sin_limite)
        ocupado = sum(f["existencia"] * f["espacio"] for f in filas)
        con, resumen = surtido.analizar(filas, 90, self.P, espacio_total=ocupado + 10)
        self.assertLess(sum(l["sugerido"] for l in con), pedido)
        self.assertLessEqual(resumen["espacio"]["ocupado"] + resumen["espacio"]["sugerido"], ocupado + 10 + 1e-6)
        self.assertTrue(any(l["limitado_por"] == "espacio" for l in con))

    def test_el_presupuesto_limita_y_lo_que_no_cabe_se_excluye(self):
        con, resumen = surtido.analizar(self.filas(), 90, self.P, presupuesto=1.0)
        self.assertEqual(sum(l["sugerido"] for l in con), 0)
        self.assertEqual(resumen["presupuesto"]["requerido"], 0.0)
        excluidos = [l for l in con if l["recomendacion"] == "Excluir"]
        self.assertTrue(excluidos)
        self.assertTrue(all(l["limitado_por"] == "presupuesto" for l in excluidos))

    def test_la_clase_a_se_surte_antes_que_la_c(self):
        productos = {1: producto(1, 50), 2: producto(2, 50)}
        existencias = {1: {"existencia": 0, "minimo": 5}, 2: {"existencia": 0, "minimo": 5}}
        ventas = {1: {"unidades": 900, "venta": 1}, 2: {"unidades": 10, "venta": 1}}
        filas = surtido.construir_filas(productos, existencias, ventas, {1: 1, 2: 1}, {1: 40.0, 2: 40.0}, {}, 0.28)
        con, _ = surtido.analizar(filas, 90, self.P, presupuesto=600.0)
        por_id = {l["id"]: l for l in con}
        self.assertEqual(por_id[1]["clase"], "A")
        self.assertGreater(por_id[1]["sugerido"], por_id[2]["sugerido"])

    def test_el_resumen_abc_suma_cien(self):
        lineas, _ = surtido.analizar(self.filas(), 90, self.P)
        clases = surtido.resumen_abc(lineas)
        self.assertEqual([c["clase"] for c in clases], ["A", "B", "C"])
        self.assertAlmostEqual(sum(c["pct_unidades"] for c in clases), 100.0, delta=0.2)
        self.assertAlmostEqual(sum(c["pct_venta"] for c in clases), 100.0, delta=0.2)


# --------------------------------------------------------------------
# Simulación
# --------------------------------------------------------------------
def escenario(**cambios):
    e = {"pedidos_dia": 60.0, "ticket": 135.0, "margen_bruto": 0.28, "costos_fijos_mes": 60000.0, "costo_variable_pedido": 32.6, "dias_mes": 30.0,
         "operadores": 3, "repartidores": 3, "capacidad_fisica": None, "horas": 10.0, "distancia_km": 2.4, "ausentismo": 0.05, "variacion_demanda": 0.10,
         "indice_semanal": [0.9, 0.9, 0.95, 1.0, 1.15, 1.25, 0.85], "dia_inicio": 1, "dias": 30,
         "modelo": {k: simulacion.DEFECTOS[k] for k in (*simulacion.PARAMS_CAPACIDAD, "umbral_utilizacion_riesgo")}}
    e.update(cambios)
    return e


class Simulacion(unittest.TestCase):
    def test_misma_entrada_y_semilla_misma_huella(self):
        a, b = simulacion.simular(escenario(), 2026, 50), simulacion.simular(escenario(), 2026, 50)
        self.assertEqual(simulacion.huella_de(a), simulacion.huella_de(b))
        self.assertEqual(a, b)

    def test_otra_semilla_otro_resultado(self):
        self.assertNotEqual(simulacion.huella_de(simulacion.simular(escenario(), 1, 50)), simulacion.huella_de(simulacion.simular(escenario(), 2, 50)))

    def test_cambiar_un_dato_cambia_la_huella(self):
        self.assertNotEqual(simulacion.huella_de(simulacion.simular(escenario(), 7, 50)),
                            simulacion.huella_de(simulacion.simular(escenario(ticket=140.0), 7, 50)))

    def test_agregar_replicas_no_cambia_las_anteriores(self):
        e = escenario()
        caps = simulacion.Capacidades(e)
        primera, _ = simulacion.una_replica(random.Random(2026 * 1_000_003), e, caps)
        otra, _ = simulacion.una_replica(random.Random(2026 * 1_000_003), e, simulacion.Capacidades(e))
        self.assertEqual(primera, otra)

    def test_sin_variacion_ni_ausentismo_el_resultado_es_el_de_la_cuenta_directa(self):
        # demanda 20 al día con capacidad de sobra: atendidos 600 en 30 días; utilidad = 600 × 5.2 − 60,000
        e = escenario(pedidos_dia=20.0, ausentismo=0.0, variacion_demanda=0.0, indice_semanal=[1.0] * 7)
        r = simulacion.simular(e, 5, 40)
        m = {x["clave"]: x for x in r["metricas"]}
        self.assertAlmostEqual(m["atendidos"]["media"], 600, delta=25)              # Poisson: 20 × 30 ± 5 %
        self.assertAlmostEqual(m["utilidad"]["media"], m["atendidos"]["media"] * 5.2 - 60000, places=2)
        self.assertEqual(m["rechazados"]["media"], 0)
        self.assertEqual(r["prob_perdida_pct"], 100.0)

    def test_si_falta_capacidad_se_rechaza(self):
        r = simulacion.simular(escenario(pedidos_dia=400.0, operadores=1, repartidores=1, ausentismo=0.0, variacion_demanda=0.0), 3, 30)
        m = {x["clave"]: x for x in r["metricas"]}
        self.assertGreater(m["rechazados"]["media"], 0)
        self.assertGreater(r["dias_saturados_pct"], 90.0)
        cap = simulacion.Capacidades(escenario()).dia(1, 1)
        self.assertLessEqual(m["atendidos"]["maximo"], cap * 30)

    def test_si_todo_el_personal_falta_no_se_atiende_nada(self):
        r = simulacion.simular(escenario(ausentismo=0.5, operadores=1, repartidores=1), 9, 30)
        self.assertGreater(r["dias_saturados_pct"], 20.0)                           # la mitad de los días sin operador o sin repartidor, aprox.

    def test_los_percentiles_estan_ordenados(self):
        for m in simulacion.simular(escenario(), 11, 100)["metricas"]:
            self.assertLessEqual(m["minimo"], m["p10"])
            self.assertLessEqual(m["p10"], m["p50"])
            self.assertLessEqual(m["p50"], m["p90"])
            self.assertLessEqual(m["p90"], m["maximo"])

    def test_se_puede_cancelar_a_la_mitad(self):
        llamadas = []
        self.assertIsNone(simulacion.simular(escenario(), 1, 100, cancelada=lambda: llamadas.append(1) or len(llamadas) >= 2))
        self.assertEqual(len(llamadas), 2)

    def test_percentil_con_interpolacion(self):
        self.assertEqual(simulacion.percentil([1, 2, 3, 4], 50), 2.5)
        self.assertEqual(simulacion.percentil([5], 90), 5.0)
        self.assertEqual(simulacion.percentil([], 10), 0.0)
        self.assertEqual(simulacion.percentil([10, 20, 30], 0), 10.0)
        self.assertEqual(simulacion.percentil([10, 20, 30], 100), 30.0)

    def test_poisson_tiene_la_media_pedida(self):
        rng = random.Random(1)
        for media in (3.0, 12.0, 80.0):
            muestra = [simulacion.poisson(rng, media) for _ in range(4000)]
            self.assertAlmostEqual(sum(muestra) / len(muestra), media, delta=media * 0.06)
        self.assertEqual(simulacion.poisson(rng, 0), 0)

    def test_la_serie_trae_un_renglon_por_dia_y_la_utilidad_acumulada(self):
        r = simulacion.simular(escenario(dias=10), 4, 20)
        self.assertEqual([s["dia"] for s in r["serie"]], list(range(1, 11)))
        self.assertAlmostEqual(r["serie"][-1]["utilidad_acumulada_media"], next(m for m in r["metricas"] if m["clave"] == "utilidad")["media"], delta=0.05)

    def test_el_contraste_compara_con_el_escenario_sin_variacion(self):
        r = simulacion.simular(escenario(), 8, 60)
        c = r["contraste"]
        self.assertAlmostEqual(c["diferencia"], c["utilidad_media"] - c["utilidad_sin_variacion"], places=3)



class IndependenciaDelPortal(unittest.TestCase):
    """Los microservicios no dependen del sistema web, y aun así calculan lo mismo."""

    def test_ningun_servicio_importa_ni_copia_codigo_del_portal(self):
        raiz = Path(__file__).resolve().parents[1]
        archivos = [f for f in raiz.rglob("*") if (f.suffix == ".py" or f.name == "Dockerfile") and "pruebas" not in f.parts]
        self.assertGreater(len(archivos), 50)
        for f in archivos:
            texto = f.read_text(encoding="utf-8")
            for prohibido in ("COPY sistema_web", "/app/web", 'parents[2] / "sistema_web"'):
                self.assertNotIn(prohibido, texto, f"{f} depende del portal")

    def test_las_formulas_son_identicas_a_las_del_portal(self):
        propia = Path(__file__).resolve().parents[1] / "comun" / "planeacion_calc.py"
        portal = next((p for p in (Path("/sistema_web/planeacion_calc.py"), Path(__file__).resolve().parents[2] / "sistema_web" / "planeacion_calc.py")
                       if p.is_file()), None)
        if portal is None:
            self.skipTest("el código del portal no está disponible en este contenedor")
        self.assertEqual(propia.read_text(encoding="utf-8").replace("\r\n", "\n"), portal.read_text(encoding="utf-8").replace("\r\n", "\n"))

if __name__ == "__main__":
    unittest.main(verbosity=2)
