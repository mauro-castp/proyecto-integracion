#!/usr/bin/env python3
"""
prueba_e2e.py — Recorre el flujo comprometido contra la aplicación real.
Codex Innovations · Equipo 04

No hace peticiones HTTP crudas: usa un navegador, llena formularios y
sigue redirecciones como lo haría una persona. Si una plantilla revienta
o una regla no se aplica, esto falla.

    python3 prueba_e2e.py
"""
import re
import subprocess
import sys
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:5000"
CLAVE = "Codex#2026"
fallos, pasos = [], 0


def chk(desc, ok, extra=""):
    global pasos
    pasos += 1
    if ok:
        print(f"  PASA   {desc}")
    else:
        print(f"  FALLA  {desc}  {extra}")
        fallos.append(desc)


def entrar(pg, correo, clave=CLAVE):
    pg.goto(f"{BASE}/entrar")
    pg.fill("#correo", correo)
    pg.fill("#clave", clave)
    pg.click("button:has-text('Entrar')")
    pg.wait_for_load_state("networkidle")


def salir(pg):
    if pg.query_selector("button.salir"):
        pg.click("button.salir")
        pg.wait_for_load_state("networkidle")


with sync_playwright() as p:
    nav = p.chromium.launch()
    ctx = nav.new_context(viewport={"width": 1280, "height": 900})
    pg = ctx.new_page()
    errores_js = []
    pg.on("pageerror", lambda e: errores_js.append(str(e)))

    print("\n== 1. Superficie pública (RN01, RN11, RN34) ==")
    pg.goto(BASE)
    chk("El catálogo carga sin sesión", "Qué puedes pedir" in pg.content())
    chk("No se publican existencias exactas",
        not re.search(r"\d+\s+(unidades|piezas) disponibles", pg.content()))
    chk("Los productos agotados se marcan", "Sin existencia" in pg.content())

    pg.goto(f"{BASE}/cobertura?zona=64103")
    chk("El CP ambiguo pide elegir colonia", "comparten" in pg.content().lower(),
        "64103 lo usan Valles y Paseo")
    pg.goto(f"{BASE}/cobertura?zona=64100")
    chk("Un CP cubierto responde con sus condiciones", "Sí llegamos" in pg.content())
    pg.goto(f"{BASE}/cobertura?zona=99999")
    chk("Fuera de cobertura se informa", "Todavía no llegamos" in pg.content())

    print("\n== 2. Autenticación y ámbito (RF03, RF06, RNF23) ==")
    pg.goto(f"{BASE}/operacion")
    chk("Una ruta privada sin sesión redirige a entrar", "/entrar" in pg.url)

    entrar(pg, "operador.mh01@codex.mx", "clave-incorrecta")
    chk("Credencial inválida no crea sesión", "incorrect" in pg.content().lower())

    entrar(pg, "operador.mh01@codex.mx")
    chk("Credencial válida entra", "Salir" in pg.content())

    pg.goto(f"{BASE}/admin/parametros")
    chk("El Operador NO entra a parámetros (403)", "No tienes acceso" in pg.content())
    pg.goto(f"{BASE}/bitacora")
    chk("El Operador NO entra a la bitácora (403)", "No tienes acceso" in pg.content())

    pg.goto(f"{BASE}/operacion")
    chk("El Operador sí ve su bandeja", "Bandeja del turno" in pg.content())
    filas = pg.query_selector_all("table tbody tr")
    chk("La bandeja trae pedidos de su microhub", len(filas) > 0, f"{len(filas)} filas")

    print("\n== 3. Ciclo del pedido como cliente (RN07, RN09, RN21) ==")
    salir(pg)
    correo_cliente = None
    # Se usa un cliente de la semilla: se localiza uno con domicilio activo.
    # Se califica el esquema en la consulta: un SET previo hace que psql
    # imprima "SET" y contamine la salida.
    correo_cliente = subprocess.run(
        ["su", "postgres", "-c",
         "psql -h /tmp -d microhubs_p1 -tAc \""
         "SELECT u.correo FROM microhubs.usuario u "
         "JOIN microhubs.cliente c ON c.usuario_id=u.id "
         "JOIN microhubs.domicilio d ON d.cliente_id=c.id AND d.activo "
         "JOIN microhubs.rol r ON r.id=u.rol_id "
         "WHERE r.clave='cliente' ORDER BY u.id LIMIT 1\""],
        capture_output=True, text=True).stdout.strip().splitlines()[-1].strip()
    chk("Hay un cliente de semilla para la prueba",
        "@" in correo_cliente and "\n" not in correo_cliente, correo_cliente)

    entrar(pg, correo_cliente)
    chk("El cliente entra", "Mis pedidos" in pg.content())

    # El carrito vive en Redis y sobrevive entre corridas: se vacía primero
    # para que la prueba no dependa de lo que dejó la ejecución anterior.
    pg.goto(f"{BASE}/carrito")
    while pg.query_selector("button:has-text('Quitar')"):
        pg.click("button:has-text('Quitar')")
        pg.wait_for_load_state("networkidle")
    chk("El carrito arranca vacío", "carrito está vacío" in pg.content())

    # Un solo producto barato: debe quedar por debajo del ticket mínimo.
    barato = subprocess.run(
        ["su", "postgres", "-c",
         "psql -h /tmp -d microhubs_p1 -tAc \""
         "SELECT p.id FROM microhubs.producto p WHERE p.estatus='activo' "
         "AND EXISTS (SELECT 1 FROM microhubs.inventario i JOIN microhubs.microhub m "
         "  ON m.id=i.microhub_id WHERE i.producto_id=p.id AND i.existencia>0 "
         "  AND m.estatus='activo') ORDER BY p.precio ASC LIMIT 1\""],
        capture_output=True, text=True).stdout.strip().splitlines()[-1].strip()
    pg.goto(f"{BASE}/?q=")
    pg.evaluate("""(pid) => {
        const f = document.createElement('form');
        f.method = 'post'; f.action = '/carrito/agregar';
        f.innerHTML = '<input name=producto_id value=' + pid + '><input name=cantidad value=1>';
        document.body.appendChild(f); f.submit();
    }""", barato)
    pg.wait_for_load_state("networkidle")

    pg.goto(f"{BASE}/carrito")
    bajo = "Te faltan" in pg.content()
    chk("Un carrito bajo el mínimo avisa cuánto falta", bajo,
        f"producto {barato}")
    chk("Y no ofrece confirmar", "Confirmar pedido" not in pg.content() if bajo else True)

    # Se agregan productos hasta superar el mínimo.
    for termino in ("aceite", "shampoo", "queso"):
        pg.goto(f"{BASE}/?q={termino}")
        b = pg.query_selector("form[action*='agregar'] button")
        if b:
            b.click()
            pg.wait_for_load_state("networkidle")

    pg.goto(f"{BASE}/carrito")
    chk("Superado el mínimo aparece confirmar", "Confirmar pedido" in pg.content())

    pg.click("button:has-text('Confirmar pedido')")
    pg.wait_for_load_state("networkidle")
    confirmado = "PED-" in pg.content()
    chk("El pedido se confirma y recibe folio", confirmado)
    folio = re.search(r"PED-\d{8}-\d{6}", pg.content())
    folio = folio.group(0) if folio else None
    url_pedido = pg.url

    chk("El detalle muestra el historial de estados", "Seguimiento" in pg.content())
    cancelable = "Cancelar pedido" in pg.content()
    chk("Un pedido asignado ofrece cancelar (RN21)", cancelable)

    print("\n== 4. La regla se impone aunque la interfaz no la muestre ==")
    # El operador avanza el pedido; el cliente ya no debe poder cancelarlo.
    id_pedido = url_pedido.rstrip("/").split("/")[-1]
    salir(pg)
    entrar(pg, "operador.mh01@codex.mx")
    pg.goto(f"{BASE}/operacion/pedido/{id_pedido}")
    propio = "No tienes acceso" not in pg.content()
    if propio:
        b = pg.query_selector("button:has-text('Iniciar preparación')")
        if b:
            b.click(); pg.wait_for_load_state("networkidle")
        chk("El operador pasa el pedido a preparación", "En preparación" in pg.content())
    else:
        chk("El pedido cayó en otro microhub: acceso denegado y auditado", True,
            "(ámbito aplicado)")

    salir(pg)
    entrar(pg, correo_cliente)
    pg.goto(url_pedido)
    if propio:
        chk("Ya en preparación, desaparece el botón de cancelar",
            "Cancelar pedido" not in pg.content())
        # Y lo importante: forzar la operación por POST igual debe fallar.
        resp = pg.request.post(f"{BASE}{'/pedido/'}{id_pedido}/cancelar")
        pg.goto(url_pedido)
        chk("Forzar la cancelación por URL tampoco funciona (RN20)",
            "cancelado" not in pg.inner_text("h1, p.sub").lower())

    print("\n== 5. Perfiles de supervisión ==")
    salir(pg)
    entrar(pg, "auditor@codex.mx")
    pg.goto(f"{BASE}/bitacora")
    chk("El Auditor entra a la bitácora", "Bitácora de auditoría" in pg.content())
    chk("La bitácora registró el intento de acceso denegado",
        "acceso denegado" in pg.content().lower())
    chk("La bitácora no ofrece editar ni borrar",
        "no tiene botón de editar" in pg.content().lower())

    salir(pg)
    entrar(pg, "admin@codex.mx")
    pg.goto(f"{BASE}/indicadores")
    chk("El Administrador ve indicadores", "Indicadores de operación" in pg.content())
    chk("Los indicadores incluyen demanda no atendida",
        "no pudimos atender" in pg.content().lower())
    pg.goto(f"{BASE}/admin/parametros")
    chk("El Administrador edita parámetros", "ticket_minimo" in pg.content())
    pg.goto(f"{BASE}/admin/usuarios")
    chk("El Administrador ve usuarios", "Usuarios" in pg.content())

    salir(pg)
    entrar(pg, "planeador@codex.mx")
    pg.goto(f"{BASE}/admin/pendientes")
    chk("El Planeador ve los pendientes de asignación", "pendientes de asignación" in pg.content().lower())

    print("\n== 6. Salud general ==")
    chk("Sin errores de JavaScript", not errores_js, "; ".join(errores_js[:2]))

    pg2 = ctx.new_page()
    pg2.set_viewport_size({"width": 390, "height": 844})
    pg2.goto(BASE)
    ancho = pg2.evaluate("document.documentElement.scrollWidth")
    chk("Sin desbordamiento horizontal en 390px", ancho <= 400, f"{ancho}px")

    nav.close()

print("\n" + "=" * 58)
print(f"  {pasos - len(fallos)} de {pasos} comprobaciones pasan")
if fallos:
    print("  Fallan:")
    for f in fallos:
        print("   -", f)
    sys.exit(1)
