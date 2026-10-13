"""Aplica la migración del web ampliado sin reiniciar ni borrar datos."""
import os
from pathlib import Path
import psycopg


def main():
    rutas = [Path(__file__).with_name('07_web_ampliado.sql'),
             Path(__file__).resolve().parent.parent / 'bloque_c/sql/07_web_ampliado.sql']
    ruta = next((p for p in rutas if p.is_file()), None)
    if ruta is None:
        raise FileNotFoundError('Falta 07_web_ampliado.sql')
    dsn = os.environ.get('PG_DSN')
    if not dsn:
        from nucleo import Config
        dsn = Config.PG_DSN
    with psycopg.connect(dsn, autocommit=True) as con:
        con.execute(ruta.read_text(encoding='utf-8'))
    # Obliga a releer las asignaciones tras agregar los nuevos perfiles.
    from nucleo import r_cache
    for key in r_cache.scan_iter('cache:permisos:*'):
        r_cache.delete(key)
    print('Web ampliado: migración aplicada.')


if __name__ == '__main__':
    main()
