"""Aplica la migración idempotente también cuando el volumen PostgreSQL ya existe."""
from pathlib import Path
import os
import psycopg

archivo = Path("/migrations/06_planeacion.sql")
if not archivo.exists():
    archivo = Path(__file__).parents[1] / "bloque_c" / "sql" / "06_planeacion.sql"

with psycopg.connect(os.environ["PG_DSN"], autocommit=True) as con:
    con.execute(archivo.read_text(encoding="utf-8"))
print("Migración de planeación aplicada.")
