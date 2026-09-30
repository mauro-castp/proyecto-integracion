"""
planeacion_demo.py — Datos de demostración para el modo local (sin Docker ni PostgreSQL)

Reproduce el ejemplo de la retroalimentación (San Bernabé 82 pedidos/día,
Valles 54, Paseo 39) para que el módulo de Planeación se pueda probar con
`python app_local.py`. Los candidatos y escenarios que se registren viven en
memoria mientras corre el proceso.
"""
import datetime as dt

DIAS = 30

# Zonas: centroides de 03_semilla.sql; demanda tomada de la tabla de ejemplo.
_ZONAS = [
    # id, clave, nombre, lat, lng, población, pedidos/día, ticket, no atendidos (periodo), pico, productos/pedido
    (1, "ZN-SB01", "San Bernabé Centro", 25.7455, -100.3585, 8420, 82, 142, 14, "18–20 h", 3.4),
    (2, "ZN-SB02", "Valles de San Bernabé", 25.7530, -100.3690, 6180, 54, 118, 21, "19–21 h", 2.8),
    (3, "ZN-SB03", "Paseo de San Bernabé", 25.7580, -100.3745, 5240, 39, 126, 18, "17–20 h", 3.1),
    (4, "ZN-SB04", "San Bernabé X (F-113)", 25.7495, -100.3800, 4310, 21, 112, 9, "18–20 h", 2.6),
]
_HORAS = {8: 4, 9: 7, 10: 9, 11: 10, 12: 13, 13: 12, 14: 9, 15: 8, 16: 14, 17: 22, 18: 31, 19: 28, 20: 19, 21: 6}
_CATEGORIAS = [("Abarrote básico", 2900, 41200, 1450), ("Bebidas", 2100, 27800, 1180),
               ("Lácteos y huevo", 1500, 26300, 1020), ("Limpieza del hogar", 620, 21400, 540),
               ("Higiene personal", 410, 16500, 370)]
_NO_ATENDIDA = [("fuera_cobertura", 27), ("sin_existencia", 18), ("bajo_ticket_minimo", 12),
                ("sin_microhub_elegible", 5)]

HUBS = [
    {"id": 1, "clave": "MH-01", "nombre": "Microhub San Bernabé Centro", "lat": 25.748, "lng": -100.364, "radio_km": 1.5},
    {"id": 2, "clave": "MH-02", "nombre": "Microhub Valles", "lat": 25.7555, "lng": -100.372, "radio_km": 1.5},
    {"id": 3, "clave": "MH-03", "nombre": "Microhub Poniente F-113", "lat": 25.750, "lng": -100.381, "radio_km": 1.2},
]

_CANDIDATOS = [
    # id, clave, nombre, lat, lng, renta, nómina, servicios, otros, m2, cap. física, acc., zona_id, población, radio
    (1, "CAND-01", "San Bernabé Norte", 25.752, -100.361, 18000, 42000, 7000, 5000, 130, 150, 9, 1, 8420, 1.5),
    (2, "CAND-02", "Valles Poniente", 25.7555, -100.376, 15500, 42000, 6500, 4500, 105, 120, 7, 2, 6180, 1.5),
    (3, "CAND-03", "Paseo Sur", 25.759, -100.372, 14000, 38000, 6000, 4000, 95, 110, 6, 3, 5240, 1.4),
    (4, "CAND-04", "F-113 Oriente", 25.747, -100.3765, 12500, 38000, 5500, 4000, 90, 100, 5, 4, 4310, 1.3),
    (5, "CAND-05", "Alianza Real", 25.7625, -100.353, 21000, 46000, 8000, 6000, 150, 180, 8, 3, 3900, 1.6),
]

_SKU = [
    # clave, nombre, categoría, precio, unidades, existencia, mínimo, quiebres
    ("AB-001", "Arroz 1 kg", "Abarrote básico", 32.5, 2100, 150, 60, 0),
    ("AB-002", "Frijol 900 g", "Abarrote básico", 36.0, 1500, 40, 60, 3),
    ("BE-001", "Agua purificada 1.5 L", "Bebidas", 18.0, 1900, 210, 80, 0),
    ("BE-002", "Refresco cola 600 ml", "Bebidas", 21.0, 1200, 30, 50, 2),
    ("LA-001", "Leche entera 1 L", "Lácteos y huevo", 27.5, 1400, 90, 60, 1),
    ("LA-002", "Huevo docena", "Lácteos y huevo", 48.0, 900, 70, 40, 0),
    ("LI-001", "Detergente 850 g", "Limpieza del hogar", 46.9, 380, 260, 30, 0),
    ("LI-002", "Cloro 1 L", "Limpieza del hogar", 24.0, 160, 120, 20, 0),
    ("HI-001", "Jabón de tocador", "Higiene personal", 14.5, 250, 45, 30, 0),
    ("HI-002", "Pasta dental", "Higiene personal", 38.0, 90, 400, 20, 0),
    ("AB-009", "Sal de mesa 1 kg", "Abarrote básico", 15.0, 40, 300, 15, 0),
    ("AB-010", "Té de manzanilla", "Abarrote básico", 29.0, 0, 85, 10, 0),
]

PEDIDOS_LISTOS = [
    ("PED-DEMO-001", 1, "San Bernabé Centro", 25.7490, -100.3610, 168.0),
    ("PED-DEMO-002", 1, "San Bernabé Centro", 25.7475, -100.3595, 143.5),
    ("PED-DEMO-003", 2, "Valles de San Bernabé", 25.7535, -100.3705, 205.0),
    ("PED-DEMO-004", 2, "Valles de San Bernabé", 25.7560, -100.3680, 119.0),
    ("PED-DEMO-005", 3, "Paseo de San Bernabé", 25.7590, -100.3750, 176.0),
    ("PED-DEMO-006", 3, "Paseo de San Bernabé", 25.7575, -100.3730, 150.0),
]
REPARTIDORES = [{"id": 101, "nombre": "Ramiro Alanís (demo)"}, {"id": 102, "nombre": "Diana Sepúlveda (demo)"}]

# Almacenes en memoria de la sesión local.
candidatos_mem = []
escenarios_mem = []
_sec = {"cand": 100, "esc": 0}


def candidatos():
    if not candidatos_mem:
        zonas = {z[0]: z[2] for z in _ZONAS}
        for c in _CANDIDATOS:
            candidatos_mem.append({
                "id": c[0], "clave": c[1], "nombre": c[2], "latitud": c[3], "longitud": c[4], "lat": c[3], "lng": c[4],
                "renta_estimada": c[5], "nomina_estimada": c[6], "servicios_estimados": c[7], "otros_costos": c[8],
                "costo_fijo": c[5] + c[6] + c[7] + c[8], "superficie_m2": c[9], "capacidad_fisica": c[10],
                "accesibilidad_vial": c[11], "zona_id": c[12], "zona": zonas[c[12]], "poblacion_cubierta": c[13],
                "radio_km": c[14], "decision": "pendiente", "decision_motivo": None, "estatus": "activo"})
    return candidatos_mem


def nuevo_candidato(d):
    _sec["cand"] += 1
    zonas = {z[0]: z[2] for z in _ZONAS}
    fila = {**d, "id": _sec["cand"], "lat": d["latitud"], "lng": d["longitud"],
            "costo_fijo": d["renta_estimada"] + d["nomina_estimada"] + d["servicios_estimados"] + d["otros_costos"],
            "zona": zonas.get(d["zona_id"], "—"), "decision": "pendiente", "decision_motivo": None, "estatus": "activo"}
    candidatos()
    candidatos_mem.append(fila)
    return fila["id"]


def historial():
    zonas, tot_p, suma_ticket, suma_prod = [], 0.0, 0.0, 0.0
    for z in _ZONAS:
        _id, clave, nombre, lat, lng, pob, ped_dia, ticket, no_at, pico, prod = z
        zonas.append({"id": _id, "clave": clave, "nombre": nombre, "lat": lat, "lng": lng, "poblacion": pob,
                      "pedidos": ped_dia * DIAS, "ticket": float(ticket), "productos_pedido": prod,
                      "pedidos_dia": float(ped_dia), "no_atendidos": no_at, "no_atendidos_dia": round(no_at / DIAS, 2),
                      "demanda_dia": ped_dia + no_at / DIAS, "pico": pico})
        tot_p += ped_dia * DIAS
        suma_ticket += ticket * ped_dia * DIAS
        suma_prod += prod * ped_dia * DIAS
    horas = [0] * 24
    for h, n in _HORAS.items():
        horas[h] = n * DIAS
    i = max(range(23), key=lambda k: horas[k] + horas[k + 1])
    return {"dias": DIAS, "zonas": zonas, "horas": horas, "pico": f"{i}–{i + 2} h",
            "no_atendida_tipo": [{"tipo": t, "n": n} for t, n in _NO_ATENDIDA],
            "categorias": [{"nombre": n, "unidades": u, "ventas": v, "pedidos": p} for n, u, v, p in _CATEGORIAS],
            "pedidos": tot_p, "pedidos_dia": round(tot_p / DIAS, 2), "ticket": round(suma_ticket / tot_p, 2),
            "productos_pedido": round(suma_prod / tot_p, 1), "no_atendidos": sum(n for _, n in _NO_ATENDIDA),
            "ventana": 90}


def surtido_filas(margen_default):
    filas = []
    for i, (clave, nombre, cat, precio, unid, exist, minimo, quiebres) in enumerate(_SKU, 1):
        filas.append({"id": i, "clave_interna": clave, "nombre": nombre, "categoria": cat, "precio": precio,
                      "costo": round(precio * (1 - margen_default), 2), "espacio": 1.0, "unidades": unid,
                      "ventas": round(unid * precio, 2), "existencia": exist, "minimo": minimo,
                      "quiebres": quiebres + (1 if exist == 0 else 0)})
    return filas


def escenario_nuevo(nombre, cand_id, supuestos, resultados, esc_id=None):
    ahora = dt.datetime.now()
    clave = next((c["clave"] for c in candidatos() if c["id"] == cand_id), None)
    if esc_id:
        for e in escenarios_mem:
            if e["id"] == int(esc_id):
                e.update(nombre=nombre, ubicacion_candidata_id=cand_id, candidato=clave, supuestos=supuestos,
                         resultados=resultados, actualizado_en=ahora)
                return e["id"]
    _sec["esc"] += 1
    escenarios_mem.append({"id": _sec["esc"], "nombre": nombre, "ubicacion_candidata_id": cand_id, "candidato": clave,
                           "supuestos": supuestos, "resultados": resultados, "creado_en": ahora,
                           "actualizado_en": ahora, "autor": "Modo local"})
    return _sec["esc"]
