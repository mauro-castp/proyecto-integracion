"""
importar_marginacion.py — Genera bloque_c/sql/18_marginacion_colonias.sql con las colonias de la zona de estudio (San Bernabé,
Monterrey) y su grado de marginación urbana 2020 de CONAPO.

Fuente oficial: CONAPO, «Cartografía digital (shp) del índice de marginación urbana por colonia 2020»
https://www.gob.mx/conapo/documentos/indices-de-marginacion-2020-284372  (archivo imc2020_shp.zip, no se sube al repositorio).

Uso:  python bloque_c/scripts/importar_marginacion.py <carpeta_con_colonias_imc2020.shp>
Requiere: pip install pyshp pyproj

Qué hace:
  1. Lee las 74 226 colonias del país y se queda con las de Nuevo León cuyo centro cae en el rectángulo de estudio
     (latitud 25.728 a 25.778, longitud −100.400 a −100.335: San Bernabé y colonias vecinas).
  2. Convierte las coordenadas de la proyección de CONAPO (EPSG:6372, Lambert de México) a latitud y longitud (EPSG:4326).
  3. Guarda por colonia: clave, nombre, código postal, municipio, población, el índice y el grado de marginación y cuatro indicadores
     del índice (sin educación básica, sin servicios de salud, hacinamiento y sin internet), su centro y su contorno simplificado.
"""
import json
import sys

import shapefile
from pyproj import Transformer

CAJA = (25.728, 25.778, -100.400, -100.335)          # lat_min, lat_max, lng_min, lng_max
SALIDA = "bloque_c/sql/18_marginacion_colonias.sql"


def centro(puntos):
    """Centroide de un polígono (fórmula del área con signo); si el área es cero, promedio de vértices."""
    a = cx = cy = 0.0
    for (x1, y1), (x2, y2) in zip(puntos, puntos[1:] + puntos[:1]):
        f = x1 * y2 - x2 * y1
        a += f; cx += (x1 + x2) * f; cy += (y1 + y2) * f
    if abs(a) < 1e-12:
        return sum(p[0] for p in puntos) / len(puntos), sum(p[1] for p in puntos) / len(puntos)
    return cx / (3 * a), cy / (3 * a)


def texto(v):
    return "NULL" if v is None else "'" + str(v).replace("'", "''") + "'"


def main(carpeta):
    t = Transformer.from_crs("EPSG:6372", "EPSG:4326", always_xy=True)
    r = shapefile.Reader(f"{carpeta}/colonias_imc2020")
    filas = []
    for sr in r.iterShapeRecords():
        d = sr.record.as_dict()
        if d["CVE_ENT"] != "19" or not sr.shape.points:
            continue
        partes = list(sr.shape.parts) + [len(sr.shape.points)]
        anillos = [sr.shape.points[partes[i]:partes[i + 1]] for i in range(len(partes) - 1)]
        mayor = max(anillos, key=len)
        lng, lat = t.transform(*centro(mayor))
        if not (CAJA[0] <= lat <= CAJA[1] and CAJA[2] <= lng <= CAJA[3]):
            continue
        poligonos = [[[round(c, 5) for c in t.transform(x, y)] for x, y in anillo] for anillo in anillos]
        geometria = {"type": "MultiPolygon", "coordinates": [[p] for p in poligonos]}
        filas.append((d["CVE_COL"], d["COLONIA"], d["CP"], d["NOM_MUN"], round(d["POBTOT"] or 0), d["IM_2020"], d["GM_2020"],
                      d["SBASC"], d["PSDSS"], d["OVHAC"], d["OVSINT"], round(lat, 6), round(lng, 6), json.dumps(geometria, separators=(",", ":"))))
    filas.sort()
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write("-- 18_marginacion_colonias.sql — GENERADO por bloque_c/scripts/importar_marginacion.py (no editar a mano).\n"
                "-- Colonias de San Bernabé y vecinas con su índice y grado de marginación urbana 2020 (CONAPO).\n"
                "-- Fuente: https://www.gob.mx/conapo/documentos/indices-de-marginacion-2020-284372\n\n"
                "CREATE TABLE IF NOT EXISTS colonia_marginacion (\n"
                "    cve_col        varchar(20)  PRIMARY KEY,\n    colonia        varchar(160) NOT NULL,\n    codigo_postal  char(5),\n"
                "    municipio      varchar(80)  NOT NULL,\n    poblacion      integer      NOT NULL CHECK (poblacion >= 0),\n"
                "    indice_2020    numeric(10,4),\n    grado_2020     varchar(12)  NOT NULL\n"
                "                   CHECK (grado_2020 IN ('Muy bajo','Bajo','Medio','Alto','Muy alto')),\n"
                "    sin_educacion_basica_pct numeric(6,2), sin_salud_pct numeric(6,2), hacinamiento_pct numeric(6,2), sin_internet_pct numeric(6,2),\n"
                "    latitud        numeric(9,6) NOT NULL,\n    longitud       numeric(9,6) NOT NULL,\n    contorno       jsonb        NOT NULL\n);\n"
                "COMMENT ON TABLE colonia_marginacion IS 'Colonias de la zona de estudio con el índice de marginación urbana 2020 de CONAPO. "
                "Bajos ingresos = grado Medio, Alto o Muy alto.';\n\n")
        f.write("INSERT INTO colonia_marginacion (cve_col, colonia, codigo_postal, municipio, poblacion, indice_2020, grado_2020, "
                "sin_educacion_basica_pct, sin_salud_pct, hacinamiento_pct, sin_internet_pct, latitud, longitud, contorno) VALUES\n")
        f.write(",\n".join("(" + ", ".join([texto(x[0]), texto(x[1]), texto(x[2]), texto(x[3]), str(x[4]), f"{x[5]:.4f}", texto(x[6]),
                                            f"{x[7]:.2f}", f"{x[8]:.2f}", f"{x[9]:.2f}", f"{x[10]:.2f}", str(x[11]), str(x[12]),
                                            texto(x[13]) + "::jsonb"]) + ")" for x in filas))
        f.write("\nON CONFLICT (cve_col) DO NOTHING;\n")
    print(f"{len(filas)} colonias → {SALIDA}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "datos_conapo")
