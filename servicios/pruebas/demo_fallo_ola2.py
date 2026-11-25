"""
demo_fallo_ola2.py — Qué pasa con el análisis cuando un servicio del que depende se cae.

Usa los contenedores reales de docker-compose.integrado.yml. Apaga costos (del que depende el punto de equilibrio y la simulación de un
microhub) y después demanda (del que sale el patrón semanal de la simulación), y en cada caso muestra:

  · lo que deja de funcionar y cómo lo dice (503 con el motivo, sin guardar nada a medias),
  · lo que sigue funcionando porque no depende de ese servicio (capacidad, cobertura y todo cálculo con los datos escritos),
  · que al volver el servicio todo responde otra vez sin tocar nada.

  python servicios/pruebas/demo_fallo_ola2.py [salida.md]      (desde la raíz del repositorio, con el sistema arriba)
"""
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
COMPOSE = ["docker", "compose", "-f", str(RAIZ / "docker-compose.integrado.yml")]
PUERTOS = {"auth": 5101, "demanda": 5115, "capacidad": 5117, "costos": 5119, "punto-equilibrio": 5120, "simulacion": 5121, "cobertura": 5116}
CLAVE = os.environ.get("MICROHUBS_CLAVE", "Codex#2026")
SALIDA = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "evidencias" / "ola2" / "fallo_servicios.md"
informe = []
ESCENARIO_A = {"pedidos_dia": 45, "ticket": 135, "margen_bruto": 0.28, "costos_fijos": 60000, "costo_variable_pedido": 32.6}


def http(servicio, metodo, ruta, cuerpo=None, token=None):
    enc = {"Accept": "application/json", "X-Traza-Id": str(uuid.uuid4())}
    datos = None
    if token:
        enc["Authorization"] = "Bearer " + token
    if cuerpo is not None:
        datos, enc["Content-Type"] = json.dumps(cuerpo).encode(), "application/json"
    req = urllib.request.Request(f"http://localhost:{PUERTOS[servicio]}/api/v1/{ruta}", data=datos, headers=enc, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"null")


def breve(r):
    """Resumen corto de una respuesta para el informe."""
    if isinstance(r, dict) and "error" in r:
        e = r["error"]
        return f"{e['codigo']}: {e['mensaje']}"
    if isinstance(r, dict):
        for clave in ("decision", "estado", "nivel", "pct_hogares"):
            if clave in r:
                return f"{clave} = {r[clave]}"
    return "ok"


def paso(titulo, servicio, metodo, ruta, cuerpo=None, token=None, esperado=200, mostrar=None):
    status, r = http(servicio, metodo, ruta, cuerpo, token)
    informe.append(f"| {titulo} | `{metodo} :{PUERTOS[servicio]}/api/v1/{ruta}` | **{status}** | {mostrar(r) if mostrar else breve(r)} |")
    if status != esperado:
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


def terminar(eid, token):
    for _ in range(60):
        r = http("simulacion", "GET", f"simulacion/ejecuciones/{eid}", token=token)[1]
        if r["estado"] in ("terminada", "fallida", "cancelada"):
            return r
        time.sleep(0.5)
    return r


def cabecera():
    informe.append("| Paso | Petición | HTTP | Resultado |")
    informe.append("|---|---|---|---|")


def apagar(servicio):
    subprocess.run(COMPOSE + ["stop", servicio], check=True, capture_output=True)


def encender(servicio):
    subprocess.run(COMPOSE + ["start", servicio], check=True, capture_output=True)
    if not esperar_salud(servicio):
        raise SystemExit(f"{servicio} no volvió a responder")


def total_ejecuciones(token):
    return http("simulacion", "GET", "simulacion/ejecuciones?por_pagina=1", token=token)[1]["paginacion"]["total"]


def main():
    t = entrar("planeador@codex.mx")
    informe.append("# Qué pasa con el análisis cuando se cae un servicio\n")
    informe.append("Los contenedores son los de `docker-compose.integrado.yml`. Cada servicio se apaga con `docker compose stop <servicio>` y se vuelve a encender con "
                   "`docker compose start <servicio>`. Los modelos piden sus datos a otros servicios con el JWT de quien consulta; si uno no responde, el modelo "
                   "dice cuál faltó y no guarda nada a medias.\n")

    informe.append("## 1. Se cae costos\n")
    informe.append("El punto de equilibrio de un microhub y la simulación de un microhub necesitan los costos fijos y variables; los cálculos con todos los datos "
                   "escritos y los servicios que no usan costos no se enteran.\n")
    cabecera()
    paso("Antes: equilibrio del microhub 1", "punto-equilibrio", "POST", "punto-equilibrio/calculos", {"microhub_id": 1}, t)
    antes = total_ejecuciones(t)
    apagar("costos")
    try:
        paso("Equilibrio del microhub 1 con costos caído", "punto-equilibrio", "POST", "punto-equilibrio/calculos", {"microhub_id": 1}, t, 503)
        paso("Simulación del microhub 1 con costos caído", "simulacion", "POST", "simulacion/ejecuciones", {"microhub_id": 1, "dias": 7, "replicas": 20}, t, 503)
        despues = total_ejecuciones(t)
        informe.append(f"| La simulación fallida no dejó nada en la cola | `GET :5121/api/v1/simulacion/ejecuciones` | **200** | ejecuciones antes {antes}, después {despues} |")
        assert despues == antes, "la simulación fallida dejó una ejecución"
        paso("Equilibrio con todos los datos escritos (escenario A)", "punto-equilibrio", "POST", "punto-equilibrio/calculos", ESCENARIO_A, t)
        manual = paso("Simulación con todos los datos escritos", "simulacion", "POST", "simulacion/ejecuciones",
                      {**ESCENARIO_A, "costos_fijos": 60000, "operadores": 3, "repartidores": 2, "dias": 7, "replicas": 40, "semilla": 5}, t, 202)
        fin = terminar(manual["id"], t)
        informe.append(f"| …y termina | `GET :5121/api/v1/simulacion/ejecuciones/{{id}}` | **200** | estado = {fin['estado']}, probabilidad de pérdida {fin['resultados']['prob_perdida_pct']} % |")
        assert fin["estado"] == "terminada"
        paso("Capacidad del microhub 1 (no usa costos)", "capacidad", "GET", "capacidad/microhubs/1?carga_dia=60", None, t)
        paso("Cobertura de la red (no usa costos)", "cobertura", "GET", "cobertura/resumen", None, t)
    finally:
        encender("costos")
    informe.append("\nSe vuelve a encender costos, sin tocar nada más:\n")
    cabecera()
    paso("Equilibrio del microhub 1", "punto-equilibrio", "POST", "punto-equilibrio/calculos", {"microhub_id": 1}, t)
    paso("Simulación del microhub 1", "simulacion", "POST", "simulacion/ejecuciones", {"microhub_id": 1, "dias": 7, "replicas": 20}, t, 202)

    informe.append("\n## 2. Se cae demanda\n")
    informe.append("La simulación saca de demanda el patrón de la semana (qué día se pide más). Si demanda no responde y se escribieron los datos del escenario, "
                   "la simulación sigue con un patrón plano y lo deja anotado en la entrada de la ejecución (`origen_de_datos.indice_semanal`); un microhub, "
                   "que necesita la demanda para saber cuántos pedidos esperar, responde 503.\n")
    cabecera()
    apagar("demanda")
    try:
        paso("Equilibrio del microhub 1 con demanda caído", "punto-equilibrio", "POST", "punto-equilibrio/calculos", {"microhub_id": 1}, t, 503)
        e = paso("Simulación con datos escritos y demanda caído", "simulacion", "POST", "simulacion/ejecuciones",
                 {**ESCENARIO_A, "operadores": 3, "repartidores": 2, "dias": 7, "replicas": 40, "semilla": 5}, t, 202)
        origen = {x["dato"]: x["fuente"] for x in e["entrada"]["origen_de_datos"]}["indice_semanal"]
        informe.append(f"| La entrada anota de dónde salió el patrón semanal | `GET :5121/api/v1/simulacion/ejecuciones/{{id}}` | **202** | indice_semanal = {origen}; "
                       f"índice = {e['entrada']['indice_semanal']} |")
        assert origen == "plano_sin_servicio"
        terminar(e["id"], t)
    finally:
        encender("demanda")
    paso("Demanda vuelve: proyección", "demanda", "GET", "demanda/proyeccion?horizonte=3", None, t)
    informe.append("\nTodas las ejecuciones de la demostración se pueden borrar de `simulacion_ejecucion`; no son datos de negocio.\n")
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text("\n".join(informe), encoding="utf-8", newline="\n")
    print(f"Listo: {SALIDA}")


if __name__ == "__main__":
    main()
