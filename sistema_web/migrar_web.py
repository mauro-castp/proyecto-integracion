"""Aplica la migración del web ampliado sin reiniciar ni borrar datos."""
import os
from pathlib import Path
import psycopg


def mover_archivos(con):
    """Los archivos que quedaron dentro de la base pasan al almacén de objetos; la fila conserva solo sus datos. Es repetible."""
    if not con.execute("SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'microhubs' "
                       "AND table_name = 'web_archivo' AND column_name = 'ruta')").fetchone()[0]:
        return
    import hashlib
    import almacen_portal
    filas = con.execute("SELECT id, tipo, contenido FROM microhubs.web_archivo WHERE ruta IS NULL AND contenido IS NOT NULL").fetchall()
    for aid, tipo, contenido in filas:
        contenido, destino = bytes(contenido), almacen_portal.clave_objeto(aid, tipo)
        try:
            almacen_portal.guardar(destino, contenido, tipo)
        except almacen_portal.ErrorAlmacen as e:                 # se queda en la base y se intenta en el siguiente arranque
            print(f'Archivos del portal: no se movió {aid} ({e}).')
            continue
        con.execute("UPDATE microhubs.web_archivo SET ruta = %s, almacen = %s, sha256 = %s, contenido = NULL WHERE id = %s",
                    (destino, almacen_portal.nombre(), hashlib.sha256(contenido).hexdigest(), aid))
    if filas:
        print(f'Archivos del portal: {len(filas)} revisados para el almacén de objetos.')


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
        # 07 redefine las funciones de aviso. Si ya se aplicó, volver a correrla en cada arranque
        # desharía las versiones posteriores de 08 y 09 (tipo, referencia y preferencias).
        ya = con.execute("SELECT to_regclass('microhubs.web_migracion') IS NOT NULL").fetchone()[0] and \
            con.execute("SELECT EXISTS (SELECT 1 FROM microhubs.web_migracion WHERE clave = 'v1')").fetchone()[0]
        if ya:
            print('Web ampliado: ya estaba aplicada; no se repite.')
            mover_archivos(con)
            return
        con.execute(ruta.read_text(encoding='utf-8'))
        mover_archivos(con)
    # Obliga a releer las asignaciones tras agregar los nuevos perfiles.
    from nucleo import r_cache
    for key in r_cache.scan_iter('cache:permisos:*'):
        r_cache.delete(key)
    print('Web ampliado: migración aplicada.')


if __name__ == '__main__':
    main()
