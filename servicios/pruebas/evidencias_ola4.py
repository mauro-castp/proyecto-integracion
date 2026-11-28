"""
evidencias_ola4.py — Casos de las altas, cambios y bajas de la entrega final y del alta de pedidos y entregas. Los llama evidencias.py.
Lo que se crea se da de baja (los productos y zonas de prueba quedan inactivos; la bitácora referencia las cuentas).
"""
import datetime as dt
import uuid
from urllib.parse import urlsplit

from pruebas.preparar_listos import dejar_listos, retirar


def _reporte_archivado(ev, pg, adm, otro):
    """La exportación queda archivada en el almacén y se descarga con una URL firmada que caduca."""
    hoy = dt.date.today()
    x, _ = ev.http("reportes", "GET", f"reportes/pedidos_por_dia/exportar?formato=csv&desde={hoy - dt.timedelta(days=30)}&hasta={hoy}", token=adm)
    xid = {k.lower(): v for k, v in x.encabezados.items()}["x-reporte-id"]
    r = ev.caso("REP-A1", "reportes", "Enlace firmado de un reporte archivado", "El archivo vive en el almacén; la base guarda su ruta y su SHA-256.",
                "GET", f"reportes/exportaciones/{xid}/enlace", token=adm,
                evidencia=lambda r: [pg("SELECT id, ruta, almacen, left(sha256, 16) AS sha256, bytes FROM reporte_exportacion WHERE id = %s", (xid,))])
    ev.caso("REP-A2", "reportes", "El enlace de otra persona", "Solo quien exportó, el administrador o el auditor.", "GET",
            f"reportes/exportaciones/{xid}/enlace", token=otro, esperado=404)
    if r is not None and r.status == 200 and "/reportes/descarga?" in r.json["url_firmada"]:      # almacén local; en la nube la URL es de Cloud Storage
        ev.caso("REP-A3", "reportes", "Descargar con la URL firmada", "La firma sustituye al token y caduca.", "GET",
                "reportes/descarga?" + urlsplit(r.json["url_firmada"]).query, verificar=lambda x: len(x.texto) > 0)
    ev.caso("REP-A4", "reportes", "Firma alterada", "Sin una firma válida no se entrega el archivo.", "GET",
            "reportes/descarga?k=reportes/otro.csv&e=1&n=otro.csv&t=text/csv&s=alterada", esperado=403)


def _despacho_de_paradas(ev, pg, hub, op, rep, rid):
    """POST /entregas/asignaciones: las paradas de una ruta se despachan todas o ninguna."""
    listos = dejar_listos(2, hub)
    ids = [p["pedido_id"] for p in listos]
    paradas = [{"pedido_id": p, "repartidor_id": rid, "orden_parada": i} for i, p in enumerate(ids, 1)]
    ev.caso("ENT-B1", "entregas", "El repartidor no despacha", "Sin entregas.asignar.", "POST", "entregas/asignaciones",
            cuerpo={"paradas": paradas}, token=rep, esperado=403)
    ev.caso("ENT-B2", "entregas", "Una parada que no existe anula el despacho", "Todas o ninguna.", "POST", "entregas/asignaciones",
            cuerpo={"paradas": paradas + [{"pedido_id": 999999999, "repartidor_id": rid, "orden_parada": len(ids) + 1}]}, token=op, esperado=404,
            evidencia=lambda x: [pg("SELECT id, estado::text AS estado FROM pedido WHERE id = ANY(%s) ORDER BY id", (ids,))])
    r = ev.caso("ENT-B3", "entregas", "Despachar las paradas de una ruta", "Crea las entregas, pone los pedidos en ruta y avisa al repartidor.", "POST",
                "entregas/asignaciones", cuerpo={"paradas": paradas}, token=op, esperado=201, verificar=lambda x: x.json["asignadas"] == len(ids),
                evidencia=lambda x: [pg("SELECT pedido_id, repartidor_id, orden_parada, salida_en FROM entrega WHERE pedido_id = ANY(%s) ORDER BY orden_parada", (ids,))])
    if r is None or r.status != 201:
        retirar([p["pedido_id"] for p in listos if p["nuevo"]])
        return
    for n, e in enumerate(r.json["entregas"], 4):       # se cierran para no dejar entregas abiertas del repartidor de demostración
        eid = e["entrega_id"]
        doc = ev.http("documentos", "POST", "documentos", {"nombre": f"cierre-{eid}.pdf", "tipo_mime": "application/pdf",
                      "contenido_base64": "JVBERi0xLjQgZXZpZGVuY2lhICUlRU9G", "referencia": {"tipo": "entrega", "id": str(eid)}}, token=rep)[0].json["id"]
        ev.caso(f"ENT-B{n}", "entregas", "Cerrar una parada despachada", "El cliente no estaba: se registra la incidencia (RN29).", "POST",
                f"entregas/{eid}/resultado", cuerpo={"resultado": "fallida", "incidencia": "Cliente ausente (corrida de evidencias)", "monto_cobrado": 0,
                "cambio_entregado": 0, "ubicacion": {"latitud": 25.7491, "longitud": -100.3611}, "evidencia_ids": [doc],
                "capturado_en": dt.datetime.now(dt.timezone.utc).isoformat(), "id_cliente_local": str(uuid.uuid4())}, token=rep, esperado=201)


def ejecutar_ola4(ev, h):
    pg, bd = h.pg, h.bd
    print("15. Entrega final: altas, cambios y bajas; pedidos y entregas")
    adm, op, rep = ev.entrar("admin@codex.mx"), ev.entrar("operador.mh01@codex.mx"), ev.entrar("repartidor1@codex.mx")
    cli = ev.entrar("juan.chapa1@correo.mx")
    m = uuid.uuid4().hex[:6].upper()

    def uno(sql, args=()):
        return bd.consultar(sql, args, una=True)

    catalogos = [
        ("PRD", "productos", "producto", {"clave_interna": f"EV-{m}", "nombre": f"Producto de evidencia {m}", "categoria_id": 1, "unidad": "pieza", "precio": 19.5},
         {"precio": 21.0}),
        ("ZNA", "zonas", "zona", {"clave": f"EV{m}", "nombre": f"Zona {m}", "colonia": f"Colonia {m}", "codigo_postal": "64102", "latitud": 25.77, "longitud": -100.37},
         {"nombre": f"Zona {m} renombrada"}),
        ("MIC", "microhubs", "microhub", {"clave": f"EV{m}", "nombre": f"Microhub {m}", "direccion": "Calle de evidencia 1", "latitud": 25.7705, "longitud": -100.3705,
                                          "radio_km": 0.5, "capacidad_turno": 10}, {"radio_km": 0.8}),
    ]
    for pref, servicio, tabla, alta, cambio in catalogos:
        r = ev.caso(f"{pref}-A1", servicio, f"Alta de {tabla}", "Alta con permiso; queda en la bitácora y limpia la caché.", "POST", servicio, cuerpo=alta,
                    token=adm, esperado=201,
                    evidencia=lambda r, t=tabla: [pg("SELECT accion, usuario_id, fecha FROM auditoria WHERE entidad = %s AND entidad_id = %s ORDER BY id", (t, str(r.json["id"])))])
        if r is None or r.status != 201:
            continue
        ident = r.json["id"]
        ev.caso(f"{pref}-A2", servicio, f"Cambio de {tabla} (PATCH)", "Solo los campos enviados.", "PATCH", f"{servicio}/{ident}", cuerpo=cambio, token=adm)
        ev.caso(f"{pref}-A3", servicio, f"Cambio de {tabla} (PUT)", "PUT es alias de PATCH.", "PUT", f"{servicio}/{ident}", cuerpo=cambio, token=adm)
        ev.caso(f"{pref}-A4", servicio, f"Alta de {tabla} sin permiso", "El operador no administra el catálogo.", "POST", servicio, cuerpo=alta, token=op, esperado=403)
        ev.caso(f"{pref}-A5", servicio, f"Baja de {tabla}", "Baja lógica: se conserva su historia.", "DELETE", f"{servicio}/{ident}", token=adm, esperado=204,
                evidencia=lambda r, t=tabla, i=ident: [pg(f"SELECT id, estatus FROM {t} WHERE id = %s", (i,))])

    correo = f"ev.{m.lower()}@ejemplo.mx"
    r = ev.caso("USR-A1", "usuarios", "Crear una cuenta", "La clave se guarda con bcrypt y no se devuelve.", "POST", "usuarios",
                cuerpo={"nombre": "Cuenta", "apellidos": "De evidencia", "correo": correo, "clave": "Clave-de-evidencia-1", "rol": "repartidor"}, token=adm, esperado=201,
                evidencia=lambda r: [pg("SELECT id, correo, left(hash_contrasena, 4) AS algoritmo, estatus FROM usuario WHERE id = %s", (r.json["id"],))])
    if r is not None and r.status == 201:
        uid = r.json["id"]
        ev.caso("USR-A2", "usuarios", "Cambiar el perfil de una cuenta", "Cierra sus sesiones.", "PATCH", f"usuarios/{uid}", cuerpo={"rol": "planeador"}, token=adm)
        ev.caso("USR-A3", "usuarios", "Cambiar una cuenta (PUT)", "PUT es alias de PATCH.", "PUT", f"usuarios/{uid}", cuerpo={"telefono": "8112223344"}, token=adm)
        ev.caso("USR-A4", "usuarios", "Nadie se cambia a sí mismo", "Protege al último administrador.", "DELETE", "usuarios/1", token=adm, esperado=409)
        ev.caso("USR-A5", "usuarios", "Dar de baja una cuenta", "Baja lógica y cierre de sesiones.", "DELETE", f"usuarios/{uid}", token=adm, esperado=204,
                evidencia=lambda r: [pg("SELECT id, estatus, fecha_baja IS NOT NULL AS con_fecha FROM usuario WHERE id = %s", (uid,))])

    hub = uno("SELECT id FROM microhub WHERE clave = 'MH-01'")["id"]
    _reporte_archivado(ev, pg, adm, ev.entrar("planeador@codex.mx"))
    _despacho_de_paradas(ev, pg, hub, op, rep, uno("SELECT id FROM usuario WHERE correo = 'repartidor1@codex.mx'")["id"])
    prods = bd.consultar("SELECT i.producto_id FROM inventario i JOIN producto p ON p.id = i.producto_id AND p.estatus = 'activo' "
                         "WHERE i.existencia >= 20 GROUP BY i.producto_id HAVING count(*) >= 2 ORDER BY max(p.precio) DESC LIMIT 2")
    cuerpo = {"lineas": [{"producto_id": p["producto_id"], "cantidad": 3} for p in prods], "operacion_uuid": str(uuid.uuid4())}
    r = ev.caso("PED-A1", "pedidos", "Crear un pedido", "Precio del servidor, ticket mínimo y asignación del motor.", "POST", "pedidos", cuerpo=cuerpo, token=cli,
                esperado=201, evidencia=lambda r: [pg("SELECT pedido_id, producto_id, cantidad, precio_unitario FROM pedido_detalle WHERE pedido_id = %s", (r.json["id"],))])
    ev.caso("PED-A2", "pedidos", "Reenviar el mismo pedido", "Idempotente: no se duplica.", "POST", "pedidos", cuerpo=cuerpo, token=cli,
            verificar=lambda x: x.json["duplicado"] is True)
    ev.caso("PED-A3", "pedidos", "Pedido bajo el mínimo", "RN07: queda como demanda no atendida.", "POST", "pedidos",
            cuerpo={"lineas": [{"producto_id": uno("SELECT id FROM producto WHERE estatus = 'activo' ORDER BY precio LIMIT 1")["id"], "cantidad": 1}]}, token=cli,
            esperado=422, evidencia=lambda x: [pg("SELECT tipo, zona_id, origen, fecha FROM demanda_no_atendida WHERE origen = 'api' ORDER BY id DESC LIMIT 1")])
    if r is None or r.status != 201 or not r.json["asignado"]:
        return
    pid, mh, total = r.json["id"], r.json["microhub_id"], r.json["total"]
    correo_op = uno("SELECT u.correo FROM usuario u JOIN rol rl ON rl.id = u.rol_id WHERE rl.clave = 'operador' AND u.microhub_id = %s AND u.estatus = 'activo' ORDER BY u.id LIMIT 1", (mh,))["correo"]
    op2 = ev.entrar(correo_op)
    correo_rep = uno("SELECT u.correo FROM usuario u JOIN rol rl ON rl.id = u.rol_id WHERE rl.clave = 'repartidor' AND u.microhub_id = %s "
        "AND u.estatus = 'activo' ORDER BY u.id LIMIT 1", (mh,))["correo"]      # RN41: del mismo microhub que el pedido
    rep_p = ev.entrar(correo_rep)
    rid = uno("SELECT id FROM usuario WHERE correo = %s", (correo_rep,))["id"]
    ev.http("pedidos", "POST", f"pedidos/{pid}/estado", {"estado": "en_preparacion"}, token=op2)
    ev.caso("PED-A4", "pedidos", "Marcar listo", "El operador libera el pedido para despacho.", "POST", f"pedidos/{pid}/listo", cuerpo={}, token=op2)
    r = ev.caso("ENT-A1", "entregas", "Asignar la entrega", "Queda en ruta y el repartidor recibe el aviso.", "POST", "entregas",
                cuerpo={"pedido_id": pid, "repartidor_id": rid}, token=op2, esperado=201,
                evidencia=lambda x: [pg("SELECT id, repartidor_id, turno_fecha, salida_en FROM entrega WHERE pedido_id = %s", (pid,))])
    ev.caso("ENT-A2", "entregas", "Asignar dos veces", "El pedido ya tiene entrega.", "POST", "entregas", cuerpo={"pedido_id": pid, "repartidor_id": rid},
            token=op2, esperado=409)
    ev.caso("ENT-A3", "entregas", "El repartidor no asigna", "Sin entregas.asignar.", "POST", "entregas", cuerpo={"pedido_id": pid, "repartidor_id": rid},
            token=rep_p, esperado=403)
    if r is not None and r.status == 201:
        eid = r.json["entrega_id"]
        doc = ev.http("documentos", "POST", "documentos", {"nombre": f"cierre-{eid}.pdf", "tipo_mime": "application/pdf",
                      "contenido_base64": "JVBERi0xLjQgZXZpZGVuY2lhICUlRU9G", "referencia": {"tipo": "entrega", "id": str(eid)}}, token=rep_p)[0].json["id"]
        ev.http("entregas", "POST", f"entregas/{eid}/resultado", {"resultado": "entregado", "monto_cobrado": total, "cambio_entregado": 0,
                "ubicacion": {"latitud": 25.7491, "longitud": -100.3611}, "evidencia_ids": [doc], "capturado_en": dt.datetime.now(dt.timezone.utc).isoformat(),
                "id_cliente_local": str(uuid.uuid4())}, token=rep_p)
