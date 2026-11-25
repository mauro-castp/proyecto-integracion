"""
generar_inventario.py — Escribe servicios/INVENTARIO_ENDPOINTS.md a partir del código.

Recorre las rutas de cada servicio (Flask) y, por cada operación, busca los casos de petición y respuesta
de la corrida de evidencias (evidencias.json y complementarias/evidencias.json) que la ejercitan. Así el
inventario no se escribe a mano: si una ruta no tiene caso de evidencia, la columna sale vacía y se nota.

  cd servicios && python pruebas/generar_inventario.py [carpeta de la corrida, por omisión evidencias/ola2]
"""
import importlib
import json
import os
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI.parent))
os.environ.setdefault("LOG_STDOUT", "0")

from comun import config  # noqa: E402

OMITIR = ("/salud", "/health", "/docs", "/openapi.json")


def operaciones(app):
    """[(método, regla)] de negocio, en el orden en que se registraron."""
    vistas = []
    for r in app.url_map.iter_rules():
        if not r.rule.startswith(config.PREFIJO + "/") or r.rule.endswith(OMITIR):
            continue
        for m in sorted(r.methods - {"HEAD", "OPTIONS"}, key=["GET", "POST", "PATCH", "PUT", "DELETE"].index):
            vistas.append((m, r.rule))
    return vistas


def casos_de(ruta_json):
    p = Path(ruta_json)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def main():
    corrida = RAIZ / (sys.argv[1] if len(sys.argv) > 1 else "evidencias/ola2")
    casos = casos_de(corrida / "evidencias.json") + casos_de(corrida / "complementarias" / "evidencias.json")
    filas, total = [], 0
    for servicio in sorted(config.PUERTOS):
        app = importlib.import_module(f"{servicio.replace('-', '_')}.app").app
        enlace = app.url_map.bind("localhost")
        por_operacion = {}
        for c in casos:
            if c["servicio"] != servicio or "url" not in c:
                continue
            ruta = "/" + c["url"].split("/", 3)[3].split("?")[0] if "/api/v1/" in c["url"] else None
            if not ruta:
                continue
            try:
                regla, _ = enlace.match(ruta, method=c["metodo"], return_rule=True)
            except Exception:
                continue
            por_operacion.setdefault((c["metodo"], regla.rule), []).append(c["id"])
        for metodo, regla in operaciones(app):
            ids = por_operacion.get((metodo, regla), [])
            texto = ", ".join(ids) if len(ids) <= 5 else ", ".join(ids[:5]) + f" y {len(ids) - 5} más"
            filas.append(f"| {servicio} | {metodo} | `{regla}` | {texto} |")
            total += 1
    sin_caso = [f for f in filas if f.endswith("|  |")]
    salida = ["# Inventario vigente de microservicios", "", "Fuente: servicios/*/app.py y docker-compose.integrado.yml.", "",
              f"{total} pares método HTTP y ruta de negocio. Excluye salud, OpenAPI, Swagger, HEAD y OPTIONS.", "",
              f"La última columna indica los casos de petición y respuesta que ejercitan cada operación: la corrida principal "
              f"(`{corrida.relative_to(RAIZ).as_posix()}/`) y la complementaria (`{corrida.relative_to(RAIZ).as_posix()}/complementarias/`). "
              "Este archivo lo escribe `servicios/pruebas/generar_inventario.py` a partir del código y de esos casos.", "",
              "| Servicio | Método | Ruta | Casos de evidencia |", "|---|---|---|---|", *filas, "",
              "## Contratos y compatibilidad", "",
              "Productos, Zonas y Microhubs conservan catalogos.xsd. Seguimiento utiliza estructuras de entregas.xsd. "
              "Inventario, Precios, Proveedores, Abastecimiento y Notificaciones (Ola 1) y Demanda, Cobertura, Capacidad, Rutas, Costos, "
              "Punto de equilibrio, Simulación y Surtido (Ola 2) tienen su propio XSD, generado con `servicios/contratos/generar.py` a partir de "
              "`contratos/ola1.py` y `contratos/ola2.py`; las referencias que comparten están en comun_ola1.xsd y comun_ola2.xsd. Lo que pedidos, "
              "entregas e inventario ganaron en la Ola 2 (resumen, ventas, listos, repartidores, quiebres) está en pedidos_ola2.xsd, "
              "entregas_ola2.xsd e inventario_ola2.xsd.", "",
              "La ruta GPS antigua bajo entregas ya no se ofrece. El puerto 5108 corresponde a Zonas y el 5124 a Notificaciones, "
              "que vuelve como servicio de la Ola 1 con su propia bandeja, envío por rol y preferencias.", ""]
    (AQUI.parent / "INVENTARIO_ENDPOINTS.md").write_text("\n".join(salida), encoding="utf-8", newline="\r\n")
    print(f"{total} operaciones; {len(sin_caso)} sin caso de evidencia")
    for f in sin_caso:
        print("  sin caso:", f)


if __name__ == "__main__":
    main()
