"""
migrar_a_almacen.py — Mueve al almacén de objetos (Google Cloud Storage) los documentos que todavía guardan su archivo DENTRO de MongoDB
(campo `contenido`), y deja en la base solo sus datos: ruta, privacidad, estado y metadatos.

Es seguro repetirlo: solo toca documentos con `contenido` y sin `ruta`. Antes de mover cada uno comprueba que su SHA-256 coincida; si no
coincide lo deja intacto y lo reporta. Solo borra el contenido de MongoDB después de confirmar que el objeto quedó en el almacén.

  docker compose exec documentos python -m servicio.migrar_a_almacen --simular     # solo cuenta, no cambia nada
  docker compose exec documentos python -m servicio.migrar_a_almacen
"""
import hashlib
import sys

from comun import almacen
from comun.datos import mongo


def migrar(simular=False, db=None, alm=None):
    db = db if db is not None else mongo()
    if db is None:
        raise SystemExit("MongoDB no está disponible.")
    alm = alm or almacen.obtener()
    cuenta = {"movidos": 0, "ya_en_almacen": 0, "sha_distinto": 0, "errores": 0, "pendientes": 0}
    for d in db.documentos.find({"contenido": {"$exists": True}, "ruta": {"$exists": False}}):
        contenido = bytes(d["contenido"])
        if hashlib.sha256(contenido).hexdigest() != d["sha256"]:
            cuenta["sha_distinto"] += 1
            print(f"  ! {d['_id']}: el SHA-256 guardado no coincide con el contenido; no se mueve.", file=sys.stderr)
            continue
        if simular:
            cuenta["pendientes"] += 1
            continue
        ruta = almacen.clave_objeto(str(d["_id"]), d["tipo_mime"], d["creado_en"].timestamp())
        try:
            if alm.existe(ruta):
                cuenta["ya_en_almacen"] += 1                                  # una corrida anterior se interrumpió a medias
            else:
                alm.guardar(ruta, contenido, d["tipo_mime"], d["sha256"])
            if hashlib.sha256(alm.leer(ruta)).hexdigest() != d["sha256"]:      # se confirma lo guardado ANTES de borrar el original
                raise almacen.ErrorAlmacen("lo guardado no coincide con el original")
        except almacen.ErrorAlmacen as e:
            cuenta["errores"] += 1
            print(f"  ! {d['_id']}: {e}", file=sys.stderr)
            continue
        db.documentos.update_one({"_id": d["_id"]}, {
            "$set": {"ruta": ruta, "privacidad": d.get("privacidad", "privado"), "estado": d.get("estado", "activo"),
                     "metadatos": {"almacen": alm.nombre, "origen": "api"}},
            "$unset": {"contenido": ""}})
        cuenta["movidos"] += 1
    return cuenta


if __name__ == "__main__":
    resultado = migrar(simular="--simular" in sys.argv)
    print("Documentos:", ", ".join(f"{k}={v}" for k, v in resultado.items()))
    sys.exit(1 if resultado["errores"] or resultado["sha_distinto"] else 0)
