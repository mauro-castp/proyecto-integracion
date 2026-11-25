"""
preparar_listos.py — Deja pedidos LISTOS PARA DESPACHAR en un microhub, sin repartidor.

Es lo que el servicio de rutas toma para armar un plan (pedidos en estado en_preparacion con listo_en). Pasa por las
mismas reglas del motor que la operación real: el pedido se crea con su carrito, lo asigna fn_asignar_pedido y el
operador de su microhub lo pasa a preparación y lo marca como listo.

  python -m pruebas.preparar_listos --cantidad 6 [--microhub 1]       (PG_DSN en el entorno)
  python -m pruebas.preparar_listos --cancelar 163 168                 retira pedidos de prueba (los regresa a «asignado» y los cancela)

Los pedidos que ya estaban listos se reutilizan y no se tocan. Los que se crean aquí se devuelven con la marca
«nuevo» y se retiran con `retirar()` al terminar: el motor no deja cancelar un pedido en preparación, así que la
prueba lo regresa a «asignado» (solo posible con un usuario de base de datos con privilegios, el de desarrollo) y
lo cancela como cualquier pedido asignado, con lo que se devuelve el inventario. Los pedidos que se crean de más
para otro microhub, mientras se busca uno del microhub pedido, se cancelan igual.
"""
import argparse
import os

import psycopg
from psycopg.rows import dict_row

from pruebas.preparar_entregas import actor, crear_pedido

DSN = os.environ.get("PG_DSN", "host=127.0.0.1 port=5432 dbname=microhubs_p1 user=postgres password=microhubs_dev")


def dejar_listos(cantidad, microhub_id=None, dsn=DSN):
    """Deja al menos `cantidad` pedidos listos para despachar (los que ya hay cuentan; solo se crean los que faltan).
    Si se indica microhub, solo cuentan los de ese microhub. Devuelve los pedidos listos, no solo los nuevos."""
    hechos, sobrantes = [], []
    with psycopg.connect(dsn, row_factory=dict_row) as con, con.cursor() as cur:
        cur.execute("SET search_path TO microhubs, public")
        cur.execute("SELECT p.id AS pedido_id, p.folio, p.microhub_id, p.zona_id FROM pedido p WHERE p.estado = 'en_preparacion' AND p.listo_en IS NOT NULL "
                    "AND NOT EXISTS (SELECT 1 FROM entrega e WHERE e.pedido_id = p.id) AND (%s::integer IS NULL OR p.microhub_id = %s) ORDER BY p.id",
                    (microhub_id, microhub_id))
        hechos = [{**f, "nuevo": False} for f in cur.fetchall()][:cantidad]
        cantidad = cantidad - len(hechos)
        intentos = 0
        while cantidad > 0 and intentos < cantidad * 12:
            intentos += 1
            cur.execute("SAVEPOINT nuevo")
            try:
                pid = crear_pedido(cur, cerca_de=microhub_id)
                cur.execute("RELEASE SAVEPOINT nuevo")
            except psycopg.Error:
                cur.execute("ROLLBACK TO SAVEPOINT nuevo")
                continue
            if not pid:
                continue
            cur.execute("SELECT p.folio, p.microhub_id, p.zona_id, (SELECT u.id FROM usuario u JOIN rol r ON r.id = u.rol_id "
                        "WHERE r.clave = 'operador' AND u.microhub_id = p.microhub_id ORDER BY u.id LIMIT 1) AS operador "
                        "FROM pedido p WHERE p.id = %s", (pid,))
            p = cur.fetchone()
            if not p["operador"] or (microhub_id and p["microhub_id"] != microhub_id):
                sobrantes.append(pid)                                  # no es del microhub pedido: se cancela al final
                continue
            actor(cur, "operador", p["operador"])
            cur.execute("UPDATE pedido SET estado = 'en_preparacion' WHERE id = %s", (pid,))
            cur.execute("UPDATE pedido SET listo_en = now() WHERE id = %s", (pid,))
            hechos.append({"pedido_id": pid, "folio": p["folio"], "microhub_id": p["microhub_id"], "zona_id": p["zona_id"], "nuevo": True})
            cantidad -= 1
        con.commit()
    if sobrantes:
        cancelar(sobrantes, dsn)
    return hechos


def retirar(pedido_ids, dsn=DSN):
    """Quita pedidos de prueba que ya estaban listos: los regresa a «asignado» y los cancela (el inventario se devuelve)."""
    if not pedido_ids:
        return
    with psycopg.connect(dsn, row_factory=dict_row) as con, con.cursor() as cur:
        cur.execute("SET search_path TO microhubs, public")
        cur.execute("SET LOCAL session_replication_role = 'replica'")      # solo para este UPDATE: el motor no permite retroceder un pedido
        cur.execute("UPDATE pedido SET estado = 'asignado', listo_en = NULL WHERE id = ANY(%s) AND estado = 'en_preparacion' "
                    "AND NOT EXISTS (SELECT 1 FROM entrega e WHERE e.pedido_id = pedido.id)", (list(pedido_ids),))
        cur.execute("SET LOCAL session_replication_role = 'origin'")
        con.commit()
    cancelar(pedido_ids, dsn)


def cancelar(pedido_ids, dsn=DSN):
    """Cancela los pedidos de prueba como administrador (el motor devuelve el inventario)."""
    with psycopg.connect(dsn, row_factory=dict_row) as con, con.cursor() as cur:
        cur.execute("SET search_path TO microhubs, public")
        cur.execute("SELECT u.id FROM usuario u JOIN rol r ON r.id = u.rol_id WHERE r.clave = 'administrador' AND u.estatus = 'activo' ORDER BY u.id LIMIT 1")
        admin = cur.fetchone()["id"]
        actor(cur, "administrador", admin)
        for pid in pedido_ids:
            cur.execute("UPDATE pedido SET estado = 'cancelado', motivo_cancelacion = 'Pedido de prueba' WHERE id = %s AND estado <> 'cancelado'", (pid,))
            if cur.rowcount:                                   # el motor no devuelve solo el inventario: lo hace quien cancela (RN18)
                cur.execute("SELECT fn_devolver_inventario(%s, 'devolucion_cancelacion', 'Pedido de prueba cancelado')", (pid,))
        con.commit()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--cantidad", type=int, default=6)
    ap.add_argument("--microhub", type=int, default=None)
    ap.add_argument("--cancelar", type=int, nargs="+", default=None, help="en vez de crear, cancela estos pedidos de prueba")
    a = ap.parse_args()
    if a.cancelar:
        retirar(a.cancelar)
        raise SystemExit(f"Retirados {len(a.cancelar)} pedidos.")
    for h in dejar_listos(a.cantidad, a.microhub):
        print(f"Pedido {h['pedido_id']} ({h['folio']}) listo en el microhub {h['microhub_id']}, zona {h['zona_id']}")
