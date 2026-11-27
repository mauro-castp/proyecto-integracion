"""
flujos_integrales.py — Tres procesos de principio a fin, solo por la API, con cada paso verificado y lo que quedó en las bases.

  F1  Planeación de ubicación → operación → pedido → entrega (el flujo obligatorio)
  F2  Pedido e inventario → alerta → abastecimiento → recepción → reporte
  F3  Trabajo sin conexión → sincronización → trazabilidad → reporte

Cada proceso pasa por: usuarios con distintos perfiles, la app que usaría cada uno (escritorio = XML, Android = JSON, portal), varios
microservicios, Redis (sesión), PostgreSQL y MongoDB, un archivo en el almacén (bucket en la nube), la bitácora, un aviso y su visualización.

  servicios/pruebas/correr.sh flujos ola4            (dentro de la red de Docker, con el sistema arriba)
"""
import argparse
import base64
import datetime as dt
import json
import os
import sys
import time
import uuid
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
os.environ.setdefault("LOG_STDOUT", "0")

from pruebas.evidencias import (B64, CLAVE, Evidencias, a_html, a_markdown, a_tabla, bd, mg, pg, rd, xml)  # noqa: E402


def uno(sql, args=()):
    return bd.consultar(sql, args, una=True)


def ahora(menos_min=0):
    return (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=menos_min)).isoformat()


def lineas_con_existencia(hub, n=2, minimo=40):
    return bd.consultar("SELECT i.producto_id, p.precio FROM inventario i JOIN producto p ON p.id = i.producto_id AND p.estatus = 'activo' "
                        "WHERE i.microhub_id = %s AND i.existencia >= %s ORDER BY p.precio DESC LIMIT %s", (hub, minimo, n))


def lineas_en_todos_los_microhubs(n=2, minimo=20):
    """Productos con existencia en todos los microhubs activos: sirve sea cual sea el que cubra la zona del cliente."""
    return bd.consultar("SELECT i.producto_id FROM inventario i JOIN producto p ON p.id = i.producto_id AND p.estatus = 'activo' "
                        "JOIN microhub m ON m.id = i.microhub_id AND m.estatus = 'activo' GROUP BY i.producto_id, p.precio "
                        "HAVING min(i.existencia) >= %s AND count(*) = (SELECT count(*) FROM microhub WHERE estatus = 'activo') "
                        "ORDER BY p.precio DESC LIMIT %s", (minimo, n))


def evidencia_archivo(ev, token, ref_tipo, ref_id, nombre):
    r = ev.http("documentos", "POST", "documentos", {"nombre": nombre, "tipo_mime": "image/jpeg", "contenido_base64": B64,
                                                     "referencia": {"tipo": ref_tipo, "id": str(ref_id)}}, token=token)[0]
    return r


# ====================================================================
def flujo1(ev):
    print("F1. Planeación → operación → pedido → entrega")
    marca = uuid.uuid4().hex[:5].upper()
    plan, adm, aud = ev.entrar("planeador@codex.mx"), ev.entrar("admin@codex.mx"), ev.entrar("auditor@codex.mx")
    cli, rep = ev.entrar("juan.chapa1@correo.mx"), ev.entrar("repartidor1@codex.mx")
    dom = uno("SELECT d.latitud::float AS lat, d.longitud::float AS lng, d.zona_id FROM domicilio d JOIN cliente c ON c.id = d.cliente_id "
              "JOIN usuario u ON u.id = c.usuario_id WHERE u.correo = 'juan.chapa1@correo.mx' AND d.activo ORDER BY d.id LIMIT 1")
    lat, lng = round(dom["lat"] + 0.0002, 6), round(dom["lng"] + 0.0002, 6)
    candidato = {"clave": f"FL-{marca}", "nombre": f"Ubicación del flujo {marca}", "latitud": str(lat), "longitud": str(lng), "renta_estimada": "15000.00",
                 "nomina_estimada": "36000.00", "servicios_estimados": "6000.00", "otros_costos": "4000.00", "superficie_m2": "100",
                 "capacidad_fisica": "120", "accesibilidad_vial": "8", "zona_id": str(dom["zona_id"]), "poblacion_cubierta": "5200", "radio_km": "1.5"}
    r = ev.caso("F1-01", "planeacion", "Escritorio (XML): el planeador registra una ubicación candidata", "Planeación de ubicación.", "POST", "candidatos",
                cuerpo=xml("candidato_nuevo", candidato), formato="xml", token=plan, esperado=201, verificar=lambda x: "<costo_fijo>61000.00</costo_fijo>" in x.texto,
                evidencia=lambda x: [pg("SELECT id, clave, nombre, costo_fijo, decision FROM ubicacion_candidata WHERE clave = %s", (candidato["clave"],))])
    if r is None or r.status != 201:
        return
    cid = uno("SELECT id FROM ubicacion_candidata WHERE clave = %s", (candidato["clave"],))["id"]
    ev.caso("F1-02", "planeacion", "El planeador simula la operación de la candidata", "Capacidad, utilización y decisión sugerida (MongoDB).", "POST",
            f"candidatos/{cid}/simular", cuerpo={"supuestos": {"demanda_diaria": 100, "operadores": 3, "repartidores": 4, "ticket": 180.0, "costo_entrega": 22.0,
            "margen_bruto": 0.30, "renta": 15000.0, "nomina": 36000.0, "servicios": 6000.0, "otros": 4000.0, "distancia_km": 1.2, "capacidad_fisica": 120}},
            token=plan, verificar=lambda x: x.json["decision"].startswith("VIABLE"))
    ev.caso("F1-03", "punto-equilibrio", "Punto de equilibrio de la candidata", "Viabilidad financiera antes de decidir.", "POST", "punto-equilibrio/calculos",
            cuerpo={"candidato_id": cid, "pedidos_dia": 100, "ticket": 180, "margen_bruto": 0.30, "costos_fijos": 61000, "costo_variable_pedido": 22}, token=plan,
            verificar=lambda x: "equilibrio" in x.texto)
    ev.caso("F1-04", "planeacion", "El planeador decide", "La decisión queda con motivo y en la bitácora.", "POST", f"candidatos/{cid}/decision",
            cuerpo={"decision": "aceptado", "motivo": "Cubre la zona del cliente y la demanda esperada supera el equilibrio."}, token=plan,
            evidencia=lambda x: [pg("SELECT decision, decision_motivo FROM ubicacion_candidata WHERE id = %s", (cid,))])
    r = ev.caso("F1-05", "microhubs", "Operación: el administrador abre el microhub", "La candidata viable se vuelve microhub activo.", "POST", "microhubs",
                cuerpo={"clave": f"MH-{marca}", "nombre": f"Microhub {marca}", "direccion": "Ubicación aprobada en planeación", "latitud": lat, "longitud": lng,
                        "radio_km": 1.5, "capacidad_turno": 120}, token=adm, esperado=201)
    if r is None or r.status != 201:
        return
    mh = r.json["id"]
    operador = None
    try:
        ev.caso("F1-06", "capacidad", "Asignar personal al microhub", "Operadores, repartidores y capacidad física.", "PUT", f"capacidad/recursos/{mh}",
                cuerpo={"operadores": 2, "repartidores": 2, "capacidad_fisica": 120}, token=adm)
        correo = f"operador.{marca.lower()}@ejemplo.mx"
        clave = "Op-" + uuid.uuid4().hex[:12]
        r = ev.caso("F1-07", "usuarios", "Crear la cuenta del operador", "Cuenta nueva con su perfil y su microhub.", "POST", "usuarios",
                    cuerpo={"nombre": "Operador", "apellidos": marca, "correo": correo, "clave": clave, "rol": "operador", "microhub_id": mh}, token=adm, esperado=201)
        operador = r.json["id"] if r is not None and r.status == 201 else None
        hub1 = uno("SELECT id FROM microhub WHERE clave = 'MH-01'")["id"]
        productos = lineas_con_existencia(hub1, 2, 40)
        for i, p in enumerate(productos, 1):
            ev.caso(f"F1-08{'ab'[i - 1]}", "inventario", "Surtir el microhub nuevo", "Transferencia atómica desde MH-01.", "POST", "inventario/transferencias",
                    cuerpo={"origen_microhub_id": hub1, "destino_microhub_id": mh, "producto_id": p["producto_id"], "cantidad": 12,
                            "motivo": "Inventario inicial del microhub nuevo", "operacion_uuid": str(uuid.uuid4())}, token=adm, esperado=201)
        op = ev.http("auth", "POST", "auth/login", {"correo": correo, "clave": clave, "dispositivo": "portal"})[0].json["token_acceso"]
        pedido = {"lineas": [{"producto_id": p["producto_id"], "cantidad": 3} for p in productos], "operacion_uuid": str(uuid.uuid4())}
        r = ev.caso("F1-09", "pedidos", "Android (JSON): el cliente hace su pedido", "El motor lo asigna al microhub más cercano que tiene todo: el nuevo.", "POST",
                    "pedidos", cuerpo=pedido, token=cli, esperado=201, verificar=lambda x: x.json["microhub_id"] == mh,
                    evidencia=lambda x: [pg("SELECT criterio, candidatos_evaluados, microhub_ganador_id, motivo FROM decision_asignacion WHERE pedido_id = %s", (x.json["id"],)),
                                         pg("SELECT tipo, producto_id, cantidad, existencia_resultante FROM movimiento_inventario WHERE referencia_tipo = 'pedido' AND referencia_id = %s", (x.json["id"],))])
        if r is None or r.status != 201 or r.json["microhub_id"] != mh:
            return
        pid, total = r.json["id"], r.json["total"]
        ev.caso("F1-10", "pedidos", "El operador prepara el pedido", "La transición la valida el motor.", "POST", f"pedidos/{pid}/estado",
                cuerpo={"estado": "en_preparacion"}, token=op)
        ev.caso("F1-11", "pedidos", "El operador lo marca listo", "Queda disponible para despacho.", "POST", f"pedidos/{pid}/listo", cuerpo={}, token=op)
        rid = uno("SELECT id FROM usuario WHERE correo = 'repartidor1@codex.mx'")["id"]
        ev.caso("F1-12", "rutas", "Proponer la ruta de despacho", "Agrupa, asigna repartidor y ordena las paradas (algoritmo de rutas).", "POST", "rutas/planes",
                cuerpo={"microhub_id": mh, "pedido_ids": [pid], "repartidor_ids": [rid], "metodo": "automatico", "guardar": True}, token=op,
                esperado=201, verificar=lambda x: "ruta" in x.texto)
        r = ev.caso("F1-13", "entregas", "El operador asigna la entrega", "El pedido pasa a ruta y el repartidor recibe el aviso.", "POST", "entregas",
                    cuerpo={"pedido_id": pid, "repartidor_id": rid, "orden_parada": 1}, token=op, esperado=201,
                    evidencia=lambda x: [pg("SELECT titulo, tipo, referencia_id FROM web_notificacion WHERE destinatario_id = %s ORDER BY id DESC LIMIT 1", (rid,))])
        if r is None or r.status != 201:
            return
        eid = r.json["entrega_id"]
        ev.caso("F1-14", "entregas", "Android: el repartidor ve su parada", "Sesión validada en Redis.", "GET", "entregas/mias?por_pagina=50", token=rep,
                verificar=lambda x: any(e["id"] == eid for e in x.json["datos"]),
                evidencia=lambda x: [rd((0, "SCARD", f"auth:sesion:{rid}"))])
        ev.caso("F1-15", "seguimiento", "El repartidor envía su recorrido", "Puntos GPS en MongoDB (2dsphere).", "POST", f"seguimiento/{eid}/ubicaciones",
                cuerpo={"puntos": [{"latitud": lat, "longitud": lng, "capturado_en": ahora(4)}, {"latitud": dom["lat"], "longitud": dom["lng"], "capturado_en": ahora(1)}]},
                token=rep, esperado=201)
        foto = evidencia_archivo(ev, rep, "entrega", eid, f"evidencia-flujo1-{marca}.jpg")
        ev.caso("F1-16", "documentos", "La foto de evidencia queda en el almacén", "En la base solo sus datos; se descarga con un enlace firmado.", "GET",
                f"documentos/{foto.json['id']}/enlace", token=adm, verificar=lambda x: x.json["url_firmada"].startswith("http"),
                evidencia=lambda x: [mg("db.documentos.findOne({_id}) sin contenido", lambda db: {k: v for k, v in (db.documentos.find_one({"nombre": f"evidencia-flujo1-{marca}.jpg"}) or {}).items() if k != "contenido"})])
        ev.caso("F1-17", "entregas", "El repartidor cierra la entrega", "Cobro, ubicación y evidencia; idempotente.", "POST", f"entregas/{eid}/resultado",
                cuerpo={"resultado": "entregado", "monto_cobrado": total, "cambio_entregado": 0, "ubicacion": {"latitud": dom["lat"], "longitud": dom["lng"]},
                        "evidencia_ids": [foto.json["id"]], "capturado_en": ahora(), "id_cliente_local": str(uuid.uuid4())}, token=rep, esperado=201,
                evidencia=lambda x: [pg("SELECT estado_anterior, estado_nuevo, usuario_id, proceso FROM historial_estatus WHERE pedido_id = %s ORDER BY id", (pid,))])
        ev.caso("F1-18", "notificaciones", "El cliente recibe el aviso del cierre", "Aviso generado por el motor.", "GET", "notificaciones?por_pagina=5", token=cli,
                verificar=lambda x: any((n.get("referencia") or {}).get("id") == str(pid) for n in x.json["datos"]))
        ev.caso("F1-19", "auditoria-monitoreo", "El auditor reconstruye la historia del pedido", "Bitácora, estados, inventario y archivos en una línea de tiempo.", "GET",
                f"auditoria/trazabilidad/pedido/{pid}", token=aud, verificar=lambda x: {"auditoria", "estados", "inventario"} <= {e["origen"] for e in x.json["eventos"]})
        ev.caso("F1-20", "reportes", "Visualización: el microhub nuevo ya aparece en la comparación", "Datos listos para Highcharts.", "GET",
                f"reportes/comparacion_microhubs/grafica?microhub_id={mh}", token=plan, verificar=lambda x: x.json["series"][0]["datos"][0] >= 1)
    finally:
        # se retira lo que se abrió: el microhub no puede darse de baja con pedidos abiertos
        for p in bd.consultar("SELECT id FROM pedido WHERE microhub_id = %s AND estado IN ('asignado', 'en_preparacion')", (mh,)):
            ev.http("pedidos", "POST", f"pedidos/{p['id']}/estado", {"estado": "cancelado", "motivo": "Cierre del flujo de demostración"}, token=adm)
        ev.caso("F1-21", "microhubs", "Cierre: dar de baja el microhub de la demostración", "Baja lógica; conserva su historia.", "DELETE", f"microhubs/{mh}",
                token=adm, esperado=204)
        if operador:
            ev.http("usuarios", "DELETE", f"usuarios/{operador}", token=adm)


# ====================================================================
def flujo2(ev):
    print("F2. Pedido e inventario → alerta → abastecimiento → recepción → reporte")
    adm, op, aud = ev.entrar("admin@codex.mx"), ev.entrar("operador.mh01@codex.mx"), ev.entrar("auditor@codex.mx")
    cli = ev.entrar("juan.chapa1@correo.mx")
    hub = uno("SELECT id FROM microhub WHERE clave = 'MH-01'")["id"]
    p = uno("SELECT i.producto_id, i.existencia, i.minimo, i.disponible FROM v_inventario_disponible i JOIN producto pr ON pr.id = i.producto_id "
            "WHERE i.microhub_id = %s AND pr.estatus = 'activo' AND i.disponible >= 25 AND EXISTS (SELECT 1 FROM proveedor_producto x JOIN proveedor v ON v.id = x.proveedor_id "
            "WHERE x.producto_id = i.producto_id AND v.estatus = 'activo') AND NOT EXISTS (SELECT 1 FROM solicitud_compra_linea l JOIN solicitud_compra s ON s.id = l.solicitud_id "
            "WHERE l.producto_id = i.producto_id AND s.microhub_id = i.microhub_id AND s.estado IN ('pendiente', 'aprobada')) ORDER BY pr.precio DESC LIMIT 1", (hub,))
    pid_prod, minimo_antes = p["producto_id"], p["minimo"]
    nuevo_minimo = p["disponible"] + 10
    r = ev.caso("F2-01", "pedidos", "Android: un cliente compra y el inventario baja", "El motor descuenta inventario en la misma transacción.", "POST", "pedidos",
                cuerpo={"lineas": [{"producto_id": pid_prod, "cantidad": 10}], "operacion_uuid": str(uuid.uuid4())}, token=cli, esperado=201,
                evidencia=lambda x: [pg("SELECT microhub_id, producto_id, cantidad, existencia_resultante FROM movimiento_inventario WHERE referencia_tipo = 'pedido' AND referencia_id = %s", (x.json["id"],))])
    pedido = r.json["id"] if r is not None and r.status == 201 else None
    try:
        ev.caso("F2-02", "inventario", "El operador fija el mínimo y nace la alerta", "El trigger avisa del faltante.", "PATCH", f"inventario/{hub}/{pid_prod}/minimo",
                cuerpo={"minimo": nuevo_minimo}, token=adm)
        ev.caso("F2-03", "inventario", "La alerta de faltante", "Qué producto, cuánto falta y qué tan grave es.", "GET", f"inventario/alertas?microhub_id={hub}&por_pagina=100",
                token=op, verificar=lambda x: any(a["producto"]["id"] == pid_prod for a in x.json["datos"]))
        r = ev.caso("F2-04", "abastecimiento", "El operador pide reposición", "Solicitud con sus líneas.", "POST", "abastecimiento/solicitudes",
                    cuerpo={"microhub_id": hub, "motivo": "Faltante detectado por el sistema", "lineas": [{"producto_id": pid_prod, "cantidad": 100}]}, token=op, esperado=201)
        if r is None or r.status != 201:
            return
        sid = r.json["id"]
        ev.caso("F2-05", "abastecimiento", "El administrador aprueba", "Quien pidió recibe el aviso.", "POST", f"abastecimiento/solicitudes/{sid}/decision",
                cuerpo={"decision": "aprobada", "motivo": "Con presupuesto"}, token=adm)
        r = ev.caso("F2-06", "abastecimiento", "Se emite la orden de compra", "Al proveedor con la mejor oferta.", "POST", f"abastecimiento/solicitudes/{sid}/ordenar",
                    cuerpo={}, token=adm, esperado=201)
        if r is None or r.status != 201:
            return
        oid = r.json["ordenes"][0]["id"]
        ev.caso("F2-07", "abastecimiento", "Llega la mercancía y se recibe", "Sube el inventario una sola vez (idempotente).", "POST", f"abastecimiento/ordenes/{oid}/recepcion",
                cuerpo={"operacion_uuid": str(uuid.uuid4()), "nota": "Completo", "lineas": [{"producto_id": pid_prod, "cantidad": 100}]}, token=op,
                esperado=201, evidencia=lambda x: [pg("SELECT existencia, minimo FROM inventario WHERE microhub_id = %s AND producto_id = %s", (hub, pid_prod))])
        foto = evidencia_archivo(ev, op, "usuario", uno("SELECT id FROM usuario WHERE correo = 'operador.mh01@codex.mx'")["id"], f"remision-{oid}.jpg")
        ev.caso("F2-08", "documentos", "La remisión firmada queda en el almacén", "Archivo con enlace firmado.", "GET", f"documentos/{foto.json['id']}/enlace", token=adm,
                verificar=lambda x: x.json["segundos"] > 0)
        ev.caso("F2-09", "auditoria-monitoreo", "Trazabilidad del producto en el microhub", "Salida por pedido y recepción por orden.", "GET",
                f"auditoria/trazabilidad/inventario?microhub_id={hub}&producto_id={pid_prod}", token=aud,
                verificar=lambda x: any("recepcion" in e["descripcion"] for e in x.json["eventos"]) and any("salida_pedido" in e["descripcion"] for e in x.json["eventos"]))
        ev.caso("F2-10", "reportes", "Reporte de alertas en CSV", "Visualización y archivo descargable con huella.", "GET",
                f"reportes/inventario_alertas/exportar?formato=csv&microhub_id={hub}", token=adm, verificar=lambda x: "Producto" in x.texto)
    finally:
        ev.http("inventario", "PATCH", f"inventario/{hub}/{pid_prod}/minimo", {"minimo": minimo_antes}, token=adm)
        if pedido:
            ev.http("pedidos", "POST", f"pedidos/{pedido}/estado", {"estado": "cancelado", "motivo": "Cierre del flujo de demostración"}, token=adm)


# ====================================================================
def flujo3(ev):
    print("F3. Sin conexión → sincronización → trazabilidad → reporte")
    adm, aud, rep = ev.entrar("admin@codex.mx"), ev.entrar("auditor@codex.mx"), ev.entrar("repartidor1@codex.mx")
    cli = ev.entrar("juan.chapa1@correo.mx")
    rid = uno("SELECT id FROM usuario WHERE correo = 'repartidor1@codex.mx'")["id"]
    productos = lineas_en_todos_los_microhubs(2, 20)
    r = ev.caso("F3-01", "pedidos", "El cliente hace un pedido", "Punto de partida del recorrido.", "POST", "pedidos",
                cuerpo={"lineas": [{"producto_id": p["producto_id"], "cantidad": 3} for p in productos]}, token=cli, esperado=201, verificar=lambda x: x.json["asignado"])
    if r is None or r.status != 201 or not r.json["asignado"]:
        return
    pid, mh = r.json["id"], r.json["microhub_id"]
    correo = uno("SELECT u.correo FROM usuario u JOIN rol rl ON rl.id = u.rol_id WHERE rl.clave = 'operador' AND u.microhub_id = %s AND u.estatus = 'activo' ORDER BY u.id LIMIT 1", (mh,))["correo"]
    op = ev.entrar(correo)
    ev.http("pedidos", "POST", f"pedidos/{pid}/estado", {"estado": "en_preparacion"}, token=op)
    ev.http("pedidos", "POST", f"pedidos/{pid}/listo", {}, token=op)
    r = ev.caso("F3-02", "entregas", "El operador asigna la entrega", "El repartidor la descarga antes de salir.", "POST", "entregas",
                cuerpo={"pedido_id": pid, "repartidor_id": rid}, token=op, esperado=201)
    if r is None or r.status != 201:
        return
    eid = r.json["entrega_id"]
    foto = evidencia_archivo(ev, rep, "entrega", eid, f"evidencia-flujo3-{eid}.jpg")
    disp = f"android-flujo-{uuid.uuid4().hex[:6]}"
    lote = {"lote_uuid": str(uuid.uuid4()), "dispositivo": disp, "cliente": "android", "operaciones": [
        {"operacion_uuid": str(uuid.uuid4()), "tipo": "ubicaciones", "creada_en": ahora(20),
         "datos": {"entrega_id": eid, "puntos": [{"latitud": 25.7488, "longitud": -100.3608, "capturado_en": ahora(20)},
                                                  {"latitud": 25.7491, "longitud": -100.3611, "capturado_en": ahora(15)}]}},
        {"operacion_uuid": str(uuid.uuid4()), "tipo": "entrega_resultado", "creada_en": ahora(12),
         "datos": {"entrega_id": eid, "resultado": "fallida", "monto_cobrado": 0, "cambio_entregado": 0, "incidencia": "El cliente no estaba en su domicilio",
                   "ubicacion": {"latitud": 25.7491, "longitud": -100.3611}, "evidencia_ids": [foto.json["id"]], "capturado_en": ahora(12)}}]}
    ev.caso("F3-03", "sincronizacion", "Android recupera la red y manda lo hecho sin conexión", "Se aplica en el orden en que ocurrió.", "POST", "sincronizacion/lotes",
            cuerpo=lote, token=rep, esperado=201, verificar=lambda x: x.json["aplicadas"] == 2,
            evidencia=lambda x: [pg("SELECT tipo, estado, intentos, creada_en FROM sync_operacion WHERE dispositivo = %s ORDER BY creada_en", (disp,)),
                                 mg("db.ubicaciones_entrega.countDocuments({entrega_id})", lambda db: db.ubicaciones_entrega.count_documents({"entrega_id": eid}))])
    ev.caso("F3-04", "sincronizacion", "La respuesta se perdió y reenvía el mismo lote", "No se repite nada.", "POST", "sincronizacion/lotes", cuerpo=lote, token=rep,
            verificar=lambda x: x.json["duplicadas"] == 2)
    ev.caso("F3-05", "notificaciones", "El cliente se entera de que la entrega falló", "Aviso del motor.", "GET", "notificaciones?por_pagina=5", token=cli,
            verificar=lambda x: any((n.get("referencia") or {}).get("id") == str(pid) for n in x.json["datos"]))
    ev.caso("F3-06", "auditoria-monitoreo", "El auditor revisa la entrega", "Bitácora y archivos de la entrega.", "GET", f"auditoria/trazabilidad/entrega/{eid}",
            token=aud, verificar=lambda x: any(e["origen"] == "documentos" for e in x.json["eventos"]))
    ev.caso("F3-07", "inventario", "El producto regresó al inventario", "La devolución la hizo el motor.", "GET",
            f"inventario/movimientos?microhub_id={mh}&por_pagina=5",
            token=adm, evidencia=lambda x: [pg("SELECT tipo, producto_id, cantidad, existencia_resultante FROM movimiento_inventario WHERE referencia_id = %s ORDER BY id", (pid,))])
    ev.caso("F3-08", "reportes", "Reporte del periodo en CSV", "La entrega ya cuenta en los reportes.", "GET", "reportes/pedidos_por_dia/exportar?formato=csv", token=adm,
            verificar=lambda x: "Pedidos" in x.texto,
            evidencia=lambda x: [pg("SELECT reporte, formato, filas, left(sha256, 16) AS sha256 FROM reporte_exportacion ORDER BY id DESC LIMIT 1")])


def main():
    ap = argparse.ArgumentParser(description="Tres procesos integrales por la API")
    ap.add_argument("--salida", default="/tmp/flujos")
    ap.add_argument("--servicios", default=os.environ.get("MICROSERVICIOS_URL", "http://{servicio}:{puerto}"))
    a = ap.parse_args()
    ev = Evidencias(a.servicios)
    for flujo in (flujo1, flujo2, flujo3):
        try:
            flujo(ev)
        except Exception as e:                                          # un flujo roto no impide probar los demás
            ev.casos.append({"id": f"{flujo.__name__}-ERR", "servicio": "auth", "puerto": 5101, "titulo": f"{flujo.__name__} se interrumpió", "objetivo": str(e),
                             "metodo": "-", "url": "-", "estado": "FALLA", "esperado": "-", "obtenido": f"{type(e).__name__}: {e}"})
            print(f"  FALLA {flujo.__name__}: {type(e).__name__}: {e}")
    salida = Path(a.salida)
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "flujos.json").write_text(json.dumps(ev.casos, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    titulo = "# Procesos integrales de principio a fin\n\n"
    (salida / "flujos.md").write_text(titulo + a_markdown(ev.casos).split("\n", 1)[1], encoding="utf-8")
    (salida / "pruebas.md").write_text(a_tabla(ev.casos), encoding="utf-8")
    (salida / "flujos.html").write_text(a_html(ev.casos), encoding="utf-8")
    pasan = sum(c["estado"] == "PASA" for c in ev.casos)
    print(f"\n{pasan} de {len(ev.casos)} pasos pasan. Archivos en {salida}")
    return 0 if pasan == len(ev.casos) else 1


if __name__ == "__main__":
    sys.exit(main())
