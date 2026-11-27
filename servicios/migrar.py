"""
migrar.py — Aplica 06 a 16 a una base que ya existía.

PostgreSQL solo ejecuta /docker-entrypoint-initdb.d al crear el volumen. Con
un volumen existente (por ejemplo, el del Primer Parcial), este paso agrega
lo de planeación (06), web ampliado (07), microservicios (08), flujo de
negocio (09) y análisis (10) sin borrar datos. Los cinco scripts son idempotentes.
docker-compose.integrado.yml lo corre una vez antes de levantar el web y los
servicios, y al terminar borra la caché de permisos para que los permisos
nuevos se lean de nuevo.
"""
import os
import sys
import time
from pathlib import Path

import psycopg

DSN = os.environ.get("PG_DSN", "host=127.0.0.1 port=5432 dbname=microhubs_p1 user=postgres password=microhubs_dev")
CARPETA = Path(os.environ.get("SQL_DIR", "/app/sql"))
SCRIPTS = ["06_planeacion.sql", "07_web_ampliado.sql", "08_microservicios.sql", "09_ola1_flujo_negocio.sql", "10_ola2_analitica.sql",
           "11_ola3_observabilidad.sql", "12_rendimiento.sql", "13_entrega_final.sql", "14_pedidos_api.sql",
           "15_archivos_bucket.sql", "16_perfil_proveedor.sql"]


def borrar_cache_permisos():
    """Los permisos nuevos no se verían hasta 5 minutos después si quedara la caché anterior."""
    try:
        import redis
        r = redis.Redis.from_url(os.environ.get("REDIS_URL", "redis://127.0.0.1:6379"), db=1, socket_timeout=2)
        for llave in r.scan_iter("cache:permisos:*"):
            r.delete(llave)
    except Exception as e:                     # Redis puede no estar disponible al migrar
        print(f"migrar: no se borró la caché de permisos ({e}).", file=sys.stderr)


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
                borrar_cache_permisos()
                return 0
        except psycopg.OperationalError as e:
            print(f"migrar: esperando PostgreSQL ({intento}/30): {e}", file=sys.stderr)
            time.sleep(2)
    print("migrar: PostgreSQL no respondió.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
