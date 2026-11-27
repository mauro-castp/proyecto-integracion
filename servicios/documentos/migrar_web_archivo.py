"""
migrar_web_archivo.py — Mueve al almacén de objetos los archivos que el portal guardaba DENTRO de PostgreSQL (tabla web_archivo).

Por cada fila: guarda el objeto, comprueba que lo guardado sea igual, registra sus datos en MongoDB (referencia: su dueño) y solo
entonces borra la fila. Es seguro repetirlo.

  docker compose -f docker-compose.integrado.yml exec documentos python -m servicio.migrar_web_archivo --simular
  docker compose -f docker-compose.integrado.yml exec documentos python -m servicio.migrar_web_archivo
"""
import hashlib
import sys

from bson import ObjectId

from comun import almacen
from comun.datos import conexion, mongo


def migrar(simular=False):
    db = mongo()
    if db is None:
        raise SystemExit("MongoDB no está disponible.")
    alm = almacen.obtener()
    cuenta = {"movidos": 0, "pendientes": 0, "errores": 0}
    with conexion(autocommit=True) as con, con.cursor() as cur:
        cur.execute("SELECT to_regclass('microhubs.web_archivo') IS NOT NULL AS hay")
        if not cur.fetchone()["hay"]:
            print("No existe la tabla web_archivo: no hay nada que mover.")
            return cuenta
        cur.execute("SELECT id, propietario_id, nombre, tipo, contenido, creado_en FROM web_archivo ORDER BY creado_en")
        for f in cur.fetchall():
            if simular:
                cuenta["pendientes"] += 1
                continue
            try:
                contenido = bytes(f["contenido"])
                sha = hashlib.sha256(contenido).hexdigest()
                oid = ObjectId()
                ruta = almacen.clave_objeto(str(oid), f["tipo"], f["creado_en"].timestamp())
                alm.guardar(ruta, contenido, f["tipo"], sha)
                if hashlib.sha256(alm.leer(ruta)).hexdigest() != sha:
                    raise almacen.ErrorAlmacen("lo guardado no coincide con el original")
                db.documentos.insert_one({"_id": oid, "nombre": f["nombre"], "tipo_mime": f["tipo"], "tamano_bytes": len(contenido),
                                          "sha256": sha, "referencia": {"tipo": "usuario", "id": str(f["propietario_id"])},
                                          "subido_por": int(f["propietario_id"]), "creado_en": f["creado_en"], "ruta": ruta,
                                          "privacidad": "privado", "estado": "activo", "metadatos": {"almacen": alm.nombre, "origen": "web"}})
                cur.execute("DELETE FROM web_archivo WHERE id = %s", (f["id"],))
                cuenta["movidos"] += 1
            except Exception as e:  # noqa: BLE001
                cuenta["errores"] += 1
                print(f"  ! {f['id']}: {type(e).__name__}: {e}", file=sys.stderr)
    return cuenta


if __name__ == "__main__":
    resultado = migrar("--simular" in sys.argv)
    print(resultado)
    sys.exit(1 if resultado["errores"] else 0)
