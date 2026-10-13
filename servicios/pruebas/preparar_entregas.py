"""
preparar_entregas.py — Deja entregas EN RUTA asignadas a un repartidor.

Sirve para la demostración y para las pruebas de las apps contra el backend
real (BackendRealTest de Android necesita 2 entregas en ruta). Recorre el
mismo camino que la operación real, pasando por las reglas del motor:

  1. Crea pedidos nuevos con un carrito que supera el ticket mínimo y los pasa
     por fn_asignar_pedido (motor real de asignación). Solo si el motor no
     encuentra microhub usa un pedido «asignado» que ya exista, para no vaciar
     la bandeja del operador al repetir la demostración.
  2. Como el operador de su microhub: en_preparacion → listo para despacho.
  3. Crea la entrega para el repartidor (turno de hoy) → el trigger le envía
     el aviso «Nueva entrega asignada» → el pedido pasa a en_ruta.

Uso (desde la raíz del repositorio, con el backend arriba):
  docker compose -f docker-compose.integrado.yml exec entregas python pruebas/preparar_entregas.py --cantidad 2
  python servicios/pruebas/preparar_entregas.py --correo repartidor1@codex.mx --cantidad 2     (PG_DSN en el entorno)
"""
import argparse
import os
import random

import psycopg
from psycopg.rows import dict_row

DSN = os.environ.get("PG_DSN", "host=127.0.0.1 port=5432 dbname=microhubs_p1 user=postgres password=microhubs_dev")


def actor(cur, rol, uid=None):
    cur.execute("SELECT set_config('app.rol', %s, true), set_config('app.usuario_id', %s, true)", (rol, str(uid or "")))


def crear_pedido(cur):
    """Pedido nuevo de un cliente real que pasa por fn_asignar_pedido. Devuelve el id o None."""
    cur.execute("SELECT c.id AS cliente_id, d.id AS domicilio_id, d.zona_id FROM cliente c "
                "JOIN domicilio d ON d.cliente_id = c.id AND d.activo ORDER BY random() LIMIT 1")
    cli = cur.fetchone()
    cur.execute("SELECT fn_ticket_minimo(%s) AS t", (cli["zona_id"],))
    minimo = float(cur.fetchone()["t"])
    cur.execute("SELECT p.id, p.precio FROM producto p WHERE p.estatus = 'activo' "
                "AND EXISTS (SELECT 1 FROM inventario i WHERE i.producto_id = p.id AND i.existencia > 20) "
                "ORDER BY random() LIMIT 2")
    productos = cur.fetchall()
    cantidad = max(1, int(minimo // (2 * float(min(p["precio"] for p in productos)))) + 1)
    subtotal = sum(float(p["precio"]) * cantidad for p in productos)
    actor(cur, "sistema")
    cur.execute("INSERT INTO pedido (cliente_id, domicilio_id, zona_id, subtotal, costo_envio) "
                "VALUES (%s,%s,%s,%s, fn_costo_envio(%s, %s::numeric)) RETURNING id",
                (cli["cliente_id"], cli["domicilio_id"], cli["zona_id"], subtotal, cli["zona_id"], subtotal))
    pid = cur.fetchone()["id"]
    for p in productos:
        cur.execute("INSERT INTO pedido_detalle (pedido_id, producto_id, cantidad, precio_unitario) VALUES (%s,%s,%s,%s)",
                    (pid, p["id"], cantidad, p["precio"]))
    cur.execute("SELECT * FROM fn_asignar_pedido(%s)", (pid,))
    return pid if cur.fetchone()["asignado"] else None


def preparar(correo, cantidad, dsn=DSN):
    creadas = []
    with psycopg.connect(dsn, row_factory=dict_row) as con, con.cursor() as cur:
        cur.execute("SET search_path TO microhubs, public")
        cur.execute("SELECT u.id FROM usuario u JOIN rol r ON r.id = u.rol_id "
                    "WHERE lower(u.correo) = %s AND r.clave = 'repartidor' AND u.estatus = 'activo'", (correo.lower(),))
        rep = cur.fetchone()
        if not rep:
            raise SystemExit(f"No existe un repartidor activo con el correo {correo}.")
        intentos = 0
        while len(creadas) < cantidad and intentos < cantidad * 10:
            intentos += 1
            cur.execute("SAVEPOINT nuevo")
            try:
                pid = crear_pedido(cur)
                cur.execute("RELEASE SAVEPOINT nuevo")
            except psycopg.Error:
                cur.execute("ROLLBACK TO SAVEPOINT nuevo")
                pid = None
            if not pid:
                cur.execute("SELECT p.id FROM pedido p WHERE p.estado = 'asignado' AND p.microhub_id IS NOT NULL "
                            "AND NOT EXISTS (SELECT 1 FROM entrega e WHERE e.pedido_id = p.id) "
                            "AND EXISTS (SELECT 1 FROM usuario u JOIN rol r ON r.id = u.rol_id WHERE r.clave = 'operador' "
                            "AND u.microhub_id = p.microhub_id) ORDER BY p.id LIMIT 1")
                fila = cur.fetchone()
                pid = fila["id"] if fila else None
            if not pid:
                continue
            cur.execute("SELECT p.folio, p.microhub_id, (SELECT u.id FROM usuario u JOIN rol r ON r.id = u.rol_id "
                        "WHERE r.clave = 'operador' AND u.microhub_id = p.microhub_id ORDER BY u.id LIMIT 1) AS operador "
                        "FROM pedido p WHERE p.id = %s", (pid,))
            p = cur.fetchone()
            if not p["operador"]:
                continue
            actor(cur, "operador", p["operador"])
            cur.execute("UPDATE pedido SET estado = 'en_preparacion' WHERE id = %s", (pid,))
            cur.execute("UPDATE pedido SET listo_en = now() WHERE id = %s", (pid,))
            orden = len(creadas) + 1
            cur.execute("INSERT INTO entrega (pedido_id, repartidor_id, turno_fecha, asignada_en, salida_en, orden_parada, "
                        "distancia_km, minutos_estimados, costo_entrega_estimado) "
                        "VALUES (%s,%s,current_date,now(),now(),%s,%s,%s,%s) RETURNING id",
                        (pid, rep["id"], orden, round(random.uniform(0.2, 1.5), 2), round(4 + 6 * orden, 1), 22.0))
            eid = cur.fetchone()["id"]
            cur.execute("UPDATE pedido SET estado = 'en_ruta' WHERE id = %s", (pid,))
            creadas.append({"entrega_id": eid, "pedido_id": pid, "folio": p["folio"]})
        con.commit()
    return creadas


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--correo", default="repartidor1@codex.mx")
    ap.add_argument("--cantidad", type=int, default=2)
    a = ap.parse_args()
    hechas = preparar(a.correo, a.cantidad)
    for h in hechas:
        print(f"Entrega {h['entrega_id']} · pedido {h['pedido_id']} ({h['folio']}) en ruta para {a.correo}")
    if len(hechas) < a.cantidad:
        raise SystemExit(f"Solo se prepararon {len(hechas)} de {a.cantidad}.")
