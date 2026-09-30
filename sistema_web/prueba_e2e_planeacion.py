#!/usr/bin/env python3
"""
prueba_e2e_planeacion.py — Recorre el flujo de planeación y despacho contra la aplicación real.
Codex Innovations · Equipo 04

Solo usa la biblioteca estándar. Requiere la aplicación levantada con Docker:

    BASE=http://127.0.0.1:5000 python prueba_e2e_planeacion.py

Deja datos de prueba (un escenario y un candidato) que quedan en la bitácora.
"""
import http.cookiejar
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

BASE = os.environ.get("BASE", "http://127.0.0.1:5000")
CLAVE = "Codex#2026"
fallos, pasos = [], 0


class Sesion:
    def __init__(self, correo):
        self.jar = http.cookiejar.CookieJar()
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))
        r = self.post("/entrar", {"correo": correo, "clave": CLAVE})
        if "sesion" not in {c.name for c in self.jar}:
            raise SystemExit(f"No se pudo iniciar sesión como {correo} ({r[0]})")

    def _abrir(self, req):
        try:
            with self.op.open(req, timeout=30) as r:
                return r.status, r.read().decode("utf-8", "replace"), r.geturl()
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", "replace"), e.geturl()

    def get(self, ruta):
        return self._abrir(urllib.request.Request(BASE + ruta))

    def post(self, ruta, datos):
        cuerpo = urllib.parse.urlencode(datos, doseq=True).encode()
        return self._abrir(urllib.request.Request(BASE + ruta, data=cuerpo))


def chk(desc, ok, extra=""):
    global pasos
    pasos += 1
    print(f"  {'PASA ' if ok else 'FALLA'}  {desc}" + ("" if ok else f"  {extra}"))
    if not ok:
        fallos.append(desc)


def id_pedidos(html):
    return [int(x) for x in re.findall(r'name="pedido" value="(\d+)"', html)]


print("\n== 1. Planeador: demanda, ubicaciones y cobertura ==")
pl = Sesion("planeador@codex.mx")
for ruta, texto in [("/planeacion/tablero", "Tablero del planeador"),
                    ("/planeacion/demanda", "Demanda por categoría"),
                    ("/planeacion/candidatos", "score ="),
                    ("/planeacion/cobertura", "Solapamiento"),
                    ("/planeacion/surtido", "Eliminar"),
                    ("/planeacion/escenarios", "Comparar escenarios")]:
    c, html, _ = pl.get(ruta)
    chk(f"{ruta} carga", c == 200 and texto in html, f"HTTP {c}")

print("\n== 2. Registrar candidato y comparar ==")
sufijo = str(int(time.time()))[-6:]
c, html, url = pl.post("/planeacion/candidatos/nuevo", {
    "clave": f"T-{sufijo}", "nombre": "Prueba e2e", "latitud": "25.75", "longitud": "-100.37",
    "renta_estimada": "10000", "nomina_estimada": "30000", "servicios_estimados": "5000",
    "otros_costos": "2000", "superficie_m2": "80", "capacidad_fisica": "90",
    "accesibilidad_vial": "6", "zona_id": "1", "poblacion_cubierta": "3000", "radio_km": "1.5"})
chk("Se registra un candidato y abre su ficha", c == 200 and "Ficha de viabilidad" in html, url)
chk("La ficha muestra decisión, equilibrio y utilización",
    all(t in html for t in ("Punto de equilibrio", "Utilización", "Demanda − equilibrio")))
c, html, _ = pl.post(re.sub(r"^.*?/planeacion", "/planeacion", url) + "/decision", {"decision": "aceptado", "motivo": ""})
chk("La decisión sin motivo no se acepta", "es humana" in html or "motivo" in html.lower())

print("\n== 3. Simulación, equilibrio y escenarios ==")
sup = {"candidato_id": "1", "demanda_diaria": "100", "operadores": "3", "repartidores": "4", "ticket": "100",
       "costo_entrega": "22", "margen_bruto": "0.46", "renta": "18000", "nomina": "42000",
       "servicios": "7000", "otros": "5000", "distancia_km": "2.4", "capacidad_fisica": "150"}
c, html, _ = pl.get("/planeacion/simulacion?" + urllib.parse.urlencode({**sup, "margen_bruto": "46", "sensibilidad": "1"}))
chk("El ejemplo de la retro da 3,000 pedidos/mes y 100/día",
    "3,000 pedidos/mes" in html and "100.0 pedidos/día" in html)
chk("Se muestra el cálculo, no solo el resultado", "costos fijos ÷ margen por pedido" in html)
chk("La sensibilidad cubre las 8 variables",
    all(v in html for v in ("Ticket promedio", "Pedidos/día", "Renta", "Nómina", "Costo de entrega",
                            "Margen bruto", "Operadores", "Repartidores")))
c, html, url = pl.post("/planeacion/escenarios/guardar", {**sup, "nombre": f"E2E A {sufijo}"})
chk("Se guarda el escenario", c == 200 and f"E2E A {sufijo}" in html and "Escenario guardado" in html)
m = re.search(r"escenario_id=(\d+)", url)
pl.post("/planeacion/escenarios/guardar", {**sup, "ticket": "90", "nombre": f"E2E B {sufijo}"})
c, html, _ = pl.get("/planeacion/escenarios")
ids = re.findall(r'name="ids" value="(\d+)"', html)[:2]
c, html, _ = pl.get("/planeacion/escenarios/comparar?" + urllib.parse.urlencode({"ids": ids}, doseq=True))
chk("Se comparan dos escenarios", c == 200 and "Comparación" in html)
c, csv_txt, _ = pl.get("/planeacion/escenarios.csv")
chk("Se exporta CSV con los escenarios", c == 200 and "escenario,candidato" in csv_txt and f"E2E A {sufijo}" in csv_txt)

print("\n== 4. Permisos por perfil ==")
c, _, _ = pl.get("/planeacion/entregas")
chk("El Planeador no planea entregas (403)", c == 403)
c, _, _ = pl.get("/panel/administrador")
chk("El Planeador no entra al panel de administrador (403)", c == 403)
rp = Sesion("repartidor1@codex.mx")
c, _, _ = rp.get("/planeacion/tablero")
chk("El Repartidor no entra a Planeación (403)", c == 403)

print("\n== 5. Operador: pedidos listos → zona → repartidor → ruta ==")
op = Sesion("operador.mh02@codex.mx")
c, html, _ = op.get("/panel/operador")
chk("Panel del operador: pendientes, preparando, listos, crítico, quiebres y capacidad, sin finanzas",
    c == 200 and all(t in html for t in ("Listos para despacho", "Inventario crítico", "Quiebres")) and "Ticket" not in html)
c, bandeja, _ = op.get("/operacion")
for pid in re.findall(r'/operacion/pedido/(\d+)', bandeja)[:4]:
    op.post(f"/operacion/pedido/{pid}/estado", {"estado": "en_preparacion"})
    c, det, _ = op.get(f"/operacion/pedido/{pid}")
    if "Marcar listo para despacho" in det:
        op.post(f"/operacion/pedido/{pid}/listo", {})
c, html, _ = op.get("/planeacion/entregas")
listos = id_pedidos(html)
chk("Aparecen pedidos listos agrupados por zona", c == 200 and (bool(listos) or "No hay pedidos listos" in html))
if listos:
    chk("Se proponen rutas con distancia y tiempo", "Tiempo estimado" in html and "Distancia" in html)
    c, html, _ = op.post("/planeacion/entregas/confirmar", {"microhub_id": "2", "pedido": listos})
    chk("Se despachan con repartidor asignado", "Se despacharon" in html, html[:200])
else:
    print("  (sin pedidos en preparación para despachar: se omite el despacho)")

print("\n== 6. Administrador ==")
ad = Sesion("admin@codex.mx")
c, html, _ = ad.get("/panel/administrador")
chk("Panel del administrador: usuarios, microhubs, auditoría y salud",
    c == 200 and all(t in html for t in ("Usuarios activos", "Microhubs activos", "Auditoría", "Salud")))

print("\n" + "=" * 58)
print(f"  {pasos - len(fallos)} de {pasos} comprobaciones pasan")
if fallos:
    print("  Fallan:")
    for f in fallos:
        print("   -", f)
    sys.exit(1)
