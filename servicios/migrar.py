"""
migrar.py — Aplica 06, 07 y 08 a una base que ya existía.

PostgreSQL solo ejecuta /docker-entrypoint-initdb.d al crear el volumen. Con
un volumen existente (por ejemplo, el del Primer Parcial), este paso agrega
lo de planeación (06), web ampliado (07) y microservicios (08) sin borrar
datos. Los tres scripts son idempotentes. docker-compose.integrado.yml lo
corre una vez antes de levantar el web y los servicios.
"""
import os
import sys
import time
from pathlib import Path

import psycopg

DSN = os.environ.get("PG_DSN", "host=127.0.0.1 port=5432 dbname=microhubs_p1 user=postgres password=microhubs_dev")
CARPETA = Path(os.environ.get("SQL_DIR", "/app/sql"))
SCRIPTS = ["06_planeacion.sql", "07_web_ampliado.sql", "08_microservicios.sql"]


def main():
    for intento in range(1, 31):
        try:
            with psycopg.connect(DSN, autocommit=True) as con:
                if not con.execute("SELECT to_regclass('microhubs.zona') IS NOT NULL").fetchone()[0]:
                    print("migrar: el esquema base aún no existe (initdb en curso); se reintenta.")
                    time.sleep(2)
                    continue
                for nombre in SCRIPTS:
                    con.execute((CARPETA / nombre).read_text(encoding="utf-8"))
                    print(f"migrar: {nombre} aplicado.")
                return 0
        except psycopg.OperationalError as e:
            print(f"migrar: esperando PostgreSQL ({intento}/30): {e}", file=sys.stderr)
            time.sleep(2)
    print("migrar: PostgreSQL no respondió.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
