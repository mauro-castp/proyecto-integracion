"""
cambiar_claves_demo.py — En la nube, ninguna cuenta puede quedarse con la clave de demostración: está en este repositorio, que es público.

Cambia la clave de TODA cuenta que todavía tenga la de demostración por la de la variable MICROHUBS_CLAVE (la genera instalar_vm.sh y vive
solo en el .env de la VM). Las cuentas que ya tienen otra clave no se tocan. Es repetible y no imprime ninguna clave.

Lo ejecuta deploy/gcp/instalar_vm.sh dentro del contenedor de autenticación:

  docker compose ... exec -T -e MICROHUBS_CLAVE auth python - < deploy/gcp/cambiar_claves_demo.py
"""
import os
import sys

import bcrypt
import psycopg

CLAVE_DEL_REPOSITORIO = b"Codex#2026"


def main():
    nueva = os.environ.get("MICROHUBS_CLAVE", "")
    if len(nueva) < 12 or nueva.encode() == CLAVE_DEL_REPOSITORIO:
        print("cambiar_claves_demo: MICROHUBS_CLAVE debe tener al menos 12 caracteres y no ser la de demostración.", file=sys.stderr)
        return 1
    with psycopg.connect(os.environ["PG_DSN"]) as con, con.cursor() as cur:
        cur.execute("SELECT id, hash_contrasena FROM microhubs.usuario WHERE hash_contrasena IS NOT NULL")
        cuentas = cur.fetchall()
        hash_nuevo, cambiadas = None, 0
        for uid, h in cuentas:
            try:
                demo = bcrypt.checkpw(CLAVE_DEL_REPOSITORIO, h.encode())
            except ValueError:                       # un hash que no es bcrypt no puede entrar con ninguna clave
                continue
            if demo:
                hash_nuevo = hash_nuevo or bcrypt.hashpw(nueva.encode(), bcrypt.gensalt(10)).decode()
                cur.execute("UPDATE microhubs.usuario SET hash_contrasena = %s WHERE id = %s", (hash_nuevo, uid))
                cambiadas += 1
    print(f"cambiar_claves_demo: {len(cuentas)} cuentas revisadas, {cambiadas} con la clave de demostración cambiadas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
