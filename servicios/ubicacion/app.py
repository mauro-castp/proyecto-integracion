"""
Servicio de ubicación de microhubs (facility location) · puerto 5127 · contrato v1

  GET  /api/v1/ubicacion/colonias            colonias de la zona de estudio con su grado de marginación CONAPO 2020
                                             (bajos_ingresos=1 solo Medio, Alto o Muy alto; contorno=1 agrega el polígono)
  GET  /api/v1/ubicacion/mapa                lo mismo en GeoJSON (FeatureCollection) para dibujar el mapa
  POST /api/v1/ubicacion/propuestas          dónde poner p microhubs: simulación de demanda + cobertura máxima + punto de equilibrio
  GET  /api/v1/ubicacion/supuestos           de dónde sale cada valor

Responsabilidad única: dónde conviene abrir microhubs para atender a las colonias de bajos ingresos. Es dueño de la tabla
colonia_marginacion (cargada de la cartografía oficial de CONAPO con bloque_c/scripts/importar_marginacion.py). Los microhubs
que ya existen los pide al servicio de microhubs solo para decir cuál queda más cerca de cada propuesta.

El cálculo está en comun/ubicacion_calc.py (funciones puras; el portal usa una copia idéntica).
"""
import json

from comun import config, ubicacion_calc as uc
from comun.base import crear_app, documentar, leer_cuerpo, requiere, responder
from comun.base_errores import filtro_invalido
from comun.clientes import mapa
from comun.datos import consultar
from comun.validar import Campo, validar
from flask import request

app = crear_app("ubicacion", "Microhubs · Ubicación (facility location)",
                "Dónde poner microhubs: colonias de bajos ingresos (CONAPO 2020), demanda simulada, cobertura máxima y punto de equilibrio.", 5127)
P = config.PREFIJO

SQL_COLONIAS = ("SELECT cve_col, colonia, codigo_postal, municipio, poblacion, indice_2020, grado_2020, sin_educacion_basica_pct, sin_salud_pct, "
                "hacinamiento_pct, sin_internet_pct, latitud, longitud{extra} FROM colonia_marginacion {donde} ORDER BY colonia, cve_col")


def _bool(nombre):
    v = (request.args.get(nombre) or "").strip().lower()
    if v in ("", "0", "false", "no"):
        return False
    if v in ("1", "true", "si", "sí"):
        return True
    raise filtro_invalido(nombre, f"{nombre} debe ser 1 o 0.")


def _colonias(bajos=False, contorno=False):
    donde = "WHERE grado_2020 IN ('Medio','Alto','Muy alto')" if bajos else ""
    return consultar(SQL_COLONIAS.format(extra=", contorno" if contorno else "", donde=donde))


def _item(f, contorno=False):
    d = {"cve_col": f["cve_col"], "colonia": f["colonia"], "codigo_postal": f["codigo_postal"], "municipio": f["municipio"],
         "poblacion": f["poblacion"], "indice_2020": float(f["indice_2020"]), "grado_2020": f["grado_2020"],
         "bajos_ingresos": f["grado_2020"] in uc.GRADOS_BAJOS_INGRESOS,
         "sin_educacion_basica_pct": float(f["sin_educacion_basica_pct"]), "sin_salud_pct": float(f["sin_salud_pct"]),
         "hacinamiento_pct": float(f["hacinamiento_pct"]), "sin_internet_pct": float(f["sin_internet_pct"]),
         "latitud": float(f["latitud"]), "longitud": float(f["longitud"])}
    if contorno:
        d["contorno"] = f["contorno"] if isinstance(f["contorno"], dict) else json.loads(f["contorno"])
    return d


@app.get(f"{P}/ubicacion/colonias")
@requiere("planeacion.ver")
def colonias():
    contorno = _bool("contorno")
    filas = [_item(f, contorno) for f in _colonias(_bool("bajos_ingresos"), contorno)]
    resumen = {g: sum(1 for x in filas if x["grado_2020"] == g) for g in ("Muy bajo", "Bajo", "Medio", "Alto", "Muy alto")}
    return responder({"datos": filas, "total": len(filas), "por_grado": resumen,
                      "fuente": "CONAPO, Índice de marginación urbana por colonia 2020"}, raiz="colonias_marginacion", items={"datos": "colonia"})


@app.get(f"{P}/ubicacion/mapa")
@requiere("planeacion.ver")
def mapa_geojson():
    rasgos = []
    for f in _colonias(_bool("bajos_ingresos"), True):
        it = _item(f, True)
        geo = it.pop("contorno")
        rasgos.append({"type": "Feature", "geometry": geo, "properties": it})
    return responder({"type": "FeatureCollection", "features": rasgos}, raiz="mapa", items={"features": "feature"})


def _microhubs_actuales():
    return [{"clave": m.get("clave"), "lat": float(m["latitud"]), "lng": float(m["longitud"])}
            for m in mapa("microhubs", "microhubs").values() if m.get("latitud") is not None]


@app.post(f"{P}/ubicacion/propuestas")
@requiere("planeacion.ver")
def propuestas():
    d = validar(leer_cuerpo("ubicacion_propuesta_nueva"), [
        Campo("p", "int", req=False, nulo=True, minimo=1, maximo=10),
        Campo("radio_km", "num", req=False, nulo=True, minimo=0.3, maximo=5),
        Campo("penetracion", "num", req=False, nulo=True, minimo=0.001, maximo=1),
        Campo("pedidos_semana_hogar", "num", req=False, nulo=True, minimo=0.1, maximo=14),
        Campo("capacidad_diaria", "int", req=False, nulo=True, minimo=1, maximo=5000),
        Campo("ticket", "num", req=False, nulo=True, minimo=1, maximo=100000),
        Campo("margen_bruto", "num", req=False, nulo=True, minimo=0.01, maximo=0.95),
        Campo("costo_entrega", "num", req=False, nulo=True, minimo=0, maximo=10000),
        Campo("costos_fijos_mes", "num", req=False, nulo=True, minimo=0, maximo=100000000),
        Campo("dias_simulados", "int", req=False, nulo=True, minimo=7, maximo=730),
        Campo("semilla", "int", req=False, nulo=True, minimo=0, maximo=2**31 - 1)])
    cols = [{"cve": f["cve_col"], "nombre": f["colonia"], "lat": float(f["latitud"]), "lng": float(f["longitud"]),
             "poblacion": f["poblacion"], "grado": f["grado_2020"]} for f in _colonias()]
    r = uc.proponer(cols, _microhubs_actuales(), d)
    return responder(r, raiz="ubicacion_propuesta", items={"propuestas": "propuesta", "colonias": "colonia", "pasos": "paso",
                                                           "indice_semanal": "indice"})


@app.get(f"{P}/ubicacion/supuestos")
@requiere("planeacion.ver")
def supuestos():
    datos = [
        {"clave": "bajos_ingresos", "valor": "Medio, Alto, Muy alto", "fuente": "CONAPO, índice de marginación urbana por colonia 2020",
         "nota": "Una colonia es de bajos ingresos si su grado de marginación es Medio o mayor."},
        {"clave": "personas_por_hogar", "valor": uc.PARAMS["personas_por_hogar"], "fuente": "INEGI, Censo 2020", "nota": "Hogares = población ÷ este valor."},
        {"clave": "penetracion", "valor": uc.PARAMS["penetracion"], "fuente": "Supuesto del equipo",
         "nota": "Se calibra con los pedidos reales; la propuesta da la penetración mínima para llegar al equilibrio."},
        {"clave": "pedidos_semana_hogar", "valor": uc.PARAMS["pedidos_semana_hogar"], "fuente": "Supuesto del equipo", "nota": "Compra de reposición de abarrotes."},
        {"clave": "radio_km", "valor": uc.PARAMS["radio_km"], "fuente": "RN05", "nota": "Radio de servicio de un microhub."},
        {"clave": "capacidad_diaria", "valor": uc.PARAMS["capacidad_diaria"], "fuente": "Servicio de capacidad", "nota": "Tope de pedidos al día por microhub."},
        {"clave": "costos_fijos_mes", "valor": uc.PARAMS["costos_fijos_mes"], "fuente": "Escenario base de costos",
         "nota": "Renta 18 000 + nómina 42 000 + servicios 7 000 + otros 5 000."},
    ]
    return responder({"datos": datos}, raiz="supuestos_ubicacion", items={"datos": "supuesto"})


documentar(app, "GET", f"{P}/ubicacion/colonias", "Colonias y marginación", permisos=["planeacion.ver"],
           descripcion="Colonias de San Bernabé y vecinas con el índice y grado de marginación urbana 2020 de CONAPO. bajos_ingresos=1 deja solo "
                       "las de grado Medio, Alto o Muy alto; contorno=1 agrega el polígono.", errores=[400, 401, 403])
documentar(app, "GET", f"{P}/ubicacion/mapa", "Mapa de marginación (GeoJSON)", permisos=["planeacion.ver"],
           descripcion="Las mismas colonias como FeatureCollection GeoJSON para dibujarlas en un mapa.", errores=[400, 401, 403])
documentar(app, "POST", f"{P}/ubicacion/propuestas", "Dónde poner los microhubs", permisos=["planeacion.ver"],
           descripcion="Integra simulación de demanda (Monte Carlo, Poisson por colonia), facility location (cobertura máxima con p microhubs: "
                       "voraz + intercambio de Teitz y Bart) y punto de equilibrio de cada propuesta. Solo colonias de bajos ingresos son demanda. "
                       "Todos los campos son opcionales y reemplazan los supuestos. No guarda nada; con la misma semilla da el mismo resultado.",
           errores=[400, 401, 403, 422])
documentar(app, "GET", f"{P}/ubicacion/supuestos", "Supuestos de ubicación", permisos=["planeacion.ver"], errores=[401, 403])
