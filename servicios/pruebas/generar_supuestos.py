"""
generar_supuestos.py — Escribe servicios/SUPUESTOS.md a partir de la base de datos y del código.

Cada modelo de la Ola 2 descansa en supuestos. El valor vive en la tabla `configuracion` (RN40: ninguno es una constante en el código) y
`supuesto_documentado` dice de dónde sale, si es medido, supuesto o normativo, y cómo se corrige con datos reales. Este script junta
las dos tablas con la lista de servicios que usa cada clave, para que el documento no pueda quedar distinto de lo que corre.

  cd servicios && python pruebas/generar_supuestos.py            (PG_DSN en el entorno)
"""
import importlib
import os
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
os.environ.setdefault("LOG_STDOUT", "0")
os.environ.setdefault("SIM_TRABAJADOR", "0")

from comun import datos as bd  # noqa: E402

SERVICIOS = [("demanda", "Demanda"), ("cobertura", "Cobertura"), ("capacidad", "Capacidad"), ("rutas", "Rutas"), ("costos", "Costos"),
             ("punto-equilibrio", "Punto de equilibrio"), ("simulacion", "Simulación"), ("surtido", "Surtido")]
ORIGEN = {"medido": "Sale de datos reales del sistema", "supuesto": "Es un valor razonable que aún no se ha medido",
          "normativo": "Lo fija el equipo o es una convención; no se estima"}


def celda(texto):
    return (texto or "").replace("|", "/").replace("\n", " ")


def main():
    uso = {}
    for servicio, _ in SERVICIOS:
        m = importlib.import_module(f"{servicio.replace('-', '_')}.app")
        for clave in m.CLAVES_SUPUESTOS:
            uso.setdefault(clave, []).append(servicio)
    filas = bd.consultar("SELECT c.clave, c.valor, c.unidad, d.servicio, d.origen, d.justificacion, d.como_calibrar FROM configuracion c "
                         "JOIN supuesto_documentado d ON d.clave = c.clave WHERE c.ambito = 'global' ORDER BY d.servicio, c.clave")
    por_servicio = {}
    for f in filas:
        por_servicio.setdefault(f["servicio"], []).append(f)
    total = len(filas)
    conteo = {o: sum(1 for f in filas if f["origen"] == o) for o in ORIGEN}
    out = ["# Supuestos de los modelos de la Ola 2", "",
           "Lo escribe `servicios/pruebas/generar_supuestos.py` a partir de las tablas `configuracion` y `supuesto_documentado`; no se edita a mano. "
           f"Generado el {time.strftime('%Y-%m-%d')}.", "",
           "## Cómo se manejan", "",
           "- **El valor vive en la base de datos**, en `configuracion` (RN40). Ningún peso, umbral ni productividad es una constante del código: el código solo "
           "trae un valor de respaldo para no caerse si una clave se borra. Cambiar un valor no requiere recompilar ni reiniciar.",
           "- **Cada supuesto dice de dónde sale y cómo se corrige.** `supuesto_documentado` guarda el origen (medido, supuesto o normativo), la justificación y "
           "el dato real con el que habría que calibrarlo. Cada servicio lo publica en `GET /api/v1/<servicio>/supuestos`.",
           "- **Cada resultado dice qué supuestos usó.** Las respuestas de los modelos traen `supuestos_usados` con la clave, el valor y si la petición lo cambió. "
           "Un dato que el usuario escribe a mano sustituye al que vendría de otro servicio, y la respuesta lo marca (`origen: manual`).",
           "- **Las conclusiones se prueban contra otros valores.** [`evidencias/ola2/escenarios.md`](../evidencias/ola2/escenarios.md) cambia un supuesto a la vez y "
           "muestra si la decisión cambia; lo corre `servicios/pruebas/escenarios_ola2.py`.", "",
           "## Qué quiere decir cada origen", "", *[f"- **{k}.** {v}." for k, v in ORIGEN.items()], "",
           f"Hoy hay {total} supuestos documentados: {conteo['medido']} medidos, {conteo['supuesto']} supuestos y {conteo['normativo']} normativos. "
           "Ninguno es «medido» todavía porque la operación real es chica (pocos pedidos); cada fila dice con qué dato real se mediría. "
           "Hasta entonces las decisiones de viabilidad deben leerse como «con estos supuestos», no como una predicción.", ""]
    for servicio, titulo in SERVICIOS:
        filas_s = por_servicio.get(servicio, [])
        out += [f"## {titulo} (`{servicio}`)", "", "| Clave | Valor | Origen | De dónde sale | Cómo se calibra | La usan |", "|---|---|---|---|---|---|"]
        for f in filas_s:
            valor = f"{f['valor']} {f['unidad'] or ''}".strip()
            out.append(f"| `{f['clave']}` | {valor} | {f['origen']} | {celda(f['justificacion'])} | {celda(f['como_calibrar'])} | {', '.join(uso.get(f['clave'], ['—']))} |")
        out.append("")
    out += ["## Dos valores que se parecen", "",
            "`costo_km_reparto` y `costo_base_entrega` los usan **rutas y cobertura** (costo del recorrido y de la última milla). El servicio de **costos** "
            "no los lee: guarda sus propios conceptos («Combustible y desgaste», «Pago base al repartidor») con vigencia, fuente y justificación. Hoy valen "
            "lo mismo (4.50 y 18.00), pero son dos lugares: si se corrige uno hay que corregir el otro. Se dejó así porque rutas la usan operadores, que "
            "no tienen permiso de costos, y el servicio de costos no puede responder con el JWT de ellos. Queda anotado como deuda técnica.", "",
            "## Datos sintéticos", "",
            "La historia de demanda de la demostración (60 días por zona) la genera `10_ola2_analitica.sql` con una fórmula determinista y está marcada "
            "`fuente = sintetica` en cada renglón (`GET /demanda/observaciones`) y contada aparte en `GET /demanda/resumen`. No son ventas reales. "
            "`POST /demanda/sincronizacion` la reemplaza por lo real, rango por rango, cuando haya pedidos suficientes. "
            "La población de cada zona (`cobertura_zona_dato`) es una estimación del equipo hasta que se capture el dato de INEGI con `PUT /cobertura/zonas/{id}/poblacion`.", ""]
    destino = AQUI.parent / "SUPUESTOS.md"
    destino.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\r\n")
    print(f"{total} supuestos documentados en {destino}")


if __name__ == "__main__":
    main()
