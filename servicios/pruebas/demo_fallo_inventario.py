"""
demo_fallo_inventario.py — Qué pasa con una recepción de mercancía cuando el servicio de inventario se cae.

Usa los contenedores reales de docker-compose.integrado.yml: apaga el contenedor de inventario, recibe mercancía
en abastecimiento, lo vuelve a encender y reintenta. Escribe el recorrido (peticiones, respuestas y existencias)
en un archivo Markdown.

  python servicios/pruebas/demo_fallo_inventario.py [salida.md]      (desde la raíz del repositorio, con el sistema arriba)
"""
import json
import math
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from decimal import Decimal
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
COMPOSE = ["docker", "compose", "-f", str(RAIZ / "docker-compose.integrado.yml")]
PUERTOS = {"auth": 5101, "inventario": 5111, "proveedores": 5113, "abastecimiento": 5114, "productos": 5103}
CLAVE = os.environ.get("MICROHUBS_CLAVE", "Codex#2026")
SALIDA = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "evidencias" / "ola1" / "fallo_inventario.md"
informe = []


def http(servicio, metodo, ruta, cuerpo=None, token=None):
    enc = {"Accept": "application/json", "X-Traza-Id": str(uuid.uuid4())}
    datos = None
    if token:
        enc["Authorization"] = "Bearer " + token
    if cuerpo is not None:
        datos, enc["Content-Type"] = json.dumps(cuerpo).encode(), "application/json"
    req = urllib.request.Request(f"http://localhost:{PUERTOS[servicio]}/api/v1/{ruta}", data=datos, headers=enc, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"null")


def mostrar(titulo, metodo, servicio, ruta, cuerpo, status, respuesta):
    informe.append(f"### {titulo}\n\n`{metodo} :{PUERTOS[servicio]}/api/v1/{ruta}` → **HTTP {status}**\n")
    if cuerpo is not None:
        informe.append("```json\n" + json.dumps(cuerpo, ensure_ascii=False, indent=2) + "\n```\n")
    informe.append("```json\n" + json.dumps(respuesta, ensure_ascii=False, indent=2)[:2500] + "\n```\n")


def paso(titulo, servicio, metodo, ruta, cuerpo=None, token=None, esperado=None):
    status, r = http(servicio, metodo, ruta, cuerpo, token)
    mostrar(titulo, metodo, servicio, ruta, cuerpo, status, r)
    if esperado is not None and status != esperado:
        raise SystemExit(f"{titulo}: se esperaba {esperado} y llegó {status}: {r}")
    return r


def entrar(correo):
    return http("auth", "POST", "auth/login", {"correo": correo, "clave": CLAVE, "dispositivo": "demo"})[1]["token_acceso"]


def esperar_salud(servicio, segundos=60):
    fin = time.time() + segundos
    while time.time() < fin:
        try:
            if http(servicio, "GET", "salud")[0] == 200:
                return True
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(1)
    return False


def main():
    t_adm, t_op = entrar("admin@codex.mx"), entrar("operador.mh01@codex.mx")
    productos = http("productos", "GET", "productos?q=AB-016", token=t_adm)[1]["datos"]
    prod = productos[0]
    unitario = Decimal(str(prod["precio"])) * Decimal("0.70")
    cantidad = max(12, math.ceil(Decimal(850) / unitario))
    pv01 = next(p for p in http("proveedores", "GET", "proveedores?q=PV-01", token=t_adm)[1]["datos"])["id"]
    informe.append("# Qué pasa si inventario se cae durante una recepción\n")
    informe.append(f"Producto: {prod['nombre']} (id {prod['id']}). Se piden {cantidad} piezas al proveedor PV-01. "
                   "Los contenedores son los de `docker-compose.integrado.yml`; el de inventario se apaga con `docker compose stop inventario`.\n")

    sol = paso("1. El operador pide la mercancía", "abastecimiento", "POST", "abastecimiento/solicitudes",
               {"microhub_id": 1, "motivo": "Demostración de fallo", "lineas": [{"producto_id": prod["id"], "cantidad": cantidad}]}, t_op, 201)
    paso("2. El administrador aprueba", "abastecimiento", "POST", f"abastecimiento/solicitudes/{sol['id']}/decision",
         {"decision": "aprobada", "motivo": "Hay presupuesto"}, t_adm, 200)
    oc = paso("3. Se emite la orden de compra", "abastecimiento", "POST", f"abastecimiento/solicitudes/{sol['id']}/ordenar",
              {"proveedor_id": pv01}, t_adm, 201)["ordenes"][0]
    antes = http("inventario", "GET", f"inventario/1/{prod['id']}", token=t_adm)[1]["existencia"]
    informe.append(f"Existencia en el microhub 1 antes de recibir: **{antes}**.\n")

    informe.append("## Se apaga inventario\n")
    subprocess.run(COMPOSE + ["stop", "inventario"], check=True, capture_output=True)
    try:
        r = paso("4. Llega la mercancía y inventario no responde", "abastecimiento", "POST", f"abastecimiento/ordenes/{oc['id']}/recepcion",
                 {"nota": "Llegó con inventario caído", "lineas": [{"producto_id": prod["id"], "cantidad": cantidad}]}, t_op, 202)
        assert r["pendientes"] == 1 and r["aplicadas"] == 0
        informe.append("La recepción se guardó, pero la entrada a inventario quedó **pendiente** (`pendiente_inventario` en la línea). "
                       "La respuesta es 202, no un error: la mercancía llegó y el sistema lo recuerda.\n")
        paso("5. El tablero cuenta lo pendiente", "abastecimiento", "GET", "abastecimiento/seguimiento", None, t_op, 200)
    finally:
        informe.append("## Se vuelve a encender inventario\n")
        subprocess.run(COMPOSE + ["start", "inventario"], check=True, capture_output=True)
    if not esperar_salud("inventario"):
        raise SystemExit("inventario no volvió a responder")

    r = paso("6. Se reintenta la recepción (mismo POST, sin líneas)", "abastecimiento", "POST", f"abastecimiento/ordenes/{oc['id']}/recepcion",
             {}, t_op, 201)
    assert (r["aplicadas"], r["pendientes"], r["orden"]["estado"]) == (1, 0, "recibida")
    despues = http("inventario", "GET", f"inventario/1/{prod['id']}", token=t_adm)[1]["existencia"]
    informe.append(f"Existencia después: **{despues}** (antes {antes} + {cantidad} recibidas = {antes + cantidad}).\n")
    assert despues == antes + cantidad
    r = paso("7. Un segundo reintento no vuelve a sumar", "abastecimiento", "POST", f"abastecimiento/ordenes/{oc['id']}/recepcion", {}, t_op, 201)
    assert r["aplicadas"] == 0
    final = http("inventario", "GET", f"inventario/1/{prod['id']}", token=t_adm)[1]["existencia"]
    informe.append(f"Existencia al final: **{final}**. La entrada entró una sola vez gracias a la `operacion_uuid` de la línea.\n")
    assert final == antes + cantidad
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text("\n".join(informe), encoding="utf-8", newline="\n")
    print(f"Listo: {SALIDA}")


if __name__ == "__main__":
    main()
