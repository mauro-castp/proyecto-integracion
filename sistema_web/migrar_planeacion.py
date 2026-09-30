"""
migrar_planeacion.py — Aplica 06_planeacion.sql a una base ya inicializada.

PostgreSQL solo ejecuta los scripts de /docker-entrypoint-initdb.d la primera
vez que crea el volumen. Cuando el volumen ya existe, este script agrega las
tablas y parámetros de Planeación sin borrar pedidos ni usuarios. Es
idempotente: puede correr en cada arranque.
"""
import os
import sys
import time
from pathlib import Path

import psycopg

DSN = os.environ.get("PG_DSN", "host=127.0.0.1 port=5432 dbname=microhubs_p1 user=postgres password=microhubs_dev")
CANDIDATOS = [Path(__file__).with_name("06_planeacion.sql"),
              Path(__file__).resolve().parent.parent / "bloque_c" / "sql" / "06_planeacion.sql"]


def main():
    ruta = next((r for r in CANDIDATOS if r.exists()), None)
    if not ruta:
        print("migrar_planeacion: no se encontró 06_planeacion.sql; se omite.", file=sys.stderr)
        return 0
    sql = ruta.read_text(encoding="utf-8")
    for intento in range(1, 16):
        try:
            with psycopg.connect(DSN, autocommit=True) as con:
                existe = con.execute("SELECT to_regclass('microhubs.zona') IS NOT NULL").fetchone()[0]
                if not existe:
                    print("migrar_planeacion: el esquema base aún no existe; se omite.")
                    return 0
                con.execute(sql)
                # Los permisos nuevos se leen de una caché de 5 min en Redis.
                print(f"migrar_planeacion: {ruta.name} aplicado.")
                return 0
        except psycopg.OperationalError as e:
            print(f"migrar_planeacion: esperando PostgreSQL ({intento}/15): {e}", file=sys.stderr)
            time.sleep(2)
    return 1


if __name__ == "__main__":
    sys.exit(main())
