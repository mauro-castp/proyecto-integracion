#!/usr/bin/env python3
"""revisar.py — captura las pantallas del prototipo y prueba las interacciones."""
from playwright.sync_api import sync_playwright
import pathlib, sys

RUTA = "file:///mnt/user-data/outputs/bloque_d/prototipos.html"
SALIDA = pathlib.Path("/home/claude/bc/capturas")
SALIDA.mkdir(parents=True, exist_ok=True)

PANTALLAS = [
    ("web", "Catálogo público",        "web-catalogo"),
    ("web", "Carrito y confirmación",  "web-carrito"),
    ("web", "Indicadores",             "web-indicadores"),
    ("web", "Bitácora de auditoría",   "web-bitacora"),
    ("mov", "Ruta del turno",          "mov-ruta"),
    ("mov", "Cierre de entrega",       "mov-cierre"),
    ("mov", "Sin conexión",            "mov-offline"),
    ("esc", "Bandeja del microhub",    "esc-bandeja"),
    ("esc", "Preparación",             "esc-preparacion"),
]

errores = []

with sync_playwright() as p:
    nav = p.chromium.launch()
    pg = nav.new_page(viewport={"width": 1280, "height": 1000}, device_scale_factor=2)
    pg.on("console", lambda m: errores.append(f"consola {m.type}: {m.text}")
          if m.type == "error" else None)
    pg.on("pageerror", lambda e: errores.append(f"pageerror: {e}"))

    pg.goto(RUTA)
    pg.wait_for_timeout(2500)   # espera a las fuentes

    for plat, etiqueta, ident in PANTALLAS:
        pg.click(f'.plataformas button[data-plat="{plat}"]')
        pg.wait_for_timeout(200)
        pg.click(f'#pantallas button:has-text("{etiqueta}")')
        pg.wait_for_timeout(400)
        vis = pg.eval_on_selector(f'.vista[data-v="{ident}"]',
                                  "e => getComputedStyle(e).display")
        if vis == "none":
            errores.append(f"{ident}: la vista no se muestra")
        pg.screenshot(path=str(SALIDA / f"{ident}.png"), full_page=True)

    # ---- interacción 1: código postal ambiguo ----
    pg.click('.plataformas button[data-plat="web"]')
    pg.click('#pantallas button:has-text("Catálogo")')
    pg.fill("#cp", "64103"); pg.click('.cob button'); pg.wait_for_timeout(250)
    t = pg.inner_text("#resCob")
    if "Dos colonias" not in t:
        errores.append("cobertura 64103: no detecta la ambigüedad")
    pg.screenshot(path=str(SALIDA / "int_cobertura_ambigua.png"), full_page=True)

    pg.fill("#cp", "64999"); pg.click('.cob button'); pg.wait_for_timeout(250)
    if "Todavía no llegamos" not in pg.inner_text("#resCob"):
        errores.append("cobertura fuera: mensaje incorrecto")

    # ---- interacción 2: carrito alcanza el ticket mínimo ----
    pg.click('#pantallas button:has-text("Carrito")'); pg.wait_for_timeout(200)
    if not pg.is_disabled("#btnConf"):
        errores.append("carrito: el botón debería iniciar deshabilitado")
    pg.click('button:has-text("Agregar otro producto")'); pg.wait_for_timeout(250)
    if pg.is_disabled("#btnConf"):
        errores.append("carrito: el botón sigue deshabilitado al superar el mínimo")
    if pg.inner_text("#sub") != "$108.00":
        errores.append(f"carrito: subtotal inesperado {pg.inner_text('#sub')}")
    pg.screenshot(path=str(SALIDA / "int_carrito_ok.png"), full_page=True)

    # ---- interacción 3: cálculo del cambio ----
    pg.click('.plataformas button[data-plat="mov"]'); pg.wait_for_timeout(150)
    pg.click('#pantallas button:has-text("Cierre")'); pg.wait_for_timeout(250)
    if pg.inner_text("#cam") != "$37.50":
        errores.append(f"cierre: cambio inicial {pg.inner_text('#cam')}")
    pg.fill("#rec", "300"); pg.wait_for_timeout(200)
    if "Falta" not in pg.inner_text("#cam"):
        errores.append("cierre: no avisa cuando el pago no cubre el total")
    pg.click('button:has-text("Cerrar entrega")'); pg.wait_for_timeout(200)
    if "no cubre" not in pg.inner_text("#msgCierre"):
        errores.append("cierre: permite cerrar con monto insuficiente")
    pg.screenshot(path=str(SALIDA / "int_cierre_insuficiente.png"), full_page=True)

    pg.click('.opcion:has-text("No se entregó")'); pg.wait_for_timeout(200)
    if pg.eval_on_selector("#bloqueMotivo", "e => getComputedStyle(e).display") == "none":
        errores.append("cierre: no aparece el motivo obligatorio")
    pg.screenshot(path=str(SALIDA / "int_cierre_fallida.png"), full_page=True)

    # ---- interacción 4: surtido por líneas ----
    pg.click('.plataformas button[data-plat="esc"]'); pg.wait_for_timeout(150)
    pg.click('#pantallas button:has-text("Preparación")'); pg.wait_for_timeout(250)
    if not pg.is_disabled("#btnRuta"):
        errores.append("preparación: el botón debería iniciar deshabilitado")
    for c in pg.query_selector_all(".pick input"):
        if not c.is_checked():
            c.check()
    pg.wait_for_timeout(250)
    if pg.is_disabled("#btnRuta"):
        errores.append("preparación: el botón no se habilita con todo surtido")
    pg.screenshot(path=str(SALIDA / "int_surtido_completo.png"), full_page=True)

    # ---- pantalla chica ----
    pg2 = nav.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
    pg2.goto(RUTA); pg2.wait_for_timeout(2000)
    pg2.screenshot(path=str(SALIDA / "movil_estrecho.png"), full_page=True)
    ancho = pg2.evaluate("document.documentElement.scrollWidth")
    if ancho > 400:
        errores.append(f"pantalla chica: hay desbordamiento horizontal ({ancho}px)")

    nav.close()

print("=" * 58)
if errores:
    print("PROBLEMAS ENCONTRADOS:")
    for e in errores:
        print("  -", e)
    sys.exit(1)
print("Sin errores. Capturas en", SALIDA)
